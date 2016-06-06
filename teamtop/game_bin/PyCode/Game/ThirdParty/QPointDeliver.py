#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QPointDeliver")
#===============================================================================
# Q点发货
#===============================================================================
from Game.Role.Data import EnumDisperseInt32
def G1(role, cnt):
	role.IncUnbindRMB_Q(100 * cnt) #加神石100,在推荐消费购买100神石
	
def G2(role, cnt):
	role.IncUnbindRMB_Q(500 * cnt) #加神石500,在推荐消费购买500神石
	
def G3(role, cnt):
	role.IncUnbindRMB_Q(1000 * cnt) #加神石1000，在推荐消费购买1000神石
	
def G4(role, cnt):
	role.IncUnbindRMB_Q(5000 * cnt) #加神石5000，在推荐消费购买2000神石
	
def G5(role, cnt):
	role.IncUnbindRMB_Q(20000 * cnt) #加神石20000，在推荐消费购买20000神石
	
def G6(role, cnt):
	role.IncUnbindRMB_Q(10 * cnt) #加神石10，在推荐消费购买10神石
	
def G7(role, cnt):
	role.AddItem(26143, cnt) #获得100神石礼盒，内部用
	#记录内部好发神石数量
	role.IncDI32(EnumDisperseInt32.GM_UnbindRMB, cnt * 100)
	
def G8(role, cnt):
	role.IncUnbindRMB_Q(10000 * cnt) #加神石20000，在推荐消费购买10000神石
	
#def G1(role, cnt):
#	role.AddItem(31105, cnt)