// Screen 6: Export
import { S, isStale } from "../state.js";
import { screenHead, alertBox, icon, staleNote } from "../ui.js";
import { checkFailure } from "../problems.js";
import { renderMarkdown } from "../markdown.js";

export function render() {
  const actions = `<button type="button" class="btn btn-primary" data-action="dl-html"${S.case ? "" : " disabled"}>${icon("download")}<span>report.html</span></button>
    <button type="button" class="btn" data-action="dl-png">${icon("download")}<span>matrix.png</span></button>
    <button type="button" class="btn" data-action="dl-svg">${icon("download")}<span>matrix.svg</span></button>
    <button type="button" class="btn" data-action="dl-report">${icon("download")}<span>register.md</span></button>
    <button type="button" class="btn" data-action="dl-csv">${icon("download")}<span>register.csv</span></button>
    <button type="button" class="btn" data-action="save">${icon("save")}<span>case JSON</span></button>`;
  return `${screenHead(7, "Export", "Download the colour-coded matrix as an image (PNG or SVG), a printable report with the matrix (HTML: open it and use Print to save as PDF), the register as Markdown or CSV, and the case file. Downloads always use the <strong>current</strong> inputs.", actions)}
  ${staleNote()}
  ${isStale() ? alertBox("info", "Preview vs download", "The preview below is the last valid state; a download is refused until the input problems are resolved.") : ""}
  <div id="report-live">${preview()}</div>`;
}

function preview() {
  const r = S.result;
  if (!r) return checkFailure() || alertBox("info", "Nothing to preview yet", "The preview appears once the inputs have been checked.");
  return `<section class="card"><header class="card-h"><h2>${icon("doc")} Preview</h2><span class="sub">register.md</span></header>
    <div class="card-b">${r.matrix_svg && r.matrix?.length ? `<div class="matrix-graphic${isStale() ? " is-stale-view" : ""}">${r.matrix_svg}</div>` : ""}<article class="md${isStale() ? " is-stale-view" : ""}">${renderMarkdown(r.report_markdown || "")}</article></div></section>`;
}

export function refreshLive(root) {
  const slot = root.querySelector("#report-live");
  if (slot) slot.innerHTML = preview();
}
