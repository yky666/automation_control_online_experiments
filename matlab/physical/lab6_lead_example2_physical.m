% Editable electrical circuit, exported from ControlLab. Requires MATLAB, Simulink, Simscape.
% Uses Foundation electrical components; Simscape Electrical is not required.
clear; clc;
course_circuit=jsondecode('{"version":1,"lab":6,"task":"lead_example2","title":"实验 6 · lead_example2 元件电路","components":[{"id":"V1","type":"V","ports":{"p":"in","n":"0"},"value":1,"label":"信号发生器"},{"id":"VCVS2","type":"VCVS","ports":{"p":"error","n":"0","cp":"in","cn":"out"},"value":1,"label":"单位负反馈比较器"},{"id":"R3","type":"R","ports":{"p":"error","n":"lead1"},"value":408248.290463863,"label":"无源 R1"},{"id":"C4","type":"C","ports":{"p":"error","n":"lead1"},"value":0.000001,"label":"C4"},{"id":"R5","type":"R","ports":{"p":"lead1","n":"0"},"value":81649.6580927726,"label":"无源 R2"},{"id":"OpAmp6","type":"OpAmp","ports":{"plus":"lead1","minus":"buffer1","out":"buffer1"},"value":0,"label":"级间缓冲器"},{"id":"R7","type":"R","ports":{"p":"buffer1","n":"lead2"},"value":408248.290463863,"label":"无源 R1"},{"id":"C8","type":"C","ports":{"p":"buffer1","n":"lead2"},"value":0.000001,"label":"C8"},{"id":"R9","type":"R","ports":{"p":"lead2","n":"0"},"value":81649.6580927726,"label":"无源 R2"},{"id":"OpAmp10","type":"OpAmp","ports":{"plus":"lead2","minus":"buffer2","out":"buffer2"},"value":0,"label":"级间缓冲器"},{"id":"R11","type":"R","ports":{"p":"buffer2","n":"m10"},"value":100000,"label":"输入电阻"},{"id":"R12","type":"R","ports":{"p":"m10","n":"boost1"},"value":3600000,"label":"反馈电阻"},{"id":"R13","type":"R","ports":{"p":"g12","n":"0"},"value":100000,"label":"R13"},{"id":"OpAmp14","type":"OpAmp","ports":{"plus":"g12","minus":"m10","out":"boost1"},"value":0,"label":"p"},{"id":"R15","type":"R","ports":{"p":"boost1","n":"m14"},"value":100000,"label":"输入电阻"},{"id":"R16","type":"R","ports":{"p":"m14","n":"control"},"value":100000,"label":"反馈电阻"},{"id":"R17","type":"R","ports":{"p":"g16","n":"0"},"value":100000,"label":"R17"},{"id":"OpAmp18","type":"OpAmp","ports":{"plus":"g16","minus":"m14","out":"control"},"value":0,"label":"p"},{"id":"R19","type":"R","ports":{"p":"control","n":"m18"},"value":100000,"label":"输入电阻"},{"id":"C20","type":"C","ports":{"p":"m18","n":"plantI0"},"value":0.00001,"label":"积分电容"},{"id":"R21","type":"R","ports":{"p":"g20","n":"0"},"value":100000,"label":"R21"},{"id":"OpAmp22","type":"OpAmp","ports":{"plus":"g20","minus":"m18","out":"plantI0"},"value":0,"label":"i"},{"id":"R23","type":"R","ports":{"p":"plantI0","n":"m22"},"value":100000,"label":"输入电阻"},{"id":"C24","type":"C","ports":{"p":"m22","n":"plantI1"},"value":0.00001,"label":"积分电容"},{"id":"R25","type":"R","ports":{"p":"g24","n":"0"},"value":100000,"label":"R25"},{"id":"OpAmp26","type":"OpAmp","ports":{"plus":"g24","minus":"m22","out":"plantI1"},"value":0,"label":"i"},{"id":"R27","type":"R","ports":{"p":"plantI1","n":"m26"},"value":100000,"label":"输入电阻"},{"id":"R28","type":"R","ports":{"p":"m26","n":"plantL0"},"value":100000,"label":"反馈电阻"},{"id":"C29","type":"C","ports":{"p":"m26","n":"plantL0"},"value":0.000002,"label":"反馈电容"},{"id":"R30","type":"R","ports":{"p":"g29","n":"0"},"value":100000,"label":"R30"},{"id":"OpAmp31","type":"OpAmp","ports":{"plus":"g29","minus":"m26","out":"plantL0"},"value":0,"label":"lag"},{"id":"R32","type":"R","ports":{"p":"plantL0","n":"m31"},"value":100000,"label":"输入电阻"},{"id":"R33","type":"R","ports":{"p":"m31","n":"out"},"value":1000000,"label":"反馈电阻"},{"id":"R34","type":"R","ports":{"p":"g33","n":"0"},"value":100000,"label":"R34"},{"id":"OpAmp35","type":"OpAmp","ports":{"plus":"g33","minus":"m31","out":"out"},"value":0,"label":"p"}],"output":"out","note":"两级无源超前网络含单位缓冲运放，避免级间加载，并用真实电阻放大器补偿 α² 衰减。可删除缓冲器并重新接线研究加载效应。","opamp":{"mode":"ideal","A0":100000,"GBW":1000000,"rail":15},"settings":{"signal":"step","amplitude":1,"frequency":1,"stop":5,"points":3001,"rise":0.02}}');
[mdl,course_result]=build_course_physical(course_circuit);
open_system(mdl);
figure('Name','Electrical circuit simulation');
plot(course_result.time,course_result.input,'--',course_result.time,course_result.output);grid on;
xlabel('Time (s)');ylabel('Voltage (V)');legend('Input','Output');
writetable(course_result,[mdl '_result.csv']);
disp(['Saved ' mdl '.slx and ' mdl '_result.csv']);

function [mdl,result]=build_course_physical(g)
mdl=sprintf('physical_lab%d_%s',g.lab,g.task);
if bdIsLoaded(mdl),close_system(mdl,0);end
load_system('fl_lib');load_system('nesl_utility');new_system(mdl);
nets=containers.Map('KeyType','char','ValueType','any');
add_block('fl_lib/Electrical/Electrical Elements/Electrical Reference',[mdl '/Ground'],'Position',[30 600 70 640]);
ph=get_param([mdl '/Ground'],'PortHandles');connect('0',ph.LConn(1));
add_block('nesl_utility/Solver Configuration',[mdl '/Solver'],'Position',[120 600 170 650]);
ph=get_param([mdl '/Solver'],'PortHandles');connect('0',ph.RConn(1));
dt=g.settings.stop/(g.settings.points-1);t=(0:g.settings.points-1)'*dt;
switch g.settings.signal
case 'sine',u=g.settings.amplitude*sin(2*pi*g.settings.frequency*t);
case 'ramp',u=g.settings.amplitude*t;
otherwise,u=g.settings.amplitude*min(t/max(g.settings.rise,eps),1);
end
wks=get_param(mdl,'ModelWorkspace');assignin(wks,'physical_input',timeseries(u,t));
for ci=1:numel(g.components)
 a=g.components(ci);p=a.ports;name=[mdl '/' a.id];
 pos=[120+mod(ci-1,5)*270 80+floor((ci-1)/5)*160];pos=[pos pos+[90 65]];
 switch a.type
 case 'R'
  add_block('fl_lib/Electrical/Electrical Elements/Resistor',name,'Position',pos,'R',num2str(a.value,17),'R_unit','Ohm');
  ph=get_param(name,'PortHandles');connect(p.p,ph.LConn(1));connect(p.n,ph.RConn(1));
 case 'C'
  add_block('fl_lib/Electrical/Electrical Elements/Capacitor',name,'Position',pos,'c',num2str(a.value,17),'c_unit','F','r','0');
  ph=get_param(name,'PortHandles');connect(p.p,ph.LConn(1));connect(p.n,ph.RConn(1));
 case 'OpAmp'
  if strcmp(g.opamp.mode,'ideal')
   add_block('fl_lib/Electrical/Electrical Elements/Op-Amp',name,'Position',pos);
   ph=get_param(name,'PortHandles');connect(p.plus,ph.LConn(1));connect(p.minus,ph.LConn(2));connect(p.out,ph.RConn(1));
  else
   % Finite A0 / single-pole GBW / output rail; same equations as browser MNA.
   sense=[a.id '_sense'];vsensor(sense,p.plus,p.minus,pos+[0 80 0 80]);
   add_block('simulink/Math Operations/Gain',[name '_openloop'],'Gain',mat2str(g.opamp.A0),'Position',pos+[100 80 130 80]);
   add_block('simulink/Math Operations/Sum',[name '_error'],'Inputs','+-','Position',pos+[240 80 220 80]);
   add_block('simulink/Math Operations/Gain',[name '_pole'],'Gain',mat2str(2*pi*g.opamp.GBW/g.opamp.A0),'Position',pos+[320 80 330 80]);
   add_block('simulink/Continuous/Integrator',[name '_state'],'LimitOutput','on','UpperSaturationLimit',num2str(g.opamp.rail),'LowerSaturationLimit',num2str(-g.opamp.rail),'Position',pos+[420 80 440 80]);
   add_line(mdl,[sense '_ps/1'],[a.id '_openloop/1'],'autorouting','on');add_line(mdl,[a.id '_openloop/1'],[a.id '_error/1'],'autorouting','on');
   add_line(mdl,[a.id '_error/1'],[a.id '_pole/1'],'autorouting','on');add_line(mdl,[a.id '_pole/1'],[a.id '_state/1'],'autorouting','on');add_line(mdl,[a.id '_state/1'],[a.id '_error/2'],'autorouting','on');
   vsource(a.id,p.out,'0',[a.id '_state/1'],pos);
  end
 case 'V'
  add_block('simulink/Sources/From Workspace',[name '_input'],'VariableName','physical_input','Position',pos+[0 80 10 80]);
  add_block('simulink/Math Operations/Gain',[name '_gain'],'Gain',num2str(a.value,17),'Position',pos+[120 80 140 80]);
  add_line(mdl,[a.id '_input/1'],[a.id '_gain/1'],'autorouting','on');
  vsource(a.id,p.p,p.n,[a.id '_gain/1'],pos);
 case 'VCVS'
  sense=[a.id '_sense'];vsensor(sense,p.cp,p.cn,pos+[0 80 0 80]);
  add_block('simulink/Math Operations/Gain',[name '_gain'],'Gain',num2str(a.value,17),'Position',pos+[120 80 140 80]);
  add_line(mdl,[sense '_ps/1'],[a.id '_gain/1'],'autorouting','on');
  vsource(a.id,p.p,p.n,[a.id '_gain/1'],pos);
 end
end
vsensor('Measure',g.output,'0',[1450 100 1500 150]);
add_block('simulink/Sinks/Scope',[mdl '/Scope'],'Position',[1670 100 1740 155]);
add_block('simulink/Sinks/To Workspace',[mdl '/Record'],'VariableName','physical_output','SaveFormat','Timeseries','Position',[1670 200 1790 250]);
add_line(mdl,'Measure_ps/1','Scope/1','autorouting','on');add_line(mdl,'Measure_ps/1','Record/1','autorouting','on');
set_param(mdl,'Solver','ode15s','StopTime',num2str(t(end),17),'MaxStep',num2str(dt,17),'RelTol','1e-7','AbsTol','1e-9','ReturnWorkspaceOutputs','on');
save_system(mdl,fullfile(pwd,[mdl '.slx']));out=sim(mdl);y=out.get('physical_output');
result=table(t,u,interp1(y.Time,y.Data,t,'linear'),'VariableNames',{'time','input','output'});
 function connect(net,port)
  if isKey(nets,net),add_line(mdl,nets(net),port,'autorouting','on');else,nets(net)=port;end
 end
 function vsensor(id,p,n,pos)
  path=[mdl '/' id];add_block('fl_lib/Electrical/Electrical Sensors/Voltage Sensor',path,'Position',pos);
  h=get_param(path,'PortHandles');connect(p,h.LConn(1));connect(n,h.RConn(2));
  add_block('nesl_utility/PS-Simulink Converter',[path '_ps'],'Position',pos+[100 0 100 0],'Unit','V');
  h2=get_param([path '_ps'],'PortHandles');add_line(mdl,h.RConn(1),h2.LConn(1),'autorouting','on');
 end
 function vsource(id,p,n,signal,pos)
  path=[mdl '/' id];add_block(sprintf('fl_lib/Electrical/Electrical Sources/Controlled Voltage\nSource'),path,'Position',pos);
  h=get_param(path,'PortHandles');connect(p,h.LConn(1));connect(n,h.RConn(2));
  add_block('nesl_utility/Simulink-PS Converter',[path '_sp'],'Position',pos+[-100 0 -100 0],'Unit','V','FilteringAndDerivatives','provide','UdotUserProvided','1');
  add_block('simulink/Continuous/Derivative',[path '_derivative'],'Position',pos+[-100 80 -100 80]);
  add_line(mdl,signal,[id '_derivative/1'],'autorouting','on');add_line(mdl,[id '_derivative/1'],[id '_sp/2'],'autorouting','on');
  h2=get_param([path '_sp'],'PortHandles');add_line(mdl,h2.RConn(1),h.RConn(1),'autorouting','on');add_line(mdl,signal,[id '_sp/1'],'autorouting','on');
 end
end
