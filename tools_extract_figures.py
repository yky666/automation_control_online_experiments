"""Read-only PDF rendering of course schematic regions, no original file edits."""
from pathlib import Path
import fitz,json
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
pdf=next((ROOT/'sources'/'lab2').glob('*典型环节*.pdf'))
doc=fitz.open(pdf)
dest=ROOT/'sources'/'figures';dest.mkdir(exist_ok=True)
tiles=[]
for idx in [4,5,6,7,8,9]:
    page=doc[idx];pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5));img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    img.thumbnail((720,510));tile=Image.new('RGB',(740,540),'#eeeeee');tile.paste(img,((740-img.width)//2,23));ImageDraw.Draw(tile).text((12,6),'lab2 page '+str(idx+1),fill='black');tiles.append(tile)
sheet=Image.new('RGB',(1480,1620),'white')
for i,tile in enumerate(tiles):sheet.paste(tile,((i%2)*740,(i//2)*540))
sheet.save(dest/'contact.png')
print('Rendered contact sheet',dest/'contact.png')
diagrams={}
for lab_id,pattern,selections in [
    (2,'*典型环节*.pdf',[(4,'p'),(5,'inertia'),(6,'integrator'),(7,'d'),(8,'pi'),(9,'pd')]),
    (3,'*时域性能*.pdf',[(5,'all')]),
    (4,'*稳定性*.pdf',[(4,'all')]),
    (5,'*频率特性*.pdf',[(14,'bandwidth'),(19,'frequency_inertia'),(25,'frequency_second')]),
    (6,'*.pdf',[(8,'lead1'),(8,'lead2'),(8,'lead_example1'),(8,'lead_example2')]),
]:
    f=next((ROOT/'sources'/f'lab{lab_id}').glob(pattern));d=fitz.open(f)
    for page_index,task in selections:
        if page_index>=len(d):continue
        page=d[page_index];images=page.get_images(full=True)
        regions=[]
        for image in images:
            regions+=page.get_image_rects(image[0])
        regions=[r for r in regions if r.width>80 and r.height>60]
        if not regions:continue
        if lab_id==6:
            regions=sorted(regions,key=lambda r:r.x0)
            region=regions[-1] if task.endswith('2') else regions[0]
        else:region=max(regions,key=lambda r:r.width*r.height)
        region=fitz.Rect(max(0,region.x0-3),max(0,region.y0-3),min(page.rect.width,region.x1+3),min(page.rect.height,region.y1+3))
        name=f'lab{lab_id}-{task}.png';page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),clip=region).save(dest/name)
        diagrams[f'{lab_id}:{task}']={'url':'/sources/figures/'+name,'caption':'课程原理图（原始接线与符号，按实际模型核对）'}
(dest/'diagrams.json').write_text(json.dumps(diagrams,ensure_ascii=False,indent=2),encoding='utf-8')
print('Extracted',len(diagrams),'original course schematic regions')
