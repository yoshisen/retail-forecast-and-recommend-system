# リテール分析 & ML プラットフォーム

現在このプロジェクトは **Excel (複数シート) データアップロード → 自動特徴生成 → 販売予測 / 商品推薦モデル訓練 → ダッシュボードで進捗と結果確認** までをカバーしています。

> 重要: 旧 README に記載されていた「自然言語での質問による分析」はまだ実装されていません（ロードマップ段階）。現状は構造化データを使った予測・推薦の検証用 UI です。

## 自然言語Q&A について (実装予定)
アップロード済みデータに対して **日本語の自然言語で質問し、集計・傾向分析・可視化（グラフ生成）を自動で返す** 機能は初期コンセプトに含まれていました。現在は未実装ですが、以下のような質問例に対応できるよう今後拡張予定です。

例: 
- 「月別売上傾向グラフを描いてください」
- 「一番売れている商品は？」
- 「ユーザー成長が最も速い月は？」
- 「地域ごとの注文数を集計してください」

予定アプローチ (案):
- 質問 → 意図解析 (集計指標 / 次元 / フィルタ抽出)
- セマンティック辞書 + 列名マッピング (日本語 → 内部標準カラム)
- クエリプラン生成 (pandas / DuckDB / SQL いずれか) → 実行
- 結果 DataFrame を自動チャート化（種類推論: 折れ線 / 棒 / 円 / ヒートマップ 等）
- 応答キャッシュ & 再質問コンテキスト保持

現段階では UI / API の土台のみのため、このセクションは将来開発のプレースホルダです。

## 主な機能 (現状)
- Excel ファイルアップロード (複数シート識別 / 標準化 / 品質レポート)
- 自動/手動の販売予測モデル訓練 (LightGBM + ベースライン)
- 自動/手動の商品推薦モデル訓練 (協同フィルタリング + コンテンツベースハイブリッド)
- WebSocket によるリアルタイム訓練進捗更新 (段階的パーセンテージ)
- 失敗時の詳細ログ表示（スタックトレース展開）
- バージョン管理（アップロード毎に version ID 発行）

## これから対応予定 (Roadmap)
- 自然言語質問 → メトリック抽出 / グラフ生成
- モデル永続化 (ファイル保存 / バージョン間ロード)
- 認証 / 権限管理
- 高度特徴 (レビュー感情 / 商品関連 / 顧客行動シート統合)
- WebSocket 再接続バックオフ強化（部分実装予定）

## 技術スタック
- フロントエンド: React + Ant Design + Vite
- スタイル: Tailwind (一部) / Ant Design コンポーネント
- バックエンド: FastAPI (Python) + Pydantic v2
- モデル: LightGBM / 協同フィルタリング (pivot + cosine) / コンテンツ類似 (カテゴリ + 価格正規化)
- データ処理: pandas

## Excel スキーマ要件
アップロードする Excel のシート名と列名仕様は `UPLOAD_SCHEMA.md` を参照してください。最低限必要:
```
トランザクション明細 (transaction_items)
トランザクション (transaction)
商品 (product)
```
推奨追加 (精度向上): 顧客, 店舗, プロモーション, 祝日, 天気, 在庫

## セットアップ手順
```bash
# フロントエンド依存
npm install

# バックエンド依存
pip install -r backend/requirements.txt

# 開発サーバー起動 (フロント)
npm run dev  # http://localhost:5173

# FastAPI バックエンド起動 (PowerShell)
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
※ Node.js 未導入の場合 https://nodejs.org/ からインストール。

## 使用フロー
1. 小規模テストデータ作成（任意）: `python generate_supermarket_data_small.py data/uploaded/small_test.xlsx`
2. フロントのアップロード画面でファイル選択 → 解析完了後自動で Dashboard に遷移
3. 自動訓練進捗（予測 / 推薦）がリアルタイム更新されることを確認
4. 失敗時は「詳細ログを見る」でスタックトレース確認 → 再訓練
5. 予測 API / 推薦 API を叩いて結果確認（将来フロント画面強化予定）

## ディレクトリ構成 (抜粋)
```
dataAnalysisProject/
├─ backend/
│  ├─ app/
│  │  ├─ api/v1/ (data, forecast, recommend ルーター)
│  │  ├─ core/ (excel_parser, feature_engine, training_events など)
│  │  ├─ models/ (forecasting, recommendation)
│  │  ├─ schemas/ (Pydantic スキーマ)
│  ├─ main.py (FastAPI アプリ本体)
│  └─ requirements.txt
├─ src/
│  ├─ pages/ (UploadPage, Dashboard, ForecastPage, RecommendPage)
│  ├─ components/ (ErrorBoundary, DataAnalysisAssistant 等)
│  ├─ services/ (API 通信ラッパ)
│  ├─ App.jsx / main.jsx
├─ generate_supermarket_data_small.py (軽量データ生成)
├─ UPLOAD_SCHEMA.md (Excel スキーマ仕様)
├─ README.md
```

## 既知の制限 / 注意
| 項目 | 状態 |
|------|------|
| 自然言語クエリ | 未実装 |
| モデル永続化 | 未実装（メモリ内のみ） |
| WebSocket 再接続 | 単純 (1 回接続 → 切れたらポーリングへ) |
| 認証 | 無し |
| 大規模データ (> 数百万行) | メモリ最適化未調整 |

## トラブルシューティング抜粋
| 症状 | 原因 | 対処 |
|------|------|------|
| 訓練が失敗し datetime64 sum error | 数値列が日付誤認識 | 最新パーサ使用 / 列名見直し |
| 進捗が 0% のまま | 必須シート不足 | `UPLOAD_SCHEMA.md` を確認 |
| 失敗後再訓練ボタンが効かない | 前回エラー状態残留 | リロード / 解析ログ確認 |
| 推薦結果が少ない | 期間短い / 顧客少ない | データ期間延長 / customer シート追加 |

## ライセンス
MIT

---
今後の機能拡張に合わせ随時更新します。改善提案歓迎。
