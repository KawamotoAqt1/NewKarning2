"""
transform修正の検証テスト
中谷（06099095.svg）と宮崎（06098954.svg）のgap_actualを検証
"""

import sys
from pathlib import Path
from svg_parser import parse_svg
from csv_loader import load_csv
from gap_extractor import merge_svg_csv, calculate_gap_actual


def test_svg_transform(svg_path: str, csv_path: str, name: str):
    """
    1つのSVG/CSVペアをテスト
    
    Args:
        svg_path: SVGファイルのパス
        csv_path: CSVファイルのパス
        name: テスト名（表示用）
    """
    print(f"\n{'='*60}")
    print(f"テスト: {name}")
    print(f"SVG: {svg_path}")
    print(f"CSV: {csv_path}")
    print(f"{'='*60}")
    
    # SVGを解析
    svg_data = parse_svg(svg_path)
    if not svg_data:
        print(f"  ❌ エラー: SVGの解析に失敗しました")
        return
    
    print(f"\n  SVG解析結果: {len(svg_data)}個の要素が見つかりました")
    for item in svg_data:
        print(f"    {item['id']}: bbox=({item['min_x']:.2f}, {item['min_y']:.2f}) - ({item['max_x']:.2f}, {item['max_y']:.2f}), "
              f"size=({item['width']:.2f}, {item['height']:.2f})")
    
    # CSVを読み込み
    csv_data = load_csv(csv_path)
    if not csv_data:
        print(f"  ❌ エラー: CSVの読み込みに失敗しました")
        return
    
    print(f"\n  CSV読み込み結果: {len(csv_data)}個のレコード")
    for item in csv_data:
        print(f"    {item['id']}: text='{item['text']}', font='{item.get('font', 'N/A')}'")
    
    # データを結合
    merged_data = merge_svg_csv(svg_data, csv_data)
    if not merged_data:
        print(f"  ❌ エラー: データの結合に失敗しました")
        return
    
    print(f"\n  結合結果: {len(merged_data)}個のレコード")
    
    # gap_actualを計算
    pairs = calculate_gap_actual(merged_data)
    
    print(f"\n  gap_actual計算結果: {len(pairs)}個のペア")
    print(f"  {'-'*60}")
    print(f"  {'左':<10} {'右':<10} {'gap_actual':>12} {'状態':<10}")
    print(f"  {'-'*60}")
    
    has_abnormal = False
    for pair in pairs:
        gap = pair['gap_actual']
        status = "✅ 正常" if -50 <= gap <= 100 else "⚠️ 異常"
        if gap < -50 or gap > 100:
            has_abnormal = True
        
        print(f"  {pair['left']:<10} {pair['right']:<10} {gap:>12.2f} {status:<10}")
    
    print(f"  {'-'*60}")
    
    if has_abnormal:
        print(f"  ⚠️  異常なgap_actualが検出されました（-50px未満または100px超過）")
    else:
        print(f"  ✅ すべてのgap_actualが正常範囲内です（-50px ～ 100px）")


def main():
    """メイン関数"""
    base_dir = Path("Study/svg_cvs")
    
    # テストケース
    test_cases = [
        ("06099095.svg", "06099095.csv", "中谷"),
        ("06098954.svg", "06098954.csv", "宮崎"),
    ]
    
    print("="*60)
    print("transform修正の検証テスト")
    print("="*60)
    
    for svg_file, csv_file, name in test_cases:
        svg_path = base_dir / svg_file
        csv_path = base_dir / csv_file
        
        if not svg_path.exists():
            print(f"\n❌ エラー: SVGファイルが見つかりません: {svg_path}")
            continue
        
        if not csv_path.exists():
            print(f"\n❌ エラー: CSVファイルが見つかりません: {csv_path}")
            continue
        
        test_svg_transform(str(svg_path), str(csv_path), name)
    
    print(f"\n{'='*60}")
    print("テスト完了")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

