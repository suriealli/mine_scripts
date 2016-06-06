#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)
#===============================================================================
# 文件检查
#===============================================================================
import md5
import Environment
import DynamicPath

def SpliteFilePath(filePath):
	pos = filePath.rfind(".")
	if pos == -1:
		return filePath, ""
	else:
		return filePath[:pos], filePath[pos + 1:]

def GetAllFilePathList(fileRoot, extList = []):
	# 修正路径
	if fileRoot.endswith(os.sep):
		fileRoot = fileRoot[:-1]
	# 修正后缀
	extList = set(extList)
	filePathList = []
	
	for dirpath, _, filenames in os.walk(fileRoot):
		for fi in filenames:
			filePath = dirpath + os.sep + fi
			_, ext = SpliteFilePath(filePath)
			if ext.lower() in extList:
				filePathList.append(filePath[len(fileRoot):])
	return filePathList

def CheckCCode():
	filePathList = GetAllFilePathList(DynamicPath.CFloderPath, ["h", "cpp"])
	for filePath in filePathList:
		rewrite = 0
		with open(DynamicPath.CFloderPath + filePath) as f:
			fileList = f.read().split('\n')
			if fileList[-1]:
				rewrite = 2
			elif fileList[-2]:
				rewrite = 1
			if rewrite:
				for _ in xrange(rewrite):
					fileList.append("")
				print "--> Fix", filePath
		if not rewrite: continue
		with open(DynamicPath.CFloderPath + filePath, "w") as f:
			f.write("\n".join(fileList))
			f.flush()

def GetPyCodeMD5():
	filePathList = GetAllFilePathList(DynamicPath.PyFloderPath, ["py"])
	# Window和Linux上文件路径排序不一样，这里要强行做成一样
	filePathList.sort(key=lambda it:it.replace(os.sep, "."))
	m = md5.new()
	for filePath in filePathList:
		f = open(DynamicPath.PyFloderPath + filePath, "rb")
		m.update(f.read())
		f.close()
		#print filePath, m.hexdigest()
	return str(m.hexdigest())

def GetConfigMD5():
	filePathList = GetAllFilePathList(DynamicPath.ServerFloderPath + "Config" + os.sep, ["py"])
	# Window和Linux上文件路径排序不一样，这里要强行做成一样
	filePathList.sort(key=lambda it:it.replace(os.sep, "."))
	m = md5.new()
	for filePath in filePathList:
		f = open(DynamicPath.ServerFloderPath + "Config" + os.sep + filePath, "rb")
		m.update(f.read())
		f.close()
		#print filePath, m.hexdigest()
	return str(m.hexdigest())

def GetBinMD5():
	m = md5.new()
	if Environment.IsWindows:
		return "nomd5"
	f = open(DynamicPath.BinPath + "ComplexServer")
	m.update(f.read())
	f.close()
	return str(m.hexdigest())

def ReadMD5(fileName):
	with open(DynamicPath.BinPath + fileName) as f:
		pycode = f.readline()[:32]
		config = f.readline()[:32]
		exe = f.readline()[:32]
		return pycode, config, exe

def WriteWinMD5():
	with open(DynamicPath.BinPath + "WIN.txt", "w") as f:
		f.write(GetPyCodeMD5())
		f.write("\n")
		f.write(GetConfigMD5())
		f.write("\n")
		f.write(GetBinMD5())
		f.write("\n")

def CheckVersionMachine():
	pycode, config, _ = ReadMD5("WIN.txt")
	my_pycode = GetPyCodeMD5()
	my_config = GetConfigMD5()
	# 断言MD5一样
	#print pycode, type(pycode), len(pycode)
	#print my_pycode, type(my_pycode), len(my_pycode)
	#print
	#print config, type(config), len(config)
	#print my_config, type(my_config), len(my_config)
	#print
	assert pycode == my_pycode
	assert config == my_config
	WriteVersionMD5(my_pycode, my_config, GetBinMD5())

def WriteVersionMD5(pycode, config, exe):
	with open(DynamicPath.BinPath + "LINUX.txt", "w") as f:
		f.write(pycode)
		f.write("\n")
		f.write(config)
		f.write("\n")
		f.write(exe)
		f.write("\n")

def CheckWorkMachine():
	pycode, config, exe = ReadMD5("LINUX.txt")
	return GetPyCodeMD5() == pycode, GetConfigMD5() == config, GetBinMD5() == exe

if __name__ == "__main__":
	if Environment.IsWindows:
		CheckCCode()
		WriteWinMD5()
	else:
		CheckVersionMachine()

