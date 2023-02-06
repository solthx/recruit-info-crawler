import json
import random
import time
import urllib.parse
import requests as req
import yaml
import pandas as pd

def chinese_encode(str):
    str = str.encode('utf-8')
    return urllib.parse.quote(str)

def solve():
    headers = {
        "cookie": "ttwid=1%7CrWqfcgEtl_jEZgrubOtgKuIYy_cHa1XM34eGvdm1CO8%7C1675169579%7C6332a00695af2e7bd1a49ac7f06e5fb29e6fc18f557cafe55631e567c7e765aa; douyin.com; home_can_add_dy_2_desktop=%220%22; passport_csrf_token=c52e30b5c9adec7f4e59cc0e0bf6ed3a; passport_csrf_token_default=c52e30b5c9adec7f4e59cc0e0bf6ed3a; s_v_web_id=verify_ldk8pu4g_bUIKW0hS_MGJQ_438m_Bdck_tbVdIgCM4lMH; csrf_session_id=88835bdd4e77185aef362147e6517461; __ac_signature=_02B4Z6wo00f01bgo.oQAAIDAM2NlZFU2n5G4CPoAAA3Ue1; SEARCH_RESULT_LIST_TYPE=%22single%22; ttcid=f06ea5d37a8949a590b611fb5059112f17; n_mh=ROKeS5kNTFJrWU3jzgnxTGZE-HZxlkcnRf6uAXoXpY8; sso_uid_tt=16c3c6df6073c69335a1208c812a0c91; sso_uid_tt_ss=16c3c6df6073c69335a1208c812a0c91; toutiao_sso_user=99fe6872ac6b274fe09faad0a061b5b6; toutiao_sso_user_ss=99fe6872ac6b274fe09faad0a061b5b6; passport_assist_user=Cj2f7CA7nhgvFKzY7fqRl3JhoWdT5Gf8hFbIgrg6yQsYdONfWz_5nMrODIVUi8BVotwn8W2t8c6GZiXGIsfGGkgKPHuiMdLAb8KkS9pOxeE0Zr0vC4N0FMnANwyOjAOXx12v4CzNkHaItbD6jpIO2K8PkkhbsWKT3h1dgbQfLxDXh6gNGImv1lQiAQODe25Y; sid_ucp_sso_v1=1.0.0-KGU2MjYzYjRjMTZhM2RkNzg4N2ZjZGIxYjkyZmQyMTcxMDQ5OTNhOWEKHQjxjcrRhAMQ3aTkngYY7zEgDDC78tfcBTgGQPQHGgJobCIgOTlmZTY4NzJhYzZiMjc0ZmUwOWZhYWQwYTA2MWI1YjY; ssid_ucp_sso_v1=1.0.0-KGU2MjYzYjRjMTZhM2RkNzg4N2ZjZGIxYjkyZmQyMTcxMDQ5OTNhOWEKHQjxjcrRhAMQ3aTkngYY7zEgDDC78tfcBTgGQPQHGgJobCIgOTlmZTY4NzJhYzZiMjc0ZmUwOWZhYWQwYTA2MWI1YjY; odin_tt=dd3d6dbb219329e25a34cdcfed543402f4ca37b9f4332ff9a870db0dbf5d3abef51d545cc6ea73f2633a35cb1a5d4b6ca2454648ed15767b67c11c50ca2284d9; passport_auth_status=78408a345e8ca888c230c4f037450282%2C; passport_auth_status_ss=78408a345e8ca888c230c4f037450282%2C; uid_tt=f904864432c1f79ffd9724ede0602b77; uid_tt_ss=f904864432c1f79ffd9724ede0602b77; sid_tt=6e15b79974d72ef1cad6123def59ca34; sessionid=6e15b79974d72ef1cad6123def59ca34; sessionid_ss=6e15b79974d72ef1cad6123def59ca34; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1675775198920%2C%22type%22%3A1%7D; strategyABtestKey=%221675170399.188%22; store-region=cn-bj; store-region-src=uid; sid_guard=6e15b79974d72ef1cad6123def59ca34%7C1675170400%7C5183997%7CSat%2C+01-Apr-2023+13%3A06%3A37+GMT; sid_ucp_v1=1.0.0-KDdiYjVkMmM2OWViOThjNjVmNDM4ZWE0NmQyMjNlYWEwN2NjY2JkOWEKFwjxjcrRhAMQ4KTkngYY7zEgDDgGQPQHGgJscSIgNmUxNWI3OTk3NGQ3MmVmMWNhZDYxMjNkZWY1OWNhMzQ; ssid_ucp_v1=1.0.0-KDdiYjVkMmM2OWViOThjNjVmNDM4ZWE0NmQyMjNlYWEwN2NjY2JkOWEKFwjxjcrRhAMQ4KTkngYY7zEgDDgGQPQHGgJscSIgNmUxNWI3OTk3NGQ3MmVmMWNhZDYxMjNkZWY1OWNhMzQ; download_guide=%223%2F20230131%22; tt_scid=Hg7GTCmJTcGXAdtWJd-JB7LVkeRoD.FtN..gT4BD94LhifZW8eatoB4NWWEkGimyc85c; msToken=1f7VJsuEtIQaiYqJndX-rtaphwH1MEojzGPiyjzkldvgDqMEG1R1Ig3PoWt1essBk-bDyfV0ShRi1PggsMMMqtSdEhueyGcke4fZ_0tOJltkPpYB05gEhWlp4QPeVA==; passport_fe_beating_status=true; msToken=cgEDAiGNMPFSMx_GOVWapuznJ8Kwe9Pjp46OoAlEwssv5jIDC9ILGfmd98HZh3VwTE7f8CrUDNWzD6oRQqPM-4vFMEsPjE7flNc_z7bNINAa8w8PXwQxtuRDVTZH_A==",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }

    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "search_channel": "aweme_general",
        "sort_type": "1",
        "publish_time": "0",
        # "keyword": "蛋仔派对",
        "search_source": "tab_search",
        "query_correct_type": "1",
        "is_filter_search": "1",
        "from_group_id": "",
        "offset": "0",
        "count": "10",
        "search_id": "202301312127451A0FED3FC8A0731BE6DD",
        "pc_client_type": "1",
        "version_code": "190600",
        "version_name": "19.6.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "109.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "109.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "cpu_core_num": "12",
        "device_memory": "8",
        "platform": "PC",
        "downlink": "10",
        "effective_type": "4g",
        "round_trip_time": "50",
        "webid": "7194798495584421379",
        "msToken": "1f7VJsuEtIQaiYqJndX-rtaphwH1MEojzGPiyjzkldvgDqMEG1R1Ig3PoWt1essBk-bDyfV0ShRi1PggsMMMqtSdEhueyGcke4fZ_0tOJltkPpYB05gEhWlp4QPeVA==",
        "X-Bogus": "DFSzswVuu7UANG4WS4H3cPt/pLw8"
    }
    url = "https://www.douyin.com/aweme/v1/web/general/search/single"
    # 1. 读取keywords
    with open("./keyword", encoding='utf-8') as f:
        keywords = f.readlines()
    for keyword in keywords:
        key = keyword.strip()
        referer = "https://www.douyin.com/search/"+chinese_encode(key)+"?publish_time=0&sort_type=1&source=tab_search&type=general"
        headers['referer'] = referer
        params['keyword'] = key
        offset = 0
        count = 20
        print(referer)
        # while offset + count <= total:
        params['offset'] = str(offset)
        params['count'] = str(count)
        data = req.get(url=url, params=params,headers=headers).json()
        print(data)
        offset += count
        # time.sleep(random.randint(7,14))
    # print(data)

if __name__ == '__main__':
    solve()
    # print(chinese_encode('蛋仔派对'))