# -*- coding: utf-8 -*-
"""ER Diagram (Crow's Foot). Table boxes: header = table name (bold, filled), rows = key column (PK/FK) + attribute.
Exactly one relationship line per table pair. Ends: parent 25 (one-and-only-one) or 30 (zero-or-one, nullable FK);
child 29 (zero-or-many) or 30 (one-to-one)."""
from draw import Diagram
import model
def build():
    S = model.SPEC['er']; RH, TW = S['row_h'], S['table_w']; T = S['tables']
    d = Diagram(S['name'], S['canvas'][0], S['canvas'][1], lpt=S.get('label_pt', 12))
    for p in S['placement']:
        rows = [tuple(r) for r in T[p['name']]]; h = RH * (len(rows) + 1)
        s = d.add(p['name'], 'erent', p['x'], p['y'], TW, h, name=p['name'], rows=rows, pt=S.get('header_pt', 13))
        s.rh = RH
    seen = set()
    for r in S['relations']:
        key = frozenset((r['parent'], r['child']))
        assert key not in seen, 'duplicate relationship line between %s' % sorted(key)
        seen.add(key)
        via = [tuple(v) for v in r['via']] if r.get('via') else None
        d.conn(r['parent'], r['child'], r['side_parent'], r['side_child'], [], ta=r['ta'], tb=r['tb'], via=via,
               ba=r.get('parent_end', 25), ea=r.get('child_end', 29))
    d.solve(); return d
def row_frac(table, attr):
    """helper for writing a spec by hand: vertical fraction of a row centre, for ta/tb on L/R sides"""
    S = model.SPEC['er']; rows = S['tables'][table]
    for i, (k, a) in enumerate(rows):
        if a == attr: return (S['row_h'] * (i + 1.5)) / (S['row_h'] * (len(rows) + 1))
    raise KeyError(attr)
