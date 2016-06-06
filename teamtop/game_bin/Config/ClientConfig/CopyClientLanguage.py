
# -*- coding:utf-8 -*-


import os
import sys
import re

realname_map = {}
realname_mapII = {}
tempFile = 'warnFile.txt'
def check(language):
	count = 0;
	newObj = {};
	warnObj = {};
	with open( "language.txt", 'r' ) as version_file:
		first_line = True
		for one in version_file:
			if(count<2):
				count += 1
				continue
			id, desc = one[0:(len(one)-1)].split( '\t' )
			realname_map[id] = desc
	count = 0;
	with open( language, 'r' ) as version_file:
		first_line = True
		for one in version_file:
			#print one
			if(count<2):
				count += 1
				continue
			id, desc,descII = one[0:(len(one)-1)].split( '\t' )
			realname_mapII[id] = desc
	for key in realname_map:
		if(key in realname_mapII):
			value = realname_mapII[key]
			if(value != realname_map[key]):
				warnObj[key] = [realname_map[key],value];
		else:
			newObj[key] = realname_map[key];
	print "print warning language and save in tempFile.txt, you need to open it in notepad++ and check in each xlsm!"
	tfile = open(tempFile,'w')
	for key in warnObj:
		tfile.write( '%s\t%s\t%s\n' % (key,warnObj[key][0],warnObj[key][1]) )
	tfile.flush()
	tfile.close()
	print "Add new line form chineLanguage to otherLanguage!"
	nfile = open(language,"a")
	for key in newObj:
		nfile.write( '%s\t%s\t%s\n' % (key,newObj[key],"") )
	nfile.flush()
	nfile.close()
	print "success"

if __name__ == '__main__':
	language = ''
	if len(sys.argv) < 2:
		print 'param num error !!!'
		sys.exit()
	language = sys.argv[2]
	check(language)
