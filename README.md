# make_hahr
# 1次元河道の設定に必要なデータ作成（hahosei.dat、hrhosei.dat）

河道断面の水が流れる範囲を指定して、その範囲における断面積や径深を計算します。

## ①断面データの整理

1次元河道に設定する河道断面から、水が流下する範囲（X位置座標）を設定。

（例）水が流下する範囲について、左岸側、右岸側それぞれを測量点（●）から設定する
- 左岸側：Lkata
- 右岸側：Rkata

図　河道断面における水が流れる範囲の設定例

### 1Ddmn.dat

- No：断面の通し番号（上流⇒下流）。複数の河川をまとめて番号を付ける。
- Kyori：測量の距離標の表示。（DioVISTAでは"KPID7.035"となり、これを7.035へ）
- Lkata、Rkata：水が流れる範囲のX位置座標。
- RN：粗度係数。河川整備計画や浸水想定区域図報告書等に記載ある可能性あり。
- Data：河道断面の測量データ保存パス

### 河道断面の測量データ（xx.csv）

- B列：X座標値
- C列：Y座標値
- ファイル名（xxの部分）は、何でもOK。1Ddmn.datのパスに記載できていれば可。

## ②hahosei.dat、hrhosei.datの作成

1. make_hoseidata.pyを実行
2. 1Ddmn.dat保存場所、hahosei.dat等の出力場所を指定する


---
# 処理の解説
### interpolate関数の説明

```python
def interpolate(x1, y1, x2, y2, y):
    return x1 + (x2 - x1) * (y - y1) / (y2 - y1)
```



```bash
y2 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ (x2, y2)
   │               ／│
   │            ／   │
   │         ／      │
 y ─ ─ ─ ─ * ─ ─ ─ ─ │ ← We want to find this x-coordinate
   │     ／          │
   │  ／             │
   │／                │
y1 (x1, y1) ─ ─ ─ ─ ─ ┘
   │                  │
   x1                 x2
```

1. slope = (y2 - y1) / (x2 - x1)
2. (y - y1) = slope * (x - x1)
3. (y - y1) = ((y2 - y1) / (x2 - x1)) * (x - x1)
4. (y - y1) * (x2 - x1) = (y2 - y1) * (x - x1)
5. (y - y1) * (x2 - x1) = (y2 - y1) * x - (y2 - y1) * x1
6. (y - y1) * (x2 - x1) + (y2 - y1) * x1 = (y2 - y1) * x
7. ((y - y1) * (x2 - x1) / (y2 - y1)) + x1 = x
8. x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)



### calculate_segment関数の説明


- 両点が水面下の場合
```bash
water_level  - - - - - - - - - - - - - - 
               |                       |
               |                       |
               |                       |
y1 - - - - - - +                       |
               |                       |
               |                       |
y2 - - - - - - - - - - - - - - - - - - +
               |                       |
               x1                      x2
```

```python
if y1 <= water_level and y2 <= water_level:
   # 両点が水面下
   return 0.5 * (x2 - x1) * (2 * water_level - y1 - y2)
```
- 台形：((water_level - y1) + (water_level - y2)) * (x2 - x1) * 0.5


- 片方が水面上、片方が水面下
```bash
               |
               |
y1 - - - - - - +
               |    /
               |   /
water_level  - - -/- - - - - - - - - - -
               | /
               |/
y2 - - - - - - +
               |
               x1                      x2
```

```python
   if y1 <= water_level:
      area = 0.5 * (x_intersect - x1) * (water_level - y1)
```


- 三角形の公式
