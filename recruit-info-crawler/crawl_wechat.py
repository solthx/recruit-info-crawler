'''
    爬取预设公众号
'''
import json
import random
import time

import requests
import requests as req
import yaml
import pandas as pd



key_word = ['暑期实习']

# 目标公司名
company_names = ['美团','腾讯','完美世界','阿里','网易','字节', '快手', '米哈游']

# 岗位
post_names = ['海外', '战投', '用研', '用户研究', '战略', '市场', '行研', '行业研究', '运营', '产品']

# 实习
role_names = ['实习']

'''
    筛选出最近日期的文章元数据
    resp: 原始元数据
    cnt: 天数，从今天开始希望分析往前的天数的文章
    account_name: 所属公众号
    @return：
        元素为(发布时间, 所属公众号, title, url)的list
'''
def meta_data_filter(resp, cnt, account_name):
    res_list = []
    for elem in resp['app_msg_list']:
        cur_time = time.time()  # 当前时间戳
        article_time = elem['update_time'] # 文章更新时间

        time_delay = cur_time - article_time
        d = int(time_delay/(60*60*24)) # 相差天数
        h = int((time_delay%(60*60*24))/(60*60)) #相差小时数
        if d*24+h < cnt*24:
            res_list.append((elem['update_time'], account_name, elem['title'], elem['link'])) # 》》》》》》》》元素
            # print(elem)
            # print("当前时间：{}，文章时间：{}，相差{}天{}小时，满足条件".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(cur_time)), time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(article_time)), d, h))
    return res_list

'''
    关键字checker
    规则：关键字匹配
    @return list[...] , 元素:命中的关键字
'''
def key_word_checker(html_text):
    res = []
    for e in key_word:
        if e in html_text:
            res.append(e)
    return res

'''
    互联网公司的岗位checker
    规则：${公司名}(任意字符)${岗位名}(任意字符)实习 
    @return list[...] , 元素:命中的公司实习，例如：腾讯2024年用户研究实习
'''
offset = 20
def dot_company_checker(html_text):
    res = []
    # print(html_text)
    for company_name in company_names:
        # print(company_name)
        pos = 0
        while pos != -1:
            pos = html_text.find(company_name, pos)
            # print(pos)
            if pos != -1:
                # pos位置是公司名
                intern_key_pos = html_text.find('实习', pos, pos+offset)
                # print(intern_key_pos)
                if intern_key_pos != -1:
                    parse_info = html_text[pos:intern_key_pos+2] # 匹配到了 (公司)xxxx(实习)
                    for post_name in post_names:
                        if post_name in parse_info: # 匹配到了 (公司)xxx(岗位)xxx(实习)
                            res.append(parse_info)
                            break
                pos += 1
    return list(set(res))


checkers = [key_word_checker, dot_company_checker]

'''
    @return 命中的内容
'''
def text_parse(html_text):
    lst = []
    # 每个checker都会返回一个list，里面包含了文本分析结果
    for checker in checkers:
        lst.extend(checker(html_text))
    return ' && '.join(lst) # 把这些结果用&&拼接

'''
    recent_data： 元素为(发布时间, 所属公众号, title, url)的list
    @return：     元素为('title', '命中关键字', 'url')的list
'''
def do_process(recent_data):
    res = []
    for e in recent_data:
        url = e[3]
        data = requests.get(url)
        # ch_data = ''.join(re.findall(pat, data.text))
        parse_info = text_parse(data.text)
        if len(parse_info)>0:
            res.append((time.strftime("%Y-%m-%d",time.localtime(e[0])), e[1], e[2], parse_info, e[3])) # 》》》》》》 发布时间, 所属公众号, title, key_word, url
            # res.append((time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(e[0])), e[1], e[2], parse_info, e[3])) # 》》》》》》 发布时间, 所属公众号, title, key_word, url
    return res


def run(config_file, accounts_json_file):
    # 0. 读取配置文件
    with open(config_file, "r") as file:
        file_data = file.read()
    config = yaml.safe_load(file_data)  # 通用配置
    with open(accounts_json_file, 'r', encoding='utf-8') as load_f:
        accounts = json.load(load_f)

    import tqdm
    res = []
    total = 1
    # 遍历预设公众号
    for account_name in accounts:
        # 1. 准备参数
        print("========> 开始处理公众号： {}, {}/{}".format(account_name, total, len(accounts)))
        total += 1
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        headers = {
            "Cookie": config['cookie'],
            "User-Agent": config['user_agent']
        }

        # for accounts_name in accounts:
        params = {
            "action": "list_ex",
            "begin": "0",
            "count": "5",
            "fakeid": accounts[account_name],
            "type": "9",
            "token": config['token'],
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }

        # 2. 爬取文章列表
        resp = req.get(url, headers=headers, verify=False, params=params).json()
        # print(resp)
        if resp['base_resp']['ret'] == 200013:
            print("frequencey control, stop at [accounts_name:{}]".format("accounts_name"))
            return ([],-1)
        # print(resp)
        # 3. 过滤近n天的文章
        recent_data = meta_data_filter(resp, int(config['recent_day']), account_name)

        # 4. 对每篇文章进行处理，关键字匹配
        # result_list为元素为dict{'title', '命中关键字', 'url'}的list
        print(">>>>>>> 爬取完毕，开始分析...")
        result_list = do_process(recent_data)
        res.extend(result_list)
        print(">>>>>>> 分析完毕，开始写入文件...")
        with open('data-wechat.csv', 'a', encoding='utf-8') as f:
            for e in result_list:
                f.writelines(str(e[0]) + "," + str(e[1]) + "," + e[2] + "," + e[3] + "," + e[4] + "\n")

        # print(result_list)
        print(">>>>>>> 处理完毕，开始睡眠...")
        time.sleep(random.randint(7,14))
        print(">>>>>>> 睡眠结束")
    return (res, 0)


# from wxauto import WeChat
#
# '''
#     将结果信息推送至微信
# '''
# def push_message():
#     # 获取当前微信客户端
#     wx = WeChat()
#
#     # 获取会话列表
#     wx.GetSessionList()


if __name__ == '__main__':
    result_list, state = run("config/wechat/wechat.yaml",
                             "recruit-info-crawler/config/wechat/accounts.json")
    with open("./data-wechat.csv", encoding='utf-8') as f:
        contents = []
        readlines = f.readlines()  # readlines是一个列表
        for i in readlines:
            line = i.strip().split(",")  # 去掉前后的换行符，之后按逗号分割开
            contents.append(line)  # contents二维列表
    df = pd.DataFrame(contents)
    df.to_csv('输出结果-wechat.csv', header=False, encoding='utf_8_sig')           # 不添加表头
    # df.columns = ["Source", "Target", "Type", "Path"]  # 添加表头
    # df.to_csv("test.csv", index=False)
    print("数据写入成功")
    # 写入到
    # push_message()