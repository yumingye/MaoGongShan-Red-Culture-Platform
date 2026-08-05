# 在项目根目录启动后端服务。
Set-Location $PSScriptRoot

if (-not (Test-Path ".\backend\.venv\Scripts\python.exe")) {
  py -3 -m venv .\backend\.venv
}

.\backend\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
# 展示环境使用单进程稳定启动，避免 Windows 热重载残留旧工作进程。
.\backend\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
