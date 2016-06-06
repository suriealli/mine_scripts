#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ShenMiBaoXiang.ShenMiBaoXiangMgr")
#===============================================================================
# 神秘宝箱抽奖
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj, EnumInt32, EnumInt8
from Game.Role import Event
from Game.Activity.ShenMiBaoXiang import ShenMiBaoXiangConfig
import random

if "_HasLoad" not in dir(): 
	
	#消息
	SMBX_AllBXState_Sync = AutoMessage.AllotMessage("SMBX_AllBXState_Sync", "同步神秘宝箱所有宝箱状态")
	SMBX_GETBX_Sync = AutoMessage.AllotMessage("SMBX_GETBX_Sync", "同步开启的神秘宝箱")
	#日志
	
	SMBX_FIRST = AutoLog.AutoTransaction("SMBX_FIRST", "神秘宝箱开启第一次")
	SMBX_SECOND = AutoLog.AutoTransaction("SMBX_SECOND", "神秘宝箱开启第二次")
	SMBX_THIRD = AutoLog.AutoTransaction("SMBX_THIRD", "神秘宝箱开启第三次")
	SMBX_FOURTH = AutoLog.AutoTransaction("SMBX_FOURTH", "神秘宝箱开启第四次")
	SMBX_KAIQI = [SMBX_FIRST, SMBX_SECOND, SMBX_THIRD, SMBX_FOURTH]
	
	SMBX_COSTE = AutoLog.AutoTransaction("SMBX_COSTE", "开启神秘宝箱减神石")
	SMBX_DEL_BaoXiang = AutoLog.AutoTransaction("SMBX_DEL_BaoXiang", "更换神秘宝箱减宝箱")
	
	Tra_SMBX_UpdateVersion = AutoLog.AutoTransaction("Tra_SMBX_UpdateVersion", "神秘宝箱_更新活动版本号")
	


def SyncData(role):
	datadict = role.GetObj(EnumObj.ShenMiBaoXiang)
	getTimes = role.GetI8(EnumInt8.ShenMiBaoXiang) 
	role.SendObj(SMBX_AllBXState_Sync, (datadict[1], datadict[2][:getTimes]))


#=============客户端消息处理======================
def ShenMiBaoXiangOpenPanel(role, msg=None):
	'''
	打开神秘宝箱面板，同步宝箱信息
	@param role:
	@param msg is None
	'''
	
	if EnumGameConfig.SMBX_Level > role.GetLevel():
		return
	if not role.ItemCnt(EnumGameConfig.SMBX_ID):
		return
	smDict = role.GetObj(EnumObj.ShenMiBaoXiang)
	#randomList = smDict[1]
	#rewardList = smDict[2]
	#getTimes = role.GetI8(EnumInt8.ShenMiBaoXiang) 
	#totalTimes = smDict[4]
	superItems = smDict[5]#本轮需要随机的特殊奖励
	
	#如果已经随机了物品，返回
	if smDict[1]:
		SyncData(role)
		return
	
	#判断是否有极品道具该出,如果有先发极品道具
	if superItems:
		if len(superItems) > 4:
			smDict[1] = superItems[:4]
			smDict[2] = superItems[:4]
			smDict[5] = superItems[4:]
		else:
			smDict[1] = superItems[:]
			smDict[2] = superItems[:]
			smDict[5] = []
	
	#可以随机到一样的
	randConfiglist = []
	for _ in range(8):
		randConfiglist.append(ShenMiBaoXiangConfig.SMBX_REWARD_RANDOM_DICT_ALL.RandomOne())
	
	if not smDict[1]:
		smDict[1] = randConfiglist[:]
		smDict[2] = randConfiglist[:4]
		#必须有一个极品道具(替换掉最后一个)
		smDict[1][7] = random.choice(ShenMiBaoXiangConfig.SMBX_SUPERITEM_DICT.keys())
		#重新打乱列表
		random.shuffle(smDict[1])
	else:
		randConfiglist = randConfiglist[:8 - len(smDict[1])]
		smDict[1].extend(randConfiglist[:])
		random.shuffle(smDict[1])
		random.shuffle(randConfiglist)
		smDict[2].extend(randConfiglist[:4 - len(smDict[2])])
	#最后才重置抽奖次数
	role.SetI8(EnumInt8.ShenMiBaoXiang, 0)
	SyncData(role)


def RequestBaoXiang(role, msg=None):
	'''
	神秘宝箱抽取一次，同步宝箱信息
	@param role:
	@param msg is None
	'''
	#判断物品使用等级
	if not role.ItemCnt(EnumGameConfig.SMBX_ID):
		return 
	
	smDict = role.GetObj(EnumObj.ShenMiBaoXiang)
	#randomList = smDict[1]
	rewardList = smDict[2]
	if not rewardList:
		return
	getTimes = role.GetI8(EnumInt8.ShenMiBaoXiang)
	if getTimes >= 4:
		return
	needRMB = ShenMiBaoXiangConfig.SMBX_MONEY_DICT[getTimes + 1]
	if needRMB > role.GetUnbindRMB():
		return
	with SMBX_COSTE:
		role.DecUnbindRMB(needRMB)
		role.IncI8(EnumInt8.ShenMiBaoXiang, 1)
		smDict[4] += 1
		totalTimes = smDict[4]
		superItems = smDict[5]
		for index, times in ShenMiBaoXiangConfig.SMBX_SUPERITEM_DICT.iteritems():
			if times < totalTimes:
				continue
			if totalTimes % times != 0:
				continue
			#触发一次必出的极品奖励(下次打开一个新的宝箱的时候会开出来)
			superItems.append(index)
		#奖励的index
		rewardIndex = rewardList[getTimes]
		
	role.SendObjAndBack(SMBX_GETBX_Sync, rewardIndex, 20, OneTimeCallBack, (rewardIndex, getTimes))

def OneTimeCallBack(role, callargv, regparam=None):
	'''
	一次抽奖客户   端回调
	'''
	rewardIndex, times = regparam
	rewardCfg = ShenMiBaoXiangConfig.SMBX_REWARD_DICT.get(rewardIndex)
	if not rewardCfg:
		print "GE_EXC, OneTimeCallBack error not config (%s)" % rewardIndex
		return
	#发物品
	with SMBX_KAIQI[times]:
		role.AddItem(rewardCfg.item, rewardCfg.num)
	#提示
	if rewardCfg.superItem:
		cRoleMgr.Msg(1, 0, GlobalPrompt.ShenMiBaoXiang_Tip % (role.GetRoleName(), rewardCfg.item, rewardCfg.num))
	else:
		role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (rewardCfg.item, rewardCfg.num))

def RequestChangeBaoXiang(role, msg=None):	
	'''
	神秘宝箱更换宝箱，同步宝箱信息
	@param role:
	@param msg is None
	'''
	#最后一个宝箱需要清理数据
	if role.ItemCnt(EnumGameConfig.SMBX_ID) <= 0:
		return 
	if EnumGameConfig.SMBX_Level > role.GetLevel():
		return
	#删除宝箱并且清理数据
	with SMBX_DEL_BaoXiang:
		role.DelItem(EnumGameConfig.SMBX_ID, 1)
		role.GetObj(EnumObj.ShenMiBaoXiang)[1] = []
		role.GetObj(EnumObj.ShenMiBaoXiang)[2] = []
		role.SetI8(EnumInt8.ShenMiBaoXiang, 0)
	
	if role.ItemCnt(EnumGameConfig.SMBX_ID) <= 0:
		#已经没有宝箱了不新生成数据
		return
	#新的一个宝箱
	ShenMiBaoXiangOpenPanel(role)
	

#### 事件 start
def InitAndUpdateVersion(role, param=None):
	'''
	根据活动版本号 和 记录的版本好 处理角色Obj数据
	'''
	SMBX_Version = EnumGameConfig.SMBX_Version
	if Environment.EnvIsNA():
		SMBX_Version = EnumGameConfig.SMBX_Version_NA
	roleVersion = role.GetI32(EnumInt32.ShenMiBaoXiangVersion)
	if roleVersion == SMBX_Version:
		return
	if roleVersion > SMBX_Version:
		print "GE_EXC, ShenMiBaoXiang::UpdateVersion VERSION(%s) < roleVersion (%s), role id(%s)" % (SMBX_Version, roleVersion, role.GetRoleID())
		return
	
	#1.确保key存在,初始化数据	#保证升级版本号数据逻辑
	#2.根据版本号处理活动数据
	#重置相关数据
	with Tra_SMBX_UpdateVersion:
		#升级版本号
		role.SetI32(EnumInt32.ShenMiBaoXiangVersion, SMBX_Version)
		#Obj 1:随机用于显示的8个index列表,2，当前宝箱可以开出的4个奖励index列表 。4总共领取的次数(用于计算极品奖励)。5，下个宝箱必出的极品奖励index列表
		role.SetObj(EnumObj.ShenMiBaoXiang, {1:[], 2:[], 4:0, 5:[]})
		role.SetI8(EnumInt8.ShenMiBaoXiang, 0)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_AfterLogin, InitAndUpdateVersion)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ShenMiBaoXiang_Open_Panel", "神秘宝箱打开面板(开启宝箱)"), ShenMiBaoXiangOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestBaoXiang", "神秘宝箱开启宝箱(领取宝箱奖励)"), RequestBaoXiang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChangeBaoXiang", "神秘宝箱更换宝箱"), RequestChangeBaoXiang)
