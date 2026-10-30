// Screen 7: Cost, options & decision.
// The GUI computes nothing: it posts the case to /api/analyze (app.analysis) and shows what comes back.
import { S, caseKey } from "../state.js";
import { h } from "../util.js";
import { screenHead, alertBox, icon, field, paramWidget, fid } from "../ui.js";
import { renderMarkdown } from "../markdown.js";
import { chartsSection } from "../analysis_charts.js";

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
      : alertBox("info", "No responses entered yet", "The tool does not invent a response or its effect. Use Load example in the top bar to see the layout, or add responses in the case file (see docs/case_schema.md); the catalogue below lists where to look.")}
    <div class="mt-4"><button type="button" class="btn" data-action="online-find"${S.ui.onlineBusy ? " disabled" : ""}${(c.risks || []).length ? "" : " disabled"}>${icon("search")}<span>Find options online</span></button>
      <p class="hint">Online search: needs internet; results are papers, not recommendations. Nothing is sent unless you press the button. No cost, effect or probability is taken from a paper: read it, then enter your own cost / effect with a Source.</p>
      <div id="online-live">${onlineResults()}</div></div>
  </div></section>`;
}

function onlineLink(url, text) {
  const ok = /^https?:\/\//i.test(url || "");
  return ok ? `<a href="${h(url)}" target="_blank" rel="noopener noreferrer">${h(text)}</a>` : h(text);
}

function onlineResults() {
  const o = S.ui.online;
  if (S.ui.onlineBusy) return alertBox("info", "Searching OpenAlex and Crossref", "Waiting for the literature indexes (up to 10 seconds each).");
  if (S.ui.onlineProblems) return alertBox("warn", "The online search could not run", `<ul>${S.ui.onlineProblems.map((p) => `<li>${h(p)}</li>`).join("")}</ul>`);
  if (!o) return "";
  const offBox = !o.ok ? alertBox("neutral", "Offline: using the data on this computer", `${h(o.message || "The literature indexes could not be reached.")} ${h(o.local_note || "")} Everything else in the tool works without internet.`) : "";
  if (!o.ok && !(o.risks || []).length) return offBox;
  const blocks = (o.risks || []).map((r) => {
    // a literature-supported tag and short blue reading chips (first author, year), like the evidence chips of the risk register
    const refs = (r.sources || []).slice(0, 4).map((x) => {
      const au = (x.authors || [])[0] || "", fam = au.split(" ").slice(-1)[0] || "Source";
      const lab = `${fam}${(x.authors || []).length > 1 ? " et al." : ""}${x.year ? ` ${x.year}` : ""}`;
      const tip = `${x.title || ""}${x.venue ? `. ${x.venue}` : ""}${x.doi ? `. DOI ${x.doi}` : ""}`;
      return /^https?:\/\//i.test(x.url || "") ? `<span class="chip"><a class="chip-open" href="${h(x.url)}" target="_blank" rel="noopener noreferrer" data-tip="${h(tip)}" title="${h(tip)}">${icon("book")}${h(lab)}</a></span>` : `<span class="chip" title="${h(tip)}">${icon("book")}${h(lab)}</span>`;
    }).join("");
    const src = refs ? `<span class="st st-lit">${icon("book")}Literature-supported</span> <span class="chips">${refs}</span>` : "";
    const cat = (r.catalogue_options || []).map((c) => `<li>${h(c.measure)} <span class="muted">(${h(c.catalogue_id)})</span></li>`).join("");
    return `<div class="mb-4"><h3>${h(r.risk_id)} ${h(r.risk_name)}</h3>
      ${cat ? `<div class="muted">Catalogue options for this risk:</div><ul>${cat}</ul>` : ""}
      ${r.from_cache ? `<p class="muted">Saved from an earlier online search${r.cached_utc ? ` (${h(r.cached_utc)})` : ""}.</p>` : ""}
      ${src ? `<div>${src}</div>` : (o.ok ? '<p class="muted">No papers returned for this risk.</p>' : "")}</div>`;
  }).join("");
  return `${offBox}${o.cache_note ? alertBox("neutral", "Offline: saved results", h(o.cache_note)) : ""}${o.partial ? alertBox("warn", "Partial results", h(o.message || "")) : ""}${blocks || '<p class="muted">No risks were searched.</p>'}`;
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

function optionRow(o, sel, cur) {
  return `<tr${o.option_id === sel ? ' class="is-preferred" style="font-weight:600"' : ""}>
      <td>${o.rank ? o.rank : "–"}</td>
      <td>${h(o.label)}${o.option_id === sel ? " (preferred)" : ""}${o.option_id === "ACCEPT" && o.option_id !== sel ? ' <span class="muted">(reference)</span>' : ""}</td><td>${money(o.mitigation_cost)}</td><td>${money(o.residual_expected_cost)}</td>
      <td>${money(o.total_expected_cost)}</td><td>${Number(o.P90).toFixed(1)}</td><td>${o.p_exceed_deadline === null ? "n/a" : pct(o.p_exceed_deadline)}</td>
      <td>${o.admissible ? "yes" : "no: " + h((o.rejected_because || []).join("; "))}</td></tr>`;
}

function optionsTable(r) {
  const cur = r.cost.currency, sel = r.decision.selected_option_id, d = r.decision;
  const all = !!S.ui.showAllOptions;
  const byId = Object.fromEntries(d.options.map((o) => [o.option_id, o]));
  let shown = all ? [...d.options].sort((a, b) => (a.rank ?? 1e9) - (b.rank ?? 1e9)) : (d.top_option_ids || []).map((i) => byId[i]).filter(Boolean);
  if (!all && byId.ACCEPT && !shown.includes(byId.ACCEPT)) shown = [...shown, byId.ACCEPT];
  const hidden = d.options.length - shown.length;
  const rows = shown.map((o) => optionRow(o, sel, cur)).join("");
  const toggle = d.options.length > (d.top_n || 5)
    ? `<button type="button" class="btn btn-sm" data-action="opts-toggle">${all ? `Show top ${d.top_n || 5} only` : `Show all ${d.options.length} options`}</button>` : "";
  return `<section class="card mb-5"><header class="card-h"><h2>Top ${Math.min(d.top_n || 5, (d.top_option_ids || []).length)} options</h2><span class="sub">ranked by the chosen criterion · same random draws for every option</span></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Rank</th><th>Option</th><th>Mitigation cost (${h(cur)})</th><th>Residual expected cost</th><th>Total expected cost</th><th>P90 (d)</th><th>P(T &gt; deadline)</th><th>Admissible</th></tr></thead><tbody>${rows}</tbody></table></div>
    <p class="muted">${hidden > 0 && !all ? `${hidden} further option${hidden === 1 ? "" : "s"} evaluated but not shown (lower ranked or rejected). ` : ""}Rank 1 is the preferred option under the criterion; the Accept row is always shown as the reference. ${toggle}</p></div></section>`;
}

function preferredDetail(r) {
  const d = r.decision, cur = r.cost.currency, sel = d.selected_option_id;
  const o = d.options.find((x) => x.option_id === sel);
  if (!o) return `<section class="card mb-5"><header class="card-h"><h2>Preferred option in detail</h2></header><div class="card-b">${alertBox("warn", "No admissible option", h(r.command.reason || d.statement))}</div></section>`;
  const acc = d.options.find((x) => x.option_id === "ACCEPT");
  const mitDefs = (S.case.mitigations || []).filter((m) => (o.mitigations || []).includes(m.id));
  const f = r.command.figures || {};
  const delta = (a, b, nd = 0, unit = "") => (a === null || a === undefined || b === null || b === undefined) ? "n/a" : `${(b - a) > 0 ? "+" : (b - a) < 0 ? "\u2212" : "\u00b1"}${money(Math.abs(b - a), nd)}${unit}`;
  const measures = [
    ["Mitigation cost", money(acc.mitigation_cost), money(o.mitigation_cost), delta(acc.mitigation_cost, o.mitigation_cost)],
    ["Residual expected cost", money(acc.residual_expected_cost), money(o.residual_expected_cost), delta(acc.residual_expected_cost, o.residual_expected_cost)],
    ["Total expected cost", money(acc.total_expected_cost), money(o.total_expected_cost), delta(acc.total_expected_cost, o.total_expected_cost)],
    ["Expected delay (d)", money(acc.expected_delay, 2), money(o.expected_delay, 2), delta(acc.expected_delay, o.expected_delay, 2, " d")],
    ["P90 duration (d)", money(acc.P90, 2), money(o.P90, 2), delta(acc.P90, o.P90, 2, " d")],
    ["P(T > deadline)", acc.p_exceed_deadline === null ? "n/a" : pct(acc.p_exceed_deadline), o.p_exceed_deadline === null ? "n/a" : pct(o.p_exceed_deadline), "—"],
  ].map(([k, a, b, c]) => `<tr><td>${k}</td><td>${a}</td><td>${b}</td><td>${c}</td></tr>`).join("");
  const parts = mitDefs.length ? `<ul>${mitDefs.map((m) => `<li><strong>${h(m.id)}</strong>: ${h(m.action || "")} <span class="muted">(targets ${h(m.risk_id || "")}; cost ${money(m.cost && m.cost.value !== undefined ? m.cost.value : m.cost)} ${h(cur)}${(m.secondary_risks || []).length ? `; ${(m.secondary_risks || []).length} secondary risk(s) modelled` : ""})</span></li>`).join("")}</ul>`
    : `<p class="muted">${sel === "ACCEPT" ? "No response: the risk is accepted as it stands." : "No response definitions found for this option."}</p>`;
  const st = r.decision_stability;
  const why = `${h(r.command.reason)}${st ? ` The choice is <strong>${st.stable ? "stable" : "not stable"}</strong> across the ${h(st.seeds.length)} seeds checked.` : ""}`;
  return `<section class="card mb-5" style="border:2px solid var(--accent, #1f5fbf)"><header class="card-h"><h2>${icon("star")} Preferred option in detail: ${h(o.label)}</h2><span class="sub">${h(r.command.command)}</span></header><div class="card-b">
    <p><strong>Why it is preferred.</strong> ${why}</p>
    <div class="subhead">What the option consists of</div>${parts}
    <div class="subhead">Before and after (Accept versus this option, ${h(cur)})</div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Measure</th><th>Accept</th><th>This option</th><th>Change</th></tr></thead><tbody>${measures}</tbody></table></div>
    ${f.expected_cost_saving_vs_accept !== undefined && sel !== "ACCEPT" ? `<p>Expected total cost saving against Accept: <strong>${money(f.expected_cost_saving_vs_accept)} ${h(cur)}</strong>; expected delay avoided <strong>${money(f.expected_delay_avoided_days, 2)} d</strong>.</p>` : ""}
    <p class="muted"><em>${h(d.caveat)}</em></p></div></section>`;
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
  if (!a) return alertBox("info", "No analysis yet", "Enter the cost model and responses above (or use Load example in the top bar), then press <strong>Run analysis</strong>.");
  return `${stale() ? alertBox("info", "Inputs changed", "These results are from the previous inputs. Run the analysis again to update them.") : ""}
    <div${stale() ? ' class="is-stale-view"' : ""}>${commandBanner(a)}${chartsSection(a)}${optionsTable(a)}${emvTable(a)}${sensitivity(a)}
    <section class="card mb-5"><header class="card-h"><h2>Full report</h2><span class="sub">analysis.md</span></header><div class="card-b"><article class="md">${renderMarkdown(a.report_markdown || "")}</article></div></section>${preferredDetail(a)}</div>`;
}

export function render() {
  const actions = `<button type="button" class="btn btn-primary" data-action="analysis-run"${S.ui.analysisBusy ? " disabled" : ""}>${icon("sparkle")}<span>Run analysis</span></button>
    <button type="button" class="btn" data-action="analysis-dl"${S.ui.analysis ? "" : " disabled"}>${icon("download")}<span>analysis.md</span></button>
    <button type="button" class="btn" data-action="analysis-charts-dl"${S.ui.analysis ? "" : " disabled"}>${icon("download")}<span>charts (HTML)</span></button>
    <button type="button" class="btn" data-action="analysis-manual-dl"${S.ui.analysis ? "" : " disabled"} title="Excel: hand formulas beside the tool's numbers">${icon("download")}<span>manual check (Excel)</span></button>`;
  return `${screenHead(4, "Cost, options & decision", "Turns the register's delay risks into a simulated schedule and cost, compares candidate responses on the same random draws, and states which option is <strong>preferred under the chosen criterion</strong>. Every cost and effect is your input with a Source; the tool never supplies one. Not a claim of optimality.", actions)}
  ${inputs()}<div id="analysis-live">${results()}</div>`;
}

export function refreshLive(root) {
  const slot = root.querySelector("#analysis-live");
  if (slot) slot.innerHTML = results();
}
