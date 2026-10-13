'use strict';

(() => {
  const $ = id => document.getElementById(id);
  const MAP_WIDTH = 4084, MAP_HEIGHT = 3336, MAX_ZOOM = 10;
  const TRANSFORM = [0.003045517499751267, 0, 2.3344767183160524, 0, -0.003045590373802226, 13.896886824009286];
  const STORAGE_KEY = 'ngsa-offline-field-notes-v1';
  const ASSETS = { draft: './assets/current-shapefile-draft.svg', original: './assets/original-reference.jpg' };
  const ACTIONS = {
    'add-feature': 'Add a missing small geology feature',
    'join-features': 'Join two same-color features into one polygon',
    'remove-polygon': 'Remove this polygon',
    'shrink-polygon': 'Make this polygon smaller',
    'expand-polygon': 'Make this polygon bigger',
  };
  const MAP_LABELS = { draft: 'Current shapefile draft', original: 'Original reference map' };
  const state = {
    view: 'draft', split: 50, zoom: 1, panX: 0, panY: 0,
    draft: null, notes: [], captureTarget: null, promptShown: false, mapReady: false,
  };
  let storage = null, storageAvailable = false, drag = null, pinch = null;
  const activePointers = new Map();
  let sampleCanvas, sampleContext;
  const stage = $('map-stage');
  const baseMap = $('base-map');
  const compareMap = $('compare-map');
  const assetImages = { draft: new Image(), original: new Image() };
  const visuals = [$('main-visual'), $('compare-visual')];
  const number = new Intl.NumberFormat('en');

  function setStorageStatus(message, warning = false) {
    $('storage-status').textContent = message;
    $('storage-indicator').classList.toggle('warning', warning);
  }
  function roundCoordinate(value) {
    const rounded = Number(value.toFixed(6));
    return Object.is(rounded, -0) ? 0 : rounded;
  }
  function coordinateAtLocal(screenX, screenY) {
    const rect = stage.getBoundingClientRect();
    const mapX = ((screenX - state.panX) / state.zoom) / rect.width * MAP_WIDTH;
    const mapY = ((screenY - state.panY) / state.zoom) / rect.height * MAP_HEIGHT;
    return {
      mapX, mapY,
      longitude: roundCoordinate(TRANSFORM[0] * mapX + TRANSFORM[1] * mapY + TRANSFORM[2]),
      latitude: roundCoordinate(TRANSFORM[3] * mapX + TRANSFORM[4] * mapY + TRANSFORM[5]),
    };
  }
  function pair(point) { return `${point.longitude.toFixed(6)}, ${point.latitude.toFixed(6)}`; }
  function axis(value, positive, negative) {
    return `${Math.abs(value).toFixed(6)}° ${value < 0 ? negative : positive}`;
  }
  function updateCoordinateReadout(point) {
    $('coordinate-readout').textContent = `${axis(point.longitude, 'E', 'W')}   ${axis(point.latitude, 'N', 'S')}`;
  }
  function safeHex(value) {
    return /^#[0-9a-f]{6}$/i.test(value || '') ? value.toUpperCase() : '';
  }
  function sampleColor(point, sourceName) {
    const image = assetImages[sourceName];
    if (!state.mapReady || !image?.complete || !image.naturalWidth ||
        point.mapX < 0 || point.mapY < 0 || point.mapX >= MAP_WIDTH || point.mapY >= MAP_HEIGHT) return '';
    const x = Math.floor(point.mapX), y = Math.floor(point.mapY);
    try {
      sampleContext.clearRect(0, 0, 1, 1);
      sampleContext.drawImage(image, x, y, 1, 1, 0, 0, 1, 1);
      const [r, g, b] = sampleContext.getImageData(0, 0, 1, 1).data;
      return `#${[r, g, b].map(c => c.toString(16).padStart(2, '0')).join('').toUpperCase()}`;
    } catch {
      return '';
    }
  }
  function deepCopy(value) { return JSON.parse(JSON.stringify(value)); }
  function persistableState() {
    return {
      version: 1, savedAt: new Date().toISOString(), view: state.view, split: state.split,
      zoom: state.zoom, panX: state.panX, panY: state.panY,
      draft: state.draft, notes: state.notes, promptShown: state.promptShown,
    };
  }
  function saveLocal(message = 'Autosaved locally') {
    if (!storageAvailable || !storage) {
      setStorageStatus('Browser storage unavailable · export a backup', true);
      return false;
    }
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(persistableState()));
      const time = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      setStorageStatus(`${message} · ${time}`);
      return true;
    } catch {
      setStorageStatus('Local storage is full or blocked · export a backup', true);
      return false;
    }
  }
  function validPoint(point) {
    if (!point || !Number.isFinite(point.longitude) || !Number.isFinite(point.latitude) ||
        !Number.isFinite(point.mapX) || !Number.isFinite(point.mapY)) return null;
    return { mapX: point.mapX, mapY: point.mapY, longitude: roundCoordinate(point.longitude), latitude: roundCoordinate(point.latitude) };
  }
  function normalizeNote(note) {
    if (!note || !ACTIONS[note.type]) return null;
    const pointA = validPoint(note.pointA);
    if (!pointA) return null;
    const pointB = note.pointB ? validPoint(note.pointB) : null;
    const sourceA = (note.mapSourceA ?? note.mapSource) === 'original' ? 'original' : 'draft';
    const sourceB = (note.mapSourceB ?? note.mapSourceA ?? note.mapSource) === 'original' ? 'original' : 'draft';
    const colorAtPointA = safeHex(note.colorAtPointA);
    return {
      id: String(note.id || `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`),
      type: note.type, pointA, pointB,
      mapSource: sourceA, mapSourceA: sourceA, mapSourceB: sourceB,
      colorCode: safeHex(note.colorCode) || colorAtPointA, colorAtPointA, colorAtPointB: safeHex(note.colorAtPointB),
      colorManuallyEdited: Boolean(note.colorManuallyEdited), confirmedColorMatch: Boolean(note.confirmedColorMatch),
      details: String(note.details || '').slice(0, 4000), createdAt: note.createdAt || new Date().toISOString(),
      updatedAt: note.updatedAt || new Date().toISOString(),
    };
  }
  function normalizeDraft(draft) {
    if (!draft) return null;
    const pointA = validPoint(draft.pointA);
    if (!pointA) return null;
    const sourceA = (draft.mapSourceA ?? draft.mapSource) === 'original' ? 'original' : 'draft';
    const sourceB = (draft.mapSourceB ?? draft.mapSourceA ?? draft.mapSource) === 'original' ? 'original' : 'draft';
    const colorAtPointA = safeHex(draft.colorAtPointA);
    return {
      id: String(draft.id || 'active-draft'),
      type: ACTIONS[draft.type] ? draft.type : '',
      pointA, pointB: draft.pointB ? validPoint(draft.pointB) : null,
      mapSource: sourceA, mapSourceA: sourceA, mapSourceB: sourceB,
      colorCode: safeHex(draft.colorCode) || colorAtPointA, colorAtPointA, colorAtPointB: safeHex(draft.colorAtPointB),
      colorManuallyEdited: Boolean(draft.colorManuallyEdited), confirmedColorMatch: Boolean(draft.confirmedColorMatch),
      details: String(draft.details || '').slice(0, 4000), editing: Boolean(draft.editing),
      createdAt: draft.createdAt || new Date().toISOString(), updatedAt: draft.updatedAt || new Date().toISOString(),
    };
  }
  function restoreState(data) {
    if (!data || data.version !== 1) return false;
    state.view = ['draft', 'original', 'compare'].includes(data.view) ? data.view : 'draft';
    state.split = Math.min(95, Math.max(5, Number(data.split) || 50));
    state.zoom = Math.min(MAX_ZOOM, Math.max(1, Number(data.zoom) || 1));
    state.panX = Number.isFinite(data.panX) ? data.panX : 0;
    state.panY = Number.isFinite(data.panY) ? data.panY : 0;
    state.notes = Array.isArray(data.notes) ? data.notes.map(normalizeNote).filter(Boolean) : [];
    state.draft = normalizeDraft(data.draft);
    state.promptShown = Boolean(data.promptShown && state.notes.length);
    return true;
  }
  function loadLocal() {
    try {
      storage = window.localStorage;
      const testKey = `${STORAGE_KEY}-check`;
      storage.setItem(testKey, 'ok'); storage.removeItem(testKey);
      storageAvailable = true;
    } catch {
      storage = null; storageAvailable = false;
    }
    if (!storageAvailable) {
      setStorageStatus('Browser storage unavailable · use backup files', true);
      return;
    }
    try {
      const raw = storage.getItem(STORAGE_KEY);
      if (raw) {
        const restored = restoreState(JSON.parse(raw));
        setStorageStatus(restored ? `Restored ${state.notes.length} saved note${state.notes.length === 1 ? '' : 's'}` : 'Autosave ready');
      } else setStorageStatus('Autosave ready · browser local storage');
    } catch {
      setStorageStatus('Saved data could not be read · export/import a backup', true);
    }
  }
  function applyTransforms() {
    const transform = `translate3d(${state.panX}px,${state.panY}px,0) scale(${state.zoom})`;
    visuals.forEach(element => { element.style.transform = transform; });
    $('zoom-readout').textContent = `${Math.round(state.zoom * 100)}%`;
    renderMarkers();
  }
  function updateSplit() {
    $('compare-split').value = String(state.split);
    $('compare-window').style.clipPath = `inset(0 0 0 ${state.split}%)`;
    $('compare-divider').style.left = `${state.split}%`;
  }
  function setView(view, persist = true) {
    state.view = view;
    document.querySelectorAll('[data-view]').forEach(button => {
      const active = button.dataset.view === view;
      button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active));
    });
    baseMap.src = view === 'original' || view === 'compare' ? ASSETS.original : ASSETS.draft;
    baseMap.alt = view === 'original' || view === 'compare' ? 'Original geological map reference image' : 'Current cleaned shapefile draft';
    $('compare-window').hidden = view !== 'compare'; $('compare-divider').hidden = view !== 'compare';
    $('compare-settings').hidden = view !== 'compare';
    $('view-label').textContent = view === 'draft' ? 'CURRENT SHAPEFILE DRAFT' : view === 'original' ? 'ORIGINAL REFERENCE MAP' : 'ORIGINAL / DRAFT COMPARISON';
    $('map-caption-title').textContent = view === 'draft' ? 'CURRENT SHAPEFILE DRAFT' : view === 'original' ? 'ORIGINAL REFERENCE MAP' : 'ORIGINAL MAP · DRAFT ON RIGHT';
    $('compare-divider').style.left = `${state.split}%`;
    updateSplit(); applyTransforms(); updateMapHint();
    if (persist) saveLocal();
  }
  function renderMarkers() {
    const layer = $('marker-visual');
    layer.replaceChildren();
    if (!state.draft) return;
    const add = (point, label, className) => {
      if (!point) return;
      const marker = document.createElement('span');
      marker.className = `map-marker ${className}`; marker.textContent = label;
      marker.style.left = `${state.panX + point.mapX / MAP_WIDTH * stage.clientWidth * state.zoom}px`;
      marker.style.top = `${state.panY + point.mapY / MAP_HEIGHT * stage.clientHeight * state.zoom}px`;
      layer.append(marker);
    };
    add(state.draft.pointA, 'A', 'point-a'); add(state.draft.pointB, 'B', 'point-b');
  }
  function updateMapHint() {
    const compareHint = state.view === 'compare' ? ' · left original / right draft' : '';
    if (state.captureTarget === 'pointB') {
      $('map-hint').textContent = `Click to set Point B${compareHint} · pinch to zoom · Escape cancels`;
      stage.setAttribute('aria-label', 'Click the map to choose the second join point. In compare view, the left side is the original and the right is the current draft. Pinch with two fingers to zoom; focus and press Enter or Space to use the map center.');
      $('map-caption-subtitle').textContent = 'Click the map to set Point B.';
    } else {
      $('map-hint').textContent = state.view === 'compare'
        ? 'Left = original · right = draft · source and color captured automatically · pinch to zoom'
        : 'Drag to pan · wheel or pinch to zoom · click a point to add a note';
      stage.setAttribute('aria-label', 'Offline map. Click to capture a location; in compare view, left is original and right is current draft. The clicked map and pixel color are recorded automatically. Drag to pan, pinch with two fingers to zoom, or focus and press Enter or Space to capture the center.');
      $('map-caption-subtitle').textContent = state.view === 'compare'
        ? 'Click left for the original map or right for the draft; source and color are captured automatically.'
        : 'Click a precise location to start an edit note.';
    }
  }
  function updateColorControls() {
    const draft = state.draft;
    if (!draft) return;
    const sourceA = draft.mapSourceA || draft.mapSource;
    const sourceB = draft.mapSourceB || sourceA;
    const sampledColor = safeHex(draft.colorAtPointA);
    $('map-source-label').textContent = MAP_LABELS[sourceA];
    $('color-code').textContent = sampledColor || 'Not sampled';
    $('color-swatch').hidden = !sampledColor;
    $('color-swatch').style.backgroundColor = sampledColor || 'transparent';
    $('point-b-color').textContent = draft.colorAtPointB || 'Not sampled yet';
    $('point-b-map-source').textContent = draft.pointB ? MAP_LABELS[sourceB] : 'Not captured yet';
    const mismatch = Boolean(draft.type === 'join-features' && draft.colorAtPointA && draft.colorAtPointB && draft.colorAtPointA !== draft.colorAtPointB);
    $('join-color-warning').hidden = !mismatch;
    $('confirm-color-wrap').hidden = !mismatch;
    $('confirm-color-match').checked = Boolean(draft.confirmedColorMatch);
    $('color-hint').textContent = sampledColor
      ? `Automatically sampled at Point A from ${MAP_LABELS[sourceA]}.`
      : 'Color not available from this image. Try the included offline launcher and recapture the point.';
  }
  function renderDraft() {
    const draft = state.draft;
    if (!draft) {
      $('note-form').hidden = true; $('editor-empty').hidden = false;
      $('editor-title').textContent = 'Choose a map point'; $('cancel-edit').hidden = true;
      renderMarkers(); updateMapHint(); return;
    }
    $('editor-empty').hidden = true; $('note-form').hidden = false;
    $('editor-title').textContent = draft.editing ? 'Edit saved note' : 'Draft change note';
    $('cancel-edit').hidden = false;
    $('cancel-edit').setAttribute('aria-label', draft.editing ? 'Cancel changes to this saved note' : 'Discard this unsaved note');
    $('point-longitude').textContent = axis(draft.pointA.longitude, 'E', 'W');
    $('point-latitude').textContent = axis(draft.pointA.latitude, 'N', 'S');
    $('edit-type').value = draft.type || '';
    $('extra-details').value = draft.details || '';
    $('join-fields').hidden = draft.type !== 'join-features';
    $('point-b-coordinate').textContent = draft.pointB ? pair(draft.pointB) : 'Not captured yet';
    $('copy-point-b').hidden = !draft.pointB;
    $('pick-point-b').textContent = state.captureTarget === 'pointB' ? 'Waiting for Point B · cancel' : draft.pointB ? 'Choose Point B again' : 'Pick the second point on the map';
    $('copy-point-a').textContent = 'Copy Point A coordinates'; $('copy-point-b').textContent = 'Copy Point B coordinates';
    updateColorControls(); updateValidation(); renderMarkers(); updateMapHint();
  }
  function updateValidation() {
    const draft = state.draft;
    if (!draft) return;
    const mismatch = Boolean(draft.type === 'join-features' && draft.colorAtPointA && draft.colorAtPointB && draft.colorAtPointA !== draft.colorAtPointB);
    const needsB = draft.type === 'join-features' && !draft.pointB;
    const confirmed = !mismatch || $('confirm-color-match').checked;
    $('save-note').disabled = !draft.type || needsB || !confirmed;
    if (draft.type && !needsB && confirmed) $('form-message').hidden = true;
  }
  function sourceAtScreen(localX) {
    if (state.view === 'original') return 'original';
    if (state.view === 'draft') return 'draft';
    const rect = stage.getBoundingClientRect();
    return localX < rect.width * state.split / 100 ? 'original' : 'draft';
  }
  function beginDraft(point, sourceName) {
    if (state.draft) {
      const message = state.draft.editing
        ? 'Discard your unsaved changes to this saved note and start a new note?'
        : 'Discard this unsaved note and start a new one?';
      if (!window.confirm(message)) { renderDraft(); return; }
    }
    const color = sampleColor(point, sourceName);
    state.draft = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, type: '', pointA: point, pointB: null,
      mapSource: sourceName, mapSourceA: sourceName, mapSourceB: sourceName,
      colorCode: color, colorAtPointA: color, colorAtPointB: '',
      colorManuallyEdited: false, confirmedColorMatch: false, details: '', editing: false,
      createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
    };
    state.captureTarget = null; state.promptShown = false;
    updateCoordinateReadout(point); renderDraft(); renderPrompt(); saveLocal('Draft autosaved');
    $('announcement').textContent = `New edit note at longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)}.`;
  }
  function capturePointB(point, sourceName) {
    const draft = state.draft;
    if (!draft) return beginDraft(point, sourceName);
    draft.pointB = point; draft.mapSourceB = sourceName;
    draft.colorAtPointB = sampleColor(point, sourceName);
    draft.confirmedColorMatch = false; state.captureTarget = null;
    updateCoordinateReadout(point); renderDraft(); saveLocal('Point B autosaved');
    $('announcement').textContent = `Point B recorded at longitude ${point.longitude.toFixed(6)}, latitude ${point.latitude.toFixed(6)}.`;
  }
  function capturePointAt(localX, localY) {
    if (!state.mapReady) return;
    const point = coordinateAtLocal(localX, localY);
    updateCoordinateReadout(point);
    const sourceName = sourceAtScreen(localX);
    if (state.captureTarget === 'pointB') capturePointB(point, sourceName);
    else beginDraft(point, sourceName);
  }
  function cancelDraft() {
    if (!state.draft) return;
    const message = state.draft.editing ? 'Discard changes to this note? The saved version will remain.' : 'Discard this unsaved point note?';
    if (!window.confirm(message)) return;
    state.draft = null; state.captureTarget = null;
    renderDraft(); saveLocal();
  }
  function mapPointerDown(event) {
    if ((event.pointerType === 'mouse' && event.button !== 0) || event.target.closest('button')) return;
    event.preventDefault();
    try { stage.setPointerCapture(event.pointerId); } catch { /* Some browsers may decline capture during a cancelled touch. */ }
    activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY, type: event.pointerType });
    if (event.pointerType === 'touch') {
      const touches = [...activePointers.entries()].filter(([, point]) => point.type === 'touch');
      if (touches.length >= 2 && !pinch) {
        const [[idA, a], [idB, b]] = touches;
        const rect = stage.getBoundingClientRect();
        const midX = (a.x + b.x) / 2 - rect.left, midY = (a.y + b.y) / 2 - rect.top;
        pinch = {
          ids: [idA, idB], startDistance: Math.max(1, Math.hypot(b.x - a.x, b.y - a.y)),
          startZoom: state.zoom, anchorX: (midX - state.panX) / state.zoom,
          anchorY: (midY - state.panY) / state.zoom,
        };
        drag = null;
        return;
      }
    }
    if (pinch) return;
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY, moved: false };
  }
  function mapPointerMove(event) {
    const rect = stage.getBoundingClientRect();
    const localX = event.clientX - rect.left, localY = event.clientY - rect.top;
    const tracked = activePointers.get(event.pointerId);
    if (tracked) { tracked.x = event.clientX; tracked.y = event.clientY; }
    if (pinch) {
      const points = pinch.ids.map(id => activePointers.get(id));
      if (points.every(Boolean)) {
        const [a, b] = points;
        const midX = (a.x + b.x) / 2 - rect.left, midY = (a.y + b.y) / 2 - rect.top;
        const distance = Math.max(1, Math.hypot(b.x - a.x, b.y - a.y));
        const factor = distance / pinch.startDistance;
        const next = Math.max(1, Math.min(MAX_ZOOM, pinch.startZoom * factor));
        state.zoom = next;
        state.panX = midX - pinch.anchorX * next; state.panY = midY - pinch.anchorY * next;
        applyTransforms();
        if (state.mapReady) updateCoordinateReadout(coordinateAtLocal(midX, midY));
      }
      return;
    }
    if (drag && drag.id === event.pointerId) {
      const dx = event.clientX - drag.x, dy = event.clientY - drag.y;
      if (Math.hypot(dx, dy) > 4) drag.moved = true;
      if (drag.moved) {
        state.panX = drag.panX + dx; state.panY = drag.panY + dy; applyTransforms();
      }
      return;
    }
    if (state.mapReady) updateCoordinateReadout(coordinateAtLocal(localX, localY));
  }
  function mapPointerUp(event) {
    if (pinch && pinch.ids.includes(event.pointerId)) {
      pinch = null; drag = null; activePointers.clear(); saveLocal(); return;
    }
    activePointers.delete(event.pointerId);
    if (!drag || drag.id !== event.pointerId) return;
    const moved = drag.moved; drag = null;
    const rect = stage.getBoundingClientRect();
    if (moved) { saveLocal(); return; }
    if (!state.mapReady) return;
    const localX = event.clientX - rect.left, localY = event.clientY - rect.top;
    capturePointAt(localX, localY);
  }
  function mapPointerCancel(event) {
    if (pinch && pinch.ids.includes(event.pointerId)) {
      pinch = null; drag = null; activePointers.clear(); saveLocal(); return;
    }
    activePointers.delete(event.pointerId);
    if (drag?.id === event.pointerId) { if (drag.moved) saveLocal(); drag = null; }
  }
  function zoomAt(factor, localX, localY) {
    const next = Math.max(1, Math.min(MAX_ZOOM, state.zoom * factor));
    const mapX = (localX - state.panX) / state.zoom, mapY = (localY - state.panY) / state.zoom;
    state.panX = localX - mapX * next; state.panY = localY - mapY * next; state.zoom = next;
    applyTransforms(); saveLocal();
  }
  function fitMap() {
    state.zoom = 1; state.panX = 0; state.panY = 0; applyTransforms(); saveLocal();
  }
  function addQueueText(parent, label, value) {
    const p = document.createElement('p'), span = document.createElement('span'), strong = document.createElement('strong');
    span.textContent = label; strong.textContent = value || 'Not provided'; p.append(span, strong); parent.append(p);
  }
  function renderQueue() {
    const container = $('saved-notes'); container.replaceChildren();
    $('note-count').textContent = String(state.notes.length);
    $('clear-notes').disabled = !state.notes.length && !state.draft;
    $('copy-all-notes').disabled = !state.notes.length;
    if (!state.notes.length) {
      const empty = document.createElement('div'); empty.className = 'no-notes'; empty.textContent = 'No saved change notes yet.'; container.append(empty);
      return;
    }
    state.notes.forEach((note, index) => {
      const article = document.createElement('article'); article.className = 'saved-note';
      const header = document.createElement('div'); header.className = 'saved-note-heading';
      const titleBlock = document.createElement('div'), order = document.createElement('small'), title = document.createElement('strong');
      order.textContent = `EDIT ${String(index + 1).padStart(2, '0')}`; title.textContent = ACTIONS[note.type]; titleBlock.append(order, title);
      const actions = document.createElement('div'); actions.className = 'note-actions';
      const edit = document.createElement('button'); edit.type = 'button'; edit.textContent = 'Edit'; edit.addEventListener('click', () => editSavedNote(note.id));
      const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = 'Remove'; remove.addEventListener('click', () => removeSavedNote(note.id));
      actions.append(edit, remove); header.append(titleBlock, actions); article.append(header);
      addQueueText(article, 'Point A', pair(note.pointA));
      addQueueText(article, 'Point A map', MAP_LABELS[note.mapSourceA || note.mapSource]);
      addQueueText(article, 'Point A sampled color', note.colorAtPointA || note.colorCode || 'Not sampled');
      if (note.pointB) {
        addQueueText(article, 'Point B', pair(note.pointB));
        addQueueText(article, 'Point B map', MAP_LABELS[note.mapSourceB || note.mapSourceA || note.mapSource]);
        addQueueText(article, 'Point B sampled color', note.colorAtPointB || 'Not sampled');
        const samplesMatch = note.colorAtPointA && note.colorAtPointB && note.colorAtPointA === note.colorAtPointB;
        addQueueText(article, 'Color check', samplesMatch ? 'Samples match' : note.confirmedColorMatch ? 'Match confirmed' : 'Review needed');
      }
      if (note.details) addQueueText(article, 'Details', note.details);
      container.append(article);
    });
  }
  function promptText(notes) {
    const result = [
      'Please update the Nigeria geological map shapefile using the field-review notes below.',
      'Coordinates are longitude, latitude in decimal degrees to six places. WGS 84 is assumed by the viewer, but the original source datum is unconfirmed; check alignment before editing.',
      'The map source and pixel color are captured automatically from the map side clicked for each point. Sampled colors are visual references, not guaranteed geological class assignments.',
      'Apply only the requested changes, preserve valid polygon topology and shared boundaries, and flag any ambiguity rather than guessing.',
      '',
    ];
    notes.forEach((note, index) => {
      result.push(`${index + 1}. ${ACTIONS[note.type]}`);
      result.push(`   - Point A coordinate (longitude, latitude): ${pair(note.pointA)}`);
      result.push(`   - Requested change: ${ACTIONS[note.type]}`);
      result.push(`   - Point A reference map: ${MAP_LABELS[note.mapSourceA || note.mapSource]}`);
      result.push(`   - Point A color code (automatically sampled): ${note.colorAtPointA || note.colorCode || 'Not sampled'}`);
      if (note.pointB) {
        result.push(`   - Point B coordinate (longitude, latitude): ${pair(note.pointB)}`);
        result.push(`   - Point B reference map: ${MAP_LABELS[note.mapSourceB || note.mapSourceA || note.mapSource]}`);
        result.push(`   - Point B color code (automatically sampled): ${note.colorAtPointB || 'Not sampled'}`);
        const match = note.colorAtPointA && note.colorAtPointB && note.colorAtPointA === note.colorAtPointB;
        result.push(`   - Color consistency: ${match ? 'same sampled color' : note.confirmedColorMatch ? 'user confirms both locations share the intended geological color despite different samples' : 'not fully verified; please review'}`);
        result.push('   - Join request: treat both locations as one polygon, retaining the shared geological color and attributes where appropriate.');
      }
      if (note.details) result.push(`   - Additional details: ${note.details}`);
      result.push('');
    });
    return result.join('\n').trim();
  }
  function renderPrompt() {
    if (state.promptShown && state.notes.length) {
      $('generated-prompt').value = promptText(state.notes); $('prompt-wrap').hidden = false;
    } else {
      $('generated-prompt').value = ''; $('prompt-wrap').hidden = true;
    }
  }
  function editSavedNote(id) {
    const note = state.notes.find(item => item.id === id);
    if (!note) return;
    if (state.draft && !window.confirm('Discard your current in-progress note and edit this saved note?')) return;
    state.draft = { ...deepCopy(note), editing: true };
    state.captureTarget = null; renderDraft(); saveLocal();
    $('editor-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function removeSavedNote(id) {
    state.notes = state.notes.filter(note => note.id !== id);
    if (state.draft?.id === id && state.draft.editing) state.draft = null;
    state.promptShown = false; renderQueue(); renderPrompt(); renderDraft(); saveLocal();
  }
  function saveDraft(event) {
    event?.preventDefault();
    const draft = state.draft;
    if (!draft) return;
    if (!draft.type) { $('form-message').textContent = 'Choose one of the five edit types first.'; $('form-message').hidden = false; return; }
    if (draft.type === 'join-features' && !draft.pointB) { $('form-message').textContent = 'Choose Point B to complete this join request.'; $('form-message').hidden = false; return; }
    const mismatch = draft.type === 'join-features' && draft.colorAtPointA && draft.colorAtPointB && draft.colorAtPointA !== draft.colorAtPointB;
    if (mismatch && !draft.confirmedColorMatch) { $('form-message').textContent = 'Confirm that both points are the same intended geological color before saving.'; $('form-message').hidden = false; return; }
    draft.colorCode = safeHex(draft.colorAtPointA); draft.details = $('extra-details').value.trim(); draft.updatedAt = new Date().toISOString();
    const saved = normalizeNote(draft);
    if (draft.editing) {
      const index = state.notes.findIndex(item => item.id === draft.id);
      if (index >= 0) state.notes[index] = saved;
      else state.notes.push(saved);
    } else state.notes.push(saved);
    state.draft = null; state.captureTarget = null; state.promptShown = false;
    renderQueue(); renderPrompt(); renderDraft();
    const stored = saveLocal();
    $('copy-status').textContent = stored ? `Edit saved on this device · ${state.notes.length} pending note${state.notes.length === 1 ? '' : 's'}.` : 'Edit added for this session. Export a JSON backup because local storage is unavailable.';
    $('announcement').textContent = `Edit note saved. ${state.notes.length} pending changes.`;
  }
  function clearAllNotes() {
    if (!state.notes.length && !state.draft) return;
    if (!window.confirm('Delete all saved notes and the current in-progress note from this device? This cannot be undone.')) return;
    state.notes = []; state.draft = null; state.captureTarget = null; state.promptShown = false;
    renderQueue(); renderPrompt(); renderDraft(); saveLocal('All notes cleared');
  }
  async function copyText(text) {
    try {
      if (navigator.clipboard?.writeText) { await navigator.clipboard.writeText(text); return true; }
    } catch { /* A local file may not have clipboard permissions. */ }
    const field = document.createElement('textarea'); field.value = text; field.setAttribute('readonly', '');
    field.style.position = 'fixed'; field.style.left = '-10000px'; document.body.append(field); field.select();
    let copied = false; try { copied = document.execCommand('copy'); } catch { copied = false; }
    field.remove(); return copied;
  }
  async function copyAllNotes() {
    if (!state.notes.length) return;
    state.promptShown = true; renderPrompt(); saveLocal();
    const copied = await copyText($('generated-prompt').value);
    $('copy-status').textContent = copied
      ? 'All saved notes copied. The complete prompt is also shown below.'
      : 'Clipboard access is blocked. The complete prompt is shown below so you can select and copy it.';
    $('announcement').textContent = copied ? 'All saved change notes copied to the clipboard.' : 'The correction prompt is displayed below.';
  }
  function downloadJson(filename, data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob), anchor = document.createElement('a');
    anchor.href = url; anchor.download = filename; anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1500);
  }
  function exportBackup() {
    const payload = { ...persistableState(), exportedAt: new Date().toISOString(), app: 'Offline Field Notes' };
    downloadJson(`geology-field-notes-${new Date().toISOString().slice(0, 10)}.json`, payload);
    setStorageStatus('Backup downloaded');
  }
  async function importBackup(event) {
    const input = event.currentTarget;
    const file = input.files?.[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      if (data.version !== 1 || !Array.isArray(data.notes)) throw new Error('This is not a compatible field-notes backup.');
      if (!window.confirm(`Replace this device's saved notes with the ${data.notes.length} note(s) from the backup?`)) return;
      restoreState(data); state.captureTarget = null;
      setView(state.view, false); $('compare-split').value = String(state.split);
      renderQueue(); renderPrompt(); renderDraft(); applyTransforms();
      saveLocal('Backup imported');
      $('copy-status').textContent = 'Backup imported and saved locally.';
    } catch (error) {
      window.alert(error.message || 'The backup could not be read.');
    } finally {
      input.value = '';
    }
  }
  function escapeCapture() {
    if (state.captureTarget !== 'pointB') return false;
    state.captureTarget = null; renderDraft(); saveLocal(); return true;
  }
  function downloadPointCoordinate(point, label) {
    copyText(pair(point)).then(copied => {
      $('copy-status').textContent = copied ? `${label} coordinate copied.` : `${label}: ${pair(point)} · select from the coordinate fields to copy.`;
    });
  }

  function applyInitialState() {
    loadLocal();
    setView(state.view, false); updateSplit(); applyTransforms(); renderQueue(); renderPrompt(); renderDraft();
    if (state.notes.length) $('copy-status').textContent = `Restored ${state.notes.length} saved note${state.notes.length === 1 ? '' : 's'} from this browser.`;
  }
  function loadImages() {
    const entries = Object.entries(ASSETS).map(([key, src]) => new Promise(resolve => {
      const image = new Image();
      image.onload = () => { assetImages[key] = image; resolve(true); };
      image.onerror = () => { assetImages[key] = null; resolve(false); };
      image.src = src;
    }));
    return Promise.all(entries);
  }

  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  $('compare-split').addEventListener('input', event => {
    state.split = Number(event.currentTarget.value); updateSplit(); saveLocal();
  });
  $('zoom-in').addEventListener('click', () => zoomAt(1.35, stage.clientWidth / 2, stage.clientHeight / 2));
  $('zoom-out').addEventListener('click', () => zoomAt(1 / 1.35, stage.clientWidth / 2, stage.clientHeight / 2));
  $('fit-map').addEventListener('click', fitMap); $('reset-view').addEventListener('click', fitMap);
  stage.addEventListener('pointerdown', mapPointerDown);
  stage.addEventListener('pointermove', mapPointerMove);
  stage.addEventListener('pointerup', mapPointerUp);
  stage.addEventListener('pointercancel', mapPointerCancel);
  stage.addEventListener('focus', () => {
    if (state.mapReady) updateCoordinateReadout(coordinateAtLocal(stage.clientWidth / 2, stage.clientHeight / 2));
  });
  stage.addEventListener('keydown', event => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault(); capturePointAt(stage.clientWidth / 2, stage.clientHeight / 2);
  });
  stage.addEventListener('wheel', event => {
    event.preventDefault(); const rect = stage.getBoundingClientRect();
    zoomAt(Math.exp(-event.deltaY * .0012), event.clientX - rect.left, event.clientY - rect.top);
  }, { passive: false });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') escapeCapture(); });
  $('edit-type').addEventListener('change', event => {
    if (!state.draft) return;
    state.draft.type = event.currentTarget.value;
    if (state.draft.type !== 'join-features') state.captureTarget = null;
    $('join-fields').hidden = state.draft.type !== 'join-features';
    updateColorControls(); updateMapHint(); updateValidation(); saveLocal('Draft autosaved');
  });
  $('extra-details').addEventListener('input', event => {
    if (state.draft) { state.draft.details = event.currentTarget.value; saveLocal('Draft autosaved'); }
  });
  $('confirm-color-match').addEventListener('change', event => {
    if (state.draft) { state.draft.confirmedColorMatch = event.currentTarget.checked; updateValidation(); saveLocal('Draft autosaved'); }
  });
  $('pick-point-b').addEventListener('click', () => {
    if (!state.draft || state.draft.type !== 'join-features') return;
    state.captureTarget = state.captureTarget === 'pointB' ? null : 'pointB';
    renderDraft(); saveLocal();
  });
  $('copy-point-a').addEventListener('click', () => { if (state.draft?.pointA) downloadPointCoordinate(state.draft.pointA, 'Point A'); });
  $('copy-point-b').addEventListener('click', () => { if (state.draft?.pointB) downloadPointCoordinate(state.draft.pointB, 'Point B'); });
  $('note-form').addEventListener('submit', saveDraft);
  $('discard-draft').addEventListener('click', cancelDraft);
  $('cancel-edit').addEventListener('click', cancelDraft);
  $('clear-notes').addEventListener('click', clearAllNotes);
  $('copy-all-notes').addEventListener('click', copyAllNotes);
  $('export-backup').addEventListener('click', exportBackup);
  $('import-backup').addEventListener('change', importBackup);
  $('generated-prompt').addEventListener('click', event => event.currentTarget.select());
  window.addEventListener('resize', renderMarkers);
  window.addEventListener('beforeunload', () => saveLocal());

  applyInitialState();
  sampleCanvas = document.createElement('canvas'); sampleCanvas.width = 1; sampleCanvas.height = 1;
  sampleContext = sampleCanvas.getContext('2d', { willReadFrequently: true });
  $('map-loading').hidden = false;
  loadImages().then(results => {
    state.mapReady = true; $('map-loading').hidden = true;
    if (results.some(ok => !ok)) {
      $('map-caption-subtitle').textContent = 'A map picture could not be loaded. Check the assets folder or re-extract the offline package.';
      setStorageStatus('Map asset missing · coordinates still work', true);
    }
    if (state.draft) {
      const sourceA = state.draft.mapSourceA || state.draft.mapSource;
      const sourceB = state.draft.mapSourceB || sourceA;
      if (!state.draft.colorAtPointA) state.draft.colorAtPointA = sampleColor(state.draft.pointA, sourceA);
      if (state.draft.pointB && !state.draft.colorAtPointB) state.draft.colorAtPointB = sampleColor(state.draft.pointB, sourceB);
      state.draft.colorCode = safeHex(state.draft.colorAtPointA);
      renderDraft();
      saveLocal('Draft restored');
    }
  });
})();
