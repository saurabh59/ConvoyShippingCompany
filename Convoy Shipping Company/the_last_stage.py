import pandas as pd
import csv
import sqlite3
import json
from lxml import etree


def scoring_function(tank, fuel, load):
    tank = int(tank)
    fuel = int(fuel)
    load = int(load)
    total_fuel_consumption = fuel * (450 / 100)
    filling_station = total_fuel_consumption / tank
    score = 0
    if filling_station > 2:
        score += 0
    elif filling_station < 1:
        score += 2
    else:
        score += 1
    if load > 20:
        score += 2
    if total_fuel_consumption <= 230:
        score += 2
    elif total_fuel_consumption > 230:
        score += 1
    return score


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
                the_column = 'score'
                line = line + ['score']
                headers = tuple(line)
                cursor.execute(f'create table convoy( {line[0]} int primary key, {line[1]} int not null, {line[2]} int not null, {line[3]} int not null, {the_column} int not null);')
                count = 1
            else:
                line = line + [scoring_function(line[1], line[2], line[3])]
                values = tuple(line)
                cursor.execute(f'insert into convoy {headers} values {values};')
                count += 1
    conn.commit()
    if (count - 1) <= 1:
        print(f'{count - 1} record was inserted into {file_name_no_ext}.s3db')
    else:
        print(f'{count - 1} records were inserted into {file_name_no_ext}.s3db')
count = 0
xml_count = 0
json_count = 0
conn = sqlite3.connect(f'{file_name_no_ext}.s3db')
database = pd.read_sql_query('select * from convoy', con=conn)
string = '<convoy>'
for y in range(len(database)):
    if database.score[y] > 3:
        ek_hai = dict()
        filtered_database = database[database['score'] > 3]
        del filtered_database['score']
        js = filtered_database.to_json(f"{file_name_no_ext}.json", orient="records")
        with open(f'{file_name_no_ext}.json', 'r') as json_file:
            new_file = json.load(json_file)
            ek_hai['convoy'] = new_file
        with open(f'{file_name_no_ext}.json', 'w') as json_file:
            json.dump(ek_hai, json_file)
        json_count += 1
    else:
        string += f'\n\t<vehicle>\n\t\t<vehicle_id>{database.vehicle_id[y]}</vehicle_id>' \
                  f'\n\t\t<engine_capacity>{database.engine_capacity[y]}</engine_capacity>' \
                  f'\n\t\t<fuel_consumption>{database.fuel_consumption[y]}</fuel_consumption>' \
                  f'\n\t\t<maximum_load>{database.maximum_load[y]}</maximum_load>' \
                  f'\n\t</vehicle>'
        xml_count += 1

string += '\n</convoy>'
root = etree.fromstring(string)
tree = root.getroottree()
tree.write(f'{file_name_no_ext}.xml')


if json_count <= 1:
    print(f"{json_count} vehicle was saved into {file_name_no_ext}.json")
else:
    print(f"{json_count} vehicles were saved into {file_name_no_ext}.json")
if xml_count < 1:
    string = '<convoy>'
    string += '\n</convoy>'
    root = etree.fromstring(string)
    tree = root.getroottree()
    tree.write(f'{file_name_no_ext}.xml')
    print(f"{xml_count} vehicles were saved into {file_name_no_ext}.xml")
elif xml_count == 1:
    print(f"{xml_count} vehicle was saved into {file_name_no_ext}.xml")
else:
    print(f"{xml_count} vehicles were saved into {file_name_no_ext}.xml")