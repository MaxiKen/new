/* Nigeria geology & minerals — live comparison viewer
 *
 * Left panel and inspector collapse into drawers on a phone; the canvas takes the whole screen.
 * Compare mode splits the screen: the printed sheet on the left of the divider, the re-plotted
 * unit polygons on the right, both locked to the same view, and the divider is dragged either way.
 * Zoom goes to 1500% of the country view, fast, with one-finger pan and two-finger pinch.
 */
'use strict';

const $ = (s) => document.querySelector(s);
const canvas = $('#map');
const ctx = canvas.getContext('2d');

const COL = {
  metallic: '#b3122b', industrial: '#12518f', gemstone: '#6b2d8f', energy: '#1b1b1b',
  fault: '#c01018', road: '#2b2b2b', river: '#1f6fb4', state: '#6b6b6b', boundary: '#101010',
};
const RADIUS = { high: 4.2, medium: 3.4, low: 2.8 };

// Zoom is quoted as a level: 100 = the whole country on screen, 1500 = the deepest zoom.
// The deepest zoom is far more than 15x the country view, because symbol-level comparison needs
// roughly 20-40 km across the screen, not 130 km.
const ZOOM_MIN_REL = 0.85;
const ZOOM_DEEP_PX_PER_DEG = 4200;   // about 26 m per screen pixel on a 1280 px viewport
const ZOOM_DEEP_FACTOR = 60;         // ...and never less than 60x the fitted view
const LEVEL_FIT = 100, LEVEL_MAX = 1500;

let VP = { w: 1, h: 1 };
const W = () => VP.w;
const H = () => VP.h;

const state = {
  stats: null, points: [], vectors: null, units: null, images: {},
  mode: 'explore', base: 'minerals',
  filters: { conf: new Set(['high', 'medium', 'low']),
             cls: new Set(['metallic', 'industrial', 'gemstone', 'energy']) },
  layers: {
    units: { on: false, op: .55 }, boundary: { on: true, op: 1 },
    faults: { on: true, op: 1 }, roads: { on: false, op: .8 },
    rivers: { on: true, op: .8 }, states: { on: false, op: .8 },
    points: { on: true, op: 1 },
  },
  baseOpacity: 1, labels: false, sel: null, split: .5, outside: true,
  view: { lon: 8.75, lat: 9.0, scale: 60 }, fitScale: 60,
  pointers: new Map(), drag: null, tap: null, hover: null,
  unitsCanvas: null, crop: { key: null, img: null, loading: false },
  sharp: { key: null, img: null, pending: false, timer: 0 },
};

const isPhone = () => window.matchMedia('(max-width: 900px)').matches;

/* ------------------------------------------------------------------ projection */
function project(lon, lat, view = state.view) {
  return [(lon - view.lon) * view.scale + W() / 2,
          (view.lat - lat) * view.scale + H() / 2];
}
function unproject(px, py, view = state.view) {
  return [view.lon + (px - W() / 2) / view.scale,
          view.lat - (py - H() / 2) / view.scale];
}
function boundsOf(key) {
  return key === 'geology' ? state.stats.bounds.geology : state.stats.bounds.minerals;
}
function computeFit() {
  const b = boundsOf(state.base === 'geology' ? 'geology' : 'minerals');
  const pad = isPhone() ? .96 : .93;
  return Math.min(W() / (b[2] - b[0]), H() / (b[3] - b[1])) * pad;
}
function fitToNigeria() {
  const b = boundsOf(state.base === 'geology' ? 'geology' : 'minerals');
  state.fitScale = computeFit();
  state.view = { lon: (b[0] + b[2]) / 2, lat: (b[1] + b[3]) / 2, scale: state.fitScale };
}
function zoomLimits() {
  const f = state.fitScale || 60;
  return [Math.max(8, f * ZOOM_MIN_REL), Math.max(ZOOM_DEEP_PX_PER_DEG, f * ZOOM_DEEP_FACTOR)];
}
function zoomLevel(scale) {
  const f = state.fitScale || 60;
  const hi = zoomLimits()[1];
  if (scale <= f) return Math.round(LEVEL_FIT * Math.max(.2, scale / f));
  const t = Math.log(scale / f) / Math.log(hi / f);          // 0 at fit, 1 at the deepest zoom
  return Math.round(LEVEL_FIT + (LEVEL_MAX - LEVEL_FIT) * Math.min(1, t));
}
function scaleForLevel(level) {
  const f = state.fitScale || 60;
  const hi = zoomLimits()[1];
  if (level <= LEVEL_FIT) return f * Math.max(.2, level / LEVEL_FIT);
  const t = Math.min(1, (level - LEVEL_FIT) / (LEVEL_MAX - LEVEL_FIT));
  return f * Math.pow(hi / f, t);
}
function clampZoom() {
  const [lo, hi] = zoomLimits();
  state.view.scale = Math.min(hi, Math.max(lo, state.view.scale));
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
    try { await img.decode(); } catch (e) { /* layer stays blank rather than breaking the page */ }
    state.images[key] = img;
  }

  buildChips();
  buildList();
  prepareUnits();
  buildUnitsCanvas();
  resize();
  fitToNigeria();
  bindUI();
  syncZoomUI();
  draw();
}

function buildChips() {
  const s = state.stats, v = s.verify || {};
  $('#chips').innerHTML = [
    `<span class="chip"><b>${s.occurrences.toLocaleString()}</b> occurrences</span>`,
    `<span class="chip"><b>${s.names}</b> commodities</span>`,
    `<span class="chip">centre on symbol <b>${(s.audit && s.audit.median_offset_km) ?? v.distance_to_glyph_centre_km_median ?? '—'} km</b></span>`,
    `<span class="chip"><b>${s.checks}</b> checks pass</span>`,
    `<span class="chip"><b>${s.counts.units.toLocaleString()}</b> unit polygons</span>`,
  ].join('');
  $('#factsTop').innerHTML = `
    <dt>Points</dt><dd>${s.occurrences.toLocaleString()}</dd>
    <dt>Distinct names</dt><dd>${s.names}</dd>
    <dt>Both readings identical</dt><dd>${s.identical}</dd>
    <dt>Duplicate points merged</dt><dd>${s.merged}</dd>
    <dt>Geology units</dt><dd>${s.counts.units.toLocaleString()}</dd>
    <dt>Centre audit</dt><dd>${s.audit ? s.audit.median_offset_pt + ' pt · ' + s.audit.median_offset_km + ' km median' : '—'}</dd>
    <dt>Picks outside Nigeria</dt><dd>${s.outside}</dd>`;
}

/* geology fills are pre-rendered once, so panning and pinching stay smooth */
function prepareUnits() {
  for (const u of state.units) {
    if (!u.p || u.p.length < 3) continue;
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const [x, y] of u.p) {
      if (x < x0) x0 = x; if (x > x1) x1 = x;
      if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
    u.b = [x0, y0, x1, y1];
  }
}

function buildUnitsCanvas() {
  const b = [2.35, 3.75, 15.15, 14.25];
  const w = 3000, h = Math.round(w * (b[3] - b[1]) / (b[2] - b[0]));
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
    g.strokeStyle = 'rgba(45,45,45,.45)';
    g.lineWidth = 1;
    g.stroke();
  }
  state.unitsCanvas = { canvas: c, bounds: b };
}

/* ------------------------------------------------------------------ scene pieces */
const SHARP_FROM_LEVEL = 320;      // above this the baked JPG runs out of detail

/* Beyond the baked resolution, ask the server for a fresh render of exactly this window, from the
   PDF, at screen resolution. Until it arrives the JPG is drawn, so panning never stalls. */
function sharpWindow(view) {
  const [lon0, lat1] = unproject(0, 0, view);
  const [lon1, lat0] = unproject(W(), H(), view);
  return { lon0, lat0, lon1, lat1 };
}
function requestSharp(view) {
  const src = state.base === 'none' ? 'geology' : state.base;
  const b = sharpWindow(view);
  const w = Math.min(2400, Math.max(64, Math.round(W() * Math.min(2, window.devicePixelRatio || 1))));
  const h = Math.min(2400, Math.max(64, Math.round(H() * Math.min(2, window.devicePixelRatio || 1))));
  const key = [src, b.lon0.toFixed(5), b.lat0.toFixed(5), b.lon1.toFixed(5), b.lat1.toFixed(5), w, h].join('|');
  if (state.sharp.key === key || state.sharp.pending) return;
  clearTimeout(state.sharp.timer);
  state.sharp.timer = setTimeout(() => {
    state.sharp.pending = true;
    const img = new Image();
    img.onload = () => {
      state.sharp = { key, img, win: b, pending: false, timer: 0 };
      schedule();
    };
    img.onerror = () => { state.sharp.pending = false; schedule(); };
    img.src = `api/view?src=${src}&lon0=${b.lon0}&lat0=${b.lat0}&lon1=${b.lon1}&lat1=${b.lat1}&w=${w}&h=${h}`;
  }, 140);
}

function drawBase(g, view) {
  if (state.base === 'none') return;
  const b = boundsOf(state.base);

  // deep zoom: use the freshly rendered window (it is placed by its own corners, so it stays in
  // register while panning) and refresh it as the view moves
  if (zoomLevel(view.scale) >= SHARP_FROM_LEVEL) {
    requestSharp(view);
    const sh = state.sharp;
    if (sh.img && sh.win && sh.img.complete) {
      const [sx0, sy0] = project(sh.win.lon0, sh.win.lat1, view);
      const [sx1, sy1] = project(sh.win.lon1, sh.win.lat0, view);
      g.save();
      g.globalAlpha = state.baseOpacity;
      g.imageSmoothingEnabled = true;
      g.imageSmoothingQuality = 'high';
      g.drawImage(sh.img, sx0, sy0, sx1 - sx0, sy1 - sy0);
      g.restore();
      return;
    }
  }

  const img = state.images[state.base];
  if (!img || !b) return;
  const [x0, y0] = project(b[0], b[3], view);
  const [x1, y1] = project(b[2], b[1], view);
  const nativePxPerDeg = (state.base === 'geology' ? 4709 : 6725) / (b[2] - b[0]);
  g.save();
  g.globalAlpha = state.baseOpacity;
  g.imageSmoothingEnabled = view.scale < nativePxPerDeg * 1.6;   // stay crisp past native detail
  g.imageSmoothingQuality = 'high';
  g.drawImage(img, x0, y0, x1 - x0, y1 - y0);
  g.restore();
}

/* At close range the polygons are drawn as real vector paths, so boundaries stay sharp for
   micro comparison instead of showing the pixel grid of the pre-rendered fill. */
function drawUnitsVector(g, view) {
  const [vx0, vy1] = unproject(0, 0, view);
  const [vx1, vy0] = unproject(W(), H(), view);
  const lw = Math.max(.35, Math.min(1.2, view.scale / 900));
  const onScreen = [];
  for (const u of state.units) {
    if (!u.in || !u.b) continue;
    const b = u.b;
    if (b[2] < vx0 || b[0] > vx1 || b[3] < vy0 || b[1] > vy1) continue;
    onScreen.push(u);
  }
  // big units first, small ones last: a small unit that touches a large one must never be
  // painted over, and in a partition it can only be hidden by a rounding overlap
  onScreen.sort((a, b) => (b.b[2] - b.b[0]) * (b.b[3] - b.b[1]) - (a.b[2] - a.b[0]) * (a.b[3] - a.b[1]));
  g.save();
  g.globalAlpha = state.layers.units.op;

  // pass 1: fills
  const paths = [];
  for (const u of onScreen) {
    g.beginPath();
    const p = u.p;
    for (let i = 0; i < p.length; i++) {
      const x = (p[i][0] - view.lon) * view.scale + W() / 2;
      const y = (view.lat - p[i][1]) * view.scale + H() / 2;
      if (i === 0) g.moveTo(x, y); else g.lineTo(x, y);
    }
    g.closePath();
    paths.push(g);
    g.fillStyle = u.c || '#dddddd';
    g.fill();
  }

  // pass 2: a thick stroke in each polygon's own colour, on top of every fill. Neighbouring
  // polygons are simplified separately, so their shared edge can differ by a fraction of a
  // pixel; this closes that hairline instead of leaving a white seam.
  for (const u of onScreen) {
    g.beginPath();
    const p = u.p;
    for (let i = 0; i < p.length; i++) {
      const x = (p[i][0] - view.lon) * view.scale + W() / 2;
      const y = (view.lat - p[i][1]) * view.scale + H() / 2;
      if (i === 0) g.moveTo(x, y); else g.lineTo(x, y);
    }
    g.closePath();
    g.strokeStyle = u.c || '#dddddd';
    g.lineWidth = 3;
    g.lineJoin = 'round';
    g.stroke();
  }

  // pass 3: the thin unit outline, so boundaries stay readable
  g.globalAlpha = state.layers.units.op * .9;
  g.strokeStyle = 'rgba(40,40,40,.45)';
  g.lineWidth = lw;
  g.beginPath();
  for (const u of onScreen) {
    const p = u.p;
    for (let i = 0; i < p.length; i++) {
      const x = (p[i][0] - view.lon) * view.scale + W() / 2;
      const y = (view.lat - p[i][1]) * view.scale + H() / 2;
      if (i === 0) g.moveTo(x, y); else g.lineTo(x, y);
    }
    g.closePath();
  }
  g.stroke();
  g.restore();
  return onScreen.length;
}

function drawUnits(g, view) {
  if (!state.layers.units.on) return;
  if (zoomLevel(view.scale) >= 200) { drawUnitsVector(g, view); return; }
  if (!state.unitsCanvas) return;
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

function drawLines(g, view) {
  const L = state.layers, V = state.vectors;
  if (!V) return;
  if (L.rivers.on) strokePaths(g, V.rivers, view, COL.river, 1, L.rivers.op);
  if (L.states.on) strokePaths(g, V.states, view, COL.state, 1, L.states.op, [4, 3]);
  if (L.roads.on) strokePaths(g, V.roads, view, COL.road, .9, L.roads.op);
  if (L.faults.on) strokePaths(g, V.faults, view, COL.fault, 2.1, L.faults.op);
  if (L.boundary.on) strokePaths(g, V.boundary, view, COL.boundary, 1.7, L.boundary.op);
}

function visiblePoints() {
  return state.points.filter((p) => state.filters.conf.has(p.c) && state.filters.cls.has(p.k) &&
    (state.outside || !p.out));
}

function drawPoints(g, view) {
  if (!state.layers.points.on) return;
  const list = visiblePoints();
  const dim = view.scale < state.fitScale * 1.4;
  g.save();
  g.globalAlpha = state.layers.points.op;
  for (const p of list) {
    const [x, y] = project(p.lon, p.lat, view);
    if (x < -20 || y < -20 || x > W() + 20 || y > H() + 20) continue;
    const r = RADIUS[p.c] || 3;
    const sel = state.sel === p;
    if (p.out) {                                   // outside the border: hollow diamond
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
    g.arc(x, y, sel ? r + 2.4 : r * (dim ? .82 : 1), 0, Math.PI * 2);
    g.fillStyle = COL[p.k] || '#666666';
    g.fill();
    g.lineWidth = sel ? 2.2 : .9;
    g.strokeStyle = sel ? '#ff00cc' : 'rgba(255,255,255,.92)';
    g.stroke();
  }
  g.restore();
}

function drawLabels(g, view) {
  if (!state.labels || view.scale < state.fitScale * 1.3) return;
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
    g.fillStyle = 'rgba(255,255,255,.86)';
    g.fillRect(x + 7, y - 7, w + 6, 13);
    g.fillStyle = '#1b2430';
    g.fillText(name, x + 10, y);
  }
  g.restore();
}

function renderScene(g, view, o) {
  if (o.base) drawBase(g, view);
  if (o.units) drawUnits(g, view);
  if (o.lines) drawLines(g, view);
  if (o.points) drawPoints(g, view);
  if (o.labels) drawLabels(g, view);
}

/* ------------------------------------------------------------------ drawing */
let frame = 0;
function schedule() { if (!frame) frame = requestAnimationFrame(draw); }
function draw() {
  frame = 0;
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  VP = { w: canvas.clientWidth, h: canvas.clientHeight };
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#fbfcfd';
  ctx.fillRect(0, 0, W(), H());

  if (state.mode === 'compare') drawCompare();
  else {
    renderScene(ctx, state.view, { base: true, units: true, lines: true, points: true, labels: true });
    if (state.mode === 'verify') drawLoupe();
  }
  updateReadout();
}

function drawCompare() {
  const split = Math.round(W() * state.split);

  // left: the printed sheet
  ctx.save();
  ctx.beginPath(); ctx.rect(0, 0, split, H()); ctx.clip();
  ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, split, H());
  renderScene(ctx, state.view, { base: true, units: false, lines: false, points: false });
  ctx.restore();

  // right: the re-plotted unit polygons
  ctx.save();
  ctx.beginPath(); ctx.rect(split, 0, W() - split, H()); ctx.clip();
  ctx.fillStyle = '#f4f6f8'; ctx.fillRect(split, 0, W() - split, H());
  renderScene(ctx, state.view, { base: false, units: true, lines: true, points: true, labels: true });
  ctx.restore();

  // divider you can drag either way
  ctx.save();
  ctx.strokeStyle = 'rgba(16,23,32,.9)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(split, 0); ctx.lineTo(split, H()); ctx.stroke();
  const my = H() / 2, hw = 15, hh = 34;
  ctx.fillStyle = '#101720';
  ctx.beginPath();
  if (ctx.roundRect) ctx.roundRect(split - hw, my - hh, hw * 2, hh * 2, 9);
  else ctx.rect(split - hw, my - hh, hw * 2, hh * 2);
  ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.font = '600 15px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('\u2194', split, my);
  ctx.textAlign = 'left';

  const tag = (x, text, colour) => {
    ctx.font = '600 11px sans-serif';
    const w = ctx.measureText(text).width + 16;
    ctx.fillStyle = 'rgba(255,255,255,.94)';
    ctx.fillRect(x, 8, w, 22);
    ctx.strokeStyle = 'rgba(16,23,32,.16)'; ctx.lineWidth = 1;
    ctx.strokeRect(x + .5, 8.5, w - 1, 21);
    ctx.fillStyle = colour;
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x + 8, 19.5);
  };
  tag(8, 'geology sheet', '#8a5410');
  tag(Math.min(split + 8, W() - 130), 'unit polygons', '#0f5f7a');
  ctx.restore();
}

/* a live crop straight from the PDF, for judging symbol centring */
function drawLoupe() {
  let anchor = state.hover || (state.sel ? (() => {
    const [x, y] = project(state.sel.lon, state.sel.lat);
    return { x, y };
  })() : null);
  if (!anchor) return;
  const { x, y } = anchor;
  const R = isPhone() ? 78 : 96;
  const [lon, lat] = unproject(x, y);
  const key = lon.toFixed(4) + ',' + lat.toFixed(4);
  if (state.crop.key !== key && !state.crop.loading) {
    state.crop.key = key;
    state.crop.loading = true;
    const img = new Image();
    img.onload = () => { state.crop.img = img; state.crop.loading = false; schedule(); };
    img.onerror = () => { state.crop.loading = false; };
    const src = state.base === 'none' ? 'minerals' : state.base;
    img.src = `api/crop?lon=${lon}&lat=${lat}&r=14&zoom=6&src=${src}`;
  }
  ctx.save();
  ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff'; ctx.fill();
  ctx.clip();
  const img = state.crop.img;
  if (img && img.complete && img.width) {
    const s = Math.max((R * 2) / img.width, (R * 2) / img.height);
    ctx.drawImage(img, x - img.width * s / 2, y - img.height * s / 2, img.width * s, img.height * s);
  }
  ctx.restore();
  ctx.save();
  ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(16,23,32,.85)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.beginPath(); ctx.arc(x, y, 2.4, 0, Math.PI * 2);
  ctx.fillStyle = '#ff00cc'; ctx.fill();
  ctx.restore();
}

/* ------------------------------------------------------------------ chrome */
function updateReadout() {
  const { lon, lat, scale } = state.view;
  const kmPerDeg = 111.32 * Math.cos(lat * Math.PI / 180);
  const barKm = niceKm(110 / scale * kmPerDeg);
  $('#scalebar').style.width = Math.max(28, barKm / kmPerDeg * scale).toFixed(0) + 'px';
  $('#scaletext').textContent = barKm + ' km';
  syncZoomUI();
}
function syncZoomUI() {
  const lvl = zoomLevel(state.view.scale);
  const txt = $('#zoomPct');
  if (txt) { txt.textContent = String(lvl); txt.title = 'zoom level, 100 = whole country, 1500 = deepest'; }
  const sl = $('#zoomSlider');
  if (sl && document.activeElement !== sl) {
    const t = Math.max(0, Math.min(1, (lvl - LEVEL_FIT) / (LEVEL_MAX - LEVEL_FIT)));
    sl.value = String(Math.round(t * 1000));
  }
}
function niceKm(x) {
  const steps = [3, 5, 10, 20, 50, 100, 200, 300, 500, 1000];
  return steps.reduce((a, b) => (Math.abs(b - x) < Math.abs(a - x) ? b : a));
}

function resize() {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  VP = { w: canvas.clientWidth, h: canvas.clientHeight };
  canvas.width = Math.max(1, Math.round(VP.w * dpr));
  canvas.height = Math.max(1, Math.round(VP.h * dpr));
  const before = state.fitScale;
  state.fitScale = computeFit();
  if (before) state.view.scale *= state.fitScale / before;   // keep the apparent zoom
  clampZoom();
  schedule();
}

function nearestPoint(px, py, tol) {
  const t = tol || (isPhone() ? 16 : 10);
  let best = null, bd = t;
  for (const p of visiblePoints()) {
    const [x, y] = project(p.lon, p.lat);
    const d = Math.hypot(x - px, y - py);
    if (d < bd) { bd = d; best = p; }
  }
  return best;
}

function setZoomAround(scale, px, py) {
  const [lon, lat] = unproject(px, py);
  state.view.scale = scale;
  clampZoom();
  const [nx, ny] = unproject(px, py);
  state.view.lon += lon - nx;
  state.view.lat += lat - ny;
  schedule();
}

/* ------------------------------------------------------------------ interaction */
function bindUI() {
  window.addEventListener('resize', resize);
  window.addEventListener('orientationchange', () => setTimeout(resize, 250));

  document.querySelectorAll('.modes button').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('.modes button').forEach((x) => x.classList.remove('on'));
    b.classList.add('on');
    setMode(b.dataset.mode);
  }));

  // drawers, phone only
  const openPanel = (on) => document.body.classList.toggle('panel-open', on);
  $('#openPanel').addEventListener('click', () => openPanel(!document.body.classList.contains('panel-open')));
  $('#closePanel').addEventListener('click', () => openPanel(false));
  $('#scrim').addEventListener('click', () => openPanel(false));
  $('#closeInspector').addEventListener('click', () => {
    document.body.classList.remove('inspector-open');
    state.sel = null;
    $('#detail').hidden = true;
    $('#emptyState').hidden = false;
    schedule();
  });

  $('#base').addEventListener('change', (e) => {
    state.base = e.target.value;
    state.crop.key = null;
    state.fitScale = computeFit();
    setUnits(state.base !== 'minerals');
    schedule();
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
  $('#lyr-outside').addEventListener('change', (e) => {
    state.outside = e.target.checked; buildList(); schedule();
  });

  document.querySelectorAll('.conf').forEach((c) => c.addEventListener('change', () => {
    if (c.checked) state.filters.conf.add(c.value); else state.filters.conf.delete(c.value);
    buildList(); schedule();
  }));
  document.querySelectorAll('.cls').forEach((c) => c.addEventListener('change', () => {
    if (c.checked) state.filters.cls.add(c.value); else state.filters.cls.delete(c.value);
    buildList(); schedule();
  }));
  $('#search').addEventListener('input', buildList);

  $('#fit').addEventListener('click', () => { fitToNigeria(); syncZoomUI(); schedule(); });
  $('#zin').addEventListener('click', () => setZoomAround(state.view.scale * 1.8, W() / 2, H() / 2));
  $('#zout').addEventListener('click', () => setZoomAround(state.view.scale / 1.8, W() / 2, H() / 2));
  $('#zoomSlider').addEventListener('input', (e) => {
    const lvl = LEVEL_FIT + (LEVEL_MAX - LEVEL_FIT) * Number(e.target.value) / 1000;
    setZoomAround(scaleForLevel(lvl), W() / 2, H() / 2);
  });
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

  bindCanvas();
}

function setMode(mode) {
  state.mode = mode;
  $('#compareHint').hidden = mode !== 'compare';
  if (mode === 'compare') {
    // the comparison the user asked for: printed geology on the left, polygons on the right
    state.base = 'geology';
    $('#base').value = 'geology';
    setUnits(true);
    state.crop.key = null;
    state.fitScale = computeFit();
  }
  schedule();
}

function setUnits(on) {
  const cb = $('#lyr-units');
  state.layers.units.on = on;
  if (cb) cb.checked = on;
}

/* pointer events cover mouse, pen and touch in one path */
function bindCanvas() {
  const pos = (e) => {
    const r = canvas.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };
  const splitX = () => W() * state.split;
  const grabWidth = () => (isPhone() ? 30 : 18);

  canvas.addEventListener('pointerdown', (e) => {
    canvas.setPointerCapture(e.pointerId);
    const p = pos(e);
    state.pointers.set(e.pointerId, p);
    state.hover = p;
    if (state.pointers.size === 2) {
      const [a, b] = [...state.pointers.values()];
      state.drag = {
        type: 'pinch',
        dist: Math.hypot(a.x - b.x, a.y - b.y),
        scale: state.view.scale,
        mid: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 },
      };
      canvas.classList.add('dragging');
      return;
    }
    if (state.mode === 'compare' && Math.abs(p.x - splitX()) < grabWidth()) {
      state.drag = { type: 'split' };
      canvas.classList.add('dragging');
      return;
    }
    state.drag = { type: 'pan', start: p, px: p.x, py: p.y, lon: state.view.lon, lat: state.view.lat, moved: false };
    canvas.classList.add('dragging');
  });

  canvas.addEventListener('pointermove', (e) => {
    if (!state.pointers.has(e.pointerId)) {
      if (e.pointerType === 'mouse') { state.hover = pos(e); hoverTip(pos(e)); if (state.mode === 'verify') schedule(); }
      return;
    }
    const p = pos(e);
    state.pointers.set(e.pointerId, p);

    if (state.drag && state.drag.type === 'pinch' && state.pointers.size >= 2) {
      const [a, b] = [...state.pointers.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      state.view.lon += (state.drag.mid.x - mid.x) / state.view.scale;
      state.view.lat -= (state.drag.mid.y - mid.y) / state.view.scale;
      state.drag.mid = mid;
      setZoomAround(state.drag.scale * (d / state.drag.dist), mid.x, mid.y);
      return;
    }
    if (state.drag && state.drag.type === 'split') {
      state.split = Math.min(.95, Math.max(.05, p.x / W()));
      schedule();
      return;
    }
    if (state.drag && state.drag.type === 'pan') {
      const dx = p.x - state.drag.px, dy = p.y - state.drag.py;
      if (Math.hypot(p.x - state.drag.start.x, p.y - state.drag.start.y) > 6) state.drag.moved = true;
      state.view.lon = state.drag.lon - dx / state.view.scale;
      state.view.lat = state.drag.lat + dy / state.view.scale;
      schedule();
      return;
    }
    if (e.pointerType === 'mouse') { hoverTip(p); if (state.mode === 'verify') schedule(); }
  });

  const end = (e) => {
    const p = pos(e);
    state.pointers.delete(e.pointerId);
    const drag = state.drag;
    if (state.pointers.size < 2 && drag && drag.type === 'pinch') {
      state.drag = { type: 'pan', start: p, px: p.x, py: p.y, lon: state.view.lon, lat: state.view.lat, moved: true };
      return;
    }
    if (state.pointers.size === 0) {
      state.drag = null;
      canvas.classList.remove('dragging');
      if (drag && drag.type === 'pan' && !drag.moved) {
        const hit = nearestPoint(p.x, p.y);
        if (hit) select(hit);
        else if (state.mode === 'verify') { state.hover = p; schedule(); }
      }
    }
  };
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);

  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const r = canvas.getBoundingClientRect();
    setZoomAround(state.view.scale * Math.exp(-e.deltaY * 0.0016),
                  e.clientX - r.left, e.clientY - r.top);
  }, { passive: false });

  canvas.addEventListener('dblclick', (e) => {
    const r = canvas.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    const [lon, lat] = unproject(px, py);
    setZoomAround(state.view.scale * 2, W() / 2, H() / 2);
    state.view.lon = lon; state.view.lat = lat;
    schedule();
  });
}

function hoverTip(p) {
  const tip = $('#hover');
  if (!tip) return;
  if (isPhone()) { tip.hidden = true; return; }
  const hit = nearestPoint(p.x, p.y);
  if (hit) {
    tip.hidden = false;
    tip.style.left = Math.min(p.x + 14, W() - 240) + 'px';
    tip.style.top = (p.y + 14) + 'px';
    tip.innerHTML = `<b>${hit.n || 'unidentified'}</b><br>${hit.k} · name confidence ${hit.c}` +
      (hit.a ? `<br><span style="opacity:.72">other reading: ${hit.a}</span>` : '');
  } else tip.hidden = true;
}

function focusPoint(p) {
  state.view.lon = p.lon; state.view.lat = p.lat;
  setZoomAround(Math.max(state.view.scale, scaleForLevel(1150)), W() / 2, H() / 2);
}

/* ------------------------------------------------------------------ selection */
function select(p, focus) {
  state.sel = p;
  if (focus) focusPoint(p);
  $('#emptyState').hidden = true;
  $('#detail').hidden = false;
  if (isPhone()) document.body.classList.add('inspector-open');
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

/* ------------------------------------------------------------------ list */
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
    el.addEventListener('click', () => {
      select(state.points[+el.dataset.i], true);
      if (isPhone()) document.body.classList.remove('panel-open');
    });
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
