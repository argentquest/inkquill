param(
    [switch]$Detach,
    [switch]$NoLogs
)

$ErrorActionPreference = "Stop"
$repoRoot   = (Resolve-Path $PSScriptRoot).Path
$logsRoot   = Join-Path $repoRoot "logs"
$pythonExe  = Join-Path $repoRoot ".venv\Scripts\python.exe"
$runStamp   = Get-Date -Format "yyyyMMdd-HHmmss"

if (-not (Test-Path $logsRoot)) {
    New-Item -ItemType Directory -Path $logsRoot | Out-Null
}

function Write-Status {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host $Message -ForegroundColor $Color
}

# Read SCHEDULER_HOST / SCHEDULER_PORT from the root .env if they are not
# already set in the shell environment.  This keeps the script in sync with
# the values the Python process reads from settings.
$envFile = Join-Path $repoRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([A-Z_]+)\s*=\s*"?([^"#\r\n]*)"?\s*$') {
            $varName  = $Matches[1]
            $varValue = $Matches[2].Trim()
            if ($varName -in @("SCHEDULER_HOST", "SCHEDULER_PORT") -and
                -not [System.Environment]::GetEnvironmentVariable($varName)) {
                [System.Environment]::SetEnvironmentVariable($varName, $varValue)
            }
        }
    }
}

$schedulerHost = $env:SCHEDULER_HOST
$schedulerPort = $env:SCHEDULER_PORT

# When running as a standalone server that Docker containers must reach via
# host.docker.internal, SCHEDULER_HOST should be 0.0.0.0.  For local VS Code
# development the launch.json uses --host localhost, which is more secure.
# This script targets the standalone-server scenario, so default to 0.0.0.0.
if (-not $schedulerHost) { $schedulerHost = "0.0.0.0" }
if (-not $schedulerPort) { $schedulerPort = "8001" }

$logFile       = Join-Path $logsRoot "scheduler-$runStamp.log"
$uvicornArgs   = "app.scheduler.main:app --host $schedulerHost --port $schedulerPort"
$uvicornArgs  += if ($Detach) { "" } else { " --reload" }
$schedulerArgs = "-m uvicorn $uvicornArgs"

Write-Status "=== Starting Ink & Quill Scheduler ===" -Color Green
Write-Status "Bind:     http://$schedulerHost`:$schedulerPort" -Color Yellow
Write-Status "Log file: $logFile" -Color Gray

if ($NoLogs) {
    Write-Status "Running without log redirection..." -Color Gray
    Invoke-Expression "& `"$pythonExe`" $schedulerArgs"
    return
}

if ($Detach) {
    Write-Status "Starting in background (reload disabled for Windows stability)..." -Color Green
    Start-Process -FilePath $pythonExe `
                  -ArgumentList $schedulerArgs `
                  -RedirectStandardOutput $logFile `
                  -RedirectStandardError  "$logFile.err" `
                  -NoNewWindow
    Write-Status "Scheduler started. Logs: $logFile" -Color Green
} else {
    Write-Status "Starting (Ctrl+C to stop)..." -Color Green
    try {
        Invoke-Expression "& `"$pythonExe`" $schedulerArgs" 2>&1 | Tee-Object -FilePath $logFile
    } catch {
        Write-Status "Scheduler stopped." -Color Yellow
    }
}
