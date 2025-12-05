学習側とアプリ側で必要な作業を整理中。


[3 tools called]


学習側とアプリ側で必要な作業を整理しました。

## 学習側（Pythonスクリプト）で必要な作業

### 1. 文字列全体の幅を考慮した重み付け平均

#### `aggregate_pairs.py` の修正

**追加する機能:**
- 文字列全体の幅を計算する関数を追加
- 各ペアレコードに文字列全体の幅を追加

```python
# 追加する関数
def calculate_total_width(sequence, bbox):
    """
    文字列全体の幅を計算（最初の文字のmin_xから最後の文字のmax_xまで）
    """
    if not sequence or not bbox:
        return None
    
    first_id = sequence[0].get("id")
    last_id = sequence[-1].get("id")
    
    if first_id not in bbox or last_id not in bbox:
        return None
    
    first_min_x = bbox[first_id].get("min_x")
    last_max_x = bbox[last_id].get("max_x")
    
    if first_min_x is None or last_max_x is None:
        return None
    
    return last_max_x - first_min_x

# aggregate_pairs関数内で追加
total_width = calculate_total_width(sequence, bbox)
record["text_total_width"] = total_width  # 文字列全体の幅
record["text_length"] = len(sequence)  # 文字列長（参考）
```

**CSV出力に追加:**
- `text_total_width` カラムを追加
- `text_length` カラムを追加（参考）

#### `build_phase1_model.py` の修正

**追加する機能:**
- 文字列全体の幅を重みとして使用した重み付け平均の計算

```python
# データ構造に追加
stats[font_key][pair_key] = {
    # ... 既存のフィールド ...
    "sum_text_total_width": 0.0,  # 文字列全体の幅の合計
    "sum_text_total_width_weighted": 0.0,  # gap_norm * text_total_width の合計
    "sum_weight_text_width": 0.0,  # 文字列全体の幅による重みの合計
}

# 集計時に追加
text_total_width = parse_float(row.get("text_total_width"))
if text_total_width is not None and text_total_width > 0:
    # 文字列全体の幅を重みとして使用（フォントサイズと組み合わせることも可能）
    weight_by_text_width = text_total_width  # または font_size_est * text_total_width
    stats[font_key][pair_key]["sum_text_total_width"] += text_total_width
    stats[font_key][pair_key]["sum_text_total_width_weighted"] += gap_norm * weight_by_text_width
    stats[font_key][pair_key]["sum_weight_text_width"] += weight_by_text_width

# 平均計算時に追加
if use_weighted_avg:
    # フォントサイズと文字列全体の幅の両方を考慮した重み付け平均
    # 例: weight = font_size * text_total_width
    combined_weight = sum_weight * sum_weight_text_width  # または適切な組み合わせ
    if combined_weight > 0:
        gap_norm_avg = sum_gap_norm_weighted / combined_weight
```

**JSON出力に追加（オプション）:**
- `text_total_width_avg` を追加（文字列全体の幅の平均値）

### 2. 既存の実装確認（フォントサイズによる重み付け平均）

**確認事項:**
- `build_phase1_model.py` でフォントサイズによる重み付け平均が正しく実装されているか確認
- 重み付け平均の計算式が正しいか確認

---

## アプリ側（HTML/JavaScript）で必要な作業

### 1. 全体トラッキング調整の一貫性修正

#### `phase0-demo.html` の修正

**問題点:**
- Phase0: px単位で直接加算
- Phase1: 係数として乗算（%単位）

**修正内容:**
- Phase1でもPhase0と同じ方法（px単位で直接加算）を使用

```javascript
// getKerningPhase1関数内の修正
// 修正前:
const trackingCoefficient = 1.0 + (globalTracking / 100);
return gapPx * trackingCoefficient;

// 修正後:
// Phase0と同じ方法（px単位で直接加算）
return gapPx + globalTracking;
```

**修正箇所:**
1. 1289行目付近: 未学習ペア（平均値アルゴリズム）の処理
2. 1337行目付近: 未学習ペア（Phase0スケールアルゴリズム）の処理
3. 1487行目付近: 学習済みペア（gap_actual_avg使用）の処理
4. 1500行目付近: 学習済みペア（gap_norm使用）の処理

### 2. 文字列全体の幅による補正（オプション）

**条件:**
- モデルJSONに `text_total_width_avg` が含まれる場合のみ実装

**実装内容:**
```javascript
// getKerningPhase1関数内で追加
const learnedTextWidth = record.text_total_width_avg;
const currentTextWidth = currentTextInfo?.phase0TotalWidth;

if (learnedTextWidth && currentTextWidth && currentTextWidth > 0) {
    // 文字列全体の幅による補正係数
    // 幅が狭い場合、ギャップが小さくなる傾向があるため補正
    const widthCorrection = currentTextWidth / learnedTextWidth;
    gapPx = gapPx * widthCorrection;
}
```

### 3. 既存の実装確認

**確認事項:**
- Phase1モデルの読み込みが正しく動作しているか
- フォント名の正規化が正しく動作しているか
- 未学習ペアの処理が正しく動作しているか

---

## 実装優先順位

### 優先度: 高
1. アプリ側: 全体トラッキング調整の一貫性修正
   - Phase0とPhase1で動作が異なる問題を修正
   - 影響範囲が大きい

### 優先度: 中
2. 学習側: 文字列全体の幅を考慮した重み付け平均
   - 学習データの精度向上
   - モデル再生成が必要

### 優先度: 低（オプション）
3. アプリ側: 文字列全体の幅による補正
   - モデルJSONに情報が含まれる場合のみ
   - リアルタイム補正が必要な場合のみ

---

## 実装時の注意点

### 学習側
- 既存のCSVファイルとの互換性を考慮（新しいカラムはオプション）
- モデルJSONの構造変更時は、アプリ側の対応も必要

### アプリ側
- 後方互換性を考慮（既存のモデルJSONでも動作するように）
- Phase0とPhase1で一貫した動作を保証

この順序で実装を進めますか？




””


Phase2の実装内容を確認中です。


[2 tools called]


Phase2の実装計画を確認中。現在の実装状況を確認します。


[3 tools called]


Phase2の実装計画を提案します。

## Phase2実装計画

### 現在の実装状況
- Phase0/Phase1のモード切り替え：実装済み
- Phase1の学習値ベースカーニング：実装済み
- 幅アンカー：実装済み
- ブレンド機能：実装済み

### Phase2で実装する機能（優先順位順）

#### 1. 重心補正（Center of Mass Adjustment）
- 目的：文字列の視覚的重心を中央に寄せる
- 実装場所：`computeKerningPositions`の後処理
- 優先度：高

#### 2. ギャップ分布の均し（標準偏差補正）
- 目的：ギャップのばらつきを均す
- 実装場所：`computeKerningPositions`の後処理
- 優先度：高

#### 3. Triplet補正
- 目的：3文字以上の連続パターンに特別な調整を適用
- 実装場所：`computeKerningPositions`の後処理
- 優先度：中

#### 4. 差分学習アプローチ
- 目的：Phase0からの乖離を抑制
- 実装場所：学習側（`build_phase1_model.py`）とアプリ側の両方
- 優先度：中

### 実装の進め方

提案：まず1と2（重心補正と標準偏差補正）から実装し、効果を確認してから3と4に進む。

進め方の選択肢：
- A. 重心補正から実装開始
- B. 標準偏差補正から実装開始
- C. 両方を同時に実装
- D. その他（指定があれば）

どれで進めますか？



””””””””””””

「W|A A|T T|A」が広く見える原因を確認中。`LATIN_PAIR`の補正値とTriplet補正の適用状況を確認します。


[4 tools called]


「W|A A|T T|A」が広く見える原因を確認中。補正値の適用状況を確認します。


[2 tools called]


「W|A A|T T|A」が広く見える原因と対策です。

## 現在の状況

1. **Phase0の`LATIN_PAIR`補正**: `-0.3`（文字幅に対する比率、詰める）
2. **Triplet補正の`LATIN_PAIR_SEQUENCE`**: `-0.1px`（px単位、詰める）

Phase1モードではPhase0の補正が適用されない場合があり、Triplet補正の`-0.1px`だけでは不十分な可能性があります。

## 対策案

### 対策1: Triplet補正値を大きくする（推奨）

`ADJUST_TRIPLET_LATIN_SEQUENCE`を`-0.1px`から`-0.2px`または`-0.3px`に変更：

```javascript:phase0-demo.html
// 381行目付近
const ADJUST_TRIPLET_LATIN_SEQUENCE = -0.2;  // -0.1から-0.2に変更（より積極的に締める）
// または
const ADJUST_TRIPLET_LATIN_SEQUENCE = -0.3;  // さらに強く締める
```

### 対策2: フォントサイズに比例した補正にする

px固定ではなく、フォントサイズに比例させる：

```javascript:phase0-demo.html
// applyTripletAdjustment関数内（1837行目付近）を修正
if (pair1 === "LATIN_PAIR") {
    pattern = "LATIN_PAIR_SEQUENCE";
    adjustment = ADJUST_TRIPLET_LATIN_SEQUENCE * (fontSize / 64);  // 64px基準でスケーリング
    // または
    adjustment = -0.003 * fontSize;  // フォントサイズの0.3%を詰める
}
```

### 対策3: Phase1でもPhase0の補正を考慮する

Phase1モードでも、未学習ペアや特定の条件下でPhase0の`LATIN_PAIR`補正を適用する。

## 推奨

まずは対策1で`ADJUST_TRIPLET_LATIN_SEQUENCE`を`-0.2px`に変更。それでも広く見える場合は`-0.3px`に調整。

どの対策を適用しますか？