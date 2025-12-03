#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dataset_train/06099095.svgからN(path21)とI(path23)の位置関係を解析
"""

import xml.etree.ElementTree as ET
from svg_parser import get_path_bbox, find_path_by_id

# SVGファイルを読み込む
svg_path = "dataset_train/06099095.svg"
tree = ET.parse(svg_path)
root = tree.getroot()

# path21とpath23を取得
path21 = find_path_by_id(root, "path21")
path23 = find_path_by_id(root, "path23")

print("=" * 80)
print("N(path21)とI(path23)の位置関係")
print("=" * 80)
print()

if path21 is None:
    print("エラー: path21が見つかりません")
else:
    print("=== N (path21) ===")
    transform_str = path21.get('transform', '')
    print(f"transform: {transform_str}")
    
    # bboxを計算
    bbox21 = get_path_bbox(path21, root)
    if bbox21:
        print(f"bbox:")
        print(f"  min_x: {bbox21['min_x']:.2f}px")
        print(f"  max_x: {bbox21['max_x']:.2f}px")
        print(f"  min_y: {bbox21['min_y']:.2f}px")
        print(f"  max_y: {bbox21['max_y']:.2f}px")
        print(f"  width: {bbox21['width']:.2f}px")
        print(f"  height: {bbox21['height']:.2f}px")
        print(f"  center_x: {(bbox21['min_x'] + bbox21['max_x']) / 2:.2f}px")
        print(f"  center_y: {(bbox21['min_y'] + bbox21['max_y']) / 2:.2f}px")
    else:
        print("エラー: bboxの計算に失敗しました")

print()

if path23 is None:
    print("エラー: path23が見つかりません")
else:
    print("=== I (path23) ===")
    transform_str = path23.get('transform', '')
    print(f"transform: {transform_str}")
    
    # bboxを計算
    bbox23 = get_path_bbox(path23, root)
    if bbox23:
        print(f"bbox:")
        print(f"  min_x: {bbox23['min_x']:.2f}px")
        print(f"  max_x: {bbox23['max_x']:.2f}px")
        print(f"  min_y: {bbox23['min_y']:.2f}px")
        print(f"  max_y: {bbox23['max_y']:.2f}px")
        print(f"  width: {bbox23['width']:.2f}px")
        print(f"  height: {bbox23['height']:.2f}px")
        print(f"  center_x: {(bbox23['min_x'] + bbox23['max_x']) / 2:.2f}px")
        print(f"  center_y: {(bbox23['min_y'] + bbox23['max_y']) / 2:.2f}px")
    else:
        print("エラー: bboxの計算に失敗しました")

print()

# 位置関係を計算
if bbox21 and bbox23:
    print("=== 位置関係 ===")
    print(f"Nの右端 (max_x): {bbox21['max_x']:.2f}px")
    print(f"Iの左端 (min_x): {bbox23['min_x']:.2f}px")
    print(f"gap_actual = I.min_x - N.max_x = {bbox23['min_x']:.2f} - {bbox21['max_x']:.2f} = {bbox23['min_x'] - bbox21['max_x']:.3f}px")
    print()
    print(f"Nの中心X: {(bbox21['min_x'] + bbox21['max_x']) / 2:.2f}px")
    print(f"Iの中心X: {(bbox23['min_x'] + bbox23['max_x']) / 2:.2f}px")
    print(f"中心間の距離: {abs((bbox23['min_x'] + bbox23['max_x']) / 2 - (bbox21['min_x'] + bbox21['max_x']) / 2):.2f}px")
    print()
    print(f"Nの中心Y: {(bbox21['min_y'] + bbox21['max_y']) / 2:.2f}px")
    print(f"Iの中心Y: {(bbox23['min_y'] + bbox23['max_y']) / 2:.2f}px")
    print(f"Y方向のずれ: {abs((bbox23['min_y'] + bbox23['max_y']) / 2 - (bbox21['min_y'] + bbox21['max_y']) / 2):.2f}px")
    print()
    print(f"Nの幅: {bbox21['width']:.2f}px")
    print(f"Iの幅: {bbox23['width']:.2f}px")
    print(f"平均幅: {(bbox21['width'] + bbox23['width']) / 2:.2f}px")
    print()
    print(f"gap_norm = gap_actual / avg_width = {(bbox23['min_x'] - bbox21['max_x']):.3f} / {(bbox21['width'] + bbox23['width']) / 2:.2f} = {(bbox23['min_x'] - bbox21['max_x']) / ((bbox21['width'] + bbox23['width']) / 2):.4f}")

