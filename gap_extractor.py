"""
結合・ソート・gap_actual計算モジュール
SVGのbounding box情報とCSVの文字情報を結合し、文字間隔を計算する
"""

from typing import List, Dict, Optional


def merge_svg_csv(svg_data: List[Dict], csv_data: List[Dict]) -> List[Dict]:
    """
    SVGのbounding box情報とCSVの文字情報をidで結合
    
    Args:
        svg_data: SVG解析結果 [{"id": str, "min_x": float, ...}, ...]
        csv_data: CSV読み込み結果 [{"id": str, "text": str, "font": str}, ...]
    
    Returns:
        結合されたデータ [{"id": str, "text": str, "font": str, "min_x": float, ...}, ...]
    """
    # SVGデータをidをキーにした辞書に変換
    svg_dict = {item["id"]: item for item in svg_data}
    
    merged = []
    for csv_item in csv_data:
        csv_id = csv_item.get("id", "").strip()
        # 空のidをスキップ
        if not csv_id:
            continue
        if csv_id in svg_dict:
            merged_item = {
                **csv_item,  # id, text, font
                **svg_dict[csv_id]  # min_x, max_x, min_y, max_y, width, height
            }
            merged.append(merged_item)
        else:
            # CSVに存在するがSVGに存在しないidの場合、警告を出す（空のidは除く）
            print(f"Warning: id '{csv_id}' found in CSV but not in SVG")
    
    return merged


def calculate_gap_actual(merged_data: List[Dict]) -> List[Dict]:
    """
    CSVの行順（文字列順）に基づいて、隣接ペアのgap_actualを計算
    
    Args:
        merged_data: 結合されたデータ（CSVの順序を保持）
    
    Returns:
        ペア情報のリスト [{"left_id": str, "left": str, "right_id": str, "right": str, "gap_actual": float}, ...]
    """
    pairs = []
    
    for i in range(len(merged_data) - 1):
        current = merged_data[i]
        next_item = merged_data[i + 1]
        
        # gap_actual = next.min_x - current.max_x
        gap_actual = next_item["min_x"] - current["max_x"]
        
        pairs.append({
            "left_id": current["id"],
            "left": current["text"],
            "right_id": next_item["id"],
            "right": next_item["text"],
            "gap_actual": gap_actual
        })
    
    return pairs


def extract_sequence(merged_data: List[Dict]) -> List[Dict]:
    """
    文字列順のシーケンス情報を抽出
    
    Args:
        merged_data: 結合されたデータ（CSVの順序を保持）
    
    Returns:
        シーケンス情報 [{"id": str, "text": str}, ...]
    """
    return [
        {"id": item["id"], "text": item["text"]}
        for item in merged_data
    ]


def extract_bbox_dict(merged_data: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    idをキーにしたbounding box情報の辞書を抽出
    
    Args:
        merged_data: 結合されたデータ
    
    Returns:
        {"id": {"min_x": float, "max_x": float, ...}, ...}
    """
    bbox_dict = {}
    
    for item in merged_data:
        bbox_dict[item["id"]] = {
            "min_x": item["min_x"],
            "max_x": item["max_x"],
            "min_y": item["min_y"],
            "max_y": item["max_y"],
            "width": item["width"],
            "height": item["height"]
        }
    
    return bbox_dict


def get_font(merged_data: List[Dict]) -> Optional[str]:
    """
    フォント名を取得（最初のレコードのfontを返す）
    
    Args:
        merged_data: 結合されたデータ
    
    Returns:
        フォント名、またはNone
    """
    if merged_data:
        return merged_data[0].get("font")
    return None


def is_japanese_char(char: str) -> bool:
    """
    文字が日本語（ひらがな、カタカナ、漢字）かどうかを判定
    
    Args:
        char: 判定する文字
    
    Returns:
        日本語の場合True
    """
    if not char:
        return False
    code = ord(char[0])
    return (
        0x3040 <= code <= 0x309F or  # ひらがな
        0x30A0 <= code <= 0x30FF or  # カタカナ
        0x4E00 <= code <= 0x9FAF or  # 漢字
        0x3400 <= code <= 0x4DBF     # 拡張漢字
    )


def get_text_type(text: str) -> str:
    """
    テキストの種類を判定
    
    Args:
        text: 判定するテキスト
    
    Returns:
        "alphabet", "japanese", "number", "symbol", "mixed"
    """
    if not text:
        return "symbol"
    
    has_alpha = False
    has_japanese = False
    has_number = False
    
    for char in text:
        if char.isalpha() and not is_japanese_char(char):
            has_alpha = True
        elif is_japanese_char(char):
            has_japanese = True
        elif char.isdigit():
            has_number = True
    
    if has_japanese:
        return "japanese"
    elif has_alpha:
        return "alphabet"
    elif has_number:
        return "number"
    else:
        return "symbol"


def get_center_y(item: Dict) -> float:
    """
    文字の中心Y座標を取得
    
    Args:
        item: 文字データ
    
    Returns:
        中心Y座標
    """
    return (item["min_y"] + item["max_y"]) / 2.0


def get_center_x(item: Dict) -> float:
    """
    文字の中心X座標を取得
    
    Args:
        item: 文字データ
    
    Returns:
        中心X座標
    """
    # Yスケールが負の場合でも、X座標は通常通り
    # ただし、min_xとmax_xが入れ替わっている可能性があるため、
    # 実際の表示位置を考慮してmax_xを使用（Yスケールが負の場合、X座標も反転する可能性がある）
    # 通常はmin_xとmax_xの平均を使用
    return (item["min_x"] + item["max_x"]) / 2.0


def group_by_rows(merged_data: List[Dict]) -> List[List[Dict]]:
    """
    Y座標で文字を行ごとにグループ化（改善版）
    
    アルゴリズム：
    1. 全文字をY座標でソート
    2. 隣接する文字のY座標の差の分布を分析
    3. 自然な区切り（大きな差）を見つけて行を判定
    4. 各グループ内でX座標でソート
    
    Args:
        merged_data: 結合されたデータ
    
    Returns:
        行ごとにグループ化されたデータのリスト [[行1の文字], [行2の文字], ...]
    """
    if not merged_data:
        return []
    
    if len(merged_data) == 1:
        return [merged_data]
    
    # Step 1: 全文字をY座標でソート（上から下の順）
    sorted_by_y = sorted(merged_data, key=lambda item: get_center_y(item))
    
    # Step 2: 隣接する文字のY座標の差を計算
    y_diffs = []
    for i in range(1, len(sorted_by_y)):
        current_y = get_center_y(sorted_by_y[i - 1])
        next_y = get_center_y(sorted_by_y[i])
        y_diff = abs(next_y - current_y)
        y_diffs.append(y_diff)
    
    if not y_diffs:
        return [sorted_by_y]
    
    # Step 3: Y座標の差の分布から、行の区切りの閾値を決定
    # 小さな差（同じ行内）と大きな差（行の区切り）を区別
    sorted_diffs = sorted(y_diffs)
    
    # 中央値と最大値を使用して閾値を決定
    median_diff = sorted_diffs[len(sorted_diffs) // 2]
    max_diff = max(y_diffs)
    
    # 閾値：中央値と最大値の中間値、または中央値の2倍のうち大きい方
    # これにより、同じ行内の小さな差と、行の区切りの大きな差を区別
    threshold = max(median_diff * 1.5, max_diff * 0.3)
    
    # 最小閾値も設定（文字の高さの平均の0.6倍以上）
    avg_height = sum(item["height"] for item in merged_data) / len(merged_data)
    min_threshold = avg_height * 0.6
    threshold = max(threshold, min_threshold)
    
    # Step 4: 閾値を使って行をグループ化
    rows = []
    current_row = [sorted_by_y[0]]
    
    for i in range(1, len(sorted_by_y)):
        current_item = sorted_by_y[i - 1]
        next_item = sorted_by_y[i]
        
        current_y = get_center_y(current_item)
        next_y = get_center_y(next_item)
        y_diff = abs(next_y - current_y)
        
        # Y座標の差が閾値以上なら行の区切り
        if y_diff > threshold:
            # 現在の行を保存
            rows.append(current_row)
            # 新しい行を開始
            current_row = [next_item]
        else:
            # 同じ行に追加
            current_row.append(next_item)
    
    # 最後の行を追加
    if current_row:
        rows.append(current_row)
    
    return rows


def is_vertical_text(name_data: List[Dict]) -> bool:
    """
    縦書きか横書きかを判定
    
    判定方法：
    - X座標の範囲とY座標の範囲を比較
    - Y座標の範囲がX座標の範囲より大きい場合、縦書きと判定
    
    Args:
        name_data: 名前の文字データ
    
    Returns:
        縦書きの場合True、横書きの場合False
    """
    if len(name_data) < 2:
        return False
    
    # X座標とY座標の範囲を計算
    x_coords = [get_center_x(item) for item in name_data]
    y_coords = [get_center_y(item) for item in name_data]
    
    x_range = max(x_coords) - min(x_coords)
    y_range = max(y_coords) - min(y_coords)
    
    # Y座標の範囲がX座標の範囲より大きい場合、縦書きと判定
    return y_range > x_range


def sort_by_x_in_row(row_data: List[Dict]) -> List[Dict]:
    """
    行内の文字をX座標でソート（左から右の順）
    
    Args:
        row_data: 1行分の文字データ
    
    Returns:
        X座標でソートされた文字データ
    """
    # Yスケールが負かどうかを判定（min_y > max_yの場合、Yスケールが負）
    has_negative_y_scale = any(item.get("min_y", 0) > item.get("max_y", 0) for item in row_data)
    
    if has_negative_y_scale:
        # Yスケールが負の場合、文字数が少ない場合（2文字など）はmax_xの降順でソート
        # 文字数が多い場合はmin_xの昇順でソート
        if len(row_data) <= 2:
            # 2文字以下の場合はmax_xの降順でソート
            return sorted(row_data, key=lambda item: item["max_x"], reverse=True)
        else:
            # 3文字以上の場合はmin_xの昇順でソート
            return sorted(row_data, key=lambda item: item["min_x"])
    else:
        # Yスケールが正の場合、通常通りmin_xの昇順でソート
        return sorted(row_data, key=lambda item: item["min_x"])


def sort_by_y_in_row(row_data: List[Dict]) -> List[Dict]:
    """
    行内の文字をY座標でソート（上から下の順）
    
    縦書きの場合、文字が重なっている可能性があるため、
    X座標が近い文字同士でグループ化し、各グループ内でY座標でソートする
    
    Args:
        row_data: 1行分の文字データ
    
    Returns:
        Y座標でソートされた文字データ
    """
    if len(row_data) <= 1:
        return row_data
    
    # X座標の範囲を計算
    x_coords = [get_center_x(item) for item in row_data]
    x_range = max(x_coords) - min(x_coords)
    avg_width = sum(item["width"] for item in row_data) / len(row_data)
    
    # X座標が近い文字同士でグループ化（同じ列と判定）
    # 閾値：平均文字幅の0.5倍以内なら同じ列
    x_threshold = avg_width * 0.5
    
    # X座標でソート
    sorted_by_x = sorted(row_data, key=lambda item: get_center_x(item))
    
    # 列ごとにグループ化
    columns = []
    current_column = [sorted_by_x[0]]
    
    for i in range(1, len(sorted_by_x)):
        current_x = get_center_x(sorted_by_x[i - 1])
        next_x = get_center_x(sorted_by_x[i])
        x_diff = abs(next_x - current_x)
        
        if x_diff > x_threshold:
            # 新しい列
            columns.append(current_column)
            current_column = [sorted_by_x[i]]
        else:
            # 同じ列
            current_column.append(sorted_by_x[i])
    
    if current_column:
        columns.append(current_column)
    
    # 各列内でY座標でソート（上から下の順）
    # Yスケールが負の場合、min_yとmax_yが入れ替わっているため、
    # 実際の表示ではmin_yが上、max_yが下になる
    # そのため、min_yの昇順でソートする
    sorted_columns = []
    for col in columns:
        # min_yの昇順でソート（上から下の順）
        sorted_col = sorted(col, key=lambda item: item["min_y"])
        sorted_columns.append(sorted_col)
    
    # 列をX座標でソート（左から右の順）
    sorted_columns.sort(key=lambda col: get_center_x(col[0]))
    
    # 列を結合
    result = []
    for col in sorted_columns:
        result.extend(col)
    
    return result


def split_by_names(merged_data: List[Dict], svg_groups: List[List[str]] = None) -> List[List[Dict]]:
    """
    データを名前ごとに分割する（CSVのname_textとname_orderを優先的に使用）
    
    処理フロー：
    1. CSVにname_textとname_orderが含まれている場合、それを使用してグループ化とソート
    2. それ以外の場合は、SVGグループ構造または位置ベースのアプローチを使用
    
    Args:
        merged_data: 結合されたデータ
        svg_groups: SVGのグループ構造 [[path5, path7], [path9, path11, ...], ...]
                    Noneの場合は位置ベースのアプローチにフォールバック
    
    Returns:
        名前ごとに分割されたデータのリスト [[名前1のデータ], [名前2のデータ], ...]
    """
    if not merged_data:
        return []
    
    if len(merged_data) == 1:
        return [merged_data]
    
    # CSVにname_textとname_orderが含まれているかチェック
    has_name_info = any(item.get('name_text') and item.get('name_order') for item in merged_data)
    
    if has_name_info:
        # CSVのname_textとname_orderを使用してグループ化とソート
        # name_textごとにグループ化
        name_groups_dict = {}
        for item in merged_data:
            name_text = item.get('name_text', '').strip()
            if name_text:
                if name_text not in name_groups_dict:
                    name_groups_dict[name_text] = []
                name_groups_dict[name_text].append(item)
        
        # 各名前グループ内でname_orderでソート
        names = []
        for name_text, name_data in sorted(name_groups_dict.items()):
            # name_orderでソート（数値として比較）
            try:
                sorted_name_data = sorted(name_data, key=lambda x: int(x.get('name_order', 0)))
            except (ValueError, TypeError):
                # name_orderが数値でない場合は文字列としてソート
                sorted_name_data = sorted(name_data, key=lambda x: x.get('name_order', ''))
            names.append(sorted_name_data)
        
        if names:
            return names
    
    # CSVにname_textとname_orderがない場合、SVGグループ構造または位置ベースのアプローチを使用
    # SVGグループ構造が提供されている場合
    if svg_groups:
        names = []
        
        # merged_dataをidをキーにした辞書に変換
        merged_dict = {item["id"]: item for item in merged_data}
        
        # 各グループ（名前）ごとに処理
        for group_path_ids in svg_groups:
            name_data = []
            
            # グループ内の各path idに対応するデータを取得
            for path_id in group_path_ids:
                if path_id in merged_dict:
                    name_data.append(merged_dict[path_id])
            
            # データが取得できた場合のみ追加
            if name_data:
                # 縦書きか横書きかを判定
                if is_vertical_text(name_data):
                    # 縦書きの場合、Y座標でソート（上から下の順）
                    sorted_name_data = sort_by_y_in_row(name_data)
                else:
                    # 横書きの場合、X座標でソート（左から右の順）
                    sorted_name_data = sort_by_x_in_row(name_data)
                names.append(sorted_name_data)
        
        # グループ構造から取得できたデータがある場合、それを返す
        if names:
            return names
    
    # SVGグループ構造がない場合、またはフォールバックとして位置ベースのアプローチ
    # Step 1: Y座標で行ごとにグループ化
    rows = group_by_rows(merged_data)
    
    # Step 2: 各行内でX座標でソート
    sorted_rows = []
    for row in rows:
        sorted_row = sort_by_x_in_row(row)
        sorted_rows.append(sorted_row)
    
    # Step 3: 各行を1つの名前として返す
    return sorted_rows

