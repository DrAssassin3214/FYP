// Charts for the "Cost, options & decision" screen: inline SVG, no library, no network.
// Every function draws ONLY values returned by /api/analyze (histogram, summary, sensitivity, value_at_stake,
// event_emv, decision, decision_sensitivity). Colours come from the --chart-* CSS variables (classes in app.css),
// so light and dark themes need no redraw. Each chart has an aria-label, a caption with its Source / Derived
// Calculation label, the ILLUSTRATIVE badge when the case is illustrative, and a data table as text alternative.
import { h } from "./util.js";
import { isIllustrative } from "./ui.js";

const W = 640;                       // viewBox width; the SVG scales to its container
const PREFERRED = "preferred under the stated criterion";
const MAX_OPTIONS = 10;

const money = (v, nd = 0) => (v === null || v === undefined || Number.isNaN(Number(v)) ? "n/a" : Number(v).toLocaleString("en-IN", { maximumFractionDigits: nd, minimumFractionDigits: nd }));
const fx = (v) => Number(v).toFixed(1);
const clip = (s, n) => (s.length > n ? `${s.slice(0, n - 1)}…` : s);

// ------------------------------------------------------------------------------------------------ helpers
function niceTicks(lo, hi, count = 5) {
  if (!(hi > lo)) return [lo];
  const raw = (hi - lo) / count, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) || 10 * mag;
  const out = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) out.push(Math.round(v / step) * step);
  return out;
}
const tickText = (v) => (Math.abs(v) >= 1000 ? money(v) : String(+v.toPrecision(6)));

function riskNames(r) { return Object.fromEntries((r.value_at_stake || []).map((v) => [v.risk_id, v.name])); }
function riskLabel(id, names) {
  if (id === "LATENT_PRODUCTIVITY") return "Latent productivity factor";
  return names[id] ? `${id} ${names[id]}` : id;
}
export function optionLabel(o) { return (o.mitigations || []).join(" + ") || "Accept (no response)"; }

/** ACCEPT and the preferred option always, then the admissible options with the lowest total expected cost. */
export function optionsShown(r, limit = MAX_OPTIONS) {
  const opts = r.decision?.options || [], sel = r.decision?.selected_option_id;
  const keep = opts.filter((o) => o.option_id === "ACCEPT" || o.option_id === sel);
  const rest = opts.filter((o) => !keep.includes(o) && o.admissible).sort((a, b) => a.total_expected_cost - b.total_expected_cost);
  return keep.concat(rest.slice(0, Math.max(0, limit - keep.length))).sort((a, b) => a.total_expected_cost - b.total_expected_cost);
}

function costSource(r) { return h((r.event_emv && r.event_emv[0] && r.event_emv[0].cost_per_day_source) || "see the assumptions"); }
function captionFor(kind, r) {
  const n = Number(r.n_used).toLocaleString("en-IN"), seed = r.seed, src = costSource(r);
  const t = {
    histogram: `Derived Calculation of the ${n} simulated durations (seed ${seed}); percentiles and deadline from the summary.`,
    tornado_delay: `Derived Calculation: mean delay each risk adds in the simulation (${n} runs, seed ${seed}).`,
    tornado_cost: `Derived Calculation: expected cost that disappears if the risk could not occur (same random draws); cost per day Source: ${src}.`,
    event_emv: `Derived Calculation: event EMV = p &times; (expected delay &times; cost per day + direct cost); cost per day Source: ${src}.`,
    options: `Derived Calculation on the same random draws for every option. The outlined bar is the ${PREFERRED}.`,
    decision_sensitivity: "Derived Calculation: the comparison repeated with the cost per delay day scaled, all else held fixed.",
  }[kind];
  return `${t} Input numbers keep the Source label they were entered with.`;
}

function figure(kind, title, svg, r, tableHtml, note = "") {
  const illus = isIllustrative() ? '<span class="ac-illus">ILLUSTRATIVE: placeholder numbers, not evidence</span>' : "";
  return `<figure class="ac-fig" data-chart="${kind}"><div class="ac-head"><h3>${h(title)}</h3>${illus}</div>${svg}
    <figcaption>${captionFor(kind, r)}${note ? ` ${note}` : ""}</figcaption>
    <details class="tv"><summary>Data table for this chart</summary><div class="tbl-wrap">${tableHtml}</div></details></figure>`;
}
function table(head, rows) {
  return `<table class="tbl"><thead><tr>${head.map((x) => `<th>${h(x)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((c) => `<td>${h(String(c))}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}
function svgOpen(height, label) { return `<svg class="ac-svg" viewBox="0 0 ${W} ${height}" role="img" aria-label="${h(label)}" focusable="false">`; }

// ------------------------------------------------------------------------------------------------ 1. histogram
export function histogramChart(r) {
  const hs = r.histogram;
  if (!hs || !hs.edges || !hs.share) return "";
  const pc = r.summary?.percentiles || {}, dl = r.activity?.deadline_days?.value;
  const L = 52, R = 14, T = 62, B = 40, H = 300, pw = W - L - R, ph = H - T - B;
  const marks = [["P50", pc.P50, "dot"], ["P90", pc.P90, "dash"], ["Deadline", dl, "solid"]].filter(([, v]) => v !== undefined && v !== null);
  const xs = [hs.edges[0], hs.edges[hs.edges.length - 1], ...marks.map((m) => m[1])];
  const lo = Math.min(...xs), hi = Math.max(...xs), pad = (hi - lo) * 0.03 || 1;
  const x0 = lo - pad, x1 = hi + pad;
  const X = (v) => L + ((v - x0) / (x1 - x0)) * pw;
  const ymax = Math.max(...hs.share) * 100 * 1.08 || 1, yt = niceTicks(0, ymax, 4), Y = (v) => T + ph - (v / yt[yt.length - 1]) * ph;
  const bars = hs.share.map((s, i) => {
    const xa = X(hs.edges[i]), xb = X(hs.edges[i + 1]), y = Y(s * 100);
    return `<rect class="ac-c1" x="${xa.toFixed(1)}" y="${y.toFixed(1)}" width="${Math.max(xb - xa - 0.6, 0.5).toFixed(1)}" height="${(T + ph - y).toFixed(1)}"><title>${fx(hs.edges[i])} to ${fx(hs.edges[i + 1])} d: ${(s * 100).toFixed(2)}% of runs</title></rect>`;
  }).join("");
  const grid = yt.map((v) => `<line class="ac-grid" x1="${L}" x2="${W - R}" y1="${Y(v).toFixed(1)}" y2="${Y(v).toFixed(1)}"/><text class="ac-mut" x="${L - 6}" y="${(Y(v) + 4).toFixed(1)}" text-anchor="end">${tickText(v)}</text>`).join("");
  const xt = niceTicks(x0, x1, 7).map((v) => `<line class="ac-axis" x1="${X(v).toFixed(1)}" x2="${X(v).toFixed(1)}" y1="${T + ph}" y2="${T + ph + 4}"/><text class="ac-mut" x="${X(v).toFixed(1)}" y="${T + ph + 17}" text-anchor="middle">${tickText(v)}</text>`).join("");
  const lines = marks.map(([name, v, kind], i) => {
    const x = X(v), row = 14 + i * 15, end = x > W - 120;
    const dash = kind === "dot" ? "2 3" : kind === "dash" ? "7 4" : "";
    const cls = name === "Deadline" ? "ac-crit-l" : "ac-ink-l";
    return `<line class="${cls}" x1="${x.toFixed(1)}" x2="${x.toFixed(1)}" y1="${T - 50 + row}" y2="${T + ph}" stroke-width="${kind === "solid" ? 2.2 : 1.6}"${dash ? ` stroke-dasharray="${dash}"` : ""}/>
      <text class="${name === "Deadline" ? "ac-crit-t" : "ac-ink"}" x="${(x + (end ? -4 : 4)).toFixed(1)}" y="${T - 50 + row - 3}" text-anchor="${end ? "end" : "start"}" font-weight="600">${name} ${fx(v)} d</text>`;
  }).join("");
  const label = `Histogram of the simulated activity duration in working days, ${hs.n} runs.${pc.P50 !== undefined ? ` P50 ${fx(pc.P50)} days.` : ""}${pc.P90 !== undefined ? ` P90 ${fx(pc.P90)} days.` : ""}${dl !== undefined && dl !== null ? ` Deadline ${dl} days; probability of finishing after it ${r.summary?.p_exceed_deadline !== undefined ? (r.summary.p_exceed_deadline * 100).toFixed(1) + "%" : "n/a"}.` : ""}`;
  const svg = `${svgOpen(H, label)}${grid}${bars}<line class="ac-axis" x1="${L}" x2="${W - R}" y1="${T + ph}" y2="${T + ph}"/>${xt}${lines}
    <text class="ac-ink" x="${L + pw / 2}" y="${H - 6}" text-anchor="middle">Activity duration (working days)</text>
    <text class="ac-ink" transform="translate(13 ${T + ph / 2}) rotate(-90)" text-anchor="middle">Share of runs (%)</text></svg>`;
  const rows = [...["P50", "P80", "P90", "P95"].filter((k) => pc[k] !== undefined).map((k) => [k, fx(pc[k])])];
  if (dl !== undefined && dl !== null) { rows.push(["Deadline", String(dl)]); if (r.summary?.p_exceed_deadline !== undefined) rows.push(["P(duration > deadline)", `${(r.summary.p_exceed_deadline * 100).toFixed(1)}%`]); }
  const binRows = hs.share.map((s, i) => [`${fx(hs.edges[i])} to ${fx(hs.edges[i + 1])}`, hs.counts[i], `${(s * 100).toFixed(2)}%`]);
  const tbl = table(["Statistic", "Working days"], rows) + table(["Duration bin (d)", "Runs", "Share"], binRows);
  return figure("histogram", "Simulated schedule duration", svg, r, tbl, "Dotted line P50, dashed line P90, solid red line the deadline.");
}

// ------------------------------------------------------------------------------------------------ horizontal bars
function hbarSvg(items, o) {
  const L = o.labelW || 214, R = 96, rowH = 26, T = 8, B = 40, H = T + items.length * rowH + B, pw = W - L - R;
  const max = Math.max(...items.map((i) => i.value), 0) || 1, xt = niceTicks(0, max, 4), top = xt[xt.length - 1] > max ? xt[xt.length - 1] : max, X = (v) => L + (v / top) * pw;
  const grid = xt.map((v) => `<line class="ac-grid" x1="${X(v).toFixed(1)}" x2="${X(v).toFixed(1)}" y1="${T}" y2="${T + items.length * rowH}"/><text class="ac-mut" x="${X(v).toFixed(1)}" y="${T + items.length * rowH + 15}" text-anchor="middle">${tickText(v)}</text>`).join("");
  const rows = items.map((it, i) => {
    const y = T + i * rowH;
    return `<text class="ac-ink" x="${L - 8}" y="${y + rowH / 2 + 4}" text-anchor="end"><title>${h(it.label)}</title>${h(clip(it.label, 34))}</text>
      <rect class="${o.cls}" x="${L}" y="${y + 4}" width="${Math.max(X(it.value) - L, 1).toFixed(1)}" height="${rowH - 8}"><title>${h(it.label)}: ${h(it.text)}</title></rect>
      <text class="ac-ink" x="${(X(it.value) + 5).toFixed(1)}" y="${y + rowH / 2 + 4}">${h(it.text)}</text>`;
  }).join("");
  const label = `${o.title}. ${items.map((i) => `${i.label}: ${i.text}`).join("; ")}.`;
  return `${svgOpen(H, label)}${grid}<line class="ac-axis" x1="${L}" x2="${L}" y1="${T}" y2="${T + items.length * rowH}"/>${rows}
    <text class="ac-ink" x="${L + pw / 2}" y="${H - 6}" text-anchor="middle">${h(o.axis)}</text></svg>`;
}

/** 2a. Tornado: risks ranked by mean delay they contribute (sensitivity). */
export function tornadoDelayChart(r) {
  const names = riskNames(r), rows = [...(r.sensitivity || [])].filter((x) => x.mean_contribution_days !== undefined).sort((a, b) => b.mean_contribution_days - a.mean_contribution_days);
  if (!rows.length) return "";
  const items = rows.map((x) => ({ label: riskLabel(x.risk_id, names), value: x.mean_contribution_days, text: `${x.mean_contribution_days.toFixed(2)} d (${(x.share_of_expected_delay * 100).toFixed(0)}%)` }));
  const svg = hbarSvg(items, { cls: "ac-c1", axis: "Mean delay contributed (working days)", title: "Contribution to expected delay by risk, largest first" });
  return figure("tornado_delay", "Tornado: contribution to expected delay", svg, r,
    table(["Risk", "Mean delay (d)", "Share of expected delay", "Spearman with total delay"], rows.map((x) => [riskLabel(x.risk_id, names), x.mean_contribution_days.toFixed(2), `${(x.share_of_expected_delay * 100).toFixed(1)}%`, x.spearman_with_total_delay.toFixed(2)])),
    "Rank correlation is descriptive and not evidence of causation.");
}

/** 2b. Tornado: risks ranked by value at stake (cost). */
export function tornadoCostChart(r) {
  const names = riskNames(r), rows = [...(r.value_at_stake || [])].sort((a, b) => b.value_at_stake - a.value_at_stake);
  if (!rows.length) return "";
  const cur = r.cost?.currency || "";
  const items = rows.map((x) => ({ label: riskLabel(x.risk_id, names), value: x.value_at_stake, text: money(x.value_at_stake) }));
  const svg = hbarSvg(items, { cls: "ac-c2", axis: `Value at stake (${cur})`, title: "Value at stake by risk, largest first" });
  return figure("tornado_cost", "Tornado: value at stake (expected cost)", svg, r,
    table(["Risk", `Value at stake (${cur})`, "Share of expected cost"], rows.map((x) => [riskLabel(x.risk_id, names), money(x.value_at_stake), `${(x.share_of_expected_cost * 100).toFixed(1)}%`])),
    "The value at stake is the ceiling on what any response to that risk can save.");
}

/** 3. Event EMV per risk (p x impact as returned). */
export function eventEmvChart(r) {
  const names = riskNames(r), rows = [...(r.event_emv || [])].sort((a, b) => b.emv - a.emv);
  if (!rows.length) return "";
  const cur = r.cost?.currency || "";
  const items = rows.map((x) => ({ label: riskLabel(x.risk_id, names), value: x.emv, text: `${money(x.emv)} (p ${x.p})` }));
  const svg = hbarSvg(items, { cls: "ac-c2", axis: `Event EMV (${cur})`, title: "Event EMV per risk, largest first" });
  return figure("event_emv", "Event EMV per risk", svg, r,
    table(["Risk", "p", "Expected delay if it occurs (d)", `Conditional cost (${cur})`, `Event EMV (${cur})`], rows.map((x) => [riskLabel(x.risk_id, names), x.p, x.expected_delay_if_occurs_days.toFixed(2), money(x.conditional_cost), money(x.emv)])));
}

// ------------------------------------------------------------------------------------------------ 4. options
export function optionsChart(r) {
  const shown = optionsShown(r), all = r.decision?.options || [], sel = r.decision?.selected_option_id;
  if (!shown.length) return "";
  const cur = r.cost?.currency || "";
  const L = 232, R = 100, rowH = 28, T = 8, B = 78, H = T + shown.length * rowH + B, pw = W - L - R;
  const max = Math.max(...shown.map((o) => o.total_expected_cost)) || 1, xt = niceTicks(0, max, 4), top = Math.max(xt[xt.length - 1], max), X = (v) => L + (v / top) * pw;
  const grid = xt.map((v) => `<line class="ac-grid" x1="${X(v).toFixed(1)}" x2="${X(v).toFixed(1)}" y1="${T}" y2="${T + shown.length * rowH}"/><text class="ac-mut" x="${X(v).toFixed(1)}" y="${T + shown.length * rowH + 15}" text-anchor="middle">${tickText(v)}</text>`).join("");
  const rows = shown.map((o, i) => {
    const y = T + i * rowH, isSel = o.option_id === sel && sel !== "ACCEPT", lab = optionLabel(o);
    const xm = X(o.mitigation_cost), xt_ = X(o.total_expected_cost);
    return `<text class="ac-ink" x="${L - 8}" y="${y + rowH / 2 + 4}" text-anchor="end"${isSel ? ' font-weight="700"' : ""}><title>${h(lab)}</title>${h(clip(lab, 38))}</text>
      <g${isSel ? ' class="ac-sel"' : ""}><rect class="ac-c2" x="${L}" y="${y + 4}" width="${Math.max(xm - L, 0).toFixed(1)}" height="${rowH - 8}"><title>${h(lab)}: mitigation cost ${money(o.mitigation_cost)} ${h(cur)}</title></rect>
      <rect class="ac-c1" x="${xm.toFixed(1)}" y="${y + 4}" width="${Math.max(xt_ - xm, 0.5).toFixed(1)}" height="${rowH - 8}"><title>${h(lab)}: residual expected cost ${money(o.residual_expected_cost)} ${h(cur)}</title></rect></g>
      <text class="ac-ink" x="${(xt_ + 5).toFixed(1)}" y="${y + rowH / 2 + 4}"${isSel ? ' font-weight="700"' : ""}>${money(o.total_expected_cost)}${isSel ? " ◆" : ""}</text>`;
  }).join("");
  const yk = T + shown.length * rowH + 50;
  const legend = `<rect class="ac-c2" x="${L}" y="${yk - 9}" width="11" height="11"/><text class="ac-ink" x="${L + 16}" y="${yk}">Mitigation cost</text>
    <rect class="ac-c1" x="${L + 120}" y="${yk - 9}" width="11" height="11"/><text class="ac-ink" x="${L + 136}" y="${yk}">Residual expected cost</text>
    <text class="ac-ink" x="${L}" y="${yk + 18}">◆ outlined = ${PREFERRED}</text>`;
  const prefLabel = sel && sel !== "ACCEPT" ? ` The ${PREFERRED} is ${optionLabel(all.find((o) => o.option_id === sel) || {})}.` : ` Accepting the risk is the ${PREFERRED}.`;
  const label = `Expected total cost (mitigation plus residual) for ${shown.length} of ${all.length} evaluated options, lowest first.${prefLabel}`;
  const svg = `${svgOpen(H, label)}${grid}<line class="ac-axis" x1="${L}" x2="${L}" y1="${T}" y2="${T + shown.length * rowH}"/>${rows}
    <text class="ac-ink" x="${L + pw / 2}" y="${T + shown.length * rowH + 33}" text-anchor="middle">Total expected cost (${h(cur)})</text>${legend}</svg>`;
  const tbl = table(["Option", `Mitigation cost (${cur})`, `Residual expected cost (${cur})`, `Total expected cost (${cur})`, ""],
    shown.map((o) => [optionLabel(o), money(o.mitigation_cost), money(o.residual_expected_cost), money(o.total_expected_cost), o.option_id === sel ? PREFERRED : ""]));
  const note = all.length > shown.length ? `Showing ${shown.length} of ${all.length} evaluated options (Accept, the preferred option and the lowest total expected cost); the full list is in the table above.` : "";
  return figure("options", "Option comparison: expected total cost", svg, r, tbl, note);
}

// ------------------------------------------------------------------------------------------------ 5. decision sensitivity
export function decisionSensitivityChart(r) {
  const ds = r.decision_sensitivity;
  if (!ds || !ds.rows || !ds.rows.length) return "";
  const cur = r.cost?.currency || "", rows = ds.rows, opts = Object.fromEntries((r.decision?.options || []).map((o) => [o.option_id, o]));
  const order = [];
  rows.forEach((x) => { if (!order.includes(x.selected_option_id)) order.push(x.selected_option_id); });
  order.sort((a, b) => (opts[a]?.mitigation_cost ?? 0) - (opts[b]?.mitigation_cost ?? 0));
  const labelOf = (id) => (opts[id] ? optionLabel(opts[id]) : id);
  const L = 214, R = 20, rowH = 34, T = 16, B = 62, H = T + order.length * rowH + B, pw = W - L - R;
  const cs = rows.map((x) => x.cost_per_delay_day), lo = Math.min(...cs), hi = Math.max(...cs), pad = (hi - lo) * 0.04 || 1;
  const X = (v) => L + ((v - (lo - pad)) / (hi - lo + 2 * pad)) * pw, Y = (id) => T + order.indexOf(id) * rowH + rowH / 2;
  const grid = order.map((id) => `<line class="ac-grid" x1="${L}" x2="${W - R}" y1="${Y(id)}" y2="${Y(id)}"/><text class="ac-ink" x="${L - 8}" y="${Y(id) + 4}" text-anchor="end"><title>${h(labelOf(id))}</title>${h(clip(labelOf(id), 34))}</text>`).join("");
  const xt = niceTicks(lo - pad, hi + pad, 6).map((v) => `<line class="ac-axis" x1="${X(v).toFixed(1)}" x2="${X(v).toFixed(1)}" y1="${T + order.length * rowH}" y2="${T + order.length * rowH + 4}"/><text class="ac-mut" x="${X(v).toFixed(1)}" y="${T + order.length * rowH + 17}" text-anchor="middle">${tickText(v)}</text>`).join("");
  const path = rows.map((x, i) => `${i ? "L" : "M"}${X(x.cost_per_delay_day).toFixed(1)} ${Y(x.selected_option_id)}`).join(" ");
  const pts = rows.map((x) => `<circle class="${x.selected_option_id === "ACCEPT" ? "ac-pt-open" : "ac-pt"}" cx="${X(x.cost_per_delay_day).toFixed(1)}" cy="${Y(x.selected_option_id)}" r="5.5"><title>${x.multiplier}x (${money(x.cost_per_delay_day)} ${h(cur)} per day): ${h(x.command)}, ${h(labelOf(x.selected_option_id))}</title></circle>`).join("");
  const entered = rows.find((x) => x.multiplier === 1);
  const mark = entered ? `<line class="ac-ink-l" stroke-dasharray="3 3" x1="${X(entered.cost_per_delay_day).toFixed(1)}" x2="${X(entered.cost_per_delay_day).toFixed(1)}" y1="${T}" y2="${T + order.length * rowH}"/><text class="ac-ink" x="${(X(entered.cost_per_delay_day) + 4).toFixed(1)}" y="${T + 11}" font-weight="600">entered value</text>` : "";
  const yk = T + order.length * rowH + 54;
  const flips = (ds.flip_between_multipliers || []).length;
  const label = `Line chart of the ${PREFERRED} against cost per delay day, ${rows.length} values from ${money(lo)} to ${money(hi)} ${cur}. ${rows.map((x) => `${x.multiplier} times: ${labelOf(x.selected_option_id)}`).join("; ")}. ${flips ? `The preferred option changes ${flips} time${flips > 1 ? "s" : ""}, so it depends on the cost per day entered.` : "The preferred option does not change across these values."}`;
  const svg = `${svgOpen(H, label)}${grid}${mark}<path class="ac-line" d="${path}"/>${pts}<line class="ac-axis" x1="${L}" x2="${W - R}" y1="${T + order.length * rowH}" y2="${T + order.length * rowH}"/>${xt}
    <text class="ac-ink" x="${L + pw / 2}" y="${T + order.length * rowH + 34}" text-anchor="middle">Cost per delay day (${h(cur)})</text>
    <circle class="ac-pt-open" cx="${L + 5}" cy="${yk - 4}" r="5"/><text class="ac-ink" x="${L + 16}" y="${yk}">Accept (no response)</text><circle class="ac-pt" cx="${L + 170}" cy="${yk - 4}" r="5"/><text class="ac-ink" x="${L + 181}" y="${yk}">a response</text></svg>`;
  const tbl = table(["Multiplier", `Cost per delay day (${cur})`, "Command", `Option ${PREFERRED}`], rows.map((x) => [`${x.multiplier}x`, money(x.cost_per_delay_day), x.command, labelOf(x.selected_option_id)]));
  return figure("decision_sensitivity", "Decision sensitivity: preferred option against cost per delay day", svg, r, tbl,
    `${flips ? "The preferred option changes along the line, so the choice depends on the cost per day entered. " : ""}${h(ds.note || "")}`);
}

/** The whole charts block (empty string when there is nothing to draw). */
export function chartsSection(r) {
  const figs = [histogramChart(r), tornadoDelayChart(r), tornadoCostChart(r), eventEmvChart(r), optionsChart(r), decisionSensitivityChart(r)].join("");
  if (!figs) return "";
  const missing = r.decision_sensitivity ? "" : '<p class="muted">No decision-sensitivity chart: only accepting the risk was evaluated, because no response with a modelled effect was entered.</p>';
  return `<section class="card mb-5" id="analysis-charts"><header class="card-h"><h2>Charts</h2><span class="sub">drawn only from the values this analysis returned</span></header>
    <div class="card-b"><div class="ac-grid-wrap">${figs}</div>${missing}</div></section>`;
}
