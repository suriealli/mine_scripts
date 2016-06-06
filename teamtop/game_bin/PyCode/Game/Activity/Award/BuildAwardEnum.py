#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Award.BuildAwardEnum")
#===============================================================================
# 注释
#===============================================================================
from Util.PY import PyParseBuild
from Game.Activity.Award import AwardConfig

if "_HasLoad" not in dir():
	pass
	
def Build():
	pf = PyParseBuild.PyFile("Common.Other.EnumAward")
	codeList = ["# 玩法奖励枚举定义" ]
	for config in AwardConfig.AWARD_ENUM_LIST:
		codeList.append("%s = %s\t\t#%s" % (config.awardEnumName, config.awardId, config.awardName))
	
	pf.ReplaceCode(codeList, "AwardEnumBegin", "AwardEnumEnd")
	pf.Write()
	print "------------------- Build OK -------------------"
	
if __name__ == "__main__":
	AwardConfig.LoadAwardEnumList()
	Build()
	
