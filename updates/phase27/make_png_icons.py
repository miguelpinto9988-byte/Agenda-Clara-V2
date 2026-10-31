#!/usr/bin/env python3
"""Generate original, transparent, antialiased 3-colour PNG UI resources.

Only Python standard library; no Pillow, SVG renderer or external assets.
Icons are created at 96x96 RGBA with alpha=0 beyond the glyph.
"""
import math,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/res/drawable-nodpi"
ROOT.mkdir(parents=True,exist_ok=True)
N=96
B=(53,104,248);C=(16,188,224);P=(124,76,232);Y=(255,167,34)
G=(18,188,128);R=(239,85,105);D=(25,54,109);WHITE=(255,255,255)
PALE=(224,235,255);MINT=(209,250,235);LILAC=(234,223,255);PINK=(255,226,231)
def dist(x,y,x1,y1,x2,y2):
    vx=x2-x1;vy=y2-y1
    if vx*vx+vy*vy==0:return math.hypot(x-x1,y-y1)
    t=max(0,min(1,((x-x1)*vx+(y-y1)*vy)/(vx*vx+vy*vy)))
    return math.hypot(x-x1-vx*t,y-y1-vy*t)
class Icon:
    def __init__(self):self.px=bytearray(N*N*4)
    def paint(self,fn,color):
        # Soft edge via four subsamples around the pixel centre.
        for py in range(N):
            for px in range(N):
                coverage=sum(fn((px+(dx+.5)/2)*24/N,(py+(dy+.5)/2)*24/N) for dx in (0,1) for dy in (0,1))/4
                if not coverage:continue
                i=(py*N+px)*4
                a=coverage
                old=self.px[i+3]/255
                out=a+old*(1-a)
                if out==0:continue
                for channel in range(3):
                    self.px[i+channel]=round((color[channel]*a+self.px[i+channel]*old*(1-a))/out)
                self.px[i+3]=round(out*255)
    def circle(self,x,y,r,col,thick=0):
        self.paint(lambda xx,yy: abs(math.hypot(xx-x,yy-y)-r)<=thick/2 if thick else math.hypot(xx-x,yy-y)<=r,col)
    def line(self,x,y,x2,y2,col,w=2.4):
        self.paint(lambda xx,yy:dist(xx,yy,x,y,x2,y2)<=w/2,col)
    def rect(self,x,y,x2,y2,col,r=0,stroke=0):
        def inside(xx,yy,inset=0):
            l=x+inset;t=y+inset;rr=x2-inset;bb=y2-inset;rad=max(0,r-inset)
            if xx<l or yy<t or xx>rr or yy>bb:return False
            if rad<=0:return True
            nearx=min(max(xx,l+rad),rr-rad);neary=min(max(yy,t+rad),bb-rad)
            return (xx-nearx)**2+(yy-neary)**2<=rad**2
        self.paint(lambda xx,yy: inside(xx,yy) and (not stroke or not inside(xx,yy,stroke)),col)
    def poly(self,points,col,w=2.4):
        for a,b in zip(points,points[1:]):self.line(a[0],a[1],b[0],b[1],col,w)
    def save(self,path):
        raw=b''.join(b'\0'+self.px[y*N*4:(y+1)*N*4] for y in range(N))
        def chunk(name,data):return struct.pack('!I',len(data))+name+data+struct.pack('!I',zlib.crc32(name+data)&0xffffffff)
        path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',N,N,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
def art(name):
    i=Icon()
    if name in ("folder","projects","category"):
        i.rect(2.5,7.5,21.5,20.8,PALE,2.2)
        i.poly([(2.5,10),(2.5,5),(10,5),(12.2,8),(21,8),(21,20),(3,20),(2.5,10)],B,2.2)
        i.line(5,11.7,19,11.7,C,2.6)
    elif name in ("date","calendar","device_calendar"):
        i.rect(3,5,21,21,PALE,2)
        i.rect(3,5,21,21,B,2,2)
        i.line(3.8,10,20,10,C,2.5);i.line(8,2.5,8,7,B);i.line(16,2.5,16,7,B)
        for x,y,c in ((8,14,Y),(15,14,C),(11.5,18,P)):i.circle(x,y,1.65,c)
    elif name=="google_calendar":
        i.rect(2.8,3.5,21,21,WHITE,1.5)
        i.rect(3,4,12,8.2,(66,133,244));i.rect(12,4,21,8.2,(52,168,83))
        i.rect(3,8,6,21,(251,188,5));i.rect(18,8,21,21,(234,67,53))
        i.rect(3,4,21,21,B,1.5,1.4)
        i.line(8,13.5,16,13.5,B,2.4);i.line(9,17,15,17,C,2.3)
    elif name in ("clock","time"):
        i.circle(12,12,9,B,2.5);i.line(12,6.5,12,12,C,2.8);i.line(12,12,16.5,15,C,2.8);i.circle(12,12,1.6,Y)
    elif name in ("bell","notification"):
        i.circle(12,11,5.4,(255,241,206))
        i.poly([(5,17.5),(7,15),(7,10),(9,6),(12,5),(15,6),(17,10),(17,15),(19,17.5),(5,17.5)],Y,2.5)
        i.line(10,20,14,20,R,2.5);i.circle(18.8,5.8,2.0,C)
    elif name=="repeat":
        i.circle(12,12,8,G,2.5)
        i.rect(2,9,7.5,14,WHITE)
        i.rect(16.5,9,22,14,WHITE)
        i.poly([(3,9),(4,13),(8,12)],G,2.6);i.poly([(21,15),(20,11),(16,12)],C,2.6)
        i.line(5,9,8,6,G,2)
    elif name in ("notes","book"):
        i.rect(5,2.7,19,22,PALE,2.1);i.rect(5,2.7,19,22,B,2.1,2)
        i.line(8,8.5,16,8.5,C,2.3);i.line(8,12.5,16,12.5,C,2.3);i.line(8,16.5,13,16.5,P,2.3)
    elif name in ("check","save"):
        i.rect(3,3,21,21,MINT,3);i.rect(3,3,21,21,G,3,2)
        i.poly([(7.5,12),(10.5,15.3),(17.4,8.8)],B,2.9)
    elif name=="whatsapp":
        i.circle(12,12,10,(29,196,83))
        i.circle(12,11.5,7.2,WHITE,1.5)
        i.poly([(7,17),(6.4,19),(9.1,17.9)],WHITE,1.8)
        i.poly([(9,8),(10.8,11),(13,13.5),(16,14.5)],WHITE,2.2)
    elif name in ("backup","cloud"):
        i.circle(9,12,5.6,PALE);i.circle(16,10.8,6.2,PALE)
        i.poly([(4,17),(2.8,14.5),(4,11),(7,9),(9.5,5),(14.5,5),(18,9),(21,11),(21,16.8),(4,17)],B,2)
        i.line(12,10.5,12,17,C,2.8);i.poly([(9.5,14),(12,17),(14.5,14)],C,2.4)
    elif name in ("widgets",):
        for x,y,c in ((2.5,2.5,P),(13.5,2.5,B),(2.5,13.5,C),(13.5,13.5,P)):
            i.rect(x,y,x+8,y+8,PALE,1.5);i.rect(x,y,x+8,y+8,c,1.5,2)
    elif name in ("settings","gear"):
        i.circle(12,12,7.4,B,2.8);i.circle(12,12,3,C,2.3)
        for k in range(8):
            a=2*math.pi*k/8;i.line(12+8*math.cos(a),12+8*math.sin(a),12+10.6*math.cos(a),12+10.6*math.sin(a),P,2.6)
    elif name in ("photo","camera"):
        i.rect(2.8,7,21,20,PALE,2.4);i.rect(2.8,7,21,20,B,2.4,2.4)
        i.rect(7,4,14,8,PALE,1.5);i.line(7.4,5,13.5,5,B,2)
        i.circle(12,13.5,4,C,2.6);i.circle(19.5,4,2.2,Y)
    elif name in ("manual","edit","pencil"):
        i.rect(3,5,17,22,PALE,2);i.rect(3,5,17,22,B,2,2)
        i.poly([(9,17),(17.3,8.7),(20.4,11.7),(12,20),(8.5,21)],Y,3)
        i.line(7,10,11.5,10,C,2.1)
    elif name=="help":
        i.circle(12,12,9,PALE);i.circle(12,12,9,B,2.3)
        i.poly([(9.4,9),(9.5,7.5),(12,6.4),(14.5,8),(14.7,10),(12,12.5),(12,14)],P,2.5);i.circle(12,18,1.2,C)
    elif name=="back":
        i.poly([(14.5,4.5),(7,12),(14.5,19.5)],B,3);i.line(7.5,12,20,12,C,2.5)
    elif name in ("school","study"):
        i.poly([(2,9),(12,4),(22,9),(12,14),(2,9)],B,2.5)
        i.poly([(6,12),(6,17),(12,20),(18,17),(18,12)],C,2.5)
        i.line(21,10,21,18,Y,2.5)
    elif name=="heart":
        i.poly([(12,20),(4,13),(3,9),(5,5),(9,5),(12,9),(15,5),(19,5),(21,9),(20,13),(12,20)],G,2.6)
        i.circle(18,5,1.4,C)
    elif name=="work":
        i.rect(3,8,21,21,(255,238,212),2);i.rect(3,8,21,21,Y,2,2.2)
        i.poly([(8,8),(8,5),(16,5),(16,8)],B,2.3);i.line(3,13,21,13,C,2.1)
    elif name=="home":
        i.poly([(3,11),(12,3),(21,11)],R,2.7);i.poly([(5.5,11),(5.5,21),(18.5,21),(18.5,11)],B,2.4)
        i.rect(10,15,14,21,PALE,1)
    elif name=="travel":
        i.line(4,20,20,4,C,3);i.poly([(10,7),(20,4),(17,14)],B,2.6);i.line(7,17,3,13,Y,2.5)
    elif name in ("trash","delete"):
        i.rect(6,7,18,21,PINK,1.5);i.rect(6,7,18,21,R,1.5,2)
        i.line(4,6.5,20,6.5,B,2.6);i.line(9,3.5,15,3.5,B,2.3)
        i.line(10,11,10,17,R,2);i.line(14,11,14,17,R,2)
    elif name in ("lock","key"):
        if name=="lock":
            i.rect(5,10,19,21,(255,240,210),2);i.rect(5,10,19,21,Y,2,2.5)
            i.poly([(8,10),(8,7),(10,4),(14,4),(16,7),(16,10)],B,2.3);i.circle(12,15,1.3,C)
        else:
            i.circle(7,8,4,Y,2.3);i.line(10,11,20,21,B,3);i.line(17,18,20,15,C,2.1)
    elif name=="search":
        i.circle(10,10,6.7,B,2.8);i.line(15.5,15.5,21,21,C,3)
    elif name=="color":
        i.circle(12,12,9,PALE);i.circle(12,12,9,B,2.4)
        for x,y,c in ((8,7,R),(15,7,Y),(7.5,14,G),(16,13,P)):i.circle(x,y,2,c)
    elif name=="urgent":
        i.poly([(12,3),(22,21),(2,21),(12,3)],R,2.6)
        i.line(12,9,12,14,Y,2.4);i.circle(12,18,1,B)
    else:
        raise RuntimeError("icon not implemented: "+name)
    return i
NAMES=[
 "folder","projects","category","date","calendar","device_calendar","google_calendar",
 "clock","time","bell","notification","repeat","notes","book","check","save","whatsapp",
 "backup","cloud","widgets","settings","gear","photo","camera","manual","edit","pencil",
 "help","back","school","study","heart","work","home","travel","trash","delete","lock",
 "key","search","color","urgent"
]
for item in NAMES:
    file=ROOT/("agenda_icon_"+item+".png")
    art(item).save(file)
    data=file.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n' and len(data)>100
print("PASS: "+str(len(NAMES))+" transparent 96px RGBA multicolour PNG icons generated")
