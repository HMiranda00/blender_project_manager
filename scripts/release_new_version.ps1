Param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version,

    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
    [string]$RepoRoot = "",
    [switch]$SkipTests,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$initPath = Join-Path $RepoRoot "__init__.py"
$manifestPath = Join-Path $RepoRoot "blender_manifest.toml"
$readmePath = Join-Path $RepoRoot "README.md"
$changelogPath = Join-Path $RepoRoot "CHANGELOG.md"
$releaseDir = Join-Path $RepoRoot "extension_repo"

if (!(Test-Path $initPath)) { throw "Missing __init__.py at $initPath" }
if (!(Test-Path $manifestPath)) { throw "Missing blender_manifest.toml at $manifestPath" }
if (!(Test-Path $readmePath)) { throw "Missing README.md at $readmePath" }
if (!(Test-Path $BlenderExe)) { throw "Blender executable not found: $BlenderExe" }

$versionParts = $Version.Split('.')
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]
$patch = [int]$versionParts[2]
$today = Get-Date -Format "yyyy-MM-dd"

Write-Host "[1/6] Updating version references to $Version"

$initText = Get-Content $initPath -Raw
$initText = [regex]::Replace(
    $initText,
    '"version"\s*:\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',
    ('"version": ({0}, {1}, {2})' -f $major, $minor, $patch)
)
Set-Content $initPath $initText

$manifestText = Get-Content $manifestPath -Raw
$manifestText = [regex]::Replace($manifestText, 'version\s*=\s*"[^"]+"', ('version = "{0}"' -f $Version))
Set-Content $manifestPath $manifestText

$readmeText = Get-Content $readmePath -Raw
$readmeText = [regex]::Replace($readmeText, 'version-[0-9]+\.[0-9]+\.[0-9]+-blue\.svg', ('version-{0}-blue.svg' -f $Version))
Set-Content $readmePath $readmeText

if (!(Test-Path $changelogPath)) {
    @"
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 
"@ | Set-Content $changelogPath
}

$changelogText = Get-Content $changelogPath -Raw
$versionHeader = "## [$Version] - $today"
if ($changelogText -notmatch [regex]::Escape($versionHeader)) {
    $insert = @"
$versionHeader

### Added
- 

### Changed
- 

### Fixed
- 

"@

    if ($changelogText -match "## \[Unreleased\]\r?\n") {
        $changelogText = $changelogText -replace "## \[Unreleased\]\r?\n", ("## [Unreleased]`r`n`r`n" + $insert)
    } else {
        $changelogText = $changelogText.TrimEnd() + "`r`n`r`n" + $insert
    }
    Set-Content $changelogPath $changelogText
}

if (-not $SkipTests) {
    Write-Host "[2/6] Running unit tests"
    powershell -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\run_unit_tests.ps1")
}

if (-not $SkipBuild) {
    Write-Host "[3/6] Validating extension manifest"
    & $BlenderExe --factory-startup --command extension validate $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Extension validate failed with code $LASTEXITCODE" }

    Write-Host "[4/6] Building extension package"
    if (!(Test-Path $releaseDir)) { New-Item -ItemType Directory -Path $releaseDir | Out-Null }
    & $BlenderExe --factory-startup --command extension build --source-dir $RepoRoot --output-dir $releaseDir
    if ($LASTEXITCODE -ne 0) { throw "Extension build failed with code $LASTEXITCODE" }

    Write-Host "[5/6] Generating extension repository index.json"
    & $BlenderExe --factory-startup --command extension server-generate --repo-dir $releaseDir
    if ($LASTEXITCODE -ne 0) { throw "Extension server-generate failed with code $LASTEXITCODE" }
    if (!(Test-Path (Join-Path $releaseDir "index.json"))) { throw "index.json was not generated in $releaseDir" }
}

Write-Host "[6/6] Done"
Write-Host "Version set to: $Version"
if (-not $SkipBuild) {
    Write-Host "Artifacts directory: $releaseDir"
    Write-Host "Index file: $(Join-Path $releaseDir 'index.json')"
}
Write-Host "Remember to fill CHANGELOG.md entries before publishing."
