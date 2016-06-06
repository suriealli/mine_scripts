#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FindBack.FindBackDefine")
#===============================================================================
# 找回系统定义
#===============================================================================

#####################################################################
RMB_Reward = 1
BindRMB_Reward = 2
TimeReawrd = 3
MoneyReward = 4

#####################################################################

def IsSpecilFB(index):
	return index in (TILIFB, FBFB, HTFB)


ExpFB = 10	#经验找回
JJCFB = 20	#英雄竞技找回
DFFB = 30	#魔兽入侵找回
HWFB = 40	#荣耀之战找回
QNAFB = 50	#答题找回
TILIFB = 60	#体力找回
DAYTASKFB = 70#日常任务找回
FBFB = 80	#副本找回
HTFB = 90	#英灵神殿找回
DLFB = 100	#试练场
CFBFB = 110	#情缘副本
