#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.VIPConfig")
#===============================================================================
# VIP配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

VIP_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
VIP_FILE_FOLDER_PATH.AppendPath("VIP")

if "_HasLoad" not in dir():
	_VIP_BASE = {}
	Cards_Dict = {}
	VIP_REWARD_DICT = {}
	SUPER_VIP_REWARD_DICT = {}
	SUPER_VIP_POINT_SHOP = {}
	SUPER_VIP_TITLE_DICT = {}
	VIP_LIBAO_DICT = {}
	
class VIPBase(TabFile.TabLine):
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("VIPBase.txt")
	def __init__(self):
		self.level = int					#vip等级
		self.growValue = int				#成长值
		self.needExp = int					#超级贵族经验
		self.tili = int						#购买体力次数
		self.gold = int						#偷桃次数
		self.lyTimes = int					#心魔炼狱复活次数
		self.unionFBBuyCnt = int			#公会副本购买次数
		self.heroTempleBuyCnt = int			#英灵神殿购买行动次数
		self.petLuckyDrawCnt = int			#宠物转转乐次数
		self.gve = int						#gve副本购买次数
		self.couplesTimes = int				#情缘副本购买次数
		self.twelevePalaceCnt = int			#勇闯十二宫次数
		self.dragonSoulCnt = int			#神龙聚灵次数
		self.DragonDigCnt = int				#购买巨龙宝藏挖宝次数
		self.DragonLuckyDigCnt = int		#购买巨龙宝藏幸运挖宝次数
		self.UnionExplorePrisonerCnt = int	#公会魔域探秘可抓战俘数量
		self.heroShengdianBuyCnt = int		#英雄圣殿购买行动次数
		
class VipReward(TabFile.TabLine):
	'''
	VIP奖励
	'''
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("VipReward.txt")
	def __init__(self):
		self.index = int
		self.serverReward1 = self.GetEvalByString
		self.gold1 = int
		self.bindRMB1 = int
		self.hero1 = int
		self.tarot1 = int
		self.serverReward2 = self.GetEvalByString
		self.gold2 = int
		self.bindRMB2 = int
		self.hero2 = int
		self.tarot2 = int
		self.reward2RMB = int
		
def LoadVIPBaseConfig():
	global _VIP_BASE
	
	for config in VIPBase.ToClassType():
		if config.level in _VIP_BASE:
			print "GE_EXC repeat key(%s) in _VIP_BASE in LoadVIPBaseConfig" % config.level
			continue
		_VIP_BASE[config.level] = config
	
class CardsConfig(TabFile.TabLine):
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("CardsConfig.txt")
	def __init__(self):
		self.cardID = int			#卡片ID -- 周卡、月卡、半年卡
		self.unbindRMB = int		#购买需要绑定元宝
		self.fanquan = int			#返券
		self.chestCoding = int		#宝箱Coding
		self.time = int				#时效
		

def LoadCardsConfig():
	global Cards_Dict
	for CC in CardsConfig.ToClassType():
		if CC.cardID in Cards_Dict:
			print "GE_EXC, repeat cardID (%s) in Cards_Dict" % CC.cardID
			continue
		Cards_Dict[CC.cardID] = CC
	
class SuperVIPDReward(TabFile.TabLine):
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("SuperVIPDReward.txt")
	def __init__(self):
		self.index = int
		self.needRMB_Q = int
		self.addExp = int
		self.rewards = self.GetEvalByString
		
def LoadSuperVIPDReward():
	global SUPER_VIP_REWARD_DICT
	
	for cfg in SuperVIPDReward.ToClassType():
		if cfg.index in SUPER_VIP_REWARD_DICT:
			print "GE_EXC, repeat index(%s) in LoadSuperVIPDReward" % cfg.index
		SUPER_VIP_REWARD_DICT[cfg.index] = cfg
	
class SuperVIPPointShop(TabFile.TabLine):
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("SuperVIPPointShop.txt")
	def __init__(self):
		self.index = int
		self.needSuperVIP = int
		self.needPoint = int
		self.needRMB_Q = int
		self.needRMB_S = int
		self.timesLimit = int
		self.codingRewards = self.GetEvalByString
		self.talentCard = int
		self.tarotReward = int
	
def LoadSuperVIPPointShop():
	global SUPER_VIP_POINT_SHOP
	
	for cfg in SuperVIPPointShop.ToClassType():
		if cfg.index in SUPER_VIP_POINT_SHOP:
			print "GE_EXC, repeat index(%s) in LoadSuperVIPPointShop" % cfg.index
		SUPER_VIP_POINT_SHOP[cfg.index] = cfg
		
class SuperVIPTitle(TabFile.TabLine):
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("SuperVIPTitle.txt")
	def __init__(self):
		self.titleId = int
		self.needRoleLevel = int
		self.needVIPLevel = int

def LoadSuperVIPTitle():
	global SUPER_VIP_TITLE_DICT
	
	for cfg in SuperVIPTitle.ToClassType():
		if cfg.titleId in SUPER_VIP_TITLE_DICT:
			print "GE_EXC, repeat titleId(%s) in LoadSuperVIPTitle" % cfg.titleId
		SUPER_VIP_TITLE_DICT[cfg.titleId] = cfg
	
def LoadVipRewardConfig():
	global VIP_REWARD_DICT
	
	for cfg in VipReward.ToClassType():
		if cfg.index in VIP_REWARD_DICT:
			print "GE_EXC, repeat index(%s) in VipReward" % cfg.index
		VIP_REWARD_DICT[cfg.index] = cfg
		
class VipLiBao(TabFile.TabLine):
	FilePath = VIP_FILE_FOLDER_PATH.FilePath("VipLibao.txt")
	
	def __init__(self):
		self.coding			= int
		self.costUnbindRMB	= int
		self.hero			= int
		self.tarot			= int
		self.serverReward	= self.GetEvalByString
		self.bindRMB		= int
		self.gold			= int
		self.unbindRMB_S	= int
	
def LoadVipLiBao():
	global VIP_LIBAO_DICT
	
	for cfg in VipLiBao.ToClassType():
		if cfg.coding in VIP_LIBAO_DICT:
			print "GE_EXC,repeat coding(%s) in vipconfig.VIP_LIBAO_DICT" % cfg.coding
		VIP_LIBAO_DICT[cfg.coding] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadVIPBaseConfig()
		LoadCardsConfig()
		LoadVipRewardConfig()
		LoadSuperVIPDReward()
		LoadSuperVIPPointShop()
		LoadSuperVIPTitle()
		LoadVipLiBao()
		