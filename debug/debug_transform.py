"""
transform適用の詳細デバッグ
中谷と宮崎の実際の座標とtransformを確認
"""

import xml.etree.ElementTree as ET
from svg_parser import parse_path_d, parse_transform, combine_transform, apply_matrix_to_point, identity_matrix, collect_parent_transforms


def debug_path_transform(svg_path: str, path_ids: list):
    """
    指定されたpath要素のtransform適用をデバッグ
    
    Args:
        svg_path: SVGファイルのパス
        path_ids: デバッグするpath idのリスト
    """
    print(f"\n{'='*80}")
    print(f"デバッグ: {svg_path}")
    print(f"{'='*80}")
    
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # 親要素のtransformを収集
    parent_transforms = collect_parent_transforms(root)
    
    for path_id in path_ids:
        print(f"\n--- {path_id} ---")
        
        # path要素を検索
        path_elem = None
        for elem in root.iter():
            if elem.tag.endswith('path') and elem.get('id') == path_id:
                path_elem = elem
                break
        
        if path_elem is None:
            print(f"  ❌ path要素が見つかりません")
            continue
        
        # d属性を取得
        path_d = path_elem.get('d', '')
        print(f"  d属性: {path_d[:100]}..." if len(path_d) > 100 else f"  d属性: {path_d}")
        
        # 座標点を抽出
        points = parse_path_d(path_d)
        if points:
            print(f"  元の座標点: 最初={points[0]}, 最後={points[-1]}, 合計{len(points)}点")
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            print(f"  元のbbox: x=[{min(xs):.2f}, {max(xs):.2f}], y=[{min(ys):.2f}, {max(ys):.2f}]")
        
        # 親要素のtransformを取得
        parent_matrix = parent_transforms.get(path_elem, identity_matrix())
        print(f"  親要素のtransform行列: {parent_matrix}")
        
        # path要素自身のtransformを取得
        path_transform_str = path_elem.get('transform', '')
        print(f"  path要素のtransform属性: {path_transform_str}")
        
        if path_transform_str:
            path_matrix = parse_transform(path_transform_str)
            print(f"  path要素のtransform行列: {path_matrix}")
            
            # 合成
            final_matrix = combine_transform(parent_matrix, path_matrix)
            print(f"  合成後のtransform行列: {final_matrix}")
        else:
            final_matrix = parent_matrix
        
        # transformを適用
        if points:
            transformed_points = []
            for x, y in points:
                tx, ty = apply_matrix_to_point(x, y, final_matrix)
                transformed_points.append((tx, ty))
            
            xs = [p[0] for p in transformed_points]
            ys = [p[1] for p in transformed_points]
            print(f"  変換後のbbox: x=[{min(xs):.2f}, {max(xs):.2f}], y=[{min(ys):.2f}, {max(ys):.2f}]")
            print(f"  変換後の座標点: 最初={transformed_points[0]}, 最後={transformed_points[-1]}")
        
        # 親要素の階層を確認
        print(f"  親要素の階層:")
        current = path_elem
        level = 0
        while current is not None:
            tag = current.tag.split('}')[-1] if '}' in current.tag else current.tag
            elem_id = current.get('id', '')
            transform_attr = current.get('transform', '')
            print(f"    {'  ' * level}{tag} id='{elem_id}' transform='{transform_attr[:50] if len(transform_attr) > 50 else transform_attr}'")
            level += 1
            # ElementTreeにはgetparent()がないので、手動で親を探す
            found_parent = None
            for parent in root.iter():
                for child in parent:
                    if child == current:
                        found_parent = parent
                        break
                if found_parent:
                    break
            current = found_parent
            if level > 10:  # 無限ループ防止
                break


def main():
    """メイン関数"""
    base_dir = "Study/svg_cvs"
    
    # 中谷のデバッグ
    print("\n" + "="*80)
    print("中谷（06099095.svg）のデバッグ")
    print("="*80)
    debug_path_transform(f"{base_dir}/06099095.svg", ["path5", "path7"])
    
    # 宮崎のデバッグ
    print("\n" + "="*80)
    print("宮崎（06098954.svg）のデバッグ")
    print("="*80)
    debug_path_transform(f"{base_dir}/06098954.svg", ["path5", "path7"])


if __name__ == "__main__":
    main()

