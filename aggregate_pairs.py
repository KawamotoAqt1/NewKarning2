"""
Phase1学習用 文字ペア集計スクリプト

複数のPhase1 JSONファイルを読み込み、文字ペアごとに1行のレコードに変換して
CSVファイルとして出力します。

使い方:
    python aggregate_pairs.py

設定:
    JSON_DIR: JSONファイルが格納されているフォルダ（デフォルト: "./output_json/train"）
    OUTPUT_CSV: 出力先のCSVファイル（デフォルト: "./pairs_aggregated.csv"）

出力:
    pairs_aggregated.csv - すべての文字ペアを集計したCSVファイル
"""

import json
import os
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional


# 設定
JSON_DIR = "./output_json/train"  # JSONファイルが格納されているフォルダ
OUTPUT_CSV = "./pairs_aggregated.csv"  # 出力先のCSVファイル


def load_json_files(json_dir: str) -> List[Dict[str, Any]]:
    """
    JSON_DIR以下のすべてのJSONファイルを読み込む
    
    Args:
        json_dir: JSONファイルが格納されているディレクトリ
    
    Returns:
        JSONデータのリスト
    """
    json_path = Path(json_dir)
    if not json_path.exists():
        print(f"Error: Directory '{json_dir}' does not exist")
        return []
    
    json_files = list(json_path.glob("*.json"))
    if not json_files:
        print(f"Warning: No JSON files found in '{json_dir}'")
        return []
    
    json_data_list = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ファイル名からsample_idを取得（fileフィールドがない場合）
                if 'file' not in data:
                    data['file'] = json_file.stem
                json_data_list.append(data)
        except Exception as e:
            print(f"Warning: Failed to load {json_file.name}: {e}")
    
    return json_data_list


def get_bbox_info(bbox_dict: Dict[str, Dict[str, float]], path_id: str, prefix: str) -> Dict[str, Optional[float]]:
    """
    bbox辞書から指定されたpath_idの情報を取得
    
    Args:
        bbox_dict: bbox情報の辞書
        path_id: 取得するpathのID
        prefix: カラム名のプレフィックス（例: "left", "right"）
    
    Returns:
        bbox情報の辞書（見つからない場合はNoneで埋める）
    """
    if path_id not in bbox_dict:
        return {
            f"{prefix}_width": None,
            f"{prefix}_height": None,
            f"{prefix}_min_x": None,
            f"{prefix}_max_x": None,
            f"{prefix}_min_y": None,
            f"{prefix}_max_y": None,
        }
    
    bbox = bbox_dict[path_id]
    return {
        f"{prefix}_width": bbox.get("width"),
        f"{prefix}_height": bbox.get("height"),
        f"{prefix}_min_x": bbox.get("min_x"),
        f"{prefix}_max_x": bbox.get("max_x"),
        f"{prefix}_min_y": bbox.get("min_y"),
        f"{prefix}_max_y": bbox.get("max_y"),
    }


def find_index_in_sequence(sequence: List[Dict[str, str]], path_id: str) -> Optional[int]:
    """
    sequence内で指定されたpath_idのインデックスを取得
    
    Args:
        sequence: sequence情報のリスト
        path_id: 検索するpathのID
    
    Returns:
        インデックス（見つからない場合はNone）
    """
    if not sequence:
        return None
    
    for i, item in enumerate(sequence):
        if item.get("id") == path_id:
            return i
    
    return None


def create_pair_key(left_char: str, right_char: str, left_font: str, right_font: str) -> str:
    """
    ペアのキー文字列を生成
    
    Args:
        left_char: 左側の文字
        right_char: 右側の文字
        left_font: 左側のフォント
        right_font: 右側のフォント
    
    Returns:
        ペアキー文字列（例: "N|A|Mincho" または "N|A|Mincho-Gothic"）
    """
    if left_font == right_font:
        return f"{left_char}|{right_char}|{left_font}"
    else:
        return f"{left_char}|{right_char}|{left_font}-{right_font}"


def calculate_total_width(sequence: List[Dict[str, str]], bbox: Dict[str, Dict[str, float]]) -> Optional[float]:
    """
    文字列全体の幅を計算（最初の文字のmin_xから最後の文字のmax_xまで）
    
    Args:
        sequence: sequence情報のリスト
        bbox: bbox情報の辞書
    
    Returns:
        文字列全体の幅（計算できない場合はNone）
    """
    if not sequence or not bbox:
        return None
    
    # sequenceの順序で最初と最後の文字を取得
    first_id = sequence[0].get("id")
    last_id = sequence[-1].get("id")
    
    if first_id is None or last_id is None:
        return None
    
    if first_id not in bbox or last_id not in bbox:
        return None
    
    first_min_x = bbox[first_id].get("min_x")
    last_max_x = bbox[last_id].get("max_x")
    
    if first_min_x is None or last_max_x is None:
        return None
    
    return last_max_x - first_min_x


def aggregate_pairs(json_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    JSONデータから文字ペアのレコードを生成
    
    Args:
        json_data_list: JSONデータのリスト
    
    Returns:
        文字ペアレコードのリスト
    """
    records = []
    
    for json_data in json_data_list:
        sample_id = json_data.get("file", "unknown")
        pairs = json_data.get("pairs", [])
        bbox = json_data.get("bbox", {})
        sequence = json_data.get("sequence", [])
        
        # pairsが存在しない or 空配列の場合はスキップ
        if not pairs:
            continue
        
        # フォント情報を取得（トップレベルのfontフィールド、またはsequenceから）
        default_font = json_data.get("font", "")
        
        # sequenceから各文字のfont情報を取得（あれば）
        sequence_font_map = {}
        for seq_item in sequence:
            seq_id = seq_item.get("id")
            seq_font = seq_item.get("font", default_font)
            if seq_id:
                sequence_font_map[seq_id] = seq_font
        
        # 文字列全体の幅を計算（サンプルごとに1回だけ計算）
        text_total_width = calculate_total_width(sequence, bbox)
        text_length = len(sequence) if sequence else None
        
        for pair in pairs:
            left_id = pair.get("left_id")
            right_id = pair.get("right_id")
            left_char = pair.get("left", "")
            right_char = pair.get("right", "")
            
            # フォント情報を取得（pairs内、sequence内、またはデフォルト）
            left_font = pair.get("left_font") or sequence_font_map.get(left_id, default_font)
            right_font = pair.get("right_font") or sequence_font_map.get(right_id, default_font)
            
            gap_actual = pair.get("gap_actual")
            
            # bboxにleft_id/right_idが見つからない場合はスキップ
            if left_id not in bbox:
                print(f"Warning: left_id '{left_id}' not found in bbox for sample '{sample_id}', skipping pair")
                continue
            if right_id not in bbox:
                print(f"Warning: right_id '{right_id}' not found in bbox for sample '{sample_id}', skipping pair")
                continue
            
            # 基本情報
            record = {
                "sample_id": sample_id,
                "left_char": left_char,
                "right_char": right_char,
                "left_font": left_font,
                "right_font": right_font,
                "gap_actual": gap_actual,
            }
            
            # bbox情報を追加
            left_bbox = get_bbox_info(bbox, left_id, "left")
            right_bbox = get_bbox_info(bbox, right_id, "right")
            record.update(left_bbox)
            record.update(right_bbox)
            
            # sequence情報を追加
            left_index = find_index_in_sequence(sequence, left_id)
            right_index = find_index_in_sequence(sequence, right_id)
            record["left_index"] = left_index if left_index is not None else -1
            record["right_index"] = right_index if right_index is not None else -1
            
            # 派生カラムを計算
            left_width = record.get("left_width")
            right_width = record.get("right_width")
            left_height = record.get("left_height")
            right_height = record.get("right_height")
            
            if left_width is not None and right_width is not None:
                record["avg_width"] = (left_width + right_width) / 2
            else:
                record["avg_width"] = None
            
            # フォントサイズを推定（文字の高さから推定、一般的に高さはフォントサイズの0.85倍程度）
            if left_height is not None and right_height is not None:
                avg_height = (left_height + right_height) / 2
                # フォントサイズ = 高さ / 0.85（一般的な比率）
                record["font_size_est"] = avg_height / 0.85
            else:
                record["font_size_est"] = None
            
            # 平均文字幅で正規化（カーニング計算時のbaseWidthPxと一致させる）
            if record.get("avg_width") is not None and record["avg_width"] != 0:
                record["gap_norm"] = gap_actual / record["avg_width"] if gap_actual is not None else None
            else:
                record["gap_norm"] = None
            
            # 後方互換性のため、左右の正規化値も保持（非推奨）
            if left_width is not None and left_width != 0:
                record["gap_norm_left"] = gap_actual / left_width if gap_actual is not None else None
            else:
                record["gap_norm_left"] = None
            
            if right_width is not None and right_width != 0:
                record["gap_norm_right"] = gap_actual / right_width if gap_actual is not None else None
            else:
                record["gap_norm_right"] = None
            
            # pair_keyを生成
            record["pair_key"] = create_pair_key(left_char, right_char, left_font, right_font)
            
            # 文字列全体の幅と文字列長を追加（サンプルごとに同じ値）
            record["text_total_width"] = text_total_width
            record["text_length"] = text_length
            
            records.append(record)
    
    return records


def write_csv(records: List[Dict[str, Any]], output_path: str):
    """
    レコードをCSVファイルに書き出す
    
    Args:
        records: レコードのリスト
        output_path: 出力先のCSVファイルパス
    """
    if not records:
        print("Warning: No records to write")
        return
    
    # カラム順を定義
    columns = [
        "sample_id",
        "left_char",
        "right_char",
        "left_font",
        "right_font",
        "gap_actual",
        "left_width",
        "right_width",
        "left_height",
        "right_height",
        "left_min_x",
        "left_max_x",
        "left_min_y",
        "left_max_y",
        "right_min_x",
        "right_max_x",
        "right_min_y",
        "right_max_y",
        "left_index",
        "right_index",
        "avg_width",
        "font_size_est",  # 推定フォントサイズ（重みとして使用）
        "gap_norm",  # 平均文字幅で正規化（推奨）
        "gap_norm_left",  # 後方互換性のため保持
        "gap_norm_right",  # 後方互換性のため保持
        "text_total_width",  # 文字列全体の幅（重みとして使用）
        "text_length",  # 文字列長（参考）
        "pair_key",
    ]
    
    # 出力ディレクトリが存在しない場合は作成
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # CSVファイルに書き出し
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Successfully wrote {len(records)} records to {output_path}")


def main():
    """メイン処理"""
    print("=" * 60)
    print("Phase1 文字ペア集計スクリプト")
    print("=" * 60)
    print(f"JSON directory: {JSON_DIR}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print("-" * 60)
    
    # JSONファイルを読み込む
    json_data_list = load_json_files(JSON_DIR)
    
    if not json_data_list:
        print("No JSON data loaded. Exiting.")
        return
    
    print(f"Loaded {len(json_data_list)} JSON files")
    
    # 文字ペアのレコードを生成
    records = aggregate_pairs(json_data_list)
    
    if not records:
        print("No pairs found. Exiting.")
        return
    
    print(f"Generated {len(records)} pair records")
    
    # CSVファイルに書き出し
    write_csv(records, OUTPUT_CSV)
    
    print("-" * 60)
    print("Processing completed!")


if __name__ == "__main__":
    main()

