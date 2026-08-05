$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $Root ".runtime"
$PidFile = Join-Path $RuntimeDir "project-pids.json"

function Test-Port([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync("127.0.0.1", $Port)
        return $task.Wait(500) -and $client.Connected
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

function Get-ListenerProcessId([int]$Port) {
    $connection = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($connection) { return [int]$connection.OwningProcess }

    $line = netstat.exe -ano |
        Select-String "127\.0\.0\.1:$Port\s+.*LISTENING\s+(\d+)$" |
        Select-Object -First 1
    if ($line -and $line.Matches.Count -gt 0) {
        return [int]$line.Matches[0].Groups[1].Value
    }
    return 0
}

function Require-Command([string]$Name, [string]$Message) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw $Message
    }
}

Set-Location $Root
$PythonLauncher = if (Get-Command "py" -ErrorAction SilentlyContinue) {
    @{ executable = "py"; arguments = @("-3") }
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    @{ executable = "python"; arguments = @() }
} else {
    throw "Python 3 was not found. Install Python 3.10 or newer and enable the python or py command."
}
Require-Command "npm.cmd" "Node.js was not found. Install Node.js 18 or newer."

$busyPorts = @(8000, 5173) | Where-Object { Test-Port $_ }
if ($busyPorts.Count -gt 0) {
    throw "Port already in use: $($busyPorts -join ', '). Run stop.bat or close the program using the port."
}

$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "[1/4] Creating backend virtual environment..."
    & $PythonLauncher.executable @($PythonLauncher.arguments) -m venv (Join-Path $Root "backend\.venv")
    if ($LASTEXITCODE -ne 0) { throw "Backend virtual environment creation failed." }
}

$RequirementFile = Join-Path $Root "backend\requirements.txt"
$RequirementStamp = Join-Path $Root "backend\.venv\.requirements.sha256"
$RequirementHash = (Get-FileHash $RequirementFile -Algorithm SHA256).Hash
$InstalledHash = if (Test-Path $RequirementStamp) { (Get-Content $RequirementStamp -Raw).Trim() } else { "" }
if ($RequirementHash -ne $InstalledHash) {
    Write-Host "[2/4] Installing backend dependencies..."
    & $Python -m pip install -r $RequirementFile
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }
    Set-Content -Path $RequirementStamp -Value $RequirementHash -Encoding ascii
}

$FrontendDir = Join-Path $Root "frontend"
$LockFile = Join-Path $FrontendDir "package-lock.json"
$NodeModules = Join-Path $FrontendDir "node_modules"
$FrontendStamp = Join-Path $RuntimeDir "frontend-lock.sha256"
New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
$LockHash = (Get-FileHash $LockFile -Algorithm SHA256).Hash
$InstalledLockHash = if (Test-Path $FrontendStamp) { (Get-Content $FrontendStamp -Raw).Trim() } else { "" }
if (-not (Test-Path $NodeModules) -or $LockHash -ne $InstalledLockHash) {
    Write-Host "[3/4] Installing frontend dependencies..."
    Push-Location $FrontendDir
    try {
        & npm.cmd install
        if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
    } finally {
        Pop-Location
    }
    Set-Content -Path $FrontendStamp -Value $LockHash -Encoding ascii
}

Write-Host "[4/4] Starting backend and frontend..."
$BackendCommand = "& '$Python' -m uvicorn backend.app:app --host 127.0.0.1 --port 8000"
$FrontendCommand = "Set-Location '$FrontendDir'; npm.cmd run dev -- --host 127.0.0.1 --port 5173"
$BackendProcess = Start-Process powershell.exe -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $BackendCommand
) -WorkingDirectory $Root -PassThru
$FrontendProcess = Start-Process powershell.exe -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $FrontendCommand
) -WorkingDirectory $FrontendDir -PassThru

$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Seconds 1
    try {
        $api = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2
        $web = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:5173/" -TimeoutSec 2
        if ($api.StatusCode -eq 200 -and $web.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # Services are still starting.
    }
}

if (-not $ready) {
    Write-Warning "Services did not become ready in 30 seconds. Check the two service windows for details."
    foreach ($windowPid in @($BackendProcess.Id, $FrontendProcess.Id)) {
        & taskkill.exe /PID $windowPid /T /F 2>$null | Out-Null
    }
    exit 1
}

$BackendServiceId = Get-ListenerProcessId 8000
$FrontendServiceId = Get-ListenerProcessId 5173
if (-not $BackendServiceId -or -not $FrontendServiceId) {
    throw "Services responded, but their listener process IDs could not be recorded."
}
$BackendService = Get-Process -Id $BackendServiceId -ErrorAction Stop
$FrontendService = Get-Process -Id $FrontendServiceId -ErrorAction Stop

@{
    backend = @{
        pid = $BackendService.Id
        startedAt = $BackendService.StartTime.ToString("o")
        windowPid = $BackendProcess.Id
        windowStartedAt = $BackendProcess.StartTime.ToString("o")
    }
    frontend = @{
        pid = $FrontendService.Id
        startedAt = $FrontendService.StartTime.ToString("o")
        windowPid = $FrontendProcess.Id
        windowStartedAt = $FrontendProcess.StartTime.ToString("o")
    }
} | ConvertTo-Json -Depth 3 | Set-Content -Path $PidFile -Encoding utf8

Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "API docs: http://127.0.0.1:8000/docs"
Start-Process "http://127.0.0.1:5173"
