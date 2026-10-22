export const REPORT_KEY='control-lab-personal-report-v1';
export const emptyReport=()=>({version:1,title:'自动控制原理实验报告',name:'',studentId:'',className:'',date:new Date().toISOString().slice(0,10),purpose:'',theory:'',content:'',steps:'',analysis:'',conclusion:'',equipment:'',extension:'',questions:'',reflection:'',runs:[]});
export function readReport(){try{const r=JSON.parse(localStorage.getItem(REPORT_KEY));if(r?.version===1&&Array.isArray(r.runs))return {...emptyReport(),...r};}catch{}return emptyReport()}
export function saveReport(d){localStorage.setItem(REPORT_KEY,JSON.stringify(d))}
export function snapshotRun(r,title){
 if(!Array.isArray(r.time)||r.time.length<2||!r.time.every(Number.isFinite))throw Error('运行时间序列无效');
 const series={input:r.input,output:r.output,...r.traces};
 for(const a of Object.values(series))if(!Array.isArray(a)||a.length!==r.time.length||!a.every(Number.isFinite))throw Error('运行数据不完整');
 const indices=Array.from({length:Math.min(1001,r.time.length)},(_,i)=>Math.round(i*(r.time.length-1)/(Math.min(1001,r.time.length)-1)));
 return {id:crypto.randomUUID(),selected:true,title,notes:'',createdAt:r.createdAt,engine:r.engine,method:r.method,originalPoints:r.time.length,time:indices.map(i=>r.time[i]),series:Object.fromEntries(Object.entries(series).map(([k,a])=>[k,indices.map(i=>a[i])])),model:r.graph||r.circuit,request:r.request||null};
}
export function captureRun(r,title){try{const d=readReport();d.runs.push(snapshotRun(r,title));saveReport(d);window.dispatchEvent(new Event('personal-report-updated'));}catch(e){window.dispatchEvent(new CustomEvent('personal-report-error',{detail:'运行已完成，但报告存档失败：'+e.message+'。请先导出运行 JSON。'}));}}
export const fields=[['purpose','实验目的'],['content','实验内容（可填写自主扩展实验）'],['equipment','实验仪器、设备及材料'],['theory','实验原理'],['steps','实验步骤与结果分析'],['analysis','结果复核与讨论'],['extension','自主扩展实验'],['questions','思考题'],['conclusion','实验结论'],['reflection','实验心得与反思']];
export function reportSections(d){
 const selected=d.runs.filter(r=>r.selected);
 return [
  {heading:'一、实验目的',text:d.purpose||'（未填写）'},
  {heading:'二、实验任务/要求',text:d.content||'（未填写）'},
  {heading:'三、实验仪器、设备及材料',text:d.equipment||'（未填写）'},
  {heading:'四、实验原理',text:d.theory||'（未填写）'},
  {heading:'五、实验步骤与结果分析',text:(d.steps||'（未填写）')+(!selected.length?'\n未选择实际运行记录。':'')},
  ...selected.map((r,i)=>({heading:`5.${i+1} ${r.title}`,subheading:true,text:`${r.createdAt} · ${r.engine}\n${r.method}\n${r.engine==='imported-csv'?'本次数据由用户导入，来源和模型对应关系需自行确认。':'本次为浏览器教学数值求解。'}\n曲线保留 ${r.time.length} / ${r.originalPoints} 点，抽样可能遗漏快速瞬态；完整数据请另存 CSV / JSON。末值不代表稳态。\n${r.notes||'（个人记录未填写）'}`,run:r})),
  {heading:'六、结果复核与自主扩展实验',text:`${d.analysis||'（结果复核未填写）'}\n${d.extension||'（自主扩展未填写）'}`},
  {heading:'七、思考题',text:d.questions||'（未填写）'},
  {heading:'八、实验结论',text:d.conclusion||'（未填写）'},
  {heading:'九、实验心得与反思',text:d.reflection||'（未填写）'},
  ...selected.map((r,i)=>({heading:`附录 ${i+1} 运行参数与模型快照`,text:JSON.stringify({request:r.request,model:r.model},null,2),appendix:true}))
 ];
}
export function downloadBlob(data,name,type){const url=URL.createObjectURL(new Blob([data],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000)}
function chartPoints(r,a,w,h){const lo=Math.min(...a),hi=Math.max(...a),span=hi-lo||1,t0=r.time[0],dt=r.time.at(-1)-t0||1;return {lo,hi,points:a.map((v,i)=>[45+(r.time[i]-t0)/dt*(w-65),25+(hi-v)/span*(h-65)])}}
function chartPng(r,a,label){const c=document.createElement('canvas');c.width=1000;c.height=340;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,c.width,c.height);x.strokeStyle='#247d78';x.lineWidth=2;const p=chartPoints(r,a,1000,340);x.beginPath();p.points.forEach(([a,b],i)=>i?x.lineTo(a,b):x.moveTo(a,b));x.stroke();x.fillStyle='#222';x.font='16px sans-serif';x.fillText(`${label}   min=${p.lo.toPrecision(4)}  max=${p.hi.toPrecision(4)}`,45,18);x.fillText(`${r.time[0]} s`,45,330);x.fillText(`${r.time.at(-1)} s`,900,330);return Uint8Array.from(atob(c.toDataURL('image/png').split(',')[1]),c=>c.charCodeAt(0))}
const escapeXml=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c])).replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,'');
// Clone the reference's paragraph roles and page furniture rather than rebuilding a generic document.
export async function wordReport(d,renderChart=chartPng,{template,patterns}={}){
 if(!template||!patterns)throw Error('学校报告模板尚未加载');
 const {default:JSZip}=await import('jszip');const zip=await JSZip.loadAsync(template);
 const paragraph=(text,role='body')=>`<w:p>${patterns[role].pPr}<w:r>${patterns[role].rPr}<w:t xml:space="preserve">${escapeXml(text)}</w:t></w:r></w:p>`;
 let body='',relations='',chart=0;
 for(const section of reportSections(d)){
  body+=paragraph(section.heading,section.subheading?'subheading':'heading');
  for(const line of section.text.split('\n'))body+=paragraph(line);
  if(section.run)for(const [label,values] of Object.entries(section.run.series)){
   chart++;body+=paragraph(`图 ${chart} ${label}`,'caption');
   const id=`rIdReportChart${chart}`,path=`media/report-chart-${chart}.png`;
   let drawing=patterns.drawing.replace(/descr="[^"]*"/g,()=>`descr="${escapeXml(label)}"`).replace(/r:embed="[^"]+"/,`r:embed="${id}"`)
    .replace(/(<wp:extent|<a:ext) cx="\d+" cy="\d+"/g,'$1 cx="5700000" cy="1938000"')
    .replace(/(<wp:docPr|<pic:cNvPr) id="\d+"/g,`$1 id="${1000+chart}"`);
   body+=`<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r>${drawing}</w:r></w:p>`;
   zip.file('word/'+path,renderChart(section.run,values,label));
   relations+=`<Relationship Id="${id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="${path}"/>`;
  }
 }
 let xml=await zip.file('word/document.xml').async('string');
 const marker='<w:p><w:r><w:t>{{REPORT_BODY}}</w:t></w:r></w:p>';
 if(!xml.includes(marker))throw Error('学校报告模板正文槽位缺失');
 xml=xml.replace(marker,()=>body);
 for(const [key,value] of Object.entries({experimentName:d.title,date:d.date,studentId:d.studentId,name:d.name,className:d.className}))xml=xml.replaceAll('{{'+key+'}}',()=>escapeXml(value));
 zip.file('word/document.xml',xml);
 const relPath='word/_rels/document.xml.rels';const rels=await zip.file(relPath).async('string');zip.file(relPath,rels.replace('</Relationships>',relations+'</Relationships>'));
 return new Blob([await zip.generateAsync({type:'uint8array',compression:'DEFLATE'})],{type:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'});
}

export async function pdfReport(d,fontBytes,{wordmark,seal}={}){
 if(!wordmark||!seal)throw Error('学校报告校徽尚未加载');
 const {PDFDocument,rgb,pushGraphicsState,popGraphicsState,rectangle,clip,endPath}=await import('pdf-lib');const {default:fontkit}=await import('@pdf-lib/fontkit');
 const pdf=await PDFDocument.create();pdf.registerFontkit(fontkit);
 const font=await pdf.embedFont(new Uint8Array(fontBytes),{subset:false});
 const logo=await pdf.embedJpg(new Uint8Array(wordmark)),watermark=await pdf.embedPng(new Uint8Array(seal));
 const width=595.3,height=841.9,left=64.8,right=530.5,bottom=54;let page,y;
 const newPage=()=>{page=pdf.addPage([width,height]);page.drawImage(watermark,{x:(width-265.75)/2,y:(height-265.75)/2,width:265.75,height:265.75,opacity:.18});y=height-54};
 const textAt=(text,x,atY,size=11,bold=false)=>{page.drawText(text,{x,y:atY,size,font,color:rgb(0,0,0)});if(bold)page.drawText(text,{x:x+.2,y:atY,size,font,color:rgb(0,0,0)});};
 const wrap=(raw,size,max)=>{const lines=[];for(const input of String(raw).split('\n')){let part='';for(const c of input.replace(/[\x00-\x08\x0b-\x1f]/g,'')){if(part&&font.widthOfTextAtSize(part+c,size)>max){if(/[，。；：！？、）》】〕〉”’]/.test(c)&&Array.from(part).length>1){const characters=Array.from(part),last=characters.pop();lines.push(characters.join(''));part=last}else{lines.push(part);part=''}}part+=c}lines.push(part)}return lines;};
 const write=(text,{size=11,bold=false,indent=22,before=0,after=5}={})=>{y-=before;for(const raw of String(text).split('\n')){let first=true;for(const line of wrap(raw,size,right-left-indent)){if(y-15<bottom)newPage();textAt(line,left+(first?indent:0),y-size,size,bold);y-=15;first=false;}}y-=after;};
 newPage();
 // The reference has a compact title table, not a separate cover page.
 const tableWidth=414.8,firstRow=62,top=y;
 const logoX=left+26,logoY=top-firstRow+9,logoWidth=153.55,logoHeight=50.4;
 // Use the exact crop rectangle from the reference title-table drawing.
 const fullWidth=logoWidth/(1-.06529-.10315),fullHeight=logoHeight/(1-.22588-.16522);
 page.pushOperators(pushGraphicsState(),rectangle(logoX,logoY,logoWidth,logoHeight),clip(),endPath());
 page.drawImage(logo,{x:logoX-.06529*fullWidth,y:logoY-.16522*fullHeight,width:fullWidth,height:fullHeight});page.pushOperators(popGraphicsState());
 const reportTitle='《自动控制实验》报告';textAt(reportTitle,left+205.55+(209.25-font.widthOfTextAtSize(reportTitle,18))/2,top-36,18);
 y=top-firstRow;const rule=()=>{page.drawLine({start:{x:left,y},end:{x:left+tableWidth,y},thickness:.5});page.drawLine({start:{x:left,y:y-1.5},end:{x:left+tableWidth,y:y-1.5},thickness:.35});};rule();y-=8;
 const names=['实验名称：',...wrap(d.title,12,305)],dates=['日期：',...wrap(d.date,12,99)];const rowHeight=Math.max(names.length,dates.length)*16+8;
 names.forEach((t,i)=>textAt(t,left+5,y-12-i*16,12,true));dates.forEach((t,i)=>textAt(t,left+320,y-12-i*16,12,true));y-=rowHeight;
 page.drawLine({start:{x:left,y},end:{x:left+tableWidth,y},thickness:.4});y-=6;
 const cells=[['学号：'+d.studentId,0,106.35],['姓名：'+d.name,106.35,106.3],['班级：'+d.className,212.65,202.15]];
 let identityHeight=0;for(const [value,offset,w] of cells){const lines=wrap(value,12,w-8);identityHeight=Math.max(identityHeight,lines.length*16);lines.forEach((t,i)=>textAt(t,left+offset+5,y-12-i*16,12,true));}
 y-=identityHeight+6;rule();y-=10;
 let chart=0;
 for(const section of reportSections(d)){
  if(y<bottom+55)newPage();
  write(section.heading,{bold:true,indent:0,before:8});write(section.text,{indent:section.appendix?0:22});
  if(section.run)for(const [label,values] of Object.entries(section.run.series)){
   if(y<bottom+200)newPage();chart++;write(`图 ${chart} ${label}`,{indent:0});
   const p=chartPoints(section.run,values,right-left,155),top=y;
   for(let i=1;i<p.points.length;i++)page.drawLine({start:{x:left+p.points[i-1][0],y:top-p.points[i-1][1]},end:{x:left+p.points[i][0],y:top-p.points[i][1]},thickness:1,color:rgb(.14,.4,.3)});
   y-=155;write(`t: ${section.run.time[0]} ~ ${section.run.time.at(-1)} s; min: ${p.lo.toPrecision(4)}; max: ${p.hi.toPrecision(4)}`,{size:9,indent:0});
  }
 }
 const pages=pdf.getPages();pages.forEach((p,i)=>p.drawText(`${i+1} / ${pages.length}`,{x:width/2-14,y:height-792.3,font,size:9}));
 return pdf.save();
}
