param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoReset,
    [switch]$Detach
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path $PSScriptRoot).Path
$frontendRoot = Join-Path $repoRoot "frontendv1"
$logsRoot = Join-Path $repoRoot "logs"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$resetScript = Join-Path $repoRoot "reset-dev-processes.ps1"
$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"

if (-not (Test-Path $logsRoot)) {
    New-Item -ItemType Directory -Path $logsRoot | Out-Null
}

function Write-Status {
    param([string]$Message)
    Write-Host $Message
}

function New-RunLogFile {
    param(
        [string]$Prefix,
        [string]$Suffix
    )

    $fileName = "{0}-{1}.{2}.log" -f $Prefix, $runStamp, $Suffix
    $path = Join-Path $logsRoot $fileName
    New-Item -ItemType File -Path $path -Force | Out-Null
    return $path
}

if ($BackendOnly -and $FrontendOnly) {
    throw "Use either -BackendOnly or -FrontendOnly, not both."
}

if (-not $NoReset) {
    Write-Status "Resetting existing backend/frontend dev processes..."
    & powershell -ExecutionPolicy Bypass -File $resetScript
}

$startBackend = -not $FrontendOnly
$startFrontend = -not $BackendOnly

if ($startBackend) {
    if (-not (Test-Path $pythonExe)) {
        throw "Backend interpreter not found at $pythonExe"
    }

    $backendStdout = New-RunLogFile -Prefix "backend-dev" -Suffix "out"
    $backendStderr = New-RunLogFile -Prefix "backend-dev" -Suffix "err"

    Write-Status "Starting backend on http://localhost:8000 ..."
    $backendProcess = Start-Process `
        -FilePath $pythonExe `
        -ArgumentList @(
            "-m", "uvicorn",
            "app.main:app",
            "--host", "localhost",
            "--port", "8000",
            "--log-level", "debug"
        ) `
        -WorkingDirectory $repoRoot `
        -RedirectStandardOutput $backendStdout `
        -RedirectStandardError $backendStderr `
        -PassThru

    Write-Status ("Backend PID: {0}" -f $backendProcess.Id)
    Write-Status ("Backend logs: {0}" -f $backendStdout)
}

if ($startFrontend) {
    $frontendStdout = New-RunLogFile -Prefix "frontend-dev" -Suffix "out"
    $frontendStderr = New-RunLogFile -Prefix "frontend-dev" -Suffix "err"

    Write-Status "Starting frontend on http://localhost:3001 ..."
    $frontendProcess = Start-Process `
        -FilePath "npm.cmd" `
        -ArgumentList @("run", "dev", "--", "--port", "3001") `
        -WorkingDirectory $frontendRoot `
        -RedirectStandardOutput $frontendStdout `
        -RedirectStandardError $frontendStderr `
        -PassThru

    Write-Status ("Frontend PID: {0}" -f $frontendProcess.Id)
    Write-Status ("Frontend logs: {0}" -f $frontendStdout)
}

Write-Status ""
Write-Status "Started requested dev services."
Write-Status "Backend URL: http://localhost:8000"
Write-Status "Frontend URL: http://localhost:3001"

$tailFiles = @()
if ($startBackend) {
    $tailFiles += $backendStdout
    $tailFiles += $backendStderr
}
if ($startFrontend) {
    $tailFiles += $frontendStdout
    $tailFiles += $frontendStderr
}

if (-not $Detach -and $tailFiles.Count -gt 0) {
    Write-Status ""
    Write-Status "Streaming logs. Press Ctrl+C to stop log tailing. Processes will continue running."
    Get-Content -Path $tailFiles -Wait -Tail 0
}
