$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LocalBackendUrl = "http://localhost:8000/api/health"
$LocalFrontendUrl = "http://localhost:5713"
$LanIp = (
    Get-NetIPConfiguration |
    Where-Object { $_.IPv4DefaultGateway -and $_.NetAdapter.Status -eq "Up" } |
    Select-Object -ExpandProperty IPv4Address |
    Select-Object -First 1
).IPAddress

if (-not $LanIp) {
    $LanIp = (
        Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.IPAddress -notlike "169.254*" } |
        Select-Object -First 1
    ).IPAddress
}

$MobileFrontendUrl = if ($LanIp) { "http://$LanIp`:5713" } else { "Unavailable: connect to Wi-Fi first" }
$MobileBackendUrl = if ($LanIp) { "http://$LanIp`:8000/api/health" } else { "Unavailable: connect to Wi-Fi first" }

Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Write-Host "Checking backend packages..." -ForegroundColor Cyan
& $Python -m pip install fastapi uvicorn pytest | Out-Host

Write-Host "Starting backend API on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$ProjectRoot`"; .\.venv\Scripts\Activate.ps1; python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5713 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$ProjectRoot`"; .\.venv\Scripts\Activate.ps1; python -m http.server 5713 --bind 0.0.0.0 -d frontend"
)

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Project is running." -ForegroundColor Green
Write-Host "Laptop frontend link: $LocalFrontendUrl" -ForegroundColor Yellow
Write-Host "Laptop backend check:  $LocalBackendUrl" -ForegroundColor Yellow
Write-Host "Mobile frontend link: $MobileFrontendUrl" -ForegroundColor Yellow
Write-Host "Mobile backend check:  $MobileBackendUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "Click on laptop: $LocalFrontendUrl" -ForegroundColor Yellow
Write-Host "Open on mobile while on same Wi-Fi: $MobileFrontendUrl" -ForegroundColor Yellow

Start-Process $LocalFrontendUrl
