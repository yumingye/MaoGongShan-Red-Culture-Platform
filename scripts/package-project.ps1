$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$TargetName = "maogongshan-red-culture-platform"
$TempBase = Join-Path ([System.IO.Path]::GetTempPath()) "maogongshan-package-$([guid]::NewGuid().ToString('N'))"
$Stage = Join-Path $TempBase $TargetName

& (Join-Path $PSScriptRoot "verify-project.ps1")

New-Item -ItemType Directory -Force -Path $Stage | Out-Null
$excludeDirs = @(
    "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".npm-cache", "dist", "build", ".git", ".agents", ".backup",
    ".runtime", "private", "backups"
)
$excludeFiles = @(
    ".env", "*.log", "*.tmp", "*.temp", "*.pyc", "*.pyo",
    "*.backup.db", "*.bak.db"
)

foreach ($folder in @("frontend", "backend", "database", "assets", "docs", "scripts")) {
    $source = Join-Path $Root $folder
    if (-not (Test-Path $source)) { continue }
    $destination = Join-Path $Stage $folder
    $arguments = @(
        $source, $destination, "/E", "/R:1", "/W:1", "/NFL", "/NDL", "/NJH", "/NJS", "/NP",
        "/XD"
    ) + $excludeDirs + @("/XF") + $excludeFiles
    & robocopy.exe @arguments | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Failed to copy $folder (robocopy exit code $LASTEXITCODE)." }
}

foreach ($file in @(
    "README.md", ".gitignore", ".env.example", "LICENSE", "netlify.toml", "render.yaml",
    "start.bat", "stop.bat", "package-project.bat"
)) {
    $source = Join-Path $Root $file
    if (Test-Path $source) {
        Copy-Item -LiteralPath $source -Destination (Join-Path $Stage $file)
    }
}

$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = (Get-Command py).Source
        $PythonArgs = @("-3")
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = (Get-Command python).Source
        $PythonArgs = @()
    } else {
        throw "Python 3 is required to sanitize the public database."
    }
} else {
    $PythonArgs = @()
}
$Sanitizer = Join-Path $Stage "backend\sanitize_public_db.py"
$PublicDb = Join-Path $Stage "database\maogongshan.db"
& $Python @PythonArgs $Sanitizer --database $PublicDb
if ($LASTEXITCODE -ne 0) { throw "Public database sanitization failed." }

$unexpectedEnvs = Get-ChildItem $Stage -Recurse -Force -File |
    Where-Object {
        $allowedEnvFiles = @(".env.example", ".env.development", ".env.production.example")
        $_.Name -eq ".env" -or
        ($_.Name -like ".env.*" -and $_.Name -notin $allowedEnvFiles)
    }
if ($unexpectedEnvs.Count -gt 0) {
    throw "Environment secret files were found in the staging directory."
}

$textFiles = Get-ChildItem $Stage -Recurse -File |
    Where-Object { $_.Extension -in ".py", ".js", ".mjs", ".vue", ".md", ".json", ".ps1", ".bat", ".example" }
$secretMatches = $textFiles | Select-String -Pattern "sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}" -ErrorAction SilentlyContinue
if ($secretMatches) {
    throw "Possible API keys were found in the staged project."
}

$RootName = Split-Path $Root -Leaf
if ($RootName -ne $TargetName) {
    $ExportFolder = Join-Path $Root $TargetName
    $expectedExport = [System.IO.Path]::GetFullPath($ExportFolder)
    $expectedParent = [System.IO.Path]::GetFullPath($Root).TrimEnd("\") + "\"
    if (-not $expectedExport.StartsWith($expectedParent, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to replace an export folder outside the project root."
    }
    if (Test-Path $ExportFolder) {
        Remove-Item -LiteralPath $ExportFolder -Recurse -Force
    }
    Copy-Item -LiteralPath $Stage -Destination $ExportFolder -Recurse
    Write-Host "Clean project folder created: $ExportFolder"
}

$OutputDir = if ($RootName -eq $TargetName) { Split-Path $Root -Parent } else { $Root }
$ZipPath = Join-Path $OutputDir "$TargetName.zip"
if (Test-Path $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
Compress-Archive -Path $Stage -DestinationPath $ZipPath -CompressionLevel Optimal

Write-Host "Package created: $ZipPath"
if ($TempBase.StartsWith([System.IO.Path]::GetTempPath(), [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $TempBase -Recurse -Force
}
