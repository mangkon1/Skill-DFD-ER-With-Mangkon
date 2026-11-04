#!/usr/bin/env bash
# ติดตั้ง skill dfd-er-design แบบ global และเพิ่มคำสั่ง "อ่าน skill นี้ก่อนทุกงาน" ใน CLAUDE.md / AGENTS.md ระดับผู้ใช้
# - สำรองไฟล์เดิมก่อนแก้ทุกครั้ง (skill เดิม -> ~/.dfd-er-design-backup/<เวลา>/, CLAUDE.md/AGENTS.md -> *.bak-<เวลา>)
# - เพิ่มข้อความแค่ครั้งเดียว (ตรวจ marker) รันซ้ำได้
# ใช้: bash install.sh [--dry-run]
set -euo pipefail
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if   [ -f "$here/skills/dfd-er-design/SKILL.md" ]; then SRC="$here/skills/dfd-er-design"
elif [ -f "$here/SKILL.md" ]; then SRC="$here"
elif [ -f "$here/../../SKILL.md" ]; then SRC="$(cd "$here/../.." && pwd)"
else echo "ไม่พบโฟลเดอร์ skill dfd-er-design" >&2; exit 1; fi
SNIP="$SRC/templates/bootstrap/CLAUDE.md"
MARK="dfd-er-design:bootstrap:start"
TS="$(date +%Y%m%d-%H%M%S)"
BK="$HOME/.dfd-er-design-backup/$TS"   # สำรองไว้นอกโฟลเดอร์ skills เพื่อไม่ให้ agent โหลด skill ซ้ำ
run(){ if [ $DRY = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

for base in "$HOME/.claude/skills" "$HOME/.cursor/skills" "$HOME/.agents/skills"; do
  dst="$base/dfd-er-design"
  if [ "$(cd "$SRC" && pwd -P)" = "$( [ -d "$dst" ] && cd "$dst" && pwd -P || echo none)" ]; then
    echo "ข้าม $dst (เป็นโฟลเดอร์ต้นทาง)"; continue; fi
  run mkdir -p "$base"
  if [ -e "$dst" ]; then b="$BK/$(basename "$(dirname "$base")")-skills"; run mkdir -p "$b"; run mv "$dst" "$b/"; echo "สำรอง $dst -> $b/"; fi
  run cp -R "$SRC" "$dst"; echo "ติดตั้ง skill -> $dst"
done

for f in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md"; do
  run mkdir -p "$(dirname "$f")"
  if [ -f "$f" ] && grep -q "$MARK" "$f"; then echo "มีคำสั่ง bootstrap แล้ว: $f (ไม่แก้)"; continue; fi
  if [ -f "$f" ]; then run cp -p "$f" "$f.bak-$TS"; echo "สำรอง $f -> $f.bak-$TS"; fi
  if [ $DRY = 1 ]; then echo "[dry-run] append bootstrap -> $f"
  else { [ -s "$f" ] && printf '\n'; cat "$SNIP"; } >> "$f"; echo "เพิ่มคำสั่ง bootstrap -> $f"; fi
done

cat <<MSG

เสร็จแล้ว ขั้นตอนที่สคริปต์ทำแทนไม่ได้:
- Cursor: Settings > Rules > User Rules วางข้อความจาก $SRC/templates/bootstrap/cursor-user-rule.txt
  (หรือคัดลอก load-dfd-er-design.mdc ไปไว้ที่ .cursor/rules/ ของแต่ละโปรเจกต์)
- เปิด agent ใหม่ (session ใหม่) เพื่อให้โหลดไฟล์ที่แก้
- ชุดเครื่องมือ (Ponytail, Graphify, document-skills): ดู $SRC/docs/toolchain.md สคริปต์นี้ไม่ติดตั้งให้
MSG
