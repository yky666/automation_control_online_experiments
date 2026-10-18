import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {circuitTemplate,simulateCircuit} from '../frontend/circuits.js';
import {physicalScript} from '../frontend/physical-export.js';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const catalog=JSON.parse(fs.readFileSync(path.join(root,'public/course/catalog.json'),'utf8'));
const dir=path.join(root,'matlab/physical');fs.mkdirSync(dir,{recursive:true});
const fixtures=[];
for(const lab of catalog.filter(l=>[2,4,5,6].includes(l.id)))for(const task of lab.tasks){
 const example=JSON.parse(fs.readFileSync(path.join(root,`public/course/examples/${lab.id}_${task.id}.json`),'utf8'));
 const g=circuitTemplate(lab.id,task.id,task.defaults,example.model.design);
 if(lab.id===5){g.settings.signal='sine';g.settings.frequency=task.defaults.frequency||1;g.settings.stop=10/g.settings.frequency;g.settings.rise=Math.min(.001,g.settings.stop/1000);}
 fs.writeFileSync(path.join(dir,`lab${lab.id}_${task.id}_physical.m`),physicalScript(g));
 fixtures.push({name:`physical_lab${lab.id}_${task.id}`,circuit:g,browser:simulateCircuit(g)});
}
const finite=circuitTemplate(2,'p',{K:10});finite.task='finite_rail';finite.opamp.mode='finite';finite.settings.amplitude=3;finite.settings.stop=.02;
fs.writeFileSync(path.join(dir,'lab2_finite_rail_physical.m'),physicalScript(finite));fixtures.push({name:'physical_lab2_finite_rail',circuit:finite,browser:simulateCircuit(finite)});
fs.mkdirSync(path.join(root,'runtime/physical'),{recursive:true});
fs.writeFileSync(path.join(root,'runtime/physical/fixtures.json'),JSON.stringify(fixtures));
fs.mkdirSync(path.join(root,'public/physical'),{recursive:true});
for(const file of fs.readdirSync(dir))if(/\.(m|slx)$/.test(file))fs.copyFileSync(path.join(dir,file),path.join(root,'public/physical',file));
console.log(`Exported ${fixtures.length} physical circuit scripts and browser fixtures`);
