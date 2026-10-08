// Screen 7: Cost, options & decision.
// The GUI computes nothing: it posts the case to /api/analyze (app.analysis) and shows what comes back.
import { S, caseKey } from "../state.js";
import { h } from "../util.js";
import { screenHead, alertBox, icon, field, paramWidget, fid } from "../ui.js";
import { renderMarkdown } from "../markdown.js";

const money = (v, nd = 0) => (v === null || v === undefined ? "n/a" : Number(v).toLocaleString("en-IN", { maximumFractionDigits: nd, minimumFractionDigits: nd }));
const pct = (v) => (v === null || v === undefined ? "n/a" : `${(v * 100).toFixed(1)}%`);

function stale() { return S.ui.analysis && S.ui.analysisKey !== caseKey(); }

function inputs() {
  const c = S.case || {};
  const cost = c.cost || {}, act = c.activity || {};
  const mits = c.mitigations || [];
  const rows = mits.map((m, i) => `<tr>
      <td><strong>${h(m.id || "")}</strong><div class="muted">${h(m.action || "")}</div></td>
      <td>${h(m.risk_id || "")}</td>
      <td>${paramWidget(`mitigations.${i}.cost`, m.cost, { label: `Cost of ${m.id}`, sm: true, unit: h(cost.currency || "INR") })}</td>
      <td>${m.p_after ? paramWidget(`mitigations.${i}.p_after`, m.p_after, { label: `Probability after ${m.id}`, sm: true, min: 0, max: 1 }) : '<span class="muted">not set</span>'}</td>
      <td>${m.delay_after ? `PERT ${h(m.delay_after.a)} / ${h(m.delay_after.m)} / ${h(m.delay_after.b)} d` : '<span class="muted">not set</span>'}</td>
    </tr>`).join("");
  return `<section class="card mb-5"><header class="card-h"><h2>Cost model</h2><span class="sub">every number needs a Source</span></header><div class="card-b"><div class="form-grid">
      ${field({ label: "Cost of one delay day", forId: fid("cost.cost_per_delay_day"), err: "cost.cost_per_delay_day", control: paramWidget("cost.cost_per_delay_day", cost.cost_per_delay_day, { label: "Cost per delay day", unit: h(cost.currency || "INR"), min: 0 }) })}
      ${field({ label: "Liquidated damages per day after the deadline", forId: fid("cost.ld_per_day_after_deadline"), control: paramWidget("cost.ld_per_day_after_deadline", cost.ld_per_day_after_deadline, { label: "Liquidated damages per day", unit: h(cost.currency || "INR"), min: 0, optional: true }) })}
      ${field({ label: "Deadline for this activity", forId: fid("activity.deadline_days"), control: paramWidget("activity.deadline_days", act.deadline_days, { label: "Deadline (working days)", unit: "working days", min: 0, optional: true }) })}
    </div></div></section>
  <section class="card mb-5"><header class="card-h"><h2>Candidate responses</h2><span class="sub">${mits.length} entered</span></header><div class="card-b">
    ${mits.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Response</th><th>Targets risk</th><th>Cost</th><th>Probability after</th><th>Delay after</th></tr></thead><tbody>${rows}</tbody></table></div>`
      : alertBox("info", "No responses entered yet", "The tool does not invent a response or its effect. Load the illustrative example to see the layout, or add responses in the case file (see docs/case_schema.md); the catalogue below lists where to look.")}
  </div></section>`;
}

function commandBanner(r) {
  const c = r.command, cmd = c.command;
  const kind = cmd === "AUTHORIZE MITIGATION" ? "ok" : cmd === "ACCEPT RISK" ? "info" : "warn";
  const f = c.figures || {};
  const extra = cmd === "AUTHORIZE MITIGATION"
    ? `<div class="muted">Mitigation cost ${money(f.mitigation_cost)} ${h(r.cost.currency)}; expected total cost saving ${money(f.expected_cost_saving_vs_accept)} ${h(r.cost.currency)}; expected delay avoided ${money(f.expected_delay_avoided_days, 2)} days.${f.runner_up_id ? ` Closest alternative is only ${money(f.runner_up_extra_cost)} ${h(r.cost.currency)} (${pct(f.runner_up_extra_cost_share)}) more expensive.` : ""}</div>` : "";
  const st = r.decision_stability;
  const stab = st ? `<div class="muted">Seed check (${h(st.seeds.join(", "))}): ${st.stable ? "the choice is <strong>stable</strong>." : "the choice <strong>changes with the seed</strong>, so it is not a firm result."}</div>` : "";
  return `<section class="card mb-5"><header class="card-h"><h2>${icon("sparkle")} Decision</h2><span class="sub">criterion: ${h(r.decision.criterion)}</span></header><div class="card-b">
    <div style="font-size:1.6rem;font-weight:700;margin-bottom:8px">${h(cmd)}</div>
    ${c.selected_option_id && c.selected_option_id !== "ACCEPT" ? `<div style="margin-bottom:6px">Preferred option: <strong>${h(c.selected_option_id)}</strong></div>` : ""}
    <p>${h(c.reason)}</p>${extra}${stab}
    <p class="muted"><em>${h(r.decision.caveat)}</em></p></div></section>`;
}

function optionsTable(r) {
  const cur = r.cost.currency, sel = r.decision.selected_option_id;
  const rows = r.decision.options.map((o) => `<tr${o.option_id === sel ? ' style="font-weight:600"' : ""}>
      <td>${h(o.label)}${o.option_id === sel ? " (preferred)" : ""}</td><td>${money(o.mitigation_cost)}</td><td>${money(o.residual_expected_cost)}</td>
      <td>${money(o.total_expected_cost)}</td><td>${Number(o.P90).toFixed(1)}</td><td>${o.p_exceed_deadline === null ? "n/a" : pct(o.p_exceed_deadline)}</td>
      <td>${o.admissible ? "yes" : "no: " + h((o.rejected_because || []).join("; "))}</td></tr>`).join("");
  return `<section class="card mb-5"><header class="card-h"><h2>Options compared</h2><span class="sub">same random draws for every option</span></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Option</th><th>Mitigation cost (${h(cur)})</th><th>Residual expected cost</th><th>Total expected cost</th><th>P90 (d)</th><th>P(T &gt; deadline)</th><th>Admissible</th></tr></thead><tbody>${rows}</tbody></table></div></div></section>`;
}

function emvTable(r) {
  const cur = r.cost.currency;
  const emv = Object.fromEntries(r.event_emv.map((x) => [x.risk_id, x]));
  const rows = r.value_at_stake.map((v) => `<tr><td>${h(v.risk_id)} ${h(v.name)}</td><td>${v.p}</td><td>${money(emv[v.risk_id]?.emv)}</td><td>${money(v.value_at_stake)}</td><td>${pct(v.share_of_expected_cost)}</td></tr>`).join("");
  const s = r.summary;
  return `<section class="card mb-5"><header class="card-h"><h2>Event EMV and value at stake</h2><span class="sub">${h(cur)}</span></header><div class="card-b">
    <p class="muted">Event EMV = p &times; (expected delay &times; cost per day + direct cost). Value at stake is the expected cost that disappears if the risk could not occur: the ceiling on what any response to it can be worth.</p>
    <p>Expected duration ${s.mean.toFixed(1)} d (expected delay ${s.expected_delay.toFixed(1)} d); P50 ${s.percentiles.P50.toFixed(1)}, P80 ${s.percentiles.P80.toFixed(1)}, P90 ${s.percentiles.P90.toFixed(1)}, P95 ${s.percentiles.P95.toFixed(1)} days. Expected delay cost ${money(r.cost.expected_cost)} ${h(cur)}.</p>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Risk</th><th>p</th><th>Event EMV</th><th>Value at stake</th><th>Share of expected cost</th></tr></thead><tbody>${rows}</tbody></table></div></div></section>`;
}

function sensitivity(r) {
  const ds = r.decision_sensitivity;
  if (!ds) return "";
  const rows = ds.rows.map((x) => `<tr><td>${x.multiplier}&times;</td><td>${money(x.cost_per_delay_day)}</td><td>${h(x.command)}: ${h(x.selected_option_id)}</td></tr>`).join("");
  return `<section class="card mb-5"><header class="card-h"><h2>Does the choice depend on the cost per delay day?</h2></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Multiplier</th><th>Cost per day</th><th>Preferred</th></tr></thead><tbody>${rows}</tbody></table></div><p class="muted">${h(ds.note)}</p></div></section>`;
}

function results() {
  const a = S.ui.analysis;
  if (S.ui.analysisBusy) return alertBox("info", "Running the simulation", "10,000 iterations per option; this takes a few seconds.");
  if (S.ui.analysisProblems) return alertBox("warn", "The analysis could not run", `<ul>${S.ui.analysisProblems.map((p) => `<li>${h(p)}</li>`).join("")}</ul>`);
  if (!a) return alertBox("info", "No analysis yet", "Enter the cost model and responses above (or load the illustrative example), then press <strong>Run analysis</strong>.");
  return `${stale() ? alertBox("info", "Inputs changed", "These results are from the previous inputs. Run the analysis again to update them.") : ""}
    <div${stale() ? ' class="is-stale-view"' : ""}>${commandBanner(a)}${optionsTable(a)}${emvTable(a)}${sensitivity(a)}
    <section class="card mb-5"><header class="card-h"><h2>Full report</h2><span class="sub">analysis.md</span></header><div class="card-b"><article class="md">${renderMarkdown(a.report_markdown || "")}</article></div></section></div>`;
}

export function render() {
  const actions = `<button type="button" class="btn" data-action="analysis-example">${icon("flask")}<span>Load illustrative example</span></button>
    <button type="button" class="btn btn-primary" data-action="analysis-run"${S.ui.analysisBusy ? " disabled" : ""}>${icon("sparkle")}<span>Run analysis</span></button>
    <button type="button" class="btn" data-action="analysis-dl"${S.ui.analysis ? "" : " disabled"}>${icon("download")}<span>analysis.md</span></button>`;
  return `${screenHead(7, "Cost, options & decision", "Turns the register's delay risks into a simulated schedule and cost, compares candidate responses on the same random draws, and states which option is <strong>preferred under the chosen criterion</strong>. Every cost and effect is your input with a Source; the tool never supplies one. Not a claim of optimality.", actions)}
  ${inputs()}<div id="analysis-live">${results()}</div>`;
}

export function refreshLive(root) {
  const slot = root.querySelector("#analysis-live");
  if (slot) slot.innerHTML = results();
}
