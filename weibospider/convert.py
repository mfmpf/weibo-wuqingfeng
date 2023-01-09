

data = {'tweets':{},"user":{}}

import json
import redis
import random
import requests


# 微博用户ID集合
# 微博用户个人信息
# 微博用户微博集合
# 每条微博详情
# 每条微博图片集合
redis_weibo_users_key          = 'weibo:users'
redis_weibo_user_info_key      = 'weibo:userid:{userid:s}'
redis_weibo_user_tweets_key    = 'weibo:userid:{userid:s}:tweets'
redis_weibo_tweet_key          = "weibo:tweet:mblogid:{mblogid:s}"
redis_weibo_tweet_markdown_key = "weibo:tweet:mblogid:{mblogid:s}:markdown"
redis_weibo_tweet_photos_key   = "weibo:tweet:mblogid:{mblogid:s}:photos"
redis_weibo_tweet_created_key  = "weibo:tweet:mblogid:{mblogid:s}:created"
redis_weibo_tweet_url_key      = "weibo:tweet:mblogid:{mblogid:s}:url"
redis_weibo_tweet_content_key  = "weibo:tweet:mblogid:{mblogid:s}:content"

import os
USERID = os.getenv('WEIBO_USER')
GITHUB_ACTION_REPOSITORY = os.getenv('OWNER_REPO')


r = redis.StrictRedis(host='localhost', port=29384, db=6)
all_tweets = r.smembers(redis_weibo_user_tweets_key.format(userid=USERID))
print(all_tweets)


pic_url_base = {
    # "thumbnail":"https://wx4.sinaimg.cn/wap180/{pic_id:s}.jpg",
    "bmiddle"  :"https://wx4.sinaimg.cn/wap360/{pic_id:s}.jpg",
    # "large"    :"https://wx4.sinaimg.cn/orj960/{pic_id:s}.jpg",
    "original" :"https://wx4.sinaimg.cn/orj1080/{pic_id:s}.jpg",
    # "largest"  :"https://wx4.sinaimg.cn/large/{pic_id:s}.jpg",
    # "mw2000"   :"https://wx4.sinaimg.cn/mw2000/{pic_id:s}.jpg"
}

# 略缩图和原图
pic_cdn_url_base = "https://raw.githubusercontent.com/{owner_repository:s}/output/output/picture/bmiddle_{pic_id:s}.jpg"
pic_original_cdn_url_base = "https://raw.githubusercontent.com/{owner_repository:s}/output/output/picture/original_{pic_id:s}.jpg"

def download_pics(pic_id):
    print("Downloading pictures...",pic_id)
    for url_base in pic_url_base:
        url = pic_url_base[url_base].format(pic_id=pic_id)
        r = requests.get(url)
        print("Downloading ",url)
        with open('../output/picture/'+url_base + '_' + pic_id + '.jpg', "wb") as f:
            f.write(r.content)


with open("../output/user_spider.jsonl", "r") as fo:
    line = fo.readline()
    user_data = json.loads(line)
    assert user_data["_id"] == str(USERID)
    data["user"] = user_data
    redis_weibo_user_info = redis_weibo_user_info_key.format(userid=USERID)
    r.sadd(redis_weibo_users_key, USERID)
    r.set(redis_weibo_user_info, json.dumps(user_data))
    print(USERID)
    print(redis_weibo_user_info)


def tweet_to_markdown(tweet):
    """
    将微博转换为markdown格式的文档
    """
    pics_div = """
    <div id=\"{div_id:s}\" class=\"justified-gallery weibo-gallery\">
        {pics_content:s}
    </div>
    """
    pics_content_base = """
        <a data-fancybox=\"{div_id:s}\" href=\"{pic_original_url:s}\">
            <img no-lazy src=\"{pic_url:s}\" >
        </a>
    """
    pics_content = ""
    div_id = hex(random.randint(1e9, 9e9))
    tweet_content = tweet["content"].replace('\n', '<br>')
    for pic_id in tweet["pic_urls"]:
        pic_url = pic_cdn_url_base.format(pic_id=pic_id,owner_repository=GITHUB_ACTION_REPOSITORY)
        pic_original_url = pic_original_cdn_url_base.format(pic_id=pic_id,owner_repository=GITHUB_ACTION_REPOSITORY)
        pics_content += pics_content_base.format(pic_url=pic_url, pic_original_url=pic_original_url, div_id=div_id)
    if tweet["pic_num"] == 0:
        return tweet_content
    else :
        return tweet_content+pics_div.format(pics_content=pics_content,div_id=div_id)


# 数据库中的
all_tweets = r.smembers(redis_weibo_user_tweets_key.format(userid=USERID))
def tweet_to_redis(tweet):
    print("从json到数据库")
    print("保存微博 ",tweet["mblogid"])
    redis_key_1 = redis_weibo_user_tweets_key.format(userid=USERID)
    redis_key_2 = redis_weibo_tweet_key.format(mblogid=tweet["mblogid"])
    redis_key_3 = redis_weibo_tweet_markdown_key.format(mblogid=tweet["mblogid"])
    r.sadd(redis_key_1, tweet["mblogid"])                            # 所有mblogid的集合
    r.set(redis_key_2, json.dumps(tweet))                            # 每个mblogid对应的文本，可解析为json
    r.set(redis_key_3, tweet_to_markdown(tweet))                     # 每个mblogid对应的文本，可解析为json
    # 如果含有转发的微博
    if 'retweeted' in tweet:
        retweet_mblogid = tweet['retweeted']['mblogid']
        redis_key_3 = redis_weibo_tweet_markdown_key.format(mblogid=retweet_mblogid)
        r.set(redis_key_3, tweet_to_markdown(tweet['retweeted']))
    # 避免重复下载照片
    if tweet["mblogid"].encode('utf-8') not in all_tweets:
        for pic_id in tweet["pic_urls"]:
            download_pics(pic_id)
        if 'retweeted' in tweet:
            for pic_id in tweet['retweeted']['pic_urls']:
                download_pics(pic_id)


with open("../output/tweet_spider.jsonl", "r") as fo:
    for line in fo.readlines():
        tweet = json.loads(line)
        tweet_to_redis(tweet)

r.save()

file = '../output/tweets.json'
tweets = []
all_tweets = r.smembers(redis_weibo_user_tweets_key.format(userid=USERID))

for mblogid in all_tweets:
    redis_key_2 = redis_weibo_tweet_key.format(mblogid=mblogid.decode())
    redis_key_3 = redis_weibo_tweet_markdown_key.format(mblogid=mblogid.decode())
    tweet = json.loads(r.get(redis_key_2).decode())
    tweet['content'] = r.get(redis_key_3).decode()
    if 'retweeted' in tweet:
        retweeted_mblogid = tweet['retweeted']["mblogid"]
        redis_key_3 = redis_weibo_tweet_markdown_key.format(mblogid=retweeted_mblogid)
        tweet['retweeted']['content'] = r.get(redis_key_3).decode()
    tweets.append(tweet)

tweets = sorted(tweets, key=lambda s: s['created_at'], reverse=True)

data["tweets"] = tweets

with open(file, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)






