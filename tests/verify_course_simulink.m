function verify_course_simulink(project_root)
% Execute the actual exported block scripts in licensed desktop Simulink.
set(groot,'defaultFigureVisible','off');
work=fullfile(project_root,'runtime','course-audit','models');if ~exist(work,'dir'),mkdir(work);end
original=pwd;cleanup=onCleanup(@()cd(original));cd(work);
files=dir(fullfile(project_root,'matlab','online','*_simulink.m'));
results=struct('file',{},'status',{},'blocks',{},'error',{});
for k=1:numel(files)
    name=files(k).name;script=fullfile(files(k).folder,name);
    if contains(name,'residue1')
        results(end+1)=struct('file',name,'status','algebra-only','blocks',0,'error','');continue
    end
    try
        [mdl,output,time]=execute_export(script);
        blocks=find_system(mdl,'SearchDepth',1,'Type','Block');
        assert(all(isfinite(output(:))),'Output contains non-finite values');
        assert(numel(time)>1,'No simulation samples');
        if contains(name,'lab2_integrator')
            assert(any(strcmp(get_param(blocks,'BlockType'),'Integrator')),'Missing actual Integrator');
        end
        if contains(name,'lab2_pi')
            assert(any(strcmp(get_param(blocks,'BlockType'),'Sum')),'Missing PI parallel sum');
        end
        if contains(name,'lab4_stability1')||contains(name,'lab2_pi')||contains(name,'lab6_lead2')
            try,print(['-s' mdl],'-dpng','-r110',fullfile(work,[mdl '.png']));catch,end
        end
        results(end+1)=struct('file',name,'status','passed','blocks',numel(blocks),'error','');
        close_system(mdl,0);close all force;
    catch problem
        results(end+1)=struct('file',name,'status','failed','blocks',0,'error',problem.message);
        bdclose('all');close all force;
        fprintf('ERROR: %s\n',problem.message);
    end
    fid=fopen(fullfile(project_root,'runtime','course-audit','native-structure-results.json'),'w');fprintf(fid,'%s',jsonencode(results));fclose(fid);
    fprintf('%s: %s\n',name,results(end).status);
end
fid=fopen(fullfile(project_root,'runtime','course-audit','native-structure-results.json'),'w');fprintf(fid,'%s',jsonencode(results));fclose(fid);
assert(~any(strcmp({results.status},'failed')),'Some exported Simulink models failed. Inspect native-structure-results.json');
end

function [model,values,time]=execute_export(script)
eval(fileread(script));
model=mdl;values=yy.Data;time=yy.Time;
end
