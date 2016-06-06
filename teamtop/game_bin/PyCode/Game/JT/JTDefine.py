#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTDefine")
#===============================================================================
# 组队竞技场定义
#===============================================================================
import Environment

#########################################################################################
DefaultJTScore = 700#基础组队竞技场积分
MaxTeamFlag = 12		#战队标识最大值 1 - 12
MaxRank = 2400
MaxLevelRank = 400	#等级段排名
CreateJTeamNeedRMB = 10
ChanegInfoNeedRMB = 5
DayFightRewardTimes = 5	#每天战斗奖励次数
DayRewardNeedFightCount = 5
WeekRewardNeedCount = 2	#周结算需要的日结奖励次数
#战斗类型
JT_fightType = 151
#需求角色等级
JTNeedLevel = 60
#需要世界等级
JTNeedWorldLevel = 70
#地图场景ID
JTReadySceneID = 565
#每天前10次战斗奖励
FightRewardItem = (25600, 1)

############################争霸赛#############################
JTGroupFightType = 155	#争霸赛小组赛战斗类型
#第一次开启的时间
FirstStartZBDay = 16747
#繁体重定义开启日期点
if Environment.EnvIsFT():
	FirstStartZBDay = 16754

def GetZBStartFlagNum():
	#获取争霸赛开启标识
	import cDateTime
	#固定时间计算
	d = cDateTime.Days() - FirstStartZBDay
	#4周一次 (num ==0 时为第4周周结日)
	num = d % 28
	if Environment.EnvIsNA() or Environment.EnvIsPL() or Environment.EnvIsRU():
		num = -1
	return num

def GetZBStartCnt():
	#获取争霸赛开启次数（用作争霸赛喝彩的版本号）
	import cDateTime
	#固定时间计算
	d = cDateTime.Days() - FirstStartZBDay
	#4周一次 (num ==0 时为第4周周结日)
	if Environment.EnvIsNA() or Environment.EnvIsPL() or Environment.EnvIsRU():
		return False, False, 0
	
	#活动是否开启, 活动是否结束, 活动id
	return (d % 28) < 4, (d % 28) < 5, d / 28
#争霸赛场景ID
JTZBSceneID = 701
JTZBJoinLiBao = {1:[(28927,1)], 2:[(28922,1)], 3:[(28917,1)]}	#参与奖礼包
