#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Marry.MarryMgr")
#===============================================================================
# 新版结婚系统
#===============================================================================
import time
import random
import datetime
import cRoleMgr
import cProcess
import cDateTime
import cSceneMgr
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumSocial, EnumSysData
from ComplexServer.Log import AutoLog
from World import Define
from Game.Item import ItemMsg
from Game.Role.Obj import Base
from Game.Role.Mail import Mail
from Game.Union import UnionMgr
from Game.NPC import EnumNPCData
from Game.Marry import MarryConfig
from Game.SysData import WorldData
from Game.Role import Call, Event, Status
from Game.Persistence import BigTable, Contain
from Game.Role.Data import EnumInt8, EnumDayInt1, EnumObj, EnumCD, EnumTempObj, \
	EnumInt16, EnumDayInt8, EnumInt1, EnumInt32
from Game.Activity.Title import Title

if "_HasLoad" not in dir():
	#结婚对象的名字
	MarryRoleNameData = AutoMessage.AllotMessage("MarryRoleNameData", "结婚对象名字信息")
	#结婚对象角色ID, 佩戴的订婚戒指道具ID
	MarryObjMsg = AutoMessage.AllotMessage("MarryObjMsg", "结婚对象信息")
	#订婚戒指铭刻信息{订婚戒指道具ID-->铭刻信息}
	MarryRingMsg = AutoMessage.AllotMessage("MarryRingMsg", "订婚戒指铭刻信息")
	#{角色ID-->好友信息}
	MarryCanMsg = AutoMessage.AllotMessage("MarryCanMsg", "可以结婚对象信息")
	#{求婚对象ID:{
		#1:求婚信息--[求婚时间戳,求婚者,求婚对象名字,求婚对象性别, 求婚对象职业,求婚对象品阶,求婚对象等级,求婚类型]}},
		#2:接受求婚信息--[接受求婚的时间戳, 求婚者的名字]
		#3:预约婚礼信息--[预约时间,预约者名字(这个预约的人的是没有的),婚礼档次,时间档]
		#4:拒绝求婚信息--[时间戳, 求婚者名字]
		#5:婚礼开始信息--[婚礼开始时间戳, 对象名字, 婚礼档次]
		#}
	#}
	MarryPropose = AutoMessage.AllotMessage("MarryPropose", "求婚信息")
	#向你求婚的玩家的名字, 求婚表白信息
	MarryGetProposeMsg = AutoMessage.AllotMessage("MarryGetProposeMsg", "收到求婚信息")
	#接受你求婚的玩家的名字
	MarryGetYes = AutoMessage.AllotMessage("MarryGetYes", "收到接受求婚信息")
	#拒绝你求婚的玩家的名字
	MarryGetNo = AutoMessage.AllotMessage("MarryGetNo", "收到拒绝求婚信息")
	#1-宣誓(删), 2-烟花, 3-礼包(删), 4-停止发放礼包(删), 5-播放皇室婚礼特效
	MarryOperator = AutoMessage.AllotMessage("MarryOperator", "婚礼内的操作")
	#[男方ID, 女方ID, 男方名字, 女方名字, 时间档, 烟花数量, 表白次数, 礼包数量, 宣誓次数, 是否发放礼包0-1-0-1, 婚礼档次, 婚礼结束tickID, 婚礼开始tickID]
	MarryXinrenPanel = AutoMessage.AllotMessage("MarryXinrenPanel", "婚礼新人面板信息")
	#{婚礼ID:[男方ID, 女方ID, 男方名字, 女方名字, 时间档, 烟花数量, 表白次数, 礼包数量, 宣誓次数, 是否发放礼包0-1-0-1, 婚礼档次, 婚礼结束tickID, 婚礼开始tickID]}
	MarryNowWeddingList = AutoMessage.AllotMessage("MarryNowWeddingList", "当前婚礼列表")
	#{0-下一个key, 1-收到数量, 2-[送贺礼的玩家ID, 送颗粒的玩家名字], 3-->[送贺礼的玩家ID, 送颗粒的玩家名字], ...}
	MarryReviveHeliMsg = AutoMessage.AllotMessage("MarryReviveHeliMsg", "收到贺礼")
	#请帖	[男方名字, 女方名字, 时间档]
	MarryInvitation = AutoMessage.AllotMessage("MarryInvitation", "皇室婚礼请帖")
	#装备上一个订婚戒指
	Ring_RolePutOn_OK = AutoMessage.AllotMessage("Ring_RolePutOn_OK", "角色成功穿上一个戒指")
	#自己的婚礼ID
	OwnMarryId = AutoMessage.AllotMessage("OwnMarryId", "自己的婚礼ID")
	#宣誓[男方名字, 女方名字]
	MarryVowData = AutoMessage.AllotMessage("MarryVowData", "婚礼宣誓数据")
	
	MarryPropose_Log = AutoLog.AutoTransaction("MarryPropose_Log", "世界告白求婚")
	MarryReservation_Log = AutoLog.AutoTransaction("MarryReservation_Log", "预约婚礼")
	MarryCancel_Log = AutoLog.AutoTransaction("MarryCancel_Log", "取消订婚")
	MarryFinish_Log = AutoLog.AutoTransaction("MarryFinish_Log", "结婚日志")
	MarryDivorce_Log = AutoLog.AutoTransaction("MarryDivorce_Log", "离婚日志")
	MarrySceneBuy_Log = AutoLog.AutoTransaction("MarrySceneBuy_Log", "婚礼内购物")
	MarryLibao_Log = AutoLog.AutoTransaction("MarryLibao_Log", "婚礼领取礼包")
	MarryHeli_Log = AutoLog.AutoTransaction("MarryHeli_Log", "婚礼赠送贺礼")
	MarryReviveHeli_Log = AutoLog.AutoTransaction("MarryReviveHeli_Log", "婚礼收到贺礼")
	MarryRebate_Log = AutoLog.AutoTransaction("MarryRebate_Log", "回赠礼物")
	
	OpenHoneymoon_Log = AutoLog.AutoTransaction("OpenHoneymoon_Log", "开启蜜月")
	FinishHoneymoon_Log = AutoLog.AutoTransaction("FinishHoneymoon_Log", "完成蜜月")
	
	MarryRingOperator_Log = AutoLog.AutoTransaction("MarryRingOperator_Log", "订婚戒指操作")
	
	#下一个可用婚礼ID
	MarryNextUseMaxID = 1001
	
	#{role_id-->{0-nextKey, 1-cnt, 2-[roleId, name], 3-[roleId, name]}}
	MarryReviveHeli_Dict = {}
	
	#当前是否有人在宣誓
	isVow = False
	
	RoyalGuardPos = {17021:[(3552,700,7),(3461,742,7),(3370,784,7),(3278,836,7),(3187,879,7)],
					17022:[(3781,802,3),(3687,848,3),(3596,894,3),(3506,938,3),(3416,985,3)]
					}
	
	RoyalGuardTick = None				#皇室卫队喊话tick
	RoyalGuardSayCnt = 0				#皇室卫队喊话次数
	RoyalGuardNpcDict = {17021:set(), 17022:set()}	#两类npc喊不同的话
	
	#本地缓存竞拍期间离婚记录
	DivorceRecordSet = set()
	
#===============================================================================
# 跨服进程请求
#===============================================================================
def RequestDivorceRecord(param):
	global DivorceRecordSet
	Call.ServerCall(Define.GetDefaultCrossID(), "Game.Marry.MarryParty", "LogicBackDivorceRecord", (cProcess.ProcessID, DivorceRecordSet))
#===============================================================================
# 辅助
#===============================================================================
def CheckBaseStatus(role):
	#结婚判断
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return False
	if role.GetI8(EnumInt8.MarryStatus):
		return False
	return True
	
def CheckTime(role, marryID, timeIndex):
	#时间检测
	timeCfg = MarryConfig.MarryTime_Dict.get(timeIndex)
	if not timeCfg:
		print "GE_EXC, OperatorCheck can not find time index (%s) in MarryTime_Dict" % timeIndex
		return False
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	if nowTime < timeCfg.beginTime or nowTime > timeCfg.endTime:
		return False
	return True
	
def ReturnMarryData(role):
	#返回婚礼ID和婚礼数据
	if role.GetSceneID() != EnumGameConfig.MarrySceneID:
		return None, None
	marryID = role.GetObj(EnumObj.MarryObj).get(5)
	if not marryID:
		return None, None
	global MarryID_Dict
	if marryID not in MarryID_Dict:
		print "GE_EXC, RequestUnburden can not find marryID (%s) in MarryID_Dict" % marryID
		return None, None
	
	return marryID, MarryID_Dict[marryID]

def ReturnUnionName(role):
	#返回公会名字
	unionObj = role.GetUnionObj()
	if unionObj:
		return unionObj.name
	else:
		return None
	
def GetMarryRoleName(role):
	#返回结婚对象名字
	if Environment.IsCross:
		return
	if not role.GetObj(EnumObj.MarryObj):
		return
	marryRoleID = role.GetObj(EnumObj.MarryObj)[1]
	if not marryRoleID:
		return None
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleID)
	if not marryRole:
		#不在线查表
		from Game.RoleView import RoleView
		if not RoleView.RoleView_BT.returnDB:
			return None
		rD = RoleView.RoleView_BT.GetData().get(marryRoleID)
		if not rD:
			return None
		viewData = rD.get("viewData")
		if not viewData:
			return None
		return viewData[1][EnumSocial.RoleNameKey]
	else:
		return marryRole.GetRoleName()
	
def AcceptMarry(role, marryObj, proposeRoleID):
	#接受求婚
	#获取结婚对象
	marryRole = cRoleMgr.FindRoleByRoleID(proposeRoleID)
	
	#对方不在线
	if not marryRole:
		role.Msg(2, 0, GlobalPrompt.MarryAcceptNotLine)
		return
	if marryRole.GetI8(EnumInt8.MarryStatus):
		#求婚对象已订婚或结婚
		#删除求婚信息
		del marryObj[2][proposeRoleID]
		if proposeRoleID in marryObj[4]:
			marryObj[4].remove(proposeRoleID)
		role.SetObj(EnumObj.MarryObj, marryObj)
		#同步自己的求婚信息
		role.SendObj(MarryPropose, marryObj[2])
		role.Msg(2, 0, GlobalPrompt.MarryAcceptMarried % marryRole.GetRoleName())
		return
	
	girlID,girlName,boyName,nowTime = role.GetRoleID(),role.GetRoleName(),marryRole.GetRoleName(),cDateTime.Seconds()
	
	#设置对象ID
	marryObj[1] = proposeRoleID
	#接受求婚信息
	marryObj[3] = PackAnswerData(marryRole)
	#接受者
	del marryObj[2][proposeRoleID][1]
	marryObj[2][proposeRoleID][2] = [nowTime, boyName,1]
	#这里不删除记录求婚先后顺序的列表
	
	role.SetObj(EnumObj.MarryObj, marryObj)
	role.SendObj(MarryPropose, marryObj[2])
	#通知自己
	role.SendObj(MarryGetYes, (1,boyName))
	
	#通知求婚者求婚被接受
	marryRole.SendObj(MarryGetYes, (2, role.GetRoleName()))
	
	#设置求婚者订婚对象信息
	marryObj = marryRole.GetObj(EnumObj.MarryObj)
	marryObj[1] = role.GetRoleID()
	#被接受者
	if girlID in marryObj[2]:
		del marryObj[2][girlID][1]
		marryObj[2][girlID][2] = [nowTime, girlName,2]
	marryObj[3] = PackAnswerData(role)
	marryRole.SetObj(EnumObj.MarryObj, marryObj)
	marryRole.SendObj(MarryPropose, marryObj[2])
	
	#设置双方订婚状态
	role.SetI8(EnumInt8.MarryStatus, 1)
	marryRole.SetI8(EnumInt8.MarryStatus, 1)
	
def RefusalMarry(role, marryObj, proposeRoleID):
	#拒绝求婚
	proposeMsg = marryObj[2][proposeRoleID].get(1)
	if not proposeMsg:
		return
	
	boyName,girlName = proposeMsg[2],role.GetRoleName()
	
	#删除求婚请求
	del marryObj[2][proposeRoleID][1]
	#拒绝者
	marryObj[2][proposeRoleID][4] = [cDateTime.Seconds(), boyName,1]
	role.SetObj(EnumObj.MarryObj, marryObj)
	role.SendObj(MarryPropose, marryObj[2])
	
	Call.LocalDBCall(proposeRoleID, CallRefusal, (role.GetRoleID(), role.GetRoleName(), cDateTime.Seconds()))
	#通知求婚被拒绝
	proposeRole = cRoleMgr.FindRoleByRoleID(proposeRoleID)
	if not proposeRole:
		return
	
	#如果不是未婚状态, 什么都不做
	if proposeRole.GetI8(EnumInt8.MarryStatus):
		return
	proposeRole.SendObj(MarryGetNo, girlName)
	
def BeginWedding(argv, regparam):
	#婚礼开始
	marryID, roleName, roleID, marryRoleName, marryRoleID, gradeIndex = regparam
	
	global MarryID_Dict
	if not MarryID_Dict.returnDB:
		print 'GE_EXC, BeginWedding MarryID_Dict not return db, marryId:%s, marry role id:(%s, %s)' % (marryID, roleID, marryRoleID)
		return
	if marryID not in MarryID_Dict:
		print "GE_EXC, BeginWedding begin wedding (%s) error" % marryID
		return
	
	#婚礼开始就设置双方结婚状态 -- 4(婚礼开始状态)
	Call.LocalDBCall(roleID, SetMarryStatus, 4)
	Call.LocalDBCall(marryRoleID, SetMarryStatus, 4)
	
	#皇室婚礼创建皇家卫队
	if gradeIndex == 3:
		CreateRoyalGuard(roleName, marryRoleName)
	
	bRole = cRoleMgr.FindRoleByRoleID(roleID)
	if bRole:
		#在线的话提示
		bRole.Msg(1, 0, GlobalPrompt.MarryBeginInform % (marryRoleName, marryID))
	
	gRole = cRoleMgr.FindRoleByRoleID(marryRoleID)
	if gRole:
		#在线的话提示
		gRole.Msg(1, 0, GlobalPrompt.MarryBeginInform % (roleName, marryID))
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryBeginInformB % (roleName, marryRoleName, marryID))
	
def CreateRoyalGuard(bRoleName, gRoleName):
	#创建皇家卫队
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.MarrySceneID)
	if not scene:
		print 'GE_EXC, Marry CreateRoyalGuard can not find scene'
		return
	global RoyalGuardPos, RoyalGuardTick, RoyalGuardNpcDict
	SCN = scene.CreateNPC
	for npcType, pos in RoyalGuardPos.iteritems():
		for posX, posY, direct in pos:
			npc = SCN(npcType, posX, posY, direct, 0)
			RoyalGuardNpcDict[npcType].add(npc)
	
	RoyalGuardTick = cComplexServer.RegTick(60, RoyalGuardSay, None)
	
def RoyalGuardSay(argv, param):
	#喊话
	global RoyalGuardTick, RoyalGuardSayCnt, RoyalGuardNpcDict
	RoyalGuardSayCnt += 1
	#根据喊话次数获取随机的喊话索引
	cfg = MarryConfig.RoyalGuardSayRandom_Dict.get(RoyalGuardSayCnt)
	if not cfg:
		return
	sayIndex = random.choice(cfg.randomList)
	#喊话索引获取喊话内容
	sayCfg = MarryConfig.RoyalGuardSay_Dict.get(sayIndex)
	if not sayCfg:
		return
	#喊话
	for npcSet in RoyalGuardNpcDict.values():
		sayIndex = random.choice(cfg.randomList)
		#喊话索引获取喊话内容
		sayCfg = MarryConfig.RoyalGuardSay_Dict.get(sayIndex)
		if not sayCfg:
			continue
		for npc in npcSet:
			npc.SetPySyncDict(EnumNPCData.EnNPC_Say, sayCfg.sayContent)
			npc.AfterChange()
	
	#注册取消喊话tick
	cComplexServer.RegTick(10, ClearSay, None)
	
	#注册下一次喊话
	RoyalGuardTick = cComplexServer.RegTick(60, RoyalGuardSay, None)
	
def ClearSay(argv, param):
	global RoyalGuardNpcDict
	for npcSet in RoyalGuardNpcDict.values():
		for npc in npcSet:
			#不说话
			npc.SetPySyncDict(EnumNPCData.EnNPC_Say, None)
			npc.AfterChange()
	
def EndWedding(argv, regparam):
	#婚礼结束
	marryID, roleName, roleID, marryRoleName, marryRoleID = regparam
	
	endSec = cDateTime.Seconds()
	
	#处理皇室婚礼
	global RoyalGuardTick, RoyalGuardNpcDict, RoyalGuardSayCnt
	if RoyalGuardTick:
		cComplexServer.UnregTick(RoyalGuardTick)
		RoyalGuardTick = None
	if RoyalGuardNpcDict:
		for npcSet in RoyalGuardNpcDict.values():
			for npc in npcSet:
				npc.Destroy()
	RoyalGuardSayCnt = 0
	RoyalGuardNpcDict = {17021:set(), 17022:set()}
	
	#婚礼结束删除赠送贺礼信息
	global MarryReviveHeli_Dict
	if roleID in MarryReviveHeli_Dict:
		del MarryReviveHeli_Dict[roleID]
	if marryRoleID in MarryReviveHeli_Dict:
		del MarryReviveHeli_Dict[marryRoleID]
	
	global MarryID_Dict
	if not MarryID_Dict.returnDB:
		print 'GE_EXC, EndWedding MarryID_Dict not return db, marryId:%s, marry role id:(%s, %s)' % (marryID, roleID, marryRoleID)
	if marryID not in MarryID_Dict:
		print "GE_EXC, EndWedding close marry ID (%s) error" % marryID
		return
	
	gradeIndex = MarryID_Dict[marryID][10]
	
	#这里再读取配置表获取婚礼档次配置
	gradeCfg = MarryConfig.MarryGrade_Dict.get(gradeIndex)
	if not gradeCfg:
		print 'GE_EXC, EndWedding can not find wedding grade index %s' % gradeIndex
		return
	
	#服务器结婚对数+1
	WorldData.WD[EnumSysData.MarryCnt] += 1
	
	Call.LocalDBCall(roleID, FinishWedding, (endSec, marryRoleID, marryRoleName, gradeIndex, WorldData.WD[EnumSysData.MarryCnt]))
	Call.LocalDBCall(marryRoleID, FinishWedding, (endSec, roleID, roleName, gradeIndex, WorldData.WD[EnumSysData.MarryCnt]))
	
	#删除婚礼数据
	del MarryID_Dict[marryID]
	MarryID_Dict.changeFlag = True
	
	global DivorceRecordSet
	DivorceRecordSet.discard(roleID)
	DivorceRecordSet.discard(marryRoleID)
	
	with MarryFinish_Log:
		#邮件奖励
		Mail.SendMail(roleID, GlobalPrompt.MarryFinisMail_Title, GlobalPrompt.MarryFinisMail_Sender, GlobalPrompt.MarryFinisMail_Content % (marryRoleName, gradeCfg.itemReward, 1), [(gradeCfg.itemReward, 1)])
		Mail.SendMail(marryRoleID, GlobalPrompt.MarryFinisMail_Title, GlobalPrompt.MarryFinisMail_Sender, GlobalPrompt.MarryFinisMail_Content % (roleName, gradeCfg.itemReward, 1), [(gradeCfg.itemReward, 1)])
		
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveMarryFinish, (roleID, marryRoleID))
	
	#同步最新的婚礼数据
	cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
	cRoleMgr.BroadMsg()
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryVow % (roleName, marryRoleName, WorldData.WD[EnumSysData.MarryCnt]))

def SendUnionMail(unionObj, roleName, marryRoleName, nowDay, beginTime, mailContent):
	#公会邀请邮件
	for role_id in unionObj.members.iterkeys():
		Mail.SendMail(role_id,GlobalPrompt.MarryInvite_Title,GlobalPrompt.MarryInvite_Sender,mailContent % (roleName, marryRoleName, nowDay, beginTime[0], beginTime[1]))
	
def PackProposeData(role, nowSec, isPropose, proposeType):
	#打包求婚数据
	#[时间,(求婚-1, 被求婚-2),名字,性别,职业,进阶,等级,告白类型(1-悄悄的,2-世界)]
	return [nowSec,isPropose,role.GetRoleName(),role.GetSex(),role.GetCareer(),role.GetGrade(),role.GetLevel(),proposeType]

def PackAnswerData(role):
	#打包答应求婚是的数据
	return [role.GetRoleID(),role.GetRoleName(),role.GetUnionID(),ReturnUnionName(role),role.GetZDL(),role.GetI16(EnumInt16.WeddingRingID)]

def PackWeddingData(role, marryRoleID, marryRoleName, timeIndex, gradeCfg, gradeIndex, endTickID, beginTickID):
	#打包婚礼数据
	if role.GetSex() == 1:
		return [role.GetRoleID(),marryRoleID,role.GetRoleName(),marryRoleName,timeIndex,gradeCfg.yanhuaCnt,gradeCfg.biaobaiCnt,gradeCfg.libaoCnt,1,4,gradeIndex,endTickID,beginTickID]
	else:
		return [marryRoleID, role.GetRoleID(),marryRoleName, role.GetRoleName(),timeIndex,gradeCfg.yanhuaCnt,gradeCfg.biaobaiCnt,gradeCfg.libaoCnt,1,4,gradeIndex,endTickID,beginTickID]
	
def Invite(role):
	#返回邀请数据--男方名字, 女方名字, 婚礼ID
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	
	bRoleID,gRoleID,bRoleName,gRoleName,timeIndex,_,_,_,_,_,_,_,_ = marryData
	roleID = role.GetRoleID()
	
	#不是新郎新娘
	if roleID not in (bRoleID, gRoleID):
		return
	#时间检测
	if not CheckTime(role, marryID, timeIndex):
		return
	#CD中
	if role.GetCD(EnumCD.MarryInviteCD):
		return
	
	#获得CD
	role.SetCD(EnumCD.MarryInviteCD, EnumGameConfig.MarryInviteCD)
	
	return bRoleName, gRoleName, marryID
	
def SendHeli(marryID, bRoleID, gRoleID, roleName):
	#赠送贺礼
	global MarryReviveHeli_Dict
	
	bRole = cRoleMgr.FindRoleByRoleID(bRoleID)
	if not bRole:
		Mail.SendMail(bRoleID, GlobalPrompt.MarryHandsel_Title, roleName, GlobalPrompt.MarryHandsel_Content % roleName, [(EnumGameConfig.MarryHongbaoCoding, 1)])
	else:
		isSendMsg, msg = MarryReviveHeli_Dict[bRoleID][1], MarryReviveHeli_Dict[bRoleID]
		bRole.AddItem(EnumGameConfig.MarryHongbaoCoding, 1)
		if bRole.GetSceneID() == EnumGameConfig.MarrySceneID and isSendMsg:
			bRole.SendObj(MarryReviveHeliMsg, msg)
		bRole.Msg(2, 0, GlobalPrompt.MarryReviveHeli % roleName)
	
	gRole = cRoleMgr.FindRoleByRoleID(gRoleID)
	if not gRole:
		Mail.SendMail(gRoleID, GlobalPrompt.MarryHandsel_Title, roleName, GlobalPrompt.MarryHandsel_Content % roleName, [(EnumGameConfig.MarryHongbaoCoding, 1)])
	else:
		isSendMsg, msg = MarryReviveHeli_Dict[gRoleID][1], MarryReviveHeli_Dict[gRoleID]
		gRole.AddItem(EnumGameConfig.MarryHongbaoCoding, 1)
		if gRole.GetSceneID() == EnumGameConfig.MarrySceneID and isSendMsg:
			gRole.SendObj(MarryReviveHeliMsg, msg)
		gRole.Msg(2, 0, GlobalPrompt.MarryReviveHeli % roleName)
	
def ReviveHeliDict(roleId, roleName, bRoleId, gRoleId):
	#收到贺礼
	global MarryReviveHeli_Dict
	
	if bRoleId not in MarryReviveHeli_Dict:
		MarryReviveHeli_Dict[bRoleId] = {0:2, 1:1, 2:[roleId, roleName]}
	else:
		MarryReviveHeli_Dict[bRoleId][0] += 1
		nextKey = MarryReviveHeli_Dict[bRoleId][0]
		MarryReviveHeli_Dict[bRoleId][1] += 1
		MarryReviveHeli_Dict[bRoleId][nextKey] = [roleId, roleName]
	
	if gRoleId not in MarryReviveHeli_Dict:
		MarryReviveHeli_Dict[gRoleId] = {0:2, 1:1, 2:[roleId, roleName]}
	else:
		MarryReviveHeli_Dict[gRoleId][0] += 1
		nextKey = MarryReviveHeli_Dict[gRoleId][0]
		MarryReviveHeli_Dict[gRoleId][1] += 1
		MarryReviveHeli_Dict[gRoleId][nextKey] = [roleId, roleName]
	
def IsHostParty(role, ownId, marryId):
	#是否在举办派对
	if role.GetSex() == 1:
		manId = ownId
		womenId = marryId
	else:
		manId = marryId
		womenId = ownId
	
	from Game.Marry import MarryParty
	if not MarryParty.MarryPartyDict.returnDB:
		return False
	
	if (manId, womenId) in MarryParty.MarryPartyDict[1]:
		return False
	
	return True
	
def CancelSkill(role):
	#取消夫妻技能
	skillSet = role.GetObj(EnumObj.WeddingRingStarObj)[3]
	
	for skillID in MarryConfig.WeddingGradeAct_Dict.iterkeys():
		if skillID not in skillSet:
			continue
		skillSet.discard(skillID)
	
	#取消双方婚戒ID激活的夫妻技能
	for skillID in MarryConfig.WeddingIDAct_Dict.iterkeys():
		if skillID not in skillSet:
			continue
		skillSet.discard(skillID)
	
	role.GetObj(EnumObj.WeddingRingStarObj)[3] = skillSet
	
	role.ResetGlobalWeddingRingSkillProperty()
	
	from Game.Marry import WeddingRing
	role.SendObj(WeddingRing.WeddingSkill, skillSet)
	
def CancelTitle(role):
	#取消结婚称号
	titleDict = role.GetObj(EnumObj.Title).get(1)
	nowSecs = cDateTime.Days()
	
	for titleId in MarryConfig.QinmiTitleSet:
		if titleId not in titleDict:
			continue
		titleDict[titleId][0] = nowSecs
	
	if EnumGameConfig.PartyKuafuTitleID in titleDict:
		titleDict[EnumGameConfig.PartyKuafuTitleID][0] = nowSecs
	
	Title.CheckTitleTimeOut(role)
	
def SyncXinren(xinrenIDList, msg):
	#同步新人面板
	for role_id in xinrenIDList:
		role = cRoleMgr.FindRoleByRoleID(role_id)
		if not role:
			continue
		if role.GetSceneID() != EnumGameConfig.MarrySceneID:
			continue
		role.SendObj(MarryXinrenPanel, msg)
	
def InitImprintData(role, roleId, marryRoleId, otherRoleRingId):
	#缓存订婚戒指铭刻信息
	global RING_BT
	if not RING_BT.returnDB:
		role.GetTempObj(EnumTempObj.MarryRingImprintMsg, {})
		return
	
	#自己的婚戒铭刻信息
	ringData = RING_BT.GetData().get(roleId, {})
	ringMsg = {}
	if ringData:
		ringMsg = ringData.get('ringData')
	if otherRoleRingId:
		#如果对象当前有佩戴订婚戒指, 获取对象的订婚戒指信息
		otherRoleRingData = RING_BT.GetData().get(marryRoleId)
		if otherRoleRingData and otherRoleRingData['ringData']:
			#获取当前佩戴的订婚戒指铭刻信息
			otherRingMsg = otherRoleRingData['ringData'].get(otherRoleRingId)
			if otherRingMsg:
				#加入所有订婚戒指铭刻信息
				ringMsg[otherRoleRingId] = otherRingMsg
		
	role.SetTempObj(EnumTempObj.MarryRingImprintMsg, ringMsg)
	
def FinishVow(argv, param):
	#结束宣誓
	global isVow
	isVow = False
#===============================================================================
# 离线命令
#===============================================================================
def SetMarryStatus(role, param):
	role.SetI8(EnumInt8.MarryStatus, param)
	
def SetHoneymoonGrade(role, param):
	beginSec, status = param
	
	if (cDateTime.Seconds() - beginSec) > 300:
		return
	role.SetI8(EnumInt8.HoneymoonStatus, status)
	
def SendHoneymoonQinmi(role, param):
	cfg = MarryConfig.HoneymoonGrade_Dict.get(param)
	if not cfg:
		print 'GE_EXC, Marry SendHoneymoonQinmi can not find %s honeymoon grade' % param
		return
	with FinishHoneymoon_Log:
		role.IncI32(EnumInt32.Qinmi, cfg.qinmi)
	
def SetHoneymoonFinish(role, param):
	endSec, marryRoleID, marryRoleName, grade = param
	if role.GetObj(EnumObj.MarryObj)[1] != marryRoleID:
		return
	role.SetI8(EnumInt8.HoneymoonStatus, 3)
	if marryRoleID in role.GetObj(EnumObj.MarryObj)[2]:
		role.GetObj(EnumObj.MarryObj)[2][marryRoleID][6] = [endSec, marryRoleName, grade]
	
def CancelPropose(role, param):
	role.SetI8(EnumInt8.MarryStatus, 0)
	role.GetObj(EnumObj.MarryObj)[1] = 0
	role.GetObj(EnumObj.MarryObj)[3] = []
	role.GetObj(EnumObj.MarryObj)[5] = 0
	
def FinishWedding(role, param):
	#完成婚礼
	endSec, marryRoleId, marryRoleName, gradeIndex, cnt = param
	
	#设置结婚状态
	role.SetI8(EnumInt8.MarryStatus, 3)
	#清理婚礼ID
	role.GetObj(EnumObj.MarryObj)[5] = 0
	if marryRoleId in role.GetObj(EnumObj.MarryObj)[2]:
		role.GetObj(EnumObj.MarryObj)[2][marryRoleId][7] = [endSec, marryRoleName, cnt]
	
	#重新获取婚礼档次配置
	cfg = MarryConfig.MarryGrade_Dict.get(gradeIndex)
	if not cfg:
		print "GE_EXC, FinishWedding can not find gradeIndex (%s) in MarryGrade_Dict" % gradeIndex
		return
	if cfg.skillID:
		#获得夫妻技能
		role.GetObj(EnumObj.WeddingRingStarObj)[3].add(cfg.skillID)
		#重算夫妻技能属性
		role.ResetGlobalWeddingRingSkillProperty()
		
		from Game.Marry import WeddingRing
		role.SendObj(WeddingRing.WeddingSkill, role.GetObj(EnumObj.WeddingRingStarObj)[3])
	
	#激活婚戒系统
	role.ActiveWeddingRing()
	
	#重算订婚戒指属性
	role.ResetMarryRingProperty()
	
	#在跨服的话后面的都不做了
	if Environment.IsCross:
		return
	
	#尝试激活结婚亲密称号
	from Game.Marry import MarryQinmi
	if MarryQinmi.QinmiLevelDict.returnDB:
		roleId = role.GetRoleID()
		
		ownGrade = role.GetI8(EnumInt8.QinmiGrade)
		
		#这里如果没有记录的话需要记录, 如果不记录而玩家一直不下线的话, 结婚对象的称号会有问题
		if roleId not in MarryQinmi.QinmiLevelDict:
			MarryQinmi.QinmiLevelDict[roleId] = ownGrade
			MarryQinmi.QinmiLevelDict.changeFlag = True
		
		marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
		if marryRole:
			marryGrade = marryRole.GetI8(EnumInt8.QinmiGrade)
		else:
			marryGrade = MarryQinmi.QinmiLevelDict.get(marryRoleId, 0)
		
		minGrade = min(ownGrade, marryGrade)
		if minGrade:
			MarryQinmi.TryActQinmiTitle(role, minGrade)
	
	#本服的话在这里更新记录的最高记录
	#如果是跨服的话, 不处理, 会在回本服的时候更新订婚戒指的最高记录
	
	#如果当前佩戴了戒指的话, 将数据加入持久化字典, 并设置对象订婚戒指信息
	ringIdSet = role.GetObj(EnumObj.En_RoleRing)
	if ringIdSet:
		for ringId in ringIdSet:
			break
		#订婚戒指管理器
		ringMgr = role.GetTempObj(EnumTempObj.enRoleRingMgr)
		ring= ringMgr.FindProp(ringId)
		if not ring :
			print 'GE_EXC, MarryMgr FinishWedding can not find ring by role:%s' % role.GetRoleID()
			return
		roleId = role.GetRoleID()
		global MarryRing_Dict
		if not MarryRing_Dict.returnDB:
			print 'GE_EXC, MarryMgr FinishWedding error by role:%s' % roleId
			return
		isImprint = ring.IsImprint()
		if isImprint:
			MarryRing_Dict[roleId] = [ring.otype, ring.otype]
		else:
			MarryRing_Dict[roleId] = [ring.otype, 0]
		MarryRing_Dict.changeFlag = True
		
		marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
		if marryRole:
			if isImprint:
				marryRole.GetObj(EnumObj.MarryObj)[6] = [ring.otype, ring.otype]
			else:
				marryRole.GetObj(EnumObj.MarryObj)[6] = [ring.otype, 0]
			#重算对象订婚戒指属性
			marryRole.ResetMarryRingProperty()
	
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	#触发改变结婚对象名字
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, role)
	
	#北美通用活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.FinishMarry()
	
def Reservation(role, param):
	#预约婚礼
	roleID, roleName, gradeIndex, timeIndex, _, nowSeconds = param
	
	role.SetI8(EnumInt8.MarryStatus, 2)
	marryObj = role.GetObj(EnumObj.MarryObj)
	if roleID not in marryObj[2]:
		marryObj[2][roleID] = {3: [nowSeconds, roleName, gradeIndex, timeIndex]}
	else:
		marryObj[2][roleID][3] = [nowSeconds, roleName, gradeIndex, timeIndex]
	marryObj[5] = MarryNextUseMaxID
	role.SetObj(EnumObj.MarryObj, marryObj)
	role.SendObj(MarryPropose, marryObj[2])
	
	if Environment.IsCross:
		#跨服的话后面的不用做了
		return
	
	global MarryID_Dict
	if MarryID_Dict.returnDB:
		#这里有可能预约的婚礼已经完成,婚礼信息已经被删除
		if not MarryNextUseMaxID:
			return
		marryData = MarryID_Dict.get(MarryNextUseMaxID)
		if not marryData:
			return
		if roleID not in (marryData[0], marryData[1]):
			#不是自己的婚礼
			return
		role.SendObj(MarryXinrenPanel, MarryID_Dict[MarryNextUseMaxID])
		role.SendObj(OwnMarryId, MarryNextUseMaxID)
	
def DivorceExEx(role, param):
	marryRoleId, marryRoleName, days = param
	
	#结婚对象ID不一致, 该离线命令不执行
	if marryRoleId != role.GetObj(EnumObj.MarryObj)[1]:
		return
	#设置结婚状态
	role.SetI8(EnumInt8.MarryStatus, 0)
	#设置蜜月状态
	role.SetI8(EnumInt8.HoneymoonStatus, 0)
	#取消结婚对象ID
	role.GetObj(EnumObj.MarryObj)[1] = 0
	#清理对象的订婚戒指信息
	if 6 in role.GetObj(EnumObj.MarryObj):
		role.GetObj(EnumObj.MarryObj)[6] = []
	
	#清理记录的最高订婚戒指数据
	if not Environment.IsCross:
		#跨服的话不处理, 等回本服后处理
		roleId = role.GetRoleID()
		global MarryRing_Dict
		if MarryRing_Dict.returnDB and (roleId in MarryRing_Dict):
			del MarryRing_Dict[roleId]
			MarryRing_Dict.changeFlag = True
	
	if days == cDateTime.Days():
		role.SetDI1(EnumDayInt1.IsDivorce, True)
	
	#重算订婚戒指属性
	role.ResetMarryRingProperty()
	
	#取消用夫妻双方婚戒ID激活的技能
	CancelSkill(role)
	CancelTitle(role)
	
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	
	#触发改变结婚对象名字
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, role)
	
	role.Msg(2, 0, GlobalPrompt.MarryDivorce_1 % marryRoleName)
	
def CallRefusal(role, param):
	refusalRoleId, refusalRoleName, refusalSec = param
	
	if refusalRoleId not in role.GetObj(EnumObj.MarryObj)[2]:
		return
	del role.GetObj(EnumObj.MarryObj)[2][refusalRoleId][1]
	role.GetObj(EnumObj.MarryObj)[2][refusalRoleId][4] = [refusalSec, refusalRoleName,2]
#===============================================================================
# 之前的离线命令
#===============================================================================
def FinishMarry(role, param):
	'''
	完成婚礼-- 之前的离线命令函数, 不要删
	@param role:
	@param param:
	'''
	marryRoleID = param
	
	role.SetI8(EnumInt8.MarryStatus, 3)
	role.GetObj(EnumObj.MarryObj)[1] = marryRoleID
	role.GetObj(EnumObj.MarryObj)[3] = []
	role.GetObj(EnumObj.MarryObj)[5] = 0
	
	#激活婚戒系统
	role.ActiveWeddingRing()
	
	if role.GetSceneID() != EnumGameConfig.MarrySceneID:
		return
	
	role.BackPublicScene()
	
def FinishMarryEx(role, param):
	'''
	完成婚礼
	@param role:
	@param param:
	'''
	gradeIndex, marryRoleID = param
	
	role.SetI8(EnumInt8.MarryStatus, 3)
	role.GetObj(EnumObj.MarryObj)[1] = marryRoleID
	role.GetObj(EnumObj.MarryObj)[3] = []
	role.GetObj(EnumObj.MarryObj)[5] = 0
	
	cfg = MarryConfig.MarryGrade_Dict.get(gradeIndex)
	if not cfg:
		print "GE_EXC, FinishMarryEx can not find gradeIndex (%s) in MarryGrade_Dict" % gradeIndex
		return
	if cfg.skillID:
		#获得夫妻技能
		role.GetObj(EnumObj.WeddingRingStarObj)[3].add(cfg.skillID)
		#重算夫妻技能属性
		role.ResetGlobalWeddingRingSkillProperty()
		
		from Game.Marry import WeddingRing
		role.SendObj(WeddingRing.WeddingSkill, role.GetObj(EnumObj.WeddingRingStarObj)[3])
	
	#激活婚戒系统
	role.ActiveWeddingRing()
	
	#在跨服的话后面的都不做了
	if Environment.IsCross:
		return
	
	if role.GetSceneID() == EnumGameConfig.MarrySceneID:
		role.BackPublicScene()
	
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	#触发改变结婚对象名字
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, role)
	
	#北美通用活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.FinishMarry()
	
def Divorce(role, param):
	'''
	离婚 -- 之前的离线命令函数, 不要删
	@param role:
	@param param:
	'''
	role.SetI8(EnumInt8.MarryStatus, 0)
	role.GetObj(EnumObj.MarryObj)[1] = 0
	
	#取消用夫妻双方婚戒ID激活的技能
	CancelSkill(role)
	CancelTitle(role)
	
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	#触发改变结婚对象名字
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, role)
	
	role.Msg(2, 0, GlobalPrompt.MarryDivorce_1 % param)
	
def DivorceEx(role, param):
	'''
	离婚(之前的离线命令函数, 不要删)
	@param role:
	@param param:
	'''
	marryRoleName, days = param
	
	role.SetI8(EnumInt8.MarryStatus, 0)
	role.GetObj(EnumObj.MarryObj)[1] = 0
	
	if days == cDateTime.Days():
		role.SetDI1(EnumDayInt1.IsDivorce, True)
	
	#取消用夫妻双方婚戒ID激活的技能
	CancelSkill(role)
	CancelTitle(role)
	
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	#触发改变结婚对象名字
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, role)
	
	role.Msg(2, 0, GlobalPrompt.MarryDivorce_1 % marryRoleName)
	
#===============================================================================
# 事件
#===============================================================================
def AfterLogin(role, param):
	#跨服不用触发
	if not role.GetObj(EnumObj.MarryObj):
		#{1:求婚对象ID, 2:求婚对象信息, 3:订婚信息, 4:求婚对象ID列表(按时间顺序排序), 5:婚礼ID, 6:[结婚对象最高级订婚戒指coding, 是否铭刻]}
		role.SetObj(EnumObj.MarryObj, {1:0, 2:{}, 3:[], 4:[], 5:0, 6:[]})
	if not role.GetObj(EnumObj.En_RoleRing):
		#初始化订婚戒指集合
		role.SetObj(EnumObj.En_RoleRing, set())
	
	#初始化铭刻信息
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	InitImprintData(role, role.GetRoleID(), marryRoleId, ReturnRingId(marryRoleId))
	#上线后尝试激活夫妻技能
	TryActRingPro(role)
	
	global MarryRing_Dict
	if role.GetI8(EnumInt8.MarryStatus) == 3:
		#这里更新订婚戒指的最高记录
		#因为可能可能之前在跨服没有记录
		ringIdSet = role.GetObj(EnumObj.En_RoleRing)
		if not ringIdSet:
			return
		for ringId in ringIdSet:
			break
		#订婚戒指管理器
		ringMgr = role.GetTempObj(EnumTempObj.enRoleRingMgr)
		ring= ringMgr.FindProp(ringId)
		if not ring :
			print 'GE_EXC, MarryMgr AfterLogin can not find ring by role:%s' % role.GetRoleID()
			return
		roleId = role.GetRoleID()
		if not MarryRing_Dict.returnDB:
			print 'GE_EXC, MarryMgr AfterLogin error by role:%s' % roleId
			return
		if roleId in MarryRing_Dict:
			#已经记录了
			return
		
		isImprint = ring.IsImprint()
		if isImprint:
			MarryRing_Dict[roleId] = [ring.otype, ring.otype]
		else:
			MarryRing_Dict[roleId] = [ring.otype, 0]
		MarryRing_Dict.changeFlag = True
	else:
		#如果离婚了, 尝试清理订婚戒指信息
		roleId = role.GetRoleID()
		if MarryRing_Dict.returnDB and (roleId in MarryRing_Dict):
			del MarryRing_Dict[roleId]
			MarryRing_Dict.changeFlag = True
	
def SyncRoleOtherData(role, param):
	#同步婚礼数据
	global MarryID_Dict
	role.SendObj(MarryNowWeddingList, MarryID_Dict.data)
	
	marryId = role.GetObj(EnumObj.MarryObj).get(5)
	if marryId:
		role.SendObj(MarryXinrenPanel, MarryID_Dict.get(marryId))
	
	role.SendObj(OwnMarryId, marryId)
	
	#同步自己的结婚对象名字
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	#同步订婚戒指铭刻信息
	role.SendObj(MarryRingMsg, role.GetTempObj(EnumTempObj.MarryRingImprintMsg))
	
	#同步请求结婚信息
	proposeMsgData = role.GetObj(EnumObj.MarryObj).get(2)
	if proposeMsgData:
		for roleId, role_data in proposeMsgData.iteritems():
			if 1 not in role_data:
				continue
			if role_data[1][1] == 1:
				continue
			role.SendObj(MarryGetProposeMsg, (roleId, role_data[1][2], GlobalPrompt.MarryRequestTips))
	
def AfterChangeSex(role, param):
	#变性后清理求婚信息
	role.GetObj(EnumObj.MarryObj)[2] = {}
	
def AfterChangeName(role, param):
	#改名后需要处理铭刻数据
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	
	global RING_BT
	if not RING_BT.returnDB: return
	
	ringBigData = RING_BT.GetData()
	for ringKey, ringData in ringBigData.iteritems():
		for _, imprintData in ringData['ringData'].iteritems():
			if roleId != imprintData[0]:
				continue
			imprintData[1] = roleName
		RING_BT.HasChangeKey(ringKey)
	
	#修改自己缓存的铭刻信息
	if role.GetTempObj(EnumTempObj.MarryRingImprintMsg):
		for ringImprintData in role.GetTempObj(EnumTempObj.MarryRingImprintMsg).itervalues():
			if roleId == ringImprintData[0]:
				ringImprintData[1] = roleName
	
	marryRoleID = role.GetObj(EnumObj.MarryObj)[1]
	if not marryRoleID:
		return
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleID)
	if not marryRole:
		return
	marryRole.SendObj(MarryRoleNameData, roleName)
	
	#修改对象缓存的铭刻信息
	if marryRole.GetTempObj(EnumTempObj.MarryRingImprintMsg):
		for ringImprintData in marryRole.GetTempObj(EnumTempObj.MarryRingImprintMsg).itervalues():
			if roleId == ringImprintData[0]:
				ringImprintData[1] = roleName
	
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, marryRole)
	
def AfterNewDay():
	#每日清理今日预约的皇室婚礼
	global DivorceRecordSet
	DivorceRecordSet = set()
	
	global MarryID_Dict
	if not MarryID_Dict.returnDB: return
	MarryID_Dict[0] = set()
	MarryID_Dict.changeFlag = True
	
	cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
	cRoleMgr.BroadMsg()
#===============================================================================
# 客户端请求
#===============================================================================
def RequestOpenWedPanel(role, msg):
	'''
	打开面板 -- 同步对象ID, 同步铭刻信息(自己的所有铭刻信息+对象身上佩戴的订婚戒指的铭刻信息)
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		#等级限制
		return
	if not role.GetI8(EnumInt8.MarryStatus):
		#结婚状态
		return
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		print "GE_EXC, RequestOpenWedPanel marry role ID (%s) error" % role.GetRoleID()
		return
	#查询对象的数据
	marryRoleData = ReturnMarryRoleData(marryRoleId)
	if not marryRoleData:
		return
	role.SendObj(MarryObjMsg, marryRoleData)
	
	#同步铭刻信息
	role.SendObj(MarryRingMsg, role.GetTempObj(EnumTempObj.MarryRingImprintMsg))
	
def GetOtherImprintData(role, marryRoleId, marryRoleRingId):
	#返回结婚对象当前佩戴的订婚戒指的铭刻信息
	imprintData = RING_BT.GetData().get(marryRoleId)
	if not imprintData:
		return None
	imprintMsg = imprintData.get('ringData')
	if not imprintMsg:
		return None
	otherRingMsg = imprintMsg.get(marryRoleRingId)
	if not otherRingMsg:
		return None
	return otherRingMsg

def ReturnMarryRoleData(roleId):
	#返回结婚对象的查看数据
	role = cRoleMgr.FindRoleByRoleID(roleId)
	from Game.RoleView import RoleView
	if role:
		return RoleView.PackRole(role)
	else:
		rD = RoleView.RoleView_BT.GetData().get(roleId)
		if not rD:
			return
		return rD.get("viewData")[1]
	
def ReturnRingId(roleId):
	#返回佩戴的订婚戒指ID
	if not roleId:
		return None
	role = cRoleMgr.FindRoleByRoleID(roleId)
	ringId = None
	if role:
		for ringId in role.GetObj(EnumObj.En_RoleRing):
			return ringId
	else:
		from Game.RoleView import RoleView
		if not RoleView.RoleView_BT.returnDB:
			return None
		rD = RoleView.RoleView_BT.GetData().get(roleId)
		if not rD:
			return None
		viewData = rD.get("viewData")
		if not viewData:
			return None
		if EnumSocial.RoleRingData not in viewData[1]:
			return None
		for ringId in viewData[1][EnumSocial.RoleRingData].iterkeys():
			return ringId
	
def RequestMyPropose(role, msg):
	'''
	打开我的求婚面板
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	marryObj = role.GetObj(EnumObj.MarryObj)
	if not marryObj:
		print "GE_EXC, RequestMyPropose MarryObj not init"
		return
	#同步我的求婚信息
	role.SendObj(MarryPropose, marryObj.get(2))
	
def RequestNowWedding(role, msg):
	'''
	打开当前婚礼列表
	@param role:
	@param msg:
	'''
	global MarryID_Dict
	if not MarryID_Dict.returnDB: return
	
	role.SendObj(MarryNowWeddingList, MarryID_Dict.data)
	
def RequestPropose(role, msg):
	'''
	求婚
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		#等级
		return
	ownSex = role.GetSex()
	if role.GetI8(EnumInt8.MarryStatus):
		#结婚状态
		role.Msg(2, 0, GlobalPrompt.ReturnMarryThird(ownSex))
		return
	if role.GetDI1(EnumDayInt1.IsDivorce):
		#今日离婚了就不能在结婚了
		return
	#求婚对象ID, 求婚宣言, 求婚类型(1-悄悄的, 2-世界告白)
	proposeRoleId, proposeMsg, proposeType = msg
	if not proposeMsg or len(proposeMsg) > 150:
		#告白不能为空 或 告白内容不能超过50个汉字的长度
		return
	needRMB = EnumGameConfig.MarryWorldPropseRMB
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.MarryWorldPropseRMB_NA
	if proposeType == 2 and role.GetUnbindRMB() < needRMB:
		#世界告白钱不够
		return
	roleId = role.GetRoleID()
	if roleId == proposeRoleId:
		#不能向自己求婚
		return
	proposeRole = cRoleMgr.FindRoleByRoleID(proposeRoleId)
	if not proposeRole:
		#不在线
		role.Msg(2, 0, GlobalPrompt.MarryProposeWait_1)
		return
	if proposeRole.GetI8(EnumInt8.MarryStatus):
		#状态不对
		role.Msg(2, 0, GlobalPrompt.MarryProposTooLate)
		return
	proposeRoleSex = proposeRole.GetSex()
	if ownSex == proposeRoleSex:
		#同性
		return
	marryObj = role.GetObj(EnumObj.MarryObj)
	if not marryObj:
		return
	if (proposeRoleId in marryObj[2]) and (1 in marryObj[2][proposeRoleId]):
		#之前求过婚了
		role.Msg(2, 0, GlobalPrompt.ReturnMarryProposeWait(proposeRoleSex))
		return
	
	proposeObj = proposeRole.GetObj(EnumObj.MarryObj)
	if not proposeObj:
		return
	
	with MarryPropose_Log:
		#世界告白扣除神石
		if proposeType == 2:
			role.DecUnbindRMB(needRMB)
	
	roleName = role.GetRoleName()
	proposeName = proposeRole.GetRoleName()
	
	#求婚信息超过30条的时候删除前面的
	if len(marryObj[2]) == 30:
		delRoleID = marryObj[4].pop(0)
		if delRoleID in marryObj[2]:
			del marryObj[2][delRoleID]
	#按时间顺序排序求婚信息
	if proposeRoleId not in marryObj[2]:
		marryObj[4].append(proposeRoleId)
	else:
		if proposeRoleId in marryObj[4]:
			marryObj[4].remove(proposeRoleId)
		marryObj[4].append(proposeRoleId)
	nowSeconds = cDateTime.Seconds()
	marryObj[2][proposeRoleId] = {}
	marryObj[2][proposeRoleId][1] = PackProposeData(proposeRole, nowSeconds, 1, proposeType)
	role.SetObj(EnumObj.MarryObj, marryObj)
	#同步男方求婚成功
	role.SendObj(MarryPropose, marryObj[2])
	
	if len(proposeObj[2]) == 30:
		delRoleID = proposeObj[4].pop(0)
		if delRoleID in proposeObj[2]:
			del proposeObj[2][delRoleID]
	#按时间顺序排序求婚信息
	if roleId not in proposeObj[2]:
		proposeObj[4].append(roleId)
	else:
		if roleId in proposeObj[4]:
			proposeObj[4].remove(roleId)
		proposeObj[4].append(roleId)
	if roleId not in proposeObj[2]:
		proposeObj[2][roleId] = {}
	proposeObj[2][roleId][1] = PackProposeData(role, nowSeconds, 2, proposeType) 
	proposeRole.SetObj(EnumObj.MarryObj, proposeObj)
	#通知女方收到求婚信息
	proposeRole.SendObj(MarryGetProposeMsg, (roleId, roleName, proposeMsg))
	
	if proposeType == 2:
		cRoleMgr.Msg(12, 0, GlobalPrompt.MarryWorldPropose % (roleName, proposeName, proposeMsg))
	role.Msg(2, 0, GlobalPrompt.MarryProposeSuccess)
	
def RequestFilter(role, msg):
	'''
	筛选结婚对象
	@param role:
	@param msg:
	'''
	CheckBaseStatus(role)
	
	if role.GetDI1(EnumDayInt1.IsDivorce):
		#今日离婚
		return
	if role.GetCD(EnumCD.MarryFilterCD):
		#筛选CD
		role.SendObj(MarryCanMsg, role.GetTempObj(EnumTempObj.MarryFilter))
		return
	
	#好友字典
	FriendDict = role.GetObj(EnumObj.Social_Friend)
	
	TmpFriendDict = {}
	ownSex = role.GetSex()
	#筛选出可以求婚的在线异性好友
	for roleId in FriendDict:
		#性别相同
		if FriendDict[roleId][EnumSocial.RoleSexKey] == ownSex:
			continue
		#不在线
		gRole = cRoleMgr.FindRoleByRoleID(roleId)
		if not gRole:
			continue
		#不是未婚状态
		if gRole.GetI8(EnumInt8.MarryStatus):
			continue
		#等级
		if gRole.GetLevel() < EnumGameConfig.MarryLevelLimit:
			continue
		#今日是否离婚
		if gRole.GetDI1(EnumDayInt1.IsDivorce):
			continue
		#加入筛选字典
		if roleId not in TmpFriendDict:
			TmpFriendDict[roleId] = FriendDict[roleId]
	#保存一个临时对象
	role.SetTempObj(EnumTempObj.MarryFilter, TmpFriendDict)
	#同步可以求婚的对象
	role.SendObj(MarryCanMsg, TmpFriendDict)

def RequestAnswerMarry(role, msg):
	'''
	响应求婚
	@param role:
	@param msg:
	'''
	CheckBaseStatus(role)
	
	marryObj = role.GetObj(EnumObj.MarryObj)
	if not marryObj:
		return
	
	#求婚对象角色ID, 接受或拒绝
	proposeRoleID, yesOrNo = msg
	
	#不在求婚信息中
	if proposeRoleID not in marryObj[2]:
		return
	proposeMsg = marryObj[2][proposeRoleID].get(1)
	if not proposeMsg:
		#对方没有求婚
		return
	if proposeMsg[1] != 2:
		#你向对方求婚 ?
		return
	
	if yesOrNo == 1:
		#接受求婚
		AcceptMarry(role, marryObj, proposeRoleID)
	elif yesOrNo == 0:
		#拒绝求婚
		RefusalMarry(role, marryObj, proposeRoleID)
	
def RequestCancelPropose(role, msg):
	'''
	取消订婚
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#结婚状态 -- 只有订婚或预定婚礼状态才可取消婚礼
	nowMarrryStatus = role.GetI8(EnumInt8.MarryStatus)
	if nowMarrryStatus not in (1, 2):
		return
	
	proposeID = role.GetObj(EnumObj.MarryObj)[3][0]
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	
	#订婚
	if nowMarrryStatus == 1:
		role.SetI8(EnumInt8.MarryStatus, 0)
		role.GetObj(EnumObj.MarryObj)[1] = 0
		role.GetObj(EnumObj.MarryObj)[3] = []
		Call.LocalDBCall(proposeID, CancelPropose, None)
		role.Msg(2, 0, GlobalPrompt.MarryCancelDinghun)
		with MarryCancel_Log:
			Mail.SendMail(proposeID, GlobalPrompt.MarryCancelDinghun_Title, GlobalPrompt.MarryCancelDinghun_Sender, GlobalPrompt.MarryCancelDinghun_Content % roleName)
			AutoLog.LogBase(roleID, AutoLog.eveReservationWedding, (1, proposeID))
		return
	
	role.SetI8(EnumInt8.MarryStatus, 0)
	role.GetObj(EnumObj.MarryObj)[1] = 0
	role.GetObj(EnumObj.MarryObj)[3] = []
	
	marryID = role.GetObj(EnumObj.MarryObj)[5]
	
	if marryID not in MarryID_Dict:
		#KeyError?
		role.GetObj(EnumObj.MarryObj)[5] = 0
		print 'GE_EXC, MarryMgr RequestCancelPropose can not find marryID %s role id %s in MarryID_Dict' % (marryID, roleID)
		return
	
	Call.LocalDBCall(proposeID, CancelPropose, None)
	
	#获取婚礼开始tick
	beginTickID = MarryID_Dict[marryID][12]
	endTickID = MarryID_Dict[marryID][11]
	
	if (not beginTickID) or (not endTickID):
		return
	del MarryID_Dict[marryID]
	MarryID_Dict.changeFlag = True
	
	role.GetObj(EnumObj.MarryObj)[5] = 0
	
	#广播一下婚礼数据
	cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
	cRoleMgr.BroadMsg()
	
	#取消婚礼开始tick
	cComplexServer.UnregTick(beginTickID)
	cComplexServer.UnregTick(endTickID)
	
	with MarryCancel_Log:
		Mail.SendMail(proposeID, GlobalPrompt.MarryCancelDinghun_Title, GlobalPrompt.MarryCancelDinghun_Sender, GlobalPrompt.MarryCancelDinghun_Content % roleName)
		AutoLog.LogBase(roleID, AutoLog.eveReservationWedding, (2, proposeID))
	role.Msg(2, 0, GlobalPrompt.MarryCancelDinghun)
	
def RequestReservation(role, msg):
	'''
	预约婚礼
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	if role.GetI8(EnumInt8.MarryStatus) != 1:
		#结婚状态 -- 必须订婚状态才可以预约婚礼
		return
	marryObj = role.GetObj(EnumObj.MarryObj)
	if not marryObj:
		return
	marryRoleMsg = marryObj.get(3)
	if not marryRoleMsg:
		print "GE_EXC, RequestReservationWedding marryRoleMsg is empty"
		return
	
	marryRoleID,marryRoleName,marryUnionID,_,_,_ = marryRoleMsg
	
	#婚礼档次, 时间档
	gradeIndex, timeIndex = msg
	
	global MarryID_Dict
	if not MarryID_Dict.returnDB:
		return
	if (gradeIndex == 3) and (timeIndex in MarryID_Dict[0]):
		#同一时间段只能预约一次皇室婚礼
		return
	
	#婚礼档次配置
	gradeCfg = MarryConfig.MarryGrade_Dict.get(gradeIndex)
	if not gradeCfg:
		return
	#金币或神石不足
	if gradeCfg.needBindRMB and role.GetBindRMB() + role.GetUnbindRMB() < gradeCfg.needBindRMB:
		return
	elif gradeCfg.needRMB and role.GetUnbindRMB() < gradeCfg.needRMB:
		return
	
	#时间档配置
	timeCfg = MarryConfig.MarryTime_Dict.get(timeIndex)
	if not timeCfg:
		return
	#时间档是否可预约
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	if nowTime > timeCfg.beginTime:
		return
	
	roleName = role.GetRoleName()
	roleID = role.GetRoleID()
	
	#扣钱
	with MarryReservation_Log:
		if gradeCfg.needBindRMB:
			role.DecRMB(gradeCfg.needBindRMB)
		else:
			role.DecUnbindRMB(gradeCfg.needRMB)
		AutoLog.LogBase(roleID, AutoLog.eveReservationWedding, (gradeIndex, timeIndex, marryRoleID))
	
	#分配婚礼ID
	global MarryNextUseMaxID
	if MarryNextUseMaxID == 2000:
		MarryNextUseMaxID = 1000
	for _ in xrange(MarryNextUseMaxID, 2000):
		MarryNextUseMaxID += 1
		if MarryNextUseMaxID not in MarryID_Dict:
			break
	if MarryNextUseMaxID in MarryID_Dict:
		print "GE_EXC, MarryNextUseMaxID over 1000"
		MarryNextUseMaxID = max(MarryID_Dict.keys()) + 1
	
	#婚礼结束时间戳
	nowYear = cDateTime.Year()
	nowMonth = cDateTime.Month()
	nowDay = cDateTime.Day()
	nowSeconds = cDateTime.Seconds()
	
	beginTime = int(time.mktime(datetime.datetime(nowYear, nowMonth, nowDay, *timeCfg.beginTime).timetuple()))
	endTime = int(time.mktime(datetime.datetime(nowYear, nowMonth, nowDay, *timeCfg.endTime).timetuple()))
	
	#注册结束
	beginTickID = cComplexServer.RegTick(beginTime - nowSeconds, BeginWedding, (MarryNextUseMaxID, roleName, roleID, marryRoleName, marryRoleID, gradeIndex))
	endTickID = cComplexServer.RegTick(endTime - nowSeconds, EndWedding, (MarryNextUseMaxID, roleName, roleID, marryRoleName, marryRoleID))
	#打包婚礼数据字典
	MarryID_Dict[MarryNextUseMaxID] = PackWeddingData(role,marryRoleID,marryRoleName,timeIndex,gradeCfg,gradeIndex,endTickID,beginTickID)
	
	if gradeIndex == 3:
		MarryID_Dict[0].add(timeIndex)
	MarryID_Dict.changeFlag = True
	
	nowSeconds = cDateTime.Seconds()
	#设置双方婚礼ID
	#[预约时间,预约者名字(这个预约的人:None),婚礼档次,时间档]
	if marryRoleID not in marryObj[2]:
		marryObj[2][marryRoleID] = {3:[nowSeconds, None, gradeIndex, timeIndex]}
	else:
		marryObj[2][marryRoleID][3] = [nowSeconds, None, gradeIndex, timeIndex]
	#记一个婚礼ID
	marryObj[5] = MarryNextUseMaxID
	
	role.SetI8(EnumInt8.MarryStatus, 2)
	role.SetObj(EnumObj.MarryObj, marryObj)
	role.SendObj(MarryPropose, marryObj[2])
	role.SendObj(OwnMarryId, MarryNextUseMaxID)
	role.SendObj(MarryXinrenPanel, MarryID_Dict[MarryNextUseMaxID])
	
	Call.LocalDBCall(marryRoleID, Reservation, (roleID, roleName, gradeIndex, timeIndex, MarryNextUseMaxID, nowSeconds))
	
	if gradeIndex == 3:
		#皇室婚礼请帖
		if role.GetSex() == 1:
			bRoleName = role.GetRoleName()
			gRoleName = marryRoleName
		else:
			bRoleName = marryRoleName
			gRoleName = role.GetRoleName()
		cNetMessage.PackPyMsg(MarryInvitation, (bRoleName, gRoleName, timeIndex))
		cRoleMgr.BroadMsg()
	
	#同步所有人婚礼信息
	cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
	cRoleMgr.BroadMsg()
	
	#公会邮件
	bUnionID = role.GetUnionID()
	
	if gradeIndex == 1:
		mailContent = GlobalPrompt.MarryInvite_ContentA
	elif gradeIndex == 2:
		mailContent = GlobalPrompt.MarryInvite_ContentB
	else:
		mailContent = GlobalPrompt.MarryInvite_ContentC
	
	with MarryReservation_Log:
		if bUnionID and bUnionID == marryUnionID:
			#男方和女方同一个公会
			SendUnionMail(role.GetUnionObj(), roleName, marryRoleName, nowDay, timeCfg.beginTime, mailContent)
			cRoleMgr.Msg(1, 0, mailContent % (roleName, marryRoleName, nowDay, timeCfg.beginTime[0], timeCfg.beginTime[1]))
			return
		if bUnionID:
			#男方公会
			SendUnionMail(role.GetUnionObj(), roleName, marryRoleName, nowDay, timeCfg.beginTime, mailContent)
		if marryUnionID:
			#女方公会
			gUnion = UnionMgr.UNION_OBJ_DICT.get(marryUnionID)
			if not gUnion:
				return
			SendUnionMail(gUnion, roleName, marryRoleName, nowDay, timeCfg.beginTime, mailContent)
	
	cRoleMgr.Msg(1, 0, mailContent % (roleName, marryRoleName, nowDay, timeCfg.beginTime[0], timeCfg.beginTime[1]))
	
def RequestWorldInvite(role, msg):
	'''
	世界邀请
	@param role:
	@param msg:
	'''
	inviteData = Invite(role)
	if not inviteData:
		return
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryInvite_Tips % inviteData)
	
def RequestUnionInvite(role, msg):
	'''
	公会邀请
	@param role:
	@param msg:
	'''
	inviteData = Invite(role)
	if not inviteData:
		return
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	for role_id in unionObj.members.iterkeys():
		trole = cRoleMgr.FindRoleByRoleID(role_id)
		if not trole:
			continue
		trole.Msg(8, 0, GlobalPrompt.MarryInvite_Tips % inviteData)
	
def RequestJoinWedding(role, msg):
	'''
	进去婚礼
	@param role:
	@param msg:婚礼ID(合法的婚礼ID:1000-2500)
	'''
	marryID = msg
	if marryID <= 1000:
		return
	if role.GetLevel() < EnumGameConfig.MarryJoinWeddingLimit:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_MarryParty):
		return
	if role.GetSceneID() == EnumGameConfig.MarrySceneID:
		role.Msg(2, 0, GlobalPrompt.MarryInScene_2)
		return
	#根据婚礼ID获取婚礼数据
	global MarryID_Dict
	marryData = MarryID_Dict.get(marryID)
	if not marryData:
		role.Msg(2, 0, GlobalPrompt.MarryFinish)
		return
	_,_,_,_,timeIndex, _,_,_,_, _,weddingGrade ,_, _ = marryData
	#婚礼档次配置
	gradeCfg = MarryConfig.MarryGrade_Dict.get(weddingGrade)
	if not gradeCfg:
		print "GE_EXC, RequestJoinWedding can not find grade index (%s) in MarryGrade_Dict" % weddingGrade
		return
	#婚礼时间配置
	cfg = MarryConfig.MarryTime_Dict.get(timeIndex)
	if not cfg:
		print "GE_EXC, RequestJoinWedding can not find time index (%s) in MarryTime_Dict" % timeIndex
		return
	#当前时间
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	#不在预约的时间档内
	if nowTime < cfg.beginTime:
		role.Msg(2, 0, GlobalPrompt.MarryNotBegin)
		return
	if nowTime > cfg.endTime:
		role.Msg(2, 0, GlobalPrompt.MarryFinish)
		return
	if not Status.CanInStatus(role, EnumInt1.ST_InWedding):
		return
	#传送
	role.Revive(EnumGameConfig.MarrySceneID, *EnumGameConfig.MarryScenePos)
	
def RequestWeddingLibao(role, msg):
	'''
	新人请求开始发放婚礼礼盒
	@param role:
	@param msg:
	'''
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	bRoleID,gRoleID,bRoleName,gRoleName,timeIndex,_,_,libaoCnt,_,isLibaoBegin,_,_,_ = marryData
	
	roleID = role.GetRoleID()
	
	if roleID not in (bRoleID, gRoleID):
		#不是婚礼主人
		return
	if not CheckTime(role, marryID, timeIndex):
		#时间不对
		return
	if not libaoCnt:
		#没有礼盒
		return
	if isLibaoBegin == 3:
		#已经开始发放礼盒
		return
	if role.GetSceneID() != EnumGameConfig.MarrySceneID:
		return
	
	#开始发礼盒标志
	MarryID_Dict[marryID][9] = 3
	MarryID_Dict.changeFlag = True
	
	if roleID == bRoleID:
		marryRoleID = gRoleID
	else:
		marryRoleID = bRoleID
	#同步新人开始发放礼盒, 同时更新新人的婚礼数据
	role.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleID)
	if marryRole and marryRole.GetSceneID() == EnumGameConfig.MarrySceneID:
		marryRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	#同步婚礼场景内所有人有婚礼数据更新了
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.MarrySceneID)
	if scene:
		cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
		scene.BroadMsg()
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarrySendLibaoWorld % (bRoleName, gRoleName, libaoCnt, marryID))
	
def RequestBuyLibao(role, msg):
	'''
	新人请求购买礼包
	@param role:
	@param msg:
	'''
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	bRoleID,gRoleID,_,_,timeIndex,_,_,libaoCnt,_,_,_,_,_ = marryData
	
	libaoIndex = msg
	roleID = role.GetRoleID()
	
	if roleID not in (bRoleID, gRoleID):
		#不是新人
		return
	if not CheckTime(role, marryID, timeIndex):
		#时间不对
		return
	if libaoCnt:
		#有礼包的时候不能买
		return
	#礼包配置
	libaoCfg = MarryConfig.MarryLibao_Dict.get(libaoIndex)
	if not libaoCfg:
		return
	if role.GetUnbindRMB() <= libaoCfg.needRMB:
		return
	afterBuyCnt = libaoCnt + libaoCfg.libaoCnt
	if afterBuyCnt > 99:
		#超过99不能买
		return
	
	with MarrySceneBuy_Log:
		role.DecUnbindRMB(libaoCfg.needRMB)
	
	MarryID_Dict[marryID][7] = afterBuyCnt
	MarryID_Dict.changeFlag = True
	
	#同步新人婚礼数据更新了
	role.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	if roleID == bRoleID:
		gRole = cRoleMgr.FindRoleByRoleID(gRoleID)
		if gRole and gRole.GetSceneID() == EnumGameConfig.MarrySceneID:
			gRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	else:
		bRole = cRoleMgr.FindRoleByRoleID(bRoleID)
		if bRole and bRole.GetSceneID() == EnumGameConfig.MarrySceneID:
			bRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	#同步其他玩家礼包数量
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.MarrySceneID)
	if scene:
		cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
		scene.BroadMsg()
	
def RequestRebate(role, msg):
	'''
	新人请求贺礼回赠
	@param role:
	@param msg:
	'''
	keyIndex = msg
	if not keyIndex:
		return
	if keyIndex < 2:
		return
	
	roleID = role.GetRoleID()
	
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	
	if roleID not in (marryData[0], marryData[1]):
		#是否是新人
		return
	global MarryReviveHeli_Dict
	if roleID not in MarryReviveHeli_Dict:
		#是否收到过贺礼
		return
	if keyIndex not in MarryReviveHeli_Dict[roleID]:
		#是否是合法的key
		return
	if role.GetUnbindRMB() < EnumGameConfig.MarryRebateRMB:
		#不够回赠贺礼的神石
		return
	
	#扣钱
	with MarryRebate_Log:
		role.DecUnbindRMB(EnumGameConfig.MarryRebateRMB)
	
		rebateID, rebateName = MarryReviveHeli_Dict[roleID][keyIndex]
		
		#收到贺礼数量-1
		MarryReviveHeli_Dict[roleID][1] -= 1
		#删除一条收到贺礼信息
		del MarryReviveHeli_Dict[roleID][keyIndex]
		
		rebateRole = cRoleMgr.FindRoleByRoleID(rebateID)
		
		if rebateRole:
			rebateRole.AddItem(EnumGameConfig.MarryRebateCoding, 1)
		else:
			Mail.SendMail(rebateID, GlobalPrompt.MarryRebateMail_Title, GlobalPrompt.MarryRebateMail_Sender, GlobalPrompt.MarryRebateTips % (role.GetRoleName(), rebateName, EnumGameConfig.MarryRebateCoding, 1), [(EnumGameConfig.MarryRebateCoding, 1)])
	#同步贺礼数据
	role.SendObj(MarryReviveHeliMsg, MarryReviveHeli_Dict[roleID])
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryRebateTips % (role.GetRoleName(), rebateName, EnumGameConfig.MarryRebateCoding, 1))
	
def RequestFireworks(role, msg):
	'''
	烟花
	@param role:
	@param msg:
	'''
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	bRoleID,gRoleID,_,_,timeIndex,yanhuaCnt,_,_,_,_,_,_,_ = marryData
	
	if role.GetRoleID() not in (bRoleID, gRoleID):
		#不是新人
		return
	if not CheckTime(role, marryID, timeIndex):
		#时间判定
		return
	if not yanhuaCnt:
		#没有烟花
		return
	
	#扣烟花
	MarryID_Dict[marryID][5] -= 1
	MarryID_Dict.changeFlag = True
	
	#放烟花
	for role_id in (bRoleID, gRoleID):
		tmpRole = cRoleMgr.FindRoleByRoleID(role_id)
		if not tmpRole:
			continue
		if tmpRole.GetSceneID() != EnumGameConfig.MarrySceneID:
			continue
		#更新新人的婚礼数据
		tmpRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	#同步婚礼场景内所有人开始放烟花
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.MarrySceneID)
	if scene:
		cNetMessage.PackPyMsg(MarryOperator, 2)
		scene.BroadMsg()
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryPlayFireworksSystem % role.GetRoleName())
	
def RequestUnburden(role, msg):
	'''
	表白
	@param role:
	@param msg:
	'''
	if not msg: return
	
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	bRoleID,gRoleID,bRoleName,gRoleName,timeIndex,_,biaobaiCnt,_,_,_,_,_,_ = marryData
	
	roleID = role.GetRoleID()
	
	if roleID not in (bRoleID, gRoleID):
		#不是新人
		return
	if not CheckTime(role, marryID, timeIndex):
		#时间不对
		return
	if not biaobaiCnt:
		#没有表白次数
		return
	if role.GetSceneID() != EnumGameConfig.MarrySceneID:
		return
	
	#扣表白次数
	global MarryID_Dict
	MarryID_Dict[marryID][6] -= 1
	MarryID_Dict.changeFlag = True
	
	#同步新人婚礼数据
	role.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	if roleID == bRoleID:
		gRole = cRoleMgr.FindRoleByRoleID(gRoleID)
		if gRole:
			gRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
		cRoleMgr.Msg(1, 0, GlobalPrompt.MarryUnburden % (bRoleName, gRoleName, msg))
	else:
		bRole = cRoleMgr.FindRoleByRoleID(bRoleID)
		if bRole:
			bRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
		cRoleMgr.Msg(1, 0, GlobalPrompt.MarryUnburden % (gRoleName, bRoleName, msg))
	
	role.Msg(2, 0, GlobalPrompt.MarrySuccessBiaobai)
	
def RequestVow(role, msg):
	'''
	宣誓 -- 宣誓不算完成婚礼
	@param role:
	@param msg:
	'''
	global isVow
	if isVow:
		role.Msg(2, 0, GlobalPrompt.MarryIsVow)
		return
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	bRoleID,gRoleID,bRoleName,gRoleName,timeIndex,_,_,_,vowCnt,_,_,_,_ = marryData
	
	roleID = role.GetRoleID()
	
	if roleID not in (bRoleID, gRoleID):
		#不是新人
		return
	if not CheckTime(role, marryID, timeIndex):
		return
	if not vowCnt:
		#没有宣誓次数
		return
	if role.GetSceneID() != EnumGameConfig.MarrySceneID:
		return
	
	#扣除宣誓次数
	global MarryID_Dict
	MarryID_Dict[marryID][8] -= 1
	MarryID_Dict.changeFlag = True
	
	#获取对象角色ID
	if roleID == bRoleID:
		marryRoleID = gRoleID
	else:
		marryRoleID = bRoleID
	
	#设置有人正在宣誓标志
	isVow = True
	
	#更新新人的婚礼数据
	role.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleID)
	if marryRole and (marryRole.GetSceneID() == EnumGameConfig.MarrySceneID):
		marryRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	#同步场景内所有玩家有人正在宣誓
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.MarrySceneID)
	if scene:
		cNetMessage.PackPyMsg(MarryVowData, (bRoleName, gRoleName))
		scene.BroadMsg()
	
	#注册一个tick, 10s后取消有人正在宣誓标志
	cComplexServer.RegTick(10, FinishVow)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryXuanshiman % (bRoleName, gRoleName))
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryXuanshiwoman % (gRoleName, bRoleName))
	
def RequestHandsel(role, msg):
	'''
	宾客赠送新人贺礼
	@param role:
	@param msg:
	'''
	marryID = msg
	
	marryData = MarryID_Dict.get(marryID)
	if not marryData:
		return
	bRoleID,gRoleID,bRoleName,gRoleName,timeIndex,_,_,_,_,_,_,_,_ = marryData
	
	roleName = role.GetRoleName()
	roleID = role.GetRoleID()
	
	if roleID in (bRoleID, gRoleID):
		#不能赠送给自己
		return
	#判断使用道具还是神石
	useItem = False
	if role.ItemCnt(EnumGameConfig.MarryHandselCoding) >= 1:
		useItem = True
	elif role.GetUnbindRMB() < EnumGameConfig.MarryHandselRMB:
		return
	if not CheckTime(role, marryID, timeIndex):
		#时间
		return
	
	with MarryHeli_Log:
		if useItem:
			role.DelItem(EnumGameConfig.MarryHandselCoding, 1)
		else:
			role.DecUnbindRMB(EnumGameConfig.MarryHandselRMB)
	
	#修改贺礼数据
	ReviveHeliDict(roleID, roleName, bRoleID, gRoleID)
	#在线的直接发贺礼, 不在线的通过邮件发
	with MarryReviveHeli_Log:
		SendHeli(marryID, bRoleID, gRoleID, roleName)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarrySendHeliWorld % (roleName, bRoleName, gRoleName))
	
def RequestBuyItem(role, msg):
	'''
	新人请求购买物品
	@param role:
	@param msg:1-贺礼, 2-烟花, 3-表白(注:这里不能买贺礼)
	'''
	marryID, marryData = ReturnMarryData(role)
	if (not marryID) or (not marryData):
		return
	bRoleID,gRoleID,_,_,timeIndex,_,_,_,_,_,_,_,_ = marryData
	
	index = msg
	if index not in (2, 3):
		return
	
	roleID = role.GetRoleID()
	
	xinrenIDList = (bRoleID, gRoleID)
	if roleID not in xinrenIDList:
		#不是新人
		return
	if not CheckTime(role, marryID, timeIndex):
		return
	
	with MarrySceneBuy_Log:
		if index == 2:
			needRMB = 0
			if Environment.EnvIsNA():
				needRMB = EnumGameConfig.MarryFireworksRMB_NA
			else:
				needRMB = EnumGameConfig.MarryFireworksRMB
			#烟花
			if role.GetUnbindRMB() < needRMB:
				#钱不够
				return
			if MarryID_Dict[marryID][5] > 98:
				#烟花数量超过最大值
				return
			#扣钱
			role.DecUnbindRMB(needRMB)
			#加烟花个数
			MarryID_Dict[marryID][5] += 1
			MarryID_Dict.changeFlag = True
			#同步新人数据
			SyncXinren(xinrenIDList, MarryID_Dict[marryID])
		elif index == 3:
			#表白次数
			if role.GetUnbindRMB() < EnumGameConfig.MarryBiaobaiRMB:
				return
			if MarryID_Dict[marryID][6] > 98:
				return
			role.DecUnbindRMB(EnumGameConfig.MarryBiaobaiRMB)
			MarryID_Dict[marryID][6] += 1
			MarryID_Dict.changeFlag = True
			SyncXinren(xinrenIDList, MarryID_Dict[marryID])
	
def RequestGetLibao(role, msg):
	'''
	领礼包
	@param role:
	@param msg:
	'''
	if role.GetSceneID() != EnumGameConfig.MarrySceneID:
		return
	if role.GetDI8(EnumDayInt8.MarryLibaoCntLimit) >= EnumGameConfig.MarryLibaoCnt:
		#每日领取的礼包个数超出限制
		role.Msg(2, 0, GlobalPrompt.MarryGetLibaoCntMax)
		return
	if role.GetCD(EnumCD.MarryLibaoCD):
		return
	
	marryID = msg
	
	global MarryID_Dict
	marryData = MarryID_Dict.get(marryID)
	if not marryData:
		return
	bRoleID,gRoleID,bRoleName,gRoleName,timeIndex,_,_,libaoCnt,_,isBegin,_,_,_  = MarryID_Dict[marryID]
	
	roleName = role.GetRoleName()
	roleID = role.GetRoleID()
	
	if roleID in (bRoleID, gRoleID):
		#自己的婚礼
		return
	if not CheckTime(role, marryID, timeIndex):
		#时间
		return
	if isBegin == 4:
		#还没有开始发放礼包
		return
	if not libaoCnt:
		#没有礼包了
		return
	
	role.SetCD(EnumCD.MarryLibaoCD, EnumGameConfig.MarryLibaocd)
	
	#扣除礼包个数
	MarryID_Dict[marryID][7] -= 1
	#增加每日领取礼包个数
	role.IncDI8(EnumDayInt8.MarryLibaoCntLimit, 1)
	#获得物品
	itemCoding = random.choice(EnumGameConfig.MarryLibaoRandomList)
	with MarryLibao_Log:
		role.AddItem(itemCoding, 1)
	#如果没有礼包了, 设置停止发放礼包状态
	if not MarryID_Dict[marryID][7]:
		MarryID_Dict[marryID][9] = 4
	MarryID_Dict.changeFlag = True
	
	for tmpRoleId in (bRoleID, gRoleID):
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
		if not tmpRole:
			continue
		if tmpRole.GetSceneID() != EnumGameConfig.MarrySceneID:
			continue
		#同步礼包剩余
		tmpRole.SendObj(MarryXinrenPanel, MarryID_Dict[marryID])
	
	#同步婚礼场景内所有玩家婚礼数据更新了
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.MarrySceneID)
	if scene:
		cNetMessage.PackPyMsg(MarryNowWeddingList, MarryID_Dict.data)
		scene.BroadMsg()
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.MarryGetLibaoWorld % (roleName, bRoleName, gRoleName, itemCoding, 1, marryID))
	role.Msg(2, 0, GlobalPrompt.MarryGetLibaoGeren % (itemCoding, 1))
	
def RequestDivorce(role, msg):
	'''
	离婚
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if role.GetI8(EnumInt8.HoneymoonStatus) in (1, 2):
		return
	if role.GetMoney() < EnumGameConfig.MarryDivorceMoney:
		return
	
	if (19, 0) < (cDateTime.Hour(), cDateTime.Minute()) < (19, 50):
		return
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	
	mRoleID = role.GetObj(EnumObj.MarryObj).get(1)
	if not mRoleID:
		print "GE_EXC, RequestDivorce can not find marry role (%s)" % roleID
		return
	
	if not IsHostParty(role, roleID, mRoleID):
		#正在开Party的话不让离婚
		return
	
	with MarryDivorce_Log:
		role.DecMoney(EnumGameConfig.MarryDivorceMoney)
		AutoLog.LogBase(roleID, AutoLog.eveDivorce, mRoleID)
	
	#设置结婚状态
	role.SetI8(EnumInt8.MarryStatus, 0)
	role.SetI8(EnumInt8.HoneymoonStatus, 0)
	role.GetObj(EnumObj.MarryObj)[1] = 0
	if 6 in role.GetObj(EnumObj.MarryObj):
		role.GetObj(EnumObj.MarryObj)[6] = []
	role.SetObj(EnumObj.MarryObj, role.GetObj(EnumObj.MarryObj))
	
	#清理记录的最高订婚戒指数据
	global MarryRing_Dict
	if MarryRing_Dict.returnDB and (roleID in MarryRing_Dict):
		del MarryRing_Dict[roleID]
		MarryRing_Dict.changeFlag = True
	
	role.SetDI1(EnumDayInt1.IsDivorce, True)
	
	#重算订婚属性
	role.ResetMarryRingProperty()
	
	#取消用夫妻双方婚戒ID激活的技能
	CancelSkill(role)
	#取消结婚相关称号
	CancelTitle(role)
	#清理举办跨服派对记录
	from Game.Marry import MarryParty
	if roleID in MarryParty.KuafuPartyCntDict:
		del MarryParty.KuafuPartyCntDict[roleID]
	if mRoleID in MarryParty.KuafuPartyCntDict:
		del MarryParty.KuafuPartyCntDict[mRoleID]
	MarryParty.KuafuPartyCntDict.changeFlag = True
	
	Call.LocalDBCall(mRoleID, DivorceExEx, (roleID, roleName, cDateTime.Days()))
	
	global DivorceRecordSet
	DivorceRecordSet.add(roleID)
	DivorceRecordSet.add(mRoleID)
	
	role.SendObj(MarryRoleNameData, GetMarryRoleName(role))
	
	#触发改变结婚对象名字
	Event.TriggerEvent(Event.Eve_ChangeMarryRoleName, role)
	
	role.Msg(2, 0, GlobalPrompt.MarryDivorce_2)
	
def RequestHoneymoon(role, msg):
	'''
	请求开启蜜月
	@param role:
	@param msg:
	'''
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if role.GetI8(EnumInt8.HoneymoonStatus):
		return
	
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		print 'GE_EXC, Marry RequestHoneymoon role :%s can not find marry role id' % role.GetRoleID()
		return
	marryRoleName = GetMarryRoleName(role)
	if not marryRoleName:
		return
	
	honeymoonGrade = msg
	
	hmCfg = MarryConfig.HoneymoonGrade_Dict.get(honeymoonGrade)
	if not hmCfg:
		return
	if role.GetUnbindRMB() < hmCfg.needRMB:
		#钱不够
		return
	
	with OpenHoneymoon_Log:
		role.DecUnbindRMB(hmCfg.needRMB)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveHoneymoonBegin, marryRoleId)
	
	role.SetI8(EnumInt8.HoneymoonStatus, honeymoonGrade)
	Call.LocalDBCall(marryRoleId, SetHoneymoonGrade, (cDateTime.Seconds(), honeymoonGrade))
	
	roleName = role.GetRoleName()
	
	#注册5分钟后蜜月结束
	cComplexServer.RegTick(300, EndHoneymoon, (role.GetRoleID(), roleName, marryRoleId, marryRoleName, honeymoonGrade))
	
	role.Msg(2, 0, GlobalPrompt.HoneymoonBegin)
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
	if marryRole:
		marryRole.Msg(2, 0, GlobalPrompt.HoneymoonBegin)
	
	if honeymoonGrade == 1:
		cRoleMgr.Msg(1, 0, GlobalPrompt.HoneymoonBegin_1 % (roleName, marryRoleName))
	else:
		role.Msg(2, 0, GlobalPrompt.HoneymoonBegin_2 % marryRoleName)
		if marryRole:
			role.Msg(2, 0, GlobalPrompt.HoneymoonBegin_2 % roleName)
		
def EndHoneymoon(argv, param):
	roleId, roleName, otherRoleId, otherRoleName, honeymoonGrade = param
	
	endSec = cDateTime.Seconds()
	#设置蜜月完成状态
	Call.LocalDBCall(roleId, SetHoneymoonFinish, (endSec, otherRoleId, otherRoleName, honeymoonGrade))
	Call.LocalDBCall(otherRoleId, SetHoneymoonFinish, (endSec, roleId, roleName, honeymoonGrade))
	
	#邮件
	cfg = MarryConfig.HoneymoonGrade_Dict.get(honeymoonGrade)
	if not cfg:
		return
	
	with FinishHoneymoon_Log:
		Mail.SendMail(roleId, GlobalPrompt.HoneymoonMailTitle, GlobalPrompt.HoneymoonMailSender, GlobalPrompt.HoneymoonMailContent % (cfg.libaoCoding, 1, cfg.qinmi), items=[(cfg.libaoCoding, 1)])
		Mail.SendMail(otherRoleId, GlobalPrompt.HoneymoonMailTitle, GlobalPrompt.HoneymoonMailSender, GlobalPrompt.HoneymoonMailContent % (cfg.libaoCoding, 1, cfg.qinmi), items=[(cfg.libaoCoding, 1)])
		
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveHoneymoonEnd, (roleId,otherRoleId))
		
	Call.LocalDBCall(roleId, SendHoneymoonQinmi, honeymoonGrade)
	Call.LocalDBCall(otherRoleId, SendHoneymoonQinmi, honeymoonGrade)
	
	if honeymoonGrade == 1:
		cRoleMgr.Msg(1, 0, GlobalPrompt.HoneymoonFinish_1 % (roleName, otherRoleName))
	else:
		brole = cRoleMgr.FindRoleByRoleID(roleId)
		if brole:
			brole.Msg(2, 0, GlobalPrompt.HoneymoonFinish_2 % otherRoleName)
		grole = cRoleMgr.FindRoleByRoleID(otherRoleId)
		if grole:
			grole.Msg(2, 0, GlobalPrompt.HoneymoonFinish_2 % roleName)
	
def RequestRingImprint(role, msg):
	'''
	请求订婚戒指铭刻
	@param role:
	@param msg:
	'''
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if role.GetLevel() < EnumGameConfig.MarryRingImprintLv:
		return
	
	#获取当前佩戴的订婚戒指ID
	ringIdSet = role.GetObj(EnumObj.En_RoleRing)
	if not ringIdSet:
		return
	for ringId in ringIdSet:
		break
	#订婚戒指管理器
	ringMgr = role.GetTempObj(EnumTempObj.enRoleRingMgr)
	ring= ringMgr.FindProp(ringId)
	if not ring :
		return
	if ring.Obj_Type != Base.Obj_Type_Ring:
		return
	if ring.IsImprint():
		#已经铭刻过了
		return
	
	#结婚对象ID, 结婚对象名字
	marryObj = role.GetObj(EnumObj.MarryObj)
	marryRoleId = marryObj.get(1)
	if not marryRoleId:
		return
	marryRoleName = GetMarryRoleName(role)
	if not marryRoleName:
		role.Msg(2, 0, GlobalPrompt.RingFindError)
		return
	
	#铭刻信息(不能为空, 不能超过20个汉字)
	imprintMsg = msg
	if (not imprintMsg) or (len(imprintMsg) == 0) or (len(imprintMsg) > 60):
		return
	
	#设置订婚戒指已铭刻
	ring.SetIsImprint()
	
	#重算订婚戒指属性
	role.ResetMarryRingProperty()
	
	#增加一个婚戒铭刻信息
	AddRoleRingData(role, role.GetRoleID(), marryRoleId, marryRoleName, ringId, ring.otype, imprintMsg)
	
def InsertRing(mgr, prop):
	#管理器增加订婚戒指操作
	mgr.objIdDict[prop.oid] = prop
	prop.package = mgr
	
	cd_dict = mgr.codingGather.get(prop.otype)
	if not cd_dict:
		mgr.codingGather[prop.otype] = cd_dict = {}
	cd_dict[prop.oid] = prop
	
def RemoveRing(mgr, prop):
	#管理器移除订婚戒指操作
	del mgr.objIdDict[prop.oid]
	prop.package = None
	
	cd_dict = mgr.codingGather.get(prop.otype)
	del cd_dict[prop.oid]
	if not cd_dict:
		del mgr.codingGather[prop.otype]
	
def RequestRingEquipment(role, msg):
	'''
	请求装备订婚戒指
	@param role:
	@param msg:
	'''
	global MarryRing_Dict
	if not MarryRing_Dict.returnDB: return
	
	ringId = msg
	
	#从背包里获取订婚戒指对象
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	ring= packMgr.FindProp(ringId)
	if not ring :
		return
	if ring.Obj_Type != Base.Obj_Type_Ring:
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	ringIdSet = role.GetObj(EnumObj.En_RoleRing)
	if not ringIdSet:
		ringIdSet = set()
	roleRingMgr = role.GetTempObj(EnumTempObj.enRoleRingMgr)
	ring_2 = None
	for eq in roleRingMgr.objIdDict.values():
		ring_2 = eq
		break
	
	if ring_2:
		#交换两个订婚戒指
		#清理两个背包中的相关数据
		RemoveRing(roleRingMgr, ring_2)
		RemoveRing(packMgr, ring)
		#清理角色OBJ记录
		packIdSet.discard(ringId)
		ringIdSet.discard(ring_2.oid)
		#清理拥有者
		ring_2.owner = None
		
		#重新写入交换后的数据
		InsertRing(roleRingMgr, ring)
		InsertRing(packMgr, ring_2)
		#重新写入角色OBJ记录
		ringIdSet.add(ringId)
		packIdSet.add(ring_2.oid)
		##拥有者拥有者
		ring.owner = role
		
		#同步客户端，身上的装备脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, ring_2.oid)
	else:
		#直接穿上去
		#清理背包管理器
		RemoveRing(packMgr, ring)
		#清理人物数组数据
		packIdSet.discard(ringId)
		
		#更新角色装备管理器数据
		InsertRing(roleRingMgr, ring)
		#拥有者
		ring.owner = role
		#人物数组数据
		ringIdSet.add(ringId)
		
	role.SetObj(EnumObj.En_RoleRing, ringIdSet)
	
	#重算订婚戒指属性
	role.ResetMarryRingProperty()
	
	#同步穿装备成功
	role.SendObj(Ring_RolePutOn_OK, (ringId, ring.otype))
	#触发魅力情人节-情人目标
	Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_EngageRing, 1))
	
	roleId = role.GetRoleID()
	isTry = False
	isImprint = ring.IsImprint()
	if roleId not in MarryRing_Dict:
		#之前没有记录
		isTry = True
		if isImprint:
			MarryRing_Dict[roleId] = [ring.otype, ring.otype]
		else:
			MarryRing_Dict[roleId] = [ring.otype, 0]
	else:
		lastCoding, lastImprintCoding = MarryRing_Dict[roleId]
		if ring.otype > lastCoding:
			#新的订婚戒指coding比之前的好
			isTry = True
			lastCoding = ring.otype
		if isImprint and (ring.otype > lastImprintCoding):
			#比之前铭刻的摇号
			isTry = True
			lastImprintCoding = ring.otype
		MarryRing_Dict[roleId] = [lastCoding, lastImprintCoding]
	MarryRing_Dict.changeFlag = True
	
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		return
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
	if not marryRole:
		return
	#修改对象缓存的铭刻信息
	imprintMsg = GetRoleRingMsg(roleId, ringId)
	if imprintMsg:
		marryRole.GetTempObj(EnumTempObj.MarryRingImprintMsg)[ringId] = [roleId, role.GetRoleName(), imprintMsg]
	#有更好的
	if isTry:
		TryActRingPro(marryRole)
	
def RequestHoneySay(role, msg):
	'''
	请求发送甜言蜜语
	@param role:
	@param msg:
	'''
	if role.GetCD(EnumCD.HoneymoonSayCD):
		return
	
	honeymoonStatus = role.GetI8(EnumInt8.HoneymoonStatus)
	if honeymoonStatus not in (1, 2):
		return
	
	sayMsg = msg
	#不能超过20个汉字
	if (not sayMsg) or (not len(sayMsg)) or (len(sayMsg) > 60):
		return
	
	role.SetCD(EnumCD.HoneymoonSayCD, 20)
	
	marryRoleName = GetMarryRoleName(role)
	if not marryRoleName:
		return
	if honeymoonStatus == 1:
		cRoleMgr.Msg(12, 0, GlobalPrompt.HoneymoonSay_2 % (role.GetRoleName(), marryRoleName, sayMsg))
	else:
		role.Msg(1, 0, GlobalPrompt.HoneymoonSay_1 % (role.GetRoleName(), marryRoleName, sayMsg))
		marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
		if not marryRoleId:
			return
		marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
		if marryRole:
			marryRole.Msg(1, 0, GlobalPrompt.HoneymoonSay_1 % (role.GetRoleName(), marryRoleName, sayMsg))
	
#===============================================================================
# 大表操作
#===============================================================================
def AddRoleRingData(role, roleId, imprintRoleId, imprintRoleName, ringId, ringCoding, ringMsg):
	#增加一条订婚戒指铭刻信息
	global RING_BT
	if not RING_BT.returnDB: return
	global MarryRing_Dict
	if not MarryRing_Dict.returnDB: return
	
	ringData = GetRoleRingData(roleId)
	if not ringData:
		ringData = {ringId:[imprintRoleId, imprintRoleName, ringMsg]}
	else:
		ringData[ringId] = [imprintRoleId, imprintRoleName, ringMsg]
	RING_BT.SetKeyValue(roleId, {"role_id" : roleId, "ringData" : ringData})
	
	with MarryRingOperator_Log:
		AutoLog.LogBase(roleId, AutoLog.eveMarryRingImprint, (ringId, imprintRoleId, imprintRoleName, ringMsg))
	
	#记录自己的订婚戒指信息, 用于触发对象的属性
	if roleId not in MarryRing_Dict:
		print 'GE_EXC, MarryMgr AddRoleRingData error by role :%s' % roleId
		return
	imprintCoding = MarryRing_Dict[roleId][1]
	isTry = False
	if ringCoding > imprintCoding:
		#新的铭刻戒指比之前的好
		isTry = True
		MarryRing_Dict[roleId][1] = ringCoding
		MarryRing_Dict.changeFlag = True
	
	#往缓存的订婚戒指铭刻信息中加入一条铭刻信息
	role.GetTempObj(EnumTempObj.MarryRingImprintMsg)[ringId] = [imprintRoleId, imprintRoleName, ringMsg]
	role.SendObj(MarryRingMsg, role.GetTempObj(EnumTempObj.MarryRingImprintMsg))
	
	role.Msg(2, 0, GlobalPrompt.RingImprintSuccess)
	
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		return
	marryrole = cRoleMgr.FindRoleByRoleID(marryRoleId)
	if not marryrole:
		return
	#修改对象缓存的铭刻信息
	marryrole.GetTempObj(EnumTempObj.MarryRingImprintMsg)[ringId] = [imprintRoleId, imprintRoleName, ringMsg]
	if isTry:
		#尝试触发对象的订婚戒指属性重算
		TryActRingPro(marryrole)
	
def DelRoleRingData(role, roleId, ringId):
	#删除一个订婚戒指
	ringData = GetRoleRingData(roleId)
	if not ringData:
		return
	if ringId not in ringData:
		return
	del ringData[ringId]
	
	RING_BT.SetKeyValue(roleId, {"role_id" : roleId, "ringData" : ringData})
	if ringId in role.GetTempObj(EnumTempObj.MarryRingImprintMsg):
		del role.GetTempObj(EnumTempObj.MarryRingImprintMsg)[ringId]
	role.SendObj(MarryRingMsg, role.GetTempObj(EnumTempObj.MarryRingImprintMsg))
	
	with MarryRingOperator_Log:
		AutoLog.LogBase(roleId, AutoLog.eveMarryRingDel, ringId)
	
def GetRoleRingData(roleId):
	#获取订婚戒指数据
	global RING_BT
	ringData = RING_BT.GetData().get(roleId)
	if not ringData:
		return None
	return ringData.get("ringData")

def GetRoleRingMsg(roleId, ringId):
	#获取铭刻信息
	ringData = GetRoleRingData(roleId)
	if not ringData:
		return None
	return ringData.get(ringId)

#===============================================================================
# 持久化数据载入
#===============================================================================
def AfterLoad():
	global MarryID_Dict
	#key:0, 记录已预约的皇室婚礼时间档
	if 0 not in MarryID_Dict:
		MarryID_Dict[0] = set()
	
	#当前时间
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	
	for marryID in MarryID_Dict.keys():
		#婚礼时间档
		if not marryID:
			continue
		timeIndex = MarryID_Dict[marryID][4]
		gradeIndex = MarryID_Dict[marryID][10]
		gradeCfg = MarryConfig.MarryGrade_Dict.get(gradeIndex)
		if not gradeCfg:
			print "GE_EXC, AfterLoad can not find grade index (%s) in MarryGrade_Dict" % gradeIndex
			continue
		
		itemRewardCoding = gradeCfg.itemReward
		
		cfg = MarryConfig.MarryTime_Dict.get(timeIndex)
		if not cfg:
			print "GE_EXC, AfterLoad can not find time index (%s) in MarryTime_Dict" % timeIndex
			del MarryID_Dict[marryID]
			continue
		mRoleID = MarryID_Dict[marryID][0]
		wRoleID = MarryID_Dict[marryID][1]
		mRoleName = MarryID_Dict[marryID][2]
		wRoleName = MarryID_Dict[marryID][3]
		
		endSec = cDateTime.Seconds()
		if nowTime >= cfg.endTime:
			#婚礼时间过了, 算完成婚礼
			if WorldData.WD.returnDB:
				WorldData.WD[EnumSysData.MarryCnt] += 1
				cnt = WorldData.WD[EnumSysData.MarryCnt]
			else:
				cnt = 100
			
			Call.LocalDBCall(mRoleID, FinishWedding, (endSec, wRoleID, wRoleName, gradeIndex, cnt))
			Call.LocalDBCall(wRoleID, FinishWedding, (endSec, mRoleID, mRoleName, gradeIndex, cnt))
			del MarryID_Dict[marryID]
			with MarryFinish_Log:
				Mail.SendMail(mRoleID, GlobalPrompt.MarryFinisMail_Title, GlobalPrompt.MarryFinisMail_Sender, GlobalPrompt.MarryFinisMail_Content % (wRoleName, itemRewardCoding, 1), [(itemRewardCoding, 1)])
				Mail.SendMail(wRoleID, GlobalPrompt.MarryFinisMail_Title, GlobalPrompt.MarryFinisMail_Sender, GlobalPrompt.MarryFinisMail_Content % (wRoleName, itemRewardCoding, 1), [(itemRewardCoding, 1)])
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveMarryFinish, (mRoleID, wRoleID))
			continue
		beginTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), *cfg.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), *cfg.endTime).timetuple()))
		if nowTime <= cfg.beginTime:
			nowSeconds = cDateTime.Seconds()
			#重新注册婚礼结束tick
			beginTickID = cComplexServer.RegTick(beginTime - nowSeconds, BeginWedding, (marryID, mRoleName, mRoleID, wRoleName, wRoleID, gradeIndex))
			endTickID = cComplexServer.RegTick(endTime - nowSeconds, EndWedding, (marryID, mRoleName, mRoleID, wRoleName, wRoleID))
			MarryID_Dict[marryID][11] = endTickID
			MarryID_Dict[marryID][12] = beginTickID
		elif nowTime > cfg.beginTime:
			nowSeconds = cDateTime.Seconds()
			BeginWedding(None, (marryID, mRoleName, mRoleID, wRoleName, wRoleID, gradeIndex))
			endTickID = cComplexServer.RegTick(endTime - nowSeconds, EndWedding, (marryID, mRoleName, mRoleID, wRoleName, wRoleID))
			MarryID_Dict[marryID][11] = endTickID
	MarryID_Dict.changeFlag = True
	
def TryActRingPro(role):
	#尝试激活订婚戒指属性
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		return
	#获取结婚对象的订婚戒指信息:最高级的订婚戒指ID, 是否铭刻过
	global MarryRing_Dict
	if not MarryRing_Dict.returnDB: return
	ringData = MarryRing_Dict.get(marryRoleId)
	if not ringData:
		return
	ringCoding, imprintCoding = ringData
	
	#修改自己记录的对象订婚戒指信息
	marryRingData = role.GetObj(EnumObj.MarryObj).get(6)
	
	if not marryRingData:
		role.GetObj(EnumObj.MarryObj)[6] = [ringCoding, imprintCoding]
	else:
		maxRindCoding, maxImprintCoding = marryRingData
		if maxRindCoding < ringCoding:
			role.GetObj(EnumObj.MarryObj)[6][0] = ringCoding
		if imprintCoding > maxImprintCoding:
			role.GetObj(EnumObj.MarryObj)[6][1] = imprintCoding
	
	#属性重算
	role.ResetMarryRingProperty()
	
def AfterRBLoad():
	pass

if "_HasLoad" not in dir():
	if (Environment.HasLogic and not Environment.IsCross) or Environment.HasWeb:
		#订婚戒指铭刻信息大表
		#role_id --> ringData
		#ringData --> {订婚戒指道具ID:[role_id, role_name, 铭刻信息]}
		RING_BT = BigTable.BigTable("sys_ring", 100, AfterRBLoad)
		
		#{0-已预约的皇室婚礼时间档, 婚礼ID:[男方ID, 女方ID, 时间档, 烟花数量, 表白次数, 礼包数量, 宣誓次数, 是否发放礼包, 婚礼档次]}
		MarryID_Dict = Contain.Dict("MarryID_Dict", (2038, 1, 1), AfterLoad)
		
		#角色ID-->[历史最大的订婚戒指coding, 是否铭刻]
		MarryRing_Dict = Contain.Dict("MarryRing_Dict", (2038, 1, 1))
		
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleChangeGender, AfterChangeSex)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterChangeName, AfterChangeName)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_OpenPanel", "打开结婚面板"), RequestOpenWedPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Filter", "筛选结婚对象"), RequestFilter)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_MyPropose", "我的求婚"), RequestMyPropose)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Propose", "求婚"), RequestPropose)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_AnswerMarry", "响应求婚"), RequestAnswerMarry)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_ReservationWedding", "预约婚礼"), RequestReservation)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_WorldInvite", "世界邀请"), RequestWorldInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_UnionInvite", "公会邀请"), RequestUnionInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_JoinWedding", "进入婚礼场景"), RequestJoinWedding)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Vow", "宣誓"), RequestVow)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Unburden", "表白"), RequestUnburden)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Fireworks", "发烟花"), RequestFireworks)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_WeddingLibao", "发礼包"), RequestWeddingLibao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_BuyLibao", "购买礼包"), RequestBuyLibao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_GetLibao", "领取礼包"), RequestGetLibao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Handsel", "赠送贺礼"), RequestHandsel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_NowWedding", "打开当前结婚列表"), RequestNowWedding)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Divorce", "离婚"), RequestDivorce)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_CancelPropose", "取消订婚"), RequestCancelPropose)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_BuyItem", "购买物品"), RequestBuyItem)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Rebate", "回赠贺礼"), RequestRebate)
		
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_Honeymoon", "请求开启蜜月"), RequestHoneymoon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_RingImprint", "请求订婚戒指铭刻"), RequestRingImprint)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_RingEquipment", "请求装备订婚戒指"), RequestRingEquipment)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Marry_HoneySay", "请求发送甜言蜜语"), RequestHoneySay)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
	