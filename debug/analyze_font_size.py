#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学習データのフォントサイズを推定
"""

import json

# 学習データを読み込み
with open('output_json/train/06099095_01_NAKATANI.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

bbox = data['bbox']
sequence = data['sequence']

print('=' * 70)
print('学習データのフォントサイズ推定')
print('=' * 70)
print()

# 各文字の幅と高さを表示
print('文字ごとのサイズ:')
for seq in sequence:
    char_id = seq['id']
    char = seq['text']
    if char_id in bbox:
        b = bbox[char_id]
        print(f'  {char}: 幅={b["width"]:.2f}px, 高さ={b["height"]:.2f}px')

print()

# 平均的な文字幅と高さを計算
all_widths = [b['width'] for b in bbox.values()]
all_heights = [b['height'] for b in bbox.values()]

avg_width = sum(all_widths) / len(all_widths)
avg_height = sum(all_heights) / len(all_heights)

print(f'平均文字幅: {avg_width:.2f}px')
print(f'平均文字高さ: {avg_height:.2f}px')
print()

# フォントサイズの推定
# 一般的に、文字の高さはフォントサイズの0.8-1.0倍程度
# また、文字幅はフォントサイズの0.5-0.8倍程度（文字によって異なる）
print('フォントサイズの推定:')
print(f'  高さから推定: {avg_height / 0.8:.1f}px ～ {avg_height / 0.9:.1f}px')
print(f'  幅から推定（参考）: {avg_width / 0.6:.1f}px ～ {avg_width / 0.7:.1f}px')
print()

# N|Iペアの詳細
ni_pair = next(p for p in data['pairs'] if p['left'] == 'N' and p['right'] == 'I')
ni_left_bbox = bbox[ni_pair['left_id']]
ni_right_bbox = bbox[ni_pair['right_id']]

print('N|Iペアの詳細:')
print(f'  N: 幅={ni_left_bbox["width"]:.2f}px, 高さ={ni_left_bbox["height"]:.2f}px')
print(f'  I: 幅={ni_right_bbox["width"]:.2f}px, 高さ={ni_right_bbox["height"]:.2f}px')
print(f'  gap_actual: {ni_pair["gap_actual"]:.3f}px')
avg_width_ni = (ni_left_bbox["width"] + ni_right_bbox["width"]) / 2
print(f'  平均文字幅: {avg_width_ni:.2f}px')
print()

# カーニング計算時の問題
print('=' * 70)
print('問題の分析:')
print('=' * 70)
print()

print('学習時（SVG）:')
print(f'  平均文字幅: {avg_width_ni:.2f}px')
print(f'  gap_actual: {ni_pair["gap_actual"]:.3f}px')
print(f'  gap_norm: {ni_pair["gap_actual"] / avg_width_ni:.4f}')
print()

print('カーニング計算時（フォントサイズ64pxを想定）:')
# Canvasで測定した場合の文字幅を推定
# 一般的に、フォントサイズ64pxの場合、Nは約40-50px、Iは約10-15px程度
font_size_64 = 64
n_width_64_est = 45  # 推定値
i_width_64_est = 12  # 推定値
avg_width_64_est = (n_width_64_est + i_width_64_est) / 2
gap_norm = ni_pair["gap_actual"] / avg_width_ni
gap_px_64 = gap_norm * avg_width_64_est

print(f'  推定のNの幅: {n_width_64_est}px')
print(f'  推定のIの幅: {i_width_64_est}px')
print(f'  推定の平均文字幅: {avg_width_64_est:.2f}px')
print(f'  gap_norm: {gap_norm:.4f}')
print(f'  gapPx = {gap_norm:.4f} × {avg_width_64_est:.2f} = {gap_px_64:.2f}px')
print(f'  学習時のgap_actual: {ni_pair["gap_actual"]:.3f}px')
print(f'  差: {gap_px_64 - ni_pair["gap_actual"]:.2f}px（約{((gap_px_64 / ni_pair["gap_actual"]) - 1) * 100:.1f}%大きい）')
print()

print('原因:')
print('  学習時のフォントサイズとカーニング計算時のフォントサイズが異なる')
print('  同じgap_normでも、文字幅が大きくなるとgapPxも大きくなる')
print()

