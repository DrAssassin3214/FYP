// Small helpers: escaping, formatting (display only), object paths, downloads.
// Formatting never changes a value; it only renders numbers returned by the service.

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export function h(v) {
  if (v === null || v === undefined) return "";
  return String(v).replace(/[&<>"']/g, (c) => ESC[c]);
}

export const isNum = (x) => typeof x === "number" && Number.isFinite(x);

const nfCache = new Map();
function nf(min, max) {
  const k = `${min}:${max}`;
  if (!nfCache.has(k)) nfCache.set(k, new Intl.NumberFormat("en-US", { minimumFractionDigits: min, maximumFractionDigits: max }));
  return nfCache.get(k);
}
/** Fixed decimals (matches the service's own f-string formatting). */
export function fmt(x, nd = 1) { return isNum(x) ? nf(nd, nd).format(x) : "—"; }
/** Up to nd decimals, no trailing zeros (for echoing inputs). */
export function fmtIn(x, nd = 4) { return isNum(x) ? nf(0, nd).format(x) : "—"; }
export function fmtMoney(x, cur = "") { return isNum(x) ? `${nf(0, 0).format(x)}${cur ? " " + cur : ""}` : "—"; }
export function fmtPct(p, nd = 1) { return isNum(p) ? `${nf(nd, nd).format(p * 100)}%` : "—"; }
export function fmtSigned(x, nd = 1) { return isNum(x) ? `${x > 0 ? "+" : x < 0 ? "−" : "±"}${nf(nd, nd).format(Math.abs(x))}` : "—"; }

export function splitPath(path) {
  if (Array.isArray(path)) return path;
  return String(path).split(".").map((p) => (/^\d+$/.test(p) ? Number(p) : p));
}
export function getPath(obj, path) {
  let cur = obj;
  for (const k of splitPath(path)) {
    if (cur === null || cur === undefined) return undefined;
    cur = cur[k];
  }
  return cur;
}
export function setPath(obj, path, value) {
  const parts = splitPath(path);
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const k = parts[i];
    if (cur[k] === null || cur[k] === undefined || typeof cur[k] !== "object") cur[k] = typeof parts[i + 1] === "number" ? [] : {};
    cur = cur[k];
  }
  cur[parts[parts.length - 1]] = value;
}
export function deletePath(obj, path) {
  const parts = splitPath(path);
  const parent = getPath(obj, parts.slice(0, -1));
  if (parent && typeof parent === "object") delete parent[parts[parts.length - 1]];
}

export const clone = (o) => (o === undefined ? undefined : JSON.parse(JSON.stringify(o)));

export function debounce(fn, ms) {
  let t = null;
  const d = (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  d.flush = (...args) => { clearTimeout(t); fn(...args); };
  d.cancel = () => clearTimeout(t);
  return d;
}

export function download(filename, content, mime = "application/octet-stream") {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

export function slug(s, fallback = "case") {
  const x = String(s || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60);
  return x || fallback;
}

export function uniqueId(prefix, existing) {
  const set = new Set(existing);
  let i = 1;
  while (set.has(`${prefix}${i}`)) i++;
  return `${prefix}${i}`;
}

/** Parse a number typed by the user. Returns {ok, value} where value is null for blank. */
export function parseNum(raw, int = false) {
  const s = String(raw ?? "").trim();
  if (s === "") return { ok: true, value: null };
  const v = Number(s);
  if (!Number.isFinite(v)) return { ok: false, value: null };
  if (int && !Number.isInteger(v)) return { ok: false, value: null };
  return { ok: true, value: v };
}

export function valAttr(v) { return v === null || v === undefined ? "" : h(v); }
