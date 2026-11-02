# -*- coding: utf-8 -*-
"""Context Diagram: process 0 in the middle, entities left/right (horizontal pairs) or below (vertical)."""
from lay import *
import lay, model
def build():
    C = model.context(); S = model.SPEC['context']
    lay.setpt(S['label_pt'])
    d = Diagram(S['name'], S['canvas'][0], S['canvas'][1], lpt=S['label_pt'])
    p = S['process']
    d.add('0', 'proc', p['x'], p['y'], p['w'], p['h'], name=p['name'], num='0', pt=p['pt'])
    for e in S['entities']:
        d.add(e['id'], 'ent', e['x'], e['y'], e.get('w', 1.8), S['entity_h'], name=model.ENT[e['id']], pt=S['entity_pt'])
    off = S.get('horizontal_offset', 0.15)
    for k in S['horizontal']:
        E = d.shapes[k]
        if (k, '0') in C: H(d, k, '0', E.y - off, C[(k, '0')], side='above', maxw=None)
        if ('0', k) in C: H(d, '0', k, E.y + off, C[('0', k)], side='below', maxw=None)
    for k in S['vertical']:
        if ('0', k) in C: V(d, '0', k, d.shapes[k].x, C[('0', k)], side='right')
        if (k, '0') in C: V(d, k, '0', d.shapes[k].x, C[(k, '0')], side='right')
    d.solve(); return d
