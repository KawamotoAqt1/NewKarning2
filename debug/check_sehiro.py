"""
「廣瀬」の位置関係を確認
"""
from svg_parser import parse_svg

data = parse_svg('Study/svg_cvs/12038616.svg')
path6 = [d for d in data if d['id'] == 'path6'][0]
path22 = [d for d in data if d['id'] == 'path22'][0]

print("=== 位置関係の比較 ===")
print(f"path6（廣）: min_x={path6['min_x']:.2f}, max_x={path6['max_x']:.2f}, center_x={(path6['min_x'] + path6['max_x'])/2:.2f}")
print(f"path22（瀬）: min_x={path22['min_x']:.2f}, max_x={path22['max_x']:.2f}, center_x={(path22['min_x'] + path22['max_x'])/2:.2f}")

print(f"\nmin_xでソート（昇順）:")
if path6['min_x'] < path22['min_x']:
    print(f"  1. path6（廣）: min_x={path6['min_x']:.2f}")
    print(f"  2. path22（瀬）: min_x={path22['min_x']:.2f}")
    print(f"  -> 廣瀬")
else:
    print(f"  1. path22（瀬）: min_x={path22['min_x']:.2f}")
    print(f"  2. path6（廣）: min_x={path6['min_x']:.2f}")
    print(f"  -> 瀬廣")

print(f"\nmax_xでソート（降順）:")
if path6['max_x'] > path22['max_x']:
    print(f"  1. path6（廣）: max_x={path6['max_x']:.2f}")
    print(f"  2. path22（瀬）: max_x={path22['max_x']:.2f}")
    print(f"  -> 廣瀬")
else:
    print(f"  1. path22（瀬）: max_x={path22['max_x']:.2f}")
    print(f"  2. path6（廣）: max_x={path6['max_x']:.2f}")
    print(f"  -> 瀬廣")

