"""
簡易版データ生成スクリプト (軽量 / テスト用)
目的: Backend のアップロード, 解析, 学習(予測/推薦)を高速確認できる最小構成 Excel を生成。

含まれるシート (日本語名):
  店舗, 商品, 顧客, トランザクション, トランザクション明細, プロモーション

最小限で学習に必要な列:
  - トランザクション: transaction_id, customer_id, transaction_date, store_id, total_amount_jpy
  - トランザクション明細: transaction_item_id, transaction_id, product_id, quantity, unit_price_jpy, discount_price_jpy, line_total_jpy
  - 商品: product_id, product_name, category_level1, retail_price_jpy, cost_price_jpy
  - 顧客: customer_id, gender, age, registration_date
  - 店舗: store_id, store_name
  - プロモーション: promotion_id, start_date, end_date, discount_rate

生成規模 (デフォルト):
  店舗 3 / 商品 80 / 顧客 200 / トランザクション 1,200 / 明細 最大 4,000 / プロモーション 10
約数 MB 以下を想定。

使用方法:
  python generate_supermarket_data_small.py [出力ファイルパス]
  例: python generate_supermarket_data_small.py data/uploaded/small_test.xlsx

オプション環境変数で規模調整可能:
  SMALL_NUM_STORES, SMALL_NUM_PRODUCTS, SMALL_NUM_CUSTOMERS, SMALL_NUM_TRANSACTIONS, SMALL_NUM_ITEMS
"""
from __future__ import annotations
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import sys

# 固定シードで再現性
random.seed(123)
np.random.seed(123)

# ==================== パラメータ (環境変数で上書き可) ====================
NUM_STORES = int(os.getenv("SMALL_NUM_STORES", 3))
NUM_PRODUCTS = int(os.getenv("SMALL_NUM_PRODUCTS", 80))
NUM_CUSTOMERS = int(os.getenv("SMALL_NUM_CUSTOMERS", 200))
NUM_TRANSACTIONS = int(os.getenv("SMALL_NUM_TRANSACTIONS", 1200))
MAX_ITEMS = int(os.getenv("SMALL_NUM_ITEMS", 4000))  # 上限 (平均 3 点程度)
NUM_PROMOTIONS = 10

START_DATE = datetime(2025, 1, 1)
END_DATE = START_DATE + timedelta(days=60)  # 約2ヶ月分 (学習テスト用)

# ==================== 生成関数 ====================

def generate_stores():
    stores = []
    for i in range(NUM_STORES):
        stores.append({
            "store_id": f"S{i+1:03d}",
            "store_name": f"テスト店舗{i+1}",
        })
    return pd.DataFrame(stores)


def generate_products():
    categories = ["食品", "日用品", "飲料", "菓子", "ヘルスケア"]
    products = []
    for i in range(NUM_PRODUCTS):
        cat = random.choice(categories)
        price = random.randint(100, 1500)
        cost = int(price * random.uniform(0.5, 0.8))
        products.append({
            "product_id": f"P{i+1:05d}",
            "product_name": f"商品{i+1}",
            "category_level1": cat,
            "retail_price_jpy": price,
            "cost_price_jpy": cost,
        })
    return pd.DataFrame(products)


def generate_customers():
    customers = []
    for i in range(NUM_CUSTOMERS):
        customers.append({
            "customer_id": f"C{i+1:06d}",
            "gender": random.choice(["男性", "女性"]),
            "age": random.randint(18, 75),
            "registration_date": (START_DATE - timedelta(days=random.randint(0, 400))).date(),
        })
    return pd.DataFrame(customers)


def generate_promotions():
    promos = []
    for i in range(NUM_PROMOTIONS):
        sd = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days - 5))
        ed = sd + timedelta(days=random.randint(3, 10))
        promos.append({
            "promotion_id": f"PR{i+1:03d}",
            "start_date": sd.date(),
            "end_date": ed.date(),
            "discount_rate": round(random.uniform(0.05, 0.30), 2),
        })
    return pd.DataFrame(promos)


def generate_transactions(customers_df, stores_df):
    txs = []
    customer_ids = customers_df.customer_id.tolist()
    store_ids = stores_df.store_id.tolist()
    for i in range(NUM_TRANSACTIONS):
        d = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
        amount = random.randint(300, 8000)
        txs.append({
            "transaction_id": f"T{i+1:07d}",
            "customer_id": random.choice(customer_ids),
            "transaction_date": d.date(),
            "store_id": random.choice(store_ids),
            "total_amount_jpy": amount,
        })
    return pd.DataFrame(txs)


def generate_transaction_items(transactions_df, products_df):
    items = []
    count = 0
    for _, tx in transactions_df.iterrows():
        # 各取引のアイテム数 (1-5)
        n_items = random.randint(1, 5)
        chosen = products_df.sample(n=min(n_items, len(products_df)))
        for _, p in chosen.iterrows():
            qty = random.randint(1, 3)
            unit_price = p.retail_price_jpy
            discount_price = int(unit_price * random.uniform(0.7, 1.0))
            line_total = discount_price * qty
            items.append({
                "transaction_item_id": f"TI{count+1:08d}",
                "transaction_id": tx.transaction_id,
                "product_id": p.product_id,
                "quantity": qty,
                "unit_price_jpy": unit_price,
                "discount_price_jpy": discount_price,
                "line_total_jpy": line_total,
            })
            count += 1
            if count >= MAX_ITEMS:
                break
        if count >= MAX_ITEMS:
            break
    return pd.DataFrame(items)

# ==================== メイン処理 ====================

def main(output_file: str):
    print("== 簡易テスト用データ生成開始 ==")
    stores_df = generate_stores(); print(f" 店舗: {len(stores_df)}")
    products_df = generate_products(); print(f" 商品: {len(products_df)}")
    customers_df = generate_customers(); print(f" 顧客: {len(customers_df)}")
    promotions_df = generate_promotions(); print(f" プロモーション: {len(promotions_df)}")
    transactions_df = generate_transactions(customers_df, stores_df); print(f" トランザクション: {len(transactions_df)}")
    items_df = generate_transaction_items(transactions_df, products_df); print(f" 明細: {len(items_df)}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with pd.ExcelWriter(output_file, engine="openpyxl") as w:
        stores_df.to_excel(w, sheet_name="店舗", index=False)
        products_df.to_excel(w, sheet_name="商品", index=False)
        customers_df.to_excel(w, sheet_name="顧客", index=False)
        transactions_df.to_excel(w, sheet_name="トランザクション", index=False)
        items_df.to_excel(w, sheet_name="トランザクション明細", index=False)
        promotions_df.to_excel(w, sheet_name="プロモーション", index=False)
    print(f"\n✓ 生成完了: {output_file}")
    print("サイズ軽量・学習高速化向け")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/uploaded/small_test.xlsx"
    main(out)
