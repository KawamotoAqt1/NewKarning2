"""
12038616の「ＨＩＲＯＳＥ」グループの文字のmin_yとmax_yを確認
"""
from svg_parser import parse_svg

data = parse_svg('Study/svg_cvs/12038616.svg')
hirose_chars = [d for d in data if d['id'] in ['path2', 'path4', 'path8', 'path10', 'path12', 'path14', 'path16', 'path18', 'path20', 'path24', 'path26', 'path28', 'path30']]

print("=== ＨＩＲＯＳＥグループの文字 ===")
for char in sorted(hirose_chars, key=lambda x: x['id']):
    print(f"{char['id']}: min_y={char['min_y']:.2f}, max_y={char['max_y']:.2f}, min_x={char['min_x']:.2f}, max_x={char['max_x']:.2f}")
    if char['min_y'] > char['max_y']:
        print(f"  -> Yスケールが負（min_y > max_y）")
    else:
        print(f"  -> Yスケールが正（min_y <= max_y）")

