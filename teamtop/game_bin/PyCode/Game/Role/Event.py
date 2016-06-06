#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Event")
#===============================================================================
# 角色事件
# 这个模块的主要功能的减少模块之间的复杂导入问题
#===============================================================================
from Util import Callback, Trace
import Environment
import cProcess

if "_HasLoad" not in dir():
	HasFinishLoad = False
	RoleEventCallBack = Callback.LocalCallbacks()

def RegEvent(key, fun, deadTime = (2038, 1, 1), index = -1):
	RoleEventCallBack.RegCallbackFunction(key, fun, deadTime, index)

def TriggerEvent(key, role, param = None):
	if HasFinishLoad is False:
		#完全载入脚本后才可以触发事件
		Trace.StackWarn("TriggerEvent without load script succeed.")
		cProcess.Crash()
	RoleEventCallBack.CallAllFunctionExs(key, role, param)
	
# 定义事件
Eve_AfterLogin = 0				#登录之后(在Eve_InitRolePyObj之后, 也是只能做登录逻辑处理，数据同步请在Eve_SyncRoleOtherData里面触发)
Eve_BeforeExit = 1				#退出之前(先触发这个，然后才是调用离开场景!!!!!这个顺序不能乱啊)
Eve_AfterLevelUp = 2			#升级之后(有可能在登录的时候触发，例如某些离线挂机，登录获得经验的系统导致的)
Eve_BeforeSaveRole = 3			#保存角色之前
Eve_InitRolePyObj = 4			#角色初始化并部分对象信息(只能用与初始化请慎重使用，这个会运行在版本修复之前，不能在这里触发同步数据给客户端)
Eve_SyncRoleOtherData = 5		#角色登录同步其他剩余的数据(登录同步的所有数据都是要在这里触发，不能有其他登录逻辑)
Eve_RoleDayClear = 6			#角色每日清理调用
Eve_AfterChangeRoleGrade = 7	#角色升阶

Eve_LoadMonsterConfigOk = 8		#成功载入怪物配置
Eve_FirstInitRole = 9			#角色第一次初始化
Eve_AfterLoadItemConfig = 10	#读入物品配置完毕
Eve_ClientLost = 11				#客户端掉线(连接断了,role还是有效的，等待一段时间重连，如果不连接上就踢掉客户端并且清理role)

Eve_AfterLoadSceneNPC = 12		#成功读入SceneNPC配置

Eve_AfterJoinUnion = 13			#加入公会
Eve_AfterLeaveUnion = 14		#离开公会

Eve_AfterRoleUpgrade = 15		#主角进阶

Eve_AfterMallBuy = 16			#神石商城购买之后

Eve_AfterLoginJoinScene = 17	#触发登陆进入公共场景后

Eve_AfterLevelUpHero = 18		#升级英雄
Eve_Finish_EvilHole = 19		#通关恶魔深渊
Eve_Finish_FB = 20				#通关副本

Eve_AfterSetKaiFuTime = 21		#开服时间设置之后

Eve_AfterChangeStep = 22		#改变任务步骤之后
Eve_AfterStrengthen = 23		#强化装备之后
Eve_AfterEquipmentUpgrade = 24	#进阶装备
Eve_AfterMountEvolve = 25		#坐骑进化
Eve_AfterStudySkill = 26		#学习技能
Eve_AfterLevelUpSkill = 27		#升级技能
Eve_AfterZhaoMuHero = 28		#招募获得一个英雄
Eve_AfterUpgradeHero = 29		#进阶获得一个英雄
Eve_AfterInviteQQFriend = 30	#邀请了QQ好友
Eve_AfterInviteeChange = 31		#被邀请者的信息变化了
Eve_SubTask = 32				#触发支线任务检测

Eve_FinishPurgatory = 33		#通关心魔炼狱

Eve_ChangeTitle = 34			#称号信息改变

Eve_AfterOnWing = 35			#装备翅膀后调用
Eve_AfterOffWing = 36			#卸下翅膀后调用

Eve_AfterChangeUnionName = 37	#公会改名后调用

Eve_AfterLoadWorldData = 38		#载入世界数据之后


Eve_SpecialSubTask = 52			#触发特殊支线任务
Eve_GamePoint = 54				#游戏点消费触发(不同平台不一样，腾讯是Q点)
Eve_AfterChangeName = 56		#玩家改名成功后
Eve_Sys_RoleFightData_OK = 1000	#系统成功载入战斗数据

Eve_DoDailyDo = 57				#做每日必做任务

AfterChangeUnbindRMB_Q = 58		#Q点神石改变

Eve_StartCircularActive = 59	#开启一个循环活动 请搜索 @CircularDefine
Eve_EndCircularActive = 60		#结束一个循环活动 请搜索 @CircularDefine
AfterChangeUnbindRMB_S = 61		#系统赠送神石改变

Eve_NewHero = 62				#获得一个新英雄(AddHero, 招募， 进阶都会触发)

Eve_BuyMonthOrYearCard = 63		#购买月卡或者年卡

Eve_AfterShareQQ = 64			#分享

Eve_RoleChangeGender = 65		#玩家变性

Eve_ChangeMarryRoleName = 66	#改变玩家结婚对象名字

Eve_AfterLoadWorldDataNotSync = 67	#载入世界数据2

Eve_AfterSystemHeFu = 68		#合服之后触发一次(系统处理)
Eve_AfterRoleHeFu = 69			#合服之后触发一次(角色处理)

Eve_AfterOnFashion = 70		#玩家穿/脱时装
Eve_AfterFashionState = 71		#玩家时装显示状态

Eve_FB_AfterJJC = 73			#找回竞技场
Eve_FB_AfterQNA = 74			#找回答题
Eve_FB_AfterHW = 75				#找回荣耀之战
Eve_FB_AfterDF = 76				#找回魔兽入侵

Eve_RecountZDL = 77				#重算战斗力事件

QQidip_Eve = 78				#idip事件记录
Eve_DelUnion = 79				#解散公会

Eve_ChangeCirActID = 80			#改变循环活动ID

Eve_StartKaifuTarget = 81		#开启七日目标
Eve_EndKaifuTarget = 82			#关闭七日目标

Eve_IncChristmasWingLotteryTime = 83	#增加圣诞羽翼转转乐免费次数
Eve_IncChristmasMountotteryTime = 84	#增加圣诞坐骑转转乐免费次数

Eve_FB_TiLiTask = 85		#找回体力任务
Eve_FB_DayTask = 86			#找回日常任务
Eve_FB_FB = 87				#找回副本
Eve_FB_HT = 88				#找回英灵神殿
Eve_FB_DL = 89				#找回勇者试练场
Eve_FB_CFB = 90				#找回情缘副本


Eve_AfterSendRose = 91		#赠送99朵玫瑰
Eve_TryCouplesGoal = 92		#情人目标尝试触发完成 根据触发参数处理逻辑
Eve_TryInGlamorRank = 93	#魅力值增加 触发尝试入榜

Eve_UpdateValentineDayVersion = 94	#魅力情人节活动版本号更新

Eve_RoleBackVIPLevel = 95	#回流用户的老服VIP等级 (0 - 20) 只要有触发，都是回流用户
Eve_AfterChangeDayBuyUnbindRMB_Q = 96	#每日充值数改变后触发
Eve_AfterChangeDayConsumeUnbindRMB = 97	#每日消费改变后触发

Eve_LatestActivityTask = 98			#最新活动活跃度任务

Eve_WangZheCrazyRewardTask = 99		#王者公测之奖励狂翻倍任务

Eve_PassionMultiRewardTask = 100	#激情活动之奖励狂翻倍任务

Eve_AfterChangeStationSoul = 101	#阵灵改变

Eve_AfterWarStation = 102			#战阵星级改变

Eve_AfterEquipmentWash = 103		#消耗装备洗练石装备洗练一次

Eve_QQCheckVersion = 104			#检查蓝钻黄钻相关活动版本号

Eve_AfterChangeDayConsumeUnbindRMB_Q = 105	#每日消费充值神石改变后触发

Eve_NewYearDayPigTask = 106			#元旦活动之金猪日常任务
Eve_AfterLoadSucceed = 107			#脚本载入完毕，配置表读取完毕

Eve_QQLZTimesMayChanged = 108 		#QQ蓝钻开通次数可能已经改变