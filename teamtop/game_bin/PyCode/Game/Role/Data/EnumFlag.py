#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumFlag")
#===============================================================================
# 角色Python对象枚举模块
#===============================================================================
import cRoleDataMgr
from Common import Coding

L = []
def F(uIdx):
	'''
	设置Python对象数组
	@param uIdx:下标
	'''
	assert uIdx < (Coding.RoleObjFlagRange[1] - Coding.RoleObjFlagRange[0])
	if not L:
		assert uIdx == 0
	else:
		assert uIdx == L[-1] + 1
	L.append(uIdx)
	cRoleDataMgr.SetFlagRule(uIdx)

#===============================================================================
# 数组使用定义
#===============================================================================
En_None = 0
F(En_None)





