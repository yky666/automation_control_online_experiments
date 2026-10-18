param([switch]$TeacherMatlab)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    $taskUv=Get-Command uv -ErrorAction SilentlyContinue
    if ($taskUv) { & $taskUv.Source venv --python 3.12 --seed .venv }
    elseif (Get-Command py -ErrorAction SilentlyContinue) { & py -3.12 -m venv .venv }
    else { throw 'Install Python 3.12 or uv, then run setup.ps1 again. MATLAB R2024b requires Python 3.9-3.12.' }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 environment creation failed.' }
}
& $taskPython -m pip install -r requirements-cloud.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependencies failed.' }
$taskMatlab=Get-Command matlab -ErrorAction SilentlyContinue
if ($TeacherMatlab -and $taskMatlab) {
    & $taskPython -m pip install -r requirements.txt
    $taskMatlabRoot=Split-Path -Parent (Split-Path -Parent $taskMatlab.Source)
    $taskEnginePackage=Join-Path $taskMatlabRoot 'extern\engines\python'
    if (Test-Path -LiteralPath $taskEnginePackage) {
        & $taskPython -m pip install $taskEnginePackage
        if ($LASTEXITCODE -ne 0) { Write-Warning 'Engine install failed; MATLAB -batch fallback remains available.' }
    }
}
& npm.cmd ci
if ($LASTEXITCODE -ne 0) { throw 'Frontend dependencies failed.' }
& $taskPython tools/export_online.py
if ($LASTEXITCODE -ne 0) { throw 'Course example export failed.' }
& node tools/export_scripts.mjs
& node tools/export_physical.mjs
if ($LASTEXITCODE -ne 0) { throw 'Physical circuit export failed.' }
if ($LASTEXITCODE -ne 0) { throw 'MATLAB script export failed.' }
& npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
Write-Host 'Ready. Run start.ps1 or double-click the launch .cmd file.' -ForegroundColor Green
