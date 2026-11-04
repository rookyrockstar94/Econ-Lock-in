"""Small engine for drawing IB Economics diagrams as theme-aware inline SVG.

Plot coordinates run 0..100 on both axes. Colours come from CSS classes
(see app.css: .dg-*), so every diagram follows the page's light/dark theme.
"""
import math, re, html

def esc(s): return html.escape(str(s), quote=True)

def lab(s):
    """'P_1' -> P with subscript 1; '^' for superscript. Returns SVG tspans."""
    out = ''
    for part in re.split(r'([_^]\{[^}]*\}|[_^][A-Za-z0-9*+\-]+)', s):
        if not part: continue
        if part[0] in '_^' and len(part) > 1:
            body = part[2:-1] if part[1] == '{' else part[1:]
            dy = '0.32em' if part[0] == '_' else '-0.45em'
            back = '-0.32em' if part[0] == '_' else '0.45em'
            out += f'<tspan dy="{dy}" font-size="72%">{esc(body)}</tspan><tspan dy="{back}"> </tspan>'
        else:
            out += esc(part)
    # trailing hair spaces from tspans are harmless
    return out

class Line:
    def __init__(s, p1, p2): s.p1, s.p2 = p1, p2
    def y_at(s, x):
        (x1, y1), (x2, y2) = s.p1, s.p2
        if x2 == x1: return None
        return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    def x_at(s, y):
        (x1, y1), (x2, y2) = s.p1, s.p2
        if y2 == y1: return None
        return x1 + (x2 - x1) * (y - y1) / (y2 - y1)
    def shifted(s, dx=0, dy=0):
        return Line((s.p1[0]+dx, s.p1[1]+dy), (s.p2[0]+dx, s.p2[1]+dy))

def meet(a, b):
    (x1, y1), (x2, y2) = a.p1, a.p2
    (x3, y3), (x4, y4) = b.p1, b.p2
    d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(d) < 1e-9: raise ValueError('parallel lines')
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / d
    return (x1 + t*(x2-x1), y1 + t*(y2-y1))

def catmull(pts, steps=12):
    """Smooth path through points (Catmull-Rom), returned as list of points."""
    if len(pts) < 3: return pts
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P)-2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(steps):
            t = k/steps; t2, t3 = t*t, t*t*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    out.append(pts[-1])
    return out

class Curve:
    def __init__(s, pts): s.pts = pts
    def y_at(s, x):
        P = s.pts
        for (x1,y1),(x2,y2) in zip(P, P[1:]):
            if min(x1,x2) <= x <= max(x1,x2) and x1 != x2:
                return y1 + (y2-y1)*(x-x1)/(x2-x1)
        return None
    def x_at(s, y):
        P = s.pts
        for (x1,y1),(x2,y2) in zip(P, P[1:]):
            if min(y1,y2) <= y <= max(y1,y2) and y1 != y2:
                return x1 + (x2-x1)*(y-y1)/(y2-y1)
        return None
    def min_pt(s): return min(s.pts, key=lambda p: p[1])

def cmeet(a, b, lo=0.5, hi=99.5):
    """Intersection of two curves/lines by scanning x (first crossing)."""
    f = lambda x: (a.y_at(x) - b.y_at(x)) if a.y_at(x) is not None and b.y_at(x) is not None else None
    prev = None; xp = None
    x = lo
    while x <= hi:
        v = f(x)
        if v is not None and prev is not None and (v == 0 or (v > 0) != (prev > 0)):
            # bisect
            l, r = xp, x
            for _ in range(40):
                m = (l+r)/2; fm = f(m)
                if fm is None: break
                if (fm > 0) == (prev > 0): l = m
                else: r = m
            xm = (l+r)/2
            return (xm, a.y_at(xm))
        if v is not None: prev, xp = v, x
        x += 0.25
    raise ValueError('no intersection')

class G:
    """One panel: axes + elements. Plot coords 0..100."""
    def __init__(s, x='Quantity', y='Price', title=None, w=360, h=300, origin=True, xaxis_mid=False, yaxis_mid=False, noaxes=False, ox=0):
        s.xl, s.yl, s.title = x, y, title
        s.W, s.H = w, h
        s.L, s.R, s.T, s.B = 54, 70, 26 if not title else 40, 40
        s.ox = ox
        s.els = []; s.fg = []; s.bg = []
        s.xmid, s.ymid, s.noaxes = xaxis_mid, yaxis_mid, noaxes
    # coordinate mapping
    def X(s, x): return s.L + (s.W - s.L - s.R) * x / 100
    def Y(s, y): return s.T + (s.H - s.T - s.B) * (100 - y) / 100
    def pt(s, p): return f'{s.X(p[0]):.1f},{s.Y(p[1]):.1f}'

    def line(s, p1, p2, cls='k', label=None, at='end', off=(4, 0), dash=False, w=None):
        L = Line(p1, p2)
        s._path([p1, p2], cls, dash, w)
        if label: s._lab(p2 if at == 'end' else p1, label, cls, off)
        return L
    def curve(s, pts, cls='k', label=None, at='end', off=(4, 0), dash=False, smooth=True, w=None):
        P = catmull(pts) if smooth else pts
        s._path(P, cls, dash, w)
        if label: s._lab(P[-1] if at == 'end' else P[0], label, cls, off)
        return Curve(P)
    def fn(s, f, x0, x1, cls='k', label=None, off=(4, 0), dash=False, step=0.5, at='end'):
        P = []; x = x0
        while x <= x1 + 1e-9:
            y = f(x)
            if 0 <= y <= 100: P.append((x, y))
            x += step
        s._path(P, cls, dash, None)
        if label: s._lab(P[-1] if at == 'end' else P[0], label, cls, off)
        return Curve(P)
    def hline(s, y, cls='k', label=None, x0=0, x1=100, dash=False, off=(4, 0), at='end'):
        return s.line((x0, y), (x1, y), cls, label, at, off, dash)
    def vline(s, x, cls='k', label=None, y0=0, y1=100, dash=False, off=(0, -6), at='end'):
        return s.line((x, y0), (x, y1), cls, label, at, off, dash)
    def _path(s, P, cls, dash, w):
        d = 'M' + ' L'.join(s.pt(p) for p in P)
        extra = ' stroke-dasharray="6 5"' if dash else ''
        if w: extra += f' stroke-width="{w}"'
        s.els.append(f'<path class="dg-ln dg-{cls}" d="{d}"{extra}/>')
    def _lab(s, p, text, cls, off, anchor='start'):
        s.fg.append(f'<text class="dg-lab dg-t{cls}" x="{s.X(p[0])+off[0]:.1f}" y="{s.Y(p[1])+off[1]+4:.1f}" text-anchor="{anchor}">{lab(text)}</text>')
    def text(s, p, text, cls='k', anchor='middle', size=None, italic=False):
        st = f' font-size="{size}"' if size else ''
        if italic: st += ' font-style="italic"'
        s.fg.append(f'<text class="dg-note dg-t{cls}" x="{s.X(p[0]):.1f}" y="{s.Y(p[1])+4:.1f}" text-anchor="{anchor}"{st}>{lab(text)}</text>')
    def drop(s, p, ylab=None, xlab=None, to='both', cls='k'):
        x, y = p
        if to in ('both', 'y') and ylab is not None:
            s.els.append(f'<path class="dg-drop" d="M{s.pt((0,y))} L{s.pt(p)}"/>')
            s.fg.append(f'<text class="dg-tick" x="{s.X(0)-6:.1f}" y="{s.Y(y)+4:.1f}" text-anchor="end">{lab(ylab)}</text>')
        if to in ('both', 'x') and xlab is not None:
            s.els.append(f'<path class="dg-drop" d="M{s.pt(p)} L{s.pt((x,0))}"/>')
            s.fg.append(f'<text class="dg-tick" x="{s.X(x):.1f}" y="{s.Y(0)+17:.1f}" text-anchor="middle">{lab(xlab)}</text>')
    def ytick(s, y, text):
        s.fg.append(f'<text class="dg-tick" x="{s.X(0)-6:.1f}" y="{s.Y(y)+4:.1f}" text-anchor="end">{lab(text)}</text>')
    def xtick(s, x, text):
        s.fg.append(f'<text class="dg-tick" x="{s.X(x):.1f}" y="{s.Y(0)+17:.1f}" text-anchor="middle">{lab(text)}</text>')
    def dot(s, p, label=None, off=(6, -8), anchor='start', cls='k'):
        s.fg.append(f'<circle class="dg-dot dg-f{cls}" cx="{s.X(p[0]):.1f}" cy="{s.Y(p[1]):.1f}" r="3.6"/>')
        if label: s._lab(p, label, 'k', off, anchor)
    def area(s, pts, cls='cs', label=None, at=None):
        s.bg.append(f'<polygon class="dg-a dg-a{cls}" points="{" ".join(s.pt(p) for p in pts)}"/>')
        if label:
            c = at or (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
            s.fg.append(f'<text class="dg-alab" x="{s.X(c[0]):.1f}" y="{s.Y(c[1])+4:.1f}" text-anchor="middle">{lab(label)}</text>')
    def arrow(s, p1, p2, cls='k'):
        x1, y1, x2, y2 = s.X(p1[0]), s.Y(p1[1]), s.X(p2[0]), s.Y(p2[1])
        a = math.atan2(y2-y1, x2-x1); h = 7
        hx1, hy1 = x2 - h*math.cos(a-0.45), y2 - h*math.sin(a-0.45)
        hx2, hy2 = x2 - h*math.cos(a+0.45), y2 - h*math.sin(a+0.45)
        s.fg.append(f'<path class="dg-arr dg-{cls}" d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} M{hx1:.1f},{hy1:.1f} L{x2:.1f},{y2:.1f} L{hx2:.1f},{hy2:.1f}"/>')
    def brace(s, x0, x1, y, text, below=True):
        """Horizontal bracket between x0 and x1 at height y, with label."""
        d = -1 if below else 1
        Y0 = s.Y(y); t = 5*d*-1
        s.fg.append(f'<path class="dg-brace" d="M{s.X(x0):.1f},{Y0:.1f} l0,{t} L{s.X(x1):.1f},{Y0+t:.1f} l0,{-t}"/>')
        s.fg.append(f'<text class="dg-note" x="{(s.X(x0)+s.X(x1))/2:.1f}" y="{Y0+t*3.2+4:.1f}" text-anchor="middle">{lab(text)}</text>')

    def render(s):
        x0, y0, x1, y1 = s.X(0), s.Y(0), s.X(100), s.Y(100)
        out = []
        if s.title:
            out.append(f'<text class="dg-ptitle" x="{(x0+x1)/2:.1f}" y="18" text-anchor="middle">{lab(s.title)}</text>')
        out += s.bg
        if not s.noaxes:
            ya = s.Y(50) if s.xmid else y0
            out.append(f'<path class="dg-axis" d="M{x0:.1f},{y1-6:.1f} L{x0:.1f},{y0:.1f} M{x0:.1f},{ya:.1f} L{x1+6:.1f},{ya:.1f}"/>')
            out.append(f'<path class="dg-axis" d="M{x0-4:.1f},{y1-2:.1f} L{x0:.1f},{y1-8:.1f} L{x0+4:.1f},{y1-2:.1f} M{x1+2:.1f},{ya-4:.1f} L{x1+8:.1f},{ya:.1f} L{x1+2:.1f},{ya+4:.1f}"/>')
            out.append(f'<text class="dg-axlab" x="{x0-8:.1f}" y="{y1-12:.1f}" text-anchor="start">{lab(s.yl)}</text>' if len(s.yl) <= 26 else '')
            out.append(f'<text class="dg-axlab" x="{x1+8:.1f}" y="{ya+30:.1f}" text-anchor="end">{lab(s.xl)}</text>')
            if not s.xmid: out.append(f'<text class="dg-tick" x="{x0-6:.1f}" y="{y0+15:.1f}" text-anchor="end">0</text>')
        out += s.els + s.fg
        return '\n'.join(out)

def figure(*panels, gap=18):
    """Combine panels left to right into one SVG string."""
    ox = 0; parts = []
    H = max(p.H for p in panels)
    for p in panels:
        parts.append(f'<g transform="translate({ox},0)">' + p.render() + '</g>')
        ox += p.W + gap
    W = ox - gap
    return f'<svg class="dg" viewBox="0 0 {W} {H}" role="img" xmlns="http://www.w3.org/2000/svg">' + '\n'.join(parts) + '</svg>'

# ---------- flow diagrams (circular flow, poverty cycle) ----------
class Flow:
    def __init__(s, w=640, h=360): s.W, s.H, s.parts = w, h, []
    def box(s, x, y, w, h, text, cls='k'):
        s.parts.append(f'<rect class="fl-box fl-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>')
        lines = text.split('\n')
        for i, t in enumerate(lines):
            yy = y + h/2 + (i - (len(lines)-1)/2) * 16 + 5
            s.parts.append(f'<text class="fl-t" x="{x+w/2}" y="{yy:.1f}" text-anchor="middle">{lab(t)}</text>')
        return (x, y, w, h)
    def arrow(s, pts, text=None, at=None, cls='k', anchor='middle', curve=False):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        a = math.atan2(yb-ya, xb-xa); h = 8
        d += f' M{xb-h*math.cos(a-0.42):.1f},{yb-h*math.sin(a-0.42):.1f} L{xb:.1f},{yb:.1f} L{xb-h*math.cos(a+0.42):.1f},{yb-h*math.sin(a+0.42):.1f}'
        s.parts.append(f'<path class="fl-arr fl-{cls}" d="{d}"/>')
        if text:
            tx, ty = at if at else ((pts[0][0]+pts[-1][0])/2, (pts[0][1]+pts[-1][1])/2 - 6)
            for i, t in enumerate(text.split('\n')):
                s.parts.append(f'<text class="fl-n fl-t{cls}" x="{tx}" y="{ty + i*14:.1f}" text-anchor="{anchor}">{lab(t)}</text>')
    def text(s, x, y, t, cls='k', anchor='middle'):
        s.parts.append(f'<text class="fl-n fl-t{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{lab(t)}</text>')
    def render(s):
        return f'<svg class="dg fl" viewBox="0 0 {s.W} {s.H}" role="img" xmlns="http://www.w3.org/2000/svg">' + '\n'.join(s.parts) + '</svg>'
