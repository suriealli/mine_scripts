#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ProjectAct.EnumProActType")
#===============================================================================
# 专属活动
#===============================================================================


#=================事件=================
ProjectGemEvent		 = 1	#宝石合成事件
ProjectMountEvent	 = 2	#神石培养坐骑事件
ProjectWishEvent	 = 3	#许愿事件
ProjectTatotEvent	 = 4	#高级占卜事件
ProjectWingEvent	 = 5	#羽翼培养事件
ProjectFuwenEvent	 = 6	#符文合成事件
ProjectPetEvent		 = 7	#宠物培养事件
ProjectRingEvent	 = 8	#婚戒培养事件
ProjectStarGirlStarEvent = 9	#星灵升星

#===========================================
#填专属活动的ID,ID须和配置表的ID一样
#===========================================
Mount_ProAct_1 = 101	#坐骑专题活动1
Mount_ProAct_2 = 102	#坐骑专题活动2
Mount_ProAct_3 = 103	#坐骑专题活动3
Mount_ProAct_4 = 104	#坐骑专题活动4
Mount_ProAct_5 = 105	#坐骑专题活动5
Mount_ProAct_6 = 106	#坐骑专题活动6
Gem_ProAct_1   = 107	#宝石专题活动1
Wish_ProAct    = 108	#中秋专题1，许愿
Tarot_ProAct   = 109	#中秋专题2，高级占卜
Wing_ProAct    = 110	#羽翼专题
FuWen_ProAct   = 111	#符文专题
Pet_Project    = 112	#宠物专题
Ring_Project   = 113	#婚戒专题
StarGirl_Project=114	#星灵专题
#===============================================
#系列活动
#===============================================

#===================坐骑专题活动===================
#这里需要特殊处理下，因为坐骑有按阶数领奖的，也有按培养次数领奖的，所以把这2类分开处理
#按阶数领奖
MOUNT_ACT_LIST1 = [Mount_ProAct_1, Mount_ProAct_2, Mount_ProAct_3, Mount_ProAct_4, Mount_ProAct_5]
#按培养次数领奖
MOUNT_ACT_LIST2 = [Mount_ProAct_6]
#===================宝石专题活动===================
GEM_ACT_LIST = [Gem_ProAct_1]
