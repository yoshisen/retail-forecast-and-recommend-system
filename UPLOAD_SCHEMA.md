# Excel アップロード仕様 / Sheet & Field 要求

本システムはアップロードされた Excel ファイルの複数シートを自動解析し、標準化された内部名へマッピングした上で予測 (Forecast) / 推薦 (Recommendation) モデルの学習に利用します。ここでは **必要なシート名 / エイリアス**, **フィールド名マッピング**, **必須 / 任意フィールド**, **データ型 / 用途** を整理します。

---
## 1. シート名マッピング (Sheet Aliases)
以下の標準シート名を内部で使用します。アップロード側のシート名はエイリアス (大小文字・スペース・ハイフン・下線除去後) が一致すれば認識されます。

| 標準名 | 主なエイリアス例 | 用途 | 学習への必須性 |
|--------|------------------|------|----------------|
| transaction | transaction, transactions, orders, order, 取引, トランザクション | 日次/購買メタ情報 (顧客, 店舗, 日付) | 推薦: 必須 (customer_id 供給), 予測: 補助 |
| transaction_items | transaction_items, transactionitems, orderitems, order_details, 取引明細, トランザクション明細 | 個別商品購買行 | 予測/推薦: 必須 |
| product | product, products, item, items, 商品 | 商品属性 (カテゴリ, 価格) | 予測/推薦: 必須 |
| customer | customer, customers, user, users, member, 顧客 | 顧客属性 (年齢等) | 推薦: 望ましい (Cold start 改善) |
| store | store, stores, shop, location, 店舗 | 店舗属性 (地理等) | 予測: 望ましい |
| promotion | promotion, promotions, campaign, プロモーション | 期間中割引フラグ生成 | 予測: 任意 |
| inventory | inventory, stock, 在庫 | 在庫・補充ポイント | 予測: 任意 |
| weather | weather, climate, 天気 | 気象影響特徴 | 予測: 任意 |
| holiday | holiday, holidays, 祝日 | 祝日フラグ生成 | 予測: 任意 |
| customer_behavior | customer_behavior, customerbehavior, 顧客行動 | 高度行動指標 (LTV 等) | 推薦: 任意 |
| product_association | product_association, association, 商品関連 | 商品間関連 (未実装) | 解析のみ (今後) |
| review | review, reviews, feedback, 評価 | レビュー感情 (未実装) | 解析のみ (今後) |

最低構成 (学習成立する最小セット):
```
transaction_items
transaction
product
```
推薦で顧客軸を活かすには `customer` 追加推奨。

---
## 2. フィールド標準化 (Field Mapping)
列名はクリーニング後 (小文字化 / 空白・ハイフン→下線 / 重複下線除去) 次のマッピングにより内部標準名に変換されます。未登録名は正規化後そのまま保持。

### 2.1 Transaction シート
| 標準フィールド | エイリアス例 | 型 | 必須 | 用途 |
|----------------|-------------|----|------|------|
| transaction_id | transactionid, trans_id, order_id | string | 必須 | キー、結合・集計 |
| customer_id | customerid, cust_id, user_id | string | 推薦で必須 | 顧客行動結合 |
| transaction_date | transactiondate, date, order_date | date | 推奨 | 時系列特徴 (day/week 等) |
| transaction_time | transactiontime, time | time/datetime | 任意 | 時間帯特徴 (未強化) |
| store_id | storeid, shop_id, location_id | string | 推奨 | 店舗別集計 |
| total_amount | totalamount, amount, total_price | numeric | 任意 | 売上金額補助 (sales_amount) |

その他列は保持され補助的特徴に利用される可能性があります。

### 2.2 Transaction Items シート (必須)
| 標準フィールド | エイリアス例 | 型 | 必須 | 用途 |
|----------------|-------------|----|------|------|
| transaction_id | 同上 | string | 必須 | Transaction 結合 |
| product_id | productid, item_id | string | 必須 | 商品識別 |
| quantity | quantity, qty | numeric | 推奨 | 販売数量 (sales_quantity) |
| unit_price / retail_price_jpy | unit_price, price, retail_price | numeric | 任意 | 価格特徴 |
| discount_price_jpy | discount_price | numeric | 任意 | 割引状況特徴 |
| original_price_jpy | original_price | numeric | 任意 | 割引差分計算 |
| line_total / line_total_jpy | line_total | numeric | 任意 | 売上金額 (sales_amount) |

### 2.3 Product シート (必須)
| 標準フィールド | エイリアス例 | 型 | 必須 | 用途 |
|----------------|-------------|----|------|------|
| product_id | productid, prod_id, item_id | string | 必須 | キー |
| product_name | productname, name | string | 推奨 | 表示・推薦結果拡充 |
| category_level1 | category1, main_category | string | 推奨 | コンテンツ類似計算 |
| category_level2 | category2, sub_category | string | 任意 | 階層特徴 |
| category_level3 | category3 | string | 任意 | 階層特徴細分 |
| retail_price | retail_price, price, unit_price | numeric | 推奨 | 価格帯 binning / 正規化 |
| cost_price | cost_price, cost | numeric | 任意 | 利益率等 (将来) |
| launch_date | (未マッピング、列名に date を含める) | date | 任意 | 新商品フラグ (将来) |

### 2.4 Customer シート (推薦強化用)
| 標準フィールド | エイリアス例 | 型 | 必須 | 用途 |
|----------------|-------------|----|------|------|
| customer_id | customerid, user_id | string | 推薦で推奨 | 行動マトリクス軸 |
| gender | gender, sex | category | 任意 | セグメント特徴 |
| age | age, customer_age | numeric | 任意 | 年齢帯特徴 |
| registration_date | registration_date, join_date | date | 任意 | 会員期間特徴 |
| loyalty_tier | (正規化後) | category | 任意 | 高度推薦 (将来) |

### 2.5 Store シート
| 標準フィールド | 型 | 用途 |
|----------------|----|------|
| store_id | string | 集計キー |
| prefecture | string | 天気/祝日結合 |
| store_type | category | 店舗種別特徴 |

### 2.6 Promotion シート
| フィールド | 型 | 用途 |
|------------|----|------|
| promotion_id | string | 識別 |
| start_date | date | 期間判定 |
| end_date | date | 期間判定 |
| discount_rate | numeric | 割引強度特徴 |

### 2.7 Weather シート
| フィールド | 型 | 用途 |
|------------|----|------|
| date | date | マージキー |
| prefecture | string | 地域マッチ |
| temperature_celsius | numeric | 気温特徴 |
| precipitation_mm | numeric | 降水量特徴 |
| humidity_percent | numeric | 湿度特徴 |

### 2.8 Holiday シート
| フィールド | 型 | 用途 |
|------------|----|------|
| date | date | マージ |
| holiday_name | string | 説明 (任意) |

### 2.9 Inventory シート
| フィールド | 型 | 用途 |
|------------|----|------|
| product_id | string | 商品キー |
| store_id | string | 店舗キー |
| stock_quantity | numeric | 在庫状況特徴 |
| reorder_point | numeric | 補充閾値 |

---
## 3. 型推論ルール
1. 列名に `date` / `time` / `day` / `timestamp` を含む場合のみ日時推論。
2. 数量・金額候補 (quantity, *_price*, line_total, total_amount 等) は数値優先。
3. ユニーク率 < 5% の列はカテゴリ化 (低カーディナリティ)。
4. 誤って datetime 化された数値列は再強制で数値化。

---
## 4. 必須/任意まとめ
| 用途 | 最低必須シート | 推奨追加 | 効果 |
|------|----------------|----------|------|
| 予測 (販売数量) | transaction_items, product | transaction, store, promotion, holiday, weather, inventory | 特徴量増加 → 精度向上 |
| 推薦 (顧客×商品) | transaction_items, transaction, product | customer, store, promotion | 個人化 / 多様性改善 |

---
## 5. 期待するデータ品質
| 項目 | 基準 |
|------|------|
| transaction_id 重複率 | < 0.1% 推奨 |
| quantity 負値 | 0 (返品は別列 return_flag 等で管理) |
| 日付欠損率 | < 1% 推奨 |
| 価格 (retail_price) 0 値 | 高頻度は異常として警告 |

---
## 6. サンプル (最小構成)
```text
Sheet: トランザクション明細
transaction_id, product_id, quantity, unit_price_jpy, discount_price_jpy, line_total_jpy

Sheet: トランザクション
transaction_id, customer_id, transaction_date, store_id, total_amount_jpy

Sheet: 商品
product_id, product_name, category_level1, retail_price_jpy, cost_price_jpy
```

---
## 7. よくあるエラーと対策
| エラー | 原因 | 対策 |
|--------|------|------|
| 必須シート不足 (missing_sheets) | `transaction_items` 未提供 | シート名スペル確認 (明細) |
| datetime64 sum error | 数値列誤認識 | 列名に余計な 'date' を含めない / 最新パーサ使用 |
| モデル未訓練 400 | 自動訓練未完了 | Dashboard で進捗確認 → 再訓練ボタン |
| 推薦件数少ない | 顧客データ欠如 or sparse | `customer` シート追加 + 期間延長 |

---
## 8. 拡張予定
- review / sentiment → 需要影響特徴追加
- product_association → バスケット分析強化
- customer_behavior → 高精細セグメント推薦

---
## 9. FAQ
**Q. 列名は日本語でも良いか?** → 可能だがマッピング辞書にない場合そのまま正規化名で保持される。モデルが利用する主要キー (transaction_id, product_id, quantity, date 等) は英数字推奨。

**Q. 同じ情報を複数列に持っている場合?** → 最初に認識された列が使用され、重複は無視される（前処理で統合を推奨）。

**Q. 日付+時刻を分けて持っている場合?** → 現在は日付列を優先し時刻列は補助。将来は時間帯特徴強化予定。

---
## 10. 連携のための最終 Checklist
- [ ] 必須シート (transaction_items, transaction, product) が存在
- [ ] 主要キー列に NULL が無い
- [ ] quantity / price 系が数値型
- [ ] 日付列が正しく認識されている (Dashboard の parse_report 参照)
- [ ] 不要巨大シート削除済み (サイズ軽量化)

以上。新しいフィールドを追加したい場合はこのファイルに追記してください。
