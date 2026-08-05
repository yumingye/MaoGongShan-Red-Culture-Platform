$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

$required = @(
    "frontend\package.json",
    "frontend\package-lock.json",
    "frontend\.env.example",
    "frontend\public\_redirects",
    "backend\app.py",
    "backend\config.py",
    "backend\requirements.txt",
    "backend\.env.example",
    "database\maogongshan.db",
    "assets\images",
    "README.md",
    "docs\DEPLOYMENT.md",
    "netlify.toml",
    "render.yaml",
    ".gitignore",
    "start.bat",
    "stop.bat",
    "package-project.bat"
)

$missing = $required | Where-Object { -not (Test-Path (Join-Path $Root $_)) }
if ($missing.Count -gt 0) {
    throw "Missing required project files: $($missing -join ', ')"
}

$forbiddenDirs = @(
    "frontend\node_modules",
    "frontend\dist",
    "frontend\.npm-cache",
    "backend\.venv",
    "backend\__pycache__",
    ".runtime"
)
$present = $forbiddenDirs | Where-Object { Test-Path (Join-Path $Root $_) }
if ($present.Count -gt 0) {
    Write-Warning "Regenerable directories are present and will be excluded from packaging: $($present -join ', ')"
}

$secretFiles = Get-ChildItem $Root -Recurse -Force -File |
    Where-Object {
        $allowedEnvFiles = @(".env.example", ".env.development", ".env.production.example")
        $_.Name -eq ".env" -or
        ($_.Name -like ".env.*" -and $_.Name -notin $allowedEnvFiles)
    }
if ($secretFiles.Count -gt 0) {
    throw "Secret environment files must not be packaged: $($secretFiles.FullName -join ', ')"
}

$largeFiles = Get-ChildItem $Root -Recurse -File |
    Where-Object {
        $_.FullName -notmatch "\\node_modules\\|\\.venv\\|\\dist\\" -and
        $_.Length -gt 90MB
    }
if ($largeFiles.Count -gt 0) {
    throw "Files close to GitHub's 100 MB limit were found: $($largeFiles.FullName -join ', ')"
}

$trackedPrivateFiles = git -C $Root -c core.quotePath=false ls-files |
    Where-Object { $_ -match '^[^/]+\.(pdf|doc|docx|zip)$' }
if ($trackedPrivateFiles.Count -gt 0) {
    throw "Root source documents or archives are still tracked by Git: $($trackedPrivateFiles -join ', ')"
}

Write-Host "Project structure verification passed."
