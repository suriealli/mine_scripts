#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQMiniClient.QQMiniClient")
#===============================================================================
# 腾讯微端
#===============================================================================
import cRoleMgr
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt1, EnumDayInt1
from Common.Other import GlobalPrompt


#回流奖励
ROLE_BACK_REWARD = [(27037, 1)]

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QQMiniClient")
	
	
	DayReward_Dict = {}
	
	DL_CFG = None
	RS_CFG = None
	
	S_CFG = None
	
class DayReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DayReward.txt")
	def __init__(self):
		self.level = int
		self.items = self.GetEvalByString

class DownLoad(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DownLoad.txt")
	def __init__(self):
		self.rmb = int
		self.items = self.GetEvalByString

class ReadyStart(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ReadyStart.txt")
	def __init__(self):
		self.rmb = int
		self.items = self.GetEvalByString

class Start(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("Start.txt")
	def __init__(self):
		self.money = int
		self.items = self.GetEvalByString

def LoadDayReward():
	global DayReward_Dict
	for d in DayReward.ToClassType():
		DayReward_Dict[d.level] = d.items

def LoadDownLoad():
	global DL_CFG
	for d in DownLoad.ToClassType():
		DL_CFG = d


def LoadReadyStart():
	global RS_CFG
	for d in ReadyStart.ToClassType():
		RS_CFG = d
		
def LoadStart():
	global S_CFG
	for d in Start.ToClassType():
		S_CFG = d




def RequestQQMiniClientDownLoadRewrad(role, msg):
	'''
	请求领取QQ微端下载礼包
	@param role:
	@param msg:
	'''
	#if not role.GetTI64(EnumTempInt64.QQMiniClient):
	#	return
	if role.GetI1(EnumInt1.QQMiniClientDownLoadReward):
		return
	
	global DL_CFG
	with Tra_QQMiniClientDownLoadRewrad:
		role.SetI1(EnumInt1.QQMiniClientDownLoadReward, 1)
		tips = GlobalPrompt.Reward_Tips
		role.IncBindRMB(DL_CFG.rmb)
		tips  += GlobalPrompt.BindRMB_Tips % DL_CFG.rmb
		for itemCoding, itemCnt in DL_CFG.items:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		role.Msg(2, 0, tips)
			
def RequestQQMiniClientStartRewrad(role, msg):
	'''
	请求领取QQ微端设置开机启动礼包
	@param role:
	@param msg:
	'''
	#if not role.GetTI64(EnumTempInt64.QQMiniClient):
	#	return
	
	if role.GetDI1(EnumDayInt1.QQMiniClientStartRewrad):
		return
	global S_CFG
	with Tra_QQMiniClientStartRewrad:
		role.SetDI1(EnumDayInt1.QQMiniClientStartRewrad, 1)
		tips = GlobalPrompt.Reward_Tips
		role.IncMoney(S_CFG.money)
		tips += GlobalPrompt.Money_Tips % S_CFG.money
		for itemCoding, itemCnt in S_CFG.items:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		role.Msg(2, 0, tips)
	

def RequestQQMiniClientReadyStartRewrad(role, msg):
	'''
	请求领取QQ微端已经设置好的开机启动礼包
	@param role:
	@param msg:
	'''
	#if not role.GetTI64(EnumTempInt64.QQMiniClient):
	#	return
	if role.GetDI1(EnumDayInt1.QQMiniClientReadyStartRewrad):
		return
	global RS_CFG
	with Tra_QQMiniClientReadyStartRewrad:
		role.SetDI1(EnumDayInt1.QQMiniClientReadyStartRewrad, 1)
		tips = GlobalPrompt.Reward_Tips
		role.IncBindRMB(RS_CFG.rmb)
		tips += GlobalPrompt.BindRMB_Tips % RS_CFG.rmb
		for itemCoding, itemCnt in RS_CFG.items:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		role.Msg(2, 0, tips)
		
def RequestQQMiniClientDayRewrad(role, msg):
	'''
	请求领取QQ微端每日登录礼包
	@param role:
	@param msg:
	'''
	#if not role.GetTI64(EnumTempInt64.QQMiniClient):
	#	return
	
	if role.GetDI1(EnumDayInt1.QQMiniClientDayReward):
		return
	global DayReward_Dict
	
	items = DayReward_Dict.get(role.GetLevel())
	if not items:
		return
	
	with Tra_QQMiniClientDayRewrad:
		role.SetDI1(EnumDayInt1.QQMiniClientDayReward, 1)
		tips = GlobalPrompt.Reward_Tips
		for itemCoding, itemCnt in items:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		role.Msg(2, 0, tips)

def RequestQQMiniClientRoleBackRewrad(role, param):
	'''
	请求领取QQ微端回流礼包
	@param role:
	@param param:
	'''
	if role.GetI1(EnumInt1.QQMiniRoleBacklibao):
		return
	
	with Tra_QQMiniClientRoleBackRewrad:
		role.SetI1(EnumInt1.QQMiniRoleBacklibao, 1)
		tips = GlobalPrompt.Reward_Tips
		for reward in ROLE_BACK_REWARD:
			role.AddItem(*reward)
			tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
		role.Msg(2, 0, tips)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and not Environment.IsCross:
		
		LoadStart()
		LoadReadyStart()
		LoadDownLoad()
		LoadDayReward()
		
		
		Tra_QQMiniClientDownLoadRewrad = AutoLog.AutoTransaction("Tra_QQMiniClientDownLoadRewrad", "QQ微端下载礼包")
		Tra_QQMiniClientStartRewrad = AutoLog.AutoTransaction("Tra_QQMiniClientStartRewrad", "QQ微端开机启动礼包")
		Tra_QQMiniClientReadyStartRewrad = AutoLog.AutoTransaction("Tra_QQMiniClientReadyStartRewrad", "QQ微端已经设置好的开机启动礼包")
		Tra_QQMiniClientDayRewrad = AutoLog.AutoTransaction("Tra_QQMiniClientDayRewrad", "QQ微端每日登录礼包")
		Tra_QQMiniClientRoleBackRewrad = AutoLog.AutoTransaction("Tra_QQMiniClientRoleBackRewrad", "QQ微端回流礼包")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_RequestQQMiniClientDownLoadRewrad", "请求领取QQ微端下载礼包"), RequestQQMiniClientDownLoadRewrad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_RequestQQMiniClientStartRewrad", "请求领取QQ微端设置开机启动礼包"), RequestQQMiniClientStartRewrad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_RequestQQMiniClientReadyStartRewrad", "请求领取QQ微端已经设置好的开机启动礼包"), RequestQQMiniClientReadyStartRewrad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_RequestQQMiniClientDayRewrad", "请求领取QQ微端每日登录礼包"), RequestQQMiniClientDayRewrad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_RequestQQMiniClientRoleBackRewrad", "请求领取QQ微端回流礼包"), RequestQQMiniClientRoleBackRewrad)
		
		