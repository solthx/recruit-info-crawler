import requests as req
import yaml
import json
import time
import pandas as pd
import random
def time_check(update_time, cnt):
    cur_time = time.time()  # 当前时间戳
    time_delay = cur_time - update_time
    d = int(time_delay / (60 * 60 * 24))  # 相差天数
    h = int((time_delay % (60 * 60 * 24)) / (60 * 60))  # 相差小时数
    return d * 24 + h < cnt * 24


def run(config_file, accounts_json_file):
    with open(config_file, "r") as file:
        file_data = file.read()
    config = yaml.safe_load(file_data)  # 通用配置
    with open(accounts_json_file, 'r', encoding='utf-8') as load_f:
        accounts = json.load(load_f)
    jobs = pd.read_csv("config/nowcoder/dump/dump.csv")['id']
    jobset = set(jobs)

    # 1. 准备header参数
    headers = {
        "User-Agent":config['user_agent'],
        "Cookie":config['cookie']
    }
    res = []
    # 遍历每个岗位
    for account_name in accounts:
        print(">>>>>>>> 开始搜索岗位：[{}]".format(account_name))
        cur_page = 1
        total_page = 2
        # 遍历每一页
        while cur_page <= total_page:
            tmp_list = []
            print(">>>>>>>> 正在遍历第{}页，共{}页".format(cur_page, total_page))
            payload = {
                'requestFrom':'1',
                'page':cur_page,
                'pageSize':'20',
                'recruitType':'2',
                'jobCity':'北京',
                'careerJobId': accounts[account_name],
                'internDayList':'1',   # 1表示出勤1～3天，2表示4～5天
                'visitorId':'b8a571ac - 6e7f - 414b - 9da8 - b575c80d673b'
            }
            url = "https://www.nowcoder.com/np-api/u/job/search?_=1673970012958"
            # 2. 发起请求
            result = req.post(url, headers=headers, data=payload).json()
            # print(result)
            if result['code'] != 0:
                return [], -1
            cur_page += 1
            total_page = result['data']['totalPage']
            data_list = result['data']['datas']
            # 遍历每个JD
            for data in data_list:
                jd_id = data['id']
                job_name = data['jobName']
                update_time = data['updateTime']
                # print(update_time)
                job_keys = data['jobKeys']
                company_name = data['user']['identity'][0]['companyName']
                page_url = "https://www.nowcoder.com/jobs/intern/detail?jobId={}".format(jd_id)
                if jd_id not in jobset and time_check(update_time, config['recent_day']):
                    jobset.add(jd_id)
                    tmp_list.append((time.strftime("%Y-%m-%d", time.localtime(update_time/1000)), '牛客', '[{} - {}]'.format(company_name, job_name), str.replace(job_keys, ","," && "), str(page_url)))
            # print(tmp_list)
            time.sleep(random.randint(7,14))
            with open('data-nowcoder.csv', 'a', encoding='utf-8') as f:
                for e in res:
                    f.writelines(str(e[0]) + "," + str(e[1]) + "," + e[2] + "," + e[3] + "," + e[4] + "\n")
            res.extend(tmp_list)
    # 更新jobid
    pd.DataFrame(data=list(jobset), columns=['id']).to_csv("config/nowcoder/dump/dump-{}.csv".format(time.strftime("%Y-%m-%d",time.localtime(time.time()))))
    return res, 0




    return [], 0

if __name__ == '__main__':
    result, state = run('config/nowcoder/nowcoder.yaml',
                        'recruit-info-crawler/config/nowcoder/accounts.json')
    with open("./data-nowcoder.csv", encoding='utf-8') as f:
        contents = []
        readlines = f.readlines()  # readlines是一个列表
        for i in readlines:
            line = i.strip().split(",")  # 去掉前后的换行符，之后按逗号分割开
            contents.append(line)  # contents二维列表
    df = pd.DataFrame(contents)
    df.to_csv('输出结果-nowcoder.csv', header=False, encoding='utf_8_sig')  # 不添加表头
    # df.columns = ["Source", "Target", "Type", "Path"]  # 添加表头
    # df.to_csv("test.csv", index=False)
    print("数据写入成功")
