<#
.SYNOPSIS
    Restores a .sql dump file into a local PostgreSQL database.

.DESCRIPTION
    Uses a Docker postgres client so psql does not need to be installed locally.
    Drops and recreates the target database before restoring.

.PARAMETER BackupFile
    Path to the .sql dump file. Required.

.PARAMETER DbHost
    Target host. Default: localhost (mapped to host.docker.internal inside Docker).

.PARAMETER Port
    Target PostgreSQL port. Default: 5432.

.PARAMETER User
    PostgreSQL user. Falls back to POSTGRES_USER in .env.

.PARAMETER Password
    PostgreSQL password. Falls back to POSTGRES_PASSWORD in .env.

.PARAMETER Database
    Target database name. Falls back to POSTGRES_DB in .env.

.PARAMETER Force
    Skip the confirmation prompt before dropping the target database.

.EXAMPLE
    .\scripts\restore_postgres_backup.ps1 -BackupFile runtime\artifacts\db-backups\inkquill_db_20260408_120000.sql

.EXAMPLE
    .\scripts\restore_postgres_backup.ps1 -BackupFile .\mybackup.sql -Database inkquill_db_test -Force
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,

    [string]$DbHost   = "localhost",
    [int]$Port        = 5432,
    [string]$User,
    [string]$Password,
    [string]$Database,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Get-DotEnvValue {
    param([string]$Name, [string]$Default = "")

    $envPath = Join-Path $RepoRoot ".env"
    if (-not (Test-Path $envPath)) { return $Default }

    foreach ($line in Get-Content $envPath) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) { continue }
        $idx = $trimmed.IndexOf("=")
        if ($idx -lt 1) { continue }
        $key   = $trimmed.Substring(0, $idx).Trim()
        $value = $trimmed.Substring($idx + 1).Trim().Trim('"')
        if ($key -eq $Name) { return $value }
    }

    return $Default
}

function Invoke-DockerPsql {
    param([string]$Db, [string]$Sql)

    & docker run --rm `
        --add-host=host.docker.internal:host-gateway `
        -e "PGPASSWORD=$Password" `
        -v "${RepoRoot}:/workspace" `
        -w /workspace `
        postgres:16-alpine `
        psql -v ON_ERROR_STOP=1 `
            -h $DockerHost -p $Port -U $User `
            -d $Db -tAc $Sql

    if ($LASTEXITCODE -ne 0) { throw "psql command failed." }
}

# ---------------------------------------------------------------------------
# Resolve paths and defaults
# ---------------------------------------------------------------------------
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $PSBoundParameters.ContainsKey("User")     -or [string]::IsNullOrWhiteSpace($User))     { $User     = Get-DotEnvValue "POSTGRES_USER" }
if (-not $PSBoundParameters.ContainsKey("Password") -or [string]::IsNullOrWhiteSpace($Password)) { $Password = Get-DotEnvValue "POSTGRES_PASSWORD" }
if (-not $PSBoundParameters.ContainsKey("Database") -or [string]::IsNullOrWhiteSpace($Database)) { $Database = Get-DotEnvValue "POSTGRES_DB" }

if ([string]::IsNullOrWhiteSpace($User))     { throw "-User is required (or set POSTGRES_USER in .env)" }
if ([string]::IsNullOrWhiteSpace($Password)) { throw "-Password is required (or set POSTGRES_PASSWORD in .env)" }
if ([string]::IsNullOrWhiteSpace($Database)) { throw "-Database is required (or set POSTGRES_DB in .env)" }

$BackupFile = Resolve-Path $BackupFile
if (-not (Test-Path $BackupFile)) { throw "Backup file not found: $BackupFile" }

$DockerHost  = if ($DbHost -in @("localhost", "127.0.0.1", "::1")) { "host.docker.internal" } else { $DbHost }
$BackupFileRel = (Resolve-Path $BackupFile).Path.Replace($RepoRoot, "").TrimStart('\').TrimStart('/')

Write-Host ""
Write-Host "Backup file : $BackupFile"
Write-Host "Target host : ${DbHost}:${Port}"
Write-Host "Target DB   : $Database"
Write-Host "User        : $User"
Write-Host ""

if (-not $Force) {
    $confirm = Read-Host "This will DROP and recreate '$Database'. Continue? [y/N]"
    if ($confirm -notmatch '^[Yy]') {
        Write-Host "Aborted."
        exit 0
    }
}

# ---------------------------------------------------------------------------
# Drop, recreate, and restore
# ---------------------------------------------------------------------------
Write-Host "Dropping database '$Database' (if exists) ..."
& docker run --rm `
    --add-host=host.docker.internal:host-gateway `
    -e "PGPASSWORD=$Password" `
    -v "${RepoRoot}:/workspace" `
    -w /workspace `
    postgres:16-alpine `
    psql -v ON_ERROR_STOP=1 `
        -h $DockerHost -p $Port -U $User `
        -d postgres -tAc "DROP DATABASE IF EXISTS ""$Database"";"

if ($LASTEXITCODE -ne 0) { throw "Failed to drop database." }

Write-Host "Creating database '$Database' ..."
& docker run --rm `
    --add-host=host.docker.internal:host-gateway `
    -e "PGPASSWORD=$Password" `
    -v "${RepoRoot}:/workspace" `
    -w /workspace `
    postgres:16-alpine `
    psql -v ON_ERROR_STOP=1 `
        -h $DockerHost -p $Port -U $User `
        -d postgres -tAc "CREATE DATABASE ""$Database"";"

if ($LASTEXITCODE -ne 0) { throw "Failed to create database." }

Write-Host "Restoring dump ..."
& docker run --rm `
    --add-host=host.docker.internal:host-gateway `
    -e "PGPASSWORD=$Password" `
    -v "${RepoRoot}:/workspace" `
    -w /workspace `
    postgres:16-alpine `
    sh -lc "psql -v ON_ERROR_STOP=1 -h '$DockerHost' -p '$Port' -U '$User' -d '$Database' < '/workspace/$($BackupFileRel.Replace('\', '/'))'"

if ($LASTEXITCODE -ne 0) { throw "Restore failed." }

Write-Host ""
Write-Host "Restore complete. Database '$Database' is ready."
Write-Host ""
