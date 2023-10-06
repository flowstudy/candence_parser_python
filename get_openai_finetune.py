import json

import sql_appbk
import hashlib

sql = """
select * from flow_code_parser where length(notion)>1 limit 10
"""
result = sql_appbk.mysql_com(sql)

#去重处理，如果notion和code_text都相同，则认为是重复的
notion_code_dict = {} #key=md5(notion+code_text), value=1
data_list = []

for item in result:
    notion = item['notion']
    code_text = item['code_text']
    text = notion+code_text
    str_md5 = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()
    if str_md5 not in notion_code_dict:
        data = {
            "input": notion,
            "output": code_text
        }
        data_list.append(data)
        notion_code_dict[str_md5] = 1 #添加到词典


print(json.dumps(data_list, indent=4, ensure_ascii=False))

