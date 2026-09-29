"""Generate original gallery typography and geometric line artwork. Requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
W,H=1800,590
im=Image.new('RGB',(W,H),'#101015')
draw=ImageDraw.Draw(im)
def font(size,bold=False):
    options=[('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in options:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)
for x in range(1020,W):
    t=(x-1020)/(W-1020)
    draw.line((x,0,x,H),fill=(int(16+30*t),int(16-2*t),int(21+2*t)))
for x in range(1000,W,44): draw.line((x,0,x,H),fill='#34202b',width=1)
for y in range(0,H,44): draw.line((1000,y,W,y),fill='#34202b',width=1)
draw.rectangle((0,0,13,H),fill='#f04459')
draw.rounded_rectangle((77,58,358,104),radius=22,fill='#391e29')
draw.text((99,63),'THE DESIGN COLLECTION',font=font(19,True),fill='#ff8b9c')
draw.text((72,130),'GEORGE',font=font(113,True),fill='#fff7f4')
draw.text((70,248),'PRINTS',font=font(113,True),fill='#f04459')
draw.text((80,404),'CHARACTER.  FUNCTION.  FILAMENT.',font=font(29,True),fill='#fff7f4')
draw.text((80,462),'Browse the designs. Explore the files. Make something.',font=font(25),fill='#b6a7b2')
def cube(cx,cy,s):
    top=[(cx,cy-s),(cx+s,cy-s/2),(cx,cy),(cx-s,cy-s/2)]
    left=[(cx-s,cy-s/2),(cx,cy),(cx,cy+s),(cx-s,cy+s/2)]
    right=[(cx,cy),(cx+s,cy-s/2),(cx+s,cy+s/2),(cx,cy+s)]
    for poly,fill in [(top,'#f04459'),(left,'#742234'),(right,'#ac2e43')]:
        draw.polygon(poly,fill=fill);draw.line(poly+[poly[0]],fill='#ff8294',width=3)
cube(1394,228,117)
cube(1277,404,117)
cube(1511,404,117)
draw.line((1136,111,1136,520),fill='#70434b',width=2)
draw.line((1109,111,1163,111),fill='#70434b',width=2)
draw.line((1109,520,1163,520),fill='#70434b',width=2)
draw.text((1600,68),'01 / ∞',font=font(26),fill='#ff9dab')
im.save(ROOT/'gallery-banner.png')
print(ROOT/'gallery-banner.png')
