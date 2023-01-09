#!/usr/bin/env python
# encoding: utf-8
"""
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import os
import json
from scrapy import Spider
from scrapy.http import Request
from spiders.common import parse_tweet_info
USERID   = os.getenv('WEIBO_USER')
MAX_PAGE = os.getenv('MAX_PAGE')



def parse_long_tweet(response):
    data = json.loads(response.text)['data']
    item = response.meta['item']
    item['content'] = data['longTextContent']
    yield item

def parse_long_retweeted(response):
    data = json.loads(response.text)['data']
    item = response.meta['item']
    item['retweeted']['content'] = data['longTextContent']
    yield item

class TweetSpider(Spider):
    """
    用户推文数据采集
    """
    name = "tweet_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里user_ids可替换成实际待采集的数据
        user_ids = [USERID]
        for user_id in user_ids:
            url = f"https://weibo.com/ajax/statuses/mymblog?uid={user_id}&page=1"
            print(url)
            yield Request(url, callback=self.parse, meta={'user_id': user_id, 'page_num': 1})
    
    def parse(self, response, **kwargs):
        """
        网页解析
        """
        data = json.loads(response.text)
        tweets = data['data']['list']
        print("result:",tweets)
        for tweet in tweets:
            item = parse_tweet_info(tweet)
            del item['user']
            if item['isLongText'] or ():
                url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
                yield Request(url, callback=parse_long_tweet, meta={'item': item})
            elif 'retweeted' in item and item['retweeted']['isLongText']:
                url = "https://weibo.com/ajax/statuses/longtext?id=" + item['retweeted']['mblogid']
                yield Request(url, callback=parse_long_retweeted, meta={'item': item})
            else:
                yield item

        user_id, page_num = response.meta['user_id'], response.meta['page_num']
        if tweets and page_num < int(MAX_PAGE):
            page_num += 1
            url = f"https://weibo.com/ajax/statuses/mymblog?uid={user_id}&page={page_num}"
            yield Request(url, callback=self.parse, meta={'user_id': user_id, 'page_num': page_num})
