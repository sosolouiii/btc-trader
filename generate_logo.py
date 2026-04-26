from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 1024
C = SIZE // 2
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

def load_bold(size):
    for p, i in [
        ('/System/Library/Fonts/Helvetica.ttc', 1),
        ('/System/Library/Fonts/HelveticaNeue.ttc', 1),
        ('/System/Library/Fonts/Avenir Next.ttc', 1),
        ('/System/Library/Fonts/ArialHB.ttc', 1),
        ('/System/Library/Fonts/Helvetica.ttc', 0),
    ]:
        try: return ImageFont.truetype(p, size, index=i)
        except:
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# ===== MAGNETIC FIELD ARCS =====
gold = (212, 175, 55)
for i, radius in enumerate([340, 410, 480]):
    alpha = int(130 - i*28)
    for a0, a1 in [(-50, 50), (130, 230)]:
        box = [C-radius, C-radius, C+radius, C+radius]
        for layer in range(4):
            c = (*gold, max(0, alpha-layer*22))
            draw.arc(box, a0, a1, fill=c, width=2)
            box = [b+(1 if idx<2 else -1) for idx,b in enumerate(box)]

# Flux particles
for t, sa, spn, r, sz, col in [
    (0.2, -50, 100, 460, 10, gold),
    (0.5, -50, 100, 460, 8, (180,220,255)),
    (0.8, -50, 100, 460, 10, gold),
    (0.3, 130, 100, 410, 7, (180,220,255)),
    (0.7, 130, 100, 410, 7, gold),
]:
    a = math.radians(sa + t*spn)
    x, y = C + r*math.cos(a), C + r*math.sin(a)
    draw.ellipse([x-sz-4,y-sz-4,x+sz+4,y+sz+4], fill=(*col,60))
    draw.ellipse([x-sz,y-sz,x+sz,y+sz], fill=(*col,200))

# ===== PERFECT CIRCLE SHIELD =====
shield_r = 215
extrude = 12

# Drop shadow
shadow = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
sd = ImageDraw.Draw(shadow)
for d in range(6):
    sd.ellipse([C-shield_r-8+d*2, C-shield_r-4+d*2, C+shield_r+8+d*2, C+shield_r+4+d*2],
               fill=(0,0,0,15))
shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
img = Image.alpha_composite(img, shadow)
draw = ImageDraw.Draw(img)

# Extrusion
for d in range(extrude, 0, -1):
    shade = int(30 + (extrude-d)*10)
    draw.ellipse([C-shield_r+d, C-shield_r+d, C+shield_r+d, C+shield_r+d],
                 fill=(shade, shade//2, 0, 255))

# Wood face
mask = Image.new('L', (SIZE, SIZE), 0)
ImageDraw.Draw(mask).ellipse([C-shield_r, C-shield_r, C+shield_r, C+shield_r], fill=255)

wood = Image.new('RGBA', (SIZE, SIZE))
for y in range(SIZE):
    for x in range(SIZE):
        dx, dy = x-C, y-C
        d = math.hypot(dx, dy)
        if d > shield_r: continue
        t = d / shield_r
        band = math.sin(t*18)*0.5 + 0.5
        r = int(108 + band*20 - t*20)
        g = int(68 + band*10 - t*15)
        b = int(32 + band*5 - t*8)
        wood.putpixel((x,y), (r,g,b,255))
wood.putalpha(mask)
img = Image.alpha_composite(img, wood)
draw = ImageDraw.Draw(img)

# Iron rim
for w, col in [(4, (130,138,145,200)), (2, (70,75,80,150))]:
    draw.ellipse([C-shield_r+w, C-shield_r+w, C+shield_r-w, C+shield_r-w],
                 outline=col, width=1)

# Inner ring
ir = shield_r - 22
draw.ellipse([C-ir, C-ir, C+ir, C+ir], outline=(90,95,100,90), width=1)

# Cross bars
bw, bl = 22, shield_r - 38
draw.rectangle([C-bl, C-bw, C+bl, C+bw], fill=(60,65,70,190))
draw.rectangle([C-bl, C-bw, C+bl, C+bw], outline=(105,112,120,140), width=2)
draw.rectangle([C-bw, C-bl, C+bw, C+bl], fill=(60,65,70,190))
draw.rectangle([C-bw, C-bl, C+bw, C+bl], outline=(105,112,120,140), width=2)

# ===== STRAIGHT TEXT: SOSO (top) + BTC (bottom) =====
font_soso = load_bold(82)
font_btc = load_bold(68)

# SOSO at top
draw.text((C+3, C-135+3), 'SOSO', font=font_soso, fill=(0,0,0,130), anchor='mm')
draw.text((C, C-135), 'SOSO', font=font_soso, fill=(255, 230, 150, 255), anchor='mm')

# BTC at bottom
draw.text((C+3, C+135+3), 'BTC', font=font_btc, fill=(0,0,0,130), anchor='mm')
draw.text((C, C+135), 'BTC', font=font_btc, fill=(220, 235, 255, 255), anchor='mm')

# ===== CENTER IRON BOSS =====
boss_r = 58
for y in range(SIZE):
    for x in range(SIZE):
        dx, dy = x-C, y-C
        d2 = dx*dx + dy*dy
        if d2 > boss_r*boss_r: continue
        t = max(0, min(1, (dy+22)/(boss_r*1.5)))
        r = int(160 - t*50)
        g = int(165 - t*45)
        b = int(170 - t*40)
        draw.point((x,y), fill=(r,g,b,255))

# Boss rim
draw.ellipse([C-boss_r, C-boss_r, C+boss_r, C+boss_r],
             outline=(200,210,220,200), width=3)
draw.ellipse([C-boss_r+2, C-boss_r+2, C+boss_r-2, C+boss_r-2],
             outline=(80,85,90,100), width=1)

# ===== BITCOIN SYMBOL =====
font_sym = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 115)
for dx,dy,a in [(3,3,100),(6,6,50)]:
    draw.text((C+dx,C+dy), '₿', font=font_sym, fill=(0,0,0,a), anchor='mm')
draw.text((C-1,C-1), '₿', font=font_sym, fill=(255,255,255,90), anchor='mm')
draw.text((C,C), '₿', font=font_sym, fill=(250, 210, 80, 255), anchor='mm')

# ===== VEGVISIR =====
vg = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
vgd = ImageDraw.Draw(vg)
for ang in range(0, 360, 45):
    rad = math.radians(ang)
    vgd.line([(C+140*math.cos(rad), C+140*math.sin(rad)),
              (C+270*math.cos(rad), C+270*math.sin(rad))],
             fill=(180,220,255,15), width=2)
vgd.line([(C-80,C),(C+80,C)], fill=(180,220,255,18), width=2)
vgd.line([(C,C-80),(C,C+80)], fill=(180,220,255,18), width=2)
img = Image.alpha_composite(img, vg)

# ===== GLOW =====
bl = img.filter(ImageFilter.GaussianBlur(radius=12))
base = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
base.paste(bl, (0,0))
final = Image.alpha_composite(base, img)

out = '/Users/richytakashi/btc-trader/public'
final.save(os.path.join(out, 'logo.png'))
final.resize((128,128), Image.Resampling.LANCZOS).save(os.path.join(out, 'favicon.png'))
print('SOSO BTC logo done.')
