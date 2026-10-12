// Screen 3: Site facts & Rules
import { h, isNum, fmtIn } from "../util.js";
import { S, isStale, riskIds } from "../state.js";
import { field, numInput, screenHead, alertBox, ul, evChips, icon, staleNote, sourceBadge } from "../ui.js";
import { screenProblems } from "../problems.js";

export const FACT_INFO = {
  required_workers: { label: "Workers required", unit: "workers", group: "Labour" },
  available_workers: { label: "Workers available (average daily attendance last week, or confirmed by the labour contractor)", unit: "workers", group: "Labour" },
  skilled_masons_short: { label: "Skilled masons fewer than needed", group: "Labour" },
  gang_payment_overdue: { label: "Gang's weekly payment or labour contractor's bill is overdue", group: "Labour" },
  gang_mostly_migrant: { label: "Gang is mostly migrant (home state far from site)", group: "Labour" },
  festival_or_harvest_in_window: { label: "A major festival, harvest or election falls inside the activity window", group: "Labour" },
  material_lead_time_days: { label: "Supplier lead time (material with the longest lead time)", unit: "days", group: "Material & equipment" },
  material_stock_days: { label: "Stock on site covers (same material)", unit: "days", group: "Material & equipment" },
  sand_cement_stock_days: { label: "Sand / cement stock on site covers", unit: "days", group: "Material & equipment" },
  sand_cement_lead_time_days: { label: "Sand / cement delivery lead time", unit: "days", group: "Material & equipment" },
  tools_shortage: { label: "Mixer, cutter, pump or hand tools short or broken", group: "Material & equipment" },
  scaffolding_ready: { label: "Scaffolding is erected and passed safe", group: "Material & equipment" },
  hoist_available: { label: "Hoist or material lift is available and working", group: "Material & equipment" },
  masonry_floor_level: { label: "Floor where masonry is done (0 = ground floor)", unit: "floor", group: "Site & schedule" },
  work_front_ready: { label: "Floors and walls planned for the next 7 days are de-propped, cleared and handed over", group: "Site & schedule" },
  frames_on_site: { label: "Door and window frames are on site", group: "Site & schedule" },
  mep_sleeve_layout_marked: { label: "Electrical and plumbing sleeve / conduit positions are marked", group: "Site & schedule" },
  lintel_level_plan_issued: { label: "Lintel and sill-band level plan is issued", group: "Site & schedule" },
  monsoon_overlap: { label: "Activity overlaps monsoon / rainy season", group: "Site & schedule" },
  external_walls_in_scope: { label: "External walls are part of this activity", group: "Site & schedule" },
  summer_overlap: { label: "Activity overlaps peak summer", group: "Site & schedule" },
  work_at_height: { label: "Masonry is done at height", group: "Site & schedule" },
  schedule_compressed: { label: "Programme judged faster than the gang can achieve", group: "Site & schedule" },
  planned_daily_output: { label: "Planned daily output (use one unit for both outputs)", unit: "units/day", group: "Site & schedule" },
  achieved_daily_output_last_week: { label: "Achieved daily output last week (same unit)", unit: "units/day", group: "Site & schedule" },
  design_incomplete: { label: "Good-for-construction drawings for wall layout, openings and lintel levels not issued", group: "Site & schedule" },
  payment_delay_expected: { label: "Client payment delays occurred or expected", group: "Site & schedule" },
  prior_rework_history: { label: "Any wall dismantled or redone on this site / gang in the last month", group: "Site & schedule" },
};
const OPS = { gt: ">", lt: "<", ge: "≥", le: "≤", eq: "=", ne: "≠", in: "in" };

function condText(c) {
  const rhs = c.other_fact ? `<code>${h(c.other_fact)}</code>` : `<code>${h(JSON.stringify(c.value))}</code>`;
  return `<code>${h(c.fact)}</code> ${OPS[c.op] || h(c.op)} ${rhs}`;
}
export function ruleCondition(r) {
  const all = (r.all_of || []).map(condText).join(" AND ");
  const any = (r.any_of || []).map(condText).join(" OR ");
  return [all, any ? `(${any})` : ""].filter(Boolean).join(" AND ");
}

function factControl(f) {
  const info = FACT_INFO[f.name] || { label: f.name };
  const facts = S.case.facts || {};
  const v = facts[f.name];
  const has = Object.prototype.hasOwnProperty.call(facts, f.name) && v !== null;
  const rulesTxt = `used by ${f.rules.map(h).join(", ")}`;
  if (f.type === "boolean") {
    const cur = !has ? "unknown" : v === true ? "true" : v === false ? "false" : "other";
    const seg = `<div class="seg sm tri" role="group" aria-label="${h(info.label)}">${[["unknown", "Unknown"], ["true", "Yes"], ["false", "No"]].map(([val, lab]) =>
      `<button type="button" data-action="fact-bool" data-fact="${h(f.name)}" data-val="${val}" aria-pressed="${cur === val}">${lab}</button>`).join("")}</div>`;
    return field({ labelHtml: `${h(info.label)}`, control: seg, hint: `<code>${h(f.name)}</code> · ${rulesTxt}${cur === "other" ? ` · current value ${h(JSON.stringify(v))}` : ""}` });
  }
  return field({ label: info.label, forId: `fact-${f.name}`, control: numInput(`facts.${f.name}`, has ? v : null, { min: 0, unit: info.unit, nullMode: "delete", id: `fact-${f.name}`, placeholder: "unknown" }),
    hint: `<code>${h(f.name)}</code> · ${rulesTxt}` });
}

function flaggedMissing() {
  const r = S.result;
  if (!r) return [];
  const inReg = new Set(riskIds());
  return Object.entries(r.rules.flags || {}).filter(([rid, fl]) => fl.level === "elevated" && !inReg.has(rid)).map(([rid, fl]) => ({ rid, fl }));
}

/** The parts that depend on the latest result: flagged-risk panel, consistency issues, rule table. */
function liveBlock() {
  const r = S.result;
  const fired = new Map((r?.rules?.fired || []).map((x) => [x.rule_id, x]));
  const notEval = new Map((r?.rules?.not_evaluable || []).map((x) => [x.rule_id, x]));
  const lib = new Map(S.library.map((x) => [x.id, x]));

  const ruleRows = S.rules.map((rule) => {
    let st = '<span class="faint">evaluating…</span>';
    if (r) {
      if (fired.has(rule.id)) {
        const f = fired.get(rule.id);
        st = f.level === "elevated"
          ? `<span class="badge b-warn">${icon("alert")}Fired: elevated</span>`
          : `<span class="badge b-neutral">${icon("info")}Relevant (normal)</span>`;
        st += `<span class="sub">facts used: ${Object.entries(f.facts_used).map(([k, v]) => `${h(k)} = ${h(JSON.stringify(v))}`).join(", ")}</span>`;
      } else if (notEval.has(rule.id)) {
        st = `<span class="badge b-neutral">${icon("minusCircle")}Not evaluable</span><span class="sub">missing: ${notEval.get(rule.id).missing_facts.map(h).join(", ")}</span>`;
      } else st = `<span class="badge b-ok">${icon("check")}Not fired</span>`;
    }
    const risk = lib.get(rule.risk_id);
    return `<tr><td class="mono">${h(rule.id)}</td><td>${h(rule.description)}<span class="sub">${ruleCondition(rule)}</span></td>
      <td><span class="mono">${h(rule.risk_id)}</span><span class="sub">${h(risk?.name || "")}</span></td>
      <td>${sourceBadge(rule.source, true)}</td><td>${h(rule.confidence)}</td><td>${evChips(rule.evidence_ids)}</td><td>${st}</td></tr>`;
  }).join("");

  const missing = flaggedMissing();
  const flagPanel = !r ? "" : missing.length
    ? `<section class="card" style="border-color:var(--warn-border)"><header class="card-h"><h2>${icon("alert")} Flagged risks not yet in the register (${missing.length})</h2></header><div class="card-b">
      <p class="muted">A rule marks these risks as elevated, but they are not in the register. They are added automatically when you change a site fact (with name, category and evidence filled in); you can also add one here. <strong>Probability and delay stay empty</strong> for you or an expert to enter.</p>
      ${missing.map(({ rid, fl }) => { const L = lib.get(rid); return `<div class="lib-item"><div class="t"><span class="mono">${h(rid)}</span> ${h(L?.name || rid)}</div>
        <div class="n">flagged by ${fl.rules.map(h).join(", ")}${L ? ` · ${h(L.category)} · ${h(L.evidence_note)}` : ""}</div>
        <div class="row">${L ? evChips(L.existence_evidence) : ""}<span class="spacer"></span><button type="button" class="btn btn-sm btn-primary" data-action="add-flagged" data-risk="${h(rid)}">${icon("plus")}Add to register</button></div></div>`; }).join("")}
    </div></section>`
    : alertBox("ok", "Every elevated flag is covered by the risk register", "");

  return `${flagPanel}
  ${r && (r.rule_base_issues || []).length ? alertBox("danger", "Rule-base consistency issues", ul(r.rule_base_issues.map(h))) : ""}
  <section class="card"><header class="card-h"><h2>Rule base</h2><span class="sub">data/rules_masonry.json · ${S.rules.length} rules${r ? ` · ${fired.size} fired, ${notEval.size} not evaluable` : ""}</span></header><div class="card-b">
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Rule</th><th>Condition</th><th>Flags risk</th><th>Source</th><th>Confidence</th><th>Evidence</th><th>Result</th></tr></thead><tbody>${ruleRows}</tbody></table></div>
    <p class="card-note">${h(r?.rules?.note || "Flags identify relevant/elevated risks; probabilities are entered separately with a Source.")}</p>
  </div></section>`;
}

export function render() {
  const facts = S.meta?.facts || [];
  const groups = {};
  for (const f of facts) {
    const g = (FACT_INFO[f.name] || {}).group || "Other";
    (groups[g] = groups[g] || []).push(f);
  }
  const known = new Set(facts.map((f) => f.name));
  const extra = Object.keys(S.case.facts || {}).filter((k) => !known.has(k));
  const pd = S.case.activity?.planned_duration_days?.value;
  return `${screenHead(2, "Site facts & Rules", "Declare the site conditions the rule engine checks. Rules only <strong>flag</strong> risks as relevant or elevated; they never produce probabilities. A blank fact is <em>unknown</em>: rules that need it are reported as not evaluable instead of guessed.")}
  ${screenProblems("rules")}
  <div class="grid-2 mb-5">
    ${Object.entries(groups).map(([g, list]) => `<section class="card"><header class="card-h"><h2>${h(g)}</h2><span class="sub">site facts (User Input)</span></header><div class="card-b"><div class="form-grid">${list.map(factControl).join("")}</div></div></section>`).join("")}
    <section class="card"><header class="card-h"><h2>Automatic fact</h2></header><div class="card-b">
      <p class="muted"><code>planned_duration_days</code> is taken from the planned duration on step 1 (${isNum(pd) ? `${fmtIn(pd, 2)} days` : "not entered yet"}) and is used by rule RL-MAT2 (relevant only, not elevated).</p>
      ${extra.length ? `<div class="subhead">Other facts in this case file</div><ul>${extra.map((k) => `<li><code>${h(k)}</code> = ${h(JSON.stringify(S.case.facts[k]))} <button type="button" class="btn btn-sm btn-danger-ghost" data-action="fact-remove" data-fact="${h(k)}">${icon("trash")}Remove</button></li>`).join("")}</ul>` : ""}
    </div></section>
  </div>
  <div id="rules-live">${staleNote()}${liveBlock()}</div>`;
}

export function refreshLive(root) {
  const slot = root.querySelector("#rules-live");
  if (slot) slot.innerHTML = staleNote() + liveBlock();
}
