#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.OutBuf")
#===============================================================================
# 输出缓存
#===============================================================================
import os
import datetime
import StringIO

class OutBuf(object):
	def __init__(self):
		self.buf = StringIO.StringIO()
	
	def __enter__(self):
		self.out = os.sys.stdout
		self.err = os.sys.stderr
		os.sys.stdout = self.buf
		os.sys.stderr = self.buf
		return self
	
	def __exit__(self, _type, _value, _traceback):
		os.sys.stdout = self.out
		os.sys.stderr = self.err
		# 要将异常继续抛出
		return False
	
	def get_value(self):
		return self.buf.getvalue()
	
	def pprint(self, s):
		self.out.write(s)

class OutBuf_NoExcept(object):
	def __init__(self):
		self.buf = StringIO.StringIO()
	
	def __enter__(self):
		self.out = os.sys.stdout
		self.err = os.sys.stderr
		os.sys.stdout = self.buf
		os.sys.stderr = self.buf
		return self
	
	def __exit__(self, _type, _value, _traceback):
		if _traceback:
			import traceback
			traceback.print_exc()
		os.sys.stdout = self.out
		os.sys.stderr = self.err
		# 不再抛出异常
		return True
	
	def get_value(self):
		return self.buf.getvalue()
	
	def pprint(self, s):
		self.out.write(s)

class OutLog_NoExcept():
	def __init__(self, file_path, lock = None):
		self.file_path = file_path
		self.lock = lock
	
	def write(self, s):
		if self.lock:
			with self.lock:
				with open(self.file_path, "a") as f:
					f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
					f.write(" : ")
					f.write(s)
		else:
			with open(self.file_path, "a") as f:
				f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				f.write(" : ")
				f.write(s)
	
	def __enter__(self):
		self.out = os.sys.stdout
		self.err = os.sys.stderr
		os.sys.stdout = self
		os.sys.stderr = self
		return self
	
	def __exit__(self, _type, _value, _traceback):
		if _traceback:
			import traceback
			traceback.print_exc()
		os.sys.stdout = self.out
		os.sys.stderr = self.err
		# 不再抛出异常
		return True
