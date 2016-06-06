#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.TableMerge")
#===============================================================================
# 表融合
#===============================================================================
from Common import Serialize
from ComplexServer.Plug.DB import DBMerge, SystemTable

#30天没上线，等级小于 40级，没有消费过
DeadTimes = 30 * 24 * 3600 # = 2592000
DeadLevel = 40

def role_data(main_cur, has_merge_cons, new_merge_cons, extend_merge_cons):
	all_role_names = set()
	# 删除死角色
	main_cur.execute("delete from role_data where (unix_timestamp(now()) - di32_0) > 2592000 and di32_11 < 40 and di32_6 = 0")
	main_cur.execute("select role_id, role_name from role_data;")
	for role_id, role_name in main_cur.fetchall():
		if role_name in all_role_names:
			NeedChangeName.setdefault(id(main_cur), []).append(role_id)
		else:
			all_role_names.add(role_name)
	#已经合过的区，默认名字是和主区唯一的
	for has_con in has_merge_cons:
		with has_con as has_cur:
			has_cur.execute("delete from role_data where (unix_timestamp(now()) - di32_0) > 2592000 and di32_11 < 40 and di32_6 = 0")
			has_cur.execute("select role_id, role_name from role_data;")
			for role_id, role_name in has_cur.fetchall():
				all_role_names.add(role_name)
				
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			# 删除死角色
			merge_cur.execute("delete from role_data where (unix_timestamp(now()) - di32_0) > 2592000 and di32_11 < 40 and di32_6 = 0")
			merge_cur.execute("select role_id, role_name from role_data;")
			for role_id, role_name in merge_cur.fetchall():
				if role_name in all_role_names:
					NeedChangeName.setdefault(id(merge_con), []).append(role_id)
				else:
					all_role_names.add(role_name)
				#把角色名字写入主库表中
				main_cur.execute("insert ignore all_role_name (role_name) values(%s);", role_name)
	
	for extend_merge_con in extend_merge_cons:
		with extend_merge_con as extend_merge_cur:
			# 删除死角色
			extend_merge_cur.execute("delete from role_data where (unix_timestamp(now()) - di32_0) > 2592000 and di32_11 < 40 and di32_6 = 0")
			extend_merge_cur.execute("select role_id, role_name from role_data;")
			for role_id, role_name in extend_merge_cur.fetchall():
				if role_name in all_role_names:
					NeedChangeName.setdefault(id(extend_merge_con), []).append(role_id)
				else:
					all_role_names.add(role_name)
				#把角色名字写入主库表中
				main_cur.execute("insert ignore all_role_name (role_name) values(%s);", role_name)
	
	print "BLUE, Merge Table role_data ok"
	
	
def role_data_ex(main_cur, new_merge_cons, extend_merge_cons):
	'''role_data'''
	#替换同名的玩家名字为他的角色ID 
	for role_id in NeedChangeName.get(id(main_cur), []):
		main_cur.execute("update role_data set role_name = %s where role_id = %s;", (str(role_id), role_id))
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			for role_id in NeedChangeName.get(id(merge_con), []):
				merge_cur.execute("update role_data set role_name = %s where role_id = %s;", (str(role_id), role_id))
	
	for extend_merge_con in extend_merge_cons:
		with extend_merge_con as extend_merge_cur:
			for role_id in NeedChangeName.get(id(extend_merge_con), []):
				extend_merge_cur.execute("update role_data set role_name = %s where role_id = %s;", (str(role_id), role_id))
	
	print "BLUE, Merge Table role_data_ex ok"
	
def sys_union(main_cur, new_merge_cons, extend_merge_cons):
	#处理公会
	unoin_names = set()
	main_cur.execute("select name from sys_union;")
	for name, in main_cur.fetchall():
		unoin_names.add(name)
	unoin_id_index = SystemTable.union.GetColumnIndex("union_id")
	unoin_name_index = SystemTable.union.GetColumnIndex("name")
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(SystemTable.union.GetSelectAllValueSQL(""))
			for row in merge_cur.fetchall():
				# 帮派名重复
				if row[unoin_name_index] in unoin_names:
					row = list(row)
					row[unoin_name_index] = str(row[unoin_id_index])
					row = tuple(row)
				unoin_names.add(row[unoin_name_index])
				main_cur.execute(SystemTable.union.GetInsertAllValueSQL(), row)
	
	print "BLUE, Merge Table sys_union ok"

def univerbuy_info(main_cur, new_merge_cons, extend_merge_cons):
	#处理全服团购
	bt_dict = {}
	main_cur.execute("select univerbuy_index, univerbuy_data from univerbuy_info;")
	main_ret = main_cur.fetchall()
	for index, data in main_ret:
		bt_dict[index] = Serialize.String2PyObj(data)
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute("select univerbuy_index, univerbuy_data from univerbuy_info;")
			merge_ret = merge_cur.fetchall()
			for index, data in merge_ret:
				univerbuy_set = Serialize.String2PyObj(data)
				if not univerbuy_set:
					continue
				btdata = bt_dict.get(index)
				if not btdata:
					bt_dict[index] = univerbuy_set
				else:
					btdata.update(univerbuy_set)
	#重新写入主数据库
	for newIndex, newData in bt_dict.iteritems():
		main_cur.execute("replace into univerbuy_info (univerbuy_index, univerbuy_data) values (%s, %s)", (newIndex, Serialize.PyObj2String(newData)))
	
	print "BLUE, Merge Table univerbuy_info ok"
	
#WONDEFUL_INDEX_4  = 4	#记录全服4-7级vip的人数｛viplevel : cnt｝@合服处理
#WONDEFUL_INDEX_11 = 11	#记录当前激活的奖励ID（有时限） {actId :set(rewardIds)}@合服处理
#WONDEFUL_INDEX_12 = 12	#记录一些可以领取几次的奖励ID｛奖励ID : cnt｝@合服处理(清理)
#WONDEFUL_INDEX_15 = 15	#记录全服8-10级vip的人数｛vipLevel : {1 : cnt, 2 : nameList} ｝@合服处理
def sys_wonderfulactdata(main_cur, new_merge_cons, extend_merge_cons):
	#处理精彩活动
	bt_dict = {}
	main_cur.execute("select wonderful_index, wonderful_data from sys_wonderfulactdata;")
	main_ret = main_cur.fetchall()
	for index, data in main_ret:
		bt_dict[index] = Serialize.String2PyObj(data)
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute("select wonderful_index, wonderful_data from sys_wonderfulactdata;")
			merge_ret = merge_cur.fetchall()
			for index, data in merge_ret:
				if index not in (4, 15):
					continue
				bt_index_data = bt_dict.get(index)
				data = Serialize.String2PyObj(data)
				if not bt_index_data:
					bt_dict[index] = data
					continue
				if index == 4:
					for vipLevel, cnt in data.iteritems():
						bt_index_data[vipLevel] = bt_index_data.get(vipLevel, 0) + cnt
				elif index == 15:
					for vipLevel, d in data.iteritems():
						levelData = bt_index_data.get(vipLevel)
						if not levelData:
							bt_index_data[vipLevel] = d
						else:
							levelData[1] += d[1]
							levelData[3] = levelData.get(3, 0) + d.get(3, 0)

	
	bt_index_data = bt_dict.get(15)
	if bt_index_data:
		for levelData in bt_index_data.itervalues():
			levelData[2] = []
			levelData[1] += levelData.get(3, 0)
			levelData[3] = 0
	
	#重新写入数据库
	for newIndex, newData in bt_dict.iteritems():
		main_cur.execute("replace into sys_wonderfulactdata (wonderful_index, wonderful_data) values (%s, %s)", (newIndex, Serialize.PyObj2String(newData)))

	print "BLUE, Merge Table sys_wonderfulactdata ok"
	
def sys_ring(main_cur, new_merge_cons, extend_merge_cons):
	#订婚戒指数据
	tableName = "sys_ring"
	bt_dict = {}
	main_cur.execute("show tables;")
	maintables = [row[0] for row in main_cur.fetchall()]
	if tableName not in maintables:
		#新表，直接不处理
		return
	
	main_cur.execute("select role_id, ringData from sys_ring;")
	main_ret = main_cur.fetchall()
	for index, data in main_ret:
		bt_dict[index] = Serialize.String2PyObj(data)
		
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute("show tables;")
			mergetables = [row[0] for row in merge_cur.fetchall()]
			#需要判断从区是否有这个表
			if tableName in mergetables:
				merge_cur.execute("select role_id, ringData from sys_ring;")
				merge_ret = merge_cur.fetchall()
				for index, data in merge_ret:
					bt_dict[index] = Serialize.String2PyObj(data)
		
	#重新写入主数据库
	for newIndex, newData in bt_dict.iteritems():
		main_cur.execute("replace into sys_ring (role_id, ringData) values (%s, %s)", (newIndex, Serialize.PyObj2String(newData)))
	
	print "BLUE, Merge Table sys_ring ok"
	
if "_HasLoad" not in dir():
	NeedChangeName = {}
	DBMerge.RegTable(role_data)
	DBMerge.RegTableEx(role_data_ex)
	
	DBMerge.RegTable(sys_union)
	DBMerge.RegTable(univerbuy_info)
	DBMerge.RegTable(sys_wonderfulactdata)
	DBMerge.RegTable(sys_ring)
