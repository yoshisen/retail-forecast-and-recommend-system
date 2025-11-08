import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
# import openai  # 如需用OpenAI，取消注释

app = FastAPI()

# CORS設定（フロントエンド開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_csv(df: pd.DataFrame):
    info = {
        "columns": [],
        "row_count": len(df)
    }
    for col in df.columns:
        dtype = str(df[col].dtype)
        stats = {}
        if pd.api.types.is_numeric_dtype(df[col]):
            stats = {
                "mean": df[col].mean(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max(),
                "nulls": int(df[col].isnull().sum())
            }
        else:
            stats = {
                "unique": int(df[col].nunique()),
                "top": df[col].mode().iloc[0] if not df[col].mode().empty else None,
                "nulls": int(df[col].isnull().sum())
            }
        info["columns"].append({
            "name": col,
            "dtype": dtype,
            "stats": stats
        })
    return info

def parse_intent(question: str, columns: list):
    q = question.lower()
    if "trend" in q or "傾向" in q:
        for col in columns:
            col_lower = col.lower()
            if "月" in col_lower or "date" in col_lower or "time" in col_lower:
                return {"type": "trend", "time_col": col}
    if "一番売れている" in q or "最も" in q:
        for col in columns:
            col_lower = col.lower()
            if "product" in col_lower or "商品" in col_lower:
                return {"type": "top_product", "product_col": col}
    if "成長が最も速い" in q:
        for col in columns:
            col_lower = col.lower()
            if "月" in col_lower or "date" in col_lower or "time" in col_lower:
                return {"type": "fastest_growth", "time_col": col}
    if "集計" in q or "注文数" in q:
        for col in columns:
            col_lower = col.lower()
            if "region" in col_lower or "area" in col_lower or "地域" in col_lower:
                return {"type": "count_by_region", "region_col": col}
    return {"type": "unknown"}

def plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        csv_info = analyze_csv(df)
        intent = parse_intent(question, list(df.columns))

        result = {
            "conclusion": "",
            "chart": None,
            "error": None,
            "csv_info": csv_info
        }

        # 1. 傾向分析
        if intent["type"] == "trend":
            time_col = intent["time_col"]
            value_col = None
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]) and col != time_col:
                    value_col = col
                    break
            if value_col:
                df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
                trend = df.groupby(df[time_col].dt.to_period("M"))[value_col].sum()
                plt.figure(figsize=(8, 4))
                trend.plot(marker="o")
                plt.title(f"{time_col} 月別{value_col}傾向")
                plt.xlabel("月")
                plt.ylabel(value_col)
                plt.tight_layout()
                img = plot_to_base64()
                result["conclusion"] = f"{value_col} の月別傾向は下記のグラフの通りです。"
                result["chart"] = img
            else:
                result["error"] = "傾向分析に適した数値列が見つかりませんでした。"

        # 2. 一番売れている商品
        elif intent["type"] == "top_product":
            product_col = intent["product_col"]
            value_col = None
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    value_col = col
                    break
            if value_col:
                top = df.groupby(product_col)[value_col].sum().idxmax()
                result["conclusion"] = f"一番売れている商品は：{top}"
                plt.figure(figsize=(8, 4))
                df.groupby(product_col)[value_col].sum().sort_values(ascending=False).plot(kind="bar")
                plt.title("商品別売上")
                plt.xlabel("商品")
                plt.ylabel(value_col)
                plt.tight_layout()
                img = plot_to_base64()
                result["chart"] = img
            else:
                result["error"] = "商品売上集計に適した数値列が見つかりませんでした。"

        # 3. 成長が最も速い月
        elif intent["type"] == "fastest_growth":
            time_col = intent["time_col"]
            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            monthly = df.groupby(df[time_col].dt.to_period("M")).size()
            growth = monthly.diff().fillna(0)
            fastest_month = growth.idxmax()
            result["conclusion"] = f"成長が最も速い月は：{fastest_month}"
            plt.figure(figsize=(8, 4))
            monthly.plot(marker="o", label="ユーザー数")
            growth.plot(marker="x", label="増加数")
            plt.legend()
            plt.title("月別ユーザー成長傾向")
            plt.xlabel("月")
            plt.ylabel("ユーザー数")
            plt.tight_layout()
            img = plot_to_base64()
            result["chart"] = img

        # 4. 地域別注文数集計
        elif intent["type"] == "count_by_region":
            region_col = intent["region_col"]
            counts = df[region_col].value_counts()
            result["conclusion"] = "地域別注文数集計は下記の通りです。"
            plt.figure(figsize=(8, 4))
            counts.plot(kind="bar")
            plt.title("地域別注文数")
            plt.xlabel("地域")
            plt.ylabel("注文数")
            plt.tight_layout()
            img = plot_to_base64()
            result["chart"] = img

        else:
            result["error"] = "このタイプの質問にはまだ対応していません。質問内容を変えてみてください。"

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={
            "conclusion": "",
            "chart": None,
            "error": str(e),
            "csv_info": None
        })
