#!/usr/bin/python
#-*-coding:utf-8-*-
import me,csv, MySQLdb, sys,traceback

#===============================================================================
# 工具
#===============================================================================
import me
def copy(m):
	import copy as CP
	return CP.deepcopy(m)
#date
def date(m,format='%Y-%m-%d'):
	import time
	s=time.strftime(format,time.localtime(m))
	return s
def monthRange(start=True,m=None,year=None):
	data=''
	import calendar,time
	if not m:m=date(time.time(),'%m')
	if not year:year=int(date(time.time(),'%Y'))
	
	FORMAT = "%s-%s-%s"
	d = calendar.monthrange(year, int(m))
	if start:
		data = FORMAT % (year, m, '01')
	else:
		data = FORMAT % (year, m, d[1])
	return data
	
def strtotime(m,format='%Y-%m-%d %H:%M:%S'):
	import time
	try:
		s = time.mktime(time.strptime(m,format))
	except:
		traceback.print_exc()
	return int(s)
	
def getDateRange(start,end,interval=86400,format="%Y-%m-%d"):
	start_time=strtotime(start,'%Y-%m-%d')
	end_time=strtotime(end,'%Y-%m-%d')
	if (start_time==end_time) and interval==86400:return [start]
	data=[]
	for i in range(0,(end_time+86400-start_time)/interval):
		data.append(date(start_time+i*interval,format))
	return data
#/date

# 处理数据库的函数
def mysql_database(sql_str, values):
    conn = MySQLdb.connect(host='127.0.0.1', user='staistar',passwd='staistarmysql2012')
    cursor = conn.cursor()
    conn.select_db('staistar')
    
    cursor.executemany(sql_str, values)
    conn.commit()
    
    cursor.close()
    conn.close()

def importProduct(reader):
    values=[]
    for obj1 in reader:
        values.append((obj1['id'], obj1['name']))
    return values

# 处理转码的函数
def mdcode(str1):
    for c in ('utf-8', 'gbk', 'gb2312'):
        try:
            return str1.decode(c).encode('utf-8')
        except:
            pass
    return 'unknown'

def filterJSON(get):
	if isinstance(get,basestring):
		get=get.strip().replace('\r','').replace('\n','').replace('\t','')
		if get=='':
			get='{}'
		return get
	elif isinstance(get,dict):
		from decimal import Decimal
		for k,v in get.items():
			if isinstance(v,Decimal):
				get[k]="%d"%v
		return get
	else:
		return '{}'
def Dict(get=None):
	if not get:get=[]
	import collections
	data=collections.OrderedDict()
	if len(get)==0:
		return data
	for k,v in enumerate(get):
		key=k
		if 'key' in v:
			key=v['key']
		data[key]=v
	return data
def dictToList(msg,index):
	if isinstance(msg,tuple) or isinstance(msg,list):
		data=[]
		for v in msg:
			t=[]
			for kk in index:
				t.append(v.get(kk,""))
			data.append(t)
		return data
	
def rangeDatum(msg,index,sum=False):
	data=Dict()
	index=index.split(',')
	range=[]
	length=len(index)
	for k,v in enumerate(index):
		if k==0:
			range.append([0,int(v)])
		if k==length-1:
			range.append([int(v),0])
		else:
			range.append([int(v),int(index[k+1])])
	for v in msg:
		for vv in range:
			#set key
			if vv[1]==0:
				key=key='%s-%s'%(vv[0],'+oo')
			else:
				key='%s-%s'%(vv[0],vv[1])
			#default value
			if not key in data:
				data[key]=0
			#compare
			interval=1
			if sum:
				interval=v
			if vv[1]>0:
				if v>=vv[0] and v<vv[1]:
					#print '%s:%s=<%s<%s'%(key,vv[0],v,vv[1])
					data[key]+=interval
			else:
				if v>=vv[0]:
					data[key]+=interval
	return data
def rangeData(msg,index,range_key,sum=False):
	data=Dict()
	#get range
	index=index.split(',')
	range=[]
	length=len(index)
	for k,v in enumerate(index):
		if k==0:
			range.append([0,int(v)])
		if k==length-1:
			range.append([int(v),0])
		else:
			range.append([int(v),int(index[k+1])])
	for v in msg:
		for vv in range:
			#set key
			if vv[1]==0:
				key=key='%s-%s'%(vv[0],'+oo')
			else:
				key='%s-%s'%(vv[0],vv[1])
			#default value
			if not key in data:
				data[key]={}
			#compare
			for kkk,vvv in v.items():
				if not kkk in data[key]:
					data[key][kkk]=0
				#compare
				interval=1
				if sum:
					interval=float(vvv)
				if vv[1]>0:
					if v[range_key]>=vv[0] and v[range_key]<vv[1]:
						#print '%s:%s=<%s<%s'%(key,vv[0],v,vv[1])
						data[key][kkk]+=interval
				else:
					if v[range_key]>=vv[0]:
						data[key][kkk]+=interval
	return data
def encrypt(msg,key=''):
	import hashlib
	return hashlib.new("md5",msg+key).hexdigest()

def formatSize(m,unit=0):
	units=['B','K','M','G','T']
	if float(m)<float(999):
		return '%s%s'%(round(m,2),units[unit])
	else:
		m=float(m)/1024
		unit+=1
		return formatSize(m,unit)
		
def pickle(m,un=None):
	import cPickle
	if un:
		m=cPickle.loads(m)
	else:
		m=cPickle.dumps(m)
	return m

def removeTags(msg):
	table_word_to_html=[' (class)*(style)*(valign)*(width)*="[^"]*"',#tags
	'(<span>)*(</span>)*',#span
	'<td>']

def drawCode():
	from PIL import Image, ImageDraw, ImageFont
	import os,me,random,StringIO
	"""
	background  #随机背景颜色
	line_color #随机干扰线颜色
	img_width = #画布宽度
	img_height = #画布高度
	font_color = #验证码字体颜色
	font_size = #验证码字体尺寸
	font = I#验证码字体
	"""
	 
	string = {'number':'',
			  'litter':'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
	background = (random.randrange(230,255),random.randrange(230,255),random.randrange(230,255))
	line_color = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
	img_width = 58
	img_height = 22
	font_color = ['black','darkblue','darkred']
	font_size = 14
	font = ImageFont.truetype('%s%sbody%sfont%sArial.ttf'%(me.S['ME'],os.sep,os.sep,os.sep),font_size)
	me.S['code'] = ''

	#新建画布
	im = Image.new('RGB',(img_width,img_height),background)
	draw = ImageDraw.Draw(im)
	code = random.sample(string['litter'],4)
	#新建画笔
	draw = ImageDraw.Draw(im)

	#画干扰线
	for i in range(random.randrange(3,5)):
		xy = (random.randrange(0,img_width),random.randrange(0,img_height),
			  random.randrange(0,img_width),random.randrange(0,img_height))
		draw.line(xy,fill=line_color,width=1)
	 
	#写入验证码文字
	x = 2
	for i in code: 
		y = random.randrange(0,10)
		draw.text((x,y), i, font=font, fill=random.choice(font_color))
		x += 14
		me.S['code'] += i
	del x
	 
	del draw
	buf = StringIO.StringIO()
	im.save(buf,'gif')
	buf.closed
	return {"return":buf.getvalue(),"type":'image/gif'}