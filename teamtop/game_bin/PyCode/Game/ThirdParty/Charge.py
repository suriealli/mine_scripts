#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.Charge")
#===============================================================================
# 第三方充值
#===============================================================================
from ComplexServer.Log import AutoLog
from Game.Role import Event



def OnCharge(role, cnt):
	with Charge_Log:
		role.IncUnbindRMB_Q(cnt)
		# 设置游戏点消费
		role.SetConsumeQPoint(role.GetConsumeQPoint() + cnt)
		# 触发事件
		Event.TriggerEvent(Event.Eve_GamePoint, role, cnt)



if "_HasLoad" not in dir():
	Charge_Log = AutoLog.AutoTransaction("Charge_Log", "第三方充值发货")
