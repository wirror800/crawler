#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: WirrorYin
# @Date:   2015-05-28 16:19:27
# @Last Modified by:   WirrorYin
# @Last Modified time: 2015-06-01 19:12:32
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request
from driving.items import SchoolItem
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import os
import sys
import json
import redis
import urllib
import urlparse

class SchoolSpider(Spider):
    name="school"
    allowed_domains=["jiaxiaozhijia.com"]

    start_urls=[]

    def __init__(self, name=None, **kwargs):
        Spider.__init__(self, name)

        self.conn = MySQLdb.connect(
            host="localhost", 
            user="root", 
            passwd="123456", 
            db="driving", 
            charset="utf8"
        )
        self.cursor = self.conn.cursor()

        self.redispool = redis.ConnectionPool(
            host='localhost', 
            port=6379, 
            db=0
        )

        self.redis = redis.Redis(connection_pool=self.redispool)

        urls = self.getUrls();
        for url in urls:
            done = self.hasCrawled(url)
            if done==False:
                self.start_urls.append(url)
                self.cacheTodo(url)

        #print len(self.start_urls)

    #分析页面
    def parse(self,response):
        hxs = Selector(response)
        info = hxs.xpath('//div[@class="jiakaobaodian-pull-left jiaxiao-general"]/dl')
        item=SchoolItem()
        item['name'] = info.xpath('dt/span/text()').extract()[0]

        costTxt = info.xpath('dd[2]/strong/b/text()')
        item['cost'] = costTxt.extract()[0] if costTxt else 0

        telTxt = info.xpath('dd[3]/span/b/text()')
        item['tel'] = telTxt.extract()[0] if telTxt else ''

        studentsTxt = info.xpath('dd[4]/span[1]/b/text()')
        item['students'] = studentsTxt.extract()[0] if studentsTxt else 0

        coachesTxt = info.xpath('dd[4]/span[2]/b/text()')
        item['coaches'] = coachesTxt.extract()[0] if coachesTxt else 0

        ranges = info.xpath('dd[5]/div/span')
        rangeArr = []
        for r in ranges:
            rangeTxt = r.xpath('text()')
            if rangeTxt:
                rangeArr.append(rangeTxt.extract()[0])
        item['ranges'] = ','.join(rangeArr)

        item['pic'] = hxs.xpath('//div[@class="jiakaobaodian-pull-left jiaxiao-logo"]/img/@src').extract()[0]

        
        summaryTxt = hxs.xpath('//div[@class="introduce-summary"]')
        item['summary'] = summaryTxt.xpath('string(.)').extract()[0] if summaryTxt else ''

        introTxt = hxs.xpath('//div[@class="introduce-all"]')
        item['intro'] = introTxt.xpath('string(.)').extract()[0] if introTxt else ''
        item['address'] = ''
        item['service'] = ''

        #locationTxt = hxs.xpath('//div[@class="map-operator clearfix"]/a[class="left"]/@href')
        #if locationTxt:
        #    baiduLocation = locationTxt.extract()[0]
        #    result = urlparse.urlparse(baiduLocation)
        #    params = urlparse.parse_qs(result.query,True)
        #    item['location'] = params['location'][0]
        #else:
        item['location'] = ''

        picInfo = self.savePic(response.url, item['pic'].replace('!640.400', ''))
        item['province'] = picInfo[0]
        item['city'] = picInfo[1]
        item['pic'] = picInfo[2]
        item['url'] = response.url

        #save image list
        images = hxs.xpath('//li[@class="jiakaobaodian-jiaxiao-content-photos"]/div[2]/ul/li')
        for img in images:
            src = img.xpath('a/img/@src')
            if src:
                self.savePic(response.url, src.extract()[0].replace('!waterfall', ''), 'dir')

        items=[]
        items.append(item)
        
        return items

    def savePic(self, locationUrl, imgUrl, type='file'):
        imgCode = self.getCode(locationUrl)
        urlId = int(imgCode - imgCode%1000000)/1000000
        districtCode = int(imgCode%1000000)
        cityCode = districtCode - districtCode%100
        provinceCode = districtCode - districtCode%10000
        if type=="dir":
            picRelativeDir = ''.join(['/downloads/',str(provinceCode), '/', str(cityCode), '/', str(urlId)])
            picAbsDir = ''.join([os.getcwd(), picRelativeDir])
            #picExtension = os.path.splitext(imgUrl)[1]
            picName = os.path.basename(imgUrl)
            picUrl = ''.join([picRelativeDir, '/', picName])
            picPath = ''.join([os.getcwd(),picUrl])
        else:
            picRelativeDir = ''.join(['/downloads/',str(provinceCode), '/', str(cityCode)])
            picAbsDir = ''.join([os.getcwd(), picRelativeDir])
            picExtension = os.path.splitext(imgUrl)[1]
            picUrl = ''.join([picRelativeDir, '/', str(urlId), picExtension])
            picPath = ''.join([os.getcwd(),picUrl])

        if not os.path.exists(picAbsDir):
            os.makedirs(picAbsDir) 
        urllib.urlretrieve(imgUrl, picPath)

        return [provinceCode, cityCode, picUrl]

    def getUrls(self):
        key = 'SCHOOL:URL:SET:TODO'
        urls = self.redis.smembers(key)

        if len(urls)==0:
            key = 'SCHOOL:URL:SET'
            urls = self.redis.zrange(key, 0, -1)
            
        return urls

    def getCode(self, url):
        key = 'SCHOOL:URL:SET'
        code = self.redis.zscore(key, url)
        return code

    def cacheTodo(self, url):
        key = 'SCHOOL:URL:SET:TODO'
        self.redis.sadd(key, url)

    def hasCrawled(self, url):
        key = 'SCHOOL:URL:SET:DONE'
        isMember = self.redis.sismember(key, url);
        
        return True if isMember>0 else False
