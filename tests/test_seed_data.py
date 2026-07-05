"""Loads the REAL data/ files (not fixtures) to catch content typos early."""

from pathlib import Path

from mama_site.models import load_site

DATA = Path(__file__).resolve().parents[1] / "data"


def test_real_data_loads():
    site = load_site(DATA)
    assert len(site.tools) == 4, "expected 4 strength tools"
    assert all(t.exercises for t in site.tools), "every tool needs at least one exercise"
    assert site.cardio, "expected the elliptical"
    assert site.gear and site.accessories, "expected gear + accessories"
    keys = {g.key for g in site.knowledge.groups}
    assert {"training", "nutrition", "bloodsugar"} <= keys, "expected training/nutrition/bloodsugar"


def test_every_exercise_has_valid_tags():
    site = load_site(DATA)
    valid_bp = {"臀腿", "核心腰", "手臂", "胸背", "肩颈", "全身"}
    valid_int = {"轻松", "中等", "加把劲"}
    valid_aspect = {"力量", "柔韧性", "稳定性"}
    for t in site.tools:
        for e in t.exercises:
            assert e.body_part in valid_bp, f"{e.id}: bad body_part {e.body_part}"
            assert e.intensity in valid_int, f"{e.id}: bad intensity {e.intensity}"
            assert e.aspects, f"{e.id}: missing aspects"
            assert set(e.aspects) <= valid_aspect, f"{e.id}: bad aspect in {e.aspects}"
            assert e.minutes > 0


def test_bodypart_coverage():
    """Each pill in the composer should have at least one exercise to offer."""
    site = load_site(DATA)
    covered = {e.body_part for t in site.tools for e in t.exercises}
    for bp in ("臀腿", "核心腰", "胸背", "肩颈"):
        assert bp in covered, f"no exercise for body_part {bp}"
