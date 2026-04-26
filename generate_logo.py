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
    alpha = int(110 - i*25)
    for a0, a1 in [(-50, 50), (130, 230)]:
        box = [C-radius, C-radius, C+radius, C+radius]
        for layer in range(3):
            c = (*gold, max(0, alpha-layer*20))
            draw.arc(box, a0, a1, fill=c, width=2)
            box = [b+(1 if idx<2 else -1) for idx,b in enumerate(box)]

# ===== SHIELD (smaller, so text dominates) =====
shield_r = 170
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
    shade = int(28 + (extrude-d)*10)
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
        band = math.sin(t*16)*0.5 + 0.5
        r = int(110 + band*18 - t*18)
        g = int(68 + band*8 - t*12)
        b = int(32 + band*4 - t*6)
        wood.putpixel((x,y), (r,g,b,255))
wood.putalpha(mask)
img = Image.alpha_composite(img, wood)
draw = ImageDraw.Draw(img)

# Rim
for w, col in [(5, (140,148,155,220)), (2, (60,65,70,140))]:
    draw.ellipse([C-shield_r+w, C-shield_r+w, C+shield_r-w, C+shield_r-w],
                 outline=col, width=1)

# Inner ring
ir = shield_r - 16
draw.ellipse([C-ir, C-ir, C+ir, C+ir], outline=(90,95,100,80), width=1)

# ===== GIANT TEXT: SOSO =====
font_soso = load_bold(150)
bbox = font_soso.getbbox('SOSO')
w = bbox[2]-bbox[0]
# Big gold SOSO
draw.text((C+5, C-35+5), 'SOSO', font=font_soso, fill=(0,0,0,140), anchor='mm')
# Main with gold stroke
draw.text((C, C-35), 'SOSO', font=font_soso, fill=(255, 220, 120, 255), anchor='mm')
# Slight outline
for ox, oy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
    draw.text((C+ox, C-35+oy), 'SOSO', font=font_soso, fill=(180, 140, 40, 60), anchor='mm')
draw.text((C, C-35), 'SOSO', font=font_soso, fill=(255, 235, 160, 255), anchor='mm')

# ===== GIANT TEXT: BTC =====
font_btc = load_bold(130)
draw.text((C+5, C+65+5), 'BTC', font=font_btc, fill=(0,0,0,140), anchor='mm')
draw.text((C, C+65), 'BTC', font=font_btc, fill=(210, 230, 255, 255), anchor='mm')
# Outline
for ox, oy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
    draw.text((C+ox, C+65+oy), 'BTC', font=font_btc, fill=(100, 120, 150, 60), anchor='mm')
draw.text((C, C+65), 'BTC', font=font_btc, fill=(230, 245, 255, 255), anchor='mm')

# ===== SMALL CENTER BITCOIN SYMBOL (between texts) =====
font_sym = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 72)
for dx,dy,a in [(2,2,80),(4,4,40)]:
    draw.text((C+dx,C-2+dy), '₿', font=font_sym, fill=(0,0,0,a), anchor='mm')
draw.text((C,C-2), '₿', font=font_sym, fill=(250, 210, 80, 255), anchor='mm')

# ===== GLOW =====
bl = img.filter(ImageFilter.GaussianBlur(radius=14))
base = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
base.paste(bl, (0,0))
final = Image.alpha_composite(base, img)

out = '/Users/richytakashi/btc-trader/public'
final.save(os.path.join(out, 'logo.png'))
final.resize((128,128), Image.Resampling.LANCZOS).save(os.path.join(out, 'favicon.png'))
print('Big SOSO BTC logo done.')
