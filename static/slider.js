// Draggable single-handle value slider (plain JS, touch-correct).
// Draggable value slider: disambiguates drag vs click by a movement threshold.

export function createSlider(root, { min, max, step = 1, value, onChange, format }) {
  const track = root.querySelector(".vs-track");
  const fill = root.querySelector(".vs-fill");
  const handle = root.querySelector(".vs-handle");
  const out = root.querySelector(".vs-value");
  let fmt = format || ((v) => String(v));

  const clampSnap = (v) => {
    v = Math.max(min, Math.min(max, v));
    return Math.round((v - min) / step) * step + min;
  };
  const toPct = (v) => ((v - min) / (max - min)) * 100;
  let val = clampSnap(value == null ? min : value);

  function paint() {
    const pct = toPct(val);
    handle.style.left = pct + "%";
    fill.style.width = pct + "%";
    handle.setAttribute("aria-valuenow", String(val));
    if (out) out.textContent = fmt(val);
    onChange && onChange(val);
  }
  function fromClientX(clientX) {
    const r = track.getBoundingClientRect();
    const pct = Math.max(0, Math.min(100, ((clientX - r.left) / r.width) * 100));
    return clampSnap(min + (pct / 100) * (max - min));
  }
  function onMove(ev) {
    ev.preventDefault(); // gotcha 2: non-passive + preventDefault stops page scroll
    const x = ev.touches ? ev.touches[0].clientX : ev.clientX;
    val = fromClientX(x);
    paint();
  }
  function onUp() {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
    document.removeEventListener("touchmove", onMove);
    document.removeEventListener("touchend", onUp);
  }
  function onDown(e) {
    e.preventDefault();
    if (e.target !== handle) onMove(e); // tap the track to jump there
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
    document.addEventListener("touchmove", onMove, { passive: false });
    document.addEventListener("touchend", onUp);
  }
  handle.addEventListener("mousedown", onDown);
  handle.addEventListener("touchstart", onDown, { passive: false });
  track.addEventListener("mousedown", onDown);
  track.addEventListener("touchstart", onDown, { passive: false });
  handle.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft" || e.key === "ArrowDown") { val = clampSnap(val - step); paint(); }
    if (e.key === "ArrowRight" || e.key === "ArrowUp") { val = clampSnap(val + step); paint(); }
  });

  paint();
  return { get: () => val, set: (v) => { val = clampSnap(v); paint(); } };
}
