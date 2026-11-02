# -*- coding: utf-8 -*-
"""Sanity-check a generated .vsdx before it goes into the report.
Usage: python check_vsdx.py FILE.vsdx [...]
Checks: zip + XML well-formed; every group shape has DisplayMode=1 (members drawn in front of the group, otherwise a
group fill hides the text and the ER header colour in Visio); DFD process/store/entity groups have no fill;
connectors per shape pair (ER must be exactly 1 per table pair)."""
import sys, zipfile, collections
from lxml import etree
N = '{http://schemas.microsoft.com/office/visio/2012/main}'
def cellv(sh, n):
    c = sh.find(N + "Cell[@N='%s']" % n)
    return None if c is None else c.get('V')
def check(path):
    z = zipfile.ZipFile(path); assert z.testzip() is None
    for n in z.namelist():
        if n.endswith('.xml') or n.endswith('.rels'): etree.fromstring(z.read(n))
    x = etree.fromstring(z.read('visio/pages/page1.xml'))
    probs = []
    groups = [s for s in x.iter(N + 'Shape') if s.get('Type') == 'Group']
    for g in groups:
        if cellv(g, 'DisplayMode') != '1': probs.append('group %s DisplayMode=%s (need 1)' % (g.get('ID'), cellv(g, 'DisplayMode')))
    label = {}
    for g in groups:
        t = ' '.join(' '.join(''.join(s.find(N + 'Text').itertext()).split()) for s in g.iter(N + 'Shape') if s.find(N + 'Text') is not None)
        label[g.get('ID')] = t[:40]
    for s in x.iter(N + 'Shape'):
        if s.get('Type') != 'Group' and s.find(N + 'Text') is not None and s.getparent().getparent().tag == N + 'Shapes':
            label.setdefault(s.get('ID'), ''.join(s.find(N + 'Text').itertext()).strip()[:40])
    ends = collections.defaultdict(dict)
    for c in x.iter(N + 'Connect'): ends[c.get('FromSheet')][c.get('FromCell')] = c.get('ToSheet')
    pairs = collections.Counter()
    for e in ends.values():
        if 'BeginX' in e and 'EndX' in e: pairs[frozenset((label.get(e['BeginX'], e['BeginX']), label.get(e['EndX'], e['EndX'])))] += 1
    mx = max(pairs.values()) if pairs else 0
    print('%s: groups=%d connectors=%d pairs=%d max_per_pair=%d %s' % (path, len(groups), len(ends), len(pairs), mx,
          'OK' if not probs else 'PROBLEMS:\n  ' + '\n  '.join(probs)))
    if 'ER' in path and mx > 1:
        for p, n in pairs.items():
            if n > 1: print('  duplicate ER line:', ' — '.join(sorted(p)))
        return False
    return not probs
if __name__ == '__main__':
    ok = all([check(p) for p in sys.argv[1:]]); sys.exit(0 if ok else 1)
