# ติดตั้ง skill dfd-er-design แบบ global (Windows PowerShell) และเพิ่มคำสั่ง "อ่าน skill นี้ก่อนทุกงาน"
# ใน ~/.claude/CLAUDE.md และ ~/.codex/AGENTS.md  สำรองไฟล์เดิมก่อนแก้ (skill เดิม -> ~/.dfd-er-design-backup/<เวลา>/) เพิ่มครั้งเดียว (ตรวจ marker) รันซ้ำได้
# ใช้: powershell -ExecutionPolicy Bypass -File install.ps1 [-DryRun]
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
if     (Test-Path (Join-Path $here 'skills\dfd-er-design\SKILL.md')) { $src = Join-Path $here 'skills\dfd-er-design' }
elseif (Test-Path (Join-Path $here 'SKILL.md'))                     { $src = $here }
elseif (Test-Path (Join-Path $here '..\..\SKILL.md'))               { $src = (Resolve-Path (Join-Path $here '..\..')).Path }
else { throw 'ไม่พบโฟลเดอร์ skill dfd-er-design' }
$src  = (Resolve-Path $src).Path
$snip = Join-Path $src 'templates\bootstrap\CLAUDE.md'
$mark = 'dfd-er-design:bootstrap:start'
$ts   = Get-Date -Format 'yyyyMMdd-HHmmss'
$bk   = Join-Path $HOME ".dfd-er-design-backup\$ts"   # สำรองไว้นอกโฟลเดอร์ skills เพื่อไม่ให้ agent โหลด skill ซ้ำ
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Do-It($msg, [scriptblock]$act) { if ($DryRun) { Write-Host "[dry-run] $msg" } else { & $act; Write-Host $msg } }

foreach ($base in @("$HOME\.claude\skills", "$HOME\.cursor\skills", "$HOME\.agents\skills")) {
  $dst = Join-Path $base 'dfd-er-design'
  if ((Test-Path $dst) -and ((Resolve-Path $dst).Path -eq $src)) { Write-Host "ข้าม $dst (เป็นโฟลเดอร์ต้นทาง)"; continue }
  Do-It "เตรียม $base" { New-Item -ItemType Directory -Force -Path $base | Out-Null }
  if (Test-Path $dst) {
    $b = Join-Path $bk ((Split-Path (Split-Path $base) -Leaf) + '-skills')
    Do-It "สำรอง $dst -> $b\" { New-Item -ItemType Directory -Force -Path $b | Out-Null; Move-Item $dst $b } }
  Do-It "ติดตั้ง skill -> $dst" { Copy-Item $src $dst -Recurse }
}

$text = [IO.File]::ReadAllText($snip, $utf8)
foreach ($f in @("$HOME\.claude\CLAUDE.md", "$HOME\.codex\AGENTS.md")) {
  $dir = Split-Path $f
  if ((Test-Path $f) -and ((Get-Content $f -Raw -Encoding UTF8) -match [regex]::Escape($mark))) {
    Write-Host "มีคำสั่ง bootstrap แล้ว: $f (ไม่แก้)"; continue }
  Do-It "เตรียม $dir" { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  if (Test-Path $f) { Do-It "สำรอง $f -> $f.bak-$ts" { Copy-Item $f "$f.bak-$ts" } }
  Do-It "เพิ่มคำสั่ง bootstrap -> $f" {
    $pre = ''; if ((Test-Path $f) -and (Get-Item $f).Length -gt 0) { $pre = "`n" }
    [IO.File]::AppendAllText($f, $pre + $text, $utf8) }
}

Write-Host ''
Write-Host 'เสร็จแล้ว ขั้นตอนที่สคริปต์ทำแทนไม่ได้:'
Write-Host "- Cursor: Settings > Rules > User Rules วางข้อความจาก $src\templates\bootstrap\cursor-user-rule.txt"
Write-Host '  (หรือคัดลอก load-dfd-er-design.mdc ไปไว้ที่ .cursor\rules\ ของแต่ละโปรเจกต์)'
Write-Host '- เปิด agent ใหม่ (session ใหม่) เพื่อให้โหลดไฟล์ที่แก้'
Write-Host "- ชุดเครื่องมือ (Ponytail, Graphify, document-skills): ดู $src\docs\toolchain.md สคริปต์นี้ไม่ติดตั้งให้"
