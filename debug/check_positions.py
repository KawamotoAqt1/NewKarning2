"""
path6とpath8の実際の位置関係を調べる
"""
import xml.etree.ElementTree as ET
from svg_parser import parse_path_d, apply_transform_to_points, calculate_bbox_from_points

# SVGファイルを読み込む
tree = ET.parse('Study/svg_cvs/12193287.svg')
root = tree.getroot()

# path6とpath8を探す
path6 = None
path8 = None

for elem in root.iter():
    if elem.tag.endswith('path'):
        path_id = elem.get('id')
        if path_id == 'path6':
            path6 = elem
        elif path_id == 'path8':
            path8 = elem

print("=== path6（あ）の情報 ===")
if path6 is not None:
    path_d = path6.get('d', '')
    transform_str = path6.get('transform', '')
    print(f"transform: {transform_str}")
    
    # 座標点を抽出
    points = parse_path_d(path_d)
    if points:
        # 最初と最後の点を表示
        print(f"元の座標点（最初の5点）: {points[:5]}")
        print(f"元の座標点（最後の5点）: {points[-5:]}")
        
        # transformを解析
        from svg_parser import parse_transform
        transform = parse_transform(transform_str)
        print(f"解析されたtransform: {transform}")
        
        # transformを適用
        transformed_points = apply_transform_to_points(points, transform)
        if transformed_points:
            print(f"変換後の座標点（最初の5点）: {transformed_points[:5]}")
            print(f"変換後の座標点（最後の5点）: {transformed_points[-5:]}")
            
            # bboxを計算
            bbox = calculate_bbox_from_points(transformed_points)
            print(f"bbox: min_x={bbox['min_x']:.2f}, max_x={bbox['max_x']:.2f}, min_y={bbox['min_y']:.2f}, max_y={bbox['max_y']:.2f}")
            print(f"center_y = {(bbox['min_y'] + bbox['max_y']) / 2:.2f}")

print("\n=== path8（り）の情報 ===")
if path8 is not None:
    path_d = path8.get('d', '')
    transform_str = path8.get('transform', '')
    print(f"transform: {transform_str}")
    
    # 座標点を抽出
    points = parse_path_d(path_d)
    if points:
        # 最初と最後の点を表示
        print(f"元の座標点（最初の5点）: {points[:5]}")
        print(f"元の座標点（最後の5点）: {points[-5:]}")
        
        # transformを解析
        from svg_parser import parse_transform
        transform = parse_transform(transform_str)
        print(f"解析されたtransform: {transform}")
        
        # transformを適用
        transformed_points = apply_transform_to_points(points, transform)
        if transformed_points:
            print(f"変換後の座標点（最初の5点）: {transformed_points[:5]}")
            print(f"変換後の座標点（最後の5点）: {transformed_points[-5:]}")
            
            # bboxを計算
            bbox = calculate_bbox_from_points(transformed_points)
            print(f"bbox: min_x={bbox['min_x']:.2f}, max_x={bbox['max_x']:.2f}, min_y={bbox['min_y']:.2f}, max_y={bbox['max_y']:.2f}")
            print(f"center_y = {(bbox['min_y'] + bbox['max_y']) / 2:.2f}")

print("\n=== 位置関係の比較 ===")
from svg_parser import parse_svg
data = parse_svg('Study/svg_cvs/12193287.svg')
path6_data = [d for d in data if d['id'] == 'path6'][0]
path8_data = [d for d in data if d['id'] == 'path8'][0]

print(f"path6（あ）: min_y={path6_data['min_y']:.2f}, max_y={path6_data['max_y']:.2f}, center_y={(path6_data['min_y'] + path6_data['max_y'])/2:.2f}")
print(f"path8（り）: min_y={path8_data['min_y']:.2f}, max_y={path8_data['max_y']:.2f}, center_y={(path8_data['min_y'] + path8_data['max_y'])/2:.2f}")

print(f"\nY座標の比較:")
print(f"  path6のmin_y ({path6_data['min_y']:.2f}) vs path8のmin_y ({path8_data['min_y']:.2f})")
print(f"  path6のcenter_y ({(path6_data['min_y'] + path6_data['max_y'])/2:.2f}) vs path8のcenter_y ({(path8_data['min_y'] + path8_data['max_y'])/2:.2f})")
print(f"  path6のmax_y ({path6_data['max_y']:.2f}) vs path8のmax_y ({path8_data['max_y']:.2f})")

# SVGのviewBoxを確認
viewbox = root.get('viewBox', '')
print(f"\nSVG viewBox: {viewbox}")
if viewbox:
    parts = viewbox.split()
    if len(parts) >= 4:
        svg_height = float(parts[3])
        print(f"SVG height: {svg_height}")
        print(f"\nYスケールが負の場合、実際の表示では:")
        print(f"  Y座標が大きいほど上に表示される")
        print(f"  Y座標が小さいほど下に表示される")
        print(f"  実際の表示位置（Y座標が大きい順）:")
        if path6_data['max_y'] > path8_data['max_y']:
            print(f"    1. path6（あ）: max_y={path6_data['max_y']:.2f} (上)")
            print(f"    2. path8（り）: max_y={path8_data['max_y']:.2f} (下)")
        else:
            print(f"    1. path8（り）: max_y={path8_data['max_y']:.2f} (上)")
            print(f"    2. path6（あ）: max_y={path6_data['max_y']:.2f} (下)")

