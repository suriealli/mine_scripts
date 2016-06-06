#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DailyFB.DailyFBMgr")
#===============================================================================
# 勇者试炼场Mgr
#===============================================================================
import copy
import random
import cDateTime
import cRoleMgr
import cSceneMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumFightStatistics
from ComplexServer.Log import AutoLog
from Game.Fight import Fight
from Game.Scene import PublicScene
from Game.DailyFB import DailyFBConfig
from Game.Role import Event, Status, Call
from Game.Role.Data import EnumObj, EnumCD, EnumInt1
from Game.Activity import CircularDefine
from Game.Activity.RewardBuff import RewardBuff

IDX_FBLEVEL = 1
IDX_KILLNUM = 2
IDX_EXP = 3
IDX_DAYINDEX = 4

if "_HasLoad" not in dir():
	#三个试炼场场景ID列表
	FB_SCENEID_LIST_DICT = {1:[356,357], 2:[364], 3:[369]}
	#三个试炼场的随机传送点列表
	TP_XY_DICT = {1:[(1515,339),(374,833),(1044,2288),(3521,1177)],2:[(1031,671),(1181,2021),(3393,2114),(3589,519)],3:[(597,923),(3678,1164),(3003,626)]}
	#三个试炼场当前可进入的场景ID	
	CAN_JOIN_SCENE_ID_DICT = {1:356, 2:364, 3:369}
	#三个试炼场FBobj
	SCENEID_FBOBJ_DICT = {}	#senceId->副本对象	
	#每个场景的最大人数
	MAX_ROLE_SCENCE = 200
	#活动开启标志
	IsOpen = False
	#推送
	DailyFB_DailyFBData_S = AutoMessage.AllotMessage("DailyFB_DailyFBData_S", "勇者试炼场_同步试炼场数据")
	DailyFB_DailyFBPass_SB = AutoMessage.AllotMessage("DailyFB_DailyFBPass_SB", "勇者试炼场_通关")
	#事务
	Tra_DailyFB_PassReward = AutoLog.AutoTransaction("Tra_DailyFB_PassReward", "勇者试炼场_通关奖励")
	Tra_DailyFB_KillReward = AutoLog.AutoTransaction("Tra_DailyFB_KillReward", "勇者试炼场_击杀获得")
	Tra_DailyFB_OneKeyFininsh = AutoLog.AutoTransaction("Tra_DailyFB_OneKeyFininsh", "勇者试炼场_一键完成")

#======================活动开启和关闭==============
def OpenAct(param1, param2):
	#开启活动
	if param2 != CircularDefine.CA_SpringFUniversal:
		return
	
	global IsOpen
	if IsOpen:
		print 'GE_EXC, HappyNewYear is already open'
	IsOpen = True

def CloseAct(param1, param2):
	#关闭活动
	if param2 != CircularDefine.CA_SpringFUniversal:
		return
	
	global IsOpen
	if not IsOpen:
		print 'GE_EXC, HappyNewYear is already close'
	IsOpen = False
#===============================================	
	
class DailyFB(object):
	'''
	勇者试炼场
	'''
	def __init__(self, FBLevel, sceneId):
		self.FBLevel = FBLevel
		self.sceneId = sceneId
		self.scene = cSceneMgr.SearchPublicScene(self.sceneId)
		if not self.scene:
			print "GE_EXC, DailyFB can not find sceneId(%s)" % self.sceneId
			return
		self.role_set = set()		#该场景中的玩家ID
	
	def AfterJoin(self, role):
		'''
		玩家进入场景  根据场景内人数 更新下个玩家要进入场景
		'''
		#强制进入状态
		Status.ForceInStatus(role, EnumInt1.ST_DailyFB)
		#缓存场景内roleID
		roleId = role.GetRoleID()
		self.role_set.add(roleId)
		#人数已超标
		if len(self.role_set) < MAX_ROLE_SCENCE:
			return
		UpdateJoinScene(self.FBLevel)

	def BeforeLeave(self, role):
		'''
		玩家离开场景
		'''
		#退出副本状态
		Status.Outstatus(role, EnumInt1.ST_DailyFB)
		#删除场景中缓存的玩家ID
		self.role_set.discard(role.GetRoleID())


def UpdateJoinScene(FBLevel):
	#判断场景是否已满，是否激活下个场景ID
	global FB_SCENEID_LIST_DICT
	global CAN_JOIN_SCENE_ID_DICT
	#获取当前可进场景在场景列表中的index
	sceneId_list = FB_SCENEID_LIST_DICT.get(FBLevel)
	can_join_sceneId = CAN_JOIN_SCENE_ID_DICT.get(FBLevel)
	if not sceneId_list or not can_join_sceneId:
		print "GE_EXC, Dailyfb UpdateJoinScene error" , sceneId_list, can_join_sceneId, FBLevel
		return
	old_index = sceneId_list.index(can_join_sceneId)
	#已经是最后个场景了,下个可进场景为场景列表的第一个
	if old_index + 1 >= len(sceneId_list):
		can_join_sceneId = sceneId_list[0]
	else:
		#下个可进场景为场景列表的下一个
		can_join_sceneId = sceneId_list[old_index + 1]
	#更新可进入场景ID
	CAN_JOIN_SCENE_ID_DICT[FBLevel] = can_join_sceneId


#### 场景事件 start
def RegDailyFBJoinAndLeaveFun():
	'''
	注册场景的 进入 离开 逻辑
	'''
	for _, sceneIdList in FB_SCENEID_LIST_DICT.iteritems():
		for sceneId in sceneIdList:
			PublicScene.SceneJoinFun[sceneId] = AfterJoinScene
			PublicScene.SceneBeforeLeaveFun[sceneId] = BeforeLeaveScene

def InitDailyFBScene(param1, param2):
	'''
	初始化副本临时对象
	'''
	#初始化
	for FBLevel, sceneIdList in FB_SCENEID_LIST_DICT.iteritems():
		for sceneId in sceneIdList:
			SCENEID_FBOBJ_DICT[sceneId] = DailyFB(FBLevel, sceneId)

def AfterJoinScene(scene, role):
	'''
	进入场景之后
	'''
	sceneId = scene.GetSceneID()
	FBObj = SCENEID_FBOBJ_DICT.get(sceneId)
	if FBObj:
		FBObj.AfterJoin(role)
	else:
		print "GE_EXC DailyFB join scene error (%s), (%s)" % (role.GetRoleID(), sceneId)

def BeforeLeaveScene(scene, role):
	'''
	离开场景之前
	'''
	sceneId = scene.GetSceneID()
	FBObj = SCENEID_FBOBJ_DICT.get(sceneId)
	if FBObj:
		FBObj.BeforeLeave(role)

def BackPublicScene(role, isForce, regparam):
	'''
	传送回去
	'''
	if role.IsKick():
		return
	
	#传送前判断是否能进入传送状态
	if not isForce and (not Status.CanInStatus(role, EnumInt1.ST_TP)):
		return
	
	#传送
	if role.GetSceneID() in SCENEID_FBOBJ_DICT:
		role.BackPublicScene()
	
#### 战斗 start
def PVE_DailyFB(role, fightType, mcid, fightCfg):
	'''
	勇者试炼场PVE战斗
	'''
	fight = Fight.Fight(fightType)
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	#创建两个阵营
	left_camp, right_camp = fight.create_camp()
	#在阵营中创建战斗单位
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	#设置回调函数
	fight.after_fight_fun = AfterFight		#战斗结束
	fight.after_play_fun = AfterPlay		#客户端播放完毕
	fight.after_fight_param = fightCfg		#注册参数
	fight.start()

def AfterFight(fightObj):
	'''
	战斗结束  计算相关数据 加塞到fightObj 再Afterplayer中对应处理
	'''
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	if role.IsKick():
		return

	if fightObj.result != 1:
		return
	if role.GetSceneID() not in SCENEID_FBOBJ_DICT:
		return
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	fightCfg = fightObj.after_fight_param
	dailyFBCfg = DailyFBConfig.GetBaseCfgByFBLevel(fightCfg.FBLevel)
	if not dailyFBCfg:
		return
	global IsOpen
	#战斗次数
	killedNum = dailyFBData[IDX_KILLNUM] + 1
	addExp = 0
	if killedNum <= dailyFBCfg.passKillNum:
		if IsOpen:
			addExp = fightCfg.ActaddExp
		else:
			addExp = fightCfg.addExp
	elif killedNum <= dailyFBCfg.maxKillNum:
		if IsOpen:
			addExp = fightCfg.ActdiscountExp
		else:
			addExp = fightCfg.discountExp
	#更新经验获得
	if addExp > 0:
		fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumExp, RewardBuff.CalNumberRole(role, RewardBuff.enDailyFB, addExp))

def AfterPlay(fightObj):
	'''
	战斗播放完毕    本场结算 判断是否通关  判断并重置相关数据  跨天传回
	'''
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	if role.IsKick():
		return
	if role.GetSceneID() not in SCENEID_FBOBJ_DICT:
		return
	if fightObj.result != 1:
		#客户端掉线 传回
		if role.IsLost():
			BackPublicScene(role, True, None)
		return
	
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	fightCfg = fightObj.after_fight_param
	dailyFBCfg = DailyFBConfig.GetBaseCfgByFBLevel(fightCfg.FBLevel)
	if not dailyFBCfg:
		print "GE_EXC AfterPlay error "
		return
	#战斗次数
	isPassFB = False 
	isMaxKill = False
	killedNum = dailyFBData[IDX_KILLNUM] + 1
	addExp = 0
	global IsOpen
	
	if killedNum <= dailyFBCfg.passKillNum:
		if IsOpen:
			addExp = fightCfg.ActaddExp
		else:
			addExp = fightCfg.addExp
		if killedNum == dailyFBCfg.passKillNum:
			isPassFB = True
	elif killedNum <= dailyFBCfg.maxKillNum:
		if IsOpen:
			addExp = fightCfg.ActdiscountExp
		else:
			addExp = fightCfg.discountExp
		if killedNum == dailyFBCfg.maxKillNum:
			isMaxKill = True
	#更新战斗场次		
	dailyFBData[IDX_KILLNUM] = killedNum
	#更新经验获得
	if addExp > 0:
		fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumExp, addExp)
		dailyFBData[IDX_EXP] += addExp
		with Tra_DailyFB_KillReward:
			role.IncExp(RewardBuff.CalNumberRole(role, RewardBuff.enDailyFB, addExp))
	
	role.SendObj(DailyFB_DailyFBData_S, dailyFBData)
	
	#通关处理
	FBLevel, roleLevel = fightCfg.FBLevel, fightCfg.roleLevel
	if isPassFB:
		passRewardCfg = DailyFBConfig.GetPassRewardCfgByLevels(FBLevel, roleLevel)
		if passRewardCfg:
			role.SendObjAndBack(DailyFB_DailyFBPass_SB, (FBLevel, roleLevel), 8, OnPassRewardCallBack, (role.GetRoleID(), FBLevel, roleLevel))
		else:
			print "GE_EXC, DailyFB AfterPlay::can not get passRewardCfg with FBLevel(%s) and roleLevel(%s)" % (FBLevel, roleLevel)
		
		#活跃度 -- 通关勇者试练场
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DailyFB, 1))
		
	#今日战斗场次超过最大限制 T出试炼场
	if isMaxKill:
		BackPublicScene(role, True, None)
		role.Msg(5, 0, GlobalPrompt.DailyFB_Tips_MaxFight)
	elif role.IsLost():
		#客户端掉线 传回
		BackPublicScene(role, True, None)

def OnPassRewardCallBack(role, calArgvs, regParam):
	'''
	通关奖励回调
	'''
	roleId, FBLevel, roleLevel = regParam
	Call.LocalDBCall(roleId, PassRewardNew, (FBLevel, roleLevel))

def PassReward(role, param):
	'''
	通关奖励(请勿修改)
	'''
	passRewardCfg = param
	rewardMoney = passRewardCfg.rewardMoney
	rewardPrompt = GlobalPrompt.DailyFB_Tips_Head + GlobalPrompt.GetDailyFBNameByLevel(passRewardCfg.FBLevel)
	with Tra_DailyFB_PassReward:
		#金币
		if rewardMoney > 0:
			role.IncMoney(rewardMoney)
			rewardPrompt += GlobalPrompt.DailyFB_Tips_Money % rewardMoney 
		#物品
		if passRewardCfg.rewardItems:
			for coding, cnt in passRewardCfg.rewardItems:
				role.AddItem(coding, cnt)
				rewardPrompt += GlobalPrompt.DailyFB_Tips_Item % (coding, cnt)
		
	role.Msg(2, 0, rewardPrompt)

def PassRewardNew(role, param):
	#新的离线命令
	FBLevel, roleLevel = param
	passRewardCfg = DailyFBConfig.GetPassRewardCfgByLevels(FBLevel, roleLevel)
	if not passRewardCfg:
		return
	PassReward(role, passRewardCfg)

#### 客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	勇者试炼场_请求打开面板  判断并重置相关数据
	'''
	backFunId,_ = msg
	if role.GetLevel() < EnumGameConfig.DailyFB_NeedLevel:
		return
	role.CallBackFunction(backFunId, UpdateAndSync(role, cDateTime.Days(), False))
		
def OnEnterFB(role, msg):
	'''
	勇者试炼场_请求进入试炼场
	'''
	if role.GetLevel() < EnumGameConfig.DailyFB_NeedLevel:
		return
	#已经在该地图
	if role.GetSceneID() in SCENEID_FBOBJ_DICT:
		return
	#传送前判断是否能进入传送状态
	if not Status.CanInStatus(role, EnumInt1.ST_DailyFB):
		return
	FBLevel = msg
	if FBLevel not in FB_SCENEID_LIST_DICT:
		return
	sceneId = CAN_JOIN_SCENE_ID_DICT.get(FBLevel)
	if not sceneId:
		return
	dailyFBCfg = DailyFBConfig.GetBaseCfgByFBLevel(FBLevel)
	if not dailyFBCfg:
		return
	
	#今日首次进入试炼场  判断 并 记录今日试炼场级别
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	nowFblevel = dailyFBData.get(IDX_FBLEVEL)
	if not nowFblevel:
		if not dailyFBCfg.CanJoin(role):
			return
		#可以进场 update data
		dailyFBData[IDX_FBLEVEL] = FBLevel
	else:
		#没有跨天 且 本次请求进入的试炼场与今日已经选择的试炼场不同 
		if nowFblevel != FBLevel:
			return
		#今日战斗胜场超过最大场次
		if dailyFBData[IDX_KILLNUM] >= dailyFBCfg.maxKillNum:
			return
		
	#同步最新的data
	role.SendObj(DailyFB_DailyFBData_S, role.GetObj(EnumObj.DailyFBData))
	
	#传送
	TP_XY_LIST = TP_XY_DICT.get(FBLevel)
	TP_X, TP_Y = TP_XY_LIST[random.randint(0,len(TP_XY_LIST)-1)]
	role.Revive(sceneId, TP_X, TP_Y)
	
	Event.TriggerEvent(Event.Eve_FB_DL, role)

def OnFightMonster(role, msg = None):
	'''
	勇者试炼场_请求挑战怪物 
	'''
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.DailyFB_NeedLevel:
		return
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	FBLevel = dailyFBData.get(IDX_FBLEVEL)
	fightCfg = DailyFBConfig.GetFightCfgByLevels(FBLevel, roleLevel)
	if not fightCfg:
		return
	
	#维护战斗CD
	if role.GetCD(EnumCD.DailyFBFightDelta):
		return
	
	#玩家不在指定的场景中
	if role.GetSceneID() not in SCENEID_FBOBJ_DICT.keys():
		return
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	role.SetCD(EnumCD.DailyFBFightDelta, EnumGameConfig.DailyFB_FightCD)
	#扔进战斗
	PVE_DailyFB(role, fightCfg.fightType, fightCfg.campId, fightCfg)
	
def OnLeaveFB(role, msg = None):
	'''
	勇者试炼场_请求离开试炼场
	'''
	BackPublicScene(role, None, None)

def OnOneKeyFinish(role, msg):
	'''
	勇者试炼场_一键完成
	'''
	targetFBLevel = msg
	today = cDateTime.Days()
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	if dailyFBData[IDX_DAYINDEX] != today:
		return

	myDailyFBLevel = dailyFBData[IDX_FBLEVEL]
	killedNum = dailyFBData[IDX_KILLNUM]
	# 1.1已经选择了其他级别试炼场
	if myDailyFBLevel and (myDailyFBLevel != targetFBLevel):
		return

	roleLevel = role.GetLevel()
	#参数 -> cfg 
	dailyFBCfg = DailyFBConfig.GetBaseCfgByFBLevel(targetFBLevel)
	if not dailyFBCfg:
		return
	#VIP等级不足
	if role.GetVIP() < dailyFBCfg.sweepNeedVIP:
		return
	
	#战斗cfg for 总经验获得
	fightCfg = DailyFBConfig.GetFightCfgByLevels(targetFBLevel, roleLevel)
	if not fightCfg:
		return
	
	#通关Cfg for 物品&经验
	passRewardCfg = DailyFBConfig.GetPassRewardCfgByLevels(targetFBLevel, roleLevel)
	if not passRewardCfg:
		return
	#已经通关
	if killedNum >= dailyFBCfg.passKillNum:
		return
	#update
	dailyFBData[IDX_FBLEVEL] = targetFBLevel
	dailyFBData[IDX_KILLNUM] = dailyFBCfg.passKillNum
	global IsOpen
	if IsOpen:
		dailyFBData[IDX_EXP] = fightCfg.ActaddExp * dailyFBCfg.passKillNum
	else:
		dailyFBData[IDX_EXP] = fightCfg.addExp * dailyFBCfg.passKillNum
	dailyFBData[IDX_DAYINDEX] = today
	#sync
	role.SendObj(DailyFB_DailyFBData_S, dailyFBData)
	#process
	prompt =  GlobalPrompt.DailyFB_Tips_Head + GlobalPrompt.GetDailyFBNameByLevel(targetFBLevel)
	with Tra_DailyFB_OneKeyFininsh:
		#物品
		if passRewardCfg.rewardItems:
			for coding, cnt in passRewardCfg.rewardItems:
				role.AddItem(coding, cnt)
				prompt += GlobalPrompt.DailyFB_Tips_Item % (coding, cnt)
		#金币
		rewardMoney = passRewardCfg.rewardMoney
		if rewardMoney > 0:
			role.IncMoney(rewardMoney)
			prompt += GlobalPrompt.DailyFB_Tips_Money % rewardMoney
		#经验
		rewardExp = 0
		if IsOpen:
			rewardExp = (dailyFBCfg.passKillNum - killedNum) * fightCfg.ActaddExp
		else:
			rewardExp = (dailyFBCfg.passKillNum - killedNum) * fightCfg.addExp
		
		if rewardExp > 0:
			role.IncExp(RewardBuff.CalNumberRole(role, RewardBuff.enDailyFB, rewardExp))
			prompt += GlobalPrompt.DailyFB_Tips_Exp % RewardBuff.CalNumberRole(role, RewardBuff.enDailyFB, rewardExp)
	
	Event.TriggerEvent(Event.Eve_FB_DL, role)
	#活跃度 -- 通关勇者试练场
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DailyFB, 1))
	
	role.Msg(2, 0, prompt)


def UpdateAndSync(role, today, Sync = True):
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	if dailyFBData[IDX_DAYINDEX] < today:
		dailyFBData[IDX_FBLEVEL] = 0
		dailyFBData[IDX_KILLNUM] = 0
		dailyFBData[IDX_EXP] = 0
		dailyFBData[IDX_DAYINDEX] = today
		#update
		role.SetObj(EnumObj.DailyFBData, dailyFBData)
	#Sync
	if Sync is True:
		role.SendObj(DailyFB_DailyFBData_S, dailyFBData)
	else:
		return dailyFBData

#### 事件 start
def OnRoleInit(role, param):
	'''
	初始化obj字典key
	'''
	dailyFBData = role.GetObj(EnumObj.DailyFBData)
	if not dailyFBData:
		dailyFBData = {1:0, 2:0, 3:0, 4:cDateTime.Days()}
		role.SetObj(EnumObj.DailyFBData, dailyFBData)

def OnSyncRoleOtherData(role, param):
	'''
	上线同步最新有效数据  给前端做效果诱导
	'''
	UpdateAndSync(role, cDateTime.Days())

def OnQuitDailyFB(role, param):
	'''
	客户端掉线 传回
	'''
	#传回
	BackPublicScene(role, None, None)
	
def AfterNewDay():
	'''
	跨天 
	'''
	#把试炼场内所有玩家传送出来
	for _, dailyFB in SCENEID_FBOBJ_DICT.iteritems():
		roleset = copy.deepcopy(dailyFB.role_set)		#BackPublicScene内部逻辑导致场景内玩家传回 从而dailyFB.role_set改变 故deepcopy
		for tmpRoleId in roleset:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				continue
			BackPublicScene(tmpRole, True, None)
			tmpRole.Msg(5, 0, GlobalPrompt.DailyFB_Tips_AfterNewDayFail)

	#更新所有人的数据
	today = cDateTime.Days()	
	for tmpRole in cRoleMgr.GetAllRole():
		UpdateAndSync(tmpRole, today)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#pre_process
		RegDailyFBJoinAndLeaveFun()
		#事件
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_ClientLost, OnQuitDailyFB)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, InitDailyFBScene)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenAct)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseAct)
		
		#跨天处理
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		#客户端请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyFB_OnOpenPanel", "勇者试炼场_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyFB_OnEnterFB", "勇者试炼场_请求进入试炼场"), OnEnterFB)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyFB_OnLeaveFB", "勇者试炼场_请求离开试炼场"), OnLeaveFB)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyFB_OnFightMonster", "勇者试炼场_请求挑战怪物"), OnFightMonster)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyFB_OnOneKeyFinish", "勇者试炼场_一键完成"), OnOneKeyFinish)		
