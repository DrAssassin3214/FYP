// Screen 5: Evidence
import { h } from "../util.js";
import { S } from "../state.js";
import { screenHead, alertBox, icon } from "../ui.js";

export function citedIds() {
  const ids = new Set();
  const walk = (o) => {
    if (Array.isArray(o)) o.forEach(walk);
    else if (o && typeof o === "object") for (const [k, v] of Object.entries(o)) { if (k === "evidence_ids" && Array.isArray(v)) v.forEach((x) => ids.add(x)); else walk(v); }
  };
  walk(S.case);
  return ids;
}

function hl(text, terms) {
  let x = h(text);
  for (const t of terms) if (t.length > 1) x = x.replace(new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"), "<mark>$1</mark>");
  return x;
}

export function evidenceList() {
  const q = S.ui.evQuery.trim().toLowerCase();
  const terms = q ? q.split(/\s+/) : [];
  const cited = citedIds();
  const searching = q.length > 0;
  const base = searching ? (S.ui.evHits || []) : S.evidenceList;
  const recs = base.filter((r) => !S.ui.evCitedOnly || cited.has(r.id));
  const missing = [...cited].filter((id) => !S.evidence.has(id));
  const scope = searching
    ? (S.ui.evBusy ? "searching the whole corpus…" : `${recs.length} best matches from the whole corpus (${S.health?.evidence_records?.toLocaleString?.() ?? ""} records)`)
    : `${recs.length} curated records shown. Type to search the whole corpus, including the literature harvest.`;
  return `<p class="hint">${h(scope)}${S.ui.evCitedOnly ? " Only IDs cited in this case." : ""}</p>
    ${missing.length && S.ui.evCitedOnly ? alertBox("warn", "Cited IDs not in the evidence corpus", `${missing.map((x) => `<code>${h(x)}</code>`).join(", ")} – check these references; the tool cannot resolve them.`) : ""}
    ${recs.map((r) => `<details class="ev-item"><summary><span class="ev-id">${h(r.id)}</span><span class="ev-cit">${hl(r.citation, terms)}<span class="sub faint" style="display:block">${hl(r.context || "NC", terms)} · depth: ${h(r.evidence_depth)}</span></span>${cited.has(r.id) ? '<span class="badge b-accent">cited</span>' : ""}</summary>
      <div class="ev-body"><dl class="dl"><dt>DOI</dt><dd>${r.doi ? h(r.doi) : '<span class="faint">not recorded</span>'}</dd><dt>Context</dt><dd>${h(r.context || "NC")}</dd><dt>Evidence depth</dt><dd>${h(r.evidence_depth)}</dd><dt>Curated notes / abstract</dt><dd>${hl(r.text || "none", terms)}</dd></dl></div></details>`).join("") || (S.ui.evBusy ? "" : '<p class="faint">No record matches.</p>')}`;
}

export function render() {
  return `${screenHead(5, "Evidence", "The literature records behind the evidence IDs. Curated records are listed; search reaches the full corpus, including the bulk literature harvest.")}
  <section class="card"><header class="card-h"><h2>${icon("book")} Evidence browser</h2><span class="sub">${S.health?.evidence_records?.toLocaleString?.() ?? S.evidenceList.length} records in the corpus</span></header><div class="card-b">
    <div class="row mb-4">
      <label class="sr-only" for="ev-q">Search evidence</label>
      <div class="input-group" style="flex:1;max-width:520px"><input id="ev-q" class="input" type="search" placeholder="Search citation, context or notes (e.g. India labour)" value="${h(S.ui.evQuery)}" data-action-input="ev-search" autocomplete="off"></div>
      <label class="checkline"><input type="checkbox" data-action="ev-cited"${S.ui.evCitedOnly ? " checked" : ""}> Only IDs cited in this case</label>
    </div>
    <div id="ev-list">${evidenceList()}</div>
  </div></section>`;
}
