"""One owned Node process per case; hard deadlines cannot kill the inventory.

Importing performs no evidence IO. Source preparation/tests use artificial data.
"""
from pathlib import Path
import argparse,hashlib,json,math,os,queue,re,shutil,struct,subprocess,threading,time
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent.parent
DEFAULT=ROOT/'research/learned-opponent-results'
MAX_STATES=15376
STATUS={'tight':'certified response within gap target','loose':'certified response with loose gap',
 'timeout':'retained hard-budget timeout','input':'retained input failure','proposal':'retained proposal failure',
 'certificate':'retained certificate failure','worker':'retained worker failure'}
def require(ok,message):
 if not ok:raise ValueError(message)
def now():return datetime.now(timezone.utc).isoformat()
def supervisor_rss():
 """Current parent working set; no dependency installation or peak inference."""
 try:
  if os.name!='nt':return {'bytes':None,'reason':'Current RSS backend specified for Windows only'}
  import ctypes
  from ctypes import wintypes
  class Counters(ctypes.Structure):
   _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
  api=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo;api.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD];api.restype=wintypes.BOOL
  c=Counters();c.cb=ctypes.sizeof(c)
  if not api(wintypes.HANDLE(-1),ctypes.byref(c),c.cb):raise OSError(ctypes.get_last_error(),'GetProcessMemoryInfo failed')
  return {'bytes':int(c.WorkingSetSize),'reason':None}
 except Exception as exc:return {'bytes':None,'reason':str(exc)}
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def local(root,name):
 require(isinstance(name,str) and name and not Path(name).is_absolute(),'Relative artifact path required')
 root=Path(root).resolve();p=(root/name).resolve();require(p!=root and p.is_relative_to(root),'Artifact escapes declared directory');return p
def save(root,name,value):
 p=local(root,name);p.parent.mkdir(parents=True,exist_ok=True)
 b=value if isinstance(value,bytes) else (json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 with p.open('xb') as f:f.write(b)
 return {'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def readref(root,ref,ceiling=64_000_000):
 require(isinstance(ref,dict) and type(ref.get('bytes')) is int and 0<=ref['bytes']<=ceiling
         and re.fullmatch('[a-f0-9]{64}',ref.get('sha256','')),'Malformed or oversized artifact reference')
 p=local(root,ref['file']);require(p.stat().st_size==ref['bytes'],'Artifact byte count differs');b=p.read_bytes()
 require(hashlib.sha256(b).hexdigest()==ref['sha256'],'Artifact hash differs');return b
def hexinteger(s,bits=1_000_000):
 require(isinstance(s,str) and len(s)<=math.ceil(bits/4)+4,'Hex token exceeds parse budget')
 require(re.fullmatch('-?0x(?:0|[1-9a-f][0-9a-f]*)',s) and s!='-0x0','Noncanonical signed hex')
 n=int(s,16);require(abs(n).bit_length()<=bits,'Hex bit budget exceeded');return n
def scalar(s):
 require(isinstance(s,dict),'Missing exact scalar');n=hexinteger(s.get('numeratorHex'));d=hexinteger(s.get('denominatorHex'))
 require(d>0 and math.gcd(n,d)==1,'Exact scalar is not reduced with positive denominator');return n,d
def validate_complete(directory,ref,plan):
 r=json.loads(readref(directory,ref));
 for key in ['id','oldRunID','scenario','seed','initialization','focal','checkpointStep','control']:
  require(r.get(key)==plan.get(key),'Complete report identity differs: '+key)
 c=r.get('certificate',{});N=r.get('mdp',{}).get('states');require(type(N) is int and 0<N<=MAX_STATES,'Complete state bound invalid')
 require(c.get('passed') is True and type(c.get('withinRequestedGap')) is bool and type(c.get('allEdgesChecked')) is int
         and c['allEdgesChecked']>0 and r['mdp'].get('edges')==c['allEdgesChecked'],'Full all-edge certificate missing')
 opt=r['optimizer'];f64=readref(directory,opt['finalFloat64']);policy=readref(directory,opt['responsePolicy']);vector=readref(directory,opt['dyadicValues'],N*1029)
 require(len(f64)==N*8 and len(policy)==N and all(math.isfinite(v[0]) for v in struct.iter_unpack('<d',f64)),'Complete vector dimensions/nonfinite proposal')
 require(vector.endswith(b'\n') and len(vector.splitlines())==N,'Complete dyadic vector newline/dimensions differ')
 for token in vector.decode('ascii').splitlines():hexinteger(token,4096)
 for name in ['baseline','response']:
  part=r[name];p=json.loads(readref(directory,part['path']));h,c=p.get('h'),p.get('c')
  require(type(h) is int and h>=0 and type(c) is int and c>0 and h+c<=N and part['h']==h and part['c']==c,'Complete path decomposition missing')
  for key in ['states','executedA','executedB','nextStates','payoffIndices']:
   require(isinstance(p.get(key),list) and len(p[key])==h+c,'Complete path array missing')
  for actor in ['A','B']:
   for key in ['stateVisits','chosenActionVisits']:
    require(len(p.get('coverage',{}).get(actor,{}).get(key,[]))==h+c,'Complete support witness missing')
  scalar(part['value']);scalar(part['eventualCycleCustomerBenefit'])
 for value in [r['certificate']['upperValue'],r['certificate']['responseOptimalityGap'],r['performance']['rawGain'],r['performance']['possibleGain']['lower'],r['performance']['possibleGain']['upper']]:scalar(value)
 return r

def supervise(task,directory,project=ROOT,budget_seconds=300,node=None,case_source=None,on_event=None):
 """Kill only the Popen-owned PID. Never solve or recertify in the parent."""
 require(0<budget_seconds<=300,'Hard case budget outside declaration')
 directory=Path(directory).resolve();project=Path(project).resolve();plan=task['plan'];began=time.perf_counter();started_at=now();events=[]
 taskref=save(directory,'tasks/'+plan['id']+'.json',task);node=node or shutil.which('node');require(node,'Node runtime unavailable')
 case_source=Path(case_source or ROOT/'research/learned-opponent-case.js').resolve()
 process=None;latest=None;complete=None;stage='input';failure=None;kind=None;reader=None;done=False;stop_reader=threading.Event()
 def event(typ,**extra):
  e={'type':typ,'elapsedMilliseconds':(time.perf_counter()-began)*1000,'at':now(),**extra};events.append(e)
  if on_event:
   try:on_event(e)
   except Exception as exc:e['eventSinkFailure']=str(exc)
  return e
 try:
  process=subprocess.Popen([str(node),str(case_source),str(local(directory,taskref['file']))],cwd=project,
    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
  messages=queue.Queue(maxsize=8);stderr=[]
  def enqueue(item):
   while not stop_reader.is_set():
    try:messages.put(item,timeout=.05);return
    except queue.Full:pass
  def read_stdout():
   try:
    while True:
     line=process.stdout.readline(1_000_001)
     if not line:break
     item={'receivedMonotonic':time.perf_counter(),'receivedAt':now(),'line':line};enqueue(item)
     if len(line)>1_000_000:break
   except Exception as exc:enqueue({'readerFailure':str(exc)})
   finally:enqueue({'eof':True})
  def read_stderr():
   kept=0
   while True:
    b=process.stderr.read(4096)
    if not b:break
    if kept<65536:stderr.append(b[:65536-kept]);kept+=len(b)
  reader=threading.Thread(target=read_stdout,daemon=True);reader.start();err_reader=threading.Thread(target=read_stderr,daemon=True);err_reader.start()
  deadline=began+budget_seconds;event('owned process started',pid=process.pid)
  while kind is None:
   remaining=deadline-time.perf_counter()
   if remaining<=0:kind='timeout';break
   try:item=messages.get(timeout=min(.05,remaining))
   except queue.Empty:continue
   if time.perf_counter()>=deadline:kind='timeout';break
   if item.get('readerFailure'):raise ValueError(item['readerFailure'])
   if item.get('eof'):
    code=process.wait(timeout=max(.001,deadline-time.perf_counter()))
    if done and complete is not None and code==0:kind='completed'
    else:kind='failure';failure={'stage':'process exit','message':'Node case exited without a successful completed protocol','exitCode':code}
    break
   require(len(item['line'])<=1_000_000,'Oversized process message');message=json.loads(item['line']);typ=message.get('type')
   if typ=='stage':stage=message['stage'];event('stage',stage=stage)
   elif typ=='iteration':
    sweep=message.get('completedSweeps');difference=message.get('difference');require(type(sweep) is int and 1<=sweep<=600 and (latest is None or sweep>latest['completedSweeps']) and type(difference) in (int,float) and math.isfinite(difference) and difference>=0,'Invalid or nonincreasing completed proposal')
    b=readref(directory,message['proposal'],MAX_STATES*8);require(len(b)>0 and len(b)%8==0 and all(math.isfinite(v[0]) for v in struct.iter_unpack('<d',b)),'Malformed received proposal')
    if time.perf_counter()>=deadline:kind='timeout';break
    latest={'completedSweeps':sweep,'difference':difference,'bytes':b};parent=supervisor_rss();child=message.get('processRSSBytes');require(child is None or type(child) is int and child>=0,'Invalid reported child RSS')
    event('completed proposal received',completedSweeps=sweep,processRSSBytes=child,supervisorRSSBytes=parent['bytes'],supervisorRSSReason=parent['reason'],approximatelyPairedRSSBytes=child+parent['bytes'] if child is not None and parent['bytes'] is not None else None)
    process.stdin.write(b'\n');process.stdin.flush()
   elif typ=='certificate':
    require(complete is None,'Second complete certificate message rejected');r=validate_complete(directory,message['complete'],plan)
    if time.perf_counter()>=deadline:kind='timeout';break
    received=event('complete certificate received',sha256=message['complete']['sha256'],lineReceivedAt=item['receivedAt'],lineReceivedMilliseconds=(item['receivedMonotonic']-began)*1000)
    complete={'reference':message['complete'],'report':r,'receivedAt':received['at'],'receivedMilliseconds':received['elapsedMilliseconds']}
   elif typ=='done':require(complete is not None and not done,'No complete certificate received or duplicate done marker');done=True
   elif typ=='failure':kind='failure';failure=message.get('failure')
   else:raise ValueError('Unknown case message')
   if time.perf_counter()>=deadline:kind='timeout'
 except subprocess.TimeoutExpired:
  kind='timeout'
 except Exception as exc:
  kind='failure';failure={'stage':stage,'message':str(exc),'errorType':type(exc).__name__}
 stopping=event('termination requested',reason=kind);exit_code=None
 if process is not None:
  if process.poll() is None:process.kill()
  try:exit_code=process.wait(timeout=10)
  except subprocess.TimeoutExpired:failure={'stage':'owned process termination','message':'Owned PID did not exit within termination wait'}
  stop_reader.set()
  for stream in [process.stdin,process.stdout,process.stderr]:
   try:stream.close()
   except Exception:pass
  if reader:reader.join(timeout=.2)
  err_reader.join(timeout=.2)
 runtime={'startedAt':started_at,'hardBudgetSeconds':budget_seconds,'caseSeconds':time.perf_counter()-began,'lastStage':stage,
  'terminationRequestedAt':stopping['at'],'terminationRequestedMilliseconds':stopping['elapsedMilliseconds'],'workerExitCode':exit_code,'ownedPID':process.pid if process else None,
  'events':events,'task':taskref,'stderr':b''.join(stderr).decode('utf-8','replace') if process else '',
  'scope':'One independently isolated Node process; killed only the Popen-owned PID. Child process RSS samples are separate from supervisor RSS, not a continuous peak. Duration includes termination/validation overhead.'}
 return {'kind':kind,'failure':failure,'latestProposal':latest,'completeCertificate':complete,'runtime':runtime}

def execute_case(plan,directory,project=ROOT,mode='evidence',payload=None,**options):
 task={'plan':plan,'mode':mode,'payload':payload or {}};o=supervise(task,directory,project,**options);available=o['completeCertificate'] is not None;success=o['kind']=='completed';received=o['completeCertificate'];partial=None;partial_error=None
 if not available and o['latestProposal']:
  p=o['latestProposal']
  try:partial={'completedSweeps':p['completedSweeps'],'difference':p['difference'],'finalFloat64':save(directory,'artifacts/'+plan['id']+'/last-received-proposal.f64le',p['bytes']),'scope':'Last fully received completed proposal only; no response/path/certificate salvaged after termination'}
  except Exception as exc:partial_error=str(exc)
 if available:r=dict(received['report'])
 else:r={**plan,'input':(payload or {}).get('input'),'mdp':None,'optimizer':partial,'baseline':None,'response':None,'certificate':None,'performance':None}
 stage=(o['failure'] or {}).get('stage',o['runtime']['lastStage']);failure_key='certificate' if stage in ['exact certificate','received certificate validation'] else stage;status=STATUS['timeout'] if o['kind']=='timeout' else STATUS.get(failure_key,STATUS['worker'])
 if success:status=STATUS['tight'] if r['certificate']['withinRequestedGap'] else STATUS['loose']
 r.update(status=status,executionSucceeded=success,scientificAvailable=available,scientificUnavailableReason=None if available else 'No complete hash-bound certificate and paths were received before termination',
  runtime={**o['runtime'],'completeCertificate':received['reference'] if available else None,'receivedCompleteAt':received['receivedAt'] if available else None,'receivedCompleteMilliseconds':received['receivedMilliseconds'] if available else None,'partialArtifactFailure':partial_error},
  failure=None if success else o['failure'] or {'stage':stage,'message':'Supervised hard-budget termination; all partial work retained'})
 return r

def planned_cases():
 rows=[]
 for seed in range(907001,907013):
  for ctrl in ['startup-only','selected95']:
   control={'id':ctrl,'period':None if ctrl=='startup-only' else 4,'phases':2 if ctrl=='startup-only' else 4}
   old=f'base-g15-t1--{ctrl}--zero--s{seed}'
   for focal in ['A','B']:rows.append({'id':old+'--focal'+focal,'oldRunID':old,'scenario':'base-g15-t1','seed':seed,'initialization':'zero','control':control,'focal':focal,'checkpointStep':2000000})
 return rows
def assert_fresh(directory):
 for name in ['execution-start.json','journal.jsonl','records','artifacts','tasks','results.json','index.json','completion.json']:
  require(not (Path(directory)/name).exists(),'Partial/closed evidence preserved; refusing rerun: '+name)
def verify(directory,project=ROOT):
 directory=Path(directory);m=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
 for group in ['sourceHashes','inputHashes']:
  for name,wanted in m[group].items():
   require(digest(local(project,name))==wanted,'Frozen dependency differs '+name)
   if group=='sourceHashes':require(digest(local(directory,'sources/'+name))==wanted,'Frozen source snapshot differs '+name)
 require(m['plan']['cases']==planned_cases() and m['plan']['retainedRecords']==48 and m['plan']['hardCaseSeconds']==300 and m['plan']['maximumSweeps']==600,'Frozen matrix/settings differ')
 d=m['v10Delivery'];require(digest(local(project,d['receipt']))==d['receiptSha256'],'Closed V10 receipt differs');archive=local(project,d['archive'])
 if archive.exists():require(digest(archive)==d['archiveSha256'] and archive.stat().st_size==d['archiveBytes'],'Closed available V10 archive differs')
 return m
def run(directory=DEFAULT,project=ROOT):
 directory=Path(directory).resolve();project=Path(project).resolve();m=verify(directory,project);assert_fresh(directory);began=time.perf_counter();manifest_hash=digest(directory/'manifest.json')
 save(directory,'execution-start.json',{'startedAt':now(),'manifestSha256':manifest_hash,'plannedRecords':48,'sourceGate':'Explicit root numerical GO is required before invoking run'})
 records=[];indexed=[];samples=[]
 def journal(value):
  with (directory/'journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':now(),**value},separators=(',',':'))+'\n')
 for plan in m['plan']['cases']:
  journal({'id':plan['id'],'type':'case started'})
  try:r=execute_case(plan,directory,project,payload={'input':m['inputs'][plan['oldRunID']]},on_event=lambda e:journal({'id':plan['id'],**e}))
  except Exception as exc:r={**plan,'status':STATUS['worker'],'executionSucceeded':False,'scientificAvailable':False,'scientificUnavailableReason':'Runner exception retained','input':m['inputs'].get(plan['oldRunID']),'mdp':None,'optimizer':None,'baseline':None,'response':None,'certificate':None,'performance':None,'runtime':{'events':[],'caseSeconds':0},'failure':{'stage':'runner','message':str(exc),'errorType':type(exc).__name__}}
  ref=save(directory,'records/'+plan['id']+'.json',r);records.append(r);indexed.append({**ref,'id':plan['id'],'status':r['status'],'executionSucceeded':r['executionSucceeded'],'scientificAvailable':r['scientificAvailable']})
  rss=[{'nodeProcessRSSBytes':e.get('processRSSBytes'),'supervisorRSSBytes':e.get('supervisorRSSBytes'),'supervisorRSSReason':e.get('supervisorRSSReason'),'approximatelyPairedRSSBytes':e.get('approximatelyPairedRSSBytes')} for e in r['runtime']['events'] if e['type']=='completed proposal received'];samples.append({'id':plan['id'],'measurements':rss,'postCaseSupervisorRSS':supervisor_rss()})
  journal({'id':plan['id'],'type':'case retained','status':r['status'],'executionSucceeded':r['executionSucceeded'],'scientificAvailable':r['scientificAvailable'],'recordSha256':ref['sha256']})
  print(json.dumps({'id':plan['id'],'status':r['status'],'scientificAvailable':r['scientificAvailable'],'seconds':r['runtime']['caseSeconds']}),flush=True)
 rr=save(directory,'results.json',{'manifestSha256':manifest_hash,'records':records});ir=save(directory,'index.json',{'manifestSha256':manifest_hash,'records':indexed})
 try:verify(directory,project);final={'passed':True}
 except Exception as exc:final={'passed':False,'message':str(exc)}
 seconds=time.perf_counter()-began;complete=len(records)==48 and [r['id'] for r in records]==[p['id'] for p in m['plan']['cases']];failures=sum(not r['executionSucceeded'] for r in records);available=sum(r['scientificAvailable'] for r in records);tight=sum(r['scientificAvailable'] and r['certificate']['withinRequestedGap'] for r in records);measurements=[x for row in samples for x in row['measurements']];child_samples=[x['nodeProcessRSSBytes'] for x in measurements if x['nodeProcessRSSBytes'] is not None];largest=max(child_samples) if child_samples else None;paired=[x['approximatelyPairedRSSBytes'] for x in measurements if x['approximatelyPairedRSSBytes'] is not None];largest_paired=max(paired) if paired else None;size=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
 completion={'inventoryComplete':complete,'primaryPassed':complete and final['passed'] and failures==0,'retainedRecords':len(records),'executionFailures':failures,'budgetFailures':sum(r['status']==STATUS['timeout'] for r in records),'scientificallyAvailable':available,'tightCertificates':tight,'looseCertificates':available-tight,'manifestSha256':manifest_hash,'resultsSha256':rr['sha256'],'indexSha256':ir['sha256'],'finalFrozenDependencyCheck':final,
  'resources':{'seconds':seconds,'largestSampledNodeProcessRSSBytes':largest,'nodeRSSUnavailableReason':None if child_samples else 'No completed-proposal child RSS measurement was received','largestApproximatelyPairedRSSBytes':largest_paired,'pairedRSSUnavailableReason':None if paired else 'No complete child/supervisor paired RSS measurement was available','rssSamples':samples,'newOutputBytesBeforeCompletion':size,'scope':'Separate Node process RSS reported at completed proposal milestones, with Windows parent current-working-set sample upon receipt; approximately paired sum is not simultaneous/continuous peak or unique physical memory. Shared pages can be counted twice. Case elapsed duration includes startup/input/solver/certificate/termination overhead.','softTargetExceeded':{'seconds':seconds>7200,'approximatelyPairedRSS':largest_paired>512000000 if largest_paired is not None else None,'newOutputBytes':size>250000000},'experimentalModelApiCalls':0,'trainingRounds':0}}
 save(directory,'completion.json',completion);return completion
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=DEFAULT);p.add_argument('--project-root',type=Path,default=ROOT);args=p.parse_args();print(json.dumps(run(args.directory,args.project_root)))
