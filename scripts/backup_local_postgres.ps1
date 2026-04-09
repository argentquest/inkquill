<#
.SYNOPSIS
    Dumps the local development PostgreSQL database to a .sql file.

.DESCRIPTION
    Runs pg_dump against the local Docker Compose 'db' container using a
    temporary postgres client container.  No local pg_dump installation needed.
    Credentials and database name fall back to values in .env.
    The dump is saved to artifacts\db-backups\<dbname>_<timestamp>.sql

.PARAMETER Port
    PostgreSQL port exposed on localhost. Default: 5432.

.PARAMETER User
    PostgreSQL user. Falls back to POSTGRES_USER in .env.

.PARAMETER Password
    PostgreSQL password. Falls back to POSTGRES_PASSWORD in .env.

.PARAMETER Database
    Database name to dump. Falls back to POSTGRES_DB in .env.

.PARAMETER OutDir
    Output directory. Default: artifacts\db-backups

.EXAMPLE
    .\scripts\backup_local_postgres.ps1

.EXAMPLE
    .\scripts\backup_local_postgres.ps1 -Database inkandquill_test
#>

param(
    [int]$Port = 5432,

    [string]$User,
    [string]$Password,
    [string]$Database,

    [string]$OutDir
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

# ---------------------------------------------------------------------------
# Resolve paths and defaults
# ---------------------------------------------------------------------------
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $PSBoundParameters.ContainsKey("User")     -or [string]::IsNullOrWhiteSpace($User))     { $User     = Get-DotEnvValue "POSTGRES_USER" }
if (-not $PSBoundParameters.ContainsKey("Password") -or [string]::IsNullOrWhiteSpace($Password)) { $Password = Get-DotEnvValue "POSTGRES_PASSWORD" }
if (-not $PSBoundParameters.ContainsKey("Database") -or [string]::IsNullOrWhiteSpace($Database)) { $Database = Get-DotEnvValue "POSTGRES_DB" }
if (-not $PSBoundParameters.ContainsKey("OutDir")   -or [string]::IsNullOrWhiteSpace($OutDir))   { $OutDir   = Join-Path $RepoRoot "artifacts\db-backups" }

if ([string]::IsNullOrWhiteSpace($User))     { throw "-User is required (or set POSTGRES_USER in .env)" }
if ([string]::IsNullOrWhiteSpace($Password)) { throw "-Password is required (or set POSTGRES_PASSWORD in .env)" }
if ([string]::IsNullOrWhiteSpace($Database)) { throw "-Database is required (or set POSTGRES_DB in .env)" }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$timestamp   = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFile    = Join-Path $OutDir "${Database}_${timestamp}.sql"
$dumpFileRel = $dumpFile.Replace($RepoRoot, "").TrimStart('\').TrimStart('/')

Write-Host ""
Write-Host "Host        : localhost:${Port}  (host.docker.internal inside container)"
Write-Host "Database    : $Database"
Write-Host "User        : $User"
Write-Host "Output file : $dumpFile"
Write-Host ""

# ---------------------------------------------------------------------------
# Run pg_dump via a temporary Docker postgres client container.
# host.docker.internal resolves to the Docker host, where the dev db listens.
# ---------------------------------------------------------------------------
$dockerArgs = @(
    "run", "--rm",
    "--add-host=host.docker.internal:host-gateway",
    "-e", "PGPASSWORD=$Password",
    "-v", "${RepoRoot}:/workspace",
    "-w", "/workspace",
    "postgres:16-alpine",
    "sh", "-lc",
    "pg_dump -h host.docker.internal -p '$Port' -U '$User' -d '$Database' --no-owner --no-privileges > '/workspace/$($dumpFileRel.Replace('\', '/'))'"
)

Write-Host "Running pg_dump ..."
& docker @dockerArgs

if ($LASTEXITCODE -ne 0) {
    throw "pg_dump failed (exit code $LASTEXITCODE). Is the 'db' container running?"
}

$size = (Get-Item $dumpFile).Length / 1MB
Write-Host ""
Write-Host ("Backup complete: {0}  ({1:N1} MB)" -f $dumpFile, $size)
Write-Host ""
Write-Host "To restore this backup run:"
Write-Host "  .\scripts\restore_postgres_backup.ps1 -BackupFile `"$dumpFile`""
Write-Host ""
