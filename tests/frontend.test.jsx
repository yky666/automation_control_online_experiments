import React from 'react';
import {vi,describe,it,expect,beforeEach,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import catalog from '../docs/catalog-qa.json';
import fixtures from './ui-results.json';

vi.mock('plotly.js-dist-min',()=>({default:{react:vi.fn(()=>Promise.resolve()),purge:vi.fn(el=>{if(!el)throw Error('Plotly target is null or undefined')}),Plots:{resize:vi.fn()}}}));
const {App}=await import('../frontend/main.jsx');
let calls=[];
let saved=[];
beforeEach(()=>{
 calls=[];saved=[];localStorage.clear();
 globalThis.fetch=vi.fn(async(url,opts)=>{
  const payload=opts?.body?JSON.parse(opts.body):null;calls.push({url,payload});
  if(url==='/api/report')return {ok:true,blob:async()=>new Blob(['report'])};
  let data=url==='/api/catalog'?catalog:url==='/api/health'?{status:'ok',matlab:{executable:false},capabilities:{native:{ready:false}}}:url==='/api/runs'?saved:fixtures[`${payload?.lab_id}:${payload?.task_id}`];
  if(url==='/api/run'){data={...data,id:'abcd1234abcd',created_at:'2026-10-15T09:00:00+08:00',elapsed:.01};saved=[data]}
  if(url.startsWith('/api/runs/'))data=saved.find(r=>url==='/api/runs/'+r.id);
  if(url==='/api/code/template')data={...data,simulink_code:'new_system(mdl); out=sim(mdl);'};
  if(!data)throw Error('Unhandled request '+url);
  return {ok:true,json:async()=>structuredClone(data)};
 });
 vi.spyOn(window,'open').mockReturnValue({document:{title:'',body:{textContent:''}},location:{href:''},close:vi.fn()});
 Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:vi.fn(()=>Promise.resolve())}});
 vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});
});
afterEach(()=>{cleanup();vi.restoreAllMocks()});
describe('chapter navigation regression',()=>{
 it('can switch from chapter 1 to chapters 2–6 after a plot has mounted',async()=>{
  render(<App mode="platform"/>);
  await waitFor(()=>expect(calls.some(c=>c.url==='/api/preview')).toBe(true));
  await waitFor(()=>expect(document.querySelector('.js-plotly-plot')||document.querySelector('.plot')).not.toBeNull());
  for(const lab of catalog.slice(1)){
   fireEvent.click(screen.getByRole('button',{name:new RegExp('0'+lab.id+'.*'+lab.title)}));
   await waitFor(()=>expect(screen.getByRole('heading',{level:1}).textContent).toBe(lab.title));
   await waitFor(()=>expect(calls.some(c=>c.url==='/api/preview'&&c.payload.lab_id===lab.id)).toBe(true));
   await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
  }
 });
});

describe('working student controls',()=>{
 it('switches every one of the 33 tasks and changes graph tabs without crashing',async()=>{
  render(<App mode="platform"/>);await screen.findByRole('heading',{level:1});
  for(const lab of catalog){
   fireEvent.click(screen.getByRole('button',{name:new RegExp('0'+lab.id+'.*'+lab.title)}));
   for(const task of lab.tasks){
    fireEvent.change(screen.getByLabelText('选择实验任务'),{target:{value:task.id}});
    await waitFor(()=>expect(calls.some(c=>c.url==='/api/preview'&&c.payload.lab_id===lab.id&&c.payload.task_id===task.id)).toBe(true));
    await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
    fireEvent.click(screen.getByRole('button',{name:'频率响应'}));
    fireEvent.click(screen.getByRole('button',{name:'相频'}));
    fireEvent.click(screen.getByRole('button',{name:'极点与根轨迹'}));
   }
  }
 });
 it('edits fixed model coefficients and can scan amplitude instead of a disabled fake control',async()=>{
  render(<App mode="platform"/>);await waitFor(()=>expect(screen.getByLabelText('分子降幂系数').value).toBe('5'));
  fireEvent.change(screen.getByLabelText('分子降幂系数'),{target:{value:'10'}});
  await waitFor(()=>expect(calls.some(c=>c.url==='/api/preview'&&c.payload.numerator?.[0]===10)).toBe(true));
  const button=screen.getByRole('button',{name:'参数扫描与对比'});expect(button.disabled).toBe(false);fireEvent.click(button);
  expect(screen.getByRole('option',{name:'输入幅值'})).toBeTruthy();
 });
 it('uses school Online for free code instead of calling local MATLAB',async()=>{
  render(<App mode="platform"/>);await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
  fireEvent.click(screen.getByRole('tab',{name:'MATLAB 代码'}));
  fireEvent.click(screen.getByRole('button',{name:'复制并打开 MATLAB Online'}));
  await waitFor(()=>expect(navigator.clipboard.writeText).toHaveBeenCalled());
  expect(window.open).toHaveBeenCalledWith('https://matlab.mathworks.com/','_blank');
  expect(calls.some(c=>c.url==='/api/code/run')).toBe(false);
 });
 it('runs the block experiment without native MATLAB and generates a report',async()=>{
  render(<App mode="platform"/>);await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
  fireEvent.click(screen.getByRole('tab',{name:'Simulink 仿真'}));
  fireEvent.click(screen.getByRole('button',{name:'运行免安装框图实验'}));
  await waitFor(()=>expect(calls.some(c=>c.url==='/api/run'&&c.payload.engine==='scipy')).toBe(true));
  await waitFor(()=>expect(screen.getByRole('button',{name:'生成报告'}).disabled).toBe(false));
  fireEvent.click(screen.getByRole('button',{name:'生成报告'}));
  fireEvent.click(await screen.findByRole('button',{name:'生成并打开报告'}));
  await waitFor(()=>expect(calls.some(c=>c.url==='/api/report'&&c.payload.run_ids[0]==='abcd1234abcd')).toBe(true));
 });
 it('handles broken stored student data without a blank screen',async()=>{
  localStorage.setItem('control-lab-student','{broken');render(<App mode="platform"/>);
  expect(await screen.findByRole('heading',{level:1})).toBeTruthy();
 });
 it('restores a legacy native result but reruns in MATLAB-free student mode',async()=>{
  saved=[{...fixtures['3:second'],id:'abc123abc123',engine:'matlab',engine_label:'MATLAB 真实运行',created_at:'2026-10-14T09:00:00+08:00',elapsed:30}];
  render(<App mode="platform"/>);await screen.findByRole('heading',{level:1});
  fireEvent.click(screen.getByRole('button',{name:new RegExp('03.*'+catalog[2].title)}));
  fireEvent.click(screen.getByRole('tab',{name:new RegExp('资料与记录')}));
  fireEvent.click(await screen.findByRole('button',{name:'查看结果'}));
  fireEvent.click(await screen.findByRole('button',{name:/运行实验/}));
  await waitFor(()=>expect(calls.some(c=>c.url==='/api/run'&&c.payload.engine==='scipy')).toBe(true));
 });
});
