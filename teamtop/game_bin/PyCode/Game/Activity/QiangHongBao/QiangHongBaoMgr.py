#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QiangHongBao.QiangHongBaoMgr")
#===============================================================================
# 抢红包Mgr
#===============================================================================
import random
import Environment
import cRoleMgr
import cSceneMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.Role import Event, Status
from Game.Fight import Fight, Middle
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt1, EnumDayInt8, EnumTempInt64


if "_HasLoad" not in dir():
	#NPC信息 (NPCType,场景ID, x坐标, y坐标, d朝向)
	Npc_Info = (19044, 17, 3330, 810, 0)
	#NPC附近传送点
	Npc_NearPoint = {1:[17,3232, 641], 2:[17,3080,929], 3:[17,3640,911]}
	#大奖励道具
	BigRewardItem = (28685,1)
	#小奖励道具
	SmallRewardItem = (28686,1)
	#单轮倒计时秒数
	Round_Seconds = 30
	#一分钟秒数
	QHB_OneMin_Sec = 60
	#活动开关
	ACTIVE_IS_START = False
	#抢红包回合开关
	ROUND_FLAG = False
	#当前抢红包参与者roleID集合
	QHB_RoleIDs_Set = set()
	#红包NPC
	QHB_NPC_OBJ = None
	#一分钟提示时候 计算出来真正开启的时间戳
	QHB_RoundStart_Timestamp = 0
	
	#抢红包_倒计时进度条同步 0-关闭  1-打开
	QiangHongBao_CountDown_S = AutoMessage.AllotMessage("QiangHongBao_CountDown_S", "抢红包_倒计时进度条同步")
	
	#抢红包回合开关通知 0-关闭 1-开始
	QiangHongBao_Round_S = AutoMessage.AllotMessage("QiangHongBao_Round_S", "抢红包回合开关通知")
	
	#抢红包开始一分钟内倒计时同步
	QiangHongBao_OneMinTick_S = AutoMessage.AllotMessage("QiangHongBao_OneMinTick_S", "抢红包开始一分钟内倒计时同步")
	
	Tra_QiangHongBao_TimeOutReward = AutoLog.AutoTransaction("Tra_QiangHongBao_TimeOutReward", "抢红包_超时获得奖励") 
	Tra_QiangHongBao_FightReward = AutoLog.AutoTransaction("Tra_QiangHongBao_FightReward", "抢红包_战斗获得奖励") 


################## 活动控制start #######################
def OnStartQiangHongBao(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_QiangHongBao != circularType:
		return
	
	global ACTIVE_IS_START
	if ACTIVE_IS_START:
		print "GE_EXC,repeat Start QiangHongBao"
		return
	
	ACTIVE_IS_START = True
	
	
def OnEndQiangHongBao(*param):
	'''
	关闭活动
	'''
	_, circularType = param
	if CircularDefine.CA_QiangHongBao != circularType:
		return
	
	global ACTIVE_IS_START
	if not ACTIVE_IS_START:
		print "GE_EXC,repeat End QiangHongBao"
		return
	
	ACTIVE_IS_START = False


###################   事件触发   ######################
def OneMinuteBefore():
	'''
	每轮抢红包一分钟前广播
	'''
	if not ACTIVE_IS_START:
		return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.QiangHongBao_Msg_OneMin)

	global QHB_RoundStart_Timestamp
	QHB_RoundStart_Timestamp = cDateTime.Seconds() + QHB_OneMin_Sec
	
	cNetMessage.PackPyMsg(QiangHongBao_OneMinTick_S, QHB_RoundStart_Timestamp)
	cRoleMgr.BroadMsg()


def QiangHongBaoStart():
	'''
	本轮抢红包开始
	'''	
	if not ACTIVE_IS_START:
		return
	
	global ROUND_FLAG
	global QHB_RoundStart_Timestamp
	if ROUND_FLAG:
		print "GE_EXC, QiangHongBaoStart:: ROUND_FLAG is True"
		return
	ROUND_FLAG = True
	QHB_RoundStart_Timestamp = 0
	#刷出红包NPC
	CreateHongBaoNPC()
	#T出参与者
	global QHB_RoleIDs_Set
	QHB_RoleIDs_Set.clear()
	#启动抢红包回合处理
	cComplexServer.RegTick(Round_Seconds, DoJudge)
	#同步客户端当前正在抢红包
	cNetMessage.PackPyMsg(QiangHongBao_Round_S, 1)
	cRoleMgr.BroadMsg()
	#广播提示
	cRoleMgr.Msg(1, 0, GlobalPrompt.QiangHongBao_Msg_Start)

	
def QiangHongBaoEnd():
	'''
	本轮抢红包结束
	'''
	if not ACTIVE_IS_START:
		return
	
	global ROUND_FLAG
	if not ROUND_FLAG:
		print "GE_EXC, QiangHongBaoEnd:: ROUND_FLAG is False"
		return
	ROUND_FLAG = False
	#注销红包NPC
	DestroyHongBaoNPC()
	#同步客户端结束当前抢红包
	cNetMessage.PackPyMsg(QiangHongBao_Round_S, 0)
	cRoleMgr.BroadMsg()
	#广播提示
	cRoleMgr.Msg(1, 0, GlobalPrompt.QiangHongBao_Msg_End)


def OnSyncRoleData(role, param = None):
	'''
	上线同步当前是否正在抢红包
	'''
	if not ACTIVE_IS_START:
		return
	
	if ROUND_FLAG:
		role.SendObj(QiangHongBao_Round_S, 1)
	elif QHB_RoundStart_Timestamp:
		role.SendObj(QiangHongBao_OneMinTick_S, QHB_RoundStart_Timestamp)
	else:
		pass
	

def RoleOffLine(role, param = None):
	'''
	玩家离线
	'''
	#非活动期间
	if not ACTIVE_IS_START:
		return
	
	#未参与抢红包
	global QHB_RoleIDs_Set
	roleId = role.GetRoleID()
	if roleId not in QHB_RoleIDs_Set:
		return
	else:
		#T出参与
		QHB_RoleIDs_Set.discard(roleId)
		#状态恢复
		Status.Outstatus(role, EnumInt1.ST_QiangHongBao)
		#注销TICK
		role.UnregTick(role.GetTI64(EnumTempInt64.QiangHongBaoTickId))


def QHBTickTock(role, callArgvs = None, regParam = None):
	'''
	角色抢红包tick触发
	'''
	if role.IsLost() or role.IsKick():
		return
	
	if not ACTIVE_IS_START or not ROUND_FLAG:
		#状态恢复
		Status.Outstatus(role, EnumInt1.ST_QiangHongBao)
		return
	
	#已经出局了
	global QHB_RoleIDs_Set
	roleId = role.GetRoleID()
	if roleId not in QHB_RoleIDs_Set:
		#状态恢复
		Status.Outstatus(role, EnumInt1.ST_QiangHongBao)
		return
	
	prompt = GlobalPrompt.QiangHongBao_Tips_Head
	rewardType = random.sample(EnumGameConfig.QiangHongBao_RandomList, 1)[0]
	with Tra_QiangHongBao_TimeOutReward:
		#出局
		QHB_RoleIDs_Set.discard(roleId)
		#获得
		if rewardType == 2:
			coding, cnt = BigRewardItem
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		else:
			coding, cnt = SmallRewardItem
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		#计数
		role.IncDI8(EnumDayInt8.QiangHongBaoCnt, 1)	
		#状态恢复
		Status.Outstatus(role, EnumInt1.ST_QiangHongBao)
	
	#通知客户端关闭读条
	role.SendObj(QiangHongBao_CountDown_S, 0)
	#获得提示
	role.Msg(2, 0, prompt)


def DoJudge(argv = None, param = None):
	'''
	红包回合判定
	'''
	if not ACTIVE_IS_START:
		return
	
	global QHB_RoleIDs_Set
	if len(QHB_RoleIDs_Set) < 1:
		cComplexServer.RegTick(Round_Seconds, DoJudge)
		return
	
	#筛选出结果 清理本轮参与者
	fightRoleList = Judge(QHB_RoleIDs_Set)
	QHB_RoleIDs_Set.difference_update(set(fightRoleList))
	
	#需要战斗的参与者处理
	fightRoleLen = len(fightRoleList)
	if fightRoleLen > 0:
		leftRoleList = random.sample(fightRoleList, fightRoleLen / 2)
		rightRoleList = list(set(fightRoleList).difference(set(leftRoleList)))
		leftRoleLen = len(leftRoleList)
		rightRoleLen = len(rightRoleList)
		if leftRoleLen != rightRoleLen:
			print "GE_EXC,DoJudge::leftRoleLen(%s) != rightRoleLen(%s)" % (leftRoleLen, rightRoleLen)
		else:
			for i in xrange(leftRoleLen):
				leftRole = cRoleMgr.FindRoleByRoleID(leftRoleList[i])
				rightRole = cRoleMgr.FindRoleByRoleID(rightRoleList[i])
				if not leftRole or not rightRole:
					continue
				#通知客户端关闭读条 注销角色身上TICK
				leftRole.SendObj(QiangHongBao_CountDown_S, 0)
				leftRole.UnregTick(leftRole.GetTI64(EnumTempInt64.QiangHongBaoTickId))	
				Status.Outstatus(leftRole, EnumInt1.ST_QiangHongBao)
				
				rightRole.SendObj(QiangHongBao_CountDown_S, 0)	
				rightRole.UnregTick(rightRole.GetTI64(EnumTempInt64.QiangHongBaoTickId))
				Status.Outstatus(rightRole, EnumInt1.ST_QiangHongBao)	
				
				PVP_QiangHongBao(leftRole, rightRole, EnumGameConfig.QiangHongBao_FIGHT_TYPE, AfterPlay, Afterfight, AfterFightLevel)
	
	#注册下一轮tick
	if ROUND_FLAG:
		cComplexServer.RegTick(Round_Seconds, DoJudge)
	

####################### 战斗 start ##############
def PVP_QiangHongBao(roleA, roleB, ftype, afterplay = None, afterfight = None, afterleave = None, regparam = None):
	'''
	PVP战斗
	@param roleA:
	@param roleB:
	@param ftype:
	@param leave_fun:
	@param backFun:
	@param regparam:
	'''
	# 判断战斗状态互斥
	if Status.IsInStatus(roleA, EnumInt1.ST_FightStatus):
		return
	
	if Status.IsInStatus(roleB, EnumInt1.ST_FightStatus):
		return
	
	#战斗
	fight = Fight.Fight(ftype)
	fight.pvp = True
	#2创建两个阵营
	left, right = fight.create_camp()
	#在阵营中创建战斗单位
	left.create_online_role_unit(roleA, fightData = Middle.GetRoleData(roleA, use_property_X = True), use_px = True)
	right.create_online_role_unit(roleB, fightData = Middle.GetRoleData(roleB, use_property_X = True), use_px = True)
	fight.after_fight_fun = afterfight
	fight.after_play_fun = afterplay
	fight.on_leave_fun = afterleave
	fight.after_fight_param = (roleA, roleB, False)
	fight.after_play_param = (roleA, roleB, False)
	#战斗
	fight.start()
	#============战斗结果============	
	if fight.result is None:
		return
	#活动是否已经结束
	if ACTIVE_IS_START is False:
		return

	win_role = None
	lost_role = None
	if fight.result == -1:#战斗失败
		win_role = roleB
		lost_role = roleA
	else:
		#战斗胜利
		win_role = roleA
		lost_role = roleB
	
	if win_role:#胜利方
		RewardRoleItem(win_role, BigRewardItem)
	if lost_role:#失败方
		RewardRoleItem(lost_role, SmallRewardItem)


def AfterFightLevel(fight, role):
	pass
	
	
def AfterPlay(fight):
	pass

		
def Afterfight(fight):
	pass


#################### 辅助 start #################
def CreateHongBaoNPC():
	'''
	创建红包NPC
	'''
	if not ACTIVE_IS_START:
		return
	
	if not ROUND_FLAG:
		return
	
	npcType, sceneId, posX, posY, posD = Npc_Info
	scene = cSceneMgr.SearchPublicScene(sceneId)
	if not scene:
		print "GE_EXC,CreateHongBaoNPC can not find sceneId:(%s)" % sceneId
		return
	
	#创建npc
	global QHB_NPC_OBJ
	QHB_NPC_OBJ = scene.CreateNPC(npcType, posX, posY, posD, 0)


def DestroyHongBaoNPC():
	'''
	注销红包NPC
	'''
	global Npc_Info
	scene = cSceneMgr.SearchPublicScene(Npc_Info[1])
	if not scene:
		print "GE_EXC, DestroyHongBaoNPC can not find scene"
		return
	
	#删除
	global QHB_NPC_OBJ
	if QHB_NPC_OBJ:
		scene.DestroyNPC(QHB_NPC_OBJ.GetNPCID())
		QHB_NPC_OBJ = None


def Judge(roleIdSet):
	'''
	根据给定角色ID集合  判定并返回参与战斗roleId列表
	'''
	fightRoleList = []
	
	allRoleList = list(roleIdSet)
	allRoleLen = len(allRoleList)
	if allRoleLen >= 4:
		fightRoleList = random.sample(allRoleList, 2 * int(allRoleLen / 4))
	
	return fightRoleList


def RewardRoleItem(role, rewardItem):
	'''
	奖励玩家物品
	'''
	#今日抢红包数量超标
	if role.GetDI8(EnumDayInt8.QiangHongBaoCnt) >= EnumGameConfig.QiangHongBao_MaxCnt:
		print "GE_EXC,QiangHongBaoMgr:: RewardRoleItem rewardCnt overflow role(%s)" % role.GetRoleID()
		return
	
	coding, cnt = rewardItem
	with Tra_QiangHongBao_TimeOutReward:
		role.IncDI8(EnumDayInt8.QiangHongBaoCnt, 1)
		role.AddItem(coding, cnt)
		role.Msg(2, 0, GlobalPrompt.QiangHongBao_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt))


####################### 客户端请求 start  #############
def OnGoToNPCNear(role, msg = None):
	'''
	抢红包_请求去NPC附近
	'''
	if not ACTIVE_IS_START:
		return
	
	if not ROUND_FLAG:
		return
	
	if role.GetLevel() < EnumGameConfig.QiangHongBao_NeedLevel:
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	#传送
	posKey = random.randint(1, len(Npc_NearPoint))
	SceneId, TP_X, TP_Y = Npc_NearPoint.get(posKey)
	role.Revive(SceneId, TP_X, TP_Y)


def OnQiaongHongBao(role, npc):
	'''
	抢红包_请求参与抢红包
	'''
	if not ACTIVE_IS_START:
		return
	
	if not ROUND_FLAG:
		return
	
	if role.GetLevel() < EnumGameConfig.QiangHongBao_NeedLevel:
		return
	
	#是否正在抢红包
	global QHB_RoleIDs_Set
	roleId = role.GetRoleID()
	if roleId in QHB_RoleIDs_Set:
		return
	
	#今日抢红包数量超标
	if role.GetDI8(EnumDayInt8.QiangHongBaoCnt) >= EnumGameConfig.QiangHongBao_MaxCnt:
		return
	
	#是否能进入抢红包状态
	if not Status.CanInStatus(role, EnumInt1.ST_QiangHongBao):
		return
	
	#进入抢红包 注册tick
	Status.ForceInStatus(role, EnumInt1.ST_QiangHongBao)
	QHB_RoleIDs_Set.add(roleId)
	role.SetTI64(EnumTempInt64.QiangHongBaoTickId, role.RegTick(Round_Seconds, QHBTickTock))
	
	#通知客户端读条
	role.SendObj(QiangHongBao_CountDown_S, 1)	


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartQiangHongBao)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndQiangHongBao)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleData)
		Event.RegEvent(Event.Eve_ClientLost, RoleOffLine)
		Event.RegEvent(Event.Eve_BeforeExit, RoleOffLine)
		
		#开抢前广播
		Cron.CronDriveByMinute((2038, 1, 1), OneMinuteBefore, H = "H in (21,)", M = "M == 59")
		Cron.CronDriveByMinute((2038, 1, 1), OneMinuteBefore, H = "H in (10, 12, 15, 17,)", M = "M == 34")
		#开抢		
		Cron.CronDriveByMinute((2038, 1, 1), QiangHongBaoStart, H = "H in (22,)", M = "M == 0")
		Cron.CronDriveByMinute((2038, 1, 1), QiangHongBaoStart, H = "H in (10, 12, 15, 17,)", M = "M == 35")
		#回合结束
		Cron.CronDriveByMinute((2038, 1, 1), QiangHongBaoEnd, H = "H in (22,)", M = "M == 5")
		Cron.CronDriveByMinute((2038, 1, 1), QiangHongBaoEnd, H = "H in (10, 12, 15, 17,)", M = "M == 40")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QiangHongBao_OnGoToNPCNear", "抢红包_请求去NPC附近"), OnGoToNPCNear)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QiangHongBao_OnQiaongHongBao", "抢红包_请求参与抢红包"), OnQiaongHongBao)		