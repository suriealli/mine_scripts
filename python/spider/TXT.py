#!/usr/bin/python2.7
#coding=utf8
import urllib2
import re
import chardet

def spider(url):
    user_agent ='Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    headers = { 'User-Agent' : user_agent }
    Request = urllib2.Request(url, headers = headers) 
    Response = urllib2.urlopen(Request)
    html = Response.read()
    charset = chardet.detect(html)['encoding']
    if charset == 'utf-8' or charset == 'UTF-8' or charset == 'utf8':
        html = html
    else:
        html = html.decode('gb2312','ignore').encode('utf-8')
    unicodehtml = html.decode("utf-8")
    #获取下一张链接
    try:
        Next = re.search('\xe4\xb8\x8a\xe4\xb8\x80\xe7\xab\xa0(.*?)\xe4\xb8\x8b\xe4\xb8\x80\xe7\xab\xa0</a>',html,re.S)
        Next = Next.group(0)
        Next = re.search('<a href=\"(.*?)\">',Next,re.S)
        url = "http://www.17k.com%s" %(Next.group(1))
    except:
        print "The End"
    #抓取标题
    try:
        title = re.search('<h1 itemprop=\"headline\">(.*?)</h1>',unicodehtml,re.S)
        title = title.group(1)
    except:
        print "未能捕捉标题"
        return
    #抓取正文
    try:
        content = re.search('<div id=\"chapterContentWapper\">(.*?)</div>',unicodehtml,re.S)
        content = content.group(1)
        content = re.sub(r"<!--[\s\S]*","",content)
    except:
        print "未能捕捉正文"
        return
    
    content = content.replace("<br>","\n")
    content = content.replace("<br/>","")
    text = {'title':title,'content':content,'Next_url':url}
    return text
    

url = "http://www.17k.com/chapter/391013/8452195.html"
TXT = spider(url)
i=1
while 1:
    filename = "D:\python_get_TXT/lxzs_%s.txt" %(i)
    f = open(filename,'w+')
    f.write(TXT['title'])
    f.write(TXT['content'])
    f.close()    
    TXT = spider(TXT['Next_url'])
    i+=1

