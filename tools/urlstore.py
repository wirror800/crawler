#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: WirrorYin
# @Date:   2015-05-29 07:56:52
# @Last Modified by:   WirrorYin
# @Last Modified time: 2015-06-05 16:52:43
from twisted.enterprise import adbapi
from PIL import Image, ImageFile
import MySQLdb
import MySQLdb.cursors
import redis
import sys, getopt
import urllib2
import urllib
import cookielib
import json
import os
import shutil
import filecmp

ImageFile.LOAD_TRUNCATED_IMAGES = True
class UrlStore(object):
    def __init__(self):
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

    def initRedis(self):
        urls = self.getUrls()
        key = 'SCHOOL:URL:SET'
        for url in urls:
            #self.redis.sadd(key, url[0]);
            self.redis.zadd(key, url[1], int(url[0])*1000000+int(url[2]));

    def clearRedis(self):
        urls = self.getUrls()
        keys = ['SCHOOL:URL:SET:TODO','SCHOOL:URL:SET:DONE', 'SCHOOL:ADDR:SET', 'SCHOOL:WATER:SET']
        for key in keys:
            total = self.redis.scard(key)
            for i in range(total):
                self.redis.spop(key);

    def getUrls(self):
        self.cursor.execute("select id,url,district from urls")
        urls = self.cursor.fetchall()
        return urls

    def getSchools(self):
        self.cursor.execute("select sid,substring_index(substring(logo, 26), '.', 1) as uid from kjz_school")
        schools = self.cursor.fetchall()
        return schools

    def genSchoolRelationship(self):
        self.cursor.execute("truncate table kjz_school_area")
        schools = self.getSchools()
        for school in schools:
            self.cursor.execute("select url from urls where id=%s" % school[1])
            url=self.cursor.fetchone()

            self.cursor.execute("select district as code from urls where url='%s'" % url[0])
            codes=self.cursor.fetchall()

            for code in codes:
                try:
                    print "insert into kjz_school_area(sid,code) values(%s, %s)" % (school[0],code[0])
                    self.cursor.execute("insert into kjz_school_area(sid,code) values(%s, %s)" % (school[0],code[0]))
                except MySQLdb.Error, e:
                    print "Error %d: %s" % (e.args[0],e.args[1])

        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def zipcode(self):
        zipcodeStr = '[{"pr" : "香港","code" : "00852","city" : "香港"}, {"pr" : "澳门","code" : "00853","city" : "澳门"}, {"pr" : "北京","code" : "010","city" : "北京"}, {"pr" : "上海","code" : "021","city" : "上海"}, {"pr" : "天津","code" : "022","city" : "天津"}, {"pr" : "重庆","code" : "023","city" : "重庆"}, {"pr" : "安徽","code" : "0551","city" : "合肥"}, {"pr" : "安徽","code" : "0553","city" : "芜湖"}, {"pr" : "安徽","code" : "0556","city" : "安庆"}, {"pr" : "安徽","code" : "0552","city" : "蚌埠"}, {"pr" : "安徽","code" : "0558","city" : "亳州"}, {"pr" : "安徽","code" : "0565","city" : "巢湖"}, {"pr" : "安徽","code" : "0566","city" : "池州"}, {"pr" : "安徽","code" : "0550","city" : "滁州"}, {"pr" : "安徽","code" : "1558","city" : "阜阳"}, {"pr" : "安徽","code" : "0559","city" : "黄山"}, {"pr" : "安徽","code" : "0561","city" : "淮北"}, {"pr" : "安徽","code" : "0554","city" : "淮南"}, {"pr" : "安徽","code" : "0564","city" : "六安"}, {"pr" : "安徽","code" : "0555","city" : "马鞍山"}, {"pr" : "安徽","code" : "0557","city" : "宿州"}, {"pr" : "安徽","code" : "0562","city" : "铜陵"}, {"pr" : "安徽","code" : "0563","city" : "宣城"}, {"pr" : "福建","code" : "0591","city" : "福州"}, {"pr" : "福建","code" : "0592","city" : "厦门"}, {"pr" : "福建","code" : "0595","city" : "泉州"}, {"pr" : "福建","code" : "0597","city" : "龙岩"}, {"pr" : "福建","code" : "0593","city" : "宁德"}, {"pr" : "福建","code" : "0599","city" : "南平"}, {"pr" : "福建","code" : "0594","city" : "莆田"}, {"pr" : "福建","code" : "0598","city" : "三明"}, {"pr" : "福建","code" : "0596","city" : "漳州"}, {"pr" : "甘肃","code" : "0931","city" : "兰州"}, {"pr" : "甘肃","code" : "0943","city" : "白银"}, {"pr" : "甘肃","code" : "0932","city" : "定西"}, {"pr" : "甘肃","code" : "0935","city" : "金昌"}, {"pr" : "甘肃","code" : "0937","city" : "酒泉"}, {"pr" : "甘肃","code" : "0933","city" : "平凉"}, {"pr" : "甘肃","code" : "0934","city" : "庆阳"}, {"pr" : "甘肃","code" : "1935","city" : "武威"}, {"pr" : "甘肃","code" : "0938","city" : "天水"}, {"pr" : "甘肃","code" : "0936","city" : "张掖"}, {"pr" : "甘肃","code" : "0941","city" : "甘南"}, {"pr" : "甘肃","code" : "1937","city" : "嘉峪关"}, {"pr" : "甘肃","code" : "0930","city" : "临夏"}, {"pr" : "甘肃","code" : "2935","city" : "陇南"}, {"pr" : "广东","code" : "020","city" : "广州"}, {"pr" : "广东","code" : "0755","city" : "深圳"}, {"pr" : "广东","code" : "0756","city" : "珠海"}, {"pr" : "广东","code" : "0769","city" : "东莞"}, {"pr" : "广东","code" : "0757","city" : "佛山"}, {"pr" : "广东","code" : "0752","city" : "惠州"}, {"pr" : "广东","code" : "0750","city" : "江门"}, {"pr" : "广东","code" : "0760","city" : "中山"}, {"pr" : "广东","code" : "0754","city" : "汕头"}, {"pr" : "广东","code" : "0759","city" : "湛江"}, {"pr" : "广东","code" : "0768","city" : "潮州"}, {"pr" : "广东","code" : "0762","city" : "河源"}, {"pr" : "广东","code" : "0663","city" : "揭阳"}, {"pr" : "广东","code" : "0668","city" : "茂名"}, {"pr" : "广东","code" : "0753","city" : "梅州"}, {"pr" : "广东","code" : "0763","city" : "清远"}, {"pr" : "广东","code" : "0751","city" : "韶关"}, {"pr" : "广东","code" : "0660","city" : "汕尾"}, {"pr" : "广东","code" : "0662","city" : "阳江"}, {"pr" : "广东","code" : "0766","city" : "云浮"}, {"pr" : "广东","code" : "0758","city" : "肇庆"}, {"pr" : "广西","code" : "0771","city" : "南宁"}, {"pr" : "广西","code" : "0779","city" : "北海"}, {"pr" : "广西","code" : "0770","city" : "防城港"}, {"pr" : "广西","code" : "0773","city" : "桂林"}, {"pr" : "广西","code" : "0772","city" : "柳州"}, {"pr" : "广西","code" : "1771","city" : "崇左"}, {"pr" : "广西","code" : "1772","city" : "来宾"}, {"pr" : "广西","code" : "0774","city" : "梧州"}, {"pr" : "广西","code" : "0778","city" : "河池"}, {"pr" : "广西","code" : "0775","city" : "玉林"}, {"pr" : "广西","code" : "1755","city" : "贵港"}, {"pr" : "广西","code" : "1774","city" : "贺州"}, {"pr" : "广西","code" : "0777","city" : "钦州"}, {"pr" : "广西","code" : "0776","city" : "百色"}, {"pr" : "贵州","code" : "0851","city" : "贵阳"}, {"pr" : "贵州","code" : "0853","city" : "安顺"}, {"pr" : "贵州","code" : "0852","city" : "遵义"}, {"pr" : "贵州","code" : "0858","city" : "六盘水"}, {"pr" : "贵州","code" : "0857","city" : "毕节"}, {"pr" : "贵州","code" : "0855","city" : "黔东南"}, {"pr" : "贵州","code" : "0859","city" : "黔西南"}, {"pr" : "贵州","code" : "0854","city" : "黔南"}, {"pr" : "贵州","code" : "0856","city" : "铜仁"}, {"pr" : "海南","code" : "0898","city" : "海口"}, {"pr" : "海南","code" : "0899","city" : "三亚"}, {"pr" : "海南","code" : "0802","city" : "白沙县"}, {"pr" : "海南","code" : "0801","city" : "保亭县"}, {"pr" : "海南","code" : "0803","city" : "昌江县"}, {"pr" : "海南","code" : "0804","city" : "澄迈县"}, {"pr" : "海南","code" : "0806","city" : "定安县"}, {"pr" : "海南","code" : "0807","city" : "东方"}, {"pr" : "海南","code" : "2802","city" : "乐东县"}, {"pr" : "海南","code" : "1896","city" : "临高县"}, {"pr" : "海南","code" : "0809","city" : "陵水县"}, {"pr" : "海南","code" : "1894","city" : "琼海"}, {"pr" : "海南","code" : "1899","city" : "琼中县"}, {"pr" : "海南","code" : "1892","city" : "屯昌县"}, {"pr" : "海南","code" : "1898","city" : "万宁"}, {"pr" : "海南","code" : "1893","city" : "文昌"}, {"pr" : "海南","code" : "1897","city" : "五指山"}, {"pr" : "海南","code" : "0805","city" : "儋州"}, {"pr" : "河北","code" : "0311","city" : "石家庄"}, {"pr" : "河北","code" : "0312","city" : "保定"}, {"pr" : "河北","code" : "0314","city" : "承德"}, {"pr" : "河北","code" : "0310","city" : "邯郸"}, {"pr" : "河北","code" : "0315","city" : "唐山"}, {"pr" : "河北","code" : "0335","city" : "秦皇岛"}, {"pr" : "河北","code" : "0317","city" : "沧州"}, {"pr" : "河北","code" : "0318","city" : "衡水"}, {"pr" : "河北","code" : "0316","city" : "廊坊"}, {"pr" : "河北","code" : "0319","city" : "邢台"}, {"pr" : "河北","code" : "0313","city" : "张家口"}, {"pr" : "河南","code" : "0371","city" : "郑州"}, {"pr" : "河南","code" : "0379","city" : "洛阳"}, {"pr" : "河南","code" : "0378","city" : "开封"}, {"pr" : "河南","code" : "0374","city" : "许昌"}, {"pr" : "河南","code" : "0372","city" : "安阳"}, {"pr" : "河南","code" : "0375","city" : "平顶山"}, {"pr" : "河南","code" : "0392","city" : "鹤壁"}, {"pr" : "河南","code" : "0391","city" : "焦作"}, {"pr" : "河南","code" : "1391","city" : "济源"}, {"pr" : "河南","code" : "0395","city" : "漯河"}, {"pr" : "河南","code" : "0377","city" : "南阳"}, {"pr" : "河南","code" : "0393","city" : "濮阳"}, {"pr" : "河南","code" : "0398","city" : "三门峡"}, {"pr" : "河南","code" : "0370","city" : "商丘"}, {"pr" : "河南","code" : "0373","city" : "新乡"}, {"pr" : "河南","code" : "0376","city" : "信阳"}, {"pr" : "河南","code" : "0396","city" : "驻马店"}, {"pr" : "河南","code" : "0394","city" : "周口"}, {"pr" : "黑龙江","code" : "0451","city" : "哈尔滨"}, {"pr" : "黑龙江","code" : "0459","city" : "大庆"}, {"pr" : "黑龙江","code" : "0452","city" : "齐齐哈尔"}, {"pr" : "黑龙江","code" : "0454","city" : "佳木斯"}, {"pr" : "黑龙江","code" : "0457","city" : "大兴安岭"}, {"pr" : "黑龙江","code" : "0456","city" : "黑河"}, {"pr" : "黑龙江","code" : "0468","city" : "鹤岗"}, {"pr" : "黑龙江","code" : "0467","city" : "鸡西"}, {"pr" : "黑龙江","code" : "0453","city" : "牡丹江"}, {"pr" : "黑龙江","code" : "0464","city" : "七台河"}, {"pr" : "黑龙江","code" : "0455","city" : "绥化"}, {"pr" : "黑龙江","code" : "0469","city" : "双鸭山"}, {"pr" : "黑龙江","code" : "0458","city" : "伊春"}, {"pr" : "湖北","code" : "027","city" : "武汉"}, {"pr" : "湖北","code" : "0710","city" : "襄阳"}, {"pr" : "湖北","code" : "0719","city" : "十堰"}, {"pr" : "湖北","code" : "0714","city" : "黄石"}, {"pr" : "湖北","code" : "0711","city" : "鄂州"}, {"pr" : "湖北","code" : "0718","city" : "恩施"}, {"pr" : "湖北","code" : "0713","city" : "黄冈"}, {"pr" : "湖北","code" : "0716","city" : "荆州"}, {"pr" : "湖北","code" : "0724","city" : "荆门"}, {"pr" : "湖北","code" : "0722","city" : "随州"}, {"pr" : "湖北","code" : "0717","city" : "宜昌"}, {"pr" : "湖北","code" : "1728","city" : "天门"}, {"pr" : "湖北","code" : "2728","city" : "潜江"}, {"pr" : "湖北","code" : "0728","city" : "仙桃"}, {"pr" : "湖北","code" : "0712","city" : "孝感"}, {"pr" : "湖北","code" : "0715","city" : "咸宁"}, {"pr" : "湖北","code" : "1719","city" : "神农架"}, {"pr" : "湖南","code" : "0731","city" : "长沙"}, {"pr" : "湖南","code" : "0730","city" : "岳阳"}, {"pr" : "湖南","code" : "0732","city" : "湘潭"}, {"pr" : "湖南","code" : "0736","city" : "常德"}, {"pr" : "湖南","code" : "0735","city" : "郴州"}, {"pr" : "湖南","code" : "0734","city" : "衡阳"}, {"pr" : "湖南","code" : "0745","city" : "怀化"}, {"pr" : "湖南","code" : "0738","city" : "娄底"}, {"pr" : "湖南","code" : "0739","city" : "邵阳"}, {"pr" : "湖南","code" : "0737","city" : "益阳"}, {"pr" : "湖南","code" : "0746","city" : "永州"}, {"pr" : "湖南","code" : "0733","city" : "株洲"}, {"pr" : "湖南","code" : "0744","city" : "张家界"}, {"pr" : "湖南","code" : "0743","city" : "湘西"}, {"pr" : "吉林","code" : "0431","city" : "长春"}, {"pr" : "吉林","code" : "0432","city" : "吉林"}, {"pr" : "吉林","code" : "1433","city" : "延边"}, {"pr" : "吉林","code" : "0436","city" : "白城"}, {"pr" : "吉林","code" : "0439","city" : "白山"}, {"pr" : "吉林","code" : "0437","city" : "辽源"}, {"pr" : "吉林","code" : "0434","city" : "四平"}, {"pr" : "吉林","code" : "0438","city" : "松原"}, {"pr" : "吉林","code" : "0435","city" : "通化"}, {"pr" : "江苏","code" : "025","city" : "南京"}, {"pr" : "江苏","code" : "0512","city" : "苏州"}, {"pr" : "江苏","code" : "0519","city" : "常州"}, {"pr" : "江苏","code" : "0518","city" : "连云港"}, {"pr" : "江苏","code" : "0523","city" : "泰州"}, {"pr" : "江苏","code" : "0510","city" : "无锡"}, {"pr" : "江苏","code" : "0516","city" : "徐州"}, {"pr" : "江苏","code" : "0514","city" : "扬州"}, {"pr" : "江苏","code" : "0511","city" : "镇江"}, {"pr" : "江苏","code" : "0517","city" : "淮安"}, {"pr" : "江苏","code" : "0513","city" : "南通"}, {"pr" : "江苏","code" : "0527","city" : "宿迁"}, {"pr" : "江苏","code" : "0515","city" : "盐城"}, {"pr" : "江西","code" : "0791","city" : "南昌"}, {"pr" : "江西","code" : "0797","city" : "赣州"}, {"pr" : "江西","code" : "0792","city" : "九江"}, {"pr" : "江西","code" : "0798","city" : "景德镇"}, {"pr" : "江西","code" : "0796","city" : "吉安"}, {"pr" : "江西","code" : "0799","city" : "萍乡"}, {"pr" : "江西","code" : "0793","city" : "上饶"}, {"pr" : "江西","code" : "0790","city" : "新余"}, {"pr" : "江西","code" : "0795","city" : "宜春"}, {"pr" : "江西","code" : "0701","city" : "鹰潭"}, {"pr" : "江西","code" : "0794","city" : "抚州"}, {"pr" : "辽宁","code" : "024","city" : "沈阳"}, {"pr" : "辽宁","code" : "0411","city" : "大连"}, {"pr" : "辽宁","code" : "0412","city" : "鞍山"}, {"pr" : "辽宁","code" : "0415","city" : "丹东"}, {"pr" : "辽宁","code" : "0413","city" : "抚顺"}, {"pr" : "辽宁","code" : "0416","city" : "锦州"}, {"pr" : "辽宁","code" : "0417","city" : "营口"}, {"pr" : "辽宁","code" : "0414","city" : "本溪"}, {"pr" : "辽宁","code" : "0421","city" : "朝阳"}, {"pr" : "辽宁","code" : "0418","city" : "阜新"}, {"pr" : "辽宁","code" : "0429","city" : "葫芦岛"}, {"pr" : "辽宁","code" : "0419","city" : "辽阳"}, {"pr" : "辽宁","code" : "0427","city" : "盘锦"}, {"pr" : "辽宁","code" : "0410","city" : "铁岭"}, {"pr" : "内蒙古","code" : "0471","city" : "呼和浩特"}, {"pr" : "内蒙古","code" : "0472","city" : "包头"}, {"pr" : "内蒙古","code" : "0476","city" : "赤峰"}, {"pr" : "内蒙古","code" : "0477","city" : "鄂尔多斯"}, {"pr" : "内蒙古","code" : "0474","city" : "乌兰察布"}, {"pr" : "内蒙古","code" : "0473","city" : "乌海"}, {"pr" : "内蒙古","code" : "0482","city" : "兴安盟"}, {"pr" : "内蒙古","code" : "0470","city" : "呼伦贝尔"}, {"pr" : "内蒙古","code" : "0475","city" : "通辽"}, {"pr" : "内蒙古","code" : "0483","city" : "阿拉善盟"}, {"pr" : "内蒙古","code" : "0478","city" : "巴彦淖尔"}, {"pr" : "内蒙古","code" : "0479","city" : "锡林郭勒"}, {"pr" : "宁夏","code" : "0951","city" : "银川"}, {"pr" : "宁夏","code" : "0952","city" : "石嘴山"}, {"pr" : "宁夏","code" : "0954","city" : "固原"}, {"pr" : "宁夏","code" : "0953","city" : "吴忠"}, {"pr" : "宁夏","code" : "1953","city" : "中卫"}, {"pr" : "青海","code" : "0971","city" : "西宁"}, {"pr" : "青海","code" : "0973","city" : "黄南"}, {"pr" : "青海","code" : "0976","city" : "玉树"}, {"pr" : "青海","code" : "0975","city" : "果洛"}, {"pr" : "青海","code" : "0972","city" : "海东"}, {"pr" : "青海","code" : "0977","city" : "海西"}, {"pr" : "青海","code" : "0974","city" : "海南"}, {"pr" : "青海","code" : "0970","city" : "海北"}, {"pr" : "山东","code" : "0531","city" : "济南"}, {"pr" : "山东","code" : "0532","city" : "青岛"}, {"pr" : "山东","code" : "0631","city" : "威海"}, {"pr" : "山东","code" : "0535","city" : "烟台"}, {"pr" : "山东","code" : "0536","city" : "潍坊"}, {"pr" : "山东","code" : "0538","city" : "泰安"}, {"pr" : "山东","code" : "0543","city" : "滨州"}, {"pr" : "山东","code" : "0534","city" : "德州"}, {"pr" : "山东","code" : "0546","city" : "东营"}, {"pr" : "山东","code" : "0530","city" : "菏泽"}, {"pr" : "山东","code" : "0537","city" : "济宁"}, {"pr" : "山东","code" : "0635","city" : "聊城"}, {"pr" : "山东","code" : "0539","city" : "临沂"}, {"pr" : "山东","code" : "0634","city" : "莱芜"}, {"pr" : "山东","code" : "0633","city" : "日照"}, {"pr" : "山东","code" : "0533","city" : "淄博"}, {"pr" : "山东","code" : "0632","city" : "枣庄"}, {"pr" : "山西","code" : "0351","city" : "太原"}, {"pr" : "山西","code" : "0355","city" : "长治"}, {"pr" : "山西","code" : "0352","city" : "大同"}, {"pr" : "山西","code" : "0356","city" : "晋城"}, {"pr" : "山西","code" : "0354","city" : "晋中"}, {"pr" : "山西","code" : "0357","city" : "临汾"}, {"pr" : "山西","code" : "0358","city" : "吕梁"}, {"pr" : "山西","code" : "0349","city" : "朔州"}, {"pr" : "山西","code" : "0350","city" : "忻州"}, {"pr" : "山西","code" : "0359","city" : "运城"}, {"pr" : "山西","code" : "0353","city" : "阳泉"}, {"pr" : "陕西","code" : "029","city" : "西安"}, {"pr" : "陕西","code" : "0915","city" : "安康"}, {"pr" : "陕西","code" : "0917","city" : "宝鸡"}, {"pr" : "陕西","code" : "0916","city" : "汉中"}, {"pr" : "陕西","code" : "0914","city" : "商洛"}, {"pr" : "陕西","code" : "0919","city" : "铜川"}, {"pr" : "陕西","code" : "0913","city" : "渭南"}, {"pr" : "陕西","code" : "0910","city" : "咸阳"}, {"pr" : "陕西","code" : "0911","city" : "延安"}, {"pr" : "陕西","code" : "0912","city" : "榆林"}, {"pr" : "四川","code" : "028","city" : "成都"}, {"pr" : "四川","code" : "0816","city" : "绵阳"}, {"pr" : "四川","code" : "0832","city" : "资阳"}, {"pr" : "四川","code" : "0827","city" : "巴中"}, {"pr" : "四川","code" : "0838","city" : "德阳"}, {"pr" : "四川","code" : "0818","city" : "达州"}, {"pr" : "四川","code" : "0826","city" : "广安"}, {"pr" : "四川","code" : "0839","city" : "广元"}, {"pr" : "四川","code" : "0833","city" : "乐山"}, {"pr" : "四川","code" : "0830","city" : "泸州"}, {"pr" : "四川","code" : "1833","city" : "眉山"}, {"pr" : "四川","code" : "1832","city" : "内江"}, {"pr" : "四川","code" : "0817","city" : "南充"}, {"pr" : "四川","code" : "0812","city" : "攀枝花"}, {"pr" : "四川","code" : "0825","city" : "遂宁"}, {"pr" : "四川","code" : "0831","city" : "宜宾"}, {"pr" : "四川","code" : "0835","city" : "雅安"}, {"pr" : "四川","code" : "0813","city" : "自贡"}, {"pr" : "四川","code" : "0837","city" : "阿坝"}, {"pr" : "四川","code" : "0836","city" : "甘孜"}, {"pr" : "四川","code" : "0834","city" : "凉山"}, {"pr" : "西藏","code" : "0891","city" : "拉萨"}, {"pr" : "西藏","code" : "0892","city" : "日喀则"}, {"pr" : "西藏","code" : "0897","city" : "阿里"}, {"pr" : "西藏","code" : "0895","city" : "昌都"}, {"pr" : "西藏","code" : "0894","city" : "林芝"}, {"pr" : "西藏","code" : "0896","city" : "那曲"}, {"pr" : "西藏","code" : "0893","city" : "山南"}, {"pr" : "新疆","code" : "0991","city" : "乌鲁木齐"}, {"pr" : "新疆","code" : "0993","city" : "石河子"}, {"pr" : "新疆","code" : "0995","city" : "吐鲁番"}, {"pr" : "新疆","code" : "0999","city" : "伊犁"}, {"pr" : "新疆","code" : "0997","city" : "阿克苏"}, {"pr" : "新疆","code" : "0906","city" : "阿勒泰"}, {"pr" : "新疆","code" : "0996","city" : "巴音"}, {"pr" : "新疆","code" : "0909","city" : "博尔塔拉"}, {"pr" : "新疆","code" : "0994","city" : "昌吉"}, {"pr" : "新疆","code" : "0902","city" : "哈密"}, {"pr" : "新疆","code" : "0903","city" : "和田"}, {"pr" : "新疆","code" : "0998","city" : "喀什"}, {"pr" : "新疆","code" : "0990","city" : "克拉玛依"}, {"pr" : "新疆","code" : "0908","city" : "克孜勒"}, {"pr" : "新疆","code" : "0901","city" : "塔城"}, {"pr" : "云南","code" : "0871","city" : "昆明"}, {"pr" : "云南","code" : "0877","city" : "玉溪"}, {"pr" : "云南","code" : "0878","city" : "楚雄"}, {"pr" : "云南","code" : "0872","city" : "大理"}, {"pr" : "云南","code" : "0873","city" : "红河"}, {"pr" : "云南","code" : "0874","city" : "曲靖"}, {"pr" : "云南","code" : "0691","city" : "西双版纳"}, {"pr" : "云南","code" : "0870","city" : "昭通"}, {"pr" : "云南","code" : "0875","city" : "保山"}, {"pr" : "云南","code" : "0692","city" : "德宏"}, {"pr" : "云南","code" : "0887","city" : "迪庆"}, {"pr" : "云南","code" : "0888","city" : "丽江"}, {"pr" : "云南","code" : "0883","city" : "临沧"}, {"pr" : "云南","code" : "0886","city" : "怒江"}, {"pr" : "云南","code" : "0879","city" : "普洱"}, {"pr" : "云南","code" : "0876","city" : "文山"}, {"pr" : "浙江","code" : "0571","city" : "杭州"}, {"pr" : "浙江","code" : "0574","city" : "宁波"}, {"pr" : "浙江","code" : "0573","city" : "嘉兴"}, {"pr" : "浙江","code" : "0575","city" : "绍兴"}, {"pr" : "浙江","code" : "0577","city" : "温州"}, {"pr" : "浙江","code" : "0580","city" : "舟山"}, {"pr" : "浙江","code" : "0572","city" : "湖州"}, {"pr" : "浙江","code" : "0579","city" : "金华"}, {"pr" : "浙江","code" : "0578","city" : "丽水"}, {"pr" : "浙江","code" : "0576","city" : "台州"}, {"pr" : "浙江","code" : "0570","city" : "衢州"}]'
        zipcodeJson = json.loads(zipcodeStr)
        for zipcode in zipcodeJson:
            try:
                sql = "insert into qcp_city_zipcode(name,province,city_code) values('%s', '%s', '%s')" % (zipcode['city'],zipcode['pr'],zipcode['code'])
                print sql
                self.cursor.execute(sql)
            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0],e.args[1])

        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def updateAddress(self):
        key = 'SCHOOL:ADDR:SET'
        specialCities = []#self.redis.smembers(key)
        if len(specialCities)>0:
            self.cursor.execute("select sid, s.name as school, concat(c.name,'市') as city \
                from kjz_school s \
                left join kjz_cities c on c.code=s.province \
                where location='' and sid in (%s) \
                " % ','.join(specialCities))
        else:
            self.cursor.execute("select sid, s.name as school, concat(c.name,'市') as city \
                from kjz_school s \
                left join kjz_cities c on c.code=s.city \
                where location='' \
                ")
        cities=self.cursor.fetchall()

        #init request
        #cookie = cookielib.CookieJar()
        #cookieStr = urllib2.HTTPCookieProcessor(cookie)
        #opener = urllib2.build_opener(cookieStr)
        #headers = {
        #    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'
        #}
        #urllib2.install_opener(opener)
        #request = urllib2.Request(url,urllib.urlencode(postdata),headers = headers)
        #urllib2.urlopen(request)
        
        for city in cities:
            if city[2] is None:
                key = 'SCHOOL:ADDR:SET'
                self.redis.sadd(key, city[0]);
                continue

            paramKeyword = urllib.quote_plus(city[1].encode('utf8'))
            paramRegion = urllib.quote_plus(city[2].encode('utf8'))
            url = 'http://api.map.baidu.com/place/v2/search?callback=cl&q=%s&region=%s&output=json&ak=5DwHqwIO0jScfsocR9PEAULz' % (paramKeyword, paramRegion)
            
            response = urllib2.urlopen(url)
            responseText = response.read()
            #print city[1], city[2], responseText[7:-1]

            #parse response
            if len(responseText and 'cl&&cl('):
                jsonStr = responseText[7:-1] #callback like:cl&&cl({...})
                jsonStr = "".join(jsonStr.split());
                baiduJson = json.loads(jsonStr)
                data = {}

                if len(baiduJson['results'])>0 and  baiduJson['results'][0].has_key('location'):
                    lat = baiduJson['results'][0]['location']['lat']
                    lng = baiduJson['results'][0]['location']['lng']
                    data['location'] = ','.join([str(lat), str(lng)])
                    data['address'] = baiduJson['results'][0]['address']

                    #do update
                    updateSql = "update kjz_school set location='%s', address='%s' where sid=%s\
                        " % (data['location'],data['address'],city[0])
                    print updateSql
                    self.cursor.execute(updateSql)

        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def renameFiles(self, imgPath, newPath):
        if os.path.exists(newPath):
            os.remove(imgPath)
            os.rename(newPath, imgPath)

            print 'rename:', newPath, imgPath

    def cmpFiles(self, imgPath):
        key = 'SCHOOL:WATER:SET'
        found = filecmp.cmp(imgPath, '/data/www/driving/demo.png')
        if found:
            print fileinfo[0], imgPath
            shutil.copy('/data/www/driving/nopic.png', imgPath)
            self.redis.sadd(key, fileinfo[0]);
            dstPath = '/data/www/driving/todos/'
            if not os.path.exists(''.join([dstPath, obj])):
                shutil.copy(imgPath, dstPath)

    def removeDir(self, filename):
        detailPath = ''.join([os.getcwd(), os.sep, filename])
        if os.path.exists(detailPath) and os.path.isdir(detailPath):
            print 'remove:', detailPath
            shutil.rmtree(detailPath,True) 

    def photoResize(self, startdir):
        os.chdir(startdir)
        for obj in os.listdir(os.curdir) :
            if os.path.isdir(obj) :
                self.photoResize(obj)
                os.chdir(os.pardir)
            else:
                imgPath = os.getcwd() + os.sep + obj
                fileinfo = os.path.splitext(obj)
                newPath = os.getcwd() + os.sep + ''.join([fileinfo[0], '_200', fileinfo[1]])
                key = 'SCHOOL:WATER:SET'
                #print imgPath
                try:
                    if len(fileinfo[0])<6:
                        img = Image.open(imgPath)
                        (x, y) = img.size
                        if(y>200):
                            box=(0,0,x,200)
                            newImg = img.crop(box)
                            newImg.save(imgPath)
                    '''    
                    if self.redis.sismember(key, fileinfo[0]):
                        os.remove(imgPath);
                        if os.path.exists(newPath):
                            os.remove(newPath);
                        orgPath = '/data/www/driving/todos/'
                        orgFile = ''.join([orgPath, obj])
                        shutil.copy(orgFile, os.getcwd())
                    
                    if os.path.exists(newPath):
                        pass
                    elif fileinfo[0].endswith('_200'):
                        pass
                        #os.remove(imgPath);
                        #print 'remove:', imgPath
                    else:
                        img = Image.open(imgPath)
                        (x, y) = img.size
                        x_s = 200
                        y_s = y * x_s / x
                        out = img.resize((x_s, y_s), Image.ANTIALIAS)
                        out.save(newPath)
                        print 'gen:',newPath
                    '''
                except IOError:
                    print("cannot resize file:", imgPath)

    def schoolNames(self):
        self.cacheTodos();
        sys.exit()
        os.chdir('/data/www/driving/todos')
        for obj in os.listdir(os.curdir) :
            fileinfo = os.path.splitext(obj)
            self.cursor.execute("select url from urls where id='%s'" % fileinfo[0])
            url=self.cursor.fetchone()

            print fileinfo[0], url[0]

    def cacheTodos(self):
        os.chdir('/data/www/driving/todos')
        for obj in os.listdir(os.curdir) :
            fileinfo = os.path.splitext(obj)
            key = 'SCHOOL:WATER:SET'
            self.redis.sadd(key, fileinfo[0]);

    def findWater(self, imgPath):
        img = Image.open(imgPath)
        pix = img.load()
        (w, d) = img.size
        for y in range(d):
            for x in range(w):
                if x > w/2 and x < w-10 and y > d/2 and y < d-10:
                    if pix[x, y] == pix[x+1, y] and pix[x, y] == pix[x, y-1] and pix[x, y] == pix[x+1, y-1] and pix[x, y] == (51, 152, 204):
                        #print "found water!", imgPath
                        return True

        return False

    def groupBySize(self):
        os.chdir('/data/www/driving/big')
        for obj in os.listdir(os.curdir) :
            imgPath = os.getcwd() + os.sep + obj
            img = Image.open(imgPath)
            (x, y) = img.size

            newPath = ''.join([os.getcwd(), os.sep, str(x), '_', str(y)])
            inpaitDir = ''.join([newPath, os.sep, 'inpaint'])
            if not os.path.exists(newPath):
                os.mkdir(newPath)
            elif not os.path.isdir(newPath):
                os.mkdir(newPath)

            if not os.path.exists(inpaitDir):
                os.mkdir(inpaitDir)

            shutil.move(imgPath, newPath)

        return True

    def batchInsert(self):
        for i in range(2000000):
            try:
                sql = "insert into kjz_score_all(uid,score,cityid,cert_type,course) values('%s', '%s',0,1,1)" % (i+1,i)
                #print sql
                self.cursor.execute(sql)
            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0],e.args[1])

        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    ########class end############

def usage():  
    print("Usage:%s [-h|-i|-s|-a|-c|-r|-n|-g|-z]\
    [--help|--init|--gen_school|--gen_address|--clear|--resize|--names|--group|--zipcode] .." % sys.argv[0]); 

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "hiascrngz")
    #opts, args = getopt.getopt(sys.argv[1:], "hi:g:c:")
    
    store = UrlStore()
    for op, value in opts:
        if op in ("-i", "--init"):
            print 'initing...'
            store.initRedis()
            print 'inited!'
        elif op in ("-c", "--clear"):
            print 'clearing...'
            store.clearRedis()
            print 'cleared!'
        elif op in ("-s", "--gen_school"):
            print 'gen school relationship...'
            store.genSchoolRelationship()
            print 'relationship gened!'
        elif op in ("-a", "--gen_address"):
            print 'gen school address...'
            store.updateAddress()
            print 'address gened!'
        elif op in ("-r", "--resize"):
            print 'gen resize images...'
            store.photoResize('/data/www/driving/downloads')
            print 'images resized!'
        elif op in ("-n", "--names"):
            print 'get school names...'
            store.schoolNames()
            print 'done!'
        elif op in ("-g", "--group"):
            print 'begin group files...'
            store.groupBySize()
            print 'end group files!'
        elif op in ("-z", "--zipcode"):
            print 'init zipcode...'
            store.zipcode()
            print 'inited zipcode!'
        else:
            usage()
            sys.exit()