#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.MysteryBox.MysteryBoxMgr")
#===============================================================================
# 神秘宝箱Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Role.Data import EnumObj
from Game.Item.MysteryBox import MysteryBoxConfig

IDX_IDXSET = 1
IDX_TIME = 2

if "_HasLoad" not in dir():
	Tra_MysteryBox_LotteryBox = AutoLog.AutoTransaction("Tra_MysteryBox_LotteryBox", "神秘宝箱_抽取奖励")
	Tra_MysteryBox_ChangeBox = AutoLog.AutoTransaction("Tra_MysteryBox_ChangeBox", "神秘宝箱_更换宝箱")
	
	#格式{boxCoding:idxSet()}
	MysteryBox_SingleBoxData_S = AutoMessage.AllotMessage("MysteryBox_SingleBoxData_S", "神秘宝箱_同步单个宝箱数据")
	#格式[boxCoding:idx]
	MysteryBox_LotteryResult_SB = AutoMessage.AllotMessage("MysteryBox_LotteryResult_SB", "神秘宝箱_同步抽奖结果")


#客户端请求 start
def OnOpenBox(role, msg):
	'''
	神秘宝箱_请求打开宝箱
	@param role:
	@param msg:目标宝箱coding  
	'''
	boxCoding = msg
	boxCfg = MysteryBoxConfig.MYSTERYBOX_BASECONFIG_DICT.get(boxCoding, None)
	if not boxCfg:
		return
	
	if role.GetLevel() < boxCfg.needLevel:
		return
	
	if role.ItemCnt(boxCoding) < 1:
		return
	
	roleMysteryBoxData = role.GetObj(EnumObj.MysteryBoxData)
	mysteryBoxRewardDict = roleMysteryBoxData[IDX_IDXSET]
	#数据超时检测处理
	timeOutStampDict = roleMysteryBoxData[IDX_TIME]
	if (boxCoding in mysteryBoxRewardDict) and (boxCoding in timeOutStampDict and timeOutStampDict[boxCoding] <= cDateTime.Seconds()):
		del mysteryBoxRewardDict[boxCoding]
		del timeOutStampDict[boxCoding]
	
	#装载数据
	rewardDict = {}
	rewardDict[boxCoding] = mysteryBoxRewardDict.get(boxCoding, set())	
	#同步客户端
	role.SendObj(MysteryBox_SingleBoxData_S, rewardDict)

	
def OnLotteryBox(role, msg):
	'''
	神秘宝箱_请求抽取奖励
	@param role: 
	@param msg: 目标宝箱coding
	'''
	boxCoding = msg
	boxCfg = MysteryBoxConfig.MYSTERYBOX_BASECONFIG_DICT.get(boxCoding)
	if not boxCfg:
		return
	
	if role.GetLevel() < boxCfg.needLevel:
		return
	
	if role.ItemCnt_NotTimeOut(boxCoding) < 1:
		return
	
	mysteryBoxDataDict = role.GetObj(EnumObj.MysteryBoxData)[IDX_IDXSET]
	idxSet = mysteryBoxDataDict.get(boxCoding, set())
	openCnt = len(idxSet)
	if openCnt >= boxCfg.maxOpenCnt:
		return
	
	needRMBList = boxCfg.needRMBList
	if len(needRMBList) < openCnt:
		return
	
	needRMB = needRMBList[openCnt]
	if needRMB < 0 or role.GetUnbindRMB() < needRMB:
		return
	
	randomObj = MysteryBoxConfig.GetRandomObjByCodingAndData(boxCoding, idxSet)
	if not randomObj:
		return
	
	rewardInfo = randomObj.RandomOne()
	if not rewardInfo:
		return
	
	idx, coding, cnt, isPrecious = rewardInfo
	with Tra_MysteryBox_LotteryBox:
		#增加中奖idx记录
		idxSet.add(idx)
		mysteryBoxDataDict[boxCoding] = idxSet
		#更新数据超时timeStamp
		timeOutStampDataDict = role.GetObj(EnumObj.MysteryBoxData)[IDX_TIME]
		timeOutStampDataDict[boxCoding] = cDateTime.Seconds() + boxCfg.timeOutSeconds
		#扣除神石
		if needRMB > 0:
			role.DecUnbindRMB(needRMB)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMysteryBoxLottery, (boxCoding, openCnt, needRMB, coding, cnt))
	
	role.SendObjAndBack(MysteryBox_LotteryResult_SB, [boxCoding, idx], 8, LotteryCallback, [boxCoding, boxCfg.boxName, idx, coding, cnt, isPrecious, role.GetRoleName()])
	

def LotteryCallback(role, callArgs, regparam):
	boxCoding, boxName, _,coding, cnt, isPrecious, roleName = regparam
	prompt = GlobalPrompt.MysteryBox_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt)
	#抽奖获得提示
	role.Msg(2, 0, prompt)
	#珍贵道具广播
	if isPrecious:
		broadMsg = GlobalPrompt.MysteryBox_Msg_Precioud % (boxName, roleName, coding, cnt)
		cRoleMgr.Msg(11, 0, broadMsg)
	
	#同步客户端对应宝箱最新数据
	if not role.IsLost() and not role.IsKick():
		rewardDict = {}
		rewardDict[boxCoding] = (role.GetObj(EnumObj.MysteryBoxData)[IDX_IDXSET]).get(boxCoding, set())
		role.SendObj(MysteryBox_SingleBoxData_S, rewardDict)
	
	Call.LocalDBCall(role.GetRoleID(), LotteryReward, [coding, cnt])


def LotteryReward(role, param = None):
	'''
	抽奖获得
	'''
	coding, cnt = param
	with Tra_MysteryBox_LotteryBox:
		#获得中奖物品
		role.AddItem(coding, cnt)


def OnChangeBox(role, msg):
	'''
	神秘宝箱_请求更换宝箱
	@param role: 
	@param msg: 目标宝箱coding
	'''
	boxCoding = msg
	boxcfg = MysteryBoxConfig.MYSTERYBOX_BASECONFIG_DICT.get(boxCoding, None)
	if not boxcfg:
		return
	
	if role.GetLevel() < boxcfg.needLevel:
		return
	
	mysteryboxDataDict = role.GetObj(EnumObj.MysteryBoxData)[IDX_IDXSET]
	idxSet = mysteryboxDataDict.get(boxCoding)
	if not idxSet:
		return
	
	if role.ItemCnt_NotTimeOut(boxCoding) < 1:
		return
	
	with Tra_MysteryBox_ChangeBox:
		#删除对应中奖纪录
		del mysteryboxDataDict[boxCoding]
		#删除物品
		role.DelItem(boxCoding, 1)
		
	#同步一个空的中奖纪录给客户端
	rewardDict = {}
	rewardDict[boxCoding] = set()
	role.SendObj(MysteryBox_SingleBoxData_S, rewardDict)
	

#事件 start
def OnInitRole(role, param = None):
	'''
	初始化角色Obj相关key
	'''
	mysteryBoxData = role.GetObj(EnumObj.MysteryBoxData)
	if IDX_IDXSET not in mysteryBoxData:
		mysteryBoxData[IDX_IDXSET] = {}
	if IDX_TIME not in mysteryBoxData:
		mysteryBoxData[IDX_TIME] = {}

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MysteryBox_OnOpenBox", "神秘宝箱_请求打开宝箱"), OnOpenBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MysteryBox_OnLotteryBox", "神秘宝箱_请求抽取奖励"), OnLotteryBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MysteryBox_OnChangeBox", "神秘宝箱_请求更换宝箱"), OnChangeBox)
