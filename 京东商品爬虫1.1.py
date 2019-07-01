# -*- coding:utf-8 -*-
# 搜索京东商品  使用动态数据抓取
import requests
from bs4 import BeautifulSoup
import re
import csv

class JD:
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}  ##浏览器请求头
    def req(self, url):
        # 解析京东搜索首页地址
        soup1 = self.requests_utf(url)
        allcount = soup1.find('span', id='J_resCount').get_text()   #找到商品总数
        print('共有',allcount,'件商品')
        print('**************************************************************************')
        # 查询搜索的商品总页数
        page = int(soup1.find('span', class_='fp-text').i.get_text())
        print(page)

        for i in range(1, page * 2, 2):
            url_star = url[:-2] + str(i)
            print(url_star)
            # 根据商品页数解析搜索地址
            soup = self.requests_utf(url_star)

            # 定位商品信息
            li_all = soup.find_all('li', class_='gl-item')

            for i in li_all:

                # 商品标题
                title = i.a['title']
                print(title)

                # 商品实际地址
                href = i.a['href']
                if href[:4] == 'http':
                    pass
                else:
                    href = 'https:' + href
                print(href)

                # 价格
                price = float(i.i.get_text())
                print(price)

                # 解析商品实际地址
                soup_href = self.requests_gbk(href)

                real_href = soup_href.find('link', rel="canonical")['href']
                real_href = 'https:' + real_href

                # 定位商品名称并去空格
                sku_name = soup_href.find('div', class_='sku-name')
                product_name = str(sku_name.get_text()).strip()

                # 产品Id
                search_ID = re.search('\d+', real_href)
                product_ID = search_ID.group()

                # 解析产品评价js，返回数据
                summary = self.product_summary(product_ID)
                goodRateShow = ''.join(summary[0])
                goodCountStr = ''.join(summary[1])

                if price <= 10000:   #清洗价格过高的数据
                    print('商品ID：', product_ID)
                    print('商品：', product_name)
                    print('商品标题：', title)
                    print('好评累计：', goodCountStr)
                    print('好评率：', goodRateShow + '%')
                    print('链接地址：', real_href)
                    print('价格：', price)
                    print('*************************************************************************')
                    with open('jingdong.csv', 'a', newline='') as csvfile:    #保存到CSV列表里
                        writer = csv.writer(csvfile)
                        writer.writerow([product_ID, product_name, title, goodCountStr, goodRateShow, real_href, price])
                else:
                    continue
                # print('可用优惠券：',quan)
                # print('优惠券信息：',quan_item)

    # 产品评价
    def product_summary(self, product_ID):
        url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv5292&productId=' + product_ID + '&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
        pro_req = self.requests_gbk(url)
        # 好评率
        pattern0 = re.compile('goodRateShow":(.*?),"poorRateShow')
        # 好评累计
        pattern1 = re.compile('"goodCountStr":"(.*?)",')
        # 部分评价
        pattern_ping0 = re.compile('("content":"(.*?){2}","creationTime)')
        search0 = re.findall(pattern0, str(pro_req))
        search1 = re.findall(pattern1, str(pro_req))
        return search0, search1

    # 解析网页utf-8
    def requests_utf(self, url):
        try:
            content = requests.get(url, headers=self.headers)
            content.encoding = 'utf-8'
            soup = BeautifulSoup(content.text, 'lxml')
            return soup
        except:
            print('UTF-8网页解析发生错误！！！！')

    # 解析网页gbk
    def requests_gbk(self, url):
        try:
            content = requests.get(url, headers=self.headers)
            content.encoding = 'gbk'
            #soup = BeautifulSoup(content.text, 'html5lib')
            soup = BeautifulSoup(content.text, "html.parser", from_encoding="gbk")
            return soup
        except:
            print('GBK网页解析发生错误！！！！')

jd = JD()
search_word = '女式包'
url = 'https://search.jd.com/Search?keyword=' + search_word + '&enc=utf-8'
jd.req(url)