const $ = (id) => document.getElementById(id);

let state = {
  config: null,
  actions: [],
  diag: null,
  events: [],
  selectedButton: '1',
  activeView: 'control',
  visualEventsClearedAt: null,
  actionFilter: '',
  saveTimer: null,
  dirty: false,
};

const icons = {
  layout: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
  layers: '<svg viewBox="0 0 24 24"><path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 13 9 5 9-5"/><path d="m3 18 9 5 9-5"/></svg>',
  activity: '<svg viewBox="0 0 24 24"><path d="M3 12h4l2-7 4 14 2-7h6"/></svg>',
  book: '<svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H21"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H21v20H6.5A2.5 2.5 0 0 1 4 19.5z"/></svg>',
  save: '<svg viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/></svg>',
  refresh: '<svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 16h5v5"/><path d="M3 12A9 9 0 0 1 18 5.3L21 8"/><path d="M21 8h-5V3"/></svg>',
  zap: '<svg viewBox="0 0 24 24"><path d="M13 2 3 14h8l-1 8 10-12h-8l1-8Z"/></svg>',
  plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M5 12h14"/></svg>',
  trash: '<svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 15H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>',
  copy: '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><rect x="2" y="2" width="13" height="13" rx="2"/></svg>',
  play: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4V8Z"/></svg>',
  'skip-forward': '<svg viewBox="0 0 24 24"><path d="m5 4 10 8L5 20V4Z"/><path d="M19 5v14"/></svg>',
  'skip-back': '<svg viewBox="0 0 24 24"><path d="m19 20-10-8 10-8v16Z"/><path d="M5 19V5"/></svg>',
  'volume-2': '<svg viewBox="0 0 24 24"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>',
  'volume-1': '<svg viewBox="0 0 24 24"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M16 9a4 4 0 0 1 0 6"/></svg>',
  'volume-x': '<svg viewBox="0 0 24 24"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="m19 9-6 6"/><path d="m13 9 6 6"/></svg>',
  'mic-off': '<svg viewBox="0 0 24 24"><path d="m2 2 20 20"/><path d="M9 9v3a3 3 0 0 0 5.12 2.12"/><path d="M15 9.34V5a3 3 0 0 0-5.94-.6"/><path d="M17 11v1a5 5 0 0 1-.54 2.26"/><path d="M7 11v1a5 5 0 0 0 5 5"/><path d="M12 19v3"/></svg>',
  globe: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20"/><path d="M12 2a15 15 0 0 0 0 20"/></svg>',
  broadcast: '<svg viewBox="0 0 24 24"><path d="M12 18a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M17.7 20.7a9 9 0 1 0-11.4 0"/><path d="M15.5 8.5a5 5 0 0 0-7 0"/></svg>',
  code: '<svg viewBox="0 0 24 24"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/><path d="m14 4-4 16"/></svg>',
  message: '<svg viewBox="0 0 24 24"><path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/></svg>',
  music: '<svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  send: '<svg viewBox="0 0 24 24"><path d="m22 2-7 20-4-9-9-4 20-7Z"/><path d="M22 2 11 13"/></svg>',
  terminal: '<svg viewBox="0 0 24 24"><path d="m4 17 6-6-6-6"/><path d="M12 19h8"/></svg>',
  'terminal-square': '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3"/><path d="M13 15h4"/></svg>',
  folder: '<svg viewBox="0 0 24 24"><path d="M3 6h7l2 2h9v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6Z"/></svg>',
  'folder-open': '<svg viewBox="0 0 24 24"><path d="M3 7h6l2 2h10v3"/><path d="m3 18 3-8h16l-3 8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/></svg>',
  camera: '<svg viewBox="0 0 24 24"><path d="M14 5h-4L8 8H4a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-4l-2-3Z"/><circle cx="12" cy="14" r="3"/></svg>',
  link: '<svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 1 0-7.07-7.07l-1.5 1.5"/><path d="M14 11a5 5 0 0 0-7.07 0l-3 3A5 5 0 0 0 11 21.07l1.5-1.5"/></svg>',
  keyboard: '<svg viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/></svg>',
  text: '<svg viewBox="0 0 24 24"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg>',
  record: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>',
  stop: '<svg viewBox="0 0 24 24"><rect x="7" y="7" width="10" height="10" rx="1"/></svg>',
  radio: '<svg viewBox="0 0 24 24"><path d="M4.9 19.1a10 10 0 0 1 0-14.2"/><path d="M7.8 16.2a6 6 0 0 1 0-8.4"/><circle cx="12" cy="12" r="2"/><path d="M16.2 7.8a6 6 0 0 1 0 8.4"/><path d="M19.1 4.9a10 10 0 0 1 0 14.2"/></svg>',
};

function icon(name) {
  return icons[name] || icons.zap;
}

function hydrateStaticIcons() {
  document.querySelectorAll('[data-icon]').forEach((el) => {
    el.innerHTML = icon(el.dataset.icon);
  });
}

async function api(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
}

function profile() {
  return state.config?.profiles?.[state.config.active_profile];
}

function actionById(id) {
  return state.actions.find((a) => a.id === id) || { id, name: id || 'Sin acción', category: 'Custom', icon: 'zap', fields: [] };
}

function toast(message) {
  const el = $('toast');
  el.textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2400);
}

function renderProfileSelect() {
  const select = $('profileSelect');
  select.innerHTML = Object.entries(state.config.profiles).map(([id, p]) => `
    <option value="${esc(id)}" ${id === state.config.active_profile ? 'selected' : ''}>${esc(p.name || id)}</option>
  `).join('');
  $('sideProfile').textContent = profile()?.name || state.config.active_profile;
}

function renderDeck() {
  const p = profile();
  const buttons = p?.buttons || {};
  $('deckGrid').innerHTML = Object.entries(buttons).map(([id, btn]) => {
    const meta = actionById(btn.action);
    return `
      <button class="macro ${state.selectedButton === id ? 'active' : ''}" data-button="${esc(id)}">
        <div class="macro-top"><span>BTN ${esc(id)}</span><span>${esc(btn.key || `F${12 + Number(id)}`)}</span></div>
        <div class="macro-icon">${icon(meta.icon)}</div>
        <div>
          <div class="macro-label">${esc(btn.label || `Botón ${id}`)}</div>
          <div class="macro-action">${esc(meta.name)}</div>
        </div>
      </button>
    `;
  }).join('');
  document.querySelectorAll('.macro').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.selectedButton = btn.dataset.button;
      renderAll();
    });
  });
}

function renderActionSelect() {
  const current = profile()?.buttons?.[state.selectedButton]?.action || '';
  const filter = (state.actionFilter || '').trim().toLowerCase();
  const filtered = filter
    ? state.actions.filter((a) => `${a.name} ${a.id} ${a.category} ${a.description || ''}`.toLowerCase().includes(filter))
    : state.actions;
  const grouped = filtered.reduce((acc, a) => {
    (acc[a.category] ||= []).push(a);
    return acc;
  }, {});
  const html = Object.entries(grouped).map(([cat, actions]) => `
    <optgroup label="${esc(cat)}">
      ${actions.map((a) => `<option value="${esc(a.id)}" ${a.id === current ? 'selected' : ''}>${esc(a.name)}</option>`).join('')}
    </optgroup>
  `).join('');
  $('actionSelect').innerHTML = html || '<option value="">Sin coincidencias — limpiá el filtro</option>';
  // Si la acción actual quedó filtrada, igual mostrarla para no perder el valor
  if (current && ![...$('actionSelect').options].some((o) => o.value === current)) {
    const meta = actionById(current);
    const opt = document.createElement('option');
    opt.value = current;
    opt.textContent = `${meta.name} (actual)`;
    opt.selected = true;
    $('actionSelect').appendChild(opt);
  }
}

function renderEditor() {
  const p = profile();
  const btn = p?.buttons?.[state.selectedButton];
  if (!btn) return;
  const meta = actionById(btn.action);
  $('editorTitle').textContent = `Botón ${state.selectedButton}`;
  $('labelInput').value = btn.label || '';
  $('keyInput').value = btn.key || '';
  renderActionSelect();
  $('actionInfo').innerHTML = `
    <strong>${icon(meta.icon)} ${esc(meta.name)}</strong><br>
    <span>${esc(meta.description || 'Acción personalizada.')}</span>
  `;
  const fields = meta.fields || [];
  $('paramsBox').innerHTML = fields.length ? fields.map((field) => {
    const value = btn.params?.[field.name] ?? '';
    const common = `data-param="${esc(field.name)}" placeholder="${esc(field.placeholder || '')}"`;
    if (field.type === 'textarea') {
      return `<label class="field"><span>${esc(field.label)}</span><textarea ${common}>${esc(value)}</textarea></label>`;
    }
    return `<label class="field"><span>${esc(field.label)}</span><input type="${esc(field.type || 'text')}" value="${esc(value)}" ${common}></label>`;
  }).join('') : '<div class="hint">Esta acción no necesita parámetros extra.</div>';
}

function renderStatus() {
  const diag = state.diag || {};
  const dot = $('statusDot');
  dot.className = `dot ${diag.listener_ok ? 'ok' : 'err'}`;
  $('statusText').textContent = diag.listener_ok ? 'Conectado y escuchando' : 'Listener con problema';
  $('sideKey').textContent = diag.last_key || '—';
  $('sideButton').textContent = diag.last_button || '—';
  $('listenerChip').textContent = `${diag.listener_backend || 'sin listener'} · ${diag.session || 'sesión?'}`;
}

function renderEvents() {
  const events = state.visualEventsClearedAt ? [] : state.events;
  $('eventsList').innerHTML = events.map((e) => `
    <div class="event ${esc(e.kind)}"><strong>${esc(e.time)}</strong> · ${esc(e.message)}</div>
  `).join('') || '<div class="event">Sin eventos visibles. Tocá un botón físico o probá una macro.</div>';
}

function renderProfiles() {
  $('profileList').innerHTML = Object.entries(state.config.profiles).map(([id, p]) => `
    <button class="profile-item ${id === state.config.active_profile ? 'active' : ''}" data-profile="${esc(id)}">
      <span><strong>${esc(p.name || id)}</strong><small>${Object.keys(p.buttons || {}).length} botones · ${esc(id)}</small></span>
      <span>${id === state.config.active_profile ? 'Activo' : 'Usar'}</span>
    </button>
  `).join('');
  document.querySelectorAll('.profile-item').forEach((item) => {
    item.addEventListener('click', async () => {
      patchSelectedButton();
      state.config.active_profile = item.dataset.profile;
      state.selectedButton = '1';
      markDirty();
      renderAll();
      try { await persistConfig(true); await loadAll(); } catch (e) { toast(`No se pudo cambiar perfil: ${e.message}`); }
    });
  });
  $('profileNameInput').value = profile()?.name || '';
}

function renderDiagnostics() {
  const d = state.diag || {};
  const deps = d.dependencies || {};
  $('diagGrid').innerHTML = `
    <dt>Versión</dt><dd>${esc(d.version)}</dd>
    <dt>Sistema</dt><dd>${esc(d.os)} · ${esc(d.platform)}</dd>
    <dt>Sesión</dt><dd>${esc(d.session)} / ${esc(d.desktop)}</dd>
    <dt>Backend</dt><dd>${esc(d.listener_backend)}</dd>
    <dt>Última tecla</dt><dd>${esc(d.last_key || '—')} <span class="muted">raw: ${esc(d.last_raw_key || '—')}</span></dd>
    <dt>Último botón</dt><dd>${esc(d.last_button || '—')}</dd>
    <dt>Última acción</dt><dd>${esc(d.last_action || '—')}</dd>
    <dt>Último error</dt><dd>${esc(d.last_error || '—')}</dd>
    <dt>Config</dt><dd>${esc(d.config_path || '—')}</dd>
  `;
  $('depsGrid').innerHTML = Object.entries(deps).map(([name, ok]) => `
    <div class="dep ${ok ? 'ok' : 'miss'}"><span>${esc(name)}</span><span>${ok ? 'OK' : 'Falta'}</span></div>
  `).join('');
}

function renderAll() {
  if (!state.config) return;
  renderProfileSelect();
  renderDeck();
  renderEditor();
  renderStatus();
  renderEvents();
  renderProfiles();
  renderDiagnostics();
  updateSaveIndicator();
  const search = $('actionSearch');
  if (search && search.value !== state.actionFilter) search.value = state.actionFilter;
}

async function loadAll() {
  const [config, actions, diag, events] = await Promise.all([
    api('/api/config'),
    api('/api/actions'),
    api('/api/diagnostics'),
    api('/api/events'),
  ]);
  state.config = config;
  state.actions = actions;
  state.diag = diag;
  state.events = events;
  state.dirty = false;
  if (!profile()?.buttons?.[state.selectedButton]) state.selectedButton = '1';
  renderAll();
}

function patchSelectedButton() {
  const btn = profile()?.buttons?.[state.selectedButton];
  if (!btn) return;
  btn.label = $('labelInput').value.trim() || `Botón ${state.selectedButton}`;
  btn.key = $('keyInput').value.trim() || `F${12 + Number(state.selectedButton)}`;
  btn.action = $('actionSelect').value;
  const meta = actionById(btn.action);
  btn.params = {};
  (meta.fields || []).forEach((field) => {
    const input = document.querySelector(`[data-param="${CSS.escape(field.name)}"]`);
    if (input) btn.params[field.name] = input.value;
  });
}

async function persistConfig(silent = false) {
  patchSelectedButton();
  await api('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state.config),
  });
  state.dirty = false;
  updateSaveIndicator();
  if (!silent) toast('Configuración guardada');
}

function updateSaveIndicator() {
  const btn = $('saveBtn');
  if (!btn) return;
  btn.classList.toggle('dirty', !!state.dirty);
  btn.innerHTML = state.dirty
    ? '<span data-icon="save"></span> Guardar *'
    : '<span data-icon="save"></span> Guardar';
  hydrateStaticIcons();
}

function markDirty() {
  state.dirty = true;
  updateSaveIndicator();
  clearTimeout(state.saveTimer);
  // Autoguardado con debounce: evita perder perfiles/cambios si se cierra la pestaña
  state.saveTimer = setTimeout(() => {
    persistConfig(true).then(() => toast('Autoguardado OK')).catch((e) => toast(`Autoguardado falló: ${e.message}`));
  }, 1500);
}

async function saveConfig() {
  clearTimeout(state.saveTimer);
  await persistConfig(false);
  state.visualEventsClearedAt = null;
  await loadAll();
}

async function testSelectedButton() {
  patchSelectedButton();
  const res = await api(`/api/test/${Number(state.selectedButton)}`, { method: 'POST' });
  toast(res.ok ? 'Macro enviada' : 'No se pudo probar');
  setTimeout(loadAll, 350);
}

function switchView(name) {
  state.activeView = name;
  document.querySelectorAll('.nav-tab').forEach((tab) => tab.classList.toggle('active', tab.dataset.view === name));
  document.querySelectorAll('.view').forEach((view) => view.classList.toggle('active', view.id === `view-${name}`));
}

function newProfile() {
  patchSelectedButton();
  const idBase = 'perfil';
  let n = 1;
  while (state.config.profiles[`${idBase}${n}`]) n += 1;
  const id = `${idBase}${n}`;
  const source = JSON.parse(JSON.stringify(profile() || { name: '', buttons: {} }));
  source.name = `Perfil ${n}`;
  state.config.profiles[id] = source;
  state.config.active_profile = id;
  state.selectedButton = '1';
  markDirty();
  renderAll();
  persistConfig(true).then(loadAll).catch((e) => toast(`No se pudo crear: ${e.message}`));
  toast('Perfil creado y guardado.');
}

function deleteProfile() {
  const ids = Object.keys(state.config.profiles);
  if (ids.length <= 1) return toast('Debe quedar al menos un perfil');
  const id = state.config.active_profile;
  delete state.config.profiles[id];
  state.config.active_profile = Object.keys(state.config.profiles)[0];
  state.selectedButton = '1';
  markDirty();
  renderAll();
  persistConfig(true).then(loadAll).catch((e) => toast(`No se pudo eliminar: ${e.message}`));
  toast('Perfil eliminado y guardado.');
}

function bindEvents() {
  document.querySelectorAll('.nav-tab').forEach((tab) => tab.addEventListener('click', () => switchView(tab.dataset.view)));
  $('refreshBtn').addEventListener('click', loadAll);
  $('saveBtn').addEventListener('click', saveConfig);
  $('testBtn').addEventListener('click', testSelectedButton);
  $('clearVisualBtn').addEventListener('click', () => { state.visualEventsClearedAt = Date.now(); renderEvents(); });
  $('profileSelect').addEventListener('change', async (e) => {
    patchSelectedButton();
    state.config.active_profile = e.target.value;
    state.selectedButton = '1';
    markDirty();
    renderAll();
    try { await persistConfig(true); await loadAll(); } catch (err) { toast(`No se pudo cambiar perfil: ${err.message}`); }
  });
  $('labelInput').addEventListener('input', () => { patchSelectedButton(); markDirty(); renderDeck(); });
  $('keyInput').addEventListener('input', () => { patchSelectedButton(); markDirty(); renderDeck(); });
  $('actionSelect').addEventListener('change', () => { patchSelectedButton(); markDirty(); renderEditor(); renderDeck(); });
  $('actionSearch').addEventListener('input', (e) => { state.actionFilter = e.target.value; renderActionSelect(); });
  document.querySelector('#paramsBox').addEventListener('input', () => { markDirty(); });
  $('newProfileBtn').addEventListener('click', newProfile);
  $('deleteProfileBtn').addEventListener('click', deleteProfile);
  $('profileNameInput').addEventListener('input', (e) => {
    profile().name = e.target.value.trim() || state.config.active_profile;
    markDirty();
    renderProfileSelect();
    renderProfiles();
  });
  $('profileNameInput').addEventListener('change', () => persistConfig(true).catch((err) => toast(err.message)));
  $('copyDiagBtn').addEventListener('click', async () => {
    const payload = JSON.stringify(state.diag, null, 2);
    await navigator.clipboard?.writeText(payload);
    toast('Diagnóstico copiado');
  });
}

async function tick() {
  try {
    const [diag, events] = await Promise.all([api('/api/diagnostics'), api('/api/events')]);
    state.diag = diag;
    state.events = events;
    renderStatus();
    renderEvents();
    renderDiagnostics();
  } catch (err) {
    console.error(err);
  }
}

hydrateStaticIcons();
bindEvents();
loadAll().catch((err) => toast(`Error cargando SATURN: ${err.message}`));
setInterval(tick, 1100);
