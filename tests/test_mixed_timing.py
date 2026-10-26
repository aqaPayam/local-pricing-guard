"""Artificial data only. No inherited market reads or cases."""
from pathlib import Path
import importlib.util, sys, unittest, uuid, shutil, io, json
from contextlib import redirect_stdout
from unittest.mock import patch
from fractions import Fraction as Q

spec=importlib.util.spec_from_file_location('mixed_primary',Path(__file__).resolve().parents[1]/'research/mixed-timing-study.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)


class Sequence(m.Envelope):
    def __init__(self,rewards,limit=None,kind='finite'):
        super().__init__();self.rewards=list(map(Q,rewards));self.kind=kind
        self.r0=m.Bounds.point(self.rewards[0]);self.cstar=m.Bounds.point(self.rewards[-1] if limit is None else Q(limit))
    def _sum(self,length):
        return m.Bounds.point(sum(self.rewards[:length],Q(0))+max(0,length-len(self.rewards))*self.rewards[-1])
    def reward(self,age):return m.Bounds.point(self.rewards[min(age,len(self.rewards)-1)])
    def price(self,age):return {'syntheticAge':age}
    def summary(self):return {'kind':self.kind,'scope':'Artificial engineering fixture only'}


class Tests(unittest.TestCase):
    def test_exact_mix_and_funded_prefix(self):
        out=m.solve_target(Sequence([3,1,0]),Q(3,2),'synthetic')
        self.assertEqual(out['frontier']['bestFixedK'],2)
        self.assertEqual(m.exact(out['rates']['constructedRateExact']),Q(3,8))
        self.assertEqual(m.exact(out['rates']['mixFractionBoundsExact']['lower']),Q(2,3))
        self.assertEqual([r['length'] for r in out['calendar']['blockPreview64'][:3]],[2,3,3])
        self.assertTrue(all(m.exact(r['cumulativePrefixExcessBounds']['lowerExact'])>=0 for r in out['executionPreview']))
        self.assertEqual(m.exact(out['rates']['absoluteSavingBoundsExact']['lower']),Q(1,8))

    def test_boundary_credit_is_not_partial_prefix_reward(self):
        out=m.solve_target(Sequence([3,1,0]),Q(3,2),'synthetic')
        first=out['executionPreview'][0]
        self.assertFalse(first['completedBlock'])
        self.assertEqual(m.exact(first['boundaryCreditAfterExact']),0)
        self.assertEqual(m.exact(first['cumulativePrefixExcessBounds']['lowerExact']),Q(3,2))
        self.assertTrue(out['executionPreview'][1]['completedBlock'])

    def test_credit_threshold_equality_chooses_funded_long_gap(self):
        rows=m.calendar_blocks(2,Q(1),Q(-1),4)
        self.assertEqual([r['length'] for r in rows],[2,3,2,3])
        self.assertEqual(m.exact(rows[1]['boundaryCreditBeforeExact']),1)
        self.assertEqual(m.exact(rows[1]['boundaryCreditAfterExact']),0)

    def test_zero_a_has_no_long_gap_or_false_saving(self):
        out=m.solve_target(Sequence([3,1,0]),Q(2),'synthetic')
        self.assertEqual(out['frontier']['bestFixedK'],2)
        self.assertEqual(m.exact(out['rates']['constructedSavingExact']),0)
        self.assertTrue(all(r['length']==2 for r in out['calendar']['blockPreview64']))

    def test_k_one_and_adjacent_cap_gaps(self):
        out=m.solve_target(Sequence([3,0]),Q(2),'synthetic')
        self.assertEqual(out['frontier']['bestFixedK'],1)
        self.assertEqual(m.exact(out['rates']['constructedRateExact']),Q(2,3))
        self.assertEqual(out['executionPreview'][0]['mode'],'cap')
        self.assertTrue(all(m.exact(r['certifiedPrefixLowerBoundExact'])>=0 for r in out['executionPreview']))

    def test_plateau_at_r0_and_constant_list_boundary(self):
        out=m.solve_target(Sequence([5,5,2]),Q(5),'synthetic')
        self.assertEqual(out['frontier']['bestFixedK'],2)
        self.assertEqual(m.exact(out['rates']['constructedRateExact']),Q(1,2))
        constant=m.solve_target(Sequence([5]),Q(5),'synthetic')
        self.assertEqual(constant['calendar']['kind'],'startup-only')
        self.assertEqual(constant['calendar']['blockPreview64'],[])
        self.assertEqual(sum(p['mode']=='cap' for p in constant['executionPreview']),1)
        self.assertEqual(m.exact(constant['rates']['constructedRateExact']),0)

    def test_lower_limit_targets_start_with_one_actual_cap(self):
        for F in [Q(2),Q(1)]:
            out=m.solve_target(Sequence([5,3,2]),F,'synthetic')
            self.assertEqual(out['calendar']['startupCaps'],1)
            self.assertIsNone(out['rates']['bestFixedK'])
            self.assertEqual(sum(p['mode']=='cap' for p in out['executionPreview']),1)
            self.assertEqual(out['executionPreview'][0]['rewardBounds']['lowerExact'],m.ratio(5))

    def test_infeasible_is_unavailable_not_zero(self):
        out=m.solve_target(Sequence([3,1]),Q(4),'synthetic')
        self.assertIn('infeasible',out['status']);self.assertIsNone(out['rates'])
        self.assertEqual(out['calendar']['kind'],'unavailable');self.assertEqual(out['executionPreview'],[])

    def test_b_zero_is_not_next_failure(self):
        out=m.solve_target(Sequence([3,1,0]),Q(4,3),'synthetic')
        self.assertEqual(out['frontier']['bestFixedK'],3)
        self.assertLess(m.exact(out['frontier']['failing']['excessBounds']['upperExact']),0)
        with self.assertRaises(ValueError):m.mixing(Q(1),Q(0))

    def test_ceiling_censor_and_no_query_above_limit(self):
        class Sentinel(Sequence):
            def _sum(self,length):
                self.assertion=length<=m.MAX_K
                if not self.assertion:raise AssertionError('Forbidden numerical query')
                return super()._sum(length)
        env=Sentinel([1,0]);out=m.solve_target(env,Q(1,2*m.MAX_K),'synthetic')
        self.assertEqual(out['status'],'censored safe ceiling')
        self.assertIsNone(out['rates']['bestFixedK']);self.assertIsNone(out['rates']['absoluteSavingBoundsExact'])
        self.assertEqual(out['frontier']['certifiedSafeK'],m.MAX_K)
        self.assertEqual(max(out['frontier']['queryLengths']),m.MAX_K)
        with self.assertRaises(ValueError):env.get(m.MAX_K+1)

    def test_overlap_preserves_safe_failing_and_null_best_fixed(self):
        class Ambiguous(Sequence):
            def _sum(self,length):
                if length==2:return m.Bounds(Q(3),Q(5))
                return super()._sum(length)
        out=m.solve_target(Ambiguous([3,1,0]),Q(2),'synthetic')
        self.assertEqual(out['frontier']['certifiedSafeK'],1)
        self.assertEqual(out['frontier']['failing']['period'],3)
        self.assertIsNone(out['rates']['bestFixedK'])
        self.assertIsNone(out['rates']['absoluteSavingBoundsExact'])
        self.assertEqual(out['calendar']['kind'],'fixed-safe')

    def test_conservative_interval_rate_and_outward_display_not_equality(self):
        pL=m.mixing(1,-3);pU=m.mixing(2,-1)
        self.assertEqual(1/(2+pU),Q(3,8));self.assertEqual(1/(2+pL),Q(4,9))
        self.assertLess(Q(3,8),Q(7,17));self.assertLess(Q(7,17),Q(4,9))
        r=m.rate_fields(Q(2,7),Q(1,3),Q(1,3),3,(Q(0),Q(1,2)))
        self.assertEqual(r['constructedRateExact'],r['optimumRateBoundsExact']['upper'])
        self.assertLess(Q(r['constructedRateDisplay']['lower']),Q(1,3))
        self.assertGreater(Q(r['constructedRateDisplay']['upper']),Q(1,3))

    def test_tiny_positive_mixing_and_huge_period_not_enumerated(self):
        tiny=Q(1,10**100)
        self.assertGreater(m.mixing(tiny,-1),0)
        rows=m.calendar_blocks(2,tiny,Q(-1),64)
        self.assertEqual(len(rows),64);self.assertTrue(all(r['length']==2 for r in rows))
        self.assertGreater(m.mixing(tiny,-1),0) # zero observed long gaps is not zero asymptotic mixing
        self.assertEqual(m.display(tiny)['lower'],'1E-100')

    def test_iid_unfunded_and_unweighted_mean_counterexamples(self):
        self.assertLess(sum(map(Q,[3,1,0])),3*Q(3,2)) # first iid long gap fails
        unweighted=(Q(3)+Q(4,3))/2;time_weighted=Q(7,4)
        self.assertGreater(unweighted,2);self.assertLess(time_weighted,2)

    def test_negative_reward_algebra(self):
        out=m.solve_target(Sequence([0,-2,-3]),Q(-3,2),'synthetic')
        self.assertTrue(out['rates']['exactOptimum'])
        self.assertTrue(all(m.exact(r['cumulativePrefixExcessBounds']['lowerExact'])>=0 for r in out['executionPreview']))

    def test_finite_cap_start_limit_differs_from_arbitrary_old_guard_cycle(self):
        raw={'finite':{'prices':[0.,1.,2.],'sets':[[0],[1],[2]],'upper':[0,1,2],'capIndex':1,
                      'rewards':{'consumerSurplus':[10.,9.,8.,9.,8.,7.,8.,7.,6.]}}}
        env=m.FiniteEnvelope(raw);self.assertEqual(env.cstar.lo,8)
        self.assertEqual(env.summary()['limitIndex'],1)
        self.assertNotEqual(env.cstar.lo,6)
        out=m.solve_target(env,Q(7),'synthetic');self.assertEqual(out['calendar']['kind'],'startup-only')

    def test_finite_condition_and_original_binary64_semantics(self):
        self.assertEqual(m.exact_float(.1),Q(3602879701896397,36028797018963968))
        raw={'finite':{'prices':[0.,1.],'sets':[[0],[0]],'capIndex':1,
                      'rewards':{'consumerSurplus':[4.,3.,3.,2.]}}}
        with self.assertRaisesRegex(ValueError,'nondecreasing'):m.FiniteEnvelope(raw)

    def test_continuous_closed_cache_and_true_contraction_tail(self):
        dec=m.interval_backend().fraction_decimal
        box=lambda q:{'lower':str(dec(Q(q))),'upper':str(dec(Q(q)))}
        record={'status':'certified recurring-cap enclosures','conditions':{'ellAtMostCap':True,'capStrictlyBelowQStar':True},
                'prefixTerms':64,'continuum':'effective','physicalCap':{'synthetic':True},
                'orbit':[{'j':j,'consumerSurplus':box(Q(1,2**j)),'executedPrice':box(Q(j))} for j in range(64)],
                'inheritedContinuum':{'consumerSurplus':box(0),'rho':box(Q(1,2))},
                'qStarMinusAJ':box(Q(1,2**64)),
                'importedBinary64':{'buyers':m.ratio(1),'mu':m.ratio(1)},
                'periodEvaluations':[{'period':1,'cycleSumConsumerSurplus':box(1)}]}
        env=m.ContinuousEnvelope(record,'artificial-source-not-a-file')
        self.assertEqual(env.get(1).lo,1);self.assertIn('originalInterval',env.cache[1].provenance)
        self.assertEqual(env.get(3).lo,Q(7,4))
        result=env.get(m.MAX_K);truth=Q(2)-Q(1,2**(m.MAX_K-1))
        self.assertLessEqual(result.lo,truth);self.assertGreaterEqual(result.hi,truth)
        self.assertLess(result.lo,2);self.assertGreater(env.reward(63).lo,0)
        with self.assertRaises(ValueError):env.reward(64)

    def test_all120_preload_failures_retained_with_null_values(self):
        plans=m.planned_models();self.assertEqual(len(plans),24)
        def fail(_):raise ValueError('Artificial pre-case identity failure')
        results=[m.execute_model(plan,fail) for plan in plans]
        slots=[t for r in results for t in r['targets']]
        self.assertEqual(len(slots),120);self.assertEqual(len({s['id'] for s in slots}),120)
        self.assertTrue(all(s['actualThresholdExact'] is None and s['rates'] is None for s in slots))
        self.assertTrue(all(s['calendar']['kind']=='unavailable' for s in slots))

    def test_per_target_failure_and_duplicates_do_not_drop_slots(self):
        plan=m.planned_models()[0]
        rows=[{'label':label,'F':Q(3,2),'identity':{'synthetic':True}} for label in m.LABELS]
        original=m.solve_target
        def one_failure(envelope,F,label,identity):
            if label==m.LABELS[1]:raise ValueError('Artificial target-only failure')
            return original(envelope,F,label,identity)
        with patch.object(m,'solve_target',one_failure):
            out=m.execute_model(plan,lambda _: (Sequence([3,1,0]),rows))
        self.assertEqual(len(out['targets']),5);self.assertEqual(out['calculationFailures'],1)
        self.assertIsNone(out['targets'][1]['rates'])
        self.assertEqual(out['targets'][1]['duplicateOf'],out['targets'][0]['id'])
        self.assertEqual(out['targets'][2]['duplicateOf'],out['targets'][0]['id'])
        self.assertTrue(out['queriedSums'])

    def test_failed_sum_attempt_retains_known_target_identities_and_query_failure(self):
        class FailedSum(Sequence):
            def _sum(self,length):
                if length==2:raise ValueError('Artificial unavailable sum enclosure')
                return super()._sum(length)
        plan=m.planned_models()[0]
        rows=[{'label':label,'F':Q(3,2),'identity':{'synthetic':True}} for label in m.LABELS]
        out=m.execute_model(plan,lambda _: (FailedSum([3,1,0]),rows))
        self.assertEqual(out['calculationFailures'],5)
        self.assertTrue(all(t['actualThresholdExact']==m.ratio(Q(3,2)) for t in out['targets']))
        self.assertEqual(out['queriedSums'][-1],{'period':2,'sumBounds':None})
        self.assertEqual(len(out['queryFailures']),5)
        self.assertTrue(all(t['frontier']['queryLengths']==[1,2] for t in out['targets']))
        self.assertEqual(out['targets'][1]['duplicateOf'],out['targets'][0]['id'])

    def test_failed_first_identified_target_still_heads_duplicate_group(self):
        plan=m.planned_models()[0]
        rows=[{'label':label,'F':Q(3,2),'identity':{'synthetic':True}} for label in m.LABELS]
        original=m.solve_target
        def first_failure(envelope,F,label,identity):
            if label==m.LABELS[0]:raise ValueError('Artificial first-slot failure')
            return original(envelope,F,label,identity)
        with patch.object(m,'solve_target',first_failure):
            out=m.execute_model(plan,lambda _: (Sequence([3,1,0]),rows))
        self.assertIsNone(out['targets'][0]['duplicateOf'])
        self.assertIsNone(out['targets'][0]['rates'])
        self.assertTrue(all(t['duplicateOf']==out['targets'][0]['id'] for t in out['targets'][1:]))

    def test_recursive_manifest_hash_closure_conflicts_and_cycles(self):
        # All reads/hashes below are injected artificial strings, not evidence I/O.
        hashes={'artificial/a/manifest.json':'a','artificial/b/manifest.json':'b',
                'artificial/source.py':'source'}
        docs={'artificial/a/manifest.json':{'sourceHashes':{'artificial/source.py':'source'},
               'inputHashes':{'artificial/b/manifest.json':'b'}},
              'artificial/b/manifest.json':{'sourceHashes':{},
               'inputHashes':{'artificial/a/manifest.json':'a'}}}
        key=lambda path:path.relative_to(m.ROOT).as_posix()
        reads=[]
        def load(path):reads.append(key(path));return docs[key(path)]
        closure=m.manifest_closure(['artificial/a/manifest.json'],load=load,hash_file=lambda path:hashes[key(path)])
        self.assertEqual(closure,hashes);self.assertEqual(len(reads),2)
        docs['artificial/b/manifest.json']['sourceHashes']={'artificial/source.py':'changed'}
        with self.assertRaisesRegex(ValueError,'dependency changed'):
            m.manifest_closure(['artificial/a/manifest.json'],load=load,hash_file=lambda path:hashes[key(path)])
        docs['artificial/b/manifest.json']['sourceHashes']={}
        with self.assertRaisesRegex(ValueError,'Conflicting'):
            m.manifest_closure(['artificial/a/manifest.json'],{'artificial/source.py':'wrong'},
                               load=load,hash_file=lambda path:hashes[key(path)])

    def test_legacy_manifest_missing_input_map_without_checkpoint_dependency(self):
        docs={'artificial/manifest.json':{'sourceHashes':{'artificial/source.js':'source'},
               'oldCheckpointHashes':{'artificial/not-model-input.bin':'not-read'}}}
        hashes={'artificial/manifest.json':'manifest','artificial/source.js':'source'}
        key=lambda path:path.relative_to(m.ROOT).as_posix()
        out=m.manifest_closure(['artificial/manifest.json'],load=lambda path:docs[key(path)],
                               hash_file=lambda path:hashes[key(path)])
        self.assertEqual(out,hashes)
        docs['artificial/manifest.json']['inputHashes']=[]
        with self.assertRaisesRegex(ValueError,'map malformed'):
            m.manifest_closure(['artificial/manifest.json'],load=lambda path:docs[key(path)],
                               hash_file=lambda path:hashes[key(path)])

    def test_prior_execution_carries_across_actual_caps_without_old_reward(self):
        raw={'finite':{'prices':[0.,1.,2.],'sets':[[0,1],[1,2],[2]],'capIndex':0,
                      'rewards':{'consumerSurplus':[10.,9.,8.,9.,8.,7.,8.,7.,6.]}}}
        out=m.solve_target(m.FiniteEnvelope(raw),Q(17,2),'synthetic')
        rows=out['executionPreview']
        self.assertIsNone(rows[0]['previousExecutedPrice']);self.assertIsNone(rows[0]['previousIndices'])
        for previous,current in zip(rows,rows[1:]):
            self.assertEqual(current['previousExecutedPrice'],previous['executedPrice'])
            self.assertEqual(current['previousIndices'],previous['executedIndices'])
        self.assertTrue(any(r['mode']=='cap' and r['previousIndices']!=[0,0] for r in rows[1:]))
        for block in out['calendar']['blockPreview64']:
            self.assertEqual(block['long'],block['length']==out['calendar']['K']+1)

    def test_partial_refusal_exclusive_writes_and_workspace_bound(self):
        directory=m.ROOT/'.local'/('mixed-synthetic-'+uuid.uuid4().hex)
        directory.mkdir(parents=True)
        try:
            m.assert_fresh(directory)
            for name in ['execution-start.json','journal.jsonl','records','results.json','index.json','completion.json']:
                file=directory/name;file.write_text('preserve',encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'refusing rerun'):m.assert_fresh(directory)
                self.assertEqual(file.read_text(encoding='utf-8'),'preserve');file.unlink()
            file=directory/'exclusive.json';m.save(file,{'synthetic':True})
            with self.assertRaises(FileExistsError):m.save(file,{'overwritten':True})
            with self.assertRaisesRegex(ValueError,'escapes'):m.contained(m.ROOT.parent/'not-the-workspace')
        finally:
            self.assertEqual(directory.parent,m.ROOT/'.local')
            self.assertTrue(directory.name.startswith('mixed-synthetic-'))
            shutil.rmtree(directory)

    def test_synthetic_full_runner_journal_and_failed_final_recheck_retained(self):
        # Only artificial envelope/loader/manifest identities; real inherited
        # inventory and numerical files are never read by this test.
        for fail_final in [False,True]:
            directory=m.ROOT/'.local'/('mixed-synthetic-'+uuid.uuid4().hex)
            directory.mkdir(parents=True)
            try:
                m.save(directory/'manifest.json',{'syntheticOnly':True})
                inputs={p[field]:'artificial-hash' for p in m.planned_models()
                        for field in ['finiteFile','continuousFile'] if p[field] is not None}
                manifest={'plan':m.plan_specification(),'inputHashes':inputs}
                targets=[{'label':label,'F':Q(3,2),'identity':{'synthetic':True}} for label in m.LABELS]
                real_digest=m.digest
                def fake_digest(path):
                    name=Path(path).relative_to(m.ROOT).as_posix()
                    return 'artificial-hash' if name in inputs else real_digest(path)
                calls=[]
                def fake_verify(_):
                    calls.append(True)
                    if fail_final and len(calls)>1:raise ValueError('Artificial final dependency change')
                    return manifest
                with patch.object(m,'verify',fake_verify),patch.object(m,'digest',fake_digest),\
                     patch.object(m,'read',lambda _: {'syntheticOnly':True}),\
                     patch.object(m,'prepare_model',lambda *_:(Sequence([3,1,0]),targets)),\
                     redirect_stdout(io.StringIO()):
                    if fail_final:
                        with self.assertRaisesRegex(ValueError,'Final dependency'):m.run(directory)
                    else:self.assertTrue(m.run(directory)['passed'])
                completion=json.loads((directory/'completion.json').read_text(encoding='utf-8'))
                self.assertEqual(completion['passed'],not fail_final)
                self.assertEqual(completion['models'],24);self.assertEqual(completion['targetLabels'],120)
                journal=[json.loads(s) for s in (directory/'journal.jsonl').read_text(encoding='utf-8').splitlines()]
                self.assertEqual(len(journal),48)
                self.assertEqual(len(list((directory/'records').glob('*.json'))),24)
                self.assertEqual(len(calls),2)
                with self.assertRaisesRegex(ValueError,'refusing rerun'):m.assert_fresh(directory)
            finally:
                self.assertEqual(directory.parent,m.ROOT/'.local')
                self.assertTrue(directory.name.startswith('mixed-synthetic-'))
                shutil.rmtree(directory)


if __name__=='__main__':unittest.main()
