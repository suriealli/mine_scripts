#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SuperCards.SuperCardsOnekeyFun")
#===============================================================================
# 注释
#===============================================================================
from Game.SuperCards import EnumSuperCards, SuperCards
from Game.Role.Data import EnumDayInt8

@SuperCards.RegSuperCardsFun(EnumSuperCards.UnionGod)
def OneKey_UnionGod(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return False
	
	nowGodIndex = role.GetDI8(EnumDayInt8.UnionGodProgress) + 1
	
	for godId in xrange(nowGodIndex, 23):
		if not SuperCards.ChallengeGod(role, godId):
			break
	return True
