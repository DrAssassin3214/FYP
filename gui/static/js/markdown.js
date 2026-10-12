// Minimal, safe Markdown renderer for the service's report (headings, lists, tables, bold, italic, code).
import { h } from "./util.js";

function inline(s) {
  let x = h(s);
  x = x.replace(/!\[([^\]]*)\]\(([^)]*)\)/g, '<span class="md-img">[figure: $1]</span>');
  x = x.replace(/`([^`]+)`/g, "<code>$1</code>");
  x = x.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  x = x.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?![*\w])/g, "$1<em>$2</em>");
  return x;
}
const cells = (r) => r.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());

export function renderMarkdown(md) {
  const lines = String(md || "").replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const L = lines[i];
    if (/^\s*$/.test(L)) { i++; continue; }
    let m;
    if ((m = L.match(/^(#{1,6})\s+(.*)$/))) { const n = Math.min(m[1].length + 1, 6); out.push(`<h${n}>${inline(m[2])}</h${n}>`); i++; continue; }
    if (/^\s*\|/.test(L)) {
      const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(lines[i++]);
      const head = cells(rows[0]);
      let body = rows.slice(1);
      if (body.length && /^\s*\|?\s*:?-{2,}/.test(body[0])) body = body.slice(1);
      const num = (c) => /^[-+]?[\d,]*\.?\d+%?$/.test(c.replace(/\s/g, ""));
      out.push(`<div class="tbl-wrap"><table class="tbl md-tbl"><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${
        body.map((r) => `<tr>${cells(r).map((c) => `<td${num(c) ? ' class="r"' : ""}>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }
    if (/^\s*[-*]\s+/.test(L)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*[-*]\s+/, ""));
      out.push(`<ul>${items.map((x) => `<li>${inline(x)}</li>`).join("")}</ul>`);
      continue;
    }
    const para = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,6}\s|\s*\||\s*[-*]\s)/.test(lines[i])) para.push(lines[i++]);
    out.push(`<p>${inline(para.join(" "))}</p>`);
  }
  return out.join("\n");
}
