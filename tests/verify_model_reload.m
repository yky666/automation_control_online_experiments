function verify_model_reload(project_root)
names={'course_lab1_ode_demo','course_lab2_integrator','course_lab2_pi','course_lab4_stability1','course_lab5_frequency_second','course_lab6_lead2'};
results=struct('model',{},'workspace',{},'passed',{});
for i=1:numel(names)
    path=fullfile(project_root,'runtime','course-audit','models',[names{i} '.slx']);
    load_system(path);workspace=get_param(names{i},'ModelWorkspace');
    assert(strcmp(workspace.DataSource,'Model File'),'Model workspace is not saved in the model');
    assert(hasVariable(workspace,'A'),'Model relies on external input amplitude');
    out=sim(names{i},'ReturnWorkspaceOutputs','on');series=out.get('web_output');
    assert(numel(series.Time)>1 && all(isfinite(series.Data(:))));
    results(end+1)=struct('model',names{i},'workspace',workspace.DataSource,'passed',true);
    close_system(names{i},0);
end
fid=fopen(fullfile(project_root,'runtime','course-audit','model-reload-results.json'),'w');fprintf(fid,'%s',jsonencode(results));fclose(fid);
fprintf('Reloaded and simulated %d self-contained models\n',numel(results));
end
