// Check the artifact, including project-subpath URLs, before publishing Pages.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dist=path.join(root,'dist'),base=process.argv[2]||'/';
assert(base.startsWith('/')&&base.endsWith('/'),'Base path must start and end with /');
const checked=new Set();
function file(relative){
 const target=path.resolve(dist,relative.replace(/^\//,''));
 assert(target.startsWith(dist+path.sep),'Asset must stay inside dist');
 assert(fs.statSync(target).isFile(),`Missing static asset: ${relative}`);checked.add(relative);return target;
}
const html=fs.readFileSync(file('index.html'),'utf8');
const urls=[...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(m=>m[1]).filter(s=>!s.startsWith('http'));
for(const url of urls){assert(url.startsWith(base+'assets/'),`Wrong entry asset prefix: ${url}`);file(decodeURIComponent(url.slice(base.length)));}
const assets=fs.readdirSync(path.join(dist,'assets'));
for(const worker of ['circuit.worker-','signal.worker-'])assert(assets.some(name=>name.startsWith(worker)&&name.endsWith('.js')),`Missing simulation worker: ${worker}`);
const scripts=assets.filter(n=>n.endsWith('.js')&&!n.startsWith('plotly-')).map(n=>fs.readFileSync(file('assets/'+n),'utf8')).join('\n');
assert(scripts.includes(base),'Compiled code must include the deployment base path');
const catalog=JSON.parse(fs.readFileSync(file('course/catalog.json'),'utf8'));
assert.equal(catalog.length,6);let tasks=0;
for(const lab of catalog){
 for(const resource of lab.files)file(resource.url);
 for(const task of lab.tasks){
  tasks++;const key=lab.id+'_'+task.id;
  file(`course/examples/${key}.json`);file(`course/reports/${key}.html`);
  if(task.native_model)file(task.native_model.download);
  if([2,4,5,6].includes(lab.id)){file(`physical/physical_lab${key}.slx`);file(`physical/lab${key}_physical.m`);}
 }
}
assert.equal(tasks,38);
console.log(`Static artifact verified: 6 chapters, ${tasks} tasks, 2 simulation workers, ${checked.size} linked files, base=${base}`);
