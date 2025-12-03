"""transform適用の検証"""
from svg_parser import parse_svg
from csv_loader import load_csv
from gap_extractor import merge_svg_csv, calculate_gap_actual

print("="*80)
print("transform適用の検証")
print("="*80)

# 中谷
print("\n【中谷（06099095.svg）】")
svg_data = parse_svg('Study/svg_cvs/06099095.svg')
csv_data = load_csv('Study/svg_cvs/06099095.csv')
merged = merge_svg_csv(svg_data, csv_data)

print("\n各文字のbbox（transform適用後）:")
for m in merged:
    print(f"  {m['id']} ({m['text']}): x=[{m['min_x']:.2f}, {m['max_x']:.2f}], y=[{m['min_y']:.2f}, {m['max_y']:.2f}], "
          f"中心X={(m['min_x'] + m['max_x']) / 2:.2f}")

print("\nCSV順序でのgap_actual:")
pairs = calculate_gap_actual(merged)
for pair in pairs:
    print(f"  {pair['left']} → {pair['right']}: {pair['gap_actual']:.2f}px")

print("\n実際の表示順序（X座標でソート）でのgap_actual:")
sorted_by_x = sorted(merged, key=lambda x: (x['min_x'] + x['max_x']) / 2)
for i in range(len(sorted_by_x) - 1):
    current = sorted_by_x[i]
    next_item = sorted_by_x[i + 1]
    gap = next_item['min_x'] - current['max_x']
    print(f"  {current['text']} ({current['id']}) → {next_item['text']} ({next_item['id']}): {gap:.2f}px")

# 宮崎
print("\n" + "="*80)
print("【宮崎（06098954.svg）】")
svg_data2 = parse_svg('Study/svg_cvs/06098954.svg')
csv_data2 = load_csv('Study/svg_cvs/06098954.csv')
merged2 = merge_svg_csv(svg_data2, csv_data2)

print("\n各文字のbbox（transform適用後）:")
for m in merged2:
    print(f"  {m['id']} ({m['text']}): x=[{m['min_x']:.2f}, {m['max_x']:.2f}], y=[{m['min_y']:.2f}, {m['max_y']:.2f}], "
          f"中心X={(m['min_x'] + m['max_x']) / 2:.2f}")

print("\nCSV順序でのgap_actual:")
pairs2 = calculate_gap_actual(merged2)
for pair in pairs2:
    print(f"  {pair['left']} → {pair['right']}: {pair['gap_actual']:.2f}px")

print("\n実際の表示順序（X座標でソート）でのgap_actual:")
sorted_by_x2 = sorted(merged2, key=lambda x: (x['min_x'] + x['max_x']) / 2)
for i in range(len(sorted_by_x2) - 1):
    current = sorted_by_x2[i]
    next_item = sorted_by_x2[i + 1]
    gap = next_item['min_x'] - current['max_x']
    print(f"  {current['text']} ({current['id']}) → {next_item['text']} ({next_item['id']}): {gap:.2f}px")

