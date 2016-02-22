#!/usr/bin/env python2.7
#encoding:utf-8
import urllib

url=['']*40

url_base = 'http://blog.liuts.com/index.php'
url_free = "http://blog.liuts.com/"
con = urllib.urlopen(url_base).read()
href = con.find(r'a href="post/')
end = con.find(r'/">',href)
url[0] = url_free + con[href + 6:end]
i = 0
while href != -1 and end != -1 and i < 40:
    i=i + 1
    href = con.find(r'a href="post',end)
    end = con.find(r'/">',href)
    url[i] = url_free + con[href + 6:end]

print url[1]

#print url 



