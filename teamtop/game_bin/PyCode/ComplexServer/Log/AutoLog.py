#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Log.AutoLog")
#===============================================================================
# 日志模块
#===============================================================================
import os
import cProcess
import cLogTransaction
import Environment
import DynamicPath
from Common import CValue
from Util import Trace
from Util.File import TabFile
from ComplexServer.Plug.DB import DBProxy

# 系统角色ID
SystemID = cProcess.ProcessID * CValue.P2_32
LogFile = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).FilePath("AutoTransaction.txt")	

def RegEvent(eve, s):
	Events[eve] = s

# 下面这个函数由C++中调用
def __LogValue(logid, roleid, transaction, event, old, new):
	if Environment.IsDevelop is True and not transaction:
		sw = "LogValue has not transaction (%s, %s, %s)" % (logid, roleid, event)
		Trace.StackWarn(sw)
	DBProxy.DBLogValue(logid, roleid, transaction, event, old, new, "")

def LogBase_Normal(roleid, event, content = ""):
	#不管有没有事务，根据事件强制获取事务
	transaction, logid = cLogTransaction.GetTransactionForEvent()
	DBProxy.DBLogBase(logid, roleid, transaction, event, repr(content))

def LogValue_Normal(roleid, event, old, new, content = ""):
	#不管有没有事务，根据事件强制获取事务
	transaction, logid = cLogTransaction.GetTransactionForEvent()
	DBProxy.DBLogValue(logid, roleid, transaction, event, old, new, repr(content))

def LogObj_Normal(roleid, event, obj_id, obj_type, obj_int, obj_data, content = ""):
	#不管有没有事务，根据事件强制获取事务
	transaction, logid = cLogTransaction.GetTransactionForEvent()
	DBProxy.DBLogObj(logid, roleid, transaction, event, obj_id, obj_type, obj_int, repr(obj_data), repr(content))

def LogBase_Check(roleid, event, content = ""):
	#不管有没有事务，根据事件强制获取事务
	transaction, logid = cLogTransaction.GetTransactionForEvent()
	DBProxy.DBLogBase(logid, roleid, transaction, event, repr(content))
	if transaction == 0:
		Trace.StackWarn("no transaction")

def LogValue_Check(roleid, event, old, new, content = ""):
	#不管有没有事务，根据事件强制获取事务
	transaction, logid = cLogTransaction.GetTransactionForEvent()
	DBProxy.DBLogValue(logid, roleid, transaction, event, old, new, repr(content))
	if transaction == 0:
		Trace.StackWarn("no transaction")

def LogObj_Check(roleid, event, obj_id, obj_type, obj_int, obj_data, content = ""):
	#不管有没有事务，根据事件强制获取事务
	transaction, logid = cLogTransaction.GetTransactionForEvent()
	DBProxy.DBLogObj(logid, roleid, transaction, event, obj_id, obj_type, obj_int, repr(obj_data), repr(content))
	if transaction == 0:
		Trace.StackWarn("no transaction")

if "_HasLoad" not in dir():
	if Environment.IsWindows:
		LogBase = LogBase_Check
		LogValue = LogValue_Check
		LogObj = LogObj_Check
	else:
		LogBase = LogBase_Normal
		LogValue = LogValue_Normal
		LogObj = LogObj_Normal

class AutoTransaction(object):
	def __init__(self, name, zs = ""):
		'''
		构建一个自动事务
		@param name:事务名
		@param zs:中文注释
		'''
		if isinstance(name, int):
			self.transaction = name
		else:
			self.transaction = AllotTransaction(name, zs)
	
	def __enter__(self):
		cLogTransaction.StartTransaction(self.transaction)
	
	def __exit__(self, _type, _value, _traceback):
		cLogTransaction.EndTransaction()
		return False
	
class BuildTransaction(object):
	def __init__(self, tra):
		'''
		构建一个自动事务
		@param tra:事务ID
		'''
		self.transaction = tra
	
	def __enter__(self):
		cLogTransaction.StartTransaction(self.transaction)
	
	def __exit__(self, _type, _value, _traceback):
		cLogTransaction.EndTransaction()
		return False

#===============================================================================
# 自动分配事务
#===============================================================================
class Transaction(TabFile.TabLine):
	FilePath = LogFile
	UseCache = False
	def __init__(self):
		self.name = str
		self.value = int
		self.zs = str

def LoadTransaction():
	for t in Transaction.ToClassType(False):
		assert t.name not in AutoTransactions
		assert t.value not in Transactions
		AutoTransactions[t.name] = t.value
		Transactions[t.value] = t.zs

def SvnUp(isUp = True):
	global HasNewMsg, CanAllotMsg
	HasNewMsg = False
	# 只有WIN下逻辑进程才需要更新日志事务
	if isUp and Environment.IsWindows and Environment.HasLogic and Environment.IP != "192.168.8.108":
		if not Environment.EnvIsFT() and not Environment.EnvIsNA() and not Environment.EnvIsRU():
			#只有主干开发环境才可以分配消息
			os.system('svn up %s' % LogFile)
			CanAllotMsg = True
	# 载入文件
	AutoTransactions.clear()
	Transactions.clear()
	LoadTransaction()

def SvnCommit():
	global HasNewMsg, CanAllotMsg
	CanAllotMsg = False
	# 检测日志
	Check()
	# 同时满足以下几个条件需要提交消息文件
	# 1 在WIN下
	# 2 有逻辑模块（有可能是django）
	# 3 有新日志事务
	if not Environment.IsWindows:
		return
	if not Environment.HasLogic:
		return
	if not HasNewMsg:
		return
	# 需要提交消息文件
	with open(LogFile, "wb") as f:
		f.write("value\tname\tzs\r\n事务值\t事务名\t注释\r\n")
		msgs = AutoTransactions.items()
		msgs.sort(key=lambda it:it[1])
		for name, value in msgs:
			f.write("%s\t%s\t%s\r\n" % (value, name, Transactions[value]))
	os.system('svn commit %s -m "Auto Transaction Commit"' % LogFile)

def SvnCommitEx():
	global HasNewMsg, CanAllotMsg
	CanAllotMsg = False
	# 检测日志
	Check()
	# 同时满足以下几个条件需要提交消息文件
	# 1 在WIN下
	# 2 有逻辑模块（有可能是django）
	# 3 有新日志事务
	if not Environment.IsWindows:
		return
	if not Environment.HasLogic:
		return
	if not HasNewMsg and AutoTransactionNames == set(AutoTransactions.keys()):
		return
	# 需要提交消息文件
	with open(LogFile, "wb") as f:
		f.write("value\tname\tzs\r\n事务值\t事务名\t注释\r\n")
		msgs = AutoTransactions.items()
		msgs.sort(key=lambda it:it[1])
		for name, value in msgs:
#			if name not in AutoTransactionNames:
#				print "-->delete transaction(%s) value(%s)" % (name, value)
#			else:
			f.write("%s\t%s\t%s\r\n" % (value, name, Transactions[value]))
	os.system('svn commit %s -m "Auto Transaction Commit"' % LogFile)


def AllotTransaction(name, zs = "None"):
	# 事务名必须唯一
	if name in AutoTransactionNames:
		print "GE_EXC, AllotTransaction has log name", name
	assert name not in AutoTransactionNames
	AutoTransactionNames.add(name)
	# 看是否有这个事务了
	tra = AutoTransactions.get(name)
	# 如果有，直接返回
	if tra:
		#更新注释
		Transactions[tra] = zs
		return tra
	# 如果没有则需要智能分配一个事务
	# 1 必须在脚本载入的时候分配
	if not CanAllotMsg:
		Trace.StackWarn("no transaction")
	assert CanAllotMsg
	# 2 标记新分配了事务
	global HasNewMsg
	HasNewMsg = True
	# 3 分配事务并且记录和返回
	if AutoTransactions:
		new_tra = max(AutoTransactions.itervalues()) + 1
	else:
		new_tra = 1
	assert new_tra < traNone
	Transactions[new_tra] = zs
	AutoTransactions[name] = new_tra
	return new_tra

def Check():
	from ComplexServer.Log import AutoLog
	from Util.PY import PyParseBuild
	mo = PyParseBuild.PyObj(AutoLog)
	# 1  检测手动分配的变量名和值唯一
	# 2  检测手段分配的值的取值范围
	# 3  检测全部的值唯一
	tra_name = set()
	tra_value = set()
	eve_name = set()
	eve_value = set()
	for k, v, z in mo.GetEnumerateInfo(False):
		if k.startswith("tra"):
			assert k not in tra_name
			assert v not in tra_value
			assert v >= traNone
			#assert v not in Transactions
			tra_name.add(k)
			tra_value.add(v)
			Transactions[v] = z
		elif k.startswith("eve"):
			assert k not in eve_name
			assert v not in eve_value
			assert v >= eveNone
			#assert v not in Events
			eve_name.add(k)
			eve_value.add(v)
			Events[v] = z

def LoadTE():
	from Util.PY import PyParseBuild
	pf = PyParseBuild.PyFile(__name__)
	for k, v, z in pf.GetEqualInfo():
		if k.startswith("tra") and v.isdigit():
			Transactions[int(v)] = z
		elif k.startswith("eve") and v.isdigit():
			Events[int(v)] = z

if "_HasLoad" not in dir():
	# 事务 事务 --> 中文注释
	Transactions = {}
	# 事件 事件 --> 中文注释
	Events = {}
	# 智能分配的事务信息 事务名 --> 事务
	AutoTransactions = {}
	# 自能分配事务名唯一检查
	AutoTransactionNames = set()
	# 是否有新的自动分配的日志事务
	HasNewMsg = False
	# 是否可以分配日志事务
	CanAllotMsg = False
	# 载入事务
	if not Environment.HasLogic:
		LoadTransaction()
		LoadTE()

#===============================================================================
# 手动分配事务
#===============================================================================
traNone = 								30000	#占位30000
traGM = 								30001	#GM指令
traRoleGM = 							30002	#内网GM指令
traRoleCommand = 						30003	#角色离线命令
traTiLi_C = 							30004	#C++时间触发改变角色体力(请不要修改这个)
traMail_BackStage = 					30005	#后台邮件
traBraveHeroMailReward = 				30006	#勇者英雄排名奖励邮件
traQQidipMail = 						30007	#腾讯idip邮件奖励(请不要修改这个)
traQQRank = 							30008	#腾讯idip消费排行榜
traHaoqiMailReward = 					30009	#豪气冲天跨服排名奖励邮件
traDayClear = 							30010	#C++触发每日清理(请不要修改这个)
traChristmasHaoMailReward = 			30011	#有钱就是任性跨服排名奖励邮件
traNewYearHaoMailReward = 				30012	#新年我最壕跨服排名奖励邮件
traLanternRankMailReward = 				30013	#元宵节点灯高手跨服排名奖励邮件
traGlamourRankMailReward = 				30014	#魅力排行奖励邮件
traSpringBMailReward = 					30137	#春节活动跨服排名奖励邮件
traQingMingRankMailReward = 			30138	#清明排行奖励邮件
traWangZheRankMailReward = 				30039	#王者积分排行奖励邮件
traPassionRechargeRankMailReward = 		30040	#激情活动充值排行奖励邮件
traPassionConsumeRankMailReward = 		30041	#激情活动消费排行奖励邮件
traQuestionFinalsRankMailReward = 		30244	#新答题活动跨服排名发奖
traKuafuFlower = 						30245	#跨服鲜花榜排名奖励邮件
traCatchingFishMailReward = 			30246	#跨服捕鱼达人排名奖励邮件
traD12GroupBuyPre20 = 					30247	#超值团购前20名奖励邮件
traD12GroupBuy = 						30248	#超值团购补差价邮件
traGame2048Reward = 					30249	#宝石2048排名发奖
#===============================================================================
# 手动分配事件
#===============================================================================
eveNone = 								30000	#占位30000
eveLoginData = 							30001	#登录数据
eveLoginObj = 							30002	#登录obj
eveTrade = 								30003	#商店购物 (2014.9.15再次启用)
eveAddItemPackageFull = 				30004	#增加物品的时候背包满了
eveGetAward = 							30005	#领取玩法奖励
eveRoleStudySkill = 					30006	#主角学习技能
eveAddItem = 							30007	#增加物品事件
eveDelItem = 							30008	#删除物品事件
eveMoveItem = 							30009	#移动物品更新
eveStrengthenEquipment = 				30010	#强化装备事件
eveUpGradeEquipment = 					30011	#装备升阶
eveSendMail = 							30012	#发送邮件
eveRoleCommand = 						30013	#角色离线命令
eveQDeliver = 							30014	#Q点发货
eveTarot_AddCard = 						30015	#增加一个命魂
eveTarot_DelCard = 						30016	#删除一个命魂
eveAddHero = 							30017	#增加一个英雄
eveFireHero = 							30018	#离队一个英雄
eveGM = 								30019	#GM指令
eveRoleGM = 							30020	#角色GM指令
eveRoleLevelUpSkill = 					30021	#角色升级技能
eveMainTask = 							30022	#主线任务
eveRoleVersionUpdataOk = 				30025	#角色成功进行一次版本修复
eveGodcastEquipment = 					30029	#装备神铸
eveUnionTransferLeader = 				30031	#公会转让团长
eveTarot_LevelUp = 						30032	#占卜命魂升级
eveRushLevelReward = 					30033	#冲级排名奖励
eveUpGradeHero = 						30034	#英雄升阶
eveUseExpItemHero = 					30035	#英雄使用经验丹
eveGloryWarCampWin = 					30036	#荣耀之战阵营胜负
eveGloryWarUnionRank = 					30037	#荣耀之战公会排名
eveGloryWarScoreRank = 					30038	#荣耀之战积分排名
eveGloryWarScore = 						30039	#荣耀之战积分
eveCardsTime = 							30040	#月卡时间
eveLevelEquipmentGem = 					30041	#升级装备上面的宝石
eveRoleExit = 							30042	#角色退出游戏时间
eveLevelArtifactGem = 					30043	#升级神器上面的符文
eveUnionChangeName = 					30044	#公会名字修改
eveCircularActiveStart = 				30045	#循环活动开启
eveAddWing = 							30046	#添加一个翅膀
eveAddPet = 							30047	#添加一个宠物
eveWonderMountDB = 						30048	#精彩活动坐骑争霸
eveWonderUnionDB = 						30049	#精彩活动公会竞赛
eveWonderZDLDB = 						30050	#精彩活动战力绝伦
eveWonderJJCDB = 						30051	#精彩活动竞技场
eveWonderDuke = 						30052	#精彩活动城主轮值
eveWonderGloryWar = 					30053	#精彩活动荣耀之战
eveWonderDisAct = 						30054	#精彩活动清除已激活的活动
eveWonderReward = 						30055	#精彩活动领奖
evePetFarmMachine = 					30059	#宠物灵树种植
eveChangeRoleGender = 					30060	#变性
eveCircularActiveEnd = 					30061	#循环活动结束
eveAsteroidFieldsReset = 				30062	#魔域星宫重置关卡
eveHallowsEnchant = 					30063	#圣器附魔
eveHallowsInheritance = 				30064	#圣器继承
evehallowsRefineSave = 					30065	#圣器洗练保存属性
eveReservationWedding = 				30066	#预约婚礼
eveCancelPropose = 						30067	#取消婚礼
eveDivorce = 							30068	#离婚
eveAddTalentCard = 						30069	#增加一个天赋卡
eveWonderRingDB = 						30070	#精彩活动情比金坚
eveGiveCard = 							30071	#赠送月卡
eveReviveCard = 						30072	#收到月卡
eveEnchantEquipment = 					30073	#装备附魔事件
eveWonderZDLRankDB = 					30074	#精彩活动战力排行
eveWonderHefu = 						30075	#精彩活动合服后数据修正
eveQQRoleBack = 						30076	#腾讯用户回流记录
eveQQActivePage = 						30078	#腾讯页面礼包数据
eveProjectActReward = 					30079	#专题活动奖励
eveFashionStarSuc = 					30080	#时装升星
eveFashionOrderSuc = 					30081	#时装升阶
eveTeamTowerJumpFight = 				30082	#组队爬塔跳关
eveTeamTowerExitReward = 				30083	#组队爬塔退出收益列表
eveOnekeyStrengthenEquipment = 			30084	#一键强化装备事件
eveFindBackRMB = 						30085	#找回系统神石找回数据
eveFindBackOneKeyRMB = 					30086	#找回系统一键神石找回数据
eveFindBackTime = 						30087	#找回系统时间找回数据
eveBuyLuckyBag = 						30088	#购买福袋
eveRewardLongyin = 						30089	#每日充值奖励龙印
eveMountOutDate = 						30090	#坐骑过期
eveQQRank = 							30091	#腾讯idip消费排行榜
eveNAHalloween = 						30092	#北美万圣节活动奖励
evePackageSetPasswd = 					30093	#背包设置密码
evePackageRestetPasswd = 				30094	#背包重新设置密码
eveRequestPackageClearPasswd = 			30095	#请求背包清除密码
eveUnlockPackage = 						30096	#背包解锁
eveDragonVeinActivate = 				30097	#龙脉激活
eveStarGirlUnlock = 					30098	#星灵解锁
eveJTReward = 							30099	#组队跨服竞技场结算奖励记录
eveJTCrossClear = 						30100	#月结清理日志
evePartyTime = 							30101	#举办Party时间
eveUpGradeDragonEquipment = 			30102	#驯龙装备升阶
eveTGRechargeRewardCDK = 				30103	#充值送豪礼-抽中的CDK对应rewardId
eveNARoleBackReward = 					30104	#北美流失召回
eveZBGroupInitData = 					30105	#跨服争霸小组初始数据
eveZBFinalInitData = 					30106	#跨服争霸总决赛初始数据
eveFinalUpGradeData = 					30107	#跨服争霸总决赛晋级记录
eveFinalUpGradeChampionData = 			30108	#跨服争霸总决赛晋级冠军
eveKaifuTargetRank = 					30109	#七日目标排行榜结算数据
eveJTDismiss = 							30110	#解散战队
eveChristmasFashionShowDonate = 		30111	#圣诞时装秀赠送商品
eveChristmasFashionShowReceive = 		30112	#圣诞时装秀收到赠送商品
eveMountApperanceUp = 					30113	#坐骑外形品质进阶
eveChristmasWingLotteryDiscountLottery = 30114	#圣诞羽翼转转乐折扣次数抽奖
eveChristmasMountLotteryDiscountLottery = 30115	#圣诞坐骑转转乐折扣次数抽奖
eveQQHK_Record = 						30116	#qq管家 七日登录记录
eveJTSR = 								30117	#跨服争霸服务器奖励基本数据
eveAddTitle = 							30118	#获得称号数据
eveDelTitle = 							30119	#失去称号数据
eveChangeUnionResource = 				30120	#公会资源变化
eveNewYearLocalRank = 					30121	#新年我最壕本地排行榜
eveEquipmentWash = 						30122	#新生成的未保存的装备洗练属性
eveTitleLevelUp_1 = 						30123	#称号普通培养升级
eveTitleLevelUp_2 = 						30124	#称号高级培养升级
eveSevenDayHegemonyRank = 				30125	#七日争霸排行榜结算
eveQQHallLottery = 						30126	#大厅充值博饼骰子
eveStationMosaic = 						30127	#助阵位镶嵌
eveStationUnlock = 						30128	#助阵位解锁
eveFindBackBindRMB = 						30129	#找回系统魔晶找回数据
eveFindBackOneKeyBindRMB = 					30130	#找回系统一键魔晶找回数据
eveMarryFinish = 							30131	#完成婚礼
eveMarryRingDel = 							30132	#删除订婚戒指
eveMarryRingImprint = 						30133	#订婚戒指铭刻
eveHoneymoonBegin = 						30134	#蜜月开始
eveHoneymoonEnd = 							30135	#蜜月结束
eveLanternLocalRank = 						30136	#元宵节花灯高手本地排行榜
eveSpringBARank = 							30137	#春节最靓丽跨服排名奖励
eveSpringBLRank = 							30138	#春节最靓丽本地排行榜
eveRosePresentDonate = 					30139	#送人玫瑰_赠送
eveRosePresentReceive = 				30140	#送人玫瑰_收到赠送
eveCouplesFashionDonate = 				30141	#情侣炫酷时装_赠送
eveCouplesFashionReceive = 				30142	#情侣炫酷时装_收到赠送
eveGlamourRankLocalRank = 				30143	#魅力派对_本地排行榜
eveKuaFuJJCInFinalsList = 				30144	#跨服个人竞技场进入决赛名单
eveKuaFuJJCFinalsRewardRank = 			30145	#跨服个人竞技场决赛奖励排名
evePetTrain = 							30146	#宠物培养
evePetUpgrade = 						30147	#宠物升星
eveUniversalBuyData = 					30148	#全民团购清理跨服数据时本地缓存数据
evePetEvoData = 						30149	#宠物修行
evePetEvoTimesData = 					30150	#宠物一键修行日志
evePetEvoSucData = 						30151	#宠物进化日志
eveFashionJD = 							30152	#时装鉴定日志
eveJTFinalRoundData = 					30153	#跨服组队竞技场总决赛每轮战斗日志
eveUpdateRoseRebateVersion = 			30154	#玫瑰返利升级活动版本号
eveUpdateGlamourRankVersion = 			30155	#魅力排行升级活动版本号
eveMountExchange = 						30156	#兑换激活坐骑
eveHallowsShenzao = 					30157	#圣器神造
eveLevelHallowsGem = 					30158	#升级圣器上面的雕纹
eveKuafuPartyAuctionRecord = 			30159	#跨服派对竞拍记录
eveShareFriend = 						30160	#好友分享
eveInviteFriend = 						30161	#好友邀请
eveInviteFriendSuccess = 				30162	#好友邀请成功
eveTheMammon = 							30163	#天降财神
eveOldPlayerBackReward = 				30164	#老玩家回流至老服奖励
eveTheMammonTimeSetting = 				30165	#天降财神设置活动开启时间
eveTitleStarUp = 						30166	#称号升星事件
eveKuafuPartyAuctionMax = 				30167	#跨服派对竞拍最高记录
evePartySendCandy = 					30168	#派对发放喜糖
eveAwakenHero = 						30169	#英雄觉醒
eveShenWangBaoKu = 						30170	#神王宝库奖池神石数
eveTTOneKeyData = 						30171	#组队爬塔一键收益奖励时候的数据
eveQMOResetDesktop = 					30172	#清明踏青重置牌面
eveQingMingRankLocalRank = 				30173	#清明消费_本地排行榜
eveBraveHeroLocalRank = 				30174	#勇者英雄坛今日本地排行榜
eveZumaScore = 							30175	#祖玛分数
eveMagicSpiritUpgrade = 				30176	#魔灵升级
eveMagicSpiritRefresh = 				30177	#魔灵洗练
eveMagicSpiritSavePro = 				30178	#魔灵洗练属性保存
eveSuperInvestInvest = 					30179	#超级投资投资
eveSuperInvestReward = 					30180	#超级投资收益
eveUnionKuaFuWarTotalRoleRank = 		30181	#公会圣域争霸个人总榜
eveUnionKuaFuWarTotalUnionRank = 		30182	#公会圣域争霸公会总榜
eveUnionKuaFuWarUnionRoleRank = 		30183	#公会圣域争霸公会内个人榜
eveWildBossScore = 						30184	#野外寻宝积分日志
eveDDUnionRank = 						30185	#魔兽入侵公会排名
eveDDKillCnt = 							30186	#魔兽入侵击杀魔兽数量
eveWildBossBox = 						30187	#野外寻宝宝箱日志
eveWildBossDropBox = 					30188	#野外寻宝掉落宝箱日志
eveBraveHeroType = 						30189	#勇者英雄坛重算区域日志
eveSuperPromptionBuy = 					30190	#超值特惠购买
eveDragonLevel = 						30191	#神龙等级
eveDragonGrade = 						30192	#神龙阶级
eveHunluanSpaceInFight = 				30193	#混乱时空进入战斗(1-梦幻龙域, 2-群魔乱舞, 3-群魔乱舞boss)
eveYeYouJieDiscountRefresh = 			30194	#页游节折扣汇商品刷新
eveLatestAct = 							30195	#最新活动奖励
eveWangZheFashionShowDonate = 			30196	#最炫时装秀赠送商品
eveWangZheFashionShowReceive = 			30197	#最炫时装秀收到赠送商品
eveWangZheZheKouHuiRefresh = 			30198	#王者公测折扣汇商品刷新
eveWangZheRechargeRebateLottery = 		30199	#王者公测充值返利抽奖
eveWangZheRankLocalRank = 				30200	#王者公测积分本地排行榜
evePetItemAddPro = 						30201	#道具增加宠物属性
evePetItemEvoData = 					30202	#道具增加宠物修行进度
eveClashOfTitansFightTimeOut = 			30203	#诸神之战战斗播放超时
eveClashOfTitansDieReborn = 			30204	#诸神之战死亡复活
eveClashOfTitansRoleScoreRankFinal = 	30205	#诸神之战最终角色积分排行榜
eveClashOfTitansGetScore = 				30206	#诸神之战角色获得积分
eveGSTrade = 							30207	#GS商店购物
evePassionMarketRefresh = 				30208	#激情卖场货架刷新
evePassionDiscountDonate = 				30209	#特惠商品赠送商品
evePassionDiscountReceive = 			30210	#特惠商品收到赠送商品

evePassionRechargeLocalRank = 			30211	#激情活动充值排行本地排行榜

evePassionExchangeRefresh = 			30212	#激情活动限时兑换刷新
eveClashOfTitansOutScene = 				30213	#诸神之战离开场景

eveFindBackMoney = 						30214	#找回系统金币找回数据
eveFindBackOneKeyMoney = 				30215	#找回系统一键金币找回数据
eveExitData = 							30216	#登出数据
eveDemonDefenseAfterFight = 			30217	#魔兽入侵战斗记录(回合数, 战斗结束后获得CD)

eveUnionDismissByResourceLack = 		30218	#连续7日公会资源增长不达标导致公会解散

eveDKCNewReward = 						30219	#新龙骑试抽奖日志
eveQQSummerLevel = 						30220	#qq空间暑期活动升级
eveJTeamDayRewardData = 				30221	#组队竞技长日结系统数据记录
eveJTeamWeekRewardData = 				30222	#组队竞技长周结系统数据记录
eveEquipmentWashUpStar = 				30223	#使用升星石生成的未保存的装备洗练属性
eveRMBFundClear = 						30224	#神石基金清理数据（1-结束时购买已领取， 2-结束时未购买， 3-活动开启期间领取）
eveMysteryBoxLottery = 					30225	#活动神秘宝箱抽取奖励
eveHeroZhuanSheng = 					30226	#英雄转生
eveCrossTeamTowerJumpFight = 			30227	#虚空幻境跳关
eveCrossTeamTowerRankData = 			30228	#结算是虚空幻境排行
eveShangYueAuToReward = 				30229	#中秋赏月活动结束自动发奖
evePassionXiaoFeiMaiDanAward = 			30230	#激情活动你消费我买单活动奖励
evePassionLoginGiftLoginAward = 		30231	#激情活动登录有礼登录奖励
evePassionLoginGiftRechargeAward = 		30232	#激情活动登录有礼充值奖励
eveFlowerRankData = 					30233	#鲜花魅力榜数据
eveFlowerMeili = 						30234	#送花加魅力值
eveKuafuFlowerRankType = 				30235	#跨服鲜花榜重算区域日志

evePassionConsumeLocalRank = 			30236	#激情活动消费排行本地排行榜
eveLostSceneFind = 						30237	#迷失之境抓捕日志

eveDKCNewOneKeyFree = 					30238	#新龙骑试一键免费领奖日志
eveDKCNewOneKeyAll = 					30239	#新龙骑试一键全部收益日志

eveNZBGroupInitData = 					30240	#新版争霸赛筛选的各个战区100强名单
eveNZB32Data = 							30241	#新版争霸赛筛选的各个战区32强名单
eveNJTFinalRoundData = 					30242	#新版争霸赛总决赛每轮战斗日志
eveJTCheersData = 						30243	#跨服争霸赛喝彩次数记录
eveTJHCActivateCode = 					30244	#天降横财_激活兑奖码	

eveMDUnionRank = 						30250	#魔龙降临公会排名
eveMDAfterFight = 						30251	#魔龙降临战斗记录(回合数, 战斗结束后获得CD)
eveTouchGoldReward = 					30252	#点金大放送

eveDelTalentCard = 						30253	#删除天赋卡（卡id,类型）

eveDeepHellFloorReward = 				30254	#深渊炼狱塔层奖励roleID
eveDeepHellScoreReward = 				30255	#深渊炼狱积分排名

eveCardAtlasAct = 						30256	#卡牌图鉴激活(图鉴id, 图鉴组品阶)
eveCardAtlasUpgrade = 					30257	#卡牌图鉴升阶(图鉴id, 图鉴品阶, 图鉴组id, 图鉴组品阶)
eveCardAtlasLevel = 					30258	#卡牌图鉴升级(图鉴id, 图鉴等级)
eveCardAtlasChip = 						30259	#卡牌图鉴分解(卡牌id)
eveElementalEssenceTimes = 				30260	#精炼次数(精炼类型,增加数量)

eveElementSpiritCultivate = 			30261	#元素之灵培养

eveGame2048GetReward = 					30262	#宝石2048领奖
eveGame2048Srart = 						30263	#宝石2048开启一次

eveBrandSculpture = 					30264	#元素印记雕刻(印记ID,类型,颜色,等级,品质值)
eveBrandShenJi = 						30265	#元素印记升级(印记ID,新等级)
eveBrandFenJie = 						30266	#元素印记分解(印记ID,)

eveChaosDivinitySkill = 				30267	#混沌神域被动技能选取(技能Id,...)

eveFestivalRebate = 					30268	#春节大回馈玩家领取奖励[(天数索引，回馈神石)]
eveFestivalRebateSys = 					30269	#春节大回馈自动发放未领取的奖励([(天数索引，回馈神石),])

eveKFZCScore = 							30270	#跨服战场积分
eveKFZCEndScore = 						30271	#跨服战场结算积分
eveSecretGardenSingleLottery = 			30272	#秘密花园单次抽奖

eveSetUnionHongBao = 					30273	#公会红包发放成功(红包金额总数，红包个数，公会id，红包id)
eveGetUnionHongBao = 		 			30274	#公会红包领取成功(获得金额总数，公会id，红包id)
eveReturnUnionHongBao = 		 		30275	#超过24小时返还公会红包(返还金额总数，公会id，红包id)

eveChaosDivinityLocalRank =				30276

eveChunJieYuanXiaoChongZhi =			30277	#元宵充值领取奖励(1为第一个档次，2为第二个档次 )
eveElementBrandWashPro = 				30278	#印记洗练 (印记ID，oldUnsavePro, newUnsavePro)
eveElementBrandSavePro = 				30279	#保存印记洗练属性(印记ID，oldSavepro, newSavePro)
eveElementBrandTransmit = 				30280	#印记继承 (低级印记数据，高阶印记老数据，高阶印记新数据)
