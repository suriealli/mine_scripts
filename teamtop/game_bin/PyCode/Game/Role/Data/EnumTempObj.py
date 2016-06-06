#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumTempObj")
#===============================================================================
# 临时对象数组
#===============================================================================
#MaxTempObjSize 注意最大 大小在Game.Role.Data.Enum中定义
#角色的临时管理器
LoginInfo = 0					#登录信息
enPackMgr = 1					#背包管理
SubTaskCheckCache = 2			#支线任务检测优化缓存{subtaskEnumType: [cfg]}
enRoleEquipmentMgr = 3			#角色装备管理
enHeroEquipmentMgrDict = 4		#英雄装备管理
enGlobalItemMgr = 5				#全局物品管理字典 key : id   value: obj
enHeroMgr = 6					#英雄管理器
CharRoleIDSet = 7				#聊天角色ID集合
enTarotMgr = 8					#占卜
FightCamp = 9					#战斗中的阵营
TitlePro = 10					#称号属性
enStationMgr = 11				#阵位管理器
PrivateNPCDict = 12				#关卡私有NPC缓存字典，进出关卡会被清理
MirrorScene = 13				#临时副本对象
ArmyGeniusMgr = 14				#临时军团天赋管理器
MountMgr = 15					#坐骑管理器
enRoleArtifactMgr = 16 			#角色神器管理
enHeroAtrifactMgrDict = 17		#英雄神器管理
FB_Moral = 18					#副本保存怒气
HelpStationProperty = 19		#助阵位置属性
MainTask_Moral = 20				#主线任务保存怒气
PurgatoryInFight = 21			#在心魔炼狱战斗中
PetMgr = 22						#宠物管理器
DragonMgr = 23					#神龙管理器
enRoleHallowsMgr = 24			#角色圣器管理器
enHeroHallowsMrgDict = 25		#英雄圣器管理器
PM = 26							#属性管理器

MarryFilter = 27				#结婚对象
TalentCardMgr = 28				#天赋卡管理

CardUM = 29						#月卡赠送临时公会成员

WildBossRegion = 30				#野外BOSS区域对象
WildRoleObj = 31				#野外BOSS角色对象

enRoleFashionMgr = 32			#装备的时装管理
enRoleFashionGlobalMgr = 33		#时装鉴定，套装等的管理

DragonTrainMgr = 34				#驯龙系统管理
StarGirlMgr = 35				#星灵系统管理
KaiFuActMgr = 36				#开服活动管理(北美专属)

GloryWarRole = 37				#荣耀之战角色对象

FindBackTempData = 38			# -------改版后已经废弃
FindBakcTrigger = 39			#找回系统性能优化集合

SevenActMgr = 40				#七日活动管理(北美专属)

DragonVein = 41					#龙脉系统管理

HalloweenNAMgr = 42				#北美万圣节(北美专属)
SpaceRole = 43					#混乱时空角色对象

CrossJTeamObj = 44				#组队竞技场跨服战队临时对象
CrossJTRole = 45				#组队竞技场角色临时对象

ZumaGame = 46					#祖玛游戏

CrossJTGroupTeam = 47			#跨服争霸小组赛对象
CrossJTFinalTeam = 48			#跨服争霸总决赛对象

MallGivingUnionData = 49		#商城赠送公会临时成员数据

GS_Data = 50				#GS消息临时数据

enRoleRingMgr = 51				#订婚戒指管理器

MarryRingImprintMsg = 52				#订婚戒指铭刻信息

enRoleMagicSpiritMgr = 53				#角色魔灵管理器
enHeroMagicSpiritMgrDict = 54		#英雄魔灵管理器字典

UnionKuaFuWarRole = 55			#公会圣域争霸角色对象
UnionKuaFuWarMgr = 56			#公会圣域争霸管理对象
UnionKuaFuWarUnion = 57			#公会圣域争霸公会对象

UnionFBSubstituteTeam = 58		#公会副本替身队伍对象

WarStationMgr = 59		#战阵管理

LoginTime = 60			#登录时间

LostScene = 61				#迷失之境 {技能id:冷却完成时间, ...}

Puzzlemgr = 62


DeepHellRole = 63				#深渊炼狱角色对象

Game2048 = 64					#2048游戏

ElementBrandMgr = 65			#元素印记管理器

ChaosDivinityTeam = 66			#混沌神域替身队伍