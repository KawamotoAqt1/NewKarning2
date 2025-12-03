"""
検出したbboxをSVGファイルに矩形として描画する
"""

import xml.etree.ElementTree as ET
from svg_parser import parse_svg
from pathlib import Path


def draw_bbox_on_svg(svg_path: str, output_path: str = None):
    """
    SVGファイルに検出したbboxを矩形として描画
    
    Args:
        svg_path: 元のSVGファイルのパス
        output_path: 出力先のSVGファイルのパス（Noneの場合は自動生成）
    """
    # bboxを取得
    results = parse_svg(svg_path)
    
    if not results:
        print(f"エラー: bboxが見つかりませんでした")
        return
    
    # SVGファイルを読み込む
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # 名前空間を取得
    nsmap = {}
    if root.tag.startswith('{'):
        ns, tag = root.tag[1:].split('}', 1)
        nsmap['svg'] = ns
    else:
        nsmap['svg'] = 'http://www.w3.org/2000/svg'
    
    svg_ns = nsmap['svg']
    
    # 新しいレイヤー（g要素）を作成してbboxを描画
    bbox_layer = ET.Element(f'{{{svg_ns}}}g')
    bbox_layer.set('id', 'bbox_overlay')
    bbox_layer.set('{http://www.inkscape.org/namespaces/inkscape}label', 'bbox_overlay')
    bbox_layer.set('{http://www.inkscape.org/namespaces/inkscape}groupmode', 'layer')
    
    # 各bboxを矩形として描画
    colors = {'path5': '#ff0000', 'path7': '#00ff00'}  # 中=赤、谷=緑
    
    for result in results:
        if result['id'] in ['path5', 'path7']:  # 中谷のみ
            color = colors.get(result['id'], '#0000ff')
            
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
            
            # テキストラベルを追加
            text = ET.Element(f'{{{svg_ns}}}text')
            text.set('x', str(result['min_x']))
            text.set('y', str(max(0, result['min_y'] - 10)))
            text.set('fill', color)
            text.set('font-size', '14')
            text.set('font-family', 'Arial, sans-serif')
            text.set('font-weight', 'bold')
            text.text = f"{result['id']} bbox"
            text.set('id', f"label_{result['id']}")
            
            # 詳細情報のテキスト
            detail_text = ET.Element(f'{{{svg_ns}}}text')
            detail_text.set('x', str(result['min_x']))
            detail_text.set('y', str(max(15, result['min_y'] - 10 + 15)))
            detail_text.set('fill', color)
            detail_text.set('font-size', '10')
            detail_text.set('font-family', 'Arial, sans-serif')
            detail_text.text = f"({result['min_x']:.1f}, {result['min_y']:.1f}) w:{result['width']:.1f} h:{result['height']:.1f}"
            detail_text.set('id', f"detail_{result['id']}")
            
            bbox_layer.append(rect)
            bbox_layer.append(text)
            bbox_layer.append(detail_text)
    
    # g1要素（メインレイヤー）を探して、その後にbboxレイヤーを追加
    g1 = None
    for elem in root.iter():
        if elem.get('id') == 'g1':
            g1 = elem
            break
    
    # g1の親要素（通常はsvg要素）にbboxレイヤーを追加
    if g1 is not None:
        # g1の親を探す
        parent = None
        for elem in root.iter():
            for child in elem:
                if child == g1:
                    parent = elem
                    break
            if parent:
                break
        
        if parent is not None:
            parent.append(bbox_layer)
        else:
            # 親が見つからない場合はrootに追加
            root.append(bbox_layer)
    else:
        # g1が見つからない場合はrootに追加
        root.append(bbox_layer)
    
    # 出力パスを決定
    if output_path is None:
        svg_file = Path(svg_path)
        output_path = svg_file.parent / f"{svg_file.stem}_with_bbox.svg"
    
    # SVGファイルを保存
    tree.write(str(output_path), encoding='utf-8', xml_declaration=True)
    
    print(f"✅ bboxを描画したSVGファイルを保存しました: {output_path}")
    print(f"\n描画したbbox:")
    for result in results:
        if result['id'] in ['path5', 'path7']:
            print(f"  {result['id']}:")
            print(f"    x={result['min_x']:.6f}, y={result['min_y']:.6f}")
            print(f"    width={result['width']:.6f}, height={result['height']:.6f}")


def main():
    """メイン関数"""
    svg_path = "Study/svg_cvs/06099095.svg"
    output_path = "Study/svg_cvs/06099095_with_bbox.svg"
    
    draw_bbox_on_svg(svg_path, output_path)


if __name__ == "__main__":
    main()

