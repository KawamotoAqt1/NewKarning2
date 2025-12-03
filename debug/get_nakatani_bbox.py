"""中谷のbboxを取得"""
from svg_parser import parse_svg

svg_path = "Study/svg_cvs/06099095.svg"
results = parse_svg(svg_path)

print("="*80)
print("中谷（06099095.svg）のbbox検出結果")
print("="*80)

for result in results:
    if result['id'] in ['path5', 'path7']:
        print(f"\n{result['id']}:")
        print(f"  min_x: {result['min_x']:.6f}")
        print(f"  max_x: {result['max_x']:.6f}")
        print(f"  min_y: {result['min_y']:.6f}")
        print(f"  max_y: {result['max_y']:.6f}")
        print(f"  width:  {result['width']:.6f}")
        print(f"  height: {result['height']:.6f}")
        print(f"  中心X:  {(result['min_x'] + result['max_x']) / 2:.6f}")
        print(f"  中心Y:  {(result['min_y'] + result['max_y']) / 2:.6f}")

