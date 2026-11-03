#!/usr/bin/env python3
"""Replace legacy Android panel icons with scalable transparent 3D-style art.

Runs AFTER phase53/build_500.py. Uses solid multicolour fills and local highlights,
not a background gradient. Exports native 2048px + mobile 256px PNG.
"""
from pathlib import Path
from PIL import Image
import cairosvg
import io, json, hashlib

BASE=Path("AgendaClara/app/src/main")
RES=BASE/"res/drawable-nodpi"
ASSETS=BASE/"assets"
FHD=Path("icon_library_500/panel_icons_fhd_2048")
SVG_START='''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><defs><filter id="shadow" x="-30%" y="-30%" width="170%" height="170%"><feDropShadow dx="0" dy="15" stdDeviation="14" flood-color="#1D2065" flood-opacity=".27"/></filter></defs><g stroke-linecap="round" stroke-linejoin="round" filter="url(#shadow)">'''
SVG_END="</g></svg>"
def rect(x,y,w,h,r,fill,stroke="#34238E",sw=13):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def path(d,fill,stroke="#36249A",sw=12):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def ellipse(x,y,rx,ry,fill,stroke="none",sw=0):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def check(x,y):
    return rect(x,y,92,89,21,"#13D94E","#079C30",9)+path(f"M{x+22} {y+46} l19 19 32 -37","none","white",15)
def lines(y):
    return rect(379,y,255,23,11,"#9386E8","none",0)+rect(379,y+44,168,17,8,"#C4B7F7","none",0)
def gleam():
    return path("M195 304 Q191 254 232 217","none","white",23)+ellipse(404,184,34,11,"#FDFBFF")
def exams():
    s=rect(125,170,746,733,117,"#7C30EC","#4620B4",23)+rect(192,233,615,611,76,"#F9F7FF","#BFB5F8",17)
    s+=rect(341,174,324,126,52,"#03CEEA","#0589C4",15)+ellipse(506,183,24,24,"#EFFFFF","#0487C1",9)
    s+=check(261,365)+check(261,493)+rect(261,626,92,89,21,"#B7AAF0","#8571D8",9)
    s+=lines(378)+lines(505)+rect(379,640,207,22,11,"#9386E8","none",0)
    s+=path("M383 249 L633 139 881 242 628 352Z","#843AF7","#4F21C0",22)
    s+=path("M459 311 Q625 394 799 304 L796 387 Q622 473 460 388Z","#652ED5","#4720B6",12)
    s+=path("M881 245 Q919 322 899 394","none","#FFBE20",26)
    s+=ellipse(900,431,24,39,"#FFC720","#E9A11A",10)+gleam()
    return s
def schedule():
    s=rect(121,167,737,710,112,"#7830EA","#4F20B4",20)+rect(133,324,715,545,88,"#FAF8FF","#C5B9F6",15)
    s+=rect(121,153,728,225,100,"#8A35F7","#551EBE",18)
    s+=rect(275,103,75,175,35,"#CFB3FF","#7042C6",13)+rect(607,103,75,175,35,"#CFB3FF","#7042C6",13)
    for y in (430,568):
        for x in (208,356,503):
            s+=rect(x,y,110,102,23,"#C9BBF7","#AAA0E7",5)
    s+=rect(356,568,110,102,23,"#B31AF5","#7714D0",9)
    s+=ellipse(726,704,215,215,"#07C7E9","#087CCF",23)+ellipse(726,704,174,174,"#FDFCFF","#B1B7FC",12)
    s+=path("M725 595 V705 H823","none","#682FDA",28)+ellipse(725,705,24,24,"#B838ED","#5C27C0",8)
    s+=path("M179 253 Q191 198 240 193","none","white",22)
    return s
def courses():
    s=rect(182,571,659,161,63,"#04C5DB","#068ABB",17)+rect(230,624,607,81,23,"#FAFBFF","#A2CDF8",9)
    s+=rect(164,417,688,161,65,"#1587F1","#1551CB",17)+rect(218,472,621,80,22,"#FEFAFF","#A1B7FF",9)
    s+=rect(188,259,658,174,65,"#FC4B9D","#C12A91",18)+rect(231,315,607,78,23,"#FEFAFF","#DDB2FF",9)
    s+=path("M146 244 L525 111 906 237 523 379Z","#823BF4","#4B20B5",23)
    s+=path("M258 306 Q523 462 794 305 L787 401 Q516 512 261 404Z","#642BD7","#4821AE",13)
    s+=path("M908 240 Q946 326 910 409","none","#FFBE19",26)+ellipse(913,450,24,38,"#FFCC21","#EFA110",9)
    s+=path("M224 247 Q313 190 405 194","none","white",19)
    return s
def myday():
    s=rect(130,156,751,732,116,"#05BFEB","#087FC9",22)+rect(200,234,610,597,76,"#F9FCFF","#9DBCF7",17)
    s+=rect(312,139,389,145,55,"#06D0D9","#068BB5",17)+ellipse(506,155,25,25,"#E4FFFF","#0385B9",10)
    s+=rect(279,321,468,160,42,"#2EDDB7","#0BAD93",11)
    s+=ellipse(508,389,49,49,"#FFD126","#F0AB18",8)
    s+=path("M508 319 V333 M508 451 V464 M437 389 H451 M566 389 H581 M459 338 L468 350 M556 433 L566 444","none","#FFE146",14)
    s+=check(289,531)+check(289,645)+lines(553)+lines(664)
    s+=path("M758 553 L787 619 855 642 793 680 786 743 745 698 683 695 718 645Z","#FFCE27","#F1A51E",12)
    s+=path("M179 303 Q179 252 217 219","none","white",23)
    return s
ART={"ui_exam_review":exams,"ui_class_schedule":schedule,"ui_course_add":courses,"ui_my_guide":myday}
def main():
    catalog_path=ASSETS/"adaptive_icon_catalog.json"
    catalog=json.loads(catalog_path.read_text(encoding="utf-8"))
    assert catalog["count"]==500 and len(catalog["icons"])==500
    FHD.mkdir(parents=True,exist_ok=True)
    changes=[]
    for key,drawing in ART.items():
        file=f"ic_adapt_{key}.png"
        old=RES/file
        assert old.exists(),file
        old_hash=hashlib.sha256(old.read_bytes()).hexdigest()
        source=(SVG_START+drawing()+SVG_END).encode("utf-8")
        for size,target in ((2048,FHD/file),(256,old)):
            png=cairosvg.svg2png(bytestring=source,output_width=size,output_height=size)
            im=Image.open(io.BytesIO(png)).convert("RGBA")
            assert im.size==(size,size) and im.getpixel((0,0))[3]==0 and im.getbbox()
            im.save(target,format="PNG",optimize=True)
        new_hash=hashlib.sha256(old.read_bytes()).hexdigest()
        assert new_hash!=old_hash, "legacy icon not replaced: "+key
        catalog["icons"][key].update(file=file,source="phase54_panel_redesign",fullhd_master=True)
        changes.append({"key":key,"old_hash":old_hash,"new_hash":new_hash})
    catalog["png_bytes"]=sum(x.stat().st_size for x in RES.glob("ic_adapt_*.png"))
    assert catalog["png_bytes"]<=15_000_000
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (FHD/"MANIFEST.json").write_text(json.dumps({"count":4,"size":[2048,2048],"replaced":changes},indent=2)+"\n",encoding="utf-8")
    print("PASS four prior panel icons replaced, new 256px Android and 2048px masters")
if __name__=="__main__":main()
