/* Nigeria geology & minerals — live comparison viewer
 *
 * Everything on screen comes from the exported package (web/data) plus live crops rendered
 * from the two source PDFs by serve_atlas.py, so the printed picture and the digitised result
 * are always compared at the same coordinate. No external libraries.
 */
'use strict';

const $ = (s) => document.querySelector(s);
const canvas = $('#map');
const ctx = canvas.getContext('2d');

const COL = {
  metallic: '#b3122b', industrial: '#12518f', gemstone: '#6b2d8f', energy: '#1b1b1b',
  fault: '#c01018', road: '#2b2b2b', river: '#1f6fb4', state: '#6b6b6b', boundary: '#101010',
};
const RADIUS = { high: 4.3, medium: 3.5, low: 2.9 };

/* viewport size used by project(); swapped while rendering the loupe into an offscreen canvas */
let VP = { w: 1, h: 1 };
const W = () => VP.w;
const H = () => VP.h;

const state = {
  stats: null, points: [], vectors: null, units: null, images: {},
  mode: 'explore', base: 'minerals',
  filters: { conf: new Set(['high', 'medium', 'low']),
             cls: new Set(['metallic', 'industrial', 'gemstone', 'energy']) },
  layers: {
    units: { on: true, op: .55 }, boundary: { on: true, op: 1 },
    faults: { on: true, op: 1 }, roads: { on: false, op: .8 },
    rivers: { on: true, op: .8 }, states: { on: false, op: .8 },
    points: { on: true, op: 1 },
  },
  baseOpacity: 1, labels: false, sel: null, split: .5, outside: true,
  view: { lon: 8.75, lat: 9.0, scale: 60 },
  drag: null, hoverPos: null, unitsCanvas: null,
  crop: { key: null, img: null, loading: false },
};

/* ------------------------------------------------------------------ projection */
function project(lon, lat, view = state.view) {
  return [(lon - view.lon) * view.scale + W() / 2,
          (view.lat - lat) * view.scale + H() / 2];
}
function unproject(px, py, view = state.view) {
  return [view.lon + (px - W() / 2) / view.scale,
          view.lat - (py - H() / 2) / view.scale];
}
function fitBounds(b, pad = .93) {
  const [w, s, e, n] = b;
  state.view = { lon: (w + e) / 2, lat: (s + n) / 2,
                 scale: Math.min(W() / (e - w), H() / (n - s)) * pad };
}

/* ------------------------------------------------------------------ boot */
async function boot() {
  const j = (p) => fetch(p).then((r) => { if (!r.ok) throw new Error(p + ' ' + r.status); return r.json(); });
  const [stats, pts, vec, units] = await Promise.all([
    j('data/stats.json'), j('data/occurrences.json'),
    j('data/vectors.json'), j('data/units.json'),
  ]);
  state.stats = stats; state.points = pts; state.vectors = vec; state.units = units;

  for (const [key, file] of [['minerals', 'data/minerals_sheet.jpg'],
                             ['geology', 'data/geology_sheet.jpg']]) {
    const img = new Image();
    img.src = file;
    try { await img.decode(); } catch (e) { /* keep going; layer simply stays blank */ }
    state.images[key] = img;
  }

  buildChips();
  buildList();
  buildUnitsCanvas();
  resize();
  fitBounds(stats.bounds.minerals, .96);
  bindUI();
  draw();
}

function buildChips() {
  const s = state.stats, v = s.verify || {};
  $('#chips').innerHTML = [
    `<span class="chip"><b>${s.occurrences.toLocaleString()}</b> occurrences</span>`,
    `<span class="chip"><b>${s.names}</b> commodities</span>`,
    `<span class="chip">centre on symbol <b>${(s.audit && s.audit.median_offset_km) ?? v.distance_to_glyph_centre_km_median ?? '—'} km</b> median</span>`,
    `<span class="chip"><b>${s.checks}</b> checks pass</span>`,
    `<span class="chip"><b>${s.layers}</b> layers</span>`,
  ].join('');
  $('#factsTop').innerHTML = `
    <dt>Points</dt><dd>${s.occurrences.toLocaleString()}</dd>
    <dt>Distinct names</dt><dd>${s.names}</dd>
    <dt>Both readings identical</dt><dd>${s.identical}</dd>
    <dt>Same family</dt><dd>${s.same_family}</dd>
    <dt>Duplicate points merged</dt><dd>${s.merged}</dd>
    <dt>Geology units</dt><dd>${s.counts.units.toLocaleString()}</dd>
    <dt>Faults / roads / rivers</dt><dd>${s.counts.faults} / ${s.counts.roads} / ${s.counts.rivers ?? '—'}</dd>
    <dt>Centre audit</dt><dd>${s.audit && s.audit.median_offset_pt != null ? s.audit.median_offset_pt + ' pt · ' + s.audit.median_offset_km + ' km median' : '—'}</dd>
    <dt>Picks outside Nigeria</dt><dd>${s.outside} (shown as hollow diamonds)</dd>`;
}

/* pre-render the geology fills once, so panning stays smooth */
function buildUnitsCanvas() {
  const b = [2.35, 3.75, 15.15, 14.25];
  const w = 2600, h = Math.round(w * (b[3] - b[1]) / (b[2] - b[0]));
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const g = c.getContext('2d');
  const sx = w / (b[2] - b[0]), sy = h / (b[3] - b[1]);
  for (const u of state.units) {
    if (!u.in || !u.p || u.p.length < 3) continue;
    g.beginPath();
    u.p.forEach(([x, y], i) => {
      const px = (x - b[0]) * sx, py = (b[3] - y) * sy;
      if (i) g.lineTo(px, py); else g.moveTo(px, py);
    });
    g.closePath();
    g.fillStyle = u.c || '#dddddd';
    g.fill();
    g.strokeStyle = 'rgba(45,45,45,.42)';
    g.lineWidth = .9;
    g.stroke();
  }
  state.unitsCanvas = { canvas: c, bounds: b };
}

/* ------------------------------------------------------------------ scene pieces */
function drawBase(g, view) {
  if (state.base === 'none') return;
  const img = state.images[state.base];
  const b = state.stats.bounds[state.base];
  if (!img || !b) return;
  const [x0, y0] = project(b[0], b[3], view);
  const [x1, y1] = project(b[2], b[1], view);
  g.save();
  g.globalAlpha = state.baseOpacity;
  g.imageSmoothingEnabled = view.scale < 700;   // stay crisp when inspecting glyphs
  g.imageSmoothingQuality = 'high';
  g.drawImage(img, x0, y0, x1 - x0, y1 - y0);
  g.restore();
}

function drawUnits(g, view) {
  if (!state.layers.units.on || !state.unitsCanvas) return;
  const { canvas: c, bounds: b } = state.unitsCanvas;
  const [x0, y0] = project(b[0], b[3], view);
  const [x1, y1] = project(b[2], b[1], view);
  g.save();
  g.globalAlpha = state.layers.units.op;
  g.drawImage(c, x0, y0, x1 - x0, y1 - y0);
  g.restore();
}

function strokePaths(g, paths, view, colour, width, alpha, dash) {
  if (!paths || !paths.length) return;
  g.save();
  g.globalAlpha = alpha;
  g.strokeStyle = colour;
  g.lineWidth = width;
  g.lineJoin = 'round';
  g.lineCap = 'round';
  if (dash) g.setLineDash(dash);
  g.beginPath();
  for (const path of paths) {
    if (!path.length) continue;
    for (let i = 0; i < path.length; i++) {
      const [px, py] = project(path[i][0], path[i][1], view);
      if (i === 0) g.moveTo(px, py); else g.lineTo(px, py);
    }
  }
  g.stroke();
  g.restore();
}

function visiblePoints() {
  return state.points.filter((p) => state.filters.conf.has(p.c) && state.filters.cls.has(p.k) &&
    (state.outside || !p.out));
}

function drawPoints(g, view, pts, dim) {
  if (!state.layers.points.on) return;
  const list = pts || visiblePoints();
  g.save();
  g.globalAlpha = dim ? state.layers.points.op * .45 : state.layers.points.op;
  const shrink = view.scale > 140 ? 1 : .88;
  for (const p of list) {
    const [x, y] = project(p.lon, p.lat, view);
    if (x < -20 || y < -20 || x > W() + 20 || y > H() + 20) continue;
    const r = (RADIUS[p.c] || 3) * shrink;
    const sel = state.sel === p;
    if (p.out) {                                  // outside the border: hollow diamond
      const d = r + 1.6;
      g.beginPath();
      g.moveTo(x, y - d); g.lineTo(x + d, y); g.lineTo(x, y + d); g.lineTo(x - d, y); g.closePath();
      g.fillStyle = 'rgba(255,255,255,.85)';
      g.fill();
      g.lineWidth = sel ? 2.2 : 1.4;
      g.strokeStyle = sel ? '#ff00cc' : (COL[p.k] || '#555555');
      g.stroke();
      continue;
    }
    g.beginPath();
    g.arc(x, y, sel ? r + 2.4 : r, 0, Math.PI * 2);
    g.fillStyle = dim ? 'rgba(120,126,134,.55)' : (COL[p.k] || '#666666');
    g.fill();
    g.lineWidth = sel ? 2.2 : .9;
    g.strokeStyle = sel ? '#ff00cc' : 'rgba(255,255,255,.92)';
    g.stroke();
  }
  g.restore();
}

function drawLabels(g, view) {
  if (!state.labels || view.scale < 46) return;
  g.save();
  g.font = '600 10px -apple-system,Segoe UI,Roboto,sans-serif';
  g.textBaseline = 'middle';
  const seen = new Set();
  for (const p of visiblePoints()) {
    if (!p.n) continue;
    const [x, y] = project(p.lon, p.lat, view);
    if (x < 0 || y < 0 || x > W() || y > H()) continue;
    const name = String(p.n).replace(/ \(.*\)$/, '');
    const key = name + '|' + Math.round(x / 90) + ',' + Math.round(y / 26);
    if (seen.has(key)) continue;
    seen.add(key);
    const w = g.measureText(name).width;
    g.fillStyle = 'rgba(255,255,255,.84)';
    g.fillRect(x + 7, y - 7, w + 6, 13);
    g.fillStyle = '#1b2430';
    g.fillText(name, x + 10, y);
  }
  g.restore();
}

function renderScene(g, view, o) {
  if (o.base) drawBase(g, view);
  if (o.units) drawUnits(g, view);
  if (o.lines) {
    const L = state.layers, V = state.vectors;
    if (L.rivers.on) strokePaths(g, V.rivers, view, COL.river, 1, L.rivers.op);
    if (L.states.on) strokePaths(g, V.states, view, COL.state, 1, L.states.op, [4, 3]);
    if (L.roads.on) strokePaths(g, V.roads, view, COL.road, .9, L.roads.op);
    if (L.faults.on) strokePaths(g, V.faults, view, COL.fault, 2.1, L.faults.op);
    if (L.boundary.on) strokePaths(g, V.boundary, view, COL.boundary, 1.7, L.boundary.op);
  }
  if (o.points) drawPoints(g, view, o.pts, o.dim);
  if (o.labels) drawLabels(g, view);
}

/* ------------------------------------------------------------------ main draw */
let frame = 0;
function schedule() { if (!frame) frame = requestAnimationFrame(draw); }
function draw() {
  frame = 0;
  const dpr = window.devicePixelRatio || 1;
  VP = { w: canvas.clientWidth, h: canvas.clientHeight };
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#fbfcfd';
  ctx.fillRect(0, 0, W(), H());

  if (state.mode === 'compare') {
    drawCompare();
  } else {
    renderScene(ctx, state.view, { base: true, units: true, lines: true, points: true, labels: true });
    if (state.mode === 'verify') drawLiveLoupe();
  }
  updateReadout();
}

function drawCompare() {
  const split = Math.round(W() * state.split);
  ctx.save();
  ctx.beginPath(); ctx.rect(0, 0, split, H()); ctx.clip();
  ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, split, H());
  renderScene(ctx, state.view, { base: true, units: false, lines: false, points: false });
  ctx.restore();

  ctx.save();
  ctx.beginPath(); ctx.rect(split, 0, W() - split, H()); ctx.clip();
  ctx.fillStyle = '#f1f3f6'; ctx.fillRect(split, 0, W() - split, H());
  renderScene(ctx, state.view, { base: false, units: true, lines: true, points: true, labels: true });
  ctx.restore();

  ctx.save();
  ctx.strokeStyle = 'rgba(16,23,32,.9)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(split, 0); ctx.lineTo(split, H()); ctx.stroke();
  const my = H() / 2;
  ctx.fillStyle = '#101720';
  ctx.beginPath();
  if (ctx.roundRect) ctx.roundRect(split - 13, my - 26, 26, 52, 7);
  else ctx.rect(split - 13, my - 26, 26, 52);
  ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.font = '600 13px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('\u2194', split, my);
  ctx.textAlign = 'left';

  const tag = (x, text, colour) => {
    ctx.font = '600 11px sans-serif';
    const w = ctx.measureText(text).width + 16;
    ctx.fillStyle = 'rgba(255,255,255,.94)';
    ctx.fillRect(x, 10, w, 22);
    ctx.strokeStyle = 'rgba(16,23,32,.15)'; ctx.lineWidth = 1;
    ctx.strokeRect(x + .5, 10.5, w - 1, 21);
    ctx.fillStyle = colour;
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x + 8, 21.5);
  };
  tag(10, 'printed sheet', '#33404c');
  tag(split + 10, 'digitised result', '#0f5f7a');
  ctx.restore();
}

/* live crop from the PDF, drawn under the cursor */
function drawLiveLoupe() {
  if (!state.hoverPos) return;
  const { x, y } = state.hoverPos;
  const R = 96;
  const [lon, lat] = unproject(x, y);
  const key = lon.toFixed(4) + ',' + lat.toFixed(4);
  if (state.crop.key !== key && !state.crop.loading) {
    state.crop.key = key;
    state.crop.loading = true;
    const img = new Image();
    img.onload = () => { state.crop.img = img; state.crop.loading = false; schedule(); };
    img.onerror = () => { state.crop.loading = false; };
    img.src = `api/crop?lon=${lon}&lat=${lat}&r=14&zoom=6&src=${state.base === 'none' ? 'minerals' : state.base}`;
  }
  ctx.save();
  ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff'; ctx.fill();
  ctx.clip();
  if (state.crop.img && state.crop.img.complete) {
    const img = state.crop.img;
    const s = Math.max((R * 2) / img.width, (R * 2) / img.height);
    const w = img.width * s, h = img.height * s;
    ctx.drawImage(img, x - w / 2, y - h / 2, w, h);
  }
  ctx.restore();
  ctx.save();
  ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(16,23,32,.85)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.beginPath(); ctx.arc(x, y, 2.4, 0, Math.PI * 2);
  ctx.fillStyle = '#ff00cc'; ctx.fill();
  ctx.font = '600 10px sans-serif'; ctx.textBaseline = 'middle';
  const cap = `live crop  ${lon.toFixed(3)}°E ${lat.toFixed(3)}°N`;
  const cw = ctx.measureText(cap).width + 12;
  ctx.fillStyle = 'rgba(255,255,255,.94)';
  ctx.fillRect(x - cw / 2, y + R + 6, cw, 17);
  ctx.fillStyle = '#33404c';
  ctx.fillText(cap, x - cw / 2 + 6, y + R + 15);
  ctx.restore();
}

/* ------------------------------------------------------------------ chrome */
function updateReadout() {
  const { lon, lat, scale } = state.view;
  const kmPerDeg = 111.32 * Math.cos(lat * Math.PI / 180);
  const barKm = niceKm(120 / scale * kmPerDeg);
  $('#scalebar').style.width = Math.max(30, barKm / kmPerDeg * scale).toFixed(0) + 'px';
  $('#scaletext').textContent = barKm + ' km';
  $('#readout').textContent = `${lat.toFixed(3)}°N  ${lon.toFixed(3)}°E  ·  ${(scale / 60).toFixed(1)}×`;
  $('#zoomBadge').hidden = false;
  $('#zoomBadge').textContent =
    `${(scale / 60).toFixed(1)}×  ·  ${visiblePoints().length.toLocaleString()} of ${state.points.length.toLocaleString()} points`;
}
function niceKm(x) {
  const steps = [5, 10, 20, 50, 100, 200, 300, 500, 1000];
  return steps.reduce((a, b) => (Math.abs(b - x) < Math.abs(a - x) ? b : a));
}

function resize() {
  const dpr = window.devicePixelRatio || 1;
  VP = { w: canvas.clientWidth, h: canvas.clientHeight };   // keep project() in sync before first draw
  canvas.width = Math.max(1, Math.round(VP.w * dpr));
  canvas.height = Math.max(1, Math.round(VP.h * dpr));
  schedule();
}

function nearestPoint(px, py, tol = 9) {
  let best = null, bd = tol;
  for (const p of visiblePoints()) {
    const [x, y] = project(p.lon, p.lat);
    const d = Math.hypot(x - px, y - py);
    if (d < bd) { bd = d; best = p; }
  }
  return best;
}

/* ------------------------------------------------------------------ interaction */
function bindUI() {
  window.addEventListener('resize', resize);

  document.querySelectorAll('.modes button').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('.modes button').forEach((x) => x.classList.remove('on'));
    b.classList.add('on');
    state.mode = b.dataset.mode;
    $('#compareHint').hidden = state.mode !== 'compare';
    schedule();
  }));

  $('#base').addEventListener('change', (e) => {
    state.base = e.target.value;
    state.crop.key = null;
    // the printed sheet already carries the geology, so the re-plot starts hidden on it
    setUnits(state.base !== 'minerals');
    schedule();
  });
  $('#lyr-outside').addEventListener('change', (e) => {
    state.outside = e.target.checked; buildList(); schedule();
  });
  $('#baseOpacity').addEventListener('input', (e) => {
    state.baseOpacity = e.target.value / 100;
    $('#baseOpacityOut').textContent = e.target.value + '%';
    schedule();
  });

  for (const name of Object.keys(state.layers)) {
    const cb = $('#lyr-' + name), op = $('#op-' + name);
    if (cb) cb.addEventListener('change', () => { state.layers[name].on = cb.checked; schedule(); });
    if (op) op.addEventListener('input', () => { state.layers[name].op = op.value / 100; schedule(); });
  }

  document.querySelectorAll('.conf').forEach((c) => c.addEventListener('change', () => {
    if (c.checked) state.filters.conf.add(c.value); else state.filters.conf.delete(c.value);
    buildList(); schedule();
  }));
  document.querySelectorAll('.cls').forEach((c) => c.addEventListener('change', () => {
    if (c.checked) state.filters.cls.add(c.value); else state.filters.cls.delete(c.value);
    buildList(); schedule();
  }));

  $('#search').addEventListener('input', buildList);
  $('#fit').addEventListener('click', () => { fitBounds(state.stats.bounds.minerals, .96); schedule(); });
  $('#zin').addEventListener('click', () => zoomAt(1.45));
  $('#zout').addEventListener('click', () => zoomAt(1 / 1.45));
  $('#toggleLabels').addEventListener('click', (e) => {
    state.labels = !state.labels;
    e.currentTarget.classList.toggle('on', state.labels);
    schedule();
  });
  $('#zoomTo').addEventListener('click', () => { if (state.sel) focusPoint(state.sel); });
  $('#findConflicts').addEventListener('click', () => {
    const list = visiblePoints().filter((p) => p.c === 'low');
    if (!list.length) return;
    const i = state.sel ? list.indexOf(state.sel) : -1;
    select(list[(i + 1) % list.length], true);
  });

  canvas.addEventListener('mousedown', (e) => {
    const r = canvas.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    if (state.mode === 'compare' && Math.abs(px - W() * state.split) < 14) {
      state.drag = { type: 'split' };
    } else {
      state.drag = { type: 'pan', px, py, lon: state.view.lon, lat: state.view.lat, moved: false };
    }
    canvas.classList.add('dragging');
  });

  window.addEventListener('mousemove', (e) => {
    const r = canvas.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    state.hoverPos = { x: px, y: py };

    if (state.drag) {
      if (state.drag.type === 'split') {
        state.split = Math.min(.94, Math.max(.06, px / W()));
      } else {
        const dx = px - state.drag.px, dy = py - state.drag.py;
        if (Math.hypot(dx, dy) > 3) state.drag.moved = true;
        state.view.lon = state.drag.lon - dx / state.view.scale;
        state.view.lat = state.drag.lat + dy / state.view.scale;
      }
      schedule();
      return;
    }

    const p = nearestPoint(px, py);
    const tip = $('#hover');
    if (p) {
      tip.hidden = false;
      tip.style.left = Math.min(px + 14, W() - 250) + 'px';
      tip.style.top = (py + 14) + 'px';
      tip.innerHTML = `<b>${p.n || 'unidentified'}</b><br>${p.k} · name confidence ${p.c}` +
        (p.a ? `<br><span style="opacity:.72">other reading: ${p.a}</span>` : '');
    } else {
      tip.hidden = true;
    }
    if (state.mode === 'verify') {
      if (p && p !== state.sel) select(p);
      schedule();
    }
  });

  window.addEventListener('mouseup', (e) => {
    const click = state.drag && state.drag.type === 'pan' && !state.drag.moved;
    state.drag = null;
    canvas.classList.remove('dragging');
    if (click) {
      const r = canvas.getBoundingClientRect();
      const p = nearestPoint(e.clientX - r.left, e.clientY - r.top);
      if (p) select(p);
    }
  });

  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const r = canvas.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    const [lon, lat] = unproject(px, py);
    state.view.scale = Math.min(4000, Math.max(16, state.view.scale * Math.exp(-e.deltaY * 0.0016)));
    const [nx, ny] = unproject(px, py);
    state.view.lon += lon - nx;
    state.view.lat += lat - ny;
    schedule();
  }, { passive: false });

  canvas.addEventListener('dblclick', (e) => {
    const r = canvas.getBoundingClientRect();
    const [lon, lat] = unproject(e.clientX - r.left, e.clientY - r.top);
    state.view.lon = lon; state.view.lat = lat;
    state.view.scale = Math.min(4000, state.view.scale * 1.9);
    schedule();
  });
}

function setUnits(on) {
  const cb = $('#lyr-units');
  state.layers.units.on = on;
  if (cb) cb.checked = on;
}

function zoomAt(k) { state.view.scale = Math.min(4000, Math.max(16, state.view.scale * k)); schedule(); }
function focusPoint(p) {
  state.view.lon = p.lon; state.view.lat = p.lat;
  state.view.scale = Math.max(state.view.scale, 1100);
  schedule();
}

/* ------------------------------------------------------------------ selection */
function select(p, focus) {
  state.sel = p;
  if (focus) focusPoint(p);
  $('#emptyState').hidden = true;
  $('#detail').hidden = false;
  $('#d-name').textContent = p.n || 'Unidentified symbol';
  $('#d-alt').textContent = p.a ? `other reading: ${p.a}` : 'both independent readings agree';
  $('#d-badges').innerHTML =
    `<span class="badge ${p.c}">${p.c} confidence</span>` +
    `<span class="badge">${p.k}</span>` +
    (p.src > 1 ? `<span class="badge">merged ${p.src} points</span>` : '');
  $('#d-facts').innerHTML = `
    <dt>Longitude</dt><dd>${p.lon.toFixed(5)}°E</dd>
    <dt>Latitude</dt><dd>${p.lat.toFixed(5)}°N</dd>
    <dt>Name source</dt><dd>${p.s || '—'}</dd>
    <dt>Legend symbol</dt><dd>${p.ls || '—'}</dd>
    <dt>Matcher margin</dt><dd>${typeof p.m === 'number' ? p.m.toFixed(3) : '—'}</dd>`;
  const img = $('#crop');
  img.onerror = () => { img.alt = 'live crop unavailable'; };
  img.src = `api/crop?lon=${p.lon}&lat=${p.lat}&r=15&zoom=9&src=minerals`;
  markListSelection();
  schedule();
}

/* ------------------------------------------------------------------ result list */
function buildList() {
  const q = ($('#search').value || '').toLowerCase().trim();
  const rows = visiblePoints().filter((p) => !q ||
    String(p.n || '').toLowerCase().includes(q) ||
    String(p.a || '').toLowerCase().includes(q));
  rows.sort((a, b) => String(a.n || 'zzz').localeCompare(String(b.n || 'zzz')));
  const shown = rows.slice(0, 400);
  $('#list').innerHTML = shown.map((p) => `
    <div class="item" data-i="${state.points.indexOf(p)}">
      <span class="nm">${p.n || 'unidentified'}<small>${p.k}</small></span>
      <span class="tag ${p.c}">${p.c}</span>
    </div>`).join('');
  $('#list').querySelectorAll('.item').forEach((el) => {
    el.addEventListener('click', () => select(state.points[+el.dataset.i], true));
  });
  $('#visibleCount').textContent =
    `${rows.length.toLocaleString()} of ${state.points.length.toLocaleString()} occurrences shown` +
    (rows.length > shown.length ? ` · first ${shown.length} listed` : '');
  markListSelection();
}
function markListSelection() {
  $('#list').querySelectorAll('.item').forEach((el) => {
    el.classList.toggle('sel', Boolean(state.sel) && state.points[+el.dataset.i] === state.sel);
  });
}

boot().catch((err) => {
  document.body.insertAdjacentHTML('afterbegin',
    `<pre style="margin:0;padding:12px;background:#3a1212;color:#ffd7d7;font-size:12px">viewer failed to start: ${err}</pre>`);
});
