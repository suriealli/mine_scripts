#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.ItemUseClassExtend")
#===============================================================================
# 特殊的物品使用类
#===============================================================================
from Game.Item.ItemUse import ItemUserClass
from Game import GlobalMessage



#特殊的等级礼包(需要提示客户端穿戴装备)
class LevelLiBao(ItemUserClass.LiBao_Normal):
	def __call__(self, role, item, cnt):
		if ItemUserClass.LiBao_Normal.__call__(self, role, item, cnt) is True:
			role.SendObj(GlobalMessage.Notify_PutOnEquipment, None)