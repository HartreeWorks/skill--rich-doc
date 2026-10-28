#!/usr/bin/env python3
"""Brand palettes for rich docs: find the one that applies to a doc, and apply it.

  brand.py resolve <doc path>                 print the brand in force (JSON) and where it came from
  brand.py mermaid <doc path>                 print a Mermaid init line and classDef lines in that brand
  brand.py svg <doc path> <in.svg> <out.svg>  recolour an SVG drawn in the default palette
  brand.py register <brand.json> <folder>...  use this brand for docs under these folders
  brand.py list                               list registered brands

A brand applies to a doc when a `.rich-doc/brand.json` sits in the doc's folder or
any folder above it (the nearest wins), or when the doc is under a folder registered
with `register`. Otherwise the default palette applies.
"""
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

DEFAULT = {
    "name": "default",
    "palette": {
        "background": "#fafaf8",
        "ink": "#24221f",
        "muted": "#6b6762",
        "border": "#c4c1bb",
        "accent": "#3c6f8b",
        "accent_soft": "#eaf2f6",
        "gap_fill": "#f6d6cf",
        "gap_ink": "#7a2418",
    },
    "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif",
}
ROLES = list(DEFAULT["palette"])


def data_dir():
    script = HERE / "data-dir.sh"
    if script.exists():
        return pathlib.Path(subprocess.run(["bash", str(script)], check=True, capture_output=True, text=True).stdout.strip())
    d = pathlib.Path(os.environ.get("XDG_CONFIG_HOME", pathlib.Path.home() / ".config")) / "hartreeworks-skills" / "rich-doc"
    d.mkdir(parents=True, exist_ok=True)
    return d


def registry_path():
    return data_dir() / "brands.json"


def load_registry():
    p = registry_path()
    return json.loads(p.read_text()) if p.exists() else {"brands": []}


def load_brand(path):
    brand = json.loads(pathlib.Path(path).read_text())
    palette = {**DEFAULT["palette"], **brand.get("palette", {})}
    unknown = set(brand.get("palette", {})) - set(ROLES)
    if unknown:
        sys.exit(f"{path}: unknown palette roles {sorted(unknown)}; use {ROLES}")
    return {"name": brand.get("name", pathlib.Path(path).parent.parent.name), "palette": palette,
            "font": brand.get("font", DEFAULT["font"]), "notes": brand.get("notes", "")}


def resolve(doc):
    doc = pathlib.Path(doc).expanduser().resolve()
    start = doc if doc.is_dir() else doc.parent
    for folder in [start, *start.parents]:
        f = folder / ".rich-doc" / "brand.json"
        if f.exists():
            return {**load_brand(f), "source": str(f)}
    best = None
    for entry in load_registry()["brands"]:
        for root in entry["folders"]:
            r = pathlib.Path(root).expanduser().resolve()
            if start == r or r in start.parents:
                if best is None or len(str(r)) > len(str(best[0])):
                    best = (r, entry["file"])
    if best:
        return {**load_brand(best[1]), "source": f"registered for {best[0]}: {best[1]}"}
    return {**DEFAULT, "notes": "", "source": "default"}


def mermaid(b):
    p = b["palette"]
    init = {"theme": "base", "themeVariables": {
        "fontFamily": b["font"], "background": p["background"],
        "primaryColor": "#ffffff", "primaryBorderColor": p["border"], "primaryTextColor": p["ink"],
        "secondaryColor": p["accent_soft"], "tertiaryColor": p["background"],
        "lineColor": p["ink"], "textColor": p["ink"], "clusterBkg": p["background"], "clusterBorder": p["border"],
        "actorBkg": "#ffffff", "actorBorder": p["border"], "noteBkgColor": p["accent_soft"], "noteBorderColor": p["accent"],
    }}
    return "\n".join([
        f"%%{{init: {json.dumps(init)}}}%%",
        f"classDef plain fill:#ffffff,stroke:{p['border']},color:{p['ink']}",
        f"classDef key fill:#ffffff,stroke:{p['ink']},stroke-width:1.5px,color:{p['ink']}",
        f"classDef new fill:{p['accent_soft']},stroke:{p['accent']},stroke-dasharray:5 3,color:{p['ink']}",
        f"classDef changed fill:{p['accent_soft']},stroke:{p['accent']},stroke-width:1.5px,color:{p['ink']}",
        f"classDef gap fill:{p['gap_fill']},stroke:{p['gap_ink']},color:{p['gap_ink']}",
        f"classDef result fill:{p['ink']},stroke:{p['ink']},color:{p['background']}",
        f"classDef muted fill:{p['background']},stroke:{p['border']},color:{p['muted']}",
    ])


def recolour(b, src, out):
    text = pathlib.Path(src).read_text()
    for role in ROLES:
        text = text.replace(DEFAULT["palette"][role], b["palette"][role])
    text = text.replace("Inter, 'Helvetica Neue', Helvetica, sans-serif", b["font"].replace('"', "'"))
    pathlib.Path(out).write_text(text)
    return out


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd = args[0]
    if cmd == "resolve" and len(args) == 2:
        print(json.dumps(resolve(args[1]), indent=2))
    elif cmd == "mermaid" and len(args) == 2:
        print(mermaid(resolve(args[1])))
    elif cmd == "svg" and len(args) == 4:
        print(recolour(resolve(args[1]), args[2], args[3]))
    elif cmd == "register" and len(args) >= 3:
        f = str(pathlib.Path(args[1]).expanduser().resolve())
        load_brand(f)
        reg = load_registry()
        reg["brands"] = [e for e in reg["brands"] if e["file"] != f]
        reg["brands"].append({"file": f, "folders": [str(pathlib.Path(x).expanduser().resolve()) for x in args[2:]]})
        registry_path().write_text(json.dumps(reg, indent=2) + "\n")
        print(f"registered {f} for {', '.join(args[2:])}")
    elif cmd == "list" and len(args) == 1:
        for e in load_registry()["brands"]:
            print(f"{e['file']}: {', '.join(e['folders'])}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
