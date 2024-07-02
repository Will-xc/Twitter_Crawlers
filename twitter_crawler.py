# coding=utf-8
# 开发人员  ：  熊超
# 开发时间  ：  2023/12/28  14:21
# 文件名称  :  twitter_crawler.PY
# 开发工具  :  PyCharm

import csv
import json
import logging
import os.path
import sys

from selenium import webdriver

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common import action_chains
from crawlers import utils, setting
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
from datetime import datetime, timedelta
import config

current_time = datetime.now().strftime("%Y%m%d-%H%M%S")

logging.basicConfig(filename='./logs/crawlers_'+current_time+'.log', level=logging.INFO, encoding='utf-8')

def login_twitter(index):
    br = webdriver.Chrome(service=Service(executable_path=setting.chrome_driver_path),
                          options=utils.get_chrome_options(True))
    br.get("https://twitter.com/i/flow/login")
    time.sleep(3)
    # 输入邮箱并点击下一步
    input_box = br.find_element(By.XPATH, "//input")
    input_box.send_keys("*******@163.com")
    button = br.find_element(By.XPATH,
                             '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]/div')
    action_chains.ActionChains(br).move_to_element(button).click().perform()

    time.sleep(1)
    input_box = br.find_element(By.XPATH, '//input[@name="password"]')
    input_box.send_keys("********")
    button = br.find_element(By.XPATH,
                             '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button/div')
    action_chains.ActionChains(br).move_to_element(button).click().perform()

    # 输入邮箱并点击下一步
    # time.sleep(3)
    # input_box = br.find_element(By.XPATH, '//input')
    # input_box.send_keys("@WadeWil8")
    # button = br.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div')
    # action_chains.ActionChains(br).move_to_element(button).click().perform()
    # 输入密码并点击下一步

    time.sleep(6)
    cookies = br.get_cookies()
    # print(cookies)
    # print(type(cookies))
    path = './profile/twitter_cookies_' + str(index) + '.json'
    with(open('./profile/twitter_cookies_2.json', 'w') as f):
        f.write(json.dumps(cookies))


# file为visited的文件操作符，以支持实时写该文件
def get_trend_tweet(trends_limit=5, visited=[], out_path="./data", visited_path="./data"):
    br = utils.create_webdriver_instance("https://twitter.com/i/trends", 2)
    last_pos = None
    end_of_page = False
    trend_tweets = {}

    # 获得所有trend card
    while not end_of_page and len(trend_tweets) <= trends_limit:
        trend_cards = collect_all_trend_from_current_view(br)
        for trend_card in trend_cards:
            trend_name = ""
            # 记录trend名称
            try:
                trend_name = trend_card.find_element(By.XPATH, './div/div[2]/span').text
                print("trend_name", trend_name)
            except exceptions.NoSuchElementException as e:
                print(e)
            # # 记录trend总发文量
            # try:
            #     trend_post_num = trend_card.find_element(By.XPATH, './div/div[3]/span').text
            #     print("trend_post_num", trend_post_num)
            # except exceptions.NoSuchElementException as e:
            #     print(e)

            # 新建标签页，并进入热点推文列表页面
            if trend_name in trend_tweets.keys():
                continue

            # 筛选推文条件
            current_date = datetime.now()
            # 计算十天前的日期
            ten_days_ago = current_date - timedelta(days=11)
            # 推文发布截止日期为10天前
            until_time = ten_days_ago.strftime("%Y-%m-%d")

            q = "{} until:{}".format(trend_name.replace("#", ""), until_time)
            trend_url = "https://twitter.com/search?q=" + q
            new_tab = 'window.open("' + trend_url + '");'
            br.execute_script(new_tab)
            br.switch_to.window(br.window_handles[-1])

            all_data = get_tweets_data(br, visited, out_path=out_path, trend_name=trend_name, visited_path=visited_path)
            trend_tweets[trend_name] = all_data

            # 删除标签页并切换句柄
            br.close()
            br.switch_to.window(br.window_handles[-1])

        # 向下滑动窗口
        last_pos, end_of_page = scroll_down_page(br, last_pos)


def get_tweets_data(driver, visited, out_path, trend_name="", tweets_limit=1000, visited_path=""):
    last_pos = None
    end_of_page = False
    all_data = []
    try:
        while not end_of_page and len(all_data) < tweets_limit:
            tweet_cards = collect_all_tweets_from_current_view(driver)
            for tweet_card in tweet_cards:
                url_el = tweet_card.find_element(By.XPATH, './/time/parent::a')
                url = url_el.get_attribute("href")
                if url in visited:
                    continue
                with open(visited_path, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                data = extract_data_from_current_tweet_card(driver, url)
                if not data == None:
                    if not trend_name == "":
                        data.append(trend_name)
                    save_tweet_data_to_csv(data, out_path)
                    visited.append(url)
                    all_data.append(data)
                    logging.info(f'data: {data} saved to {out_path}')
            last_pos, end_of_page = scroll_down_page(driver, last_pos)
    except exceptions.NoSuchElementException as e1:
        print(e1)
    except exceptions.TimeoutException as e2:
        print(e2)
    return all_data


def save_tweet_data_to_csv(records, filepath, mode='a+'):
    header = ['tweet_url', 'publisher_name', 'followers', 'followings', 'post_time', 'now_time', 'tweet_text'
        , 'comments', 'retweets', 'likes', 'views', 'bookmarks', 'image_urls', 'trend_name']
    with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)
        if records:
            row = records
            writer.writerow(row)
    f.close()


def extract_data_from_current_tweet_card(driver, url):
    # 新建标签页，并进入推文详情页
    new_tab = 'window.open("' + url + '");'
    driver.execute_script(new_tab)
    driver.switch_to.window(driver.window_handles[-1])

    try:
        tweet_card = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//article[@tabindex="-1"]'))
        )
    except exceptions.TimeoutException as e:
        print(e)
        return

    image_urls = []
    # 鼠标悬停以获取推文发布者的follower数量和following数量
    try:
        element = WebDriverWait(tweet_card, 10).until(
            EC.presence_of_element_located((By.XPATH, './/div[@data-testid="User-Name"]/div[2]/div/div[1]')))
        ActionChains(driver).move_to_element(element).perform()
    except exceptions.TimeoutException as e:
        print(e)
    time.sleep(2)
    try:
        followers = driver.find_element(By.XPATH,
                                        '//*[@id="layers"]/div[2]/div[1]/div/div/div/div/div/div/div/div[4]/div/div[2]/a/span[1]/span').text
    except exceptions.NoSuchElementException as e:
        print(e)
        followers = "0"

    try:
        followings = driver.find_element(By.XPATH,
                                         '//div[@id="layers"]//div[@data-testid="HoverCard"]/div/div/div[4]//a[1]/span[1]/span').text
    except exceptions.NoSuchElementException as e:
        print(e)
        followings = "0"

    try:
        publisher_name = tweet_card.find_element(By.XPATH,
                                                 './/div[@data-testid="User-Name"]/div[2]/div/div[1]//span').text
    except exceptions.NoSuchElementException as e:
        print(e)
        publisher_name = ""

    try:
        post_time = tweet_card.find_element(By.XPATH, './/time').get_attribute('datetime')
    except exceptions.NoSuchElementException as e:
        print(e)
        post_time = ""

    try:
        tweet_text = tweet_card.find_element(By.XPATH, './/div[@data-testid="tweetText"]//span').text
    except exceptions.NoSuchElementException as e:
        print(e)
        tweet_text = ""

    try:
        features = tweet_card.find_elements(By.XPATH, './/span[@data-testid="app-text-transition-container"]')
        views = features[0].text if len(features) == 5 else "0"
        comments = features[1].text if len(features) == 5 else features[0].text
        retweets = features[2].text if len(features) == 5 else features[1].text
        likes = features[3].text if len(features) == 5 else features[2].text
        bookmarks = features[4].text if len(features) == 5 else features[3].text
    except exceptions.NoSuchElementException as e:
        print(e)
        views = "0"
        comments = "0"
        retweets = "0"
        likes = "0"
        bookmarks = "0"
    except IndexError as ie:
        logging.debug(f'tweet: {url}, IndexError: {ie}')
        views = "0"
        comments = "0"
        retweets = "0"
        likes = "0"
        bookmarks = "0"

    # 获得推文中的图片，若附带的为视频则获取视频的封面
    try:
        images = tweet_card.find_elements(By.XPATH, './/div[@data-testid="tweetPhoto"]/img')
        for image in images:
            image_urls.append(image.get_attribute("src"))
    except exceptions.NoSuchElementException as e:
        print(e)
    try:
        poster_images = tweet_card.find_elements(By.XPATH, './/div[@data-testid="videoComponent"]//video')
        for poster_image in poster_images:
            image_urls.append(poster_image.get_attribute("poster"))
    except exceptions.NoSuchElementException as e:
        print(e)

    # 获得推文的评论集合
    comment_texts = {}
    comment_dict = {}
    try:
        last_pos = None
        end_of_page = False
        if comments == "0":
            raise exceptions.TimeoutException("该推文没有评论")
        while not end_of_page:
            comment_articles = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, '//article[@tabindex="0"]'))
            )
            for comment_article in comment_articles:
                try:
                    comment_text = utils.remove_invalid_chars(comment_article.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text)
                except exceptions.NoSuchElementException as e1:
                    comment_text = ""
                except exceptions.StaleElementReferenceException as e2:
                    comment_text = ""
                comment_likes = "0"
                try:
                    comment_likes = comment_article.find_elements(By.XPATH, './/span[@data-testid="app-text-transition-container"]')[2].text
                    if comment_likes == "":
                        comment_likes = "0"
                except exceptions.StaleElementReferenceException as e:
                    comment_likes = ""
                comment_texts[comment_text] = comment_likes
            last_pos, end_of_page = scroll_down_page(driver, last_pos)
    except exceptions.TimeoutException as e:
        print("该推文没有评论：", url, e.msg)

    # 将推文的评论单独进行存储，存储之后的文件需要再前面和后面增加[]并删除文件最后的, 以支持作为json列表进行解析
    comment_dict[url] = comment_texts
    with open(config.comments_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(comment_dict) + ",")
    f.close()

    # 关闭该标签页并切换句柄
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])

    now_time = time.asctime()

    data = (url, publisher_name, followers, followings, post_time, now_time, utils.remove_invalid_chars(tweet_text),
            comments, retweets, likes, views, bookmarks, image_urls)
    print("data:", data)
    return list(data)


def scroll_down_page(driver, last_position, num_seconds_to_load=1.5, scroll_attempt=0, max_attempts=5):
    """页面滚动  因为页面元素会动态刷新，所以每次滚动合适的长度"""
    end_of_scroll_region = False
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        # if scroll_attempt < max_attempts:
        #     end_of_scroll_region = True
        # else:
        #     scroll_down_page(last_position, curr_position, scroll_attempt + 1)
        end_of_scroll_region = True
    last_position = curr_position
    return last_position, end_of_scroll_region


def collect_all_tweets_from_current_view(driver, limit=25):
    """The page is continously loaded, so as you scroll down the number of tweets returned by this function will
     continue to grow. To limit the risk of 're-processing' the same tweet over and over again, you can set the
     `lookback_limit` to only process the last `x` number of tweets extracted from the page in each iteration.
     You may need to play around with this number to get something that works for you. I've set the default
     based on my computer settings and internet speed, etc..."""
    page_cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))
    if len(page_cards) <= limit:
        return page_cards
    else:
        return page_cards[-limit:]


def collect_all_trend_from_current_view(driver, limit=25):
    trend_cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="trend"]')))
    if len(trend_cards) <= limit:
        return trend_cards
    else:
        return trend_cards[:limit]


def crawl_trend_tweets():
    visited_path = './profile/visited_trend.txt'
    out_path = './data/trend_tweets_trend.csv'
    visited = []
    if os.path.exists(visited_path):
        with open(visited_path, 'r', encoding='utf-8') as f:
            visited = f.readlines()
            visited = [x.strip() for x in visited]
    # 创建一个新文件
    if not os.path.exists(out_path):
        save_tweet_data_to_csv(None, out_path, mode='w')
    get_trend_tweet(trends_limit=5, visited=visited, out_path=out_path, visited_path=visited_path)


def craw_keyword_tweets(keyword):
    visited_path = config.visitied_file
    out_path = config.tweets_file
    visited = []
    if os.path.exists(visited_path):
        with open(visited_path, 'r', encoding='utf-8') as f:
            visited = f.readlines()
            visited = [x.strip() for x in visited]
    # 创建一个新文件
    if not os.path.exists(out_path):
        save_tweet_data_to_csv(None, out_path, mode='w')

    # 先注入cookie进入首页再进行页面跳转，否则会进入登录页面

    # 筛选推文条件
    current_date = datetime.now()
    # 计算十天前的日期
    ten_days_ago = current_date - timedelta(days=11)
    # 推文发布截止日期为10天前
    until_time = ten_days_ago.strftime("%Y-%m-%d")
    # 最少评论数
    min_replies = 1
    # 最少点赞数
    min_faves = 1

    q = "{} until:{}".format(keyword, until_time)
    br = utils.create_webdriver_instance("https://twitter.com", 2)
    br.get("https://twitter.com/search?lang=en&q={}&src=typed_query&f=top".format(q))
    time.sleep(3)
    get_tweets_data(br, visited, out_path=out_path, trend_name=keyword, visited_path=visited_path)


if __name__ == '__main__':
    # login_twitter(2)
    # crawl_trend_tweets()

    keywords = []
    # 政治
    politics = "president、government、congress、election、international relations、The bill passed、Democratic party、Republican、immigrant、civil rights、taxation、Healthcare、Environmental Policy、foreign policy、war、conflict、Emmanuel Macron、human rights、Demonstrations and protests、legislation"
    politics_keywords = politics.split("、")
    for politics_keyword in politics_keywords:
        keywords.append(politics_keyword)

    # 经济
    economics = "GDP、inflation"
    economics_keywords = economics.split("、")
    for economics_keyword in economics_keywords:
        keywords.append(economics_keyword)

    # 社会
    social = "football、NBA、world cup"
    social_keywords = social.split("、")
    for social_keyword in social_keywords:
        keywords.append(social_keyword)

    # 科技
    technology = "Google、Apple、Microsoft"
    technology_keywords = technology.split("、")
    for technology_keyword in technology_keywords:
        keywords.append(technology_keyword)

    # 文化
    culture = "Chinese traditional culture、Chinese characters"
    culture_keywords = culture.split("、")
    for culture_keyword in culture_keywords:
        keywords.append(culture_keyword)

    # 开始依据关键词爬取数据
    keywords_num = len(keywords)
    last_keyword = sys.argv[1] if sys.argv[1] != 'None' else "president"  # 上次停止处的关键词
    last_keyword_index = keywords.index(last_keyword)
    logging.info("开始爬取")
    for index, keyword in enumerate(keywords[last_keyword_index:]):
        logging.info(f'keyword: {keyword}, index: {index+1}')
        craw_keyword_tweets(keyword)
