#!/usr/bin/env python2.7
#encoding=utf8


def spider(url):
     html = requests.get(url)
     selector = etree.HTML(html.text)

     picitems = []
     picitems = selector.xpath('//div[@id="post_content_29397251028"]/img[@class="BDE_Image"]')
     print(len(picitems));
     picitems = selector.xpath('//div[@class="d_post_content j_d_post_content  clearfix"]/img[@class="BDE_Image"]')
     print(len(picitems))
 
     i = 0
     for pic in picitems:
         url = pic.xpath('@src')[0]
#        print(url)
         #print(url)
         dir = './%d.jpg'%i
         download_Image(url, dir)
         i += 1
 

# 下载图片
def download_Image(url, save_path):
     urllib.request.urlretrieve(url, save_path)


