"""Static site generator: YAML data -> HTML in dist/ (+ exercises.json for composer)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .anatomy import BACK, FRONT, VIEWBOX_BACK, VIEWBOX_FRONT
from .models import VERDICT_UI, Site, load_site

ROOT = Path(__file__).resolve().parents[2]


def _body_svg(view: dict[str, list[str]], lit: set[str], viewbox: str) -> str:
    """Render one body view; paths of `lit` muscles get the .lit class, rest .base.

    Front and back share one coordinate space: the back is offset +724 in x, so
    each view needs its own viewBox (front "0 0 724 1448", back "724 0 724 1448").
    """
    paths = []
    for slug, ds in view.items():
        if slug == "hair":
            continue
        cls = "lit" if slug in lit else "base"
        for d in ds:
            paths.append(f'<path class="{cls}" d="{d}"/>')
    return f'<svg viewBox="{viewbox}" class="body" aria-hidden="true">{"".join(paths)}</svg>'


def _anatomy_html(muscles: list[str]) -> str:
    """Front/back body diagram with the target muscles lit. '' if no muscles set."""
    if not muscles:
        return ""
    lit = set(muscles)
    fl, bl = lit & set(FRONT), lit & set(BACK)
    parts = []
    if fl:
        parts.append(f'<figure class="bwrap"><figcaption class="lab">正面</figcaption>{_body_svg(FRONT, fl, VIEWBOX_FRONT)}</figure>')
    if bl:
        parts.append(f'<figure class="bwrap"><figcaption class="lab">背面</figcaption>{_body_svg(BACK, bl, VIEWBOX_BACK)}</figure>')
    if not parts:
        return ""
    return f'<div class="bodies">{"".join(parts)}</div>'


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["verdict_ui"] = VERDICT_UI
    return env


def _write(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _level_groups(exercises):
    """Group a tool's exercises by their `level` label, preserving yaml order.
    Returns list of (label, [exercises]); label "" means ungrouped."""
    groups: list[tuple[str, list]] = []
    for e in exercises:
        lvl = e.level or ""
        if not groups or groups[-1][0] != lvl:
            groups.append((lvl, []))
        groups[-1][1].append(e)
    return groups


def _exercises_json(site: Site) -> str:
    rows = []
    for t in site.tools:
        for e in t.exercises:
            rows.append(
                {
                    "id": e.id,
                    "tool": t.id,
                    "tool_name": t.name,
                    "name": e.name,
                    "body_part": e.body_part,
                    "aspects": e.aspects,
                    "intensity": e.intensity,
                    "minutes": e.minutes,
                    "sets": e.sets,
                    "target": e.target,
                    "gif": e.gif,
                    "url": f"/tools/{t.id}/{e.id}/",
                }
            )
    return json.dumps(rows, ensure_ascii=False, indent=2)


def build(data_dir: Path, out_dir: Path) -> None:
    site = load_site(data_dir)
    env = _env()
    ctx = {"site": site}

    # Clean the output dir first so deleted pages/assets don't linger as stale
    # files (e.g. a removed exercise's page would otherwise keep 200-ing).
    if out_dir.exists():
        shutil.rmtree(out_dir)

    def render(template: str, rel: str, active: str | None, **kw) -> None:
        html = env.get_template(template).render(nav_active=active, **ctx, **kw)
        _write(out_dir / rel, html)

    # family photos (private, gitignored, deploy-from-disk) — build scans the
    # folder so new photos are picked up automatically. add via scripts/add-photos.sh
    photos_dir = ROOT / "static" / "photos"
    photos = sorted(f"/static/photos/{p.name}" for p in photos_dir.glob("*.jpg")) if photos_dir.exists() else []

    render("home.html", "index.html", "home", photos=photos)
    render("why.html", "why/index.html", "why", photos=photos)
    render("tools_overview.html", "tools/index.html", "tools")
    render("learn.html", "learn/index.html", "learn")
    # Filter chips on /videos: only equipment + body-part tags (by design: drop
    # activity tags like 力量/有氧/热身/跟练/拉伸/放松/普拉提/无器械).
    FILTER_TAG_ORDER = [
        "弹力圈", "弹力带", "小球", "壶铃", "泡沫轴",  # 器械
        "臀腿", "腿", "核心", "腰", "胸背", "肩颈", "全身",  # 部位
    ]
    present = {t for v in site.videos for t in v.tags}
    all_tags = [t for t in FILTER_TAG_ORDER if t in present]
    tool_names = {t.id: t.name for t in site.tools}
    render("videos.html", "videos/index.html", "videos", all_tags=all_tags, tool_names=tool_names)
    render("about.html", "about/index.html", None)
    render("thanks.html", "thanks/index.html", None)

    for t in site.tools:
        render("tool_page.html", f"tools/{t.id}/index.html", "tools", tool=t,
               level_groups=_level_groups(t.exercises),
               tool_videos=[v for v in site.videos if v.tool == t.id])
        n = len(t.exercises)
        for i, e in enumerate(t.exercises):
            nxt = t.exercises[(i + 1) % n] if n > 1 else None
            prv = t.exercises[(i - 1) % n] if n > 1 else None
            render("exercise.html", f"tools/{t.id}/{e.id}/index.html", "tools", tool=t, ex=e,
                   anatomy_html=_anatomy_html(e.muscles), next_ex=nxt, prev_ex=prv)

    for c in site.cardio:
        render("cardio_page.html", f"tools/{c.id}/index.html", "tools", cardio=c)

    for i in site.info:
        render("info_page.html", f"tools/{i.id}/index.html", "tools", item=i)

    # static assets
    if (out_dir / "static").exists():
        shutil.rmtree(out_dir / "static")
    shutil.copytree(ROOT / "static", out_dir / "static")

    _write(out_dir / "exercises.json", _exercises_json(site))
    _write(
        out_dir / "videos.json",
        json.dumps(
            [
                {"id": v.id, "title": v.title, "platform": v.platform, "embed": v.embed,
                 "minutes": v.minutes, "tags": v.tags, "body_part": v.body_part, "note": v.note}
                for v in site.videos
            ],
            ensure_ascii=False,
            indent=2,
        ),
    )
    # knowledge.json — flat list of every /learn article, for the home page's
    # 「训练小知识」浮卡 (client-side random pick, different on each refresh).
    _write(
        out_dir / "knowledge.json",
        json.dumps(
            [
                {"id": a.id, "title": a.title, "body": a.body, "group": g.label, "icon": g.icon}
                for g in site.knowledge.groups
                for a in g.articles
            ],
            ensure_ascii=False,
            indent=2,
        ),
    )
