
# -*- coding:utf-8 -*-


import os
import sys
import re


tempFile = 'initTemp.jsfl'
def check(path,language):
	newPath = path.replace("\\" ,"/")
	txt =" var path ='file:///" + newPath+"/';var fla = fl.openDocument( path + '"+language +".fla' );fla.exportSWF( path + '" + language+".swf', false );fla.exportSWF( path + 'config.swf', false );fl.closeDocument( fl.documents[0], false );"
	tfile = open(tempFile,'w')
	tfile.write(txt)
	tfile.flush()
	tfile.close()
if __name__ == '__main__':
	pwd = sys.path[0]
	language = ''
	if len(sys.argv) < 2:
		print 'param num error !!!'
		sys.exit()
	language = sys.argv[2]
	check(pwd,language)
