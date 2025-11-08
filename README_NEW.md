# イオン連鎖スーパーマーケット分析システム

## 📊 プロジェクト概要

Excel ファイルから連鎖スーパーマーケットのデータを自動解析し、販売予測と個性化推薦を提供する全栈データ分析システム。

### 主要機能

- ✅ **Excel アップロードと自動解析**: 複数シート対応、自動型推論
- 📈 **販売予測**: LightGBM ベースの時系列予測
- 🎁 **商品推薦**: 協同フィルタリング + コンテンツベース
- 📊 **データ質量報告**: 自動検証とレポート生成
- 🔄 **バージョン管理**: 複数データバージョンの管理
- 🌐 **Web UI**: React ベースの直感的なインターフェース

---

## 🏗️ アーキテクチャ

```
Frontend (React + Vite)
    ↕ REST API
Backend (FastAPI + Python)
    ├─ Excel Parser
    ├─ Quality Checker
    ├─ Feature Engine
    ├─ Forecasting Models
    └─ Recommendation Engine
```

---

## 🚀 クイックスタート

### 必要要件

- Python 3.11+
- Node.js 18+
- 10GB+ ディスク空き容量

### バックエンドセットアップ

\`\`\`bash
# 1. プロジェクトディレクトリに移動
cd dataAnalysisProject/backend

# 2. Python仮想環境作成
python -m venv dataanalysisproject

# 3. 仮想環境アクティベート
# Windows:
dataanalysisproject\\Scripts\\activate
# macOS/Linux:
source dataanalysisproject/bin/activate

# 4. 依存パッケージインストール
pip install -r requirements.txt

# 5. アプリケーション起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

バックエンドが起動したら: http://localhost:8000

API ドキュメント: http://localhost:8000/api/docs

### フロントエンドセットアップ

\`\`\`bash
# 1. プロジェクトルートに移動
cd dataAnalysisProject

# 2. 依存パッケージインストール
npm install

# 3. 開発サーバー起動
npm run dev
\`\`\`

フロントエンドが起動したら: http://localhost:5173

---

## 📁 プロジェクト構造

\`\`\`
dataAnalysisProject/
├── backend/                      # FastAPI バックエンド
│   ├── app/
│   │   ├── main.py              # エントリポイント
│   │   ├── config.py            # 設定管理
│   │   ├── api/v1/              # APIエンドポイント
│   │   ├── core/                # コアロジック
│   │   │   ├── excel_parser.py # Excel解析
│   │   │   ├── quality.py      # 質量チェック
│   │   │   ├── feature_engine.py  # 特徴生成
│   │   ├── models/              # MLモデル
│   │   └── schemas/             # Pydanticスキーマ
│   ├── tests/                   # テスト
│   └── requirements.txt         # Python依存
├── frontend/                    # (既存構造維持)
│   └── src/
├── data/                        # データディレクトリ
│   ├── uploaded/               # アップロードファイル
│   ├── processed/              # 処理済みデータ
│   └── models/                 # 保存モデル
├── generate_supermarket_data.py # テストデータ生成
└── PROJECT_SPEC.md             # プロジェクト仕様書
\`\`\`

---

## 📝 使用方法

### 1. テストデータ生成

\`\`\`bash
python generate_supermarket_data.py
\`\`\`

これにより `aeon_tokyo_sales_data.xlsx` が生成されます。

### 2. Excel アップロード

\`\`\`bash
curl -X POST "http://localhost:8000/api/v1/upload" \\
  -F "file=@aeon_tokyo_sales_data.xlsx"
\`\`\`

または Web UI からアップロード。

### 3. データサマリー取得

\`\`\`bash
curl "http://localhost:8000/api/v1/data/summary"
\`\`\`

### 4. 質量報告取得

\`\`\`bash
curl "http://localhost:8000/api/v1/data/quality"
\`\`\`

---

## 🧪 テスト

### バックエンドテスト

\`\`\`bash
cd backend
pytest tests/ -v --cov=app
\`\`\`

### フロントエンドテスト

\`\`\`bash
npm run test
\`\`\`

---

## 📊 API エンドポイント

### 現在実装済み (P0 - Week 1)

| エンドポイント | メソッド | 説明 |
|------------|------|------|
| `/` | GET | ルート |
| `/api/health` | GET | ヘルスチェック |
| `/api/v1/upload` | POST | Excel アップロード |
| `/api/v1/data/summary` | GET | データサマリー |
| `/api/v1/data/quality` | GET | 質量報告 |
| `/api/v1/versions` | GET | バージョンリスト |

### 今後実装予定

| エンドポイント | メソッド | 説明 | 優先度 |
|------------|------|------|-------|
| `/api/v1/forecast` | GET | 販売予測（単一） | P0 Week2 |
| `/api/v1/forecast/batch` | POST | 販売予測（バッチ） | P0 Week2 |
| `/api/v1/recommend` | GET | 個別推薦 | P0 Week3 |
| `/api/v1/recommend/popular` | GET | 人気商品 | P0 Week3 |
| `/api/v1/inventory/suggestions` | GET | 在庫提案 | P1 |
| `/api/v1/promotion/simulate` | POST | プロモーションシミュレーション | P1 |

---

## 🔧 設定

`.env` ファイルで設定をカスタマイズ可能:

\`\`\`env
# Application
DEBUG=true
APP_NAME="AEON Retail Analytics System"

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB

# Data Processing
CHUNK_SIZE=50000
TIMEZONE=Asia/Tokyo

# Model
FORECAST_HORIZON=14
MIN_HISTORY_DAYS=90

# Cache
CACHE_TTL=3600
\`\`\`

---

## 📈 開発ロードマップ

### ✅ Phase 1 (Week 1) - 完了
- [x] プロジェクト構造構築
- [x] Excel 解析エンジン
- [x] データ質量チェッカー
- [x] FastAPI 基本エンドポイント
- [x] アップロード機能

### 🎯 Phase 2 (Week 2) - 進行中
- [ ] 特徴エンジニアリング
- [ ] 販売予測モデル (Baseline + LightGBM)
- [ ] 予測 API エンドポイント
- [ ] モデル評価

### 📅 Phase 3 (Week 3) - 予定
- [ ] 協同フィルタリング実装
- [ ] 推薦エンジン
- [ ] 推薦 API エンドポイント
- [ ] 冷启动処理

### 📅 Phase 4 (Week 4) - 予定
- [ ] React UI 実装
- [ ] データ可視化
- [ ] E2E テスト
- [ ] Docker 化

---

## 🤝 貢献

プルリクエスト歓迎！以下の手順に従ってください:

1. Fork このリポジトリ
2. Feature ブランチ作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエスト作成

---

## 📄 ライセンス

MIT License

---

## 📧 お問い合わせ

プロジェクトに関する質問や提案は Issues でお願いします。

---

**開発状況**: Phase 1 完了、Phase 2 開始

**最終更新**: 2025-10-31
