# これまでの試行の比較

## 試行1: gap_actual_avgをフォントサイズでスケール（最初）
```javascript
gapPx = gapActualAvg * (currentFontSize / learnedFontSize)
```
- **結果**: 計算値は正しい（8.613px）が、視覚的に広い
- **問題**: SVGのbboxとCanvas APIのmeasureText().widthの差を考慮していない

## 試行2: gap_normを使用（文字幅でスケール）
```javascript
gapPx = gapNorm * currentAvgWidth
```
- **結果**: 計算値が小さくなる（7.366px）が、まだ広い
- **問題**: gap_normはSVGのbboxで計算されているため、Canvas APIで再現できない

## 試行3: actualBoundingBoxRight - actualBoundingBoxLeftを使用
```javascript
actualWidth = actualBoundingBoxRight - actualBoundingBoxLeft
gapPx = gapActualAvg * fontSizeScale * (currentActualWidth / learnedActualWidth)
```
- **結果**: actualWidthが両方とも45pxになってしまい、正しくない
- **問題**: actualBoundingBoxLeftが負の値で、actualBoundingBoxRightがmeasureText().widthより大きいため

## 試行4: measureText().widthの比率で補正
```javascript
widthRatio = currentAvgWidth / learnedAvgWidth
gapPx = gapActualAvg * fontSizeScale * widthRatio
```
- **結果**: まだ正しくない
- **問題**: gap_actualはSVGのbboxで計算されているが、measureText().widthの比率で補正しても、SVGのbboxとCanvas APIのmeasureText().widthの差を考慮していない

## 試行5: 固定比率0.855を適用
```javascript
canvasToSvgRatio = 0.855  // Canvas API / SVG bbox
gapPx = gapActualAvg * fontSizeScale * canvasToSvgRatio
```
- **結果**: まだ試行中
- **問題**: 試行4と実質的に同じアプローチ（固定比率を使っているだけ）

## 試行6（最新）: actualBoundingBoxRight/Leftを使用した位置計算
```javascript
// 位置計算
currentRightEdge = x + A.actualBoundingBoxRight
nextLeftEdge = currentRightEdge + gap
nextX = nextLeftEdge - B.actualBoundingBoxLeft

// gap_actualの補正
gapPx = gapActualAvg * fontSizeScale  // 試行1と同じ
```
- **違い**: 位置計算で`actualBoundingBoxRight`と`actualBoundingBoxLeft`を使用
- **問題**: gap_actualの補正は試行1と同じ（比率をかけていない）
- **期待**: 位置計算で`actualBoundingBoxRight`と`actualBoundingBoxLeft`を使用することで、SVGのbboxを基準にした位置計算ができるはず

## 根本的な問題

**すべての試行が「比率をかける」という同じアプローチ**

しかし、本当の問題は：
1. **文字の配置基準点が異なる**
   - SVG: bboxのmin_x/max_xで配置
   - Canvas API: fillText(x, y)のx座標がベースラインの左端

2. **gap_actualの意味**
   - gap_actual = I.min_x - N.max_x = 8.615px
   - これは「Iの左端（bbox）からNの右端（bbox）までの距離」
   - Canvas APIで再現するには、この基準点の違いを考慮する必要がある

3. **単純な比率補正では不十分**
   - gap_actualに比率をかけるだけでは、文字の配置基準点の違いを解決できない

## 本当に必要なアプローチ

SVGのbboxとCanvas APIのmeasureText().widthの差を考慮するだけでなく、
**文字の配置基準点の違いを考慮した補正**が必要。

具体的には：
- SVG: N.max_x = 340.05px, I.min_x = 348.67px
- Canvas API: NをfillText(x, y)で描画した場合、Nの右端は x + measureText().width
- IをfillText(x, y)で描画した場合、Iの左端は x + actualBoundingBoxLeft

しかし、実際には：
- fillText(x, y)のx座標は文字のベースラインの左端
- 文字の実際の左端は x + actualBoundingBoxLeft
- 文字の実際の右端は x + actualBoundingBoxRight

したがって、gap_actualをCanvas APIで再現するには：
1. Nの右端を計算: currentX + N.actualBoundingBoxRight
2. Iの左端を計算: nextX + I.actualBoundingBoxLeft
3. gap = Iの左端 - Nの右端 = 8.615px（SVGのbbox基準）

しかし、これは複雑すぎる。

**より簡単なアプローチ**:
- gap_actualをそのまま使用し、フォントサイズでスケール
- しかし、文字の配置基準点の違いを考慮する必要がある
- つまり、fillTextのx座標を調整する必要がある

