#!/usr/bin/env python2.7
#encoding=utf8
import requests
from lxml import etree
import urllib

def spider(url):
     html = requests.get(url)
     selector = etree.HTML(html.text)

     picitems = []
#     picitems = selector.xpath('//div[@id="post_content_29397251028"]/img[@class="BDE_Image"]')
     picitems = selector.xpath('//div[@id="image-show"]/img[@id="bigImg"]')
     print picitems
#     picitems = selector.xpath('//div[@class="d_post_content j_d_post_content  clearfix"]/img[@class="BDE_Image"]')
     print(len(picitems))
     for pic in picitems:
         url = pic.xpath('@src')[0]
#         print(url)
         filename = url.split("/")[8]
         dir = './%s' % filename
         download_Image(url, dir)
 

# 下载图片
def download_Image(url, save_path):
     urllib.urlretrieve(url, save_path)
for i in range(2,100):
    url = "http://pic.ali213.net/html/2015-12-31/59231_%s.html" %i

    spider(url)
