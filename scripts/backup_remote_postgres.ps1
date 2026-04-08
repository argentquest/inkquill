<#
.SYNOPSIS
    Dumps a PostgreSQL database from a remote host to a local .sql file.

.DESCRIPTION
    Uses a Docker postgres client so pg_dump does not need to be installed locally.
    The dump is saved to artifacts\db-backups\<dbname>_<timestamp>.sql

.PARAMETER Host
    Remote host name or IP address. Required.

.PARAMETER Port
    Remote PostgreSQL port. Default: 5432.

.PARAMETER User
    PostgreSQL user. Falls back to POSTGRES_USER in .env.

.PARAMETER Password
    PostgreSQL password. Falls back to POSTGRES_PASSWORD in .env.

.PARAMETER Database
    Database name to dump. Falls back to POSTGRES_DB in .env.

.PARAMETER OutDir
    Output directory for the dump file. Default: artifacts\db-backups

.EXAMPLE
    .\scripts\backup_remote_postgres.ps1 -Host 192.168.1.50

.EXAMPLE
    .\scripts\backup_remote_postgres.ps1 -Host 192.168.1.50 -Database mydb -User postgres -Password secret
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Host,

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

$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFile   = Join-Path $OutDir "${Database}_${timestamp}.sql"
$dumpFileRel = $dumpFile.Replace($RepoRoot, "").TrimStart('\').TrimStart('/')

Write-Host ""
Write-Host "Remote host : ${Host}:${Port}"
Write-Host "Database    : $Database"
Write-Host "User        : $User"
Write-Host "Output file : $dumpFile"
Write-Host ""

# ---------------------------------------------------------------------------
# Run pg_dump via a Docker postgres client
# (avoids needing psql/pg_dump installed on this machine)
# ---------------------------------------------------------------------------
$dockerArgs = @(
    "run", "--rm",
    "-e", "PGPASSWORD=$Password",
    "-v", "${RepoRoot}:/workspace",
    "-w", "/workspace",
    "postgres:16-alpine",
    "sh", "-lc",
    "pg_dump -h '$Host' -p '$Port' -U '$User' -d '$Database' --no-owner --no-privileges > '/workspace/$($dumpFileRel.Replace('\', '/'))'"
)

Write-Host "Running pg_dump ..."
& docker @dockerArgs

if ($LASTEXITCODE -ne 0) {
    throw "pg_dump failed (exit code $LASTEXITCODE). Check host, credentials, and network access."
}

$size = (Get-Item $dumpFile).Length / 1MB
Write-Host ""
Write-Host ("Backup complete: {0}  ({1:N1} MB)" -f $dumpFile, $size)
Write-Host ""
Write-Host "To restore into your local dev database run:"
Write-Host "  .\scripts\restore_postgres_backup.ps1 -BackupFile `"$dumpFile`""
Write-Host ""
