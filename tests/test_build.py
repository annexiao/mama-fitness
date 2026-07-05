from pathlib import Path

from mama_site.build import build


def _build(tmp_path: Path, data_dir: Path) -> Path:
    out = tmp_path / "dist"
    build(data_dir, out)
    return out


def test_home_has_nav_and_composer(tmp_path, data_dir):
    out = _build(tmp_path, data_dir)
    home = (out / "index.html").read_text("utf-8")
    assert "妈妈的训练" in home
    assert 'href="/tools/"' in home
    assert "今天练什么" in home
    assert (out / "exercises.json").exists()


def test_tool_gallery_and_detail(tmp_path, data_dir):
    out = _build(tmp_path, data_dir)
    gallery = (out / "tools" / "loop-band" / "index.html").read_text("utf-8")
    assert "侧向螃蟹步" in gallery
    assert 'href="/tools/loop-band/crab-walk/"' in gallery
    detail = (out / "tools" / "loop-band" / "crab-walk" / "index.html").read_text("utf-8")
    assert "臀中肌" in detail
    # self-check renders icon + label (never color alone):
    assert "正常，继续" in detail and "✓" in detail


def test_cardio_gear_accessory_pages(tmp_path, data_dir):
    out = _build(tmp_path, data_dir)
    assert (out / "tools" / "elliptical" / "index.html").exists()
    gear = (out / "tools" / "knee-brace" / "index.html").read_text("utf-8")
    assert "是辅助不是替代" in gear
    assert (out / "tools" / "yoga-mat" / "index.html").exists()


def test_why_learn_about(tmp_path, data_dir):
    out = _build(tmp_path, data_dir)
    assert "陪我去很多地方" in (out / "why" / "index.html").read_text("utf-8")
    learn = (out / "learn" / "index.html").read_text("utf-8")
    assert "蛋白质" in learn and "次数" in learn
    about = (out / "about" / "index.html").read_text("utf-8")
    assert "不作为专业的医疗或健身建议" in about and "生日礼物" in about
