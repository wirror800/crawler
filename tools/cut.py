#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: WirrorYin
# @Date:   2015-05-29 07:56:52
# @Last Modified by:   WirrorYin
# @Last Modified time: 2015-06-11 21:03:54
from PIL import Image, ImageFile
import redis
import sys, getopt
import os
import shutil
import filecmp

ImageFile.LOAD_TRUNCATED_IMAGES = True
class ImageUtil(object):
    def __init__(self):
        self.redispool = redis.ConnectionPool(
            host='localhost', 
            port=6379, 
            db=0
        )

        self.redis = redis.Redis(connection_pool=self.redispool)

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

    def split(self, dir):
        os.chdir(dir)
        for obj in os.listdir(os.curdir) :
            if os.path.isdir(obj) :
                continue

            imgPath = os.getcwd() + os.sep + obj
            fileinfo = os.path.splitext(obj)
            img = Image.open(imgPath)
            (x, y) = img.size
            filename = fileinfo[0]
            extension = fileinfo[1]

            newfiles = filename.split('-')
            for idx,f in enumerate(newfiles):
                if len(f)>0:
                    box=(idx*x/2,0,(idx+1)*x/2,y)
                    newImgPath = ''.join([dir,os.sep,'dst',os.sep,f,extension])
                    newImg = img.crop(box)
                    newImg.save(newImgPath)
                    print 'gen file:', newImgPath

    def resize(self, dir):
        os.chdir(dir)
        for obj in os.listdir(os.curdir) :
            if os.path.isdir(obj) :
                continue
            imgPath = os.getcwd() + os.sep + obj
            newPath = ''.join([dir,os.sep,'dst',os.sep,obj])
            img = Image.open(imgPath)
            (x, y) = img.size
            x_s = 700
            y_s = y * x_s / x
            out = img.resize((x_s, y_s), Image.ANTIALIAS)
            out.save(newPath)
            print 'new file:', newPath

    ########class end############

def usage():  
    print("Usage:%s [-h|-s|-r]\
    [--help|--split|--resize] .." % sys.argv[0]); 

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "hsr")
    #opts, args = getopt.getopt(sys.argv[1:], "hi:g:c:")
    
    util = ImageUtil()
    for op, value in opts:
        if op in ("-h", "--help"):
            usage()
        elif op in ("-s", "--split"):
            print 'spliting...'
            util.split('/data/www/driving/ph')
            print 'done!'
        elif op in ("-r", "--resize"):
            print 'resizing...'
            util.resize('/data/www/driving/resize')
            print 'done!'
        else:
            usage()
            sys.exit()