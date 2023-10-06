import json
import time
import requests

def get_code_text(contract_code):
    #url = "http://127.0.0.1:8080/parse"
    url =  "http://8.218.127.18:8080/parse"
    ret = requests.post(url, data=contract_code)
    parse_data = ret.json()
    return parse_data

declaration_full_list = []

def parse(declaration_list):
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
        declaration_full_list.append(data)

        #递归解析
        if "Members" in declaration and "Declarations" in declaration["Members"]: #递归条件
            sub_node = declaration["Members"]["Declarations"]
            if sub_node:
                parse(sub_node)


def get_notion(ori_code, declaration):
    ori_code_line_list = ori_code.split("\n")
    start_line = declaration["start_line"] #开始行号
    #从开始行向前取开头为"//"的行，直到取到非"//"开头的行或者行号为0
    notion_list = []
    for i in range(start_line-1, -1, -1):
        line = ori_code_line_list[i].strip()
        print("line-----", line)
        if 0 == line.find("//"):
            notion_list.append(line[2:].strip().replace("/", ""))
        else:
            break

    notion_list.reverse() #反转
    return "\n".join(notion_list)

#抽取代码和注释
def extract_code_notion(ori_code, declaration_list):
    for declaration in declaration_list:
        #抽取代码
        start_pos = declaration["start_pos"]
        end_pos = declaration["end_pos"] + 1
        code_text = ori_code[start_pos:end_pos]
        declaration["code_text"] = code_text

        #抽取注释
        notion = get_notion(ori_code, declaration)
        declaration["notion"] = notion


if __name__ == '__main__':
    #code = "pub contract FlowToken {}"
    code = """
    pub contract HelloWorld {
      // Declare a public field of type String.
      pub var greeting: String
    }
    """
    #code = open("hello.cdc", "r").read()
    code = open("FungibleToken.cdc", "r").read()

    parse_data = get_code_text(code)
    print(json.dumps(parse_data))
    parse(parse_data["program"]["Declarations"])
    #
    # print("declaration_full_list:", declaration_full_list)
    #
    extract_code_notion(code, declaration_full_list)

    print(json.dumps(declaration_full_list))
    # print(code[103:108+1])
    # print(code)