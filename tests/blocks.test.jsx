import React from 'react';
import {it,expect,vi,beforeEach,afterEach} from 'vitest';
import {render,screen,fireEvent,cleanup,act} from '@testing-library/react';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {courseGraph,validateGraph,modelScript} from '../frontend/blocks.js';
import {BlockEditor} from '../frontend/BlockEditor.jsx';
import {CourseManual,rcParameters,leadComponents,comparisonScript} from '../frontend/CourseManual.jsx';
import {makeCode} from '../frontend/online.js';
const read=path=>JSON.parse(readFileSync(resolve(process.cwd(),path),'utf8'));
const catalog=read('public/course/catalog.json');
const example=(lab,id)=>read(`public/course/examples/${lab}_${id}.json`);
const req=(lab,id)=>({lab_id:lab,task_id:id,params:catalog.find(l=>l.id===lab).tasks.find(t=>t.id===id).defaults,amplitude:1,stop_time:5,points:1501,settling_threshold:.02,solver:'ode45',auto_duration:true});
beforeEach(()=>{localStorage.clear();vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});vi.spyOn(window,'open').mockReturnValue({opener:null});Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:vi.fn(()=>Promise.resolve())}})});
afterEach(()=>{cleanup();vi.restoreAllMocks()});
it('exports real teaching structures and checks every catalog topology',()=>{
 for(const lab of catalog)for(const task of lab.tasks){const r=req(lab.id,task.id),e=example(lab.id,task.id);if(e.model.num.length>e.model.den.length)continue;const g=courseGraph(r,e.model);expect(validateGraph(g),lab.id+task.id).toEqual([])}
 const pi=courseGraph(req(2,'pi'),example(2,'pi').model);expect(pi.nodes.map(n=>n.type)).toEqual(expect.arrayContaining(['Integrator','Sum','Gain','Step','Scope']));
 const stability=makeCode(example(4,'stability1'),req(4,'stability1'),'simulink');expect(stability).toContain('simulink/Continuous/Integrator');expect(stability).toContain("'Gain','10*K'");
 const lead=makeCode(example(6,'lead2'),req(6,'lead2'),'simulink');expect(lead.match(/\[1\/wz 1\]\/alpha/g)).toHaveLength(2);expect(lead).toContain("'Gain','alpha^2'");
});
it('adds and deletes modules, edits parameters, connects ports, and exports the edited graph',()=>{
 render(<BlockEditor request={req(1,'ode_demo')} example={example(1,'ode_demo')} licensed={false}/>);
 fireEvent.click(screen.getByRole('button',{name:'新建空白模型'}));
 fireEvent.click(screen.getByRole('button',{name:'＋ Step'}));fireEvent.click(screen.getByRole('button',{name:'＋ Gain'}));
 fireEvent.change(screen.getByLabelText('模块参数 Gain'),{target:{value:'3'}});
 fireEvent.click(screen.getByRole('button',{name:'＋ Scope'}));
 for(const [from,to] of [['b1','b2'],['b2','b3']]){fireEvent.change(screen.getByLabelText('连线源模块'),{target:{value:from}});fireEvent.change(screen.getByLabelText('连线目标模块'),{target:{value:to}});fireEvent.click(screen.getByRole('button',{name:'加入连线'}))}
 expect(screen.getByRole('button',{name:'导出当前画布 .m'}).disabled).toBe(false);
 const g=JSON.parse(localStorage.getItem('control-lab-graph-1-ode_demo'));expect(g.nodes[1].params.Gain).toBe('3');
 const script=modelScript(g,{prelude:'A=1; sys=tf(3,1);',request:req(1,'ode_demo')});expect(script).toContain("'Gain','3'");expect(script).toContain("add_line(mdl,'b1/1','b2/1'");
 expect(screen.getByRole('button',{name:'复制画布并进入 Simulink Online'}).disabled).toBe(true);
 fireEvent.click(screen.getByRole('button',{name:'删除所选模块及连线'}));expect(screen.getByRole('button',{name:'导出当前画布 .m'}).disabled).toBe(true);
});
it('rejects occupied inputs and malformed cached models instead of crashing',()=>{
 const r=req(2,'pi'),e=example(2,'pi'),g=courseGraph(r,e.model);g.edges.push({...g.edges[0]});expect(validateGraph(g).join(' ')).toContain('已有输入连线');
 localStorage.setItem('control-lab-graph-2-pi',JSON.stringify({version:1,nodes:[{id:'x',type:'Sum'}],edges:[]}));render(<BlockEditor request={r} example={e} licensed={false}/>);expect(screen.getByRole('button',{name:'导出当前画布 .m'}).disabled).toBe(false);
});
it('drags repeatedly under StrictMode, saves the final position, and undoes each gesture',()=>{
 class DragBoundary extends React.Component{
  state={error:null};static getDerivedStateFromError(error){return {error}}
  render(){return this.state.error?<div role="alert">{this.state.error.message}</div>:this.props.children}
 }
 // jsdom has no PointerEvent implementation; preserve coordinates and identity.
 class TestPointerEvent extends MouseEvent{
  constructor(type,init={}){super(type,init);Object.defineProperty(this,'pointerId',{value:init.pointerId??1})}
 }
 const oldPointer=window.PointerEvent;window.PointerEvent=TestPointerEvent;
 const consoleError=vi.spyOn(console,'error').mockImplementation(()=>{});
 try{
  const r=req(1,'ode_demo'),e=example(1,'ode_demo'),initial=courseGraph(r,e.model).nodes[0];
  render(<React.StrictMode><DragBoundary><BlockEditor request={r} example={e} licensed={false}/></DragBoundary></React.StrictMode>);
  const canvas=screen.getByRole('img',{name:'可拖动模块与端口连线画布'});
  canvas.getBoundingClientRect=()=>({left:0,top:0,width:1320,height:500});
  const gesture=(x,y)=>{
   const block=screen.getByRole('button',{name:`模块 ${initial.id} ${initial.type}`});
   fireEvent.pointerDown(block,{clientX:Number(block.querySelector('rect').getAttribute('x'))+10,clientY:Number(block.querySelector('rect').getAttribute('y'))+10,pointerId:1,button:0});
   fireEvent.pointerMove(canvas,{clientX:x+10,clientY:y+10,pointerId:1});
   fireEvent.pointerUp(canvas,{clientX:x+10,clientY:y+10,pointerId:1});
   expect(screen.queryByRole('alert')).toBeNull();
  };
  gesture(120,160);gesture(240,220);
  const saved=()=>JSON.parse(localStorage.getItem('control-lab-graph-1-ode_demo')).nodes[0];
  expect(saved()).toMatchObject({x:240,y:220});
  fireEvent.click(screen.getByRole('button',{name:'撤销'}));expect(saved()).toMatchObject({x:120,y:160});
  fireEvent.click(screen.getByRole('button',{name:'撤销'}));expect(saved()).toMatchObject({x:initial.x,y:initial.y});
  // A whole gesture can be batched before React renders; persist its last move.
  act(()=>{
   const block=screen.getByRole('button',{name:`模块 ${initial.id} ${initial.type}`});
   fireEvent.pointerDown(block,{clientX:initial.x+10,clientY:initial.y+10,pointerId:1,button:0});
   fireEvent.pointerMove(canvas,{clientX:190,clientY:190,pointerId:1});
   fireEvent.pointerMove(canvas,{clientX:310,clientY:270,pointerId:1});
   fireEvent.pointerUp(canvas,{clientX:310,clientY:270,pointerId:1});
  });
  expect(screen.queryByRole('alert')).toBeNull();expect(saved()).toMatchObject({x:300,y:260});
  fireEvent.click(screen.getByRole('button',{name:'撤销'}));expect(saved()).toMatchObject({x:initial.x,y:initial.y});
  const block=screen.getByRole('button',{name:`模块 ${initial.id} ${initial.type}`});
  fireEvent.pointerDown(block,{clientX:initial.x+10,clientY:initial.y+10,pointerId:1,button:0});
  fireEvent.pointerMove(canvas,{clientX:900,clientY:900,pointerId:2});
  fireEvent.pointerUp(canvas,{pointerId:2}); // Another pointer cannot finish this gesture.
  fireEvent.pointerMove(canvas,{clientX:150,clientY:210,pointerId:1});
  fireEvent.lostPointerCapture(canvas,{pointerId:1});
  fireEvent.pointerCancel(canvas,{pointerId:1});fireEvent.pointerUp(canvas,{pointerId:1});
  expect(screen.queryByRole('alert')).toBeNull();expect(saved()).toMatchObject({x:140,y:200});
  fireEvent.click(screen.getByRole('button',{name:'撤销'}));expect(saved()).toMatchObject({x:initial.x,y:initial.y});
  expect(screen.getByRole('button',{name:'撤销'}).disabled).toBe(true);
  fireEvent.pointerDown(block,{clientX:initial.x+10,clientY:initial.y+10,pointerId:1,button:0});
  fireEvent.pointerUp(canvas,{pointerId:1});expect(screen.getByRole('button',{name:'撤销'}).disabled).toBe(true);
  expect(consoleError).not.toHaveBeenCalled();
 }finally{window.PointerEvent=oldPointer}
});
it('maps physical values with signs and generates all required comparison cases',()=>{
 expect(rcParameters('inertia',{R1:100,R2:100,C:.1})).toEqual({K:-1,T:.01});
 expect(rcParameters('pd',{R1:100,R2:200,C:1}).T).toBeCloseTo(.1);
 expect(rcParameters('integrator',{R1:100,R2:100,C:100}).T).toBeCloseTo(10);
 const rc=leadComponents({alpha:3,wm:6,C:1});expect((rc.R1+rc.R2)/rc.R2).toBeCloseTo(3);expect(rc.R1*rc.R2*1e-6/(rc.R1+rc.R2)).toBeCloseTo(1/rc.wp);
 const task=catalog[2].tasks.find(t=>t.id==='damping_sweep');expect(task.presets).toHaveLength(6);const script=comparisonScript(example(3,'damping_sweep'),req(3,'damping_sweep'),task.presets);expect(script).toContain('zeta = 0;');expect(script).toContain('zeta = 1.25;');expect(script).toContain("hold on");
});
it('stores only student-entered measurements and computes frequency units and phase',()=>{
 const lab=catalog[4],task=lab.tasks[1];render(<CourseManual lab={lab} task={task} request={req(5,task.id)} example={example(5,task.id)} onApply={vi.fn()}/>);
 for(const [label,value] of [['工况说明','f=100'],['f / Hz','100'],['输入峰值 A / V','1'],['输出峰值 B / V','.5'],['滞后 Δt / ms','1']])fireEvent.change(screen.getByLabelText(label),{target:{value}});
 fireEvent.click(screen.getByRole('button',{name:'保存本行实际记录'}));const rows=JSON.parse(localStorage.getItem('course-measures-5'));expect(rows).toHaveLength(1);expect(rows[0].phase_deg).toBe(-36);expect(rows[0].gain_dB).toBeCloseTo(-6.0206);expect(rows[0].w).toBeCloseTo(200*Math.PI);
});
it('rebuilds actual source and transfer blocks when applying changed global settings',()=>{
 const r=req(2,'p'),e=example(2,'p');const {rerender}=render(<BlockEditor request={r} example={e} licensed={false}/>);
 const next={...r,input_signal:'ramp',numerator:[2],denominator:[1,1]};
 rerender(<BlockEditor request={next} example={e} licensed={false}/>);
 fireEvent.click(screen.getByRole('button',{name:'恢复课件结构（按当前参数重建）'}));
 const g=JSON.parse(localStorage.getItem('control-lab-graph-2-p'));
 expect(g.nodes.some(b=>b.type==='Ramp')).toBe(true);
 expect(g.nodes.some(b=>b.type==='TransferFcn')).toBe(true);
 expect(g.nodes.some(b=>b.type==='Gain')).toBe(false);
});
it('offers the corrected integral model instead of an Online launch of the known bad original',()=>{
 render(<BlockEditor request={req(2,'integrator')} example={example(2,'integrator')} licensed={true} coursework={{originals:['/sources/lab2/task3.slx']}}/>);
 expect(screen.getByText(/原始 task3 分母缺少 s/)).toBeTruthy();
 expect(screen.getByRole('link',{name:'下载修正积分模型 .slx'}).getAttribute('href')).toBe('/models/course_lab2_integrator.slx');
 expect(screen.queryByRole('button',{name:'在原生 Online 编辑原模型 ↗'})).toBeNull();
});
it('surfaces a blocked signal Online launch without claiming it opened',async()=>{
 window.open.mockReturnValue(null);
 render(<BlockEditor request={req(2,'pi')} example={example(2,'pi')} licensed={true}/>);
 fireEvent.click(screen.getByRole('button',{name:'复制画布并进入 Simulink Online'}));
 expect(screen.getByRole('status').textContent).toContain('拦截');
 expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
});
