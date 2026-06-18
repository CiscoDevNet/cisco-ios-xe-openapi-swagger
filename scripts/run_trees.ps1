$ErrorActionPreference = "Continue"
# Run from the repo root regardless of the caller's cwd (script lives in scripts/).
Set-Location (Join-Path $PSScriptRoot "..")
foreach ($v in @("17.9.x","17.12.x","17.15.x","26.1.1","17.18.1")) {
  Write-Host "===== START $v $(Get-Date -Format o) ====="
  python -X utf8 scripts/generate_all_pyang_trees.py --version $v --include-mibs 2>&1 | Tee-Object -FilePath "trees-$v.log"
  Write-Host "===== END   $v exit=$LASTEXITCODE $(Get-Date -Format o) ====="
}
Write-Host "ALL DONE $(Get-Date -Format o)"
