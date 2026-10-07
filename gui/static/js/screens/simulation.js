// Screen 7: Simulation settings + results dashboard
import { h, fmt, fmtIn, fmtPct, isNum, valAttr } from "../util.js";
import { S, isStale, riskIds } from "../state.js";
import { field, numInput, selectInput, screenHead, alertBox, ul, term, staleNote, needRun, icon, ciText, serviceWarnings, tipIcon, runButton } from "../ui.js";
import { screenProblems } from "../problems.js";
import * as charts from "../charts.js";

export function criterionSelect(id = "f-crit") {
  const crit = S.case.simulation?.criterion || "min_expected_total_cost";
  const opts = Object.entries(S.meta?.criteria || {}).map(([k, v]) => ({ value: k, label: v }));
  return field({ label: "Decision criterion", forId: id, err: "simulation.criterion", control: selectInput("simulation.criterion", crit, opts, { id }),
    hint: "Options are ranked by this criterion among the admissible options evaluated." });
}

function corrEditor() {
  const rows = S.case.simulation?.correlation || [];
  const ids = riskIds();
  const opt = (v) => `<option value="">Select risk…</option>${ids.map((x) => `<option value="${h(x)}"${x === v ? " selected" : ""}>${h(x)}</option>`).join("")}${v && !ids.includes(v) ? `<option value="${h(v)}" selected>${h(v)} (not in register)</option>` : ""}`;
  return `${rows.map((c, i) => `<div class="corr-row">
      <select class="select select-sm" data-bind="simulation.correlation.${i}.a" data-t="sel" aria-label="Correlation ${i + 1}: risk A">${opt(c.a)}</select>
      <select class="select select-sm" data-bind="simulation.correlation.${i}.b" data-t="sel" aria-label="Correlation ${i + 1}: risk B">${opt(c.b)}</select>
      <input class="input input-sm" type="number" step="0.05" min="-1" max="1" data-bind="simulation.correlation.${i}.rho" data-t="num" value="${valAttr(c.rho)}" placeholder="rho -1..1" aria-label="Correlation ${i + 1}: rho">
      <button type="button" class="btn btn-danger-ghost btn-sm btn-icon" data-action="corr-remove" data-i="${i}" aria-label="Remove correlation ${i + 1}">${icon("trash")}</button></div>`).join("")}
    <button type="button" class="btn btn-sm" data-action="corr-add"${ids.length < 2 ? " disabled" : ""}>${icon("plus")}Add correlated pair</button>
    <div class="field-err" data-err="simulation.correlation" role="alert"></div>`;
}

function tile(k, v, unit, d = "", cls = "") {
  return `<div class="tile ${cls}"><div class="k">${k}</div><div class="v">${v}${unit ? `<span class="u">${unit}</span>` : ""}</div>${d ? `<div class="d">${d}</div>` : ""}</div>`;
}

export function render() {
  const sim = S.case.simulation || {};
  const r = S.result;
  const settings = `<section class="card"><header class="card-h"><h2>Simulation settings</h2><span class="sub">T = T0 + Σ Iᵢ·Dᵢ, ${term("Bernoulli occurrence", "bernoulli")}, ${term("common random numbers", "crn")}</span></header><div class="card-b">
    <div class="form-grid">
      ${field({ label: "Iterations (n)", forId: "f-sim-n", err: "simulation.n", control: numInput("simulation.n", sim.n, { t: "int", step: 1000, min: 1, max: S.meta?.max_n, id: "f-sim-n", placeholder: "e.g. 10000" }), hint: "More runs = smaller sampling error; tails need more runs than the mean." })}
      ${field({ labelHtml: term("Random seed", "seed"), forId: "f-sim-seed", control: numInput("simulation.seed", sim.seed, { t: "int", step: 1, id: "f-sim-seed" }) })}
      ${field({ labelHtml: term("Precision tolerance (optional)", "tolerance"), forId: "f-sim-tol", control: numInput("simulation.precision_tolerance_days", sim.precision_tolerance_days, { min: 0, unit: "days", id: "f-sim-tol", placeholder: "blank = fixed n" }) })}
      ${criterionSelect("f-crit-sim")}
    </div>
    <div class="subhead mt-4">${term("Correlated occurrence (optional)", "corr")}</div>
    ${corrEditor()}
    <div class="row mt-4">${runButton()}<span class="hint">Shortcut <span class="kbd">Ctrl</span>+<span class="kbd">Enter</span>. The same case + seed reproduce the same numbers.</span></div>
  </div></section>`;
  if (!r) return `${screenHead(7, "Simulation", "Monte Carlo simulation of the activity duration under the stated inputs.")}${screenProblems("simulation")}${settings}${needRun("the duration distribution, percentiles and sensitivity")}`;

  const s = r.summary, b = r.baseline, ci = s.percentile_ci95 || {};
  const dl = r.plots?.deadline;
  const tiles = `<div class="tiles">
    ${tile(term("Planned baseline T0", "planned"), fmt(b.planned_days, 2), "d", "Derived Calculation")}
    ${tile("Mean duration", fmt(s.mean, 2), "d", `SE ${fmt(s.mean_se, 3)} · sd ${fmt(s.std, 2)}`)}
    ${tile(term("Expected delay", "expdelay"), fmt(s.expected_delay, 2), "d", `P(any delay) ${fmtPct(s.p_any_delay)}`, "hl")}
    ${["P50", "P80", "P90", "P95"].map((k) => tile(term(k, "pct"), fmt(s.percentiles[k], 2), "d", ciText(ci[k], 2))).join("")}
    ${isNum(s.p_exceed_deadline) ? tile(term("P(T > deadline)", "pexceed"), fmtPct(s.p_exceed_deadline), "", `deadline ${fmtIn(dl)} d`, s.p_exceed_deadline > 0.5 ? "warn" : "") : tile("P(T > deadline)", "—", "", "no deadline entered")}
    ${tile(term("CVaR90", "cvar"), fmt(s.cvar_90, 2), "d", `CVaR95 ${fmt(s.cvar_95, 2)} d`)}
  </div>`;
  const pde = s.p_delay_exceeds || {};
  const sens = r.sensitivity || [];
  const ac = r.analytic_check;
  const analytic = ac
    ? alertBox("info", `${term("Analytic check", "analytic")}`, `Exact expected risk delay for independent risks = <strong>${fmt(ac.expected_delay, 3)} d</strong> (sd ${fmt(ac.std, 3)}); simulated expected delay = <strong>${fmt(s.expected_delay, 3)} d</strong> with n = ${fmtIn(r.n_used)}. They should agree within sampling error.`)
    : alertBox("neutral", `${term("Analytic check", "analytic")} not computed`, "The service computes the exact check only when risks are independent (no correlation) and the baseline duration is deterministic. Here a productivity range or a correlation is present, so rely on the convergence chart instead.");

  return `${screenHead(7, "Simulation", `Monte Carlo simulation of the activity duration: ${fmtIn(r.n_used)} iterations, seed ${h(s.seed)}. Results are a simulation under the stated inputs, not a prediction.`)}
  ${screenProblems("simulation")}
  ${staleNote()}
  ${serviceWarnings(r)}
  <div class="${isStale() ? "is-stale-view" : ""}">
  ${tiles}
  <div class="grid-2 mb-5">
    <section class="card chart-card"><header class="card-h"><h2>Duration distribution</h2><span class="sub">density, with P-lines and deadline</span></header><div class="card-b"><div class="chart" id="ch-hist" role="img" aria-label="Histogram of simulated activity duration"></div></div></section>
    <section class="card chart-card"><header class="card-h"><h2>Cumulative distribution (CDF)</h2><span class="sub">share of runs finishing within x days</span></header><div class="card-b"><div class="chart" id="ch-cdf" role="img" aria-label="Cumulative distribution of simulated duration"></div></div></section>
  </div>
  <section class="card"><header class="card-h"><h2>Percentiles</h2><span class="sub">table view</span></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Statistic</th><th class="r">Duration (d)</th><th class="r">95% CI (sampling)</th><th class="r">Delay vs T0 (d)</th></tr></thead><tbody>
    ${Object.keys(s.percentiles).map((k) => `<tr><td>${k}</td><td class="r">${fmt(s.percentiles[k], 2)}</td><td class="r">${ci[k] ? `${fmt(ci[k][0], 2)} – ${fmt(ci[k][1], 2)}` : "—"}</td><td class="r">${fmt(s.delay_percentiles?.[k], 2)}</td></tr>`).join("")}
    <tr><td>Min / Max</td><td class="r">${fmt(s.min, 2)} / ${fmt(s.max, 2)}</td><td></td><td></td></tr>
    ${Object.entries(pde).map(([x, p]) => `<tr><td>P(delay &gt; ${fmtIn(Number(x))} d)</td><td class="r">${fmtPct(p)}</td><td></td><td></td></tr>`).join("")}
    </tbody></table></div></div></section>
  <div class="grid-2 mb-5">
    <section class="card chart-card"><header class="card-h"><h2>${term("Sensitivity", "spearman")}: Spearman rank correlation</h2></header><div class="card-b"><div class="chart short" id="ch-sens"></div></div></section>
    <section class="card chart-card"><header class="card-h"><h2>${term("Share of expected delay", "share")}</h2></header><div class="card-b"><div class="chart short" id="ch-share"></div></div></section>
  </div>
  <section class="card"><header class="card-h"><h2>Sensitivity table</h2><span class="sub">descriptive association, not causation</span></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>#</th><th>Risk</th><th class="r">Spearman ρ with total delay</th><th class="r">Mean contribution (d)</th><th class="r">Share of expected delay</th></tr></thead><tbody>
    ${sens.map((x, i) => `<tr><td>${i + 1}</td><td class="mono">${h(x.risk_id)}</td><td class="r">${fmt(x.spearman_with_total_delay, 3)}</td><td class="r">${fmt(x.mean_contribution_days, 3)}</td><td class="r">${fmtPct(x.share_of_expected_delay)}</td></tr>`).join("")}
    </tbody></table></div>
    ${sens.some((x) => x.risk_id === "LATENT_PRODUCTIVITY") ? '<p class="card-note">LATENT_PRODUCTIVITY = routine variability of the baseline from the productivity range (not a risk event).</p>' : ""}
  </div></section>
  <section class="card chart-card"><header class="card-h"><h2>${term("Convergence", "convergence")}</h2><span class="sub">running statistics vs iterations</span></header><div class="card-b"><div class="chart" id="ch-conv"></div>
    <details class="tv"><summary>Show data table</summary><div class="tbl-wrap"><table class="tbl"><thead><tr><th class="r">n</th><th class="r">Mean</th><th class="r">P50</th><th class="r">P80</th><th class="r">P90</th></tr></thead><tbody>
    ${(r.convergence || []).map((c) => `<tr><td class="r">${fmtIn(c.n)}</td><td class="r">${fmt(c.mean, 3)}</td><td class="r">${fmt(c.P50, 3)}</td><td class="r">${fmt(c.P80, 3)}</td><td class="r">${fmt(c.P90, 3)}</td></tr>`).join("")}</tbody></table></div></details>
  </div></section>
  ${analytic}
  </div>
  ${settings}`;
}

export function after(root) {
  const r = S.result;
  if (!r) return;
  const s = r.summary;
  charts.histogram(root.querySelector("#ch-hist"), r.plots.duration_hist.ACCEPT, s.percentiles, r.plots.deadline);
  charts.cdf(root.querySelector("#ch-cdf"), [{ name: "Accept (no response)", cdf: r.plots.duration_cdf.ACCEPT }], r.plots.deadline);
  const sens = r.sensitivity || [];
  charts.barH(root.querySelector("#ch-sens"), sens.map((x) => ({ label: x.risk_id, value: x.spearman_with_total_delay, text: fmt(x.spearman_with_total_delay, 2) })), { xTitle: "Spearman ρ", range: [Math.min(0, ...sens.map((x) => x.spearman_with_total_delay)) - 0.05, 1.05] });
  charts.barH(root.querySelector("#ch-share"), sens.map((x) => ({ label: x.risk_id, value: x.share_of_expected_delay, text: fmtPct(x.share_of_expected_delay) })), { xTitle: "Share of expected delay", tickformat: ".0%" });
  charts.convergence(root.querySelector("#ch-conv"), r.convergence || []);
}
