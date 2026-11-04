# Changelog
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
