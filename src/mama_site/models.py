"""Data models for the 妈妈的训练 fitness education site.

Content lives in YAML under ``data/``; ``load_site`` reads and validates it into
dataclasses. Four content shapes:

- ``Tool``     — strength tool with an exercise gallery (reps x sets). 弹力圈/小球/弹力带/壶铃
- ``Cardio``   — cardio machine, duration/intensity based (not reps). 椭圆机
- ``InfoItem`` — 护具 (护膝/登山杖) and 配件 (瑜伽垫/跑步鞋): a notes page, no exercises.
- ``Knowledge``— training + nutrition articles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


def video_embed_url(url: str) -> str:
    """Turn a Bilibili or YouTube watch URL into an embeddable player URL. '' if unknown."""
    if not url:
        return ""
    m = re.search(r"(BV[0-9A-Za-z]+)", url)
    if m and "bilibili" in url:
        # autoplay=0 → shows the cover as a preview and does NOT autoplay
        return f"//player.bilibili.com/player.html?bvid={m.group(1)}&page=1&danmaku=0&high_quality=1&autoplay=0"
    m = re.search(r"(?:v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([0-9A-Za-z_-]{6,})", url)
    if m and ("youtu" in url):
        return f"https://www.youtube.com/embed/{m.group(1)}"
    return ""

VERDICTS = {"ok", "stop", "check"}
INFO_GROUPS = {"护具", "配件"}


@dataclass
class SelfCheck:
    where: str
    symptom: str
    verdict: str  # ok | stop | check


@dataclass
class Exercise:
    id: str
    tool: str
    name: str
    body_part: str  # 臀腿 | 核心腰 | 手臂 | 胸背 | 肩颈 | 全身
    intensity: str  # 轻松 | 中等 | 加把劲
    minutes: int
    sets: str
    target: str
    why: str
    # optional gallery sub-group label within a tool (e.g. "🟢 初级"). "" = ungrouped.
    level: str = ""
    # which aspect(s) this exercise trains — multi. 力量 | 柔韧性 | 稳定性
    aspects: list[str] = field(default_factory=list)
    science_tip: str = ""
    band: str = ""  # for the shared 弹力带 tool: which band this exercise uses
    dos: list[str] = field(default_factory=list)
    donts: list[str] = field(default_factory=list)
    self_check: list[SelfCheck] = field(default_factory=list)
    gif: str = ""
    anatomy: str = ""
    video: str = ""  # a Bilibili or YouTube URL; embedded on the detail page
    extra_videos: list[str] = field(default_factory=list)  # additional 讲解 videos beyond `video`
    # anatomy highlight: body-highlighter region slugs to light up (e.g. ["gluteal"]).
    # empty = no body diagram (e.g. 盆底肌 has no surface region).
    muscles: list[str] = field(default_factory=list)
    # optional advanced progression, rendered as a second section on the detail page
    advanced_name: str = ""
    advanced_intro: str = ""  # what it is + when it's OK to progress to it
    advanced_video: str = ""
    advanced_gif: str = ""

    @property
    def video_embed(self) -> str:
        return video_embed_url(self.video)

    @property
    def extra_video_embeds(self) -> list[str]:
        return [e for e in (video_embed_url(v) for v in self.extra_videos) if e]

    @property
    def advanced_video_embed(self) -> str:
        return video_embed_url(self.advanced_video)


@dataclass
class Tool:
    id: str
    name: str
    emoji: str
    function: str
    frequency: str
    photo: str = ""
    note: str = ""
    exercises: list[Exercise] = field(default_factory=list)


@dataclass
class Cardio:
    id: str
    name: str
    emoji: str
    function: str
    photo: str = ""
    how_to_use: list[str] = field(default_factory=list)
    duration: str = ""
    intensity: str = ""
    knee_note: str = ""
    self_check: list[SelfCheck] = field(default_factory=list)
    video: str = ""


@dataclass
class InfoItem:
    """护具 or 配件 — a notes page, no exercises."""

    id: str
    name: str
    emoji: str
    group: str  # 护具 | 配件
    photo: str = ""
    why: str = ""  # prose "为什么重要" intro, rendered above the notes on the item page
    when_to_use: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    how_to_choose: str = ""
    caution: str = ""
    videos: list[str] = field(default_factory=list)  # Bilibili/YouTube 讲解 URLs, embedded on the item page

    @property
    def video_embeds(self) -> list[str]:
        return [e for e in (video_embed_url(v) for v in self.videos) if e]


@dataclass
class Video:
    id: str
    title: str
    platform: str  # bilibili | youtube
    vid: str  # Bilibili BV id, or YouTube video id
    minutes: int
    tags: list[str] = field(default_factory=list)  # keywords for the /videos filter
    tool: str = ""  # related tool id (shown on that tool page); "" = home-only
    body_part: str = ""
    note: str = ""

    @property
    def embed(self) -> str:
        if self.platform == "youtube":
            return f"https://www.youtube.com/embed/{self.vid}"
        # autoplay=0 → shows the cover as a preview and does NOT autoplay
        return f"//player.bilibili.com/player.html?bvid={self.vid}&page=1&danmaku=0&high_quality=1&autoplay=0"


@dataclass
class Article:
    id: str
    title: str
    body: str


@dataclass
class KnowledgeGroup:
    key: str
    label: str
    icon: str
    articles: list[Article] = field(default_factory=list)


@dataclass
class Knowledge:
    groups: list[KnowledgeGroup] = field(default_factory=list)


@dataclass
class Benefit:
    text: str
    img: str = ""  # optional small cartoon shown next to the benefit


@dataclass
class SiteMeta:
    brand: str
    letter: str
    benefits: list[Benefit] = field(default_factory=list)
    warm_strip: str = ""  # short line shown atop the composer home


@dataclass
class Site:
    meta: SiteMeta
    tools: list[Tool]
    cardio: list[Cardio]
    info: list[InfoItem]
    knowledge: Knowledge
    videos: list[Video] = field(default_factory=list)

    @property
    def gear(self) -> list[InfoItem]:
        return [i for i in self.info if i.group == "护具"]

    @property
    def accessories(self) -> list[InfoItem]:
        return [i for i in self.info if i.group == "配件"]


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _self_check(raw: list[dict], owner: str) -> list[SelfCheck]:
    out = []
    for s in raw:
        sc = SelfCheck(**s)
        if sc.verdict not in VERDICTS:
            raise ValueError(f"{owner}: bad verdict {sc.verdict!r} (expected one of {VERDICTS})")
        out.append(sc)
    return out


def load_site(data_dir: Path) -> Site:
    meta_raw = _load_yaml(data_dir / "site.yaml")
    benefits = [
        Benefit(text=b) if isinstance(b, str) else Benefit(**b)
        for b in meta_raw.get("benefits", [])
    ]
    meta = SiteMeta(
        brand=meta_raw["brand"],
        letter=meta_raw["letter"],
        benefits=benefits,
        warm_strip=meta_raw.get("warm_strip", ""),
    )

    exercises = []
    for e in _load_yaml(data_dir / "exercises.yaml").get("exercises", []):
        sc = _self_check(e.get("self_check", []), f"exercise {e.get('id')}")
        exercises.append(Exercise(**{**e, "self_check": sc}))

    tools = [Tool(**t) for t in _load_yaml(data_dir / "tools.yaml").get("tools", [])]
    tool_ids = {t.id for t in tools}
    for ex in exercises:
        if ex.tool not in tool_ids:
            raise ValueError(f"exercise {ex.id}: unknown tool {ex.tool!r}")
    for t in tools:
        t.exercises = [e for e in exercises if e.tool == t.id]

    cardio = []
    for c in _load_yaml(data_dir / "cardio.yaml").get("cardio", []):
        sc = _self_check(c.get("self_check", []), f"cardio {c.get('id')}")
        cardio.append(Cardio(**{**c, "self_check": sc}))

    info = []
    for i in _load_yaml(data_dir / "info.yaml").get("info", []):
        item = InfoItem(**i)
        if item.group not in INFO_GROUPS:
            raise ValueError(f"info {item.id}: bad group {item.group!r} (expected one of {INFO_GROUPS})")
        info.append(item)

    kraw = _load_yaml(data_dir / "knowledge.yaml").get("knowledge", [])
    knowledge = Knowledge(
        groups=[
            KnowledgeGroup(
                key=g["key"],
                label=g["label"],
                icon=g.get("icon", ""),
                articles=[Article(**a) for a in g.get("articles", [])],
            )
            for g in kraw
        ]
    )

    videos = [Video(**v) for v in _load_yaml(data_dir / "videos.yaml").get("videos", [])]

    return Site(
        meta=meta, tools=tools, cardio=cardio, info=info, knowledge=knowledge, videos=videos
    )


# Shared verdict presentation: icon + human label (never color alone).
VERDICT_UI = {
    "ok": ("✓", "正常，继续"),
    "stop": ("✕", "先停下来"),
    "check": ("!", "检查姿势"),
}
