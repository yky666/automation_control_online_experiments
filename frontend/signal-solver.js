import {validateGraph,portCount} from './blocks.js';
import {factor} from './circuits.js';
const conv=(a,b)=>{const c=Array(a.length+b.length-1).fill(0);a.forEach((v,i)=>b.forEach((w,j)=>c[i+j]+=v*w));return c};
const plus=(a,b)=>{const n=Math.max(a.length,b.length);return Array.from({length:n},(_,i)=>(a[i-n+a.length]||0)+(b[i-n+b.length]||0))};
// Arithmetic-only expression parser: no eval, statements, property access or functions.
export function numberExpression(text,vars){
 const tokens=String(text).match(/\d*\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?|[A-Za-z_][A-Za-z0-9_]*|[()+\-*/^]/g)||[];
 if(tokens.join('')!==String(text).replace(/\s/g,''))throw Error('仅支持数值、变量和 + - * / ^ () 算术表达式');let i=0;
 function atom(){let x,t=tokens[i++];if(t==='-')return -atom();if(t==='+')return atom();if(t==='('){x=expression();if(tokens[i++]!==')')throw Error('括号不匹配')}else if(t&&/^[\d.]/.test(t))x=Number(t);else if(Object.hasOwn(vars,t))x=vars[t];else throw Error('未知变量：'+t);if(tokens[i]==='^'){i++;x=x**atom()}return x}
 function product(){let x=atom();while(['*','/'].includes(tokens[i])){const op=tokens[i++],r=atom();x=op==='*'?x*r:x/r}return x}
 function expression(){let x=product();while(['+','-'].includes(tokens[i])){const op=tokens[i++],r=product();x=op==='+'?x+r:x-r}return x}
 const n=expression();if(i!==tokens.length||!Number.isFinite(n))throw Error('参数表达式无效');return n;
}
export function vectorExpression(text,vars){
 const str=text.trim();if(Array.isArray(vars[str]))return checkedVector(vars[str]);
 if(!str.startsWith('['))return [numberExpression(str,vars)];const end=str.indexOf(']');if(end<0)throw Error('系数向量缺少 ]');
 const values=str.slice(1,end).trim().split(/[\s,;]+/).filter(Boolean).map(v=>numberExpression(v,vars));let suffix=str.slice(end+1).trim();
 if(suffix){const op=suffix[0],v=numberExpression(suffix.slice(1),vars);if(!['*','/'].includes(op))throw Error('向量后只支持乘除标量');return checkedVector(values.map(x=>op==='*'?x*v:x/v))}return checkedVector(values);
}
function checkedVector(values){if(!values.length||!values.every(Number.isFinite))throw Error('系数向量必须包含有限数值');return values.slice()}
function responseAt(n,d,w){const evalp=a=>a.reduce(([r,i],c)=>[c-i*w,r*w],[0,0]);const [a,b]=evalp(n),[c,e]=evalp(d);return {mag:Math.hypot(a,b)/Math.hypot(c,e),phase:Math.atan2(b,a)-Math.atan2(e,c)}}
export function signalVariables(request,example){
 const m=example.model,p={...m.params,...request.params,A:request.amplitude??1,pi:Math.PI},lab=request.lab_id,id=request.task_id;
 let n=m.num,d=m.den,plantN,plantD;
 if(request.numerator){n=request.numerator;d=request.denominator;}
 else if(lab===1){if(m.closed){const baseN=m.open_num.map(v=>v/(m.params.K||1)*p.K);const baseD=m.open_den;if(id==='dynamic_feedback'){n=conv(baseN,[1,1]);d=plus(baseD,baseN)}else{n=baseN;d=plus(baseD,baseN)}}}
 else if(lab===2){const K=p.K,T=p.T,Tf=p.Tf;n={p:[K],inertia:[K],integrator:[K],d:[K*T,0],pi:[K*T,K],pd:[K*(Tf+T),K]}[id];d={p:[1],inertia:[T,1],integrator:[T,0],d:[Tf,1],pi:[T,0],pd:[Tf,1]}[id];}
 else if(lab===3){if(['second','zero','damping_sweep','frequency_sweep'].includes(id)){n=id==='zero'?[p.wn*p.wn/p.zero,p.wn*p.wn]:[p.wn*p.wn];d=[1,2*p.zeta*p.wn,p.wn*p.wn]}else if(m.closed){n=m.open_num.map(v=>v/(m.params.K||1)*p.K);d=plus(m.open_den,n)}}
 else if(lab===4){n=[10*p.K];d=id==='reduced'?conv([1,0],[p.T1,1]):conv([1,0],conv([p.T1,1],[p.T2,1]));d=plus(d,n);}
 else if(lab===5){if(id==='bandwidth'){n=[p.K];d=[p.K/(2*Math.PI*p.GBW),1]}else if(id==='frequency_inertia'){n=[p.K];d=[p.T,1]}else{n=[p.wn*p.wn];d=[1,2*p.zeta*p.wn,p.wn*p.wn]}}
 else if(lab===6){
  if(id==='lead1'){plantN=[2*p.Kv];plantD=[1,2,0]}
  else if(id==='lead_example1'){plantN=[p.K];plantD=conv([1,0],conv([.1,1],[.001,1]))}
  else if(id==='lead_example2'){plantN=[p.K];plantD=[.2,1,0,0]}
  else {plantN=[p.K];plantD=conv([1,0],conv([.5,1],[1/30,1]))}
  let alpha=p.alpha,wm=p.wm;if(['lead1','lead_example1'].includes(id)){
   let low=1e-8,high=1e8;for(let i=0;i<150;i++){const w=Math.sqrt(low*high);if(responseAt(plantN,plantD,w).mag>1)low=w;else high=w}const wc=Math.sqrt(low*high);let ph=responseAt(plantN,plantD,wc).phase*180/Math.PI;while(ph>0)ph-=360;const phi=p.targetPM-(180+ph)+p.reserve;if(!(phi>0&&phi<85))throw Error('所需超前角需在 0～85° 内');alpha=(1+Math.sin(phi*Math.PI/180))/(1-Math.sin(phi*Math.PI/180));low=1e-8;high=1e10;for(let i=0;i<150;i++){const w=Math.sqrt(low*high);if(responseAt(plantN,plantD,w).mag>1/Math.sqrt(alpha))low=w;else high=w}wm=Math.sqrt(low*high);
  }
  p.alpha=alpha;p.wm=wm;p.wz=wm/Math.sqrt(alpha);p.wp=wm*Math.sqrt(alpha);n=plantN;d=plantD;
  for(let i=0;i<(['lead2','lead_example2'].includes(id)?2:1);i++){n=conv(n,[1/p.wz,1]);d=conv(d,[1/p.wp,1])}d=plus(d,n);
 }
 return {...p,num:n,den:d,plant_num:plantN,plant_den:plantD};
}
export function simulateSignal(graph,request,example){
 const errors=validateGraph(graph);if(errors.length)throw Error(errors.join('；'));
 const vars=signalVariables(request,example),nodes=graph.nodes.filter(b=>b.type!=='Scope'),outputs=Object.fromEntries(nodes.map((b,i)=>[b.id,i])),states={};let N=nodes.length;
 for(const b of nodes){if(b.type==='TransferFcn'){const n=vectorExpression(b.params.Numerator,vars),d=vectorExpression(b.params.Denominator,vars);if(!d.length||d[0]===0||n.length>d.length||d.length>13)throw Error(b.id+' 需为分母首项非零、最高 12 阶的真有理传递函数');states[b.id]={indices:Array.from({length:d.length-1},()=>N++),n,d};}else if(b.type==='Integrator')states[b.id]={indices:[N++]};}
 const signal=request.input_signal||example.model.input_signal;
 const stop=signal==='sine'&&request.auto_duration?Math.max(10/vars.frequency,example.model.input_signal==='sine'?example.model.stop_time:0):request.stop_time??5;
 const points=signal==='sine'?Math.max(request.points??1501,Math.ceil(stop*vars.frequency*60)+1):request.points??1501,dt=stop/(points-1);if(!(stop>0&&stop<=120&&Number.isInteger(points)&&points>=201&&points<=20001))throw Error('时长/采样点数无效，正弦每周期需 60 点且总数不超过 20001；请缩短时长或降低频率');
 const sources=nodes.filter(b=>portCount(b).inputs===0);
 for(const b of sources){
  if(b.type==='SineWave'){
   if(numberExpression(b.params.SampleTime,vars)!==0)throw Error(b.id+'：浏览器仅支持连续正弦源，SampleTime 必须为 0');
   const hz=Math.abs(numberExpression(b.params.Frequency,vars))/(2*Math.PI);
   if(hz*dt>1/60+1e-12)throw Error(b.id+'：正弦采样不足，每周期至少需要 60 点；请增加采样点或缩短时长');
  }
  if(b.type==='FromWorkspace'&&b.params.VariableName.trim()!=='web_input')throw Error(b.id+'：浏览器仅提供 web_input 工作区输入');
 }
 const input=b=>outputs[graph.edges.find(e=>e.to===b.id&&e.port===1)?.from],mat=Array.from({length:N},()=>Array(N).fill(0)),dynamic=[];
 for(const b of nodes){const k=outputs[b.id],j=input(b),p=b.params;mat[k][k]=1;
  if(b.type==='Gain')mat[k][j]-=numberExpression(p.Gain,vars);
  else if(b.type==='Sum')for(let port=1;port<=portCount(b).inputs;port++){const e=graph.edges.find(e=>e.to===b.id&&e.port===port);mat[k][outputs[e.from]]-=p.Inputs[port-1]==='+'?1:-1;}
  else if(b.type==='Derivative'){mat[k][j]-=1/dt;dynamic.push({kind:'derivative',row:k,input:j});}
  else if(b.type==='Integrator'){const s=states[b.id].indices[0];mat[k][s]=-1;mat[s][s]=1;mat[s][j]-=dt;dynamic.push({kind:'state',row:s,initial:numberExpression(p.InitialCondition,vars)});}
  else if(b.type==='TransferFcn'){
   const {indices:s,n,d}=states[b.id],order=s.length,a=d.map(v=>v/d[0]),bn=Array(d.length-n.length).fill(0).concat(n.map(v=>v/d[0])),direct=bn[0];mat[k][j]-=direct;
   for(let l=0;l<order;l++){mat[k][s[l]]-=bn[order-l]-direct*a[order-l];mat[s[l]][s[l]]=1;if(l<order-1)mat[s[l]][s[l+1]]-=dt;else{for(let q=0;q<order;q++)mat[s[l]][s[q]]+=dt*a[order-q];mat[s[l]][j]-=dt}dynamic.push({kind:'state',row:s[l],initial:0})}
  }
 }
 const initialMatrix=mat.map(r=>r.slice());for(const item of dynamic){initialMatrix[item.row].fill(0);initialMatrix[item.row][item.row]=1}
 const solve=factor(mat),initialSolve=factor(initialMatrix),scopes=graph.nodes.filter(b=>b.type==='Scope');
 const channels=scopes.flatMap(scope=>graph.edges.filter(e=>e.to===scope.id).sort((a,b)=>a.port-b.port).map(e=>({...e,label:scopes.length===1?'Scope '+e.port:scope.id+' / '+e.port})));
 const time=[],series=channels.map(()=>[]),sourceTraces=Object.fromEntries(sources.map(b=>[b.id,[]]));let previous=new Float64Array(N);
 const u=t=>vars.A*(signal==='sine'?Math.sin(2*Math.PI*vars.frequency*t):signal==='ramp'?t:signal==='step_ramp'?1+t:signal==='polynomial'?5+2*t+8*t*t:1);
 for(const item of dynamic)if(item.kind==='state')previous[item.row]=item.initial;
 for(let i=0;i<points;i++){const t=i*dt,rhs=new Float64Array(N);for(const b of nodes){const k=outputs[b.id],p=b.params;
  if(b.type==='Step')rhs[k]=numberExpression(t>=numberExpression(p.Time,vars)?p.After:p.Before,vars);
  else if(b.type==='SineWave')rhs[k]=numberExpression(p.Amplitude,vars)*Math.sin(numberExpression(p.Frequency,vars)*t+numberExpression(p.Phase,vars));
  else if(b.type==='Ramp')rhs[k]=numberExpression(p.InitialOutput,vars)+Math.max(0,t-numberExpression(p.start,vars))*numberExpression(p.slope,vars);
  else if(b.type==='FromWorkspace')rhs[k]=u(t);
 }
 for(const item of dynamic)rhs[item.row]=item.kind==='derivative'?(i===0?0:-previous[item.input]/dt):previous[item.row];const x=(i===0?initialSolve:solve)(rhs);if(Array.from(x).some(v=>!Number.isFinite(v)||Math.abs(v)>1e12))throw Error('信号模型响应发散或超出范围');previous=x;time.push(t);channels.forEach((e,j)=>series[j].push(x[outputs[e.from]]));sources.forEach(b=>sourceTraces[b.id].push(x[outputs[b.id]]));}
 return {time,input:sources.length?sourceTraces[sources[0].id]:time.map(()=>0),inputLabel:sources.length?sources[0].id+' · '+sources[0].type:'无外部激励（零参考线）',sourceTraces,channels:channels.map(e=>({label:e.label,scope:e.to,port:e.port,from:e.from})),output:series[0],traces:Object.fromEntries(series.map((y,i)=>[channels[i].label,y])),method:'浏览器信号框图 · 隐式欧拉',createdAt:new Date().toISOString(),engine:'browser-signal',graph:structuredClone(graph),request:structuredClone(request)};
}
