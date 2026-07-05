from pathlib import Path

import pytest

from mama_site.models import load_site


def test_load_joins_and_groups(data_dir: Path):
    site = load_site(data_dir)
    assert site.meta.brand == "妈妈的训练"
    assert site.tools[0].id == "loop-band"
    assert [e.id for e in site.tools[0].exercises] == ["crab-walk"]
    assert site.tools[0].exercises[0].self_check[0].verdict == "ok"
    assert site.cardio[0].id == "elliptical"
    assert [g.id for g in site.gear] == ["knee-brace"]
    assert [a.id for a in site.accessories] == ["yoga-mat"]
    keys = [g.key for g in site.knowledge.groups]
    assert keys == ["training", "nutrition"]
    assert site.knowledge.groups[1].articles[0].id == "protein"


def test_bad_verdict_raises(data_dir: Path):
    (data_dir / "exercises.yaml").write_text(
        "exercises:\n  - {id: x, tool: loop-band, name: n, body_part: 臀腿,"
        " intensity: 中等, minutes: 3, sets: s, target: t, why: w,"
        " self_check: [{where: a, symptom: b, verdict: WRONG}]}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="bad verdict"):
        load_site(data_dir)


def test_orphan_exercise_raises(data_dir: Path):
    (data_dir / "exercises.yaml").write_text(
        "exercises:\n  - {id: x, tool: nope, name: n, body_part: 臀腿,"
        " intensity: 中等, minutes: 3, sets: s, target: t, why: w}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown tool"):
        load_site(data_dir)


def test_bad_info_group_raises(data_dir: Path):
    (data_dir / "info.yaml").write_text(
        "info:\n  - {id: x, name: n, emoji: 🦵, group: NOPE}\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="bad group"):
        load_site(data_dir)
