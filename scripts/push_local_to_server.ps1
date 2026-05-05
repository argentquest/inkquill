<#
.SYNOPSIS
    Dumps the local dev database and uploads, then restores them on the remote Ubuntu server.

.DESCRIPTION
    Full workflow:
      1. Dump the local dev PostgreSQL (default: port 5433, dev compose credentials).
      2. rsync/scp the local upload files to the server for each target environment.
      3. SCP the dump to the server.
      4. SSH to the server and run restore_dump_to_env.sh for each target environment.

    Requirements (Windows):
      - Docker Desktop running locally (for pg_dump via container).
      - OpenSSH client: ssh, scp (built into Windows 10/11).
      - rsync optional — falls back to scp if rsync is not available.

.PARAMETER Server
    SSH connection string for the Ubuntu server, e.g. deploy@192.168.1.100.
    Can also be an SSH alias from ~/.ssh/config.

.PARAMETER Environments
    Which environments to seed on the server. Default: @("test", "prod").

.PARAMETER DevPort
    Local dev database host port. Default: 5433 (docker-compose.dev.yml).

.PARAMETER DevUser
    Local dev database user. Default: inkandquill_dev.

.PARAMETER DevPassword
    Local dev database password. Default: inkandquill_dev_password.

.PARAMETER DevDatabase
    Local dev database name. Default: inkandquill_dev.

.PARAMETER LocalUploadsPath
    Local uploads directory to sync. Default: runtime\data\uploads relative to repo root.

.PARAMETER RemoteRepoPath
    Absolute path to the repo checkout on the server. Default: ~/inkquill.

.PARAMETER RemoteDataRoot
    Base path for server data. Environments are expected at
    <RemoteDataRoot>/test and <RemoteDataRoot>/prod. Default: /srv/care-circle.

.PARAMETER SkipDatabase
    Skip the database dump and restore step.

.PARAMETER SkipUploads
    Skip syncing the uploads directory.

.PARAMETER SshIdentity
    Path to the SSH private key file (-i flag). Optional.

.EXAMPLE
    # Full seed to both test and prod:
    .\scripts\push_local_to_server.ps1 -Server deploy@192.168.1.100

.EXAMPLE
    # Database only, test env only:
    .\scripts\push_local_to_server.ps1 -Server deploy@192.168.1.100 -Environments test -SkipUploads

.EXAMPLE
    # Uploads only, with a specific SSH key:
    .\scripts\push_local_to_server.ps1 -Server deploy@myhost -SkipDatabase -SshIdentity ~/.ssh/id_deploy
#>

[CmdletBinding(SupportsShouldProcess = $true)]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingPlainTextForPassword', 'DevPassword',
    Justification = 'Password passed only as Docker PGPASSWORD env var, never written to disk.')]
param(
    [Parameter(Mandatory = $true)]
    [string]$Server,

    [string[]]$Environments = @("test", "prod"),

    [int]$DevPort = 5433,
    [string]$DevUser = "inkandquill_dev",
    [string]$DevPassword = "inkandquill_dev_password",
    [string]$DevDatabase = "inkandquill_dev",

    [string]$LocalUploadsPath,
    [string]$RemoteRepoPath = "~/inkquill",
    [string]$RemoteDataRoot = "/srv/care-circle",

    [switch]$SkipDatabase,
    [switch]$SkipUploads,

    [string]$SshIdentity
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($LocalUploadsPath)) {
    $LocalUploadsPath = Join-Path $RepoRoot "runtime\data\uploads"
}

$SshArgs = @()
if (-not [string]::IsNullOrWhiteSpace($SshIdentity)) {
    $SshArgs += @("-i", $SshIdentity)
}

function Invoke-Ssh {
    param([string[]]$RemoteCmd)
    & ssh @SshArgs $Server @RemoteCmd
    if ($LASTEXITCODE -ne 0) { throw "SSH command failed: $($RemoteCmd -join ' ')" }
}

function Invoke-Scp {
    param([string]$Source, [string]$Dest, [switch]$Recurse)
    $scpArgs = @()
    if ($Recurse) { $scpArgs += "-r" }
    $scpArgs += @SshArgs
    $scpArgs += @($Source, $Dest)
    & scp @scpArgs
    if ($LASTEXITCODE -ne 0) { throw "SCP failed: $Source -> $Dest" }
}

# ---------------------------------------------------------------------------
# Step 1: Dump the local dev database
# ---------------------------------------------------------------------------
if (-not $SkipDatabase) {
    Write-Host ""
    Write-Host "==> Dumping local dev database ($DevDatabase @ localhost:$DevPort) ..."

    $artifactDir = Join-Path $RepoRoot "runtime\artifacts\db-backups"
    New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $dumpFile = Join-Path $artifactDir "${DevDatabase}_${timestamp}.sql"
    $dumpFileRel = $dumpFile.Replace($RepoRoot, "").TrimStart('\').TrimStart('/')

    & docker run --rm `
        --add-host=host.docker.internal:host-gateway `
        -e "PGPASSWORD=$DevPassword" `
        -v "${RepoRoot}:/workspace" `
        -w /workspace `
        postgres:16-alpine `
        sh -lc "pg_dump -h host.docker.internal -p '$DevPort' -U '$DevUser' -d '$DevDatabase' --no-owner --no-privileges > '/workspace/$($dumpFileRel.Replace('\', '/'))'"

    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump failed. Is the dev database container running? (docker compose -f infra/docker-compose.dev.yml up db)"
    }

    $sizeMB = [math]::Round((Get-Item $dumpFile).Length / 1MB, 1)
    Write-Host "    Dump saved: $dumpFile ($sizeMB MB)"

    # Copy the dump to the server
    $remoteDump = "/tmp/${DevDatabase}_${timestamp}.sql"
    Write-Host "==> Copying dump to $Server:$remoteDump ..."
    Invoke-Scp -Source $dumpFile -Dest "${Server}:${remoteDump}"

    # Restore on server for each environment
    foreach ($env in $Environments) {
        if ($PSCmdlet.ShouldProcess("$Server [$env]", "Restore database")) {
            Write-Host ""
            Write-Host "==> Restoring into '$env' on $Server ..."
            Invoke-Ssh -RemoteCmd @(
                "bash", "$RemoteRepoPath/scripts/restore_dump_to_env.sh",
                "-e", $env,
                "-f", $remoteDump
            )
        }
    }

    # Clean up remote dump file
    Write-Host "==> Removing remote dump file ..."
    Invoke-Ssh -RemoteCmd @("rm", "-f", $remoteDump)
}

# ---------------------------------------------------------------------------
# Step 2: Sync upload files
# ---------------------------------------------------------------------------
if (-not $SkipUploads) {
    if (-not (Test-Path $LocalUploadsPath)) {
        Write-Host ""
        Write-Host "WARNING: Local uploads directory not found: $LocalUploadsPath — skipping upload sync."
    } else {
        $localFiles = Get-ChildItem $LocalUploadsPath -Recurse -File
        Write-Host ""
        Write-Host "==> Syncing uploads ($($localFiles.Count) files) ..."

        # Use rsync if available, fall back to scp
        $rsyncAvailable = $null -ne (Get-Command rsync -ErrorAction SilentlyContinue)

        $localUploadsFwd = $LocalUploadsPath.Replace('\', '/')

        foreach ($env in $Environments) {
            $remoteUploads = "${RemoteDataRoot}/${env}/runtime/data/uploads/"
            Write-Host "    -> $Server:$remoteUploads"

            if ($PSCmdlet.ShouldProcess("$Server [$env]", "Sync uploads")) {
                # Ensure remote directory exists
                Invoke-Ssh -RemoteCmd @("mkdir", "-p", $remoteUploads)

                if ($rsyncAvailable) {
                    $rsyncArgs = @("-az", "--progress")
                    if (-not [string]::IsNullOrWhiteSpace($SshIdentity)) {
                        $rsyncArgs += @("-e", "ssh -i $SshIdentity")
                    }
                    $rsyncArgs += @("$localUploadsFwd/", "${Server}:${remoteUploads}")
                    & rsync @rsyncArgs
                    if ($LASTEXITCODE -ne 0) { throw "rsync failed for $env uploads" }
                } else {
                    # scp -r copies the directory contents
                    Invoke-Scp -Source "$localUploadsFwd/" -Dest "${Server}:${remoteUploads}" -Recurse
                }
            }
        }
    }
}

Write-Host ""
Write-Host "Done. Environments seeded: $($Environments -join ', ')"
Write-Host ""
Write-Host "Next step — bring up the full stack on the server:"
Write-Host "  ssh $Server"
Write-Host "  cd $RemoteRepoPath"
foreach ($env in $Environments) {
    Write-Host "  bash scripts/deploy_care_circle_docker_host.sh -e $env -a up -b -d --auto-migrate"
}
