// The hero's toy: the known as a lit region in the dark, with open questions on its edge.
// Answer one and the region grows, its edge gets longer, and questions that were out of reach come within it.
// Plain SVG and no libraries. Respects prefers-reduced-motion.
(function () {
  var svg = document.getElementById('edge');
  if (!svg) return;
  var NS = 'http://www.w3.org/2000/svg';
  var W = 600, H = 540, CX = 300, CY = 270, R0 = 118, FIT = 196;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Seeded random, so the picture is the same on every visit until someone plays with it.
  var seed = 7;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
  function mk(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function wrap(a) { a = a % (2 * Math.PI); return a < 0 ? a + 2 * Math.PI : a; }
  function gap(a, b) { var d = Math.abs(wrap(a) - wrap(b)); return Math.min(d, 2 * Math.PI - d); }

  var state, bumps, edgeQs, farQs, facts, scale, scaleTo, answered, busy = false, nextId = 0;

  function radius(t) {
    var r = R0 * (1 + 0.075 * Math.sin(3 * t + 0.5) + 0.05 * Math.sin(5 * t + 1.3) + 0.03 * Math.sin(7 * t + 2.1));
    for (var i = 0; i < bumps.length; i++) {
      var b = bumps[i], d = gap(t, b.t);
      r += b.a * Math.exp(-d * d / (2 * b.w * b.w));
    }
    return r;
  }
  function maxRadius() { var m = 0; for (var i = 0; i < 120; i++) m = Math.max(m, radius(i / 120 * 2 * Math.PI)); return m; }
  function px(t, r) { return [CX + Math.cos(t) * r * scale, CY + Math.sin(t) * r * scale]; }

  // ---- static layers ----
  var defs = mk('defs', {}, svg);
  var g1 = mk('radialGradient', { id: 'kg', cx: '50%', cy: '50%', r: '50%' }, defs);
  mk('stop', { offset: '0%', 'stop-color': '#ffd08a', 'stop-opacity': '0.95' }, g1);
  mk('stop', { offset: '55%', 'stop-color': '#f4a340', 'stop-opacity': '0.55' }, g1);
  mk('stop', { offset: '100%', 'stop-color': '#b4540a', 'stop-opacity': '0.28' }, g1);
  var blur = mk('filter', { id: 'soft', x: '-30%', y: '-30%', width: '160%', height: '160%' }, defs);
  mk('feGaussianBlur', { stdDeviation: '14' }, blur);
  var stars = mk('g', { 'class': 'stars', 'aria-hidden': 'true' }, svg);
  for (var s = 0; s < 70; s++) mk('circle', { cx: (rnd() * W).toFixed(1), cy: (rnd() * H).toFixed(1), r: (rnd() * 1.1 + 0.3).toFixed(2), opacity: (rnd() * 0.35 + 0.08).toFixed(2) }, stars);
  var halo = mk('path', { fill: '#f4a340', opacity: '0.35', filter: 'url(#soft)', 'aria-hidden': 'true' }, svg);
  var body = mk('path', { fill: 'url(#kg)', 'aria-hidden': 'true' }, svg);
  var rim = mk('path', { fill: 'none', stroke: '#ffd08a', 'stroke-width': '2', 'stroke-opacity': '0.9', 'aria-hidden': 'true' }, svg);
  var factLayer = mk('g', { 'aria-hidden': 'true' }, svg);
  var farLayer = mk('g', { 'class': 'far', 'aria-hidden': 'true' }, svg);
  var qLayer = mk('g', { 'class': 'edge-qs' }, svg);
  var label = mk('text', { x: CX, y: CY + 6, 'text-anchor': 'middle', 'class': 'known-label', 'aria-hidden': 'true' }, svg);
  label.textContent = 'KNOWN';

  var status = document.getElementById('edge-status');
  var resetBtn = document.getElementById('edge-reset');

  function reset() {
    seed = 7; bumps = []; edgeQs = []; farQs = []; facts = []; scale = scaleTo = 1; answered = 0;
    for (var i = 0; i < 7; i++) addEdge(i / 7 * 2 * Math.PI + 0.35 + rnd() * 0.4);
    for (var j = 0; j < 22; j++) {
      var t = rnd() * 2 * Math.PI, d = R0 * (1.45 + Math.pow(rnd(), 1.6) * 1.9);
      farQs.push({ t: t, d: d, s: 0.7 + rnd() * 0.6 });
    }
    factLayer.textContent = ''; qLayer.textContent = '';
    draw();
    say('Tap a <b>?</b> to answer it.');
  }
  function addEdge(t, fresh) {
    for (var i = 0; i < edgeQs.length; i++) if (gap(edgeQs[i].t, t) < 0.3) return false;
    if (edgeQs.length >= 18) return false;
    edgeQs.push({ t: wrap(t), id: nextId++, fresh: !!fresh });
    return true;
  }
  function say(html) { if (status) status.innerHTML = html; }

  function shapePath() {
    var d = '', n = 160;
    for (var i = 0; i <= n; i++) {
      var t = i / n * 2 * Math.PI, p = px(t, radius(t));
      d += (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    }
    return d + 'Z';
  }

  function draw() {
    var d = shapePath();
    body.setAttribute('d', d); rim.setAttribute('d', d); halo.setAttribute('d', d);
    label.setAttribute('font-size', String(Math.max(11, 15 * scale)));
    // facts: one small light for every answered question, inside the known
    facts.forEach(function (f) {
      var p = px(f.t, f.r);
      f.el.setAttribute('cx', p[0].toFixed(1)); f.el.setAttribute('cy', p[1].toFixed(1));
    });
    // far questions: dim, not yet askable
    farLayer.textContent = '';
    farQs.forEach(function (f) {
      var p = px(f.t, f.d);
      if (p[0] < -20 || p[0] > W + 20 || p[1] < -20 || p[1] > H + 20) return;
      var tx = mk('text', { x: p[0].toFixed(1), y: p[1].toFixed(1), 'text-anchor': 'middle', 'font-size': (16 * f.s * Math.max(scale, 0.55)).toFixed(1) }, farLayer);
      tx.textContent = '?';
    });
    // edge questions: the ones you can answer
    edgeQs.forEach(function (q) {
      var p = px(q.t, radius(q.t) + 20 / scale);
      if (!q.el) {
        q.el = mk('g', { 'class': 'q' + (q.fresh ? ' fresh' : ''), tabindex: '0', role: 'button', 'aria-label': 'Answer this open question' }, qLayer);
        mk('circle', { r: '17', 'class': 'q-ring' }, q.el);
        var tx = mk('text', { 'text-anchor': 'middle', y: '6.5' }, q.el);
        tx.textContent = '?';
        q.el.addEventListener('click', function () { answer(q); });
        q.el.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); answer(q); } });
      }
      q.el.setAttribute('transform', 'translate(' + p[0].toFixed(1) + ' ' + p[1].toFixed(1) + ')');
    });
  }

  function answer(q) {
    if (busy) return;
    busy = true;
    var t = q.t, before = radius(t);
    // the answered question becomes a fact inside the known
    var f = { t: t, r: before * 0.86, el: mk('circle', { r: '3.2', 'class': 'fact' }, factLayer) };
    facts.push(f);
    edgeQs.splice(edgeQs.indexOf(q), 1);
    if (q.el) { q.el.classList.add('gone'); var el = q.el; setTimeout(function () { el.remove(); }, still ? 0 : 450); }
    var b = { t: t, a: 0, w: 0.36 + rnd() * 0.08 }, A = R0 * (0.32 + rnd() * 0.12);
    bumps.push(b);
    answered++;
    var start = performance.now(), dur = still ? 0 : 1100;
    (function step(now) {
      var k = dur ? Math.max(0, Math.min(1, (now - start) / dur)) : 1, e = 1 - Math.pow(1 - k, 3);
      b.a = A * e;
      var target = Math.min(1, FIT / maxRadius());
      scale += (target - scale) * (dur ? 0.08 : 1);
      draw();
      if (k < 1) requestAnimationFrame(step);
      else settle(t);
    })(start);
  }

  function settle(t) {
    // new questions on the longer edge, either side of the answer
    var born = 0;
    [-0.42, 0.42, 0].forEach(function (o, i) {
      if (i === 2 && born >= 2) return;
      if (addEdge(t + o + (rnd() - 0.5) * 0.12, true)) born++;
    });
    // questions that were out of reach now sit on the edge
    var reached = 0;
    farQs = farQs.filter(function (f) {
      if (f.d <= radius(f.t) + R0 * 0.5) { if (addEdge(f.t, true)) reached++; return false; }
      return true;
    });
    // keep a few far ones in the dark, further out than before
    while (farQs.length < 18) farQs.push({ t: rnd() * 2 * Math.PI, d: maxRadius() * (1.5 + rnd() * 1.4), s: 0.7 + rnd() * 0.6 });
    // ease the zoom the rest of the way out
    var target = Math.min(1, FIT / maxRadius());
    (function zoom() {
      scale += (target - scale) * (still ? 1 : 0.12);
      draw();
      if (Math.abs(target - scale) > 0.002) requestAnimationFrame(zoom);
      else { scale = target; draw(); busy = false; }
    })();
    var n = born + reached;
    say('Answered: <b>' + answered + '</b>. ' + (n ? n + ' new question' + (n === 1 ? '' : 's') + ' on the edge' + (reached ? ', ' + reached + ' that nobody could ask before' : '') + '.' : 'The edge grew.') +
      ' Open on the edge now: <b>' + edgeQs.length + '</b>.');
    if (resetBtn) resetBtn.hidden = false;
  }

  if (resetBtn) resetBtn.addEventListener('click', function () {
    if (busy) return;
    reset();
    resetBtn.hidden = true;
  });
  reset();
})();
