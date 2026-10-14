// Screen 1: Project schedule. Laid out like a scheduling program (task table on the left, Gantt bars on the right).
// The GUI computes nothing: /api/schedule/import reads the MSP XML and does the critical-path pass.
import { S } from "../state.js";
import { h } from "../util.js";
import { screenHead, alertBox, icon } from "../ui.js";

const ROW = 26;
const num = (v, nd = 1) => (v === null || v === undefined ? "" : Number(v).toLocaleString("en-IN", { maximumFractionDigits: nd, minimumFractionDigits: 0 }));
const dt = (s) => (s ? s.slice(0, 10) : "");

function predText(t, byUid) {
  return (t.predecessors || []).map((p) => {
    const lag = p.lag_days ? `${p.lag_days > 0 ? "+" : "−"}${num(Math.abs(p.lag_days), 2)}d` : "";
    return `${p.id ?? p.uid}${p.type}${lag}`;
  }).join(", ");
}

function empty() {
  return `${alertBox("info", "No schedule loaded", "Open the project schedule exported from Microsoft Project: in MS Project choose <strong>File › Save As › XML Format</strong>, then press <strong>Open MSP XML file</strong> here. Primavera and native .mpp files are not read yet.")}
  <p class="muted">The tool reads task names, outline levels, durations, dates, predecessor links (FS, SS, FF, SF with lags) and works out the critical path in working days. You then pick the masonry task to assess; its planned duration and the room it has before the project finish move are carried into the analysis.</p>`;
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
  const sc = S.ui.schedule;
  const sel = sc && sc.tasks.find((t) => t.uid === S.ui.schedSel);
  const canUse = sel && !sel.summary;
  const bar = `<button type="button" class="btn btn-primary" data-action="sched-open">${icon("folder")}<span>Open MSP XML file</span></button>
    <button type="button" class="btn" data-action="sched-use"${canUse ? "" : " disabled"} title="Copy the selected task into Case &amp; Activity">${icon("check")}<span>Use selected task for analysis</span></button>`;
  let info = "";
  if (S.ui.schedBusy) info = alertBox("info", "Reading the schedule", "");
  else if (S.ui.schedProblems) info = alertBox("warn", "The schedule could not be read", `<ul>${S.ui.schedProblems.map((p) => `<li>${h(p)}</li>`).join("")}</ul>`);
  const p = sc && sc.project;
  const summary = sc ? `<div class="tiles"><div class="tile"><div class="k">Project</div><div class="v" style="font-size:1.1rem">${h(p.name)}</div></div>
    <div class="tile"><div class="k">Tasks</div><div class="v">${p.leaf_tasks}<span class="u">of ${p.tasks}</span></div></div>
    <div class="tile"><div class="k">Project length</div><div class="v">${num(p.finish_days, 1)}<span class="u">working days</span></div></div>
    <div class="tile"><div class="k">Critical tasks</div><div class="v">${p.critical_tasks}</div></div></div>
    ${(sc.warnings || []).length ? alertBox("neutral", "Notes on this import", `<ul>${sc.warnings.slice(0, 8).map((w) => `<li>${h(w)}</li>`).join("")}</ul>`) : ""}
    <p class="hint">${sel ? (sel.summary ? "That row is a summary task; pick one of the tasks inside it." : `Selected: <strong>${h(sel.name)}</strong> — ${num(sel.duration_days, 2)} d planned, ${num(sel.total_float_days, 2)} d total float.`) : "Click a task row to select it. Tasks marked “masonry?” have brick, block or wall in the name."}</p>` : "";
  return `${screenHead(1, "Project schedule", "Same layout as a scheduling program: task table with predecessors and float, and a Gantt chart. Import your site schedule, then choose the masonry task to assess.", bar)}
  ${info}${sc ? summary + table(sc) : empty()}`;
}
