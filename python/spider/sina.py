#!/usr/bin/env python2.7
#encoding:utf-8
import urllib
import urllib2
url=['']*40

url_base = 'http://weibo.com/zuozuomuxifans?from=myfollow_group&is_all=1'
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
values = {'name' : 'Michael Foord','location' : 'Northampton','language' : 'Python' }
headers = { 'User-Agent' : user_agent }
data = urllib.urlencode(values)
req = urllib2.Request(url_base,data,headers)
response = urllib2.urlopen(req)
html = response.read()
print html


#print url 



