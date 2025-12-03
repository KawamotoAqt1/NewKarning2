"""
12038616のtransform属性を確認
"""
import xml.etree.ElementTree as ET
from svg_parser import parse_transform

tree = ET.parse('Study/svg_cvs/12038616.svg')
root = tree.getroot()

for elem in root.iter():
    if elem.tag.endswith('path'):
        path_id = elem.get('id')
        if path_id in ['path6', 'path22']:
            transform_str = elem.get('transform', '')
            transform = parse_transform(transform_str)
            print(f"{path_id}: transform={transform_str}")
            print(f"  解析結果: tx={transform['tx']:.2f}, ty={transform['ty']:.2f}, sx={transform['sx']:.2f}, sy={transform['sy']:.2f}")
            print()

