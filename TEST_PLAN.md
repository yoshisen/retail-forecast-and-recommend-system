# テスト計画書

## 🧪 テスト概要

完全なシステムコード実装後に実行する総合テスト計画。

## 📋 テスト項目

### 1. バックエンド単体テスト

#### 1.1 Excel パーサーテスト
```python
# tests/test_excel_parser.py

def test_sheet_mapper_japanese():
    """日本語シート名認識テスト"""
    mapper = SheetMapper()
    assert mapper.detect_type("トランザクション") == "transactions"
    assert mapper.detect_type("商品") == "products"

def test_field_standardizer():
    """フィールド名標準化テスト"""
    standardizer = FieldStandardizer()
    assert standardizer.standardize("商品ID") == "product_id"
    assert standardizer.standardize("Product ID") == "product_id"

def test_excel_parser_full():
    """完全Excel解析テスト"""
    parser = ExcelParser()
    result = parser.parse("data/uploaded/lumi_tokyo_data.xlsx")
    assert "transactions" in result
    assert len(result["transactions"]) > 0
```

**実行コマンド**:
```powershell
cd backend
pytest tests/test_excel_parser.py -v
```

#### 1.2 データ品質チェッカーテスト
```python
# tests/test_quality.py

def test_missing_rate_calculation():
    """欠損率計算テスト"""
    df = pd.DataFrame({
        'col1': [1, 2, None, 4, 5],
        'col2': [None, None, None, None, 5]
    })
    checker = DataQualityChecker()
    report = checker.check_quality({"test": df})
    assert report["test"]["col2"]["missing_rate"] == 0.8

def test_outlier_detection():
    """外れ値検出テスト"""
    # IQR法で異常値検出できることを確認
    pass

def test_validator_required_fields():
    """必須フィールド検証テスト"""
    validator = DataValidator()
    valid, issues = validator.validate({
        "transactions": pd.DataFrame(columns=["transaction_id", "customer_id"])
    })
    assert not valid  # product_id が欠けているため失敗
```

**実行コマンド**:
```powershell
pytest tests/test_quality.py -v
```

#### 1.3 特徴量エンジニアリングテスト
```python
# tests/test_feature_engine.py

def test_time_features():
    """時系列特徴量生成テスト"""
    df = pd.DataFrame({
        'transaction_date': pd.date_range('2024-01-01', periods=10)
    })
    engine = FeatureEngine({"transactions": df})
    result = engine.create_time_features(df.copy())
    assert 'year' in result.columns
    assert 'month' in result.columns
    assert 'dayofweek' in result.columns

def test_lag_features():
    """ラグ特徴量テスト"""
    # lag_1, lag_7, lag_14 が正しく生成されることを確認
    pass

def test_rolling_features():
    """移動平均特徴量テスト"""
    # rolling_mean_7, rolling_std_14 が正しく計算されることを確認
    pass
```

**実行コマンド**:
```powershell
pytest tests/test_feature_engine.py -v
```

#### 1.4 予測モデルテスト
```python
# tests/test_forecasting.py

def test_baseline_forecaster():
    """ベースライン予測テスト"""
    train_df = pd.DataFrame({
        'product_id': ['P001'] * 30,
        'store_id': ['S001'] * 30,
        'quantity': list(range(30))
    })
    forecaster = BaselineForecaster()
    forecaster.fit(train_df)
    preds = forecaster.predict('P001', 'S001', horizon=7)
    assert len(preds) == 7

def test_lightgbm_forecaster():
    """LightGBM予測テスト"""
    # モデル訓練・予測・評価が正常に動作することを確認
    pass

def test_forecasting_pipeline():
    """予測パイプライン統合テスト"""
    pipeline = ForecastingPipeline()
    # train → predict → metrics の一連の流れをテスト
    pass
```

**実行コマンド**:
```powershell
pytest tests/test_forecasting.py -v
```

#### 1.5 推薦モデルテスト
```python
# tests/test_recommendation.py

def test_collaborative_filter():
    """協同フィルタリングテスト"""
    cf = CollaborativeFilter()
    user_item_matrix = np.random.rand(100, 50)
    cf.fit(user_item_matrix)
    recommendations = cf.recommend(customer_id='C001', top_k=10)
    assert len(recommendations) <= 10

def test_content_based_recommender():
    """コンテンツベース推薦テスト"""
    # カテゴリ・価格類似度による推薦が動作することを確認
    pass

def test_hybrid_recommender():
    """ハイブリッド推薦テスト"""
    # CF + Content の重み付けスコアが正しく計算されることを確認
    pass
```

**実行コマンド**:
```powershell
pytest tests/test_recommendation.py -v
```

#### 1.6 APIエンドポイントテスト
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """ヘルスチェックテスト"""
    response = client.get("/health")
    assert response.status_code == 200

def test_upload_excel():
    """Excelアップロードテスト"""
    with open("data/uploaded/lumi_tokyo_data.xlsx", "rb") as f:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.xlsx", f)}
        )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_forecast_endpoint():
    """予測APIテスト"""
    response = client.get("/api/v1/forecast?product_id=P000001&store_id=LUMI0001&horizon=14")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["predictions"]) == 14

def test_recommend_endpoint():
    """推薦APIテスト"""
    response = client.get("/api/v1/recommend?customer_id=C000001&top_k=10")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["recommendations"]) <= 10
```

**実行コマンド**:
```powershell
pytest tests/test_api.py -v
```

### 2. フロントエンドテスト

#### 2.1 コンポーネントテスト
```javascript
// src/__tests__/UploadPage.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import UploadPage from '../pages/UploadPage';

test('renders upload area', () => {
  render(<UploadPage />);
  expect(screen.getByText(/ファイルをドロップ/i)).toBeInTheDocument();
});

test('handles file upload', async () => {
  // ファイル選択・アップロード処理のテスト
});
```

**実行コマンド**:
```powershell
npm run test
```

#### 2.2 APIクライアントテスト
```javascript
// src/__tests__/api.test.js
import { uploadExcel, getForecast, getRecommendations } from '../services/api';

test('uploadExcel makes POST request', async () => {
  const file = new File(['content'], 'test.xlsx');
  const response = await uploadExcel(file);
  expect(response.success).toBe(true);
});
```

### 3. 統合テスト

#### 3.1 エンドツーエンドフロー
```python
# tests/integration/test_full_flow.py

def test_upload_train_predict_flow():
    """完全フロー統合テスト"""
    # 1. Excelアップロード
    with open("data/uploaded/lumi_tokyo_data.xlsx", "rb") as f:
        upload_response = client.post("/api/v1/upload", files={"file": f})
    assert upload_response.status_code == 200
    
    # 2. 予測モデル訓練
    train_response = client.post("/api/v1/forecast/train")
    assert train_response.status_code == 200
    
    # 3. 予測実行
    forecast_response = client.get("/api/v1/forecast?product_id=P000001&store_id=LUMI0001")
    assert forecast_response.status_code == 200
    
    # 4. 推薦モデル訓練
    rec_train_response = client.post("/api/v1/recommend/train")
    assert rec_train_response.status_code == 200
    
    # 5. 推薦実行
    rec_response = client.get("/api/v1/recommend?customer_id=C000001")
    assert rec_response.status_code == 200
```

**実行コマンド**:
```powershell
pytest tests/integration/ -v
```

#### 3.2 パフォーマンステスト
```python
# tests/performance/test_load.py
import time

def test_batch_forecast_performance():
    """バッチ予測パフォーマンステスト"""
    pairs = [{"product_id": f"P{i:06d}", "store_id": "LUMI0001"} for i in range(100)]
    
    start = time.time()
    response = client.post("/api/v1/forecast/batch", json={"pairs": pairs})
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 10  # 100件を10秒以内
```

**実行コマンド**:
```powershell
pytest tests/performance/ -v
```

### 4. データ品質テスト

#### 4.1 サンプルデータ検証
```python
def test_generated_data_quality():
    """生成データ品質テスト"""
    df = pd.read_excel("data/uploaded/lumi_tokyo_data.xlsx", sheet_name="Transactions")
    
    # 取引件数確認（月間50万件想定）
    assert len(df) > 400000
    
    # 顧客数確認（12万人想定）
    assert df['customer_id'].nunique() > 100000
    
    # 店舗数確認（65店舗）
    assert df['store_id'].nunique() == 65
    
    # 商品数確認（3500種類）
    assert df['product_id'].nunique() > 3000
```

### 5. エラーハンドリングテスト

#### 5.1 異常系テスト
```python
def test_invalid_file_format():
    """無効ファイルフォーマットテスト"""
    response = client.post("/api/v1/upload", files={"file": ("test.txt", b"invalid")})
    assert response.status_code == 400

def test_missing_required_sheet():
    """必須シート欠如テスト"""
    # Transactions シートがないExcelファイルをアップロード
    # エラーメッセージが適切に返されることを確認
    pass

def test_forecast_nonexistent_product():
    """存在しない商品予測テスト"""
    response = client.get("/api/v1/forecast?product_id=INVALID&store_id=LUMI0001")
    assert response.status_code == 404
```

## 📊 テストカバレッジ目標

| モジュール | 目標カバレッジ |
|----------|--------------|
| Excel Parser | 90%+ |
| Quality Checker | 85%+ |
| Feature Engine | 80%+ |
| Forecasting | 85%+ |
| Recommendation | 85%+ |
| API Endpoints | 95%+ |

## 🚀 全テスト実行コマンド

### バックエンド総合テスト
```powershell
cd backend
pytest tests/ -v --cov=app --cov-report=html --cov-report=term
```

### フロントエンド総合テスト
```powershell
npm run test -- --coverage
```

### 統合テスト
```powershell
# バックエンド起動後
pytest tests/integration/ -v
```

## ✅ テスト完了チェックリスト

- [ ] Excel解析（多言語対応）正常動作確認
- [ ] データ品質レポート生成確認
- [ ] 特徴量エンジニアリング各種機能確認
- [ ] LightGBM予測精度確認（MAE, RMSE, MAPE）
- [ ] ハイブリッド推薦システム動作確認
- [ ] 全APIエンドポイントレスポンス確認
- [ ] フロントエンドUI操作確認
- [ ] エンドツーエンドフロー確認
- [ ] エラーハンドリング確認
- [ ] パフォーマンス基準達成確認
- [ ] カバレッジ目標達成確認

## 📝 テスト実行ログサンプル

```
================================ test session starts ================================
platform win32 -- Python 3.11.0, pytest-7.4.3, pluggy-1.3.0
rootdir: C:\Users\MT250530\Documents\dataAnalysisProject\backend
plugins: cov-4.1.0
collected 47 items

tests/test_excel_parser.py::test_sheet_mapper_japanese PASSED                 [  2%]
tests/test_excel_parser.py::test_field_standardizer PASSED                    [  4%]
tests/test_excel_parser.py::test_excel_parser_full PASSED                     [  6%]
tests/test_quality.py::test_missing_rate_calculation PASSED                   [  8%]
tests/test_quality.py::test_outlier_detection PASSED                          [ 10%]
tests/test_feature_engine.py::test_time_features PASSED                       [ 12%]
tests/test_forecasting.py::test_baseline_forecaster PASSED                    [ 14%]
tests/test_forecasting.py::test_lightgbm_forecaster PASSED                    [ 17%]
tests/test_recommendation.py::test_collaborative_filter PASSED                [ 19%]
tests/test_recommendation.py::test_hybrid_recommender PASSED                  [ 21%]
tests/test_api.py::test_health_check PASSED                                   [ 23%]
tests/test_api.py::test_upload_excel PASSED                                   [ 25%]
tests/test_api.py::test_forecast_endpoint PASSED                              [ 27%]
tests/test_api.py::test_recommend_endpoint PASSED                             [ 29%]
...
================================ 47 passed in 23.45s ================================

----------- coverage: platform win32, python 3.11.0 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/config.py                        35      2    94%
app/core/excel_parser.py            156     12    92%
app/core/quality.py                 134     15    89%
app/core/feature_engine.py          218     28    87%
app/models/forecasting.py           187     22    88%
app/models/recommendation.py        165     19    88%
app/api/v1/forecast.py               78      5    94%
app/api/v1/recommend.py              82      4    95%
-----------------------------------------------------
TOTAL                              1055     107    90%
```

---

**テスト実施後**: 結果をGitHub Issuesまたはプロジェクトドキュメントに記録
