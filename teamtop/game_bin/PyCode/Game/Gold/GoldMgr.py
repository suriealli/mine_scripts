#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Gold.GoldMgr")
#===============================================================================
# 炼金
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.DailyDo import DailyDo
from Game.Gold import GoldConfig
from Game.Role import Event
from Game.Role.Data import EnumInt16, EnumDayInt8, EnumCD, EnumObj, EnumTempObj
from Game.Union import UnionMgr
from Game.VIP import VIPConfig
from Game.ThirdParty.QQidip import QQEventDefine

if "_HasLoad" not in dir():
	
	Gold_VIP_TIMES = {0:2,1:4,2:6,3:8,4:10,5:12,6:14,7:20}
	CALL_FRIEND_CD = 32 #招募炼金CD
	HELP_PLAYER_LIMIT = 4 #每次协助炼金的人数上限
	
	Gold_Client_Suc = AutoMessage.AllotMessage("Gold_Client_Suc", "炼金界面状态")
	Gold_Get_Suc = AutoMessage.AllotMessage("Gold_Get_Suc", "炼金收获成功")
	#日志
	GoldCost = AutoLog.AutoTransaction("GoldCost", "炼金消耗")
	HelpGoldMoney = AutoLog.AutoTransaction("HelpGoldMoney", "协助炼金获取")
	GoldHarvest = AutoLog.AutoTransaction("GoldHarvest", "炼金收获")

def GetTendata(role):
	'''
	获取玩家十次炼金的消耗和收获
	@param role:
	@param times:从第几次炼金开始至炼金10次
	'''
	vip = role.GetVIP()
	if vip < EnumGameConfig.GOLD_PERFERT_TEN:
		return
	gold_cnt = role.GetI16(EnumInt16.GoldTimesDay)
	max_gold_smelt_cnt = 0
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	if vipConfig:
		max_gold_smelt_cnt = vipConfig.gold
	
	left_times = 0#记录玩家剩余可炼金次数
	if gold_cnt + 10 > max_gold_smelt_cnt:
		left_times = max_gold_smelt_cnt - gold_cnt
		if 0 == left_times:
			return
	else:
		left_times = 10
	gold_cfg = GoldConfig.GOLD_BASE_DICT.get(role.GetLevel())
	if not gold_cfg:
		return
	################################################
	#YY防沉迷对奖励特殊处理
	money = 0
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		money = gold_cfg.perfectMoney_fcm
	elif yyAntiFlag == 0:#原有收益
		money = gold_cfg.perfectMoney
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	times = gold_cnt
	total_cost = 0 #记录10消耗
	total_gold = 0 #记录10收获
	for _ in xrange(left_times):
		cfg = GoldConfig.GOLD_TIMES_DCIT.get(times + 1)
		if not cfg:
			return
		total_cost += cfg.cost		
		total_gold += money
		times += 1
	return (total_cost, total_gold, left_times)
#============================================	
def RequestGold(role, msg):
	'''
	客户端请求炼金
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.GLOD_LEVEL_ACTIVATE:
		return
	gold_cnt = role.GetI16(EnumInt16.GoldTimesDay)
	vip = role.GetVIP()
	gold_max_cnt = EnumGameConfig.Gold_MAX_SMELT_CNT
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	if vipConfig:
		gold_max_cnt = vipConfig.gold
	
	if gold_cnt >= gold_max_cnt:
		return
	data = role.GetObj(EnumObj.Gold_Player_Data)
	if data.get(1):#在炼金
		return
	#根据次数读取消耗
	cfg = GoldConfig.GOLD_TIMES_DCIT.get(gold_cnt + 1)
	if not cfg:
		print "GE_EXC,can not find times in Gold_VIP_TIMES, (%s)" % gold_cnt+1
		return	
	cost = cfg.cost
	if role.GetRMB() < cost:
		return	
	with GoldCost:
		role.DecRMB(cost)
		role.IncI16(EnumInt16.GoldTimesDay, 1)
		role.SetObj(EnumObj.Gold_Player_Data, {1: 1, 2: {}})
		role.SendObj(Gold_Client_Suc, [1,{}])
	
	#每日必做 -- 炼金
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_Gold, 1))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Gold, 1))
	
	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.gold()
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.gold()
	elif Environment.EnvIsRU():
		#七日活动
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		sevenActMgr.gold()
		
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_Gold)
	
def RequestHelpGold(role, msg):	
	'''
	玩家请求协助炼金
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.GLOD_LEVEL_ACTIVATE:
		role.Msg(2, 0, GlobalPrompt.GOLD_HELP_LEVEL_MSG)
		return
	global GOLD_HELP_DATA
	bossID = msg
	roleId = role.GetRoleID()
	if bossID == roleId:
		return	
	boss_role = cRoleMgr.FindRoleByRoleID(bossID)
	if not boss_role:#玩家不在线
		role.Msg(2, 0, GlobalPrompt.GOLD_END_MSG)
		return
	gold_data = boss_role.GetObj(EnumObj.Gold_Player_Data)
	state = gold_data.get(1)
	if not state:
		role.Msg(2, 0, GlobalPrompt.GOLD_END_MSG)
		return

	help_data = gold_data.get(2)
	if roleId in help_data:#已在协助列表
		role.Msg(2, 0, GlobalPrompt.GOLD_INIT_MSG)
		return
	leng = len(help_data)
	if len(help_data) >= 4:
		role.Msg(2, 0, GlobalPrompt.GOLD_FULL_MSG)
		return
	sex, career, grade = role.GetPortrait()
	help_data[roleId] = [roleId, role.GetRoleName(), sex, career, grade, leng]
	
	help_cnt = role.GetDI8(EnumDayInt8.GoldHelpTimesDay)
	if help_cnt < EnumGameConfig.GOLD_HELP_TIMES:
		cfg = GoldConfig.GOLD_BASE_DICT.get(role.GetLevel())
		if not cfg:
			return
		################################################
		#YY防沉迷对奖励特殊处理
		money = 0
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:#收益减半
			money = cfg.assistMoney_fcm
		elif yyAntiFlag == 1:#原有收益
			money = cfg.assistMoney
		else:
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		################################################
		with HelpGoldMoney:
			role.IncDI8(EnumDayInt8.GoldHelpTimesDay, 1)
			role.IncMoney(money)
			role.Msg(2, 0, GlobalPrompt.GOLD_HELP_SUC_MSG % money)
	else:
		role.Msg(2, 0, GlobalPrompt.GOLD_HELP_SUC_MSG2)
	boss_role.SendObj(Gold_Client_Suc, [state ,gold_data.get(2)])
	
def RequestGetGold(role, msg):		
	'''
	客户端请求收获
	@param role:
	@param msg:
	'''
	global GOLD_HELP_DATA
	
	gold_data = role.GetObj(EnumObj.Gold_Player_Data)
	state = gold_data.get(1)
	if not state:
		return
	cfg = GoldConfig.GOLD_BASE_DICT.get(role.GetLevel())
	if not cfg:
		print "GE_EXC,can not find level in GOLD_HELP_DATA, (%s)", role.GetLevel()
		return 
	help_data = gold_data.get(2)
	money = 0
	perfert = False
	isHalfYearCard = False
	with GoldHarvest:
		Earning = role.GetEarningGoldBuff()
		
		#各版本判断
		if Environment.EnvIsNA():
			#北美版
			if role.GetCD(EnumCD.Card_Year):
				#有年卡, 金币加成10%
				Earning += EnumGameConfig.Card_YearGold
				isHalfYearCard = True
		else:
			#其他版本
			if role.GetCD(EnumCD.Card_HalfYear):
				#有半年卡, 金币加成10%
				Earning += EnumGameConfig.Card_HalfYearGold
				isHalfYearCard = True
				
		from Game.Activity.QingMing import QuanMingLianJin
		qingMingBuff = QuanMingLianJin.GetGoldBuff(role)
		if qingMingBuff > 0:
			Earning += qingMingBuff
				
		from Game.Activity.ZhongQiu import ZhongQiuLianJin
		zhongQiuGoldBuff = ZhongQiuLianJin.GetGoldBuff(role)
		if zhongQiuGoldBuff > 0:
			Earning += zhongQiuGoldBuff
		
		################################################
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:#收益减半
			tmpMoney = cfg.perfectMoney_fcm
			tmpAdvanceMoney = cfg.advanceMoney_fcm
		elif yyAntiFlag == 0:#原有收益
			tmpMoney = cfg.perfectMoney
			tmpAdvanceMoney = cfg.advanceMoney
		else:
			tmpMoney = 0
			tmpAdvanceMoney = 0
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		################################################
		if role.GetVIP() >= EnumGameConfig.GOLD_VIP_LEVLE:
			money = int(tmpMoney * (1 + Earning / 100.0))
			role.IncMoney(money)
			perfert = True
		else:
			if len(help_data) < HELP_PLAYER_LIMIT:
				money = int(tmpAdvanceMoney * (1 + Earning / 100.0))
				role.IncMoney(money)
			elif len(help_data) >= HELP_PLAYER_LIMIT:
				money = int(tmpMoney * (1 + Earning / 100.0))
				role.IncMoney(money)
				perfert = True
	#清除数据
	role.SetObj(EnumObj.Gold_Player_Data, {1: 0, 2: {}})
	role.SetCD(EnumCD.Gold_Call_CD, 0)
	if perfert:
		role.SendObj(Gold_Get_Suc, 1)
	else:
		role.SendObj(Gold_Get_Suc, 0)
	role.SendObj(Gold_Client_Suc, [0, {}])
	
	if isHalfYearCard:
		#有半年卡
		theTip = GlobalPrompt.GOLD_SUC_MSG % money + GlobalPrompt.Card_GoldBuff_Tips
		if qingMingBuff:
			theTip += GlobalPrompt.QingMingLianJinBuffTips1 % EnumGameConfig.QingMingLianJinBuff
		role.Msg(2, 0, theTip)
			
	else:
		theTip = GlobalPrompt.GOLD_SUC_MSG % money
		if qingMingBuff:
			theTip += GlobalPrompt.QingMingLianJinBuffTips2 % EnumGameConfig.QingMingLianJinBuff
		role.Msg(2, 0, theTip)
		
		
def RequestRecruitingGold(role, msg):	
	'''
	客户端请求招募炼金术士
	@param role:
	@param msg:
	'''
	help_type = msg
	#CD时间
	cd = role.GetCD(EnumCD.Gold_Call_CD)
	if cd > 0:
		return
	role.SetCD(EnumCD.Gold_Call_CD, CALL_FRIEND_CD)	
	if 1 == help_type:#世界喊话
		#传闻
		cRoleMgr.Msg(7, 0, GlobalPrompt.GOLD_HELP_DESC_MSG % (role.GetRoleName(), role.GetRoleID()))	
	else:
		unionObj = role.GetUnionObj()
		if not unionObj:
			return
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.GOLD_HELP_DESC_MSG % (role.GetRoleName(), role.GetRoleID()))

def RequestTenGold(role, msg):
	'''
	客户端请求10次完美炼金
	@param role:
	@param msg:
	'''
	vip = role.GetVIP()
	if vip < EnumGameConfig.GOLD_PERFERT_TEN:
		return
	global Gold_VIP_TIMES
	#获取玩家已炼金次数
	gold_cnt = role.GetI16(EnumInt16.GoldTimesDay)
	#获取该玩家总共可以炼金的次数
	max_times = 3
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	if vipConfig:
		max_times = vipConfig.gold
	if gold_cnt >= max_times:
		return 
	data = GetTendata(role)
	if not data:
		return
	cost, gold, times = data
	if role.GetRMB() < cost:
		return
	isHalfYearCard = False
	with GoldHarvest:
		role.DecRMB(cost)
		Earning = role.GetEarningGoldBuff()
		
		#各版本判断
		if Environment.EnvIsNA():
			#北美版
			if role.GetCD(EnumCD.Card_Year):
				#有年卡, 金币加成10%
				Earning += EnumGameConfig.Card_YearGold
				isHalfYearCard = True
		else:
			#其他版本
			if role.GetCD(EnumCD.Card_HalfYear):
				#有半年卡, 金币加成10%
				Earning += EnumGameConfig.Card_HalfYearGold
				isHalfYearCard = True
			
		from Game.Activity.QingMing import QuanMingLianJin
		qingMingBuff = QuanMingLianJin.GetGoldBuff(role)
		if qingMingBuff > 0:
			Earning += qingMingBuff
				
		from Game.Activity.ZhongQiu import ZhongQiuLianJin
		zhongQiuGoldBuff = ZhongQiuLianJin.GetGoldBuff(role)
		if zhongQiuGoldBuff > 0:
			Earning += zhongQiuGoldBuff
		
		gold = int(gold * (1 + Earning / 100.0))
		role.IncMoney(gold)
		role.IncI16(EnumInt16.GoldTimesDay, times)
		#清除数据
		role.SetObj(EnumObj.Gold_Player_Data, {1: 0, 2: {}})
		role.SendObj(Gold_Client_Suc, [0, {}])
		role.SendObj(Gold_Get_Suc, 2)
		
		if isHalfYearCard:
			#有半年卡
			theTip = GlobalPrompt.GOLD_SUC_MSG % gold + GlobalPrompt.Card_GoldBuff_Tips
			if qingMingBuff:
				theTip += GlobalPrompt.QingMingLianJinBuffTips1 % EnumGameConfig.QingMingLianJinBuff
			role.Msg(2, 0, theTip)
			
		else:
			theTip = GlobalPrompt.GOLD_SUC_MSG % gold
			if qingMingBuff:
				theTip += GlobalPrompt.QingMingLianJinBuffTips2 % EnumGameConfig.QingMingLianJinBuff
			role.Msg(2, 0, theTip)
		
	#每日必做 -- 炼金
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_Gold, 10))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Gold, 10))
	
	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.gold()
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.gold()
	elif Environment.EnvIsRU():
		#七日活动
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		sevenActMgr.gold()
		
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_Gold)
	
	
def RequestOpenPanel(role, msg):
	'''
	打开炼金界面
	@param role:
	@param msg:
	'''
	gold_data = role.GetObj(EnumObj.Gold_Player_Data)
	state = gold_data.get(1)
	if gold_data.get(2):
		role.SendObj(Gold_Client_Suc, [state ,gold_data.get(2)])
	else:
		role.SendObj(Gold_Client_Suc, [state, {}])
#====================================================

def RoleDayClear(role, param):
	'''
	#每日清零
	@param role:
	@param param:
	'''
	role.SetI16(EnumInt16.GoldTimesDay, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_open_panel", "客户端打开炼金界面"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_gold", "客户端请求炼金"), RequestGold)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_help_gold", "客户端请求协助炼金"), RequestHelpGold)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_get_gold", "客户端请求收获"), RequestGetGold)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_Recruiting_gold", "客户端请求招募炼金术士"), RequestRecruitingGold)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_ten_gold", "客户端请求10次完美炼金"), RequestTenGold)
		
	
