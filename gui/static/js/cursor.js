// Custom follow cursor (after thedesignshop.studio). The native arrow is hidden (html.has-cursor); text carets in
// fields are unaffected. Enabled only for a fine pointer and no reduced-motion preference, so touch devices and
// people who ask for less motion keep their normal pointer.
//
// Over header controls and navigation the cursor "snaps": it stops following the mouse, glides to the centre of the
// element and becomes a frame 10px larger than it (the same behaviour as the reference site's header links).
// The logo (.brand) is deliberately left out: it already has its own colour-sweep hover animation, so the cursor's
// own rectangular snap-frame on top of it was a redundant second box.
const SNAP = ".topbar .btn, .topbar .ai-badge, .topbar .problems-btn, .rail .navlink, .screen-head .actions .btn, .tabs button, .modal-h .btn, .modal-f .btn, .chip, .ev-id, .mx-risk, .rcard-actions .btn";
// Deliberately narrow: an ordinary <button> (a Yes/No toggle, an "Add" button, a select) already has its own clear
// hover state from its own CSS and doesn't need the ring too — every round of "remove the ring from X" so far has
// turned out to be an ordinary button or label, not a real navigation target, so those no longer opt in by default.
// Only a genuine link (the DOI reference) and an expandable row still do; everything meant to feel special is
// already named explicitly in SNAP above.
const INTERACTIVE = "a[href], summary";
const TEXT_FIELD = 'input:not([type="checkbox"]):not([type="radio"]):not([type="button"]), textarea';
// An evidence row's whole multi-line <summary> counts as INTERACTIVE (clicking anywhere on it expands the row),
// so its own padding reads, visually, as dead space between rows — that space kept showing the big ring. These
// rows keep the plain dot instead; only their own id chip (already in SNAP, checked first) still reacts.
const PLAIN = ".ev-cit, .ev-item summary, .lib-group > summary";   // library category headers: a whole-row toggle, same dead-space problem
// The logo runs its own hover animation; the cursor itself just gets out of the way over it, rather than showing
// a dot/ring on top of it.
const HIDE_OVER = ".topbar .brand";

export function initCursor() {
  const fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!fine || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const el = document.createElement("div");
  el.className = "cursor is-hidden";
  el.setAttribute("aria-hidden", "true");
  document.body.appendChild(el);
  document.documentElement.classList.add("has-cursor");

  let x = 0, y = 0, cx = 0, cy = 0, sw = 10, sh = 10, seen = false, inViewport = true, overHide = false, dialogOpen = false, snapEl = null, mode = "dot";

  function setSnap(next) {
    snapEl = next;
    el.classList.toggle("is-snap", !!next);
  }
  // Hidden for any of three independent reasons — the pointer left the window, a dialog is open, or it's over
  // something (the logo) that wants the cursor gone entirely — tracked separately so none of them can accidentally
  // un-hide one of the others (classify() runs on every pointermove, including ones while a dialog is open).
  function updateHidden() {
    el.classList.toggle("is-hidden", !inViewport || overHide || dialogOpen);
    // the native arrow comes back only inside dialogs; there are no scrollbars while the custom cursor is active (CSS)
    document.documentElement.classList.toggle("has-cursor", !dialogOpen);
  }
  // Inside a dialog (Settings, confirmations) the real system cursor takes over instead: clicking there has to be
  // dependable above all else, and a custom cursor riding on top of a native <dialog>'s top layer is one more place
  // for a click to go slightly wrong. html.has-cursor is what hides the native arrow, so dropping it here is enough.
  const dialog = document.querySelector("dialog.modal");
  if (dialog) {
    new MutationObserver(() => {
      dialogOpen = dialog.open;
      updateHidden();
    }).observe(dialog, { attributes: true, attributeFilter: ["open"] });
  }
  function classify(t) {
    overHide = !!t?.closest(HIDE_OVER);
    updateHidden();
    if (overHide) return;
    // A snap target (e.g. the id chip nested inside an otherwise-plain evidence row) always wins first, so wrapping
    // that row's padding in PLAIN below can never swallow the one thing inside it that should still react.
    const snap = t?.closest(SNAP) || null;
    if (!snap && t?.closest(PLAIN)) { setSnap(null); mode = "dot"; el.classList.remove("is-link", "is-text"); return; }
    setSnap(snap);
    const isLink = !snapEl && !!t?.closest(INTERACTIVE);
    const isText = !snapEl && !isLink && !!t?.closest(TEXT_FIELD);
    el.classList.toggle("is-link", isLink);
    el.classList.toggle("is-text", isText);
    mode = snapEl ? "snap" : isLink ? "link" : isText ? "text" : "dot";
  }

  window.addEventListener("pointermove", (e) => {
    x = e.clientX; y = e.clientY;
    if (!seen) { cx = x; cy = y; seen = true; inViewport = true; updateHidden(); }
    classify(e.target instanceof Element ? e.target : null);
  }, { passive: true });
  window.addEventListener("scroll", () => { if (seen) classify(document.elementFromPoint(x, y)); }, { passive: true });
  document.documentElement.addEventListener("pointerleave", () => { inViewport = false; updateHidden(); });
  document.documentElement.addEventListener("pointerenter", () => { if (seen) { inViewport = true; updateHidden(); } });

  const SIZE = { dot: 10, link: 46, text: 6 };   // "snap" has no fixed size: it targets the hovered element's own rect

  const tick = () => {
    if (!el.isConnected) document.body.appendChild(el);
    let tx = x, ty = y, tw = SIZE[mode] ?? SIZE.dot, th = tw;
    if (snapEl) {
      if (!snapEl.isConnected) { setSnap(null); mode = "dot"; }
      else {
        const r = snapEl.getBoundingClientRect();
        tw = r.width + 10; th = r.height + 10;
        tx = r.left + r.width / 2; ty = r.top + r.height / 2;
      }
    }
    // Position AND size lerp in this one loop, every frame, so they can never drift apart the way a JS-driven
    // position alongside a separately-timed CSS transition for width/height could (that mismatch, worse under any
    // dropped frame, is what produced a stretched, wrongly-placed ring instead of a clean frame around a target).
    // Snapping onto a header control glides slowly (the nice part); free movement tracks the real pointer almost
    // 1:1, so what you see lines up with where clicks actually land (a slow dot here reads as "broken clicking").
    const ease = snapEl ? 0.22 : 0.65;
    cx += (tx - cx) * ease; cy += (ty - cy) * ease;
    sw += (tw - sw) * 0.35; sh += (th - sh) * 0.35;
    el.style.width = `${sw.toFixed(1)}px`; el.style.height = `${sh.toFixed(1)}px`;
    el.style.transform = `translate(${(cx - sw / 2).toFixed(1)}px, ${(cy - sh / 2).toFixed(1)}px)`;
    requestAnimationFrame(tick);
  };
  tick();
}
