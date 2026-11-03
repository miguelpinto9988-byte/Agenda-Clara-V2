#!/usr/bin/env python3
"""Generate exactly 500 offline PNGs: 328 existing themes + 172 UI actions.
Solid varied pigments, specular white reflections, true transparency.
Runs after existing phase 52 so historical signed sources are untouched.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
import argparse, hashlib, io, json, urllib.parse, urllib.request, zipfile

GROUPS = [
 ('general','home dashboard quick_actions main_menu bottom_navigation overview welcome activity_feed quick_create favorites help_center'),
 ('educacion','my_guide study_plan study_session study_progress focus_mode study_timer pomodoro study_goal daily_review weekly_review learning_materials'),
 ('tarea','new_task edit_task delete_task complete_task reopen_task task_priority task_due task_filter task_search task_repeat task_archive'),
 ('notas','new_note edit_note delete_note pin_note note_color note_category sticky_note notes_gallery notes_search notes_archive notes_share'),
 ('calendario','calendar_month calendar_week calendar_day calendar_today calendar_add calendar_event calendar_reminder calendar_schedule calendar_export calendar_import calendar_sync'),
 ('oralidad','voice_mic voice_record voice_waveform voice_listen voice_recognize voice_stop voice_pause voice_replay voice_review voice_command voice_language'),
 ('recordatorio','notify_all notify_urgent notify_snooze notify_mark_read notify_settings notify_calendar notify_tasks notify_exams notify_class notify_quiet_mode notify_test'),
 ('comunicacion','whatsapp_link whatsapp_connect whatsapp_disconnect whatsapp_scan whatsapp_sync whatsapp_import whatsapp_message whatsapp_group whatsapp_history whatsapp_filter whatsapp_privacy'),
 ('investigacion','search_global search_courses search_tasks search_notes search_events search_files search_filters search_recent search_results search_clear search_suggestions'),
 ('documentos','pdf_import pdf_export document_scan document_ocr document_review document_edit document_download document_upload document_folder document_preview file_attach'),
 ('agenda','widget_tasks widget_notes widget_calendar widget_voice widget_edit widget_add widget_settings widget_resize widget_refresh widget_float widget_pin'),
 ('derecho','privacy_policy privacy_permission privacy_local privacy_lock privacy_unlock data_consent encrypted_backup secure_restore account_security session_expired device_access'),
 ('informatica','app_settings theme_light theme_dark text_size high_contrast reduced_motion notifications_settings storage_status network_status language_settings'),
 ('carpeta','backup_create backup_restore data_export data_import data_sync data_cleanup data_history trash_restore trash_permanent data_storage'),
 ('general','action_add action_edit action_delete action_save action_cancel action_done action_retry action_share action_copy action_paste'),
 ('planificacion','class_schedule class_today class_week course_edit course_add course_remove exam_schedule exam_add exam_review exam_results'),
]
ADDITIONS=[('ui_'+name,anchor) for anchor,labels in GROUPS for name in labels.split()]
assert len(ADDITIONS)==172 and len({k for k,_ in ADDITIONS})==172
REMOTE='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/'

def retrieve(source):
    url=REMOTE+urllib.parse.quote(source,safe='/')
    req=urllib.request.Request(url,headers={'User-Agent':'AgendaClara/IconQA-500'})
    with urllib.request.urlopen(req,timeout=45) as f: blob=f.read()
    if not blob.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Invalid source PNG '+source)
    with Image.open(io.BytesIO(blob)) as im:return source,im.convert('RGBA').copy()

def crop_fit(image,size,ratio):
    bbox=image.getchannel('A').getbbox()
    if not bbox:raise ValueError('Empty source illustration')
    output=image.crop(bbox)
    limit=int(size*ratio)
    output.thumbnail((limit,limit),Image.Resampling.LANCZOS)
    return output

def flat_colors(image):
    palette=image.quantize(colors=64,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE)
    solid=palette.convert('RGBA')
    solid.putalpha(image.getchannel('A'))
    return solid

def draw_icon(primary,secondary,size,extra,key):
    seed=hashlib.sha256(key.encode('utf8')).digest()
    canvas=Image.new('RGBA',(size,size),(0,0,0,0))
    base=crop_fit(primary,size,.75 if extra else .81)
    canvas.alpha_composite(base,((size-base.width)//2,(size-base.height)//2-5*size//256))
    if extra:
        badge=crop_fit(secondary,size,.34)
        x=size-badge.width-int(size*(.053+.002*(seed[0]%14)))
        y=size-badge.height-int(size*(.053+.002*(seed[1]%14)))
        shadow=Image.new('RGBA',(size,size),(0,0,0,0))
        shade=Image.new('RGBA',badge.size,(23,28,65,48))
        shade.putalpha(badge.getchannel('A').point(lambda a:int(a*.26)))
        shadow.alpha_composite(shade,(max(0,x-int(size*.005)),min(size-badge.height,y+int(size*.009))))
        canvas.alpha_composite(shadow)
        canvas.alpha_composite(badge,(x,y))
    canvas=flat_colors(canvas)
    bbox=canvas.getchannel('A').getbbox()
    if bbox:
        l,t,r,b=bbox;w=r-l;h=b-t
        gloss=Image.new('RGBA',(size,size),(0,0,0,0));d=ImageDraw.Draw(gloss)
        box=(l+int(.13*w),t+int(.12*h),l+int(.56*w),t+int(.45*h))
        width=max(2,int(size*.014))
        d.arc(box,187+(seed[2]%21),250+(seed[3]%23),fill=(255,255,255,210),width=width)
        dot=(l+int(.57*w),t+int(.12*h),l+int(.62*w),t+int(.17*h))
        d.ellipse(dot,fill=(255,255,255,166))
        cx=l+int(w*(.39+(seed[4]%18)*.012))
        cy=t+int(h*(.42+(seed[5]%20)*.011))
        rad=max(2,int(size*(.006+(seed[6]%5)*.001)))
        d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),fill=(255,255,255,90+(seed[7]%100)))
        gloss.putalpha(ImageChops.multiply(gloss.getchannel('A'),canvas.getchannel('A')))
        canvas.alpha_composite(gloss)
    assert canvas.getpixel((0,0))[3]==0
    return canvas

def load_registry(project):
    assets=project/'app/src/main/assets'
    res=project/'app/src/main/res/drawable-nodpi'
    origin=json.loads((assets/'adaptive_icon_sources.json').read_text(encoding='utf8'))
    old={entry['key']:entry for entry in origin['icons']}
    if len(old)!=328:raise ValueError('Expected exactly 328 prior sources')
    if set(old)&{k for k,_ in ADDITIONS}:raise ValueError('UI icon collision')
    return assets,res,old

def build(project,output,mode):
    assets,res,old=load_registry(project);res.mkdir(parents=True,exist_ok=True)
    base_sources={key:entry['asset'] for key,entry in old.items()}
    anchors={anchor:base_sources[anchor] for _,anchor in ADDITIONS}
    ordered=sorted(list(base_sources)+[key for key,_ in ADDITIONS])
    by_key={key:anchor for key,anchor in ADDITIONS}
    candidate=sorted(set(base_sources.values()))
    repeats=Counter(base_sources.values())
    selected={}
    for key in ordered:
        if key in base_sources:
            main=base_sources[key]
            if repeats[main]>1:
                i=int(hashlib.sha256(key.encode('utf8')).hexdigest()[:12],16)%len(candidate)
                secondary=candidate[i]
                if secondary==main:secondary=candidate[(i+1)%len(candidate)]
                selected[key]=(main,secondary)
            else:selected[key]=(main,None)
        else:
            main=anchors[by_key[key]]
            i=int(hashlib.sha256(key.encode('utf8')).hexdigest()[:12],16)%len(candidate)
            secondary=candidate[i]
            if secondary==main:secondary=candidate[(i+1)%len(candidate)]
            selected[key]=(main,secondary)
    wanted=sorted({name for pair in selected.values() for name in pair if name})
    with ThreadPoolExecutor(max_workers=12) as pool:drawings=dict(pool.map(retrieve,wanted))
    size=2048 if mode=='fullhd' else 256
    destination=output/'FULLHD-2048' if mode=='fullhd' else res
    destination.mkdir(parents=True,exist_ok=True)
    icons=[];png_bytes=0;hashes=set()
    for key in ordered:
        a,b=selected[key]
        picture=draw_icon(drawings[a],drawings[b] if b else drawings[a],size,bool(b),key)
        filename='ic_adapt_'+key+'.png';path=destination/filename
        picture.save(path,format='PNG',optimize=True,compress_level=9)
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        hashes.add(digest);png_bytes+=len(raw)
        icons.append({'key':key,'file':filename,'sha256':digest,'bytes':len(raw),'base':a,'secondary':b})
    if len(hashes)!=500:raise AssertionError(f'Only {len(hashes)} unique PNGs of 500')
    manifest={'count':500,'new_icons':172,'format':'PNG','dimensions':[size,size],
        'transparency':True,'style':'flat solid colors, vivid varied pigments, crisp 3D imagery, specular reflections, transparent background',
        'source':'Microsoft Fluent Emoji 3D (MIT), modified and composed',
        'license':'MIT','distinct_source_drawings':len(drawings),'png_bytes':png_bytes,'icons':icons}
    output.mkdir(parents=True,exist_ok=True)
    (output/f'MANIFEST-{size}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    if mode=='mobile':
        if png_bytes>15_000_000:raise AssertionError('Mobile resource budget exceeded: '+str(png_bytes))
        catalog=json.loads((assets/'adaptive_icon_catalog.json').read_text(encoding='utf8'))
        catalog.update(count=500,png_bytes=png_bytes,render_style=manifest['style'],
            source=manifest['source'],mobile_icon_resolution=[256,256],fullhd_library_resolution=[2048,2048])
        for key,anchor in ADDITIONS:
            catalog['icons'][key]={'family':'ui','file':'ic_adapt_'+key+'.png','anchor':anchor}
        (assets/'adaptive_icon_catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        java=project/'app/src/main/java/pe/agendaclara/app/AdaptiveIconIndex.java'
        lines=['package pe.agendaclara.app;','/** Generated index of 500 bundled transparent PNG resources. */',
               'final class AdaptiveIconIndex {',' private AdaptiveIconIndex(){}',' static final String[] KEYS = {']
        for i in range(0,len(ordered),10):lines.append('   '+','.join('"'+key+'"' for key in ordered[i:i+10])+',')
        java.write_text('\n'.join(lines+[' };','}'])+'\n',encoding='utf8')
    else:
        pack=output/'Agenda-Clara-500-Iconos-FullHD-2048.zip'
        with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
            for entry in icons:z.write(destination/entry['file'],'PNG-2048/'+entry['file'])
            z.write(output/'MANIFEST-2048.json','MANIFEST.json')
            license_file=assets/'licenses/microsoft-fluent-emoji-MIT.txt'
            if license_file.exists():z.write(license_file,'LICENSE-MIT.txt')
    print(f'PASS 500 PNG {size}x{size}: 172 additional UI icons; {len(hashes)} hashes; {png_bytes} bytes')

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--project',type=Path,default=Path('AgendaClara'))
    cli.add_argument('--output',type=Path,default=Path('icon_library_500'))
    cli.add_argument('--mode',choices=['mobile','fullhd'],required=True)
    args=cli.parse_args()
    build(args.project,args.output,args.mode)
