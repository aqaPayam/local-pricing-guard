"""Primary full-grid-after-cap parent; adapted reviewed transport is explicit. Import is IO-free; no implicit training.

One owned Node process per run. A separate watchdog remains active while
strict checkpoint validation blocks. Independent replay has a separate author.
"""
from pathlib import Path
import argparse,types,hashlib,json,math,os,platform,queue,re,shutil,struct,subprocess,sys,threading,time,zlib
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent.parent
LAYOUT='dense5-own-rival-original-action-v1'
TREATMENT='full-grid-after-cap'
SCIENTIFIC_TREATMENT={'capClock':'startup','supportMode':TREATMENT,'initialCap':True,'postInitialOriginalIndices':'all'}
def require(ok,message):
 if not ok:raise ValueError(message)
def strict_equal(a,b):
 if type(a) is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(strict_equal(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(strict_equal(x,y) for x,y in zip(a,b))
 return a==b

def load_local_module(project,name):
 path=local(project,name);module=types.ModuleType('reference_'+path.stem.replace('-','_'));module.__file__=str(path);source=path.read_bytes();exec(compile(source,str(path),'exec'),module.__dict__);return module

def now():return datetime.now(timezone.utc).isoformat()
def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def local(root,name):
 require(isinstance(name,str) and name and '\\' not in name and ':' not in name and not name.startswith('/') and all(p not in ('','.','..') for p in name.split('/')),'Unsafe relative artifact path')
 root=Path(root).resolve();p=(root/name).resolve();require(p.is_relative_to(root) and p!=root,'Artifact escapes root');return p
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()
def parent_runtime():return {'executablePath':sys.executable,'executableSha256':digest(sys.executable),'pythonVersion':sys.version,'implementation':platform.python_implementation(),'zlibCompileVersion':zlib.ZLIB_VERSION,'zlibRuntimeVersion':zlib.ZLIB_RUNTIME_VERSION,'scope':'Actual parent executable/version and zlib backend identity; not a complete formal pin of every OS/standard-library binary'}
def parent_fingerprint(value):
 keys=('executableSha256','pythonVersion','implementation','zlibCompileVersion','zlibRuntimeVersion');require(all(k in value for k in keys),'Parent runtime identity incomplete');return {k:value[k] for k in keys}
def save(root,name,value):
 p=local(root,name);p.parent.mkdir(parents=True,exist_ok=True);b=value if isinstance(value,bytes) else encode(value)
 with p.open('xb') as f:f.write(b)
 return {'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def readref(root,ref,ceiling=64_000_000):
 require(isinstance(ref,dict) and type(ref.get('bytes')) is int and 0<=ref['bytes']<=ceiling and re.fullmatch('[a-f0-9]{64}',ref.get('sha256','')),'Malformed/oversized reference')
 p=local(root,ref['file']);require(p.stat().st_size==ref['bytes'],'Stored length differs');b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==ref['sha256'],'Stored hash differs');return b
def strict_dense(root,ref,n,encoding,on_sample=None):
 require(type(n) is int and 1<=n<=62 and encoding in ('f64le','u32le'),'Invalid approved dense dimensions')
 expected=5*n*n*n*(8 if encoding=='f64le' else 4)
 require(ref.get('rawBytes')==expected and ref.get('encoding')==encoding and ref.get('compression')=='gzip-single-member' and re.fullmatch('[a-f0-9]{64}',ref.get('rawSha256','')),'Declared raw length/encoding differs')
 # Exact ceiling and identity gate precedes decompression/allocation.
 p=local(root,ref['file']);require(type(ref.get('bytes')) is int and 18<=ref['bytes']<=expected+65536 and p.stat().st_size==ref['bytes'],'Compressed bound differs')
 compressed_hash=hashlib.sha256();raw_hash=hashlib.sha256();decoder=zlib.decompressobj(31);raw=bytearray();done=False
 with p.open('rb') as f:
  header=f.read(10);require(len(header)==10 and header[:4]==b'\x1f\x8b\x08\x00' and header[4:8]==b'\0'*4,'Canonical gzip header differs');f.seek(0)
  for chunk_index,chunk in enumerate(iter(lambda:f.read(1<<16),b'')):
   compressed_hash.update(chunk);require(not done,'Trailing gzip data or multiple members')
   out=decoder.decompress(chunk,expected-len(raw)+1);raw.extend(out);raw_hash.update(out)
   require(len(raw)<=expected and not decoder.unconsumed_tail,'Inflation exceeds exact dense ceiling')
   if on_sample and chunk_index%64==0:on_sample('strict gzip inflation '+encoding)
   if decoder.eof:require(not decoder.unused_data,'Trailing gzip data or multiple members');done=True
 require(done and len(raw)==expected and compressed_hash.hexdigest()==ref['sha256'] and raw_hash.hexdigest()==ref['rawSha256'],'Gzip/raw length/hash differs')
 if on_sample:on_sample('closed dense bytes '+encoding)
 return raw

def rng_transition(value):
 mask=(1<<32)-1;s=[(value>>(32*i))&mask for i in range(4)];t=(s[1]<<9)&mask
 s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=((s[3]<<11)|(s[3]>>21))&mask
 return sum((s[i]&mask)<<(32*i) for i in range(4))
def linear_apply(columns,value):
 out=0
 while value:
  lowest=value&-value;out^=columns[lowest.bit_length()-1];value-=lowest
 return out
_RNG_POWERS=[]
def advanced_actor(state,words):
 require(isinstance(state,list) and len(state)==4 and all(type(v) is int and 0<=v<2**32 for v in state) and any(state),'Malformed initial actor state')
 if not _RNG_POWERS:_RNG_POWERS.append([rng_transition(1<<i) for i in range(128)])
 value=sum(v<<(32*i) for i,v in enumerate(state));bit=0
 while words:
  if bit==len(_RNG_POWERS):_RNG_POWERS.append([linear_apply(_RNG_POWERS[-1],c) for c in _RNG_POWERS[-1]])
  if words&1:value=linear_apply(_RNG_POWERS[bit],value)
  words>>=1;bit+=1
 return [(value>>(32*i))&0xffffffff for i in range(4)]
def exact_ratio(value):
 require(isinstance(value,dict) and isinstance(value.get('numerator'),str) and isinstance(value.get('denominator'),str),'Exact ratio absent')
 n=value['numerator'];d=value['denominator'];require(len(n)<=1300 and len(d)<=1300 and re.fullmatch('-?(0|[1-9][0-9]*)',n) and n!='-0' and re.fullmatch('[1-9][0-9]*',d),'Exact ratio token malformed/oversized')
 numerator=int(n);denominator=int(d);require(abs(numerator).bit_length()<=4096 and denominator.bit_length()<=4096 and math.gcd(numerator,denominator)==1,'Exact ratio not canonical reduced')
 require(type(value.get('approximate')) in (int,float) and math.isfinite(value['approximate']),'Approximate ratio display invalid')

def validate_checkpoint(directory,ref,task,on_sample=None):
 m=json.loads(readref(directory,ref));plan=task['plan'];finite=task['finite'];n=len(finite['prices']);step=m.get('step');T=task.get('T',2_000_000);ends=task.get('checkpoints',[T//2,T])
 require(type(n) is int and 1<=n<=62 and type(step) is int and step in ends,'Unplanned checkpoint')
 require(strict_equal(task.get('scientificTreatment'),SCIENTIFIC_TREATMENT) and strict_equal(plan.get('scientificTreatment'),SCIENTIFIC_TREATMENT) and plan.get('treatment')==TREATMENT and plan.get('arm')=='startup','Explicit production task treatment differs')
 for key in ('id','arm','seed'):require(m.get(key)==plan[key],'Checkpoint identity differs: '+key)
 require(m.get('treatment')==TREATMENT and strict_equal(m.get('scientificTreatment'),SCIENTIFIC_TREATMENT),'Checkpoint scientific support treatment differs')
 require(type(finite.get('capIndex')) is int and 0<=finite['capIndex']<n,'Original cap invalid')
 cap=list(range(finite['capIndex']+1));full=list(range(n));supports=[[cap if p==0 else full for rival in range(n)] for p in range(5)]
 compact=lambda v:hashlib.sha256(json.dumps(v,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 declaration={'schemaVersion':1,'treatment':TREATMENT,'clock':'startup-only-five-phase','initialCap':'original physical cap; phase0 only','laterPhases':[1,2,3,4],'laterSupport':'all original price indices, independent of previous rival','originalIndexRange':[0,n-1],'originalCapIndex':finite['capIndex'],'originalGuardMasksSha256':compact(finite['sets']),'physicalRecordUnchanged':True,'floorTransferred':False,'scope':'Initial cap, unrestricted thereafter over the original price grid; no inherited guard floor','effectiveSupportsSha256':compact(supports)}
 require(strict_equal(m.get('supportTreatment'),declaration),'Checkpoint declared effective support differs')
 require(type(m.get('seed')) is int and type(m.get('schemaVersion')) is int and m['schemaVersion']==1 and type(m.get('n')) is int and m['n']==n and type(m.get('phases')) is int and m['phases']==5 and m.get('layout')==LAYOUT,'Dense metadata identity differs')
 software_keys=('executableSha256','node','v8','platform','architecture','osRelease','execArgv')
 if task.get('executionMode') in ('frozen-primary','artificial'):
  require(all(k in m.get('software',{}) and k in task['software'] for k in software_keys) and {k:m['software'][k] for k in software_keys}=={k:task['software'][k] for k in software_keys},'Frozen software backend identity differs')
 else:require(m.get('software')==task['software'],'Artificial fixture software identity differs')
 require(m.get('finiteGameRef')==task['finiteGameRef'] and m.get('learning')=={'T':T,'alpha':.1,'gamma':19/20,'initialization':'positive-zero'},'Input/learning identity differs')
 cells=5*n*n*n;require(m.get('allocation')=={'cellsPerFirm':cells,'qBytesPerFirm':cells*8,'countBytesPerFirm':cells*4},'Dense allocated capacity differs')
 phase=0 if step==0 else 1+(step-1)%4;terminal=m.get('terminal',{});previous=terminal.get('previousIndices')
 require(type(terminal.get('phase')) is int and terminal.get('phase')==phase and isinstance(previous,list) and len(previous)==2 and all(type(v) is int and 0<=v<n for v in previous),'NEXT clock/history differs')
 require(type(m.get('caps')) is int and m.get('caps')==(1 if plan['arm']=='startup' else math.ceil(step/4)),'Cap count differs')
 require(isinstance(m.get('actors'),list) and len(m['actors'])==2 and all(isinstance(a,list) and len(a)==4 and all(type(v) is int and 0<=v<2**32 for v in a) for a in m['actors']) and m['actors']==[advanced_actor(a,2*step) for a in plan['actors']],'Actor states differ from exact fixed-draw advancement')
 artifacts=m.get('artifacts',{});require(all(isinstance(artifacts.get(k),list) and len(artifacts[k])==2 for k in ('q','counts')),'Both firms dense artifacts required')
 policies=m.get('policies',{});require(all(isinstance(policies.get(k),list) and len(policies[k])==2 for k in ('own','world')),'Both policy coordinate families required')
 own=[readref(directory,r,5*n*n) for r in policies['own']];world=[readref(directory,r,5*n*n) for r in policies['world']]
 require(all(len(p)==5*n*n for p in own+world),'Policy byte lengths differ')
 for p in range(5):
  for a in range(n):
   for b in range(n):
    index=(p*n+a)*n+b;require(world[0][index]==own[0][index] and world[1][index]==own[1][(p*n+b)*n+a],'B WORLD policy was not mapped exactly once')
 # Decompress one pair at a time. No vector from the child initializes learning.
 for firm in range(2):
  q=strict_dense(directory,artifacts['q'][firm],n,'f64le',on_sample);counts=strict_dense(directory,artifacts['counts'][firm],n,'u32le',on_sample);total=0
  if on_sample:on_sample('both dense vectors live during validation')
  maxima=bytearray(5*n*n*8)
  for row in range(5*n*n):
   phase0=row//(n*n);rival=row%n;capped=phase0==0 or (plan['arm']=='recurring4' and phase0==4)
   allowed=set(range(finite['capIndex']+1)) if capped else set(range(n))
   for a in range(n):
    cell=row*n+a;value=struct.unpack_from('<d',q,cell*8)[0];count=struct.unpack_from('<I',counts,cell*4)[0];require(math.isfinite(value) and count<=step,'Nonfinite Q or invalid cell count');total+=count
    if a not in allowed:require(q[cell*8:cell*8+8]==b'\0'*8 and count==0,'Forbidden dense cell changed')
   winner=min(allowed)
   for a in sorted(allowed):
    if struct.unpack_from('<d',q,(row*n+a)*8)[0]>struct.unpack_from('<d',q,(row*n+winner)*8)[0]:winner=a
   require(own[firm][row]==winner,'Saved greedy policy differs from legal Q scan');maxima[row*8:row*8+8]=q[(row*n+winner)*8:(row*n+winner+1)*8]
  require(total==step,'Global per-firm count differs from step')
  require(m.get('cacheIdentity',{}).get('best',[None,None])[firm]==hashlib.sha256(own[firm]).hexdigest() and m.get('cacheIdentity',{}).get('maximum',[None,None])[firm]==hashlib.sha256(maxima).hexdigest(),'Saved cache identity differs from reconstructed legal maxima')
 blocks=m.get('transcriptBlocks');require(isinstance(blocks,list) and len(blocks)==step//10000,'Transcript block inventory differs')
 for i,b in enumerate(blocks):require(b=={'block':i+1,'firstRound':i*10000+1,'lastRound':(i+1)*10000,'rounds':10000,'bytes':1200000,'sha256':b.get('sha256')} and re.fullmatch('[a-f0-9]{64}',b.get('sha256','')),'Transcript inclusive one-based identity differs')
 partial=m.get('transcriptPartial',{});require(partial.get('rounds')==step%10000 and partial.get('bytes')==(step%10000)*120 and re.fullmatch('[a-f0-9]{64}',partial.get('sha256','')),'Partial transcript identity differs')
 require(isinstance(m.get('windows'),list) and len(m['windows'])==2,'Both planned window records required')
 require(isinstance(m.get('windowMetrics'),list) and len(m['windowMetrics'])==2,'Both exact window summaries required')
 for i,w in enumerate(m['windows']):
  end=ends[i];start=max(0,end-100000);rounds=max(0,min(step,end)-start)
  require(w.get('startStep')==start and w.get('endStep')==end and w.get('rounds')==rounds,'Window bounds differ')
  transitions=w.get('transitions');require(isinstance(transitions,list),'Window transitions absent');last=-1;total=0;caps=0;max_allowed=[0,0];price_changes=[0,0]
  for pair in transitions:
   require(isinstance(pair,list) and len(pair)==2 and all(type(v) is int for v in pair),'Window count is not integral');key,count=pair
   require(last<key<5*n**4 and count>0,'Window ordering/count differs');last=key;total+=count;row,index=divmod(key,n*n);p,history=divmod(row,n*n);pa,pb=divmod(history,n);a,b=divmod(index,n);cap=p==0 or (plan['arm']=='recurring4' and p==4)
   legalA=range(finite['capIndex']+1) if cap else range(n);legalB=range(finite['capIndex']+1) if cap else range(n)
   require(a in legalA and b in legalB,'Illegal executed window action');caps+=count if cap else 0
   max_allowed[0]+=count if a==legalA[-1] else 0;max_allowed[1]+=count if b==legalB[-1] else 0;price_changes[0]+=count if a!=pa else 0;price_changes[1]+=count if b!=pb else 0
  def cumulative_caps(t):return 0 if t<=0 else 1 if plan['arm']=='startup' else (t+3)//4
  require(total==rounds and w.get('capExecutions')==caps and caps==cumulative_caps(min(step,end))-cumulative_caps(min(step,start)),'Window total/cap count differs')
  for key in ('maxAllowed','explorations','priceChanges'):require(isinstance(w.get(key),list) and len(w[key])==2 and all(type(v) is int and 0<=v<=rounds for v in w[key]),'Window actor counter differs')
  require(w['maxAllowed']==max_allowed and w['priceChanges']==price_changes,'Window action geometry counters differ from exact transition counts')
  summary=m['windowMetrics'][i];require(isinstance(summary,dict) and summary.get('startStep')==start and summary.get('endStep')==end and summary.get('rounds')==rounds,'Exact window summary identity differs')
  if rounds==0:require(summary.get('metrics') is None and isinstance(summary.get('reason'),str),'Empty-window missing reason')
  else:
   metrics=summary.get('metrics');require(isinstance(metrics,dict),'Exact window metrics absent')
   for key in ('consumerSurplus','capRuleFrequency'):exact_ratio(metrics.get(key))
   for key in ('profits','prices','maskCount','maskFraction','maskSpan','maxAllowedUsage','explorationFrequency','priceChangeFrequency'):
    require(isinstance(metrics.get(key),dict) and set(metrics[key])=={'A','B'},'Exact actor window metric absent')
    for value in metrics[key].values():exact_ratio(value)
 graph=json.loads(readref(directory,m.get('graph')));require(isinstance(graph,dict),'Closed graph absent')
 require(strict_equal(graph.get('scientificTreatment'),SCIENTIFIC_TREATMENT) and strict_equal(graph.get('supportTreatment'),declaration) and 'floor' in graph and graph['floor'] is None,'Graph has wrong treatment or inherited guard floor')
 require(graph.get('cycles') and all('floorApplies' in c and c['floorApplies'] is None and c.get('floorGap') is None for c in graph['cycles']),'Full-support cycles must not inherit guard-floor claims')
 for k in ('actualTerminal','freshCapCounterfactual'):require(graph.get(k) and 'floorApplies' in graph[k] and graph[k]['floorApplies'] is None and graph[k].get('floorGap') is None,'Full-support trajectory has inherited guard-floor claim')
 if on_sample:on_sample('graph decoded during checkpoint validation')
 return m

def current_rss():
 try:
  if os.name!='nt':return {'bytes':None,'reason':'Current working-set backend is Windows-specific'}
  import ctypes
  from ctypes import wintypes
  class C(ctypes.Structure):
   _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD),('peak',ctypes.c_size_t),('working',ctypes.c_size_t),('other',ctypes.c_size_t*6)]
  c=C();c.cb=ctypes.sizeof(c);api=ctypes.WinDLL('psapi').GetProcessMemoryInfo;api.argtypes=[wintypes.HANDLE,ctypes.POINTER(C),wintypes.DWORD]
  require(api(wintypes.HANDLE(-1),ctypes.byref(c),c.cb),'RSS query failed');return {'bytes':int(c.working),'reason':None}
 except Exception as e:return {'bytes':None,'reason':str(e)}
def owned_process_rss(process):
 try:
  if os.name!='nt':return {'bytes':None,'reason':'Owned process working-set backend is Windows-specific'}
  import ctypes
  from ctypes import wintypes
  class C(ctypes.Structure):_fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD),('peak',ctypes.c_size_t),('working',ctypes.c_size_t),('other',ctypes.c_size_t*6)]
  c=C();c.cb=ctypes.sizeof(c);api=ctypes.WinDLL('psapi').GetProcessMemoryInfo;api.argtypes=[wintypes.HANDLE,ctypes.POINTER(C),wintypes.DWORD]
  require(api(wintypes.HANDLE(int(process._handle)),ctypes.byref(c),c.cb),'Owned process RSS query failed');return {'bytes':int(c.working),'reason':None}
 except Exception as e:return {'bytes':None,'reason':str(e)}

def supervise(task,directory,project=ROOT,budget_seconds=600,node=None,case_source=None,validator=validate_checkpoint):
 require(strict_equal(task.get('scientificTreatment'),SCIENTIFIC_TREATMENT) and strict_equal(task.get('plan',{}).get('scientificTreatment'),SCIENTIFIC_TREATMENT) and task['plan'].get('treatment')==TREATMENT and task['plan'].get('arm')=='startup','Supervisor requires the explicit full-grid-after-cap treatment');require(0<budget_seconds<=600,'Hard budget outside prospective bound');directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=True);project=Path(project).resolve()
 began=time.perf_counter();deadline=began+budget_seconds;events=[];lock=threading.RLock();stop=threading.Event();eligible={};received=set();checkpoint_failures={};failure=None;done=False;termination=None;process=None;messages=queue.Queue(maxsize=8);samples=[];stderr=[];reader=None;err=None
 def event(kind,**fields):
  with lock:
   row={'sequence':len(events),'type':kind,'elapsedMilliseconds':(time.perf_counter()-began)*1000,'at':now(),**fields};events.append(row);return row
 taskref=save(directory,'tasks/'+task['plan']['id']+'.json',task)
 try:
  node=node or shutil.which('node');require(node,'Node24 runtime required');case_source=Path(case_source or ROOT/'research/guard-reference-case.js').resolve()
  process=subprocess.Popen([node,str(case_source),str(local(directory,taskref['file']))],cwd=project,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
  event('owned process started',pid=process.pid)
  def watchdog():
   nonlocal termination
   if not stop.wait(max(0,deadline-time.perf_counter())):
    with lock:
     if process.poll() is None:
      termination=event('deadline termination requested',pid=process.pid)
      try:process.kill()
      except ProcessLookupError:pass
  threading.Thread(target=watchdog,daemon=True).start()
  def enqueue(value):
   while not stop.is_set():
    try:messages.put(value,timeout=.02);return
    except queue.Full:pass
  def stdout_reader():
   try:
    while True:
     line=process.stdout.readline(1_000_001)
     if not line:break
     received_event=event('process line received',lineBytes=len(line));enqueue({'line':line,'received':received_event})
     if len(line)>1_000_000:break
   except Exception as e:enqueue({'error':str(e)})
   finally:enqueue({'eof':True})
  def stderr_reader():
   remaining=65536
   while True:
    b=process.stderr.read(4096)
    if not b:break
    if remaining:stderr.append(b[:remaining]);remaining-=min(remaining,len(b))
  reader=threading.Thread(target=stdout_reader,daemon=True);reader.start();err=threading.Thread(target=stderr_reader,daemon=True);err.start()
  while time.perf_counter()<deadline and termination is None:
   try:item=messages.get(timeout=min(.05,max(.001,deadline-time.perf_counter())))
   except queue.Empty:continue
   if item.get('error'):raise ValueError(item['error'])
   if item.get('eof'):break
   require(len(item['line'])<=1_000_000,'Oversized child message');message=json.loads(item['line']);kind=message.get('type')
   if kind=='checkpoint':
    step=message.get('step');require(len(received)<len(task['checkpoints']) and step==task['checkpoints'][len(received)] and step not in received,'Duplicate/out-of-order checkpoint receipt');received.add(step);event('checkpoint received',step=step,metadata=message['metadata'])
    try:
     def validation_sample(stage):
      child=owned_process_rss(process);samples.append({'elapsedMilliseconds':(time.perf_counter()-began)*1000,'nodeProcessRSSBytes':child['bytes'],'nodeRSSUnavailableReason':child['reason'],'supervisorRSS':current_rss(),'stage':stage,'measurementSource':'Parent queries its owned child and itself sequentially; approximate paired working set'})
     checked=validator(directory,message['metadata'],task,on_sample=validation_sample) if validator is validate_checkpoint else validator(directory,message['metadata'],task)
     with lock:
      if time.perf_counter()<deadline and termination is None and process.poll() is None:
       proof=event('checkpoint validated',step=step,metadata=message['metadata']);eligible[step]={'step':step,'metadata':message['metadata'],'parentEligible':True,'receivedSequence':item['received']['sequence'],'validatedSequence':proof['sequence'],'scientificAvailable':False,'reason':'Awaiting independently authored full training replay'}
       process.stdin.write((json.dumps({'type':'ack','step':step})+'\n').encode());process.stdin.flush()
      else:event('checkpoint validation completed too late',step=step)
    except Exception as e:
     eligible.pop(step,None)
     checkpoint_failures[step]={'message':str(e),'metadata':message['metadata']}
     event('checkpoint rejected',step=step,message=str(e))
     if process.poll() is None:
      process.stdin.write((json.dumps({'type':'reject','step':step,'reason':str(e)})+'\n').encode());process.stdin.flush()
   elif kind=='sample':
    require(type(message.get('rssBytes')) is int and message['rssBytes']>0,'Malformed process RSS sample');samples.append({'elapsedMilliseconds':(time.perf_counter()-began)*1000,'nodeProcessRSSBytes':message['rssBytes'],'supervisorRSS':current_rss()})
   elif kind=='checkpoint-failure':
    step=message.get('step');require(type(step) is int and step in task['checkpoints'],'Unplanned checkpoint failure');received.add(step);checkpoint_failures[step]={'message':message.get('message'),'metadata':None};event('child checkpoint failure',step=step,message=message.get('message'))
   elif kind=='done':require(not done,'Duplicate done message');done=True;event('done received')
   elif kind=='failure':failure=message;event('child failure',message=message)
   else:raise ValueError('Unknown child message')
  # A done message is not success: natural zero exit must precede the deadline.
  if process.poll() is None and time.perf_counter()<deadline and termination is None:
   try:process.wait(timeout=max(.001,deadline-time.perf_counter()))
   except subprocess.TimeoutExpired:pass
  if process.poll() is None:
   with lock:
    if termination is None:termination=event('deadline termination requested',pid=process.pid)
    process.kill()
  process.wait(timeout=10);exit_time=time.perf_counter();event('process exited',exitCode=process.returncode)
  execution_succeeded=done and process.returncode==0 and termination is None and exit_time<deadline and len(eligible)==len(task['checkpoints']) and failure is None
  status='completed' if execution_succeeded else 'timeout' if termination is not None else 'failure'
 except Exception as e:
  failure={'stage':'supervisor','message':str(e)};status='failure';execution_succeeded=False
  if process is not None and process.poll() is None:event('owned process stopped after supervisor failure',pid=process.pid);process.kill();process.wait(timeout=10)
 finally:
  stop.set()
  for thread in (reader,err):
   if thread is not None:thread.join(timeout=1)
  if process is not None:
   for handle in (process.stdin,process.stdout,process.stderr):
    try:handle.close()
    except Exception:pass
  event('supervision closed')
 checkpoints=[eligible.get(step,{'step':step,'metadata':checkpoint_failures.get(step,{}).get('metadata'),'parentEligible':False,'scientificAvailable':False,'reason':checkpoint_failures.get(step,{}).get('message','No complete checkpoint validated before deadline/termination')}) for step in task['checkpoints']]
 return {'id':task['plan']['id'],'arm':task['plan']['arm'],'seed':task['plan']['seed'],'treatment':TREATMENT,'scientificTreatment':SCIENTIFIC_TREATMENT.copy(),'status':status,'executionSucceeded':execution_succeeded,'checkpoints':checkpoints,'task':taskref,'events':events,'failure':failure,'stderr':b''.join(stderr).decode('utf-8','replace') if process is not None else '', 'rssSamples':samples,'parentRuntime':parent_runtime(),'budgetSeconds':budget_seconds,'seconds':time.perf_counter()-began}

def node_json(project,arguments,input_value=None):
 node=shutil.which('node');require(node,'Node24 runtime required')
 result=subprocess.run([node,str(Path(project)/'research/guard-reference-study.js'),*arguments],cwd=project,input=encode(input_value) if input_value is not None else None,capture_output=True,timeout=180)
 require(result.returncode==0,'Source/identity administration failed: '+result.stderr.decode('utf-8','replace')[-4000:])
 return json.loads(result.stdout)

def inventory(project=ROOT,baseline_loader=None):
 project=Path(project).resolve();loader=baseline_loader or load_local_module(project,'research/guard-reference-baseline.py').load_baseline
 baseline=loader(project)  # Explicitly authorized old-chain authentication; no Q decode or anchors.
 value=node_json(project,['inventory','-'],baseline)
 require(value['scientificTreatment']==SCIENTIFIC_TREATMENT and len(value['runs'])==12,'Prospective fixed matrix differs')
 return value

def freeze(directory,benchmark_file,project=ROOT):
 project=Path(project).resolve();directory=Path(directory).resolve();require(directory!=project and directory.is_relative_to(project),'Evidence directory must remain inside project')
 require(not directory.exists() or not any(directory.iterdir()),'Existing/partial evidence retained; no freeze overwrite')
 value=inventory(project);benchmark_path=local(project,benchmark_file);require(not benchmark_path.is_relative_to(directory),'Benchmark stays outside new evidence')
 benchmark=json.loads(benchmark_path.read_bytes());require(benchmark.get('passed') is True and benchmark.get('artificial') is True and benchmark.get('n')==62 and benchmark.get('rounds')==2000000 and benchmark.get('fullIndependentReplay') is True and benchmark.get('sourcesUnchanged') is True,'Complete maximal artificial production-parent/replay benchmark required')
 require(benchmark.get('sourceHashes')==value['sourceHashes'] and benchmark.get('finalSourceHashes')==value['sourceHashes'],'Final benchmark does not bind current complete source closure')
 require(parent_fingerprint(benchmark['parentRuntime'])==parent_fingerprint(parent_runtime()),'Benchmark Python/zlib backend differs')
 inputs=dict(value['inputHashes'])
 def use(ref):
  require(type(ref.get('bytes')) is int and ref['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',ref.get('sha256','')),'Invalid benchmark artifact identity')
  path=local(project,ref['file']);require(path.stat().st_size==ref['bytes'] and digest(path)==ref['sha256'],'Benchmark artifact changed '+ref['file'])
  require(ref['file'] not in inputs or inputs[ref['file']]==ref['sha256'],'Conflicting benchmark dependency');inputs[ref['file']]=ref['sha256']
 require(isinstance(benchmark.get('artifacts'),list) and benchmark['artifacts'],'Complete benchmark artifact inventory required')
 for ref in benchmark['artifacts']:use(ref)
 use(benchmark['parentRuntimeReceipt']);inputs[benchmark_path.relative_to(project).as_posix()]=digest(benchmark_path)
 plan={'runs':value['runs'],'retainedRuns':12,'T':2000000,'checkpoints':[1000000,2000000],'alpha':.1,'gamma':19/20,'initialization':'positive-zero','scientificTreatment':SCIENTIFIC_TREATMENT.copy(),'clock':'0->1->2->3->4->1','transcript':{'bytesPerRound':120,'roundsPerBlock':10000,'completeBlocksPerRun':200},'hardCaseSeconds':600,'softResourceTargets':{'primarySeconds':3600,'replaySeconds':3600,'sampledRSSBytes':512000000,'newRawEquivalentBytes':1000000000},'scope':'Initial cap then all original62 price indices; no transferred guard floor; full independent replay required'}
 manifest={'schemaVersion':1,'frozenAt':now(),'sourceHashes':value['sourceHashes'],'inputHashes':inputs,'baseline':value['baseline'],'inputs':{'finiteGame':value['finiteGame']},'runtime':value['runtime'],'parentRuntime':parent_runtime(),'benchmark':{'file':benchmark_path.relative_to(project).as_posix(),'sha256':digest(benchmark_path)},'plan':plan}
 directory.mkdir(parents=True,exist_ok=True)
 for name,h in manifest['sourceHashes'].items():
  data=local(project,name).read_bytes();require(hashlib.sha256(data).hexdigest()==h,'Source changed during freeze');save(directory,'sources/'+name,data)
 save(directory,'manifest.json',manifest);return {'directory':directory.relative_to(project).as_posix(),'manifestSha256':digest(directory/'manifest.json'),'sources':len(manifest['sourceHashes']),'inputs':len(inputs),'retainedRuns':12,'scope':'Source/input/runtime freeze only; no static anchors or learning executed'}

def run_inventory(directory,admin_gate,project=ROOT):
 """Exactly one declared inventory. Only callable after explicit administrative GO."""
 directory=Path(directory).resolve();project=Path(project).resolve();node=shutil.which('node');require(node,'Node24 runtime required')
 require((directory/'manifest.json').exists(),'Prospectively frozen manifest required')
 require({p.name for p in directory.iterdir()}=={'manifest.json','sources'} and (directory/'sources').is_dir(),'Fresh frozen directory may contain only manifest.json and sources; auxiliary files are outside the study')
 require(not any((directory/n).exists() for n in ('execution-start.json','journal.jsonl','index.json','results.json','completion.json','records','tasks','checkpoints')),'Existing or partial run retained; no rerun/overwrite')
 manifest_bytes=(directory/'manifest.json').read_bytes();manifest_hash=hashlib.sha256(manifest_bytes).hexdigest();manifest=json.loads(manifest_bytes)
 require(parent_fingerprint(manifest['parentRuntime'])==parent_fingerprint(parent_runtime()),'Frozen Python/zlib parent runtime differs')
 require(strict_equal(manifest['plan']['scientificTreatment'],SCIENTIFIC_TREATMENT),'Frozen support treatment differs')
 require(len(manifest['plan']['runs'])==12 and manifest['plan']['T']==2_000_000 and manifest['plan']['checkpoints']==[1_000_000,2_000_000],'Primary declared matrix differs')
 admin=Path(admin_gate).resolve();require(not admin.is_relative_to(directory),'Administrative receipt must be outside the evidence directory');require(admin.is_relative_to(project) and admin!=project,'Administrative receipt must be project-relative');gate=json.loads(admin.read_bytes())
 require(gate.get('passed') is True and gate.get('studyManifestHash')==manifest_hash and gate.get('sourcesVerified') is True and gate.get('inputsVerified') is True,'Separate passed administrative source/input GO required')
 for key,name in [('auditorSourceHash','research/audit-guard-reference-study.py'),('controlAuditorSourceHash','research/replay-guard-reference.js'),('replayCoreSourceHash','research/audit-guard-reference.js')]:
  token=gate.get(key);require(isinstance(token,str) and re.fullmatch('[a-f0-9]{64}',token) and token==manifest.get('sourceHashes',{}).get(name),'Administrative checker source binding differs: '+key)
 def verify_frozen():
  completed=subprocess.run([node,str(project/'research/guard-reference-study.js'),'verify',str(directory)],cwd=project,capture_output=True,text=True,timeout=120)
  require(completed.returncode==0,'Frozen dependency/runtime check failed: '+completed.stderr[-3000:]);value=json.loads(completed.stdout);require(value.get('passed') is True,'Frozen verification did not pass')
 verify_frozen();began=time.perf_counter();start={'startedAt':now(),'manifestSha256':manifest_hash,'adminGateSha256':digest(admin),'adminGate':{'file':admin.relative_to(project).as_posix(),'bytes':admin.stat().st_size,'sha256':digest(admin)},'software':manifest['runtime'],'runIds':[p['id'] for p in manifest['plan']['runs']],'scope':'ONE primary inventory; accepted checkpoints remain pending independent full replay'};save(directory,'execution-start.json',start)
 records=[];index=[];raw_equivalent=0;dense_stored_bytes=0
 with (directory/'journal.jsonl').open('xb') as journal:
  def log(kind,**fields):journal.write((json.dumps({'at':now(),'type':kind,**fields},separators=(',',':'))+'\n').encode());journal.flush();os.fsync(journal.fileno())
  anchor_ref=None;anchor_failure=None
  try:
   physical=json.loads(readref(project,manifest['inputs']['finiteGame']));anchors=load_local_module(project,'research/guard-reference-analysis.py').stage_anchors(physical['finite']);anchor_ref=save(directory,'stage-anchors.json',anchors);log('static anchors retained',reference=anchor_ref)
  except Exception as exc:
   anchor_failure={'message':str(exc),'stage':'static full-grid anchors'};log('static anchors unavailable',failure=anchor_failure)
  for plan in manifest['plan']['runs']:
   case_began=time.perf_counter();log('run started',id=plan['id']);ref=manifest['inputs']['finiteGame']
   try:
    raw=json.loads(readref(project,ref));require(raw.get('scenario',{}).get('id')=='base-g15-t1' and len(raw['finite']['prices'])==62,'Original game identity differs')
    task={'plan':plan,'scientificTreatment':SCIENTIFIC_TREATMENT.copy(),'record':raw,'finite':raw['finite'],'originalTargets':raw.get('originalTargets',[]),'finiteGameRef':ref,'software':manifest['runtime'],'T':manifest['plan']['T'],'checkpoints':manifest['plan']['checkpoints'],'manifestSha256':manifest_hash,'executionMode':'frozen-primary','projectRoot':'.'}
    precase_seconds=time.perf_counter()-case_began;remaining=manifest['plan']['hardCaseSeconds']-precase_seconds;require(remaining>0,'Case deadline expired during precase validation')
    record=supervise(task,directory,project,budget_seconds=remaining,node=node,case_source=project/'research/guard-reference-case.js');record['precaseSeconds']=precase_seconds;record['wholeCaseSeconds']=time.perf_counter()-case_began
   except Exception as e:
    record={'id':plan['id'],'arm':plan['arm'],'seed':plan['seed'],'treatment':TREATMENT,'scientificTreatment':SCIENTIFIC_TREATMENT.copy(),'status':'input failure','executionSucceeded':False,'failure':{'message':str(e),'stage':'precase'},'events':[],'rssSamples':[],'checkpoints':[{'step':step,'metadata':None,'parentEligible':False,'scientificAvailable':False,'reason':'Precase input failure: '+str(e)} for step in manifest['plan']['checkpoints']]}
   for cp in record['checkpoints']:
    if cp['parentEligible']:
     try:
      meta=json.loads(readref(directory,cp['metadata']));raw_equivalent+=sum(r['rawBytes'] for refs in meta['artifacts'].values() for r in refs);dense_stored_bytes+=sum(r['bytes'] for refs in meta['artifacts'].values() for r in refs)
     except Exception as e:cp['parentEligible']=False;cp['reason']='Post-validation artifact drift: '+str(e);record['executionSucceeded']=False;record['status']='post-validation failure'
   record['manifestSha256']=manifest_hash;record_ref=save(directory,'records/'+plan['id']+'.json',record);records.append(record);index.append({'id':plan['id'],**record_ref,'status':record['status']});log('run retained',id=plan['id'],record=record_ref,status=record['status'])
  final_check={'passed':True,'checkedAt':now(),'failure':None}
  try:verify_frozen()
  except Exception as e:final_check={'passed':False,'checkedAt':now(),'failure':str(e)}
  log('inventory completed',retainedRuns=len(records),finalFrozenDependencyCheck=final_check)
 index_ref=save(directory,'index.json',{'manifestSha256':manifest_hash,'records':index});results_ref=save(directory,'results.json',{'manifestSha256':manifest_hash,'stageAnchors':anchor_ref,'stageAnchorsFailure':anchor_failure,'records':records})
 samples=[s for r in records for s in r['rssSamples']];node_samples=[s['nodeProcessRSSBytes'] for s in samples if s['nodeProcessRSSBytes'] is not None];paired=[s['nodeProcessRSSBytes']+s['supervisorRSS']['bytes'] for s in samples if s['supervisorRSS']['bytes'] is not None and s['nodeProcessRSSBytes'] is not None]
 stored_bytes=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file());failures=sum(not r['executionSucceeded'] for r in records);eligible=sum(cp['parentEligible'] for r in records for cp in r['checkpoints'])
 completion={'manifestSha256':manifest_hash,'parentRuntime':parent_runtime(),'executionStartSha256':digest(directory/'execution-start.json'),'journalSha256':digest(directory/'journal.jsonl'),'indexSha256':index_ref['sha256'],'resultsSha256':results_ref['sha256'],'completedAt':now(),'inventoryComplete':len(records)==12,'primaryPassed':len(records)==12 and failures==0 and final_check['passed'] and anchor_ref is not None,'executionPassed':len(records)==12 and failures==0,'anchorCalculationPassed':anchor_ref is not None,'stageAnchorsSha256':anchor_ref['sha256'] if anchor_ref else None,'stageAnchorsFailure':anchor_failure,'retainedRuns':len(records),'retainedCheckpointSlots':sum(len(r['checkpoints']) for r in records),'parentEligibleCheckpoints':eligible,'executionFailures':failures,'budgetFailures':sum(r['status']=='timeout' for r in records),'fullTrainingReplay':False,'scientificAcceptance':'Pending independently authored full replay; primary execution success does not imply scientific acceptance','finalFrozenDependencyCheck':final_check,'resources':{'seconds':time.perf_counter()-began,'largestSampledNodeProcessRSSBytes':max(node_samples,default=None),'largestApproximatelyPairedRSSBytes':max(paired,default=None),'pairedRSSUnavailableReason':None if paired else 'No paired working-set sample available','rawEquivalentEligibleCheckpointBytes':raw_equivalent,'storedBytesBeforeCompletion':stored_bytes,'scope':'Process-level samples; paired sums are approximate, not a continuous/private peak. Gzip bytes differ from complete dense canonical raw bytes.'}}
 resource=completion['resources'];resource['eligibleCompressedDenseBytes']=dense_stored_bytes;resource['rawEquivalentOutputBytesBeforeCompletion']=stored_bytes-dense_stored_bytes+raw_equivalent if eligible==24 else None;resource['rawEquivalentOutputUnavailableReason']=None if eligible==24 else 'Partial/unvalidated checkpoint artifacts retained; only validated canonical dense bytes and actual stored bytes are counted separately'
 resource['sampledPairedRSSSoftTargetExceeded']=max(paired)>512_000_000 if paired else None;resource['rawEquivalentOutputSoftTargetExceeded']=resource['rawEquivalentOutputBytesBeforeCompletion']>1_000_000_000 if resource['rawEquivalentOutputBytesBeforeCompletion'] is not None else None;resource['primarySecondsSoftTargetExceeded']=resource['seconds']>3600
 save(directory,'completion.json',completion);return completion

if __name__=='__main__':
 parser=argparse.ArgumentParser(description='Prospective reference source administration and separately gated execution')
 parser.add_argument('mode',choices=['runtime','inventory','freeze','run']);parser.add_argument('--directory',default=str(ROOT/'research/guard-reference-results'));parser.add_argument('--admin-gate');parser.add_argument('--benchmark');args=parser.parse_args()
 if args.mode=='runtime':result=parent_runtime()
 elif args.mode=='inventory':result=inventory()
 elif args.mode=='freeze':require(args.benchmark,'Explicit final source-bound artificial benchmark required');result=freeze(args.directory,args.benchmark)
 else:require(args.admin_gate,'Explicit independent administrative GO required');result=run_inventory(args.directory,args.admin_gate)
 print(json.dumps(result))
