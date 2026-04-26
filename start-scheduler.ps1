param(
    [switch]$Detach,
    [switch]$NoLogs
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path $PSScriptRoot).Path
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

$logFile = Join-Path $logsRoot "scheduler-$runStamp.log"
$schedulerArgs = if ($Detach) {
    "-m uvicorn app.scheduler.main:app --host 0.0.0.0 --port 8001"
} else {
    "-m uvicorn app.scheduler.main:app --host 0.0.0.0 --port 8001 --reload"
}

Write-Status "=== Starting Ink & Quill Scheduler ===" -Color Green
Write-Status "Log file: $logFile" -Color Gray
Write-Status "Scheduler will run on http://localhost:8001" -Color Yellow

if ($NoLogs) {
    Write-Status "Running scheduler without log redirection..." -Color Gray
    Invoke-Expression "& `"$pythonExe`" $schedulerArgs"
} else {
    Write-Status "Logs will be written to $logFile" -Color Gray
    
    if ($Detach) {
        Write-Status "Starting scheduler in background (detached, reload disabled for Windows stability)..." -Color Green
        Start-Process -FilePath $pythonExe `
                      -ArgumentList $schedulerArgs `
                      -RedirectStandardOutput $logFile `
                      -RedirectStandardError "$logFile.err" `
                      -NoNewWindow
        Write-Status "Scheduler started in background. Check $logFile for output." -Color Green
    } else {
        Write-Status "Starting scheduler (press Ctrl+C to stop)..." -Color Green
        try {
            Invoke-Expression "& `"$pythonExe`" $schedulerArgs" 2>&1 | Tee-Object -FilePath $logFile
        } catch {
            Write-Status "Scheduler stopped." -Color Yellow
        }
    }
}
