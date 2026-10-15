% Optional teacher check: compare Online script models with the SciPy examples.
function verify_online_models(project_root)
files=dir(fullfile(project_root,'matlab','online','*.m'));
checked=0; max_error=0;
for file=files'
    if contains(file.name,'_simulink'), continue; end
    key=extractBetween(file.name,'lab','.m');
    expected=jsondecode(fileread(fullfile(project_root,'public','course','examples',[key{1} '.json'])));
    script=fileread(fullfile(file.folder,file.name));
    parts=strsplit(script,"[num,den] = tfdata");
    setup=erase(parts{1},'clear; clc; close all;');
    [n,d]=evaluate_model(setup);
    while numel(n)>1 && n(1)==0, n(1)=[]; end
    while numel(d)>1 && d(1)==0, d(1)=[]; end
    n=n/d(1); d=d/d(1);
    en=expected.model.num(:)'; ed=expected.model.den(:)';
    assert(numel(n)==numel(en) && numel(d)==numel(ed),'%s sizes differ: n=%s d=%s expected n=%s d=%s',file.name,mat2str(n),mat2str(d),mat2str(en),mat2str(ed));
    err=max([abs(n-en)./max(1,abs(en)),abs(d-ed)./max(1,abs(ed))]);
    % Independent margin solvers can produce small lead-design differences.
    % Fixed algebraic models should agree to machine precision.
    tolerance=1e-10;
    if startsWith(expected.model.task_id,'lead'), tolerance=1e-3; end
    assert(err<tolerance,'%s differs from example: %g',file.name,err);
    checked=checked+1; max_error=max(max_error,err);
end
result=struct('checked',checked,'max_relative_coefficient_error',max_error);
disp(result);
fid=fopen(fullfile(project_root,'runtime','online-model-verification.json'),'w');
fprintf(fid,'%s',jsonencode(result));fclose(fid);
end

function [n,d]=evaluate_model(setup)
eval(setup);
[n,d]=tfdata(sys,'v');
end
