#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.HeFu")
#===============================================================================
# 合服相关
#===============================================================================
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDisperseInt32
from Game.SysData import WorldData
from Game.Role import Event
from Game.Role.Mail import Mail

mail_title = "合服通知以及补偿"
mail_sender = "系统"
mail_content = "亲爱的玩家，您所在的服务器已经进行了数据互通，请您留意。登陆方式保持不变，依然从原来的服务器登陆即可，关于合服活动详情，请关注精彩活动。附件为本次合服补偿内容。"


def HeFuInit(role):
	#合服之后的角色数据初始化
	hefuCnt = WorldData.GetHeFuCnt()
	if not hefuCnt:
		#没有合服
		return
	if role.GetDI32(EnumDisperseInt32.HerFuRecord) == hefuCnt:
		#已经处理过了
		return
	
	with Tra_HeFu:
		#先记录
		role.SetDI32(EnumDisperseInt32.HerFuRecord, hefuCnt)
		#发邮件
		HeFuMail(role)
		#触发事件
		Event.TriggerEvent(Event.Eve_AfterRoleHeFu, role, None)
	


def HeFuMail(role):
	#发送一封合服邮件
	#with Tra_HeFuMail:
	Mail.SendMail(role.GetRoleID(), mail_title, mail_sender, mail_content, money = 10000000)

if "_HasLoad" not in dir():
	#Tra_HeFuMail = AutoLog.AutoTransaction("Tra_HeFuMail", "合服角色登录邮件")
	Tra_HeFu = AutoLog.AutoTransaction("Tra_HeFu", "合服角色数据处理")


