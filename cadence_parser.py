import json
import time
import requests

class CadenceParser():
    def __init__(self):
        self.url = "http://8.218.127.18:8080/parse" #cadence解析器地址
        self.declaration_full_list = [] #全局变量，存储解析结果

    def get_code_text(self, contract_code):
        """
        获取代码解析结果
        :param contract_code: 原始合约代码
        :return: 解析结果
        """
        ret = requests.post(self.url, data=contract_code.encode("utf-8"))
        parse_data = ret.json()
        return parse_data

    def parse(self, declaration_list):
        """
        解析代码
        :param declaration_list: 原始的解析结果
        :return: 用来递归调用
        """
        for declaration in declaration_list:
            data = {
                "Type": declaration["Type"],
                #"CompositeKind": declaration["CompositeKind"],
                #"Identifier": declaration["Identifier"]["Identifier"],
                "start_pos": declaration["StartPos"]["Offset"],
                "end_pos": declaration["EndPos"]["Offset"],
                "start_line": declaration["StartPos"]["Line"]-1, #开始行号,从1开始
            }
            #print(data)
            self.declaration_full_list.append(data)

            #递归解析
            if "Members" in declaration and "Declarations" in declaration["Members"]:
                sub_node = declaration["Members"]["Declarations"]
                if sub_node:
                    self.parse(sub_node)

    def get_notion(self, ori_code, declaration):
        """
        获得注释
        :param ori_code: 原始代码
        :param declaration: 实体
        :return: 注释
        """
        ori_code_line_list = ori_code.split("\n")
        start_line = declaration["start_line"]
        notion_list = []
        for i in range(start_line-1, -1, -1):
            line = ori_code_line_list[i].strip()
            if 0 == line.find("//"):
                notion_list.append(line[2:].strip())
            else:
                break

        notion_list.reverse()
        return "\n".join(notion_list)

    def extract_code_notion(self, ori_code, declaration_list):
        """
        获得全部实体的代码和注释
        :param ori_code: 原始代码
        :param declaration_list: 实体列表
        :return:
        """
        for declaration in declaration_list:
            #抽取代码
            start_pos = declaration["start_pos"]
            end_pos = declaration["end_pos"] + 1
            code_text = ori_code[start_pos:end_pos]
            declaration["code_text"] = code_text

            #抽取注释
            notion = self.get_notion(ori_code, declaration)
            declaration["notion"] = notion

    def process(self, code):
        self.declaration_full_list = [] #清空全局变量先
        parse_data = self.get_code_text(code)
        if "program" in parse_data and "Declarations" in parse_data["program"]:
            declaration_list = parse_data["program"]["Declarations"]
            self.parse(declaration_list)
            self.extract_code_notion(code, self.declaration_full_list)
            return self.declaration_full_list
        else:
            return None

if __name__ == "__main__":
    code = "pub contract FlowToken {}"
    parser = CadenceParser()
    ret = parser.process(code)
    print(ret)