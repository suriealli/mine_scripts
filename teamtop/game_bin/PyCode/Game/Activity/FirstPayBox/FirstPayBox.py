#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FirstPayBox.FirstPayBox")
#===============================================================================
# 首充大礼包(原超值首充宝箱)
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt1, EnumObj, EnumTempObj
from Game.Role import Event


RewardRMB = 100#奖励魔晶

RewardItems = [(35606, 1), (25656, 1), (25681, 10), (25600, 10), (26032, 1), (25829, 100), (27399, 1)]		#奖励物品
RewardItems_NA = [(25600, 10), (25656, 1), (26032, 1)]	#奖励物品_北美版

FirstPayBox_tips = "#C(#00ff00)%s#n成功领取了价值不菲的#C(#00ff00)首充大礼包#n，琳琅满目的奖品把边上的小伙伴都惊呆了！#C(#00ff00)#U#A(#K(OLTB))我也要领取#n#n#n"

def FirstPayBox_Open(role, msg):
	'''
	请求领取超值首充宝箱奖励
	@param role:
	@param msg:
	'''
	if role.GetI1(EnumInt1.FirstPayBoxOpen):
		return
	
	if not role.GetI1(EnumInt1.FirstPay):
		return
	
	with Tra_FirstPayBox_Open:
		#先设置已经领取,再奖励
		role.SetI1(EnumInt1.FirstPayBoxOpen, True)

		tips = GlobalPrompt.Reward_Tips
		role.IncBindRMB(RewardRMB)
	
		tips += GlobalPrompt.BindRMB_Tips % RewardRMB
		
		rewardItemList = RewardItems

		for itemCoding, itemCnt in rewardItemList:
			if itemCoding == 25829:
				#数值道具:魔晶
				continue
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
	
	role.Msg(2, 0, tips)
	
	cRoleMgr.Msg(1, 0, FirstPayBox_tips % role.GetRoleName())

def AfterEve_QPoint(role, param):
	#Q点改变就算充值了
	role.SetI1(EnumInt1.FirstPay, True)
	
def SyncRoleOtherData(role, param):
	#屏蔽北美
	if Environment.EnvIsNA() : return
	#同步客户端是否连续
	mountId = EnumGameConfig.FirstPayMountId
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if mountId not in mountMgr.MountId_list:
		return
	if mountId not in mountMgr.Mount_outData_dict:
		return
	firstPayMountData = role.GetObj(EnumObj.FirstPayBoxDay).get(mountId)
	if not firstPayMountData:
		print 'GE_EXC, SyncRoleOtherData FirstPayBox mount error'
		return
	
	if firstPayMountData[3]:
		#连续
		role.SendObj(Tra_FirstPayBox_Mount, firstPayMountData[2] - firstPayMountData[1] + 1)
	else:
		#不连续
		if not firstPayMountData.get(4):
			#第一次
			role.SendObj(Tra_FirstPayBox_Mount, 0)
			firstPayMountData[4] = 1
	role.GetObj(EnumObj.FirstPayBoxDay)[mountId] = firstPayMountData
	
if "_HasLoad" not in dir():
	Tra_FirstPayBox_Mount = AutoMessage.AllotMessage("Tra_FirstPayBox_Mount", "首充坐骑是否连续")
	
	Tra_FirstPayBox_Open = AutoLog.AutoTransaction("Tra_FirstPayBox_Open", "领取超值首充宝箱奖励")
	
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FirstPayBox_Open", "请求领取超值首充宝箱奖励"), FirstPayBox_Open)
		
		Event.RegEvent(Event.Eve_GamePoint, AfterEve_QPoint)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
	
