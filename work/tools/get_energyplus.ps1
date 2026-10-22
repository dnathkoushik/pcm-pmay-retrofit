# Download the portable (no-install) EnergyPlus 26.2.0 build used in this project.
#   powershell -ExecutionPolicy Bypass -File work/tools/get_energyplus.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$url = "https://github.com/NatLabRockies/EnergyPlus/releases/download/v26.2.0/EnergyPlus-26.2.0-4bd7a1f26f-Windows-x86_64.zip"
$zip = Join-Path $here "EnergyPlus-26.2.0.zip"
if (Test-Path (Join-Path $here "EnergyPlus-26.2.0\energyplus.exe")) { Write-Host "EnergyPlus already present"; exit 0 }
Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $here
Rename-Item (Join-Path $here "EnergyPlus-26.2.0-4bd7a1f26f-Windows-x86_64") "EnergyPlus-26.2.0"
Remove-Item $zip
Write-Host "EnergyPlus 26.2.0 ready in $here\EnergyPlus-26.2.0"
