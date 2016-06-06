#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYCharge")
#===============================================================================
# YY充值
#===============================================================================
import uuid
import md5
import time
import json
import datetime
import struct
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.model import me
from ComplexServer.API import Define as Http_Define
from Integration.WebPage.pf import server
from Common import Serialize
from Game.Role.Data import EnumInt32
import ComplexServer.API.Define as De
from World import Define

YYHttp_Error1 = "{code:%s, data:{orderid:%s, rmb:%s, account:%s} }"
YYHttp_Error2 = "{code:%s, data:null }"
PaySucc = 1			#充值成功
ParamError = -10	#参数错误
Md5Error = -11		#校验码错误
TimeError = -15		#无效的时间戳
OrderError = -18	#订单号重复
AccountError = -19	#无效的玩家帐号
OtherError = -100	#其他错误

#KEY = "YYcharge_s58g_87dgsawzs"
KEY = 12345
CHARGE_TK_SQL = "insert into charge (account, role_id, token, billno, payamt_coins, dt, level, from_1, from_2, amt) values(%s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s);"

if "_HadLoad" not in dir():
	TIME_TICK = 0		#汇总数据半小时生成一次
	CONTENT_DATA = {}	#页数-数据
	TOTAL_CHARGE = 0	#总的充值金额
	
	
def Req_DoCharge(request):
	'''
	【接口】--第三方充值
	'''
	table = AutoHTML.Table([
		me.say(request,"帐号"),
		"<input type='text' name='account'>"
	])
	table.body.append([
		me.say(request,"订单号"),
		"<input type='text' name='orderid'>"
	])
	table.body.append([
		me.say(request,"充值的人民币"),
		"<input type='text' name='rmb'>"
	])
	table.body.append([
		me.say(request,"游戏币总数"),
		"<input type='text' name='num'>"
	])
	table.body.append([
		me.say(request,"充值渠道名称"),
		"<input type='text' name='type'>"
	])
	table.body.append([
		me.say(request,"游戏名称"),
		"<input type='text' name='game'>"
	])
	table.body.append([
		me.say(request,"合作方服务器名称"),
		"<input type='text' name='server'>"
	])
	table.body.append([
		me.say(request,"角色参数"),
		"<input type='text' name='role'>"
	])
	table.body.append([
		me.say(request,"物品id"),
		"<input type='text' name='itemid'>"
	])
	table.body.append([
		me.say(request,"物品单价"),
		"<input type='text' name='price'>"
	])
	table.body.append([
		me.say(request,"合作方自定义参数"),
		"<input type='text' name='cparam'>"
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
		me.say(request,"YY充值"),
		AutoHTML.GetURL(Res_DoCharge),
		table.ToHtml(),
		me.say(request,"充值")
	)
	return HttpResponse(html)

def Res_DoCharge(request):
	account = AutoHTML.AsString(request.GET, "account")
	role = AutoHTML.AsString(request.GET, 'role')
	billno = AutoHTML.AsString(request.GET, 'orderid')
	rmb = AutoHTML.AsInt(request.GET, "rmb")
	num = AutoHTML.AsInt(request.GET, "num")
	chargetype = AutoHTML.AsString(request.GET, "type")
	game = AutoHTML.AsString(request.GET, "game")
	server = AutoHTML.AsInt(request.GET, "server")
	itemid = AutoHTML.AsString(request.GET, "itemid")
	price = AutoHTML.AsInt(request.GET, "price")
	cparam = AutoHTML.AsString(request.GET, "cparam")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s%s%s%s%s%s%s%s%s" % (account,billno,rmb,num,chargetype,unixtime,game,server,role,itemid,price,cparam,KEY)).hexdigest()
	d = {"account": account,
		"role": role,
		"orderid" :billno,
		"rmb" : rmb,
		"num" : num,
		"time":unixtime,
		"type":chargetype,
		"game":game,
		"server":server,
		"itemid":itemid,
		"sign" : sign,
		"price":price,
		"cparam":cparam
		}
	return _DoCharge(OtherHelp.Request(d))

def YYCharge(request):
	return OtherHelp.Apply(_DoCharge, request, __name__)

def _DoCharge(request):
	account = AutoHTML.AsString(request.GET, "account")
	role = AutoHTML.AsString(request.GET, 'role')
	billno = AutoHTML.AsString(request.GET, 'orderid')
	rmb = AutoHTML.AsInt(request.GET, "rmb")
	num = AutoHTML.AsInt(request.GET, "num")
	unixtime = AutoHTML.AsInt(request.GET, "time")
	chargetype = AutoHTML.AsString(request.GET, "type")
	game = AutoHTML.AsString(request.GET, "game")
	server = AutoHTML.AsInt(request.GET, "server")
	itemid = AutoHTML.AsString(request.GET, "itemid")
	sign = AutoHTML.AsString(request.GET, "sign")
	price = AutoHTML.AsInt(request.GET, "price")
	cparam = AutoHTML.AsString(request.GET, "cparam")
	pf = AutoHTML.AsString(request.GET, "pf")
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(json.dumps({"code":TimeError, "data":None}))
	#签名验证
	if sign != md5.new("%s%s%s%s%s%s%s%s%s%s%s%s%s" % (account,billno,rmb,num,chargetype,unixtime,game,server,role,itemid,price,cparam,KEY)).hexdigest():
		return HttpResponse(json.dumps({"code":Md5Error, "data":None}))
	con = DBHelp.ConnectMasterDBByID(server)
	if not con:
		return HttpResponse(Http_Define.ErrorServer)
	with con as cur:
		cur.execute("select role_id, di32_11 from role_data where account = %s; ", account)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"code":AccountError, "data":None}))
		
		role_id = result[0][0]
		role_level = result[0][1]
		
		cur.execute("select account, billno from charge where billno = %s", billno)
		result = cur.fetchall()
		if result:
			#订单号要唯一
			return HttpResponse(json.dumps({"code":OrderError, "data":{"orderid":billno, "rmb":rmb, "account":account}}))
		
		if not DBHelp.InsertRoleCommand_Cur(cur, role_id, "('Game.ThirdParty.YYCharge', 'OnCharge', %s)" % num ):
			return HttpResponse(json.dumps({"code":OtherError, "data":None}))
	
		#把真实货币直接存储在amt里面
		token = uuid.uuid4()
		#account, role_id, token, billno, payamt_coins, dt, level, from_1, from_2, amt
		#帐号 ------玩家ID----UID----订单号 ----充值总的rmb----时间-- 等级 ---平台 ----充值类型 --总的游戏币 
		cur.execute(CHARGE_TK_SQL, (account, role_id, token, billno, num, role_level, pf, itemid, rmb))
		#return HttpResponse(YYHttp_Error1 % (PaySucc, billno, rmb, account))
		return HttpResponse(json.dumps({"code":PaySucc, "data":{"orderid":billno, "rmb":rmb, "account":account}}))



def Req_YYTotalCharge(request):
	'''
	【接口】--YY充值汇总
	'''
	now = datetime.datetime.now()
	one_day_ago = now - datetime.timedelta(days = 1)
	table = AutoHTML.Table(["开始时间（必填）", "<input type='text' name='start' value='%s' style='width:300'/>" % one_day_ago.strftime("%Y-%m-%d %H:%M:%S")])
	table.body.append(["结束时间（必填）", "<input type='text' name='end' value='%s' style='width:300'/>" % now.strftime("%Y-%m-%d %H:%M:%S")])
	table.body.append([me.say(request,"游戏代号"),"<input type='text' name='game'>"])
	table.body.append([me.say(request,"页数"),"<input type='text' name='page'>"])
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
		me.say(request,"YY充值汇总"),
		AutoHTML.GetURL(Res_YYTotalCharge),
		table.ToHtml(),
		me.say(request,"查询")
	)
	return HttpResponse(html)

TOTAL_KEY = "YYTotalC_dfds878#08fjlk"

def Res_YYTotalCharge(request):
	game = AutoHTML.AsString(request.GET, "game")
	page = AutoHTML.AsInt(request.GET, "page")
	start = AutoHTML.AsDateTime(request.GET, "start")
	end = AutoHTML.AsDateTime(request.GET, "end")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s%s" % (game,start,end,page,unixtime,TOTAL_KEY)).hexdigest()
	d = {
		"game": game,
		"page": page,
		"start": start.strftime('%Y-%m-%d %H:%M:%S'),
		"end": end.strftime('%Y-%m-%d %H:%M:%S'),
		"time":unixtime,
		"sign":sign
		}
#		start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
#	end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
	return _YYTotalCharge(OtherHelp.Request(d))
	
def YYTotalCharge(request):
	return OtherHelp.Apply(_YYTotalCharge, request, __name__)

def _YYTotalCharge(request):
	game = AutoHTML.AsString(request.GET, "game")
	page = AutoHTML.AsInt(request.GET, "page")
	start = AutoHTML.AsDateTime(request.GET, "start")
	end = AutoHTML.AsDateTime(request.GET, "end")
	unixtime = AutoHTML.AsInt(request.GET, "time")
	sign = AutoHTML.AsString(request.GET, "sign")
	
	#验证时间
	if abs(time.time() - unixtime) > 300:
		return HttpResponse(json.dumps({"data":None, "message":De.ErrorTime, "status":300}))
	#签名验证
	if sign != md5.new("%s%s%s%s%s%s" % (game,start,end,page,unixtime,TOTAL_KEY)).hexdigest():
		return HttpResponse(json.dumps({"data":None, "message":De.ErrorSign, "status":304}))
	
	global TOTAL_CHARGE
	global TIME_TICK
	global CONTENT_DATA
	if TIME_TICK and CONTENT_DATA and TOTAL_CHARGE:
		nowTime = int(time.time())
		if abs(nowTime - TIME_TICK) < 900:
			data = CONTENT_DATA.get(page, [])
			return HttpResponse(json.dumps({"data":PackContentData(TOTAL_CHARGE, data, page), "message":1, "status":200}))
	
	
	serverids=server.getAll().keys()
	totalCharge = 0
	SendData = []
	#serverids=[16]
	for sid in serverids:
#		if sid in Define.TestWorldIDs:
#			continue
		if sid >= 30000:
			continue
		con = DBHelp.ConnectMasterDBByID(sid)
		if not con:continue
			
		with con as cur:
			cur.execute("select amt, role_id from charge where dt >= '%s' and dt <= '%s'" % (start, end))
			result = cur.fetchall()
			if not result:
				continue
			roleamt_dict = {}
			for amt, roleid in result:
				if amt == 0 or roleid == 0:
					continue
				roleid = str(roleid)
				totalCharge += amt
				roleamt_dict[roleid] = roleamt_dict.get(roleid, 0) + amt
			roleids = tuple(roleamt_dict.keys())
			if not roleids:
				continue
			cur.execute("select role_id, role_name, account, array from role_data where role_id in (%s);" % (','.join(roleids)))
			result = cur.fetchall()
			if not result:
				continue
			roleu_dict = {}
			union_list = []
			for data in result:
				role_id,role_name, account, array = data
				array = Serialize.String2PyObjEx(array)
				i32 = struct.unpack("i" * (len(array[1]) / 4), array[1])
				unionId = i32[EnumInt32.UnionID]
				union_list.append(str(unionId))
				roleu_dict[role_id] = (unionId, role_id, role_name, account)
			
			#没有公会的直接打包数据
			HasUnion_dict = {}
			for role_id, amtdata in roleu_dict.iteritems():
				unionId, role_id, role_name, account = amtdata
				if not unionId:
					SendData.append(PackData(sid, account, roleamt_dict.get(str(role_id), 0), role_id, role_name, 0, ''))
				else:
					HasUnion_dict[role_id] = amtdata
			
			cur.execute("select union_id, name from sys_union where union_id in (%s);" % (','.join(union_list)))
			result = cur.fetchall()
			if not result:
				continue
			unionData = {}
			for udata in result:
				union_id, union_name = udata
				unionData[union_id] = union_name
			for roleId, roleamt in HasUnion_dict.iteritems():
				unionId, _, role_name, account = roleamt
				union_name = unionData.get(union_id, "")
				SendData.append(PackData(sid, account, roleamt_dict.get(str(roleId), 0), roleId, role_name, union_id, union_name))
	
	TIME_TICK = int(time.time())
	TOTAL_CHARGE = totalCharge
	#分页
	PageData(SendData)
	
	postData = CONTENT_DATA.get(page, [])
	
	return HttpResponse(json.dumps({"data":PackContentData(totalCharge, postData, page), "message":1, "status":200}))

def PageData(SendData):
	#每20份数据一页
	global CONTENT_DATA
	CONTENT_DATA = {}
	pageNum = 0
	length = len(SendData)
	if length % 2 == 0:
		pageNum = len(SendData) / 2
	else:
		pageNum = len(SendData) / 2 + 1
	for i in xrange(pageNum):
		max_t = (i + 1) * 2
		min_t = i * 2
		CONTENT_DATA[i + 1] = SendData[min_t:max_t]
	
def PackContentData(totalCharge, SendData, page):
	global CONTENT_DATA
	return {"total":totalCharge,
	"pageSize":len(CONTENT_DATA),
	"curPage":page,
	"content":SendData,
	}
	
def PackData(server, account, rmb, roleId, roleName, guildId, guildName):
	return {
	"server": server,
	"account": account,
	"rmb": rmb,
	"roleId": roleId,
	"roleName": roleName,
	"guildId": guildId,
	"guildName": guildName
	}
	
Permission.reg_develop(Req_DoCharge)
Permission.reg_develop(Res_DoCharge)
Permission.reg_public(YYCharge)

Permission.reg_develop(Req_YYTotalCharge)
Permission.reg_develop(Res_YYTotalCharge)
Permission.reg_public(YYTotalCharge)