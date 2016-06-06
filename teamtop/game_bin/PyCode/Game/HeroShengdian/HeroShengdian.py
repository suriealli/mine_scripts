#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.HeroShengdian.HeroShengdian")
#===============================================================================
# 英雄圣殿
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumFightStatistics, GlobalPrompt
from Game.Fight import FightEx
from Game.VIP import VIPConfig
from Game.Role.Mail import Mail
from Game.Role import Status, Event
from Game.Persistence import Contain
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt1, EnumInt16, EnumDayInt8
from Game.HeroShengdian import HeroShengdianConfig

if "_HasLoad" not in dir():
	HeroShengdianRecord = AutoMessage.AllotMessage("HeroShengdianRecord", "英雄圣殿通关记录")
	
	HeroShengdianReward_Log = AutoLog.AutoTransaction("HeroShengdianReward_Log", "英雄圣殿奖励日志")
	HeroShengdianBuyCnt_Log = AutoLog.AutoTransaction("HeroShengdianBuyCnt_Log", "英雄圣殿购买次数")
	
def RequestFight(role, msg):
	'''
	请求挑战英雄圣殿 
	@param role:
	@param msg:神殿ID
	'''
	if not msg:
		return
	HeroShengdianIndex = msg
	
	#等级不到
	level = role.GetLevel()
	if level < EnumGameConfig.HS_MinLevel:
		return
	
	#没有通关次数了
	buyCnt = role.GetI16(EnumInt16.HeroShengdianBuyCnt)
	itemCnt = role.ItemCnt(EnumGameConfig.HS_ItemCoding)
	freeCnt = EnumGameConfig.HS_MaxCnt - role.GetDI8(EnumDayInt8.HeroShengdianFreeCnt)
	if freeCnt < 0:
		print 'GE_EXC, HeroShengdian RequestFight free cnt error role id %s' % role.GetRoleID()
		return
	
	if ((freeCnt + buyCnt) <= 0) and (not itemCnt):
		#没有行动力以及没有道具
		return
	
	#使用优先级： 免费行动力 --> 道具行动力 --> 购买的行动力
	useItem = False
	if freeCnt:
		useItem = False
	elif itemCnt:
		useItem = True
	elif buyCnt:
		useItem = False
	else:
		return
	
	#未通关前面神殿
	if HeroShengdianIndex > role.GetI16(EnumInt16.HeroShengdianMaxIndex) + 1:
		return
	
	#在战斗状态中
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#配置
	cfg = HeroShengdianConfig.HeroShengdian_Dict.get(HeroShengdianIndex)
	if not cfg:
		print "GE_EXC, HeroShengdian RequestFight can not find HeroShengdianIndex (%s) in HeroShengdian_Dict" % HeroShengdianIndex
		return
	
	if level < cfg.needLevel:
		role.Msg(2, 0, GlobalPrompt.HeroShengdian_LevelLimit)
		return
	
	FightEx.PVE_HS(role, cfg.fightType, cfg.mcid, AfterFight, (HeroShengdianIndex, cfg, useItem, freeCnt))
	
def AfterFight(fightObj):
	if fightObj is None:
		print "GE_EXC, HeroShengdian fight error"
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
	HeroShengdianIndex, cfg, useItem, freeCnt = fightObj.after_fight_param
	
	guanqiaName = GlobalPrompt.Return_ShengdianGuanqiaName(cfg.stageId)
	if not guanqiaName:
		return
	
	with HeroShengdianReward_Log:
		#扣次数
		if useItem:
			#如果是扣物品而又没有物品的话算失败
			if role.ItemCnt(EnumGameConfig.HS_ItemCoding) <= 0:
				print 'GE_EXC, HeroShengdian AfterFight error by role id' % roleID
				return
			role.DelItem(EnumGameConfig.HS_ItemCoding, 1)
		else:
			if not freeCnt:
				role.DecI16(EnumInt16.HeroShengdianBuyCnt, 1)
			else:
				role.IncDI8(EnumDayInt8.HeroShengdianFreeCnt, 1)
		
		fightRound = fightObj.round
		shengdianName = cfg.shengdianName
		
		global HeroShengdianRecordDict
		if HeroShengdianIndex not in HeroShengdianRecordDict:
			#首个通关
			HeroShengdianRecordDict[HeroShengdianIndex] = [[roleID, roleName], [roleID, roleName, fightRound]]
			HeroShengdianRecordDict.changeFlag = True
			
			role.SendObj(HeroShengdianRecord, HeroShengdianRecordDict.data)
			
			cRoleMgr.Msg(1, 0, GlobalPrompt.HeroShengdian_First % (roleName, shengdianName, guanqiaName))
			cRoleMgr.Msg(1, 0, GlobalPrompt.HeroShengdian_Fast % (roleName, fightRound, shengdianName, guanqiaName))
		elif fightRound < HeroShengdianRecordDict[HeroShengdianIndex][1][2]:
			#更新最快通关记录
			HeroShengdianRecordDict[HeroShengdianIndex][1] = [roleID, roleName, fightRound]
			HeroShengdianRecordDict.changeFlag = True
			
			role.SendObj(HeroShengdianRecord, HeroShengdianRecordDict.data)
			
			cRoleMgr.Msg(1, 0, GlobalPrompt.HeroShengdian_Fast % (roleName, fightRound, shengdianName, guanqiaName))
			
		#更新最大通关ID
		if HeroShengdianIndex > role.GetI16(EnumInt16.HeroShengdianMaxIndex):
			role.SetI16(EnumInt16.HeroShengdianMaxIndex, HeroShengdianIndex)
		
		tmpRewardList = []
		if cfg.randomRewardCoding:
			#随机奖励
			randomReward = (cfg.randomRewardCoding, cfg.HSI_RandomCnt.RandomOne())
			tmpRewardList = cfg.reward + [randomReward]
		else:
			tmpRewardList = cfg.reward
			
		if role.PackageEmptySize() < len(tmpRewardList):
			Mail.SendMail(roleID, GlobalPrompt.HeroShengdian_Mail_Title, GlobalPrompt.HeroShengdian_Mail_Sender, GlobalPrompt.HeroShengdian_Mail_Content, items = tmpRewardList)
		else:
			for item in tmpRewardList:
				role.AddItem(*item)
		fightObj.set_fight_statistics(roleID, EnumFightStatistics.EnumItems, tmpRewardList)
			
def RequestSaoDang(role, msg):
	'''
	请求扫荡 
	@param role:
	@param msg:
	'''
	if not msg:
		return
	HeroShengdianIndex = msg
	
	level = role.GetLevel()
	if level < EnumGameConfig.HS_MinLevel:
		return
	
	#未通关
	if HeroShengdianIndex > role.GetI16(EnumInt16.HeroShengdianMaxIndex):
		return
	
	#没有通关次数了
	buyCnt = role.GetI16(EnumInt16.HeroShengdianBuyCnt)
	itemCnt = role.ItemCnt(EnumGameConfig.HS_ItemCoding)
	freeCnt = EnumGameConfig.HS_MaxCnt - role.GetDI8(EnumDayInt8.HeroShengdianFreeCnt)
	if freeCnt < 0:
		print 'GE_EXC, HeroShengdian RequestSaoDang free cnt error role id %s' % role.GetRoleID()
		return
	
	if ((freeCnt + buyCnt) <= 0) and (not itemCnt):
		#没有行动力以及没有道具
		return
	
	#使用优先级： 免费行动力 --> 道具行动力 --> 购买的行动力
	useItem = False
	if freeCnt:
		useItem = False
	elif itemCnt:
		useItem = True
	elif buyCnt:
		useItem = False
	else:
		return
	
	#配置错误
	cfg = HeroShengdianConfig.HeroShengdian_Dict.get(HeroShengdianIndex)
	if not cfg:
		print "GE_EXC, HeroShengdian SaoDang can not find HeroShengdianID (%s) in HeroShengdian_Dict" % HeroShengdianIndex
		return
	
	if level < cfg.needLevel:
		role.Msg(2, 0, GlobalPrompt.HeroShengdian_LevelLimit)
		return
	
	#判断背包
	if role.PackageEmptySize() < len(cfg.reward):
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	with HeroShengdianReward_Log:
		#扣次数
		if useItem:
			role.DelItem(EnumGameConfig.HS_ItemCoding, 1)
		else:
			if not freeCnt:
				role.DecI16(EnumInt16.HeroShengdianBuyCnt, 1)
			else:
				role.IncDI8(EnumDayInt8.HeroShengdianFreeCnt, 1)
		
		tmpRewardList = []
		if cfg.randomRewardCoding:
			#随机奖励
			randomReward = (cfg.randomRewardCoding, cfg.HSI_RandomCnt.RandomOne())
			tmpRewardList = cfg.reward + [randomReward]
		else:
			tmpRewardList = cfg.reward
		
		tips = GlobalPrompt.Reward_Tips
		
		for item in tmpRewardList:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	role.Msg(2, 0, tips)
	
def RequestOpenPanel(role, msg):
	'''
	请求打开面板 -- 同步通关记录
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.HS_MinLevel:
		return
	
	global HeroShengdianRecordDict
	role.SendObj(HeroShengdianRecord, HeroShengdianRecordDict.data)
	
def RequestBuyCnt(role, msg):
	'''
	请求购买英雄圣殿行动次数
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.HS_MinLevel:
		return
	
	vipLevel = role.GetVIP()
	if not vipLevel:
		return
	vipCfg = VIPConfig._VIP_BASE.get(vipLevel)
	if not vipCfg:
		return
	
	buyCnt = role.GetDI8(EnumDayInt8.HeroShengdianTodayBuyCnt)
	if buyCnt >= vipCfg.heroShengdianBuyCnt:
		return
	buyCnt += 1
	
	cfg = HeroShengdianConfig.HeroShengdianCnt_Dict.get(buyCnt)
	if not cfg:
		print "GE_EXC, HeroShengdian BuyCnt can not find cnt (%s) in HeroShengdianCnt_Dict" % buyCnt
		return
	
	if role.GetUnbindRMB() < cfg.needUnbindRMB:
		return
	
	with HeroShengdianBuyCnt_Log:
		role.DecUnbindRMB(cfg.needUnbindRMB)
		role.IncDI8(EnumDayInt8.HeroShengdianTodayBuyCnt, 1)
		role.IncI16(EnumInt16.HeroShengdianBuyCnt, 1)
	
def AfterChangeName(role, param):
	global HeroShengdianRecordDict
	if not HeroShengdianRecordDict:
		return
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	
	for recordList in HeroShengdianRecordDict.values():
		for record in recordList:
			if record[0] != roleID:
				continue
			#改名
			record[1] = roleName
			HeroShengdianRecordDict.changeFlag = True

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#{shengdianIndex:[[最早通关  roleId, roleName], [最快通关 roleId, roleName, fightRound]]}
		HeroShengdianRecordDict = Contain.Dict("HeroShengdianRecordDict", (2038, 1, 1), isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterChangeName, AfterChangeName)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroShengdian_OpenPanel", "请求打开英雄圣殿面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroShengdian_Fight", "请求英雄圣殿挑战"), RequestFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroShengdian_SaoDang", "请求英雄圣殿扫荡"), RequestSaoDang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HeroShengdian_BuyCnt", "请求购买英雄圣殿行动次数"), RequestBuyCnt)
		
