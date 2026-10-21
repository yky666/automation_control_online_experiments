import React from 'react';
import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,cleanup,waitFor} from '@testing-library/react';
import {readFileSync} from 'node:fs';
import {circuitTemplate,simulateCircuit,validateCircuit,parseCircuitCsv,circuitCsv,factor} from '../frontend/circuits.js';
import {physicalScript} from '../frontend/physical-export.js';
import {CircuitLab,circuitReport} from '../frontend/CircuitLab.jsx';
import {courseGraph} from '../frontend/blocks.js';
import {simulateSignal,signalVariables,numberExpression} from '../frontend/signal-solver.js';
const read=p=>JSON.parse(readFileSync(p,'utf8'));
afterEach(()=>{cleanup();localStorage.clear();vi.restoreAllMocks();vi.unstubAllGlobals()});
it('solves nodal equations against independent RC and inverting amplifier analytic results',()=>{
 const g=circuitTemplate(2,'inertia');g.settings.rise=0;g.settings.points=10001;g.settings.stop=.5;const result=simulateCircuit(g);
 for(const t of [.05,.1,.3,.5]){const i=Math.round(t/result.dt);expect(result.output[i]).toBeCloseTo(-(1-Math.exp(-t/.1)),3)}
 const p=circuitTemplate(2,'p',{K:3});expect(simulateCircuit(p).output.at(-1)).toBeCloseTo(-3,10);
 const resistance=p.components.find(c=>c.label==='反馈电阻');resistance.value*=2;expect(simulateCircuit(p).output.at(-1)).toBeCloseTo(-6,10);
});
it('resolves changed connections, detects floating nodes, and enforces finite op-amp rails',()=>{
 const g=circuitTemplate(2,'p',{K:10});g.opamp.mode='finite';g.settings.amplitude=3;g.settings.stop=.02;const r=simulateCircuit(g);expect(r.output.at(-1)).toBeCloseTo(-15,6);expect(r.metrics.clippedSamples).toBeGreaterThan(0);
 g.opamp.mode='ideal';expect(simulateCircuit(g).output.at(-1)).toBeCloseTo(-30,8);
 g.components.find(c=>c.type==='OpAmp').ports.minus='floating';expect(()=>simulateCircuit(g)).toThrow(/奇异/);
 const solve=factor([[0,2,1],[3,1,2],[1,4,1]]),x=solve([7,11,12]);for(const [i,row] of [[0,[0,2,1]],[1,[3,1,2]],[2,[1,4,1]]])expect(row.reduce((a,v,j)=>a+v*x[j],0)).toBeCloseTo([7,11,12][i],10);
});
it('measures actual frequency response and preserves physical inversion',()=>{
 const g=circuitTemplate(5,'frequency_inertia',{K:1,T:.001,frequency:100});g.settings.stop=.1;g.settings.amplitude=1;g.settings.points=10001;const r=simulateCircuit(g);
 expect(r.metrics.gainDB).toBeCloseTo(-10*Math.log10(1+(.2*Math.PI)**2),1);
 expect(r.metrics.phase).toBeCloseTo(180-Math.atan(.2*Math.PI)*180/Math.PI,0);
});
it('accepts native CSV, rejects malformed values and escapes report text',()=>{
 const g=circuitTemplate(2,'p'),r=simulateCircuit(g),imported=parseCircuitCsv(circuitCsv(r),g);expect(imported.output).toEqual(r.output.map(v=>v||0));expect(imported.engine).toBe('imported-csv');
 expect(()=>parseCircuitCsv('time,input,output\n0,1,0\n0,1,1',g)).toThrow(/递增/);expect(()=>parseCircuitCsv('time,input,output\n0,1,0\n1,1,NaN',g)).toThrow(/数值/);
 const html=circuitReport(r,'<script>','<img src=x>');expect(html).not.toContain('<script>');expect(html).toContain('&lt;img');expect(html).toContain('本记录为模拟/导入数据');
});
it('makes every physical course task a real netlist and executable native script',()=>{
 const catalog=read('public/course/catalog.json');for(const l of catalog.filter(l=>[2,4,5,6].includes(l.id)))for(const t of l.tasks){const e=read(`public/course/examples/${l.id}_${t.id}.json`),g=circuitTemplate(l.id,t.id,t.defaults,e.model.design);if(l.id===5)g.settings.stop=10/g.settings.frequency;expect(validateCircuit(g),t.id).toEqual([]);const r=simulateCircuit(g);expect(r.output.every(Number.isFinite),t.id).toBe(true);const script=physicalScript(g);expect(script).toContain('fl_lib/Electrical/Electrical Elements/Resistor');expect(script).toContain('out=sim(mdl)');expect(script).toContain('writetable');}
});
it('edits real component values and electrical terminals, inserts and removes parts',()=>{
 const lab=read('public/course/catalog.json')[1],task=lab.tasks[0],example=read('public/course/examples/2_p.json');render(<CircuitLab lab={lab} task={task} request={{params:task.defaults}} example={example} licensed={false}/>);
 fireEvent.click(screen.getByRole('button',{name:'元件 R2 R'}));fireEvent.change(screen.getByLabelText('元件值'),{target:{value:'300000'}});fireEvent.change(screen.getByLabelText('端子 p'),{target:{value:'out'}});
 const saved=JSON.parse(localStorage.getItem('control-circuit-2-p'));expect(saved.components.find(c=>c.id==='R2').value).toBe(300000);expect(saved.components.find(c=>c.id==='R2').ports.p).toBe('out');
 fireEvent.click(screen.getByRole('button',{name:'＋ 电容 / F'}));expect(screen.getByRole('button',{name:'删除元件'})).toBeTruthy();fireEvent.click(screen.getByRole('button',{name:'删除元件'}));expect(screen.getByRole('button',{name:'复制电路并进入 Online ↗'}).disabled).toBe(true);
});
it('simulates edited signal feedback against the analytic ODE and updates task parameters',()=>{
 const e=read('public/course/examples/1_ode_demo.json'),request={lab_id:1,task_id:'ode_demo',params:{},stop_time:2,points:10001,amplitude:1},g=courseGraph(request,e.model),r=simulateSignal(g,request,e);expect(r.output[0]).toBe(0);expect(r.output.at(-1)).toBeCloseTo((1-Math.exp(-4))/2,4);
 const gain=g.nodes.find(c=>c.type==='Gain');gain.params.Gain='4';expect(simulateSignal(g,request,e).output.at(-1)).toBeCloseTo((1-Math.exp(-8))/4,4);
 expect(()=>numberExpression('globalThis.alert(1)',{})).toThrow();
});
it('runs the circuit button through a worker and marks edited results as stale',async()=>{
 class TestWorker{postMessage(g){const result=simulateCircuit(g);queueMicrotask(()=>this.onmessage({data:{result}}))}terminate(){}}
 vi.stubGlobal('Worker',TestWorker);
 const lab=read('public/course/catalog.json')[1],task=lab.tasks[0],example=read('public/course/examples/2_p.json');render(<CircuitLab lab={lab} task={task} request={{params:task.defaults}} example={example} licensed={false}/>);
 fireEvent.click(screen.getByRole('button',{name:'▶ 运行当前电路'}));await waitFor(()=>expect(screen.getByRole('heading',{name:'本次运行结果'})).toBeTruthy());
 expect(screen.getByRole('img',{name:'本次实际求解的输入和输出电压曲线'})).toBeTruthy();
 fireEvent.click(screen.getByRole('button',{name:'元件 R2 R'}));fireEvent.change(screen.getByLabelText('元件值'),{target:{value:'50000'}});expect(screen.getByText(/参数或接线已改变/)).toBeTruthy();
});
it('rebuilds all signal model coefficients and solves every course graph',()=>{
 const catalog=read('public/course/catalog.json');
 for(const l of catalog)for(const t of l.tasks){
  const e=read(`public/course/examples/${l.id}_${t.id}.json`);if(e.model.num.length>e.model.den.length)continue;
  const request={lab_id:l.id,task_id:t.id,params:t.defaults,stop_time:.01,points:201,auto_duration:true};
  const vars=signalVariables(request,e);expect(vars.num.length,t.id).toBe(e.model.num.length);
  for(const key of ['num','den'])for(const [i,v] of vars[key].entries())expect(Math.abs(v/vars.den[0]-e.model[key][i]/e.model.den[0])/Math.max(1,Math.abs(e.model[key][i]/e.model.den[0])),`${l.id}/${t.id} ${key}[${i}]`).toBeLessThan(1e-5);
  expect(simulateSignal(courseGraph(request,e.model),request,e).output.every(Number.isFinite),t.id).toBe(true);
 }
});
it('keeps the working circuit and gives an error when rebuilding invalid parameters',()=>{
 const lab=read('public/course/catalog.json')[3],task=lab.tasks[0],example=read(`public/course/examples/4_${task.id}.json`);
 const {rerender}=render(<CircuitLab lab={lab} task={task} request={{params:task.defaults}} example={example} licensed={false}/>);
 const before=screen.getByRole('img',{name:'电气元件端子与节点接线图'}).innerHTML;
 rerender(<CircuitLab lab={lab} task={task} request={{params:{...task.defaults,K:-1}}} example={example} licensed={false}/>);
 fireEvent.click(screen.getByRole('button',{name:'按当前任务参数重建'}));
 expect(screen.getByRole('status').textContent).toContain('重建失败');
 expect(screen.getByRole('img',{name:'电气元件端子与节点接线图'}).innerHTML).toBe(before);
 expect(screen.getByRole('button',{name:'▶ 运行当前电路'}).disabled).toBe(false);
});
it('loads edited electrical connections and reports malformed imports without replacing the circuit',async()=>{
 const lab=read('public/course/catalog.json')[1],task=lab.tasks[0],example=read('public/course/examples/2_p.json');
 render(<CircuitLab lab={lab} task={task} request={{params:task.defaults}} example={example} licensed={false}/>);
 const file=document.querySelector('input[type="file"][accept=".json"]');
 const g=circuitTemplate(2,'p',{K:4});
 fireEvent.change(file,{target:{files:[{size:100,text:async()=>JSON.stringify(g)}]}});
 await waitFor(()=>expect(JSON.parse(localStorage.getItem('control-circuit-2-p'))).toEqual(g));
 fireEvent.change(file,{target:{files:[{size:10,text:async()=>'{broken'}]}});
 await waitFor(()=>expect(screen.getByRole('status').textContent).not.toBe(''));
 expect(JSON.parse(localStorage.getItem('control-circuit-2-p'))).toEqual(g);
});
it('surfaces a blocked physical Online launch without claiming it opened',()=>{
 const lab=read('public/course/catalog.json')[1],task=lab.tasks[0],example=read('public/course/examples/2_p.json');
 vi.spyOn(window,'open').mockReturnValue(null);
 render(<CircuitLab lab={lab} task={task} request={{params:task.defaults}} example={example} licensed={true}/>);
 fireEvent.click(screen.getByRole('button',{name:'复制电路并进入 Online ↗'}));
 expect(screen.getByRole('status').textContent).toContain('拦截');
});
