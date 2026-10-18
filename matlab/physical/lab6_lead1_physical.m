% Editable electrical circuit, exported from ControlLab. Requires MATLAB, Simulink, Simscape.
% Uses Foundation electrical components; Simscape Electrical is not required.
clear; clc;
course_circuit=jsondecode('{"version":1,"lab":6,"task":"lead1","title":"实验 6 · lead1 元件电路","components":[{"id":"V1","type":"V","ports":{"p":"in","n":"0"},"value":1,"label":"信号发生器"},{"id":"VCVS2","type":"VCVS","ports":{"p":"error","n":"0","cp":"in","cn":"out"},"value":1,"label":"单位负反馈比较器"},{"id":"R3","type":"R","ports":{"p":"error","n":"leadMid"},"value":137219.44396967866,"label":"R3"},{"id":"R4","type":"R","ports":{"p":"leadMid","n":"leadMinus"},"value":201343.12317347125,"label":"R4"},{"id":"C5","type":"C","ports":{"p":"leadMid","n":"leadMinus"},"value":0.000001,"label":"C5"},{"id":"R6","type":"R","ports":{"p":"leadMinus","n":"leadRaw"},"value":338562.5671431499,"label":"R6"},{"id":"R7","type":"R","ports":{"p":"g6","n":"0"},"value":100000,"label":"R7"},{"id":"OpAmp8","type":"OpAmp","ports":{"plus":"g6","minus":"leadMinus","out":"leadRaw"},"value":0,"label":"有源超前"},{"id":"R9","type":"R","ports":{"p":"leadRaw","n":"m8"},"value":100000,"label":"输入电阻"},{"id":"R10","type":"R","ports":{"p":"m8","n":"control"},"value":100000,"label":"反馈电阻"},{"id":"R11","type":"R","ports":{"p":"g10","n":"0"},"value":100000,"label":"R11"},{"id":"OpAmp12","type":"OpAmp","ports":{"plus":"g10","minus":"m8","out":"control"},"value":0,"label":"p"},{"id":"R13","type":"R","ports":{"p":"control","n":"m12"},"value":100000,"label":"输入电阻"},{"id":"C14","type":"C","ports":{"p":"m12","n":"plantI0"},"value":0.00001,"label":"积分电容"},{"id":"R15","type":"R","ports":{"p":"g14","n":"0"},"value":100000,"label":"R15"},{"id":"OpAmp16","type":"OpAmp","ports":{"plus":"g14","minus":"m12","out":"plantI0"},"value":0,"label":"i"},{"id":"R17","type":"R","ports":{"p":"plantI0","n":"m16"},"value":100000,"label":"输入电阻"},{"id":"R18","type":"R","ports":{"p":"m16","n":"plantL0"},"value":100000,"label":"反馈电阻"},{"id":"C19","type":"C","ports":{"p":"m16","n":"plantL0"},"value":0.000005,"label":"反馈电容"},{"id":"R20","type":"R","ports":{"p":"g19","n":"0"},"value":100000,"label":"R20"},{"id":"OpAmp21","type":"OpAmp","ports":{"plus":"g19","minus":"m16","out":"plantL0"},"value":0,"label":"lag"},{"id":"R22","type":"R","ports":{"p":"plantL0","n":"m21"},"value":100000,"label":"输入电阻"},{"id":"R23","type":"R","ports":{"p":"m21","n":"sign"},"value":2000000,"label":"反馈电阻"},{"id":"R24","type":"R","ports":{"p":"g23","n":"0"},"value":100000,"label":"R24"},{"id":"OpAmp25","type":"OpAmp","ports":{"plus":"g23","minus":"m21","out":"sign"},"value":0,"label":"p"},{"id":"R26","type":"R","ports":{"p":"sign","n":"m25"},"value":100000,"label":"输入电阻"},{"id":"R27","type":"R","ports":{"p":"m25","n":"out"},"value":100000,"label":"反馈电阻"},{"id":"R28","type":"R","ports":{"p":"g27","n":"0"},"value":100000,"label":"R28"},{"id":"OpAmp29","type":"OpAmp","ports":{"plus":"g27","minus":"m25","out":"out"},"value":0,"label":"p"}],"output":"out","note":"有源超前含实际 R1、R2、R3、C 和极性补偿运放；被控对象由积分、RC 惯性电路实现。","opamp":{"mode":"ideal","A0":100000,"GBW":1000000,"rail":15},"settings":{"signal":"step","amplitude":1,"frequency":1,"stop":5,"points":3001,"rise":0.02}}');
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
