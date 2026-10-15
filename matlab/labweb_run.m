function json = labweb_run(request_json)
% Native MATLAB/Simulink worker. All inputs are validated by the local API.
req = jsondecode(request_json);
set(groot,'DefaultFigureVisible','off');
if strcmp(req.mode,'code')
    codeFile=fullfile(req.job_dir,'user_script.m');
    fid=fopen(codeFile,'w','n','UTF-8');fprintf(fid,'%s',req.code);fclose(fid);
    escaped=strrep(codeFile,'''','''''');
    cleanup=onCleanup(@()close('all','force'));
    transcript=evalc('evalin(''base'', [''run('''''' escaped '''''')'']);');
    figs=findall(groot,'Type','figure'); images={};
    for i=1:numel(figs)
        filename=sprintf('figure_%d.png',i);
        exportgraphics(figs(i),fullfile(req.job_dir,filename),'Resolution',160);
        images{end+1}=filename; %#ok<AGROW>
    end
    out=struct('console',transcript,'images',{images},'version',version,'engine','matlab');
    json=jsonencode(out);return
end
m=req.model;
num=reshape(m.num,1,[]);den=reshape(m.den,1,[]);
sys=tf(num,den);G=tf(reshape(m.open_num,1,[]),reshape(m.open_den,1,[]));
p=pole(sys);z=zero(sys);
w=reshape(req.preview.bode.w,[],1);
[mag,phase]=bode(G,w);
[GM,PM,Wcg,Wcp]=margin(G);
out=struct('version',version,'poles',[real(p),imag(p)],'zeros',[real(z),imag(z)], ...
    'bode',struct('w',w,'magnitude',20*log10(squeeze(mag)),'phase',squeeze(phase)), ...
    'margins',struct('phase_margin',PM,'gain_margin_db',20*log10(GM), ...
    'crossover',Wcp,'phase_crossover',Wcg,'gain_margin_infinite',isinf(GM)));
if numel(num)>numel(den)
    [r,rp,k]=residue(num,den);
    out.residue=struct('residues',[real(r),imag(r)],'poles',[real(rp),imag(rp)],'direct',k);
    out.time=[];out.input=[];out.output=[];
    if strcmp(req.mode,'simulink');error('ControlLab:Improper','Nonproper model cannot be simulated as Transfer Fcn.');end
else
    t=linspace(0,m.stop_time,m.points).';A=m.params.A;
    switch m.input_signal
        case 'step',u=A*ones(size(t));
        case 'ramp',u=A*t;
        case 'step_ramp',u=A*(1+t);
        case 'polynomial',u=A*(5+2*t+8*t.^2);
        otherwise,u=A*sin(2*pi*m.params.frequency*t);
    end
    if strcmp(req.mode,'simulink')
        mdl=['web_lab_' strrep(req.job_id,'-','_')];
        load_system('simulink');new_system(mdl);
        cleanup=onCleanup(@()close_system(mdl,0));
        add_block('simulink/Sources/From Workspace',[mdl '/Input'], ...
            'VariableName','web_input','Interpolate','on','Position',[35 90 155 125]);
        add_block('simulink/Continuous/Transfer Fcn',[mdl '/Plant'], ...
            'Numerator',mat2str(num,16),'Denominator',mat2str(den,16),'Position',[220 80 410 135]);
        add_block('simulink/Sinks/To Workspace',[mdl '/Output'], ...
            'VariableName','web_output','SaveFormat','Timeseries', ...
            'SampleTime',num2str(m.stop_time/(m.points-1),16),'Position',[480 90 590 125]);
        add_line(mdl,'Input/1','Plant/1');add_line(mdl,'Plant/1','Output/1');
        set_param(mdl,'StopTime',num2str(m.stop_time,16),'Solver',m.solver, ...
            'MaxStep',num2str(m.stop_time/(m.points-1),16),'RelTol','1e-7','AbsTol','1e-9');
        modelWorkspace=get_param(mdl,'ModelWorkspace');
        assignin(modelWorkspace,'web_input',timeseries(u,t));
        save_system(mdl,fullfile(req.job_dir,[mdl '.slx']));
        copyfile(fullfile(req.job_dir,[mdl '.slx']),fullfile(req.job_dir,'model.slx'));
        simIn=Simulink.SimulationInput(mdl);
        simIn=simIn.setVariable('web_input',timeseries(u,t));
        simIn=simIn.setModelParameter('ReturnWorkspaceOutputs','on');
        simOut=sim(simIn);ts=simOut.get('web_output');
        % Floating point sample periods can place the final hit just below StopTime.
        % Clamp the query by that rounding error rather than producing NaN at the last point.
        if ts.Time(end)<t(end)-2*m.stop_time/(m.points-1)
            error('ControlLab:IncompleteLog','Simulink output log does not cover the requested window.');
        end
        y=interp1(ts.Time,ts.Data,min(max(t,ts.Time(1)),ts.Time(end)),'linear');
        out.simulink=struct('model','model.slx','solver',m.solver,'logged_samples',numel(ts.Time), ...
            'output_sample_time',m.stop_time/(m.points-1));
        try
            print(['-s' mdl],'-dpng',fullfile(req.job_dir,'model.png'));
            out.simulink.image='model.png';
        catch
            % Model file and numerical simulation remain available.
        end
    else
        y=lsim(sys,u,t);
    end
    out.time=t;out.input=u;out.output=y;
    if isstable(sys)&&strcmp(m.input_signal,'step')&&abs(dcgain(sys)*A)>1e-12
        info=stepinfo(y,t,dcgain(sys)*A,'SettlingTimeThreshold',m.settling_threshold);
        out.stepinfo=struct('steady_state',dcgain(sys)*A,'overshoot',info.Overshoot, ...
            'settling_time',info.SettlingTime,'rise_time',info.RiseTime,'peak_time',info.PeakTime);
    end
    if isfield(m,'baseline')&&~isempty(m.baseline)
        b=m.baseline;sys0=tf(b.num.',b.den.');G0=tf(b.open_num.',b.open_den.');
        [mag0,ph0]=bode(G0,w);
        out.baseline=struct('y',lsim(sys0,u,t),'magnitude',20*log10(squeeze(mag0)),'phase',squeeze(ph0));
    end
    if strcmp(m.input_signal,'sine')&&isstable(sys)
        f=m.params.frequency;mask=t>=m.stop_time-5/f;
        coeff=[sin(2*pi*f*t(mask)),cos(2*pi*f*t(mask)),ones(sum(mask),1)]\y(mask);
        exact=squeeze(freqresp(sys,2*pi*f));B=hypot(coeff(1),coeff(2));
        out.sine_fit=struct('frequency_hz',f,'amplitude',B,'gain',B/A, ...
            'phase',atan2d(coeff(2),coeff(1)),'theoretical_gain',abs(exact), ...
            'theoretical_phase',angle(exact)*180/pi,'relative_gain_error',abs(B/A/abs(exact)-1));
    end
end
json=jsonencode(out,'ConvertInfAndNaN',true);
end
