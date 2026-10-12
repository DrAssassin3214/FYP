// Plotly wrappers with a theme-aware template. Charts only draw series returned by the service.
import { isNum } from "./util.js";

function T() {
  const cs = getComputedStyle(document.documentElement);
  const g = (n) => cs.getPropertyValue(n).trim();
  return {
    ink: g("--chart-ink"), muted: g("--chart-muted"), grid: g("--chart-grid"), axis: g("--chart-axis"),
    s1: g("--chart-1"), s2: g("--chart-2"), s3: g("--chart-3"), s4: g("--chart-4"), crit: g("--chart-critical"),
    surface: g("--surface"), text: g("--text"), font: g("--font-sans"),
  };
}
export function alpha(hex, a) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || "");
  if (!m) return hex;
  const n = parseInt(m[1], 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
const CONFIG = {
  displaylogo: false, responsive: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d", "toggleSpikelines", "hoverClosestCartesian", "hoverCompareCartesian"],
  toImageButtonOptions: { format: "png", scale: 2 },
};
function axis(t, title, extra = {}) {
  return {
    title: { text: title, font: { size: 12, color: t.ink }, standoff: 8 },
    gridcolor: t.grid, linecolor: t.axis, zeroline: false, showline: true, ticks: "outside", tickcolor: t.axis, ticklen: 4,
    tickfont: { size: 11, color: t.muted }, automargin: true, ...extra,
  };
}
function layout(t, o = {}) {
  return {
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: t.font, size: 12, color: t.ink },
    margin: { l: 58, r: 18, t: o.legend ? 40 : 26, b: 46 },
    hoverlabel: { bgcolor: t.surface, bordercolor: t.axis, font: { color: t.text, family: t.font, size: 12 } },
    showlegend: !!o.legend,
    legend: { orientation: "h", x: 0, y: 1.13, xanchor: "left", font: { size: 12, color: t.ink }, bgcolor: "rgba(0,0,0,0)" },
    bargap: 0.04,
    ...o.extra,
  };
}
function draw(el, traces, lay) {
  if (!el) return;
  if (!window.Plotly) { el.innerHTML = '<p class="faint">Chart library not loaded.</p>'; return; }
  window.Plotly.react(el, traces, lay, CONFIG);
}

/** Vertical reference lines for percentiles and the deadline. */
function refLines(t, pct, deadline) {
  const shapes = [], ann = [];
  const keys = ["P50", "P80", "P90", "P95"].filter((k) => isNum(pct?.[k]));
  keys.forEach((k, i) => {
    const x = pct[k];
    shapes.push({ type: "line", x0: x, x1: x, y0: 0, y1: 1, yref: "paper", line: { color: t.muted, width: 1, dash: "dot" } });
    ann.push({ x, y: i % 2 ? 0.93 : 1.0, yref: "paper", text: k, showarrow: false, xanchor: "left", yanchor: "bottom", xshift: 2, font: { size: 10.5, color: t.muted } });
  });
  if (isNum(deadline)) {
    shapes.push({ type: "line", x0: deadline, x1: deadline, y0: 0, y1: 1, yref: "paper", line: { color: t.crit, width: 2 } });
    ann.push({ x: deadline, y: 0.8, yref: "paper", text: `Deadline ${deadline} d`, showarrow: false, xanchor: "right", yanchor: "bottom", xshift: -3,
      font: { size: 11, color: t.crit }, bgcolor: t.surface, borderpad: 2 });
  }
  return { shapes, annotations: ann };
}

/** Histogram (density) of one series, bars from service bin edges. */
export function histogram(el, hist, pct, deadline) {
  const t = T();
  const e = hist.edges, d = hist.density;
  const x = e.slice(0, -1), w = x.map((v, i) => e[i + 1] - v);
  const cd = x.map((v, i) => [v, e[i + 1]]);
  const tr = [{ type: "bar", x, y: d, width: w, offset: 0, marker: { color: alpha(t.s1, 0.85), line: { color: t.surface, width: 1 } },
    customdata: cd, hovertemplate: "%{customdata[0]:.1f}–%{customdata[1]:.1f} days<br>density %{y:.3f}<extra></extra>", name: "Simulated duration" }];
  const r = refLines(t, pct, deadline);
  draw(el, tr, layout(t, { extra: { xaxis: axis(t, "Activity duration (working days)"), yaxis: axis(t, "Probability density"), ...r } }));
}

/** Step-area overlay of several histogram series: [{name, hist, color}] */
export function histOverlay(el, series, deadline) {
  const t = T();
  const cols = [t.s1, t.s2, t.s3, t.s4];
  const tr = series.map((s, i) => {
    const c = s.color || cols[i % 4];
    const e = s.hist.edges, d = s.hist.density;
    return { type: "scatter", mode: "lines", x: e, y: [...d, d[d.length - 1]], line: { shape: "hv", color: c, width: 2 },
      fill: "tozeroy", fillcolor: alpha(c, 0.14), name: s.name, hovertemplate: `${s.name}<br>from %{x:.1f} d: density %{y:.3f}<extra></extra>` };
  });
  const r = refLines(t, null, deadline);
  draw(el, tr, layout(t, { legend: true, extra: { xaxis: axis(t, "Activity duration (working days)"), yaxis: axis(t, "Probability density", { rangemode: "tozero" }), ...r } }));
}

/** CDF(s): [{name, cdf:{q, days}, color}] with P-guides and deadline. */
export function cdf(el, series, deadline) {
  const t = T();
  const cols = [t.s1, t.s2, t.s3, t.s4];
  const tr = series.map((s, i) => ({ type: "scatter", mode: "lines", x: s.cdf.days, y: s.cdf.q, name: s.name,
    line: { color: s.color || cols[i % 4], width: 2 }, hovertemplate: `${s.name}<br>%{y:.0%} of runs ≤ %{x:.1f} d<extra></extra>` }));
  const shapes = [], ann = [];
  [0.5, 0.8, 0.9, 0.95].forEach((q) => {
    shapes.push({ type: "line", xref: "paper", x0: 0, x1: 1, y0: q, y1: q, line: { color: t.grid, width: 1 } });
    ann.push({ xref: "paper", x: 1, y: q, text: `P${Math.round(q * 100)}`, showarrow: false, xanchor: "right", yanchor: q === 0.9 ? "top" : "bottom", font: { size: 10.5, color: t.muted } });
  });
  if (isNum(deadline)) {
    shapes.push({ type: "line", x0: deadline, x1: deadline, y0: 0, y1: 1, yref: "paper", line: { color: t.crit, width: 2 } });
    ann.push({ x: deadline, y: 0.05, yref: "paper", text: `Deadline ${deadline} d`, showarrow: false, xanchor: "left", xshift: 3, font: { size: 11, color: t.crit }, bgcolor: t.surface, borderpad: 2 });
  }
  draw(el, tr, layout(t, { legend: series.length > 1, extra: { xaxis: axis(t, "Activity duration (working days)"),
    yaxis: axis(t, "Cumulative share of runs", { range: [0, 1.02], tickformat: ".0%" }), shapes, annotations: ann } }));
}

/** Convergence: running mean / percentiles vs n. */
export function convergence(el, rows) {
  const t = T();
  const keys = [["mean", "Mean", t.s1], ["P50", "P50", t.s2], ["P80", "P80", t.s3], ["P90", "P90", t.s4]];
  const n = rows.map((r) => r.n);
  const tr = keys.filter(([k]) => rows.every((r) => isNum(r[k]))).map(([k, name, c]) => ({
    type: "scatter", mode: "lines+markers", x: n, y: rows.map((r) => r[k]), name, line: { color: c, width: 2 }, marker: { size: 6, color: c },
    hovertemplate: `${name} after %{x:,} runs: %{y:.2f} d<extra></extra>` }));
  draw(el, tr, layout(t, { legend: true, extra: { xaxis: axis(t, "Iterations included", { tickformat: "," }), yaxis: axis(t, "Duration (working days)") } }));
}

/** Horizontal bar chart (one series). items: [{label, value, text}] */
export function barH(el, items, o = {}) {
  const t = T();
  const tr = [{ type: "bar", orientation: "h", y: items.map((x) => x.label), x: items.map((x) => x.value),
    marker: { color: o.color || t.s1 }, text: items.map((x) => x.text), textposition: "outside", cliponaxis: false,
    textfont: { size: 11, color: t.ink }, hovertemplate: `%{y}: %{text}<extra></extra>` }];
  const xa = axis(t, o.xTitle || "", { range: o.range, tickformat: o.tickformat, zeroline: true, zerolinecolor: t.axis });
  draw(el, tr, layout(t, { extra: { xaxis: xa, yaxis: axis(t, "", { autorange: "reversed", ticks: "", showline: false }), margin: { l: 110, r: 50, t: 16, b: 42 }, bargap: 0.35 } }));
}

export function purge(root) {
  if (!window.Plotly) return;
  root.querySelectorAll(".js-plotly-plot").forEach((el) => { try { window.Plotly.purge(el); } catch (e) { /* ignore */ } });
}
