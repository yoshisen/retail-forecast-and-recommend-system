# デプロイ・起動ガイド

## 🚀 ローカル環境セットアップ

### 0. 快速启动（推荐）

**使用启动脚本一键启动前后端服务：**

```powershell
# 方法1: PowerShell脚本（推荐）
.\start.ps1

# 方法2: 批处理文件
.\start.bat

# 方法3: 仅启动后端（在backend目录）
cd backend
.\start_backend.ps1
```

脚本会自动：
- ✅ 检查并创建虚拟环境
- ✅ 安装依赖（如果缺失）
- ✅ 启动后端服务（端口8000）
- ✅ 启动前端服务（端口5173）

---

### 1. バックエンド起動（手动）

```powershell
# プロジェクトルートから
cd backend

# 仮想環境作成（初回のみ）
python -m venv dataanalysisproject

# 仮想環境アクティベート
.\dataanalysisproject\Scripts\activate

# 依存関係インストール（初回のみ）
pip install -r requirements.txt

# FastAPIサーバー起動
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**確認**: http://localhost:8000/api/docs にアクセスしてSwagger UIが表示されればOK

### 2. フロントエンド起動

```powershell
# 新しいターミナルを開く
# プロジェクトルートで

# 依存関係インストール（初回のみ）
npm install

# 開発サーバー起動
npm run dev
```

**確認**: http://localhost:5173 にアクセスしてUIが表示されればOK

### 3. サンプルデータ生成（オプション）

```powershell
# プロジェクトルートで
python generate_supermarket_data.py
```

生成されたファイル: `data/uploaded/lumi_tokyo_data.xlsx`

## 📦 本番環境デプロイ

### Docker構成（推奨）

#### Dockerfile作成

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコピー
COPY . .

# ポート公開
EXPOSE 8000

# Uvicorn起動
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile（フロントエンド）**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 依存関係インストール
COPY package*.json ./
RUN npm ci

# ビルド
COPY . .
RUN npm run build

# Nginx配信
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - TZ=Asia/Tokyo
    restart: unless-stopped

  frontend:
    build: .
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### 起動コマンド
```powershell
docker-compose up -d
```

### クラウドデプロイ

#### AWS EC2デプロイ

```bash
# EC2インスタンス接続後
sudo yum update -y
sudo yum install python3.11 git -y

# リポジトリクローン
git clone <your-repo-url>
cd dataAnalysisProject

# バックエンドセットアップ
cd backend
python3.11 -m venv dataanalysisproject
source dataanalysisproject/bin/activate
pip install -r requirements.txt

# systemdサービス作成
sudo nano /etc/systemd/system/retail-api.service
```

**retail-api.service**
```ini
[Unit]
Description=Retail Analytics API
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/dataAnalysisProject/backend
Environment="PATH=/home/ec2-user/dataAnalysisProject/backend/dataanalysisproject/bin"
Environment="PYTHONPATH=/home/ec2-user/dataAnalysisProject/backend"
ExecStart=/home/ec2-user/dataAnalysisProject/backend/dataanalysisproject/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable retail-api
sudo systemctl start retail-api
```

#### Nginx リバースプロキシ設定

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /var/www/retail-frontend;
        try_files $uri /index.html;
    }
}
```

## 🧪 テスト実行

### バックエンドテスト

```powershell
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### フロントエンドテスト

```powershell
npm run test
```

### エンドツーエンドテスト

```powershell
# Playwrightインストール（初回のみ）
npx playwright install

# E2Eテスト実行
npm run test:e2e
```

## 📊 モニタリング

### ログ確認

```powershell
# バックエンドログ
tail -f backend/logs/app.log

# Docker環境
docker-compose logs -f backend
```

### ヘルスチェック

```powershell
# API ヘルスチェック
curl http://localhost:8000/api/health

# フロントエンド確認
curl http://localhost:5173
```

## 🔒 セキュリティ設定

### 環境変数（本番用）

**.env.production**
```
VITE_API_BASE_URL=https://api.your-domain.com/api/v1
DATABASE_URL=postgresql://user:password@host:5432/retail_db
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

### HTTPS設定（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🛠️ トラブルシューティング

### バックエンドが起動しない

```powershell
# Python バージョン確認
python --version  # 3.11+ 必要

# 依存関係再インストール
pip install --upgrade -r requirements.txt

# ポート確認
netstat -ano | findstr :8000
```

### フロントエンドビルドエラー

```powershell
# キャッシュクリア
npm cache clean --force

# node_modules再インストール
Remove-Item -Recurse -Force node_modules
npm install
```

### CORS エラー

backend/main.py の CORS設定確認:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 パフォーマンス最適化

### バックエンド

```python
# Uvicorn ワーカー増加
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn使用
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### フロントエンド

```powershell
# 本番ビルド
npm run build

# バンドルサイズ分析
npm run build -- --mode analyze
```

## 🔄 アップデート手順

```powershell
# コードプル
git pull origin main

# バックエンド更新
cd backend
.\dataanalysisproject\Scripts\activate
pip install -r requirements.txt
# サーバー再起動

# フロントエンド更新
npm install
npm run build
```

---

**問題が発生した場合**: GitHub Issuesで報告してください
