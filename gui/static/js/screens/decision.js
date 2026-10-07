// Screen 9: Decision
import { h, fmt, fmtIn, fmtMoney, fmtPct, fmtSigned, isNum } from "../util.js";
import { S, isStale } from "../state.js";
import { screenHead, alertBox, ul, term, staleNote, needRun, icon, serviceWarnings, segmented, runButton } from "../ui.js";
import * as charts from "../charts.js";

/** P50 of an option read from the service's simulated CDF series (quantile 0.5). */
function p50Of(r, optId) {
  const c = r.plots?.duration_cdf?.[optId];
  if (!c) return null;
  const i = c.q.findIndex((q) => Math.abs(q - 0.5) < 1e-12);
  return i >= 0 ? c.days[i] : null;
}

export function defaultCompare(r) {
  const d = r.decision;
  const ids = d.options.map((o) => o.option_id);
  if (S.ui.compareOpt && ids.includes(S.ui.compareOpt)) return S.ui.compareOpt;
  if (d.selected_option_id && d.selected_option_id !== "ACCEPT") return d.selected_option_id;
  return ids.find((x) => x !== "ACCEPT") || null;
}

export function render() {
  const r = S.result;
  if (!r) return `${screenHead(9, "Decision", "Comparison of Accept and each option under the selected criterion.")}${needRun("the options table and the preferred option")}`;
  const d = r.decision, cur = r.cost.currency;
  const sel = d.selected_option_id;
  const hasDeadline = d.options.some((o) => isNum(o.p_exceed_deadline));
  const rows = d.options.map((o) => {
    const pref = o.option_id === sel;
    const cpd = isNum(o.mitigation_cost_per_day_avoided) ? `${fmtMoney(o.mitigation_cost_per_day_avoided)}<span class="sub">vs ${fmtMoney(o.delay_cost_per_day)} delay cost/day</span>`
      : `<span class="faint">—</span><span class="sub">${o.option_id === "ACCEPT" ? "reference" : o.mitigation_cost > 0 ? "no delay avoided" : "no mitigation cost"}</span>`;
    const adm = o.admissible ? `<span class="badge b-ok">${icon("check")}Yes</span>` : `<span class="badge b-danger">${icon("xCircle")}No</span><span class="sub">${o.rejected_because.map(h).join("; ")}</span>`;
    return `<tr class="${pref ? "is-preferred" : ""}${o.admissible ? "" : " is-rejected"}">
      <td><strong>${h(o.label)}</strong> ${pref ? `<span class="badge b-accent">${icon("star")}Preferred</span>` : ""}<span class="sub mono">${h(o.option_id)}${o.mitigations.length ? " · " + o.mitigations.map(h).join(" + ") : ""}</span></td>
      <td class="r">${fmtMoney(o.mitigation_cost)}</td><td class="r">${fmtMoney(o.residual_expected_cost)}</td><td class="r"><strong>${fmtMoney(o.total_expected_cost)}</strong></td>
      <td class="r">${fmt(o.expected_duration, 2)}</td><td class="r">${fmt(o.P90, 2)}</td>
      ${hasDeadline ? `<td class="r">${isNum(o.p_exceed_deadline) ? fmtPct(o.p_exceed_deadline) : "NR"}</td>` : ""}
      <td class="r">${cpd}</td><td>${adm}</td></tr>`;
  }).join("");

  const cmpId = defaultCompare(r);
  const acc = d.options.find((o) => o.option_id === "ACCEPT");
  const opt = d.options.find((o) => o.option_id === cmpId);
  let compare;
  if (!opt) {
    compare = `<section class="card"><div class="card-b">${alertBox("neutral", "No mitigation options to compare", "Define mitigations and options on step 8 to compare them with Accept.")}</div></section>`;
  } else {
    const metrics = [
      ["Expected duration", "d", acc.expected_duration, opt.expected_duration, 2],
      ["P50 duration", "d", p50Of(r, "ACCEPT"), p50Of(r, cmpId), 2],
      ["P80 duration", "d", acc.P80, opt.P80, 2],
      ["P90 duration", "d", acc.P90, opt.P90, 2],
      ["Expected delay", "d", acc.expected_delay, opt.expected_delay, 2],
      ...(hasDeadline ? [["P(T > deadline)", "%", acc.p_exceed_deadline, opt.p_exceed_deadline, 1]] : []),
      ["Total expected cost", cur, acc.total_expected_cost, opt.total_expected_cost, 0],
    ];
    const cell = (v, u, nd) => (u === "%" ? fmtPct(v, nd) : u === cur ? fmtMoney(v) : fmt(v, nd));
    const diff = (a, b, u, nd) => {
      if (!isNum(a) || !isNum(b)) return "—";
      const dv = b - a;
      const txt = u === "%" ? `${fmtSigned(dv * 100, nd)} pp` : u === cur ? `${dv > 0 ? "+" : dv < 0 ? "−" : "±"}${fmtMoney(Math.abs(dv))}` : `${fmtSigned(dv, nd)} d`;
      const word = Math.abs(dv) < 1e-12 ? "no change" : dv < 0 ? "lower" : "higher";
      return `<span class="${dv < 0 ? "delta-down" : dv > 0 ? "delta-up" : ""}">${txt}</span> <span class="sub" style="display:inline">${word}</span>`;
    };
    const optSel = `<label class="sr-only" for="cmp-sel">Option to compare</label><select id="cmp-sel" class="select select-sm" style="width:auto" data-action-change="compare">${d.options.filter((o) => o.option_id !== "ACCEPT").map((o) => `<option value="${h(o.option_id)}"${o.option_id === cmpId ? " selected" : ""}>${h(o.label)}${o.option_id === sel ? " (preferred)" : ""}</option>`).join("")}</select>`;
    compare = `<section class="card"><header class="card-h"><h2>Before / after: Accept vs ${h(opt.label)}</h2>${optSel}
        ${segmented([{ value: "hist", label: "Density" }, { value: "cdf", label: "CDF" }], S.ui.compareView, { action: "compare-view", sm: true, aria: "Chart type" })}</header>
      <div class="card-b"><div class="grid-2">
        <div><div class="chart" id="ch-cmp" role="img" aria-label="Duration distribution without and with the option"></div>
          <p class="chart-cap">Both series use the same random draws (${term("common random numbers", "crn")}); the vertical line is the deadline.</p></div>
        <div><div class="tbl-wrap"><table class="tbl"><thead><tr><th>Measure</th><th class="r">Without</th><th class="r">With</th><th class="r">Difference</th></tr></thead><tbody>
          ${metrics.map(([lab, u, a, b, nd]) => `<tr><td>${lab}${u === "d" ? " (d)" : ""}</td><td class="r">${cell(a, u, nd)}</td><td class="r">${cell(b, u, nd)}</td><td class="r">${diff(a, b, u, nd)}</td></tr>`).join("")}
        </tbody></table></div>
        <p class="card-note">P50 is read from the service's simulated CDF series; all other values from the options table. Total expected cost includes the mitigation cost.</p></div>
      </div></div></section>`;
  }

  return `${screenHead(9, "Decision", "Options are compared on the same simulated scenarios. The statement below is the service's own wording.", runButton("Re-run"))}
  ${staleNote()}
  <div class="${isStale() ? "is-stale-view" : ""}">
  <div class="statement" role="status"><div class="lab">${icon("scale", "ic-sm")}Decision-support statement (from the service)</div><div class="txt">${h(d.statement)}</div></div>
  ${alertBox("neutral", "Caveat", `<span class="caveat">${h(d.caveat)}</span>`)}
  ${serviceWarnings(r)}
  <section class="card"><header class="card-h"><h2>Decision rule</h2><span class="sub">criterion: ${h(r.criteria?.[d.criterion] || d.criterion)}</span></header><div class="card-b"><div class="rule-text">${h(d.rule)}</div></div></section>
  <section class="card"><header class="card-h"><h2>Options evaluated (${d.options.length})</h2><span class="sub">${term("TEC", "tec")} = mitigation cost + residual expected cost · ${term("admissible", "admissible")}</span></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Option</th><th class="r">Mitigation cost</th><th class="r">Residual E[cost]</th><th class="r">Total E[cost]</th><th class="r">E[duration] d</th><th class="r">P90 d</th>${hasDeadline ? '<th class="r">P(T&gt;deadline)</th>' : ""}<th class="r">${term("Cost / day avoided", "cpda")}</th><th>Admissible</th></tr></thead><tbody>${rows}</tbody></table></div>
    <p class="card-note">Currency: ${h(cur)}. ${sel ? `The highlighted row is preferred under the selected criterion among the ${d.options.filter((o) => o.admissible).length} admissible options evaluated.` : "No option is admissible under the constraints."}</p>
  </div></section>
  ${compare}
  </div>`;
}

export function after(root) {
  const r = S.result;
  if (!r) return;
  const cmpId = defaultCompare(r);
  const el = root.querySelector("#ch-cmp");
  if (!el || !cmpId) return;
  const lab = r.decision.options.find((o) => o.option_id === cmpId)?.label || cmpId;
  const cs = getComputedStyle(document.documentElement);
  const c1 = cs.getPropertyValue("--chart-1").trim(), c2 = cs.getPropertyValue("--chart-2").trim();
  if (S.ui.compareView === "cdf") {
    charts.cdf(el, [{ name: "Without (Accept)", cdf: r.plots.duration_cdf.ACCEPT, color: c1 }, { name: `With ${lab}`, cdf: r.plots.duration_cdf[cmpId], color: c2 }], r.plots.deadline);
  } else {
    charts.histOverlay(el, [{ name: "Without (Accept)", hist: r.plots.duration_hist.ACCEPT, color: c1 }, { name: `With ${lab}`, hist: r.plots.duration_hist[cmpId], color: c2 }], r.plots.deadline);
  }
}
