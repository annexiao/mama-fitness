import assert from "node:assert";
import { pickRoutine } from "../static/composer.js";

const ex = [
  { id: "a", body_part: "臀腿", intensity: "中等", minutes: 4, sets: "2x12", aspects: ["力量"] },
  { id: "b", body_part: "臀腿", intensity: "轻松", minutes: 5, sets: "2x15", aspects: ["柔韧性"] },
  { id: "c", body_part: "手臂", intensity: "中等", minutes: 4, sets: "2x12", aspects: ["力量"] },
  { id: "d", body_part: "全身", intensity: "加把劲", minutes: 3, sets: "2x10", aspects: ["稳定性"] },
];

// body-part filter includes 全身, excludes 手臂
let r = pickRoutine(ex, { bodyPart: "臀腿", minutes: 30, intensity: "中等" });
assert.ok(r.items.every((i) => i.body_part === "臀腿" || i.body_part === "全身"), "only 臀腿/全身");
assert.ok(!r.items.some((i) => i.body_part === "手臂"), "no 手臂");

// intensity ceiling excludes 加把劲 when 中等 selected
assert.ok(!r.items.some((i) => i.intensity === "加把劲"), "no 加把劲 above ceiling");

// no repeats + warmup/cooldown present
assert.strictEqual(new Set(r.items.map((i) => i.id)).size, r.items.length, "no repeats");
assert.ok(r.warmup && r.cooldown, "warmup + cooldown");

// 'all' body part + high intensity includes everything
r = pickRoutine(ex, { bodyPart: "all", minutes: 45, intensity: "加把劲" });
assert.ok(r.items.length >= 2, "picks multiple");

// aspects filter: only 柔韧性 -> just exercise b
r = pickRoutine(ex, { bodyPart: "all", minutes: 45, intensity: "加把劲", aspects: ["柔韧性"] });
assert.ok(r.items.every((i) => i.aspects.includes("柔韧性")), "aspect filter keeps only 柔韧性");
assert.strictEqual(r.items.length, 1, "only one 柔韧性 exercise");

// empty aspects -> no aspect filter
r = pickRoutine(ex, { bodyPart: "all", minutes: 45, intensity: "加把劲", aspects: [] });
assert.ok(r.items.length >= 2, "empty aspects = no filter");

console.log("composer algo OK");
