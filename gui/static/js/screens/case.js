// Screen 1: Case & Activity
import { S } from "../state.js";
import { field, textInput, textArea, paramWidget, screenHead, term, fid } from "../ui.js";
import { screenProblems } from "../problems.js";

export function render() {
  const c = S.case, p = c.project || {}, a = c.activity || {};
  const pd = a.planned_duration_days || {};
  return `${screenHead(1, "Case & Activity", "Name the project and the single brick-masonry activity assessed. All durations are in <strong>working days</strong>. Nothing is pre-filled with invented numbers.")}
  ${screenProblems("case")}
  <div class="grid-2 mb-5">
    <section class="card"><header class="card-h"><h2>Project</h2></header><div class="card-b"><div class="form-grid">
      ${field({ label: "Project name", forId: fid("project.name"), control: textInput("project.name", p.name, { placeholder: "e.g. Block B residential" }), cls: "wide" })}
      ${field({ label: "Location", forId: fid("project.location"), control: textInput("project.location", p.location, { placeholder: "City / site" }) })}
      ${field({ label: "Construction type", forId: fid("project.construction_type"), control: textInput("project.construction_type", p.construction_type, { placeholder: "e.g. Residential building" }) })}
      ${field({ label: "Notes", forId: fid("project.notes"), control: textArea("project.notes", p.notes, { rows: 2 }), cls: "wide" })}
    </div></div></section>
    <section class="card"><header class="card-h"><h2>Activity</h2></header><div class="card-b"><div class="form-grid">
      ${field({ label: "Activity ID", forId: fid("activity.id"), control: textInput("activity.id", a.id) })}
      ${field({ label: "Activity name", forId: fid("activity.name"), control: textInput("activity.name", a.name), cls: "span-2" })}
      ${field({ labelHtml: `${term("Planned duration", "planned")} of the activity`, forId: fid("activity.planned_duration_days"), err: "activity.planned_duration_days", cls: "span-2",
        control: paramWidget("activity.planned_duration_days", pd, { label: "Planned duration (working days)", unit: "working days", min: 0 }),
        hint: "Needed for the risk matrix: each risk's impact is its expected delay as a fraction of this duration. Also used by the material-stock rule." })}
    </div></div></section>
  </div>`;
}
