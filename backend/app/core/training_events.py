"""Training events and progress broadcasting utilities."""
from typing import Any, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

PROGRESS_STAGES_FORECAST = [
    (5, "init"),
    (25, "feature_engine"),
    (40, "feature_done"),
    (50, "model_init"),
    (85, "model_train"),
    (95, "metrics"),
    (100, "complete"),
]

PROGRESS_STAGES_RECOMMEND = [
    (5, "init"),
    (20, "interaction_matrix"),
    (40, "product_features"),
    (55, "model_init"),
    (85, "model_train"),
    (95, "metrics"),
    (100, "complete"),
]


def _ensure_ws_state(app):
    if not hasattr(app.state, "ws_clients"):
        app.state.ws_clients = set()


def broadcast_training_update(app, payload: Dict[str, Any]):
    """Send a training update payload to all connected websocket clients."""
    _ensure_ws_state(app)
    dead = []
    for ws in app.state.ws_clients:
        try:
            asyncio.create_task(ws.send_json(payload))
        except Exception as e:
            logger.warning("WebSocket send failed: %s", e)
            dead.append(ws)
    for d in dead:
        app.state.ws_clients.discard(d)


def _init_training_record(app, version_id: str, model: str, status: str = "running"):
    version_data = app.state.data_versions.get(version_id)
    if not version_data:
        return
    tr = version_data.get("training", {})
    if model not in ["forecast", "recommend"]:
        return
    tr[model] = status
    tr[f"{model}_progress"] = 0
    tr.pop(f"{model}_error", None)
    tr.pop(f"{model}_metrics", None)
    tr.pop(f"{model}_matrix_info", None)
    version_data["training"] = tr


def _update_progress(app, version_id: str, model: str, progress: int, stage: str):
    version_data = app.state.data_versions.get(version_id)
    if not version_data:
        return
    tr = version_data.get("training", {})
    tr[f"{model}_progress"] = progress
    version_data["training"] = tr
    broadcast_training_update(app, {
        "type": "training_update",
        "model": model,
        "version": version_id,
        "status": tr.get(model),
        "progress": progress,
        "stage": stage,
        "metrics": tr.get(f"{model}_metrics"),
        "error": tr.get(f"{model}_error"),
    })


def _finalize(app, version_id: str, model: str, status: str, metrics: Dict[str, Any] | None = None, matrix_info: Dict[str, Any] | None = None, error: str | None = None, error_trace: str | None = None):
    version_data = app.state.data_versions.get(version_id)
    if not version_data:
        return
    tr = version_data.get("training", {})
    tr[model] = status
    if metrics:
        tr[f"{model}_metrics"] = metrics
    if matrix_info:
        tr[f"{model}_matrix_info"] = matrix_info
    if error:
        tr[f"{model}_error"] = error
    if error_trace:
        tr[f"{model}_error_trace"] = error_trace
    if status == "failed":
        tr[f"{model}_progress"] = tr.get(f"{model}_progress", 0)
    else:
        tr[f"{model}_progress"] = 100
    version_data["training"] = tr
    broadcast_training_update(app, {
        "type": "training_update",
        "model": model,
        "version": version_id,
        "status": status,
        "progress": tr.get(f"{model}_progress", 0),
        "stage": "complete" if status == "completed" else "error",
        "metrics": tr.get(f"{model}_metrics"),
        "error": tr.get(f"{model}_error"),
    })


def run_forecast_training(app, version_id: str):
    from app.core.feature_engine import FeatureEngine
    from app.models.forecasting import ForecastingPipeline

    version_data = app.state.data_versions.get(version_id)
    if not version_data:
        return {"error": "version_not_found"}
    parsed = version_data["parsed_data"]
    _init_training_record(app, version_id, "forecast")
    features_df = None
    pipeline = None
    metrics = None
    try:
        for progress, stage in PROGRESS_STAGES_FORECAST[:-1]:
            if stage == "init":
                _update_progress(app, version_id, "forecast", progress, stage)
            elif stage == "feature_engine":
                feature_engine = FeatureEngine(parsed)
                _update_progress(app, version_id, "forecast", progress, stage)
                features_df = feature_engine.generate_forecast_features()
            elif stage == "feature_done":
                _update_progress(app, version_id, "forecast", progress, stage)
            elif stage == "model_init":
                _update_progress(app, version_id, "forecast", progress, stage)
                pipeline = ForecastingPipeline(features_df)
            elif stage == "model_train":
                _update_progress(app, version_id, "forecast", progress, stage)
                metrics = pipeline.train()
            elif stage == "metrics":
                _update_progress(app, version_id, "forecast", progress, stage)
        app.state.forecast_pipeline = pipeline
        _finalize(app, version_id, "forecast", "completed", metrics=metrics)
        return {"metrics": metrics, "feature_count": len(features_df.columns) if features_df is not None else 0, "sample_count": len(features_df) if features_df is not None else 0}
    except Exception as e:
        import traceback
        tb = traceback.format_exc(limit=20)
        logger.error("Forecast training failed: %s", e, exc_info=True)
        _finalize(app, version_id, "forecast", "failed", error=str(e), error_trace=tb)
        return {"error": str(e), "trace": tb}


def run_recommend_training(app, version_id: str):
    from app.core.feature_engine import RecommendationFeatureEngine
    from app.models.recommendation import HybridRecommender

    version_data = app.state.data_versions.get(version_id)
    if not version_data:
        return {"error": "version_not_found"}
    parsed = version_data["parsed_data"]
    _init_training_record(app, version_id, "recommend")
    interaction_df = None
    matrix_info = None
    product_features = None
    recommender = None
    try:
        for progress, stage in PROGRESS_STAGES_RECOMMEND[:-1]:
            if stage == "init":
                _update_progress(app, version_id, "recommend", progress, stage)
            elif stage == "interaction_matrix":
                rec_engine = RecommendationFeatureEngine(parsed)
                _update_progress(app, version_id, "recommend", progress, stage)
                interaction_df, matrix_info = rec_engine.generate_user_item_matrix()
            elif stage == "product_features":
                _update_progress(app, version_id, "recommend", progress, stage)
                product_features = rec_engine.generate_product_features()
            elif stage == "model_init":
                _update_progress(app, version_id, "recommend", progress, stage)
                recommender = HybridRecommender()
            elif stage == "model_train":
                _update_progress(app, version_id, "recommend", progress, stage)
                recommender.fit(interaction_df, product_features)
            elif stage == "metrics":
                _update_progress(app, version_id, "recommend", progress, stage)
        app.state.recommender = recommender
        _finalize(app, version_id, "recommend", "completed", matrix_info=matrix_info)
        return {"matrix_info": matrix_info, "n_products": len(product_features) if product_features is not None else 0}
    except Exception as e:
        import traceback
        tb = traceback.format_exc(limit=20)
        logger.error("Recommender training failed: %s", e, exc_info=True)
        _finalize(app, version_id, "recommend", "failed", error=str(e), error_trace=tb)
        return {"error": str(e), "trace": tb}
