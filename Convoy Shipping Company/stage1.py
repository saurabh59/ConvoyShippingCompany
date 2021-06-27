import pandas as pd
import csv


print("Input file name:")
file_name = input()
if file_name[-4:] == "xlsx":
    k = pd.read_excel(fr'{file_name}', sheet_name="Vehicles", dtype=str)
    file_name_no_ext = f'{file_name.replace(".xlsx", "")}'
    k.to_csv(f'{file_name_no_ext}.csv', index=False)
    if k.shape[0] <= 1:
        print(f'{k.shape[0]} line was imported to {file_name_no_ext}.csv')
    else:
        print(f'{k.shape[0]} lines were imported to {file_name_no_ext}.csv')
else:
    file_name_no_ext = f'{file_name.replace(".csv", "")}'
count = 0
cell_count = 0
with open(f'{file_name_no_ext}.csv', "r") as csv_read_file, open(f'{file_name_no_ext}[CHECKED].csv', 'w') as csv_write_file:
    file_reader = csv.reader(csv_read_file, delimiter=",", lineterminator="\n")
    file_writer = csv.writer(csv_write_file, delimiter=",", lineterminator="\n")
    for line in file_reader:
        if count == 0:
            file_writer.writerow(line)
            count = 1
        else:
            a_list = []
            for x in line:
                if x.isdigit():
                    a_list.append(x)
                else:
                    j = "".join([y for y in x if y.isdigit()])
                    a_list.append(int(j))
                    cell_count += 1
            file_writer.writerow(a_list)
print(f'{cell_count} cells were corrected in {file_name_no_ext}[CHECKED].csv')