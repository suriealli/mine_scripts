#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ProjectAct.ProjectAct")
#===============================================================================
# 专题活动
#===============================================================================
import Environment
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Hero import HeroConfig
from Game.Role.Data import EnumObj, EnumInt32, EnumInt16, EnumTempObj
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.ProjectAct import ProjectActConfig, ProjectActDefine, EnumProActType

if "_HasLoad" not in dir():
	
	ProActGetFun_Dict = {}
	ProActOpenFun_Dict = {}
	ProjectActcFun_Dict = {}
	
	__COSTART_DICT = {}	#各种专题活动开关
	ProjectAct_Can_Reward = AutoMessage.AllotMessage("ProjectAct_Can_Reward", "通知客户端专属活动有奖励可以领取")
	ProjectAct_Can_Reward_Dict = AutoMessage.AllotMessage("ProjectAct_Can_Reward_Dict", "通知客户端所有可以领取的专属活动奖励")
	ProjectAct_Open_Panel_Data = AutoMessage.AllotMessage("ProjectAct_Open_Panel_Data", "打开某个专属活动需要发送的数据")

	#日志
	ProjectActReward = AutoLog.AutoTransaction("ProjectActReward", "专属活动奖励")

#==========================专题活动的开启和关闭=====================================
def StartCircularActive(*param):
	#某个专题活动开启
	_, activetype = param
	if activetype not in CircularDefine.CA_ProjectActList:
		return
	
	global __COSTART_DICT
	startBool = __COSTART_DICT.get(activetype, False)
	if startBool:
		print "GE_EXC, ProjectAct activetype(%s) is already started " % activetype
		return
	__COSTART_DICT[activetype] = True

def EndCircularActive(*param):
	#某个专题活动关闭
	_, activetype = param
	if activetype not in CircularDefine.CA_ProjectActList:
		return
	
	global __COSTART_DICT
	startBool = __COSTART_DICT.get(activetype, False)
	if not startBool:
		print "GE_EXC, ProjectAct activetype(%s) is already ended " % activetype
		return
	if activetype in __COSTART_DICT:
		del __COSTART_DICT[activetype]

def GetActState(actId):
	'''
	检查活动状态，False活动未开启或已结束，True进行中

	'''
	global __COSTART_DICT
	
	return __COSTART_DICT.get(actId, False)
#=====================================各种事件=========================================
def SetWonderIncFun():
	global ProjectActcFun_Dict
	ProjectActcFun_Dict[EnumProActType.ProjectGemEvent] = CheckGemAct	 #宝石合成相关
	ProjectActcFun_Dict[EnumProActType.ProjectMountEvent] = CheckMountCulAct#坐骑神石培养相关
	ProjectActcFun_Dict[EnumProActType.ProjectWishEvent] = CheckWishState	 #许愿池相关
	ProjectActcFun_Dict[EnumProActType.ProjectTatotEvent] = CheckTarotState #高级占卜相关
	ProjectActcFun_Dict[EnumProActType.ProjectWingEvent] = CheckWingState  #羽翼相关
	ProjectActcFun_Dict[EnumProActType.ProjectFuwenEvent] = CheckFuwenAct   #符文相关
	ProjectActcFun_Dict[EnumProActType.ProjectPetEvent] = CheckPetAct     #宠物相关
	ProjectActcFun_Dict[EnumProActType.ProjectRingEvent] = CheckRingAct    #婚戒相关
	ProjectActcFun_Dict[EnumProActType.ProjectStarGirlStarEvent] = CheckStarGirlStar #星灵升星

	
def GetFunByType(Etype, param = None):
	fun = ProjectActcFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, GetFunByType error Etype(%s)" % Etype
		return
	fun(param)
#======================================下面为事件处理===========================================

#=======宝石相关=========
def CheckGemAct(param):
	'''
	检测专题宝石活动
	@param role:
	'''
	role, level, cnt = param
	starting_act = []
	for actId in EnumProActType.GEM_ACT_LIST:#遍历宝石系列活动，取出开启中的活动
		if GetActState(actId):
			starting_act.append(actId)
	if not starting_act:#没有该系列活动开启
		return

	for actId in starting_act:
		SetGemData(role, actId, level, cnt)
		
def SetGemData(role, actId, level, cnt):
	#设置玩家宝石合成数据
	#玩家合成宝石相关数据
	GemObj = role.GetObj(EnumObj.ProjectDataObj)
	if actId not in GemObj:#没有该活动的相关数据
		GemObj[actId] = {}
	actObj = GemObj[actId]
	actObj[level] = actObj.get(level, 0) + cnt
#	lower_list = []#取出5-10级中，比合成宝石相等或低的等级
#	for lv in ProjectActDefine.GEM_LEVEL_EVAL:
#		if lv <= level:
#			lower_list.append(lv)
#	if not lower_list:
#		return
#	for glv in lower_list:#每种宝石加上合成数
#		actObj[glv] = actObj.get(glv, 0) + cnt * (2 ** (level - glv))
	
	#根据活动取配置
	define_dict = ProjectActDefine.GEM_LEVEL_NUM_REWARD
	
	active_reward = set()	#缓冲激活的奖励
	for lv, num in actObj.iteritems():
		reward_evl = define_dict.get(lv)#根据宝石等级取配置
		if not reward_evl:
			continue
		for needcnt, reward in reward_evl.iteritems():
			if num >= needcnt:#大于指定数量的就激活奖励
				active_reward.add(reward)
	if not active_reward:
		return
	SetActActive(role, actId, active_reward)
#===============坐骑相关===================
def CheckMountCulAct(param):
	'''
	检测坐骑神石培养专题
	@param param:
	'''
	role, cnt = param

	starting_act = []
	for actId in EnumProActType.MOUNT_ACT_LIST2:#遍历宝石系列活动，取出开启中的活动
		if GetActState(actId):
			starting_act.append(actId)
	if not starting_act:#没有该系列活动开启
		return
	#增加神石培养次数
	role.IncI32(EnumInt32.MountCultivateTimes, cnt)
	totalNum = role.GetI32(EnumInt32.MountCultivateTimes)
	if totalNum < ProjectActDefine.MIN_MOUNT_TIMES:
		return
	for actId in starting_act:
		SetMountData(role, actId)

def SetMountData(role, actId):
	#设置玩家培养坐骑数据
	#总培养次数
	totalNum = role.GetI32(EnumInt32.MountCultivateTimes)
	
	define_dict = {}
	if Environment.EnvIsNA():
		define_dict = ProjectActDefine.CUL_NUM_DICT_NA.get(actId)
		if not define_dict:
			print "GE_EXC,ProjectActDefine.CUL_NUM_DICT_NA is Wrong actId(%s)" % actId
			return
	else:
		define_dict = ProjectActDefine.CUL_NUM_DICT.get(actId)
		if not define_dict:
			print "GE_EXC,ProjectActDefine.CUL_NUM_DICT is Wrong actId(%s)" % actId
			return
	active_reward = set()
	for num, reward in define_dict.iteritems():
		if num <= totalNum:#培养次数大于或等于配置次数，激活奖励
			active_reward.add(reward)
	if not active_reward:
		return
	SetActActive(role, actId, active_reward)

#===========许愿池相关===========
def CheckWishState(param):
	#专题活动许愿池
	role, cnt = param
	if not cnt:
		return
	if not GetActState(EnumProActType.Wish_ProAct):
		return
	role.IncI32(EnumInt32.ProjectWishTimes, cnt)
	total_times = role.GetI32(EnumInt32.ProjectWishTimes)
	if total_times < ProjectActDefine.MIN_WISH_TIMES:#次数没达到最小次数要求
		return
	active_reward = set()
	for deftimes, reward in ProjectActDefine.WISH_TIMES_REWARD.iteritems():
		if total_times >= deftimes:
			active_reward.add(reward)
	#激活奖励
	SetActActive(role, EnumProActType.Wish_ProAct, active_reward)
#==========高级占卜==========
def CheckTarotState(param):
	#专题高级占卜
	role, grade = param
	if grade not in ProjectActDefine.GRADE_LIST:
		return
	actId = EnumProActType.Tarot_ProAct
	if not GetActState(actId):
		return
	DataObj = role.GetObj(EnumObj.ProjectDataObj)
	if actId not in DataObj:
		DataObj[actId] = {}
	actData = DataObj.get(actId)
	for degrade in ProjectActDefine.GRADE_LIST:
		if grade >= degrade:
			actData[degrade] = actData.get(degrade, 0) + 1
	
	active_reward = set()
	for detype, timesDict in ProjectActDefine.TAROT_TIMES_REWARD.iteritems():
		totalCnt = actData.get(detype)
		if detype > grade:
			continue
		for times, rewardId in timesDict.iteritems():
			if totalCnt >= times:
				active_reward.add(rewardId)
	#激活奖励
	SetActActive(role, EnumProActType.Tarot_ProAct, active_reward)

#==========羽翼培养==========
def CheckWingState(param):
	#羽翼专题
	role, cnt = param
	if not cnt:
		return
	if not GetActState(EnumProActType.Wing_ProAct):
		return
	role.IncI32(EnumInt32.ProjectWingTimes, cnt)
	total_times = role.GetI32(EnumInt32.ProjectWingTimes)
	if total_times < ProjectActDefine.MIN_WING_TIMES:#次数没达到最小次数要求
		return
	active_reward = set()
	
	wing_times_dict = {}
	if Environment.EnvIsNA():
		wing_times_dict = ProjectActDefine.WING_TIMES_REWARD_NA
	else:
		wing_times_dict = ProjectActDefine.WING_TIMES_REWARD
		
	for deftimes, reward in wing_times_dict.iteritems():
		if total_times >= deftimes:
			active_reward.add(reward)
	#激活奖励
	SetActActive(role, EnumProActType.Wing_ProAct, active_reward)
	
#=======符文相关=========
def CheckFuwenAct(param):
	'''
	检测专题符文活动
	@param role:
	'''
	role, level, cnt = param
	
	actId = EnumProActType.FuWen_ProAct
	if not GetActState(actId):#活动未开启
		return

	FuwenObj = role.GetObj(EnumObj.ProjectDataObj)
	if actId not in FuwenObj:#没有该活动的相关数据
		FuwenObj[actId] = {}
	actObj = FuwenObj[actId]
	actObj[level] = actObj.get(level, 0) + cnt
	
	#根据活动取配置
	define_dict = {}
	if Environment.EnvIsNA():
		define_dict = ProjectActDefine.FUWEN_LEVEL_NUM_REWARD_NA
	else:
		define_dict = ProjectActDefine.FUWEN_LEVEL_NUM_REWARD
	
	active_reward = set()	#缓冲激活的奖励
	for lv, num in actObj.iteritems():
		reward_evl = define_dict.get(lv)#根据符文等级取配置
		if not reward_evl:
			continue
		for needcnt, reward in reward_evl.iteritems():
			if num >= needcnt:#大于指定数量的就激活奖励
				active_reward.add(reward)
	if not active_reward:
		return
	SetActActive(role, actId, active_reward)

#=======宠物相关=========
def CheckPetAct(param):
	'''
	宠物专题
	@param param:
	'''
	role, cnt = param
	if not cnt:
		return
	actId = EnumProActType.Pet_Project
	if not GetActState(actId):
		return
	
	PetObj = role.GetObj(EnumObj.ProjectDataObj)
	if actId not in PetObj:#没有该活动的相关数据
		PetObj[actId] = 0
	
	PetObj[actId] = PetObj.get(actId, 0) + cnt
	total_times = PetObj[actId]
	if total_times < ProjectActDefine.MIN_PET_TIMES:#次数没达到最小次数要求
		return
	active_reward = set()
	
	pet_times_dict = {}
	if Environment.EnvIsNA():
		pet_times_dict = ProjectActDefine.PET_TIMES_REWARD_NA
	else:
		pet_times_dict = ProjectActDefine.PET_TIMES_REWARD
	
	for deftimes, reward in pet_times_dict.iteritems():
		if total_times >= deftimes:
			active_reward.add(reward)
	#激活奖励
	SetActActive(role, EnumProActType.Pet_Project, active_reward)
	
#=======婚戒相关=========
def CheckRingAct(param):
	#婚戒专题
	role, cnt = param
	if not cnt:
		return
	actId = EnumProActType.Ring_Project
	if not GetActState(actId):
		return
	
	RingObj = role.GetObj(EnumObj.ProjectDataObj)
	if actId not in RingObj:#没有该活动的相关数据
		RingObj[actId] = 0
	
	RingObj[actId] = RingObj.get(actId, 0) + cnt
	total_times = RingObj[actId]
	if total_times < ProjectActDefine.MIN_RING_TIMES:#次数没达到最小次数要求
		return
	active_reward = set()
	
	ring_times_dict = {}
	if Environment.EnvIsNA():
		ring_times_dict = ProjectActDefine.RING_TIMES_REWARD_NA
	else:
		ring_times_dict = ProjectActDefine.RING_TIMES_REWARD
	
	for deftimes, reward in ring_times_dict.iteritems():
		if total_times >= deftimes:
			active_reward.add(reward)
	#激活奖励
	SetActActive(role, EnumProActType.Ring_Project, active_reward)

#=====星灵相关========
def CheckStarGirlStar(param):
	role, _ = param
	actId = EnumProActType.StarGirl_Project
	if not GetActState(actId):
		return
	
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	max_level = 0
	for _, girlObj in starGirlMgr.girl_dict.iteritems():
		if girlObj.star_level > max_level:
			max_level = girlObj.star_level
	reward = ProjectActDefine.STARGRIL_START_REWARD.get(max_level)
	if not reward: return
	rewardList = [reward]
	#激活奖励
	SetActActive(role, EnumProActType.StarGirl_Project, rewardList)
#===========================================================================================
def SetActActive(role, actId, reward):
	'''
	激活某活动的某些奖励
	@param role:
	@param actId:
	@param reward:
	'''
	cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in SetActActive" % actId
		return
	#激活的数据
	ProjectObj = role.GetObj(EnumObj.ProjectObj)
	#1次性的
	foreverObj = ProjectObj.setdefault(1, {})
	#激活的数据(每日清零的)
	DailyObj = ProjectObj.setdefault(2, {})

	#领取的数据
	GetedObj = role.GetObj(EnumObj.ProjectGetedObj)
	
	active_list = set()
	geted_list = set()
	if cfg.daytick == 1:
		active_list = DailyObj.get(actId, set())
		geted_list = GetedObj.get(2)
	else:
		active_list = foreverObj.get(actId, set())
		geted_list = GetedObj.get(1)

	send_bool = False #是否通知客户端
	for rewardId in reward:
		if rewardId not in cfg.rewardList:#奖励ID不是配置表配置的
			continue
		if rewardId in geted_list:#已领取
			continue
		if rewardId in active_list:#已激活
			continue
		if cfg.daytick:#根据是否清零，记录在不同位置
			if actId not in DailyObj:
				DailyObj[actId] = set()
			DailyObj[actId].add(rewardId) #将奖励ID加入激活中
		else:
			if actId not in foreverObj:
				foreverObj[actId] = set()
			foreverObj[actId].add(rewardId)
		if not send_bool:
			send_bool = True
	if send_bool:
		role.SendObj(ProjectAct_Can_Reward, 1)
		
def GetCanGetID(role):
	'''
	获取玩家可以领取的奖励
	@param role:
	'''
	#获取玩家可以领取的列表和已领取列表
	canObj = role.GetObj(EnumObj.ProjectObj).get(1, {})
	
	getedObj = role.GetObj(EnumObj.ProjectGetedObj)
	#遍历玩家可领取奖励，删除活动结束或已领取的奖励
	for actId, rewardList in canObj.items():
		cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,can not find actId(%s) in GetCanGetID" % actId
			del canObj[actId]
		
		geted_list = set()
		if cfg.daytick:#获取已领取列表
			geted_list = getedObj.get(1, set())
		else:
			geted_list = getedObj.get(2, set())
		
		state = GetActState(actId)
		if not state:#活动已经结束了
			del canObj[actId]
		else:
			for rewardId in rewardList:
				if rewardId in geted_list:#已经领取了，则删除
					rewardList.remove(rewardId)
	#遍历开启的活动，看有没有玩家达要求的活动
	SetActData(role)
	
def SetActData(role):
	'''
	设置玩家可领取字典,遍历边开启的活动
	@param role:
	'''
	global __COSTART_DICT

	#遍历正开启的活动
	for actId, state in __COSTART_DICT.iteritems():
		if not state:#活动结束
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
	cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in ProjectAct.CheckRewardByActId" % actId
		return canList
	rewardList = cfg.rewardList
	#获取已领取列表
	getedObj = role.GetObj(EnumObj.ProjectGetedObj)
	getedList = set()
	if cfg.daytick:
		getedList = getedObj.get(2, set())
	else:
		getedList = getedObj.get(1, set())
	
	for rewardId in rewardList:
		if rewardId in getedList:
			continue
		state = CheckRewardByRewardId(role, actId, rewardId)
		if state:
			canList.append(rewardId)
	return canList

def GetGetedReward(role, actId):
	'''
	获取指定活动已领取的奖励
	@param role:
	@param actId:
	'''
	#玩家已领取列表
	GetedRewards = role.GetObj(EnumObj.ProjectGetedObj)
	cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in ProjectAct" % actId
		return []
	geted_list = set()
	if cfg.daytick:#跟据是否每日清零求不同的数据
		geted_list = GetedRewards.get(2, set())
	else:
		geted_list = GetedRewards.get(1, set())
	getedList = []
	for reward in cfg.rewardList:
		if reward in geted_list:
			getedList.append(reward)
	return getedList

def CheckRewardByRewardId(role, actId, rewardId):
	'''
	检测某个奖励是否能领取
	@param role:
	@param actId:
	@param rewardId:
	'''
	cfg = ProjectActConfig.ACT_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,can not find rewardId(%s) in ProjectAct.CheckRewardByRewardId" % rewardId
		return False
	if cfg.level:
		if role.GetLevel() < cfg.level:#等级不足
			return False
	if cfg.needZDL:
		if role.GetZDL() < cfg.needZDL:#战斗力不足
			return False
	if cfg.oneFlyNum:#翅膀等级，翅膀数
		wlevel, num = cfg.oneFlyNum
		wingDict = role.GetObj(EnumObj.Wing)[1]
		wingList = wingDict.values()
		cnt = 0
		for wing in wingList:
			if wlevel <= wing[0]:
				cnt += 1
		if cnt < num:#该等级的翅膀数量不足
			return False
	if cfg.mountLevel:#坐骑等阶
		evolve = role.GetI16(EnumInt16.MountEvolveID)
		if evolve < cfg.mountLevel:
			return False
	if cfg.PetNum:#宠物星数，宠物个数
		star, num = cfg.PetNum
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
		petDict = petMgr.pet_dict 
		if not petDict:#没宠物
			return False
		petNum = 0
		for pet in petDict.values():
			if pet.star >= star:
				petNum += 1
		if petNum < num:#该等阶的宠物数量不足
			return False
	if cfg.GemNum:#合成宝石等级，个数
		gemLevel, num = cfg.GemNum
		gemData = role.GetObj(EnumObj.ProjectDataObj).get(actId, {})
		if gemData.get(gemLevel, 0) < num:
			return False
	if cfg.mountCulNum:#坐骑神石培养次数
		if role.GetI32(EnumInt32.MountCultivateTimes) < cfg.mountCulNum:
			return False
	if cfg.wishTimes:#许愿次数
		wishobj = role.GetObj(EnumObj.WishPoolWishRecord)
		total_times = 0
		for times in wishobj.values():
			total_times += times
		if total_times < cfg.wishTimes:
			return False
	if cfg.tarotTimes:#高级占卜次数
		grade, times = cfg.tarotTimes
		DataObj = role.GetObj(EnumObj.ProjectDataObj)
		actId = EnumProActType.Tarot_ProAct
		if actId not in DataObj:
			return False
		actData = DataObj.get(actId, {})
		if actData.get(grade) < times:
			return False
	if cfg.wingTimes:#每日羽翼培养次数
		if role.GetI32(EnumInt32.ProjectWingTimes) < cfg.wingTimes:
			return False
	if cfg.FuWenNum:#合成符文等级，个数
		fuwen_level, cnt = cfg.FuWenNum
		fuwenData = role.GetObj(EnumObj.ProjectDataObj).get(actId, {})
		if fuwenData.get(fuwen_level, 0) < cnt:
			return False
	if cfg.PetTimes:#宠物每日培养次数
		PetData = role.GetObj(EnumObj.ProjectDataObj).get(EnumProActType.Pet_Project, 0)
		if PetData < cfg.PetTimes:
			return False
	if cfg.RingTimes:#婚戒每日培养次数
		PetData = role.GetObj(EnumObj.ProjectDataObj).get(EnumProActType.Ring_Project, 0)
		if PetData < cfg.RingTimes:
			return False
	if cfg.StarGirlStar:#星灵星级
		starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
		max_level = 0
		for _, girlObj in starGirlMgr.girl_dict.iteritems():
			if girlObj.star_level > max_level:
				max_level = girlObj.star_level
		if max_level != cfg.StarGirlStar:
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
	with ProjectActReward:
		tips = ""
		tips += GlobalPrompt.Purgatory_Revive_Success
		#物品
		if cfg.rewardItem:
			for item in cfg.rewardItem:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % (item[0], item[1])
		#魔晶
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		#金币
		if cfg.money:
			role.IncMoney(cfg.money)
			tips += GlobalPrompt.Money_Tips % cfg.money
		#命魂
		if cfg.rewardTarot:
			role.AddTarotCard(cfg.rewardTarot, 1)
			tips += GlobalPrompt.Tarot_Tips % (cfg.rewardTarot, 1)
		#英雄
		if cfg.rewardHero:
			role.AddHero(cfg.rewardHero)
			herocfg = HeroConfig.Hero_Base_Config.get(cfg.rewardHero)
			if herocfg:
				name = herocfg.name
				tips += GlobalPrompt.ADD_HERO_MSG % name
		#体力
		if cfg.rewardTiLi:
			role.IncTiLi(cfg.rewardTiLi)
			tips += GlobalPrompt.TiLi_Tips % cfg.rewardTiLi
		#神石
		if cfg.UnbindRMB_S:
			role.IncUnbindRMB_S(cfg.UnbindRMB_S)
			tips += GlobalPrompt.UnBindRMB_Tips % cfg.UnbindRMB_S
		#声望
		if cfg.Reputation:
			role.IncReputation(cfg.Reputation)
			tips += GlobalPrompt.Reputation_Tips % cfg.Reputation
		#命力
		if cfg.TaortHP:
			role.IncI32(EnumInt32.TaortHP, cfg.TaortHP)
			tips += GlobalPrompt.TaortHP_Tips % cfg.TaortHP
		if cfg.TempBless:
			tempBless, keepTime = cfg.TempBless
			starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
			if not starGirlMgr: return
			starGirlMgr.AddTempBless(tempBless, keepTime)
			tips += GlobalPrompt.AddTemp_Bless % tempBless
			
		name = "actId = %d" % actId
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveProjectActReward, name)

	role.CallBackFunction(backId, [actId, cfg.rewardId])
	#重新获取可以领取的活动ID
	proObj = role.GetObj(EnumObj.ProjectObj)
	sendList = []
	canDict = proObj.get(1)
	if canDict:
		sendList += canDict.keys()
	daycanDict = proObj.get(2)
	if daycanDict:
		sendList += daycanDict.keys()
	role.SendObj(ProjectAct_Can_Reward_Dict, sendList)
	role.Msg(2, 0, tips)

#==============================公用的打开和获取=============================
def OpenPublicAct(param):
	'''
	打开面板，公用函数
	@param param:
	'''
	role, cfg = param
	actId = cfg.actId
	#已领取
	GetedRewards = GetGetedReward(role, actId)
	#可领取
	CanList = set()
	if cfg.daytick:
		dailyObj = role.GetObj(EnumObj.ProjectObj).get(2, {})
		if dailyObj:
			CanList = dailyObj.get(actId, set())
	else:
		foreverObj = role.GetObj(EnumObj.ProjectObj).get(1, {})
		if foreverObj:
			CanList = foreverObj.get(actId, set())
	sendData = role.GetObj(EnumObj.ProjectDataObj).get(actId, {})
	role.SendObj(ProjectAct_Open_Panel_Data, [actId, GetedRewards, CanList, sendData])

def GetPublicAct(param):
	'''
	获取奖励，公用函数
	@param param:
	'''
	#获取奖励时只检测是否激活该奖励和活动是否开启，不做条件检测
	role, actId, rewardId, daytick, backId = param
	if not GetActState(actId):#活动未开启
		return
	
	cfg = ProjectActConfig.ACT_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,ProjectAct can not find rewardId(%s) in cfg" % rewardId
		return
	#已领取相关数据
	getedObj = role.GetObj(EnumObj.ProjectGetedObj)
	getedList = set()
	
	proObj = role.GetObj(EnumObj.ProjectObj)
	if daytick == 1:
		dailyObj = proObj.get(2)
		if rewardId not in dailyObj.get(actId, set()):#可领取奖励里没有该奖励
			return
		dailyObj[actId].remove(rewardId)#存在的话就移除该奖励
		if dailyObj[actId] == set():
			del dailyObj[actId]
		getedList = getedObj.get(2, set())
	else:
		foreverObj = proObj.get(1)
		if rewardId not in foreverObj.get(actId, set()):#可领取奖励里没有该奖励
			return
		foreverObj[actId].remove(rewardId)#存在的话就移除该奖励
		if foreverObj[actId] == set():
			del foreverObj[actId]
		getedList = getedObj.get(1, set())
	#加入已领取列表
	getedList.add(rewardId)
	GetReward(role, cfg, actId, backId)
#==============================打开================================
def LoadOpenFunByType():
	global ProActOpenFun_Dict
	ProActOpenFun_Dict[EnumProActType.Mount_ProAct_1]  	 = OpenPublicAct	#坐骑专题1
	ProActOpenFun_Dict[EnumProActType.Mount_ProAct_2]  	 = OpenPublicAct	#坐骑专题2
	ProActOpenFun_Dict[EnumProActType.Mount_ProAct_3]  	 = OpenPublicAct	#坐骑专题3
	ProActOpenFun_Dict[EnumProActType.Mount_ProAct_4]  	 = OpenPublicAct	#坐骑专题4
	ProActOpenFun_Dict[EnumProActType.Mount_ProAct_5]  	 = OpenPublicAct	#坐骑专题5
	ProActOpenFun_Dict[EnumProActType.Mount_ProAct_6]  	 = OpenPublicAct	#坐骑专题6
	ProActOpenFun_Dict[EnumProActType.Gem_ProAct_1]  	 = OpenPublicAct	#宝石专题1
	ProActOpenFun_Dict[EnumProActType.Wish_ProAct]  	 = OpenPublicAct	#许愿池专题
	ProActOpenFun_Dict[EnumProActType.Tarot_ProAct]  	 = OpenPublicAct	#高级占卜专题
	ProActOpenFun_Dict[EnumProActType.Wing_ProAct]  	 = OpenPublicAct	#羽翼专题
	ProActOpenFun_Dict[EnumProActType.FuWen_ProAct]  	 = OpenPublicAct	#符文专题
	ProActOpenFun_Dict[EnumProActType.Pet_Project]    	 = OpenPublicAct	#宠物专题
	ProActOpenFun_Dict[EnumProActType.Ring_Project]    	 = OpenPublicAct	#婚戒专题
	ProActOpenFun_Dict[EnumProActType.StarGirl_Project]	 = OpenPublicAct	#星灵专题
	
def GetOpenFunByType(Etype, param):
	global ProActOpenFun_Dict
	fun = ProActOpenFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, ProjectAct Etype(%s) not in ProActOpenFun_Dict" % Etype
		return
	fun(param)
#==============================获取================================
def LoadGetFunByType():
	global ProActGetFun_Dict
	ProActGetFun_Dict[EnumProActType.Mount_ProAct_1]  	 = GetPublicAct		#坐骑专题1
	ProActGetFun_Dict[EnumProActType.Mount_ProAct_2]  	 = GetPublicAct		#坐骑专题2
	ProActGetFun_Dict[EnumProActType.Mount_ProAct_3]  	 = GetPublicAct		#坐骑专题3
	ProActGetFun_Dict[EnumProActType.Mount_ProAct_4]  	 = GetPublicAct		#坐骑专题4
	ProActGetFun_Dict[EnumProActType.Mount_ProAct_5]  	 = GetPublicAct		#坐骑专题5
	ProActGetFun_Dict[EnumProActType.Mount_ProAct_6]  	 = GetPublicAct		#坐骑专题6
	ProActGetFun_Dict[EnumProActType.Gem_ProAct_1]  	 = GetPublicAct		#宝石专题1
	ProActGetFun_Dict[EnumProActType.Wish_ProAct]   	 = GetPublicAct		#中秋专题：许愿
	ProActGetFun_Dict[EnumProActType.Tarot_ProAct]   	 = GetPublicAct		#中秋专题：高级占卜
	ProActGetFun_Dict[EnumProActType.Wing_ProAct]    	 = GetPublicAct		#羽翼专题
	ProActGetFun_Dict[EnumProActType.FuWen_ProAct]    	 = GetPublicAct		#符文专题
	ProActGetFun_Dict[EnumProActType.Pet_Project]    	 = GetPublicAct		#宠物专题
	ProActGetFun_Dict[EnumProActType.Ring_Project]    	 = GetPublicAct		#婚戒专题
	ProActGetFun_Dict[EnumProActType.StarGirl_Project]	 = GetPublicAct		#星灵专题
	
def GetGetFunByType(Etype, param):
	global ProActGetFun_Dict
	fun = ProActGetFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, ProjectAct Etype(%s) not in ProActGetFun_Dict" % Etype
		return
	fun(param)
#============================玩家事件============================
def AfterLogin(role, param):
	#玩家登陆之后
	#老数据修改
	if role.GetObj(EnumObj.ProjectGetedObj) == {}:
		role.SetObj(EnumObj.ProjectGetedObj, {1:set(), 2:set()})
	if role.GetObj(EnumObj.ProjectObj) == {}:
		role.SetObj(EnumObj.ProjectObj, {1:{}, 2:{}})
	#重新获取次玩家可以领取的奖励
	GetCanGetID(role)

def SyncRoleOtherData(role, param):
	proObj = role.GetObj(EnumObj.ProjectObj)
	if proObj.get(1) or proObj.get(2):
		role.SendObj(ProjectAct_Can_Reward, 1)
		
def RoleDayClear(role, param):
	#玩家每日清零
	
	#清理些需要每日清理的数据
	role.SetI32(EnumInt32.MountCultivateTimes, 0)#清理神石培养次数
	#清理每日许愿次数
	role.SetI32(EnumInt32.ProjectWishTimes, 0)
	#清理每日羽翼培养次数
	role.SetI32(EnumInt32.ProjectWingTimes, 0)
	#清理激活的每日需要清理的奖励
	if role.GetObj(EnumObj.ProjectObj) == {}:
		role.SetObj(EnumObj.ProjectObj, {1:{}, 2:{}})
	proObj = role.GetObj(EnumObj.ProjectObj)
	proObj[2] = {}	#清空
	#清理需要每日清零的已领取奖励
	if role.GetObj(EnumObj.ProjectGetedObj) == {}:
		role.SetObj(EnumObj.ProjectGetedObj, {1:set(), 2:set()})
	GetedObj = role.GetObj(EnumObj.ProjectGetedObj)
	GetedObj[2] = set()	#清空
	#清零各种记录数据
	role.SetObj(EnumObj.ProjectDataObj, {})
	
	if EnumProActType.StarGirl_Project not in __COSTART_DICT:
		stargirl_list = ProjectActDefine.STARGRIL_START_REWARD_REMOVE.values()
		new_list = set()
		for rid in GetedObj.get(1):
			if rid not in stargirl_list:
				new_list.add(rid)
		GetedObj[1] = new_list
	#需要检测是否有新活动开启了，需要重新获取一次玩家可以领取的奖励
	#但玩家数据清理会在Event.Eve_StartCircularActive 事件触发前执行，所以定了个1分钟的Tick
	role.RegTick(30, TickGetCanGetID, None)

def TickGetCanGetID(role, callargv, regparam):
	#重新获取次玩家可以领取的奖励
	GetCanGetID(role)
	
def AfterChangeMountEvole(role, param):
	#坐骑培养升星事件
	for actId in EnumProActType.MOUNT_ACT_LIST1:#遍历按阶数领奖的活动
		if GetActState(actId):
			CheckMountEvalAct(role, actId)
		
def CheckMountEvalAct(role, actId):
	'''
	这里处理玩家激活的坐骑奖励，并通知玩家
	@param role:
	@param actId:
	'''
	#坐骑的阶数
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	active_reward = [] #可激活的奖励
	cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC, can not find actid(%s) in CheckMountEvalAct" % actId
		return
	#由于高级培养，可能导致玩家一次进阶几星，所以需要大于或等于
	for level, rewardId in ProjectActDefine.MOUNT_EVOLE_DICT.iteritems():
		#达到要求
		if level <= evolveId and rewardId in cfg.rewardList:
			active_reward.append(rewardId)
	if not active_reward:
		return

	SetActActive(role, actId, active_reward)
#============================客户端操作===========================
def RequestOpenPanel(role, param):
	'''
	客户端请求打开精彩活动界面
	@param role:
	@param param:
	'''
	proObj = role.GetObj(EnumObj.ProjectObj)
	sendList = []
	canDict = proObj.get(1)#激活的一次性活动ID
	if canDict:
		sendList += canDict.keys()
	daycanDict = proObj.get(2)#每日清零的活动ID
	if daycanDict:
		sendList += daycanDict.keys()
	role.SendObj(ProjectAct_Can_Reward_Dict, sendList)
		
def RequestOpenAct(role, param):
	'''
	客户端请求打开某个活动
	@param role:
	@param param:
	'''
	actId = param
	if not actId:
		return
	cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,ProjectAct OpenAct can not find actId(%s)" % actId
		return
	GetOpenFunByType(actId, (role, cfg))
	
def RequestGetReward(role, param):
	'''
	客户端请求获取奖励
	@param role:
	@param param:
	'''
	backId, (actId, rewardId) = param
	cfg = ProjectActConfig.ACT_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,ProjectAct can not find actId(%s) in ACT_BASE_DICT" % actId
		return
	state = GetActState(actId)
	if not state:#活动未开启
		return
	if rewardId not in cfg.rewardList:#该活动不存在该奖励ID
		print "GE_EXC,ProjectAct GetReward but rewardId(%s) not in rewardList" % rewardId
		return
	if cfg.daytick == 1:
		if rewardId in role.GetObj(EnumObj.ProjectGetedObj).get(2, set()):#奖励已领取
			return
	else:
		if rewardId in role.GetObj(EnumObj.ProjectGetedObj).get(1, set()):#奖励已领取
			return
	GetGetFunByType(actId, (role, actId, rewardId, cfg.daytick, backId))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGetFunByType()
		LoadOpenFunByType()
		SetWonderIncFun()
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_AfterMountEvolve, AfterChangeMountEvole)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ProjectAct_Open_Act_Panel", "客户端请求打开专属活动界面"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ProjectAct_Open_Act", "客户端请求打开某个专属活动"), RequestOpenAct)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ProjectAct_Get_Reward", "客户端请求获取专属活动奖励"), RequestGetReward)
		
