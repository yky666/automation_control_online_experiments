import React from 'react';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {vi,it,expect,beforeEach,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {onlineUrl,makeCode,makeScanCode} from '../frontend/online.js';
vi.mock('plotly.js-dist-min',()=>({default:{react:vi.fn(()=>Promise.resolve()),purge:vi.fn(el=>{if(!el)throw Error('null plot')}),Plots:{resize:vi.fn()}}}));
const {App}=await import('../frontend/main.jsx');
const coursePath=path=>resolve(process.cwd(),'public',path.replace(/^\//,''));
const catalog=JSON.parse(await readFile(coursePath('course/catalog.json'),'utf8'));
let requests=[];
beforeEach(()=>{
 requests=[];localStorage.clear();
 globalThis.fetch=vi.fn(async url=>{requests.push(url);if(url.startsWith('/api'))throw Error('Online mode touched server API');const data=JSON.parse(await readFile(coursePath(url),'utf8'));return {ok:true,json:async()=>data}});
 vi.spyOn(window,'open').mockReturnValue({opener:{}});
 vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});
 Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:vi.fn(()=>Promise.resolve())}});
});
afterEach(()=>{cleanup();vi.restoreAllMocks()});
it('requires the Online permission choice and opens the matching GitHub script',async()=>{
 render(<App/>);await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
 fireEvent.click(await screen.findByRole('tab',{name:'MATLAB 代码'}));
 const online=screen.getByRole('button',{name:'复制并打开 MATLAB Online'});expect(online.disabled).toBe(true);
 expect(screen.getByRole('button',{name:'下载 .m'}).disabled).toBe(false);
 fireEvent.click(screen.getByRole('checkbox',{name:'我已有可用的 MATLAB Online 许可'}));
 await waitFor(()=>expect(online.disabled).toBe(false));fireEvent.click(online);
 await waitFor(()=>expect(navigator.clipboard.writeText).toHaveBeenCalled());
 expect(window.open).toHaveBeenCalledWith(onlineUrl(1,'tf1'),'_blank');
 expect(new URL(window.open.mock.calls[0][0]).searchParams.get('file')).toBe('matlab/online/lab1_tf1.m');
 expect(requests.some(u=>u.startsWith('/api'))).toBe(false);
});
it('edits code while keeping the default example, and reports an example without executing code',async()=>{
 render(<App/>);await waitFor(()=>expect(screen.getByLabelText('分子降幂系数').value).toBe('5'));
 fireEvent.change(screen.getByLabelText('分子降幂系数'),{target:{value:'[10]'}});
 fireEvent.click(screen.getByRole('tab',{name:'MATLAB 代码'}));
 await waitFor(()=>expect(screen.getByLabelText('MATLAB 代码编辑器').value).toContain('Gopen = tf([10],[1 5 8 4 0]);'));
 expect(screen.getByText(/图表和指标展示默认参数的预计算示例/)).toBeTruthy();
 expect(requests.filter(u=>u.includes('/examples/'))).toHaveLength(1);
 fireEvent.click(screen.getAllByRole('button',{name:'查看示例报告'})[0]);
 expect(window.open).toHaveBeenCalledWith('/course/reports/1_tf1.html','_blank');
 expect(requests.some(u=>u.startsWith('/api'))).toBe(false);
});
it('browses all 33 examples and redirects Simulink only after confirmation',async()=>{
 render(<App/>);await screen.findByRole('heading',{level:1});
 for(const lab of catalog){
  fireEvent.click(screen.getByRole('button',{name:new RegExp('0'+lab.id+'.*'+lab.title)}));
  for(const task of lab.tasks){
   fireEvent.change(screen.getByLabelText('选择实验任务'),{target:{value:task.id}});
   await waitFor(()=>expect(requests).toContain(`/course/examples/${lab.id}_${task.id}.json`));
   await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
  }
 }
 fireEvent.click(screen.getByRole('tab',{name:'Simulink 仿真'}));
 const button=await screen.findByRole('button',{name:'复制画布并进入 Simulink Online'});expect(button.disabled).toBe(true);
 fireEvent.click(screen.getByRole('checkbox',{name:'我已有可用的 MATLAB Online 许可'}));fireEvent.click(button);
 await waitFor(()=>expect(navigator.clipboard.writeText).toHaveBeenCalled());
 expect(window.open).toHaveBeenCalledWith(onlineUrl(6,'lead_example2','simulink'),'_blank');
});
it('generates changed task parameters, sine settings and valid custom-model scripts',async()=>{
 const example=JSON.parse(await readFile(coursePath('course/examples/3_second.json'),'utf8'));
 const request={lab_id:3,task_id:'second',params:{zeta:.7,wn:3,frequency:2},amplitude:2,stop_time:7,points:2001,settling_threshold:.05,auto_duration:false,input_signal:'sine',solver:'ode15s'};
 const code=makeCode(example,request,'simulink');
 expect(code).toContain('zeta = 0.7;');expect(code).toContain('wn = 3;');expect(code).toContain('frequency = 2;');expect(code).toContain('stop_time = 7;');expect(code).toContain("'Solver','ode15s'");
 expect(code).toContain('new_system(mdl)');expect(code).toContain('simulink/Sources/Sine Wave');expect(()=>makeCode(example,{...request,points:NaN})).toThrow();
 const scan=makeScanCode(example,request,'amplitude',[1,2,3]);
 expect(scan).toContain('A = 1;');expect(scan).toContain('A = 3;');expect(scan).not.toContain('close all');
});
it('reports blocked Online and report windows instead of claiming success',async()=>{
 render(<App/>);await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
 window.open.mockReturnValue(null);
 fireEvent.click(screen.getAllByRole('button',{name:'查看示例报告'})[0]);
 expect(screen.getByRole('alert').textContent).toContain('拦截');
 fireEvent.click(screen.getByRole('checkbox',{name:'我已有可用的 MATLAB Online 许可'}));
 fireEvent.click(screen.getByRole('tab',{name:'MATLAB 代码'}));
 fireEvent.click(screen.getByRole('button',{name:'复制并打开 MATLAB Online'}));
 expect(screen.getByRole('alert').textContent).toContain('拦截');
 expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
});
it('does not advertise an empty browser run archive as saved history',async()=>{
 render(<App/>);await screen.findByRole('heading',{level:1});
 expect(screen.queryByRole('button',{name:/运行记录/})).toBeNull();
 fireEvent.click(screen.getByRole('button',{name:'课程资料'}));
 expect(screen.getByRole('heading',{name:'如何保存实验结果'})).toBeTruthy();
 expect(screen.queryByRole('heading',{name:'已保存运行'})).toBeNull();
});
it('warns at the known incorrect original integral model download',async()=>{
 render(<App/>);await screen.findByRole('heading',{level:1});
 fireEvent.click(screen.getByRole('button',{name:new RegExp('02.*'+catalog[1].title)}));
 fireEvent.click(screen.getByRole('tab',{name:/资料与记录/}));
 expect(screen.getByText(/原始 task3 分母缺少 s/)).toBeTruthy();
});
it('downloads current code when clipboard access fails without reporting a successful copy',async()=>{
 render(<App/>);await waitFor(()=>expect(document.querySelector('.plot')).not.toBeNull());
 navigator.clipboard.writeText.mockRejectedValue(Error('denied'));
 fireEvent.click(screen.getByRole('checkbox',{name:'我已有可用的 MATLAB Online 许可'}));
 fireEvent.click(screen.getByRole('tab',{name:'MATLAB 代码'}));
 fireEvent.click(screen.getByRole('button',{name:'复制并打开 MATLAB Online'}));
 await waitFor(()=>expect(screen.getByRole('status').textContent).toContain('当前脚本已下载'));
 expect(screen.getByRole('status').textContent).not.toContain('当前修改已复制');
 expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
});
