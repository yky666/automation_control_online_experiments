function verify_physical(project_root)
fixtures=jsondecode(fileread(fullfile(project_root,'runtime','physical','fixtures.json')));
results=struct('name',{},'passed',{},'relative_error',{},'excluded_corner_samples',{},'message',{});
cd(fullfile(project_root,'runtime','physical'));
for k=1:numel(fixtures)
 name=fixtures(k).name;
 stem=erase(name,'physical_');script=fullfile(project_root,'matlab','physical',[stem '_physical.m']);
 try
  result=run_one(script);f=fixtures(k);reference=f.browser.output;
  valid=true(size(reference));
  if any(strcmp(name,{'physical_lab2_d','physical_lab2_pd'})) && strcmp(f.circuit.settings.signal,'step')
   % At the corner of the ramp-to-step input the derivative is discontinuous.
   % Compare smooth intervals, rather than assign a physical peak to the corner.
   dt=f.browser.dt;valid=abs(result.time-f.circuit.settings.rise)>2*dt & result.time>2*dt;
  end
  difference=max(abs(result.output(valid)-reference(valid)));relative=difference/max(1,max(abs(reference(valid))));
  assert(all(isfinite(result.output)),'Nonfinite native result');
  assert(relative<.03,'Browser/native difference exceeds 3 percent');
  results(end+1)=struct('name',name,'passed',true,'relative_error',relative,'excluded_corner_samples',sum(~valid),'message','');
  model_file=get_param(name,'FileName');target=fullfile(project_root,'matlab','physical',[name '.slx']);
  if ~strcmp(model_file,target),copyfile(model_file,target);end
  fprintf('PASS %s %.6g\n',name,relative);
 catch err
  results(end+1)=struct('name',name,'passed',false,'relative_error',NaN,'excluded_corner_samples',0,'message',getReport(err,'basic','hyperlinks','off'));
  fprintf('FAIL %s: %s\n',name,err.message);
 end
 close all;bdclose('all');
 fid=fopen(fullfile(project_root,'runtime','physical','verification.json'),'w');fprintf(fid,'%s',jsonencode(results));fclose(fid);
end
assert(all([results.passed]),'Physical model verification has failures');
end
function result=run_one(script)
run(script);result=course_result;
end
