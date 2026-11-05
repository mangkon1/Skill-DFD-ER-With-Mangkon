# -*- coding: utf-8 -*-
"""Tiny diagram engine: shapes + orthogonal connectors -> PIL PNG preview and Visio .vsdx"""
from PIL import Image, ImageDraw, ImageFont, features
import math, os, sys, zipfile, io
from xml.sax.saxutils import escape

def _find_font(names):
    """TH Sarabun New (SIPA). Set DFDER_FONT_DIR to the folder that holds the .ttf files."""
    dirs = [os.environ.get('DFDER_FONT_DIR', ''), os.path.expanduser('~/.fonts/sipa'), os.path.expanduser('~/.fonts'),
            '/usr/share/fonts/truetype/thai', '/usr/share/fonts/truetype', 'C:/Windows/Fonts',
            os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts'), '/Library/Fonts', os.path.expanduser('~/Library/Fonts')]
    for d in dirs:
        for n in names:
            p = os.path.join(d, n)
            if d and os.path.isfile(p): return p
    raise FileNotFoundError('TH Sarabun New font not found (%s); install it or set DFDER_FONT_DIR' % names[0])
FONT_R = _find_font(['THSarabunNew.ttf', 'THSarabunNew-Regular.ttf'])
FONT_B = _find_font(['THSarabunNew Bold.ttf', 'THSarabunNew-Bold.ttf', 'THSarabunNewBold.ttf'])
# Thai text: Pillow needs libraqm (+FriBiDi) to place vowels/tone marks. Windows/macOS wheels often load without
# FriBiDi -> raqm silently off -> BASIC layout draws marks in the wrong place (they even land on the line above).
# Then we place every mark ourselves (thai_text) so the PNG still reads correctly. Visio renders .vsdx text itself.
HAS_RAQM = features.check('raqm') and not os.environ.get('DFDER_NO_RAQM')   # DFDER_NO_RAQM=1 tests the fallback
ENGINE = ImageFont.Layout.RAQM if HAS_RAQM else ImageFont.Layout.BASIC
if not HAS_RAQM and not os.environ.get('DFDER_QUIET'):
    print('WARNING: Pillow has no libraqm; using the built-in Thai mark placement for PNG text. '
          'Open the PNG and check tone marks (see docs/dfd-style.md, Thai text).', file=sys.stderr)
# arrowheads: 'small' (default since 3.3) or 'legacy' (spare-part report figures); set by the spec key "arrow"
ARROWS = {'small': {'png': (0.075, 0.03), 'visio': 0}, 'legacy': {'png': (0.11, 0.045), 'visio': 1}}
ARROW = dict(ARROWS['small'])
K = 1.5295   # layout pt -> real TH Sarabun New pt (same visual size)
VFONT = 'TH Sarabun New'
_fc = {}
def font(pt, bold=False, dpi=72):
    k = (pt, bold, dpi)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONT_B if bold else FONT_R, int(round(pt * K * dpi / 72)), layout_engine=ENGINE)
    return _fc[k]

UP_V = set('\u0e31\u0e34\u0e35\u0e36\u0e37\u0e47\u0e4d')       # upper vowels + nikhahit
TONE = set('\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e4e')             # tone marks, thanthakhat
LOW = set('\u0e38\u0e39\u0e3a')                                 # sara u, uu, phinthu
ASC = set('\u0e1b\u0e1d\u0e1f\u0e2c')                           # ascender consonants (marks move left)
def clusters(s):
    s = s.replace('\u0e33', '\u0e4d\u0e32')                         # sara am = nikhahit + sara aa
    out = []
    for ch in s:
        if (ch in UP_V or ch in TONE or ch in LOW) and out: out[-1][1].append(ch)
        else: out.append([ch, []])
    return out
_ink = {}
def ink(f, ch):
    """real ink box of one glyph relative to its origin (left, baseline): BASIC getbbox is not reliable for marks"""
    k = (id(f), ch)
    if k not in _ink:
        n = f.size * 4; im = Image.new('L', (n, n), 0)
        ImageDraw.Draw(im).text((n // 2, n // 2), ch, font=f, fill=255, anchor='ls')
        b = im.getbbox() or (n // 2, n // 2, n // 2, n // 2)
        _ink[k] = (b[0] - n // 2, b[1] - n // 2, b[2] - n // 2, b[3] - n // 2)
    return _ink[k]
def thai_text(g, xy, s, f, anchor='mm', fill='black'):
    """draw one line with explicit Thai mark placement (only used when raqm is unavailable)"""
    if not s: return
    x, y = xy; asc, desc = f.getmetrics(); size = f.size
    cl = clusters(s)
    W = sum(f.getlength(b) for b, m in cl)
    x0 = x - W / 2 if anchor[0] == 'm' else x - W if anchor[0] == 'r' else x
    yb = y + (asc - desc) / 2 if anchor[1] == 'm' else y + asc if anchor[1] == 't' else y
    xt = ink(f, '\u0e19')[1]; gap = 0.035 * size
    pen = x0
    for b, marks in cl:
        g.text((pen, yb), b, font=f, fill=fill, anchor='ls')
        bb = ink(f, b)
        tr = pen + bb[2] - (0.3 * (bb[2] - bb[0]) if b in ASC else 0)
        top = yb + xt - gap; bot = yb + gap
        ups = [m for m in marks if m in UP_V] + [m for m in marks if m in TONE]
        for m in ups:
            mb = ink(f, m); oy = top - mb[3]
            g.text((tr - mb[2], oy), m, font=f, fill=fill, anchor='ls'); top = oy + mb[1] - gap
        for m in marks:
            if m in LOW:
                mb = ink(f, m); oy = bot - mb[1]
                g.text((tr - mb[2], oy), m, font=f, fill=fill, anchor='ls'); bot = oy + mb[3] + gap
        pen += f.getlength(b)
def put_text(g, xy, s, f, anchor='mm', fill='black'):
    if HAS_RAQM: g.text(xy, s, font=f, fill=fill, anchor=anchor)
    else: thai_text(g, xy, s, f, anchor, fill)

def textw(s, pt, bold=False):
    f = font(pt, bold, 720)
    if not HAS_RAQM: return sum(f.getlength(b) for b, m in clusters(s)) / 720.0
    return f.getlength(s) / 720.0          # inches

LINE = lambda pt: pt / 72.0 * 1.22

BREAKS = ('หนึ่ง', 'การใช้งาน', 'พร้อม', 'เข้าทะเบียน', 'รอช่าง', 'ว่า', 'และ', 'ที่', 'ของ', 'ตาม', 'สถานะ', 'ใน', 'ส่ง', 'หัวหน้า', 'เป็น', 'ให้', 'จาก', 'อุปกรณ์', 'รุ่น', 'ข้อมูล', 'เครื่อง', 'ผล')
def split_item(item, maxw, pt):
    if textw(item, pt) <= maxw: return [item]
    best = None
    for i in range(1, len(item)):
        if item[i] == ' ':
            a, b = item[:i], item[i + 1:]
        elif any(item.startswith(w, i) for w in BREAKS):
            a, b = item[:i], item[i:]
        else: continue
        if len(a) < 4 or len(b) < 4: continue
        m = max(textw(a, pt), textw(b, pt))
        if best is None or m < best[0]: best = (m, a, b)
    if not best: return [item]
    return split_item(best[1], maxw, pt) + split_item(best[2], maxw, pt)

def wrap(labels, maxw, pt, sep=', '):
    out = []
    for l in labels:
        parts = split_item(l, maxw, pt)
        for k, part in enumerate(parts):
            if k == 0 and out and out[-1] is not None and textw(out[-1] + sep + part, pt) <= maxw and len(parts) == 1:
                out[-1] = out[-1] + sep + part
            else:
                out.append(part)
    return out

class Shape:
    def __init__(s, sid, kind, x, y, w, h, name='', num='', dup=False, rows=None, pt=16):
        s.id, s.kind, s.x, s.y, s.w, s.h = sid, kind, x, y, w, h
        s.name, s.num, s.dup, s.rows, s.pt = name, num, dup, rows or [], pt
        s.ports = []                         # list of (lx, ly) local coords from top-left (y down)
    @property
    def l(s): return s.x - s.w / 2
    @property
    def r(s): return s.x + s.w / 2
    @property
    def t(s): return s.y - s.h / 2
    @property
    def b(s): return s.y + s.h / 2
    def side_pt(s, side, f):
        if side == 'L': return (s.l, s.t + f * s.h)
        if side == 'R': return (s.r, s.t + f * s.h)
        if side == 'T': return (s.l + f * s.w, s.t)
        if side == 'B': return (s.l + f * s.w, s.b)
    def add_port(s, p):
        lx, ly = p[0] - s.l, p[1] - s.t
        for i, q in enumerate(s.ports):
            if abs(q[0] - lx) < 1e-6 and abs(q[1] - ly) < 1e-6: return i
        s.ports.append((lx, ly)); return len(s.ports) - 1

class Conn:
    def __init__(c, a, b, sa, sb, labels=(), ta=None, tb=None, via=None, lab=None, ea=13, ba=0):
        c.a, c.b, c.sa, c.sb, c.labels = a, b, sa, sb, list(labels)
        c.ta, c.tb, c.via, c.lab = ta, tb, via, lab or {}
        c.ea, c.ba = ea, ba
        c.pts = []; c.lbox = None

class Diagram:
    def __init__(d, name, W, H, lpt=14):
        d.name, d.W, d.H, d.lpt = name, W, H, lpt
        d.shapes = {}; d.conns = []; d.texts = []
    def add(d, *a, **k):
        s = Shape(*a, **k); d.shapes[s.id] = s; return s
    def conn(d, *a, **k):
        c = Conn(*a, **k); d.conns.append(c); return c
    # ---------------------------------------------------------- layout
    def solve(d):
        for s_ in d.shapes.values(): s_.ports = []
        # automatic port fractions
        sides = {}
        for c in d.conns:
            for end in ('a', 'b'):
                sid = getattr(c, end); side = getattr(c, 's' + end); t = getattr(c, 't' + end)
                if t is None: sides.setdefault((sid, side), []).append((c, end))
        for (sid, side), lst in sides.items():
            def key(item):
                c, end = item
                other = d.shapes[c.b if end == 'a' else c.a]
                oend = 'b' if end == 'a' else 'a'
                ot = getattr(c, 't' + oend); osd = getattr(c, 's' + oend)
                if ot is not None and not c.via:
                    op = other.side_pt(osd, ot)
                    return op[1] if side in 'LR' else op[0]
                if ot is not None and c.via and side in 'LR':
                    op = other.side_pt(osd, ot)
                    return op[1]
                v = c.via
                if side in 'LR':
                    oy = other.y
                    if v and end == 'a' and v[0][0] == 'y': oy = v[0][1]
                    if v and end == 'b':
                        ys = [q[1] for q in v if q[0] == 'y']
                        if ys: oy = ys[-1]
                    return oy
                ox = other.x
                if v and end == 'a' and v[0][0] == 'x': ox = v[0][1]
                if v and end == 'b':
                    xs = [q[1] for q in v if q[0] == 'x']
                    if xs: ox = xs[-1]
                return ox
            lst.sort(key=key)
            n = len(lst)
            for i, (c, end) in enumerate(lst):
                setattr(c, 't' + end, (i + 1) / (n + 1))
        for c in d.conns:
            A, B = d.shapes[c.a], d.shapes[c.b]
            for S_, sd, t_ in ((A, c.sa, c.ta), (B, c.sb, c.tb)):
                if not (0.0 < t_ < 1.0):   # hard rule: both ends sit ON a shape edge (no floating arrows)
                    raise ValueError('%s: flow %s -> %s %s end is off the %s edge of %s (fraction %.3f); move the shape or '
                                     'the flow so both ends touch the boxes' % (d.name, c.a, c.b, c.labels[:1], sd, S_.id, t_))
            pa = A.side_pt(c.sa, c.ta); pb = B.side_pt(c.sb, c.tb)
            pts = [pa]
            cur = pa
            if c.via:
                for ax, v in c.via:
                    cur = (v, cur[1]) if ax == 'x' else (cur[0], v)
                    pts.append(cur)
                if c.sb in 'LR':
                    if abs(cur[1] - pb[1]) > 1e-6: pts.append((cur[0], pb[1]))
                else:
                    if abs(cur[0] - pb[0]) > 1e-6: pts.append((pb[0], cur[1]))
                pts.append(pb)
            else:
                ha, hb = c.sa in 'LR', c.sb in 'LR'
                if ha and hb:
                    if abs(pa[1] - pb[1]) > 1e-6:
                        mx = (pa[0] + pb[0]) / 2
                        pts += [(mx, pa[1]), (mx, pb[1])]
                elif not ha and not hb:
                    if abs(pa[0] - pb[0]) > 1e-6:
                        my = (pa[1] + pb[1]) / 2
                        pts += [(pa[0], my), (pb[0], my)]
                elif ha and not hb:
                    pts.append((pb[0], pa[1]))
                else:
                    pts.append((pa[0], pb[1]))
                pts.append(pb)
            # dedupe
            q = [pts[0]]
            for p in pts[1:]:
                if abs(p[0] - q[-1][0]) > 1e-6 or abs(p[1] - q[-1][1]) > 1e-6: q.append(p)
            r = [q[0]]
            for i in range(1, len(q) - 1):
                a, b, e = r[-1], q[i], q[i + 1]
                if (abs(a[0] - b[0]) < 1e-6 and abs(b[0] - e[0]) < 1e-6) or (abs(a[1] - b[1]) < 1e-6 and abs(b[1] - e[1]) < 1e-6): continue
                r.append(b)
            r.append(q[-1])
            c.pts = r
            c.pa_i = A.add_port(pa); c.pb_i = B.add_port(pb)
            d.place_label(c)
    def place_label(d, c):
        if not c.labels: return
        pt = c.lab.get('pt', d.lpt)
        lh = LINE(pt) * 1.05
        w = max(textw(s, pt) for s in c.labels) + 0.08
        h = lh * len(c.labels) + 0.04
        segs = list(zip(c.pts[:-1], c.pts[1:]))
        if 'seg' in c.lab: si = c.lab['seg']
        else:
            hs = [(abs(p[0] - q[0]), i) for i, (p, q) in enumerate(segs) if abs(p[1] - q[1]) < 1e-6]
            si = max(hs)[1] if hs else 0
        p, q = segs[si]
        at = c.lab.get('at', 0.5)
        mx, my = p[0] + (q[0] - p[0]) * at, p[1] + (q[1] - p[1]) * at
        side = c.lab.get('side')
        if abs(p[1] - q[1]) < 1e-6:          # horizontal
            side = side or 'above'
            cx = mx; cy = my - h / 2 - 0.02 if side == 'above' else my + h / 2 + 0.02
        else:
            side = side or 'right'
            cy = my; cx = mx + w / 2 + 0.04 if side == 'right' else mx - w / 2 - 0.04
        if 'end' in c.lab:
            e = c.pts[0] if c.lab['end'] == 'a' else c.pts[-1]
            o = c.pts[1] if c.lab['end'] == 'a' else c.pts[-2]
            sg = 1 if o[0] > e[0] else -1
            cx = e[0] + sg * (w / 2 + c.lab.get('gap', 0.06))
        if 'cx' in c.lab: cx = c.lab['cx']
        cx += c.lab.get('dx', 0); cy += c.lab.get('dy', 0)
        c.lbox = (cx, cy, w, h, pt)
    # ---------------------------------------------------------- PNG
    def png(d, path, dpi=200, margin=0.1):
        W, H = int((d.W) * dpi), int((d.H) * dpi)
        im = Image.new('RGB', (W, H), 'white'); g = ImageDraw.Draw(im)
        P = lambda x, y: (x * dpi, y * dpi)
        lw = max(1, int(dpi / 100))
        def ctext(s, cx, cy, pt, bold=False, maxw=None):
            f = font(pt, bold, dpi)
            lines = s.split('\n')
            lh = LINE(pt) * dpi * 1.05
            tot = lh * len(lines)
            for i, ln in enumerate(lines):
                y = cy * dpi - tot / 2 + lh * (i + 0.5)
                put_text(g, (cx * dpi, y), ln, f, 'mm')
        for s in d.shapes.values():
            if s.kind == 'proc':
                g.rectangle([P(s.l, s.t), P(s.r, s.b)], outline='black', width=lw)
                hh = getattr(s, 'hh', 0.32)
                g.line([P(s.l, s.t + hh), P(s.r, s.t + hh)], fill='black', width=lw)
                ctext(s.num, s.x, s.t + hh / 2, s.pt, True)
                ctext(s.name, s.x, s.t + hh + (s.h - hh) / 2, s.pt)
            elif s.kind == 'ent':
                g.rectangle([P(s.l, s.t), P(s.r, s.b)], outline='black', width=lw)
                if s.dup:
                    g.line([P(s.l, s.t + 0.16), P(s.l + 0.16, s.t)], fill='black', width=lw)
                ctext(s.name, s.x, s.y, s.pt)
            elif s.kind == 'store':
                iw = getattr(s, 'iw', 0.45)
                g.line([P(s.r, s.t), P(s.l, s.t), P(s.l, s.b), P(s.r, s.b)], fill='black', width=lw)
                g.line([P(s.l + iw, s.t), P(s.l + iw, s.b)], fill='black', width=lw)
                if s.dup:
                    g.line([P(s.l + 0.07, s.t), P(s.l + 0.07, s.b)], fill='black', width=lw)
                ctext(s.num, s.l + iw / 2 + (0.035 if s.dup else 0), s.y, s.pt, True)
                ctext(s.name, s.l + iw + (s.w - iw) / 2, s.y, s.pt)
            elif s.kind == 'erent':
                rh = s.rh
                g.rectangle([P(s.l, s.t), P(s.r, s.b)], outline='black', width=lw)
                g.rectangle([P(s.l, s.t), P(s.r, s.t + rh)], outline='black', width=lw, fill=(0xBD, 0xD7, 0xEE))
                ctext(s.name, s.x, s.t + rh / 2, s.pt, True)
                g.line([P(s.l + 0.42, s.t + rh), P(s.l + 0.42, s.b)], fill='black', width=lw)
                f = font(s.pt - 2, False, dpi)
                for i, (k, a) in enumerate(s.rows):
                    yy = s.t + rh * (i + 1.5)
                    if k: put_text(g, P(s.l + 0.21, yy), k, font(s.pt - 2, True, dpi), 'mm')
                    put_text(g, P(s.l + 0.5, yy), a, f, 'lm')
                    if k and 'PK' in k:
                        tw = textw(a, s.pt - 2) * dpi
                        g.line([P(s.l + 0.5, yy + 0.09), (P(s.l + 0.5, 0)[0] + tw, (yy + 0.09) * dpi)], fill='black', width=1)
        for c in d.conns:
            g.line([P(*p) for p in c.pts], fill='black', width=lw)
            if c.ea == 13: d._arrow(g, c.pts[-2], c.pts[-1], dpi)
            if c.ba == 13: d._arrow(g, c.pts[1], c.pts[0], dpi)
            for code, p0, p1 in ((c.ba, c.pts[0], c.pts[1]), (c.ea, c.pts[-1], c.pts[-2])):
                if code in (24, 25, 27, 28, 29, 30): d._crow(g, code, p0, p1, dpi, lw)
            if c.lbox:
                cx, cy, w, h, pt = c.lbox
                ctext('\n'.join(c.labels), cx, cy, pt)
        for (x, y, s, pt, b) in d.texts:
            ctext(s, x, y, pt, b)
        im.save(path)
    def _arrow(d, g, p, q, dpi):
        ang = math.atan2(q[1] - p[1], q[0] - p[0]); L, Wd = ARROW['png']
        bx, by = q[0] - L * math.cos(ang), q[1] - L * math.sin(ang)
        nx, ny = -math.sin(ang) * Wd, math.cos(ang) * Wd
        g.polygon([(q[0] * dpi, q[1] * dpi), ((bx + nx) * dpi, (by + ny) * dpi), ((bx - nx) * dpi, (by - ny) * dpi)], fill='black')
    def _crow(d, g, code, p0, p1, dpi, lw):
        # p0 = end point on entity, p1 = next point (direction away from entity)
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); ux, uy = math.cos(ang), math.sin(ang); nx, ny = -uy, ux
        P = lambda a, b: ((p0[0] + ux * a + nx * b) * dpi, (p0[1] + uy * a + ny * b) * dpi)
        bar = lambda a: g.line([P(a, -0.07), P(a, 0.07)], fill='black', width=lw)
        crow = lambda: (g.line([P(0, -0.08), P(0.16, 0)], fill='black', width=lw), g.line([P(0, 0.08), P(0.16, 0)], fill='black', width=lw))
        circ = lambda a: g.ellipse([P(a - 0.045, -0.045)[0] if False else (p0[0] + ux * a) * dpi - 0.045 * dpi, (p0[1] + uy * a) * dpi - 0.045 * dpi, (p0[0] + ux * a) * dpi + 0.045 * dpi, (p0[1] + uy * a) * dpi + 0.045 * dpi], outline='black', fill='white', width=lw)
        if code == 25: bar(0.10); bar(0.16)
        elif code == 24: bar(0.12)
        elif code == 27: crow()
        elif code == 28: crow(); bar(0.20)
        elif code == 29: crow(); circ(0.25)
        elif code == 30: bar(0.10); circ(0.22)
