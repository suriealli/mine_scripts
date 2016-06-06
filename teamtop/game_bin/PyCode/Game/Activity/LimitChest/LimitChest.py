#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LimitChest.LimitChest")
#===============================================================================
# 限次宝箱
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumObj
from Game.Activity.LimitChest import LimitChestConfig
from Game.Role import Event

if "_HasLoad" not in dir():
	
	ThingTypeList = [1, 2, 3, 4, 5, 6]   #1:道具 2：命魂 3：金币 4：魔晶 5：体力 6:神石,物品类型必然是其中的一种
	
	
	
	#消息,这里两条消息分开主要是为了方便客户端的显示
	Sync_LimitChest_ShowData = AutoMessage.AllotMessage("Sync_LimitChest_ShowData", "同步玩家限次宝箱显示数据")
	Sync_LimitChest_ShowTimes = AutoMessage.AllotMessage("Sync_LimitChest_ShowTimes", "同步玩家限次宝箱玩家已经开箱的次数")
	
	#Sync_LimitChest_ShowData格式：[箱子coding,下方显示，左方显示]
	#										下方显示：[((物品类型, 物品code),物品数量)........]
	#										左方显示：[(玩家姓名，物品类型，（物品coding,数量）) ........]
	
	#日志
	Tra_OpenLimitChest = AutoLog.AutoTransaction("Tra_OpenLimitChest", "开启限次宝箱")


def RequestOpenChest(role, msg):
	'''
	客户端请求开启宝箱 
	@param role:
	@param msg:
	'''
	
	#玩家背包已满
	if role.PackageIsFull() or role.TarotPackageIsFull():
		role.Msg(2, 0, GlobalPrompt.LimitChest_PackageFullTips)
		return

	chest_code = msg
	#宝箱的数量不够
	if role.ItemCnt(chest_code) < 1:
		return
	
	config = LimitChestConfig.LimitChestConfigDict.get(chest_code)
	if not config:
		print "GE_EXC,error while config = LimitChestConfig.LimitChestConfigDict.get(chest_code), no such chest_code(%s)" % chest_code
		return

	price = 0
	rewarddata = role.GetObj(EnumObj.LimitChest)
	#这里有个比较特殊的处理，策划要求记录玩家最近开宝箱获得的奖励内容
	#1.显示最近获得的十个不同的奖励类型的奖励
	#2.如果奖励已经在之前获得过，则显示获得的奖励的总的数量
	#3.如果出现了新的奖励类型，则把最早出现的奖励类型干掉
	#由于不可预知需要记录的奖励的数量，没有才用记录某种类型出现的时间戳的方式。这里才用列表和字典同时记录，列表控制奖励类型出现的先后顺序，字典来记录某种奖励出现的次数,可以确定列表是字典keys()的子集
	#也即是rewardlist, rewarddict
	rewardlist, rewarddict, times = rewarddata.setdefault(chest_code, [[], {}, 0])
	
	#取出持久化字典里的数据
	serverlist = LimitChestDict.get(chest_code, [])
	
	#如果次数大于免费的次数的话，就要扣神石了
	if times + 1 > config.FreeCnt:
		price = config.Cost
	#取出随机的奖励
	thingtype, thing = config.RandomRate.RandomOne()
	if thingtype not in ThingTypeList:
		print "GE_EXC, thingtype(%s) can not be recognized while RequestOpenChest in LimitChest" % thingtype
		return

	#玩家的神石不够
	if role.GetUnbindRMB() < price:
		return

	with Tra_OpenLimitChest:
		#扣宝箱
		if role.DelItem(chest_code, 1) < 1:
			return
		#扣神石
		if price > 0:
			role.DecUnbindRMB(price)
		#加次数
		rewarddata[chest_code][2] += 1
		

		#道具，那么thing就是(itemcoding,cnt)
		if thingtype == 1:
			thingcode, thingcnt = thing
			rewarddict[(thingtype, thingcode)] = rewarddict.get((thingtype, thingcode), 0) + thingcnt
			if not (thingtype, thingcode) in rewardlist:
				rewardlist.append((thingtype, thingcode))
			role.AddItem(*thing)
			rewardTips = GlobalPrompt.LimitChest_RewardTips + GlobalPrompt.Item_Tips % thing
			
			
		#命魂,那么thing就是(tarotcode,tarotcnt)
		elif thingtype == 2:
			thingcode, thingcnt = thing
			rewarddict[(thingtype, thingcode)] = rewarddict.get((thingtype, thingcode), 0) + thingcnt
			if not (thingtype, thingcode) in rewardlist:
				rewardlist.append((thingtype, thingcode))
			role.AddTarotCard(*thing)
			rewardTips = GlobalPrompt.LimitChest_RewardTips + GlobalPrompt.Tarot_Tips % thing

		#金币，那么thing[1]就是金币的数量
		elif thingtype == 3:
			thingcode, thingcnt = thing#这里的thingcode只是为了客户端显示用的，下面的魔晶、体力、神石也都一样
			rewarddict[(thingtype, thingcode)] = rewarddict.get((thingtype, thingcode), 0) + thingcnt
			if not (thingtype, thingcode) in rewardlist:
				rewardlist.append((thingtype, thingcode))
			role.IncMoney(thingcnt)
			rewardTips = GlobalPrompt.LimitChest_RewardTips + GlobalPrompt.Money_Tips % thingcnt
			
			
		#魔晶，那么thing[1]就是魔晶的数量
		elif thingtype == 4:
			thingcode, thingcnt = thing
			rewarddict[(thingtype, thingcode)] = rewarddict.get((thingtype, thingcode), 0) + thingcnt
			if not (thingtype, thingcode) in rewardlist:
				rewardlist.append((thingtype, thingcode))
			role.IncBindRMB(thingcnt)
			rewardTips = GlobalPrompt.LimitChest_RewardTips + GlobalPrompt.BindRMB_Tips % thingcnt
			
			
		#体力，那么thing[1]就是体力的值
		elif thingtype == 5:
			thingcode, thingcnt = thing
			rewarddict[(thingtype, thingcode)] = rewarddict.get((thingtype, thingcode), 0) + thingcnt
			if not (thingtype, thingcode) in rewardlist:
				rewardlist.append((thingtype, thingcode))
			role.IncTiLi(thingcnt)
			rewardTips = GlobalPrompt.LimitChest_RewardTips + GlobalPrompt.TiLi_Tips % thingcnt
			
			

		#神石，那么thing[1]就是系统神石的数量
		elif thingtype == 6:
			thingcode, thingcnt = thing
			rewarddict[(thingtype, thingcode)] = rewarddict.get((thingtype, thingcode), 0) + thingcnt
			if not (thingtype, thingcode) in rewardlist:
				rewardlist.append((thingtype, thingcode))
			role.IncUnbindRMB_S(thingcnt)
			rewardTips = GlobalPrompt.LimitChest_RewardTips + GlobalPrompt.UnBindRMB_Tips % thingcnt
			
		else:
			return
		
		#只有部分物品需要记录在红手榜
		if (thingtype, thing) in config.RedHand:
			serverlist.append((role.GetRoleName(), thingtype, thingcode, thingcnt))
				
		#只显示最近十次获得的不同的物品种类
		while len(rewardlist) > 10 :
			rewardlist.pop(0)
		while len(serverlist) > 10:
			serverlist.pop(0)
		LimitChestDict[chest_code] = serverlist
		#这么做是为了显示最近获得的十种奖励，同时当奖励类型重复的时候，则增加已经获得的奖励物品的数量
		showlist = zip(rewardlist, map(rewarddict.get, rewardlist))
		#将玩家个人数据同步给客户端
		role.SendObj(Sync_LimitChest_ShowData, (chest_code, showlist, serverlist))
		role.SendObj(Sync_LimitChest_ShowTimes, rewarddata[chest_code][2])
		
		role.Msg(2, 0, rewardTips)


def RequestOpenPanel(role, msg):
	'''
	客户端请求打开限次宝箱二级面板
	@param role:
	@param msg:
	'''
	chest_code = msg
	rewarddata = role.GetObj(EnumObj.LimitChest)
	rewardlist, rewarddict, times = rewarddata.setdefault(chest_code, [[], {}, 0])
	#只显示最近十次获得的不同的物品种类
	while len(rewardlist) > 10 :
		rewardlist.pop(0)
	showlist = zip(rewardlist, map(rewarddict.get, rewardlist))
	serverlist = LimitChestDict.get(chest_code, [])
	#将玩家个人数据同步给客户端
	role.SendObj(Sync_LimitChest_ShowData, (chest_code, showlist, serverlist))
	role.SendObj(Sync_LimitChest_ShowTimes, times)

def DailyClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	if role.GetObj(EnumObj.LimitChest):
		role.GetObj(EnumObj.LimitChest).clear()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, DailyClear)
		
	if (Environment.HasLogic or Environment.HasWeb) and not Environment.IsCross:
		#保存全服玩家的开箱记录{chestCoding:rewardinfo}
		LimitChestDict = Contain.Dict("LimitChestDict", (2038, 1, 1), None, None, isSaveBig=True)
		
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LimitChest_RequestOpenChest", "客户端请求开启限次宝箱"), RequestOpenChest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LimitChest_RequestOpenPanel", "客户端请求打开限次宝箱面板"), RequestOpenPanel)


