// Screen 8: Mitigation & options
import { h, fmtIn, fmtMoney, isNum } from "../util.js";
import { S, riskIds, currency } from "../state.js";
import { field, textInput, textArea, numInput, selectInput, paramWidget, distWidget, screenHead, sourceBadge, evChips, icon, alertBox, term, emptyState, tipIcon } from "../ui.js";
import { screenProblems } from "../problems.js";
import { criterionSelect } from "./simulation.js";

const blank = (v) => v === null || v === undefined || v === "";

function effectText(m) {
  const parts = [];
  if (m.p_after && !blank(m.p_after.value)) parts.push(`p → <b>${fmtIn(m.p_after.value)}</b> ${sourceBadge(m.p_after.source)}`);
  if (m.delay_after) {
    const d = m.delay_after;
    parts.push(`delay → <b>${d.kind === "fixed" ? fmtIn(d.m) : d.kind === "uniform" ? `${fmtIn(d.a)}–${fmtIn(d.b)}` : `${fmtIn(d.a)} / ${fmtIn(d.m)} / ${fmtIn(d.b)}`}</b> d ${sourceBadge(d.source)}`);
  }
  return parts.length ? parts.join(" · ") : '<span class="tag-req tag-ej">Expert judgment required</span>';
}

function secondaryEditor(m, i) {
  const list = m.secondary_risks || [];
  return `${list.map((s, j) => {
    const base = `mitigations.${i}.secondary_risks.${j}`;
    return `<div class="opt-card"><div class="row between"><strong>Secondary risk ${j + 1}</strong><button type="button" class="btn btn-danger-ghost btn-sm" data-action="sec-remove" data-i="${i}" data-j="${j}">${icon("trash")}Remove</button></div>
      <div class="form-grid mt-2">
        ${field({ label: "ID", req: true, control: textInput(`${base}.id`, s.id, { id: `m${i}s${j}-id` }), forId: `m${i}s${j}-id` })}
        ${field({ label: "Name", control: textInput(`${base}.name`, s.name, { id: `m${i}s${j}-n` }), forId: `m${i}s${j}-n`, cls: "span-2" })}
        ${field({ labelHtml: term("Probability p", "p"), req: true, control: paramWidget(`${base}.p`, s.p, { label: `Probability of secondary risk ${j + 1}`, min: 0, max: 1, step: 0.01 }), cls: "span-2" })}
      </div>
      <div class="subhead">Delay if it occurs</div>${distWidget(`${base}.delay`, s.delay, { label: `Delay of secondary risk ${j + 1}` })}</div>`;
  }).join("")}
  <button type="button" class="btn btn-sm" data-action="sec-add" data-i="${i}">${icon("plus")}Add secondary risk</button>`;
}

function mitCard(m, i) {
  const key = `mit:${i}`;
  const open = S.ui.open.has(key);
  const base = `mitigations.${i}`;
  const risks = S.case.risks || [];
  const target = risks.find((r) => r.id === m.risk_id);
  const riskOpts = [{ value: "", label: "Select target risk…" }, ...risks.map((r) => ({ value: r.id, label: `${r.id} – ${r.name || ""}` }))];
  if (m.risk_id && !target) riskOpts.push({ value: m.risk_id, label: `${m.risk_id} (not in register)` });
  const strategies = (S.meta?.strategies || ["mitigate"]).map((s) => ({ value: s, label: s }));
  const noEffect = (!m.p_after || blank(m.p_after.value)) && !m.delay_after;
  const body = !open ? "" : `<div class="rcard-b">
    <div class="form-grid">
      ${field({ label: "Mitigation ID", req: true, control: textInput(`${base}.id`, m.id, { id: `m${i}-id` }), forId: `m${i}-id` })}
      ${field({ label: "Target risk", req: true, control: selectInput(`${base}.risk_id`, m.risk_id || "", riskOpts, { id: `m${i}-risk`, rerender: true }), forId: `m${i}-risk` })}
      ${field({ label: "Strategy", control: selectInput(`${base}.strategy`, m.strategy || "mitigate", strategies, { id: `m${i}-str` }), forId: `m${i}-str` })}
      ${field({ label: "Action", control: textInput(`${base}.action`, m.action, { id: `m${i}-act`, placeholder: "What will be done" }), forId: `m${i}-act`, cls: "wide" })}
      ${field({ label: "Mechanism", control: textArea(`${base}.mechanism`, m.mechanism, { id: `m${i}-mech`, placeholder: "How it changes the probability or the delay" }), forId: `m${i}-mech`, cls: "wide" })}
      ${field({ label: `Cost (${currency() || "currency"})`, req: true, control: paramWidget(`${base}.cost`, m.cost, { label: `Cost of ${m.id}`, min: 0, id: `m${i}-cost` }), forId: `m${i}-cost`, cls: "span-2" })}
      ${field({ label: "Time to implement", control: numInput(`${base}.time_to_implement_days`, m.time_to_implement_days, { min: 0, unit: "days", id: `m${i}-tti` }), forId: `m${i}-tti`, hint: "Recorded only; not used by the simulation." })}
    </div>
    <div class="subhead">Effect on ${h(m.risk_id || "the target risk")} ${tipIcon("Effect sizes have no defaults and no literature values exist for them here: enter p after and/or delay after with a source (usually Expert Judgment).")}</div>
    ${noEffect ? alertBox("warn", "EXPERT JUDGMENT REQUIRED", "Enter the probability after mitigation and/or the delay distribution after mitigation. Without either, the service warns that this mitigation has no modelled effect.") : ""}
    <div class="form-grid">
      ${field({ labelHtml: `p after mitigation ${!m.p_after || blank(m.p_after.value) ? '<span class="tag-req tag-ej">Expert judgment required</span>' : ""}`, control: paramWidget(`${base}.p_after`, m.p_after, { label: `p after ${m.id}`, optional: true, min: 0, max: 1, step: 0.01, placeholder: target?.p?.value !== undefined && target?.p?.value !== null ? `now ${target.p.value}` : "0 – 1", id: `m${i}-pa` }), forId: `m${i}-pa`, cls: "span-2", hint: "Blank = probability unchanged." })}
    </div>
    <div class="subhead">Delay after mitigation (optional; blank = unchanged)</div>
    ${distWidget(`${base}.delay_after`, m.delay_after, { optional: true, label: `Delay after ${m.id}` })}
    <div class="subhead">Feasibility</div>
    <div class="row"><label class="checkline"><input type="checkbox" data-bind="${base}.feasible" data-t="bool" data-rerender="1"${m.feasible === false ? "" : " checked"}> Feasible on this site</label></div>
    ${m.feasible === false ? `<div class="form-grid mt-2">${field({ label: "Why infeasible", control: textInput(`${base}.infeasible_reason`, m.infeasible_reason, { id: `m${i}-inf` }), forId: `m${i}-inf`, cls: "wide" })}</div>` : ""}
    <div class="subhead">Secondary risks created by this response (optional)</div>
    ${secondaryEditor(m, i)}
    <div class="subhead">Evidence ${tipIcon("evidence")}</div>
    ${evChips(m.evidence_ids, `${base}.evidence_ids`)}
  </div>`;
  return `<article class="rcard${open ? " is-open" : ""}" data-card="${key}">
    <div class="rcard-h">
      <span class="rcard-id">${h(m.id || "(no id)")}</span>
      <div class="rcard-main">
        <div class="rcard-title"><span class="name">${h(m.action || "Unnamed mitigation")}</span><span class="badge b-neutral">${h(m.strategy || "mitigate")}</span>${m.feasible === false ? `<span class="badge b-danger">${icon("xCircle")}Infeasible</span>` : ""}</div>
        <div class="rcard-meta"><span class="m">targets <b class="mono">${h(m.risk_id || "?")}</b></span>
          <span class="m">cost ${m.cost && isNum(m.cost.value) ? `<b>${fmtMoney(m.cost.value, currency())}</b> ${sourceBadge(m.cost.source)}` : '<span class="tag-req">input required</span>'}</span>
          <span class="m">${effectText(m)}</span>
          ${(m.secondary_risks || []).length ? `<span class="m">${m.secondary_risks.length} secondary risk(s)</span>` : ""}
          <span class="m">${evChips(m.evidence_ids)}</span></div>
        <div class="field-err" data-err="${base}" role="alert"></div>
      </div>
      <div class="rcard-actions">
        <button type="button" class="btn btn-ghost btn-sm" data-action="card-toggle" data-key="${key}" aria-expanded="${open}">${open ? "Done" : "Edit"}${icon("chevDown", "chev ic-sm")}</button>
        <button type="button" class="btn btn-danger-ghost btn-sm btn-icon" data-action="mit-remove" data-i="${i}" aria-label="Remove ${h(m.id)}" title="Remove mitigation">${icon("trash")}</button>
      </div>
    </div>${body}</article>`;
}

function optCard(o, i) {
  const mits = S.case.mitigations || [];
  const chosen = new Set(o.mitigation_ids || []);
  const targetOf = new Map(mits.map((m) => [m.id, m.risk_id]));
  const usedTargets = new Map();
  for (const id of chosen) usedTargets.set(targetOf.get(id), id);
  const boxes = mits.map((m) => {
    const other = usedTargets.get(m.risk_id);
    const disabled = !chosen.has(m.id) && other && other !== m.id;
    return `<label class="checkline${disabled ? " is-disabled" : ""}"><input type="checkbox" data-action="opt-mit" data-o="${i}" data-mid="${h(m.id)}"${chosen.has(m.id) ? " checked" : ""}${disabled ? " disabled" : ""}>
      <span><span class="mono">${h(m.id)}</span> ${h(m.action || "")}<span class="hint" style="display:block">targets ${h(m.risk_id || "?")}${disabled ? ` · ${h(other)} already targets this risk (one mitigation per risk)` : ""}</span></span></label>`;
  }).join("");
  const unknown = [...chosen].filter((id) => !targetOf.has(id));
  return `<div class="opt-card"><div class="row" style="flex-wrap:nowrap">
      <div class="field" style="width:130px"><label for="o${i}-id">Option ID</label>${textInput(`options.${i}.id`, o.id, { id: `o${i}-id`, sm: true })}</div>
      <div class="field" style="flex:1"><label for="o${i}-l">Label</label>${textInput(`options.${i}.label`, o.label, { id: `o${i}-l`, sm: true })}</div>
      <button type="button" class="btn btn-danger-ghost btn-sm btn-icon" style="align-self:flex-end" data-action="opt-remove" data-i="${i}" aria-label="Remove option ${h(o.id)}">${icon("trash")}</button></div>
    <div class="opt-mits">${boxes || '<span class="faint">Define mitigations first.</span>'}</div>
    ${unknown.length ? `<div class="hint mt-2">References unknown mitigation(s): ${unknown.map(h).join(", ")}</div>` : ""}
    <div class="field-err" data-err="option.${h(o.id)}" role="alert"></div></div>`;
}

export function render() {
  const mits = S.case.mitigations || [];
  const opts = S.case.options || [];
  const con = S.case.constraints || {};
  return `${screenHead(8, "Mitigation & options", "Define candidate responses and combine them into options. <strong>Effect sizes have no defaults</strong>: the probability or delay after mitigation must be entered with its source. <em>Accept (no response)</em> is always evaluated as well.")}
  ${screenProblems("mitigation")}
  <div class="grid-3-1">
    <div>
      <section class="card"><header class="card-h"><h2>Mitigations (${mits.length})</h2><button type="button" class="btn btn-sm" data-action="mit-add"${(S.case.risks || []).length ? "" : " disabled"}>${icon("plus")}Add mitigation</button></header><div class="card-b">
        ${mits.length ? mits.map(mitCard).join("") : emptyState({ ic: "sliders", title: "No mitigations yet", text: (S.case.risks || []).length ? "Add a response for a risk in the register. You will need its cost and its effect (p after and/or delay after) with sources." : "Add risks to the register first (step 4)." })}
      </div></section>
      <section class="card"><header class="card-h"><h2>Options (${opts.length} + Accept)</h2><button type="button" class="btn btn-sm" data-action="opt-add"${mits.length ? "" : " disabled"}>${icon("plus")}Add option</button></header><div class="card-b">
        <p class="hint">An option is a set of mitigations applied together; at most one mitigation per risk.</p>
        <div class="field-err" data-err="options" role="alert"></div>
        ${opts.map(optCard).join("") || '<p class="faint">No options: only Accept will be evaluated.</p>'}
      </div></section>
    </div>
    <aside class="card"><header class="card-h"><h2>Decision rule</h2></header><div class="card-b">
      <div class="form-grid" style="grid-template-columns:1fr">
        ${criterionSelect("f-crit-mit")}
        ${field({ labelHtml: `Max ${term("P(T > deadline)", "pexceed")} (constraint)`, forId: "f-con-p", err: "constraints.max_p_exceed_deadline", control: numInput("constraints.max_p_exceed_deadline", con.max_p_exceed_deadline, { min: 0, max: 1, step: 0.01, id: "f-con-p", placeholder: "blank = no limit" }), hint: "Optional, user-set (0–1). Needs a deadline." })}
        ${field({ label: `Max mitigation budget (${currency() || "currency"})`, forId: "f-con-b", control: numInput("constraints.max_mitigation_budget", con.max_mitigation_budget, { min: 0, id: "f-con-b", placeholder: "blank = no limit" }), hint: "Optional, user-set." })}
      </div>
      <p class="card-note">Options that are infeasible or violate a constraint are removed before ranking. The result is described as <em>preferred under the selected criterion among the evaluated options</em>, never as optimal.</p>
    </div></aside>
  </div>`;
}
