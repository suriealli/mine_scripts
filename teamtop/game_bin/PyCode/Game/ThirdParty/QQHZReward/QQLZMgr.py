#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZReward.QQLZMgr")
#===============================================================================
# 蓝钻特权
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.ThirdParty import QVIP
from Game.ThirdParty.QQHZReward import QQHZConfig
from Game.Role.Data import EnumDayInt1,EnumInt1, EnumInt8

def RequestGetQQLZdaily(role, msg):
	'''
	客户端请求获取蓝钻每日奖励
	'''
	#检测是否为蓝钻用户
	vip_type = QVIP.GetQVip(role)
	if not vip_type:
		return
	if vip_type != QVIP.LZ:
		return
	vip_level = QVIP.GetQVipLevel(role)
	if not vip_level:
		return
	#检查是否已领取
	if role.GetDI1(EnumDayInt1.QQLZDailyReward):
		return
	
	#读取VIP每日奖励配置表,根据玩家等级获取奖励ID
	rewardDict = QQHZConfig.QQHZ_DAILY_REWARD.get(vip_level)
	if not rewardDict:
		print "GE_EXC,can't find QQLZdaily by level (%s)" % vip_level
		return
	role_level = role.GetLevel()
	LZ_rewardId = 0
	for rewardId, leveleval in rewardDict.iteritems():
		min_level, max_level = leveleval
		if min_level <= role_level <= max_level:
			LZ_rewardId = rewardId
			break
	if not LZ_rewardId:
		return
	#根据奖励ID读取每日奖励表
	dailyConfig = QQHZConfig.QQHZ_DAILY_REWARD_DICT.get(LZ_rewardId)
	if not dailyConfig:
		print "GE_EXC,can not find rewardId(%s) in DailyReward" % LZ_rewardId
		return

	rewards = []
	vip_rewards = dailyConfig.LZrewards
	#年钻额外奖励
	years_reward = dailyConfig.LZYearsRewards
	
	rewards.extend(vip_rewards)
	if QVIP.GetQVipYear(role):
		rewards.extend(years_reward)
	#是否是豪华蓝钻
	if role.GetQQHHLZ():
		rewards.extend(dailyConfig.LZHHReward)
	#判断背包
	if role.PackageEmptySize() < len(rewards):
		#提示
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return

	#设置次数
	role.SetDI1(EnumDayInt1.QQLZDailyReward, 1)
	with QQLZDayAward:
		if dailyConfig.bindRMB:
			role.IncBindRMB(dailyConfig.bindRMB)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % dailyConfig.bindRMB)
		if dailyConfig.money:
			role.IncMoney(dailyConfig.money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % dailyConfig.money)
		if not rewards:
			return
		for coding, cnt in rewards:
			role.AddItem(coding, cnt)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (coding, cnt))
			
def RequestGetQQLZnovice(role, msg):
	'''
	获取蓝钻新手礼包，只能获取一次
	'''
	#检测是否为蓝钻用户
	vip_type = QVIP.GetQVip(role)
	if not vip_type:
		return
	if vip_type != QVIP.LZ:
		return
	#检查是否已领取过
	if role.GetI1(EnumInt1.QQLZRewardStatus):
		return
	
	vip_level = QVIP.GetQVipLevel(role)
	if not vip_level:
		return
	#根据蓝钻等级获取奖励
	noviceConfig = QQHZConfig.QQHZ_NOVICE_REWARD.get(vip_level)
	if not noviceConfig:
		print "GE_EXC,can't find QQLZnovice by level (%s)" % vip_level
		return
	
	#根据vip类型分奖励
	rewards = noviceConfig.LZrewards
	
	#判断背包
	if role.PackageEmptySize() < len(rewards):
		#提示
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		
	role.SetI1(EnumInt1.QQLZRewardStatus, True)
	with QQLZNovice:
		if noviceConfig.bindRMB:
			role.IncBindRMB(noviceConfig.bindRMB)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % noviceConfig.bindRMB)
		if noviceConfig.money:
			role.IncMoney(noviceConfig.money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % noviceConfig.money)
		if not rewards:
			return
		for coding, cnt in rewards:
			role.AddItem(coding, cnt)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (coding, cnt))
				
def RequestGetQQLZlevel(role, msg):
	'''
	蓝钻等级礼包
	'''
	#检测是否为蓝钻用户
	vip_type = QVIP.GetQVip(role)
	if not vip_type:
		return
	if vip_type != QVIP.LZ:
		return
	#获取当前玩家礼包的索引
	nowPackIndex = role.GetI8(EnumInt8.QQLZLevelIndex)
	
	#礼包领完了
	if nowPackIndex == -1:
		role.Msg(2, 0, GlobalPrompt.NavicePackEnd)
		return
	
	#获取礼包配置
	cfg = QQHZConfig.QQHZ_LEVEL_REWARD.get(nowPackIndex)
	if not cfg:
		print "GE_EXC, can not find QQLZLevel index (%s)" % nowPackIndex
		return
	
	#等级不足
	if role.GetLevel() < cfg.level:
		return

	rewards = cfg.LZitems
	
	#背包空间不足
	if role.PackageEmptySize() < len(rewards):
		role.Msg(2, 0, GlobalPrompt.NavicePackLessPackage)
		return
	
	#设置可领取下一个礼包
	role.SetI8(EnumInt8.QQLZLevelIndex, cfg.nextPackIndex)

	#发奖
	with QQLZLevel:
		if cfg.addTarot:
			role.AddTarotCard(cfg.addTarot, 1)
			role.Msg(2, 0, GlobalPrompt.Tarot_Tips % (cfg.addTarot, 1))
		if not rewards:
			return
		for rd in rewards:
			role.AddItem(*rd)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (rd[0], rd[1]))

def AfterLogin(role, param):
	'''
	玩家登录后
	@param role:
	@param param:
	'''
	#为老玩家做下数据兼容
	if role.GetI8(EnumInt8.QQLZLevelIndex) == 0:
		role.SetI8(EnumInt8.QQLZLevelIndex, 1)

if "_HasLoad" not in dir():
	#日志
	QQLZDayAward = AutoLog.AutoTransaction("QQLZDayAward", "蓝钻用户每日礼包")
	QQLZNovice = AutoLog.AutoTransaction("QQLZNovice","蓝钻用户新手礼包")
	QQLZLevel = AutoLog.AutoTransaction("QQLZLevel","蓝钻用户等级礼包")
	#事件
	Event.RegEvent(Event.Eve_AfterLoginJoinScene, AfterLogin)
	if Environment.EnvIsQQ():
		if Environment.HasLogic and not Environment.IsCross:
			#注册消息
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQLZdaliy_Rewards", "客户端请求获取每日蓝钻礼包"), RequestGetQQLZdaily)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQLZnovice_Rewards", "客户端请求获取蓝钻新手礼包"), RequestGetQQLZnovice)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQLZlevel_Rewards", "客户端请求获取蓝钻等级礼包"), RequestGetQQLZlevel)
			
		