#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色命令
#===============================================================================
from World import Define
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import WorldHelp
from Integration.WebPage.User import Permission

def Req(request):
	'''【工具】--角色命令'''
	return HttpResponse(html)

def PRes(request):
	return HttpResponse("OK")


def HasExpCommand(command):
	#是否有加经验的指令
	if "IncExp" in command:
		return True
	if "role.SetDI32(11" in command:
		return True
	return False
	

def Res(request):
	role_ids = AutoHTML.AsInts(request.POST, "role_ids")
	zone_id = zone_select.GetValue(request.POST)
	role_names = AutoHTML.AsStrings(request.POST, "role_names")
	accounts = AutoHTML.AsStrings(request.POST, "accounts")
	command = AutoHTML.AsString(request.POST, "command")
	
	#计算正式服角色id
	role_ids_ex = set()
	for role_id in role_ids:
		if DBHelp.GetDBIDByRoleID(role_id) not in Define.TestWorldIDs:
			role_ids_ex.add(role_id)
	
	# 检查权限(没有权限的只能给模拟服发指令)
	if not Permission.check(request, AutoHTML.GetURL(PRes)):
		if role_ids_ex:
			return HttpResponse("你只能给模拟服的角色发指令！！")
		if zone_id not in Define.TestWorldIDs:
			return HttpResponse("你只能给模拟服的角色发指令！！")
	
	#加经验的指令不能用于正式服
	if HasExpCommand(command) is True:
		if zone_id not in Define.TestWorldIDs:
			return HttpResponse("不能给正式服的玩家加经验啊!")
		if role_ids_ex:
			return HttpResponse("不能给正式服的玩家加经验啊!")
	
	# 结果集
	results = []
	# 根据角色ID发送指令
	for role_id in role_ids:
		results.append((role_id, DBHelp.SendRoleCommend(role_id, command)))
	# 根据角色名或者帐号发送指令
	if role_names or accounts:
		con = DBHelp.ConnectMasterDBByID(zone_id)
		with con as cur:
			for role_name in role_names:
				cur.execute("select role_id from role_data where role_name = %s;", role_name)
				result = cur.fetchall()
				if result:
					role_id = result[0][0]
					results.append((role_name, DBHelp.InsertRoleCommand_Cur(cur, role_id, command)))
				else:
					results.append((role_name, "找不到该角色或者已经流失"))
			for account in accounts:
				cur.execute("select role_id from role_data where account = %s;", account)
				result = cur.fetchall()
				if result:
					role_id = result[0][0]
					results.append((account, DBHelp.InsertRoleCommand_Cur(cur, role_id, command)))
				else:
					results.append((account, "找不到该角色或者已经流失"))
	
	if role_ids_ex:
		#发的角色命令中有正式服角色id时才记录
		con = DBHelp.ConnectHouTaiWeb()
		with con as cur:
			#检查下表是否存在
			is_exist = False
			
			cur.execute("show tables")
			for row in cur.fetchall():
				if row[0] == 'role_gm':
					is_exist = True
					break
			
			if is_exist:
				sql = "insert into role_gm(user, role_ids, command, exec_time) values('%s', '%s', '%s', NOW())"
				cur.execute(sql % (request.session.get('user',{}).get('name','unknown')+'/'+request.META['REMOTE_ADDR'],
								','.join(map(str, role_ids_ex)),
								command)
						)
	
	table = AutoHTML.Table(["目标", "结果"], results, "共发送%s个指令" % len(results))
	return HttpResponse(table.ToHtml())

zone_select = AutoHTML.Select("zone_select")
for zone in WorldHelp.GetZone().values():
	zone_select.Append(zone.get_name(), zone.zid)
zone_select.lis.sort(key=lambda it:it[1])
html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色命令</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
<table border='1px' cellspacing='0px'>
<tr><td>根据角色ID发送指令:<br></td><td>根据区+角色名或者帐号发送指令:%s</td></tr>
<tr><td>%s</td><td>
<table border='0px' cellspacing='0px' width='100%%'>
<tr><td>角色名</td><td>帐号</td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>
</td></tr>
<tr><td colspan=2>%s</td></tr>
</table>
<input type="submit" name="发送" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), zone_select.ToHtml(), AutoHTML.ToTextarea("role_ids"), AutoHTML.ToTextarea("role_names"), AutoHTML.ToTextarea("accounts"), AutoHTML.ToTextarea("command"))

Permission.reg_public(Req)
Permission.reg_public(Res)
Permission.reg_develop(PRes)
Permission.reg_log(Res)


