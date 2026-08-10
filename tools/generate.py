#!/usr/bin/env python3
"""Generate the course Gantt pages from a semester config.

Usage:
    python3 tools/generate.py semesters/fa2026.json [--current]

Writes  <semester>/modules-gantt.html  and  <semester>/detailed-gantt.html.
With --current, also copies the pages into  current/  (the stable path that
Canvas iframes point at, so Canvas never needs relinking between semesters).

No dependencies beyond the Python standard library.
"""
import json
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Visual design tokens (light surface — Canvas pages are light).
# Series color: one blue, two steps (dark = HW deliverable, light = reflection).
# Neutral gray = breaks/holidays (not a data series). Gold = today marker.
# ---------------------------------------------------------------------------
INK = "#0b0b0b"          # primary text
INK_2 = "#52514e"        # secondary text
MUTED = "#898781"        # axis labels
GRID = "#e1e0d9"         # hairline gridlines
BLUE = "#2a78d6"         # module bars + HW milestones
BLUE_DK = "#1c5cab"      # borders
BLUE_LT = "#86b6ef"      # reflection milestones (light step, ordinal pair)
GRAY_BAR = "#e1e0d9"     # break bars / no-class bands
GRAY_BRD = "#c3c2b7"
GOLD = "#eda100"         # today marker

INIT = ('%%{init: ' + json.dumps({
    "theme": "base",
    "themeVariables": {
        "fontFamily": "system-ui, sans-serif",
        "textColor": INK_2,
        "taskBkgColor": BLUE,
        "taskBorderColor": BLUE_DK,
        "taskTextColor": "#ffffff",
        "taskTextOutsideColor": INK,
        "activeTaskBkgColor": BLUE_LT,
        "activeTaskBorderColor": BLUE_DK,
        "doneTaskBkgColor": GRAY_BAR,
        "doneTaskBorderColor": GRAY_BRD,
        "sectionBkgColor": "rgba(137,135,129,0.07)",
        "altSectionBkgColor": "transparent",
        "gridColor": GRID,
        "todayLineColor": GOLD
    },
    "gantt": {
        "fontSize": 12,
        "sectionFontSize": 12,
        "barHeight": 22,
        "barGap": 6,
        "topPadding": 42,
        "leftPadding": 118
    }
}) + '}%%')

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{
    margin: 0; background: #ffffff;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: {ink};
  }}
  .wrap {{ padding: 8px 12px 10px; }}
  header {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; margin: 2px 2px 0; }}
  header h1 {{ font-size: 14px; font-weight: 650; margin: 0; }}
  header .sub {{ font-size: 12px; color: {ink2}; }}
  .mermaid {{ width: 100%; font-family: system-ui, sans-serif; }}
  /* Recessive chrome: hairline grid, muted axis text (overrides Mermaid defaults) */
  .mermaid svg .grid .tick line {{ stroke: {grid}; stroke-width: 1; }}
  .mermaid svg .grid .tick text {{ fill: {muted}; }}
  .mermaid svg .sectionTitle {{ fill: {ink2}; }}
  footer {{ display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
           margin: 2px 2px 0; font-size: 11.5px; color: {ink2}; }}
  .chip {{ display: inline-flex; align-items: center; gap: 5px; }}
  .sw {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; }}
  .sw.bar {{ background: {blue}; }}
  .sw.hw {{ background: {blue}; transform: rotate(45deg); width: 8px; height: 8px; }}
  .sw.refl {{ background: {blue_lt}; border: 1px solid {blue_dk}; transform: rotate(45deg); width: 8px; height: 8px; }}
  .sw.brk {{ background: {gray}; border: 1px solid {gray_brd}; }}
  .sw.today {{ background: {gold}; width: 3px; height: 12px; border-radius: 1px; }}
  .note {{ color: {muted}; }}
</style>
</head>
<body>
<div class="wrap">
<header><h1>{heading}</h1><span class="sub">{subtitle}</span></header>
<pre class="mermaid">
{diagram}
</pre>
<footer>
{legend}
<span class="note">{caption}</span>
</footer>
</div>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({{ startOnLoad: true, gantt: {{ useWidth: document.querySelector(".wrap").clientWidth - 8 }} }});
</script>
</body>
</html>
"""

LEGEND_MODULES = (
    '<span class="chip"><span class="sw bar"></span>Module</span>'
    '<span class="chip"><span class="sw brk"></span>No classes</span>'
    '<span class="chip"><span class="sw today"></span>Today</span>'
)
LEGEND_DETAILED = (
    '<span class="chip"><span class="sw bar"></span>Module</span>'
    '<span class="chip"><span class="sw hw"></span>HW due</span>'
    '<span class="chip"><span class="sw refl"></span>Reflection due</span>'
    '<span class="chip"><span class="sw brk"></span>No classes</span>'
    '<span class="chip"><span class="sw today"></span>Today</span>'
)


def header_lines(cfg):
    lines = [
        INIT,
        "gantt",
        "    dateFormat YYYY-MM-DD",
        "    axisFormat %b %e",
        "    tickInterval 1week",
        "    weekday monday",
        "    todayMarker stroke-width:4px,stroke:" + GOLD + ",opacity:0.45",
    ]
    dates = [h["date"] for h in cfg.get("no_class", [])]
    if dates:
        lines.insert(3, "    excludes " + ", ".join(dates))
    return lines


def task_line(m):
    if m["start"] == m["end"]:  # single-day module (e.g. Welcome) reads better as a milestone
        return f"    {m['name']} : milestone, {m['id']}, {m['start']}, 0d"
    tag = "done, " if m.get("break") else ""
    return f"    {m['name']} : {tag}{m['id']}, {m['start']}, {m['end']}"


def milestone_line(ms):
    tag = "active, " if ms.get("kind") == "reflection" else ""
    return f"    {ms['name']} : {tag}milestone, {ms['date']}, 0d"


def modules_gantt(cfg):
    lines = header_lines(cfg)
    lines.append("    section Modules")
    for m in cfg["modules"]:
        lines.append(task_line(m))
    return "\n".join(lines)


def detailed_gantt(cfg):
    lines = header_lines(cfg)
    for m in cfg["modules"]:
        lines.append(f"    section {m['name']}")
        lines.append(task_line(m))
        for ms in cfg["milestones"]:
            if ms["module"] == m["id"]:
                lines.append(milestone_line(ms))
    return "\n".join(lines)


def render(cfg, heading, diagram, legend):
    return PAGE.format(
        title=heading,
        heading=heading,
        subtitle=cfg.get("subtitle", ""),
        diagram=diagram,
        legend=legend,
        caption=cfg.get("no_class_caption", ""),
        ink=INK, ink2=INK_2, muted=MUTED, grid=GRID, blue=BLUE, blue_dk=BLUE_DK,
        blue_lt=BLUE_LT, gray=GRAY_BAR, gray_brd=GRAY_BRD, gold=GOLD,
    )


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cfg_path = Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.resolve().parent.parent
    outdir = root / cfg["semester"]
    outdir.mkdir(exist_ok=True)

    pages = {
        "modules-gantt.html": render(cfg, cfg["title"], modules_gantt(cfg), LEGEND_MODULES),
        "detailed-gantt.html": render(cfg, cfg["title"] + " — deliverables", detailed_gantt(cfg), LEGEND_DETAILED),
    }
    for name, content in pages.items():
        (outdir / name).write_text(content)
        print(f"wrote {outdir / name}")

    if "--current" in sys.argv:
        cur = root / "current"
        cur.mkdir(exist_ok=True)
        for name in pages:
            shutil.copy2(outdir / name, cur / name)
            print(f"wrote {cur / name}")


if __name__ == "__main__":
    main()
