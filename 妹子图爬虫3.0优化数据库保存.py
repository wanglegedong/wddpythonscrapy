from bs4 import BeautifulSoup
import os
import requests
from pymongo import MongoClient
import datetime
import time
import random

class mzitu():
    def __init__(self):
        client = MongoClient()  #与MongDB建立连接（这是默认连接本地MongDB数据库）
        db = client['meinvxiezhenji']  #选择或创建一个数据库
        self.meizitu_collection = db['meizitu']  #在meizixiezhenji这个数据库中，选择一个集合
        self.title = ''  #用来保存页面主题
        self.url = ''  ##用来保存页面地址
        self.img_urls = []  ##初始化一个 列表  用来保存图片地址
        self.href=''
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]   #这是hearders 库
        self.iplist = [
            "123.163.96.88",
            "163.204.246.48",
            "183.129.244.16",
            "120.79.203.1",
            "114.113.222.131",
            "180.118.135.18",
            "120.25.203.182",
            "163.204.245.203",
            "59.37.33.62",
            "43.248.123.237",
            "175.44.156.198",
            "120.236.178.117",
            "183.158.202.222",
            "221.1.200.242",
            "61.176.223.7"
        ]  # 这是IP池
    def all_url(self, url):   #查找全站图片的URL
        html = self.request(url,href=None)           #请求访问网页
        all_a = BeautifulSoup(html.text, 'lxml').find('div', class_='all').find_all('a')  #解析网页并找到图片地址
        for a in all_a:
            title = a.get_text()
            old = '早期图片'   #简单清洗一个叫早期图片的没用的URL
            if title == old:
                continue
            self.title = title  ##将主题保存到self.title中
            print(u'开始保存：', title)
            path = str(title).replace("?", '_')
            self.mkdir(path)
            href = a['href']
            self.url = href  ##将页面地址保存到self.url中
            if self.meizitu_collection.find_one({'主题页面': href}):  ##判断这个主题是否已经在数据库中、不在就运行else下的内容，在则忽略。
                print(u'这个页面已经爬取过了')
            else:
                self.html(href)

    def html(self, href):
        html = self.request(href)
        max_span = BeautifulSoup(html.text, 'lxml').find('div', class_='pagenavi').find_all('span')[-2].get_text()
        page_num = 0  ##这个当作计数器用 （用来判断图片是否下载完毕）
        self.img_urls=[] ##每个文件夹保存后清零
        for page in range(1, int(max_span) + 1):
            page_num = page_num + 1  ##每for循环一次就+1  （当page_num等于max_span的时候，就证明我们的在下载最后一张图片了）
            page_url = href + '/' + str(page)
            self.img(page_url,href ,max_span, page_num)  ##调用img函数

    def img(self, page_url,href,max_span, page_num):  ##添加上面传递的参数
        img_html = self.request(page_url,href=href)
        img_url = BeautifulSoup(img_html.text, 'lxml').find('div', class_='main-image').find('img')['src']
        self.img_urls.append(img_url)
        if int(max_span) == page_num:  ##我们传递下来的两个参数用上了 当max_span和Page_num相等时，就是最后一张图片了，最后一次下载图片并保存到数据库中。
            self.save(img_url,href)
            post = {  ##这是构造一个字典，里面有啥都是中文，很好理解吧！
                '标题': self.title,
                '主题页面': self.url,
                '图片地址': self.img_urls,
                '获取时间': datetime.datetime.now()
            }
            self.meizitu_collection.save(post)  ##将post中的内容写入数据库。
            print(u'插入数据库成功')
        else:  ##max_span 不等于 page_num执行这下面
            self.save(img_url,href)
    def save(self, img_url,href):
        name = img_url[-9:-4]
        print(u'开始保存：', img_url)
        img = self.request(img_url,href=href)
        print(img)
        f = open(name + '.jpg', 'ab')
        f.write(img.content)
        f.close()
        time.sleep(0.5)

    def mkdir(self, path):  ##这个函数创建文件夹
        path = path.strip()
        isExists = os.path.exists(os.path.join("D:\mzitu", path))
        if not isExists:
            print(u'建了一个名字叫做', path, u'的文件夹！')
            os.makedirs(os.path.join("D:\mzitu", path))
            os.chdir(os.path.join("D:\mzitu", path))  ##切换到目录
            return True
        else:
            print(u'名字叫做', path, u'的文件夹已经存在了！')
            os.chdir(os.path.join("D:\mzitu", path))
            return False

    def request(self,url,href=None,proxy=None,timeout=3,num_retries=6):
        UA = random.choice(self.user_agent_list)
        headers = {'User-Agent': UA}
        headers['referer'] = href
        try:
            return requests.get(url, headers=headers,proxies=proxy, timeout=timeout)
        except:
            print(u'开始使用代理')
            time.sleep(10)
            IP = ''.join(str(random.choice(self.iplist)).strip())  ##下面有解释哦
            proxy = {'http': IP}
            try:
                return requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
            except:
                if num_retries > 0:
                    time.sleep(10)
                    IP = ''.join(str(random.choice(self.iplist)).strip())
                    proxy = {'http': IP}
                    print(u'正在更换代理，10S后将重新获取倒数第', num_retries, u'次')
                    print(u'当前代理是：', proxy)
                    num_retries -= 1
                    return self.request(url,href=href, proxy=proxy,timeout=3,num_retries=num_retries)
                else:
                    print(u'代理也不好使了！取消代理')
                    return self.request(url, 3)

Mzitu = mzitu()  ##实例化
Mzitu.all_url('http://www.mzitu.com/all')  ##给函数all_url传入参数  你可以当作启动爬虫（就是入口）
# -*- coding:utf-8 -*-
