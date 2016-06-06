#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 解析C++代码
#===============================================================================
import DynamicPath

def TripBreakCharacter(s, charTuple = ('\n', '\r')):
	'''
	按照传入的字符集cs的逆序，截取掉s的尾部
	@param s:源字符串
	@param charTuple:要删除的字符串
	'''
	for c in charTuple:
		if s.endswith(c):
			s = s[:-1]
	return s

def TripAllCharacter(s, charTuple = (' ', '\t')):
	'''
	去掉字符串前后的某些字符
	@param s:字符串
	@param charTuple:字符串前后忽视的char集合
	'''
	_begin = None
	_end = 0
	for _idx, _c in enumerate(s):
		if _c not in charTuple:
			if _begin is None:
				_begin = _idx
			_end = _idx
	if _begin is None:
		return ""
	else:
		return s[_begin:_end + 1]

def ParseComment(s):
	'''
	从一个字符串中解析出如代码部分和注释部分
	@param line:
	'''
	_pos = s.find(r"//")
	if _pos == -1:
		return s, ""
	else:
		return s[:_pos], s[_pos + 2:]

def ParseEqual(s):
	'''
	从一个字符串中解析出一个等式的左右两边的字符串
	@param s:
	'''
	_pos = s.find("=")
	if _pos == -1:
		return None, None
	_l = s[:_pos]
	_r = s[_pos + 1:]
	return _l, _r

def IsEnumBegin(line, enumName):
	'''
	是否是一个枚举的开始的一行
	@param line:一行字符串
	@param enumName:结构体名
	'''
	_code, _annota = ParseComment(line)
	_pe = _code.find("enum")
	_pn = _code.find(enumName)
	return _pn > _pe + 1 and _pe > -1

def IsBegin(line):
	'''
	是否是代码块开始了
	@param line:一行字符串
	'''
	_code, _annota = ParseComment(line)
	return  _code.find("{") != -1

def IsEnd(line):
	'''
	是否是代码块结束了
	@param line:一行字符串
	'''
	_code, _annota = ParseComment(line)
	return  _code.find("}") != -1

def ParseEnumInfo(line, lastValue):
	'''
	解析出一行C枚举代码的枚举信息
	@param line:字符串行
	@param lastValue:上次的枚举值
	@return:枚举名, 枚举值, 注释
	'''
	_code, _annota = ParseComment(line)
	_pos = _code.find(",")
	if _pos != -1:
		_code = _code[:_pos]
	_enumKey, _enumValue = ParseEqual(_code)
	if _enumKey:
		_enumKey = TripAllCharacter(_enumKey)
		_enumValue = int(TripAllCharacter(_enumValue))
	else:
		_enumKey = TripAllCharacter(_code)
		_enumValue = lastValue + 1
	return _enumKey, _enumValue, _annota


class CFile(object):
	def __init__(self, filePath):
		if filePath.find("CCode") == -1:
			filePath = DynamicPath.CFloderPath + filePath
		self.filePath = filePath
		self.__Read()
	
	def __Read(self):
		try:
			with open(self.filePath) as f:
				self.fileList = f.read().split('\n')
		except:
			self.fileList = []
			print "can't open file(%s)" % self.filePath
	
	def GetEnumerate(self, name):
		isEnum = False
		isBegin = False
		lastValue = -1
		ret = []
		for line in self.fileList:
			line = TripAllCharacter(line)
			if not line:
				continue
			if IsEnumBegin(line, name):
				isEnum = True
				continue
			if not isEnum:
				continue
			if IsBegin(line):
				isBegin = True
				continue
			if not isBegin:
				continue
			if IsEnd(line):
				return ret
			
			key, value, annoto = ParseEnumInfo(line, lastValue)
			if key:
				lastValue = value
				ret.append((key, value, annoto))
		return ret


