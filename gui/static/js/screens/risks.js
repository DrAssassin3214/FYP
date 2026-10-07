// Screen 4: Risk register (+ curated library and AI suggestions)
import { h, fmtIn, isNum } from "../util.js";
import { S, isStale, riskIds } from "../state.js";
import { field, textInput, textArea, selectInput, paramWidget, distWidget, screenHead, statusBadge, sourceBadge, evChips, icon, alertBox, ul, term, emptyState, tipIcon } from "../ui.js";
import { screenProblems } from "../problems.js";

const isBlank = (v) => v === null || v === undefined || v === "";

function delayText(d) {
  if (!d) return '<span class="tag-req">input required</span>';
  const k = d.kind || "pert";
  if (k === "fixed") return isBlank(d.m) ? '<span class="tag-req">input required</span>' : `<b>${fmtIn(d.m)}</b> d fixed`;
  if (k === "uniform") return isBlank(d.a) || isBlank(d.b) ? '<span class="tag-req">input required</span>' : `<b>${fmtIn(d.a)}–${fmtIn(d.b)}</b> d uniform`;
  if ([d.a, d.m, d.b].some(isBlank)) return '<span class="tag-req">input required</span>';
  return `<b>${fmtIn(d.a)} / ${fmtIn(d.m)} / ${fmtIn(d.b)}</b> d ${k === "pert" ? "PERT" : "triangular"}`;
}

function resultLine(rid) {
  const r = S.result;
  if (!r || !rid) return "";
  const row = (r.risks || []).find((x) => x.id === rid);
  const mx = (r.matrix || []).find((x) => x.risk_id === rid);
  const flag = row?.flag;
  const parts = [];
  if (mx && mx.basis === "literature-seed") parts.push(`<span>matrix <b>${h(mx.level)}</b> (p class ${mx.p_class} × impact ${mx.impact_class}) · <b>literature seed</b>: survey RII importance rank ${row?.seed?.rank} of ${row?.seed?.n_seeded} (a ranking, not a probability or a delay; the same class is used on both axes, an Assumption)${row?.seed?.raised_by_rule ? "; probability class raised by 1 for a rule flag (Assumption, capped at 5)" : ""}. Enter probability and delay to replace it</span>`);
  else if (mx) parts.push(`<span>matrix <b>${h(mx.level)}</b> (p class ${mx.p_class} × impact ${mx.impact_class})</span><span>expected delay if it occurs <b>${fmtIn(mx.expected_delay_if_occurs_days, 2)} d</b></span>`);
  else if (row && !row.complete) parts.push("<span>not on the matrix yet: enter probability and delay with their sources</span>");
  else parts.push("<span>not on the matrix: see the notes on the Risk matrix step</span>");
  if (flag) parts.push(`<span>rule flag <b>${h(flag.level)}</b> (${flag.rules.map(h).join(", ")})</span>`);
  return `<div class="rcard-res${isStale() ? " is-stale-view" : ""}" data-res="${h(rid)}">${parts.join("")}${isStale() ? '<span class="chip-stale badge">last valid state</span>' : ""}</div>`;
}

export function refreshLive(root) {
  root.querySelectorAll(".rcard-res[data-res]").forEach((el) => { el.outerHTML = resultLine(el.dataset.res); });
}

export function riskCard(r, i) {
  const key = `risk:${i}`;
  const open = S.ui.open.has(key);
  const p = r.p || {};
  const pTxt = isBlank(p.value) ? '<span class="tag-req">input required</span>' : `<b>${fmtIn(p.value)}</b>`;
  const statuses = (S.meta?.statuses || []).map((s) => ({ value: s, label: s }));
  const base = `risks.${i}`;
  const body = !open ? "" : `<div class="rcard-b">
    <div class="form-grid">
      ${field({ label: "Risk ID", req: true, control: textInput(`${base}.id`, r.id, { id: `r${i}-id` }), forId: `r${i}-id` })}
      ${field({ label: "Name", control: textInput(`${base}.name`, r.name, { id: `r${i}-name` }), forId: `r${i}-name`, cls: "span-2" })}
      ${field({ label: "Category", control: textInput(`${base}.category`, r.category, { id: `r${i}-cat`, placeholder: "e.g. Material" }), forId: `r${i}-cat` })}
      ${field({ label: "Status", tip: "status", control: selectInput(`${base}.status`, r.status || "expert/user-provided", statuses, { id: `r${i}-st`, rerender: true }), forId: `r${i}-st`,
        hint: r.status === "AI-suggested-unverified" ? "Change only after a person has reviewed it." : "" })}
      ${field({ label: "Description", control: textArea(`${base}.description`, r.description, { id: `r${i}-desc` }), forId: `r${i}-desc`, cls: "wide" })}
    </div>
    <div class="subhead">Occurrence ${tipIcon("bernoulli")}</div>
    <div class="form-grid">
      ${field({ labelHtml: `${term("Probability p", "p")} of occurring during the activity`, req: true, control: paramWidget(`${base}.p`, p, { label: `Probability of ${r.id}`, placeholder: "0 – 1", min: 0, max: 1, step: 0.01, id: `r${i}-p` }), forId: `r${i}-p`, cls: "span-2",
        hint: "Enter from site records or expert judgement. Survey rankings (RII) are not probabilities." })}
      ${field({ label: "Note on p", control: textInput(`${base}.p.note`, p.note, { id: `r${i}-pn`, placeholder: "e.g. elicited from site engineer" }), forId: `r${i}-pn` })}
    </div>
    <div class="subhead">Extra delay if it occurs (working days)</div>
    ${distWidget(`${base}.delay`, r.delay, { label: `Delay of ${r.id}` })}
    <div class="subhead">Evidence ${tipIcon("evidence")}</div>
    ${evChips(r.evidence_ids, `${base}.evidence_ids`)}
  </div>`;
  return `<article class="rcard${open ? " is-open" : ""}" data-card="${key}">
    <div class="rcard-h">
      <span class="rcard-id">${h(r.id || "(no id)")}</span>
      <div class="rcard-main">
        <div class="rcard-title"><span class="name">${h(r.name || "Unnamed risk")}</span>${statusBadge(r.status)}</div>
        <div class="rcard-meta">
          ${r.category ? `<span class="m">${h(r.category)}</span>` : ""}
          <span class="m">p ${pTxt} ${p.source ? sourceBadge(p.source) : ""}</span>
          <span class="m">delay ${delayText(r.delay)} ${r.delay?.source ? sourceBadge(r.delay.source) : ""}</span>
          <span class="m">${evChips(r.evidence_ids)}</span>
        </div>
        ${resultLine(r.id)}
        <div class="field-err" data-err="${base}" role="alert"></div>
      </div>
      <div class="rcard-actions">
        <button type="button" class="btn btn-ghost btn-sm" data-action="card-toggle" data-key="${key}" aria-expanded="${open}" aria-label="${open ? "Collapse" : "Edit"} ${h(r.id)}">${open ? "Done" : "Edit"}${icon("chevDown", "chev ic-sm")}</button>
        <button type="button" class="btn btn-danger-ghost btn-sm btn-icon" data-action="risk-remove" data-i="${i}" aria-label="Remove ${h(r.id)}" title="Remove risk">${icon("trash")}</button>
      </div>
    </div>${body}</article>`;
}

function libItem(L, inReg) {
  const scope = L.scope === "project" ? ' <span class="badge" title="Affects the whole project more than this one activity">project-level</span>' : "";
  return `<div class="lib-item"><div class="t"><span class="mono faint">${h(L.id)}</span> ${h(L.name)}${scope}</div>
    <div class="n">${h(L.description)}<br><span class="faint">${h(L.evidence_note)}</span></div>
    <div class="row">${evChips(L.existence_evidence)}<span class="spacer"></span>${inReg.has(L.id)
      ? `<span class="badge b-ok">${icon("check")}In register</span>`
      : `<button type="button" class="btn btn-sm" data-action="lib-add" data-risk="${h(L.id)}">${icon("plus")}Add</button>`}</div></div>`;
}

/** The whole curated library, grouped by category, filtered by the search box; "Add all" never fills a number. */
export function libraryPanel() {
  const inReg = new Set(riskIds());
  const q = (S.ui.libQuery || "").trim().toLowerCase();
  const list = S.library.filter((L) => !q || `${L.id} ${L.name} ${L.category} ${L.description}`.toLowerCase().includes(q));
  const missing = S.library.filter((L) => !inReg.has(L.id)).length;
  const cats = [...new Set(list.map((L) => L.category))].sort();
  const groups = cats.map((c) => {
    const items = list.filter((L) => L.category === c);
    const todo = items.filter((L) => !inReg.has(L.id)).length;
    return `<details class="lib-group" open><summary><b>${h(c)}</b> <span class="faint">(${items.length})</span>${todo ? `<button type="button" class="btn btn-sm" data-action="lib-add-all" data-cat="${h(c)}">${icon("plus")}Add all ${todo}</button>` : `<span class="badge b-ok">${icon("check")}all in register</span>`}</summary>
      ${items.map((L) => libItem(L, inReg)).join("")}</details>`;
  }).join("");
  return `<div class="row mb-3"><input id="lib-q" class="input" type="search" placeholder="Filter the ${S.library.length} risks (e.g. supervision, price, safety)" value="${h(S.ui.libQuery || "")}" data-action-input="lib-search" autocomplete="off" style="flex:1">
      ${missing ? `<button type="button" class="btn btn-primary" data-action="lib-add-all" data-cat="">${icon("plus")}Add all ${missing}</button>` : ""}</div>
    <div id="lib-list">${groups || '<p class="faint">No library risk matches this filter.</p>'}</div>`;
}

function suggestPanel() {
  const ai = S.health?.ai || { mode: "offline", label: "AI: offline mode (evidence retrieval only)" };
  const s = S.ui.suggest;
  const inReg = new Set(riskIds());
  let res = "";
  if (s?.error) res = alertBox("danger", "Suggestion request failed", ul(s.error.map(h)));
  else if (s && s.mode === "offline-retrieval") {
    res = `${alertBox("neutral", "Offline retrieval mode", h(s.note))}
      <div class="subhead">Curated library matches (${s.library_risks.length}) – retrieval, no AI</div>
      ${s.library_risks.length ? s.library_risks.map((L) => `<div class="lib-item"><div class="t">${h(L.name)}</div><div class="n">${h(L.category)} · ${h(L.description)}</div>
        <div class="row">${evChips(L.existence_evidence)}<span class="spacer"></span>${inReg.has(L.id) ? `<span class="badge b-ok">${icon("check")}In register</span>` : `<button type="button" class="btn btn-sm" data-action="lib-add" data-risk="${h(L.id)}">${icon("plus")}Add</button>`}</div></div>`).join("")
        : '<p class="faint">No library risk matches these words.</p>'}
      <div class="subhead">Related evidence records (${s.evidence.length})</div>
      ${s.evidence.length ? s.evidence.map((e) => `<div class="lib-item"><div class="t">${evChips([e.id])}</div><div class="n">${h(e.citation)}<br><span class="faint">${h(e.context)}</span></div></div>`).join("") : '<p class="faint">No evidence record matches.</p>'}`;
  } else if (s && s.mode === "llm") {
    res = `${alertBox("warn", "Guarded LLM candidates", "Candidates are AI-suggested and unverified. Citations were checked against the evidence store; any numbers the model produced were rejected. Accepting a candidate creates a risk with <strong>empty</strong> probability and delay.")}
      ${(s.candidates || []).map((c, i) => `<div class="lib-item"><div class="t">${h(c.name)} <span class="badge b-ai">${icon("sparkle")}AI-suggested, unverified</span></div>
        <div class="n">${h(c.category)} · ${h(c.mechanism)}</div>
        ${(c.issues || []).length ? `<div class="alert alert-warn" style="margin:6px 0">${icon("alert")}<div class="a-body"><div class="a-title">Guard issues</div>${ul(c.issues.map(h))}</div></div>` : ""}
        ${Object.keys(c.rejected_numeric_fields || {}).length ? `<div class="hint">Rejected numbers (not used): <code>${h(JSON.stringify(c.rejected_numeric_fields))}</code></div>` : ""}
        <div class="row mt-2">${evChips(c.evidence_ids)}<span class="spacer"></span>${c.name === "(unparseable output)" ? "" : `<button type="button" class="btn btn-sm" data-action="ai-accept" data-i="${i}">${icon("plus")}Accept as unverified risk</button>`}</div></div>`).join("") || '<p class="faint">The model proposed no supported candidates.</p>'}
      <details class="tv"><summary>Audit record (prompt, model, retrieved IDs, raw output)</summary><pre class="rule-text" style="max-height:260px;overflow:auto">${h(JSON.stringify(s.audit, null, 2))}</pre></details>`;
  }
  return `<p class="muted" style="font-size:var(--fs-sm)"><span class="ai-badge${ai.mode === "llm" ? " is-llm" : ""}">${icon("sparkle", "ic-sm")}${h(ai.label)}</span></p>
    <form data-form="suggest" class="row" style="flex-wrap:nowrap">
      <label class="sr-only" for="suggest-q">Describe site conditions</label>
      <input id="suggest-q" class="input" type="text" placeholder="e.g. monsoon labour shortage bricks" value="${h(S.ui.suggestQuery)}" autocomplete="off">
      <button class="btn btn-primary${S.ui.suggestBusy ? " is-busy" : ""}" type="submit"${S.ui.suggestBusy ? " disabled" : ""}>${icon("search", "btn-ic")}<span class="spinner" aria-hidden="true"></span>Suggest</button>
    </form>
    <p class="hint mt-2">AI never fills in probabilities, delays or costs. Items it proposes are tagged <em>AI-suggested, unverified</em>.</p>
    <div class="mt-3">${res}</div>`;
}

export function render() {
  const risks = S.case.risks || [];
  const tab = S.ui.riskTab;
  return `${screenHead(3, "Risk register", `Risks that can add delay to this activity. Each needs a ${term("probability", "p")} and a delay range with their sources; a risk is placed on the matrix once both are entered (${term("occurrence model", "bernoulli")}).`,
    `<button type="button" class="btn" data-action="risk-add-custom">${icon("plus")}<span class="lbl">Custom risk</span></button>`)}
  ${screenProblems("risks")}
  <div class="grid-3-1">
    <div>
      ${risks.length ? risks.map(riskCard).join("") : `<div class="card"><div class="card-b">${emptyState({ ic: "shield", title: "No risks in the register", text: "Add risks from the curated library (existence supported by cited records), from the rule flags on step 2, or as custom risks. Probabilities and delays are always entered by you.", actions: `<button type="button" class="btn" data-action="risk-add-custom">${icon("plus")}Add custom risk</button>` })}</div></div>`}
    </div>
    <aside class="card aside-card">
      <div class="tabs" role="tablist">
        <button type="button" role="tab" aria-selected="${tab === "library"}" data-action="risk-tab" data-val="library">${icon("book", "ic-sm")}Library (${S.library.length})</button>
        <button type="button" role="tab" aria-selected="${tab === "ai"}" data-action="risk-tab" data-val="ai">${icon("sparkle", "ic-sm")}AI suggestions</button>
      </div>
      <div class="card-b">${tab === "library" ? `<p class="hint">${S.library.length} risks from the literature (data/risk_library_masonry.json). Evidence supports that a risk <em>exists</em>; it gives no probability. Risks not listed here can be added as custom or AI-suggested risks.</p>${libraryPanel()}` : suggestPanel()}</div>
    </aside>
  </div>`;
}
