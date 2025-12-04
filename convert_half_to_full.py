#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSVファイル内のtextとname_text列の半角アルファベットを全角アルファベットに変換するスクリプト
"""

import csv
from pathlib import Path
import sys

def half_to_full_width(text: str) -> str:
    """
    半角アルファベットを全角アルファベットに変換
    A-Z -> Ａ-Ｚ
    a-z -> ａ-ｚ
    """
    result = []
    for char in text:
        if 'A' <= char <= 'Z':
            # 半角大文字を全角大文字に変換
            result.append(chr(ord(char) - ord('A') + ord('Ａ')))
        elif 'a' <= char <= 'z':
            # 半角小文字を全角小文字に変換
            result.append(chr(ord(char) - ord('a') + ord('ａ')))
        else:
            # その他の文字はそのまま
            result.append(char)
    return ''.join(result)

def convert_csv_half_to_full(input_path: str, output_path: str = None):
    """
    CSVファイル内のtextとname_text列の半角アルファベットを全角に変換
    
    Args:
        input_path: 入力CSVファイルのパス
        output_path: 出力CSVファイルのパス（Noneの場合は上書き）
    
    Returns:
        bool: 変換が成功したかどうか
    """
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"エラー: ファイルが見つかりません: {input_path}", file=sys.stderr)
        return False
    
    if output_path is None:
        output_path = input_path
    
    # CSVファイルを読み込んで変換
    rows = []
    fieldnames = None
    detected_encoding = None
    
    # 複数のエンコーディングを試す
    encodings = ['utf-8', 'cp932', 'shift_jis', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames  # ヘッダーをそのまま保持
                
                for row in reader:
                    # textカラムとname_textカラムのみを変換
                    if 'text' in row and row['text']:
                        row['text'] = half_to_full_width(row['text'])
                    if 'name_text' in row and row['name_text']:
                        row['name_text'] = half_to_full_width(row['name_text'])
                    rows.append(row)
            
            detected_encoding = encoding
            print(f"エンコーディング検出: {encoding}")
            break
            
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"エラー: {encoding} で読み込み中にエラーが発生しました: {e}", file=sys.stderr)
            continue
    
    if detected_encoding is None:
        print(f"エラー: {input_path} のエンコーディングを検出できませんでした", file=sys.stderr)
        return False
    
    try:
        # 変換したデータを書き込み（UTF-8で出力）
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()  # ヘッダーは変換せずそのまま書き込み
            writer.writerows(rows)
        
        print(f"変換完了: {input_path} -> {output_path}")
        print(f"変換した行数: {len(rows)}")
        return True
        
    except Exception as e:
        print(f"エラー: {input_path} の書き込み中にエラーが発生しました: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        target = Path(target_path)
        
        if target.is_file():
            # ファイルが指定された場合
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            convert_csv_half_to_full(target_path, output_path)
        elif target.is_dir():
            # ディレクトリが指定された場合
            csv_files = list(target.glob("*.csv"))
            if not csv_files:
                print(f"エラー: {target_path} にCSVファイルが見つかりません", file=sys.stderr)
                sys.exit(1)
            
            print(f"変換対象フォルダ: {target_path}")
            print(f"見つかったCSVファイル数: {len(csv_files)}")
            print()
            
            success_count = 0
            fail_count = 0
            
            for csv_file in csv_files:
                print(f"[{success_count + fail_count + 1}/{len(csv_files)}] 処理中: {csv_file.name}")
                if convert_csv_half_to_full(str(csv_file)):
                    success_count += 1
                else:
                    fail_count += 1
                print()
            
            print("=" * 50)
            print(f"処理完了: 成功 {success_count}件, 失敗 {fail_count}件")
        else:
            print(f"エラー: {target_path} はファイルでもディレクトリでもありません", file=sys.stderr)
            sys.exit(1)
    else:
        # デフォルト: dataset_trainフォルダ内のすべてのCSVファイルを変換
        dataset_dir = Path("dataset_train")
        if not dataset_dir.exists():
            print(f"エラー: {dataset_dir} フォルダが見つかりません", file=sys.stderr)
            sys.exit(1)
        
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            print(f"エラー: {dataset_dir} にCSVファイルが見つかりません", file=sys.stderr)
            sys.exit(1)
        
        print(f"変換対象フォルダ: {dataset_dir}")
        print(f"見つかったCSVファイル数: {len(csv_files)}")
        print("（特定のファイルやフォルダを指定する場合は、コマンドライン引数で指定してください）")
        print("例: python convert_half_to_full.py dataset_train/06096813.csv")
        print("例: python convert_half_to_full.py dataset_train")
        print()
        
        success_count = 0
        fail_count = 0
        
        for csv_file in csv_files:
            print(f"[{success_count + fail_count + 1}/{len(csv_files)}] 処理中: {csv_file.name}")
            if convert_csv_half_to_full(str(csv_file)):
                success_count += 1
            else:
                fail_count += 1
            print()
        
        print("=" * 50)
        print(f"処理完了: 成功 {success_count}件, 失敗 {fail_count}件")

