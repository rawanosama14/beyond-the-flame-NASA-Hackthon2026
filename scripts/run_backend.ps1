$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$env:PYTHONPATH = (Join-Path $Root "backend")
$HostValue = if ($env:HOST) { $env:HOST } else { "127.0.0.1" }
$PortValue = if ($env:PORT) { $env:PORT } else { "8000" }
python -m uvicorn app.main:app --app-dir (Join-Path $Root "backend") --host $HostValue --port $PortValue --reload
