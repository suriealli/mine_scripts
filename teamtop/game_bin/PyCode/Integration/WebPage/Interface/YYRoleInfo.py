#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYRoleInfo")
#===============================================================================
# YY--角色信息
#===============================================================================
import struct
import time
import md5
import json
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me
from Common import Serialize
from ComplexServer.Plug.DB import DBHelp
from Game.Role.Data import EnumInt32

#"nickname" : ""		/*玩家名*/
#"grade" : ""			/*玩家等级*/
#"sex" : ""				/* 性别 */
#"profession" : ""		/* 职业 */
#"createTime": ""		/* 创建时间 */
#"roleId": ""			/*玩家ID*/
#"Reputation" : ,		/* 声望 */
#"Fight" : ,			/* 战斗力 */
#"LastLoginTime" : "",	/* 最后登录时间 */
#"PayStone" : ,			/* 充值神石数量 */
#"RewardStone" :		/* 奖励神石数量 */
#"OnlineTime" : ,		 /* 在线时间 */

Career_Name = {1:"战士", 2:"法师"}
Sex_Name = {1:"m", 2:"f"}
#              玩家id    等级              性别          战斗力             最后活跃时间 总在线时间 创建时间     充值rmb   发放rmb
SQL = "select role_id, di32_11, di32_8, di32_9, di32_7, di32_0, di32_1, di32_10, di32_13, di32_24, role_name, array from role_data where account = %s;"

KEY = "YYRoleInfo_#dsfd0_osd_l1"


def Req_YYRoleInfo(request):
	'''
	【接口】--YY角色查询
	'''
	table = AutoHTML.Table([me.say(request,"区"), "<input type='text' name='server'>"])
	table.body.append([me.say(request,"帐号"), "<input type='text' name='account'>"])
	table.body.append([me.say(request,"游戏编号"), "<input type='text' name='game'>"])
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
	</html>''' % (me.say(request,"YY角色信息"),AutoHTML.GetURL(Res_YYRoleInfo), table.ToHtml(),me.say(request,"查询"))
	return HttpResponse(html)

def Res_YYRoleInfo(request):
	account = AutoHTML.AsString(request.GET, "account")
	game = AutoHTML.AsString(request.GET, "game")
	server = AutoHTML.AsInt(request.GET, "server")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s" % (account,game,server,unixtime,KEY)).hexdigest()
	d = {"account": account,
		"time":unixtime,
		"game":game,
		"server":server,
		"sign" : sign,
		}
	return _RoleInfo(OtherHelp.Request(d))

def YYRoleInfo(request):
	return OtherHelp.Apply(_RoleInfo, request, __name__)

#正式接口
def _RoleInfo(request):
	account = AutoHTML.AsString(request.GET, 'account')
	game = AutoHTML.AsString(request.GET, 'game')
	server = AutoHTML.AsString(request.GET, 'server')
	unixtime = AutoHTML.AsInt(request.GET, 'time')
	sign = AutoHTML.AsString(request.GET, 'sign')
	
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(json.dumps({"retcode" : -1}))
	
	#签名验证
	if sign.lower() != md5.new("%s%s%s%s%s" % (account,game,server,unixtime,KEY)).hexdigest():
		return HttpResponse(json.dumps({"retcode" : -1}))
	
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		return HttpResponse(json.dumps({"retcode" : -3}))
	
	with con as cur:
		cur.execute(SQL, account)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"retcode" : -2}))
		
		#等级              战斗力          性别             最后活跃时间 总在线时间 创建时间     充值rmb   发放rmb
		#Reputation, Physical, GuildId
		role_id, Level, career, Fight, sex, LastLoginTime, OnlineTime, RegisterTime, PayStone, RewardStone, nickname, array = result[0]
		profession = Career_Name.get(career)
		sexN = Sex_Name.get(sex)
		#时间格式转换
		LastLoginTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(LastLoginTime))
		RegisterTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(RegisterTime))
		
		array = Serialize.String2PyObjEx(array)
		i32 = struct.unpack("i" * (len(array[1]) / 4), array[1])
		Reputation = i32[EnumInt32.enReputation]
		
		return HttpResponse(json.dumps({"retcode" : 0,
							"roleinfo":[{"nickname":nickname,
										 "grade":Level,
										 "sex":sexN,
										 "profession":profession,
										 "createTime":str(RegisterTime),
										 "roleId":role_id,
										 "Reputation":Reputation,
										 "Fight":Fight,
										 "LastLoginTime":str(LastLoginTime),
										 "OnlineTime":OnlineTime,
										 "PayStone":PayStone,
										 "RewardStone":RewardStone}]}))

Permission.reg_develop(Req_YYRoleInfo)
Permission.reg_develop(Res_YYRoleInfo)
Permission.reg_public(YYRoleInfo)