const state = {
  config: null,
  actions: {},
  selectedButton: "1",
  actionFilter: "",
  saveTimer: null,
};

const keysByButton = {
  "1": "F13",
  "2": "F14",
  "3": "F15",
  "4": "F16",
  "5": "F17",
  "6": "F18",
};

const iconPaths = {
  activity: '<path d="M22 12h-4l-3 8L9 4l-3 8H2"/>',
  aperture: '<circle cx="12" cy="12" r="9"/><path d="m14.8 3.6-3.4 8.2h8.4"/><path d="m20.4 14.8-8.2-3.4v8.4"/><path d="m9.2 20.4 3.4-8.2H4.2"/><path d="m3.6 9.2 8.2 3.4V4.2"/><path d="m5.7 5.7 6.1 6.9"/><path d="m18.3 18.3-6.1-6.9"/>',
  book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4v15.5A2.5 2.5 0 0 1 6.5 22H20V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2Z"/>',
  browser: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="M2 9h20"/><path d="M7 6.5h.01"/><path d="M11 6.5h.01"/><path d="M8 14h8"/><path d="M12 11v6"/>',
  bug: '<path d="M8 2l1.88 1.88"/><path d="M14.12 3.88L16 2"/><path d="M9 7.13V6a3 3 0 0 1 6 0v1.13"/><path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6Z"/><path d="M6 13H2"/><path d="M22 13h-4"/><path d="M6.7 17 4 19"/><path d="m20 19-2.7-2"/>',
  camera: '<path d="M14.5 4 16 7h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3l1.5-3h5Z"/><circle cx="12" cy="13" r="3"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  clipboard: '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
  circleHelp: '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 1 1 5.8 1c-.8 1.2-2.9 1.5-2.9 3"/><path d="M12 17h.01"/>',
  code: '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
  command: '<path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0 0-6Z"/>',
  cpu: '<rect width="14" height="14" x="5" y="5" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M9 1v4"/><path d="M15 1v4"/><path d="M9 19v4"/><path d="M15 19v4"/><path d="M1 9h4"/><path d="M1 15h4"/><path d="M19 9h4"/><path d="M19 15h4"/>',
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  folder: '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7l-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2Z"/>',
  gamepad: '<path d="M6 12h4"/><path d="M8 10v4"/><path d="M15 13h.01"/><path d="M18 11h.01"/><rect width="20" height="12" x="2" y="6" rx="2"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 0 20"/><path d="M12 2a15.3 15.3 0 0 0 0 20"/>',
  keyboard: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="M6 8h.01"/><path d="M10 8h.01"/><path d="M14 8h.01"/><path d="M18 8h.01"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/><path d="M7 16h10"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
  layoutGrid: '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
  lock: '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
  messageCircle: '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.5 8.5 0 0 1-4-.96L3 20l1.2-4.4A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8 10h8"/><path d="M8 14h5"/>',
  mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/>',
  micOff: '<path d="m2 2 20 20"/><path d="M9 9v3a3 3 0 0 0 5.1 2.1"/><path d="M15 9.3V5a3 3 0 0 0-5.1-2.1"/><path d="M19 10v2a7 7 0 0 1-1.1 3.8"/><path d="M5 10v2a7 7 0 0 0 9.5 6.5"/><path d="M12 19v3"/>',
  monitor: '<rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 7.5A9 9 0 1 1 12 3Z"/>',
  music: '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
  orbit: '<circle cx="12" cy="12" r="3"/><path d="M3 12c0-2.7 4-5 9-5s9 2.3 9 5-4 5-9 5-9-2.3-9-5Z"/><path d="M12 3c2.7 0 5 4 5 9s-2.3 9-5 9-5-4-5-9 2.3-9 5-9Z"/>',
  package: '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
  play: '<path d="m8 5 11 7-11 7V5Z"/>',
  plug: '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M6 8h12v3a6 6 0 0 1-12 0Z"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  printer: '<path d="M6 9V3h12v6"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v7H6Z"/><path d="M17 12h.01"/>',
  radio: '<path d="M4.9 19.1a10 10 0 1 1 14.2 0"/><path d="M7.8 16.2a6 6 0 1 1 8.4 0"/><circle cx="12" cy="12" r="2"/>',
  refresh: '<path d="M21 12a9 9 0 0 1-15.5 6.3L3 16"/><path d="M3 21v-5h5"/><path d="M3 12A9 9 0 0 1 18.5 5.7L21 8"/><path d="M21 3v5h-5"/>',
  save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  settings: '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.5a2 2 0 0 1-1 1.73l-.15.08a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.73v-.5a2 2 0 0 1 1-1.72l.15-.1a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2Z"/><circle cx="12" cy="12" r="3"/>',
  sliders: '<path d="M4 21v-7"/><path d="M4 10V3"/><path d="M12 21v-9"/><path d="M12 8V3"/><path d="M20 21v-5"/><path d="M20 12V3"/><path d="M2 14h4"/><path d="M10 8h4"/><path d="M18 16h4"/>',
  skipBack: '<path d="M19 20 9 12l10-8v16Z"/><path d="M5 19V5"/>',
  skipForward: '<path d="m5 4 10 8-10 8V4Z"/><path d="M19 5v14"/>',
  sparkles: '<path d="m12 3-1.9 5.8L4 11l6.1 2.2L12 19l1.9-5.8L20 11l-6.1-2.2Z"/>',
  stopCircle: '<circle cx="12" cy="12" r="10"/><rect width="7" height="7" x="8.5" y="8.5" rx="1"/>',
  tag: '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/><circle cx="7.5" cy="7.5" r=".5"/>',
  terminal: '<path d="m4 17 6-6-6-6"/><path d="M12 19h8"/>',
  trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/>',
  type: '<path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/>',
  video: '<path d="m22 8-6 4 6 4V8Z"/><rect width="14" height="12" x="2" y="6" rx="2"/>',
  volume2: '<path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/>',
  volumeX: '<path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="m22 9-6 6"/><path d="m16 9 6 6"/>',
  wrench: '<path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-2.4 2.4-3-3Z"/>',
};

const actionIcons = {
  play_pause: "play",
  prev_track: "skipBack",
  next_track: "skipForward",
  volume_up: "volume2",
  volume_down: "volume2",
  mute: "volumeX",
  mute_mic: "micOff",
  screenshot: "camera",
  show_desktop: "monitor",
  lock_screen: "lock",
  sleep: "moon",
  file_explorer: "folder",
  task_manager: "activity",
  clipboard_history: "clipboard",
  emoji_picker: "sparkles",
  open_spotify: "music",
  open_obs: "aperture",
  open_chrome: "browser",
  open_discord: "messageCircle",
  open_vscode: "code",
  open_steam: "gamepad",
  open_telegram: "send",
  open_terminal: "terminal",
  open_youtube: "play",
  open_twitch: "monitor",
  custom_url: "link",
  obs_scene: "aperture",
  obs_start_stream: "radio",
  obs_stop_stream: "radio",
  obs_start_record: "aperture",
  obs_stop_record: "stopCircle",
  obs_toggle_mute_mic: "micOff",
  vscode_run: "play",
  vscode_build: "wrench",
  vscode_debug: "bug",
  vscode_stop: "play",
  vscode_terminal: "terminal",
  vscode_format: "sparkles",
  vscode_palette: "command",
  vscode_save_all: "save",
  vscode_live_server_open: "globe",
  vscode_live_server_stop: "globe",
  custom_hotkey: "keyboard",
  type_text: "type",
  open_app: "package",
  open_folder: "folder",
  run_command: "terminal",
  system_command: "monitor",
  print: "printer",
};

const categoryNames = {
  media: "Multimedia",
  system: "Sistema",
  apps: "Apps",
  web: "Web",
  obs: "OBS",
  dev: "Dev",
  custom: "Personalizado",
};

const emptyButton = (id) => ({
  key: keysByButton[id],
  label: `Botón ${id}`,
  action: "custom_hotkey",
  params: { hotkey: "" },
});

const $ = (selector) => document.querySelector(selector);

const els = {
  navTabs: document.querySelectorAll(".nav-tab"),
  menuToggle: $("#menuToggle"),
  mainMenu: $("#mainMenu"),
  sections: {
    macros: $("#macrosSection"),
    profiles: $("#profilesSection"),
    diagnostics: $("#diagnosticsSection"),
    help: $("#helpSection"),
  },
  statusSystem: $("#statusSystem"),
  statusListener: $("#statusListener"),
  statusKey: $("#statusKey"),
  heroProfileName: $("#heroProfileName"),
  reloadBtn: $("#reloadBtn"),
  saveBtn: $("#saveBtn"),
  profileSelect: $("#profileSelect"),
  profileNameInput: $("#profileNameInput"),
  newProfileBtn: $("#newProfileBtn"),
  deleteProfileBtn: $("#deleteProfileBtn"),
  profileList: $("#profileList"),
  buttonGrid: $("#buttonGrid"),
  selectedKey: $("#selectedKey"),
  selectedTitle: $("#selectedTitle"),
  keyInput: $("#keyInput"),
  labelInput: $("#labelInput"),
  actionSearch: $("#actionSearch"),
  actionSelect: $("#actionSelect"),
  actionDescription: $("#actionDescription"),
  paramsPanel: $("#paramsPanel"),
  paramsJson: $("#paramsJson"),
  testBtn: $("#testBtn"),
  diagnosticSummary: $("#diagnosticSummary"),
  dependencyList: $("#dependencyList"),
  eventList: $("#eventList"),
  keyEventList: $("#keyEventList"),
  refreshDiagBtn: $("#refreshDiagBtn"),
  toast: $("#toast"),
};

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("is-visible");
  clearTimeout(state.saveTimer);
  state.saveTimer = setTimeout(() => els.toast.classList.remove("is-visible"), 2600);
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `Error ${response.status}`);
  }
  return data;
}

function activeProfileId() {
  return state.config.active_profile || Object.keys(state.config.profiles)[0];
}

function activeProfile() {
  return state.config.profiles[activeProfileId()];
}

function activeButtons() {
  const profile = activeProfile();
  profile.buttons = profile.buttons || {};
  for (let i = 1; i <= 6; i += 1) {
    const id = String(i);
    profile.buttons[id] = { ...emptyButton(id), ...(profile.buttons[id] || {}) };
    profile.buttons[id].params = profile.buttons[id].params || {};
  }
  return profile.buttons;
}

function selectedConfig() {
  return activeButtons()[state.selectedButton];
}

function allActions() {
  return Object.entries(state.actions).flatMap(([category, items]) =>
    items.map((item) => ({ ...item, category }))
  );
}

function findAction(actionId) {
  return allActions().find((item) => item.id === actionId);
}

function actionLabel(actionId) {
  const action = findAction(actionId);
  return action ? action.name : actionId || "Sin acción";
}

function actionCategory(actionId) {
  const action = findAction(actionId);
  return action ? action.category : "custom";
}

function iconSvg(name) {
  const path = iconPaths[name] || iconPaths.settings;
  return `<svg class="outline-icon" viewBox="0 0 24 24" aria-hidden="true">${path}</svg>`;
}

function hydrateStaticIcons(root = document) {
  root.querySelectorAll("[data-ui-icon]").forEach((node) => {
    node.innerHTML = iconSvg(node.dataset.uiIcon);
  });
}

function actionIcon(actionId) {
  return actionIcons[actionId] || "settings";
}

function categoryLabel(category) {
  return categoryNames[category] || category;
}

function setSection(sectionName) {
  els.navTabs.forEach((tab) => tab.classList.toggle("is-active", tab.dataset.section === sectionName));
  Object.entries(els.sections).forEach(([name, section]) => {
    section.classList.toggle("is-active", name === sectionName);
  });
  els.mainMenu?.classList.remove("is-open");
  els.menuToggle?.setAttribute("aria-expanded", "false");
  if (sectionName === "diagnostics") {
    loadDiagnostics();
  }
}

function renderProfiles() {
  els.profileSelect.innerHTML = "";
  Object.entries(state.config.profiles).forEach(([id, profile]) => {
    const option = document.createElement("option");
    option.value = id;
    option.textContent = profile.name || id;
    option.selected = id === activeProfileId();
    els.profileSelect.append(option);
  });
  els.profileNameInput.value = activeProfile().name || activeProfileId();
  els.heroProfileName.textContent = activeProfile().name || activeProfileId();
  renderProfileList();
}

function renderProfileList() {
  if (!els.profileList) return;
  els.profileList.innerHTML = "";

  Object.entries(state.config.profiles).forEach(([id, profile]) => {
    const buttons = profile.buttons || {};
    const configuredCount = Object.values(buttons).filter((button) => button?.action).length;
    const card = document.createElement("button");
    card.className = "profile-card";
    card.type = "button";
    card.classList.toggle("is-active", id === activeProfileId());
    card.innerHTML = `
      <span class="profile-card-icon">${iconSvg("layers")}</span>
      <span class="profile-card-title">
        <strong>${escapeHtml(profile.name || id)}</strong>
        <span>${configuredCount}/6 botones configurados</span>
      </span>
      <span class="badge ${id === activeProfileId() ? "ok" : ""}">${id === activeProfileId() ? "Activo" : "Perfil"}</span>
    `;
    card.addEventListener("click", () => {
      state.config.active_profile = id;
      state.selectedButton = "1";
      renderAll();
      showToast("Perfil activo cambiado. Guardá para conservarlo.");
    });
    els.profileList.append(card);
  });
}

function renderButtons() {
  const buttons = activeButtons();
  els.buttonGrid.innerHTML = "";

  Object.entries(buttons).forEach(([id, button]) => {
    const deckButton = document.createElement("button");
    deckButton.className = "deck-button";
    deckButton.type = "button";
    deckButton.classList.toggle("is-selected", id === state.selectedButton);
    deckButton.dataset.category = actionCategory(button.action);
    deckButton.dataset.id = id;
    deckButton.innerHTML = `
      <span class="button-number">${id}</span>
      <span class="button-icon">${iconSvg(actionIcon(button.action))}</span>
      <span class="button-label">${escapeHtml(button.label || `Botón ${id}`)}</span>
      <span class="button-topline">
        <span class="button-key">${button.key || keysByButton[id]}</span>
        <span class="button-category">${escapeHtml(categoryLabel(actionCategory(button.action)))}</span>
      </span>
      <span class="button-action">${escapeHtml(actionLabel(button.action))}</span>
    `;
    deckButton.addEventListener("click", () => {
      state.selectedButton = id;
      renderButtons();
      renderEditor();
    });
    els.buttonGrid.append(deckButton);
  });
}

function renderActionOptions() {
  const current = selectedConfig();
  const filter = state.actionFilter.trim().toLowerCase();
  const groups = Object.entries(state.actions);
  els.actionSelect.innerHTML = "";

  groups.forEach(([category, items]) => {
    const filtered = items.filter((item) => {
      if (!filter) return true;
      return `${item.id} ${item.name} ${item.description}`.toLowerCase().includes(filter);
    });
    if (!filtered.length) return;

    const group = document.createElement("optgroup");
    group.label = categoryLabel(category).toUpperCase();
    filtered.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.name;
      option.selected = item.id === current.action;
      group.append(option);
    });
    els.actionSelect.append(group);
  });

  if (!els.actionSelect.value && current.action) {
    const option = document.createElement("option");
    option.value = current.action;
    option.textContent = current.action;
    option.selected = true;
    els.actionSelect.append(option);
  }
}

function renderParamFields(action, params) {
  els.paramsPanel.innerHTML = "";
  const fields = action?.params || [];

  if (!fields.length) {
    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent = "Esta acción no necesita parámetros.";
    els.paramsPanel.append(hint);
    return;
  }

  fields.forEach((field) => {
    const wrapper = document.createElement("div");
    wrapper.className = "param-field";

    const label = document.createElement("label");
    label.htmlFor = `param_${field.name}`;
    label.textContent = field.label || field.name;
    wrapper.append(label);

    const input = field.type === "textarea" ? document.createElement("textarea") : document.createElement("input");
    input.id = `param_${field.name}`;
    input.name = field.name;
    input.placeholder = field.placeholder || "";
    input.value = params[field.name] || "";
    if (field.type !== "textarea") input.type = field.type || "text";

    input.addEventListener("input", () => {
      selectedConfig().params[field.name] = input.value;
      syncJsonFromConfig();
      renderButtons();
    });

    wrapper.append(input);
    els.paramsPanel.append(wrapper);
  });
}

function renderEditor() {
  const current = selectedConfig();
  const action = findAction(current.action);

  els.selectedKey.textContent = current.key || keysByButton[state.selectedButton];
  els.selectedTitle.textContent = `CONFIGURAR BOTÓN ${state.selectedButton}`;
  els.keyInput.value = current.key || keysByButton[state.selectedButton];
  els.labelInput.value = current.label || "";

  renderActionOptions();
  els.actionSelect.value = current.action || "";
  els.actionDescription.textContent = action?.description || "Acción personalizada o no reconocida por el catálogo.";

  renderParamFields(action, current.params || {});
  syncJsonFromConfig();
}

function syncJsonFromConfig() {
  els.paramsJson.value = JSON.stringify(selectedConfig().params || {}, null, 2);
}

function syncConfigFromJson() {
  try {
    selectedConfig().params = JSON.parse(els.paramsJson.value || "{}");
    renderParamFields(findAction(selectedConfig().action), selectedConfig().params);
    renderButtons();
    return true;
  } catch (error) {
    showToast(`JSON inválido: ${error.message}`);
    return false;
  }
}

function createProfileId(name) {
  const base = name
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "") || "perfil";
  let id = base;
  let count = 2;
  while (state.config.profiles[id]) {
    id = `${base}_${count}`;
    count += 1;
  }
  return id;
}

function newProfile() {
  const name = prompt("Nombre del nuevo perfil:", "Nuevo perfil");
  if (!name) return;
  const id = createProfileId(name);
  state.config.profiles[id] = {
    name,
    buttons: Object.fromEntries(Array.from({ length: 6 }, (_, index) => {
      const btnId = String(index + 1);
      return [btnId, emptyButton(btnId)];
    })),
  };
  state.config.active_profile = id;
  state.selectedButton = "1";
  renderAll();
  showToast("Perfil creado. No olvides guardar.");
}

function deleteProfile() {
  const id = activeProfileId();
  const ids = Object.keys(state.config.profiles);
  if (ids.length <= 1) {
    showToast("Tiene que quedar al menos un perfil.");
    return;
  }
  const profileName = state.config.profiles[id].name || id;
  if (!confirm(`Eliminar perfil "${profileName}"?`)) return;
  delete state.config.profiles[id];
  state.config.active_profile = Object.keys(state.config.profiles)[0];
  state.selectedButton = "1";
  renderAll();
  showToast("Perfil eliminado. No olvides guardar.");
}

async function saveConfig() {
  if (!syncConfigFromJson()) return;
  try {
    await fetchJson("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.config),
    });
    showToast("Configuración guardada.");
    await loadDiagnostics();
  } catch (error) {
    showToast(`No se pudo guardar: ${error.message}`);
  }
}

async function testSelectedButton() {
  if (!syncConfigFromJson()) return;
  await saveConfig();
  try {
    const result = await fetchJson(`/api/test/${state.selectedButton}`, { method: "POST" });
    showToast(`Probando: ${result.action}`);
  } catch (error) {
    showToast(`No se pudo probar: ${error.message}`);
  }
}

function renderDiagnosticSummary(report) {
  const system = report.system || {};
  const runtime = report.runtime || {};
  const listener = runtime.listener || {};
  els.statusSystem.textContent = `${system.system || "--"} ${system.session_type || ""}`.trim();
  els.statusListener.textContent = listener.active ? `${listener.backend} activo` : "Inactivo";
  els.statusKey.textContent = runtime.last_key?.key || "--";

  const rows = [
    ["Sistema", system.system || "--"],
    ["Versión", system.release || "--"],
    ["Sesión", system.session_type || "--"],
    ["Escritorio", system.desktop || "--"],
    ["Python", system.python || "--"],
    ["Listener", listener.active ? `${listener.backend} activo` : listener.error || "Inactivo"],
  ];

  els.diagnosticSummary.innerHTML = rows.map(([label, value]) => `
    <div class="kv-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>
  `).join("");
}

function renderDependencies(report) {
  const deps = report.dependencies || {};
  const packages = deps.python_packages || {};
  const commands = deps.commands || {};
  const packageRows = Object.entries(packages).map(([name, ok]) => dependencyRow(name, ok));

  const commandRows = Object.entries(commands).map(([name, value]) => {
    if (typeof value === "boolean") return dependencyRow(name, value);
    if (value && typeof value.available === "boolean") return dependencyRow(name, value.available);
    if (value && typeof value === "object") {
      return dependencyRow(name, Object.values(value).some(Boolean));
    }
    return dependencyRow(name, false);
  });

  const warnings = (report.warnings || []).map((warning) => `
    <div class="dependency-item"><span>${escapeHtml(warning)}</span><strong class="badge warn">Aviso</strong></div>
  `);

  els.dependencyList.innerHTML = [...warnings, ...packageRows, ...commandRows].join("") || "<p class='hint'>Sin datos.</p>";
}

function dependencyRow(name, ok) {
  return `
    <div class="dependency-item">
      <span>${escapeHtml(name)}</span>
      <strong class="badge ${ok ? "ok" : "error"}">${ok ? "OK" : "Falta"}</strong>
    </div>
  `;
}

function renderEvents(report) {
  const events = report.events || [];
  if (!events.length) {
    els.eventList.innerHTML = "<p class='hint'>Todavía no hay eventos.</p>";
    return;
  }
  els.eventList.innerHTML = events.slice().reverse().map((event) => `
    <div class="event-item">
      <span>${escapeHtml(event.ts)} · ${escapeHtml(event.message)}</span>
      <strong class="badge ${event.level === "error" ? "error" : event.level === "warning" ? "warn" : ""}">
        ${escapeHtml(event.level)}
      </strong>
    </div>
  `).join("");
}

function renderKeyEvents(report) {
  const events = report.key_events || [];
  if (!events.length) {
    els.keyEventList.innerHTML = "<p class='hint'>Todavía no se detectaron teclas. Tocá un botón físico del Pro Micro.</p>";
    return;
  }
  els.keyEventList.innerHTML = events.slice().reverse().map((event) => `
    <div class="event-item">
      <span>${escapeHtml(event.ts)} · ${escapeHtml(event.raw || event.key)} → ${escapeHtml(event.key || "--")}</span>
      <strong class="badge ${event.matched ? "ok" : "warn"}">
        ${event.matched ? `Botón ${escapeHtml(event.button)}` : "Sin mapa"}
      </strong>
    </div>
  `).join("");
}

async function loadDiagnostics() {
  try {
    const report = await fetchJson("/api/diagnostics");
    renderDiagnosticSummary(report);
    renderDependencies(report);
    renderEvents(report);
    renderKeyEvents(report);
  } catch (error) {
    showToast(`Diagnóstico no disponible: ${error.message}`);
  }
}

function renderAll() {
  renderProfiles();
  renderButtons();
  renderEditor();
}

async function loadApp() {
  try {
    const [config, actions] = await Promise.all([
      fetchJson("/api/config"),
      fetchJson("/api/actions"),
    ]);
    state.config = config;
    state.actions = actions;
    state.selectedButton = "1";
    renderAll();
    await loadDiagnostics();
    showToast("Panel listo.");
  } catch (error) {
    showToast(`No se pudo iniciar: ${error.message}`);
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindEvents() {
  if (els.menuToggle && els.mainMenu) {
    els.menuToggle.addEventListener("click", (event) => {
      event.stopPropagation();
      const isOpen = els.mainMenu.classList.toggle("is-open");
      els.menuToggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  document.addEventListener("click", (event) => {
    if (!els.mainMenu || !els.mainMenu.classList.contains("is-open")) return;
    if (event.target.closest(".menu-wrapper")) return;
    els.mainMenu.classList.remove("is-open");
    els.menuToggle?.setAttribute("aria-expanded", "false");
  });

  els.navTabs.forEach((tab) => {
    tab.addEventListener("click", () => setSection(tab.dataset.section));
  });

  els.reloadBtn.addEventListener("click", loadApp);
  els.saveBtn.addEventListener("click", saveConfig);
  els.refreshDiagBtn.addEventListener("click", loadDiagnostics);
  els.testBtn.addEventListener("click", testSelectedButton);
  els.newProfileBtn.addEventListener("click", newProfile);
  els.deleteProfileBtn.addEventListener("click", deleteProfile);

  els.profileSelect.addEventListener("change", () => {
    state.config.active_profile = els.profileSelect.value;
    state.selectedButton = "1";
    renderAll();
    showToast("Perfil activo cambiado. Guardá para conservarlo.");
  });

  els.profileNameInput.addEventListener("input", () => {
    activeProfile().name = els.profileNameInput.value || activeProfileId();
    els.heroProfileName.textContent = activeProfile().name;
    const selected = els.profileSelect.selectedOptions[0];
    if (selected) selected.textContent = activeProfile().name;
  });

  els.labelInput.addEventListener("input", () => {
    selectedConfig().label = els.labelInput.value;
    renderButtons();
  });

  els.keyInput.addEventListener("input", () => {
    selectedConfig().key = els.keyInput.value.trim() || keysByButton[state.selectedButton];
    renderButtons();
    renderProfiles();
  });

  els.actionSearch.addEventListener("input", () => {
    state.actionFilter = els.actionSearch.value;
    renderActionOptions();
  });

  els.actionSelect.addEventListener("change", () => {
    const current = selectedConfig();
    current.action = els.actionSelect.value;
    current.params = {};
    const action = findAction(current.action);
    (action?.params || []).forEach((field) => {
      current.params[field.name] = "";
    });
    if (!current.label || current.label.startsWith("Boton ") || current.label.startsWith("Botón ")) {
      current.label = action?.name || current.action;
      els.labelInput.value = current.label;
    }
    els.actionDescription.textContent = action?.description || "Acción personalizada.";
    renderParamFields(action, current.params);
    syncJsonFromConfig();
    renderButtons();
  });

  els.paramsJson.addEventListener("blur", syncConfigFromJson);

  setInterval(loadDiagnostics, 5000);

  if (window.io) {
    const socket = window.io();
    socket.on("button_press", (payload) => {
      const button = document.querySelector(`.deck-button[data-id="${payload.id}"]`);
      if (!button) return;
      button.classList.add("is-pressed");
      setTimeout(() => button.classList.remove("is-pressed"), 220);
      loadDiagnostics();
    });
    socket.on("key_event", () => {
      loadDiagnostics();
    });
    socket.on("action_error", (payload) => {
      showToast(`Error en ${payload.action}: ${payload.error}`);
      loadDiagnostics();
    });
  }
}

bindEvents();
hydrateStaticIcons();
loadApp();
