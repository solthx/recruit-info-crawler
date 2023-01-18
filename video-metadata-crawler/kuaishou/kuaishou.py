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


'''
    获取评论数，收藏数等信息
'''
def get_video_info(aweme_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'cookie': 'kpf=PC_WEB; clientid=3; didv=1675254135325; did=web_07c2ff7d7ddca5d377e23cbc6363f3b9; client_key=65890b29; _did=web_1698828760788FD; userId=1722213999; ktrace-context=1|MS43NjQ1ODM2OTgyODY2OTgyLjgyNDE3OTUxLjE2NzUzMTI4NjUxNzAuMTE5MTkw|MS43NjQ1ODM2OTgyODY2OTgyLjM2NjQyNDUxLjE2NzUzMTI4NjUxNzAuMTE5MTkx|0|graphql-server|webservice|false|NA; clientid=3; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABusxoAF6Tlu4b2nJupePaU3fU49gtj2Wd08X-cwVyddXVtXoTyvIDKgpbpnVfg9x6OO-ov2KcetSOQMX5zXUJynB_i7p4GeNGPMbbbrYDVpay4ZYsgL4iZ29bm8NDmCBI3kPFiqz5ChGhPqQ8P4-ujFuiwNGKj6Katykc92JJySHPKvIg4MjtpKdvlf7jzcA-rbjL4GHYIDghBWHZE-grjBoSuDcrlwmr6APhXfdZrBO5uo0FIiChFniTAt4dlO6xgBz0Nbz68WDik7RAke3O4t0OthttDSgFMAE; kuaishou.server.web_ph=d8367bf2fd5970832228bdc193c15d5721d4; kpn=KUAISHOU_VISION'
    }
    with open('comment_query', encoding='utf-8') as f:
        query = f.read()

    data = {
        "operationName": "commentListQuery",
        "variables": {
            "photoId": aweme_id,
            "pcursor": ''
        },
        "query": query
    }
    data = req.post('https://www.kuaishou.com/graphql', headers=headers, json=data).json()

    print(aweme_id)
    print(data)
    return {'comment_count':data['data']['visionCommentList']['commentCount']}


def extract_tag(title):
    words = title.split(' ')
    res = []
    for e in words:
        if e.startswith('#'):
            res.append(e[1:])
    return res



def parse_and_dump_data(keyword, data, meta_dict):
    if data['data'] == None or data['data']['visionSearchPhoto'] == None or data['data']['visionSearchPhoto']['feeds'] == None:
        return {}
    data_list = data['data']['visionSearchPhoto']['feeds']
    guide_word_set = set()
    # 持久化meta_data
    with open('meta_data.csv', 'a', encoding='utf-8') as f:
        for e in data_list:
            photo = e['photo']
            aweme_id = photo['id']
            title = photo['caption'].replace(',', '，')
            # 如果已经保存过这个视频，就跳过
            if aweme_id in meta_dict.keys():
                continue
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(photo['timestamp']/1000))  # 视频创建时间
            # comment_count = stat['comment_count']  # 评论数
            digg_count = photo['realLikeCount']  # 点赞数
            play_count = photo['viewCount']  # 播放数
            # video_info = get_video_info(aweme_id)
            # comment_count = video_info['comment_count']
            video_url = 'https://www.kuaishou.com/short-video/'+aweme_id
            tags = extract_tag(title)
            meta_dict[aweme_id] = {
                'query': keyword,
                'aweme_id': aweme_id,
                'title': title,
                'create_time': create_time,
                'play_count' : play_count,
                'digg_count': digg_count,
                # 'comment_count': comment_count,
                # 'collect_count': collect_count,
                # 'share_count': share_count,
                # 'download_count': download_count,
                'video_url': video_url,
                'tags': tags
            }
            lst = [keyword, ' && '.join(list(guide_word_set)), aweme_id, title, create_time, str(play_count), str(digg_count),
                    video_url,
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

    print(dic)
    print(counter)

    counter_data = do_formate(counter)

    pd.DataFrame(dic).to_excel(writer, sheet_name="meta-data", index=False)
    pd.DataFrame(counter_data).to_excel(writer, sheet_name="tags-rank", index=False)

    writer.save()
    writer.close()


def solve():
    headers = {
        'accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '163',
        'content-type': 'application/json',
        'Cookie': 'kpf=PC_WEB; clientid=3; didv=1675254135325; did=web_07c2ff7d7ddca5d377e23cbc6363f3b9; client_key=65890b29; _did=web_1698828760788FD; userId=1722213999; ktrace-context=1|MS43NjQ1ODM2OTgyODY2OTgyLjgyNDE3OTUxLjE2NzUzMTI4NjUxNzAuMTE5MTkw|MS43NjQ1ODM2OTgyODY2OTgyLjM2NjQyNDUxLjE2NzUzMTI4NjUxNzAuMTE5MTkx|0|graphql-server|webservice|false|NA; clientid=3; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABusxoAF6Tlu4b2nJupePaU3fU49gtj2Wd08X-cwVyddXVtXoTyvIDKgpbpnVfg9x6OO-ov2KcetSOQMX5zXUJynB_i7p4GeNGPMbbbrYDVpay4ZYsgL4iZ29bm8NDmCBI3kPFiqz5ChGhPqQ8P4-ujFuiwNGKj6Katykc92JJySHPKvIg4MjtpKdvlf7jzcA-rbjL4GHYIDghBWHZE-grjBoSuDcrlwmr6APhXfdZrBO5uo0FIiChFniTAt4dlO6xgBz0Nbz68WDik7RAke3O4t0OthttDSgFMAE; kuaishou.server.web_ph=d8367bf2fd5970832228bdc193c15d5721d4; kpn=KUAISHOU_VISION',
        'Host': 'www.kuaishou.com',
        'Origin': 'https://www.kuaishou.com',
        'Referer': 'https://www.kuaishou.com/search/video?searchKey=%E8%9B%8B%E4%BB%94%E6%B4%BE%E5%AF%B9',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'

    }

    url = 'https://www.kuaishou.com/graphql'

    total = 1000
    # 1. 读取keywords
    with open("keyword", encoding='utf-8') as f:
        keywords = f.readlines()
    # 遍历每一个keyword，每一个keyword对应一个excel的sheet
    for keyword in keywords:
        print(">>>>>>>> 搜索: {}".format(keyword))
        key = keyword.strip()
        meta_dict = {}  # 保存视频的meta_data信息
        pcursor = 1
        pre = -1
        old = 0
        while len(meta_dict)<total:
            params = {
                "operationName": "visionSearchPhoto",
                "query": "fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  likeCount\n  viewCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  __typename\n}\n\nquery visionSearchPhoto($keyword: String, $pcursor: String, $searchSessionId: String, $page: String, $webPageArea: String) {\n  visionSearchPhoto(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    searchSessionId\n    pcursor\n    aladdinBanner {\n      imgUrl\n      link\n      __typename\n    }\n    __typename\n  }\n}\n",
                'variables': {'keyword': key, 'pcursor': f"{pcursor}", 'page': "search",
                              'searchSessionId': "MTRfMTcyMjIxMzk5OV8xNjc1MzUxOTUzMzA4X-ibi-S7lOa0vuWvuV85MDQx"}
            }
            params = json.dumps(params)
            for j in range(15):
                data = req.post(url=url, headers=headers, data=params).json()
                # print(data)
                # print(data.encoding)
                # print(data.apparent_encoding)
                # data.encoding = 'utf-8'
                parse_and_dump_data(key, data, meta_dict)  # 把爬到的数据持久化
                # print("sleep...")
                # # time.sleep(random.randint(1, 3))
                # print("awake!")
            pcursor += 1
            print('{}/{}'.format(len(meta_dict), total))
            if old > 3:
                break
            if pre == len(meta_dict):
                old += 1

            pre = len(meta_dict)

        # print(meta_dict)  # 接下来就是这个meta_dict进行提取
        # 保存meta_dict
        global_data.update(meta_dict)
        save_result(key, meta_dict, False)

    # print(data)


if __name__ == '__main__':
    solve()
    save_result("汇总", global_data, True)
    # print(chinese_encode('蛋仔派对'))