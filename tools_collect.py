"""Copy course originals; originals are never edited. Run from the project root."""
from pathlib import Path
import json, shutil, zipfile, xml.etree.ElementTree as ET
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
COURSE = ROOT.parent
DIRS = ['第一次','第二次','第三次','第四次','第五次','第六次']
manifest=[]
for i, folder in enumerate(DIRS,1):
    dest=ROOT/'sources'/f'lab{i}'
    dest.mkdir(parents=True,exist_ok=True)
    source=COURSE/folder
    inputs=list(source.glob('*.m'))+list(source.glob('*.slx'))
    if i==1: inputs+=list((source/'code').glob('task*.m'))+list((source/'code').glob('*.slx'))
    inputs += [f for f in source.glob('实验*.pdf') if '思考题' not in f.name]
    inputs += list(source.glob('实验*.pptx'))
    if i==1: inputs += list(source.glob('24345063-杨开元-实验一报告-LaTeX版.pdf'))
    files=[]
    texts=[]
    for f in inputs:
        shutil.copy2(f,dest/f.name)
        files.append({'name':f.name,'url':f'/sources/lab{i}/{f.name}','type':f.suffix[1:]})
        if f.suffix=='.pdf':
            try: texts.append(f.name+'\n'+'\n'.join(p.extract_text() or '' for p in PdfReader(f).pages))
            except Exception as e: print(f.name,type(e).__name__)
        elif f.suffix=='.pptx':
            with zipfile.ZipFile(f) as z:
                for name in sorted((n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')),key=lambda s:int(s.split('slide')[-1].split('.')[0])):
                    tree=ET.fromstring(z.read(name))
                    texts.append('\n'.join(n.text or '' for n in tree.iter() if n.tag.endswith('}t')))
    (ROOT/'sources'/f'lab{i}.txt').write_text('\n\n'.join(texts),encoding='utf-8',errors='replace')
    manifest.append({'id':i,'files':files})
(ROOT/'sources'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Collected',sum(len(x['files']) for x in manifest),'course originals.')
