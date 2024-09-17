import csv

def convert_csv_to_dat(input_file, output_file):
    with open(input_file, 'r', newline='') as csvfile, open(output_file, 'w') as datfile:
        csv_reader = csv.DictReader(csvfile)
        
        # ヘッダー行を書き込む
        datfile.write("   No          kyori     Lkata     Rkata        RN          data\n")
        
        for row in csv_reader:
            try:
                formatted_line = (
                    f"{int(row['no']):>5}"
                    f"{float(row['kyori']):>15.3f}"
                    f"{float(row['Lkata']):>10.3f}"
                    f"{float(row['Rkata']):>10.3f}"
                    f"{float(row['RN']):>10.4f}"
                    f"          {row['data']}"  # dataフィールドを左詰めにし、前に10個の空白を追加
                )
                datfile.write(formatted_line + '\n')
            except (ValueError, KeyError) as e:
                print(f"警告: 行 {row} の変換中にエラーが発生しました: {e}. スキップします。")

# 使用例
input_csv = '1Ddmn.csv'
output_dat = '1Ddmn.dat'

convert_csv_to_dat(input_csv, output_dat)
print(f"変換が完了しました。出力ファイル: {output_dat}")