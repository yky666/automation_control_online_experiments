$ErrorActionPreference='Stop'
$taskPidFile=Join-Path $PSScriptRoot 'runtime\server.pid'
if (-not (Test-Path -LiteralPath $taskPidFile)) { Write-Host 'No owned background server.'; exit }
$taskProcessId=[int](Get-Content -LiteralPath $taskPidFile)
$taskProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$taskProcessId" -ErrorAction SilentlyContinue
if ($taskProcess -and $taskProcess.CommandLine -match 'uvicorn backend.main:app' -and $taskProcess.ExecutablePath -eq (Join-Path $PSScriptRoot '.venv\Scripts\python.exe')) {
    Stop-Process -Id $taskProcessId
    Write-Host 'Control Lab stopped.'
} else { Write-Host 'The saved PID no longer belongs to this project; nothing was stopped.' }
