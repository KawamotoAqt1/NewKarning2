"""
SVG解析モジュール
SVGファイルから各文字（path要素）のbounding boxを計算する
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
import re
import math

# transform_utilsから関数をインポート
from transform_utils import (
    identity_matrix,
    parse_transform,
    combine_transform,
    apply_matrix_to_point
)


def compute_cumulative_transform(elem: ET.Element, root: ET.Element) -> Tuple[float, float, float, float, float, float]:
    """
    指定された要素について、親要素から順にtransformを累積して合成した最終transform行列を返す
    
    <g transform="translate(10,20)">
        <g transform="scale(2)">
            <path transform="matrix(...)"/>
        </g>
    </g>
    
    この場合、path要素には translate → scale → matrix の順に適用された最終行列が返される
    
    Args:
        elem: 対象の要素
        root: SVGのルート要素
    
    Returns:
        累積されたtransform行列 (a, b, c, d, e, f)
    """
    # 親要素をたどって累積transformを計算
    cumulative_matrix = identity_matrix()
    
    # 親要素のリストを構築（ルートからelemまで）
    ancestors = []
    current = elem
    while current is not None and current != root:
        ancestors.insert(0, current)  # 先頭に挿入して順序を保持
        # 親要素を探す
        found_parent = None
        for parent in root.iter():
            for child in parent:
                if child == current:
                    found_parent = parent
                    break
            if found_parent:
                break
        current = found_parent
    
    # ルートから順にtransformを適用
    for ancestor in ancestors:
        if ancestor.tag.endswith('g') or ancestor.tag.endswith('svg'):
            transform_str = ancestor.get('transform', '')
            if transform_str:
                ancestor_matrix = parse_transform(transform_str)
                cumulative_matrix = combine_transform(cumulative_matrix, ancestor_matrix)
    
    # 要素自身のtransformも適用
    if elem.tag.endswith('g') or elem.tag.endswith('path') or elem.tag.endswith('svg'):
        transform_str = elem.get('transform', '')
        if transform_str:
            elem_matrix = parse_transform(transform_str)
            cumulative_matrix = combine_transform(cumulative_matrix, elem_matrix)
    
    return cumulative_matrix


def parse_path_d(path_d: str) -> List[tuple]:
    """
    SVG pathのd属性を解析して、座標点のリストを返す
    
    Args:
        path_d: path要素のd属性（例: "M 10,20 L 30,40 Z"）
    
    Returns:
        [(x, y), ...] の座標点リスト
    """
    if not path_d:
        return []
    
    points = []
    # コマンドと数値を分離（より正確な正規表現）
    # 数値は符号、小数点、指数表記に対応
    tokens = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', path_d)
    
    i = 0
    current_x, current_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    
    def read_number():
        """次のトークンを数値として読み取る"""
        nonlocal i
        if i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
            val = float(tokens[i])
            i += 1
            return val
        return None
    
    def read_point(is_relative=False):
        """次の2つの数値を座標点として読み取る"""
        nonlocal current_x, current_y
        x = read_number()
        if x is None:
            return None
        y = read_number()
        if y is None:
            return None
        
        if is_relative:
            x += current_x
            y += current_y
        
        current_x, current_y = x, y
        return (x, y)
    
    while i < len(tokens):
        token = tokens[i]
        is_relative = token.islower()
        cmd = token.upper()
        i += 1
        
        if cmd == 'M':  # MoveTo
            pt = read_point(is_relative)
            if pt:
                current_x, current_y = pt
                start_x, start_y = pt
                points.append(pt)
                # 連続する座標はLineToとして扱う
                while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                    pt = read_point(is_relative)
                    if pt:
                        points.append(pt)
        
        elif cmd == 'L':  # LineTo
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                pt = read_point(is_relative)
                if pt:
                    points.append(pt)
        
        elif cmd == 'H':  # Horizontal LineTo
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                x = read_number()
                if x is not None:
                    if is_relative:
                        x += current_x
                    current_x = x
                    points.append((x, current_y))
        
        elif cmd == 'V':  # Vertical LineTo
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                y = read_number()
                if y is not None:
                    if is_relative:
                        y += current_y
                    current_y = y
                    points.append((current_x, y))
        
        elif cmd == 'C':  # Cubic Bezier
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                # 制御点1, 制御点2, 終点を読み取る（終点のみを記録）
                for j in range(3):
                    pt = read_point(is_relative)
                    if pt and j == 2:  # 終点のみ
                        points.append(pt)
                    elif pt is None:
                        break
        
        elif cmd == 'S':  # Smooth Cubic Bezier
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                # 制御点2, 終点を読み取る（終点のみを記録）
                for j in range(2):
                    pt = read_point(is_relative)
                    if pt and j == 1:  # 終点のみ
                        points.append(pt)
                    elif pt is None:
                        break
        
        elif cmd == 'Q':  # Quadratic Bezier
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                # 制御点, 終点を読み取る（終点のみを記録）
                for j in range(2):
                    pt = read_point(is_relative)
                    if pt and j == 1:  # 終点のみ
                        points.append(pt)
                    elif pt is None:
                        break
        
        elif cmd == 'T':  # Smooth Quadratic Bezier
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                pt = read_point(is_relative)
                if pt:
                    points.append(pt)
        
        elif cmd == 'Z':  # ClosePath
            # 開始点に戻る
            if points:
                points.append((start_x, start_y))
                current_x, current_y = start_x, start_y
        
        elif cmd == 'A':  # Arc
            while i < len(tokens) and tokens[i] not in 'MmLlHhVvCcSsQqTtAaZz':
                # rx, ry, x-axis-rotation, large-arc-flag, sweep-flag, x, y
                # 最後のx, y（終点）のみを記録
                vals = []
                for j in range(7):
                    val = read_number()
                    if val is None:
                        break
                    vals.append(val)
                
                if len(vals) >= 7:
                    x, y = vals[5], vals[6]
                    if is_relative:
                        x += current_x
                        y += current_y
                    current_x, current_y = x, y
                    points.append((x, y))
    
    return points


def calculate_bbox_from_points(points: List[tuple]) -> Optional[Dict[str, float]]:
    """
    座標点のリストからbounding boxを計算
    
    Args:
        points: [(x, y), ...] の座標点リスト
    
    Returns:
        {"min_x": float, "max_x": float, "min_y": float, "max_y": float, "width": float, "height": float}
        または None（pointsが空の場合）
    """
    if not points:
        return None
    
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    
    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "width": max_x - min_x,
        "height": max_y - min_y
    }


def apply_transform_to_points(points: List[tuple], matrix: Tuple[float, float, float, float, float, float]) -> List[tuple]:
    """
    座標点リストにアフィン変換行列を適用
    
    Args:
        points: [(x, y), ...] の座標点リスト
        matrix: アフィン変換行列 (a, b, c, d, e, f)
    
    Returns:
        変換後の座標点リスト
    """
    result = []
    for x, y in points:
        new_x, new_y = apply_matrix_to_point(x, y, matrix)
        result.append((new_x, new_y))
    return result


def get_path_bbox(path_element: ET.Element, root: ET.Element, parent_matrix: Optional[Tuple[float, float, float, float, float, float]] = None) -> Optional[Dict[str, float]]:
    """
    単一のpath要素からbounding boxを計算
    
    すべてのtransformを適用した後の座標でbboxを計算する
    svgpathtoolsを使用してベジェ曲線の制御点も含めた正確なbboxを計算
    
    Args:
        path_element: path要素のET.Element
        root: SVGのルート要素（階層的なtransform計算のため）
        parent_matrix: 親要素のtransform行列（2×3形式、オプション）
    
    Returns:
        bounding box情報の辞書、またはNone
    """
    # path要素のd属性を取得
    path_d = path_element.get('d', '')
    if not path_d:
        return None
    
    # svgpathtoolsが利用可能な場合はそれを使用（より正確）
    try:
        from svgpathtools import parse_path
        path_obj = parse_path(path_d)
        # 元のbbox（transform適用前）
        bbox_original = path_obj.bbox()
        if bbox_original is None:
            return None
        
        x1, y1, x2, y2 = bbox_original
        
        # 累積transformを計算
        if parent_matrix is not None:
            path_transform_str = path_element.get('transform', '')
            if path_transform_str:
                path_matrix = parse_transform(path_transform_str)
                cumulative_matrix = combine_transform(parent_matrix, path_matrix)
            else:
                cumulative_matrix = parent_matrix
        else:
            cumulative_matrix = compute_cumulative_transform(path_element, root)
        
        # bboxの4つの角と、ベジェ曲線の制御点も含めたすべての点を取得
        # まず、pathオブジェクトからすべての点を取得
        all_points = []
        for segment in path_obj:
            # 各セグメントの端点と制御点を取得
            if hasattr(segment, 'start'):
                all_points.append((segment.start.real, segment.start.imag))
            if hasattr(segment, 'end'):
                all_points.append((segment.end.real, segment.end.imag))
            # ベジェ曲線の制御点
            if hasattr(segment, 'control'):
                if isinstance(segment.control, list):
                    for ctrl in segment.control:
                        all_points.append((ctrl.real, ctrl.imag))
                else:
                    all_points.append((segment.control.real, segment.control.imag))
            if hasattr(segment, 'control1'):
                all_points.append((segment.control1.real, segment.control1.imag))
            if hasattr(segment, 'control2'):
                all_points.append((segment.control2.real, segment.control2.imag))
        
        # すべての点にtransformを適用
        if all_points:
            transformed_points = apply_transform_to_points(all_points, cumulative_matrix)
            bbox = calculate_bbox_from_points(transformed_points)
            return bbox
        else:
            # フォールバック: bboxの4つの角のみ
            corners = [
                (x1, y1),  # 左上
                (x2, y1),  # 右上
                (x2, y2),  # 右下
                (x1, y2)   # 左下
            ]
            transformed_corners = [apply_matrix_to_point(x, y, cumulative_matrix) for x, y in corners]
            xs = [p[0] for p in transformed_corners]
            ys = [p[1] for p in transformed_corners]
            return {
                "min_x": min(xs),
                "max_x": max(xs),
                "min_y": min(ys),
                "max_y": max(ys),
                "width": max(xs) - min(xs),
                "height": max(ys) - min(ys)
            }
    except ImportError:
        # svgpathtoolsが利用できない場合は従来の方法を使用
        pass
    except Exception as e:
        # svgpathtoolsでエラーが発生した場合は従来の方法にフォールバック
        print(f"Warning: svgpathtoolsでエラーが発生しました: {e}")
        pass
    
    # 従来の方法（フォールバック）
    points = parse_path_d(path_d)
    if not points:
        return None
    
    # 累積transformを計算
    if parent_matrix is not None:
        path_transform_str = path_element.get('transform', '')
        if path_transform_str:
            path_matrix = parse_transform(path_transform_str)
            cumulative_matrix = combine_transform(parent_matrix, path_matrix)
        else:
            cumulative_matrix = parent_matrix
    else:
        cumulative_matrix = compute_cumulative_transform(path_element, root)
    
    # transformを適用
    transformed_points = apply_transform_to_points(points, cumulative_matrix)
    
    # bounding boxを計算
    bbox = calculate_bbox_from_points(transformed_points)
    
    return bbox


def find_path_by_id(root: ET.Element, target_id: str) -> Optional[ET.Element]:
    """
    SVG内で指定されたidを持つpath要素を検索
    
    Args:
        root: SVGのルート要素
        target_id: 検索するid
    
    Returns:
        見つかったpath要素、またはNone
    """
    # 再帰的に全ての要素を走査
    for elem in root.iter():
        if elem.tag.endswith('path') and elem.get('id') == target_id:
            return elem
    return None


def get_group_bbox(group_element: ET.Element, root: ET.Element, parent_matrix: Optional[Tuple[float, float, float, float, float, float]] = None) -> Optional[Dict[str, float]]:
    """
    g要素（グループ）内の全path要素からbounding boxを計算
    
    すべてのtransformを適用した後の座標でbboxを計算する
    
    Args:
        group_element: g要素のET.Element
        root: SVGのルート要素（階層的なtransform計算のため）
        parent_matrix: 親要素のtransform行列（2×3形式、オプション）
    
    Returns:
        グループ全体のbounding box情報の辞書、またはNone
    """
    all_points = []
    
    # グループの累積transformを計算
    if parent_matrix is not None:
        # 親のtransformとグループ自身のtransformを合成
        group_transform_str = group_element.get('transform', '')
        if group_transform_str:
            group_matrix = parse_transform(group_transform_str)
            cumulative_matrix = combine_transform(parent_matrix, group_matrix)
        else:
            cumulative_matrix = parent_matrix
    else:
        # compute_cumulative_transformを使用して階層的に計算
        cumulative_matrix = compute_cumulative_transform(group_element, root)
    
    # グループ内の全path要素を走査
    for path_elem in group_element.iter():
        if path_elem.tag.endswith('path'):
            path_d = path_elem.get('d', '')
            if path_d:
                points = parse_path_d(path_d)
                if points:
                    # path要素の累積transformを計算
                    path_cumulative_matrix = compute_cumulative_transform(path_elem, root)
                    # transformを適用
                    transformed_points = apply_transform_to_points(points, path_cumulative_matrix)
                    all_points.extend(transformed_points)
    
    if not all_points:
        return None
    
    bbox = calculate_bbox_from_points(all_points)
    
    return bbox


def collect_parent_transforms(root: ET.Element) -> Dict[ET.Element, Tuple[float, float, float, float, float, float]]:
    """
    全ての要素について、親要素までのtransform（要素自身のtransformは除く）を事前に収集
    
    Args:
        root: ルート要素
    
    Returns:
        要素をキーにした親要素のtransform行列（2×3形式）の辞書
    """
    transforms = {}
    
    def traverse(elem: ET.Element, parent_matrix: Tuple[float, float, float, float, float, float]):
        """再帰的に要素を走査してtransformを収集"""
        # 現在の要素の親要素のtransformを保存（要素自身のtransformは含まない）
        transforms[elem] = parent_matrix
        
        # 現在の要素のtransformを計算（子要素に渡すため）
        current_matrix = parent_matrix
        
        if elem.tag.endswith('g') or elem.tag.endswith('svg'):
            transform_str = elem.get('transform', '')
            if transform_str:
                elem_matrix = parse_transform(transform_str)
                # transformを合成（行列の乗算）
                current_matrix = combine_transform(current_matrix, elem_matrix)
        
        # 子要素を再帰的に処理
        for child in elem:
            traverse(child, current_matrix)
    
    # ルート要素から開始（単位行列）
    initial_matrix = identity_matrix()
    traverse(root, initial_matrix)
    
    return transforms


def parse_svg_groups(svg_path: str) -> List[List[str]]:
    """
    SVGファイルを解析して、名前ごとのグループ（<g>要素）内のpath要素のidを取得
    
    名前のグループは、直接の子要素としてpath要素が2つ以上含まれる<g>要素と判定する
    
    Args:
        svg_path: SVGファイルのパス
    
    Returns:
        グループごとのpath idのリスト [[path5, path7], [path9, path11, ...], ...]
    """
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        groups = []
        
        # 全ての<g>要素を走査
        for g_elem in root.iter():
            if g_elem.tag.endswith('g'):
                g_id = g_elem.get('id', '')
                
                # 直接の子要素としてpath要素のidを収集（ネストされた要素は除外）
                path_ids = []
                for child in g_elem:
                    if child.tag.endswith('path'):
                        path_id = child.get('id')
                        if path_id and path_id.startswith('path'):
                            path_ids.append(path_id)
                
                # 直接の子要素としてpath要素が1つ以上含まれるグループを追加
                # （これが名前のグループと判定）
                # 1つのpath要素でも名前として扱う（例：path3が単独で1つの名前）
                if len(path_ids) >= 1:
                    groups.append(path_ids)
        
        return groups
    
    except Exception as e:
        print(f"Error parsing SVG groups {svg_path}: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_svg(svg_path: str) -> List[Dict[str, float]]:
    """
    SVGファイルを解析して、各文字（idを持つ要素）のbounding boxを計算
    
    Args:
        svg_path: SVGファイルのパス
    
    Returns:
        [{"id": str, "min_x": float, "max_x": float, "min_y": float, "max_y": float, "width": float, "height": float}, ...]
    """
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # SVGのviewBoxを取得（必要に応じて使用）
        viewbox = root.get('viewBox', '')
        
        # 全ての要素について親要素のtransformを事前に収集
        parent_transforms = collect_parent_transforms(root)
        
        results = []
        processed_ids = set()
        
        # 再帰的に要素を走査して、clipPath内のpath要素を除外
        def traverse_for_paths(elem: ET.Element, in_clip_path: bool = False):
            """再帰的に要素を走査してpath要素を収集（clipPath内を除外）"""
            # clipPath内かどうかを判定
            current_in_clip_path = in_clip_path or elem.tag.endswith('clipPath')
            
            # g要素をチェック
            if elem.tag.endswith('g'):
                g_id = elem.get('id')
                if g_id and g_id.startswith('path'):
                    if g_id not in processed_ids:
                        parent_matrix = parent_transforms.get(elem, identity_matrix())
                        bbox = get_group_bbox(elem, root, parent_matrix)
                        if bbox:
                            results.append({
                                "id": g_id,
                                **bbox
                            })
                            processed_ids.add(g_id)
            
            # path要素をチェック（clipPath内でない場合のみ）
            if elem.tag.endswith('path') and not current_in_clip_path:
                path_id = elem.get('id')
                if path_id and path_id.startswith('path'):
                    if path_id not in processed_ids:
                        parent_matrix = parent_transforms.get(elem, identity_matrix())
                        bbox = get_path_bbox(elem, root, parent_matrix)
                        if bbox:
                            results.append({
                                "id": path_id,
                                **bbox
                            })
                            processed_ids.add(path_id)
            
            # 子要素を再帰的に処理
            for child in elem:
                traverse_for_paths(child, current_in_clip_path)
        
        # ルート要素から再帰的に走査
        traverse_for_paths(root)
        
        return results
    
    except Exception as e:
        print(f"Error parsing SVG {svg_path}: {e}")
        import traceback
        traceback.print_exc()
        return []

