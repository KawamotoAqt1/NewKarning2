#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase1 カーニングモデル生成スクリプト

このスクリプトは、pairs_aggregated.csv から Phase1 デモ用の学習済みペアモデルJSONを生成します。

使い方：
1. このスクリプトと同じディレクトリに pairs_aggregated.csv を置く
2. ターミナルで python build_phase1_model.py を実行
3. 同じディレクトリに phase1_model.json が生成される
4. フロントエンドのデモからこの JSON を読み込んで Phase1カーニングに利用する

出力される JSON の構造：
{
  "Gothic": {
    "K|A": {
      "gap_norm_left_avg": 0.30,
      "gap_norm_right_avg": 0.28,
      "gap_actual_avg": 9.33,
      "count": 5
    },
    ...
  },
  "Mincho": { ... },
  ...
}
"""

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Optional

# ============================================
# 設定定数
# ============================================

CSV_PATH = "pairs_aggregated.csv"
OUTPUT_JSON_PATH = "phase1_model.json"

# 異常値フィルタ設定
MIN_GAPNORM = -1.0  # これ未満の gap_norm は除外（重なりすぎ）
MAX_GAPNORM = 1.0   # これより大きい gap_norm は除外（広げすぎ）
MIN_COUNT = 1       # 集計結果出力時、ペアごとの最小採用件数

# 有効なフォントカテゴリ（念のため検証用）
VALID_FONT_CATEGORIES = {"Gothic", "Mincho", "MaruGothic", "Brush", "Design"}


# ============================================
# 補助関数
# ============================================

def parse_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """
    値をfloatに変換。変換できない場合はdefaultを返す。
    """
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def is_valid_gap_norm(value: Optional[float]) -> bool:
    """
    gap_norm値が有効範囲内かチェック
    """
    if value is None:
        return False
    return MIN_GAPNORM <= value <= MAX_GAPNORM


def should_skip_row(row: Dict[str, str]) -> tuple[bool, str]:
    """
    行をスキップすべきかどうかを判定。
    戻り値: (skip: bool, reason: str)
    """
    # left_font が空または欠損
    left_font = row.get("left_font", "").strip()
    if not left_font:
        return True, "left_font is empty"
    
    # left_char, right_char が空または欠損
    left_char = row.get("left_char", "").strip()
    right_char = row.get("right_char", "").strip()
    if not left_char or not right_char:
        return True, "left_char or right_char is empty"
    
    # gap_norm（平均文字幅で正規化）を優先的に取得
    gap_norm = parse_float(row.get("gap_norm"))
    
    # gap_normがない場合は後方互換性のためgap_norm_left/gap_norm_rightをチェック
    if gap_norm is None:
        gap_norm_left = parse_float(row.get("gap_norm_left"))
        gap_norm_right = parse_float(row.get("gap_norm_right"))
        
        # 数値に変換できない場合はスキップ
        if gap_norm_left is None or gap_norm_right is None:
            return True, "gap_norm (or gap_norm_left/gap_norm_right) is not a valid number"
        
        # 異常値チェック
        if not is_valid_gap_norm(gap_norm_left):
            return True, f"gap_norm_left ({gap_norm_left}) is out of range"
        
        if not is_valid_gap_norm(gap_norm_right):
            return True, f"gap_norm_right ({gap_norm_right}) is out of range"
    else:
        # gap_normがある場合はそれをチェック
        if not is_valid_gap_norm(gap_norm):
            return True, f"gap_norm ({gap_norm}) is out of range"
    
    return False, ""


# ============================================
# メイン処理
# ============================================

def build_phase1_model(csv_path: str, output_json_path: str) -> Dict[str, Any]:
    """
    CSVからPhase1モデルJSONを生成する
    
    Args:
        csv_path: 入力CSVファイルのパス
        output_json_path: 出力JSONファイルのパス
    
    Returns:
        生成されたモデル辞書
    """
    # 集計用のデータ構造
    # stats[font_key][pair_key] = {
    #     "sum_gap_norm": float,  # 平均文字幅で正規化した値
    #     "sum_gap_norm_left": float,  # 後方互換性のため保持
    #     "sum_gap_norm_right": float,  # 後方互換性のため保持
    #     "sum_gap_actual": float,
    #     "sum_font_size_est": float,  # 推定フォントサイズの合計（案1用）
    #     "count": int
    # }
    stats: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
        lambda: defaultdict(lambda: {
            "sum_gap_norm": 0.0,
            "sum_gap_norm_left": 0.0,
            "sum_gap_norm_right": 0.0,
            "sum_gap_actual": 0.0,
            "sum_font_size_est": 0.0,
            "count": 0
        })
    )
    
    # CSV読み込み
    csv_file_path = Path(csv_path)
    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")
    
    print(f"CSVファイルを読み込み中: {csv_path}")
    
    skipped_count = 0
    processed_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # ヘッダー行を除いて2行目から
            # スキップ判定
            skip, reason = should_skip_row(row)
            if skip:
                skipped_count += 1
                if skipped_count <= 10:  # 最初の10件だけ警告を表示
                    print(f"  警告: 行 {row_num} をスキップしました: {reason}")
                continue
            
            # データを取得
            font_key = row["left_font"].strip()
            left_char = row["left_char"].strip()
            right_char = row["right_char"].strip()
            pair_key = f"{left_char}|{right_char}"
            
            gap_norm = parse_float(row.get("gap_norm"))  # 平均文字幅で正規化した値（推奨）
            gap_norm_left = parse_float(row.get("gap_norm_left"))  # 後方互換性のため
            gap_norm_right = parse_float(row.get("gap_norm_right"))  # 後方互換性のため
            gap_actual = parse_float(row.get("gap_actual"), 0.0)
            font_size_est = parse_float(row.get("font_size_est"))  # 推定フォントサイズ（案1用）
            
            # 集計に追加
            if gap_norm is not None:
                stats[font_key][pair_key]["sum_gap_norm"] += gap_norm
            if gap_norm_left is not None:
                stats[font_key][pair_key]["sum_gap_norm_left"] += gap_norm_left
            if gap_norm_right is not None:
                stats[font_key][pair_key]["sum_gap_norm_right"] += gap_norm_right
            stats[font_key][pair_key]["sum_gap_actual"] += gap_actual
            if font_size_est is not None:
                stats[font_key][pair_key]["sum_font_size_est"] += font_size_est
            stats[font_key][pair_key]["count"] += 1
            
            processed_count += 1
    
    print(f"処理完了: {processed_count} 件のレコードを処理しました")
    if skipped_count > 10:
        print(f"  （その他 {skipped_count - 10} 件のレコードをスキップしました）")
    elif skipped_count > 0:
        print(f"  （{skipped_count} 件のレコードをスキップしました）")
    
    # 最終的なJSON形式を組み立て
    result: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    for font_key, pairs_dict in stats.items():
        result[font_key] = {}
        
        for pair_key, data in pairs_dict.items():
            count = data["count"]
            
            # MIN_COUNT より小さい場合はスキップ
            if count < MIN_COUNT:
                continue
            
            # 平均を計算
            gap_norm_avg = data["sum_gap_norm"] / count if data["sum_gap_norm"] > 0 else None
            gap_norm_left_avg = data["sum_gap_norm_left"] / count if data["sum_gap_norm_left"] > 0 else None
            gap_norm_right_avg = data["sum_gap_norm_right"] / count if data["sum_gap_norm_right"] > 0 else None
            gap_actual_avg = data["sum_gap_actual"] / count
            font_size_avg = data["sum_font_size_est"] / count if data["sum_font_size_est"] > 0 else None
            
            result[font_key][pair_key] = {
                "gap_norm_avg": gap_norm_avg,  # 平均文字幅で正規化（推奨）
                "gap_norm_left_avg": gap_norm_left_avg,  # 後方互換性のため保持
                "gap_norm_right_avg": gap_norm_right_avg,  # 後方互換性のため保持
                "gap_actual_avg": gap_actual_avg,
                "font_size_avg": font_size_avg,  # 学習時の平均フォントサイズ（案1用）
                "count": count
            }
    
    # JSONファイルに書き出し
    output_path = Path(output_json_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Phase1モデルを生成しました: {output_json_path}")
    
    # 統計情報を表示
    total_pairs = sum(len(pairs) for pairs in result.values())
    print(f"\n生成されたモデルの統計:")
    for font_key, pairs_dict in sorted(result.items()):
        print(f"  {font_key}: {len(pairs_dict)} ペア")
    print(f"  合計: {total_pairs} ペア")
    
    return result


# ============================================
# メイン実行
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Phase1 カーニングモデル生成スクリプト")
    print("=" * 60)
    print(f"入力CSV: {CSV_PATH}")
    print(f"出力JSON: {OUTPUT_JSON_PATH}")
    print(f"フィルタ設定: MIN_GAPNORM={MIN_GAPNORM}, MAX_GAPNORM={MAX_GAPNORM}, MIN_COUNT={MIN_COUNT}")
    print("-" * 60)
    
    try:
        model = build_phase1_model(CSV_PATH, OUTPUT_JSON_PATH)
        print("\n✅ 処理が正常に完了しました")
    except FileNotFoundError as e:
        print(f"\n❌ エラー: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

