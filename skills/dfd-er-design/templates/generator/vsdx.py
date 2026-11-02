# -*- coding: utf-8 -*-
import zipfile, os
from xml.sax.saxutils import escape, quoteattr
from draw import VFONT, LINE, K
EX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
NS = "xmlns='http://schemas.microsoft.com/office/visio/2012/main' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' xml:space='preserve'"

def cell(n, v, f=None, u=None):
    s = "<Cell N='%s' V=%s" % (n, quoteattr(str(v)))
    if u: s += " U='%s'" % u
    if f is not None: s += " F=%s" % quoteattr(f)
    return s + '/>'

def num(v): return '%.6f' % v

def char(pt, bold=False):
    return ("<Section N='Character'><Row IX='0'>" + cell('Font', VFONT) + cell('Color', '#000000') +
            cell('Style', 1 if bold else 0) + cell('Size', num(pt * K / 72.0), u='PT') +
            cell('ComplexScriptFont', VFONT) + cell('ComplexScriptSize', num(pt * K / 72.0), u='PT') +
            cell('AsianFont', VFONT) + cell('LangID', 'th-TH') + "</Row></Section>")

def para(h=1, spline=None):
    s = "<Section N='Paragraph'><Row IX='0'>" + cell('HorzAlign', h)
    if spline is not None: s += cell('SpLine', num(spline), u='PT')  # value in inches
    return s + "</Row></Section>"

def geom(ix, rows, nofill=0, noline=0):
    s = "<Section N='Geometry' IX='%d'>" % ix + cell('NoFill', nofill) + cell('NoLine', noline) + cell('NoShow', 0) + cell('NoSnap', 0)
    for i, (t, x, y, fx, fy) in enumerate(rows):
        s += "<Row T='%s' IX='%d'>" % (t, i + 1) + cell('X', num(x), fx) + cell('Y', num(y), fy) + "</Row>"
    return s + "</Section>"

def rect_rows(w, h):
    return [('MoveTo', 0, 0, '0', '0'), ('LineTo', w, 0, 'Width*1', '0'), ('LineTo', w, h, 'Width*1', 'Height*1'),
            ('LineTo', 0, h, '0', 'Height*1'), ('LineTo', 0, 0, 'Geometry%d.X1', 'Geometry%d.Y1')]

def rect_geom(ix, w, h, nofill=0, noline=0):
    rows = rect_rows(w, h)
    rows[-1] = ('LineTo', 0, 0, 'Geometry%d.X1' % (ix + 1), 'Geometry%d.Y1' % (ix + 1))
    return geom(ix, rows, nofill, noline)

def xform(px, py, w, h, extra=''):
    return (cell('PinX', num(px)) + cell('PinY', num(py)) + cell('Width', num(w)) + cell('Height', num(h)) +
            cell('LocPinX', num(w / 2), 'Width*0.5') + cell('LocPinY', num(h / 2), 'Height*0.5') + cell('Angle', 0) + extra)

LINEF = cell('LineWeight', '0.01041666666666667', u='PT') + cell('LineColor', '#000000') + cell('LinePattern', 1)
FILLW = cell('FillForegnd', '#FFFFFF') + cell('FillPattern', 1)
NOFILL = cell('FillPattern', 0)
NOLINE = cell('LinePattern', 0)
ER_HEAD = '#BDD7EE'   # ER table header fill (light blue); body stays white

def conn_section(s, H):
    if not s.ports: return ''
    out = "<Section N='Connection'>"
    for i, (lx, ly) in enumerate(s.ports):
        out += "<Row IX='%d'>" % i + cell('X', num(lx)) + cell('Y', num(s.h - ly)) + cell('DirX', 0) + cell('DirY', 0) + cell('Type', 0) + cell('AutoGen', 0) + "</Row>"
    return out + "</Section>"

def text(t): return "<Text>%s</Text>" % escape(t)

class W:
    def __init__(w, d):
        w.d = d; w.H = d.H; w.next = 1; w.sid = {}
    def nid(w):
        i = w.next; w.next += 1; return i

def shape_xml(w, s):
    H = w.H; d = w.d
    gid = w.nid(); w.sid[s.id] = gid
    px, py = s.x, H - s.y
    attr = "ID='%d' NameU='%s.%d' Name='%s.%d' LineStyle='3' FillStyle='3' TextStyle='3'" % (gid, s.kind, gid, s.kind, gid)
    if s.kind == 'ent':
        x = "<Shape %s Type='Shape'>" % attr + xform(px, py, s.w, s.h) + LINEF + NOFILL + cell('VerticalAlign', 1)
        x += char(s.pt) + para(1, LINE(s.pt) * 1.05) + conn_section(s, H) + rect_geom(0, s.w, s.h, nofill=1)
        if s.dup:
            x += geom(1, [('MoveTo', 0, s.h - 0.16, '0', 'Height-0.16'), ('LineTo', 0.16, s.h, '0.16', 'Height*1')], nofill=1)
        return x + text(s.name) + "</Shape>"
    if s.kind == 'proc':
        # group = outline + connection points; child 1 = header band holding the process NUMBER; child 2 = process name
        hh = 0.32
        x = "<Shape %s Type='Group'>" % attr + xform(px, py, s.w, s.h) + LINEF + NOFILL
        x += cell('SelectMode', 0) + cell('DisplayMode', 1) + cell('IsTextEditTarget', 0)
        x += conn_section(s, H) + rect_geom(0, s.w, s.h, nofill=1)
        x += "<Shapes>"
        cid = w.nid()
        x += "<Shape ID='%d' NameU='ProcessNumber.%d' Name='ProcessNumber.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (cid, cid, cid)
        x += (cell('PinX', num(s.w / 2), 'Sheet.%d!Width*0.5' % gid) + cell('PinY', num(s.h - hh / 2), 'Sheet.%d!Height-%g' % (gid, hh / 2)) +
              cell('Width', num(s.w), 'Sheet.%d!Width*1' % gid) + cell('Height', num(hh)) +
              cell('LocPinX', num(s.w / 2), 'Width*0.5') + cell('LocPinY', num(hh / 2), 'Height*0.5') + cell('Angle', 0))
        x += LINEF + NOFILL + cell('VerticalAlign', 1) + cell('TopMargin', num(0), u='PT') + cell('BottomMargin', num(0), u='PT')
        x += char(s.pt, True) + para(1)
        x += geom(0, [('MoveTo', 0, 0, '0', '0'), ('LineTo', s.w, 0, 'Width*1', '0')], nofill=1)
        x += text(s.num) + "</Shape>"
        cid = w.nid(); bh = s.h - hh
        x += "<Shape ID='%d' NameU='ProcessName.%d' Name='ProcessName.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (cid, cid, cid)
        x += (cell('PinX', num(s.w / 2), 'Sheet.%d!Width*0.5' % gid) + cell('PinY', num(bh / 2), '(Sheet.%d!Height-%g)*0.5' % (gid, hh)) +
              cell('Width', num(s.w), 'Sheet.%d!Width*1' % gid) + cell('Height', num(bh), 'Sheet.%d!Height-%g' % (gid, hh)) +
              cell('LocPinX', num(s.w / 2), 'Width*0.5') + cell('LocPinY', num(bh / 2), 'Height*0.5') + cell('Angle', 0))
        x += NOLINE + NOFILL + cell('VerticalAlign', 1) + char(s.pt) + para(1, LINE(s.pt) * 1.05)
        x += rect_geom(0, s.w, bh, nofill=1, noline=1)
        x += text(s.name) + "</Shape></Shapes></Shape>"
        return x
    if s.kind == 'store':
        iw = 0.45
        x = "<Shape %s Type='Group'>" % attr + xform(px, py, s.w, s.h) + LINEF + NOFILL + cell('VerticalAlign', 1)
        x += cell('LeftMargin', num(0.02), u='IN') + cell('RightMargin', num(0.02), u='IN')
        x += cell('TxtPinX', num((s.w + iw) / 2), '(Width+0.45)*0.5') + cell('TxtPinY', num(s.h / 2), 'Height*0.5')
        x += cell('TxtWidth', num(s.w - iw), 'Width-0.45') + cell('TxtHeight', num(s.h), 'Height*1')
        x += cell('TxtLocPinX', num((s.w - iw) / 2), 'TxtWidth*0.5') + cell('TxtLocPinY', num(s.h / 2), 'TxtHeight*0.5') + cell('TxtAngle', 0)
        x += cell('SelectMode', 0) + cell('DisplayMode', 1) + cell('IsTextEditTarget', 1)
        x += char(s.pt) + para(1, LINE(s.pt) * 1.05) + conn_section(s, H)
        x += rect_geom(0, s.w, s.h, nofill=1, noline=1)
        x += geom(1, [('MoveTo', s.w, s.h, 'Width*1', 'Height*1'), ('LineTo', 0, s.h, '0', 'Height*1'), ('LineTo', 0, 0, '0', '0'), ('LineTo', s.w, 0, 'Width*1', '0')], nofill=1)
        x += geom(2, [('MoveTo', iw, 0, '0.45', '0'), ('LineTo', iw, s.h, '0.45', 'Height*1')], nofill=1)
        if s.dup:
            x += geom(3, [('MoveTo', 0.07, 0, '0.07', '0'), ('LineTo', 0.07, s.h, '0.07', 'Height*1')], nofill=1)
        x += text(s.name)
        cid = w.nid(); ox = iw / 2 + (0.035 if s.dup else 0)
        x += "<Shapes><Shape ID='%d' NameU='id.%d' Name='id.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (cid, cid, cid)
        x += (cell('PinX', num(ox)) + cell('PinY', num(s.h / 2), 'Sheet.%d!Height*0.5' % gid) + cell('Width', num(iw)) +
              cell('Height', num(s.h), 'Sheet.%d!Height*1' % gid) + cell('LocPinX', num(iw / 2), 'Width*0.5') + cell('LocPinY', num(s.h / 2), 'Height*0.5') + cell('Angle', 0))
        x += NOLINE + NOFILL + cell('VerticalAlign', 1) + char(s.pt, True) + para(1) + rect_geom(0, iw, s.h, nofill=1, noline=1)
        x += text(s.num) + "</Shape></Shapes></Shape>"
        return x
    if s.kind == 'erent':
        rh = s.rh; n = len(s.rows)
        x = "<Shape %s Type='Group'>" % attr + xform(px, py, s.w, s.h) + LINEF + FILLW
        x += cell('VerticalAlign', 0) + cell('TopMargin', num(0.0), u='IN') + cell('LeftMargin', num(0.08), u='IN')
        x += cell('TxtPinX', num((s.w + 0.42) / 2), '(Width+0.42)*0.5') + cell('TxtPinY', num((s.h - rh) / 2), '(Height-%s)*0.5' % num(rh))
        x += cell('TxtWidth', num(s.w - 0.42), 'Width-0.42') + cell('TxtHeight', num(s.h - rh), 'Height-%s' % num(rh))
        x += cell('TxtLocPinX', num((s.w - 0.42) / 2), 'TxtWidth*0.5') + cell('TxtLocPinY', num((s.h - rh) / 2), 'TxtHeight*0.5') + cell('TxtAngle', 0)
        x += cell('SelectMode', 0) + cell('DisplayMode', 1) + cell('IsTextEditTarget', 1)
        x += char(s.pt - 2) + para(0, rh) + conn_section(s, H) + rect_geom(0, s.w, s.h)
        x += geom(1, [('MoveTo', 0.42, 0, '0.42', '0'), ('LineTo', 0.42, s.h - rh, '0.42', 'Height-%s' % num(rh))], nofill=1)
        x += text('\n'.join(a for k, a in s.rows))
        hid = w.nid()
        x += "<Shapes><Shape ID='%d' NameU='head.%d' Name='head.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (hid, hid, hid)
        x += (cell('PinX', num(s.w / 2), 'Sheet.%d!Width*0.5' % gid) + cell('PinY', num(s.h - rh / 2), 'Sheet.%d!Height-%s' % (gid, num(rh / 2))) +
              cell('Width', num(s.w), 'Sheet.%d!Width*1' % gid) + cell('Height', num(rh)) + cell('LocPinX', num(s.w / 2), 'Width*0.5') + cell('LocPinY', num(rh / 2), 'Height*0.5') + cell('Angle', 0))
        x += LINEF + cell('FillForegnd', ER_HEAD) + cell('FillPattern', 1) + cell('VerticalAlign', 1) + char(s.pt, True) + para(1) + rect_geom(0, s.w, rh)
        x += text(s.name) + "</Shape>"
        kid = w.nid()
        x += "<Shape ID='%d' NameU='keys.%d' Name='keys.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (kid, kid, kid)
        x += (cell('PinX', num(0.21)) + cell('PinY', num((s.h - rh) / 2), 'Sheet.%d!(Height-%s)*0.5' % (gid, num(rh)) if False else cell('PinY', num((s.h - rh) / 2))) +
              cell('Width', num(0.42)) + cell('Height', num(s.h - rh)) + cell('LocPinX', num(0.21), 'Width*0.5') + cell('LocPinY', num((s.h - rh) / 2), 'Height*0.5') + cell('Angle', 0))
        x += NOLINE + NOFILL + cell('VerticalAlign', 0) + cell('TopMargin', num(0.0), u='IN') + char(s.pt - 2, True) + para(1, rh) + rect_geom(0, 0.42, s.h - rh, nofill=1, noline=1)
        x += text('\n'.join(k for k, a in s.rows)) + "</Shape></Shapes></Shape>"
        return x
    raise ValueError(s.kind)

def conn_xml(w, c):
    H = w.H
    cid = w.nid()
    pts = [(x, H - y) for x, y in c.pts]
    bx, by = pts[0]; ex, ey = pts[-1]
    W_, H_ = ex - bx, ey - by
    A, B = w.sid[c.a], w.sid[c.b]
    fa = 'PAR(PNT(Sheet.%d!Connections.X%d,Sheet.%d!Connections.Y%d))' % (A, c.pa_i + 1, A, c.pa_i + 1)
    fb = 'PAR(PNT(Sheet.%d!Connections.X%d,Sheet.%d!Connections.Y%d))' % (B, c.pb_i + 1, B, c.pb_i + 1)
    x = "<Shape ID='%d' NameU='Dynamic connector.%d' Name='Dynamic connector.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (cid, cid, cid)
    x += cell('PinX', num((bx + ex) / 2), 'GUARD((BeginX+EndX)/2)') + cell('PinY', num((by + ey) / 2), 'GUARD((BeginY+EndY)/2)')
    x += cell('Width', num(W_), 'GUARD(EndX-BeginX)') + cell('Height', num(H_), 'GUARD(EndY-BeginY)')
    x += cell('LocPinX', num(W_ / 2), 'GUARD(Width*0.5)') + cell('LocPinY', num(H_ / 2), 'GUARD(Height*0.5)') + cell('Angle', 0)
    x += cell('BeginX', num(bx), fa) + cell('BeginY', num(by), fa) + cell('EndX', num(ex), fb) + cell('EndY', num(ey), fb)
    x += cell('ObjType', 2) + cell('ShapeRouteStyle', 1) + cell('ConLineRouteExt', 1) + cell('ConFixedCode', 0) + cell('GlueType', 0)
    x += cell('BegTrigger', 2, '_XFTRIGGER(Sheet.%d!EventXFMod)' % A) + cell('EndTrigger', 2, '_XFTRIGGER(Sheet.%d!EventXFMod)' % B)
    x += LINEF + NOFILL + cell('BeginArrow', c.ba) + cell('EndArrow', c.ea) + cell('BeginArrowSize', 1) + cell('EndArrowSize', 1)
    x += cell('LineJumpStyle', 0) + cell('ShapePlowCode', 0)
    if c.lbox:
        cx, cy, tw, th, pt = c.lbox
        cy = H - cy
        x += cell('TxtPinX', num(cx - bx)) + cell('TxtPinY', num(cy - by)) + cell('TxtWidth', num(tw + 0.06)) + cell('TxtHeight', num(th))
        x += cell('TxtLocPinX', num((tw + 0.06) / 2), 'TxtWidth*0.5') + cell('TxtLocPinY', num(th / 2), 'TxtHeight*0.5') + cell('TxtAngle', 0)
        x += cell('VerticalAlign', 1) + cell('LeftMargin', 0, u='PT') + cell('RightMargin', 0, u='PT') + cell('TopMargin', 0, u='PT') + cell('BottomMargin', 0, u='PT')
        x += char(pt) + para(1, LINE(pt) * 1.05)
    rows = [('MoveTo', 0, 0, None, None)]
    for (px, py) in pts[1:]:
        rows.append(('LineTo', px - bx, py - by, None, None))
    x += geom(0, rows, nofill=1)
    if c.labels: x += text('\n'.join(c.labels))
    x += "</Shape>"
    connects = ("<Connect FromSheet='%d' FromCell='BeginX' FromPart='9' ToSheet='%d' ToCell='Connections.X%d' ToPart='%d'/>" % (cid, A, c.pa_i + 1, 100 + c.pa_i) +
                "<Connect FromSheet='%d' FromCell='EndX' FromPart='12' ToSheet='%d' ToCell='Connections.X%d' ToPart='%d'/>" % (cid, B, c.pb_i + 1, 100 + c.pb_i))
    return x, connects

def text_xml(w, t):
    x0, y0, s, pt, b = t
    tid = w.nid()
    tw = 4.0; th = pt / 72 * 1.4 * (s.count('\n') + 1)
    x = "<Shape ID='%d' NameU='Text.%d' Name='Text.%d' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>" % (tid, tid, tid)
    x += xform(x0, w.H - y0, tw, th) + NOLINE + NOFILL + char(pt, b) + para(1) + rect_geom(0, tw, th, nofill=1, noline=1) + text(s) + "</Shape>"
    return x

def write(d, path):
    w = W(d)
    shapes = ''.join(shape_xml(w, s) for s in d.shapes.values())
    cx = ''; cn = ''
    for c in d.conns:
        a, b = conn_xml(w, c); cx += a; cn += b
    tx = ''.join(text_xml(w, t) for t in d.texts)
    page = ("<?xml version='1.0' encoding='utf-8' ?><PageContents %s><Shapes>%s%s%s</Shapes><Connects>%s</Connects></PageContents>" % (NS, shapes, cx, tx, cn))
    pages = ("<?xml version='1.0' encoding='utf-8' ?><Pages %s><Page ID='0' NameU='Page-1' Name='Page-1' ViewScale='-1' ViewCenterX='%s' ViewCenterY='%s'><PageSheet LineStyle='0' FillStyle='0' TextStyle='0'>" % (NS, num(d.W / 2), num(d.H / 2)) +
             cell('PageWidth', num(d.W), u='IN') + cell('PageHeight', num(d.H), u='IN') + cell('ShdwOffsetX', '0.125') + cell('ShdwOffsetY', '-0.125') +
             cell('PageScale', 1, u='IN') + cell('DrawingScale', 1, u='IN') + cell('DrawingSizeType', 0) + cell('DrawingScaleType', 0) + cell('InhibitSnap', 0) +
             cell('UIVisibility', 0) + cell('ShdwType', 0) + cell('ShdwObliqueAngle', 0) + cell('ShdwScaleFactor', 1) + cell('DrawingResizeType', 1) +
             cell('RouteStyle', 1) + cell('PageLineJumpDirX', 0) + cell('PageLineJumpDirY', 0) + cell('LineJumpCode', 0) +
             cell('PrintPageOrientation', 1 if d.H >= d.W else 2) +
             "</PageSheet><Rel r:id='rId1'/></Page></Pages>")
    doc = open(os.path.join(EX, 'visio_document.xml'), encoding='utf-8').read()
    fn = "<FaceName NameU='TH SarabunPSK' UnicodeRanges='-1593835409 1342185562 0 0' CharSets='1610678659 -2147483648' Panose='2 11 5 0 4 2 0 2 0 3' Flags='324'/>"
    doc = doc.replace('</FaceNames>', fn + '</FaceNames>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/visio/document.xml" ContentType="application/vnd.ms-visio.drawing.main+xml"/>'
          '<Override PartName="/visio/pages/pages.xml" ContentType="application/vnd.ms-visio.pages+xml"/>'
          '<Override PartName="/visio/pages/page1.xml" ContentType="application/vnd.ms-visio.page+xml"/>'
          '<Override PartName="/visio/windows.xml" ContentType="application/vnd.ms-visio.windows+xml"/>'
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/document" Target="visio/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>')
    drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/pages" Target="pages/pages.xml"/>'
             '<Relationship Id="rId2" Type="http://schemas.microsoft.com/visio/2010/relationships/windows" Target="windows.xml"/></Relationships>')
    prels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/page" Target="page1.xml"/></Relationships>')
    app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Visio</Application><AppVersion>16.0000</AppVersion></Properties>')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:title>%s</dc:title><dc:language>th-TH</dc:language></cp:coreProperties>' % escape(d.name))
    win = ("<?xml version='1.0' encoding='utf-8' ?><Windows ClientWidth='1920' ClientHeight='900' %s><Window ID='0' WindowType='Drawing' WindowState='1073741824' "
           "ContainerType='Page' Page='0' ViewScale='-1' ViewCenterX='%s' ViewCenterY='%s'><ShowRulers>1</ShowRulers><ShowGrid>0</ShowGrid><ShowPageBreaks>0</ShowPageBreaks>"
           "<ShowGuides>1</ShowGuides><ShowConnectionPoints>1</ShowConnectionPoints><GlueSettings>9</GlueSettings><SnapSettings>65847</SnapSettings>"
           "<SnapExtensions>34</SnapExtensions><SnapAngles/><DynamicGridEnabled>1</DynamicGridEnabled><TabSplitterPos>0.5</TabSplitterPos></Window></Windows>") % (NS, num(d.W / 2), num(d.H / 2))
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', rels)
        z.writestr('docProps/app.xml', app); z.writestr('docProps/core.xml', core)
        z.writestr('visio/document.xml', doc); z.writestr('visio/_rels/document.xml.rels', drels)
        z.writestr('visio/pages/pages.xml', pages); z.writestr('visio/pages/_rels/pages.xml.rels', prels)
        z.writestr('visio/pages/page1.xml', page); z.writestr('visio/windows.xml', win)
