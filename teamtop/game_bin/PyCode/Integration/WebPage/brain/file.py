# -*- coding: utf-8 -*-
import me
def drawCode():
	data={}
	#导入包
	import Image, ImageDraw, ImageFont, random, md5, datetime, cStringIO, math
	#image='/media/images/checkcode.gif'
	#im = Image.open(image)  
	#是否要扭曲
	flag = True
	PI = 3.1415926535897932384626433832795
	PI2 = 6.283185307179586476925286766559  
	#图片大小
	imgWidth = 72
	imgHeight = 30
	#文字大小
	minSize = 20
	maxSize = 30
	#噪点个数
	maxPixel = 30
	#噪音线条数
	maxLine = 3
	#倾斜度
	minTilt = -10
	maxTilt = 10
	#设置字体  使用绝对路径
	fontType = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
	#声明图片   ？，画布大小，背景颜色
	img = Image.new("RGBA", (imgWidth, imgHeight),(20, 20, 20, 255))
	#画布
	draw = ImageDraw.Draw(img)    
	#随机一个md5的字符 取其中的4个
	mp = md5.new()    
	mp_src = mp.update(str(datetime.datetime.now()))    
	mp_src = mp.hexdigest()    
	rand_str = mp_src[0:4]
	#依次将字符画到画布上    xy = 位置,text = 文字,font = 字体,fill = 字体颜色
	for i in range(len(rand_str)):
		draw.text(xy = (i * 18 + 2, 0),\
				  text = rand_str[i],\
				  font = ImageFont.truetype(fontType, random.randrange(minSize,maxSize)),\
				  fill = (255, 255, 255, 255))
	#添加噪点
	for i in range(maxPixel):
		x = random.randrange(0, imgWidth)
		y = random.randrange(0, imgHeight)
		#xy = 噪点坐标，value = 颜色
		img.putpixel(xy = (x, y),
					 value = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255),255))
	#画噪音线
	for i in range(maxLine):
		#xy = 坐标，fill = 颜色
		draw.line(xy = (random.randrange(0,imgWidth), random.randrange(0,imgHeight),\
						random.randrange(0,imgWidth), random.randrange(0,imgHeight)),\
				  fill = (100, 150, 100, 255))
	#倾斜度
	img = img.rotate(random.randrange(minTilt, maxTilt))
	#扭曲 通过正弦函数
	if flag:
		tempimg = Image.new("RGBA", (imgWidth, imgHeight),(255, 255, 255, 255))
		for i in range(imgWidth):
			for j in range(imgHeight):
				dx = (PI * j) / imgHeight
				dx += 1
				dy = math.sin(dx)
				oldX = i + dy * 3
				oldY = j
				color = img.getpixel((i, j))
				if (oldX >= 0 and oldX < imgWidth and oldY >= 0 and oldY < imgHeight):
					tempimg.putpixel(xy = (oldX, oldY), value = color)
		img = tempimg
	#释放资源
	del draw
	#将值保存到 session
	me.S['check_code'] = rand_str
	print rand_str
	#写入流
	buf = cStringIO.StringIO()    
	img.save(buf, 'gif')
	from django.http import HttpResponse
	data['return']=HttpResponse(buf.getvalue(),'image/gif')
	#输出
	return data
	