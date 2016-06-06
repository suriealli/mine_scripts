#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色数据查看
#===============================================================================
import struct
from MySQLdb import cursors
from django.http import HttpResponse
from Common import Serialize, Define, CValue
from ComplexServer.Plug.DB import DBHelp
from Game.Role.Data import EnumInt64, EnumInt32, EnumInt16, EnumInt8, EnumInt1, EnumCD
from Game.Role.Data import EnumDayInt1, EnumDayInt8, EnumDynamicInt64, EnumDisperseInt32
from Game.Role.Data import EnumObj
from Integration import AutoHTML
from Integration.Help import OtherHelp, ConfigHelp
from Integration.WebPage.User import Permission


def Req(request):
	'''【工具】--角色数据'''
	return HttpResponse(html)

RoleColumn = ["account", "role_id", "role_name", "command_size", "command_index"]
RoleArray1 = [("i64", "q", 8, OtherHelp.GetModuleDefine(EnumInt64)),
			("i32", "i", 4, OtherHelp.GetModuleDefine(EnumInt32)),
			("i16", "h", 2, OtherHelp.GetModuleDefine(EnumInt16)),
			("i8", "b", 1, OtherHelp.GetModuleDefine(EnumInt8)),
			("di8", "b", 1, OtherHelp.GetModuleDefine(EnumDayInt8)),
			]
RoleArray2 = [("i1", "B", 1, OtherHelp.GetModuleDefine(EnumInt1)),
			("di1", "B", 1, OtherHelp.GetModuleDefine(EnumDayInt1))]
RoleArray3 = [("cd", OtherHelp.GetModuleDefine(EnumCD)),
			("di64", OtherHelp.GetModuleDefine(EnumDynamicInt64))]
RoleArray4 = [("di32", OtherHelp.GetModuleDefine(EnumDisperseInt32))]
RoleArray5 = [("o", OtherHelp.GetModuleDefine(EnumObj))]

def Res(request):
	roleid = AutoHTML.AsInt(request.POST, "roleid")
	con = DBHelp.ConnectMasterDBRoleID(roleid)
	con.cursorclass = cursors.DictCursor
	html = []
	with con as cur:
		cur.execute("select * from role_data where role_id = %s;" % roleid)
		result = cur.fetchall()
		if not result: return HttpResponse("没有找到该角色！")
		role_data = result[0]
		array = Serialize.String2PyObjEx(role_data["array"])
		role_data["i64"] = array[0]
		role_data["i32"] = array[1]
		role_data["i16"] = array[2]
		role_data["i8"] = array[3]
		role_data["di8"] = array[4]
		role_data["i1"] = array[5]
		role_data["di1"] = array[6]
		role_data["di64"] = array[7]
		role_data["ci8"] = array[8]
		role_data["cd"] = array[9]
		role_data["objs"] = array[10]
		# 基本数据
		body = []
		row = []
		for name in RoleColumn:
			row.append("%s(%s)" % (name, role_data[name]))
		body.append(("基本", "|".join(row)))
		# 数组数据
		for name, s, z, mif, in RoleArray1:
			row = []
			sv = role_data[name]
			sl = struct.unpack(s * (len(sv) / z), sv)
			for k, v, sz in mif:
				if v < len(sl):
					row.append("%s(%s)" % (sz if sz else k, sl[v]))
				else:
					row.append("%s(%s)" % (sz if sz else k, 0))
			body.append((name, "|".join(row)))
		for name, s, z, mif in RoleArray2:
			row = []
			sv = role_data[name]
			sl = struct.unpack(s * (len(sv) / z), sv)
			for k, v, sz in mif:
				idx, bit = divmod(v, 8)
				if idx < len(sl):
					if sl[idx] & (1 << bit):
						row.append("%s(%s)" % (sz if sz else k, True))
					else:
						row.append("%s(%s)" % (sz if sz else k, False))
				else:
					row.append("%s(%s)" % (sz if sz else k, "error"))
			body.append((name, "|".join(row)))
		for name, mif in RoleArray3:
			row = []
			sv = role_data[name]
			sd = sv
			for k, v, sz in mif:
				row.append("%s(%s)" % (sz if sz else k, sd.get(v, 0)))
			body.append((name, "|".join(row)))
		for name, mif in RoleArray4:
			row = []
			for k, v, sz in mif:
				row.append("%s(%s)" % (sz if sz else k, role_data.get("%s_%s" % (name, v), 0)))
			body.append((name, "|".join(row)))
		for name, mif in RoleArray5:
			objs = role_data["objs"]
			for k, v, sz in mif:
				if v < len(objs):
					o = objs[v]
				else:
					o = {}
				body.append((sz if sz else k, AutoHTML.PyObjToHtml(o)))
		html.append(AutoHTML.Table(("名称", "数据"), body, "角色基本数据").ToHtml())
		# OBJ数据
		body = []
		cur.execute("select * from role_obj_%s where role_id = %s;" % (roleid % Define.ROLE_HORIZONTAL_TABLE, roleid))
		for obj in cur.fetchall():
			body.append((obj["obj_id"], ConfigHelp.GetFullNameByCoding(obj["obj_type"]), obj["obj_int"], AutoHTML.PyObjToHtml(Serialize.String2PyObjEx(obj["obj_data"]))))
		html.append(AutoHTML.Table(("对象ID", "对象类型", "对象数值", "对象数据"), body, "角色对象数据").ToHtml())
		# 离线命令
		command_start = (roleid % CValue.P2_32) * CValue.P2_32
		command_end = (roleid % CValue.P2_32 + 1) * CValue.P2_32
		body = []
		cur.execute("select * from role_command where command_id > %s and command_id < %s;" % (command_start, command_end))
		for command in cur.fetchall():
			body.append((command["command_id"], command["command_index"], command["command_datetime"], command["command_text"]))
		html.append(AutoHTML.Table(("命令ID", "索引", "接收时间", "内容"), body, "离线命令").ToHtml())
		# 邮件
		body = []
		cur.execute("select * from role_mail where role_id = %s;" % roleid)
		for mail in cur.fetchall():
			body.append((mail["mail_id"], mail["title"], mail["sender"], mail["dt"], mail["content"], mail["maildata"]))
		html.append(AutoHTML.Table(("邮件ID", "标题", "发送者", "接收时间", "内容", "数据"), body, "邮件").ToHtml())
	
	con.close()
	return HttpResponse("<br>".join(html))

def ExportRole(request):
	roleid = AutoHTML.AsInt(request.GET, "roleid")
	con = DBHelp.ConnectMasterDBRoleID(roleid)
	con.cursorclass = cursors.DictCursor
	with con as cur:
		# 角色数据
		cur.execute("select * from role_data where role_id = %s" % roleid)
		result = cur.fetchall()
		if not result:
			return repr(None)
		role_data = result[0]
		# obj数据
		cur.execute("select * from role_obj_%s where role_id = %s;" % (roleid % Define.ROLE_HORIZONTAL_TABLE, roleid))
		role_obj = cur.fetchall()
		# 离线命令
		cur.execute("select * from role_command where role_id = %s;" % roleid)
		role_command = cur.fetchall()
		# 邮件
		cur.execute("select * from role_mail where role_id = %s;" % roleid)
		role_mail = cur.fetchall()
		return HttpResponse(repr((role_data, role_obj, role_command, role_mail)))

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色数据</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
角色ID：<input type="text" name="roleid"><br>
<input type="submit" name="查询" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), )

Permission.reg_design(Req)
Permission.reg_design(Res)
Permission.reg_public(ExportRole)

