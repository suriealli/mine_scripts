
# -*- coding:utf-8 -*-


import os
import sys
import re
VERSION_CONFIG_FILE = 'english_configs.txt'

def check():
	print "[check(){}[]<>count] walk ..."
	file = open(VERSION_CONFIG_FILE, 'rb' )
	allText = file.read()
	arr = allText.split("\r\n");
	count = 0
	while count<len(arr):
	    lineArr = arr[count].split('\t')
	    if(len(lineArr) <2):
	        count = count + 1
	        continue
	    source_text = lineArr[0]
	    target_text = lineArr[1]
	    countA =  len([ele for ele in target_text if ele == '('])
	    countA2 =  len([ele for ele in target_text if ele == ')'])

	    countB =  len([ele for ele in target_text if ele == '['])
	    countB2 =  len([ele for ele in target_text if ele == ']'])

	    countC =  len([ele for ele in target_text if ele == '{'])
	    countC2 =  len([ele for ele in target_text if ele == '}'])

	    countD =  len([ele for ele in target_text if ele == '<'])
	    countD2 =  len([ele for ele in target_text if ele == '>'])
	    if countA != countA2:
	        print '%s%s%s>>> left  (   count:%s   right   )   count:%s'%("line",count+1 ," error",countA,countA2)		
	    if countB != countB2:
	        print '%s%s%s>>> left  [   count:%s   right   ]   count:%s'%("line",count+1 ," error",countB,countB2)		
	    if countC != countC2:
	        print '%s%s%s>>> left  {   count:%s   right   }   count:%s'%("line",count+1 ," error",countC,countC2)
	    if countD != countD2:
	        print '%s%s%s>>> left  <   count:%s   right   >   count:%s'%("line",count+1 ," error",countD,countD2)
	    count = count + 1
	print "check over"
	os.system('pause')

if __name__ == '__main__':
	check()
