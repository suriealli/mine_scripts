#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.Profile")
#===============================================================================
# Python函数分析
#===============================================================================
import os
import sys
import datetime
import cProfile
import pstats
import DynamicPath
import traceback

DumpFolder = DynamicPath.DynamicFolder(DynamicPath.FilePath)
DumpFolder.AppendPath("Profile")

if "_HasLoad" not in dir():
	PF = cProfile.Profile()
	FunctionNames = set()
	ModuleNames = set()

def StratProfile():
	PF.enable()

def EndProfile():
	PF.clear()
	PF.disable()

def DumpProfile(fileName = None):
	if not fileName:
		now = datetime.datetime.now()
		fileName = "PD_%s_%s_%s_%s_%s_%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
	PF.dump_stats(DumpFolder.FilePath(fileName))
	return fileName

def ShowProfile(fileName):
	PS = pstats.Stats(DumpFolder.FilePath(fileName))
	PS.strip_dirs()
	PS.sort_stats(2)
	PS.print_stats(.3)

class RedirectIO(object):
	def __init__(self, fileName):
		self.filename = DumpFolder.FilePath(fileName)

	def write(self, s):
		with open(self.filename, 'a') as f:
			f.write(s)

def DumpStats(profileName, outFileName = None, sortType = 1, cnt = 100):
	'''
	#分析，写入文件
	@param profileName:
	@param outFileName:
	@param sortType: -1,0,1,2  对应”stdname”, “calls”, “time”和”cumulative”
	'''
	if outFileName is None:
		outFileName = profileName + "_out"
	#重定向IO
	myiotest = RedirectIO(outFileName)
	temp = sys.stdout
	try:
		sys.stdout = myiotest
		PS = pstats.Stats(DumpFolder.FilePath(profileName))
		PS.strip_dirs()
		PS.sort_stats(sortType)
		PS.print_stats(cnt)
		
		sys.stdout = temp
	except:
		sys.stdout = temp
		traceback.print_exc()
		


def DumpAndShowProfile(fileName = None):
	fileName = DumpProfile(fileName)
	ShowProfile(fileName)

def __OnReturn(frame, event, arg):
	if event != "return":
		return
	functionName = frame.f_code.co_name
	fp = frame.f_code.co_filename
	pos = fp.find("PyCode")
	if pos != -1:
		fp = fp[pos + 7:]
	pos = fp.find(".")
	if pos != -1:
		fp = fp[:pos]
	moduleName = fp.replace(os.sep, ".")
	if functionName in FunctionNames or moduleName in ModuleNames:
		print "BLUE %s %s %s %s" % (moduleName, functionName, frame.f_lineno, str(arg))

def ShowReturn(name):
	if name.find(".") == -1:
		FunctionNames.add(name)
	else:
		ModuleNames.add(name)
	sys.setprofile(__OnReturn)

def ClearReturn():
	FunctionNames.clear()
	ModuleNames.clear()
	sys.setprofile(None)

if __name__ == "__main__":
	ShowProfile("init")
	
