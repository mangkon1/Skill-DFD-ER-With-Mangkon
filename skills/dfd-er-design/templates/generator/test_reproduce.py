# -*- coding: utf-8 -*-
"""Regression test: the example spec must reproduce the reference diagrams exactly.
Usage: python test_reproduce.py      (exit 0 = all match)
PNG: byte-identical md5 (needs the same Pillow/raqm + TH Sarabun New build; otherwise falls back to a pixel diff,
<0.2% different pixels passes). VSDX: page XML must be identical to ../vsdx/*.vsdx. finalize report must be all 0."""
import os, sys, hashlib, tempfile, zipfile, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); REF = os.path.dirname(HERE)
sys.path.insert(0, HERE)
EXPECT = {'01_Context_Diagram': '74d3150a1809060fcef33eb04896a635', '02_DFD_Level1': '376932e5c9fad27574a7b288d100cc89',
          '03_ER_Diagram': 'd39965a07991a474bf16505a7e4ca66b', '04_DFD_Level2_P6': 'ebc8f920b65bc592517fdd29cd3e01a6',
          '04_DFD_Level2_P8': '94213522028a917a08ead0728f9a0838'}
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
def pixdiff(a, b):
    from PIL import Image, ImageChops
    A, B = Image.open(a).convert('L'), Image.open(b).convert('L')
    if A.size != B.size: return 1.0
    h = ImageChops.difference(A, B).point(lambda v: 255 if v > 40 else 0).histogram()
    return h[255] / float(A.size[0] * A.size[1])
def main():
    import build
    out = tempfile.mkdtemp(prefix='dfder_')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): bad = build.main([os.path.join(HERE, 'examples', 'spare_part.json'), '--out', out])
    print(buf.getvalue().strip()); ok = bad == 0
    for n, h in EXPECT.items():
        p = os.path.join(out, 'png', n + '.png'); r = os.path.join(REF, 'png', n + '.png')
        if md5(p) == h: st = 'png identical'
        else:
            d = pixdiff(p, r); st = 'png differs %.3f%% pixels' % (d * 100); ok &= d < 0.002
        pa = zipfile.ZipFile(os.path.join(out, 'vsdx', n + '.vsdx')).read('visio/pages/page1.xml')
        pb = zipfile.ZipFile(os.path.join(REF, 'vsdx', n + '.vsdx')).read('visio/pages/page1.xml')
        st += ', vsdx ' + ('identical' if pa == pb else 'DIFFERENT'); ok &= pa == pb
        print('%-20s %s' % (n, st))
    print('PASS' if ok else 'FAIL'); return ok
if __name__ == '__main__': sys.exit(0 if main() else 1)
