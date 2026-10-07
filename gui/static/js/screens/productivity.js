// Screen 2: Productivity (manual range or published models)
import { h, fmt, fmtIn, isNum } from "../util.js";
import { S, currentBaseline } from "../state.js";
import { field, numInput, sourcePicker, screenHead, segmented, alertBox, ul, term, sourceBadge, emptyState, icon, evChips } from "../ui.js";
import { screenProblems } from "../problems.js";
import { baselineCard } from "./case.js";

function equation(m) {
  const terms = m.terms.map((t) => {
    const sign = t.coef < 0 ? "−" : "+";
    const pw = t.power && t.power !== 1 ? `<sup>${fmtIn(t.power)}</sup>` : "";
    return m.form === "loglog" ? ` ${sign} ${fmtIn(Math.abs(t.coef))}·ln(${h(t.var)})` : ` ${sign} ${fmtIn(Math.abs(t.coef))}·${h(t.var)}${pw}`;
  }).join("");
  return m.form === "loglog" ? `ln(y) = ${fmtIn(m.intercept)}${terms}` : `y = ${fmtIn(m.intercept)}${terms}`;
}
const nr = (x, nd = 2) => (isNum(x) ? fmtIn(x, nd) : '<span class="faint">NR</span>');

function modelCard(m, sel, idx) {
  const inputs = sel ? (S.case.productivity.models[idx].inputs || {}) : {};
  const vars = m.variables.map((v) => {
    const range = isNum(v.min) || isNum(v.max) ? `range in the model's data: ${nr(v.min)} – ${nr(v.max)} ${h(v.unit)}` : '<strong>range not reported in the source</strong>: extrapolation cannot be checked';
    return field({ label: `${v.name} (${v.unit})`, req: true, control: numInput(`productivity.models.${idx}.inputs.${v.name}`, inputs[v.name], { unit: v.unit, id: `mv-${m.model_id}-${v.name}` }),
      hint: `${h(v.description)}<br>${range}`, forId: `mv-${m.model_id}-${v.name}` });
  }).join("");
  return `<article class="opt-card${sel ? " card accent" : ""}" style="margin-bottom:var(--s-3)">
    <div class="row between">
      <label class="checkline"><input type="checkbox" data-action="model-toggle" data-id="${h(m.model_id)}"${sel ? " checked" : ""}> <strong>${h(m.name)}</strong></label>
      <span class="badge b-neutral mono">${h(m.model_id)}</span>
    </div>
    <dl class="dl mt-3">
      <dt>Citation</dt><dd>${h(m.citation)}</dd>
      <dt>DOI</dt><dd>${m.doi ? h(m.doi) : '<span class="faint">not recorded</span>'}</dd>
      <dt>Country / activity</dt><dd>${h(m.country)} · ${h(m.activity)}</dd>
      <dt>Fit</dt><dd class="num">n = ${nr(m.n, 0)} · R² = ${nr(m.r2)} · RMSE ${nr(m.rmse)} · MAPE ${nr(m.mape)}</dd>
      <dt>Equation</dt><dd><span class="formula">${equation(m)}</span> <span class="hint">output ${h(m.output_unit)}, ${h(m.output_basis)}${m.crew_size_in_data ? `, crew of ${m.crew_size_in_data} in the data` : ""}</span></dd>
      <dt>Validity</dt><dd>${h(m.validity_text)}</dd>
      <dt>Limitations</dt><dd>${h(m.limitations)}</dd>
      <dt>Evidence depth</dt><dd>${h(m.evidence_depth)} ${sourceBadge("Literature")}</dd>
    </dl>
    ${sel ? `<div class="subhead mt-4">Model inputs for your site</div><div class="form-grid">${vars}</div>` : ""}
  </article>`;
}

export function render() {
  const pr = S.case.productivity || {};
  const mode = pr.mode || "manual";
  const man = pr.manual || {};
  const selIds = (pr.models || []).map((x) => x.id);
  const b = currentBaseline();
  const warns = b && mode === "model" ? (b.warnings || []) : [];
  let body;
  if (mode === "manual") {
    body = `<section class="card"><header class="card-h"><h2>Manual productivity range</h2><span class="sub">m² of wall per day per crew</span></header><div class="card-b">
      <p class="muted">Enter your own site records or an expert estimate. There are no defaults: no Indian brick-masonry productivity values exist in the evidence base.</p>
      <div class="form-grid">
        ${field({ label: "Minimum", req: true, control: numInput("productivity.manual.min", man.min, { min: 0, unit: "m²/day/crew" }) })}
        ${field({ label: "Most likely", req: true, control: numInput("productivity.manual.most_likely", man.most_likely, { min: 0, unit: "m²/day/crew" }) })}
        ${field({ label: "Maximum", req: true, control: numInput("productivity.manual.max", man.max, { min: 0, unit: "m²/day/crew" }) })}
        ${field({ label: "Source", tip: "source", control: sourcePicker({ attrs: 'data-bind="productivity.manual.source" data-t="src"', value: man.source || "", label: "Source of the productivity range" }) })}
      </div>
      <div class="field-err" data-err="productivity" role="alert"></div>
    </div></section>`;
  } else {
    const n = selIds.length;
    const spread = n === 1 ? `<section class="card"><header class="card-h"><h2>Productivity spread for a single model</h2>${sourceBadge("Assumption")}</header><div class="card-b">
        <div class="form-grid">${field({ label: "± spread around the prediction", control: numInput("productivity.single_model_spread_pct", pr.single_model_spread_pct, { min: 0, max: 100, unit: "%" }),
        hint: "Optional and user-set (the service labels it an Assumption). Blank = deterministic baseline; the service then warns that productivity uncertainty is not represented." })}</div></div></section>`
      : n > 1 ? alertBox("info", `${term("Epistemic range", "epistemic")} from ${n} models`, "The service uses the spread between the selected models' predictions as the baseline range. It reflects model disagreement, not site variability.")
      : "";
    body = `${S.models.length < 2 ? alertBox("neutral", `${S.models.length} published model available`, `Only the model(s) in <code>data/productivity_models.json</code> are offered. An epistemic range needs at least two applicable models; with one model, set an explicit spread below or use a manual range.`) : ""}
      ${S.models.map((m) => modelCard(m, selIds.includes(m.model_id), selIds.indexOf(m.model_id))).join("") || emptyState({ title: "No published models", text: "data/productivity_models.json is empty." })}
      ${n === 0 ? alertBox("warn", "No model selected", "Tick at least one model to use it for the baseline.") : ""}
      <div class="field-err" data-err="productivity" role="alert"></div>
      ${spread}`;
  }
  return `${screenHead(2, "Productivity", "Choose how the baseline productivity is obtained. <strong>How the baseline is derived:</strong> T0 = quantity ÷ (crews × most-likely productivity per crew); the min–max productivity gives the range of the baseline duration used in the simulation.",
    segmented([{ value: "manual", label: "Manual range", icon: "user" }, { value: "model", label: "Published models", icon: "book" }], mode, { action: "prod-mode", aria: "Productivity mode" }))}
  ${screenProblems("productivity")}
  <div id="prod-warn">${warnBox(warns)}</div>
  <div class="grid-3-1"><div>${body}</div><div id="baseline-slot">${baselineCard()}</div></div>`;
}

function warnBox(warns) {
  return warns.length ? alertBox("warn", `Model validity / extrapolation warnings (${warns.length}) – from the service`, ul(warns.map(h)), { cls: "big" }) : "";
}

export function refreshLive(root) {
  const slot = root.querySelector("#baseline-slot");
  if (slot) slot.innerHTML = baselineCard();
  const w = root.querySelector("#prod-warn");
  const b = currentBaseline();
  if (w) w.innerHTML = warnBox(b && (S.case.productivity || {}).mode === "model" ? (b.warnings || []) : []);
}
