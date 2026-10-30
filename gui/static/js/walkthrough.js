// Guided walkthrough: a small floating panel that opens each screen in turn. It reads nothing and computes nothing;
// it only navigates (go) and explains. Start it from Settings > Start walkthrough.
import { h } from "./util.js";

const STEPS = [
  { screen: null, title: "Welcome",
    html: `<p>This tool answers one question for a brickwork activity: <strong>is it cheaper to pay for a response now, or to accept the risk of delay?</strong></p>
      <p>It works from the numbers you enter. Every number carries a Source (Assumption, Expert Judgment, Historical Data and so on), and the tool never invents a probability, a delay or a cost.</p>
      <p>This tour takes about two minutes. You can leave at any time with Skip.</p>` },
  { screen: "schedule", title: "Masonry schedule",
    html: `<ul><li>Enter the brick and block tasks with durations, predecessors and the project calendar, or open an MS Project file saved as XML.</li>
      <li>Mark the task you want assessed with the star. Its duration, float, labour, material and site data become the activity and the site facts of the case.</li>
      <li>All durations are in working days.</li></ul>` },
  { screen: "risks", title: "Risk register",
    html: `<ul><li>Add risks from the library, or add your own.</li>
      <li>Each risk needs a probability and a delay range (minimum, most likely, maximum), each with a Source.</li>
      <li>A risk with a number missing stays in the register but is kept off the matrix, with a note saying what is missing.</li>
      <li>AI suggestions, if you switch them on in Settings, are candidates only and are marked unverified.</li></ul>` },
  { screen: "matrix", title: "Risk matrix",
    html: `<ul><li>A 5 by 5 grid that orders the register for attention: probability class against impact class.</li>
      <li>Enter the four impact edges (the share of planned duration at which each impact class starts).</li>
      <li>The level is a label for ranking. It is not a time or a money value, and it does not feed the simulation.</li></ul>` },
  { screen: "analysis", title: "Cost, options and decision",
    html: `<ul><li>Enter the cost per delay day, the deadline and any liquidated damages per day.</li>
      <li>Add responses: each needs a cost and an effect (probability after, delay after), with sources.</li>
      <li>Press <strong>Run analysis</strong>. You get the simulated duration and cost, the chance of missing the deadline, and every option compared on the same random draws.</li>
      <li>The command reads AUTHORIZE MITIGATION or ACCEPT RISK, under the criterion you chose. Check the stability note and the cost-per-day table before relying on it.</li></ul>` },
  { screen: "evidence", title: "Evidence",
    html: `<p>The literature records behind the evidence IDs shown on risks and responses. Search covers the whole corpus. A record shows that a risk or effect is reported in the literature; it does not set your probability.</p>` },
  { screen: "report", title: "Export",
    html: `<ul><li>Download the matrix as PNG or SVG, a printable report (open it and use Print to save as PDF), the register as Markdown or CSV, and the case file.</li>
      <li>Downloads always use the current inputs.</li>
      <li>Save the case (Ctrl+S) to keep your work and to reopen it later.</li></ul>` },
  { screen: null, title: "You are set",
    html: `<ul><li><strong>Load example</strong> in the top bar fills the tool with placeholder numbers so you can see every screen working. Do not use those numbers as results.</li>
      <li><strong>New</strong> starts a blank case. <strong>Open</strong> and <strong>Save</strong> handle case files.</li>
      <li>The problems button appears when an input needs fixing.</li>
      <li>To see this tour again: Settings, then Start walkthrough.</li></ul>` },
];

let panel = null, idx = 0, ctx = null, onKey = null;

function focusRail(id) {
  document.querySelectorAll(".navlink.walk-focus").forEach((n) => n.classList.remove("walk-focus"));
  if (!id) return;
  const run = () => document.querySelector(`#rail a.navlink[href="#/${id}"]`)?.classList.add("walk-focus");
  requestAnimationFrame(() => requestAnimationFrame(run));
}

function render() {
  const s = STEPS[idx];
  const last = idx === STEPS.length - 1;
  if (s.screen) ctx.go(s.screen);
  focusRail(s.screen);
  panel.innerHTML = `<div class="walk-top"><span class="walk-count">${idx + 1} of ${STEPS.length}</span></div>
    <h2 id="walk-title">${h(s.title)}</h2>${s.html}
    <div class="walk-dots" aria-hidden="true">${STEPS.map((_, i) => `<i class="${i === idx ? "on" : ""}"></i>`).join("")}</div>
    <div class="walk-foot"><button type="button" class="btn btn-ghost" data-walk="skip">${last ? "Close" : "Skip"}</button>
      <span class="right">${idx > 0 ? '<button type="button" class="btn" data-walk="back">Back</button>' : ""}${last ? "" : '<button type="button" class="btn btn-primary" data-walk="next">Next</button>'}</span></div>`;
  panel.querySelector(last ? '[data-walk="skip"]' : '[data-walk="next"]')?.focus();
}

export function stopWalkthrough() {
  if (onKey) document.removeEventListener("keydown", onKey, true);
  onKey = null;
  focusRail(null);
  panel?.remove();
  panel = null;
}

export function startWalkthrough(c) {
  stopWalkthrough();
  ctx = c; idx = 0;
  panel = document.createElement("div");
  panel.className = "walk";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-labelledby", "walk-title");
  panel.addEventListener("click", (e) => {
    const b = e.target.closest("[data-walk]");
    if (!b) return;
    const a = b.dataset.walk;
    if (a === "skip") return stopWalkthrough();
    idx = Math.max(0, Math.min(STEPS.length - 1, idx + (a === "next" ? 1 : -1)));
    render();
  });
  onKey = (e) => {
    if (e.key === "Escape") { stopWalkthrough(); }
    else if (e.key === "ArrowRight" && idx < STEPS.length - 1 && !/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) { idx++; render(); }
    else if (e.key === "ArrowLeft" && idx > 0 && !/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) { idx--; render(); }
  };
  document.addEventListener("keydown", onKey, true);
  document.body.appendChild(panel);
  render();
}
