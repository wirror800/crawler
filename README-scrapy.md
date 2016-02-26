# Scrapy安装

## 1、安装scrapy
### 下载安装
        #wget https://codeload.github.com/scrapy/scrapy/zip/0.24 -O scrapy.zip
        #unzip scrapy.zip

### pip安装
        #pip install Scrapy

### pipy国内镜像目前有：
        http://pypi.douban.com/  豆瓣
        http://pypi.hustunique.com/  华中理工大学
        http://pypi.sdutlinux.org/  山东理工大学
        http://pypi.mirrors.ustc.edu.cn/  中国科学技术大学
        对于pip这种在线安装的方式来说，很方便，但网络不稳定的话很要命。使用国内镜像相对好一些，

        如果想手动指定源，可以在pip后面跟-i 来指定源，比如用豆瓣的源来安装web.py框架：
        #pip install web.py -i http://pypi.douban.com/simple

## 2、安装依赖
### (1)python 2.7
        #yum groupinstall "Development tools"
        #yum -y install zlib-devel
        #yum -y install bzip2-devel
        #yum -y install openssl-devel
        #yum -y install ncurses-devel
        #yum -y install sqlite-devel
        #yum -y install libxslt-devel
        #yum -y install libffi-devel 

        #wget --no-check-certificate https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tar.xz
        #tar xf Python-2.7.10.tar.xz
        #cd Python-2.7.10
        #./configure --prefix=/usr/local
        #make && make install
        #ln -s /usr/local/bin/python2.7 /usr/local/bin/python

        修改yum依赖的python路径
        #vi /usr/bin/yum 


### (2)pip和setuptools
        #wget --no-check-certificate https://raw.github.com/pypa/pip/master/contrib/get-pip.py
        #python get-pip.py

        `PS：默认安装的pyOpenSSL的版本较高，会与openssl版本不兼容，可以指定安装低版本的`
        #pip install pyOpenSSL==0.12

### (3)lxml
        #pip install lxml

### (4)OpenSSL
        #wget ftp://ftp.openssl.org/source/openssl-1.0.2a.tar.gz  
        #tar zxvf openssl-1.0.2a.tar.gz  
        #cd openssl-1.0.2a  
        #./config --prefix=/usr/local/openssl  
        #make && make install  
        #mv /usr/bin/openssl /usr/bin/openssl.OFF  
        #mv /usr/include/openssl /usr/include/openssl.OFF  
        #ln -s /usr/local/openssl/bin/openssl /usr/bin/openssl  
        #ln -s /usr/local/openssl/include/openssl /usr/include/openssl  
        #echo "/usr/local/openssl/lib">>/etc/ld.so.conf  
        #ldconfig -v  
        #openssl version -a  

        #wget ftp://mirror.switch.ch/pool/4/mirror/fedora/linux/development/rawhide/x86_64/os/Packages/o/openssl-libs-1.0.2a-4.fc23.x86_64.rpm
        #wget ftp://mirror.switch.ch/pool/4/mirror/fedora/linux/development/rawhide/x86_64/os/Packages/o/openssl-devel-1.0.2a-4.fc23.x86_64.rpm
        #rpm -ivh openssl-devel-1.0.2a-4.fc23.x86_64.rpm

### (5)PIL/ImageMagick/Opencv
        # wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
        # tar zxvf Imaging-1.1.7.tar.gz
        # cd Imaging-1.1.7
        # vi setup.py
        JPEG_ROOT = "/usr/lib64"
        ZLIB_ROOT = "/usr/include"
        FREETYPE_ROOT = "/usr/include"
        # python setup.py install

        或者
        # pip install PIL --allow-external PIL --allow-unverified PIL
        
        或者
        # pip install Pillow

        # wget http://www.imagemagick.org/download/ImageMagick.tar.gz
        # tar zxvf ImageMagick.tar.gz
        # cd ImageMagick-6.9.1
        # ./configure
        # make
        # sudo make install
        # sudo ldconfig /usr/local/lib
        # /usr/local/bin/convert logo: logo.gif
        # make check

        # wget ftp://195.220.108.108/linux/Mandriva/official/2011/x86_64/media/main/updates/lib64python2.7-2.7.2-2.2-mdv2011.0.x86_64.rpm
        # rpm -ivh lib64python2.7-2.7.2-2.2-mdv2011.0.x86_64.rpm
        # wget ftp://195.220.108.108/linux/fedora/linux/development/rawhide/x86_64/os/Packages/p/python-devel-2.7.10-1.fc23.x86_64.rpm
        # rpm -ivh python-devel-2.7.10-1.fc23.x86_64.rpm
        # wget http://www.imagemagick.org/download/python/PythonMagick-0.9.11.tar.gz
        # tar zxvf PythonMagick-0.9.11.tar.gz
        # cd PythonMagick-0.9.11
        # ./configure
        # make
        # make install

## 3、使用Scrapy
### (1)测试
        # scrapy -h
        # scrapy list

### (2)生成项目
        # scrapy startproject driving

### (3)执行抓取
        # cd driving
        # scrapy crawl school