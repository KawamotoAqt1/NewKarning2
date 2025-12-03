# Phase0 ルールベース×係数（幅に応じた調整）アルゴリズム解説

## 📐 基本概念

Phase0のカーニング計算は、**「ベースライン + 補正値」**という構造になっています。

```
最終ギャップ = ベースライン + ペアカテゴリ補正 + 黒密度補正 + 全体トラッキング調整
```

ただし、各要素は**異なる基準でスケーリング**されています。

---

## 🎯 なぜ「幅に応じた調整」が必要なのか？

### 問題：文字のサイズが異なる

同じフォントサイズ（例：64px）でも、実際の文字幅は異なります：
- **W**（幅広）：約52px
- **A**（中程度）：約43px
- **V**（中程度）：約40px
- **E**（狭い）：約40px

**固定の補正値**を使うと、文字幅が大きいペアでは「詰めすぎ」、小さいペアでは「広すぎ」になってしまいます。

### 解決策：文字幅に比例した補正

文字幅に比例して補正値を調整することで、**視覚的に一貫した間隔**を実現します。

---

## 📊 アルゴリズムの詳細

### 1. ベースライン（base）

**役割**: フォントファミリーとスタイルに応じた基本間隔

**計算方法**:
```javascript
base = baseTracking[fontFamily][styleId]  // テーブルから取得

// base = 0 の場合（デフォルト）
if (base === 0) {
    // Phase1の学習データに基づくデフォルト値
    // 文字幅の35%をベースラインとする
    base = 0.35 * (avgWidth / baseWidthPx)
}
```

**単位**: `fontSize`に対する比率
- 例：`base = 0.35` → `gap_base = 0.35 * 64px = 22.4px`

**なぜfontSize基準？**
- フォントサイズが変わっても、**相対的な間隔**を維持できる
- スタイル（和モダン、北欧など）による**全体的な間隔調整**に適している

---

### 2. ペアカテゴリ補正（pairAdj）

**役割**: 文字の形状の組み合わせに応じた補正

**カテゴリ例**:
- `LATIN_PAIR`（英字同士）: `-0.3` → 詰める（欧文は詰め気味が美しい）
- `VERTICAL_VERTICAL`（四角×四角）: `+0.4` → 広げる（重く見えるので）
- `CURVE_CURVE`（丸×丸）: `-0.2` → 詰める（スカスカに見えがち）
- `DIAGONAL_ANY`（斜線含む）: `-0.5` → 詰める（斜線は詰めてもぶつかって見えにくい）

**計算方法**:
```javascript
pairCat = getPairCategory(leftCharType, rightCharType)
pairAdj = pairCategoryAdjust[pairCat]  // テーブルから取得
gap_pair = pairAdj * avgWidth  // 文字幅でスケーリング
```

**単位**: **文字幅に対する比率**
- 例：`pairAdj = -0.3`, `avgWidth = 52px` → `gap_pair = -0.3 * 52px = -15.6px`

**なぜ文字幅基準？**
- 文字幅が大きいペアほど、**視覚的な影響が大きい**
- 文字幅に比例して補正することで、**視覚的に一貫した効果**を得られる

---

### 3. 黒密度補正（densAdj）

**役割**: 文字の「黒さ」（インクの密度）に応じた補正

**組み合わせ例**:
- `HEAVY-HEAVY`（濃い×濃い）: `+0.5` → 広げる（重く見えるので）
- `HEAVY-LIGHT`（濃い×薄い）: `+0.2` → 少し広げる
- `LIGHT-LIGHT`（薄い×薄い）: `-0.2` → 詰める（スカスカに見えがち）

**計算方法**:
```javascript
densityKey = leftDensity + "-" + rightDensity
densAdj = densityAdjust[densityKey]  // テーブルから取得
gap_density = densAdj * avgWidth  // 文字幅でスケーリング
```

**単位**: **文字幅に対する比率**（pairAdjと同じ）

---

### 4. 全体トラッキング調整（globalTracking）

**役割**: ユーザーが指定する全体の間隔調整

**計算方法**:
```javascript
gap_tracking = globalTracking  // px単位で直接加算
```

**単位**: **px（ピクセル）**
- 例：`globalTracking = 5px` → `gap_tracking = 5px`

**なぜpx単位？**
- ユーザーが直感的に調整できるように、**絶対値**で指定
- フォントサイズや文字幅に依存しない

---

## 🔢 最終的な計算式

```javascript
// 1. 平均文字幅を計算
avgWidth = (leftChar.width + rightChar.width) / 2

// 2. ベースライン（fontSize基準）
gap_base = base * baseWidthPx

// 3. ペアカテゴリ補正（文字幅基準）
gap_pair = pairAdj * avgWidth

// 4. 黒密度補正（文字幅基準）
gap_density = densAdj * avgWidth

// 5. 全体トラッキング調整（px単位）
gap_tracking = globalTracking

// 6. 最終ギャップ
gap = gap_base + gap_pair + gap_density + gap_tracking
    = base * baseWidthPx + (pairAdj + densAdj) * avgWidth + globalTracking
```

---

## 📝 具体例：W|Aペア

### 前提条件
- `fontSize = 64px`
- `W`の幅 = 52px
- `A`の幅 = 43px
- `avgWidth = (52 + 43) / 2 = 47.5px`
- `base = 0`（デフォルト）→ `0.35 * (47.5 / 64) = 0.2598`
- `pairAdj = -0.3`（LATIN_PAIR）
- `densAdj = 0`（MEDIUM-MEDIUM）
- `globalTracking = 0`

### 計算過程

```javascript
// 1. ベースライン
gap_base = 0.2598 * 64 = 16.63px

// 2. ペアカテゴリ補正
gap_pair = -0.3 * 47.5 = -14.25px

// 3. 黒密度補正
gap_density = 0 * 47.5 = 0px

// 4. 全体トラッキング調整
gap_tracking = 0px

// 5. 最終ギャップ
gap = 16.63 + (-14.25) + 0 + 0 = 2.38px
```

**結果**: WとAの間は約2.4pxの間隔になります。

---

## 🎨 設計思想

### 1. **階層的な補正構造**

```
ベースライン（全体的な間隔）
  ↓
ペアカテゴリ補正（形状の組み合わせ）
  ↓
黒密度補正（視覚的重さ）
  ↓
全体トラッキング調整（ユーザー調整）
```

### 2. **異なる基準でのスケーリング**

- **ベースライン**: `fontSize`基準 → フォントサイズに比例
- **補正値**: `文字幅`基準 → 文字の大きさに比例
- **トラッキング**: `px`基準 → 絶対値で調整

### 3. **Phase1との整合性**

- Phase1の学習データ（`gap_norm_avg: 0.3532`）をベースラインのデフォルト値として使用
- Phase0のルールベースとPhase1の学習ベースを**スムーズに統合**

---

## 🛡️ 安全装置（ガード）

```javascript
minGap = -0.2 * baseWidthPx  // 最大20%のオーバーラップまで許可
maxGap = 0.8 * baseWidthPx   // 最大80%の間隔まで許可

if (gap < minGap) gap = minGap;
if (gap > maxGap) gap = maxGap;
```

**目的**: 計算結果が極端な値になった場合でも、**視覚的に許容できる範囲**に制限する

---

## 💡 まとめ

Phase0のアルゴリズムは、**「ベースライン + 文字幅に比例した補正」**という構造になっています。

- **ベースライン**: フォントサイズに比例（全体的な間隔）
- **補正値**: 文字幅に比例（視覚的な一貫性）
- **トラッキング**: 絶対値（ユーザー調整）

この設計により、**フォントサイズや文字幅が変わっても、視覚的に一貫した美しい間隔**を実現できます。

