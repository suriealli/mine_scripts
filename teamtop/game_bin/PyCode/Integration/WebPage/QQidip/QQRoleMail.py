#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQRoleMail")
#===============================================================================
# 通过邮件发送简单物品
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from Game.Role.Mail import EnumMail
from Integration.Help import ConfigHelp

'''
"body" :
	{
		"Uin" : ,			  /* 用户QQ号 */
		"AreaId" : ,		   /* 所在大区ID */
		"RoleId" : ,		   /* 角色ID */
		"ItemId" : ,		   /* 道具ID */
		"ItemNum" : ,		  /* 道具数量 */
		"MailTitle" : "",	  /* 邮件标题 */
		"MailContent" : "",	/* 邮件内容 */
		"Source" : ,		   /* 渠道号 */
		"Serial" : ""		  /* 流水号 */
	}
'''

sender  ="系统"

SQL = "select role_id from role_data where account = %s;"
#正式接口
def Mail(request):
	serverid = request.BodyGet("AreaId")
	Uin = request.BodyGet("Uin")#openID account
	RoleId = request.BodyGet("RoleId")
	ItemId = request.BodyGet("ItemId")
	ItemNum = request.BodyGet("ItemNum")
	MailTitle = request.BodyGet("MailTitle")
	MailContent = request.BodyGet("MailContent")
	
	Source = request.BodyGet("Source")
	Serial = request.BodyGet("Serial")
	
	isUnion = False
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
		else:
			isUnion = True
			
	#如果道具id不存在返回itemid error，uin返回openid error，角色id不正确返回roleid error
	if not ConfigHelp.HasItem(ItemId):
		return request.ErrorResponse(-1008, "itemid error")
	
	with con as cur:
		cur.execute(SQL, Uin)
		result = cur.fetchall()
		if not result:
			#查询不到角色
			return request.ErrorResponse(-1009, "openid error")
		roleId = result[0][0]
		if roleId != RoleId:
			return request.ErrorResponse(-1010, "roleid error")
	
	
	maildata = {}
	if ItemId and ItemNum:
		maildata[EnumMail.EnumItemsKey] = [(ItemId, ItemNum)]
	if Source:
		maildata[EnumMail.EnumSourceKey] = Source
	if Serial:
		maildata[EnumMail.EnumSerialKey] = Serial
	
	result = None
	if isUnion is False:
		result = DBHelp.SendRoleMail(RoleId, MailTitle, sender, MailContent, 30007, maildata)
	else:
		result = DBHelp.SendRoleMail_Unoin(RoleId, MailTitle, sender, MailContent, 30007, maildata)
	if result:
		return request.response({"Result" : 0, "RetMsg" : "succeed"})
	else:
		return request.response({}, 1)

