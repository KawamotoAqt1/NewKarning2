"""
CSVファイルを新しいフォーマット（name_text, name_order列を追加）に更新するスクリプト
"""
import csv
import os
from pathlib import Path
from typing import List, Dict
from csv_loader import load_csv
from svg_parser import parse_svg_groups
from gap_extractor import merge_svg_csv, split_by_names, is_vertical_text, sort_by_x_in_row, sort_by_y_in_row

def update_csv_to_new_format(csv_path: str, svg_path: str, output_path: str = None) -> bool:
    """
    CSVファイルを新しいフォーマットに更新
    
    Args:
        csv_path: 元のCSVファイルのパス
        svg_path: 対応するSVGファイルのパス
        output_path: 出力先のCSVファイルのパス（Noneの場合は元のファイルを上書き）
    
    Returns:
        成功した場合True
    """
    try:
        # CSVを読み込む
        csv_data = load_csv(csv_path)
        if not csv_data:
            print(f"Warning: CSV file is empty: {csv_path}")
            return False
        
        # SVGからグループ情報を取得
        svg_groups = parse_svg_groups(svg_path)
        
        # SVGデータを読み込む
        from svg_parser import parse_svg
        svg_data = parse_svg(svg_path)
        
        # データを結合
        merged_data = merge_svg_csv(svg_data, csv_data)
        
        # 名前ごとに分割
        if svg_groups:
            name_groups = split_by_names(merged_data, svg_groups)
        else:
            name_groups = split_by_names(merged_data, None)
        
        # 各名前グループからname_textを生成し、name_orderを設定
        updated_rows = []
        for name_group in name_groups:
            # name_textを生成（各文字のtextを結合）
            name_text = ''.join([item.get('text', '') for item in name_group])
            
            # 各文字にname_textとname_orderを追加
            for order, item in enumerate(name_group, start=1):
                # 元のCSVデータから対応する行を探す
                csv_row = next((row for row in csv_data if row['id'] == item['id']), None)
                if csv_row:
                    updated_rows.append({
                        'id': csv_row['id'],
                        'text': csv_row['text'],
                        'font': csv_row['font'],
                        'name_text': name_text,
                        'name_order': str(order)
                    })
        
        # 新しいCSVファイルを書き込む
        output_file = output_path if output_path else csv_path
        
        # Shift-JISでエンコードして書き込む
        with open(output_file, 'w', encoding='cp932', newline='') as f:
            fieldnames = ['id', 'text', 'font', 'name_text', 'name_order']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        print(f"Updated: {csv_path} -> {output_file}")
        return True
        
    except Exception as e:
        print(f"Error updating {csv_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """すべてのCSVファイルを更新"""
    dataset_dir = Path("Study/svg_cvs")
    
    # すべてのCSVファイルを取得
    csv_files = list(dataset_dir.glob("*.csv"))
    
    print(f"Found {len(csv_files)} CSV files")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for csv_file in csv_files:
        # 対応するSVGファイルを探す
        svg_file = dataset_dir / f"{csv_file.stem}.svg"
        
        if not svg_file.exists():
            print(f"Warning: SVG file not found for {csv_file.name}")
            error_count += 1
            continue
        
        if update_csv_to_new_format(str(csv_file), str(svg_file)):
            success_count += 1
        else:
            error_count += 1
    
    print("=" * 60)
    print(f"Processing completed:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(csv_files)}")

if __name__ == "__main__":
    main()

