param([switch]$OpenBrowser)
$ErrorActionPreference = 'Stop'
$taskProjectRoot = $PSScriptRoot
$taskRuntime = Join-Path $taskProjectRoot 'runtime'
$taskPython = Join-Path $taskProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Please run setup.ps1 first. The Python environment is missing.' }
if (-not (Test-Path -LiteralPath (Join-Path $taskProjectRoot 'dist\index.html'))) { throw 'Please run npm.cmd install and npm.cmd run build first.' }
New-Item -ItemType Directory -Force -Path $taskRuntime | Out-Null
$taskReady = $false
try { $taskHealth = Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 2; $taskReady = $taskHealth.status -eq 'ok' -and $taskHealth.version -eq '2.2.0'; if (-not $taskReady -and (Test-Path -LiteralPath (Join-Path $taskRuntime 'server.pid'))) { & (Join-Path $taskProjectRoot 'stop.ps1') } } catch {}
if (-not $taskReady) {
    $taskProc = Start-Process -FilePath $taskPython -ArgumentList @('-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8765') -WorkingDirectory $taskProjectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskRuntime 'server.stdout.log') -RedirectStandardError (Join-Path $taskRuntime 'server.stderr.log')
    $taskProc.Id | Set-Content -LiteralPath (Join-Path $taskRuntime 'server.pid') -Encoding ASCII
    for ($taskAttempt=0; $taskAttempt -lt 60; $taskAttempt++) {
        Start-Sleep -Milliseconds 500
        try { $taskHealth = Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 1; if ($taskHealth.status -eq 'ok') { $taskReady=$true; break } } catch {}
        if ($taskProc.HasExited) { break }
    }
}
if (-not $taskReady) { throw ('Startup failed. Read ' + (Join-Path $taskRuntime 'server.stderr.log')) }
Write-Host 'Control Lab: http://127.0.0.1:8765' -ForegroundColor Cyan
Write-Host 'Student mode: platform experiments do not use local MATLAB.'
if ($OpenBrowser) { Start-Process 'http://127.0.0.1:8765' }
