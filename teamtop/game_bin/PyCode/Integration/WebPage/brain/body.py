# -*- coding: utf-8 -*-
import os,sys,json,time,traceback
import me,tool,memory,model,word
from StringIO import StringIO
data={}

config={
	"operator_time_adjust":{1:0,2:0,101:-15*3600,102:0},
	"operator_currency":{1:"CNY",2:"CNY",101:"USD",102:"TWD"},
	"currency_name":{"CNY":"元","USD":"美元","TWD":"台幣"},
	"currency_rate":{"CNY":0.1,"USD":0.1,"TWD":5}
}

#draw form
def drawForm(msg):
	form=""
	#default data
	data=msg.get('data',{})
	form='<form class="form" method="post">'
	#table
	table=''
	for k,v in msg['property'].items():
		#get entity info
		if k not in data and k in me.S['G']:
			data[k]=me.S['G'][k]
		#secret or protected field
		if ('secret' in msg and k in msg['secret']) or 'protected' in v:
			continue
		if 'label' not in v:
			v['label']=k.title()
		v['label']=word.check(v['label'])
		#tips
		tips=''
		if 'tips' in v:
			tips='&nbsp&nbsp&nbsp&nbsp<span class="warm">* %s</span>' % (v['tips'])
		#style
		#ERROR
		if 'E' in me.S:
			if k in me.S['E']:
				tips='<span class="warn">%s</span>%s' % (me.S['E'][k],tips)
		column=''
		#common type columns
		type_template={
			"hidden":'<input type="hidden" name="%s" value="%s"/>' % (k,data.get(k)),
			"password":'<td class="label">%s:</td><td><input name="%s" type="password"/>%s</td>' % (v['label'],k,tips),
			"text":'<td class="label">%s:</td><td><textarea class="textarea" name="%s">%s</textarea>%s</td>' % (v['label'],k,data.get(k,''),tips),
			"datetime":'<td class="label">%s:</td><td><input type="text" class="date" name="%s" value="%s" id="datetime_%s"/></td>' % (v['label'],k,data.get(k,time.strftime('%Y-%m-%d %H:%M:%S')),k),
			"date":'<td class="label">%s:</td><td><input type="text" class="date" name="%s" value="%s" id="date_%s"/>%s</td>' % (v['label'],k,data.get(k,time.strftime('%Y-%m-%d')),k,tips),
			"string":'<td class="label">%s:</td><td><input type="text" name="%s" value="%s"/>%s</td>' % (v['label'],k,data.get(k,''),tips),
			"int":'<td class="label">%s:</td><td><input type="text" name="%s" value="%s"/>%s</td>' % (v['label'],k,data.get(k,''),tips)
		}
		if v['type'] in type_template:
			column=type_template[v['type']]
		if v['type']=='checkbox':
			#default data
			checked=[]
			if k in data:
				checked=data[k].split(',')
			column='<td class="label">'+v['label']+':</td><td>'
			for vv in v['option']:
				checked_html=""
				if vv['value'] in checked:
					checked_html=' checked="checked" '
				column+='<input type="checkbox" name="'+k+'" value="'+vv['value']+'" '+checked_html+'/>'+vv['label']
		
			column+='<span><span id="input_'+k+'_tips">'+tips+'</span></span></td>'
		if v['type']=='radio':
			column='<td class="label">'+v['label']+':</td><td>'
			for vv in v['option']:
				selected=''
				if (k not in data and 'selected' in vv) or (k in data and str(data[k])==str(vv['value'])):
					selected='checked="checked"'
				column+='<input type="radio" name="'+k+'" value="'+vv['value']+'" '+selected+'/>'+vv['label']+' '
			column+='<span><span id="input_'+k+'_tips">'+tips+'</span></span></td>'
		if v['type']=='link':
			column='<td class="label">%s:</td><td>'%(v['label'])
			linkData={}
			if 'memory' in v["link"]:
				linkData=model.get({"temp":v['link']['memory']})['temp']
			#default view
			if 'view' not in v:v['view']="select"
			#checkbox
			if v['view']=="checkbox":
				column+='<input class="checkAll" type="checkbox" value="" forname="%s">%s&nbsp;&nbsp;'%(k,word.check('全选'))
				for kk,vv in linkData.items():
					checked=''
					if str(vv['key']) in str(data.get(k)).split(","):
						checked=' checked'
					column+='<input type="checkbox" name="%s" value="%s"%s> %s &nbsp;'%(k,vv['key'],checked,vv['value'])
			#select
			elif v['view']=="select":
				column+='<select name="'+k+'">'
				for kk,vv in linkData.items():
					selected=''
					if str(data.get(k))==str(vv['key']):
						selected=' selected="selected"'
					column+='<option value="%s"%s>%s</option>'%(vv['key'],selected,vv['value'])
				column+='</select>'
			
			column+='<span><span>%s</span></span></td>'%(tips)
		if v['type']!='hidden' and v['type']!='user':
			column="<tr>%s</tr>"%(column)
		table+=column
	#wrap form
	table='<table style="line-height:1.5em;" class="table table-striped">%s' % (table)
	form+=table
	
	#close form
	submit_text=word.check('提交')
	form+='<tr><td>%s</td><td><button class="submit pending btn btn-info btn-small" type="submit"><i class="icon-share-alt icon-white"></i>&nbsp;%s</button></td></tr></table></form>' % (word.check('确认提交'),submit_text)
	return form
#获取分页信息
def getRange(m=None):
	#if is a instant scent render with javascript
	if not m:m={}
	m['render']=' href="'
	#get now range
	size=m.get('size','10')
	m['range']=me.S['G'].get('range','1,'+size)
	msg_path=''
	if 'msg' in m:
		for k,v in m['msg'].items():
			msg_path+='&'+k+'='+v
	m['render']=m['render']+m['url']
	#get model count
	msg={'one':True,'model':m['model'],'field':'count(*) as count'}
	if 'memory' in m:
		msg['memory']=m['memory']
	if 'filter' in m:
		msg['filter']=m['filter']
	if 'option' in m:
		msg['option']=m['option']
	m['count']=memory.get('recall',msg)
	m['count']=m['count']['count']
	#if count 0
	if m['count']==0:
		return {"html":'<div class="range" class="warm">'+word.check("没有数据!")+'</div>',"range":m['range']}
	Range=m['range'].split(',')
	page_size=int(Range[1])
	page=int(Range[0])
	import math
	page_count=int(math.ceil(float(m['count'])/page_size))
	if page_count==0:
		page_count=1
	pre_page=page-1
	if pre_page<1:
		pre_page=1
	next_page=page+1
	if next_page>page_count:
		next_page=page_count
	start_page=page-5
	if start_page<1:
		start_page=1
	end_page=page+5
	if end_page>page_count:
		end_page=page_count
	color=''
	active=''
	range_html='%s %s &nbsp<a %s?range=1,%s%s">%s</a>&nbsp<a %s?range=%s,%s%s">%s</a>&nbsp' % (word.check('总页数'),page_count,m['render'],page_size,msg_path,word.check('首页'),m['render'],pre_page,page_size,msg_path,word.check('上页'))
	start_list_page=1
	if page>1 and (page-5)>0:
		start_list_page=page-5
	end_list_page=start_list_page+9
	if page_count<end_list_page:
		end_list_page=page_count
	for i in range(start_list_page,end_list_page+1):
		color=''
		active=''
		#active
		if i==page:
			color='red'
			active='class="active"'
		range_html+='<a %s style="color:%s" %s?range=%s,%s%s">%s</a>&nbsp' % (active,color,m['render'],i,page_size,msg_path,i)
	range_html+='<a %s?range=%s,%s%s">%s</a>&nbsp<a %s?range=%s,%s%s">%s</a>&nbsp' % (m['render'],next_page,page_size,msg_path,'下页',m['render'],page_count,page_size,msg_path,'末页')
	return {"html":'<div class="range">%s</div>' % range_html,"range":m['range']}

def render(frame):
	from mako.template import Template
	from mako.lookup import TemplateLookup
	from mako.exceptions import RichTraceback
	content=''
	try:
		mylookup = TemplateLookup(directories=[os.path.dirname(__file__).replace('brain','body'+os.sep+'frame'+os.sep)],strict_undefined=False,input_encoding='utf-8',output_encoding='utf-8', encoding_errors='replace')
		View=Template(frame,strict_undefined=False,lookup=mylookup,input_encoding='utf-8',output_encoding='utf-8', encoding_errors='replace')
		content=View.render(**data) #theme place
	except:
		traceback = RichTraceback()
		for (filename, lineno, function, line) in traceback.traceback:
			print "File %s, line %s, in %s" % (filename, lineno, function)
			print line, "\n"
		print "%s: %s" % (str(traceback.error.__class__.__name__), traceback.error)
	return content

def show():
	#if just for redirect action or response
	if 'url' in data or 'response' in data or 'return' in data:
		return data
	#data
	data['S']=me.S
	if me.S['A']['model']!="guide":
		data["location"]=locate()
	content=render('<%include file="index.htm"/>')
	return content

def locate():
	html=""
	try:
		import right
		html='''<ul class="breadcrumb" style="background:none;margin:0;padding:8px 10px 5px 5px;;margin-bottom:8px;">
			<li><a href="#"><i class="icon-map-marker"></i>&nbsp;&nbsp;首页</a> <span class="divider">/</span></li>
			<li><a href="#">%s</a> <span class="divider">/</span></li>
			<li class="active">%s</li>
		</ul>'''%(
			model.info().get(me.S["A"]["model"],{"label":"欢迎页"})["label"],
			right.getAll().get("%s_%s"%(me.S['A']['model'],me.S['A']['action']),{"name":"欢迎来到猎影游戏管理后台！"})["name"]
		)
	except:
		pass
	return html
def now():
	import time
	return time.time()+config['operator_time_adjust'][int(me.S['A']['operator'])]

#body data
def D(context,msg):
	data={}
	data=me.review('model').get(msg)
	return data
def M(context,msg=None):
	data=me.review('model').info(msg)
	return data
#frame
def say(context,msg):
	return me.review('word').check(msg)

def conf(context,cat,key):
	global config
	return config[cat][key]
def parseJSON(context,m):
	import tool,json
	m=tool.filterJSON(m)
	m=json.loads(m)
	return m
def encodeURL(context,m,slash=False):
	import tool
	m=tool.encodeURL(m,slash)
	return m
def decodeURL(context,m,slash=False):
	import tool
	m=tool.decodeURL(m,slash)
	return m
def pickle(context,m,un=None):
	m=me.review("tool").pickle(m.encode("utf8"),un)
	return m
def call(context,m):
	data=eval(m)
	return data