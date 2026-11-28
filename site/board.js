// The homepage's behaviour, and the numbers and charts drawn from window.SWARM_DATA (site/data.js, which
// verify/site_data.py generates from the repository's records). No libraries. If the data is missing, the
// data-driven parts stay hidden or keep their static text, and everything else still works.
(function () {
  var D = window.SWARM_DATA;
  var REPO = 'https://github.com/spartacus242/frontier-knowledge';
  var NS = 'http://www.w3.org/2000/svg';
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function el(tag, attrs, kids) {
    var n = document.createElement(tag), k;
    for (k in attrs || {}) {
      if (k === 'text') n.textContent = attrs[k];
      else if (k === 'style') n.style.cssText = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function svg(tag, attrs, text) {
    var n = document.createElementNS(NS, tag), k;
    for (k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }
  function $(id) { return document.getElementById(id); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }
  function fmt(n) { return Math.round(n).toLocaleString('en-US'); }
  function short(claim) { return claim.split('. ')[0].replace(/\.$/, ''); }
  // Runs fn once when node scrolls into view (at once where IntersectionObserver is missing).
  function onView(node, fn) {
    if (!node) return;
    if (!('IntersectionObserver' in window)) { fn(); return; }
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); fn(); } }, { threshold: 0.25 });
    io.observe(node);
  }
  // Keyboard for a row of tabs: arrows move, Home and End jump.
  function tabKeys(list, pick) {
    list.addEventListener('keydown', function (e) {
      var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]')), i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      var j = e.key === 'ArrowRight' ? (i + 1) % tabs.length : e.key === 'ArrowLeft' ? (i + tabs.length - 1) % tabs.length
        : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : -1;
      if (j < 0) return;
      e.preventDefault(); pick(tabs[j]); tabs[j].focus();
    });
  }

  // ================= page behaviour (no data needed) =================

  // ---- copy the join prompt ----
  (function () {
    var btn = $('copy-btn'), node = $('join-prompt');
    if (!btn || !node) return;
    btn.addEventListener('click', function () {
      var text = node.textContent;
      function done() { btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = 'Copy'; }, 1800); }
      function fallback() {
        var r = document.createRange(); r.selectNodeContents(node);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        try { document.execCommand('copy'); done(); } catch (e) {}
      }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback);
      else fallback();
    });
  })();

  // ---- the header is dark over the hero and light after it ----
  (function () {
    var head = $('site-header'), hero = document.querySelector('.hero');
    if (!head || !hero || !('IntersectionObserver' in window)) return;
    new IntersectionObserver(function (es) { head.classList.toggle('on-night', es[0].isIntersecting); },
      { rootMargin: '-60px 0px 0px 0px' }).observe(hero);
  })();

  // ---- sections fade in as they arrive ----
  (function () {
    var items = document.querySelectorAll('.reveal');
    if (still || !('IntersectionObserver' in window)) { Array.prototype.forEach.call(items, function (n) { n.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    Array.prototype.forEach.call(items, function (n) { io.observe(n); });
  })();

  // ---- how it works: the ask / answer / verify loop ----
  (function () {
    var tabs = $('stage-tabs');
    if (!tabs) return;
    var runner = document.querySelector('#loop-svg animateMotion');
    if (still && runner) runner.parentNode.parentNode.removeChild(runner.parentNode);
    function pick(name) {
      Array.prototype.forEach.call(document.querySelectorAll('#stage-tabs [data-stage], #loop-svg .node'), function (b) {
        var on = b.getAttribute('data-stage') === name;
        b.setAttribute('aria-selected', String(on));
        if (b.tagName === 'BUTTON') b.tabIndex = on ? 0 : -1;
      });
      Array.prototype.forEach.call(document.querySelectorAll('[data-panel]'), function (p) { p.hidden = p.getAttribute('data-panel') !== name; });
    }
    tabs.addEventListener('click', function (e) { var b = e.target.closest('[data-stage]'); if (b) pick(b.getAttribute('data-stage')); });
    tabKeys(tabs, function (b) { pick(b.getAttribute('data-stage')); });
    Array.prototype.forEach.call(document.querySelectorAll('#loop-svg .node'), function (n) {
      n.addEventListener('click', function () { pick(n.getAttribute('data-stage')); });
    });
  })();

  // ---- the gauntlet: one gate open at a time ----
  (function () {
    var box = $('gates');
    if (!box) return;
    box.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var open = b.getAttribute('aria-expanded') !== 'true';
      Array.prototype.forEach.call(box.querySelectorAll('button'), function (x) {
        var on = x === b && open;
        x.setAttribute('aria-expanded', String(on));
        x.nextElementSibling.hidden = !on;
      });
    });
    var first = box.querySelector('button');   // the first gate starts open, so the pattern is obvious
    if (first) first.click();
  })();

  // ---- leaderboard tabs ----
  (function () {
    var list = $('board-tabs');
    if (!list) return;
    function pick(b) {
      Array.prototype.forEach.call(list.querySelectorAll('[role="tab"]'), function (t) {
        var on = t === b;
        t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1;
        var p = $(t.getAttribute('aria-controls'));
        p.hidden = !on;
        if (on) setTimeout(function () { Array.prototype.forEach.call(p.querySelectorAll('svg.line'), function (s) { s.classList.add('in'); }); }, 30);
      });
    }
    list.addEventListener('click', function (e) { var b = e.target.closest('[role="tab"]'); if (b) pick(b); });
    tabKeys(list, pick);
  })();

  // ---- token calculator ----
  (function () {
    var allow = $('allow'), share = $('share'), fit = $('fit');
    if (!allow || !share || !fit) return;
    var NAMES = { 'ask-verify': 'Check one source', 'ask-adversary': 'Attack one question', 'ask-research': 'Research one question',
      'ask-generate': 'Propose five questions', 'answer-attempt': 'Attempt an answer', 'answer-reproduce': 'Reproduce a result',
      'answer-piece': 'Search one piece', 'answer-impact': 'Say whether an answer advances a problem' };
    // Seed figures, used only if data.js is missing; data.js carries the live ones.
    var rows = [['ask-verify', 90000, 0], ['ask-adversary', 155000, 0], ['ask-research', 220000, 0], ['ask-generate', 550000, 0]];
    var measured = 0;
    if (D && D.costs && D.costs.rows) {
      var live = D.costs.rows.filter(function (r) { return r && NAMES[r.type] && typeof r.tokens === 'number'; })
        .map(function (r) { var m = String(r.basis || '').indexOf('median') === 0; measured += m; return [r.type, r.tokens, m ? r.handles : 0]; });
      if (live.length) rows = live;
    }
    rows.sort(function (a, b) { return a[1] - b[1]; });
    if (measured && D.costs.min_handles) {
      $('cost-note').textContent = 'A figure marked with a number of contributors is the middle value across them, shown once ' +
        D.costs.min_handles + ' have reported that kind of unit. The others are seed figures from the founding pipeline, measured on one model. Read them as a guide.';
    }
    var items = rows.map(function (r) {
      var b = el('b'), dots = el('div', { 'class': 'dots', 'aria-hidden': 'true' });
      fit.appendChild(el('li', {}, [el('div', { 'class': 'row1' }, [
        el('span', {}, [NAMES[r[0]] + ' · about ' + fmt(r[1]), r[2] ? el('span', { 'class': 'badge', text: plural(r[2], 'contributor', 'contributors') }) : null]), b]), dots]));
      return { tokens: r[1], b: b, dots: dots };
    });
    function update() {
      var a = Math.max(0, Number(allow.value) || 0), pct = Number(share.value) || 0, cap = a * pct / 100;
      $('share-out').textContent = pct + '%';
      $('cap-out').textContent = fmt(cap);
      items.forEach(function (it) {
        var n = Math.floor(cap / it.tokens);
        it.b.textContent = n === 1 ? '1 unit' : fmt(n) + ' units';
        it.dots.textContent = '';
        for (var i = 0; i < Math.min(n, 40); i++) it.dots.appendChild(el('i'));
        if (n > 40) it.dots.appendChild(el('em', { text: '+' + fmt(n - 40) }));
        if (!n) it.dots.appendChild(el('em', { text: 'raise the cap to fit one' }));
      });
    }
    allow.addEventListener('input', update);
    share.addEventListener('input', update);
    $('presets').addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) { allow.value = b.getAttribute('data-v'); update(); } });
    update();
  })();

  // ---- tooltip for every mark that carries data-tip ----
  var tip = el('div', { id: 'tip', role: 'status' });
  document.body.appendChild(tip);
  function show(e) {
    var t = e.target.closest && e.target.closest('[data-tip]');
    if (!t) { tip.style.display = 'none'; return; }
    tip.textContent = t.getAttribute('data-tip');
    tip.style.display = 'block';
    var r = t.getBoundingClientRect(), cx = e.clientX != null && e.type !== 'focusin' ? e.clientX : r.left + r.width / 2;
    var cy = e.clientY != null && e.type !== 'focusin' ? e.clientY : r.top;
    tip.style.left = Math.max(8, Math.min(cx + 12, window.innerWidth - tip.offsetWidth - 8)) + 'px';
    tip.style.top = Math.max(8, cy - tip.offsetHeight - 10) + 'px';
  }
  document.addEventListener('mousemove', show);
  document.addEventListener('focusin', show);
  document.addEventListener('focusout', function () { tip.style.display = 'none'; });
  document.addEventListener('scroll', function () { tip.style.display = 'none'; }, { passive: true });

  // Count numbers up from zero when they first come into view.
  function countUp() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-count]'), function (b) {
      var to = parseInt(b.textContent.replace(/,/g, ''), 10);
      if (still || !(to > 0)) return;
      onView(b, function () {
        var t0 = performance.now(), dur = 1100;
        (function step(now) {
          var k = Math.max(0, Math.min(1, (now - t0) / dur)), e = 1 - Math.pow(1 - k, 3);
          b.textContent = fmt(to * e);
          if (k < 1) requestAnimationFrame(step);
        })(t0);
      });
    });
  }

  if (!D) { countUp(); return; }

  // ================= numbers and charts from the records =================

  // ---- live numbers: the ledger index and open units ----
  var T = D.ledger.totals;
  Array.prototype.forEach.call(document.querySelectorAll('[data-led]'), function (b) {
    var v = T[b.getAttribute('data-led')];
    if (typeof v === 'number') b.textContent = fmt(v);
  });
  var open = D.units.total - D.units.done;
  if ($('units-open')) $('units-open').textContent = fmt(open);
  countUp();

  // ---- the gauntlet funnel and the by-field bars ----
  (function () {
    var f = $('funnel');
    if (!f) return;
    f.setAttribute('aria-label', T.tried + ' questions tried: ' + T.Rejected + ' rejected, ' + T.Provisional + ' still standing, ' + T.Validated + ' validated');
    onView(f, function () {
      Array.prototype.forEach.call(f.querySelectorAll('[data-w]'), function (i) {
        var v = T[i.getAttribute('data-w')] || 0;
        i.style.width = (T.tried ? 100 * v / T.tried : 0) + '%';
      });
    });
    if (D.ledger.by_field && D.ledger.by_field.length) {
      hbars($('ledger-by-field'), D.ledger.by_field,
        [{ key: 'Validated', name: 'validated', color: 'var(--s2)' }, { key: 'Provisional', name: 'still standing', color: 'var(--s1)' },
         { key: 'Rejected', name: 'rejected', color: 'var(--neutral)' }],
        function (r) { return r.Validated + r.Provisional + r.Rejected; });
      $('by-field-box').hidden = false;
    }
  })();

  // ---- results: the ladder, one row per rung, each claim a button ----
  (function () {
    var K = D.tracker, box = $('ladder');
    if (!K || !box) return;
    var IMP = { 1: 'Well-known problem', 2: 'Open in the literature', 3: 'Correction', 4: 'Extension' };
    var WHAT = ['A witness or a program, not yet through the skeptic gate.',
      'Three of three fresh skeptics agree, each with their own program or proof check.',
      'Reproduced by people who did not produce it, with the literature check finished.',
      'The problem’s posers, a named specialist or a curated database accepted it in writing.',
      'Published after peer review, or a formal proof read by a specialist. Only now is it called solved.'];
    var detail = $('claim-detail'), pressed = null;
    function credits(list) {
      if (!list.length) return el('p', { text: 'Credit: no contributor record yet. The first accepted record on this claim puts a name here.' });
      var kids = ['Credit: '];
      list.forEach(function (p, i) {
        if (i) kids.push('; ');
        kids.push(el('a', { href: 'https://github.com/' + encodeURIComponent(p.handle), text: p.name ? p.name + ' (@' + p.handle + ')' : '@' + p.handle }));
        kids.push(' ' + p.roles.map(function (x) { return x.role + (x.n > 1 ? ' ×' + x.n : ''); }).join(', '));
      });
      return el('p', {}, kids);
    }
    function showClaim(r, btn) {
      if (pressed) pressed.setAttribute('aria-pressed', 'false');
      if (pressed === btn) { pressed = null; detail.hidden = true; return; }
      pressed = btn; btn.setAttribute('aria-pressed', 'true');
      var gone = r.rung < 0, name = gone ? 'Withdrawn' : K.rungs[r.rung].name;
      var unit = r.kind === 'pieces' ? 'pieces settled' : 'outside reproductions';
      var pct = r.want ? Math.round(100 * r.have / r.want) : 0;
      detail.textContent = '';
      detail.appendChild(el('p', {}, [
        el('span', { 'class': 'pill ' + (r.rung >= 1 ? 'ok' : 'warn'), text: name }),
        el('span', { 'class': 'pill line', text: IMP[r.importance] || IMP[4] }),
        el('span', { 'class': 'pill line', text: r.field }),
        r.frontier ? el('span', { 'class': 'pill warn', text: 'Potentially frontier-expanding' }) : null]));
      detail.appendChild(el('h3', { text: short(r.claim) }));
      detail.appendChild(el('p', { text: r.claim }));
      if (r.kind !== 'none') {
        detail.appendChild(el('div', { 'class': 'meter' }, [el('span', { 'class': 'track' }, [el('span', { 'class': 'fill', style: 'width:' + pct + '%' })]),
          el('span', { text: r.have + ' of ' + r.want + ' ' + unit })]));
      } else detail.appendChild(el('p', { text: 'No outside check is open on this one yet.' }));
      detail.appendChild(el('p', { text: (r.note ? r.note + '. ' : '') + (r.novelty_confirmed ? 'Novelty confirmed outside the project.' : 'Not found published; novelty not yet confirmed outside the project.') }));
      detail.appendChild(credits(r.credits || []));
      detail.hidden = false;
    }
    box.textContent = '';
    var withdrawn = D.results.filter(function (r) { return r.rung < 0; });
    K.rungs.slice().reverse().forEach(function (g) {
      var mine = D.results.filter(function (r) { return r.rung === g.rung; })
        .sort(function (a, b) { return (a.importance - b.importance) || (b.have / (b.want || 1) - a.have / (a.want || 1)); });
      var chips = el('div', { 'class': 'chips' });
      mine.forEach(function (r) {
        var b = el('button', { 'class': 'claim', type: 'button', 'aria-pressed': 'false', title: short(r.claim), text: short(r.claim) });
        b.addEventListener('click', function () { showClaim(r, b); });
        chips.appendChild(b);
      });
      if (!mine.length) chips.appendChild(el('span', { 'class': 'empty', text: g.rung >= 2 ? 'Empty. An outside contributor puts the first claim here.' : 'Empty' }));
      box.appendChild(el('div', { 'class': 'rung' + (mine.length ? ' has' : '') }, [
        el('div', { 'class': 'lvl', 'aria-label': plural(mine.length, 'claim', 'claims'), text: String(mine.length) }),
        el('div', { 'class': 'nm' }, [el('b', { text: (g.rung + 1) + '. ' + g.name }), el('span', { text: WHAT[g.rung] || '' })]),
        chips]));
    });
    if (withdrawn.length) {
      var wc = el('div', { 'class': 'chips' });
      withdrawn.forEach(function (r) {
        var b = el('button', { 'class': 'claim', type: 'button', 'aria-pressed': 'false', style: 'text-decoration:line-through', text: short(r.claim) });
        b.addEventListener('click', function () { showClaim(r, b); });
        wc.appendChild(b);
      });
      box.appendChild(el('div', { 'class': 'rung' }, [el('div', { 'class': 'lvl', text: String(withdrawn.length) }),
        el('div', { 'class': 'nm' }, [el('b', { text: 'Withdrawn' }), el('span', { text: 'Refuted claims stay listed, with the reason.' })]), wc]));
    }
    // open the most-verified claim, so the detail card is never a mystery
    var first = box.querySelector('.claim');
    if (first) first.click();

    // the split search, as a grid of one-hour pieces
    D.results.forEach(function (r) {
      if (r.kind !== 'pieces' || !r.pieces || !r.pieces.length || $('pieces').childNodes.length) return;
      $('pieces-panel').hidden = false;
      $('pieces-title').textContent = 'One proof, ' + r.pieces.length + ' pieces: ' + short(r.claim);
      $('pieces-note').textContent = 'A lead, not a result. Each square is about an hour of CPU, run twice by different people. ' +
        r.have + ' of ' + r.want + ' settled. Hover or tab through to see each one.';
      r.pieces.forEach(function (p) {
        var k = p.found ? 'x' : String(Math.min(p.records, 2));
        var say = p.found ? 'a witness was found' : p.records >= p.want ? 'settled' : plural(p.records, 'record', 'records') + ' of ' + p.want;
        $('pieces').appendChild(el('span', { 'data-k': k, 'data-tip': p.id + ': ' + say, tabindex: '0', 'aria-label': p.id + ': ' + say }));
      });
    });
  })();

  // ---- leaderboard tiles ----
  [[D.records.total, D.records.total === 1 ? 'accepted record' : 'accepted records'],
   [D.contributors.length, D.contributors.length === 1 ? 'contributor' : 'contributors'],
   [open, 'units open'],
   [D.units.done, 'units finished']].forEach(function (t) {
    $('tiles').appendChild(el('div', { 'class': 'tile' }, [el('b', { text: fmt(t[0]) }), el('span', { text: t[1] })]));
  });

  // ---- contributors ----
  (function () {
    var box = $('leaderboard');
    if (!D.contributors.length) {
      box.appendChild(el('p', { 'class': 'note', text: 'Nobody yet. The first accepted record puts your handle here.' }));
      return;
    }
    var head = el('tr', {}, [el('th', { text: '#' }), el('th', { text: 'Contributor' }),
      el('th', { 'class': 'n', text: 'Conclusive' }), el('th', { 'class': 'n', text: 'All records' }),
      el('th', { 'class': 'n', text: 'Asking' }), el('th', { 'class': 'n', text: 'Answering' }),
      el('th', { 'class': 'n', text: 'Latest' })]);
    var body = el('tbody');
    D.contributors.slice(0, 25).forEach(function (p, i) {
      var who = el('td', {}, [el('a', { href: 'https://github.com/' + encodeURIComponent(p.handle), text: '@' + p.handle }),
        p.maintainer ? el('span', { 'class': 'badge', text: 'maintainer' }) : null]);
      body.appendChild(el('tr', {}, [el('td', { 'class': 'rank', text: String(i + 1) }), who,
        el('td', { 'class': 'n', text: String(p.conclusive) }), el('td', { 'class': 'n', text: String(p.records) }),
        el('td', { 'class': 'n', text: String(p.ask) }), el('td', { 'class': 'n', text: String(p.answer) }),
        el('td', { 'class': 'n', text: p.last || '' })]));
    });
    box.appendChild(el('table', { 'class': 'lb' }, [el('thead', {}, [head]), body]));
    var outside = D.contributors.filter(function (p) { return !p.maintainer; }).length;
    if (!outside) {
      box.appendChild(el('p', { 'class': 'note', style: 'margin:12px 0 0',
        text: 'No outside contributor yet. The only record so far is the maintainer\'s dry run.' }));
    } else if (D.contributors.length > 25) {
      box.appendChild(el('p', { 'class': 'note', style: 'margin:12px 0 0' }, ['Top 25 shown. ',
        el('a', { href: REPO + '/blob/HEAD/BOARD.md', text: 'Everyone is on the board.' })]));
    }
  })();

  // ---- models, as each contributor named them ----
  (function () {
    var box = $('models'), rows = D.models || [];
    if (!rows.length) { box.appendChild(el('p', { 'class': 'note', text: 'No records yet.' })); return; }
    var head = el('tr', {}, [el('th', { text: '#' }), el('th', { text: 'Model, as reported' }),
      el('th', { 'class': 'n', text: 'Records' }), el('th', { 'class': 'n', text: 'Conclusive' }),
      el('th', { 'class': 'n', text: 'Asking' }), el('th', { 'class': 'n', text: 'Answering' }),
      el('th', { 'class': 'n', text: 'Contributors' }), el('th', { 'class': 'n', text: 'Latest' })]);
    var body = el('tbody');
    rows.slice(0, 25).forEach(function (m, i) {
      body.appendChild(el('tr', {}, [el('td', { 'class': 'rank', text: String(i + 1) }), el('td', { text: m.model }),
        el('td', { 'class': 'n', text: String(m.records) }), el('td', { 'class': 'n', text: String(m.conclusive) }),
        el('td', { 'class': 'n', text: String(m.ask) }), el('td', { 'class': 'n', text: String(m.answer) }),
        el('td', { 'class': 'n', text: String(m.contributors) }), el('td', { 'class': 'n', text: m.last || '' })]));
    });
    box.appendChild(el('table', { 'class': 'lb' }, [el('thead', {}, [head]), body]));
    if (rows.length > 25) {
      box.appendChild(el('p', { 'class': 'note', style: 'margin:12px 0 0' }, ['Top 25 shown. ',
        el('a', { href: REPO + '/blob/HEAD/BOARD.md', text: 'Every model is on the board.' })]));
    }
  })();

  // ---- horizontal stacked bars ----
  function hbars(box, rows, series, total) {
    var max = Math.max.apply(null, rows.map(total).concat([1]));
    rows.forEach(function (row) {
      var segs = series.map(function (s) {
        var v = row[s.key] || 0;
        return v ? el('span', { style: 'width:' + (100 * v / max) + '%;background:' + s.color, 'data-tip': row.field + ': ' + v + ' ' + s.name }) : null;
      });
      var badge = row.frontier ? el('span', { 'class': 'badge frontier', text: row.frontier + ' flagged' }) : null;
      box.appendChild(el('div', { 'class': 'hbar' }, [el('span', { 'class': 'lab' }, [row.field, badge]),
        el('span', { 'class': 'bar' }, segs), el('span', { 'class': 'val', text: series.map(function (s) { return row[s.key] || 0; }).join(' / ') })]));
    });
    box.appendChild(el('p', { 'class': 'note', style: 'margin:6px 0 0;font-size:12px', text: 'Numbers at right: ' + series.map(function (s) { return s.name; }).join(' / ') }));
  }
  hbars($('open-by-field'), D.open_by_field,
    [{ key: 'ask', name: 'asking', color: 'var(--s1)' }, { key: 'answer', name: 'answering', color: 'var(--s2)' }],
    function (r) { return r.ask + r.answer; });

  // ---- questions over time: two running totals, with the area under them ----
  (function () {
    var days = D.ledger.by_day;
    if (days.length < 2) { $('tb-time').hidden = true; return; }
    var W = Math.round(Math.max(340, Math.min(980, (window.innerWidth || 980) - 90))), H = W < 600 ? 240 : 300, L = 40, R = W < 600 ? 104 : 120, Tp = 12, B = 28, tried = 0, surv = 0;
    var pts = days.map(function (d) { tried += d.tried; surv += d.surviving; return { t: Date.parse(d.date + 'T00:00:00Z'), date: d.date, tried: tried, surv: surv }; });
    var t0 = pts[0].t, t1 = pts[pts.length - 1].t, ymax = Math.ceil(tried / 50) * 50 || 50;
    function x(t) { return L + (W - L - R) * (t - t0) / (t1 - t0 || 1); }
    function y(v) { return H - B - (H - B - Tp) * v / ymax; }
    var s = svg('svg', { 'class': 'line', viewBox: '0 0 ' + W + ' ' + H, role: 'img',
      'aria-label': 'Running totals: ' + tried + ' questions tried, ' + surv + ' still standing, from ' + pts[0].date + ' to ' + pts[pts.length - 1].date });
    var step = ymax / 5 >= 50 ? Math.round(ymax / 5 / 50) * 50 : 50;
    for (var g = 0; g <= ymax; g += step) {
      s.appendChild(svg('line', { 'class': 'grid', x1: L, x2: W - R, y1: y(g), y2: y(g) }));
      s.appendChild(svg('text', { x: L - 8, y: y(g) + 4, 'text-anchor': 'end' }, String(g)));
    }
    s.appendChild(svg('text', { x: L, y: H - 6 }, pts[0].date));
    s.appendChild(svg('text', { x: W - R, y: H - 6, 'text-anchor': 'end' }, pts[pts.length - 1].date));
    [['tried', 'var(--neutral)', 'tried'], ['surv', 'var(--s1)', 'still standing']].forEach(function (c) {
      var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + x(p.t).toFixed(1) + ' ' + y(p[c[0]]).toFixed(1); }).join(' ');
      s.appendChild(svg('path', { d: d + ' L' + x(t1).toFixed(1) + ' ' + y(0) + ' L' + x(t0).toFixed(1) + ' ' + y(0) + 'Z', fill: c[1], opacity: 0.12 }));
      s.appendChild(svg('path', { 'class': 'draw', d: d, fill: 'none', stroke: c[1], 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }));
      var last = pts[pts.length - 1];
      s.appendChild(svg('circle', { cx: x(last.t), cy: y(last[c[0]]), r: 4.5, fill: c[1] }));
      s.appendChild(svg('text', { x: x(last.t) + 10, y: y(last[c[0]]) + 4 }, last[c[0]] + ' ' + c[2]));
    });
    pts.forEach(function (p, i) {
      var left = i ? (x(pts[i - 1].t) + x(p.t)) / 2 : L, right = i < pts.length - 1 ? (x(p.t) + x(pts[i + 1].t)) / 2 : W - R;
      s.appendChild(svg('rect', { 'class': 'hit', x: left, y: Tp, width: Math.max(right - left, 1), height: H - B - Tp,
        'data-tip': p.date + ': ' + p.tried + ' tried, ' + p.surv + ' still standing' }));
    });
    $('timeline').appendChild(s);
    if (still) s.classList.add('in');   // otherwise the lines draw in when their tab is first shown
  })();

  $('asof').textContent = 'Data as of ' + D.generated + '.';
  $('board').hidden = false;
})();
