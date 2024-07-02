# coding=utf-8
# 开发人员  ：  熊超
# 开发时间  ：  2023/12/28  14:29
# 文件名称  :  utils.PY
# 开发工具  :  PyCharm
import json
import time
import string

from selenium import webdriver
from crawlers import setting
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import ftfy


def get_chrome_options(need_proxy=True):
    options = webdriver.ChromeOptions()
    if need_proxy:
        options.add_argument("--proxy-server={}".format(setting.proxy))
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.39 Safari/537.36"')
    options.add_argument('--start-maximized')
    options.add_argument('headless')
    return options


def create_webdriver_instance(url, cookie_index):
    br = webdriver.Chrome(service=Service(executable_path=setting.chrome_driver_path),
                          options=get_chrome_options(True))
    br.get(url)
    path = './profile/twitter_cookies_' + str(cookie_index) + '.json'
    with(open(path, 'r', ) as f):
        cookies = json.load(f)
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
            # print(cookie)
        br.add_cookie(cookie)
    br.refresh()
    time.sleep(1)
    return br


# 对文本进行清洗，去除非法字符
def remove_invalid_chars(text):
    filtered_string = filter(lambda x: x in string.printable, text)
    return "".join(filtered_string)


# 解析字符串时间，返回标准格式的日期
def parse_date_format(time_text):
    if "年" in time_text:
        return time_text.replace("年", "-").replace("月", "-").replace("日", "")
    else:
        res = pd.to_datetime(time_text)
        return str(res.date())


def find_element_by_xpath(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element
    except exceptions.NoSuchElementException as e:
        print(e)
    return None
