"""Generate raster brand assets (favicon.ico, apple-touch-icon.png, og-image.png).

Run from repo root:
    python scripts/generate_brand_assets.py

Output written to assets/icons/. Idempotent — overwrites existing files.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

BRAND_BLUE = (21, 101, 192)        # #1565c0
BRAND_BLUE_DARK = (13, 71, 161)    # #0d47a1
BRAND_CYAN = (0, 188, 235)         # #00bceb
WHITE = (255, 255, 255)


def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int],
                       bottom: tuple[int, int, int]) -> Image.Image:
    """Return an RGB image filled with a top→bottom-right gradient."""
    w, h = size
    img = Image.new("RGB", size, top)
    pixels = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(w):
            pixels[x, y] = (r, g, b)
    return img


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1),
                                           radius=radius, fill=255)
    return mask


def _icon_mark(size: int) -> Image.Image:
    """Square icon with the brand 'X' mark — matches favicon.svg."""
    img = _vertical_gradient((size, size), BRAND_BLUE, BRAND_BLUE_DARK)
    # Round the corners
    mask = _rounded_mask((size, size), radius=int(size * 0.1875))
    rounded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rounded.paste(img, (0, 0), mask)

    draw = ImageDraw.Draw(rounded)
    # X stroke — two crossing rounded rectangles
    s = size
    pad = int(s * 0.22)
    stroke = max(2, int(s * 0.11))
    # diagonal \
    draw.line([(pad, pad), (s - pad, s - pad)], fill=WHITE, width=stroke)
    # diagonal /
    draw.line([(s - pad, pad), (pad, s - pad)], fill=WHITE, width=stroke)
    # cyan accent dot top-right
    dot_r = int(s * 0.09)
    draw.ellipse([(s - pad - dot_r, pad - dot_r),
                  (s - pad + dot_r, pad + dot_r)], fill=BRAND_CYAN)
    return rounded


def write_favicon_ico() -> None:
    """Multi-resolution .ico (16, 32, 48)."""
    base = _icon_mark(256)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    path = OUT / "favicon.ico"
    base.save(path, format="ICO", sizes=sizes)
    print(f"  wrote {path.relative_to(ROOT)}")


def write_apple_touch_icon() -> None:
    img = _icon_mark(180)
    path = OUT / "apple-touch-icon.png"
    img.save(path, format="PNG", optimize=True)
    print(f"  wrote {path.relative_to(ROOT)}")


def write_pwa_icons() -> None:
    for size in (192, 512):
        img = _icon_mark(size)
        path = OUT / f"icon-{size}.png"
        img.save(path, format="PNG", optimize=True)
        print(f"  wrote {path.relative_to(ROOT)}")


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def write_og_image() -> None:
    """1200×630 Open Graph / Twitter card image."""
    w, h = 1200, 630
    img = _vertical_gradient((w, h), BRAND_BLUE, BRAND_BLUE_DARK)
    draw = ImageDraw.Draw(img)

    # Diagonal cyan accent stripe in the corner
    draw.polygon([(w, 0), (w, 90), (w - 220, 0)], fill=BRAND_CYAN)

    # Mark in the top-left
    mark = _icon_mark(140)
    img.paste(mark, (72, 72), mark)

    # Headline
    title_font = _load_font(72, bold=True)
    sub_font = _load_font(34)
    tag_font = _load_font(24, bold=True)

    draw.text((72, 250), "Cisco IOS-XE", font=title_font, fill=WHITE)
    draw.text((72, 332), "OpenAPI & YANG Docs", font=title_font, fill=WHITE)

    draw.text((72, 460), "608 OpenAPI specs · 5 releases · Multi-version",
              font=sub_font, fill=(220, 235, 255))

    # Pill tag bottom-left
    pill_text = "ciscodevnet.github.io/cisco-ios-xe-openapi-swagger"
    bbox = draw.textbbox((0, 0), pill_text, font=tag_font)
    pad_x, pad_y = 18, 10
    px, py = 72, h - 70
    pw = bbox[2] - bbox[0] + pad_x * 2
    ph = bbox[3] - bbox[1] + pad_y * 2
    draw.rounded_rectangle([px, py - ph + 4, px + pw, py + 4], radius=ph // 2,
                           fill=(255, 255, 255, 40), outline=BRAND_CYAN, width=2)
    draw.text((px + pad_x, py - ph + 4 + pad_y - bbox[1]), pill_text,
              font=tag_font, fill=BRAND_CYAN)

    path = OUT / "og-image.png"
    img.save(path, format="PNG", optimize=True)
    print(f"  wrote {path.relative_to(ROOT)}")


def main() -> int:
    print(f"Generating brand assets into {OUT.relative_to(ROOT)}/")
    write_favicon_ico()
    write_apple_touch_icon()
    write_pwa_icons()
    write_og_image()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
