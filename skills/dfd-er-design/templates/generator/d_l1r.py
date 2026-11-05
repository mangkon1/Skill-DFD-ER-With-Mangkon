# -*- coding: utf-8 -*-
"""DFD Level 1, layout "column-rails" (compact portrait page, the style of the instructor reference the user likes).
- Processes in ONE column. Entities in a column on the LEFT, data stores in a column on the RIGHT.
- A store / entity box sits right beside the process that uses it most ("home"); its lines to that process are
  straight horizontal lines. Lines to other processes run in parallel vertical RAILS outside the box column
  (stores: out of the box's top/bottom edge, the box is lengthened to reach its rails; entities: out of the box's
  left edge) and enter the process side horizontally between the other boxes.
- Boxes are copied (duplicate mark) only as needed to fit the page width: we start with one box per process
  (no rails) and merge copies as long as the drawing stays planar and the page stays <= "max_width" in.
- ZERO crossings, ZERO line jumps by construction (rails are nested: a rail that encloses another line's port or
  box gets a column further out). Every line end is glued to a shape edge.
Spec: "level1": {"name": "02_DFD_Level1", "layout": "column-rails"}  optional: "max_width" 6.0 (in, A4 portrait report
width), "label_pt" 8, "PPT" 9, "SPT" 8, "EPT" 9, "max_label_w" 0.9 (labels wrap above this), "store_name_w" 0.75,
"rail_step" 0.1, "port_pad" 0.07, "process_gap" 0.18. Entities/stores may be drawn several times (all copies carry the
duplicate mark), so check it with: check_vsdx.py --max-copies 0"""
import itertools
import lay, model
from lay import fr, lab_h
from draw import Diagram, textw, LINE
from d_l1s import _fits, _compatible, _noncrossing, _orders

BRK = ('ข้อมูล', 'การ', 'ประเภท', 'สนาม', 'รายงาน', 'ที่', 'ลูกค้า', 'การจอง')
def wrap1(s, maxw, pt):
    if textw(s, pt) <= maxw: return [s]
    best = None
    for i in range(3, len(s) - 2):
        if not any(s.startswith(w, i) for w in BRK) and s[i] != ' ': continue
        a, b = s[:i].strip(), s[i:].strip()
        m = max(textw(a, pt), textw(b, pt))
        if best is None or m < best[0]: best = (m, a, b)
    if not best: return [s]
    return wrap1(best[1], maxw, pt) + wrap1(best[2], maxw, pt)

def order_side(np_, blocks):
    """port order (block keys) per process so the side is non-crossing (stack construction, brute force fallback)"""
    per = [[k for k in blocks if p in blocks[k]] for p in range(np_)]
    st = []; out = []
    for p in range(np_):
        here = set(per[p]); seq = []
        # close / touch open blocks from the top of the stack
        while st and st[-1] in here and st[-1] not in seq:
            k = st[-1]; seq.append(k)
            if max(blocks[k]) == p: st.pop()
            else: break
        rest = [k for k in per[p] if k not in seq]
        if any(min(blocks[k]) < p for k in rest): return _orders(list(range(np_)), blocks)
        only = [k for k in rest if max(blocks[k]) == p]
        new = sorted([k for k in rest if max(blocks[k]) > p],
                     key=lambda k: (-max(blocks[k]), -min([u for u in blocks[k] if u > p])))
        seq += only + new; st += new
        out.append(seq)
    flat = [k for s in out for k in s]
    return out if _noncrossing(flat) else _orders(list(range(np_)), blocks)

class Plan:
    pass

def build():
    S = model.SPEC['level1']
    LPT = S.get('label_pt', 8); lay.setpt(LPT)
    F = model.level1(); P = list(model.P1); ix = {q: i for i, q in enumerate(P)}
    bad = [k for k in F if model.is_proc(k[0]) and model.is_proc(k[1])]
    assert not bad, 'column-rails: process-to-process flows are not supported yet: %s' % bad
    lines = []
    for q in P:
        for D in model.STORE:
            if (q, D) in F: lines.append(dict(p=ix[q], n=D, side='R', tow=True, lab=F[(q, D)]))
            if (D, q) in F: lines.append(dict(p=ix[q], n=D, side='R', tow=False, lab=F[(D, q)]))
        for e in model.ENT:
            if (e, q) in F: lines.append(dict(p=ix[q], n=e, side='L', tow=False, lab=F[(e, q)]))
            if (q, e) in F: lines.append(dict(p=ix[q], n=e, side='L', tow=True, lab=F[(q, e)]))
    maxw = S.get('max_label_w', 0.9)
    for L in lines: L['lab'] = [x for s in L['lab'] for x in wrap1(s, maxw, LPT)]
    # start: one box per (node, process) = no rails; then greedily merge copies while planar and narrow enough
    blocks = {}
    for L in lines:
        k = (L['side'], L['n'])
        blocks.setdefault(k, [])
        if [L['p']] not in blocks[k]: blocks[k].append([L['p']])
    budget = S.get('max_width', 6.0)
    def flat(bl, side):
        return {(n, i): u for (sd, n), us in bl.items() if sd == side for i, u in enumerate(us)}
    def plan(bl):
        o = {}
        for side in 'LR':
            B = flat(bl, side)
            if not _compatible(B): return None
            r = order_side(len(P), B)
            if r is None: return None
            o[side] = (B, r)
        return o
    cur = plan(blocks); g0 = _geom(S, P, lines, cur)
    if g0['W'] > budget:
        print('  column-rails: even one box per process needs %.2f in > max_width %.2f; use a smaller label_pt' % (g0['W'], budget))
    best = (cur, g0); lim = max(budget, g0['W'])
    while True:
        cands = []
        for k, us in blocks.items():
            for i, j in itertools.combinations(range(len(us)), 2):
                nb = dict(blocks); m = sorted(us[i] + us[j])
                nb[k] = [u for t, u in enumerate(us) if t not in (i, j)] + [m]
                o = plan(nb)
                if o is None: continue
                g = _geom(S, P, lines, o)
                if g['W'] > lim + 1e-6: continue
                cands.append((g['L'] - best[1]['L'], g['W'], g['nrail'], nb, o, g))
        if not cands: break
        cands.sort(key=lambda c: c[:3])
        _, _, _, blocks, o, g = cands[0]; best = (o, g)
    o, g = best
    d = _emit(S, P, lines, o, g)
    nb = {sd: sum(1 for s in d.shapes.values() if s.kind == kd) for sd, kd in (('R', 'store'), ('L', 'ent'))}
    dup = sorted({n for (sd, n), us in blocks.items() if len(us) > 1})
    print('  %s [column-rails]: store boxes %d (stores %d), entity boxes %d (entities %d), copied %s, rails %d, '
          'crossings 0 by construction' % (d.name, nb['R'], len({L['n'] for L in lines if L['side'] == 'R'}), nb['L'],
                                          len({L['n'] for L in lines if L['side'] == 'L'}), dup or 'none', g['nrail']))
    return d

def _geom(S, P, lines, o):
    """pure geometry: port y, boxes, rail levels, page width (works on copies of the line dicts)"""
    LPT = S.get('label_pt', 8); lines = [dict(L) for L in lines]
    PPT, SPT, EPT = S.get('PPT', 9), S.get('SPT', 8), S.get('EPT', 9)
    PW = S.get('PW') or max(textw(x, PPT) for q in P for x in wrap1(model.P1[q], S.get('proc_name_w', 1.0), PPT)) + 0.22
    SN = {D: wrap1(model.STORE[D], S.get('store_name_w', 0.75), SPT) for D in model.STORE}
    SW = S.get('SW') or max(textw(x, SPT) for L in lines if L['side'] == 'R' for x in SN[L['n']]) + S.get('store_id_w', 0.3) + 0.16
    EW = S.get('EW') or max(textw(model.ENT[L['n']], EPT) for L in lines if L['side'] == 'L') + 0.3
    pad = S.get('port_pad', 0.07)
    SH = S.get('SH', 0.26); EH = S.get('EH', 0.36); clr = S.get('clear', 0.07); gap = S.get('process_gap', 0.18)
    step = S.get('rail_step', 0.1); HH = S.get('HH', 0.26)
    RP = lambda L: lab_h(len(L['lab'])) + pad
    labw = {sd: max([textw(s, LPT) for L in lines if L['side'] == sd for s in L['lab']] + [0.5]) + 0.2 for sd in 'LR'}
    G = {}
    for sd in 'LR':
        B, orders = o[sd]
        for key, us in B.items():
            Ls = [L for L in lines if L['side'] == sd and L['n'] == key[0] and L['p'] in us]
            cnt = {u: sum(1 for L in Ls if L['p'] == u) for u in us}
            med = sorted(us)[len(us) // 2]
            home = min(us, key=lambda u: (-cnt[u], abs(u - med)))
            G[(sd, key)] = dict(sd=sd, key=key, us=us, home=home, L=Ls)
            for L in Ls: L['blk'] = (sd, key)
    # vertical layout
    y = 0.15; proc = {}
    for i, q in enumerate(P):
        top = y; ends = []
        for sd in 'LR':
            cur = top + HH + 0.04; obst = top + HH
            for key in o[sd][1][i]:
                b = G[(sd, key)]
                Ls = sorted([L for L in b['L'] if L['p'] == i], key=lambda L: (L['tow'] if sd == 'L' else not L['tow']))
                if b['home'] == i:
                    nex = len(b['L']) - len(Ls)
                    span = sum(RP(L) for L in Ls[1:])
                    h = max((max(SH, LINE(SPT) * 1.05 * len(SN[key[0]]) + 0.08)) if sd == 'R' else EH, span + 0.16, (nex + 1) * 0.085 if sd == 'L' else 0)
                    y0 = max(cur + RP(Ls[0]), obst + clr + h / 2 - span / 2)
                    yy = y0
                    for k_, L in enumerate(Ls):
                        if k_: yy += RP(L)
                        L['y'] = yy
                    c = (Ls[0]['y'] + Ls[-1]['y']) / 2
                    b['cy'] = c; b['h'] = h
                    cur = Ls[-1]['y']; obst = c + h / 2
                    cur = max(cur, obst + clr - lab_h(1) - pad)
                else:
                    for L in Ls:
                        L['y'] = max(cur + RP(L), obst + clr); cur = L['y']
                obst = max(obst, cur)
            ends.append(max(cur, obst))
        bot = max(ends) + 0.1
        nm = wrap1(model.P1[q], PW - 0.2, PPT)
        bot = max(bot, top + HH + LINE(S.get('PPT', 9)) * 1.05 * len(nm) + 0.2, top + S.get('min_process_h', 0.75))
        proc[i] = (top, bot, nm)
        y = bot + gap
    H = y
    # rails: interval per rail line; levels by enclosure
    rails = []
    for (sd, key), b in G.items():
        for L in b['L']:
            if L['p'] == b['home']: continue
            L['up'] = L['y'] < b['cy']
            rails.append(L)
    # entity left-edge exits: up-exits above down-exits; farther target = outer rail
    for (sd, key), b in G.items():
        if sd != 'L': continue
        ups = sorted([L for L in b['L'] if L.get('up') is True and L['p'] != b['home']], key=lambda L: -L['y'])
        dns = sorted([L for L in b['L'] if L.get('up') is False and L['p'] != b['home']], key=lambda L: -L['y'])
        ex = ups + dns; n = len(ex)
        for k, L in enumerate(ex): L['ye'] = b['cy'] - b['h'] / 2 + b['h'] * (k + 1) / (n + 1)
    for L in rails:
        b = G[L['blk']]
        if L['side'] == 'R': L['ye'] = b['cy'] - b['h'] / 2 if L['up'] else b['cy'] + b['h'] / 2
        L['iv'] = (min(L['ye'], L['y']), max(L['ye'], L['y']))
    def inside(v, iv): return iv[0] + 1e-6 < v < iv[1] - 1e-6
    lev = {}
    def level(A):
        k = id(A)
        if k in lev: return lev[k]
        lev[k] = -99
        m = -1
        for C in rails:
            if C is A or C['side'] != A['side']: continue
            bc = G[C['blk']]
            if inside(C['y'], A['iv']) or (C['blk'] != A['blk'] and (inside(bc['cy'], A['iv']))):
                m = max(m, level(C))
        lev[k] = m + 1; return lev[k]
    for L in rails: L['lv'] = level(L)
    assert all(v >= 0 for v in lev.values()), 'rail nesting cycle'
    nl = {sd: max([L['lv'] + 1 for L in rails if L['side'] == sd] + [0]) for sd in 'LR'}
    x_el = 0.15 + nl['L'] * step + (0.1 if nl['L'] else 0)
    x_er = x_el + EW; xpl = x_er + labw['L']; xpr = xpl + PW; xs = xpr + labw['R']
    for L in rails:
        L['xr'] = (x_el - S.get('rail_off', 0.1) - L['lv'] * step) if L['side'] == 'L' else (xs + SW + S.get('rail_off', 0.1) + L['lv'] * step)
    for (sd, key), b in G.items():
        if sd == 'R':
            xr = [L['xr'] for L in b['L'] if 'xr' in L and L['p'] != b['home']]
            b['l'] = xs; b['w'] = max(SW, (max(xr) + S.get('rail_ext', 0.04) - xs) if xr else 0)
        else:
            b['l'] = x_el; b['w'] = EW
    W = max([b['l'] + b['w'] for b in G.values()] + [xpr]) + 0.15
    if S.get('debug'): print('    W %.2f: EW %.2f labL %.2f PW %.2f labR %.2f SW %.2f rails %s' % (W, EW, labw['L'], PW, labw['R'], SW, nl))
    Ltot = sum(abs(L['y'] - L['ye']) for L in rails)
    return dict(SN=SN, lines=lines, G=G, proc=proc, W=W, H=H, xpl=xpl, PW=PW, nrail=len(rails), L=Ltot, nl=nl)

def _emit(S, P, lines, o, g):
    lines = g['lines']
    LPT = S.get('label_pt', 8)
    d = Diagram(S['name'], g['W'], g['H'], lpt=LPT)
    Ps = {}
    for i, q in enumerate(P):
        top, bot, nm = g['proc'][i]
        Ps[i] = d.add(q, 'proc', g['xpl'] + g['PW'] / 2, (top + bot) / 2, g['PW'], bot - top, name='\n'.join(nm),
                      num=model.disp(q), pt=S.get('PPT', 9))
        Ps[i].hh = S.get('HH', 0.26)
    copies = {}
    for (sd, key), b in g['G'].items(): copies[(sd, key[0])] = copies.get((sd, key[0]), 0) + 1
    box = {}
    for (sd, key), b in g['G'].items():
        n, k = key; dup = copies[(sd, n)] > 1
        if sd == 'R':
            box[(sd, key)] = d.add('%s@%d' % (n, k), 'store', b['l'] + b['w'] / 2, b['cy'], b['w'], b['h'],
                                   name='\n'.join(g['SN'][n]), num=n, pt=S.get('SPT', 8), dup=dup)
            box[(sd, key)].iw = S.get('store_id_w', 0.3)
        else:
            box[(sd, key)] = d.add('%s@%d' % (n, k), 'ent', b['l'] + b['w'] / 2, b['cy'], b['w'], b['h'],
                                   name=model.ENT[n], pt=S.get('EPT', 9), dup=dup)
    for L in lines:
        b = g['G'][L['blk']]; Bx = box[L['blk']]; Pq = Ps[L['p']]; y = L['y']
        lab = lambda seg, end: {'seg': seg, 'end': end, 'gap': 0.05, 'side': 'above'}
        if L['p'] == b['home']:
            if L['side'] == 'R':
                if L['tow']: d.conn(Pq.id, Bx.id, 'R', 'L', L['lab'], ta=fr(Pq, y), tb=fr(Bx, y), lab=lab(0, 'a'))
                else: d.conn(Bx.id, Pq.id, 'L', 'R', L['lab'], ta=fr(Bx, y), tb=fr(Pq, y), lab=lab(0, 'b'))
            else:
                if L['tow']: d.conn(Pq.id, Bx.id, 'L', 'R', L['lab'], ta=fr(Pq, y), tb=fr(Bx, y), lab=lab(0, 'a'))
                else: d.conn(Bx.id, Pq.id, 'R', 'L', L['lab'], ta=fr(Bx, y), tb=fr(Pq, y), lab=lab(0, 'b'))
            continue
        xr = L['xr']
        if L['side'] == 'R':
            e = 'T' if L['up'] else 'B'; f = fr(Bx, xr, 'x')
            if L['tow']: d.conn(Pq.id, Bx.id, 'R', e, L['lab'], ta=fr(Pq, y), tb=f, via=[('x', xr)], lab=lab(0, 'a'))
            else: d.conn(Bx.id, Pq.id, e, 'R', L['lab'], ta=f, tb=fr(Pq, y), via=[('y', y)], lab=lab(1, 'b'))
        else:
            fe = fr(Bx, L['ye'])
            if L['tow']: d.conn(Pq.id, Bx.id, 'L', 'L', L['lab'], ta=fr(Pq, y), tb=fe, via=[('x', xr), ('y', L['ye'])], lab=lab(0, 'a'))
            else: d.conn(Bx.id, Pq.id, 'L', 'L', L['lab'], ta=fe, tb=fr(Pq, y), via=[('x', xr), ('y', y)], lab=lab(2, 'b'))
    d.solve()
    return d
