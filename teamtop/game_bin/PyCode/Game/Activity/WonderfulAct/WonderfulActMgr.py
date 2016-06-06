#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WonderfulAct.WonderfulActMgr")
#===============================================================================
# 精彩活动
#===============================================================================
import datetime
import Environment
import cComplexServer
import cDateTime
import cRoleMgr
import cProcess
from Util import Time
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumSysData, EnumGameConfig
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.BallFame import BallFame
from Game.Activity.CarnivalOfTopup import COTMgr
from Game.Activity.GoldChest import GoldChest
from Game.Activity.WonderfulAct import WonderfulActConfig, EnumWonderType,\
	WonderfulData
from Game.Activity.WonderfulAct import WonderfulActDefine as wad
from Game.Hero import HeroConfig
from Game.Role import Event, RoleMgr
from Game.Role.Data import EnumObj, EnumInt16, EnumTempObj, EnumInt32, EnumInt8, EnumInt1
from Game.Role.Mail import Mail
from Game.RoleFightData import RoleFightData
from Game.SysData import WorldData
from Game.SystemRank import SystemRank
from Game.Union import UnionMgr, UnionDefine
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	WONDEFUL_INDEX_1 = 1	#存储历来需要记录奖励领取数的奖励
	WONDEFUL_INDEX_2 = 2	#记录首冲人数	
	WONDEFUL_INDEX_3 = 3	#记录购买月卡人数
	WONDEFUL_INDEX_4 = 4	#记录全服4-7级vip的人数（目前只在活动期间记录）
	WONDEFUL_INDEX_5 = 5	#记录指定的橙色英雄数 （目前只在活动期间记录）
	WONDEFUL_INDEX_6 = 6	#记录商城购买宝石数
	WONDEFUL_INDEX_7 = 7	#记录高级占卜数
	WONDEFUL_INDEX_8 = 8	#首战竞技，再战竞技记录
	WONDEFUL_INDEX_9 = 9	#圣城争霸
	WONDEFUL_INDEX_10 = 10	#坐骑争霸活动
	WONDEFUL_INDEX_11 = 11	#记录当前激活的奖励ID（有时限）
	WONDEFUL_INDEX_12 = 12	#记录一些可以领取几次的奖励ID
	WONDEFUL_INDEX_13 = 13	#工会竞赛
	WONDEFUL_INDEX_14 = 14	#战力绝伦(这个活动已经被七日目标活动取代，具体参见七日目标时间控制的代码)
	WONDEFUL_INDEX_15 = 15	#记录全服8-10级vip的人数（目前只在活动期间记录）
	WONDEFUL_INDEX_16 = 16	#记录全服坐骑进阶人数（2阶以上，目前只在活动期间记录）
	WONDEFUL_INDEX_17 = 17	#记录全服工会每日夺宝树（活动期间）
	WONDEFUL_INDEX_18 = 18	#记录全服每日累计消费
	WONDEFUL_INDEX_19 = 19	#记录荣誉之战数据
	WONDEFUL_INDEX_20 = 20	#记录情比金坚数据
	WONDEFUL_INDEX_21 = 21	#记录充值狂人
	WONDEFUL_INDEX_22 = 22	#公会争霸
	WONDEFUL_INDEX_23 = 23	#战力排行
	WONDEFUL_INDEX_24 = 24	#记录全服翅膀培养次数
	WONDEFUL_INDEX_25 = 25	#记录全服宠物培养次数
	WONDEFUL_INDEX_26 = 26	#记录全服宠物修行次数
	WONDEFUL_INDEX_27 = 27	#记录全服时装升星消耗的时装精华
	WONDEFUL_INDEX_28 = 28	#记录全服时装升阶消耗的时装之魄
	WONDEFUL_INDEX_29 = 29	#记录全服星灵升级消耗
	WONDEFUL_INDEX_30 = 30	#记录全服星灵升星消耗
	WONDEFUL_INDEX_31 = 31	#记录全服龙脉升级消耗
	WONDEFUL_INDEX_32 = 32	#记录全服龙脉进化消耗
	WONDEFUL_INDEX_33 = 33	#记录全服称号升级消耗
	WONDERFUL_RIGHT_ACT = {}	#缓存当日开启的活动
	WONDERFUL_ROLE_CAN_REWARD = {}	#缓存玩家可领取的活动奖励
	
	IS_OPERATION = False	#合服事件是否在数据载入前调用
	
	HALLOWS_IS_START = False	#充值送圣器开启标志
	#消息
	Wonder_Can_Reward = AutoMessage.AllotMessage("Wonder_Can_Reward", "通知客户端精彩活动有奖励可以领取")
	Wonder_Can_Reward_Dict = AutoMessage.AllotMessage("Wonder_Can_Reward_Dict", "通知客户端所有可以领取的活动奖励")
	Wonder_Open_Panel_Data = AutoMessage.AllotMessage("Wonder_Open_Panel_Data", "打开某个活动需要发送的数据")
	Wonder_Send_Process = AutoMessage.AllotMessage("Wonder_Send_Process", "发送玩家服务器Id")
	#日志
	WonderfulActReward = AutoLog.AutoTransaction("WonderfulActReward", "精彩活动领奖")
	WonderfulActJJC = AutoLog.AutoTransaction("WonderfulActJJC", "精彩活动竞技场数据")
	WonderfulDuke = AutoLog.AutoTransaction("WonderfulDuke", "精彩活动竞圣城争霸数据")
	WonderfulGlory = AutoLog.AutoTransaction("WonderfulGlory", "精彩活动荣耀之战数据")
	WonderfulZDL = AutoLog.AutoTransaction("WonderfulZDL", "精彩活动战力绝伦数据")
	WonderfulUnion = AutoLog.AutoTransaction("WonderfulUnion", "精彩活动公会竞赛数据")
	WonderfulMount = AutoLog.AutoTransaction("WonderfulMount", "精彩活动坐骑争霸数据")
	WonderfulClear = AutoLog.AutoTransaction("WonderfulClear", "修改开服时间精彩活动数据清空")
	WonderfulDisAct = AutoLog.AutoTransaction("WonderfulDisAct", "精彩活动清除已消失的活动")
	WonderfulRing = AutoLog.AutoTransaction("WonderfulRing", "精彩活动婚戒排行数据")
	WonderfulZDLRank = AutoLog.AutoTransaction("WonderfulZDLRank", "精彩活动战力排行")
	WonderfulHefu = AutoLog.AutoTransaction("WonderfulHefu", "精彩活动合服数据修正")
	WonderIncFun_Dict = {}
	WonderOpenFun_Dict = {}
	WonderGetFun_Dict = {}
	WonderSettlementFun_Dict = {}
#===============================================================================
def SetWonderIncFun():
	global WonderIncFun_Dict
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Fill] = IncFillNum		#增加首冲数
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Card] = IncMCardNum	#增加购买月卡人数
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_VIP] = IncVIPNum		#增加VIP人数
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Hero] = IncHeroNum		#增加全服橙色英雄人数
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Gem] = IncGemNum		#增加商城购买宝石数
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Tarot] = IncTarotNum 	#增加高级占卜数
	WonderIncFun_Dict[EnumWonderType.Wonder_Set_JJC] = SetJJCData		#记录首站和再战竞技场
	WonderIncFun_Dict[EnumWonderType.Wonder_Set_Duke] = SetDukeData	#城主轮值相关活动
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Equip] = IncEquipNum	#获取装备
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_ZDL] = ChangeZDL		#玩家战斗力改变
	WonderIncFun_Dict[EnumWonderType.Wonder_Change_Wing] = ChangeWing	#玩家活动翅膀或改变翅膀等级
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_UnionTreasure] = IncUnionTre	#全服增加工会夺宝数
	WonderIncFun_Dict[EnumWonderType.Wonder_Inc_Pet] = IncPetStarNum	#玩家宠物星级改变
	WonderIncFun_Dict[EnumWonderType.Wonder_Set_GloryWar] = SetGloryWar	#荣耀之战
	WonderIncFun_Dict[EnumWonderType.Wonder_Wed_Ring] = ChangeWedRing	#婚戒升阶
	WonderIncFun_Dict[EnumWonderType.Wonder_Wing_Times] = IncWingTimes	#增加个人和全服翅膀培养数
	WonderIncFun_Dict[EnumWonderType.Wonder_Pet_Times] = IncPetTimes	#增加个人和全服宠物培养数
	WonderIncFun_Dict[EnumWonderType.Wonder_UnionFeed] = UnionFeed		#公会神兽喂养
	WonderIncFun_Dict[EnumWonderType.Wonder_UnionGod] = UnionGods		#公会魔神
	WonderIncFun_Dict[EnumWonderType.Wonder_UnionTotalFill] = UnionTotalFill#公会累计充值
	WonderIncFun_Dict[EnumWonderType.Wonder_PetEvo] = PetEvo			#宠物修行
	WonderIncFun_Dict[EnumWonderType.Wonder_FashionUpStar] = FashionUpStar#时装升星
	WonderIncFun_Dict[EnumWonderType.Wonder_FashionUpOrder] = FashionUpOrder#时装升价
	WonderIncFun_Dict[EnumWonderType.Wonder_StarGirlLevelUp] = StarGirlLevelUp#星灵升级
	WonderIncFun_Dict[EnumWonderType.Wonder_StarGirlStar] = StarGirlStar#星灵升星
	WonderIncFun_Dict[EnumWonderType.Wonder_DragonVeinLevel] = DragonVeinLevel#龙脉升级
	WonderIncFun_Dict[EnumWonderType.Wonder_DragonVeinEvo] = DragonVeinEvo#龙脉升级
	WonderIncFun_Dict[EnumWonderType.Wonder_Act_TitleLevel] = TitleLevel	#称号升级
	
	
def GetFunByType(Etype, param = None):
	fun = WonderIncFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, GetFunByType error Etype(%s)" % Etype
		return
	fun(param)
	

#==============================各种接口===============================
def IncPetTimes(param):
	#增加个人和全服的宠物培养次数
	role, times = param
	Pet_ActId = EnumWonderType.Wonder_Act_CulPet
	if GetActState(Pet_ActId) == 1:#宠物培养，个人培养数，每日清零
		role.IncI32(EnumInt32.PetCultivateTimes, times)
		#检查玩家是否达成条件
		roleTimes = role.GetI32(EnumInt32.PetCultivateTimes)
		reward_List = [] #保存达到条件的奖励ID
		for totimes, rewardId in wad.CULPET_REWARD_DICT.iteritems():
			if totimes <= roleTimes:
				reward_List.append(rewardId)
		if not reward_List:
			return
		#将奖励加入激活字典
		SetActIdR(Pet_ActId, reward_List)
		for reward in reward_List:#检查奖励，可以领取的话通知玩家领奖
			if CheckReward(role, Pet_ActId, reward):
				break
	##宠物培养，全服，每日清零
	TogPet_Actid = EnumWonderType.Wonder_Act_TogPet
	if GetActState(TogPet_Actid) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_25)
		if TogPet_Actid not in WAData:
			WAData[TogPet_Actid] = 0
		WAData[TogPet_Actid] = WAData.get(TogPet_Actid, 0) + times #增加全服宠物培养次数
	
		Total_Times = WAData.get(TogPet_Actid)
		reward_list = []#保存达到条件的奖励ID
		for totalTimes, reward in wad.TOGPET_REWARD_DICT.iteritems():
			if totalTimes <= Total_Times:
				reward_list.append(reward)
		if not reward_list:
			return
		#将奖励加入激活字典
		SetActIdR(TogPet_Actid, reward_list)
		for role in cRoleMgr.GetAllRole():#通知在线的达要求的玩家领奖
			CheckReward(role, TogPet_Actid, reward)

def IncWingTimes(param):
	#增加个人和全服的培养翅膀次数
	role, times = param
	Wing_ActId = EnumWonderType.Wonder_Act_CulWing
	if GetActState(Wing_ActId) == 1:#天天爱飞翔，个人培养数，每日清零
		role.IncI32(EnumInt32.WingCultivateTimes, times)
		#检查玩家是否达成条件
		roleTimes = role.GetI32(EnumInt32.WingCultivateTimes)
		reward_List = [] #保存达到条件的奖励ID
		for totimes, rewardId in wad.CULWING_REWARD_DICT.iteritems():
			if totimes <= roleTimes:
				reward_List.append(rewardId)
		if not reward_List:
			return
		#将奖励加入激活字典
		SetActIdR(Wing_ActId, reward_List)
		for reward in reward_List:#检查奖励，可以领取的话通知玩家领奖
			if CheckReward(role, Wing_ActId, reward):
				break
	#大家一起飞，全服，每日清零
	TogWing_Actid = EnumWonderType.Wonder_Act_TogWing
	if GetActState(TogWing_Actid) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_24)
		if TogWing_Actid not in WAData:
			WAData[TogWing_Actid] = 0
		WAData[TogWing_Actid] = WAData.get(TogWing_Actid, 0) + times #增加全服翅膀培养次数
	
		Total_Times = WAData.get(TogWing_Actid)
		reward_list = []#保存达到条件的奖励ID
		for totalTimes, reward in wad.TOGWING_REWARD_DICT.iteritems():
			if totalTimes <= Total_Times:
				reward_list.append(reward)
		if not reward_list:
			return
		#将奖励加入激活字典
		SetActIdR(TogWing_Actid, reward_list)
		for role in cRoleMgr.GetAllRole():#通知在线的达要求的玩家领奖
			CheckReward(role, Wing_ActId, reward)

def ChangeWedRing(param):
	'''
	婚戒品阶改变
	@param param:
	'''
	role = param
	state = GetActState(EnumWonderType.Wonder_Act_MarryRing)
	if state != 1:
		return
	SetActIdR(EnumWonderType.Wonder_Act_MarryRing, wad.MARRY_REWARD_DICT.get(5))
	CheckReward(role, EnumWonderType.Wonder_Act_MarryRing, wad.MARRY_REWARD_DICT.get(5))

def SetGloryWar(param):
	'''
	设置荣耀之战数据
	@param param:
	'''
	state = GetActState(EnumWonderType.Wonder_Act_GloryWar)
	if state != 1:#活动未开启
		return
	
	Data = WonderfulData.GetWAData(WONDEFUL_INDEX_19)
	if Data is None or len(Data) >= 3:#数据出错
		return

	roleId = 0
	if param:
		roleId = param[0]
	with WonderfulGlory:
		if roleId:#有玩家获得荣耀第一
			role = cRoleMgr.FindRoleByRoleID(roleId)
			sex, career, grade = 0, 0, 0
			if role:
				name = role.GetRoleName()
				sex, career, grade = role.GetPortrait()
			else:
				roleData = RoleFightData.GetRoleFightData(roleId)[0]
				sex, career, grade, name = roleData.get(6), roleData.get(7), roleData.get(8), roleData.get(3)
			Data.append([roleId, sex, career, grade, name])
		else:#没玩家活动，即该活动未激活
			Data.append([0])
		if roleId:
			AutoLog.LogBase(roleId, AutoLog.eveWonderGloryWar, (Data, cDateTime.Now()))
		else:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderGloryWar, (Data, cDateTime.Now()))
	roleId = CheckGlory(Data)
	if roleId:#有玩家胜利的场数大于1
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(EnumWonderType.Wonder_Act_GloryWar)
		SetActIdR(EnumWonderType.Wonder_Act_GloryWar, cfg.rewardList)			
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if role:
			role.SendObj(Wonder_Can_Reward, 1)

def CheckGlory(GloryData):
	'''
	获取可以领奖的玩家Id,不存在返回0
	'''
	if GloryData is None or len(GloryData) < 2: return 0
	roleIdCnt = {}
	for roleData in GloryData:
		roleId = roleData[0]
		if not roleId:
			continue
		roleIdCnt[roleId] = roleIdCnt.get(roleId, 0) + 1
		if roleIdCnt[roleId] >= 2:
			#只要次数大于等于2，就可以领奖
			return roleId
	return 0
##############################################################################


def IncPetStarNum(role):
	'''
	玩家宠物星级改变
	@param param:
	'''
	actId = EnumWonderType.Wonder_Act_Pet
	state = GetActState(actId)
	if state != 1:#活动未开启返回
		return
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	if not petMgr.pet_dict:#玩家没宠物
		return
	StarNum = {}
	SG = StarNum.get
	for pet in petMgr.pet_dict.itervalues():#获取玩家不同星级宠物的数量，是一个字典{star:NUM}
		for star in xrange(1, pet.star + 1):
			StarNum[star] = SG(star, 0) + 1

	petRewadList = []
	PA = petRewadList.append
	RewardCfg = wad.WONDER_PET_REWARD
	for petstar, num in StarNum.iteritems():
		starCfg = RewardCfg.get(petstar)
		if not starCfg:
			continue
		for snum, rewardId in starCfg.iteritems():
			if snum <= num:
				PA(rewardId)
	if not petRewadList:#没有达要求的奖励
		return
	SetActIdR(actId, petRewadList)
	for rewardId in petRewadList:
		if CheckReward(role, actId, rewardId):
			return

def IncUnionTre(boxType):
	'''
	增加每日全服工会夺宝数
	@param param:
	'''
	if not boxType:
		return
	UT_ActId = 0
	for actId in EnumWonderType.WonderActUTreasureList:#遍历看是否有开启的活动
		if 1 == GetActState(actId):
			UT_ActId = actId
			break
	if not UT_ActId : return
	
	waData = WonderfulData.GetWAData(WONDEFUL_INDEX_17)
	if waData is None:
		return
	waData[boxType] = waData.get(boxType, 0) + 1	#根据宝箱类型，增加该宝箱的开启数
	Num = waData.get(boxType)
	unionTr = wad.WONDER_UNION_TREASURE.get(UT_ActId)
	defineList = unionTr.get(boxType)
	if not defineList:
		return
	if Num < defineList[0]:#开启的宝箱数量不足
		return
	rewardId = defineList[1]
	SetActIdR(UT_ActId, rewardId)
	for role in cRoleMgr.GetAllRole():
		CheckReward(role, UT_ActId, rewardId)
		
def ChangeWing(param):
	'''
	玩家翅膀升级或增加
	@param param:
	'''
	role, mark, level = param #mark为1是增加翅膀，0为培养翅膀
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj = roleObj[1]
	wingDict = role.GetObj(EnumObj.Wing)[1]

	WingNum = len(wingDict)
	if WingNum <= 3:
		return

	#活动2
	if 1 == GetActState(EnumWonderType.Wonder_Act_WingLevel):
		LevelDict = {}
		for wLevel in wingDict.values():
			realLevel = wLevel[0]
			for Dlevel in xrange(1, realLevel + 1):#获取玩家翅膀等级对应数量的字典
				LevelDict[Dlevel] = LevelDict.get(Dlevel, 0) + 1
		#获取达到要求的奖励
		rewardList = []
		WWR_Get = wad.WONDER_WING_CNT_REWARDS.get
		for level, cnt in LevelDict.iteritems():
			if cnt >= 4:
				rewardList.append(WWR_Get(4).get(level))
			if cnt >= 8:
				rewardList.append(WWR_Get(8).get(level))
		if rewardList:
			for reward in rewardList:
				if reward not in wonderObj:
					role.SendObj(Wonder_Can_Reward, 1)
					break
	
	if not mark:
		return
	#活动1
	if 1 == GetActState(EnumWonderType.Wonder_Act_Wing):
		rewardId = wad.WONDER_WING_REWARD
		if rewardId not in wonderObj:
			if CanGetReward(role, rewardId):
				role.SendObj(Wonder_Can_Reward, 1)
	
	#活动3
	if 1 == GetActState(EnumWonderType.Wonder_Act_WingBack):
		wrewardList = []
		for num, rewardId in wad.WONDER_WING_BACK_REWARD.iteritems():
			if num <= WingNum:
				wrewardList.append(rewardId)
		if not wrewardList:
			return
		for reward in wrewardList:
			cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(reward)
			if not cfg or not cfg.MallWing:
				print "GE_EXC, error in ChangeWing Wonder_Act_WingBack (%s)" % reward
				return
			wNum, WIds = cfg.MallWing
			cnt = 0
			for wid in wingDict.iterkeys():
				if wid in WIds:
					cnt += 1
			if cnt < wNum:
				continue
			role.SendObj(Wonder_Can_Reward, 1)
			return

def ChangeZDL(role):
	'''
	玩家战斗力改变
	@param param:
	'''
	
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj = roleObj[1]
	if GetActState(EnumWonderType.Wonder_Act_Union) == 1:
		if wad.WONDER_UNION_REWARD3 not in wonderObj:
			cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(wad.WONDER_UNION_REWARD3)
			if not cfg:
				print "GE_EXC, ChangeZDL error cfg"
				return
			if role.GetZDL() >= cfg.needZDL:
				SetActIdR(EnumWonderType.Wonder_Act_Union, wad.WONDER_UNION_REWARD3)
				role.SendObj(Wonder_Can_Reward, 1)
	
	if not WorldData.WD.returnDB:
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	
	from Game.Activity.KaifuTarget import TimeControl
	if GetActState(EnumWonderType.Wonder_Act_ZDL) == 1 and TimeControl.KaifuTargetTime_New < kaifuTime:
		if wad.WONDER_ZDL_REWARD3 not in wonderObj:
			cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(wad.WONDER_ZDL_REWARD3)
			if not cfg:
				print "GE_EXC, ChangeZDL error cfg 2"
				return
			if role.GetZDL() >= cfg.needZDL:
				SetActIdR(EnumWonderType.Wonder_Act_ZDL, wad.WONDER_ZDL_REWARD3)
				role.SendObj(Wonder_Can_Reward, 1)
	

def IncEquipNum(param):
	'''
	获取装备
	@param param:
	'''
	role, coding = param
	suitId = 0
	for suit, IdList in wad.EQUIPMENT_SUIT_DICT.iteritems():
		if coding in IdList:
			suitId = suit
	if not suitId:
		return
	suitNum = CheckEquip(role, suitId, coding)
	if not suitNum:
		return
	rewardList = []
	SuitNumR = wad.EQUIPMENT_SUIT_MAP_REWARD.get(suitId)#{1:128,2:129,3:130}
	for num, rewardId in SuitNumR.iteritems():
		if num <= suitNum:
			rewardList.append(rewardId)

	if coding in wad.SAME_SUIT_LIST3:
		suitNum2 = CheckEquip(role, 3, coding)
		if suitNum2:
			SuitNumR2 = wad.EQUIPMENT_SUIT_MAP_REWARD.get(3)
			for num, rewardId in SuitNumR2.iteritems():
				if num <= suitNum2:
					rewardList.append(rewardId)
	if not rewardList:
		return
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj = roleObj[1]
	for reward in rewardList:
		if reward not in wonderObj:
			role.SendObj(Wonder_Can_Reward, 1)
			return

def CheckEquip(role, suitId, coding = 0):
	#检查装备数量是否足够,返回最少装备数
	eid_list = []
	if 3 == suitId:
		eid_list = wad.SAME_SUIT_LIST3
	else:	
		eid_list = wad.EQUIPMENT_SUIT_DICT.get(suitId)
	if not eid_list:
		print "GE_EXC, CheckEquip suitId (%s)" % suitId
		return
	eid_dict = dict((i, 0)for i in eid_list)
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	for _, item in globaldict.iteritems():
		rcoding = item.cfg.coding
		if rcoding in eid_dict:
			eid_dict[rcoding] += 1
	if coding:
		if coding in eid_dict:
			eid_dict[coding] += 1
	samesuitDict = {}
	if suitId == 1 or suitId == 2:
		same_suit_list = wad.SAME_SUIT_LIST[suitId]
		for eid, cnt in eid_dict.iteritems():
			for idList in same_suit_list:
				if eid in idList:
					samesuitDict[idList[0]] = samesuitDict.get(idList[0], 0) + cnt
	elif suitId == 3:
		samesuitDict = eid_dict
	num_List = samesuitDict.values()
	num_List.sort()
	suitNum = num_List[0]
	return suitNum

def SetDukeData(param = None):
	'''
	城主轮值相关活动
	'''
	unionObj = param
	#圣城争霸活动
	state = GetActState(EnumWonderType.Wonder_Act_Duke)
	if state == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_9)
	
		if len(WAData) >= 3:
			return
		with WonderfulDuke:
			if not unionObj:
				WAData.append([0])
			else:
				unionId = unionObj.union_id
				unionName = unionObj.name
				leaderId = unionObj.leader_id
				leader = cRoleMgr.FindRoleByRoleID(leaderId)
				if leader:
					name = leader.GetRoleName()
					sex, career, grade = leader.GetPortrait()
				else:
					fightData = RoleFightData.GetRoleFightData(leaderId)
					sex, career, grade, name = fightData[0].get(6), fightData[0].get(7), fightData[0].get(8), fightData[0].get(3)
				now = cDateTime.Now()
				unixTime = Time.DateTime2UnitTime(now)
				WAData.append([unionId, unionName, name, sex, career, grade, unixTime, leaderId])
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderDuke, (WAData, cDateTime.Now()))
		if len(WAData) >= 3:#记录满
			unionList = []
			unionList.extend(WAData)
			unionList.sort(key = lambda x:x[0])
			selectUnion = 0
			if unionList[0][0] == unionList[1][0]:
				selectUnion = unionList[0][0]
			elif unionList[1][0] == unionList[2][0]:
				selectUnion = unionList[1][0]
			if not selectUnion:
				return
			union = UnionMgr.GetUnionObjByID(selectUnion)
			if not union:
				return
			for roleId, _ in union.members.iteritems():
				role = cRoleMgr.FindRoleByRoleID(roleId)
				if not role:
					continue
				role.SendObj(Wonder_Can_Reward, 1)
			cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(EnumWonderType.Wonder_Act_Duke)
			rewardList = cfg.rewardList
			SetActIdR(EnumWonderType.Wonder_Act_Duke, rewardList)
	#公会争霸相关活动
	unionRankId = EnumWonderType.Wonder_Act_UnionRank
	if GetActState(unionRankId) == 1:
		#活动开启期间，每次城主轮值结束都会覆盖上次的数据
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_22)
		if unionRankId not in WAData:
			WAData[unionRankId] = 0
		if not unionObj:
			return
		WAData[unionRankId] = unionObj.union_id #只记录公会ID
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(EnumWonderType.Wonder_Act_UnionRank)
		rewardList = cfg.rewardList
		SetActIdR(EnumWonderType.Wonder_Act_UnionRank, rewardList)
		#在线会员
		for roleId, _ in unionObj.members.iteritems():
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
			role.SendObj(Wonder_Can_Reward, 1)

def SetJJCData(param = None):
	'''
	记录首站和再战、决战竞技场
	'''
	rankList = param
	if not rankList:
		print "GE_EXC,Wonderful SetJJCData rankList is None"
		return
	rightActId = 0
	#获取当前正在开启的jjc活动
	for actId in EnumWonderType.WonderActJJCList:
		state = GetActState(actId)
		if 1 == state:
			rightActId = actId
			break
	if not rightActId:
		return
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(rightActId)
	if not cfg:
		print "GE_EXC,SetJJCData rightActId(%s) is wrong" % rightActId
		return
	rewardList = cfg.rewardList
	SetActIdR(actId, rewardList)
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_8)
	with WonderfulActJJC:
		WAData[rightActId] = {}
		WAData[rightActId][1] = rankList[0:1]
		WAData[rightActId][2] = rankList[1:2]
		WAData[rightActId][3] = rankList[2:10]
		WAData[rightActId][4] = rankList
		for roleId in rankList:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
			role.SendObj(Wonder_Can_Reward, 1)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderJJCDB, (rightActId, rankList, cDateTime.Now()))
		
def IncTarotNum(param = None):
	'''
	#增加高级占卜数
	'''
	global WONDEFUL_INDEX_7
	
	role = param
	state =  GetActState(EnumWonderType.Wonder_Act_Tarot)
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_7)
	if 1 == state:
		#总共
		WAData[2] = WAData.get(2,0) + 1
		totalNum = WAData[2]
		rewardList = []
		for num, rewardId in wad.WONDER_DIVINATION_DICT.iteritems():
			if totalNum >= num:
				rewardList.append(rewardId)
		if rewardList:
			actId = EnumWonderType.Wonder_Act_Tarot
			SetActIdR(actId, rewardList)
			roles_data = cRoleMgr.GetAllRole()
			for crole in roles_data:
				for rewardId in rewardList:
					state = CheckReward(crole, actId, rewardId)
					if state:
						break
	ACT_LIST = EnumWonderType.WonderActTarotDayList
	TarotDay_ActId = 0
	for actId in ACT_LIST:
		if 1 == GetActState(actId):
			TarotDay_ActId = actId
	if TarotDay_ActId:
		#每日
		WAData[1] = WAData.get(1,0) + 1
		dayNum = WAData[1]
		dayRewardList = []
		rewardList = []
		ActDict = wad.WONDER_DIVINATION_DAY_DICT.get(TarotDay_ActId)
		for num, rewardId in ActDict.iteritems():
			if dayNum >= num:
				dayRewardList.append(rewardId)
		if dayRewardList:
			SetActIdR(TarotDay_ActId, dayRewardList)
			roles_data = cRoleMgr.GetAllRole()
			for Onrole in roles_data:
				for rewardId in dayRewardList:
					state = CheckReward(Onrole, TarotDay_ActId, rewardId)
					if state:
						break
	RoleTarotList = EnumWonderType.WonderActRoleTarotList
	RoleTarot_ActId = 0
	for actId in RoleTarotList:
		if 1 == GetActState(actId):
			RoleTarot_ActId = actId
	if RoleTarot_ActId:
		#玩家每日高级占卜数+1
		role.IncI16(EnumInt16.WonderRoleTarot, 1)
		totalCnt = role.GetI16(EnumInt16.WonderRoleTarot)
		Rolerewards = []
		RoleTarotDict = wad.WONDER_ROLE_TAROT.get(RoleTarot_ActId)
		for cnt, rewardId in RoleTarotDict.iteritems():
			if cnt <= totalCnt:
				Rolerewards.append(rewardId)
		if not Rolerewards:
			return
		SetActIdR(RoleTarot_ActId, Rolerewards)
		wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
		WonderList = wonderObj[2]
		for reward in Rolerewards:
			if reward not in WonderList:
				role.SendObj(Wonder_Can_Reward, 1)
				return
			
def IncGemNum(param = None):
	'''
	增加商城购买的4级宝石数
	'''
	role, coding, cnt = param
	if not cnt:
		return
	GemNum = 0
	for num, codings in wad.LIBAO_FOR_GEM_DICT.iteritems():
		if coding in codings:
			GemNum = num
	if not GemNum:
		return
	totalNum = GemNum * cnt
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_6)
	state =  GetActState(EnumWonderType.Wonder_Act_GemTog)
	if 1 == state:
		#总共
		WAData[2] = WAData.get(2,0) + totalNum
		totalGNum = WAData[2]
		rewardList = []
		for num, rewardId in wad.WONDER_GEM_DICT.iteritems():
			if totalGNum >= num:
				rewardList.append(rewardId)	
		if rewardList:
			GemTog_actId = EnumWonderType.Wonder_Act_GemTog
			SetActIdR(GemTog_actId, rewardList)
			roles_data = cRoleMgr.GetAllRole()
			for crole in roles_data:
				for rewardId in rewardList:
					state = CheckReward(crole, GemTog_actId, rewardId)
					if state:
						break
	ACT_LIST = EnumWonderType.WonderActGemDayList
	GemDay_actId = 0
	for actId in ACT_LIST:
		if 1 == GetActState(actId):
			GemDay_actId = actId
	if GemDay_actId:
		#每天
		WAData[1] = WAData.get(1,0) + totalNum
		dayNum = WAData[1]
		dayRewardList = []
		GemDict = wad.WONDER_GEM_DAY_DICT.get(GemDay_actId)
		for num, rewardId in GemDict.iteritems():
			if dayNum >= num:
				dayRewardList.append(rewardId)
		if dayRewardList:
			SetActIdR(GemDay_actId, dayRewardList)
			roles_data = cRoleMgr.GetAllRole()
			for crole in roles_data:
				for rewardId in dayRewardList:
					state = CheckReward(crole, GemDay_actId, rewardId)
					if state:
						break
	RoleGemList = EnumWonderType.WonderActRoleGemList
	RoleGem_ActId = 0
	for actid in RoleGemList:
		if 1 == GetActState(actid):
			RoleGem_ActId = actid
	if RoleGem_ActId:
		role.IncI16(EnumInt16.WonderRoleGem, totalNum)
		totalCnt = role.GetI16(EnumInt16.WonderRoleGem)
		Rolerewards = []
		RoleGemDict = wad.WONDER_ROLE_GEM.get(RoleGem_ActId)
		for gcnt, rewardId in RoleGemDict.iteritems():
			if gcnt <= totalCnt:
				Rolerewards.append(rewardId)
		if not Rolerewards:
			return
		SetActIdR(RoleGem_ActId, Rolerewards)
		wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
		WonderList = wonderObj[2]
		for reward in Rolerewards:
			if reward not in WonderList:
				role.SendObj(Wonder_Can_Reward, 1)
				return
			
def IncHeroNum(param = None):
	'''
	增加指定的橙色英雄数量
	'''
	heroId = param
	if not heroId:
		return
	if heroId in EnumGameConfig.WONDERFUL_HERO_IDS:
		actId = wad.HEAR_ID_LIST.get(heroId)
		state = GetActState(actId)
		if state == 1:
			WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_5)
			WAData[heroId] = WAData.get(heroId, 0) + 1
			num = WAData[heroId]
			NumDict = wad.WONDER_HERO_DICT.get(heroId)
			if num not in NumDict:
				return
			rewardId = NumDict.get(num)
			SetActIdR(actId, rewardId)
			roles_data = cRoleMgr.GetAllRole()
			for role in roles_data:
				CheckReward(role, actId, rewardId)
		
def IncVIPNum(param = None):
	'''
	增加对应VIP人数，只针对大于或等于VIP4
	'''
	role, IncNum = param
	vipLevel = role.GetVIP()
	oldLevel = vipLevel - IncNum
	CheckRoleVip(role, vipLevel)
	if vipLevel < wad.MIN_VIP_LEVEL:
		return
	#是否合服
	IsHefu = WorldData.IsHeFu()
	Tvips = []
	if vipLevel >= 8:
		for vip in wad.WONDER_ACTID_VIP_DICT.get(EnumWonderType.Wonder_Act_TVIP):
			if oldLevel < vip:
				Tvips.append(vip)
		#取出贵族返利对应的VIP
		VIPList = []
		if IsHefu:#根据是否合服选取不同的VIP
			VIPList = wad.WONDER_ACTID_VIP_DICT.get(EnumWonderType.Wonder_Act_SeniorVIP)
		else:
			VIPList = wad.WONDER_ACTID_VIP_DICT.get(EnumWonderType.Wonder_Act_VIP)
		addvip = []#缓存满足条件的VIP
		for vip in VIPList:
			if oldLevel < vip <= vipLevel:
				addvip.append(vip)
		name = role.GetRoleName()#获取该VIP的玩家名
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
		rewardList = []
		#合服前，各个vip对应的数量是放key1里面，合服后1里面存放总的该VIP对应的数量，清空key2里面的玩家名
		#以后新增的VIP，对应增加的数量存在key3里面，key2存放新增的VIP玩家名，下次合服，需将key3的数据加到
		#key1,然后清空key3和key2的数据，用于下次合服后存新增的VIP信息
		WAData12 = WonderfulData.GetWAData(WONDEFUL_INDEX_12)
		if IsHefu:#已合服
			for level in addvip:
				if level not in WAData:
					WAData[level] = {1:0,2:[name],3:1}
				else:
					WAData[level][3] = WAData[level].get(3, 0) + 1
					WAData[level][2].append(name)
				#取出该VIP的总人数
				total_num = WAData[level].get(1, 0) + WAData[level].get(3, 0)
				vipReward = wad.WONDER_HIGHVIP_REWARD.get(level)#该vip对应的奖励列表
				#重新设置这些奖励ID对应的领取次数
				for rewardId in vipReward:
					WAData12[rewardId] = total_num
					rewardList.append(rewardId)
		else:#未合服
			for level in addvip:
				if level not in WAData:
					WAData[level] = {1:1,2:[name]}
				else:
					WAData[level][1] += 1
					WAData[level][2].append(name)
				#取出该VIP的总人数
				total_num = WAData[level].get(1, 0)
				vipReward = wad.WONDER_VIP_REWARD.get(level)#该vip对应的奖励列表
				#重新设置这些奖励ID对应的领取次数
				for rewardId in vipReward:
					WAData12[rewardId] = total_num
					rewardList.append(rewardId)
		#通知在线玩家可以领奖
		roles_data = cRoleMgr.GetAllRole()
		for role in roles_data:
			vipObj = role.GetObj(EnumObj.Wonder_Vip_Reward_Dict)
			viptimes = vipObj.get(1)
			for rewardId in rewardList:
				if viptimes.get(rewardId) < total_num:
					state = CanGetReward(role, rewardId)
					if state:
						role.SendObj(Wonder_Can_Reward, 1)
						break
	if IsHefu:#下面的逻辑只在合服前执行
		return
	if vipLevel < 8 or Tvips:#下面处理的是4-7级VIP
		WAData4 = WonderfulData.GetWAData(WONDEFUL_INDEX_4)
		vip_list = []
		if Tvips:
			vip_list = Tvips
		else:
			VIPList = wad.WONDER_ACTID_VIP_DICT.get(EnumWonderType.Wonder_Act_TVIP)
			for vip in VIPList:
				if oldLevel < vip <= vipLevel:
					vip_list.append(vip)
		rewards = []
		for level in vip_list:
			WAData4[level] = WAData4.get(level, 0) + 1
			num = WAData4.get(level)
			define_num = wad.WONDER_VIP_DICT.get(level)
			if num >= define_num:
				vipRewards = wad.WONDER_VIP_REWARD.get(level)
				rewards += vipRewards
		#通知在线玩家领奖
		roles_data = cRoleMgr.GetAllRole()
		actId = EnumWonderType.Wonder_Act_TVIP
		for role in roles_data:
			for rewardId in rewards:
				state = CheckReward(role, actId, rewardId)
				if state:
					break

def CheckRoleVip(role, vipLevel):
	#贵族等级活动
	vipLevelR = []
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj = roleObj[1]
	for vip, rewardId in wad.WONDER_VIP_Level_Dict.iteritems():
		if vip <= vipLevel:
			vipLevelR.append(rewardId)
	for rewardId in vipLevelR:
		if rewardId not in wonderObj:
			role.SendObj(Wonder_Can_Reward, 1)
			return
	vipTiliR = []
	for vip, rewardId in wad.WONDER_VIP_TILI_DICT.iteritems():
		if vip <= vipLevel:
			vipTiliR.append(rewardId)
	for reward in vipTiliR:
		if reward not in vipTiliR:
			role.SendObj(Wonder_Can_Reward, 1)
			return
		
def IncFillNum(param = None):
	'''
	增加首冲人数
	'''
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_2)
	WAData += 1
	WonderfulData.SetWAData(WONDEFUL_INDEX_2, WAData)
	num = WAData
	rewardId = 0
	if num in wad.WONDER_FIRST_DICT:
		rewardId = wad.WONDER_FIRST_DICT.get(num)
	if not rewardId:
		return
	roles_data = cRoleMgr.GetAllRole()
	actId = EnumWonderType.Wonder_Act_Fill
	for role in roles_data:
		CheckReward(role, actId, rewardId)
			
def IncMCardNum(param = None):
	'''
	增加购买月卡人数
	'''
	role, cardId = param
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj = roleObj[1]
	if cardId == 1:#周卡
		if wad.WONDER_CARD_REWARD1 not in wonderObj:
			role.SendObj(Wonder_Can_Reward, 1)
	else:
		if wad.WONDER_CARD_REWARD2 not in wonderObj:
			role.SendObj(Wonder_Can_Reward, 1)
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_3)
		old_num = WAData
		if old_num > 30:
			return
		WAData += 1
		WonderfulData.SetWAData(WONDEFUL_INDEX_3, WAData)
		num = WAData
		roles_data = cRoleMgr.GetAllRole()
		rewardId = 0
		if num in wad.WONDER_MONTH_DICT:
			rewardId = wad.WONDER_MONTH_DICT[num]
		if not rewardId:
			return
		actId = EnumWonderType.Wonder_Act_MCard
		for role in roles_data:
			CheckReward(role, actId, rewardId)

def UnionFeed(unionObj):
	'''
	公会神兽喂养
	@param role:
	'''
	if not unionObj:
		return
	actId = EnumWonderType.Wonder_Act_UnionShenShou
	if GetActState(actId) != 1:
		return
	nowGrouth =  unionObj.other_data.get(UnionDefine.O_ShenShowDayFeed, 0)
	shenshouId = unionObj.other_data.get(UnionDefine.O_ShenShouIdCalled, None)
	if shenshouId:#神兽已经召唤了
		nowGrouth = max(nowGrouth, 120)
	canReward = set()
	for grouth, rewardId in wad.UNION_SHENSHOU_DICT.iteritems():
		if grouth <= nowGrouth:
			canReward.add(rewardId)
	if not canReward:
		return
	SetActIdR(actId, canReward)
	for roleId in unionObj.members.iterkeys():
		crole = cRoleMgr.FindRoleByRoleID(roleId)
		if not crole:
			continue
		for rewardId in canReward:
			state = CheckReward(crole, actId, rewardId)
			if state: break
				
def UnionGods(unionObj):
	'''
	公会魔神
	@param unionObj:
	'''
	if not unionObj:
		return
	actId = EnumWonderType.Wonder_Act_UnionGod
	if GetActState(actId) != 1:
		return
	timeDict = unionObj.god.get(UnionDefine.GOD_FIGHT_IDX)
	rewards = set()
	for god, (times, rewardId) in wad.UNION_GOD_DICT.iteritems():
		if timeDict.get(god, 0) < times:
			continue
		rewards.add(rewardId)
	if not rewards: 
		return
	SetActIdR(actId, rewards)
	for roleId in unionObj.members.iterkeys():
		crole = cRoleMgr.FindRoleByRoleID(roleId)
		if not crole:
			continue
		for rewardId in rewards:
			state = CheckReward(crole, actId, rewardId)
			if state: break
			
def UnionTotalFill(unionObj):
	'''
	公会一起充
	@param unionObj:
	'''
	if not unionObj:
		return
	actId = EnumWonderType.Wonder_UnionTotalFill
	if GetActState(actId) != 1:
		return
	totalfill = unionObj.other_data.get(UnionDefine.O_TotalFillRMB)
	canReward = set()
	for fill, rewardId in wad.UNION_FILL_DICT.iteritems():
		if totalfill < fill:
			continue
		canReward.add(rewardId)
	if not canReward:
		return
	SetActIdR(actId, canReward)
	for roleId in unionObj.members.iterkeys():
		crole = cRoleMgr.FindRoleByRoleID(roleId)
		if not crole:
			continue
		for rewardId in canReward:
			state = CheckReward(crole, actId, rewardId)
			if state: break
			
def PetEvo(param):
	'''
	宠物修行
	@param param:
	'''
	role, times = param
	PE_actId = EnumWonderType.Wonder_Act_PetEvo
	if GetActState(PE_actId) == 1:
		role.IncI32(EnumInt32.PetEvoTimes, times)
		PetEvoTimes = role.GetI32(EnumInt32.PetEvoTimes)
		rewards = set()
		for evotimes, rewardId in wad.PET_EVO_DICT.iteritems():
			if evotimes > PetEvoTimes:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(PE_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, PE_actId, rewardId)
				if state:break
	
	TPE_actId = EnumWonderType.Wonder_Act_TotalPetEvo
	if GetActState(TPE_actId) == 1:
		if times <= 0: return
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_26)
		if TPE_actId not in WAData:
			WAData[TPE_actId] = 0
		WAData[TPE_actId] = WAData.get(TPE_actId, 0) + times #增加全服宠物培养次数
		totalTimes = WAData.get(TPE_actId)
		rewards = set()
		for ttimes, rewardId in wad.PET_TOTALEVO_DICT.iteritems():
			if ttimes > totalTimes:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(TPE_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, TPE_actId, rewardId)
				if state:
					break
				
def FashionUpStar(param):
	'''
	时装升星
	@param param:
	'''
	role, cnt = param
	if cnt <= 0:
		return
	Upstar_actId = EnumWonderType.Wonder_Act_FashionUpStar
	if GetActState(Upstar_actId) == 1:
		role.IncI32(EnumInt32.FashionUpStarTimes, cnt)
		usTimes = role.GetI32(EnumInt32.FashionUpStarTimes)
		rewards = set()
		for times, rewardId in wad.FASHION_UPSTAR_DICT.iteritems():
			if times > usTimes:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(Upstar_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, Upstar_actId, rewardId)
				if state: break
		
	total_actId = EnumWonderType.Wonder_Act_FashionTotalStar
	if GetActState(total_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_27)
		if total_actId not in WAData:
			WAData[total_actId] = 0
		WAData[total_actId] = WAData.get(total_actId, 0) + cnt #增加全服时装升星消耗
		totalCnt = WAData.get(total_actId)
		rewards = set()
		for times, rewardId in wad.FASHION_TOTAL_DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(total_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, total_actId, rewardId)
				if state:
					break
				
def FashionUpOrder(param):
	'''
	时装升价
	@param param:
	'''
	role, cnt = param
	if cnt <= 0:
		return
	Upstar_actId = EnumWonderType.Wonder_Act_FashionUpOrder
	if GetActState(Upstar_actId) == 1:
		role.IncI32(EnumInt32.FashionUpOrderTimes, cnt)
		usTimes = role.GetI32(EnumInt32.FashionUpOrderTimes)
		rewards = set()
		for times, rewardId in wad.FASHION_ORDER_DICT.iteritems():
			if times > usTimes:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(Upstar_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, Upstar_actId, rewardId)
				if state: break
		
	total_actId = EnumWonderType.Wonder_Act_FashionTotalOrder
	if GetActState(total_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_28)
		if total_actId not in WAData:
			WAData[total_actId] = 0
		WAData[total_actId] = WAData.get(total_actId, 0) + cnt #增加全服时装升星消耗
		totalCnt = WAData.get(total_actId)
		rewards = set()
		for times, rewardId in wad.FASHION_TOTAL_ORDER_DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(total_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, total_actId, rewardId)
				if state:
					break

def StarGirlLevelUp(param):
	#星灵升级
	role, cnt = param
	if cnt < 0: return
	Levelup_actId = EnumWonderType.Wonder_ACT_StarGirlLevel
	if GetActState(Levelup_actId) == 1:
		role.IncI32(EnumInt32.StarGirlLevelUpTimes, cnt)
		total_times = role.GetI32(EnumInt32.StarGirlLevelUpTimes)
		rewards = set()
		for times, rewardId in wad.STARGIRL_LEVELUP_DICT.iteritems():
			if times > total_times:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(Levelup_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, Levelup_actId, rewardId)
				if state: break
	totalLu_actId = EnumWonderType.Wonder_ACT_TotalStarGirlLevel
	if GetActState(totalLu_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_29)
		if totalLu_actId not in WAData:
			WAData[totalLu_actId] = 0
		WAData[totalLu_actId] = WAData.get(totalLu_actId, 0) + cnt #增加全服星灵升级消耗
		totalCnt = WAData.get(totalLu_actId)
		rewards = set()
		for times, rewardId in wad.STARGIRL_TOTAL_LEVELUP_DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(totalLu_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, totalLu_actId, rewardId)
				if state:
					break
				
def StarGirlStar(param):
	#星灵升星
	role, cnt = param
	if cnt < 0: return
	star_actId = EnumWonderType.Wonder_ACT_StarGirlStar
	if GetActState(star_actId) == 1:
		role.IncI32(EnumInt32.StarGirlStarTimes, cnt)
		total_times = role.GetI32(EnumInt32.StarGirlStarTimes)
		rewards = set()
		for times, rewardId in wad.STARGIRL_STAR_DICT.iteritems():
			if times > total_times:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(star_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, star_actId, rewardId)
				if state: break
	totalStar_actId = EnumWonderType.Wonder_ACT_TotalStarGirlStar
	if GetActState(totalStar_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_30)
		if totalStar_actId not in WAData:
			WAData[totalStar_actId] = 0
		WAData[totalStar_actId] = WAData.get(totalStar_actId, 0) + cnt #增加全服星灵升星消耗
		totalCnt = WAData.get(totalStar_actId)
		rewards = set()
		for times, rewardId in wad.STARGIRL_TOTAL_STAR_DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(totalStar_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, totalStar_actId, rewardId)
				if state:
					break
				
def DragonVeinLevel(param):
	#龙脉升级
	role, cnt = param
	if cnt < 0: return
	level_actId = EnumWonderType.Wonder_Act_DragonLevelUp
	if GetActState(level_actId) == 1:
		role.IncI32(EnumInt32.DragonVeinLevelTimes, cnt)
		total_times = role.GetI32(EnumInt32.DragonVeinLevelTimes)
		rewards = set()
		for times, rewardId in wad.DRAGON_LEVEL_DICT.iteritems():
			if times > total_times:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(level_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, level_actId, rewardId)
				if state: break
				
	total_actId = EnumWonderType.Wonder_Act_TotalDragonLevelUp
	if GetActState(total_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_31)
		if total_actId not in WAData:
			WAData[total_actId] = 0
		WAData[total_actId] = WAData.get(total_actId, 0) + cnt #增加全服龙脉升级消耗
		totalCnt = WAData.get(total_actId)
		rewards = set()
		for times, rewardId in wad.DRAGON_TOTAL_LEVEL_DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(total_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, total_actId, rewardId)
				if state:
					break
				
def DragonVeinEvo(param):
	#龙脉进化
	role, cnt = param
	if cnt < 0: return
	evo_actId = EnumWonderType.Wonder_Act_DragonEvo
	if GetActState(evo_actId) == 1:
		role.IncI32(EnumInt32.DragonVeinEvoTimes, cnt)
		total_times = role.GetI32(EnumInt32.DragonVeinEvoTimes)
		rewards = set()
		for times, rewardId in wad.DRAGON_EVO_DICT.iteritems():
			if times > total_times:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(evo_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, evo_actId, rewardId)
				if state: break
				
	total_actId = EnumWonderType.Wonder_Act_TotalDragonEvo
	if GetActState(total_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_32)
		if total_actId not in WAData:
			WAData[total_actId] = 0
		WAData[total_actId] = WAData.get(total_actId, 0) + cnt #增加全服龙脉进化消耗
		totalCnt = WAData.get(total_actId)
		rewards = set()
		for times, rewardId in wad.DRAGON_TOTAL_EVO_DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(total_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, total_actId, rewardId)
				if state:
					break
				
def TitleLevel(param):
	#称号升级
	role, cnt = param
	if cnt < 0: return
	level_actId = EnumWonderType.Wonder_Act_TitleLevel
	if GetActState(level_actId) == 1:
		role.IncI32(EnumInt32.TitleLevelUpTimes, cnt)
		total_times = role.GetI32(EnumInt32.TitleLevelUpTimes)
		rewards = set()
		for times, rewardId in wad.TITLE_LEVELUP__DICT.iteritems():
			if times > total_times:
				continue
			rewards.add(rewardId)
		if rewards:
			SetActIdR(level_actId, rewards)
			for rewardId in rewards:
				state = CheckReward(role, level_actId, rewardId)
				if state: break
				
	total_actId = EnumWonderType.Wonder_Act_TotalTitleLevel
	if GetActState(total_actId) == 1:
		WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_33)
		if total_actId not in WAData:
			WAData[total_actId] = 0
		WAData[total_actId] = WAData.get(total_actId, 0) + cnt #增加全服称号升级消耗
		totalCnt = WAData.get(total_actId)
		rewards = set()
		for times, rewardId in wad.TITLE_TOTAL_LEVELUP__DICT.iteritems():
			if times > totalCnt:
				continue
			rewards.add(rewardId)
		if not rewards:
			return
		SetActIdR(total_actId, rewards)
		roles_data = cRoleMgr.GetAllRole()
		for crole in roles_data:#通知在线玩家领奖
			for rewardId in rewards:
				state = CheckReward(crole, total_actId, rewardId)
				if state:
					break
#=============================各种接口================================
def CheckReward(role, actId, rewardId, param = None):
	'''
	通知在线玩家有奖励可以领取
	'''
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC, CheckReward, error actId (%s)" % actId
		return
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	getedList = None
	if cfg.dayfresh:#奖励是否每日刷新
		getedList = roleObj[2]
	else:
		getedList = roleObj[1]
	if rewardId in getedList:
		return
	state = CanGetReward(role, rewardId, param)
	if state:
		role.SendObj(Wonder_Can_Reward, 1)
		return True
	
def SetActIdR(actId, rewardList):
	'''
	将可以领取的活动奖励存起来
	'''
	
	actData = WonderfulData.GetWAData(WONDEFUL_INDEX_11)
	if actData is None: return
	
	rewardSet = actData.get(actId)
	if not rewardSet:
		actData[actId] = rewardSet = set()
	if type(rewardList) == int:
		rewardSet.add(rewardList)
	elif type(rewardList) == list or type(rewardList) == set:
		RA = rewardSet.add
		for rewardId in rewardList:
			RA(rewardId)
			
def CanGetReward(role, rewardId, param=None):
	'''
	玩家是否能获取该奖励
	@param role:
	@param rewardId:
	'''
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, CanGetReward error rewardId (%s)" % rewardId
		return False
	if cfg.needVIP:
		if role.GetVIP() < cfg.needVIP:
			return False
	if cfg.level:
		if role.GetLevel() < cfg.level:
			return False
	if cfg.needZDL:
		if role.GetZDL() < cfg.needZDL:
			return False
	if cfg.needFill:
		if not role.GetI8(EnumInt8.FiveGiftFirst):
			return False
	if cfg.bugCard:
		if cfg.bugCard == 1:
			if not role.GetI1(EnumInt1.WeekCardFirst):
				return False
		if cfg.bugCard == 2:
			if not role.GetI1(EnumInt1.MonthCardFirst):
				return False
	
	if cfg.fillNum:#需要首冲人数
		if role.GetI8(EnumInt8.FiveGiftFirst) == 0:
			return False
		fill_num = WonderfulData.GetWAData(WONDEFUL_INDEX_2)
		if fill_num < cfg.fillNum:
			return False
	if cfg.cardNum:#购买月卡人数
		card_num = WonderfulData.GetWAData(WONDEFUL_INDEX_3)
		if card_num < cfg.cardNum:
			return False
	if cfg.oneFlyNum:#翅膀要求(1,4) 一级翅膀4对
		wlevel, num = cfg.oneFlyNum
		wingDict = role.GetObj(EnumObj.Wing)[1]
		wingList = wingDict.values()
		cnt = 0
		for wing in wingList:
			if wlevel <= wing[0]:
				cnt += 1
		if cnt < num:
			return False
	if cfg.VIPNum:#VIP需要的人数 (（4,5）4级vip5人)
		vip, roleNum = cfg.VIPNum
		num = 0
		if vip >= 8:
			WAData8 = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
			num = WAData8.get(vip, 0)
		else:
			WAData4 = WonderfulData.GetWAData(WONDEFUL_INDEX_4)
			num = WAData4.get(vip, 0)
		if num < roleNum:
			return False
	if cfg.orangeHeroNum:#橙色英雄数
		HeroData = WonderfulData.GetWAData(WONDEFUL_INDEX_5)
		heroId, heroNum = cfg.orangeHeroNum
		if HeroData.get( heroId, 0) < heroNum:
			return False
	if cfg.needGemNum:#需要总商城出售宝石数
		GemDataT = WonderfulData.GetWAData(WONDEFUL_INDEX_6)
		if GemDataT.get(2,0) < cfg.needGemNum:
			return False
	if cfg.needGemNumDay:#需要每日商城出售宝石数
		GemDataD = WonderfulData.GetWAData(WONDEFUL_INDEX_6)
		if GemDataD.get(1,0) < cfg.needGemNumDay:
			return False
	if cfg.TarotNum:#高级占卜数
		TarDataT = WonderfulData.GetWAData(WONDEFUL_INDEX_7)
		if TarDataT.get(2,0) < cfg.TarotNum:
			return False
	if cfg.TarotNumDay:#每日高级占卜数
		TarDataD = WonderfulData.GetWAData(WONDEFUL_INDEX_7)
		if TarDataD.get(1,0) < cfg.TarotNumDay:
			return False
	if cfg.mountLevel:#需要坐骑等级
		evolve = role.GetI16(EnumInt16.MountEvolveID)
		if evolve < cfg.mountLevel:
			return False
	if cfg.maxNum:#领取的最大量
		MaxData = WonderfulData.GetWAData(WONDEFUL_INDEX_1)
		thisIdNum = MaxData.get(cfg.rewardId, 0)
		if cfg.maxNum <= thisIdNum:
			return False
	if cfg.mountNumber:#需要的坐骑个数
		evolveId, num = cfg.mountNumber
		MountData = WonderfulData.GetWAData(WONDEFUL_INDEX_16)
		if MountData.get(evolveId,0) < num:
			return False
	if cfg.singleFill:#单笔充值数
		if role.GetI32(EnumInt32.WonderSingleFill) < cfg.singleFill:
			return False
	if cfg.equipNum:#收集指定套装数
		eid, suitNum = cfg.equipNum
		num = CheckEquip(role, eid, param)
		if num < suitNum:
			return False
	if cfg.TotalFill:#玩家每日累计充值
		if role.GetI32(EnumInt32.WonderTotalFill) < cfg.TotalFill:
			return False
	if cfg.TotalGem:#玩家每日累计购买宝石数
		if role.GetI16(EnumInt16.WonderRoleGem) < cfg.TotalGem:
			return False
	if cfg.totalTaro:#玩家每日高级占卜数
		if role.GetI16(EnumInt16.WonderRoleTarot) < cfg.totalTaro:
			return False
	if cfg.MallWing:#翅膀返利
		wingDict = role.GetObj(EnumObj.Wing)[1]
		keyList = wingDict.keys()
		if not keyList : return False
		wNum, WIds = cfg.MallWing
		cnt = 0
		for wid in keyList:
			if wid in WIds:
				cnt += 1
		if cnt < wNum : return False	
	if cfg.UnionTreNum:#天天夺宝
		boxType, boxNum = cfg.UnionTreNum
		TreData = WonderfulData.GetWAData(WONDEFUL_INDEX_17)
		totalNum = TreData.get(boxType, 0)
		if totalNum < boxNum:
			return False
	if cfg.TotalRMB:#全服累计消费
		TotalData = WonderfulData.GetWAData(WONDEFUL_INDEX_18)
		if TotalData < cfg.TotalRMB:
			return False
	if cfg.PetNum:#（星数，个数）
		star, num = cfg.PetNum
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
		petDict = petMgr.pet_dict 
		if not petDict:
			return False
		petNum = 0
		for pet in petDict.values():
			if pet.star >= star:
				petNum += 1
		if petNum < num:
			return False
	if cfg.MarryCnt:#全服结婚的对数
		if WorldData.WD[EnumSysData.MarryCnt] < cfg.MarryCnt:
			return False
	if cfg.RingLevel:#戒指等级
		if role.GetI16(EnumInt16.WeddingRingID) < cfg.RingLevel:
			return False
	if cfg.HefuDay:#合服天数判断
		if WorldData.GetHeFuDay() != cfg.HefuDay:
			return False
	if cfg.WingTimes:#个人翅膀培养次数
		if role.GetI32(EnumInt32.WingCultivateTimes) < cfg.WingTimes:
			return False
	if cfg.TogWingTimes:#全服翅膀培养次数
		WingData = WonderfulData.GetWAData(WONDEFUL_INDEX_24)
		if not WingData:
			return False
		totalTimes = WingData.get(EnumWonderType.Wonder_Act_TogWing, 0)
		if totalTimes < cfg.TogWingTimes:
			return False
	if cfg.PetTimes:#个人宠物培养次数
		if role.GetI32(EnumInt32.PetCultivateTimes) < cfg.PetTimes:
			return False
	if cfg.TogPetTimes:#全服宠物培养次数
		PetData = WonderfulData.GetWAData(WONDEFUL_INDEX_25)
		if not PetData:
			return False
		totalTimes = PetData.get(EnumWonderType.Wonder_Act_TogPet, 0)
		if totalTimes < cfg.TogPetTimes:
			return False
	if cfg.needFeedTimes:#公会神兽成长度
		unionObj = role.GetUnionObj()
		if not unionObj:
			return False
		if not unionObj.other_data.get(UnionDefine.O_ShenShouIdCalled, None) and \
			unionObj.other_data.get(UnionDefine.O_ShenShowDayFeed, 0) < cfg.needFeedTimes:
			return False
	if cfg.unionGod:#公会魔神通关
		unionObj = role.GetUnionObj()
		if not unionObj:
			return False
		from Game.Union import UnionGod
		UnionGod.IsNextDay(role, unionObj)#这里必须这样调用下
		FTDict = unionObj.god.get(UnionDefine.GOD_FIGHT_IDX)
		godId, times = cfg.unionGod
		if FTDict.get(godId, 0) < times:
			return False
	if cfg.unionFill:#公会累计充值
		unionObj = role.GetUnionObj()
		if not unionObj:
			return False
		totalfill = unionObj.other_data.get(UnionDefine.O_TotalFillRMB)
		if totalfill < cfg.unionFill:
			return False
	if cfg.petEvoTimes:#个人宠物修行
		if role.GetI32(EnumInt32.PetEvoTimes) < cfg.petEvoTimes:
			return False
	if cfg.totalPetTimes:#宠物齐修行
		PetData = WonderfulData.GetWAData(WONDEFUL_INDEX_26)
		if not PetData:
			return False
		totalTimes = PetData.get(EnumWonderType.Wonder_Act_TotalPetEvo, 0)
		if totalTimes < cfg.totalPetTimes:
			return False
	if cfg.upstartimes:#时装升星
		if role.GetI32(EnumInt32.FashionUpStarTimes) < cfg.upstartimes:
			return False
	if cfg.totalUpstar:#时装齐升星
		PetData = WonderfulData.GetWAData(WONDEFUL_INDEX_27)
		if not PetData:
			return False
		totalTimes = PetData.get(EnumWonderType.Wonder_Act_FashionTotalStar, 0)
		if totalTimes < cfg.totalUpstar:
			return False
	if cfg.upordertimes:#时装升阶
		if role.GetI32(EnumInt32.FashionUpOrderTimes) < cfg.upordertimes:
			return False
	if cfg.totalUpOrder:#时装齐升阶
		tData = WonderfulData.GetWAData(WONDEFUL_INDEX_28)
		if not tData:
			return False
		totalTimes = tData.get(EnumWonderType.Wonder_Act_FashionTotalOrder, 0)
		if totalTimes < cfg.totalUpOrder:
			return False
	if cfg.StarGirlLevel:#星灵升级
		if role.GetI32(EnumInt32.StarGirlLevelUpTimes) < cfg.StarGirlLevel:
			return False
	if cfg.totalStarGirlLevel:#星灵齐升级
		tData = WonderfulData.GetWAData(WONDEFUL_INDEX_29)
		if not tData:
			return False
		totalTimes = tData.get(EnumWonderType.Wonder_ACT_TotalStarGirlLevel, 0)
		if totalTimes < cfg.totalStarGirlLevel:
			return False
	if cfg.StarGirlStar:#星灵升星
		if role.GetI32(EnumInt32.StarGirlStarTimes) < cfg.StarGirlStar:
			return False
	if cfg.totalStarGirlStar:#星灵齐升星
		tData = WonderfulData.GetWAData(WONDEFUL_INDEX_30)
		if not tData:
			return False
		totalTimes = tData.get(EnumWonderType.Wonder_ACT_TotalStarGirlStar, 0)
		if totalTimes < cfg.totalStarGirlStar:
			return False
	if cfg.dragonLevel:#龙脉升级
		if role.GetI32(EnumInt32.DragonVeinLevelTimes) < cfg.dragonLevel:
			return False
	if cfg.totaldragonLevel:#龙脉齐升级
		tData = WonderfulData.GetWAData(WONDEFUL_INDEX_31)
		if not tData:
			return False
		totalTimes = tData.get(EnumWonderType.Wonder_Act_TotalDragonLevelUp, 0)
		if totalTimes < cfg.totaldragonLevel:
			return False
	if cfg.dragonEvo:#龙脉进化
		if role.GetI32(EnumInt32.DragonVeinEvoTimes) < cfg.dragonEvo:
			return False
	if cfg.totaldragonEvo:#龙脉齐进化
		tData = WonderfulData.GetWAData(WONDEFUL_INDEX_32)
		if not tData:
			return False
		totalTimes = tData.get(EnumWonderType.Wonder_Act_TotalDragonEvo, 0)
		if totalTimes < cfg.totaldragonEvo:
			return False
	if cfg.titleLevel:#称号升级
		if role.GetI32(EnumInt32.TitleLevelUpTimes) < cfg.titleLevel:
			return False
	if cfg.totaltitleLevel:#称号齐升级
		tData = WonderfulData.GetWAData(WONDEFUL_INDEX_33)
		if not tData:
			return False
		totalTimes = tData.get(EnumWonderType.Wonder_Act_TotalTitleLevel, 0)
		if totalTimes < cfg.totaltitleLevel:
			return False
	return True

def GetEndTime(actId):
	'''
	获取活动的结束时间，无时限返回-1

	'''
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		return
	end_time = cfg.endtime
	if end_time != datetime.datetime(2038, 1, 1):#有填指定结束时间
		return end_time
	else:
		IsHefu = WorldData.IsHeFu()
		kaifu_start = 0
		kaifu_time = 0
		if cfg.IsHefu == 2:#合服后才开启的活动
			if not IsHefu:#未合服
				return 1
			kaifu_start = cfg.hefutime
			kaifu_time = WorldData.WD.get(EnumSysData.HeFuKey)
		else:
			if cfg.IsHefu == 1 and IsHefu:#合服前开启的活动，但已合服
				return 1
			kaifu_start = cfg.kaifutime
			kaifu_time = WorldData.WD.get(EnumSysData.KaiFuKey)
		keepday = cfg.keepday#持续时间
		if -1 == keepday:#活动无时限
			return -1
		if kaifu_time is None:
			return 1
		unit_time = Time.DateTime2UnitTime(kaifu_time)
		if kaifu_time.hour or kaifu_time.minute or kaifu_time.second:
			unit_time -= kaifu_time.hour * 3600 + kaifu_time.minute * 60 + kaifu_time.second
		if not kaifu_start:
			kaifu_start = unit_time
		else:
			kaifu_start = unit_time + (kaifu_start * 3600 * 24)
		keepday = kaifu_start + (keepday * 3600 * 24) - 1
		return Time.UnixTime2DateTime(keepday)

def GetDisappearTime(actId):
	'''
	获取活动从面板上消失的时间
	'''
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		return
	#=========合服特殊操作=============
	IsHefu = WorldData.IsHeFu()
	if IsHefu and cfg.IsHefu == 1:#已经合服了，但活动不需要合服
		return 1
	if not IsHefu and cfg.IsHefu == 2:#未合服，但活动需要合服
		return 1
	#=================================
	endTime = GetEndTime(actId)
	if endTime == -1:
		return endTime
	if cfg.rewardday:
		unit_time = Time.DateTime2UnitTime(endTime)
		rewardday = unit_time + 24*3600
		endTime = Time.UnixTime2DateTime(rewardday)
	return endTime
	
def GetActState(actId):
	'''
	检查活动状态，-1 活动未开启，0 结束，1进行中，2处在领奖期间

	'''
	#有些活动是受循环活动控制的，不读配置
	if actId == EnumWonderType.Wonder_Act_FillLiBao:
		if COTMgr.__COTSTART:
			return 1
		else:
			return -1
	elif actId == EnumWonderType.Wonder_Act_SendCard:
		if BallFame.isBallFameOpen:
			return 1
		else:
			return -1
	elif actId == EnumWonderType.Wonder_Act_SendKey:
		if GoldChest.__IS_START:
			return 1
		else:
			return -1
	elif actId == EnumWonderType.Wonder_Act_SendHallows:
		global HALLOWS_IS_START
		if HALLOWS_IS_START:
			return 1
		else:
			return -1
	else:
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,can not find actId(%s) in GetActState" % actId
			return 0
		if cfg.processIds:
			if cProcess.ProcessID not in cfg.processIds:
				#只有部分的服务器开启
				return -1
		#=========获取合服状态=========
		IsHefu = WorldData.IsHeFu()
		if IsHefu and cfg.IsHefu == 1:#已经合服了，但活动不需要合服
			return 0
		if not IsHefu and cfg.IsHefu == 2:#未合服，但活动需要合服
			return 0
		#==========================
		now = cDateTime.Now()
		start = cfg.starttime#指定开启时间
		rewardday = cfg.rewardday
		if start != datetime.datetime(2038, 1, 1):#不是默认时间，那就有指定开启时间
			if start > now:
				return 0
			end_time = cfg.endtime
			if end_time < now:#活动结束
				remain_day = now - end_time
				if rewardday and remain_day.days < rewardday:
					return 2
				return 0
			else:
				return 1
		else:
			act_start = 0	#保存开始活动的天数
			rely_time = 0	#开服或合服时间
			#根据是否合服，获取配置
			if cfg.IsHefu == 2:#合服后才开启的活动取合服时间
				act_start = cfg.hefutime
				rely_time = WorldData.WD.get(EnumSysData.HeFuKey)
			else:#合服前和合服无关的活动取开服时间
				act_start = cfg.kaifutime
				rely_time = WorldData.WD.get(EnumSysData.KaiFuKey)

			keepday = cfg.keepday#持续时间
			if rely_time is None:
				return 0
			unit_time = Time.DateTime2UnitTime(rely_time)
			if rely_time.hour or rely_time.minute or rely_time.second:
				unit_time -= rely_time.hour * 3600 + rely_time.minute * 60 + rely_time.second
			if not act_start:
				act_start = unit_time
			else:
				act_start = unit_time + (act_start * 3600 * 24)
			unit_nowtime = Time.DateTime2UnitTime(now)
			if unit_nowtime < act_start:#活动未开启
				return 0
			if keepday == -1:#活动无时限
				return 1
			if keepday:
				keepday = act_start + (keepday * 3600 * 24) - 1
			if unit_nowtime > keepday:#活动结束
				ckeepday = Time.UnixTime2DateTime(keepday)
				remain_day = now.day - ckeepday.day
				if rewardday and rewardday >= remain_day:
					return 2
				return 0
			else:
				return 1

def GetCanGetIDByAct(role, actId):
	'''
	根据活动ID获取可以领取的奖励
	@param role:
	@param actId:
	'''
	
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,can not find actId(%s) in GetCanGetIDByAct" % actId
		return
	if GetActState(actId) != 1 and GetActState(actId) != 2:
		return []
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	getedList = set()
	if cfg.dayfresh:#奖励是否每日刷新
		getedList = roleObj[2]
	else:
		getedList = roleObj[1]

	canList = []	#存可以领取的奖励ID
	keep = cfg.keepday
	if keep == -1:#无时限活动
		IsHefu = WorldData.IsHeFu()
		rewardList = []
		if not IsHefu:#没合服，取未合服前开启的活动奖励
			if actId not in WonderfulActConfig.WONDER_FOREVER_REWARD:
				return canList
			rewardList = WonderfulActConfig.WONDER_FOREVER_REWARD.get(actId)
		else:#合服后，取合服后开启的活动奖励
			if actId not in WonderfulActConfig.WONDER_HEFU_FOREVER_REWARD:
				return
			rewardList = WonderfulActConfig.WONDER_HEFU_FOREVER_REWARD.get(actId)
		if actId == EnumWonderType.Wonder_Act_VIP or actId == EnumWonderType.Wonder_Act_SeniorVIP:#贵族返利
			#获取可以领取几次的奖励数据
			VipData = WonderfulData.GetWAData(WONDEFUL_INDEX_12)
			#获取玩家有关每个奖励可以领取多次的数据
			vipObj = role.GetObj(EnumObj.Wonder_Vip_Reward_Dict)
			viptimes = vipObj.get(1)
			for rewardId, times in VipData.iteritems():
				#是否是该活动的奖励ID，是的话判断次数
				if rewardId in rewardList and viptimes.get(rewardId, 0) < times:
					state = CanGetReward(role, rewardId)
					if state:
						canList.append(rewardId)
		else:#无时限其他活动
			for rewardId in rewardList:
				if rewardId not in getedList:
					state = CanGetReward(role, rewardId)
					if state:
						canList.append(rewardId)
	else:#有时限
		RewardData = WonderfulData.GetWAData(WONDEFUL_INDEX_11)
		canList = []
		if actId not in RewardData:#活动ID未在激活数据里
			return canList
		#获取该活动对应的奖励，并进行遍历
		rewards = RewardData.get(actId)
		for rewardId in rewards:
			tstate = False
			if rewardId not in getedList:
				if actId in EnumWonderType.SPECIAL_ACT_LIST:#有些活动需进行特殊处理
					tstate = CheckSpecialReward(role, actId, rewardId)
				else:
					tstate = CanGetReward(role, rewardId)
			if tstate:
				canList.append(rewardId)
	return canList

def CheckSpecialReward(role, actId, rewardId):
	#这里是对一些需要存DB结算的活动特殊处理
	state = False
	if actId == EnumWonderType.Wonder_Act_Mount:
		state = CheckMountReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_JJC or actId == EnumWonderType.Wonder_Act_JJC2 or \
		actId == EnumWonderType.Wonder_Act_JJC3 or actId == EnumWonderType.Wonder_Act_JJC4:
		state = CheckJJCReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_Duke:
		state = CheckDukeReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_Union:
		state = CheckUnionReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_ZDL:
		state = CheckZDLReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_GloryWar:
		state = CheckGloryWarReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_MarryRing:
		state = CheckMarryRing(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_FillRank:
		state = CheckFillRank(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_UnionRank:
		state = CheckUnionRankReward(role, actId, rewardId)
	elif actId == EnumWonderType.Wonder_Act_ZDLRank:
		state = CheckZDLRankReward(role, actId, rewardId)
	return state

def GetCanGetID(role):
	'''
	获取玩家所有活动可以领取的奖励
	@param role:
	'''
	global WONDEFUL_INDEX_11
	global WONDEFUL_INDEX_12
	
	RewardData = WonderfulData.GetWAData(WONDEFUL_INDEX_11)
	#每日刷新活动
	dayFrest = WonderfulActConfig.WONDER_DAY_FRESH_LIST
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	canDict = {}
	for actId, rewards in RewardData.iteritems():
		if GetActState(actId) != 1 and GetActState(actId) != 2:
			continue
		getedList = set()
		if actId in dayFrest:#根据是否是每日刷新，获取玩家的已领取列表
			getedList = roleObj[2]
		else:
			getedList = roleObj[1]
		for rewardId in rewards:
			state = False
			if rewardId not in getedList:#玩家未领取，检测各种条件
				if actId in EnumWonderType.SPECIAL_ACT_LIST:
					state = CheckSpecialReward(role, actId, rewardId)
				else:
					state = CanGetReward(role, rewardId)
			if state:
				if actId not in canDict:
					canDict[actId] = set()
				canDict[actId].add(rewardId)
	#无时限的活动
	IsHefu = WorldData.IsHeFu()
	Forever_dict = {}
	if IsHefu:#根据是否合服取不同的无时限配置
		Forever_dict = WonderfulActConfig.WONDER_HEFU_FOREVER_REWARD
	else:
		Forever_dict = WonderfulActConfig.WONDER_FOREVER_REWARD
	for actId, rewards in Forever_dict.iteritems():#变量各个活动的奖励ID
		getedList = set()
		if GetActState(actId) != 1 and GetActState(actId) != 2:
			continue
		if actId in dayFrest:#根据是否是每日刷新，获取玩家的已领取列表
			getedList = roleObj[2]
		else:
			getedList = roleObj[1]
		if actId == EnumWonderType.Wonder_Act_VIP or actId == EnumWonderType.Wonder_Act_SeniorVIP:
			VipData = WonderfulData.GetWAData(WONDEFUL_INDEX_12)
			if not VipData:
				continue
			vipObj = role.GetObj(EnumObj.Wonder_Vip_Reward_Dict)
			viptimes = vipObj.get(1)
			for rewardId, times in VipData.iteritems():
				state = CanGetReward(role, rewardId)
				if state:
					if viptimes.get(rewardId) < times:#玩家领取的次数小于可以领取的次数，可以领取
						if actId not in canDict:
							canDict[actId] = set()
						canDict[actId].add(rewardId)
		else:
			for rewardId in rewards:
				if rewardId in getedList:#奖励已领取
					continue
				state = CanGetReward(role, rewardId)
				if state:
					if actId not in canDict:
						canDict[actId] = set()
					canDict[actId].add(rewardId)
	return canDict
#==================================玩家事件=================================
def AfterChangeMountEvole(role, param):
	'''
	玩家坐骑阶数改变
	@param role:
	@param param:
	'''
	_, newValue = param
	
	if not WorldData.WD.returnDB:
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	from Game.Activity.KaifuTarget import TimeControl
	if 1 == GetActState(EnumWonderType.Wonder_Act_Mount) and ((TimeControl.KaifuTargetTime_New < kaifuTime) or (Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015, 4, 10, 0, 0, 0))):#坐骑争霸活动
		cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(wad.WONDER_MOUNT_REWARD3)
		if cfg:
			if newValue == cfg.mountLevel:
				actId = EnumWonderType.Wonder_Act_Mount
				SetActIdR(actId, wad.WONDER_MOUNT_REWARD3)
				CheckReward(role, actId, wad.WONDER_MOUNT_REWARD3)

	if 1 == GetActState(EnumWonderType.Wonder_Act_MountUp):#坐骑升级活动
		canRewardId = 0
		for level, rId in wad.WONDER_MOUNT_UP.iteritems():
			if newValue == level:
				canRewardId = rId
				break
		if canRewardId:
			actId = EnumWonderType.Wonder_Act_MountUp
			SetActIdR(actId, canRewardId)
			CheckReward(role, actId, canRewardId)

	if 1 == GetActState(EnumWonderType.Wonder_Act_MountTog):#坐骑一起冲活动
		minEvolve = 0
		#需要改动配置
		for evolveList in wad.WONDER_MOUNTTOG_EVOLVEIDS:
			if newValue == evolveList:
				minEvolve = evolveList
				break
		if not minEvolve:
			return
		waData = WonderfulData.GetWAData(WONDEFUL_INDEX_16)
		#记录数量加一
		waData[minEvolve] = nowNum = waData.get(minEvolve, 0) + 1
		NumRewardDict = wad.WONDER_MOUNTTOG_NUM.get(minEvolve)
		rewardId = NumRewardDict.get(nowNum)
		if not rewardId:
			return
		actId = EnumWonderType.Wonder_Act_MountTog
		SetActIdR(actId, rewardId)
		roles_data = cRoleMgr.GetAllRole()
		for role in roles_data:
			CheckReward(role, actId, rewardId)
					
def RoleDayClear(role, param):
	'''
	玩家每日清理
	@param role:
	@param param:
	'''
	clearRoleData(role)

def clearRoleData(role):
	fill = role.GetI32(EnumInt32.WonderSingleFill)
	if fill:#单笔充值
		role.SetI32(EnumInt32.WonderSingleFill, 0)
	totalFill = role.GetI32(EnumInt32.WonderTotalFill)
	if totalFill:#每日累计充值
		role.SetI32(EnumInt32.WonderTotalFill, 0)
	WonderRoleGem = role.GetI16(EnumInt16.WonderRoleGem)
	if WonderRoleGem:#每日购买宝石数
		role.SetI16(EnumInt16.WonderRoleGem, 0)
	WonderRoleTarot = role.GetI16(EnumInt16.WonderRoleTarot)
	if WonderRoleTarot:#每日高级占卜数
		role.SetI16(EnumInt16.WonderRoleTarot, 0)
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	dayList = roleObj[2]
	if dayList:
		roleObj[2] = set()
	WingCultivateTimes = role.GetI32(EnumInt32.WingCultivateTimes)
	if WingCultivateTimes:#每日翅膀培养次数
		role.SetI32(EnumInt32.WingCultivateTimes, 0)
	PetCultivateTimes = role.GetI32(EnumInt32.PetCultivateTimes)
	if PetCultivateTimes:#每日宠物培养次数
		role.SetI32(EnumInt32.PetCultivateTimes, 0)

def AfterChangeUnbindRMB_S(role, param):
	#监听系统赠送神石数值变化
	oldValue, newValue = param
	if newValue > oldValue:
		return
	value = oldValue - newValue
	SetActUnRMBTog(value)
	
def SetActUnRMBTog(value):
	RightActId = 0
	for actId in EnumWonderType.WonderActUnRMBTogList:
		if GetActState(actId) == 1:
			RightActId = actId
			break
	if not RightActId:#所有活动都未开启
		return
	#增加全服累计消费
	RMBData = WonderfulData.GetWAData(WONDEFUL_INDEX_18)
	RMBData += value
	WonderfulData.SetWAData(WONDEFUL_INDEX_18, RMBData)	
	totalRMB = RMBData
	rewardList = []
	totalRMBDict = wad.WONDER_TOTAL_RMB.get(RightActId)#遍历检测是否达到激活的神石数
	for cnt, rewardId in totalRMBDict.iteritems():
		if cnt <= totalRMB:
			rewardList.append(rewardId)
	if not rewardList:
		return
	SetActIdR(RightActId, rewardList)
	roles_data = cRoleMgr.GetAllRole()
	for crole in roles_data:#通知在线玩家领奖
		for rewardId in rewardList:
			state = CheckReward(crole, RightActId, rewardId)
			if state:
				break
	
def AfterChangeUnbindRMB(role, param):
	#监听Q点神石数值变化
	oldValue, newValue = param
	if newValue > oldValue:
		#单笔神石数
		SingleFill = newValue - oldValue
		roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
		gettedList = roleObj[2]
		role.IncI32(EnumInt32.WonderTotalFill, SingleFill)
		totalFill = role.GetI32(EnumInt32.WonderTotalFill)
		#==============每日累计购神石活动================
		RMBTog_ActId = 0
		if Environment.EnvIsRU():
			enumList = EnumWonderType.WonderActRMBTogList_2
			wonderTotalFill = wad.WONDER_TOTAL_FILL_2
		else:
			enumList = EnumWonderType.WonderActRMBTogList
			wonderTotalFill = wad.WONDER_TOTAL_FILL
		for actId in enumList:
			if 1 == GetActState(actId):
				RMBTog_ActId = actId
				break
		if RMBTog_ActId:#每日累计充值
			totalReward = []
			RMBTogDict = wonderTotalFill.get(RMBTog_ActId)
			for total, rewardId in RMBTogDict.iteritems():
				if total <= totalFill:
					totalReward.append(rewardId)
			if totalReward:
				SetActIdR(RMBTog_ActId, totalReward)
				for rewardId in totalReward:
					if rewardId not in gettedList:
						role.SendObj(Wonder_Can_Reward, 1)
						break
		#================狂欢充值抢好礼===========
		FillLiBaoId = EnumWonderType.Wonder_Act_FillLiBao
		if 1 == GetActState(FillLiBaoId):
			FillliBao_reward = []
			for unbind, Fillreward in wad.WONDER_FILLLIBAO_REWARD.iteritems():
				if unbind <= totalFill:
					FillliBao_reward.append(Fillreward)
			if FillliBao_reward:
				SetActIdR(FillLiBaoId, FillliBao_reward)
				for FillId in FillliBao_reward:
					if FillId not in gettedList:
						role.SendObj(Wonder_Can_Reward, 1)
						break
		#===============购神石送布拉祖卡============
		if 1 == GetActState(EnumWonderType.Wonder_Act_SendCard):
			SendCard_reward = []
			for unrmb, sendrewrd in wad.WONDER_SENDCARD_REWARD.iteritems():
				if unrmb <= totalFill:
					SendCard_reward.append(sendrewrd)
			if SendCard_reward:
				SetActIdR(EnumWonderType.Wonder_Act_SendCard, SendCard_reward)
				for cardId in SendCard_reward:
					if cardId not in gettedList:
						role.SendObj(Wonder_Can_Reward, 1)
						break
		#===============购神石送黄金钥匙============
		if 1 == GetActState(EnumWonderType.Wonder_Act_SendKey):
			Sendkey_reward = []
			for fill, reward in wad.WONDER_SEND_KEY_DICT.iteritems():
				if fill <= totalFill:
					Sendkey_reward.append(reward)
			if Sendkey_reward:
				SetActIdR(EnumWonderType.Wonder_Act_SendKey, Sendkey_reward)
				for reward in Sendkey_reward:
					if reward not in gettedList:
						role.SendObj(Wonder_Can_Reward, 1)
						break
		#===============购神石送圣器============
		if 1 == GetActState(EnumWonderType.Wonder_Act_SendHallows):
			SendHallows_reward = []
			for fill, reward in wad.WONDER_SEND_HALLOWS_DICT.iteritems():
				if fill <= totalFill:
					SendHallows_reward.append(reward)
			if SendHallows_reward:
				SetActIdR(EnumWonderType.Wonder_Act_SendHallows, SendHallows_reward)
				for reward in SendHallows_reward:
					if reward not in gettedList:
						role.SendObj(Wonder_Can_Reward, 1)
						break
		#============单笔购神石送改名活动===========
		if 1 == GetActState(EnumWonderType.Wonder_Act_ChangeName):
			#单笔购神石送改名活动
			gettedList = roleObj[2]
			reward = wad.SINGAL_FILL_CHANGE_NAME
			cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(reward)
			if cfg:
				if cfg.TotalFill <= totalFill and reward not in gettedList:
					role.SendObj(Wonder_Can_Reward, 1)
		#===============充值狂人=======================
		if 1 == GetActState(EnumWonderType.Wonder_Act_FillRank):
			fillData = WonderfulData.GetWAData(WONDEFUL_INDEX_21)
			roleId = role.GetRoleID()
			actId = EnumWonderType.Wonder_Act_FillRank
			if actId not in fillData:
				fillData[actId] = {}
			ActData = fillData.get(actId)
			#这里记录玩家的总充值数
			if roleId not in ActData:#第一次充值
				ActData[roleId] = [role.GetRoleName(), SingleFill, roleId]
			else:
				#不是第一次
				tataoFill = ActData.get(roleId)[1]
				ActData[roleId] = [role.GetRoleName(), tataoFill + SingleFill, roleId]
		#================单笔神石返利(北美)===============
		if Environment.EnvIsNA():
			if 1 == GetActState(EnumWonderType.Wonder_Act_OnceRMB):
				rewardId = 0
				for r, rId in wad.ONCE_RMB_REWARD_DICT.iteritems():
					if SingleFill == r:
						rewardId = rId
						break
				rewardConfig = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
				if rewardConfig:
					#发邮件
					Mail.SendMail(role.GetRoleID(), GlobalPrompt.WONDERFUL_ONCE_RMB_MAIL_TITLE, GlobalPrompt.WONDERFUL_ONCE_RMB_MAIL_SENDER, GlobalPrompt.WONDERFUL_ONCE_RMB_MAIL_CONTENT % (Time.DateTime2String(cDateTime.Now()), SingleFill), rewardConfig.rewardItem, money = rewardConfig.money)
		#================充值送英雄宝珠=============
		if 1 == GetActState(EnumWonderType.Wonder_Act_HeroGem):
			cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(EnumWonderType.Wonder_Act_HeroGem)
			if cfg:
				for reward in cfg.rewardList:
					if reward not in gettedList and CanGetReward(role, reward):
						role.SendObj(Wonder_Can_Reward, 1)
						break
		#================单笔购神石===============
		#以下是只取当日单笔充值的最高神石，小于就直接返回了
		if role.GetI32(EnumInt32.WonderSingleFill) < SingleFill:
			role.SetI32(EnumInt32.WonderSingleFill, SingleFill)
		else:
			return
		#单笔购神石活动
		state = GetActState(EnumWonderType.Wonder_Act_SingalFill)
		if state != 1:
			return
		rewards = []
		for fill, rewardId in wad.WONDER_SINGELFILL_DICT.iteritems():
			if fill <= SingleFill:
				rewards.append(rewardId)
		if not rewards:
			return
		SetActIdR(EnumWonderType.Wonder_Act_SingalFill, rewards)
		for rewardId in rewards:
			if rewardId not in gettedList:
				role.SendObj(Wonder_Can_Reward, 1)
				return
	else:
		value = oldValue - newValue
		SetActUnRMBTog(value)
		
def HallowsStart(*param):
	_, circularType = param
	if circularType != CircularDefine.CA_SendHallows:
		return
	global HALLOWS_IS_START
	if HALLOWS_IS_START is True:
		print "GE_EXC, SendHallows has already been started"
		return
	HALLOWS_IS_START = True	
	
def HallowsEnd(*param):
	_, circularType = param
	if circularType != CircularDefine.CA_SendHallows:
		return
	global HALLOWS_IS_START
	if HALLOWS_IS_START is False:
		print "GE_EXC, SendHallows has already been ended"
		return
	HALLOWS_IS_START = False
	
def SyncRoleOtherData(role, param):
	if role.GetLevel() < wad.WONDERFUL_ACT_LEVEL:
		return
	#获取玩家可以领取的奖励
	canDict = GetCanGetID(role)
	if canDict:
		role.SendObj(Wonder_Can_Reward, 1)
	role.SendObj(Wonder_Send_Process, cProcess.ProcessID)
	
def AfterLogin(role, param):
	'''
	玩家登录后
	@param role:
	@param param:
	'''
	role.SendObj(Wonder_Send_Process, cProcess.ProcessID)
	if role.GetLevel() < wad.WONDERFUL_ACT_LEVEL:
		return
	#这里做些老服处理(宠物大师活动开启，并且全服没有激活奖励)
	if GetActState(EnumWonderType.Wonder_Act_Pet) and \
		EnumWonderType.Wonder_Act_Pet not in WonderfulData.GetWAData(WONDEFUL_INDEX_11):
		IncPetStarNum(role)
	#获取玩家可以领取的奖励
	canDict = GetCanGetID(role)
	if canDict:
		role.SendObj(Wonder_Can_Reward, 1)
	
def AfterLevelUp(role, param):
	'''
	玩家升级之后
	@param role:
	@param param:
	'''
	actState = GetActState(EnumWonderType.Wonder_Act_Level)#玩家升级，检测疯狂冲级活动是否开启
	if 1 != actState:
		return
	level = role.GetLevel()
	wonder_list = role.GetObj(EnumObj.Wonder_Reward_List)
	gettedList = wonder_list[1]
	state = False
	for elvel, rewardId in wad.ENUM_LEVEL_DICT.iteritems():
		if elvel <= level:
			SetActIdR(EnumWonderType.Wonder_Act_Level, rewardId)
			Levelstate = CanGetReward(role, rewardId)
			if Levelstate:
				if rewardId not in gettedList:
					state = True
	if state:
		role.SendObj(Wonder_Can_Reward, 1)
		return

def AfterSetKaiFuTime(param1, param2):
	'''
	重新设置开服时间
	@param param1:
	@param param2:
	'''
	with WonderfulClear:
		#将坐骑争霸数据清空
		WonderfulData.SetWAData(WONDEFUL_INDEX_10, {})
		#将圣城争霸数据清空
		WonderfulData.SetWAData(WONDEFUL_INDEX_9, [])
		#首战、再战竞技清空
		WonderfulData.SetWAData(WONDEFUL_INDEX_8, {})
		#战力绝伦清空
		WonderfulData.SetWAData(WONDEFUL_INDEX_14, {})
		#公会竞赛清空
		WonderfulData.SetWAData(WONDEFUL_INDEX_13, {})
		#清空荣耀之战数据
		WonderfulData.SetWAData(WONDEFUL_INDEX_19, [])
		WGD = WonderfulData.GetWAData
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderDisAct, (WGD(WONDEFUL_INDEX_8), WGD(WONDEFUL_INDEX_9), WGD(WONDEFUL_INDEX_10), \
																WGD(WONDEFUL_INDEX_13), WGD(WONDEFUL_INDEX_14), WGD(WONDEFUL_INDEX_19), cDateTime.Now()))

def AfterMarry(role, param):
	#玩家结婚后
	MarryCnt = WorldData.WD[EnumSysData.MarryCnt]
	IsHefu = WorldData.IsHeFu()
	rewardId = 0
	if IsHefu:
		rewardId = wad.MARRY_CNT_DICT1.get(MarryCnt)
	else:
		rewardId = wad.MARRY_CNT_DICT.get(MarryCnt)
	if not rewardId:
		return
	roles_data = cRoleMgr.GetAllRole()
	for crole in roles_data:
		if IsHefu:
			CheckReward(crole, EnumWonderType.Wonder_Act_MarryTog2, rewardId)
		else:
			CheckReward(crole, EnumWonderType.Wonder_Act_MarryTog, rewardId)

def SetVIPData():
	global IS_OPERATION
	if not IS_OPERATION:
		return
	DoHefuEvent()
	#将标准置为False
	IS_OPERATION = False
	
def AfterSystemHeFu(param1, param2):
	#系统合服后
	#高级vip返利处理
	global IS_OPERATION
	if not WonderfulData.WA_BT.returnDB:
		IS_OPERATION = True
	else:
		DoHefuEvent()

def DoHefuEvent():
	#一些合服后的操作
	#高级vip返利处理
	with WonderfulHefu:
		#清理11和12的相关数据
		WonderfulData.SetWAData(WONDEFUL_INDEX_11, {})
		WonderfulData.SetWAData(WONDEFUL_INDEX_12, {})
		#重新对12进行数据写入
		vipData = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
		rewardData = WonderfulData.GetWAData(WONDEFUL_INDEX_12)
		if vipData:
			for vip, data in vipData.iteritems():
				rewardList = wad.WONDER_HIGHVIP_REWARD.get(vip)
				if not rewardList:
					continue
				#获取新老该VIP总人数
				totalNum = data.get(1, 0) + data.get(3, 0)
				for rewardId in rewardList:
					rewardData[rewardId] = totalNum
		#清空充值狂人记录
		WonderfulData.SetWAData(WONDEFUL_INDEX_21, {})
		#清空公会争霸
		WonderfulData.SetWAData(WONDEFUL_INDEX_22, {})
		#清空战力排行
		WonderfulData.SetWAData(WONDEFUL_INDEX_23, {})
		#清除一些合服后继承的活动记录
		ClearData()
		#这里将合服活动7日登陆的奖励激活
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(EnumWonderType.Wonder_Act_SevenDay)
		if not cfg:
			return
		if not cfg.rewardList:
			return
		SetActIdR(EnumWonderType.Wonder_Act_SevenDay, cfg.rewardList)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderHefu)
		
		
def AfterRoleHeFu(role, param):
	#合服后玩家身上做的处理
	#需要清理一些活动已领奖的奖励ID，因为这些活动在合服后需要重新开启
	#只清除EnumObj.Wonder_Reward_List中key 1的奖励，即一次性奖励
	
	#获取玩家已领取的数据
	roleObj = role.GetObj(EnumObj.Wonder_Reward_List)
	rewardData = roleObj.get(1)
	if not rewardData:
		return
	
	WBD = WonderfulActConfig.WONDERFUL_BASE_DICT.get
	for actId in EnumWonderType.AFTER_HEFU_ACT_LIST:
		cfg = WBD(actId)
		if not cfg:
			print "GE_EXC,can not find actId(%s) in Eve_AfterRoleHeFu" % actId
			continue
		rewardList = cfg.rewardList #该活动对应的奖励列表
		for rewardId in rewardList:
			if rewardId in rewardData:#奖励ID已领取的话就清除
				rewardData.remove(rewardId)
				
	ClearForeverData(role)
	
def ClearForeverData(role):
	role.SetI32(EnumInt32.PetEvoTimes, 0)
	role.SetI32(EnumInt32.FashionUpStarTimes, 0)
	role.SetI32(EnumInt32.FashionUpOrderTimes, 0)
	role.SetI32(EnumInt32.StarGirlLevelUpTimes, 0)
	role.SetI32(EnumInt32.StarGirlStarTimes, 0)
	role.SetI32(EnumInt32.DragonVeinLevelTimes, 0)
	role.SetI32(EnumInt32.DragonVeinEvoTimes, 0)
	role.SetI32(EnumInt32.TitleLevelUpTimes, 0)
#============================================================================================
def GetGetedReward(role, cfg):
	'''
	获取玩家某活动已经领取的奖励
	@param cfg:
	'''
	rewardList = cfg.rewardList
	if not rewardList:
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	getedList = set()
	if cfg.dayfresh:
		getedList = wonderObj[2]
	else:
		getedList = wonderObj[1]
	GetedList = []
	for rewardId in rewardList:
		if rewardId in getedList:
			GetedList.append(rewardId)
	return GetedList

def GetActRewards(actId, rewardId):
	'''
	检测某奖励ID是否在某活动中
	@param actId:
	'''
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		return
	rewardList = cfg.rewardList
	for Id in rewardList:
		if Id == rewardId:
			return True
	return False

def CheckHeroFull(role):
	#英雄满了
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	if not roleHeroMgr:
		return
	if roleHeroMgr.IsHeroFull():
		role.Msg(2, 0, GlobalPrompt.FULL_HERO_MSG)
		return False
	return True

def GetReward(role, cfg, actId, backId):
	'''
	给玩家发奖励
	'''
	with WonderfulActReward:
		role.Msg(2, 0, GlobalPrompt.Purgatory_Revive_Success)
		if cfg.rewardItem:
			for item in cfg.rewardItem:
				role.AddItem(*item)
				role.Msg(2, 0, GlobalPrompt.Item_Tips % (item[0], item[1]))
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % cfg.bindRMB)
		if cfg.money:
			role.IncMoney(cfg.money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % cfg.money)
		if cfg.rewardTarot:#命魂
			role.AddTarotCard(cfg.rewardTarot, 1)
			role.Msg(2, 0, GlobalPrompt.Tarot_Tips % (cfg.rewardTarot, 1))
		if cfg.rewardHero:#英雄
			role.AddHero(cfg.rewardHero)
			herocfg = HeroConfig.Hero_Base_Config.get(cfg.rewardHero)
			if herocfg:
				name = herocfg.name
				role.Msg(2, 0, GlobalPrompt.ADD_HERO_MSG % name)
		if cfg.rewardTiLi:#体力
			role.IncTiLi(cfg.rewardTiLi)
			role.Msg(2, 0, GlobalPrompt.TiLi_Tips % cfg.rewardTiLi)
		if cfg.UnbindRMB_S:#神石
			role.IncUnbindRMB_S(cfg.UnbindRMB_S)
			role.Msg(2, 0, GlobalPrompt.UnBindRMB_Tips % cfg.UnbindRMB_S)
		if cfg.Reputation:#声望
			role.IncReputation(cfg.Reputation)
			role.Msg(2, 0, GlobalPrompt.Reputation_Tips % cfg.Reputation)
		if cfg.TaortHP:#增加命力
			role.IncI32(EnumInt32.TaortHP, cfg.TaortHP)
			role.Msg(2, 0, GlobalPrompt.TaortHP_Tips % cfg.TaortHP)
		name = "actId = %d" % actId
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveWonderReward, name)
	if actId == EnumWonderType.Wonder_Act_VIP or actId == EnumWonderType.Wonder_Act_SeniorVIP:
		canList = GetCanGetIDByAct(role, actId)
		if cfg.rewardId in canList:
			role.CallBackFunction(backId, [actId, cfg.rewardId, 1])
		else:
			role.CallBackFunction(backId, [actId, cfg.rewardId, 0])
	else:
		role.CallBackFunction(backId, [actId, cfg.rewardId, 0])
	canDict = GetCanGetID(role)
	if actId not in canDict:
		role.SendObj(Wonder_Can_Reward_Dict, canDict.keys())
#=============================高级VIP返利========================
def OpenWonderHighVIP(param):
	'''
	打开高级VIP返利界面
	@param role:
	@param param:
	'''
	role, cfg = param
	actId = cfg.actId
	VIPList = wad.WONDER_ACTID_VIP_DICT.get(actId)
	VIPData = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
	vipNum = {}
	for vip in VIPList:
		vipDict = VIPData.get(vip, {})
		old_num = vipDict.get(1,0)
		new_num = vipDict.get(3,0)
		vipNum[vip] = old_num + new_num
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, vipNum])
	
def GetWonderHighVIP(param):
	'''
	获取高级VIP返利
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.VIPNum:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not WorldData.IsHeFu():#该活动是合服后才开启的
		return
	vip, _ = cfg.VIPNum
	VIPData = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
	if not VIPData:
		return
	VIPDict = VIPData.get(vip, {})
	nameList = VIPDict.get(2)	#获取玩家名数据

	#玩家已领取的数据
	vipobj = role.GetObj(EnumObj.Wonder_Vip_Reward_Dict)
	viptimes = vipobj.get(1)
	getedTimes = viptimes.get(rewardId, 0)#玩家已经领取的次数
	
	oldNum = VIPDict.get(1, 0)#合服后的已有的vip数量
	newNum = VIPDict.get(3, 0)#合服后新增的vip数量

	if getedTimes >= oldNum + newNum:#已经全领取了
		return

	viptimes[rewardId] = viptimes.get(rewardId,0) + 1
	GetReward(role, cfg, actId, backId)
	
	if getedTimes >= oldNum:
		remainNum = getedTimes - oldNum
		if len(nameList) > remainNum:
			name = nameList[remainNum]
			reward = cfg.rewardItem
			coding, cnt = reward[0][0], reward[0][1]
			cRoleMgr.Msg(1, 0, GlobalPrompt.WONDERFUL_GET_REWARD % (role.GetRoleName(),coding, cnt, name))
#=============================爱宠齐成长==========================
def OpenWonderTogPet(param):
	'''
	打开爱宠齐成长界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	total_num = 0	#显示全服培养次数
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_25)
	if WAData:
		total_num = WAData.get(cfg.actId, 0)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [total_num]])

def GetWonderTogPet(param):
	'''
	获取爱宠齐成长奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:#奖励已领取
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:#vip等级不够
		return
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_25)
	if not WAData:
		return
	TogPetTimes = WAData.get(actId, 0)
	if TogPetTimes < cfg.TogPetTimes:#全服培养次数不足
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#=============================家有小宠快成长=======================
def OpenWonderCulPet(param):
	'''
	打开家有小宠快成长界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderCulPet(param):
	'''
	获取家有小宠快成长奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:#奖励已领取
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetI32(EnumInt32.PetCultivateTimes) < cfg.PetTimes:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#=============================一起来飞翔===========================
def OpenWonderTogWing(param):
	'''
	打开一起来飞翔界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	total_num = 0	#显示全服培养次数
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_24)
	if WAData:
		total_num = WAData.get(cfg.actId, 0)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [total_num]])

def GetWonderTogWing(param):
	'''
	获取一起来飞翔奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:#奖励已领取
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:#vip等级不够
		return
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_24)
	if not WAData:
		return
	TogWingTimes = WAData.get(actId, 0)
	if TogWingTimes < cfg.TogWingTimes:#全服培养次数不足
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#=============================天天爱飞翔===========================
def OpenWonderCulWing(param):
	'''
	天天爱飞翔
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])

def GetWonderCulWing(param):
	'''
	获取天天爱飞翔奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:#奖励已领取
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetI32(EnumInt32.WingCultivateTimes) < cfg.WingTimes:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#==============================战力排行============================
def OpenWonderZDLRank(param):
	'''
	打开战力排行界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	ZDLRank = WonderfulData.GetWAData(WONDEFUL_INDEX_23)
	select_list = []
	if not ZDLRank:
		#没有数据，直接获取战斗力排行榜，排序后取前10
		sys_data = SystemRank.ZR.GetData()
		data_list = sys_data.values()
		data_list.sort(key = lambda x : (x[2], x[1]), reverse = True)
		select_list = data_list[0:10]
	else:
		select_list = ZDLRank.get(cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, select_list])
	
def GetWonderZDLRank(param):
	'''
	获取战力排行奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	canState = CheckZDLRankReward(role,actId, rewardId)
	if not canState:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
def CheckZDLRankReward(role, actId, rewardId):
	#检查战力排行奖励
	state = GetActState(actId)
	if state == -1 or state == 0:#活动结束或未开启
		return False
	
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:#已领取奖励
		return False
	
	ZDLObj = WonderfulData.GetWAData(WONDEFUL_INDEX_23)
	if not ZDLObj:
		return False
	rankData = ZDLObj.get(actId)
	if not rankData:#没有该活动对应的数据
		return
	#rankData格式 【【玩家名，玩家ID】，【玩家名，玩家ID】，。。。】
	roleId = role.GetRoleID()
	if rewardId == wad.FIRST_ZDL_REWARD:#第一名奖励
		if roleId != rankData[0][1]:
			return False
	elif rewardId == wad.SECOND_ZDL_REWARD:#第二名奖励
		if len(rankData) < 2:
			return False
		if roleId != rankData[1][1]:
			return False
	elif rewardId == wad.THIRD_ZDL_REWARD:#第三名奖励
		if len(rankData) < 3:
			return False
		if roleId != rankData[2][1]:
			return False
	elif rewardId == wad.FOUR_ZDL_REWARD:#4-5名奖励
		four_five_data = rankData[3:5]
		if not four_five_data:#没有4-5名的数据
			return False
		roleId_list = []
		for newData in four_five_data:
			roleId_list.append(newData[1])
		if roleId not in roleId_list:
			return False
	elif rewardId == wad.FIVE_ZDL_REWARD:#6-10名奖励
		six_data = rankData[5:10]
		if not six_data:#没有6-10名的数据
			return False
		roleId_list = []
		for newData in six_data:
			roleId_list.append(newData[1])
		if roleId not in roleId_list:
			return False
	return True

def SetZDLRankDB(param):
	#战力排行结算
	actId = param
	
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,Wonderful can not find actId(%s) in cfg"
		return
	#获取战力榜前10数据
	rank_list = GetZDLRank()
	if not rank_list:
		print "GE_EXC,can find SetZDLRankDB in wonderful"
		return
	rank_list = rank_list[0:10]
	with WonderfulZDLRank:
		ZDLDate = WonderfulData.GetWAData(WONDEFUL_INDEX_23)
		if actId not in ZDLDate:
			ZDLDate[actId] = []
		
		roleId_list = []
		##保存前10名玩家的姓名和玩家ID,在此之前已经排过序
		for zdlData in rank_list:
			ZDLDate[actId].append([zdlData[0],zdlData[4]])
			roleId_list.append(zdlData[4])
		#将奖励存储
		SetActIdR(actId, cfg.rewardList)
		#通知这些玩家可以领奖
		for roleId in roleId_list:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
			role.SendObj(Wonder_Can_Reward, 1)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderZDLRankDB, (ZDLDate.get(actId), cDateTime.Now()))
#==============================公会争霸============================
def OpenWonderUnionRank(param):
	'''
	打开公会争霸界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderUnionRank(param):
	'''
	获取公会争霸奖励，这里获胜公会会在21.59分清零，所以需在此之前领取
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	#检测奖励是否能领取
	state = CheckUnionRankReward(role, actId, rewardId)
	if not state:
		return 
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)

def CheckUnionRankReward(role, actId, rewardId):
	#检查玩家是否能领将
	if GetActState(actId) != 1 and GetActState(actId) != 2:#只能在活动进行中和领奖期间领取
		return False
	
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:#已领取
		return False
	
	unionId = role.GetUnionID()
	if not unionId:#没有公会
		return False
	WAData = WonderfulData.GetWAData(WONDEFUL_INDEX_22)
	if not WAData:#没有相关数据
		return False
	unionDataId = WAData.get(actId)
	if not unionDataId:#没有相关数据
		return False
	if unionId != unionDataId:#获胜的公会不是该玩家的公会
		return False
	
	return True
#==============================充值狂人============================
def OpenWonderFillRank(param):
	'''
	打开充值狂人界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	sendData = []
	fillRank = WonderfulData.GetWAData(WONDEFUL_INDEX_21)
	if fillRank:#取充值前10名的数据
		resultData = fillRank.get(1, [])
		if resultData:#数据已结算
			sendData = resultData
		else:
			fillData = fillRank.get(EnumWonderType.Wonder_Act_FillRank)
			sortData = sorted(fillData.values(), key = lambda x:x[1], reverse = True)
			sendData = sortData[0:10]
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, sendData])

def GetWonderFillRank(param):
	'''
	获取充值狂人奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	#检测奖励是否能领取
	state = CheckFillRank(role, actId, rewardId)
	if not state:
		return 
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
def SortFillRank(param):
	#对充值狂人进行一次排序，保存前10名玩家的相关数据
	actId = param
	fillRank = WonderfulData.GetWAData(WONDEFUL_INDEX_21)
	if not fillRank:
		return
	fillData = fillRank.get(EnumWonderType.Wonder_Act_FillRank)
	if not fillData:
		return
	#根据神石数进行从大到小排序
	sortList = sorted(fillData.values(), key = lambda x:x[1], reverse = True)
	saveList = sortList[0:10]
	fillRank[1] = saveList
	#激活奖励
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	rewardList = cfg.rewardList
	SetActIdR(actId, rewardList)
	#通知现在达要求的玩家
	for roledata in saveList:
		roleId = roledata[2]
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if role:
			role.SendObj(Wonder_Can_Reward, 1)
		
def CheckFillRank(role, actId, rewardId):
	#检查是否能领奖
	state = GetActState(actId)
	if state == -1 or state == 0:#活动结束或未开启
		return False
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:#已领取
		return
	
	fillRank = WonderfulData.GetWAData(WONDEFUL_INDEX_21)
	if not fillRank:
		return False
	sortData = fillRank.get(1)
	if not sortData:#格式：[[玩家名， 充值数， 玩家ID]，...]
		return False
	roleId = role.GetRoleID()
	if rewardId == wad.FILLRANK_INDEX_1:#第一名奖励
		if roleId != sortData[0][2]:
			return False
		if Environment.EnvIsNA():
			if sortData[0][1] < wad.NA_MIN_FILLNUM:#充值数少于规定的最小值
				return False
		else:
			if sortData[0][1] < wad.MIN_FILLNUM:#充值数少于规定的最小值
				return False
	elif rewardId == wad.FILLRANK_INDEX_2:#第二名奖励
		if len(sortData) < 2:#人数不足
			return False
		if roleId != sortData[1][2]:
			return False
		if Environment.EnvIsNA():
			if sortData[1][1] < wad.NA_MIN_FILLNUM:#充值数少于规定的最小值
				return False
		else:
			if sortData[1][1] < wad.MIN_FILLNUM:#充值数少于规定的最小值
				return False
	elif rewardId == wad.FILLRANK_INDEX_3:#第三名奖励
		if len(sortData) < 3:#人数不足
			return False
		if roleId != sortData[2][2]:
			return False
		if Environment.EnvIsNA():
			if sortData[2][1] < wad.NA_MIN_FILLNUM:#充值数少于规定的最小值
				return False
		else:
			if sortData[2][1] < wad.MIN_FILLNUM:#充值数少于规定的最小值
				return False
	elif rewardId == wad.FILLRANK_INDEX_4:#1-10名奖励
		roleList = []
		for data in sortData:
			roleList.append(data[2])
		if roleId not in roleList:
			return False
	else:
		return False
	return True
#==============================7日签到送豪礼========================
def OpenWonderSevenDay(param):
	'''
	打开7日签到送豪礼界面
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])

def GetWonderSevenDay(param):
	'''
	获取7日签到送豪礼
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:#奖励已领取
		return
	if GetActState(actId) != 1:#只在开启时才能领取
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if WorldData.GetHeFuDay() != cfg.HefuDay:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#=============================一起来结婚============================
def OpenWonderMarryTog(param):
	'''
	打开一起来结婚界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WorldData.WD[EnumSysData.MarryCnt]]])

def GetWonderMarryTog(param):
	'''
	获取一起来结婚奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return	
	if not cfg.MarryCnt:
		print "GE_EXC, MarryCnt is None in GetWonderMarryCntReward"
		return
	if cfg.MarryCnt > WorldData.WD[EnumSysData.MarryCnt]:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#=========================情比金坚==============================
def OpenWonderMarryRing(param):
	'''
	打开情比金坚界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderMarryRing(param):
	'''
	获取情比金坚奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	getBool = CheckMarryRing(role, actId, rewardId)
	if not getBool:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)	
	
def GetMarryRingRank():
	'''
	获取婚戒排行榜
	'''
	#先跟新排行榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateWeddingRing(role)
	sys_data = SystemRank.WR.GetData()
	data_list = sys_data.values()
	data_list.sort(key = lambda x : (x[1], x[2]), reverse = True)
	select_list = data_list[0:20]
	return select_list

def SetMarryRingDB(param):
	'''
	婚戒排行榜结算
	'''
	actId = param
	rank_list = GetMarryRingRank()
	if not rank_list:
		print "GE_EXC,can find MarryRing in wonderful"
		return
	first_data = rank_list[0:1]		#第一名
	second_data = rank_list[1:2]	#第二名
	third_data = rank_list[2:3]
	four_data = rank_list[3:20]	#第三到20名
	RingDate = {}
	with WonderfulRing:
		if first_data:
			RingDate[1] = set()
			if len(first_data[0]) == 6:
				RingDate[1].add(first_data[0][4])
				if first_data[0][5]:
					RingDate[1].add(first_data[0][5])
		if second_data:
			RingDate[2] = set()
			if len(second_data[0]) == 6:
				RingDate[2].add(second_data[0][4])
				if second_data[0][5]:
					RingDate[2].add(second_data[0][5])
		if third_data:
			RingDate[3] = set()
			if len(third_data[0]) == 6:
				RingDate[3].add(third_data[0][4])
				if third_data[0][5]:
					RingDate[3].add(third_data[0][5])
		if four_data:
			RingDate[4] = set()
			for data in four_data:
				if len(data) < 6:
					break
				RingDate[4].add(data[4])
				if data[5]:
					RingDate[4].add(data[5])
		#存DB
		WonderfulData.SetWAData(WONDEFUL_INDEX_20, RingDate)
		
		#将奖励存储
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,Wonderful can not find actId(%s) in SetMarryRingDB"
			return
		SetActIdR(EnumWonderType.Wonder_Act_MarryRing, cfg.rewardList)
		#通知在线达要求的玩家
		SendList = []
		if RingDate.has_key(1):
			SendList += RingDate[1]
		if RingDate.has_key(2):
			SendList += RingDate[2]
		if RingDate.has_key(3):
			SendList += RingDate[3]
		if RingDate.has_key(4):
			SendList += RingDate[4]
		SendList = set(SendList)
		for roleId in SendList:
			onrole = cRoleMgr.FindRoleByRoleID(roleId)
			if not onrole:
				continue
			onrole.SendObj(Wonder_Can_Reward, 1)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderRingDB, (RingDate, cDateTime.Now()))

def CheckMarryRing(role, actId, rewardId):
	'''
	检测情比金坚
	@param role:
	@param actId:
	@param rewardId:
	'''
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return False
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return False
	
	RingDate = WonderfulData.GetWAData(WONDEFUL_INDEX_20)
	roleId = role.GetRoleID()
	for key, reward in wad.MARRY_REWARD_DICT.iteritems():
		if rewardId == reward:
			if 1 == key:#第一类奖励
				if roleId not in RingDate.get(1, []):
					return False
			elif 2 == key:#第二类奖励
				if roleId not in RingDate.get(2, []):
					return False
			elif 3 == key:#第三类奖励
				if roleId not in RingDate.get(3, []):
					return False
			elif 4 == key:#第四类奖励
				if roleId not in RingDate.get(4, []):
					return False
			else:
				state = GetActState(EnumWonderType.Wonder_Act_MarryRing)
				if state != 1: return False
				if role.GetI16(EnumInt16.WeddingRingID) < cfg.RingLevel:
					return False
			break
	return cfg
#=========================狂欢充值抢好礼,购神石送布拉祖卡,充值送黄金钥匙=========================
def OpenWonderFillLiBao(param):
	'''
	打开狂欢充值抢好礼,购神石送布拉祖卡,充值送黄金钥匙界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])

def GetWonderFillLiBao(param):
	'''
	获取狂欢充值抢好礼,购神石送布拉祖卡,充值送黄金钥匙
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	if GetActState(actId) != 1:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.TotalFill:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TotalFill," % rewardId
		return
	if role.GetI32(EnumInt32.WonderTotalFill) < cfg.TotalFill:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#==============================荣耀之战============================
def OpenWonderGloryWar(param):
	'''
	打开荣誉之战界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	roleData = WonderfulData.GetWAData(WONDEFUL_INDEX_19)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, roleData])
	
def GetWonderGloryWar(param):
	'''
	获取荣耀之战奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return	
	canState = CheckGloryWarReward(role, actId, rewardId)
	if not canState:
		return
	if cfg.rewardHero:
		if not CheckHeroFull(role):
			return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
def CheckGloryWarReward(role, actId, rewardId):
	sysRoleId = CheckGlory(WonderfulData.GetWAData(WONDEFUL_INDEX_19))
	if not sysRoleId:
		return False
	if role.GetRoleID() != sysRoleId:
		return False
	return True
#==============================宠物大师============================
def OpenWonderPet(param):
	'''
	打开宠物大师界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderPet(param):
	'''
	获取宠物大师奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.PetNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need PetNum" % rewardId
		return
	star, num = cfg.PetNum
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	petDict = petMgr.pet_dict 
	if not petDict:
		return
	petNum = 0
	for pet in petDict.values():
		if pet.star >= star:
			petNum += 1
	if petNum < num:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#==============================单笔充值送改名卡=====================
def OpenWonderChangeName(param):
	'''
	打开单笔充值送改名卡面板
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderChangeName(param):
	'''
	获取单笔充值送改名卡奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.TotalFill:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TotalFill," % rewardId
		return
	if role.GetI32(EnumInt32.WonderTotalFill) < cfg.TotalFill:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
#==============================充值送英雄宝珠=====================
def OpenWonderHeroGem(param):
	'''
	打开充值送英雄宝珠面板
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderHeroGem(param):
	'''
	获取充值送英雄宝珠奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not role.GetI32(EnumInt32.WonderTotalFill):
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===============================全服累计消费========================
def OpenWonderUnRMBTog(param):
	'''
	打开全服累计消费面板
	@param param:
	'''	
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	NumData = WonderfulData.GetWAData(WONDEFUL_INDEX_18)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [NumData]])
def GetWonderUnRMBTog(param):
	'''
	获取全服累计消费奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not cfg.TotalRMB :
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TotalRMB ," % rewardId
		return
	TotalRMB = cfg.TotalRMB 
	total = WonderfulData.GetWAData(WONDEFUL_INDEX_18)
	if total < TotalRMB:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===============================天天来夺宝==========================
def OpenWonderUnionTre(param):
	'''
	打开天天来夺宝界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	TreasureDict = WonderfulData.GetWAData(WONDEFUL_INDEX_17)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, TreasureDict])
		
def GetWonderUnionTre(param):
	'''
	获取天天来夺宝奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not cfg.UnionTreNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need UnionTreNum," % rewardId
		return
	boxType, boxNum = cfg.UnionTreNum
	totalNum = WonderfulData.GetWAData(WONDEFUL_INDEX_17).get(boxType, 0)
	if totalNum < boxNum:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#===============================羽翼返利============================
def OpenWonderWingBack(param):
	'''
	打开羽翼返利界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderWingBack(param):
	'''
	获取羽翼返利奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.MallWing:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need MallWing," % rewardId
		return
	wNum, WIds = cfg.MallWing
	wingDict = role.GetObj(EnumObj.Wing)[1]
	wingList = wingDict.keys()
	if not wingList:
		return
	cnt = 0
	for wid in wingList:
		if wid in WIds:
			cnt += 1
	if cnt < wNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#================================每天累计高级占卜=========================
def OpenWonderRoleTarot(param):
	'''
	打开每天累计高级占卜
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderRoleTarot(param):
	'''
	获取每天累计高级占卜奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.totalTaro:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need totalTaro," % rewardId
		return
	if role.GetI16(EnumInt16.WonderRoleTarot) < cfg.totalTaro:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===========================每日玩家购买宝石数=========================
def OpenWonderRoleGem(param):
	'''
	打开每日玩家购买宝石数
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderRoleGem(param):
	'''
	获取每日玩家购买宝石数奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.TotalGem:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TotalGem," % rewardId
		return
	if role.GetI16(EnumInt16.WonderRoleGem) < cfg.TotalGem:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#===========================每日累计充值=========================
def OpenWonderRMBTog(param):
	'''
	打开每日累计充值界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderRMBTog(param):
	'''
	获取每日累计充值奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.TotalFill:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TotalFill," % rewardId
		return
	if role.GetI32(EnumInt32.WonderTotalFill) < cfg.TotalFill:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#=============================天天来占卜==============================
def OpenWonderTarotDay(param):
	'''
	天天来占卜
	@param param:
	'''
	role, cfg = param
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_7).get(1, 0)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])	

def GetWonderTarotDay(param):
	'''
	获取天天来占卜奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not cfg.TarotNumDay:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TarotNumDay," % rewardId
		return
	global WONDEFUL_INDEX_7
	
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_7).get(1, 0)
	if num < cfg.TarotNumDay:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#=============================大家来占卜==============================
def OpenWonderTarot(param):
	'''
	大家来占卜
	@param param:
	'''
	role, cfg = param
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_7).get(2, 0)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])	

def GetWonderTarot(param):
	'''
	获取大家来占卜奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not cfg.TarotNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need TarotNum," % rewardId
		return
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_7).get(2, 0)
	if num < cfg.TarotNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#==============================天天宝石=============================
def OpenWonderGemDay(param):
	'''
	打开天天宝石界面
	@param param:
	'''
	role, cfg = param
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_6).get(1, 0)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])
	
def GetWonderGemDay(param):
	'''
	获取天天宝石奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not cfg.needGemNumDay:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need needGemNumDay," % rewardId
		return
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_6).get(1, 0)
	if num < cfg.needGemNumDay:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================幻翼炫酷===============================
def OpenWonderWingLevel(param):
	'''
	打开幻翼炫酷界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])

def GetWonderWingLevel(param):
	'''
	获取奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.oneFlyNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need oneFlyNum," % rewardId
		return
	wlevel, num = cfg.oneFlyNum
	wingDict = role.GetObj(EnumObj.Wing)[1]
	wingList = wingDict.values()
	cnt = 0
	for wingData in wingList:
		if wingData[0] >= wlevel:
			cnt += 1
	if cnt < num:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================飞的更高===============================
def OpenWonderWing(param):
	'''
	打开飞的更高界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])

def GetWonderWing(param):
	'''
	获取飞的更高奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.oneFlyNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need oneFlyNum," % rewardId
		return
	wlevel, num = cfg.oneFlyNum
	wingDict = role.GetObj(EnumObj.Wing)[1]
	wingList = wingDict.values()
	cnt = 0
	for wing in wingList:
		if wlevel <= wing[0]:
			cnt += 1
	if cnt < num:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================装备收集活动============================
def OpenWonderEquipSuit(param):
	'''
	打开装备收集活动界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderEquipSuit(param):
	'''
	获取装备收集奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.equipNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need equipNum," % rewardId
		return
	suit, suitNum = cfg.equipNum
	num = CheckEquip(role, suit)
	if num < suitNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================坐骑升级活动============================
def OpenWonderMountUp(param):
	'''
	打开坐骑升级界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderMountUp(param):
	'''
	获取坐骑升级奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.mountLevel:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need mountLevel," % rewardId
		return
	if role.GetI16(EnumInt16.MountEvolveID) < cfg.mountLevel:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#================================单笔购买神石活动============================
def OpenWonderSingalFill(param):
	'''
	打开单笔购买神石界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderSingalFill(param):
	'''
	获取单笔购买神石奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.singleFill:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need singleFill," % rewardId
		return
	if role.GetI32(EnumInt32.WonderSingleFill) < cfg.singleFill:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#================================宝石团购界面===================================
def OpenWonderGemTog(param):
	'''
	打开宝石团购界面
	@param param:
	'''
	role, cfg = param
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_6).get(2, 0)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])
	
def GetWonderGemTog(param):
	'''
	获取宝石团购奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if not cfg.needGemNum:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need needGemNum," % rewardId
		return
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_6).get(2, 0)
	if num < cfg.needGemNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================坐骑一起冲===================================
def OpenWonderMountTog(param):
	'''
	打开坐骑一起冲界面
	@param param:
	'''
	role, cfg = param
	evolveIds = wad.WONDER_MOUNTTOG_NUM.keys()
	evolveIds.sort()
	NumList = []
	for evolveId in evolveIds:
		num = WonderfulData.GetWAData(WONDEFUL_INDEX_16).get(evolveId, 0)
		leng = len(wad.WONDER_MOUNTTOG_NUM[evolveId])
		for _ in xrange(leng):
			NumList.append(num)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, NumList])
	
def GetWonderMountTog(param):
	'''
	活动坐骑一起冲奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.mountNumber:
		print "GE_EXC,WonderfulReward is error by rewardId=(%s),need mountNumber" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	evolveId, cfgNum = cfg.mountNumber
	
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_16).get(evolveId)
	if num < cfgNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================橙色英雄合成==================================
def OpenWonderHero(param):
	'''
	打开橙色英雄合成界面
	@param param:
	'''
	role, cfg = param
	actId = cfg.actId
	hero  = 0
	for heroId, act in wad.HEAR_ID_LIST.iteritems():
		if act == actId:
			hero = heroId
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_5).get(hero, 0)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])
	
def GetWonderHero(param):
	'''
	获取橙色英雄合成奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.orangeHeroNum:
		print "GE_EXC, WonderfulReward is error by rewardId=(%s),need orangeHeroNum" % rewardId
		return
	if cfg.needVIP > role.GetVIP():
		return
	
	heroId, cfgNum = cfg.orangeHeroNum
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_5).get(heroId, 0)
	if num < cfgNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================贵族返体力活动=================================
def OpenWonderVIPStr(param):
	'''
	打开贵族返体力界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderVIPStr(param):
	'''
	获取贵族返体力奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.needVIP > role.GetVIP():
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
#================================贵族等级活动=================================
def OpenWonderVIPLevel(param):
	'''
	打开贵族等级界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderVIPLevel(param):	
	'''
	获取贵族等级奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.needVIP > role.GetVIP():
		return
	if cfg.rewardHero:
		if not CheckHeroFull(role):
			return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================贵族团购活动=================================
def OpenWonderTVIP(param):
	'''
	打开贵族团购界面
	@param param:
	'''	
	role, cfg = param
	actId = cfg.actId
	VIPList = wad.WONDER_ACTID_VIP_DICT.get(actId)
	vipDict = WonderfulData.GetWAData(WONDEFUL_INDEX_4)
	vipNum = {}
	for vip in VIPList:
		num = vipDict.get(vip, 0)
		vipNum[vip] = num
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, vipNum])
	
def GetWonderTVIP(param):
	'''
	获取贵族团购奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.VIPNum:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	vip, num = cfg.VIPNum
	vipNum = WonderfulData.GetWAData(WONDEFUL_INDEX_4).get(vip, 0)
	if vipNum < num:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)	
#================================贵族返利活动=================================
def OpenWonderVIP(param):
	'''
	打开贵族返利活动界面
	@param param:
	'''
	role, cfg = param
	actId = cfg.actId
	VIPList = wad.WONDER_ACTID_VIP_DICT.get(actId)
	VIPData = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
	vipNum = {}
	for vip in VIPList:
		vipDict = VIPData.get(vip, {})
		num = vipDict.get(1,0)
		vipNum[vip] = num
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, vipNum])
	
def GetWonderVIP(param):
	'''
	获取贵族返利活动奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.VIPNum:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if WorldData.IsHeFu():#合服后该活动已经关闭了
		return
	vip, _ = cfg.VIPNum
	VIPData = WonderfulData.GetWAData(WONDEFUL_INDEX_15)
	if not VIPData:
		return
	VIPDict = VIPData.get(vip, {})
	nameList = VIPDict.get(2)	#获取玩家名数据

	#玩家已领取的数据
	vipDict = role.GetObj(EnumObj.Wonder_Vip_Reward_Dict)
	viptimes = vipDict.get(1)
	getedTimes = viptimes.get(rewardId, 0)#已经领取的次数
	VIPNum = VIPDict.get(1,0)
	if VIPNum <= getedTimes:
		return
	viptimes[rewardId] = viptimes.get(rewardId,0) + 1
	GetReward(role, cfg, actId, backId)
	
	#各版本判断
	if not Environment.EnvIsNA():
		if len(nameList) > getedTimes:
			name = nameList[getedTimes]
			reward = cfg.rewardItem
			coding, cnt = reward[0][0], reward[0][1]
			cRoleMgr.Msg(1, 0, GlobalPrompt.WONDERFUL_GET_REWARD % (role.GetRoleName(),coding, cnt, name))
#================================月卡/半年卡团购活动===========================
def OpenWonderMCard(param):
	'''
	打开月卡/半年卡团购活动界面
	@param param:
	'''
	
	role, cfg = param
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_3)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])
	
def GetWonderMCard(param):
	'''
	获取月卡/半年卡团购活动奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_3)
	if num < cfg.cardNum:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================购月卡/半年卡送森林之狼========================
def OpenWonderCard(param):
	'''
	打开购月卡/半年卡送森林之狼界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderCard(param):
	'''
	获取购月卡/半年卡送森林之狼奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not cfg.bugCard:
		return
	if cfg.bugCard == 1:
		if not role.GetI1(EnumInt1.WeekCardFirst):
			return
	elif cfg.bugCard == 2:
		if not role.GetI1(EnumInt1.MonthCardFirst):
			return
	else:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================首冲团购======================================
def OpenWonderFill(param):
	'''
	打开首冲团购界面
	@param param:
	'''
	role, cfg = param
	num = WonderfulData.GetWAData(WONDEFUL_INDEX_2)
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [num]])
	
def GetWonderFill(param):
	'''
	获取首冲团购奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return

	num = WonderfulData.GetWAData(WONDEFUL_INDEX_2)
	if num < cfg.fillNum:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#================================战力绝伦=======================================
def OpenWonderZDL(param):
	'''
	打开战力绝伦界面
	'''
	role, cfg = param
	mountData = WonderfulData.GetWAData(WONDEFUL_INDEX_14)
	firstName = ""
	if not mountData:
		#获取排行榜第一名
		ZDLRank = GetZDLRank()
		if ZDLRank:
			firstData = ZDLRank[0:1]
			firstName = firstData[0][0]
	else:
		firstData = mountData.get(1)
		firstName = firstData[0]
	#获取玩家已获取奖励
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [firstName]])

def GetWonderZDL(param):
	'''
	获取战力绝伦奖励
	@param param:
	'''
	if not WorldData.WD.returnDB: return
	
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	
	from Game.Activity.KaifuTarget import TimeControl
	if TimeControl.KaifuTargetTime_New >= kaifuTime:
		return
	role, actId, rewardId, backId = param
	cfg = CheckZDLReward(role,actId, rewardId)
	if not cfg:
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)

def CheckZDLReward(role, actId, rewardId):
	'''
	检查战力绝伦奖励
	@param role:
	@param actId:
	@param rewardId:
	'''
	state = GetActState(actId)
	if state == -1 or state == 0:
		return False
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return False
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return False
	if rewardId == wad.WONDER_ZDL_REWARD3:
		if state != 1:return False
		if role.GetZDL() < cfg.needZDL:
			return False
	else:
		if state != 2 and state != 1:return False
		ZDLObj = WonderfulData.GetWAData(WONDEFUL_INDEX_14)
		if not ZDLObj:
			return False
		roleId = role.GetRoleID()
		if rewardId == wad.WONDER_ZDL_REWARD1:
			if not CheckHeroFull(role):
				return False
			firstData = ZDLObj.get(1)
			if not firstData:
				return False
			if roleId != firstData[1]:
				return False
		if rewardId == wad.WONDER_ZDL_REWARD2:
			roleList = ZDLObj.get(2)
			if roleId not in roleList:
				return False
	return cfg

def GetZDLRank():
	'''
	获取战斗力排行榜
	'''
	#先跟新排行榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateZDLRank(role)
	sys_data = SystemRank.ZR.GetData()
	data_list = sys_data.values()
	data_list.sort(key = lambda x : (x[2], x[1]), reverse = True)
	select_list = data_list[0:20]
	return select_list

def SetZDLDB(param):
	'''
	战力绝伦结算
	'''
	if not WorldData.WD.returnDB: return
	
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	
	from Game.Activity.KaifuTarget import TimeControl
	if TimeControl.KaifuTargetTime_New >= kaifuTime:
		return
	actId = param
	rank_list = GetZDLRank()
	if not rank_list:
		print "GE_EXC,can find ZDLDate in wonderful"
		return
	first_data = rank_list[0:1]
	ZDLDate = WonderfulData.GetWAData(WONDEFUL_INDEX_14)
	with WonderfulZDL:
		ZDLDate[1] = [first_data[0][0],first_data[0][4]]
		role_list = []
		second_data = rank_list[1:20]
		for data in second_data:
			role_list.append(data[4])
		ZDLDate[2] = role_list
		#将奖励存储
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,Wonderful can not find actId(%s) in cfg"
			return
		SetActIdR(EnumWonderType.Wonder_Act_ZDL, cfg.rewardList)
		
		firstRoleId = ZDLDate[1][1]
		SRoleList = ZDLDate[2]
		firstRole = cRoleMgr.FindRoleByRoleID(firstRoleId)
		if firstRole:
			firstRole.SendObj(Wonder_Can_Reward, 1)
		for roleId in SRoleList:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
			role.SendObj(Wonder_Can_Reward, 1)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderZDLDB, (first_data, role_list, cDateTime.Now()))
#================================公会竞赛=======================================
def OpenWonderUnion(param):
	'''
	打开工会竞赛界面
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	state = GetActState(cfg.actId)
	name = ""
	if state == 1:
		sys_data = SystemRank.GetSortUnionList()#[(id, level, exp, name)]
		if sys_data:
			firstData = sys_data[0]
			name = firstData[3]
	else:
		unionData = WonderfulData.GetWAData(WONDEFUL_INDEX_13)
		if unionData:
			name = unionData[1]
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [name]])

def GetWonderUnion(param):
	'''
	获取工会竞赛奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	state = CheckUnionReward(role, actId, rewardId)
	if not state:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
def CheckUnionReward(role, actId, rewardId):
	'''
	检查工会竞赛奖励
	@param role:
	@param actId:
	@param rewardId:
	'''
	state = GetActState(actId)
	if state == -1 or state == 0:
		return False
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		return False
	if rewardId == wad.WONDER_UNION_REWARD3:#只可在活动进行时领取
		if state != 1:
			return False
		if cfg.needZDL > role.GetZDL():
			return False
	else:
		if state != 2 and state != 1:
			return False
		UnionDate = WonderfulData.GetWAData(WONDEFUL_INDEX_13)
		if not UnionDate : return
		unionId = UnionDate[0]
		if not unionId:
			return False
		unionObj = role.GetUnionObj()
		if not unionObj:
			return False
		if unionObj.union_id != unionId:
			return False
		if rewardId == wad.WONDER_UNION_REWARD1:
			roleId = role.GetRoleID()
			if roleId != UnionDate[2]:
				return False
	return cfg

def SetUnoionDB(param):
	actId = param
	#工会排行榜
	sys_data = SystemRank.GetSortUnionList()#[(id, level, exp, name)]
	if not sys_data:
		return
	firstData = sys_data[0]
	unionId = firstData[0]
	unionObj = UnionMgr.GetUnionObjByID(unionId)
	if not unionObj:
		return
	leader_id = unionObj.leader_id
	with WonderfulUnion:
		WonderfulData.SetWAData(WONDEFUL_INDEX_13, [unionId, firstData[3], leader_id])
		#将奖励存储
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,Wonderful can not find actId(%s) in cfg" % actId
			return
		SetActIdR(EnumWonderType.Wonder_Act_Union, cfg.rewardList)
		for roleId, _ in unionObj.members.iteritems():
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
			role.SendObj(Wonder_Can_Reward, 1)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderUnionDB, (leader_id, unionId, firstData[3], cDateTime.Now()))
#================================圣城争霸=======================================
def OpenWonderDuke(param):
	'''
	打开圣城争霸界面
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	unionDates = WonderfulData.GetWAData(WONDEFUL_INDEX_9)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, unionDates])

def GetWonderDuke(param):
	'''
	获取圣城争霸奖励
	'''
	role, actId, rewardId, backId = param
	cfg = CheckDukeReward(role, actId, rewardId)
	if not cfg:
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)

def CheckDukeReward(role, actId, rewardId):
	'''
	检测圣城争霸奖励
	@param role:
	@param actId:
	@param rewardId:
	'''
	state = GetActState(actId)
	if state !=1  and state != 2:
		return False

	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return False
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return False
	wunionList = WonderfulData.GetWAData(WONDEFUL_INDEX_9)
	if not wunionList:
		return False
	if len(wunionList) < 3:
		return False
	unionList = []
	unionList.extend(wunionList)
	unionList.sort(key = lambda x:x[0])
	selectUnion = 0
	if unionList[0][0] == unionList[1][0]:
		selectUnion = unionList[0][0]
	elif unionList[1][0] == unionList[2][0]:
		selectUnion = unionList[1][0]
	if not selectUnion:
		return False
	unionId = role.GetUnionID()
	if not unionId:
		return False
	if unionId != selectUnion:
		return False
	return cfg
#=============================首战，再战竞技======================================
def OpenWonderJJC(param):
	'''
	打开首站，再战竞技界面
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, []])
	
def GetWonderJJC(param):
	'''
	获取首站，再战奖励
	@param param:
	'''	
	role, actId, rewardId, backId = param
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	cfg = CheckJJCReward(role, actId, rewardId)
	if not cfg:
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
def CheckJJCReward(role, actId, rewardId):
	'''
	检测首站，再战竞技
	@param role:
	@param actId:
	@param rewardId:
	'''
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return False
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return False
	
	JJCDate = WonderfulData.GetWAData(WONDEFUL_INDEX_8).get(actId)
	if not JJCDate:
		return False
	roleId = role.GetRoleID()
	if rewardId in wad.WONDER_JJC_REWARD1:#第一类奖励
		if roleId not in JJCDate.get(1):
			return False
	elif rewardId in wad.WONDER_JJC_REWARD2:#第二类奖励
		if roleId not in JJCDate.get(2):
			return False
	elif rewardId in wad.WONDER_JJC_REWARD3:#第三类奖励
		if roleId not in JJCDate.get(3):
			return False
	elif rewardId in wad.WONDER_JJC_REWARD4:#第四类奖励
		roleList = JJCDate.get(4, [])
		if actId == EnumWonderType.Wonder_Act_JJC4:
			if roleId not in roleList[10:20]:
				return False
		else:
			if roleId not in roleList:
				return False
	return cfg
#=============================坐骑争霸===========================================
def OpenWonderMount(param):
	'''
	打开坐骑争霸界面
	'''
	role, cfg = param
	mountData = WonderfulData.GetWAData(WONDEFUL_INDEX_10)
	firstName = ""
	if not mountData:
		#获取排行榜第一名
		mountRank = GetMountRank()
		if mountRank:
			firstData = mountRank[0:1]
			firstName = firstData[0][0]
	else:
		firstData = mountData.get(1)
		firstName = firstData[0]
	#获取玩家已获取奖励
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [firstName]])

def GetWonderMount(param):	
	'''
	获取坐骑争霸奖励
	'''
	if not WorldData.WD.returnDB:
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	
	from Game.Activity.KaifuTarget import TimeControl
	if TimeControl.KaifuTargetTime_New >= kaifuTime:
		return
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	#这里要做下特殊处理，因为第3类奖励在活动期间可以领取，结束了不能领
	#第1,2类活动是活动开启期间不能领取，在领奖期间才行

	state = CheckMountReward(role, actId, rewardId)
	if not state:
		return
	wonderObj[1].add(rewardId)
	GetReward(role, state, actId, backId)
	
def CheckMountReward(role, actId, rewardId):
	'''
	检测是否可以领奖
	@param role:
	@param actId:
	@param rewardId:
	'''
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		return False
	state = GetActState(actId)
	if rewardId == wad.WONDER_MOUNT_REWARD3:
		if state != 1:
			return False
		evolve = role.GetI16(EnumInt16.MountEvolveID)
		if evolve < cfg.mountLevel:
			return False
	else:
		if state != 2 and state != 1:
			return False
		
		mountData = WonderfulData.GetWAData(WONDEFUL_INDEX_10)
		if not mountData:
			return False
		roleId = role.GetRoleID()
		if rewardId == wad.WONDER_MOUNT_REWARD1:
			firstData = mountData[1]
			if roleId != firstData[1]:
				return False
		elif rewardId == wad.WONDER_MOUNT_REWARD2:
			secondData = mountData[2]
			if roleId not in secondData:
				return False
		else:
			return False
	return cfg

def GetMountRank():
	'''
	获取坐骑排行榜
	'''
	#先跟新排行榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateMountRank(role)
	#获取坐骑排行榜
	sys_data = SystemRank.MR.GetData()
	data_list = sys_data.values()
	data_list.sort(key = lambda x : (x[1], x[2]), reverse = True)
	select_list = data_list[0:20]
	return select_list

def SetMountDB(param):
	'''
	结算炫酷坐骑最后的排名
	'''
	actId = param
	
	if not WorldData.WD.returnDB:
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	
	from Game.Activity.KaifuTarget import TimeControl
	if TimeControl.KaifuTargetTime_New >= kaifuTime:
		return
	
	rank_list = GetMountRank()
	if not rank_list:
		print "GE_EXC,SetMountDB wonderful rank_list is NULL"
		return
	first_data = rank_list[0:1]
	MountDate = WonderfulData.GetWAData(WONDEFUL_INDEX_10)
	with WonderfulMount:
		MountDate[1] = [first_data[0][0],first_data[0][4]]
		role_list = []
		second_data = rank_list[1:20]
		for data in second_data:
			role_list.append(data[4])
		MountDate[2] = role_list
		#将奖励存储
		cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
		if not cfg:
			print "GE_EXC,Wonderful can not find actId(%s) in cfg" % actId
			return
		SetActIdR(EnumWonderType.Wonder_Act_Mount, cfg.rewardList)
		
		firstRoleId = MountDate[1][1]
		firstRole = cRoleMgr.FindRoleByRoleID(firstRoleId)
		if firstRole:
			firstRole.SendObj(Wonder_Can_Reward, 1)
		SRoleList = MountDate[2]
		for roleId in SRoleList:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
			role.SendObj(Wonder_Can_Reward, 1)
		AutoLog.LogBase(first_data[0][4], AutoLog.eveWonderMountDB, (first_data[0][0], SRoleList, cDateTime.Now()))
#=============================疯狂冲级===========================================
def OpenWonderLevel(param):
	'''
	打开疯狂冲级界面
	'''
	role, cfg = param
	rewardList = cfg.rewardList
	GetedNum = {}
	Getdate = WonderfulData.GetWAData(WONDEFUL_INDEX_1)
	for rewardId in rewardList:
		num = Getdate.get(rewardId, 0)
		GetedNum[rewardId] = num
	GetedList = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedList, canList, GetedNum])

def GetWonderLevel(param):
	'''
	获取疯狂冲级奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:#已经领取了
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,Wonderful can not find rewardId(%s) in cfg" % rewardId
		return	
	if role.GetLevel() < cfg.level:
		return
	if not cfg.maxNum:
		print "GE_EXC,Wonderful no maxNum in GetWonderLevel,rewardId(%s)" % rewardId
		return
	Geteddate = WonderfulData.GetWAData(WONDEFUL_INDEX_1)
	GetedNum = Geteddate.get(rewardId, 0)
	if cfg.maxNum <= GetedNum:
		role.Msg(2, 0, GlobalPrompt.WONDERFUL_NO_TIMES)
		return
	if cfg.rewardHero:
		if not CheckHeroFull(role):
			return
	Geteddate[rewardId] = Geteddate.get(rewardId, 0) + 1
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
#=============================神兽快成长=========================
def OpenUnionShenShou(param):
	'''
	打开神兽快成长界面
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	unionObj = role.GetUnionObj()
	nowGrouth = 0
	if unionObj:
		nowGrouth =  unionObj.other_data.get(UnionDefine.O_ShenShowDayFeed, 0)
		if unionObj.other_data.get(UnionDefine.O_ShenShouIdCalled, None):
			nowGrouth = 120
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [nowGrouth]])
	
def GetUnionShenShou(param):
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if not unionObj.other_data.get(UnionDefine.O_ShenShouIdCalled, None) and \
			unionObj.other_data.get(UnionDefine.O_ShenShowDayFeed, 0) < cfg.needFeedTimes:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)

#===================================公会魔神==================================
def OpenUnionGod(param):
	'''
	打开公会魔神界面
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	unionObj = role.GetUnionObj()
	timeDict = {}
	if unionObj:
		timeDict = unionObj.god.get(UnionDefine.GOD_FIGHT_IDX)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, timeDict])
	
def GetUnionGod(param):
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	godId, times = cfg.unionGod
	FTDict = unionObj.god.get(UnionDefine.GOD_FIGHT_IDX)
	if FTDict.get(godId, 0) < times:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
#==================================公会累计充值======================================
def OpenUnionTotalFill(param):
	'''
	打开公会累计充值
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	unionObj = role.GetUnionObj()
	rmb = 0
	if unionObj:
		rmb = unionObj.other_data.get(UnionDefine.O_TotalFillRMB)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [rmb]])
	
def GetUnionTotalFill(param):
	'''
	获取公会累计充值奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	if unionObj.other_data.get(UnionDefine.O_TotalFillRMB, 0) < cfg.unionFill:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
#====================================个人宠物修行=================================
def OpenPetEvo(param):
	'''
	打开个人宠物修行
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.PetEvoTimes)]])
	
def GetPetEvo(param):
	'''
	获取个人宠物修行
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.petEvoTimes > role.GetI32(EnumInt32.PetEvoTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)

#==============================宠物齐修行===============================
def OpenTotalPetEvo(param):
	'''
	打开宠物齐修行界面
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_26).get(cfg.actId, 0)]])
	
def GetTotalPetEvo(param):
	'''
	获取宠物齐修行奖励
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if role.GetVIP() < cfg.needVIP:
		return
	PetData = WonderfulData.GetWAData(WONDEFUL_INDEX_26)
	if not PetData:
		return
	if PetData.get(actId, 0) < cfg.totalPetTimes:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===================================时装升星========================================
def OpenFashionUpStar(param):
	'''
	打开时装升星
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.FashionUpStarTimes)]])
	
def GetFashionUpStar(param):
	'''
	获取时装升星奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.upstartimes > role.GetI32(EnumInt32.FashionUpStarTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)

#===================================时装齐升星=======================================
def OpenFashionTotalStar(param):
	'''
	打开时装齐升星
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_27).get(cfg.actId, 0)]])
	
def GetFashionTotalStar(param):
	'''
	获取时装齐升星
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_27)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totalUpstar:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===================================时装升阶========================================
def OpenFashionUpOrder(param):
	'''
	打开时装升阶
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.FashionUpOrderTimes)]])
	
def GetFashionUpOrder(param):
	'''
	获取时装升阶奖励
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.upordertimes > role.GetI32(EnumInt32.FashionUpOrderTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===================================时装齐升阶=======================================
def OpenFashionTotalOrder(param):
	'''
	打开时装齐升阶
	@param role:
	@param param:
	'''
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_28).get(cfg.actId, 0)]])
	
def GetFashionTotalOrder(param):
	'''
	获取时装齐升阶
	@param role:
	@param param:
	'''
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_28)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totalUpOrder:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===================================星灵升级======================================
def OpenStarGirlLevel(param):
	#打开星灵升级界面
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.StarGirlLevelUpTimes)]])

def GetStarGirlLevel(param):
	#获取星灵升级奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.StarGirlLevel > role.GetI32(EnumInt32.StarGirlLevelUpTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#====================================星灵齐升级======================================
def OpenTotalStarGirlLevel(param):
	#打开星灵齐升级
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_29).get(cfg.actId, 0)]])
	
def GetTotalStarGirlLevel(param):
	#获取星灵齐升级
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_29)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totalStarGirlLevel:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===================================星灵升星======================================
def OpenStarGirlStar(param):
	#打开星灵升星界面
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.StarGirlStarTimes)]])

def GetStarGirlStar(param):
	#获取星灵升星奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.StarGirlStar > role.GetI32(EnumInt32.StarGirlStarTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#====================================星灵齐升星======================================
def OpenTotalStarGirlStar(param):
	#打开星灵齐升星
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_30).get(cfg.actId, 0)]])
	
def GetTotalStarGirlStar(param):
	#获取星灵齐升星
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_30)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totalStarGirlStar:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)

#===================================龙脉升级======================================
def OpenDragonLevelUp(param):
	#打开龙脉升级界面
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.DragonVeinLevelTimes)]])

def GetDragonLevelUp(param):
	#获取龙脉升级奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.dragonLevel > role.GetI32(EnumInt32.DragonVeinLevelTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#====================================龙脉齐升级======================================
def OpenTotalDragonLevelUp(param):
	#打开龙脉齐升级
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_31).get(cfg.actId, 0)]])
	
def GetTotalDragonLevelUp(param):
	#获取龙脉齐升级奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_31)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totaldragonLevel:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)

#===================================龙脉进化======================================
def OpenDragonEvo(param):
	#打开龙脉进化界面
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.DragonVeinEvoTimes)]])

def GetDragonEvo(param):
	#获取龙脉进化奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.dragonEvo > role.GetI32(EnumInt32.DragonVeinEvoTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#====================================龙脉齐进化======================================
def OpenTotalDragonEvo(param):
	#打开龙脉齐进化
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_32).get(cfg.actId, 0)]])
	
def GetTotalDragonEvo(param):
	#获取龙脉齐进化奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_32)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totaldragonEvo:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
	
#===================================称号升级======================================
def OpenTitleLevel(param):
	#打开称号升级界面
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [role.GetI32(EnumInt32.TitleLevelUpTimes)]])

def GetTitleLevel(param):
	#获取称号升级奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[1]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	if cfg.titleLevel > role.GetI32(EnumInt32.TitleLevelUpTimes):
		return
	wonderObj[1].add(rewardId)
	GetReward(role, cfg, actId, backId)
#====================================称号齐升级======================================
def OpenTotalTitleLevel(param):
	#打开称号齐升级
	role, cfg = param
	GetedRewards = GetGetedReward(role, cfg)
	canList = GetCanGetIDByAct(role, cfg.actId)
	role.SendObj(Wonder_Open_Panel_Data, [cfg.actId, GetedRewards, canList, [WonderfulData.GetWAData(WONDEFUL_INDEX_33).get(cfg.actId, 0)]])
	
def GetTotalTitleLevel(param):
	#获取称号齐升级奖励
	role, actId, rewardId, backId = param
	
	state = GetActState(actId)
	if state != 1:#活动不在进行中
		return
	wonderObj = role.GetObj(EnumObj.Wonder_Reward_List)
	if rewardId in wonderObj[2]:
		return
	cfg = WonderfulActConfig.WONDER_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, Wonderful can not find rewardId(%s) in cfg" % rewardId
		return
	CostData = WonderfulData.GetWAData(WONDEFUL_INDEX_33)
	if not CostData:
		return
	if CostData.get(actId, 0) < cfg.totaltitleLevel:
		return
	if role.GetVIP() < cfg.needVIP:
		return
	wonderObj[2].add(rewardId)
	GetReward(role, cfg, actId, backId)
#===================================打开============================================
def SetWonderOpenFun():
	global WonderOpenFun_Dict
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Level]  	 = OpenWonderLevel		#打开疯狂冲级界面
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Mount]  	 = OpenWonderMount		#打开坐骑争霸活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_JJC]    	 = OpenWonderJJC			#打开首战竞技
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_JJC2]   	 = OpenWonderJJC			#打开再战竞技
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Duke]   	 = OpenWonderDuke		#圣城争霸
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Union]  	 = OpenWonderUnion 		#公会竞赛	
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_ZDL]    	 = OpenWonderZDL			#战力绝伦
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Fill]  	 = OpenWonderFill		#首充团购
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Card]   	 = OpenWonderCard		#购月卡/半年卡送森林之狼
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_MCard]  	 = OpenWonderMCard		#月卡/半年卡团购活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_VIP]    	 = OpenWonderVIP			#贵族返利活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TVIP]   	 = OpenWonderTVIP		#贵族团购活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_VIPLevel] = OpenWonderVIPLevel	#贵族等级活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_VIPStr]   	 = OpenWonderVIPStr		#贵族返体力活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Hero]   	 = OpenWonderHero		#橙色英雄合成（天空）
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_MountTog] = OpenWonderMountTog	#坐骑一起冲
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GemTog] = OpenWonderGemTog		#宝石团购
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_SingalFill] = OpenWonderSingalFill	#单笔购买神石活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_MountUp] = OpenWonderMountUp		#坐骑升级活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_EquipSuit] = OpenWonderEquipSuit	#装备收集活动
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Wing] = OpenWonderWing		#飞的更高
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_WingLevel] = OpenWonderWingLevel	#幻翼炫酷
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Hero2]   	 = OpenWonderHero		#橙色英雄合成（死神）
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Hero3]   	 = OpenWonderHero		#橙色英雄合成（血族剑姬）	
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GemDay] = OpenWonderGemDay		#天天宝石团购
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Tarot] = OpenWonderTarot		#大家来占卜
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TarotDay] = OpenWonderTarotDay	#天天来占卜
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RMBTog] = OpenWonderRMBTog		#每天累计购买神石
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleGem] = OpenWonderRoleGem		#每天累计购买宝石
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleTarot] = OpenWonderRoleTarot	#每天累计高级占卜
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_WingBack] = OpenWonderWingBack	#羽翼返利
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure] = OpenWonderUnionTre	#天天来夺宝
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GemDay2] = OpenWonderGemDay		#天天宝石团购2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TarotDay2] = OpenWonderTarotDay	#天天来占卜2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RMBTog2] = OpenWonderRMBTog		#每天累计购买神石2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleGem2] = OpenWonderRoleGem	#每天累计购买宝石2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleTarot2] = OpenWonderRoleTarot	#每天累计高级占卜2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog] = OpenWonderUnRMBTog	#全服累计消费
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_ChangeName] = OpenWonderChangeName	#单笔充值送改名卡
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_Pet] = OpenWonderPet		#宠物大师
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_JJC3] = OpenWonderJJC		#打开决战竞技
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GloryWar] = OpenWonderGloryWar	#荣耀之战
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RMBTog3] = OpenWonderRMBTog		#每天累计购买神石3
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleGem3] = OpenWonderRoleGem	#每天累计购买宝石3
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleTarot3] = OpenWonderRoleTarot	#每天累计高级占卜3	
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure2] = OpenWonderUnionTre#天天来夺宝2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GemDay3] = OpenWonderGemDay		#天天宝石团购3
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TarotDay3] = OpenWonderTarotDay	#天天来占卜3
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog2] = OpenWonderUnRMBTog	#全服累计消费2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_FillLiBao] = OpenWonderFillLiBao	#狂欢充值抢好礼
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_SendCard] = OpenWonderFillLiBao	#购神石送布拉祖卡
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RMBTog4] = OpenWonderRMBTog		#每天累计购买神石4
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleGem4] = OpenWonderRoleGem	#每天累计购买宝石4
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleTarot4] = OpenWonderRoleTarot	#每天累计高级占卜4	
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure3] = OpenWonderUnionTre#天天来夺宝3
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GemDay4] = OpenWonderGemDay		#天天宝石团购4
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TarotDay4] = OpenWonderTarotDay	#天天来占卜4
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog3] = OpenWonderUnRMBTog	#全服累计消费3
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_MarryTog] = OpenWonderMarryTog	#一起来结婚
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_MarryRing] = OpenWonderMarryRing	#情比金坚
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_SendKey] = OpenWonderFillLiBao	#充值送黄金钥匙
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_SevenDay] = OpenWonderSevenDay	#7日签到送豪礼
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_FillRank] = OpenWonderFillRank	#充值狂人
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionRank] = OpenWonderUnionRank	#公会争霸
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_JJC4] = OpenWonderJJC		#决战竞技(合服后)
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_ZDLRank] = OpenWonderZDLRank	#战力排行
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_SeniorVIP] = OpenWonderHighVIP	#高级贵族返利
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_CulWing] = OpenWonderCulWing	#天天爱飞翔
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TogWing] = OpenWonderTogWing	#大家一起飞
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_CulPet] = OpenWonderCulPet		#家有小宠快成长
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TogPet] = OpenWonderTogPet		#爱宠齐成长
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure4] = OpenWonderUnionTre#天天来夺宝
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_GemDay5] = OpenWonderGemDay		#天天宝石团购
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TarotDay5] = OpenWonderTarotDay	#天天来占卜
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RMBTog5] = OpenWonderRMBTog		#每天累计购买神石
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleGem5] = OpenWonderRoleGem	#每天累计购买宝石
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RoleTarot5] = OpenWonderRoleTarot	#每天累计高级占卜
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog4] = OpenWonderUnRMBTog	#全服累计消费
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_MarryTog2] = OpenWonderMarryTog	#一起来结婚2
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_HeroGem] = OpenWonderHeroGem		#充值送英雄宝珠
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionShenShou] = OpenUnionShenShou	#神兽快成长
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_UnionGod] = OpenUnionGod			#公会魔神
	WonderOpenFun_Dict[EnumWonderType.Wonder_UnionTotalFill] = OpenUnionTotalFill	#公会累计充值
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_PetEvo] = OpenPetEvo				#宠物修行
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TotalPetEvo] = OpenTotalPetEvo		#宠物齐修行
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_FashionUpStar] = OpenFashionUpStar	#时装升星
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_FashionTotalStar] = OpenFashionTotalStar#时装齐升星
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_FashionUpOrder] = OpenFashionUpOrder#时装升阶
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_FashionTotalOrder] = OpenFashionTotalOrder#时装齐升阶
	WonderOpenFun_Dict[EnumWonderType.Wonder_ACT_StarGirlLevel] = OpenStarGirlLevel#星灵升级
	WonderOpenFun_Dict[EnumWonderType.Wonder_ACT_TotalStarGirlLevel] = OpenTotalStarGirlLevel#星灵齐升级
	WonderOpenFun_Dict[EnumWonderType.Wonder_ACT_StarGirlStar] = OpenStarGirlStar#星灵升星
	WonderOpenFun_Dict[EnumWonderType.Wonder_ACT_TotalStarGirlStar] = OpenTotalStarGirlStar#星灵齐升星
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_DragonLevelUp] = OpenDragonLevelUp#龙脉升级
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TotalDragonLevelUp] = OpenTotalDragonLevelUp#龙脉齐升级
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_DragonEvo] = OpenDragonEvo			#龙脉进化
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TotalDragonEvo] = OpenTotalDragonEvo#龙脉齐进化
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TitleLevel] = OpenTitleLevel		#称号升级
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_TotalTitleLevel] = OpenTotalTitleLevel#龙称号齐升级
	WonderOpenFun_Dict[EnumWonderType.Wonder_Act_SendHallows] = OpenWonderFillLiBao	#充值送黄金钥匙
	if Environment.EnvIsRU():
		WonderOpenFun_Dict[EnumWonderType.Wonder_Act_RMBTo6] = OpenWonderRMBTog		#每天累计购买神石
	
	
def GetOpenFunByType(Etype, param):
	global WonderOpenFun_Dict
	fun = WonderOpenFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC,Wonderful Etype(%s) not in WonderOpenFun_Dict" % Etype
		return
	fun(param)
#==================================获取======================================
def SetWonderGetFun():
	global WonderGetFun_Dict
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Level]  	 = GetWonderLevel		#疯狂冲级界面
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Mount]  	 = GetWonderMount		#坐骑争霸活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_JJC]    	 = GetWonderJJC			#首战竞技
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_JJC2]   	 = GetWonderJJC			#再战竞技
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Duke]   	 = GetWonderDuke			#圣城争霸
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Union]  	 = GetWonderUnion 		#公会竞赛	
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_ZDL]    	 = GetWonderZDL			#战力绝伦
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Fill]   	 = GetWonderFill			#首充团购
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Card]   	 = GetWonderCard			#购月卡/半年卡送森林之狼
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_MCard]  	 = GetWonderMCard		#月卡/半年卡团购活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_VIP]    	 = GetWonderVIP			#贵族返利活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TVIP]   	 = GetWonderTVIP			#贵族团购活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_VIPLevel] = GetWonderVIPLevel		#贵族等级活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_VIPStr]   	 = GetWonderVIPStr		#贵族返体力活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Hero]   	 = GetWonderHero			#橙色英雄合成（天空）
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_MountTog] = GetWonderMountTog		#坐骑一起冲
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GemTog] = GetWonderGemTog		#宝石团购
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_SingalFill] = GetWonderSingalFill	#单笔购买神石活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_MountUp] = GetWonderMountUp		#坐骑升级活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_EquipSuit] = GetWonderEquipSuit	#装备收集活动
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Wing] = GetWonderWing			#飞的更高
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_WingLevel] = GetWonderWingLevel	#幻翼炫酷
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Hero2]  	 = GetWonderHero			#橙色英雄合成（死神）
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Hero3]  	 = GetWonderHero			#橙色英雄合成（血族剑姬）
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GemDay] = GetWonderGemDay		#天天宝石团购
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Tarot] = GetWonderTarot		#大家来占卜
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TarotDay] = GetWonderTarotDay		#天天来占卜
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RMBTog] = GetWonderRMBTog		#每天累计购买神石
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleGem] = GetWonderRoleGem		#每天累计购买宝石
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleTarot] = GetWonderRoleTarot	#每天累计高级占卜
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_WingBack] = GetWonderWingBack		#羽翼返利
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure] = GetWonderUnionTre	#天天来夺宝
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GemDay2] = GetWonderGemDay		#天天宝石团购2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TarotDay2] = GetWonderTarotDay	#天天来占卜2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RMBTog2] = GetWonderRMBTog		#每天累计购买神石2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleGem2] = GetWonderRoleGem		#每天累计购买宝石2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleTarot2] = GetWonderRoleTarot	#每天累计高级占卜2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog] = GetWonderUnRMBTog	#全服累计消费
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_ChangeName] = GetWonderChangeName	#单笔充值送改名卡
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_Pet] = GetWonderPet			#宠物大师
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_JJC3] = GetWonderJJC			#决战竞技
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GloryWar] = GetWonderGloryWar	#荣耀之战
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RMBTog3] = GetWonderRMBTog		#每天累计购买神石3
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleGem3] = GetWonderRoleGem		#每天累计购买宝石3
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleTarot3] = GetWonderRoleTarot	#每天累计高级占卜3	
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure2] = GetWonderUnionTre	#天天来夺宝2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GemDay3] = GetWonderGemDay		#天天宝石团购3
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TarotDay3] = GetWonderTarotDay	#天天来占卜3	
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog2] = GetWonderUnRMBTog	#全服累计消费2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_FillLiBao] = GetWonderFillLiBao	#狂欢充值抢好礼
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_SendCard] = GetWonderFillLiBao	#购神石送布拉祖卡
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RMBTog4] = GetWonderRMBTog		#每天累计购买神石4
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleGem4] = GetWonderRoleGem		#每天累计购买宝石4
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleTarot4] = GetWonderRoleTarot	#每天累计高级占卜4	
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure3] = GetWonderUnionTre	#天天来夺宝3
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GemDay4] = GetWonderGemDay		#天天宝石团购4
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TarotDay4] = GetWonderTarotDay	#天天来占卜4
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog3] = GetWonderUnRMBTog	#全服累计消费3
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_MarryTog] = GetWonderMarryTog	#一起来结婚
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_MarryRing] = GetWonderMarryRing	#情比金坚
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_SendKey] = GetWonderFillLiBao	#充值送黄金钥匙
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_SevenDay] = GetWonderSevenDay	#7日签到送豪礼
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_FillRank] = GetWonderFillRank	#充值狂人
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionRank] = GetWonderUnionRank	#公会争霸
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_JJC4] = GetWonderJJC			#决战竞技(合服后)
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_ZDLRank] = GetWonderZDLRank		#战力排行
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_SeniorVIP] = GetWonderHighVIP		#高级贵族返利
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_CulWing] = GetWonderCulWing		#天天爱飞翔
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TogWing] = GetWonderTogWing		#大家一起飞
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_CulPet] = GetWonderCulPet		#家有小宠快成长
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TogPet] = GetWonderTogPet		#爱宠齐成长
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionTreasure4] = GetWonderUnionTre	#天天来夺宝
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_GemDay5] = GetWonderGemDay		#天天宝石团购
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TarotDay5] = GetWonderTarotDay	#天天来占卜
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RMBTog5] = GetWonderRMBTog		#每天累计购买神石
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleGem5] = GetWonderRoleGem		#每天累计购买宝石
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_RoleTarot5] = GetWonderRoleTarot	#每天累计高级占卜
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnRMBTog4] = GetWonderUnRMBTog	#全服累计消费
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_MarryTog2] = GetWonderMarryTog	#一起来结婚2
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_HeroGem] = GetWonderHeroGem		#充值送英雄宝珠
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionShenShou] = GetUnionShenShou#神兽快成长
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_UnionGod] = GetUnionGod			#神兽魔神
	WonderGetFun_Dict[EnumWonderType.Wonder_UnionTotalFill] = GetUnionTotalFill	#公会累计充值
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_PetEvo] = GetPetEvo				#宠物修行
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TotalPetEvo] = GetTotalPetEvo	#宠物齐修行
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_FashionUpStar] = GetFashionUpStar#时装升星
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_FashionTotalStar] = GetFashionTotalStar#时装齐升星
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_FashionUpOrder] = GetFashionUpOrder#时装升阶
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_FashionTotalOrder] = GetFashionTotalOrder#时装齐升阶
	WonderGetFun_Dict[EnumWonderType.Wonder_ACT_StarGirlLevel] = GetStarGirlLevel#星灵升级
	WonderGetFun_Dict[EnumWonderType.Wonder_ACT_TotalStarGirlLevel] = GetTotalStarGirlLevel#星灵齐升级
	WonderGetFun_Dict[EnumWonderType.Wonder_ACT_StarGirlStar] = GetStarGirlStar#星灵升星
	WonderGetFun_Dict[EnumWonderType.Wonder_ACT_TotalStarGirlStar] = GetTotalStarGirlStar#星灵齐升星
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_DragonLevelUp] = GetDragonLevelUp#龙脉升级
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TotalDragonLevelUp] = GetTotalDragonLevelUp#龙脉齐升级
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_DragonEvo] = GetDragonEvo		#龙脉进化
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TotalDragonEvo] = GetTotalDragonEvo#龙脉齐进化
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TitleLevel] = GetTitleLevel		#称号升级
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_TotalTitleLevel] = GetTotalTitleLevel#龙称号齐升级
	WonderGetFun_Dict[EnumWonderType.Wonder_Act_SendHallows] = GetWonderFillLiBao	#购神石送布拉祖卡
	if Environment.EnvIsRU():
		WonderGetFun_Dict[EnumWonderType.Wonder_Act_RMBTo6] = GetWonderRMBTog		#每天累计购买神石

def GetGetFunByType(Etype, param):
	global WonderGetFun_Dict
	fun = WonderGetFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC, Wonderful Etype(%s) not in WonderGetFun_Dict" % Etype
		return
	fun(param)
#==================================结算======================================
def SetWonderSettlementFun():
	global WonderSettlementFun_Dict
	WonderSettlementFun_Dict[EnumWonderType.Wonder_Act_Mount] = SetMountDB			#坐骑争霸
	WonderSettlementFun_Dict[EnumWonderType.Wonder_Act_Union] = SetUnoionDB		#公会竞赛	
	WonderSettlementFun_Dict[EnumWonderType.Wonder_Act_ZDL] = SetZDLDB			#战力绝伦
	WonderSettlementFun_Dict[EnumWonderType.Wonder_Act_MarryRing] = SetMarryRingDB	#情比金坚
	WonderSettlementFun_Dict[EnumWonderType.Wonder_Act_FillRank] = SortFillRank		#充值狂人
	WonderSettlementFun_Dict[EnumWonderType.Wonder_Act_ZDLRank] = SetZDLRankDB		#战力排行

def GetSettlementFunByType(Etype, param = None):
	global WonderSettlementFun_Dict
	fun = WonderSettlementFun_Dict.get(Etype)
	if not fun:
		print "GE_EXC,Wonderful Etype(%s) not in WonderSettlementFun_Dict" % Etype
		return
	fun(param)
##============================================================
def OperationTick():
	'''
	每日23:59做的操作
	'''
	global WONDERFUL_RIGHT_ACT
	
	if not WONDERFUL_RIGHT_ACT:
		SetRightAct(1, 1)
	nowtime = cDateTime.Now()
	#这里做结算处理
	for actId, cfg in WONDERFUL_RIGHT_ACT.iteritems():
		if actId == EnumWonderType.Wonder_Act_FillLiBao or actId == EnumWonderType.Wonder_Act_SendCard:
			continue
		endtime = GetEndTime(actId)
		if endtime == -1 or endtime == 1:
			continue
		if endtime.year == nowtime.year and endtime.month == nowtime.month and endtime.day == nowtime.day:
			if not cfg.daytick:
				continue
			WonderfulOper(actId)
	ZeroClearData()

def ClearData():
	WonderfulData.GetWAData(WONDEFUL_INDEX_6)[1] = 0	#商城购买宝石数
	WonderfulData.GetWAData(WONDEFUL_INDEX_7)[1] = 0	#高级占卜数
	WonderfulData.SetWAData(WONDEFUL_INDEX_17, {})		#全服每日夺宝
	WonderfulData.SetWAData(WONDEFUL_INDEX_18, 0)		#全服每日累计消费
	#全服翅膀培养数
	WonderfulData.GetWAData(WONDEFUL_INDEX_24)[EnumWonderType.Wonder_Act_TogWing] = 0
	#全服宠物培养数
	WonderfulData.GetWAData(WONDEFUL_INDEX_25)[EnumWonderType.Wonder_Act_TogPet] = 0
	#清除公会争霸数据
	WonderfulData.GetWAData(WONDEFUL_INDEX_22)[EnumWonderType.Wonder_Act_UnionRank] = 0
	#清除宠物修行次数
	WonderfulData.GetWAData(WONDEFUL_INDEX_26)[EnumWonderType.Wonder_Act_TotalPetEvo] = 0
	#清除时装升星
	WonderfulData.GetWAData(WONDEFUL_INDEX_27)[EnumWonderType.Wonder_Act_FashionTotalStar] = 0
	#清除时装升阶
	WonderfulData.GetWAData(WONDEFUL_INDEX_28)[EnumWonderType.Wonder_Act_FashionTotalOrder] = 0
	#清除星灵升级消耗
	WonderfulData.GetWAData(WONDEFUL_INDEX_29)[EnumWonderType.Wonder_ACT_TotalStarGirlLevel] = 0
	#清除星灵升星消耗
	WonderfulData.GetWAData(WONDEFUL_INDEX_30)[EnumWonderType.Wonder_ACT_TotalStarGirlStar] = 0
	#清除龙脉升级消耗
	WonderfulData.GetWAData(WONDEFUL_INDEX_31)[EnumWonderType.Wonder_Act_TotalDragonLevelUp] = 0
	#清除龙脉进化消耗
	WonderfulData.GetWAData(WONDEFUL_INDEX_32)[EnumWonderType.Wonder_Act_TotalDragonEvo] = 0
	#清除称号升级消耗
	WonderfulData.GetWAData(WONDEFUL_INDEX_33)[EnumWonderType.Wonder_Act_TotalTitleLevel] = 0
	
def ZeroClearData():
	#这里做些清0操作
	ClearData()
	#注册个Tick
	cComplexServer.RegTick(2 * 60, SetRightAct)
	
def WonderfulOper(actId):
	'''
	每日活动处理
	@param actId:
	'''
	GetSettlementFunByType(actId, actId)
		
def SetRightAct(callargv, regparam):
	'''
	获取当天进行中和可领奖的活动
	'''
	global WONDERFUL_RIGHT_ACT
	global IS_START_1
	global IS_START_2
	#这里做清除处理
	nowtime = cDateTime.Now()
	rewardDict = WonderfulData.GetWAData(WONDEFUL_INDEX_11)
	if rewardDict is None:
		return 
	DisActList = []
	with WonderfulDisAct:
		for actId in rewardDict.keys():
			if actId == EnumWonderType.Wonder_Act_FillLiBao:
				if not COTMgr.__COTSTART:
					DisActList.append(actId)
			elif actId == EnumWonderType.Wonder_Act_SendCard:
				if not BallFame.isBallFameOpen:
					DisActList.append(actId)
			elif actId == EnumWonderType.Wonder_Act_SendKey:
				if not GoldChest.__IS_START:
					DisActList.append(actId)
			elif actId == EnumWonderType.Wonder_Act_SendHallows:
				global HALLOWS_IS_START
				if not HALLOWS_IS_START:
					DisActList.append(actId)
			else:
				disTime = GetDisappearTime(actId)
				if disTime == -1:
					continue
				if disTime == 1 or disTime <= nowtime:
					del rewardDict[actId]
					DisActList.append(actId)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWonderDisAct, (DisActList, WonderfulData.GetWAData(WONDEFUL_INDEX_11), cDateTime.Now()))
	#重置
	if WONDERFUL_RIGHT_ACT:
		WONDERFUL_RIGHT_ACT = {}
	for cfg in WonderfulActConfig.WONDERFUL_BASE_DICT.itervalues():
		state = GetActState(cfg.actId)
		if state == 1 or state == 2:#开启中和可领奖的
			WONDERFUL_RIGHT_ACT[cfg.actId] = cfg

#======================================客户端请求=======================================
def RequestOpenPanel(role, msg):
	'''
	客户端请求打开界面
	@param role:
	@param msg:
	'''
	#获取玩家可以领取的奖励
	canDict = GetCanGetID(role)
	role.SendObj(Wonder_Can_Reward_Dict, canDict.keys())

def RequestOpenAct(role, msg):
	'''
	客户端请求打开某个活动
	@param role:
	@param msg:
	'''
	actId = msg
	if not actId:
		return
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,Wonderful OpenAct can not find actId(%s)" % actId
		return
	GetOpenFunByType(actId, (role, cfg))
	
def RequestGetReward(role, msg):
	'''
	客户端请求获取活动奖励
	@param role:
	@param msg:
	'''
	backId, (actId, rewardId) = msg
	cfg = WonderfulActConfig.WONDERFUL_BASE_DICT.get(actId)
	if not cfg:
		print "GE_EXC,Wonderful can not find actId(%s) in WONDERFUL_BASE_DICT" % actId
		return
	state = GetActState(actId)
	if state != 1 and state != 2:
		print "GE_EXC,Wonderful GetReward but actId(%s) is end" % actId
		return
	if rewardId not in cfg.rewardList:#该活动不存在该奖励ID
		print "GE_EXC,Wonderful GetReward but rewardId(%s) not in rewardList" % rewardId
		return
	GetGetFunByType(actId, (role, actId, rewardId, backId))
##============================================================
if "_HasLoad" not in dir():
	WonderfulAct = None
	if Environment.HasLogic:
		#每日清零
		Cron.CronDriveByMinute((2038, 1, 1), OperationTick, H = "H == 23", M = "M == 59")
		#服务器启动预处理
		SetWonderIncFun()
		SetWonderGetFun()
		SetWonderSettlementFun()
		SetWonderOpenFun()
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_AfterLoginJoinScene, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterMountEvolve, AfterChangeMountEvole)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterChangeUnbindRMB_S)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_ChangeMarryRoleName, AfterMarry)
		Event.RegEvent(Event.Eve_AfterSystemHeFu, AfterSystemHeFu)
		Event.RegEvent(Event.Eve_AfterRoleHeFu, AfterRoleHeFu)

		Event.RegEvent(Event.Eve_StartCircularActive, HallowsStart)
		Event.RegEvent(Event.Eve_EndCircularActive, HallowsEnd)
	if Environment.HasLogic and not Environment.IsCross:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wonderful_Open_Act_Panel", "客户端请求打开精彩活动界面"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wonderful_Open_Act", "客户端请求打开某个活动"), RequestOpenAct)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wonderful_Get_Reward", "客户端请求获取奖励"), RequestGetReward)
	
