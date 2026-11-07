# Bản Windows của setup_paths.sh. Chạy trong PowerShell (không cần quyền admin):
#   powershell -ExecutionPolicy Bypass -File setup_paths.ps1 C:\duong\dan\toi\data_inputs
# Thư mục: dùng junction. File parquet: hard link (cùng ổ đĩa), nếu khác ổ thì copy.
param([Parameter(Mandatory=$true)][string]$Data)
$ErrorActionPreference = "Stop"
$Data = (Resolve-Path $Data).Path
$Repo = $PSScriptRoot
$Root = Join-Path $HOME "mnt\NCKH - NEU"     # Python expanduser("~") = %USERPROFILE% = $HOME

$pap = Join-Path $Root "_claude_pap"
if ((Test-Path $Root) -and -not ((Test-Path $pap) -and ((Get-Item $pap).LinkType -eq "Junction"))) {
  Write-Host "Da ton tai $Root (khong phai ban setup). Dung de tranh ghi de."; exit 1
}
New-Item -ItemType Directory -Force -Path $Root | Out-Null

function Link-Dir($target, $link) {
  if (Test-Path $link) { (Get-Item $link).Delete() }
  New-Item -ItemType Junction -Path $link -Target $target | Out-Null
}
Link-Dir (Join-Path $Repo "_claude_pap") $pap
foreach ($d in "_drive_latest","data_external","_claude_eda","_claude_feasibility") {
  Link-Dir (Join-Path $Data $d) (Join-Path $Root $d)
}

function Link-File($rel) {
  $src = Join-Path $Data $rel; $dst = Join-Path $Repo $rel
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  if (Test-Path $dst) { Remove-Item $dst -Force }
  try { New-Item -ItemType HardLink -Path $dst -Target $src | Out-Null }
  catch { Copy-Item $src $dst }
}
Link-File "_claude_pap\out\county_panel.parquet"
Link-File "_claude_pap\out\bank_panel.parquet"
Link-File "_claude_pap\rq3_explore\bank_coverage_pre.parquet"

# Script thăm dò rq3_explore/G*.py ghi vào "/tmp/g1" = \tmp\g1 trên ổ đang đứng
New-Item -ItemType Directory -Force -Path (Join-Path (Split-Path $Repo -Qualifier) "tmp\g1") | Out-Null
Write-Host "OK: $Root -> repo + data_inputs"
