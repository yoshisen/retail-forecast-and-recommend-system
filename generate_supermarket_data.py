"""
イオン東京圏スーパーマーケット販売データ生成器
データ分析テスト用の複数シートを含むExcelファイルを生成
LUMI Tokyo Metropolitan Area scale simulation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

# 設定ランダムシード（再現性のため）
random.seed(42)
np.random.seed(42)
fake = Faker('ja_JP')

# ==================== 配置パラメータ (LUMI東京圏規模) ====================
# LUMI東京圏: 約60店舗、10万人以上の会員、月間約50万件の取引
NUM_STORES = 65  # 東京圏のLUMI店舗数
NUM_CUSTOMERS = 120000  # イオン会員数
NUM_PRODUCTS = 3500  # 取扱商品数
NUM_TRANSACTIONS = 500000  # 月間取引数（約6ヶ月分で300万件）
NUM_TRANSACTION_ITEMS = 1500000  # 取引明細数
NUM_PROMOTIONS = 150  # プロモーション数

# ==================== 店舗テーブル生成 ====================
def generate_stores():
    stores = []
    store_types = ['イオンモール', 'イオンスタイル', 'まいばすけっと', 'マックスバリュ']
    location_types = ['商業地区', '住宅地', '駅前', 'ショッピングモール', '郊外']
    
    # 東京圏の主要エリア
    areas = [
        {'prefecture': '東京都', 'city': '新宿区', 'lat_range': (35.68, 35.71), 'lon_range': (139.69, 139.72)},
        {'prefecture': '東京都', 'city': '渋谷区', 'lat_range': (35.65, 35.68), 'lon_range': (139.69, 139.72)},
        {'prefecture': '東京都', 'city': '品川区', 'lat_range': (35.60, 35.63), 'lon_range': (139.71, 139.74)},
        {'prefecture': '東京都', 'city': '江東区', 'lat_range': (35.66, 35.69), 'lon_range': (139.79, 139.82)},
        {'prefecture': '東京都', 'city': '世田谷区', 'lat_range': (35.63, 35.66), 'lon_range': (139.63, 139.66)},
        {'prefecture': '東京都', 'city': '練馬区', 'lat_range': (35.73, 35.76), 'lon_range': (139.64, 139.67)},
        {'prefecture': '東京都', 'city': '足立区', 'lat_range': (35.77, 35.80), 'lon_range': (139.79, 139.82)},
        {'prefecture': '神奈川県', 'city': '横浜市', 'lat_range': (35.44, 35.47), 'lon_range': (139.62, 139.65)},
        {'prefecture': '神奈川県', 'city': '川崎市', 'lat_range': (35.52, 35.55), 'lon_range': (139.69, 139.72)},
        {'prefecture': '千葉県', 'city': '千葉市', 'lat_range': (35.60, 35.63), 'lon_range': (140.10, 140.13)},
        {'prefecture': '千葉県', 'city': '船橋市', 'lat_range': (35.69, 35.72), 'lon_range': (139.98, 140.01)},
        {'prefecture': '埼玉県', 'city': 'さいたま市', 'lat_range': (35.85, 35.88), 'lon_range': (139.64, 139.67)},
        {'prefecture': '埼玉県', 'city': '川口市', 'lat_range': (35.80, 35.83), 'lon_range': (139.72, 139.75)},
    ]
    
    for i in range(NUM_STORES):
        area = random.choice(areas)
        store_type = random.choice(store_types)
        
        stores.append({
            'store_id': f'LUMI{i+1:04d}',
            'store_name': f'イオン{area["city"]}{random.choice(["駅前", "中央", "南", "北", "東", "西"])}店',
            'store_type': store_type,
            'store_size_sqm': random.randint(1000, 8000),
            'opening_date': fake.date_between(start_date='-10y', end_date='-1y'),
            'location_type': random.choice(location_types),
            'prefecture': area['prefecture'],
            'city': area['city'],
            'postcode': f'{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'latitude': round(random.uniform(area['lat_range'][0], area['lat_range'][1]), 6),
            'longitude': round(random.uniform(area['lon_range'][0], area['lon_range'][1]), 6),
            'parking_spaces': random.randint(50, 500),
            'opening_hours': '09:00-23:00',
            'average_foot_traffic': random.randint(1000, 10000)
        })
    return pd.DataFrame(stores)

# ==================== 商品テーブル生成 ====================
def generate_products():
    products = []
    
    # 日本のスーパーマーケット商品カテゴリー
    categories = {
        '食品': {
            '乳製品': ['牛乳', 'ヨーグルト', 'チーズ', 'バター', '生クリーム'],
            '飲料': ['緑茶', 'コーヒー', '炭酸飲料', 'ジュース', 'ミネラルウォーター', 'スポーツドリンク'],
            'スナック菓子': ['ポテトチップス', 'せんべい', 'チョコレート', 'キャンディー', 'ナッツ', 'クッキー'],
            '調味料・油': ['醤油', '味噌', '料理酒', '食用油', 'みりん', '酢', 'だし'],
            '精肉': ['豚肉', '牛肉', '鶏肉', 'ひき肉'],
            '鮮魚': ['鮭', 'まぐろ', 'さば', 'いか', 'えび'],
            '米・麺': ['白米', '玄米', 'うどん', 'そば', 'ラーメン', 'パスタ'],
            '冷凍食品': ['冷凍餃子', '冷凍唐揚げ', '冷凍うどん', 'アイスクリーム'],
            'パン': ['食パン', 'フランスパン', '菓子パン', '惣菜パン'],
            '野菜': ['キャベツ', '人参', '玉ねぎ', 'じゃがいも', 'トマト', 'きゅうり'],
            '果物': ['りんご', 'みかん', 'バナナ', 'ぶどう', 'いちご']
        },
        '日用品': {
            '洗剤': ['洗濯洗剤', '食器用洗剤', 'ハンドソープ', 'トイレ用洗剤'],
            '紙製品': ['トイレットペーパー', 'ティッシュペーパー', 'ウェットティッシュ', 'キッチンペーパー'],
            '日用雑貨': ['ゴミ袋', 'ラップ', 'アルミホイル', 'ジップロック']
        },
        'ヘルスケア・ビューティー': {
            'ヘアケア': ['シャンプー', 'コンディショナー', 'ヘアトリートメント'],
            'ボディケア': ['ボディソープ', 'ハンドクリーム', 'ボディローション'],
            'オーラルケア': ['歯磨き粉', '歯ブラシ', 'デンタルフロス', 'マウスウォッシュ'],
            'スキンケア': ['化粧水', '乳液', '洗顔料', '日焼け止め']
        },
        'ホーム・キッチン': {
            'キッチン用品': ['フライパン', '鍋', '包丁', 'まな板', '食器', '箸'],
            '収納用品': ['タッパー', 'ジップロック', 'ラップ']
        }
    }
    
    # 日本のブランド
    brands = ['明治', '森永', 'グリコ', 'サントリー', 'キリン', 'アサヒ', 'コカ・コーラ', 
              'カルビー', '亀田製菓', 'キッコーマン', '味の素', '日清', 'ニッスイ', '伊藤ハム',
              '花王', 'ライオン', 'P&G', 'ユニリーバ', '資生堂', 'トップバリュ']
    
    product_id = 1
    for cat1, cat2_dict in categories.items():
        for cat2, cat3_list in cat2_dict.items():
            for cat3 in cat3_list:
                # 各細分カテゴリーで複数の製品を生成
                num_variations = random.randint(10, 20)
                for _ in range(num_variations):
                    if product_id > NUM_PRODUCTS:
                        break
                    
                    brand = random.choice(brands)
                    spec = random.choice(['100ml', '200ml', '500ml', '1L', '2L', '50g', '100g', '200g', '500g', '1kg', '個装', '箱入'])
                    retail_price = round(random.uniform(100, 3000), 0)  # 日本円
                    cost_price = round(retail_price * random.uniform(0.5, 0.8), 0)
                    
                    products.append({
                        'product_id': f'P{product_id:06d}',
                        'product_name': f'{brand}{cat3}{spec}',
                        'brand': brand,
                        'category_level1': cat1,
                        'category_level2': cat2,
                        'category_level3': cat3,
                        'product_description': f'{brand}の高品質な{cat3}',
                        'unit_of_measure': random.choice(['個', '本', '袋', '箱', 'パック']),
                        'package_size': spec,
                        'weight_g': round(random.uniform(50, 2000), 0),
                        'supplier_id': f'SUP{random.randint(1, 100):04d}',
                        'cost_price_jpy': int(cost_price),
                        'retail_price_jpy': int(retail_price),
                        'shelf_life_days': random.choice([7, 14, 30, 60, 90, 180, 365, 720]),
                        'perishable_flag': 1 if cat2 in ['乳製品', '精肉', '鮮魚', '野菜', '果物'] else 0,
                        'organic_flag': random.choice([0, 0, 0, 1]),
                        'private_label_flag': 1 if brand == 'トップバリュ' else 0,
                        'seasonal_flag': random.choice([0, 0, 0, 1]),
                        'launch_date': fake.date_between(start_date='-3y', end_date='-1m')
                    })
                    product_id += 1
                    
                if product_id > NUM_PRODUCTS:
                    break
            if product_id > NUM_PRODUCTS:
                break
        if product_id > NUM_PRODUCTS:
            break
    
    return pd.DataFrame(products)

# ==================== 顧客テーブル生成 ====================
def generate_customers():
    customers = []
    
    prefectures = ['東京都', '神奈川県', '千葉県', '埼玉県']
    income_levels = ['200万円未満', '200-400万円', '400-600万円', '600-800万円', '800万円以上']
    education_levels = ['中学校', '高校', '専門学校', '大学', '大学院']
    occupations = ['会社員', '公務員', '自営業', '学生', '主婦/主夫', '退職', 'パート・アルバイト']
    
    for i in range(NUM_CUSTOMERS):
        gender = random.choice(['男性', '女性'])
        age = random.randint(18, 80)
        birth_date = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
        
        customers.append({
            'customer_id': f'C{i+1:08d}',
            'registration_date': fake.date_between(start_date='-5y', end_date='-1m'),
            'gender': gender,
            'age': age,
            'birth_date': birth_date.date(),
            'income_level': random.choice(income_levels),
            'education_level': random.choice(education_levels),
            'occupation': random.choice(occupations),
            'marital_status': random.choice(['未婚', '既婚', '離婚']),
            'household_size': random.randint(1, 5),
            'has_children': random.choice([0, 1]),
            'children_age_range': random.choice(['0-3歳', '4-6歳', '7-12歳', '13-18歳', 'なし']) if random.random() > 0.5 else 'なし',
            'postcode': f'{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'prefecture': random.choice(prefectures),
            'city': fake.city(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'loyalty_tier': random.choice(['一般', 'シルバー', 'ゴールド', 'プラチナ']),
            'total_lifetime_value_jpy': round(random.uniform(50000, 5000000), 0),
            'preferred_store_id': f'LUMI{random.randint(1, NUM_STORES):04d}',
            'waon_card_number': f'WAON{random.randint(1000000000, 9999999999)}'
        })
    
    return pd.DataFrame(customers)

# ==================== プロモーションテーブル生成 ====================
def generate_promotions():
    promotions = []
    promotion_types = ['割引', '２つ買うと１つ無料', '○円以上で割引', '２個目半額', 'ポイント２倍']
    promotion_names = ['春のセール', '夏のセール', '秋のセール', '冬のセール', 
                       'お正月セール', 'ゴールデンウィークセール', '年末セール',
                       '新生活応援セール', '週末セール', '平日セール']
    
    start_date = datetime(2024, 1, 1)
    
    for i in range(NUM_PROMOTIONS):
        promo_start = start_date + timedelta(days=random.randint(0, 600))
        promo_end = promo_start + timedelta(days=random.randint(3, 21))
        
        promotions.append({
            'promotion_id': f'PROMO{i+1:05d}',
            'promotion_name': f'{random.choice(promotion_names)}',
            'promotion_type': random.choice(promotion_types),
            'start_date': promo_start.date(),
            'end_date': promo_end.date(),
            'discount_rate': round(random.uniform(0.1, 0.5), 2) if random.random() > 0.5 else None,
            'min_purchase_amount_jpy': random.choice([0, 1000, 2000, 3000, 5000]) if random.random() > 0.3 else 0,
            'max_discount_jpy': random.choice([100, 300, 500, 1000, 2000]) if random.random() > 0.3 else None
        })
    
    return pd.DataFrame(promotions)

# ==================== トランザクションテーブル生成 ====================
def generate_transactions(customers_df, stores_df):
    transactions = []
    
    start_date = datetime(2024, 5, 1)  # 6ヶ月間のデータ
    end_date = datetime(2025, 10, 31)
    
    payment_methods = ['現金', 'クレジットカード', 'デビットカード', 'WAON', 'PayPay', '楽天Pay', 'LINE Pay']
    
    # 顧客IDのリストを作成（頻繁に買い物する顧客を多めに）
    customer_ids = list(customers_df['customer_id'].values)
    # 20%の顧客が60%の取引を行うというパレートの法則を適用
    frequent_customers = random.sample(customer_ids, int(len(customer_ids) * 0.2))
    customer_pool = customer_ids + frequent_customers * 2
    
    for i in range(NUM_TRANSACTIONS):
        trans_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        
        # 営業時間内にランダムな時間を生成（9:00-23:00）
        trans_time = trans_date.replace(
            hour=random.randint(9, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        total_amount = round(random.uniform(500, 15000), 0)  # 日本円
        discount_amount = round(total_amount * random.uniform(0, 0.15), 0) if random.random() > 0.6 else 0
        
        transactions.append({
            'transaction_id': f'TRX{i+1:010d}',
            'customer_id': random.choice(customer_pool),
            'transaction_date': trans_date.date(),
            'transaction_time': trans_time.time(),
            'store_id': random.choice(stores_df['store_id'].values),
            'cashier_id': f'CSH{random.randint(1, 200):04d}',
            'payment_method': random.choice(payment_methods),
            'total_amount_jpy': int(total_amount),
            'discount_amount_jpy': int(discount_amount),
            'tax_amount_jpy': int((total_amount - discount_amount) * 0.10),  # 消費税10%
            'waon_points_used': random.choice([0, 0, 0, random.randint(10, 500)]),
            'waon_points_earned': int((total_amount - discount_amount) * 0.005),  # 0.5%ポイント還元
            'coupon_id': f'COUP{random.randint(1, 500):05d}' if random.random() > 0.8 else None,
            'receipt_number': f'RCP{i+1:012d}'
        })
        
        if (i + 1) % 50000 == 0:
            print(f'  トランザクション生成中: {i+1}/{NUM_TRANSACTIONS}')
    
    return pd.DataFrame(transactions)

# ==================== トランザクション明細テーブル生成 ====================
def generate_transaction_items(transactions_df, products_df):
    items = []
    
    # 各トランザクションに対して1-10個の商品明細を生成
    transaction_count = 0
    for _, trans in transactions_df.iterrows():
        num_items = random.randint(1, 10)
        selected_products = products_df.sample(n=min(num_items, len(products_df)))
        
        for idx, product in selected_products.iterrows():
            quantity = random.randint(1, 5)
            unit_price = product['retail_price_jpy']
            original_price = unit_price
            
            # ランダムに割引を適用
            if random.random() > 0.75:
                discount_price = round(unit_price * random.uniform(0.7, 0.95), 0)
            else:
                discount_price = unit_price
            
            line_total = int(discount_price * quantity)
            
            items.append({
                'transaction_item_id': f'TI{len(items)+1:010d}',
                'transaction_id': trans['transaction_id'],
                'product_id': product['product_id'],
                'product_barcode': f'49{random.randint(10000000000, 99999999999)}',  # JAN code format
                'quantity': quantity,
                'unit_price_jpy': int(unit_price),
                'original_price_jpy': int(original_price),
                'discount_price_jpy': int(discount_price),
                'line_total_jpy': line_total,
                'promotion_id': f'PROMO{random.randint(1, NUM_PROMOTIONS):05d}' if random.random() > 0.8 else None,
                'return_flag': 1 if random.random() > 0.98 else 0
            })
            
            if len(items) >= NUM_TRANSACTION_ITEMS:
                break
        
        transaction_count += 1
        if transaction_count % 50000 == 0:
            print(f'  トランザクション明細生成中: {len(items)}/{NUM_TRANSACTION_ITEMS}')
        
        if len(items) >= NUM_TRANSACTION_ITEMS:
            break
    
    return pd.DataFrame(items)

# ==================== 在庫テーブル生成 ====================
def generate_inventory(products_df, stores_df):
    inventory = []
    inventory_id = 1
    
    print("  在庫データ生成中...")
    
    # 各店舗に部分的な商品の在庫を生成（全商品ではない）
    for idx, store_id in enumerate(stores_df['store_id']):
        # 各店舗はランダムに70-90%の商品を在庫
        num_products = int(len(products_df) * random.uniform(0.7, 0.9))
        selected_products = products_df.sample(n=num_products)
        
        for _, product in selected_products.iterrows():
            stock_qty = random.randint(0, 800)
            reorder_point = random.randint(50, 200)
            
            inventory.append({
                'inventory_id': f'INV{inventory_id:08d}',
                'product_id': product['product_id'],
                'store_id': store_id,
                'stock_quantity': stock_qty,
                'reorder_point': reorder_point,
                'max_stock_level': reorder_point * 5,
                'last_restock_date': fake.date_between(start_date='-30d', end_date='today'),
                'expiry_date': fake.date_between(start_date='today', end_date='+180d') if product['perishable_flag'] else None,
                'shelf_location': f'{random.choice(["A", "B", "C", "D", "E", "F"])}-{random.randint(1, 30):02d}-{random.randint(1, 8):02d}',
                'days_on_shelf': random.randint(1, 90)
            })
            inventory_id += 1
        
        if (idx + 1) % 10 == 0:
            print(f'    店舗 {idx + 1}/{len(stores_df)} 完了')
    
    return pd.DataFrame(inventory)

# ==================== 祝日テーブル生成 ====================
def generate_holidays():
    holidays = [
        {'date': '2024-01-01', 'holiday_name': '元日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-01-08', 'holiday_name': '成人の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-02-11', 'holiday_name': '建国記念の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2024-02-23', 'holiday_name': '天皇誕生日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2024-03-20', 'holiday_name': '春分の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2024-04-29', 'holiday_name': '昭和の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-05-03', 'holiday_name': '憲法記念日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-05-04', 'holiday_name': 'みどりの日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-05-05', 'holiday_name': 'こどもの日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-07-15', 'holiday_name': '海の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-08-11', 'holiday_name': '山の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-09-16', 'holiday_name': '敬老の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-09-22', 'holiday_name': '秋分の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2024-10-14', 'holiday_name': 'スポーツの日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2024-11-03', 'holiday_name': '文化の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2024-11-23', 'holiday_name': '勤労感謝の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2025-01-01', 'holiday_name': '元日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-01-13', 'holiday_name': '成人の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-02-11', 'holiday_name': '建国記念の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2025-02-23', 'holiday_name': '天皇誕生日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2025-03-20', 'holiday_name': '春分の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2025-04-29', 'holiday_name': '昭和の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-05-03', 'holiday_name': '憲法記念日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-05-04', 'holiday_name': 'みどりの日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-05-05', 'holiday_name': 'こどもの日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-07-21', 'holiday_name': '海の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-08-11', 'holiday_name': '山の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-09-15', 'holiday_name': '敬老の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
        {'date': '2025-09-23', 'holiday_name': '秋分の日', 'holiday_type': '国民の祝日', 'is_long_weekend': 0},
        {'date': '2025-10-13', 'holiday_name': 'スポーツの日', 'holiday_type': '国民の祝日', 'is_long_weekend': 1},
    ]
    
    return pd.DataFrame(holidays)

# ==================== 天気テーブル生成 ====================
def generate_weather(stores_df):
    weather_data = []
    
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2025, 10, 31)
    
    weather_conditions = ['晴れ', '曇り', '雨', '小雨', '大雨', '雪', '強風']
    
    # 各店舗の都道府県で天気データを生成
    prefectures = stores_df['prefecture'].unique()
    
    print("  天気データ生成中...")
    
    current_date = start_date
    day_count = 0
    while current_date <= end_date:
        for prefecture in prefectures:
            # 季節に応じた温度範囲
            month = current_date.month
            if month in [12, 1, 2]:  # 冬
                temp_range = (-2, 12)
            elif month in [3, 4, 5]:  # 春
                temp_range = (8, 22)
            elif month in [6, 7, 8]:  # 夏
                temp_range = (22, 36)
            else:  # 秋
                temp_range = (12, 25)
            
            weather_data.append({
                'date': current_date.date(),
                'prefecture': prefecture,
                'temperature_celsius': round(random.uniform(temp_range[0], temp_range[1]), 1),
                'weather_condition': random.choice(weather_conditions),
                'humidity_percent': random.randint(40, 90),
                'precipitation_mm': round(random.uniform(0, 50), 1) if random.random() > 0.7 else 0
            })
        
        current_date += timedelta(days=1)
        day_count += 1
        if day_count % 100 == 0:
            print(f'    {day_count}日分完了')
    
    return pd.DataFrame(weather_data)

# ==================== 顧客行動テーブル生成 ====================
def generate_customer_behavior(customers_df, transactions_df):
    behavior = []
    
    print("  顧客行動データ生成中...")
    
    for idx, customer_id in enumerate(customers_df['customer_id']):
        customer_trans = transactions_df[transactions_df['customer_id'] == customer_id]
        
        if len(customer_trans) > 0:
            avg_basket = round(customer_trans['total_amount_jpy'].mean(), 0)
            purchase_freq = len(customer_trans)
            last_purchase = customer_trans['transaction_date'].max()
            days_since = (datetime(2025, 10, 31).date() - pd.to_datetime(last_purchase).date()).days
        else:
            avg_basket = 0
            purchase_freq = 0
            last_purchase = None
            days_since = 999
        
        behavior.append({
            'customer_id': customer_id,
            'avg_basket_size': round(random.uniform(3, 20), 1),
            'avg_transaction_value_jpy': int(avg_basket) if avg_basket > 0 else int(random.uniform(1000, 8000)),
            'purchase_frequency': purchase_freq,
            'last_purchase_date': last_purchase,
            'days_since_last_purchase': days_since,
            'preferred_categories': random.choice(['食品', '日用品', 'ヘルスケア・ビューティー', '食品,日用品']),
            'price_sensitivity': random.choice(['低', '中', '高']),
            'promotion_response_rate': round(random.uniform(0.1, 0.8), 2),
            'channel_preference': random.choice(['店舗', 'オンライン', 'オムニチャネル']),
            'churn_risk_score': round(random.uniform(0, 1), 3)
        })
        
        if (idx + 1) % 10000 == 0:
            print(f'    {idx + 1}/{len(customers_df)} 顧客完了')
    
    return pd.DataFrame(behavior)

# ==================== メイン関数 ====================
def main():
    print("=" * 70)
    print("イオン東京圏スーパーマーケット販売データ生成開始")
    print("=" * 70)
    
    print("\n[1/10] 店舗データ生成中...")
    stores_df = generate_stores()
    print(f"  ✓ 完了: {len(stores_df)}店舗")
    
    print("\n[2/10] 商品データ生成中...")
    products_df = generate_products()
    print(f"  ✓ 完了: {len(products_df)}商品")
    
    print("\n[3/10] 顧客データ生成中...")
    customers_df = generate_customers()
    print(f"  ✓ 完了: {len(customers_df)}顧客")
    
    print("\n[4/10] プロモーションデータ生成中...")
    promotions_df = generate_promotions()
    print(f"  ✓ 完了: {len(promotions_df)}プロモーション")
    
    print("\n[5/10] トランザクションデータ生成中...")
    transactions_df = generate_transactions(customers_df, stores_df)
    print(f"  ✓ 完了: {len(transactions_df):,}トランザクション")
    
    print("\n[6/10] トランザクション明細データ生成中...")
    transaction_items_df = generate_transaction_items(transactions_df, products_df)
    print(f"  ✓ 完了: {len(transaction_items_df):,}明細")
    
    print("\n[7/10] 在庫データ生成中...")
    inventory_df = generate_inventory(products_df, stores_df)
    print(f"  ✓ 完了: {len(inventory_df):,}在庫レコード")
    
    print("\n[8/10] 祝日データ生成中...")
    holidays_df = generate_holidays()
    print(f"  ✓ 完了: {len(holidays_df)}祝日")
    
    print("\n[9/10] 天気データ生成中...")
    weather_df = generate_weather(stores_df)
    print(f"  ✓ 完了: {len(weather_df):,}天気レコード")
    
    print("\n[10/10] 顧客行動データ生成中...")
    customer_behavior_df = generate_customer_behavior(customers_df, transactions_df)
    print(f"  ✓ 完了: {len(customer_behavior_df):,}顧客行動レコード")
    
    # Excelファイルに保存（各テーブルを別シートに）
    print("\n" + "=" * 70)
    print("Excelファイルに保存中...")
    print("=" * 70)
    output_file = 'data/uploaded/lumi_tokyo_sales_data.xlsx'
    
    # ディレクトリが存在しない場合は作成
    import os
    os.makedirs('data/uploaded', exist_ok=True)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        stores_df.to_excel(writer, sheet_name='店舗', index=False)
        products_df.to_excel(writer, sheet_name='商品', index=False)
        customers_df.to_excel(writer, sheet_name='顧客', index=False)
        transactions_df.to_excel(writer, sheet_name='トランザクション', index=False)
        transaction_items_df.to_excel(writer, sheet_name='トランザクション明細', index=False)
        promotions_df.to_excel(writer, sheet_name='プロモーション', index=False)
        inventory_df.to_excel(writer, sheet_name='在庫', index=False)
        holidays_df.to_excel(writer, sheet_name='祝日', index=False)
        weather_df.to_excel(writer, sheet_name='天気', index=False)
        customer_behavior_df.to_excel(writer, sheet_name='顧客行動', index=False)
    
    print(f"\n✓ Excelファイル生成完了: {output_file}")
    print("\n" + "=" * 70)
    print("データ統計サマリー")
    print("=" * 70)
    print(f"  📍 店舗テーブル:              {len(stores_df):>10,} レコード")
    print(f"  📦 商品テーブル:              {len(products_df):>10,} レコード")
    print(f"  👤 顧客テーブル:              {len(customers_df):>10,} レコード")
    print(f"  🛒 トランザクションテーブル:  {len(transactions_df):>10,} レコード")
    print(f"  📋 トランザクション明細:      {len(transaction_items_df):>10,} レコード")
    print(f"  🎉 プロモーションテーブル:    {len(promotions_df):>10,} レコード")
    print(f"  📊 在庫テーブル:              {len(inventory_df):>10,} レコード")
    print(f"  🎌 祝日テーブル:              {len(holidays_df):>10,} レコード")
    print(f"  ⛅ 天気テーブル:              {len(weather_df):>10,} レコード")
    print(f"  📈 顧客行動テーブル:          {len(customer_behavior_df):>10,} レコード")
    print("=" * 70)
    print("\n期間: 2024年5月1日 ～ 2025年10月31日")
    print("対象: イオン東京圏（東京都、神奈川県、千葉県、埼玉県）")
    print("\nデータ生成完了！データ分析にご活用ください。")
    print("=" * 70)

if __name__ == "__main__":
    main()
