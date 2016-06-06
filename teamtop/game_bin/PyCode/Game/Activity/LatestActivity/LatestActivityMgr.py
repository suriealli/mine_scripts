#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LatestActivity.LatestActivityMgr")
#===============================================================================
# 最新活动
#===============================================================================
import cComplexServer
import Environment
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumObj, EnumInt16, EnumTempObj, EnumInt32
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.SysData import WorldData
from Game.Activity.LatestActivity import LatestActivityConfig, EnumLatestType, LatestActDefine

if "_HasLoad" not in dir():
	__COSTART_DICT = {}	#通过循环活动开启的活动
	KAIFU_DAY_STARTING_SET = set()	#根据开服天数开启的活动
	LatestActOpenFun_Dict = {}	#打开
	LatestActGetFun_Dict = {}	#获取
	LatestEventActcFun_Dict = {}#事件
	LatestAct_Can_Reward = AutoMessage.AllotMessage("LatestAct_Can_Reward", "通知客户端最新活动有奖励可以领取")
	LatestAct_Opening_Acts = AutoMessage.AllotMessage("LatestAct_Opening_Acts", "通过开服天数方式正在开启的最新活动")
	LatestAct_Can_Reward_List = AutoMessage.AllotMessage("LatestAct_Can_Reward_List", "通知客户端所有可以领取的最新活动奖励")
	LatestAct_Open_Panel_Data = AutoMessage.AllotMessage("LatestAct_Open_Panel_Data", "打开某个最新活动需要发送的数据")
	LatestAct_ActivityTask_Data = AutoMessage.AllotMessage("LatestAct_ActivityTask_Data", "最新活动活跃度奖励数据")
	#日志
	LatestActReward = AutoLog.AutoTransaction("LatestActReward", "最新活动奖励")
	LatestActRewardCost = AutoLog.AutoTransaction("LatestActRewardCost", "最新活动领奖消耗奖励")
#==========================最新活动的开启和关闭=====================================
def StartCircularActive(*param):
	#某个最新活动开启
	_, activetype = param
	min_actType, max_actType = CircularDefine.CA_LatestList
	if activetype > max_actType or activetype < min_actType:
		return
	global __COSTART_DICT
	startBool = __COSTART_DICT.get(activetype, False)
	if startBool:
		print "GE_EXC, LatestActivityMgr activetype(%s) is already started " % activetype
		return
	__COSTART_DICT[activetype] = True

def EndCircularActive(*param):
	#某个最新活动关闭
	_, activetype = param
	min_actType, max_actType = CircularDefine.CA_LatestList
	if activetype > max_actType or activetype < min_actType:
		return
	
	global __COSTART_DICT
	startBool = __COSTART_DICT.get(activetype, False)
	if not startBool:
		print "GE_EXC, LatestActivityMgr activetype(%s) is already ended " % activetype
		return
	if activetype in __COSTART_DICT:
		del __COSTART_DICT[activetype]
#=============================通过开服天数的开启方式=========================
def CallAfterNewDay():
	#开服新的一天
	global KAIFU_DAY_STARTING_SET
	#初始化正在开启的活动
	InitIsActive()
	roleList = cRoleMgr.GetAllRole()
	for role in roleList:
		#同步客户端正在开启的活动
		role.SendObj(LatestAct_Opening_Acts, KAIFU_DAY_STARTING_SET)

def AfterSetKaiFuTime(param1, param2):
	#重新设置开服时间
	global KAIFU_DAY_STARTING_SET
	#初始化正在开启的活动
	InitIsActive()
	roleList = cRoleMgr.GetAllRole()
	for role in roleList:
		#同步客户端正在开启的活动
		role.SendObj(LatestAct_Opening_Acts, KAIFU_DAY_STARTING_SET)
	
def AfterLoadWorldData(param1, param2):
	InitIsActive()

def InitIsActive():
	#初始化正在开启的活动
	global KAIFU_DAY_STARTING_SET
	KAIFU_DAY_STARTING_SET = set()	#清空正在开启的活动
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for actId, cfg in LatestActivityConfig.ACT_BASE_DICT.iteritems():
		if cfg.kaifuDay and kaifuDay > cfg.kaifuDay:
			continue
		if not cfg.startKaifu:
			continue
		for startDay, endDay in cfg.startKaifu:
			if startDay <= kaifuDay <= endDay:
				KAIFU_DAY_STARTING_SET.add(actId)
				break
#=====================各种通用方法=======================
def GetActId():
	'''
	获取当前正在开启的活动id
	'''
	return KAIFU_DAY_STARTING_SET | set(__COSTART_DICT.keys())

def GetActState(actId):
	'''
	检查活动状态，False活动未开启或已结束，True进行中

	'''
	global __COSTART_DICT
	global KAIFU_DAY_STARTING_SET
	
	if actId not in KAIFU_DAY_STARTING_SET and actId not in __COSTART_DICT:
		return False
	else:
		return True
	
def SetActActive(role, actId, reward):
	'''
	激活指定活动的指定奖励
	@param role:
	@param actId:
	@param reward:
	'''
	cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in SetActActive" % actId
		return
	#激活的数据
	LatestActData = role.GetObj(EnumObj.LatestActData)
	#1次性的
	foreverObj = LatestActData.setdefault(1, {})
	#激活的数据(每日清零的)
	DailyObj = LatestActData.setdefault(2, {})
	
	active_list = set()
	geted_dict = {}
	if cfg.daytick:
		active_list = DailyObj.get(actId, set())
		geted_dict = LatestActData.get(4, {})
	else:
		active_list = foreverObj.get(actId, set())
		geted_dict = LatestActData.get(3, {})

	send_bool = False #是否通知客户端
	for rewardId in reward:
		if rewardId not in cfg.rewardList:#奖励ID不是配置表配置的
			continue
		if rewardId in active_list:#已激活
			continue
		if cfg.daytick:#根据是否清零，记录在不同位置
			reward_cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
			if not reward_cfg:
				continue
			if reward_cfg.dayGettimes <= geted_dict.get(rewardId, 0):
				continue
			if actId not in DailyObj:
				DailyObj[actId] = set()
			DailyObj[actId].add(rewardId) #将奖励ID加入激活中
		else:
			if rewardId in geted_dict:
				continue
			if actId not in foreverObj:
				foreverObj[actId] = set()
			foreverObj[actId].add(rewardId)
		if not send_bool:
			send_bool = True
	if send_bool:
		role.SendObj(LatestAct_Can_Reward, 1)
		
def GetCanGetID(role):
	'''
	获取玩家可以领取的奖励
	@param role:
	'''
	#先把已经激活的奖励检测遍，去除已经过期
	LatestActData = role.GetObj(EnumObj.LatestActData)
	foreverData = LatestActData.get(1, {})
	for actId, _ in foreverData.items():
		cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,can not find actId(%s) in GetCanGetID" % actId
			del foreverData[actId]
		state = GetActState(actId)
		if not state:
			del foreverData[actId]
					
	dayClearData = LatestActData.get(2, {})
	for actId, _ in dayClearData.items():
		cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,can not find actId(%s) in GetCanGetID" % actId
			del dayClearData[actId]
		state = GetActState(actId)
		if not state:
			del dayClearData[actId]
	#遍历开启的活动，看有没有玩家达要求的活动
	SetActData(role)
	
def SetActData(role):
	'''
	设置玩家可领取字典,遍历边开启的活动
	@param role:
	'''
	global __COSTART_DICT
	global KAIFU_DAY_STARTING_SET

	#遍历正开启的活动
	for actId, state in __COSTART_DICT.iteritems():
		if actId in EnumLatestType.FillRMB_Latest_List:
			continue
		if actId in EnumLatestType.ConsumeRMB_Latest_List:
			continue
		if not state:#活动结束
			continue

		#该活动是否有可领取奖励，有的话加入可领取列表
		canList = CheckRewardByActId(role, actId)
		if not canList:
			continue
		
		SetActActive(role, actId, canList)
		
	for actId in KAIFU_DAY_STARTING_SET:
		if actId in EnumLatestType.FillRMB_Latest_List:
			continue
		if actId in EnumLatestType.ConsumeRMB_Latest_List:
			continue
		#该活动是否有可领取奖励，有的话加入可领取列表
		canList = CheckRewardByActId(role, actId)
		if not canList:
			continue
		
		SetActActive(role, actId, canList)
		
def CheckRewardByActId(role, actId):
	'''
	检测某个活动是否有奖励可以领取
	@param role:
	@param actId:
	'''
	canList = []
	cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in LatestAct.CheckRewardByActId" % actId
		return canList
	rewardList = cfg.rewardList
	#获取已领取列表
	LatestActData = role.GetObj(EnumObj.LatestActData)
	getedDict = {}
	if cfg.daytick:
		getedDict = LatestActData.get(4, {})
	else:
		getedDict = LatestActData.get(3, {})
	
	for rewardId in rewardList:
		if not cfg.daytick:#不是每日的
			if rewardId in getedDict:
				continue
		else:
			reward_cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
			if not reward_cfg:
				print "GE_EXC,can not find rewardId(%s) and actID(%s) in CheckRewardByActId" % (rewardId, actId)
				return
			if not reward_cfg.dayGettimes:
				if rewardId in getedDict:
					continue
		state = CheckRewardByRewardId(role, actId, rewardId)
		if state:
			canList.append(rewardId)
	return canList

def CheckRewardByRewardId(role, actId, rewardId):
	'''
	检测指定奖励是否能领取
	@param role:
	@param actId:
	@param rewardId:
	'''
	cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,can not find rewardId(%s) in LatestActivity.CheckRewardByRewardId" % rewardId
		return False
	
	
	if cfg.needLevel:
		if role.GetLevel() < cfg.needLevel:
			return False
	if cfg.dayGettimes:
		base_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
		if not base_cfg:
			return False
		if base_cfg.daytick:#只有每日奖励才需判断奖励次数
			dayData = role.GetObj(EnumObj.LatestActData).get(4, {})
			if dayData.get(rewardId, 0) > cfg.dayGettimes:
				return False
	if cfg.mountEvolve:
		MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
		if MountEvolveID != cfg.mountEvolve:
			return False
	if cfg.StarGirlStar:
		starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
		max_level = 0
		for _, girlObj in starGirlMgr.girl_dict.iteritems():
			if girlObj.star_level > max_level:
				max_level = girlObj.star_level
	
		if max_level == 20:#20星的命魂奖励专题活动已领取过，最新活动不予领取
			ProjectGetedObj = role.GetObj(EnumObj.ProjectGetedObj)
			if 94 in ProjectGetedObj.get(1, set()):
				return False
			
		if max_level != cfg.StarGirlStar:
			return False
	if cfg.mountGrade:
		#取坐骑的最小进化数
		MountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if not MountMgr:
			return False
		MIN = 10
		for mountId in MountMgr.MountId_list:
			if mountId in MountMgr.Mount_outData_dict:
				continue
			grade = MountMgr.MountAGDict.get(mountId, 0)
			if MIN > grade:
				MIN = grade
		if MIN != cfg.mountGrade:
			return False
	if cfg.needItem:
		coding, cnt = cfg.needItem
		if role.ItemCnt(coding) < cnt:
			return False
	if cfg.activityScore:
		if role.GetObj(EnumObj.LatestActData).get(6, 0) < cfg.activityScore:
			return False
	if cfg.needPetStarNum:#宠物的星数
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
		IsFalse = False
		for _, pet in petMgr.pet_dict.iteritems():
			if pet.star == cfg.needPetStarNum:
				IsFalse = True
				break
		if not IsFalse:
			return False
	if cfg.needPetGrade:#宠物的阶数
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
		IsFalse = False
		for _, pet in petMgr.pet_dict.iteritems():
			if pet.evoId == cfg.needPetGrade:
				IsFalse = True
		if not IsFalse:
			return False
	if cfg.wingLevel:#羽翼等级
		wingDict = role.GetObj(EnumObj.Wing)[1]
		if not wingDict:
			return False
		MIN = 100
		for _, wingdata in wingDict.iteritems():
			if MIN > wingdata[0]:
				MIN = wingdata[0]
		if MIN != cfg.wingLevel:
			return False
	if cfg.dragonGrade:
		dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
		if not dragonTrainMgr:
			return False
		MIN_GRADE = 10
		for _, dragonObj in dragonTrainMgr.dragon_dict.iteritems():
			if MIN_GRADE > dragonObj.grade:
				MIN_GRADE = dragonObj.grade
		if MIN_GRADE != cfg.dragonGrade:
			return False
	if cfg.washCnt:
		#如果需要的洗练次数不为0，则不能在这里触发
		if role.GetI16(EnumInt16.EquipmentWashNum) < cfg.washCnt:
			return False
	if cfg.StationSoulLevel:
		if role.GetI16(EnumInt16.StationSoulId) < cfg.StationSoulLevel:
			return False
	if cfg.zhanHunStar:
		if role.GetI16(EnumInt16.WarStationStarNum) < cfg.zhanHunStar:
			return False
	if cfg.HallowsCnt:
		#圣器洗练次数
		if role.GetI32(EnumInt32.Hallows_Latest_Times) < cfg.HallowsCnt :
			return False
	return True

def GetReward(role, cfg, actId, backId):
	'''
	#给玩家发奖励
	@param role:
	@param cfg:
	@param actId:
	@param backId:
	'''
	with LatestActReward:
		tips = ""
		tips += GlobalPrompt.Purgatory_Revive_Success
		#物品
		if cfg.rewardItems:
			for item in cfg.rewardItems:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % (item[0], item[1])
			if item[0] in LatestActivityConfig.CHECK_CODING_SET:
				TriggerFillItem(role, item[0])
		#魔晶
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		#金币
		if cfg.money:
			role.IncMoney(cfg.money)
			tips += GlobalPrompt.Money_Tips % cfg.money
		#星灵临时祝福值
		if cfg.TempBless:
			tempBless, keepTime = cfg.TempBless
			starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
			if not starGirlMgr: return
			starGirlMgr.AddTempBless(tempBless, keepTime)
			tips += GlobalPrompt.AddTemp_Bless % tempBless
		#命魂
		if cfg.rewardTarot:
			role.AddTarotCard(cfg.rewardTarot, 1)
			tips += GlobalPrompt.Tarot_Tips % (cfg.rewardTarot, 1)
		name = "actId = %d" % actId
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveLatestAct, name)
	proObj = role.GetObj(EnumObj.LatestActData)
	
	if actId in EnumLatestType.ExchangeItem_Latest_List:
		dailyObj = proObj.get(2)
		if actId in dailyObj:
			del dailyObj[actId]
		TriggerFillItem(role)
			
	act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
	OpenPublicAct((role, act_cfg))
	#重新获取可以领取的活动ID
	sendList = []
	canDict = proObj.get(1)
	if canDict:
		sendList += canDict.keys()
	daycanDict = proObj.get(2)
	if daycanDict:
		sendList += daycanDict.keys()
	role.SendObj(LatestAct_Can_Reward_List, sendList)
	role.Msg(2, 0, tips)
	
def GetGetedReward(role, actId):
	'''
	获取指定活动已领取的奖励
	@param role:
	@param actId:
	'''
	#玩家已领取列表
	GetedRewards = role.GetObj(EnumObj.LatestActData)
	cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in LatestAct" % actId
		return []
	geted_dict = {}
	if cfg.daytick:#跟据是否每日清零求不同的数据
		geted_dict = GetedRewards.get(4, {})
	else:
		geted_dict = GetedRewards.get(3, {})
	sendData = {}
	for reward in cfg.rewardList:
		if reward in geted_dict:
			sendData[reward] = geted_dict.get(reward, 0)
	return sendData
#==================玩家事件处理=====================
def AfterChangeUnbindRMB(role, param):
	#玩家充值神石改变
	oldValue, newValue = param
	
	if oldValue >= newValue:
		return
	right_actId = 0
	for actId in EnumLatestType.FillRMB_Latest_List:
		if GetActState(actId):
			right_actId = actId
			break
	if not right_actId:
		return
	role.IncI32(EnumInt32.LatestFillRMB, newValue - oldValue)
	
def AfterChangeMountEvole(role, param):
	#坐骑阶数发生改变
	actId = EnumLatestType.MountEvolve_Latest
	if not GetActState(actId):
		return
	#坐骑的阶数
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	
	reward = LatestActDefine.MOUNT_EVOLE_DICT.get(evolveId) #@UndefinedVariable
	if not reward: 
		return
	rewardList = [reward]
	SetActActive(role, actId, rewardList)
	
def AfterLogin(role, param):
	LatestActData = role.GetObj(EnumObj.LatestActData)
	if 1 not in LatestActData:
		LatestActData[1] = {}
	if 2 not in LatestActData:
		LatestActData[2] = {}
	if 3 not in LatestActData:
		LatestActData[3] = {}
	if 4 not in LatestActData:
		LatestActData[4] = {}
	if 5 not in LatestActData:
		LatestActData[5] = {}
	if 6 not in LatestActData:
		LatestActData[6] = 0
	if 7 not in LatestActData:#指定星级宠物增加的临时属性
		LatestActData[7] = {}
	if 8 not in LatestActData:#宠物临时修行进度
		LatestActData[8] = {}
	if 9 not in LatestActData:#神龙临时进度
		LatestActData[9] = {}
	#获取玩家可以领取的奖励
	GetCanGetID(role)
	
def SyncRoleOtherData(role, param):
	proObj = role.GetObj(EnumObj.LatestActData)
	if proObj.get(1) or proObj.get(2):
		role.SendObj(LatestAct_Can_Reward, 1)
	
	global KAIFU_DAY_STARTING_SET
	role.SendObj(LatestAct_Opening_Acts, KAIFU_DAY_STARTING_SET)
	#特殊处理
	for actId in EnumLatestType.FillRMB_Latest_List:
		if GetActState(actId):
			act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
			OpenPublicAct((role, act_cfg))
	for actId in EnumLatestType.ConsumeRMB_Latest_List:
		if GetActState(actId):
			act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
			OpenPublicAct((role, act_cfg))
	
def RoleDayClear(role, param):
	#玩家每日清零
	proObj = role.GetObj(EnumObj.LatestActData)
	proObj[2] = {}	#清空
	#清理需要每日清零的已领取奖励
	proObj[4] = {}	#清空
	#活跃度任务
	proObj[5] = {}	#清空
	#活跃度
	proObj[6] = 0	#清空
	
	if role.GetI32(EnumInt32.LatestFillRMB) > 0:
		role.SetI32(EnumInt32.LatestFillRMB, 0)

	for ActId in EnumLatestType.Special_Act_List:
		if ActId in __COSTART_DICT or ActId in KAIFU_DAY_STARTING_SET:
			continue
		if ActId == EnumLatestType.StarGirl_Latest:
			ClearSpeAct(role, LatestActDefine.STARGRIL_START_REWARD_REMOVE.values())
	#需要检测是否有新活动开启了，需要重新获取一次玩家可以领取的奖励
	#但玩家数据清理会在Event.Eve_StartCircularActive 事件触发前执行，所以定了个1分钟的Tick
	role.RegTick(30, TickGetCanGetID, None)
	
	#装备洗练临时数据清理
	role.SetI16(EnumInt16.EquipmentWashNum, 0)

def ClearSpeAct(role, defineData):
	#针对一次性活动的处理，清除已领取的奖励
	if type(defineData) != list:
		return
	proObj = role.GetObj(EnumObj.LatestActData)
	foreverData = proObj.get(3)
	new_dict = {}
	for rid in foreverData.keys():
		if rid not in defineData:
			new_dict[rid] = 1
	proObj[3] = new_dict
	
def TickGetCanGetID(role, callargv, regparam):
	#重新获取次玩家可以领取的奖励
	GetCanGetID(role)
	
def AfterChangeStationSoul(role, param):
	#阵灵等级改变
	actId = EnumLatestType.StationSoul_Latest
	if not GetActState(actId):
		return
	StationSoulId = role.GetI16(EnumInt16.StationSoulId)
	rewardList = set()
	for level, rewardId in LatestActDefine.STATION_SOUL_REWARD.iteritems():
		if StationSoulId < level:
			continue
		rewardList.add(rewardId)
	if not rewardList:
		return
	SetActActive(role, actId, rewardList)
#==========================公用的打开和获取方法========================
def OpenPublicAct(param):
	'''
	打开面板，公用函数
	@param param:
	'''
	role, cfg = param
	actId = cfg.actId
	#已领取
	GetedRewards = GetGetedReward(role, actId)
	latestActData = role.GetObj(EnumObj.LatestActData)
	#可领取
	CanList = set()
	if cfg.daytick:
		dailyObj = latestActData.get(2, {})
		if dailyObj:
			CanList = dailyObj.get(actId, set())
	else:
		foreverObj = latestActData.get(1, {})
		if foreverObj:
			CanList = foreverObj.get(actId, set())
	role.SendObj(LatestAct_Open_Panel_Data, [actId, GetedRewards, CanList])
	
	if actId not in LatestActivityConfig.ACT_TASK_ID_SET:
		return
	role.SendObj(LatestAct_ActivityTask_Data, (latestActData.get(5, {}), latestActData.get(6, 0)))

def GetPublicAct(param):
	'''
	获取奖励，公用函数
	@param param:
	'''
	#获取奖励时只检测是否激活该奖励和活动是否开启，不做条件检测
	role, actId, rewardId, daytick, backId = param
	if not GetActState(actId):#活动未开启
		return
	
	cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,LatestAct can not find rewardId(%s) in cfg" % rewardId
		return
	
	proObj = role.GetObj(EnumObj.LatestActData)
	getedDcit = {}
	coding, cnt = 0, 0
	if cfg.needItem:
		coding, cnt = cfg.needItem
	if daytick == 1:
		dailyObj = proObj.get(2)
		if rewardId not in dailyObj.get(actId, set()):#可领取奖励里没有该奖励
			return
		if coding and cnt:
			if role.ItemCnt(coding) < cnt:#这种情况存在与玩家激活了奖励，却删除了道具，导致数量不够
				dailyObj[actId].remove(rewardId)
				act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
				OpenPublicAct((role, act_cfg))
				role.Msg(2, 0, GlobalPrompt.JTItemLackOf)
				return
		dailyObj[actId].remove(rewardId)#存在的话就移除该奖励
		if dailyObj[actId] == set():
			del dailyObj[actId]
		getedDcit = proObj.get(4, {})
	else:
		foreverObj = proObj.get(1)
		if rewardId not in foreverObj.get(actId, set()):#可领取奖励里没有该奖励
			return
		if coding and cnt:
			if role.ItemCnt(coding) < cnt:#这种情况存在与玩家激活了奖励，却删除了道具，导致数量不够
				foreverObj[actId].remove(rewardId)
				act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
				OpenPublicAct((role, act_cfg))
				role.Msg(2, 0, GlobalPrompt.JTItemLackOf)
				return
		foreverObj[actId].remove(rewardId)#存在的话就移除该奖励
		if foreverObj[actId] == set():
			del foreverObj[actId]
		getedDcit = proObj.get(3, {})
	if coding and cnt:
		with LatestActRewardCost:
			if role.DelItem(coding, cnt) < cnt:
				return
	#加入已领取字典
	getedDcit[rewardId] = getedDcit.get(rewardId, 0) + 1
	#发降
	GetReward(role, cfg, actId, backId)
	
def GetFillRMB(param):
	#领取充值满额送礼活动奖励
	role, actId, rewardId, _, backId = param
	if not GetActState(actId):#活动未开启
		return
	
	cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,LatestAct can not find rewardId(%s) in cfg" % rewardId
		return
	
	proObj = role.GetObj(EnumObj.LatestActData)
	
	#LatestFillRMB = role.GetI32(EnumInt32.LatestFillRMB)
	LatestFillRMB = role.GetDayBuyUnbindRMB_Q()
	#可以领取的次数
	canTimes = LatestFillRMB / cfg.needFillRMB_D
	
	getedDcit = proObj.get(4, {})
	if getedDcit.get(rewardId, 0) >= canTimes:
		act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
		OpenPublicAct((role, act_cfg))
		return
	#加入已领取字典
	getedDcit[rewardId] = getedDcit.get(rewardId, 0) + 1
	#发降
	GetReward(role, cfg, actId, backId)
	
def GetConsumeRMB(param):
	#领取消费满额送礼活动奖励
	role, actId, rewardId, _, backId = param
	if not GetActState(actId):#活动未开启
		return
	
	cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,LatestAct can not find rewardId(%s) in cfg" % rewardId
		return
	
	proObj = role.GetObj(EnumObj.LatestActData)
	
	#这里不会扣， 直接用每日消费充值神石了
	consumeRMB = role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q)
	#可以领取的次数
	canTimes = consumeRMB / cfg.needConsumeRMB
	
	getedDcit = proObj.get(4, {})
	if getedDcit.get(rewardId, 0) >= canTimes:
		act_cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
		OpenPublicAct((role, act_cfg))
		return
	#加入已领取字典
	getedDcit[rewardId] = getedDcit.get(rewardId, 0) + 1
	#发奖
	GetReward(role, cfg, actId, backId)
#=====================================各种事件=========================================
def SetEventFun():
	global LatestEventActcFun_Dict
	LatestEventActcFun_Dict[EnumLatestType.StarGirl_Latest] = CheckStarGirlStar 	#星灵升星
	LatestEventActcFun_Dict[EnumLatestType.MountGrade_Latest] = CheckMountGrade 	#坐骑进化
	LatestEventActcFun_Dict[EnumLatestType.PetTrain_Latest] = CheckPetTrain			#宠物培养升星
	LatestEventActcFun_Dict[EnumLatestType.PetEvo_Latest] = CheckPetEvo				#宠物修行
	LatestEventActcFun_Dict[EnumLatestType.WingTrain_Latest] = CheckWingTrain		#羽翼培养
	LatestEventActcFun_Dict[EnumLatestType.DragonTrain_Latest] = CheckDragonTrain	#神龙进化日
	LatestEventActcFun_Dict[EnumLatestType.EquipmentWash_Latest] = AfterEquipmentWash	#装备洗练日
	LatestEventActcFun_Dict[EnumLatestType.ZhanHun_Latest] = AfterZhanHun_UpStar	#战魂培养日
	LatestEventActcFun_Dict[EnumLatestType.Hallows_Latest] = AfterHallows_Latest	#圣器洗练日
	
def GetFunByType(Etype, param = None):
	fun = LatestEventActcFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, GetFunByType error Etype(%s)" % Etype
		return
	fun(param)
	
#=======圣器洗练日======
def AfterHallows_Latest(param):
	role, _ = param
	
	actId = EnumLatestType.Hallows_Latest
	if not GetActState(actId):
		return
	starNum = role.GetI32(EnumInt32.Hallows_Latest_Times)
	rewardList = set()
	for star, rewardId in LatestActDefine.HALLOWS_WASH.iteritems():
		if star > starNum:
			continue
		rewardList.add(rewardId)
	if not rewardList:
		return
	SetActActive(role, actId, rewardList)
#=======羽翼培养======
def AfterZhanHun_UpStar(param):
	role, _ = param
	
	actId = EnumLatestType.ZhanHun_Latest
	if not GetActState(actId):
		return
	starNum = role.GetI16(EnumInt16.WarStationStarNum)
	rewardList = set()
	for star, rewardId in LatestActDefine.ZhanHun_Star.iteritems():
		if star > starNum:
			continue
		rewardList.add(rewardId)
	if not rewardList:
		return
	SetActActive(role, actId, rewardList)
	
	
#=======羽翼培养======
def CheckWingTrain(param):
	actId = EnumLatestType.WingTrain_Latest
	if not GetActState(actId):
		return
	role = param
	wingDict = role.GetObj(EnumObj.Wing)[1]
	if not wingDict:
		return
	MIN = 100
	for _, wingdata in wingDict.iteritems():
		if MIN > wingdata[0]:
			MIN = wingdata[0]
	rewardId = LatestActDefine.WING_TRAIN_REWARD.get(MIN)
	if not rewardId:
		return
	SetActActive(role, actId, [rewardId])
#=====星灵相关========
def CheckStarGirlStar(param):
	role, _ = param
	actId = EnumLatestType.StarGirl_Latest
	if not GetActState(actId):
		return
	
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	max_level = 0
	for _, girlObj in starGirlMgr.girl_dict.iteritems():
		if girlObj.star_level > max_level:
			max_level = girlObj.star_level
			
	if max_level == 20:#20星的命魂奖励专题活动已领取过，最新活动不予领取
		ProjectGetedObj = role.GetObj(EnumObj.ProjectGetedObj)
		if 94 in ProjectGetedObj.get(1, set()):
			return
	reward = LatestActDefine.STARGRIL_START_REWARD.get(max_level)
	if not reward: return
	rewardList = [reward]
	#激活奖励
	SetActActive(role, actId, rewardList)
	
#=====活跃度任务========
def DoActivityTask(role, param):
	index, cnt = param
	actIdSet = GetActId() & LatestActivityConfig.ACT_TASK_ID_SET
	if not actIdSet:
		return
	for actId in actIdSet:
		break
	cfg = LatestActivityConfig.ACT_TASK_DICT.get((actId, index))
	if not cfg:
		return
	
	finish_cnt = role.GetObj(EnumObj.LatestActData).get(5, {}).get(index, 0)
	if finish_cnt >= cfg.max_cnt:
		#任务完成了
		return
	
	if cfg.consume and cfg.consume > cnt:
		#消费任务
		return
	if cfg.fill and cfg.fill > cnt:
		#充值任务
		return
	
	if cfg.max_cnt < cnt:
		cnt = cfg.max_cnt
	
	if finish_cnt + cnt > cfg.max_cnt:
		add_score_cnt = cfg.max_cnt - finish_cnt
		role.GetObj(EnumObj.LatestActData)[5][index] = cfg.max_cnt
	else:
		add_score_cnt = cnt
		role.GetObj(EnumObj.LatestActData)[5][index] = finish_cnt + cnt
	
	role.GetObj(EnumObj.LatestActData)[6] += cfg.score * add_score_cnt
	
	TriggerActivityReward(role, actId)
	
	role.SendObj(LatestAct_ActivityTask_Data, (role.GetObj(EnumObj.LatestActData).get(5, {}), role.GetObj(EnumObj.LatestActData).get(6, 0)))
	
#====坐骑进化=====
def CheckMountGrade(param):
	#坐骑进化或增加坐骑触发
	role = param
	actId = EnumLatestType.MountGrade_Latest
	if not GetActState(actId):
		return
	MountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	MIN = 10
	for mountId in MountMgr.MountId_list:
		if mountId in MountMgr.Mount_outData_dict:
			continue
		grade = MountMgr.MountAGDict.get(mountId, 0)
		if MIN > grade:
			MIN = grade
	rewardId = LatestActDefine.MOUNT_GRADE_DICT.get(MIN)
	if not rewardId:
		return
	#激活奖励
	SetActActive(role, actId, [rewardId])

#=======兑换得豪礼活动========
def TriggerFillItem(role, coding = 0):
	right_actId = 0
	for actId in EnumLatestType.ExchangeItem_Latest_List:
		if GetActState(actId):
			right_actId = actId
			break
	if not right_actId:
		return
	
	roleCnt = 0
	if coding:
		roleCnt = role.ItemCnt_NotTimeOut(coding)
	else:
		actCfg = LatestActivityConfig.ACT_BASE_DICT.get(right_actId)
		if not actCfg:
			return
		if not actCfg.checkCoding:
			return
		roleCnt = role.ItemCnt_NotTimeOut(actCfg.checkCoding)
	rewardList = set()
	defineData = LatestActDefine.EXCHANGE_ITEM_DICT.get(right_actId)
	if not defineData:
		print "GE_EXC,LatestActDefine.EXCHANGE_ITEM_DICT has not actId(%s)" % right_actId
		return
	for cnt, rewardId in defineData.iteritems():
		if roleCnt < cnt:
			continue
		rewardList.add(rewardId)
	if not rewardList:
		return
	#激活奖励
	SetActActive(role, right_actId, rewardList)
	
#==========宠物培养日===========
def CheckPetTrain(param):
	if not GetActState(EnumLatestType.PetTrain_Latest):
		return
	role, star = param
	rewardId = LatestActDefine.PET_STAR_REWARD.get(star, 0)
	if not rewardId:
		return
	#激活奖励
	SetActActive(role, EnumLatestType.PetTrain_Latest, [rewardId])
#==========宠物修行日===========
def CheckPetEvo(param):
	if not GetActState(EnumLatestType.PetEvo_Latest):
		return
	role, evoId = param
	rewardId = LatestActDefine.PET_EVO_REWARD.get(evoId)
	if not rewardId:
		return
	#激活奖励
	SetActActive(role, EnumLatestType.PetEvo_Latest, [rewardId])
#=========活跃度=============
def TriggerActivityReward(role, actId):
	roleActScore = role.GetObj(EnumObj.LatestActData).get(6, 0)
	if not roleActScore:
		return
	rewardList = set()
	rewardDict = LatestActDefine.ACTIVITY_REWARD.get(actId)
	if not rewardDict:
		return
	for act, rewardId in rewardDict.iteritems():
		if roleActScore < act:
			continue
		rewardList.add(rewardId)
	if not rewardList:
		return
	#激活奖励
	SetActActive(role, actId, rewardList)
	
#===========龙脉============
def CheckDragonTrain(param):
	actId = EnumLatestType.DragonTrain_Latest
	if not GetActState(actId):
		return
	role = param
	
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	if not dragonTrainMgr:
		return
	MIN_GRADE = 10
	for _, dragonObj in dragonTrainMgr.dragon_dict.iteritems():
		if MIN_GRADE > dragonObj.grade:
			MIN_GRADE = dragonObj.grade
	
	rewardId = LatestActDefine.DRAGON_TRAIN_REWARD.get(MIN_GRADE)
	if not rewardId:
		return
	#激活奖励
	SetActActive(role, actId, [rewardId])
#===========装备洗练============
def AfterEquipmentWash(param):
	'''
	洗练装备后判断是否有奖励可以领取
	@param role:
	@param param:
	'''
	role, cnt = param
	#装备洗练对应ID
	actId = EnumLatestType.EquipmentWash_Latest
	if not GetActState(actId):
		return
	if cnt > 0:
		role.IncI16(EnumInt16.EquipmentWashNum, cnt)
	
	WashCnt = role.GetI16(EnumInt16.EquipmentWashNum)
	for i in LatestActDefine.EQUIPMENT_WASH:
		if i[0] > WashCnt:
			break
		rewardId = i[1]
		#激活奖励
		SetActActive(role, actId, [rewardId])
#==============================打开================================
def LoadOpenFunByType():
	global LatestActOpenFun_Dict
	LatestActOpenFun_Dict[EnumLatestType.MountEvolve_Latest]	 = OpenPublicAct	#坐骑培养日
	LatestActOpenFun_Dict[EnumLatestType.StarGirl_Latest]		 = OpenPublicAct	#星灵专题
	LatestActOpenFun_Dict[EnumLatestType.Activity_Latest_1]		 = OpenPublicAct	#活跃度
	LatestActOpenFun_Dict[EnumLatestType.MountGrade_Latest]		 = OpenPublicAct	#坐骑进化日
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest]		 = OpenPublicAct	#充值满额送礼
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest]	 = OpenPublicAct	#兑换得豪礼活动
	LatestActOpenFun_Dict[EnumLatestType.Activity_Latest_2]		 = OpenPublicAct	#活跃度
	LatestActOpenFun_Dict[EnumLatestType.Activity_Latest_3]		 = OpenPublicAct	#活跃度
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_2]		 = OpenPublicAct	#充值满额送礼2
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_2]	 = OpenPublicAct	#兑换得豪礼活动2
	LatestActOpenFun_Dict[EnumLatestType.PetTrain_Latest]		 = OpenPublicAct	#宠物培养日
	LatestActOpenFun_Dict[EnumLatestType.PetEvo_Latest]		 	 = OpenPublicAct	#宠物修行日
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_3]		 = OpenPublicAct	#充值满额送礼3
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_3] = OpenPublicAct	#兑换得豪礼活动3
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_4]	 	 = OpenPublicAct	#充值满额送礼4
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_4] = OpenPublicAct	#兑换得豪礼活动4
	LatestActOpenFun_Dict[EnumLatestType.WingTrain_Latest]		 = OpenPublicAct	#羽翼培养日
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_5]	 	 = OpenPublicAct	#充值满额送礼5
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_5] = OpenPublicAct	#兑换得豪礼活动5
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_6]	 	 = OpenPublicAct	#充值满额送礼6
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_6] = OpenPublicAct	#兑换得豪礼活动6
	LatestActOpenFun_Dict[EnumLatestType.DragonTrain_Latest] 	 = OpenPublicAct	#神龙进化日
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_7]	 	 = OpenPublicAct	#充值满额送礼7
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_7] = OpenPublicAct	#兑换得豪礼活动7
	LatestActOpenFun_Dict[EnumLatestType.EquipmentWash_Latest] 	 = OpenPublicAct	#装备洗练日
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_8]	 	 = OpenPublicAct	#充值满额送礼8
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_8] = OpenPublicAct		#兑换得豪礼活动8
	LatestActOpenFun_Dict[EnumLatestType.ConsumeRMB_Latest_1] 	= OpenPublicAct	#充值满额送好礼1
	LatestActOpenFun_Dict[EnumLatestType.ConsumeRMB_Latest_2] 	= OpenPublicAct	#充值满额送好礼2
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_9] = OpenPublicAct			#兑换得豪礼活动9
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_10] = OpenPublicAct		#兑换得豪礼活动10
	LatestActOpenFun_Dict[EnumLatestType.StationSoul_Latest] = OpenPublicAct		#战灵培养日
	LatestActOpenFun_Dict[EnumLatestType.ZhanHun_Latest] = OpenPublicAct			#战魂培养日
	LatestActOpenFun_Dict[EnumLatestType.Hallows_Latest] = OpenPublicAct			#圣器洗练日
	LatestActOpenFun_Dict[EnumLatestType.FillRMB_Latest_11] = OpenPublicAct		#充值满额送礼-圣器洗练
	LatestActOpenFun_Dict[EnumLatestType.ExchangeItem_Latest_11] = OpenPublicAct	#兑换得豪礼-圣器洗炼

def GetOpenFunByType(Etype, param):
	global LatestActOpenFun_Dict
	fun = LatestActOpenFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, LatestAct Etype(%s) not in ProActOpenFun_Dict" % Etype
		return
	fun(param)
#==============================获取================================
def LoadGetFunByType():
	global LatestActGetFun_Dict
	LatestActGetFun_Dict[EnumLatestType.MountEvolve_Latest]	 = GetPublicAct		#坐骑培养日
	LatestActGetFun_Dict[EnumLatestType.StarGirl_Latest]	 = GetPublicAct		#星灵专题
	LatestActGetFun_Dict[EnumLatestType.Activity_Latest_1]	 = GetPublicAct		#活跃度
	LatestActGetFun_Dict[EnumLatestType.MountGrade_Latest]	 = GetPublicAct		#坐骑进化日
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest]		 = GetFillRMB		#充值满额送礼
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest] = GetPublicAct		#兑换得豪礼活动
	LatestActGetFun_Dict[EnumLatestType.Activity_Latest_2]	 = GetPublicAct		#活跃度
	LatestActGetFun_Dict[EnumLatestType.Activity_Latest_3]	 = GetPublicAct		#活跃度
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_2]	 = GetFillRMB		#充值满额送礼2
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_2] = GetPublicAct	#兑换得豪礼活动2
	LatestActGetFun_Dict[EnumLatestType.PetTrain_Latest]	 = GetPublicAct		#宠物培养日
	LatestActGetFun_Dict[EnumLatestType.PetEvo_Latest]		 = GetPublicAct		#宠物修行日
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_3]	 = GetFillRMB		#充值满额送礼3
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_3] = GetPublicAct	#兑换得豪礼活动3
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_4]	 = GetFillRMB		#充值满额送礼4
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_4] = GetPublicAct	#兑换得豪礼活动4
	LatestActGetFun_Dict[EnumLatestType.WingTrain_Latest]	 = GetPublicAct		#羽翼培养日
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_5]	 = GetFillRMB		#充值满额送礼5
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_5] = GetPublicAct	#兑换得豪礼活动5
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_6]	 = GetFillRMB		#充值满额送礼6
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_6] = GetPublicAct	#兑换得豪礼活动6
	LatestActGetFun_Dict[EnumLatestType.DragonTrain_Latest] = GetPublicAct		#神龙进化日
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_7]	 = GetFillRMB		#充值满额送礼7
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_7] = GetPublicAct	#兑换得豪礼活动7
	LatestActGetFun_Dict[EnumLatestType.EquipmentWash_Latest] = GetPublicAct	#装备洗练日
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_8]	 = GetFillRMB		#充值满额送礼8
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_8] = GetPublicAct	#兑换得豪礼活动8
	LatestActGetFun_Dict[EnumLatestType.ConsumeRMB_Latest_1] = GetConsumeRMB	#消费满额送好礼1
	LatestActGetFun_Dict[EnumLatestType.ConsumeRMB_Latest_2] = GetConsumeRMB	#消费满额送好礼2
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_9] = GetPublicAct	#兑换得豪礼活动9
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_10] = GetPublicAct	#兑换得豪礼活动10
	LatestActGetFun_Dict[EnumLatestType.StationSoul_Latest] = GetPublicAct		#战灵培养日
	LatestActGetFun_Dict[EnumLatestType.ZhanHun_Latest] = GetPublicAct			#兑换得豪礼活动8
	LatestActGetFun_Dict[EnumLatestType.Hallows_Latest] = GetPublicAct			#圣器洗练日
	LatestActGetFun_Dict[EnumLatestType.FillRMB_Latest_11] = GetFillRMB		#充值满额送礼-圣器洗练
	LatestActGetFun_Dict[EnumLatestType.ExchangeItem_Latest_11] = GetPublicAct	#兑换得豪礼-圣器洗炼
	
def GetGetFunByType(Etype, param):
	global LatestActGetFun_Dict
	fun = LatestActGetFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, LatestAct Etype(%s) not in ProActGetFun_Dict" % Etype
		return
	fun(param)
#=======================客户端消息========================
def RequestOpenPanel(role, param):
	'''
	客户端请求打开最新活动界面
	@param role:
	@param param:
	'''
	proObj = role.GetObj(EnumObj.LatestActData)
	sendList = []
	canDict = proObj.get(1)#激活的一次性活动ID
	if canDict:
		sendList += canDict.keys()
	daycanDict = proObj.get(2)#每日清零的活动ID
	if daycanDict:
		sendList += daycanDict.keys()
	role.SendObj(LatestAct_Can_Reward_List, sendList)
	role.SendObj(LatestAct_ActivityTask_Data, (proObj.get(5, {}), proObj.get(6, 0)))
	
def RequestOpenAct(role, param):
	'''
	客户端请求打开某个活动
	@param role:
	@param param:
	'''
	actId = param
	if not actId:
		return
	cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,LatestAct OpenAct can not find actId(%s)" % actId
		return
	GetOpenFunByType(actId, (role, cfg))
	
def RequestGetReward(role, param):
	'''
	客户端请求获取奖励
	@param role:
	@param param:
	'''
	backId, (actId, rewardId) = param
	cfg = LatestActivityConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,LatestAct can not find actId(%s) in ACT_BASE_DICT" % actId
		return
	state = GetActState(actId)
	if not state:#活动未开启
		return
	
	if rewardId not in cfg.rewardList:#该活动不存在该奖励ID
		print "GE_EXC,LatestAct GetReward but rewardId(%s) and actId(%s) not in rewardList" % (rewardId, actId)
		return
	LatestActData = role.GetObj(EnumObj.LatestActData)
	if cfg.daytick:
		getedData = LatestActData.get(4, {})
		reward_cfg = LatestActivityConfig.ACT_REWARD_DICT.get(rewardId)
		if not reward_cfg:
			return
		if reward_cfg.dayGettimes:
			if getedData.get(rewardId, 0) >= reward_cfg.dayGettimes:#每日领取次数已达标
				return
		else:
			if rewardId in getedData:
				return
	else:
		if rewardId in LatestActData.get(3, {}):#奖励已领取
			return
	GetGetFunByType(actId, (role, actId, rewardId, cfg.daytick, backId))

def AfterLevelUp(role, param):
	actId = EnumLatestType.EquipmentWash_Latest
	if not GetActState(actId):
		return
	if role.GetLevel() < 100:
		return
	
	AfterEquipmentWash((role, 0))

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGetFunByType()
		LoadOpenFunByType()
		SetEventFun()
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterMountEvolve, AfterChangeMountEvole)
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeUnbindRMB)  
		Event.RegEvent(Event.Eve_LatestActivityTask, DoActivityTask)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_AfterChangeStationSoul, AfterChangeStationSoul)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LatestAct_Open_Act_Panel", "客户端请求打开最新活动界面"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LatestAct_Open_Act", "客户端请求打开指定最新活动"), RequestOpenAct)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LatestAct_Get_Reward", "客户端请求获取最新活动奖励"), RequestGetReward)
