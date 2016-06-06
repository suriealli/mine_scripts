#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CircularDefine")
#===============================================================================
# 循环活动定义
#===============================================================================

##########################################################################
#@CircularDefine
#注意循环活动的开启和关闭不能有其他逻辑触发，只能作为一个开关，不能在开启的时候做一些类似全服公告
#类似全服发奖之类的东西
#也不能在关闭的时候触发任何其他逻辑，例如触发发奖励，这样是不允许的
#再次声明，循环活动开启关闭管理只用于设置具体活动的开启关闭FLAG的设置，其他出现任何逻辑处理都是会有问题的
#如有问题请@黄伟奇
##########################################################################

CA_ToSky = 1					#冲上云霄
CA_PetFoot = 2					#人参果树
CA_MysterShop = 3				#神秘商店
CA_CarnivalOfTopup = 4			#狂欢充值
CA_RMBFund = 5					#神石基金
CA_WorldCupGuess16 = 6			#世界杯16强竞猜
CA_WorldCupChampionGuess = 7	#世界杯冠军竞猜
CA_WorldCupReward16 = 8			#世界杯16强竞猜奖励
CA_WorldCupChampionReward = 9	#世界杯冠军竞猜奖励
CA_PetLuckyDraw = 10			#宠物转转乐
CA_BallFame = 11				#一球成名
CA_DragonEgg = 12				#砸龙蛋
CA_TwelvePalace = 13			#勇闯十二宫
CA_GoldChest = 14				#黄金宝箱
CA_BraveHeroShop = 15			#英雄徽章商店
CA_DailySeckill = 16			#天天秒杀
CA_SeaXunbao = 17				#深海寻宝
CA_NationBack = 18				#国庆节日有礼,神石回赠
CA_NationStrikeBoss = 19		#国庆击杀boss
#########################################
#世界杯 占用了20-40的枚举了
CA_WorldCupStart = 20 
CA_WorldCupEnd = 60
########################################
########################################
# 国庆活动
ND_FB				= 61
ND_DailyLiBao 		= 62
ND_ExchangeReward 	= 63
########################################
CA_Halloween = 64				#万圣节活动
CA_DaliyMountLottery = 65		#天马行空
CA_QQHallLottery = 66			#大厅搏饼
########### 双十一活动 ##########
CA_BlessRoulette = 67			#祝福轮盘
CA_Seckill = 68					#秒杀汇
CA_DoubleElevenShop = 69		#狂欢兑不停商店

CA_PetLuckyFarm = 70
CA_DragonStele = 71		#龙魂石碑
CA_GodsTreasure = 72	#众神秘宝

########### 感恩节活动 ##########  
CA_TGRechargeReward = 73	#感恩节充值好礼
CA_TGOnlineReward	 = 74	#感恩节在线有礼
CA_CutTurkey = 75			#切火鸡

########## 双十二活动 ###########
CA_DTFeastWheel = 76		#盛宴摩天轮
CA_DTLoveTogether = 77		#爱在一起
CA_DTRebate = 78			#返利领不停
CA_DTLuckyCoinLottery = 79	#好运币专场

########## 圣诞嘉年华  ###########
CA_ChristmasWishTree = 80	#圣诞许愿树
CA_ChristmasWingLottery = 81	#圣诞羽翼转转乐	
CA_ChristmasMountLottery = 82	#圣诞坐骑转转乐
CA_ChristmasFashionShow = 83	#圣诞时装秀
CA_ChristmasShop = 84			#圣诞狂欢兑不停

########## 元旦活动  ###########
CA_HolidayOnlineReward = 85		#迎新送好礼（在线领奖）
CA_HolidayShopping = 86			#元旦购物节
CA_HolidayRechargeLottery = 87	#充值开宝箱（充值抽奖
CA_HolidayMoneyWish = 88		#元旦金币祈福礼
########## 新年活动  ###########
CA_NewYearDiscount = 89			#新年折扣汇
CA_NYearOnlineReward = 90		#新年活动--新年冲冲冲
CA_NewYearShop = 91				#新年乐翻天-新年兑不停
########## 女神卡牌  ###########
CA_GoddessCard = 92				#女神卡牌


########## 魅力情人节  ###########
CA_RosePresent = 93			#送人玫瑰
CA_RoseRebate = 94			#玫瑰返利
CA_GlamourParty = 95		#魅力派对
CA_CouplesFashion = 96		#情侣酷炫时装
CA_CouplesGoal = 97			#情人目标
CA_GlamourCoinExchange = 98		#魅力大兑换

CA_HZCDKActive = 99				#黄钻活动(服务端仅仅控制活动开关)

#专题活动占用100-200的，枚举
##########################################################################
CA_ProjectActMount1		 = 101	#坐骑活动1 升阶
CA_ProjectActMount2		 = 102	#坐骑活动2 升阶
CA_ProjectActMount3		 = 103	#坐骑活动3 升阶
CA_ProjectActMount4		 = 104	#坐骑活动4 升阶
CA_ProjectActMount5		 = 105	#坐骑活动5 升阶
CA_ProjectActMount6		 = 106	#坐骑活动6 培养次数
CA_ProjectActGem1		 = 107	#宝石活动1 
CA_ProjectWish_ProAct	 = 108	#中秋活动1-许愿 
CA_ProjectTarot_ProAct	 = 109	#中秋活动2-占卜 
CA_ProjectActWing		 = 110	#羽翼活动1 培养次数
CA_ProjectActArtifactGem		 = 111	#符文活动 1
CA_ProjectActPet				 = 112	#宠物活动1
CA_ProjectActWeddingRing		 = 113	#婚戒活动1
CA_ProjectActStarGirlStar		 = 114	#星灵专题
#此枚举只用于专题活动
CA_ProjectActList = [CA_ProjectActMount1, CA_ProjectActMount2, CA_ProjectActMount3, CA_ProjectActMount4, CA_ProjectActMount5, \
					 CA_ProjectActMount6, CA_ProjectActGem1, CA_ProjectWish_ProAct, CA_ProjectTarot_ProAct, CA_ProjectActWing, \
					 CA_ProjectActArtifactGem, CA_ProjectActPet, CA_ProjectActWeddingRing, CA_ProjectActStarGirlStar]

##########################################################################
# 超值大礼占用201-300的枚举
##########################################################################
CA_SuperDiscountStart = 201 
CA_SuperDiscountEnd = 300

#########春节活动##########
CA_SpringFUniversal = 301	#普天同庆
CA_SpringFGodWealth = 302	#天降财神
CA_SpringFNianComing = 303	#年兽来了
CA_SpringDiscount = 304		#折扣汇
CA_SpringFashion = 305		#靓丽时装秀

########## 元宵节活动  ###########
CA_HappnessLantern = 306			#欢乐花灯
CA_LanternRebate = 307				#花灯返利
CA_LanternRiddle = 308				#猜灯谜
CA_LanternStore = 309				#花灯商店

CA_GodWarChest = 310	#战神宝箱
CA_RMBComfig = 311		#神石滚滚来


########## 清明节活动  ###########

CA_QingMingOuting = 312		#清明 踏青
CA_QingMingLuckyLottery = 313	#清明 幸运轮盘
CA_QingMingExchange = 314				#清明节好礼兑不停
CA_QingMingQuanMingLianJin = 315		#清明全民炼金
CA_QingMingSevenDayRecharge = 316		#清明节七日充值
CA_QingMingSevenDayConsume = 317		#清明节七日消费

########### 魔灵大转盘 ##########
CA_MoLingLuckyDraw = 318			#魔灵大转盘

########占用320-340, 请不要使用
###################超级投资##############################
CA_InvestTili = 320				#体力投资
CA_InvestDragon = 321			#神龙投资
CA_InvestBindRMB = 322			#魔晶投资
CA_InvestGem = 323				#宝石投资
CA_InvestArtifactGem = 324		#符文投资
CA_InvestHallowsGem = 325		#雕纹投资
CA_InvestFashionClothes = 326	#时装投资
CA_InvestStarGirl = 327			#星灵投资
############328客户端预览占用
CA_WarStation_1 = 329			#战阵战魂投资
CA_WarStation_2 = 330			#战阵阵灵投资
CA_MoFaZhen = 331				#魔法阵投资
########## 五一活动  ###########
CA_FiveOneLogin = 341			#五一登录奖励
CA_FiveOneCost = 342			#五一消费送惊喜
CA_FiveOneAttackDragon = 343	#五一勇者斗恶龙
CA_FiveOneDragonBaoKu = 344		#五一神龙宝库
########## 腾讯页游节活动  ###########
CA_YeYouJieDiscount = 345		#页游节折扣汇#
CA_YeYouJieBaoJiBuff = 346		#页游节暴击

########## 空间十周年  ###########
CA_KongJianRegress = 347		#十周年回归#
CA_KongJianRecharge = 348		#累计充值送惊喜
CA_KongJianExchange = 349		#周年纪念币
CA_KongJianFirstRecharge = 350	# 首充拿大礼 
CA_KongJianLoginReward = 351	#天天领好礼
CA_KongJianConsumeRebate = 352	#十周年活动消费返金券
######### 最新活动 占用400-500##############
CA_LatestMountEvolve = 400		#坐骑培养日
CA_StarGirl = 401				#星灵
CA_FillRMBLatest = 402			#充值满额送好礼
CA_LatestActivity_1 = 403		#活跃度
CA_MountGrade = 404				#坐骑进化日
CA_ExchangeItem = 405			#兑换得豪礼活动
CA_LatestActivity_2 = 406		#活跃度
CA_LatestActivity_3 = 407		#活跃度
CA_FillRMBLatest_2 = 408		#充值满额送好礼
CA_ExchangeItem_2 = 409			#兑换得豪礼活动
CA_PetTrainLatest = 410			#宠物培养日
CA_PetEvoLatest = 411			#宠物进化日
CA_FillRMBLatest_3 = 412		#充值满额送好礼
CA_ExchangeItem_3 = 413			#兑换得豪礼活动
CA_FillRMBLatest_4 = 414		#充值满额送好礼
CA_ExchangeItem_4 = 415			#兑换得豪礼活动
CA_WingTrainLatest = 416		#羽翼培养日
CA_FillRMBLatest_5 = 417		#充值满额送好礼
CA_ExchangeItem_5 = 418			#兑换得豪礼活动
CA_FillRMBLatest_6 = 419		#充值满额送好礼
CA_ExchangeItem_6 = 420			#兑换得豪礼活动
CA_DragonTrain = 421			#神龙进化日
CA_FillRMBLatest_7 = 422		#充值满额送好礼
CA_ExchangeItem_7 = 423			#兑换得豪礼活动
CA_EquipmentWash = 424			#装备洗练日
CA_FillRMBLatest_8 = 425		#充值满额送好礼
CA_ExchangeItem_8 = 426			#兑换得豪礼活动
CA_ConsumeRMB_Latest_1 = 427	#消费满额送好礼1
CA_ConsumeRMB_Latest_2 = 428	#消费满额送好礼2
CA_ExchangeItem_Latest_9 = 429	#兑换得豪礼活动9
CA_ExchangeItem_Latest_10 = 430	#兑换得豪礼活动10
CA_StationSoul_Latest = 431		#战灵培养日
CA_ZhanHun_Latest = 432			#战魂培养日
CA_Hallows_Latest = 433			#圣器洗练日
CA_FillRMBLatest_11 = 434		#充值满额送好礼
CA_ExchangeItem_11 = 435		#兑换得豪礼活动
#[最小活动ID， 最大活动ID]
CA_LatestList = [CA_LatestMountEvolve, CA_ExchangeItem_11]
#### 王者公测 ####
CA_ZaiXianLuxuryReward = 501		#在线有豪礼
CA_WangZheExchange = 502			#兑换由我定
CA_WangZheFashionShow = 503			#最炫时装秀
CA_WangZheZheKouHui = 504			#公测折扣汇
CA_WangZheCrazyReward = 505			#奖励狂翻倍
CA_WangZheRechargeRebare = 506		#充值返利
CA_DuanWuJieZongzi = 507			#欢庆端午节 

#### 激情活动 508-560  #####
CA_PassionGift = 508				#激情有礼
CA_PassionMultiReward = 509			#奖励翻倍
CA_PassionRecharge = 510			#充值返利
CA_PassionConsume = 511				#消费返利
CA_PassionExchange = 512			#限时兑换
CA_PassionDiscount = 513			#特惠商品
CA_PassionMarket = 514				#激情卖场
CA_PassionTurntable = 515			#激情大转盘
CA_PassionOnlineGift = 516			#激情在线有礼 
CA_PassionLoginGift = 517			#激情活动登录有礼
CA_PassionXiaoFeiMaiDan = 518		#激情活动你消费我买单
CA_PassionGodTree = 519				#神树探秘
CA_PassionGodTreeExchange = 520		#神树兑换
CA_PassionRechargeTaget = 521		#每日购买神石返好礼
CA_PassionConsumeTarget = 522		#每日消费神石返好礼
CA_PassionTaoGuan = 523				#欢乐砸陶罐
CA_PassionLianChongGift = 524		#激情活动连冲豪礼
CA_PassionTGPointExchange	 = 525		#感恩活动充值积分兑换
CA_PassionTGBuy3in2			 = 526		#感恩活动买二送一
CA_PassionSignInAward = 527				#每日签到奖励
CA_PassionChongZhi = 528				#感恩节的充值活动
CA_PassionConsumePointExchange = 529	#消费充值神石积分兑换
CA_PassionRechargeHongBao = 530		#激情活动充值送红包
CA_PassionHongBao = 531				#激情活动发红包
CA_PassionD12Shop = 532				#激情活动自选商城
CA_PassionD12GroupBuy = 533			#激情活动超值团购
CA_PassionChristmasExchange = 534	#激情活动圣诞大兑换
CA_PassionJXLB = 535				#激情活动惊喜礼包
CA_PassionSuperTurnTable = 536		#激情活动超值转盘
CA_PassionChunJieActive = 537		#激情活动春节活跃有礼
CA_PassionNianShou = 538			#激情活动春节打年兽
CA_PassionSpringHongBao = 539		#激情活动红包闹新春
CA_ChunJieYuanXiao = 540			#春节元宵花灯活动
CA_ChunJieYuanXiaoChongZhi = 541	#春节元宵充值活动
CA_PassionDaiBi = 542				#充值送代币


CA_QiangHongBao = 561 				#抢红包
CA_ZhongQiuLianJin = 562			#中秋全民炼金
CA_HuoYueDaLi = 563					#中秋活跃大礼
CA_ZhongQiuRecharge = 564			#中秋首冲
CA_ZhongQiuShangYue = 565			#中秋赏月 

CA_SendHallows = 566				#精彩活动充值送圣器

#######双十一活动#########
CA_ElevenMallReward = 580			#双十一商城满返
CA_ElevenRecharge = 581				#双十一充值大放送
CA_ElevenPointExchange = 582		#双十一积分兑换
CA_ElevenTurntable = 584 			#双十一转盘

#######点金大放送#########
CA_TouchGoldReward = 590			#点金大放送

######元旦活动############
CA_NewYearDayEgg = 591				#元旦砸旦活动
CA_NewYearDayPig = 592				#元旦金猪活动

######连连看############
CA_LianLianKan = 593				#连连看

######幸运扭蛋############
CA_LuckyGashaponFashion = 594		#时装扭蛋
CA_LuckyGashaponMount = 595			#坐骑扭蛋
