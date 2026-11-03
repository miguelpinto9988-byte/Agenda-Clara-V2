#!/usr/bin/env python3
"""Render four bespoke panel icons for Agenda Clara. Transparent, 2048px master,
256px Android variant, solid pigments with localized specular reflections.
The former four resources are physically deleted before replacement.
"""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFilter
S=2048
C={'purple':'#8D27F1','purple_light':'#BC6BFC','purple_dark':'#5318A9',
'blue':'#087EF1','blue_dark':'#0757BF','cyan':'#06CCEA','cyan_light':'#6FF5FF',
'teal':'#16DCC2','mint':'#8CFFE9','green':'#22D64F','green_dark':'#079834',
'yellow':'#FFCA19','orange':'#F89510','pink':'#FC439B','white':'#FFFFFF',
'paper':'#F5F4FF','ink':'#392476','lavender':'#B9A8F7'}
def box(d,xy,fill,r=40,stroke=None,sw=0):
    d.rounded_rectangle(tuple(int(x) for x in xy),radius=r,fill=fill,outline=stroke,width=sw)
def spec(d,xy,width=16):
    d.arc(xy,196,258,fill='#FFFFFF',width=width)
def base():
    # Render at 1024 and upscale to 2048: sharp enough to retain bezels.
    im=Image.new('RGBA',(1024,1024),(0,0,0,0))
    return im,ImageDraw.Draw(im)
def gloss(d,coords):
    for x,y,w,h in coords:d.ellipse((x,y,x+w,y+h),fill=(255,255,255,225))
def exam():
    im,d=base()
    box(d,(160,190,838,895),C['purple_dark'],90)
    box(d,(142,171,815,870),C['purple'],87,stroke=C['purple_light'],sw=16)
    box(d,(224,247,732,808),C['paper'],54,stroke=C['lavender'],sw=15)
    box(d,(320,142,633,240),C['cyan'],40,stroke=C['blue'],sw=13)
    for y in (365,500,635):
        box(d,(286,y,372,y+84),C['green'],23,stroke=C['green_dark'],sw=9)
        d.line((308,y+42,329,y+60,357,y+19),fill=C['white'],width=15,joint='curve')
        box(d,(410,y+16,660,y+34),C['lavender'],9)
        box(d,(410,y+51,578,y+69),C['lavender'],9)
    d.polygon(((541,211),(782,136),(951,276),(706,352)),fill=C['purple_dark'])
    d.polygon(((541,198),(781,119),(954,265),(709,334)),fill=C['purple'],stroke=C['purple_light'],width=12)
    box(d,(686,335,818,407),C['purple_dark'],24)
    d.line((885,280,899,421),fill=C['yellow'],width=22)
    d.ellipse((881,411,930,463),fill=C['yellow'])
    spec(d,(182,198,488,490),20);spec(d,(566,151,856,283),14)
    gloss(d,[(335,161,30,15),(297,265,39,17)])
    return im
def schedule():
    im,d=base()
    box(d,(150,161,844,878),C['purple_dark'],90)
    box(d,(135,145,823,850),C['purple'],89,stroke=C['purple_light'],sw=15)
    box(d,(157,355,810,838),C['paper'],75,stroke=C['lavender'],sw=14)
    box(d,(266,80,365,285),C['purple_light'],48,stroke=C['purple_dark'],sw=12)
    box(d,(600,80,699,285),C['purple_light'],48,stroke=C['purple_dark'],sw=12)
    for y in (430,563,695):
        for x in (238,372,506):box(d,(x,y,x+104,y+94),C['lavender'],24)
    box(d,(376,563,479,657),C['purple'],22)
    d.ellipse((484,487,969,961),fill=C['blue_dark'])
    d.ellipse((493,476,952,936),fill=C['cyan'],outline=C['blue'],width=20)
    d.ellipse((554,536,894,877),fill=C['paper'],outline=C['cyan_light'],width=12)
    d.line((724,707,724,616),fill=C['purple'],width=25)
    d.line((724,707,808,707),fill=C['purple'],width=25)
    d.ellipse((700,683,748,731),fill=C['purple_dark'])
    spec(d,(162,161,503,477),20);spec(d,(519,495,913,902),18)
    gloss(d,[(300,91,30,15),(650,90,34,17)])
    return im
def courses():
    im,d=base()
    # A stack of three rounded books with shaded hard edges
    for i,(x,y,color,edge) in enumerate([(156,666,C['teal'],C['blue_dark']),
                                        (181,505,C['blue'],C['blue_dark']),
                                        (167,348,C['purple'],C['purple_dark'])]):
        box(d,(x+21,y+27,x+718,y+151),edge,31)
        box(d,(x,y,x+702,y+137),color,30,stroke=edge,sw=11)
        box(d,(x+92,y+56,x+643,y+119),C['paper'],25)
        box(d,(x+153,y+68,x+627,y+103),'#D6D9FC',12)
        d.line((x+68,y+29,x+300,y+29),fill=C['white'],width=15)
    d.polygon(((267,302),(500,150),(790,295),(548,457)),fill=C['purple_dark'])
    d.polygon(((247,284),(490,127),(785,284),(540,439)),fill=C['purple'],stroke=C['purple_light'],width=13)
    box(d,(402,426,665,485),C['purple_dark'],28)
    d.line((726,292,766,453),fill=C['yellow'],width=22)
    d.ellipse((740,439,797,507),fill=C['orange'],outline=C['yellow'],width=9)
    spec(d,(290,180,580,392),19)
    return im
def myday():
    im,d=base()
    box(d,(146,155,865,880),C['blue_dark'],90)
    box(d,(127,134,840,856),C['cyan'],90,stroke=C['blue'],sw=16)
    box(d,(208,227,763,801),C['paper'],70,stroke=C['lavender'],sw=16)
    box(d,(299,105,641,228),C['teal'],45,stroke=C['blue'],sw=13)
    box(d,(286,277,696,391),C['mint'],34)
    d.ellipse((454,301,532,379),fill=C['yellow'])
    for dx,dy in [(0,-63),(0,62),(-92,0),(92,0),(-65,-47),(65,-47)]:
        d.line((493+dx,344+dy,493+dx+(10 if dx==0 else 0),344+dy+(10 if dy==0 else 0)),fill=C['orange'],width=14)
    for y in (431,550,669):
        box(d,(286,y,364,y+76),C['green'],22,stroke=C['green_dark'],sw=7)
        d.line((307,y+40,326,y+54,345,y+22),fill=C['white'],width=13)
        box(d,(405,y+16,649,y+36),C['lavender'],10)
    d.line((526,719,636,802,834,565),fill=C['green_dark'],width=95,joint='curve')
    d.line((526,703,636,787,834,550),fill=C['green'],width=74,joint='curve')
    d.line((543,697,630,767,816,553),fill=C['mint'],width=14,joint='curve')
    d.polygon(((841,420),(863,465),(909,488),(866,512),(841,563),(818,512),(772,488),(817,466)),fill=C['yellow'])
    spec(d,(157,158,518,481),18); gloss(d,[(314,125,39,15)])
    return im
ICONS={'ui_exam_review':exam,'ui_class_schedule':schedule,
       'ui_course_add':courses,'ui_my_guide':myday}
def run():
    project=Path('AgendaClara/app/src/main')
    res=project/'res/drawable-nodpi'
    if not res.exists():raise RuntimeError('Build original 500-icon Android library first')
    out=Path('icon_library_500/panel_fhd_2048');out.mkdir(parents=True,exist_ok=True)
    report={}
    for key,fn in ICONS.items():
        master=fn().resize((S,S),Image.Resampling.LANCZOS)
        mobile=master.resize((256,256),Image.Resampling.LANCZOS)
        source=out/f'ic_adapt_{key}.png'
        dest=res/f'ic_adapt_{key}.png'
        # Replace old file, never keep its earlier visual version.
        if dest.exists():dest.unlink()
        master.save(source,format='PNG',optimize=True)
        mobile.save(dest,format='PNG',optimize=True)
        with Image.open(source) as check:
            assert check.size==(2048,2048) and check.getpixel((0,0))[3]==0
        with Image.open(dest) as check:
            assert check.size==(256,256) and check.getpixel((0,0))[3]==0
        report[key]={'master':str(source),'android':str(dest),
                     'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    assert len({r['sha256'] for r in report.values()})==4
    assets=project/'assets/adaptive_icon_catalog.json'
    if assets.exists():
        catalog=json.loads(assets.read_text(encoding='utf-8'))
        catalog['png_bytes']=sum(x.stat().st_size for x in res.glob('ic_adapt_*.png'))
        catalog['panel_reflection_icons']={k:dict(master_resolution=[2048,2048],
          mobile_resolution=[256,256],background='RGBA transparent',source='Agenda Clara vector original')
          for k in ICONS}
        assets.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    Path('icon_library_500/PANEL-ICON-REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: 4 panel icons replaced; 2048 master + 256 Android; transparent')
if __name__=='__main__':run()
