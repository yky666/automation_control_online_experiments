import React from 'react';
import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,cleanup,waitFor} from '@testing-library/react';
import {newBlock} from '../frontend/blocks.js';
import {simulateSignal,vectorExpression} from '../frontend/signal-solver.js';
import {signalCsv,signalReport} from '../frontend/signal-report.js';
import {BlockEditor} from '../frontend/BlockEditor.jsx';

const request={lab_id:1,task_id:'custom',params:{},stop_time:2,points:1201,amplitude:1};
const example={model:{params:{},num:[1],den:[1],input_signal:'step'}};
function fixture(){
 return {version:1,lab_id:1,task_id:'custom',nodes:[
  newBlock('Step','step',0,0,{Time:'1',Before:'2',After:'4'}),
  newBlock('Gain','gain',200,0,{Gain:'3'}),
  newBlock('Scope','scopeA',400,0,{NumInputPorts:'2'}),
  newBlock('Scope','scopeB',400,200),
 ],edges:[{from:'step',to:'gain',port:1},{from:'gain',to:'scopeA',port:1},
  {from:'step',to:'scopeA',port:2},{from:'gain',to:'scopeB',port:1}]};
}
afterEach(()=>{cleanup();localStorage.clear();vi.restoreAllMocks();vi.unstubAllGlobals()});

it('records all scopes and the edited source instead of a reconstructed default input',()=>{
 const r=simulateSignal(fixture(),request,example);
 expect(Object.keys(r.traces)).toEqual(['scopeA / 1','scopeA / 2','scopeB / 1']);
 expect(r.channels[2]).toEqual({label:'scopeB / 1',scope:'scopeB',port:1,from:'gain'});
 expect(r.input[0]).toBe(2);expect(r.input.at(-1)).toBe(4);
 expect(r.output[0]).toBe(6);expect(r.output.at(-1)).toBe(12);
 expect(r.traces['scopeA / 2']).toEqual(r.input);
 expect(r.sourceTraces.step).toEqual(r.input);
 const rows=signalCsv(r).split('\n');
 expect(rows[0]).toBe('"time","input","output","scopeA / 1","scopeA / 2","scopeB / 1","source step"');
 expect(rows.at(-1)).toBe('2,4,12,12,4,12,4');
 const html=signalReport(r,'<script>','<img src=x>','scopeA / 2');
 expect(html).toContain('本次输出曲线 · scopeA / 2');
 expect(html).toContain('scopeB / 1');expect(html).toContain('末值（非稳态判定）');
 expect(html).toContain('&lt;script&gt;');expect(html).not.toContain('<img');
});

it('retains independent sources and their phase, start time and amplitude',()=>{
 const g=fixture();g.nodes.push(newBlock('SineWave','sine',0,200,{Amplitude:'2',Frequency:'2*pi',Phase:'pi/2'}));
 g.edges=g.edges.map(e=>e.to==='scopeB'?{...e,from:'sine'}:e);
 const r=simulateSignal(g,request,example);
 expect(r.sourceTraces.sine[0]).toBeCloseTo(2,12);
 expect(r.sourceTraces.sine[300]).toBeCloseTo(-2,12);
 expect(r.traces['scopeB / 1']).toEqual(r.sourceTraces.sine);
 expect(signalCsv(r).split('\n')[0]).toContain('"source sine"');
});

it('supports initial-condition responses without inventing an external input',()=>{
 const g={version:1,nodes:[newBlock('Integrator','state',0,0,{InitialCondition:'2'}),newBlock('Gain','feedback',200,0,{Gain:'-1'}),newBlock('Scope','scope',400,0)],edges:[{from:'state',to:'feedback',port:1},{from:'feedback',to:'state',port:1},{from:'state',to:'scope',port:1}]};
 const r=simulateSignal(g,request,example);
 expect(r.input.every(v=>v===0)).toBe(true);expect(r.sourceTraces).toEqual({});
 expect(r.inputLabel).toContain('无外部激励');expect(r.output.at(-1)).toBeCloseTo(2*Math.exp(-2),3);
 expect(Object.keys(r.traces)).toEqual(['Scope 1']);
});

it('rejects invalid coefficients, settings and unsupported source semantics',()=>{
 for(const expr of ['[]','[1]/0','[1]*1e309','bad'])expect(()=>vectorExpression(expr,{bad:[NaN]})).toThrow(/有限|无效/);
 expect(()=>vectorExpression('den',{den:[]})).toThrow(/有限/);
 for(const settings of [{points:0},{stop_time:0}])expect(()=>simulateSignal(fixture(),{...request,...settings},example)).toThrow(/时长|采样/);
 const g=fixture();g.nodes[0]=newBlock('SineWave','step',0,0,{Frequency:'1000'});
 expect(()=>simulateSignal(g,request,example)).toThrow(/60 点/);
 g.nodes[0].params.Frequency='1';g.nodes[0].params.SampleTime='.1';
 expect(()=>simulateSignal(g,request,example)).toThrow(/SampleTime/);
 g.nodes[0]=newBlock('FromWorkspace','step',0,0,{VariableName:'other'});
 expect(()=>simulateSignal(g,request,example)).toThrow(/web_input/);
});

it('lets students inspect every scope in the worker UI and labels generic signals without volts',async()=>{
 class TestWorker{postMessage({graph,request,example}){const result=simulateSignal(graph,request,example);queueMicrotask(()=>this.onmessage({data:{result}}))}terminate(){}}
 vi.stubGlobal('Worker',TestWorker);
 localStorage.setItem('control-lab-graph-1-custom',JSON.stringify(fixture()));
 render(<BlockEditor request={request} example={example} licensed={false}/>);
 fireEvent.click(screen.getByRole('button',{name:'▶ 运行当前信号框图'}));
 await waitFor(()=>expect(screen.getByRole('heading',{name:'本次信号框图运行结果'})).toBeTruthy());
 fireEvent.change(screen.getByLabelText('Scope 通道'),{target:{value:'scopeB / 1'}});
 expect(screen.getByRole('img',{name:'本次实际求解的输入和输出信号曲线'})).toBeTruthy();
 expect(screen.getByText('信号幅值')).toBeTruthy();expect(screen.queryByText('电压 / V')).toBeNull();
 expect(screen.getByText(/橙线：step · Step · 绿线：scopeB/)).toBeTruthy();
});
