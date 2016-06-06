#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JJC.JJCMgr")
#===============================================================================
# 竞技场管理器
#===============================================================================
import Environment
import cRoleDataMgr
import cRoleMgr
import cProcess
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumAward, GlobalPrompt,\
	EnumFightStatistics, EnumSocial
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.Award import AwardMgr
from Game.Activity.Title import Title
from Game.DailyDo import DailyDo
from Game.Fight import FightEx
from Game.JJC import JJCConfig
from Game.Persistence import BigTable, Contain
from Game.Role import Event, Status
from Game.Role.Data import EnumDayInt8, EnumInt8, EnumObj, EnumCD, EnumInt1, EnumTempInt64,\
	EnumTempObj, EnumInt16
from Game.RoleFightData import RoleFightData
from Game.Slave import SlaveOperate
from Game.Task import EnumTaskType
from Game.ThirdParty.QQidip import QQEventDefine
from Game.Union import UnionMgr
from Game.GlobalData import ZoneName


if "_HasLoad" not in dir():
	JJC_ACTIVATE_LEVEL = 31				#竞技场激活等级
	JJC_FRONT_LIST_MAX = 50				#FRONT列表最大长度
	JJC_REAR_LIST_MAX = 1950			#REAR列表最大长度
	JJC_BROKEN_LIMIT_RANK = 2001		#竞技场超出限制的排名统一设置为2001
	JJC_REAR_LIST_FIRST_RANK_IDX = 51	#50名后的列表起始排名为51
	JJC_CAN_SEE_ROLE_CNT = 7			#竞技场面板可以看到的玩家数量
	JJC_WIN_SCORE = 2					#竞技场胜利积分
	JJC_LOST_SCORE = 1					#竞技场失败积分
	JJC_INIT_CHALLENGE_CNT = 15			#竞技场初始挑战次数
	JJC_EXCHANGE_CNT_MAX = 12			#竞技场可以兑换的最大奖励数量
	JJC_CHALLENGE_CD = 5 * 60			#竞技场挑战CD
	
	JJC_FT_CHALLENGE_CD = 15 * 60		#繁体版竞技场CD(类似强化装备CD规则)
	
	JJC_ROLE_OBJ_DICT = {}				#保存竞技场role对象字典
	JJC_ROLE_CAN_CHALLENGE_DICT = {}	#保存角色可以挑战的roleId集合字典
	
	#索引
	EXCHANGE_INDEX = 1	#竞技场对象兑换索引
	
	#消息
	JJC_Show_Main_Panel = AutoMessage.AllotMessage("JJC_Show_Main_Panel", "通知客户端显示竞技场主面板")
	JJC_Show_Rank_Panel = AutoMessage.AllotMessage("JJC_Show_Rank_Panel", "通知客户端显示竞技场排行榜面板")
	JJC_Show_Exchange_Panel = AutoMessage.AllotMessage("JJC_Show_Exchange_Panel", "通知客户端显示竞技场兑换面板")
	JJC_Show_First_Fight_Rank = AutoMessage.AllotMessage("JJC_Show_First_Fight_Rank", "通知客户端显示竞技场第一次战斗排名")
	JJC_Show_Fight_Msg = AutoMessage.AllotMessage("JJC_Show_Fight_Msg", "通知客户端显示竞技场战斗提示信息")

class JJCRole(object):
	def __init__(self, jjcData):
		self.role_id = jjcData["role_id"]
		self.role_name = jjcData["role_name"]
		self.role_level = jjcData["role_level"]
		self.role_sex = jjcData["role_sex"]
		self.role_grade = jjcData["role_grade"]
		self.role_career = jjcData["role_career"]
		self.role_zdl = jjcData["role_zdl"]
		self.role_wing_id = jjcData["role_wing_id"]
		self.role_union_name = jjcData["role_union_name"]
		self.role_fashion_clithes = jjcData["role_fashion_clithes"]
		self.role_fashion_hat = jjcData["role_fashion_hat"]
		self.role_fashion_weapons = jjcData["role_fashion_weapons"]
		self.role_fashion_state = jjcData["role_fashion_state"]
		self.role_war_station = jjcData["role_war_station"]
		self.role_station_soul = jjcData["role_station_soul"]
		
	def HasChange(self):
		'''
		JJC数据发生改变
		'''
		JJC_BT.SetValue(self.__dict__)
		
	def HasDelete(self):
		JJC_BT.DelKey(self.role_id)
		JJC_BT.SaveData()
		
	def GetStandAppearence(self):
		return (self.role_id, self.role_name, self.role_sex, self.role_grade, self.role_career, self.role_level, \
			self.role_wing_id, self.role_fashion_clithes, self.role_fashion_hat, self.role_fashion_weapons, \
			self.role_fashion_state, self.role_war_station, self.role_station_soul)
		
	def GetRankPanelData(self):
		return (self.role_id, self.role_name, self.role_level, self.role_zdl, self.role_union_name)
	
	def GetKuaFuJJCData(self):
		return (self.role_id, self.role_name, self.role_level, self.role_sex, self.role_grade, 
			self.role_career, self.role_zdl, self.role_wing_id, self.role_fashion_clithes, 
			self.role_fashion_hat, self.role_fashion_weapons, self.role_fashion_state, 
			RoleFightData.GetRoleFightData(self.role_id), ZoneName.ZoneName, self.role_war_station, self.role_station_soul)
			
#===============================================================================
# DB AfterLoad
#===============================================================================
def JJCBTAfterLoad():
	global JJC_ROLE_OBJ_DICT
	
	jjcData = JJC_BT.GetData()
	if jjcData:
		for roleId, data in jjcData.iteritems():
			JJC_ROLE_OBJ_DICT[roleId] = JJCRole(data)
		
def JJCFrontListAfterLoadDB():
	'''
	持久化数据返回
	'''
	pass
	
def JJCRearListAfterLoadDB():
	'''
	持久化数据返回
	'''
	pass

#===============================================================================
# Show
#===============================================================================
def ShowJJCMainPanel(role):
	'''
	展示竞技场面板
	@param role:
	'''
	roleDataList = GetCanSeeJJCRoleData(role)
	
	role.SendObj(JJC_Show_Main_Panel, roleDataList)
	
	#是否显示兑换面板
	IsExchangeAwardToGet(role)
	
def ShowJJCRankPanel(role):
	'''
	展示竞技场排行榜面板
	@param role:
	'''
	rankDataList = GetJJCRankPanelData(role)
	
	role.SendObj(JJC_Show_Rank_Panel, rankDataList)
	
def ShowJJCExchangePanel(role):
	'''
	展示竞技场兑换面板
	@param role:
	'''
	exchangeDict = role.GetObj(EnumObj.JJC)[EXCHANGE_INDEX]
	
	exchangeStateList = []	#0:不可领, 1:可领取, 2:已领取
	for x in xrange(JJC_EXCHANGE_CNT_MAX):
		exchangeId = x + 1
		exchangeStateList.append(exchangeDict.get(exchangeId, 0))
		
	#同步客户端
	role.SendObj(JJC_Show_Exchange_Panel, exchangeStateList)
	
#===========================================================================
# 
#===========================================================================
def ActivateJJC(role):
	'''
	激活竞技场
	@param role:
	'''
	global JJC_FRONT_LIST
	global JJC_REAR_LIST
	
	roleId = role.GetRoleID()
	if len(JJC_FRONT_LIST) < JJC_FRONT_LIST_MAX:
		if roleId in JJC_FRONT_LIST:
			return
		#1~50
		JJC_FRONT_LIST.append(roleId)
	elif len(JJC_REAR_LIST) < JJC_REAR_LIST_MAX:
		if roleId in JJC_REAR_LIST:
			return
		#51~2000
		JJC_REAR_LIST.append(roleId)
	else:
		#2000名以后不创建
		return
	
	#更新战斗数据
	RoleFightData.UpdateRoleFightData(role)
	
	#创建竞技场Role
	CreateJJCRole(role)
	
def CreateJJCRole(role):
	'''
	创建竞技场Role
	@param role:
	'''
	roleId = role.GetRoleID()
	#创建
	jjcRole = JJCRole({"role_id": roleId, "role_name": role.GetRoleName(), 
		"role_level": role.GetLevel(), "role_sex": role.GetSex(), 
		"role_grade": role.GetGrade(), "role_career": role.GetCareer(), 
		"role_zdl": role.GetZDL(), "role_union_name": UnionMgr.GetUnionName(role), 
		"role_wing_id": role.GetWingID(), 
		"role_fashion_clithes":role.GetTI64(EnumTempInt64.FashionClothes),
		"role_fashion_hat":role.GetTI64(EnumTempInt64.FashionHat),
		"role_fashion_weapons":role.GetTI64(EnumTempInt64.FashionWeapons),
		"role_fashion_state":role.GetI1(EnumInt1.FashionViewState),
		"role_war_station":role.GetI16(EnumInt16.WarStationStarNum),
		"role_station_soul":role.GetI16(EnumInt16.StationSoulId)
		})
	#保存角色JJCRole对象
	global JJC_ROLE_OBJ_DICT
	JJC_ROLE_OBJ_DICT[roleId] = jjcRole
	
	#保存
	jjcRole.HasChange()
	
def DeleteJJCRole(roleId):
	'''
	删除竞技场Role
	@param roleId:
	'''
	global JJC_ROLE_OBJ_DICT
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRole = JJC_ROLE_OBJ_DICT[roleId]
	
	#删除
	jjcRole.HasDelete()
	del JJC_ROLE_OBJ_DICT[roleId]
	
def Update(role):
	'''
	更新角色数据(战斗数据和战斗力)
	@param role:
	'''
	#更新战斗数据
	RoleFightData.UpdateRoleFightData(role)
	
	roleId = role.GetRoleID()
	#更新JJCRoleObj战斗力数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_zdl = role.GetZDL()
	#更改玩家名
	jjcRoleObj.role_name = role.GetRoleName()
	#更改玩家性别
	jjcRoleObj.role_sex = role.GetSex()
	#更改公会名
	unionObj = role.GetUnionObj()
	if unionObj:
		jjcRoleObj.role_union_name = unionObj.name
	else:
		jjcRoleObj.role_union_name = ""
	#保存
	jjcRoleObj.HasChange()
	
def GetCanSeeJJCRoleData(role):
	'''
	获取可以看到的竞技场角色数据
	@param role:
	'''
	roleId = role.GetRoleID()
	canSeeRoleDataList = []			#需要同步客户端的角色数据[(rank,appearence), ...]
	canChallengeRoleIdList = []		#可以挑战的roleId列表
	
	jjcRank = GetJJCRank(roleId)
	groupConfig = GetGroupConfigByJJCRank(jjcRank)
	if not groupConfig:
		return canSeeRoleDataList
	
	#先添加自己的数据
	myJJCRoleObj = GetJJCRoleObj(roleId)
	if myJJCRoleObj:
		#排名，站立外形
		canSeeRoleDataList.append((jjcRank, myJJCRoleObj.GetStandAppearence()))
	
	#获取组内可以看到的挑战角色数据
	for canSeeRank in groupConfig.groupCanSeeRankList:
		jjcRoleId = GetRoleIdByJJCRank(canSeeRank)
		jjcRoleObj = GetJJCRoleObj(jjcRoleId)
		if not jjcRoleObj:
			continue
		#排名，站立外形
		canSeeRoleDataList.append((canSeeRank, jjcRoleObj.GetStandAppearence()))
		#加入可挑战列表
		canChallengeRoleIdList.append(jjcRoleId)
	
	#获取晋级可以看到的挑战角色数据
	if groupConfig.canBePromoted:
		
		for canSeeRank in groupConfig.promotedCanSeeRankList:
			jjcRoleId = GetRoleIdByJJCRank(canSeeRank)
			jjcRoleObj = GetJJCRoleObj(jjcRoleId)
			if not jjcRoleObj:
				continue
			#排名，站立外形
			canSeeRoleDataList.append((canSeeRank, jjcRoleObj.GetStandAppearence()))
			#加入可挑战列表
			canChallengeRoleIdList.append(jjcRoleId)
		
	#保存角色可挑战RoleID列表
	global JJC_ROLE_CAN_CHALLENGE_DICT
	if canChallengeRoleIdList:
		JJC_ROLE_CAN_CHALLENGE_DICT[roleId] = canChallengeRoleIdList
	
	return canSeeRoleDataList
	
def GetJJCRankPanelData(role):
	'''
	获取竞技场排行数据
	@param role:
	'''
	rankRoleDataList = []			#需要同步客户端的排行榜数据(最多10名)
	for idx in xrange(min(10, len(JJC_FRONT_LIST))):
		rankRoleId = JJC_FRONT_LIST[idx]
		rankRoleObj = GetJJCRoleObj(rankRoleId)
		if not rankRoleObj:
			continue
		rankRoleDataList.append(rankRoleObj.GetRankPanelData())
	
	return rankRoleDataList

def FirstChallenge(role):
	'''
	第一次挑战竞技场
	@param role:
	'''
	if not role.IsMonthCard():
		#挑战CD
		if role.GetCD(EnumCD.JJC_Challenge_CD):
			return
	
	#是否还有挑战次数
	if role.GetI8(EnumInt8.JJC_Challenge_Cnt) == 0:
		return
	
	#扣除挑战次数
	role.DecI8(EnumInt8.JJC_Challenge_Cnt, 1)
	
	#如果有月卡或者半年卡，则竞技场免CD
	if not role.IsMonthCard():
		#竞技场挑战CD
		role.SetCD(EnumCD.JJC_Challenge_CD, JJC_CHALLENGE_CD)
	
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		#print "GE_EXC in JJC FirstChallenge already in fight"
		return
	#战斗
	FightEx.PVE(role, 0, 9999, AfterFightFirst)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_JJC, 1))
	
def Challenge(role, beChallengedRoleId):
	'''
	挑战竞技场
	@param role:
	@param beChallengedRoleId: 被挑战角色ID
	'''
	roleId = role.GetRoleID()
	
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#不可以挑战自己
	if roleId == beChallengedRoleId:
		return
	
	if not role.IsMonthCard():
		if Environment.EnvIsFT():
			#繁体版
			if role.GetCD(EnumCD.FT_JJC_CD):
				return
		#挑战CD
		elif role.GetCD(EnumCD.JJC_Challenge_CD):
			return
	
	#是否还有挑战次数
	if role.GetI8(EnumInt8.JJC_Challenge_Cnt) == 0:
		return
		
	#判断被挑战者是否可以挑战
	if roleId not in JJC_ROLE_CAN_CHALLENGE_DICT:
		return
	canChallengeRoleIdList = JJC_ROLE_CAN_CHALLENGE_DICT[roleId]
	if beChallengedRoleId not in canChallengeRoleIdList:
		return
	
	#被挑战者是否有战斗数据(如果在线则更新战斗数据)
	beChallengedRole = cRoleMgr.FindRoleByRoleID(beChallengedRoleId)
	if beChallengedRole:
		#更新数据
		Update(beChallengedRole)
	beChallengedRoleFightData = RoleFightData.GetRoleFightData(beChallengedRoleId)
	if not beChallengedRoleFightData:
		return
	
	#扣除挑战次数
	role.DecI8(EnumInt8.JJC_Challenge_Cnt, 1)
	
	#如果有月卡或者半年卡，则竞技场免CD
	if not role.IsMonthCard():
		if Environment.EnvIsFT():
			nowCD = role.GetCD(EnumCD.JJC_Challenge_CD) + JJC_CHALLENGE_CD
			role.SetCD(EnumCD.JJC_Challenge_CD, nowCD)
			if nowCD >= JJC_FT_CHALLENGE_CD:
				role.SetCD(EnumCD.FT_JJC_CD, nowCD)
		else:	
			#竞技场挑战CD
			role.SetCD(EnumCD.JJC_Challenge_CD, JJC_CHALLENGE_CD)
	
	#更新数据
	Update(role)
	
	#战斗
	FightEx.PVP_JJC(role, 0, beChallengedRoleFightData, AfterFight, afterFightParam = beChallengedRoleId)
	
	#每日必做任务
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_JJC, 1))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_JJC, 1))
	
	#版本判断
	if Environment.EnvIsNA():
		#北美万圣节活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.challenge_jjc()
	elif Environment.EnvIsRU():
		#七日活动
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		#挑战竞技场
		sevenActMgr.challenge_jjc()
		
	
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_JJC)
	
def WinChallenge(role, beChallengedRoleId):
	'''
	挑战胜利
	@param role:
	@param beChallengedRoleId:
	'''
	global JJC_FRONT_LIST
	global JJC_REAR_LIST
	
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	#获取双方排名
	roleRank = GetJJCRank(roleId)
	beChallengedRoleRank = GetJJCRank(beChallengedRoleId)
	#如果排名比被挑战者的排名高，则不用发生变化
	if roleRank < beChallengedRoleRank:
		return
	else:
		if roleRank > 2000:
			#超过2000名，需要生成一份新的JJCRole
			CreateJJCRole(role)
			
			#替换排名
			if beChallengedRoleId in JJC_REAR_LIST:
				JJC_REAR_LIST[JJC_REAR_LIST.index(beChallengedRoleId)] = roleId
				
				#被打出2000名(可能已经流失，删除对应竞技场role)
				DeleteJJCRole(beChallengedRoleId)
		elif roleRank > 50:
			#大于50名的直接交换排名
			
			#分两种情况(被挑战者是前50名，被挑战者不是前50名)
			if beChallengedRoleRank > 50:
				if roleId in JJC_REAR_LIST and beChallengedRoleId in JJC_REAR_LIST:
					JJC_REAR_LIST[roleRank- JJC_REAR_LIST_FIRST_RANK_IDX] = beChallengedRoleId
					JJC_REAR_LIST[beChallengedRoleRank - JJC_REAR_LIST_FIRST_RANK_IDX] = roleId
			else:
				if roleId in JJC_REAR_LIST and beChallengedRoleId in JJC_FRONT_LIST:
					JJC_REAR_LIST[roleRank- JJC_REAR_LIST_FIRST_RANK_IDX] = beChallengedRoleId
					JJC_FRONT_LIST[beChallengedRoleRank - 1] = roleId
		else:
			#50名以内的，插入排名
			if roleId in JJC_FRONT_LIST and beChallengedRoleId in JJC_FRONT_LIST:
				JJC_FRONT_LIST.remove(roleId)
				JJC_FRONT_LIST.insert(beChallengedRoleRank - 1, roleId)
				
	#更新竞技场面板
	ShowJJCMainPanel(role)
	
	#被挑战者是否在线
	beChallengedRole = cRoleMgr.FindRoleByRoleID(beChallengedRoleId)
	if beChallengedRole:
		#更新竞技场面板
		ShowJJCMainPanel(beChallengedRole)
		groupConfig = GetGroupConfigByJJCRank(GetJJCRank(beChallengedRoleId))
		if groupConfig:
			msg = GlobalPrompt.JJC_FAILURE_MSG % (roleName, groupConfig.groupName, groupConfig.groupRank)
			#提示
			beChallengedRole.Msg(11, 0, msg)
			#通知客户端显示提示
			beChallengedRole.SendObj(JJC_Show_Fight_Msg, msg)
	
	#挑战第一名成功传闻
	if beChallengedRoleRank == 1:
		beChallengedJJCRoleObj = GetJJCRoleObj(beChallengedRoleId)
		if not beChallengedJJCRoleObj:
			return
		#传闻
		cRoleMgr.Msg(1, 0, GlobalPrompt.JJC_FIRST_HEARSAY % (roleName, beChallengedJJCRoleObj.role_name))
		
def LostChallenge(role, beChallengedRoleId):
	'''
	挑战失败
	@param role:
	@param beChallengedRoleId:
	'''
	#被挑战者是否在线
	beChallengedRole = cRoleMgr.FindRoleByRoleID(beChallengedRoleId)
	if beChallengedRole:
		msg = GlobalPrompt.JJC_SUCCESS_MSG % role.GetRoleName()
		#提示
		beChallengedRole.Msg(11, 0, msg)
		#通知客户端显示提示
		beChallengedRole.SendObj(JJC_Show_Fight_Msg, msg)
		
def WinAward(role, fightObj):
	#增加竞技场积分
	role.IncDI8(EnumDayInt8.JJC_Score, JJC_WIN_SCORE)
	
	#金币奖励
	level = role.GetLevel()
	challengeAwardConfig = JJCConfig.JJC_CHALLENGE_AWARD.get(level)
	################################################
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		winMoney = challengeAwardConfig.winMoney_fcm
	elif yyAntiFlag == 0:
		winMoney = challengeAwardConfig.winMoney
	else:
		winMoney = 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	
	#是否有未兑换的奖励
	IsExchangeAwardToGet(role)
	
	if winMoney and challengeAwardConfig:
		role.IncMoney(winMoney)
		#战斗后奖励统计显示
		roleId = role.GetRoleID()
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, winMoney)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumJJCScore, JJC_WIN_SCORE)
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_GetJJCScore, 0))
	
def LostAward(role, fightObj):
	#增加竞技场积分
	role.IncDI8(EnumDayInt8.JJC_Score, JJC_LOST_SCORE)
	
	#金币奖励
	level = role.GetLevel()
	challengeAwardConfig = JJCConfig.JJC_CHALLENGE_AWARD.get(level)
	################################################
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		lostMoney = challengeAwardConfig.lostMoney_fcm
	elif yyAntiFlag == 0:#原有收益
		lostMoney = challengeAwardConfig.lostMoney
	else:
		lostMoney = 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	
	#是否有未兑换的奖励
	IsExchangeAwardToGet(role)
	
	if lostMoney and challengeAwardConfig:
		role.IncMoney(lostMoney)
		#战斗后奖励统计显示
		roleId = role.GetRoleID()
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, lostMoney)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumJJCScore, JJC_LOST_SCORE)
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_GetJJCScore, 0))
	
def IsExchangeAwardToGet(role):
	'''
	是否有未兑换的奖励
	@param role:
	'''
	exchangeDict = role.GetObj(EnumObj.JJC)[EXCHANGE_INDEX]
	for x in xrange(JJC_EXCHANGE_CNT_MAX):
		exchangeId = x + 1
		if exchangeDict.get(exchangeId, 0) == 1:
			#显示兑换奖励面板
			ShowJJCExchangePanel(role)
		
def BuyJJCCnt(role):
	'''
	购买竞技场次数
	@param role:
	'''
	#今日是否还可以购买
	cnt = role.GetDI8(EnumDayInt8.JJC_Buy_Cnt)
	if cnt >= EnumGameConfig.JJC_Buy_Challenge_Cnt_Max:
		return
	
	buyCnt = cnt + 1
	#获取配置
	buyCntConfig = JJCConfig.JJC_BUY_CNT.get(buyCnt)
	if not buyCntConfig:
		return
	
	#消耗神石
	if role.GetRMB() < buyCntConfig.cost:
		return
	role.DecRMB(buyCntConfig.cost)
	
	#增加次数
	role.IncDI8(EnumDayInt8.JJC_Buy_Cnt, 1)
	role.IncI8(EnumInt8.JJC_Challenge_Cnt, 1)
	
def Exchange(role, exchangeId, backFunId):
	'''
	兑换
	@param role:
	@param exchangeId:
	@param backFunId:
	'''
	exchangeDict = role.GetObj(EnumObj.JJC)[EXCHANGE_INDEX]
	
	#是否可以领取
	if exchangeId not in exchangeDict:
		return
	
	#0:不可领, 1:可领取, 2:已领取
	if exchangeDict[exchangeId] != 1:
		return
	
	#奖励
	level = role.GetLevel()
	exchangeConfig = JJCConfig.JJC_EXCHANGE.get((level, exchangeId))
	if not exchangeConfig:
		return
	
	#设置已领取
	exchangeDict[exchangeId] = 2
	
	if exchangeConfig.reputation > 0:
		#声望奖励
		role.IncReputation(exchangeConfig.reputation)
	elif exchangeConfig.item:
		#物品奖励
		role.AddItem(*exchangeConfig.item)
	
	#回调客户端
	role.CallBackFunction(backFunId, None)
	
	#展示兑换面板
	ShowJJCExchangePanel(role)
	
	
	
def ResetChallengeCD(role):
	'''
	重置挑战CD
	@param role:
	'''
	challengeCD = role.GetCD(EnumCD.JJC_Challenge_CD)
	
	perMinuteNeedRMB = EnumGameConfig.JJC_PER_MINUTE_CD_NEED_RMB
	#版本判断
	if Environment.EnvIsNA():
		perMinuteNeedRMB = EnumGameConfig.JJC_PER_MINUTE_CD_NEED_RMB_NA
	
	needRMB = (challengeCD / 60 + 1) * perMinuteNeedRMB
	#RMB是否足够
	if role.GetRMB() < needRMB:
		return
	
	#扣RMB
	role.DecRMB(needRMB)
	
	#重置CD
	role.SetCD(EnumCD.JJC_Challenge_CD, 0)
	if Environment.EnvIsFT():
		role.SetCD(EnumCD.FT_JJC_CD, 0)
#===============================================================================
# 战斗相关
#===============================================================================
def OnLeave(fight, role, reason):
	# reason 0战斗结束离场；1战斗中途掉线
	print "OnLeave", role.GetRoleID(), reason
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None

def AfterFight(fight):
	beChallengedRoleId = fight.after_fight_param
	
	#获取战斗玩家
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	# fight.round当前战斗回合
	#print "fight round", fight.round
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#print "left win"
		#挑战成功
		WinChallenge(role, beChallengedRoleId)
		#日志
		with TraJJCWinChallengeAward:
			#胜利奖励
			WinAward(role, fight)
			#挑战成功,增加一个手下败将
			SlaveOperate.AddLoser(role.GetRoleID(), beChallengedRoleId)
	elif fight.result == -1:
		#print "right win"
		#挑战失败
		LostChallenge(role, beChallengedRoleId)
		#日志
		with TraJJCLostChallengeAward:
			#失败奖励
			LostAward(role, fight)
	else:
		#print "all lost"
		pass
	
	
	Event.TriggerEvent(Event.Eve_FB_AfterJJC, role, None)
	
def AfterFightFirst(fight):
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	#设置第一次挑战竞技场标志
	role.SetI1(EnumInt1.JJCFirstChallenge, 1)
	#无论胜负都要激活竞技场
	ActivateJJC(role)
	#更新竞技场面板
	ShowJJCMainPanel(role)
		
	# fight.round当前战斗回合
	#print "fight round", fight.round
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#print "left win"
		#日志
		with TraJJCWinChallengeAward:
			#胜利奖励
			WinAward(role, fight)
	elif fight.result == -1:
		#print "right win"
		#日志
		with TraJJCLostChallengeAward:
			#失败奖励
			LostAward(role, fight)
	else:
		#print "all lost"
		pass
	
	Event.TriggerEvent(Event.Eve_FB_AfterJJC, role, None)
	
def AfterPlay(fight):
	print "AfterPlay", fight.after_play_param
	
#===============================================================================
# Cron
#===============================================================================
def JJCRankAward():
	'''
	结算竞技场奖励
	'''
	#生成总排名列表
	rankList = []
	rankList.extend(JJC_FRONT_LIST)
	rankList.extend(JJC_REAR_LIST)
	
	for idx, roleId in enumerate(rankList):
		rank = idx + 1
		
		jjcRoleObj = GetJJCRoleObj(roleId)
		if not jjcRoleObj:
			continue
		
		#获取奖励配置
		rankAwardDict = JJCConfig.JJC_RANK_AWARD.get(jjcRoleObj.role_level)
		if not rankAwardDict:
			continue
		jjcRankAwardConfig = rankAwardDict.get(rank)
		if not jjcRankAwardConfig:
			continue
		jjcRankReputationConfig = JJCConfig.JJC_RANK_REPUTATION.get(rank)
		if not jjcRankReputationConfig:
			continue
		
		#时间(天数)， 金币，声望，魔晶，物品List
		AwardMgr.SetAward(roleId, EnumAward.JJCAward, money = jjcRankAwardConfig.money, reputation = jjcRankReputationConfig.reputation, itemList = jjcRankAwardConfig.itemList)
		
		#称号奖励
		if jjcRankAwardConfig.titleId:
			Title.AddTitle(roleId, jjcRankAwardConfig.titleId)
	
	from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
	selectList = rankList[0:200]
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Set_JJC, selectList)
	
	#跨服竞技场分配区域
	from Game.KuaFuJJC import KuaFuJJCMgr
	kuaFuJJCDataDict = {}
	for jjcRoleId in list(JJC_FRONT_LIST):
		if jjcRoleId not in JJC_ROLE_OBJ_DICT:
			continue
		kuaFuJJCDataDict[jjcRoleId] = JJC_ROLE_OBJ_DICT[jjcRoleId].GetKuaFuJJCData()
	KuaFuJJCMgr.AllotKuaFuJJCZone(kuaFuJJCDataDict)
	
def GMJJCSendData():
	#用GM指令把竞技场数据发给跨服
	global JJC_FRONT_LIST
	#跨服竞技场分配区域
	from Game.KuaFuJJC import KuaFuJJCMgr
	kuaFuJJCDataDict = {}
	for jjcRoleId in list(JJC_FRONT_LIST):
		if jjcRoleId not in JJC_ROLE_OBJ_DICT:
			continue
		kuaFuJJCDataDict[jjcRoleId] = JJC_ROLE_OBJ_DICT[jjcRoleId].GetKuaFuJJCData()
	KuaFuJJCMgr.AllotKuaFuJJCZone(kuaFuJJCDataDict)
#===============================================================================
# 接口
#===============================================================================
def GetJJCRank(roleId):
	'''
	获取竞技场排名
	@param roleId:
	'''
	if roleId in JJC_FRONT_LIST:
		return JJC_FRONT_LIST.index(roleId) + 1
	
	if roleId in JJC_REAR_LIST:
		return JJC_REAR_LIST.index(roleId) + JJC_REAR_LIST_FIRST_RANK_IDX
	
	return JJC_BROKEN_LIMIT_RANK

def GetJJCRoleObj(roleId):
	'''
	获取竞技场角色对象
	@param roleId:
	'''
	return JJC_ROLE_OBJ_DICT.get(roleId, None)

def GetRoleIdByJJCRank(rank):
	if rank >= 1 and rank <= JJC_FRONT_LIST_MAX:
		if rank > len(JJC_FRONT_LIST):
			return 0
		else:
			return JJC_FRONT_LIST[rank - 1]
	elif rank >= JJC_FRONT_LIST_MAX + 1 and rank <= 2000:
		if rank - JJC_FRONT_LIST_MAX > len(JJC_REAR_LIST):
			return 0
		else:
			return JJC_REAR_LIST[rank - JJC_FRONT_LIST_MAX - 1]
	else:
		return 0

def GetGroupRankByJJCRank(jjcRank):
	config = JJCConfig.JJC_RANK_TO_GROUP.get(jjcRank)
	if not config:
		return 0
	return config.groupRank

def GetGroupIdByJJCRank(jjcRank):
	config = JJCConfig.JJC_RANK_TO_GROUP.get(jjcRank)
	if not config:
		return 0
	return config.groupId

def GetGroupConfigByJJCRank(jjcRank):
	config = JJCConfig.JJC_RANK_TO_GROUP.get(jjcRank)
	if not config:
		return None
	return config


#===============================================================================
# 事件
#===============================================================================
def OnRoleExit(role, param):
	'''
	离线
	@param role:
	@param param:
	'''
	#更新数据
	Update(role)

def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#每日清理调用
	
	#重置挑战次数
	role.SetI8(EnumInt8.JJC_Challenge_Cnt, JJC_INIT_CHALLENGE_CNT)
	#重置兑换
	role.SetObj(EnumObj.JJC, {EXCHANGE_INDEX:{}})
	
def OnRoleLevelUp(role, param):
	'''
	升级
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	level = role.GetLevel()
	if level > JJC_ACTIVATE_LEVEL:
		#更新JJCRoleObj等级数据
		if roleId not in JJC_ROLE_OBJ_DICT:
			return
		jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
		jjcRoleObj.role_level = level
		#保存
		jjcRoleObj.HasChange()
	
def OnRoleJoinUnion(role, param):
	'''
	加入公会
	@param role:
	@param param:
	'''
	unionName = param
	roleId = role.GetRoleID()
	#更新JJCRoleObj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_union_name = unionName
	#保存
	jjcRoleObj.HasChange()
	
def OnRoleLeaveUnion(role, param):
	'''
	离开公会
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	#更新JJCRoleObj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_union_name = ""
	#保存
	jjcRoleObj.HasChange()
	
def OnRoleUpgrade(role, param):
	'''
	角色进阶
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	#更新JJCRoleObj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_grade = role.GetGrade()
	#保存
	jjcRoleObj.HasChange()

def AfterWarStation(role, param):
	'''
	战阵星级改变
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	#更新JJCRoleobj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_war_station = role.GetI16(EnumInt16.WarStationStarNum)
	#保存
	jjcRoleObj.HasChange()
	
def AfterFashionState(role, param):
	'''
	改变时装状态调用
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	#跟新JJCRoleobj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_fashion_state = role.GetI1(EnumInt1.FashionViewState)
	#保存
	jjcRoleObj.HasChange()
	
def AfterOnFashion(role, param):
	'''
	时装装备/脱后调用
	@param role:
	@param param:
	'''
	social_type, _ = param

	roleId = role.GetRoleID()
	#跟新JJCRoleobj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	
	if social_type == EnumSocial.RoleFashionClothes:#时装衣服
		jjcRoleObj.role_fashion_clithes = role.GetTI64(EnumTempInt64.FashionClothes)
	elif social_type == EnumSocial.RoleFashionHat:#时装帽子
		jjcRoleObj.role_fashion_hat = role.GetTI64(EnumTempInt64.FashionHat)
	elif social_type == EnumSocial.RoleFashionWeapons:#时装武器
		jjcRoleObj.role_fashion_weapons = role.GetTI64(EnumTempInt64.FashionWeapons)
	else:
		return
	#保存
	jjcRoleObj.HasChange()
	
def OnRoleOnWing(role, param):
	'''
	装备翅膀后调用
	@param role:
	@param param:
	'''
	wingId = param
	roleId = role.GetRoleID()
	#更新JJCRoleObj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_wing_id = wingId
	#保存
	jjcRoleObj.HasChange()
	
def OnRoleOffWing(role, param):
	'''
	卸下翅膀后调用
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	#更新JJCRoleObj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_wing_id = 0
	#保存
	jjcRoleObj.HasChange()
	
def OnRoleHeFu(role, param):
	'''
	合服调用
	@param role:
	@param param:
	'''
	#还没有挑战过竞技场
	if not role.GetI1(EnumInt1.JJCFirstChallenge):
		return
	
	#无论胜负都要激活竞技场
	ActivateJJC(role)

def AfterChangeStationSoul(role, param):
	'''
	阵灵改变
	'''
	roleId = role.GetRoleID()
	#更新JJCRoleobj数据
	if roleId not in JJC_ROLE_OBJ_DICT:
		return
	jjcRoleObj = JJC_ROLE_OBJ_DICT[roleId]
	jjcRoleObj.role_station_soul = role.GetI16(EnumInt16.StationSoulId)
	#保存
	jjcRoleObj.HasChange()
	
	
#===============================================================================
# 数组改变调用
#===============================================================================
def AfterChangeJJCScore(role, oldValue, newValue):
	'''
	竞技场积分改变
	@param role:
	@param oldValue:
	@param newValue:
	'''
	level = role.GetLevel()
	jjcScore = newValue
	exchangeDict = role.GetObj(EnumObj.JJC)[EXCHANGE_INDEX]
	
	#判断是否有可以领取的奖励
	for x in xrange(JJC_EXCHANGE_CNT_MAX):
		exchangeId = x + 1
		if exchangeId in exchangeDict:
			continue
		
		#配置
		exchangeConfig = JJCConfig.JJC_EXCHANGE.get((level, exchangeId))
		if not exchangeConfig:
			continue
		
		#判断竞技场积分是否满足条件
		if jjcScore >= exchangeConfig.score:
			exchangeDict[exchangeId] = 1
					
#===============================================================================
# 客户端请求
#===============================================================================
def RequestJJCOpenMainPanel(role, msg):
	'''
	客户端请求打开竞技场主面板
	@param role:
	@param msg:
	'''
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	#是否第一次挑战竞技场
	if role.GetI1(EnumInt1.JJCFirstChallenge):
		ShowJJCMainPanel(role)
	else:
		#发第一次战斗假人排名
		role.SendObj(JJC_Show_First_Fight_Rank, len(JJC_FRONT_LIST) + len(JJC_REAR_LIST) + 1)
	
def RequestJJCOpenRankPanel(role, msg):
	'''
	客户端请求打开竞技场排行榜
	@param role:
	@param msg:
	'''
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	ShowJJCRankPanel(role)
	
def RequestJJCOpenExchangePanel(role, msg):
	'''
	客户端请求打开竞技场兑换面板
	@param role:
	@param msg:
	'''
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	ShowJJCExchangePanel(role)
	
def RequestJJCChallenge(role, msg):
	'''
	客户端请求挑战竞技场
	@param role:
	@param msg:
	'''
	beChallengedRoleId = msg
	
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	#是否第一次挑战竞技场
	if role.GetI1(EnumInt1.JJCFirstChallenge):
		Challenge(role, beChallengedRoleId)
	else:
		FirstChallenge(role)
	
def RequestJJCBuyCnt(role, msg):
	'''
	客户端请求购买竞技场次数
	@param role:
	@param msg:
	'''
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	#日志
	with TraJJCBuyCnt:
		BuyJJCCnt(role)
	
def RequestJJCExchange(role, msg):
	'''
	客户端请求竞技场积分兑换
	@param role:
	@param msg:
	'''
	backFunId, exchangeId = msg
	
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	#日志
	with TraJJCExchange:
		Exchange(role, exchangeId, backFunId)
	
def RequestJJCResetChallengeCD(role, msg):
	'''
	客户端请求重置竞技场挑战
	@param role:
	@param msg:
	'''
	#等级是否满足条件
	if role.GetLevel() < JJC_ACTIVATE_LEVEL:
		return
	
	#日志
	with TraJJCResetCD:
		ResetChallengeCD(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#竞技场1~50名持久化列表
		JJC_FRONT_LIST = Contain.List("jjc_front_list", (2038, 1, 1), JJCFrontListAfterLoadDB, isSaveBig = False)
		#竞技场51~2000名持久化列表
		JJC_REAR_LIST = Contain.List("jjc_rear_list", (2038, 1, 1), JJCRearListAfterLoadDB)
	
	
	
	
	if Environment.HasLogic and not Environment.IsCross:
		JJC_BT = BigTable.BigTable("sys_jjc", 100, JJCBTAfterLoad)
		
		#结算竞技场奖励
		Cron.CronDriveBySecond((2038, 1, 1), JJCRankAward, H = "H == 22", M = "M == 0", S = "S == %s" % (cProcess.ProcessID % 59))
	
	if Environment.HasLogic:
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		#离线
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		#升级触发
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		
		#加入公会后调用
		Event.RegEvent(Event.Eve_AfterJoinUnion, OnRoleJoinUnion)
		#离开公会后调用
		Event.RegEvent(Event.Eve_AfterLeaveUnion, OnRoleLeaveUnion)
		#主角进阶后调用
		Event.RegEvent(Event.Eve_AfterRoleUpgrade, OnRoleUpgrade)
		#装备翅膀后调用
		Event.RegEvent(Event.Eve_AfterOnWing, OnRoleOnWing)
		#卸下翅膀后调用
		Event.RegEvent(Event.Eve_AfterOffWing, OnRoleOffWing)
		#合服后调用
		Event.RegEvent(Event.Eve_AfterRoleHeFu, OnRoleHeFu)
		#穿脱时装调用
		Event.RegEvent(Event.Eve_AfterOnFashion, AfterOnFashion)
		#时装显示状态调用
		Event.RegEvent(Event.Eve_AfterFashionState, AfterFashionState)
		#战阵星级改变调用
		Event.RegEvent(Event.Eve_AfterWarStation, AfterWarStation)
		#设置数组改变调用的函数
		cRoleDataMgr.SetDayInt8Fun(EnumDayInt8.JJC_Score, AfterChangeJJCScore)
		#阵灵改变
		Event.RegEvent(Event.Eve_AfterChangeStationSoul, AfterChangeStationSoul)
		
		#日志
		TraJJCBuyCnt = AutoLog.AutoTransaction("TraJJCBuyCnt", "竞技场购买次数")
		TraJJCExchange = AutoLog.AutoTransaction("TraJJCExchange", "竞技场兑换奖励")
		TraJJCResetCD = AutoLog.AutoTransaction("TraJJCResetCD", "竞技场重置CD")
		TraJJCWinChallengeAward = AutoLog.AutoTransaction("TraJJCWinChallengeReward", "竞技场挑战胜利奖励")
		TraJJCLostChallengeAward = AutoLog.AutoTransaction("TraJJCLostChallengeReward", "竞技场挑战失败奖励")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Open_Main_Panel", "客户端请求打开竞技场主面板"), RequestJJCOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Open_Rank_Panel", "客户端请求打开竞技场排行榜"), RequestJJCOpenRankPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Open_Exchange_Panel", "客户端请求打开竞技场兑换面板"), RequestJJCOpenExchangePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Challenge", "客户端请求挑战竞技场"), RequestJJCChallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Buy_Cnt", "客户端请求购买竞技场次数"), RequestJJCBuyCnt)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Exchange", "客户端请求竞技场积分兑换"), RequestJJCExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JJC_Reset_Challenge_CD", "客户端请求重置竞技场挑战"), RequestJJCResetChallengeCD)
