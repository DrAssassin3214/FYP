# Route the Claude Code CLI through a local OmniRoute gateway (reversible).
#   .\setup_omniroute.ps1            test the gateway, then set the two user environment variables
#   .\setup_omniroute.ps1 -Undo      remove them again
# Needs OmniRoute already running (default http://localhost:20128) and your OmniRoute key (Dashboard > Endpoints).
param([string]$BaseUrl = "http://localhost:20128", [switch]$Undo)

if ($Undo) {
  [Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $null, "User")
  [Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", $null, "User")
  Write-Host "Removed ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN. Open a new terminal; Claude Code is back to normal."
  return
}

$secure = Read-Host "Paste your OmniRoute key (input hidden)" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
if (-not $key) { Write-Host "No key entered. Nothing changed."; return }

Write-Host "Testing $BaseUrl/v1/messages ..."
$body = '{"model":"auto","max_tokens":20,"messages":[{"role":"user","content":"Reply with OK"}]}'
try {
  $r = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/messages" -TimeoutSec 60 -Body $body -ContentType "application/json" `
        -Headers @{ "x-api-key" = $key; "anthropic-version" = "2023-06-01" }
  Write-Host "Gateway answered in the Anthropic format. Reply: $($r | ConvertTo-Json -Depth 4 -Compress)"
} catch {
  Write-Host "The gateway did not accept an Anthropic-style request: $($_.Exception.Message)"
  Write-Host "Nothing changed. OmniRoute may not support Claude Code directly; check its docs before forcing it."
  return
}

[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $BaseUrl, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", $key, "User")
Write-Host "Set ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN for your user. Open a NEW terminal and run: claude"
Write-Host "Undo any time with: .\setup_omniroute.ps1 -Undo"
