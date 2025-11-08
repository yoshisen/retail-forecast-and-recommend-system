"""
Forecasting Models - 販売予測モデル
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import lightgbm as lgb
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class BaselineForecaster:
    """ベースライン予測モデル（移動平均）"""
    
    def __init__(self, window: int = 7):
        self.window = window
        self.history = {}
    
    def fit(self, df: pd.DataFrame, target_col: str = 'sales_quantity'):
        """学習"""
        if 'product_id' in df.columns and 'store_id' in df.columns:
            for (product_id, store_id), group in df.groupby(['product_id', 'store_id']):
                key = (product_id, store_id)
                self.history[key] = group[target_col].tail(self.window).mean()
        else:
            self.history['global'] = df[target_col].tail(self.window).mean()
        
        return self
    
    def predict(self, product_id: Optional[str] = None, store_id: Optional[str] = None, 
                horizon: int = 14) -> np.ndarray:
        """予測"""
        key = (product_id, store_id) if product_id and store_id else 'global'
        
        if key in self.history:
            prediction = self.history[key]
        elif 'global' in self.history:
            prediction = self.history['global']
        else:
            prediction = 0
        
        return np.array([prediction] * horizon)


class LightGBMForecaster:
    """LightGBM 予測モデル"""
    
    def __init__(self, params: Optional[Dict] = None):
        self.params = params or {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        self.model = None
        self.feature_names = None
        self.feature_importance = None
    
    def prepare_features(self, df: pd.DataFrame, target_col: str = 'sales_quantity') -> Tuple[pd.DataFrame, pd.Series]:
        """特徴量を準備"""
        # 除外するカラム
        exclude_cols = [target_col, 'date', 'product_id', 'store_id', 'customer_id', 
                       'transaction_id', 'product_name', 'store_name']
        
        # 数値型と整数型のカラムのみ使用
        feature_cols = []
        for col in df.columns:
            if col not in exclude_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    feature_cols.append(col)
        
        X = df[feature_cols].fillna(0)
        y = df[target_col].fillna(0)
        
        self.feature_names = feature_cols
        
        return X, y
    
    def fit(self, df: pd.DataFrame, target_col: str = 'sales_quantity', 
            test_size: float = 0.2, n_estimators: int = 100):
        """学習"""
        logger.info("Training LightGBM model")
        
        X, y = self.prepare_features(df, target_col)
        
        # 時系列なので順序を保持して分割
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # データセット作成
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # 学習
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=n_estimators,
            valid_sets=[valid_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10), lgb.log_evaluation(period=0)]
        )
        
        # 特徴重要度
        self.feature_importance = dict(zip(self.feature_names, self.model.feature_importance()))
        
        # 評価
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # MAPEは0除算を避ける
        mask = y_test > 0
        if mask.sum() > 0:
            mape = mean_absolute_percentage_error(y_test[mask], y_pred[mask])
        else:
            mape = 0
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
        
        logger.info(f"Model metrics: MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape:.2%}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """予測"""
        if self.model is None:
            raise ValueError("モデルが学習されていません")
        
        # 特徴量を揃える
        X_aligned = X[self.feature_names].fillna(0)
        
        return self.model.predict(X_aligned)
    
    def save(self, path: Path):
        """モデル保存"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'feature_importance': self.feature_importance,
                'params': self.params
            }, f)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: Path):
        """モデル読み込み"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.feature_importance = data['feature_importance']
            self.params = data['params']
        logger.info(f"Model loaded from {path}")


class ForecastingPipeline:
    """予測パイプライン（階層化戦略）"""
    
    def __init__(self, features_df: pd.DataFrame):
        self.features_df = features_df
        self.baseline_model = BaselineForecaster()
        self.lgbm_model = LightGBMForecaster()
        self.metrics = {}
    
    def train(self, target_col: str = 'sales_quantity'):
        """学習"""
        logger.info("Training forecasting pipeline")
        
        # データを準備
        df = self.features_df.copy()
        
        # 欠損値を含む行を削除
        df = df.dropna(subset=[target_col])
        
        if len(df) < 100:
            logger.warning(f"データ量が少ない: {len(df)}行")
        
        # ベースラインモデル
        self.baseline_model.fit(df, target_col)
        
        # LightGBMモデル
        self.metrics = self.lgbm_model.fit(df, target_col)
        
        logger.info("Training completed")
        
        return self.metrics
    
    def forecast(self, product_id: str, store_id: str, horizon: int = 14, 
                 use_baseline: bool = False) -> Dict[str, Any]:
        """予測実行"""
        if use_baseline:
            # ベースライン予測
            predictions = self.baseline_model.predict(product_id, store_id, horizon)
            method = 'baseline'
        else:
            # LightGBM予測
            # 最新データを取得
            if 'product_id' in self.features_df.columns and 'store_id' in self.features_df.columns:
                latest_data = self.features_df[
                    (self.features_df['product_id'] == product_id) & 
                    (self.features_df['store_id'] == store_id)
                ].tail(1)
            else:
                latest_data = self.features_df.tail(1)
            
            if len(latest_data) == 0:
                # データがない場合はベースライン
                predictions = self.baseline_model.predict(product_id, store_id, horizon)
                method = 'baseline_fallback'
            else:
                # 特徴量を複製してhorizon日分予測
                predictions = []
                for i in range(horizon):
                    pred = self.lgbm_model.predict(latest_data)[0]
                    predictions.append(max(0, pred))  # 負の予測を0にクリップ
                
                predictions = np.array(predictions)
                method = 'lightgbm'
        
        # 日付範囲を生成
        if 'date' in self.features_df.columns:
            last_date = self.features_df['date'].max()
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon)
        else:
            forecast_dates = pd.date_range(start=pd.Timestamp.now(), periods=horizon)
        
        return {
            'product_id': product_id,
            'store_id': store_id,
            'method': method,
            'horizon': horizon,
            'predictions': predictions.tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'total_forecast': float(predictions.sum()),
            'avg_daily_forecast': float(predictions.mean())
        }
    
    def batch_forecast(self, pairs: List[Tuple[str, str]], horizon: int = 14) -> List[Dict]:
        """バッチ予測"""
        results = []
        for product_id, store_id in pairs:
            try:
                result = self.forecast(product_id, store_id, horizon)
                results.append(result)
            except Exception as e:
                logger.error(f"Error forecasting {product_id}, {store_id}: {str(e)}")
                results.append({
                    'product_id': product_id,
                    'store_id': store_id,
                    'error': str(e)
                })
        
        return results
    
    def save(self, model_dir: Path):
        """モデル保存"""
        model_dir.mkdir(parents=True, exist_ok=True)
        self.lgbm_model.save(model_dir / 'lgbm_model.pkl')
        
        # メタデータ
        with open(model_dir / 'metadata.pkl', 'wb') as f:
            pickle.dump({
                'metrics': self.metrics,
                'feature_names': self.lgbm_model.feature_names
            }, f)
    
    def load(self, model_dir: Path):
        """モデル読み込み"""
        self.lgbm_model.load(model_dir / 'lgbm_model.pkl')
        
        with open(model_dir / 'metadata.pkl', 'rb') as f:
            data = pickle.load(f)
            self.metrics = data['metrics']
