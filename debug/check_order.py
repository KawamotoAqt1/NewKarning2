"""CSVの順序と実際の表示順序を確認"""
from svg_parser import parse_svg
from csv_loader import load_csv
from gap_extractor import merge_svg_csv

# 中谷
svg_data = parse_svg('Study/svg_cvs/06099095.svg')
csv_data = load_csv('Study/svg_cvs/06099095.csv')
merged = merge_svg_csv(svg_data, csv_data)

print("中谷のbbox:")
for m in merged:
    if m['id'] in ['path5', 'path7']:
        print(f"  {m['id']} ({m['text']}): x=[{m['min_x']:.2f}, {m['max_x']:.2f}], y=[{m['min_y']:.2f}, {m['max_y']:.2f}]")
        print(f"    中心X: {(m['min_x'] + m['max_x']) / 2:.2f}")

print("\nCSVの順序:")
for i, m in enumerate(merged):
    if m['id'] in ['path5', 'path7']:
        print(f"  {i}: {m['id']} ({m['text']})")

print("\n実際の表示順序（X座標でソート）:")
sorted_by_x = sorted([m for m in merged if m['id'] in ['path5', 'path7']], key=lambda x: (x['min_x'] + x['max_x']) / 2)
for i, m in enumerate(sorted_by_x):
    print(f"  {i}: {m['id']} ({m['text']}) - 中心X: {(m['min_x'] + m['max_x']) / 2:.2f}")

