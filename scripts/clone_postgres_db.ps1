param(
    [string]$SourceDb,
    [string[]]$TargetDbs,
    [string]$DbHost,
    [int]$DbPort,
    [string]$DbUser,
    [string]$DbPassword,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Get-EnvValue {
    param(
        [string]$Name,
        [string]$Default = ""
    )

    $value = [Environment]::GetEnvironmentVariable($Name)
    if (-not [string]::IsNullOrWhiteSpace($value)) {
        return $value.Trim('"')
    }

    return $Default
}

function Get-DotEnvMap {
    param(
        [string]$Path
    )

    $map = @{}

    if (-not (Test-Path $Path)) {
        return $map
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $separatorIndex = $trimmed.IndexOf("=")
        if ($separatorIndex -lt 1) {
            continue
        }

        $key = $trimmed.Substring(0, $separatorIndex).Trim()
        $value = $trimmed.Substring($separatorIndex + 1).Trim().Trim('"')
        $map[$key] = $value
    }

    return $map
}

function Invoke-DockerPostgresClient {
    param(
        [string[]]$ClientArgs
    )

    $dockerArgs = @(
        "run",
        "--rm",
        "--add-host=host.docker.internal:host-gateway",
        "-e", "PGPASSWORD=$script:ResolvedDbPassword",
        "-v", "${script:RepoRoot}:/workspace",
        "-w", "/workspace",
        "postgres:16-alpine"
    ) + $ClientArgs

    & docker @dockerArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Docker postgres client command failed."
    }
}

function Invoke-PostgresSql {
    param(
        [string]$Database,
        [string]$Sql
    )

    Invoke-DockerPostgresClient -ClientArgs @(
        "psql",
        "-v", "ON_ERROR_STOP=1",
        "-h", $script:ResolvedDockerHost,
        "-p", "$script:ResolvedDbPort",
        "-U", $script:ResolvedDbUser,
        "-d", $Database,
        "-tAc", $Sql
    )
}

function Test-DatabaseExists {
    param(
        [string]$Database
    )

    $sql = "SELECT 1 FROM pg_database WHERE datname = '$Database';"
    $result = Invoke-PostgresSql -Database "postgres" -Sql $sql
    if ($null -eq $result) {
        return $false
    }

    return (($result | Out-String).Trim() -eq "1")
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DotEnv = Get-DotEnvMap -Path (Join-Path $RepoRoot ".env")
$SourceDb = if ($PSBoundParameters.ContainsKey("SourceDb")) { $SourceDb } else { (Get-EnvValue -Name "POSTGRES_DB" -Default $DotEnv["POSTGRES_DB"]).Trim('"') }
$DbHost = if ($PSBoundParameters.ContainsKey("DbHost")) { $DbHost } else { (Get-EnvValue -Name "POSTGRES_SERVER" -Default $DotEnv["POSTGRES_SERVER"]).Trim('"') }
$DbPort = if ($PSBoundParameters.ContainsKey("DbPort")) { $DbPort } else { [int](Get-EnvValue -Name "POSTGRES_PORT" -Default $DotEnv["POSTGRES_PORT"]) }
$DbUser = if ($PSBoundParameters.ContainsKey("DbUser")) { $DbUser } else { (Get-EnvValue -Name "POSTGRES_USER" -Default $DotEnv["POSTGRES_USER"]).Trim('"') }
$DbPassword = if ($PSBoundParameters.ContainsKey("DbPassword")) { $DbPassword } else { (Get-EnvValue -Name "POSTGRES_PASSWORD" -Default $DotEnv["POSTGRES_PASSWORD"]).Trim('"') }

if (-not $PSBoundParameters.ContainsKey("TargetDbs") -or -not $TargetDbs -or $TargetDbs.Count -eq 0) {
    $defaultTestDb = Get-EnvValue -Name "POSTGRES_TEST_DB" -Default "${SourceDb}_test"
    $defaultProdDb = Get-EnvValue -Name "POSTGRES_PROD_DB" -Default "${SourceDb}_prod"
    $TargetDbs = @($defaultTestDb, $defaultProdDb)
}

if ([string]::IsNullOrWhiteSpace($DbPassword)) {
    throw "POSTGRES_PASSWORD was not provided. Set it in the environment or pass -DbPassword."
}

$ResolvedDbPassword = $DbPassword
$ResolvedDbPort = $DbPort
$ResolvedDbUser = $DbUser
$ResolvedDockerHost = if ($DbHost -in @("localhost", "127.0.0.1", "::1")) { "host.docker.internal" } else { $DbHost }

$artifactDir = Join-Path $RepoRoot "runtime\artifacts\db-clones"
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
$dumpFile = Join-Path $artifactDir "$SourceDb.sql"

if ($TargetDbs -contains $SourceDb) {
    throw "Source database '$SourceDb' cannot also be a target."
}

Write-Host "Source database: $SourceDb"
Write-Host "Target databases: $($TargetDbs -join ', ')"
Write-Host "Database host: ${DbHost}:$DbPort"

if (-not (Test-DatabaseExists -Database $SourceDb)) {
    throw "Source database '$SourceDb' does not exist."
}

foreach ($targetDb in $TargetDbs) {
    if ((Test-DatabaseExists -Database $targetDb) -and -not $Force) {
        throw "Target database '$targetDb' already exists. Re-run with -Force to replace it."
    }
}

Write-Host "Creating dump file $dumpFile"
Invoke-DockerPostgresClient -ClientArgs @(
    "sh",
    "-lc",
    "pg_dump -h '$ResolvedDockerHost' -p '$ResolvedDbPort' -U '$ResolvedDbUser' -d '$SourceDb' --no-owner --no-privileges > '/workspace/runtime/artifacts/db-clones/$SourceDb.sql'"
)

foreach ($targetDb in $TargetDbs) {
    Write-Host "Preparing target database $targetDb"

    if (Test-DatabaseExists -Database $targetDb) {
        Invoke-PostgresSql -Database "postgres" -Sql "DROP DATABASE ""$targetDb"";"
    }

    Invoke-PostgresSql -Database "postgres" -Sql "CREATE DATABASE ""$targetDb"";"

    Write-Host "Restoring dump into $targetDb"
    Invoke-DockerPostgresClient -ClientArgs @(
        "sh",
        "-lc",
        "psql -v ON_ERROR_STOP=1 -h '$ResolvedDockerHost' -p '$ResolvedDbPort' -U '$ResolvedDbUser' -d '$targetDb' < '/workspace/runtime/artifacts/db-clones/$SourceDb.sql'"
    )
}

Write-Host "Database clone completed successfully."
