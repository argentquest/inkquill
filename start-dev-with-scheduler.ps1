param(
    [switch]$Detach,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path $PSScriptRoot).Path
$frontendRoot = Join-Path $repoRoot "frontendv1"
$logsRoot = Join-Path $repoRoot "logs"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"

if (-not (Test-Path $logsRoot)) {
    New-Item -ItemType Directory -Path $logsRoot | Out-Null
}

function Write-Status {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host $Message -ForegroundColor $Color
}

Write-Status "=== Starting Ink & Quill Full Dev Environment with Scheduler ===" -Color Green
Write-Status "Backend (8000) + Scheduler (8001) + Frontend (3000)" -Color Yellow

$startBackend = -not $FrontendOnly
$startScheduler = $true
$startFrontend = -not $BackendOnly

# Start Backend
if ($startBackend) {
    Write-Status "`nStarting Main Backend on http://localhost:8000 ..." -Color Cyan
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$repoRoot'; .\$pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`"" -NoNewWindow
    Start-Sleep -Seconds 4
}

# Start Scheduler
if ($startScheduler) {
    Write-Status "`nStarting Scheduler on http://localhost:8001 ..." -Color Magenta
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$repoRoot'; .\$pythonExe -m uvicorn app.scheduler.main:app --host 0.0.0.0 --port 8001 --reload`"" -NoNewWindow
    Start-Sleep -Seconds 3
}

# Start Frontend
if ($startFrontend) {
    Write-Status "`nStarting React Frontend (frontendv1) on http://localhost:3000 ..." -Color Blue
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$frontendRoot'; npm run dev`"" -NoNewWindow
}

Write-Status "`nAll services started!" -Color Green
Write-Status "→ Main App:     http://localhost:8000" -Color White
Write-Status "→ Scheduler UI: http://localhost:8001/scheduler" -Color White
Write-Status "→ React Frontend: http://localhost:3000" -Color White
Write-Status "`nPress Ctrl+C in each window to stop individual services." -Color Gray