[CmdletBinding()]
param(
    [ValidateSet("test", "prod")]
    [string]$Environment,

    [ValidateSet("up", "down", "restart", "logs", "migrate", "config", "ps", "pull")]
    [string]$Action = "up",

    [switch]$Build,
    [switch]$Detached,
    [switch]$AutoMigrate,
    [switch]$VerifyFrontendBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$deployRoot = Join-Path $repoRoot "deployments/docker-host"
$hostEnvFile = Join-Path $deployRoot "env/$Environment.host.env"
$baseCompose = Join-Path $deployRoot "docker-compose.base.yml"
$envCompose = Join-Path $deployRoot "docker-compose.$Environment.yml"
$frontendRoot = Join-Path $repoRoot "frontendv1"

if (-not (Test-Path $hostEnvFile)) {
    throw "Host env file not found: $hostEnvFile. Copy the .example file first."
}

function Get-EnvValue {
    param(
        [string]$Path,
        [string]$Key
    )

    foreach ($line in Get-Content $Path) {
        if ($line -match "^\s*$Key=(.*)$") {
            return $Matches[1].Trim()
        }
    }
    return $null
}

$runtimeEnvRelative = Get-EnvValue -Path $hostEnvFile -Key "CARE_CIRCLE_RUNTIME_ENV_FILE"
if (-not $runtimeEnvRelative) {
    throw "CARE_CIRCLE_RUNTIME_ENV_FILE is missing from $hostEnvFile"
}

$runtimeEnvFile = Join-Path $deployRoot ($runtimeEnvRelative -replace '^\./', '')
if (-not (Test-Path $runtimeEnvFile)) {
    throw "Runtime env file not found: $runtimeEnvFile. Copy the .example file first."
}

$projectName = Get-EnvValue -Path $hostEnvFile -Key "CARE_CIRCLE_PROJECT_NAME"
if (-not $projectName) {
    throw "CARE_CIRCLE_PROJECT_NAME is missing from $hostEnvFile"
}

$dataRoot = Get-EnvValue -Path $hostEnvFile -Key "CARE_CIRCLE_DATA_ROOT"
if (-not $dataRoot) {
    throw "CARE_CIRCLE_DATA_ROOT is missing from $hostEnvFile"
}

$requiredDirs = @(
    $dataRoot,
    (Join-Path $dataRoot "cache"),
    (Join-Path $dataRoot "logs"),
    (Join-Path $dataRoot "logs/backend"),
    (Join-Path $dataRoot "postgres")
)

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

$composeArgs = @(
    "--project-name", $projectName,
    "--env-file", $hostEnvFile,
    "-f", $baseCompose,
    "-f", $envCompose
)

function Invoke-Compose {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args,

        [string]$FailureMessage = "docker compose command failed"
    )

    & docker compose @Args
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

function Invoke-Migration {
    param(
        [switch]$UseBuild
    )

    $runArgs = $composeArgs + @("run", "--rm", "--no-deps")
    if ($UseBuild) {
        $runArgs += "--build"
    }
    $runArgs += @("backend", "alembic", "upgrade", "head")
    Invoke-Compose -Args $runArgs -FailureMessage "docker compose action failed: migrate"
}

function Invoke-FrontendProductionBuild {
    if (-not (Test-Path $frontendRoot)) {
        throw "Frontend workspace not found: $frontendRoot"
    }

    Push-Location $frontendRoot
    try {
        & npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "frontend production build failed"
        }
    }
    finally {
        Pop-Location
    }
}

Push-Location $deployRoot
try {
    switch ($Action) {
        "up" {
            if ($AutoMigrate -and $Detached) {
                $dbUpArgs = $composeArgs + @("up", "-d", "db")
                Invoke-Compose -Args $dbUpArgs -FailureMessage "docker compose action failed: up"
                Invoke-Migration -UseBuild:$Build
            }

            $cmd = $composeArgs + @("up")
            if ($Build) { $cmd += "--build" }
            if ($Detached) { $cmd += "-d" }
            Invoke-Compose -Args $cmd -FailureMessage "docker compose action failed: up"

            if ($Detached) {
                Invoke-Compose -Args ($composeArgs + @("restart", "gateway")) -FailureMessage "docker compose action failed: restart"
            }

            if ($VerifyFrontendBuild) {
                Invoke-FrontendProductionBuild
            }
        }
        "down" {
            Invoke-Compose -Args ($composeArgs + @("down")) -FailureMessage "docker compose action failed: down"
        }
        "restart" {
            Invoke-Compose -Args ($composeArgs + @("restart")) -FailureMessage "docker compose action failed: restart"
        }
        "logs" {
            & docker compose @composeArgs logs -f
        }
        "migrate" {
            Invoke-Migration
        }
        "config" {
            Invoke-Compose -Args ($composeArgs + @("config")) -FailureMessage "docker compose action failed: config"
        }
        "ps" {
            Invoke-Compose -Args ($composeArgs + @("ps")) -FailureMessage "docker compose action failed: ps"
        }
        "pull" {
            Invoke-Compose -Args ($composeArgs + @("pull")) -FailureMessage "docker compose action failed: pull"
        }
    }
}
finally {
    Pop-Location
}
