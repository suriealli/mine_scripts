#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ThanksGiving.ThanksGivingConfig")
#===============================================================================
# 狂欢感恩节配置
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment
from Util import Random
import copy
from ComplexServer.Plug import Switch

NOMAL_REWARD = 1	#物品奖励
CDK_REWARD = 2		#CDK奖励

QQHALL_RECHARGEREWARD = 1	#大厅充值奖励次数
QQHALL_INVITEFRIEND = 2		#大厅邀请好友奖励次数
QQHALL_ONLINEREWARD = 3		#大厅在线奖励次数
OTHERS_RECHARGEREWARD = 4	#非大厅的充值奖励次数

if "_HasLoad" not in dir():
	TG_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TG_FILE_FOLDER_PATH.AppendPath("ThanksGiving")
	
	TG_OLINEREWARD_DICT = {}	#在线赢大礼配置{rewardIndex:cfg,}
	
	TG_RECHARGEREWARD_ITEMS_1_DICT = {}		#第一套充值送豪礼物品奖励配置{rangeId:randomer,}
	TG_RECHARGEREWARD_ITEMS_2_DICT = {}		#第二套充值送豪礼物品奖励配置{rangeId:randomer,}
	TG_RECHARGEREWARD_ITEMS_3_DICT = {}		#第三套充值送豪礼物品奖励配置{rangeId:randomer,}
	TG_RECHARGEREWARD_ITEMS_4_DICT = {}		#第四套充值送豪礼物品奖励配置{rangeId:randomer,}
	TG_RECHARGEREWARD_ITEMS_BASE_DICT = {}	#所有物品奖励配置{rewardId:cfg,}
	
	TG_RECHARGEREWARD_CDK_DICT = {}			#充值送豪礼CDK奖励配置{serverId:{rewardId:cfg,},}
	TG_RECHARGEREWARD_CDK_BASE_DICT = {}	#CDK奖励基本配置{rewardId:cfg,}
	TG_RECHARGEREWARD_RANGE2ID_DICT = {}	#充值送豪礼 奖励等级区段-区段ID关联{rangeId:[levelDown,levelUp],}
	TG_RECHARGEREWARD_TIMES_DICT = {}		#充值送豪礼次数奖励配置{rewardId:cfg,}
	
	TG_RECHARGEREWARD_CDKRATE_DICT = {}				#CDK抽奖概率控制配置
	TG_RECHARGEREWARD_CDKRATE_RANGE2ID_DICT = {}	#CDK配置等级区段-区段ID关联{rangeId:[levelDown,levelUp],}
	
	CutTurkey_Dict = {}			#切火鸡
	CutTurkeyQ_Dict = {}		#切火鸡题库
	CutTurkeyLevel_List = []	#切火鸡等级最小等级区间列表(有序)
	
class OnlineReward(TabFile.TabLine):
	'''
	在线赢大礼 配置
	'''
	FilePath = TG_FILE_FOLDER_PATH.FilePath("OnlineReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needMinutes = int 
		self.rewardItems = self.GetEvalByString
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardTimes = int	#大厅登陆的额外奖励抽奖次数

class RechargeRewardItems(TabFile.TabLine):
	'''
	充值送豪礼物品奖励配置
	'''
	FilePath = TG_FILE_FOLDER_PATH.FilePath("RechargeRewardItems.txt")
	def __init__(self):
		self.rewardId = int 
		self.rewardType = int
		self.rangeId = int 
		self.levelRange = self.GetEvalByString
		self.itemIndex = int 
		self.rateValue = int
		self.item = self.GetEvalByString
		self.isPrecious = int
	
class RechargeRewardCDK(TabFile.TabLine):
	'''
	充值送豪礼CDK奖励配置
	'''
	FilePath = TG_FILE_FOLDER_PATH.FilePath("RechargeRewardCDK.txt")
	def __init__(self):
		self.rewardId = int 
		self.serverId = int 
		self.cdkey = str	
		self.isPrecious = int

class RechargeRewardTimes(TabFile.TabLine):
	'''
	充值送豪礼奖励次数配置
	'''
	FilePath = TG_FILE_FOLDER_PATH.FilePath("RechargeRewardTimes.txt")
	def __init__(self):
		self.rewardIndex = int
		self.needRMBOnce = int
		self.rewardTimes = int

class CDKRateControl(TabFile.TabLine):
	'''
	CDK抽奖概率配置
	'''
	FilePath = TG_FILE_FOLDER_PATH.FilePath("CDKRateControl.txt")
	def __init__(self):
		self.rewardType = int 
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.rateValue = int 

def GetLocalServerCDKRewardIdSet():
	'''
	返回本服能用的所有CDK对应rewardId 
	@return: 
	'''
	localServerIDs = Switch.LocalServerIDs
	localServerCDKRewardIdSet = set()
	for serverId, rewardCDKDict in TG_RECHARGEREWARD_CDK_DICT.iteritems():
		if serverId not in localServerIDs:
			continue
		localServerCDKRewardIdSet = localServerCDKRewardIdSet.union(rewardCDKDict.keys())
	
	return localServerCDKRewardIdSet

def GetRewardRandomerByTypeAndLevel(rewardType = 1, roleLevel = 1):
	'''
	根据等级随机奖励
	@return (rewardId, rangeId, itemIndex,isPrecious, coding, cnt)
	'''
	tmpRangeId = 0
	for rangeId, levelRange in TG_RECHARGEREWARD_RANGE2ID_DICT.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	randomer = None
	if rewardType == QQHALL_RECHARGEREWARD:
		randomer = TG_RECHARGEREWARD_ITEMS_1_DICT.get(tmpRangeId)
	elif rewardType == QQHALL_INVITEFRIEND:
		randomer = TG_RECHARGEREWARD_ITEMS_2_DICT.get(tmpRangeId)
	elif rewardType == QQHALL_ONLINEREWARD:
		randomer = TG_RECHARGEREWARD_ITEMS_3_DICT.get(tmpRangeId)
	elif rewardType == OTHERS_RECHARGEREWARD:
		randomer = TG_RECHARGEREWARD_ITEMS_4_DICT.get(tmpRangeId)
	else:
		print "GE_EXC,error rewardType(%s) on GetRewardRandomerByTypeAndLevel" % rewardType
		return None
	
	if not randomer:
		print "GE_EXC,can not get randomer by rangeId(%s),roleLevel(%s),rewardType(%s)" % (tmpRangeId, roleLevel, rewardType)
		return None
	
	#返回独立的randomer 防止调用逻辑增加CDK随机项导致配置错乱
	return copy.deepcopy(randomer)	

def GetCDKRateByTypeAndLevel(rewardType, roleLevel):
	'''
	根据抽奖类型和玩家等级获取CDK抽奖概率
	@return: 找到返回对应概率 没有返回0 
	'''
	tmpRangeId = 0
	for rangeId, levelRange in TG_RECHARGEREWARD_CDKRATE_RANGE2ID_DICT.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	rateCfgDict = TG_RECHARGEREWARD_CDKRATE_DICT.get(rewardType)
	if not rateCfgDict:
		print "GE_EXC, error rewardType(%s) can not get rateCfgDict" % rewardType
		return 0
	
	rateCfg = rateCfgDict.get(tmpRangeId)
	if not rateCfg:
		print "GE_EXC, error tmpRangeId(%s) can not get rateCfg" % tmpRangeId
		return 0
	
	return rateCfg.rateValue

def LoadOnlineReward():
	global TG_OLINEREWARD_DICT
	for cfg in OnlineReward.ToClassType():
		if cfg.rewardIndex in TG_OLINEREWARD_DICT:
			print "GE_EXC,repeat rewardIndex(%s) in TG_OLINEREWARD_DICT" % cfg.rewardIndex
		TG_OLINEREWARD_DICT[cfg.rewardIndex] = cfg

def LoadRechargeRewardItems():
	global TG_RECHARGEREWARD_ITEMS_1_DICT
	global TG_RECHARGEREWARD_ITEMS_2_DICT
	global TG_RECHARGEREWARD_ITEMS_3_DICT
	global TG_RECHARGEREWARD_ITEMS_4_DICT
	global TG_RECHARGEREWARD_RANGE2ID_DICT
	global TG_RECHARGEREWARD_ITEMS_BASE_DICT
	for cfg in RechargeRewardItems.ToClassType():
		rewardId = cfg.rewardId
		rewardType = cfg.rewardType
		rangeId = cfg.rangeId
		itemIndex = cfg.itemIndex
		isPrecious = cfg.isPrecious
		rateValue = cfg.rateValue
		coding, cnt = cfg.item
		#等级区段ID-等级区段关联
		TG_RECHARGEREWARD_RANGE2ID_DICT[rangeId] = cfg.levelRange	
		
		#所有物品奖励基本配置
		if rewardId in TG_RECHARGEREWARD_ITEMS_BASE_DICT:
			print "GE_EXC,repeat rewardId(%s) in recharge reward items" % rewardId
		TG_RECHARGEREWARD_ITEMS_BASE_DICT[rewardId] = cfg
			
		#构建每个等级区段奖励随机器randomer
		if rewardType == QQHALL_RECHARGEREWARD:
			#第一套奖励
			if rangeId not in TG_RECHARGEREWARD_ITEMS_1_DICT:
				TG_RECHARGEREWARD_ITEMS_1_DICT[rangeId] = Random.RandomRate()
			TG_RECHARGEREWARD_ITEMS_1_DICT[rangeId].AddRandomItem(rateValue, (NOMAL_REWARD, rewardId, rangeId, itemIndex,isPrecious, coding, cnt))
		elif rewardType == QQHALL_INVITEFRIEND:
			#第二套奖励
			if rangeId not in TG_RECHARGEREWARD_ITEMS_2_DICT:
				TG_RECHARGEREWARD_ITEMS_2_DICT[rangeId] = Random.RandomRate()
			TG_RECHARGEREWARD_ITEMS_2_DICT[rangeId].AddRandomItem(rateValue, (NOMAL_REWARD, rewardId, rangeId, itemIndex,isPrecious, coding, cnt))
		elif rewardType == QQHALL_ONLINEREWARD:
			#第三套奖励
			if rangeId not in TG_RECHARGEREWARD_ITEMS_3_DICT:
				TG_RECHARGEREWARD_ITEMS_3_DICT[rangeId] = Random.RandomRate()
			TG_RECHARGEREWARD_ITEMS_3_DICT[rangeId].AddRandomItem(rateValue, (NOMAL_REWARD, rewardId, rangeId, itemIndex,isPrecious, coding, cnt))
		elif rewardType == OTHERS_RECHARGEREWARD:
			#第四套奖励
			if rangeId not in TG_RECHARGEREWARD_ITEMS_4_DICT:
				TG_RECHARGEREWARD_ITEMS_4_DICT[rangeId] = Random.RandomRate()
			TG_RECHARGEREWARD_ITEMS_4_DICT[rangeId].AddRandomItem(rateValue, (NOMAL_REWARD, rewardId, rangeId, itemIndex,isPrecious, coding, cnt))
		else:
			print "GE_EXC,error rewardType(%s) on LoadRechargeRewardItems" % rewardType

def LoadRechargeRewardCDK():
	global TG_RECHARGEREWARD_CDK_DICT
	global TG_RECHARGEREWARD_CDK_BASE_DICT
	for cfg in RechargeRewardCDK.ToClassType():
		serverId = cfg.serverId
		rewardId = cfg.rewardId
		if serverId not in TG_RECHARGEREWARD_CDK_DICT:
			TG_RECHARGEREWARD_CDK_DICT[serverId] = {}
		rewardDict = TG_RECHARGEREWARD_CDK_DICT[serverId]
		if rewardId in rewardDict:
			print "GE_EXC,repeat rewardId(%s) in serverId(%s) on LoadRechargeRewardCDK" % (rewardId, serverId)
		rewardDict[rewardId] = cfg
		
		if rewardId in TG_RECHARGEREWARD_CDK_BASE_DICT:
			print "GE_EXC,repeat rewardId(%s) in recharge reward CDK" % rewardId
		TG_RECHARGEREWARD_CDK_BASE_DICT[rewardId] = cfg

def LoadRechargeRewardTimes():
	global TG_RECHARGEREWARD_TIMES_DICT
	for cfg in RechargeRewardTimes.ToClassType():
		rewardIndex = cfg.rewardIndex
		if rewardIndex in TG_RECHARGEREWARD_TIMES_DICT:
			print "GE_EXC,repeat rewardIndex(%s) in TG_RECHARGEREWARD_TIMES_DICT" % rewardIndex
		TG_RECHARGEREWARD_TIMES_DICT[rewardIndex] = cfg
	
class CutTurkeyConfig(TabFile.TabLine):
	FilePath = TG_FILE_FOLDER_PATH.FilePath("CutTurkey.txt")
	def __init__(self):
		self.index = int			#火鸡
		self.minLevel = int			#区间最小角色等级
		self.randomRange = eval		#切火鸡随机次数范围
		self.rewardCoding = int		#奖励礼包coding
		self.questionsStore = eval	#题库
	
def LoadCutTurkey():
	global CutTurkey_Dict, CutTurkeyLevel_List
	
	for CTC in CutTurkeyConfig.ToClassType():
		if (CTC.index, CTC.minLevel) in CutTurkey_Dict:
			print 'GE_EXC, repeat index %s, minLevel %s in CutTurkey_Dict' % (CTC.index, CTC.minLevel)
			continue
		CutTurkey_Dict[(CTC.index, CTC.minLevel)] = CTC
		CutTurkeyLevel_List.append(CTC.minLevel)
	CutTurkeyLevel_List = list(set(CutTurkeyLevel_List))
	CutTurkeyLevel_List.sort()
	
class CutTurkeyQAConfig(TabFile.TabLine):
	FilePath = TG_FILE_FOLDER_PATH.FilePath("CutTurkeyQ.txt")
	def __init__(self):
		self.index = int			#题目索引
		self.answer = int			#答案
	
def LoadCutTurkeyQ():
	global CutTurkeyQ_Dict
	
	for CTQ in CutTurkeyQAConfig.ToClassType():
		if CTQ.index in CutTurkeyQ_Dict:
			print 'GE_EXC, repeat index %s in CutTurkeyQ_Dict' % CTQ.index
			continue
		CutTurkeyQ_Dict[CTQ.index] = CTQ
	
		
def LoadCDKRateControl():
	global TG_RECHARGEREWARD_CDKRATE_DICT
	global TG_RECHARGEREWARD_CDKRATE_RANGE2ID_DICT
	for cfg in CDKRateControl.ToClassType():
		rewardType = cfg.rewardType
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		TG_RECHARGEREWARD_CDKRATE_RANGE2ID_DICT[rangeId] = levelRange
		
		if rewardType not in TG_RECHARGEREWARD_CDKRATE_DICT:
			TG_RECHARGEREWARD_CDKRATE_DICT[rewardType] = {}
		rangeDict = TG_RECHARGEREWARD_CDKRATE_DICT[rewardType]
		if rangeId in rangeDict:
			print "GE_EXC, repeat rangeId(%s) in rewardType(%s) " % (rangeId, rewardType)
		rangeDict[rangeId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadOnlineReward()
		LoadRechargeRewardItems()
		LoadRechargeRewardTimes()	
		LoadRechargeRewardCDK()	
		LoadCDKRateControl()		
		LoadCutTurkey()
		LoadCutTurkeyQ()