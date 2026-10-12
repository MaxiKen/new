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
const editTypes = {
  'add-feature': 'Add a missing small geology feature',
  'join-features': 'Join two features into one polygon',
  'remove-polygon': 'Remove this polygon',
  'shrink-polygon': 'Make this polygon smaller',
  'expand-polygon': 'Make this polygon bigger',
};
const mapSourceLabels = { draft: 'Current shapefile draft', original: 'Original reference map' };
const state = { data: null, width: 0, height: 0, scale: 1, fitScale: 1, x: 0, y: 0,
  mode: 'clean', clickMode: 'polygon', split: .5, contacts: true, selected: null, point: null,
  secondPoint: null, draft: null, captureTarget: null, pendingNotes: [], nextNoteId: 1,
  highlighted: null, issue: 'contact-review', issueIndex: -1, sourceReady: false, ready: false };
let fillPaths = [], contactPaths = [], contactBoxes = [], framePending = false;
let sampleCanvas = null, sampleContext = null;
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
  const drawMarker = (point, label, color) => {
    if (!point) return;
    const x = state.x + point.mapX * state.scale;
    const y = state.y + point.mapY * state.scale;
    const marker = () => {
      ctx.beginPath(); ctx.moveTo(x - 10, y); ctx.lineTo(x + 10, y);
      ctx.moveTo(x, y - 10); ctx.lineTo(x, y + 10); ctx.arc(x, y, 5.5, 0, Math.PI * 2); ctx.stroke();
    };
    ctx.save(); ctx.lineCap = 'round';
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 5; marker();
    ctx.strokeStyle = color; ctx.lineWidth = 1.7; marker();
    ctx.beginPath(); ctx.arc(x, y, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    ctx.font = '600 10px sans-serif'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 3; ctx.strokeStyle = '#fff'; ctx.strokeText(label, x + 9, y - 9);
    ctx.fillStyle = color; ctx.fillText(label, x + 9, y - 9);
    ctx.restore();
  };
  drawMarker(state.point, 'A', '#245f83');
  drawMarker(state.secondPoint, 'B', '#9b6730');
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
function coordinatePair(point) { return `${point.longitude.toFixed(6)}, ${point.latitude.toFixed(6)}`; }
function updateCoordinateReadout(point) {
  $('coordinates').textContent = `${axisCoordinate(point.longitude, 'E', 'W')}   ${axisCoordinate(point.latitude, 'N', 'S')}`;
}
function featureIndexAt(mapX, mapY) {
  let selected = null;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  for (let i = state.data.features.length - 1; i >= 0; i--) {
    const box = state.data.features[i].bbox;
    if (mapX >= box[0] && mapX <= box[2] && mapY >= box[1] && mapY <= box[3] && ctx.isPointInPath(fillPaths[i], mapX, mapY, 'evenodd')) {
      selected = i; break;
    }
  }
  ctx.restore();
  return selected;
}
function sourceForClick(screenX) {
  if (state.mode === 'source') return 'original';
  if (state.mode === 'compare') return screenX < state.width * state.split ? 'original' : 'draft';
  return 'draft';
}
function samplePointColor(point, mapSource) {
  if (!point) return '';
  if (mapSource === 'draft') {
    const index = featureIndexAt(point.mapX, point.mapY);
    return index === null ? '' : state.data.classes[state.data.features[index].classId - 1].color.toUpperCase();
  }
  if (!state.sourceReady || !sampleContext || point.mapX < 0 || point.mapY < 0 ||
      point.mapX >= source.naturalWidth || point.mapY >= source.naturalHeight) return '';
  const x = Math.floor(point.mapX), y = Math.floor(point.mapY);
  sampleContext.clearRect(0, 0, 1, 1);
  sampleContext.drawImage(source, x, y, 1, 1, 0, 0, 1, 1);
  const [r, g, b] = sampleContext.getImageData(0, 0, 1, 1).data;
  return `#${[r, g, b].map(value => value.toString(16).padStart(2, '0')).join('').toUpperCase()}`;
}
function updateMapHint() {
  if (state.captureTarget === 'second') {
    $('map-hint').textContent = 'Click the map to set Point B · Escape cancels';
    canvas.setAttribute('aria-label', 'Choose Point B for the pending join note by clicking the map.');
  } else if (state.clickMode === 'coordinate') {
    $('map-hint').textContent = 'Drag to pan · scroll to zoom · click a point to start an edit note';
    canvas.setAttribute('aria-label', 'Interactive Nigeria geological map. Drag to pan, use plus or minus to zoom, press F to fit, click a point to start an edit note.');
  } else {
    $('map-hint').textContent = 'Drag to pan · scroll to zoom · click a polygon';
    canvas.setAttribute('aria-label', 'Interactive Nigeria geological map. Drag to pan, use plus or minus to zoom, press F to fit, click a polygon to inspect.');
  }
}
function renderOverview() {
  if (state.draft) return renderDraftEditor();
  $('inspect-title').textContent = 'Map overview';
  $('clear-selection').hidden = true;
  $('clear-selection').setAttribute('aria-label', 'Clear map inspection');
  const coordinateMode = state.clickMode === 'coordinate';
  $('inspector').innerHTML = coordinateMode
    ? `<div class="empty-state"><span class="inspect-icon">${targetIcon}</span><h3>Ready to note a map edit.</h3><p>Click a location, choose one of five edit types, then save it to your session list.</p><p>Nothing is written to disk.</p></div>`
    : `<div class="empty-state"><span class="inspect-icon">${targetIcon}</span><h3>Every body, individually.</h3><p>Click a polygon to see its unit, area, and review flags. Same-colored bodies remain separate features.</p></div>`;
}
function setClickMode(mode) {
  state.clickMode = mode;
  if (mode !== 'coordinate') state.captureTarget = null;
  document.querySelectorAll('[data-click-mode]').forEach(button => {
    const active = button.dataset.clickMode === mode;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  updateMapHint();
  if (state.draft) renderDraftEditor();
  else if (state.selected === null && !state.point) renderOverview();
}
async function copyText(text) {
  try {
    if (navigator.clipboard?.writeText) { await navigator.clipboard.writeText(text); return true; }
  } catch { /* Fall through to the selection-based clipboard fallback. */ }
  const field = document.createElement('textarea');
  field.value = text; field.setAttribute('readonly', '');
  field.style.position = 'fixed'; field.style.left = '-10000px';
  document.body.append(field); field.select();
  let copied = false;
  try { copied = document.execCommand('copy'); } catch { copied = false; }
  field.remove();
  return copied;
}
async function copyCoordinates(point, button, resetLabel = 'Copy coordinates') {
  const copied = await copyText(coordinatePair(point));
  button.textContent = copied ? 'Copied ✓' : 'Copy unavailable';
  $('announcement').textContent = copied
    ? `Copied longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)}.`
    : 'Clipboard access was unavailable. The coordinate is shown above for manual copying.';
  window.setTimeout(() => { if (button.isConnected) button.textContent = resetLabel; }, 1800);
}
function colorHex(value) { return /^#[0-9a-f]{6}$/i.test(value || '') ? value.toUpperCase() : ''; }
function setDraftSource(mapSource) {
  const draft = state.draft;
  draft.mapSource = mapSource;
  draft.colorAtPointA = samplePointColor(draft.point, mapSource);
  draft.colorAtPointB = draft.secondPoint ? samplePointColor(draft.secondPoint, mapSource) : '';
  if (!draft.colorManuallyEdited) draft.colorCode = draft.colorAtPointA;
  draft.confirmedColorMatch = false;
  renderDraftEditor();
}
function renderDraftEditor() {
  const draft = state.draft;
  if (!draft) return renderOverview();
  state.point = draft.point; state.secondPoint = draft.secondPoint;
  $('inspect-title').textContent = 'Draft change note';
  $('clear-selection').hidden = false;
  $('clear-selection').setAttribute('aria-label', 'Discard unsaved change note');
  const actionOptions = Object.entries(editTypes).map(([value, label], index) => `<option value="${value}" ${draft.type === value ? 'selected' : ''}>${index + 1}. ${safe(label)}</option>`).join('');
  const colorValue = colorHex(draft.colorCode);
  const colorMismatch = Boolean(draft.colorAtPointA && draft.colorAtPointB && draft.colorAtPointA !== draft.colorAtPointB);
  const pointB = draft.secondPoint ? coordinatePair(draft.secondPoint) : 'Not captured yet';
  $('inspector').innerHTML = `<div class="point-selection note-editor">
    <p class="point-intro">Point A · primary clicked location · decimal degrees</p>
    <div class="point-coordinate"><span>Longitude</span><strong id="point-longitude">${axisCoordinate(draft.point.longitude, 'E', 'W')}</strong></div>
    <div class="point-coordinate"><span>Latitude</span><strong id="point-latitude">${axisCoordinate(draft.point.latitude, 'N', 'S')}</strong></div>
    <button id="copy-point-coordinate" class="copy-coordinate" type="button">Copy Point A coordinates</button>
    <label class="note-field" for="edit-type"><span>Requested change</span><select id="edit-type"><option value="">Choose one of five edit types…</option>${actionOptions}</select></label>
    <div class="join-endpoints" id="join-endpoints" ${draft.type === 'join-features' ? '' : 'hidden'}>
      <div class="endpoint-heading"><span>Point B · second feature</span><strong id="point-b-coordinate">${safe(pointB)}</strong></div>
      <button id="pick-second-point" class="secondary-button" type="button">${state.captureTarget === 'second' ? 'Waiting for Point B · cancel' : draft.secondPoint ? 'Choose Point B again' : 'Pick the second point on the map'}</button>
      <div class="join-color-summary"><span>Sampled color at Point B</span><strong id="point-b-color">${safe(draft.colorAtPointB || 'Not sampled yet')}</strong><p id="join-color-warning" ${colorMismatch ? '' : 'hidden'}>The sampled colors differ. Confirm both points belong to the same geological color before saving.</p></div>
      <label id="color-confirmation-wrap" class="color-confirmation" ${colorMismatch ? '' : 'hidden'}><input id="confirm-color-match" type="checkbox" ${draft.confirmedColorMatch ? 'checked' : ''}><span>I confirm these points belong to the same intended geological color despite the different samples.</span></label>
    </div>
    <label class="note-field" for="note-map-source"><span>Reference map</span><select id="note-map-source"><option value="draft" ${draft.mapSource === 'draft' ? 'selected' : ''}>Current shapefile draft</option><option value="original" ${draft.mapSource === 'original' ? 'selected' : ''}>Original reference map</option></select></label>
    <div class="note-field"><label for="note-color-code">Color code at Point A</label><div class="color-input-row"><input id="note-color-picker" type="color" value="${colorValue || '#808080'}" aria-label="Choose Point A color"><input id="note-color-code" type="text" value="${safe(draft.colorCode)}" maxlength="7" placeholder="No color sampled" autocomplete="off" spellcheck="false"></div><small>Auto-sampled from the selected map; edit if you know the intended code.</small><div id="color-code-error" class="field-error" hidden>Use a six-digit hex color such as #A1B2C3, or leave it blank.</div></div>
    <label class="note-field" for="edit-details"><span>Additional details <small>optional</small></span><textarea id="edit-details" rows="3" placeholder="Unit name/code, what looks wrong, or other context…">${safe(draft.details)}</textarea></label>
    <p class="session-only-note">Saving adds this edit to the in-memory list only. Nothing is written to a file or sent to a server.</p>
    <button id="save-note" class="save-note-button" type="button" ${!draft.type || (draft.type === 'join-features' && !draft.secondPoint) ? 'disabled' : ''}>Save to pending notes</button>
    <div id="draft-error" class="field-error" role="alert" hidden></div>
  </div>`;
  $('copy-point-coordinate').addEventListener('click', event => copyCoordinates(draft.point, event.currentTarget, 'Copy Point A coordinates'));
  $('edit-type').addEventListener('change', event => { draft.type = event.currentTarget.value; renderDraftEditor(); });
  $('note-map-source').addEventListener('change', event => setDraftSource(event.currentTarget.value));
  $('note-color-code').addEventListener('input', event => {
    draft.colorCode = event.currentTarget.value.trim(); draft.colorManuallyEdited = true;
    const hex = colorHex(draft.colorCode);
    if (hex) $('note-color-picker').value = hex;
    updateDraftValidation();
  });
  $('note-color-picker').addEventListener('input', event => {
    draft.colorCode = event.currentTarget.value.toUpperCase(); draft.colorManuallyEdited = true;
    $('note-color-code').value = draft.colorCode; updateDraftValidation();
  });
  $('edit-details').addEventListener('input', event => { draft.details = event.currentTarget.value; });
  $('pick-second-point')?.addEventListener('click', () => {
    if (state.captureTarget === 'second') state.captureTarget = null;
    else state.captureTarget = 'second';
    updateMapHint(); renderDraftEditor();
    if (state.captureTarget === 'second') $('announcement').textContent = 'Choose Point B by clicking the map. Point A and the note details will be kept.';
  });
  $('confirm-color-match')?.addEventListener('change', event => {
    draft.confirmedColorMatch = event.currentTarget.checked; updateDraftValidation();
  });
  $('save-note')?.addEventListener('click', saveDraftNote);
  updateDraftValidation(); updateMapHint(); requestDraw();
}
function updateDraftValidation() {
  const draft = state.draft;
  if (!draft || !$('save-note')) return;
  const rawColor = $('note-color-code').value.trim();
  const invalidColor = rawColor !== '' && !colorHex(rawColor);
  $('color-code-error').hidden = !invalidColor;
  const needsSecond = draft.type === 'join-features';
  const a = draft.colorAtPointA, b = draft.colorAtPointB;
  const colorMismatch = Boolean(needsSecond && a && b && a !== b);
  const warning = $('join-color-warning');
  if (warning) warning.hidden = !colorMismatch;
  const confirmation = $('color-confirmation-wrap');
  if (confirmation) confirmation.hidden = !colorMismatch;
  const confirmInput = $('confirm-color-match');
  const colorConfirmed = !colorMismatch || Boolean(confirmInput?.checked);
  $('save-note').disabled = !draft.type || (needsSecond && !draft.secondPoint) || invalidColor || !colorConfirmed;
}
function beginDraft(screenX, screenY) {
  if (state.draft && !window.confirm('Discard the unsaved change note and start a new one?')) {
    renderDraftEditor(); return;
  }
  const point = mapPointAt(screenX, screenY);
  const mapSource = sourceForClick(screenX);
  const color = samplePointColor(point, mapSource);
  state.selected = null; state.point = point; state.secondPoint = null; state.captureTarget = null;
  state.draft = { point, secondPoint: null, type: '', mapSource, colorCode: color, colorAtPointA: color,
    colorAtPointB: '', colorManuallyEdited: false, confirmedColorMatch: false, details: '' };
  updateCoordinateReadout(point); renderDraftEditor();
  $('announcement').textContent = `New edit note at longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)}.`;
}
function captureSecondPoint(screenX, screenY) {
  if (!state.draft) return beginDraft(screenX, screenY);
  const point = mapPointAt(screenX, screenY);
  state.draft.secondPoint = point;
  state.draft.colorAtPointB = samplePointColor(point, state.draft.mapSource);
  state.draft.confirmedColorMatch = false;
  state.point = state.draft.point; state.secondPoint = point; state.captureTarget = null;
  updateCoordinateReadout(point); renderDraftEditor();
  $('announcement').textContent = `Point B recorded at longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)}.`;
}
function buildChangePrompt(notes) {
  const formatNote = (note, index) => {
    const lines = [
      `${index + 1}. ${editTypes[note.type]}`,
      `   - Point A coordinate (longitude, latitude): ${coordinatePair(note.point)}`,
      `   - Requested change: ${editTypes[note.type]}`,
      `   - Reference map: ${mapSourceLabels[note.mapSource]}`,
      `   - Point A sampled color: ${note.colorAtPointA || 'Not sampled'}`,
      `   - Recorded color code: ${note.colorCode || 'Not provided'}`,
    ];
    if (note.secondPoint) {
      lines.push(`   - Point B coordinate (longitude, latitude): ${coordinatePair(note.secondPoint)}`);
      lines.push(`   - Point B sampled color: ${note.colorAtPointB || 'Not sampled'}`);
      const sampledColorsMatch = note.colorAtPointA && note.colorAtPointB && note.colorAtPointA === note.colorAtPointB;
      lines.push(`   - Color consistency: ${sampledColorsMatch ? 'same sampled color' : note.confirmedColorMatch ? 'user confirms both points share the intended geological color despite different samples' : 'not fully verified; please review'}`);
      lines.push('   - Join request: treat both locations as one polygon, retaining the shared geological color/attributes where appropriate.');
    }
    if (note.details) lines.push(`   - Additional details: ${note.details}`);
    return lines.join('\n');
  };
  return [
    'Please update the Nigeria geological map shapefile using these field-review notes.',
    'Coordinates are longitude, latitude in decimal degrees to six places. The viewer assumes WGS 84, but the original map datum is unconfirmed; verify alignment before editing.',
    'The reference-map field says whether each location was marked on the original source map or the current shapefile draft. Colors are sampled/recorded point colors, not guaranteed geological class assignments.',
    'Apply only the requested edits, preserve valid polygon topology and shared boundaries, and flag any ambiguity instead of guessing.',
    '',
    ...notes.map(formatNote),
  ].join('\n');
}
async function copyAllNotes() {
  if (!state.pendingNotes.length) return;
  const prompt = buildChangePrompt(state.pendingNotes);
  $('compiled-note').value = prompt; $('compiled-note-wrap').hidden = false;
  const copied = await copyText(prompt);
  $('copy-status').textContent = copied
    ? 'All pending edit notes were copied. The complete prompt is shown below.'
    : 'Clipboard access was unavailable. The complete prompt is shown below; select the text to copy it.';
  $('announcement').textContent = copied ? 'All pending edit notes copied to the clipboard.' : 'The edit prompt is displayed below and can be selected for copying.';
}
function hideCompiledPrompt() {
  $('compiled-note-wrap').hidden = true; $('compiled-note').value = ''; $('copy-status').textContent = '';
}
function renderPendingNotes() {
  $('pending-count').textContent = String(state.pendingNotes.length);
  $('copy-all-notes').disabled = !state.pendingNotes.length;
  $('pending-notes').innerHTML = state.pendingNotes.length ? state.pendingNotes.map((note, index) => {
    const pointB = note.secondPoint ? `<p><span>Point B</span><strong>${safe(coordinatePair(note.secondPoint))}</strong></p><p><span>Point B color</span><strong>${safe(note.colorAtPointB || 'Not sampled')}</strong></p>` : '';
    const colorsMatch = note.colorAtPointA && note.colorAtPointB && note.colorAtPointA === note.colorAtPointB;
    const consistency = note.secondPoint ? `<p><span>Color check</span><strong>${colorsMatch ? 'Samples match' : note.confirmedColorMatch ? 'Match confirmed' : 'Review needed'}</strong></p>` : '';
    const details = note.details ? `<p><span>Details</span><strong>${safe(note.details)}</strong></p>` : '';
    return `<article class="pending-note"><div class="pending-note-heading"><div><small>EDIT ${String(index + 1).padStart(2, '0')}</small><strong>${safe(editTypes[note.type])}</strong></div><button class="remove-note" type="button" data-remove-note="${note.id}" aria-label="Remove edit note ${index + 1}">×</button></div><p><span>Point A</span><strong>${safe(coordinatePair(note.point))}</strong></p><p><span>Reference map</span><strong>${safe(mapSourceLabels[note.mapSource])}</strong></p><p><span>Point A color</span><strong>${safe(note.colorCode || note.colorAtPointA || 'Not sampled')}</strong></p>${pointB}${consistency}${details}</article>`;
  }).join('') : '<div class="no-pending-notes">No pending edits yet. Save a point note to add it here.</div>';
  $('pending-notes').querySelectorAll('[data-remove-note]').forEach(button => button.addEventListener('click', () => {
    const id = Number(button.dataset.removeNote);
    state.pendingNotes = state.pendingNotes.filter(note => note.id !== id);
    hideCompiledPrompt(); renderPendingNotes();
  }));
}
function saveDraftNote() {
  const draft = state.draft;
  if (!draft) return;
  const colorCode = $('note-color-code').value.trim().toUpperCase();
  if (!draft.type) { $('draft-error').textContent = 'Choose one of the five edit types first.'; $('draft-error').hidden = false; return; }
  if (draft.type === 'join-features' && !draft.secondPoint) { $('draft-error').textContent = 'Pick Point B to complete this join request.'; $('draft-error').hidden = false; return; }
  if (draft.type === 'join-features' && draft.colorAtPointA && draft.colorAtPointB && draft.colorAtPointA !== draft.colorAtPointB && !draft.confirmedColorMatch) {
    $('draft-error').textContent = 'Confirm that both locations represent the same intended color before saving this join.'; $('draft-error').hidden = false; return;
  }
  if (colorCode && !colorHex(colorCode)) { $('draft-error').textContent = 'Enter a six-digit hex color or clear the color field.'; $('draft-error').hidden = false; return; }
  state.pendingNotes.push({ id: state.nextNoteId++, type: draft.type, point: draft.point, secondPoint: draft.secondPoint,
    mapSource: draft.mapSource, colorCode, colorAtPointA: draft.colorAtPointA, colorAtPointB: draft.colorAtPointB,
    confirmedColorMatch: draft.confirmedColorMatch, details: draft.details.trim() });
  const savedCount = state.pendingNotes.length;
  state.draft = null; state.point = null; state.secondPoint = null; state.captureTarget = null; state.selected = null;
  hideCompiledPrompt(); renderPendingNotes(); renderOverview(); requestDraw();
  $('copy-status').textContent = `Edit ${savedCount} saved to the in-memory pending list. Nothing was written to disk.`;
  $('announcement').textContent = `Edit note ${savedCount} added to the pending list.`;
}
function startCoordinateNote(screenX, screenY) { beginDraft(screenX, screenY); }
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
  state.selected = index; state.point = null; state.secondPoint = null; state.captureTarget = null;
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
  select(featureIndexAt(x, y));
}
function clearCurrentInspection() {
  if (state.selected !== null) { select(null); return; }
  if (state.draft) {
    if (!window.confirm('Discard this unsaved change note?')) return;
    state.draft = null; state.point = null; state.secondPoint = null; state.captureTarget = null;
    updateMapHint(); renderOverview(); requestDraw(); return;
  }
  select(null);
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
    if (state.captureTarget === 'second') captureSecondPoint(x,y);
    else if (state.clickMode === 'coordinate') startCoordinateNote(x,y);
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
  if (e.key==='Escape') {
    if (state.captureTarget === 'second') { state.captureTarget = null; renderDraftEditor(); }
    else select(null);
  }
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
$('clear-selection').addEventListener('click',clearCurrentInspection);
$('copy-all-notes').addEventListener('click',copyAllNotes);
$('compiled-note').addEventListener('click',event=>event.currentTarget.select());
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
    sampleCanvas=document.createElement('canvas');sampleCanvas.width=1;sampleCanvas.height=1;sampleContext=sampleCanvas.getContext('2d',{willReadFrequently:true});
    state.ready=true; resize(); fit(data.extent); state.fitScale=state.scale;
    $('loading').hidden=true; $('class-count').textContent=number.format(data.stats.classCount);
    $('feature-count').textContent=number.format(data.stats.featureCount); $('contact-count').textContent=number.format(data.stats.contactCount);
    legend(); issueList(); renderPendingNotes();
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
