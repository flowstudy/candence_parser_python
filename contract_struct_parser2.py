import json
import time
import requests
import sql_appbk
# get_code_text 配置url地址

"""
功能：通过代码原结构，解析Identifier/Identifiers，获得代码块的EndPos
输入：declaration_node Declarations其中的一个node
返回：end_pos
"""
def parse_declaration_end_pos(declaration_node):
    if "EndPos" in declaration_node:
        end_pos = declaration_node["EndPos"]['Line']
    return end_pos

"""
功能：通过代码原结构，解析Identifier/Identifiers，获得代码块的StartPos
输入：declaration_node Declarations其中的一个node
返回：start_pos
"""
def parse_declaration_start_pos(declaration_node):
    if "StartPos" in declaration_node:
        start_pos = declaration_node["StartPos"]['Line']
    return start_pos


"""
功能：通过代码原结构，解析Identifier/Identifiers，获得代码块的名称，struct_name
输入：declaration_node Declarations其中的一个node
返回：struct_name,list 
"""
def parse_declaration_struct_name(declaration_node):
    if "Identifier" in declaration_node:
        struct_name = declaration_node["Identifier"]["Identifier"]
    # elif "Identifiers" in declaration_node and declaration_node["Identifiers"]!=None:
    #     struct_name = declaration_node["Identifiers"][0]["Identifier"]
    else:
        struct_name = "other"
    return struct_name

"""
功能：通过代码原结构，解析Declarations节点，获得代码块的类型，struct_type
输入：declaration_node Declarations其中的一个node
返回：struct_type,字符串类型，可能是，resource, fun, event，空字符串（表示没有match规则的类型）
"""
def parse_declaration_struct_type(declaration_node):
    # step1 1，如果包含CompositeKind 字段，值为CompositeKindResource 则
    # struct_type为resource。值为CompositeKindEvent 则struct_type为event。

    # 2，如果包含 type 字段，且 type字段的值为FunctionDeclaration
    # 则struct_type为函数fun。

    struct_type = ""
    if "CompositeKind" in declaration_node:
        if "CompositeKindContract" == declaration_node["CompositeKind"]:
            struct_type = "contract"
        elif "CompositeKindResource" == declaration_node["CompositeKind"]:
            struct_type = "resource"
        elif "CompositeKindEvent" == declaration_node["CompositeKind"]:
            struct_type = "event"
        # elif "CompositeKindStructure" == declaration_node["CompositeKind"]:
        # struct_type = "structure"
        #
        # elif "FunctionDeclaration" == declaration_node["type"]:
        #     struct_type = "fun"
        else:
            struct_type = "other"
    elif "Type" in declaration_node:
        if "FunctionDeclaration" == declaration_node["Type"]:
            struct_type = "fun"
        else:
            struct_type = "other"
        # elif
        # "FieldDeclaration" = declaration_node["Type"]
        #   struct_type = "Field"
    else:
        struct_type = "other"
    return struct_type


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type, 第二步 
输入:代码
返回:
"""
def process_declaration_node(declaration_node):

    # 分别调用函数，获取此节点的类型，名称，位置行号
    struct_type = parse_declaration_struct_type(declaration_node)
    struct_name = parse_declaration_struct_name(declaration_node)
    start_pos = parse_declaration_start_pos(declaration_node)
    end_pos = parse_declaration_end_pos(declaration_node)
    result_dic = {}
    result_dic["struct_type"] = struct_type
    result_dic["struct_name"] = struct_name
    result_dic["start_pos"] = start_pos
    result_dic["end_pos"] = end_pos
    return result_dic


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type,第一步 调用  找节点
输入:代码
返回:
"""
def parse_code(declaration_nodes):
    ret_list = []
    # 遍历code的declaration节点，逐个进行处理
    for declaration_node in declaration_nodes:
        # 非import类型才继续处理分析
        if declaration_node['Type'] != 'ImportDeclaration':
            # 调用函数解析一个节点内的数据
            # 最外层，第一层函数 一般只有一个
            result_dic = process_declaration_node(declaration_node)
            ret_list.append(result_dic)
            if "Members" in declaration_node and declaration_node["Members"]["Declarations"]:
                for declaration_node2 in declaration_node["Members"]["Declarations"]:
                    # 第二层
                    result_dic = process_declaration_node(declaration_node2)
                    ret_list.append(result_dic)
                    # 第三层
                    if "Members" in declaration_node2 and declaration_node2["Members"]["Declarations"]:
                        for declaration_node3 in declaration_node2["Members"]["Declarations"]:
                            # 第二层
                            result_dic = process_declaration_node(declaration_node3)
                            ret_list.append(result_dic)
    print(ret_list)
    return ret_list


"""
功能:递归go解析后的json各个节点
输入:代码
返回:
"""
ret_list = []

def parse_code2(declaration_nodes):

    if isinstance(declaration_nodes, dict):
        for ky, val in declaration_nodes.items():
            if ky == "Declarations" :
                for declaration in val:
                    result_dic = process_declaration_node(declaration)
                    ret_list.append(result_dic)
                    # result_dic = process_declaration_node(declaration_nodes)
                    parse_code2(declaration)
            elif ky == "Members":
                for declaration in val['Declarations']:
                    result_dic = process_declaration_node(declaration)
                    ret_list.append(result_dic)
                    # result_dic = process_declaration_node(declaration_nodes)
                    parse_code2(declaration)
    # print(ret_list)
    return ret_list



"""
功能：通过contract_code 代码 调用go服务，获取包含代码结构的code_text,
"""
def get_code_text(contract_code):
    url =  "http://127.0.0.1:8080/parse"
    # url =  "http://8.218.127.18:8080/parse"
    ret = requests.post(url, data=contract_code.encode('utf-8'))
    ret_text = ret.text
    if ret_text is None or ret_text == '':
        return "null"
    code_text = json.loads(ret_text)
    return code_text

"""
功能： 更新数据库
输入： 
返回： 
"""
def code_et():
    print("运行contract_struct_parse2....")
    global ret_list
    sql = """
    SELECT id,contract_address,contract_name,contract_code FROM `flow_code` WHERE contract_type = "contract" and is_structed = 0 limit 20
    """
    flow_code = sql_appbk.mysql_com(sql)
    if 0 == len(flow_code):
        time.sleep(60*60)
        print("sleep")
        return 0

    for item in flow_code:
        # print(item['contract_code'])
        # print(item["id"])
        # print("next contract_code ......printing...... ")
        contract_code_single = item['contract_code']

    # step1，E extract，所有东西都是etl，获得原始解析数据，从GO的服务中获取
        code_text = get_code_text(contract_code_single)

        if code_text != "null":
        # step2 T transform 解析原始数据代码，获得需要的数据结构信息
        #     declaration_nodes = code_text["program"]["Declarations"]

            result_list = parse_code2(code_text['program'])
            # result_list = parse_code2(declaration_nodes)
            for ret_dic in result_list:
                ret_dic['contract_address'] = item['contract_address']
                ret_dic['contract_name'] = item['contract_name']
            print(result_list)
                # sql_insert = """
                # INSERT INTO flow_code_struct (contract_address,contract_name,struct_type,struct_name,start_pos,end_pos) VALUES ("{}", "{}", "{}", "{}", "{}", "{}")
                # """.format(item['contract_address'], item['contract_name'], ret_dic['struct_type'], ret_dic["struct_name"], ret_dic['start_pos'], ret_dic['end_pos'])
                # insert_struct = sql_appbk.mysql_com(sql_insert)

            sql_appbk.insert_data_list(result_list, "flow_code_struct")
            ret_list = []


            sql_update = """
            update  `flow_code` set is_structed=1 where id = {}
            """.format(item["id"])
            sql_appbk.mysql_com(sql_update)
        else:
            # 解析后的code_text，有值为空的情况
            print("code_text is null")
    return 0


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type
输入:代码
返回:
"""
def process():
    while 1:
        code_et()

if __name__ == '__main__':
    declaration_node_text = """
    import FungibleToken from 0xf233dcee88fe0abe
    import NonFungibleToken from 0x1d7e57aa55817448
    import DapperUtilityCoin from 0xead892083b3e2c6c

    // Offers
    //
    // Contract holds the Offer resource and a public method to create them.
    //
    // Each Offer can have one or more royalties of the sale price that
    // goes to one or more addresses.
    //
    // Owners of NFT can watch for OfferAvailable events and check
    // the Offer amount to see if they wish to accept the offer.
    //
    // Marketplaces and other aggregators can watch for OfferAvailable events
    // and list offers of interest to logged in users.
    //
    pub contract Offers {
        // OfferAvailable
        // An Offer has been created and added to the users DapperOffer resource.
        //
        pub event OfferAvailable(
            offerAddress: Address,
            offerId: UInt64,
            nftType: Type,
            nftId: UInt64,
            offerAmount: UFix64,
            royalties: {Address:UFix64},
        )

        // OfferCompleted
        // The Offer has been resolved. The offer has either been accepted
        //  by the NFT owner, or the offer has been removed and destroyed.
        //
        pub event OfferCompleted(
            offerId: UInt64,
            nftType: Type,
            nftId: UInt64,
            purchased: Bool,
            acceptingAddress: Address?,
        )

        // Royalty
        // A struct representing a recipient that must be sent a certain amount
        // of the payment when a NFT is sold.
        //
        pub struct Royalty {
            pub let receiver: Capability<&{FungibleToken.Receiver}>
            pub let amount: UFix64

            init(receiver: Capability<&{FungibleToken.Receiver}>, amount: UFix64) {
                self.receiver = receiver
                self.amount = amount
            }
        }
pub resource SomeResource {
    pub var value: Int

    init(value: Int) {
        self.value = value
    }
}
        // OfferDetails
        // A struct containing Offers' data.
        //
        pub struct OfferDetails {
            // The ID of the offer
            pub let offerId: UInt64
            // The Type of the NFT
            pub let nftType: Type
            // The ID of the NFT
            pub let nftId: UInt64
            // The Offer amount for the NFT
            pub let offerAmount: UFix64
            // Flag to tracked the purchase state
            pub var purchased: Bool
            // This specifies the division of payment between recipients.
            pub let royalties: [Royalty]

            // setToPurchased
            // Irreversibly set this offer as purchased.
            //
            access(contract) fun setToPurchased() {
                self.purchased = true
            }

            // initializer
            //
            init(
                offerId: UInt64,
                nftType: Type,
                nftId: UInt64,
                offerAmount: UFix64,
                royalties: [Royalty]
            ) {
                self.offerId = offerId
                self.nftType = nftType
                self.nftId = nftId
                self.offerAmount = offerAmount
                self.purchased = false
                self.royalties = royalties
            }
        }

        // OfferPublic
        // An interface providing a useful public interface to an Offer resource.
        //
        pub resource interface OfferPublic {
            // accept
            // This will accept the offer if provided with the NFT id that matches the Offer
            //
            pub fun accept(
                item: @NonFungibleToken.NFT,
                receiverCapability: Capability<&{FungibleToken.Receiver}>
            ): Void
            // getDetails
            // Return Offer details
            //
            pub fun getDetails(): OfferDetails
        }

        pub resource Offer: OfferPublic {
            // The OfferDetails struct of the Offer
            access(self) let details: OfferDetails
            // The vault which will handle the payment if the Offer is accepted.
            access(contract) let vaultRefCapability: Capability<&{FungibleToken.Provider, FungibleToken.Balance}>
            // Receiver address for the NFT when/if the Offer is accepted.
            access(contract) let nftReceiverCapability: Capability<&{NonFungibleToken.CollectionPublic}>

            init(
                vaultRefCapability: Capability<&{FungibleToken.Provider, FungibleToken.Balance}>,
                nftReceiverCapability: Capability<&{NonFungibleToken.CollectionPublic}>,
                nftType: Type,
                nftId: UInt64,
                amount: UFix64,
                royalties: [Royalty],
            ) {
                pre {
                    nftReceiverCapability.check(): "reward capability not valid"
                }
                self.vaultRefCapability = vaultRefCapability
                self.nftReceiverCapability = nftReceiverCapability

                var price: UFix64 = amount
                let royaltyInfo: {Address:UFix64} = {}

                for royalty in royalties {
                    assert(royalty.receiver.check(), message: "invalid royalty receiver")
                    price = price - royalty.amount
                    royaltyInfo[royalty.receiver.address] = royalty.amount
                }

                assert(price > 0.0, message: "price must be > 0")

                self.details = OfferDetails(
                    offerId: self.uuid,
                    nftType: nftType,
                    nftId: nftId,
                    offerAmount: amount,
                    royalties: royalties
                )

                emit OfferAvailable(
                    offerAddress: nftReceiverCapability.address,
                    offerId: self.details.offerId,
                    nftType: self.details.nftType,
                    nftId: self.details.nftId,
                    offerAmount: self.details.offerAmount,
                    royalties: royaltyInfo,
                )
            }

            // accept
            // Accept the offer if...
            // - Calling from an Offer that hasn't been purchased/desetoryed.
            // - Provided with a NFT matching the NFT id within the Offer details.
            // - Provided with a NFT matching the NFT Type within the Offer details.
            //
            pub fun accept(
                    item: @NonFungibleToken.NFT,
                    receiverCapability: Capability<&{FungibleToken.Receiver}>
                ): Void {

                pre {
                    !self.details.purchased: "Offer has already been purchased"
                    item.id == self.details.nftId: "item NFT does not have specified ID"
                    item.isInstance(self.details.nftType): "item NFT is not of specified type"
                }

                self.details.setToPurchased()
                self.nftReceiverCapability.borrow()!.deposit(token: <- item)

                let initalDucSupply = self.vaultRefCapability.borrow()!.balance
                let payment <- self.vaultRefCapability.borrow()!.withdraw(amount: self.details.offerAmount)

                // Payout royalties
                for royalty in self.details.royalties {
                    if let receiver = royalty.receiver.borrow() {
                        let amount = royalty.amount
                        let part <- payment.withdraw(amount: amount)
                        receiver.deposit(from: <- part)
                    }
                }

                receiverCapability.borrow()!.deposit(from: <- payment)

                // If a DUC vault is being used for payment we must assert that no DUC is leaking from the transactions.
                let isDucVault = self.vaultRefCapability.isInstance(
                    Type<Capability<&DapperUtilityCoin.Vault{FungibleToken.Provider, FungibleToken.Balance}>>()
                )

                if isDucVault {
                    assert(self.vaultRefCapability.borrow()!.balance == initalDucSupply, message: "DUC is leaking")
                }

                emit OfferCompleted(
                    offerId: self.details.offerId,
                    nftType: self.details.nftType,
                    nftId: self.details.nftId,
                    purchased: self.details.purchased,
                    acceptingAddress: receiverCapability.address,
                )
            }

            // getDetails
            // Return Offer details
            //
            pub fun getDetails(): OfferDetails {
                return self.details
            }

            destroy() {
                if !self.details.purchased {
                    emit OfferCompleted(
                        offerId: self.details.offerId,
                        nftType: self.details.nftType,
                        nftId: self.details.nftId,
                        purchased: self.details.purchased,
                        acceptingAddress: nil,
                    )
                }
            }
        }

        // makeOffer
        pub fun makeOffer(
            vaultRefCapability: Capability<&{FungibleToken.Provider, FungibleToken.Balance}>,
            nftReceiverCapability: Capability<&{NonFungibleToken.CollectionPublic}>,
            nftType: Type,
            nftId: UInt64,
            amount: UFix64,
            royalties: [Royalty],
        ): @Offer {
            let newOfferResource <- create Offer(
                vaultRefCapability: vaultRefCapability,
                nftReceiverCapability: nftReceiverCapability,
                nftType: nftType,
                nftId: nftId,
                amount: amount,
                royalties: royalties,
            )
            return <-newOfferResource
        }
    }

        """

    # result = get_code_text(declaration_node_text)
    # result_list = parse_code2(result['program'])
    # print(result_list)

    while 1:
        code_et()




    # result  = parse_declaration_struct_type(declaration_node_text)
    # print(result)