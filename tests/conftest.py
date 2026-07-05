from pathlib import Path

import pytest


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """A minimal valid data dir for validation tests."""
    (tmp_path / "site.yaml").write_text(
        "brand: 妈妈的训练\nletter: |\n  陪我去很多地方。\nbenefits: [上楼更轻松]\n",
        encoding="utf-8",
    )
    (tmp_path / "tools.yaml").write_text(
        "tools:\n  - {id: loop-band, name: 弹力圈, emoji: 🟢,"
        " function: 练臀腿, frequency: 每周 2 到 3 次}\n",
        encoding="utf-8",
    )
    (tmp_path / "exercises.yaml").write_text(
        "exercises:\n  - id: crab-walk\n    tool: loop-band\n    name: 侧向螃蟹步\n"
        "    body_part: 臀腿\n    intensity: 中等\n    minutes: 4\n    sets: 2 组\n"
        "    target: 臀中肌\n    why: 帮膝盖更稳\n"
        "    self_check:\n      - {where: 臀部, symptom: 酸, verdict: ok}\n",
        encoding="utf-8",
    )
    (tmp_path / "cardio.yaml").write_text(
        "cardio:\n  - {id: elliptical, name: 椭圆机, emoji: 🚴, function: 有氧}\n",
        encoding="utf-8",
    )
    (tmp_path / "info.yaml").write_text(
        "info:\n  - {id: knee-brace, name: 护膝, emoji: 🦵, group: 护具,"
        " caution: 是辅助不是替代}\n"
        "  - {id: yoga-mat, name: 瑜伽垫, emoji: 🧘, group: 配件}\n",
        encoding="utf-8",
    )
    (tmp_path / "knowledge.yaml").write_text(
        "knowledge:\n"
        "  - key: training\n    label: 训练知识\n    icon: 🏋️\n"
        "    articles:\n      - {id: reps, title: 次数, body: 6 到 12 次}\n"
        "  - key: nutrition\n    label: 饮食知识\n    icon: 🥗\n"
        "    articles:\n      - {id: protein, title: 蛋白质, body: 每餐都要有}\n",
        encoding="utf-8",
    )
    return tmp_path
