(function(){
'use strict';
const D = JSON.parse(document.getElementById('data').textContent);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const strip = h => String(h).replace(/<[^>]+>/g, '').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"');
const view = $('#view');

// ---------- indexes ----------
const ALLUNITS = [...D.units, ...D.exam, ...D.formulas];
const UNIT = {}, TOPIC = {}, ENTRY = {}, DIA = {}, TOPIC_SEQ = [];
ALLUNITS.forEach(u => { UNIT[u.id] = u; u.topics.forEach(t => { t.unit = u; TOPIC[t.id] = t; TOPIC_SEQ.push(t); t.entries.forEach(e => { e.topicObj = t; ENTRY[e.id] = e; }); }); });
D.dias.forEach(d => DIA[d.id] = d);
const SYL_TOPICS = D.units.flatMap(u => u.topics);
const SYL_ENTRIES = SYL_TOPICS.flatMap(t => t.entries);
const UNIT_HUE = {u1:'Introduction', u2:'Microeconomics', u3:'Macroeconomics', u4:'The global economy'};
const unitLabel = u => u.id.match(/^u\d/) ? `Unit ${u.id.slice(1)}` : u.title;
const unitOfTopic = tid => TOPIC[tid] ? TOPIC[tid].unit : null;

// ---------- storage & progress ----------
const store = {
  get(k, d){ try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch(e){ return d; } },
  set(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }
};
let P = Object.assign({learnt:{}, flash:{}, quiz:{n:0, c:0}, calc:{n:0, c:0}, last:null, updatedAt:0}, store.get('econ-progress', {}));
let progDoc = null, saveT = null, applyingRemote = false;
function saveP(){
  P.updatedAt = Date.now(); store.set('econ-progress', P);
  if (progDoc && !applyingRemote){ clearTimeout(saveT); saveT = setTimeout(() => { progDoc.set(JSON.parse(JSON.stringify(P))).catch(()=>{}); }, 1200); }
}
(async () => {
  try {
    if (!window.claude || !window.claude.use) return;
    const [db, user] = await Promise.all([window.claude.use('db'), window.claude.use('user')]);
    if (!db || !user) return;
    const id = await user.id(); if (!id) return;
    progDoc = db.doc('data/users/' + id + '/progress');
    let first = true;
    progDoc.onSnapshot(snap => {
      const r = snap.exists ? snap.data() : null;
      if (r && (r.updatedAt || 0) > (P.updatedAt || 0)){
        applyingRemote = true; P = Object.assign({learnt:{}, flash:{}, quiz:{n:0,c:0}, calc:{n:0,c:0}}, r); store.set('econ-progress', P); applyingRemote = false;
        renderRail(); if (['home'].includes(curRoute()) || TOPIC[curRoute()] || UNIT[curRoute()]) route();
      } else if (first && (!r || (P.updatedAt || 0) > (r.updatedAt || 0)) && P.updatedAt){ progDoc.set(JSON.parse(JSON.stringify(P))).catch(()=>{}); }
      first = false;
      $('#syncNote').textContent = 'Progress syncs to your account.';
    }, () => {});
  } catch(e){}
})();
const learntIn = list => list.filter(e => P.learnt[e.id]).length;
function pct(list){ return list.length ? Math.round(100 * learntIn(list) / list.length) : 0; }

// ---------- level & theme ----------
let SL = store.get('econ-sl', false);
function applyLevel(){ document.body.classList.toggle('sl', SL); $('#lvHL').setAttribute('aria-pressed', String(!SL)); $('#lvSL').setAttribute('aria-pressed', String(SL)); }
$('#lvHL').onclick = () => { SL = false; store.set('econ-sl', SL); applyLevel(); };
$('#lvSL').onclick = () => { SL = true; store.set('econ-sl', SL); applyLevel(); toast('SL view: HL-only material hidden'); };
applyLevel();
function applyTheme(t){
  if (t === 'auto'){ document.documentElement.removeAttribute('data-theme'); try{ localStorage.removeItem('econ-theme'); }catch(e){} }
  else { document.documentElement.setAttribute('data-theme', t); try{ localStorage.setItem('econ-theme', t); }catch(e){} }
  $$('[data-th]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.th === t)));
}
$$('[data-th]').forEach(b => b.onclick = () => applyTheme(b.dataset.th));
applyTheme(document.documentElement.getAttribute('data-theme') || 'auto');
let toastT = null;
function toast(msg){ const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => t.hidden = true, 2200); }

// ---------- diagrams ----------
const isWide = d => { const m = d.svg.match(/viewBox="0 0 (\d+)/); return m && +m[1] > 430; };
function figHTML(id){
  const d = DIA[id]; if (!d) return '';
  return `<figure class="fig ${isWide(d)?'wide':''} ${d.hl?'hl-only':''}" id="fig-${id}"><div class="svgwrap">${d.svg}</div>
    <figcaption>${esc(d.title)} ${d.hl?'<span class="badge hl">HL</span>':''}<a href="#d-${id}">Open diagram →</a></figcaption>
    <details><summary>How to draw it and what it shows</summary><ol>${d.steps.map(s=>`<li>${esc(s)}</li>`).join('')}</ol><p>${esc(d.explain)}</p>${d.watch?`<p class="watch"><b>Watch out:</b> ${esc(d.watch)}</p>`:''}</details></figure>`;
}
const LEGEND = `<div class="legend"><span><i style="background:var(--c-d)"></i>demand side</span><span><i style="background:var(--c-s)"></i>supply side</span><span><i style="background:var(--c-c)"></i>costs</span><span><i style="background:var(--c-m)"></i>marginal revenue</span><span><i style="background:var(--c-g)"></i>government</span></div>`;

// ---------- rail ----------
function renderRail(){
  const r = curRoute(); const t = TOPIC[r] || (ENTRY[r] && ENTRY[r].topicObj); const u = UNIT[r] || (t && t.unit);
  let h = `<a href="#home" class="${r==='home'?'on':''}"><span>Home</span></a><div class="grp">Syllabus</div>`;
  D.units.forEach(U => {
    const ents = U.topics.flatMap(x => x.entries);
    h += `<a href="#${U.id}" class="${u===U && !t?'on':''}"><span class="num">${U.id.slice(1)}</span><span>${esc(U.title)}</span><span class="n">${pct(ents)}%</span></a>`;
    if (u === U){
      h += '<div class="sub">' + U.topics.map(T => `<a href="#${T.id}" class="${t===T?'on':''} ${T.level==='HL'?'hl-only':''}"><span class="num">${T.num}</span><span>${esc(T.title)}</span>${T.level==='HL'?'<span class="n">HL</span>':''}</a>` +
        (t === T ? '<div class="toc">' + T.entries.map(e => `<a href="#${e.id}" data-toc="${e.id}" class="${e.hl?'hl-only':''}">${esc(e.title)}</a>`).join('') + '</div>' : '')).join('') + '</div>';
    }
  });
  h += `<div class="grp">Toolkit</div>
    <a href="#diagrams" class="${r==='diagrams'||r.startsWith('d-')?'on':''}"><span>Diagrams</span><span class="n">${D.dias.length}</span></a>
    <a href="#formulas" class="${u&&u.id==='f'?'on':''}"><span>Formulas &amp; calculations</span></a>
    <a href="#glossary" class="${r==='glossary'?'on':''}"><span>Glossary</span><span class="n">${D.glossary.length}</span></a>
    <a href="#exam" class="${u&&u.id==='x'?'on':''}"><span>Exam skills</span></a>`;
  if (u && (u.id === 'x' || u.id === 'f')) h += '<div class="sub">' + u.topics.map(T => `<a href="#${T.id}" class="${t===T?'on':''}"><span>${esc(T.title)}</span></a>`).join('') + '</div>';
  h += `<div class="grp">Practice</div>
    <a href="#practice" class="${r==='practice'?'on':''}"><span>Practice hub</span></a>
    <a href="#flashcards" class="${r==='flashcards'?'on':''}"><span>Flashcards</span></a>
    <a href="#quiz" class="${r==='quiz'?'on':''}"><span>Multiple-choice quiz</span><span class="n">${D.mcq.length}</span></a>
    <a href="#drills" class="${r==='drills'?'on':''}"><span>Calculation drills</span><span class="n">${GENS.length}</span></a>
    <a href="#diagram-drill" class="${r==='diagram-drill'?'on':''}"><span>Diagram drill</span></a>
    <a href="#essays" class="${r==='essays'?'on':''}"><span>Essay plans</span><span class="n">${D.essays.length}</span></a>
    <a href="#missing" class="${r==='missing'?'on':''}"><span>Missing from the guide</span></a>`;
  $('#nav').innerHTML = h;
}

// ---------- router ----------
let pendingScroll = null;
const curRoute = () => decodeURIComponent((location.hash || '#home').slice(1)) || 'home';
function route(){
  const r = curRoute();
  closeRail(); closeResults();
  let scrollTo = null;
  if (r === 'home') view.innerHTML = homeHTML();
  else if (UNIT[r] && r.match(/^u\d/)) view.innerHTML = unitHTML(UNIT[r]);
  else if (r === 'exam') view.innerHTML = unitHTML(UNIT.x);
  else if (r === 'formulas') view.innerHTML = unitHTML(UNIT.f);
  else if (TOPIC[r]) { view.innerHTML = topicHTML(TOPIC[r]); P.last = r; saveP(); }
  else if (ENTRY[r]) { const t = ENTRY[r].topicObj; view.innerHTML = topicHTML(t); scrollTo = r; P.last = t.id; saveP(); }
  else if (r === 'diagrams') view.innerHTML = diagramsHTML();
  else if (r.startsWith('d-') && DIA[r.slice(2)]) view.innerHTML = diagramHTML(DIA[r.slice(2)]);
  else if (r === 'glossary') { view.innerHTML = glossaryHTML(); bindGlossary(); }
  else if (r === 'practice') view.innerHTML = practiceHTML();
  else if (r === 'flashcards') { view.innerHTML = '<div id="pv"></div>'; flashStart(); }
  else if (r === 'quiz') { view.innerHTML = '<div id="pv"></div>'; quizSetup(); }
  else if (r === 'drills') { view.innerHTML = '<div id="pv"></div>'; drillSetup(); }
  else if (r === 'diagram-drill') { view.innerHTML = '<div id="pv"></div>'; ddrillStart(); }
  else if (r === 'essays') { view.innerHTML = '<div id="pv"></div>'; essaysRender(); }
  else if (r === 'missing') view.innerHTML = missingHTML();
  else if (r === 'search') view.innerHTML = searchPageHTML(lastQuery);
  else view.innerHTML = `<div class="phead"><h1>Page not found</h1><p class="lede">That link doesn't match anything in the guide. <a href="#home">Go to the start page</a>.</p></div>`;
  fillDiagrams();
  renderRail();
  if (scrollTo){ const el = document.getElementById(scrollTo); if (el){ el.scrollIntoView({block:'start'}); el.classList.remove('flashme'); void el.offsetWidth; el.classList.add('flashme'); } }
  else if (pendingScroll !== null){ window.scrollTo(0, pendingScroll); pendingScroll = null; }
  else window.scrollTo(0, 0);
  if (pendingTerm){ const el = document.querySelector(`[data-gt="${CSS.escape(pendingTerm)}"]`); if (el){ el.scrollIntoView({block:'center'}); el.classList.add('flash'); } pendingTerm = null; }
  tocSpy();
}
window.addEventListener('hashchange', route);
function fillDiagrams(){ $$('.dslot').forEach(s => { s.outerHTML = figHTML(s.dataset.d); }); }

// ---------- views ----------
function homeHTML(){
  const done = learntIn(SYL_ENTRIES), tot = SYL_ENTRIES.length;
  const last = P.last && TOPIC[P.last];
  const hlN = SYL_ENTRIES.filter(e => e.hl).length + SYL_TOPICS.filter(t=>t.level==='HL').length;
  const art = DIA['tax-specific'] ? DIA['tax-specific'].svg : '';
  return `<section class="hero"><div class="phead" style="margin:0">
      <div class="eyebrow"><span>IB Diploma · Economics</span><span>Higher Level</span><span>First assessment 2022 guide</span></div>
      <h1>Econ <em>Lock-In</em></h1>
      <p class="lede">The whole HL course in one place: every syllabus point with definitions, fully labelled diagrams, HL calculations, evaluation and exam technique, then practice until it sticks.</p>
      <div class="stats"><span><b>${tot}</b>notes</span><span><b>${D.dias.length}</b>diagrams</span><span><b>${D.glossary.length}</b>key terms</span><span><b>${GENS.length}</b>calc drills</span><span><b>${D.mcq.length}</b>quiz questions</span></div>
      ${last ? `<a class="resume" href="#${last.id}"><div><small>Pick up where you left off</small><div><b>${last.num} ${esc(last.title)}</b></div></div></a>` : ''}
    </div><div class="art" aria-hidden="true">${art}</div></section>
    <h2 class="sec-h">The syllabus · ${done} of ${tot} notes marked learnt</h2>
    <div class="hub">${D.units.map(u => { const ents = u.topics.flatMap(t => t.entries); return `<a class="ucard" href="#${u.id}"><span class="k">Unit ${u.id.slice(1)} · ${u.topics.length} topics</span><h3>${esc(u.title)}</h3><p>${esc(u.blurb)}</p>
      <span class="meter"><span class="pbar"><i style="width:${pct(ents)}%"></i></span>${learntIn(ents)}/${ents.length}</span></a>`; }).join('')}</div>
    <h2 class="sec-h">Toolkit</h2>
    <div class="tools">
      <a class="ucard" href="#diagrams"><span class="k">${D.dias.length} diagrams</span><h3>Diagrams</h3><p>Every diagram the course uses, drawn to exam standard with drawing steps and pitfalls.</p></a>
      <a class="ucard" href="#formulas"><span class="k">Paper 2 &amp; 3</span><h3>Formulas</h3><p>All the calculations, each with a worked example and a drill that generates fresh numbers.</p></a>
      <a class="ucard" href="#exam"><span class="k">Papers 1, 2, 3 &amp; IA</span><h3>Exam skills</h3><p>Command terms, markbands, essay structures, the IA portfolio and the nine key concepts.</p></a>
    </div>
    <h2 class="sec-h">Practice</h2>
    <div class="tools">
      <a class="ucard" href="#flashcards"><span class="k">${D.glossary.length} cards</span><h3>Flashcards</h3><p>Definitions with spaced repetition: cards you miss come back sooner.</p></a>
      <a class="ucard" href="#quiz"><span class="k">${D.mcq.length} questions</span><h3>Quiz</h3><p>Multiple choice by unit with an explanation for every answer.</p></a>
      <a class="ucard" href="#drills"><span class="k">${GENS.length} types</span><h3>Calc drills</h3><p>Unlimited calculation questions with full working, HL included.</p></a>
      <a class="ucard" href="#diagram-drill"><span class="k">${D.dias.length} diagrams</span><h3>Diagram drill</h3><p>Name the diagram, or sketch it from memory and check.</p></a>
      <a class="ucard" href="#essays"><span class="k">${D.essays.length} prompts</span><h3>Essay plans</h3><p>Exam-style questions with timed practice and model plans.</p></a>
      <a class="ucard" href="#glossary"><span class="k">A–Z</span><h3>Glossary</h3><p>Every key term, searchable and linked back to its notes.</p></a>
    </div>
    <h2 class="sec-h">How to use this guide</h2>
    <div class="entry"><ul>
      <li><b>Read a topic</b>, then press <b>Mark learnt</b> on each note. Your progress shows in the contents and on this page${progDoc ? ' and syncs to your account' : ''}.</li>
      <li><b>HL view</b> shows everything. Switch to <b>SL view</b> (bottom of the contents) to hide HL-only material; purple boxes and <span class="badge hl">HL</span> badges mark it.</li>
      <li>Diagram colours are consistent: <span style="color:var(--c-d)">blue</span> for demand-side curves, <span style="color:var(--c-s)">red</span> for supply-side, <span style="color:var(--c-c)">green</span> for costs, <span style="color:var(--c-m)">violet</span> for MR and <span style="color:var(--c-g)">amber</span> for government.</li>
      <li>Underlined links jump to related notes, diagrams and glossary terms. Search (top of the contents) covers everything.</li>
      <li>Spot a gap or an error? Tap <b>Missing?</b> at the bottom right; notes go on a list you can hand back to Claude.</li>
      <li>Content follows the IB Economics guide (first assessment 2022, with the May 2024 assessment update) and the SaveMyExams IB Economics HL notes, cross-checked against the standard IB textbooks.</li>
    </ul></div>`;
}

function unitHTML(u){
  const isSyl = !!u.id.match(/^u\d/);
  const ents = u.topics.flatMap(t => t.entries);
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><span>${isSyl ? 'Unit ' + u.id.slice(1) : 'Toolkit'}</span>${isSyl?`<span>${learntIn(ents)}/${ents.length} learnt</span>`:''}</div>
    <h1>${esc(u.title)}</h1>${u.blurb?`<p class="lede">${esc(u.blurb)}</p>`:''}</div>
    ${u.id === 'f' ? '<p><a class="btn" href="#drills" style="text-decoration:none">Open the calculation drills →</a></p>' : ''}
    <div class="tlist">${u.topics.map(t => `<a class="trow ${t.level==='HL'?'hl-only':''}" href="#${t.id}"><span class="tn">${t.num || '§'}</span><div><h3>${esc(t.title)} ${t.level==='HL'?'<span class="badge hl">HL only</span>':''}</h3>${t.blurb?`<p>${esc(t.blurb)}</p>`:`<p>${t.entries.map(e=>esc(e.title)).join(' · ')}</p>`}</div>
      <div class="side">${isSyl?`<span>${learntIn(t.entries)}/${t.entries.length}</span><span class="pbar"><i style="width:${pct(t.entries)}%"></i></span>`:`<span>${t.entries.length} notes</span>`}</div></a>`).join('')}</div>`;
}

function topicHTML(t){
  const u = t.unit, isSyl = !!u.id.match(/^u\d/);
  const i = TOPIC_SEQ.indexOf(t); const prev = TOPIC_SEQ[i-1], next = TOPIC_SEQ[i+1];
  const same = x => x && x.unit === u;
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><a href="#${isSyl?u.id:u.id==='x'?'exam':'formulas'}">${isSyl?'Unit '+u.id.slice(1)+' · '+esc(u.title):esc(u.title)}</a>${t.level==='HL'?'<span class="badge hl">HL only</span>':''}</div>
    <h1>${t.num?`<span class="tn">${t.num}</span>`:''}${esc(t.title)}</h1>${t.blurb?`<p class="lede">${esc(t.blurb)}</p>`:''}
    ${t.entries.length > 1 ? `<div class="chips">${t.entries.map(e => `<a href="#${e.id}" class="${P.learnt[e.id]?'done':''} ${e.hl?'hlonly':''}">${esc(e.title)}${e.hl?' · HL':''}</a>`).join('')}</div>` : ''}</div>
    ${t.entries.map(e => entryHTML(e, isSyl)).join('')}
    <nav class="pnav">${same(prev)?`<a href="#${prev.id}"><small>← Previous</small>${prev.num} ${esc(prev.title)}</a>`:'<span></span>'}${same(next)?`<a class="nx" href="#${next.id}"><small>Next →</small>${next.num} ${esc(next.title)}</a>`:''}</nav>`;
}
function entryHTML(e, isSyl){
  const terms = e.terms.length ? `<div class="terms"><div class="th">Key terms</div><dl>${e.terms.map(([a, b]) => `<div class="t"><dt>${esc(a)}</dt><dd>${D.glossary.find(g => g.t.toLowerCase() === a.toLowerCase() && g.e === e.id)?.d || esc(b)}</dd></div>`).join('')}</dl></div>` : '';
  return `<article class="entry ${e.hl?'hlonly':''}" id="${e.id}"><header><h2>${esc(e.title)} ${e.hl?'<span class="badge hl">HL only</span>':''}</h2>
    ${isSyl?`<button class="learnt" data-learn="${e.id}" aria-pressed="${!!P.learnt[e.id]}">${P.learnt[e.id]?'Learnt':'Mark learnt'}</button>`:''}</header>${terms}${e.html}</article>`;
}
document.addEventListener('click', ev => {
  const b = ev.target.closest('[data-learn]');
  if (b){ const id = b.dataset.learn; if (P.learnt[id]) delete P.learnt[id]; else P.learnt[id] = Date.now(); saveP();
    b.setAttribute('aria-pressed', String(!!P.learnt[id])); b.textContent = P.learnt[id] ? 'Learnt' : 'Mark learnt';
    const c = document.querySelector(`.chips a[href="#${id}"]`); if (c) c.classList.toggle('done', !!P.learnt[id]);
    const y = window.scrollY; renderRail(); window.scrollTo(0, y); return; }
  const g = ev.target.closest('a.gref');
  if (g){ pendingTerm = g.dataset.term.toLowerCase(); if (curRoute() === 'glossary'){ ev.preventDefault(); route(); } }
});

function diagramsHTML(){
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><span>Toolkit</span><span>${D.dias.length} diagrams</span></div><h1>Diagrams</h1>
    <p class="lede">Every diagram in the course, grouped by unit. Open one for the drawing steps, the explanation examiners want, and the mistakes that cost marks.</p></div>${LEGEND}` +
    D.units.map(u => { const ds = D.dias.filter(d => unitOfTopic(d.topic) === u); if (!ds.length) return '';
      return `<h2 class="sec-h">Unit ${u.id.slice(1)} · ${esc(u.title)}</h2><div class="dgrid">${ds.map(d => `<a class="dcard ${d.hl?'hlonly':''}" href="#d-${d.id}"><div class="th">${d.svg}</div><b>${esc(d.title)}</b><small>${TOPIC[d.topic] ? TOPIC[d.topic].num + ' ' + esc(TOPIC[d.topic].title) : ''}${d.hl?' · HL':''}</small></a>`).join('')}</div>`; }).join('');
}
function diagramHTML(d){
  const t = TOPIC[d.topic]; const i = D.dias.indexOf(d); const prev = D.dias[i-1], next = D.dias[i+1];
  const uses = SYL_ENTRIES.filter(e => e.dias.includes(d.id));
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><a href="#diagrams">Diagrams</a>${t?`<a href="#${t.id}">${t.num} ${esc(t.title)}</a>`:''}${d.hl?'<span class="badge hl">HL</span>':''}</div><h1>${esc(d.title)}</h1></div>
    <div class="ddetail ${isWide(d)?'wide':''}"><div class="svgwrap">${d.svg}</div>${LEGEND}
    <h2>How to draw it</h2><ol>${d.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol>
    <h2>What it shows</h2><p>${esc(d.explain)}</p>
    ${d.watch?`<div class="box warn"><div class="box-h">Watch out</div><p>${esc(d.watch)}</p></div>`:''}
    ${uses.length?`<h2>Used in</h2><div class="chips">${uses.map(e => `<a href="#${e.id}">${e.topicObj.num} ${esc(e.title)}</a>`).join('')}</div>`:''}</div>
    <nav class="pnav">${prev?`<a href="#d-${prev.id}"><small>← Previous</small>${esc(prev.title)}</a>`:'<span></span>'}${next?`<a class="nx" href="#d-${next.id}"><small>Next →</small>${esc(next.title)}</a>`:''}</nav>`;
}

// ---------- glossary ----------
let pendingTerm = null, gUnit = store.get('econ-gunit', 'all');
function glossaryHTML(){
  const units = [['all','All'], ...D.units.map(u => [u.id, 'Unit ' + u.id.slice(1)]), ['x','Exam'], ['f','Formulas']];
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><span>Toolkit</span><span>${D.glossary.length} terms</span></div><h1>Glossary</h1>
    <p class="lede">Every key term from the notes, with the definition to learn word for word. Each links back to where it is explained.</p></div>
    <div class="gtools"><label class="vh" for="gq">Filter terms</label><input id="gq" type="search" placeholder="Filter terms…"><div class="filters" id="gunits">${units.map(([k, l]) => `<button data-gu="${k}" aria-pressed="${gUnit===k}">${l}</button>`).join('')}</div></div>
    <div class="letters" id="gletters"></div><div id="glist"></div>`;
}
function bindGlossary(){
  const draw = () => {
    const q = ($('#gq').value || '').trim().toLowerCase();
    const items = D.glossary.filter(g => (gUnit === 'all' || g.u === gUnit) && (!q || g.t.toLowerCase().includes(q) || strip(g.d).toLowerCase().includes(q)));
    const groups = {};
    items.forEach(g => { const L = (g.t.match(/[A-Za-z0-9]/) || ['#'])[0].toUpperCase(); const k = /\d/.test(L) ? '#' : L; (groups[k] = groups[k] || []).push(g); });
    const keys = Object.keys(groups).sort();
    $('#gletters').innerHTML = keys.map(k => `<a href="#glossary" data-gl="${k}">${k}</a>`).join('');
    $('#glist').innerHTML = items.length ? `<div class="gl">${keys.map(k => `<h3 id="gl-${k}">${k}</h3>` + groups[k].map(g => `<div class="gi ${g.hl?'hl-only':''}" data-gt="${esc(g.t.toLowerCase())}"><dt>${esc(g.t)}${g.hl?' <span class="badge hl">HL</span>':''}</dt><dd>${g.d}<span class="src"><a href="#${g.e}">${TOPIC[g.topic] ? (TOPIC[g.topic].num + ' ' + esc(TOPIC[g.topic].title)) : ''} →</a></span></dd></div>`).join('')).join('')}</div>`
      : `<div class="empty">No terms match "${esc(q)}". Try a shorter word, or switch the unit filter to All.</div>`;
  };
  $('#gq').addEventListener('input', draw);
  $('#gunits').addEventListener('click', ev => { const b = ev.target.closest('[data-gu]'); if (!b) return; gUnit = b.dataset.gu; store.set('econ-gunit', gUnit); $$('[data-gu]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); draw(); });
  $('#gletters').addEventListener('click', ev => { const a = ev.target.closest('[data-gl]'); if (!a) return; ev.preventDefault(); document.getElementById('gl-' + a.dataset.gl)?.scrollIntoView({block:'start'}); });
  if (pendingTerm){ gUnit = 'all'; $$('[data-gu]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.gu === 'all'))); }
  draw();
}

// ---------- search ----------
const IDX = [];
SYL_TOPICS.concat(D.exam.flatMap(u=>u.topics), D.formulas.flatMap(u=>u.topics)).forEach(t => {
  IDX.push({k:'Topic', title:(t.num ? t.num + ' ' : '') + t.title, body:(t.blurb||'').toLowerCase(), href:'#'+t.id, snip:t.blurb||'', w:3});
  t.entries.forEach(e => IDX.push({k: t.num ? t.num + ' · note' : t.unit.title, title:e.title, body:(e.text + ' ' + e.terms.map(x=>x[0]).join(' ')).toLowerCase(), raw:e.text, href:'#'+e.id, w:2}));
});
D.dias.forEach(d => IDX.push({k:'Diagram', title:d.title, body:(d.explain + ' ' + d.steps.join(' ')).toLowerCase(), raw:d.explain, href:'#d-'+d.id, w:2}));
D.glossary.forEach(g => IDX.push({k:'Key term', title:g.t, body:strip(g.d).toLowerCase(), raw:strip(g.d), href:'#glossary', term:g.t.toLowerCase(), w:4}));
IDX.forEach(x => x.tl = x.title.toLowerCase());
function search(q){
  const toks = q.toLowerCase().split(/\s+/).filter(Boolean); if (!toks.length) return [];
  const out = [];
  for (const x of IDX){
    let s = 0, ok = true;
    for (const t of toks){ const inT = x.tl.includes(t); const inB = x.body.includes(t); if (!inT && !inB){ ok = false; break; } s += inT ? 6 : 1; if (inT && x.tl.startsWith(t)) s += 2; }
    if (!ok) continue;
    if (x.tl === q.toLowerCase()) s += 12;
    out.push([s * x.w, x]);
  }
  return out.sort((a, b) => b[0] - a[0]).map(a => a[1]);
}
function snippet(x, q){
  const raw = x.raw || x.snip || ''; const toks = q.toLowerCase().split(/\s+/).filter(Boolean);
  let i = -1; for (const t of toks){ i = raw.toLowerCase().indexOf(t); if (i >= 0) break; }
  let s = i < 0 ? raw.slice(0, 140) : (i > 60 ? '…' : '') + raw.slice(Math.max(0, i - 60), i + 110) + '…';
  s = esc(s); toks.forEach(t => { s = s.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
  return s;
}
let lastQuery = '';
const qi = $('#q'), res = $('#results');
qi.addEventListener('input', () => {
  const q = qi.value.trim(); lastQuery = q;
  if (q.length < 2){ closeResults(); return; }
  const r = search(q);
  res.hidden = false;
  res.innerHTML = r.length ? r.slice(0, 8).map(x => `<a href="${x.href}" ${x.term?`data-term="${esc(x.term)}" class="gref"`:''}><small>${esc(x.k)}</small>${esc(x.title)}</a>`).join('') + (r.length > 8 ? `<a class="all" href="#search">All ${r.length} results →</a>` : '') : `<div class="none">Nothing found for "${esc(q)}".</div>`;
});
qi.addEventListener('keydown', ev => { if (ev.key === 'Enter'){ const q = qi.value.trim(); if (q.length > 1){ lastQuery = q; if (curRoute() === 'search') route(); else location.hash = 'search'; } } if (ev.key === 'Escape'){ qi.value = ''; closeResults(); } });
function closeResults(){ res.hidden = true; }
document.addEventListener('click', ev => { if (!ev.target.closest('.search')) closeResults(); });
function searchPageHTML(q){
  const r = q ? search(q) : [];
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><span>Search</span><span>${r.length} results</span></div><h1>${q ? '“' + esc(q) + '”' : 'Search'}</h1>
    ${q ? '' : '<p class="lede">Type in the search box in the contents and press Enter.</p>'}</div>` +
    r.slice(0, 120).map(x => `<a class="sres ${x.term?'gref':''}" href="${x.href}" ${x.term?`data-term="${esc(x.term)}"`:''}><small>${esc(x.k)}</small><div><b>${esc(x.title)}</b></div><p>${snippet(x, q)}</p></a>`).join('');
}

// ---------- mobile rail ----------
function openRail(){ $('#rail').classList.add('open'); $('#scrim').hidden = false; $('#menuBtn').setAttribute('aria-expanded', 'true'); }
function closeRail(){ $('#rail').classList.remove('open'); $('#scrim').hidden = true; $('#menuBtn').setAttribute('aria-expanded', 'false'); }
$('#menuBtn').onclick = openRail; $('#scrim').onclick = closeRail;
$('#searchBtn').onclick = () => { openRail(); setTimeout(() => qi.focus(), 220); };
function tocSpy(){
  const links = $$('[data-toc]'); if (!links.length) return;
  let cur = null; for (const a of links){ const el = document.getElementById(a.dataset.toc); if (el && el.getBoundingClientRect().top < window.innerHeight * 0.4) cur = a; }
  links.forEach(a => a.classList.toggle('cur', a === cur));
}
let spyT = null; window.addEventListener('scroll', () => { if (spyT) return; spyT = setTimeout(() => { spyT = null; tocSpy(); }, 120); }, {passive:true});

// ---------- practice hub ----------
function practiceHTML(){
  const fl = Object.values(P.flash); const mastered = fl.filter(b => b >= 4).length;
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><span>Practice</span></div><h1>Practice</h1>
    <p class="lede">Retrieval beats rereading. Mix these modes: definitions daily, calculations before Papers 2 and 3, essay plans before Paper 1.</p></div>
    <div class="stats" style="margin-bottom:18px"><span><b>${mastered}</b>flashcards mastered</span><span><b>${P.quiz.c}/${P.quiz.n}</b>quiz answers right</span><span><b>${P.calc.c}/${P.calc.n}</b>calculations right</span><span><b>${learntIn(SYL_ENTRIES)}</b>notes learnt</span></div>
    <div class="modes">
      <a class="ucard" href="#flashcards"><span class="k">Paper 1 &amp; 2 definitions</span><h3>Flashcards</h3><p>${D.glossary.length} terms, spaced repetition in five boxes.</p></a>
      <a class="ucard" href="#quiz"><span class="k">All units</span><h3>Quiz</h3><p>${D.mcq.length} multiple-choice questions with explanations.</p></a>
      <a class="ucard" href="#drills"><span class="k">Paper 2 &amp; 3</span><h3>Calculation drills</h3><p>${GENS.length} question types with new numbers every time.</p></a>
      <a class="ucard" href="#diagram-drill"><span class="k">Diagrams</span><h3>Diagram drill</h3><p>Name it from the picture, or sketch it from the name.</p></a>
      <a class="ucard" href="#essays"><span class="k">Papers 1, 2, 3</span><h3>Essay plans</h3><p>${D.essays.length} exam-style prompts with a timer and model plans.</p></a>
    </div>`;
}
const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
function unitFilterHTML(cur, key){
  return `<div class="filters" data-uf="${key}">${[['all','All units'], ...D.units.map(u => [u.id, 'Unit ' + u.id.slice(1)])].map(([k, l]) => `<button data-u="${k}" aria-pressed="${cur===k}">${l}</button>`).join('')}</div>`;
}

// ---------- flashcards ----------
let FL = {unit: store.get('econ-flunit', 'all'), rev: false, card: null, shown: false};
function flashDeck(){ return D.glossary.filter(g => (FL.unit === 'all' || g.u === FL.unit) && (!SL || !g.hl) && g.u.match(/^u\d/)); }
function flashNext(){
  const deck = flashDeck(); if (!deck.length){ FL.card = null; return; }
  const w = deck.map(g => { const b = P.flash[g.t] || 0; return [g, b === 0 ? 4 : Math.max(0.3, 5 - b)]; });
  let tot = w.reduce((s, x) => s + x[1], 0), r = Math.random() * tot;
  for (const [g, x] of w){ r -= x; if (r <= 0){ if (g !== FL.card || deck.length === 1){ FL.card = g; break; } } }
  if (!FL.card || !deck.includes(FL.card)) FL.card = deck[Math.floor(Math.random() * deck.length)];
  FL.shown = false;
}
function flashStart(){ flashNext(); flashRender(); }
function flashRender(){
  const deck = flashDeck(); const c = FL.card; const pv = $('#pv'); if (!pv) return;
  const counts = [0,0,0,0,0,0]; deck.forEach(g => counts[P.flash[g.t] || 0]++);
  pv.innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><span>${deck.length} cards</span></div><h1>Flashcards</h1>
    <p class="lede">Say the definition out loud, flip, then be honest. Cards you get right move up a box and come back less often.</p></div>
    <div class="gtools">${unitFilterHTML(FL.unit, 'fl')}<button class="btn ghost" id="flRev">${FL.rev ? 'Show term first' : 'Show definition first'}</button></div>
    ${c ? `<div class="pcard flash-card" id="flCard" tabindex="0" role="button" aria-label="Flip card">
      <span class="fh">${FL.shown ? (FL.rev ? 'Term' : 'Definition') : (FL.rev ? 'Which term is this?' : 'Define')}${TOPIC[c.topic] ? ' · ' + TOPIC[c.topic].num : ''}</span>
      ${FL.rev ? (FL.shown ? `<div class="ft">${esc(c.t)}</div><div class="fd">${c.d}</div>` : `<div class="fd">${c.d.replace(new RegExp(c.t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'), 'ig'), '___')}</div>`)
               : (FL.shown ? `<div class="ft">${esc(c.t)}</div><div class="fd">${c.d}</div>` : `<div class="ft">${esc(c.t)}</div>`)}
      ${FL.shown ? '' : '<span class="fh">Tap or press space to flip</span>'}</div>
    <div class="prow">${FL.shown ? `<button class="btn ghost" id="flAgain">Again (1)</button><button class="btn" id="flGot">Got it (2)</button><a href="#${c.e}" style="font-size:14px">Read the note →</a>` : `<button class="btn" id="flFlip">Flip</button>`}
      <span class="sp"></span><span class="boxes" title="Cards in each box">${counts.map((n, i) => `<span>${i === 0 ? 'new' : 'box ' + i} ${n}</span>`).join('')}</span></div>`
    : '<div class="empty">No cards in this filter.</div>'}`;
  const flip = () => { FL.shown = true; flashRender(); };
  $('#flCard') && ($('#flCard').onclick = () => { if (!FL.shown) flip(); });
  $('#flFlip') && ($('#flFlip').onclick = flip);
  $('#flAgain') && ($('#flAgain').onclick = () => { P.flash[c.t] = 1; saveP(); flashNext(); flashRender(); });
  $('#flGot') && ($('#flGot').onclick = () => { P.flash[c.t] = Math.min(5, (P.flash[c.t] || 0) + 1); saveP(); flashNext(); flashRender(); });
  $('#flRev').onclick = () => { FL.rev = !FL.rev; FL.shown = false; flashRender(); };
  pv.querySelector('[data-uf]').onclick = ev => { const b = ev.target.closest('[data-u]'); if (!b) return; FL.unit = b.dataset.u; store.set('econ-flunit', FL.unit); flashNext(); flashRender(); };
}
document.addEventListener('keydown', ev => {
  if (ev.target.closest('input,textarea')) return;
  const r = curRoute();
  if (r === 'flashcards' && FL.card){
    if (ev.key === ' ' && !FL.shown){ ev.preventDefault(); FL.shown = true; flashRender(); }
    else if (FL.shown && ev.key === '1') $('#flAgain')?.click(); else if (FL.shown && ev.key === '2') $('#flGot')?.click();
  }
  if (r === 'quiz' && QZ.qs && /^[1-4]$/.test(ev.key)) $$('.qopts button')[+ev.key - 1]?.click();
});

// ---------- quiz ----------
let QZ = {unit: store.get('econ-qzunit', 'all'), qs: null, i: 0, score: 0, answered: false};
function quizSetup(){
  const pool = D.mcq.filter(q => QZ.unit === 'all' || (unitOfTopic(q.t) && unitOfTopic(q.t).id === QZ.unit));
  $('#pv').innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><span>${D.mcq.length} questions</span></div><h1>Quiz</h1>
    <p class="lede">Ten questions at a time. Read each explanation even when you are right; that is where the learning happens. Keys 1–4 answer.</p></div>
    <div class="gtools">${unitFilterHTML(QZ.unit, 'qz')}</div>
    <div class="pcard"><p style="margin-top:0">${pool.length} questions in this set. Your record so far: <b>${P.quiz.c} of ${P.quiz.n}</b> correct.</p><button class="btn" id="qzGo" ${pool.length?'':'disabled'}>Start 10 questions</button></div>`;
  $('#pv [data-uf]').onclick = ev => { const b = ev.target.closest('[data-u]'); if (!b) return; QZ.unit = b.dataset.u; store.set('econ-qzunit', QZ.unit); quizSetup(); };
  $('#qzGo').onclick = () => { QZ.qs = shuffle(pool).slice(0, 10).map(q => { const order = shuffle(q.a.map((_, i) => i)); return Object.assign({}, q, {order}); }); QZ.i = 0; QZ.score = 0; QZ.answered = false; quizRender(); };
}
function quizRender(){
  const q = QZ.qs[QZ.i]; const t = TOPIC[q.t];
  $('#pv').innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><a href="#quiz">Quiz</a></div><h1>Quiz</h1></div>
    <div class="pcard"><div class="qmeta"><span>Question ${QZ.i + 1} of ${QZ.qs.length}</span><span>${t ? t.num + ' ' + esc(t.title) : ''}</span><span>Score ${QZ.score}</span></div>
    <div class="qq">${q.q}</div><div class="qopts">${q.order.map((oi, k) => `<button data-oi="${oi}"><b>${k + 1}.</b> ${q.a[oi]}</button>`).join('')}</div>
    <div id="qx"></div></div>`;
  $$('.qopts button').forEach(b => b.onclick = () => {
    if (QZ.answered) return; QZ.answered = true;
    const ok = +b.dataset.oi === q.c; if (ok) QZ.score++;
    P.quiz.n++; if (ok) P.quiz.c++; saveP();
    $$('.qopts button').forEach(x => { x.disabled = true; if (+x.dataset.oi === q.c) x.classList.add('right'); });
    if (!ok) b.classList.add('wrong');
    $('#qx').innerHTML = `<div class="qx"><p class="verdict ${ok?'ok':'bad'}">${ok ? 'Correct' : 'Not quite'}</p>${q.x ? `<p>${q.x}</p>` : ''}${t ? `<p><a href="#${t.id}">Revise ${t.num} ${esc(t.title)} →</a></p>` : ''}
      <div class="prow"><button class="btn" id="qzNext">${QZ.i + 1 < QZ.qs.length ? 'Next question' : 'See score'}</button></div></div>`;
    $('#qzNext').onclick = () => { QZ.i++; QZ.answered = false; if (QZ.i < QZ.qs.length) quizRender(); else quizDone(); };
    $('#qzNext').focus();
  });
}
function quizDone(){
  $('#pv').innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><a href="#quiz">Quiz</a></div><h1>Quiz complete</h1></div>
    <div class="pcard"><div class="score">${QZ.score}/${QZ.qs.length}</div><p>${QZ.score >= 9 ? 'Excellent. Try another unit.' : QZ.score >= 6 ? 'Solid. Revisit the topics you missed, then go again.' : 'Worth revising those topics before another round.'}</p>
    <div class="prow"><button class="btn" id="qzAgain">Another 10</button><a class="btn ghost" href="#practice" style="text-decoration:none">Back to practice</a></div></div>`;
  $('#qzAgain').onclick = () => { QZ.qs = null; quizSetup(); };
  QZ.qs = null;
}

// ---------- calculation drills ----------
const ri = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const pick = a => a[Math.floor(Math.random() * a.length)];
const r2 = x => Math.round(x * 100) / 100;
const f2 = x => (Math.round(x * 100) / 100).toLocaleString('en-US', {maximumFractionDigits: 2});
const money = x => '$' + f2(x);
const pc = (a, b) => (b - a) / a * 100;
const GENS = [
 {id:'pct', t:'t3-1', name:'Percentage change', hl:false, gen(){ const a = ri(20, 400), b = a + ri(-a/2, a) ; return {q:`The price of a good changes from ${money(a)} to ${money(b)}. Calculate the percentage change in price.`, a:pc(a,b), unit:'%', w:`<p>% change = (new − old) ÷ old × 100</p><p>= (${b} − ${a}) ÷ ${a} × 100 = <b>${f2(pc(a,b))}%</b></p>`}; }},
 {id:'ped', t:'t2-5', name:'Price elasticity of demand (PED)', gen(){ const p1 = ri(4, 40), p2 = p1 + pick([-1, 1]) * ri(1, Math.max(1, Math.floor(p1/3))), q1 = ri(10, 90) * 10; const e = -pick([0.3, 0.5, 0.8, 1.2, 1.5, 2, 2.5]); const q2 = Math.round(q1 * (1 + e * pc(p1, p2) / 100)); const v = pc(q1, q2) / pc(p1, p2);
   return {q:`When the price of a good changes from ${money(p1)} to ${money(p2)}, quantity demanded changes from ${q1} to ${q2} units per week. Calculate the PED (to 2 d.p.).`, a:v, w:`<p>%ΔQd = (${q2} − ${q1}) ÷ ${q1} × 100 = ${f2(pc(q1,q2))}%</p><p>%ΔP = (${p2} − ${p1}) ÷ ${p1} × 100 = ${f2(pc(p1,p2))}%</p><p>PED = %ΔQd ÷ %ΔP = <b>${f2(v)}</b> → demand is ${Math.abs(v) > 1 ? 'price elastic (|PED| > 1)' : Math.abs(v) < 1 ? 'price inelastic (|PED| < 1)' : 'unit elastic'}.</p>`}; }},
 {id:'ped-rev', t:'t2-5', name:'PED and total revenue', gen(){ const p1 = ri(5, 30), q1 = ri(20, 80) * 10, e = pick([0.4, 0.6, 1.5, 2]); const up = pick([true, false]); const dp = ri(5, 20) * (up ? 1 : -1); const p2 = r2(p1 * (1 + dp/100)), q2 = Math.round(q1 * (1 - e * dp / 100)); const tr1 = p1*q1, tr2 = p2*q2;
   return {q:`A firm sells ${q1} units at ${money(p1)}. PED is −${e}. It ${up?'raises':'cuts'} price by ${Math.abs(dp)}%. Calculate the change in total revenue (use the new quantity rounded to the nearest unit).`, a:tr2 - tr1, unit:'$', w:`<p>%ΔQd = PED × %ΔP = −${e} × ${dp} = ${f2(-e*dp)}% → new Q = ${q1} × ${f2(1 - e*dp/100)} ≈ ${q2}</p><p>New P = ${money(p2)}. TR₁ = ${p1} × ${q1} = ${money(tr1)}; TR₂ = ${p2} × ${q2} = ${money(tr2)}</p><p>Change in TR = <b>${money(tr2 - tr1)}</b>. ${e < 1 ? 'Demand is inelastic, so TR moves in the same direction as price.' : 'Demand is elastic, so TR moves in the opposite direction to price.'}</p>`}; }},
 {id:'yed', t:'t2-5', name:'Income elasticity of demand (YED)', gen(){ const y1 = ri(20, 60) * 1000, dy = pick([5, 8, 10, 12, 20]) , y2 = y1 * (1 + dy/100); const e = pick([-0.8, -0.4, 0.3, 0.6, 1.4, 2.2]); const q1 = ri(10, 60) * 10, q2 = Math.round(q1 * (1 + e * dy / 100)); const v = pc(q1, q2) / pc(y1, y2);
   return {q:`Average income rises from ${money(y1)} to ${money(y2)}. Quantity demanded of good X changes from ${q1} to ${q2}. Calculate YED and say what type of good X is.`, a:v, w:`<p>YED = %ΔQd ÷ %ΔY = ${f2(pc(q1,q2))}% ÷ ${f2(pc(y1,y2))}% = <b>${f2(v)}</b></p><p>${v < 0 ? 'Negative: an <b>inferior good</b>.' : v > 1 ? 'Positive and greater than 1: a <b>normal, income-elastic (luxury) good</b>.' : 'Between 0 and 1: a <b>normal, income-inelastic (necessity) good</b>.'}</p>`}; }},
 {id:'pes', t:'t2-6', name:'Price elasticity of supply (PES)', gen(){ const p1 = ri(5, 50), dp = pick([10, 20, 25, 40]), p2 = r2(p1 * (1 + dp/100)), e = pick([0.3, 0.5, 1.6, 2.4]), q1 = ri(10, 90) * 10, q2 = Math.round(q1 * (1 + e * dp/100)); const v = pc(q1, q2) / pc(p1, p2);
   return {q:`The price of a product rises from ${money(p1)} to ${money(p2)}, and quantity supplied rises from ${q1} to ${q2}. Calculate PES.`, a:v, w:`<p>PES = %ΔQs ÷ %ΔP = ${f2(pc(q1,q2))}% ÷ ${f2(pc(p1,p2))}% = <b>${f2(v)}</b> → ${v > 1 ? 'price elastic supply' : 'price inelastic supply'}.</p>`}; }},
 {id:'lin-eq', t:'t2-3', name:'Equilibrium from linear functions', hl:true, gen(){ const pe = ri(4, 20), qe = ri(20, 120), b = ri(2, 8), d = ri(2, 8); const a = qe + b * pe, c = qe - d * pe;
   return {q:`Qd = ${a} − ${b}P and Qs = ${c < 0 ? '−' + (-c) : c} + ${d}P. Calculate the equilibrium price.`, a:pe, unit:'$', w:`<p>Set Qd = Qs: ${a} − ${b}P = ${c} + ${d}P → ${a - c} = ${b + d}P → P = <b>${money(pe)}</b></p><p>Q = ${a} − ${b} × ${pe} = <b>${qe}</b> units.</p>`}; }},
 {id:'lin-tax', t:'t2-7', name:'Specific tax with linear functions', hl:true, gen(){ const b = ri(2, 6), d = ri(2, 6), pe = ri(8, 20), qe = ri(40, 120); const a = qe + b*pe, c = qe - d*pe; const t = ri(1, 4);
   const pc_ = (a - c + d*t) / (b + d), q = a - b*pc_, pp = pc_ - t;
   const which = pick(['rev', 'cons', 'prod', 'pc']);
   const ask = {rev:['the government\'s tax revenue', t*q, '$'], cons:['the consumer burden (consumer share of the tax revenue)', (pc_ - pe)*q, '$'], prod:['the producer burden (producer share of the tax revenue)', (pe - pp)*q, '$'], pc:['the new price paid by consumers', pc_, '$']}[which];
   return {q:`Qd = ${a} − ${b}P and Qs = ${c < 0 ? '−' + (-c) : c} + ${d}P. The government imposes a specific tax of ${money(t)} per unit. Calculate ${ask[0]}.`, a:ask[1], unit:'$', w:`<p>Before the tax: ${a} − ${b}P = ${c} + ${d}P → Pe = ${money(pe)}, Qe = ${qe}.</p><p>With the tax, producers receive P − ${t}: Qs = ${c} + ${d}(P − ${t}) = ${c - d*t} + ${d}P.</p><p>${a} − ${b}P = ${c - d*t} + ${d}P → P = ${f2(a - c + d*t)} ÷ ${b + d} = ${money(pc_)} (consumers); producers receive ${money(pp)}; Q = ${f2(q)}.</p><p>Revenue = ${t} × ${f2(q)} = ${money(t*q)}; consumer burden = (${f2(pc_)} − ${pe}) × ${f2(q)} = ${money((pc_-pe)*q)}; producer burden = (${pe} − ${f2(pp)}) × ${f2(q)} = ${money((pe-pp)*q)}.</p><p>Answer: <b>${money(ask[1])}</b></p>`}; }},
 {id:'lin-sub', t:'t2-7', name:'Subsidy with linear functions', hl:true, gen(){ const b = ri(2, 6), d = ri(2, 6), pe = ri(8, 20), qe = ri(40, 120); const a = qe + b*pe, c = qe - d*pe; const s = ri(1, 4);
   const p = (a - c - d*s) / (b + d), q = a - b*p;
   const which = pick(['cost', 'p', 'q']); const ask = {cost:['the total cost of the subsidy to the government', s*q, '$'], p:['the new market price paid by consumers', p, '$'], q:['the new equilibrium quantity', q, '']}[which];
   return {q:`Qd = ${a} − ${b}P and Qs = ${c < 0 ? '−' + (-c) : c} + ${d}P. A subsidy of ${money(s)} per unit is paid to producers. Calculate ${ask[0]}.`, a:ask[1], unit:ask[2], w:`<p>With the subsidy producers receive P + ${s}: Qs = ${c} + ${d}(P + ${s}) = ${c + d*s} + ${d}P.</p><p>${a} − ${b}P = ${c + d*s} + ${d}P → P = ${f2(a - c - d*s)} ÷ ${b + d} = ${money(p)}; Q = ${f2(q)}; producers receive ${money(p + s)}.</p><p>Government spending = ${s} × ${f2(q)} = ${money(s*q)}.</p><p>Answer: <b>${ask[2]==='$'?money(ask[1]):f2(ask[1])}</b></p>`}; }},
 {id:'lin-ceil', t:'t2-7', name:'Price ceiling or floor: shortage and surplus', hl:true, gen(){ const b = ri(2, 6), d = ri(2, 6), pe = ri(8, 20), qe = ri(60, 140); const a = qe + b*pe, c = qe - d*pe; const ceil = pick([true, false]); const pm = ceil ? pe - ri(1, 4) : pe + ri(1, 4); const qd = a - b*pm, qs = c + d*pm;
   return {q:`Qd = ${a} − ${b}P and Qs = ${c < 0 ? '−' + (-c) : c} + ${d}P. The government sets a ${ceil ? 'maximum' : 'minimum'} price of ${money(pm)}. Calculate the size of the ${ceil ? 'shortage' : 'surplus'}${ceil ? '' : ' and the cost to the government of buying it'}.`, a: ceil ? qd - qs : (qs - qd) * pm, unit: ceil ? 'units' : '$', w:`<p>At P = ${pm}: Qd = ${a} − ${b}×${pm} = ${qd}; Qs = ${c} + ${d}×${pm} = ${qs}.</p><p>${ceil ? `Shortage = Qd − Qs = <b>${qd - qs}</b> units.` : `Surplus = Qs − Qd = ${qs - qd} units; cost = ${pm} × ${qs - qd} = <b>${money((qs-qd)*pm)}</b>.`}</p>`}; }},
 {id:'cs', t:'t2-3', name:'Consumer and producer surplus', hl:true, gen(){ const b = ri(2, 5), d = ri(2, 5), pe = ri(6, 20), qe = ri(40, 120); const a = qe + b*pe, c = qe - d*pe; const pmaxD = a / b, pminS = -c / d; const which = pick(['cs', 'ps']);
   const v = which === 'cs' ? 0.5 * (pmaxD - pe) * qe : 0.5 * (pe - Math.max(0, pminS)) * qe;
   return {q:`Qd = ${a} − ${b}P and Qs = ${c < 0 ? '−' + (-c) : c} + ${d}P${c > 0 ? ' (supply meets the quantity axis, so producer surplus is a trapezium)' : ''}. The equilibrium is P = ${pe}, Q = ${qe}. Calculate the ${which === 'cs' ? 'consumer' : 'producer'} surplus.`, a: which === 'ps' && c > 0 ? (pe * (c + qe) / 2) : v, unit:'$',
     w: which === 'cs' ? `<p>Demand meets the price axis where Qd = 0: P = ${a} ÷ ${b} = ${f2(pmaxD)}.</p><p>CS = ½ × (${f2(pmaxD)} − ${pe}) × ${qe} = <b>${money(v)}</b></p>` : c > 0 ? `<p>At P = 0, Qs = ${c}, so PS is the trapezium between P = 0 and P = ${pe}: ½ × (${c} + ${qe}) × ${pe} = <b>${money(pe*(c+qe)/2)}</b></p>` : `<p>Supply meets the price axis where Qs = 0: P = ${f2(pminS)}.</p><p>PS = ½ × (${pe} − ${f2(pminS)}) × ${qe} = <b>${money(v)}</b></p>`}; }},
 {id:'profit', t:'t2-11', name:'Revenue, cost and profit', hl:true, gen(){ const q = ri(10, 90) * 10, p = ri(8, 40), atc = r2(p + pick([-1, 1]) * ri(1, 8) + Math.random()); const tr = p*q, tc = atc*q;
   const which = pick(['profit', 'tr', 'tc']);
   return {q:`A firm sells ${q} units at ${money(p)} each. Average total cost at this output is ${money(atc)}. Calculate ${which === 'profit' ? 'its economic profit (or loss)' : which === 'tr' ? 'total revenue' : 'total cost'}.`, a: which === 'profit' ? tr - tc : which === 'tr' ? tr : tc, unit:'$', w:`<p>TR = P × Q = ${p} × ${q} = ${money(tr)}</p><p>TC = ATC × Q = ${atc} × ${q} = ${money(tc)}</p><p>Profit = TR − TC = <b>${money(tr - tc)}</b> → ${tr - tc > 0 ? 'abnormal profit' : tr - tc < 0 ? 'a loss' : 'normal profit'}.</p>`}; }},
 {id:'mr', t:'t2-11', name:'Marginal revenue from a demand schedule', hl:true, gen(){ const a = ri(20, 40), b = pick([1, 2]); const q1 = ri(2, 8), q2 = q1 + 1; const p1 = a - b*q1, p2 = a - b*q2; const mr = p2*q2 - p1*q1;
   return {q:`A firm can sell ${q1} units at ${money(p1)} each or ${q2} units at ${money(p2)} each. Calculate the marginal revenue of unit ${q2}.`, a:mr, unit:'$', w:`<p>TR at ${q1} = ${p1} × ${q1} = ${p1*q1}; TR at ${q2} = ${p2} × ${q2} = ${p2*q2}</p><p>MR = ΔTR ÷ ΔQ = (${p2*q2} − ${p1*q1}) ÷ 1 = <b>${money(mr)}</b>. MR is below price because the firm must cut the price on all units to sell one more.</p>`}; }},
 {id:'costs', t:'t2-11', name:'AFC, AVC, ATC and MC', hl:true, gen(){ const fc = ri(5, 30) * 10, q = ri(5, 20), vc = ri(5, 15) * q * 10, dvc = ri(4, 18) * 10; const which = pick(['afc', 'avc', 'atc', 'mc']);
   const v = {afc: fc/q, avc: vc/q, atc: (fc + vc)/q, mc: dvc}[which];
   return {q:`A firm has fixed costs of ${money(fc)}. At ${q} units of output its variable costs are ${money(vc)}, and at ${q + 1} units they are ${money(vc + dvc)}. Calculate the ${which.toUpperCase()}${which === 'mc' ? ' of unit ' + (q + 1) : ' at ' + q + ' units'}.`, a:v, unit:'$', w:`<p>AFC = FC ÷ Q = ${fc} ÷ ${q} = ${money(fc/q)}; AVC = VC ÷ Q = ${vc} ÷ ${q} = ${money(vc/q)}; ATC = TC ÷ Q = ${fc + vc} ÷ ${q} = ${money((fc+vc)/q)}</p><p>MC = ΔTC ÷ ΔQ = ${dvc} ÷ 1 = ${money(dvc)} (fixed costs do not change, so ΔTC = ΔVC).</p><p>Answer: <b>${money(v)}</b></p>`}; }},
 {id:'nominal-real', t:'t3-1', name:'Real GDP from nominal GDP and a deflator', gen(){ const n = ri(200, 3000), def = ri(102, 130); const v = n / def * 100;
   return {q:`Nominal GDP is $${n}bn and the GDP deflator is ${def} (base year = 100). Calculate real GDP.`, a:v, unit:'$bn', w:`<p>Real GDP = nominal GDP ÷ deflator × 100 = ${n} ÷ ${def} × 100 = <b>$${f2(v)}bn</b></p>`}; }},
 {id:'growth', t:'t3-1', name:'Real GDP growth rate', gen(){ const a = ri(400, 2000), b = Math.round(a * (1 + pick([-3, -1, 1.5, 2.5, 4, 6.5]) / 100));
   return {q:`Real GDP rises from $${a}bn in year 1 to $${b}bn in year 2. Calculate the rate of economic growth.`, a:pc(a, b), unit:'%', w:`<p>Growth = (${b} − ${a}) ÷ ${a} × 100 = <b>${f2(pc(a,b))}%</b>${b < a ? ' (negative growth: real GDP has fallen).' : ''}</p>`}; }},
 {id:'gni', t:'t3-1', name:'GDP, GNI and per capita', gen(){ const gdp = ri(200, 900), net = ri(-40, 40), pop = ri(5, 80); const which = pick(['gni', 'pc']);
   return {q:`GDP is $${gdp}bn and net income from abroad is ${net < 0 ? '−' : ''}$${Math.abs(net)}bn. The population is ${pop} million. Calculate ${which === 'gni' ? 'GNI' : 'GNI per capita'}.`, a: which === 'gni' ? gdp + net : (gdp + net) * 1000 / pop, unit: which === 'gni' ? '$bn' : '$', w:`<p>GNI = GDP + net income from abroad = ${gdp} + (${net}) = $${gdp + net}bn</p><p>GNI per capita = $${gdp + net}bn ÷ ${pop}m = ${money((gdp + net) * 1000 / pop)}</p><p>Answer: <b>${which === 'gni' ? '$' + (gdp + net) + 'bn' : money((gdp + net) * 1000 / pop)}</b></p>`}; }},
 {id:'cpi', t:'t3-3', name:'Weighted price index and inflation', hl:true, gen(){ const items = shuffle(['Food', 'Housing', 'Transport', 'Clothing', 'Energy']).slice(0, 3); const w = [pick([40, 50]), 30]; w.push(100 - w[0] - w[1]); const ch = items.map(() => pick([-2, 1, 3, 4, 5, 8, 10]));
   const idx = 100 + w.reduce((s, x, i) => s + x * ch[i] / 100, 0);
   return {q:`A basket has three categories: ${items.map((it, i) => `${it} (weight ${w[i]}%, price change ${ch[i] > 0 ? '+' : ''}${ch[i]}%)`).join(', ')}. With the base year index = 100, calculate the new price index.`, a:idx, w:`<p>Weighted change = ${items.map((_, i) => `${w[i]/100} × ${ch[i]}`).join(' + ')} = ${f2(idx - 100)}%</p><p>Index = 100 + ${f2(idx - 100)} = <b>${f2(idx)}</b>, so the inflation rate is ${f2(idx - 100)}%.</p>`}; }},
 {id:'inflation', t:'t3-3', name:'Inflation rate from index numbers', gen(){ const a = ri(100, 160) + ri(0, 9)/10, b = r2(a * (1 + pick([-0.5, 1.2, 2, 3.4, 6, 9]) / 100));
   return {q:`The CPI was ${a} last year and is ${b} this year. Calculate the rate of inflation.`, a:pc(a, b), unit:'%', w:`<p>Inflation = (${b} − ${a}) ÷ ${a} × 100 = <b>${f2(pc(a,b))}%</b></p>`}; }},
 {id:'unemp', t:'t3-3', name:'Unemployment rate', gen(){ const emp = ri(5, 40) * 1000, un = ri(150, 3000); const which = pick(['rate', 'lf']);
   return {q:`${emp.toLocaleString()} thousand people are employed and ${un.toLocaleString()} thousand are unemployed (actively seeking work). Calculate the unemployment rate.`, a: un / (emp + un) * 100, unit:'%', w:`<p>Labour force = employed + unemployed = ${(emp + un).toLocaleString()} thousand</p><p>Unemployment rate = ${un} ÷ ${emp + un} × 100 = <b>${f2(un / (emp + un) * 100)}%</b></p>`}; }},
 {id:'real-i', t:'t3-5', name:'Real interest rate', gen(){ const n = pick([0.5, 1, 2.5, 3.75, 5, 5.25]), inf = pick([1.2, 2, 3.5, 6.4, 8]);
   return {q:`The nominal interest rate is ${n}% and inflation is ${inf}%. Calculate the real interest rate.`, a:n - inf, unit:'%', w:`<p>Real interest rate ≈ nominal rate − inflation = ${n} − ${inf} = <b>${f2(n - inf)}%</b>${n - inf < 0 ? '. It is negative, so savers lose purchasing power and borrowing is cheap in real terms.' : ''}</p>`}; }},
 {id:'mult', t:'t3-6', name:'Keynesian multiplier', hl:true, gen(){ const mode = pick(['mpc', 'leak']); let k, w;
   if (mode === 'mpc'){ const mpc = pick([0.5, 0.6, 0.75, 0.8, 0.9]); k = 1 / (1 - mpc); const g = ri(2, 20); return {q:`The marginal propensity to consume is ${mpc}. Government spending rises by $${g}bn. Calculate the maximum change in real GDP.`, a:k*g, unit:'$bn', w:`<p>k = 1 ÷ (1 − MPC) = 1 ÷ ${f2(1 - mpc)} = ${f2(k)}</p><p>ΔY = k × ΔG = ${f2(k)} × ${g} = <b>$${f2(k*g)}bn</b></p>`}; }
   const s = pick([0.1, 0.15, 0.2]), t = pick([0.1, 0.15, 0.2, 0.25]), m = pick([0.05, 0.1, 0.15, 0.2]); k = 1 / (s + t + m); const inj = ri(1, 15);
   return {q:`MPS = ${s}, MPT = ${t} and MPM = ${m}. Investment rises by $${inj}bn. Calculate the multiplier and the resulting change in real GDP.`, a:k*inj, unit:'$bn', w:`<p>MPW = MPS + MPT + MPM = ${f2(s + t + m)}</p><p>k = 1 ÷ MPW = ${f2(k)}; ΔY = ${f2(k)} × ${inj} = <b>$${f2(k*inj)}bn</b></p>`}; }},
 {id:'budget', t:'t3-6', name:'Budget balance and debt-to-GDP', gen(){ const g = ri(200, 600), t = g + ri(-80, 30), gdp = ri(800, 3000), debt = ri(300, 2500); const which = pick(['bal', 'ratio', 'debtgdp']);
   return {q:`Government spending is $${g}bn and tax revenue is $${t}bn. GDP is $${gdp}bn and the national debt is $${debt}bn. Calculate ${which === 'bal' ? 'the budget balance' : which === 'ratio' ? 'the budget balance as a % of GDP' : 'the debt-to-GDP ratio'}.`, a: which === 'bal' ? t - g : which === 'ratio' ? (t - g) / gdp * 100 : debt / gdp * 100, unit: which === 'bal' ? '$bn' : '%', w:`<p>Budget balance = T − G = ${t} − ${g} = $${t - g}bn (${t - g < 0 ? 'a deficit' : t - g > 0 ? 'a surplus' : 'balanced'}); as % of GDP = ${f2((t - g)/gdp*100)}%</p><p>Debt-to-GDP = ${debt} ÷ ${gdp} × 100 = ${f2(debt/gdp*100)}%</p>`}; }},
 {id:'tax-avg', t:'t3-4', name:'Average and marginal tax rates', hl:true, gen(){ const b1 = 10000, r1 = pick([10, 15]), b2 = 40000, r2_ = pick([20, 25, 30]), r3 = pick([40, 45]); const inc = ri(15, 90) * 1000;
   const tax = Math.max(0, Math.min(inc, b2) - b1) * r1 / 100 + Math.max(0, inc - b2) * r2_ / 100 * 0 + 0;
   const t2 = Math.max(0, Math.min(inc, b2) - b1) * r1/100 + Math.max(0, Math.min(inc, 80000) - b2) * r2_/100 + Math.max(0, inc - 80000) * r3/100;
   const mrate = inc > 80000 ? r3 : inc > b2 ? r2_ : inc > b1 ? r1 : 0;
   const which = pick(['tax', 'avg']);
   return {q:`Income tax: 0% on the first $10,000, ${r1}% on income from $10,001 to $40,000, ${r2_}% from $40,001 to $80,000, and ${r3}% above $80,000. Calculate the ${which === 'tax' ? 'total tax paid' : 'average tax rate'} on an income of ${money(inc)}.`, a: which === 'tax' ? t2 : t2 / inc * 100, unit: which === 'tax' ? '$' : '%', w:`<p>Tax = ${r1}% × ${money(Math.max(0, Math.min(inc, b2) - b1))}${inc > b2 ? ` + ${r2_}% × ${money(Math.min(inc, 80000) - b2)}` : ''}${inc > 80000 ? ` + ${r3}% × ${money(inc - 80000)}` : ''} = ${money(t2)}</p><p>Average rate = ${money(t2)} ÷ ${money(inc)} × 100 = ${f2(t2/inc*100)}%; marginal rate = ${mrate}%.</p><p>Answer: <b>${which === 'tax' ? money(t2) : f2(t2/inc*100) + '%'}</b></p>`}; }},
 {id:'fx-conv', t:'t4-5', name:'Exchange rate conversions', gen(){ const r = pick([0.78, 0.92, 1.08, 1.27, 1.35, 7.1, 82.5, 148]); const cur = r > 5 ? (r > 100 ? 'yen' : r > 50 ? 'rupees' : 'yuan') : 'euros'; const p = ri(5, 500);
   return {q:`The exchange rate is US$1 = ${r} ${cur}. A product costs $${p} in the US. Calculate its price in ${cur}.`, a:p*r, unit:cur, w:`<p>Price in ${cur} = ${p} × ${r} = <b>${f2(p*r)} ${cur}</b></p>`}; }},
 {id:'fx-pct', t:'t4-5', name:'Appreciation or depreciation (%)', gen(){ const a = pick([1.1, 1.25, 0.85, 7.0, 110]), b = r2(a * (1 + pick([-15, -8, -4, 5, 9, 12]) / 100));
   return {q:`The exchange rate of currency X changes from 1 X = ${a} US$ to 1 X = ${b} US$. Calculate the percentage change in the value of currency X.`, a:pc(a, b), unit:'%', w:`<p>% change = (${b} − ${a}) ÷ ${a} × 100 = <b>${f2(pc(a,b))}%</b> → X has ${b > a ? 'appreciated' : 'depreciated'} against the dollar.</p>`}; }},
 {id:'ca', t:'t4-6', name:'Current account balance', gen(){ const g = ri(-60, 40), s = ri(-10, 30), pi = ri(-25, 15), si = ri(-12, 8);
   return {q:`Balance of trade in goods: ${g}; trade in services: ${s}; primary income: ${pi}; secondary income: ${si} (all $bn). Calculate the current account balance.`, a:g + s + pi + si, unit:'$bn', w:`<p>Current account = goods + services + primary income + secondary income = ${g} + ${s} + ${pi} + ${si} = <b>$${g + s + pi + si}bn</b> (${g + s + pi + si < 0 ? 'deficit' : 'surplus'}).</p>`}; }},
 {id:'tot', t:'t4-6', name:'Terms of trade', hl:true, gen(){ const x = ri(90, 130), m = ri(90, 130);
   return {q:`The index of average export prices is ${x} and the index of average import prices is ${m}. Calculate the terms of trade index.`, a:x/m*100, w:`<p>Terms of trade = (index of export prices ÷ index of import prices) × 100 = ${x} ÷ ${m} × 100 = <b>${f2(x/m*100)}</b> → ${x/m > 1 ? 'an improvement since the base year' : x/m < 1 ? 'a deterioration since the base year' : 'no change'}.</p>`}; }},
 {id:'tariff', t:'t4-2', name:'Tariff: revenue and import changes', hl:true, gen(){ const b = ri(2, 5), d = ri(2, 5), pw = ri(4, 10), t = ri(1, 4); const a = ri(120, 220), c = ri(0, 30); const q1 = c + d*pw, q2 = a - b*pw, q3 = c + d*(pw + t), q4 = a - b*(pw + t); const which = pick(['rev', 'imp', 'ps']);
   const ans = {rev:t * (q4 - q3), imp:(q2 - q1) - (q4 - q3), ps: t * (q1 + q3) / 2}[which];
   return {q:`Domestic Qd = ${a} − ${b}P and Qs = ${c} + ${d}P. The world price is ${money(pw)} and the country imposes a tariff of ${money(t)} per unit. Calculate ${which === 'rev' ? 'the tariff revenue' : which === 'imp' ? 'the fall in the quantity imported' : 'the gain in domestic producer surplus'}.`, a:ans, unit: which === 'imp' ? 'units' : '$',
     w:`<p>Free trade at P = ${pw}: Qs = ${q1}, Qd = ${q2}, imports = ${q2 - q1}.</p><p>With the tariff P = ${pw + t}: Qs = ${q3}, Qd = ${q4}, imports = ${q4 - q3}.</p><p>Tariff revenue = ${t} × ${q4 - q3} = ${money(t*(q4-q3))}; fall in imports = ${(q2 - q1) - (q4 - q3)}; gain in PS = ½ × (${q1} + ${q3}) × ${t} = ${money(t*(q1+q3)/2)}.</p><p>Answer: <b>${which === 'imp' ? ans : money(ans)}</b></p>`}; }},
 {id:'oc', t:'t4-1', name:'Opportunity cost and comparative advantage', hl:true, gen(){ const aw = ri(4, 12) * 10, ac = ri(2, 8) * 10, bw = ri(2, 10) * 10, bc = ri(2, 10) * 10; if (aw/ac === bw/bc) return GENS.find(g => g.id === 'oc').gen();
   const ocA = aw/ac, ocB = bw/bc; const who = pick(['A', 'B']);
   return {q:`With all its resources Country A can produce ${aw} wheat or ${ac} cloth; Country B can produce ${bw} wheat or ${bc} cloth. Calculate the opportunity cost of 1 unit of cloth in Country ${who} (in units of wheat).`, a: who === 'A' ? ocA : ocB, unit:'wheat', w:`<p>Opportunity cost of 1 cloth = wheat given up ÷ cloth gained.</p><p>A: ${aw} ÷ ${ac} = ${f2(ocA)} wheat; B: ${bw} ÷ ${bc} = ${f2(ocB)} wheat.</p><p>${ocA < ocB ? 'A' : 'B'} has the lower opportunity cost of cloth, so it has the comparative advantage in cloth; ${ocA < ocB ? 'B' : 'A'} has the comparative advantage in wheat. Any terms of trade between ${f2(Math.min(ocA, ocB))} and ${f2(Math.max(ocA, ocB))} wheat per cloth benefit both.</p>`}; }},
];
let DR = {topic: store.get('econ-drunit', 'all'), cur: null, gen: null, answered: false};
function drillSetup(){
  const list = GENS.filter(g => (DR.topic === 'all' || unitOfTopic(g.t)?.id === DR.topic) && (!SL || !g.hl));
  $('#pv').innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><a href="#formulas">Formulas</a><span>${GENS.length} types</span></div><h1>Calculation drills</h1>
    <p class="lede">Fresh numbers every time. Answer to two decimal places; full working appears after you check. Paper 3 gives method marks, so copy the layout of the working.</p></div>
    <div class="gtools">${unitFilterHTML(DR.topic, 'dr')}</div>
    <div class="pcard" id="drCard"></div>
    <h2 class="sec-h">Choose a type</h2><div class="chips" id="drList">${list.map(g => `<a href="#drills" data-g="${g.id}" class="${g.hl?'hlonly':''}">${esc(g.name)}${g.hl?' · HL':''}</a>`).join('')}</div>`;
  $('#pv [data-uf]').onclick = ev => { const b = ev.target.closest('[data-u]'); if (!b) return; DR.topic = b.dataset.u; store.set('econ-drunit', DR.topic); DR.gen = null; drillSetup(); };
  $('#drList').onclick = ev => { const a = ev.target.closest('[data-g]'); if (!a) return; ev.preventDefault(); DR.gen = GENS.find(g => g.id === a.dataset.g); drillNew(); };
  if (!DR.gen || !list.includes(DR.gen)) DR.gen = null;
  drillNew(list);
}
function drillNew(list){
  list = list || GENS.filter(g => (DR.topic === 'all' || unitOfTopic(g.t)?.id === DR.topic) && (!SL || !g.hl));
  const g = DR.gen || pick(list); if (!g) return;
  DR.cur = Object.assign({g}, g.gen()); DR.answered = false;
  const t = TOPIC[g.t];
  $('#drCard').innerHTML = `<div class="qmeta"><span>${esc(g.name)}${g.hl?' · HL':''}</span><span>${t ? `<a href="#${t.id}">${t.num} ${esc(t.title)}</a>` : ''}</span><span>Record ${P.calc.c}/${P.calc.n}</span></div>
    <div class="qq">${DR.cur.q}</div>
    <form class="calc-in" id="drForm"><label class="vh" for="drIn">Your answer</label><input id="drIn" inputmode="decimal" autocomplete="off" placeholder="Answer${DR.cur.unit ? ' (' + esc(DR.cur.unit) + ')' : ''}"><button class="btn" type="submit">Check</button><button class="btn ghost" type="button" id="drShow">Show working</button><span class="sp"></span><button class="btn ghost" type="button" id="drNext">${DR.gen ? 'Another like this' : 'Next question'}</button></form>
    <div id="drOut"></div>`;
  $('#drForm').onsubmit = ev => { ev.preventDefault(); drillCheck(); };
  $('#drShow').onclick = () => drillCheck(true);
  $('#drNext').onclick = () => drillNew();
}
function drillCheck(reveal){
  const c = DR.cur; const raw = ($('#drIn').value || '').replace(/[,$%\s]/g, '').replace('−', '-');
  const v = parseFloat(raw);
  let ok = null;
  if (!reveal){ if (isNaN(v)){ $('#drOut').innerHTML = '<p class="verdict bad">Type a number first (e.g. −1.25).</p>'; return; }
    ok = Math.abs(v - c.a) <= Math.max(0.011, Math.abs(c.a) * 0.005);
    if (!DR.answered){ P.calc.n++; if (ok) P.calc.c++; saveP(); } DR.answered = true; }
  $('#drOut').innerHTML = `${ok === null ? '' : `<p class="verdict ${ok?'ok':'bad'}">${ok ? 'Correct' : 'Not quite: the answer is ' + f2(c.a) + (c.unit && c.unit !== '$' ? ' ' + esc(c.unit) : '')}</p>`}<div class="work">${c.w}</div>`;
}

// ---------- diagram drill ----------
let DD = {mode:'name', d:null, answered:false};
function ddrillStart(){
  const pool = D.dias.filter(d => !SL || !d.hl);
  DD.d = pick(pool); DD.answered = false;
  const opts = shuffle([DD.d, ...shuffle(pool.filter(x => x !== DD.d)).slice(0, 3)]);
  const masked = DD.d.svg.replace(/<text class="dg-ptitle"[^>]*>.*?<\/text>/g, '');
  $('#pv').innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><a href="#diagrams">Diagrams</a></div><h1>Diagram drill</h1>
    <p class="lede">Two ways to drill. <b>Name it</b>: identify the diagram from the picture. <b>Sketch it</b>: draw it on paper from the name alone, then compare.</p></div>
    <div class="filters" style="margin-bottom:14px"><button id="ddName" aria-pressed="${DD.mode==='name'}">Name it</button><button id="ddSketch" aria-pressed="${DD.mode==='sketch'}">Sketch it</button></div>
    <div class="pcard">${DD.mode === 'name' ? `<div class="qmeta"><span>Which diagram is this?</span></div><figure class="fig ${isWide(DD.d)?'wide':''}" style="border:0;padding:0"><div class="svgwrap">${masked}</div></figure>
      <div class="qopts">${opts.map((o, k) => `<button data-id="${o.id}"><b>${k + 1}.</b> ${esc(o.title)}</button>`).join('')}</div><div id="ddx"></div>`
      : `<div class="qmeta"><span>Sketch this from memory</span><span>${TOPIC[DD.d.topic] ? TOPIC[DD.d.topic].num : ''}</span></div><div class="qq">${esc(DD.d.title)}</div>
      <p>Draw it fully labelled: axes, curves, equilibrium points, shifts and any shaded areas. Then reveal it.</p><div class="prow"><button class="btn" id="ddReveal">Reveal the diagram</button></div><div id="ddx"></div>`}</div>`;
  $('#ddName').onclick = () => { DD.mode = 'name'; ddrillStart(); };
  $('#ddSketch').onclick = () => { DD.mode = 'sketch'; ddrillStart(); };
  const after = ok => `<div class="qx">${ok === null ? '' : `<p class="verdict ${ok?'ok':'bad'}">${ok ? 'Correct' : 'It was: ' + esc(DD.d.title)}</p>`}
    ${DD.mode === 'sketch' ? figHTML(DD.d.id) : ''}<ol>${DD.d.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol>${DD.d.watch ? `<p class="watch" style="color:var(--mark)"><b>Watch out:</b> ${esc(DD.d.watch)}</p>` : ''}
    <div class="prow"><button class="btn" id="ddNext">Next diagram</button><a href="#d-${DD.d.id}">Open the diagram page →</a></div></div>`;
  $$('.qopts button').forEach(b => b.onclick = () => { if (DD.answered) return; DD.answered = true; const ok = b.dataset.id === DD.d.id;
    $$('.qopts button').forEach(x => { x.disabled = true; if (x.dataset.id === DD.d.id) x.classList.add('right'); }); if (!ok) b.classList.add('wrong');
    $('#ddx').innerHTML = after(ok); $('#ddNext').onclick = ddrillStart; });
  $('#ddReveal') && ($('#ddReveal').onclick = () => { $('#ddx').innerHTML = after(null); $('#ddReveal').remove(); $('#ddNext').onclick = ddrillStart; });
}

// ---------- essays ----------
let ES = {paper: store.get('econ-espaper', 'all'), timer: null, left: 0, running: null};
const PAPERS = [['all', 'All'], ['P1a', 'Paper 1 (a) · 10'], ['P1b', 'Paper 1 (b) · 15'], ['P2', 'Paper 2 (g) · 15'], ['P3', 'Paper 3 policy · 10']];
const MINUTES = {P1a: 25, P1b: 40, P2: 35, P3: 25};
function essaysRender(){
  const list = D.essays.filter(e => ES.paper === 'all' || e.paper === ES.paper);
  $('#pv').innerHTML = `<div class="phead"><div class="eyebrow"><a href="#practice">Practice</a><a href="#exam">Exam skills</a><span>${D.essays.length} prompts</span></div><h1>Essay plans</h1>
    <p class="lede">Pick a question, start the timer, write a plan or a full answer, then compare it with the model plan. Timings match the real papers.</p></div>
    <div class="gtools"><div class="filters" id="esF">${PAPERS.map(([k, l]) => `<button data-p="${k}" aria-pressed="${ES.paper===k}">${l}</button>`).join('')}</div><button class="btn ghost" id="esRand">Random question</button></div>
    ${list.map(e => { const t = TOPIC[e.t]; return `<div class="essay" id="es-${e.id}"><div class="qmeta"><span>${esc(PAPERS.find(p=>p[0]===e.paper)?.[1] || e.paper)}</span><span>${t ? `<a href="#${t.id}">${t.num} ${esc(t.title)}</a>` : ''}</span></div>
      <div class="eq">${e.q} <span class="mono">[${esc(e.marks)}]</span></div>
      <div class="prow"><button class="btn ghost" data-time="${e.id}">Start ${MINUTES[e.paper] || 30}-minute timer</button><span class="timer" id="tm-${e.id}"></span></div>
      <details><summary>Model plan</summary><div class="plan">${e.html}</div></details></div>`; }).join('')}`;
  $('#esF').onclick = ev => { const b = ev.target.closest('[data-p]'); if (!b) return; ES.paper = b.dataset.p; store.set('econ-espaper', ES.paper); essaysRender(); };
  $('#esRand').onclick = () => { const e = pick(list); if (!e) return; const el = document.getElementById('es-' + e.id); el.scrollIntoView({block:'center'}); el.classList.remove('flashme'); void el.offsetWidth; el.classList.add('flashme'); };
  $$('[data-time]').forEach(b => b.onclick = () => {
    const id = b.dataset.time, e = D.essays.find(x => x.id === id);
    clearInterval(ES.timer); $$('.timer').forEach(x => x.textContent = '');
    if (ES.running === id){ ES.running = null; b.textContent = `Start ${MINUTES[e.paper] || 30}-minute timer`; return; }
    $$('[data-time]').forEach(x => { const ee = D.essays.find(y => y.id === x.dataset.time); x.textContent = `Start ${MINUTES[ee.paper] || 30}-minute timer`; });
    ES.running = id; ES.left = (MINUTES[e.paper] || 30) * 60; b.textContent = 'Stop timer';
    const tick = () => { const el = document.getElementById('tm-' + id); if (!el){ clearInterval(ES.timer); return; } const m = Math.floor(ES.left / 60), s = ES.left % 60; el.textContent = `${m}:${String(s).padStart(2, '0')}`; if (ES.left-- <= 0){ clearInterval(ES.timer); el.textContent = 'Time!'; toast('Time is up: finish your conclusion'); } };
    tick(); ES.timer = setInterval(tick, 1000);
  });
}

// ---------- missing list ----------
const LKEY = 'econ-missing';
let NOTES = store.get(LKEY, []), notesCol = null, notesOnline = false, notesErr = '';
function notesChanged(){ const open = NOTES.filter(n => !n.done).length; $('#mcount').textContent = open ? String(open) : ''; if (curRoute() === 'missing'){ const y = window.scrollY; view.innerHTML = missingHTML(); window.scrollTo(0, y); } }
notesChanged();
(async () => {
  try {
    if (!window.claude || !window.claude.use) return;
    const db = await window.claude.use('db'); if (!db) return;
    notesCol = db.collection('missing'); notesOnline = true;
    const local = store.get(LKEY, []);
    notesCol.orderBy('createdAt', 'desc').onSnapshot(snap => { NOTES = snap.docs.map(d => Object.assign({id: d.id}, d.data())); notesErr = ''; notesChanged(); },
      e => { notesErr = (e && e.message) || 'Could not load the online list.'; notesChanged(); });
    if (local.length){ for (const n of local){ const c = Object.assign({}, n); delete c.id; await notesCol.add(c); } try { localStorage.removeItem(LKEY); } catch(e){} }
  } catch(e){ notesErr = (e && e.message) || ''; }
})();
function readingContext(){
  const r = curRoute();
  const arts = $$('#view article.entry'); let best = null;
  for (const a of arts){ const b = a.getBoundingClientRect(); if (b.top < window.innerHeight * 0.45 && b.bottom > 70) best = a; }
  if (best && ENTRY[best.id]) return {id: best.id, title: (ENTRY[best.id].topicObj.num ? ENTRY[best.id].topicObj.num + ' · ' : '') + ENTRY[best.id].title};
  if (TOPIC[r]) return {id: r, title: TOPIC[r].title};
  if (r.startsWith('d-') && DIA[r.slice(2)]) return {id: r, title: DIA[r.slice(2)].title};
  const h1 = $('#view h1'); return {id: r, title: h1 ? h1.textContent.trim() : 'Home'};
}
let mctx = null, mkind = '';
function openNotes(){ mctx = readingContext(); $('#mctxT').textContent = mctx.title; $('#mstat').textContent = notesOnline ? 'Saves to the online list Claude can read.' : 'Saves in this browser only (open the guide on claude.ai to save online).'; $('#mstat').classList.remove('err'); $('#mpanel').hidden = false; $('#mfab').setAttribute('aria-expanded', 'true'); $('#mtext').focus(); }
function closeNotes(){ $('#mpanel').hidden = true; $('#mfab').setAttribute('aria-expanded', 'false'); }
$('#mfab').onclick = () => $('#mpanel').hidden ? openNotes() : closeNotes();
$('#mcancel').onclick = closeNotes; $('#mlistLink').onclick = closeNotes;
$$('[data-kind]').forEach(b => b.onclick = () => { mkind = mkind === b.dataset.kind ? '' : b.dataset.kind; $$('[data-kind]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.kind === mkind))); });
$('#msave').onclick = async () => {
  const text = $('#mtext').value.trim();
  if (!text){ $('#mstat').textContent = 'Write a short note first.'; $('#mstat').classList.add('err'); return; }
  const n = {text, kind: mkind || 'missing', ctxId: mctx ? mctx.id : '', ctxTitle: mctx ? mctx.title : '', createdAt: Date.now(), done: false};
  $('#msave').disabled = true;
  try {
    if (notesCol) await notesCol.add(n); else { n.id = 'l' + Date.now(); NOTES.unshift(n); store.set(LKEY, NOTES); notesChanged(); }
    $('#mtext').value = ''; mkind = ''; $$('[data-kind]').forEach(x => x.setAttribute('aria-pressed', 'false')); closeNotes(); toast('Note saved');
  } catch(e){ $('#mstat').textContent = 'Could not save: ' + ((e && e.message) || 'try again.'); $('#mstat').classList.add('err'); }
  $('#msave').disabled = false;
};
function missingHTML(){
  const open = NOTES.filter(n => !n.done), done = NOTES.filter(n => n.done);
  const row = n => `<div class="note ${n.done?'done':''}"><span class="badge">${esc(n.kind || 'missing')}</span><div><p>${esc(n.text)}</p><small>${n.ctxId ? `<a href="#${esc(n.ctxId)}">${esc(n.ctxTitle || n.ctxId)}</a> · ` : ''}${new Date(n.createdAt).toLocaleDateString()}</small></div>
    <div class="acts"><button data-nd="${n.id}">${n.done ? 'Reopen' : 'Done'}</button><button data-nx="${n.id}">Delete</button></div></div>`;
  return `<div class="phead"><div class="eyebrow"><a href="#home">Home</a><span>${notesOnline ? 'Online list' : 'This browser'}</span></div><h1>Missing from the guide</h1>
    <p class="lede">Everything you have flagged while studying. When it gets long, ask Claude to “read the Missing list on my Econ Lock-In guide and add what's there.”</p></div>
    ${notesErr ? `<p class="mstat err">${esc(notesErr)}</p>` : ''}
    <h2 class="sec-h">Open · ${open.length}</h2>${open.length ? open.map(row).join('') : '<div class="empty">Nothing flagged yet. Tap <b>Missing?</b> at the bottom right of any page to add a note.</div>'}
    ${done.length ? `<h2 class="sec-h">Added · ${done.length}</h2>${done.map(row).join('')}` : ''}`;
}
document.addEventListener('click', async ev => {
  const d = ev.target.closest('[data-nd]'), x = ev.target.closest('[data-nx]');
  if (!d && !x) return;
  const id = (d || x).dataset[d ? 'nd' : 'nx']; const n = NOTES.find(q => q.id === id); if (!n) return;
  try {
    if (notesCol && !String(id).startsWith('l')){ const ref = notesCol.doc(id); if (d) await ref.update({done: !n.done}); else await ref.delete(); }
    else { if (d) n.done = !n.done; else NOTES = NOTES.filter(q => q.id !== id); store.set(LKEY, NOTES); notesChanged(); }
  } catch(e){ toast('Could not update the note'); }
});

// ---------- boot ----------
route();
})();
