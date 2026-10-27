#!/usr/bin/env python3

# Draws the Scenegen app icon: a fanned stack of numbered OBS scenes, the
# front one showing a slide, on a macOS-style rounded square.
#
# Not needed for 'make install', which uses the committed Scenegen.icns.
# To regenerate (needs Pillow):  python3 macos/make_icon.py macos/Scenegen.icns

# pylint: disable=missing-function-docstring

import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

K = 4                   # supersampling factor; drawn at 4096px, saved at 1024px
SIZE = 1024 * K

FONT_PATHS = ["/System/Library/Fonts/SFNSRounded.ttf",
              "/System/Library/Fonts/SFNS.ttf",
              "/System/Library/Fonts/Helvetica.ttc"]

def s(v):
    return int(v * K)

def font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            f = ImageFont.truetype(path, s(size))
            try:
                f.set_variation_by_name("Bold")
            except (OSError, ValueError):
                pass
            return f
    return ImageFont.load_default()

def gradient(size, top, bottom):
    # Diagonal gradient from top-left to bottom-right
    w, h = size
    small = Image.new("RGB", (256, 256))
    px = small.load()
    for y in range(256):
        for x in range(256):
            t = (x + y) / 510
            px[x, y] = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
    return small.resize((w, h), Image.BICUBIC)

def rounded_mask(size, box, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius, fill=255)
    return mask

def shadow(mask, offset, blur, opacity):
    sh = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    alpha = mask.point(lambda a: a * opacity // 255)
    sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(blur)))
    out = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    out.paste(sh, offset, sh)
    return out

def card(number, front):
    """One scene card, drawn unrotated on its own layer."""
    w, h = s(560), s(380)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, w - 1, h - 1), s(40),
                        fill=(255, 255, 255, 255) if front else (226, 232, 246, 255))

    # The "screen": a dark slide inside the card
    sx0, sy0, sx1, sy1 = s(30), s(30), w - s(30), h - s(30)
    d.rounded_rectangle((sx0, sy0, sx1, sy1), s(22),
                        fill=(24, 30, 62, 255) if front else (150, 162, 196, 255))

    if front:
        # Scene number badge, top-left
        d.rounded_rectangle((s(54), s(54), s(150), s(122)), s(20), fill=(255, 196, 61, 255))
        d.text((s(102), s(89)), str(number), font=font(50), anchor="mm",
               fill=(24, 30, 62, 255))

        # Slide content: a title and a few lines of text
        d.rounded_rectangle((s(180), s(68), s(440), s(104)), s(18), fill=(255, 255, 255, 255))
        for i, length in enumerate((420, 360, 400)):
            y = s(170 + i * 52)
            d.rounded_rectangle((s(64), y, s(64 + length), y + s(24)), s(12),
                                fill=(120, 140, 210, 255))
        # Red "live" dot, top-right
        cx, cy, r = s(476), s(86), s(22)
        halo = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(halo).ellipse((cx - r - s(12), cy - r - s(12), cx + r + s(12), cy + r + s(12)),
                                     fill=(255, 69, 58, 80))
        layer.alpha_composite(halo)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 69, 58, 255))
    return layer

def place(canvas, layer, center, angle):
    pad = s(80)
    padded = Image.new("RGBA", (layer.width + 2 * pad, layer.height + 2 * pad), (0, 0, 0, 0))
    padded.paste(layer, (pad, pad))
    rotated = padded.rotate(angle, resample=Image.BICUBIC, expand=True)
    x = center[0] - rotated.width // 2
    y = center[1] - rotated.height // 2

    sh = shadow(rotated.getchannel("A"), (0, s(18)), s(22), 110)
    canvas.alpha_composite(sh, (x, y))
    canvas.alpha_composite(rotated, (x, y))

def draw():
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    # Rounded-square body per the macOS icon grid: 824px square, 100px margin
    box = (s(100), s(100), s(924), s(924))
    body_mask = rounded_mask(canvas.size, box, s(185))
    canvas.alpha_composite(shadow(body_mask, (0, s(10)), s(18), 120))

    body = gradient(canvas.size, (76, 50, 170), (14, 150, 170)).convert("RGBA")
    # Soft highlight fading down from the top
    glow = Image.linear_gradient("L").resize(canvas.size).point(lambda v: max(0, 50 - v // 3))
    white = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    white.putalpha(glow)
    body.alpha_composite(white)
    canvas.paste(body, (0, 0), body_mask)

    # Fanned stack of scenes, back to front
    place(canvas, card(3, False), (s(552), s(470)), -16)
    place(canvas, card(2, False), (s(532), s(500)), -7)
    place(canvas, card(1, True), (s(504), s(542)), 3)

    # Clip everything to the body so nothing spills past the rounded square
    clipped = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped.paste(canvas, (0, 0), Image.composite(body_mask, Image.new("L", canvas.size, 0),
                                                  body_mask))
    # Keep the outer drop shadow, which lies outside the body
    outer = canvas.copy()
    outer.putalpha(ImageChops.multiply(canvas.getchannel("A"), ImageChops.invert(body_mask)))
    out = Image.alpha_composite(outer, clipped)
    return out.resize((1024, 1024), Image.LANCZOS)

def write_icns(icon, path):
    with tempfile.TemporaryDirectory() as tmp:
        iconset = os.path.join(tmp, "Scenegen.iconset")
        os.mkdir(iconset)
        for size in (16, 32, 128, 256, 512):
            icon.resize((size, size), Image.LANCZOS).save(f"{iconset}/icon_{size}x{size}.png")
            icon.resize((size * 2, size * 2), Image.LANCZOS).save(f"{iconset}/icon_{size}x{size}@2x.png")
        subprocess.run(["iconutil", "-c", "icns", "-o", path, iconset], check=True)

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "Scenegen.icns"
    icon = draw()
    if out.endswith(".png"):
        icon.save(out)
    else:
        write_icns(icon, out)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
