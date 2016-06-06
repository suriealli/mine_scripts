#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.Charge")
#===============================================================================
# 第三方充值
#===============================================================================
import uuid
import md5
import time
import Environment
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp
from ComplexServer.API import Define as Http_Define
from Integration.WebPage.model import me

KEY = "s5s#4qkcW_de#dvz66H"
CHARGE_SQL = "insert into charge (account, role_id, token, billno, amt, dt, level) values(%s, %s, %s, %s, %s, NOW(), %s);"
CHARGE_TK_SQL = "insert into charge (account, role_id, token, billno, payamt_coins, dt, level, from_1, amt) values(%s, %s, %s, %s, %s, NOW(), %s, %s, %s);"


def GetKey():
	#新版KEY每一个版本都分配一个key
	if Environment.IsRUXP:
		return "101XP_sffa#_ol109_#jsdFD47"
	elif Environment.IsPL:
		return "Poland_chargessr#_ogFA45685K#SOo"
	elif Environment.IsPLXP:
		return "Poland101XP_chargessr#_ffl#sfjasl#jd"
	elif Environment.IsTKPLUS1:
		return "#tkplus1_wam_#dfghljfds#ddfg"
	elif Environment.IsRURBK:
		return "RBK_jfdljf##djdjdjpqeio#mcb"
	elif Environment.IsRUGN:
		return "GN_jfdljf##LUKUIYH#csedf"
	elif Environment.IsTKESP:
		return "#tkesp_stsd_#0o12dgsfgds_#"
	elif Environment.IsFR:
		return "#_frcharge#_0o_odsfdsgf_#"
	elif Environment.IsNAPLUS1:
		return "#_naplus1_dfg#o0_weoshfsd1290#"
	elif Environment.IsEN:
		return "en_charge_abhyue123_88asptyk"
	elif Environment.IsESP:
		return "esp_charge_adfjjdfj#11_655ffd#jv"
	elif Environment.Is7K:
		return "7k7k_charge_adfjjdfj#_#0o_odsfdsgf_#"
	else:
		#旧版的
		return KEY

def UseOldAPI():
	#北美和繁体使用旧的API，土耳其，俄罗斯和后续的版本都使用新的API
	return Environment.EnvIsFT() or Environment.EnvIsNA()

def Req_DoCharge(request):
	'''
	【接口】--第三方充值
	'''
	table = AutoHTML.Table([
		me.say(request,"区"),
		"<input type='text' name='serverid'>"
	])
	table.body.append([
		me.say(request,"帐号"),
		"<input type='text' name='account'>"
	])
	table.body.append([
		me.say(request,"订单号"),
		"<input type='text' name='billno'>"
	])
	table.body.append([
		me.say(request,"充值数量"),
		"<input type='text' name='cnt'>"
	])
	table.body.append([
		me.say(request,"平台"),
		"<input type='text' name='pf'>"
	])
	table.body.append([
		me.say(request,"真实货币"),
		"<input type='text' name='realamt'>"
	])
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	<form action="%s" method="GET" target="_blank">
	%s
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>''' % (
		me.say(request,"第三方充值"),
		AutoHTML.GetURL(Res_DoCharge),
		table.ToHtml(),
		me.say(request,"充值")
	)
	return HttpResponse(html)

def Res_DoCharge(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	cnt = AutoHTML.AsString(request.GET, "cnt")
	billno = AutoHTML.AsString(request.GET, "billno")
	pf = AutoHTML.AsInt(request.GET, "pf")
	realamt = AutoHTML.AsInt(request.GET, "realamt")
	unixtime = int(time.time())
	if not UseOldAPI():
		sign = md5.new("%s%s%s%s%s%s%s%s" % (serverid, account, billno, cnt, unixtime, pf,realamt,GetKey())).hexdigest()
		d = {"serverid": serverid,
			"account": account,
			"billno" :billno,
			"cnt" : cnt,
			"unixtime" : unixtime,
			"sign" : sign,
			"pf":pf,
			"realamt":realamt
			}
		return _DoCharge(OtherHelp.Request(d))
	sign = md5.new("%s%s%s%s%s%s" % (serverid, account, billno, cnt, unixtime, GetKey())).hexdigest()
	d = {"serverid": serverid,
		"account": account,
		"billno" :billno,
		"cnt" : cnt,
		"unixtime" : unixtime,
		"sign" : sign,
		}
	return _DoCharge(OtherHelp.Request(d))


def DoCharge(request):
	return OtherHelp.Apply(_DoCharge, request, __name__)

def _DoCharge(request):
	if not UseOldAPI():
		return TKCharge(request)
	
	#旧的接口
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	unixtime = AutoHTML.AsInt(request.GET, "unixtime")
	billno = AutoHTML.AsString(request.GET, "billno")
	cnt = AutoHTML.AsInt(request.GET, "cnt")
	sign = AutoHTML.AsString(request.GET, "sign")
	#北美混服新增特殊处理
	pf = AutoHTML.AsInt(request.GET, "pf")
	realamt = AutoHTML.AsInt(request.GET, "realamt")
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(Http_Define.ErrorTime)
	#验证签名
	if sign != md5.new("%s%s%s%s%s%s" % (serverid, account, billno, cnt, unixtime, GetKey())).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		cur.execute("select role_id, di32_11 from role_data where account = %s; ", account)
		result = cur.fetchall()
		if not result:
			return HttpResponse("error_norole")
		
		role_id = result[0][0]
		role_level = result[0][1]
		
		cur.execute("select account, billno from charge where billno = %s", billno)
		result = cur.fetchall()
		if result:
			#订单号要唯一
			return HttpResponse(Http_Define.Errorbillno)
		
		if not DBHelp.InsertRoleCommand_Cur(cur, role_id, "('Game.ThirdParty.Charge', 'OnCharge', %s)" % cnt ):
			return HttpResponse("error_rolecommamd")
	
		token = uuid.uuid4()
		if pf and Environment.EnvIsNA():
			cur.execute(CHARGE_TK_SQL, (account, role_id, token, billno, realamt, role_level, pf, cnt))
		else:
			cur.execute(CHARGE_SQL, (account, role_id, token, billno, cnt, role_level))
		return HttpResponse("ok")

def TKCharge(request):
	#新的接口
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	unixtime = AutoHTML.AsInt(request.GET, "unixtime")
	billno = AutoHTML.AsString(request.GET, "billno")
	cnt = AutoHTML.AsInt(request.GET, "cnt")
	sign = AutoHTML.AsString(request.GET, "sign")
	pf = AutoHTML.AsInt(request.GET, "pf")
	realamt = AutoHTML.AsInt(request.GET, "realamt")
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(Http_Define.ErrorTime)
	#验证签名
	if sign != md5.new("%s%s%s%s%s%s%s%s" % (serverid, account, billno, cnt, unixtime, pf, realamt, GetKey())).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		cur.execute("select role_id, di32_11 from role_data where account = %s; ", account)
		result = cur.fetchall()
		if not result:
			return HttpResponse("error_norole")
		
		role_id = result[0][0]
		role_level = result[0][1]
		
		cur.execute("select account, billno from charge where billno = %s", billno)
		result = cur.fetchall()
		if result:
			#订单号要唯一
			return HttpResponse(Http_Define.Errorbillno)
		
		if not DBHelp.InsertRoleCommand_Cur(cur, role_id, "('Game.ThirdParty.Charge', 'OnCharge', %s)" % cnt ):
			return HttpResponse("error_rolecommamd")
		
		#把真实货币直接存储在amt里面
		token = uuid.uuid4()
		cur.execute(CHARGE_TK_SQL, (account, role_id, token, billno, cnt, role_level, pf, realamt))
		return HttpResponse("ok")


Permission.reg_develop(Req_DoCharge)
Permission.reg_develop(Res_DoCharge)
Permission.reg_public(DoCharge)

