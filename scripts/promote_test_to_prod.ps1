[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$SkipTestDeploy,
    [switch]$SkipTestHealthCheck,
    [switch]$SkipProdMigrations,
    [switch]$SkipProdHealthCheck,
    [int]$HealthTimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$testProject = "inkandquill-test"
$prodProject = "inkandquill-prod"
$testComposeArgs = @("-p", $testProject, "-f", "docker-compose.yml", "-f", "docker-compose.test.yml")
$prodComposeArgs = @("-p", $prodProject, "-f", "docker-compose.yml", "-f", "docker-compose.prod.yml")
$testGatewayUrl = "http://localhost:8082/health"
$prodGatewayUrl = "http://localhost:8083/health"

function Invoke-Compose {
    param(
        [string[]]$ComposeArgs
    )

    & docker compose @ComposeArgs
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose command failed: docker compose $($ComposeArgs -join ' ')"
    }
}

function Wait-ForHttp200 {
    param(
        [string]$Url,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
            if ($response.StatusCode -eq 200) {
                return
            }
        }
        catch {
        }

        Start-Sleep -Seconds 5
    }

    throw "Timed out waiting for healthy response from $Url"
}

function Get-GitRevision {
    $revision = (& git rev-parse --short HEAD 2>$null)
    if ($LASTEXITCODE -eq 0) {
        return $revision.Trim()
    }

    return "unknown"
}

Set-Location $repoRoot

$revision = Get-GitRevision
Write-Host "Promoting current workspace revision: $revision"

if (-not $SkipTestDeploy) {
    $testUpArgs = $testComposeArgs + @("up", "--build", "-d")
    if ($PSCmdlet.ShouldProcess("test stack", "Build and start")) {
        Invoke-Compose -ComposeArgs $testUpArgs
    }
}

if (-not $SkipTestHealthCheck) {
    if ($PSCmdlet.ShouldProcess($testGatewayUrl, "Wait for test health")) {
        Wait-ForHttp200 -Url $testGatewayUrl -TimeoutSeconds $HealthTimeoutSeconds
    }
}

if (-not $SkipProdMigrations) {
    $prodMigrationArgs = $prodComposeArgs + @("run", "--rm", "--no-deps", "backend", "alembic", "upgrade", "head")
    if ($PSCmdlet.ShouldProcess("prod database", "Apply migrations")) {
        Invoke-Compose -ComposeArgs $prodMigrationArgs
    }
}

$prodUpArgs = $prodComposeArgs + @("up", "--build", "-d")
if ($PSCmdlet.ShouldProcess("prod stack", "Build and start")) {
    Invoke-Compose -ComposeArgs $prodUpArgs
}

if (-not $SkipProdHealthCheck) {
    if ($PSCmdlet.ShouldProcess($prodGatewayUrl, "Wait for prod health")) {
        Wait-ForHttp200 -Url $prodGatewayUrl -TimeoutSeconds $HealthTimeoutSeconds
    }
}

Write-Host "Promotion completed successfully."
