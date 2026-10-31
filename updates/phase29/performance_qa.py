#!/usr/bin/env python3
"""Profile native Android navigation: gfxinfo frame time and app PSS only."""
import argparse, json, math, re, statistics, subprocess, time
import xml.etree.ElementTree as ET
from pathlib import Path
PKG="pe.agendaclara.app"

def frames(text):
    active=False; header=None; result=[]
    for line in text.splitlines():
        line=line.strip()
        if line=="---PROFILEDATA---":
            active=not active; header=None; continue
        if not active: continue
        if line.startswith("Flags,"):
            header=line.split(","); continue
        if not header or not line[:1].isdigit(): continue
        values=line.split(",")
        if len(values)!=len(header): continue
        row=dict(zip(header,values))
        try:
            begin=int(row["IntendedVsync"]); end=int(row["FrameCompleted"])
            if int(row["Flags"])==0 and begin>0 and 0<end-begin<10_000_000_000:
                result.append(((end-begin)/1e6,end))
        except (KeyError,ValueError): pass
    return result

def pss(text):
    m=re.search(r"\bTOTAL PSS:\s*([\d,]+)",text,re.I)
    if not m: m=re.search(r"(?m)^\s*TOTAL\s+([\d,]+)\s+",text)
    if not m: raise ValueError("Android meminfo does not expose TOTAL PSS")
    return int(m.group(1).replace(",",""))

def summary(samples,before,after,hz):
    if len(samples)<5 or hz<=0: raise ValueError("Need >=5 valid frames and a positive refresh rate")
    ms=sorted(x[0] for x in samples)
    stamps=sorted(set(x[1] for x in samples))
    periods=[(b-a)/1e6 for a,b in zip(stamps,stamps[1:])]
    active=[x for x in periods if 2<x<100]
    return {"frames":len(samples),"refresh_reference_hz":hz,
            "frame_p50_ms":round(ms[math.ceil(len(ms)*.5)-1],2),
            "frame_p95_ms":round(ms[math.ceil(len(ms)*.95)-1],2),
            "over_frame_budget_pct":round(100*sum(x>1000/hz for x in ms)/len(ms),2),
            "approx_active_drawing_fps":round(1000/statistics.median(active),1) if len(active)>=3 else None,
            "pss_before_kib":before,"pss_after_kib":after,"pss_delta_kib":after-before}

def adb(serial,*args):
    command=["adb"]+(["-s",serial] if serial else [])+list(args)
    return subprocess.run(command,text=True,capture_output=True,check=True,timeout=45).stdout

def tap(serial,name):
    adb(serial,"shell","uiautomator","dump","/sdcard/agenda_perf.xml")
    xml=adb(serial,"exec-out","cat","/sdcard/agenda_perf.xml")
    for node in ET.fromstring(xml).iter("node"):
        label=node.get("content-desc","")
        if label.startswith(name+",") and "pestaña" in label:
            bounds=list(map(int,re.findall(r"\d+",node.get("bounds",""))))
            if len(bounds)==4:
                adb(serial,"shell","input","tap",str((bounds[0]+bounds[2])//2),str((bounds[1]+bounds[3])//2))
                time.sleep(.65)
                if not adb(serial,"shell","pidof",PKG).strip(): raise RuntimeError("App exited after "+name)
                return
    raise RuntimeError("Missing navigation tab: "+name)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",required=True,choices=("emulator","physical"))
    ap.add_argument("--serial");ap.add_argument("--out",required=True)
    ap.add_argument("--refresh-hz",type=float,default=60.0)
    ap.add_argument("--baseline-json",help="Prior measurement on same device/configuration")
    args=ap.parse_args()
    is_emulator=adb(args.serial,"shell","getprop","ro.kernel.qemu").strip()=="1"
    if (args.mode=="emulator")!=is_emulator: ap.error("Wrong device type for requested mode")
    if not adb(args.serial,"shell","pm","path",PKG).strip().startswith("package:"):
        ap.error("Install the application first; this script never installs it")
    if is_emulator:
        for setting in ("animator_duration_scale","window_animation_scale","transition_animation_scale"):
            adb(args.serial,"shell","settings","put","global",setting,"1")
    adb(args.serial,"shell","am","start","-W","-n",PKG+"/.MainActivity")
    time.sleep(3)
    before=pss(adb(args.serial,"shell","dumpsys","meminfo",PKG))
    adb(args.serial,"shell","dumpsys","gfxinfo",PKG,"reset")
    if is_emulator:
        for _ in range(3):
            for tab in ("Calendario","Revisar","Conexiones","Agenda"): tap(args.serial,tab)
    else:
        print("En el teléfono recorre las cuatro pestañas tres veces, revisa colores, botón + y transiciones.")
        print("Evita utilizar tareas o mensajes personales durante la prueba.")
        input("Pulsa Enter al finalizar las comprobaciones: ")
    sample=frames(adb(args.serial,"shell","dumpsys","gfxinfo",PKG,"framestats"))
    after=pss(adb(args.serial,"shell","dumpsys","meminfo",PKG))
    data=summary(sample,before,after,args.refresh_hz)
    if args.baseline_json:
        baseline=json.loads(Path(args.baseline_json).read_text(encoding="utf-8"))
        if data["refresh_reference_hz"]!=baseline["refresh_reference_hz"]:
            raise ValueError("Invalid comparison: refresh rates differ")
        data["baseline_delta"]={"p95_ms":round(data["frame_p95_ms"]-baseline["frame_p95_ms"],2),
                                "pss_kib":data["pss_after_kib"]-baseline["pss_after_kib"]}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    text=["# Agenda Clara - rendimiento de navegación","",
          "Fuente: Android dumpsys gfxinfo y meminfo. No se guardan tareas ni mensajes.",
          "FPS de dibujo estimados en ráfagas activas: no son FPS sostenidos.",
          "Sin línea base comparable no se afirma mejora de rendimiento.","",
          "| Métrica | Valor |","|---|---:|"]
    text.extend(f"| {key} | {value} |" for key,value in data.items())
    out.with_suffix(".md").write_text("\n".join(text)+"\n",encoding="utf-8")
    print("PASS rendimiento Android:",out)
if __name__=="__main__": main()
