#!/usr/bin/env python3
"""Android 15 UI smoke: note/task modal re-expands when soft keyboard closes.
All edits are unsaved synthetic text; no tasks or notes are stored.
"""
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

PKG='pe.agendaclara.app'
OUT=Path('screenshots');OUT.mkdir(exist_ok=True)

def adb(*args,output=False):
    p=subprocess.run(['adb',*args],check=True,stdout=subprocess.PIPE if output else subprocess.DEVNULL)
    return p.stdout if output else b''

def hierarchy():
    adb('shell','uiautomator','dump','/sdcard/agenda_dialog.xml')
    return ET.fromstring(adb('exec-out','cat','/sdcard/agenda_dialog.xml',output=True).decode('utf-8','replace'))

def bounds(node):
    values=[int(x) for x in re.findall(r'\d+',node.get('bounds',''))]
    return values if len(values)==4 else None

def find_form(root,label):
    text=' '.join((n.get('text','')+' '+n.get('content-desc','')) for n in root.iter('node'))
    if label not in text:raise AssertionError(f'Dialog {label} missing')
    edits=[n for n in root.iter('node') if n.get('class','').endswith('EditText') and bounds(n)]
    if not edits:raise AssertionError(f'No editable field in dialog {label}')
    outer=next((n for n in root.iter('node') if bounds(n)),None)
    if outer is None:raise AssertionError('No bounds in UI hierarchy')
    return bounds(outer),bounds(edits[0])

def height(b):return b[3]-b[1]

def exercise(action,label,filename):
    adb('shell','am','force-stop',PKG)
    adb('shell','am','start','-W','-n',PKG+'/.MainActivity','-a',action)
    time.sleep(6)
    before,field=find_form(hierarchy(),label)
    adb('shell','input','tap',str((field[0]+field[2])//2),str((field[1]+field[3])//2))
    time.sleep(3)
    during,_=find_form(hierarchy(),label)
    adb('shell','input','keyevent','4')
    time.sleep(4)
    after,_=find_form(hierarchy(),label)
    (OUT/filename).write_bytes(adb('exec-out','screencap','-p',output=True))
    resized = height(during)<height(before)-40
    if resized:
        # Tall dialogs must recover their usable content height after hiding the IME.
        if height(after)<=height(during)+40:
            raise AssertionError(f'{label}: dialog remained keyboard-sized (during {during}, after {after})')
    else:
        # Short dialogs can already fit above the keyboard at their natural height.
        # Android moves them up, without shrinking their content, then re-centers them.
        if during[1]>=before[1]-40:
            raise AssertionError(f'{label}: dialog neither resized nor moved above keyboard: {before}/{during}')
        if abs(after[1]-before[1])>65:
            raise AssertionError(f'{label}: dialog did not return to original position: {before}/{after}')
    if height(after)<height(before)-65:
        raise AssertionError(f'{label}: original height not restored (before {before}, after {after})')
    print(f'PASS {label}: dialog before/during/after {height(before)}/{height(during)}/{height(after)}, mode={"resize" if resized else "recenter"}')

adb('shell','settings','put','secure','show_ime_with_hard_keyboard','1')
exercise('new_sticky_note','Crear nota','27-restauracion-teclado-nota.png')
exercise('new_task','Nueva tarea','28-restauracion-teclado-tarea.png')
