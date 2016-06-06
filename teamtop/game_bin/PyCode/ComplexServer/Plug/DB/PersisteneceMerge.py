#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.PersisteneceMerge")
#===============================================================================
# 持久化数据融合
#===============================================================================
import copy
from Common import Serialize
from Common.Other import EnumSysData
from ComplexServer.Plug.DB import DBMerge



def world_data(main_cur, new_merge_cons, extend_merge_cons):
	#世界数据
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'world_data';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
		
		#清理许愿池次数，金币副本次数，通关副本最大ID
		main_data[EnumSysData.WishPoolCnt] = 0
		main_data[EnumSysData.GoldMirrorCnt_1] = 0
		main_data[EnumSysData.GoldMirrorCnt_2] = 0
		main_data[EnumSysData.FBActiveID] = 0

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			#累计左右阵营人数，结婚人数
			main_data[EnumSysData.CampLeftKey] = main_data.get(EnumSysData.CampLeftKey, 0) + merge_data.get(EnumSysData.CampLeftKey, 0)
			main_data[EnumSysData.CampRightKey] = main_data.get(EnumSysData.CampRightKey, 0) + merge_data.get(EnumSysData.CampRightKey, 0)
			main_data[EnumSysData.MarryCnt] = main_data.get(EnumSysData.MarryCnt, 0) + merge_data.get(EnumSysData.MarryCnt, 0)
			
			main_level = main_data.get(EnumSysData.ShenshuLevel, 0)
			merge_level = merge_data.get(EnumSysData.ShenshuLevel, 0)
			
			if main_level < merge_level:
				#合服时区神树等级最高的
				main_data[EnumSysData.ShenshuLevel] = merge_level
				main_data[EnumSysData.ShenshuExp] = merge_data.get(EnumSysData.ShenshuExp, 0)
			
			#秘密花园本服累计次数取最高
			main_data[EnumSysData.SecretGardenServerCnt] = max(main_data.get(EnumSysData.SecretGardenServerCnt, 0), merge_data.get(EnumSysData.SecretGardenServerCnt, 0))

			#超值转盘 本服抽奖次数
			main_data[EnumSysData.SuperTurnTableLotteryCount] = main_data.get(EnumSysData.SuperTurnTableLotteryCount, 0) + merge_data.get(EnumSysData.SuperTurnTableLotteryCount, 0)
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("world_data", main_info, main_data))
	
	print "GREEN, Merge Persistenece world_data ok"

def world_data_notsync(main_cur, new_merge_cons, extend_merge_cons):
	from Game.SysData import WorldDataNotSync
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'world_data_notsync';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	#处理组队爬塔通关次数，所有的服务器加起来
	main_ttfd = main_data.setdefault(WorldDataNotSync.TeamTowerFinishDict, {})
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			
			ttfd = merge_data.get(WorldDataNotSync.TeamTowerFinishDict)
			if not ttfd:
				continue
			for index, cnt in ttfd.iteritems():
				main_ttfd[index] = main_ttfd.get(index, 0) + cnt
				
	main_data[WorldDataNotSync.TeamTowerFinishDict] = main_ttfd
	
	#重置本服今日产出CDK奖励个数
	main_data[WorldDataNotSync.ToDayCDKOutPut] = 0
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("world_data_notsync", main_info, main_data))
	
	print "GREEN, Merge Persistenece world_data_notsync ok"

#def MarryDict(main_cur, new_merge_cons, extend_merge_cons):
#	#{roleID:[roleName, unionName, zdl, weddingRingID]}
#	main_info = {}
#	main_data = {}
#	sql = "select info, data from sys_persistence where per_key = 'MarryDict';"
#	main_cur.execute(sql)
#	main_result = main_cur.fetchall()
#	if main_result:
#		main_info  = Serialize.String2PyObj(main_result[0][0])
#		main_data = Serialize.String2PyObj(main_result[0][1])
#
#	for merge_con in new_merge_cons:
#		with merge_con as merge_cur:
#			merge_cur.execute(sql)
#			row = merge_cur.fetchall()
#			if not row:
#				continue
#			merge_data = Serialize.String2PyObj(row[0][1])
#			for roleId, d in merge_data.iteritems():
#				main_data[roleId] = d
#	main_info = Serialize.PyObj2String(main_info)
#	main_data = Serialize.PyObj2String(main_data)
#	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("MarryDict", main_info, main_data))
#	
#	print "GREEN, Merge Persistenece MarryDict ok"

def MarryID_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#婚礼ID 1000 - 2000
	#{婚礼ID:[男方ID, 女方ID, 时间档, 烟花数量, 表白次数, 礼包数量, 宣誓次数, 是否发放礼包, 婚礼档次]}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'MarryID_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	extendId = 2001
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for marryId, d in merge_data.iteritems():
				if not marryId:
					#融合预约的皇室婚礼时间档
					for timeIndex in d:
						main_data[marryId].add(timeIndex)
					continue
				
				if marryId not in main_data:
					main_data[marryId] = d
					continue
				isOk = False
				marryId = 1000
				for _ in xrange(1000, 2000):
					marryId += 1
					if marryId in main_data:
						continue
					main_data[marryId] = d
					isOk = True
					break
				if isOk is True:
					continue
				extendId += 1
				print "GE_EXC persisteneceMerge MarryID_Dict use extend marryId (%s)" % extendId
				main_data[extendId] = d
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("MarryID_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece MarryID_Dict ok"

def RMBBankDict(main_cur, new_merge_cons, extend_merge_cons):
	#神石银行
	#{roleID:data}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'RMBBankDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("RMBBankDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece RMBBankDict ok"
	
	
def RMBFundDict(main_cur, new_merge_cons, extend_merge_cons):
	#神石基金
	#{1:活动期间累计充值, 2:购买金额, 3:是否领取, 4:天数, 5:活动是否结束}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'RMBFundDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
		nowindex = main_data.get("index")
		if nowindex:
			#合的时候活动没有结束
			for roleId, fundData in main_data.iteritems():
				if roleId == "index":
					continue
				#没有购买基金, 基金已兑换, 活动结束(当前数据记录所对应的活动标识)
				if not fundData[2] or fundData[3] or fundData[5]:
					continue
				#直接满20天
				fundData[4] = 20
				#标记活动结束
				fundData[5] = True
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			nowindex = merge_data.get("index")
			for roleId, fundData in merge_data.iteritems():
				if roleId == "index":
					continue
				main_data[roleId] = fundData
				#没有购买基金, 基金已兑换, 活动结束
				if not fundData[2] or fundData[3] or fundData[5]:
					continue
				if nowindex:
					#合的时候活动没有结束
					#直接满20天
					fundData[4] = 20
					#标记活动结束
					fundData[5] = True
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("RMBFundDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece RMBFundDict ok"

def BraveHeroBossDict(main_cur, new_merge_cons, extend_merge_cons):
	#勇者英雄坛
	#{role_id:[bossIndex, bossHpDict]}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'BraveHeroBossDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, bossMsg in merge_data.iteritems():
				main_data[roleId] = bossMsg
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("BraveHeroBossDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece BraveHeroBossDict ok"
	
def NationBackDict(main_cur, new_merge_cons, extend_merge_cons):
	#神石回赠(所有服的开启天数是一样的, 和服的时候不用处理'begin_days')
	#{'begin_days':活动开启的天数, roleId:{活动开启的天数:[当前天数充值神石数, 当前天数获得经验, 是否领取奖励, 当天开始时的经验]}}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'NationBackDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, nationBackMsg in merge_data.iteritems():
				main_data[roleId] = nationBackMsg
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("NationBackDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece NationBackDict ok"
	
def PETFARMROLECD_DICT(main_cur, new_merge_cons, extend_merge_cons):
	#宠物灵树
	#{roleId:种植时的时间戳}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'PETFARMROLECD_DICT';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("PETFARMROLECD_DICT", main_info, main_data))
	
	print "GREEN, Merge Persistenece PETFARMROLECD_DICT ok"
	
	
def TwelvePalaceDict(main_cur, new_merge_cons, extend_merge_cons):
	#勇闯十二宫
	#{roleId:帮助角色字典{roleid:name,sex,career,grade}}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'TwelvePalaceDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TwelvePalaceDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece TwelvePalaceDict ok"
	
def CollectLongyinDict(main_cur, new_merge_cons, extend_merge_cons):
	#每日集龙印
	#{role_id:{1:累计龙印个数, 2:当天累计充值, 3:{月份:set(天)}, 4:set(当天领取充值奖励集合-每日清理), 5:set(领取收集龙印奖励集合), 6:补签次数}}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'CollectLongyinDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, collectLongyinData in merge_data.iteritems():
				main_data[roleId] = collectLongyinData
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("CollectLongyinDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece CollectLongyinDict ok"



def Rank_QQ(main_cur, new_merge_cons, extend_merge_cons):
	#世界数据
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_QQ';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_QQ", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_QQ ok"

def Rank_Haoqi(main_cur, new_merge_cons, extend_merge_cons):
	#豪气冲天本地充值排行榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_Haoqi';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_Haoqi", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_Haoqi ok"
	
def HQRMB_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#豪气冲天
	#{1:今日充值{role_id --> [今日充值, 是否领取], 2:昨日排行榜数据[[充值, 角色ID, 角色名, 服务器名]]
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'HQRMB_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			if 1 in merge_data:
				for roleId, haoqiData in merge_data[1].iteritems():
					main_data[1][roleId] = haoqiData
				#这里不排序, 载回来的时候长度超过时会排序一次
				main_data[2].extend(merge_data[2])
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("HQRMB_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece HQRMB_Dict ok"

def JTStoreData_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#跨服竞技场金券兑换商店
	#{roleId:{交易index:交易次数}}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JTStoreData_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JTStoreData_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece JTStoreData_Dict ok"



def JT_TeamDict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JT_TeamDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for teamId, data in merge_data.iteritems():
				main_data[teamId] = data
	
	team_Names = set()
	for teamId, data in main_data.items():
		name = data[2]
		if name in team_Names:
			data[2] = str(teamId)
		team_Names.add(name)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JT_TeamDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece JT_TeamDict ok"


def JT_RoleRewardGrade(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JT_RoleRewardGrade';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JT_RoleRewardGrade", main_info, main_data))
	
	print "GREEN, Merge Persistenece JT_RoleRewardGrade ok"


def GroupBuyCarnival_RoleId_List(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'GroupBuyCarnival_RoleId_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("GroupBuyCarnival_RoleId_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece GroupBuyCarnival_RoleId_List ok"

def MarryPartyDict(main_cur, new_merge_cons, extend_merge_cons):
	#PartyID 3000 - 4000
	#{1:{(manId, womenId):{2:高级Party,3:豪华Party,4:今日Party,5:开始时间,6:PartyID,7:{roleid:免费喜糖次数},8:[男方名字, 女方名字],9:{roleid:剩余发放喜糖次数}}}}, 2:{partyId-->(男方ID, 女方ID)}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'MarryPartyDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			
			for partyHostId, partyData in merge_data[1].iteritems():
				main_data[1][partyHostId] = partyData
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("MarryPartyDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece MarryPartyDict ok"

def TG_RechargeReward_UsedCDKRewardId_List(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'TG_RechargeReward_UsedCDKRewardId_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TG_RechargeReward_UsedCDKRewardId_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece TG_RechargeReward_UsedCDKRewardId_List ok"


def JT_ZB_GuessDict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JT_ZB_GuessDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
		
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JT_ZB_GuessDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece JT_ZB_GuessDict ok"

	

def KaifuTarget_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#{'accountSet':已经结算过的活动类型集合, targetType:{(roleId, _):[排名,是否领取奖励, 排行榜数据],}}
	#合服只处理'accountSet', 其他数据不处理了, 策划说开服七天内不会合服
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'KaifuTarget_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
		
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for targetType, data in merge_data.iteritems():
				if targetType != 'accountSet':
					continue
				main_data[targetType] |= data
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("KaifuTarget_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece KaifuTarget_Dict ok"
	
def GroupBuyParty_BuyRecord_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#双十二盛宴-团购派对购买记录
	#{itemIndex:[roleId,],}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'GroupBuyParty_BuyRecord_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for itemIndex, roleIdList in merge_data.iteritems():
				if itemIndex in main_data:
					main_data[itemIndex].extend(roleIdList)
				else:
					main_data[itemIndex] = roleIdList
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("GroupBuyParty_BuyRecord_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece GroupBuyParty_BuyRecord_Dict ok"

def RICH_RANK_CONSUME_RMB_DICT(main_cur, new_merge_cons, extend_merge_cons):
	#累计消耗神石记录
	#{roleId: rmb}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'RICH_RANK_CONSUME_RMB_DICT';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, rmb in merge_data.iteritems():
				main_data[roleId] = rmb
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("RICH_RANK_CONSUME_RMB_DICT", main_info, main_data))
	
	print "GREEN, Merge Persistenece RICH_RANK_CONSUME_RMB_DICT ok"
	
def Rank_DoubleTwelveRich(main_cur, new_merge_cons, extend_merge_cons):
	#双十二富豪榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_DoubleTwelveRich';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_DoubleTwelveRich", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_DoubleTwelveRich ok"
	
def ZUMA_SCORE_DICT(main_cur, new_merge_cons, extend_merge_cons):
	#祖玛最高积分字典
	#{roleId: score}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'ZUMA_SCORE_DICT';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, score in merge_data.iteritems():
				main_data[roleId] = score
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("ZUMA_SCORE_DICT", main_info, main_data))
	
	print "GREEN, Merge Persistenece ZUMA_SCORE_DICT ok"

def Rank_ChristmasHao(main_cur, new_merge_cons, extend_merge_cons):
	#圣诞嘉年华-有钱就是任性本地充值排行榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_ChristmasHao';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_ChristmasHao", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_ChristmasHao ok"

def JT_ServerRewardDict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JT_ServerRewardDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for rewardType, data in merge_data.iteritems():
				if rewardType == 3 and data == 1:
					main_data[rewardType] = 1
					continue
				main_type_data = main_data.get(rewardType)
				if not main_type_data:
					main_data[rewardType] = data
					continue
				for index, teamdata in data.items():
					if not teamdata[4]:
						continue
					main_type_data[index] = teamdata
							
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JT_ServerRewardDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece JT_ServerRewardDict ok"
	
	
def JT_ServerRewardRoleRecord(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JT_ServerRewardRoleRecord';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JT_ServerRewardRoleRecord", main_info, main_data))
	
	print "GREEN, Merge Persistenece JT_ServerRewardRoleRecord ok"

def NYH_List(main_cur, new_merge_cons, extend_merge_cons):
	#新年乐翻天-新年我最壕
	#[[newValue, roleId, role.GetRoleName(), ZoneName.ZoneName]]
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'NYH_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TG_RechargeReward_UsedCDKRewardId_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece NYH_List ok"
	
def SB_List(main_cur, new_merge_cons, extend_merge_cons):
	#新年乐翻天-新年我最壕
	#[[newValue, roleId, role.GetRoleName(), ZoneName.ZoneName]]
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'SB_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("SB_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece SB_List ok"
	
def JTStoreGoods_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#跨服竞技场金券兑换商店当前出售的商品
	#{roleId:[交易id列表]}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JTStoreGoods_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JTStoreGoods_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece JTStoreGoods_Dict ok"


def Rank_NewYearHao(main_cur, new_merge_cons, extend_merge_cons):
	#新年乐翻天
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_NewYearHao';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_NewYearHao", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_NewYearHao ok"

def Rank_SpringBeautiful(main_cur, new_merge_cons, extend_merge_cons):
	#新年乐翻天
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_SpringBeautiful';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_SpringBeautiful", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_SpringBeautiful ok"
	
def PurgatoryBestDict(main_cur, new_merge_cons, extend_merge_cons):
	#心魔炼狱
	#roleid-->[心魔炼狱id，轮数]
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'PurgatoryBestDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("PurgatoryBestDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece PurgatoryBestDict ok"

def LanternFestivalRebateDict(main_cur, new_merge_cons, extend_merge_cons):
	#Index -->{roleID -->roleName}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'LanternFestivalRebateDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for index, dataDict in merge_data.iteritems():
				main_data.setdefault(index, {}).update(dataDict)
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("LanternFestivalRebateDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece LanternFestivalRebateDict ok"


def Rank_LanternFestivalPoint(main_cur, new_merge_cons, extend_merge_cons):
	#元宵节点灯高手排行榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_LanternFestivalPoint';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_LanternFestivalPoint", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_LanternFestivalPoint ok"
	


#def QReport_Dict(main_cur, new_merge_cons, extend_merge_cons):
#	#腾讯罗盘上报数据
#	main_info = {}
#	main_data = {}
#	sql = "select info, data from sys_persistence where per_key = 'QReport_Dict';"
#	main_cur.execute(sql)
#	main_result = main_cur.fetchall()
#	if main_result:
#		main_info  = Serialize.String2PyObj(main_result[0][0])
#		main_data = Serialize.String2PyObj(main_result[0][1])
#
#	for merge_con in new_merge_cons:
#		with merge_con as merge_cur:
#			merge_cur.execute(sql)
#			row = merge_cur.fetchall()
#			if not row:
#				continue
#			merge_data = Serialize.String2PyObj(row[0][1])
#			for days, mergepfData in merge_data.iteritems():
#				if days not in main_data:
#					main_data[days] = mergepfData
#					continue
#				mainPfdata = main_data[days]
#				for pf, priceData in mergepfData.items():
#					if pf not in mainPfdata:
#						mainPfdata[pf] = priceData
#						continue
#					mainpfpricedata = mainPfdata[pf]
#					mainpfpricedata[0] += priceData[0]
#					mainpfpricedata[1] += priceData[1]
#					mainpfpricedata[2] += priceData[2]
#					mainpfpricedata[3] += priceData[3]
#				
#	main_info = Serialize.PyObj2String(main_info)
#	main_data = Serialize.PyObj2String(main_data)
#	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("QReport_Dict", main_info, main_data))
#	
#	print "GREEN, Merge Persistenece QReport_Dict ok"

def RoseRebate_SendRecord_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#玫瑰返利数据 
	#{rebateCategory:set([roleId,]),}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'RoseRebate_SendRecord_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for rebateCategory, roleIdSet in merge_data.iteritems():
				if rebateCategory in main_data:
					main_data[rebateCategory].update(roleIdSet)
				else:
					main_data[rebateCategory] = roleIdSet
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("RoseRebate_SendRecord_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece RoseRebate_SendRecord_Dict ok"

def MarryRing_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#当前佩戴的订婚戒指ID
	#roleid-->当前佩戴的婚戒ID
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'MarryRing_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("MarryRing_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece MarryRing_Dict ok"
	
	
def LanternRankYesterday(main_cur, new_merge_cons, extend_merge_cons):
	#点灯高手昨日排行
	#[[newValue, roleZDL，roleId, role.GetRoleName(), ZoneName.ZoneName]]
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'LanternRankYesterday';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("LanternRankYesterday", main_info, main_data))
	print "GREEN, Merge Persistenece LanternRankYesterday ok"	
	
	
def Rank_GlamourScore(main_cur, new_merge_cons, extend_merge_cons):
	#魅力排行_今日榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_GlamourScore';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_GlamourScore", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_GlamourScore ok"

def YGSR_List(main_cur, new_merge_cons, extend_merge_cons):
	#魅力排行_昨日榜
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'YGSR_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("YGSR_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece YGSR_List ok"
	
def UNION_EXPLORE_METER_DICT(main_cur, new_merge_cons, extend_merge_cons):
	#公会魔域探秘探索度字典
	#{roleId: meter}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'UNION_EXPLORE_METER_DICT';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, score in merge_data.iteritems():
				main_data[roleId] = score
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("UNION_EXPLORE_METER_DICT", main_info, main_data))
	
	print "GREEN, Merge Persistenece UNION_EXPLORE_METER_DICT ok"


def ShenWangBaoKuDict(main_cur, new_merge_cons, extend_merge_cons):
	#{'Pool':奖池神石数, 'ActVersion':活动版本号,'LuckyRoles':[获奖角色数据]}
	#合服只处理'Pool', 其他数据不处理了
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'ShenWangBaoKuDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
		
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for targetType, data in merge_data.iteritems():
				if targetType != 'Pool':
					continue
				main_data['Pool'] = max(main_data.get('Pool', 0), data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("ShenWangBaoKuDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece ShenWangBaoKuDict ok"

def KuafuPartyCntDict(main_cur, new_merge_cons, extend_merge_cons):
	#结婚期间举办的跨服派对次数
	#roleid-->次数
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'KuafuPartyCntDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("KuafuPartyCntDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece KuafuPartyCntDict ok"
	
def Rank_QingMingScore(main_cur, new_merge_cons, extend_merge_cons):
	#清明消费_今日榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_QingMingScore';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_QingMingScore", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_QingMingScore ok"

def YQMCR_List(main_cur, new_merge_cons, extend_merge_cons):
	#清明消费_昨日榜
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'YQMCR_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("YQMCR_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece YQMCR_List ok"

def QinmiLevelDict(main_cur, new_merge_cons, extend_merge_cons):
	#记录的亲密品阶， 用于激活夫妻亲密称号
	#roleid-->亲密品阶
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'QinmiLevelDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("QinmiLevelDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece QinmiLevelDict ok"
	
	
def Rank_WangZheJiFen(main_cur, new_merge_cons, extend_merge_cons):
	#魅力排行_今日榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_WangZheJiFen';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_WangZheJiFen", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_WangZheJiFen ok"

def YWZJFR_List(main_cur, new_merge_cons, extend_merge_cons):
	#魅力排行_昨日榜
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'YWZJFR_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("YWZJFR_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece YWZJFR_List ok"
	
def Rank_PassionRechargeRank(main_cur, new_merge_cons, extend_merge_cons):
	#激情活动充值排行_今日榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_PassionRechargeRank';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_PassionRechargeRank", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_PassionRechargeRank ok"
	
def PRR_List(main_cur, new_merge_cons, extend_merge_cons):
	#激情活动充值排行_昨日榜
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'PRR_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("PRR_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece PRR_List ok"

def Rank_PassionConsumeRank(main_cur, new_merge_cons, extend_merge_cons):
	#激情活动充值排行_今日榜
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'Rank_PassionConsumeRank';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("Rank_PassionConsumeRank", main_info, main_data))
	
	print "GREEN, Merge Persistenece Rank_PassionConsumeRank ok"


def PCR_List(main_cur, new_merge_cons, extend_merge_cons):
	#激情活动充值排行_昨日榜
	main_info = {}
	main_data = []
	sql = "select info, data from sys_persistence where per_key = 'PCR_List';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])

	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.extend(merge_data)
	
	#不进行排序，等载入时候会重新排序一次
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("PCR_List", main_info, main_data))
	
	print "GREEN, Merge Persistenece PCR_List ok"


def TurnTableDict(main_cur, new_merge_cons, extend_merge_cons):
	#全名转转乐个人抽奖数据
	#roleid-->{1:抽奖次数, 2:set(已领取宝箱集合)}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'TurnTableDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TurnTableDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece TurnTableDict ok"
	

def GuBaoTanMi_UnlockReward_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#古堡探秘角色记录数据
	#roleid-->{1:探秘次数, 2:set(已领取累计奖励索引集合)}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'GuBaoTanMi_UnlockReward_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, d in merge_data.iteritems():
				main_data[roleId] = d
				
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("GuBaoTanMi_UnlockReward_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece GuBaoTanMi_UnlockReward_Dict ok"
	
def FlowerMeili_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#鲜花魅力值
	##{1:{男性魅力值}, 2:{女性魅力值}, 3:{活动期间魅力值   活动版本号:{1:{男性数据}, 2:{女性数据}}}, 4:{膜拜字典}}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'FlowerMeili_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			
			#{1:{男性魅力值}, 2:{女性魅力值}, 3:{活动期间魅力值   活动版本号:{1:{男性数据}, 2:{女性数据}}}, 4:{膜拜字典}}
			for index, data in merge_data.iteritems():
				if index in (1, 2, 4):
					#1、2、4字典直接合并
					for roleId, d in data.iteritems():
						main_data[index][roleId] = d
				
				if index == 3:
					#{1:{}, 2:{}}
					for idx in data.iterkeys():
						#需要遍历处理
						for roleId, d in data[idx].iteritems():
							main_data[index][idx][roleId] = d
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("FlowerMeili_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece FlowerMeili_Dict ok"
	
def JTCheers_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#跨服争霸赛喝彩记录
	##{role_id:喝彩次数}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'JTCheers_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			
			for index, data in merge_data.iteritems():
				main_data[index] = data
	
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("JTCheers_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece main_data ok"
	
def NJT_ServerRewardDict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'NJT_ServerRewardDict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for rewardType, data in merge_data.iteritems():
				main_type_data = main_data.get(rewardType)
				if not main_type_data:
					main_data[rewardType] = data
					continue
				for index, teamdata in data.items():
					if not teamdata[4]:
						continue
					main_type_data[index] = teamdata
							
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("NJT_ServerRewardDict", main_info, main_data))
	
	print "GREEN, Merge Persistenece NJT_ServerRewardDict ok"

def NJT_ServerRewardRoleRecord(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'NJT_ServerRewardRoleRecord';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, data in merge_data.iteritems():
				main_data[roleId] = data
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("NJT_ServerRewardRoleRecord", main_info, main_data))
	
	print "GREEN, Merge Persistenece NJT_ServerRewardRoleRecord ok"

def DEGroupBuy_BuyRecord_Dict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'DEGroupBuy_BuyRecord_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for defaultKey, roleIdSet in merge_data.iteritems():
				if defaultKey in main_data:
					main_data[defaultKey].update(roleIdSet)
				else:
					main_data[defaultKey] = roleIdSet
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("DEGroupBuy_BuyRecord_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece DEGroupBuy_BuyRecord_Dict ok"

def TJHC_LotteryRecord_Dict_A(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'TJHC_LotteryRecord_Dict_A';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TJHC_LotteryRecord_Dict_A", main_info, main_data))
	
	print "GREEN, Merge Persistenece TJHC_LotteryRecord_Dict_A ok"

def TJHC_LotteryRecord_Dict_B(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'TJHC_LotteryRecord_Dict_B';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TJHC_LotteryRecord_Dict_B", main_info, main_data))
	
	print "GREEN, Merge Persistenece TJHC_LotteryRecord_Dict_B ok"

def TJHC_NextRoundGambler_Dict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'TJHC_NextRoundGambler_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TJHC_NextRoundGambler_Dict", main_info, main_data))
	
	print "GREEN, Merge Persistenece TJHC_NextRoundGambler_Dict ok"

def TouchGoldReward_Dict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'TouchGoldReward_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("TouchGoldReward_Dict", main_info, main_data))

	print "GREEN, Merge Persistenece TouchGoldReward_Dict ok"


def D12GroupBuy_Record_Dict(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'D12GroupBuy_Record_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result:
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			
			main_day = main_data.get(-1,0)
			merge_day = merge_data.get(-1,0)
			
			if not main_day:main_data = {}
			if not merge_day: merge_data = {}
			
			#同一天则排序
			if main_day == merge_day:
				key_set = set()
				for item_index in main_data.get(1,{}).keys():
					key_set.add(item_index)
				for item_index in merge_data.get(1,{}).keys():
					key_set.add(item_index)
					
				main_dict = main_data[1] = main_data.get(1,{})
				merge_dict = merge_data[1] = merge_data.get(1,{})
				for item_index in key_set:
					main_dict[item_index] = main_dict.get(item_index,[])
					main_dict[item_index].extend(merge_dict.get(item_index,[]))
				
				for item_index,item_info in main_dict.iteritems():
					item_info.sort(key = lambda x:x[1], reverse = False)
			else:
				#删除旧的数据
				if main_day < merge_data:
					main_data = copy.deepcopy(merge_data)
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("D12GroupBuy_Record_Dict", main_info, main_data))

	print "GREEN, Merge Persistenece D12GroupBuy_Record_Dict ok"

def CatchingFish_RANK_LIST(main_cur, new_merge_cons, extend_merge_cons):
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'CatchingFish_RANK_LIST';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result :
		main_info  = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			if "OwnerCalculus" not in main_data :
				main_data["OwnerCalculus"] = []
			main_date_Calculus = main_data["OwnerCalculus"]
			if "OwnerCalculus" not in merge_data :
				merge_data["OwnerCalculus"] = []
			merge_date_Calculus = merge_data["OwnerCalculus"]
			main_date_Calculus.extend(merge_date_Calculus)
			main_date_Calculus.sort(key=lambda x:(-x[0], -x[1]))
			main_date_Calculus = main_date_Calculus
			
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("CatchingFish_RANK_LIST", main_info, main_data))
	print "GREEN, Merge Persistenece CatchingFish_RANK_LIST ok"


def GAME2048_SCORE_DICT(main_cur, new_merge_cons, extend_merge_cons):
	#{roleId:[排行榜数据]}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'GAME2048_SCORE_DICT';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result :
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			for roleId, scoreList in merge_data.iteritems():
				main_data[roleId] = scoreList
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("GAME2048_SCORE_DICT", main_info, main_data))
	print "GREEN, Merge Persistenece GAME2048_SCORE_DICT ok"


def FestivalRebate_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#{roleId:[排行榜数据]}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'FestivalRebate_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result :
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("FestivalRebate_Dict", main_info, main_data))
	print "GREEN, Merge Persistenece FestivalRebate_Dict ok"


def SecretGarden_Dict(main_cur, new_merge_cons, extend_merge_cons):
	#{roleId:[排行榜数据]}
	main_info = {}
	main_data = {}
	sql = "select info, data from sys_persistence where per_key = 'SecretGarden_Dict';"
	main_cur.execute(sql)
	main_result = main_cur.fetchall()
	if main_result :
		main_info = Serialize.String2PyObj(main_result[0][0])
		main_data = Serialize.String2PyObj(main_result[0][1])
	for merge_con in new_merge_cons:
		with merge_con as merge_cur:
			merge_cur.execute(sql)
			row = merge_cur.fetchall()
			if not row:
				continue
			merge_data = Serialize.String2PyObj(row[0][1])
			main_data.update(merge_data)
	main_info = Serialize.PyObj2String(main_info)
	main_data = Serialize.PyObj2String(main_data)
	main_cur.execute("replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)", ("SecretGarden_Dict", main_info, main_data))
	print "GREEN, Merge Persistenece SecretGarden_Dict ok"


if "_HasLoad" not in dir():
	DBMerge.RetPersistence(world_data)
	DBMerge.RetPersistence(world_data_notsync)
#	DBMerge.RetPersistence(MarryDict)
	DBMerge.RetPersistence(MarryID_Dict)
	DBMerge.RetPersistence(RMBBankDict)
	DBMerge.RetPersistence(RMBFundDict)
	DBMerge.RetPersistence(BraveHeroBossDict)
	DBMerge.RetPersistence(NationBackDict)
	DBMerge.RetPersistence(PETFARMROLECD_DICT)
	DBMerge.RetPersistence(TwelvePalaceDict)
	DBMerge.RetPersistence(CollectLongyinDict)
	DBMerge.RetPersistence(Rank_QQ)
	DBMerge.RetPersistence(JT_TeamDict)
	DBMerge.RetPersistence(JT_RoleRewardGrade)
	DBMerge.RetPersistence(Rank_Haoqi)
	DBMerge.RetPersistence(HQRMB_Dict)
	DBMerge.RetPersistence(JTStoreData_Dict)
	DBMerge.RetPersistence(GroupBuyCarnival_RoleId_List)
	DBMerge.RetPersistence(MarryPartyDict)
	DBMerge.RetPersistence(TG_RechargeReward_UsedCDKRewardId_List)
	DBMerge.RetPersistence(KaifuTarget_Dict)
	DBMerge.RetPersistence(GroupBuyParty_BuyRecord_Dict)
	DBMerge.RetPersistence(JT_ZB_GuessDict)
	DBMerge.RetPersistence(RICH_RANK_CONSUME_RMB_DICT)
	DBMerge.RetPersistence(Rank_DoubleTwelveRich)
	DBMerge.RetPersistence(ZUMA_SCORE_DICT)
	DBMerge.RetPersistence(Rank_ChristmasHao)
	DBMerge.RetPersistence(JT_ServerRewardDict)
	DBMerge.RetPersistence(JT_ServerRewardRoleRecord)
	DBMerge.RetPersistence(JTStoreGoods_Dict)
	DBMerge.RetPersistence(NYH_List)
	DBMerge.RetPersistence(Rank_NewYearHao)
#	DBMerge.RetPersistence(QReport_Dict)
	DBMerge.RetPersistence(PurgatoryBestDict)
	DBMerge.RetPersistence(LanternFestivalRebateDict)
	DBMerge.RetPersistence(Rank_LanternFestivalPoint)
	DBMerge.RetPersistence(LanternRankYesterday)
	DBMerge.RetPersistence(MarryRing_Dict)
	DBMerge.RetPersistence(SB_List)
	DBMerge.RetPersistence(Rank_SpringBeautiful)
	DBMerge.RetPersistence(RoseRebate_SendRecord_Dict)	
	DBMerge.RetPersistence(Rank_GlamourScore)
	DBMerge.RetPersistence(YGSR_List)
	DBMerge.RetPersistence(UNION_EXPLORE_METER_DICT)
	DBMerge.RetPersistence(ShenWangBaoKuDict)
	DBMerge.RetPersistence(KuafuPartyCntDict)
	DBMerge.RetPersistence(Rank_QingMingScore)
	DBMerge.RetPersistence(YQMCR_List)
	DBMerge.RetPersistence(QinmiLevelDict)
	DBMerge.RetPersistence(Rank_WangZheJiFen)
	DBMerge.RetPersistence(YWZJFR_List)
	DBMerge.RetPersistence(Rank_PassionRechargeRank)
	DBMerge.RetPersistence(PRR_List)
	DBMerge.RetPersistence(TurnTableDict)
	DBMerge.RetPersistence(GuBaoTanMi_UnlockReward_Dict)
	DBMerge.RetPersistence(FlowerMeili_Dict)	
	DBMerge.RetPersistence(Rank_PassionConsumeRank)
	DBMerge.RetPersistence(PCR_List)
	DBMerge.RetPersistence(JTCheers_Dict)
	DBMerge.RetPersistence(NJT_ServerRewardDict)
	DBMerge.RetPersistence(NJT_ServerRewardRoleRecord)
	
	DBMerge.RetPersistence(DEGroupBuy_BuyRecord_Dict)
	
	DBMerge.RetPersistence(TJHC_LotteryRecord_Dict_A)
	DBMerge.RetPersistence(TJHC_LotteryRecord_Dict_B)
	DBMerge.RetPersistence(TJHC_NextRoundGambler_Dict)
	DBMerge.RetPersistence(TouchGoldReward_Dict)

	DBMerge.RetPersistence(D12GroupBuy_Record_Dict)
#	DBMerge.RetPersistence(CatchingFish_RANK_LIST)
	DBMerge.RetPersistence(GAME2048_SCORE_DICT)

	DBMerge.RetPersistence(FestivalRebate_Dict)
	DBMerge.RetPersistence(SecretGarden_Dict)
	
