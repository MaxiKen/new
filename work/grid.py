import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys

NC,NR=12,7
COLS=[chr(ord('A')+i) for i in range(NC)]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def overlay(base, out, crop=None):
    im=Image.open(base).convert('RGB')
    if crop: im=im.crop(crop)
    W,H=im.size
    CW,CH=W/NC,H/NR
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    lw=max(3,int(round(W/2000)))
    for i in range(NC+1):
        x=int(round(i*CW)); d.line([(x,0),(x,H)],fill=(25,25,25,150),width=lw if 0<i<NC else lw*3)
    for j in range(NR+1):
        y=int(round(j*CH)); d.line([(0,y),(W,y)],fill=(25,25,25,150),width=lw if 0<j<NR else lw*3)
    fs=int(round(min(CW,CH)*0.165))
    font=ImageFont.truetype(FONT, fs)
    for j in range(NR):
        for i in range(NC):
            lab=f'{COLS[i]}{j+1}'
            x0=int(round(i*CW)); y0=int(round(j*CH))
            bb=d.textbbox((0,0),lab,font=font)
            tw,th=bb[2]-bb[0], bb[3]-bb[1]
            padx,pady=int(tw*0.45),int(th*0.35)
            bx0,by0=x0+int(CW*0.02), y0+int(CH*0.02)
            d.rounded_rectangle([bx0,by0,bx0+tw+2*padx,by0+th+2*pady],radius=int(pady*1.2),
                                fill=(255,255,255,215),outline=(20,20,20,190),width=max(2,lw))
            d.text((bx0+padx-bb[0],by0+pady-bb[1]),lab,font=font,fill=(15,15,15,255))
    im=Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB')
    im.save(out, optimize=True)
    print('wrote',out, im.size)

overlay('NGSA_geology_isolated_v2.png','NGSA_geology_isolated_v2_grid.png')
overlay('NGSA_map_geology_legend_isolated.png','NGSA_isolated_v1_grid.png')
overlay('pic NGSA geological-map-of-nigeria-.jpg','pic_NGSA_grid.png',crop=(120,96,120+6268,96+3540))
