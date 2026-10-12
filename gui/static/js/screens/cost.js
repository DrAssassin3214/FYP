// Screen 6: Cost & EMV
import { h, fmt, fmtIn, fmtMoney, fmtPct, isNum } from "../util.js";
import { S, isStale } from "../state.js";
import { field, textInput, paramWidget, screenHead, alertBox, term, staleNote, needRun, sourceBadge, tipIcon } from "../ui.js";
import { screenProblems } from "../problems.js";

export function render() {
  const c = S.case.cost || {};
  const r = S.result;
  let results = "";
  if (!r) results = needRun("the simulated cost and event EMV table");
  else {
    const cs = r.cost, cur = cs.currency;
    const emvRows = r.event_emv || [];
    const sum = emvRows.reduce((a, x) => a + (isNum(x.emv) ? x.emv : 0), 0);
    const names = new Map((S.case.risks || []).map((x) => [x.id, x.name]));
    const latent = (r.sensitivity || []).find((x) => x.risk_id === "LATENT_PRODUCTIVITY");
    results = `<div class="${isStale() ? "is-stale-view" : ""}">
    <div class="tiles">
      <div class="tile hl"><div class="k">Simulated expected cost</div><div class="v">${fmtMoney(cs.expected_cost)}<span class="u">${h(cur)}</span></div><div class="d">std ${fmtMoney(cs.std)}</div></div>
      ${["P50", "P80", "P90", "P95"].map((k) => `<div class="tile"><div class="k">${term(k + " cost", "pct")}</div><div class="v">${fmtMoney(cs[k])}<span class="u">${h(cur)}</span></div></div>`).join("")}
    </div>
    <section class="card"><header class="card-h"><h2>${term("Event EMV", "emv")} by risk</h2><span class="sub">analytic, per risk: p × (E[delay | occurs] × cost per day + direct cost)</span></header><div class="card-b">
      <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Risk</th><th class="r">p</th><th class="r">E[delay | occurs] (d)</th><th class="r">Conditional cost</th><th class="r">Event EMV</th></tr></thead><tbody>
      ${emvRows.map((x) => `<tr><td><span class="mono">${h(x.risk_id)}</span><span class="sub">${h(names.get(x.risk_id) || "")}</span></td><td class="r">${fmtIn(x.p)}</td><td class="r">${fmt(x.expected_delay_if_occurs_days, 2)}</td><td class="r">${fmtMoney(x.conditional_cost)}</td><td class="r"><strong>${fmtMoney(x.emv)}</strong></td></tr>`).join("")}
      </tbody><tfoot><tr><td colspan="4">Sum of event EMV</td><td class="r">${fmtMoney(sum, cur)}</td><td></td></tr>
      <tr><td colspan="4">Simulated expected cost (reference)</td><td class="r">${fmtMoney(cs.expected_cost, cur)}</td><td></td></tr></tfoot></table></div>
      ${alertBox("info", "Why the two totals can differ", `The sum of event EMVs equals the simulated expected cost only for <strong>independent, additive risks with a linear cost model</strong>. The simulated cost is the reference: it also includes ${latent ? `delay from baseline productivity variability (LATENT_PRODUCTIVITY, mean ${fmt(latent.mean_contribution_days, 2)} d), ` : ""}liquidated damages (non-linear) and any correlation you set, none of which have an event EMV.`, { cls: "mt-4" })}
    </div></section></div>`;
  }
  return `${screenHead(6, "Cost & EMV", "Monetary inputs used to convert simulated delay into cost. The cost per delay day is required and has no default.")}
  ${screenProblems("cost")}
  ${staleNote()}
  <section class="card"><header class="card-h"><h2>Cost inputs</h2></header><div class="card-b"><div class="form-grid">
    ${field({ label: "Cost per delay day", req: true, tip: "source", err: "cost.cost_per_delay_day", cls: "span-2", forId: "f-cost-cd",
      control: paramWidget("cost.cost_per_delay_day", c.cost_per_delay_day, { label: "Cost per delay day", min: 0, unit: `${c.currency || ""}/day`, id: "f-cost-cd" }),
      hint: "Overheads, idle labour and equipment per extra working day. Contract- and site-specific." })}
    ${field({ labelHtml: term("Liquidated damages per day after deadline", "ld"), err: "cost.ld_per_day_after_deadline", cls: "span-2", forId: "f-cost-ld",
      control: paramWidget("cost.ld_per_day_after_deadline", c.ld_per_day_after_deadline, { label: "Liquidated damages per day", optional: true, min: 0, unit: `${c.currency || ""}/day`, placeholder: "blank = not modelled", id: "f-cost-ld" }),
      hint: "Needs a deadline (step 1). 0 or blank = not modelled." })}
    ${field({ label: "Currency", forId: "f-cost-cur", control: textInput("cost.currency", c.currency, { id: "f-cost-cur", placeholder: "INR", rerender: false }) })}
  </div></div></section>
  ${results}`;
}
