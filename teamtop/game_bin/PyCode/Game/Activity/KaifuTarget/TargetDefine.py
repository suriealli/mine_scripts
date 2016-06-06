#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.TargetDefine")
#===============================================================================
# 活动定义
#===============================================================================
import datetime
import Environment

if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() or Environment.IsDevelop:
		#此时间段后开新的
		KaifuTime_New = datetime.datetime(2015,6,18,23,59,58)
		#此时间段后开旧的, 旧的优先级会高一点, 先判断是否开新的, 再判断是否开旧的, 能开旧的就替换掉新的
		KaifuTime_Old = datetime.datetime(2015,11,15,23,59,58)
	elif Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsNA() or Environment.EnvIsFT() or Environment.EnvIsPL():
		#北美、繁体、波兰开新版的七日目标
		KaifuTime_New = datetime.datetime(2015,6,18,23,59,58)
		KaifuTime_Old = datetime.datetime(2038,10,15,23,59,58)
	else:
		#其他版本开旧版的七日目标
		KaifuTime_New = datetime.datetime(2015,6,18,23,59,58)
		KaifuTime_Old = datetime.datetime(2015,6,18,23,59,58)
		
###########旧的活动枚举###############
Level = 1			#冲级达人
Mount = 2			#坐骑达人
Gem = 3				#宝石达人
WedingRing = 4		#婚戒达人
HeroZDL = 5			#英雄战力
RoleZDL = 6			#主角战力
TotalZDl = 7		#总战力
###########新的活动枚举###############
NewLevel = 1			#冲级达人
NewMount = 2			#坐骑达人
NewGem = 3				#宝石达人
NewTotalZDl = 4			#总战力
NewConsume = 5			#消费达人
NewCharge = 6			#充值达人
