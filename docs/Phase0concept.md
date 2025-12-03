了解です！
ここからは **「Phase0：ルールだけで動くカーニングエンジン仕様」** を、実装に落とせるレベルでまとめます。

---

# Phase0 カーニングロジック仕様（学習なし版）

## 0. 目的とゴール

**目的：**

* 「デザイナーの介入なしでも、明らかに変な空き・詰まりがない」
* 「テンプレとしてユーザーに見せても、”自動生成としては十分きれい”と言えるレベル」

**Phase0の前提：**

* 機械学習・教師データはまだ使わない
* すべて「手作業で決めた係数」と「ロジック」で決まる
* 将来の Phase1 以降で、このロジックの係数を“学習で置き換える”前提

---

## 1. 入出力イメージ

### 入力

* `text`：表札に使う文字列（例：「佐藤」「Tanaka」「Wave」）
* `fontId`：フォントID（内部的には後述の fontFamily にマッピング）
* `fontSize`：表示サイズ（px）
* `styleId`：テンプレスタイルID（和モダン / 北欧 / モダン / カジュアル等）
* `globalTracking`：全体トラッキング調整値（px、デフォルト: 0、範囲: -50 ～ +50）
* `direction`：横書き or 縦書き（まずは横書き想定でOK）

### 出力

* 各文字の **X座標**（横書きの場合）

  * `positions = [x0, x1, x2, ...]`
* （あるいは）各ペアの **文字間隔 gap[i]**

---

## 2. 事前に用意しておくテーブル（ハードコードでOK）

### 2.1 フォントファミリー分類テーブル

100フォント以上を、性格でざっくり分ける：

* `Mincho`（明朝系）
* `Gothic`（角ゴシック系）
* `MaruGothic`（丸ゴ系）
* `Brush`（筆文字系・日本語筆記体）
* `Script`（アルファベット筆記体・スクリプト）
* `Design`（装飾系・ロゴ風）

```js
fontFamilyMap = {
  "ヒラギノ明朝 ProN": "Mincho",
  "游明朝": "Mincho",
  "游ゴシック": "Gothic",
  "新ゴ": "Gothic",
  "丸ゴシック": "MaruGothic",
  "HG行書体": "Brush",
  "Brush Script MT": "Script",
  "Comic Sans MS": "Design",
  // ...
}
```

### 2.2 ファミリー別・スタイル別の「基本トラッキング」

テンプレの世界観に合わせて **ベースの字間** を少し変える。

例（px / 1em 換算の“係数”でもOK）：

```js
baseTracking[fontFamily][styleId] = px単位

// 実装例
baseTracking = {
  Mincho: {
    default: 0,
    和モダン: -0.5,   // 少し詰める
    北欧: +0.5,       // 少し広げる
    モダン: 0,
    カジュアル: 0,
  },
  Gothic: {
    default: 0,
    モダン: -0.3,
    カジュアル: +0.3,
    和モダン: 0,
    北欧: 0,
  },
  MaruGothic: {
    default: 0,
  },
  Brush: {
    default: -0.8,
  },
  Script: {
    default: -0.5,
  },
  Design: {
    default: 0,
  },
}
```

Phase0ではここは「デザイナーと相談して、見た目で決める」想定です。

---

## 3. 文字ごとの特徴量の定義

**ここが無限組み合わせ問題を潰すポイント**です。
文字そのものではなく「特徴」に落とします。

### 3.1 文字カテゴリ（charType）

**実装ではCanvasベースで自動判定**しています。以下の文字タイプが定義されています：

* `VERTICAL_HEAVY`：縦線が多く、四角っぽく、黒密度が高い（漢字で縦長＋HEAVY）
* `VERTICAL_LIGHT`：縦線が多く、線が細い（漢字で縦長＋LIGHT/MEDIUM）
* `CURVE`：丸みが多い（かなでfillRatio < 0.3 && 0.8 < aspectRatio < 1.25、または記号でfillRatio > 0.6）
* `DIAGONAL`：斜線が主成分（かなでaspectRatio > 1.3 || < 0.6）
* `COMPLEX`：画数が多く黒い（漢字で縦長以外、またはfillRatio > 0.5）
* `LATIN_UPPER`：英大文字
* `LATIN_LOWER`：英小文字
* `KANA`：ひらがな/カタカナ（CURVE/DIAGONAL以外）

**判定ロジック（実装済み）**：

```js
// 文字種（charCategory）をUnicode範囲で判定
// KANJI, HIRAGANA, KATAKANA, LATIN_UPPER, LATIN_LOWER, SYMBOL

// その後、Canvas分析結果（fillRatio, aspectRatio）と組み合わせてcharTypeを決定

if (charCategory === "KANJI") {
  if (aspectRatio < 0.7) {
    charType = density === "HEAVY" ? "VERTICAL_HEAVY" : "VERTICAL_LIGHT";
  } else {
    charType = "COMPLEX";
  }
} else if (charCategory === "HIRAGANA" || charCategory === "KATAKANA") {
  if (fillRatio < 0.3 && 0.8 < aspectRatio < 1.25) {
    charType = "CURVE";
  } else if (aspectRatio > 1.3 || aspectRatio < 0.6) {
    charType = "DIAGONAL";
  } else {
    charType = "KANA";
  }
} else if (charCategory === "LATIN_UPPER") {
  charType = "LATIN_UPPER";
} else if (charCategory === "LATIN_LOWER") {
  charType = "LATIN_LOWER";
} else {
  charType = fillRatio > 0.6 ? "CURVE" : "MIXED";
}
```

---

### 3.2 黒密度（blackDensity / density）

**実装ではCanvasベースで自動判定**しています。Phase0では **ざっくり3段階** です：

* `LIGHT`（白多め：ハ, ノ, 川）
* `MEDIUM`（普通）
* `HEAVY`（真っ黒：田, 黒, 満 など）

**実装方法（Canvasベース）**：

1. オフスクリーンCanvasに1文字を描画
2. **実際に描画された黒ピクセルの範囲（minX, maxX, minY, maxY）を検出**
3. その範囲内でのみ `getImageData` でピクセルを走査
4. 黒ピクセル判定：RGB平均 < 200 かつ α > 100
5. `fillRatio = filledPixels / totalPixels`（実際の描画領域内のみ）
6. しきい値で3段階に分類

```js
// 実装済みの閾値
if (fillRatio > 0.45) {
  density = "HEAVY";
} else if (fillRatio < 0.20) {
  density = "LIGHT";
} else {
  density = "MEDIUM";
}
```

**重要なポイント**：
* `fillRatio`は**実際に描画されたピクセルの範囲内のみ**で計算（バウンディングボックス全体ではない）
* これにより、人が見たものと同じ値に基づいて計算される

---

## 4. ペアのカテゴリ分類（pairCategory）

文字A, 文字Bの `charType` から、
**ペアのパターン**を少数に絞ります。

例：

* `VERTICAL_VERTICAL`：縦線×縦線（田-田, 田-川）
* `VERTICAL_CURVE`：四角×丸（田-あ）
* `CURVE_CURVE`：丸×丸（あ-お, O-O）
* `DIAGONAL_ANY`：斜線を含むペア（ノ-レ, A-V）
* `COMPLEX_COMPLEX`：黒くて情報量の多い字同士（藤-橋）
* `LATIN_PAIR`：英字同士（A-V, T-o）
* `MIXED`：その他

```js
function getPairCategory(typeA, typeB) {
  if (isLatin(typeA) && isLatin(typeB)) return "LATIN_PAIR";
  if (isDiagonal(typeA) || isDiagonal(typeB)) return "DIAGONAL_ANY";
  if (isVertical(typeA) && isVertical(typeB)) return "VERTICAL_VERTICAL";
  if (isCurve(typeA) && isCurve(typeB)) return "CURVE_CURVE";
  if (isComplex(typeA) && isComplex(typeB)) return "COMPLEX_COMPLEX";
  // ...
  return "MIXED";
}
```

---

## 5. ペアカテゴリごとの補正ルール（Phase0の心臓部）

### 5.1 ペアカテゴリ → 補正値（px）

**ベーストラッキングに対しての“足し引き”** を定義します。

例（イメージ）：

```js
pairCategoryAdjust = {
  VERTICAL_VERTICAL: +0.4,   // 四角が並ぶと重く見えるので少し広げる
  VERTICAL_CURVE:   +0.1,    // ほんのり広げる
  CURVE_CURVE:      -0.2,    // 丸同士でスカスカに見えがちなので詰める
  DIAGONAL_ANY:     -0.5,    // 斜線は詰めてもぶつかって見えにくい
  COMPLEX_COMPLEX:  +0.6,    // 画数多いのは窮屈に見えるので広げる
  LATIN_PAIR:       -0.3,    // 欧文は全体的に詰め気味が美しい
  MIXED:            0.0,
}
```

ここは **Phase0では“目視で決める”** 前提でOK。
（後でδ学習の対象になります）

---

### 5.2 黒密度の組み合わせによる補正

ざっくりで十分：

* `HEAVY-HEAVY`：+0.4 ～ +0.6
* `HEAVY-LIGHT`：+0.2
* `LIGHT-LIGHT`：-0.2

```js
densityAdjust = {
  "HEAVY-HEAVY": +0.5,
  "HEAVY-MEDIUM": +0.3,
  "HEAVY-LIGHT": +0.2,
  "MEDIUM-MEDIUM": 0.0,
  "MEDIUM-LIGHT": -0.1,
  "LIGHT-LIGHT": -0.2,
}
```

---

## 6. 最終的な文字間隔計算フロー（擬似コード）

```js
function computeKerningPositions(text, fontId, fontSize, styleId, globalTracking = 0) {
  const fontFamily = fontFamilyMap[fontId] || "Gothic";
  const base = baseTracking[fontFamily]?.[styleId] || 
              baseTracking[fontFamily]?.default || 0;
  
  // 1. 各文字の特徴量を取得
  const chars = Array.from(text);
  const features = chars.map(ch => getCharFeatures(ch, fontId, fontSize));
  // features[i] = { width, height, fillRatio, aspectRatio, charType, density, charCategory }

  // 2. 位置計算
  let x = 50; // 開始位置
  const positions = [x];

  for (let i = 0; i < chars.length - 1; i++) {
    const A = features[i];
    const B = features[i + 1];

    // 2-1. ペアカテゴリ補正
    const pairCat = getPairCategory(A.charType, B.charType);
    const pairAdj = pairCategoryAdjust[pairCat] || 0;

    // 2-2. 黒密度補正
    const densityKey = A.density + "-" + B.density; // "HEAVY-LIGHT" など
    const densAdj = densityAdjust[densityKey] || 0;

    // 2-3. 最終ギャップ（全体トラッキング調整を追加）
    let gap = base + pairAdj + densAdj + globalTracking;

    // 2-4. 最小・最大のガード（めり込み/空きすぎ防止）
    const minGap = -0.2 * fontSize;  // 若干オーバーラップ許可もあり
    const maxGap = 0.8 * fontSize;
    if (gap < minGap) gap = minGap;
    if (gap > maxGap) gap = maxGap;

    // 2-5. 次の文字のX座標
    x = x + A.width + gap;
    positions.push(x);
  }

  return { positions, gaps, features, ... };
}
```

**重要なポイント**：
* `A.width`は**実際の描画領域の幅**（`measureText`の値ではなく、Canvasで検出した実際の描画範囲）
* `globalTracking`：ユーザーが指定する全体トラッキング調整値（-50px ～ +50px）
* `getCharFeatures`は`resolveCharFeatures`を呼び出し、Canvasベースで自動判定

---

## 7. Phase0 の「評価と限界」のイメージ

### 想定される精度（ネガティブ込み）

* **良くなるところ**

  * まったく同じ固定トラッキングよりは、
    「明らかに変な大きな空き」「不自然な詰まり」がかなり減る
  * フォント変更しても、それなりに均質感は保てる

* **まだ弱いところ**

  * 特殊な名字（例：左右にバランス崩れやすい漢字）
  * 筆文字などクセの強いフォント
  * テンプレの世界観に合わせた“わざと崩したいレイアウト”

---

## 8. Phase0 の完了基準（ここまでできればOK）

* [x] 代表フォント 3〜5個で、上記ロジックを実装して動く状態
* [x] Canvasベースの文字特徴量自動判定を実装
* [x] 実際の描画領域に基づく計算を実装
* [x] 全体トラッキング調整機能を実装
* [ ] デザイナーが10〜20パターンの名字を入れて確認
  → 「明らかにおかしい例」が大きく減っている
* [ ] 「修正ゼロ」ではなくても
  → 「毎回ゼロから調整」ではなく「微調整スタート」に変わっている

ここまで行けば：

> 「ロジックだけで、どのくらいまで行けるか」
> 「学習を入れる価値がどのくらいありそうか」

が**現物ベースで見える**ので、
Phase1 の投資判断（やる価値ある / なし）ができる状態になります。

---


