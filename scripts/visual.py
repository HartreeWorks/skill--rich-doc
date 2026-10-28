#!/usr/bin/env python3
"""Screenshots and SVG rendering for rich docs, via headless Chrome.

  visual.py shot <url> <out.png> [--width W] [--height H] [--crop x,y,w,h] [--scale S]
  visual.py svg <in.svg> [--scale S]          writes <in>.png beside the SVG

Crop coordinates are in CSS pixels; they are multiplied by --scale.
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import tempfile

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def capture(url, out, width, height, scale):
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--force-device-scale-factor={scale}", f"--window-size={width},{height}",
         "--virtual-time-budget=6000", f"--screenshot={out}", url],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def crop(path, box, scale):
    from PIL import Image
    x, y, w, h = (int(v) * scale for v in box.split(","))
    with Image.open(path) as im:
        im.crop((x, y, x + w, y + h)).save(path)


def svg_size(path):
    text = pathlib.Path(path).read_text()
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', text)
    if not m:
        sys.exit("SVG needs a viewBox")
    return int(float(m.group(1))), int(float(m.group(2)))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shot")
    s.add_argument("url")
    s.add_argument("out")
    s.add_argument("--width", type=int, default=1280)
    s.add_argument("--height", type=int, default=1100)
    s.add_argument("--crop")
    s.add_argument("--scale", type=int, default=1)
    v = sub.add_parser("svg")
    v.add_argument("svg")
    v.add_argument("--scale", type=int, default=2)
    a = p.parse_args()

    if a.cmd == "shot":
        out = str(pathlib.Path(a.out).resolve())
        capture(a.url, out, a.width, a.height, a.scale)
        if a.crop:
            crop(out, a.crop, a.scale)
        print(out)
    else:
        src = pathlib.Path(a.svg).resolve()
        w, h = svg_size(src)
        out = src.with_suffix(".png")
        # Wrap the SVG in a zero-margin page so the screenshot is exactly the drawing.
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as page:
            page.write(f'<html><body style="margin:0"><img src="{src.as_uri()}" width="{w}" height="{h}"></body></html>')
        capture(pathlib.Path(page.name).as_uri(), str(out), w, h, a.scale)
        pathlib.Path(page.name).unlink()
        print(out)


if __name__ == "__main__":
    main()
