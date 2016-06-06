#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionDefine")
#===============================================================================
# 激情活动枚举定义
#===============================================================================

#roleObj = role.GetObj(EnumObj.PassionActData)中的活动数据枚举
PassionGift = 1				#激情有礼
PassionMultiReward = 2 		#激情奖励翻倍
PassionMarket_BUYRECORD = 3 #激情卖场购买记录
PassionMarket_GOODS = 4		#激情卖场商品
PassionDiscount = 5			#特惠商品
PassionConsume = 6			#激情活动 -- 消费返利
PassionExchange = 7 		#激情活动 -- 限时兑换
PassionRecharge = 8			#激情活动 -- 充值返利
PassionOnlineGift = 9		#在线有礼活动
PassionTurntable = 10 		#激情转盘活动
PassionLoginGiftLoginRec = 11 	#激情登陆有礼登录奖励领取记录
PassionLoginGiftRechargeRec = 12 #激情登陆有礼充值记录{第X天:}
PassionLoginGiftRechargeAwradRec = 13 #激情登陆有礼充值奖励领取记录set([第x天])
PassionMaiDanConsumeRec = 14 #激情你消费我买单消费记录{第X天:XX神石}
PassionMaiDanConsumeAwradRec = 15 #激情你消费我买单奖励领取记录set([第x天])
PassionGodTreeExchange = 16			#激情活动神树兑换数据记录
PassionRechargeTarget = 17 	#激情活动每日购买神石返好礼set([当日已经领取的奖励index])
PassionConsumeTarget = 18 	#激情活动每日消费充值神石返好礼set([当日已经领取的奖励index])
PassionLianchongDays = 19 	#激情活动连冲豪礼([已经领取的奖励Days])


PassionThanksGivingChongZhi = 20			#充值奖励状态索引[]
PassionTGExchange = 21						#感恩节积分兑换{1:充值积分， 2:兑换记录}
PassionConsumePointRMB_Q = 22				#今日消费已经计算积分的消费充值神石数
PassionRechargeAndReward = 23					#充值满额领豪礼，剩余可使用的神石数

PassionD12Shop = 24						##{ 1:活动期间限购	2: #每日限购}
PassionD12GroupBuy = 25
PassionChristmasExchange = 26			#激情活动圣诞兑换{ 兑换index： 已经兑换个数 }

PassionJXLB = 27			#激情活动惊喜礼包
PassionSuperTurnTable = 28 	#激情活动超值转盘

PassionNewYearEgg = 29		#激情活动砸旦
PassionNewYearPig = 30		#激情活动金猪兑换


PassionSpringHongBao = 31	#红包闹新春领奖数据
PassionChunJieYuanXiao = 32	#春节元宵活动

PassionDaiBi = 33			#充值送代币{1:充值满奖励是否领取，2:重复奖励领取次数}
