# -*- coding: utf-8 -*-
import traceback
import me
def check(msg):
	Words=None
	if isinstance(msg,dict):
		Words=msg
	else:
		if isinstance(msg,unicode):
			msg=msg.encode("utf8")
		Word=me.review("words","heart")
		Words=Word.info.get(msg,None)
	if Words:
		msg=Words.get(me.S['A']['lang'],msg)
	return msg
		
	
