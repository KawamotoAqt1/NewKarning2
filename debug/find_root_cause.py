#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根本原因を特定するスクリプト
"""

import json

# 学習データを読み込み
with open('output_json/train/06099095_01_NAKATANI.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

bbox = data['bbox']
pairs = data['pairs']

# N|Iペアの詳細
ni_pair = next(p for p in pairs if p['left'] == 'N' and p['right'] == 'I')
n_bbox = bbox[ni_pair['left_id']]
i_bbox = bbox[ni_pair['right_id']]

print('=' * 70)
print('根本原因の分析')
print('=' * 70)
print()

print('1. 学習データ（SVG）の座標:')
print(f'   N (path21): min_x={n_bbox["min_x"]:.2f}, max_x={n_bbox["max_x"]:.2f}, width={n_bbox["width"]:.2f}')
print(f'   I (path23): min_x={i_bbox["min_x"]:.2f}, max_x={i_bbox["max_x"]:.2f}, width={i_bbox["width"]:.2f}')
print(f'   gap_actual = I.min_x - N.max_x = {i_bbox["min_x"]:.2f} - {n_bbox["max_x"]:.2f} = {ni_pair["gap_actual"]:.3f}px')
print()

print('2. 重要な理解:')
print('   gap_actualは「右側の文字の左端（I.min_x）から左側の文字の右端（N.max_x）までの距離」')
print('   これは、実際の文字間の「空白」の距離を表している')
print()

print('3. Canvas APIでの描画:')
print('   - fillText(x, y)は、x座標を文字のベースラインの左端として描画')
print('   - measureText().widthは文字の実際の描画幅')
print('   - しかし、SVGのbbox.widthは文字の境界ボックス全体を含む')
print()

print('4. 問題の核心:')
print('   SVGのbbox.width ≠ Canvas APIのmeasureText().width')
print('   この差が、gap_actualをそのまま使っても間隔が合わない原因')
print()

# A|Nペアと比較
an_pair = next(p for p in pairs if p['left'] == 'A' and p['right'] == 'N')
a_bbox = bbox[an_pair['left_id']]
an_n_bbox = bbox[an_pair['right_id']]

print('5. A|Nペアとの比較:')
print(f'   A: min_x={a_bbox["min_x"]:.2f}, max_x={a_bbox["max_x"]:.2f}, width={a_bbox["width"]:.2f}')
print(f'   N: min_x={an_n_bbox["min_x"]:.2f}, max_x={an_n_bbox["max_x"]:.2f}, width={an_n_bbox["width"]:.2f}')
print(f'   gap_actual = {an_pair["gap_actual"]:.3f}px')
print()

print('6. 実際の比率を計算:')
print('   学習データ（SVG bbox）:')
print(f'     N: {n_bbox["width"]:.2f}px, I: {i_bbox["width"]:.2f}px')
print('   Canvas API（フォントサイズ45pxで測定、コンソール出力より）:')
print('     N: 約31px, I: 約15px')
print()
print('   比率:')
n_ratio = 31 / n_bbox["width"]
i_ratio = 15 / i_bbox["width"]
print(f'     N: 31 / {n_bbox["width"]:.2f} = {n_ratio:.3f}')
print(f'     I: 15 / {i_bbox["width"]:.2f} = {i_ratio:.3f}')
print(f'     平均: {(n_ratio + i_ratio) / 2:.3f}')
print()

print('7. 解決策:')
print('   gap_actualをそのまま使うのではなく、')
print('   Canvas APIで測定した文字幅とSVGのbboxの文字幅の比率を考慮する')
print('   または、gap_normを使用して、現在の文字幅でスケールする')
print()

print('8. しかし、gap_normも問題がある:')
print('   gap_norm = gap_actual / avg_width')
print('   学習データでは avg_width = (36.72 + 17.08) / 2 = 26.90px')
print(f'   gap_norm = {ni_pair["gap_actual"]:.3f} / 26.90 = {ni_pair["gap_actual"] / 26.90:.4f}')
print('   しかし、Canvas APIでは avg_width = (31 + 15) / 2 = 23px')
print(f'   gapPx = {ni_pair["gap_actual"] / 26.90:.4f} * 23 = {(ni_pair["gap_actual"] / 26.90) * 23:.3f}px')
print(f'   これは学習時のgap_actual ({ni_pair["gap_actual"]:.3f}px)より小さい')
print()

print('9. 本当の原因:')
print('   gap_normを使用すると、文字幅が小さいため、gapPxも小さくなる')
print('   しかし、ユーザーは「まだ広い」と言っている')
print('   これは、gap_normの計算方法に問題があるか、')
print('   または、Canvas APIで測定される文字幅が実際の描画幅と異なる可能性がある')
print()

