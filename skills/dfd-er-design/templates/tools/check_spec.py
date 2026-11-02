# -*- coding: utf-8 -*-
"""Logic checks on a diagram spec (+ optional Data Dictionary JSON) BEFORE drawing.
Usage: python check_spec.py SPEC.json [DD.json]
Prints the CRUD matrix (Level-1 process x store: W = writes/creates/updates, R = reads) and fails on:
- a store never written (miracle: data used before it is created) or never read (black hole store);
- a process with no input or no output (black hole / miracle process);
- entity<->store or store<->store flows (must pass through a process);
- a process reading a store before any earlier process (or itself) writes it (creation order);
- Level-2 diagrams that are not balanced with their Level-1 parent;
- (with DD) a table in store_tables missing from the DD/ER, an ER relation without an FK, or an FK without an ER line."""
import sys, json
def main(spec_path, dd_path=None):
    S = json.load(open(spec_path, encoding='utf-8')); ENT, ST, P = S['entities'], S['stores'], S['processes']
    F = [tuple(f) for f in S['level1_flows']]; err = []; warn = []
    kind = lambda n: 'E' if n in ENT else 'D' if n in ST else 'P' if n in P else '?'
    for a, b, l in F:
        ka, kb = kind(a), kind(b)
        if '?' in (ka, kb): err.append('unknown node in flow %s -> %s' % (a, b))
        if ka != 'P' and kb != 'P': err.append('flow must touch a process: %s(%s) -> %s(%s) "%s"' % (a, ka, b, kb, l))
    pl = list(P)
    print('CRUD matrix (W = write, R = read)')
    print('%-6s' % '' + ''.join('%-6s' % d for d in ST))
    for p in pl:
        row = ''
        for d in ST:
            w = any(a == p and b == d for a, b, l in F); r = any(a == d and b == p for a, b, l in F)
            row += '%-6s' % (('W' if w else '') + ('R' if r else '') or '.')
        print('%-6s' % p + row)
    for d in ST:
        ws = [pl.index(a) for a, b, l in F if b == d and a in P]; rs = [pl.index(b) for a, b, l in F if a == d and b in P]
        if not ws: err.append('store %s %s is never written (where does its data come from?)' % (d, ST[d]))
        if not rs: err.append('store %s %s is never read (black hole store)' % (d, ST[d]))
        if ws and rs and min(rs) < min(ws): warn.append('store %s is read by %s before it is written by %s (reorder processes: master -> transaction -> report)' % (d, pl[min(rs)], pl[min(ws)]))
    for p in P:
        if not any(b == p for a, b, l in F): err.append('process %s has no input (miracle)' % p)
        if not any(a == p for a, b, l in F): err.append('process %s has no output (black hole)' % p)
    seen = {}
    for a, b, l in F: seen.setdefault((a, b), []).append(l)
    for D2 in S.get('level2', {}).get('diagrams', []):
        p = D2['process']
        o1 = {('X' if a == p else a, 'X' if b == p else b) for a, b, l in F if p in (a, b)}
        o2 = {('X' if a[0].isdigit() else a, 'X' if b[0].isdigit() else b) for a, b, l in D2['flows'] if not (a[0].isdigit() and b[0].isdigit())}
        if o1 != o2: err.append('Level 2 of %s not balanced: only in L1 %s, only in L2 %s' % (p, sorted(o1 - o2), sorted(o2 - o1)))
    if dd_path and 'er' in S:
        DD = json.load(open(dd_path, encoding='utf-8')); tabs = {t['table']: t for t in DD['tables']}
        for d, ts in S.get('store_tables', {}).items():
            for t in ts:
                if t not in tabs: err.append('store %s table %s missing from the Data Dictionary' % (d, t))
                if t not in S['er']['tables']: err.append('store %s table %s missing from the ER' % (d, t))
        fk = {frozenset((t, c['references'])) for t, T in tabs.items() for c in T['columns'] if c['key'] == 'FK'}
        rel = [frozenset((r['parent'], r['child'])) for r in S['er']['relations']]
        if len(rel) != len(set(rel)): err.append('ER has more than one line for a table pair')
        for k in fk - set(rel): err.append('FK without ER line: %s' % ' - '.join(sorted(k)))
        for k in set(rel) - fk: err.append('ER line without FK: %s' % ' - '.join(sorted(k)))
        for t, T in tabs.items():
            used = any(t in ts for ts in S.get('store_tables', {}).values())
            if not used: warn.append('table %s is not mapped to any data store' % t)
    for w in warn: print('WARN', w)
    for e in err: print('ERROR', e)
    print('OK' if not err else '%d error(s)' % len(err)); return not err
if __name__ == '__main__':
    sys.exit(0 if main(*sys.argv[1:3]) else 1)
