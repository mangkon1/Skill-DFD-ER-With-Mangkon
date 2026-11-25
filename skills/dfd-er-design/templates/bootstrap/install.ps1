# ติดตั้ง skill thai-reply + dfd-er-design แบบ global (Windows PowerShell) และเพิ่มคำสั่ง "อ่าน thai-reply เป็นอันดับแรก แล้ว dfd-er-design ก่อนทุกงาน"
# ใน ~/.claude/CLAUDE.md และ ~/.codex/AGENTS.md  สำรองไฟล์เดิมก่อนแก้ (skill เดิม -> ~/.dfd-er-design-backup/<เวลา>/)
# เพิ่มครั้งเดียว (ตรวจ marker ของแต่ละ skill) รันซ้ำได้; บล็อก thai-reply วางไว้ก่อนบล็อก dfd-er-design
# ใช้: powershell -ExecutionPolicy Bypass -File install.ps1 [-DryRun]
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
if     (Test-Path (Join-Path $here 'skills\dfd-er-design\SKILL.md')) { $src = Join-Path $here 'skills\dfd-er-design' }
elseif (Test-Path (Join-Path $here 'SKILL.md'))                     { $src = $here }
elseif (Test-Path (Join-Path $here '..\..\SKILL.md'))               { $src = (Resolve-Path (Join-Path $here '..\..')).Path }
else { throw 'ไม่พบโฟลเดอร์ skill dfd-er-design' }
$src  = (Resolve-Path $src).Path
if     (Test-Path (Join-Path $here 'skills\thai-reply\SKILL.md')) { $thai = (Resolve-Path (Join-Path $here 'skills\thai-reply')).Path }
elseif (Test-Path (Join-Path $src '..\thai-reply\SKILL.md'))     { $thai = (Resolve-Path (Join-Path $src '..\thai-reply')).Path }
else { $thai = $null; Write-Warning 'ไม่พบโฟลเดอร์ skill thai-reply (ติดตั้งเฉพาะ dfd-er-design แต่ยังเพิ่มคำสั่งตอบภาษาไทยใน bootstrap)' }
$snip = Join-Path $src 'templates\bootstrap\CLAUDE.md'
$mark = 'dfd-er-design:bootstrap:start'
$tmark = 'thai-reply:bootstrap:start'
$ts   = Get-Date -Format 'yyyyMMdd-HHmmss'
$bk   = Join-Path $HOME ".dfd-er-design-backup\$ts"   # สำรองไว้นอกโฟลเดอร์ skills เพื่อไม่ให้ agent โหลด skill ซ้ำ
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Do-It($msg, [scriptblock]$act) { if ($DryRun) { Write-Host "[dry-run] $msg" } else { & $act; Write-Host $msg } }

foreach ($sk in @($thai, $src) | Where-Object { $_ }) {
$name = Split-Path $sk -Leaf
foreach ($base in @("$HOME\.claude\skills", "$HOME\.cursor\skills", "$HOME\.agents\skills")) {
  $dst = Join-Path $base $name
  if ((Test-Path $dst) -and ((Resolve-Path $dst).Path -eq $sk)) { Write-Host "ข้าม $dst (เป็นโฟลเดอร์ต้นทาง)"; continue }
  Do-It "เตรียม $base" { New-Item -ItemType Directory -Force -Path $base | Out-Null }
  if (Test-Path $dst) {
    $b = Join-Path $bk ((Split-Path (Split-Path $base) -Leaf) + '-skills')
    Do-It "สำรอง $dst -> $b\" { New-Item -ItemType Directory -Force -Path $b | Out-Null; Move-Item $dst $b } }
  Do-It "ติดตั้ง skill -> $dst" { Copy-Item $sk $dst -Recurse }
}
}

$text = ([IO.File]::ReadAllText($snip, $utf8)) -replace "`r`n", "`n"
function Get-Block($n) { $m = [regex]::Match($text, "(?s)<!-- ${n}:bootstrap:start.*?<!-- ${n}:bootstrap:end -->"); return $m.Value + "`n" }
$tblock = Get-Block 'thai-reply'; $dblock = Get-Block 'dfd-er-design'
foreach ($f in @("$HOME\.claude\CLAUDE.md", "$HOME\.codex\AGENTS.md")) {
  $dir = Split-Path $f
  $cur = ''; if (Test-Path $f) { $cur = [IO.File]::ReadAllText($f, $utf8) }
  $hasT = $cur.Contains($tmark); $hasD = $cur.Contains($mark)
  if ($hasT -and $hasD) { Write-Host "มีคำสั่ง bootstrap ครบแล้ว: $f (ไม่แก้)"; continue }
  Do-It "เตรียม $dir" { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  if (Test-Path $f) { Do-It "สำรอง $f -> $f.bak-$ts" { Copy-Item $f "$f.bak-$ts" } }
  $new = $cur
  if (-not $hasT) {
    if ($hasD) { $i = $new.IndexOf('<!-- ' + $mark); $new = $new.Substring(0, $i) + $tblock + "`n" + $new.Substring($i) }   # แทรกก่อนบล็อก dfd-er-design เดิม
    else { if ($new.Length -gt 0) { $new += "`n" }; $new += $tblock } }
  if (-not $hasD) { if ($new.Length -gt 0) { $new += "`n" }; $new += $dblock }
  Do-It "เพิ่มคำสั่ง bootstrap (thai-reply ก่อน dfd-er-design) -> $f" { [IO.File]::WriteAllText($f, $new, $utf8) }
}

Write-Host ''
Write-Host 'เสร็จแล้ว ขั้นตอนที่สคริปต์ทำแทนไม่ได้:'
Write-Host "- Cursor: Settings > Rules > User Rules วางข้อความจาก $src\templates\bootstrap\cursor-user-rule.txt"
Write-Host '  (หรือคัดลอก 00-load-thai-reply.mdc และ load-dfd-er-design.mdc ไปไว้ที่ .cursor\rules\ ของแต่ละโปรเจกต์)'
Write-Host '- เปิด agent ใหม่ (session ใหม่) เพื่อให้โหลดไฟล์ที่แก้'
Write-Host "- ชุดเครื่องมือ (Ponytail, Graphify, document-skills): ดู $src\docs\toolchain.md สคริปต์นี้ไม่ติดตั้งให้"
