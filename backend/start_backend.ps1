# 快速启动脚本（需要先cd到backend目录激活虚拟环境）
# Windows PowerShell

Write-Host "🚀 启动 AEON 零售分析平台 后端服务..." -ForegroundColor Cyan
Write-Host ""

# 检查是否在backend目录
if (!(Test-Path "app")) {
    Write-Host "❌ 错误: 请在backend目录下运行此脚本" -ForegroundColor Red
    Write-Host "执行: cd backend" -ForegroundColor Yellow
    exit 1
}

# 检查虚拟环境
if (!(Test-Path "dataanalysisproject")) {
    Write-Host "⚠️  虚拟环境不存在，正在创建..." -ForegroundColor Yellow
    python -m venv dataanalysisproject
    Write-Host "✅ 虚拟环境创建完成" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host "🔧 激活虚拟环境..." -ForegroundColor Yellow
.\dataanalysisproject\Scripts\Activate.ps1

# 检查依赖
Write-Host "📦 检查依赖包..." -ForegroundColor Yellow
pip list | Select-String "fastapi" > $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  依赖包未安装，正在安装..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 启动服务器
Write-Host ""
Write-Host "🚀 启动 FastAPI 服务器..." -ForegroundColor Green
Write-Host "📍 API 文档: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "📍 健康检查: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
