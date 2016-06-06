#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 索引
#===============================================================================
from django.http import HttpResponse
from Integration.WebPage.User import Permission

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>索引页</title>
</head>
<body>
%s
</body>
</html>'''

def Index(request):
	from Integration import AutoURL
	indexs = []
	for url, doc in AutoURL.auto_indexs.iteritems():
		if not Permission.check(request, url):
			continue
		function=(doc.split('】')[0]+'】',doc.split('】')[1])
		indexs.append((url,function))
	indexs.sort(key=lambda item:item[0])
	guides={}
	for v in indexs:	
		if v[1][0] not in guides:
			guides[v[1][0]]=[]
		guides[v[1][0]].append({"url":v[0],"name":v[1][1]})
	#html
	data=""
	#获取语言设置
	if 'lang' in request.GET:
		request.session['lang']=request.GET['lang']
	#默认语言
	if 'lang' not in request.session:
		request.session['lang']='zh_cn'
	#翻译
	from Integration.WebPage.model import me
	for k,v in guides.items():
		data+="<ul style='float:left;'><li style='list-style-type:none;margin:0 0 5px -18px'>※"+me.say(request,k)+"</li>"
		for vv in v:
			if vv['url'] == "/model/user/login/":
				data+='<li style="list-style-type:circle;"><a href="%s">%s</a></li>' % (vv['url'],me.say(request,vv['name']))
			else:
				data+='<li style="list-style-type:circle;"><a href="%s" target="_blank">%s</a></li>' % (vv['url'],me.say(request,vv['name']))
		data+="</ul>"
	#show
	return HttpResponse(html % data)

