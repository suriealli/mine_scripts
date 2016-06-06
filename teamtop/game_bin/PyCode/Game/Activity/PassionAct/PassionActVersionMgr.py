#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActVersionMgr")
#===============================================================================
# 激情活动版本Mgr
#===============================================================================
import Environment
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt32, EnumDayInt1, EnumObj, EnumInt8, EnumDayInt8,\
	EnumInt16
from Game.Activity.PassionAct import PassionDefine

#### 激情活动版本号  再次开启活动递增该版本号
###############################################
if Environment.EnvIsQQ() or Environment.IsDevelop:
	#国服2016年3月3日更新增加版本号
	PassionVersion = 13
elif Environment.EnvIsFT():
	#繁体1月25日维护增加版本号
	PassionVersion = 10
elif Environment.EnvIsNA():
	PassionVersion = 6
elif Environment.EnvIsTK():
	PassionVersion = 2
else:
	PassionVersion = 1
###############################################

if "_HasLoad" not in dir():
	Tra_PassionAct_UpdateVersion = AutoLog.AutoTransaction("Tra_PassionAct_UpdateVersion", "激情活动_更新活动版本号")

def UpdateVersion(role, param = None):
	'''
	根据激情活动版本号 和 记录的版本好 处理角色Obj数据
	'''
	roleVersion = role.GetI32(EnumInt32.PassionActVersion)
	if PassionVersion == roleVersion:
		return
	
	if PassionVersion < roleVersion:
		print "GE_EXC, PassionActVersionMgr::UpdateVersion PassionVersion(%s) < roleVersion (%s)" % (PassionVersion, roleVersion)
		return 
	
	#重置相关数据
	with Tra_PassionAct_UpdateVersion:
		#升级版本号
		role.SetI32(EnumInt32.PassionActVersion, PassionVersion)
		#激情有礼数据
		role.SetDI1(EnumDayInt1.PassionGift_IsReward,0)
		role.SetI8(EnumInt8.PassionGiftAccuCnt,0)
		#激情卖场数据
		role.SetDI8(EnumDayInt8.PassionMarketRefreshCnt,0)
		
		#激情活动大转盘数据
		role.SetI8(EnumInt8.PassionTurntableTimes, 0)
		
		#激情活动在线有礼活动数据
		role.SetI8(EnumInt8.PassionOnlineGiftLeftCnt, 0)
		
		#激情活动连充送豪礼连充天数
		role.SetI8(EnumInt8.PassionLianChongGiftDays, 0)
		
		#激情感恩活动连充
		role.SetI8(EnumInt8.ChongZhiDays, 0)
		#天降横财_清除累计消费充值神石
		role.SetI32(EnumInt32.TJHC_ConsumeUnbindRMB_Q, 0)
		#天降横财_清楚激活兑奖码数
		role.SetI16(EnumInt16.TJHC_ActivatedCnt, 0)
		
		#Obj数据
		role.SetObj(EnumObj.PassionActData, {
					PassionDefine.PassionGift:set(), 			#激情有礼
					PassionDefine.PassionMultiReward:{}, 		#激情奖励翻倍
					PassionDefine.PassionMarket_BUYRECORD:{}, 	#激情卖场购买记录
					PassionDefine.PassionMarket_GOODS:{}, 		#激情卖场商品
					PassionDefine.PassionDiscount:{}, 			#特惠商品
					PassionDefine.PassionConsume:set(), 		#激情活动 -- 消费返利
					PassionDefine.PassionExchange:{}, 			#激情活动 - -限时兑换
					PassionDefine.PassionRecharge:set(), 		#激情活动 -- 充值返利
					PassionDefine.PassionOnlineGift:{}, 		#激情活动 -- 在线有礼数据清空
					PassionDefine.PassionTurntable:{}, 			#激情活动 -- 大转盘数据清空
					PassionDefine.PassionLoginGiftLoginRec:{}, 				#激情登陆有礼登录奖励领取记录
					PassionDefine.PassionLoginGiftRechargeRec: {}, 			#激情登陆有礼充值记录{第X天:}
					PassionDefine.PassionLoginGiftRechargeAwradRec:set(), 	#激情登陆有礼充值奖励领取记录set([第x天])
					PassionDefine.PassionMaiDanConsumeRec:{}, 				#激情你消费我买单消费记录{第X天:XX神石}
					PassionDefine.PassionMaiDanConsumeAwradRec:set(), 		#激情你消费我买单奖励领取记录set([第x天])
					PassionDefine.PassionGodTreeExchange:{}, 				#激情活动神树兑换数据记录
					PassionDefine.PassionRechargeTarget:set(), 				#激情活动每日购买神石返好礼set([当日已经领取的奖励index])
					PassionDefine.PassionConsumeTarget:set(), 				#激情活动每日消费充值神石返好礼set([当日已经领取的奖励index])
					PassionDefine.PassionLianchongDays:set(), 				#激情活动连冲豪礼
					PassionDefine.PassionThanksGivingChongZhi:[], 			#激情活动感恩充值
					PassionDefine.PassionTGExchange:{1:0, 2:{}}, 			#感恩节积分兑换{1:充值积分,2:兑换记录}
					PassionDefine.PassionConsumePointRMB_Q:0, 				#消费积分兑换已经转换成积分的消费充值神石数
					PassionDefine.PassionRechargeAndReward:0, 				#充值满额领豪礼，剩余可使用的神石数
					PassionDefine.PassionD12Shop:{1:{}, 2:{}}, 				#商城自选{1:活动限购,2:每日限购}
					PassionDefine.PassionD12GroupBuy:set(), 				#超值团购购买记录
					PassionDefine.PassionChristmasExchange:{}, 				#圣诞兑换{ 兑换index： 已经兑换个数 }
					PassionDefine.PassionJXLB:{}, 							#惊喜礼包{物品索引index:已购买数量}
					PassionDefine.PassionSuperTurnTable:{1:0, 2:set()}, 		#超值转盘{1:玩家抽奖次数,2:玩家已领取奖励}
					PassionDefine.PassionNewYearEgg:{1:[0] * 12, 2:[0] * 3, 3:[0] * 3}, #新年砸旦{1：[蛋的状态],2:[在线状态],3:[充值状态]}
					PassionDefine.PassionNewYearPig:{1:{}, 2:0, 3:{}}, 				#新年金猪兑换{1：{index：剩余数量}，2：锤子数量，3：{任务index，奖励状态}}
					PassionDefine.PassionChunJieYuanXiao : set(), 				#春节元宵活动
					PassionDefine.PassionSpringHongBao:set(), 				#红包闹新春领奖数据
					PassionDefine.PassionDaiBi:{1:0, 2:0}			#充值送代币{1:充值满奖励是否领取，2:重复奖励领取次数}
					})


def CheckRoleVersion(role):
	roleVersion = role.GetI32(EnumInt32.PassionActVersion)
	return roleVersion == PassionVersion


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, UpdateVersion)
