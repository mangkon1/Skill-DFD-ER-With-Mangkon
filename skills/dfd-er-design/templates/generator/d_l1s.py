# -*- coding: utf-8 -*-
"""DFD Level 1, store_mode "single" (default for new work): ZERO crossings, ZERO line jumps.
Processes stay in one column (creation order), entities on the left, stores on the right. Every line leaves the
process right edge horizontally, runs in its OWN vertical lane and enters the store's left edge; nothing crosses.

How: the lines on the right side form blocks (one block = one store box). A drawing without crossings exists iff the
blocks form a non-crossing partition of the process ports (top to bottom), with free port order inside each process.
We search for the FEWEST store copies that make that possible (copy = the allowed single duplicate, drawn with the
duplicate mark), preferring copies that serve neighbouring processes; then nest blocks: a block whose ports lie
between two ports of another block is drawn in a column closer to the processes, so the outer block's lanes go
around it ("around the back"). Each store has at most 2 boxes. If no layout with <= 1 copy per store exists, the
build stops and says so (split the process or reorder) instead of drawing a crossing.
Spec: "duplicates": "auto" (default) or {"D4": ["6.0", "7.0", "8.0"]} (processes served by the 2nd box).
Entities: each drawn once on the left ('side' = straight line, 'lane' = down from the entity box into the process)."""
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
    # left side: each entity ONCE (single boxes first). Entity lanes nest without crossing iff the entities' process
    # sets are pairwise non-interlacing; only then (last resort) an entity gets ONE copy, split where it helps.
    P = list(model.P1); ix = {q: i for i, q in enumerate(P)}
    users = {e: sorted({ix[q] for q in P for (e2, dr, how) in E[q] if e2 == e}) for e in order}
    split = _plan_left(users, P)
    if split:
        for q in P:
            for it in E[q]:
                if it[0] in split and q in split[it[0]]: it[0] = it[0] + '@2'
        order = []; first = set()
        for q in P:
            for it in E[q]:
                if it[0] not in order: order.append(it[0])
                it[2] = 'lane' if it[0] in first else 'side'
            for it in E[q]: first.add(it[0])
    # inside one process: entities arriving by lane from above first (inner = box further right, on top), then the
    # entities whose box is beside this process (outer first) -> no lane crosses another entity's line or box
    for q in P: E[q].sort(key=lambda it: (0, -order.index(it[0])) if it[2] == 'lane' else (1, order.index(it[0])))
    return E, order, None, {}

def _plan_left(users, P):
    B = {e: u for e, u in users.items()}
    if _compatible(B): return {}
    ents = list(B)
    for k in range(1, len(ents) + 1):
        for Es in itertools.combinations(ents, k):
            opts = [[set(P[i] for i in B[e][c:]) for c in range(1, len(B[e]))] for e in Es]
            for combo in itertools.product(*opts):
                sp = dict(zip(Es, combo)); BB = {}
                for e, u in B.items():
                    if e in sp:
                        BB[e] = [i for i in u if P[i] not in sp[e]]; BB[e + '@2'] = [i for i in u if P[i] in sp[e]]
                    else: BB[e] = u
                if _compatible(BB): return sp
    raise ValueError('Level 1 left side cannot avoid crossings even with one copy per entity; reorder processes')

# ------------------------------------------------------------------ combinatorics (no geometry)
def _fits(A, B):
    """block A (process indices) fits inside one gap of block B (endpoints may be shared)"""
    b = sorted(set(B))
    gaps = [(b[j], b[j + 1]) for j in range(len(b) - 1)] + [(None, b[0]), (b[-1], None)]
    for lo, hi in gaps:
        if all((lo is None or a >= lo) and (hi is None or a <= hi) for a in A): return True
    return False
def _compatible(blocks):
    ks = list(blocks)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            A, B = blocks[ks[i]], blocks[ks[j]]
            if not (_fits(A, B) or _fits(B, A)): return False
    return True
def _noncrossing(seq):
    last = {x: i for i, x in enumerate(seq)}; st = []; seen = set()
    for i, x in enumerate(seq):
        if x in seen:
            if st[-1] != x: return False
        else: seen.add(x); st.append(x)
        if last[x] == i: st.pop()
    return True
def _orders(procs, blocks, limit=20000):
    """port order (list of block keys) inside every process so the whole right side is a non-crossing sequence"""
    per = [[k for k in blocks if p in blocks[k]] for p in range(len(procs))]
    opts = [list(itertools.permutations(L)) for L in per]
    n = 0
    for combo in itertools.product(*opts):
        n += 1
        if n > limit: return None
        seq = [k for c in combo for k in c]
        if _noncrossing(seq): return [list(c) for c in combo]
    return None

def plan_blocks(lines, S):
    P = list(model.P1); idx = {q: i for i, q in enumerate(P)}
    users = {D: sorted({idx[L['p']] for L in lines if L['s'] == D}) for D in model.STORE}
    users = {D: u for D, u in users.items() if u}
    def blocks_for(split):
        B = {}
        for D, u in users.items():
            if D in split:
                B[(D, 0)] = [i for i in u if P[i] not in split[D]]; B[(D, 1)] = [i for i in u if P[i] in split[D]]
            else: B[(D, 0)] = list(u)
        return {k: v for k, v in B.items() if v}
    mode = S.get('duplicates', 'auto')
    if isinstance(mode, dict):
        sp = {D: set(v) for D, v in mode.items()}; B = blocks_for(sp)
        o = _orders(P, B) if _compatible(B) else None
        if o is None: raise ValueError('level1 duplicates %s still give crossing lines; use "auto"' % mode)
        return [(sp, B, o)]
    def splits(D, allsets):
        u = users[D]
        if not allsets:
            for k in range(1, len(u)): yield set(P[i] for i in u[k:])
        else:
            for m in range(1, 2 ** (len(u) - 1)): yield set(P[u[i]] for i in range(len(u)) if (m >> i) & 1)
    stores = [D for D in model.STORE if D in users]
    for k in range(0, len(stores) + 1):
        if mode == 'none' and k: break
        for allsets in (False, True):
            sols = []
            for Ds in itertools.combinations(stores, k):
                for combo in itertools.product(*[list(splits(D, allsets)) for D in Ds]):
                    sp = dict(zip(Ds, combo)); B = blocks_for(sp)
                    if not _compatible(B): continue
                    o = _orders(P, B)
                    if o is not None: sols.append((sp, B, o))
                    if len(sols) >= S.get('max_candidates', 40): break
            if sols: return sols
    raise ValueError('Level 1 cannot be drawn without crossings even with one copy per store; split a process or '
                     'reorder processes (docs/dfd-style.md)')

# ------------------------------------------------------------------ geometry
def build():
    S = model.SPEC['level1']
    lay.setpt(S.get('label_pt', 14))
    for k, v in S.get('layout', {}).items(): setattr(lay, k, v)
    F = model.level1(); g = lambda a, b: F.get((a, b), [])
    lines = []
    for q in model.P1:
        for D in model.STORE:
            if (q, D) in F: lines.append(dict(p=q, s=D, w=True, lab=g(q, D)))
            if (D, q) in F: lines.append(dict(p=q, s=D, w=False, lab=g(D, q)))
    best = None
    for sp, B, orders in plan_blocks(lines, S):
        d = _draw(S, F, g, lines, sp, B, orders)
        r = _score(d)
        if best is None or r < best[0]: best = (r, d, sp)
    r, d, sp = best
    d.dup_report = {D: 2 for D in sp}
    print('  %s: store boxes %d (stores %d), duplicated %s, crossings 0 by construction' % (
        d.name, sum(1 for s in d.shapes.values() if s.kind == 'store'), len(model.STORE), sorted(sp) or 'none'))
    return d

def _score(d):
    import finalize
    rep = finalize.report(d)
    L = sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for c in d.conns for p, q in zip(c.pts[:-1], c.pts[1:]))
    xs = [s.r for s in d.shapes.values()]
    return (sum(rep.values()), max(xs) * 2 + L)

def _draw(S, F, g, lines, sp, B, orders):
    ENTRY, EORD, ELEFT, LFROM = _entries(S, F)
    T0, DY, BH = S.get('T0', 0.32), S.get('DY', 0.48), S.get('BH', 0.8)
    LPT = S.get('label_pt', 14)
    d = Diagram(S['name'], 20, 30, lpt=LPT)
    for L in lines:
        L['key'] = (L['s'], 1 if L['s'] in sp and L['p'] in sp[L['s']] else 0)
    RP = lambda L: lab_h(len(L['lab'])) + S.get('port_pad', 0.12)
    if ELEFT is None: ELEFT = {e: 0.15 + i * S.get('entity_step', 2.4) for i, e in enumerate(EORD)}
    base = lambda e: e.split('@')[0]
    ew = {e: max(1.6, textw(model.ENT[base(e)], 16) + 0.4) for e in EORD}
    ecopies = {base(e) for e in EORD if '@' in e}
    xp = S.get('XP') or (max(ELEFT[e] + ew[e] for e in EORD) + S.get('entity_gap', 2.4) + lay.PW / 2)
    P = {}; y = 0.3; HH = 0.32
    for i, q in enumerate(model.P1):
        need_l = T0 * 2 + (len(ENTRY.get(q, [])) - 1) * DY + (0.12 if any(e[2] == 'side' for e in ENTRY.get(q, [])) else 0)
        need_r = HH + 0.12 + sum(RP(L) for L in lines if L['p'] == q) + 0.1
        h = max(S.get('min_process_h', 1.0), need_l, need_r)
        P[q] = d.add(q, 'proc', xp, y + h / 2, lay.PW, h, name=proc_name(q), num=model.disp(q), pt=lay.PPT)
        # ports in the planned block order (write line above read line of the same store)
        yy = P[q].t + HH + 0.12
        for key in orders[i]:
            for L in sorted([L for L in lines if L['p'] == q and L['key'] == key], key=lambda L: not L['w']):
                yy += RP(L); L['yp'] = yy - 0.04
        y += h + S.get('process_gap', 0.36)
    labw = max([textw(s, LPT) for L in lines for s in L['lab']] + [1.0]) + 0.25
    step = S.get('lane_step_r', 0.14); SP = S.get('store_port_step', 0.16)
    blk = {}
    for key in B:
        Ls = sorted([L for L in lines if L['key'] == key], key=lambda L: L['yp'])
        blk[key] = dict(L=Ls, lo=Ls[0]['yp'], hi=Ls[-1]['yp'])
    # nesting level: 0 = nothing nested inside; outer blocks get columns further right (they go around the inner ones)
    def inside(a, b): return blk[b]['lo'] < blk[a]['lo'] - 1e-9 and blk[a]['hi'] < blk[b]['hi'] - 1e-9
    lev = {}
    for key in sorted(blk, key=lambda k: blk[k]['hi'] - blk[k]['lo']):
        inner = [k for k in blk if k != key and inside(k, key)]
        lev[key] = 1 + max(lev[k] for k in inner) if inner else 0
    # store box + lanes per block
    for key, b in blk.items():
        m = len(b['L']); h = max(lay.SH, SP * (m + 1))
        ys = [L['yp'] for L in b['L']]
        if m % 2: cy = ys[m // 2]
        else: cy = (ys[m // 2 - 1] + ys[m // 2]) / 2
        b['h'] = h; b['cy'] = cy
        for k, L in enumerate(b['L']): L['ys'] = cy - h / 2 + h * (k + 1) / (m + 1)
        if m % 2: b['L'][m // 2]['ys'] = cy
        ab = [L for L in b['L'] if L['yp'] < L['ys'] - 1e-6]
        be = [L for L in b['L'] if L['yp'] > L['ys'] + 1e-6]
        b['ab'] = ab; b['be'] = sorted(be, key=lambda L: -L['yp'])
        b['nl'] = max(len(ab), len(be))
    nlev = max(lev.values()) + 1
    x0 = xp + lay.PW / 2 + labw; colx = []
    for Lv in range(nlev):
        nl = max([blk[k]['nl'] for k in blk if lev[k] == Lv] + [0])
        sxl = x0 + nl * step + 0.3; colx.append(sxl); x0 = sxl + lay.SW + 0.35
    for key, b in blk.items():
        D, c = key; sxl = colx[lev[key]]
        St = d.add('%s@%d' % key, 'store', sxl + lay.SW / 2, b['cy'], lay.SW, b['h'], name=model.STORE[D], num=D,
                   pt=lay.SPT, dup=(D in sp))
        for grp in (b['ab'], b['be']):
            for i, L in enumerate(grp):
                L['xl'] = sxl - 0.3 - i * step
        for L in b['L']:
            Pq = P[L['p']]; straight = abs(L['yp'] - L['ys']) < 1e-6
            via = None if straight else [('x', L['xl'])]
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
        boxes[ent] = d.add(ent, 'ent', ELEFT[ent] + ew[ent] / 2, sum(ys) / len(ys), ew[ent], BH, name=model.ENT[base(ent)], pt=16,
                            dup=base(ent) in ecopies)
    lab_end = lambda dr: {'end': 'b' if dr == 'in' else 'a', 'gap': 0.08, 'side': 'above'}
    lstep = S.get('lane_step', 0.18)
    for ent, Bx in boxes.items():
        lanes = sorted([(v, q, dr) for (q, e, dr, how), v in ey.items() if e == ent and how == 'lane'])
        n = len(lanes)
        for i, (v, q, dr) in enumerate(lanes):
            if LFROM.get(ent, 'left') == 'left': x = Bx.l + 0.15 + (n - 1 - i) * lstep
            else: x = Bx.r - 0.2 - i * lstep
            f = (x - Bx.l) / Bx.w
            if dr == 'in': d.conn(ent, q, 'B', 'L', g(base(ent), q), ta=f, tb=fr(P[q], v), lab=lab_end(dr))
            else: d.conn(q, ent, 'L', 'B', g(q, base(ent)), ta=fr(P[q], v), tb=f, lab=lab_end(dr))
    for (q, e, dr, how), v in ey.items():
        if how != 'side': continue
        Bx = boxes[e]
        if dr == 'in': d.conn(e, q, 'R', 'L', g(base(e), q), ta=fr(Bx, v), tb=fr(P[q], v), lab=lab_end(dr))
        else: d.conn(q, e, 'L', 'R', g(q, base(e)), ta=fr(P[q], v), tb=fr(Bx, v), lab=lab_end(dr))
    drawn = {(c.a.split('@')[0], c.b.split('@')[0]) for c in d.conns}
    missing = [k for k in F if k not in drawn]
    assert not missing, 'flows in spec but not drawn (check entries): %s' % missing
    d.solve()
    return d
