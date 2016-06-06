#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Marry.MarryParty")
#===============================================================================
# 结婚派对
#===============================================================================
import time
import random
import datetime
import Environment
import cRoleMgr
import cProcess
import cDateTime
import cSceneMgr
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer import Init
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from World import Define
from Game.Role.Mail import Mail
from Game.Role import Call, Status, Event, KuaFu
from Game.Persistence import Contain
from Game.GlobalData import ZoneName
from Game.Marry import MarryConfig
from Game.SysData import WorldData, WorldDataNotSync
from Game.Role.Data import EnumInt8, EnumObj, EnumDayInt8, EnumInt32, EnumInt1,\
	EnumCD, EnumTempObj
from Game.Activity.Title import Title
from Game.Activity.RewardBuff import RewardBuff

if "_HasLoad" not in dir():
	#{(manId, womenId):{2:高级Party,3:豪华Party,4:今日Party,5:开始时间,6:PartyID,7:{roleid:免费喜糖次数},8:[男方名字, 女方名字],9:{roleid:剩余发放喜糖次数},10:服务器名字}}
	PartyAllData = AutoMessage.AllotMessage("PartyAllData", "当前所有结婚派对数据")
	#{(manId, womenId):{2:高级Party,3:豪华Party,4:今日Party,5:开始时间,6:PartyID,7:{roleid:免费喜糖次数},8:[男方名字, 女方名字],9:{roleid:剩余发放喜糖次数},10:服务器名字}}
	PartyOwnData = AutoMessage.AllotMessage("PartyOwnData", "自己的结婚派对数据")
	#跨服派对数据
	#{(manId, womenId):{2:高级Party,3:豪华Party,4:今日Party,5:开始时间,6:PartyID,7:{roleid:免费喜糖次数},8:[男方名字, 女方名字],9:{roleid:剩余发放喜糖次数},10:服务器名字}}
	PartyKuafuData = AutoMessage.AllotMessage("PartyKuafuData", "跨服结婚派对数据")
	#(免费次数, 剩余次数, Party档次, 男方名字, 女方名字)
	PartyHostData = AutoMessage.AllotMessage("PartyHostData", "结婚派对主人数据")
	#{(男方ID, 女方ID):{0:[男方名字, 女方名字], 1:派对档次, 2:{role_id:[普通祝福, 高级祝福]}}}
	PartyGuestData = AutoMessage.AllotMessage("PartyGuestData", "结婚派对宾客数据")
	#邀请伴侣(邀请人名字, 男方ID, 女方ID)
	PartyInvite = AutoMessage.AllotMessage("PartyInvite", "结婚派对邀请对象")
	#跨服邀请伴侣--邀请人名字
	PartyKuafuInvite = AutoMessage.AllotMessage("PartyKuafuInvite", "结婚跨服派对邀请对象")
	#是否可以进入跨服派对
	PartyKuafuCanJoin = AutoMessage.AllotMessage("PartyKuafuCanJoin", "结婚派对是否可以进入跨服派对")
	#竞拍记录 -- [[玩家名字, 服务器名字, 价格]] -- 已序, 后面得是最高的
	PartyKuafuAuctionRecord = AutoMessage.AllotMessage("PartyKuafuAuctionRecord", "结婚派对跨服竞拍记录")
	#喜庆度
	PartyKuafuHappyCnt = AutoMessage.AllotMessage("PartyKuafuHappyCnt", "结婚派对跨服喜庆度")
	#喜庆度礼盒领取记录
	PartyKuafuHappyBoxRecord = AutoMessage.AllotMessage("PartyKuafuHappyBoxRecord", "结婚派对跨服喜庆度礼盒领取记录")
	#跨服派对是否消费喜庆度
	PartyKuafuHappyConsumeRecord = AutoMessage.AllotMessage("PartyKuafuHappyConsumeRecord", "结婚派对跨服喜庆度消费记录")
	
	PartyHostAdvance_Log = AutoLog.AutoTransaction("PartyHostAdvance_Log", "举办高级结婚派对")
	PartyHostLuxury_Log = AutoLog.AutoTransaction("PartyHostLuxury_Log", "举办豪华结婚派对")
	PartyHostKuafu_Log = AutoLog.AutoTransaction("PartyHostKuafu_Log", "举办跨服结婚派对")
	
	PartyCandy_Log = AutoLog.AutoTransaction("PartyCandy_Log", "结婚派对赠送普通喜糖")
	PartyCandyAdvance_Log = AutoLog.AutoTransaction("PartyCandyAdvance_Log", "结婚派对赠送高级喜糖")
	PartyCandyLuxury_Log = AutoLog.AutoTransaction("PartyCandyLuxury_Log", "结婚派对赠送豪华喜糖")
	
	PartyBless_Log = AutoLog.AutoTransaction("PartyBless_Log", "结婚派对普通祝福")
	PartyBlessAdvance_Log = AutoLog.AutoTransaction("PartyBlessAdvance_Log", "结婚派对高级祝福")
	
	KuafuAuction_Log = AutoLog.AutoTransaction("KuafuAuction_Log", "跨服竞拍")
	
	KuafuFlower_Log = AutoLog.AutoTransaction("KuafuFlower_Log", "跨服派对送花")
	KuafuFireworks_Log = AutoLog.AutoTransaction("KuafuFireworks_Log", "跨服派对放烟花")
	KuafuHappyReward_Log = AutoLog.AutoTransaction("KuafuHappyReward_Log", "跨服派对喜庆度礼盒")
	
#===============================================================================
# 服务器tick触发函数
#===============================================================================
def BeginParty(argv, param):
	#非跨服逻辑进程
	#活动开始将Party状态设置为开始
	manId, manName, womenId, womenName, partyGrade = param
	
	nowDays = cDateTime.Days()
	Call.LocalDBCall(manId, SetPartyStatusEx, (2, nowDays))
	Call.LocalDBCall(womenId, SetPartyStatusEx, (2, nowDays))
	
	partyName = GlobalPrompt.ReturnPartyGrade(partyGrade)
	if not partyName:
		print 'GE_EXC, MarryParty BeginParty can not find party grade %s' % partyGrade
		return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyBeginNormal % (manName, womenName, partyName, manId, womenId))
	
def BeginPartyEx(param):
	if not WorldData.WD.returnDB:
		return
	if WorldData.GetWorldKaiFuDay() < 10:
		#开服天数小于10天的不发跨服派对传闻
		return
	
	#########################################跨服进程调用######################################
	#活动开始将Party状态设置为开始
	manId, manName, womenId, womenName, partyGrade = param
	
	partyName = GlobalPrompt.ReturnPartyGrade(partyGrade)
	if not partyName:
		print 'GE_EXC, MarryParty BeginParty can not find party grade %s' % partyGrade
		return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyBeginKuafu % (manName, womenName, partyName, manId, womenId))
	
def OneMinuteTips(argv, param):
	#Party结束前一分钟提示
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyOneMinuteTips % param)
	
def EndParty(argv, param):
	#活动结束将Party状态设置为完成, 并增加亲密度
	manId, manName, womenId, womenName, qinmi, partyGrade = param
	
	cfg = MarryConfig.PartyGrade_Dict.get(partyGrade)
	if cfg and cfg.qinmi:
		qinmi = cfg.qinmi
	
	nowDays = cDateTime.Days()
	Call.LocalDBCall(manId, SetPartyStatusEx, (3, nowDays))
	Call.LocalDBCall(manId, OutLineIncQinmiEx, (RewardBuff.CalNumber(RewardBuff.enMarryParty, qinmi), partyGrade))
	Call.LocalDBCall(womenId, SetPartyStatusEx, (3, nowDays))
	Call.LocalDBCall(womenId, OutLineIncQinmiEx, (RewardBuff.CalNumber(RewardBuff.enMarryParty, qinmi), partyGrade))
	
	global PartyBlessDict
	#删除Party祝福数据
	if (manId, womenId) in PartyBlessDict:
		del PartyBlessDict[(manId, womenId)]
	#同步所有人祝福数据
	cNetMessage.PackPyMsg(PartyGuestData, PartyBlessDict)
	cRoleMgr.BroadMsg()
	
	#删除Party数据
	global MarryPartyDict
	if (manId, womenId) not in MarryPartyDict[1]:
		print 'GE_EXC, MarryParty EndParty can not find (%s, %s) in MarryPartyDict[1]' % (manId, womenId)
		return
	del MarryPartyDict[1][(manId, womenId)]
	MarryPartyDict.changeFlag = True
	
	#同步所有人最新的派对数据
	cNetMessage.PackPyMsg(PartyAllData, MarryPartyDict.get(1, {}))
	cRoleMgr.BroadMsg()
	
	partyName = GlobalPrompt.ReturnPartyGrade(partyGrade)
	if not partyName:
		print 'GE_EXC, MarryParty EndParty can not find party grade name %s' % partyGrade
		return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyEnd % (manName, womenName, partyName))
	
	#魅力情人节-魅力派对活动开启 处理相关逻辑
	from Game.Activity.ValentineDay import GlamourPartyMgr
	if GlamourPartyMgr.IS_START:
		Call.LocalDBCall(manId, GlamourPartyMgr.AfterParty, (partyGrade, nowDays, qinmi))
		Call.LocalDBCall(womenId, GlamourPartyMgr.AfterParty, (partyGrade, nowDays, qinmi))
	
	#王者公测奖励狂翻倍触发任务进度
	from Game.Activity.WangZheGongCe import WangZheCrazyRewardMgr
	Call.LocalDBCall(manId, WangZheCrazyRewardMgr.AfterParty, nowDays)
	Call.LocalDBCall(womenId, WangZheCrazyRewardMgr.AfterParty, nowDays)
	
	#激情活动奖励狂翻倍触发任务进度
	from Game.Activity.PassionAct import PassionMultiRewardMgr
	Call.LocalDBCall(manId, PassionMultiRewardMgr.AfterParty, nowDays)
	Call.LocalDBCall(womenId, PassionMultiRewardMgr.AfterParty, nowDays)
	
def EndPartyEx(param):
	if not WorldData.WD.returnDB:
		return
	if WorldData.GetWorldKaiFuDay() < 10:
		return
	
	#########################################跨服进程调用######################################
	
	#活动结束将Party状态设置为完成, 并增加亲密度
	manId, manName, womenId, womenName, partyGrade = param
	
	cfg = MarryConfig.PartyGrade_Dict.get(partyGrade)
	if not cfg:
		print 'GE_EXC, MarryParty EndPartyEx can not find party grade %s in PartyGrade_Dict' % partyGrade
		return
	
	if KuaFu.IsLocalRoleByRoleID(manId):
		Call.LocalDBCall(manId, OutLineIncQinmiEx, (RewardBuff.CalNumber(RewardBuff.enMarryParty, cfg.qinmi), partyGrade))
		Call.LocalDBCall(womenId, OutLineIncQinmiEx, (RewardBuff.CalNumber(RewardBuff.enMarryParty, cfg.qinmi), partyGrade))
		global KuafuPartyCntDict
		if not KuafuPartyCntDict.returnDB:
			print 'GE_EXC, MarryParty EndPartyEx KuafuPartyCntDict not returnDB'
		else:
			if manId not in KuafuPartyCntDict:
				KuafuPartyCntDict[manId] = 1
			else:
				KuafuPartyCntDict[manId] += 1
			KuafuPartyCntDict.changeFlag = True
			
			if KuafuPartyCntDict[manId] == 3:
				Title.AddTitle(manId, EnumGameConfig.PartyKuafuTitleID)
				Title.AddTitle(womenId, EnumGameConfig.PartyKuafuTitleID)
			
	partyName = GlobalPrompt.ReturnPartyGrade(partyGrade)
	if not partyName:
		print 'GE_EXC, MarryParty EndParty can not find party grade name %s' % partyGrade
		return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyEnd % (manName, womenName, partyName))
	
	if KuaFu.IsLocalRoleByRoleID(manId):
		#魅力情人节-魅力派对活动开启 处理相关逻辑
		from Game.Activity.ValentineDay import GlamourPartyMgr
		if GlamourPartyMgr.IS_START:
			nowDays = cDateTime.Days()
			Call.LocalDBCall(manId, GlamourPartyMgr.AfterParty, (partyGrade, nowDays, cfg.qinmi))
			Call.LocalDBCall(womenId, GlamourPartyMgr.AfterParty, (partyGrade, nowDays, cfg.qinmi))
			
#===============================================================================
# 离线函数
#===============================================================================
def SetPartyStatus(role, param):
	#设置Party状态(之前的离线命令不要删除)
	role.SetDI8(EnumDayInt8.PartyStatus, param)
	
def SetPartyStatusEx(role, param):
	#设置Party状态
	status, days = param
	
	if cDateTime.Days() != days:
		return
	
	role.SetDI8(EnumDayInt8.PartyStatus, status)
	
def OutLineIncQinmi(role, qinmi):
	#增加亲密度
	role.IncI32(EnumInt32.Qinmi, qinmi)
	
def OutLineIncQinmiEx(role, param):
	#增加亲密度
	qinmi, partyGrade = param
	
	if partyGrade == 1:
		log = PartyHostAdvance_Log
	elif partyGrade == 2:
		log = PartyHostLuxury_Log
	elif partyGrade == 3:
		log = PartyHostKuafu_Log
	else:
		print 'GE_EXC, MarryParty OutLineIncQinmiEx can not find party grade %s' % partyGrade
		return
	
	with log:
		role.IncI32(EnumInt32.Qinmi, qinmi)
		if partyGrade:
			if Environment.EnvIsNA():
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.FinishParty(partyGrade)
#===============================================================================
# 邮件
#===============================================================================
def SendBless(roleId, roleName, coding):
	#发送祝福邮件
	Mail.SendMail(roleId, GlobalPrompt.PartyBless_Title, GlobalPrompt.PartyBless_Sender, GlobalPrompt.PartyBless_Content % roleName, items=[(coding, 1)])
	
def SendCandyMail(roleId, manName, womenName, coding):
	#发送喜糖邮件
	Mail.SendMail(roleId, GlobalPrompt.PartyCandy_Title, GlobalPrompt.PartyCandy_Sender, GlobalPrompt.PartyCandy_Content % (manName, womenName), items=[(coding, 1)])
	
def SendEmptyBless(roleId, roleName, blessGrade):
	#发送空的祝福邮件
	Mail.SendMail(roleId, GlobalPrompt.PartyBless_Title, GlobalPrompt.PartyBless_Sender, GlobalPrompt.PartyBless_Content_2 % (roleName, blessGrade))
#===============================================================================
# 辅助
#===============================================================================
def SendCandy(role, marryId, candyCoding, qinmi, manName, womenName):
	#发放喜糖
	scene = cSceneMgr.SearchPublicScene(role.GetSceneID())
	if not scene:
		return
	for srole in scene.GetAllRole():
		#给参加Party的所有宾客发喜糖, 每人一个, 自己不发
		if role == srole:
			continue
		SendCandyMail(srole.GetRoleID(), manName, womenName, candyCoding)
	#加亲密度
	role.IncI32(EnumInt32.Qinmi, qinmi)
	Call.LocalDBCall(marryId, OutLineIncQinmi, qinmi)
	
def ReturnMarryData(role):
	#返回结婚双方信息
	#错误返回 None
	#正确返回 男方ID, 男方名字, 女方ID, 女方名字, 请求方ID, 结婚对象ID
	roleId = role.GetRoleID()
	
	from Game.Marry import MarryMgr
	if role.GetSex() == 1:
		manId = role.GetRoleID()
		manName = role.GetRoleName()
		womenId = marryId = role.GetObj(EnumObj.MarryObj).get(1)
		womenName = MarryMgr.GetMarryRoleName(role)
		if not womenName:
			return
	else:
		manId = marryId = role.GetObj(EnumObj.MarryObj).get(1)
		manName = MarryMgr.GetMarryRoleName(role)
		if not manName:
			return
		womenId = role.GetRoleID()
		womenName = role.GetRoleName()
	return manId, manName, womenId, womenName, roleId, marryId

def SyncOwnPartyData(role, manId, womenId, partyData):
	#同步自己的派对数据
	role.SendObj(PartyOwnData, {(manId, womenId):partyData})
	
	hostData = ReturnOwnPartyData(role)
	if hostData:
		role.SendObj(PartyHostData, hostData)
	
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		return
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
	if not marryRole:
		return
	marryRole.SendObj(PartyOwnData, {(manId, womenId):partyData})
	if hostData:
		marryRole.SendObj(PartyHostData, hostData)
	
def ReturnOwnPartyData(role):
	global MarryPartyDict
	if not MarryPartyDict.returnDB:
		return
	marryData = ReturnMarryData(role)
	if not marryData:
		return
	manId, manName, womenId, womenName, _, _ = marryData
	partyData = MarryPartyDict[1].get((manId, womenId))
	if not partyData:
		return
	roleId = role.GetRoleID()
	return partyData[7].get(roleId, 0), partyData[9].get(roleId, 0), partyData[4], manName, womenName

def GetServerType():
	#返回服务器类型
	return WorldDataNotSync.GetData(WorldDataNotSync.PartyServerType)

def AfterJoinKuafuParty(role, (processId, st)):
	#########################################跨服逻辑######################################
	
	global CanInKuafuParty
	if not CanInKuafuParty:
		role.GotoLocalServer(None, None)
		return
	
	#玩家加入跨服派对后处理
	global ProcessToServerType
	serverType = ProcessToServerType.get(processId)
	if not serverType:
		#根据进程ID获取跨服进程保存的服务器类型
		print 'GE_EXC, MarryParty AfterJoinKuafuParty can not find server type by %s' % processId
		role.GotoLocalServer(None, None)
		return
	if serverType != st:
		#跨服进程保存的服务器类型和本地进程的不一致
		print 'GE_EXC, MarryParty AfterJoinKuafuParty logic server type %s != cross save server type %s' % (st, serverType)
		role.GotoLocalServer(None, None)
		return
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty AfterJoinKuafuParty server type error %s' % serverType
		role.GotoLocalServer(None, None)
		return
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB:
		print 'GE_EXC, MarryParty AfterJoinKuafuParty not KuafuPartyDict.returnDB'
		role.GotoLocalServer(None, None)
		return
	partyData = KuafuPartyDict[2].get(serverType)
	if not partyData:
		print 'GE_EXC, MarryParty AfterJoinKuafuParty can not find party data by server type %s' % serverType
		role.GotoLocalServer(None, None)
		return
	
	roleId = role.GetRoleID()
	isOwn = False
	for idTuple, pData in KuafuPartyDict[2][serverType].iteritems():
		if roleId in idTuple:
			isOwn = True
			break
	
	if not isOwn:
		global kuafuPartyRoleCnt_Dict
		if serverType not in kuafuPartyRoleCnt_Dict:
			kuafuPartyRoleCnt_Dict[serverType] = 1
		else:
			kuafuPartyRoleCnt_Dict[serverType] += 1
		
		if kuafuPartyRoleCnt_Dict[serverType] == EnumGameConfig.PartyCloseCnt:
			#通知该服务器类型的逻辑进程关闭入口
			serverIdSet = ServerTypeDict.get(serverType)
			if not serverIdSet:
				print 'GE_EXC, MarryParty AfterJoinKuafuParty can not find server id set in server type dict by server type %s' % serverType
				return
			
			global ServerTypeIsClose
			ServerTypeIsClose[serverType] = True
			
			for serverId in serverIdSet:
				Call.ServerCall(serverId, "Game.Marry.MarryParty", "SetCanInKuafuParty", False)
		
		if kuafuPartyRoleCnt_Dict[serverType] >= EnumGameConfig.PartyKickCnt:
			#开始踢人
			role.GotoLocalServer(None, None)
		
	global HappyCntDict
	if isOwn:
		#是自己的派对
		#(免费次数, 剩余次数, Party档次, 男方名字, 女方名字)
		role.SendObj(PartyHostData, (pData[7].get(roleId, 0), pData[9].get(roleId, 0), pData[4], pData[8][0], pData[8][1]))
		#同步新人领取喜庆度礼盒奖励记录
		global HappyCntHostRewardRecordDict
		role.SendObj(PartyKuafuHappyBoxRecord, HappyCntHostRewardRecordDict.get(serverType, set()))
		#同步喜庆度
		role.SendObj(PartyKuafuHappyCnt, (HappyCntDict.get(serverType, 0), 0))
	else:
		#别人的派对
		global PartyBlessDict
		if serverType not in PartyBlessDict:
			PartyBlessDict[serverType] = {}
		if idTuple not in PartyBlessDict[serverType]:
			PartyBlessDict[serverType][idTuple] = {0:pData[8], 1:3, 2:{}}
		#{(男方ID, 女方ID):{0:[男方名字, 女方名字], 1:派对档次, 2:{role_id:[普通祝福, 高级祝福]}}}
		role.SendObj(PartyGuestData, PartyBlessDict[serverType])
		#同步领取喜庆度礼盒奖励记录
		global HappyCntGuessRewardRecordDict
		role.SendObj(PartyKuafuHappyBoxRecord, HappyCntGuessRewardRecordDict.get(serverType, set()))
		#同步喜庆度
		role.SendObj(PartyKuafuHappyCnt, (HappyCntDict.get(serverType, 0), 0))
	
	global KuafuHappyIsConsumeSet
	role.SendObj(PartyKuafuHappyConsumeRecord, KuafuHappyIsConsumeSet.get(serverType, set([])))
	
def SetCanInKuafuParty(param):
	#########################################跨服进程调用######################################
	global CanInKuafuParty
	CanInKuafuParty = param
	
def IsPersistenceDataOK():
	#依赖的持久化数据时候都已经载入完毕
	if not WorldData.WD.returnDB:
		return False
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
		return False
	return True
	
def RecountServerType():
	#重算服务器类型
	if not IsPersistenceDataOK():
		return
	kaifuDay = WorldData.GetWorldKaiFuDay()
	
	for serverType, cfg in MarryConfig.PartyServerType_Dict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			break
	else:
		print 'GE_EXC, MarryParty can not find server type by kaifu day %s' % kaifuDay
	
	WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.PartyServerType] = serverType
	
def RequestServerType():
	RequestLogicServerType()
	
def SyncAuctionData(role, param):
	#########################################跨服逻辑######################################
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB:
		return
	
	marryData, processId, zoneNAME, st = param
	
	global ProcessToServerType
	serverType = ProcessToServerType.get(processId)
	if not serverType:
		role.GotoLocalServer(None, None)
		return
	if st != serverType:
		print 'GE_EXC, MarryParty SyncAuctionData logic server type %s != cross save server type %s' % (st, serverType)
		role.GotoCrossServer(None, None)
		return
	
	#同步竞拍数据
	role.SendObj(PartyKuafuAuctionRecord, KuafuPartyDict[1].get(serverType, []))
	
	#记录结婚对象数据
	roleId = role.GetRoleID()
	if roleId not in RoleProDataDict:
		RoleProDataDict[roleId] = (marryData, zoneNAME)

def InAuctionRecord(role, price, serverType, zone_name):
	#########################################跨服逻辑######################################
	#尝试进入竞拍记录
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB:
		return
	auctionRecordList = KuafuPartyDict[1].get(serverType, [])
	
	roleId, roleName = role.GetRoleID(), role.GetRoleName()
	
	with KuafuAuction_Log:
		if auctionRecordList:
			returnRoleId, _, _, returnPrice = auctionRecordList[-1]
			#返还上一次竞拍的跨服币
			Mail.SendMail(returnRoleId, GlobalPrompt.PartyAuctionFailTitle, GlobalPrompt.PartyAuctionSender, GlobalPrompt.PartyAuctionFailContent % roleName, kuafuMoney=returnPrice)
		
	#先看是否在之前的记录中, 如果在的话删除旧的记录, 加入新的记录
	for index, value in enumerate(auctionRecordList):
		if value[0] == roleId:
			auctionRecordList.pop(index)
			auctionRecordList.append([roleId, roleName, zone_name, price])
			scene = role.GetScene()
			for role in scene.GetAllRole():
				role.SendObj(PartyKuafuAuctionRecord, auctionRecordList)
			return
	#竞拍记录最多10条记录
	if len(auctionRecordList) > 9:
		auctionRecordList.pop(0)
	auctionRecordList.append([roleId, roleName, zone_name, price])
	KuafuPartyDict[1][serverType] = auctionRecordList
	KuafuPartyDict.changeFlag = True
	
	scene = role.GetScene()
	for role in scene.GetAllRole():
		role.SendObj(PartyKuafuAuctionRecord, auctionRecordList)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestHost(role, msg):
	'''
	请求立即举办派对
	@param role:
	@param msg:
	'''
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	
	#23点40分后不能举办Party
	nowHour, nowMinute = cDateTime.Hour(), cDateTime.Minute()
	if (nowHour, nowMinute) >= (23, 40):
		return
	if (nowHour, nowMinute) == (0, 0):
		#0点不能办
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		#未完婚
		return
	if role.GetI8(EnumInt8.HoneymoonStatus) != 3:
		#未完成蜜月
		return
	if role.GetDI8(EnumDayInt8.PartyStatus):
		#Party状态
		return
	
	grade = msg
	if grade not in (1, 2): return
	
	#配置
	cfg = MarryConfig.PartyGrade_Dict.get(grade)
	if not cfg:
		return
	
	isFree = False
	if grade == 1:
		#第一次举办第一档派对是免费的
		isFree = False if role.GetI1(EnumInt1.PartyIsHost) else True
	
	if (not isFree) and (role.GetUnbindRMB() < cfg.needRMB):
		return
	
	marryData = ReturnMarryData(role)
	if not marryData:
		role.Msg(2, 0, GlobalPrompt.MarryFindError)
		return
	manId, manName, womenId, womenName, roleId, _ = marryData
	
	if (manId, womenId) in MarryPartyDict[1]:
		return
	
	#没有1, 1被删掉了...
	#{2:高级Party举办次数, 3:豪华Party举办次数, 4:今日举办的Party档次, 5:Party开始时间, 6:PartyID, 7:{角色ID:免费喜糖个数}, 8:{roleid:名字}, 9:{roleid:剩余发放喜糖次数}
	MarryPartyDict[1][(manId, womenId)] = partyData = {2:0, 3:0, 4:0, 5:0, 6:0, 7:{manId:0, womenId:0}, 8:[], 9:{manId:0, womenId:0}, 10:ZoneName.ZoneName}
	
	if grade == 1:
		log = PartyHostAdvance_Log
	else:
		log = PartyHostLuxury_Log
	
	with log:
		if not isFree:
			role.DecUnbindRMB(cfg.needRMB)
		AutoLog.LogBase(roleId, AutoLog.evePartyTime, (nowHour, nowMinute))
	
	if grade == 1:
		#标记举办过普通Party了
		role.SetI1(EnumInt1.PartyIsHost, True)
	else:
		#其他Party数+1
		partyData[grade+1] += 1
	#档次
	partyData[4] = grade
	#Party开始时间戳
	partyData[5] = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	#初始化免费喜糖
	candyCnt = cfg.freeCandy
	partyData[7][manId] = candyCnt
	partyData[7][womenId] = candyCnt
	#名字
	partyData[8] = [manName, womenName]
	#剩余次数
	partyData[9][manId] = cfg.candyCnt
	partyData[9][womenId] = cfg.candyCnt
	
	MarryPartyDict[1][(manId, womenId)] = partyData
	MarryPartyDict.changeFlag = True
	
	#直接开启Party
	BeginParty(None, (manId, manName, womenId, womenName, grade))
	
	#注册20分钟后结束Party
	cComplexServer.RegTick(1200, EndParty, (manId, manName, womenId, womenName, cfg.qinmi, grade))
	#注册19分钟后提示
	cComplexServer.RegTick(1140, OneMinuteTips, (manName, womenName))
	
	#广播所有人
	cNetMessage.PackPyMsg(PartyAllData, MarryPartyDict.get(1, {}))
	cRoleMgr.BroadMsg()
	#同步自己和伴侣
	SyncOwnPartyData(role, manId, womenId, partyData)
	
def RequestReservation(role, msg):
	'''
	请求预约派对
	@param role:
	@param msg:
	'''
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if role.GetI8(EnumInt8.HoneymoonStatus) != 3:
		return
	#Party状态
	if role.GetDI8(EnumDayInt8.PartyStatus):
		return
	if not msg: return
	
	grade, hour, minute = msg
	
	if grade != 2:
		#暂时只有第二档可以预约
		return
	if not role.GetI1(EnumInt1.PartyIsHost):
		#需要先办过第一档派对才能办第二档
		return
	#只能预约20分和40分
	if minute not in (20, 40):
		return
	#23:40不能预约
	if (hour, minute) == (23, 40):
		return
	#0点不能预约
	if (hour, minute) == (0, 0):
		return
	cfg = MarryConfig.PartyGrade_Dict.get(grade)
	if not cfg:
		return
	if role.GetUnbindRMB() < cfg.needRMB:
		return
	marryData = ReturnMarryData(role)
	if not marryData:
		role.Msg(2, 0, GlobalPrompt.MarryFindError)
		return
	manId, manName, womenId, womenName, roleId, _ = marryData
	#有数据了
	if (manId, womenId) in MarryPartyDict[1]:
		return
	#判断预约时间
	nowHour, nowMinute = cDateTime.Hour(), cDateTime.Minute()
	if (nowHour, nowMinute) >= (hour, minute):
		return
	
	nowTime = cDateTime.Seconds()
	beginTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), hour, minute, 0).timetuple()))
	if beginTime <= nowTime:
		return
	
	#{2:高级Party举办次数, 3:豪华Party举办次数, 4:今日举办的Party档次, 5:Party开始时间, 6:PartyID, 7:{角色ID:免费喜糖个数}, 8:[男方名字, 女方名字], 9:{roleid:剩余发放喜糖次数}
	MarryPartyDict[1][(manId, womenId)] = partyData = {2:0, 3:0, 4:0, 5:0, 6:0, 7:{manId:0, womenId:0}, 8:[], 9:{manId:0, womenId:0}, 10:ZoneName.ZoneName}
	
	if grade == 1:
		log = PartyHostAdvance_Log
	else:
		log = PartyHostLuxury_Log
	
	with log:
		role.DecUnbindRMB(cfg.needRMB)
		AutoLog.LogBase(roleId, AutoLog.evePartyTime, (hour, minute))
	
	partyData[grade] += 1
	#档次
	partyData[4] = grade
	#开始时间戳
	partyData[5] = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), hour, minute, 0).timetuple()))
	#喜糖
	partyData[7][manId] = cfg.freeCandy
	partyData[7][womenId] = cfg.freeCandy
	#名字
	partyData[8] = [manName, womenName]
	#剩余次数
	partyData[9][manId] = cfg.candyCnt
	partyData[9][womenId] = cfg.candyCnt
	
	MarryPartyDict[1][(manId, womenId)] = partyData
	MarryPartyDict.changeFlag = True
	
	nowDays = cDateTime.Days()
	Call.LocalDBCall(manId, SetPartyStatusEx, (1, nowDays))
	Call.LocalDBCall(womenId, SetPartyStatusEx, (1, nowDays))
	
	cComplexServer.RegTick(beginTime - nowTime, BeginParty, (manId, manName, womenId, womenName, grade))
	
	cComplexServer.RegTick(beginTime - nowTime + 1200, EndParty, (manId, manName, womenId, womenName, cfg.qinmi, grade))
	#注册19分钟后提示
	cComplexServer.RegTick(beginTime - nowTime + 1140, OneMinuteTips, (manName, womenName))
	
	#广播所有人
	cNetMessage.PackPyMsg(PartyAllData, MarryPartyDict.get(1, {}))
	cRoleMgr.BroadMsg()
	#同步自己和伴侣
	SyncOwnPartyData(role, manId, womenId, partyData)
	
def RequestJoin(role, msg):
	'''
	请求进入派对
	@param role:
	@param msg:
	'''
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	
	if not Status.CanInStatus(role, EnumInt1.ST_MarryParty):
		return
	if role.GetLevel() < EnumGameConfig.PartyLvLimit:
		return
	if role.GetSceneID() == EnumGameConfig.PartySceneID:
		return
	partyData = MarryPartyDict[1].get(msg)
	if not partyData:
		return
	
	nowSec = cDateTime.Seconds()
	beginSec = partyData[5]
	
	if (not beginSec) or (nowSec < beginSec) or (nowSec >= (1200 + beginSec)):
		role.Msg(2, 0, GlobalPrompt.PartyNotBegin)
		return
	
	global PartyRevivePos
	role.Revive(EnumGameConfig.PartySceneID, *PartyRevivePos)
	
def RequestWorldInvite(role, msg):
	'''
	请求世界邀请
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		CrossWorldInvite(role)
	else:
		LogicWorldInvite(role)
	
def CrossWorldInvite(role):
	#跨服逻辑
	global CanInKuafuParty
	if not CanInKuafuParty: return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB: return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	if role.GetCD(EnumCD.PartyKuafuWInviteCD):
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if not role.GetI1(EnumInt1.PartyIsHost):
		#必须要举办过免费派对才能举办跨服派对
		return
	
	roleId = role.GetRoleID()
	for idTuple, pData in KuafuPartyDict[2][serverType].iteritems():
		if roleId not in idTuple:
			return
		break
	partyGradeName = GlobalPrompt.ReturnPartyGrade(3)
	if not partyGradeName:
		return
	manName, womenName = pData[8]
	manId, womenId = idTuple
	
	for serverId in ServerTypeDict[serverType]:
		Call.ServerCall(serverId, "Game.Marry.MarryParty", "WorldInvite", ((manName, womenName, partyGradeName, manId, womenId)))
	
	role.SetCD(EnumCD.PartyKuafuWInviteCD, EnumGameConfig.PartyKuafuCD)
	
	role.Msg(2, 0, GlobalPrompt.PartyKuafuInviteSuccess)
	
def WorldInvite(inviteData):
	if not WorldData.WD.returnDB:
		return
	if WorldData.GetWorldKaiFuDay() < 10:
		return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyWorldInvite_Kuafu % inviteData)
	
def LogicWorldInvite(role):
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	
	if role.GetSceneID() != EnumGameConfig.PartySceneID: return
	
	if role.GetCD(EnumCD.PartyWorldIvCD):
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if role.GetI8(EnumInt8.HoneymoonStatus) != 3:
		return
	
	marryData = ReturnMarryData(role)
	if not marryData:
		return
	manId, manName, womenId, womenName, _, _ = marryData
	
	partyData = MarryPartyDict[1].get((manId, womenId))
	if not partyData:
		return
	
	if not partyData[4]:
		return
	
	beginSec = partyData[5]
	if not beginSec or cDateTime.Seconds() < beginSec: return
	
	partyGradeName = GlobalPrompt.ReturnPartyGrade(partyData[4])
	if not partyGradeName:
		return
	
	role.SetCD(EnumCD.PartyWorldIvCD, EnumGameConfig.PartyCD)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyWorldInvite_Logic % (manName, womenName, partyGradeName, manId, womenId))
	
def RequestInvite(role, msg):
	'''
	请求邀请伴侣
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		CrossInviteMRole(role)
	else:
		LogicInviteMRole(role)
	
def CrossInviteMRole(role):
	global CanInKuafuParty
	if not CanInKuafuParty: return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB: return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	if role.GetCD(EnumCD.PartyKuafuMInviteCD):
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if not role.GetI1(EnumInt1.PartyIsHost):
		#必须要举办过免费派对才能举办跨服派对
		return
	
	roleId, roleName = role.GetRoleID(), role.GetRoleName()
	for idTuple, _ in KuafuPartyDict[2][serverType].iteritems():
		if roleId not in idTuple:
			return
		break
	
	for serverId in ServerTypeDict[serverType]:
		Call.ServerCall(serverId, "Game.Marry.MarryParty", "KuafuInviteMarryRole", ((role.GetObj(EnumObj.MarryObj).get(1, 0), roleName)))
	
	role.SetCD(EnumCD.PartyKuafuMInviteCD, EnumGameConfig.PartyKuafuCD)
	
def LogicInviteMRole(role):
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	if role.GetSceneID() != EnumGameConfig.PartySceneID: return
	
	marryData = ReturnMarryData(role)
	if not marryData:
		return
	manId, _, womenId, _, _, marryId = marryData
	
	marryRole = cRoleMgr.FindRoleByRoleID(marryId)
	if not marryRole:
		#对象不在线
		role.Msg(2, 0, GlobalPrompt.PartyNotOnLine)
		return
	partyData = MarryPartyDict[1].get((manId, womenId))
	if not partyData:
		#没有派对数据
		return
	if not partyData[4]:
		#派对结束了
		return
	if marryRole.GetSceneID() == EnumGameConfig.PartySceneID:
		#对象在场景中
		return
	
	beginSec = partyData[5]
	if not beginSec or cDateTime.Seconds() < beginSec: return
	
	role.SetCD(EnumCD.PartyInviteCD, EnumGameConfig.PartyCD)
	
	marryRole.SendObj(PartyInvite, (role.GetRoleName(), manId, womenId))
	
def KuafuInviteMarryRole(param):
	roleId, inviteName = param
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role:
		return
	role.SendObj(PartyKuafuInvite, inviteName)
	
def RequestCandy(role, msg):
	'''
	请求发放喜糖
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		CrossCandy(role, msg)
	else:
		LogicCandy(role, msg)
	
def CrossCandy(role, candyGrade):
	global CanInKuafuParty
	if not CanInKuafuParty: return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB: return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	if role.GetCD(EnumCD.PartyWorldIvCD):
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if not role.GetI1(EnumInt1.PartyIsHost):
		#必须要举办过免费派对才能举办跨服派对
		return
	
	roleId = role.GetRoleID()
	for idTuple, partyData in KuafuPartyDict[2][serverType].iteritems():
		if roleId not in idTuple:
			return
		break
	marryId = role.GetObj(EnumObj.MarryObj).get(1)
	
	if not partyData:
		return
	if not partyData[4]:
		return
	
	beginSec = partyData[5]
	if not beginSec or cDateTime.Seconds() < beginSec:
		return
	
	#不能发超过Party档次的喜糖
	if candyGrade > partyData[4]:
		return
	
	cfg = MarryConfig.PartyCandyGrade_Dict.get(candyGrade)
	if not cfg:
		return
	candyName = GlobalPrompt.ReturnCandyGrade(candyGrade)
	if not candyName:
		return
	
	if candyGrade == 1:
		log = PartyCandy_Log
	elif candyGrade == 2:
		log = PartyCandyAdvance_Log
	else:
		log = PartyCandyLuxury_Log
	
	with log:
		if partyData[7][roleId]:
			#有免费喜糖
			partyData[7][roleId] -= 1
			KuafuPartyDict[2][serverType][idTuple] = partyData
			KuafuPartyDict.changeFlag = True
			
			manName, womenName = partyData[8][0], partyData[8][1]
			
			SendCandy(role, marryId, cfg.candyCoding, cfg.qinmi, manName, womenName)
			
			role.SendObj(PartyHostData, (partyData[7][roleId], partyData[9][roleId], partyData[4], manName, womenName))
			
			#记录发放的喜糖
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.evePartySendCandy, (partyData[4], candyGrade))
			
			role.GetScene().Msg(1, 0, GlobalPrompt.PartyCandy % (manName, womenName, candyName))
		elif partyData[9][roleId] > 0:
			#还有剩余次数
			if role.GetKuaFuMoney() < cfg.needRMB:
				return
			role.DecKuaFuMoney(cfg.needRMB)
			
			partyData[9][roleId] -= 1
			
			KuafuPartyDict[2][serverType][idTuple] = partyData
			KuafuPartyDict.changeFlag = True
			
			manName, womenName = partyData[8][0], partyData[8][1]
			
			SendCandy(role, marryId, cfg.candyCoding, cfg.qinmi, manName, womenName)
			
			role.SendObj(PartyHostData, (partyData[7][roleId], partyData[9][roleId], partyData[4], manName, womenName))
			
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.evePartySendCandy, (partyData[4], candyGrade))
			
			role.GetScene().Msg(1, 0, GlobalPrompt.PartyCandy % (manName, womenName, candyName))
		else:
			return
	
def LogicCandy(role, candyGrade):
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	if role.GetSceneID() != EnumGameConfig.PartySceneID: return
	
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	if role.GetI8(EnumInt8.HoneymoonStatus) != 3:
		return
	
	marryData = ReturnMarryData(role)
	if not marryData:
		return
	manId, _, womenId, _, roleId, marryId = marryData
	partyData = MarryPartyDict[1].get((manId, womenId))
		
	if not partyData:
		return
	if not partyData[4]:
		return
	
	beginSec = partyData[5]
	if not beginSec or cDateTime.Seconds() < beginSec:
		return
	
	#不能发超过Party档次的喜糖
	if candyGrade > partyData[4]:
		return
	
	cfg = MarryConfig.PartyCandyGrade_Dict.get(candyGrade)
	if not cfg:
		return
	candyName = GlobalPrompt.ReturnCandyGrade(candyGrade)
	if not candyName:
		return
	
	if candyGrade == 1:
		log = PartyCandy_Log
	elif candyGrade == 2:
		log = PartyCandyAdvance_Log
	else:
		log = PartyCandyLuxury_Log
	
	with log:
		if partyData[7][roleId]:
			#有免费喜糖
			partyData[7][roleId] -= 1
			MarryPartyDict[1][(manId, womenId)] = partyData
			MarryPartyDict.changeFlag = True
			
			manName, womenName = partyData[8][0], partyData[8][1]
			
			SendCandy(role, marryId, cfg.candyCoding, cfg.qinmi, manName, womenName)
			
			role.SendObj(PartyHostData, (partyData[7][roleId], partyData[9][roleId], partyData[4], manName, womenName))
			
			AutoLog.LogBase(roleId, AutoLog.evePartySendCandy, (partyData[4], candyGrade))
			
			cRoleMgr.Msg(1, 0, GlobalPrompt.PartyCandy % (manName, womenName, candyName))
		elif partyData[9][roleId] > 0:
			#还有剩余次数
			if role.GetUnbindRMB() < cfg.needRMB:
				return
			role.DecUnbindRMB(cfg.needRMB)
			
			partyData[9][roleId] -= 1
			
			MarryPartyDict[1][(manId, womenId)] = partyData
			MarryPartyDict.changeFlag = True
			
			manName, womenName = partyData[8][0], partyData[8][1]
			
			SendCandy(role, marryId, cfg.candyCoding, cfg.qinmi, manName, womenName)
			
			role.SendObj(PartyHostData, (partyData[7][roleId], partyData[9][roleId], partyData[4], manName, womenName))
			
			AutoLog.LogBase(roleId, AutoLog.evePartySendCandy, (partyData[4], candyGrade))
			
			cRoleMgr.Msg(1, 0, GlobalPrompt.PartyCandy % (manName, womenName, candyName))
		else:
			return
		
def RequestBless(role, msg):
	'''
	请求祝福
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		CrossBless(role, msg)
	else:
		LogicBless(role, msg)
	
def CrossBless(role, (blessGrade, manId, womenId)):
	global CanInKuafuParty
	if not CanInKuafuParty: return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB: return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	if role.GetDI8(EnumDayInt8.PartyBlessCnt) >= EnumGameConfig.PartyBlessMaxCnt:
		return
	
	roleName = role.GetRoleName()
	
	partyData = KuafuPartyDict[2][serverType].get((manId, womenId))
	
	if not partyData:
		return
	#自己不能给自己祝福
	roleId = role.GetRoleID()
	if roleId in (manId, womenId):
		return
	
	if blessGrade not in (1, 2):
		return
	
	global PartyBlessDict
	blessData = PartyBlessDict[serverType].get((manId, womenId))
	if not blessData:
		print 'GE_EXC, MarryParty RequestBless can not find server type %s bless data by (%s, %s)' % (serverType, manId, womenId)
		return
	
	if roleId not in blessData[2]:
		blessData[2][roleId] = [0, 0]
	
	if blessData[2][roleId][blessGrade-1]:
		#已经祝福过了
		return
	
	cfg = MarryConfig.PartyBless_Dict.get(blessGrade)
	if not cfg:
		return
	
	isFree = False
	if cfg.needMoney:
		useMoney = True
		if role.GetMoney() < cfg.needMoney:
			return
	elif cfg.needRMB:
		useMoney = False
		if role.GetKuaFuMoney() < cfg.needRMB:
			return
	else:
		isFree = True
	
	beginSec = partyData[5]
	if not beginSec or cDateTime.Seconds() < beginSec: return
	
	blessName = GlobalPrompt.ReturnBlessGrade(blessGrade)
	if not blessName:
		return
	
	if blessGrade == 1:
		log = PartyBless_Log
	else:
		log = PartyBlessAdvance_Log
	
	with log:
		if not isFree:
			if useMoney:
				role.DecMoney(cfg.needMoney)
			else:
				role.DecKuaFuMoney(cfg.needRMB)
		
		blessData[2][roleId][blessGrade-1] = 1
		role.IncDI8(EnumDayInt8.PartyBlessCnt, 1)
		
		PartyBlessDict[serverType][(manId, womenId)] = blessData
		
		if blessGrade == 1:
			global NormalBlessCnt
			if serverType not in NormalBlessCntDict:
				NormalBlessCntDict[serverType] = cnt = 0
			else:
				cnt = NormalBlessCntDict[serverType]
				
			if cnt < 200:
				NormalBlessCntDict[serverType] += 1
				SendBless(manId, roleName, cfg.giftCoding)
				SendBless(womenId, roleName, cfg.giftCoding)
			else:
				SendEmptyBless(manId, roleName, blessName)
				SendEmptyBless(womenId, roleName, blessName)
		else:
			global LuxuryBlessCntDict
			if serverType not in LuxuryBlessCntDict:
				LuxuryBlessCntDict[serverType] = cnt = 0
			else:
				cnt = LuxuryBlessCntDict[serverType]
				
			if cnt < 50:
				LuxuryBlessCntDict[serverType] += 1
				SendBless(manId, roleName, cfg.giftCoding)
				SendBless(womenId, roleName, cfg.giftCoding)
			else:
				SendEmptyBless(manId, roleName, blessName)
				SendEmptyBless(womenId, roleName, blessName)
			
		role.AddItem(cfg.rewardCoding, 1)
		
	role.SendObj(PartyGuestData, PartyBlessDict[serverType])
	
	role.GetScene().Msg(1, 0, GlobalPrompt.PartyBless % (roleName, partyData[8][0], partyData[8][1], blessName))

def LogicBless(role, (blessGrade, manId, womenId)):
	global MarryPartyDict
	if not MarryPartyDict.returnDB: return
	if role.GetSceneID() != EnumGameConfig.PartySceneID: return
		
	if role.GetDI8(EnumDayInt8.PartyBlessCnt) >= EnumGameConfig.PartyBlessMaxCnt:
		return
	
	roleName = role.GetRoleName()
	
	partyData = MarryPartyDict[1].get((manId, womenId))
	
	if not partyData:
		return
	#自己不能给自己祝福
	roleId = role.GetRoleID()
	if roleId in (manId, womenId):
		return
	
	if blessGrade not in (1, 2):
		return
	
	global PartyBlessDict
	blessData = PartyBlessDict.get((manId, womenId))
	if not blessData:
		PartyBlessDict[(manId, womenId)] = blessData = {0:partyData[8], 1:partyData[4], 2:{}}
	
	if roleId not in blessData[2]:
		blessData[2][roleId] = [0, 0]
	
	if blessData[2][roleId][blessGrade-1]:
		#已经祝福过了
		return
	
	cfg = MarryConfig.PartyBless_Dict.get(blessGrade)
	if not cfg:
		return
	
	isFree = False
	if cfg.needMoney:
		useMoney = True
		if role.GetMoney() < cfg.needMoney:
			return
	elif cfg.needRMB:
		useMoney = False
		if role.GetUnbindRMB() < cfg.needRMB:
			return
	else:
		isFree = True
	
	beginSec = partyData[5]
	if not beginSec or cDateTime.Seconds() < beginSec: return
	
	blessName = GlobalPrompt.ReturnBlessGrade(blessGrade)
	if not blessName:
		return
	
	if blessGrade == 1:
		log = PartyBless_Log
	else:
		log = PartyBlessAdvance_Log
	
	with log:
		if not isFree:
			if useMoney:
				role.DecMoney(cfg.needMoney)
			else:
				role.DecUnbindRMB(cfg.needRMB)
		
		blessData[2][roleId][blessGrade-1] = 1
		role.IncDI8(EnumDayInt8.PartyBlessCnt, 1)
		
		PartyBlessDict[(manId, womenId)] = blessData
		
		SendBless(manId, roleName, cfg.giftCoding)
		SendBless(womenId, roleName, cfg.giftCoding)
		role.AddItem(cfg.rewardCoding, 1)
		
	role.SendObj(PartyGuestData, PartyBlessDict)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyBless % (roleName, partyData[8][0], partyData[8][1], blessName))

def RequestJoinKuafuAuction(role, msg):
	'''
	请求进入跨服竞拍
	@param role:
	@param msg:
	'''
	#开服天数
	if not WorldData.WD.returnDB: return
	if WorldData.GetWorldKaiFuDay() < 10: return
	
	#竞拍时间
	global CanInAuction
	if not CanInAuction: return
	
	if not Status.CanInStatus(role, EnumInt1.ST_MarryParty):
		return
	
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	#派对状态
	if not role.GetI1(EnumInt1.PartyIsHost):
		return
	#蜜月
	if role.GetI8(EnumInt8.HoneymoonStatus) != 3:
		return
	
	#去往跨服竞拍, 参数:结婚对象ID, 结婚对象名字
	global ServerTypeToSceneID
	serverType = GetServerType()
	sceneId = ServerTypeToSceneID.get(serverType)
	if not sceneId:
		return
	
	marryData = ReturnMarryData(role)
	if not marryData:
		role.Msg(2, 0, GlobalPrompt.AuctionFindError)
		return
	
	global AuctionPosRandomRange
	posx1, posx2, posy1, posy2 = AuctionPosRandomRange[random.randint(0, 5)]
	role.GotoCrossServer(None, sceneId, random.randint(posx1, posx2), random.randint(posy1, posy2), SyncAuctionData, (marryData, cProcess.ProcessID, ZoneName.ZoneName, serverType))
	
def RequestAuction(role, msg):
	'''
	请求跨服竞拍
	@param role:
	@param msg:
	'''
	#竞拍时间
	global CanInAuction
	if not CanInAuction: return
	
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	#派对状态
	if not role.GetI1(EnumInt1.PartyIsHost):
		return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	price = msg
	
	cfg = MarryConfig.PartyGrade_Dict.get(3)
	if not cfg:
		return
	if price < (cfg.needRMB + 10):
		#最低出价+10
		return
	
	#跨服币不够
	if role.GetKuaFuMoney() < price:
		return
	
	global RoleProDataDict 
	roleProData = RoleProDataDict.get(role.GetRoleID())
	if not roleProData:
		return
	_, zone_name = roleProData
	
	#不是最高出价
	global MaxAuctionPriceDict
	if price < (MaxAuctionPriceDict.get(serverType, 0) + 10):
		#上次出价+10
		return
	MaxAuctionPriceDict[serverType] = price
	
	#扣跨服币
	with KuafuAuction_Log:
		role.DecKuaFuMoney(price)
	
	#进入竞拍记录
	InAuctionRecord(role, price, serverType, zone_name)
	
def RequestJoinKuafuParty(role, msg):
	'''
	请求进入跨服派对
	@param role:
	@param msg:
	'''
	global PartyIsOpen
	if not PartyIsOpen: return
	
	if not WorldData.WD.returnDB: return
	if WorldData.GetWorldKaiFuDay() < 10: return
	
	if not Status.CanInStatus(role, EnumInt1.ST_MarryParty):
		return
	
	global KuafuPartyData
	for idTuple in KuafuPartyData.iterkeys():
		break
	if role.GetRoleID() not in idTuple:
		global CanInKuafuParty
		if not CanInKuafuParty:
			role.Msg(2, 0, GlobalPrompt.PartyKuafuFull) 
			return
	
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	global ServerTypeToSceneID
	serverType = GetServerType()
	sceneId = ServerTypeToSceneID.get(serverType)
	if not sceneId:
		return
	
	global KuafuPosRandomRange
	posx1, posx2, posy1, posy2 = KuafuPosRandomRange[random.randint(0, 4)]
	role.GotoCrossServer(None, sceneId, random.randint(posx1, posx2), random.randint(posy1, posy2), AfterJoinKuafuParty, (cProcess.ProcessID, serverType))
	
def RequestLeaveKuafu(role, msg):
	'''
	请求离开跨服派对
	@param role:
	@param msg:
	'''
	role.GotoLocalServer(None, None)
	
def RequestKuafuFlower(role, msg):
	'''
	请求跨服派对送花
	@param role:
	@param msg:
	'''
	if not Environment.IsCross:
		return
	
	cfg = MarryConfig.PartyHappyCnt_Dict.get(1)
	if not cfg:
		return
	
	if role.GetKuaFuMoney() < cfg.needKuafuMoney:
		return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB: return
	
	partyData = KuafuPartyDict[2].get(serverType)
	if not partyData:
		return
	
	roleId = role.GetRoleID()
	isHost = False
	for hostIdTuple in partyData.iterkeys():
		if roleId in hostIdTuple:
			isHost = True
		break
	
	with KuafuFlower_Log:
		role.DecKuaFuMoney(cfg.needKuafuMoney)
		
		global HappyCntDict, KuafuHappyIsConsumeSet
		if serverType not in HappyCntDict:
			HappyCntDict[serverType] = cfg.happy
		else:
			HappyCntDict[serverType] += cfg.happy
		
		if serverType not in KuafuHappyIsConsumeSet:
			KuafuHappyIsConsumeSet[serverType] = set([roleId,])
			role.SendObj(PartyKuafuHappyConsumeRecord, KuafuHappyIsConsumeSet.get(serverType, set([])))
		elif roleId not in KuafuHappyIsConsumeSet[serverType]:
			KuafuHappyIsConsumeSet[serverType].add(roleId)
			role.SendObj(PartyKuafuHappyConsumeRecord, KuafuHappyIsConsumeSet.get(serverType, set([])))
			
	scene = role.GetScene()
	cNetMessage.PackPyMsg(PartyKuafuHappyCnt, (HappyCntDict[serverType], 1))
	scene.BroadMsg()
	
	if isHost:
		scene.Msg(1, 0, GlobalPrompt.PartyHostFlower % role.GetRoleName())
	else:
		scene.Msg(1, 0, GlobalPrompt.PartyFlower % role.GetRoleName())
	
def RequestKuafuFireworks(role, msg):
	'''
	请求跨服派对燃放烟花
	@param role:
	@param msg:
	'''
	if not Environment.IsCross:
		return
	
	cfg = MarryConfig.PartyHappyCnt_Dict.get(2)
	if not cfg:
		return
	
	if role.GetKuaFuMoney() < cfg.needKuafuMoney:
		return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB: return
	
	partyData = KuafuPartyDict[2].get(serverType)
	if not partyData:
		return
	
	roleId = role.GetRoleID()
	isHost = False
	for hostIdTuple in partyData.iterkeys():
		if roleId in hostIdTuple:
			isHost = True
		break
	
	with KuafuFireworks_Log:
		role.DecKuaFuMoney(cfg.needKuafuMoney)
		
		global HappyCntDict, KuafuHappyIsConsumeSet
		if serverType not in HappyCntDict:
			HappyCntDict[serverType] = cfg.happy
		else:
			HappyCntDict[serverType] += cfg.happy
		
		if serverType not in KuafuHappyIsConsumeSet:
			KuafuHappyIsConsumeSet[serverType] = set([roleId,])
			role.SendObj(PartyKuafuHappyConsumeRecord, KuafuHappyIsConsumeSet.get(serverType, set([])))
		elif roleId not in KuafuHappyIsConsumeSet[serverType]:
			KuafuHappyIsConsumeSet[serverType].add(roleId)
			role.SendObj(PartyKuafuHappyConsumeRecord, KuafuHappyIsConsumeSet.get(serverType, set([])))
	
	scene = role.GetScene()
	cNetMessage.PackPyMsg(PartyKuafuHappyCnt, (HappyCntDict[serverType], 2))
	scene.BroadMsg()
	
	if isHost:
		scene.Msg(1, 0, GlobalPrompt.PartyHostFireworks % role.GetRoleName())
	else:
		scene.Msg(1, 0, GlobalPrompt.PartyFireworks % role.GetRoleName())
	
def RequestKuafuGuestBox(role, msg):
	'''
	请求领取跨服派对嘉宾礼盒
	@param role:
	@param msg:
	'''
	if not Environment.IsCross:
		return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB:
		return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	roleId = role.GetRoleID()
	
	global KuafuHappyIsConsumeSet
	if (serverType not in KuafuHappyIsConsumeSet) or (roleId not in KuafuHappyIsConsumeSet[serverType]):
		return
	
	partyData = KuafuPartyDict[2].get(serverType)
	if not partyData:
		return
	
	for hostIdTuple in partyData.iterkeys():
		if roleId in hostIdTuple:
			return
		break
	
	global HappyCntDict
	happyCnt = HappyCntDict.get(serverType, 0)
	
	if happyCnt < EnumGameConfig.PartyKuafuBoxLimit:
		return
	cfg = MarryConfig.PartyHappyReward_Dict.get(EnumGameConfig.PartyKuafuBoxLimit)
	if not cfg:
		return
	
	
	global HappyCntGuessRewardRecordDict
	if serverType not in HappyCntGuessRewardRecordDict:
		HappyCntGuessRewardRecordDict[serverType] = set([roleId,])
	elif roleId in HappyCntGuessRewardRecordDict[serverType]:
		return
	else:
		HappyCntGuessRewardRecordDict[serverType].add(roleId)
	
	
	with KuafuHappyReward_Log:
		role.AddItem(cfg.jiaBinReward, 1)
	
	role.SendObj(PartyKuafuHappyBoxRecord, HappyCntGuessRewardRecordDict[serverType])
	
	role.Msg(2, 0, GlobalPrompt.PartyHappyReward)
	
def RequestKuafuHostBox(role, msg):
	'''
	请求领取跨服派对新婚礼盒
	@param role:
	@param msg:
	'''
	if not Environment.IsCross:
		return
	
	global KuafuPartyDict
	if not KuafuPartyDict.returnDB:
		return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global ServerTypeDict
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty RequestWorldInvite can not find server type %s in ServerTypeDict' % serverType
		return
	
	roleId = role.GetRoleID()
	
	partyData = KuafuPartyDict[2].get(serverType)
	if not partyData:
		return
	
	for hostIdTuple in partyData.iterkeys():
		if roleId not in hostIdTuple:
			return
		break
	
	global HappyCntDict
	happyCnt = HappyCntDict.get(serverType, 0)
	if happyCnt < EnumGameConfig.PartyKuafuBoxLimit:
		return
	cfg = MarryConfig.PartyHappyReward_Dict.get(EnumGameConfig.PartyKuafuBoxLimit)
	if not cfg:
		return
	
	global HappyCntHostRewardRecordDict
	if serverType not in HappyCntHostRewardRecordDict:
		HappyCntHostRewardRecordDict[serverType] = set([roleId,])
	elif roleId in HappyCntHostRewardRecordDict[serverType]:
		return
	else:
		HappyCntHostRewardRecordDict[serverType].add(roleId)
		
	with KuafuHappyReward_Log:
		role.AddItem(cfg.xinRenReward, 1)
	
	role.SendObj(PartyKuafuHappyBoxRecord, HappyCntHostRewardRecordDict[serverType])
	
	role.Msg(2, 0, GlobalPrompt.PartyHappyReward)
	
#===============================================================================
# 事件
#===============================================================================
def SyncRoleOtherData(role, param):
	#上线同步
	global MarryPartyDict
	if not MarryPartyDict.returnDB:
		return
	
	#同步竞拍记录
	global LogicAuctionRecord
	role.SendObj(PartyKuafuAuctionRecord, LogicAuctionRecord)
	
	#同步所有派对数据
	role.SendObj(PartyAllData, MarryPartyDict.get(1, {}))
	#同步跨服派对数据
	global KuafuPartyData
	role.SendObj(PartyKuafuData, KuafuPartyData)
	
	#同步宾客数据
	global PartyBlessDict
	role.SendObj(PartyGuestData, PartyBlessDict)
	
	marryData = ReturnMarryData(role)
	if not marryData:
		return
	manId, manName, womenId, womenName, _, _ = marryData
	partyData = MarryPartyDict[1].get((manId, womenId))
	roleId = role.GetRoleID()
	if partyData:
		#同步自己的派对数据
		role.SendObj(PartyOwnData, {(manId, womenId):partyData})
		#同步主人数据
		role.SendObj(PartyHostData, (partyData[7].get(roleId, 0), partyData[9].get(roleId, 0), partyData[4], manName, womenName))
	
def AfterSetKaiFuTime(param1, param2):
	#设置开服时间后尝试重算服务器类型
	RecountServerType()

def AfterLoadWorldData(param1, param2):
	#世界数据载回后尝试重算服务器类型
	RecountServerType()

def AfterLoadWorldDataNotSync(param1, param2):
	#私有世界数据载回后尝试重算服务器类型
	RecountServerType()

#===============================================================================
# 持久化数据载回
#===============================================================================
def AfterLoad():
	global MarryPartyDict
	if not MarryPartyDict:
		MarryPartyDict[1] = {}
		MarryPartyDict[2] = {}
		MarryPartyDict.changeFlag = True
	#载回来的时候要把之前预约过和正在开启的Party开起来
	nowSec = cDateTime.Seconds()
	
	for (manId, womenId), partyData in MarryPartyDict[1].items():
		cfg = MarryConfig.PartyGrade_Dict.get(partyData[4])
		if not cfg:
			print 'GE_EXC, MarryParty after load MarryPartyDict can not find party grade %s' % partyData[4]
			continue
		
		manName = partyData[8][0]
		womenName = partyData[8][1]
		grade = partyData[4]
		
		if nowSec >= partyData:
			#如果当前时间超过Party开启的时间了算完成
			EndParty(None, (manId, manName, womenId, womenName, cfg.qinmi, partyData[6], grade))
			continue
		
		#注册开启和关闭tick
		cComplexServer.RegTick(partyData[5] - nowSec, BeginParty, (manId, manName, womenId, womenName, grade))
		cComplexServer.RegTick(partyData[5] + 1200 - nowSec, EndParty, (manId, manName, womenId, womenName, cfg.qinmi, grade))
		cComplexServer.RegTick(partyData[5] + 1140 - nowSec, OneMinuteTips, (manName, womenName))
	
def AfterLoadKuafuParty():
	global KuafuPartyDict
	if KuafuPartyDict:
		return
	
	KuafuPartyDict[1] = {}
	KuafuPartyDict[2] = {}
	KuafuPartyDict.changeFlag = True
	
#===============================================================================
# 回调跨服进程
#===============================================================================
def OnCrossRequestServerType(sessionid, msg):
	#跨服进程请求逻辑进程派对服务器类型, 返回(进程ID, 服务器类型)
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType()))
#===============================================================================
# 跨服进程
#===============================================================================
def AfterNewHour():
	if not Environment.IsCross:
		#非跨服逻辑进程
		if cDateTime.Hour() != 0:
			return
		#0点重新计算服务器类型
		RecountServerType()
		
		#0点清理缓存的跨服派对数据, 同步所有人最新的派对数据
		global KuafuPartyData
		KuafuPartyData = {}
		cNetMessage.PackPyMsg(PartyKuafuData, KuafuPartyData)
		cRoleMgr.BroadMsg()
	else:
		#每个整点的60s后向逻辑进程请求服务器类型数据
		cComplexServer.RegTick(60, RequestLogicServerType, None)
		
		if cDateTime.Hour() == 19:
			Call.ServerCall(0, "Game.Marry.MarryMgr", "RequestDivorceRecord", None)
	
def LogicBackDivorceRecord(param):
	processId, DivorceRecordSet = param
	global ProcessToServerType
	serverType = ProcessToServerType.get(processId)
	if not serverType:
		print 'GE_EXC, MarryParty LogicBackDivorceRecord can not find processId %s' % processId
		return
	global ServerDivorceRecordDict
	if serverType not in ServerDivorceRecordDict:
		ServerDivorceRecordDict[serverType] = set()
	ServerDivorceRecordDict[serverType] |= DivorceRecordSet

def RequestLogicServerType(argv=None, param=None):
	#向所有进程请求服务器类型
	Call.ServerCall(0, "Game.Marry.MarryParty", "LogicSendServerType", None)
	
def LogicSendServerType(param):
	if not WorldDataNotSync.WorldDataPrivate.returnDB: return
	
	Call.ServerCall(Define.GetDefaultCrossID(), "Game.Marry.MarryParty", "LogicBackServerType", (cProcess.ProcessID, GetServerType()))
	
def LogicBackServerType(param):
	global ServerTypeDict, ProcessToServerType
	processId, serverType = param
	
	if serverType not in ServerTypeDict:
		print 'GE_EXC, MarryParty LogicBackServerType get error server type %s' % serverType
		return
	
	if processId  not in ProcessToServerType:
		ProcessToServerType[processId] = serverType
	else:
		st = ProcessToServerType.get(processId)
		ProcessToServerType[processId] = serverType
		if processId in ServerTypeDict[st]:
			ServerTypeDict[st].discard(processId)
		
	ServerTypeDict[serverType].add(processId)
	
def OnRoleClientLost(role, param):
	#跨服派对阶段需要计数场景中的人数
	global CanInKuafuParty
	if not CanInKuafuParty:
		return
	
	global SceneIdToServerType
	serverType = SceneIdToServerType.get(role.GetSceneID())
	if not serverType:
		return
	
	global KuafuPartyDict
	partyData = KuafuPartyDict[2].get(serverType)
	if not partyData:
		return
	
	for idTuple in partyData.iterkeys():
		break
	else:
		return
	
	if role.GetRoleID() in idTuple:
		#主人离去不算
		return
	
	global kuafuPartyRoleCnt_Dict
	if serverType not in kuafuPartyRoleCnt_Dict:
		print 'GE_EXC, MarryParty OnRoleClientLost find serverType %s in serverType' % serverType
		return
	
	if not kuafuPartyRoleCnt_Dict[serverType]:
		return
	
	kuafuPartyRoleCnt_Dict[serverType] -= 1
	
	global ServerTypeIsClose
	if (kuafuPartyRoleCnt_Dict[serverType] == EnumGameConfig.PartyRestartCnt) and ServerTypeIsClose.get(serverType):
		#如果入口是关闭的, 当人数下降到200人时重新开放入口
		serverIdSet = ServerTypeDict.get(serverType)
		if not serverIdSet:
			print 'GE_EXC, MarryParty AfterJoinKuafuParty can not find server id set in server type dict by server type %s' % serverType
			return
		
		ServerTypeIsClose[serverType] = False
		
		for serverId in serverIdSet:
			Call.ServerCall(serverId, "Game.Marry.MarryParty", "SetCanInKuafuParty", True)
	
def BeginAuction():
	#开始竞拍
	global CanInAuction
	CanInAuction = True
	
	if Environment.IsCross:
		cComplexServer.RegTick(600, SyncAuctionRecord, None)
	else:
		if not WorldData.WD.returnDB:
			return
		if WorldData.GetWorldKaiFuDay() < 10:
			#开服天数小于10天的不发传闻
			return
		
		global AuctionIsRumor
		AuctionIsRumor = True
		
		cComplexServer.RegTick(600, AuctionRumor, None)
	
def AuctionRumor(argv, param):
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyAuctionRumor)
	
	cComplexServer.RegTick(1800, AuctionRumorEx, None)
	
def AuctionRumorEx(argv, param):
	global AuctionIsRumor
	if not AuctionIsRumor: return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyAuctionRumor)
	cComplexServer.RegTick(1800, AuctionRumorEx, None)

def SyncAuctionRecord(argv, param):
	#每10分钟向逻辑进程发送最新的竞拍数据
	global CanInAuction
	if not CanInAuction: return
	
	global ServerTypeDict, KuafuPartyDict
	
	for serverType, serverIdSet in ServerTypeDict.iteritems():
		for st, auctionRecord in KuafuPartyDict[1].iteritems():
			if not auctionRecord:
				continue
			if st != serverType:
				continue
			for serverId in serverIdSet:
				Call.ServerCall(serverId, "Game.Marry.MarryParty", "BroadNewAuctionRecord", auctionRecord)
	
	cComplexServer.RegTick(600, SyncAuctionRecord, None)
	
def BroadNewAuctionRecord(auctionRecord):
	if not WorldData.WD.returnDB:
		return
	if WorldData.GetWorldKaiFuDay() < 10:
		#开服天数小于10天的不更新最新的竞拍数据
		return
	
	global LogicAuctionRecord
	LogicAuctionRecord = auctionRecord
	
	cNetMessage.PackPyMsg(PartyKuafuAuctionRecord, auctionRecord)
	cRoleMgr.BroadMsg()
	
def EndAuction():
	#结束竞拍
	global CanInAuction
	CanInAuction = False
	
	if not Environment.IsCross:
		global LogicAuctionRecord, AuctionIsRumor
		LogicAuctionRecord = []
		AuctionIsRumor = False
		return
	
	#########################################跨服逻辑######################################
	
	global ServerTypeToSceneID, KuafuPartyDict, MaxAuctionPriceDict
	#清理最高竞拍价格
	MaxAuctionPriceDict = {}
	
	SSS = cSceneMgr.SearchPublicScene
	for sceneId in ServerTypeToSceneID.itervalues():
		scene = SSS(sceneId)
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
	
	#获取最高竞拍
	if not KuafuPartyDict.returnDB:
		print 'GE_EXC, MarryParty EndAuction not KuafuPartyDict.returnDB'
		return
	global ServerTypeDict, ServerDivorceRecordDict, RoleProDataDict
	for serverType, auctionRecordList in KuafuPartyDict[1].iteritems():
		maxAuction = auctionRecordList[-1]
		roleId = maxAuction[0]
		
		divroceSet = ServerDivorceRecordDict.get(serverType)
		if divroceSet and roleId in divroceSet:
			#该玩家已离婚
			Mail.SendMail(roleId, GlobalPrompt.PartyAuctionFailTitle_2, GlobalPrompt.PartyAuctionSender, GlobalPrompt.PartyAuctionFailContent_2)
			continue
		
		#没有离婚, 查询玩家对象信息
		roleProData = RoleProDataDict.get(roleId)
		if not roleProData:
			print 'GE_EXC, MarryParty EndAuction can not find role process data by role %s' % roleId
			continue
		marryData, zoneNAME = roleProData
		
		manId, manName, womenId, womenName, _, _ = marryData
		
		cfg = MarryConfig.PartyGrade_Dict.get(3)
		if not cfg:
			print 'GE_EXC, MarryParty can not find party grade 3 cfg'
			return
		
		if serverType not in KuafuPartyDict[2]:
			KuafuPartyDict[2][serverType] = {(manId, womenId):{2:0, 3:0, 4:3, 5:cDateTime.Seconds()+600, 6:0, 7:{manId:cfg.freeCandy, womenId:cfg.freeCandy}, 8:[manName, womenName], 9:{manId:cfg.candyCnt, womenId:cfg.candyCnt}, 10:zoneNAME}}
		
		with KuafuAuction_Log:
			#记录服务器最高竞拍价格
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKuafuPartyAuctionMax, (serverType, maxAuction[-1], manId, womenId))
		
		#广播逻辑进程跨服派对数据
		for serverId in ServerTypeDict[serverType]:
			Call.ServerCall(serverId, "Game.Marry.MarryParty", "AddPartyData", ((manId, womenId), (manName, womenName), {2:0, 3:0, 4:3, 5:cDateTime.Seconds()+600, 6:0, 7:{manId:cfg.freeCandy, womenId:cfg.freeCandy}, 8:[manName, womenName], 9:{manId:cfg.candyCnt, womenId:cfg.candyCnt}, 10:zoneNAME}))
		
	with KuafuAuction_Log:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKuafuPartyAuctionRecord, KuafuPartyDict[1].copy())
		
	#清理竞拍数据
	KuafuPartyDict[1] = {}
	KuafuPartyDict.changeFlag = True
	
	ServerDivorceRecordDict = {}
	RoleProDataDict = {}
	
def AddPartyData(param):
	if not WorldData.WD.returnDB:
		return
	if WorldData.GetWorldKaiFuDay() < 10:
		#开服天数小于10天的不同步跨服派对数据
		return
	
	global KuafuPartyData
	if KuafuPartyData:
		print 'GE_EXC, MarryParty AddPartyData error'
		return
	
	#清理竞拍数据
	global LogicAuctionRecord
	LogicAuctionRecord = []
	
	(manId, womenId), (manName, womenName), partyData = param
	
	KuafuPartyData[(manId, womenId)] = partyData
	
	#广播所有人
	cNetMessage.PackPyMsg(PartyKuafuData, KuafuPartyData)
	cRoleMgr.BroadMsg()
	
	#不是本服角色
	if KuaFu.IsLocalRoleByRoleID(manId):
		with KuafuAuction_Log:
			#同步角色派对数据
			Mail.SendMail(manId, GlobalPrompt.PartyAuctionSuccessTitle, GlobalPrompt.PartyAuctionSender, GlobalPrompt.PartyAuctionSuccessContent)
			
			Mail.SendMail(womenId, GlobalPrompt.PartyAuctionSuccessTitle, GlobalPrompt.PartyAuctionSender, GlobalPrompt.PartyAuctionSuccessContent)
		
	cComplexServer.RegTick(60, AuctionSuccessRumor, (manName, womenName))
	
def AuctionSuccessRumor(argv, param):
	cRoleMgr.Msg(1, 0, GlobalPrompt.PartyAuctionSuccess % param)
	
def BeginKuafuParty():
	#设置可以进入标志
	global CanInKuafuParty, KuafuPartyDict
	CanInKuafuParty = True
	
	if not Environment.IsCross:
		global PartyIsOpen
		PartyIsOpen = True
		return
	
	#########################################跨服逻辑######################################
	
	if not KuafuPartyDict.returnDB: return
	
	#跨服派对开始
	global ServerTypeDict
	for serverType, partyData in KuafuPartyDict[2].iteritems():
		for idTuple, pData in partyData.iteritems():
			break
		serverIdSet = ServerTypeDict.get(serverType)
		if not serverIdSet:
			print 'GE_EXC, MarryParty BeginKuafuParty can not find server type %s id set' % serverType
			continue
		manId, womenId, manName, womenName, partyGrade = idTuple[0], idTuple[1], pData[8][0], pData[8][1], 3
		for serverId in serverIdSet:
			Call.ServerCall(serverId, "Game.Marry.MarryParty", "BeginPartyEx", (manId, manName, womenId, womenName, partyGrade))
	
def EndKuafuParty():
	global CanInKuafuParty
	CanInKuafuParty = False
	
	if not Environment.IsCross:
		global PartyIsOpen
		PartyIsOpen = False
		return
	
	#########################################跨服逻辑######################################
	
	#清理祝福数据
	global PartyBlessDict, NormalBlessCntDict, LuxuryBlessCntDict, kuafuPartyRoleCnt_Dict, ServerTypeDict
	#祝福
	PartyBlessDict = {}
	#跨服普通祝福
	NormalBlessCntDict = {}
	#跨服豪华祝福
	LuxuryBlessCntDict = {}
	#派对人数
	kuafuPartyRoleCnt_Dict = {}
	#派对入口
	ServerTypeIsClose = {}
	
	#清理跨服派对数据
	global KuafuPartyDict, HappyCntHostRewardRecordDict, HappyCntDict, KuafuHappyIsConsumeSet, HappyCntGuessRewardRecordDict
	for serverType, partyData in KuafuPartyDict[2].iteritems():
		for idTuple, pData in partyData.iteritems():
			break
		serverIdSet = ServerTypeDict.get(serverType)
		if not serverIdSet:
			print 'GE_EXC, MarryParty EndKuafuParty can not find server type %s in ServerTypeDict' % serverType
			continue
		manId, womenId, manName, womenName, partyGrade = idTuple[0], idTuple[1], pData[8][0], pData[8][1], 3
		for serverId in serverIdSet:
			Call.ServerCall(serverId, "Game.Marry.MarryParty", "EndPartyEx", (manId, manName, womenId, womenName, partyGrade))
		
		happyCnt = HappyCntDict.get(serverType, 0)
		if happyCnt >= 10000:
			cfg = MarryConfig.PartyHappyReward_Dict.get(EnumGameConfig.PartyKuafuBoxLimit)
			if not cfg:
				print "GE_EXC, MarryParty EndKuafuParty can not find xinRenReward cfg"
				continue
			rewardSet = HappyCntHostRewardRecordDict.get(serverType, set())
			for tRoleId in (manId, womenId):
				if tRoleId in rewardSet:
					continue
				with KuafuHappyReward_Log:
					Mail.SendMail(tRoleId, GlobalPrompt.PartyHappyTitle, GlobalPrompt.PartyHappySender, GlobalPrompt.PartyHappyContent, items = [(cfg.xinRenReward, 1)])
	KuafuHappyIsConsumeSet = {}
	HappyCntDict = {}
	HappyCntGuessRewardRecordDict = {}
	HappyCntHostRewardRecordDict = {}
	KuafuPartyDict[2] = {}
	KuafuPartyDict.changeFlag = True
	
	#清理服务器类型对应的服务器
	ServerTypeDict = {1:set(), 2:set(), 3:set(), 4:set(), 5:set()}
	ProcessToServerType = {}
	
	#清退场景内所有玩家
	global ServerTypeToSceneID
	SSS = cSceneMgr.SearchPublicScene
	for sceneId in ServerTypeToSceneID.itervalues():
		scene = SSS(sceneId)
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
	
if "_HasLoad" not in dir():
	#############################################################################
	#逻辑进程  普通逻辑进程或者是特定的跨服进程
	#############################################################################
	if Environment.HasLogic and (not Environment.IsCross or cProcess.ProcessID == Define.GetDefaultCrossID()):
		#是否可以进入跨服竞拍标志
		CanInAuction = False
		#是否可以进入跨服派对标志
		CanInKuafuParty = False
		#Party祝福字典{(男方ID, 女方ID):{0:[男方名字, 女方名字], 1:派对档次, 2:{role_id:[普通祝福, 高级祝福]}}}
		PartyBlessDict = {}
		#{服务器类型:场景ID}
		ServerTypeToSceneID = {1:500, 2:501, 3:502, 4:503, 5:504}
		#每小时调用重新计算服务器跨服派对类型
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		if not Environment.EnvIsNAXP() and not Environment.IsNAPLUS1 and not Environment.EnvIsESP():
			#西班牙不开
			if Environment.EnvIsFT() or Environment.EnvIsQQ() or Environment.EnvIsNA() or Environment.IsDevelop:
				Cron.CronDriveByMinute((2038, 1, 1), BeginAuction, H = "H == 13", M = "M == 0")
				Cron.CronDriveByMinute((2038, 1, 1), EndAuction, H = "H == 19", M = "M == 20")
				Cron.CronDriveByMinute((2038, 1, 1), BeginKuafuParty, H = "H == 19", M = "M == 30")
				Cron.CronDriveByMinute((2038, 1, 1), EndKuafuParty, H = "H == 19", M = "M == 50")
			
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_WorldInvite", "请求世界邀请"), RequestWorldInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_Invite", "请求邀请伴侣"), RequestInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_Candy", "请求发放喜糖"), RequestCandy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_Bless", "请求祝福"), RequestBless)
	
	#############################################################################
	#逻辑进程(非跨服)
	#############################################################################
	if (Environment.HasLogic and not Environment.IsCross) or Environment.HasWeb:
		#举办跨服派对次数字典	{role_id:cnt}
		KuafuPartyCntDict = Contain.Dict("KuafuPartyCntDict", (2038, 1, 1))
		#2暂时没用了
		#{1:{(manId, womenId):{2:高级Party,3:豪华Party,4:今日Party,5:开始时间,6:PartyID,7:{roleid:免费喜糖次数},8:[男方名字, 女方名字],9:{roleid:剩余发放喜糖次数}}}, 2 : {反向字典--合服的时候key冲突处理用}}
		#注:普通派对的数据在结束后会删除, 跨服派对的数据将在0点清理
		MarryPartyDict = Contain.Dict("MarryPartyDict", (2038, 1, 1), AfterLoad)
		
	if (Environment.HasLogic and not Environment.IsCross):
		#是否竞拍传闻
		AuctionIsRumor = False
		#跨服派对是否开启
		PartyIsOpen = False
		#本地缓存竞拍记录
		LogicAuctionRecord = []
		#本地Party传送位置
		PartyRevivePos = (5552, 3878)
		#本地缓存跨服派对数据
		KuafuPartyData = {}
		#进入跨服竞拍随机坐标范围(posx1, posx2, posy1, posy2)
		AuctionPosRandomRange = (
								(2241,3079, 2241,2599),
								(2198,2799, 1879,2200),
								(3480,4081, 1636,1879),
								(3882,4799, 1761,1880),
								(4791,5558, 1202,1561),
								(3920,4761, 922,1199)
								)
		#进入跨服派对随机坐标范围(posx1, posx2, posy1, posy2)
		KuafuPosRandomRange = (
							(5322,5835, 3720,3960),
							(5684,6279, 3563,3798),
							(5920,6320, 3402,3636),
							(4791,5558, 1202,1561),
							(3920,4761, 922,1199)
							)
		#起服重算服务器派对类型
		Init.InitCallBack.RegCallbackFunction(RecountServerType)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, AfterLoadWorldDataNotSync)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_ImHost", "请求立即举办派对"), RequestHost)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_ReHost", "请求预约派对"), RequestReservation)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_Join", "请求进入派对"), RequestJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_JoinKuafuAuction", "请求进入跨服竞拍"), RequestJoinKuafuAuction)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_JoinKuafuParty", "请求进入跨服派对"), RequestJoinKuafuParty)
	
	#############################################################################
	#跨服逻辑进程
	#############################################################################
	if (Environment.HasLogic and Environment.IsCross and cProcess.ProcessID == Define.GetDefaultCrossID()) or Environment.HasWeb:
		#{1:{服务器类型:跨服竞拍记录[role_id, role_name, zone_name, price]}, 2:{服务器类型:跨服派对数据{(manId, womenId):{2:高级Party,3:豪华Party,4:今日Party,5:开始时间,6:PartyID,7:{roleid:免费喜糖次数},8:[男方名字, 女方名字],9:{roleid:剩余发放喜糖次数},10:服务器名字}}}}
		#注:1:竞拍数据在竞拍结束后清理, 2:派对数据在派对结束后清理
		KuafuPartyDict = Contain.Dict("KuafuPartyDict", (2038, 1, 1), AfterLoadKuafuParty)
		
	if (Environment.HasLogic and Environment.IsCross and cProcess.ProcessID == Define.GetDefaultCrossID()):
		#普通祝福次数
		NormalBlessCntDict = {}
		#豪华祝福次数
		LuxuryBlessCntDict = {}
		#最高竞拍价格{服务器类型:最高出价}
		MaxAuctionPriceDict = {}
		#{服务器类型:人数}
		kuafuPartyRoleCnt_Dict = {}
		#{服务器类型:set(服务器ID)}
		ServerTypeDict = {1:set(), 2:set(), 3:set(), 4:set(), 5:set()}
		#{服务器ID --> 服务器类型}
		ProcessToServerType = {}
		#{服务器类型 --> 离婚记录集合}
		ServerDivorceRecordDict = {}
		#{场景ID:服务器类型}
		SceneIdToServerType = {500:1, 501:2, 502:3, 503:4, 504:5}
		#{服务器类型:入口是否关闭}
		ServerTypeIsClose = {}
		
		#{role_id : (marryData, zoneName)}
		#注:在竞拍结束后清理
		RoleProDataDict = {}
		#喜庆度
		HappyCntDict = {}
		#喜庆度宾客礼盒领取记录
		HappyCntGuessRewardRecordDict = {}
		#喜庆度新人礼盒领取记录
		HappyCntHostRewardRecordDict = {}
		#是否消费
		KuafuHappyIsConsumeSet = {}
		
		#起服时向非跨服逻辑进程请求派对服务器类型
		Init.InitCallBack.RegCallbackFunction(RequestServerType)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleClientLost)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_Auction", "请求跨服竞拍"), RequestAuction)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_LeaveKuafu", "请求离开跨服派对"), RequestLeaveKuafu)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_KuafuFlower", "请求跨服派对送花"), RequestKuafuFlower)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_KuafuFireworks", "请求跨服派对燃放烟花"), RequestKuafuFireworks)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_KuafuGuestBox", "请求领取跨服派对嘉宾礼盒"), RequestKuafuGuestBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Party_KuafuHostBox", "请求领取跨服派对新婚礼盒"), RequestKuafuHostBox)
		
		
