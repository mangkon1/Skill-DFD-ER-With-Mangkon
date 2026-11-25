#!/usr/bin/env bash
# ติดตั้ง skill thai-reply + dfd-er-design แบบ global และเพิ่มคำสั่ง "อ่าน thai-reply เป็นอันดับแรก แล้ว dfd-er-design ก่อนทุกงาน"
# ใน CLAUDE.md / AGENTS.md ระดับผู้ใช้
# - สำรองไฟล์เดิมก่อนแก้ทุกครั้ง (skill เดิม -> ~/.dfd-er-design-backup/<เวลา>/, CLAUDE.md/AGENTS.md -> *.bak-<เวลา>)
# - เพิ่มข้อความแค่ครั้งเดียว (ตรวจ marker ของแต่ละ skill) รันซ้ำได้; บล็อก thai-reply วางไว้ก่อนบล็อก dfd-er-design
# ใช้: bash install.sh [--dry-run]
set -euo pipefail
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if   [ -f "$here/skills/dfd-er-design/SKILL.md" ]; then SRC="$here/skills/dfd-er-design"
elif [ -f "$here/SKILL.md" ]; then SRC="$here"
elif [ -f "$here/../../SKILL.md" ]; then SRC="$(cd "$here/../.." && pwd)"
else echo "ไม่พบโฟลเดอร์ skill dfd-er-design" >&2; exit 1; fi
if   [ -f "$here/skills/thai-reply/SKILL.md" ]; then THAI="$here/skills/thai-reply"
elif [ -f "$SRC/../thai-reply/SKILL.md" ]; then THAI="$(cd "$SRC/../thai-reply" && pwd)"
else THAI=""; echo "คำเตือน: ไม่พบโฟลเดอร์ skill thai-reply (ติดตั้งเฉพาะ dfd-er-design แต่ยังเพิ่มคำสั่งตอบภาษาไทยใน bootstrap)" >&2; fi
SNIP="$SRC/templates/bootstrap/CLAUDE.md"
MARK="dfd-er-design:bootstrap:start"
TMARK="thai-reply:bootstrap:start"
block(){ awk -v n="$1" 'index($0,"<!-- " n ":bootstrap:start"){p=1} p{print} index($0,"<!-- " n ":bootstrap:end"){p=0}' "$SNIP"; }
TS="$(date +%Y%m%d-%H%M%S)"
BK="$HOME/.dfd-er-design-backup/$TS"   # สำรองไว้นอกโฟลเดอร์ skills เพื่อไม่ให้ agent โหลด skill ซ้ำ
run(){ if [ $DRY = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

for S in $THAI "$SRC"; do
name="$(basename "$S")"
for base in "$HOME/.claude/skills" "$HOME/.cursor/skills" "$HOME/.agents/skills"; do
  dst="$base/$name"
  if [ "$(cd "$S" && pwd -P)" = "$( [ -d "$dst" ] && cd "$dst" && pwd -P || echo none)" ]; then
    echo "ข้าม $dst (เป็นโฟลเดอร์ต้นทาง)"; continue; fi
  run mkdir -p "$base"
  if [ -e "$dst" ]; then b="$BK/$(basename "$(dirname "$base")")-skills"; run mkdir -p "$b"; run mv "$dst" "$b/"; echo "สำรอง $dst -> $b/"; fi
  run cp -R "$S" "$dst"; echo "ติดตั้ง skill -> $dst"
done
done

for f in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md"; do
  run mkdir -p "$(dirname "$f")"
  hasT=0; hasD=0
  [ -f "$f" ] && grep -q "$TMARK" "$f" && hasT=1
  [ -f "$f" ] && grep -q "$MARK" "$f" && hasD=1
  if [ $hasT = 1 ] && [ $hasD = 1 ]; then echo "มีคำสั่ง bootstrap ครบแล้ว: $f (ไม่แก้)"; continue; fi
  if [ -f "$f" ]; then run cp -p "$f" "$f.bak-$TS"; echo "สำรอง $f -> $f.bak-$TS"; fi
  if [ $DRY = 1 ]; then echo "[dry-run] เพิ่ม bootstrap (thai-reply ก่อน dfd-er-design) -> $f"; continue; fi
  if [ $hasT = 0 ]; then
    if [ $hasD = 1 ]; then   # แทรกบล็อก thai-reply ไว้ก่อนบล็อก dfd-er-design เดิม
      tb="$(mktemp)"; block thai-reply > "$tb"
      awk -v tb="$tb" -v m="<!-- dfd-er-design:bootstrap:start" 'index($0,m) && !d {while((getline l < tb)>0) print l; print ""; d=1} {print}' "$f" > "$f.tmp-$TS" && mv "$f.tmp-$TS" "$f"; rm -f "$tb"
    else { [ -s "$f" ] && printf '\n'; block thai-reply; } >> "$f"; fi
    echo "เพิ่มคำสั่ง thai-reply -> $f"
  fi
  if [ $hasD = 0 ]; then { printf '\n'; block dfd-er-design; } >> "$f"; echo "เพิ่มคำสั่ง dfd-er-design -> $f"; fi
done

cat <<MSG

เสร็จแล้ว ขั้นตอนที่สคริปต์ทำแทนไม่ได้:
- Cursor: Settings > Rules > User Rules วางข้อความจาก $SRC/templates/bootstrap/cursor-user-rule.txt
  (หรือคัดลอก 00-load-thai-reply.mdc และ load-dfd-er-design.mdc ไปไว้ที่ .cursor/rules/ ของแต่ละโปรเจกต์)
- เปิด agent ใหม่ (session ใหม่) เพื่อให้โหลดไฟล์ที่แก้
- ชุดเครื่องมือ (Ponytail, Graphify, document-skills): ดู $SRC/docs/toolchain.md สคริปต์นี้ไม่ติดตั้งให้
MSG
