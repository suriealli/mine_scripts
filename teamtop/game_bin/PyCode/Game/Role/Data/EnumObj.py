#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumObj")
#===============================================================================
# 角色Python对象枚举模块
#===============================================================================
import cRoleDataMgr
from Common import Coding

# 禁止reload，具体原因在Game.Login中
assert "_HasLoad" not in dir()

L = []
def F(uIdx):
	'''
	设置Python对象数组
	@param uIdx:下标
	'''
	assert uIdx < (Coding.RoleObjFlagRange[1] - Coding.RoleObjFlagRange[0])
	if not L:
		assert uIdx == 0
	else:
		assert uIdx == L[-1] + 1
	L.append(uIdx)
	cRoleDataMgr.SetFlagRule(uIdx)

#===============================================================================
# 数组使用定义
#===============================================================================
En_PackageItems = 0				#背包物品ID集合 Set(PropID)
F(En_PackageItems)

En_RoleEquipments = 1			#角色装备ID集合 Set(EquipmentID)
F(En_RoleEquipments)

En_HeroEquipments = 2			#英雄装备信息(字典) {HeroID --> ID集合 Set(EquipmentID)}
F(En_HeroEquipments)

JJC = 3							#竞技场相关{1: {位置: 领取状态}}
F(JJC)

Union = 4						#公会相关{1 :{公会等级：领取状态},2:{公会商店普通商品购买次数goodId:cnt},3:{公会商店神兽掉落商品购买次数goodId:cnt},4:{公会技能id-->{'level':技能等级,'time':时间戳}}
F(Union)

En_Hero_Data_Dict = 5			#新英雄数据	{1-->[招募英雄ID], 2-->{英雄编号-->上次招募时间戳}, 3:{英雄类型 --> set(招募的英雄ID)}}
F(En_Hero_Data_Dict)

RoleSkill = 6					#已经学会的技能{技能ID-->技能等级}
F(RoleSkill)

RoleFightSkill = 7				#出战技能 { 1 -->[技能ID]}
F(RoleFightSkill)

Create_PF = 8					#创建时的登录来源
F(Create_PF)

VIPData = 9						#VIP数据 {1 --> {vip等级-->礼包状态,}}
F(VIPData)

InviteInfo = 10					#邀请信息{0:邀请者角色ID, 被邀请者角色ID:(被邀请者等级, 被邀请者消耗Q点)}
F(InviteInfo)

QTaskID = 11					#QQ交叉推广信息
F(QTaskID)

Title = 12						#称号{1:{称号索引 --> [失效时间戳, 等级，经验，星级}, 2 : 当前佩戴的称号[]
F(Title)

PersistenceTick = 13			#持久化Tick 持久化TickID --> (回调函数ID, 回调函数参数)
F(PersistenceTick)

Social_Friend = 14				#好友字典 role_id --> 好友信息字典
F(Social_Friend)
Social_Back = 15				#黑名单
F(Social_Back)
Social_Recent = 16				#最近联系人
F(Social_Recent)

InviteFriendObj = 17			#好友邀请和分享数据	{1:[分享状态(每日检测是否需要重置)], 2:set(邀请个数(每日重置)), 3:set(成功邀请个数(不重置)), 4:set(邀请群个数(每日重置))}
F(InviteFriendObj)

Social_GroupDefine = 18			#好友分组定义{分组ID:分组名}
F(Social_GroupDefine)

FB_JoinData = 19				#副本每日次数记录(每日清理){ 副本ID : 次数  }
F(FB_JoinData)

GT_Record = 20					#天地宝库兑换记录{itemCoding:cnt}
F(GT_Record)

FB_Progress = 21				#副本未完成的数据记录{副本ID:{1:回合数,2:正在准备攻击第几个怪物,3:通关星级,4:[随机到的奖励物品列表]}}
F(FB_Progress)

FB_Star = 22					#副本星级数据{副本ID : 星级 }
F(FB_Star)

FB_ZJReward = 23				#副本通关章节领取奖励记录{ 1 : set(通关奖励领取记录), 2 : set(全3星奖励领取记录)}
F(FB_ZJReward)


PurgatoryReward = 24			#心魔炼狱	{心魔炼狱ID --> [击杀怪物波数, 通关回合(未通关为0)]}
F(PurgatoryReward)

Mount = 25						#坐骑信息{1:[mountId,...],2:[FoodID,...],3:{mountId:过期时间}, 4:激活过但过期了的坐骑ID集合, 5:{坐骑ID:坐骑外形品阶}
F(Mount)						#1:坐骑:已解锁的幻化ID,2:已使用的食物ID

Award = 26						#玩法奖励
F(Award)

EvilHold_SaoDangData = 27		#恶魔深渊扫荡数据 { 0 : 恶魔深渊ID, 1:已经完成的扫荡次数, 2:剩余扫荡次数, 3:当前开始的扫荡时间戳 }
F(EvilHold_SaoDangData)
EvilHole_StarBoxReward = 28		#恶魔深渊3星宝箱奖励领取记录{1 --> set()  }
F(EvilHole_StarBoxReward)
EvilHole_Star = 29				#恶魔深渊通关评星数据 { 恶魔深渊索引 : 最高评星1， 2， 3 } 
F(EvilHole_Star)

Dragon_Treasure = 30			#{1：[记录当前的3个场景id],2:[事件id,当前场景ID],3:[已抽取的奖励id],4:[幸运挖宝的场景]}
F(Dragon_Treasure)

Gold_Player_Data = 31			#{1: 是否炼金, 2: {玩家id:[玩家信息],...}}
F(Gold_Player_Data)		

SubTaskDict = 32				#支线任务数据{1:set(等待激活的支线任务), 2 : set(已经激活，等待完成的支线任务) 3: set(已经完成，等待领奖的支线任务)}
F(SubTaskDict)
DayTask = 33					#日常任务数据{-1: 可接任务 index, 0 : 已接任务index, 1 : m1, 2 : m2 , 3 : m3, 4 : m4}
F(DayTask)
TiLiTask = 34					#体力任务数据{-1: 可接任务 index, 0 : 已接任务index, 1 : m1, 2 : m2 , 3 : m3, 4 : m4}
F(TiLiTask)

CardsDict = 35					#月卡返券领取状态{cardID:是否领取(0:未领, 1:领取)} 每日清理
F(CardsDict)

CardsIsVaild = 36				#月卡是否有效{cardID:(1-有效, 0-无效)}
F(CardsIsVaild)

FlowerRecord = 37				#角色送花记录{1--> set(roleids)}
F(FlowerRecord)

En_RoleArtifact = 38			#角色神器ID集合 Set(EquipmentID)
F(En_RoleArtifact)

En_HeroArtifact = 39			#英雄神器信息(字典) {HeroID --> ID集合 Set(EquipmentID)}
F(En_HeroArtifact)

LEGION_REWARD = 40				#{1:set(已领取的七日礼包ID,...),2:set(已领取的登录礼包id,...),3:0(清理的时间)}
F(LEGION_REWARD)

DailyDoDict = 41				#每日必做 {1:{任务索引:完成次数}, 2:set(领取过的奖励索引)}
F(DailyDoDict)

Wing = 42						#翅膀{1:{wingId1:[level, exp], wingId2:[level, exp]}
F(Wing)

TarotCardDict = 43				#塔罗牌占卜命魂数据{packageId --> {cardId -- >cardDatadict 0:type, 1:level, 2:exp, 3:islock｝}
F(TarotCardDict)

Mall_Day_Limit_Dict = 44		#神石商城每日限购数据{tradeId-->cnt}
F(Mall_Day_Limit_Dict)

Mall_Limit_Dict = 45			#神石商城永久限购数据{tradeId-->cnt}
F(Mall_Limit_Dict)

Wonder_Reward_List = 46			#记录精彩活动奖励{1:一次性，2：每日刷新}
F(Wonder_Reward_List)

Wonder_Vip_Reward_Dict = 47		#记录精彩活动VIP团购奖励{奖励ID->领取次数}
F(Wonder_Vip_Reward_Dict)

StarColor_Dict = 48				#记录角色英雄星级对应的最大品阶数据{star-->colorCode}
F(StarColor_Dict)

Pet = 49						#宠物{petId: {1:培养属性{}, 2:技能{}}}
F(Pet)

AppPanelLoginReward = 50 		#QQ应用面板登陆奖励{days:1}
F(AppPanelLoginReward)

ToSkyRecord_List = 51			#冲上云霄奖励记录[[month, day, item_list],]
F(ToSkyRecord_List)

MysterShopRecord = 52			#神秘商店兑换记录 {itemCoding:cnt}
F(MysterShopRecord)

WorldCup = 53					#世界杯竞猜个人数据{1 : set(竞猜的16强ID列表), 2 : 竞猜的冠军ID, 3 : 16强奖励领取Flag, 4 : 冠军竞猜领取奖励Flag, 5 : 淘汰赛{阶段  : {组别 : {竞猜类型 : (队伍ID, 是否已经领奖)}}}
F(WorldCup)						#注意获取的时候请使用函数 GetRoleWorldCupData

AsteroidFields = 54				#魔域星宫挑战个人数据{星域id --> 关卡index }
F(AsteroidFields)

AsteroidFieldsDaily = 55		#魔域星宫挑战个人数据（每日清零）{星域id --> 关卡index }
F(AsteroidFieldsDaily)

Dragon = 56						#神龙
F(Dragon)

En_RoleHallows = 57				#角色圣器 ID集合Set(EquipmentID)
F(En_RoleHallows)

En_HeroHallows = 58				##英雄圣器信息(字典) {HeroID --> ID集合 Set(HallowsID)}
F(En_HeroHallows)

WeiXinTarget = 59				#微信关注达成目标{1:set(已领取的微信关注目标索引)}
F(WeiXinTarget)

MarryObj = 60				#求婚信息	{1:求婚对象ID, 2:求婚对象信息, 3:订婚信息, 4:求婚对象ID列表(按时间顺序排序), 5:婚礼ID, 6:对象的订婚戒指信息(最高等级订婚戒指, 是否铭刻)}
F(MarryObj)

WeddingRingSoulPro = 61		#戒灵属性 {1:{品阶:戒灵属性}, 2:{}}
F(WeddingRingSoulPro)

WeddingRingStarObj = 62		#{1:{}, 2{}, 3:set()}
F(WeddingRingStarObj)

TalentCardDict = 63				#天赋卡
F(TalentCardDict)

TalentUnlockDict = 64			#记录玩家解锁的天赋卡槽
F(TalentUnlockDict)

CouplesFBRewardDict = 65		#情缘副本
F(CouplesFBRewardDict)

GameUnionAiwanContiReward = 66		#游戏联盟爱玩连续登录奖励
F(GameUnionAiwanContiReward)

GameUnionQQGJContiReward = 67		#游戏联盟QQ管家连续登录奖励
F(GameUnionQQGJContiReward)

UniverBuyDict = 68			#全民团购，记录玩家每种商品购买的次数 {index:cnt}
F(UniverBuyDict)

KaifuBossWorship = 69			#开服boss膜拜 {bossId:1}
F(KaifuBossWorship)

KaifuBossSeverAward = 70			#开服全服奖励是否领取过 {bossId:1}
F(KaifuBossSeverAward)

WishPoolExRecord = 71			#许愿池兑换记录
F(WishPoolExRecord)

WishPoolWishRecord = 72			#许愿池许愿次数记录
F(WishPoolWishRecord)

GoldChest = 73				#{阶段->set(已领取的物品index)}，每日清空
F(GoldChest)

GoldChestOpen = 74				#{宝箱id->1开启}，每日清空
F(GoldChestOpen)

OG = 75						#北美版OG任务使用
F(OG)

StrayMerchantDict = 76			#商品id->state(1，购买，0，未购买)
F(StrayMerchantDict)

BraveHeroShop = 77				#勇者徽章商店
F(BraveHeroShop)
BraveHeroScore = 78				#积分兑换记录
F(BraveHeroScore)

HefuBossWorship = 79			#合服boss膜拜 {bossId:1}
F(HefuBossWorship)

HefuBossSeverAward = 80			#合服全服奖励是否领取过 {bossId:1}
F(HefuBossSeverAward)

ReConnect = 81					#断线重连的信息传递
F(ReConnect)

LOGIN_SEVEN_DAYS_REWARD_BETA = 82	#北美封测七日登录奖励{1:set(已领取的七日礼包ID,...)}
F(LOGIN_SEVEN_DAYS_REWARD_BETA)

QQRoleBackData = 83	#腾讯回流用户礼包领取数据 {1:回流用户群ID, 2:回流当天day时间戳, 3:回流礼包领取状态, 4:回来连续登录奖励领取记录列表[day1, day2, day3]}
F(QQRoleBackData)

ProjectObj = 84					#专属活动,存储玩家可以领取的奖励{1:{actid->set(rewardId)}, 2:{actid->set(rewardId)}},1为1次性，2为每日清零
F(ProjectObj)

ProjectGetedObj = 85			#专属活动，记录玩家已领取的奖励 {1:set(), 2:set()}#1永久， 2每日
F(ProjectGetedObj)

ProjectDataObj = 86				#专属活动，记录玩家玩家活动期间各种需要保存的数据{actID:{LEVEL:NUM}}
F(ProjectDataObj)

QQActivePageData = 87			#腾讯页面礼包 {1 :set(已经激活ID), 2 : set(已经领取ID)}
F(QQActivePageData)

LimitChest = 88					#限次宝箱，记录玩家开箱获奖的情况{chestCoding:[[(type,thing)],{(type,thing):cnt},times]}
F(LimitChest)

DragonTrain = 89				#驯龙系统
F(DragonTrain)

En_RoleFashions = 90			#角色时装相关set(角色时装ID集合)
F(En_RoleFashions)

FashionData = 91				#时装激活，鉴定，套装相关{{fashionId:{0:是否鉴定, 1:时装阶数, 2:套装ID}, ...}
F(FashionData)

TeamTowerData = 92				#组队爬塔数据{1 : {最高层通关记录index : layer}，2:[历史最好成绩index,round], 3:[今天打过的章节index, layer, 通关分数]}
F(TeamTowerData)

StarGirl = 93					#星灵系统
F(StarGirl)

KaiFuAct = 94					#开服活动(北美版专属)
F(KaiFuAct)

FindBackData = 95				#找回系统数据{1 :{系统index : 可以找回次数},  2 : {系统index : 找回日期标识}}
F(FindBackData)

NationData = 96					#国庆活动{1(节日有礼回赠数据):{活动Unix天数:[当天充值神石, 当天获得经验, 是否领取]},2(登陆礼包已领取dayIndex):set()}
F(NationData)

SevenAct = 97					#七日活动(北美专属)
F(SevenAct)

HalloweenData = 98				#万圣节活动 {1:{收集的卡cardId:cnt}, 2:set(已领取的收集卡奖励), 3:set(当日已完成的任务)，4:{各种buff的结束时间}，5：{buffID:TICK}}
F(HalloweenData)

NAHalloweenData = 99			#北美万圣节
F(NAHalloweenData)

PackagePasswd = 100				#背包密码{'passwd':'thepasswd','reset_time':'清除密码的时间'}
F(PackagePasswd)

DoubleElevenShop = 101			#{1:{coding:已兑换的数量}}
F(DoubleElevenShop)

SaveFashionApe = 102			#保存的时装外观形象{postype:coding}
F(SaveFashionApe)

QQidipRoleConsume = 103			#角色消费日志(特殊做的)
F(QQidipRoleConsume)

GodsTreasure = 104				#众神秘宝{位置ID：位置}
F(GodsTreasure)

VIPLibaoData = 105				#记录玩家已领取的vip礼包{vip等级:状态（1，领取了免费的，2，领取了免费和购买了礼包）,20:set(超级vip每日已领取记录),21:{超级vip限购index:已购买数量}}
F(VIPLibaoData)

FirstPayBoxDay = 106			#首充大礼包{1:{1:开始天数, 2:当前天数, 3:是否连续}}
F(FirstPayBoxDay)

Zuma = 107						#祖玛系统{}
F(Zuma)

KaifuTarget = 108				#7日活动数据
F(KaifuTarget)

DTRebateReward = 109			#双十二返利领不停奖励
F(DTRebateReward)

NATimeLimitBuyData = 110		#北美限时商城{1:{trade:cnt},2:{trade:cnt}},1为每日清理，2不清理
F(NATimeLimitBuyData)

ChristmasActive = 111			#圣诞活动数据{1:圣诞许愿树货架:{goodId:remainCnt(剩余可购买数量),},3:圣诞时装秀购买记录:{goodId:boughtCnt,}]
F(ChristmasActive)

########################################################
#特殊
QQOtherData = 112				#qq其他运营活动数据{1:qq管家7日活动领奖数据[ 0 ：不能领取， 1，可以领取 ， 2：已经领取], 2 : GS系统数据{1 : 角色生日(月份，日)，2 : }}
F(QQOtherData)
########################################################


NYearData = 113					#新年活动｛1：set(已领取的免费index), 2:{1:tickid, 2:{coding:cnt}, 3:刷新时间戳, 4:今日刷新次数, 5:天数}, 3:{兑换字典}｝
F(NYearData)

DailyFBData = 114				#勇者试炼场｛1：进入的试炼场级别（0-表示未进入）, 2:战斗胜利场次, 3:获得经验, 4:数据天数标志(跨天重置数据需要)｝
F(DailyFBData)

GoddessCard = 115				#女神卡牌
F(GoddessCard)

SevenDayHegemony = 116			#七日争霸{'targetAward目标奖励的领取情况':{actType活动类型:set(awardIndex奖励索引)]}
F(SevenDayHegemony)

NYearDataEX = 117				#(复用兑换活动 之前数据不好清理 开个新的同结构)新年活动｛1：set(已领取的免费index), 2:{1:tickid, 2:{coding:cnt}, 3:刷新时间戳, 4:今日刷新次数, 5:天数}, 3:{兑换字典}｝
F(NYearDataEX)

StationObj = 118				#助阵位{1:{助阵位ID:镶嵌等级}, 2:[已解锁的副助阵位ID列表]}
F(StationObj)


XinYueVIPData = 119				#新月特权{1:set(玩家已领取的玩家等级礼包),2:set(玩家已领取的VIP等级礼包),3:set(玩家已领取的每日礼包),4:set(玩家已领取的每周礼包),5:set(玩家已领取的每月礼包),6:记录领取周奖励时的周数,7:[记录领取月奖励时的年数和月数]}
F(XinYueVIPData)

JTMedalCrystal = 120			#{"medal":{1勋章孔位:晶石coding},'sealing':[封印等级,经验]}
F(JTMedalCrystal)

KuaFuJJCData = 121				#跨服竞技场{1:{goodId:bougthCnt,}} 		#(1-跨服商店兑换记录)
F(KuaFuJJCData)

SpringFestivalData = 122		#春节活动{1:[index(0未购买,1-3为购买的档次),购买的时间],2:set(已领取的红包奖励),3:set(已领取的天降财神奖励),4:天降财神总共领取的红包数,5:set(年兽来了已领取的奖励ID),6:{1:tickid, 2:{coding:cnt}, 3:刷新时间戳, 4:今日刷新次数, 5:天数},7:是否领取购买红包奖励标志,8:{时装秀兑换记录}}
F(SpringFestivalData)

LanternFestival = 123			#元宵节活动{"riddles":[每日生成角色猜谜的谜题编号],"rebate":{index某个积分返利的index:{rebateLevel返利的级别:set(roleId已经领取过的激活该返利的角色id)}},'store':{coding物品id:购买次数cnt},'target':set(当日已经领取过的积分目标奖励)}
F(LanternFestival)

OpenYear = 124					#开年活动{1:set([已经领取过的连续登陆礼包index]),2:set([已经领取过的累计登陆礼包index]),3:set([已经领取过的消费礼包index])}
F(OpenYear)

En_RoleRing = 125				#装备的订婚戒指集合
F(En_RoleRing)

ValentineDayData = 126			#魅力情人节{1:{rebateCategory:{rebateType:gottenCnt,},},2:{兑换字典},3:{goodId:buyCnt,}, 4:set([targetid,]), 5:{goalId:isReward,}}  1-玫瑰返利大项奖励已领取次数 2-魅力币兑换记录 3-情人炫酷时装购买记录 4-魅力派对目标奖励领取记录 5-情人目标 key:达成的GoalId value:是否领取
F(ValentineDayData)

GodWarChestData = 127			#战神宝箱{1:[index(0未购买,1-3为购买的档次),购买的时间],2:set(已领取的红包奖励)}
F(GodWarChestData)

RMBComingData = 128				#超级理财{1:[index(0未购买,1-3为购买的档次),购买的时间],2:set(已领取的红包奖励),3:是否领取过道具奖励}
F(RMBComingData)

OldPlayerBack = 129				#老玩家回流活动{1:set([回归登录大礼(老服)已经领取的index]),2:set([回归等级大礼(新服)已经领取的index]),3:set([老玩家独享奖励(老服)已经领取的index]),4:set([老玩家独享奖励(新服)已经领取的index]),5:set([老玩家贵族特权奖励(老服)已经领取的index]),6:set([老玩家贵族特权奖励(新服)已经领取的index]),}
F(OldPlayerBack)

LianChongRebateData = 130		#连充返利{1:{rewardType:[buyTimes,lastModifyDay],}, 2:{rewardType:set(rewardLevel)},3:[rewardType1,rewardType2,]} 1:累计返利项达成天次及最后更新日 2:累计返利项领取记录F(LianChongRebateData) 3: 今日充值达标已领奖的项
F(LianChongRebateData)

ShenWangBaoKu = 131				#神王宝库{1:[个人抽奖记录], 2:{玩家积商城兑换数据}}
F(ShenWangBaoKu)

QingMingData = 132				#清明活动{1:{pos:rewardId,},2：set([rewardIndex,],3:{(year,month,day):充值记录},4:{(year,month,day):消费记录},5:set([充值奖励领取记录]),6:set([消费奖励领取记录]),7:{徽章兑换记录 }}	1-清明踏青翻牌记录 2-今日累计翻牌奖励领取记录 3:角色消费记录
F(QingMingData)

QQLZHDData = 133				#蓝钻转转乐已领取奖励set()
F(QQLZHDData)

En_RoleMagicSpirits = 134			#主角魔灵集合
F(En_RoleMagicSpirits)

En_HeroMagicSpirits = 135			#英雄魔灵集合
F(En_HeroMagicSpirits)

MFZData = 136						#魔法阵数据{1:[skillType,skillLevel],2:{heroId:[skillType,skillLevel],} 1-主角携带技能 2-英雄携带节能
F(MFZData)

QQHZHDData = 137				#黄钻转转乐已领取奖励set()
F(QQHZHDData)

SuperInvestObj = 138				#超级投资{超级投资索引:{1:投资时间, 2:已领取的奖励集合}}
F(SuperInvestObj)

FiveOneDayObj = 139				#五一活动{1:set(已领取的消费奖励),2:恶龙血量,3:{随机到的奖品},4:{神龙宝库每个物品兑换次数}}
F(FiveOneDayObj)

SuperCards = 140				#{1:失效Unix天数, 2:set(选择特权), 3:set(已经使用过的一键特权)}
F(SuperCards)

YeYouJieWarmup = 141			#页游节预热活动{1:set(已经领取的登录奖励index),2:{页游节折扣汇某个goodId的购买次数},3:{页游节折扣汇当前商品字典goodid:是否可购买 }}
F(YeYouJieWarmup)

YeYouJieKuangHuan = 142			#页游节狂欢暴击{1:set(已领取返利奖励的天数)}
F(YeYouJieKuangHuan)

KongJianDecennial = 143			#空间十周年{1:set(累充送惊喜已领取奖励{rewardIndex:levelRangeId,}), 2:set(周年纪念币兑换记录[exchangeId,levelRangeId],)}
F(KongJianDecennial)

LatestActData = 144			#最新活动{1:{可以领取的一次性actId->set(rewardId)}, 2:{可以领取的每日actId->set(rewardId)}, 3:{已领取的一次性奖励rewardId->次数}, 4:{已领取的每日奖励rewardId->次数}, 5:{活跃度任务->完成次数}, 6:活跃度}
F(LatestActData)

WangZheGongCe = 145			#王者公测{1:{在线有豪礼领取记录 (rewardIndex, levelRangeId):set(itemIndex,)},2:{兑换由我定兑换记录coding:cnt,}, 3:{最炫时装秀购买记录goodId:boughtCnt,},4:{公测折扣汇某个goodId的购买次数},5:{公测折扣汇当前商品字典goodid:是否可购买 }, 6:{奖励狂翻倍已领取记录finishTaskIndex:rewardFlag,},},7:set(充值返利转盘已抽出itemIndex),8:set(充值返利返利领取记录)}
F(WangZheGongCe)

OldRoleback_FT = 146			#繁体版老玩家回流 {1:set([已经签到的天数])}
F(OldRoleback_FT)

GSMall_Limit_Dict = 147			#GS商城限购数据{1:{每日限购tradeId-->cnt}, 2:{永久限制tradeId-->cnt}}
F(GSMall_Limit_Dict)

PassionActData = 148		#激情活动数据{激情有礼累计奖励领取记录1:set([rewardIndex]),2奖励狂翻倍任务记录{finishedTaskIndex:rewardFlag,},3:{激情卖场某个goodId的购买次数},4:{激情卖场当前商品字典goodid:是否可购买 },5:{最炫时装秀购买记录goodId:boughtCnt,}}
F(PassionActData)

QQLZBaoXiang = 149			#蓝钻宝箱活动数据{1:{ 宝箱ID:[宝箱奖品索引， 英雄等级段, 第几次抽奖]}, 2: [抽取次数对应的宝箱id] }
F(QQLZBaoXiang)

ShenMiBaoXiang = 150		#神秘宝箱抽取{1:随机用于显示的8个index列表,2，当前宝箱可以开出的4个奖励index列表 。4总共领取的次数(用于计算极品奖励)。5，下个宝箱必出的极品奖励index列表}
F(ShenMiBaoXiang)

PreciousStoreBuyData = 151			#珍宝商店购买数据{1:{每日限购index-->cnt}, 2:{活动期间限购index-->cnt}}
F(PreciousStoreBuyData)

DKCNewData = 152			#新龙骑试炼数据{1:{DKCLevel:{rewardPoolId:[idx, pos],},},} 1:关卡DKCLevel中第rewardPoolId套奖励中下标idx的位置pos
F(DKCNewData)

MysteryBoxData = 153			#神秘宝箱数据{1:{boxCoding:idxSet(),}, 2:{boxCoding:timeOutStamp,}} 1:神秘宝箱抽取奖励状态 宝箱coding:已抽取的idxSet 2:数据超时时间戳 宝箱coding:timeOutStamp
F(MysteryBoxData)

En_RoleCuiLian = 154			#淬炼字典 {1:角色淬炼次数, 英雄ID:英雄淬炼次数}
F(En_RoleCuiLian)

CTTRoleData = 155			#虚空幻境{1:{商品：购买状态},2:记录刷新时的天数}
F(CTTRoleData)

ZhongQiuData = 156			#中秋活动数据 {1:set([dayIndex,]),2:[rewardId,], }} 1:中秋首冲已领取奖励dayIndex集合 2:中秋赏月翻开而未领取的奖励;
F(ZhongQiuData)

LostSceneObj = 157			#迷失之境兑换数据{1:{已兑换物品coding:已兑换数量}}
F(LostSceneObj)

ElevenActData = 158			#双十一活动数据{1:set(rewardindex,),5:当日商城消费神石,6:set([已领取奖励]),7:{1:充值积分，2：{兑换index: 兑换cnt}} 1:今日登录有礼已经领取的奖励索引6:#双十一充值大放送;7:#双十一积分兑换
F(ElevenActData)

ToouchGoldData = 159		#点石成金,{原石类型：数量}
F(ToouchGoldData)

NewQandAData = 160			#新答题活动数据{0:(决赛总时间, 决赛得分) 周几: 当天数据，8：[当天题目]，9：当前登录对应2015年11月9日周数， 10：本日得分, 11：最新题目对应天数 12：答题开始时间戳}		
F(NewQandAData)

PuzzleData = 161			#趣味拼图数据{0:[拼图顺序]，1：int 奖励索引，2：finsh 记录完成情况，3：记录图片的id，4：tick 记录拼图cd的tick，5：记录图片的开始时间 ，6：记录时间的结束时间，7：记录拼图状态，8：记录奖励状态，9：奖励等级}
F(PuzzleData)

CatchingFishBox = 162		#捕鱼活动奖励状态[]index代表第几个宝箱，[index]代表宝箱状态
F(CatchingFishBox)

CardAtlasDict = 163			#卡牌图鉴	{1:{卡牌id:卡牌个数}, 2:{图鉴组id:{0:图鉴组id品阶, 图鉴id:[图鉴品阶, 图鉴强化等级]}}}
F(CardAtlasDict)

NewYearDayEgg = 164			#版本修复后可复用（可用）-
F(NewYearDayEgg)

NewYearDayPigData = 165		#版本修复后可复用（可用）-
F(NewYearDayPigData)

Game2048Data = 166			#游戏2048数据
F(Game2048Data)

ElementBrandData = 167		#元素印记{1:{brandId:[type,color,level,talent,pos,savePro,unsavePro],},2:{brandId:[type,color,level,talent,pos,savePro,unsavePro],},3:{(type,color,level):cnt,},4:set(visionId,)} 1表示背包中印记数据，2表示镶嵌的印记数据 3表示材料印记数据 4表示激活的幻化外形ID集合
F(ElementBrandData)

SealData = 168				#圣印系统数据{Sealtype:SealId}
F(SealData)

ChaosDivinityData = 169		#混沌神域数据{0:set(通关章节),1:set(技能ID),2:{1:,2:,3:,4:,5:,6:,7:,8:,9:,10:,11:,12:}}
F(ChaosDivinityData)

QQLZShopData = 170			#QQ蓝钻商店购买数据
F(QQLZShopData)

LianLianKanData = 171		#连连看数据
F(LianLianKanData)

QQLZFeedBackData = 172 		#蓝钻回馈已抽取奖励
F(QQLZFeedBackData)