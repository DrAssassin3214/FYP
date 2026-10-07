// Maps the service's validation messages to screens / fields so they can be shown inline.
// The messages themselves are the service's; a plain-language hint is added only for a few
// technical phrasings, and the original text is always kept.
import { h } from "./util.js";
import { S } from "./state.js";
import { alertBox, icon } from "./ui.js";

export function classify(p) {
  let m;
  const s = String(p);
  if ((m = s.match(/^risks\[(\d+)\]/))) return { screen: "risks", key: `risks.${m[1]}` };
  if (/^activity\.planned_duration_days/.test(s)) return { screen: "case", key: "activity.planned_duration_days" };
  if ((m = s.match(/^activity\.(\w+)/))) return { screen: "case", key: `activity.${m[1]}` };
  if (/^impact_bin_edges/.test(s)) return { screen: "matrix", key: "impact_bin_edges_fraction" };
  if (/^rules\[/.test(s)) return { screen: "rules", key: "rules" };
  return { screen: null, key: null };
}

export function friendly(p) {
  const s = String(p);
  let hint = "";
  if (/not 'NoneType'/.test(s)) hint = "A required number is empty: enter min, most likely and max (or the single value for a fixed delay).";
  else if (/unknown source ''/.test(s)) hint = "Source not selected: choose where this number comes from.";
  else if (/value is missing/.test(s)) hint = "Enter a value (and its source).";
  return hint ? `${h(hint)}<span class="raw">${h(s)}</span>` : h(s);
}

/** When the very first check failed (no valid result yet): show the real cause instead of "waiting for the first check". */
export function checkFailure() {
  if (S.result || S.validation.status !== "err") return "";
  const probs = S.validation.problems || [];
  return alertBox("danger", "The case could not be checked", `<ul>${probs.map((p) => `<li>${friendly(p)}</li>`).join("")}</ul>`);
}

export const SCREEN_TITLES = {
  case: "Case & Activity", rules: "Site facts & Rules", risks: "Risk register", matrix: "Risk matrix",
};

export function problemsFor(screen) {
  return (S.validation.problems || []).filter((p) => (classify(p).screen || "case") === screen);
}
export function countByScreen() {
  const out = {};
  for (const p of S.validation.problems || []) {
    const sc = classify(p).screen || "case";
    out[sc] = (out[sc] || 0) + 1;
  }
  return out;
}

/** Screen-level summary of service problems for that screen (all messages verbatim). */
export function screenProblems(screen) {
  const list = problemsFor(screen);
  if (!list.length) return "";
  return alertBox("danger", `${list.length} input problem${list.length > 1 ? "s" : ""} reported by the service`,
    `<ul>${list.map((p) => `<li>${friendly(p)}</li>`).join("")}</ul>`, { attrs: ' data-screen-problems="1"' });
}

/** Fill every [data-err] slot on the page from the current problem list. */
export function applyInline(root = document) {
  const byKey = new Map();
  for (const p of S.validation.problems || []) {
    const { key } = classify(p);
    if (!key) continue;
    if (!byKey.has(key)) byKey.set(key, []);
    byKey.get(key).push(p);
  }
  root.querySelectorAll("[data-err]").forEach((el) => {
    const msgs = byKey.get(el.dataset.err) || [];
    el.classList.toggle("show", msgs.length > 0);
    el.innerHTML = msgs.length ? `${icon("alert")}<span>${msgs.map(friendly).join("<br>")}</span>` : "";
    const card = el.closest(".rcard");
    if (card && el.dataset.err.match(/^risks\.\d+$/)) card.classList.toggle("has-error", msgs.length > 0);
  });
}
