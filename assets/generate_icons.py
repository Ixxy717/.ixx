"""
IXX Icon Generator

Reads assets/ixx-icon-source.png (673x673) and produces:
  assets/generated/ixx-icon-16.png
  assets/generated/ixx-icon-24.png
  assets/generated/ixx-icon-32.png
  assets/generated/ixx-icon-48.png
  assets/generated/ixx-icon-64.png
  assets/generated/ixx-icon-128.png
  assets/generated/ixx-icon-256.png
  assets/generated/ixx-icon.ico   (multi-size Windows icon)

SVG is intentionally skipped: embedding raster data in SVG produces poor results
at small sizes. PNG and ICO are the canonical icon formats for IXX.

Usage:
    python assets/generate_icons.py

Requires Pillow:
    pip install Pillow
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent
SOURCE     = REPO_ROOT / "assets" / "ixx-icon-source.png"
OUTPUT_DIR = REPO_ROOT / "assets" / "generated"

SIZES = [16, 24, 32, 48, 64, 128, 256]

# Sizes to bundle into the .ico (Windows standard set)
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]


def check_pillow() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("Pillow is required but not installed.")
        print("Install it with:  pip install Pillow")
        sys.exit(1)


def generate() -> None:
    check_pillow()

    from PIL import Image

    if not SOURCE.exists():
        print(f"Source icon not found: {SOURCE}")
        print("Place your 673x673 PNG at assets/ixx-icon-source.png and try again.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading source icon: {SOURCE}")
    img = Image.open(SOURCE).convert("RGBA")
    print(f"  Source size: {img.width}x{img.height}")

    # Generate individual PNGs
    png_paths = []
    for size in SIZES:
        resized = img.resize((size, size), Image.LANCZOS)
        # Apply a sharpening pass for small sizes where detail matters most
        if size <= 48:
            from PIL import ImageFilter
            resized = resized.filter(ImageFilter.UnsharpMask(radius=0.6, percent=120, threshold=2))
        out = OUTPUT_DIR / f"ixx-icon-{size}.png"
        resized.save(out, "PNG", optimize=True)
        png_paths.append(out)
        print(f"  Generated: {out.name}")

    # Generate multi-size .ico
    # Pillow's ICO writer uses BMP for frames <256px which flattens alpha to white.
    # Instead, embed each frame as a raw PNG chunk so all sizes keep full RGBA transparency.
    import io, struct

    ico_path = OUTPUT_DIR / "ixx-icon.ico"
    png_chunks = []
    for size in ICO_SIZES:
        frame = img.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        frame.save(buf, "PNG")
        png_chunks.append(buf.getvalue())

    count = len(png_chunks)
    header = struct.pack("<HHH", 0, 1, count)
    dir_offset = 6 + count * 16
    entries = b""
    data = b""
    for size, chunk in zip(ICO_SIZES, png_chunks):
        w = size if size < 256 else 0  # 0 means 256 in the ICO spec
        entries += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(chunk), dir_offset + len(data))
        data += chunk

    with open(ico_path, "wb") as f:
        f.write(header + entries + data)
    print(f"  Generated: {ico_path.name}  (multi-size PNG-embedded, full RGBA: {ICO_SIZES})")

    # Copy VS Code icons into extension folder for convenience
    vscode_icons = REPO_ROOT / "editor" / "vscode" / "icons"
    vscode_icons.mkdir(parents=True, exist_ok=True)
    vscode_copies = [32, 128]
    for size in vscode_copies:
        src = OUTPUT_DIR / f"ixx-icon-{size}.png"
        dst = vscode_icons / f"ixx-icon-{size}.png"
        import shutil
        shutil.copy2(src, dst)
        print(f"  Copied to: editor/vscode/icons/ixx-icon-{size}.png")

    print()
    print("Done. Generated files:")
    for p in png_paths:
        print(f"  {p.relative_to(REPO_ROOT)}")
    print(f"  assets/generated/ixx-icon.ico")
    print()
    print("Note: SVG is intentionally not generated.")
    print("  PNG and ICO are the canonical IXX icon formats.")
    print("  VS Code icon: editor/vscode/icons/ixx-icon-32.png")
    print("  Windows ICO:  assets/generated/ixx-icon.ico")


if __name__ == "__main__":
    generate()
