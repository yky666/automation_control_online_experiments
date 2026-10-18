// Electrical netlists. The solver stamps KCL/voltage constraints, never a preset TF.
export const COMPONENTS={R:['p','n'],C:['p','n'],OpAmp:['plus','minus','out'],V:['p','n'],VCVS:['p','n','cp','cn']};
export const COMPONENT_LABELS={R:'电阻 / Ω',C:'电容 / F',OpAmp:'运算放大器',V:'输入电压源 / V',VCVS:'受控电压源 / V/V'};
export function circuitTemplate(lab,task,params={},design={}){
 const components=[];let seq=0;
 const add=(type,ports,value,label)=>{const id=type+(++seq);components.push({id,type,ports,value,label:label||id});return id};
 const r=(p,n,v=1e5,label)=>add('R',{p,n},v,label),c=(p,n,v=1e-6,label)=>add('C',{p,n},v,label);
 const amp=(minus,out,label)=>{const plus='g'+seq;r(plus,'0',1e5);return add('OpAmp',{plus,minus,out},0,label)};
 const stage=(input,out,kind,{R1=1e5,R2=1e5,C=1e-6}={})=>{
  const m='m'+seq;
  if(kind==='d')c(input,m,C);else r(input,m,R1,'输入电阻');
  if(kind==='pd')c(input,m,C,'输入旁路电容');
  if(kind==='i')c(m,out,C,'积分电容');
  else if(kind==='pi'){const mid='z'+seq;r(m,mid,R2);c(mid,out,C)}
  else {r(m,out,R2,'反馈电阻');if(kind==='lag')c(m,out,C,'反馈电容')}
  amp(m,out,kind);return m;
 };
 add('V',{p:'in',n:'0'},1,'信号发生器');
 let note='',output='out';
 if(lab===2){
  const kind={integrator:'i',inertia:'lag'}[task]||task,K=Math.abs(params.K??1),T=params.T??.1;
  const R1=1e5,R2=R1*K,C=kind==='i'?T/(R1*K):T/(['pd','d'].includes(kind)?R1:R2);
  stage('in','out',kind,{R1,R2,C});
  note='保留反相电路负号。R、C 为实际连接元件；D/PD 的阶跃尖峰取决于输入上升时间、带宽和步长。';
 }else if(lab===4){
  const m=stage('in','s1','i');r('fb',m,1e5,'反馈求和电阻');stage('s1','s2','lag',{C:(params.T1??.1)/1e5});
  stage('s2','s3',task==='reduced'?'p':'lag',{C:(params.T2??.1)/1e5});
  stage('s3','out','p',{R2:1e5*(params.K??1)});stage('out','fb','p');
  note='按课件接入积分、惯性、比例和反馈反相器，共五个运放。降阶工况将第二惯性级改成单位反相器，保持负反馈极性。';
 }else if(lab===5){
  if(task==='bandwidth'){stage('in','s1','p',{R2:1e5*(params.K??1)});stage('s1','out','p');note='两级反相放大；选择有限带宽模式观察增益带宽与输出限幅。GBW 是教学假设，可编辑，不代表指定芯片实测参数。'}
  else if(task==='frequency_inertia'){stage('in','out','lag',{R2:1e5*(params.K??1),C:(params.T??.001)/(1e5*(params.K??1))});note='保留反相惯性电路符号；与正增益归一化模型比较时需考虑额外 180° 相位。'}
  else {const wn=params.wn??Math.sqrt(500),zeta=params.zeta??10/(2*Math.sqrt(500)),m=stage('in','s1','i');r('out',m,1e5);stage('s1','s2','lag',{C:1/(2*zeta*wn*1e5)});stage('s2','out','p',{R2:1e5*wn/(20*zeta)});note='课件三运放二阶电路：默认 100 kΩ、1 μF、R3=500 kΩ；按当前 ωn、ζ 重建时改相应 R/C。输出相对输入反相，默认 −500/(s²+10s+500)。';}
 }else if(lab===6){
  add('VCVS',{p:'error',n:'0',cp:'in',cn:'out'},1,'单位负反馈比较器');
  const alpha=design.alpha??params.alpha??6,wm=design.wm??params.wm??6,wz=design.wz??wm/Math.sqrt(alpha),C=1e-6,R1=1/wz/C,R2=R1/(alpha-1);
  const passive=['lead2','lead_example2'].includes(task);let prev='error';
  if(passive){for(let i=1;i<=2;i++){const n='lead'+i;r(prev,n,R1,'无源 R1');c(prev,n,C);r(n,'0',R2,'无源 R2');const b='buffer'+i;add('OpAmp',{plus:n,minus:b,out:b},0,'级间缓冲器');prev=b;}stage(prev,'boost1','p',{R2:alpha*alpha*1e5});stage('boost1','control','p');prev='control';}
  else {const m='leadMinus';r(prev,'leadMid',R2);r('leadMid',m,R1);c('leadMid',m,C);r(m,'leadRaw',R1+R2);amp(m,'leadRaw','有源超前');stage('leadRaw','control','p');prev='control';}
  let gain,lags,integrators;
  if(task==='lead1'){gain=params.Kv??20;lags=[.5];integrators=1;}
  else if(task==='lead_example1'){gain=params.K??1000;lags=[.1,.001];integrators=1;}
  else if(task==='lead_example2'){gain=params.K??10;lags=[.2];integrators=2;}
  else {gain=params.K??10;lags=[.5,1/30];integrators=1;}
  for(let i=0;i<integrators;i++){const n='plantI'+i;stage(prev,n,'i',{C:1e-5});prev=n}
  for(let i=0;i<lags.length;i++){const n='plantL'+i;stage(prev,n,'lag',{C:lags[i]/1e5});prev=n}
  const stages=integrators+lags.length;
  stage(prev,stages%2===0?'sign':'out','p',{R2:gain*1e5});if(stages%2===0)stage('sign','out','p');
  note=passive?'两级无源超前网络含单位缓冲运放，避免级间加载，并用真实电阻放大器补偿 α² 衰减。可删除缓冲器并重新接线研究加载效应。':'有源超前含实际 R1、R2、R3、C 和极性补偿运放；被控对象由积分、RC 惯性电路实现。';
 }else {
  stage('in','out','lag');note='本章以数学/信号模型为主。此处为可自由搭建的 RC 电路练习；本章指定实验请使用下面的信号框图及原生 Simulink。';
 }
 return {version:1,lab,task,title:`实验 ${lab} · ${task} 元件电路`,components,output,note,opamp:{mode:lab===5&&task==='bandwidth'?'finite':'ideal',A0:1e5,GBW:params.GBW??1e6,rail:15},settings:{signal:lab===5?'sine':'step',amplitude:lab===5?(params.A??.05):1,frequency:params.frequency??1,stop:lab===5?10/(params.frequency||1):lab===4?4:task==='lead_example1'?.2:5,points:[4,5].includes(lab)?6001:3001,rise:task==='lead_example1'?.0001:.02}};
}
export function validateCircuit(g){
 const errors=[];if(!g||!Array.isArray(g.components)||g.components.length<1||g.components.length>100)return ['需包含 1～100 个元件'];
 const ids=new Set(),nets=new Set(['0']);
 for(const a of g.components){if(!a||!/^[A-Za-z][A-Za-z0-9_]{0,40}$/.test(a.id)||ids.has(a.id)||!COMPONENTS[a.type]){errors.push('元件 ID 重复或类型无效');continue}ids.add(a.id);
  for(const p of COMPONENTS[a.type]){const n=a.ports?.[p];if(typeof n!=='string'||!/^([A-Za-z][A-Za-z0-9_]{0,30}|0)$/.test(n))errors.push(a.id+' 的端子 '+p+' 节点名无效');else nets.add(n)}
  if(['R','C'].includes(a.type)&&!(Number.isFinite(a.value)&&a.value>0&&a.value<1e12))errors.push(a.id+' 元件值必须为正有限数');
  if(['V','VCVS'].includes(a.type)&&!Number.isFinite(a.value))errors.push(a.id+' 源参数无效');
 }
 if(nets.size>65)errors.push('最多支持 64 个非接地节点');if(!nets.has(g.output)||g.output==='0')errors.push('请选择有效的非接地输出节点');
 if(!g.components.some(c=>c?.type==='V'))errors.push('需要至少一个独立电压源');
 if(!['ideal','finite'].includes(g.opamp?.mode)||![g.opamp?.A0,g.opamp?.GBW,g.opamp?.rail].every(x=>Number.isFinite(x)&&x>0))errors.push('运放模式/增益/带宽/限幅无效');
 const s=g.settings;if(!s||!['step','sine','ramp'].includes(s.signal)||![s.amplitude,s.frequency,s.stop,s.points,s.rise].every(Number.isFinite)||s.stop<=0||s.stop>120||s.frequency<=0||s.frequency>1e8||Math.abs(s.amplitude)>100||s.rise<0||s.points<201||s.points>20001||!Number.isInteger(s.points))errors.push('激励或采样参数超出范围');
 return [...new Set(errors)];
}
export function inputVoltage(t,s){return s.amplitude*(s.signal==='sine'?Math.sin(2*Math.PI*s.frequency*t):s.signal==='ramp'?t:Math.min(t/Math.max(s.rise,1e-15),1));}
// Row-scaled LU with partial pivoting. Factor once per active saturation pattern.
export function factor(matrix){
 const a=matrix.map(row=>Float64Array.from(row)),n=a.length,scale=a.map(row=>Math.max(...Array.from(row,Math.abs))),piv=[];
 for(let i=0;i<n;i++){if(!(scale[i]>0))throw Error('电路奇异：有悬空节点、缺少参考地或冗余理想源');for(let j=0;j<n;j++)a[i][j]/=scale[i]}
 for(let k=0;k<n;k++){let p=k;for(let i=k+1;i<n;i++)if(Math.abs(a[i][k])>Math.abs(a[p][k]))p=i;
  if(Math.abs(a[p][k])<1e-14)throw Error('电路奇异：检查断路、短接的电压源、运放负反馈和接地');piv.push(p);[a[k],a[p]]=[a[p],a[k]];
  for(let i=k+1;i<n;i++){a[i][k]/=a[k][k];for(let j=k+1;j<n;j++)a[i][j]-=a[i][k]*a[k][j]}
 }
 return b=>{const x=Float64Array.from(b,(v,i)=>v/scale[i]);for(let k=0;k<n;k++){const p=piv[k];[x[k],x[p]]=[x[p],x[k]]}for(let k=0;k<n;k++){for(let i=k+1;i<n;i++)x[i]-=a[i][k]*x[k]}
  for(let i=n-1;i>=0;i--){for(let j=i+1;j<n;j++)x[i]-=a[i][j]*x[j];x[i]/=a[i][i]}return x;};
}
export function simulateCircuit(g){
 const errors=validateCircuit(g);if(errors.length)throw Error(errors.join('；'));
 const nets=[...new Set(g.components.flatMap(a=>Object.values(a.ports)))].filter(n=>n!=='0'),index=Object.fromEntries(nets.map((n,i)=>[n,i]));
 const branches=g.components.filter(c=>['V','VCVS','OpAmp'].includes(c.type)),bi=Object.fromEntries(branches.map((c,i)=>[c.id,nets.length+i])),N=nets.length+branches.length;
 const s=g.settings,dt=s.stop/(s.points-1),finite=g.opamp.mode==='finite',amps=branches.filter(c=>c.type==='OpAmp'),cache=new Map();
 if(s.signal==='sine'&&s.frequency*dt>1/40)throw Error('正弦采样不足：请缩短时长或增加采样点，使每周期至少 40 点');
 const vv=(x,n)=>n==='0'?0:x[index[n]],stamp=(a,i,j,v)=>{if(i!=null&&j!=null)a[i][j]+=v};
 const matrix=mask=>{const a=Array.from({length:N},()=>Array(N).fill(0));
  const conduct=(p,n,v)=>{p=index[p];n=index[n];stamp(a,p,p,v);stamp(a,n,n,v);stamp(a,p,n,-v);stamp(a,n,p,-v)};
  for(const c of g.components){const p=c.ports,k=bi[c.id];
   if(c.type==='R'||c.type==='C')conduct(p.p,p.n,c.type==='R'?1/c.value:c.value/dt);
   else if(c.type==='OpAmp'){
    stamp(a,index[p.out],k,1);
    if(!finite){stamp(a,k,index[p.plus],1);stamp(a,k,index[p.minus],-1)}
    else {const sat=mask[amps.indexOf(c)]||0;stamp(a,k,index[p.out],sat?1:1+g.opamp.A0/(2*Math.PI*g.opamp.GBW*dt));if(!sat){stamp(a,k,index[p.plus],-g.opamp.A0);stamp(a,k,index[p.minus],g.opamp.A0)}}
   }else {stamp(a,index[p.p],k,1);stamp(a,index[p.n],k,-1);stamp(a,k,index[p.p],1);stamp(a,k,index[p.n],-1);if(c.type==='VCVS'){stamp(a,k,index[p.cp],-c.value);stamp(a,k,index[p.cn],c.value)}}
  }return a;
 };
 let x=new Float64Array(N),time=[],input=[],output=[],traces=Object.fromEntries(nets.map(n=>[n,[]])),clipped=0;
 for(let step=0;step<s.points;step++){
  const t=step*dt,base=new Float64Array(N);
  for(const c of g.components){const p=c.ports;if(c.type==='C'){const i=c.value/dt*(vv(x,p.p)-vv(x,p.n));if(index[p.p]!=null)base[index[p.p]]+=i;if(index[p.n]!=null)base[index[p.n]]-=i}
   else if(c.type==='V')base[bi[c.id]]=inputVoltage(t,s)*c.value;
   else if(c.type==='OpAmp'&&finite)base[bi[c.id]]=g.opamp.A0/(2*Math.PI*g.opamp.GBW*dt)*vv(x,p.out);
  }
  let mask=amps.map(()=>0),next,converged=false;
  for(let it=0;it<30;it++){
   const key=mask.join(','),rhs=Float64Array.from(base);for(let j=0;j<amps.length;j++)if(mask[j])rhs[bi[amps[j].id]]=mask[j]*g.opamp.rail;
   let entry=cache.get(key);if(!entry){const a=matrix(mask);entry={a,solve:factor(a)};if(cache.size<128)cache.set(key,entry)}next=entry.solve(rhs);
   if(!finite){converged=true;break}
   const nm=amps.map((c,j)=>{const v=vv(next,c.ports.out),raw=(g.opamp.A0*(vv(next,c.ports.plus)-vv(next,c.ports.minus))+base[bi[c.id]])/(1+g.opamp.A0/(2*Math.PI*g.opamp.GBW*dt));return mask[j]?(mask[j]*raw<g.opamp.rail-1e-9?0:mask[j]):v>g.opamp.rail+1e-9?1:v< -g.opamp.rail-1e-9?-1:0});
   if(nm.every((v,j)=>v===mask[j])){converged=true;if(nm.some(Boolean))clipped++;break}mask=nm;
  }
  if(!converged)throw Error('限幅迭代未收敛，请增加采样点或检查正反馈');
  if(!next||Array.from(next).some(v=>!Number.isFinite(v)||Math.abs(v)>1e12))throw Error('电路响应发散或电流/电压超出求解范围，请检查反馈与仿真时长');
  x=next;time.push(t);input.push(inputVoltage(t,s));output.push(vv(x,g.output));for(const n of nets)traces[n].push(vv(x,n));
 }
 const metrics={min:Math.min(...output),max:Math.max(...output),final:output.at(-1),clippedSamples:clipped};
 if(s.signal==='sine'){const start=Math.floor(s.points*.75);let ss=0,cc=0,sc=0,sy=0,cy=0;for(let i=start;i<s.points;i++){const a=Math.sin(2*Math.PI*s.frequency*time[i]),b=Math.cos(2*Math.PI*s.frequency*time[i]);ss+=a*a;cc+=b*b;sc+=a*b;sy+=a*output[i];cy+=b*output[i]}const det=ss*cc-sc*sc;if(det>1e-15){const a=(sy*cc-cy*sc)/det,b=(cy*ss-sy*sc)/det;metrics.amplitude=Math.hypot(a,b);metrics.phase=Math.atan2(b,a)*180/Math.PI;metrics.gainDB=20*Math.log10(metrics.amplitude/Math.abs(s.amplitude))}}
 return {kind:'circuit',engine:'browser-mna',method:'改进节点分析 MNA · 隐式欧拉',createdAt:new Date().toISOString(),circuit:structuredClone(g),time,input,output,traces,metrics,dt};
}
export function circuitCsv(result){return 'time,input,output\n'+result.time.map((t,i)=>[t,result.input[i],result.output[i]].join(',')).join('\n');}
export function parseCircuitCsv(text,circuit){
 const lines=text.replace(/^\uFEFF/,'').trim().split(/\r?\n/),header=lines.shift()?.trim().toLowerCase().split(',');if(header?.join(',')!=='time,input,output')throw Error('CSV 表头必须为 time,input,output');
 if(lines.length<2||lines.length>200000)throw Error('CSV 需包含 2～200000 行');const rows=lines.map(l=>l.split(',').map(v=>v.trim()===''?NaN:Number(v)));if(rows.some((r,i)=>r.length!==3||r.some(v=>!Number.isFinite(v))||i>0&&r[0]<=rows[i-1][0]))throw Error('CSV 数值无效或时间未严格递增');
 return {kind:'circuit',engine:'imported-csv',method:'用户导入的外部运行数据（来源需自行确认）',createdAt:new Date().toISOString(),circuit:structuredClone(circuit),time:rows.map(r=>r[0]),input:rows.map(r=>r[1]),output:rows.map(r=>r[2]),traces:{},metrics:{min:rows.reduce((a,r)=>Math.min(a,r[2]),Infinity),max:rows.reduce((a,r)=>Math.max(a,r[2]),-Infinity),final:rows.at(-1)[2]}};
}
