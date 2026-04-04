Param(
    [string]$TargetRepoPath = "",
    [string]$TargetRepoUrl = "",

    [string]$TargetSubdir = "",
    [string]$SourceRepoRoot = "",
    [string]$SourceArtifactsDir = "",
    [switch]$Commit,
    [switch]$Push,
    [string]$Branch = "",
    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SourceRepoRoot)) {
    $SourceRepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

if ([string]::IsNullOrWhiteSpace($SourceArtifactsDir)) {
    $SourceArtifactsDir = Join-Path $SourceRepoRoot "extension_repo"
}

$resolvedSourceArtifactsDir = (Resolve-Path $SourceArtifactsDir).Path

if ([string]::IsNullOrWhiteSpace($TargetRepoPath)) {
    if ([string]::IsNullOrWhiteSpace($TargetRepoUrl)) {
        throw "Provide -TargetRepoPath or -TargetRepoUrl."
    }

    $repoName = [System.IO.Path]::GetFileNameWithoutExtension($TargetRepoUrl.TrimEnd('/'))
    $TargetRepoPath = Join-Path ([System.IO.Path]::GetDirectoryName($SourceRepoRoot)) $repoName
}

if (!(Test-Path $TargetRepoPath)) {
    if ([string]::IsNullOrWhiteSpace($TargetRepoUrl)) {
        throw "Target repo path does not exist: $TargetRepoPath"
    }

    Write-Host "Cloning target repository into $TargetRepoPath"
    & git clone $TargetRepoUrl $TargetRepoPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone target repository from $TargetRepoUrl"
    }
}

$resolvedTargetRepoPath = (Resolve-Path $TargetRepoPath).Path

$targetDir = $resolvedTargetRepoPath
if (-not [string]::IsNullOrWhiteSpace($TargetSubdir)) {
    $targetDir = Join-Path $resolvedTargetRepoPath $TargetSubdir
}

if (!(Test-Path (Join-Path $resolvedTargetRepoPath ".git"))) {
    throw "Target repo is not a git repository: $resolvedTargetRepoPath"
}

if (!(Test-Path $resolvedSourceArtifactsDir)) {
    throw "Source artifacts directory not found: $resolvedSourceArtifactsDir"
}

$indexPath = Join-Path $resolvedSourceArtifactsDir "index.json"
if (!(Test-Path $indexPath)) {
    throw "index.json not found at $indexPath. Run scripts/release_new_version.ps1 first."
}

$index = Get-Content $indexPath -Raw | ConvertFrom-Json
if ($null -eq $index.data -or $index.data.Count -eq 0) {
    throw "index.json does not contain any extension entries."
}

$addonEntry = $index.data | Where-Object { $_.id -eq "blender_project_manager" } | Select-Object -First 1
if ($null -eq $addonEntry) {
    $addonEntry = $index.data | Select-Object -First 1
}

$version = $addonEntry.version
$archiveName = Split-Path $addonEntry.archive_url -Leaf
$archivePath = Join-Path $resolvedSourceArtifactsDir $archiveName
if (!(Test-Path $archivePath)) {
    throw "Extension archive referenced by index.json was not found: $archivePath"
}

$optionalRepoMetadata = Join-Path $resolvedSourceArtifactsDir "blender_repo.toml"

Write-Host "[1/4] Preparing target directory"
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

Write-Host "[2/4] Syncing extension artifacts for version $version"
Get-ChildItem -Path $targetDir -Filter "blender_project_manager-*.zip" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne $archiveName } |
    Remove-Item -Force

Copy-Item -Path $archivePath -Destination (Join-Path $targetDir $archiveName) -Force
Copy-Item -Path $indexPath -Destination (Join-Path $targetDir "index.json") -Force

if (Test-Path $optionalRepoMetadata) {
    Copy-Item -Path $optionalRepoMetadata -Destination (Join-Path $targetDir "blender_repo.toml") -Force
}

if (-not $Commit -and -not $Push) {
    Write-Host "[3/4] Skipping git commit/push"
    Write-Host "[4/4] Done"
    Write-Host "Target directory updated: $targetDir"
    exit 0
}

if (-not [string]::IsNullOrWhiteSpace($Branch)) {
    Write-Host "[3/4] Switching target repository to branch $Branch"
    & git -C $resolvedTargetRepoPath checkout $Branch
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to checkout branch '$Branch' in target repository."
    }
} else {
    Write-Host "[3/4] Using current target repository branch"
}

if (-not [string]::IsNullOrWhiteSpace($TargetRepoUrl)) {
    $currentRemote = (& git -C $resolvedTargetRepoPath remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to read origin URL from target repository."
    }
    if ($currentRemote -ne $TargetRepoUrl) {
        throw "Target repository origin mismatch. Expected '$TargetRepoUrl', got '$currentRemote'."
    }
}

& git -C $resolvedTargetRepoPath add -- $targetDir
if ($LASTEXITCODE -ne 0) {
    throw "Failed to stage synced artifacts in target repository."
}

$stagedDiff = & git -C $resolvedTargetRepoPath diff --cached --name-only
if ($LASTEXITCODE -ne 0) {
    throw "Failed to inspect staged changes in target repository."
}

if ([string]::IsNullOrWhiteSpace($stagedDiff)) {
    Write-Host "[4/4] No changes to commit"
    exit 0
}

if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    $CommitMessage = "Publish Blender Project Manager extension v$version"
}

& git -C $resolvedTargetRepoPath commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Failed to commit synced artifacts in target repository."
}

if ($Push) {
    $currentBranch = (& git -C $resolvedTargetRepoPath branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($currentBranch)) {
        throw "Failed to determine current branch for push."
    }

    & git -C $resolvedTargetRepoPath push origin $currentBranch
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to push branch '$currentBranch' to origin."
    }
}

Write-Host "[4/4] Done"
Write-Host "Target directory updated: $targetDir"
