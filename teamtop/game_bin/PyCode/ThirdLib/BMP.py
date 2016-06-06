#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 生成BMP图片
#===============================================================================
import zipfile
import os
class color(object):
	R =0
	G =0
	B =0
	def __init__(self,r,g,b):
		self.R = r % 256
		self.G = g % 256
		self.B = b % 256
	
	def __eq__(self, other):
		return self.R == other.R and self.G == other.G and self.B == other.B

def bin2int( b,start,count):
	r = 0
	for i in range(start+count-1,start-1,-1):
		r=r*256+ b[i]
	return r

def int2bin(x , nBits):
	b = bytearray( nBits)
	for i in range(nBits-1,-1,-1):
		b[nBits-1-i]= x % 256
		x = x / 256
	return b

def putbin(b, x_int,start, count):
	b[start:start + count] = int2bin(x_int, count)

class bmp24(object):
	width = 1
	height = 1
	bitCount =24
	DataSizePerLine = 0
	data = []
	head = bytearray(14)
	bmpinfo = bytearray(40)
	
	def __init__( self, w, h):
		w=abs(int(w))
		h=abs(int(h))
		if w<1:
			w=10
		if h<1:
			h=10
		self.width = w
		self.height = h
		self.DataSizePerLine= (self.width * self.bitCount + 31) // 32 * 4
		self.data = [bytearray(self.DataSizePerLine) for _ in range(0,h)]
		self.head[0] = ord("B")
		self.head[1] = ord("M")
		putbin( self.head, 54 + self.DataSizePerLine * h, 2,4) #文件大小
		putbin( self.head, 54, 10, 4) #位图数开始的位置
		putbin( self.bmpinfo, 40, 0, 4)
		putbin( self.bmpinfo, w, 4, 4)
		putbin( self.bmpinfo, h, 8, 4)
		putbin( self.bmpinfo, 1, 12, 2) # 设置位面数
		putbin( self.bmpinfo, self.bitCount, 14,2) # 设置每个像素所点的bit数
		putbin( self.bmpinfo, 0, 16, 4) # 设置biCompression
		putbin( self.bmpinfo, self.DataSizePerLine * h, 20,4)#biSizeImage
		putbin( self.bmpinfo, 2835, 24, 4)#biXPlosPerMeter
		putbin( self.bmpinfo, 2835, 28, 4)#biYPlosPerMeter
		putbin( self.bmpinfo, 0, 32, 4)#biClrUsed
		putbin( self.bmpinfo, 0, 36, 4)#biClrImportant
	
	def __draw_point( self, x, y, clr):
		Y = self.height - y - 1
		X = x * 3
		self.data[Y][X] = clr.B
		self.data[Y][X+1] = clr.G
		self.data[Y][X+2] = clr.R
		
	def draw_point( self, x, y, clr):
		if x < 0:
			return
		if x >= self.width:
			return
		if y < 0:
			return
		if y >= self.height:
			return
		self.__draw_point(x,y,clr)
	
	def get_point(self, x, y):
		if x < 0:
			return
		if x >= self.width:
			return
		if y < 0:
			return
		if y >= self.height:
			return
		Y = self.height - y - 1
		X = x * 3
		return color(self.data[Y][X+2], self.data[Y][X+1], self.data[Y][X])
	
	def fill(self, clr):
		for x in range(0, self.width):
			y=self.height - 1
			self.__draw_point(x, y, clr)
		for y in range(1,self.height):
			self.data[y] = self.data[0][:]
	
	def box(self, x1, y1, x2, y2, clr):
		if x1 > x2:
			x1, x2 = x2, x1
		if y1 > y2:
			y1, y2 = y2, y1
		x1=max(x1, 0)
		x2=min(x2, self.width-1)
		y1=max(y1, 0)
		y2=min(y2, self.height-1)
		for x in range(x1, x2 + 1):
			for y in range(y1,y2+1):
				self.__draw_point(x,y,clr)
	
	def line(self,x1,y1,x2,y2,clr):
		if (x1>x2):
			x1,x2=x2,x1
			y1,y2=y2,y1
		
		dx=x2-x1;ddx=1;
		if (dx==0):
			ddx=0;
		dy = y2-y1;
		ddy = 1;
		if (dy<0) :
			ddy=-1;
		if (dy == 0):
			ddy=0;
		if ( (dy==0)and(dx==0)):
			self.draw_point( x1,y1,clr);return;
		
		if (dy==0):
			for i in range(x1,x2+1 ):
				self.draw_point( i,y1,clr);
			return;
		
		if (dx==0):
			if (dy<0) :
				y1,y2=y2,y1
			for i in range(y1 ,y2+1) :
				self.draw_point( x1,i,clr);
			return;
		
		self.draw_point(x1,y1,clr);
		self.draw_point(x2,y2,clr);
		x = x1
		y = y1
		dx = abs(x2-x1)
		dy = abs(y2-y1)
		s1 = ddx;
		s2 = ddy;
		key =0;
		if(dx>dy):
			dx,dy=dy,dx
			key=1
		e = 2*dy-dx;
		for i in range(0,dx+1):
			px = 0;
			py = 0 ;
			self.draw_point(x,y,clr);
			while(e>=0):	
						if(key==1):
								x += s1 ; px += s1;
						else:
								y += s2; py += s2;
						e = e-2*dx ;
						self.draw_point(x,y,clr);
			if(key==1):
					y += s2;
			else:
					x += s1;
			e = e+2*dy;
			self.draw_point(x,y,clr);
	
	def iter_triangle(self, x, y):
		r = 0
		while True:
			r += 1
			for dx in xrange(r):
				dy = r -dx -1
				nx = x + dx
				ny = y + dy
				if nx < self.width and ny < self.height:
					yield nx, ny
				else:
					raise StopIteration
	
	def drow_points(self, pos_list, clr):
		for x, y in pos_list:
			for nx, ny in self.iter_triangle(x, y):
				if self.get_point(nx, ny) == clr:
					continue
				self.draw_point(nx, ny, clr)
				break
	
	def save_zip(self, folder, file_name):
		bmp_file_path = "%s%s.bmp" % (folder, file_name)
		zip_file_path = "%s%s.zip" % (folder, file_name)
		with open(bmp_file_path, "wb") as f:
			f.write(self.head)
			f.write(self.bmpinfo)
			for d in self.data:
				f.write(d)
		zf = zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED)
		zf.write(bmp_file_path, "%s.bmp" % file_name)
		zf.close()
		os.remove(bmp_file_path)
		return zip_file_path

back = color(0, 0, 0)
white = color(255,255,255)
red = color(255,0,0)
green = color(0,255,0)
blue = color(0,0,255)


