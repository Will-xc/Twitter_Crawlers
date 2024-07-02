# coding=utf-8
# 开发人员  ：  熊超
# 开发时间  ：  2024/2/15  22:08
# 文件功能  :  
# 开发工具  :  PyCharm

import subprocess
import sys
import time
import subprocess
import os
from pathlib import Path
import re


resume_keyword = None
def handle_log_errors():
    log_directory = current_dir / 'logs'
    # 获取所有.log文件，按修改时间排序，取最后一个
    latest_log = sorted(log_directory.glob('*.log'), key=os.path.getmtime, reverse=True)[0]

    with open(latest_log, 'r', encoding='utf-8') as file:
        keywords = []
        for line in file:
            # 检查行中是否包含"keyword:**"格式
            if 'keyword' in line:
                match = re.search(r'keyword: (\w+),', line)
                if match:
                    extracted_word = match.group(1)
                    keywords.append(extracted_word)

    last_keyword = keywords[-1] if keywords else None
    if last_keyword:
        resume_keyword = last_keyword
        print(f"从日志中提取的最后一个关键词(重启开始关键词）: {resume_keyword}")
    else:
        print("未在日志中找到关键词格式为 'keyword:**' 的行。")


if __name__ == '__main__':
    while(True):
        try:
            current_dir = Path(__file__).parent
            crawler_script = str(current_dir / 'twitter_crawler.py')
            command = ['python', crawler_script] if resume_keyword else ['python', crawler_script, str(resume_keyword)]
            process = subprocess.run(command, capture_output=True, text=True)

            if process.returncode != 0:
                print("crawler.py执行出错，错误信息如下：")
                print(process.stderr)
                handle_log_errors()
            else:
                break;
        except Exception as e:
            print(f"执行过程中发生未知错误: {e}")

        # 打印提示信息
        print("重新启动中...")

        # 等待一段时间再重新启动，避免频繁重启
        time.sleep(5)
    print("爬取结束，全部成功！！！")
