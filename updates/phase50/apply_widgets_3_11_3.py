#!/usr/bin/env python3
"""Agenda Clara 3.11.3: modern floating chooser and colorful notes wave.
Applies only to the verified 3.11.2 source. All widget actions remain unchanged.
"""
from pathlib import Path
import base64,hashlib,io,math,struct,subprocess,zipfile,zlib

ROOT=Path("AgendaClara")
STAGE=Path(__file__).resolve().parent
RES=ROOT/"app/src/main/res"
GRADLE=ROOT/"app/build.gradle"
EXPECTED={
 "app/src/main/java/pe/agendaclara/app/WidgetTaskActivity.java":"7b19f4cb76e1a681906cbfb0e72bf6710fcbc494a491eb49079ba81f6da2a578",
 "app/src/main/java/pe/agendaclara/app/VoiceQuickTask.java":"75eecbf269603801eb7df2d97b262189dc4eff1cf9ac834d057d723ee4fa0d06",
 "app/src/main/res/layout/widget_sticky_notes.xml":"761346d6c7d3f1b9cb28ba161441c7039386b1abeeab602794feed0a3559158d",
 "app/src/main/res/layout/widget_sticky_notes_compact.xml":"ab41e53cac9a487f5bc7f162603b529bc2cfe762797d521cd11a8c89ef6bb98c",
}
for name,checksum in EXPECTED.items():
 p=ROOT/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=checksum:
  raise RuntimeError("Unexpected Agenda Clara 3.11.2 file: "+name)
version=GRADLE.read_text(encoding="utf8")
if version.count("versionCode 53")!=1 or version.count("versionName '3.11.2'")!=1:
 raise RuntimeError("Unexpected Android version; refusing patch")
resource_dir=RES/"drawable-nodpi"

# Approved vivid, transparent widget iconography is kept; names below allow
# the new 3D PNG asset bundle to replace just the artwork when present.
resources={}
bundle=STAGE/"artwork.zip.b64"
if bundle.exists():
 with zipfile.ZipFile(io.BytesIO(base64.b64decode(bundle.read_text("ascii")))) as archive:
  required={"ic_ref_widget_art_"+s+".png" for s in ("brand","voice","manual","wave","ribbon")}
  if set(archive.namelist())!=required:raise RuntimeError("Invalid artwork contents")
  for filename in archive.namelist():resources[filename]=archive.read(filename)
else:
 sources={"brand":"ic_ref_widget_brand.png","voice":"ic_ref_widget_voice.png",
          "manual":"ic_ref_widget_manual.png","wave":"ic_ref_voice_waveform.png"}
 for key,filename in sources.items():
  resources["ic_ref_widget_art_"+key+".png"]=(resource_dir/filename).read_bytes()
 # Reproducible transparent RGBA wave-strip with cyan -> purple flowing curves.
 w,h=900,110
 rows=bytearray()
 for y in range(h):
  rows.append(0)
  for x in range(w):
   t=x/(w-1)
   baseline=58+15*math.sin(t*3*math.pi+.6)+8*math.sin(t*6*math.pi)
   alpha=round(min(90,max(0,(y-baseline)*9)))
   rows.extend((round(40+110*t),round(195-110*t),round(251-12*t),alpha))
 def chunk(tag,data):
  return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
 resources["ic_ref_widget_art_ribbon.png"]=(
   b"\x89PNG\r\n\x1a\n"
   +chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))
   +chunk(b"IDAT",zlib.compress(rows,9))
   +chunk(b"IEND",b"")
 )
for name,data in resources.items():
 if not data.startswith(b"\x89PNG\r\n\x1a\n"):
  raise RuntimeError("Not a PNG: "+name)
 width,height,depth,color=struct.unpack(">IIBB",data[16:26])
 if name.endswith("_ribbon.png"):
  if (width,height,depth,color)!=(900,110,8,6):raise RuntimeError("Invalid ribbon: "+name)
 elif (width,height,depth)!=(256,256,8) or color not in (3,6):
  raise RuntimeError("Invalid widget icon: "+name)
 if (resource_dir/name).exists():raise RuntimeError("Refusing to overwrite "+name)

patch=zlib.decompress(base64.b64decode((STAGE/"code.patch.zlib.b64").read_text("ascii")))
subprocess.run(["git","apply","--check","--directory=AgendaClara","-"],input=patch,check=True)
subprocess.run(["git","apply","--directory=AgendaClara","-"],input=patch,check=True)
for name,data in resources.items():(resource_dir/name).write_bytes(data)
GRADLE.write_text(version.replace("versionCode 53","versionCode 54")
 .replace("versionName '3.11.2'","versionName '3.11.3'"),encoding="utf8")
print("PASS 3.11.3: white/lavender selector, existing transparent icons, cyan/violet notes waves")
