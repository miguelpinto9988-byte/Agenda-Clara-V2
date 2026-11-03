#!/usr/bin/env python3
"""Agenda Clara: build 328 distinct local PNG illustrations from licensed Microsoft Fluent Emoji 3D artwork.
Source: https://github.com/microsoft/fluentui-emoji (MIT); license bundled. No runtime emoji or network requests.
"""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw,ImageFont
from concurrent.futures import ThreadPoolExecutor
import urllib.request,urllib.parse,json,ast,hashlib,re,io,zipfile,sys

REPO='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/'
GROUPS={
'math':'Abacus|Input numbers|Triangular ruler|Straight ruler|Chart increasing|Bar chart|Plus|Minus',
'flask':'Test tube|Alembic|Petri dish|Microscope|Dna|Microbe',
'atom':'Atom symbol|Magnet|Telescope|Satellite|Electric plug|High voltage',
'leaf':'Seedling|Potted plant|Leaf fluttering in wind|Evergreen tree|Herb|Dna|Microbe',
'book':'Books|Open book|Blue book|Green book|Orange book|Closed book|Notebook|Spiral notepad|Scroll',
'scroll':'Classical building|Scroll|Amphora|Globe showing europe-africa|Books',
'globe':'Globe showing americas|Globe showing europe-africa|Globe with meridians|World map|Compass|Mount fuji',
'chat':'Speech balloon|Input latin letters|Open book|Books|Thought balloon',
'laptop':'Laptop|Desktop computer|Keyboard|Computer mouse|Gear|Robot|Computer disk',
'palette':'Artist palette|Paintbrush|Crayon|Framed picture|Performing arts|Camera',
'music':'Musical notes|Musical note|Musical keyboard|Violin|Guitar|Drum|Microphone',
'brain':'Brain|Thought balloon|Light bulb|Open book|Puzzle piece',
'scales':'Balance scale|Classical building|Scroll|Handshake|Books',
'chart':'Chart increasing|Bar chart|Money bag|Credit card|Receipt|Office building',
'heart':'Stethoscope|Hospital|Medical symbol|Anatomical heart|Adhesive bandage',
'grad':'Graduation cap|School|Books|Backpack|Memo|Pencil|Open book',
'gear':'Gear|Robot|Factory|Electric plug|Nut and bolt',
'scope':'Microscope|Magnifying glass tilted left|Telescope|Dna|Test tube',
'ball':'Soccer ball|Basketball|Volleyball|Tennis|Running shoe|Trophy',
'clock':'Calendar|Spiral calendar|Tear-off calendar|Alarm clock|Stopwatch',
'pencil':'Memo|Pencil|Spiral notepad|Clipboard|Page facing up|Notebook|Pen',
'star':'Glowing star|Bell|Trophy|Bullseye|Sparkles|Star',
'tools':'Gear|Building construction|Factory|Electric plug',
'camera':'Camera|Camera with flash|Video camera|Movie camera|Framed picture',
'plant':'Potted plant|Seedling|Evergreen tree|Deciduous tree|Sunflower',
'food':'Cooking|Pot of food|Bread|Cake|Green apple',
'general':'Books|Clipboard|Bookmark tabs|File folder|Open book|Light bulb'
}
EXACT={
'matematicas':'Abacus','algebra':'Input numbers','geometria':'Triangular ruler','estadistica':'Bar chart',
'quimica':'Test tube','quimica_organica':'Alembic','bioquimica':'Dna',
'fisica':'Atom symbol','astronomia':'Telescope','electricidad':'Electric plug','electromagnetismo':'Magnet',
'biologia':'Seedling','botanica':'Potted plant','microbiologia':'Microbe','genetica':'Dna',
'historia':'Classical building','historia_del_peru':'Scroll','arqueologia':'Amphora',
'geografia':'Globe showing americas','geologia':'Rock','cartografia':'World map',
'literatura':'Books','lectura':'Open book','novela':'Green book','poesia':'Orange book','cuentos':'Closed book',
'ingles':'Input latin letters','frances':'Input latin letters','idiomas':'Speech balloon',
'informatica':'Laptop','programacion':'Laptop','hardware':'Computer mouse','desarrollo_web':'Desktop computer',
'arte':'Artist palette','pintura':'Artist palette','dibujo':'Crayon','fotografia':'Camera','teatro':'Performing arts',
'musica':'Musical notes','piano':'Musical keyboard','guitarra':'Guitar','coro':'Microphone',
'psicologia':'Brain','neurociencia':'Brain','filosofia':'Light bulb','derecho':'Balance scale',
'economia':'Chart increasing','contabilidad':'Bar chart','finanzas':'Money bag','marketing':'Megaphone',
'medicina':'Stethoscope','salud':'Anatomical heart','odontologia':'Tooth','enfermeria':'Medical symbol',
'educacion':'Graduation cap','aula':'School','pedagogia':'Books',
'ingenieria':'Gear','robotica':'Robot','industriales':'Factory',
'investigacion':'Microscope','experimentos':'Test tube','tesis':'Books',
'deporte':'Soccer ball','futbol':'Soccer ball','baloncesto':'Basketball','voleibol':'Volleyball',
'calendario':'Spiral calendar','horario':'Calendar','agenda':'Spiral calendar','alarma':'Alarm clock','recordatorio':'Bell',
'examen':'Memo','parcial':'Memo','final':'Graduation cap','practica':'Pencil','tarea':'Clipboard','notas':'Spiral notepad',
'silabo':'Page facing up','pdf':'Page facing up','presentacion':'Speech balloon','proyecto':'Rocket',
'general':'Books','sin_categoria':'Bookmark tabs','curso_desconocido':'Open book'
}
def get(url,parse=False):
    r=urllib.request.Request(url,headers={'User-Agent':'AgendaClara-AssetBuild/1.0'})
    with urllib.request.urlopen(r,timeout=45) as f:data=f.read()
    return json.loads(data) if parse else data
def categories():
    tree=ast.parse(Path('updates/phase51/generate_icons.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='DATA' for x in node.targets):
            a=ast.literal_eval(node.value)
            return {key:group for group,names in a.items() for key in names.split()}
    raise RuntimeError('Missing category registry')
def chosen(key,group,names):
    exact=EXACT.get(key,'').lower()
    if exact in names:return exact
    choices=[x.lower() for x in GROUPS.get(group,GROUPS['general']).split('|') if x.lower() in names]
    if not choices:raise RuntimeError('No artwork for '+key)
    h=int(hashlib.sha256(key.encode()).hexdigest()[:10],16)
    return choices[h%len(choices)]
def pict(im):
    im=im.convert('RGBA');box=im.getchannel('A').getbbox()
    if not box:raise RuntimeError('Blank illustration')
    im=im.crop(box);im.thumbnail((226,226),Image.Resampling.LANCZOS)
    out=Image.new('RGBA',(256,256))
    x=(256-im.width)//2;y=(256-im.height)//2-3
    shadow=Image.new('RGBA',(256,256));shadow.paste(im,(x,y+5))
    alpha=shadow.getchannel('A').filter(ImageFilter.GaussianBlur(4)).point(lambda v:int(v*.11))
    shadow=Image.new('RGBA',(256,256),(20,23,48));shadow.putalpha(alpha)
    out.alpha_composite(shadow);out.alpha_composite(im,(x,y))
    return out
def encoded(im,colors):
    p=im.quantize(colors=colors,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE)
    buf=io.BytesIO();p.save(buf,format='PNG',optimize=True,compress_level=9)
    return buf.getvalue()
def gallery(dest,keys,file):
    cols=8;w=180;h=181;rows=(len(keys)+7)//8
    board=Image.new('RGB',(cols*w,rows*h+74),'#F5F4FA');d=ImageDraw.Draw(board)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    d.text((24,18),'AGENDA CLARA · ICONOS PNG REALES',font=ImageFont.truetype(font,21),fill='#2C204C')
    d.text((24,48),'Muestra desde los archivos guardados, no una maqueta',font=ImageFont.truetype(font,13),fill='#6D6187')
    small=ImageFont.truetype(font,13)
    for i,k in enumerate(keys):
        x=(i%cols)*w;y=(i//cols)*h+74
        d.rounded_rectangle((x+5,y+4,x+w-5,y+h-4),16,fill='white',outline='#E2DFEB')
        im=Image.open(dest/f'ic_adapt_{k}.png').convert('RGBA')
        im.thumbnail((134,134));board.paste(im,(x+(w-im.width)//2,y+5),im)
        name=k.replace('_',' ');name=name[:21]+('…' if len(name)>21 else '')
        d.text((x+11,y+143),name,font=small,fill='#30284A')
    board.save(file,optimize=True)
def main():
    dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path('AgendaClara/app/src/main/res/drawable-nodpi')
    out=Path(sys.argv[2]) if len(sys.argv)>2 else Path('icon_pro_artifacts')
    out.mkdir(parents=True,exist_ok=True)
    keys=sorted(p.stem.replace('ic_adapt_','') for p in dest.glob('ic_adapt_*.png'))
    if len(keys)!=328 or len(set(keys))!=328:raise RuntimeError('Expected 328 original resource names')
    tree=get('https://api.github.com/repos/microsoft/fluentui-emoji/git/trees/main?recursive=1',True)
    if tree.get('truncated'):raise RuntimeError('Fluent Emoji tree truncated')
    sources={}
    for e in tree['tree']:
        m=re.fullmatch(r'assets/([^/]+)/3D/[^/]+_3d\.png',e['path'])
        if m:sources[m[1].lower()]=e['path']
    if len(sources)<1000:raise RuntimeError('Missing official 3D resources')
    groups=categories()
    selection={k:chosen(k,groups.get(k,'general'),sources) for k in keys}
    needed=set(selection.values())
    def load(name):
        u=REPO+urllib.parse.quote(sources[name],safe='/')
        b=get(u)
        if not b.startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('Bad remote image '+name)
        img=Image.open(io.BytesIO(b));img.load()
        return name,img.convert('RGBA')
    with ThreadPoolExecutor(max_workers=10) as pool:
        artwork=dict(pool.map(load,sorted(needed)))
    icons={k:pict(artwork[selection[k]]) for k in keys}
    # If two subjects use the same drawing, compose a related secondary subject symbol,
    # never a generic colored background plate.
    by_asset={}
    for key,art in selection.items():by_asset.setdefault(art,[]).append(key)
    for art,aliases in by_asset.items():
        for j,key in enumerate(sorted(aliases)):
            if j==0:continue
            group=groups.get(key,'general')
            options=[v.lower() for v in GROUPS.get(group,GROUPS['general']).split('|') if v.lower() in artwork and v.lower()!=art]
            if not options:continue
            symbol=artwork[options[j%len(options)]].copy()
            symbol=symbol.crop(symbol.getchannel('A').getbbox())
            symbol.thumbnail((64+(j%3)*10,64+(j%3)*10),Image.Resampling.LANCZOS)
            icons[key].alpha_composite(symbol,(256-symbol.width-4,256-symbol.height-4))
    # Ensure every semantic key has its own PNG; enhance only truly repeated illustrations.
    seen={}
    for key in sorted(keys):
        art_digest=hashlib.sha256(icons[key].tobytes()).hexdigest()
        if art_digest in seen:
            group=groups.get(key,'general')
            variants=[v.lower() for v in GROUPS.get(group,GROUPS['general']).split('|')
                      if v.lower() in artwork and v.lower()!=selection[key]]
            if not variants:variants=[v for v in sorted(artwork) if v!=selection[key]]
            extra=artwork[variants[int(hashlib.sha256(key.encode()).hexdigest()[-6:],16)%len(variants)]].copy()
            box=extra.getchannel('A').getbbox()
            extra=extra.crop(box)
            side=65+(int(hashlib.sha256(key.encode()).hexdigest()[:2],16)%3)*8
            extra.thumbnail((side,side),Image.Resampling.LANCZOS)
            xx=4+(int(hashlib.sha256(key.encode()).hexdigest()[2:4],16)%11)
            icons[key].alpha_composite(extra,(xx,256-extra.height-5))
        seen[hashlib.sha256(icons[key].tobytes()).hexdigest()]=key
    for colors in (200,160,128,96):
        raw={k:encoded(v,colors) for k,v in icons.items()}
        total=sum(len(v) for v in raw.values())
        print('Palette',colors,'total image size',total,flush=True)
        if total<=15_000_000:break
    else:raise RuntimeError('Iconography larger than authorized 15 MB')
    for k,b in raw.items():(dest/f'ic_adapt_{k}.png').write_bytes(b)
    lic=get(REPO+'LICENSE').decode('utf-8')
    if 'MIT License' not in lic:raise RuntimeError('License missing')
    (out/'LICENSE-MIT.txt').write_text(lic,encoding='utf8')
    metadata={'count':len(keys),'format':'PNG','dimensions':[256,256],'transparent':True,'style':'colored 3D illustration; no uniform chrome or backplate','source':'Microsoft Fluent Emoji 3D','license':'MIT','distinct_base_drawings':len(artwork),'png_bytes':total,'palette_colors':colors,
      'icons':[{'key':k,'filename':f'ic_adapt_{k}.png','asset':sources[selection[k]],'sha256':hashlib.sha256(raw[k]).hexdigest(),'bytes':len(raw[k])} for k in keys]}
    (out/'MANIFEST.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf8')
    first=['matematicas','quimica','fisica','biologia','historia','literatura','geografia','ingles','informatica','arte','musica','educacion','psicologia','economia','derecho','medicina','ingenieria','investigacion','deporte','tarea','examen','notas','horario','recordatorio','calendario','proyecto','practica','parcial','final','silabo','social_studies','botanica','programacion','piano','fotografia','odontologia','novela','ciencias_sociales']
    gallery(dest,[x for x in first if x in keys],out/'MUESTRA-REAL-ICONOS.png')
    for i in range(0,len(keys),64):gallery(dest,keys[i:i+64],out/f'CATALOGO-{i//64+1:02d}.png')
    pack=out/'Agenda-Clara-328-Iconos-Pro.zip'
    with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for key in keys:z.write(dest/f'ic_adapt_{key}.png',f'res/drawable-nodpi/ic_adapt_{key}.png')
        for sample in out.glob('*.png'):z.write(sample,'muestras/'+sample.name)
        z.write(out/'LICENSE-MIT.txt','LICENSE-MIT.txt')
        z.write(out/'MANIFEST.json','MANIFEST.json')
    print('PASS 328 PNG 256x256, real images',len(artwork),'source drawings',total,'bytes',flush=True)
if __name__=='__main__':main()
