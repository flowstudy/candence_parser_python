import time

import sql_appbk
import cadence_parser

PARSER = cadence_parser.CadenceParser()



def process():

    sql = """
        SELECT id,contract_address,contract_name,contract_code FROM flow_code WHERE  is_structed=0 limit 20
        """
    flow_code = sql_appbk.mysql_com(sql)
    if 0 == len(flow_code):
        print("sleep。。。。。。。。。。。。。。。。。。")
        time.sleep(60 * 60)
        return 0

    for item in flow_code:
        contract_code = item['contract_code']
        print("process contract-------", item['contract_address'], item['contract_name'])

        try:
            result_list = PARSER.process(contract_code) # 解析代码
        except Exception as e:
            print("ERROR", e) # 解析失败，也做标记位-1
            sql_update = """
                    update flow_code set is_structed=-1 where id = {}
                    """.format(item["id"])
            sql_appbk.mysql_com(sql_update)
            continue


        data_list = []
        for sub_item in result_list: # 给节点添加合约地址和合约名称
            data = {}
            data['contract_address'] = item['contract_address']
            data['contract_name'] = item['contract_name']
            data["struct_type"] = sub_item["Type"]
            data["notion"] = sub_item["notion"]
            data["code_text"] = sub_item["code_text"]
            data["start_pos"] = sub_item["start_pos"]
            data["end_pos"] = sub_item["end_pos"]
            data["start_line"] = sub_item["start_line"]
            data_list.append(data)
        # 插入数据库
        sql_appbk.insert_data_list(data_list, "flow_code_parser")


        sql_update = """
                update flow_code set is_structed=1 where id = {}
                """.format(item["id"])
        sql_appbk.mysql_com(sql_update)
    return 0

if __name__ == "__main__":
    while 1:
        process()