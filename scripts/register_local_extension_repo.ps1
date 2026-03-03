Param(
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
    [string]$RepoRoot = "",
    [string]$RepoId = "blender_project_manager_repo",
    [string]$RepoName = "Blender Project Manager (Local Repo)",
    [switch]$Sync
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
if (!(Test-Path $BlenderExe)) { throw "Blender executable not found: $BlenderExe" }

$repoDir = Join-Path $RepoRoot "extension_repo"
$indexPath = Join-Path $repoDir "index.json"
if (!(Test-Path $indexPath)) {
    throw "index.json not found at $indexPath. Run scripts/release_new_version.ps1 first."
}

$indexUri = "file:///" + ($indexPath -replace "\\", "/")

Write-Host "Registering extension repo in Blender"
& $BlenderExe --factory-startup --command extension repo-add $RepoId --name $RepoName --url $indexUri --source USER
if ($LASTEXITCODE -ne 0) { throw "repo-add failed with code $LASTEXITCODE" }

if ($Sync) {
    Write-Host "Syncing repository"
    & $BlenderExe --factory-startup --command extension sync
    if ($LASTEXITCODE -ne 0) {
        throw "sync failed with code $LASTEXITCODE. Blender may require online access enabled in preferences."
    }
}

Write-Host "Done. Repo URL: $indexUri"
