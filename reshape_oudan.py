# make adjust oudan csv by d.baba 24.08

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# input oudan csv folder path
oudan_folder = 'Takatoki_2022/oudan'

# get output oudan csv folder
output_folder = f'{oudan_folder}/adjust_unst_oudan'
output_folder_iric = f'{oudan_folder}/adjust_oudan2'
# set output folder
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
if not os.path.exists(output_folder_iric):
    os.makedirs(output_folder_iric)

# check output oudan graph
# (Valid(all show display):1, Valid(Not show display):2, else(not check):else)
check_graph = 2

# get oudan list
file_list = list(map(lambda x: x.replace('\\','/'), 
                     glob.glob(oudan_folder+'/*.csv')))

# function
# find riverbed id
def find_index(listdata, value):
    index = min(range(len(listdata)), key=lambda i: abs(listdata.iloc[i]-value))
    return index

# pick right and left id
def pick_id(xlist, ylist):
    # get x range(center)
    if xlist.iloc[0] == (xlist.iloc[-1] * -1):
        x_left_range = xlist.iloc[0] * 1/2
        x_right_range = xlist.iloc[0] * 1/2
    elif xlist.iloc[0] < 0 and xlist.iloc[-1] < 0:
        x_left_range = (xlist.iloc[0] + xlist.iloc[-1]) * 3/4
        x_right_range = (xlist.iloc[0] + xlist.iloc[-1]) * 1/4
    elif xlist.iloc[0] < 0 and xlist.iloc[-1] > 0:
        x_left_range = xlist.iloc[0] + (abs(xlist.iloc[0]) + xlist.iloc[-1]) * 1/4
        x_right_range = xlist.iloc[-1] - (abs(xlist.iloc[0]) + xlist.iloc[-1]) * 1/4
    else:
        x_left_range = (xlist.iloc[0] + xlist.iloc[-1]) * 1/4
        x_right_range = (xlist.iloc[0] + xlist.iloc[-1]) * 3/4
    # get riverbet range
    riverbed_range = ylist.iloc[find_index(xlist, x_left_range):find_index(xlist, x_right_range)+1]
    # get riverbet id
    riverbed = min(riverbed_range)
    riverbed_ids = [i for i, y in enumerate(ylist) if y == riverbed]
    if len(riverbed_ids) >1:
        riverbed_id = int((max(riverbed_ids) + min(riverbed_ids)) / 2)
    else:
        riverbed_id = riverbed_ids[0]
    # get right and left emb
    y_left_emb = max(ylist.iloc[:riverbed_id])
    y_right_emb = max(ylist.iloc[riverbed_id+1:])
    y_left_emb_ids = [i for i, y in enumerate(ylist.iloc[:riverbed_id]) if y == y_left_emb]
    y_right_emb_ids = [i for i, y in enumerate(ylist.iloc[riverbed_id+1:]) if y == y_right_emb]
    if len(y_left_emb_ids) > 1:
        y_left_emb_id = max(y_left_emb_ids)
    else:
        y_left_emb_id = y_left_emb_ids[0]
    if len(y_right_emb_ids) > 1:
        y_right_emb_id = min(y_right_emb_ids) + riverbed_id +1
    else:
        y_right_emb_id = y_right_emb_ids[0] + riverbed_id +1
    return y_left_emb_id, y_right_emb_id

def identify(file):
    with open(file, 'r') as f:
        # get label as str list
        label = f.readline().strip().split(',')
        # get data(xy) as str list
        data = [line.strip().split(',') for line in f]

        df = pd.DataFrame(data, columns=None)
        df.iloc[:, 0] = 0  # set zero
        # pick xy
        x = df.iloc[:,1].astype(float)
        y = df.iloc[:,2].astype(float)
        left, right = pick_id(x, y)
        x_left = x[left]
        x_right = x[right]
        adjust_df = df.iloc[left:right+1,:].reset_index(drop=True)
    return df, adjust_df, left, right, x_left, x_right, label

temp_list = []
for file in file_list:
    line_data = []
    file_name = os.path.splitext(file.split('/')[-1])[0]
    print(f'---{file_name}---')
    before, after, left, right, x_left, x_right, label= identify(file)
    print(left, right)
    # For UNST(data(oudan))
    output_path = output_folder + f'/{file_name}.csv'
    line_data = [file_name, x_left, x_right, output_path]
    temp_list.append(line_data)
    before.to_csv(output_path, index=False, header=False)

    # For iRIC 
    output_path_iric = output_folder_iric + f'/{file_name}.csv'
    label[6] = str(int(len(after)))
    with open(output_path_iric, 'w') as opt:
        opt.write(','.join(label)+'\n')
        after.to_csv(opt, index=False, header=False, na_rep='', lineterminator='\n')

    # check
    if check_graph == 1 or check_graph == 2:
        # make graph
        x = before.iloc[:,1].astype(float)
        y = before.iloc[:,2].astype(float)
        x_filtered = after.iloc[:,1].astype(float)
        y_filtered = after.iloc[:,2].astype(float)
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, marker='o', linestyle='-', color='b', label='before')
        plt.plot(x_filtered, y_filtered, marker='o', linestyle='-', color='r', label='after')

        # set label etc
        plt.title(f'{output_path_iric}')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()

        # show graph
        plt.grid(True)
        chk_file = file_name+'.png'
        plt.savefig(f'chk3/{chk_file}')
        if check_graph == 1:
            plt.show()

# For UNST(1Ddmn.dat)
df_1d = pd.DataFrame(temp_list, columns=['kyori', 'Lkata', 'Rkata', 'data'])
df_1d['sort_kp'] = df_1d['kyori'].astype(float)
df_1d.insert(3, 'RN', '{:.4f}'.format(0.0300))
df_1d = df_1d.sort_values(['sort_kp'],ascending=False).reset_index(drop=True)
df_1d = df_1d.drop(columns=['sort_kp'])
df_1d.index = df_1d.index + 1
print(df_1d)
df_1d.to_csv('chk3.csv')