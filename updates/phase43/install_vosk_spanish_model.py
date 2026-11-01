#!/usr/bin/env python3
"""Pin the freely redistributable Apache-2.0 Vosk Spanish small model for offline STT."""
from pathlib import Path
import hashlib,io,urllib.request,zipfile
URLS=[
 'https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip',
 'https://github.com/BartekReterski/VoskModels/releases/download/v1/vosk-model-small-es-0.42.zip'
]
EXPECTED='09b239888f633ef2f0b4e09736e3d9936acfd810bc65d53fad45261762c6511f'
OUT=Path('AgendaClara/app/src/main/assets/vosk_es')
if OUT.exists():raise RuntimeError('Refusing to overwrite existing Spanish model')
model=None
for url in URLS:
    try:
        print('Downloading Vosk model from',url,flush=True)
        request=urllib.request.Request(url,headers={'User-Agent':'AgendaClara-Vosk-Installer/1.0'})
        with urllib.request.urlopen(request,timeout=90) as response:
            data=response.read(50_000_000)
        sha=hashlib.sha256(data).hexdigest()
        if sha!=EXPECTED:raise RuntimeError('Checksum mismatch: '+sha)
        model=data;break
    except Exception as e:
        print('Unavailable:',type(e).__name__,str(e)[:130],flush=True)
if model is None:raise RuntimeError('No verified Apache-2.0 Spanish model source available')
OUT.mkdir(parents=True)
with zipfile.ZipFile(io.BytesIO(model)) as archive:
    for entry in archive.infolist():
        parts=Path(entry.filename).parts
        if entry.is_dir() or len(parts)<2:continue
        relative=Path(*parts[1:])
        if relative.is_absolute() or '..' in relative.parts:raise RuntimeError('Unsafe ZIP path')
        dest=OUT/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(archive.read(entry))
(OUT/'uuid').write_text('AgendaClara-vosk-model-small-es-0.42-sha256-'+EXPECTED+'\n')
assert (OUT/'am'/'final.mdl').is_file() and (OUT/'conf'/'model.conf').is_file()
print('PASS: offline Spanish Vosk model bundled with verified checksum')
