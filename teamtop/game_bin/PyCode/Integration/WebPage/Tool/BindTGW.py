#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 绑定TGW
#===============================================================================
import copy
import Environment
from django.http import HttpResponse
from ComplexServer.API import QQYun
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>TGW信息</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s<br>
<input type="submit" name="提交" />
</form>
%s<br>
</body>
</html>'''

def Bind(request):
	'''【运维】--TGW信息'''
	if not Environment.EnvIsQQ():
		return HttpResponse("必须是QQ环境")
	# 先清理缓存
	InstanceIdCashe.clear()
	fun = Sel.GetValue(request.POST)
	table = fun()
	return HttpResponse(html % (AutoHTML.GetURL(Bind), Sel.ToHtml(), table.ToHtml()))

def Show():
	bind_info = GetBindInfo()
	# 按照机器名排序
	kv = bind_info.items()
	kv.sort(key=lambda it:it[0])
	body = []
	for name, (ip, tgw_bind, work_bind, need_unbind, need_bind) in kv:
		body.append((name, ip, MakeBindTable(tgw_bind), MakeBindTable(work_bind), MakeBindTable(need_unbind), MakeBindTable(need_bind)))
	table = AutoHTML.Table(["机器名", "机器IP", "已经绑定", "应该绑定", "需要解绑", "需要绑定"], body, "服务端绑定信息")
	return table

def CheckAll():
	bind_info = GetBindInfo()
	# 按照机器名排序
	kv = bind_info.items()
	kv.sort(key=lambda it:it[0])
	body = []
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		for name, (ip, tgw_bind, work_bind, need_unbind, need_bind) in kv:
			# 这里不用自己记录的绑定信息，而是去腾讯查
			tgw_bind = {}
			response = QQYun.get_cvm_bind_info(ip)
			for info in response["domainList"]:
				# 记录端口对应的绑定域名
				tgw_bind[info["port"]] = info["domain"]
				# 记录域名的资源ID缓存
				InstanceIdCashe[info["domain"]] = info["instanceId"]
			# 保存到数据库中去
			cur.execute("update computer_tmp set tgw_bind = %s where name = %s;", (repr(tgw_bind), name))
			# 重新diff
			need_unbind, need_bind = GetBindDiff(tgw_bind, work_bind)
			# 记录在显示table中
			body.append((name, ip, MakeBindTable(tgw_bind), MakeBindTable(work_bind), MakeBindTable(need_unbind), MakeBindTable(need_bind)))
	table = AutoHTML.Table(["机器名", "机器IP", "已经绑定", "应该绑定", "需要解绑", "需要绑定"], body, "服务端绑定信息")
	return table

def FixDiff():
	bind_info = GetBindInfo()
	# 按照机器名排序
	kv = bind_info.items()
	kv.sort(key=lambda it:it[0])
	body = []
	# 批量解绑或者绑定
	group = QQYun.Group()
	for name, (ip, tgw_bind, work_bind, need_unbind, need_bind) in kv:
		for port, domain in need_bind.iteritems():
			instanceid = GetInstanceIdByDomain(domain)
			# 按道理说应该不会有对同一个域名的重复绑定
			assert group.can_bind(instanceid)
			group.bind(instanceid, ip, port)
		for port, domain in need_unbind.iteritems():
			instanceid = GetInstanceIdByDomain(domain)
			group.unbind(instanceid, ip, port)
	group.execute()
	# 总结结果
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		for name, (ip, tgw_bind, work_bind, need_unbind, need_bind) in kv:
			exe = []
			for port, domain in need_bind.iteritems():
				instanceid = GetInstanceIdByDomain(domain)
				result = group.binds[(instanceid, ip, port)]
				if result is True:
					tgw_bind[port] = domain
				else:
					exe.append(result)
			for port, domain in need_unbind.iteritems():
				instanceid = GetInstanceIdByDomain(domain)
				result = group.unbinds[(instanceid, ip, port)]
				if result is True:
					del tgw_bind[port]
				else:
					exe.append(result)
			# 保存到数据库中去
			cur.execute("update computer_tmp set tgw_bind = %s where name = %s;", (repr(tgw_bind), name))
			# 重新diff
			need_unbind, need_bind = GetBindDiff(tgw_bind, work_bind)
			# 显示在表格中
			body.append((name, ip, MakeBindTable(tgw_bind), MakeBindTable(work_bind), MakeBindTable(need_unbind), MakeBindTable(need_bind), repr(exe)))
	table = AutoHTML.Table(["机器名", "机器IP", "已经绑定", "应该绑定", "需要解绑", "需要绑定", "执行问题"], body, "服务端绑定信息")
	return table

def FixAll():
	bind_info = GetBindInfo()
	# 按照机器名排序
	kv = bind_info.items()
	kv.sort(key=lambda it:it[0])
	body = []
	# 批量解绑或者绑定
	group = QQYun.Group()
	for name, (ip, tgw_bind, work_bind, need_unbind, need_bind) in kv:
		# 这里不用自己记录的绑定信息，而是去腾讯查
		tgw_bind = {}
		response = QQYun.get_cvm_bind_info(ip)
		for info in response["domainList"]:
			# 记录端口对应的绑定域名
			tgw_bind[info["port"]] = info["domain"]
			# 记录域名的资源ID缓存
			InstanceIdCashe[info["domain"]] = info["instanceId"]
		# 重新diff
		need_unbind, need_bind = GetBindDiff(tgw_bind, work_bind)
		for port, domain in need_bind.iteritems():
			instanceid = GetInstanceIdByDomain(domain)
			# 按道理说应该不会有对同一个域名的重复绑定
			assert group.can_bind(instanceid)
			group.bind(instanceid, ip, port)
		for port, domain in need_unbind.iteritems():
			instanceid = GetInstanceIdByDomain(domain)
			group.unbind(instanceid, ip, port)
	group.execute()
	# 总结结果
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		for name, (ip, tgw_bind, work_bind, need_unbind, need_bind) in kv:
			exe = []
			for port, domain in need_bind.iteritems():
				instanceid = GetInstanceIdByDomain(domain)
				result = group.binds[(instanceid, ip, port)]
				if result is True:
					tgw_bind[port] = domain
				else:
					exe.append(result)
			for port, domain in need_unbind.iteritems():
				instanceid = GetInstanceIdByDomain(domain)
				result = group.unbinds[(instanceid, ip, port)]
				if result is True:
					del tgw_bind[port]
				else:
					exe.append(result)
			# 保存到数据库中去
			cur.execute("update computer_tmp set tgw_bind = %s where name = %s;", (repr(tgw_bind), name))
			# 重新diff
			need_unbind, need_bind = GetBindDiff(tgw_bind, work_bind)
			# 显示在表格中
			body.append((name, ip, MakeBindTable(tgw_bind), MakeBindTable(work_bind), MakeBindTable(need_unbind), MakeBindTable(need_bind), repr(exe)))
	table = AutoHTML.Table(["机器名", "机器IP", "已经绑定", "应该绑定", "需要解绑", "需要绑定", "执行问题"], body, "服务端绑定信息")
	return table

Sel = AutoHTML.Select()
Sel.Append("显示当前状态", Show)
Sel.Append("全部重新检查", CheckAll)
Sel.Append("差异修正", FixDiff)
Sel.Append("全部修正", FixAll)

def GetBindInfo():
	computers = {}
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		# 获取所有的机器信息
		cur.execute("select name, ip, tgw_bind from computer_tmp where name like 'z%';")
		for name, ip, tgw_bind in cur.fetchall():
			computers[name] = ip, {} if tgw_bind is None else eval(tgw_bind), {}
		# 获取所有的区、进程信息，计算工作区
		# 注意，这里还没处理合服
		cur.execute("select ghl_process_key, public_ip from zone_tmp")
		for ghl_process_key, public_ip in cur.fetchall():
			cur.execute("select computer_name, port from process_tmp where pkey = %s;", ghl_process_key)
			result = cur.fetchall()
			if not result:
				continue
			computer_name = result[0][0]
			# 版本机上的模拟服忽视
			if computer_name.startswith("b"):
				continue
			port = result[0][1]
			work_bind = computers[computer_name][2]
			work_bind[port] = public_ip
	for name, (ip, tgw_bind, work_bind) in computers.items():
		need_unbind, need_bind = GetBindDiff(tgw_bind, work_bind)
		computers[name] = ip, tgw_bind, work_bind, need_unbind, need_bind
	return computers

def GetBindDiff(tgw_bind, work_bind):
	tgw_bind = copy.copy(tgw_bind)
	work_bind = copy.copy(work_bind)
	keys = set(tgw_bind.iterkeys())
	for key in keys:
		if tgw_bind.get(key) == work_bind.get(key):
			del tgw_bind[key]
			del work_bind[key]
	return tgw_bind, work_bind

def MakeBindTable(bind):
	# 按照端口排序
	kv = bind.items()
	kv.sort(key=lambda it:it[0])
	return AutoHTML.MakeInnerTable(kv)

InstanceIdCashe = {}
def GetInstanceIdByDomain(domain):
	if domain not in InstanceIdCashe:
		instanceids = QQYun.get_instance_id(domain)
		for _domain, _instanceid in instanceids["instanceIds"].iteritems():
			InstanceIdCashe[_domain] = _instanceid
	return InstanceIdCashe[domain]

Permission.reg_develop(Bind)
