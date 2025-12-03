"""
「ＨＩＲＯＳＥ」と「廣瀬」の文字の重なりを確認
"""
from svg_parser import parse_svg

data = parse_svg('Study/svg_cvs/12038616.svg')

# 「ＨＩＲＯＳＥ」グループ
hirose_chars = [d for d in data if d['id'] in ['path8', 'path10', 'path12', 'path14', 'path16', 'path18']]
hirose_chars.sort(key=lambda x: x['id'])

print("=== 「ＨＩＲＯＳＥ」グループ ===")
for i, char in enumerate(hirose_chars):
    print(f"{char['id']}: min_x={char['min_x']:.2f}, max_x={char['max_x']:.2f}")
    if i > 0:
        prev_char = hirose_chars[i-1]
        overlap = not (prev_char['max_x'] < char['min_x'] or char['max_x'] < prev_char['min_x'])
        print(f"  -> 前の文字と重なっている: {overlap}")

# 「廣瀬」グループ
sehiro_chars = [d for d in data if d['id'] in ['path6', 'path22']]
sehiro_chars.sort(key=lambda x: x['id'])

print("\n=== 「廣瀬」グループ ===")
for i, char in enumerate(sehiro_chars):
    print(f"{char['id']}: min_x={char['min_x']:.2f}, max_x={char['max_x']:.2f}")
    if i > 0:
        prev_char = sehiro_chars[i-1]
        overlap = not (prev_char['max_x'] < char['min_x'] or char['max_x'] < prev_char['min_x'])
        print(f"  -> 前の文字と重なっている: {overlap}")

