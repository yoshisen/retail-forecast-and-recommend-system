"""
Data Management API Router
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Request
from pathlib import Path
import logging
from datetime import datetime
import shutil
from typing import Optional

from app.config import settings
from app.core.excel_parser import ExcelParser
from app.core.quality import DataQualityChecker, DataValidator
from app.core.training_events import run_forecast_training, run_recommend_training

logger = logging.getLogger(__name__)

router = APIRouter()

# Global state will be accessed via request.app.state


@router.post("/upload")
async def upload_excel(
    request: Request,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Excelファイルをアップロードして解析
    
    Returns:
        - success: bool
        - version: str - データバージョンID
        - parse_report: dict - 解析報告
        - quality_report: dict - 質量報告
        - warnings: list - 警告リスト
    """
    logger.info("Receiving file upload: %s", file.filename)
    
    # ファイル拡張子チェック
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不正なファイル形式: {file_ext}. 許可: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # 一時保存
    version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_path = settings.UPLOAD_DIR / f"{version_id}_{file.filename}"
    
    try:
        # ファイル保存
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("File saved to: %s", upload_path)
        
        # Excel解析
        parser = ExcelParser(upload_path)
        parse_result = parser.parse()
        
        if not parse_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Excel解析エラー: {parse_result.get('error', 'Unknown error')}"
            )
        
        parsed_data = parse_result['parsed_data']
        parse_report = parse_result['report']
        
        # データ質量チェック
        quality_checker = DataQualityChecker(parsed_data)
        quality_report = quality_checker.generate_report()
        
        # データ検証
        validation_result = DataValidator.validate_relationships(parsed_data)
        
        # 必須シートチェック
        required_sheets = ['transaction_items', 'product']
        available_sheets = list(parsed_data.keys())
        missing_sheets = [s for s in required_sheets if s not in available_sheets]
        
        if missing_sheets:
            logger.warning("Missing required sheets: %s", missing_sheets)
        
        # 初期トレーニング状態
        training_status = {
            'forecast': 'pending',
            'forecast_progress': 0,
            'recommend': 'pending',
            'recommend_progress': 0
        }

        # グローバル状態に保存
        request.app.state.data_versions[version_id] = {
            'parsed_data': parsed_data,
            'parse_report': parse_report,
            'quality_report': quality_report,
            'validation_result': validation_result,
            'uploaded_at': datetime.now().isoformat(),
            'filename': file.filename,
            'training': training_status
        }
        request.app.state.current_version = version_id
        
        logger.info("Successfully processed file, version: %s", version_id)
        
        # 警告リスト生成
        warnings = []
        if missing_sheets:
            warnings.append({
                'type': 'missing_sheets',
                'message': f"必須シート不足: {', '.join(missing_sheets)}",
                'impact': '一部機能が制限されます'
            })
        
        # オプションシート不足
        optional_sheets = {
            'promotion': 'プロモーション分析機能',
            'inventory': '在庫最適化機能',
            'weather': '天気影響分析',
            'customer_behavior': '高度な顧客分析'
        }
        for sheet, feature in optional_sheets.items():
            if sheet not in available_sheets:
                warnings.append({
                    'type': 'missing_optional_sheet',
                    'message': f"{sheet} シートがありません",
                    'impact': f"{feature}が利用できません"
                })
        
        # 自動訓練条件チェック
        can_train_forecast = all(sheet in available_sheets for sheet in ['transaction_items', 'product'])
        can_train_recommend = 'transaction_items' in available_sheets and 'customer' in available_sheets and 'product' in available_sheets

        def _auto_train_forecast(app, ver_id):
            if not can_train_forecast:
                app.state.data_versions[ver_id]['training']['forecast'] = 'skipped'
                return
            run_forecast_training(app, ver_id)

        def _auto_train_recommend(app, ver_id):
            if not can_train_recommend:
                app.state.data_versions[ver_id]['training']['recommend'] = 'skipped'
                return
            run_recommend_training(app, ver_id)

        if background_tasks:
            background_tasks.add_task(_auto_train_forecast, request.app, version_id)
            background_tasks.add_task(_auto_train_recommend, request.app, version_id)

        # 処理後ファイル削除（オプション）
        if settings.DELETE_AFTER_PARSE and background_tasks:
            background_tasks.add_task(upload_path.unlink, missing_ok=True)
        
        return {
            'success': True,
            'version': version_id,
            'parse_report': parse_report,
            'quality_report': quality_report,
            'validation_result': validation_result,
            'warnings': warnings,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'filename': file.filename,
                'available_sheets': available_sheets
            },
            'parsed_data_summary': {
                'total_sheets': len(parsed_data),
                'sheet_names': list(parsed_data.keys())
            },
            'auto_training': {
                'forecast': 'scheduled' if can_train_forecast else 'skipped',
                'recommend': 'scheduled' if can_train_recommend else 'skipped'
            }
        }
    
    except Exception as e:
        logger.error("Error processing file: %s", str(e), exc_info=True)
        
        # エラー時はファイル削除
        if upload_path.exists():
            upload_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"ファイル処理エラー: {str(e)}"
        )


@router.get("/data/summary")
async def get_data_summary(request: Request, version: Optional[str] = None):
    """
    データサマリーを取得
    
    Args:
        version: データバージョン（省略時は最新）
    
    Returns:
        データサマリー情報
    """
    version_id = version or request.app.state.current_version

    if not version_id or version_id not in request.app.state.data_versions:
        raise HTTPException(
            status_code=404,
            detail="データが見つかりません。先にファイルをアップロードしてください"
        )

    version_data = request.app.state.data_versions[version_id]
    quality_report = version_data['quality_report']

    training_info = version_data.get('training', {})
    summary = {
        'version': version_id,
        'uploaded_at': version_data['uploaded_at'],
        'filename': version_data['filename'],
        'overall_summary': quality_report['overall_summary'],
        'sheet_summaries': {},
        'training': training_info
    }
    for sheet_name, sheet_report in quality_report['sheet_reports'].items():
        summary['sheet_summaries'][sheet_name] = {
            'rows': sheet_report['row_count'],
            'columns': sheet_report['column_count'],
            'data_range': sheet_report.get('data_range', {})
        }

    return {
        'success': True,
        'data': summary,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'version': version_id
        }
    }


@router.get("/data/quality")
async def get_quality_report(request: Request, version: Optional[str] = None):
    """データ質量報告を取得"""
    version_id = version or request.app.state.current_version

    if not version_id or version_id not in request.app.state.data_versions:
        raise HTTPException(status_code=404, detail="データが見つかりません")

    version_data = request.app.state.data_versions[version_id]

    return {
        'success': True,
        'data': version_data['quality_report'],
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'version': version_id
        }
    }


@router.get("/versions")
async def list_versions(request: Request):
    """利用可能なデータバージョンのリスト"""
    versions = []
    for version_id, data in request.app.state.data_versions.items():
        versions.append({
            'version': version_id,
            'uploaded_at': data['uploaded_at'],
            'filename': data['filename'],
            'is_current': version_id == request.app.state.current_version
        })

    return {
        'success': True,
        'data': {
            'versions': sorted(versions, key=lambda x: x['uploaded_at'], reverse=True),
            'current_version': request.app.state.current_version
        }
    }
