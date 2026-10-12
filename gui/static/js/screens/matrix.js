// Screen 4: Risk matrix (ordinal prioritisation only)
import { h, fmt, fmtIn, isNum, valAttr } from "../util.js";
import { S } from "../state.js";
import { screenHead, alertBox, icon, term, staleNote, tipIcon, serviceWarnings, sourceBadge, sourcePicker, textInput } from "../ui.js";
import { screenProblems, checkFailure } from "../problems.js";

const pct = (x) => `${fmtIn(x * 100, 2)}%`;

/** The grid, table and notes: everything that depends on the latest result. */
function liveBlock() {
  const edges = S.case.impact_bin_edges_fraction;
  const e = Array.isArray(edges) ? edges : [null, null, null, null];
  const pe = S.meta?.matrix?.p_edges || [];
  const labels = S.meta?.matrix?.labels || ["1", "2", "3", "4", "5"];
  const levels = S.meta?.matrix?.levels || {};
  const r = S.result;
  const rows = r?.matrix || [];
  const names = new Map((S.case.risks || []).map((x) => [x.id, x.name]));
  const seedOf = (id) => (r?.risks || []).find((x) => x.id === id)?.seed;
  const seedTag = '<span class="tag-seed">literature tier</span>';
  const isSeed = (x) => x.basis === "literature-seed";
  const rowOf = (id) => (r?.risks || []).find((x) => x.id === id);
  const ms = r?.matrix_settings;
  const edgesSrc = ms?.impact_edges_source || "not given";
  const nSeed = r?.summary?.n_seeded || 0;
  const pRange = (k) => k === 1 ? `p < ${pe[0]}` : k === 5 ? `p ≥ ${pe[3]}` : `${pe[k - 2]} – ${pe[k - 1]}`;
  const iRange = (k) => {
    if (!e.every(isNum)) return "";
    return k === 1 ? `< ${pct(e[0])}` : k === 5 ? `≥ ${pct(e[3])}` : `${pct(e[k - 2])} – ${pct(e[k - 1])}`;
  };

  let grid = "";
  for (let pc = 5; pc >= 1; pc--) {
    grid += `<div class="mx-head"><b>${pc} · ${h(labels[pc - 1])}</b>${h(pRange(pc))}</div>`;
    for (let ic = 1; ic <= 5; ic++) {
      const lvl = levels[pc]?.[ic] || "";
      const here = rows.filter((x) => x.p_class === pc && x.impact_class === ic);
      const capped = pc === 1 && (ic === 4 || ic === 5);
      grid += `<div class="mx-cell lvl-${h(lvl)}${capped ? " is-capped" : ""}" role="cell"${capped ? ' data-tip="Review: the level is capped by the scoring rule (probability class 1 is Low whatever the impact)"' : ""} aria-label="p class ${pc}, impact class ${ic}, level ${h(lvl)}${here.length ? `: ${h(here.map((x) => x.risk_id).join(", "))}` : ""}">
        ${here.map((x) => `<span class="mx-risk${isSeed(x) ? " is-seed" : ""}" tabindex="0" data-tip="${h(isSeed(x) ? `${x.risk_id} – ${names.get(x.risk_id) || ""} | literature tier ${x.tier} (Assumption): survey RII rank ${seedOf(x.risk_id)?.rank} of ${seedOf(x.risk_id)?.n_seeded}; a ranking, not a probability or a delay and not an assessed level | score ${x.score}` : `${x.risk_id} – ${names.get(x.risk_id) || ""} | p = ${x.p} | expected delay if it occurs = ${fmt(x.expected_delay_if_occurs_days, 2)} d | score ${x.score} (${x.level})`)}">${h(x.risk_id)}</span>`).join("")}
        <span class="lvl" aria-hidden="true">${h(lvl)}</span></div>`;
    }
  }
  const header = `<div class="mx-head"></div>${[1, 2, 3, 4, 5].map((k) => `<div class="mx-head col"><b>${k}</b>${h(iRange(k))}</div>`).join("")}`;
  const matrix = `<div class="matrix-wrap"><div class="matrix-ylab">Probability class (p)</div>
    <div class="matrix" role="table" aria-label="Risk matrix, probability class by impact class">${grid}${header}</div>
    <div></div><div class="matrix-xlab">Impact class (expected delay if it occurs ÷ planned duration)<span class="sub">Impact edges ${e.every(isNum) ? e.map((x) => pct(x)).join(" / ") : "not entered"} of planned duration · Source: ${h(edgesSrc)}</span></div></div>`;

  const legend = `<div class="legend mt-3">${["Low", "Moderate", "High", "Extreme"].map((l) => `<span class="it"><span class="swatch lvl-${l}" style="border:1px solid var(--border)"></span>${l}</span>`).join("")}
    <span class="it"><span class="swatch is-seed-sw"></span>literature tier (Assumption)</span>
    <span class="it faint">${sourceBadge("Assumption", true)} Level = p class × impact class with thresholds ${(ms?.level_thresholds || [5, 10, 15]).join(" / ")}; probability edges ${(ms?.p_edges || pe).join(" / ")}. A risk in probability class 1 is Low whatever its impact (dark corner on the two cells concerned); risks with impact class 5 are listed below.</span></div>`;

  const pSrc = (x) => (isSeed(x) ? sourceBadge("Assumption", true) : sourceBadge(rowOf(x.risk_id)?.p?.source, true));
  const table = rows.length ? `<div class="tbl-wrap mt-4"><table class="tbl"><thead><tr><th>Risk</th><th class="r">p</th><th>Source</th><th class="r">p class</th><th class="r">Expected delay (d)</th><th class="r">Impact class</th><th class="r">Score</th><th>Level</th></tr></thead><tbody>
    ${rows.slice().sort((a, b) => b.score - a.score).map((x) => `<tr><td><span class="mono">${h(x.risk_id)}</span> <span class="sub">${h(names.get(x.risk_id) || "")}</span></td><td class="r">${isSeed(x) ? seedTag : fmtIn(x.p)}</td><td>${pSrc(x)}</td><td class="r">${x.p_class}${x.raised_by_rule ? ' <span class="sub">+1 rule flag</span>' : ""}</td><td class="r">${isSeed(x) ? seedTag : fmt(x.expected_delay_if_occurs_days, 2)}</td><td class="r">${x.impact_class}</td><td class="r">${x.score}</td><td>${isSeed(x) ? `<span class="tag-seed">literature tier ${x.tier} (Assumption)</span>` : h(x.level)}</td></tr>`).join("")}
    </tbody></table></div>` : "";
  const hc = r?.high_consequence || [];
  const hcBlock = rows.length ? `<div class="subhead mt-4">High-consequence list <span class="sub">impact class 5, entered numbers only; a filter, not a score</span></div>
    ${hc.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Risk</th><th class="r">p</th><th>Source</th><th class="r">p class</th><th>Level</th></tr></thead><tbody>${hc.map((x) => `<tr><td><span class="mono">${h(x.risk_id)}</span> <span class="sub">${h(names.get(x.risk_id) || "")}</span></td><td class="r">${fmtIn(x.p)}</td><td>${sourceBadge(rowOf(x.risk_id)?.p?.source, true)}</td><td class="r">${x.p_class}</td><td>${h(x.level)}</td></tr>`).join("")}</tbody></table></div>` : '<p class="hint">No risk with entered numbers is in impact class 5.</p>'}` : "";

  let content;
  if (!r) content = checkFailure() || alertBox("info", "Waiting for the first check of the inputs", "");
  else if (!rows.length) content = alertBox("warn", "No risks on the matrix yet", "A risk appears here once it has a literature seed (library risks with survey evidence) or its probability and delay range are entered on the Risk register step with the planned duration on step 1 and the four impact edges above.");
  else content = `<section class="card"><header class="card-h"><h2>Probability × impact</h2><span class="badge b-warn">${icon("alert")}ordinal prioritisation only – a label, not a quantity</span></header><div class="card-b">${nSeed ? `<p class="hint mb-3">${nSeed} risk${nSeed > 1 ? "s sit" : " sits"} at a <b>literature tier (Assumption)</b> (grey dashed chips): a relative importance ranking from survey indices (RII), used as a starting place until you enter probability and delay. The cell colour under such a chip is not an assessed level. An importance index is not a probability or a number of days (see the note on ranking basis above).</p>` : ""}${matrix}${legend}${table}${hcBlock}</div></section>`;

  return `${staleNote()}${content}${r ? serviceWarnings(r, "Notes") : ""}`;
}

export function render() {
  const edges = S.case.impact_bin_edges_fraction;
  const e = Array.isArray(edges) ? edges : [null, null, null, null];
  const pe = S.meta?.matrix?.p_edges || [];
  const edgeInputs = [0, 1, 2, 3].map((k) => `<div class="field"><label for="edge-${k}">Edge ${k + 1}</label>
    <div class="input-group"><input id="edge-${k}" class="input" type="number" step="any" min="0" data-action-input="edge" data-k="${k}" value="${valAttr(e[k])}" placeholder="fraction" autocomplete="off"><span class="addon">× planned</span></div></div>`).join("");
  const open = !!S.ui.showEdges || (S.validation?.problems || []).some((x) => /impact_bin_edges/.test(x));   // errors force it open
  const dots = `<button type="button" class="btn btn-ghost btn-icon" data-action="toggle-edges" aria-expanded="${open}" aria-label="Impact class thresholds" title="Impact class thresholds (advanced)">${icon("dots")}</button>`;
  const es = S.case.impact_bin_edges_source || {};
  const edgesCard = `<section class="card"><header class="card-h"><h2>Impact bin edges ${tipIcon("impact")}</h2><span class="sub">USER INPUT: four ascending fractions of the planned duration</span></header><div class="card-b">
    <div class="form-grid" style="grid-template-columns:repeat(4,minmax(0,1fr))">${edgeInputs}</div>
    <div class="row mt-3"><label class="hint" for="edges-src">Source of the four edges</label>${sourcePicker({ attrs: 'id="edges-src" data-bind="impact_bin_edges_source.source" data-t="src"', value: es.source || "", label: "Source of the impact bin edges" })}
      ${textInput("impact_bin_edges_source.note", es.note, { id: "edges-note", placeholder: "note, e.g. ILLUSTRATIVE placeholder or who agreed the edges", aria: "Note on the impact bin edges" })}</div>
    <div class="field-err" data-err="impact_bin_edges_fraction" role="alert"></div>
    <p class="hint mt-2">Only used for risks with their own probability and delay: the expected delay ÷ planned duration is sorted into impact classes 1 to 5 by these edges (a value exactly on an edge goes to the higher class). Example: 0.05 means 5% of the planned duration. No default is supplied. Probability classes use the engine's equal-width edges (${pe.join(" / ")}), an Assumption. Literature-tier risks ignore these edges.</p>
  </div></section>`;

  return `${screenHead(4, "Risk matrix", `A 5×5 grid that orders the register for attention. ${term("Ordinal prioritisation only", "matrix")}: the continuous p and delay range stay in the register; the class is a label.`, dots)}
  ${screenProblems("matrix")}
  ${open ? edgesCard : ""}
  <section class="card"><div class="card-b"><div class="field field-wide"><label for="seed-basis">Literature ranking basis</label>
    <select id="seed-basis" class="select" data-bind="seed_basis" data-t="sel" data-rerender="1">
      <option value="seed"${(S.case.seed_basis || "seed") === "seed" ? " selected" : ""}>Seed studies, direct matches (default)</option>
      <option value="all"${S.case.seed_basis === "all" ? " selected" : ""}>All studies pooled, direct and related matches</option>
    </select>
    <p class="hint mt-2">Both rank risks by survey importance (RII) and use the same per-study averaging and five equal-count bands. The default keeps the held-out surveys out of the ranking so they can be used for a held-out comparison (only held-out surveys with enough overlap with the library can be compared, and their agreement with the seed is weak and not statistically significant). "All" places every library risk, but related matches are weaker, and because the held-out surveys are then used, no held-out comparison applies.</p></div>
    <div class="alert alert-warn seed-explain mt-3" role="note">${icon("alert")}<div class="a-body"><div class="a-title">What the literature seed is, and is not</div>
      <p>The seed is an <strong>importance ranking</strong> from general building-construction surveys (RII scores). It is <strong>not a probability and not a delay</strong>. It only gives a risk a starting place on the matrix (a <em>literature tier</em>, not an assessed level) until you enter its own probability and delay. Two Assumptions turn the ranking into a matrix cell:</p>
      <ul>
        <li>${sourceBadge("Assumption", true)} The same RII class is used for BOTH the probability and impact axes.</li>
        <li>${sourceBadge("Assumption", true)} A rule flag raises the probability class by 1 (capped at 5).</li>
      </ul></div></div></div></section>
  <div id="matrix-live">${liveBlock()}</div>`;
}

export function refreshLive(root) {
  const slot = root.querySelector("#matrix-live");
  if (slot) slot.innerHTML = liveBlock();
}
