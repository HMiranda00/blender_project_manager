Param()

$ErrorActionPreference = "Stop"

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd -and $pythonCmd.Source -like "*WindowsApps*") {
    $pythonCmd = $null
}
if (-not $pythonCmd) {
    $fallback = Join-Path $env:LocalAppData "Programs\\Python\\Python312\\python.exe"
    if (Test-Path $fallback) {
        $pythonCmd = @{ Source = $fallback }
    } else {
        throw "Python not found. Install Python 3.12 or add it to PATH."
    }
}

Write-Host "Running pure unit tests..."
& $pythonCmd.Source -m unittest discover -s tests -p "test_*.py" -v
