#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.File.TabFile")
#===============================================================================
# 读取tab为分隔符的配置文件
#===============================================================================
import os
import sys
import cPickle
import datetime
import Environment

# Win的UTF8的BOM字节
UTF8_BOM = chr(239) + chr(187) + chr(191)


if "_HasLoad" not in dir():
	LanguageConfig = {}

def InitLanguageTranslateConfig(lcd):
	global LanguageConfig
	LanguageConfig = lcd


def Strip(s):
	'''
	去掉换行符
	@param s:字符串
	'''
	if s.endswith("\r\n"):
		return s[:-2]
	if s.endswith("\n"):
		return s[:-1]
	return s

class Obj(object):
	'''
	一个字典
	'''
	def __str__(self):
		for k, v in self.__dict__.iteritems():
			print k, v
	
class TabLine(object):
	FilePath = None
	#UseCache = Environment.IsWindows
	UseCache = False
	@classmethod
	def ToClassType(cls, checkLogic = True):
		if cls.FilePath is None:
			print "GE_EXC, cls(%s) has not file path." % (cls.__name__)
			return []
		return TabFile(cls.FilePath, checkLogic).ToClassType(cls)
	
	def GetAllProperty(self):
		'''
		返回回一个字典
		这个字典保存了模板实例中的属性对应的函数引用
		'''
		propertyDict = {}
		classPropertys = set(dir(self.__class__))
		for name in dir(self):
			# 如果这个字段名是属于类对象的，忽视之
			if name in classPropertys:
				continue
			propertyDict[name] = getattr(self, name)
		return propertyDict
	
	def GetCodeByString(self, s):
		return compile(s, "<string>", "eval")
	
	def GetBoolByString(self, s):
		if s:
			if eval(s):
				return True
			else:
				return False
		else:
			return False
	
	def GetIntByString(self, s):
		'''
		根据配置表中的字段，获取整数（没填就是0）
		'''
		if s:
			return int(s)
		else:
			return 0
	
	def GetEvalByString(self, s):
		'''
		根据配置表中的字段，获取对象（没填就是None）
		'''
		if s:
			return eval(s)
		else:
			return None
	
	def GetFunctionByString(self, s):
		'''
		根据配置表填写的("模块名", "函数名")，获取函数对象
		@param s:字段字符串
		'''
		#由于模块的导入和一些多语言版本的原因，这个已经禁止使用了
		assert False
		# 如果没有填写，则忽视之
		if not s:
			return None
		moduleName, functionName = eval(s)
		__import__(moduleName)
		return getattr(sys.modules[moduleName], functionName)
	
	def GetDatetimeByString(self, s):
		'''
		根据配置表填写的(年,月,日,[时,[分,[秒]]])，日期时间
		@param s:字段字符串
		'''
		if not s:
			return datetime.datetime(2038, 1, 1)
		return datetime.datetime(*eval(s))
	
	def GetTimeByString(self, s):
		'''
		根据配置表填写的(时,分,秒)，时间
		@param s:字段字符串
		'''
		if not s:
			return datetime.time(0, 0, 0)
		return datetime.time(*eval(s))
	
	def GetI1Index(self, s):
		'''
		根据配置表填写的变量名，获取I1数组对应的值
		@param s:
		'''
		if not s:
			return 0
		from Game.Role.Data import EnumInt1
		return getattr(EnumInt1, s)
	
	def GetCDIndex(self, s):
		'''
		根据配置表填写的变量名，获取CD数组对应的值
		@param s:
		'''
		if not s:
			return 0
		from Game.Role.Data import EnumCD
		return getattr(EnumCD, s)
	
	def GetPropertyIndex(self, s):
		'''
		根据配置表填写的变量名，获取属性枚举数组对应的值
		@param s:
		'''
		if not s:
			return 0
		from Game.Property import PropertyEnum
		return getattr(PropertyEnum, s)
	
	def GetDI64Index(self, s):
		'''
		根据配置表填写的变量名，获取角色DI64数组对应的值
		@param s:
		'''
		if not s:
			return 0
		from Game.Role.Data import EnumDynamicInt64
		return getattr(EnumDynamicInt64, s)
	
	def __str__(self):
		'''
		格式化打印的信息
		'''
		return ", ".join(["%s(%s)" % (name, getattr(self, name)) for name in self.GetAllProperty().iterkeys()])

class TabFile(object):
	CacheCnt = 0
	UncacheCnt = 0
	def __init__(self, filePath, checkLogic = True):
		self.filePath = filePath
		self.checkLogic = checkLogic
		
		self.hasExcept = False
	
	@staticmethod
	def __StringToList(s):
		return Strip(s).split('\t')
	
	def __ReadEnName(self, f):
		'''
		读取配子表的每列的英文名
		@param f:文件对象
		'''
		enLine = f.readline()
		if enLine.startswith(UTF8_BOM):
			enLine = enLine[3:]
		self.enNameList = self.__StringToList(enLine)
		assert len(set(self.enNameList)) == len(self.enNameList)
	
	def __CheckWithEnName(self, idx, row):
		'''
		检测一行数据是否和英文列名匹配
		@param idx:行索引
		@param row:行数据
		'''
		if len(row) == len(self.enNameList):
			return True
		print "GE_EXC, line(%s) not match enName (%s)" % (idx, self.filePath)
		for idx in xrange(max(len(self.enNameList), len(row))):
			if idx < len(self.enNameList):
				print self.enNameList[idx],
			else:
				print None,
			print " -- ",
			if idx < len(row):
				print row[idx]
			else:
				print None
		return False
	
	def __ReadZhName(self, f):
		'''
		读取配子表的每列的中文名
		并且检测匹配问题
		@param f:文件对象
		'''
		self.zhNameList = self.__StringToList(f.readline())
		self.__CheckWithEnName(0, self.zhNameList)
	
	def __ReadData(self, f):
		'''
		读取配置表数据
		并且检测匹配问题
		@param f:文件对象
		'''
		for idx, line in enumerate(f):
			# 空行，忽视之
			if not line:
				continue
			row = self.__StringToList(line)
			if self.__CheckWithEnName(idx, row):
				self.dataList.append(row)
			else:
				continue
	
	def __TranslateByLanguage(self):
		#不读取自己
		if self.filePath.find("language") >= 0:
			return 
		global LanguageConfig
		if not LanguageConfig:
			#尝试读取？
			return
		
		#用译文替换原文
		for row in self.dataList:
			for index, value in enumerate(row):
				translateValue = LanguageConfig.get(value)
				if not translateValue:
					continue
				row[index] = translateValue

	def PrintFilePath(self):
		if self.hasPrint:
			return
		print "GE_EXC, %s" % self.filePath
		self.hasPrint = True
	
	def ToClassType(self, classType):
		'''
		按照模板信息，将每行读成一个列表
		@param classType:类对象
		'''
		# Windows环境，尝试使用缓存
		if classType.UseCache:
			# 如果能使用缓存，则直接缓存读取之
			if self.__CanUseCashe(classType):
				TabFile.CacheCnt += 1
				with open(self.cachePath + "d", "rb") as f:
					return cPickle.load(f)
			# 否则先正常读取配置文件，并缓存之
			else:
				TabFile.UncacheCnt += 1
				result = self.__ToClassType_Normal(classType)
				if self.hasExcept is True:
					#有异常，不缓存文件
					return result
				with open(self.cachePath + "c", "wb") as f:
					#保存配置类的类型
					cPickle.dump(classType, f, cPickle.HIGHEST_PROTOCOL)
				with open(self.cachePath + "mb", "wb") as f:
					#序列化类成员列表
					cPickle.dump(classType().__dict__.keys(), f, cPickle.HIGHEST_PROTOCOL)
				with open(self.cachePath + "d", "wb") as f:
					#序列化配置表内容
					cPickle.dump(result, f, cPickle.HIGHEST_PROTOCOL)
				return result
		else:
			return self.__ToClassType_Normal(classType)
		
		# Windows环境下，尝试使用缓存
		l = self.__ToClassType_Cashe(classType)
		if l is not None:
			return l
		else:
			return self.__ToClassType_Normal(classType)
	
	def __CanUseCashe(self, classType):
		self.cachePath = self.filePath[:self.filePath.find("Config")] + "File" + self.filePath[self.filePath.rfind(os.sep):]
		# class文件必须存在
		if not os.path.isfile(self.cachePath + "c"):
			return False
		# classType必须一样
		with open(self.cachePath + "c", "rb") as f:
			if f.read() != cPickle.dumps(classType, cPickle.HIGHEST_PROTOCOL):
				return False
		# classType成员变量必须一样
		if not os.path.isfile(self.cachePath + "mb"):
			return False
		# classType成员变量和序列化的类成员变量必须一样
		with open(self.cachePath + "mb", "rb") as f:
			if f.read() != cPickle.dumps(classType().__dict__.keys(), cPickle.HIGHEST_PROTOCOL):
				return False
		
		# 缓存文件和原文件必须都存在
		if not os.path.isfile(self.filePath):
			return False
		if not os.path.isfile(self.cachePath + "d"):
			return False
		# 缓存文件必须比原文件新
		tstat = os.stat(self.filePath)
		dstat = os.stat(self.cachePath + "d")
		if tstat.st_mtime >= dstat.st_mtime:
			return False
		return True
	
	def Read(self):
		# 初始化
		self.dataList = []
		self.hasPrint = False
		# 检测读取权限
		if self.checkLogic and (not Environment.HasLogic):
			print "GE_EXC, read file(%s) without logic" % self.filePath
		
		#检测有没有翻译文件
		if Environment.Language and Environment.Language != "default":
			SF = self.filePath
			find_filepath = SF[:SF.rfind(".")] + "_" + Environment.Language + SF[SF.rfind("."):]
			if os.path.isfile(find_filepath):
				#替换成这个语言版本的配置表
				self.filePath = find_filepath
				print "BLUE, change config txt ", self.filePath[SF.rfind(os.sep):]

		# 读取文件
		with open(self.filePath, 'r') as f:
			self.__ReadEnName(f)
			self.__ReadZhName(f)
			self.__ReadData(f)
			self.__TranslateByLanguage()
	
	def __ToClassType_Normal(self, classType):
		self.Read()
		# 构建读取数据
		obj = classType()
		propertyDict = obj.GetAllProperty()
		# 检测属性和英文名是否匹配
		if not (set(propertyDict.iterkeys()) <= set(self.enNameList)):
			self.PrintFilePath()
			for k in propertyDict.iterkeys():
				if k in self.enNameList:
					continue
				print "GE_EXC, not match property(%s)" % k
			return []
		# 构建属性对应的列
		for idx, enName in enumerate(self.enNameList):
			if enName not in propertyDict:
				continue
			propertyDict[enName] = (propertyDict[enName], idx)
		# 构建结果集
		rowList = []
		self.hasExcept = False
		for rowIdx, row in enumerate(self.dataList):
			# 为该行构建个对象
			obj = classType()
			# 对于每一个属性，从配置表中读取并转化之
			isExcept = False
			for name, value in propertyDict.iteritems():
				fun, idx = value
				try:
					setattr(obj, name, fun(row[idx]))
				except:
					self.PrintFilePath()
					print "GE_EXC, file (%s) line(%s) cell(%s) column(%s), value(%s) can't call by function(%s)" % (self.filePath, rowIdx + 3, idx, name, type(row[idx]), fun.__name__)
					isExcept = True
					self.hasExcept = True
			if isExcept is True:
				continue
			rowList.append(obj)
		return rowList
	
	def ReverseTemplate(self):
		'''
		根据配子表反向生成模板
		'''
		print '''class Template(TabFile.TabLine):'''
		print '''	def __init__(self):'''
		for idx in xrange(len(self.enNameList)):
			print "		self.%s = str			#%s"%(self.enNameList[idx], self.zhNameList[idx])

