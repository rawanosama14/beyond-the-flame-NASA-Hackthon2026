$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Source = Join-Path $Root "frontend"
$Destination = Join-Path $Root ".runtime\frontend"
$Runtime = Join-Path $Root ".runtime"
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
if (Test-Path $Destination) { Remove-Item -Recurse -Force $Destination }
Copy-Item -Recurse -Force $Source $Destination
Set-Location $Destination
npm ci
if (-not $env:NEXT_PUBLIC_API_BASE_URL) { $env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000" }
npm run dev
