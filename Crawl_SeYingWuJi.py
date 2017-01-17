#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-11 07:18:23
# Project: SeYingWuJi

#coding: utf-8
from pyspider.libs.base_handler import *
import os
import sys
from datetime import datetime
import re
reload(sys)
sys.setdefaultencoding('utf-8')


fmt_jpg = re.compile("http://.*.xitek.com/.*.jpg$")
fmt_url = re.compile("http://.*xitek.com/.*$")
    
IMAGE_DIR_PATH='D:\\lhq\\openimages\\image_network\\images\\'#定义保存图片位置
BRIEF_DIR_PATH='D:\\lhq\\openimages\\image_network\\images_brief\\'#定义保存信息位置
PROGRAME_NAME='seyingwuji5'
#import redis

class Handler(BaseHandler):
    crawl_config = {
        
    }
    def __init__(self):
        self.base_url='http://ww.xitek.com/'
        self.deal=Deal()
        self.time=CrawTime()
        #self.pool = redis.ConnectionPool(host = 'localhost', port = 6379, db=0)
        

        
    def on_start(self):
        self.crawl(self.base_url, callback=self.index_page)
        self.brief = Brief()
        self.deal.save_brief(self.brief)

    @config(priority=1)
    def index_page(self, response):
        
        #self.r = redis.Redis(connection_pool=self.pool)
        #self.r.sadd('urls', response.url)
        
        for each in response.doc('img').items():
            if fmt_jpg.match(each.attr.src):
                self.detail_page(each.attr.src)
        
        #urls_set = self.r.smembers('urls')
        #print urls_set
        for each in response.doc('a[href^="http"]').items():
            if fmt_url.match(each.attr.href):
            #if each.attr.href not in urls_set and fmt_url.match(each.attr.href):
                self.crawl(each.attr.href, callback=self.index_page)
    
    @config(priority=2)
    def detail_page(self, url):
        
        brief = Brief()
        brief.OriginalURL = url
        brief.CrawlTime = self.time.getTimeStr(datetime.now())
        brief.MD5 = md5(brief.OriginalURL + brief.CrawlTime)
        
        if self.deal.dir_path:

            extension=self.deal.getextension(brief.OriginalURL)
            file_name=brief.MD5+'.'+extension
            save_path = self.deal.dir_path + file_name
            
            
            #images_set = self.r.smembers('images')
            #print images_set
            
            if brief.OriginalURL and not os.path.exists(save_path):
            #if brief.OriginalURL and save_path not in images_set and not os.path.exists(save_path):
                #self.r.sadd('images', save_path)
                self.deal.save_brief(brief)
                self.crawl(brief.OriginalURL, callback=self.save_img, save={'save_path': save_path})
                
    @config(priority=3)   
    def save_img(self,response):
        content=response.content
        file_path=response.save['save_path']
        self.deal.save_Img(content,file_path)

class Deal:
    def __init__(self):
        self.dir_path=IMAGE_DIR_PATH + PROGRAME_NAME
        if not self.dir_path.endswith('\\'):
            self.dir_path=self.dir_path+'\\'
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def mkDIR(self,name):
        name=name.strip()
        dir_name=self.dir_path+name
        exists=os.path.exists(dir_name)
        if not exists:
             os.makedirs(dir_name)
        return dir_name

    def save_Img(self,content,file_name):
        file=open(file_name,'wb')
        file.write(content)
        file.close()

    def save_brief(self,brief):
        file_name=brief.dir_path + PROGRAME_NAME+'.tsv'
        file=open(file_name, 'a')
        content = brief.OriginalURL + '\t' + brief.CrawlTime + '\t' + brief.MD5 + '\n'
        file.write(content.encode('utf-8'))
        file.close()

    def getextension(self,url):
        extension=url.split('.')[-1]
        return extension

class Brief:
    def __init__(self):     
            
        self.OriginalURL = 'OriginalURL'
        self.CrawlTime = 'CrawlTime'
        self.MD5 = 'MD5'
        
        self.dir_path=BRIEF_DIR_PATH
        if not self.dir_path.endswith('\\'):
            self.dir_path=self.dir_path+'\\'
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        
        
    def printout(self):
        print self.OriginalURL
        print self.CrawTime
        print self.MD5
        
class CrawTime:
    def __init__(self):
        self.fmt = '%Y-%m-%d %H:%M:%S'
        
    def getTimeStr(self, dt):
        return str(dt.strftime(self.fmt))
    
    def getDateTime(self, st):
        return datetime.strptime(st, self.fmt)

import hashlib
def md5(str):
    m = hashlib.md5()   
    m.update(str)
    return m.hexdigest()      
    
import re
def getFmtStr(temp):   
    str = temp.decode("utf8")
    return str

