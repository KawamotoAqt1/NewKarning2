from svg_parser import parse_svg

data = parse_svg('Study/svg_cvs/12193287.svg')
chars = [d for d in data if d['id'] in ['path6', 'path8']]

print('修正後の位置情報:')
for d in sorted(chars, key=lambda x: x['min_y']):
    center_y = (d['min_y'] + d['max_y']) / 2
    print(f"{d['id']}: min_y={d['min_y']:.2f}, max_y={d['max_y']:.2f}, center_y={center_y:.2f}")

