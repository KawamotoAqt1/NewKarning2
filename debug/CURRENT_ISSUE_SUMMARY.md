# 現在の課題まとめ

## 問題の概要
**NとIの間隔が学習画像と比べて広い**

## 学習データの値
- **N|Iペアのgap_actual**: 8.615px
  - 計算式: `gap_actual = I.min_x - N.max_x`
  - N (path21): min_x=303.33px, max_x=340.05px, width=36.72px
  - I (path23): min_x=348.67px, max_x=365.75px, width=17.08px
  - gap_actual = 348.67 - 340.05 = 8.615px

- **A|Nペアのgap_actual**: 9.854px（参考）
  - A: min_x=260.67px, max_x=293.48px, width=32.81px
  - N: min_x=303.33px, max_x=340.05px, width=36.72px
  - gap_actual = 303.33 - 293.48 = 9.854px

## 現在の実装
- **案1の実装**: `gap_actual_avg`をフォントサイズの比率でスケール
  - `gapPx = gap_actual_avg * (currentFontSize / learnedFontSize)`
  - フォントサイズ45pxの場合: `gapPx = 8.615 * (45 / 45.01) = 8.613px`（ほぼ一致）

## 根本的な問題

### 1. SVGのbboxとCanvas APIのmeasureTextの差
- **SVG bbox（学習データ）**:
  - N: 36.72px
  - I: 17.08px
  - 平均: 26.90px

- **Canvas API measureText（フォントサイズ45px）**:
  - N: 約31px
  - I: 約15px
  - 平均: 約23px

- **比率**: Canvas API / SVG bbox ≈ 0.86（約14%小さい）

### 2. gap_normを使用した場合の問題
- **学習データ**:
  - gap_norm = gap_actual / avg_width = 8.615 / 26.90 = 0.3202

- **Canvas APIで計算**:
  - gapPx = gap_norm * currentAvgWidth = 0.3202 * 23 = 7.366px
  - これは学習時のgap_actual (8.615px)より**小さい**

- **しかし、ユーザーは「まだ広い」と言っている**
  - 計算値が小さいのに、視覚的には広く見える
  - これは矛盾している

## 試した解決策

1. **gap_actual_avgを直接使用**（フォントサイズでスケール）
   - 結果: 計算値は正しいが、視覚的に広い

2. **gap_normを使用**（文字幅でスケール）
   - 結果: 計算値が小さくなるが、まだ広い

3. **文字幅の比率で補正**
   - 結果: まだ試行中

## 考えられる原因

### 可能性1: Canvas APIのmeasureTextが実際の描画幅と異なる
- `measureText().width`は文字の描画幅を返すが、実際の描画位置との関係が不明確
- `fillText(x, y)`のx座標と文字の実際の左端の関係

### 可能性2: 文字の配置方法の違い
- SVGではbboxのmin_x/max_xで配置
- Canvas APIではベースラインの左端から描画
- この差が間隔に影響している可能性

### 可能性3: gap_actualの計算方法の問題
- `gap_actual = next.min_x - current.max_x`は正しい
- しかし、Canvas APIで再現する際の基準点が異なる可能性

## 次のステップ

1. **実際のCanvas描画位置を確認**
   - `fillText`で描画した文字の実際の位置を測定
   - SVGのbboxと比較

2. **文字の配置基準点を統一**
   - SVG: bboxのmin_x/max_x
   - Canvas: ベースラインの左端
   - この差を考慮した補正が必要かも

3. **視覚的な間隔と計算値の関係を確認**
   - 計算値が正しいのに視覚的に広い場合、別の要因がある可能性

## 実装した解決策

### 1. Canvas APIの実際の描画位置を取得
- `resolveCharFeatures`関数に`actualBoundingBoxLeft`、`actualBoundingBoxRight`、`actualWidth`を追加
- Canvas APIの`measureText().actualBoundingBoxLeft`と`actualBoundingBoxRight`を使用して、実際の描画位置を測定

### 2. gap_actualの補正方法を改善
- `getKerningPhase1`関数で、実際の描画幅（`actualWidth`）を使用して補正
- フォントサイズの比率と実際の描画幅の比率の両方を考慮
- SVGのbboxとCanvas APIの実際の描画位置の差を補正

### 3. 位置計算の改善
- `computeKerningPositions`関数で、`actualBoundingBoxLeft`と`actualBoundingBoxRight`を考慮した位置計算
- 次の文字のx座標を計算する際に、実際の描画位置を考慮

## 現在のコードの状態
- `phase0-demo.html`の`getKerningPhase1`関数: 実際の描画幅を使用した補正を実装
- `resolveCharFeatures`関数: `actualBoundingBoxLeft`、`actualBoundingBoxRight`、`actualWidth`を追加
- `computeKerningPositions`関数: 実際の描画位置を考慮した位置計算を実装
- デバッグ情報を出力中（N|Iペアの場合）

## 次のステップ（テスト）
1. ブラウザで`phase0-demo.html`を開いて、N|Iペアの間隔を確認
2. コンソールのデバッグ情報を確認して、計算値が正しいか確認
3. 視覚的に間隔が適切か確認

