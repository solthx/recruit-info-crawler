'''
    根据公众号名称获取fake_id，并打印
'''

import requests
import requests as req
import yaml
import time
import random
import json
from tqdm import tqdm

def run():
    # accounts_name = ["字节跳动招聘","完美世界招聘","美的集团招聘","腾讯互娱招聘","联合利华微招聘","网易游戏雷火伏羲招聘","阿里巴巴灵犀互娱招聘","毕马威招聘","滴滴校园招聘","欧莱雅校园招聘","网易游戏互娱校园招聘","游族招聘","米哈游招聘","德勤招聘","快手招聘","畅游招聘","网易招聘","美团招聘","腾讯招聘","小红书招聘","西山居招聘","哔哩哔哩招聘"]
    # accounts_name = ["内推军","校招咨询","高校求职通","直通Offer","闪电Offer","校招薪水","校园招聘","校招僧","银行招聘网","校招推推","校招日历"]
    accounts_name = ["清华经管学院职业发展中心", "中大内推圈", "同济实习KING", "复旦管院职业发展中心", "花哥哥带你拿offer", "TLAB创投实验室", "Candy实习吧", "创投实习圈", "YoungsBlood", "UplusCareer", "内推熊", "北京实习生频道", "好实习不南", "暑期实习网", "多多群岛", "WeCareer Club", "求职工场", "麦芒求职", "商赛网"]
    res = {}
    for i in tqdm(range(len(accounts_name))):
        name = accounts_name[i]
        url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"
        headers = {
            "Cookie": "appmsglist_action_3873895966=card; RK=nn2hkLuxZ2; ptcz=94a3c19a976e49ca513846c2b7493f31804a857a82d2371dcbd89e8d7c306324; pgv_pvid=1319829434; pgv_info=ssid=s4071861854; pac_uid=0_2a1f12ff42478; rewardsn=; wxtokenkey=777; wwapp.vid=; wwapp.cst=; wwapp.deviceid=; uin=o1154238323; skey=@uUBcc2CMn; ua_id=hPVs1zvlXYpuzKypAAAAAA9lAJ1ke4QkXUiBQzCnTVI=; wxuin=73589296608638; sig_login=h01869a59a4594a42d6952808cfb80435d419023cc28f662b16fc9e548a3cc13f2313e512ad89f7b6dc; mm_lang=zh_CN; use_waban_ticket=1; media_ticket=b0aa7d4a6683288480a311bdb38f62e790e8e7e6; media_ticket_id=gh_8faf819ba59c; uuid=9fd5f701e74f1b3823bc2c172eeda8de; rand_info=CAESIEkIggQ1MTFIJg3dVwAePBzaEDWQUvVBgP/FedjXGbmU; slave_bizuin=3873895966; data_bizuin=3873895966; bizuin=3873895966; data_ticket=T/61ZeIedR8etaUqXJA2fXYl4rBTI3tjgIQvwT6Uf+VsM9L9Kp7xMWl9RZXeb584; slave_sid=UFNZOG04OTNsSl91UGZMY1RxRDR2ZnhsOVdzNDFuT1IxZVZpX28ycHdNVmxvaXVGRXIzYjBNWUtkVVZubDVQV3hpVFJjWWJvc19aRTBxXzJpcW45Qk1LT3dxMVZKRmRHN0tsc2JMb0xhdkpLcnBZR3A4NTBzZFRjcmlyWmZLWWlrS054Y2JOckRIc2xVTm9N; slave_user=gh_85f25ffaaecc; xid=bdae953a51306588a7753ffb53f23f8b",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        params = {
            "action": "search_biz",
            "begin": "0",
            "count": "5",
            "query": name,
            "token": "170799045",
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }
        # {"base_resp":{"ret":0,"err_msg":"ok"},"list":[{"fakeid":"Mzk0MzE5MDExNw==","nickname":"JDigger","alias":"jdigger","round_head_img":"http:\/\/mmbiz.qpic.cn\/sz_mmbiz_png\/fLibXIGakXtVicFQQX4k7cVibKEb4GBsuOro6icZFRb2r3ZVmX5byphDt9MfTVwlwTleLpWpYOPAIYMek722SjZxJw\/0?wx_fmt=png","service_type":1,"signature":"发布一级市场投融资（PE、VC、FA）领域优质JD（Job Description，职位介绍），分享实用干货。"}],"total":1}

        resp = req.get(url, headers=headers, verify=False, params=params).json()
        # print(resp)
        if (len(resp['list'])>0):
            res[name] = resp['list'][0]['fakeid']
        else:
            print("这个公众号名字不太对：{}".format(name))
        time.sleep(random.randint(5, 10))
        print()
    return res

if __name__ == '__main__':
    res = run()
    print(res)