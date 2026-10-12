// Screen 10: Explanation (deterministic, plus optional guarded LLM narrative)
import { h } from "../util.js";
import { S, isStale } from "../state.js";
import { screenHead, alertBox, ul, icon, staleNote, needRun } from "../ui.js";

export function resultToken(r) { return r ? `${r.audit?.input_hash_sha256}|${r.audit?.timestamp_utc}` : null; }

export function render() {
  const r = S.result;
  if (!r) return `${screenHead(10, "Explanation", "Plain-language explanation of the result.")}${needRun("the explanation")}`;
  const ex = S.ui.explainFor === resultToken(r) ? S.ui.explain : null;
  const ai = S.health?.ai || { mode: "offline" };
  let body;
  if (S.ui.explainBusy) body = `<div class="card"><div class="card-b"><div class="row"><span class="spinner"></span> Building the explanation…</div></div></div>`;
  else if (!ex) body = `<div class="card"><div class="card-b"><button type="button" class="btn btn-primary" data-action="explain">${icon("message")}Generate explanation</button></div></div>`;
  else if (ex.error) body = alertBox("danger", "Explanation failed", ul(ex.error.map(h)));
  else {
    const llm = ex.llm;
    let llmBlock;
    if (ai.mode !== "llm") {
      llmBlock = alertBox("neutral", "AI: offline mode (retrieval + deterministic explanations)", "No LLM is configured (ANTHROPIC_API_KEY not set), so no narrative is generated. The deterministic explanation above is the primary explanation in every mode.");
    } else if (ex.llm_error) {
      llmBlock = alertBox("danger", "LLM narrative unavailable", h(ex.llm_error));
    } else if (llm) {
      const ok = llm.verified;
      llmBlock = `<section class="card"><header class="card-h"><h2>${icon("sparkle")} Optional LLM narrative</h2>
        ${ok ? `<span class="badge b-ok">${icon("check")}Numbers verified against the engine trace</span>` : `<span class="badge b-danger">${icon("alert")}${llm.unmatched_numbers.length} unmatched number(s)</span>`}</header>
        <div class="card-b"><p class="hint">Model ${h(llm.model_id)} · AI-generated, secondary text. ${h(llm.note)}</p>
        <div class="quote" style="white-space:pre-wrap">${h(llm.text)}</div>
        ${ok ? "" : alertBox("warn", "Numbers not found in the engine trace (do not rely on them)", `<p>${llm.unmatched_numbers.map((x) => `<code>${h(x)}</code>`).join(", ")}</p>`, { cls: "mt-4" })}
        <details class="tv"><summary>Prompt sent to the model</summary><pre class="rule-text" style="max-height:240px;overflow:auto">${h(llm.prompt)}</pre></details></div></section>`;
    } else llmBlock = "";
    body = `<section class="card"><header class="card-h"><h2>Deterministic explanation</h2><span class="badge b-accent">${icon("check")}built from the engine's numbers, no AI</span></header>
      <div class="card-b"><ol class="explain-list">${ex.deterministic.map((x) => `<li>${h(x)}</li>`).join("")}</ol></div></section>${llmBlock}`;
  }
  return `${screenHead(10, "Explanation", "The primary explanation is assembled deterministically from the result (no language model). An optional LLM narrative is shown only when a key is configured, and every number in it is checked against the engine trace.",
    ex && !ex.error ? `<button type="button" class="btn" data-action="explain">${icon("refresh")}<span class="lbl">Regenerate</span></button>` : "")}
  ${staleNote()}<div class="${isStale() ? "is-stale-view" : ""}">${body}</div>`;
}
