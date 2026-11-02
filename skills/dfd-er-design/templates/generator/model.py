# -*- coding: utf-8 -*-
"""Loads a diagram spec (JSON) and exposes it to the drawing modules.
Spec keys: system, entities, stores, store_tables, processes, process_breaks, level1_flows,
context, level1, level2, er  (see examples/spare_part.json)."""
import json
SYSTEM = ''; ENT = {}; STORE = {}; STORE_TABLES = {}; P1 = {}; P2 = {}; F1 = []; SPEC = {}
def load(path):
    global SYSTEM, ENT, STORE, STORE_TABLES, P1, P2, F1, SPEC
    import lay
    SPEC = json.load(open(path, encoding='utf-8'))
    SYSTEM = SPEC.get('system', ''); ENT = SPEC['entities']; STORE = SPEC['stores']
    STORE_TABLES = SPEC.get('store_tables', {}); P1 = SPEC['processes']; P2 = {}
    F1 = [tuple(f) for f in SPEC['level1_flows']]
    lay.BR.clear(); lay.BR.update(SPEC.get('process_breaks', {}))
    return SPEC
def _merge(pairs):
    out = {}
    for a, b, l in pairs:
        L = out.setdefault((a, b), [])
        if l not in L: L.append(l)
    return out
def is_proc(n): return n[0].isdigit()
def level1():
    """one arrow per direction per pair; labels of the same direction are merged"""
    return _merge(F1)
def context():
    """derived from Level 1 (balanced by construction): drop stores, collapse processes into 0"""
    pairs = []
    for (a, b), ls in level1().items():
        if a in STORE or b in STORE: continue
        a2 = '0' if is_proc(a) else a; b2 = '0' if is_proc(b) else b
        for l in ls: pairs.append((a2, b2, l))
    return _merge(pairs)
def disp(n): return n[:-2] if n.endswith('.0') else n
