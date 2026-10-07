// Application controller: boot, routing, data binding, live checking, files, theme.
// The GUI never computes a result: it posts the case JSON to the local API (app.service) and renders what comes back.
import { $, $$, h, fmtIn, getPath, setPath, deletePath, debounce, download, slug, uniqueId, parseNum } from "./util.js";
import { get, post } from "./api.js";
import { S, caseKey, isDirty, isStale, riskIds } from "./state.js";
import { icon, toast, openModal, closeModal, confirmModal, showEvidence, refreshSourcePicker, alertBox } from "./ui.js";
import { applyInline, countByScreen, screenProblems, classify, friendly, SCREEN_TITLES } from "./problems.js";
import * as sCase from "./screens/case.js";
import * as sRules from "./screens/rules.js";
import * as sRisks from "./screens/risks.js";
import * as sMatrix from "./screens/matrix.js";
import * as sEv from "./screens/evidence.js";
import * as sRep from "./screens/report.js";
import { initCursor } from "./cursor.js";

const SCREENS = [
  { id: "case", n: 1, title: "Case & Activity", ic: "building", group: "Define", mod: sCase },
  { id: "rules", n: 2, title: "Site facts & Rules", ic: "rules", group: "Identify", mod: sRules },
  { id: "risks", n: 3, title: "Risk register", ic: "shield", group: "Identify", mod: sRisks },
  { id: "matrix", n: 4, title: "Risk matrix", ic: "grid", group: "Prioritise", mod: sMatrix, results: true },
  { id: "evidence", n: 5, title: "Evidence", ic: "book", group: "Reference", mod: sEv },
  { id: "report", n: 6, title: "Export", ic: "doc", group: "Reference", mod: sRep, results: true },
];
const BY_ID = Object.fromEntries(SCREENS.map((s) => [s.id, s]));
const screenEl = () => $("#screen");

// ------------------------------------------------------------------ theme
function theme() { return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light"; }
function setTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  try { window.localStorage.setItem("fyp-gui-theme", t); } catch (e) { /* storage unavailable: theme still applies for this session */ }
  renderToolbar();
}

// ------------------------------------------------------------------ chrome
function renderToolbar() {
  const ai = S.health?.ai;
  const dark = theme() === "dark";
  $("#toolbar").innerHTML = `
    <button type="button" class="btn btn-ghost" data-action="new" title="New blank case (template)">${icon("file")}<span class="lbl">New</span></button>
    <button type="button" class="btn btn-ghost" data-action="open" title="Open a case JSON file (Ctrl+O)">${icon("folder")}<span class="lbl">Open</span></button>
    <button type="button" class="btn btn-ghost" data-action="save" title="Save the case as JSON (Ctrl+S)">${icon("save")}<span class="lbl">Save</span></button>
    <button type="button" class="btn btn-ghost" data-action="example" title="Load the ILLUSTRATIVE example (placeholder numbers)">${icon("flask")}<span class="lbl">Load example</span></button>
    <span class="sep" aria-hidden="true"></span>
    <button type="button" class="btn btn-ghost btn-icon" data-action="theme" aria-label="Switch to ${dark ? "light" : "dark"} theme" title="Switch to ${dark ? "light" : "dark"} theme">${icon(dark ? "sun" : "moon")}</button>
    ${ai ? `<span class="ai-badge${ai.mode === "llm" ? " is-llm" : ""}" tabindex="0" data-tip="${h(ai.label)}" aria-label="${h(ai.label)}">${icon("sparkle", "ic-sm")}<span>${ai.mode === "llm" ? "AI: guarded LLM" : "AI: offline mode"}</span></span>` : ""}`;
}

function renderRail() {
  const counts = countByScreen();
  let html = "", group = "";
  for (const s of SCREENS) {
    if (s.group !== group) { if (group) html += "</div>"; group = s.group; html += `<div class="rail-group"><div class="rail-group-title">${h(group)}</div>`; }
    const n = counts[s.id] || 0;
    const flag = n ? `<span class="nav-flag err" title="${n} input problem(s)">${icon("alert", "ic-sm")}${n}</span>`
      : s.results && S.result && isStale() ? `<span class="nav-flag stale" title="Inputs have problems; showing the last valid state">stale</span>` : "";
    html += `<a class="navlink" href="#/${s.id}" data-tip="${h(`${s.n}. ${s.title}`)}"${S.ui.screen === s.id ? ' aria-current="page"' : ""}><span class="nav-num">${s.n}</span>${icon(s.ic)}<span class="nav-label">${h(s.title)}</span>${flag}</a>`;
  }
  html += `</div>
    <button type="button" class="navlink rail-settings" data-action="settings" data-tip="Settings: API key, model">${icon("gear")}<span class="nav-label">Settings</span></button>
    <div class="rail-foot">Offline tool. The register and matrix come from the service; the GUI computes nothing.<br>v${h(S.health?.version || "")} Â· ${(S.health?.evidence_records ?? S.evidenceList.length).toLocaleString()} evidence records</div>`;
  $("#rail").innerHTML = html;
}

function renderDirty() {
  const el = $("#dirty");
  const d = isDirty();
  el.classList.toggle("is-dirty", d);
  el.querySelector(".dirty-txt").textContent = d ? "Unsaved changes" : S.ui.fileName ? `Saved Â· ${S.ui.fileName}` : "No unsaved changes";
  el.title = d ? "The case differs from the last saved / opened / loaded version" : "";
  const nameInput = $("#case-name");
  if (document.activeElement !== nameInput) nameInput.value = S.case?.project?.name || "";
}

function renderProblemsBtn() {
  const n = (S.validation.problems || []).length;
  const b = $("#problems-btn");
  b.hidden = n === 0;
  b.innerHTML = `${icon("alert", "ic-sm")}${n} problem${n === 1 ? "" : "s"}`;
}

function renderKpi() {
  const el = $("#kpi-strip");
  const r = S.result;
  if (!r) {
    el.className = "kpi-strip is-empty";
    el.innerHTML = `${icon("info")}<span>&nbsp;Checking the caseâ€¦ the register and matrix update as you type.</span>`;
    return;
  }
  const s = r.summary;
  const item = (k, v, u = "", cls = "") => `<div class="kpi-item ${cls}"><span class="k">${k}</span><span class="v"${typeof v === "number" && !u ? ` data-n="${v}" data-k="${k}"` : ""}>${v}${u ? `<small>${u}</small>` : ""}</span></div>`;
  el.className = "kpi-strip";
  el.innerHTML = [
    item("Risks in register", s.n_risks),
    item("Complete", `${s.n_complete}<small>/ ${s.n_risks}</small>`),
    item("On matrix", s.n_on_matrix),
    ...["Extreme", "High", "Moderate", "Low"].map((k) => s.levels[k] ? item(k, s.levels[k]) : ""),
    item("Rule-flagged", s.n_flagged),
    s.n_flagged_missing ? item("Flagged, not in register", s.n_flagged_missing, "", "pref") : "",
    isStale() ? `<span class="badge chip-stale" title="Inputs have problems">${icon("alert")}Showing last valid state</span>` : "",
  ].join("");
  countUp(el);
}

// Numbers in the summary strip count up to their new value (easeOutQuint, like the reference site's motion).
const kpiPrev = new Map();
function countUp(root) {
  const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.querySelectorAll(".v[data-n]").forEach((v) => {
    const to = Number(v.dataset.n), key = v.dataset.k, from = kpiPrev.has(key) ? kpiPrev.get(key) : 0;
    kpiPrev.set(key, to);
    if (calm || from === to) return;
    const t0 = performance.now(), ms = 700;
    const step = (now) => {
      const p = Math.min(1, (now - t0) / ms), e = 1 - Math.pow(1 - p, 5);
      v.textContent = String(Math.round(from + (to - from) * e));
      if (p < 1 && v.isConnected) requestAnimationFrame(step);
      else v.textContent = String(to);
    };
    requestAnimationFrame(step);
  });
}

function renderChrome() { renderToolbar(); renderRail(); renderDirty(); renderProblemsBtn(); renderKpi(); }

// ------------------------------------------------------------------ screens
// Page title: every letter is a two-line window (letter + its copy below); on hover the letters roll up one after another.
function rollTitle(h1) {
  if (!h1 || h1.querySelector(".ch")) return;
  const text = h1.textContent;
  h1.setAttribute("aria-label", text);
  const esc = (c) => c.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  let i = 0;
  h1.innerHTML = text.split(" ").map((w) =>
    `<span class="word" aria-hidden="true">${[...w].map((c) => `<span class="ch" style="--i:${i++}" data-c="${esc(c)}">${esc(c)}</span>`).join("")}</span>`
  ).join(" ");
}

function renderScreen({ nav = false } = {}) {
  const root = screenEl();
  const y = window.scrollY;
  const activeId = document.activeElement && root.contains(document.activeElement) ? document.activeElement.id : null;
  const mod = BY_ID[S.ui.screen].mod;
  root.innerHTML = mod.render();
  if (!root.querySelector("[data-screen-problems]")) {
    const html = screenProblems(S.ui.screen);
    if (html) root.querySelector(".screen-head")?.insertAdjacentHTML("afterend", html);
  }
  applyInline(root);
  rollTitle(root.querySelector(".screen-head h1"));
  if (nav) {
    root.classList.remove("is-entering"); void root.offsetHeight; root.classList.add("is-entering");   // staggered rise-in, on navigation only
    clearTimeout(renderScreen.enterTimer);
    renderScreen.enterTimer = setTimeout(() => root.classList.remove("is-entering"), 1600);
    window.scrollTo(0, 0);
    root.querySelector("h1")?.focus({ preventScroll: true });
  } else {
    window.scrollTo(0, y);
    if (activeId) document.getElementById(activeId)?.focus({ preventScroll: true });
  }
}
function renderAll(opts) { renderChrome(); renderScreen(opts); }

function go(id) {
  if (!BY_ID[id]) id = "case";
  if (location.hash !== `#/${id}`) { location.hash = `#/${id}`; return; }
  S.ui.screen = id;
  renderRail();
  renderScreen({ nav: true });
}
window.addEventListener("hashchange", () => {
  const id = (location.hash.match(/^#\/([\w-]+)/) || [])[1] || "case";
  S.ui.screen = BY_ID[id] ? id : "case";
  renderRail();
  renderScreen({ nav: true });
});

// ------------------------------------------------------------------ evidence lookups
async function ensureEvidence(ids) {
  const need = [...new Set((ids || []).filter(Boolean))].filter((id) => !S.evidence.has(id));
  if (!need.length) return false;
  const r = await get(`/api/evidence?ids=${encodeURIComponent(need.join(","))}`);
  if (!r.ok) return false;
  for (const rec of r.data.records) S.evidence.set(rec.id, rec);
  return r.data.records.length > 0;
}
function refreshEvList() { const list = $("#ev-list"); if (list) list.innerHTML = sEv.evidenceList(); }
const searchEvidence = debounce(async () => {
  const q = S.ui.evQuery.trim();
  if (!q) { S.ui.evHits = null; S.ui.evBusy = false; refreshEvList(); return; }
  S.ui.evBusy = true; refreshEvList();
  const r = await get(`/api/evidence?q=${encodeURIComponent(q)}&k=50`);
  if (S.ui.evQuery.trim() !== q) return;          // a newer query superseded this one
  S.ui.evBusy = false;
  S.ui.evHits = r.ok ? r.data.records : [];
  refreshEvList();
}, 300);

// ------------------------------------------------------------------ change tracking + live check
let vseq = 0;
async function validateNow() {
  if (!S.case) return;
  const seq = ++vseq;
  const key = caseKey();
  const res = await post("/api/validate", S.case);
  if (seq !== vseq) return;   // a newer edit superseded this request
  if (res.ok && res.data.ok) {
    S.validation = { status: "ok", problems: [], warnings: res.data.warnings || [], key };
    S.result = res.data.result; S.resultKey = key;
  } else {
    S.validation = { status: "err", problems: res.data?.problems || [`validation failed (HTTP ${res.status})`], warnings: [], key };
  }
  let added = [];
  if (S.validation.status === "ok" && S.ui.autoAddPending) { S.ui.autoAddPending = false; added = autoAddFlaggedRisks(); }
  afterValidation();
  if (added.length) {
    changed({ rerender: true });
    toast(`${added.length} rule-flagged risk${added.length > 1 ? "s were" : " was"} added to the register (${added.join(", ")}). Enter each probability and delay to place ${added.length > 1 ? "them" : "it"} on the matrix.`, "info",
      { actionLabel: "Open register", timeout: 12000, onAction: () => { location.hash = "#/risks"; } });
  }
}
const validateSoon = debounce(validateNow, 350);

function afterValidation() {
  const root = screenEl();
  applyInline(root);
  const old = root.querySelector("[data-screen-problems]");
  const html = screenProblems(S.ui.screen);
  if (old) { if (html) old.outerHTML = html; else old.remove(); }
  else if (html) root.querySelector(".screen-head")?.insertAdjacentHTML("afterend", html);
  BY_ID[S.ui.screen].mod.refreshLive?.(root);
  renderRail(); renderProblemsBtn(); renderKpi();
}

function changed({ rerender = false } = {}) {
  renderDirty(); renderKpi();
  if (rerender) { renderRail(); renderScreen(); }
  validateSoon();
}

// ------------------------------------------------------------------ binding handlers
function markInvalid(el, bad) { el.classList.toggle("is-invalid", bad); }

function applyBind(el) {
  const path = el.dataset.bind, t = el.dataset.t;
  let v;
  if (t === "num" || t === "int") {
    if (el.validity && el.validity.badInput) { markInvalid(el, true); return false; }
    const r = parseNum(el.value, t === "int");
    if (!r.ok) { markInvalid(el, true); return false; }
    markInvalid(el, false);
    v = r.value;
    if (v === null && el.dataset.null === "delete") { deletePath(S.case, path); return true; }
  } else if (t === "bool") v = !!el.checked;
  else v = el.value;
  setPath(S.case, path, v);
  if (t === "src") refreshSourcePicker(el);
  return true;
}

// A number typed while the source is still blank is by definition the user's own input; never overwrites a chosen source
// and never picks Literature (a paper supports that a risk exists, not its probability or delay).
function autoSource(sel, hasValue) {
  if (!sel || sel.value || !hasValue) return;
  if (![...sel.options].some((o) => o.value === "User Input")) return;
  sel.value = "User Input";
  refreshSourcePicker(sel);
}

function applyParam(wrap) {
  const path = wrap.dataset.param;
  const optional = wrap.dataset.optional === "1";
  const vEl = wrap.querySelector('[data-prole="value"]');
  const sEl = wrap.querySelector('[data-prole="source"]');
  refreshSourcePicker(sEl);
  if (vEl.validity && vEl.validity.badInput) { markInvalid(vEl, true); return false; }
  const r = parseNum(vEl.value);
  if (!r.ok) { markInvalid(vEl, true); return false; }
  markInvalid(vEl, false);
  autoSource(sEl, r.value !== null && r.value !== undefined);
  const cur = getPath(S.case, path);
  if (r.value === null && optional) { setPath(S.case, path, null); return true; }
  const obj = cur && typeof cur === "object" ? { ...cur } : {};
  obj.value = r.value;
  obj.source = sEl.value;
  setPath(S.case, path, obj);
  return true;
}

function applyDist(wrap) {
  const path = wrap.dataset.dist;
  const optional = wrap.dataset.optional === "1";
  const q = (role) => wrap.querySelector(`[data-drole="${role}"]`);
  const cur = getPath(S.case, path) || {};
  const read = (role) => {
    const el = q(role);
    if (!el) return { ok: true, value: undefined };
    if (el.validity && el.validity.badInput) { markInvalid(el, true); return { ok: false }; }
    const r = parseNum(el.value);
    markInvalid(el, !r.ok);
    return r;
  };
  const a = read("a"), m = read("m"), b = read("b"), lam = read("lam");
  if (![a, m, b, lam].every((x) => x.ok)) return false;
  autoSource(q("source"), [a, m, b].some((x) => x.value !== null && x.value !== undefined));
  refreshSourcePicker(q("source"));
  const pick = (x, k) => (x.value !== undefined ? x.value : (cur[k] ?? null));
  if (optional && [a, m, b].every((x) => x.value === null || x.value === undefined)) { setPath(S.case, path, null); return true; }
  const kind = q("kind").value;
  const obj = { kind, source: q("source").value };
  if (kind === "fixed") { const v = pick(m, "m"); obj.a = v; obj.m = v; obj.b = v; }
  else if (kind === "uniform") { obj.a = pick(a, "a"); obj.b = pick(b, "b"); }
  else { obj.a = pick(a, "a"); obj.m = pick(m, "m"); obj.b = pick(b, "b"); }
  if (kind === "pert") { const l = lam.value !== undefined ? lam.value : cur.lam; if (l !== null && l !== undefined) obj.lam = l; }
  if (cur.evidence_ids) obj.evidence_ids = cur.evidence_ids;
  setPath(S.case, path, obj);
  return true;
}

function applyEdges() {
  const vals = [0, 1, 2, 3].map((k) => { const el = $(`#edge-${k}`); const r = parseNum(el.value); markInvalid(el, !r.ok); return r.ok ? r.value : null; });
  S.case.impact_bin_edges_fraction = vals.every((v) => v === null) ? null : vals;
}

async function addEvidence(input) {
  const id = input.value.trim();
  if (!id) return;
  const path = input.dataset.evAdd;
  const list = getPath(S.case, path);
  const arr = Array.isArray(list) ? list : [];
  if (!arr.includes(id)) arr.push(id);
  setPath(S.case, path, arr);
  await ensureEvidence([id]);
  if (!S.evidence.has(id)) toast(`Evidence ID "${h(id)}" is not in the evidence corpus; it is kept but flagged.`, "info");
  changed({ rerender: true });
  setTimeout(() => $(`[data-ev-add="${CSS.escape(path)}"]`)?.focus(), 0);
}

function onInput(e) {
  const el = e.target;
  if (el.matches("[data-bind]") && ["num", "int", "text"].includes(el.dataset.t)) {
    if (applyBind(el)) changed();
    if (el.id === "case-name") renderDirty();
  } else if (el.matches('[data-prole="value"]')) {
    if (applyParam(el.closest(".param"))) changed();
  } else if (el.matches('input[data-drole]')) {
    if (applyDist(el.closest(".dist-wrap"))) changed();
  } else if (el.dataset.actionInput === "edge") {
    applyEdges(); changed();
  } else if (el.dataset.actionInput === "lib-search") {
    S.ui.libQuery = el.value;
    const slot = $("#lib-list");
    if (slot) { const tmp = document.createElement("div"); tmp.innerHTML = sRisks.libraryPanel(); slot.innerHTML = tmp.querySelector("#lib-list").innerHTML; }
  } else if (el.dataset.actionInput === "ev-search") {
    S.ui.evQuery = el.value;
    refreshEvList();
    searchEvidence();
  }
}

function onChange(e) {
  const el = e.target;
  if (el.matches(".chip-add")) { addEvidence(el); return; }
  if (el.matches('[data-bind^="facts."]')) { S.ui.autoAddPending = true; validateSoon(); return; }   // a committed site fact
  if (el.matches("[data-bind]") && ["sel", "src", "bool"].includes(el.dataset.t)) {
    if (applyBind(el)) changed({ rerender: el.dataset.rerender === "1" });
    return;
  }
  if (el.matches('[data-prole="source"]')) { if (applyParam(el.closest(".param"))) changed(); return; }
  if (el.matches('select[data-drole]')) {
    if (applyDist(el.closest(".dist-wrap"))) changed({ rerender: el.dataset.drole === "kind" });
    return;
  }
  const act = el.dataset.action || el.dataset.actionChange;
  if (act && CHANGE_ACTIONS[act]) CHANGE_ACTIONS[act](el);
}

// ------------------------------------------------------------------ case factories (no numbers are ever filled in)
function newRisk(id, extra = {}) {
  return { id, name: "", category: "", description: "", status: "expert/user-provided", evidence_ids: [],
    p: { value: null, source: "" }, delay: { kind: "pert", a: null, m: null, b: null, source: "" }, ...extra };
}
/** Bulk add: every library risk (optionally one category) not yet in the register. Probability and delay stay EMPTY. */
function addAllFromLibrary(cat) {
  const have = new Set(riskIds());
  const todo = S.library.filter((L) => (!cat || L.category === cat) && !have.has(L.id));
  if (!todo.length) { toast("Everything in this group is already in the register.", "info"); return; }
  S.case.risks = S.case.risks || [];
  todo.forEach((L) => S.case.risks.push(newRisk(L.id, { name: L.name, category: L.category, description: L.description, status: "literature-supported", evidence_ids: [...(L.existence_evidence || [])] })));
  changed({ rerender: true });
  toast(`${todo.length} risk${todo.length > 1 ? "s" : ""} added with empty probability and delay. Those with a literature seed appear on the matrix as a ranking.`, "ok");
}
function addRiskFromLibrary(rid) {
  const L = S.library.find((x) => x.id === rid);
  if (!L) return;
  if (riskIds().includes(rid)) { toast(`${h(rid)} is already in the register.`, "info"); return; }
  S.case.risks = S.case.risks || [];
  S.case.risks.push(newRisk(L.id, { name: L.name, category: L.category, description: L.description, status: "literature-supported", evidence_ids: [...(L.existence_evidence || [])] }));
  openNewRisk(S.case.risks.length - 1, `${h(L.id)} added. Enter its probability and delay with their sources.`);
}
/** After a deliberate change of a site fact: risks the rules flag as elevated but that are missing from the
 *  register are added from the curated library, with name/category/evidence filled and probability/delay
 *  left EMPTY (no number is ever invented). A risk the user deletes afterwards is not added again in this session. */
function autoAddFlaggedRisks() {
  const flags = S.result?.rules?.flags || {};
  const have = new Set(riskIds());
  const added = [];
  for (const [rid, fl] of Object.entries(flags)) {
    if (fl.level !== "elevated" || have.has(rid) || S.ui.autoAdded.has(rid)) continue;
    const L = S.library.find((x) => x.id === rid);
    if (!L) continue;
    S.case.risks = S.case.risks || [];
    S.case.risks.push(newRisk(L.id, { name: L.name, category: L.category, description: L.description, status: "literature-supported", evidence_ids: [...(L.existence_evidence || [])] }));
    S.ui.autoAdded.add(rid);
    added.push(rid);
  }
  return added;
}
function openNewRisk(i, msg) {
  S.ui.open.add(`risk:${i}`);
  toast(msg, "ok");
  if (S.ui.screen !== "risks") { location.hash = "#/risks"; }
  changed({ rerender: S.ui.screen === "risks" });
  setTimeout(() => {
    const el = document.getElementById(`r${i}-p`);
    if (el) { el.scrollIntoView({ block: "center", behavior: "smooth" }); el.focus({ preventScroll: true }); }
  }, 120);
}

// ------------------------------------------------------------------ actions
async function guardDiscard(what) {
  if (!isDirty()) return true;
  return confirmModal("Discard unsaved changes?", `The current case has unsaved changes. ${h(what)} will replace it. Save first if you want to keep it.`, "Discard and continue");
}
function loadCase(c, { fileName = null, msg = "" } = {}) {
  S.case = c;
  S.savedKey = caseKey();
  S.result = null; S.resultKey = null;
  S.validation = { status: "idle", problems: [], warnings: [], key: null };
  S.ui.open.clear(); S.ui.autoAdded.clear(); S.ui.suggest = null;
  S.ui.autoAddPending = true;                 // a freshly loaded case may already have flagged risks missing
  S.ui.fileName = fileName;
  renderAll({ nav: true });
  if (msg) toast(msg, "ok");
  ensureEvidence([...sEv.citedIds()]).then((found) => { if (found) renderScreen(); });
  validateNow();
}

async function downloadFrom(path, name) {
  const res = await post(path, S.case);
  if (res.ok && res.data instanceof Blob) { download(name, res.data); toast(`Downloaded ${h(name)} (built from the current inputs).`, "ok"); }
  else {
    const probs = res.data?.problems || [`HTTP ${res.status}`];
    S.validation = { status: "err", problems: probs, warnings: [], key: caseKey() };
    afterValidation();
    toast(`Cannot create ${h(name)}: ${probs.length} problem(s) in the inputs.`, "err", { actionLabel: "Show", onAction: openProblems });
  }
}

// PNG: the server draws the SVG; the browser rasterises it at 2x (no extra library).
async function downloadPng() {
  const res = await post("/api/matrix-svg", S.case);
  if (!(res.ok && res.data instanceof Blob)) return downloadFrom("/api/matrix-svg", "risk_matrix.png");   // shows the problems
  const url = URL.createObjectURL(res.data);
  try {
    const img = new Image();
    await new Promise((ok, bad) => { img.onload = ok; img.onerror = bad; img.src = url; });
    const k = 2, c = document.createElement("canvas");
    c.width = img.naturalWidth * k; c.height = img.naturalHeight * k;
    const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height); g.drawImage(img, 0, 0, c.width, c.height);
    const blob = await new Promise((ok) => c.toBlob(ok, "image/png"));
    download("risk_matrix.png", blob); toast("Downloaded risk_matrix.png (built from the current inputs).", "ok");
  } catch { toast("Could not create the PNG in this browser; use matrix.svg instead.", "err"); }
  finally { URL.revokeObjectURL(url); }
}

function saveCase() {
  const name = `${slug(S.case?.project?.name)}.json`;
  download(name, JSON.stringify(S.case, null, 2) + "\n", "application/json");
  S.savedKey = caseKey();
  S.ui.fileName = name;
  renderDirty();
  toast(`Case saved as ${h(name)}.`, "ok");
}

function removeWithUndo(listPath, i, label) {
  const list = getPath(S.case, listPath);
  const [item] = list.splice(i, 1);
  S.ui.open.clear();
  changed({ rerender: true });
  toast(`${h(label)} removed.`, "info", { actionLabel: "Undo", timeout: 7000, onAction: () => { getPath(S.case, listPath).splice(i, 0, item); changed({ rerender: true }); } });
}

function openProblems() {
  const root = $("#popover-root");
  if (root.innerHTML) { closeProblems(); return; }
  const btn = $("#problems-btn");
  const probs = S.validation.problems || [];
  const rect = btn.getBoundingClientRect();
  root.innerHTML = `<div class="popover" role="dialog" aria-label="Input problems" style="top:${rect.bottom + 8}px;left:${Math.max(16, Math.min(rect.left, window.innerWidth - 580))}px">
    <h3>${icon("alert")} ${probs.length} problem${probs.length === 1 ? "" : "s"} reported by the service</h3>
    ${probs.map((p) => { const c = classify(p); const sc = c.screen || "case"; return `<div class="prob-item">${icon("alert")}<div>${friendly(p)}</div><button type="button" class="btn btn-sm where" data-action="goto" data-screen="${sc}">${h(SCREEN_TITLES[sc] || sc)} ${icon("chevRight", "ic-sm")}</button></div>`; }).join("")}
  </div>`;
  btn.setAttribute("aria-expanded", "true");
  root.querySelector("button")?.focus();
}
function closeProblems() { $("#popover-root").innerHTML = ""; $("#problems-btn").setAttribute("aria-expanded", "false"); }

// ------------------------------------------------------------------ settings (AI provider key)
async function refreshHealth() {
  const r = await get("/api/health");
  if (r.ok) { S.health = r.data; renderToolbar(); renderRail(); }
}

const PROVIDER_INFO = {
  anthropic: { label: "Anthropic (Claude)", placeholder: "sk-ant-...", defaultModel: "claude-sonnet-5", envVar: "ANTHROPIC_API_KEY", getKeyUrl: "console.anthropic.com" },
  gemini: { label: "Google (Gemini)", placeholder: "AIza...", defaultModel: "gemini-3.8-flash", envVar: "GEMINI_API_KEY", getKeyUrl: "aistudio.google.com" },
};

function settingsStatusBox(d) {
  const sourceTxt = { settings: "saved in this tool's settings", environment: `from the ${PROVIDER_INFO[d.provider]?.envVar || "environment"} variable`, none: "not configured" }[d.source] || d.source;
  if (!d.configured) {
    return alertBox("info", "", "No API key configured. The AI layer runs offline: it can still retrieve evidence and list matching library risks, but nothing is drafted by a model.", { attrs: ' id="set-status"' });
  }
  return alertBox("ok", "", `${h(PROVIDER_INFO[d.provider]?.label || d.provider)} key configured (${h(sourceTxt)}): <span class="mono">${h(d.masked_key || "")}</span>, model <span class="mono">${h(d.model)}</span>.`, { attrs: ' id="set-status"' });
}

function openSettings() {
  get("/api/settings").then((r) => {
    const d = r.ok ? r.data : { configured: false, source: "none", provider: "anthropic", masked_key: null, model: "claude-sonnet-5", settings_path: "" };
    const provider = d.provider || "anthropic";
    const dlg = openModal({
      title: `${icon("gear")} Settings`,
      body: `
        ${settingsStatusBox(d)}
        <div class="form-grid">
          <div class="field span-2">
            <label for="set-provider">Provider</label>
            <select id="set-provider" class="input">
              ${Object.entries(PROVIDER_INFO).map(([id, info]) => `<option value="${id}" ${id === provider ? "selected" : ""}>${h(info.label)}</option>`).join("")}
            </select>
            <div class="hint">Which LLM API this key belongs to. Switching providers does not clear the other provider's saved key/model, but only one is active at a time.</div>
          </div>
          <div class="field span-2">
            <label for="set-key" id="set-key-label">API key</label>
            <div class="input-with-btn">
              <input id="set-key" type="password" class="input mono" placeholder="${d.configured ? "leave blank to keep the saved key" : PROVIDER_INFO[provider].placeholder}" autocomplete="off" spellcheck="false">
              <button type="button" class="btn btn-ghost btn-icon" id="set-key-eye" aria-label="Show key" title="Show/hide">${icon("eye")}</button>
            </div>
            <div class="hint" id="set-key-hint">Stored outside this project folder (<span class="mono">${h(d.settings_path || "a per-user settings file")}</span>), so it is never included if you zip or submit the project. Leaving this blank and clicking Save keeps whatever is already saved; use Clear to remove it.</div>
          </div>
          <div class="field span-2">
            <label for="set-model">Model</label>
            <input id="set-model" type="text" class="input mono" value="${h(d.source === "none" ? "" : d.model || "")}" placeholder="${PROVIDER_INFO[provider].defaultModel}">
            <div class="hint" id="set-model-hint">Optional. Leave blank to use the default (${h(PROVIDER_INFO[provider].defaultModel)}).</div>
          </div>
        </div>
        <div id="set-test-result"></div>
        ${alertBox("warn", "What this key is used for", "One thing: proposing candidate risks for you to review, each tied to cited evidence and marked unverified. It never sets a probability, a delay or a place on the matrix. Those come from your inputs.")}`,
      footer: `
        <button type="button" class="btn btn-danger-ghost" id="set-clear" ${d.configured ? "" : "disabled"}>Clear saved key</button>
        <span class="sep" aria-hidden="true"></span>
        <button type="button" class="btn" id="set-test">Test connection</button>
        <button type="button" class="btn btn-primary" id="set-save">Save</button>`,
    });

    const providerSelect = dlg.querySelector("#set-provider");
    const keyInput = dlg.querySelector("#set-key");
    const modelInput = dlg.querySelector("#set-model");
    const testResult = dlg.querySelector("#set-test-result");
    providerSelect.addEventListener("change", () => {
      const info = PROVIDER_INFO[providerSelect.value];
      dlg.querySelector("#set-key-label").textContent = `${info.label} API key`;
      keyInput.placeholder = keyInput.value.trim() ? keyInput.placeholder : info.placeholder;
      modelInput.placeholder = info.defaultModel;
      dlg.querySelector("#set-model-hint").textContent = `Optional. Leave blank to use the default (${info.defaultModel}).`;
    });
    dlg.querySelector("#set-key-eye").addEventListener("click", () => {
      const showing = keyInput.type === "text";
      keyInput.type = showing ? "password" : "text";
      dlg.querySelector("#set-key-eye").innerHTML = icon(showing ? "eye" : "eyeOff");
    });
    dlg.querySelector("#set-test").addEventListener("click", async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true; btn.classList.add("is-busy");
      testResult.innerHTML = "";
      const res = await post("/api/settings/test", { api_key: keyInput.value.trim(), model: modelInput.value.trim(), provider: providerSelect.value });
      btn.disabled = false; btn.classList.remove("is-busy");
      const ok = res.ok && res.data.ok;
      testResult.innerHTML = alertBox(ok ? "ok" : "danger", ok ? "Connected" : "Could not connect", h(res.data.message || `HTTP ${res.status}`));
    });
    dlg.querySelector("#set-clear").addEventListener("click", async () => {
      if (!(await confirmModal("Clear the saved API key?", "The tool goes back to offline mode (evidence retrieval only). You can add a key again at any time.", "Clear key"))) return;
      const res = await post("/api/settings", { api_key: "" });
      if (res.ok) { await refreshHealth(); toast("API key cleared. AI is now in offline mode.", "info"); closeModal(); }
      else toast(`Could not clear the key: ${(res.data.problems || []).join("; ") || "unknown error"}`, "err");
    });
    dlg.querySelector("#set-save").addEventListener("click", async (e) => {
      const btn = e.currentTarget;
      const body = { model: modelInput.value.trim(), provider: providerSelect.value };
      if (keyInput.value.trim()) body.api_key = keyInput.value.trim();
      btn.disabled = true; btn.classList.add("is-busy");
      const res = await post("/api/settings", body);
      btn.disabled = false; btn.classList.remove("is-busy");
      if (res.ok) {
        await refreshHealth();
        toast(res.data.configured ? "Settings saved. AI is in guarded LLM mode." : "Settings saved.", "ok");
        closeModal();
      } else {
        testResult.innerHTML = alertBox("danger", "Could not save", h((res.data.problems || []).join("; ") || `HTTP ${res.status}`));
      }
    });
  });
}

const ACTIONS = {
  theme: () => setTheme(theme() === "dark" ? "light" : "dark"),
  settings: () => openSettings(),
  save: () => saveCase(),
  open: async () => { if (await guardDiscard("Opening a file")) $("#file-input").click(); },
  new: async () => {
    if (!(await guardDiscard("A new blank case"))) return;
    const r = await get("/api/template");
    if (r.ok) { loadCase(r.data, { msg: "New blank case." }); go("case"); }
  },
  example: async () => {
    if (!(await guardDiscard("The ILLUSTRATIVE example"))) return;
    const r = await get("/api/example");
    if (r.ok) loadCase(r.data, { msg: "ILLUSTRATIVE example loaded: every number is a placeholder, not evidence." });
  },
  "dl-report": () => downloadFrom("/api/report", "register.md"),
  "dl-csv": () => downloadFrom("/api/register-csv", "register.csv"),
  "toggle-edges": () => { S.ui.showEdges = !S.ui.showEdges; renderScreen(); },
  "dl-html": () => downloadFrom("/api/report-html", "risk_report.html"),
  "dl-svg": () => downloadFrom("/api/matrix-svg", "risk_matrix.svg"),
  "dl-png": () => downloadPng(),
  "modal-close": () => closeModal(),
  "ev-open": (b) => showEvidence(b.dataset.id),
  "ev-remove": (b) => {
    const arr = getPath(S.case, b.dataset.path) || [];
    setPath(S.case, b.dataset.path, arr.filter((x) => x !== b.dataset.id));
    changed({ rerender: true });
  },
  "card-toggle": (b) => { const k = b.dataset.key; S.ui.open.has(k) ? S.ui.open.delete(k) : S.ui.open.add(k); renderScreen(); },
  "risk-remove": (b) => { const i = +b.dataset.i; removeWithUndo("risks", i, `Risk ${S.case.risks[i]?.id || ""}`); },
  "risk-add-custom": () => {
    S.case.risks = S.case.risks || [];
    S.case.risks.push(newRisk(uniqueId("R-CUST-", riskIds())));
    openNewRisk(S.case.risks.length - 1, "Custom risk added. Give it a name, probability and delay with their sources.");
  },
  "lib-add": (b) => addRiskFromLibrary(b.dataset.risk),
  "lib-add-all": (b) => addAllFromLibrary(b.dataset.cat || ""),
  "add-flagged": (b) => addRiskFromLibrary(b.dataset.risk),
  "ai-accept": (b) => {
    const c = S.ui.suggest?.candidates?.[+b.dataset.i];
    if (!c) return;
    S.case.risks = S.case.risks || [];
    S.case.risks.push(newRisk(uniqueId("R-AI-", riskIds()), { name: c.name, category: c.category, description: c.mechanism, status: "AI-suggested-unverified", evidence_ids: [...(c.evidence_ids || [])] }));
    openNewRisk(S.case.risks.length - 1, "AI-suggested risk added as unverified. Its probability and delay are empty and must come from you or an expert.");
    ensureEvidence(c.evidence_ids).then((found) => { if (found) renderScreen(); });
  },
  "risk-tab": (b) => { S.ui.riskTab = b.dataset.val; renderScreen(); },
  "fact-bool": (b) => {
    S.case.facts = S.case.facts || {};
    if (b.dataset.val === "unknown") delete S.case.facts[b.dataset.fact];
    else S.case.facts[b.dataset.fact] = b.dataset.val === "true";
    S.ui.autoAddPending = true;
    changed({ rerender: true });
  },
  "fact-remove": (b) => { delete S.case.facts[b.dataset.fact]; changed({ rerender: true }); },
  goto: (b) => {
    closeProblems();
    go(b.dataset.screen);
    setTimeout(() => { const e = screenEl().querySelector(".field-err.show, [data-screen-problems]"); e?.scrollIntoView({ block: "center", behavior: "smooth" }); }, 150);
  },
};
const CHANGE_ACTIONS = {
  "ev-cited": (el) => { S.ui.evCitedOnly = el.checked; refreshEvList(); },
};

async function onClick(e) {
  const b = e.target.closest("[data-action]");
  if (!b) {
    if (!e.target.closest(".popover, #problems-btn")) closeProblems();
    return;
  }
  if (b.matches("input[type=checkbox], select")) return;   // handled on change
  const fn = ACTIONS[b.dataset.action];
  if (fn) { e.preventDefault(); await fn(b); }
}

async function onSubmit(e) {
  const f = e.target.closest("form[data-form]");
  if (!f) return;
  e.preventDefault();
  if (f.dataset.form === "suggest") {
    const q = f.querySelector("#suggest-q").value.trim();
    S.ui.suggestQuery = q;
    S.ui.suggestBusy = true; renderScreen();
    const res = await post("/api/suggest-risks", { activity_name: S.case.activity?.name || "Brick masonry", query: q });
    S.ui.suggestBusy = false;
    S.ui.suggest = res.ok ? res.data : { error: res.data?.problems || [`HTTP ${res.status}`] };
    if (S.ui.screen === "risks") renderScreen();
  }
}

// ------------------------------------------------------------------ tooltips
let tipTarget = null;
function showTip(el) {
  const tip = $("#tip");
  const text = el.dataset.tip;
  if (!text) return;
  if (el.classList.contains("navlink") && getComputedStyle(el.querySelector(".nav-label")).display !== "none") return;
  tipTarget = el;
  tip.textContent = text;
  tip.classList.add("show");
  tip.setAttribute("aria-hidden", "false");
  const r = el.getBoundingClientRect();
  const tw = tip.offsetWidth, th = tip.offsetHeight;
  let left = el.classList.contains("navlink") ? r.right + 8 : r.left + r.width / 2 - tw / 2;
  let top = el.classList.contains("navlink") ? r.top + r.height / 2 - th / 2 : r.bottom + 8;
  if (top + th > window.innerHeight - 44) top = r.top - th - 8;
  left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
  tip.style.left = `${left}px`; tip.style.top = `${Math.max(8, top)}px`;
}
function hideTip() { tipTarget = null; const t = $("#tip"); t.classList.remove("show"); t.setAttribute("aria-hidden", "true"); }

// ------------------------------------------------------------------ boot
async function boot() {
  initCursor();
  const bar = $("#topbar");
  const onScroll = () => bar.classList.toggle("is-scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  document.addEventListener("input", onInput);
  document.addEventListener("change", onChange);
  document.addEventListener("click", onClick);
  document.addEventListener("submit", onSubmit);
  document.addEventListener("mouseover", (e) => { const el = e.target.closest("[data-tip]"); if (el && el !== tipTarget) showTip(el); else if (!el && tipTarget) hideTip(); });
  document.addEventListener("focusin", (e) => { const el = e.target.closest("[data-tip]"); if (el) showTip(el); else hideTip(); });
  document.addEventListener("focusout", hideTip);
  window.addEventListener("scroll", hideTip, { passive: true });
  document.addEventListener("keydown", (e) => {
    if (e.target.matches(".chip-add") && e.key === "Enter") { e.preventDefault(); addEvidence(e.target); return; }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); saveCase(); }
    else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "o") { e.preventDefault(); ACTIONS.open(); }
    else if (e.key === "Escape") { closeProblems(); hideTip(); }
  });
  $("#problems-btn").addEventListener("click", (e) => { e.stopPropagation(); openProblems(); });
  $("#file-input").addEventListener("change", async (e) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    let c;
    try { c = JSON.parse(await f.text()); } catch (err) { toast(`${h(f.name)} is not valid JSON (${h(err.message)}).`, "err"); return; }
    if (!c || typeof c !== "object" || Array.isArray(c) || !("activity" in c || "project" in c)) { toast(`${h(f.name)} does not look like a case file (no activity/project block).`, "err"); return; }
    loadCase(c, { fileName: f.name, msg: `Opened ${h(f.name)}.` });
  });
  window.addEventListener("beforeunload", (e) => { if (isDirty()) { e.preventDefault(); e.returnValue = ""; } });

  const [health, meta, lib, rules, ev, tpl] = await Promise.all([
    get("/api/health"), get("/api/meta"), get("/api/risk-library"), get("/api/rules"), get("/api/evidence"), get("/api/template")]);
  if (![health, meta, lib, rules, ev, tpl].every((r) => r.ok)) {
    screenEl().innerHTML = alertBox("danger", "Could not load reference data from the local server", "Check the terminal where <code>python -m gui</code> is running.");
    return;
  }
  S.health = health.data; S.meta = meta.data; S.library = lib.data; S.rules = rules.data;
  S.evidenceList = ev.data.records;
  S.evidence = new Map(ev.data.records.map((r) => [r.id, r]));
  const dl = document.createElement("datalist");
  dl.id = "ev-ids";
  dl.innerHTML = ev.data.records.map((r) => `<option value="${h(r.id)}">${h(r.citation.slice(0, 80))}</option>`).join("");
  document.body.appendChild(dl);
  const id = (location.hash.match(/^#\/([\w-]+)/) || [])[1];
  S.ui.screen = BY_ID[id] ? id : "case";
  loadCase(tpl.data);
  window.FYP = { S, go };   // for inspection from the browser console
}

boot();
