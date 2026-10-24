"""Run every dithering algorithm on one image; print runtime and error, save results.

Usage::

    python examples/demo.py [path/to/image.jpg] [--size 160] [--colours 8]

Without an image path a procedural test picture (sunset gradient, sun, hills,
colour ramps) is generated, so the demo runs anywhere. Results are written to
``examples/output/`` together with a contact sheet ``overview.png``.
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import numpy as np
from PIL import Image, ImageDraw

import hitherdither
from hitherdither.palette import Palette

HERE = os.path.dirname(os.path.abspath(__file__))


def make_test_image(w, h):
    """A picture with smooth gradients, hard edges and a grey ramp."""
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    sky = np.stack(
        [255 * (0.25 + 0.75 * y) + 0 * x, 255 * (0.1 + 0.5 * y ** 2) + 0 * x, 255 * (0.5 - 0.35 * y) + 0 * x],
        axis=2,
    )
    img = Image.fromarray(np.clip(sky, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.55, h * 0.30, w * 0.80, h * 0.30 + w * 0.25], fill=(255, 235, 150))
    d.polygon([(0, h * 0.75), (w * 0.3, h * 0.55), (w * 0.6, h * 0.78), (w * 0.85, h * 0.6), (w, h * 0.72), (w, h), (0, h)], fill=(40, 70, 60))
    ramp = np.tile(np.linspace(0, 255, w, dtype="uint8"), (max(h // 10, 4), 1))
    img.paste(Image.fromarray(ramp).convert("RGB"), (0, h - ramp.shape[0]))
    return img


def mean_abs_error(a, b):
    """Mean absolute RGB difference of a blurred version of each, i.e. how close the
    dithered image looks from a distance (0 = identical)."""
    from PIL import ImageFilter

    ra = np.asarray(a.convert("RGB").filter(ImageFilter.GaussianBlur(2)), "float")
    rb = np.asarray(b.convert("RGB").filter(ImageFilter.GaussianBlur(2)), "float")
    return float(np.abs(ra - rb).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?")
    ap.add_argument("--size", type=int, default=160, help="max side in pixels (error diffusion/Yliluoma are slow)")
    ap.add_argument("--colours", type=int, default=8)
    args = ap.parse_args()

    if args.image:
        img = Image.open(args.image).convert("RGB")
        img.thumbnail((args.size, args.size))
    else:
        img = make_test_image(args.size, int(args.size * 0.7))
    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "original.png"))

    palette = Palette.create_by_median_cut(img, n=args.colours)
    print("Image %dx%d, palette of %d colours (median cut)" % (img.width, img.height, len(palette)))

    t = np.array([256 / 4] * 3)
    runs = [
        ("bayer-8", lambda: hitherdither.ordered.bayer.bayer_dithering(img, palette, t, order=8)),
        ("bayer-4", lambda: hitherdither.ordered.bayer.bayer_dithering(img, palette, t, order=4)),
        ("cluster-dot-8", lambda: hitherdither.ordered.cluster.cluster_dot_dithering(img, palette, t, order=8)),
        ("yliluoma-1-8", lambda: hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(img, palette, order=8)),
    ]
    for m in ("floyd-steinberg", "atkinson", "jarvis-judice-ninke", "stucki", "burkes", "sierra3", "sierra2", "sierra-2-4a", "stevenson-arce"):
        runs.append((m, lambda m=m: hitherdither.diffusion.error_diffusion_dithering(img, palette, m)))
    # baseline: nearest colour without dithering
    runs.insert(0, ("no-dither", lambda: palette.create_PIL_png_from_rgb_array(np.array(img))))

    rows = []
    results = [("original", img)]
    for name, fn in runs:
        t0 = time.perf_counter()
        try:
            res = fn()
        except Exception as e:  # report failures instead of hiding them
            rows.append((name, None, "FAILED: %s: %s" % (type(e).__name__, e)))
            continue
        dt = time.perf_counter() - t0
        res.convert("RGB").save(os.path.join(out_dir, name + ".png"))
        used = len(np.unique(np.asarray(res)))
        rows.append((name, dt, "blurred MAE %.2f, %d colours used" % (mean_abs_error(img, res), used)))
        results.append((name, res.convert("RGB")))

    print("\n%-22s %9s  %s" % ("algorithm", "time (s)", "quality (lower MAE = closer to original)"))
    for name, dt, info in rows:
        print("%-22s %9s  %s" % (name, "-" if dt is None else "%.3f" % dt, info))

    # contact sheet
    cols = 4
    w, h = img.size
    n = len(results)
    sheet = Image.new("RGB", (cols * (w + 8) + 8, ((n + cols - 1) // cols) * (h + 24) + 8), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(results):
        cx, cy = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 24)
        sheet.paste(im, (cx, cy + 14))
        d.text((cx, cy), name, fill=(230, 230, 230))
    sheet.save(os.path.join(out_dir, "overview.png"))
    print("\nSaved images and overview.png in", out_dir)


if __name__ == "__main__":
    main()
