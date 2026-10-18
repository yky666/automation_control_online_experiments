from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'runtime'/'course-audit'
for lab,pages in [(2,[11,12,13,14,15,16,17,18,19,20,21,22]),(3,[23,25,26,27,28]),(4,[8,10,13,15,19,20,21]),(5,[15,16,20,21,26,27,28,29,30]),(6,[10,11,28,29,30,31,35])]:
    pdf=next(p for p in (ROOT/'sources'/f'lab{lab}').glob('*.pdf') if '杨开元' not in p.name);doc=fitz.open(pdf)
    for chunk in range(0,len(pages),4):
        canvas=Image.new('RGB',(2240,1340),'white')
        for j,p in enumerate(pages[chunk:chunk+4]):
            pix=doc[p-1].get_pixmap(matrix=fitz.Matrix(1.6,1.6));img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);img.thumbnail((1100,640));xy=((j%2)*1120,(j//2)*670);canvas.paste(img,(xy[0],xy[1]+25));ImageDraw.Draw(canvas).text((xy[0]+12,xy[1]+5),f'Lab {lab} / page {p}',fill='black')
        canvas.save(DEST/f'lab{lab}-pages-{chunk}.png')
print('Rendered relevant task pages')
