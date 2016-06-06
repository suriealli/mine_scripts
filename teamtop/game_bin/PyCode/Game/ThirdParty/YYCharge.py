#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.YYCharge")
#===============================================================================
# YY充值
#===============================================================================
from ComplexServer.Log import AutoLog
from Game.Role import Event

def OnCharge(role, cnt):
	with YYCharge_Log:
		role.IncUnbindRMB_Q(cnt)
		# 设置游戏点消费
		role.SetConsumeQPoint(role.GetConsumeQPoint() + cnt)
		# 触发事件
		Event.TriggerEvent(Event.Eve_GamePoint, role, cnt)



if "_HasLoad" not in dir():
	YYCharge_Log = AutoLog.AutoTransaction("YYCharge_Log", "YY充值发货")
