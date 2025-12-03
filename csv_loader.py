"""
CSV読み込みモジュール
UTF-8でエンコードされたCSVファイルを読み込む（Shift-JISにも対応）
"""

import csv
from typing import List, Dict
import sys


def load_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    UTF-8でエンコードされたCSVファイルを読み込む（UTF-8で失敗した場合はShift-JISを試す）
    
    Args:
        csv_path: CSVファイルのパス
    
    Returns:
        [{"id": str, "text": str, "font": str}, ...] のリスト
    """
    results = []
    
    # まずUTF-8で試す（学習用CSVはUTF-8）
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # id, text, font の3列を取得（name_text, name_orderはオプション）
                if 'id' in row and 'text' in row and 'font' in row:
                    csv_id = row['id'].strip()
                    # 空のidをスキップ
                    if not csv_id:
                        continue
                    result = {
                        "id": csv_id,
                        "text": row['text'].strip(),
                        "font": row['font'].strip()
                    }
                    # name_textとname_orderが存在する場合は追加
                    if 'name_text' in row:
                        result['name_text'] = row['name_text'].strip()
                    if 'name_order' in row:
                        result['name_order'] = row['name_order'].strip()
                    results.append(result)
            return results
    
    except UnicodeDecodeError:
        # UTF-8で失敗した場合、Shift-JISを試す（後方互換性のため）
        try:
            with open(csv_path, 'r', encoding='cp932') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if 'id' in row and 'text' in row and 'font' in row:
                        csv_id = row['id'].strip()
                        # 空のidをスキップ
                        if not csv_id:
                            continue
                        result = {
                            "id": csv_id,
                            "text": row['text'].strip(),
                            "font": row['font'].strip()
                        }
                        # name_textとname_orderが存在する場合は追加
                        if 'name_text' in row:
                            result['name_text'] = row['name_text'].strip()
                        if 'name_order' in row:
                            result['name_order'] = row['name_order'].strip()
                        results.append(result)
                return results
        except UnicodeDecodeError:
            # cp932でも失敗した場合、shift_jisを試す
            try:
                with open(csv_path, 'r', encoding='shift_jis') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        if 'id' in row and 'text' in row and 'font' in row:
                            csv_id = row['id'].strip()
                            # 空のidをスキップ
                            if not csv_id:
                                continue
                            results.append({
                                "id": csv_id,
                                "text": row['text'].strip(),
                                "font": row['font'].strip()
                            })
                    return results
            except Exception as e:
                print(f"Error reading CSV {csv_path}: {e}", file=sys.stderr)
                return []
    
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}", file=sys.stderr)
        return []
    
    return results

