#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 区配置
#===============================================================================
import re
import traceback
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from django.http import HttpResponse
from World import Define
from Integration.WebPage.User import Permission

def IsOnlyComputerPort(cur,cname,port):
	return cur.execute("select pkey from process_tmp where computer_name = %s and port = %s ;",(cname,port)) == 0

def MakeSelect(Name,html=[],value=[],selected=0,label=''):
	s=[u'<label>%s</label><select id="id_%s" name="%s" >'%(label,Name,Name)]
	for n,v in enumerate(value):
		Selected='selected=selected' if n==selected else ''
		s+=[u'<option value="%s" %s >%s</option>'%(v,Selected,html[n])]
	s+=[u'</select>']
	return ''.join(s)

def GetMysqlSelect():
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute('select name from mysql_tmp order by name;')
		html=[ r[0] for r in cur.fetchall()]
	return	MakeSelect('mysql',html,html)
			
def GetHostsSelect():
	con = DBHelp.ConnectGlobalWeb()
	html = []
	value = []
	with con as cur:
		cur.execute('select ip, name from computer_tmp order by name;')
		for ip, name in cur.fetchall():
			html.append("%s.%s" % (ip, name))
			value.append(name)
	return	MakeSelect('host',html,value)

def GetGlobalPkeySelect():
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select pkey from process_tmp where ptype= 'C' order by pkey;")
		html=[ r[0] for r in cur.fetchall()]
	return	MakeSelect('GPkey',html,html)

def GetLanguageSelect():
	return MakeSelect('language', Define.Language,Define.Language)

def isIP(ipstr):
	p=re.compile(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)')
	return True if p.match(ipstr) else False
	
def AddMysql(request):
	con = DBHelp.ConnectGlobalWeb()
	if request.method=="POST":#接收提交信息
		try:
			name=request.POST.get('name','')
			mIp,mPort,mUsr,mPass=request.POST.get('master','').split()
			sIp,sPort,sUsr,sPass=request.POST.get('slave','').split()
		except ValueError:
			return HttpResponse('格式错误!')
		with con as cur:
			cur.execute("select * from mysql_tmp where name = %s or (master_ip = %s and master_port= %s) or ( slave_ip = %s and slave_port= %s); ", (name,mIp,mPort,sIp,sPort))
			result = cur.fetchall()
			if not result:#没有这个实例名
				cur.execute("insert into mysql_tmp(name,master_ip,master_port,master_user,master_pwd,slave_ip,slave_port,slave_user,slave_pwd) \
				values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,mIp,mPort,mUsr,mPass,sIp,sPort,sUsr,sPass))
				return HttpResponse('[%s]增加成功!'%name)
			else:
				return HttpResponse('[%s]已存在<br>%s'%(name,repr(result)))
	# 查找已经存在的数据库
	with con as cur:
		cur.execute("select name, master_ip, master_port, master_user, master_pwd from mysql_tmp order by name;")
		body = cur.fetchall()
	table = AutoHTML.Table(["名称", "主IP", "主端口", "主用户", "主密码"], body)
	html='''
	【配置】--增加Mysql
	<form method="post" action="%s">
	<table>
	<tr><td>实例名:</td><td><input type="text" name="name"></td></tr>
	<tr><td>master地址 端口 用户 密码:</td><td><input type="text" name="master" style="width:300px"></td></tr>
	<tr><td>slave地址 端口 用户 密码:</td><td><input type="text" name="slave" style="width:300px"></td></tr>
	<tr><td></td><td><input type="submit" value="提交"></td></tr>
	</table>
	</form>
	%s
	''' % (AutoHTML.GetURL(AddMysql), table.ToHtml())
	return HttpResponse(html)

def AddComputer(request):
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		if request.method=="POST":#接收提交信息
			name=request.POST.get('name','')
			ip=request.POST.get('ip','')
			public_ip=request.POST.get('public_ip','')
			if name and ip:
				try:
					cur.execute("insert into computer_tmp(name,ip,public_ip) values(%s,%s,%s)",(name,ip,public_ip))
				except:
					return HttpResponse('增加机器错误!')	
		table = AutoHTML.Table(('机器名','地址'))
		cur.execute('select name,ip from computer_tmp order by name;')
		for row in cur.fetchall():
			table.body.append(row)
	html='''
	【配置】--增加机器
	<form method="post" action="%s">
	<table>
	<tr><td>机器名称:</td><td><input type="text" name="name"></td></tr>
	<tr><td>机器地址:</td><td><input type="text" name="ip" style="width:300px"></td></tr>
	<tr><td>机器公网IP:</td><td><input type="text" name="public_ip" style="width:300px"></td></tr>
	<tr><td></td><td><input type="submit" value="提交"></td></tr>
	</table>
	</form>
	已存在机器：
	%s
	''' % (AutoHTML.GetURL(AddComputer), table.ToHtml())

	return HttpResponse(html)

def CopyTmpConfig(request):
	from World import Build
	thisURL=AutoHTML.GetURL(CopyTmpConfig)
	html='''
	【配置】--设置正式配置(当前操作信息都是临时表，操作确认后记得复制到正式表)<br>
	<a href="%s?action=CopyFromTemp">复制到正式表</a>
	<a href="%s?action=CopyToTemp">还原临时表</a>
	'''%(thisURL,thisURL)
	try:
		action=AutoHTML.AsString(request.GET,'action')
		if action=="CopyFromTemp":
			Build.CopyFromTemp()
			return HttpResponse('复制到正式表,执行成功!')
		if action=="CopyToTemp":
			Build.CopyToTemp()
			return HttpResponse('还原临时表,执行成功!')
	except:
		traceback.print_exc()
	return HttpResponse(html)
	
def  AddSingleZone(request):
	html='''
	【配置】--增加单进程区
	<form method="post" action="%s">
	<table>
	<tr><td>区id:</td><td><input type="text" name="zid"></td></tr>
	<tr><td>区名字:</td><td><input type="text" name="zname"></td></tr>
	<tr><td>机器:</td><td>%s</td></tr>
	<tr><td>端口:</td><td><input type="text" name="port"></td></tr>
	<tr><td>对外地址:</td><td><input type="text" name="outside"></td></tr>
	<tr><td>MYSQL:</td><td>%s</td></tr>
	<tr><td>语言包:</td><td>%s</td></tr>
	<tr><td></td><td><input type="submit" value="提交"></td></tr>
	</table>
	</form>
	'''%(AutoHTML.GetURL(AddSingleZone),GetHostsSelect(),GetMysqlSelect(),GetLanguageSelect())
	
	if request.method=="POST":
		zid=AutoHTML.AsInt(request.POST, 'zid')
		zname=AutoHTML.AsString(request.POST, 'zname')
		port=AutoHTML.AsInt(request.POST, 'port')
		outside=AutoHTML.AsString(request.POST, 'outside')
		mysqlname=AutoHTML.AsString(request.POST, 'mysql')
		host=AutoHTML.AsString(request.POST, 'host')
		language=AutoHTML.AsString(request.POST, 'language')
		if zid <= 0:
			return HttpResponse("区ID必须大于0")
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			if not IsOnlyComputerPort(cur,host,port):return HttpResponse('重复监听端口！')
			cur.execute("insert into zone_tmp(zid,name,ztype,all_process_key,mysql_name,public_ip,language,merge_zids) values(%s,%s,'Single',%s,%s,%s,%s,%s)",(zid,zname,'All%s'%zid,mysqlname,outside,language,repr([])))
			cur.execute("insert into process_tmp(pkey,ptype,pid,computer_name,port,bind_zid,work_zid) values(%s,'All',%s,%s,%s,%s,%s)",('All%s'%zid,zid,host,port,zid,zid))
			return HttpResponse('增加单进程区[%s]成功！'%zid)
	return HttpResponse(html)
	
	
def  AddGlobalProcess(request):
	html='''
	【配置】--增加全局进程
	<form method="post" action="%s">
	<table>
	<tr><td>进程id:</td><td><input type="text" name="pid"></td></tr>
	<tr><td>机器:</td><td>%s</td></tr>
	<tr><td>端口:</td><td><input type="text" name="port"></td></tr>
	<tr><td></td><td><input type="submit" value="提交"></td></tr>
	</table>
	</form>
	'''%(AutoHTML.GetURL(AddGlobalProcess),GetHostsSelect())
	
	if request.method=="POST":
		pid=AutoHTML.AsInt(request.POST, 'pid')
		port=AutoHTML.AsInt(request.POST, 'port')
		host=AutoHTML.AsString(request.POST, 'host')
		if pid <= 0:
			return HttpResponse("进程ID必须大于0")
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:#pkey唯一
			if not IsOnlyComputerPort(cur,host,port):return HttpResponse('重复监听端口！')
			cur.execute("insert into process_tmp(pkey,ptype,pid,computer_name,port) values(%s,'C',%s,%s,%s)",('C%s'%pid,pid,host,port))
			return HttpResponse('增加全局进程[%s]成功！'%pid)
	return HttpResponse(html)	

def  AddStandardProcess(request):
	html='''
	【配置】--增加标准进程区
	<form method="post" action="%s">
	<table>
	<tr><td>区id:</td><td><input type="text" name="zid"></td></tr>
	<tr><td>区名字:</td><td><input type="text" name="zname"></td></tr>
	<tr><td>机器:</td><td>%s</td></tr>
	<tr><td>端口:</td><td><input type="text" name="port"></td></tr>
	<tr><td>对外地址:</td><td><input type="text" name="outside"></td></tr>
	<tr><td>MYSQL:</td><td>%s</td></tr>
	<tr><td>全局进程Pkey:</td><td>%s</td></tr>
	<tr><td>语言包:</td><td>%s</td></tr>
	<tr><td></td><td><input type="submit" value="提交"></td></tr>
	</table>
	</form>
	'''%(AutoHTML.GetURL(AddStandardProcess),GetHostsSelect(),GetMysqlSelect(),GetGlobalPkeySelect(),GetLanguageSelect())
	if request.method=="POST":
		zid=AutoHTML.AsInt(request.POST, 'zid')
		zname=AutoHTML.AsString(request.POST, 'zname')
		port=AutoHTML.AsInt(request.POST, 'port')
		outside=AutoHTML.AsString(request.POST, 'outside')
		mysqlname=AutoHTML.AsString(request.POST, 'mysql')
		host=AutoHTML.AsString(request.POST, 'host')
		GPkey=AutoHTML.AsString(request.POST, 'GPkey')
		language=AutoHTML.AsString(request.POST, 'language')
		if zid <= 0:
			return HttpResponse("区ID必须大于0")
		if zid >= 32767:
			return HttpResponse("区ID不能大于32767")
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			if not IsOnlyComputerPort(cur,host,port):return HttpResponse('重复监听端口！')
			cur.execute("insert into zone_tmp(zid,name,ztype,c_process_key,d_process_key,ghl_process_key,mysql_name,public_ip,language,merge_zids) \
			values(%s,%s,'Standard',%s,%s,%s,%s,%s,%s,%s)",(zid,zname,GPkey,'D%s'%zid,'GHL%s'%zid,mysqlname,outside,language,repr([])))#记录区信息
			cur.execute("insert into process_tmp(pkey,ptype,pid,computer_name,port,bind_zid,work_zid) \
			values(%s,'D',%s,%s,%s,%s,%s)",('D%s'%zid,zid,host,10000+zid,zid,zid))#区数据库进程信息
			cur.execute("insert into process_tmp(pkey,ptype,pid,computer_name,port,bind_zid,work_zid) \
			values(%s,'GHL',%s,%s,%s,%s,%s)",('GHL%s'%zid,zid,host,port,zid,zid))#区逻辑进程信息
			return HttpResponse('增加标准进程[%s]成功！'%zid)
	return HttpResponse(html)	

def AddDevice(request):
	'''【配置】--增加设备'''
	s=['''<iframe  src='%s'  style="width:100%%;height:50px""  frameborder="0" marginwidth="0" marginheight="0"></iframe><br><hr>'''%AutoHTML.GetURL(CopyTmpConfig)]
	s+=['''<iframe  src='%s'  style="width:100%%;height:150px""  frameborder="0" marginwidth="0" marginheight="0"></iframe><br><hr>'''%AutoHTML.GetURL(AddMysql)]
	s+=['''<iframe  src='%s'   style="width:100%%;height:60%%"" frameborder="0" marginwidth="0" marginheight="0"></iframe><br><hr>'''%AutoHTML.GetURL(AddComputer)]
	return HttpResponse(''.join(s))
	
def AddZone(request):
	'''【配置】--增加游戏区'''
	con = DBHelp.ConnectGlobalWeb()
	table = AutoHTML.Table(('区id','区名','进程类型'))
	with con as cur:
		cur.execute('select zid,name,ztype from zone_tmp ;')
		for row in cur.fetchall():
			table.body.append(row)
	html=u'''
	<html>
<head>
<style>
body { font-family:Verdana; font-size:18px; margin:10px 10px;}
#container {margin:0 auto; width:100%%;}
#header { height:50px;  margin-bottom:5px;}
#mainContent { height:300px; margin-bottom:5px;}
#sidebar { float:left; width:300px; height:320px; }
#content { margin:10px 355px !important; margin:100px 252px;  height:320px; }
#footer { margin:30px 10px; height:160px; }
</style>
</head>
<body>
<div id="container">
  <div id="header"><iframe  src='%s' height="100%%" width="100%%" frameborder="0" marginwidth="0" marginheight="0"></iframe></div>
  <div id="mainContent">
    <div id="sidebar"><iframe  src='%s' height="100%%" width="350" frameborder="30" marginwidth="0" marginheight="0"></iframe></div>
    <div id="content"><iframe  src='%s' height="100%%" width="350" frameborder="30" marginwidth="0" marginheight="0"></iframe></div>
  </div>
  <div id="footer"><hr>%s</div>
</div>
</body>
</html>'''%(AutoHTML.GetURL(CopyTmpConfig),AutoHTML.GetURL(AddGlobalProcess),AutoHTML.GetURL(AddStandardProcess),table.ToHtml())
	return HttpResponse(html)


Permission.reg_develop(AddMysql)
Permission.reg_develop(AddComputer)
Permission.reg_develop(CopyTmpConfig)
Permission.reg_develop(AddSingleZone)
Permission.reg_develop(AddGlobalProcess)
Permission.reg_develop(AddStandardProcess)
Permission.reg_develop(AddDevice)
Permission.reg_develop(AddZone)

