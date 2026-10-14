// Screen 1: Masonry schedule = the case and its activity. Laid out like a scheduling program (task table left, Gantt right, Task information
// tabs below). The GUI computes nothing: /api/schedule/compute and /import do the critical-path pass; the assessed task feeds the case.
import { S } from "../state.js";
import { h } from "../util.js";
import { screenHead, alertBox, icon, field, textInput, textArea, staleNote, fid } from "../ui.js";
import { screenProblems } from "../problems.js";
import { FACT_INFO, liveBlock } from "./rules.js";

const ROW = 26;
const num = (v, nd = 1) => (v === null || v === undefined ? "" : Number(v).toLocaleString("en-IN", { maximumFractionDigits: nd, minimumFractionDigits: 0 }));
const dt = (s) => (s ? s.slice(0, 10) : "");

function predText(t, byUid) {
  return (t.predecessors || []).map((p) => {
    const lag = p.lag_days ? `${p.lag_days > 0 ? "+" : "−"}${num(Math.abs(p.lag_days), 2)}d` : "";
    return `${p.id ?? p.uid}${p.type}${lag}`;
  }).join(", ");
}


// ---- editable rows (typed like MSP: the row number is the task ID; predecessors are typed as 3, 3FS, 5SS+2d) ----
export const blankRow = () => ({ name: "", outline_level: 1, duration_days: 0, predecessors: "", facts: {} });
export const defaultCalendar = () => ({ name: "Standard", workdays: [0, 1, 2, 3, 4], hours_per_day: 8, exceptions: [] });
export function rowsFromResult(res) {
  return res.tasks.map((t) => ({ name: t.name, outline_level: t.outline_level, duration_days: t.duration_days, predecessors: predText(t), facts: {} }));
}
/** Rewrite predecessor ids after rows are inserted, deleted or moved. map[oldId] = newId (missing = row deleted). */
export function remapPreds(rows, map) {
  rows.forEach((r) => {
    r.predecessors = String(r.predecessors || "").split(/[;,]/).map((x) => x.trim()).filter(Boolean).map((x) => {
      const m = x.match(/^(\d+)(.*)$/);
      if (!m) return x;
      const n = map[+m[1]];
      return n ? `${n}${m[2]}` : null;
    }).filter(Boolean).join(", ");
  });
}
export function rowsPayload() {
  return { name: (S.case.project || {}).name || "Project", start: S.ui.schedStart, calendar: S.ui.schedCal || defaultCalendar(), tasks: S.ui.schedRows.map((r) => ({ name: r.name, outline_level: r.outline_level, duration_days: r.duration_days, predecessors: String(r.predecessors || "").replace(/−/g, "-") })) };
}

const finp = (i, k, r) => `<input class="msp-in" inputmode="numeric" style="text-align:right" value="${h((r.facts || {})[k] ?? "")}" data-action-change="sched-fact-num" data-i="${i}" data-f="fact:${k}" aria-label="${k} of task ${i + 1}">`;
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function calendarPanel() {
  const c = S.ui.schedCal || defaultCalendar();
  const ex = c.exceptions.map((e, i) => `<div class="cal-ex"><input class="msp-in" value="${h(e.name)}" placeholder="Name (e.g. Diwali)" data-action-change="sched-cal-ex" data-i="${i}" data-f="name">
    <input class="msp-in" type="date" value="${h(e.from)}" data-action-change="sched-cal-ex" data-i="${i}" data-f="from"><input class="msp-in" type="date" value="${h(e.to)}" data-action-change="sched-cal-ex" data-i="${i}" data-f="to">
    <select class="msp-in" data-action-change="sched-cal-ex" data-i="${i}" data-f="working"><option value="0"${e.working ? "" : " selected"}>Non-working</option><option value="1"${e.working ? " selected" : ""}>Working</option></select>
    <button type="button" class="btn btn-sm btn-ghost" data-action="sched-cal-del" data-i="${i}" aria-label="Remove exception">${icon("trash")}</button></div>`).join("");
  return `<div class="card cal-panel"><button type="button" class="cal-sum" data-action="sched-cal-toggle" aria-expanded="${!!S.ui.schedCalOpen}">${icon(S.ui.schedCalOpen ? "chevDown" : "chevRight")}<strong>Project calendar</strong> <span class="muted">— working days ${c.workdays.map((d) => DAYS[d]).join(" ")}, ${c.hours_per_day} h/day, ${c.exceptions.length} exception${c.exceptions.length === 1 ? "" : "s"}</span></button>
    ${S.ui.schedCalOpen ? `<div class="cal-body"><div class="cal-days" role="group" aria-label="Working weekdays">${DAYS.map((d, k) => `<label class="cal-day"><input type="checkbox" data-action-change="sched-cal-day" data-d="${k}"${c.workdays.includes(k) ? " checked" : ""}> ${d}</label>`).join("")}
      <label class="cal-day">Hours per day <input class="msp-in" type="number" min="1" max="24" step="0.5" style="width:70px" value="${h(c.hours_per_day)}" data-action-change="sched-cal-hpd"></label></div>
      <div class="cal-ex-head muted">Exceptions (holidays, festivals, rain stoppage; or an extra working day)</div>${ex}
      <button type="button" class="btn btn-sm" data-action="sched-cal-add">${icon("plus")}<span>Add exception</span></button>
      <p class="hint">Like Change Working Time in MS Project. Durations are counted in working days of this calendar; Start and Finish dates skip the days that are off. One calendar for the whole project (task and resource calendars are not modelled).</p></div>` : ""}</div>`;
}

const TABS = [["general", "General"], ["res", "Labour", "Labour"], ["mat", "Material & equipment", "Material & equipment"], ["site", "Site & schedule", "Site & schedule"], ["rules", "Rules"]];

function factFields(grp, row) {
  const facts = row.facts || {};
  return (S.meta?.facts || []).filter((f) => (FACT_INFO[f.name] || {}).group === grp).map((f) => {
    const info = FACT_INFO[f.name], v = facts[f.name];
    if (f.type === "boolean") {
      const cur = v === true ? "true" : v === false ? "false" : "unknown";
      return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div class="seg sm tri" role="group" aria-label="${h(info.label)}">${[["unknown", "Unknown"], ["true", "Yes"], ["false", "No"]].map(([val, lab]) =>
        `<button type="button" data-action="sched-fact-bool" data-fact="${h(f.name)}" data-val="${val}" aria-pressed="${cur === val}">${lab}</button>`).join("")}</div><div class="hint"><code>${h(f.name)}</code> · used by ${f.rules.map(h).join(", ")}</div></div>`;
    }
    return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div class="num-u"><input class="msp-in boxed" inputmode="decimal" placeholder="unknown" value="${h(v ?? "")}" data-action-change="sched-fact-num" data-i="${(S.ui.schedSel || 1) - 1}" data-f="fact:${f.name}"><span class="unit">${h(info.unit || "")}</span></div><div class="hint"><code>${h(f.name)}</code> · used by ${f.rules.map(h).join(", ")}</div></div>`;
  }).join("");
}

function generalTab(i, r, t) {
  const p = S.case.project || {}, a = S.case.activity || {};
  const proj = `<div class="form-grid">
    ${field({ label: "Project name", forId: fid("project.name"), control: textInput("project.name", p.name, { placeholder: "e.g. Block B residential" }), cls: "wide" })}
    ${field({ label: "Location", forId: fid("project.location"), control: textInput("project.location", p.location, { placeholder: "City / site" }) })}
    ${field({ label: "Construction type", forId: fid("project.construction_type"), control: textInput("project.construction_type", p.construction_type, { placeholder: "e.g. Residential building" }) })}
    ${field({ label: "Notes", forId: fid("project.notes"), control: textArea("project.notes", p.notes, { rows: 2 }), cls: "wide" })}</div>`;
  let act = "";
  if (r && !(t && t.summary)) {
    const on = S.ui.schedAssess === i + 1, pd = a.planned_duration_days || {};
    act = on ? `<div class="subhead">Assessed activity (row ${i + 1}) ★</div><div class="form-grid">
      ${field({ label: "Activity ID", forId: fid("activity.id"), control: textInput("activity.id", a.id) })}
      <div class="fld"><div class="fld-l">Activity name</div><div>${h(r.name || "(unnamed)")}</div><div class="hint">From the task name in the table.</div></div>
      <div class="fld"><div class="fld-l">Planned duration</div><div>${h(pd.value ?? r.duration_days)} working days <span class="muted">(${h(pd.source || "User Input")})</span></div><div class="hint">From the Dur. column. The risk matrix measures each risk's impact as a fraction of this duration, and the material-stock rule uses it.</div></div>
      <div class="fld"><div class="fld-l">Room before the finish moves</div><div>${t && t.total_float_days !== undefined ? `${h(t.total_float_days)} d total float` : "—"}</div><div class="hint">From the critical-path pass; it sets the derived deadline unless you enter one on the Cost, options &amp; decision tab.</div></div></div>`
      : `<div class="subhead">Task ${i + 1}: ${h(r.name || "(unnamed)")}</div><p class="muted">This task is not the one the analysis is run on. Its labour, material and site data are kept with it. To run the risk analysis on this task press <button type="button" class="btn btn-sm" data-action="sched-assess">${icon("check")}<span>Assess this task</span></button></p>`;
  } else act = `<p class="muted">Select a task row (click its number) to see its activity details and enter its labour, material and site data.</p>`;
  return proj + act;
}

function taskInfo() {
  const i = (S.ui.schedSel || 0) - 1, r = S.ui.schedRows[i];
  const t = S.ui.schedule && S.ui.schedule.tasks.find((x) => x.id === i + 1);
  const tab = S.ui.schedTab && TABS.some((x) => x[0] === S.ui.schedTab) ? S.ui.schedTab : "general";
  const head = `<h3>Task information${r ? ` <span class="muted">— ${i + 1}: ${h(r.name || "(unnamed)")}${S.ui.schedAssess === i + 1 ? " ★ assessed" : ""}</span>` : ""}</h3>
    <div class="seg sm" role="tablist">${TABS.map(([k, lab]) => `<button type="button" role="tab" data-action="sched-tab" data-val="${k}" aria-pressed="${tab === k}">${lab}</button>`).join("")}</div>`;
  let body;
  if (tab === "general") body = generalTab(i, r, t);
  else if (!r || (t && t.summary)) body = `<p class="muted">${r ? "That row is a summary task; select a task inside it." : "Select a task row (click its number) first."}</p>`;
  else if (tab === "rules") {
    body = S.ui.schedAssess === i + 1
      ? `<p class="muted">Rules check the assessed task's site facts and only <strong>flag</strong> risks as relevant or elevated; they never produce probabilities. A blank fact is <em>unknown</em>: rules that need it are reported as not evaluable instead of guessed.</p><div id="rules-live">${staleNote()}${liveBlock()}</div>`
      : `<p class="muted">Rules run on the assessed task. Select the task marked ★, or press <strong>Assess this task</strong> for this one.</p>`;
  } else {
    const grp = TABS.find((x) => x[0] === tab)[2];
    const known = new Set((S.meta?.facts || []).map((f) => f.name));
    const extra = tab === "site" ? Object.keys(r.facts || {}).filter((k) => !known.has(k)) : [];
    const pdNote = tab === "site" && S.ui.schedAssess === i + 1 ? `<p class="hint"><code>planned_duration_days</code> is this task's duration (${h(r.duration_days)} d) and is used by rule RL-MAT2 (relevant only, not elevated).</p>` : "";
    body = `<div class="ti-grid">${factFields(grp, r) || '<p class="muted">Loading the fact list…</p>'}</div>${pdNote}
      ${extra.length ? `<div class="subhead">Other facts in this case file</div><ul>${extra.map((k) => `<li><code>${h(k)}</code> = ${h(JSON.stringify(r.facts[k]))} <button type="button" class="btn btn-sm btn-danger-ghost" data-action="sched-fact-remove" data-fact="${h(k)}">${icon("trash")}Remove</button></li>`).join("")}</ul>` : ""}
      <p class="hint">Only what you fill in is used. “Unknown” stays unknown and the rules treat it as not evaluable.${S.ui.schedAssess === i + 1 ? " These facts are the case's site facts." : " They take effect when this task is the assessed one."}</p>`;
  }
  return `<section class="card task-info">${head}<div class="ti-body">${body}</div></section>`;
}

/** Called after a re-check so the rule results inside Task information stay current. */
export function refreshLive(root) {
  const slot = root.querySelector("#rules-live");
  if (slot) slot.innerHTML = staleNote() + liveBlock();
}

/** Rows to show when "Masonry only" is on: masonry tasks, the summary rows above them, and the selected row. null = show all. */
function visibleIds(sc) {
  if (!S.ui.schedMasOnly || !sc) return null;
  const keep = new Set(), T = sc.tasks;
  T.forEach((t, i) => {
    if (t.masonry_like || t.id === S.ui.schedSel) {
      keep.add(t.id);
      for (let j = i - 1, lvl = t.outline_level; j >= 0; j--) if (T[j].outline_level < lvl) { keep.add(T[j].id); lvl = T[j].outline_level; }
    }
  });
  return keep.size ? keep : null;
}

function editable(sc) {
  const rows = S.ui.schedRows;
  const byId = new Map((sc ? sc.tasks : []).map((t) => [t.id, t]));
  const total = Math.max(sc ? sc.project.finish_days : 1, 1);
  const px = Math.max(4, Math.min(40, 560 / total));
  const gw = Math.ceil(total * px) + 40;
  const cols = `58px 400px 76px 92px 92px 130px 70px 74px 62px 44px ${gw}px`;
  const ticks = [];
  const step = total > 120 ? 20 : total > 40 ? 10 : 5;
  for (let d = 0; d <= total; d += step) ticks.push(`<span class="g-tick" style="left:${(d * px).toFixed(1)}px">${d}</span>`);
  const head = `<div class="msp-row msp-head" style="grid-template-columns:${cols}"><div>ID</div><div>Task name</div><div class="r">Dur. (d)</div><div>Start</div><div>Finish</div><div>Predecessors</div><div class="r">Workers</div><div class="r">Stock (d)</div><div class="r">Float (d)</div><div>Crit.</div><div class="g-cell g-axis">${ticks.join("")}</div></div>`;
  const vis = visibleIds(sc);
  const body = rows.map((r, i) => {
    const id = i + 1, t = byId.get(id) || {};
    if (vis && !vis.has(id)) return "";
    const sel = S.ui.schedSel === id;
    const sum = !!t.summary;
    const bar = t.es === undefined ? "" : sum
      ? `<span class="g-sum" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, (t.ef - t.es) * px).toFixed(1)}px"></span>`
      : t.milestone ? `<span class="g-ms" style="left:${(t.es * px - 6).toFixed(1)}px" title="milestone"></span>`
        : `<span class="g-bar ${t.critical ? "crit" : ""}" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, t.duration_days * px).toFixed(1)}px"></span>`;
    const mas = t.masonry_like ? ` <span class="badge b-accent" title="The name suggests brick, block or masonry work">masonry?</span>` : "";
    const inp = (f, v, extra = "") => `<input class="msp-in" ${extra} value="${h(v)}" data-action-change="sched-edit" data-i="${i}" data-f="${f}" aria-label="${f} of task ${id}">`;
    return `<div class="msp-row${sel ? " is-sel" : ""}${sum ? " is-sum" : ""}" style="grid-template-columns:${cols}" role="row">
      <div class="faint" data-action="sched-pick" data-uid="${id}" title="${S.ui.schedAssess === id ? "Assessed task: its duration, float and facts feed the analysis. " : ""}Select this row" tabindex="0">${id}${S.ui.schedAssess === id ? ' <span class="star" aria-label="assessed task">★</span>' : ""}</div>
      <div class="msp-name" style="padding-left:${(r.outline_level - 1) * 14}px">${inp("name", r.name, 'placeholder="Task name"')}${mas}</div>
      <div>${sum ? `<span class="muted r">${num(t.ef - t.es, 2)}</span>` : inp("duration_days", r.duration_days, 'inputmode="decimal" style="text-align:right"')}</div>
      <div>${h(dt(t.start))}</div><div>${h(dt(t.finish))}</div>
      <div>${sum ? "" : inp("predecessors", r.predecessors, 'placeholder="e.g. 2, 3SS+1d"')}</div>
      <div>${sum ? "" : finp(i, "required_workers", r)}</div><div>${sum ? "" : finp(i, "material_stock_days", r)}</div>
      <div class="r">${sum || t.total_float_days === undefined ? "" : num(t.total_float_days, 2)}</div>
      <div>${sum ? "" : t.critical ? '<span class="crit-dot" title="on the critical path"></span>' : ""}</div>
      <div class="g-cell">${bar}</div></div>`;
  }).join("");
  return `<div class="msp" role="table" aria-label="Masonry schedule" style="--row:${ROW}px">${head}${body}</div>`;
}

function toolbar() {
  const has = S.ui.schedSel != null, i = (S.ui.schedSel || 0) - 1, n = S.ui.schedRows.length;
  const b = (a, ic, label, dis = false, tip = "") => `<button type="button" class="btn btn-sm" data-action="${a}"${dis ? " disabled" : ""} title="${tip || label}">${icon(ic)}<span>${label}</span></button>`;
  return `<div class="msp-tools" role="toolbar" aria-label="Task tools">
    <label class="msp-start">Start date <input class="msp-in" type="date" value="${h(S.ui.schedStart || "")}" data-action-change="sched-meta" data-f="start"></label>
    ${b("sched-assess", "check", S.ui.schedAssess === S.ui.schedSel && has ? "Assessed task" : "Assess this task", !has || S.ui.schedAssess === S.ui.schedSel, "Make this the task the risk analysis is run on: its duration, float and site facts feed the case")}
    ${b("sched-add", "plus", "Add task", false, "Add a task under the selected row (or at the end)")}
    ${b("sched-del", "trash", "Delete", !has, "Delete the selected task")}
    ${b("sched-out", "chevLeft", "Outdent", !has || i < 1 && true, "Move the task up one outline level")}
    ${b("sched-in", "chevRight", "Indent", !has || i < 1, "Make the task part of the summary above it")}
    ${b("sched-up", "chevUp", "Move up", !has || i < 1)}
    ${b("sched-down", "chevDown", "Move down", !has || i >= n - 1)}
    <label class="cal-day"><input type="checkbox" data-action-change="sched-mas-only"${S.ui.schedMasOnly ? " checked" : ""}> Masonry tasks only</label>
  </div>`;
}

export function render() {
  const sc = S.ui.schedule, rows = S.ui.schedRows;
  const bar = `<button type="button" class="btn btn-primary" data-action="sched-open">${icon("folder")}<span>Open MSP XML file</span></button>`;
  let info = "";
  if (S.ui.schedBusy) info = alertBox("info", "Reading the schedule", "");
  else if (S.ui.schedProblems) info = alertBox("warn", "The schedule could not be calculated", `<ul>${S.ui.schedProblems.map((p) => `<li>${h(p)}</li>`).join("")}</ul>`);
  const p = sc && sc.project;
  const as = sc && sc.tasks.find((t) => t.id === S.ui.schedAssess);
  const summary = sc ? `<div class="tiles"><div class="tile"><div class="k">Assessed task ★</div><div class="v" style="font-size:1.05rem">${as ? h(as.name) : "none"}</div></div>
    <div class="tile"><div class="k">Tasks</div><div class="v">${p.leaf_tasks}<span class="u">of ${p.tasks}</span></div></div>
    <div class="tile"><div class="k">Programme length</div><div class="v">${num(p.finish_days, 1)}<span class="u">working days</span></div></div>
    <div class="tile"><div class="k">Critical tasks</div><div class="v">${p.critical_tasks}</div></div></div>
    ${(sc.warnings || []).length ? alertBox("neutral", "Notes", `<ul>${sc.warnings.slice(0, 8).map((w) => `<li>${h(w)}</li>`).join("")}</ul>`) : ""}` : "";
  return `${screenHead(1, "Masonry schedule", "The brick and block work of the building (external walls, internal walls, partitions, lintels, parapet) as a task table with durations, predecessors, calendar, float and a Gantt chart, like a scheduling program. Mark the task to assess with ★; its duration, float, labour, material and site data become the activity and site facts of the case. Type the tasks, or open an MS Project file saved as XML (Primavera and .mpp files are not read yet).", bar)}
  ${screenProblems("schedule")}${info}${rows ? summary + calendarPanel() + toolbar() + editable(sc) + taskInfo() : alertBox("info", "Loading", "")}`;
}
