# -*- coding:UTF-8 -*-
# XRLAM("ZYX.BuildRequest")
#===============================================================================
# 注释
#===============================================================================
import Game.StarGirl.StarGirlMgr as m

if "_HasLoad" not in dir():
	pass

def info(obj, collapse = 1):
	'''
	
	@param obj:
	@param collapse:
	'''
	"""Print methods and doc strings.
	
	Takes module, class, list, dictionary, or string."""
	methodList = [method for method in dir(obj) if callable(getattr(obj, method))]
	processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
	for method in methodList:
		if method.startswith("Request"):
			print "import %s as m" % m.__name__
			print "m." + method + "(role, None)"
			doc = processFunc(str(getattr(obj, method).__doc__))
			doc = doc[:doc.find('@')]
			print "#%s\n" % doc
			
if __name__ == '__main__':
	info(m)
	