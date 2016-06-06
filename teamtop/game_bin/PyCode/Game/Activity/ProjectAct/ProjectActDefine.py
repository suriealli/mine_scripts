#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ProjectAct.ProjectActDefine")
#===============================================================================
# 专题活动的一些定义
#===============================================================================

MOUNT_EVOLE_DICT = {32:1, 36:5, 40:9, 42:11, 44:13, 46:15, 47:16, 49:18, 51:20, \
					52:21, 54:23, 56:25, 57:26, 59:28, 61:30 }	#坐骑星数-》奖励ID

#=======================================
#坐骑专题
#=======================================
MIN_MOUNT_TIMES = 100	#最小达标次数
#{活动ID:{培养次数：奖励ID}},国服
CUL_NUM_DICT = {106:{100:51, 300:52, 1000:53}}
#{活动ID:{培养次数：奖励ID}},美服
CUL_NUM_DICT_NA = {106:{100:51, 300:52, 500:53}}
#=======================================
#宝石专题
#=======================================
#活动需要遍历的等级宝石列表
GEM_LEVEL_EVAL = [5,6,7,8,9,10]

#{宝石等级：{宝石个数：奖励ID}}
GEM_LEVEL_NUM_REWARD = {5:{8:54}, 6:{6:55}, 7:{4:56}}

#=========================================
#许愿池专题
#=========================================
MIN_WISH_TIMES = 30	#最小的达标次数
#许愿次数-》奖励ID
WISH_TIMES_REWARD = {30:57, 80:58, 200:59}

#=========================================
#占卜专题
#=========================================
#命魂品阶:{达标个数:奖励id}
TAROT_TIMES_REWARD = {4:{5:60, 10:61}, 5:{2:62}}
GRADE_LIST = [4, 5, 6]

#=========================================
#羽翼专题
#=========================================
MIN_WING_TIMES = 10 #最小达标数
#培养次数-》奖励ID
WING_TIMES_REWARD = {100:63, 250:64, 500:65}
WING_TIMES_REWARD_NA = {50:63, 200:64, 300:65}
#=======================================
#符文专题
#=======================================
#活动需要遍历的等级符文列表
FUWEN_LEVEL_EVAL = [5,6,7,8,9,10]

#{符文等级：{符文个数：奖励ID}}
FUWEN_LEVEL_NUM_REWARD = {5:{8:66}, 6:{6:67}, 7:{4:68}}
FUWEN_LEVEL_NUM_REWARD_NA = {6:{1:66}, 7:{1:67}, 8:{1:68}}
#=======================================
#宠物专题
#=====================================
MIN_PET_TIMES = 10 #最小达标数
#培养次数-》奖励ID
PET_TIMES_REWARD = {100:69, 250:70, 500:71}
PET_TIMES_REWARD_NA = {50:69, 100:70, 200:71}
#=======================================
#婚戒专题
#=======================================
MIN_RING_TIMES = 10 #最小达标数
#培养次数-》奖励ID
RING_TIMES_REWARD = {200:72, 500:73, 1000:74}
RING_TIMES_REWARD_NA = {50:72, 200:73, 300:74}
#=======================================
#星灵专题
#=======================================
#星灵等级-》奖励ID
STARGRIL_START_REWARD = {2:76, 3:77, 4:78, 5:79, 6:80, 7:81, 8:82, 9:83, 10:84, 11:85, 12:86, 13:87, 14:88, 15:89, 16:90, 17:91, 18:92, 19:93, 20:94}
STARGRIL_START_REWARD_REMOVE = {2:76, 3:77, 4:78, 5:79, 6:80, 7:81, 8:82, 9:83, 10:84, 11:85, 12:86, 13:87, 14:88, 15:89, 16:90, 17:91, 18:92, 19:93}
