# -*- coding: utf-8 -*-
"""Usage: python build.py SPEC.json [--out OUT_DIR] [--only ctx,l1,l2,er] [--lo]
Writes OUT_DIR/png/*.png (220 dpi) and OUT_DIR/vsdx/*.vsdx, then prints the finalize report
(overlap / cross / through_shape / label_hits / label_label: all must be 0; in Level 1 store_mode "single"
unavoidable crossings are allowed, minimised and drawn with line jumps)."""
import sys, os, subprocess, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model
def fit(d, m=0.12):
    xs = []; ys = []
    for s in d.shapes.values(): xs += [s.l, s.r]; ys += [s.t, s.b]
    for c in d.conns:
        for p in c.pts: xs.append(p[0]); ys.append(p[1])
        if c.lbox:
            cx, cy, w, h, pt = c.lbox; xs += [cx - w / 2, cx + w / 2]; ys += [cy - h / 2, cy + h / 2]
    for (x, y, t, pt, b) in d.texts: ys += [y - 0.15, y + 0.15]; xs += [x - 1, x + 1]
    dx = m - min(xs); dy = m - min(ys)
    for s in d.shapes.values(): s.x += dx; s.y += dy
    for c in d.conns:
        c.pts = [(p[0] + dx, p[1] + dy) for p in c.pts]
        if c.lbox: cx, cy, w, h, pt = c.lbox; c.lbox = (cx + dx, cy + dy, w, h, pt)
    d.texts = [(x + dx, y + dy, t, pt, b) for (x, y, t, pt, b) in d.texts]
    d.W = max(xs) - min(xs) + 2 * m; d.H = max(ys) - min(ys) + 2 * m
MODS = {'ctx': 'd_ctx', 'l1': 'd_l1', 'l2': 'd_l2', 'er': 'd_er'}
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--out', default='out')
    ap.add_argument('--only', default='ctx,l1,l2,er'); ap.add_argument('--lo', action='store_true')
    a = ap.parse_args(argv)
    model.load(a.spec)
    import importlib, vsdx, finalize
    os.makedirs(os.path.join(a.out, 'png'), exist_ok=True); os.makedirs(os.path.join(a.out, 'vsdx'), exist_ok=True)
    bad = 0
    KEY = {'ctx': 'context', 'l1': 'level1', 'l2': 'level2', 'er': 'er'}
    for k in a.only.split(','):
        if KEY[k] not in model.SPEC: print('skip %s (no "%s" in spec)' % (k, KEY[k])); continue
        ds = importlib.import_module(MODS[k]).build()
        for d in (ds if isinstance(ds, list) else [ds]):
            r = finalize.finalize(d); print(d.name, r)
            # crossings are tolerated only in store_mode "single" (minimised, drawn with line jumps); all else must be 0
            if isinstance(r, dict) and any(v for k_, v in r.items() if not (k_ == 'cross' and getattr(d, 'hops', False))): bad += 1
            fit(d); print('  size %.2f x %.2f in' % (d.W, d.H))
            d.png(os.path.join(a.out, 'png', d.name + '.png'), dpi=220)
            vsdx.write(d, os.path.join(a.out, 'vsdx', d.name + '.vsdx'))
            if a.lo:
                subprocess.run(['soffice', '--headless', '--convert-to', 'png', os.path.join(a.out, 'vsdx', d.name + '.vsdx'),
                                '--outdir', os.path.join(a.out, 'lo')], capture_output=True)
    return bad
if __name__ == '__main__':
    sys.exit(1 if main() else 0)
