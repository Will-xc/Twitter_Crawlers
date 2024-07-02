# Twitter_Crawlers

针对Twitter的爬虫，使用selenium进行实现。

**需注意：在使用前需开启魔法上网工具**

# 1.主要功能

（1）通过**关键词**进行检索并爬取相关每条推文的的信息，爬取信息包括：**（推文链接、发布者用户名、发布者粉丝数、发布者following人数、发文时间、当前时间、推文文字内容、评论量、转发量、点赞量、浏览量、收藏量、推文附带图片链接、关键词名称）**。其中图片链接以列表形式链接，若附带视频则爬取视频封面。

示例如下：

| tweet_url                                                    | publisher_name  | followers | followings | post_time                | now_time                 | tweet_text                                                   | comments | retweets | likes | views | bookmarks | image_urls                                                   | trend_name |
| ------------------------------------------------------------ | --------------- | --------- | ---------- | ------------------------ | ------------------------ | ------------------------------------------------------------ | -------- | -------- | ----- | ----- | --------- | ------------------------------------------------------------ | ---------- |
| https://twitter.com/ShotGun_Bonnie/status/1759728039817060722 | @ShotGun_Bonnie | 34.1K     | 26.2K      | 2024-02-19T23:53:53.000Z | Sat Mar  2 15:59:21 2024 | Checkout the crowd of supporters that gathered outside of Trump International Golf Club for Presidents Day | 4        | 37       | 79    | 1,569 | 1         | ['https://pbs.twimg.com/amplify_video_thumb/1759689794546733057/img/WxtOwpah4ZdsfHQE.jpg'] | president  |

才外，**还会爬取每条推文的所有文字评论及其点赞数**，示例如下：

```json
{"https://twitter.com/ShotGun_Bonnie/status/1759728039817060722": 
{"Would have loved to have a merchandise booth there today. Those folks will buy ANYTHING!": "0",
 "": "3", 
 "BIDEN was taking a nap NO ONE SHOWED UP TO WISH HIM HAPPY PRESIDENTS DAY": "1"}
 },
```

（2）爬取Twitter中的Trend的相关推文，可以设置Trend数和每个Trend的爬取数量。

# 2.使用流程

（1）首先在setting.py中修改chrome_driver存放的地址，将该地址修改为你实际存放的绝对路径

```python
# chrome_driver的地址
chrome_driver_path = 'E:\\***\\chromedriver.exe'
```

（2）若需要设置代理，在setting.py中修改对应的代理位置，若不需要开启代理，则在twitter_crawler.py中将代理关闭，代码如下

```python
# 代理地址
proxy = "127.0.0.1:7890"
```

```python
# twitter_crawler.py中找到这一句并把参数改为False
br = webdriver.Chrome(service=Service(executable_path=setting.chrome_driver_path),
                      options=utils.get_chrome_options(False))
```

（3）在twitter_crawler.py中的login_twitter方法中将邮箱、密码替换成自己的

```python
# 输入邮箱并点击下一步
input_box = br.find_element(By.XPATH, "//input")
input_box.send_keys("******@163.com")
button = br.find_element(By.XPATH,
                         '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]/div')
action_chains.ActionChains(br).move_to_element(button).click().perform()

time.sleep(1)
input_box = br.find_element(By.XPATH, '//input[@name="password"]')
input_box.send_keys("******")
```

（4）在twitter_crawler.py的main方法中将其他代码注释，单独运行一下login_twitter方法进行一次登录

```python
if __name__ == '__main__':
    # login_twitter(2)
```

（5）此时，已经将cookie保存下来了，那么将login_twitter方法进行注释，在main方法中输入自己需要爬取的关键词。**重点是构造keywords集合，也就是搜索关键词集合**

```python
keywords = []
# 政治
politics = "president、government"
politics_keywords = politics.split("、")
for politics_keyword in politics_keywords:
    keywords.append(politics_keyword)

# 经济
economics = "GDP、inflation"
economics_keywords = economics.split("、")
for economics_keyword in economics_keywords:
    keywords.append(economics_keyword)

# 社会
social = "football、NBA"
social_keywords = social.split("、")
for social_keyword in social_keywords:
    keywords.append(social_keyword)

# 科技
technology = "Google、Appl"
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
```

（6）启动main.py即可开始爬取。



**其他注意事项：**

1.Trend功能的爬取需要在twitter_crawler.py的main方法中进行实现，由于时间和个人需求原因没有写了，不过也可以参照关键词爬取写一下，main.py中的重启逻辑也需要重写。

2.在运行过程中会生成log日志以查看爬取进度和已爬取推文信息

3.爬取的推文信息保存在生成的data目录的.csv文件中，评论信息保存在json文件中。



# 说明

1.由于时间原因该爬虫代码不是很规范，复用性和可维护性不足，后期也不一定会维护。

2.本爬虫仅供个人欣赏、学习之用，任何组织和个人不得公开传播或用于任何商业盈利用途，否则一切后果由该组织或个人承担。









