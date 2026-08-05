# 在项目根目录启动前端开发服务。
Set-Location (Join-Path $PSScriptRoot "frontend")

if (-not (Test-Path ".\node_modules")) {
  npm.cmd install
}

npm.cmd run dev -- --host 127.0.0.1
