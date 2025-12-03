"""
学習用JSON出力モジュール
処理結果を学習用JSON形式で出力する
"""

import json
import os
from typing import Dict, List, Optional


def export_to_json(
    output_path: str,
    file_id: str,
    font: Optional[str],
    sequence: List[Dict[str, str]],
    pairs: List[Dict[str, any]],
    bbox: Dict[str, Dict[str, float]]
) -> bool:
    """
    学習用JSONファイルを出力
    
    Args:
        output_path: 出力先のJSONファイルパス
        file_id: ファイルID（例: "13097882"）
        font: フォント名（例: "Mincho"）
        sequence: シーケンス情報 [{"id": str, "text": str}, ...]
        pairs: ペア情報 [{"left_id": str, "left": str, "right_id": str, "right": str, "gap_actual": float}, ...]
        bbox: bounding box情報 {"id": {"min_x": float, ...}, ...}
    
    Returns:
        成功した場合True、失敗した場合False
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # JSONデータを構築
        json_data = {
            "file": file_id,
            "font": font or "Unknown",
            "sequence": sequence,
            "pairs": pairs,
            "bbox": bbox
        }
        
        # JSONファイルに書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error exporting JSON to {output_path}: {e}")
        return False

