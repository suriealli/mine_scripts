#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# checkout一个最新的不带客户端资源的分支
#===============================================================================
import os

def auto_checkout(env):
	tag_name_file = os.sep.join([os.path.splitdrive(os.getcwd())[0], 'tag_name_list_file.txt'])
	
	os.system('svn list https://192.168.8.208/svn/LongQiShi/tags > %s' % tag_name_file)
	
	#获取最新的分支名字(有先后顺序的， 只需要获取最后一个名字)
	with open(tag_name_file) as t:
		tag_name = None
		while 1:
			line = t.readline()
			if not line:
				break
			if not line.startswith(env):
				continue
			tag_name = line
	
	url = 'https://192.168.8.208/svn/LongQiShi/tags' + '/' + tag_name
	
	tag_name = os.sep.join([os.path.splitdrive(os.getcwd())[0], tag_name[:-2]])
	#分支存在
	if os.path.exists(tag_name):
		return
	
	#写个bat来切换目录check
	check_bat_file = os.sep.join([os.path.splitdrive(os.getcwd())[0], 'check_bat_file.bat'])
	with open(check_bat_file, 'w') as c:
		c.write('cd \\\nsvn co --depth empty %s\nsvn up %s\Config\nsvn up %s\Server\n' % (url, tag_name, tag_name))
	os.system(check_bat_file)
	
	os.remove(tag_name_file)
	os.remove(check_bat_file)

if __name__ == '__main__':
	#qq、na、rumsk、tk、tw
	auto_checkout('tk')
	
