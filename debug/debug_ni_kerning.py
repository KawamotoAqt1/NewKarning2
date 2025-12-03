#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N|I のカーニング計算をデバッグ
"""

import json

# 学習データを読み込み
with open('output_json/train/06099095_01_NAKATANI.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

# モデルを読み込み
with open('assets/phase1_model.json', 'r', encoding='utf-8') as f:
    model = json.load(f)

print('=' * 70)
print('N|I のカーニング計算デバッグ')
print('=' * 70)
print()

# 学習データからN|Iの情報を取得
ni_pair = next(p for p in train_data['pairs'] if p['left'] == 'N' and p['right'] == 'I')
ni_left_bbox = train_data['bbox'][ni_pair['left_id']]
ni_right_bbox = train_data['bbox'][ni_pair['right_id']]

print('1. 学習データ（SVGから取得）:')
print(f'   gap_actual: {ni_pair["gap_actual"]:.3f}px')
print(f'   左文字 (N): 幅={ni_left_bbox["width"]:.2f}px')
print(f'   右文字 (I): 幅={ni_right_bbox["width"]:.2f}px')
avg_width_train = (ni_left_bbox["width"] + ni_right_bbox["width"]) / 2
print(f'   平均文字幅: {avg_width_train:.2f}px')
gap_norm_train = ni_pair["gap_actual"] / avg_width_train
print(f'   gap_norm (学習時): {gap_norm_train:.4f}')
print()

# モデルの値を取得
model_ni = model.get("Mincho", {}).get("N|I")
if model_ni:
    print('2. モデルの値（phase1_model.json）:')
    print(f'   gap_norm_avg: {model_ni.get("gap_norm_avg", "N/A")}')
    print(f'   gap_norm_left_avg: {model_ni.get("gap_norm_left_avg", "N/A")}')
    print(f'   gap_norm_right_avg: {model_ni.get("gap_norm_right_avg", "N/A")}')
    print(f'   gap_actual_avg: {model_ni.get("gap_actual_avg", "N/A")}')
    print(f'   count: {model_ni.get("count", "N/A")}')
    print()
    
    # カーニング計算時のシミュレーション
    print('3. カーニング計算時のシミュレーション:')
    print('   （フォントサイズ64px、実際の文字幅をCanvasで測定したと仮定）')
    print()
    
    # 仮の文字幅（実際のCanvas測定値に近い値）
    # フォントサイズ64pxの場合、NとIの実際の幅は異なる可能性がある
    font_size = 64
    
    # 仮定: フォントサイズに対する文字幅の比率は学習時と同じ
    n_width_ratio = ni_left_bbox["width"] / 36.72  # 学習時のNの幅を基準
    i_width_ratio = ni_right_bbox["width"] / 17.08  # 学習時のIの幅を基準
    
    # フォントサイズ64pxでの仮定幅
    n_width_64 = font_size * n_width_ratio
    i_width_64 = font_size * i_width_ratio
    avg_width_64 = (n_width_64 + i_width_64) / 2
    
    print(f'   フォントサイズ: {font_size}px')
    print(f'   仮定のNの幅: {n_width_64:.2f}px')
    print(f'   仮定のIの幅: {i_width_64:.2f}px')
    print(f'   仮定の平均文字幅: {avg_width_64:.2f}px')
    print()
    
    # gap_norm_avgを使用した場合
    gap_norm_avg = model_ni.get("gap_norm_avg")
    if gap_norm_avg:
        gap_px_using_avg = gap_norm_avg * avg_width_64
        print(f'   モデルのgap_norm_avg ({gap_norm_avg:.4f}) を使用:')
        print(f'   gapPx = {gap_norm_avg:.4f} × {avg_width_64:.2f} = {gap_px_using_avg:.2f}px')
        print(f'   学習時のgap_actual: {ni_pair["gap_actual"]:.3f}px')
        print(f'   差: {gap_px_using_avg - ni_pair["gap_actual"]:.3f}px')
    else:
        # 旧方式（左右の平均）
        gap_norm_left = model_ni.get("gap_norm_left_avg", 0)
        gap_norm_right = model_ni.get("gap_norm_right_avg", 0)
        gap_norm_old = (gap_norm_left + gap_norm_right) / 2
        gap_px_using_old = gap_norm_old * avg_width_64
        print(f'   モデルのgap_norm_avgがないため、旧方式を使用:')
        print(f'   gap_norm_left_avg: {gap_norm_left:.4f}')
        print(f'   gap_norm_right_avg: {gap_norm_right:.4f}')
        print(f'   gap_norm平均: {gap_norm_old:.4f}')
        print(f'   gapPx = {gap_norm_old:.4f} × {avg_width_64:.2f} = {gap_px_using_old:.2f}px')
        print(f'   学習時のgap_actual: {ni_pair["gap_actual"]:.3f}px')
        print(f'   差: {gap_px_using_old - ni_pair["gap_actual"]:.3f}px')
    print()

print('4. 問題の可能性:')
print('   - 学習時のフォントサイズとカーニング計算時のフォントサイズが異なる')
print('   - 文字幅の計算方法が異なる（SVGのbbox vs CanvasのmeasureText）')
print('   - フォント名が正しく認識されていない（フォールバックフォントが使われている）')
print()

