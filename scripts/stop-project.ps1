$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$PidFile = Join-Path $Root ".runtime\project-pids.json"

if (-not (Test-Path $PidFile)) {
    Write-Host "No project PID file was found. The project may already be stopped."
    exit 0
}

$Saved = Get-Content $PidFile -Raw | ConvertFrom-Json
foreach ($service in @("frontend", "backend")) {
    $entry = $Saved.$service
    if (-not $entry) { continue }
    $targets = @(
        @{ pid = $entry.pid; startedAt = $entry.startedAt; label = "$service service" },
        @{ pid = $entry.windowPid; startedAt = $entry.windowStartedAt; label = "$service window" }
    )
    $handled = @{}
    foreach ($target in $targets) {
        if (-not $target.pid -or $handled.ContainsKey([string]$target.pid)) { continue }
        $handled[[string]$target.pid] = $true
        $process = Get-Process -Id ([int]$target.pid) -ErrorAction SilentlyContinue
        if (-not $process) { continue }

        $expected = [datetime]::Parse($target.startedAt)
        if ([math]::Abs(($process.StartTime - $expected).TotalSeconds) -gt 5) {
            Write-Warning "PID $($target.pid) is now owned by another process; it was not stopped."
            continue
        }

        & taskkill.exe /PID $target.pid /T /F 2>$null | Out-Null
        Write-Host "Stopped $($target.label) (PID $($target.pid))."
    }
}

Remove-Item -LiteralPath $PidFile -Force
