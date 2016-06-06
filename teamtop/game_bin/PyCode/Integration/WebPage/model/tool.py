#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 工具
#===============================================================================
import me

def date(m,format='%Y-%m-%d'):
	import time
	s=time.strftime(format,time.localtime(m))
	return s
	
def strtotime(m,format='%Y-%m-%d %H:%M:%S'):
	import time
	s = time.mktime(time.strptime(m,format))
	return int(s)
	
def getDateRange(start,end):
	start_time=strtotime(start,'%Y-%m-%d')
	end_time=strtotime(end,'%Y-%m-%d')
	data=[]
	for i in range(start_time,end_time+86400):
		data.append(date(i))
	return data
def drawCode(request):
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
	S=request.session
	string = {'number':'',
			  'litter':'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
	background = (random.randrange(230,255),random.randrange(230,255),random.randrange(230,255))
	line_color = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
	img_width = 58
	img_height = 22
	font_color = ['black','darkblue','darkred']
	font_size = 14
	font = ImageFont.truetype('%s%sview%sfont%sArial.ttf'%(S['ME'],os.sep,os.sep,os.sep),font_size)
	S['code'] = ''

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
		S['code'] += i
	del x
	 
	del draw
	buf = StringIO.StringIO()
	im.save(buf,'gif')
	buf.closed
	return {"return":buf.getvalue(),"type":'image/gif'}