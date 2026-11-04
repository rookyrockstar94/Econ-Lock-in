"""Build the single-file IB Economics HL study guide.

Content lives in src/content/*.md in a light markup (see README in that folder);
diagrams in diagrams_*.py. Output: ../IB Economics HL Study Guide.html
"""
import re, json, html, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diagrams_reg import DIAS, ORDER
import diagrams_u12, diagrams_u2b, diagrams_u34  # noqa: register diagrams

def esc(s): return html.escape(s, quote=False)
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

LINKS = []  # (src, target) for validation
def inline(s, src=''):
    s = esc(s)
    s = re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', r'<span class="fr"><span>\1</span><span>\2</span></span>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    s = re.sub(r'_\{([^}]*)\}', r'<sub>\1</sub>', s)
    s = re.sub(r'\^\{([^}]*)\}', r'<sup>\1</sup>', s)
    def link(m):
        tgt, txt = m.group(1), m.group(2) if m.group(2) else None
        LINKS.append((src, tgt))
        if tgt.startswith('d:'):
            t = tgt[2:]; return f'<a class="xref dref" href="#d-{t}">{txt or DIAS.get(t, {}).get("title", t)}</a>'
        if tgt.startswith('g:'):
            t = tgt[2:]; return f'<a class="xref gref" href="#glossary" data-term="{t}">{txt or t}</a>'
        return f'<a class="xref" href="#{tgt}">{txt or "@" + tgt}</a>'
    s = re.sub(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', link, s)
    return s

def blocks_to_html(lines, src):
    """Convert body lines (no @terms) to HTML."""
    out = []; i = 0; n = len(lines)
    def para(buf):
        if buf: out.append('<p>' + inline(' '.join(buf), src) + '</p>')
    buf = []
    while i < n:
        ln = lines[i]
        st = ln.strip()
        if not st:
            para(buf); buf = []; i += 1; continue
        if st.startswith(':::'):
            para(buf); buf = []
            kind, _, title = st[3:].partition(' ')
            j = i + 1; inner = []
            depth = 1
            while j < n:
                s2 = lines[j].strip()
                if s2.startswith(':::') and s2 != ':::': depth += 1
                elif s2 == ':::':
                    depth -= 1
                    if depth == 0: break
                inner.append(lines[j]); j += 1
            out.append(box(kind, title.strip(), inner, src))
            i = j + 1; continue
        if st.startswith('{{dia:'):
            para(buf); buf = []
            did = st[6:-2].strip(); LINKS.append((src, 'd:' + did))
            out.append(f'<div class="dslot" data-d="{did}"></div>')
            i += 1; continue
        if st.startswith('#### '):
            para(buf); buf = []
            out.append('<h4>' + inline(st[5:], src) + '</h4>'); i += 1; continue
        if st.startswith('|'):
            para(buf); buf = []
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells): rows.append(cells)
                i += 1
            h = '<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{inline(c, src)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
            h += ''.join('<tr>' + ''.join(f'<td>{inline(c, src)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'
            out.append(h); continue
        if re.match(r'^(\s*)([-*]|\d+\.) ', ln):
            para(buf); buf = []
            items = []
            while i < n and (re.match(r'^(\s*)([-*]|\d+\.) ', lines[i]) or (lines[i].startswith('    ') and lines[i].strip() and items)):
                m = re.match(r'^(\s*)([-*]|\d+\.) (.*)', lines[i])
                if m: items.append((len(m.group(1)) // 2, m.group(2)[0].isdigit(), m.group(3)))
                else: items[-1] = (items[-1][0], items[-1][1], items[-1][2] + ' ' + lines[i].strip())
                i += 1
            out.append(listhtml(items, src)); continue
        buf.append(st); i += 1
    para(buf)
    return '\n'.join(out)

def listhtml(items, src):
    h = ''; stack = []
    for lvl, ordered, text in items:
        tag = 'ol' if ordered else 'ul'
        while len(stack) > lvl + 1: h += f'</li></{stack.pop()}>'
        if len(stack) < lvl + 1:
            stack.append(tag); h += f'<{tag}><li>'
        else: h += '</li><li>'
        h += inline(text, src)
    while stack: h += f'</li></{stack.pop()}>'
    return h

BOXES = {'hl': ('HL only', 'hlbox'), 'tip': ('Exam tip', 'tip'), 'ex': ('Real-world example', 'ex'), 'calc': ('Worked example', 'calc'),
         'warn': ('Common mistakes', 'warn'), 'formula': ('Formula', 'formula'), 'eval': ('Evaluation', 'eval'), 'key': ('Key idea', 'key'),
         'model': ('Model answer', 'model'), 'plan': ('Essay plan', 'plan')}
def box(kind, title, inner, src):
    label, cls = BOXES.get(kind, (kind, kind))
    if kind == 'eval':
        cols = (title.split('|') + ['Limitations'])[:2] if title else ['Strengths', 'Limitations']
        L = [l.strip()[2:] for l in inner if l.strip().startswith('+ ')]
        R = [l.strip()[2:] for l in inner if l.strip().startswith('- ')]
        rest = [l for l in inner if not (l.strip().startswith('+ ') or l.strip().startswith('- '))]
        h = f'<div class="box eval"><div class="box-h">Evaluation</div><div class="evcols"><div><h5>{inline(cols[0].strip(), src)}</h5><ul>' + ''.join(f'<li>{inline(x, src)}</li>' for x in L) + \
            f'</ul></div><div><h5>{inline(cols[1].strip(), src)}</h5><ul>' + ''.join(f'<li>{inline(x, src)}</li>' for x in R) + '</ul></div></div>'
        rb = blocks_to_html(rest, src)
        return h + (f'<div class="evnote">{rb}</div>' if rb.strip() else '') + '</div>'
    if kind == 'formula':
        rows = []
        for l in inner:
            if not l.strip(): continue
            a, _, b = l.strip().partition('::')
            rows.append(f'<div class="fx"><div class="fx-eq">{inline(a.strip(), src)}</div>' + (f'<div class="fx-n">{inline(b.strip(), src)}</div>' if b else '') + '</div>')
        return f'<div class="box formula"><div class="box-h">{inline(title, src) if title else label}</div>{"".join(rows)}</div>'
    body = blocks_to_html(inner, src)
    head = label + (': ' + inline(title, src) if title and kind not in ('hl',) else '')
    if kind == 'hl': head = 'HL only' + (' · ' + inline(title, src) if title else '')
    return f'<div class="box {cls}"><div class="box-h">{head}</div>{body}</div>'

def plain(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()

def parse_file(path):
    """Returns list of units: {id,title,num,topics:[{id,num,title,level,entries:[...]}]}"""
    units = []; unit = topic = entry = None
    lines = open(path, encoding='utf8').read().split('\n')
    def close_entry():
        nonlocal entry
        if entry is not None:
            body = entry.pop('_lines')
            entry['html'] = blocks_to_html(body, entry['id'])
            entry['text'] = plain(entry['html'])
            entry['dias'] = re.findall(r'data-d="([^"]+)"', entry['html'])
            entry = None
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('# '):
            close_entry()
            p = [x.strip() for x in ln[2:].split('|')]
            unit = dict(id=p[0].lower(), title=p[1], blurb=p[2] if len(p) > 2 else '', topics=[]); units.append(unit); topic = None
        elif ln.startswith('## '):
            close_entry()
            p = [x.strip() for x in ln[3:].split('|')]
            tid = 't' + p[0].replace('.', '-') if re.match(r'^\d', p[0]) else p[0]
            topic = dict(id=tid, num=p[0] if re.match(r'^\d', p[0]) else '', title=p[1], level=(p[2] if len(p) > 2 else 'SL'), blurb=(p[3] if len(p) > 3 else ''), entries=[])
            unit['topics'].append(topic)
        elif ln.startswith('### '):
            close_entry()
            p = [x.strip() for x in ln[4:].split('|')]
            entry = dict(id='e-' + p[0], title=p[1], hl=(len(p) > 2 and p[2] == 'HL'), terms=[], _lines=[], topic=topic['id'])
            topic['entries'].append(entry)
        elif ln.strip() == '@terms' and entry is not None:
            i += 1
            while i < len(lines) and lines[i].strip() != '@end':
                if '::' in lines[i]:
                    t, _, d = lines[i].partition('::')
                    entry['terms'].append([t.strip(), d.strip()])
                i += 1
        elif entry is not None:
            entry['_lines'].append(ln)
        i += 1
    close_entry()
    return units

def build():
    C = os.path.join(HERE, 'content')
    syllabus = []
    for f in ['u1.md', 'u2a.md', 'u2b.md', 'u3.md', 'u4.md']:
        p = os.path.join(C, f)
        if not os.path.exists(p): continue
        for u in parse_file(p):
            ex = next((x for x in syllabus if x['id'] == u['id']), None)
            if ex: ex['topics'] += u['topics']
            else: syllabus.append(u)
    extra = {}
    for f in ['exam.md', 'formulas.md']:
        p = os.path.join(C, f)
        if os.path.exists(p): extra[f[:-3]] = parse_file(p)
    # glossary
    gloss = {}
    for u in syllabus + sum(extra.values(), []):
        for t in u['topics']:
            for e in t['entries']:
                for term, d in e['terms']:
                    k = term.lower()
                    if k in gloss: continue
                    gloss[k] = dict(t=term, d=inline(d, e['id']), e=e['id'], u=u['id'], topic=t['id'], hl=e['hl'])
    glossary = sorted(gloss.values(), key=lambda g: re.sub(r'[^a-z0-9]', '', g['t'].lower()))
    # practice
    mcq = parse_mcq(os.path.join(C, 'mcq.md'))
    essays = parse_essays(os.path.join(C, 'essays.md'))
    dias = [dict(DIAS[d]) for d in ORDER]
    # validate links
    ids = set()
    for u in syllabus + sum(extra.values(), []):
        ids.add(u['id'])
        for t in u['topics']:
            ids.add(t['id']); ids.update(e['id'] for e in t['entries'])
    bad = [(s, t) for s, t in LINKS if not (t.startswith('d:') and t[2:] in DIAS) and not t.startswith('g:') and t not in ids and t not in ('home', 'diagrams', 'glossary', 'formulas', 'exam', 'practice', 'missing')]
    if bad: print('BAD LINKS:', bad[:40])
    for d in dias:
        if d['topic'] not in ids: print('diagram topic missing', d['id'], d['topic'])
    data = dict(units=syllabus, exam=extra.get('exam', []), formulas=extra.get('formulas', []), glossary=glossary, dias=dias, mcq=mcq, essays=essays)
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    shell = open(os.path.join(HERE, 'shell.html'), encoding='utf8').read()
    css = open(os.path.join(HERE, 'app.css'), encoding='utf8').read()
    app = open(os.path.join(HERE, 'app.js'), encoding='utf8').read()
    SKEL = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>'
    out = SKEL + shell.replace('/*CSS*/', css).replace('/*DATA*/', js).replace('/*APP*/', app)
    out += '</body></html>'
    dst = os.path.join(HERE, '..', 'Econ Lock-In.html')
    open(dst, 'w', encoding='utf8').write(out)
    ne = sum(len(t['entries']) for u in syllabus for t in u['topics'])
    print(f'units {len(syllabus)} topics {sum(len(u["topics"]) for u in syllabus)} entries {ne} terms {len(glossary)} diagrams {len(dias)} mcq {len(mcq)} essays {len(essays)} size {len(out)//1024}KB')

def parse_mcq(p):
    if not os.path.exists(p): return []
    qs = []; q = None
    for ln in open(p, encoding='utf8'):
        ln = ln.rstrip('\n')
        if ln.startswith('? '):
            q = dict(q=inline(ln[2:]), a=[], c=0, x='', t=''); qs.append(q)
        elif q is None: continue
        elif ln.startswith('* '): q['c'] = len(q['a']); q['a'].append(inline(ln[2:]))
        elif ln.startswith('- '): q['a'].append(inline(ln[2:]))
        elif ln.startswith('> '): q['x'] += inline(ln[2:])
        elif ln.startswith('@ '): q['t'] = ln[2:].strip()
    return qs

def parse_essays(p):
    if not os.path.exists(p): return []
    out = []; cur = None; lines = []
    def close():
        if cur: cur['html'] = blocks_to_html(lines, cur['id']); out.append(cur)
    for ln in open(p, encoding='utf8').read().split('\n'):
        if ln.startswith('### '):
            close(); lines = []
            pp = [x.strip() for x in ln[4:].split('|')]
            cur = dict(id=pp[0], q=inline(pp[1]), paper=pp[2], marks=pp[3], t=pp[4] if len(pp) > 4 else '')
        elif cur is not None: lines.append(ln)
    close()
    return out

if __name__ == '__main__':
    build()
