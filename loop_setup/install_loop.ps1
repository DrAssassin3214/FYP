# Copies the refinement-loop agents and command into this project's .claude folder (run from the FYP folder).
$dst = Join-Path (Get-Location) ".claude"
New-Item -ItemType Directory -Force -Path "$dst\agents","$dst\commands" | Out-Null
Copy-Item "$PSScriptRoot\agents\*.md" "$dst\agents" -Force
Copy-Item "$PSScriptRoot\commands\*.md" "$dst\commands" -Force
Write-Host "Installed agents and /refine-loop into $dst"
Write-Host "Next: omniroute launch   (or just: claude), then type /refine-loop"
