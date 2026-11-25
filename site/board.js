// Draws the leaderboard and charts on the landing page from window.SWARM_DATA (site/data.js, which
// verify/site_data.py generates from the repository's records). No libraries. If the data is missing, the
// section stays hidden and the page's static text stands.
(function () {
  var D = window.SWARM_DATA;
  if (!D) return;
  var REPO = 'https://github.com/spartacus242/frontier-knowledge';
  var NS = 'http://www.w3.org/2000/svg';

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

  // ---- the static stat tiles in "Where it stands" follow the ledger index ----
  var T = D.ledger.totals;
  Array.prototype.forEach.call(document.querySelectorAll('[data-led]'), function (b) {
    var v = T[b.getAttribute('data-led')];
    if (typeof v === 'number') b.textContent = v;
  });

  // ---- tiles ----
  var open = D.units.total - D.units.done;
  [[D.records.total, plural(D.records.total, 'accepted record', 'accepted records').replace(/^\d+ /, '')],
   [D.contributors.length, D.contributors.length === 1 ? 'contributor' : 'contributors'],
   [open, 'units open'],
   [D.units.done, 'units finished']].forEach(function (t) {
    $('tiles').appendChild(el('div', { 'class': 'stat' }, [el('b', { text: String(t[0]) }), el('span', { text: t[1] })]));
  });

  // ---- leaderboard ----
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

  // ---- outside checks ----
  (function () {
    var box = $('checks'), shown = 0;
    D.results.forEach(function (r) {
      if (r.kind === 'none') return;
      shown++;
      var label = r.refuted ? 'Refuted by an outside record'
        : r.inside_confirmed ? 'Confirmed inside the project' : 'Lead, not confirmed';
      var unit = r.kind === 'pieces' ? 'pieces settled' : 'outside reproductions';
      var pct = r.want ? Math.round(100 * r.have / r.want) : 0;
      box.appendChild(el('div', { 'class': 'check' }, [
        el('p', { 'class': 't' }, [r.claim.split('. ')[0].replace(/\.$/, ''),
          el('span', { 'class': 'badge', text: label }),
          r.frontier ? el('span', { 'class': 'badge frontier', text: 'potentially frontier-expanding' }) : null]),
        el('div', { 'class': 'meter', 'data-tip': r.have + ' of ' + r.want + ' ' + unit }, [
          el('span', { 'class': 'track' }, [el('span', { 'class': 'fill', style: 'width:' + pct + '%' })]),
          el('span', { text: r.have + ' of ' + r.want + ' ' + unit })])
      ]));
      if (r.kind === 'pieces' && r.pieces.length) drawPieces(r);
    });
    if (!shown) box.appendChild(el('p', { 'class': 'note', text: 'No result has an outside check open yet.' }));
  })();

  function drawPieces(r) {
    $('pieces-panel').hidden = false;
    $('pieces-title').textContent = r.claim.split('. ')[0].replace(/\.$/, '') + ', in ' + r.pieces.length + ' pieces';
    $('pieces-note').textContent = 'A lead, not a result. Each square is about an hour of CPU, run twice by different people. ' +
      r.have + ' of ' + r.want + ' settled.';
    r.pieces.forEach(function (p) {
      var k = p.found ? 'x' : String(Math.min(p.records, 2));
      var say = p.found ? 'a witness was found' : p.records >= p.want ? 'settled' : plural(p.records, 'record', 'records') + ' of ' + p.want;
      $('pieces').appendChild(el('span', { 'data-k': k, 'data-tip': p.id + ': ' + say, tabindex: '0', 'aria-label': p.id + ': ' + say }));
    });
  }

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
  hbars($('ledger-by-field'), D.ledger.by_field,
    [{ key: 'Validated', name: 'validated', color: 'var(--s2)' }, { key: 'Provisional', name: 'provisional', color: 'var(--s1)' },
     { key: 'Rejected', name: 'rejected', color: 'var(--neutral)' }],
    function (r) { return r.Validated + r.Provisional + r.Rejected; });

  // ---- questions over time: two running totals on one axis ----
  (function () {
    var days = D.ledger.by_day;
    if (days.length < 2) { $('timeline').parentNode.hidden = true; return; }
    var W = 720, H = 240, L = 40, R = 96, Tp = 12, B = 28, tried = 0, surv = 0;
    var pts = days.map(function (d) { tried += d.tried; surv += d.surviving; return { t: Date.parse(d.date + 'T00:00:00Z'), date: d.date, tried: tried, surv: surv }; });
    var t0 = pts[0].t, t1 = pts[pts.length - 1].t, ymax = Math.ceil(tried / 50) * 50 || 50;
    function x(t) { return L + (W - L - R) * (t - t0) / (t1 - t0 || 1); }
    function y(v) { return H - B - (H - B - Tp) * v / ymax; }
    var s = svg('svg', { 'class': 'line', viewBox: '0 0 ' + W + ' ' + H, role: 'img',
      'aria-label': 'Running totals: ' + tried + ' questions tried, ' + surv + ' still standing, from ' + pts[0].date + ' to ' + pts[pts.length - 1].date });
    for (var g = 0; g <= ymax; g += ymax / 5 >= 50 ? Math.round(ymax / 5 / 50) * 50 : 50) {
      s.appendChild(svg('line', { 'class': 'grid', x1: L, x2: W - R, y1: y(g), y2: y(g) }));
      s.appendChild(svg('text', { x: L - 8, y: y(g) + 4, 'text-anchor': 'end' }, String(g)));
    }
    s.appendChild(svg('text', { x: L, y: H - 6 }, pts[0].date));
    s.appendChild(svg('text', { x: W - R, y: H - 6, 'text-anchor': 'end' }, pts[pts.length - 1].date));
    [['tried', 'var(--neutral)', 'tried'], ['surv', 'var(--s1)', 'still standing']].forEach(function (c) {
      var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + x(p.t).toFixed(1) + ' ' + y(p[c[0]]).toFixed(1); }).join(' ');
      s.appendChild(svg('path', { d: d, fill: 'none', stroke: c[1], 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }));
      var last = pts[pts.length - 1];
      s.appendChild(svg('circle', { cx: x(last.t), cy: y(last[c[0]]), r: 4, fill: c[1] }));
      s.appendChild(svg('text', { x: x(last.t) + 9, y: y(last[c[0]]) + 4 }, last[c[0]] + ' ' + c[2]));
    });
    pts.forEach(function (p, i) {
      var left = i ? (x(pts[i - 1].t) + x(p.t)) / 2 : L, right = i < pts.length - 1 ? (x(p.t) + x(pts[i + 1].t)) / 2 : W - R;
      s.appendChild(svg('rect', { 'class': 'hit', x: left, y: Tp, width: Math.max(right - left, 1), height: H - B - Tp,
        'data-tip': p.date + ': ' + p.tried + ' tried, ' + p.surv + ' still standing' }));
    });
    $('timeline').appendChild(s);
  })();

  // ---- open problems by field (shown once answer/open-problems.json exists) ----
  (function () {
    var list = D.open_problems || [];
    if (!list.length) return;
    $('problems-panel').hidden = false;
    var by = {};
    list.forEach(function (p) { (by[p.field || 'Other fields'] = by[p.field || 'Other fields'] || []).push(p); });
    Object.keys(by).sort().forEach(function (f) {
      $('problems').appendChild(el('p', { 'class': 't', style: 'font-weight:600;margin:10px 0 4px', text: f }));
      $('problems').appendChild(el('ul', { 'class': 'plain' }, by[f].map(function (p) {
        return el('li', {}, [String(p.title || p.statement || ''), p.frontier ? el('span', { 'class': 'badge frontier', text: 'potentially frontier-expanding' }) : null]);
      })));
    });
  })();

  $('asof').textContent = 'Data as of ' + D.generated + '.';
  $('board').hidden = false;

  // ---- one tooltip for every mark that carries data-tip ----
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
})();
