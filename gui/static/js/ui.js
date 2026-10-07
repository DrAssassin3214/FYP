// Reusable view components (return HTML strings) + toasts, tooltips and modals.
import { $, h, isNum, valAttr } from "./util.js";
import { S, isStale } from "./state.js";

// ------------------------------------------------------------------ icons (hand-drawn 24px strokes)
export const ICONS = {
  dots: '<circle cx="12" cy="5" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="12" cy="19" r="1.4"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  save: '<path d="M5 3h11l3 3v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M8 3v5h7V3M8 21v-7h8v7"/>',
  flask: '<path d="M9 3h6M10 3v6L5 18a2 2 0 0 0 1.7 3h10.6A2 2 0 0 0 19 18l-5-9V3"/><path d="M7.4 14.5h9.2"/>',
  play: '<path d="M7 4.8v14.4a.6.6 0 0 0 .9.5l11.2-7.2a.6.6 0 0 0 0-1L7.9 4.3a.6.6 0 0 0-.9.5z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
  moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
  alert: '<path d="M10.3 4.2 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z"/><path d="M12 9.5v4.5M12 17.2v.1"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.8v.1"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  checkCircle: '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.8 2.8L16.2 9.6"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  xCircle: '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
  minusCircle: '<circle cx="12" cy="12" r="9"/><path d="M8 12h8"/>',
  chevDown: '<path d="M6 9l6 6 6-6"/>',
  chevRight: '<path d="M9 6l6 6-6 6"/>',
  download: '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  sparkle: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5M8 7h8"/>',
  user: '<circle cx="12" cy="8" r="3.6"/><path d="M5 20.5a7 7 0 0 1 14 0"/>',
  building: '<path d="M4 21V5.5L12 3v18M12 8.5l8 2.2V21M2.5 21h19M7 8h2M7 12h2M7 16h2M15 13.5h2M15 17h2"/>',
  gauge: '<path d="M3.5 17a8.5 8.5 0 1 1 17 0"/><path d="M12 17l4.2-5.2"/><path d="M6.5 17h.1M17.5 17h.1"/>',
  rules: '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M4 6l1 1 2-2M4 12l1 1 2-2M4.5 18h1.5"/>',
  shield: '<path d="M12 3l8 3v6c0 4.9-3.4 8-8 9-4.6-1-8-4.1-8-9V6z"/><path d="M12 8.5v4.5M12 16v.1"/>',
  grid: '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M3.5 9.2h17M3.5 14.8h17M9.2 3.5v17M14.8 3.5v17"/>',
  rupee: '<path d="M6.5 4h11M6.5 8.5h11M6.5 4h3.5a4.5 4.5 0 0 1 0 9H6.5l8 7.5"/>',
  hist: '<path d="M3.5 20.5h17M6 20.5v-4M9.5 20.5V11M13 20.5V6.5M16.5 20.5v-8M20 20.5v-3"/>',
  sliders: '<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',
  scale: '<path d="M12 3.5v17M5 7h14M8.5 20.5h7M5 7l-2.8 6.5a3.2 3.2 0 0 0 5.6 0zM19 7l-2.8 6.5a3.2 3.2 0 0 0 5.6 0z"/>',
  message: '<path d="M4 5h16v11H9.5L4 20z"/><path d="M8 9h8M8 12.5h5"/>',
  doc: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  star: '<path d="M12 3.6l2.6 5.3 5.8.9-4.2 4.1 1 5.8L12 16.9l-5.2 2.8 1-5.8-4.2-4.1 5.8-.9z"/>',
  refresh: '<path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 4v5h-5"/>',
  undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  code: '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/>',
  layers: '<path d="M12 3 2.5 8 12 13l9.5-5z"/><path d="M2.5 12.5 12 17.5l9.5-5M2.5 16.5 12 21.5l9.5-5"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.2M12 18.8V21M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M3 12h2.2M18.8 12H21M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6"/>',
  eye: '<path d="M2.5 12s3.5-7 9.5-7 9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7z"/><circle cx="12" cy="12" r="2.8"/>',
  eyeOff: '<path d="M3 3l18 18"/><path d="M10.6 5.2A9.8 9.8 0 0 1 12 5c6 0 9.5 7 9.5 7a15.6 15.6 0 0 1-3 3.9M6.2 6.9A15.7 15.7 0 0 0 2.5 12s3.5 7 9.5 7a9.6 9.6 0 0 0 3.4-.6"/><path d="M9.5 12a2.8 2.8 0 0 0 4 2.5"/>',
};
export function icon(name, cls = "") {
  const fill = name === "play" || name === "star" ? " ic-fill" : "";
  return `<svg class="ic${fill} ${cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICONS[name] || ""}</svg>`;
}

// ------------------------------------------------------------------ glossary tooltips
export const TIPS = {
  source: "Source: where a number comes from - Literature, Historical Data, User Input, Expert Judgment, Derived Calculation or Assumption. Values marked Assumption or Expert Judgment need review before use.",
  bernoulli: "Occurrence model: the risk either occurs during the activity (with probability p) or it does not. If it occurs, it adds an extra delay drawn from the delay range you give.",
  p: "p = probability that the risk occurs at least once during this activity (an event probability, not a survey score or RII).",
  pert: "Beta-PERT: a smooth three-point distribution between min and max, peaked at the most likely value. Shape weight lambda = 4 is the conventional default.",
  planned: "Planned activity duration in working days. The matrix measures each risk's impact as a fraction of it.",
  matrix: "The risk matrix is ordinal prioritisation only: a label for attention, not a quantity of time or money.",
  evidence: "Evidence IDs refer to records in the evidence corpus (curated workbook, research notes, model registries and the literature harvest). Click an ID to read the citation and evidence depth.",
  status: "Risk status: literature-supported (existence backed by a cited record), expert/user-provided, or AI-suggested and unverified. Status never changes a number.",
  impact: "Impact class = expected delay if the risk occurs, divided by the planned duration, binned by the four edges you enter.",
};
export function term(label, key) {
  const t = TIPS[key] || key;
  return `<span class="term" tabindex="0" data-tip="${h(t)}">${h(label)}</span>`;
}
export function tipIcon(key, label = "What is this?") {
  const t = TIPS[key] || key;
  return `<span class="term-i" tabindex="0" role="img" aria-label="${h(label)}: ${h(t)}" data-tip="${h(t)}">${icon("info", "ic-sm")}</span>`;
}

// ------------------------------------------------------------------ provenance
export const SOURCE_META = {
  "Literature": { cls: "s-lit", g: "LIT", short: "Literature" },
  "Historical Data": { cls: "s-his", g: "HIS", short: "Historical" },
  "User Input": { cls: "s-usr", g: "USR", short: "User Input" },
  "Expert Judgment": { cls: "s-exp", g: "EXP", short: "Expert Judgment" },
  "Derived Calculation": { cls: "s-der", g: "DER", short: "Derived" },
  "Assumption": { cls: "s-asm", g: "ASM", short: "Assumption" },
};
export function srcMeta(s) { return SOURCE_META[s] || { cls: "s-none", g: "?", short: s ? `Unknown: ${s}` : "No source" }; }
/** Read-only source badge. Hidden by default; pass force=true where the Source itself is the content. */
export function sourceBadge(s, force = false) {
  if (!force) return "";
  const m = srcMeta(s);
  return `<span class="src ${m.cls}" title="Source: ${h(s || "not given")}"><span class="src-g" aria-hidden="true">${m.g}</span>${h(m.short)}</span>`;
}
/** Source selector. attrs: the data-* binding attributes. */
export function sourcePicker({ attrs, value, label = "Source", sm = false, optional = false }) {
  const m = srcMeta(value);
  const cls = !value && optional ? "s-opt" : m.cls;
  const list = S.meta?.sources || Object.keys(SOURCE_META);
  let opts = `<option value=""${!value ? " selected" : ""}>Select source…</option>`;
  if (value && !list.includes(value)) opts += `<option value="${h(value)}" selected>Unknown: ${h(value)}</option>`;
  opts += list.map((s) => `<option value="${h(s)}"${s === value ? " selected" : ""}>${h(s)}</option>`).join("");
  return `<span class="srcpick ${cls}${sm ? " sm" : ""}"><span class="src-g" aria-hidden="true">${!value && optional ? "–" : m.g}</span><select class="src-select" ${attrs} aria-label="${h(label)}">${opts}</select></span>`;
}
export function refreshSourcePicker(sel) {
  const wrap = sel.closest(".srcpick");
  if (!wrap) return;
  const optional = wrap.classList.contains("s-opt") || wrap.dataset.optional === "1";
  const m = srcMeta(sel.value);
  wrap.className = `srcpick ${!sel.value && optional ? "s-opt" : m.cls}${wrap.classList.contains("sm") ? " sm" : ""}`;
  const g = wrap.querySelector(".src-g");
  if (g) g.textContent = !sel.value && optional ? "–" : m.g;
}

// ------------------------------------------------------------------ status + evidence
export function statusBadge(st) {
  if (st === "literature-supported") return `<span class="st st-lit" title="Existence of this risk is supported by a cited record">${icon("book")}Literature-supported</span>`;
  if (st === "AI-suggested-unverified") return `<span class="st st-ai" title="Proposed by retrieval/AI; not verified by a person">${icon("sparkle")}AI-suggested, unverified</span>`;
  if (st === "expert/user-provided") return `<span class="st st-exp">${icon("user")}Expert / user-provided</span>`;
  return `<span class="st st-exp">${h(st || "no status")}</span>`;
}
export function evChip(id, removePath = null) {
  const rec = S.evidence.get(id);
  const tip = rec ? `${rec.citation}` : "Not found in the evidence corpus";
  const x = removePath
    ? `<button type="button" class="chip-x" data-action="ev-remove" data-path="${h(removePath)}" data-id="${h(id)}" aria-label="Remove evidence ${h(id)}">${icon("x")}</button>`
    : "";
  return `<span class="chip${rec ? "" : " is-missing"}"><button type="button" class="chip-open" data-action="ev-open" data-id="${h(id)}" data-tip="${h(tip)}" aria-label="Evidence ${h(id)}${rec ? "" : " (not in index)"}">${icon("book")}${h(id)}${rec ? "" : " ?"}</button>${x}</span>`;
}
export function evChips(ids, editPath = null) {
  const list = (ids || []).filter(Boolean);
  const chips = list.map((id) => evChip(id, editPath)).join("");
  const add = editPath ? `<input class="chip-add" data-ev-add="${h(editPath)}" placeholder="+ ID" aria-label="Add evidence ID (press Enter)" list="ev-ids" autocomplete="off">` : "";
  if (!chips && !add) return `<span class="faint">none</span>`;
  return `<span class="chips">${chips || (editPath ? "" : '<span class="faint">none</span>')}${add}</span>`;
}

// ------------------------------------------------------------------ form controls
export const fid = (path) => `f-${String(path).replace(/[^a-zA-Z0-9]+/g, "-")}`;

export function field({ label, labelHtml, tip, req = false, hint = "", err = null, control, cls = "", forId = null }) {
  const lab = labelHtml ?? h(label);
  return `<div class="field ${cls}">
    <label${forId ? ` for="${forId}"` : ""}>${lab}${req ? '<span class="req" title="required">*</span>' : ""}${tip ? " " + tipIcon(tip) : ""}</label>
    ${control}
    ${hint ? `<div class="hint">${hint}</div>` : ""}
    ${err ? `<div class="field-err" data-err="${h(err)}" role="alert"></div>` : ""}
  </div>`;
}
export function numInput(path, value, o = {}) {
  const { t = "num", step = "any", min, max, placeholder = "", cls = "", aria, nullMode, unit, sm = false } = o;
  const id = o.id || fid(path);
  const inp = `<input class="input${sm ? " input-sm" : ""} ${cls}" type="number" inputmode="decimal" step="${step}"${min !== undefined ? ` min="${min}"` : ""}${max !== undefined ? ` max="${max}"` : ""} id="${id}" data-bind="${h(path)}" data-t="${t}"${nullMode ? ` data-null="${nullMode}"` : ""} value="${valAttr(value)}" placeholder="${h(placeholder)}"${aria ? ` aria-label="${h(aria)}"` : ""} autocomplete="off">`;
  return unit ? `<div class="input-group">${inp}<span class="addon">${h(unit)}</span></div>` : inp;
}
export function textInput(path, value, o = {}) {
  const id = o.id || fid(path);
  return `<input class="input${o.sm ? " input-sm" : ""} ${o.cls || ""}" type="text" id="${id}" data-bind="${h(path)}" data-t="text" value="${valAttr(value)}" placeholder="${h(o.placeholder || "")}"${o.aria ? ` aria-label="${h(o.aria)}"` : ""}${o.rerender ? ' data-rerender="1"' : ""} autocomplete="off">`;
}
export function textArea(path, value, o = {}) {
  const id = o.id || fid(path);
  return `<textarea class="textarea" id="${id}" data-bind="${h(path)}" data-t="text" rows="${o.rows || 2}" placeholder="${h(o.placeholder || "")}"${o.aria ? ` aria-label="${h(o.aria)}"` : ""}>${h(value ?? "")}</textarea>`;
}
export function selectInput(path, value, options, o = {}) {
  const id = o.id || fid(path);
  const opts = options.map((x) => {
    const v = typeof x === "object" ? x.value : x;
    const l = typeof x === "object" ? x.label : x;
    return `<option value="${h(v)}"${String(v) === String(value ?? "") ? " selected" : ""}${x.disabled ? " disabled" : ""}>${h(l)}</option>`;
  }).join("");
  return `<select class="select${o.sm ? " select-sm" : ""} ${o.cls || ""}" id="${id}" data-bind="${h(path)}" data-t="${o.t || "sel"}"${o.rerender ? ' data-rerender="1"' : ""}${o.aria ? ` aria-label="${h(o.aria)}"` : ""}>${opts}</select>`;
}

/** Value + Source for a parameter object {value, source, evidence_ids, note}. */
export function paramWidget(path, param, o = {}) {
  const { label = "value", optional = false, placeholder = "", unit = null, step = "any", min, max, sm = false } = o;
  const p = param || {};
  const id = o.id || fid(path);
  const inp = `<input class="input${sm ? " input-sm" : ""}" type="number" inputmode="decimal" step="${step}"${min !== undefined ? ` min="${min}"` : ""}${max !== undefined ? ` max="${max}"` : ""} id="${id}" data-prole="value" value="${valAttr(p.value)}" placeholder="${h(placeholder)}" aria-label="${h(label)}" autocomplete="off">`;
  const group = unit ? `<div class="input-group">${inp}<span class="addon">${h(unit)}</span></div>` : inp;
  const note = p.note ? `<div class="param-note${/ILLUSTRATIVE|REQUIRED|placeholder/i.test(p.note) ? " illus" : ""}">${h(p.note)}</div>` : "";
  const evs = (p.evidence_ids || []).length ? `<div class="param-note">${evChips(p.evidence_ids)}</div>` : "";
  const src = sourcePicker({ attrs: 'data-prole="source"', value: p.source || "", label: `Source of ${label}`, sm, optional: optional && (p.value === null || p.value === undefined) });
  return `<div class="param" data-param="${h(path)}" data-optional="${optional ? 1 : 0}">${group}${src}${note}${evs}</div>`;
}

/** Delay distribution {kind, a, m, b, lam, source}. */
export function distWidget(path, d, o = {}) {
  const { optional = false, label = "Delay if it occurs" } = o;
  d = d || {};
  const kind = d.kind || "pert";
  const kinds = [["pert", "Beta-PERT"], ["triangular", "Triangular"], ["uniform", "Uniform"], ["fixed", "Fixed"]];
  const kindSel = `<div class="field"><label>Distribution</label><select class="select" data-drole="kind" aria-label="${h(label)}: distribution">${kinds.map(([v, l]) => `<option value="${v}"${v === kind ? " selected" : ""}>${l}</option>`).join("")}</select></div>`;
  const num = (role, lab, val) => `<div class="field"><label>${lab}</label><input class="input" type="number" inputmode="decimal" step="any" min="0" data-drole="${role}" value="${valAttr(val)}" placeholder="days" aria-label="${h(label)}: ${lab} (working days)" autocomplete="off"></div>`;
  let cells;
  if (kind === "fixed") cells = num("m", "Delay (d)", d.m) + "<div></div><div></div>";
  else if (kind === "uniform") cells = num("a", "Min (d)", d.a) + num("b", "Max (d)", d.b) + "<div></div>";
  else cells = num("a", "Min (d)", d.a) + num("m", "Most likely (d)", d.m) + num("b", "Max (d)", d.b);
  const allBlank = [d.a, d.m, d.b].every((x) => x === null || x === undefined);
  const src = sourcePicker({ attrs: 'data-drole="source"', value: d.source || "", label: `Source of ${label}`, optional: optional && allBlank });
  const lam = kind === "pert"
    ? `<div class="row mt-2"><label class="hint" for="${fid(path)}-lam">${term("PERT shape λ", "pert")}</label><input id="${fid(path)}-lam" class="input input-sm" style="width:110px" type="number" step="any" min="0" data-drole="lam" value="${valAttr(d.lam)}" placeholder="4 (default)" autocomplete="off"></div>`
    : "";
  return `<div class="dist-wrap" data-dist="${h(path)}" data-optional="${optional ? 1 : 0}"><div class="dist">${kindSel}${cells}${src}</div>${lam}</div>`;
}

export function segmented(options, value, o = {}) {
  return `<div class="seg${o.sm ? " sm" : ""}${o.cls ? " " + o.cls : ""}" role="group"${o.aria ? ` aria-label="${h(o.aria)}"` : ""}>${options.map((x) =>
    `<button type="button" data-action="${h(o.action)}" data-val="${h(x.value)}"${o.data || ""} aria-pressed="${String(x.value) === String(value)}">${x.icon ? icon(x.icon, "ic-sm") : ""}${h(x.label)}</button>`).join("")}</div>`;
}

// ------------------------------------------------------------------ blocks
export function screenHead(n, title, lede = "", actions = "") {
  return `<div class="screen-head"><span class="step">Step ${n}</span><div class="titles"><h1 tabindex="-1">${h(title)}</h1>${lede ? `<p class="lede">${lede}</p>` : ""}</div>${actions ? `<div class="actions">${actions}</div>` : ""}</div>`;
}
export function alertBox(kind, title, body = "", o = {}) {
  const ic = o.icon || { warn: "alert", danger: "alert", info: "info", neutral: "info", ok: "checkCircle" }[kind];
  return `<div class="alert alert-${kind}${o.cls ? " " + o.cls : ""}" role="${kind === "danger" ? "alert" : "note"}"${o.attrs || ""}>${icon(ic)}<div class="a-body">${title ? `<div class="a-title">${title}</div>` : ""}${body}</div></div>`;
}
export const ul = (items) => `<ul>${items.map((x) => `<li>${x}</li>`).join("")}</ul>`;
export function emptyState({ ic = "info", title, text = "", actions = "" }) {
  return `<div class="empty">${icon(ic)}<h3>${h(title)}</h3>${text ? `<p>${text}</p>` : ""}${actions}</div>`;
}
export function staleNote() {
  if (!isStale()) return "";
  return alertBox("warn", "Some inputs need fixing",
    "The register and matrix below are from the last valid state. They update as soon as the input problems are resolved.");
}
export function serviceWarnings(result, title = "Warnings returned by the service") {
  const w = result?.warnings || [];
  if (!w.length) return "";
  return alertBox("warn", `${title} (${w.length})`, ul(w.map((x) => h(x))));
}
export function ciText(ci, nd = 1) {
  if (!Array.isArray(ci) || !isNum(ci[0])) return "";
  return `95% CI ${ci[0].toFixed(nd)}–${ci[1].toFixed(nd)}`;
}

// ------------------------------------------------------------------ toasts
export function toast(msg, kind = "info", o = {}) {
  const root = $("#toasts");
  const el = document.createElement("div");
  el.className = `toast t-${kind}`;
  el.setAttribute("role", kind === "err" ? "alert" : "status");
  const ic = { ok: "checkCircle", err: "alert", info: "info" }[kind] || "info";
  el.innerHTML = `${icon(ic)}<span>${msg}</span>${o.actionLabel ? `<button type="button" class="linkbtn">${h(o.actionLabel)}</button>` : ""}`;
  if (o.actionLabel) el.querySelector("button").addEventListener("click", () => { o.onAction?.(); el.remove(); });
  root.appendChild(el);
  setTimeout(() => el.remove(), o.timeout || (kind === "err" ? 7000 : 3800));
}

// ------------------------------------------------------------------ modal dialogs
export function openModal({ title, body, footer = "" }) {
  const dlg = $("#modal");
  dlg.innerHTML = `<div class="modal-h"><h2 id="modal-title">${title}</h2><button type="button" class="btn btn-ghost btn-icon" data-action="modal-close" aria-label="Close">${icon("x")}</button></div>
    <div class="modal-b">${body}</div>${footer ? `<div class="modal-f">${footer}</div>` : ""}`;
  if (!dlg.open) dlg.showModal();
  return dlg;
}
export function closeModal() { const d = $("#modal"); if (d.open) d.close(); }
export function confirmModal(title, text, okLabel = "Continue") {
  return new Promise((resolve) => {
    const dlg = openModal({ title: h(title), body: `<p>${text}</p>`,
      footer: `<button type="button" class="btn" data-confirm="0">Cancel</button><button type="button" class="btn btn-primary" data-confirm="1">${h(okLabel)}</button>` });
    const done = (v) => { dlg.removeEventListener("click", onClick); dlg.removeEventListener("close", onClose); closeModal(); resolve(v); };
    const onClick = (e) => { const b = e.target.closest("[data-confirm]"); if (b) done(b.dataset.confirm === "1"); };
    const onClose = () => done(false);
    dlg.addEventListener("click", onClick);
    dlg.addEventListener("close", onClose);
    setTimeout(() => dlg.querySelector('[data-confirm="1"]')?.focus(), 0);
  });
}
export function showEvidence(id) {
  const r = S.evidence.get(id);
  if (!r) {
    openModal({ title: `Evidence ${h(id)}`, body: alertBox("warn", "Not found in the evidence index",
      `<p>The ID <code>${h(id)}</code> is not a record in the evidence corpus (curated workbook, research notes, model registries and the literature harvest). Check the ID on the Evidence screen or remove it; the tool does not invent citations.</p>`) });
    return;
  }
  const doi = r.doi ? `<a href="https://doi.org/${h(r.doi)}" target="_blank" rel="noopener noreferrer">${h(r.doi)}</a> <span class="faint">(opens only if you are online)</span>` : '<span class="faint">not recorded</span>';
  openModal({
    title: `${icon("book")} Evidence <span class="mono">${h(r.id)}</span>`,
    body: `<dl class="dl">
      <dt>Citation</dt><dd>${h(r.citation)}</dd>
      <dt>DOI</dt><dd>${doi}</dd>
      <dt>Context</dt><dd>${h(r.context || "NC")}</dd>
      <dt>Evidence depth</dt><dd>${h(r.evidence_depth || "NC")}</dd>
      <dt>Curated notes</dt><dd><div class="quote">${h(r.text || "none")}</div></dd>
    </dl>
    <p class="card-note">From Literature_Evidence_Package.xlsx. Notes are the curator's summary, not quotations; survey rankings (e.g. RII) indicate importance, not probability.</p>`,
  });
}
