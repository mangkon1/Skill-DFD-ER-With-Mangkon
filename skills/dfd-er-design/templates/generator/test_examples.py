# -*- coding: utf-8 -*-
"""Regression test for the default Level 1 layout (store_mode "single", compact, v3.4) on the worked examples.
Usage: python test_examples.py   (exit 0 = all pass)
Each example must build with finalize all 0, pass check_vsdx (0 crossings), draw every entity once, draw at most one
copy per store, and stay compact (width <= 1.7 x height)."""
import os, sys, subprocess, tempfile, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
EXAMPLES = ['booking/booking.json', 'library/library.json']
def run(spec):
    import importlib, model, finalize, build, d_l1
    model.load(spec)
    out = io.StringIO()
    with contextlib.redirect_stdout(out): d = d_l1.build()
    r = finalize.finalize(d); build.fit(d)
    ent = [s.name for s in d.shapes.values() if s.kind == 'ent']
    st = {}
    for s in d.shapes.values():
        if s.kind == 'store': st[s.num] = st.get(s.num, 0) + 1
    probs = []
    if any(r.values()): probs.append('finalize %s' % r)
    if len(ent) != len(set(ent)): probs.append('entity drawn more than once: %s' % ent)
    if any(v > 2 for v in st.values()): probs.append('store with more than one copy: %s' % st)
    if d.W > 1.7 * d.H: probs.append('too wide %.1f x %.1f' % (d.W, d.H))
    tmp = tempfile.mkdtemp()
    import vsdx; p = os.path.join(tmp, 'l1.vsdx'); vsdx.write(d, p)
    c = subprocess.run([sys.executable, os.path.join(HERE, '..', 'tools', 'check_vsdx.py'), p], capture_output=True, text=True)
    if c.returncode: probs.append('check_vsdx: ' + c.stdout.strip().replace('\n', ' | '))
    print('%-22s %5.1f x %4.1f in  stores %s  entities %d  %s' % (os.path.basename(spec), d.W, d.H, st, len(ent),
                                                               'PASS' if not probs else 'FAIL ' + '; '.join(probs)))
    return not probs
if __name__ == '__main__':
    ok = all([run(os.path.join(ROOT, 'examples', e)) for e in EXAMPLES])
    print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
