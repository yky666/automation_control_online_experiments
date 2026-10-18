// Course signal-flow blocks. Simulation and the full library remain in Simulink.
export const BLOCKS={
 Step:{library:'simulink/Sources/Step',inputs:0,outputs:1,params:{Time:'0',Before:'0',After:'A'}},
 SineWave:{library:'simulink/Sources/Sine Wave',inputs:0,outputs:1,params:{Amplitude:'A',Frequency:'2*pi*frequency',Phase:'0',SampleTime:'0'}},
 Ramp:{library:'simulink/Sources/Ramp',inputs:0,outputs:1,params:{slope:'A',start:'0',InitialOutput:'0'}},
 FromWorkspace:{library:'simulink/Sources/From Workspace',inputs:0,outputs:1,params:{VariableName:'web_input'}},
 Gain:{library:'simulink/Math Operations/Gain',inputs:1,outputs:1,params:{Gain:'K'}},
 Sum:{library:'simulink/Math Operations/Sum',inputs:2,outputs:1,params:{Inputs:'+-'}},
 Integrator:{library:'simulink/Continuous/Integrator',inputs:1,outputs:1,params:{InitialCondition:'0'}},
 Derivative:{library:'simulink/Continuous/Derivative',inputs:1,outputs:1,params:{}},
 TransferFcn:{library:'simulink/Continuous/Transfer Fcn',inputs:1,outputs:1,params:{Numerator:'[1]',Denominator:'[1 1]'}},
 Scope:{library:'simulink/Sinks/Scope',inputs:1,outputs:0,params:{NumInputPorts:'1'}},
};
export function portCount(block){const spec=BLOCKS[block.type];return {inputs:block.type==='Sum'?String(block.params?.Inputs||'').replace(/[^+-]/g,'').length:block.type==='Scope'?Number(block.params?.NumInputPorts)||0:spec?.inputs||0,outputs:spec?.outputs||0}}
export function newBlock(type,id,x=100,y=100,params={}){if(!BLOCKS[type])throw Error('不支持的模块');return {id,type,x,y,params:{...BLOCKS[type].params,...params}}}
export function courseGraph(request,model){
 const nodes=[],edges=[];let n=0;
 const add=(type,params={},x=120,y=120)=>{const b=newBlock(type,'b'+(++n),x,y,params);nodes.push(b);return b.id};
 const link=(from,to,port=1)=>edges.push({from,to,port});
 const source=add(({sine:'SineWave',ramp:'Ramp',step_ramp:'FromWorkspace',polynomial:'FromWorkspace'})[model.input_signal]||'Step',{},30,100);
 let end,scope;
 if(request.lab_id===1&&request.task_id==='ode_demo'){
  const sum=add('Sum',{},185,100),integrator=add('Integrator',{},370,100),gain=add('Gain',{Gain:'2'},370,270);link(source,sum);link(sum,integrator);link(integrator,gain);link(gain,sum,2);end=integrator;
 }else if(request.lab_id===1&&request.task_id==='connections'&&!request.numerator){
  const g1=add('TransferFcn',{Numerator:'[5]',Denominator:'[1 1]'},230,100);end=add('TransferFcn',{Numerator:'[2 1]',Denominator:'[1 0]'},450,100);link(source,g1);link(g1,end);
 }else if(request.lab_id===2&&!request.numerator){
  const kind=request.task_id;
  if(kind==='p'){end=add('Gain',{},270,100);link(source,end)}
  if(kind==='inertia'){end=add('TransferFcn',{Numerator:'[K]',Denominator:'[T 1]'},270,100);link(source,end)}
  if(kind==='integrator'){const gain=add('Gain',{Gain:'K/T'},220,100);end=add('Integrator',{},410,100);link(source,gain);link(gain,end)}
  if(kind==='d'){const gain=add('Gain',{Gain:'K*T'},220,100);end=add('Derivative',{},410,100);link(source,gain);link(gain,end)}
  if(kind==='pi'||kind==='pd'){
   const operation=add(kind==='pi'?'Integrator':'Derivative',{},200,50),scale=add('Gain',{Gain:kind==='pi'?'1/T':'T'},380,50),sum=add('Sum',{Inputs:'++'},560,100);end=add('Gain',{},730,100);link(source,operation);link(operation,scale);link(scale,sum);link(source,sum,2);link(sum,end);
  }
  if(kind==='d'||kind==='pd'){
   scope=add('Scope',{NumInputPorts:'2'},930,100);link(end,scope);
   const filtered=add('TransferFcn',{Numerator:kind==='d'?'[K*T 0]':'[K*(Tf+T) K]',Denominator:'[Tf 1]'},490,300);link(source,filtered);link(filtered,scope,2);
  }
 }else if(request.lab_id===4&&!request.numerator){
  const sum=add('Sum',{},190,100),gain=add('Gain',{Gain:'10*K'},350,100),integrator=add('Integrator',{},510,100),lag=add('TransferFcn',{Denominator:'[T1 1]'},670,100);link(source,sum);link(sum,gain);link(gain,integrator);link(integrator,lag);end=lag;
  if(request.task_id!=='reduced'){end=add('TransferFcn',{Denominator:'[T2 1]'},840,100);link(lag,end)}link(end,sum,2);
 }else if(request.lab_id===6&&!request.numerator){
  const sum=add('Sum',{},190,100);let prev=sum;link(source,sum);
  const passive=['lead2','lead_example2'].includes(request.task_id);
  for(let j=0;j<(passive?2:1);j++){const c=add('TransferFcn',{Numerator:passive?'[1/wz 1]/alpha':'[1/wz 1]',Denominator:'[1/wp 1]'},350+j*175,100);link(prev,c);prev=c}
  if(passive){const g=add('Gain',{Gain:'alpha^2'},700,100);link(prev,g);prev=g}
  end=add('TransferFcn',{Numerator:'plant_num',Denominator:'plant_den'},880,100);link(prev,end);link(end,sum,2);
 }else if(request.lab_id===5&&request.task_id==='frequency_second'&&!request.numerator){
  const sum=add('Sum',{},180,100),gain=add('Gain',{Gain:'10'},340,100),i=add('Integrator',{},500,100),lag=add('TransferFcn',{Denominator:'[1/(2*zeta*wn) 1]'},660,100);end=add('Gain',{Gain:'wn/(20*zeta)'},840,100);link(source,sum);link(sum,gain);link(gain,i);link(i,lag);link(lag,end);link(end,sum,2);
 }else{
  end=add('TransferFcn',{Numerator:'num',Denominator:'den'},350,100);link(source,end);
 }
 if(!scope){scope=add('Scope',{NumInputPorts:request.lab_id===5?'2':'1'},1080,100);link(end,scope);if(request.lab_id===5)link(source,scope,2)}
 return {version:1,lab_id:request.lab_id,task_id:request.task_id,nodes,edges};
}

export function validateGraph(graph){
 const errors=[];if(!Array.isArray(graph?.nodes)||!graph.nodes.length||graph.nodes.length>60||!Array.isArray(graph.edges)||graph.edges.length>360)return ['模型需包含 1～60 个模块和最多 360 条连线'];
 const ids=new Set();
 for(const node of graph.nodes){
  if(!/^[A-Za-z][A-Za-z0-9_]{0,39}$/.test(node.id)||ids.has(node.id)||!BLOCKS[node.type]){errors.push('模块名称重复或类型无效');continue}ids.add(node.id);
  if(!Number.isFinite(node.x)||!Number.isFinite(node.y)||node.x<0||node.y<0||node.x>3000||node.y>1500)errors.push(node.id+' 的位置无效');
  for(const key of Object.keys(BLOCKS[node.type].params)){const value=node.params?.[key];if(typeof value!=='string'||!value.trim()||value.length>240||/[\r\n'"%]/.test(value))errors.push(node.id+' 的参数 '+key+' 无效')}
  if(node.type==='Sum'&&!/^[+-]{2,6}$/.test(node.params?.Inputs))errors.push(node.id+' 的 Sum 符号需为 2～6 个 + 或 -');
  if(node.type==='Scope'&&!/^[1-6]$/.test(node.params?.NumInputPorts))errors.push('Scope 输入端口数需为 1～6');
 }
 const occupied=new Set();for(const edge of graph.edges){const from=graph.nodes.find(n=>n.id===edge.from),to=graph.nodes.find(n=>n.id===edge.to),key=edge.to+':'+edge.port;
  if(!from||!to||!BLOCKS[from.type]||!BLOCKS[to.type]||portCount(from).outputs<1||!Number.isInteger(edge.port)||edge.port<1||edge.port>portCount(to).inputs){errors.push('连线的源或目标端口无效');continue}if(occupied.has(key))errors.push(key+' 已有输入连线');occupied.add(key);
 }
 for(const node of graph.nodes){if(!BLOCKS[node.type])continue;for(let p=1;p<=portCount(node).inputs;p++)if(!occupied.has(node.id+':'+p))errors.push(node.id+' 的输入 '+p+' 未连接')}
 if(!graph.nodes.some(n=>n.type==='Scope'))errors.push('请插入 Scope 观察输出');
 return [...new Set(errors)];
}

export function modelScript(graph,{prelude='',request={}}={}){
 const errors=validateGraph(graph);if(errors.length)throw Error(errors.join('；'));
 const quote=s=>"'"+s.replace(/'/g,"''")+"'";
 const name=`course_lab${Number(graph.lab_id)||1}_${String(graph.task_id||'model').replace(/[^A-Za-z0-9_]/g,'')}`;
 const lines=[prelude,"% 课程模块结构；在原生 Simulink 中继续插入、组合、编辑和仿真",`mdl = '${name}';`,"if bdIsLoaded(mdl), close_system(mdl,0); end","new_system(mdl);","[num,den]=tfdata(sys,'v');","if exist('G0','var'), [plant_num,plant_den]=tfdata(G0,'v'); end","if exist('u','var') && exist('t','var'), wks=get_param(mdl,'ModelWorkspace'); assignin(wks,'web_input',timeseries(u,t)); end"];
 const variables=[...new Set(['A','K','T','Tf','T1','T2','frequency','wn','zeta','alpha','wz','wp','GBW','num','den','plant_num','plant_den',...Object.keys(request.params||{})])].filter(v=>/^[A-Za-z][A-Za-z0-9_]*$/.test(v));
 lines.push("% 将模块变量保存到模型工作区，避免依赖个人基础工作区配置。","wks=get_param(mdl,'ModelWorkspace');",`course_variables={${variables.map(quote).join(',')}};`,"for course_i=1:numel(course_variables), course_name=course_variables{course_i}; if exist(course_name,'var'), assignin(wks,course_name,eval(course_name)); end; end");
 for(const b of graph.nodes){let args=Object.keys(BLOCKS[b.type].params).flatMap(key=>[quote(key),quote(b.params[key])]);lines.push(`add_block('${BLOCKS[b.type].library}',[mdl '/${b.id}'],'Position',[${b.x} ${b.y} ${b.x+115} ${b.y+65}]${args.length?','+args.join(','):''});`)}
 for(const e of graph.edges)lines.push(`add_line(mdl,'${e.from}/1','${e.to}/${e.port}','autorouting','on');`);
 const scope=graph.nodes.find(n=>n.type==='Scope'),output=graph.edges.find(e=>e.to===scope.id&&e.port===1);
 lines.push("add_block('simulink/Sinks/To Workspace',[mdl '/Record'],'VariableName','web_output','SaveFormat','Timeseries','Position',[1070 340 1190 380]);",`add_line(mdl,'${output.from}/1','Record/1','autorouting','on');`);
 const stop=Number(request.stop_time||5);if(!(stop>0&&stop<=120))throw Error('仿真时间无效');
 lines.push(`model_stop=${stop}; model_step=model_stop/1500;`,"if exist('t','var') && numel(t)>1, model_stop=t(end); model_step=t(2)-t(1); end",`set_param(mdl,'StopTime',num2str(model_stop,16),'Solver','${request.solver==='ode15s'?'ode15s':'ode45'}','RelTol','1e-7','AbsTol','1e-9','MaxStep',num2str(model_step,16),'ReturnWorkspaceOutputs','on');`,"save_system(mdl); open_system(mdl);","% Record 为附加数据记录模块；Scope 可双击查看各通道。","out=sim(mdl); yy=out.get('web_output');","figure; plot(yy.Time,yy.Data); grid on; xlabel('Time (s)'); ylabel('Output');");
 return lines.join('\n');
}
