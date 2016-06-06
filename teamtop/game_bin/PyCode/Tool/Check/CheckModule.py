#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 检测脚本
# 1 检测脚本的XRLAM部分是否正确
# 2 检测脚本是否在reload的时候使用自己的逻辑
#===============================================================================
def CheckModule():
	from Util.PY import Load, PyParseBuild
	for module in Load.LoadPartModuleEx("Game"):
		po = PyParseBuild.PyObj(module)
		if po.pyFile.filePath.find("__init__") >= 0:
			continue
		# 检测reload的合法性
		po.CheckSelfUser()
		po.CheckSelfInherit()
		# 检测并修复XRLAM部分是否正确
		po.FixXRLAM()

if __name__ == "__main__":
	CheckModule()
	print "End"

