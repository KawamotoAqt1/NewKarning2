"""
任意のpathIDのbboxを確認するテストコード
Inkscapeの選択枠と比較するためのデバッグツール
"""

import xml.etree.ElementTree as ET
from svg_parser import (
    parse_svg,
    find_path_by_id,
    get_path_bbox,
    get_group_bbox,
    compute_cumulative_transform,
    parse_path_d,
    apply_transform_to_points,
    calculate_bbox_from_points
)
from transform_utils import apply_matrix_to_point
from typing import Optional


def debug_print_bbox(svg_path: str, target_id: str):
    """
    指定されたpathIDのbboxを計算し、詳細情報を表示
    
    Inkscapeで選択したときの枠と比較できるように、以下の情報を表示：
    - min_x, max_x, min_y, max_y
    - width, height
    - 中心座標
    - transform適用前後の座標例
    
    Args:
        svg_path: SVGファイルのパス
        target_id: 対象のpathID（例: "path5", "path7"）
    """
    print(f"\n{'='*80}")
    print(f"bboxデバッグ: {svg_path}")
    print(f"対象ID: {target_id}")
    print(f"{'='*80}")
    
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # まず、g要素として検索
        target_elem = None
        for elem in root.iter():
            if elem.tag.endswith('g') and elem.get('id') == target_id:
                target_elem = elem
                print(f"\n要素タイプ: <g> (グループ)")
                break
        
        # g要素が見つからない場合、path要素として検索
        if target_elem is None:
            target_elem = find_path_by_id(root, target_id)
            if target_elem:
                print(f"\n要素タイプ: <path>")
        
        if target_elem is None:
            print(f"\n❌ エラー: ID '{target_id}' が見つかりません")
            return
        
        # transform情報を表示
        print(f"\n--- Transform情報 ---")
        cumulative_matrix = compute_cumulative_transform(target_elem, root)
        print(f"累積transform行列: {cumulative_matrix}")
        
        # 要素自身のtransform
        elem_transform_str = target_elem.get('transform', '')
        if elem_transform_str:
            print(f"要素自身のtransform: {elem_transform_str}")
        else:
            print(f"要素自身のtransform: (なし)")
        
        # 親要素の階層を表示
        print(f"\n--- 親要素の階層 ---")
        ancestors = []
        current = target_elem
        while current is not None and current != root:
            ancestors.insert(0, current)
            found_parent = None
            for parent in root.iter():
                for child in parent:
                    if child == current:
                        found_parent = parent
                        break
                if found_parent:
                    break
            current = found_parent
        
        for i, ancestor in enumerate(ancestors):
            tag = ancestor.tag.split('}')[-1] if '}' in ancestor.tag else ancestor.tag
            elem_id = ancestor.get('id', '')
            transform_attr = ancestor.get('transform', '')
            print(f"  {'  ' * i}{tag} id='{elem_id}' transform='{transform_attr[:60] if len(transform_attr) > 60 else transform_attr}'")
        
        # bboxを計算
        print(f"\n--- Bounding Box計算 ---")
        
        if target_elem.tag.endswith('g'):
            bbox = get_group_bbox(target_elem, root)
        else:
            bbox = get_path_bbox(target_elem, root)
        
        if bbox:
            print(f"\n✅ 計算されたbbox:")
            print(f"  min_x: {bbox['min_x']:.6f}")
            print(f"  max_x: {bbox['max_x']:.6f}")
            print(f"  min_y: {bbox['min_y']:.6f}")
            print(f"  max_y: {bbox['max_y']:.6f}")
            print(f"  width:  {bbox['width']:.6f}")
            print(f"  height: {bbox['height']:.6f}")
            print(f"  中心X:  {(bbox['min_x'] + bbox['max_x']) / 2:.6f}")
            print(f"  中心Y:  {(bbox['min_y'] + bbox['max_y']) / 2:.6f}")
            
            print(f"\n--- Inkscape比較用フォーマット ---")
            print(f"  x:      {bbox['min_x']:.6f}")
            print(f"  y:      {bbox['min_y']:.6f}")
            print(f"  width:  {bbox['width']:.6f}")
            print(f"  height: {bbox['height']:.6f}")
            
            # 座標点のサンプルを表示
            if target_elem.tag.endswith('path'):
                path_d = target_elem.get('d', '')
                if path_d:
                    points = parse_path_d(path_d)
                    if points:
                        print(f"\n--- 座標点のサンプル ---")
                        print(f"  元の座標点（最初の3点）: {points[:3]}")
                        print(f"  元の座標点（最後の3点）: {points[-3:]}")
                        
                        transformed_points = apply_transform_to_points(points, cumulative_matrix)
                        print(f"  変換後の座標点（最初の3点）: {transformed_points[:3]}")
                        print(f"  変換後の座標点（最後の3点）: {transformed_points[-3:]}")
        else:
            print(f"\n❌ エラー: bboxを計算できませんでした")
        
        # parse_svg関数で取得した結果と比較
        print(f"\n--- parse_svg関数の結果との比較 ---")
        svg_results = parse_svg(svg_path)
        for result in svg_results:
            if result['id'] == target_id:
                print(f"  parse_svgで取得したbbox:")
                print(f"    min_x: {result['min_x']:.6f}")
                print(f"    max_x: {result['max_x']:.6f}")
                print(f"    min_y: {result['min_y']:.6f}")
                print(f"    max_y: {result['max_y']:.6f}")
                print(f"    width:  {result['width']:.6f}")
                print(f"    height: {result['height']:.6f}")
                
                if bbox:
                    # 比較
                    diff_x = abs(bbox['min_x'] - result['min_x'])
                    diff_y = abs(bbox['min_y'] - result['min_y'])
                    diff_w = abs(bbox['width'] - result['width'])
                    diff_h = abs(bbox['height'] - result['height'])
                    
                    if diff_x < 0.01 and diff_y < 0.01 and diff_w < 0.01 and diff_h < 0.01:
                        print(f"  ✅ 一致しています（誤差 < 0.01）")
                    else:
                        print(f"  ⚠️  差異があります:")
                        print(f"    min_xの差: {diff_x:.6f}")
                        print(f"    min_yの差: {diff_y:.6f}")
                        print(f"    widthの差:  {diff_w:.6f}")
                        print(f"    heightの差: {diff_h:.6f}")
                break
        else:
            print(f"  ⚠️  parse_svg関数の結果に '{target_id}' が見つかりませんでした")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()


def main():
    """メイン関数"""
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法: python debug_bbox.py <svg_path> <target_id>")
        print("例: python debug_bbox.py Study/svg_cvs/06099095.svg path5")
        print("例: python debug_bbox.py Study/svg_cvs/06098954.svg path7")
        return
    
    svg_path = sys.argv[1]
    target_id = sys.argv[2]
    
    debug_print_bbox(svg_path, target_id)


if __name__ == "__main__":
    # デフォルトのテストケース
    if len(__import__('sys').argv) == 1:
        print("デフォルトのテストケースを実行します...")
        print("\n" + "="*80)
        print("テスト1: 中谷（06099095.svg）の「中」（path5）")
        print("="*80)
        debug_print_bbox("Study/svg_cvs/06099095.svg", "path5")
        
        print("\n" + "="*80)
        print("テスト2: 中谷（06099095.svg）の「谷」（path7）")
        print("="*80)
        debug_print_bbox("Study/svg_cvs/06099095.svg", "path7")
        
        print("\n" + "="*80)
        print("テスト3: 宮崎（06098954.svg）の「宮」（path5）")
        print("="*80)
        debug_print_bbox("Study/svg_cvs/06098954.svg", "path5")
        
        print("\n" + "="*80)
        print("テスト4: 宮崎（06098954.svg）の「崎」（path7）")
        print("="*80)
        debug_print_bbox("Study/svg_cvs/06098954.svg", "path7")
    else:
        main()

