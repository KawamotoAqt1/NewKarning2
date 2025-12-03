# Phase1モデル生成手順

`phase1_model.json`を生成するための手順です。

## 📋 全体のワークフロー

```
SVG/CSVファイル
    ↓
[Step 1] batch_process.py
    ↓
JSONファイル (output_json/train/*.json)
    ↓
[Step 2] aggregate_pairs.py
    ↓
pairs_aggregated.csv
    ↓
[Step 3] build_phase1_model.py
    ↓
phase1_model.json
```

## 🚀 実行手順

### Step 1: SVG/CSVからJSONファイルを生成

SVGファイルとCSVファイルのペアから、文字間隔情報を含むJSONファイルを生成します。

```bash
# デフォルト設定で実行（dataset_train/ → output_json/train/）
python batch_process.py

# または、カスタムディレクトリを指定
python batch_process.py <入力ディレクトリ> <出力ディレクトリ>
```

**入力:**
- `dataset_train/` フォルダ内のSVG/CSVペア
  - 例: `06099095.svg`, `06099095.csv`

**出力:**
- `output_json/train/` フォルダ内のJSONファイル
  - 例: `06099095_01_NAKATANI.json`, `06099095_02_SAITO.json`

---

### Step 2: JSONファイルからCSVを集計

複数のJSONファイルから文字ペア情報を集計して、1つのCSVファイルにまとめます。

```bash
python aggregate_pairs.py
```

**設定:**
- 入力ディレクトリ: `./output_json/train` (デフォルト)
- 出力ファイル: `./pairs_aggregated.csv` (デフォルト)

**出力:**
- `pairs_aggregated.csv` - すべての文字ペアを集計したCSVファイル
  - カラム: `sample_id`, `left_char`, `right_char`, `left_font`, `right_font`, `gap_actual`, `gap_norm_left`, `gap_norm_right`, など

---

### Step 3: CSVからPhase1モデルJSONを生成

集計されたCSVファイルから、フォント別・文字ペア別の平均値を計算してモデルJSONを生成します。

```bash
python build_phase1_model.py
```

**設定:**
- 入力ファイル: `pairs_aggregated.csv` (デフォルト)
- 出力ファイル: `phase1_model.json` (デフォルト)

**フィルタ設定:**
- `MIN_GAPNORM = -1.0` - これ未満のgap_normは除外（重なりすぎ）
- `MAX_GAPNORM = 1.0` - これより大きいgap_normは除外（広げすぎ）
- `MIN_COUNT = 1` - 集計結果出力時、ペアごとの最小採用件数

**出力:**
- `phase1_model.json` - Phase1カーニングモデル
  - 構造:
    ```json
    {
      "Gothic": {
        "K|A": {
          "gap_norm_left_avg": 0.30,
          "gap_norm_right_avg": 0.28,
          "gap_actual_avg": 9.33,
          "count": 2
        },
        ...
      },
      "Mincho": { ... },
      ...
    }
    ```

---

## 📝 一括実行（全ステップ）

すべてのステップを順番に実行する場合：

```bash
# Step 1: JSONファイル生成
python batch_process.py

# Step 2: CSV集計
python aggregate_pairs.py

# Step 3: モデル生成
python build_phase1_model.py
```

---

## ⚙️ カスタマイズ

### aggregate_pairs.py の設定変更

`aggregate_pairs.py` を編集:

```python
JSON_DIR = "./output_json/train"  # JSONファイルが格納されているフォルダ
OUTPUT_CSV = "./pairs_aggregated.csv"  # 出力先のCSVファイル
```

### build_phase1_model.py の設定変更

`build_phase1_model.py` を編集:

```python
CSV_PATH = "pairs_aggregated.csv"  # 入力CSVファイル
OUTPUT_JSON_PATH = "phase1_model.json"  # 出力JSONファイル

# 異常値フィルタ設定
MIN_GAPNORM = -1.0  # 最小値
MAX_GAPNORM = 1.0   # 最大値
MIN_COUNT = 1       # 最小サンプル数
```

---

## 🔍 確認方法

### 生成されたモデルの統計を確認

`build_phase1_model.py` を実行すると、最後に統計情報が表示されます：

```
生成されたモデルの統計:
  Gothic: 20 ペア
  Mincho: 15 ペア
  MaruGothic: 25 ペア
  Brush: 4 ペア
  Design: 15 ペア
  合計: 79 ペア
```

### モデルファイルの内容を確認

```bash
# JSONファイルを整形して表示（jqが必要な場合）
cat phase1_model.json | python -m json.tool

# または、Pythonで確認
python -c "import json; data = json.load(open('phase1_model.json')); print(f'フォント数: {len(data)}'); [print(f'{k}: {len(v)} ペア') for k, v in data.items()]"
```

---

## ⚠️ 注意事項

1. **データの順序**: Step 1 → Step 2 → Step 3 の順で実行してください
2. **ファイルパス**: 各スクリプトはデフォルトのパスを想定しています。カスタムパスを使用する場合は設定を変更してください
3. **エンコーディング**: CSVファイルはShift-JIS（cp932）でエンコードされている必要があります
4. **異常値**: `MIN_GAPNORM` と `MAX_GAPNORM` の範囲外の値は自動的に除外されます

---

## 🐛 トラブルシューティング

### pairs_aggregated.csv が見つからない

- Step 2 (`aggregate_pairs.py`) が正常に実行されたか確認
- `output_json/train/` フォルダにJSONファイルが存在するか確認

### phase1_model.json が生成されない

- `pairs_aggregated.csv` が存在するか確認
- CSVファイルの形式が正しいか確認（カラム名が一致しているか）
- エラーメッセージを確認（異常値が多すぎる場合など）

### モデルに含まれるペア数が少ない

- `MIN_COUNT` の値を小さくする（例: `MIN_COUNT = 1`）
- 学習データ（JSONファイル）を増やす
- 異常値フィルタ（`MIN_GAPNORM`, `MAX_GAPNORM`）の範囲を広げる

