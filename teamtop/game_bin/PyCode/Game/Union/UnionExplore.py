#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionExplore")
#===============================================================================
# 公会魔域探秘
#===============================================================================
import copy
import random
import cComplexServer
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Fight import FightEx
from Game.JJC import JJCMgr
from Game.Persistence import Contain
from Game.Role import Event, Rank, Status
from Game.Role.Data import EnumDayInt8, EnumInt8, EnumInt1
from Game.RoleFightData import RoleFightData
from Game.Union import UnionConfig, UnionDefine, UnionMgr
from Game.VIP import VIPConfig

if "_HasLoad" not in dir():
	CALL_BACK_TIME_FOR_QUESTION = 10	#等待答题回调时间
	CALL_BACK_TIME = 60					#等待回调时间
	
	UNION_EXPLORE_MEMBER_RANK_OBJ_DICT = {}	#公会成员排行榜对象字典
	
	#消息
	Union_Explore_Show_Rank = AutoMessage.AllotMessage("Union_Explore_Show_Rank", "通知客户端显示公会魔域探秘排行榜")
	Union_Explore_Show_Other_Data = AutoMessage.AllotMessage("Union_Explore_Show_Other_Data", "通知客户端显示公会魔域探秘其它数据")
	Union_Explore_Show_Prisoner_Panel = AutoMessage.AllotMessage("Union_Explore_Show_Prisoner_Panel", "通知客户端显示公会魔域探秘战俘面板")
	Union_Explore_Show_Question = AutoMessage.AllotMessage("Union_Explore_Show_Question", "通知客户端显示公会魔域探秘问题")
	Union_Explore_Show_Monster_Event = AutoMessage.AllotMessage("Union_Explore_Show_Monster_Event", "通知客户端显示公会魔域打怪物事件")
	Union_Explore_Show_Treasure = AutoMessage.AllotMessage("Union_Explore_Show_Treasure", "通知客户端显示公会魔域宝箱")
	Union_Explore_Show_Prisoner_Event = AutoMessage.AllotMessage("Union_Explore_Show_Prisoner_Event", "通知客户端显示公会魔域抓战俘事件")
	
class UnionExploreRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 200						#最大排行榜数量
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_UnionExplore"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		if v1[2] != v2[2]:
			#深度
			return v1[2] < v2[2]
		elif v1[3] != v1[3]:
			#战俘数量
			return v1[3] < v2[3]
		else:
			#roleId小的先注册
			return v1[0] > v2[0]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
		
	def GetRank(self, role_id):
		# 获取角色的排名（没上榜返回0）
		value = self.data.get(role_id)
		if value is None:
			return 0
		rank = 1
		for _value in self.data.itervalues():
			if self.IsLess(value, _value):
				rank += 1
		return rank
		
class UnionExploreUnionRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		if v1[2] != v2[2]:
			#深度
			return v1[2] < v2[2]
		elif v1[3] != v1[3]:
			#战俘数量
			return v1[3] < v2[3]
		else:
			#roleId小的先注册
			return v1[0] > v2[0]
	
def AfterLoad():
	pass

def GetExploreMeter(role):
	roleId = role.GetRoleID()
	return UNION_EXPLORE_METER_DICT.get(roleId, 0)

def IncExploreMeter(role, incMeter):
	roleId = role.GetRoleID()
	roleMeter = GetExploreMeter(role)
	roleMeter += incMeter
	if roleMeter > EnumGameConfig.UNION_EXPLORE_METER_MAX:
		roleMeter = EnumGameConfig.UNION_EXPLORE_METER_MAX
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_MAX_METER_PROMPT)
	
	global UNION_EXPLORE_METER_DICT
	UNION_EXPLORE_METER_DICT[roleId] = roleMeter
	
def DecExploreMeter(role, decMeter):
	roleId = role.GetRoleID()
	roleMeter = GetExploreMeter(role)
	if roleMeter == 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_MIN_METER_PROMPT)
		return
	
	if roleMeter - decMeter < 0:
		roleMeter = 0
	else:
		roleMeter -= decMeter
	
	global UNION_EXPLORE_METER_DICT
	UNION_EXPLORE_METER_DICT[roleId] = roleMeter
	
def GetRewardByExploreFactor(role, factor, reward):
	meter = GetExploreMeter(role)
	return int((2 - 10**(-meter/9999.0)) * factor * reward)
	
def InRank(role):
	InServerRank(role)
	InUnionRank(role)
	
def InServerRank(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	meter = GetExploreMeter(role)
	prisonerCnt = unionObj.GetPrisonerCnt(roleId)
	
	#先删除再入榜
	if roleId in UER.data:
		del UER.data[roleId]
	UER.HasData(roleId, [roleId, role.GetRoleName(), meter, prisonerCnt])
	
def InUnionRank(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	littleRank = UNION_EXPLORE_MEMBER_RANK_OBJ_DICT.get(unionObj.union_id)
	if not littleRank:
		return
	
	meter = GetExploreMeter(role)
	prisonerCnt = unionObj.GetPrisonerCnt(roleId)
	
	#先删除再入榜
	if roleId in littleRank.data:
		del littleRank.data[roleId]
	littleRank.HasData(roleId, [roleId, role.GetRoleName(), meter, prisonerCnt])

def AnswerQuestionCall(role):
	questionIdList = UnionConfig.UNION_EXPLORE_QUESTION.keys()
	
	questionId = random.sample(questionIdList, 1)
	
	role.SendObjAndBack(Union_Explore_Show_Question, questionId, CALL_BACK_TIME_FOR_QUESTION, QuestionCallBack, questionId)

def QuestionCallBack(role, callargv, regparam):
	questionId, = regparam
	
	#日志
	with TraUnionExploreQuestionReward:
		QuestionReward(role, callargv, questionId)
	
def QuestionReward(role, callargv, questionId):
	questionConfig = UnionConfig.UNION_EXPLORE_QUESTION.get(questionId)
	if not questionConfig:
		return
	
	questionRewardConfig = UnionConfig.UNION_EXPLORE_QUESTION_REWARD.get(role.GetLevel())
	if not questionRewardConfig:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if callargv and callargv == questionConfig.right:
		#正确
		addContribution = GetRewardByExploreFactor(role, questionRewardConfig.exploreFactor, questionRewardConfig.rightContribution)
		addResource = GetRewardByExploreFactor(role, questionRewardConfig.exploreFactor, questionRewardConfig.rightResource)
		if addContribution > 0:
			role.IncContribution(addContribution)
		if addResource > 0:
			unionObj.IncUnionResource(addResource)
		
		#增加探索度
		meter = random.randint(*questionRewardConfig.rightUpRange)
		IncExploreMeter(role, meter)
		
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_QUESTION_RIGHT_PROMPT % (addContribution, addResource, meter))
	else:
		#错误
		addContribution = GetRewardByExploreFactor(role, questionRewardConfig.exploreFactor, questionRewardConfig.wrongContribution)
		addResource = GetRewardByExploreFactor(role, questionRewardConfig.exploreFactor, questionRewardConfig.wrongResource)
		if addContribution > 0:
			role.IncContribution(addContribution)
		if addResource > 0:
			unionObj.IncUnionResource(addResource)
		
		#减少探索度
		meter = random.randint(*questionRewardConfig.wrongDownRange)
		DecExploreMeter(role, meter)
		
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_QUESTION_WRONG_PROMPT % (addContribution, addResource, meter))
	
	#保存
	unionObj.HasChange()
	
	#入榜
	InRank(role)
	
	#通知客户端显示
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
def FightMonsterCall(role):
	role.SendObjAndBack(Union_Explore_Show_Monster_Event, None, CALL_BACK_TIME, MonsterCallBack)
	
def MonsterCallBack(role, callargv, regparam):
	FightMonster(role, callargv)
			
def FightMonster(role, callargv):
	meter = GetExploreMeter(role)
	
	monsterConfig = UnionConfig.UNION_EXPLORE_MONSTER.get(meter)
	if not monsterConfig:
		return
	
	mcid = monsterConfig.mcidList[random.randint(0, len(monsterConfig.mcidList) - 1)]
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if callargv and callargv == 1:
		#状态判断
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		#战斗
		FightEx.PVE(role, 166, mcid, AfterFightMonster, None)
	else:
		#逃跑
		#日志
		with TraUnionExploreLostMonsterReward:
			LostMonster(role, True)
	
def WinMonster(role):
	monsterRewardConfig = UnionConfig.UNION_EXPLORE_MONSTER_REWARD.get(role.GetLevel())
	if not monsterRewardConfig:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	addContribution = GetRewardByExploreFactor(role, monsterRewardConfig.exploreFactor, monsterRewardConfig.winContribution)
	addResource = GetRewardByExploreFactor(role, monsterRewardConfig.exploreFactor, monsterRewardConfig.winResource)
	if addContribution > 0:
		role.IncContribution(addContribution)
	if addResource > 0:
		unionObj.IncUnionResource(addResource)
		
	#保存
	unionObj.HasChange()
		
	#增加探索度
	meter = random.randint(*monsterRewardConfig.winUpRange)
	IncExploreMeter(role, meter)
	
	#入榜
	InRank(role)
	
	#通知客户端显示
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_MONSTER_WIN_PROMPT % (addContribution, addResource, meter))

def LostMonster(role, isEscape = False):
	monsterRewardConfig = UnionConfig.UNION_EXPLORE_MONSTER_REWARD.get(role.GetLevel())
	if not monsterRewardConfig:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	addContribution = GetRewardByExploreFactor(role, monsterRewardConfig.exploreFactor, monsterRewardConfig.lostContribution)
	addResource = GetRewardByExploreFactor(role, monsterRewardConfig.exploreFactor, monsterRewardConfig.lostResource)
	if addContribution > 0:
		role.IncContribution(addContribution)
	if addResource > 0:
		unionObj.IncUnionResource(addResource)
		
	#保存
	unionObj.HasChange()
		
	#减少探索度
	meter = random.randint(*monsterRewardConfig.lostDownRange)
	DecExploreMeter(role, meter)
	
	#入榜
	InRank(role)
	
	#通知客户端显示
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
	#提示
	if isEscape is True:
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_MONSTER_ESCAPE_PROMPT % (addContribution, addResource, meter))
	else:
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_MONSTER_LOST_PROMPT % (addContribution, addResource, meter))
	
def GetTreasureCall(role):
	role.SendObjAndBack(Union_Explore_Show_Treasure, None, 5, TreasureCallBack)
	
def TreasureCallBack(role, callargv, regparam):
	#日志
	with TraUnionExploreTreasureReward:
		TreasureReward(role)
	
def TreasureReward(role):
	treasureRewardConfigList = UnionConfig.UNION_EXPLORE_TREASURE_REWARD.get(role.GetLevel())
	if not treasureRewardConfigList:
		return
	
	roleMeter = GetExploreMeter(role)
	rewardConfig = None
	for config in treasureRewardConfigList:
		if roleMeter >= config.meterRange[0] and roleMeter <= config.meterRange[1]:
			rewardConfig = config
			break
	
	if not rewardConfig:
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		itemCoding, itemCnt = rewardConfig.itemRandomObj_fcm.RandomOne()
		role.AddItem(itemCoding, itemCnt)
	elif yyAntiFlag == 0:
		itemCoding, itemCnt = rewardConfig.itemRandomObj.RandomOne()
		role.AddItem(itemCoding, itemCnt)
	else:
		itemCoding, itemCnt = 0, 0
	
	#增加探索度
	meter = random.randint(*rewardConfig.upRange)
	IncExploreMeter(role, meter)
	
	#入榜
	InRank(role)
	
	#通知客户端显示
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
	#提示
	if yyAntiFlag == -1:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward + GlobalPrompt.UNION_EXPLORE_GET_TREASURE_fcm % meter)
	else:
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_GET_TREASURE_PROMPT % (itemCoding, itemCnt, meter))
	
def TakePrisonerCall(role):
	#是否有可挑战的玩家
	prisonerRoleId = GetChallengePrisonerRoleId(role)
	if not prisonerRoleId:
		FightMonsterCall(role)
		return
	
	#战俘数据
	prisonerRoleObj = JJCMgr.JJC_ROLE_OBJ_DICT.get(prisonerRoleId)
	if not prisonerRoleObj:
		FightMonsterCall(role)
		return
	
	role.SendObjAndBack(Union_Explore_Show_Prisoner_Event, (prisonerRoleObj.role_name, prisonerRoleObj.role_zdl), CALL_BACK_TIME, PrisonerCallBack, prisonerRoleId)
	
def PrisonerCallBack(role, callargv, regparam):
	prisonerRoleId = regparam
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if callargv and callargv == 1:
		#状态判断
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		#挑战战俘
		beChallengedPrisonerFightData = RoleFightData.GetRoleFightData(prisonerRoleId)
		if not beChallengedPrisonerFightData:
			print "GE_EXC can't find fight data(%s) in PrisonerCallBack" % beChallengedPrisonerFightData
			return
		#战斗
		FightEx.PVP_UnionExplore(role, 167, beChallengedPrisonerFightData, AfterFightPrisoner, afterFightParam = prisonerRoleId)
	else:
		#逃跑
		#日志
		with TraUnionExploreLostPrisonerReward:
			LostPrisoner(role, True)
		
def GetChallengePrisonerRoleId(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return 
	
	#获取玩家排名
	rank = UER.GetRank(roleId)
	if not rank:
		return
			
	canChallengePrisonerData = GetCanChallengePrisoner(role)
	if not canChallengePrisonerData:
		return
	
	rankList = canChallengePrisonerData.values()
	rankList.sort(key = lambda x:x[2], reverse = True)
	
	#获取前后10名
	idx = rank
	randomList = []
	if idx >= 10:
		randomList = rankList[idx - 10 : idx]
	else:
		randomList = rankList[:idx]
	randomList.extend(rankList[idx : idx + 10])
	challengePrisonerData = randomList[random.randint(0, len(randomList) - 1)]
	
	return challengePrisonerData[0]

def GetCanChallengePrisoner(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return None
	
	uerData = copy.deepcopy(UER.data)
	#排除已经是自己战俘的玩家
	prisonerData = unionObj.GetPrisonerData(roleId)
	for prisonerRoleId in prisonerData.iterkeys():
		if prisonerRoleId in uerData:
			del uerData[prisonerRoleId]
	
	#排除自己
	if roleId in uerData:
		del uerData[roleId]
		
	return uerData
	
def WinPrisoner(role, prisonerRoleId):
	prisonerRewardConfig = UnionConfig.UNION_EXPLORE_PRISONER_REWARD.get(role.GetLevel())
	if not prisonerRewardConfig:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	addContribution = GetRewardByExploreFactor(role, prisonerRewardConfig.exploreFactor, prisonerRewardConfig.winContribution)
	if addContribution > 0:
		role.IncContribution(addContribution)
		
	#增加探索度
	meter = random.randint(*prisonerRewardConfig.winUpRange)
	IncExploreMeter(role, meter)
	
	#有70%概率抓到战俘
	if random.randint(1, 100) < 70:
		#战俘数据
		prisonerRoleObj = JJCMgr.JJC_ROLE_OBJ_DICT.get(prisonerRoleId)
		if not prisonerRoleObj:
			return
		
		roleId = role.GetRoleID()
		prisonerData = unionObj.GetPrisonerData(roleId)
		if prisonerRoleId in prisonerData:
			return
		
		#战俘是否已满
		vip = role.GetVIP()
		if vip:
			vipConfig = VIPConfig._VIP_BASE.get(vip)
			if len(prisonerData) >= vipConfig.UnionExplorePrisonerCnt:
				#提示
				role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_PRISONER_FULL_PROMPT % (addContribution, meter))
				return
		else:
			if len(prisonerData) >= EnumGameConfig.UNION_EXPLORE_PRISONER_CNT_NO_VIP:
				#提示
				role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_PRISONER_FULL_PROMPT % (addContribution, meter))
				return
		
		#计算产量
		resourcePerHour = 0
		outputHours = 0
		for config in UnionConfig.UNION_EXPLORE_PRISONER_OUTPUT_LIST:
			if prisonerRoleObj.role_zdl >= config.zdlRange[0] and prisonerRoleObj.role_zdl <= config.zdlRange[1]:
				resourcePerHour = random.randint(*config.resourceRange)
				outputHours = random.randint(*config.timeRange)
			
		prisonerData[prisonerRoleId] = [prisonerRoleObj.role_id, prisonerRoleObj.role_name, prisonerRoleObj.role_zdl, resourcePerHour, outputHours]
		
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_TAKE_PRISONER_SUCCESS_PROMPT % (addContribution, meter))
		
		#保存
		unionObj.HasChange()
	else:
		#没有抓到战俘
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_PRISONER_ESCAPE_PROMPT % (addContribution, meter))
	
	#入榜
	InRank(role)
	
	#通知客户端显示
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
def LostPrisoner(role, isEscape = False):
	prisonerRewardConfig = UnionConfig.UNION_EXPLORE_PRISONER_REWARD.get(role.GetLevel())
	if not prisonerRewardConfig:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	addContribution = GetRewardByExploreFactor(role, prisonerRewardConfig.exploreFactor, prisonerRewardConfig.lostContribution)
	if addContribution > 0:
		role.IncContribution(addContribution)
		
	#减少探索度
	meter = random.randint(*prisonerRewardConfig.lostDownRange)
	DecExploreMeter(role, meter)
	
	#入榜
	InRank(role)
	
	#通知客户端显示
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
	#提示
	if isEscape is True:
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_YOU_ESCAPE_PROMPT % (addContribution, meter))
	else:
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_TAKE_PRISONER_FAIL_PROMPT % (addContribution, meter))
		

def UnionExplore(role):
	if role.GetI8(EnumInt8.UnionExploreCnt) <= 0:
		return
	role.DecI8(EnumInt8.UnionExploreCnt, 1)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_UnionExplore, 1))
	
	eventId = UnionConfig.UNION_EXPLORE_EVENT_RANDOM_OBJ.RandomOne()
	if eventId == 1:
		#答题
		AnswerQuestionCall(role)
	elif eventId == 2:
		#怪物战斗
		FightMonsterCall(role)
	elif eventId == 3:
		#宝箱
		GetTreasureCall(role)
	elif eventId == 4:
		#抓俘虏
		TakePrisonerCall(role)
	else:
		return
	

def UnionExploreBuyCnt(role):
	cnt = role.GetDI8(EnumDayInt8.UnionExploreBuyCnt)
	
	config = UnionConfig.UNION_EXPLORE_BUY_CNT.get(cnt + 1)
	if not config:
		return
	
	if role.GetUnbindRMB() < config.needRMB:
		return
	
	role.DecUnbindRMB(config.needRMB)
	
	role.IncDI8(EnumDayInt8.UnionExploreBuyCnt, 1)
	role.IncI8(EnumInt8.UnionExploreCnt, 1)
	
def CreateMemberRank(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	global UNION_EXPLORE_MEMBER_RANK_OBJ_DICT
	if unionObj.union_id in UNION_EXPLORE_MEMBER_RANK_OBJ_DICT:
		return
	
	#没有公会排行榜则新生成
	UNION_EXPLORE_MEMBER_RANK_OBJ_DICT[unionObj.union_id] = littleRank = UnionExploreUnionRank(100)
	for memberId, memberData in unionObj.members.iteritems():
		memberName = memberData[UnionDefine.M_NAME_IDX]
		meter = UNION_EXPLORE_METER_DICT.get(memberId, 0)
		prisonerCnt = unionObj.GetPrisonerCnt(memberId)
		littleRank.HasData(memberId, [memberId, memberName, meter, prisonerCnt])
		
def UnionExploreGetResource(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	canGetResource = unionObj.GetPrisonerOutputResource(roleId)
	
	if canGetResource > 0:
		unionObj.IncUnionResource(canGetResource)
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_EXPLORE_GET_RESOURE_PROMPT % canGetResource)
	
	#重置
	unionObj.ResetPrisonerOutputResource(roleId)
	
	#删除过期的战俘
	prisonerDict = unionObj.other_data[UnionDefine.O_PRISONER_IDX]
	if roleId in prisonerDict:
		prisonerData = prisonerDict[roleId]
		timeOverPrisonerRoleIdList = []
		for prisonerRoleId, data in prisonerData.iteritems():
			timeOverHour = data[4]
			if timeOverHour > 0:
				continue
			timeOverPrisonerRoleIdList.append(prisonerRoleId)
		
		for prisonerRoleId in timeOverPrisonerRoleIdList:
			del prisonerData[prisonerRoleId]
		
	#保存
	unionObj.HasChange()
	
	#通知客户端显示
	ShowUnionExplorePrisonerPanel(role)
	ShowUnionExploreOtherData(role)
		
#===============================================================================
# 显示
#===============================================================================
def ShowUnionExploreRank(role):
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	CreateMemberRank(role)
	
	#公会排行，魔域排行
	role.SendObj(Union_Explore_Show_Rank, (UNION_EXPLORE_MEMBER_RANK_OBJ_DICT[unionId].data, UER.data))
	
def ShowUnionExploreOtherData(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	prisonerCnt = unionObj.GetPrisonerCnt(roleId)
	resourcePerHour = unionObj.GetAllPrisonerOutputPerHour(roleId)
	roleMeter = GetExploreMeter(role)
	
	#战俘数量，公会资源每小时产量，探索度
	role.SendObj(Union_Explore_Show_Other_Data, (prisonerCnt, resourcePerHour, roleMeter))

def ShowUnionExplorePrisonerPanel(role):
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	prisonerData = unionObj.GetPrisonerData(roleId)
	
	canGetResource = unionObj.GetPrisonerOutputResource(roleId)
	
	#战俘数据，可领取公会资源
	role.SendObj(Union_Explore_Show_Prisoner_Panel, (prisonerData.values(), canGetResource))
	
#===============================================================================
# 时间
#===============================================================================
def AfterNewHour():
	#每小时计算产量
	btData = UnionMgr.BT.GetData()
	for unionId in btData.iterkeys():
		unionObj = UnionMgr.GetUnionObjByID(unionId)
		if not unionObj:
			continue
		
		prisonerDict = unionObj.other_data[UnionDefine.O_PRISONER_IDX]
		for roleId, prisonerData in prisonerDict.iteritems():
			outputResource = 0
			for data in prisonerData.itervalues():
				resourcePerHour = data[3]
				timeOverHour = data[4]
				
				if timeOverHour <= 0:
					#已过期
					continue
				
				outputResource += resourcePerHour
				data[4] = timeOverHour - 1
			
			prisonerResourceDict = unionObj.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX]
			canGetResource = prisonerResourceDict.get(roleId, 0) + outputResource
			prisonerResourceDict[roleId] = canGetResource
	
		#保存
		unionObj.HasChange()
	
#===============================================================================
# 战斗相关
#===============================================================================
def AfterFightMonster(fight):
	'''
	
	@param fight:
	'''
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
		
	if fight.result == 1:
		#left win
		#日志
		with TraUnionExploreWinMonsterReward:
			WinMonster(role)
	elif fight.result == -1:
		#right win
		#日志
		with TraUnionExploreLostMonsterReward:
			LostMonster(role)
	else:
		#all lost
		pass
	
def AfterFightPrisoner(fight):
	'''
	
	@param fight:
	'''
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	prisonerRoleId = fight.after_fight_param
	if fight.result == 1:
		#left win
		#日志
		with TraUnionExploreWinPrisonerReward:
			WinPrisoner(role, prisonerRoleId)
	elif fight.result == -1:
		#right win
		#日志
		with TraUnionExploreLostPrisonerReward:
			LostPrisoner(role)
	else:
		#all lost
		pass
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleDayClear(role, param):
	role.SetI8(EnumInt8.UnionExploreCnt, EnumGameConfig.UNION_EXPLORE_DAY_FREE_CNT)
	
def OnRoleLeaveUnion(role, param):
	'''
	离开公会
	@param role:
	@param param:
	'''
	unionId = param
	roleId = role.GetRoleID()
	
	if unionId not in UNION_EXPLORE_MEMBER_RANK_OBJ_DICT:
		return
	
	littleRank = UNION_EXPLORE_MEMBER_RANK_OBJ_DICT[unionId]
	
	#删除个人在公会排行榜数据
	if roleId in littleRank.data:
		del littleRank.data[roleId]
		
def OnRoleDelUnion(role, param):
	'''
	离开公会
	@param role:
	@param param:
	'''
	unionId = param
	
	if unionId not in UNION_EXPLORE_MEMBER_RANK_OBJ_DICT:
		return
	
	#删除公会排行榜数据
	del UNION_EXPLORE_MEMBER_RANK_OBJ_DICT[unionId]
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionExploreOpenMainPanel(role, msg):
	'''
	客户端请求打开公会魔域探秘主面板
	@param role:
	@param msg:
	'''
	ShowUnionExploreRank(role)
	ShowUnionExploreOtherData(role)
	
def RequestUnionExploreOpenPrisonerPanel(role, msg):
	'''
	客户端请求打开公会魔域探秘战俘面板
	@param role:
	@param msg:
	'''
	ShowUnionExplorePrisonerPanel(role)

def RequestUnionExplore(role, msg):
	'''
	客户端请求公会魔域探秘
	@param role:
	@param msg:
	'''
	#状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	UnionExplore(role)

def RequestUnionExploreBuyCnt(role, msg):
	'''
	客户端请求公会魔域探秘购买行动力
	@param role:
	@param msg:
	'''
	#日志
	with TraUnionExploreBuyCnt:
		UnionExploreBuyCnt(role)

def RequestUnionExploreGetResource(role, msg):
	'''
	客户端请求公会魔域探秘领取公会资源
	@param role:
	@param msg:
	'''
	UnionExploreGetResource(role)

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		UNION_EXPLORE_METER_DICT = Contain.Dict("UNION_EXPLORE_METER_DICT", (2038, 1, 1), AfterLoad)
	
	if Environment.HasLogic and not Environment.IsCross:
		#公会魔域探秘排行榜
		UER = UnionExploreRank()
		
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#离开公会后调用
		Event.RegEvent(Event.Eve_AfterLeaveUnion, OnRoleLeaveUnion)
		#解散公会后调用
		Event.RegEvent(Event.Eve_DelUnion, OnRoleDelUnion)
		
		#时间
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		
		#日志
		TraUnionExploreBuyCnt = AutoLog.AutoTransaction("TraUnionExploreBuyCnt", "公会魔域探秘购买行动力")
		TraUnionExploreQuestionReward = AutoLog.AutoTransaction("TraUnionExploreQuestionReward", "公会魔域探秘答题奖励")
		TraUnionExploreWinMonsterReward = AutoLog.AutoTransaction("TraUnionExploreWinMonsterReward", "公会魔域探秘打怪胜利奖励")
		TraUnionExploreLostMonsterReward = AutoLog.AutoTransaction("TraUnionExploreLostMonsterReward", "公会魔域探秘打怪失败奖励")
		TraUnionExploreTreasureReward = AutoLog.AutoTransaction("TraUnionExploreTreasureReward", "公会魔域探秘宝箱奖励")
		TraUnionExploreWinPrisonerReward = AutoLog.AutoTransaction("TraUnionExploreWinPrisonerReward", "公会魔域探秘抓战俘胜利奖励")
		TraUnionExploreLostPrisonerReward = AutoLog.AutoTransaction("TraUnionExploreLostPrisonerReward", "公会魔域探秘抓战俘失败奖励")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Explore_Open_Main_Panel", "客户端请求打开公会魔域探秘主面板"), RequestUnionExploreOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Explore_Open_Prisoner_Panel", "客户端请求打开公会魔域探秘战俘面板"), RequestUnionExploreOpenPrisonerPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Explore", "客户端请求公会魔域探秘"), RequestUnionExplore)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Explore_Buy_Cnt", "客户端请求公会魔域探秘购买行动力"), RequestUnionExploreBuyCnt)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Explore_Get_Resource", "客户端请求公会魔域探秘领取公会资源"), RequestUnionExploreGetResource)
		
		
		
		
