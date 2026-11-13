"""Gift-guide collage pins for The Nish Edit Pinterest (1000x1500), product cutouts, no prices."""
import json, os, sys, base64, io, html
from PIL import Image
from playwright.sync_api import sync_playwright
E = html.escape
FS = os.path.abspath('node_modules/@fontsource')
BR, BG, Y, CH = '#6e3e2c', '#eed6b2', '#f6e27f', '#8E1B2C'
def ff(n, f, fam, w=400): return f"@font-face{{font-family:'{fam}';src:url('file://{FS}/{n}/files/{f}');font-weight:{w}}}"
FONTS = ''.join([ff('instrument-serif', 'instrument-serif-latin-400-normal.woff2', 'D'),
                 ff('pinyon-script', 'pinyon-script-latin-400-normal.woff2', 'S'),
                 ff('inter', 'inter-latin-400-normal.woff2', 'T', 400), ff('inter', 'inter-latin-700-normal.woff2', 'T', 700)])
def cut(n):
    im = Image.open(f'img/{n}-cut.png').convert('RGBA'); bb = im.getchannel('A').point(lambda a: 255 if a > 20 else 0).getbbox()
    im = im.crop(bb); b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(), im.size

GUIDES = {
 'stocking': dict(big='Stocking', script='stuffers', sub='small, good and all under $30', items=[('14',''),('16',''),('13',''),('15',''),('17',''),('12','')],
              boxes=[(50, 520, 450, 400), (520, 500, 200, 430), (730, 560, 230, 330), (60, 950, 340, 430), (420, 960, 170, 420), (610, 1010, 330, 360)]),
 'host':  dict(big='Gift guide', script='for the host', sub='for the friend who always has people over', items=[('01', 'cb2'), ('02', 'cb2'), ('03', 'cb2'), ('04', 'parachute')],
              boxes=[(70, 560, 430, 470), (500, 520, 430, 500), (110, 1010, 330, 380), (470, 1040, 470, 330)]),
 'cozy':  dict(big='Gift guide', script='for the cozy one', sub='for the friend who lives in knits', items=[('08', 'avec les filles'), ('06', 'nordstrom'), ('07', 'caslon'), ('04', 'parachute')],
              boxes=[(60, 520, 420, 720), (440, 520, 300, 560), (700, 560, 260, 520), (470, 1080, 460, 300)]),
 'luxe':  dict(big='Gift guide', script='luxe for less', sub='gifts that look more expensive than they are', items=[('11', 'tom ford'), ('06', 'nordstrom'), ('12', 'ilia'), ('02', 'cb2')],
              boxes=[(60, 540, 420, 520), (500, 520, 440, 760), (90, 1080, 330, 300), (520, 1100, 0, 0)]),
}

def pin(g):
    imgs = ''
    for (n, lab), (x, y, w, h) in zip(g['items'], g['boxes']):
        if w == 0: continue
        src, _ = cut(n)
        imgs += (f"<div class=a style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:flex;align-items:center;justify-content:center'>"
                 f"<img src='{src}' style='max-width:100%;max-height:100%;object-fit:contain;filter:drop-shadow(0 10px 18px rgba(80,40,20,.18))'></div>")
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{FONTS}*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1000px;height:1500px;background:{BG};position:relative;overflow:hidden}} .a{{position:absolute}} .cap{{text-transform:uppercase}}</style></head><body>
<div class='a cap' style='left:60px;top:46px;font:700 22px T;color:{BR}'>the nish edit</div>
<div class='a cap' style='right:60px;top:46px;font:700 22px T;color:{BR}'>holiday 2026</div>
<div class=a style='left:60px;top:90px;width:880px;height:2px;background:{BR}'></div>
<div class='a cap' style='left:60px;top:120px;width:880px;font:400 170px/1 D;color:{BR};text-align:center'>{E(g['big'])}</div>
<div class=a style='left:60px;top:285px;width:880px;font:400 104px/1.15 S;color:{BR};text-align:center;white-space:nowrap'>{E(g['script'])}</div>
<div class='a cap' style='left:60px;top:440px;width:880px;font:700 26px T;color:{BR};text-align:center'>{E(g['sub'])}</div>
{imgs}
<div class=a style='left:0;top:1400px;width:1000px;height:100px;background:{BR}'></div>
<div class='a cap' style='left:60px;top:1428px;font:700 30px T;color:{BG}'>shop the gift guide &rarr;</div>
<div class=a style='right:60px;top:1436px;font:400 18px T;color:{BG};opacity:.85'>Affiliate links. I may earn a commission.</div>
</body></html>"""

os.makedirs('gg', exist_ok=True)
with sync_playwright() as pw:
    br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 1000, 'height': 1500})
    for k in (sys.argv[1:] or GUIDES):
        fp = os.path.abspath(f'gg/_{k}.html'); open(fp, 'w').write(pin(GUIDES[k]))
        pg.goto('file://' + fp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(150)
        pg.screenshot(path=f'gg/gift-{k}.png'); os.remove(fp); print(k)
    br.close()
