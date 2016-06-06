#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.HeroTemple.HeroTemple")
#===============================================================================
# 英灵神殿
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumFightStatistics, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.HeroTemple import HeroTempleConfig
from Game.Role import Status, Event
from Game.Role.Data import EnumInt1, EnumInt16, EnumDayInt8, EnumCD, EnumTempObj
from Game.Fight import FightEx
from Game.Persistence import Contain
from Game.Role.Mail import Mail
from Game.VIP import VIPConfig
from Game.Activity import ExtendReward
from Game.ThirdParty.QQLZ import QQLZShopMgr

if "_HasLoad" not in dir():
	HeroTempleRecord = AutoMessage.AllotMessage("HeroTempleRecord", "英灵神殿通关记录")
	
	HeroTempleReward_Log = AutoLog.AutoTransaction("HeroTempleReward_Log", "英灵神殿奖励日志")
	HeroTempleBuyCnt_Log = AutoLog.AutoTransaction("HeroTempleBuyCnt_Log", "英灵神殿购买次数")
	
def RequestFight(role, msg):
	'''
	请求挑战英灵神殿 
	@param role:
	@param msg:神殿ID
	'''
	if not msg:
		return
	heroTempleIndex = msg
	
	#等级不到
	level = role.GetLevel()
	if level < EnumGameConfig.HT_MinLevel:
		return
	#没有通关次数了
	if EnumGameConfig.HT_MaxCnt + role.GetDI8(EnumDayInt8.HeroTempBuyCnt) - role.GetDI8(EnumDayInt8.HeroTempCnt) <= 0:
		return
	#未通关需要的副本
	if role.GetI16(EnumInt16.FB_Active_ID) < EnumGameConfig.HT_NeedFBID:
		return
	#未通关前面神殿
	if heroTempleIndex > role.GetI16(EnumInt16.HeroTempleMaxIndex) + 1:
		return
	#在战斗状态中
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	################################################
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	rewardFlag = True
	if yyAntiFlag == 1:#收益减半
		cfg = HeroTempleConfig.HeroTemple_fcm_Dict.get(heroTempleIndex)
	elif yyAntiFlag == 0:#原有收益
		#配置错误
		cfg = HeroTempleConfig.HeroTemple_Dict.get(heroTempleIndex)
	else:
		cfg = HeroTempleConfig.HeroTemple_Dict.get(heroTempleIndex)
		rewardFlag = False
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	#配置
	if not cfg:
		print "GE_EXC, HeroTemple RequestFight can not find heroTempleIndex (%s) in HeroTemple_Dict" % heroTempleIndex
		return
	if level < cfg.needLevel:
		role.Msg(2, 0, GlobalPrompt.HeroTemple_LevelLimit)
		return
	
	FightEx.PVE_HT(role, cfg.fightType, cfg.mcid, AfterFight, (heroTempleIndex, cfg, rewardFlag))
	
	Event.TriggerEvent(Event.Eve_FB_HT, role)
	
def AfterFight(fightObj):
	if fightObj is None:
		print "GE_EXC, HeroTemple fight error"
		return
	#失败不处理
	if fightObj.result != 1:
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	heroTempleIndex, cfg, rewardFlag = fightObj.after_fight_param
	if not cfg:
		print "GE_EXC, HeroTemple RequestFight can not find HeroTempleReward_Dict (%s) in HeroTemple_Dict" % heroTempleIndex
		return
	guanqiaName = GlobalPrompt.Return_GuanqiaName(cfg.stageId)
	if not guanqiaName:
		return
	#扣次数
	role.IncDI8(EnumDayInt8.HeroTempCnt, 1)
	
	fightRound = fightObj.round
	templeName = cfg.templeName
	global HeroTempleRecordDict
	if heroTempleIndex not in HeroTempleRecordDict:
		#首个通关
		HeroTempleRecordDict[heroTempleIndex] = [[roleID, roleName], [roleID, roleName, fightRound]]
		role.SendObj(HeroTempleRecord, HeroTempleRecordDict.data)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroTemple_First % (roleName, templeName, guanqiaName))
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroTemple_Fast % (roleName, fightRound, templeName, guanqiaName))
	elif fightRound < HeroTempleRecordDict[heroTempleIndex][1][2]:
		#更新最快通关记录
		HeroTempleRecordDict[heroTempleIndex][1] = [roleID, roleName, fightRound]
		HeroTempleRecordDict.changeFlag = True
		role.SendObj(HeroTempleRecord, HeroTempleRecordDict.data)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroTemple_Fast % (roleName, fightRound, templeName, guanqiaName))
		
	#发奖励
	with HeroTempleReward_Log:
		#更新最大通关ID
		if heroTempleIndex > role.GetI16(EnumInt16.HeroTempleMaxIndex):
			role.SetI16(EnumInt16.HeroTempleMaxIndex, heroTempleIndex)
		if rewardFlag:
			tmpRewardList = []
			if cfg.randomRewardCoding:
				#随机奖励
				randomReward = (cfg.randomRewardCoding, cfg.HT_RandomCnt.RandomOne())
				tmpRewardList = cfg.reward + [randomReward] + ExtendReward.GetExtendReward(role, (2, 1)).items()
			else:
				tmpRewardList = cfg.reward + ExtendReward.GetExtendReward(role, (2, 1)).items()
				
			if role.GetCD(EnumCD.Card_HalfYear):
				rewardMoney = cfg.rewardMoney + cfg.rewardMoney * EnumGameConfig.Card_HalfYearGold / 100
			else:
				rewardMoney = cfg.rewardMoney
			
			if role.PackageEmptySize() < len(tmpRewardList):
				Mail.SendMail(roleID, GlobalPrompt.HeroTemple_Mail_Title, GlobalPrompt.HeroTemple_Mail_Sender, GlobalPrompt.HeroTemple_Mail_Content, items=tmpRewardList, money=rewardMoney)
			else:
				role.IncMoney(rewardMoney)
				for item in tmpRewardList:
					role.AddItem(*item)
			fightObj.set_fight_statistics(roleID, EnumFightStatistics.EnumMoney, rewardMoney)
			fightObj.set_fight_statistics(roleID, EnumFightStatistics.EnumItems, tmpRewardList)
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.ChallengeHero()
			HalloweenNAMgr.ChallengeHeroCnt()
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HeroTemple, 1))
	
def RequestSaoDang(role, msg):
	'''
	请求扫荡 
	@param role:
	@param msg:
	'''
	if not msg:
		return
	heroTempleIndex = msg
	
	level = role.GetLevel()
	if level < EnumGameConfig.HT_MinLevel:
		return
	#未通关
	if heroTempleIndex > role.GetI16(EnumInt16.HeroTempleMaxIndex):
		return
	#没有通关次数了
	if EnumGameConfig.HT_MaxCnt + role.GetDI8(EnumDayInt8.HeroTempBuyCnt) - role.GetDI8(EnumDayInt8.HeroTempCnt) <= 0:
		return
	################################################
	#YY防沉迷对奖励特殊处理
	SendReward = True
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		cfg = HeroTempleConfig.HeroTemple_fcm_Dict.get(heroTempleIndex)
	elif yyAntiFlag == 0:#原有收益
		#配置错误
		cfg = HeroTempleConfig.HeroTemple_Dict.get(heroTempleIndex)
	else:
		cfg = HeroTempleConfig.HeroTemple_Dict.get(heroTempleIndex)
		SendReward = False
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	if not cfg:
		print "GE_EXC, HeroTemple SaoDang can not find heroTempleID (%s) in HeroTemple_Dict" % heroTempleIndex
		return
	#如果VIP < 2, 且不是蓝钻渠道登录的蓝钻用户，不允许扫荡
	if role.GetVIP() < 2 and not QQLZShopMgr.IsQQLZ(role):
		return
	if level < cfg.needLevel:
		role.Msg(2, 0, GlobalPrompt.HeroTemple_LevelLimit)
		return
	
	#判断背包, +1是因为boss会随机出多一个物品, 但是在开启了砸龙蛋活动后还是可能有背包满的情况
	if role.PackageEmptySize() < len(cfg.reward) + 1:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	#扣次数
	role.IncDI8(EnumDayInt8.HeroTempCnt, 1)
	
	tmpRewardList = []
	if cfg.randomRewardCoding:
		#随机奖励
		randomReward = (cfg.randomRewardCoding, cfg.HT_RandomCnt.RandomOne())
		tmpRewardList = cfg.reward + [randomReward] + ExtendReward.GetExtendReward(role, (2, 1)).items()
	else:
		tmpRewardList = cfg.reward + ExtendReward.GetExtendReward(role, (2, 1)).items()
	
	rewardMoney = 0
	#发奖励
	isHalfYearCard = False
	if Environment.EnvIsNA():
		if role.GetCD(EnumCD.Card_Year):
			isHalfYearCard = True
	else:
		if role.GetCD(EnumCD.Card_HalfYear):
			isHalfYearCard = True
	if isHalfYearCard:
		rewardMoney = cfg.rewardMoney + cfg.rewardMoney * EnumGameConfig.Card_HalfYearGold / 100
	else:
		rewardMoney = cfg.rewardMoney
	
	if SendReward:
		tips = GlobalPrompt.Reward_Tips
		
		with HeroTempleReward_Log:
			role.IncMoney(rewardMoney)
			tips += GlobalPrompt.Money_Tips % rewardMoney
			for item in tmpRewardList:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
		
		if isHalfYearCard:
			role.Msg(2, 0, tips + GlobalPrompt.Card_GoldBuff_Tips)
		else:
			role.Msg(2, 0, tips)
	
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.ChallengeHeroCnt()
	
	Event.TriggerEvent(Event.Eve_FB_HT, role)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HeroTemple, 1))
	
def RequestOpenPanel(role, msg):
	'''
	请求打开面板 -- 同步通关记录
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.HT_MinLevel:
		return
	
	global HeroTempleRecordDict
	role.SendObj(HeroTempleRecord, HeroTempleRecordDict.data)
	
def RequestBuyCnt(role, msg):
	'''
	请求购买英灵神殿行动次数
	@param role:
	@param msg:
	'''
	vipLevel = role.GetVIP()
	if not vipLevel:
		return
	if role.GetLevel() < EnumGameConfig.HT_MinLevel:
		return
	buyCnt = role.GetDI8(EnumDayInt8.HeroTempBuyCnt)
	vipCfg = VIPConfig._VIP_BASE.get(vipLevel)
	if not vipCfg:
		return
	if buyCnt >= vipCfg.heroTempleBuyCnt:
		return
	buyCnt += 1
	
	cfg = HeroTempleConfig.HeroTempleCnt_Dict.get(buyCnt)
	if not cfg:
		print "GE_EXC, HeroTemple BuyCnt can not find cnt (%s) in HeroTempleCnt_Dict" % buyCnt
		return
	if role.GetBindRMB() + role.GetUnbindRMB() < cfg.needRMB:
		return
	
	with HeroTempleBuyCnt_Log:
		role.DecRMB(cfg.needRMB)
		role.SetDI8(EnumDayInt8.HeroTempBuyCnt, buyCnt)
	
def AfterChangeName(role, param):
	global HeroTempleRecordDict
	if not HeroTempleRecordDict:
		return
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	
	for recordList in HeroTempleRecordDict.values():
		for record in recordList:
			if record[0] != roleID:
				continue
			#改名
			record[1] = roleName
			HeroTempleRecordDict.changeFlag = True

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		HeroTempleRecordDict = Contain.Dict("HeroTempleRecordDict", (2038, 1, 1), isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterChangeName, AfterChangeName)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroTemple_OpenPanel", "请求打开英灵神殿面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroTemple_Fight", "请求英灵神殿挑战"), RequestFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroTemple_SaoDang", "请求英灵神殿扫荡"), RequestSaoDang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroTemple_BuyCnt", "请求购买英灵神殿行动次数"), RequestBuyCnt)
		
