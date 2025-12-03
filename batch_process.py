"""
一括処理スクリプト
フォルダ内の全SVG/CSVペアを処理して、学習用JSONを生成する

【運用方針】
- 学習データは「ユーザーが目視で確認済みのSVG+CSVセットだけ」
- dataset_train/svg/ と dataset_train/csv/ を処理して output_json/train/ に出力
- dataset_all は「元データの倉庫」として扱い、自動では学習に含めない
- 学習用パイプラインは dataset_train のみを入力とする
"""

import os
import sys
from pathlib import Path
from typing import List
from svg_parser import parse_svg, parse_svg_groups
from csv_loader import load_csv
from gap_extractor import (
    merge_svg_csv,
    calculate_gap_actual,
    extract_sequence,
    extract_bbox_dict,
    get_font,
    split_by_names
)
from export_json import export_to_json


# デフォルトのディレクトリ設定
# 学習用パイプラインは dataset_train を前提とする
DEFAULT_DATASET_DIR = "./dataset_train"  # 学習用データセット（目視確認済み）
DEFAULT_OUTPUT_DIR = "./output_json/train"  # 学習用JSON出力先


def find_svg_csv_pairs(dataset_dir: str) -> List[tuple]:
    """
    データセットディレクトリ内のSVG/CSVペアを検索
    
    dataset_dir直下にSVGとCSVが混在している構造を想定
    
    Args:
        dataset_dir: データセットディレクトリのパス
    
    Returns:
        [(svg_path, csv_path, file_id), ...] のリスト
    """
    pairs = []
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        print(f"Error: Dataset directory '{dataset_dir}' does not exist")
        return pairs
    
    # dataset_dir直下にSVGとCSVが混在している構造
    svg_files = list(dataset_path.glob("*.svg"))
    
    for svg_file in svg_files:
        file_id = svg_file.stem
        csv_file = dataset_path / f"{file_id}.csv"
        
        if csv_file.exists():
            pairs.append((str(svg_file), str(csv_file), file_id))
        else:
            print(f"Warning: CSV file not found for {svg_file.name}")
    
    return pairs


def process_single_pair(svg_path: str, csv_path: str, file_id: str, output_dir: str) -> bool:
    """
    1つのSVG/CSVペアを処理してJSONを生成
    
    Args:
        svg_path: SVGファイルのパス
        csv_path: CSVファイルのパス
        file_id: ファイルID
        output_dir: 出力ディレクトリ
    
    Returns:
        成功した場合True、失敗した場合False
    """
    try:
        print(f"Processing: {file_id}")
        
        # Step 1: SVGを解析（bounding box情報を取得）
        svg_data = parse_svg(svg_path)
        if not svg_data:
            print(f"  Error: Failed to parse SVG {svg_path}")
            return False
        
        # Step 1.5: SVGのグループ構造を取得（名前ごとのグループ）
        svg_groups = parse_svg_groups(svg_path)
        
        # Step 2: CSVを読み込み
        csv_data = load_csv(csv_path)
        if not csv_data:
            print(f"  Error: Failed to load CSV {csv_path}")
            return False
        
        # Step 3: 結合・gap_actual計算
        merged_data = merge_svg_csv(svg_data, csv_data)
        if not merged_data:
            print(f"  Error: Failed to merge SVG and CSV data")
            return False
        
        # 名前ごとに分割（SVGグループ構造を使用）
        name_groups = split_by_names(merged_data, svg_groups)
        
        if not name_groups:
            print(f"  Warning: No names found in {file_id}")
            return False
        
        # 各名前ごとにJSONを出力
        success_count = 0
        for name_index, name_data in enumerate(name_groups):
            # CSVのname_textを優先的に使用
            name_text = ""
            if name_data and name_data[0].get("name_text"):
                name_text = name_data[0].get("name_text", "").strip()
            
            # name_textが取得できない場合、各文字のtextを結合（後方互換性のため）
            if not name_text:
                for item in name_data:
                    text = item.get("text", "").strip()
                    if text:
                        name_text += text
            
            # 名前のテキストが取得できない場合、インデックスを使用
            if not name_text:
                name_text = f"name{name_index + 1}"
            
            # ファイル名に使用できない文字を置換
            safe_name = "".join(c if c.isalnum() or ord(c) > 127 else '_' for c in name_text)
            # 長すぎる場合は切り詰め
            if len(safe_name) > 30:
                safe_name = safe_name[:30]
            
            # gap_actualを計算
            pairs = calculate_gap_actual(name_data)
            
            # シーケンス情報を抽出
            sequence = extract_sequence(name_data)
            
            # bounding box情報を抽出（全データから該当するidのみ）
            all_bbox = extract_bbox_dict(merged_data)
            bbox = {item["id"]: all_bbox[item["id"]] for item in name_data if item["id"] in all_bbox}
            
            # フォント名を取得
            font = get_font(name_data)
            
            # ファイル名を生成（複数の名前がある場合はインデックスも含める）
            if len(name_groups) > 1:
                output_filename = f"{file_id}_{name_index + 1:02d}_{safe_name}.json"
            else:
                # 名前が1つでも名前をファイル名に含める
                output_filename = f"{file_id}_{safe_name}.json"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Step 4: JSONを出力
            success = export_to_json(
                output_path=output_path,
                file_id=file_id,
                font=font,
                sequence=sequence,
                pairs=pairs,
                bbox=bbox
            )
            
            if success:
                print(f"  Success: Generated {output_path} (name: {name_text})")
                success_count += 1
            else:
                print(f"  Error: Failed to export JSON for name: {name_text}")
        
        return success_count == len(name_groups)
    
    except Exception as e:
        print(f"  Error processing {file_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main(dataset_dir: str = None, output_dir: str = None):
    """
    メイン処理
    
    Args:
        dataset_dir: データセットディレクトリ（デフォルト: DEFAULT_DATASET_DIR = "./dataset_train"）
        output_dir: 出力ディレクトリ（デフォルト: DEFAULT_OUTPUT_DIR = "./output_json/train"）
    
    注意:
        - 学習用パイプラインは dataset_train を前提とする
        - dataset_all を処理する場合は明示的に引数で指定すること
    """
    # デフォルト値の設定
    if dataset_dir is None:
        dataset_dir = DEFAULT_DATASET_DIR
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    print("=" * 60)
    print("SVG+CSV → JSON 変換パイプライン")
    print("=" * 60)
    print(f"Dataset directory: {dataset_dir} (SVGとCSVが混在)")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    # SVG/CSVペアを検索
    pairs = find_svg_csv_pairs(dataset_dir)
    
    if not pairs:
        print("No SVG/CSV pairs found")
        return
    
    print(f"Found {len(pairs)} SVG/CSV pairs")
    print("-" * 60)
    
    # 各ペアを処理
    success_count = 0
    error_count = 0
    
    for svg_path, csv_path, file_id in pairs:
        if process_single_pair(svg_path, csv_path, file_id, output_dir):
            success_count += 1
        else:
            error_count += 1
    
    # 結果を表示
    print("-" * 60)
    print(f"Processing completed:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(pairs)}")


if __name__ == "__main__":
    # コマンドライン引数からディレクトリを取得（オプション）
    dataset_dir = None
    output_dir = None
    
    if len(sys.argv) > 1:
        dataset_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    main(dataset_dir, output_dir)

