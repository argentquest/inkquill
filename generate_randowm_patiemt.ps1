# generate_randowm_patiemt.ps1
# Runs the care circle provider test against a randomly selected active patient.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

python scripts/test_care_circle_providers.py
