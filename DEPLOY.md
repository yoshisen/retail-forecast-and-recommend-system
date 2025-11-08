# LUMI Tokyo Retail Analytics & ML Platform

## 🎯 プロジェクト概要

日本のスーパーマーケット（LUMI東京首都圏規模）向けの販売予測と商品推薦システム。Excelファイルからの一括データアップロード、自動特徴量生成、機械学習モデル訓練、リアルタイム予測・推薦APIを提供。

### スケール
- **店舗数**: 65店舗（東京・神奈川・千葉・埼玉）
- **顧客数**: 120,000名
- **商品数**: 3,500種類
- **月間取引件数**: 500,000件

## 🏗️ アーキテクチャ

```
┌─────────────────┐
│  React Frontend │  Ant Design UI
│   (Vite + TS)   │  - Upload / Dashboard / Forecast / Recommend
└────────┬────────┘
         │ REST API
┌────────▼─────────────────────────────────────────┐
│            FastAPI Backend                        │
│  ┌──────────────┐  ┌───────────────────────┐    │
│  │ Excel Parser │→│ Data Quality Checker  │    │
│  │ (多言語対応)   │  │ (欠損・異常値・重複)    │    │
│  └──────┬───────┘  └───────────┬───────────┘    │
│         │                      │                 │
│  ┌──────▼──────────────────────▼───────┐        │
│  │     Feature Engineering              │        │
│  │  時系列・ラグ・移動平均・価格・        │        │
│  │  プロモーション・天気・祝日・在庫      │        │
│  └──────┬───────────────────────────────┘        │
│         │                                         │
│  ┌──────▼──────────┐  ┌───────────────────┐    │
│  │ Forecasting     │  │ Recommendation     │    │
│  │ - Baseline      │  │ - Collaborative   │    │
│  │ - LightGBM      │  │ - Content-Based   │    │
│  │ - Prophet (P1)  │  │ - Hybrid          │    │
│  └─────────────────┘  └───────────────────┘    │
└───────────────────────────────────────────────────┘
```

## 📂 プロジェクト構造

```
dataAnalysisProject/
├── backend/
│   ├── main.py                      # FastAPI エントリーポイント
│   ├── requirements.txt              # Python依存関係
│   └── app/
│       ├── config.py                 # 設定管理
│       ├── api/
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── forecast.py       # 予測API
│       │       └── recommend.py      # 推薦API
│       ├── core/
│       │   ├── excel_parser.py       # Excel解析
│       │   ├── quality.py            # データ品質チェック
│       │   └── feature_engine.py     # 特徴量生成
│       ├── models/
│       │   ├── forecasting.py        # 予測モデル
│       │   └── recommendation.py     # 推薦モデル
│       └── schemas/
│           └── schemas.py            # Pydanticスキーマ
├── src/
│   ├── App.jsx                       # Reactメインアプリ
│   ├── main.jsx
│   ├── index.css
│   ├── pages/
│   │   ├── UploadPage.jsx            # データアップロード
│   │   ├── Dashboard.jsx             # ダッシュボード
│   │   ├── ForecastPage.jsx          # 予測ページ
│   │   └── RecommendPage.jsx         # 推薦ページ
│   └── services/
│       └── api.js                    # API クライアント
├── data/
│   ├── uploaded/                     # アップロードファイル
│   ├── processed/                    # 処理済みデータ
│   └── models/                       # 保存モデル
├── package.json
├── vite.config.js
├── tailwind.config.js
├── .env
└── README.md
```

## 🚀 セットアップ

### 前提条件
- Python 3.11+
- Node.js 18+
- npm または yarn

### バックエンドセットアップ

```powershell
# 仮想環境作成
cd backend
python -m venv dataanalysisproject
.\dataanalysisproject\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# サーバー起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンドセットアップ

```powershell
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

ブラウザで http://localhost:5173 にアクセス

## 📊 データフォーマット

### 必須シート（英語/日本語/中国語対応）

1. **取引データ (Transactions/トランザクション/交易)**
   - transaction_id, customer_id, product_id, store_id
   - quantity, unit_price, total_price
   - transaction_date

2. **商品マスタ (Products/商品/产品)**
   - product_id, product_name
   - category, sub_category
   - unit_cost, selling_price

3. **顧客マスタ (Customers/顧客/客户)**
   - customer_id, customer_name
   - gender, age, membership_level
   - registration_date

4. **店舗マスタ (Stores/店舗/门店)**
   - store_id, store_name
   - prefecture, city, area

### オプションシート（機能拡張）

- **Promotions**: プロモーション効果分析
- **Weather**: 天気と売上の相関
- **Holidays**: 祝日需要予測
- **Inventory**: 在庫最適化

## 🔧 API エンドポイント

### データアップロード
```
POST /api/v1/upload
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "data": {
    "version": "20240101_120000",
    "sheet_summaries": {...}
  }
}
```

### 販売予測
```
GET /api/v1/forecast?product_id=P000001&store_id=LUMI0001&horizon=14

Response:
{
  "success": true,
  "data": {
    "product_id": "P000001",
    "predictions": [12.5, 13.2, ...],
    "dates": ["2024-01-01", "2024-01-02", ...]
  }
}
```

### 商品推薦
```
GET /api/v1/recommend?customer_id=C000001&top_k=10

Response:
{
  "success": true,
  "data": {
    "customer_id": "C000001",
    "recommendations": [
      {
        "product_id": "P000123",
        "product_name": "コシヒカリ 5kg",
        "score": 0.87
      }
    ]
  }
}
```

## 🧠 機械学習モデル

### 販売予測
- **ベースラインモデル**: 移動平均（MA-7/MA-14/MA-28）
- **LightGBM**: 勾配ブースティング決定木
  - 特徴量: 時系列ラグ、移動平均、価格、プロモーション、天気、祝日
  - メトリクス: MAE, RMSE, MAPE
  - 早期停止: 50ラウンド改善なしで停止

### 推薦システム
- **協同フィルタリング (CF)**: ユーザー間類似度（コサイン類似度）
- **コンテンツベース**: カテゴリー・価格帯類似度
- **ハイブリッド**: CF 60% + Content 40%
- **フォールバック**: 新規ユーザー → 人気商品

## 🎨 フロントエンド機能

### 1. データアップロードページ
- ドラッグ&ドロップでExcelアップロード
- リアルタイム解析進捗表示
- データ品質レポート自動生成
- 警告・エラー表示

### 2. ダッシュボード
- 総シート数・レコード数統計
- シート別データサマリー
- モデル訓練ボタン（予測・推薦）
- バージョン管理

### 3. 販売予測ページ
- 商品ID・店舗ID入力
- 予測期間スライダー（1-90日）
- 予測結果グラフ（Recharts）
- 詳細データテーブル

### 4. 商品推薦ページ
- 顧客ID入力
- 推薦商品数設定（Top-K）
- 推薦カード表示（スコア付き）
- 人気商品ランキング

## ⚙️ 設定

### backend/app/config.py
```python
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
FORECAST_HORIZON = 14                 # 予測日数
TOP_K_RECOMMEND = 10                  # 推薦商品数
MISSING_RATE_CRITICAL = 0.6           # 欠損率閾値
```

### .env
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 🧪 テスト計画（実装後）

### バックエンドテスト
```powershell
cd backend
pytest tests/ -v --cov=app
```

### フロントエンドテスト
```powershell
npm run test
```

### 統合テスト
1. Excelアップロード → 解析成功
2. モデル訓練 → メトリクス確認
3. 予測API → 正常レスポンス
4. 推薦API → Top-K商品返却

## 📋 TODO リスト

### P0（MVP完了）
- [x] Excel多言語パーサー
- [x] データ品質チェッカー
- [x] 特徴量エンジニアリング
- [x] LightGBM予測モデル
- [x] ハイブリッド推薦システム
- [x] FastAPI エンドポイント
- [x] React UI（4ページ）
- [x] ルーティング・ナビゲーション

### P1（次期優先）
- [ ] Prophet 時系列予測追加
- [ ] モデル永続化（pickle/joblib）
- [ ] PostgreSQL データベース統合
- [ ] Docker Compose 構成
- [ ] Celery バックグラウンドタスク
- [ ] 単体・統合テスト
- [ ] エラーロギング（Sentry）
- [ ] API認証（JWT）

### P2（将来拡張）
- [ ] 在庫最適化モデル
- [ ] 価格弾力性分析
- [ ] A/Bテスト基盤
- [ ] リアルタイムストリーミング予測
- [ ] GraphQL API
- [ ] 管理者ダッシュボード

## 🐛 既知の問題

1. **モデル永続化未実装**: 現状メモリ保持のみ、再起動でリセット
2. **バッチ予測パフォーマンス**: 大量リクエスト時の最適化必要
3. **フロントエンドルーティング**: `window.location.href` でページリロード発生

## 🤝 コントリビューション

1. Feature ブランチ作成
2. コード変更 + テスト追加
3. Pull Request 作成
4. レビュー後マージ

## 📝 ライセンス

Apache-2.0 license

## 👥 作者

Senior Full-Stack Data & ML Engineering AI Agent

---

**最終更新**: 2024-01-XX  
**バージョン**: 1.0.0  
**ステータス**: MVP完了 🚀
