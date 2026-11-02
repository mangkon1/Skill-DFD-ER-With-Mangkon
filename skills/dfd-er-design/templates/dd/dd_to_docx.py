# -*- coding: utf-8 -*-
"""Build Data Dictionary tables (report format) from a DD JSON, cloning the caption + table of dd_template.docx.
Usage: python dd_to_docx.py dd_spare_part.json out.docx [--template dd_template.docx]
Format kept from the template: caption 'ตารางที่ 3.x␣␣table (ไทย)' above the table (regular, justified, keepNext),
8 columns 1750/1700/980/500/650/920/500/1300 twips (= 8300, fixed layout), TH SarabunPSK 15 pt, header row bold and
repeated on every page, rows cantSplit. Text is replaced run-by-run so fonts and the Thai cs flags stay."""
import sys, json, copy, os, argparse
import docx
from docx.oxml.ns import qn
KEYS = ["name", "description", "type", "size", "not_null", "unique", "key", "references"]
def set_cell(tc, text):
    ts = list(tc.iter(qn('w:t')))
    if ts:
        ts[0].text = text; ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        for t in ts[1:]: t.text = ''
    else:  # empty cell: copy the run formatting of the paragraph mark
        p = tc.find(qn('w:p')); ppr = p.find(qn('w:pPr'))
        r = p.makeelement(qn('w:r'), {})
        if ppr is not None and ppr.find(qn('w:rPr')) is not None: r.append(copy.deepcopy(ppr.find(qn('w:rPr'))))
        t = r.makeelement(qn('w:t'), {}); t.text = text; r.append(t); p.append(r)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dd'); ap.add_argument('out')
    ap.add_argument('--template', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dd_template.docx'))
    a = ap.parse_args()
    D = json.load(open(a.dd, encoding='utf-8'))
    doc = docx.Document(a.template); body = doc.element.body
    tbl = body.find(qn('w:tbl')); cap = tbl.getprevious()
    rows = tbl.findall(qn('w:tr')); head, sample, sample_empty = rows[0], rows[1], rows[2]
    anchor = cap
    for T in D['tables']:
        c2 = copy.deepcopy(cap); ts = list(c2.iter(qn('w:t')))
        ts[0].text = D['caption_format'].format(**T); ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        for t in ts[1:]: t.text = ''
        t2 = copy.deepcopy(tbl)
        for r in t2.findall(qn('w:tr'))[1:]: t2.remove(r)
        for col in T['columns']:
            src = sample if col.get('description') else sample_empty
            r = copy.deepcopy(sample)
            for tc, k in zip(r.findall(qn('w:tc')), KEYS): set_cell(tc, col.get(k, ''))
            t2.append(r)
        anchor.addprevious(c2); anchor.addprevious(t2)
        sp = docx.oxml.parse_xml('<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
        anchor.addprevious(sp)
    body.remove(cap); body.remove(tbl)
    doc.save(a.out); print('wrote', a.out, len(D['tables']), 'tables')
if __name__ == '__main__': main()
