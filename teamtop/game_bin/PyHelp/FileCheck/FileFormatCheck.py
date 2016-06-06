#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("GS.Check")
#===============================================================================
# 检查"PyCode\Game"目录下所有文件的第三行是否规范  @author: Gaoshuai
#===============================================================================
import os.path

# 对不符合格式要求的文件计数
FILE_COUNT = 1
# 递归遍历目录下的所有文件
def FileFormatCheck(path):
	global FILE_COUNT
	for name_And_Suffix in os.listdir(path):
		if os.path.isdir(os.path.join(path,name_And_Suffix )):
			#如果当前路径是文件夹的话，向该目录递归调用
			FileFormatCheck(os.path.join(path, name_And_Suffix))
			continue
		if os.path.isfile(os.path.join(path,name_And_Suffix )):
			#如果当前目录是文件，并且是以.py结尾的，读取文件并判断
			file_Name, file_Suffix = os.path.splitext(name_And_Suffix)
			if file_Suffix != '.py':
				continue
			absPath = os.path.join(path,name_And_Suffix )
			newString = '# XRLAM("'+path[35:]+'.'+file_Name+'")\n'
			newString = newString.replace('\\','.')

			#打开文件并且只判断文件的第三行是否出错
			file_opened = open(absPath,'r')
			row = 1
			for line in file_opened:
				if row != 3 :
					row += 1
					continue
				if not line == newString:
					print "Find Error File, on the 3rd Line. Path %d : "%FILE_COUNT+newString[9:-3]+file_Suffix
					FILE_COUNT += 1
				break	
					
			file_opened.close()
				
	
if __name__ == "__main__":
	CurFloderPath = os.getcwd()
	# 获取当前路径
	# CurFloderPath == E:\LongQiShi\Develop\Server\PyHelp\FileCheck
	ServerFloderPath = CurFloderPath[:-17]
	check_dir = os.path.join(ServerFloderPath,"PyCode\\Game")
	# 需要检查的工作目录
	# check_dir = E:\LongQiShi\Develop\Server\PyCode\Game
	if os.path.exists(check_dir):
		FileFormatCheck(check_dir)
	else:
		print 'Wrong path Dir.'
	