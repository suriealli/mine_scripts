#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Marry.MarryConfig")
#===============================================================================
# 注释
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random
from Game.Property import PropertyEnum


if "_HasLoad" not in dir():
	MW_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	MW_FILE_FOLDER_PATH.AppendPath("Marry")
	
	MarryTime_Dict = {}
	MarryGrade_Dict = {}
	MarryLibao_Dict = {}
	
	WeddingRing_Dict = {}
	WeddingRingSoul_Dict = {}
	WeddingRingSoulP_Dict = {}
	WeddingRingSoulPM_Dict = {}
	
	WeddingIDAct_Dict = {}
	WeddingSingleProAct_Dict = {}
	WeddingMultiProAct_Dict = {}
	WeddingSkill_Dict = {}
	WeddingGradeAct_Dict = {}
	
	
	PartyGrade_Dict = {}
	PartyCandyGrade_Dict = {}
	PartyBless_Dict = {}
	PartyHappyCnt_Dict = {}
	PartyHappyReward_Dict = {}
	
	Qinmi_Dict = {}
	QinmiGrade_Dict = {}
	QinmiTitleSet = set()
	QinmiTitleIdToGrade = {}
	
	HoneymoonGrade_Dict = {}
	
	RingGradePro_Dict = {}
	RingImprintPro_Dict = {}
	
	RoyalGuardSay_Dict = {}
	
	RoyalGuardSayRandom_Dict = {}
	
	Ring_Dict = {}
	
	PartyServerType_Dict = {}
	
class PartyServerTypeConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("PartyServerType.txt")
	def __init__(self):
		self.serverType = int						#服务器类型
		self.kaifuDay = eval						#开服天数区间
	
def LoadPartySTConfig():
	global PartyServerType_Dict
	
	for PST in PartyServerTypeConfig.ToClassType():
		if PST.serverType in PartyServerType_Dict:
			print "GE_EXC, repeat serverType (%s) in PartyServerType_Dict" % PST.serverType
		PartyServerType_Dict[PST.serverType] = PST
	
class RingConfig(TabFile.TabLine):
	#订婚戒指
	ITEM_R = 6#用于识别普通物品/装备/神器/圣器/时装
	useFun = None
	canOverlap = False#默认不可以叠加
	canTrade = False
	kinds = 7
	FilePath = MW_FILE_FOLDER_PATH.FilePath("Ring.txt")
	def __init__(self):
		self.coding = int							#道具coding
		self.name = str								#名字
		self.pt1 = int								#基础属性类型
		self.pv1 = int								#基础属性值
		self.pt2 = int
		self.pv2 = int
		self.pt3 = int
		self.pv3 = int
		self.pt4 = int
		self.pv4 = int
		self.pt5 = int
		self.pv5 = int
		
		self.impt1 = int
		self.impt2 = int
		self.impt3 = int
		self.impt4 = int
		
		self.impv1 = int							#铭刻属性
		self.impv2 = int
		self.impv3 = int
		self.impv4 = int
		
		self.canSell = int							#是否可以出售
		self.saleBack = int
		self.salePrice = int
		
		self.jiaMi = int							#是否加密
		
		self.needLog = int							#是否需要记录日志
		
	def InitProperty(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		if self.pt3 and self.pv3:
			self.p_dict[self.pt3] = self.pv3
		if self.pt4 and self.pv4:
			self.p_dict[self.pt4] = self.pv4
		if self.pt5 and self.pv5:
			self.p_dict[self.pt5] = self.pv5
		
		self.imp_dict = {}
		if self.impt1 and self.impv1:
			self.imp_dict[self.impt1] = self.impv1
		if self.impt2 and self.impv2:
			self.imp_dict[self.impt2] = self.impv2
		if self.impt3 and self.impv3:
			self.imp_dict[self.impt3] = self.impv3
		if self.impt4 and self.impv4:
			self.imp_dict[self.impt4] = self.impv4
		
def LoadRingBase():
	#订婚戒指基础配置
	global Ring_Dict
	from Game.Role.Obj import Base
	from Game.Item import ItemConfig
	from Game.Item import Item
	for RC in RingConfig.ToClassType():
		if RC.coding in ItemConfig.ItemCfg_Dict:
			print "GE_EXC, repeat coding in LoadRingBase, (%s)" % RC.coding
		
		RC.InitProperty()
		
		ItemConfig.ItemCfg_Dict[RC.coding] = RC
		if RC.coding in Base.Obj_Config:
			print "GE_EXC, LoadRingBase repeat coding in Base.Obj_Config"
		Base.Obj_Config[RC.coding] = RC
		
		if RC.coding in Base.Obj_Type_Fun:
			print "GE_EXC, repeat RegTypeObjFun. EC,(%s)" % RC.coding
		Base.Obj_Type_Fun[RC.coding] = Item.Ring
		ItemConfig.GoodsSet.add(RC.coding)
		
		if RC.coding not in Ring_Dict:
			Ring_Dict[RC.coding] = RC
	
class RoyalGuardSayRandom(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("RoyalGuardSayRandom.txt")
	def __init__(self):
		self.sayCnt = int							#说话次数
		self.randomList = eval						#随机列表
	
def LoadRoyalGuardSayRandom():
	global RoyalGuardSayRandom_Dict
	
	for RGSR in RoyalGuardSayRandom.ToClassType():
		if RGSR.sayCnt in RoyalGuardSayRandom_Dict:
			print 'GE_EXC, repeat sayCnt %s in RoyalGuardSayRandom_Dict' % RGSR.sayCnt
		RoyalGuardSayRandom_Dict[RGSR.sayCnt] = RGSR
	
class RoyalGuardSay(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("RoyalGuardSay.txt")
	def __init__(self):
		self.sayIndex = int							#说话索引
		self.sayContent = str						#说话内容
	
def LoadRoyalGuardSay():
	global RoyalGuardSay_Dict
	
	for RGS in RoyalGuardSay.ToClassType():
		if RGS.sayIndex in RoyalGuardSay_Dict:
			print 'GE_EXC, repeat sayIndex %s in RoyalGuardSay_Dict' % RGS.sayIndex
		RoyalGuardSay_Dict[RGS.sayIndex] = RGS
	
class HoneymoonGrade(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("HoneymoonGrade.txt")
	def __init__(self):
		self.grade = int				#蜜月档次
		self.needRMB = int				#需要的神石
		self.qinmi = int				#亲密
		self.libaoCoding = int			#礼包道具coding
	
def LoadHoneymoonGrade():
	global HoneymoonGrade_Dict
	
	for HG in HoneymoonGrade.ToClassType():
		if HG.grade in HoneymoonGrade_Dict:
			print 'GE_EXC, repeat grade %s in HoneymoonGrade_Dict' % HG.grade
		HoneymoonGrade_Dict[HG.grade] = HG
	
	
class PartyGrade(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("PartyGrade.txt")
	def __init__(self):
		self.grade = int				#派对档次
		self.needRMB = int				#需要的神石
		self.freeCandy = eval			#免费喜糖
		self.qinmi = int				#亲密度
		self.candyCnt = int				#可发放喜糖次数
		
def LoadPartyGrade():
	global PartyGrade_Dict
	
	for PG in PartyGrade.ToClassType():
		if PG.grade in PartyGrade_Dict:
			print 'GE_EXC, repeat grade %s in PartyGrade_Dict' % PG.grade
		PartyGrade_Dict[PG.grade] = PG
	
class PartyCandyGrade(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("PartyCandy.txt")
	def __init__(self):
		self.grade = int
		self.needRMB = int
		self.candyCoding = int
		self.qinmi = int
		
def LoadPartyCandyGrade():
	global PartyCandyGrade_Dict
	
	for PCG in PartyCandyGrade.ToClassType():
		if PCG.grade in PartyCandyGrade_Dict:
			print 'GE_EXC, repeat grade %s in PartyCandyGrade_Dict' % PCG.grade
		PartyCandyGrade_Dict[PCG.grade] = PCG
	
class PartyBless(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("PartyBless.txt")
	def __init__(self):
		self.grade = int
		self.needMoney = self.GetIntByString
		self.needRMB = self.GetIntByString
		self.rewardCoding = int
		self.giftCoding = int
	
def LoadPartyBless():
	global PartyBless_Dict
	
	for PB in PartyBless.ToClassType():
		if PB.grade in PartyBless_Dict:
			print 'GE_EXC, repeat grade %s in PartyBless_Dict' % PB.grade
		PartyBless_Dict[PB.grade] = PB
	
class PartyHappy(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("PartyHappy.txt")
	def __init__(self):
		self.happyIndex = int
		self.needKuafuMoney = int
		self.happy = int
	
def LoadPartyHappy():
	global PartyHappyCnt_Dict
	
	for PH in PartyHappy.ToClassType():
		if PH.happyIndex in PartyHappyCnt_Dict:
			print 'GE_EXC, repeat happyIndex %s in PartyHappyCnt_Dict' % PH.happyIndex
		PartyHappyCnt_Dict[PH.happyIndex] = PH
		
	
class PartyHappyReward(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("KuaFuPartyReward.txt")
	def __init__(self):
		self.needXiqing = int
		self.jiaBinReward = int
		self.xinRenReward = int
	
def LoadPartyHappyReward():
	global PartyHappyReward_Dict
	
	for PHR in PartyHappyReward.ToClassType():
		if PHR.needXiqing in PartyHappyReward_Dict:
			print 'GE_EXC, repeat needXiqing %s in PartyHappyReward_Dict' % PHR.needXiqing
		PartyHappyReward_Dict[PHR.needXiqing] = PHR
	
		
class Qinmi(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("Qinmi.txt")
	def __init__(self):
		self.qinmiLevel = int
		self.needQinmi = int
		self.nextLevel = int
		self.needQinmiGrade = int
		
		self.maxhp = int
		self.attack_p = int
		self.attack_m = int
		self.defense_p = int
		self.defense_m = int
		self.crit = int
		self.critpress = int
		self.parry = int
		self.puncture = int
		
	def InitProperty(self):
		#初始化属性字典
		self.p_dict = {}
		self.p_dict[PropertyEnum.maxhp] = self.maxhp
		self.p_dict[PropertyEnum.attack_p] = self.attack_p
		self.p_dict[PropertyEnum.defense_p] = self.defense_p
		self.p_dict[PropertyEnum.attack_m] = self.attack_m
		self.p_dict[PropertyEnum.defense_m] = self.defense_m
		self.p_dict[PropertyEnum.crit] = self.crit
		self.p_dict[PropertyEnum.critpress] = self.critpress
		self.p_dict[PropertyEnum.parry] = self.parry
		self.p_dict[PropertyEnum.puncture] = self.puncture
	
def LoadQinmi():
	global Qinmi_Dict
	
	for QM in Qinmi.ToClassType():
		if QM.qinmiLevel in Qinmi_Dict:
			print 'GE_EXC, repeat qinmiLevel %s in Qinmi_Dict' % QM.qinmiLevel
			continue
		QM.InitProperty()
		Qinmi_Dict[QM.qinmiLevel] = QM
	
class QinmiGrade(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("QinmiGrade.txt")
	def __init__(self):
		self.qinmiGrade = int
		self.needRoleLevel = int
		self.needQinmi = int
		self.needQinmiLevel = int
		self.maxLevel = int
		
		self.maxhp = int
		self.attack_p = int
		self.attack_m = int
		self.defense_p = int
		self.defense_m = int
		self.crit = int
		self.critpress = int
		self.parry = int
		self.puncture = int
		
		self.titleId = int
		
	def InitProperty(self):
		#初始化属性字典
		self.p_dict = {}
		self.p_dict[PropertyEnum.maxhp] = self.maxhp
		self.p_dict[PropertyEnum.attack_p] = self.attack_p
		self.p_dict[PropertyEnum.defense_p] = self.defense_p
		self.p_dict[PropertyEnum.attack_m] = self.attack_m
		self.p_dict[PropertyEnum.defense_m] = self.defense_m
		self.p_dict[PropertyEnum.crit] = self.crit
		self.p_dict[PropertyEnum.critpress] = self.critpress
		self.p_dict[PropertyEnum.parry] = self.parry
		self.p_dict[PropertyEnum.puncture] = self.puncture
	
def LoadQinmiGrade():
	global QinmiGrade_Dict, QinmiTitleSet
	
	for QMG in QinmiGrade.ToClassType():
		if QMG.qinmiGrade in QinmiGrade_Dict:
			print 'GE_EXC, repeat qinmiGrade %s in QinmiGrade_Dict' % QMG.qinmiGrade
			continue
		QMG.InitProperty()
		QinmiGrade_Dict[QMG.qinmiGrade] = QMG
		
		QinmiTitleSet.add(QMG.titleId)
		
		if QMG.titleId in QinmiTitleIdToGrade:
			print 'GE_EXC, repeat qinmi title id %s in QinmiTitleIdToGrade' % QMG.titleId
			continue
		
		QinmiTitleIdToGrade[QMG.titleId] = QMG.qinmiGrade
	
class MarryTimeConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("MarryTime.txt")
	def __init__(self):
		self.index = int						#时间档索引
		self.beginTime = eval					#开始时间
		self.endTime = eval						#结束时间
		
class MarryGradeConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("MarryGrade.txt")
	def __init__(self):
		self.index = int						#婚礼档次索引
		self.needBindRMB = self.GetIntByString	#需要的魔晶
		self.needRMB = self.GetIntByString		#需要的神石
		self.time = int							#持续时间
		self.timeList = eval					#可选的时间档
		self.yanhuaCnt = int					#烟花数量
		self.biaobaiCnt = int					#表白次数
		self.libaoCnt = int						#礼包个数
		self.maxCnt = int						#婚礼最大容纳人数
		self.itemReward = int					#婚礼完成后奖励coding
		self.skillID = int						#夫妻技能ID
		
class MarryLibaoConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("MarryLibao.txt")
	def __init__(self):
		self.index = int						#婚礼礼包索引
		self.needRMB = int						#需要的神石
		self.libaoCnt = int						#礼包个数
	
class WeddingRingCofig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("WeddingRing.txt")
	def __init__(self):
		self.weddingRingID = int					#婚戒ID
		self.critRate = int							#暴击概率
		self.maxExp = int							#最大经验值
		self.addExp = int							#每次增加经验
		self.nextID = int							#下一阶ID
		self.isUpGrade = int						#是否进阶（大进阶）
		self.activeRingSoul = self.GetIntByString	#激活的婚戒戒灵ID
		self.upNeedLevel = int						#升阶需要的角色等级
		
		self.maxhp = int
		self.attack_p = int
		self.attack_m = int
		self.defense_p = int
		self.defense_m = int
		self.crit = int
		self.critpress = int
		self.parry = int
		self.puncture = int
	
	def InitProperty(self):
		#初始化属性字典
		self.p_dict = {}
		self.p_dict[PropertyEnum.maxhp] = self.maxhp
		self.p_dict[PropertyEnum.attack_p] = self.attack_p
		self.p_dict[PropertyEnum.defense_p] = self.defense_p
		self.p_dict[PropertyEnum.attack_m] = self.attack_m
		self.p_dict[PropertyEnum.defense_m] = self.defense_m
		self.p_dict[PropertyEnum.crit] = self.crit
		self.p_dict[PropertyEnum.critpress] = self.critpress
		self.p_dict[PropertyEnum.parry] = self.parry
		self.p_dict[PropertyEnum.puncture] = self.puncture
		
	def InitCrit(self):
		#初始化暴击概率
		self.critTrue = Random.RandomRate()
		self.critTrue.AddRandomItem(self.critRate, 1)
		self.critTrue.AddRandomItem(10000 - self.critRate, 0)
		
class WeddingRingSoulConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("WeddingRingSoul.txt")
	def __init__(self):
		self.index = int					#戒灵ID索引
		self.proCnt = int					#属性条数
		self.proEnumList = eval				#属性枚举列表
		self.ChushiMax = int				#初始最大星级
		
		self.starRate1 = int				#一星概率
		self.starRate2 = int				#二星概率
		self.starRate3 = int				#三星概率
		self.starRate4 = int				#四星概率
		self.starRate5 = int				#五星概率
		self.starRate6 = int				#六星概率
		self.starRate7 = int				#七星概率
		self.starRate8 = int				#八星概率
		self.starRate9 = int				#九星概率
		self.starRate10 = int				#十星概率
		self.starRate11 = int				#极品概率
		
	def InitRandom(self):
		#初始化随机星级概率
		self.randomStar = Random.RandomRate()
		self.randomStar.AddRandomItem(self.starRate1, 1)
		self.randomStar.AddRandomItem(self.starRate2, 2)
		self.randomStar.AddRandomItem(self.starRate3, 3)
		self.randomStar.AddRandomItem(self.starRate4, 4)
		self.randomStar.AddRandomItem(self.starRate5, 5)
		self.randomStar.AddRandomItem(self.starRate6, 6)
		self.randomStar.AddRandomItem(self.starRate7, 7)
		self.randomStar.AddRandomItem(self.starRate8, 8)
		self.randomStar.AddRandomItem(self.starRate9, 9)
		self.randomStar.AddRandomItem(self.starRate10, 10)
		self.randomStar.AddRandomItem(self.starRate11, 11)
		
	def randomList(self, cnt):
		#随机数量
		return self.randomStar.RandomMany(cnt)
	
class WeddingRingSoulPMConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("WeddingRingSoulPM.txt")
	def __init__(self):
		self.proEnum = int				#属性枚举
		self.maxValue = int				#最大值
	
class WeddingRingSoulRConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("WeddingRingSoulR.txt")
	def __init__(self):
		self.star = int					#星级
		self.randomRange = eval			#属性百分百范围
	
class WeddingRingSkillConfig(TabFile.TabLine):
	FilePath = MW_FILE_FOLDER_PATH.FilePath("WeddingRingSkill.txt")
	def __init__(self):
		self.skillId = int
		self.activeGrade = self.GetIntByString
		self.singleRingNeedPro = self.GetEvalByString
		self.allRingNeedPro = self.GetEvalByString
		self.gradeAct = self.GetIntByString
		
		self.maxhp = int
		self.attack_p = int
		self.attack_m = int
		self.defense_p = int
		self.defense_m = int
		self.crit = int
		self.critpress = int
		self.parry = int
		self.puncture = int
		
	def InitProperty(self):
		#初始化属性字典
		self.p_dict = {}
		self.p_dict[PropertyEnum.maxhp] = self.maxhp
		self.p_dict[PropertyEnum.attack_p] = self.attack_p
		self.p_dict[PropertyEnum.defense_p] = self.defense_p
		self.p_dict[PropertyEnum.attack_m] = self.attack_m
		self.p_dict[PropertyEnum.defense_m] = self.defense_m
		self.p_dict[PropertyEnum.crit] = self.crit
		self.p_dict[PropertyEnum.critpress] = self.critpress
		self.p_dict[PropertyEnum.parry] = self.parry
		self.p_dict[PropertyEnum.puncture] = self.puncture
	
def LoadWeddingRingSkillConfig():
	global WeddingIDAct_Dict
	global WeddingSingleProAct_Dict
	global WeddingMultiProAct_Dict
	global WeddingSkill_Dict
	global WeddingGradeAct_Dict
	
	for WRS in WeddingRingSkillConfig.ToClassType():
		if WRS.skillId in WeddingSkill_Dict:
			print "GE_EXC, repeat skillId (%s) in WeddingSkill_Dict" % WRS.skillId
			continue
		WRS.InitProperty()
		WeddingSkill_Dict[WRS.skillId] = WRS
		
		if WRS.gradeAct:
			if WRS.skillId in WeddingGradeAct_Dict:
				print "GE_EXC, repeat skillId (%s) in WeddingGradeAct_Dict" % WRS.skillId
				continue
			WeddingGradeAct_Dict[WRS.skillId] = WRS
			continue
		if WRS.activeGrade:
			if WRS.skillId in WeddingIDAct_Dict:
				print "GE_EXC, repeat skillId (%s) in weddingRingIDAct" % WRS.skillId
				continue
			WeddingIDAct_Dict[WRS.skillId] = WRS
			continue
		if WRS.singleRingNeedPro:
			if WRS.skillId in WeddingSingleProAct_Dict:
				print "GE_EXC, repeat skillId (%s) in WeddingSingleProAct_Dict" % WRS.skillId
				continue
			WeddingSingleProAct_Dict[WRS.skillId] = WRS
			continue
		if WRS.allRingNeedPro:
			if WRS.skillId in WeddingMultiProAct_Dict:
				print "GE_EXC, repeat skillId (%s) in WeddingMultiProAct_Dict" % WRS.skillId
				continue
			WeddingMultiProAct_Dict[WRS.skillId] = WRS
			
def LoadMarryTimeConfig():
	global MarryTime_Dict
	for MT in MarryTimeConfig.ToClassType():
		if MT.index in MarryTime_Dict:
			print "GE_EXC, repeat index (%s) in MarryTime_Dict" % MT.index
			continue
		MarryTime_Dict[MT.index] = MT
	
def LoadMarryGradeConfig():
	global MarryGrade_Dict
	for MG in MarryGradeConfig.ToClassType():
		if MG.index in MarryGrade_Dict:
			print "GE_EXC, repeat index (%s) in MarryGrade_Dict" % MG.index
			continue
		MarryGrade_Dict[MG.index] = MG

def LoadMarryLibaoConfig():
	global MarryLibao_Dict
	for ML in MarryLibaoConfig.ToClassType():
		if ML.index in MarryLibao_Dict:
			print "GE_EXC, repeat index (%s) in MarryLibao_Dict" % ML.index
			continue
		MarryLibao_Dict[ML.index] = ML
	
def LoadWeddingRingConfig():
	global WeddingRing_Dict
	for WR in WeddingRingCofig.ToClassType():
		if WR.weddingRingID in WeddingRing_Dict:
			print "GE_EXC, repeat weddingRingID (%s) in WeddingRing_Dict" % WR.weddingRingID
			continue
		WR.InitProperty()
		WR.InitCrit()
		WeddingRing_Dict[WR.weddingRingID] = WR
		
def LoadWeddingRingSoulConfig():
	global WeddingRingSoul_Dict
	for WRS in WeddingRingSoulConfig.ToClassType():
		if WRS.index in WeddingRingSoul_Dict:
			print "GE_EXC, repeat index (%s) in WeddingRingSoul_Dict" % WRS.index
			continue
		WRS.InitRandom()
		WeddingRingSoul_Dict[WRS.index] = WRS
		
def LoadWeddingRingSoulPMConfig():
	global WeddingRingSoulPM_Dict
	for WRSPM in WeddingRingSoulPMConfig.ToClassType():
		if WRSPM.proEnum in WeddingRingSoulPM_Dict:
			print "GE_EXC, repeat proEnum (%s) in WeddingRingSoulPM_Dict" % WRSPM.proEnum
			continue
		WeddingRingSoulPM_Dict[WRSPM.proEnum] = WRSPM.maxValue
	
def LoadWeddingRingSoulPConfig():
	global WeddingRingSoulP_Dict
	for WRSP in WeddingRingSoulRConfig.ToClassType():
		if WRSP.star in WeddingRingSoulP_Dict:
			print "GE_EXC, repeat star (%s) in WeddingRingSoulP_Dict" % WRSP.star
			continue
		WeddingRingSoulP_Dict[WRSP.star] = WRSP.randomRange
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMarryTimeConfig()
		LoadMarryGradeConfig()
		LoadMarryLibaoConfig()
		LoadWeddingRingConfig()
		LoadWeddingRingSkillConfig()
		LoadWeddingRingSoulConfig()
		LoadWeddingRingSoulPMConfig()
		LoadWeddingRingSoulPConfig()
		
		LoadPartyGrade()
		LoadPartyCandyGrade()
		LoadPartyBless()
		LoadPartyHappy()
		LoadPartyHappyReward()
		
		LoadQinmi()
		LoadQinmiGrade()
		LoadHoneymoonGrade()
		LoadRingBase()
		LoadRoyalGuardSay()
		LoadRoyalGuardSayRandom()
		LoadPartySTConfig()
		