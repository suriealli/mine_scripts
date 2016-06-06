#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Hero.HeroConfig")
#===============================================================================
# 英雄配置
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile
from Game.Role.Obj import Base
from Game.Property import PropertyEnum


if "_HasLoad" not in dir():
	HERO_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HERO_FILE_FOLDER_PATH.AppendPath("HeroConfig")
	
	#基础配置
	Hero_Base_Config = {}
	#英雄经验配置
	HeroLevelExp_Dict = {}
	#解雇英雄返还物品配置
	HeroLevelExpReturnItems_Dict = {}
	#经验丹配置
	HeroExpItem_Dict = {}
	#英雄祭坛
	HeroAltar_Dict = {}
	#英雄祭坛奖励
	HeroAltarReward_Dict = {}
	#英雄兑换配置
	HeroChange_Dict = {}
	#淬炼石配置
	CuiLianShi_Dict = {}
	#转生光环配置
	ZhuangShengHaloConfigDict = {}
	MaxZhuanShengHaloLv = 0
	#主角转生配置
	RoleZhuanShengConfigDict = {}
	MaxRoleZhuanShengLv = 0
	
#基础配置
class HeroBaseConfig(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("HeroBaseConfig.txt")
	def __init__(self):
		self.heroNumber = int			#英雄编号
		self.name = str					#名字
		self.career = int				#法、攻、辅
		self.star = int					#星阶
		self.heroType = int				#英雄类型
		self.grade = int				#品阶
		
		self.colorCode = int			#颜色编码
		
		self.returnItems = self.GetEvalByString				#解雇返还物品
		
		#招募
		self.needReputation = int							#招募需要声望
		self.needLevel = int								#招募需要等级
		self.needMoney = int								#招募需要银币
		self.needItems = self.GetEvalByString				#招募需要物品
		self.coolCD = int									#招募冷却CD
		
		#进阶
		self.nextGradeHeroNumber = int		#升阶后英雄编号
		self.upgradeNeedLv = int			#升阶需要等级
		self.upgradeNeedItem = eval			#升阶需要物品
		self.upgradeNeedHeroNumber = int	#升阶需要英雄编号
		self.upgradeNeedRoleLv = int		#升阶需要主角等级
		
		#觉醒
		self.canAwaken = int										#是否可觉醒
		self.awakenHeroNumber = self.GetEvalByString				#觉醒后的英雄Number
		self.needHeroActID = int									#觉醒需要通关的英雄圣殿id
		self.awakenRoleLevel = int									#觉醒需要主角等级
		self.awakenHeroLevel = int									#觉醒需要英雄等级
		self.awakenHeroStar	 = int									#觉醒需要英雄达到品阶
		self.awakenNeedItem = self.GetEvalByString					#觉醒需要的道具
		
		self.canFollow = int			#是否能够跟随
		
		self.NpcType = int				#外形
		
		self.maxLevel = int				#最大等级
		
		self.CuiLianShiCnt = int		#可以使用淬炼石最大个数
		
		#技能
		self.normal_skill = eval		#默认普通技能
		self.learn_activeSkill = eval	#已学习的主动技能
		self.learn_passiveSkill = eval	#已学习的被动技能
		
		#属性 -- 乘了10000的
		self.maxhp = int				#生命
		self.maxhp_Plus = int			#生命成长
		self.maxhp_Coe = int			#生命系数
		self.attackspeed = int			#攻击速度
		self.anger = int				#怒气
		self.attack_Plus = int			#攻击成长
		self.attack_Coe = int			#攻击系数
		self.attack_p = int				#物攻
		self.defense_p = int			#物防
		self.attack_m = int				#法功
		self.defense_m = int			#法防
		self.crit = int					#暴击
		self.critpress = int			#免暴
		self.antibroken = int			#破防
		self.notbroken = int			#免破
		self.parry = int				#格挡
		self.puncture = int				#破挡
		self.damageupgrade = int		#增伤
		self.damagereduce = int			#免伤
#=====================================================
#转生
#=====================================================
		self.zhuanshengLevel = int
		self.canZhuanSheng	 = int
		self.zhuanshengNeedLevel = self.GetIntByString
		self.zhuanshengHeroNumber = self.GetIntByString
		self.zhuanshengNeedRoleZSLv	 = self.GetIntByString
		self.zhuanshengNeedItem = self.GetEvalByString
		self.zhuanshengNeedMoney = self.GetIntByString

		#转生属性 -- 基础属性
		self.maxhp_z = int				#生命
		self.attackspeed_z = int		#攻击速度
		self.anger_z = int				#怒气
		self.attack_p_z = int			#物攻
		self.defense_p_z = int			#物防
		self.attack_m_z = int			#法功
		self.defense_m_z = int			#法防
		self.crit_z = int				#暴击
		self.critpress_z = int			#免暴
		self.antibroken_z = int			#破防
		self.notbroken_z = int			#免破
		self.parry_z = int				#格挡
		self.puncture_z = int			#破挡
		self.damageupgrade_z = int		#增伤
		self.damagereduce_z = int		#免伤
	
	def InitProperty(self):
		self.p_dict = {}
		self.p_dict[PropertyEnum.maxhp] = (self.maxhp, self.maxhp_Plus, self.maxhp_Coe)
		self.p_dict[PropertyEnum.attackspeed] = (self.attackspeed, 0, 0)
		self.p_dict[PropertyEnum.anger] = (self.anger, 0, 0)
		self.p_dict[PropertyEnum.attack_p] = (self.attack_p, self.attack_Plus, self.attack_Coe)
		self.p_dict[PropertyEnum.defense_p] = (self.defense_p, 0, 0)
		self.p_dict[PropertyEnum.attack_m] = (self.attack_m, self.attack_Plus, self.attack_Coe)
		self.p_dict[PropertyEnum.defense_m] = (self.defense_m, 0, 0)
		self.p_dict[PropertyEnum.crit] = (self.crit, 0, 0)
		self.p_dict[PropertyEnum.critpress] = (self.critpress, 0, 0)
		self.p_dict[PropertyEnum.antibroken] = (self.antibroken, 0, 0)
		self.p_dict[PropertyEnum.notbroken] = (self.notbroken, 0, 0)
		self.p_dict[PropertyEnum.parry] = (self.parry, 0, 0)
		self.p_dict[PropertyEnum.puncture] = (self.puncture, 0, 0)
		self.p_dict[PropertyEnum.damageupgrade] = (self.damageupgrade, 0, 0)
		self.p_dict[PropertyEnum.damagereduce] = (self.damagereduce, 0, 0)
		
		from Game.Role.Config import RoleConfig
		if self.grade in RoleConfig.Grade_To_Star_Dict:
			if RoleConfig.Grade_To_Star_Dict[self.grade] != self.star:
				print "GE_EXC, error in heroConfig grade to star (%s)" % self.heroNumber
		RoleConfig.Grade_To_Star_Dict[self.grade] = self.star
		
		if self.grade in RoleConfig.Grade_To_ColorCode_Dict:
			if RoleConfig.Grade_To_ColorCode_Dict[self.grade] != self.colorCode:
				print "GE_EXC, error in heroConfig grade to colorCode (%s)" % self.heroNumber
		RoleConfig.Grade_To_ColorCode_Dict[self.grade] = self.colorCode
	
	def InitZhuangshengProperty(self):
		self.p_dict_z = {}
		self.p_dict_z[PropertyEnum.maxhp] = self.maxhp_z
		self.p_dict_z[PropertyEnum.attackspeed] = self.attackspeed_z
		self.p_dict_z[PropertyEnum.anger] = self.anger_z
		self.p_dict_z[PropertyEnum.attack_p] = self.attack_p_z
		self.p_dict_z[PropertyEnum.defense_p] = self.defense_p_z
		self.p_dict_z[PropertyEnum.attack_m] = self.attack_m_z
		self.p_dict_z[PropertyEnum.defense_m] = self.defense_m_z
		self.p_dict_z[PropertyEnum.crit] = self.crit_z
		self.p_dict_z[PropertyEnum.critpress] = self.critpress_z
		self.p_dict_z[PropertyEnum.antibroken] = self.antibroken_z
		self.p_dict_z[PropertyEnum.notbroken] = self.notbroken_z
		self.p_dict_z[PropertyEnum.parry] = self.parry_z
		self.p_dict_z[PropertyEnum.puncture] = self.puncture_z
		self.p_dict_z[PropertyEnum.damageupgrade] = self.damageupgrade_z
		self.p_dict_z[PropertyEnum.damagereduce] = self.damagereduce_z
	
	
class HeroLevelExpConfig(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("HeroLevelExp.txt")
	def __init__(self):
		self.level = int
		self.exp1 = int
		self.returnItems1 = self.GetEvalByString	#返还物品
		self.exp2 = int
		self.returnItems2 = self.GetEvalByString
		self.exp3 = int
		self.returnItems3 = self.GetEvalByString
		self.exp4 = int
		self.returnItems4 = self.GetEvalByString
		self.exp5 = int
		self.returnItems5 = self.GetEvalByString
		self.exp6 = int
		self.returnItems6 = self.GetEvalByString
		self.exp7 = int
		self.returnItems7 = self.GetEvalByString
		self.exp8 = int
		self.returnItems8 = self.GetEvalByString
		
class HeroExpItem(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("HeroExpItem.txt")
	def __init__(self):
		self.itemCoding = int
		self.exp = int
		self.cost = int

class HeroAltar(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("HeroAltar.txt")
	def __init__(self):
		self.index = int
		self.name = str
		self.openLevel = int
		self.needItem = eval
		self.needUnbindRMB = int
		self.discountUnbindRMB = int		#折扣召唤需要的神石
		self.normal = eval
		self.advanced = eval
		
	def NormalRandom(self):
		self.normal_call = Random.RandomRate()
		for (rate, mcid) in self.normal:
			self.normal_call.AddRandomItem(rate, mcid)
	
	def AdvancedRandom(self):
		self.advanced_call = Random.RandomRate()
		for (rate, mcid) in self.advanced:
			self.advanced_call.AddRandomItem(rate, mcid)
	
class HeroAltarReward(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("HeroAltarReward.txt")
	def __init__(self):
		self.mcid = int
		self.rewardItems = self.GetEvalByString
		self.heroNumber = self.GetEvalByString
		
class HeroChangeConfig(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("HeroChangeConfig.txt")
	def __init__(self):
		self.heroNumber = int
		self.needLevel = int
		self.needItem = eval

class CuiLianShiConfig(TabFile.TabLine):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("CuiLianShi.txt")
	def __init__(self):
		self.pt = int
		self.pv = int


class HaloConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("ZhuanShengHalo.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.HaloLevel = int
		self.NeedExp = int
		self.AddCoe = int


class RoleZhuanShengConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = HERO_FILE_FOLDER_PATH.FilePath("ZhuanShengRole.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.ZhuanShengLv = int
		self.NeedMoney = int
		self.NeedHaloLv = int
		self.NeedItem = eval


def LoadHaloConfig():
	global ZhuangShengHaloConfigDict
	for config in HaloConfig.ToClassType():
		if config.HaloLevel in ZhuangShengHaloConfigDict:
			print "GE_EXC,repeat HaloLevel(%s) in ZhuangShengHaloConfigDict" % config.HaloLevel
		config.InitProperty()
		ZhuangShengHaloConfigDict[config.HaloLevel] = config
	
	global MaxZhuanShengHaloLv
	MaxZhuanShengHaloLv = max(ZhuangShengHaloConfigDict.iterkeys())


def LoadRoleZhuanShengConfig():
	global RoleZhuanShengConfigDict
	for config in RoleZhuanShengConfig.ToClassType():
		if config.ZhuanShengLv in RoleZhuanShengConfigDict:
			print "GE_EXC,repeat ZhuanShengLv(%s) in RoleZhuanShengConfigDict" % config.ZhuanShengLv
		config.InitProperty()
		RoleZhuanShengConfigDict[config.ZhuanShengLv] = config
	
	global MaxRoleZhuanShengLv
	MaxRoleZhuanShengLv = max(RoleZhuanShengConfigDict.iterkeys())


def LoadCuiLianShiConfig():
	global CuiLianShi_Dict
	for CuiLian in CuiLianShiConfig.ToClassType():
		if CuiLian.pt in CuiLianShi_Dict:
			print "GE_EXC, repeat hero number (%s) in CuiLianShi_Dict" % CuiLian.pt
			continue
		CuiLianShi_Dict[CuiLian.pt] = CuiLian.pv
def LoadHeroChangeConfig():
	global HeroChange_Dict
	for HCC in HeroChangeConfig.ToClassType():
		if HCC.heroNumber in HeroChange_Dict:
			print "GE_EXC, repeat hero number (%s) in HeroChange_Dict" % HCC.heroNumber
			continue
		HeroChange_Dict[HCC.heroNumber] = HCC
	
def LoadHeroAltar():
	global HeroAltar_Dict
	for HA in HeroAltar.ToClassType():
		if HA.index in HeroAltar_Dict:
			print "GE_EXC, repeat index (%s) in HeroAltar_Dict" % HA.index
			continue
		HeroAltar_Dict[HA.index] = HA
		
		HA.NormalRandom()
		HA.AdvancedRandom()
		
def LoadHeroAltarReward():
	global HeroAltarReward_Dict
	for HAR in HeroAltarReward.ToClassType():
		if HAR.mcid in HeroAltarReward_Dict:
			print "GE_EXC, repeat mcid (%s) in HeroAltarReward_Dict" % HAR.mcid
		HeroAltarReward_Dict[HAR.mcid] = HAR
	
def LoadHeroBaseConfig():
	#读取基础配置
	global Hero_Base_Config
	for HBC in HeroBaseConfig.ToClassType():
		if HBC.heroNumber in Hero_Base_Config:
			print "GE_EXC, repeat heroNumber in LoadHeroBaseConfig (%s)" % HBC.heroNumber
			continue
		#可以觉醒的英雄 没有觉醒后英雄编号
		if HBC.canAwaken and not HBC.awakenHeroNumber:
			print "GE_EXC, HBC(%s) error,HBC.canAwaken and not HBC.awakenHeroNumber" % HBC.heroNumber
			continue
		HBC.InitProperty()
		HBC.InitZhuangshengProperty()
		Hero_Base_Config[HBC.heroNumber] = HBC
		
		#载入数据用配置
		if HBC.heroNumber in Base.Obj_Config:
			print "GE_EXC, LoadHeroBaseConfig repeat heroNumber (%s) in Base.Obj_Config" % HBC.heroNumber
			continue
		Base.Obj_Config[HBC.heroNumber] = HBC

def LoadHeroLevelExp():
	#英雄经验配置
	global HeroLevelExp_Dict
	global HeroLevelExpReturnItems_Dict
	for LEXP in HeroLevelExpConfig.ToClassType():
		if LEXP.level in HeroLevelExp_Dict:
			print "GE_EXC, repeat hero level (%s) in LoadHeroLevelExp" % LEXP.level
			continue
		HeroLevelExp_Dict[LEXP.level] = {1:LEXP.exp1, 2:LEXP.exp2, 3:LEXP.exp3, 4:LEXP.exp4, 5:LEXP.exp5, 6:LEXP.exp6, 7:LEXP.exp7, 8:LEXP.exp8}
		HeroLevelExpReturnItems_Dict[LEXP.level] = {1:LEXP.returnItems1, 2:LEXP.returnItems2, 3:LEXP.returnItems3, 4:LEXP.returnItems4, 5:LEXP.returnItems5, 6:LEXP.returnItems6, 7:LEXP.returnItems7, 8:LEXP.returnItems8}
	
def LoadHeroExpItem():
	#读取经验丹配置
	global HeroExpItem_Dict
	for HEI in HeroExpItem.ToClassType():
		if HEI.itemCoding in HeroExpItem_Dict:
			print "GE_EXC, repeat itemCoding in LoadHeroExpItem (%s)" % HEI.itemCoding
			continue
		HeroExpItem_Dict[HEI.itemCoding] = HEI

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHeroBaseConfig()
		LoadHeroLevelExp()
		LoadHeroExpItem()
		LoadHeroAltar()
		LoadHeroAltarReward()
		LoadHeroChangeConfig()
		LoadCuiLianShiConfig()
		LoadHaloConfig()
		LoadRoleZhuanShengConfig()

