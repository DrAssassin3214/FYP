// Screen 1: Masonry schedule = the case and its activity. Laid out like a scheduling program (task table left, Gantt right, Task information
// tabs below). The GUI computes nothing: /api/schedule/compute and /import do the critical-path pass; the assessed task feeds the case.
import { S } from "../state.js";
import { h } from "../util.js";
import { screenHead, alertBox, icon, field, textInput, textArea, staleNote, fid } from "../ui.js";
import { screenProblems } from "../problems.js";
import { FACT_INFO, liveBlock } from "./rules.js";

const ROW = 26;
const num = (v, nd = 1) => (v === null || v === undefined ? "" : Number(v).toLocaleString("en-IN", { maximumFractionDigits: nd, minimumFractionDigits: 0 }));
const GL = 340;                                    // width of the task-name column in the Gantt chart
const dt = (s) => (s ? s.slice(0, 10) : "");

function predText(t, byUid) {
  return (t.predecessors || []).map((p) => {
    const lag = p.lag_days ? `${p.lag_days > 0 ? "+" : "−"}${num(Math.abs(p.lag_days), 2)}d` : "";
    return `${p.id ?? p.uid}${p.type}${lag}`;
  }).join(", ");
}


// ---- editable rows (typed like MSP: the row number is the task ID; predecessors are typed as 3, 3FS, 5SS+2d) ----
function workersFact(t) {
  const n = ((t.msp_resources || {}).labour || []).reduce((a, x) => a + (+x.units || 0), 0);
  return n > 0 ? { required_workers: Math.round(n) } : {};     // workers required from the MSP assignments of this task
}
export const blankRow = () => ({ name: "", outline_level: 1, duration_days: 0, predecessors: "", facts: {} });
export const defaultCalendar = () => ({ name: "Standard", workdays: [0, 1, 2, 3, 4], hours_per_day: 8, exceptions: [], events: [] });
export function rowsFromResult(res) {
  return res.tasks.map((t) => ({ name: t.name, outline_level: t.outline_level, duration_days: t.duration_days, predecessors: predText(t), facts: workersFact(t), msp_resources: t.msp_resources || null }));
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
  return { name: (S.case.project || {}).name || "Project", start: S.ui.schedStart, calendar: S.ui.schedCal || defaultCalendar(), tasks: S.ui.schedRows.map((r) => ({ name: r.name, outline_level: r.outline_level, duration_days: r.duration_days, predecessors: String(r.predecessors || "").replace(/−/g, "-"), start_no_earlier: r.start_no_earlier || "" })) };
}

const dateCell = (i, which, v, held) => `<input class="msp-in msp-date${held ? " is-held" : ""}" type="date" value="${h(v)}" data-action-change="sched-${which}" data-i="${i}" data-f="${which}" aria-label="${which === "start" ? "Start date (start no earlier than)" : "Finish date (sets the duration)"} of task ${i + 1}"${held ? ' title="Start held: this task cannot start before this date. Clear the date to release it."' : ""}>`;
const finp = (i, k, r) => `<input class="msp-in" inputmode="numeric" style="text-align:right" value="${h((r.facts || {})[k] ?? "")}" data-action-change="sched-fact-num" data-i="${i}" data-f="fact:${k}" aria-label="${k} of task ${i + 1}">`;
const matCell = (i, r) => {
  const dv = ((wplan(i) || {}).plan || {}).derived_facts || {}, v = dv.material_short !== undefined ? dv.material_short : (r.facts || {}).material_short;
  return v === true ? '<span class="badge b-warn">Short</span>' : v === false ? '<span class="badge b-ok">OK</span>' : "";
};
const EVENT_KINDS = [["monsoon", "Monsoon / heavy rain"], ["summer", "Extreme heat"], ["festival", "Festival, harvest or election"]];
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function calendarPanel() {
  const c = S.ui.schedCal || defaultCalendar();
  const ex = c.exceptions.map((e, i) => `<div class="cal-ex"><input class="msp-in" value="${h(e.name)}" placeholder="Name (e.g. Diwali)" data-action-change="sched-cal-ex" data-i="${i}" data-f="name">
    <input class="msp-in" type="date" value="${h(e.from)}" data-action-change="sched-cal-ex" data-i="${i}" data-f="from"><input class="msp-in" type="date" value="${h(e.to)}" data-action-change="sched-cal-ex" data-i="${i}" data-f="to">
    <select class="msp-in" data-action-change="sched-cal-ex" data-i="${i}" data-f="working"><option value="0"${e.working ? "" : " selected"}>Non-working</option><option value="1"${e.working ? " selected" : ""}>Working</option></select>
    <button type="button" class="btn btn-sm btn-ghost" data-action="sched-cal-del" data-i="${i}" aria-label="Remove exception">${icon("trash")}</button></div>`).join("");
  const evs = (c.events || []).map((e, i) => `<div class="cal-ex"><input class="msp-in" value="${h(e.name)}" placeholder="Name (e.g. Monsoon 2026)" data-action-change="sched-ev-set" data-i="${i}" data-f="name">
    <input class="msp-in" type="date" value="${h(e.from)}" data-action-change="sched-ev-set" data-i="${i}" data-f="from"><input class="msp-in" type="date" value="${h(e.to)}" data-action-change="sched-ev-set" data-i="${i}" data-f="to">
    <select class="msp-in" data-action-change="sched-ev-set" data-i="${i}" data-f="kind" aria-label="Kind of period">${EVENT_KINDS.map(([v, l]) => `<option value="${v}"${e.kind === v ? " selected" : ""}>${l}</option>`).join("")}</select>
    <button type="button" class="btn btn-sm btn-ghost" data-action="sched-ev-del" data-i="${i}" aria-label="Remove period">${icon("trash")}</button></div>`).join("");
  return `<div class="card cal-panel"><button type="button" class="cal-sum" data-action="sched-cal-toggle" aria-expanded="${!!S.ui.schedCalOpen}">${icon(S.ui.schedCalOpen ? "chevDown" : "chevRight")}<strong>Project calendar</strong> <span class="muted">— working days ${c.workdays.map((d) => DAYS[d]).join(" ")}, ${c.hours_per_day} h/day, ${c.exceptions.length} exception${c.exceptions.length === 1 ? "" : "s"}</span></button>
    ${S.ui.schedCalOpen ? `<div class="cal-body"><div class="cal-days" role="group" aria-label="Working weekdays">${DAYS.map((d, k) => `<label class="cal-day"><input type="checkbox" data-action-change="sched-cal-day" data-d="${k}"${c.workdays.includes(k) ? " checked" : ""}> ${d}</label>`).join("")}
      <label class="cal-day">Hours per day <input class="msp-in" type="number" min="1" max="24" step="0.5" style="width:70px" value="${h(c.hours_per_day)}" data-action-change="sched-cal-hpd"></label></div>
      <div class="cal-ex-head muted">Exceptions (holidays, festivals, rain stoppage; or an extra working day)</div>${ex}
      <button type="button" class="btn btn-sm" data-action="sched-cal-add">${icon("plus")}<span>Add exception</span></button>
      <div class="cal-ex-head muted">Seasons and festivals (they do not change working days; a task that overlaps one raises the monsoon, heat or festival flag by itself)</div>${evs}
      <button type="button" class="btn btn-sm" data-action="sched-ev-add">${icon("plus")}<span>Add season or festival</span></button>
      <p class="hint">Like Change Working Time in MS Project. Durations are counted in working days of this calendar; Start and Finish dates skip the days that are off. One calendar for the whole project (task and resource calendars are not modelled).</p></div>` : ""}</div>`;
}

const TABS = [["general", "General"], ["res", "Labour", "Labour"], ["mat", "Material & equipment", "Material & equipment"], ["site", "Site & schedule", "Site & schedule"], ["rules", "Rules"]];

const WORK_GROUPS = [["masons", "Masons"], ["helpers", "Helpers (mazdoor / coolie)"], ["bhisti", "Bhisti"]];
const wnum = (v) => (v === undefined || v === null ? "" : h(v));
const wplan = (i) => (S.ui.workPlans || {})[i] || null;

/** Quantity of masonry -> workers required, from a published labour norm; shortfall is flagged automatically. */
function workBlock(i, r) {
  const w = r.work || {}, norms = S.meta?.work_norms || [], norm = norms.find((n) => n.item_id === w.norm_id);
  const wp = wplan(i), plan = wp && wp.plan;
  const sel = `<select class="select msp-in boxed" data-action-change="work-set" data-i="${i}" data-f="norm_id" aria-label="Labour norm"><option value="">Choose a labour norm…</option>${norms.map((n) => `<option value="${h(n.item_id)}"${n.item_id === w.norm_id ? " selected" : ""}>${h(n.title)} (per ${h(n.unit)})</option>`).join("")}</select>`;
  const inp = (f, v, ph = "") => `<input class="msp-in boxed" inputmode="decimal" placeholder="${h(ph)}" value="${wnum(v)}" data-action-change="work-set" data-i="${i}" data-f="${f}">`;
  const eff = Number(w.efficiency) > 0 ? Number(w.efficiency) : 1, U = norm ? (norm.unit === "m3" ? "m³" : "m²") : "";
  const normPanel = norm ? `<table class="tbl work-tbl"><thead><tr><th>Taken from the norm</th><th class="r">Labour days per ${U}</th><th class="r">Output per worker per day</th></tr></thead><tbody>${(norm.groups || []).map((g) => `<tr><td>${h(g.label)}</td><td class="r">${num(g.constant_per_unit, 2)}</td><td class="r"><strong>${num(g.output_per_worker_day * eff, 2)}</strong> ${U}${eff !== 1 ? ` <span class="muted">(norm ${num(g.output_per_worker_day, 2)} × ${num(eff, 2)})</span>` : ""}</td></tr>`).join("")}</tbody></table>` : "";
  const need = (g) => { const x = plan && (plan.groups || []).find((y) => y.group === g); return x ? x.required_workers : null; };
  let out = "";
  if (!norms.length) out = `<div class="note-box"><strong>The labour norm list did not load.</strong> This page has the new screen, but the app's Python side is still the old version. Close the app completely and start it again (run_desktop.bat), then reopen this tab.</div>`;
  else if (!norm) out = `<p class="muted">Pick a labour norm and enter the quantity of work: the number of workers required is worked out from it, compared with the workers available, and a shortfall is flagged automatically (no yes/no question).</p>`;
  else if (!(r.duration_days > 0)) out = `<p class="muted">Enter this task's duration (Dur. column): the workers required are the work content divided by the days available.</p>`;
  else if (wp && wp.error) out = `<div class="note-box">${h(wp.error)}</div>`;
  else if (plan && plan.groups && plan.groups.length) {
    const rows = plan.groups.map((g) => `<tr${g.short ? ' class="short"' : ""}><td>${h(g.label)}</td><td class="r">${num(g.constant_per_unit, 2)}</td><td class="r">${num(g.person_days, 0)}</td><td class="r"><strong>${g.required_workers}</strong></td><td class="r">${g.available === null ? "–" : num(g.available, 0)}</td><td class="r">${g.available === null ? "" : g.short ? `<span class="badge b-warn">${icon("alert")}short by ${num(g.shortfall, 0)}</span>` : '<span class="badge b-ok">enough</span>'}</td></tr>`).join("");
    const slip = plan.implied_duration_days !== null && plan.implied_duration_days !== undefined
      ? `<p>With the workers available the work takes <strong>${num(plan.implied_duration_days, 1)} days</strong> (${plan.slip_days > 0.05 ? `<strong>${num(plan.slip_days, 1)} more</strong> than` : "within"} the planned ${num(plan.duration_days, 0)}), paced by ${h(((plan.groups.find((g) => g.group === plan.binding_group) || {}).label || "").toLowerCase())}.</p>` : "";
    const flags = plan.flags.filter((f) => f.group).map((f) => `<li class="${f.level === "elevated" ? "warn" : ""}">${h(f.message)}</li>`).join("");
    out = `<table class="tbl work-tbl"><thead><tr><th>Group</th><th class="r">Days per ${h(plan.unit)}</th><th class="r">Person-days</th><th class="r">Required</th><th class="r">Available</th><th></th></tr></thead><tbody>${rows}</tbody></table>
      <p class="hint">Required = person-days ÷ ${num(plan.duration_days, 0)} planned days, rounded up. ${plan.available_usable === null ? "" : `Usable workers ${num(plan.available_usable, 0)} of ${plan.required_total} needed (a surplus in one group does not cover a shortage in another).`}</p>
      ${slip}${flags ? `<ul class="work-flags">${flags}</ul>` : ""}
      <p class="hint">${h(plan.norm.citation)}. Planning norm, not measured site output${plan.efficiency === 1 ? "; lower the efficiency below 1 if your gang is slower than the norm" : ""}. ${plan.norm.conditions ? h(plan.norm.conditions) : ""}</p>`;
  }
  return `<div class="work-box"><div class="subhead">Work quantity &rarr; workers required</div>
    <div class="form-grid">
      <div class="fld wide"><div class="fld-l">Labour norm (IS 7272 / CPWD Analysis of Rates)</div>${sel}</div>
      <div class="fld"><div class="fld-l">Quantity of work</div><div class="num-u">${inp("quantity", w.quantity, "e.g. 1000")}<span class="unit">${norm ? h(norm.unit === "m3" ? "m³" : "m²") : ""}</span></div></div>
      <div class="fld"><div class="fld-l">Adjust for your gang (1 = exactly the norm)</div><div class="num-u">${inp("efficiency", w.efficiency, "1 = as the norm")}<span class="unit">×</span></div></div>
      ${WORK_GROUPS.map(([g, lab]) => `<div class="fld"><div class="fld-l">${h(lab)} available</div><div class="num-u">${inp("avail:" + g, (w.available || {})[g], need(g) !== null ? "needs " + need(g) : "number")}<span class="unit">workers</span></div>${need(g) !== null ? `<div class="hint">calculated from the quantity: <strong>${need(g)}</strong> needed</div>` : ""}</div>`).join("")}
      ${plan && plan.groups && plan.groups.length ? `<div class="fld"><button type="button" class="btn btn-sm" data-action="work-use-crew" data-i="${i}">Use the calculated crew</button><div class="hint">Fills the available boxes with the numbers needed. Replace them with who is actually on site to see a shortfall.</div></div>` : ""}
    </div>${normPanel}${out}</div>`;
}

/** Materials from the quantity of work: daily need, stock cover versus lead time (no default conversion factors). */
const RES_CLASSES = [["material", "Material (bricks, blocks)"], ["mortar", "Mortar material (sand, cement)"], ["equipment", "Equipment / tools"], ["machinery", "Machinery (hoist / lift)"], ["scaffolding", "Scaffolding"]];
/** Facts the listed items work out by themselves; the typed Yes/No is only a fallback when nothing is listed. */
const AUTO_FACTS = { material_short: "Bricks / blocks", material_stockout_before_delivery: "Bricks / blocks (with lead time)", mortar_stockout_before_delivery: "Sand / cement (with lead time)", tools_shortage: "Equipment / tools", hoist_available: "Machinery (hoist / lift)", scaffolding_ready: "Scaffolding (with its inspection result)" };

function materialBlock(i, r) {
  const w = r.work || {}, mats = w.materials || [], wp = wplan(i), plan = wp && wp.plan;
  const norm = (S.meta?.work_norms || []).find((n) => n.item_id === w.norm_id);
  const U = norm ? (norm.unit === "m3" ? "m³" : "m²") : "unit of work";
  const inp = (m, f, v, ph, w2 = "") => `<input class="msp-in boxed" ${w2} inputmode="${f === "name" || f === "unit" ? "text" : "decimal"}" placeholder="${h(ph)}" value="${wnum(v)}" data-action-change="work-mat-set" data-i="${i}" data-m="${m}" data-f="${f}">`;
  const rows = mats.map((m, k) => {
    const pm = plan && plan.materials[k], cls = m.class || "material", isMat = cls === "material" || cls === "mortar";
    const sel = `<select class="msp-in boxed" data-action-change="work-mat-set" data-i="${i}" data-m="${k}" data-f="class" aria-label="Type of resource">${RES_CLASSES.map(([v, l]) => `<option value="${v}"${cls === v ? " selected" : ""}>${h(l)}</option>`).join("")}</select>`;
    const need = isMat ? inp(k, "per_unit_of_work", m.per_unit_of_work, `per 1 ${U}`) : inp(k, "required", m.required, "count needed");
    const req = pm && pm.required !== null && pm.required !== undefined ? num(pm.required, isMat ? 0 : 0) : "";
    let status = "";
    if (cls === "scaffolding") status = `<select class="msp-in boxed" data-action-change="work-mat-set" data-i="${i}" data-m="${k}" data-f="safe_passed" aria-label="Passed the safety inspection"><option value="">Inspection: not stated</option><option value="yes"${m.safe_passed === true ? " selected" : ""}>Passed safe</option><option value="no"${m.safe_passed === false ? " selected" : ""}>Not passed</option></select> `;
    if (pm && pm.short === true) status += `<span class="badge b-warn">${icon("alert")}short by ${num(pm.shortfall, 0)}</span>${pm.stockout_before_delivery === true ? ' <span class="badge b-warn">before delivery</span>' : pm.stockout_before_delivery === false ? ' <span class="badge b-ok">delivery in time</span>' : ""}`;
    else if (pm && pm.short === false) status += '<span class="badge b-ok">enough</span>';
    return `<tr><td>${sel}</td><td>${inp(k, "name", m.name, "e.g. Bricks")}</td><td>${inp(k, "unit", m.unit, isMat ? "nos / bags / m³" : "nos")}</td><td>${need}</td><td class="r">${req}</td><td>${inp(k, "stock", m.stock, isMat ? "quantity on site" : "count available")}</td><td>${inp(k, "lead_time_days", m.lead_time_days, "dealer, days")}</td><td>${status}</td>
      <td><button type="button" class="btn btn-sm btn-danger-ghost" data-action="work-mat-del" data-i="${i}" data-m="${k}" aria-label="Remove resource">${icon("trash")}</button></td></tr>`;
  }).join("");
  return `<div class="work-box"><div class="subhead">Materials, equipment and machinery</div>
    ${w.quantity > 0 ? "" : `<p class="muted">Equipment, machinery and scaffolding are checked from their counts straight away. Bricks, sand and cement also need the quantity of work (Labour tab), because the quantity needed is worked out from it.</p>`}
    <table class="tbl work-tbl"><thead><tr><th>Type</th><th>Name</th><th>Unit</th><th>Per 1 ${U} / count needed</th><th class="r">Required</th><th>On site</th><th>Dealer lead time</th><th>Status</th><th></th></tr></thead><tbody>${rows || `<tr><td colspan="9" class="muted">Nothing added.</td></tr>`}</tbody></table>
    <button type="button" class="btn btn-sm" data-action="work-mat-add" data-i="${i}">${icon("plus")}Add resource</button>
    <p class="hint">Stock is a <b>quantity</b>, never a number of days. Materials and mortar: required = quantity of work × your per-unit factor (brick size, mix and wastage vary, so there is no default; recorded as User Input). Equipment and machinery: enter the count needed and the count available. Only the dealer's lead time is in days: if the on-site quantity supports less of the work than the lead time allows, the stock-out rule is raised. Machinery means the hoist or material lift. A count cannot show that scaffolding passed its safety inspection, so that one answer is stated on the scaffolding row. The flags below fill in by themselves from this table.</p></div>`;
}

const READY_KINDS = [["work_front", "Work front handed over (floor de-propped, cleared)"], ["frames", "Door and window frames on site"], ["mep", "MEP sleeve and conduit layout marked"], ["lintel", "Lintel and sill level plan issued"], ["design", "Drawings / design information issued"]];
const WALLS = [["", "Choose…"], ["external", "External walls"], ["internal", "Internal walls"], ["both", "External and internal walls"]];
/** Where each flag's data is entered, shown while the flag cannot be worked out yet. */
const FACT_HINT = {
  required_workers: "pick a labour norm and enter the quantity of work", available_workers: "enter the workers available (Labour tab)", skilled_masons_short: "pick a labour norm, the quantity and the masons available (Labour tab)",
  gang_payment_overdue: "enter the gang payment due date (Labour tab)", gang_mostly_migrant: "enter the migrant workers and the workers available (Labour tab)",
  festival_or_harvest_in_window: "add a festival, harvest or election period in the project calendar", monsoon_overlap: "add a monsoon period in the project calendar", summer_overlap: "add an extreme-heat period in the project calendar",
  work_at_height: "enter the floor, or list the scaffolding needed (Material tab)", external_walls_in_scope: "choose the wall location", payment_delay_expected: "enter the client payment due and expected dates",
  prior_rework_history: "enter the rework items recorded on earlier work", schedule_compressed: "enter the normal duration", design_incomplete: "add the drawings under Ready before work starts",
  work_front_ready: "add the work front under Ready before work starts", frames_on_site: "add the frames under Ready before work starts", mep_sleeve_layout_marked: "add the MEP layout under Ready before work starts", lintel_level_plan_issued: "add the lintel plan under Ready before work starts",
  planned_daily_output: "enter the quantity of work", masonry_floor_level: "enter the floor",
  material_short: "list the bricks / blocks in the Material tab", material_stockout_before_delivery: "list the bricks / blocks with their dealer lead time", mortar_stockout_before_delivery: "list the sand / cement with their dealer lead time",
  tools_shortage: "list the equipment with the count needed and available", hoist_available: "list the hoist / lift with the count needed and available", scaffolding_ready: "list the scaffolding, the amount needed and erected, and its inspection result",
};
const sInp = (i, f, v, ph, kind = "num") => `<input class="msp-in boxed" ${kind === "date" ? 'type="date"' : 'inputmode="decimal"'} placeholder="${h(ph || "")}" value="${kind === "date" ? h(v ?? "") : wnum(v)}" data-action-change="site-set" data-i="${i}" data-f="${f}" data-kind="${kind}">`;

/** Gang data (Labour tab): counts and dates, from which the migrant-gang and payment flags are worked out. */
function gangBlock(i, r) {
  const s = (r.work || {}).site || {};
  return `<div class="work-box"><div class="subhead">Gang</div><div class="form-grid">
    <div class="fld"><div class="fld-l">Migrant workers in the gang (home state far from site)</div><div class="num-u">${sInp(i, "migrant_workers", s.migrant_workers, "number")}<span class="unit">workers</span></div><div class="hint">Compared with the workers available above: more than half is flagged.</div></div>
    <div class="fld"><div class="fld-l">Gang payment due on</div>${sInp(i, "gang_pay_due", s.gang_pay_due, "", "date")}</div>
    <div class="fld"><div class="fld-l">Gang paid on (leave empty if unpaid)</div>${sInp(i, "gang_paid_on", s.gang_paid_on, "", "date")}<div class="hint">Overdue if paid after the due date, or still unpaid when the task starts.</div></div></div></div>`;
}

/** Site and schedule data: wall location, floor, dates and counts, from which the site flags are worked out. */
function siteBlock(i, r) {
  const w = r.work || {}, s = w.site || {}, ready = s.readiness || [], plan = (wplan(i) || {}).plan, st = (plan && plan.site) || {};
  const rrows = ready.map((x, k) => `<tr><td><select class="msp-in boxed" data-action-change="site-ready-set" data-i="${i}" data-k="${k}" data-f="kind" aria-label="Item">${READY_KINDS.map(([v, l]) => `<option value="${v}"${x.kind === v ? " selected" : ""}>${h(l)}</option>`).join("")}</select></td>
    <td><input class="msp-in boxed" type="date" value="${h(x.ready_by || "")}" data-action-change="site-ready-set" data-i="${i}" data-k="${k}" data-f="ready_by" aria-label="Ready by"></td>
    <td>${(st.readiness || [])[k] && st.readiness[k].ready_at_start === true ? '<span class="badge b-ok">ready at start</span>' : (st.readiness || [])[k] && st.readiness[k].ready_at_start === false ? `<span class="badge b-warn">${icon("alert")}after start</span>` : ""}</td>
    <td><button type="button" class="btn btn-sm btn-danger-ghost" data-action="site-ready-del" data-i="${i}" data-k="${k}" aria-label="Remove item">${icon("trash")}</button></td></tr>`).join("");
  const why = Object.entries(st.because || {}).map(([f, t]) => `<li><code>${h(f)}</code>: ${h(t)}</li>`).join("");
  const notes = (st.notes || []).map((t) => `<li>${h(t)}</li>`).join("");
  return `<div class="work-box"><div class="subhead">Site data (the flags below are worked out from it)</div><div class="form-grid">
    <div class="fld"><div class="fld-l">Walls in this task</div><select class="select msp-in boxed" data-action-change="site-set" data-i="${i}" data-f="wall_location" data-kind="text" aria-label="Wall location">${WALLS.map(([v, l]) => `<option value="${v}"${s.wall_location === v ? " selected" : ""}>${l}</option>`).join("")}</select></div>
    <div class="fld"><div class="fld-l">Floor (0 = ground floor)</div><div class="num-u">${sInp(i, "floor_level", s.floor_level, "0, 1, 2…")}<span class="unit">floor</span></div></div>
    <div class="fld"><div class="fld-l">Normal duration without acceleration</div><div class="num-u">${sInp(i, "normal_duration_days", s.normal_duration_days, "days")}<span class="unit">days</span></div><div class="hint">A planned duration shorter than this is flagged as compressed.</div></div>
    <div class="fld"><div class="fld-l">Rework items recorded on earlier work</div><div class="num-u">${sInp(i, "rework_items", s.rework_items, "count")}<span class="unit">items</span></div></div>
    <div class="fld"><div class="fld-l">Client payment due on</div>${sInp(i, "client_pay_due", s.client_pay_due, "", "date")}</div>
    <div class="fld"><div class="fld-l">Client payment expected on</div>${sInp(i, "client_pay_expected", s.client_pay_expected, "", "date")}<div class="hint">Flagged when it is expected after the due date.</div></div></div>
    <div class="subhead">Ready before work starts</div>
    <table class="tbl work-tbl"><thead><tr><th>Item</th><th>Ready by</th><th></th><th></th></tr></thead><tbody>${rrows || '<tr><td colspan="4" class="muted">Nothing added.</td></tr>'}</tbody></table>
    <button type="button" class="btn btn-sm" data-action="site-ready-add" data-i="${i}">${icon("plus")}Add item</button>
    <p class="hint">An item is ready if its date is on or before the task's start date; otherwise the matching flag is raised. Seasons and festivals come from the project calendar (Seasons and festivals), compared with this task's dates.</p>
    ${why || notes ? `<ul class="work-flags">${why}${notes}</ul>` : ""}</div>`;
}

function factFields(grp, row) {
  const facts = row.facts || {};
  return (S.meta?.facts || []).filter((f) => (FACT_INFO[f.name] || {}).group === grp).map((f) => {
    const info = FACT_INFO[f.name], v = facts[f.name];
    const dv = (((wplan((S.ui.schedSel || 1) - 1) || {}).plan || {}).derived_facts || {})[f.name];
    const because = ((((wplan((S.ui.schedSel || 1) - 1) || {}).plan || {}).site || {}).because || {})[f.name];
    const tag = `<div class="hint"><code>${h(f.name)}</code> · used by ${f.rules.map(h).join(", ")}</div>`;
    if (dv !== undefined) {                                     // worked out from the data entered: read-only, with its reason
      const shown = typeof dv === "boolean" ? (dv ? "Yes" : "No") : num(dv, 1);
      return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div><strong>${h(shown)}</strong> <span class="muted">${because ? "because " + h(because) : "worked out from the data entered"}</span></div>${tag}</div>`;
    }
    if (f.type === "boolean") {                                 // no Yes/No question: it is derived, or it is not known yet
      if (v === true || v === false) return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div><strong>${v ? "Yes" : "No"}</strong> <span class="muted">from the case file, not worked out from data</span> <button type="button" class="btn btn-sm btn-danger-ghost" data-action="sched-fact-remove" data-fact="${h(f.name)}">${icon("trash")}Clear</button></div>${tag}</div>`;
      return `<div class="fld"><div class="fld-l">${h(info.label)}</div><div class="muted">Not known yet. It fills in by itself once you ${h(FACT_HINT[f.name] || "enter the data")}.</div>${tag}</div>`;
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

/** Labour and material assignments read from the MS Project file for this task (read-only). */
function mspResources(r, tab) {
  const m = r && r.msp_resources;
  if (!m) return "";
  const list = tab === "res" ? (m.labour || []).map((x) => `${h(x.name)}: ${num(x.units, 2)} unit${x.units === 1 ? "" : "s"}`) : (m.material || []).map((x) => `${h(x.name)}: ${num(x.quantity, 2)} ${h(x.unit || "")}`);
  return list.length ? `<div class="note-box"><strong>From the MS Project file, this task:</strong> ${list.join("; ")}.${tab === "res" ? " Workers required was set from the work-resource units." : " Stock cover and lead time are not in MS Project; enter them below."}</div>` : "";
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
    body = `${mspResources(r, tab)}${tab === "res" ? workBlock(i, r) + gangBlock(i, r) : tab === "mat" ? materialBlock(i, r) : tab === "site" ? siteBlock(i, r) : ""}<div class="ti-grid">${factFields(grp, r) || '<p class="muted">Loading the fact list…</p>'}</div>${pdNote}
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

/** After opening an MSP file: what was read, what was left out, and how the tool's float and dates compare with MSP's own saved values. */
function importCheck() {
  const c = S.ui.schedCheck;
  if (!c) return "";
  const r = c.read || {}, bad = (c.slack_difference_count || 0) + (c.date_difference_count || 0), nm = c.not_modelled || [];
  const tbl = (rows, a, b) => rows.length ? `<table class="tbl"><thead><tr><th>ID</th><th>Task</th><th>${a}</th><th>${b}</th></tr></thead><tbody>${rows.map((d) => `<tr><td>${d.id}</td><td>${h(d.name)}</td><td>${d.tool_days !== undefined ? num(d.tool_days, 2) + " d" : h(d.tool.join(" to "))}</td><td>${d.msp_days !== undefined ? num(d.msp_days, 2) + " d" : h(d.msp.join(" to "))}</td></tr>`).join("")}</tbody></table>` : "";
  return `<section class="card import-check"><h3>Import check <span class="muted">— ${h(c.file || "")}</span> ${bad || nm.length ? '<span class="badge b-warn">Review</span>' : '<span class="badge b-ok">No differences found</span>'}</h3>
    <ul>
      ${c.scope && c.scope.mode === "masonry" ? `<li><strong>Scope:</strong> masonry tasks only — ${c.scope.kept} kept, ${c.scope.left_out} other task${c.scope.left_out === 1 ? "" : "s"} left out${(c.scope.left_out_examples || []).length ? ` (e.g. ${c.scope.left_out_examples.slice(0, 3).map(h).join("; ")})` : ""}. Their effect on the kept tasks' dates and float is kept through the “Programme start” and “Programme finish” rows. Labour and material: ${c.scope.assignments_used} assignment${c.scope.assignments_used === 1 ? "" : "s"} on the kept tasks used.</li>` : c.scope && c.scope.note ? `<li><strong>Scope:</strong> ${h(c.scope.note)}</li>` : ""}
      <li><strong>Read:</strong> ${r.tasks_read} of ${r.tasks_in_file} tasks, ${r.links_read} predecessor links${r.links_skipped ? `, ${r.links_skipped} links skipped (no predecessor id)` : ""}; project calendar and start date.</li>
      <li><strong>Float:</strong> ${c.slack_compared ? `${c.slack_compared - c.slack_difference_count} of ${c.slack_compared} tasks agree with MS Project's total slack (±0.01 d)` : "the file has no total-slack values to compare"}.</li>
      <li><strong>Dates:</strong> ${c.dates_compared ? `${c.dates_compared - c.date_difference_count} of ${c.dates_compared} start and finish dates agree with the ones MS Project saved` : "no saved dates to compare"}.</li>
      <li><strong>Critical flag:</strong> ${c.critical_compared ? `compared on ${c.critical_compared} tasks (differences are listed in Notes above)` : "not in the file"}.</li>
      <li><strong>In the file but not modelled:</strong> ${nm.length ? nm.map((x) => `${x.count} ${h(x.what)}`).join("; ") : "none found"}.</li></ul>
    ${tbl(c.slack_differences || [], "Tool float", "MSP total slack")}${tbl(c.date_differences || [], "Tool start – finish", "MSP start – finish")}
    ${bad ? '<p class="hint">A difference is not always an error: MS Project applies task calendars, constraints and manual dates that this tool ignores. Check the listed tasks in MS Project before relying on them.</p>' : ""}</section>`;
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

function ganttChart(sc) {
  if (!sc) return "";
  const rows = S.ui.schedRows, byId = new Map(sc.tasks.map((t) => [t.id, t]));
  const total = Math.max(sc.project.finish_days, 1);
  const px = Math.max(4, Math.min(40, 760 / total)), w = Math.ceil(total * px) + 40;
  const step = total > 120 ? 20 : total > 40 ? 10 : 5;
  const ticks = [];
  for (let d = 0; d <= total; d += step) ticks.push(`<span class="g-tick" style="left:${(d * px).toFixed(1)}px">${d}</span>`);
  const cols = `${GL}px ${w}px`;
  const vis = visibleIds(sc);
  const head = `<div class="msp-row msp-head" style="grid-template-columns:${cols}"><div>Task</div><div class="g-cell g-axis">${ticks.join("")}</div></div>`;
  const body = rows.map((r, i) => {
    const id = i + 1, t = byId.get(id) || {};
    if (vis && !vis.has(id)) return "";
    const sum = !!t.summary, sel = S.ui.schedSel === id;
    const bar = t.es === undefined ? "" : sum
      ? `<span class="g-sum" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, (t.ef - t.es) * px).toFixed(1)}px"></span>`
      : t.milestone ? `<span class="g-ms" style="left:${(t.es * px - 6).toFixed(1)}px" title="milestone"></span>`
        : `<span class="g-bar ${t.critical ? "crit" : ""}" style="left:${(t.es * px).toFixed(1)}px;width:${Math.max(2, t.duration_days * px).toFixed(1)}px" title="${h(dt(t.start))} to ${h(dt(t.finish))}"></span>`;
    return `<div class="msp-row${sel ? " is-sel" : ""}${sum ? " is-sum" : ""}" style="grid-template-columns:${cols}" role="row" data-action="sched-pick" data-uid="${id}" tabindex="0">
      <div class="msp-name" style="padding-left:${8 + (r.outline_level - 1) * 14}px" title="${h(r.name)}">${h(r.name || "(unnamed)")}</div><div class="g-cell">${bar}</div></div>`;
  }).join("");
  return `<section class="card"><header class="card-h"><h2>Gantt chart</h2><span class="hint">Working days from the programme start. <span class="g-key crit"></span> critical <span class="g-key"></span> not critical &#9670; milestone. Click a row to select it in the table below.</span></header><div class="card-b"><div class="msp msp-gantt" role="table" aria-label="Gantt chart" style="--row:${ROW}px">${head}${body}</div></div></section>`;
}

function editable(sc) {
  const rows = S.ui.schedRows;
  const byId = new Map((sc ? sc.tasks : []).map((t) => [t.id, t]));
  const cols = `58px 400px 76px 132px 132px 130px 70px 74px 62px 44px`;
  const head = `<div class="msp-row msp-head" style="grid-template-columns:${cols}"><div>ID</div><div>Task name</div><div class="r">Dur. (d)</div><div>Start</div><div>Finish</div><div>Predecessors</div><div class="r">Workers</div><div>Material</div><div class="r">Float (d)</div><div>Crit.</div></div>`;
  const vis = visibleIds(sc);
  const body = rows.map((r, i) => {
    const id = i + 1, t = byId.get(id) || {};
    if (vis && !vis.has(id)) return "";
    const sel = S.ui.schedSel === id;
    const sum = !!t.summary;
    const inp = (f, v, extra = "") => `<input class="msp-in" ${extra} value="${h(v)}" data-action-change="sched-edit" data-i="${i}" data-f="${f}" aria-label="${f} of task ${id}">`;
    return `<div class="msp-row${sel ? " is-sel" : ""}${sum ? " is-sum" : ""}" style="grid-template-columns:${cols}" role="row">
      <div class="faint" data-action="sched-pick" data-uid="${id}" title="${S.ui.schedAssess === id ? "Assessed task: its duration, float and facts feed the analysis. " : ""}Select this row" tabindex="0">${id}${S.ui.schedAssess === id ? ' <span class="star" aria-label="assessed task">★</span>' : ""}</div>
      <div class="msp-name" style="padding-left:${(r.outline_level - 1) * 14}px">${inp("name", r.name, 'placeholder="Task name"')}</div>
      <div>${sum ? `<span class="muted r">${num(t.ef - t.es, 2)}</span>` : inp("duration_days", r.duration_days, 'inputmode="decimal" style="text-align:right"')}</div>
      <div>${sum ? h(dt(t.start)) : dateCell(i, 'start', dt(t.start), !!r.start_no_earlier)}</div><div>${sum ? h(dt(t.finish)) : dateCell(i, 'finish', dt(t.finish), false)}</div>
      <div>${sum ? "" : inp("predecessors", r.predecessors, 'placeholder="e.g. 2, 3SS+1d"')}</div>
      <div>${sum ? "" : finp(i, "required_workers", r)}</div><div>${sum ? "" : matCell(i, r)}</div>
      <div class="r">${sum || t.total_float_days === undefined ? "" : num(t.total_float_days, 2)}</div>
      <div>${sum ? "" : t.critical ? '<span class="crit-dot" title="on the critical path"></span>' : ""}</div>
</div>`;
  }).join("");
  return `<div class="msp" role="table" aria-label="Masonry schedule" style="--row:${ROW}px">${head}${body}</div><p class="hint">Pick a <b>Start</b> date to hold a task back (it cannot start before that date; clear it to release). Pick a <b>Finish</b> date to set the duration in working days from the task's start. Both follow the project calendar.</p>`;
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
  ${screenProblems("schedule")}${info}${rows ? summary + importCheck() + ganttChart(sc) + calendarPanel() + toolbar() + editable(sc) + taskInfo() : alertBox("info", "Loading", "")}`;
}
