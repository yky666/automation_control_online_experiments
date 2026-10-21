// Emit actual browser-solver traces for the independent SciPy audit (one case per line).
import fs from 'node:fs';
import {courseGraph} from '../frontend/blocks.js';
import {simulateSignal} from '../frontend/signal-solver.js';
import {circuitTemplate,simulateCircuit} from '../frontend/circuits.js';
const catalog=JSON.parse(fs.readFileSync('public/course/catalog.json'));
for(const lab of catalog)for(const task of lab.tasks){
 const e=JSON.parse(fs.readFileSync(`public/course/examples/${lab.id}_${task.id}.json`));
 const base={lab:lab.id,task:task.id,num:e.model.num,den:e.model.den,params:task.defaults};
 if(e.model.num.length<=e.model.den.length){
  const runs=[10001,20001].map(points=>{
   const request={lab_id:lab.id,task_id:task.id,params:task.defaults,stop_time:e.model.stop_time,points,amplitude:e.model.params.A,input_signal:e.model.input_signal,auto_duration:false};
   const r=simulateSignal(courseGraph(request,e.model),request,e);
   return {time:r.time,input:r.input,output:lab.id===2&&['d','pd'].includes(task.id)?r.traces['Scope 2']:r.output};
  });
  console.log(JSON.stringify({...base,kind:'signal',runs}));
 }
 if([2,4,5,6].includes(lab.id)){
  const circuit=circuitTemplate(lab.id,task.id,task.defaults,e.model.design);circuit.settings.points=20001;
  const r=simulateCircuit(circuit);
  console.log(JSON.stringify({...base,kind:'circuit',settings:circuit.settings,opamp:circuit.opamp,runs:[{time:r.time,input:r.input,output:r.output}]}));
 }
}
