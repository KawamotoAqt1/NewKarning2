# CSVフォーマット提案

## 現在のフォーマット
```csv
id,text,font
path38,J,Mincho
path34,U,Mincho
path30,I,Mincho
```

## 提案1: name_group と name_order を追加

### フォーマット
```csv
id,text,font,name_group,name_order
path22,瀬,MaruGothic,1,2
path6,廣,MaruGothic,1,1
path18,E,Gothic,2,6
path16,S,Gothic,2,5
path14,O,Gothic,2,4
path12,R,Gothic,2,3
path10,I,Gothic,2,2
path8,H,Gothic,2,1
```

### 説明
- `name_group`: 同じ名前に属する文字に同じグループ番号を付与（1, 2, 3, ...）
- `name_order`: 名前内での文字の順序（1から開始、左から右または上から下の順）

### メリット
- 同じ名前が複数回出現する場合にも対応可能
- グループ番号で名前を明確に区別できる
- 順序情報が明確

### デメリット
- グループ番号を手動で管理する必要がある

---

## 提案2: name_text と name_order を追加

### フォーマット
```csv
id,text,font,name_text,name_order
path22,瀬,MaruGothic,廣瀬,2
path6,廣,MaruGothic,廣瀬,1
path18,E,Gothic,HIROSE,6
path16,S,Gothic,HIROSE,5
path14,O,Gothic,HIROSE,4
path12,R,Gothic,HIROSE,3
path10,I,Gothic,HIROSE,2
path8,H,Gothic,HIROSE,1
```

### 説明
- `name_text`: 名前のテキスト全体（例: "廣瀬", "HIROSE"）
- `name_order`: 名前内での文字の順序（1から開始）

### メリット
- 名前のテキスト全体がCSVに含まれるため、可読性が高い
- デバッグ時に名前を確認しやすい
- 順序情報が明確

### デメリット
- 同じ名前が複数回出現する場合、name_textが重複する

---

## 提案3: name_id と name_order を追加（name_textはオプション）

### フォーマット
```csv
id,text,font,name_id,name_order,name_text
path22,瀬,MaruGothic,1,2,廣瀬
path6,廣,MaruGothic,1,1,廣瀬
path18,E,Gothic,2,6,HIROSE
path16,S,Gothic,2,5,HIROSE
path14,O,Gothic,2,4,HIROSE
path12,R,Gothic,2,3,HIROSE
path10,I,Gothic,2,2,HIROSE
path8,H,Gothic,2,1,HIROSE
```

### 説明
- `name_id`: 名前の一意なID（1, 2, 3, ...）
- `name_order`: 名前内での文字の順序（1から開始）
- `name_text`: 名前のテキスト全体（オプション、可読性のため）

### メリット
- name_idで名前を明確に区別できる
- name_textで可読性を確保
- 最も柔軟な形式

### デメリット
- 列数が増える

---

## 推奨: 提案2（name_text と name_order）

**理由:**
1. シンプルで理解しやすい
2. 名前のテキスト全体が含まれるため、可読性が高い
3. デバッグ時に名前を確認しやすい
4. 実装が比較的簡単

### 実装時の注意点
- `name_text`が空の場合は、従来通りSVGの座標ベースでソート
- `name_order`が指定されている場合は、CSVの順序を優先
- 後方互換性のため、`name_text`と`name_order`はオプション列として扱う

---

## 後方互換性

既存のCSVファイル（`name_text`と`name_order`がない場合）は、従来通りSVGの座標ベースでソートする。

```python
# 疑似コード
if 'name_text' in row and 'name_order' in row:
    # CSVの順序情報を使用
    use_csv_order = True
else:
    # SVGの座標ベースでソート
    use_csv_order = False
```

