# -*- coding: utf-8 -*-
"""Layout helpers: H (horizontal flow), V (vertical flow), R (routed via a channel), store_rows (process + its stores)."""
from draw import Diagram, wrap, LINE, textw
import model
LPT = 14
def fr(S, v, axis='y'):
    return (v - S.t) / S.h if axis == 'y' else (v - S.l) / S.w
def lines(labels, maxw=None):
    return wrap(labels, maxw, LPT) if maxw else list(labels)
def lab_h(n): return n * LINE(LPT) * 1.05 + 0.04
def setpt(p):
    global LPT; LPT = p
def H(d, a, b, y, labels, side='above', maxw=1.9, via=None, lab=None, sa=None, sb=None):
    """straight horizontal flow a->b at y (both shapes must span y)"""
    A, B = d.shapes[a], d.shapes[b]
    if sa is None: sa = 'R' if A.x < B.x else 'L'
    if sb is None: sb = 'L' if A.x < B.x else 'R'
    lb = dict(side=side); lb.update(lab or {})
    return d.conn(a, b, sa, sb, lines(labels, maxw), ta=fr(A, y), tb=fr(B, y), lab=lb, via=via)
def V(d, a, b, x, labels, side="right", maxw=None, lab=None):
    A, B = d.shapes[a], d.shapes[b]
    sa = 'B' if A.y < B.y else 'T'; sb = 'T' if A.y < B.y else 'B'
    lb = dict(side=side); lb.update(lab or {})
    return d.conn(a, b, sa, sb, lines(labels, maxw), ta=fr(A, x, 'x'), tb=fr(B, x, 'x'), lab=lb)
def R(d, a, b, ya, xs, yb, labels, sa=None, sb=None, maxw=None, lab=None):
    """route a(at ya) -> vertical channel x=xs -> b(at yb)"""
    A, B = d.shapes[a], d.shapes[b]
    if sa is None: sa = 'R' if A.x < xs else 'L'
    if sb is None: sb = 'L' if B.x > xs else 'R'
    lb = lab or {}
    return d.conn(a, b, sa, sb, lines(labels, maxw), ta=fr(A, ya), tb=fr(B, yb), via=[('x', xs)], lab=lb)

PW = 2.1    # process width
SH, PAD, PAD2, SPT, PPT = 0.44, 0.1, 0.06, 15, 16
SW = 2.75   # store width
BR = {}     # process-name line breaks, filled from the spec (process_breaks / level2 breaks)
def proc_name(p):
    return BR.get(p) or model.P1.get(p) or model.P2.get(p)
def wrapname(n, w=PW - 0.2, pt=16):
    from draw import split_item
    return '\n'.join(split_item(n, w, pt))
def store_rows(d, p, x_p, x_s, ytop, stores, flows, dupset, minh=1.0, sid_suffix='', top_extra=0):
    """place process p at x_p with its stores stacked at x_s starting at ytop. returns process shape"""
    slots = []
    for D in stores:
        Lw = flows.get((p, D), []); Lr = flows.get((D, p), [])
        h = PAD + (lab_h(len(Lw)) if Lw else 0) + SH + (lab_h(len(Lr)) if Lr else 0) + PAD2
        slots.append((D, Lw, Lr, h))
    tot = sum(s[3] for s in slots) + top_extra
    ph = max(minh, tot + 0.1)
    P = d.add(p, 'proc', x_p, ytop + ph / 2, PW, ph, name=proc_name(p), num=model.disp(p), pt=PPT)
    y = ytop + (ph - tot) / 2 + top_extra
    for D, Lw, Lr, h in slots:
        yc = y + PAD + (lab_h(len(Lw)) if Lw else 0) + SH / 2
        sid = D + '@' + p + sid_suffix
        S = d.add(sid, 'store', x_s, yc, SW, SH, name=model.STORE[D], num=D, pt=SPT, dup=(D in dupset))
        if Lw and Lr:
            H(d, p, sid, yc - SH * 0.2, Lw, side='above', maxw=None)
            H(d, sid, p, yc + SH * 0.2, Lr, side='below', maxw=None)
        elif Lw: H(d, p, sid, yc, Lw, side='above', maxw=None)
        else: H(d, sid, p, yc, Lr, side='above', maxw=None)
        y += h
    return P
