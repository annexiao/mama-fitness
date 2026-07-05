// Client-side workout composer. Rule-based random from exercises.json.
// Loaded as a module so pickRoutine is unit-testable under node.

import { createSlider } from "./slider.js";

const INTENSITY_ORDER = { "轻松": 1, "中等": 2, "加把劲": 3 };

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function pickRoutine(exercises, { bodyPart, minutes, intensity, aspects }) {
  const ceil = INTENSITY_ORDER[intensity] || 3;
  const want = aspects || [];
  let pool = exercises.filter((e) => (INTENSITY_ORDER[e.intensity] || 2) <= ceil);
  if (bodyPart && bodyPart !== "all") {
    pool = pool.filter((e) => e.body_part === bodyPart || e.body_part === "全身");
  }
  if (want.length) {
    // keep exercises that train at least one of the selected aspects
    pool = pool.filter((e) => (e.aspects || []).some((a) => want.includes(a)));
  }
  pool = shuffle(pool.slice());

  const target = Number(minutes) || 30;
  const budget = Math.max(target - 5, 8); // reserve ~5 min for warm-up + cool-down
  const items = [];
  let total = 0;
  for (const e of pool) {
    if (total >= budget && items.length >= 2) break;
    items.push(e);
    total += Number(e.minutes) || 4;
  }
  if (items.length === 0 && pool.length) items.push(pool[0]);

  return {
    warmup: { name: "原地踏步热身", detail: "2 分钟" },
    items,
    cooldown: { name: "拉伸放松", detail: "3 分钟" },
  };
}

// ---- browser bootstrap (skipped under node) ----
if (typeof document !== "undefined") {
  let duration = null; // slider handle, set in wire()

  const one = (group) => {
    const on = document.querySelector(`.pickrow[data-group="${group}"] .pill.on`);
    return on ? on.dataset.value : null;
  };
  const minutes = () => (duration ? duration.get() : 20);

  // A routine step as a flowchart box (with a small GIF), arrows between boxes.
  const box = (icon, gif, name, detail, url, warm) => {
    const cls = warm ? "fbox warmup" : "fbox";
    const media = gif
      ? `<span class="fgif"><img src="${gif}" alt=""></span>`
      : `<span class="fgif">${icon}</span>`;
    const inner =
      `${media}<span class="fmeta"><span class="fname">${name}</span>` +
      `<span class="fset">${detail}</span></span>`;
    return url
      ? `<a class="${cls}" href="${url}">${inner}</a>`
      : `<div class="${cls}">${inner}</div>`;
  };
  const arrow = '<div class="farrow">↓</div>';

  // aspect filter: "all" (都可以) or nothing selected -> no filter
  const aspectFilter = () => {
    const a = one("aspects");
    return !a || a === "all" ? [] : [a];
  };

  const render = (r) => {
    const plan = document.getElementById("plan");
    const bp = one("bodyPart") === "all" ? "全身" : one("bodyPart");
    const asp = aspectFilter();
    if (!r.items.length) {
      plan.innerHTML =
        '<div class="plan"><div class="plan-empty">这个组合暂时没有合适的动作，换个选择试试。</div></div>';
      return;
    }
    const meta = [bp, `${minutes()} 分钟`, one("intensity")]
      .concat(asp.length ? asp : [])
      .join(" · ");
    const boxes = [box("♨", "", r.warmup.name, r.warmup.detail, null, true)]
      .concat(r.items.map((e) => box("🎬", e.gif, e.name, e.sets, e.url, false)))
      .concat([box("🧘", "", r.cooldown.name, r.cooldown.detail, null, true)]);
    let h = '<div class="plan"><div class="pt">今天的组合</div>';
    h += `<div class="pmeta">${meta}</div>`;
    h += `<div class="flow">${boxes.join(arrow)}</div>`;
    h += '</div><button class="reroll" id="reroll">↻ 换一套</button>';
    plan.innerHTML = h;
    document.getElementById("reroll").addEventListener("click", generate);
  };

  async function generate() {
    const all = await fetch("/exercises.json").then((r) => r.json());
    render(
      pickRoutine(all, {
        bodyPart: one("bodyPart"),
        minutes: minutes(),
        intensity: one("intensity"),
        aspects: aspectFilter(),
      }),
    );
    suggestVideo();
  }

  // ---- video suggestion: pick a ready-made video near the chosen duration ----
  let VIDEOS = null;
  const loadVideos = async () => {
    if (!VIDEOS) VIDEOS = await fetch("/videos.json").then((r) => r.json()).catch(() => []);
    return VIDEOS;
  };
  const pickVideo = (vids, target, bodyPart) => {
    if (!vids.length) return null;
    // duration is a hard cap: never longer than the chosen 练多久 (shorter is fine)
    let pool = vids.filter((v) => (Number(v.minutes) || 0) <= target);
    if (!pool.length) return null;
    // prefer videos for the chosen body part; 全身 videos fit anything.
    // fall back to any (within duration) if nothing matches, so it's never empty.
    if (bodyPart && bodyPart !== "all" && bodyPart !== "全身") {
      const match = pool.filter(
        (v) =>
          v.body_part === "全身" ||
          v.body_part === bodyPart ||
          (v.body_part && (bodyPart.indexOf(v.body_part) >= 0 || v.body_part.indexOf(bodyPart) >= 0)),
      );
      if (match.length) pool = match;
    }
    return pool[Math.floor(Math.random() * pool.length)];
  };
  async function suggestVideo() {
    const box = document.getElementById("videoSuggest");
    if (!box) return;
    const v = pickVideo(await loadVideos(), minutes(), one("bodyPart"));
    if (!v) {
      box.innerHTML = "";
      return;
    }
    box.innerHTML =
      '<div class="section-label" style="margin-top:26px">🎬 或者，跟一个视频练</div>' +
      '<div class="vcard"><div class="bili"><iframe src="' +
      v.embed +
      '" scrolling="no" frameborder="0" allowfullscreen="true" loading="lazy"></iframe></div>' +
      '<div class="vinfo"><span class="vt">' +
      v.title +
      '</span><span class="vdur">' +
      v.minutes +
      " 分钟</span></div>" +
      (v.note ? '<div class="vnote">' + v.note + "</div>" : "") +
      '</div><button class="reroll" id="rerollVideo">↻ 换一个视频</button>';
    document.getElementById("rerollVideo").addEventListener("click", suggestVideo);
  }

  const wire = () => {
    document.querySelectorAll(".pickrow").forEach((row) => {
      const multi = row.dataset.multi === "true";
      row.querySelectorAll(".pill").forEach((p) => {
        p.addEventListener("click", () => {
          if (multi) {
            p.classList.toggle("on"); // aspects: toggle, allow several / none
          } else {
            row.querySelectorAll(".pill").forEach((x) => x.classList.remove("on"));
            p.classList.add("on");
          }
        });
      });
    });
    const sliderEl = document.getElementById("durationSlider");
    if (sliderEl) {
      duration = createSlider(sliderEl, {
        min: 10,
        max: 45,
        step: 5,
        value: 20,
        format: (v) => v + " 分钟",
      });
    }
    const gen = document.getElementById("gen");
    if (gen) gen.addEventListener("click", generate);
    generate(); // show a first routine on load
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
}
