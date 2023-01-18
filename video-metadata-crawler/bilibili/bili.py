import json
import random
import time
import urllib.parse
import requests as req
import pandas as pd

global_data = {}  # 全局

'''
把爬取到的数据持久化下来
'''


def get_vedio_info(aweme_id):
    headers = {
        "cookie": "buvid3=AB199CE4-3AD1-A7A9-94FA-10A5C7F42CF335382infoc; i-wanna-go-back=-1; _uuid=810B8DD51-B6CF-B475-74A4-973672EEB9A135380infoc; nostalgia_conf=-1; CURRENT_BLACKGAP=0; buvid_fp_plain=undefined; blackside_state=0; LIVE_BUVID=AUTO2516595028857899; b_nut=100; CURRENT_QUALITY=112; buvid4=F7C8471F-039B-6FBB-DE3F-8017CC215E1536758-022071120-AYi90B%2FUs1bbEpgfbnj6Aw%3D%3D; CURRENT_FNVAL=4048; rpdid=|(u~J|luJmJm0J'uY~uYumkYR; fingerprint=abc3e973ad839978a42f6de5f9a3cc38; buvid_fp=abc3e973ad839978a42f6de5f9a3cc38; bsource=search_baidu; b_lsid=65D627106_18617BB9749; innersign=0; SESSDATA=f13b515b%2C1690988707%2Cb4a28%2A21; bili_jct=91aed87e929c9caf7cca9d31d821f354; DedeUserID=1675180; DedeUserID__ckMd5=dccd51fe1095d84c; sid=qjeeaj6w; PVID=1; b_ut=5",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",

        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
    }
    data = req.get("https://api.bilibili.com/x/web-interface/archive/stat?aid={}".format(aweme_id), headers=headers).json()
    time.sleep(random.randint(1, 3))
    return data['data']

def parse_and_dump_data(keyword, data, meta_dict):
    result_list = data['data']['result']
    for e in result_list:
        if e['result_type'] == 'video':
            data_list = e['data']
    # 持久化meta_data
    with open('dump/meta_data.csv', 'a', encoding='utf-8') as f:
        for e in data_list:
            aweme_id = e['aid']
            title = e['title']
            # 如果已经保存过这个视频，就跳过
            if aweme_id in meta_dict.keys():
                continue
            stat = get_vedio_info(aweme_id)
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e['senddate']))  # 视频创建时间
            # print(stat)
            play_count = stat['view'] # 播放数
            bulletchat_count = stat['danmaku'] # 弹幕数
            comment_count = stat['reply']  # 评论数
            digg_count = stat['like']  # 点赞数
            share_count = stat['share']  # 转发数
            coin_count = stat['coin']  # 下载数
            bvid = stat['bvid']

            collect_count = stat['favorite']  # 收藏数
            video_url = "https://www.bilibili.com/video/"+bvid+"/?spm_id_from=333.337.search-card.all.click#/"
            tags = []
            if 'tag' in e.keys():
                tags = e['tag'].split(',')

            meta_dict[aweme_id] = {
                'query': keyword,
                'aweme_id': aweme_id,
                'title': title,
                'create_time': create_time,
                'play_count': play_count,
                'digg_count': digg_count,
                'comment_count': comment_count,
                'collect_count': collect_count,
                'share_count': share_count,
                'coin_count': coin_count,
                'bulletchat_count': bulletchat_count,
                'video_url': video_url,
                'tags': tags
            }
            lst = [keyword,  str(aweme_id), title, create_time, str(play_count), str(digg_count),
                   str(comment_count), str(collect_count), str(share_count), str(coin_count), str(bulletchat_count), video_url,
                   ' && '.join(tags)]
            f.writelines(', '.join(lst) + '\n')

def chinese_encode(str):
    str = str.encode('utf-8')
    return urllib.parse.quote(str)


def do_formate(counter):
    lst = []
    for k in counter.keys():
        lst.append((counter[k], k))
    slst = list(reversed(sorted(lst)))
    res = {'tag': [], 'count': []}
    for e in slst:
        res['tag'].append(e[1])
        res['count'].append(e[0])
    return res


def save_result(key, meta_dict, isAll):
    writer = pd.ExcelWriter(key + ".xlsx")
    dic = {}
    guide_words = None

    stop_word = ['query', 'aweme_id']
    if isAll:
        stop_word = ['aweme_id']

    counter = {}

    for k in meta_dict.keys():
        items_dict = meta_dict[k]
        for kk in items_dict.keys():
            if kk in stop_word:
                if kk == 'guide_words':
                    guide_words = items_dict[kk]
                continue
            if kk not in dic:
                dic[kk] = []
            dic[kk].append(str(items_dict[kk]))
        tags = items_dict['tags']
        tag_list = list(tags)
        for tag in tag_list:
            ct = tag.lower()
            if ct not in counter.keys():
                counter[ct] = 0
            counter[ct] += 1

    # print(dic)
    # print(counter)

    counter_data = do_formate(counter)

    pd.DataFrame(dic).to_excel(writer, sheet_name="meta-data", index=False)
    pd.DataFrame(counter_data).to_excel(writer, sheet_name="tags-rank", index=False)

    writer.save()
    writer.close()

from tqdm import tqdm

def solve():
    headers = {
        "cookie": "buvid3=AB199CE4-3AD1-A7A9-94FA-10A5C7F42CF335382infoc; i-wanna-go-back=-1; _uuid=810B8DD51-B6CF-B475-74A4-973672EEB9A135380infoc; nostalgia_conf=-1; CURRENT_BLACKGAP=0; buvid_fp_plain=undefined; blackside_state=0; LIVE_BUVID=AUTO2516595028857899; b_nut=100; CURRENT_QUALITY=112; buvid4=F7C8471F-039B-6FBB-DE3F-8017CC215E1536758-022071120-AYi90B%2FUs1bbEpgfbnj6Aw%3D%3D; CURRENT_FNVAL=4048; rpdid=|(u~J|luJmJm0J'uY~uYumkYR; sid=620mlei3; b_ut=7; fingerprint=abc3e973ad839978a42f6de5f9a3cc38; bsource=search_baidu; innersign=1; b_lsid=631FE153_1860C9B2A98; PVID=2; buvid_fp=abc3e973ad839978a42f6de5f9a3cc38",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
    }

    params = {
        "__refresh__": "true",
        "_extra":"",
        "context":"",
        "page": "1",
        "page_size": "42",
        "order": "",
        "duration": "",
        "from_source": "",
        "from_spmid": "333.337",
        "platform": "",
        "pchighlight":"1",
        "single_column": "0",
        # "keyword": "蛋仔派对",
        "qv_id":"aT2dS0UV4vf2sMVz2CCMTPT8n1ehBkuG",
        "ad_resource": "5646",
        "source_tag": "3",
        "w_rid": "b5f43a06cdd560bddbda9e43b2cb2642",
        "wts":"1675243615"
    }
    url = "https://api.bilibili.com/x/web-interface/wbi/search/all/v2"

    # 1. 读取keywords
    with open("keyword", encoding='utf-8') as f:
        keywords = f.readlines()
    # 遍历每一个keyword，每一个keyword对应一个excel的sheet
    for keyword in keywords:
        print(">>>>>>>> 搜索: {}".format(keyword))
        key = keyword.strip()
        meta_dict = {}  # 保存视频的meta_data信息
        referer = "https://search.bilibili.com/all?keyword=" + chinese_encode(key) + "&from_source=webtop_search&spm_id_from=333.1007&search_source=5"
        headers['referer'] = referer
        params['keyword'] = key

        for i in tqdm(range(42)):
            idx = i+1
            params['page'] = str(idx)
            data = req.get(url=url, params=params, headers=headers).json()
            # print(data)
            parse_and_dump_data(key, data, meta_dict)  # 把爬到的数据持久化
            time.sleep(random.randint(10, 20))

        # print(meta_dict)  # 接下来就是这个meta_dict进行提取
        # 保存meta_dict
        global_data.update(meta_dict)
        save_result(key, meta_dict, False)

    # print(data)


if __name__ == '__main__':
    solve()
    save_result("汇总", global_data, True)