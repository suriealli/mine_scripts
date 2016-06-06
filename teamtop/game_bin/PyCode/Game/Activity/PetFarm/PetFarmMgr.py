#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PetFarm.PetFarmMgr")
#===============================================================================
# 宠物灵树（宠物灵树）管理器
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Persistence import Contain
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.PetFarm import PetFarmConfig


if "_HasLoad" not in dir():
	
	__ISPETFARMSTART = False				#宠物灵树活动开始标志
	PETFRUIT_CODE = 26144					#宠物圣果code
	
	#消息
	PETFARM_SHOWROLEDATA = AutoMessage.AllotMessage("PETFARM_SHOWROLEDATA", "显示玩家获奖数据")
	PETFARM_SHOWROLECD = AutoMessage.AllotMessage("PETFARM_SHOWROLECD", "玩家CD时间")#状态0：未种植1：种植 2：可收获

	#日志
	Tra_PetFarm_Machine = AutoLog.AutoTransaction("Tra_PetFarm_Machine", "宠物灵树请求种植")
	Tra_PetFarm_Harvest = AutoLog.AutoTransaction("Tra_PetFarm_Harvest", "宠物灵树请求普通收获")
	Tra_PetFarm_OnekeyHarvest = AutoLog.AutoTransaction("Tra_PetFarm_OnekeyHarvest", "宠物灵树请求一键收获")
	Tra_PetFarm_QuickerMachine = AutoLog.AutoTransaction("Tra_PetFarm_QuickerMachine", "宠物灵树请求浇水")

#============================================================================
def PetFarmStart(*param):
	'''
	宠物灵树活动开启
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_PetFoot:
		return
	global __ISPETFARMSTART
	if __ISPETFARMSTART:
		print "GE_EXC, PetFarm is already started "
		return
	__ISPETFARMSTART = True


def PetFarmEnd(*param):
	'''
	宠物灵树活动关闭
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_PetFoot:
		return
	global __ISPETFARMSTART
	global PETFARMROLECD_DICT
	if not __ISPETFARMSTART:
		print "GE_EXC, PetFarm is already ended "
		return
	__ISPETFARMSTART = False
	#所有玩家退出种植状态
	
	PETFARMROLECD_DICT.clear()
#============================================================================
def RequestMachine(role, msg):
	'''
	请求开始种植
	@param role:
	@param msg:
	'''
	#如果宠物灵树活动没有开启
	if not __ISPETFARMSTART:
		return
	#玩家等级限制
	if role.GetLevel() < EnumGameConfig.PETFARM_NEEDLEVEL:
		return
	#玩家进入种植状态
	roleID = role.GetRoleID()
	#如果玩家已经处于种植状态
	global PETFARMROLECD_DICT
	if roleID in PETFARMROLECD_DICT:
		return
	#设置CD时间
	cdtime = PETFARMROLECD_DICT[roleID] = cDateTime.Seconds() + EnumGameConfig.PETFARM_CDTIME
	role.SendObj(PETFARM_SHOWROLECD, (1, cdtime))
	
	#日志事件
	with Tra_PetFarm_Machine:
		AutoLog.LogBase(roleID, AutoLog.evePetFarmMachine, None)


def RequestHarvest(role, msg):
	'''
	请求普通收获
	@param role:
	@param msg:
	'''
	#如果宠物灵树活动没有开启
	if not __ISPETFARMSTART:
		return
	#如果玩家并没有在种植状态
	global PETFARMROLECD_DICT
	if not role.GetRoleID() in PETFARMROLECD_DICT:
		return
	#如果还没有CD，则返回
	roleID = role.GetRoleID()
	if cDateTime.Seconds() < PETFARMROLECD_DICT.get(roleID):
		return
	awardtype, awardlist = __RandomAward(role)
	if not awardlist or not awardtype or not isinstance(awardlist, list):
		print "GE_EXC, roleID(%s) can not get __RandomAward in PetFarm ,check PetFarmConfig ?" % roleID
		return
	#如果背包空间不足
	if role.PackageEmptySize() < len(awardlist):
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	with Tra_PetFarm_Harvest:
		#玩家退出种植状态	
		del PETFARMROLECD_DICT[roleID]
		#发放奖励
		role_AddItem = role.AddItem
		for items in awardlist:
			role_AddItem(*items)
			if items[0]== PETFRUIT_CODE and items[1] >= 50:
				cRoleMgr.Msg(1, 0, GlobalPrompt.PetFarm_LuckRole % (role.GetRoleName(), items[0], items[1]))

	#玩家奖励数据
	global PETFARMROLEAWARD_DICT
	PetFarmData = PETFARMROLEAWARD_DICT.get(roleID, [])
	PetFarmData.append((cDateTime.Now(), awardtype))
	#如果玩家数据过长，则截取片段
	if len(PetFarmData) > EnumGameConfig.PETFARM_ROLEDATA_LENTH:
		PetFarmData = PetFarmData[-EnumGameConfig.PETFARM_ROLEDATA_LENTH:]
	#保存新数据
	PETFARMROLEAWARD_DICT[roleID] = PetFarmData
	#客户端显示数据
	role.SendObj(PETFARM_SHOWROLEDATA, PetFarmData)
	role.SendObj(PETFARM_SHOWROLECD, (0, None))



def OnekeyHarvest(role, msg):
	'''
	请求一键收获
	@param role:
	@param msg:
	'''
	#如果宠物灵树活动没有开启
	if not __ISPETFARMSTART:
		return
	#如果玩家并没有在种植状态
	global PETFARMROLECD_DICT
	if not role.GetRoleID() in PETFARMROLECD_DICT:
		return
	#如果VIP等级不符合要求则返回
	#when the VIP level is not right
	if role.GetVIP() < EnumGameConfig.PETFARM_ONEKEYHARVESTVIPLEVEL:
		return

	#计算剩余CD时间，不足一小时的按照一小时计算
	#calculate the remaining hours to cold down
	roleID = role.GetRoleID()
	hours_remainning = (PETFARMROLECD_DICT[roleID] - cDateTime.Seconds()) / 3600
	#如果已完成CD
	if hours_remainning <= 0:
		return
	
	perHourCDNeedRMB = EnumGameConfig.PETFARM_PER_HOUR_CD_NEED_RMB
	#版本判断
	if Environment.EnvIsNA():
		perHourCDNeedRMB = EnumGameConfig.PETFARM_PER_HOUR_CD_NEED_RMB_NA
	elif Environment.EnvIsRU():
		perHourCDNeedRMB = EnumGameConfig.PETFARM_PER_HOUR_CD_NEED_RMB_RU
	
	#不足一小时的按一小时计算
	if hours_remainning % 3600:
		hours_remainning += 1
	OnekeyHarvest_price = hours_remainning * perHourCDNeedRMB
	#如果玩家神石不足则返回
	#if there is not enough RMB
	if role.GetUnbindRMB() < OnekeyHarvest_price:
		return
	
	#如果背包空间不足
	awardtype, awardlist= __RandomAward(role)
	if not awardlist or not awardtype or not isinstance(awardlist, list):
		print "GE_EXC, roleID(%s) can not get __RandomAward in PetFarm ,check PetFarmConfig ?" % roleID
		return
	if role.PackageEmptySize() < len(awardlist):
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	#这里添加系统日志
	#add sys log here
	with Tra_PetFarm_OnekeyHarvest:
		#玩家退出种植状态	
		del PETFARMROLECD_DICT[roleID]
		#扣除玩家神石
		role.DecUnbindRMB(OnekeyHarvest_price)
		#发放奖励
		role_AddItem = role.AddItem
		for items in awardlist:
			role_AddItem(*items)
			if items[1] >= 50:
				cRoleMgr.Msg(1, 0, GlobalPrompt.PetFarm_LuckRole % (role.GetRoleName(), items[0], items[1]))
	#保存玩家奖励数据
	global PETFARMROLEAWARD_DICT
	PetFarmData = PETFARMROLEAWARD_DICT.get(roleID, [])
	PetFarmData.append((cDateTime.Now(), awardtype))
	#如果玩家数据过长，则截取片段
	if len(PetFarmData) > EnumGameConfig.PETFARM_ROLEDATA_LENTH:
		PetFarmData = PetFarmData[-EnumGameConfig.PETFARM_ROLEDATA_LENTH:]
	PETFARMROLEAWARD_DICT[roleID] = PetFarmData
	
	#客户端显示奖励数据
	role.SendObj(PETFARM_SHOWROLEDATA, PetFarmData)
	role.SendObj(PETFARM_SHOWROLECD, (0, None))


def QuickerGrow(role, msg):
	'''
	请求浇水
	@param role:
	@param msg:
	'''

	#如果宠物灵树活动没有开启
	if not __ISPETFARMSTART:
		return
	#如果玩家并没有在种植状态
	global PETFARMROLECD_DICT
	if not role.GetRoleID() in PETFARMROLECD_DICT:
		return
	#玩家贵族等级不符合条件
	if not role.GetVIP() < EnumGameConfig.PETFARM_ONEKEYHARVESTVIPLEVEL:
		return
	
	needRMB = EnumGameConfig.PETFARM_QUICKERMACHINE_PRICE
	#版本判断
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.PETFARM_QUICK_COST_NA
	
	#玩家神石不足
	if role.GetUnbindRMB() < needRMB:
		return
	roleID = role.GetRoleID()
	#扣除6神石，CD时间减去2小时
	#日志
	#如果CD时间已经到了
	nowtime = cDateTime.Seconds()
	cdtime = PETFARMROLECD_DICT[roleID]
	if nowtime < cdtime:
		with Tra_PetFarm_QuickerMachine:
			role.DecUnbindRMB(needRMB)
		#重新设置CD
		if cdtime-nowtime < 7200:
			cdtime = nowtime
		else:
			cdtime -= 7200
		PETFARMROLECD_DICT[roleID] = cdtime
		#玩家已处于种植状态
		isplanting = 1
		if cdtime <= nowtime:
			isplanting = 2
		role.SendObj(PETFARM_SHOWROLECD,(isplanting, cdtime))
		role.Msg(2, 0 , GlobalPrompt.PetFarm_BuyCD_Ok)

def __RandomAward(role):
	'''
	发放奖励
	'''
	#如果宠物灵树活动没有开启
	if not __ISPETFARMSTART:
		return
	awardtype = PetFarmConfig.PETFARMRANDOM.RandomOne()
	awardlist = PetFarmConfig.PetFarmHarvestConfigDict.get(awardtype)
	return awardtype, awardlist
	
def OpenPetFarm(role, msg):
	'''
	显示玩家获奖信息
	@param role:
	@param msg:
	'''
	#宠物灵树活动尚未开始
	if not __ISPETFARMSTART:
		return
	roleID = role.GetRoleID()
	#显示玩家数据
	PetFarmData = PETFARMROLEAWARD_DICT.get(roleID, [])
	role.SendObj(PETFARM_SHOWROLEDATA, PetFarmData)
	#如果玩家在种植状态
	isinplantting = 0
	if roleID in PETFARMROLECD_DICT:
		isinplantting = 1
	#如果玩家在收获状态
		if cDateTime.Seconds() >= PETFARMROLECD_DICT.get(roleID):
			isinplantting = 2
	role.SendObj(PETFARM_SHOWROLECD, (isinplantting, PETFARMROLECD_DICT.get(roleID)))
	
def PetFarmAfterLogin(role, param):
	roleID = role.GetRoleID()
	
	isinplantting = 0
	#如果玩家在种植状态
	if roleID in PETFARMROLECD_DICT:
		isinplantting = 1
	#如果玩家在收获状态
		if cDateTime.Seconds() >= PETFARMROLECD_DICT.get(roleID):
			isinplantting = 2
	role.SendObj(PETFARM_SHOWROLECD, (isinplantting, PETFARMROLECD_DICT.get(roleID)))


if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#构建一个持久化字典用来保存进入了种植状态的角色，在活动结束时全部退出种植状态
		PETFARMROLECD_DICT = Contain.Dict("PETFARMROLECD_DICT", (2038, 1, 1), None, None)
		#构建一个持久化字典来保存玩家的历史获奖情况
		PETFARMROLEAWARD_DICT = Contain.Dict("PETFARMROLEAWARD_DICT", (2038, 1, 1), None, None)
	
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, PetFarmStart)
		Event.RegEvent(Event.Eve_EndCircularActive, PetFarmEnd)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, PetFarmAfterLogin)
			
	
		#客户端请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_OpenPetFarm", "客户端请求宠物灵树打开面板"), OpenPetFarm)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_RequestMachine", "客户端请求宠物灵树进入种植状态"), RequestMachine)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_RequestHarvest", "客户端请求宠物灵树收获"), RequestHarvest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_OnekeyHarvest", "客户端请求宠物灵树一键收获"), OnekeyHarvest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_QuickerMachine", "客户端请求宠物灵树快速种植"), QuickerGrow)
	
	

