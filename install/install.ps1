<#
Roblox Apex installer for Windows (PowerShell 5.1+ or PowerShell 7)

  .\install\install.ps1 -Project C:\path\to\MyGame     # install into MyGame\.claude\skills (recommended)
  .\install\install.ps1 -User                          # install into %USERPROFILE%\.claude\skills
  .\install\install.ps1 -Project C:\path\to\MyGame -Uninstall
  .\install\install.ps1 -User -Uninstall

Re-running is the update path. Only directories recorded in the marker file are ever removed.
If script execution is blocked:  powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -User
#>
param(
  [string]$Project,
  [switch]$User,
  [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
$Src = Join-Path (Split-Path -Parent $PSScriptRoot) '.claude\skills'
$Marker = '.roblox-apex-installed'

if ($User) { $Dest = Join-Path $env:USERPROFILE '.claude\skills' }
elseif ($Project) {
  if (-not (Test-Path $Project -PathType Container)) { throw "'$Project' is not a directory" }
  $Dest = Join-Path (Resolve-Path $Project).Path '.claude\skills'
}
else { Get-Help $MyInvocation.MyCommand.Path; exit 1 }

$versionLine = Select-String -Path (Join-Path $Src 'roblox\SKILL.md') -Pattern '^\s+version:\s*(\S+)' | Select-Object -First 1
$Version = $versionLine.Matches[0].Groups[1].Value
$MarkerPath = Join-Path $Dest $Marker

function Remove-Previous {
  if (Test-Path $MarkerPath) {
    Get-Content $MarkerPath | Select-Object -Skip 1 | ForEach-Object {
      if ($_ -match '^roblox(-[a-z-]+)?$') {
        $p = Join-Path $Dest $_
        if (Test-Path $p) { Remove-Item -Recurse -Force $p }
      }
    }
    Remove-Item -Force $MarkerPath
  }
}

if ($Uninstall) {
  if (-not (Test-Path $MarkerPath)) { Write-Host "Roblox Apex is not installed in $Dest"; exit 0 }
  Remove-Previous
  Write-Host "Removed Roblox Apex from $Dest (.apex\ and CLAUDE.md were left untouched)."
  exit 0
}

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Remove-Previous
$skills = Get-ChildItem -Path $Src -Directory | Where-Object { $_.Name -match '^roblox(-[a-z-]+)?$' }
foreach ($s in $skills) {
  if (Test-Path (Join-Path $Dest $s.Name)) { throw "$Dest\$($s.Name) exists and was not installed by Roblox Apex; move it and retry." }
}
Set-Content -Path $MarkerPath -Value $Version
foreach ($s in $skills) {
  Copy-Item -Recurse -Force $s.FullName (Join-Path $Dest $s.Name)
  Add-Content -Path $MarkerPath -Value $s.Name
}
Write-Host "Installed Roblox Apex $Version ($($skills.Count) skills) into $Dest"
Write-Host "Next: open Claude Code in your project and run /roblox-status, then /roblox-init."
