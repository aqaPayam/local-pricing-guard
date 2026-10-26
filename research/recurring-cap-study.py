"""Prospective recurring inherited-cap calculations; no default case execution.

Reuses the frozen primary 80-digit interval/model implementation with explicit
source/input hashes. Independent audit calculation code must remain separate.
"""
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
import argparse, hashlib, importlib.util, json, math, platform, sys, time
from datetime import datetime, timezone

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'research'))
from continuous_interval import Interval as I, Unresolved, decimal, fraction_decimal, exact_binary64, bisect_increasing
spec=importlib.util.spec_from_file_location('frozen_continuous_primary',ROOT/'research/continuous-study.py')
continuous=importlib.util.module_from_spec(spec);spec.loader.exec_module(continuous)

OUT=ROOT/'research/recurring-results'
J=64
MAX_PERIOD=65536
FRONTIER=[1,2,4,8,16,32,64,128]
KINDS=['effective','nominal']
LABELS=continuous.TARGET_LABELS
SOURCES=['research/recurring-cap-study.py','tests/test_recurring_cap.py',
 'research/SPARSE_RESET_PROTOCOL.md','research/SPARSE_RESET_THEORY.md',
 'research/continuous_interval.py','research/continuous-study.py']


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:f.write(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n')
def box(record):return I(record['lower'],record['upper'])


def upper_at_point(model,rival):
    """One scalar rival point; parameter intervals are never bisected as a root."""
    rival=decimal(rival)
    if not model.ell<=rival<=model.high:raise ValueError('Rival endpoint outside inherited interval')
    y=I(rival);w=model.w(y);best=1+w;target=w-model.t
    if target.lo<=0 or best.hi>=model.high:raise Unresolved('Inherited interior/positive-threshold premise not enclosed')
    residual=lambda x:target-model.profit(x,y)
    at_high=residual(I(model.high))
    if at_high.sign==-1:
        price=I(model.high)
        proof={'kind':'ceiling-clipped','ceilingResidual':at_high.json()}
    elif at_high.sign==1:
        price,signs=bisect_increasing(residual,best.hi,model.high,'1e-28')
        proof={'kind':'interior upper root',**signs}
    else:raise Unresolved('Upper-map ceiling sign unresolved')
    if price.width>Decimal('1e-25'):raise Unresolved('Upper-map scalar bracket exceeds declared width')
    if (price-best).lo<=0:raise Unresolved('Upper-map branch is not certified above best response')
    return {'rivalExact':str(rival),'normalizedPrice':price.json(),'bestProfitW':w.json(),'bestResponse':best.json(),
            'normalizedTargetProfit':target.json(),'proof':proof}


def map_interval(model,rival,cache=None):
    rival=I.cast(rival);cache={} if cache is None else cache
    def endpoint(value):
        key=str(value)
        if key not in cache:cache[key]=upper_at_point(model,value)
        return cache[key]
    lower=endpoint(rival.lo);upper=endpoint(rival.hi)
    left,right=box(lower['normalizedPrice']),box(upper['normalizedPrice'])
    if left.lo>right.hi:raise Unresolved('Monotone endpoint images inconsistent')
    # U is already globally certified nondecreasing by inherited theorem.
    image=I(left.lo,right.hi)
    return image,{'lowerEndpoint':lower,'upperEndpoint':upper,
                  'method':'Scalar endpoint roots plus inherited monotonicity; no broad-parameter root solve'}


def power_nonnegative(value,exponent):
    value=I.cast(value)
    if value.lo<0 or not isinstance(exponent,int) or exponent<0:raise ValueError('Nonnegative integer-power domain')
    result=I(1)
    while exponent:
        if exponent&1:result=result*value
        value=value*value;exponent//=2
    return result


def orbit(model,cap,qstar,rho,terms=J):
    cap=I.cast(cap);qstar=I.cast(qstar);rho=I.cast(rho)
    if cap.lo!=cap.hi or cap.lo<model.ell or cap.hi>=qstar.lo:raise Unresolved('Required inherited cap ell<=A<q_star not certified')
    if rho.lo<0 or rho.hi>=1:raise Unresolved('Inherited contraction bound invalid')
    current=cap;prices=[current];rewards=[];profits=[];steps=[];cache={}
    for j in range(terms):
        rewards.append(model.surplus(current,current))
        profits.append(model.mass_scale*model.profit(current,current))
        following,proof=map_interval(model,current,cache)
        if following.hi<current.lo:raise Unresolved('Orbit contradicts increasing-path theorem')
        if j==0 and following.lo<=cap.hi:raise Unresolved('Strict initial upward slack not enclosed')
        steps.append({'j':j,'executedNormalizedPrice':current.json(),'executedPrice':model.original_price(current).json(),
                      'consumerSurplus':rewards[-1].json(),'profitPerSellerOnWorstCSPath':profits[-1].json(),
                      'nextNormalizedPrice':following.json(),'upperMapProof':proof})
        current=following;prices.append(current)
    gap=qstar-current
    if gap.hi<0:raise Unresolved('Orbit exceeds inherited fixed-point enclosure')
    return {'cap':cap,'qstar':qstar,'rho':rho,'prices':prices,'rewards':rewards,'profits':profits,
            'steps':steps,'distanceAfterPrefix':I(max(Decimal(0),gap.lo),gap.hi),
            'massScale':model.mass_scale,'model':model}


class PeriodBounds:
    def __init__(self,trajectory,cstar):
        self.orbit=trajectory;self.cstar=I.cast(cstar);self.cache={}
        self.cs_prefix=[I(0)];self.profit_prefix=[I(0)]
        for reward,profit in zip(trajectory['rewards'],trajectory['profits']):
            self.cs_prefix.append(self.cs_prefix[-1]+reward)
            self.profit_prefix.append(self.profit_prefix[-1]+profit)

    def get(self,k):
        if not isinstance(k,int) or k<1 or k>MAX_PERIOD:raise ValueError('Period outside prospectively declared search')
        if k in self.cache:return self.cache[k]
        o=self.orbit;j=len(o['rewards']);tail=None
        if k<=j:
            total=self.cs_prefix[k];profit_total=self.profit_prefix[k];last=o['rewards'][k-1]
        else:
            count=k-j;r=I(o['rho'].hi)
            geometric=(1-power_nonnegative(r,count))/(1-r)
            excess=o['massScale']*o['distanceAfterPrefix']*geometric
            total=self.cs_prefix[j]+count*self.cstar+I(0,excess.hi)
            # This is only the profit on the CS-worst top-choice path. A
            # rectangle encloses its remaining prices; no profit ordering claim.
            prices=I(o['prices'][-1].lo,o['qstar'].hi)
            tail_profit=o['massScale']*o['model'].profit(prices,prices)
            profit_total=self.profit_prefix[j]+count*tail_profit
            last_excess=o['massScale']*o['distanceAfterPrefix']*power_nonnegative(r,k-1-j)
            last=self.cstar+I(0,last_excess.hi)
            tail={'termsAfterPrefix':count,'constantFloor':self.cstar.json(),
                  'geometricSum':geometric.json(),'excessSumUpper':str(excess.hi),
                  'lastRoundExcessUpper':str(last_excess.hi),'pathProfitTailPerSeller':tail_profit.json()}
        average=total/k;own=profit_total/k
        result={'period':k,'averageConsumerSurplus':average.json(),'cycleSumConsumerSurplus':total.json(),
                'lastRoundConsumerSurplus':last.json(),'profitAOnWorstCSPath':own.json(),
                'profitBOnWorstCSPath':own.json(),'jointProfitOnWorstCSPath':(2*own).json(),
                'capRuleActivationFrequency':(I(1)/k).json(),'startupCapCount':1,
                'capExecutionCountFormula':'ceil(T/K) for T>=1 from immediate actual cap activation',
                'finiteActivationAverageLowerBound':str(average.lo),'tail':tail,
                'scope':'Worst CS path profits are descriptive; no uniform profit bound or incentive-stability claim.'}
        self.cache[k]=result
        return result


def target_result(row,bounds):
    f=decimal(float(row['actualGuaranteedThreshold']))
    result={'label':row['label'],'requestedImported':exact_binary64(row['requestedTarget']),
            'actualThresholdImported':exact_binary64(row['actualGuaranteedThreshold']),
            'actualThresholdExact':str(f),'searchCeiling':MAX_PERIOD}
    cstar=bounds.cstar;first=box(bounds.get(1)['averageConsumerSurplus'])
    if cstar.lo>=f:
        return {**result,'status':'no recurring cap needed for the long-run target',
                'withoutIntervention':{'recurringFrequency':0,'startupCaps':0,'longRunFloor':cstar.json(),
                                       'finiteActivationAverageGuaranteedFromArbitraryOldPrices':False},
                'oneImmediateCapThenOriginalGuard':{'recurringFrequency':0,'startupCaps':1,
                                                    'finiteActivationAverageFloor':cstar.json()}}
    if first.hi<f:return {**result,'status':'infeasible for this fixed-cap family','strongestPeriod':bounds.get(1),
                          'scope':'Does not rule out a stricter cap or a different persistent controller.'}
    if first.lo<f:return {**result,'status':'unresolved period-one boundary','strongestPeriod':bounds.get(1)}
    safe=1;failed=None;tried=[];k=2
    while k<=MAX_PERIOD:
        value=box(bounds.get(k)['averageConsumerSurplus']);tried.append(k)
        if value.hi<f:failed=k;break
        if value.lo>=f:safe=k
        if k==MAX_PERIOD:break
        k=min(MAX_PERIOD,2*k)
    if failed is None:
        return {**result,'status':'censored safe lower bound' if safe==MAX_PERIOD else 'unresolved censored bracket',
                'certifiedSafePeriodLowerBound':safe,'safePeriod':bounds.get(safe),
                'certifiedFailingPeriodUpperBound':None,'ceilingPeriod':bounds.get(MAX_PERIOD),
                'doublingPeriods':tried,'scope':'No next-period evaluation beyond the declared ceiling; no finite optimum or no-cap inference.'}
    # Two certification searches retain ambiguity rather than guessing a sign.
    # Any returned safe L and failed H rigorously bracket the true optimum by
    # monotonicity of exact G_K, even if interval certification has overlaps.
    low,high=safe,failed
    while high-low>1:
        middle=(low+high)//2
        if box(bounds.get(middle)['averageConsumerSurplus']).lo>=f:low=middle
        else:high=middle
    safe=low
    low,high=safe,failed
    while high-low>1:
        middle=(low+high)//2
        if box(bounds.get(middle)['averageConsumerSurplus']).hi<f:high=middle
        else:low=middle
    failed=high
    exact=failed==safe+1
    return {**result,'status':'largest certified fixed period' if exact else 'certified integer bracket',
            'largestPeriod':safe if exact else None,'certifiedSafePeriodLowerBound':safe,
            'certifiedFailingPeriodUpperBound':failed,'possibleLargestPeriodBracket':[safe,failed-1],
            'safePeriod':bounds.get(safe),'nextFailingPeriod':bounds.get(failed),'doublingPeriods':tried,
            'scope':'Optimal only among the same physical inherited cap applied at fixed integer periods.'}


def inherited_cap(guard,cap,raw):
    scenario=guard['scenario'];sid=scenario['id'];prices=guard['game']['prices'];n=len(prices)
    if guard['id']!=sid+'-guard' or guard['controller']!='guard' or cap['id']!=sid+'-cap' or cap['scenario']!=scenario or raw['scenario']!=scenario or raw['guardCaseId']!=guard['id'] or raw['capCaseId']!=cap['id'] or n!=scenario['gridSize']:
        raise ValueError('Inherited physical cap scenario/economy/case identity differs')
    if cap['controller']!='cap' or cap['game']['prices']!=prices or cap['game']['n']!=n or cap['game']['treatment']!={'type':'cap'}:
        raise ValueError('Inherited physical cap price grid/treatment differs')
    support=cap['game']['sets'][0]
    if not support or support!=list(range(len(support))) or any(s!=support for s in cap['game']['sets']):raise ValueError('Inherited cap is not a common prefix independent of previous state')
    index=support[-1];price=prices[index]
    if len(raw['results'])!=5 or {r['label'] for r in raw['results']}!=set(LABELS):raise ValueError('Expected all five old target labels')
    for row in raw['results']:
        saved=row['existingCompetitiveCap']
        if saved['index']!=index or saved['price']!=price or saved['allowedInitialPricesPerSeller']!=index+1:raise ValueError('Initializer/raw cap index or physical price mismatch')
        exact_binary64(row['requestedTarget']);exact_binary64(row['actualGuaranteedThreshold'])
    return {'oldIndex':index,'oldGridSize':n,'physicalPriceImported':exact_binary64(price),
            'lowerPriceImported':exact_binary64(prices[0]),'sourceGuardCase':guard['id'],
            'sourceCapCase':cap['id'],'rawInitializerLabelsChecked':5},price


def validate_inherited():
    manifest=read(ROOT/'research/continuous-results/manifest.json')
    for field in ['sourceHashes','inputHashes']:
        for name,h in manifest[field].items():
            if digest(ROOT/name)!=h:raise ValueError('Inherited continuous frozen dependency changed '+name)
    results=read(ROOT/'research/continuous-results/results.json')
    audit=read(ROOT/'research/continuous-results/independent-audit.json')
    if not audit['passed'] or audit['studyManifestHash']!=digest(ROOT/'research/continuous-results/manifest.json') or audit['resultsSha256']!=digest(ROOT/'research/continuous-results/results.json') or audit['auditorSourceHash']!=digest(ROOT/'research/audit-continuous-study.py'):
        raise ValueError('Inherited continuous independent-audit binding failed')
    old_audit=read(ROOT/'research/handover-init-results/independent-audit.json')
    old_manifest=read(ROOT/'research/handover-init-results/manifest.json')
    if not old_audit['passed'] or old_audit['studyManifestHash']!=digest(ROOT/'research/handover-init-results/manifest.json') or old_audit['auditorSourceHash']!=digest(ROOT/'research/audit-handover-init.js') or not all(old_audit['corruptionNegativeControls'].values()):raise ValueError('Inherited initializer audit binding did not pass')
    # Every inherited initializer source/input hash is checked, including both
    # original cap and guard cases and raw target results' audited provenance.
    for field in ['sourceHashes','inputHashes']:
        for name,h in old_manifest.get(field,{}).items():
            if digest(ROOT/name)!=h:raise ValueError('Inherited initializer frozen dependency changed '+name)
    return manifest,results


def inventory():
    manifest,_=validate_inherited();names=['research/continuous-results/manifest.json',
      'research/continuous-results/results.json','research/continuous-results/completion.json',
      'research/continuous-results/independent-audit.json','research/audit-continuous-study.py',
      'research/handover-init-results/manifest.json','research/handover-init-results/results.json',
      'research/handover-init-results/independent-audit.json','research/audit-handover-init.js']
    for scenario in manifest['plan']['scenarios']:
        for kind in ['guard','cap']:names.append(f"research/cycle-results/cases/{scenario['id']}-{kind}.json")
    return manifest['plan']['scenarios'],{name:digest(ROOT/name) for name in names}


def freeze():
    if OUT.exists() and any(OUT.iterdir()):raise ValueError('Recurring evidence directory nonempty; no overwrite')
    scenarios,inputs=inventory()
    manifest={'frozenAt':datetime.now(timezone.utc).isoformat(),'plan':{'scenarios':scenarios,
      'continuums':KINDS,'targetLabels':LABELS,'records':16,'targetLabelsAcrossModels':80,'prefixTerms':J,
      'maximumSearchPeriod':MAX_PERIOD,'fixedPeriodFrontier':FRONTIER,'runtimeTargetSeconds':1800,
      'sampledRSSTargetBytes':250_000_000,'trainingRounds':0,'apiCalls':0},
      'sourceHashes':{name:digest(ROOT/name) for name in SOURCES},'inputHashes':inputs}
    for name in SOURCES:
        dest=OUT/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
    save(OUT/'manifest.json',manifest)
    print(json.dumps({'frozenAt':manifest['frozenAt'],'manifestSha256':digest(OUT/'manifest.json')}))


def verify():
    manifest=read(OUT/'manifest.json')
    for field in ['sourceHashes','inputHashes']:
        for name,h in manifest[field].items():
            if digest(ROOT/name)!=h:raise ValueError('Recurring frozen dependency changed '+name)
            if field=='sourceHashes' and digest(OUT/'sources'/name)!=h:raise ValueError('Recurring source snapshot changed '+name)
    validate_inherited();return manifest


def run():
    manifest=verify()
    if (OUT/'execution-start.json').exists() or (OUT/'results.json').exists():raise ValueError('Closed or partial recurring execution preserved')
    started=time.perf_counter();save(OUT/'execution-start.json',{'startedAt':datetime.now(timezone.utc).isoformat(),
      'manifestSha256':digest(OUT/'manifest.json')})
    old_cont=read(ROOT/'research/continuous-results/results.json')['records']
    old_targets=read(ROOT/'research/handover-init-results/results.json')['records']
    records=[];samples=[]
    for scenario in manifest['plan']['scenarios']:
        sid=scenario['id'];rows=[];pre_error=None
        try:
            guard=read(ROOT/f'research/cycle-results/cases/{sid}-guard.json')
            capcase=read(ROOT/f'research/cycle-results/cases/{sid}-cap.json')
            selected=[r for r in old_targets if r['scenario']['id']==sid]
            if len(selected)!=1:raise ValueError('Missing/duplicate old initializer record')
            rows=selected[0]['results'];physical,cap_price=inherited_cap(guard,capcase,selected[0])
            if guard['scenario']!=scenario:raise ValueError('Primary scenario differs from inherited guard')
        except Exception as error:pre_error=error
        for kind in KINDS:
            began=time.perf_counter();context={'expectedScenario':scenario}
            try:
                if pre_error is not None:raise ValueError('Pre-case identity failure: '+str(pre_error))
                context['physicalCap']=physical
                inherited=[r for r in old_cont if r['scenario']==sid and r['continuum']==kind]
                if len(inherited)!=1 or inherited[0]['status']!='certified theorem and enclosures' or not inherited[0]['assumptions']['eligible']:raise ValueError('No unique independently certified inherited continuum')
                inherited=inherited[0]
                model=continuous.Model(scenario['economy'],guard['game']['prices'][0],guard['game']['prices'][-1],scenario['epsilon'],kind=='effective')
                context.update({'importedBinary64':model.imported,'rounding':model.rounding})
                if model.imported!=inherited['importedBinary64'] or model.rounding!=inherited['rounding'] or {'lowerExact':str(model.ell),'upperExact':str(model.high)}!=inherited['domainNormalized']:raise ValueError('Inherited continuum exact constant/domain identity mismatch')
                a=fraction_decimal((Fraction(float(cap_price))-Fraction(float(scenario['economy']['cost'])))/Fraction(float(scenario['economy']['mu'])))
                qstar=box(inherited['worst']['normalizedPrice']);rho=box(inherited['assumptions']['rho']);cstar=box(inherited['worst']['consumerSurplus'])
                context.update({'normalizedCapExact':str(a),'conditions':{'ellAtMostCap':model.ell<=a,'capStrictlyBelowQStar':a<qstar.lo}})
                trajectory=orbit(model,I(a),qstar,rho,J);bounds=PeriodBounds(trajectory,cstar)
                frontier=[bounds.get(k) for k in FRONTIER]
                comparisons=[target_result(row,bounds) for row in rows]
                result={'status':'certified recurring-cap enclosures','physicalCap':physical,
                  'importedBinary64':model.imported,
                  'normalizedCapExact':str(a),'conditions':{'ellAtMostCap':model.ell<=a,'capStrictlyBelowQStar':a<qstar.lo},
                  'inheritedContinuum':{'qstar':qstar.json(),'consumerSurplus':cstar.json(),'rho':rho.json(),
                    'nash':inherited['nash'],'rounding':model.rounding},
                  'prefixTerms':J,'orbit':trajectory['steps'],'aJ':trajectory['prices'][-1].json(),
                  'qStarMinusAJ':trajectory['distanceAfterPrefix'].json(),'frontier':frontier,'comparisons':comparisons,
                  'periodEvaluations':[bounds.cache[k] for k in sorted(bounds.cache)],
                  'scope':'Same inherited physical cap replaces the guard on an actual first execution and then every K executions. Family-only period optimum; finite activation-average bound differs from individual-round bound and from arbitrary initial phase.'}
            except Exception as error:
                result={**context,'status':'unresolved calculation or condition','failure':str(error),'failureType':type(error).__name__,
                        'comparisons':continuous.comparisons_for(rows)}
            result.update({'scenario':sid,'continuum':kind,'seconds':time.perf_counter()-began})
            save(OUT/'records'/f'{sid}-{kind}.json',result);records.append(result)
            samples.append({'scenario':sid,'continuum':kind,'rssBytes':continuous.rss_bytes()})
            print(json.dumps({'scenario':sid,'continuum':kind,'status':result['status'],'seconds':result['seconds']}),flush=True)
    save(OUT/'results.json',{'manifestSha256':digest(OUT/'manifest.json'),'records':records})
    try:verify();endcheck={'passed':True}
    except Exception as error:endcheck={'passed':False,'failure':str(error)}
    resources={'seconds':time.perf_counter()-started,'rssSamples':samples,
      'largestObservedRSSBytes':max((r['rssBytes'] for r in samples if r['rssBytes'] is not None),default=None),
      'sampling':'After each record; not a continuously measured peak.','python':platform.python_version(),
      'trainingRounds':0,'apiCalls':0}
    save(OUT/'completion.json',{'records':len(records),'resolved':sum(r['status']=='certified recurring-cap enclosures' for r in records),
      'unresolved':sum(r['status']!='certified recurring-cap enclosures' for r in records),
      'targetLabels':sum(len(r['comparisons']) for r in records),'resultsSha256':digest(OUT/'results.json'),
      'resources':resources,'finalFrozenDependencyCheck':endcheck})
    if not endcheck['passed']:raise ValueError('Final dependency drift invalidates retained results')
    print(json.dumps({'complete':True,'records':len(records),'seconds':resources['seconds']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['freeze','run','verify']);args=parser.parse_args()
    if args.mode=='freeze':freeze()
    elif args.mode=='run':run()
    else:verify();print(json.dumps({'passed':True}))
