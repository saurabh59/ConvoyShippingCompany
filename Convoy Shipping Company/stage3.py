import pandas as pd
import csv
import sqlite3
import json

print("Input file name:")
file_name = input()
if (".csv" in file_name or ".xlsx" in file_name) and "[CHECKED]" not in file_name:
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
if "[CHECKED]" in file_name:
    file_name_no_ext = file_name.replace('[CHECKED]', "")
    if ".csv" in file_name_no_ext:
        file_name_no_ext = file_name_no_ext.replace(".csv", "")
    else:
        file_name_no_ext = file_name_no_ext.replace(".xlsx", "")
if ".s3db" in file_name:
    file_name_no_ext = file_name.replace(".s3db", "")
else:
    conn = sqlite3.connect(f'{file_name_no_ext}.s3db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS convoy;')
    count = 0

    with open(f'{file_name_no_ext}[CHECKED].csv', 'r') as checked_csv:
        file_reader = csv.reader(checked_csv, delimiter=',', lineterminator='\n')
        for line in file_reader:
            if count == 0:
                headers = tuple(line)
                cursor.execute(f'create table convoy( {line[0]} int primary key, {line[1]} int not null, {line[2]} int not null, {line[3]} int not null);')
                count = 1
            else:
                values = tuple(line)
                cursor.execute(f'insert into convoy {headers} values {values};')
                count += 1
    conn.commit()
    if (count - 1) <= 1:
        print(f'{count - 1} record was inserted into {file_name_no_ext}.s3db')
    else:
        print(f'{count - 1} records were inserted into {file_name_no_ext}.s3db')
count = 0
conn = sqlite3.connect(f'{file_name_no_ext}.s3db')
ek_hai = dict()
database = pd.read_sql_query('select * from convoy', con=conn)
js = database.to_json(f"{file_name_no_ext}.json", orient="records")
with open(f'{file_name_no_ext}.json', 'r') as json_file:
    new_file = json.load(json_file)
    ek_hai['convoy'] = new_file
with open(f'{file_name_no_ext}.json', 'w') as json_file:
    json.dump(ek_hai, json_file)
if len(new_file) <= 1:
    print(f"{len(new_file)} vehicle was saved into {file_name_no_ext}.json")
else:
    print(f"{len(new_file)} vehicles were saved into {file_name_no_ext}.json")


