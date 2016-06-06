#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 系统表定义
#===============================================================================
import cProcess
from Common import CValue
from ComplexServer.Plug.DB import Column
from Util.MySQL import DynamicTable, DynamicColumn

def ColletTable():
	'''
	构建本模块定义的表
	'''
	se = set()
	for value in globals().itervalues():
		if not isinstance(value, DynamicTable.Table):
			continue
		if value in se:
			continue
		se.add(value)
		Tables[value.name] = value

def BuildTable():
	'''
	构建本模块定义的表
	'''
	# 连接MySQL，并且构建数据库
	DynamicTable.MySQL.Init(cProcess.ProcessID)
	DynamicTable.MySQL.UserTable("role_sys_data_%s" % cProcess.ProcessID)
	# 构建表
	for table in Tables.itervalues():
		table.Build()
	# 关闭MySQL
	DynamicTable.MySQL.Final()

def GetTableByName(name):
	return Tables[name]

def GetPRIByName(name):
	return Tables[name].pri

#===============================================================================
# 表定义(注意表名要全小写字母)
#===============================================================================
#持久化数据
persistence = DynamicTable.Table("sys_persistence")
persistence.AddColumn(DynamicColumn.StringColumn("per_key", 60, "持久化数据的唯一Key"))
persistence.AddColumn(DynamicColumn.DateTimeColumn("save_datetime", "持久化数据的最后保存时间"))
persistence.AddColumn(DynamicColumn.SmallObjColumn("info", "持久化数据的自用信息"))
persistence.AddColumn(DynamicColumn.MediumObjColumn("data", "持久化数据的客户数据"))
persistence.AddKey(DynamicColumn.ToPRI("per_key"))

#公会(修改结构的是需要考虑合服)
union = DynamicTable.Table("sys_union")
union.AddColumn(DynamicColumn.IntColumn("union_id", "int", True, False, "公会ID"))
union.AddColumn(DynamicColumn.IntColumn("camp_id", "tiny", True, False, "阵营ID"))
union.AddColumn(DynamicColumn.IntColumn("leader_id", "big", True, False, "会长ID"))
union.AddColumn(DynamicColumn.IntColumn("level", "small", True, False, "公会等级"))
union.AddColumn(DynamicColumn.IntColumn("exp", "big", True, False, "公会经验"))
union.AddColumn(DynamicColumn.IntColumn("population", "small", True, False, "公会当前最大人口"))
union.AddColumn(DynamicColumn.IntColumn("resource", "big", True, False, "公会资源"))
union.AddColumn(DynamicColumn.StringColumn("name", 60, "公会名字"))
union.AddColumn(DynamicColumn.StringColumn("leader_name", 60, "团长名字"))
union.AddColumn(DynamicColumn.StringColumn("notice", 200, "公会公告"))
union.AddColumn(DynamicColumn.ObjColumn("news", "公会广播"))
union.AddColumn(DynamicColumn.ObjColumn("members", "公会成员"))
union.AddColumn(DynamicColumn.ObjColumn("election", "公会选举"))
union.AddColumn(DynamicColumn.ObjColumn("treasure", "公会夺宝"))
union.AddColumn(DynamicColumn.ObjColumn("god", "公会魔神"))
union.AddColumn(DynamicColumn.ObjColumn("fb", "公会副本"))
union.AddColumn(DynamicColumn.ObjColumn("other_data", "公会其它信息"))
union.AddKey(DynamicColumn.ToPRI("union_id"))

#竞技场(修改结构的是需要考虑合服)
jjc = DynamicTable.Table("sys_jjc")
jjc.AddColumn(Column.role_id)
jjc.AddColumn(Column.role_name)
jjc.AddColumn(DynamicColumn.IntColumn("role_level", "int", True, False, "等级"))
jjc.AddColumn(DynamicColumn.IntColumn("role_sex", "small", True, False, "性别"))
jjc.AddColumn(DynamicColumn.IntColumn("role_grade", "small", True, False, "品阶"))
jjc.AddColumn(DynamicColumn.IntColumn("role_career", "small", True, False, "职业"))
jjc.AddColumn(DynamicColumn.IntColumn("role_zdl", "int", True, False, "战斗力"))
jjc.AddColumn(DynamicColumn.IntColumn("role_wing_id", "small", True, False, "翅膀ID"))
jjc.AddColumn(DynamicColumn.StringColumn("role_union_name", 60, "军团名字"))
jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_clithes", "int", True, False, "时装衣服ID"))
jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_hat", "int", True, False, "时装帽子ID"))
jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_weapons", "int", True, False, "时装武器ID"))
jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_state", "small", True, False, "时装是否显示状态"))
jjc.AddColumn(DynamicColumn.IntColumn("role_war_station", "int", True, False, "战阵星级"))
jjc.AddColumn(DynamicColumn.IntColumn("role_station_soul", "int", True, False, "阵灵ID"))
jjc.AddKey(DynamicColumn.ToPRI(Column.role_id))

#英雄战力排行榜
herozdl = DynamicTable.Table("sys_herozdl")
herozdl.AddColumn(Column.role_id)
herozdl.AddColumn(DynamicColumn.ObjColumn("herodata", "英雄数据"))
herozdl.AddKey(DynamicColumn.ToPRI(Column.role_id))

#统计
statistics = DynamicTable.Table("sys_statistics")
statistics.AddColumn(DynamicColumn.StringColumn("skey", "60", "统计项"))
statistics.AddColumn(DynamicColumn.IntColumn("roles", "int", False, False, "人数"))
statistics.AddColumn(DynamicColumn.IntColumn("count", "int", False, False, "次数"))
statistics.AddColumn(DynamicColumn.IntColumn("min_count", "int", False, False, "最小次数"))
statistics.AddColumn(DynamicColumn.IntColumn("max_count", "int", False, False, "最大次数"))
statistics.AddColumn(DynamicColumn.DateTimeColumn("dt", "保持时间"))
statistics.AddKey(DynamicColumn.ToMUL("skey"))

#战斗数据(修改结构的是需要考虑合服)
roleFightData = DynamicTable.Table("sys_rolefightdata")
roleFightData.AddColumn(Column.role_id)
roleFightData.AddColumn(DynamicColumn.ObjColumn("fightData", "战斗数据"))
roleFightData.AddKey(DynamicColumn.ToPRI(Column.role_id))

#角色外观数据(前200名)(修改结构的是需要考虑合服)
roleViewData = DynamicTable.Table("sys_role_view")
roleViewData.AddColumn(Column.role_id)
roleViewData.AddColumn(DynamicColumn.ObjColumn("viewData", "外观数据"))
roleViewData.AddKey(DynamicColumn.ToPRI(Column.role_id))

#奴隶系统(修改结构的是需要考虑合服)
roleSlaveData = DynamicTable.Table("sys_role_slave")
roleSlaveData.AddColumn(Column.role_id)
roleSlaveData.AddColumn(DynamicColumn.ObjColumn("slaveData", "奴隶系统数据"))
roleSlaveData.AddKey(DynamicColumn.ToPRI(Column.role_id))

#精彩活动(修改结构的是需要考虑合服)
sys_wonderfulactdata = DynamicTable.Table("sys_wonderfulactdata")
wa_index = DynamicColumn.IntColumn("wonderful_index", "int", False, False, "精彩活动数据存储编号")
sys_wonderfulactdata.AddColumn(wa_index)
sys_wonderfulactdata.AddColumn(DynamicColumn.ObjColumn("wonderful_data", "精彩活动数据"))
sys_wonderfulactdata.AddKey(DynamicColumn.ToPRI(wa_index))


# 连接信息（流失统计）
connect_info = DynamicTable.Table("connect_info", CValue.P2_32 * cProcess.ProcessID + 1, {})
connect_info.AddColumn(DynamicColumn.IntColumn("cid", "bigint", True, True, "连接id"))
connect_info.AddColumn(Column.account)
connect_info.AddColumn(Column.userip)
connect_info.AddColumn(DynamicColumn.DateTimeColumn("connect_time", "连接时间"))
connect_info.AddColumn(DynamicColumn.IntColumn("request_create", "tinyint", True, False, "请求创建角色次数"))
connect_info.AddColumn(DynamicColumn.IntColumn("first_operate", "tinyint", True, False, "是否有第一次操作"))
connect_info.AddColumn(Column.from_1)
connect_info.AddColumn(Column.from_2)
connect_info.AddColumn(Column.from_3)
connect_info.AddColumn(DynamicColumn.StringColumn("status"))
connect_info.AddKey(DynamicColumn.ToPRI("cid"))
connect_info.AddKey(DynamicColumn.ToUNI(Column.account))

# 登录信息（流失统计）
login_info = DynamicTable.Table("login_info", CValue.P2_32 * cProcess.ProcessID + 1, {})
login_info.AddColumn(DynamicColumn.IntColumn("lid", "bigint", True, True, "登录id"))
login_info.AddColumn(Column.account)
login_info.AddColumn(Column.userip)
login_info.AddColumn(DynamicColumn.DateTimeColumn("login_day", "登录日期"))
login_info.AddColumn(DynamicColumn.IntColumn("lkey", "bigint", True, False, "登录key（用于限定每日只记录一次登录）"))
login_info.AddColumn(Column.from_1)
login_info.AddColumn(Column.from_2)
login_info.AddColumn(Column.from_3)
login_info.AddKey(DynamicColumn.ToPRI("lid"))
login_info.AddKey(DynamicColumn.ToUNI("lkey"))

# 在线信息（在线统计）
online_info = DynamicTable.Table("online_info", CValue.P2_32 * cProcess.ProcessID + 1, {})
online_info.AddColumn(DynamicColumn.IntColumn("roles", "smallint", True, False, "角色数"))
online_info.AddColumn(DynamicColumn.IntColumn("ips", "smallint", True, False, "IP数"))
online_info.AddColumn(DynamicColumn.DateTimeColumn("sta_time", "统计时间"))

#所有的玩家名字
all_role_name = DynamicTable.Table("all_role_name")
all_role_name.AddColumn(Column.role_name)
all_role_name.AddKey(DynamicColumn.ToPRI(Column.role_name))

#全民团购(修改结构的是需要考虑合服)
univerbuy_info = DynamicTable.Table("univerbuy_info")
ub_index = DynamicColumn.IntColumn("univerbuy_index", "int", False, False, "全民团购数据存储编号")
univerbuy_info.AddColumn(ub_index)
univerbuy_info.AddColumn(DynamicColumn.ObjColumn("univerbuy_data", "全民团购数据"))
univerbuy_info.AddKey(DynamicColumn.ToPRI(ub_index))


#idip事件
qq_idip_event = DynamicTable.Table("qq_idip_event")
qq_idip_event.AddColumn(Column.role_id)
qq_idip_event.AddColumn(Column.account)

qq_idip_event.AddColumn(DynamicColumn.IntColumn("event_allot_id", "bigint", True, False, "唯一ID"))
qq_idip_event.AddColumn(DynamicColumn.IntColumn("event_id", "int", False, False, "事件ID"))
qq_idip_event.AddColumn(DynamicColumn.IntColumn("event_num", "int", False, False, "事件完成次数"))
qq_idip_event.AddColumn(DynamicColumn.DateTimeColumn("event_time", "事件记录时间"))
qq_idip_event.AddKey(DynamicColumn.ToMUL("role_id"))
qq_idip_event.AddKey(DynamicColumn.ToMUL("account"))
qq_idip_event.AddKey(DynamicColumn.ToMUL("event_id"))
qq_idip_event.AddKey(DynamicColumn.ToPRI("event_allot_id"))

#跨服竞技场
kuafu_jjc = DynamicTable.Table("sys_kuafu_jjc")
kuafu_jjc.AddColumn(Column.role_id)
kuafu_jjc.AddColumn(Column.role_name)
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_level", "int", True, False, "等级"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_sex", "small", True, False, "性别"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_grade", "small", True, False, "品阶"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_career", "small", True, False, "职业"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_zdl", "int", True, False, "战斗力"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_wing_id", "small", True, False, "翅膀ID"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_clithes", "int", True, False, "时装衣服ID"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_hat", "int", True, False, "时装帽子ID"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_weapons", "int", True, False, "时装武器ID"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_fashion_state", "small", True, False, "时装是否显示状态"))
kuafu_jjc.AddColumn(DynamicColumn.ObjColumn("role_fight_data", "战斗数据"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_election_score", "int", True, False, "海选积分"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_finals_score", "int", True, False, "决赛积分"))
kuafu_jjc.AddColumn(DynamicColumn.StringColumn("role_zone_name", 60, "服务器名字"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_war_station", "int", True, False, "战阵星级"))
kuafu_jjc.AddColumn(DynamicColumn.IntColumn("role_station_soul", "int", True, False, "阵灵ID"))
kuafu_jjc.AddKey(DynamicColumn.ToPRI(Column.role_id))

#订婚戒指数据(修改结构的是需要考虑合服)
ringData = DynamicTable.Table("sys_ring")
ringData.AddColumn(Column.role_id)
ringData.AddColumn(DynamicColumn.ObjColumn("ringData", "订婚戒指数据"))
ringData.AddKey(DynamicColumn.ToPRI(Column.role_id))

#跨服争霸赛观战数据
NJT_Fiht_ViewData = DynamicTable.Table("njt_fight_viewdata")
group_index = DynamicColumn.IntColumn("group_index", "int", False, False, "战区编号")
NJT_Fiht_ViewData.AddColumn(group_index)
NJT_Fiht_ViewData.AddColumn(DynamicColumn.ObjColumn("FightViewData", "观战数据"))
NJT_Fiht_ViewData.AddKey(DynamicColumn.ToPRI(group_index))

if "_HasLoad" not in dir():
	Tables = {}
	ColletTable()


