#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A|N と N|I のギャップを比較分析
"""

import json

# JSONファイルを読み込み
with open('output_json/train/06099095_01_NAKATANI.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pairs = data['pairs']
bbox = data['bbox']

print('=' * 70)
print('A|N と N|I のギャップ比較分析')
print('=' * 70)
print()

# A|N の情報
an_pair = next(p for p in pairs if p['left'] == 'A' and p['right'] == 'N')
an_left_bbox = bbox[an_pair['left_id']]
an_right_bbox = bbox[an_pair['right_id']]

# N|I の情報
ni_pair = next(p for p in pairs if p['left'] == 'N' and p['right'] == 'I')
ni_left_bbox = bbox[ni_pair['left_id']]
ni_right_bbox = bbox[ni_pair['right_id']]

print('1. A|N ペア:')
print(f'   gap_actual: {an_pair["gap_actual"]:.3f}px')
print(f'   左文字 (A): 幅={an_left_bbox["width"]:.2f}px')
print(f'   右文字 (N): 幅={an_right_bbox["width"]:.2f}px')
an_gap_norm_left = an_pair["gap_actual"] / an_left_bbox["width"]
an_gap_norm_right = an_pair["gap_actual"] / an_right_bbox["width"]
print(f'   gap_norm_left: {an_gap_norm_left:.4f}')
print(f'   gap_norm_right: {an_gap_norm_right:.4f}')
print(f'   gap_norm平均: {(an_gap_norm_left + an_gap_norm_right) / 2:.4f}')
print()

print('2. N|I ペア:')
print(f'   gap_actual: {ni_pair["gap_actual"]:.3f}px')
print(f'   左文字 (N): 幅={ni_left_bbox["width"]:.2f}px')
print(f'   右文字 (I): 幅={ni_right_bbox["width"]:.2f}px')
ni_gap_norm_left = ni_pair["gap_actual"] / ni_left_bbox["width"]
ni_gap_norm_right = ni_pair["gap_actual"] / ni_right_bbox["width"]
print(f'   gap_norm_left: {ni_gap_norm_left:.4f}')
print(f'   gap_norm_right: {ni_gap_norm_right:.4f}')
print(f'   gap_norm平均: {(ni_gap_norm_left + ni_gap_norm_right) / 2:.4f}')
print()

print('=' * 70)
print('問題の分析:')
print('=' * 70)
print()

print('3. モデルの値（phase1_model.json）:')
print('   A|N:')
print('     gap_norm_left_avg: 0.3003')
print('     gap_norm_right_avg: 0.2684')
print('     平均: 0.2844')
print()
print('   N|I:')
print('     gap_norm_left_avg: 0.2346')
print('     gap_norm_right_avg: 0.5043  ← 非常に大きい！')
print('     平均: 0.3695')
print()

print('4. 視覚的な問題の原因:')
print()
print('   N|I の gap_norm_right_avg が 0.5043 と非常に大きい理由:')
print(f'   - I の文字幅が {ni_right_bbox["width"]:.2f}px と非常に小さい')
print(f'   - gap_actual ({ni_pair["gap_actual"]:.3f}px) を I の幅で割ると')
print(f'     8.615 / {ni_right_bbox["width"]:.2f} = {ni_gap_norm_right:.4f}')
print()
print('   しかし、実際のカーニング計算では:')
print('   gapPx = gapNorm * baseWidthPx')
print('   ここで baseWidthPx は「平均的な文字幅」を使用')
print()
print('   問題: I は非常に細い文字なので、')
print('   - gap_norm_right が大きくなりやすい')
print('   - しかし実際のカーニングでは baseWidthPx（平均幅）を使うため、')
print('   - 視覚的には広く見える')
print()

print('5. 解決策の提案:')
print('   - gap_norm_right が異常に大きい場合（例: > 0.4）は、')
print('     左側の文字幅で正規化した値（gap_norm_left）を優先する')
print('   - または、両方の値の平均ではなく、より信頼性の高い方を選ぶ')
print()

