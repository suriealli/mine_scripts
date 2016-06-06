#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.ItemUseBase")
#===============================================================================
# 物品使用
#===============================================================================

def RegItemUse(coding, itemName = None):
	#语法糖注册
	def f(fun):
		RegItemUserEx(coding, fun)
		return fun
	return f

def RegItemUserEx(coding, fun):
	#直接注册
	import Environment
	from Game.Item import ItemConfig
	# 如果没有逻辑，则不需要注册
	if not Environment.HasLogic:
		return
	cfg = ItemConfig.ItemCfg_Dict.get(coding)
	if not cfg:
		print "GE_EXC, can not find item coding in reg fun (%s)" % coding
	else:
		cfg.SetUseFun(fun)
