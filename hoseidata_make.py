## 08 - 0906 coded by k.yama
"""_summary_
各断面で水深が0.1m上がるごとの断面積、潤辺、水面幅を計算
"""


import numpy as np
import pandas as pd
import os

def interpolate(x1, y1, x2, y2, y):
    """2点間の直線とy座標の交点のx座標を求める"""
    return x1 + (x2 - x1) * (y - y1) / (y2 - y1)

def calculate_segment(x1, y1, x2, y2, water_level):
    """セグメントの面積と長さを計算"""
    if y1 <= water_level and y2 <= water_level:
        # 両点が水面下
        return 0.5 * (x2 - x1) * (2 * water_level - y1 - y2), ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    elif y1 > water_level and y2 > water_level:
        # 両点が水面上
        return 0, 0
    else:
        # 片方が水面上、もう片方が水面下
        x_intersect = interpolate(x1, y1, x2, y2, water_level)
        if y1 <= water_level:
            area = 0.5 * (x_intersect - x1) * (water_level - y1)
            length = ((x_intersect - x1)**2 + (water_level - y1)**2)**0.5
        else:
            area = 0.5 * (x2 - x_intersect) * (water_level - y2)
            length = ((x2 - x_intersect)**2 + (water_level - y2)**2)**0.5
        return area, length


def calculate_section_properties(x, y, water_depth, min_y):
    """
    指定された水深での断面積、潤辺、水面幅を計算します。
    複雑な断面形状に対応するように改善されています。
    """
    water_level = min_y + water_depth
    # 水面下の点を特定
    underwater_indices = [i for i, yi in enumerate(y) if yi <= water_level]

    if not underwater_indices:
        return 0, 0, 0  # 水面下の点がない場合

    i = underwater_indices[0]
    j = underwater_indices[-1]

    # 計算に関連する点のリスト(水面下の点の両端から1点ずつ外側に広げたもの)を作成
    relevant_indices = list(range(max(0, i-1), min(len(x), j+2)))
    area = 0
    wetted_perimeter = 0

    # 各セグメントの面積と長さを計算
    for k in range(len(relevant_indices) - 1):
        idx1, idx2 = relevant_indices[k], relevant_indices[k+1]
        segment_area, segment_length = calculate_segment(x[idx1], y[idx1], x[idx2], y[idx2], water_level)
        area += segment_area
        wetted_perimeter += segment_length

    # 水面幅を計算
    ii = interpolate(x[relevant_indices[0]], y[relevant_indices[0]], x[relevant_indices[1]], y[relevant_indices[1]], water_level)
    jj = interpolate(x[relevant_indices[-2]], y[relevant_indices[-2]], x[relevant_indices[-1]], y[relevant_indices[-1]], water_level)
    surface_width = jj - ii

    return area, wetted_perimeter, surface_width


def process_section(row, base_path):
    """各断面に対する処理を行います。"""
    # dataフィールドが'data'だけの場合はスキップ
    if row['data'].strip().lower() == 'data':
        print(f"警告: 行 {row['No']} のデータフィールドが無効です。スキップします。")
        return None

    section_file = os.path.join(base_path, row['data'].strip())
    print(f"デバッグ: 読み込もうとしているファイル: {section_file}")
    
    try:
        section_df = pd.read_csv(section_file, header=None, names=['x', 'y'])
    except FileNotFoundError:
        print(f"警告: ファイル {section_file} が見つかりません。この断面をスキップします。")
        return None
    except pd.errors.EmptyDataError:
        print(f"警告: ファイル {section_file} が空です。この断面をスキップします。")
        return None
    
    lkata, rkata = float(row['Lkata']), float(row['Rkata'])
    filtered_df = section_df[(section_df['x'] >= lkata) & (section_df['x'] <= rkata)]
    
    if filtered_df.empty:
        print(f"警告: 断面 {row['No']} にデータがありません。この断面をスキップします。")
        return None
    
    min_y = filtered_df['y'].min()
    max_y = filtered_df['y'].max()
    water_depths = np.arange(0, max_y - min_y + 0.1, 0.1)
    
    areas = []
    perimeters = []
    surface_widths = []
    for depth in water_depths:
        area, perimeter, surface_width = calculate_section_properties(filtered_df['x'].values, filtered_df['y'].values, depth, min_y)
        areas.append(area)
        perimeters.append(perimeter)
        surface_widths.append(surface_width)
    
    roughness = [0.03] * len(water_depths)  # 粗度データを追加
    
    return int(row['No']), float(row['kyori']), min_y, water_depths, areas, perimeters, surface_widths, roughness

def write_results_to_files(results, output_path):
    output_files = {
        'hahosei.dat': '断面積データ',
        'hshosei.dat': '潤辺データ',
        'hrhosei.dat': '径深データ',
        'saisin.dat': '最深河床高データ',
        'suishin.dat': '水深データ',
        'suimenhaba.dat': '水面幅データ',
        'soudodata.dat': '粗度データ'
    }
    
    for filename, description in output_files.items():
        filepath = os.path.join(output_path, filename)
        try:
            with open(filepath, 'w') as f:
                if filename == 'saisin.dat':
                    for result in results:
                        if result is not None:
                            no, kyori, min_y, _, _, _, _, _ = result
                            f.write(f"{no:5d}{kyori:10.3f}{min_y:10.3f}\n")
                else:
                    for result in results:
                        if result is not None:
                            no, _, _, water_depths, areas, perimeters, surface_widths, roughness = result
                            f.write(f"{no:3d}{len(water_depths):10d}\n")
                            if filename == 'hahosei.dat':
                                data = areas
                            elif filename == 'hshosei.dat':
                                data = perimeters
                            elif filename == 'hrhosei.dat':
                                data = [a / p if p else 0 for a, p in zip(areas, perimeters)]
                            elif filename == 'suishin.dat':
                                data = water_depths
                            elif filename == 'suimenhaba.dat':
                                data = surface_widths
                            elif filename == 'soudodata.dat':
                                data = roughness
                            
                            for i in range(0, len(data), 10):
                                f.write(' '.join([f"{d:10.3f}" for d in data[i:i+10]]) + '\n')
            print(f"{description}を {filepath} に書き込みました。")
        except IOError as e:
            print(f"エラー: {filepath} への書き込み中にエラーが発生しました: {e}")

def main():
    base_path = './'  # 実際のベースパスを入力
    dmn_file = os.path.join(base_path, '1Ddmn.dat')
    
    try:
        # ヘッダー行をスキップするオプションを追加
        dmn_df = pd.read_csv(dmn_file, sep=r'\s+', names=['No', 'kyori', 'Lkata', 'Rkata', 'RN', 'data'], skiprows=1)
    except FileNotFoundError:
        print(f"エラー: ファイル {dmn_file} が見つかりません。")
        return
    except pd.errors.EmptyDataError:
        print(f"エラー: ファイル {dmn_file} が空です。")
        return
    
    results = []
    for _, row in dmn_df.iterrows():
        try:
            result = process_section(row, base_path)
            if result is not None:
                results.append(result)
        except Exception as e:
            print(f"警告: 断面 {row['No']} の処理中にエラーが発生しました: {e}")
    
    write_results_to_files(results, base_path)

if __name__ == "__main__":
    main()