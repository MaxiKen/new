const $ = (id) => document.getElementById(id);
const canvas = $('map');
const ctx = canvas.getContext('2d');
const viewport = $('map-viewport');
const number = new Intl.NumberFormat('en');
const issueLabels = {
  'annotation-heavy': 'Annotation-heavy reconstruction',
  'narrow-body': 'Narrow bodies / possible artifacts',
  'contact-review': 'Inferred same-color contacts',
  'similar-colors': 'Indistinguishable legend colors',
  'unresolved-code': 'Unmatched map codes',
  'water': 'Water interpretation',
};
const state = { data: null, width: 0, height: 0, scale: 1, fitScale: 1, x: 0, y: 0,
  mode: 'clean', clickMode: 'polygon', split: .5, contacts: true, selected: null, point: null, highlighted: null,
  issue: 'contact-review', issueIndex: -1, sourceReady: false, ready: false };
let fillPaths = [], contactPaths = [], contactBoxes = [], framePending = false;
const overviewCaches = new Map();
const targetIcon = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="6"/><path d="M12 2v5m0 10v5M2 12h5m10 0h5"/></svg>';
const source = new Image();
const safe = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function makePath(rings) {
  const path = new Path2D();
  for (const ring of rings) {
    if (!ring.length) continue;
    path.moveTo(ring[0][0], ring[0][1]);
    for (let i = 1; i < ring.length; i++) path.lineTo(ring[i][0], ring[i][1]);
    path.closePath();
  }
  return path;
}
function requestDraw() { if (!framePending) { framePending = true; requestAnimationFrame(draw); } }
function visible(box) {
  return box[2] * state.scale + state.x >= 0 && box[0] * state.scale + state.x <= state.width &&
    box[3] * state.scale + state.y >= 0 && box[1] * state.scale + state.y <= state.height;
}
function worldTransform() { ctx.translate(state.x, state.y); ctx.scale(state.scale, state.scale); }
function overviewCache() {
  const key = state.contacts ? 'contacts' : 'fills';
  if (overviewCaches.has(key)) return overviewCaches.get(key);
  const cached = document.createElement('canvas');
  cached.width = Math.ceil(state.data.stats.width / 2);
  cached.height = Math.ceil(state.data.stats.height / 2);
  const c = cached.getContext('2d'); c.scale(.5,.5); c.lineJoin='round';
  state.data.features.forEach((f,i)=>{
    c.fillStyle=state.data.classes[f.classId-1].color;c.strokeStyle=c.fillStyle;c.lineWidth=.9;
    c.stroke(fillPaths[i]);c.fill(fillPaths[i],'evenodd');
  });
  if(state.contacts){c.strokeStyle='#679181';c.globalAlpha=.52;c.lineWidth=.9;for(const path of contactPaths)c.stroke(path);}
  overviewCaches.set(key,cached);return cached;
}
function drawVectors() {
  ctx.save(); worldTransform();
  // Fast overview is rasterized from the FINAL vector paths. Switch back to
  // the full paths at detail zoom, so inspection never enlarges pixel steps.
  if (state.scale < .6 && !state.highlighted) {
    ctx.drawImage(overviewCache(),0,0,state.data.stats.width,state.data.stats.height);
    if(state.selected!==null){ctx.strokeStyle='#326fa3';ctx.lineWidth=2.3/state.scale;ctx.stroke(fillPaths[state.selected]);}
    ctx.restore();return;
  }
  const features = state.data.features;
  for (let i = 0; i < features.length; i++) {
    const feature = features[i];
    if (!visible(feature.bbox)) continue;
    const color = state.data.classes[feature.classId - 1].color;
    ctx.globalAlpha = state.highlighted && feature.classId !== state.highlighted ? .3 : 1;
    ctx.fillStyle = color; ctx.strokeStyle = color;
    // Same-fill hairline removes display antialias seams, not data geometry.
    ctx.lineWidth = .45 / state.scale; ctx.lineJoin = 'round';
    ctx.stroke(fillPaths[i]); ctx.fill(fillPaths[i], 'evenodd');
  }
  ctx.globalAlpha = 1;
  if (state.contacts) {
    ctx.strokeStyle = '#679181'; ctx.globalAlpha = .52;
    ctx.lineWidth = .45 / state.scale; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    for (let i=0;i<contactPaths.length;i++) if(visible(contactBoxes[i])) ctx.stroke(contactPaths[i]);
    ctx.globalAlpha = 1;
  }
  if (state.selected !== null) {
    ctx.strokeStyle = '#326fa3'; ctx.lineWidth = 2.3 / state.scale;
    ctx.stroke(fillPaths[state.selected]);
  }
  ctx.restore();
}
function drawPhoto() {
  ctx.save(); worldTransform();
  if (state.sourceReady) ctx.drawImage(source, 0, 0, state.data.stats.width, state.data.stats.height);
  ctx.restore();
}
function drawPointMarker() {
  if (!state.point) return;
  const x = state.x + state.point.mapX * state.scale;
  const y = state.y + state.point.mapY * state.scale;
  const marker = () => {
    ctx.beginPath(); ctx.moveTo(x - 10, y); ctx.lineTo(x + 10, y);
    ctx.moveTo(x, y - 10); ctx.lineTo(x, y + 10); ctx.arc(x, y, 5.5, 0, Math.PI * 2); ctx.stroke();
  };
  ctx.save(); ctx.lineCap = 'round';
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 5; marker();
  ctx.strokeStyle = '#245f83'; ctx.lineWidth = 1.7; marker();
  ctx.beginPath(); ctx.arc(x, y, 2.5, 0, Math.PI * 2);
  ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = '#245f83'; ctx.lineWidth = 1.2; ctx.stroke();
  ctx.restore();
}
function draw() {
  framePending = false;
  const ratio = Math.min(devicePixelRatio || 1, 2);
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, state.width, state.height);
  if (!state.ready) return;
  if (state.mode === 'clean') drawVectors();
  else if (state.mode === 'source') drawPhoto();
  else {
    drawPhoto();
    ctx.save(); ctx.beginPath(); ctx.rect(state.width * state.split, 0, state.width, state.height); ctx.clip();
    ctx.fillStyle = '#f1f5ed'; ctx.fillRect(0, 0, state.width, state.height);
    drawVectors(); ctx.restore();
    ctx.strokeStyle = '#c99554'; ctx.lineWidth = 1.5; ctx.beginPath();
    ctx.moveTo(state.width * state.split, 0); ctx.lineTo(state.width * state.split, state.height); ctx.stroke();
  }
  drawPointMarker();
  $('zoom-label').textContent = `${Math.round(state.scale / state.fitScale * 100)}%`;
}
function resize() {
  const rect = viewport.getBoundingClientRect();
  const previous = {w:state.width, h:state.height};
  state.width = rect.width; state.height = rect.height;
  const ratio = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(rect.width * ratio); canvas.height = Math.round(rect.height * ratio);
  if (state.ready && !previous.w) fit(state.data.extent);
  else if (state.ready) { state.x += (state.width - previous.w) / 2; state.y += (state.height - previous.h) / 2; }
  requestDraw();
}
function fit(box, padding = 40) {
  const width = Math.max(box[2] - box[0], 20), height = Math.max(box[3] - box[1], 20);
  state.scale = Math.min((state.width - padding * 2) / width, (state.height - padding * 2) / height);
  state.scale = Math.max(.02, state.scale);
  if (state.data && box.every((v,i)=>Math.abs(v-state.data.extent[i])<.01)) state.fitScale=state.scale;
  state.x = state.width / 2 - (box[0] + box[2]) / 2 * state.scale;
  state.y = state.height / 2 - (box[1] + box[3]) / 2 * state.scale;
  requestDraw();
}
function zoom(factor, x = state.width / 2, y = state.height / 2) {
  if (!state.ready) return;
  const next = Math.max(state.fitScale * .65, Math.min(6, state.scale * factor));
  const change = next / state.scale;
  state.x = x - (x - state.x) * change; state.y = y - (y - state.y) * change; state.scale = next;
  requestDraw();
}
function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll('[data-mode]').forEach(b => { b.classList.toggle('active', b.dataset.mode === mode); b.setAttribute('aria-pressed', String(b.dataset.mode === mode)); });
  $('source-notice').hidden = mode === 'clean'; $('compare-control').hidden = mode !== 'compare';
  $('mode-label').textContent = mode === 'clean' ? 'CLEANED POLYGON COVERAGE' : mode === 'source' ? 'UNTOUCHED REFERENCE PHOTO' : 'SOURCE / CLEANED GEOMETRY';
  $('map-subtitle').textContent = mode === 'clean' ? 'Black annotations filled from surrounding geology' : 'Source annotations remain for comparison only';
  requestDraw();
}
function roundedCoordinate(value) {
  const rounded = Number(value.toFixed(6));
  return Object.is(rounded, -0) ? 0 : rounded;
}
function mapPointAt(screenX, screenY) {
  const mapX = (screenX - state.x) / state.scale;
  const mapY = (screenY - state.y) / state.scale;
  const t = state.data.transform;
  return {
    mapX, mapY,
    longitude: roundedCoordinate(t[0] * mapX + t[1] * mapY + t[2]),
    latitude: roundedCoordinate(t[3] * mapX + t[4] * mapY + t[5]),
  };
}
function axisCoordinate(value, positiveHemisphere, negativeHemisphere) {
  const rounded = Math.abs(value) < .0000005 ? 0 : value;
  return `${Math.abs(rounded).toFixed(6)}° ${rounded < 0 ? negativeHemisphere : positiveHemisphere}`;
}
function updateCoordinateReadout(point) {
  $('coordinates').textContent = `${axisCoordinate(point.longitude, 'E', 'W')}   ${axisCoordinate(point.latitude, 'N', 'S')}`;
}
function renderOverview() {
  $('inspect-title').textContent = 'Map overview';
  $('clear-selection').hidden = true;
  $('clear-selection').setAttribute('aria-label', 'Clear map inspection');
  const coordinateMode = state.clickMode === 'coordinate';
  $('inspector').innerHTML = coordinateMode
    ? `<div class="empty-state"><span class="inspect-icon">${targetIcon}</span><h3>Capture a map point.</h3><p>Click anywhere on the map to show its longitude and latitude in decimal degrees.</p></div>`
    : `<div class="empty-state"><span class="inspect-icon">${targetIcon}</span><h3>Every body, individually.</h3><p>Click a polygon to see its unit, area, and review flags. Same-colored bodies remain separate features.</p></div>`;
}
function setClickMode(mode) {
  state.clickMode = mode;
  document.querySelectorAll('[data-click-mode]').forEach(button => {
    const active = button.dataset.clickMode === mode;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  const coordinateMode = mode === 'coordinate';
  $('map-hint').textContent = coordinateMode
    ? 'Drag to pan · scroll to zoom · click anywhere for coordinates'
    : 'Drag to pan · scroll to zoom · click a polygon';
  canvas.setAttribute('aria-label', coordinateMode
    ? 'Interactive Nigeria geological map. Drag to pan, use plus or minus to zoom, press F to fit, click anywhere to read its coordinates.'
    : 'Interactive Nigeria geological map. Drag to pan, use plus or minus to zoom, press F to fit, click a polygon to inspect.');
  if (state.selected === null && !state.point) renderOverview();
}
async function copyCoordinates(point, button) {
  const value = `${point.longitude.toFixed(6)}, ${point.latitude.toFixed(6)}`;
  let copied = false;
  try {
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(value);
    else throw new Error('Clipboard API unavailable');
    copied = true;
  } catch {
    const field = document.createElement('textarea');
    field.value = value; field.setAttribute('readonly', '');
    field.style.position = 'fixed'; field.style.left = '-10000px';
    document.body.append(field); field.select();
    try { copied = document.execCommand('copy'); } catch { copied = false; }
    field.remove();
  }
  button.textContent = copied ? 'Copied ✓' : 'Copy unavailable';
  $('announcement').textContent = copied
    ? `Copied longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)}.`
    : 'Clipboard access was unavailable. The coordinate is shown above for manual copying.';
  window.setTimeout(() => { if (button.isConnected) button.textContent = 'Copy coordinates'; }, 1800);
}
function showCoordinate(screenX, screenY) {
  const point = mapPointAt(screenX, screenY);
  state.selected = null; state.point = point;
  $('inspect-title').textContent = 'Clicked map point';
  $('clear-selection').hidden = false;
  $('clear-selection').setAttribute('aria-label', 'Clear point coordinate');
  $('inspector').innerHTML = `<div class="point-selection"><p class="point-intro">Clicked location · decimal degrees</p><div class="point-coordinate"><span>Longitude</span><strong id="point-longitude">${axisCoordinate(point.longitude, 'E', 'W')}</strong></div><div class="point-coordinate"><span>Latitude</span><strong id="point-latitude">${axisCoordinate(point.latitude, 'N', 'S')}</strong></div><button id="copy-coordinate" class="copy-coordinate" type="button">Copy coordinates</button><p class="coordinate-note">Copy format: longitude, latitude. WGS 84 is assumed; the source datum is unconfirmed.</p></div>`;
  $('copy-coordinate').addEventListener('click', event => copyCoordinates(point, event.currentTarget));
  updateCoordinateReadout(point);
  $('announcement').textContent = `Clicked map point. Longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)} decimal degrees. WGS 84 assumed; datum unconfirmed.`;
  requestDraw();
}
function legend() {
  if (!state.data) return;
  const query = $('legend-search').value.trim().toLowerCase();
  const units = state.data.classes.filter(u => u.count > 0 && `${u.code} ${u.name}`.toLowerCase().includes(query));
  $('legend').innerHTML = units.length ? units.map(u => `<button class="unit ${u.id === state.highlighted ? 'active' : ''}" data-unit="${u.id}" aria-pressed="${u.id === state.highlighted}"><span class="swatch" style="background:${u.color}"></span><span class="unit-copy"><strong>${safe(u.code)}</strong><small title="${safe(u.name)}">${safe(u.name)}</small></span><span class="unit-number">${u.count}</span></button>`).join('') : '<div class="skeleton">No matching units. Try a rock type or unit code.</div>';
  $('legend').querySelectorAll('[data-unit]').forEach(button => button.addEventListener('click', () => {
    const id = Number(button.dataset.unit); state.highlighted = state.highlighted === id ? null : id;
    $('clear-highlight').hidden = !state.highlighted; legend(); requestDraw();
  }));
}
function select(index, focus = false) {
  state.selected = index; state.point = null;
  $('clear-selection').hidden = index === null;
  $('clear-selection').setAttribute('aria-label', index === null ? 'Clear map inspection' : 'Clear polygon selection');
  if (index === null) {
    renderOverview();
  } else {
    const f = state.data.features[index], u = state.data.classes[f.classId - 1];
    $('inspect-title').textContent = `Polygon ${number.format(f.id)}`;
    $('inspector').innerHTML = `<div class="selection"><div class="selected-label"><span class="swatch" style="background:${u.color}"></span><div><strong>${safe(u.code)}</strong><small>CLASS ${u.id} · SINGLEPART FEATURE</small></div></div><p class="selected-name">${safe(u.name)}</p><div class="details-row"><span>Approximate area</span><strong>${number.format(f.area)} km²</strong></div><div class="details-row" title="Source pixels in the annotation buffer, summarized per reconstructed body. Not accuracy."><span>Annotation buffer</span><strong>${f.annotation}%</strong></div><div class="details-row" title="Close first/second color matches. Not accuracy."><span>Color ambiguity</span><strong>${f.ambiguity}%</strong></div><div class="details-row"><span>Candidate class IDs</span><strong>${u.candidates.join(', ')}</strong></div><div>${f.issues.length ? f.issues.map(i => `<span class="flag">${safe(issueLabels[i])}</span>`).join('') : '<span class="flag">Draft · geological review still needed</span>'}</div><button id="compare-selection" class="inspect-compare">Compare this body with the photo ↗</button></div>`;
    $('compare-selection').addEventListener('click', () => { setMode('compare'); fit(f.bbox, 80); });
    if (focus) { fit(f.bbox, 80); if (state.scale > 3) zoom(3 / state.scale); }
    $('announcement').textContent = `Selected polygon ${f.id}, ${u.code}, ${u.name}. ${f.issues.length} review flags.`;
  }
  requestDraw();
}
function issueList() {
  const counts = state.data.stats.issueCounts;
  $('issues').innerHTML = Object.entries(issueLabels).map(([key,label]) => `<button class="issue ${key === state.issue ? 'active' : ''}" data-issue="${key}" aria-pressed="${key === state.issue}"><span>${label}</span><span>${number.format(counts[key] || 0)}</span></button>`).join('');
  $('issues').querySelectorAll('[data-issue]').forEach(b => b.addEventListener('click', () => { state.issue = b.dataset.issue; state.issueIndex = -1; issueList(); nextIssue(); }));
  $('next-issue').disabled = !counts[state.issue];
}
function nextIssue() {
  const indexes = state.data.features.map((f,i) => f.issues.includes(state.issue) ? i : -1).filter(i => i >= 0);
  if (!indexes.length) return;
  state.issueIndex = (state.issueIndex + 1) % indexes.length;
  select(indexes[state.issueIndex], true);
  $('issue-position').textContent = `${state.issueIndex + 1} of ${number.format(indexes.length)} flagged bodies`;
}
function pick(screenX, screenY) {
  const x = (screenX - state.x) / state.scale, y = (screenY - state.y) / state.scale;
  let selected = null;
  ctx.save(); ctx.setTransform(1,0,0,1,0,0);
  for (let i = state.data.features.length - 1; i >= 0; i--) {
    const b = state.data.features[i].bbox;
    if (x >= b[0] && x <= b[2] && y >= b[1] && y <= b[3] && ctx.isPointInPath(fillPaths[i],x,y,'evenodd')) { selected = i; break; }
  }
  ctx.restore(); select(selected);
}
let down = null, moved = false;
const pointers = new Map();
let pinch = null;
canvas.addEventListener('pointerdown', e => {
  if (!state.ready || e.button > 0) return;
  canvas.setPointerCapture(e.pointerId); canvas.focus({preventScroll:true});
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  down = {x:e.clientX,y:e.clientY,lastX:e.clientX,lastY:e.clientY}; moved = false;
  if (pointers.size === 2) { const [a,b] = [...pointers.values()]; pinch = Math.hypot(a.x-b.x,a.y-b.y); moved = true; }
});
canvas.addEventListener('pointermove', e => {
  if (!state.ready) return;
  const rect = canvas.getBoundingClientRect();
  const sx=e.clientX-rect.left, sy=e.clientY-rect.top;
  updateCoordinateReadout(mapPointAt(sx,sy));
  if (!pointers.has(e.pointerId)) return;
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if (pointers.size === 2) {
    const [a,b] = [...pointers.values()]; const distance=Math.hypot(a.x-b.x,a.y-b.y);
    if (pinch) zoom(distance/pinch,(a.x+b.x)/2-rect.left,(a.y+b.y)/2-rect.top);
    pinch=distance; moved=true; return;
  }
  if (down) {
    if (Math.hypot(e.clientX-down.x,e.clientY-down.y)>4) moved=true;
    state.x+=e.clientX-down.lastX; state.y+=e.clientY-down.lastY;
    down.lastX=e.clientX; down.lastY=e.clientY; requestDraw();
  }
});
canvas.addEventListener('pointerup', e => {
  if (!pointers.has(e.pointerId)) return;
  const rect=canvas.getBoundingClientRect();
  if (!moved && pointers.size===1) {
    const x=e.clientX-rect.left, y=e.clientY-rect.top;
    if (state.clickMode === 'coordinate') showCoordinate(x,y);
    else pick(x,y);
  }
  pointers.delete(e.pointerId); pinch=null;
  if (pointers.size) { const p=[...pointers.values()][0]; down={x:p.x,y:p.y,lastX:p.x,lastY:p.y}; moved=true; }
  else down=null;
});
canvas.addEventListener('pointercancel', e => { pointers.delete(e.pointerId);down=null;pinch=null; });
canvas.addEventListener('wheel', e => { if (!state.ready) return; e.preventDefault();const r=canvas.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.0015),e.clientX-r.left,e.clientY-r.top); }, {passive:false});
canvas.addEventListener('keydown', e => {
  if (['+','=','-','f','F','Escape','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) e.preventDefault();
  if (e.key==='+' || e.key==='=') zoom(1.35);
  if (e.key==='-') zoom(1/1.35);
  if (e.key.toLowerCase()==='f' && state.data) fit(state.data.extent);
  if (e.key==='Escape') select(null);
  if (e.key==='ArrowLeft') state.x+=35;
  if (e.key==='ArrowRight') state.x-=35;
  if (e.key==='ArrowUp') state.y+=35;
  if (e.key==='ArrowDown') state.y-=35;
  requestDraw();
});
$('zoom-in').addEventListener('click',()=>zoom(1.4)); $('zoom-out').addEventListener('click',()=>zoom(1/1.4));
$('fit').addEventListener('click',()=>state.ready && fit(state.data.extent));
$('show-contacts').addEventListener('change',e=>{state.contacts=e.target.checked;requestDraw();});
$('compare-position').addEventListener('input',e=>{state.split=Number(e.target.value)/100;requestDraw();});
$('legend-search').addEventListener('input',legend);
$('clear-highlight').addEventListener('click',()=>{state.highlighted=null;$('clear-highlight').hidden=true;legend();requestDraw();});
$('clear-selection').addEventListener('click',()=>select(null));
$('next-issue').addEventListener('click',nextIssue);
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
document.querySelectorAll('[data-click-mode]').forEach(b=>b.addEventListener('click',()=>setClickMode(b.dataset.clickMode)));
new ResizeObserver(resize).observe(viewport);
async function initialize() {
  try {
    const response=await fetch('/data/map.json');
    if (!response.ok) throw new Error(`Geometry request returned HTTP ${response.status}.`);
    const data=await response.json(); state.data=data;
    if (!data.features?.length || !data.classes?.length) throw new Error('No polygon data was found.');
    fillPaths=data.features.map(f=>makePath(f.rings));
    contactBoxes=data.contacts.map(points=>{let a=Infinity,b=Infinity,c=-Infinity,d=-Infinity;for(const [x,y] of points){a=Math.min(a,x);b=Math.min(b,y);c=Math.max(c,x);d=Math.max(d,y);}return[a,b,c,d];});
    contactPaths=data.contacts.map(points=>{const p=new Path2D();p.moveTo(...points[0]);for(let i=1;i<points.length;i++)p.lineTo(...points[i]);return p;});
    await new Promise((resolve,reject)=>{source.onload=()=>{state.sourceReady=true;resolve();};source.onerror=()=>reject(new Error('The comparison photo could not be loaded.'));source.src='/data/source.jpg';});
    state.ready=true; resize(); fit(data.extent); state.fitScale=state.scale;
    $('loading').hidden=true; $('class-count').textContent=number.format(data.stats.classCount);
    $('feature-count').textContent=number.format(data.stats.featureCount); $('contact-count').textContent=number.format(data.stats.contactCount);
    legend(); issueList();
    $('regions').innerHTML=data.regions.map((r,i)=>`<button data-region="${i}" class="${i===0?'active':''}">${safe(r.name)}</button>`).join('');
    $('regions').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{select(null);fit(data.regions[Number(b.dataset.region)].box);$('regions').querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b));}));
    requestDraw();
    window.mapReview = Object.freeze({ready:true,stats:data.stats});
    $('announcement').textContent=`Map ready. ${number.format(data.features.length)} individual polygons. No black fill classes and no internal coverage gaps.`;
  } catch (error) {
    console.error(error); $('loading').hidden=true; $('error').hidden=false; $('error-message').textContent=error.message;
  }
}
initialize();
