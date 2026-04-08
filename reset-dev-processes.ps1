param(
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path $PSScriptRoot).Path
$frontendRoot = Join-Path $repoRoot "frontendv1"

function Write-Status {
    param([string]$Message)

    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Get-ProcessDetails {
    Get-CimInstance Win32_Process | Select-Object ProcessId, Name, CommandLine
}

function Stop-MatchingProcesses {
    param(
        [string]$Label,
        [scriptblock]$Predicate
    )

    $matches = Get-ProcessDetails | Where-Object { & $Predicate $_ }
    $stopped = @{}

    foreach ($process in $matches) {
        if ($process.ProcessId -eq $PID) {
            continue
        }

        if ($stopped.ContainsKey($process.ProcessId)) {
            continue
        }

        Write-Status ("Stopping {0}: PID {1} ({2})" -f $Label, $process.ProcessId, $process.Name)
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
        $stopped[$process.ProcessId] = $true
    }

    return $stopped.Keys
}

function Stop-PortOwners {
    param(
        [int[]]$Ports,
        [scriptblock]$Predicate
    )

    $processIndex = @{}
    foreach ($process in Get-ProcessDetails) {
        $processIndex[[int]$process.ProcessId] = $process
    }

    $stopped = @{}

    foreach ($port in $Ports) {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($connection in $connections) {
            $process = $processIndex[[int]$connection.OwningProcess]
            if (-not $process) {
                continue
            }

            if ($process.ProcessId -eq $PID) {
                continue
            }

            if (-not (& $Predicate $process)) {
                continue
            }

            if ($stopped.ContainsKey($process.ProcessId)) {
                continue
            }

            Write-Status ("Stopping port owner: PID {0} on port {1} ({2})" -f $process.ProcessId, $port, $process.Name)
            Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
            $stopped[$process.ProcessId] = $true
        }
    }

    return $stopped.Keys
}

$backendMatcher = {
    param($process)
    $cmd = [string]$process.CommandLine
    if ([string]::IsNullOrWhiteSpace($cmd)) { return $false }

    return (
        $cmd -like "*$repoRoot*" -and
        (
            $cmd -like "*-m uvicorn*" -or
            $cmd -like "*app.main:app*"
        )
    )
}

$frontendMatcher = {
    param($process)
    $cmd = [string]$process.CommandLine
    if ([string]::IsNullOrWhiteSpace($cmd)) { return $false }

    return (
        $cmd -like "*$frontendRoot*" -and
        (
            $cmd -like "*next dev*" -or
            $cmd -like "*npm run dev*" -or
            $cmd -like "*node*frontendv1*"
        )
    )
}

Write-Status "Resetting backend and frontend dev processes for this workspace..."

$stoppedBackend = Stop-MatchingProcesses -Label "backend process" -Predicate $backendMatcher
$stoppedFrontend = Stop-MatchingProcesses -Label "frontend process" -Predicate $frontendMatcher
$stoppedPortOwners = Stop-PortOwners -Ports @(8000, 3001) -Predicate {
    param($process)
    (& $backendMatcher $process) -or (& $frontendMatcher $process)
}

$totalStopped = @(
    @($stoppedBackend) + @($stoppedFrontend) + @($stoppedPortOwners) | Sort-Object -Unique
)

if ($totalStopped.Count -eq 0) {
    Write-Status "No matching backend or frontend dev processes were running."
} else {
    Write-Status ("Stopped {0} process(es)." -f $totalStopped.Count)
}
