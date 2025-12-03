"""
Transform関連のユーティリティ関数
SVGのtransform属性を解析し、アフィン変換行列として扱う
"""

import re
import math
from typing import Tuple, Optional


def identity_matrix() -> Tuple[float, float, float, float, float, float]:
    """
    単位行列（2×3形式）を返す
    
    Returns:
        (a, b, c, d, e, f) のタプル（matrix(a, b, c, d, e, f) に対応）
    """
    return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def parse_transform(transform_str: str) -> Tuple[float, float, float, float, float, float]:
    """
    transform属性を解析して、アフィン変換行列（2×3形式）を返す
    
    SVGのtransform属性は以下の形式をサポート：
    - translate(tx, ty)
    - translate(tx)  # ty=0
    - scale(sx, sy)
    - scale(sx)  # sy=sx
    - matrix(a, b, c, d, e, f)
    - rotate(angle [, cx, cy])
    
    複数のtransformが指定されている場合、左から右に適用される
    例: "translate(10,20) scale(2) matrix(...)"
    
    Args:
        transform_str: transform属性の文字列
    
    Returns:
        (a, b, c, d, e, f) のタプル（matrix(a, b, c, d, e, f) に対応）
    """
    if not transform_str or not transform_str.strip():
        return identity_matrix()
    
    # 単位行列から開始
    result_matrix = identity_matrix()
    
    # 複数のtransformが指定されている場合、左から右に適用
    i = 0
    while i < len(transform_str):
        # 空白をスキップ
        while i < len(transform_str) and transform_str[i].isspace():
            i += 1
        if i >= len(transform_str):
            break
        
        # matrix(a, b, c, d, e, f) のパターン（最優先）
        matrix_match = re.match(r'matrix\s*\(\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if matrix_match:
            a, b, c, d, e, f = map(float, matrix_match.groups())
            matrix = (a, b, c, d, e, f)
            result_matrix = combine_transform(result_matrix, matrix)
            i += matrix_match.end()
            continue
        
        # translate(x, y) のパターン
        translate_match = re.match(r'translate\s*\(\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if translate_match:
            tx = float(translate_match.group(1))
            ty = float(translate_match.group(2))
            translate_matrix = (1.0, 0.0, 0.0, 1.0, tx, ty)
            result_matrix = combine_transform(result_matrix, translate_matrix)
            i += translate_match.end()
            continue
        
        # translate(x) のパターン（yが省略された場合、y=0）
        translate_match = re.match(r'translate\s*\(\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if translate_match:
            tx = float(translate_match.group(1))
            translate_matrix = (1.0, 0.0, 0.0, 1.0, tx, 0.0)
            result_matrix = combine_transform(result_matrix, translate_matrix)
            i += translate_match.end()
            continue
        
        # scale(x, y) のパターン
        scale_match = re.match(r'scale\s*\(\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if scale_match:
            sx = float(scale_match.group(1))
            sy = float(scale_match.group(2))
            scale_matrix = (sx, 0.0, 0.0, sy, 0.0, 0.0)
            result_matrix = combine_transform(result_matrix, scale_matrix)
            i += scale_match.end()
            continue
        
        # scale(x) のパターン（yが省略された場合、y=x）
        scale_match = re.match(r'scale\s*\(\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if scale_match:
            sx = float(scale_match.group(1))
            scale_matrix = (sx, 0.0, 0.0, sx, 0.0, 0.0)
            result_matrix = combine_transform(result_matrix, scale_matrix)
            i += scale_match.end()
            continue
        
        # rotate(angle, cx, cy) のパターン
        rotate_match = re.match(r'rotate\s*\(\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*,\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if rotate_match:
            angle = float(rotate_match.group(1))
            cx = float(rotate_match.group(2))
            cy = float(rotate_match.group(3))
            # 回転中心を考慮した回転行列
            angle_rad = math.radians(angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            # translate(-cx, -cy) * rotate(angle) * translate(cx, cy)
            rotate_matrix = (
                cos_a, sin_a, -sin_a, cos_a,
                cx - cx * cos_a + cy * sin_a,
                cy - cx * sin_a - cy * cos_a
            )
            result_matrix = combine_transform(result_matrix, rotate_matrix)
            i += rotate_match.end()
            continue
        
        # rotate(angle) のパターン（回転中心は原点）
        rotate_match = re.match(r'rotate\s*\(\s*([-\d.eE+-]+)\s*\)', transform_str[i:])
        if rotate_match:
            angle = float(rotate_match.group(1))
            angle_rad = math.radians(angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            rotate_matrix = (cos_a, sin_a, -sin_a, cos_a, 0.0, 0.0)
            result_matrix = combine_transform(result_matrix, rotate_matrix)
            i += rotate_match.end()
            continue
        
        # マッチしない場合は1文字進む（エラー回避）
        i += 1
    
    return result_matrix


def combine_transform(matrix1: Tuple[float, float, float, float, float, float],
                      matrix2: Tuple[float, float, float, float, float, float]) -> Tuple[float, float, float, float, float, float]:
    """
    2つのアフィン変換行列を合成（行列の乗算）
    
    matrix1 を適用した後に matrix2 を適用する場合：
    result = matrix2 × matrix1
    
    3×3アフィン行列として扱う：
    [a c e]   [a1 c1 e1]   [a2 c2 e2]
    [b d f] = [b1 d1 f1] × [b2 d2 f2]
    [0 0 1]   [0  0  1 ]   [0  0  1 ]
    
    Args:
        matrix1: 最初に適用する行列 (a1, b1, c1, d1, e1, f1)
        matrix2: 次に適用する行列 (a2, b2, c2, d2, e2, f2)
    
    Returns:
        合成された行列 (a, b, c, d, e, f)
    """
    a1, b1, c1, d1, e1, f1 = matrix1
    a2, b2, c2, d2, e2, f2 = matrix2
    
    # 行列の乗算（2×3形式、3×3アフィン行列として計算）
    # result = matrix2 × matrix1
    a = a2 * a1 + b2 * c1
    b = a2 * b1 + b2 * d1
    c = c2 * a1 + d2 * c1
    d = c2 * b1 + d2 * d1
    e = e2 * a1 + f2 * c1 + e1
    f = e2 * b1 + f2 * d1 + f1
    
    return (a, b, c, d, e, f)


def apply_matrix_to_point(x: float, y: float, matrix: Tuple[float, float, float, float, float, float]) -> Tuple[float, float]:
    """
    座標点にアフィン変換行列を適用
    
    [x']   [a c e] [x]
    [y'] = [b d f] [y]
    [1 ]   [0 0 1] [1]
    
    x' = a*x + c*y + e
    y' = b*x + d*y + f
    
    Args:
        x: 元のX座標
        y: 元のY座標
        matrix: アフィン変換行列 (a, b, c, d, e, f)
    
    Returns:
        変換後の座標 (new_x, new_y)
    """
    a, b, c, d, e, f = matrix
    
    new_x = a * x + c * y + e
    new_y = b * x + d * y + f
    
    return (new_x, new_y)

