# gamedev-course-site

Static support site for **CMSC 445 / COAR 463 — Intro to Game Development** (VCU).

```
semesters/fa2026.json     ← the ONLY file you edit each year (dates + deliverables)
tools/generate.py         ← regenerates the HTML pages from the config 
fa2026/                   ← generated pages for Fall 2026 
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


## Notes

- Pages render with [Mermaid](https://mermaid.js.org/) v11 loaded from the jsDelivr CDN;
  the gold vertical bar is Mermaid's `todayMarker`, so "today" tracks automatically.
- No build system, no dependencies: the generator uses only the Python standard library,
  and you can also hand-edit the Mermaid text inside the generated HTML directly.
