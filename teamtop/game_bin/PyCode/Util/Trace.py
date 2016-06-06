#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 警告
#===============================================================================
import inspect

def StackWarn(warn = ""):
	print "Traceback(show stack):"
	framelist = inspect.stack()
	for idx in xrange(len(framelist) - 1, 0, -1):
		frame = framelist[idx]
		print '  File "%s", line %s, in %s' % (frame[1], frame[2], frame[3])
		source =  frame[4]
		if source:
			source = source[0]
			for start in xrange(len(source)):
				if source[start] != '\t' and source[start] != ' ':
					source = source[start:]
					break
			print '    %s' % source,
	print "StackError:%s" % warn

