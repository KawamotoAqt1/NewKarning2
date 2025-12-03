# フォルダ構造と運用方針

## 📁 フォルダ構造

```
project_root/
  dataset_all/      ← すべてのSVGとCSVが混在（元データの倉庫）
    *.svg
    *.csv
  dataset_train/    ← ユーザーが「学習に使う」と判断したSVG+CSVペアだけ（手動コピー）
    *.svg
    *.csv
  output_json/
    all/      ← dataset_all を一括処理した結果（必要なら）
    train/    ← dataset_train を処理した結果（学習用）
```

## 🎯 運用フロー

### 1. データ準備
- すべてのSVGとCSVを `dataset_all/` に配置（混在）

### 2. 目視確認と選別（手動）
- Inkscape等でSVGを開いてレイアウトを確認
- 「横書き」「カーニング学習に使える」と判断したものだけを選別
- 選別したSVG+CSVペアを `dataset_train/` にコピー
  - 例：`06099095.svg` と `06099095.csv` をセットでコピー

### 3. JSON生成（自動）
```bash
# 学習用データを処理（デフォルト）
python batch_process.py

# または明示的に指定
python batch_process.py ./dataset_train ./output_json/train

# dataset_allを処理する場合（必要なら）
python batch_process.py ./dataset_all ./output_json/all
```

注意: `dataset_train/` と `dataset_all/` は、SVGとCSVが同じフォルダに混在している構造です。

### 4. 学習
- 学習用スクリプトは `output_json/train/` のデータのみを読み込む
- `output_json/all/` は学習に含めない

## ⚠️ 重要な注意事項

- **学習データは「ユーザーが目視で確認済みのSVG+CSVセットだけ」**
- **学習用パイプラインは `dataset_train` のみを入力とする**
- **`dataset_all` は自動では学習に含めない**
- **横書き判定は自動化しない（ユーザーが目視で行う）**

## 🛠 コードの使い方

### 学習用パイプライン（デフォルト）
```bash
python batch_process.py
```
- 入力: `./dataset_train`（svg/ と csv/ サブディレクトリ）
- 出力: `./output_json/train/`

### 全件処理（必要なら）
```bash
python batch_process.py ./dataset_all ./output_json/all
```
- 入力: `./dataset_all`（svg/ と csv/ サブディレクトリ）
- 出力: `./output_json/all/`
