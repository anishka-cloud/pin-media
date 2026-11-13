"""Sale carousels in Nish's Canva 'bridal era lookbook' template look (1080x1350).
Usage: python3 render_tpl.py <set>   (set = main | hosting | gifts | cozy | under55 | bigbuys)"""
import json, os, sys, base64, html, io
from PIL import Image
from playwright.sync_api import sync_playwright

E = html.escape
FS = os.path.abspath('node_modules/@fontsource')
BR, BG, Y = '#6e3e2c', '#eed6b2', '#f6e27f'
D = json.load(open('data.json'))
SETS = json.load(open('sets.json'))
ALL = {i['n']: i for i in D['items']}
DATE = D['date']

COVER = {
 'main':    dict(big='On sale', script='Black Friday', sub='early black friday, edited.', label='on sale'),
 'hosting': dict(big='Hosting', script='on sale', sub='hosting season, sorted.', label='on sale'),
 'gifts':   dict(big='Gifts', script='under $120', sub="that don't look it.", label='gift edit'),
 'cozy':    dict(big='Cozy', script='season', sub='the soft stuff, marked down.', label='on sale'),
 'under55': dict(big='Under $55', script='on sale', sub='everything here is under $55.', label='on sale'),
 'bigbuys': dict(big='Big buys', script='marked down', sub='the bigger buys, finally on sale.', label='on sale'),
}
SHORT = {'01': 'Green glass hurricane', '02': 'Alabaster hurricane', '03': 'Taper holder', '04': 'Gauze shams',
         '05': 'Cement floor lamp', '06': 'Camel cashmere', '07': 'Cashmere V-neck', '08': 'Suede barn coat',
         '11': 'Oud Minerale', '12': 'Multi-Stick'}

def ff(name, file, fam, w=400, st='normal'):
    return f"@font-face{{font-family:'{fam}';src:url('file://{FS}/{name}/files/{file}');font-weight:{w};font-style:{st}}}"
FONTS = ''.join([ff('instrument-serif', 'instrument-serif-latin-400-normal.woff2', 'D'),
                 ff('pinyon-script', 'pinyon-script-latin-400-normal.woff2', 'S'),
                 ff('inter', 'inter-latin-400-normal.woff2', 'T', 400), ff('inter', 'inter-latin-600-normal.woff2', 'T', 600),
                 ff('inter', 'inter-latin-700-normal.woff2', 'T', 700)])

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

_cache = {}
def cut(n):
    if n in _cache: return _cache[n]
    p = f'img/{n}-cut.png'
    if os.path.exists(p):
        im = Image.open(p).convert('RGBA'); bb = im.getchannel('A').point(lambda a: 255 if a > 20 else 0).getbbox()
        im = im.crop(bb) if bb else im
    else:
        im = Image.open(f'img/{n}.png').convert('RGBA')
    _cache[n] = uri(im); return _cache[n]
def photo(n): return uri(Image.open(f'img/{n}.png').convert('RGB'))

def page(bg, body):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1350px;background:{bg};position:relative;overflow:hidden}}
.a{{position:absolute}} .cap{{text-transform:uppercase}} img{{display:block}}</style></head><body>{body}</body></html>"""

def header(col, mid, right, top=40, l=44, r=1036, line=106):
    return (f"<div class='a cap' style='left:{l}px;top:{top}px;font:700 22px T;color:{col}'>the nish edit</div>"
            f"<div class='a cap' style='left:668px;top:{top}px;font:700 22px T;color:{col}'>{E(mid)}</div>"
            f"<div class='a cap' style='right:{1080-r}px;top:{top}px;font:700 22px T;color:{col}'>{E(right)}</div>"
            f"<div class=a style='left:{l}px;top:{line}px;width:{r-l}px;height:2px;background:{col}'></div>")

def price_html(it, main, sub, pillbg, pillfg, size=64):
    return (f"<span style='font:700 {size}px T;color:{main};letter-spacing:-.02em'>${E(it['now'])}</span>"
            f"<span style='font:400 {int(size*.5)}px T;color:{sub};text-decoration:line-through;margin-left:18px'>${E(it['was'])}</span>"
            f"<span class=cap style='font:700 {int(size*.42)}px T;color:{pillfg};background:{pillbg};padding:6px 16px;border-radius:30px;margin-left:18px;vertical-align:{int(size*.18)}px'>{E(it['off'])} off</span>")

def fine(it):
    extra = f" · {it['fine']}" if it.get('fine') else ''
    return f"price at {it['retailer']} on {DATE.lower()}, may change{extra}"

def item_dark(it, k, n, label):
    b = (header(BG, label, f"{k:02d}/{n:02d}") +
         f"<div class=a style='left:44px;top:149px;width:992px;height:660px;background:{BG}'></div>"
         f"<div class=a style='left:84px;top:175px;width:912px;height:610px;display:flex;align-items:center;justify-content:center'>"
         f"<img src='{cut(it['n'])}' style='max-width:100%;max-height:100%;object-fit:contain'></div>"
         f"<div class='a cap' data-fit style='left:44px;top:842px;width:992px;height:125px;font:400 120px/1 D;color:{Y};white-space:nowrap'>{E(SHORT[it['n']])}</div>"
         f"<div class=a style='left:44px;top:985px;white-space:nowrap'>{price_html(it, Y, BG, Y, BR)}</div>"
         f"<div class='a cap' style='left:44px;top:1090px;width:992px;font:400 28px/1.15 T;color:{BG}'>{E(it['brand'])} &middot; {E(it['name'])}</div>"
         f"<div class='a cap' style='left:44px;top:1175px;font:700 38px T;color:{BG}'>linked in my bio</div>"
         f"<div class=a style='left:44px;top:1240px;font:400 20px T;color:{BG};opacity:.8'>{E(fine(it))}</div>")
    return page(BR, b)

def item_light(it, k, n, label):
    b = (header(BR, label, f"{k:02d}/{n:02d}") +
         f"<div class='a cap' data-fit style='left:44px;top:150px;width:992px;height:250px;font:400 130px/0.95 D;color:{BR};text-align:right'>{E(SHORT[it['n']])}</div>"
         f"<div class=a style='left:60px;top:420px;width:520px;height:880px;display:flex;align-items:center;justify-content:center'>"
         f"<img src='{cut(it['n'])}' style='max-width:100%;max-height:100%;object-fit:contain'></div>"
         f"<div class=a style='left:610px;top:520px;width:426px;text-align:right'>"
         f"<div style='font:700 76px T;color:{BR};letter-spacing:-.02em'>${E(it['now'])}</div>"
         f"<div style='margin-top:8px'><span style='font:400 32px T;color:{BR};opacity:.75;text-decoration:line-through'>${E(it['was'])}</span>"
         f"<span class=cap style='font:700 26px T;color:{BG};background:{BR};padding:6px 16px;border-radius:30px;margin-left:14px;vertical-align:4px'>{E(it['off'])} off</span></div>"
         f"<div class=cap style='margin-top:36px;font:400 28px/1.15 T;color:{BR}'>{E(it['brand'])} &middot; {E(it['name'])}</div>"
         f"<div class=cap style='margin-top:36px;font:700 38px T;color:{BR}'>linked in my bio</div>"
         f"<div style='margin-top:20px;font:400 20px/1.3 T;color:{BR};opacity:.8'>{E(fine(it))}</div></div>")
    return page(BG, b)

def cover(items, c):
    tiles = [items[i % len(items)]['n'] for i in range(4)]
    pos = [(-30, -41), (543, -41), (-30, 675), (545, 675)]
    bgt = ''.join(f"<img class=a src='{photo(t)}' style='left:{x}px;top:{y}px;width:575px;height:716px;object-fit:cover'>" for t, (x, y) in zip(tiles, pos))
    picks = [it['n'] for it in items[:3]]
    xs = [120, 400, 680]
    prods = ''.join(f"<div class=a style='left:{x}px;top:705px;width:280px;height:540px;display:flex;align-items:flex-end;justify-content:center'>"
                    f"<img src='{cut(p)}' style='max-width:100%;max-height:100%;object-fit:contain'></div>" for x, p in zip(xs, picks))
    b = (f"<div class=a style='left:41px;top:61px;width:997px;height:1228px;background:{BG}'></div>" +
         header(BR, c['label'], DATE, top=100, l=93, r=987, line=181) +
         f"<div class='a cap' data-fit style='left:93px;top:208px;width:893px;height:215px;font:400 206px/1 D;color:{BR};text-align:center;white-space:nowrap'>{E(c['big'])}</div>"
         f"<div class=a data-fit style='left:150px;top:390px;width:803px;height:190px;font:400 170px/1.1 S;color:{BR};text-align:right;white-space:nowrap'>{E(c['script'])}</div>"
         f"<div class=a style='left:514px;top:577px;width:439px;height:2px;background:{BR}'></div>"
         f"<div class='a cap' style='left:420px;top:600px;width:533px;font:700 32px/1.1 T;color:{BR};text-align:right'>{E(c['sub'])}</div>" + prods)
    return page(BR, b)

def end():
    b = (header(BG, 'on sale', DATE) +
         f"<div class='a cap' style='left:44px;top:250px;width:992px;font:400 230px/0.92 D;color:{Y};text-align:center'>All linked<br>in bio</div>"
         f"<div class=a style='left:44px;top:770px;width:992px;font:400 110px/1.1 S;color:{BG};text-align:center'>on sale this week</div>"
         f"<div class='a cap' style='left:44px;top:960px;width:992px;font:700 38px/1.3 T;color:{BG};text-align:center'>tap the link in my bio, then<br>on sale this week &middot; {E(DATE)}</div>"
         f"<div class=a style='left:44px;top:1120px;width:992px;font:700 34px T;color:{Y};text-align:center'>i earn a little from these links</div>"
         f"<div class=a style='left:44px;top:1200px;width:992px;font:400 22px T;color:{BG};opacity:.8;text-align:center'>Sale prices checked {E(DATE)} and can change or end without notice.</div>")
    return page(BR, b)

FIT = """() => { const bad=[]; document.querySelectorAll('[data-fit]').forEach((el,i)=>{ let fs=parseFloat(getComputedStyle(el).fontSize); let n=0;
  while((el.scrollHeight>el.clientHeight+1||el.scrollWidth>el.clientWidth+1)&&fs>14&&n<200){fs-=2;el.style.fontSize=fs+'px';n++;}
  if(el.scrollHeight>el.clientHeight+1||el.scrollWidth>el.clientWidth+1) bad.push(i);}); return bad; }"""

def build(setname):
    ids = [i['n'] for i in D['items']] if setname == 'main' else SETS[setname]['items']
    items = [ALL[n] for n in ids]
    c = COVER[setname]; n = len(items)
    jobs = [('01-cover', cover(items, c))]
    for k, it in enumerate(items, 1):
        jobs.append((f'{k+1:02d}', (item_dark if k % 2 else item_light)(it, k, n, c['label'])))
    jobs.append((f'{n+2:02d}-end', end()))
    out = f'tpl-{setname}'; os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    res = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1350})
        for name, doc in jobs:
            fp = os.path.abspath(f'{out}/_t.html'); open(fp, 'w').write(doc)
            pg.goto('file://' + fp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(120)
            bad = pg.evaluate(FIT); pg.screenshot(path=f'{out}/{name}.png'); os.remove(fp)
            res.append((name, 'ok' if not bad else 'OVERFLOW'))
        br.close()
    return res

if __name__ == '__main__':
    for s in sys.argv[1:]:
        print(s, [r for r in build(s) if r[1] != 'ok'] or 'all ok')
