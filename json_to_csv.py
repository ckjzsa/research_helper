import csv
import json


def transcsv(jsonpath, csvpath):
    json_file = open(jsonpath, 'r', encoding='utf8')
    csv_file = open(csvpath, 'w', newline='', encoding='gbk', errors='ignore')
    writer = csv.writer(csv_file)
    #读文件
    ls = json.load(json_file)
    data = [list(ls.keys())]
    for item in ls:
        data.append(ls[item])  # 获取每一行的值value

    #写入文件
    header = ["标题", "中文标题", "第一作者", "通讯作者", "第一单位", "链接"]
    writer.writerow(header)
    for line in data[1:]:
        writer.writerow(line)
    #关闭文件
    json_file.close()
    csv_file.close()
