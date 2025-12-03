"""
12038616の「瀬廣」の位置関係を調べる
"""
from svg_parser import parse_svg

data = parse_svg('Study/svg_cvs/12038616.svg')
path6_data = [d for d in data if d['id'] == 'path6'][0]
path22_data = [d for d in data if d['id'] == 'path22'][0]

print("=== 位置関係の比較 ===")
print(f"path6（廣）: min_x={path6_data['min_x']:.2f}, max_x={path6_data['max_x']:.2f}, center_x={(path6_data['min_x'] + path6_data['max_x'])/2:.2f}")
print(f"path22（瀬）: min_x={path22_data['min_x']:.2f}, max_x={path22_data['max_x']:.2f}, center_x={(path22_data['min_x'] + path22_data['max_x'])/2:.2f}")

print(f"\nX座標の比較:")
print(f"  path6のmin_x ({path6_data['min_x']:.2f}) vs path22のmin_x ({path22_data['min_x']:.2f})")
print(f"  path6のcenter_x ({(path6_data['min_x'] + path6_data['max_x'])/2:.2f}) vs path22のcenter_x ({(path22_data['min_x'] + path22_data['max_x'])/2:.2f})")
print(f"  path6のmax_x ({path6_data['max_x']:.2f}) vs path22のmax_x ({path22_data['max_x']:.2f})")

print(f"\n実際の表示位置（左から右の順）:")
if path6_data['min_x'] < path22_data['min_x']:
    print(f"  1. path6（廣）: min_x={path6_data['min_x']:.2f} (左)")
    print(f"  2. path22（瀬）: min_x={path22_data['min_x']:.2f} (右)")
else:
    print(f"  1. path22（瀬）: min_x={path22_data['min_x']:.2f} (左)")
    print(f"  2. path6（廣）: min_x={path6_data['min_x']:.2f} (右)")

