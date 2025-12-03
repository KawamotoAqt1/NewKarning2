"""
検出したbboxをSVGファイルに矩形として描画する（シンプル版）
"""

import xml.etree.ElementTree as ET
from svg_parser import parse_svg


def draw_bbox_on_svg(svg_path: str, output_path: str = None):
    """
    SVGファイルに検出したbboxを矩形として描画
    """
    # bboxを取得
    results = parse_svg(svg_path)
    
    if not results:
        print(f"エラー: bboxが見つかりませんでした")
        return
    
    # SVGファイルを読み込む
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # SVGの名前空間
    svg_ns = 'http://www.w3.org/2000/svg'
    inkscape_ns = 'http://www.inkscape.org/namespaces/inkscape'
    
    # 新しいレイヤー（g要素）を作成
    bbox_layer = ET.Element(f'{{{svg_ns}}}g')
    bbox_layer.set('id', 'bbox_overlay')
    bbox_layer.set(f'{{{inkscape_ns}}}label', 'bbox_overlay')
    bbox_layer.set(f'{{{inkscape_ns}}}groupmode', 'layer')
    
    # 各bboxを矩形として描画
    colors = {'path5': '#ff0000', 'path7': '#00ff00'}  # 中=赤、谷=緑
    
    print("\n描画するbbox:")
    for result in results:
        if result['id'] in ['path5', 'path7']:  # 中谷のみ
            color = colors.get(result['id'], '#0000ff')
            
            print(f"  {result['id']}:")
            print(f"    x={result['min_x']:.6f}, y={result['min_y']:.6f}")
            print(f"    width={result['width']:.6f}, height={result['height']:.6f}")
            
            # 矩形を追加
            rect = ET.Element(f'{{{svg_ns}}}rect')
            rect.set('x', str(result['min_x']))
            rect.set('y', str(result['min_y']))
            rect.set('width', str(result['width']))
            rect.set('height', str(result['height']))
            rect.set('fill', 'none')
            rect.set('stroke', color)
            rect.set('stroke-width', '3')
            rect.set('stroke-dasharray', '5,5')
            rect.set('opacity', '0.9')
            rect.set('id', f"bbox_{result['id']}")
            bbox_layer.append(rect)
            
            # ラベルを追加
            text = ET.Element(f'{{{svg_ns}}}text')
            text.set('x', str(result['min_x']))
            text.set('y', str(max(10, result['min_y'] - 5)))
            text.set('fill', color)
            text.set('font-size', '14')
            text.set('font-family', 'Arial')
            text.set('font-weight', 'bold')
            text.text = f"{result['id']}"
            text.set('id', f"label_{result['id']}")
            bbox_layer.append(text)
    
    # rootにbboxレイヤーを追加
    root.append(bbox_layer)
    
    # 出力パスを決定
    if output_path is None:
        import os
        base_dir = os.path.dirname(svg_path)
        base_name = os.path.basename(svg_path)
        name, ext = os.path.splitext(base_name)
        output_path = os.path.join(base_dir, f"{name}_with_bbox{ext}")
    
    # SVGファイルを保存
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    print(f"\n✅ bboxを描画したSVGファイルを保存しました:")
    print(f"   {output_path}")


if __name__ == "__main__":
    svg_path = "Study/svg_cvs/06099095.svg"
    draw_bbox_on_svg(svg_path)

