# gamedev-course-site

Static support site for **CMSC 445 / COAR 463 — Intro to Game Development** (VCU).
It serves the live Gantt charts that the Canvas weekly front pages embed via iframe,
replacing the previous instructor's `lowkeylabs/gamedev-course-admin` repo with one you own.

```
semesters/fa2026.json     ← the ONLY file you edit each year (dates + deliverables)
tools/generate.py         ← regenerates the HTML pages from the config (stdlib only)
fa2026/                   ← generated pages for Fall 2026 (kept as archive later)
current/                  ← copies of the active semester's pages — Canvas points HERE
index.html                ← landing page listing semesters
```

## One-time setup (about 10 minutes)

1. Create a **public** repo under your GitHub account (e.g. `kdamevski/gamedev-course-site`)
   and push these files to the `main` branch. It must be public — Canvas iframes need
   publicly reachable URLs, so GitHub Enterprise / private Pages won't work.
2. In the repo: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`**.
3. After a minute the site is live at
   `https://<your-username>.github.io/gamedev-course-site/`.
4. In Canvas, update the iframe embeds to the **stable** path:

   ```html
   <iframe width="100%" height="300" loading="lazy"
     src="https://<your-username>.github.io/gamedev-course-site/current/modules-gantt.html"></iframe>
   ```

   Point Canvas at `current/…`, never at `fa2026/…` — that way the Canvas pages
   never need relinking again. (In the Fall 2025 export there are ~20 pages
   embedding `modules-gantt.html` and 2 embedding `detailed-gantt.html`; a
   find-and-replace of the old `lowkeylabs.github.io/gamedev-course-admin/fa2025`
   prefix during course copy handles all of them.)

## Yearly rollover (about 15 minutes)

1. Copy last year's config: `cp semesters/fa2026.json semesters/fa2027.json`.
2. Edit the new file: bump `"semester"` and `"title"`, then update the dates.
   Tip: if the new fall semester starts exactly 52 weeks later, every date just
   moves back one calendar day, same weekday. Check the
   [VCU academic calendar](https://academiccalendars.vcu.edu/) for the actual
   first day of classes and fall-break week before trusting that shortcut.
3. Regenerate and repoint `current/`:

   ```sh
   python3 tools/generate.py semesters/fa2027.json --current
   ```

4. Commit and push. Canvas updates automatically — no Canvas edits needed.

The previous semester's folder (`fa2026/` etc.) stays in the repo as a permanent archive.

## Fall 2026 schedule mapping (verified against the VCU academic calendar)

Classes begin **Tue Aug 18**; last day of classes **Mon Dec 7**; finals (Monroe Park)
**Dec 8–15**. Deliverable dates are shifted +364 days from Fall 2025 (same weekday),
which lands cleanly on the 2026 calendar.

| Module | Dates |
|---|---|
| Welcome (first day of classes) | Tue Aug 18 |
| Unity Essentials | Aug 18 – Sep 14 |
| Solo project | Sep 14 – Sep 28 |
| Pair project 1 | Sep 28 – Oct 12 |
| Pair project 2 | Oct 12 – Oct 26 |
| Team project | Oct 26 – Dec 7 |
| Fall break | Nov 23 – 29 |
| Finals | Dec 8 – 15 (exam + Showcase milestone set to **Fri Dec 11** — confirm your section's exam slot when published) |

No-class days baked into the charts (gray bands): **Labor Day Mon Sep 7**,
**Reading Day Fri Oct 16**, **Election Day Tue Nov 3**, **fall break Nov 23–29**.

> ⚠️ **Reading Day (Fri Oct 16) falls on a class-meeting day.** With the Friday
> meeting pattern, Fall 2026 has **14 class meetings** (Fall 2025 had 15) — the
> lost meeting lands in the Pair project 2 window, which then has only one
> meeting (Oct 23) between HW5 (Oct 8/9) and HW6 (due Thu Oct 22). Consider
> shifting HW6 to the following week or moving one topic online.

Homework milestones are Thursdays and reflections Fridays, matching the 2025 rhythm.
Adjust any individual date in `semesters/fa2026.json` and re-run the generator.

## Design notes

The pages use a deliberate, minimal visual system: one blue for course content
(dark-blue bars and HW diamonds; light-blue diamonds for reflections — same hue,
two steps, so the distinction survives color-vision deficiencies), neutral gray for
breaks and no-class bands (not a data color), and a single gold vertical line for
"today" (it updates live). Gridlines fall on Mondays (one per week), axis text is
muted, and each page carries its own legend and a no-class caption, so the chart is
readable without any surrounding explanation. All colors and sizes live at the top
of `tools/generate.py` if you want to re-brand.

## Notes

- Pages render with [Mermaid](https://mermaid.js.org/) v11 loaded from the jsDelivr CDN;
  the gold vertical bar is Mermaid's `todayMarker`, so "today" tracks automatically.
- No build system, no dependencies: the generator uses only the Python standard library,
  and you can also hand-edit the Mermaid text inside the generated HTML directly.
