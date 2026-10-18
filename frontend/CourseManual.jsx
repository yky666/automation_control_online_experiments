import React,{useState} from 'react';
import {makeCode,downloadText} from './online.js';

export function rcParameters(kind,{R1,R2,C,compensated=false}){
 if(!(R1>0&&R2>0&&C>0))throw Error('电阻、电容必须大于零');
 const r1=R1*1000,r2=R2*1000,c=C*1e-6;
 const sign=compensated?1:-1;
 return {K:['integrator','d'].includes(kind)?sign:sign*r2/r1,T:(kind==='pd'?r1:['integrator','d'].includes(kind)?r1:r2)*c};
}
export function leadComponents({alpha,wm,C}){
 if(!(alpha>1&&wm>0&&C>0))throw Error('α>1、ωm>0、C>0');const wp=wm*Math.sqrt(alpha),wz=wm/Math.sqrt(alpha),r1=1/wz/(C*1e-6),r2=r1/(alpha-1);
 return {R1:r1,R2:r2,R3:r1+r2,wz,wp};
}
export function comparisonScript(example,request,presets){
 const lines=['clear; clc; close all;',"figure('Name','Course comparison'); hold on; grid on;"];
 for(const [i,preset] of presets.entries()){
  const req={...request,params:{...request.params,...preset.params},numerator:preset.numerator,denominator:preset.denominator};
  const prelude=makeCode(example,req).split('[num,den] = tfdata')[0].replace('clear; clc; close all;','');
  lines.push(`% 工况 ${i+1}：${preset.label}`,prelude,"t_compare=linspace(0,10,10001);",`[yc,tc]=step(sys,t_compare); plot(tc,yc,'DisplayName','${preset.label.replace(/'/g,"''")}');`,"disp(sys); damp(sys); if isstable(sys), disp(stepinfo(sys)); end");
 }
 lines.push("legend('show'); xlabel('Time (s)'); ylabel('Output');");return lines.join('\n');
}

export function CourseManual({lab,task,request,example,onApply,onSelectTask}){
 const [checked,setChecked]=useState(()=>{try{return JSON.parse(localStorage.getItem('course-checks-'+lab.id))||{}}catch{return {}}}),[notice,setNotice]=useState('');
 const [rc,setRc]=useState(()=>({R1:100,R2:100*Math.abs(request.params.K??1),C:10*(request.params.T??.1),compensated:(request.params.K??1)>0})),[cap,setCap]=useState(1);
 const [rows,setRows]=useState(()=>{try{return JSON.parse(localStorage.getItem('course-measures-'+lab.id))||[]}catch{return []}});
 const [measurement,setMeasurement]=useState({case:'',f:'',A:'',B:'',delay_ms:'',Mp:'',tp:'',ts:''});
 const guide=lab.coursework;if(!guide)return null;
 const updateRows=next=>{setRows(next);try{localStorage.setItem('course-measures-'+lab.id,JSON.stringify(next))}catch{setNotice('浏览器存储已满，请先导出记录')}};
 let components;try{if(example?.model.design.alpha)components=leadComponents({alpha:example.model.design.alpha,wm:example.model.design.wm,C:cap})}catch{}
 return <section className="course-manual" aria-label="课件任务核对">
  <div className="section-heading"><h2>课件任务与操作清单</h2><span className="chapter-tag">{guide.pages}</span></div>
  <p className="muted">数值模型入口不等于完整实验过程。以下项目由你完成操作后手动标记，网页不把示例浏览当作已完成实验。</p>
  <div className="course-checklist">{guide.required.map((text,i)=><label key={text}><input type="checkbox" checked={!!checked[i]} onChange={e=>{const next={...checked,[i]:e.target.checked};setChecked(next);localStorage.setItem('course-checks-'+lab.id,JSON.stringify(next))}}/><span>{text}</span></label>)}</div>
  <div className="course-caveats">{guide.caveats.map(text=><p key={text}>{text}</p>)}</div>
  {lab.id===1&&onSelectTask&&<div className="course-presets"><h3>课件入门与教学例</h3><div>{[['ode_demo','积分器反馈建模'],['conversion','模型双向转换'],['connections','串联、并联、反馈']].map(([id,label])=><button key={id} onClick={()=>onSelectTask(id)}>{label}</button>)}</div></div>}
  {task.presets?.length>0&&<div className="course-presets"><h3>课件工况</h3><div>{task.presets.map(p=><button key={p.label} onClick={()=>onApply(p)}>{p.label}</button>)}<button onClick={()=>{try{downloadText(comparisonScript(example,request,task.presets),`lab${lab.id}_${task.id}_course_comparison.m`)}catch(e){setNotice(e.message)}}}>下载全部工况同图比较脚本</button></div></div>}
  {lab.id===2&&<div className="rc-panel"><h3>电路元件 → 模块参数</h3><p>电阻单位 kΩ，电容单位 μF。PD 按输入电阻 R₁C 取时间常数；课件旧公式 R₂C 在 R₁≠R₂ 时不适用。</p><div className="rc-fields">{[['R1','R₁ / kΩ'],['R2','R₂ / kΩ'],['C','C / μF']].map(([key,label])=><label key={key}>{label}<input aria-label={label} type="number" min="0.0001" step="0.1" value={rc[key]} onChange={e=>setRc(r=>({...r,[key]:Number(e.target.value)}))}/></label>)}</div><label className="checkbox-label"><input type="checkbox" checked={rc.compensated} onChange={e=>setRc(r=>({...r,compensated:e.target.checked}))}/>按课件允许加入额外反相器（改为正增益）</label><div className="rc-options">{[.1,1,10,100].map(C=><button key={C} onClick={()=>setRc(r=>({...r,C}))}>{C} μF</button>)}</div><button className="secondary-btn" onClick={()=>{try{const params=rcParameters(task.id,rc);onApply({params});setNotice(`已写入 K=${params.K}、T=${params.T} s；电阻电容是信号模型的参数映射，未生成物理电路。`)}catch(e){setNotice(e.message)}}}>计算并应用 K、T</button></div>}
  {lab.id===6&&<div className="rc-panel"><h3>超前网络元件选值（默认示例设计）</h3><label>C / μF<input aria-label="校正网络电容 μF" type="number" min="0.0001" step="0.1" value={cap} onChange={e=>setCap(Number(e.target.value))}/></label>{components&&<p>R₁={(components.R1/1000).toFixed(3)} kΩ，R₂={(components.R2/1000).toFixed(3)} kΩ；有源归一化取 R₃={(components.R3/1000).toFixed(3)} kΩ。无源每级衰减 1/α，两级另用 α² 放大补偿。实际参数修改后的元件值请运行代码计算。</p>}<p>由零点时间 Tz=1/ωz 得 R₁=Tz/C，R₂=R₁/(α−1)。元件标准化、极性和负载影响需要另行核对。</p></div>}
  <details className="measurement-panel"><summary>填写自己的实验记录 · 导出 CSV（{rows.length} 行）</summary><p>只填实际读取的数据。频率记录中 Δt 为输出滞后时间，允许负值表示超前；不自动用示例曲线填表。</p><div className="measurement-fields">{[['case','工况说明'],['f','f / Hz'],['A','输入峰值 A / V'],['B','输出峰值 B / V'],['delay_ms','滞后 Δt / ms'],['Mp','超调量 / %'],['tp','峰值时间 / s'],['ts','调节时间 / s']].map(([key,label])=><label key={key}>{label}<input aria-label={label} type={key==='case'?'text':'number'} step="any" value={measurement[key]} onChange={e=>setMeasurement(m=>({...m,[key]:e.target.value}))}/></label>)}</div><button disabled={rows.length>=200} onClick={()=>{if(!measurement.case.trim()){setNotice('请填写工况说明');return}const m=measurement,frequency=m.f!==''?Number(m.f):null,A=m.A!==''?Number(m.A):null,B=m.B!==''?Number(m.B):null;const row={...m,task:task.id,w:frequency!=null?2*Math.PI*frequency:'',gain_dB:A>0&&B>0?20*Math.log10(B/A):'',phase_deg:frequency!=null&&m.delay_ms!==''?-360*frequency*Number(m.delay_ms)/1000:''};updateRows([...rows,row]);setMeasurement({...measurement,case:''});setNotice('已保存你填写的记录，未作为自动测量结果。')}}>保存本行实际记录</button><button disabled={!rows.length} onClick={()=>{const keys=['task','case','f','w','A','B','delay_ms','gain_dB','phase_deg','Mp','tp','ts'];const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';downloadText('\ufeff'+[keys.map(cell).join(','),...rows.map(r=>keys.map(k=>cell(r[k])).join(','))].join('\n'),`lab${lab.id}_my_measurements.csv`,'text/csv;charset=utf-8')}}>导出我的记录 CSV</button>{rows.map((r,i)=><div className="edge-row" key={i}><span>{r.case} {r.gain_dB!==''?`· ${Number(r.gain_dB).toFixed(3)} dB`:''} {r.phase_deg!==''?`· ${Number(r.phase_deg).toFixed(3)}°`:''}</span><button aria-label={`删除记录 ${i+1}`} onClick={()=>updateRows(rows.filter((_,j)=>i!==j))}>删除</button></div>)}</details>
  {notice&&<p className="block-notice" role="status">{notice}</p>}
 </section>;
}
