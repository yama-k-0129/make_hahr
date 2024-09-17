### make 1d data by d.baba 24.09

'''
コード実行前の事前処理(iRIC上の処理)
堤内地測点の除去(左岸天端~右岸天端までの測点に調整)
iRIC出力形式のrivファイルまたはcsvまたはtxtファイルを出力
（kuiの中央座標も併せて出力されるrivファイル推奨。）
'''

import os
import pandas as pd

## input ##
# select use input data format
    ## output by iRIC(specify the left and right levee)
        # 0:csv or txt
        # 1:riv
        # 2:xml(Under development...)
    ## oudansokuryo(kui & oudan(folder), iRIC format)(Under development...)
        # else:csv or txt(specify the left and right levee)
input_format = 0

# input path(if you select input format = 5, Write the folder path)
river_data = 'kusano_del2.csv'

## output ##
# output path(folder)
output_folder = 'test2'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def read_csvdata(river_data, output_folder):
    kyori = []
    coords = []
    dmn = []
    paths = []
    with open(river_data, 'r') as f:
        for line in f:
            xy = line.strip().split(',')
            if len(coords) == 1:
                kp = xy[0]
                kyori.append(kp)
            if not xy[0] == '':
                coords.append((xy[2], xy[3]))
            else:
                df = coords_to_df(coords)
                dmn.append((df.iloc[0,1], df.iloc[-1,1]))
                output_path = f'{output_folder}/{str(kp)}.csv'
                paths.append(output_path)
                df.to_csv(output_path, header=False, index=False)
                coords = []
        df_dmn = pd.DataFrame(dmn, columns=['Lkata', 'Rkata'])
        df_dmn.insert(0, 'kyori', kyori)
        df_dmn.insert(3, 'RN', 0.030)
        df_dmn.insert(4, 'data', paths)
        df_dmn.index = df_dmn.index + 1
        df_dmn.to_csv('1Dmn2.csv')

def read_rivdata(river_data, output_folder):
    out = 0
    kyori = []
    dmn = []
    paths = []
    with open(river_data, 'r') as f:
        for line in f:
            kui = line.strip().split()
            if not kui:
                continue
            kyori.append(kui[0])
            if '#x-section' in line:
                oudan_num = len(kyori) - 2
                break
        print(f'断面数は" {oudan_num} "')
        while out < oudan_num:
            header = f.readline().strip().split()
            if not header:
                continue
            data = []
            while len(data) < (int(header[1]) * 2):
                xy = f.readline().split()
                if not xy:
                    continue
                data.extend(map(float, xy))
            coords = []
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    coords.append((data[i], data[i+1]))
            df = coords_to_df(coords)
            dmn.append((df.iloc[0,1], df.iloc[-1,1]))
            output_path = f'{output_folder}/{str(header[0])}.csv'
            paths.append(output_path)
            df.to_csv(output_path, header=False, index=False)
            out += 1
        df_dmn = pd.DataFrame(dmn, columns=['Lkata', 'Rkata'])
        df_dmn.insert(0, 'kyori', kyori[1:-1])
        df_dmn.insert(3, 'RN', 0.030)
        df_dmn.insert(4, 'data', paths)
        df_dmn.index = df_dmn.index + 1
        df_dmn.to_csv('1Dmn.csv')

# def read_xmldata():


def coords_to_df(coords):
    df = pd.DataFrame(coords, columns=['x', 'y'])
    df.insert(0, 'Zero', 0)
    for r in range(1, 13):
        df[f'{r}'] = None
    return df

if input_format == 0:
    read_csvdata(river_data, output_folder)
elif input_format == 1:
    read_rivdata(river_data, output_folder)
#elif input_format == 2:
#    read_xmldata(river_data, output_folder)



                



            

            
