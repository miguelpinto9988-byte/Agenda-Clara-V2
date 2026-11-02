#!/usr/bin/env python3
"""Generate distinct glossy 256x256 RGBA PNG icons with no external dependencies.
All surrounding pixels remain transparent. Original Agenda Clara widget artwork.
"""
from pathlib import Path
import math,struct,zlib

SIZE=256
OUT=Path("AgendaClara/app/src/main/res/drawable-nodpi")
OUT.mkdir(parents=True,exist_ok=True)

class Canvas:
    def __init__(self):
        self.p=bytearray(SIZE*SIZE*4)
    def pixel(self,x,y,color,alpha=1.):
        if x<0 or y<0 or x>=SIZE or y>=SIZE or alpha<=0:return
        idx=(y*SIZE+x)*4
        r,g,b=color
        a=max(0.,min(1.,alpha))
        olda=self.p[idx+3]/255.
        newa=a+olda*(1-a)
        if newa<=0:return
        for i,c in enumerate((r,g,b)):
            self.p[idx+i]=round((c*a+self.p[idx+i]*olda*(1-a))/newa)
        self.p[idx+3]=round(newa*255)
    def box(self,x0,y0,x1,y1,radius,color,color2=None,opacity=1.):
        for y in range(max(0,int(y0)-1),min(SIZE,int(y1)+2)):
            for x in range(max(0,int(x0)-1),min(SIZE,int(x1)+2)):
                cx=min(max(x+.5,x0+radius),x1-radius)
                cy=min(max(y+.5,y0+radius),y1-radius)
                dist=math.hypot(x+.5-cx,y+.5-cy)
                alpha=min(1,max(0,radius+0.6-dist))*opacity
                if alpha<=0:continue
                t=max(0,min(1,(y-y0)/max(1,y1-y0)))
                if color2 is not None:
                    c=tuple(round(color[i]*(1-t)+color2[i]*t) for i in range(3))
                else:c=color
                self.pixel(x,y,c,alpha)
    def circle(self,cx,cy,radius,color,opacity=1.):
        for y in range(max(0,int(cy-radius-2)),min(SIZE,int(cy+radius+3))):
            for x in range(max(0,int(cx-radius-2)),min(SIZE,int(cx+radius+3))):
                a=max(0.,min(1.,radius+.5-math.hypot(x+.5-cx,y+.5-cy)))*opacity
                if a:self.pixel(x,y,color,a)
    def line(self,x1,y1,x2,y2,width,color,opacity=1.):
        half=width/2
        vx=x2-x1;vy=y2-y1;vv=vx*vx+vy*vy
        for y in range(max(0,int(min(y1,y2)-half-2)),min(SIZE,int(max(y1,y2)+half+3))):
            for x in range(max(0,int(min(x1,x2)-half-2)),min(SIZE,int(max(x1,x2)+half+3))):
                t=max(0,min(1,((x+.5-x1)*vx+(y+.5-y1)*vy)/vv)) if vv else 0
                d=math.hypot(x+.5-(x1+t*vx),y+.5-(y1+t*vy))
                a=max(0.,min(1.,half+.5-d))*opacity
                if a:self.pixel(x,y,color,a)
    def tile(self,top,bottom,round_tile=False):
        # Soft drop shadow, vivid gradient and translucent highlight.
        for r,opacity in [(105,.025),(103,.04),(101,.06)]:
            self.circle(130,133,r,(4,22,83),opacity)
        if round_tile:
            self.circle(127,126,101,bottom)
            self.circle(126,113,85,top,.55)
            self.circle(118,83,70,(255,255,255),.09)
        else:
            self.box(24,22,231,229,55,top,bottom)
            self.box(36,32,218,92,36,(255,255,255),None,.10)
    def save(self,name):
        scan=b''.join(b'\x00'+bytes(self.p[y*SIZE*4:(y+1)*SIZE*4]) for y in range(SIZE))
        def chunk(code,data):
            return struct.pack(">I",len(data))+code+data+struct.pack(">I",zlib.crc32(code+data)&0xffffffff)
        png=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack(">IIBBBBB",SIZE,SIZE,8,6,0,0,0))
             +chunk(b'IDAT',zlib.compress(scan,9))+chunk(b'IEND',b''))
        (OUT/("ic_ref_widget_"+name+".png")).write_bytes(png)

white=(255,255,255)
c=Canvas();c.tile((83,112,251),(6,183,222))
c.box(56,75,199,206,22,(230,250,255),(247,255,255))
c.box(56,75,199,110,20,(120,92,255))
c.box(83,60,102,100,9,(101,234,255))
c.box(155,60,174,100,9,(101,234,255))
for y in (137,159):
    c.line(82,y,104,y,9,(152,177,215))
c.circle(164,168,40,white)
c.circle(164,168,35,(18,211,138))
c.line(143,166,156,179,11,white);c.line(156,179,184,148,11,white)
c.save("brand")

c=Canvas();c.tile((140,82,255),(2,177,255),True)
c.circle(126,126,83,(79,221,255),.25)
c.line(128,79,128,175,22,(25,72,175),.25)
c.line(82,127,174,127,22,(25,72,175),.25)
c.line(128,81,128,171,17,white);c.line(82,127,174,127,17,white)
c.save("plus")

c=Canvas();c.tile((97,106,255),(105,65,245))
c.box(102,58,155,161,26,white)
c.box(108,65,122,125,7,(211,238,255))
for x in range(86,172,8):
    # Lower microphone support arc, gracefully declining near the edges.
    y=123+math.sqrt(max(0,45**2-(x-128)**2)) if abs(x-128)<=45 else 123
    if 90<=x<=166:c.circle(x,round(y),5.5,white)
c.line(128,169,128,190,11,white);c.line(103,190,153,190,11,white)
for x in (68,188):
    c.line(x,107,x,141,7,(117,228,255),.9)
c.save("voice")

c=Canvas();c.tile((42,224,199),(3,157,170))
c.box(67,48,193,208,20,white,(226,245,255))
for y in (94,122,150):
    c.line(93,y,165 if y!=150 else 139,y,9,(28,181,160))
c.circle(183,185,39,white);c.circle(183,185,32,(15,153,237))
c.line(183,170,183,200,10,white);c.line(168,185,198,185,10,white)
c.save("manual")

c=Canvas();c.tile((255,111,120),(233,46,83),True)
c.circle(128,128,79,(255,216,214),.45)
c.box(89,89,167,167,15,white)
c.save("cancel")
print("PASS generated five original 256x256 transparent PNG icons")
