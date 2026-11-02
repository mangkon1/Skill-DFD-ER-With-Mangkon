# post-processing: separate overlapping line segments into lanes, place labels clear of lines/shapes
from draw import LINE, textw
E = 1e-6
LANE = 0.08     # spacing between parallel lines
NEAR = 0.055    # parallel lines closer than this are "overlapping"

def segs_of(c):
    return [(i, c.pts[i], c.pts[i + 1]) for i in range(len(c.pts) - 1)]
def orient(p, q):
    return 'H' if abs(p[1] - q[1]) < E else 'V'
def rng(p, q, o):
    return (min(p[0], q[0]), max(p[0], q[0])) if o == 'H' else (min(p[1], q[1]), max(p[1], q[1]))
def coord(p, o): return p[1] if o == 'H' else p[0]

def all_segs(d):
    out = []
    for c in d.conns:
        n = len(c.pts) - 1
        for i, p, q in segs_of(c):
            o = orient(p, q)
            out.append(dict(c=c, i=i, o=o, k=coord(p, o), r=rng(p, q, o), mov=(0 < i < n - 1)))
    return out

def seg_hits_shape(o, k, r, d, skip=()):
    for s in d.shapes.values():
        if s.id in skip: continue
        if o == 'H':
            if s.t + 0.01 < k < s.b - 0.01 and r[0] < s.r - 0.01 and r[1] > s.l + 0.01: return True
        else:
            if s.l + 0.01 < k < s.r - 0.01 and r[0] < s.b - 0.01 and r[1] > s.t + 0.01: return True
    return False

def conflicts(S, me, k, d):
    """number of other segments parallel & overlapping & too close to me at coordinate k"""
    n = 0
    for s in S:
        if s is me or s['o'] != me['o']: continue
        if s['c'] is me['c'] and abs(s['i'] - me['i']) <= 1: continue
        lo, hi = max(s['r'][0], me['r'][0]), min(s['r'][1], me['r'][1])
        if hi - lo > 0.01 and abs(s['k'] - k) < NEAR: n += 1
    return n

def shift(c, i, o, newk):
    p, q = c.pts[i], c.pts[i + 1]
    if o == 'H': c.pts[i] = (p[0], newk); c.pts[i + 1] = (q[0], newk)
    else: c.pts[i] = (newk, p[1]); c.pts[i + 1] = (newk, q[1])

def nudge(d, rounds=12):
    for _ in range(rounds):
        S = all_segs(d); moved = False
        for me in S:
            if conflicts(S, me, me['k'], d) == 0: continue
            if not me['mov']: continue
            best = None
            for j in range(1, 14):
                for sg in (1, -1):
                    k = me['k'] + sg * j * LANE / 2
                    # neighbours' ranges change when we move; approximate with current ranges
                    c = me['c']; i = me['i']
                    # adjacent segments get longer/shorter; ensure we don't go past their far ends (keeps orthogonal shape)
                    if seg_hits_shape(me['o'], k, me['r'], d): continue
                    n = conflicts(S, me, k, d)
                    if best is None or n < best[0]: best = (n, j, k)
                    if n == 0: break
                if best and best[0] == 0: break
            if best and best[0] < conflicts(S, me, me['k'], d):
                shift(me['c'], me['i'], me['o'], best[2]); me['k'] = best[2]; moved = True
        if not moved: break
    for c in d.conns: _clean(c)

def _clean(c):
    q = [c.pts[0]]
    for p in c.pts[1:]:
        if abs(p[0] - q[-1][0]) > E or abs(p[1] - q[-1][1]) > E: q.append(p)
    r = [q[0]]
    for i in range(1, len(q) - 1):
        a, b, e = r[-1], q[i], q[i + 1]
        if (abs(a[0] - b[0]) < E and abs(b[0] - e[0]) < E) or (abs(a[1] - b[1]) < E and abs(b[1] - e[1]) < E): continue
        r.append(b)
    r.append(q[-1]); c.pts = r

# ------------------------------------------------------------------ labels
def rect_seg(rc, p, q, pad=0.03):
    x0, y0, x1, y1 = rc[0] - pad, rc[1] - pad, rc[2] + pad, rc[3] + pad
    if abs(p[1] - q[1]) < E:
        y = p[1]; a, b = sorted((p[0], q[0]))
        return y0 < y < y1 and a < x1 and b > x0
    x = p[0]; a, b = sorted((p[1], q[1]))
    return x0 < x < x1 and a < y1 and b > y0
def rect_rect(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
def lrect(cx, cy, w, h): return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

def label_cost(d, c, rc, placed, extra_shapes):
    cost = 0
    if rc[0] < 0.02 or rc[1] < 0.02 or rc[2] > d.W - 0.02 or rc[3] > d.H - 0.02: cost += 200
    for o in d.conns:
        for i, p, q in segs_of(o):
            if rect_seg(rc, p, q): cost += 60
    for s in d.shapes.values():
        if rect_rect(rc, (s.l - 0.04, s.t - 0.03, s.r + 0.04, s.b + 0.03)): cost += 150
    for r2 in placed:
        if rect_rect(rc, (r2[0] - 0.02, r2[1] - 0.01, r2[2] + 0.02, r2[3] + 0.01)): cost += 120
    return cost

def candidates(c, w, h):
    gap = 0.035
    out = []
    n = len(c.pts) - 1
    for i, p, q in segs_of(c):
        L = abs(p[0] - q[0]) + abs(p[1] - q[1])
        if L < 0.12: continue
        for f in (0.5, 0.3, 0.7, 0.15, 0.85, 0.05, 0.95, 0.4, 0.6, 0.22, 0.78):
            mx, my = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
            if abs(p[1] - q[1]) < E:
                for sd in (-1, 1):
                    out.append((mx, my + sd * (h / 2 + gap), i, f))
                # end-anchored (text starts/ends at the segment end region)
            else:
                for sd in (1, -1):
                    out.append((mx + sd * (w / 2 + gap), my, i, f))
        if abs(p[1] - q[1]) < E and L > w + 0.1:
            a, b = sorted((p[0], q[0]))
            for sd in (-1, 1):
                out.append((a + 0.05 + w / 2, p[1] + sd * (h / 2 + gap), i, 0))
                out.append((b - 0.05 - w / 2, p[1] + sd * (h / 2 + gap), i, 1))
    return out

def variants(c, pt):
    from draw import wrap
    base = list(c.labels)
    return [base]

def dims(lines, pt):
    lh = LINE(pt) * 1.05
    return max(textw(s, pt) for s in lines) + 0.08, lh * len(lines) + 0.04

def place_labels(d, passes=3):
    items = [c for c in d.conns if c.lbox]
    rects = {}
    for c in items:
        cx, cy, w, h, pt = c.lbox; rects[id(c)] = lrect(cx, cy, w, h)
    for _ in range(passes):
        for c in items:
            cx0, cy0, w0, h0, pt = c.lbox
            placed = [r for k, r in rects.items() if k != id(c)]
            best = (label_cost(d, c, rects[id(c)], placed, None), cx0, cy0, w0, h0, c.labels)
            if best[0] == 0: continue
            for li, lines in enumerate(variants(c, pt)):
                w, h = dims(lines, pt)
                for (x, y, i, f) in candidates(c, w, h):
                    rc = lrect(x, y, w, h)
                    cost = label_cost(d, c, rc, placed, None)
                    cost += 0.6 * (abs(x - cx0) + abs(y - cy0)) + 0.8 * li
                    if cost < best[0]: best = (cost, x, y, w, h, lines)
            _, x, y, w, h, lines = best
            c.labels = list(lines)
            c.lbox = (x, y, w, h, pt); rects[id(c)] = lrect(x, y, w, h)

# ------------------------------------------------------------------ report
def report(d):
    S = all_segs(d)
    ov = 0
    for a in range(len(S)):
        for b in range(a + 1, len(S)):
            s, t = S[a], S[b]
            if s['c'] is t['c'] or s['o'] != t['o']: continue
            lo, hi = max(s['r'][0], t['r'][0]), min(s['r'][1], t['r'][1])
            if hi - lo > 0.01 and abs(s['k'] - t['k']) < NEAR - 0.005: ov += 1
    cr = 0
    for a in range(len(S)):
        for b in range(a + 1, len(S)):
            s, t = S[a], S[b]
            if s['c'] is t['c'] or s['o'] == t['o']: continue
            h, v = (s, t) if s['o'] == 'H' else (t, s)
            if h['r'][0] + E < v['k'] < h['r'][1] - E and v['r'][0] + E < h['k'] < v['r'][1] - E: cr += 1
    thru = 0
    for s in S:
        if seg_hits_shape(s['o'], s['k'], s['r'], d, skip=()): thru += 1
    lab = 0; labl = 0
    rs = [(c, lrect(*c.lbox[:4])) for c in d.conns if c.lbox]
    for c, rc in rs:
        for o in d.conns:
            for i, p, q in segs_of(o):
                if rect_seg(rc, p, q, pad=0.0): lab += 1
        for s in d.shapes.values():
            if rect_rect(rc, (s.l, s.t, s.r, s.b)): lab += 1
    for a in range(len(rs)):
        for b in range(a + 1, len(rs)):
            if rect_rect(rs[a][1], rs[b][1]): labl += 1
    return dict(overlap=ov, cross=cr, through_shape=thru, label_hits=lab, label_label=labl)

def finalize(d):
    nudge(d)
    place_labels(d)
    return report(d)
