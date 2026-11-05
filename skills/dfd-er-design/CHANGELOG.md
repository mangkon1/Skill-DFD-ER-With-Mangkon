# Changelog
## 2026-11-05 (3.4)
- Level 1 default (store_mode single) is now compact: all stores in ONE column right next to the processes; flows from
  other processes enter the store's TOP or BOTTOM edge through nested right rails (store box lengthened to its last rail);
  entity flows to later processes leave the entity's left edge into left rails. Same minimum copies, 0 crossings, no jumps.
  booking 23.2 x 17.9 in -> 11.3 x 16.9 in; v3.3 layout kept as "store_mode": "columns"
- New worked example + test examples/library (library system, 3 entities, 5 stores, 7 processes): 11.9 x 14.7 in,
  7 store boxes (D2, D4 copied once), entities once, 0 crossings
- check_vsdx.py prints drawing size and empty-area ratio; WARN when a DFD with stores is wider than 1.7 x height or 16 in,
  or more than 60% empty
- templates/generator/test_examples.py: builds booking + library, requires finalize 0, check_vsdx OK, entities once,
  <= 1 copy per store, width <= 1.7 x height
## 2026-11-05 (3.3)
- Smaller arrowheads by default in every DFD (Visio Begin/EndArrowSize 0, PNG 0.075 x 0.06 in); spec key "arrow": "legacy"
  keeps the old size (examples/spare_part.json uses it, so the submitted report figures still reproduce byte-identical)
- Level 1 default (store_mode single): entities drawn ONCE on the left, staggered, nested L-shaped lanes; an entity gets one
  copy only when its process set interlaces another's (last resort, searched automatically); port order inside a process
  fixed so lanes never cross (lanes from above first, inner entity on top)
- Includes the 3.2 work below (no crossings / no line jumps, planar stores with minimum copies, stricter check_vsdx)
- column-rails stays available as an option but is not the default (it duplicates entities)
## 2026-11-05 (3.2)
- Hard rule: no crossing lines and no line jumps in any diagram; detour around instead. build.py fails on any cross; hop
  drawing removed (PNG) and Visio LineJumpCode is always 0
- d_l1s.py rewritten as a planar layout: store blocks nested by process span (wider blocks in further columns, lines detour
  around inner blocks), exhaustive search for the fewest store copies (max 1 per store) with zero crossings; booking: 8 boxes
  (D2, D3, D5 copied once; proven minimum for one process column), 0 crossings
- New Level 1 layout "column-rails" (d_l1r.py, instructor reference style, A4 portrait): entity/store boxes beside the
  processes, long flows in nested parallel side rails, copies merged greedily while planar and page width <= max_width
  (6.0 in); booking: 5.85 x 12.31 in, 8 store boxes, 8 entity boxes, 13 rail lines, 0 crossings. Shape options iw (store id
  column) and hh (process number band) added with the old defaults (legacy output byte-identical)
- check_vsdx.py FAILS on any two connectors whose segments intersect/touch, any connector through a shape, and any connector
  through another connector's label; prints crossings=N per page
## 2026-11-05 (3.1)
- Hard rule: every flow has both ends glued to a connection point on a shape edge. The generator raises an error on any end
  off a shape edge; the Context builder grows the system box so every arrow starts/ends on it (fixes floating arrows)
- check_vsdx.py now FAILS on loose arrow shapes, unglued connector ends, missing/off-edge connection points and ends not on
  the glued shape's boundary (--tol), and on a store/entity drawn more than twice or a copy without the duplicate mark;
  WARNs with the duplicate count (--max-copies 0 for the older per-process templates)
- New Level 1 store_mode "single" (default for new specs, d_l1s.py): each store drawn once, every process routes its own
  orthogonal line to it, channel order optimised for fewest crossings, at most one justified duplicate per store
  ("duplicates": auto/none/explicit), remaining crossings drawn as line jumps (PNG + Visio)
- Thai text: Pillow without libraqm no longer garbles tone marks (built-in mark placement + warning; DFDER_NO_RAQM=1 to test)
- check_spec.py warns about the per-process layout and validates "duplicates"; build.py skips sections missing from the spec
- Docs: Thai text rule, glue rule, single-store rules, "mistakes from AI tests" (checklist E); worked example examples/booking
## 2026-11-04 (3.0)
- The skill is now the user's global working rules: the description says it MUST be loaded first in every task of any kind
- SKILL.md restructured: Part 1 global rules (Thai replies, back up before replacing, never overwrite user edits, ~$ lock files, verify, reuse-first, safety) + Step 0 toolchain check; Part 2 DFD/ER scoped to diagram/database/report work
- Added docs/toolchain.md (Ponytail, Graphify, Anthropic document-skills, OmniRoute warning) summarised from https://aismartworkth.com/guide/claude-code-first-3 with official links; no third-party source vendored
- Added templates/bootstrap: CLAUDE.md, AGENTS.md, Cursor rule (.mdc, alwaysApply), Cursor User Rule text, install.ps1, install.sh (global install, idempotent bootstrap, backups)
## 2026-11-02 (2.0)
- Fixed the Visio templates: process/store/entity boxes are hollow (NoFill) and every group uses DisplayMode 1, so no white box hides text or lines; ER table headers are filled light blue (#BDD7EE) in both .vsdx and .png
- Added the JSON-driven generator (Context, DFD Level 1, Level 2, ER) that reproduces the templates byte for byte, with test_reproduce.py
- Added docs: principles, dfd-style, er-style, report-insertion, checklist (exact sizes, fonts, lines, captions, page numbers, lessons learned)
- Added Data Dictionary docx template + generator, MariaDB DDL generator and example, check_spec.py (CRUD matrix, balancing) and check_vsdx.py
- Moved templates to templates/vsdx and templates/png; style-reference images replaced by the corrected PNGs
- Updated references/chapter3_example.docx with the corrected diagrams
## 2026-11-01
- Initial skill creation based on research document rules for DFD/ER design
- Principles: data must have origin and destination, balanced input/output, Visio-only, no intersecting lines
- Updated Visio templates with user-corrected versions (proper fonts, colors, labels, table headers)
- Align SKILL.md frontmatter with the Agent Skills standard so the same URL installs on every supported agent
