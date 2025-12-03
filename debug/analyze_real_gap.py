#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際のgap_actualとCanvas描画でのgapの関係を分析
"""

import json

# 学習データを読み込み
with open('output_json/train/06099095_01_NAKATANI.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

bbox = data['bbox']
pairs = data['pairs']

# N|Iペアの詳細
ni_pair = next(p for p in pairs if p['left'] == 'N' and p['right'] == 'I'])
n_bbox = bbox[ni_pair['left_id']]
i_bbox = bbox[ni_pair['right_id']]

print('=' * 70)
print('N|I ペアの実際のgap分析')
print('=' * 70)
print()

print('学習データ（SVG）:')
print(f'  N: min_x={n_bbox["min_x"]:.2f}, max_x={n_bbox["max_x"]:.2f}, width={n_bbox["width"]:.2f}')
print(f'  I: min_x={i_bbox["min_x"]:.2f}, max_x={i_bbox["max_x"]:.2f}, width={i_bbox["width"]:.2f}')
print(f'  gap_actual = I.min_x - N.max_x = {i_bbox["min_x"]:.2f} - {n_bbox["max_x"]:.2f} = {ni_pair["gap_actual"]:.3f}px')
print()

print('重要な点:')
print('  gap_actualは「右側の文字の左端（I.min_x）から左側の文字の右端（N.max_x）までの距離」')
print('  これは、実際の文字間の「空白」の距離を表している')
print()

# A|Nペアと比較
an_pair = next(p for p in pairs if p['left'] == 'A' and p['right'] == 'N')
a_bbox = bbox[an_pair['left_id']]
an_n_bbox = bbox[an_pair['right_id']]

print('A|N ペアとの比較:')
print(f'  A: min_x={a_bbox["min_x"]:.2f}, max_x={a_bbox["max_x"]:.2f}, width={a_bbox["width"]:.2f}')
print(f'  N: min_x={an_n_bbox["min_x"]:.2f}, max_x={an_n_bbox["max_x"]:.2f}, width={an_n_bbox["width"]:.2f}')
print(f'  gap_actual = N.min_x - A.max_x = {an_n_bbox["min_x"]:.2f} - {a_bbox["max_x"]:.2f} = {an_pair["gap_actual"]:.3f}px')
print()

print('問題の分析:')
print('=' * 70)
print('Canvas APIで描画する際:')
print('  - fillTextは文字のベースラインの左端から描画を開始')
print('  - measureTextで測定されるwidthは文字の実際の描画幅')
print('  - しかし、SVGのbboxのwidthは文字の境界ボックス全体を含む')
print()
print('つまり:')
print('  - SVGのbbox.width ≠ Canvas APIのmeasureText.width')
print('  - この差が、gap_actualをそのまま使っても間隔が合わない原因')
print()
print('解決策:')
print('  gap_actualをそのまま使うのではなく、')
print('  Canvas APIで測定した文字幅とSVGのbboxの文字幅の比率を考慮する必要がある')
print()

# 実際の比率を計算
# 学習データでは、Nの幅は36.72px、Iの幅は17.08px
# しかし、Canvas APIで測定すると、フォントサイズ45pxでNは約31px、Iは約15px
# この比率を計算

print('文字幅の比率（推定）:')
print('  SVG bbox - N: 36.72px')
print('  Canvas API（45px）- N: 約31px（推定）')
print('  比率: 31 / 36.72 = 0.844')
print()
print('  SVG bbox - I: 17.08px')
print('  Canvas API（45px）- I: 約15px（推定）')
print('  比率: 15 / 17.08 = 0.878')
print()
print('この比率を考慮すると:')
print('  gap_actual = 8.615px')
print('  補正後のgap = 8.615px * (平均比率)')
print('  平均比率 ≈ 0.86')
print('  補正後のgap ≈ 8.615 * 0.86 = 7.41px')
print()
print('しかし、これは推測です。実際のCanvas APIで測定した値を確認する必要があります。')

