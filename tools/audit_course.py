"""Read course handouts and original SLX topology without modifying originals."""
from pathlib import Path
import json,re,zipfile,xml.etree.ElementTree as ET
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'runtime'/'course-audit';DEST.mkdir(parents=True,exist_ok=True)

def extract():
    all_models=[]
    for lab in range(1,7):
        source=ROOT/'sources'/f'lab{lab}'
        pdfs=[p for p in source.glob('*.pdf') if '杨开元' not in p.name]
        parts=[]
        if pdfs:
            pdf=pdfs[0];doc=fitz.open(pdf)
            for i,page in enumerate(doc):parts.append(f'\n--- 第 {i+1} 页 ---\n'+page.get_text(sort=True))
        else:
            ppt=next(source.glob('*.pptx'))
            with zipfile.ZipFile(ppt) as z:
                for name in sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+.xml$',n)],key=lambda n:int(re.search(r'slide(\d+)',n).group(1))):
                    tree=ET.fromstring(z.read(name));parts.append('\n--- 第 '+re.search(r'slide(\d+)',name).group(1)+' 页 ---\n'+'\n'.join(n.text or '' for n in tree.iter() if n.tag.endswith('}t')))
        (DEST/f'lab{lab}.txt').write_text(''.join(parts),encoding='utf-8')
        for model in source.glob('*.slx'):
            systems=[]
            with zipfile.ZipFile(model) as z:
                for name in z.namelist():
                    if not name.startswith('simulink/systems/') or not name.endswith('.xml'):continue
                    tree=ET.fromstring(z.read(name));blocks=[]
                    for b in tree.iter('Block'):
                        params={p.attrib['Name']:p.text for p in b.findall('P') if p.attrib.get('Name') not in ('ScopeSpecificationString','Position','ZOrder')}
                        blocks.append(dict(name=b.attrib.get('Name'),type=b.attrib.get('BlockType'),sid=b.attrib.get('SID'),parameters=params))
                    lines=[ET.tostring(line,encoding='unicode') for line in tree.iter('Line')]
                    systems.append(dict(path=name,blocks=blocks,lines=lines))
                all_models.append(dict(lab=lab,path=model.relative_to(ROOT).as_posix(),systems=systems))
    (DEST/'original-models.json').write_text(json.dumps(all_models,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Read six handouts and',len(all_models),'original models')

if __name__=='__main__':extract()
