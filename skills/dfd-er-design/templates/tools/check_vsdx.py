# -*- coding: utf-8 -*-
"""Sanity-check a .vsdx diagram before it goes into the report.
Usage: python check_vsdx.py FILE.vsdx [...] [--tol 0.02] [--max-copies 2]
(--max-copies 0 = no limit, only for the older per-process templates of the finished spare-part report)
FAIL (exit 1) on:
- zip/XML not well-formed;
- a group shape without DisplayMode=1 (group fill would hide text / the ER header colour in Visio);
- FLOATING LINES: an arrow or line that is not a real connector (no BeginX/EndX), a connector end that is not glued
  (no <Connect> for BeginX or EndX), a glue to a connection point that does not exist, a connection point that is not on
  the shape's edge, or a connector end that is not on the glued shape's boundary (tolerance --tol inches, default 0.02);
- a data store / external entity drawn more than twice, or a copy without the duplicate mark;
- an ER diagram with more than one line for a table pair.
WARN on every duplicated store/entity (with the count): a copy is allowed only when one copy would cause unavoidable
crossings, overly long lines or clutter (docs/dfd-style.md)."""
import sys, zipfile, collections, re
from lxml import etree
N = '{http://schemas.microsoft.com/office/visio/2012/main}'
def cellv(sh, n):
    c = sh.find(N + "Cell[@N='%s']" % n)
    return None if c is None else c.get('V')
def fnum(sh, n, d=None):
    v = cellv(sh, n)
    try: return float(v)
    except (TypeError, ValueError): return d
def txt(sh):
    t = sh.find(N + 'Text')
    return '' if t is None else ' '.join(''.join(t.itertext()).split())
MAXC = 2
def check(path, tol=0.02):
    z = zipfile.ZipFile(path); assert z.testzip() is None
    for n in z.namelist():
        if n.endswith('.xml') or n.endswith('.rels'): etree.fromstring(z.read(n))
    pages = sorted(n for n in z.namelist() if re.match(r'visio/pages/page\d+\.xml$', n))
    ok = True
    for pg in pages:
        ok &= check_page(path, pg, etree.fromstring(z.read(pg)), tol)
    return ok
def check_page(path, pg, x, tol):
    probs = []; warns = []
    top = x.find(N + 'Shapes')
    tops = list(top) if top is not None else []
    groups = [s for s in x.iter(N + 'Shape') if s.get('Type') == 'Group']
    for g in groups:
        if cellv(g, 'DisplayMode') != '1': probs.append('group %s DisplayMode=%s (need 1)' % (g.get('ID'), cellv(g, 'DisplayMode')))
    label = {}
    for g in groups:
        label[g.get('ID')] = ' '.join(txt(s) for s in g.iter(N + 'Shape') if txt(s))[:40]
    for s in x.iter(N + 'Shape'):
        if s.get('Type') != 'Group' and txt(s) and s.getparent().getparent().tag == N + 'Shapes':
            label.setdefault(s.get('ID'), txt(s)[:40])
    byid = {s.get('ID'): s for s in tops}
    ends = collections.defaultdict(dict)
    for c in x.iter(N + 'Connect'): ends[c.get('FromSheet')][c.get('FromCell')] = (c.get('ToSheet'), c.get('ToCell'))
    # ---------- floating / unglued lines
    def bbox(s):
        px, py, w, h = fnum(s, 'PinX', 0), fnum(s, 'PinY', 0), fnum(s, 'Width', 0), fnum(s, 'Height', 0)
        lx, ly = fnum(s, 'LocPinX', w / 2), fnum(s, 'LocPinY', h / 2)
        return px - lx, py - ly, w, h
    def cpoint(s, cellname):
        m = re.match(r'Connections\.X(\d+)$', cellname or '')
        sec = s.find(N + "Section[@N='Connection']")
        if not m or sec is None: return None
        ix = int(m.group(1)) - 1
        for r in sec.findall(N + 'Row'):
            if r.get('IX') == str(ix): return fnum(r, 'X'), fnum(r, 'Y')
        return None
    nconn = 0
    for s in tops:
        if s.get('Type') == 'Group': continue
        is1d = s.find(N + "Cell[@N='BeginX']") is not None
        arrow = (fnum(s, 'BeginArrow', 0) or 0) != 0 or (fnum(s, 'EndArrow', 0) or 0) != 0
        geo = s.find(N + "Section[@N='Geometry']") is not None
        if not is1d:
            if arrow: probs.append('loose arrow shape %s "%s": draw flows as connectors glued to both shapes' % (s.get('ID'), txt(s)[:30]))
            continue
        nconn += 1; e = ends.get(s.get('ID'), {})
        for endc, xc, yc in (('BeginX', 'BeginX', 'BeginY'), ('EndX', 'EndX', 'EndY')):
            name = 'connector %s "%s" %s' % (s.get('ID'), txt(s)[:30], 'begin' if endc == 'BeginX' else 'end')
            if endc not in e: probs.append('%s is not glued to any shape (floating line end)' % name); continue
            to, tocell = e[endc]; T = byid.get(to)
            if T is None: probs.append('%s glued to unknown/inner shape %s' % (name, to)); continue
            l, b, w, h = bbox(T); px, py = fnum(s, xc), fnum(s, yc)
            cp = cpoint(T, tocell)
            if tocell and tocell.startswith('Connections'):
                if cp is None: probs.append('%s glued to %s.%s which does not exist' % (name, label.get(to, to), tocell)); continue
                cx, cy = cp
                if cx is None or cy is None: continue
                if min(abs(cx), abs(cx - w), abs(cy), abs(cy - h)) > tol:
                    probs.append('%s: connection point %s of "%s" is not on its edge' % (name, tocell, label.get(to, to)))
            if px is None or py is None: continue
            inside = l - tol <= px <= l + w + tol and b - tol <= py <= b + h + tol
            onedge = inside and min(abs(px - l), abs(px - l - w), abs(py - b), abs(py - b - h)) <= tol
            if not onedge:
                probs.append('%s at (%.3f, %.3f) is not on the boundary of "%s" (floating arrow)' % (name, px, py, label.get(to, to)))
    # ---------- duplicated stores / entities
    stores = collections.defaultdict(list); ents = collections.defaultdict(list)
    for s in tops:
        nm = s.get('NameU', '')
        kids = [k for k in s.iter(N + 'Shape') if k is not s]
        sid = next((txt(k) for k in kids if re.match(r'^D\d+$', txt(k))), None)
        if s.get('Type') == 'Group' and sid and not nm.startswith('erent'):
            nsec = len(s.findall(N + "Section[@N='Geometry']")); stores[sid].append(nsec >= 4 if nm.startswith('store') else None)
        elif nm.startswith('ent.'):
            ents[txt(s)].append(len(s.findall(N + "Section[@N='Geometry']")) >= 2)
    for kind, G in (('store', stores), ('entity', ents)):
        for k, marks in sorted(G.items()):
            if len(marks) > 1:
                warns.append('%s %s drawn %d times (allowed only when one copy would cause unavoidable crossings / very long lines)' % (kind, k, len(marks)))
                if MAXC and len(marks) > MAXC: probs.append('%s %s drawn %d times: at most ONE duplicate (%d copies)' % (kind, k, len(marks), MAXC))
                if any(m is False for m in marks): probs.append('%s %s is duplicated but a copy has no duplicate mark' % (kind, k))
    pairs = collections.Counter()
    for sid, e in ends.items():
        if 'BeginX' in e and 'EndX' in e: pairs[frozenset((label.get(e['BeginX'][0], e['BeginX'][0]), label.get(e['EndX'][0], e['EndX'][0])))] += 1
    mx = max(pairs.values()) if pairs else 0
    if 'ER' in path and mx > 1:
        for p, n in pairs.items():
            if n > 1: probs.append('duplicate ER line: ' + ' - '.join(sorted(p)))
    nst = sum(len(v) for v in stores.values())
    print('%s [%s]: groups=%d connectors=%d stores=%d (unique %d) entities=%d (unique %d) %s' % (
        path, pg.split('/')[-1], len(groups), nconn, nst, len(stores), sum(len(v) for v in ents.values()), len(ents),
        'OK' if not probs else 'FAIL'))
    for w_ in warns: print('  WARN', w_)
    for p in probs: print('  FAIL', p)
    return not probs
if __name__ == '__main__':
    a = sys.argv[1:]; tol = 0.02
    if '--tol' in a: i = a.index('--tol'); tol = float(a[i + 1]); del a[i:i + 2]
    if '--max-copies' in a: i = a.index('--max-copies'); MAXC = int(a[i + 1]); del a[i:i + 2]
    ok = all([check(p, tol) for p in a]); sys.exit(0 if ok else 1)
