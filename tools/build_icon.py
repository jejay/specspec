"""Regenerate the Windows launcher container from the unchanged supplied PNG.

Developer-only Pillow dependency; application builds use the tracked ICO.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / "branding/app-icon.png"
    with Image.open(source) as image:
        image.save(
            ROOT / "branding/app-icon.ico",
            format="ICO",
            sizes=[(n, n) for n in [16, 24, 32, 48, 64, 128, 256]],
        )
    print("Built branding/app-icon.ico from the selected launcher PNG.")


if __name__ == "__main__":
    main()
