#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色查询
#===============================================================================
from django.http import HttpResponse
from Common import CValue
from Common.Other import EnumSocial
from ComplexServer.Plug.DB import DBHelp
from Game.Role.Data import EnumDisperseInt32
from Integration import AutoHTML
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me

def Test_GetRoleInfo(request):
	'''
	【接口】--查询角色
	'''
	return HttpResponse(
		html%(
			me.say(request,'查询角色'),
			AutoHTML.GetURL(GetRoleInfo),
			me.say(request,'操作'),
			me.say(request,'角色ID列表'),
			me.say(request,'查询')
		)
	)

def GetRoleInfo(request):
	return OtherHelp.Apply(_GetRoleInfo, request, "RoleQuery.log")

Permission.reg_develop(Test_GetRoleInfo)
Permission.reg_public(GetRoleInfo)

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>%s</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s：<input type="text" name="op"><br>
%s：<input type="text" name="roleids">
<input type="submit" value="%s" />
</form>
</body>
</html>'''

def _GetRoleInfo(request):
	# 获取参数
	op = AutoHTML.AsString(request.POST, "op")
	role_ids = eval(AutoHTML.AsString(request.POST, "roleids"))
	role_ids.sort()
	# 获取查找函数
	fun = globals()[op]
	d = {}
	# 查找之
	last_con = None
	last_dbid = 0
	for role_id in role_ids:
		dbid = DBHelp.GetDBIDByRoleID(role_id)
		if dbid != last_dbid:
			if last_con: last_con.close()
			last_con = DBHelp.ConnectMasterDBByID(dbid)
			last_dbid = dbid
		d[role_id] = fun(last_con, role_id)
	if last_con: last_con.close()
	
	return HttpResponse(repr(d))

# 断言一些数据的取值
assert EnumDisperseInt32.enSex == 7
assert EnumDisperseInt32.enCareer == 8
assert EnumDisperseInt32.ZDL == 9
assert EnumDisperseInt32.enLevel == 11
assert EnumDisperseInt32.enVIP == 12
assert EnumDisperseInt32.HuangZuan_Y_H_L == 17
assert EnumDisperseInt32.LanZuan_Y_H_L == 18
assert EnumDisperseInt32.RoleGrade == 19
assert EnumDisperseInt32.RightMountID == 20
assert EnumDisperseInt32.FTVIP == 21

# di32_0 最后保存时间
# di32_7 性别
# di32_8 职业
# di32_9 战斗力
# di32_11 等级
# di32_12 VIP

Column_RoleName = "role_name"
Column_NoActiveTime = "unix_timestamp(now()) - di32_0"
Column_Sex = "di32_7"
Column_Career = "di32_8"
Column_ZDL = "di32_9"
Column_Level = "di32_11"
Column_VIP = "di32_12"
Column_HuangZuan = "di32_17"
Column_lanZuan = "di32_18"
Column_Grade = "di32_19"
Column_MountID = "di32_20"
Column_FTVIP = "di32_21"

# 查询角色数据的SQL模板
def Make_SQL(*columns):
	return "select %s" % ", ".join(columns) + " from role_data where role_id = %s;"

# 查询好友
SQL_FRIEND = Make_SQL(Column_RoleName, Column_NoActiveTime, Column_Sex, Column_Career, Column_Level, Column_VIP, Column_HuangZuan, Column_lanZuan, Column_Grade, Column_ZDL, Column_FTVIP)
def friend_info(con, roleid):
	'''
	查询好友信息
	@param con:mysql连接
	@param roleid:角色id
	@return: False:角色不存在或者不活跃, 字典:角色信息
	'''
	with con as cur:
		cur.execute(SQL_FRIEND % roleid)
		result = cur.fetchall()
		if not result:
			return False
		role_name, no_active_time, sex, career, level, vip, huangzuan, lanzuan, grade, zdl, ftvip = result[0]
		if no_active_time > DBHelp.TwoWeekSecond:
			return False
		
		#低16位，黄钻等级
		huangLevel = huangzuan % CValue.P2_16
		#高16位，低8位年费，高8位豪华
		huang_nf_hh = huangzuan / CValue.P2_16
		huang_nf = huang_nf_hh % CValue.P2_8
		huang_hh = huang_nf_hh / CValue.P2_8
		
		lanLevel = lanzuan % CValue.P2_16
		lan_nf_hh = lanzuan / CValue.P2_16
		lan_nf = lan_nf_hh % CValue.P2_8
		lan_hh = lan_nf_hh / CValue.P2_8
		
		return {EnumSocial.RoleOnLineKey: False,
				EnumSocial.RoleIDKey: roleid,
				EnumSocial.RoleNameKey: role_name,
				EnumSocial.RoleLevelKey: level,
				EnumSocial.RoleVIPKey: vip,
				EnumSocial.RoleHZKey: huangLevel,
				EnumSocial.RoleLZKey: lanLevel,
				EnumSocial.RoleYHZKey: huang_nf,
				EnumSocial.RoleYLZKey: lan_nf,
				EnumSocial.RoleHHHZKey: huang_hh,
				EnumSocial.RoleHHLZKey: lan_hh,
				EnumSocial.RoleSexKey: sex,
				EnumSocial.RoleCareerKey: career,
				EnumSocial.RoleGradeKey: grade,
				EnumSocial.RoleZDLKey: zdl,
				EnumSocial.FTVIP : ftvip,
				}

# 查询随缘组队
SQL_SELECT_TEAM_ROLE = Make_SQL(Column_RoleName, Column_NoActiveTime, Column_Sex, Column_Career, Column_ZDL, Column_Level, Column_Grade, Column_MountID)
def team_role_info(con, roleid):
	'''
	查询随缘组队角色信息
	@param con:mysql连接
	@param roleid:角色id
	@return: False:角色不存在或者不活跃, 字典:角色信息
	'''
	with con as cur:
		cur.execute(SQL_SELECT_TEAM_ROLE % roleid)
		result = cur.fetchall()
		if not result:
			return False
		role_name, no_active_time, sex, career, zdl, level, grade, mountid = result[0]
		if no_active_time > DBHelp.TwoWeekSecond:
			return False
		return {EnumSocial.RoleIDKey: roleid,
				EnumSocial.RoleNameKey: role_name,
				EnumSocial.RoleLevelKey: level,
				EnumSocial.RoleCareerKey: career,
				EnumSocial.RoleGradeKey: grade,
				EnumSocial.RoleSexKey: sex,
				EnumSocial.RoleZDLKey: zdl,
				EnumSocial.RoleMountIDKey: mountid,
				}

# 查询试练场数据
SQL_SELECT_TRAINING_ROLE = Make_SQL(Column_RoleName, Column_NoActiveTime, Column_Sex, Column_Career, Column_Level, Column_Grade, Column_MountID)
def training_role(con, roleid):
	'''
	查询试练场角色信息
	@param con:mysql连接
	@param roleid:角色id
	@return: False:角色不存在或者不活跃, 字典:角色信息
	'''
	with con as cur:
		cur.execute(SQL_SELECT_TRAINING_ROLE % roleid)
		result = cur.fetchall()
		if not result:
			return False
		role_name, no_active_time, sex, career, level, grade, mountid = result[0]
		if no_active_time > DBHelp.TwoWeekSecond:
			return False
		return {EnumSocial.RoleIDKey: roleid,
				EnumSocial.RoleNameKey: role_name,
				EnumSocial.RoleLevelKey: level,
				EnumSocial.RoleCareerKey: career,
				EnumSocial.RoleGradeKey: grade,
				EnumSocial.RoleSexKey: sex,
				EnumSocial.RoleMountIDKey: mountid,
				}


