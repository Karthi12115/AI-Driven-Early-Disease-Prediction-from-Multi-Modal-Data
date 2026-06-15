$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LocalAppUrl = "http://localhost:8000"

Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Write-Host "Checking backend packages..." -ForegroundColor Cyan
& $Python -m pip install fastapi uvicorn pytest | Out-Host

Write-Host "Starting full app on $LocalAppUrl ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$ProjectRoot`"; .\.venv\Scripts\Activate.ps1; python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload"
)

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Local app link: $LocalAppUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "For different Wi-Fi / mobile data:" -ForegroundColor Green
Write-Host "1. Open a NEW terminal."
Write-Host "2. Run this command if cloudflared is installed:" -ForegroundColor Yellow
Write-Host "   cloudflared tunnel --url http://localhost:8000" -ForegroundColor Yellow
Write-Host "3. Copy the https://...trycloudflare.com link printed by cloudflared."
Write-Host "4. Open that HTTPS link on your mobile from any network."
Write-Host ""
Write-Host "If cloudflared is not installed, install Cloudflare Tunnel first, then run the command above."

Start-Process $LocalAppUrl
