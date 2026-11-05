# -*- coding: utf-8 -*-
"""DFD Level 1 on ONE page (instructor style): processes in one column (creation order), stores to the right,
entity boxes on the left; 'lane' entries run down from the entity box bottom then turn into the process,
'side' entries go straight from the entity side. Stores used by more than one process get the duplicate mark."""
from lay import *
import lay, model
from draw import textw
def build():
    S = model.SPEC['level1']
    # store_mode "single" (default for new specs): each store drawn once, lines routed to it (d_l1s.py).
    # "per_process" = the older instructor style used by examples/spare_part.json (a store copy beside every process).
    if S.get('layout') == 'column-rails' or S.get('style') == 'column-rails':
        import d_l1r; return d_l1r.build()
    mode = S.get('store_mode', 'per_process' if 'store_order' in S else 'single')
    if mode == 'single':     # default (v3.4): compact single boxes, store top/bottom entry (d_l1r.build_single)
        import d_l1r; return d_l1r.build_single()
    if mode == 'columns':    # v3.3: planar stores in staggered columns, entities staggered with lanes (d_l1s)
        import d_l1s; return d_l1s.build()
    lay.setpt(S['label_pt'])
    for k, v in S['layout'].items(): setattr(lay, k, v)
    ORDER, ENTRY = S['store_order'], S['entries']; SHARE = S.get('shared_store', {})
    T0, DY, BH, XP, XS = S['T0'], S['DY'], S['BH'], S['XP'], S['XS']
    F = model.level1(); g = lambda a, b: F.get((a, b), [])
    d = Diagram(S['name'], S['canvas'][0], S['canvas'][1], lpt=S['label_pt'])
    cnt = {}
    for q, L in ORDER.items():
        for D in L: cnt[D] = cnt.get(D, 0) + 1
    du = {D for D, n in cnt.items() if n > 1}
    P = {}; y = 0.3
    for q in model.P1:
        te = lab_h(1) + 0.2 if q in SHARE else 0
        need = T0 * 2 + (len(ENTRY[q]) - 1) * DY
        if any(e and e[2] == 'side' for e in ENTRY[q]): need += 0.12
        P[q] = store_rows(d, q, XP, XS, y, ORDER[q], F, du, minh=need, top_extra=te)
        if q in SHARE:   # reuse a store box already drawn for an earlier process (no extra copy)
            D, src = SHARE[q]; St = d.shapes[D + '@' + src]
            yy = P[q].t + 0.1 + lab_h(1) + 0.05
            if (D, q) in F: d.conn(St.id, q, 'B', 'R', g(D, q), ta=0.3, tb=fr(P[q], yy), lab={'side': 'above'})
            else: d.conn(q, St.id, 'R', 'B', g(q, D), ta=fr(P[q], yy), tb=0.3, lab={'side': 'above'})
        y = P[q].b + S.get('process_gap', 0.32)
    ey = {}
    for q in model.P1:
        for k, e in enumerate(ENTRY[q]):
            if e: ey[(q,) + tuple(e)] = P[q].t + T0 + k * DY
    boxes = {}
    for ent in S['entity_order']:
        ys = [v for (q, e, dr, how), v in ey.items() if e == ent and how == 'side']
        yc = sum(ys) / len(ys)
        w = max(1.6, textw(model.ENT[ent], 16) + 0.4)
        boxes[ent] = d.add(ent, 'ent', S['entity_left'][ent] + w / 2, yc, w, BH, name=model.ENT[ent], pt=16)
    lab_end = lambda dr: {'end': 'b' if dr == 'in' else 'a', 'gap': 0.08, 'side': 'above'}
    step = S.get('lane_step', 0.17)
    for ent, B in boxes.items():
        lanes = sorted([(v, q, dr) for (q, e, dr, how), v in ey.items() if e == ent and how == 'lane'])
        n = len(lanes)
        for i, (v, q, dr) in enumerate(lanes):
            if S['lane_from'].get(ent) == 'left': x = B.l + 0.15 + (n - 1 - i) * step
            else: x = B.r - 0.2 - i * step
            f = (x - B.l) / B.w
            if dr == 'in': d.conn(ent, q, 'B', 'L', g(ent, q), ta=f, tb=fr(P[q], v), lab=lab_end(dr))
            else: d.conn(q, ent, 'L', 'B', g(q, ent), ta=fr(P[q], v), tb=f, lab=lab_end(dr))
    for (q, e, dr, how), v in ey.items():
        if how != 'side': continue
        B = boxes[e]
        if dr == 'in': d.conn(e, q, 'R', 'L', g(e, q), ta=fr(B, v), tb=fr(P[q], v), lab=lab_end(dr))
        else: d.conn(q, e, 'L', 'R', g(q, e), ta=fr(P[q], v), tb=fr(B, v), lab=lab_end(dr))
    drawn = {(c.a.split('@')[0], c.b.split('@')[0]) for c in d.conns}
    missing = [k for k in F if k not in drawn]
    assert not missing, 'flows in spec but not drawn (add them to entries/store_order): %s' % missing
    d.solve(); return d
