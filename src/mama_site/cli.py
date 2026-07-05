from pathlib import Path

from .build import ROOT, build


def main() -> None:
    out = ROOT / "dist"
    build(ROOT / "data", out)
    print("built ->", out)


if __name__ == "__main__":
    main()
