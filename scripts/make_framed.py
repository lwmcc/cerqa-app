#!/usr/bin/env python3
"""Puts app screenshots in simple device frames.

  make_framed.py phone <screenshot.png> <ios|android> <out.webp>
      one framed phone on a transparent background, 560 px wide (home page 1.19 section)
  make_framed.py hero <ios.png> <android.png> <out.jpg> [title]
      1200x630 blog hero: iPhone and Android side by side on the Cerqa navy, optional title on the left

Screenshots should be full-screen captures (iPhone 1320x2868, Android 1080x2340 or similar).
"""
import sys

from PIL import Image, ImageDraw, ImageFont

NAVY = (27, 45, 74)
BEZEL = (16, 21, 29)
EDGE = (58, 66, 80)


def frame(shot_path, kind, width, pad_frac=None, aspect=None):
    shot = Image.open(shot_path).convert("RGB")
    if aspect:  # crop from the top so different phones end up the same height
        shot = shot.crop((0, 0, shot.width, min(shot.height, round(shot.width * aspect))))
    pad = round(width * (pad_frac or (0.04 if kind == "ios" else 0.032)))
    inner_w = width - 2 * pad
    inner_h = round(shot.height * inner_w / shot.width)
    shot = shot.resize((inner_w, inner_h), Image.LANCZOS)
    h = inner_h + 2 * pad
    outer_r = round(width * (0.18 if kind == "ios" else 0.13))
    inner_r = outer_r - pad
    scale = 3  # draw shapes big, then shrink, for smooth edges
    W, H = width * scale, h * scale
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, W - 1, H - 1), outer_r * scale, fill=EDGE)
    e = 2 * scale
    d.rounded_rectangle((e, e, W - 1 - e, H - 1 - e), outer_r * scale - e, fill=BEZEL)
    body = body.resize((width, h), Image.LANCZOS)
    mask = Image.new("L", (inner_w * scale, inner_h * scale), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, inner_w * scale - 1, inner_h * scale - 1), inner_r * scale, fill=255)
    mask = mask.resize((inner_w, inner_h), Image.LANCZOS)
    body.paste(shot, (pad, pad), mask)
    d = ImageDraw.Draw(body)
    top = pad + round(inner_w * 0.03)
    if kind == "ios":  # Dynamic Island
        iw, ih = round(inner_w * 0.29), round(inner_w * 0.085)
        d.rounded_rectangle(((width - iw) // 2, top, (width + iw) // 2, top + ih), ih // 2, fill=(0, 0, 0))
    else:  # punch-hole camera
        r = round(inner_w * 0.022)
        d.ellipse((width // 2 - r, top, width // 2 + r, top + 2 * r), fill=(0, 0, 0))
    return body


def font(size, bold=True):
    for path in ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            f = ImageFont.truetype(path, size)
            if bold and path.endswith("SFNS.ttf"):
                f.set_variation_by_name("Bold")
            return f
        except Exception:
            continue
    return ImageFont.load_default()


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def hero(ios, android, out, title=None):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    for y in range(H):  # soft vertical gradient
        c = tuple(round(a + (b - a) * y / H) for a, b in zip(NAVY, (44, 72, 116)))
        d.line([(0, y), (W, y)], fill=c)
    phone_w = 300
    # same bezel and same screen shape, so the two phones match exactly
    a = frame(ios, "ios", phone_w, pad_frac=0.036, aspect=2868 / 1320)
    b = frame(android, "android", phone_w, pad_frac=0.036, aspect=2868 / 1320)
    if title:
        x0 = W - 2 * phone_w - 90
        f = font(50)
        lines = wrap(d, title, f, x0 - 110)
        y = (H - len(lines) * 62) // 2 - 10
        for line in lines:
            d.text((64, y), line, font=f, fill=(255, 255, 255))
            y += 62
        d.text((64, y + 16), "cerqa.app", font=font(26, bold=False), fill=(170, 190, 220))
    else:
        x0 = (W - 2 * phone_w - 40) // 2
    # phones side by side at the same height, bleeding off the bottom
    img.paste(a, (x0, 56), a)
    img.paste(b, (x0 + phone_w + 40, 56), b)
    img.save(out, quality=88)
    print("wrote", out)


if __name__ == "__main__":
    if sys.argv[1] == "phone":
        frame(sys.argv[2], sys.argv[3], 560).save(sys.argv[4], quality=88)
        print("wrote", sys.argv[4])
    else:
        hero(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
