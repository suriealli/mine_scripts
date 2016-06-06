#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FindBack.FindBackConfig")
#===============================================================================
# 找回系统配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.FindBack import FindBackDefine, FindBackBase
from Game.Role.Data import EnumInt16


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("FindBack")

	FindBackConfig_Dict = {}#找回基础配置
	FindBackMoney_Dict = {}#金币找回需要的金币(按照角色等级配置)
	FindBackReward_RMB_Dict = {}#神石找回奖励 vipType - rolelevel - cfg
	FindBackReward_BindRMB_Dict = {}#魔晶找回奖励
	FindBackReward_Money_Dict = {}#金币找回奖励
	
	#特殊体力找回
	TiLiFBRMB = None
	TiLiFBBindRMB = None
	TiLiFBMoney = None
	
	#特殊找回
	#副本
	FB_FBConfig_Dict = {}
	#英灵神殿
	FB_HTConfig_Dict = {}


######################################################################
def GetVIPType(viplevel):
	if viplevel >= 4 and viplevel < 7:
		return 1
	elif viplevel >= 7:
		return 2
	return 0

def GetFBFBConfig(role, viptype):
	fbdict = FB_FBConfig_Dict.get(viptype)
	if not fbdict:
		return None
	return fbdict.get(role.GetI16(EnumInt16.FB_Active_ID))

def GetFBHTConfig(role, viptype):
	fbdict = FB_HTConfig_Dict.get(viptype)
	if not fbdict:
		return None
	return fbdict.get(role.GetI16(EnumInt16.HeroTempleMaxIndex))

def GetRMBReward(role, index = 0):
	viptype = GetVIPType(role.GetVIP())
	if index == FindBackDefine.TILIFB:
		return TiLiFBRMB
	elif index == FindBackDefine.FBFB:
		return GetFBFBConfig(role, viptype)
	elif index == FindBackDefine.HTFB:
		return GetFBHTConfig(role, viptype)
		
	roleleveldict = FindBackReward_RMB_Dict.get(viptype)
	if not roleleveldict:
		return None
	return roleleveldict.get(role.GetLevel())


def GetBindRMBReward(role, index = 0):
	if index == FindBackDefine.TILIFB:
		return TiLiFBBindRMB
	elif index == FindBackDefine.FBFB:
		return GetFBFBConfig(role, 1)
	elif index == FindBackDefine.HTFB:
		return GetFBHTConfig(role, 1)
	
	return FindBackReward_BindRMB_Dict.get(role.GetLevel())

def GetMoneyReward(role, index = 0):
	if index == FindBackDefine.TILIFB:
		return TiLiFBMoney
	elif index == FindBackDefine.FBFB:
		return GetFBFBConfig(role, 1)
	elif index == FindBackDefine.HTFB:
		return GetFBHTConfig(role, 1)
	
	return FindBackReward_Money_Dict.get(role.GetLevel())




#########################################################################################
#基本配置
class FindBackConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBack.txt")
	def __init__(self):
		self.fIndex = int
		self.name = str
		self.maxTimes = int
		self.sec = int
		self.needUnbindRMB = int
		self.needBindRMB = int
	
	#体力找回特殊，5体力算一次
	def NeedUnbindRMB(self, cnt):
		if self.fIndex == FindBackDefine.TILIFB:
			if cnt % 5 > 0:
				cnt = cnt / 5 + 1
			else:
				cnt = cnt / 5
		return self.needUnbindRMB * cnt
	
	def NeedBindRMB(self, cnt):
		if self.fIndex == FindBackDefine.TILIFB:
			if cnt % 5 > 0:
				cnt = cnt / 5 + 1
			else:
				cnt = cnt / 5
		return self.needBindRMB * cnt
	

class FindBackMoneyConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBackNeedMoney.txt")
	def __init__(self):
		self.fIndex = int
		self.level = int
		self.needMoney = int

	def NeedMoney(self, cnt):
		if self.fIndex == FindBackDefine.TILIFB:
			if cnt % 5 > 0:
				cnt = cnt / 5 + 1
			else:
				cnt = cnt / 5
		return self.needMoney * cnt

#########################################################################################
#特殊体力找回的模拟配置
class TiLiFBRMBConfig(object):
	def __init__(self):
		pass
	def RewardRole(self, role, index, cnt, rewardtype = 0):
		if role.GetVIP() < 4:
			print "GE_EXC, TiLiFBRMBConfig role.GetVIP() < 4"
			cnt = 0
		elif role.GetVIP() <= 6:
			cnt = int(cnt * 0.9)
		role.IncTiLi(cnt)
		return (0, 0, 0, 0, {}, cnt)

class TiLiFBBindRMBConfig(object):
	def __init__(self):
		pass
	def RewardRole(self, role, index, cnt, rewardtype = 0):
		cnt = int(cnt * 0.7)
		role.IncTiLi(cnt)
		return (0, 0, 0, 0, {}, cnt)


class TiLiFBMoneyConfig(object):
	def __init__(self):
		pass
	def RewardRole(self, role, index, cnt, rewardtype = 0):
		cnt = int(cnt * 0.5)
		role.IncTiLi(cnt)
		return (0, 0, 0, 0, {}, cnt)

#########################################################################################



#神石找回
class FindBackReward_RMB(FindBackBase.FindBackReward_Base):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBackReward_RMB.txt")
	def __init__(self):
		self.vipType = int
		FindBackBase.FindBackReward_Base.__init__(self)
		
#魔晶找回
class FindBackReward_BindRMB(FindBackBase.FindBackReward_Base):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBackReward_BindRMB.txt")
	def __init__(self):
		FindBackBase.FindBackReward_Base.__init__(self)
#金币
class FindBackReward_Money(FindBackBase.FindBackReward_Base):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBackReward_Money.txt")
	def __init__(self):
		FindBackBase.FindBackReward_Base.__init__(self)



class FB_FBConfig(FindBackBase.FindBackOther_Base):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBackFB.txt")
	def __init__(self):
		FindBackBase.FindBackOther_Base.__init__(self)
		self.FBID = int

class FB_HTConfig(FindBackBase.FindBackOther_Base):
	FilePath = FILE_FOLDER_PATH.FilePath("FindBackHT.txt")
	def __init__(self):
		FindBackBase.FindBackOther_Base.__init__(self)
		self.htIndex = int


def LoadFindBackConfig():
	global FindBackConfig_Dict
	for fbcfg in FindBackConfig.ToClassType():
		FindBackConfig_Dict[fbcfg.fIndex] = fbcfg
	global TiLiFBRMB, TiLiFBBindRMB, TiLiFBMoney
	TiLiFBRMB = TiLiFBRMBConfig()
	TiLiFBBindRMB = TiLiFBBindRMBConfig()
	TiLiFBMoney = TiLiFBMoneyConfig()


def QQChangeConfig():
	#国服，修改找回系统答题找回最大次数为 0
	global FindBackConfig_Dict
	from Game.FindBack.FindBackDefine import QNAFB
	fbObj = FindBackConfig_Dict.get(QNAFB)
	if not fbObj:
		return
	fbObj.maxTimes = 0


def LoadFindBackMoneyConfig():
	global FindBackConfig_Dict
	for fbcfg in FindBackMoneyConfig.ToClassType():
		if fbcfg.fIndex not in FindBackMoney_Dict:
			FindBackMoney_Dict[fbcfg.fIndex] = {}
		FindBackMoney_Dict[fbcfg.fIndex][fbcfg.level] = fbcfg


def LoadFindBackReward_RMB():
	global FindBackReward_RMB_Dict
	for fbcfg in FindBackReward_RMB.ToClassType():
		if fbcfg.vipType not in FindBackReward_RMB_Dict:
			FindBackReward_RMB_Dict[fbcfg.vipType] = {}
		FindBackReward_RMB_Dict[fbcfg.vipType][fbcfg.level] = fbcfg


def LoadFindBackReward_BindRMB_Dict():
	global FindBackReward_BindRMB_Dict
	for fbcfg in FindBackReward_BindRMB.ToClassType():
		FindBackReward_BindRMB_Dict[fbcfg.level] = fbcfg


def LoadFindBackReward_Money_Dict():
	global FindBackReward_Money_Dict
	for fbcfg in FindBackReward_Money.ToClassType():
		FindBackReward_Money_Dict[fbcfg.level] = fbcfg


def LoadFindBackReward_FB():
	global FB_FBConfig_Dict
	for fbcfg in FB_FBConfig.ToClassType():
		if fbcfg.vipType not in FB_FBConfig_Dict:
			FB_FBConfig_Dict[fbcfg.vipType] = {}
		FB_FBConfig_Dict[fbcfg.vipType][fbcfg.FBID] = fbcfg


def LoadFindBackReward_HT():
	global FB_HTConfig_Dict
	for fbcfg in FB_HTConfig.ToClassType():
		if fbcfg.vipType not in FB_HTConfig_Dict:
			FB_HTConfig_Dict[fbcfg.vipType] = {}
		FB_HTConfig_Dict[fbcfg.vipType][fbcfg.htIndex] = fbcfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadFindBackConfig()
		LoadFindBackMoneyConfig()
		LoadFindBackReward_RMB()
		LoadFindBackReward_BindRMB_Dict()
		LoadFindBackReward_Money_Dict()
		
		LoadFindBackReward_FB()
		LoadFindBackReward_HT()
	
	
	if Environment.EnvIsQQ() or Environment.EnvIsQQUnion() or Environment.EnvIsFT():
		QQChangeConfig()
