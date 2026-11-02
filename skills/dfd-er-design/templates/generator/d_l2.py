# -*- coding: utf-8 -*-
"""DFD Level 2: only for Level-1 processes that really have several steps. Same style as Level 1.
Balancing: every flow between the parent process and the outside in Level 1 must appear here (checked)."""
from lay import *
import lay, model
from draw import textw
def build_one(D2):
    S = model.SPEC['level2']
    lay.setpt(S['label_pt'])
    for k, v in S['layout'].items(): setattr(lay, k, v)
    lay.BR.update(D2.get('breaks', {})); model.P2.update(D2['subprocesses'])
    XE, XP, XS = S['XE'], S['XP'], S['XS']
    F = {}
    for a, b, l in D2['flows']: F.setdefault((a, b), []).append(l)
    d = Diagram(D2['name'], S['canvas'][0], S['canvas'][1], lpt=S['label_pt'])
    subs = sorted({x for k in F for x in k if x[0].isdigit()})
    stores = {q: [D for D in model.STORE if (q, D) in F or (D, q) in F] for q in subs}
    cnt = {}
    for q in subs:
        for D in stores[q]: cnt[D] = cnt.get(D, 0) + 1
    du = {D for D, n in cnt.items() if n > 1}
    ents = {q: [e for e in model.ENT if (e, q) in F or (q, e) in F] for q in subs}
    P = {}; y = 0.3
    for q in subs:
        P[q] = store_rows(d, q, XP, XS, y, stores[q], F, du, minh=max(1.25, 0.95 * len(ents[q]) + 0.35))
        y = P[q].b + 0.85
    for a, b in zip(subs, subs[1:]):
        if (a, b) in F: V(d, a, b, P[a].x, F[(a, b)], side='right')
    for q in subs:
        es = ents[q]; Q = P[q]
        for k, e in enumerate(es):
            yc = Q.t + (k + 0.5) * Q.h / len(es)
            w = max(1.6, textw(model.ENT[e], 16) + 0.4)
            both = (e, q) in F and (q, e) in F
            d.add(e, 'ent', XE, yc, w, 0.8 if not both else 0.9, name=model.ENT[e], pt=16)
            if (e, q) in F: H(d, e, q, yc - (0.2 if both else 0), F[(e, q)], side='above', maxw=None)
            if (q, e) in F: H(d, q, e, yc + (0.2 if both else 0), F[(q, e)], side='below' if both else 'above', maxw=None)
    pairs = [(c.a.split('@')[0], c.b.split('@')[0]) for c in d.conns]
    assert len(pairs) == len(set(pairs)), 'two arrows for the same direction: %s' % pairs
    assert set(pairs) == set(F), set(F) ^ set(pairs)
    check_balance(D2)
    d.solve(); return d
def check_balance(D2):
    """external side of Level 2 (entities + stores) must equal the parent's Level-1 flows (labels may be split)"""
    p = D2['process']; L1 = model.level1()
    outer1 = {(a, b) for (a, b) in L1 if p in (a, b)}
    outer1 = {('X' if a == p else a, 'X' if b == p else b) for a, b in outer1}
    outer2 = set()
    for a, b, l in D2['flows']:
        if a[0].isdigit() and b[0].isdigit(): continue
        outer2.add(('X' if a[0].isdigit() else a, 'X' if b[0].isdigit() else b))
    if outer1 != outer2: print('  WARN balance %s: only L1 %s | only L2 %s' % (p, sorted(outer1 - outer2), sorted(outer2 - outer1)))
def build():
    return [build_one(D2) for D2 in model.SPEC['level2']['diagrams']]
