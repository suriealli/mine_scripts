#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Common.Message.PyMessage")
#===============================================================================
# Python中定义的消息, 取值范围[512, 768)  [2 * 8bit, 3 * 8bit)
#===============================================================================
PyMsg_None = 512					#消息占位

Http_Request = 513					#HTTP访问请求
Https_Request = 514					#HTTPS访问请求

GM_Request = 515					#GM请求
GM_Response = 516					#GM回复

DB_Visit = 517						#DB访问请求
DB_VisitAndBack = 518				#DB访问请求并等待回调
DB_LogBase = 519					#基本日志
DB_LogObj = 520						#对象日志
DB_LogValue = 521					#数值日志
DB_MustSaveRole = 522				#数据库进程命令逻辑进程强制保存角色数据并踢掉玩家
DB_MustKickRole = 523				#数据库进程命令逻辑进程强制踢掉玩家
DB_NotifyCommand = 524				#数据库进程告诉逻辑进程有离线命令来了

Control_RoleLogin = 525				#角色登录
Control_RoleExit = 526				#角色离开
Control_AddFriend = 527				#添加好友
Control_DelFriend = 528				#删除好友
Control_InitFriends = 529			#更新好友信息
Control_OnLineFriend = 530			#好友上线
Control_OutLineFriend = 531			#好友下线
Control_RoleCall = 532				#角色函数呼叫
Control_OnRoleCall = 533			#角色函数呼叫

Server_BigMessage = 534				#服务端超大消息
Server_BigCallBack = 535			#服务端超大函数回调

Control_RequestLogicBraveHeroRank = 536		#请求逻辑进程的排行榜数据(回调)
Control_UpdataBraveHeroRankToLogic = 537	#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetBraveHeroRank = 538				#逻辑进程向控制进程主动请求跨服排行榜数据

Control_UpdateBankLog = 539					#控制进程同步最新的跨服神石银行日志
Control_AddBankLog = 540					#增加一个跨服神石银行日志

Control_UpdataBraveHeroRankToLogic_T = 541	#发送跨服排行榜数据到逻辑进程(今天)

Control_UpdateWeiXinGuanZhuCnt = 542		#更新微信关注人数
Control_GetWeiXinGuanZhuCnt = 543			#逻辑进程请求获取微信关注人数

Control_RequestLoad = 544					#请求载入数据
Control_CommandLoad = 545					#命令载入数据
Control_SuccessLoad = 546					#成功载入数据

Control_RequestQQRank = 547					#向逻辑进程请求数据
Control_ReceiveQQRank = 548					#逻辑进程主动发送数据


LogicRequestJTRank = 549					#逻辑进程请求组队竞技的排行榜
Cross_To_Logic_UpdateJTRank = 550			#跨服进程把自己的排行榜(显示的数据 500 个)更新到逻辑进程
LogicChangeJTRank = 551						#逻辑进程改变了一个排行榜上面的数据信息

Control_RequestLogicHaoqiRank = 552			#请求逻辑进程的豪气冲天排行榜数据(回调)
Control_UpdataHaoqiRankToLogic = 553		#发送豪气冲天跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetHaoqiRank = 554					#逻辑进程向控制进程主动请求豪气冲天跨服排行榜数据
Control_UpdataHaoqiRankToLogic_T = 555		#发送豪气冲天跨服排行榜数据到逻辑进程(今天)

Cross_To_Logic_Ranks = 556					#跨服进程把 战斗排行榜的排序位置同步给逻辑进程 2000个
Cross_Change_JTInfo = 557					#跨服进程把参加这次活动的战队信息重新更新到所有的逻辑进程

LogicRequestGroups = 558					#逻辑进程请求跨服争霸赛小组资格
Cross_To_Logic_Groups = 559					#跨服进程把跨服争霸赛的小组资格通知到逻辑进程

LogicRequestSignUpInfo = 560				#逻辑进程请求跨服争霸赛报名数据
Cross_To_Logic_SignUpInfo = 561				#跨服进程把跨服争霸赛的报名数据通知到逻辑进程

LogicRequestGroupRank = 562					#逻辑进程请求跨服争霸赛小组排名
Cross_To_Logic_GroupRank = 563				#跨服进程把跨服争霸赛的小组排名通知到逻辑进程

LogicRequestSignUpJTeam = 564				#逻辑进程一个战队请求报名


LogicRequestFinalData = 565					#逻辑进程请求跨服争霸赛总决赛数据
Cross_To_Logic_FinalData = 566				#跨服进程把跨服争霸赛的总决赛数据通知到逻辑进程

Control_RequestControlZumaUnionRank = 567	#逻辑进程向控制进程主动请求祖玛公会跨服排行榜数据
Control_RequestLogicZumaUnionRank = 568		#请求逻辑进程的祖玛公会排行榜数据(回调)
Control_UpdateZumaUnionRankToLogic = 569	#发送祖玛公会跨服排行榜数据到逻辑进程(今天，昨天)
Control_UpdateZumaUnionRankToLogic_T = 570	#发送祖玛公会跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicRichRank = 571			#请求逻辑进程的双十二富豪榜数据(回调)
Control_UpdateLogicRichRank = 572			#更新逻辑进程双十二富豪榜
Control_RequestControlRichRank = 573		#逻辑进程向控制进程主动请求双十二富豪榜数据
Control_RequestLogicRichRankReward = 574	#请求逻辑进程的双十二富豪榜颁发奖励

Control_RequestLogicZumaUnionRankReward = 575#请求逻辑进程的祖玛公会榜颁发奖励

Control_RequestLogicChristmasHaoRank = 576			#请求逻辑进程的有钱就是任性排行榜数据(回调)
Control_UpdataChristmasHaoRankToLogic = 577			#发送有钱就是任性跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetChristmasHaoRank = 578					#逻辑进程向控制进程主动请求有钱就是任性跨服排行榜数据
Control_UpdataChristmasHaoRankToLogic_T = 579		#发送有钱就是任性跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicNewYearHaoRank = 580			#请求逻辑进程的新年我最壕排行榜数据(回调)
Control_UpdataNewYearHaoRankToLogic = 581			#发送新年我最壕跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetNewYearHaoRank = 582					#逻辑进程向控制进程主动请求新年我最壕跨服排行榜数据
Control_UpdataNewYearHaoRankToLogic_T = 583		#发送新年我最壕跨服排行榜数据到逻辑进程(今天)

Logic_To_Cross_JJC_Data = 584					#逻辑进程给跨服进程发送跨服个人竞技场数据
Cross_To_Logic_JJC_Election_Union_Reward = 585	#跨服进程把海选公会奖励名单发送到逻辑进程
Cross_To_Logic_JJC_Union_Today_Score = 586		#跨服进程把公会今日积分发送到逻辑进程


Logic_Request_Cross_JJC_Palace_Data = 587		#逻辑进程请求跨服个人竞技场龙骑殿堂数据
Cross_To_Logic_JJC_Palace_Data = 588			#跨服进程给逻辑进程发送跨服个人竞技场龙骑殿堂数据


Control_RequestLogicLanternRank = 589			#请求逻辑进程的元宵节积分排行榜数据(回调)
Control_UpdateLanternRankToLogic = 590			#控制进程同步跨服排行榜给逻辑进程(今天，昨天)
Logic_RequestGetCrossLanternRank = 591			#逻辑进程请求获取跨服元宵节积分排行榜数据
Control_UpdateLanternRankToLogic_T = 592		#控制进程同步跨服排行榜给逻辑进程(今天)


Control_RequestLogicSpringBRank = 593			#请求逻辑进程的春节最靓丽排行榜数据(回调)
Control_UpdateSpringBRankToLogic = 594			#发送春节最靓丽跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetSpringBRank = 595					#逻辑进程向控制进程主动请求春节最靓丽跨服排行数据
Control_UpdateSpringBRankToLogic_T = 596		#发送春节最靓丽跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicGlamourRank = 597		#请求逻辑进程的排行榜数据(回调)
Control_UpdataGlamourRankToLogic = 598		#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetGlamourRank = 599				#逻辑进程携带本服排行向控制进程主动请求跨服排行榜数据
Control_UpdataGlamourRankToLogic_T = 600	#发送跨服排行榜数据到逻辑进程(今天)

Control_ServerCall = 601					#跨服呼叫逻辑进程调用函数
Control_OnServerCall = 602					#逻辑进程间调用函数

Control_ControlServerCall = 603				#逻辑进程呼叫控制进程执行某个函数

Control_RequestLogicQingMingRank = 604		#请求逻辑进程的排行榜数据(回调)
Control_UpdataQingMingRankToLogic = 605		#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetQingMingRank = 606				#逻辑进程携带本服排行向控制进程主动请求跨服排行榜数据
Control_UpdataQingMingRankToLogic_T = 607	#发送跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicWangZheRank = 608		#请求逻辑进程的排行榜数据(回调)
Control_UpdataWangZheRankToLogic = 609		#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetWangZheRank = 610				#逻辑进程携带本服排行向控制进程主动请求跨服排行榜数据
Control_UpdataWangZheRankToLogic_T = 611	#发送跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicPassionRechargeRank = 612		#请求逻辑进程的排行榜数据(回调)
Control_UpdataPassionRechargeRankToLogic = 613		#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetPassionRechargeRank = 614				#逻辑进程携带本服排行向控制进程主动请求跨服排行榜数据
Control_UpdataPassionRechargeRankToLogic_T = 615	#发送跨服排行榜数据到逻辑进程(今天)

Control_SuperServerCall = 616					#跨服呼叫逻辑进程调用函数(大消息)
Control_OnSuperServerCall = 617					#逻辑进程间调用函数(大消息

Control_RequestLogicTurnTablePoolValue = 618		#请求逻辑进程的奖池数据(回调)
Control_UpdataTurnTablePoolValueToLogic = 619		#发送跨服奖池榜数据到逻辑进程
Control_GetGlobalTurnTablePoolValue = 620			#逻辑进程向控制进程主动请求跨服奖池数据

Control_RequestLogicFlowerRank = 621				#请求逻辑进程的排行榜数据(回调)
Control_UpdataFlowerRankToLogic = 622				#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetFlowerRank = 623							#逻辑进程向控制进程主动请求跨服排行榜数据
Control_UpdataKuafuFlowerRankToLogic_T = 624		#发送跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicPassionConsumeRank = 625		#请求逻辑进程的排行榜数据(回调)
Control_UpdataPassionConsumeRankToLogic = 626		#发送跨服排行榜数据到逻辑进程(今天，昨天)
Control_GetPassionConsumeRank = 627				#逻辑进程携带本服排行向控制进程主动请求跨服排行榜数据
Control_UpdataPassionConsumeRankToLogic_T = 628	#发送跨服排行榜数据到逻辑进程(今天)

Control_RequestLogicZBCheersData = 629				#跨服争霸赛请求逻辑进程的奖池数据(回调)
Control_UpdataZBCheersDataToLogic = 630				#跨服争霸赛发送跨服奖池榜数据到逻辑进程
Control_GetGlobalZBCheersData = 631					#跨服争霸赛逻辑进程向控制进程主动请求跨服奖池数据
Control_GetGlobalZBCheersReward = 632				#跨服争霸赛控制进程通知逻辑进程发奖(总奖金, 总的喝彩次数)
Control_GetGlobalZBTeamData = 633					#跨服争霸赛控制进程向跨服逻辑进程请求巅峰战队队伍数据
Control_GetGlobalZBFirstTeamData = 634				#跨服争霸赛控制进程向跨服逻辑进程请求巅峰战队冠军队伍数据

Control_UpdateNewQandARank = 635					#新答题决赛跨服排行榜数据消息
Control_RequestFinalsRankData = 636					#新答题活动请求逻辑进程数据			
Control_LogicSendFinalsRankData = 637				#新答题活动逻辑进程发送数据

TJHC_SendGamblerData_Logic2Control = 638			#天降横财_发送参与兑奖数据_逻辑进程到控制进程
TJHC_SendLotteryResult_Control2Logic = 639			#天降横财_发送抽奖结果_控制进程到逻辑进程
TJHC_RequestLotteryResult_Logic2Control = 640		#天降横财_请求抽奖结果_逻辑进程到控制进程（回调）

CatchingFish_Calculus_FromControl = 641						#捕鱼活动逻辑进程向控制进程获得积分排行榜数据 
CatchingFish_CalculusToLogicControl = 642					#捕鱼活动控制进程向逻辑进程发送排行榜数据
CatchingFish_Calculs_FromLogic = 643						#请求逻辑进程的排行榜数据(回调)

Control_RequestD12GroupBuyData = 644				#超值团购_请求逻辑进程数据
Control_LogicSendD12GroupBuyData = 645				#超值团购_发送团购数据到逻辑进程
Control_CleanLogicGroupBuyData = 646				#超值团购_清空逻辑进程后备缓存
Control_RequestControlD12GroupBuyData = 647			#超值团购_请求控制进程数据

Control_RequestLogicGame2048Rank = 648		#请求逻辑进程的宝石2048排行榜数据(回调)
Control_UpdateGame2048RankToLogic_T = 649	#发送宝石2048跨服排行榜数据到逻辑进程(今天) 
Control_UpdateGame2048RankToLogic = 650		#发送宝石2048跨服排行榜数据到逻辑进程(今天，昨天)
Control_RequestControlGame2048Rank = 651	

Control_RequestLogicChaosDivinityRank 	= 652 		#混沌神域_请求逻辑进程排行数据
Control_SyncChaosDivinityTodayRank 		= 653 		#混沌神域_同步今日排行榜到逻辑进程
Control_SyncChaosDivinityAllRank 		= 654 		#混沌神域_同步排行榜所有到逻辑进程
Control_RankRewardUpdated 				= 655 		#混沌神域_通知逻辑进程今日奖励已更新
Control_ChaosDivinityLogicRequest 		= 656 		#混沌神域_逻辑进程请求排行榜数据
Control_SyncChaosDivinityTYRank 		= 658 		#混沌神域_同步今日、昨日排行榜到逻辑进程