from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 1024
C = SIZE // 2
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ===== MAGNETIC FIELD ARCS =====
gold = (245, 158, 11)
for i, radius in enumerate([340, 410, 480]):
    alpha = int(150 - i*40)
    for a0, a1 in [(-55, 55), (125, 235)]:
        box = [C-radius, C-radius, C+radius, C+radius]
        for layer in range(5):
            col = (*gold, max(0, alpha - layer*20))
            draw.arc(box, a0, a1, fill=col, width=2)
            box = [b + (1 if idx<2 else -1) for idx,b in enumerate(box)]

# Flux particles
for t, a_start, a_span, r, sz in [
    (0.15, -55, 110, 450, 10),
    (0.45, -55, 110, 450, 8),
    (0.75, -55, 110, 450, 10),
    (0.25, 125, 110, 400, 7),
    (0.65, 125, 110, 400, 7),
]:
    ang = math.radians(a_start + t*a_span)
    x = C + r*math.cos(ang)
    y = C + r*math.sin(ang)
    draw.ellipse([x-sz-4, y-sz-4, x+sz+4, y+sz+4], fill=(*gold, 70))
    draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(*gold, 210))
    draw.ellipse([x-sz//2, y-sz//2, x+sz//2, y+sz//2], fill=(255, 240, 200, 255))

# ===== 3D HEXAGON BADGE =====
R = 210
depth = 18

def hex(cx, cy, r, rot=30):
    return [(cx + r*math.cos(math.radians(60*i+rot)),
             cy + r*math.sin(math.radians(60*i+rot))) for i in range(6)]

# Extrusion shadow layers (dark amber/brown)
for d in range(depth, 0, -1):
    s = int(30 + (depth-d)*10)
    pts = hex(C + d*1.2, C + d, R, 30)
    draw.polygon(pts, fill=(s, s//2+5, 0, 255))

# Main face - bright gold with manual gradient
face = hex(C, C, R, 30)
# Fill base bright gold
draw.polygon(face, fill=(250, 175, 35, 255))

# Top-left highlight (metallic sheen)
hl = [(C, C-R+10), (C-R+30, C), (C, C)]
draw.polygon(hl, fill=(255, 235, 160, 90))
# Bottom-right shadow
sh = [(C, C+R-10), (C+R-30, C), (C, C)]
draw.polygon(sh, fill=(140, 80, 5, 80))

# Bevel edges: bright top, dark bottom
for i in range(6):
    a, b = face[i], face[(i+1)%6]
    top = a[1] < C and b[1] < C
    left = a[0] < C and b[0] < C
    if top or (left and not top):
        draw.line([a,b], fill=(255, 230, 150, 200), width=4)
    else:
        draw.line([a,b], fill=(120, 60, 0, 160), width=4)

# Inner groove
inner = hex(C, C, R-12, 30)
draw.polygon(inner, outline=(180, 110, 15, 100))

# ===== BITCOIN SYMBOL (SFNS) =====
font_b = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 320)
# Thick drop shadow for 3D depth
for dx, dy, a in [(5,5,120),(9,9,60),(13,13,30)]:
    draw.text((C+dx, C+dy), '₿', font=font_b, fill=(0,0,0,a), anchor='mm')
# Slight inner highlight then main white
draw.text((C-2, C-2), '₿', font=font_b, fill=(255,255,255,90), anchor='mm')
draw.text((C, C), '₿', font=font_b, fill=(255,255,255,255), anchor='mm')

# ===== SOSO CURVED TEXT =====
def load_bold(size):
    for path,idx in [
        ('/System/Library/Fonts/Helvetica.ttc',1),
        ('/System/Library/Fonts/HelveticaNeue.ttc',1),
        ('/System/Library/Fonts/Avenir Next.ttc',1),
        ('/System/Library/Fonts/ArialHB.ttc',1),
        ('/System/Library/Fonts/Helvetica.ttc',0),
    ]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except:
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()

font_s = load_bold(84)
arc_r = 150
sa, ea = -118, -62
step = (ea - sa) / max(1, len('SOSO')-1)
for i, ch in enumerate('SOSO'):
    ang = math.radians(sa + step*i)
    x = C + arc_r*math.cos(ang)
    y = C + arc_r*math.sin(ang)
    draw.text((x+2,y+2), ch, font=font_s, fill=(0,0,0,130), anchor='mm')
    draw.text((x,y), ch, font=font_s, fill=(255,255,255,255), anchor='mm')

# ===== OUTER GLOW =====
blurred = img.filter(ImageFilter.GaussianBlur(radius=16))
base = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
base.paste(blurred, (0,0))
final = Image.alpha_composite(base, img)

out = '/Users/richytakashi/btc-trader/public'
final.save(os.path.join(out, 'logo.png'))
final.resize((128,128), Image.Resampling.LANCZOS).save(os.path.join(out, 'favicon.png'))
print('Logo and favicon generated.')
