#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("World.Language")
#===============================================================================
# 语言包
#===============================================================================
import sys
import os
#======================================================
#添加import路径使Language文件可以在Eclipse以外执行
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)
#======================================================
import string
import DynamicPath
from Util.PY import Load
from Util.File import TabFile

#不需要翻译的模块
ExtendModuleVariable = set(["ComplexServer.Log.AutoLog.Events", "ComplexServer.Log.AutoLog.Transactions",
						"ComplexServer.Statistics.StatisticsDict"])
#把换行个制表符替换掉
replace_dict = {"\n" : "#2014#", "\t" : "#2015#"}
#忽视不需要翻译的文件夹
IgnoreFloder = ["language", "MapConfig", "GongGaoConfig"]
#忽视的txt文件
IgnoreTxt = ["AutoTransaction.txt", "AutoMessage.txt", "GameZoneName.txt", "language.txt"]
#忽视的文件夹第一层txt
IgnoreFloderTxt = ["ClientConfig"]

#Win的UTF8的BOM字节
UTF8_BOM = chr(239) + chr(187) + chr(191)
#特殊字符
spe = "·’『』，→“”-–?…！：（）×；【】+？ș♂～①"

Englist = set(string.printable)
for c in spe:
	Englist.add(c)

def all_english(s):
	#这个字符串是否是全英文
	for c in s:
		if c in Englist : continue
		return False
	return True

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


def CountS(textold, translate):
	#检测翻译前后是否对应上 '%s'个数
	return textold.count('%s') == translate.count('%s')



#脚本语言包配置
class LanguageScript(TabFile.TabLine):
	def __init__(self):
		self.module_variable_name = str
		self.source_text = str
		self.target_text = str
		self.need_translate = int

	@classmethod
	def ToClassType(cls, filepath, checkLogic = True):
		return TabFile.TabFile(filepath, checkLogic).ToClassType(cls)

class LanguageConfig(TabFile.TabLine):
	def __init__(self):
		self.source_text = str
		self.target_text = str
		self.need_translate = int

	@classmethod
	def ToClassType(cls, filepath, checkLogic = True):
		return TabFile.TabFile(filepath, checkLogic).ToClassType(cls)

def LoadLanguageConfig(languagePath):
	#读取旧的配置表语言包
	l_dict = {}
	for la in LanguageConfig.ToClassType(languagePath, False):
		l_dict[la.source_text] = la.target_text
		if not la.need_translate and "no need to translate" not in la.target_text:
			if CountS(la.source_text, la.target_text) is False:
				print "GE_EXC , LoadLanguageConfig CountS ", la.source_text, la.target_text
	return l_dict


def LoadLanguageScript(languagePath):
	#读取旧的脚本语言包
	l_dict = {}
	for la in LanguageScript.ToClassType(languagePath, False):
		l_dict[la.module_variable_name] = (la.source_text, la.target_text)
		if not la.need_translate and "no need to translate" not in la.target_text:
			if CountS(la.source_text, la.target_text) is False:
				print "GE_EXC , LoadLanguageScript CountS ", la.module_variable_name
	return l_dict


###############################################################################
def LoadLanguageConfigEX(language):
	#读取语言包的配置(等待服务器启动后替换掉配置表中的原文为译文)
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("language")
	languageFilePath = FilePath.FilePath("%s_configs.txt" % language)
	TabFile.InitLanguageTranslateConfig(LoadLanguageConfig(languageFilePath))



def LoadLanguageScriptEx(language):
	#读取和替换脚本里面的原文为译文
	cnt = 0
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("language")
	languageFilePath = FilePath.FilePath("%s_script.txt" % language)
	Script_Translate_Dict = LoadLanguageScript(languageFilePath)
	SG = Script_Translate_Dict.get
	for module in load_module():
		for name in dir(module):
			key = "%s.%s" % (module.__name__, name)
			if key in ExtendModuleVariable:
				continue
			can_print = True#控制下面的循环不要打印太多的东西
			value = getattr(module, name)
			# 如果是字符串，则检测是否全英文
			if isinstance(value, str):
				if not all_english(value):
					translate_tuple = SG(key)
					if not translate_tuple:
						cnt += 1
						#print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
						continue
					_, translate = translate_tuple
					if not translate:
						cnt += 1
						continue
					if CountS(value, translate) is False:
						#print "GE_EXC, module(%s), variable(%s)  translate error." % (module.__name__, name)
						cnt += 1
					else:
						#替换成译文
						setattr(module, name, translate)
			# 额外检测容器中是否有中文
			elif isinstance(value, (tuple, list, set)):
				for s in value:
					if isinstance(s, str):
						if can_print and (not all_english(s)):
							can_print = False
							print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
			elif isinstance(value, dict):
				for k, v in value.iteritems():
					if isinstance(k, str):
						if can_print and (not all_english(k)):
							can_print = False
							print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
					if isinstance(v, str):
						if can_print and (not all_english(v)):
							can_print = False
							print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
	
	if cnt > 0:
		print "GE_EXC LoadLanguageScriptEx error cnt (%s)" % cnt
	else:
		print "GREEN, LanguageScript is Ok"


###############################################################################


#特殊的读取配置表
class ConfigTable(object):
	def __init__(self, filePath):
		self.filePath = filePath
		self.Read()
	
	def Read(self):
		# 初始化
		self.dataList = []
		self.hasPrint = False
		# 读取文件
		with open(self.filePath, 'r') as f:
			self.__ReadEnName(f)
			self.__ReadZhName(f)
			self.__ReadData(f)
	
	@staticmethod
	def __StringToList(s):
		return Strip(s).split('\t')
	
	def __CheckWithEnName(self, idx, row):
		if len(row) == len(self.enNameList):
			return True
		print "GE_EXC, line(%s) not match enName (%s)" % (idx, self.filePath)
		for idx in xrange(max(len(self.enNameList), len(row))):
			if idx < len(self.enNameList):
				print self.enNameList[idx],
			else:
				print None
			if idx < len(row):
				print row[idx]
			else:
				print None
		return False
	
	def __ReadEnName(self, f):
		enLine = f.readline()
		if enLine.startswith(UTF8_BOM):
			enLine = enLine[3:]
		self.enNameList = self.__StringToList(enLine)
		if not len(set(self.enNameList)) == len(self.enNameList):
			print self.filePath
		assert len(set(self.enNameList)) == len(self.enNameList)
	
	def __ReadZhName(self, f):
		self.zhNameList = self.__StringToList(f.readline())
		self.__CheckWithEnName(0, self.zhNameList)
	
	def __ReadData(self, f):
		for idx, line in enumerate(f):
			if not line : continue # 空行，忽视之
			row = self.__StringToList(line)
			if self.__CheckWithEnName(idx, row):
				self.dataList.append(row)
			else : continue



def load_module():
	for module in Load.LoadPartModule("Common"):
		yield module
	for module in Load.LoadPartModule("ComplexServer"):
		yield module
	for module in Load.LoadPartModule("Control"):
		yield module
	for module in Load.LoadPartModule("DB"):
		yield module
	for module in Load.LoadPartModule("Game"):
		yield module
	for module in Load.LoadPartModule("World"):
		yield module


def Build_Language_Script(language):
	#构建脚本语言包
	scripts = {}
	for module in load_module():
		for name in dir(module):
			key = "%s.%s" % (module.__name__, name)
			if key in ExtendModuleVariable:
				continue
			can_print = True#控制下面的循环不要打印太多的东西
			value = getattr(module, name)
			# 如果是字符串，则检测是否全英文
			if isinstance(value, str):
				if not all_english(value):
					scripts[key] = value
			# 额外检测容器中是否有中文
			elif isinstance(value, (tuple, list, set)):
				for s in value:
					if isinstance(s, str):
						if can_print and (not all_english(s)):
							can_print = False
							print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
			elif isinstance(value, dict):
				for k, v in value.iteritems():
					if isinstance(k, str):
						if can_print and (not all_english(k)):
							can_print = False
							print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
					if isinstance(v, str):
						if can_print and (not all_english(v)):
							can_print = False
							print "GE_EXC, module(%s), variable(%s) has not all translate." % (module.__name__, name)
	#脚本路径
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("language")

	languageFilePath = FilePath.FilePath("%s_script.txt" % language)
	old_la_dict = LoadLanguageScript(languageFilePath)
	#module_variable_name	source_text	target_text	need_translate
	#模块名和变量名	原文	译文	是否需要重新翻译
	with open(languageFilePath, "wb") as f:
		f.write("module_variable_name\tsource_text\ttarget_text\tneed_translate\r\n模块名和变量名\t原文\t译文\t是否需要重新翻译\r\n")
		key_value = scripts.items()
		key_value.sort(key=lambda it:it[0])
		need_translate = []
		#第一步，写入不用重新翻译的内容
		for key, value in key_value:
			oldValue = old_la_dict.get(key)
			if oldValue:
				if value == oldValue[0] and oldValue[1]:
					#原文一样，并且有译文， 不需要翻译
					f.write("%s\t%s\t%s\t%s\r\n" % (key, value, oldValue[1], 0))
					continue
				
				
				#原文不一样，重新翻译
				need_translate.append((key, (value, oldValue[1])))
				continue
			# 新的内容，翻译
			need_translate.append((key, (value, "")))
		
		#第二步，写入旧的内容(已经废弃的内容)
		key_value = old_la_dict.items()
		key_value.sort(key=lambda it:it[0])
		for key, value in key_value:
			if key in scripts:
				continue
			f.write("%s\t%s\t%s\t%s\r\n" % (key, value[0], value[1], -1))
		
		#第三部，写入需要重新翻译或者新的原文
		for key, value in need_translate:
			f.write("%s\t%s\t%s\t%s\r\n" % (key, value[0], value[1], 1))
		
		print "Succeed srcipt len", len(scripts)


def Build_Language_Configs(language):
	#构建配置表语言包
	#记得SVN UPDATA
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("language")
	languageFilePath = FilePath.FilePath("%s_configs.txt" % language)
	old_la_dict = LoadLanguageConfig(languageFilePath)
	global configs
	configs = set()
	global NowLanguage
	NowLanguage = language
	LoadAllConfigs(DynamicPath.ConfigPath)
	
	with open(languageFilePath, "wb") as f:
		f.write("source_text\ttarget_text\tneed_translate\r\n原文\t译文\t是否需要重新翻译\r\n")
		configs = list(configs)
		configs.sort()
		hasWrite = set()
		for c in configs:
			oldtext = old_la_dict.get(c)
			if oldtext:
				f.write("%s\t%s\t%s\r\n" % (c, oldtext, 0))
				hasWrite.add(c)
			else:
				if c.startswith("     "):
					c_1 = c[5:]
					oldtext = old_la_dict.get(c_1)
					if oldtext:
						oldtext_1 = "     " + oldtext
						f.write("%s\t%s\t%s\r\n" % (c, oldtext_1, 0))
						hasWrite.add(c)
		
		for c, oldtext in old_la_dict.iteritems():
			if c in hasWrite:
				continue
			if oldtext:
				#已经翻译过，但是不删除
				f.write("%s\t%s\t%s\r\n" % (c, oldtext, 0))
		
		for c in configs:
			if c in hasWrite:
				continue
			#if c not in old_la_dict:
			s = "%s\t%s\t%s\r\n" % (c, "", 1)
			f.write(s)

	print "Succeed configs len", len(configs)



def LoadAllConfigs(path, onlyFloder = False):
	plist = os.listdir(path)
	for n in plist:
		if n[-4:] == '.txt':
			if onlyFloder is True or n in IgnoreTxt :
				#忽视的txt
				continue
			FindNeedTranslate(path + os.sep + n, n)
		elif '.' not in n:
			if n in IgnoreFloder:
				continue
			#文件夹，继续遍历
			newp = path + os.sep + n
			if n in IgnoreFloderTxt:
				LoadAllConfigs(newp, True)
			else:
				LoadAllConfigs(newp)

def IsDefaultTXT(realtxt):
	global NowLanguage, AllLanguages
	for al in AllLanguages:
		if al.startswith(NowLanguage):
			continue
		salts = '_' + al +'.txt'
		if salts in realtxt:
			return False
	return True


def FindNeedTranslate(txtPath, txt):
	if not IsDefaultTXT(txt):
		return
	global configs
	ct = ConfigTable(txtPath)
	for row in ct.dataList:
		for value in row:
			if not value:
				continue 
			if not isinstance(value, str):
				continue
			if not all_english(value):
				if value.startswith("#备注#"):
					continue
				if "С 16 по 20 июля в качестве" in value:
					print "txtPath", txtPath
				configs.add(value)



if __name__ == "__main__":
	#所有的语言版本，新的语言版本需要添加一个，作为导出翻译的忽视txt
	AllLanguages = ["english", "ft", "rumsk", "tk", "pl", "fr","en","ger", "esp"]
	Build_Language_Script("ger")
	Build_Language_Configs("ger")
	print "Build_Language OK ！"


