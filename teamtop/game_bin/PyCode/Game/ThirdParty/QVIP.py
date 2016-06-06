#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QVIP")
#===============================================================================
# QQVIP
#===============================================================================
import Environment
from ComplexServer.API import QQHttp
from Game.Role import Event
from Game.Role.Data import EnumTempInt64, EnumTempObj, EnumInt8

HZ = 1
LZ = 2
HZ_NAME = "黄钻"
LZ_Name = "蓝钻"

#微端登录 pf
#union-10131-1	具有联盟平台礼包特权
#union-10131-2	具有3366平台礼包特权(蓝钻等)
#union-10131-7	具有QQ会员平台礼包特权
#union-10131-8	具有QQ空间平台礼包特权
#union-10131-9	具有游戏频道平台礼包特权
#union-10131-10	具有所有官网平台礼包特权

def OnLogin(role, param):
	if not Environment.EnvIsQQ():
		return
	#信息先清理
	role.SetTI64(EnumTempInt64.IsGameUnoin, 0)
	role.SetTI64(EnumTempInt64.IsGameUnionAiWan, 0)
	role.SetTI64(EnumTempInt64.IsGameUnionQQGJ, 0)
	role.SetTI64(EnumTempInt64.IsQQGame, 0)
	role.SetTI64(EnumTempInt64.Is3366, 0)
	role.SetTI64(EnumTempInt64.QQMiniClient, 0)
	role.SetTI64(EnumTempInt64.IsQzone, 0)
	role.SetTI64(EnumTempInt64.IsPengYou, 0)
	role.SetTI64(EnumTempInt64.IsWebsite, 0)
	
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	openkey = login_info["openkey"]
	pf = login_info["pf"]
	lis = pf.split("*")# 有 * 号 表示是新版的pf 格式为 "创建平台 * 登录平台"
	if len(lis) > 1:
		login_pf = lis[1]
	else:
		login_pf = pf
	if login_pf in set(["3366", "qqgame", "website"]):
		role.SetTI64(EnumTempInt64.QVIP, LZ)
		if login_pf == "3366":
			role.SetTI64(EnumTempInt64.Is3366, 1)
		elif login_pf == "qqgame":
			role.SetTI64(EnumTempInt64.IsQQGame, 1)
		elif login_pf == "website":
			role.SetTI64(EnumTempInt64.IsWebsite, 1)
	else:
		role.SetTI64(EnumTempInt64.QVIP, HZ)
		if login_pf == "union-10131-1":
			#微端登录 
			role.SetTI64(EnumTempInt64.QQMiniClient, 1)
			#union-10131-1	具有联盟平台礼包特权
			role.SetTI64(EnumTempInt64.IsGameUnoin, 1)
		elif login_pf == "union-10131-8":
			#微端登录 union-10131-8	具有QQ空间平台礼包特权
			role.SetTI64(EnumTempInt64.QQMiniClient, 1)
		elif login_pf.startswith("union"):
			#游戏联盟登录(非微端)
			if login_pf.startswith("union-10029"):
				#游戏联盟,爱玩渠道
				role.SetTI64(EnumTempInt64.IsGameUnoin, 1)
				role.SetTI64(EnumTempInt64.IsGameUnionAiWan, 1)
			elif login_pf.startswith("union-10135"):
				#游戏联盟,QQ管家
				role.SetTI64(EnumTempInt64.IsGameUnoin, 1)
				role.SetTI64(EnumTempInt64.IsGameUnionQQGJ, 1)
			else:
				pass
				#print "GE_EXC, gameunion login unknow pf (%s)" % login_pf
		elif login_pf == "qzone":
			#空间渠道
			role.SetTI64(EnumTempInt64.IsQzone, 1)
		elif login_pf == "pengyou":
			#朋友网
			role.SetTI64(EnumTempInt64.IsPengYou, 1)
		else:
			pass
			#未知平台
			#print "GE_EXC, roleLogin with unknow pf (%s)" % login_pf
			
	if not Environment.IsCross:
		# 再次查询腾讯各种V
		QQHttp.get_vip(openid, openkey, pf, OnGetVIP, role)
	
		#心悦VIP
		if login_info.get("adtag") == "gw.home.web.lqsz_20150325" or role.GetXinYueLevel():
			userip = login_info["userip"]
			QQHttp.get_xinyue_vip(openid, openkey, pf, userip, OnGetXinYueVIP, role)
	

def OnGetVIP(response, regparam):
	if response is None:
		return
	code, body = response
	if code != 200:
		#print "GE_EXC, QVIP get_vip error code(%s)" % code
		return
	body = eval(body)
	if body["ret"] != 0:
		print "GE_EXC, QVIP get_vip ret(%s) " % body["ret"]
		return
	role = regparam
	if role.IsKick():
		return
	qvip = GetQVip(role)
	if qvip == HZ:
		role.SetQQLZ(0)
		role.SetQQYLZ(0)
		role.SetQQHHLZ(0)
		if body.get("is_yellow", 0):
			role.SetQQHZ(body.get("yellow_level", 0))
			role.SetQQYHZ(body.get("is_year_yellow", 0))
			role.SetQQHHHZ(body.get("is_high_yellow", 0))
		else:
			role.SetQQHZ(0)
			role.SetQQYHZ(0)
			role.SetQQHHHZ(0)
	elif qvip == LZ:
		role.SetQQHZ(0)
		role.SetQQYHZ(0)
		role.SetQQHHHZ(0)
		if body.get("is_blue", 0):
			role.SetQQLZ(body.get("blue_level", 0))
			role.SetQQYLZ(body.get("is_year_blue", 0))
			role.SetQQHHLZ(body.get("is_high_blue", 0))
		else:
			role.SetQQLZ(0)
			role.SetQQYLZ(0)
			role.SetQQHHLZ(0)

def OnGetXinYueVIP(response, regparam):
	if response is None:
		return
	code, body = response
	if code != 200:
		print "GE_EXC, QVIP OnGetXinYueVIP error code(%s)" % code
		return
	body = eval(body)
	if body["ret"] != 0:
		print "GE_EXC, QVIP OnGetXinYueVIP ret(%s) " % body["ret"]
		return
	role = regparam
	
	if body.get("xy_type") != 1:
		return 
	xy_level = int(body["xy_level"])
	role.SetI8(EnumInt8.QQXinYueVipLevel, xy_level)



def GetQVip(role):
	'''
	获取QQVip类型
	@return: 0:没有QQVip 1:黄钻 2:蓝钻
	'''
	return role.GetTI64(EnumTempInt64.QVIP)

def GetQVipName(role):
	'''
	获取QQVip的名字（正确处理了黄钻蓝钻）
	'''
	qvip = GetQVip(role)
	if qvip == HZ:
		return HZ_NAME
	elif qvip == LZ:
		return LZ_Name
	else:
		return ""

def GetQVipLevel(role):
	'''
	获取QQVip的等级（正确处理了黄钻蓝钻）
	'''
	qvip = GetQVip(role)
	if qvip == HZ:
		return role.GetQQHZ()
	elif qvip == LZ:
		return role.GetQQLZ()
	else:
		return 0

def GetQVipYear(role):
	'''
	获取QQVip是否年费（正确处理了黄钻蓝钻）
	'''
	qvip = GetQVip(role)
	if qvip == HZ:
		return role.GetQQYHZ()
	elif qvip == LZ:
		return role.GetQQYLZ()
	else:
		return False

def GetQVipHight(role):
	'''
	获取QQVip是否豪华（正确处理了黄钻蓝钻）
	'''
	qvip = GetQVip(role)
	if qvip == HZ:
		return role.GetQQHFHZ()
	elif qvip == LZ:
		return role.GetQQHFLZ()
	else:
		return False

if "_HasLoad" not in dir():
	if Environment.EnvIsQQ():
		Event.RegEvent(Event.Eve_AfterLogin, OnLogin, index = 0)
	
	if Environment.EnvIsQQ() and not Environment.IsCross:
		#特殊事件触发
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnLogin, index = 0)
