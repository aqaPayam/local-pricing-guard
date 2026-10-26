// Pure checked representation transforms for the prospective manual game.
// No Q values, evidence IO, optimization, reward execution or learning here.
const need=(ok,message)=>{if(!ok)throw Error(message);};
function shape(finite,control){
 const n=finite?.prices?.length;need(Number.isInteger(n)&&n>0&&n<=62,'Finite price dimension missing');
 need(finite.prices.every((p,i)=>Number.isFinite(p)&&(!i||p>finite.prices[i-1])),'Increasing saved prices required');
 need(Number.isInteger(finite.capIndex)&&finite.capIndex>=0&&finite.capIndex<n,'Physical cap index differs');
 need(finite.sets?.length===n&&finite.sets.every(s=>s.length>0&&s.every((a,i)=>Number.isInteger(a)&&a>=0&&a<n&&(!i||a>s[i-1]))),'Original nonempty ascending guard masks required');
 const phases=control?.id==='startup-only'?2:control?.id==='selected95'&&control.period===4?4:null;
 need(phases&&control.phases===phases&&(control.id!=='startup-only'||control.period===null),'Original two-phase startup/K4 identity differs');
 const rows=phases*n*n,cap=Array.from({length:finite.capIndex+1},(_,i)=>i),support=(phase,rival)=>phase===0?cap:finite.sets[rival],offsets=[0];
 for(let row=0;row<rows;row++)offsets.push(offsets.at(-1)+support(Math.floor(row/(n*n)),row%n).length);
 return {n,phases,rows,support,offsets,cells:offsets.at(-1)};
}
export function checkpointGameData({id,seed,finite,control,terminal,greedyOwn,counts,overflow=[[],[]],source},{expectedRounds=2000000}={}){
 const L=shape(finite,control),{n,phases,rows,offsets,cells,support}=L;
 need(typeof id==='string'&&Number.isSafeInteger(seed)&&Number.isSafeInteger(expectedRounds)&&expectedRounds>0,'Checkpoint identity/horizon missing');
 need(terminal&&Number.isInteger(terminal.phase)&&terminal.phase>=0&&terminal.phase<phases&&terminal.previousIndices?.length===2&&terminal.previousIndices.every(a=>Number.isInteger(a)&&a>=0&&a<n),'Actual terminal state malformed');
 need(terminal.phase===(control.id==='startup-only'?1:expectedRounds%4),'Actual next clock phase differs');
 need(greedyOwn?.length===2&&counts?.length===2&&overflow?.length===2,'Both original firms required');
 const actionCounts=[],worldPolicies=[[],[]];
 for(let actor=0;actor<2;actor++){
  need(greedyOwn[actor].length===rows&&counts[actor].length===cells,'Saved greedy/count dimensions differ');
  const decoded=Array.from(counts[actor]);need(decoded.every(v=>Number.isInteger(v)&&v>=0&&v<=65535),'Original u16 count malformed');
  const seen=new Set();for(const pair of overflow[actor]){
   need(Array.isArray(pair)&&pair.length===2,'Malformed count overflow entry');const [cell,count]=pair;
   need(Number.isInteger(cell)&&cell>=0&&cell<cells&&!seen.has(cell)&&decoded[cell]===65535&&Number.isInteger(count)&&count>65535&&count<=expectedRounds,'Count overflow identity malformed');seen.add(cell);decoded[cell]=count;
  }
  need(decoded.reduce((s,v)=>s+v,0)===expectedRounds,'Saved exact action-count horizon differs');
  for(let row=0;row<rows;row++)need(support(Math.floor(row/(n*n)),row%n).includes(greedyOwn[actor][row]),'Saved own-coordinate greedy action illegal');
  for(let state=0;state<rows;state++){
   const phase=Math.floor(state/(n*n)),a=Math.floor(state/n)%n,b=state%n,row=phase*n*n+(actor===0?a*n+b:b*n+a);
   worldPolicies[actor].push(greedyOwn[actor][row]);
  }
  actionCounts.push(decoded);
 }
 return {id,seed,control:{...control},status:'available',available:true,reason:null,n,phases,terminal:{...terminal,previousIndices:[...terminal.previousIndices]},
  originalWorldPolicies:{A:worldPolicies[0],B:worldPolicies[1],encoding:'Original-index actions indexed by WORLD (phase,previousA,previousB); B mapped once from saved own/rival rows'},
  trainingCounts:{A:actionCounts[0],B:actionCounts[1],rowOffsets:offsets,expectedRounds,encoding:'Exact decoded u32 compact counts; OWN/rival rows, ascending original legal actions. B support lookup swaps history; greedy world actions do not.'},source};
}
export function responseGamePolicy(record,actions,finite){
 const L=shape(finite,record.control);
 if(!record.scientificAvailable)return {recordId:record.id,scientificAvailable:false,executionSucceeded:record.executionSucceeded,status:record.status,actions:null,reason:record.failure?.message??'No independently accepted complete response certificate',source:record.optimizer?.responsePolicy??null};
 need(record.certificate?.passed===true&&['A','B'].includes(record.focal)&&actions?.length===L.rows,'Certified response policy identity/dimension differs');
 const out=Array.from(actions);for(let state=0;state<L.rows;state++){
  const phase=Math.floor(state/(L.n*L.n)),a=Math.floor(state/L.n)%L.n,b=state%L.n;
  need(L.support(phase,record.focal==='A'?b:a).includes(out[state]),'Response action illegal at an off-path world state');
 }
 return {recordId:record.id,scientificAvailable:true,executionSucceeded:record.executionSucceeded,status:record.status,actions:out,reason:null,encoding:'Original-index focal actions indexed by WORLD (phase,previousA,previousB)',source:record.optimizer?.responsePolicy??null};
}
