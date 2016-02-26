# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import redis
import MySQLdb
import MySQLdb.cursors

class ProvincePipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            db = 'driving',
            user = 'root',
            passwd = '123456',
            cursorclass = MySQLdb.cursors.DictCursor,
            charset = 'utf8',
            use_unicode = False
        )

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self, tx, item):
        tx.execute('insert into urls values (%s, %s, %s)', ('NULL', item['url'], item['district']))

class SchoolPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            db = 'driving',
            user = 'root',
            passwd = '123456',
            cursorclass = MySQLdb.cursors.DictCursor,
            charset = 'utf8',
            use_unicode = False
        )

        self.redispool = redis.ConnectionPool(
            host='localhost', 
            port=6379, 
            db=0
        )

        self.redis = redis.Redis(connection_pool=self.redispool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)

        #save to redis
        key = 'SCHOOL:URL:SET:DONE'
        self.redis.sadd(key, item['url']);

        return item

    def _conditional_insert(self, tx, item):
        tx.execute('insert into kjz_school\
        (name,recruit_area,telphone,logo,summary,introduce,special_service,address,expense_fee,students_cnt,coach_cnt,province,city,location)\
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (
            item['name'],
            item['ranges'], 
            item['tel'], 
            item['pic'], 
            item['summary'],
            item['intro'],
            item['service'], 
            item['address'], 
            item['cost'], 
            item['students'], 
            item['coaches'], 
            item['province'], 
            item['city'], 
            item['location']
        ))