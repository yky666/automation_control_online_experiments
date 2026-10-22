"""Derive an anonymous reusable school template from a private reference DOCX.

The source stays outside the repository. Only its page furniture, styles, and
an empty title table are retained. No experiment prose or student data is copied.
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'w':W}
def xml(root):return E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
def fill(cell,text):
 p=cell.find('w:p',NS);pr=deepcopy(p.find('w:pPr',NS));run=p.find('w:r',NS)
 rp=deepcopy(run.find('w:rPr',NS)) if run is not None else None
 for child in list(cell):
  if child.tag!=f'{{{W}}}tcPr':cell.remove(child)
 for line in text.split('\n'):
  p=E.SubElement(cell,f'{{{W}}}p')
  if pr is not None:p.append(deepcopy(pr))
  r=E.SubElement(p,f'{{{W}}}r')
  if rp is not None:r.append(deepcopy(rp))
  E.SubElement(r,f'{{{W}}}t').text=line

def main():
 parser=argparse.ArgumentParser();parser.add_argument('source');parser.add_argument('--out',default='assets/reports');args=parser.parse_args()
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 with ZipFile(args.source) as source:
  root=E.fromstring(source.read('word/document.xml'));body=root.find('w:body',NS);tbl=deepcopy(body.find('w:tbl',NS));rows=tbl.findall('w:tr',NS)
  fill(rows[0].findall('w:tc',NS)[1],'《自动控制实验》报告')
  for cell,text in zip(rows[1].findall('w:tc',NS),['实验名称：\n{{experimentName}}','日期：\n{{date}}']):fill(cell,text)
  for cell,text in zip(rows[2].findall('w:tc',NS),['学号：{{studentId}}','姓名：{{name}}','班级：{{className}}','']):fill(cell,text)
  patterns={}
  for role,index in [('heading',1),('body',2),('subheading',14),('caption',21)]:
   para=list(body)[index]
   patterns[role]={'pPr':E.tostring(para.find('w:pPr',NS),encoding='unicode'),'rPr':E.tostring(para.find('w:r/w:rPr',NS),encoding='unicode')}
  drawing=body.xpath('.//w:drawing',namespaces=NS)[1]
  for node in drawing.iter():
   for attr in ['descr','title','name']:
    if attr in node.attrib:node.set(attr,'实验运行曲线')
  patterns['drawing']=E.tostring(drawing,encoding='unicode')
  (out/'sysu-report-patterns.json').write_text(json.dumps(patterns,ensure_ascii=False,indent=2))
  sect=deepcopy(body.find('w:sectPr',NS));body.clear();body.append(tbl)
  p=E.SubElement(body,f'{{{W}}}p');r=E.SubElement(p,f'{{{W}}}r');E.SubElement(r,f'{{{W}}}t').text='{{REPORT_BODY}}';body.append(sect)
  relroot=E.fromstring(source.read('word/_rels/document.xml.rels'))
  keep={'word/document.xml','word/styles.xml','word/numbering.xml','word/settings.xml','word/fontTable.xml','word/theme/theme1.xml','word/media/image1.png','word/media/image2.jpeg'}
  for rel in list(relroot):
   target=rel.get('Target','');part='word/'+target;kind=rel.get('Type','').rsplit('/',1)[-1]
   if kind in ['header','footer']:
    keep.add(part);rels='word/_rels/'+target+'.rels'
    if rels in source.namelist():keep.add(rels)
   elif part not in keep:relroot.remove(rel)
  data={f:source.read(f) for f in keep if f in source.namelist()};data['word/document.xml']=xml(root);data['word/_rels/document.xml.rels']=xml(relroot)
  settings=E.fromstring(data['word/settings.xml'])
  for child in list(settings):
   if E.QName(child).localname in ['rsids','docVars','attachedTemplate','mailMerge','saveThroughXslt']:settings.remove(child)
  update=settings.find('w:updateFields',NS)
  if update is None:update=E.SubElement(settings,f'{{{W}}}updateFields')
  update.set(f'{{{W}}}val','true');data['word/settings.xml']=xml(settings)
  # Cached page counts must not carry the private source's page count.
  for f in data:
   if f.startswith('word/footer') and f.endswith('.xml'):
    foot=E.fromstring(data[f])
    for t in foot.findall('.//w:t',NS):
     if t.text and t.text.strip().isdigit():t.text='1'
    data[f]=xml(foot)
  types=E.fromstring(source.read('[Content_Types].xml'))
  for item in list(types):
   if E.QName(item).localname=='Override' and item.get('PartName','').lstrip('/') not in data:types.remove(item)
  data['[Content_Types].xml']=xml(types)
  rootrels=E.Element(f'{{{R}}}Relationships',nsmap={None:R});E.SubElement(rootrels,f'{{{R}}}Relationship',Id='rId1',Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument',Target='word/document.xml');data['_rels/.rels']=xml(rootrels)
  with ZipFile(out/'sysu-lab-template.docx','w',ZIP_DEFLATED) as target:
   for f,b in sorted(data.items()):target.writestr(f,b)
  (out/'sysu-seal.png').write_bytes(data['word/media/image1.png']);(out/'sysu-wordmark.jpeg').write_bytes(data['word/media/image2.jpeg'])
 print('Anonymous template generated; original prose, figures, identity and metadata excluded.')
if __name__=='__main__':main()
