"""svgpathtoolsを使用して正確なbboxを計算"""
try:
    from svgpathtools import parse_path, Path
    SVG_PATH_TOOLS_AVAILABLE = True
except ImportError:
    SVG_PATH_TOOLS_AVAILABLE = False
    print("svgpathtoolsがインストールされていません。pip install svgpathtools でインストールしてください。")

import xml.etree.ElementTree as ET
from transform_utils import parse_transform, combine_transform, apply_matrix_to_point, identity_matrix
from svg_parser import compute_cumulative_transform

if SVG_PATH_TOOLS_AVAILABLE:
    svg_path = "Study/svg_cvs/06099095.svg"
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # path5を取得
    path5 = None
    for elem in root.iter():
        if elem.tag.endswith('path') and elem.get('id') == 'path5':
            path5 = elem
            break
    
    if path5:
        path_d = path5.get('d', '')
        transform_str = path5.get('transform', '')
        
        print("="*80)
        print("path5（中）のbbox計算（svgpathtools使用）")
        print("="*80)
        print(f"path d: {path_d[:100]}...")
        print(f"transform: {transform_str}")
        
        # svgpathtoolsでpathを解析
        path_obj = parse_path(path_d)
        print(f"\npathオブジェクト: {type(path_obj)}")
        print(f"セグメント数: {len(path_obj)}")
        
        # 元のbbox（transform適用前）
        bbox_original = path_obj.bbox()
        print(f"\n元のbbox（transform適用前）:")
        print(f"  x: {bbox_original[0]:.6f}, y: {bbox_original[1]:.6f}")
        print(f"  width: {bbox_original[2] - bbox_original[0]:.6f}")
        print(f"  height: {bbox_original[3] - bbox_original[1]:.6f}")
        
        # transformを適用
        cumulative_matrix = compute_cumulative_transform(path5, root)
        print(f"\n累積transform行列: {cumulative_matrix}")
        
        # 4つの角の座標を取得してtransformを適用
        x1, y1, x2, y2 = bbox_original
        corners = [
            (x1, y1),  # 左上
            (x2, y1),  # 右上
            (x2, y2),  # 右下
            (x1, y2)   # 左下
        ]
        
        transformed_corners = [apply_matrix_to_point(x, y, cumulative_matrix) for x, y in corners]
        print(f"\n変換後の4つの角:")
        for i, (x, y) in enumerate(transformed_corners):
            print(f"  角{i+1}: ({x:.6f}, {y:.6f})")
        
        # 変換後のbboxを計算
        xs = [p[0] for p in transformed_corners]
        ys = [p[1] for p in transformed_corners]
        
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        
        print(f"\n計算されたbbox（svgpathtools + transform）:")
        print(f"  min_x: {min_x:.6f}")
        print(f"  max_x: {max_x:.6f}")
        print(f"  min_y: {min_y:.6f}")
        print(f"  max_y: {max_y:.6f}")
        print(f"  width:  {max_x - min_x:.6f}")
        print(f"  height: {max_y - min_y:.6f}")
        
        # しかし、これは4つの角だけなので、回転やスケールがある場合は不正確
        # より正確には、pathのすべての点（制御点を含む）を取得する必要がある
        print(f"\n注意: これは4つの角のみで計算しています。")
        print(f"回転やスケールがある場合は、すべての点を取得する必要があります。")

