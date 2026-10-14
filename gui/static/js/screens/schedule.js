// Screen 1: Project schedule. Laid out like a scheduling program (task table on the left, Gantt bars on the right).
// The GUI computes nothing: /api/schedule/import reads the MSP XML and does the critical-path pass.
import { S } from "../state.js";
import { h } from "../util.js";
import { screenHead, alertBox, icon } from "../ui.js";
import { FACT_INFO } from "./rules.js";

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
  return { name: S.ui.schedName || "Project", start: S.ui.schedStart, calendar: S.ui.schedCal || defaultCalendar(), tasks: S.ui.schedRows.map((r) => ({ name: r.name, outline_level: r.outline_level, duration_days: r.duration_days, predecessors: String(r.predecessors || "").replace(/−/g, "-") })) };
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

const TABS = [["res", "Resources (labour)", "Labour"], ["mat", "Material & equipment", "Material & equipment"], ["site", "Site & schedule", "Site & schedule"]];
function taskInfo() {
  const i = (S.ui.schedSel || 0) - 1, r = S.ui.schedRows[i];
  const t = S.ui.schedule && S.ui.schedule.tasks.find((x) => x.id === i + 1);
  if (!r) return `<section class="card task-info"><h3>Task information</h3><p class="muted">Select a task (click its row number) to enter its labour, material and site data. These travel with the task into the analysis, like resource and task details in MS Project.</p></section>`;
  if (t && t.summary) return `<section class="card task-info"><h3>Task information</h3><p class="muted">Row ${i + 1} is a summary task. Select a task inside it.</p></section>`;
  const tab = S.ui.schedTab || "res";
  const grp = (TABS.find((x) => x[0] === tab) || TABS[0])[2];
  const facts = r.facts || {};
  const items = (S.meta?.facts || []).filter((f) => (FACT_INFO[f.name] || {}).group === grp).map((f) => {
    const info = FACT_INFO[f.name], v = facts[f.name];
    if (f.type === "boolean") {
      const cur = v === true ? "true" : v === false ? "false" : "unknown";
      return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div class="seg sm tri" role="group" aria-label="${h(info.label)}">${[["unknown", "Unknown"], ["true", "Yes"], ["false", "No"]].map(([val, lab]) =>
        `<button type="button" data-action="sched-fact-bool" data-fact="${h(f.name)}" data-val="${val}" aria-pressed="${cur === val}">${lab}</button>`).join("")}</div></div>`;
    }
    return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div class="num-u"><input class="msp-in boxed" inputmode="decimal" placeholder="unknown" value="${h(v ?? "")}" data-action-change="sched-fact-num" data-i="${i}" data-f="fact:${f.name}"><span class="unit">${h(info.unit || "")}</span></div></div>`;
  }).join("");
  return `<section class="card task-info"><h3>Task information <span class="muted">— ${i + 1}: ${h(r.name || "(unnamed)")}</span></h3>
    <div class="seg sm" role="tablist">${TABS.map(([k, lab]) => `<button type="button" role="tab" data-action="sched-tab" data-val="${k}" aria-pressed="${tab === k}">${lab}</button>`).join("")}</div>
    <div class="ti-grid">${items || '<p class="muted">Loading the fact list…</p>'}</div>
    <p class="hint">Only what you fill in is carried over. “Unknown” stays unknown and the rules treat it as not evaluable. Press “Use selected task for analysis” to copy this task, its duration and these site facts into the case.</p></section>`;
}

function editable(sc) {
  const rows = S.ui.schedRows;
  const byId = new Map((sc ? sc.tasks : []).map((t) => [t.id, t]));
  const total = Math.max(sc ? sc.project.finish_days : 1, 1);
  const px = Math.max(4, Math.min(40, 560 / total));
  const gw = Math.ceil(total * px) + 40;
  const cols = `46px 280px 76px 92px 92px 130px 70px 74px 62px 44px ${gw}px`;
  const ticks = [];
  const step = total > 120 ? 20 : total > 40 ? 10 : 5;
  for (let d = 0; d <= total; d += step) ticks.push(`<span class="g-tick" style="left:${(d * px).toFixed(1)}px">${d}</span>`);
  const head = `<div class="msp-row msp-head" style="grid-template-columns:${cols}"><div>ID</div><div>Task name</div><div class="r">Dur. (d)</div><div>Start</div><div>Finish</div><div>Predecessors</div><div class="r">Workers</div><div class="r">Stock (d)</div><div class="r">Float (d)</div><div>Crit.</div><div class="g-cell g-axis">${ticks.join("")}</div></div>`;
  const body = rows.map((r, i) => {
    const id = i + 1, t = byId.get(id) || {};
    const sel = S.ui.schedSel === id;
    const sum = !!t.summary;
    const bar = t.es === undefined ? "" : sum
      ? `<span class="g-sum" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, (t.ef - t.es) * px).toFixed(1)}px"></span>`
      : t.milestone ? `<span class="g-ms" style="left:${(t.es * px - 6).toFixed(1)}px" title="milestone"></span>`
        : `<span class="g-bar ${t.critical ? "crit" : ""}" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, t.duration_days * px).toFixed(1)}px"></span>`;
    const mas = t.masonry_like ? ` <span class="badge b-accent" title="The name suggests brick, block or masonry work">masonry?</span>` : "";
    const inp = (f, v, extra = "") => `<input class="msp-in" ${extra} value="${h(v)}" data-action-change="sched-edit" data-i="${i}" data-f="${f}" aria-label="${f} of task ${id}">`;
    return `<div class="msp-row${sel ? " is-sel" : ""}${sum ? " is-sum" : ""}" style="grid-template-columns:${cols}" role="row">
      <div class="faint" data-action="sched-pick" data-uid="${id}" title="Select this row" tabindex="0">${id}</div>
      <div class="msp-name" style="padding-left:${(r.outline_level - 1) * 14}px">${inp("name", r.name, 'placeholder="Task name"')}${mas}</div>
      <div>${sum ? `<span class="muted r">${num(t.ef - t.es, 2)}</span>` : inp("duration_days", r.duration_days, 'inputmode="decimal" style="text-align:right"')}</div>
      <div>${h(dt(t.start))}</div><div>${h(dt(t.finish))}</div>
      <div>${sum ? "" : inp("predecessors", r.predecessors, 'placeholder="e.g. 2, 3SS+1d"')}</div>
      <div>${sum ? "" : finp(i, "required_workers", r)}</div><div>${sum ? "" : finp(i, "material_stock_days", r)}</div>
      <div class="r">${sum || t.total_float_days === undefined ? "" : num(t.total_float_days, 2)}</div>
      <div>${sum ? "" : t.critical ? '<span class="crit-dot" title="on the critical path"></span>' : ""}</div>
      <div class="g-cell">${bar}</div></div>`;
  }).join("");
  return `<div class="msp" role="table" aria-label="Project schedule" style="--row:${ROW}px">${head}${body}</div>`;
}

function toolbar() {
  const has = S.ui.schedSel != null, i = (S.ui.schedSel || 0) - 1, n = S.ui.schedRows.length;
  const b = (a, ic, label, dis = false, tip = "") => `<button type="button" class="btn btn-sm" data-action="${a}"${dis ? " disabled" : ""} title="${tip || label}">${icon(ic)}<span>${label}</span></button>`;
  return `<div class="msp-tools" role="toolbar" aria-label="Task tools">
    <label class="msp-start">Project name <input class="msp-in" value="${h(S.ui.schedName || "")}" data-action-change="sched-meta" data-f="name" placeholder="Project"></label>
    <label class="msp-start">Start date <input class="msp-in" type="date" value="${h(S.ui.schedStart || "")}" data-action-change="sched-meta" data-f="start"></label>
    ${b("sched-add", "plus", "Add task", false, "Add a task under the selected row (or at the end)")}
    ${b("sched-del", "trash", "Delete", !has, "Delete the selected task")}
    ${b("sched-out", "chevLeft", "Outdent", !has || i < 1 && true, "Move the task up one outline level")}
    ${b("sched-in", "chevRight", "Indent", !has || i < 1, "Make the task part of the summary above it")}
    ${b("sched-up", "chevUp", "Move up", !has || i < 1)}
    ${b("sched-down", "chevDown", "Move down", !has || i >= n - 1)}
  </div>`;
}

function empty() {
  return `${alertBox("info", "No schedule yet", "Type the tasks straight into the table, as in Microsoft Project, or open a schedule saved from MS Project (<strong>File › Save As › XML Format</strong>). Primavera and native .mpp files are not read yet.")}
  <p class="muted">In the table: the row number is the task ID. Type a duration in working days and the predecessors as <code>3</code> (finish-to-start), <code>3SS+2d</code> (start-to-start, 2 days lag), <code>4FF-1d</code> and so on. Indent a task under the row above to make that row a summary task. The critical path, float and Gantt bars update as you edit. Then pick the masonry task to assess; its planned duration and the room it has before the project finish move are carried into the analysis.</p>`;
}

function table(sc) {
  const rows = sc.tasks;
  const total = Math.max(sc.project.finish_days, 1);
  const px = Math.max(4, Math.min(40, 620 / total));
  const gw = Math.ceil(total * px) + 40;
  const cols = `46px 340px 100px 92px 92px 130px 72px 50px ${gw}px`;
  const ticks = [];
  const step = total > 120 ? 20 : total > 40 ? 10 : 5;
  for (let d = 0; d <= total; d += step) ticks.push(`<span class="g-tick" style="left:${(d * px).toFixed(1)}px">${d}</span>`);
  const head = `<div class="msp-row msp-head" style="grid-template-columns:${cols}"><div>ID</div><div>Task name</div><div class="r">Dur. (d)</div><div>Start</div><div>Finish</div><div>Predecessors</div><div class="r">Float (d)</div><div>Crit.</div><div class="g-cell g-axis">${ticks.join("")}</div></div>`;
  const body = rows.map((t) => {
    const sel = S.ui.schedSel === t.uid;
    const bar = t.es === undefined ? "" : t.summary
      ? `<span class="g-sum" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, (t.ef - t.es) * px).toFixed(1)}px"></span>`
      : t.milestone || t.duration_days === 0
        ? `<span class="g-ms" style="left:${(t.es * px - 6).toFixed(1)}px" title="milestone"></span>`
        : `<span class="g-bar ${t.critical ? "crit" : ""}" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, t.duration_days * px).toFixed(1)}px"><span class="g-pc" style="width:${Math.min(100, t.percent_complete || 0)}%"></span></span>`;
    const mas = t.masonry_like ? ` <span class="badge b-accent" title="The name suggests brick, block or masonry work">masonry?</span>` : "";
    return `<div class="msp-row${sel ? " is-sel" : ""}${t.summary ? " is-sum" : ""}" style="grid-template-columns:${cols}" data-action="sched-pick" data-uid="${t.uid}" role="row" tabindex="0">
      <div class="faint">${h(t.id)}</div>
      <div class="msp-name" style="padding-left:${(Math.max(1, t.outline_level) - 1) * 14}px">${t.summary ? "" : t.milestone ? "◆ " : ""}${h(t.name)}${mas}</div>
      <div class="r">${num(t.duration_days, 2)}</div><div>${h(dt(t.start))}</div><div>${h(dt(t.finish))}</div>
      <div class="muted">${h(predText(t))}</div>
      <div class="r">${t.summary ? "" : num(t.total_float_days, 2)}</div>
      <div>${t.summary ? "" : t.critical ? '<span class="crit-dot" title="on the critical path"></span>' : ""}</div>
      <div class="g-cell">${bar}</div></div>`;
  }).join("");
  return `<div class="msp" role="table" aria-label="Project schedule" style="--row:${ROW}px">${head}${body}</div>`;
}

export function render() {
  const sc = S.ui.schedule, rows = S.ui.schedRows;
  const sel = sc && S.ui.schedSel != null ? sc.tasks.find((t) => t.id === S.ui.schedSel) : null;
  const canUse = sel && !sel.summary;
  const bar = `<button type="button" class="btn btn-primary" data-action="sched-new">${icon("file")}<span>${rows ? "New schedule" : "Start a new schedule"}</span></button>
    <button type="button" class="btn" data-action="sched-open">${icon("folder")}<span>Open MSP XML file</span></button>
    <button type="button" class="btn" data-action="sched-use"${canUse ? "" : " disabled"} title="Copy the selected task into Case &amp; Activity">${icon("check")}<span>Use selected task for analysis</span></button>`;
  let info = "";
  if (S.ui.schedBusy) info = alertBox("info", "Reading the schedule", "");
  else if (S.ui.schedProblems) info = alertBox("warn", "The schedule could not be calculated", `<ul>${S.ui.schedProblems.map((p) => `<li>${h(p)}</li>`).join("")}</ul>`);
  const p = sc && sc.project;
  const summary = sc ? `<div class="tiles"><div class="tile"><div class="k">Project</div><div class="v" style="font-size:1.1rem">${h(p.name)}</div></div>
    <div class="tile"><div class="k">Tasks</div><div class="v">${p.leaf_tasks}<span class="u">of ${p.tasks}</span></div></div>
    <div class="tile"><div class="k">Project length</div><div class="v">${num(p.finish_days, 1)}<span class="u">working days</span></div></div>
    <div class="tile"><div class="k">Critical tasks</div><div class="v">${p.critical_tasks}</div></div></div>
    ${(sc.warnings || []).length ? alertBox("neutral", "Notes", `<ul>${sc.warnings.slice(0, 8).map((w) => `<li>${h(w)}</li>`).join("")}</ul>`) : ""}
    <p class="hint">${sel ? (sel.summary ? "That row is a summary task; pick one of the tasks inside it." : `Selected: <strong>${h(sel.name)}</strong> — ${num(sel.duration_days, 2)} d planned, ${num(sel.total_float_days, 2)} d total float.`) : "Click a row number to select a task. Tasks marked “masonry?” have brick, block or wall in the name."}</p>` : "";
  return `${screenHead(1, "Project schedule", "Same layout as a scheduling program: task table with durations, predecessors and float, and a Gantt chart. Type your tasks or open an MS Project file, then choose the masonry task to assess.", bar)}
  ${info}${rows ? summary + calendarPanel() + toolbar() + editable(sc) + taskInfo() : empty()}`;
}
