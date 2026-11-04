# -*- coding: utf-8 -*-
"""DFD Level 1, store_mode "single" (default for new work): every data store is drawn ONCE in a store column on the
right and every process that uses it routes its own orthogonal line to it (process edge -> own vertical channel ->
store edge). Channel order is optimised to minimise crossings; ports are ordered so lines to the same store never
cross. A store gets ONE extra copy (marked as a duplicate, extra line in the ID box) only when that copy removes at
least `dup_min_gain` crossing-equivalents (crossings + vertical length / 6 in) - or when the spec forces it with
"duplicates": {"D4": ["7.0", "8.0"]} (processes served by the 2nd copy). "duplicates": "none" disables copies.
Entities: each drawn once on the left ('side' entry = straight line, 'lane' = down from the entity box and into the
process), same as the instructor style. All ends are glued to connection points on the shape edges."""
import itertools
from lay import *
import lay, model
from draw import textw

def _entries(S, F):
    if 'entries' in S: return S['entries'], S['entity_order'], S.get('entity_left'), S.get('lane_from', {})
    order, first, E = [], set(), {}
    for q in model.P1:
        L = []
        for e in model.ENT:
            dirs = [dr for dr, k in (('in', (e, q)), ('out', (q, e))) if k in F]
            if not dirs: continue
            if e not in order: order.append(e)
            how = 'lane' if e in first else 'side'
            for dr in dirs: L.append([e, dr, how])
        for e, dr, how in L: first.add(e)
        E[q] = L
    return E, order, None, {}

def build():
    S = model.SPEC['level1']
    lay.setpt(S.get('label_pt', 14))
    for k, v in S.get('layout', {}).items(): setattr(lay, k, v)
    F = model.level1(); g = lambda a, b: F.get((a, b), [])
    ENTRY, EORD, ELEFT, LFROM = _entries(S, F)
    T0, DY, BH = S.get('T0', 0.32), S.get('DY', 0.48), S.get('BH', 0.8)
    d = Diagram(S['name'], 20, 30, lpt=S.get('label_pt', 14))
    LPT = S.get('label_pt', 14)
    # ---------- lines process <-> store (one line per direction per pair)
    lines = []
    for q in model.P1:
        for D in model.STORE:
            if (q, D) in F: lines.append(dict(p=q, s=D, w=True, lab=g(q, D)))
            if (D, q) in F: lines.append(dict(p=q, s=D, w=False, lab=g(D, q)))
    RP = lambda L: lab_h(len(L['lab'])) + S.get('port_pad', 0.08)
    # ---------- processes in one column
    if ELEFT is None:
        ELEFT = {e: 0.15 + i * S.get('entity_step', 2.4) for i, e in enumerate(EORD)}
    ew = {e: max(1.6, textw(model.ENT[e], 16) + 0.4) for e in EORD}
    xp = S.get('XP') or (max(ELEFT[e] + ew[e] for e in EORD) + S.get('entity_gap', 2.4) + lay.PW / 2)
    P = {}; y = 0.3; HH = 0.32
    for q in model.P1:
        need_l = T0 * 2 + (len(ENTRY.get(q, [])) - 1) * DY + (0.12 if any(e[2] == 'side' for e in ENTRY.get(q, [])) else 0)
        need_r = HH + 0.12 + sum(RP(L) for L in lines if L['p'] == q) + 0.1
        h = max(S.get('min_process_h', 1.0), need_l, need_r)
        P[q] = d.add(q, 'proc', xp, y + h / 2, lay.PW, h, name=proc_name(q), num=model.disp(q), pt=lay.PPT)
        y += h + S.get('process_gap', 0.36)
    labw = max([textw(s, LPT) for L in lines for s in L['lab']] + [1.0]) + 0.25
    step = S.get('channel_step', 0.13)
    cx0 = xp + lay.PW / 2 + labw

    def layout(groups):
        """groups: {(D, copy): [line,...]} -> place stores, order ports, optimise channels; returns plan + score"""
        SP = S.get('store_port_step', 0.16)
        st = []
        for key, Ls in groups.items():
            yc = sum(P[L['p']].y for L in Ls) / len(Ls)
            st.append([yc, key, Ls, max(lay.SH, SP * (len(Ls) + 1))])
        FO = S.get('store_column')            # optional fixed top-to-bottom order, e.g. ["D1", "D2", ...]
        st.sort(key=lambda r: (FO.index(r[1][0]) * 10 + r[1][1], 0) if FO and r[1][0] in FO else (r[0], r[1]))
        ypos = {}; bot = -1e9
        for yc, key, Ls, h in st:
            yy = max(yc, bot + S.get('store_gap', 0.35) + h / 2); ypos[key] = (yy, h); bot = yy + h / 2
        # process right-side ports: ordered by target store y
        for q in model.P1:
            Lq = [L for Ls in groups.values() for L in Ls if L['p'] == q]
            Lq.sort(key=lambda L: (ypos[L['key']][0], not L['w']))
            yy = P[q].t + HH + 0.12
            for L in Lq:
                yy += RP(L); L['yp'] = yy - 0.04
        # store left-side ports: ordered by process port y (lines to one store never cross)
        for key, Ls in groups.items():
            yc, h = ypos[key]; Ls.sort(key=lambda L: L['yp'])
            for i, L in enumerate(Ls): L['ys'] = yc - h / 2 + h * (i + 1) / (len(Ls) + 1)
        allL = [L for Ls in groups.values() for L in Ls]
        n = len(allL)
        # pair cost: crossings when A's channel is left of B's (linear ordering problem, local search)
        def c2(A, B):
            alo, ahi = sorted((A['yp'], A['ys'])); blo, bhi = sorted((B['yp'], B['ys']))
            return (alo + 1e-6 < B['yp'] < ahi - 1e-6) + (blo + 1e-6 < A['ys'] < bhi - 1e-6)
        C = [[c2(A, B) if A is not B else 0 for B in allL] for A in allL]
        idx = list(range(n))
        idx.sort(key=lambda i: -(allL[i]['ys'] - allL[i]['yp']))
        def total(o): return sum(C[o[i]][o[j]] for i in range(n) for j in range(i + 1, n))
        best = total(idx); improved = True
        while improved and best:
            improved = False
            for i in range(n):
                a = idx.pop(i); bi, bc = i, None
                for j in range(n):
                    idx.insert(j, a); c = total(idx) if n < 60 else 0; idx.pop(j)
                    if bc is None or c < bc: bi, bc = j, c
                idx.insert(bi, a)
                if bc < best: best = bc; improved = True
        order = [allL[i] for i in idx]
        vlen = sum(abs(L['yp'] - L['ys']) for L in allL)
        return dict(order=order, ypos=ypos, cross=best, vlen=vlen, score=best + vlen / S.get('dup_len_weight', 12.0))

    def group(split):
        G = {}
        for L in lines:
            c = 1 if L['s'] in split and L['p'] in split[L['s']] else 0
            L['key'] = (L['s'], c); G.setdefault(L['key'], []).append(L)
        return G
    mode = S.get('duplicates', 'auto'); split = {}
    if isinstance(mode, dict): split = {D: set(v) for D, v in mode.items()}
    plan = layout(group(split))
    if mode == 'auto':
        gain = S.get('dup_min_gain', 4.0)
        while True:
            cand = None
            for D in model.STORE:
                if D in split: continue
                ps = [q for q in model.P1 if any(L['s'] == D and L['p'] == q for L in lines)]
                for k in range(1, len(ps)):
                    sp = dict(split); sp[D] = set(ps[k:])
                    r = layout(group(sp))
                    if plan['score'] - r['score'] >= gain and (cand is None or r['score'] < cand[0]['score']): cand = (r, sp)
            if not cand: break
            print('    dup %s: score %.1f -> %.1f (cross %d -> %d)' % ([k for k in cand[1] if k not in split], plan['score'], cand[0]['score'], plan['cross'], cand[0]['cross'])); plan, split = cand
        plan = layout(group(split))
    d.dup_report = {D: 2 for D in split}; d.hops = plan['cross'] > 0
    # ---------- draw stores once (or twice when justified) in the store column
    sx = cx0 + len(plan['order']) * step + 0.3 + lay.SW / 2
    for key, (yy, h) in plan['ypos'].items():
        D, c = key
        d.add('%s@%d' % (D, c), 'store', sx, yy, lay.SW, h, name=model.STORE[D], num=D, pt=lay.SPT, dup=(D in split))
    for i, L in enumerate(plan['order']):
        xc = cx0 + (i + 0.5) * step; Pq = P[L['p']]; St = d.shapes['%s@%d' % L['key']]
        straight = abs(L['yp'] - L['ys']) < 1e-6
        via = None if straight else [('x', xc)]
        if L['w']:
            d.conn(L['p'], St.id, 'R', 'L', L['lab'], ta=fr(Pq, L['yp']), tb=fr(St, L['ys']), via=via,
                   lab={'seg': 0, 'end': 'a', 'gap': 0.06, 'side': 'above'})
        else:
            d.conn(St.id, L['p'], 'L', 'R', L['lab'], ta=fr(St, L['ys']), tb=fr(Pq, L['yp']), via=via,
                   lab={'seg': 0 if straight else 2, 'end': 'b', 'gap': 0.06, 'side': 'above'})
    # ---------- entities (each drawn once) on the left
    ey = {}
    for q in model.P1:
        for k, e in enumerate(ENTRY.get(q, [])):
            if e: ey[(q,) + tuple(e)] = P[q].t + T0 + k * DY
    boxes = {}
    for ent in EORD:
        ys = [v for (q, e, dr, how), v in ey.items() if e == ent and how == 'side']
        yc = sum(ys) / len(ys)
        boxes[ent] = d.add(ent, 'ent', ELEFT[ent] + ew[ent] / 2, yc, ew[ent], BH, name=model.ENT[ent], pt=16)
    lab_end = lambda dr: {'end': 'b' if dr == 'in' else 'a', 'gap': 0.08, 'side': 'above'}
    lstep = S.get('lane_step', 0.18)
    for ent, B in boxes.items():
        lanes = sorted([(v, q, dr) for (q, e, dr, how), v in ey.items() if e == ent and how == 'lane'])
        n = len(lanes)
        for i, (v, q, dr) in enumerate(lanes):
            if LFROM.get(ent, 'left') == 'left': x = B.l + 0.15 + (n - 1 - i) * lstep
            else: x = B.r - 0.2 - i * lstep
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
    assert not missing, 'flows in spec but not drawn (check entries): %s' % missing
    d.solve()
    print('  %s: stores drawn %s, duplicated %s, channel crossings %d' % (d.name, len(plan['ypos']), sorted(split) or 'none', plan['cross']))
    return d
