Param(
    [Parameter(Mandatory = $true)]
    [string]$BlenderVersion,
    [string]$OutputDir = "validation_reports"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$dateStamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$outFile = Join-Path $OutputDir "validation_${BlenderVersion}_$dateStamp.md"

$template = @"
# Validation Report - Blender $BlenderVersion

Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Tester:
Commit/tag:
OS:

## Checklist Results

Copy and fill the checklist from:
docs/BLENDER_VALIDATION_CHECKLIST.md

## Failures and Logs

- Failure:
  - Repro steps:
  - Expected:
  - Observed:
  - Error log:
"@

$template | Set-Content $outFile
Write-Host "Created: $outFile"
