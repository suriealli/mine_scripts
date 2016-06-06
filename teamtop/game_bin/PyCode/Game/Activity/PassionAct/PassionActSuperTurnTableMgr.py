#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActSuperTurnTableMgr")
#===============================================================================
# 超级转盘管理器
#===============================================================================
import Environment
import cRoleMgr
import cProcess
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig,GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Call, Event
from Game.Role.Data import EnumObj
from Game.GlobalData import ZoneName
from Game.Activity import CircularDefine
from Game.SysData import WorldData
from Game.Activity.PassionAct.PassionDefine import PassionSuperTurnTable
from Game.Activity.PassionAct.PassionActSuperTurnTableConfig import GetRandomObj,GetLuckyRandomObj,SuperTurnTableBonus_Dict


if "_HasLoad" not in dir():

	IsOpen = False

	CrossServerRecord = []		#跨服记录[(区名,角色名,物品coding)]
	LocalServerRecord = []		#本服记录[(角色名,物品coding)]

	OpenPaneRoles = set()		#
	LotteryConsumeDict = {1:EnumGameConfig.SuperTurnTableOnce,10:EnumGameConfig.SuperTurnTableTen}	#{次数:消耗神石}
	#日志
	PassionSTTLottery = AutoLog.AutoTransaction("PassionSTTLottery", "超值转盘抽奖")
	PassionSTTReward = AutoLog.AutoTransaction("PassionSTTReward", "超值转盘领取奖励")
	#消息
	PassionSTTRoleData 			= AutoMessage.AllotMessage("PassionSTTRoleData", "超值转盘玩家数据")		#cnt
	PassionSTTRecord 			= AutoMessage.AllotMessage("PassionSTTRecord", "超级转盘服务器记录")		#{1:跨服[(区名,角色名,物品coding)],2:本服[(角色名,物品coding)]}
	PassionSTTAward 			= AutoMessage.AllotMessage("PassionSTTAward", "超值转盘奖励数据")			#set(奖励ID)
	PassionSTTLotterCallBack	= AutoMessage.AllotMessage("PassionSTTLotterCallBack", "超值转盘结果回调")	#

def StartActivity(param1, param2):
	if param2 != CircularDefine.CA_PassionSuperTurnTable:
		return
	
	global IsOpen
	if IsOpen:
		print "GE_EXC, PassionSuperTurnTable is already open"
		return
	
	IsOpen = True

def EndActivity(param1, param2):
	if param2 != CircularDefine.CA_PassionSuperTurnTable:
		return
	
	global IsOpen
	if not IsOpen:
		print "GE_EXC, PassionSuperTurnTable is already close"
		return
	
	IsOpen = False

def SysncRoleData(role):
	global IsOpen
	if not IsOpen: return

	lottery_times = role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable][1]
	role.SendObj(PassionSTTRoleData,lottery_times)

def SyncRoleAward(role):
	global IsOpen
	if not IsOpen: return

	rewardIds = role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable][2]
	role.SendObj(PassionSTTAward,rewardIds)

def SyncServerData():
	'''
	面板内广播服务器记录
	'''
	global IsOpen
	if not IsOpen: return

	for roleId in OpenPaneRoles:
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if role:
			SyncServerDataToRole(role)

def SyncServerDataToRole(role):
	'''
	同步服务器记录到角色
	'''
	global IsOpen
	if not IsOpen: return

	if not role: return

	global CrossServerRecord
	global LocalServerRecord

	role.SendObj(PassionSTTRecord, {1:CrossServerRecord,2:LocalServerRecord})

def OpenPane(role,msg):
	'''
	请求打开面板
	'''
	global IsOpen
	if not IsOpen: return

	SysncRoleData(role)
	SyncServerDataToRole(role)
	SyncRoleAward(role)

	global OpenPaneRoles
	OpenPaneRoles.add(role.GetRoleID())

def ClosePane(role,msg):
	'''
	请求关闭面板
	'''
	global OpenPaneRoles
	OpenPaneRoles.discard(role.GetRoleID())

def IncLotteryTimes(role,times):
	'''
	增加一次抽奖次数
	'''
	if not role or times < 0:
		return

	role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable][1] += times

	Lottery_cnt = WorldData.GetSTTLotteryCnt()

	WorldData.SetSTTLotteryCnt(Lottery_cnt+times)

	#同步角色数据
	SysncRoleData(role)

def LotteryTimesFunc(role,times):
	def times_func(sub_func):
		item_list = []
		counter = 1
		while counter < times+1:
			item_list.extend(sub_func(role,counter))
			counter+=1
		return item_list

	return times_func

def LuckyLottery(role):
	'''
	超级抽奖，每抽奖满100次触发
	'''
	random_obj = GetLuckyRandomObj(role.GetLevel())
	if not random_obj:
		return

	return random_obj.RandomOne()

def Lottery(role,times):
	'''
	抽奖
	'''
	#今日已抽奖次数
	daytimes = role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable][1]
	nowtimes = daytimes + times

	item_list = []	#[(cfg,islucy)]
	#触发超级抽奖
	if nowtimes and not (nowtimes % 100):
		lucky_item = LuckyLottery(role)
		if lucky_item:
			item_list.append((lucky_item,1))
	else:
		random_obj = GetRandomObj(role.GetLevel())
		if not random_obj:
			return

		cfg = random_obj.RandomOne()
		if not cfg:
			return

		item_list.append((cfg,0))

	return item_list

def LotteryAward(role,is_jump,consume_param,item_list):
	'''
	发奖
	'''
	item_list = ExtractPyType(item_list)

	#跳过播放特效
	if is_jump:
		LotteryAwardD(role,None,(consume_param,item_list))
	else:
		if len(item_list) > 1:
			print "GE_EXG, when it is not jump,len(item_list)(%s) must be 1 in STT Lottery" % len(item_list)

		cfg_dict = item_list[0][0]
		role.SendObjAndBack(PassionSTTLotterCallBack,cfg_dict[1],15,LotteryAwardD,(consume_param,item_list))

def ExtractPyType(param):
	'''
	obj 转换到 python标准类型
	{1:id,2:(coding,cnt),3:isLocal,4:isCross}
	'''
	if not param:
		return

	pyitem_list = []

	itemobj_list = param
	for cfg,islucky in itemobj_list:
		pyitem = {1:cfg.id,2:cfg.item,3:cfg.isLocal,4:cfg.isCross}
		pyitem_list.append((pyitem,islucky))

	return pyitem_list


def LotteryAwardD(role, callargv, regparam):
	'''
	尝试发奖
	'''
	_,item_list = regparam
	if not len(item_list):
		return

	Call.LocalDBCall(role.GetRoleID(), LotteryAwardDCallBack, regparam)

def LotteryAwardDCallBack(role, param):
	'''
	发奖回调
	'''
	(needRMB,needTimes),item_list = param
	if not len(item_list):
		return

	tips = GlobalPrompt.STT_Random_Reward_Tips

	zone_name = ZoneName.GetZoneName(cProcess.ProcessID)
	with PassionSTTLottery:
		role.DecUnbindRMB_Q(needRMB)
		for cfg_dict,_ in item_list:
			role.AddItem(*cfg_dict[2])
			tips += GlobalPrompt.Item_Tips % cfg_dict[2]
			#本服记录
			if cfg_dict[3]:
				UpdateLocalServer((role.GetRoleName(),cfg_dict[2][0],cfg_dict[2][1]))
			#全服记录
			if cfg_dict[4]:
				Call.ServerCall(0,"Game.Activity.PassionAct.PassionActSuperTurnTableMgr","UpdateCrossServer",(zone_name,role.GetRoleName(),cfg_dict[2][0],cfg_dict[2][1]))

		IncLotteryTimes(role,needTimes)

	role.Msg(2, 0, tips)

def UpdateLocalServer(param):
	'''
	更新本服记录
	'''
	global LocalServerRecord
	if len(LocalServerRecord) > 100:
		LocalServerRecord.pop(0)

	LocalServerRecord.append(param)

	SyncServerData()

def UpdateCrossServer(param):
	'''
	更新服务器记录
	'''
	global CrossServerRecord
	if len(CrossServerRecord) > 100:
		CrossServerRecord.pop(0)

	CrossServerRecord.append(param)

	SyncServerData()


def LotteryMethod(role,consume_param,is_jump):
	'''
	N次抽奖
	'''
	_,needTimes = consume_param

	times_func = LotteryTimesFunc(role,needTimes)
	if not times_func:
		return

	#N次抽奖
	item_list = times_func(Lottery)
	if not item_list: return
	elif not len(item_list): return

	if not is_jump:
		is_jump = ( needTimes > 1 )	#大于一次跳过播放动画
	
	#发奖
	LotteryAward(role,is_jump,consume_param,item_list)

def OnLottery(role,msg):
	'''
	客户端请求抽奖
	'''
	global IsOpen
	if not IsOpen: return

	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel:
		return

	#世界数据没有载回
	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionActSuperTurnTableMgr OnLottery"
		return

	if not msg: return
	cnt,is_jump = msg

	global LotteryConsumeDict
	needRMB = LotteryConsumeDict.get(cnt,0)

	if not needRMB:
		return

	#充值神石检测
	if role.GetUnbindRMB_Q() < needRMB:
		return

	#抽奖
	LotteryMethod(role,(needRMB,cnt),is_jump)


def OnAward(role,msg):
	'''
	客户端请求领奖
	'''
	global IsOpen
	if not IsOpen: return

	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel:
		return

	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionActSuperTurnTableMgr OnAward"
		return

	if not msg: return
	reward_id = msg

	reward_cfg = SuperTurnTableBonus_Dict.get(reward_id,None)
	if not reward_cfg:
		return

	#没有达到抽奖次数
	if WorldData.GetSTTLotteryCnt() < reward_cfg.needTimes:
		return

	#已领取过该奖励
	rewardIds = role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable][2]
	if reward_id in rewardIds:
		return

	tips = GlobalPrompt.Reward_Tips
	with PassionSTTReward:
		for item in reward_cfg.itemReward:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		rewardIds.add(reward_id)

	role.Msg(2, 0, tips)

	SyncRoleAward(role)

def OnRoleInit(role,param):
	'''
	角色初始化
	'''
	if PassionSuperTurnTable not in role.GetObj(EnumObj.PassionActData):
		role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable] = {1:0,2:set()}

def RoleDayClear(role, param):
	global IsOpen
	if not IsOpen: return

	role.GetObj(EnumObj.PassionActData)[PassionSuperTurnTable] = {1:0,2:set()}
	
	SysncRoleData(role)
	SyncRoleAward(role)

def everyNewDay():
	global IsOpen
	if not IsOpen: return
	
	#本服总抽奖次数清0
	WorldData.SetSTTLotteryCnt(0)

def OnRoleLost(role,param):
	global IsOpen
	if not IsOpen: return

	global OpenPaneRoles
	roleId = role.GetRoleID()
	
	OpenPaneRoles.discard(roleId)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, StartActivity)
		Event.RegEvent(Event.Eve_EndCircularActive, EndActivity)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleLost)
		
		cComplexServer.RegAfterNewDayCallFunction(everyNewDay)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActSTT_RequestOpenPane", "请求打开超级转盘面板"), OpenPane)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActSTT_RequestClosePane", "请求关闭面板"), ClosePane)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActSTT_RequestLottery", "请求超级转盘抽奖") , OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActSTT_Requestaward", "请求超值转盘领取福利"), OnAward)