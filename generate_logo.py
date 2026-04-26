from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 1024
C = SIZE // 2
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ===== HELPERS =====
def ellipse_pts(cx, cy, rx, ry, rot=0):
    pts = []
    for i in range(60):
        a = math.radians(6*i + rot)
        pts.append((cx + rx*math.cos(a), cy + ry*math.sin(a)))
    return pts

def ring(draw, cx, cy, r, col, width=2):
    box = [cx-r, cy-r, cx+r, cy+r]
    draw.arc(box, 0, 360, fill=col, width=width)

# ===== MAGNETIC FIELD ARCS (Gold + Frost) =====
for i, radius in enumerate([360, 430, 500]):
    alpha = int(140 - i*35)
    for a0, a1 in [(-50, 50), (130, 230)]:
        box = [C-radius, C-radius, C+radius, C+radius]
        for layer in range(5):
            col = (*((180, 220, 255) if layer%2 else (212, 175, 55)), max(0, alpha - layer*18))
            draw.arc(box, a0, a1, fill=col, width=2)
            box = [b + (1 if idx<2 else -1) for idx,b in enumerate(box)]

# Flux particles
for t, a_start, a_span, r, sz, color in [
    (0.15, -50, 100, 470, 10, (212, 175, 55)),
    (0.45, -50, 100, 470, 8, (180, 220, 255)),
    (0.75, -50, 100, 470, 10, (212, 175, 55)),
    (0.25, 130, 100, 420, 7, (180, 220, 255)),
    (0.65, 130, 100, 420, 7, (212, 175, 55)),
]:
    ang = math.radians(a_start + t*a_span)
    x = C + r*math.cos(ang)
    y = C + r*math.sin(ang)
    draw.ellipse([x-sz-4, y-sz-4, x+sz+4, y+sz+4], fill=(*color, 70))
    draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(*color, 210))
    draw.ellipse([x-sz//2, y-sz//2, x+sz//2, y+sz//2], fill=(255, 255, 255, 255))

# ===== 3D VIKING SHIELD =====
shield_r = 220
extrude = 14

def circ_pts(cx, cy, r, steps=80):
    return [(cx + r*math.cos(math.radians(360*i/steps)),
             cy + r*math.sin(math.radians(360*i/steps))) for i in range(steps)]

# Elliptical shadow for 3D tilt
shadow = ellipse_pts(C + extrude*1.5, C + extrude*1.2, shield_r+10, shield_r*0.85)
shadow_layer = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
ImageDraw.Draw(shadow_layer).polygon(shadow, fill=(0,0,0,60))
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=12))
img = Image.alpha_composite(img, shadow_layer)
draw = ImageDraw.Draw(img)

# Extrusion sides (depth rings)
for d in range(extrude, 0, -1):
    shade = int(40 + (extrude-d)*9)
    pts = circ_pts(C + d*0.9, C + d*0.7, shield_r, 80)
    # Squash vertically for perspective
    pts = [(x, y + (x-C)*0.05) for x,y in pts]
    draw.polygon(pts, fill=(shade, shade//2+3, 0, 255))

# Main wooden face (slightly squashed for 3D perspective)
face_pts = circ_pts(C, C, shield_r, 80)
face_pts = [(x, y + (x-C)*0.05) for x,y in face_pts]

# Wood base fill
mask = Image.new('L', (SIZE, SIZE), 0)
ImageDraw.Draw(mask).polygon(face_pts, fill=255)

# Radial wood gradient (dark outer, warm inner)
wood = Image.new('RGBA', (SIZE, SIZE))
for y in range(SIZE):
    for x in range(SIZE):
        dx, dy = x-C, y-C
        dist = math.hypot(dx, dy) / shield_r
        if dist > 1: continue
        # wood grain bands
        band = math.sin(dist * 18) * 0.5 + 0.5
        r = int(100 + band*25 - dist*30)
        g = int(65 + band*15 - dist*25)
        b = int(30 + band*8 - dist*15)
        wood.putpixel((x,y), (r,g,b,255))
wood.putalpha(mask)
img = Image.alpha_composite(img, wood)
draw = ImageDraw.Draw(img)

# Iron rim (outer ring)
rim_pts = circ_pts(C, C, shield_r-2, 80)
rim_pts = [(x, y + (x-C)*0.05) for x,y in rim_pts]
draw.polygon(rim_pts, outline=(140, 150, 160, 200))

# Inner iron ring
inner_rim = circ_pts(C, C, shield_r-18, 80)
inner_rim = [(x, y + (x-C)*0.05) for x,y in inner_rim]
draw.polygon(inner_rim, outline=(90, 95, 100, 120))

# Cross bars (behind boss)
bar_w = 22
bar_l = shield_r - 35
# Horizontal bar
hb = [(C-bar_l, C-bar_w), (C+bar_l, C-bar_w), (C+bar_l, C+bar_w), (C-bar_l, C+bar_w)]
draw.polygon(hb, fill=(70, 75, 80, 200))
draw.polygon(hb, outline=(120, 125, 130, 180))
# Vertical bar
vb = [(C-bar_w, C-bar_l), (C+bar_w, C-bar_l), (C+bar_w, C+bar_l), (C-bar_w, C+bar_l)]
draw.polygon(vb, fill=(70, 75, 80, 200))
draw.polygon(vb, outline=(120, 125, 130, 180))

# Central iron boss (dome)
boss_r = 65
boss_pts = circ_pts(C, C, boss_r, 60)
boss_pts = [(x, y + (x-C)*0.05) for x,y in boss_pts]
# Boss gradient (lighter top, darker bottom)
for y in range(SIZE):
    for x in range(SIZE):
        dx, dy = x-C, y-C
        if dx*dx + dy*dy <= boss_r*boss_r:
            t = max(0, min(1, (dy + 30) / (boss_r*1.5)))
            r = int(160 - t*60)
            g = int(165 - t*55)
            b = int(170 - t*50)
            draw.point((x,y), fill=(r,g,b,255))

# Boss rim highlight
draw.polygon(boss_pts, outline=(200, 210, 220, 200), width=3)

# ===== BITCOIN SYMBOL ON BOSS =====
font_b = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 130)
for dx, dy, a in [(3,3,100),(6,6,50)]:
    draw.text((C+dx, C+dy), '₿', font=font_b, fill=(0,0,0,a), anchor='mm')
draw.text((C-1, C-1), '₿', font=font_b, fill=(255,255,255,90), anchor='mm')
draw.text((C, C), '₿', font=font_b, fill=(255, 220, 100, 255), anchor='mm')

# ===== SOSO CURVED ON TOP =====
def load_font(path, size, idx=0):
    try: return ImageFont.truetype(path, size, index=idx)
    except: return None

font_s = None
for p, i in [
    ('/System/Library/Fonts/Helvetica.ttc', 1),
    ('/System/Library/Fonts/HelveticaNeue.ttc', 1),
    ('/System/Library/Fonts/Avenir Next.ttc', 1),
    ('/System/Library/Fonts/ArialHB.ttc', 1),
    ('/System/Library/Fonts/Helvetica.ttc', 0),
]:
    font_s = load_font(p, 78, i)
    if font_s: break
if not font_s:
    font_s = ImageFont.load_default()

arc_r = 158
sa, ea = -115, -65
step = (ea - sa) / max(1, len('SOSO')-1)
for i, ch in enumerate('SOSO'):
    ang = math.radians(sa + step*i)
    x = C + arc_r*math.cos(ang)
    y = C + arc_r*math.sin(ang)
    # Chisel shadow
    draw.text((x+2, y+2), ch, font=font_s, fill=(0,0,0,160), anchor='mm')
    # Frost-white main
    draw.text((x, y), ch, font=font_s, fill=(220, 235, 255, 255), anchor='mm')

# ===== VEGVISIR COMPASS PATTERN (faint background) =====
vg = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
vgd = ImageDraw.Draw(vg)
# Simple 8-pointed star / compass
for angle in range(0, 360, 45):
    rad = math.radians(angle)
    x1 = C + 140*math.cos(rad)
    y1 = C + 140*math.sin(rad)
    x2 = C + 280*math.cos(rad)
    y2 = C + 280*math.sin(rad)
    vgd.line([(x1,y1),(x2,y2)], fill=(180, 220, 255, 20), width=2)
# Cross through center
vgd.line([(C-80,C),(C+80,C)], fill=(180,220,255,25), width=2)
vgd.line([(C,C-80),(C,C+80)], fill=(180,220,255,25), width=2)
img = Image.alpha_composite(img, vg)

# ===== OUTER GLOW =====
blurred = img.filter(ImageFilter.GaussianBlur(radius=14))
base = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
base.paste(blurred, (0,0))
final = Image.alpha_composite(base, img)

out = '/Users/richytakashi/btc-trader/public'
final.save(os.path.join(out, 'logo.png'))
final.resize((128,128), Image.Resampling.LANCZOS).save(os.path.join(out, 'favicon.png'))
print('Viking logo generated.')
