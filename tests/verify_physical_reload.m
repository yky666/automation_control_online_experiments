function verify_physical_reload(project_root)
names={'physical_lab2_pi','physical_lab2_finite_rail','physical_lab6_lead2'};
results=struct('name',{},'passed',{},'workspace',{},'electric_components',{});
for k=1:numel(names)
 name=names{k};load_system(fullfile(project_root,'matlab','physical',[name '.slx']));
 wks=get_param(name,'ModelWorkspace');assert(hasVariable(wks,'physical_input'),'Missing embedded input');
 out=sim(name,'ReturnWorkspaceOutputs','on');y=out.get('physical_output');assert(all(isfinite(y.Data(:))) && numel(y.Time)>2);
 blocks=find_system(name,'SearchDepth',1,'Type','Block');count=0;
 for j=1:numel(blocks)
  reference=get_param(blocks{j},'ReferenceBlock');if startsWith(reference,'fl_lib/'),count=count+1;end
 end
 assert(count>4,'Missing real electrical components');
 results(end+1)=struct('name',name,'passed',true,'workspace',wks.DataSource,'electric_components',count);
 if k==1
  print(['-s' name],'-dpng','-r120',fullfile(project_root,'docs','native-models',[name '.png']));
 end
 close_system(name,0);
end
fid=fopen(fullfile(project_root,'docs','physical-reload-verification.json'),'w');fprintf(fid,'%s',jsonencode(results));fclose(fid);
fprintf('Reloaded and simulated %d physical circuits\n',numel(results));
end
