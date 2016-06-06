#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZRollGiftMgr")
#===============================================================================
# 蓝钻转大礼Mgr PS:活动开关由前端热更 出现界面和屏蔽界面控制
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt8
from Game.ThirdParty.QQLZ import QQLZRollGiftConfig

if "_HasLoad" not in dir():
	#日志
	Tra_QQLZKaiTongGift = AutoLog.AutoTransaction("Tra_QQLZKaiTongGift", "蓝钻转大礼礼包获取")
	#同步
	QQLZKaiTongGift_RollResult = AutoMessage.AllotMessage("QQLZKaiTongGift_RollResult_SB", "蓝钻转大礼抽奖结果")	
	QQLZGift_State_OfferGift = AutoMessage.AllotMessage('QQLZGift_State_OfferGift_S', "蓝钻献大礼活动状态同步")

def OnLZKaiTongRewardRoll(role, param = None):
	'''
	蓝钻开通转大礼 请求抽奖
	'''
	#11-12维护后 关闭活动 不再处理此请求
	role.Msg(2, 0, GlobalPrompt.QQLZKaiTongGift_Tips_Ended)
	return;
	#蓝钻转大礼次数
	effectiveTimes = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)
	usedTimes	= role.GetI8(EnumInt8.QQLZKaiTong_UsedTimes_Roll)
		
	# 剩余次数不足
	if (effectiveTimes < 1 or usedTimes >= effectiveTimes):
		return
		
	# 次数已满
	if usedTimes >= EnumGameConfig.QQLZKaiTongGift_MaxTimes:
		return
		
	#奖励随机
	rewardId = QQLZRollGiftConfig.QQLZKTR_RANDOMER.RandomOne()
	if not rewardId or rewardId not in QQLZRollGiftConfig.QQLZ_KAITONG_REWARD_DICT:
		print "GE_EXC,OnLZKaiTongGiftRoll:: random rewardId(%s) error" % rewardId
		return 
		
	#获取奖励配置失效
	rewardcfg = QQLZRollGiftConfig.QQLZ_KAITONG_REWARD_DICT.get(rewardId)
	if not rewardcfg:
		print "GE_EXC,OnLZKaiTongGiftRoll:: cannot find rewardcfg with rewardId(%s)" % (rewardId)
		return
	
	#增加已抽奖次数
	usedTimes += 1
	role.SetI8(EnumInt8.QQLZKaiTong_UsedTimes_Roll, usedTimes)
		
	# 发送抽奖结果 等待回调 超时自动触发
	role.SendObjAndBack(QQLZKaiTongGift_RollResult, rewardId, 8, QQLZKaiTongRewardCallBack, (rewardcfg, usedTimes))	

def QQLZKaiTongRewardCallBack(role, callargv, regparam):
	'''
	蓝钻转大礼抽奖回调
	@param role: 
	@param callargv:
	@param regparam:  rewardcfg,usedTimes 抽奖随机出来的奖励赤cfg,此次抽奖后的抽奖次数
	'''
	# 参数检测
	rewardcfg, usedTimes = regparam	
	# process
	with Tra_QQLZKaiTongGift:
		# 礼包获得
		itemCoding, itemCnt = rewardcfg.rateItem[0], rewardcfg.rateItem[1]
		role.AddItem(itemCoding, itemCnt)
		# 额外获取-蓝钻坐骑道具
		Master_Reward_Tips = ""
		if usedTimes == EnumGameConfig.QQLZKaiTongGift_MaxTimes:
			role.AddItem(EnumGameConfig.QQLZKaiTongGift_MountProCoding, 1)
			Master_Reward_Tips = GlobalPrompt.QQLZKaiTongGift_Tips_Reward_Master
		
		promptMsg = GlobalPrompt.QQLZKaiTongGift_Tips_Reward_Head + GlobalPrompt.QQLZKaiTongGift_Tips_Reward_Item % (itemCoding, itemCnt) + Master_Reward_Tips
		role.Msg(2, 0, promptMsg)		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZKaiTongGift_OnRollRewards", "客户端请求蓝钻开通转大礼抽奖"), OnLZKaiTongRewardRoll)