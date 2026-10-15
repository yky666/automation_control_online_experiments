import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {makeCode} from '../frontend/online.js';
const catalog=JSON.parse(await readFile(new URL('../public/course/catalog.json',import.meta.url),'utf8'));
await mkdir(new URL('../matlab/online/',import.meta.url),{recursive:true});
for(const lab of catalog)for(const task of lab.tasks){
 const example=JSON.parse(await readFile(new URL(`../public/course/examples/${lab.id}_${task.id}.json`,import.meta.url),'utf8'));
 const req={lab_id:lab.id,task_id:task.id,params:task.defaults,stop_time:lab.id===4?4:5,amplitude:1,points:1501,settling_threshold:.02,solver:'ode45',auto_duration:true};
 for(const mode of ['matlab','simulink'])await writeFile(new URL(`../matlab/online/lab${lab.id}_${task.id}${mode==='simulink'?'_simulink':''}.m`,import.meta.url),makeCode(example,req,mode),'utf8');
}
console.log('Exported 66 standalone MATLAB / Simulink scripts');
