# -*- coding:UTF-8 -*-
# XRLAM("Common.Other.EnumGameConfig")
#===============================================================================
# 游戏简单枚举
#===============================================================================

#===============================================================================
# 一些等级枚举
#===============================================================================
Level_30 = 30


#===============================================================================
# 排行榜
#===============================================================================
FlowerMaxCnt = 10#最大送花记录
FlowerMoney = 100#送花奖励金币参数

#===============================================================================
# 体力相关
#===============================================================================
TiLi_Buy_RMB = 20		#体力购买魔晶
TiLi_Buy_RMB_NA = 95	#体力购买魔晶_北美版
TiLi_Buy_RMB_RU = 100	#体力购买魔晶_俄罗斯版
TiLi_Buy_TiLi = 50		#每次购买体力值
TiLi_Buy_Times = 1		#普通玩家购买次数

#===============================================================================
# 主线任务砸蛋
#===============================================================================
#一级龙晶+8       25681
#坐骑培养石+2     25600
#一级法攻宝石+1:  25722
#一级物攻宝石+1：25721
#魔晶+18     
#金币+8888
#限时礼包+1：
EggMoney = 8888
EggBindRMB = 18
EggItems = [(25681, 8), (25600, 2), (25722, 1), (25721, 1)]


#===============================================================================
# 腾讯游戏保存到桌面奖励
#===============================================================================
#魔晶+50。一级龙晶+20.四级物攻石+1.四级法攻石+1
QSaveBindRMB = 50
QSaveItems = [(25681, 20), (25748, 1), (25749, 1)]



#===============================================================================
# 组队基本
#===============================================================================
OfflineTickSec = 300 #离线自动离队秒数
FastInviteCD = 30 #快速邀请CD秒

#===============================================================================
# 首冲奖励
#===============================================================================
ConsumeQPointRewardNeedLevel = 25	#领取首冲礼包需要的等级

#===============================================================================
# 副本
#===============================================================================
FB_DayMaxPlayTimes 		 = 20 		#每天最多参加副本次数
FB_EachFBDailyJoinCnt	 = 2			#每个副本每天可以参加的次数
FB_BuyTimesNeedRMB	 = 50			#购买每个副本需要的魔晶
FB_BuyTimesNeedRMB_NA = 225			#购买每个副本需要的魔晶_北美版
FB_BuyTimesNeedRMB_RU = 50			#购买每个副本需要的魔晶_俄罗斯版
FB_GuaJiCD		 = 15 * 60			#副本挂机CD, 单位秒
FB_BuyCDNeedRMB	 = 1 				#副本每跳过1分钟CD需要的魔晶或者神石，不足1分钟按照1分钟算
FB_BuyCDNeedRMB_NA = 5				#副本每跳过1分钟CD需要的魔晶或者神石，不足1分钟按照1分钟算_北美版
FB_ActivedNeedLevel		 = 28		#开启副本玩法需要的基本等级

FB_VIP_Free = 5#

#===============================================================================
# 竞技场
#===============================================================================
JJC_Buy_Challenge_Cnt_Max = 20	#竞技场最大购买次数
JJC_PER_MINUTE_CD_NEED_RMB = 1			#竞技场每分钟CD需要的RMB
JJC_PER_MINUTE_CD_NEED_RMB_NA = 5		#竞技场每分钟CD需要的RMB_北美版

#===============================================================================
# 公会
#===============================================================================
Union_Create_Need_RMB = 10			#创建公会需要消耗的神石
Union_NA_Create_Need_Bind_RMB = 100	#北美版创建工会需要消耗的魔晶

Union_Gold_Box_Need_RMB = 20000			#开启金宝箱需要RMB
Union_Silver_Box_Need_RMB = 10000		#开启银宝箱需要RMB
Union_Copper_Box_Need_RMB = 5000		#开启铜宝箱需要RMB
Union_Gold_Box_Need_RMB_NA = 96000		#开启金宝箱需要RMB_北美版
Union_Silver_Box_Need_RMB_NA = 48000	#开启银宝箱需要RMB_北美版
Union_Copper_Box_Need_RMB_NA = 24000	#开启铜宝箱需要RMB_北美版
Union_Gold_Box_Need_RMB_RU = 15000		#开启金宝箱需要RMB_俄罗斯版
Union_Silver_Box_Need_RMB_RU = 10000	#开启银宝箱需要RMB_俄罗斯版
Union_Copper_Box_Need_RMB_RU = 5000		#开启铜宝箱需要RMB_俄罗斯版
Union_Get_Treasure_Need_Progress = 5#领取夺宝宝箱需要的进度
Union_Rob_Gold_Cnt_Max = 2			#夺取金宝箱次数
Union_Rob_Silver_Cnt_Max = 2		#夺取银宝箱次数
Union_Rob_Copper_Cnt_Max = 2		#夺取铜宝箱次数

Union_Clear_Join_CD_RMB = 50		#清除加入公会CD需要的神石或者魔晶

Union_Per_RMB_To_Union_Resource = 10		#贡献1神石对应公会资源基数
Union_Per_RMB_To_Member_Contribution = 5	#贡献1神石对应成员贡献度基数

UnionCntMax = 50				#每个阵营的最大公会数量
UnionNeedResourceDaily = 500	#公会每天须增加资源数
UnionMaxLackResourceDays = 7	#公会每日增加资源不达标连续天数（超过该天数就自动解散公会）
UnionHongBaoMessageLen = 45		#公会红包祝福语最多15个汉字, 每个汉字占三个编码长度		15 * 3
UnionHongBaoMinCnt = 5			#公会红包最少发5个
UnionHongBaoMaxRMB = 1000		#公会红包最大金额1000
UnionHongBaoRMB = 100			#内部使用的发红包道具代表充值神石个数
UnionHongBaoCnt = 10			#内部使用的发红包道具发放红包个数
#===============================================================================
# 英雄
#===============================================================================
Hero_ZhaoMu_LevelLimit = 15			#招募英雄等级限制
Hero_Altar_LevelLimit = 30			#英雄祭坛开启等级
Hero_Altar_FightType = 0			#英雄祭坛战斗类型
Hero_Altar_Normal_HeroCnt = 33		#英雄祭坛普通召唤最大英雄个数(最多能召唤一个英雄)
Hero_Altar_Advanced_HeroCnt = 32	#英雄祭坛高级召唤最大英雄个数(最多能召唤两个英雄)
Hero_Altar_DiscountCD = 86400		#英雄祭坛折扣召唤CD

#===============================================================================
# 阵形
#===============================================================================
Station_Level_Limit = 15			#上阵等级限制
HelpStation_Level_Limit = 31		#助阵等级限制
HelpStation_Level_LimitEx = 60		#副助阵位等级限制
HelpStation_Mosaic_LvLimit = 75		#助阵位水晶镶嵌等级限制
HSUnlockConsume = 388				#副助阵位解锁需要神石
#==========坐骑============
ACTIVE_MOUNT_LEVLE = 9 #激活坐骑的等级
VIP_Senior_Mount = 6 #贵族6开启高级培养
MountApperanceGradeLv = 40	#坐骑外形品质进化等级限制


#===============================================================================
# 恶魔深渊
#===============================================================================
EvilHoleNeedTiLi = 30#每次需要体力
EvilHoleSaoDangSec = 20 * 60#秒
FastSaoDangNeedRMB = 1#快速扫荡需要魔晶、分钟

#===============================================================================
# 占卜
#===============================================================================
TarotCard_Max_Level = 10				#最高等级
TarotNeedLevel = 50						#占卜需要等级
TarotActive_NeedUnBindRMB = 200			#高级占卜需要神石
TarotActive_NeedUnBindRMB_NA = 895		#高级占卜需要神石_北美版
TarotActive_NeedUnBindRMB_RU = 100		#高级占卜需要神石_俄罗斯版
TarotActive_ItemCoding = 26042			#高级占卜替代物品编码

TarotActive_Grade_4 = 1900			#高级占卜紫色概率
TarotActive_Grade_5 = 100				#高级占卜黄色概率

TarotRingNeedLevel = 70					#占卜光环开启等级
TarotRingMaxLevel = 10					#占卜光环最高等级
TarotRingStrengthenItemCoding = 26043	#强化光环需要物品
TarotSuperZhanbuMoneyLimit = 180000000	#超级抽取需要最小金币数
TarotSuperZhanbuLvLimit = 80			#超级抽取等级限制
TarotSuperZhanbuVipLimit = 7			#超级抽取vip限制

#===============================================================================
# 心魔炼狱
#===============================================================================
PurgatoryMaxCnt = 3			#心魔炼狱次数
PurgatoryFightType = 3		#心魔炼狱战斗类型
PurgatoryOnekeyVIP = 5		#心魔炼狱一键收益vip限制

#=========炼金===========
GLOD_LEVEL_ACTIVATE = 30 #炼金开启等级
GOLD_HELP_TIMES = 20 #每天协助炼金次数
GOLD_VIP_LEVLE = 5 #完美收获的vip等级
GOLD_PERFERT_TEN = 7 #显示10次完美收获的vip等级
Gold_MAX_SMELT_CNT = 3#非VIP玩家炼金次数
#===============================================================================
# 地精宝库
#===============================================================================
GT_Level = 30			#参与劫宝等级限制
GT_Sec = 15				#劫宝成功倒计时
GT_CD = 25				#劫宝战斗CD
GT_PVE_TYPE = 4			#劫宝与小妖战斗类型
GT_PVP_TYPE = 5			#劫宝与离线玩家战斗类型
GT_NA_REWARD_CNT_MAX = 4#劫宝北美版最大奖励次数
#===============================================================================
# 魔兽入侵
#===============================================================================
DD_NEED_LEVEL = 30	#参与魔兽入侵需要等级

#=========城主轮值========
FIGHT_LOST_CD = 60 #战斗失败CD
DUKE_SCENE_ID = 8 #场景ID
#==========宝石=========
VIP_ALL_SYNTHETI = 6 #一键合成
#==========巨龙宝藏=========
SEARCH_MAX_TIMES = 15	#每日玩家最多免费寻宝次数

#===============================================================================
# 每日必做
#===============================================================================
Daily_Level_Limit = 32		#领取奖励等级限制
#===============================================================================
# 答题
#===============================================================================
QandA_NEED_LEVEL = 30	#参与答题需要等级
QandA_SCENE_ID = 50		#答题场景id
QandA_the_line = 977		#答题场景中间线
#===============================================================================
#装备，神器宝石封灵需要
#================================================================================
DEFENCE_TYPE_GEM = (4, 5) #防御性宝石类型
#===============================================================================
# 在线礼包
#===============================================================================
OnlineReward_NEED_LEVEL = 4		#领取在线礼包需要的等级
#===============================================================================
# 符文宝轮
#===============================================================================
RuneWHeel_Need_Level = 60				#使用符文宝轮需要的等级
Fifty_RuneWHeel_Need_VIPLevel = 4		#50次抽奖需要的贵族等级
RuneWHeel_RunePearlCode = 26031			#符文宝珠物品编码
RuneWHeel_FirstTinmepRice = 20			#第一次符文宝轮价格
RuneWHeel_OtherTimePrice = 45			#非第一次符文宝轮价格
RuneWHeel_FirstTinmepRice_NA = 85		#第一次符文宝轮价格_北美版
RuneWHeel_OtherTimePrice_NA = 155		#非第一次符文宝轮价格_北美版
RuneWHeel_FirstTinmepRice_RU = 100		#第一次符文宝轮价格_俄罗斯版
RuneWHeel_OtherTimePrice_RU = 180			#非第一次符文宝轮价格_俄罗斯版
#===============================================================================
# 幸运转盘
#===============================================================================
LuckTurntable_Need_level = 30			#使用幸运转盘需要的等级
LuckTurntable_Need_VIPlevel = 1			#使用幸运转盘需要的VIP等级
LuckTurntablePrice = 20		#幸运转盘一次的价格为20神石
LuckTurntablePrice_NA = 85	#幸运转盘一次的价格_北美版
LuckTurntablePrice_RU = 150	#幸运转盘一次的价格_俄罗斯版
LuckTurntableInc = 6		#幸运转盘每次成功抽奖后奖池的增加数
#===============================================================================
# 荣耀之战
#===============================================================================
GloryWar_WorldLevel = 45								#开启世界等级
GloryWar_LevelLimit = 30								#进入等级限制
GloryWar_SceneID = 10									#场景ID
GloryWar_PvpFightFailCD = 10							#战斗失败CD时间
GloryWar_PvpFightWinCD = 7								#战斗胜利CD时间
GloryWar_PvpFightClickFailCD = 15						#战斗胜利CD时间
GloryWar_PVPFightType = 18								#pvp战斗类型
GloryWar_PVEFightType = 19								#pve战斗类型
#===============================================================================
#精彩活动
#===============================================================================
GEM_CONDIG_LIST = (25747, 25748, 25749, 25750, 25751, 25752, 25753, 25754, 25755, 26039, 26040, \
				  25997, 25998, 25999, 26000, 26001, 26002, 26003, 26004, 26005)	#宝石或宝石礼包
WONDERFUL_HERO_IDS = [15, 30, 45]	#精彩活动升橙色指定的英雄编号
#===============================================================================
# 会员
#===============================================================================
Card_BuyLevelLimit = 31			#购买月卡等级限制
Card_experienceTime = 1800		#月卡体验时间
Card_HalfYearGold = 10			#半年卡金币加成(乘了100的)
Card_YearGold = 10				#年卡金币加成
#===============================================================================
# 英灵神殿
#===============================================================================
HT_MinLevel = 80			#开启等级
HT_MaxCnt = 5				#最大行动次数
HT_NeedFBID = 62			#需要通关的副本ID
#===============================================================================
# 英雄圣殿
#===============================================================================
HS_MinLevel = 160			#开启等级
HS_MaxCnt = 2				#每日免费次数
HS_ItemCoding = 28239		#英雄圣殿替代行动力物品
#===============================================================================
# 奴隶系统
#===============================================================================

SlaveNeedLevel = 31			#开启等级

SlavePlayCD = 20 * 60		#互动CD
SlavePlayTimes = 6			#互动最大次数
SlaveCatchTimes = 10		#抓捕次数
SlaveSaveTimes = 6			#解救次数
SlaveBattleTimes = 3		#反抗(求救)次数

SlaveBuyCatchTimes = 10		#每天可以购买的抓捕次数
SlaveBuySaveTimes = 10		#每天可以购买的解救次数
SlaveBuyBattleTimes = 10	#每天可以购买的反抗(求救)次数

SlaveFightType_1 = 35			#奴隶主动战斗战斗类型
SlaveFightType_2 = 36			#奴隶观看战斗战斗类型
SlaveFightNeedLevel = 10	#抓奴隶，拯救，求助不得超过的等级差
SlaveOnHourNeedRMB = 20		#压榨一个小时需要魔晶
#===============================================================================
# 冲上云霄
#===============================================================================
ToSkyLevelLimit = 70			#冲上云霄等级限制
ToSkyNeedPackageSize = 3		#翻牌需要预留的背包空格
ToSkyFirstNeedRMB = 20			#第一次翻牌需要的神石
ToSkySecondNeedRMB = 40			#第二次翻牌需要的神石
ToSkyThirdNeedRMB = 88			#第三次及以后翻牌需要的神石
ToSkyFirstNeedRMB_NA = 85		#第一次翻牌需要的神石_北美版
ToSkySecondNeedRMB_NA = 155		#第二次翻牌需要的神石_北美版
ToSkyThirdNeedRMB_NA = 295		#第三次及以后翻牌需要的神石_北美版
ToSkyFirstNeedRMB_RU = 30		#第一次翻牌需要的神石_俄罗斯版
ToSkySecondNeedRMB_RU = 60		#第二次翻牌需要的神石_俄罗斯版
ToSkyThirdNeedRMB_RU = 132		#第三次及以后翻牌需要的神石_俄罗斯版
ToSkyMaxRecordCnt = 3			#最大奖励记录条数
#===============================================================================
# 宠物灵树
#===============================================================================
PETFARM_NEEDLEVEL = 70					#宠物灵树开启等级
PETFARM_ONEKEYHARVESTVIPLEVEL = 4		#宠物灵树一键收获开启等级
PETFARM_CDTIME = 96 * 60 * 60			#宠物灵树CD时间
PETFARM_QUICKERMACHINE_PRICE = 6		#宠物灵树快速种植价格
PETFARM_ROLEDATA_LENTH = 5				#玩家奖励信息长度
PETFARM_PER_HOUR_CD_NEED_RMB = 3		#宠物灵树每小时CD需要消耗的神石
PETFARM_PER_HOUR_CD_NEED_RMB_NA = 25	#宠物灵树每小时CD需要消耗的神石_北美版
PETFARM_PER_HOUR_CD_NEED_RMB_RU = 1		#宠物灵树每小时CD需要消耗的神石_俄罗斯版
PETFARM_QUICK_COST_NA = 55				#宠物灵树浇水消耗的神石
#===============================================================================
# 神秘商店
#===============================================================================
MysterShop_LevelLimit = 50				#神秘商店开启等级
#===============================================================================
# 狂欢充值
#===============================================================================
COT_Level_Needed = 45					#狂欢充值开启等级
COT_GlobalItemList = [26226, 26230, 26929, 26928, 26930, 26931, 28031, 28032, 27709, 27710]		#狂欢充值全服公告道具code列表
COT_GlobalTarotList = []			#狂欢充值全服公告命魂code列表
COT_GlobalTalentList = [7, 107, 19, 119]				#狂欢充值全服公告天赋卡列表
#===============================================================================
# 神石基金
#===============================================================================
RMBFund_LevelLimit = 30					#神石基金开启等级
#===============================================================================
# 一球成名
#===============================================================================
BallFame_LevelLimit = 45				#等级限制
BallFame_NeedItemCoding = 26235			#射门需要物品coding
BallFame_GoalsBox = 26236				#进球宝箱coding
BallFame_CheersBox = 26237				#喝彩宝箱coding
BallFame_MaxCheersCnt = 2				#最大喝彩次数
#===============================================================================
# 魔域星宫
#===============================================================================
AsteroidFields_NeedLevel = 80						#魔域星宫需要的等级
AsteroidFields_XingdongliPrice = {1:50, 2:100}		#魔域星宫行动力价格:{次数：价格}
AsteroidFields_XingdongliPrice_NA = {1:100, 2:200}	#魔域星宫行动力价格:{次数：价格}_北美版
AsteroidFields_XingdongliPrice_RU = {1:250, 2:500}		#魔域星宫行动力价格:{次数：价格}_俄罗斯版
AsteroidFieldsXiongdongliToCost = 1					#进入星域需要消耗的行动力个数
AsteroidFields_DailyInitXingdongli = 1				#魔域星宫每日初始行动力
#===============================================================================
# 砸龙蛋
#===============================================================================
SILVER_EGG_NEED_MONEY = 80000		#银龙蛋需要消耗的金币
SILVER_EGG_NEED_MONEY_NA = 150000	#北美银龙蛋需要消耗的金币
#===============================================================================
# 圣器
#===============================================================================
Hallows_Max_EnchantsLevel = 12 		#最大附魔等级
Hallows_RefinePrice = 10			#洗练价格
Hallows_RefinePrice_NA = 45			#北美洗练价格
Hallows_RefineLockPrice = 10		#洗练锁价格
Hallows_RefineLockPrice_NA = 45		#北美洗练锁价格
Hallows_RefineLockCode = 26302		#洗练锁code
Hallows_RefineLockCode_Tmp = 29430	#临时圣器洗练锁code
Hallows_EnchantNeedlevel = 80		#附魔开启等级
Hallows_ShenzaoNeedlevel = 80		#神造开启等级
Hallows_RefineStoneCode = 26272		#洗练石code
Hallows_RefineStoneCode_Tmp = 29428	#临时圣器洗练石code
Hallows_RefineStoneCost = 1			#洗练一次消耗的洗练石个数
#===============================================================================
# 婚戒
#===============================================================================
WeddingRingSoulCoding = 26342			#精炼石coding
WeddingRingSoulLockCoding = 26343		#精炼锁coding
WeddingRingCoding = 26344				#婚戒锻造石coding
WeddingRingSoulUnbindRMB = 10			#洗练需要的神石数量
WeddingRingSoulUnbindRMB_NA = 45		#北美用洗练需要的神石数量
#===============================================================================
# 结婚
#===============================================================================
MarryLevelLimit = 36									#结婚等级限制
MarryWorldPropseRMB = 120								#世界告白神石
MarryWorldPropseRMB_NA = 195							#北美世界告白神石
MarrySceneID = 17										#结婚场景ID
HoneymoonSayRMB = 120									#高级甜言蜜语消耗神石
MarryRingImprintLv = 60									#订婚戒指铭刻等级限制

MarryJoinWeddingLimit = 30								#参加婚礼等级限制
MarryScenePos = (3098, 1028)							#进入结婚场景的位置
MarrySceneMaxRoleCnt = 300								#单个结婚场景内最大人数
MarryLibaoCoding = 26346								#新婚礼盒
MarryHongbaoCoding = 26348								#新婚庆礼
MarryLibaocd = 15										#领取婚礼礼包CD
MarryBiaobaiRMB = 24									#购买表白次数价格
MarryFireworksRMB = 24									#购买烟花价格
MarryFireworksRMB_NA = 10								#北美购买烟花价格
MarryHandselCoding = 26347								#贺礼coding
MarryHandselRMB = 18									#贺礼价格
MarryDivorceMoney = 200000								#离婚金币
MarryInviteCD = 20										#世界邀请CD
MarryLibaoRandomList = [26032, 25600, 26344, 26342]		#礼包随机
MarryLibaoCnt = 30										#每日领取婚礼礼包个数限制
MarryRebateRMB = 10										#回赠贺礼价格
MarryRebateCoding = 26366								#回赠贺礼coding
#===============================================================================
# 变性
#===============================================================================
ChangeGenderNeedLevel = 1			#变性需要的等级
ChangeGenderCardCode = 26345		#变性卡code
#===============================================================================
# 勇闯十二宫
#===============================================================================
TwelvePalaceNeedLevel = 80			#勇闯十二宫需要等级
TwelvePalaceNeedVIP = 1				#勇闯十二宫需要VIP等级
TwelvePalaceHelpNeedLevel = 60		#勇闯十二宫协助闯宫所需等级
TwelvePalaceAskForHelpCD = 30		#勇闯十二宫请求协助CD时间
TwelvePalacePalaceCardCode = 26349	#闯宫令code
TwelvePalaceAwardCode = 26352		#勇闯十二宫奖励编码
TwelvePalaceAwardCnt = 1			#勇闯十二宫奖励个数
TwelvePalaceHelpAwardCode = 26351	#勇闯十二宫协助他人奖励编码
TwelvePalaceHelpAwardCnt = 1		#勇闯十二宫协助他人奖励个数
TwelvePalaceHelpPlayerLimit = 8		#协助闯宫 人数上限
TwelvePalaceInAdvancePrice = 10		#提前闯关价格
TwelvePalaceInAdvancePrice_NA = 25	#北美提前闯关价格
TwelvePalaceMaxHelpTimes = 2		#可以获得奖励的的最高协助次数
#===============================================================================
# 游戏联盟登录奖励 
#===============================================================================
GameUnionAiWanBuff = {1:150, 4:50, 6:50}		#游戏联盟爱玩登录buff
GameUnionQQGJBuff = {1:150, 4:50, 6:50}		#游戏联盟QQ管家登录buff

#===============================================================================
# 神石银行
#===============================================================================
RMBBankLevelLimit = 20				#神石银行等级限制
RMBBankMax = 10000					#神石银行最大存入数
RMBBankMax_NA = 20000				#北美神石银行最大存入数
#===============================================================================
#开服boss
#===============================================================================
KaifuBossNeedLevel = 32				#开服boss等级限制
KaifuBossSceneId = 64				#开服boss的场景 id 

#===============================================================================
# GVE
#===============================================================================
GVE_DAY_CNT_MAX = 3		#GVE每天最大次数

#===============================================================================
# 宠物转转乐
#===============================================================================
PET_LUCKY_DRAW_NEED_RMB = 48		#转一次单价
PET_LUCKY_DRAW_NEED_RMB_NA = 155	#转一次单价_北美版
PET_LUCKY_DRAW_NEED_RMB_RU = 80		#转一次单价_俄罗斯版

#===============================================================================
# 黄金宝箱
#===============================================================================
GoldChestNeedLevel = 45

#===============================================================================
# 许愿池
#===============================================================================
WP_ActGoldCnt = 100				#许愿池激活金币副本次数
WP_GoldRate = 1000				#许愿池激活金币副本概率
WP_GoldLevel = 30				#金币副本进入等级限制

#===============================================================================
# 勇者英雄坛
#===============================================================================
BraveHeroLevelLimit = 60		#勇者英雄坛等级限制
BraveHeroCntMax = 3				#勇者英雄坛最大次数
BraveHeroVIP = 6				#勇者英雄坛快速挑战vip等级限制
BraveHeroMaxBuyCnt = 39			#勇者英雄坛购买最大值(购买次数超过该值按该值的购买神石计算)
BraveHeroFightType = 42			#勇者英雄坛战斗类型
BraveHeroCanFightTime = 23		#勇者英雄坛不能挑战的时间点
#===============================================================================
# 天天秒杀
#===============================================================================
DailySeckillNeedLevel = 40		#天天秒杀的等级限制 
DailySeckillCD = 2				#天天秒杀的冷却时间
#===============================================================================
#合服boss
#===============================================================================
HefuBossNeedLevel = 32				#合服boss等级限制
HefuBossSceneId = 64				#合服boss的场景 id 
#===============================================================================
#VIP尊享服务
#===============================================================================
VIP_ExtraServiceNeedQPoint 		 = 30000		#VIP尊享服务对象最少Q点消费
VIP_PersonalInfoCommitReward 	 = 26512		#玩家个人信息提交奖励code
VIP_ExtraInfoMaxLenOfName		 = 30		#名字长度上限(中文长度为3)
VIP_ExtraInfoMaxLenOfIdCard		 = 20		#身份证长度上限
VIP_ExtraInfoMaxLenOfAdress		 = 90		#地址长度上限(中文长度为3)
VIP_ExtraInfoLenOfPhoneNum 		 = (8, 15)	#手机号长度限制
VIP_ExtraInfoLenOfQQNum			 = (6, 13)	#QQ号长度限制
#===============================================================================
#超值大礼
#===============================================================================
SuperDiscount_NeedLevel 		 = 30		#等级限制	

#===============================================================================
# 组队相关
#===============================================================================
TEAM_UNION_FB_NEED_LEVEL = 60		#公会副本需求等级
TEAM_GVE_NEED_LEVEL = 30			#GVE副本需求等级
TEAM_TOWER_NEED_LEVEL = 45			#组队爬塔需求等级
TEAM_TOWER_NEED_LEVEL_0 = 35			#组队爬塔序章需求等级



#===============================================================================
# 野外寻宝
#===============================================================================
WildBossRegionCnt = 6
WildBossMinLevel = 40								#野外寻宝最小等级
WildBossRegionList = [39, 60, 80, 100, 120, 140]	#战区最小等级
WildBossSafePos = (747, 843)						#野外寻宝失败传送场景
WildBossNpc_1 = [12103, 1855, 1360, 1, 1]			#野外寻宝npc1[npc类型, x点坐标, y点坐标, 朝向]
WildBossNpc_2 = [12104, 1855, 1360, 1, 1]			#野外寻宝npc2[npc类型, x点坐标, y点坐标, 朝向]
WildBossNpc_3 = [12105, 1855, 1360, 1, 1]			#野外寻宝npc3[npc类型, x点坐标, y点坐标, 朝向]
WildBossNpc_4 = [12106, 1855, 1360, 1, 1]			#野外寻宝npc4[npc类型, x点坐标, y点坐标, 朝向]
WildBossNpc_5 = [19032, 1855, 1360, 1, 1]			#野外寻宝npc5[npc类型, x点坐标, y点坐标, 朝向]
WildBossNpc_6 = [22004, 1855, 1360, 1, 1]			#野外寻宝npc6[npc类型, x点坐标, y点坐标, 朝向]
def get_wildboss_npc_data(regionIndex):
	npcDict = {1:WildBossNpc_1, 2:WildBossNpc_2, 3:WildBossNpc_3, 4:WildBossNpc_4, 5:WildBossNpc_5, 6:WildBossNpc_6}
	if regionIndex in npcDict:
		return npcDict[regionIndex]
	else:
		print 'GE_EXC, WildBoss get_wildboss_npc_data error region index (%s)' % regionIndex
		return npcDict[4]
WildBossMcid_1 = 14103								#野外寻宝boss1阵营ID
WildBossMcid_2 = 14104								#野外寻宝boss2阵营ID
WildBossMcid_3 = 14105								#野外寻宝boss3阵营ID
WildBossMcid_4 = 14106								#野外寻宝boss4阵营ID
WildBossMcid_5 = 17016								#野外寻宝boss5阵营ID
WildBossMcid_6 = 18090								#野外寻宝boss6阵营ID
def return_wildboss_mcid(regionIndex):
	mcidDict = {1:WildBossMcid_1, 2:WildBossMcid_2, 3:WildBossMcid_3, 4:WildBossMcid_4, 5:WildBossMcid_5, 6:WildBossMcid_6}
	if regionIndex in mcidDict:
		return mcidDict[regionIndex]
	else:
		print 'GE_EXC, WildBoss return_wildboss_mcid error region index (%s)' % regionIndex
		return mcidDict[4]
WildBoss_MaxHp_1 = 460800000						#野外寻宝boss1最大血量
WildBoss_MaxHp_2 = 1382400000						#野外寻宝boss2最大血量
WildBoss_MaxHp_3 = 2764800000						#野外寻宝boss3最大血量
WildBoss_MaxHp_4 = 6048000000						#野外寻宝boss4最大血量
WildBoss_MaxHp_5 = 12902400000						#野外寻宝boss5最大血量
WildBoss_MaxHp_6 = 12902400000						#野外寻宝boss6最大血量
def get_wildboss_maxhp(regionIndex):
	maxHpDict = {1:WildBoss_MaxHp_1, 2:WildBoss_MaxHp_2, 3:WildBoss_MaxHp_3, 4:WildBoss_MaxHp_4, 5:WildBoss_MaxHp_5, 6:WildBoss_MaxHp_6}
	if regionIndex in maxHpDict:
		return maxHpDict[regionIndex]
	else:
		print 'GE_EXC, WildBoss return_wildboss_maxhp error region index (%s)' % regionIndex
		return maxHpDict[4]
WildBossBoxCoding_1 = [26665, 26671, 26672, 26667]	#野外寻宝第一战区宝箱coding(按优先级排, 低优先级在前)
WildBossBoxCoding_2 = [26665, 26671, 26673, 26668]	#野外寻宝第二战区宝箱coding(按优先级排, 低优先级在前)
WildBossBoxCoding_3 = [26666, 26671, 26674, 26669]	#野外寻宝第三战区宝箱coding(按优先级排, 低优先级在前)
WildBossBoxCoding_4 = [26666, 26671, 26675, 26670]	#野外寻宝第四战区宝箱coding(按优先级排, 低优先级在前)
WildBossBoxCoding_5 = [26666, 26671, 26675, 26670]	#野外寻宝第五战区宝箱coding(按优先级排, 低优先级在前)
WildBossBoxCoding_6 = [26666, 26671, 26675, 26670]	#野外寻宝第六战区宝箱coding(按优先级排, 低优先级在前)
def get_wildboss_boxcoding(regionIndex):
	boxCodingDict = {1:WildBossBoxCoding_1, 2:WildBossBoxCoding_2, 3:WildBossBoxCoding_3, 4:WildBossBoxCoding_4, 5:WildBossBoxCoding_5, 6:WildBossBoxCoding_6}
	if regionIndex in boxCodingDict:
		return boxCodingDict[regionIndex]
	else:
		print 'GE_EXC, WildBoss return_wildboss_boxcoding error region index (%s)' % regionIndex
		return boxCodingDict[4]
WildBossZdl = 100000								#野外寻宝最小战斗力
WildBossMaxMoney_1 = 373400							#第一战区最大金币奖励
WildBossMaxMoney_2 = 498000							#第二战区最大金币奖励	
WildBossMaxMoney_3 = 672500							#第三战区最大金币奖励
WildBossMaxMoney_4 = 788880							#第四战区最大金币奖励
WildBossMaxMoney_5 = 946600							#第五战区最大金币奖励
WildBossMaxMoney_6 = 1104320						#第六战区最大金币奖励

#获得金币 = min(伤害 / 伤害金币系数, 最大金币奖励)
WildBossMoneyCoe_1 = 10								#第一战区伤害金币系数
WildBossMoneyCoe_2 = 24								#第二战区伤害金币系数
WildBossMoneyCoe_3 = 40								#第三战区伤害金币系数
WildBossMoneyCoe_4 = 60								#第四战区伤害金币系数
WildBossMoneyCoe_5 = 80								#第五战区伤害金币系数
WildBossMoneyCoe_6 = 100							#第六战区伤害金币系数

def GetWildBossMaxMoney(index):
	return {1 : WildBossMaxMoney_1, 2: WildBossMaxMoney_2, 3 : WildBossMaxMoney_3, 4 : WildBossMaxMoney_4, 5:WildBossMaxMoney_5, 6:WildBossMaxMoney_6}.get(index)
def GetWildBossMaxMoneyCoe(index):
	return {1 : WildBossMoneyCoe_1, 2: WildBossMoneyCoe_2, 3 : WildBossMoneyCoe_3, 4 : WildBossMoneyCoe_4, 5:WildBossMoneyCoe_5, 6:WildBossMoneyCoe_6}.get(index)

WildBossSingleFightType = 44						#单人抢夺战斗类型
WildBossBossFightType = 45							#boss战斗类型

WildBossBuffNpcType = 16074							#野外寻宝buffnpc类型
WildBossBuffNpcDirect = 1							#野外寻宝buffnpc朝向

#===============================================================================
# 中秋活动
#===============================================================================
AF_DailyLiBaoNeedLevel 	 = 30 			#中秋登陆礼包最低等级
AF_LatteryNeedLevel		 = 30			#中秋搏饼最低等级
AF_LatteryInitNomalNum 	 = 5				#中秋搏饼每日初始免费次数
AF_MasterRecordNum		 = 9			#中秋搏饼大奖记录条数		
AF_LatteryRollNum 		 = 6				#中秋搏饼单次摇骰子个数	
AF_LatteryMasterTypeMin	 = 5				#中秋搏饼大奖最低类型
AF_MoonCakeDayNumMax	 = 20			#中秋月饼使用次数上限
AF_LatteryDiceValue = {1:100000, 2:10000, 3:1000, 4:100, 5:10, 6:1}	#搏饼骰子权值 (方便判定摇出骰子类型)
#===============================================================================
# 黄钻大礼
#===============================================================================
QQHZGift_RollGiftNeedLevel 	 = 20			#黄钻转大礼等级限制
QQHZGift_RGMaxNum			 = 12			#黄钻转大礼最多次数
QQHZGift_RGMountProCoding	 = 27028			#黄钻转大礼最终大奖坐骑道具coding

QQHZGift_OfferGiftNeedLevel	 = 20			#黄钻献大礼等级限制
QQHZGift_OG_Daily_MaxNum 	 = 12			#黄钻献大礼每日最大次数
#===============================================================================
# 深海寻宝
#===============================================================================
SeaXunbaoLevelLimit = 60					#深海寻宝等级限制
SeaXunbaoNormalCoding = 26897				#深海普通寻宝coding
SeaXunbaoAdvanceCoding = 26898				#深海高级寻宝coding
SeaXunbaoNormalMoney = 80000				#深海普通寻宝单次需要金币
SeaXunbaoNormalMoney_NA = 150000			#北美深海寻宝单次需要的金币
#===============================================================================
# 组队爬塔
#===============================================================================
TT_RewardTimes = 2#每天收益次数
TT_OneKeyNeedVIPLevel = 2 #一键收益需要vip等级
#===============================================================================
# 驯龙系统
#===============================================================================
DT_NOT_VIP_DRAGON_SOUL_CNT = 2	#非VIP聚灵次数

#===============================================================================
# 星灵系统
#===============================================================================
STAR_GIRL_NORMAL_DIVINE_MAX_CNT = 10			#普通占星最大次数
STAR_GIRL_SUPER_DIVINE_MAX_CNT = 100			#虔诚占星最大次数
STAR_GIRL_NORMAL_DIVINE_MONEY = 10000			#普通占星消耗金币
STAR_GIRL_NORMAL_DIVINE_REWARD_STAR_LUCKY = 20	#普通占星获得的星运数量
STAR_GIRL_GIRL_LEVEL_UP_FREE_CNT = 10			#星灵升级免费次数
STAR_GIRL_PRAY_FREE_CNT = 3						#星灵祈祷免费次数
STAR_GIRL_ADD_LOVE = 2							#星灵每次增加的爱心值
STAR_GIRL_LUCKY_LEVEL = 60						#星灵幸运石使用等级

#===============================================================================
# 时装系统
#===============================================================================
ACTIVE_FASHION_LEVEL = 45	#激活时装等级
IDE_FASHION_LEVEL = 65		#激活鉴定功能等级
FORING_FASHION_LEVEL = 85	#激活时装升星，进阶等级
FASHION_HOLE_LEVEL = 90		#激活时装光环
FASHION_YIGUI_LEVEL = 45	#激活衣柜等级
#===============================================================================
# 国庆活动
#===============================================================================
ND_ExchangeNeedLevel = 30	#国庆奖励兑换等级限制

ND_DailyLiBaoNeedLevel = 30	#国庆登陆礼包等级限制

NationLevelLimit = 30				#国庆神石回赠等级限制
#===============================================================================
# 国庆副本
#==============================================================================
NATION_MIN_LEVEL = 30	#国庆副本最低等级限制
#===============================================================================
# 每日集龙印
#===============================================================================
CollectLongyinLvLimit = 20				#每日集龙印等级限制
#===============================================================================
# 万圣节
#==============================================================================
HALLOWEEN_MIN_LEVEL = 30	#万圣节活动最低等级限制
HALLOWEEN_CARD_LIOBAO = [27030, 27031, 27032]	#变身卡礼包

#===============================================================================
# 龙脉
#==============================================================================
DragonVeinLevelUp_DailyFreeTimes = 10	#龙脉每日免费升级次数
DragonVeinGrade_not_clear = 5			#从该等级开始祝福值不用每日清空
DragonVeinNeedLevel = 90 				#龙脉开启等级

#===============================================================================
# 蓝钻开通奖励
#==============================================================================
QQLZKaiTongGift_MaxTimes = 12	#蓝钻转大礼最多领奖次数
QQLZKaiTongGift_MountProCoding = 27039	#蓝钻转大礼最终大奖坐骑道具coding (for 蓝钻转大礼)

#===============================================================================
# 混乱时空
#===============================================================================
HunluanSpace_LvLimit = 32					#混乱时空等级限制
HunluanSpace_ClickCD = 50					#混乱时空点击cd

#===============================================================================
# 大厅搏饼
#===============================================================================
QQHall_LotteryNeedLevel		 = 30			#大厅搏饼最低等级
QQHall_LotteryMasterRecordNum = 9			#大厅搏饼大奖记录条数		
QQHall_LotteryRollNum 		 = 6				#大厅搏饼单次摇骰子个数	
QQHall_LotteryMasterTypeMin	 = 5				#大厅搏饼大奖最低类型
QQHall_LotteryDiceValue 	 = {1:100000, 2:10000, 3:1000, 4:100, 5:10, 6:1}	#搏饼骰子权值 (方便判定摇出骰子类型)

#===============================================================================
# 祝福轮盘
#===============================================================================
BlessRoulette_NeedLevel = 30	#等级限制
BlessRoulette_BatchDrawNum = 10	#批量抽奖次数
BlessRoulette_UnbindRMBCost = 88		#每次抽奖神石消耗
BlessRoulette_MineRecordSize = 10	#我的抽奖记录条数
BlessRoulette_MasterRecordSize = 6 #本服大奖记录条数 
#===============================================================================
# 豪气冲天
#===============================================================================
HaoqiRMBLimit = 10000				#豪气冲天上榜充值神石限制

#===============================================================================
# 狂欢兑不停
#===============================================================================
DoubleElevenShop_LvLimit = 30			#狂欢兑不停等级限制

#===============================================================================
# 团购嘉年华
#===============================================================================
GroupBuyCarnival_NeedLevel = 30	#等级限制
#===============================================================================
# 宠物福田
#===============================================================================
PetLuckyFarmNeedLevel = 70			#等级限制
PetLuckyFarmGoldHoeCode = 27154		#金锄头code
PetLuckyFarmSilverHoeCode = 27153	#银锄头code
PetLuckyFarmMoneyPerTime = 80000	#银锄头每次消耗的金币
PetLuckyFarmMoneyPerTime_NA = 150000#北美银锄头每次消耗的金币
#===============================================================================
# 结婚派对
#===============================================================================
PartyLvLimit = 15				#参与结婚派对等级限制
PartySceneID = 16				#结婚派对场景ID
PartyBlessMaxCnt = 30			#结婚派对每日最大祝福次数
PartyCD = 20					#结婚派对邀请cd
PartyKuafuCD = 240				#结婚派对跨服邀请cd
PartyCloseCnt = 250				#跨服派对关闭入口人数
PartyKickCnt = 300				#跨服派对开始踢人人数
PartyRestartCnt = 200			#跨服派对重新开放入口人数
PartyKuafuTitleID = 36			#跨服派对称号id
PartyKuafuBoxLimit = 10000		#可以领取跨服礼包喜庆度限制

#==============================================================================
# 龙魂石碑
#===============================================================================
DragonStele_NeedLevel = 45				#等级限制
DragonStele_ExtraBoundary = 100			#额外奖励获取次数（每DragonStele_ExtraTime次获得一次额外）
DragonStele_BatchTimes = 10				#批量祈祷的祈祷次数
DragonStele_PrayPro_Nomal = 27166		#普通祈祷道具 银龙币
DragonStele_PrayPro_Special = 27165		#高级祈祷道具 金龙币
DragonStele_PrayMoney = 80000			#单次普通祈祷金币
DragonStele_PrayMoney_NA = 150000		#北美单次普通祈祷金币
DragonStele_PrayRMB = 88				#单次高级祈祷神石
DragonStele_PrayRMB_NA = 195			#北美单次高级祈祷神石

#===============================================================================
# 蓝钻献大礼
#===============================================================================
QQLZGift_OG_NeedLevel 		 = 30		#等级限制
QQLZGift_OG_DayMaxTimes		 = 12		#每日最多领奖次数次数
QQHZGift_OG_MountProCoding	 = 27028		#最终大奖坐骑道具coding
#===============================================================================
# 步步高升
#===============================================================================
StepByStepMaxChestIndex = 7				#步步高升最大宝箱索引
StepByStep_NeedLevel = 30				#步步高升等级限制
#===============================================================================
# 勇闯龙窟
#===============================================================================
DragonHoleNeedLevel = 35				#勇闯龙窟等级限制
#===============================================================================
# 切火鸡
#===============================================================================
CutTurkeyLv = 30						#切火鸡等级限制
CutTurkeyNMaxCnt = 10					#切普通火鸡最大次数
CutTurkeyAMaxCnt = 10					#切高级火鸡最大次数
CutTurkeyCountdown = 10					#切火鸡倒计时
CutTurkeyRMB = 40						#切高级火鸡消耗神石
#===============================================================================
# 狂欢感恩节-充值送豪礼
#===============================================================================
TG_RechargeReward_RecordNum = 10		#大奖记录条数
TG_RechargeReward_NeedLevel = 30		#等级限制
TG_RechargeReward_CDK_DayMax = 5		#单服每日CDK奖励上限
TG_RechargeReward_NeedInviteTimes = 2	#奖励次数所需邀请好友次数 

#===============================================================================
# 狂欢感恩节-在线赢大礼
#===============================================================================
TG_OnlineReward_NeedLevel = 30		#等级限制
#===============================================================================
# 首充大礼包
#===============================================================================
FirstPayMountId = 15				#首充大礼包赠送坐骑ID

#===============================================================================
# 公告渠道区分
#===============================================================================
PLATFORM_MSG_LanZuan = 2		#蓝钻
PLATFORM_MSG_HuangZuan = 3		#黄钻

#===============================================================================
# 技能升级、进化
#===============================================================================
SKILLOPERATE_CannotChangePosSkillID = [1, 11, 18, 20]	#第一个技能ID（不可操作其位置）
SKILLOPERATE_DragonveinSkill = 1					#龙脉技能type
SKILLOPERATE_SkillIdLink = {1:18, 18:1, 2:19, 19:2, 11:20, 20:11, 12:21, 21:12}	#普通技能和进化后的技能关联

#===============================================================================
# 祖玛
#===============================================================================
ZUMA_FREE_CNT = 2		#祖玛免费次数
ZUMA_BUY_LIMIT_CNT = 3	#祖玛购买次数限制
ZUMA_BUY_CNT_RMB = 20	#祖玛购买次数神石
ZUMA_BUY_CNT_RMB_NA = 50#祖玛购买次数神石(北美)
#===============================================================================
# 双十二活动
#===============================================================================
DoubleTwelve_NeedLevel = 30				#等级限制
FeastWheel_PreciousRecordMaxSize = 10	#盛宴摩天轮珍贵奖励记录最多条数	
LuckyCoinLotter_AwardNum = 12			#好运币专场 一轮抽奖次数
LuckyCoinLotter_AllLotteryRecord = 8190	#好运币满盘都被抽了的记录值 pow(2,LuckyCoinLotter_AwardNum+1) - 2 (1+2+3...+12)
LuckyCoinLotter_LuckyCoinCoding = 27474	#好运币coding

#===============================================================================
# 7日目标
#===============================================================================
KaifuTargetNeedLevel = 1

#===============================================================================
# 蓝钻豪华六重礼
#===============================================================================
QQLZLuxuryGift_NeedLevel = 30

#===============================================================================
# 圣诞许愿树
#===============================================================================
ChristmasWishTree_NeedLevel = 30		#等级限制
ChristmasWishTree_ShelfGoodsCnt = 6		#货架商品个数
ChristmasWishTree_SockCoding = 27567	#圣诞袜子的coding

#===============================================================================
# 圣诞羽翼转转乐
#===============================================================================
ChristmasWingLottery_NeedLevel = 65		#等级限制
ChristmasWingLottery_RecordMaxNum = 10	#大奖记录条数上限
ChristmasWingLottery_BatchLotteryNum = 10	#批量抽奖次数
ChristmasWingLottery_LotteryCost = 88	#神石抽奖消耗
ChristmasWingLottery_LotteryCost_NA = 195	#北美神石抽奖消耗
ChristmasWingLottery_DiscountCost = 10	#折扣抽奖神石消耗
ChristmasWingLottery_DiscountCost_NA = 95#北美折扣抽奖神石消耗

#===============================================================================
# 圣诞抽奖次数源头定义
#===============================================================================
Source_List = [1, 2, 4, 8]		#所有源头
Source_DemonDefense = 1		#魔兽入侵
Source_DukeOnDuty = 2		#城主轮值
Source_GloryWar = 4			#荣耀之战
Source_TeamTower = 8		#组队爬塔

#===============================================================================
# 圣诞坐骑转转乐
#===============================================================================
ChristmasMountLottery_NeedLevel = 30	#等级限制
ChristmasMountLottery_RecordMaxNum = 10	#大奖记录条数上限
ChristmasMountLottery_BatchLotteryNum = 10	#批量抽奖次数
ChristmasMountLottery_LotteryCost = 88	#神石抽奖消耗
ChristmasMountLottery_LotteryCost_NA = 195	#北美神石抽奖消耗
ChristmasMountLottery_DiscountCost = 10	#折扣抽奖神石消耗
ChristmasMountLottery_DiscountCost_NA = 95#北美折扣抽奖神石消耗
#===============================================================================
# 圣诞嘉年华
#===============================================================================
ChristmasHaoExpLimit = 10000			#本地排行榜上榜需求最少积分
ChristmasShopLvLimit = 30				#圣诞狂欢兑不停等级限制

#===============================================================================
# 圣诞时装秀
#===============================================================================
ChristmasFashionShow_NeedLevel = 45	#等级限制

#===============================================================================
# 装备洗练
#===============================================================================
EQUIPMENT_MIN_ROLE_LEVEL = 100		#装备洗练的玩家最低等级
EQUIPMENT_MIN_STRENG_LEVEL = 100	#装备洗练的装备强化最低等级
EQUIPMENT_WASH_CODING = 27587		#装备洗练石coding
EQUIOMENT_WASH_LOCK_CODING = 27588	#装备锁定coding
EQUIPMENT_WASH_UNBINDRMB = 10		#每次消耗的神石
EQUIPMENT_WASH_UNBINDRMB_NA = 45	#每次消耗的神石(北美)
EQUIPMENT_INC_WASHNUM_RMB = 10		#用神石额加的洗练度
EQUIPMENT_INC_WASHNUM = 1			#基础增加的洗练度
EQUIPMENT_DEC_JICHENG_COST = 10		#装备继承消耗的神石
EQUIPMENT_DEC_JICHENG_COST_NA = 45	#装备继承消耗的神石(北美)
EQUIPMENT_LOCK_COST = 10			#每次锁消耗的神石
EQUIPMENT_LOCK_COST_NA = 45			#每次锁消耗的神石(北美)
EQUIPMENT_WASH_STONE = 28587		#装备洗练升星石coding
EQUIPMENT_WASH_STONE_GUOQI = 28604	#过期的装备洗练升星石coding
EQUIPMENT_WASH_CODING_TMP = 28594	#装备洗练石临时道具coding
#===============================================================================
# 北美祭坛文书
#===============================================================================
NA_HEROALTAR_CODING = 27591	#文书coding
NA_HEROALTAR_DISCOUNT = 6	#折扣

#===============================================================================
# 元旦在线奖励
#===============================================================================
HolidayOnlineReward_NeedLevel = 30	#等级限制

#===============================================================================
# 元旦充值奖励
#===============================================================================
HolidayRechargeReward_NeedLevel = 30	#等级限制
HRR_PreciousRecordMaxSize = 10			#珍贵奖励记录最多条数	

#===============================================================================
# 公会任务
#===============================================================================
UNION_TASK_DAY_CNT = 5			#公会任务每日次数
UNION_TASK_DAY_HELP_CNT = 20	#公会任务每日助人次数


#===============================================================================
# 豪华蓝钻转大礼
#===============================================================================
QQLZLuxuryRoll_NeedLevel = 20		#等级限制
QQLZLuxuryRoll_CrystalBaseCnt = 1	#但次抽奖获得的蓝钻水晶数
#===============================================================================
# 新年活动
#===============================================================================
NYEAR_MIN_LEVEL = 30	#参加活动的最低等级
NYEAR_MIN_SCORE = 5000	#新年我最壕上榜最小积分
NYEAR_MAX_REFRESH = 20	#新年折扣汇刷新次数
#===============================================================================
#公会神兽
#===============================================================================
UnionShenShouMaxCallTime = 1			#公会神兽每日最大召唤次数
UnionShenShouMaxChallengeTime = 10		#公会神兽每日最大挑战次数

#===============================================================================
# 勇者试炼场
#===============================================================================
DailyFB_NeedLevel = 30		#等级限制
DailyFB_FightCD = 10		#战斗CD 秒

#===============================================================================
# 黄钻兑好礼
#===============================================================================
QQHZRoll_NeedLevel = 20		#等级限制
QQHZRoll_CrystalBaseCnt = 1	#单次抽奖获得的黄钻水晶数

#===============================================================================
# 女神卡牌
#===============================================================================
GODDESS_CARD_RESET_CNT = 40						#女神卡牌重置次数
GODDESS_CARD_TURN_OVER_ONE_NEED_RMB = 25		#翻牌1次需要RMB
GODDESS_CARD_TURN_OVER_ONE_NEED_RMB_NA = 50		#北美翻牌1次需要RMB
GODDESS_CARD_TURN_OVER_FIVE_NEED_RMB = 100		#翻牌5次需要RMB
GODDESS_CARD_TURN_OVER_FIVE_NEED_RMB_NA = 200	#北美翻牌5次需要RMB
GODDESS_CARD_TURN_OVER_FINAL_NEED_RMB = 100		#终极翻牌需要RMB
GODDESS_CARD_TURN_OVER_FINAL_NEED_RMB_NA = 200	#终极翻牌需要RMB
#===============================================================================
# 称号
#===============================================================================
LevelUpNeedUnbindRMB = 10 #称号培养升级神石
LevelUpNeedUnbindRMB_NA = 25#北美称号培养升级神石
TitleLevelItemCoding = 27669#称号培养石

#===============================================================================
# 龙骑试炼
#===============================================================================
DKC_NeedLevel = 100		#等级限制
DKC_PassRecordNum = 2	#试练记录条数
#===============================================================================
# 超级贵族
#===============================================================================
SUPER_VIP_RMB_POINT = 1		#超级贵族花费神石换算成积分的比例
#===============================================================================
# 运营活动
#===============================================================================
OA_ExchangeShopLvLimit = 30

#===============================================================================
# 跨服商店
#===============================================================================
KuaFuShop_NeedLevel = 60

#===============================================================================
# 春节活动
#===============================================================================
Spring_Festival_NeedLevel = 30	#春节活动需要的等级 
SPRING_MIN_SCORE = 1000	#上榜最低消费
#===============================================================================
# 送人玫瑰
#===============================================================================
RolePresent_NeedLevel = 30

#===============================================================================
# 蓝钻兑好礼
#===============================================================================
QQLZRoll_NeedLevel = 20		#等级限制
QQLZRoll_CrystalBaseCnt = 1	#单次抽奖获得的蓝钻水晶数

#===============================================================================
# 跨服个人竞技场
#===============================================================================
KUAFU_JJC_FREE_CNT = 1						#跨服个人竞技场海选免费次数
KUAFU_JJC_FINALS_FREE_CNT = 10				#跨服个人竞技场决赛免费次数
KUAFU_JJC_RESET_ROUND_KUAFU_MONEY = 100		#跨服个人竞技场重置轮数需要跨服币
KUAFU_JJC_RESET_ROUND_KUAFU_MONEY_NA = 250	#跨服个人竞技场重置轮数需要跨服币(北美)
KUAFU_JJC_FINALS_GUESS_MONEY = 200000		#跨服个人竞技场竞猜金币
KUAFU_JJC_FINALS_GUESS_RMB = 100				#跨服个人竞技场竞猜神石

#===============================================================================
# 开年活动
#===============================================================================
OpenYearGift = 27882		#开年礼包道具
OpenYearNeedLevel = 30		#开年活动等级限制
#===============================================================================
# 元宵节活动
#===============================================================================
LanternFestivalNeedLevel = 30


#===============================================================================
# 魅力币兑换
#===============================================================================
GlamourCoinExchange_NeedLevel = 30

#===============================================================================
# 情侣炫酷时装
#===============================================================================
CouplesFashion_NeedLevel = 30	#等级限制

#===============================================================================
# 魅力派对
#===============================================================================
GlamourParty_NeedLevel = 30	#等级限制

#===============================================================================
# 情人目标
#===============================================================================
CouplesGoal_NeedLevel = 30	#等级限制
QinmiLover_Coding = 37032	#亲密恋人衣服Coding
GoalType_QinmiParty = 1		#亲密派对
GoalType_EngageRing = 2		#订婚戒指
GoalType_ClothesEquip = 3	#亲密恋人衣服穿戴
GoalType_ClothesStar = 4	#亲密恋人衣服星级
GoalType_ClothesStage = 5	#亲密恋人衣服阶级

#===============================================================================
# 公会魔域探秘
#===============================================================================
UNION_EXPLORE_DAY_FREE_CNT = 10				#公会魔域探秘每日免费行动力
UNION_EXPLORE_METER_MAX = 99999				#公会魔域探秘最大探索度
UNION_EXPLORE_PRISONER_CNT_NO_VIP = 1		#公会魔域探秘默认抓俘虏次数

#===============================================================================
# 战神宝箱开启等级
#===============================================================================
GODWAR_CHEST_NEED_LEVEL = 80	#战神宝箱开启等级

#===============================================================================
# 老玩家回流
#===============================================================================
BackToOldNeedKaiFuDay = 15		#回流至老服需要的开服时间
BackToOldNeedLevel = 100			#回流至老服需要的角色等级
BackToOldNeedUnloginDays = 10	#回流至老服需要的未登录的时间
#===============================================================================
# 神王宝库
#===============================================================================
ShenWangBaoKuNeedLevel = 45		#神王宝库需要角色等级
ShenWangBaoKuLuckrolelist_lenth = 20		#玩家中奖信息长度
ShenWangBaoKuLuckPoolInit = 5000			#奖池初始化数量
ShenWangBaoKuPointPerTime = 1				#每次抽奖增加的积分 
ShenWangBaoKuIncPoolPerTime = 8				#每次抽奖奖池增加神石数
ShenWangBaoKuPerTimePrice = 88				#每次抽奖的价格
ShenWangBaoKuPerTimePrice_NA = 225			#每次抽奖的价格(北美)
ShenWangBaoKuTenTimePrice = 800				#十次抽奖的价格
ShenWangBaoKuTenTimePrice_NA = 1995			#十次抽奖的价格(北美)
ShenWangBaoKuYiZhuCoding = 28216			#神王遗珠物品ID

#===============================================================================
# 清明踏青
#===============================================================================
QMO_NeedLevel = 30		#清明踏青等级限制
QMO_PosList = [1, 2, 3, 4, 5, 6, 7, 8, 9]	#清明踏青牌位置列表
QMO_LotteryItemCoding = 28261		#清明踏青幸运钥匙coding
QMO_LotteryPrice = 88				#清明踏青单次翻牌神石价格

#===============================================================================
# 清明幸运大轮盘
#===============================================================================
QMLL_NeedLevel = 30			#清明幸运大轮盘等级限制
QMLL_RecordMaxNum = 30		#中奖纪录条数

#===============================================================================
# 清明全民炼金
#===============================================================================
QingMingLianJinBuff = 50	#清明炼金buff百分比加成
QingMingLianJinBuffLastTime = 7200 #金币buff持续时间
QingMingLianJinItems = [(25600, 10), (27368, 1)]	#清明炼金奖励道具
QingMingLianJinMoney = 300000	#清明炼金奖励金币
QingMingLianJinNeedLevel = 30	#等级限制

#===============================================================================
# 清明七日充值
#===============================================================================
QingMingRechargeNeedLevel = 30 #等级限制

#===============================================================================
# 清明七日消费
#===============================================================================
QingMingConsumeNeedLevel = 30	#等级限制
#===============================================================================
# 清明转转乐
#===============================================================================
QQLZHappyDraw_NeedLevel = 20	#需要等级
QQLZHappyDraw_CrystalBaseCnt = 1		#每次增加的水晶

#===============================================================================
# 魔灵大转盘
#===============================================================================
MOLING_LUCKY_DRAW_NEED_RMB = 88		#转一次消耗神石数
MOLING_LUCKY_DRAW_NEED_RMB_NA = 195	#北美转一次消耗神石数
#===============================================================================
# 魔法阵
#===============================================================================
MFZ_NeedLevel = 120				#魔法阵等级限制
MFZ_RefreshCoding = 28280		#魔法阵洗练材料
#===============================================================================
# 黄钻转转乐
#===============================================================================
QQHZ_HAPPY_LEVEL = 20	#黄钻转转乐最低等级
QQHZHappyDraw_CrystalBaseCnt = 1		#每次增加的水晶
#===============================================================================
# 五一活动
#===============================================================================
FIVE_ONE_NEED_LEVEL = 30	#五一活动需要的最低等级
FIVE_ONE_ATTICK_NEED_RMB = 88	#五一活动勇者斗恶龙需要的神石数
FIVE_ONE_ATTICK_NEED_RMB_NA = 225#五一活动勇者斗恶龙需要的神石数(北美)
FIVE_ONE_DRAGON_HORN_ID = 28299	#五一活动勇者斗恶龙需要的龙角ID
FIVE_ONE_DRAGON_BALL_ID = 28300	#五一活动勇者斗恶龙需要的龙珠ID

#===============================================================================
# 新在线奖励
#===============================================================================
ZaiXianJiangLi_NeedLevel = 30		#新在线奖励_等级限制
ZaiXianJiangLi_MaxMins = 30			#新在线奖励_可抽奖在线分钟数
ZaiXianJiangLi_MaxLotteryTimes = 5	#新在线奖励_每日最多可抽奖次数
ZaiXianJiangLi_MaxRecordNums = 10		#新在线奖励_记录条数

#===============================================================================
# 至尊周卡
#===============================================================================
SuperCardsLvLimit = 100				#至尊周卡等级限制
SuperCardsBuyLimit = 150			#至尊周卡购买需要当日累计充值
SuperCardsBuyRMB = 300				#至尊周卡购买价格
SkipFightType = 42					#跳过播放战斗类型

#===============================================================================
# 腾讯页游节预热活动等级限制
#===============================================================================
YeYouJieWarmUpNeedLevel = 30

#===============================================================================
# 页游节狂欢暴击
#===============================================================================
YeYouJieRechage_NeedLevel = 30		#腾讯页游节充值返利等级限制
ONEDAY_SEC = 86400					#一整天的秒数


#===============================================================================
# 空间十周年
#===============================================================================
KJD_RegressReward_DefaultKey = 1		#回归奖励默认key
KJD_FirstRechargeReward_DefaultKey = 1	#首冲拿大礼奖励默认key
KJD_LoginReward_DefaultKey = 1			#登录领好礼奖励默认key
KJD_NeedLevel = 30						#空间十周年活动等级限制


#===============================================================================
# 王者公测
#===============================================================================
WangZheGongCe_NeedLevel = 30			#在线有豪礼_等级限制
ZaiXianLuxuryReward_RewardCnt = 3		#在线有豪礼_单条奖励个数
ZheKouHui_RefreshCnt = 6				#公测折扣汇展示商品数

WZCR_Task_QAndATargetCnt = 10			#奖励狂翻倍 答题正确次数条件

WZCR_Task_ClashOfTitans = 1				#诸神之战
WZCR_Task_HunLuanSpace = 2				#混乱时空
WZCR_Task_MarryParty = 3				#派对
WZCR_Task_QAndA = 4						#答题
WZCR_Task_DemonDefense = 5				#魔兽入侵
WZCR_Task_DukeOnDuty = 6				#城主轮值
WZCR_Task_KuaFuJT = 7					#跨服组队竞技

WZRR_LotteryItemCoding = 28442			#充值返利抽奖所需道具
WZRR_LotteryCnt = 12					#充值返利单轮抽取次数

WZR_RechargeFactor = 1					#王者公测积分充值系数
WZR_ConsumeFactor = 0					#王者公测积分消费系数

#===============================================================================
# 最新活动活跃度
#===============================================================================
LA_TT = 1								#活跃度 -- 组队爬塔
LA_UnionTask = 2						#活跃度 -- 公会任务
LA_UnionExplore = 3						#活跃度 -- 魔域探秘
LA_DayTask = 4							#活跃度 -- 日常任务
LA_DragonTreasure = 5					#活跃度 -- 巨龙宝藏
LA_DailyFB = 6							#活跃度 -- 勇者试练场
LA_Purgatory = 7						#活跃度 -- 心魔炼狱
LA_Zuma = 8								#活跃度 -- 天天消龙珠
LA_SlaveOperate = 9						#活跃度 -- 勇斗领主
LA_EquipmentForing = 10					#活跃度 -- 装备强化
LA_HallowsForing = 11					#活跃度 -- 圣器洗练
LA_JJC = 12								#活跃度 -- 英雄竞技
LA_StarGirlUp = 13						#活跃度 -- 星灵升级
LA_DragonVeinUp = 14					#活跃度 -- 龙脉升级
LA_Gold = 15							#活跃度 -- 炼金
LA_FB = 16								#活跃度 -- 通关副本
LA_CouplesFB = 17						#活跃度 -- 情缘副本
LA_UnionFB = 18							#活跃度 -- 公会副本
LA_AsteroidFields = 19					#活跃度 -- 魔域星宫
LA_HeroTemple = 20						#活跃度 -- 英灵神殿
LA_LuckTurntable = 21					#活跃度 -- 幸运转转乐
LA_WishPool = 22						#活跃度 -- 许愿次
LA_TarotAd = 23							#活跃度 -- 高级占卜
LA_RuneWheel = 24						#活跃度 -- 符文宝轮
LA_HeroAltar = 25						#活跃度 -- 英雄祭坛
LA_Charge = 26							#活跃度 -- 充值
LA_Consume = 27							#活跃度 -- 消费

#===============================================================================
# 繁体版老玩家回流
#===============================================================================
FTOldRoleBackLoginMoney = 10000000					#【繁体版】老玩家回流登录奖励金币
FTOldRoleBackLoginbindRMB = 500						#【繁体版】老玩家回流登录奖励魔晶
FTOldRoleBackLoginUnbindRMB = 100					#【繁体版】老玩家回流登录奖励神石
FTOldRoleBackLoginItems = [(27492, 1), (25644, 50), (27400, 10), (27580, 10)]	#【繁体版】老玩家回流登录奖励 道具

#===============================================================================
# 欢庆端午节
#===============================================================================
DuanWuJieNeedLevel = 30					#等级限制
DuanWuJieNormalZongziCoding = 28436		#普通粽子
DuanWuJieGoldZongziCoding = 28434		#黄金粽子
DuanWuJieNormalPrice = 80000			#开普通粽子需要金币
DuanWuJieGoldPrice = 88					#开黄金粽子需要神石

#===============================================================================
# 诸神之战
#===============================================================================
ClashOfTitansAddScorePerMinute = 50		#每分钟系统发放积分
ClashOfTitansMaxRebornCnt = 10			#最大复活次数
ClashOfTitansSceneID = 564				#诸神之战场景ID
ClashOfTitansNPCType = 19036			#诸神之战英魂NPC类型
ClashOfTitansFightType = 170			#诸神之战战斗类型
ClashOfTitansNeedLevel = 32				#诸神之战等级限制
ClashOfTitansProtectSeconds = 20		#诸神之战复活保护时间
ClashOfTitansFightCDSeconds = 20		#诸神之战战斗冷却时间
ClashOfTitansFightTimeOutSeconds = 120	#诸神之战战斗客户端回调超时时间
ClashOfTitansFightScoreBase = 30		#诸神之战战斗积分基数
ClashOfTitansFightScoreCoe = 2			#诸神之战战斗积分连杀系数

#===============================================================================
# 蓝钻宝箱
#===============================================================================
QQLZBX_TianMa_ID = 27039				#蓝钻宝箱天马流星ID
QQLZBX_TianMa_Mount_ID = 13				#蓝钻宝箱天马流星对应坐骑ID

#===============================================================================
# 激情活动
#===============================================================================
WorldKaiFuDay_7 = 7		#激情活动开启要求开服天数
PassionGift_TodayReward = [28531, 1]		#激情有礼每日任务完成奖励
PassionGift_NeedLevel = 30				#激情有礼等级限制
PassionGift_TargetScore = 100			#激情有礼任务达成目标活跃度积分	

PassionMultiReward_NeedLevel = 30	#激情奖励狂翻倍等级限制

PMR_Task_QAndATargetCnt = 10			#奖励狂翻倍 答题正确次数条件

PassionMulti_Task_ClashOfTitans = 1				#诸神之战
PassionMulti_Task_HunLuanSpace = 2				#混乱时空
PassionMulti_Task_MarryParty = 3				#派对
PassionMulti_Task_QAndA = 4						#答题
PassionMulti_Task_DemonDefense = 5				#魔兽入侵
PassionMulti_Task_DukeOnDuty = 6				#城主轮值
PassionMulti_Task_KuaFuJT = 7					#跨服组队竞技
PassionMulti_Task_ShenShuMiJing = 8				#神树秘境
PassionMulti_Task_MDragonCome = 9				#魔龙降临
PassionMulti_Task_NewQandA = 10					#新答题活动


PassionMarket_NeedLevel = 30				#激情卖场_等级限制
PassionMarket_RefreshCnt = 6				#激情卖场货架商品数

PassionDiscount_NeedLevel = 30			#特惠商品_等级限制

PassionMinLevel = 30					#激情活动最小等级

PassionTurntableNeedLevel = 30			#激情转盘等级限制
PassionTurntableRefreshPrice = 100		#激情转盘刷新价格
PassionOnlineGiftNeedLevel = 30			#激情在线有礼等级限制

PassionLoginGiftNeedLevel = 30			#激情登录有礼等级限制
PassionXiaoFeiMaiDanNeedLevel = 30		#激情活动你消费我买单


PassionTaoGuanOnePrice = 88				#激情欢乐砸陶罐一次价格
PassionTaoGuanTenPrice = 800			#激情欢乐砸陶罐十次价格
#===============================================================================
# 神秘宝箱
#===============================================================================
SMBX_ID = 28527							#神秘宝箱ID
SMBX_Level = 60

#===============================================================================
# 阵灵系统
#===============================================================================
StationSoul_NeedLevel = 100				#阵灵系统等级限制


#===============================================================================
# 新龙骑试炼
#===============================================================================
DKCNew_needLevel = 100		#新龙骑试炼_等级限制
DKCNew_NeedRMB_1 = 0		#第1次开启宝箱的神石消耗
DKCNew_NeedRMB_2 = 20		#第2次开启宝箱的神石消耗
DKCNew_NeedRMB_3 = 50		#第3次开启宝箱的神石消耗
DKCNew_NeedRMB_4 = 100		#第4次开启宝箱的神石消耗
def GetRMBByCnt(openCnt):
	needRMB = 0
	if openCnt == 1:
		needRMB = DKCNew_NeedRMB_1
	elif openCnt == 2:
		needRMB = DKCNew_NeedRMB_2
	elif openCnt == 3:
		needRMB = DKCNew_NeedRMB_3
	elif openCnt == 4:
		needRMB = DKCNew_NeedRMB_4
	else:
		needRMB = DKCNew_NeedRMB_4
	
	return needRMB

def GetTotalRMBByCnt(toBeOpenCnt):
	needRMB = DKCNew_NeedRMB_4
	if toBeOpenCnt == 1:
		needRMB = DKCNew_NeedRMB_4
	elif toBeOpenCnt == 2:
		needRMB = DKCNew_NeedRMB_3 + DKCNew_NeedRMB_4
	elif toBeOpenCnt == 3:
		needRMB = DKCNew_NeedRMB_2 + DKCNew_NeedRMB_3 + DKCNew_NeedRMB_4
	elif toBeOpenCnt == 4:
		needRMB = DKCNew_NeedRMB_1 + DKCNew_NeedRMB_2 + DKCNew_NeedRMB_3 + DKCNew_NeedRMB_4
	else:
		pass
	
	return needRMB


KDC_OneKeyFree_NeedVIP = 5				#新龙骑试炼_一键免费收益VIP限制
KDC_OneKeyAll_NeedVIP = 8				#新龙骑试炼_一键全部收益VIP限制

DKC_RewardPos_Set = set([1, 2, 3, 4])		#新龙骑试炼_奖励位置集合

#===============================================================================
# 神秘宝箱
#===============================================================================
MysteryBox_NeedRMB_1 = 0		#第1次开启宝箱的神石消耗
MysteryBox_NeedRMB_2 = 40		#第2次开启宝箱的神石消耗
MysteryBox_NeedRMB_3 = 80		#第3次开启宝箱的神石消耗
MysteryBox_NeedRMB_4 = 100		#第4次开启宝箱的神石消耗
def GetBoxRMBByCnt(openCnt):
	needRMB = 0
	if openCnt == 1:
		needRMB = MysteryBox_NeedRMB_1
	elif openCnt == 2:
		needRMB = MysteryBox_NeedRMB_2
	elif openCnt == 3:
		needRMB = MysteryBox_NeedRMB_3
	elif openCnt == 4:
		needRMB = MysteryBox_NeedRMB_4
	else:
		needRMB = MysteryBox_NeedRMB_4
	
	return needRMB
#===============================================================================
# 全民转转乐
#===============================================================================
TurnTableMinLevel = 40					#最小等级
TurnTableSinglePrice = 20				#单次价格
TurnTableSinglePrice_NA = 50			#北美单次价格
TurnTableIntoPool = 10					#每次转盘进入奖池神石数
TurnTableInitPoolValue = 100000			#全名转转乐初始奖池
TurnTableJumpGrade = 15000				#全民转转乐多次抽奖不中奖池升级

#==========================================
#神秘宝箱开通版本号，每次修改奖品配置表请将下面的版本号加1
#==========================================
SMBX_Version = 5						#神秘宝箱版本号
SMBX_Version_NA = 1						#神秘宝箱版本号（北美）

#==========================================
#淬炼石Coding
#==========================================
CuiLianShi_Coding = 28680				#淬炼石Coding
CuiLian_Level = 40						#淬炼要求主角等级


#==========================================
#抢红包
#==========================================
QiangHongBao_NeedLevel = 30				#抢红包等级限制
QiangHongBao_MaxCnt = 20				#抢红包每日最多个数
QiangHongBao_RandomList = [1, 1, 2]		#抢红包超时奖励 1-小红包 2-大红包
QiangHongBao_FIGHT_TYPE = 172			#抢红包战斗类型


#==========================================
#古堡探秘
#==========================================
GuBaoTanMi_NeedLevel = 30 					#古堡探秘等级限制
GuBaoTanMi_FangDaJing = 28707				#古堡探秘放大镜

GuBaoTanMi_YiCiRMB = 20					#古堡探秘一次神石消耗
GuBaoTanMi_YiCiRMB_NA = 50				#北美古堡探秘一次神石消耗
#==========================================
#虚空幻境
#==========================================
CTT_SCENE_ID = 600						#场景ID
CTT_JOIN_LEVEL = 90						#进入虚空幻境需要的等级
CTT_NEED_LEVEL = 160					#虚空幻境创建队伍需要的等级
MAX_PLAYER_IN_SCENE = 3000				#场景最大的人数限制
MAX_CLOSE_TP_CNT = 2750					#当场景人数小于或等于2750时，允许玩家进入
CLICK_TP_CD = 5							#点击传送CD
CTT_RewardTimes = 1						#收益次数
CTT_POINT_DAY_MAX = 1000				#每日获取的最高幻境点

#进入跨服派对随机坐标范围(posx1, posx2, posy1, posy2)
KuafuPosRandomRange = (
						(3557,3908, 441,727),
						(2995,3374, 903,992),
						(1603,2654, 1052,1824),
						(554,897, 565,795)
						)
#===============================================================================
# 鲜花系统
#===============================================================================
FlowerLvLimit = 30						#送花限制最小等级
FlowerWorshipCoe = 5000					#膜拜金币系数
FlowerWorshipMaxMoney = 600000			#跨服魅力榜膜拜最大金币值

#===============================================================================
# 中秋活动2015
#===============================================================================
ZhongQiuLianJin_Buff = 50				#中秋全民炼金_buff百分比加成
ZhongQiuLianJinBuff_LastTime = 7200 	#中秋全民炼金_buff持续时间
ZhongQiuLianJin_NeedLevel = 30			#中秋全民炼金_等级限制

HuoYueDaLi_RewardMins_List = [120, 240]		#中秋活跃大礼有奖在线分钟数
HuoYueDaLi_RewardDailyDo_List = [100, 140]		#中秋活跃大礼有奖的每日必做积分
HuoYueDaLi_NeedLevel = 30						#中秋活跃大礼_等级限制
HuoYueDaLi_MaxStep = 36							#中秋活跃大礼_最大步数

ZhongQiuShouChong_NeedLevel = 30		#中秋首冲等级限制
ZhongQiuShouChong_MinRMB = 100			#中秋首冲最低神石

ZhongQiuShangYue_NeedLevel = 30			#中秋赏月等极限制
ZhongQiuShangYue_LotteryCoding = 28745	#中秋赏月道具coding
ZhongQiuShangYue_LotteryRMB = 88		#中秋赏月单次神石消耗
#===============================================================================
# 转生
#===============================================================================
RoleMaxLevel = 179
#===============================================================================
# 神器淬炼
#===============================================================================
ArtifactCuiLian_Level = 120		#神器开启淬炼等级
ArtifactCuilian = 28833			#神器淬炼石Coding
ArtifactCuilianHalo = 28834		#强化神器淬炼光环所需道具Coding

#===============================================================================
# 跨服争霸赛
#===============================================================================
JTCheersMaxCnt = 300			#跨服争霸赛每日最大喝彩次数
JTCheersMinLevel = 30			#跨服争霸赛喝彩需要最小等级
JTCheersCheersRMB = 10			#跨服争霸赛喝彩一次需要神石
JTCheersResponsesRMB = 10		#跨服争霸赛回应一次需要神石
JTCheersTitleNeedCCnt = 1500	#跨服争霸赛获得称号需要喝彩次数
JTCheersTitleNeedPCnt = 300		#跨服争霸赛获得称号需要回应次数
JTCheersTitle = 79				#跨服争霸赛称号id

#===============================================================================
# 宝石锻造
#===============================================================================
GemFoege_NeedLevel = 120		#宝石锻造_等级限制
#===============================================================================
# 迷失之境
#===============================================================================
LostSceneNeedLevel = 90					#迷失之境需要等级
LostSceneNpcCnt = 30					#迷失之境npc个数
LostSceneSceneID = 700					#迷失之境场景id
LostSceneJoinPos = (2797, 1721)			#迷失之境玩家进入位置(x, y)
LostSceneScore_15sReward = 10			#迷失之境15s奖励
LostSceneScore_exReward = 130			#迷失之境额外奖励
LostSceneScore_findReward = 120			#迷失之境追捕奖励
LostSceneFindRangeX = 700				#迷失之境侦测x范围
LostSceneFindRangeY = 350				#迷失之境侦测y范围
LostSceneArrestRangeX = 100				#迷失之境抓捕x范围
LostSceneArrestRangeY = 100				#迷失之境抓捕y范围

#===============================================================================
# 双十一2015
#===============================================================================
DELoginReward_NeedLevel = 30			#登陆有礼_等级限制
DETopic_NeedLevel = 30					#专题转盘_等级限制
DEQiangHongBao_NeedLevel = 30			#抢红包_等级限制
DEGroupBuy_NeedLevel = 30				#团购送神石_等级限制
DETopic_PreciousRecordMaxSize = 10		#专题转盘_珍贵奖励记录最多条数	
DEQiangHongBao_RoleMaxCnt = 3			#抢红包玩家背包最多红包个数
DEQiangHongBaoCD = 10					#双十一抢红包CD
ElevenMallReward_NeedLevel = 30			#双十一商城满返_等级限制
ElevenRecharge_NeedLevel = 30			#双十一充值大放送_等级限制

#================================================================================
#宝石分解的最低等级
#================================================================================
GemResolve_NeedLevel = 120
#===============================================================================
# 神数秘境
#===============================================================================
ShenshumijingLevel = 30										#参与等级
ShenshumijingSceneID = 722									#场景id
ShenshumijingMaxRMBIncLv = 10								#最大神石增益等级
ShenshumijingCaijiNpcCnt = 10								#采集npc个数
ShenshumijingGuardScore = 1									#剩余npc每个扣神树经验值
ShenshumijingShenshuNpcType = (22005, 650, 433, 1, 1)		#神树密境神树npc(npcType, posX, posY, direct, isBroad)
ShenshumijingTeamFightType = 175							#神树密境组队战斗类型
ShenshumijingFightType = 176								#神树密境单人战斗类型
ShenshumijingJoinRegion = [952, 630, 1404, 1011]			#[左上x, 左上y, 右下x, 右下y]
ShenshumijingIncExpTime = 15								#加经验时间间隔
ShenshumijingCaijiTime = 180								#刷采集怪时间间隔
ShenhumijingCaijiEndTime = 900								#采集阶段持续时间
ShenshumijingSyncPanelTime = 15								#同步守卫阶段面板时间
ShenshumijingGuardBeforeTipsTime = 240						#守卫出现前一分钟提示
ShenshumijingNextGuardTime = 180							#下一波守卫出现时间
ShenshumijingGuardEndTime = 900								#守卫阶段持续时间
ShenshumijingSucItems = [(29034, 1)]						#神树密境守卫成功后道具奖励
ShenshumijingMaxGuardWave = 5								#神数秘境最大守卫波数
#===============================================================================
# 点石成金
#===============================================================================
Max_Free_Times = 5	#点石成金免费次数
#===============================================================================
#首冲神石数
#===============================================================================
ShouChongNumbers = 200


#===============================================================================
# 天降横财
#===============================================================================
TJHC_BaseN_Range = (10000, 60000)			#天降横财_基数初始随机范围
TJHC_BaseN_Factor = 100000					#天降横财_基数的倍数因子
TJHC_NeedLevel = 30							#天降横财_等级限制
TJHC_UniqueCode_Price = 100					#天降横财_兑奖券需要消费充值神石数
TJHC_NOMAL_REWARDID = 999					#天降横财_普通奖励ID
TJHC_PreciousRecordCnt = 100				#天降横财_中奖记录条数
TJHC_NeedKaiFuDay = 0						#天降横财_开服天数限制
PassionRechargeRank_NeedKaiFuDay = 0		#充值排行_开服天数限制
TJHC_RoleUCode_RoundMaxCnt = 2000			#天降横财_玩家最多兑奖码数据
TJHC_ServerUCode_MaxCnt = 5000				#天降横财_本服最多兑奖码数据
TJHC_RoleUCode_TotalMaxCnt = 30000			#天降横财_玩家总共兑奖码限制
PreciousStore_NeedKaiFuDay = 0				#珍宝商店_开服天数限制
#===============================================================================
# 魔龙降临
#===============================================================================
MD_NEED_LEVEL = 30							#魔龙降临进入最低等级
#===============================================================================
# 点金大放送
#===============================================================================
TouchGoldRewardNeedLv = 120					#点金大放送需要等级
TouchGoldRewardDiscount = 6					#原石购买折扣
TouchGoldRewardMulti = 2					#积分buff倍数

#===============================================================================
# 捕鱼达人
#===============================================================================
CatchingFish_NeedLevel = 30					#捕鱼达人所需等级
CatchingFish_PoolValue = 100000				#捕鱼达人基础鱼池奖金
CatchingFish_IncValue = 6					#捕鱼达人每次增加的奖金数
CatchingFish_ItemLittleCoding = 29051		#捕鱼小网的coding
CatchingFish_ItemMidCoding = 29052			#捕鱼中网的coding
CatchingFish_ItemLargCoding = 29053			#捕鱼大网的coding

#===============================================================================
# 充值积分消费积分道具coding
#===============================================================================
PointItemRecharge = 29059
PointItemConsume = 29057

#===============================================================================
# 卡牌图鉴
#===============================================================================
CAMaxPackageSize = 128							#卡牌背包最大格子数
CardAtlasLevel = 38								#卡牌图鉴开放等级
#===============================================================================
# 元素精炼
#===============================================================================
ElementalEssenceMinLevel = 130					#元素精炼最低等级
ElementalEssenceTimes = 10						#元素精炼精炼次数

#===============================================================================
# 元素之灵
#===============================================================================
ElementSpiritCreamBaseExp = 10					#元素精华单次经验值 
ElementSpiritNeedLevel = 130					#元素之灵等级限制
ElementSpirit_ChangeSkillTypeRMB = 100			#元素之灵_切换技能类型神石消耗
#===============================================================================
# 元旦活动
#===============================================================================
NewYearDayMinLevel = 30								#新年活动最低等级
NewYearDay_Task_DemonDefense = 1					#魔兽入侵
NewYearDay_Task_MDragonCome = 2						#魔龙降临
NewYearDay_Task_DukeOnDuty = 3						#城主轮值
NewYearDay_Task_GloryWar = 4						#荣誉之战
NewYearDay_Task_ShenShuMiJing = 5					#神树秘境
NewYearDay_Task_WildBoss = 6						#野外夺宝
NewYearDay_Task_HunluanSpace = 7						#混乱时空
NewYearDay_Task_ClashOfTitans = 8						#诸神之战

SuperTurnTableOnce = 20								#超值转盘抽奖1次消耗神石
SuperTurnTableTen = 200 							#超值转盘抽奖10次消耗神石



#===============================================================================
# 元素印记
#===============================================================================
ElementBrand_MaxPackageSize = 120					#元素印记背包空间上限
ElementBrand_NeedLevel = 130						#元素印记等级限制
ElementBrand_WashStoneCoding = 29425						#印记洗练石
ElementBrand_WashLockCoding = 29426						#印记洗练锁
ElementBrand_WashLockRMB = 10						#印记洗练锁神石价格
ElementBrand_WashStoneRMB = 10						#印记洗练石神石价格

#===============================================================================
# 宝石2048
#===============================================================================
Game2048_FREE_CNT = 3		#2048免费次数
Game2048RoleLevel = 50


#===============================================================================
#圣印系统
#===============================================================================
SealMinLevel = 130			#圣印系统最低等级限制

#===============================================================================
# 跨服战场
#===============================================================================
KFZC_LEVEL = 130											#跨服战场等级限制
KFZC_REGIONLEVEL_LIST = [130, 150, 170]						#跨服战场区域等级
KFZC_ROLE_CNT = 60											#跨服战场每个战场人数
KFZC_ROLECNTEX = 30											#跨服战场剩余分配
KFZC_FUHUO_TIME = 40										#跨服战场复活时间
KFZC_SMALL_JUDIAN_NPC_1 = [22011, 4767, 794, 0, 1]			#跨服战场小据点npc类型
KFZC_SMALL_JUDIAN_NPC_2 = [22013, 4816, 3333, 0, 1]			#跨服战场小据点npc类型
KFZC_BIG_JUDIAN_NPC = [22012, 4720, 2020, 0, 1]				#跨服战场大据点npc类型
KFZC_SAFE_PLACE_1 = [(8282, 8752), (1773, 1973)]				#跨服战场出生点1
KFZC_SAFE_PLACE_2 = [(745, 1216), (1773, 1983)]				#跨服战场出生点2
KFZC_SCENE_CNT = 20											#跨服战场场景数
KFZC_SCENE_DICT = {1:range(1064, 1084), 2:range(1084, 1104), 3:range(1104, 1124)}
KFZC_ALL_SCENE = range(1064, 1124)							#所有场景id
KFZC_BELONG_SEC = 30										#跨服战场归属倒计时时间
KFZC_CHECK_SEC = 600										#跨服战场检查占据时间
KFZC_SYNC_SEC = 10											#跨服战场同步时间
KFZC_VOTES_SEC = 20											#跨服战场投票时间
KFZC_BIG_GUARD_CNT = 6										#跨服战场大据点守卫个数
KFZC_SMALL_GUARD_CNT = 5									#跨服战场小据点守卫个数
KFZC_JUMP_SCENE = 1124										#跨服战场跳转场景
KFZC_JUMP_POS = [(2884,3480,555,854),
				(2325,2614,1072,1375),
				(1423,1501,1397,1740),
				(785,1487,1711,1995),
				(2037,2529,1683,1900),
				(1001, 1201, 1376, 1505)]						#跨服战场随机点
KFZC_FIGHT_ATTACK_CD = 10									#跨服战场攻击方点击cd
KFZC_FIGHT_DEFENSE_CD = 20									#跨服战场防守方点击cd
KFZC_FIGHT_BOSS_CD = 10										#跨服战场boss点击cd
KFZC_FIGHT_GUARD_CD = 15									#跨服战场守卫点击cd
KFZC_FIGHT_TYPE = 180										#跨服战场战斗类型
KFZC_MIN_SCORE = 100										#跨服战场获得奖励最低积分
#===============================================================================
# 混沌神域
#===============================================================================
ChaosDivinityLevel = 130
ChaosDivinitySubRMB = 200
#===============================================================================
# QQ蓝钻特权
#===============================================================================
QQLZDailyFBBuff = 1000	#QQ蓝钻特权，勇者试炼场获得经验加成  万分比
QQLZSlaveBuff = 3		#QQ蓝钻特权，勇斗领主每日互动增加次数

#===============================================================================
# 春节大回馈
#===============================================================================
FestivalRebate_NeedLevel = 30
FestivalRebate_MaxRebate = 20000
SpringHongBaoLevel = 30
#===============================================================================
# 连连看
#===============================================================================
LianLianKan_RefreshCost = 20	#刷新花费
LianLianKan_BuyMaxTimes = 20	#可购买的最大次数


#===============================================================================
# 秘密花园
#===============================================================================
SecretGarden_NeedLevel = 30				#秘密花园等级限制
SecretGarden_LotteryRMB_1 = 20			#秘密花园单次抽奖神石

#===============================================================================
# 幸运扭蛋--时装扭蛋
#===============================================================================
GashaponFashionLevel = 85			#时装扭蛋限制玩家等级
CommonGashaponCoast = 48			#初级扭蛋消耗魔晶数量
GoodGashaponRMB = 48				#高级扭蛋消耗充值神石数
SuperGashaponItem = 29443			#幸运币，超级扭蛋
GashaponMaxTime = 10				#每日初级扭蛋最大次数
#===============================================================================
# 幸运扭蛋--坐骑扭蛋
#===============================================================================
MountGashaponLevel = 40				#坐骑扭蛋限制玩家等级
CommonMountGashaponCoast = 48		#初级坐骑扭蛋消耗魔晶数量
GoodMountGashaponRMB = 48			#高级坐骑扭蛋消耗充值神石数
SuperMountGashaponRMB = 188			#超级坐骑扭蛋消耗充值神石数
MountGashaponMaxTime = 10			#每日初级坐骑扭蛋最大次数
MasterChipCoding = 29459			#万能碎片coding
MasterChipCnt = 1					#万能碎片Cnt

#===============================================================================
# 蓝钻回馈大礼
#===============================================================================
QQLZFeedBack_NeedLevel = 20 			#蓝钻回馈大礼领取等级

#===============================================================================
# 充值送代币
#===============================================================================
DaiBiRoleLevel = 30				#充值送代币等级限制
DaiBiRewardMaxTimes = 100		#重复奖励做多领取次数
DaiBiRechargeMoney_1 = 500		#奖励1，达到此充值数量，可领奖一次
DaiBiReward = (29454, 1) 		#奖励 1 coding，奖励cnt
DaiBiRechargeMoney_2 = 1000		#奖励2，充值每达到该数值，可重复领奖
DaiBiReReward = (29452, 1) 		#奖励 2 coding，奖励cnt
DaiBiReRewardRMB = 100			#奖励2 每次奖励附带赠送的系统神石


#===============================================================================
# 收集大作战
#===============================================================================
CF_OnePrice = 10				#单价
CF_SubCoding = 25636			#抽取替代道具
CF_ThreeCollect = [1, 2, 3]		#第一个收集索引
CF_FiveCollect = [1, 2, 3, 4, 5]	#第二个收集索引

#===============================================================================
# 元素之灵-铸灵幻化
#===============================================================================
ElementSoul_NeedLevel = 130						#元素铸灵等级限制
ElementVision_NeedLevel = 130					#元素幻化等级限制
ElementTalentSkill_NeedLevel = 130				#元素天赋技能等级限制
ElementSoul_ZhuLingCoding = 29462				#元素铸灵道具coding


#===============================================================================
# 印记排行榜
#===============================================================================
ElementBrandRank_NeedLevel = 30			#印记排行榜等级限制
#===============================================================================
# YY防沉迷
#===============================================================================
YY_Anti_ThreeHours = 180		#3小时，180分钟
YY_Anti_FiveHours = 300			#5小时，300分钟