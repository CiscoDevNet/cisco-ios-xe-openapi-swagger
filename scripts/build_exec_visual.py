"""Build an executive-ready 16:9 PNG summary of the IOS-XE Documentation Hub project.

Output: docs/exec_summary.png (1920x1080, < 10 MB).
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "exec_summary.png"

W, H = 1920, 1080

# Cisco-aligned palette
NAVY = (10, 35, 66)            # background
DEEP = (0, 53, 90)             # darker panel
CARD = (255, 255, 255)
CARD_SHADOW = (5, 22, 44)
CISCO_BLUE = (0, 188, 235)     # primary accent
CISCO_BLUE_DK = (27, 160, 215)
TEAL = (88, 185, 71)           # impact accent
ORANGE = (255, 158, 27)        # AI accent
RED = (224, 60, 49)            # problem accent
TEXT_DARK = (20, 28, 45)
TEXT_MUTED = (96, 110, 130)
WHITE = (255, 255, 255)
HAIRLINE = (220, 226, 236)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "seguisb.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = " ".join(cur + [w])
        if draw.textlength(trial, font=font) <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_text_block(draw, x, y, max_w, text, font, fill, line_gap=6):
    lines = _wrap(draw, text, font, max_w)
    line_h = font.size + line_gap
    for i, ln in enumerate(lines):
        draw.text((x, y + i * line_h), ln, font=font, fill=fill)
    return y + len(lines) * line_h


def _rounded_panel(draw, box, fill, radius=18, shadow=None):
    x1, y1, x2, y2 = box
    if shadow is not None:
        draw.rounded_rectangle((x1 + 4, y1 + 6, x2 + 4, y2 + 6), radius=radius, fill=shadow)
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def _accent_bar(draw, box, color, radius=18):
    x1, y1, x2, y2 = box
    # left accent stripe inside a clipped rounded rect
    draw.rounded_rectangle((x1, y1, x1 + 10, y2), radius=radius, fill=color)
    draw.rectangle((x1 + 8, y1, x1 + 12, y2), fill=color)


def build():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Background gradient (navy -> deep)
    for y in range(H):
        t = y / H
        r = int(NAVY[0] * (1 - t) + DEEP[0] * t)
        g = int(NAVY[1] * (1 - t) + DEEP[1] * t)
        b = int(NAVY[2] * (1 - t) + DEEP[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Top accent bar
    draw.rectangle((0, 0, W, 8), fill=CISCO_BLUE)

    # --- Header -------------------------------------------------------------
    f_eyebrow = _font(22, bold=True)
    f_title = _font(58, bold=True)
    f_sub = _font(26)
    draw.text((80, 48), "CISCO IOS-XE  ·  PROGRAMMABILITY ENABLEMENT", font=f_eyebrow, fill=CISCO_BLUE)
    draw.text((80, 84), "From 1,000+ YANG Models to a Self-Service Documentation Hub", font=f_title, fill=WHITE)

    # URL pill (top-right, compact so it never overlaps the title)
    f_url_lbl = _font(13, bold=True)
    f_url = _font(20, bold=True)
    url_text = "cs.co/xeswagger"
    url_lbl = "VISIT THE HUB"
    pad_h, pad_v = 18, 10
    url_w = draw.textlength(url_text, font=f_url)
    lbl_w = draw.textlength(url_lbl, font=f_url_lbl)
    pill_w = int(max(url_w, lbl_w)) + pad_h * 2
    pill_h = f_url.size + f_url_lbl.size + pad_v * 2 + 2
    pill_x2 = W - 80
    pill_x1 = pill_x2 - pill_w
    pill_y1 = 40
    pill_y2 = pill_y1 + pill_h
    draw.rounded_rectangle((pill_x1, pill_y1, pill_x2, pill_y2), radius=10, fill=CISCO_BLUE)
    draw.text(
        (pill_x1 + (pill_w - lbl_w) // 2, pill_y1 + pad_v),
        url_lbl,
        font=f_url_lbl,
        fill=NAVY,
    )
    draw.text(
        (pill_x1 + (pill_w - url_w) // 2, pill_y1 + pad_v + f_url_lbl.size + 2),
        url_text,
        font=f_url,
        fill=WHITE,
    )
    draw.text(
        (80, 162),
        "A static, AI-assisted portal that turns raw YANG / NETCONF artifacts into searchable OpenAPI,",
        font=f_sub,
        fill=(210, 224, 240),
    )
    draw.text(
        (80, 196),
        "telemetry recipes, code samples, and per-platform coverage — across every supported IOS-XE release.",
        font=f_sub,
        fill=(210, 224, 240),
    )

    # --- KPI strip ----------------------------------------------------------
    kpis = [
        ("739", "OpenAPI specs"),
        ("42,557", "REST paths"),
        ("85,481", "Operations"),
        ("1,196", "YANG + MIB modules"),
        ("5", "IOS-XE releases"),
        ("9", "Model categories"),
    ]
    kpi_y = 252
    kpi_h = 96
    pad_x = 80
    gap = 18
    total_w = W - pad_x * 2
    cell_w = (total_w - gap * (len(kpis) - 1)) // len(kpis)
    f_kpi_num = _font(36, bold=True)
    f_kpi_lbl = _font(18)
    for i, (num, lbl) in enumerate(kpis):
        x1 = pad_x + i * (cell_w + gap)
        x2 = x1 + cell_w
        draw.rounded_rectangle((x1, kpi_y, x2, kpi_y + kpi_h), radius=14, fill=(255, 255, 255, 255), outline=None)
        # white pill
        draw.rounded_rectangle((x1, kpi_y, x2, kpi_y + kpi_h), radius=14, fill=WHITE)
        nw = draw.textlength(num, font=f_kpi_num)
        draw.text((x1 + (cell_w - nw) // 2, kpi_y + 14), num, font=f_kpi_num, fill=CISCO_BLUE_DK)
        lw = draw.textlength(lbl, font=f_kpi_lbl)
        draw.text((x1 + (cell_w - lw) // 2, kpi_y + 60), lbl, font=f_kpi_lbl, fill=TEXT_MUTED)

    # --- Four story cards ---------------------------------------------------
    cards = [
        {
            "accent": RED,
            "tag": "THE PROBLEM",
            "title": "YANG sprawl was blocking adoption",
            "body": (
                "Network engineers had to read 1,000+ YANG modules across 5 IOS-XE releases just to find a "
                "single RESTCONF path or telemetry xpath. Coverage gaps, version drift, and platform support "
                "were tribal knowledge — slowing automation projects and DevNet onboarding."
            ),
            "bullets": [
                "No single place to search every model, path, or operation",
                "Telemetry xpaths derived by hand from prefix maps",
                "Platform-by-platform support unclear per release",
            ],
        },
        {
            "accent": ORANGE,
            "tag": "HOW AI / LLM WAS USED",
            "title": "LLM-driven generation, audit, and UX",
            "body": (
                "An LLM coding agent (GitHub Copilot in agent mode) drove the build: writing the Python "
                "generators that convert YANG -> OpenAPI 3.0, scaffolding the vanilla-JS hub, authoring "
                "the accountability / coverage reports, and continuously auditing the surface for drift."
            ),
            "bullets": [
                "Generated 739 specs + 9 Swagger UI viewers from raw YANG",
                "Authored deep-link, search, code-gen, and telemetry tooling",
                "Self-checked accountability: 100% module coverage per release",
            ],
        },
        {
            "accent": TEAL,
            "tag": "BUSINESS / TEAM IMPACT",
            "title": "Minutes, not weeks, to first API call",
            "body": (
                "A static, GitHub-Pages-hosted hub (no backend, no infra cost) lets any Cisco engineer, "
                "partner, or customer browse, search, and copy ready-to-run RESTCONF / NETCONF / MDT "
                "recipes for the exact release and platform they run."
            ),
            "bullets": [
                "Universal fuzzy search across modules, paths, operations",
                "1-click curl / Python / Ansible / JavaScript snippets",
                "Per-release Postman + Bruno exports, Offline PWA shell",
                "Cross-version diffs surface what changed between releases",
            ],
        },
        {
            "accent": CISCO_BLUE,
            "tag": "FOR A CISCO AUDIENCE",
            "title": "DevNet-ready, release-aware, zero ops",
            "body": (
                "Aligns with Cisco programmability strategy: standardizes on YANG + OpenAPI, plays cleanly "
                "with Catalyst Center, Crosswork, and pyATS workflows, and scales to every new IOS-XE "
                "train through a fully automated build pipeline."
            ),
            "bullets": [
                "Single source of truth for 26.1.1, 17.18.1, 17.15.x, 17.12.x, 17.9.x",
                "Direct fit for DevNet, TAC enablement, and SE pre-sales demos",
                "Built entirely with open tooling — easy to fork & extend",
            ],
        },
    ]

    card_y = 388
    card_h = 600
    cards_pad_x = 80
    cards_gap = 22
    cards_total_w = W - cards_pad_x * 2
    cw = (cards_total_w - cards_gap * (len(cards) - 1)) // len(cards)

    f_tag = _font(16, bold=True)
    f_cardtitle = _font(24, bold=True)
    f_body = _font(17)
    f_bullet = _font(16)

    for i, c in enumerate(cards):
        x1 = cards_pad_x + i * (cw + cards_gap)
        x2 = x1 + cw
        box = (x1, card_y, x2, card_y + card_h)
        _rounded_panel(draw, box, CARD, radius=18, shadow=CARD_SHADOW)
        _accent_bar(draw, box, c["accent"], radius=18)

        inner_x = x1 + 28
        inner_w = cw - 56
        y = card_y + 26
        draw.text((inner_x, y), c["tag"], font=f_tag, fill=c["accent"])
        y += 28
        y = _draw_text_block(draw, inner_x, y, inner_w, c["title"], f_cardtitle, TEXT_DARK, line_gap=4)
        y += 14
        # divider
        draw.line((inner_x, y, inner_x + inner_w, y), fill=HAIRLINE, width=1)
        y += 14
        y = _draw_text_block(draw, inner_x, y, inner_w, c["body"], f_body, TEXT_DARK, line_gap=6)
        y += 12
        for b in c["bullets"]:
            # bullet dot
            draw.ellipse((inner_x, y + 7, inner_x + 7, y + 14), fill=c["accent"])
            y = _draw_text_block(
                draw, inner_x + 16, y, inner_w - 16, b, f_bullet, (60, 72, 92), line_gap=4
            )
            y += 6

    # --- Footer -------------------------------------------------------------
    footer_y = H - 56
    draw.line((80, footer_y - 14, W - 80, footer_y - 14), fill=(255, 255, 255, 40), width=1)
    f_foot = _font(16)
    f_foot_b = _font(16, bold=True)
    draw.text((80, footer_y), "Cisco IOS-XE YANG Documentation Hub", font=f_foot_b, fill=WHITE)
    draw.text(
        (80, footer_y + 22),
        "Static GitHub Pages site  ·  vanilla JS + Swagger UI + Chart.js  ·  built and maintained with an LLM coding agent",
        font=f_foot,
        fill=(190, 205, 225),
    )
    tag = "Executive Summary  ·  2026.06  ·  http://cs.co/xeswagger"
    tw = draw.textlength(tag, font=f_foot)
    draw.text((W - 80 - tw, footer_y + 11), tag, font=f_foot, fill=(190, 205, 225))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    size = OUT.stat().st_size
    print(f"Wrote {OUT} ({W}x{H}, {size/1024:.1f} KB)")


if __name__ == "__main__":
    build()
