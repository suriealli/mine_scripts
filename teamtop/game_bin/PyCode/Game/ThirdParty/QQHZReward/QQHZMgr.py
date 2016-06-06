#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZReward.QQHZMgr")
#===============================================================================
#QQ黄钻特权管理 腾讯 繁体
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.Title import Title
from Game.Role.Data import EnumDayInt1, EnumInt1, EnumInt8, EnumTempInt64
from Game.ThirdParty import QVIP
from Game.ThirdParty.QQHZReward import QQHZConfig

if "_HasLoad" not in dir():
	QQHZ_TITLE_ID = 35		#黄钻称号ID

def RequestGetQQHZdaily(role, msg):
	'''
	客户端请求获取黄钻每日奖励
	'''
	#检查是否已领取
	if role.GetDI1(EnumDayInt1.QQHZDailyReward):
		return
	
	#检测是否为黄钻用户
	vip_level = 0
	ftvip = 0
	YearBool = False
	vip_type = 0
	if Environment.EnvIsQQ():
		#腾讯
		vip_type = QVIP.GetQVip(role)
		if not vip_type:
			return
		if vip_type != QVIP.HZ:
			return
		vip_level = QVIP.GetQVipLevel(role)
		if not vip_level:
			return
		YearBool = QVIP.GetQVipYear(role)
	elif Environment.EnvIsFT():
		#繁体
		ftvip = role.GetFTVIP()
		if ftvip != 1 and ftvip != 2:
			return
		#繁体黄钻 = 腾讯黄钻8级
		vip_level = 8
		vip_type = QVIP.HZ
		if ftvip == 2:
			#繁体蓝钻 = 年费
			YearBool = True
	else:
		return
		
	
	#读取VIP每日奖励配置表,根据玩家等级获取奖励ID
	rewardDict = QQHZConfig.QQHZ_DAILY_REWARD.get(vip_level)
	if not rewardDict:
		print "GE_EXC,can't find QQHZdaily by level (%s)" % vip_level
		return
	role_level = role.GetLevel()
	HZ_rewardId = 0
	for rewardId, leveleval in rewardDict.iteritems():
		min_level, max_level = leveleval
		if min_level <= role_level <= max_level:
			HZ_rewardId = rewardId
			break
	if not HZ_rewardId:
		return
	#根据奖励ID读取每日奖励表
	dailyConfig = QQHZConfig.QQHZ_DAILY_REWARD_DICT.get(HZ_rewardId)
	if not dailyConfig:
		print "GE_EXC,can not find rewardId(%s) in DailyReward" % HZ_rewardId
		return
	
	rewards = []
	vip_rewards = []#记录vip奖励
	years_reward = []#记录年钻额外奖励
	#根据vip类型读取不同的配置
	if vip_type == QVIP.HZ:
		vip_rewards = dailyConfig.HZrewards
		#年钻额外奖励
		years_reward = dailyConfig.HZYearsRewards

	
	
	rewards.extend(vip_rewards)
	if YearBool:
		rewards.extend(years_reward)
	
	#判断背包
	if role.PackageEmptySize() < len(rewards):
		#提示
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return

	#设置次数
	role.SetDI1(EnumDayInt1.QQHZDailyReward, 1)
	with QQHZDayAward:
		if not Environment.EnvIsFT():
			if dailyConfig.bindRMB:
				role.IncBindRMB(dailyConfig.bindRMB)
				role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % dailyConfig.bindRMB)
		else:
			rewardbindrmb = dailyConfig.bindRMB
			if role.GetFTVIP() == 2:
				rewardbindrmb += dailyConfig.HZYearsRMB
			if rewardbindrmb:
				role.IncBindRMB(rewardbindrmb)
				role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % rewardbindrmb)
				
		if dailyConfig.money:
			role.IncMoney(dailyConfig.money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % dailyConfig.money)
		#奖励
		for coding, cnt in rewards:
			role.AddItem(coding, cnt)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (coding, cnt))
			
def RequestGetQQHZnovice(role, msg):
	'''
	获取黄钻新手礼包，只能获取一次
	'''
	#检查是否已领取过
	if role.GetI1(EnumInt1.QQHZRewardStatus):
		return
	vip_level = 0
	vip_type = 0
	#检测是否为黄钻用户
	if Environment.EnvIsQQ():
		vip_type = QVIP.GetQVip(role)
		if not vip_type:
			return
		if vip_type != QVIP.HZ:
			return
		vip_level = QVIP.GetQVipLevel(role)
		if not vip_level:
			return
	elif Environment.EnvIsFT():
		#繁体
		ftvip = role.GetFTVIP()
		if ftvip != 1 and ftvip != 2:
			return
		#繁体黄钻 = 腾讯黄钻8级
		vip_level = 8
		vip_type = QVIP.HZ
	else:
		return
	#根据黄钻等级获取奖励
	noviceConfig = QQHZConfig.QQHZ_NOVICE_REWARD.get(vip_level)
	if not noviceConfig:
		print "GE_EXC,can't find QQHZnovice by level (%s)" % vip_level
		return
	
	#根据vip类型分奖励
	rewards = []
	if vip_type == QVIP.HZ:
		rewards = noviceConfig.HZrewards
	
	#判断背包
	if role.PackageEmptySize() < len(rewards):
		#提示
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		
	role.SetI1(EnumInt1.QQHZRewardStatus, True)
	with QQHZNovice:
		if noviceConfig.bindRMB:
			role.IncBindRMB(noviceConfig.bindRMB)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % noviceConfig.bindRMB)
		if noviceConfig.money:
			role.IncMoney(noviceConfig.money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % noviceConfig.money)
		#奖励
		for coding, cnt in rewards:
			role.AddItem(coding, cnt)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (coding, cnt))
				
def RequestGetQQHZlevel(role, msg):
	'''
	黄钻等级礼包
	'''
	#检测是否为黄钻用户
	vip_type = 0
	#检测是否为黄钻用户
	if Environment.EnvIsQQ():
		vip_type = QVIP.GetQVip(role)
		if not vip_type:
			return
		if vip_type != QVIP.HZ:
			return
	elif Environment.EnvIsFT():
		#繁体
		ftvip = role.GetFTVIP()
		if ftvip != 1 and ftvip != 2:
			return
		vip_type = QVIP.HZ
	else:
		return
	
	#获取当前玩家礼包的索引
	nowPackIndex = role.GetI8(EnumInt8.QQVIPLevelIndex)
	
	#礼包领完了
	if nowPackIndex == -1:
		role.Msg(2, 0, GlobalPrompt.NavicePackEnd)
		return
	
	#获取礼包配置
	cfg = QQHZConfig.QQHZ_LEVEL_REWARD.get(nowPackIndex)
	if not cfg:
		print "GE_EXC, can not find QQHZLevel index (%s)" % nowPackIndex
		return
	
	#等级不足
	if role.GetLevel() < cfg.level:
		return
	rewards = []
	if vip_type == QVIP.HZ:
		rewards = cfg.HZitems
	
	#背包空间不足
	if role.PackageEmptySize() < len(rewards):
		role.Msg(2, 0, GlobalPrompt.NavicePackLessPackage)
		return
	
	#设置可领取下一个礼包
	role.SetI8(EnumInt8.QQVIPLevelIndex, cfg.nextPackIndex)

	#发奖
	with QQHZLevel:
		if cfg.addTarot:
			role.AddTarotCard(cfg.addTarot, 1)
			role.Msg(2, 0, GlobalPrompt.Tarot_Tips % (cfg.addTarot, 1))
		for rd in rewards:
			role.AddItem(*rd)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (rd[0], rd[1]))

def RequestGet3366Reward(role, param):
	'''
	客户端请求获取3366每日礼包
	@param role:
	@param param:
	'''
	rewardId = param
	if role.GetDI1(EnumDayInt1.Logion3366Reward):#已领取
		return
	#不是3366平台
	if role.GetTI64(EnumTempInt64.Is3366) == 0:
		return
	#3366成长等级
	GrowLevel = role.GetTI64(EnumTempInt64.GrowLevel3366)

	cfg = QQHZConfig.DAY_3366_REWARD.get(rewardId)
	if not cfg:
		print "GE_EXC, can not find rewardId=(%s) in Day3366Reward" % rewardId
		return

	if cfg.MinLevel > GrowLevel or GrowLevel > cfg.MaxLevel:
		return
	if cfg.items:
		#背包空间不足
		if role.PackageEmptySize() < len(cfg.items):
			role.Msg(2, 0, GlobalPrompt.NavicePackLessPackage)
			return
	#设置已领取标志
	role.SetDI1(EnumDayInt1.Logion3366Reward, 1)
	with Day3366Reward:
		tips = ""
		if cfg.money:
			role.IncMoney(cfg.money)
			tips += GlobalPrompt.Money_Tips % cfg.money
		if cfg.items:
			for rd in cfg.items:
				role.AddItem(*rd)
				tips += GlobalPrompt.Item_Tips % (rd[0], rd[1])
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		role.Msg(2, 0, tips)
		
def RequestGetQQHZTitle(role, msg):
	'''
	客户端请求获取黄钻称号
	@param role:
	@param msg:
	'''
	if role.GetI1(EnumInt1.QQHZTitle):
		return
	
	if role.GetQQHZ() >= 1:
		role.SetI1(EnumInt1.QQHZTitle, 1)
		Title.AddTitle(role.GetRoleID(), QQHZ_TITLE_ID)
		
				
if "_HasLoad" not in dir():
	#日志
	QQHZDayAward = AutoLog.AutoTransaction("QQHZDayAward", "黄钻用户每日礼包")
	QQHZNovice = AutoLog.AutoTransaction("QQHZNovice", "黄钻用户新手礼包")
	QQHZLevel = AutoLog.AutoTransaction("QQHZLevel", "黄钻用户等级礼包")
	Day3366Reward = AutoLog.AutoTransaction("Day3366Reward", "3366每日礼包奖励")
	
	if Environment.EnvIsFT() or Environment.EnvIsQQ():
		if Environment.HasLogic and not Environment.IsCross:
			#注册消息
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQHZdaliy_Rewards", "客户端请求获取每日黄钻礼包"), RequestGetQQHZdaily)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQHZnovice_Rewards", "客户端请求获取黄钻新手礼包"), RequestGetQQHZnovice)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQHZlevel_Rewards", "客户端请求获取黄钻等级礼包"), RequestGetQQHZlevel)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_3366Days_Rewards", "客户端请求获取3366每日礼包"), RequestGet3366Reward)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_QQHZ_Title", "客户端请求获取黄钻称号"), RequestGetQQHZTitle)
			
