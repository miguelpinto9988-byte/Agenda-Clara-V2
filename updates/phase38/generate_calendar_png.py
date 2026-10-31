#!/usr/bin/env python3
"""Create two transparent, polished Calendar PNG icons with stdlib only.

These icons are intentionally distinct from the four legacy bottom navigation glyphs.
Each generated PNG is a deterministic 192x192 RGBA resource.
"""
from pathlib import Path
import math
import struct
import zlib

N = 192


def rounded(x, y, left, top, right, bottom, radius):
    cx = min(max(x, left + radius), right - radius)
    cy = min(max(y, top + radius), bottom - radius)
    return (x - cx)**2 + (y - cy)**2 <= radius**2


def circle(x, y, cx, cy, radius):
    return (x - cx)**2 + (y - cy)**2 <= radius**2


def segment(x, y, ax, ay, bx, by, thickness):
    dx, dy = bx - ax, by - ay
    t = max(0., min(1., ((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
    return circle(x, y, ax+t*dx, ay+t*dy, thickness/2)


def blend(dst, rgb, opacity):
    if opacity <= 0: return dst
    opacity = min(opacity, 1.)
    base = dst[3] / 255.
    alpha = opacity + base*(1.-opacity)
    if alpha == 0: return (0, 0, 0, 0)
    return tuple(round((rgb[k]*opacity + dst[k]*base*(1.-opacity))/alpha) for k in range(3)) + (round(alpha*255),)


def picture(kind):
    pixels = bytearray(N*N*4)
    def paint(shape, rgb, opacity=1, rect=(0, 0, N, N)):
        left, top, right, bottom = rect
        for y in range(max(0, top), min(N, bottom)):
            for x in range(max(0, left), min(N, right)):
                coverage = 0
                for dx,dy in ((.24,.24),(.76,.24),(.24,.76),(.76,.76)):
                    coverage += bool(shape(x+dx,y+dy))
                if not coverage: continue
                p = 4*(y*N+x)
                rgb_val = rgb(x,y) if callable(rgb) else rgb
                pixels[p:p+4] = bytes(blend(tuple(pixels[p:p+4]), rgb_val, opacity*coverage/4))
    # Soft halo creates slight optical separation from adjacent bold lettering.
    paint(lambda x,y: rounded(x,y,22,26,185,185,39),(48,72,136),.07)
    paint(lambda x,y: rounded(x,y,17,18,181,180,41),(44,66,127),.15)
    if kind == 'today':
        paint(lambda x,y:rounded(x,y,14,12,177,176,38),
              lambda x,y:(round(37+27*y/N),round(197-87*y/N),round(252-16*y/N)))
        paint(lambda x,y:rounded(x,y,20,16,171,75,34), (191,242,255),.18)
        # Paper calendar sheet, with distinct saturated royal-blue header.
        paint(lambda x,y:rounded(x,y,37,43,154,151,18),(245,251,255))
        paint(lambda x,y:rounded(x,y,38,44,153,81,17),(26,112,226))
        paint(lambda x,y: 44<x<147 and 72<y<81, (26,112,226))
        for pos in (68,124):
            paint(lambda x,y,p=pos:rounded(x,y,p-6,30,p+6,57,6),(21,75,179))
            paint(lambda x,y,p=pos:rounded(x,y,p-3,28,p+3,55,3),(225,253,255))
        # Selected day represented by a check and halo, never a fixed date number.
        paint(lambda x,y:circle(x,y,96,115,26),(224,238,255))
        paint(lambda x,y:circle(x,y,96,115,21),(53,90,238))
        paint(lambda x,y:segment(x,y,84,114,93,123,6),(255,255,255))
        paint(lambda x,y:segment(x,y,93,123,109,106,6),(255,255,255))
    elif kind == 'classes':
        paint(lambda x,y:rounded(x,y,14,12,177,176,38),
              lambda x,y:(round(51+48*y/N),round(109+12*y/N),round(248-20*y/N)))
        paint(lambda x,y:rounded(x,y,22,19,167,68,30),(191,227,255),.17)
        paint(lambda x,y:rounded(x,y,36,38,157,157,17),(249,251,255))
        paint(lambda x,y:rounded(x,y,37,39,156,70,16),(66,79,230))
        paint(lambda x,y: 42<x<151 and 64<y<72,(66,79,230))
        for cx in (62,128):
            paint(lambda x,y,c=cx:rounded(x,y,c-5,27,c+5,48,5),(32,70,164))
            paint(lambda x,y,c=cx:rounded(x,y,c-2,25,c+2,46,2),(243,251,255))
        # Timetable blocks and left-of-row day indicators.
        for yy,color in ((84,(62,146,250)),(107,(22,188,187)),(130,(145,101,245))):
            paint(lambda x,y,p=yy:circle(x,y,52,p+5,5),color)
            paint(lambda x,y,p=yy:rounded(x,y,64,p,131,p+10,5),color)
        # Tiny clock badge at the lower-right; immediately recognizable as schedule.
        paint(lambda x,y:circle(x,y,143,137,25),(229,236,255))
        paint(lambda x,y:circle(x,y,143,137,21),(255,255,255))
        paint(lambda x,y:circle(x,y,143,137,17),(54,101,233))
        paint(lambda x,y:circle(x,y,143,137,13),(255,255,255))
        paint(lambda x,y:segment(x,y,143,137,143,127,3.7),(41,84,205))
        paint(lambda x,y:segment(x,y,143,137,151,141,3.7),(41,84,205))
    else: raise ValueError(kind)
    raw = b''.join(b'\0'+pixels[y*N*4:(y+1)*N*4] for y in range(N))
    def chunk(tag,payload):
        return struct.pack('>I',len(payload))+tag+payload+struct.pack('>I',zlib.crc32(tag+payload)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,6,0,0,0))+
            chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))


def generate(output):
    out = Path(output)
    out.mkdir(parents=True,exist_ok=True)
    for kind,name in (('today','ic_ref_today_jump.png'),('classes','ic_ref_class_schedule.png')):
        data = picture(kind)
        path=out/name
        if path.exists(): raise RuntimeError(f'Refusing to overwrite {path}')
        path.write_bytes(data)
        print(f'PASS PNG {path} {len(data)} bytes')

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2: raise SystemExit('Usage: generate_calendar_png.py target-drawable-nodpi')
    generate(sys.argv[1])
