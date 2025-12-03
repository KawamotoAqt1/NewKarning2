"""path5とpath7の座標点とtransformを詳細に確認"""
import xml.etree.ElementTree as ET
from svg_parser import parse_path_d, compute_cumulative_transform, apply_transform_to_points, calculate_bbox_from_points
from transform_utils import parse_transform

svg_path = "Study/svg_cvs/06099095.svg"
tree = ET.parse(svg_path)
root = tree.getroot()

# path5を取得
path5 = None
path7 = None
for elem in root.iter():
    if elem.tag.endswith('path'):
        elem_id = elem.get('id')
        if elem_id == 'path5':
            path5 = elem
        elif elem_id == 'path7':
            path7 = elem

print("="*80)
print("path5（中）の詳細")
print("="*80)

if path5:
    path_d = path5.get('d', '')
    transform_str = path5.get('transform', '')
    
    print(f"\npath d属性: {path_d[:100]}...")
    print(f"transform: {transform_str}")
    
    # 座標点を抽出
    points = parse_path_d(path_d)
    print(f"\n抽出された座標点数: {len(points)}")
    print(f"最初の10点: {points[:10]}")
    print(f"最後の10点: {points[-10:]}")
    
    # transformを解析
    transform_matrix = parse_transform(transform_str)
    print(f"\ntransform行列: {transform_matrix}")
    
    # 累積transformを計算
    cumulative_matrix = compute_cumulative_transform(path5, root)
    print(f"累積transform行列: {cumulative_matrix}")
    
    # transformを適用
    transformed_points = apply_transform_to_points(points, cumulative_matrix)
    print(f"\n変換後の最初の10点: {transformed_points[:10]}")
    print(f"変換後の最後の10点: {transformed_points[-10:]}")
    
    # bboxを計算
    bbox = calculate_bbox_from_points(transformed_points)
    if bbox:
        print(f"\n計算されたbbox:")
        print(f"  min_x: {bbox['min_x']:.6f}")
        print(f"  max_x: {bbox['max_x']:.6f}")
        print(f"  min_y: {bbox['min_y']:.6f}")
        print(f"  max_y: {bbox['max_y']:.6f}")
        print(f"  width:  {bbox['width']:.6f}")
        print(f"  height: {bbox['height']:.6f}")

print("\n" + "="*80)
print("path7（谷）の詳細")
print("="*80)

if path7:
    path_d = path7.get('d', '')
    transform_str = path7.get('transform', '')
    
    print(f"\npath d属性: {path_d[:100]}...")
    print(f"transform: {transform_str}")
    
    # 座標点を抽出
    points = parse_path_d(path_d)
    print(f"\n抽出された座標点数: {len(points)}")
    print(f"最初の10点: {points[:10]}")
    print(f"最後の10点: {points[-10:]}")
    
    # transformを解析
    transform_matrix = parse_transform(transform_str)
    print(f"\ntransform行列: {transform_matrix}")
    
    # 累積transformを計算
    cumulative_matrix = compute_cumulative_transform(path7, root)
    print(f"累積transform行列: {cumulative_matrix}")
    
    # transformを適用
    transformed_points = apply_transform_to_points(points, cumulative_matrix)
    print(f"\n変換後の最初の10点: {transformed_points[:10]}")
    print(f"変換後の最後の10点: {transformed_points[-10:]}")
    
    # bboxを計算
    bbox = calculate_bbox_from_points(transformed_points)
    if bbox:
        print(f"\n計算されたbbox:")
        print(f"  min_x: {bbox['min_x']:.6f}")
        print(f"  max_x: {bbox['max_x']:.6f}")
        print(f"  min_y: {bbox['min_y']:.6f}")
        print(f"  max_y: {bbox['max_y']:.6f}")
        print(f"  width:  {bbox['width']:.6f}")
        print(f"  height: {bbox['height']:.6f}")

