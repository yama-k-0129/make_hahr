# make_hahr
UNST ---ha.dat, hr.dat making program

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
