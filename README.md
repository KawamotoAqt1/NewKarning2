# SVG+CSV から Phase1 学習用JSON生成ツール

このプロジェクトは、SVGファイルとCSVファイルのペアから、文字間隔（gap_actual）を計算して学習用JSONを生成するPythonスクリプト群です。

## 📁 プロジェクト構成

```
.
├── svg_parser.py      # SVG解析モジュール（bounding box計算）
├── csv_loader.py      # CSV読み込みモジュール（Shift-JIS対応）
├── gap_extractor.py   # 結合・ソート・gap_actual計算
├── export_json.py     # 学習用JSON出力
├── batch_process.py   # 一括処理スクリプト（メイン）
├── requirements.txt   # 依存関係
└── README.md          # このファイル
```

## 🎯 機能

1. **SVG解析**: SVGファイルから各文字（path要素）のbounding boxを計算
2. **CSV読み込み**: Shift-JISでエンコードされたCSVファイルを読み込み
3. **データ結合**: SVGとCSVのデータをidで結合
4. **文字間隔計算**: CSVの行順（文字列順）に基づいて、隣接文字間のgap_actualを計算
5. **JSON出力**: 学習用JSON形式で結果を出力

## 📋 前提条件

- Python 3.7以上
- 標準ライブラリのみで動作（外部依存なし）

## 🚀 セットアップ

### 1. 仮想環境の作成（推奨）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

**注意**: 現在の実装は標準ライブラリのみを使用しているため、`requirements.txt`は空です。必要に応じて`svgpathtools`などのライブラリを追加できます。

## 📂 フォルダ構成

### 入力フォルダ構成

```
dataset/
   13097882.svg
   13097882.csv
   06098136.svg
   06098136.csv
   ...
```

### CSVファイル形式（Shift-JIS）

```csv
id,text,font
path38,J,Mincho
path34,U,Mincho
path30,I,Mincho
...
```

- `id`: SVG内のpath要素のidと一致
- `text`: 実際の文字（例：「山」「川」「J」「U」など）
- `font`: フォント名（Mincho / Gothic など）

### SVGファイル形式

- Illustratorで文字をアウトライン化 → InkscapeでPDF→SVG変換したもの
- 1文字ごとに`<path id="pathXX">`のような要素になっている
- 各path要素の`d`属性からbounding boxを計算

### 出力フォルダ構成

```
output/
   13097882.json
   06098136.json
   ...
```

## 🎮 使用方法

### 基本的な使用方法

```bash
python batch_process.py
```

デフォルトでは、`./Study/svg_cvs` ディレクトリ内のSVG/CSVペアを処理し、`./output` ディレクトリにJSONファイルを生成します。

### カスタムディレクトリの指定

```bash
python batch_process.py <データセットディレクトリ> <出力ディレクトリ>
```

例：
```bash
python batch_process.py ./dataset ./output
```

## 📊 出力JSON形式

```json
{
  "file": "13097882",
  "font": "Mincho",
  "sequence": [
    {"id": "path38", "text": "J"},
    {"id": "path34", "text": "U"},
    {"id": "path30", "text": "I"},
    ...
  ],
  "pairs": [
    {
      "left_id": "path38",
      "left": "J",
      "right_id": "path34",
      "right": "U",
      "gap_actual": 32.1
    },
    ...
  ],
  "bbox": {
    "path38": {
      "min_x": 123.4,
      "max_x": 148.0,
      "min_y": 200.0,
      "max_y": 245.0,
      "width": 24.6,
      "height": 45.0
    },
    ...
  }
}
```

### フィールド説明

- `file`: ファイルID（拡張子なし）
- `font`: フォント名（CSVから取得、最初のレコードの値を採用）
- `sequence`: 文字列順のシーケンス情報
- `pairs`: 隣接文字ペアの情報とgap_actual（実際の文字間隔）
- `bbox`: 各文字（id）のbounding box情報

## 🔍 処理の流れ

1. **SVG解析** (`svg_parser.py`)
   - SVGファイルを読み込み
   - 各path要素の`d`属性を解析
   - transform属性を考慮してbounding boxを計算

2. **CSV読み込み** (`csv_loader.py`)
   - Shift-JISでエンコードされたCSVを読み込み
   - id, text, fontの情報を取得

3. **データ結合** (`gap_extractor.py`)
   - SVGとCSVのデータをidで結合
   - CSVの行順を文字列順として保持

4. **gap_actual計算** (`gap_extractor.py`)
   - 隣接文字ペアごとに `gap_actual = next.min_x - current.max_x` を計算

5. **JSON出力** (`export_json.py`)
   - 学習用JSON形式でファイルに保存

## ⚠️ 注意事項

- CSVファイルはShift-JIS（cp932）でエンコードされている必要があります
- SVGファイル内のpath要素のidとCSVのidが一致している必要があります
- CSVの行順が文字列の並び順として扱われます
- transform属性の解析は簡易実装のため、複雑なtransformには対応していない場合があります

## 🐛 トラブルシューティング

### CSVファイルが読み込めない

- CSVファイルがShift-JISでエンコードされているか確認してください
- ファイルパスが正しいか確認してください

### SVGファイルが解析できない

- SVGファイルが有効なXML形式か確認してください
- path要素にid属性が設定されているか確認してください

### gap_actualが負の値になる

- 文字が重なっている場合、負の値になることがあります
- これは正常な動作です

## 📝 ライセンス

このプロジェクトは内部使用を想定しています。

## 👥 開発者向け情報

### モジュールの詳細

- **svg_parser.py**: SVG pathの`d`属性を解析して座標点を抽出し、bounding boxを計算
- **csv_loader.py**: Shift-JISエンコーディングに対応したCSV読み込み
- **gap_extractor.py**: データ結合と文字間隔計算のロジック
- **export_json.py**: JSON形式での出力処理

### 改善の余地

- SVG path解析の精度向上（`svgpathtools`ライブラリの利用を検討）
- transform属性の完全な対応（rotate, skewなど）
- エラーハンドリングの強化

