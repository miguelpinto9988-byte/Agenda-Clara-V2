#!/usr/bin/env python3
"""Pin the official Spanish fast OCR model at CI build-time; no external user documents."""
from pathlib import Path
import hashlib,urllib.request
url='https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/spa.traineddata'
EXPECTED_SIZE=2294433
EXPECTED_SHA512='901e8c0c6dc50f57c723922061d5a98b223f1b499b9af1546b072dd70772c5a3ffa33ddbc76295b115bd586863f3d653602bdb6d1fce28a59a86d296efa24241'
out=Path('AgendaClara/app/src/main/assets/tessdata/spa.traineddata')
out.parent.mkdir(parents=True,exist_ok=True)
req=urllib.request.Request(url,headers={'User-Agent':'AgendaClara-build/3.12.0 (official tessdata_fast)'})
with urllib.request.urlopen(req,timeout=80) as response:
    data=response.read(4_000_000)
if len(data)!=EXPECTED_SIZE or hashlib.sha512(data).hexdigest()!=EXPECTED_SHA512:
    raise RuntimeError('El modelo OCR oficial no coincide con la versión fijada; se cancela la compilación.')
out.write_bytes(data)
print('PASS Tesseract tessdata_fast español: modelo oficial y SHA-512 comprobados, bytes:',len(data))
