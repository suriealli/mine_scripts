#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.DBMerge")
#===============================================================================
# 数据库合服
#===============================================================================
import cProcess
from ComplexServer.Plug.DB import DBHelp

if "_HasLoad" not in dir():
	MERGE_TABLE = {"role_command" : None,
				"role_command_cache" : None,
				"role_mail" : None,
				"account_login" : None,
				"charge" : None,
				"merge_info" : None,
				"sys_persistence" : None,
				"sys_statistics" : None,
				"connect_info" : None,
				"login_info" : None,
				"online_info" : None,
				"all_role_name" : None,
				"log_base" : None,
				"log_obj" : None,
				"log_value" : None,
				"sys_jjc" : False, 			#删除竞技场数据(游戏逻辑需要修改，合服后重新激活)
				"sys_rolefightdata" : False, #删除战斗数据
				"sys_role_view" : False, 	#删除外观数据
				"sys_role_slave" : False, 	#删除奴隶数据(游戏逻辑需要修改，合服后重新激活)
				"qq_idip_event" : None,
				"report_info": None,
				"sys_herozdl":False,
				"sys_kuafu_jjc": None, 		#跨服数据，不做处理
				"njt_fight_viewdata":None	#跨服数据，不做处理
				}
	MERGE_TABLE_EX = {}
	MERGE_PRESISTENCE = {"BallFameDict" : False, 		#删除一球成名
						"role_flower" : False, 			#删除送花记录
						"Rank_Level" : False, 			#删除等级排行榜
						"Rank_Mount" : False, 			#删除坐骑排行榜
						"Rank_ZDL" : False, 			#删除战斗力排行榜
						"Rank_Purgatory" : False, 		#删除心魔炼狱排行榜
						"Rank_WeddingRing" : False, 	#删除婚戒排行榜
						"Rank_TeamTower" : False, 		#删除组队爬塔排行榜
						"Rank_UnionFB" : False, 		#删除工会副本排行榜
						"jjc_front_list" : False, 		#删除竞技场排名
						"jjc_rear_list" : False, 		#删除竞技场排名
						"WorldCupData" : False, 		#删除世界杯数据
						"The_Niubility_Dict" : False, 	#删除开服BOSS
						"The_Worship_Dict" : False, 	#删除开服BOSS
						"CouplesFB_Rank_List" : False, 	#删除情缘副本排名
						"DukeOnDuty" : False, 			#删除城主轮值数据
						"LuckPool" : False, 			#删除幸运转盘数据
						"rewardrolelist" : False, 		#删除符文宝轮数据
						"HeroAltarRecordList" : False, 	#删除英雄祭坛数据
						"HeroTempleRecordDict" : False, #删除英灵神殿数据
						"WishPoolRecordList" : False, 	#删除需要池数据
						"Rank_BraveHeroScore" : False, 	#删除勇者英雄坛本服排名
						"WonderfulAct" : False, 		#删除已经失效的旧的精彩活动数据
						"AWARDDATA_DICT" : False, 		#删除狂欢充值
						"AWARDLIMIT_LIST" : False, 		#删除狂欢充值
						"PETFARMROLEAWARD_DICT" : False, #删除宠物灵树历史记录
						"rush_level" : False, 			#删除冲级排名
						"DailySecKill_Goods_Dict":False, #删除每日秒杀商品数据
						"The_Niubility_Dict_Hefu" : False, 	#删除合服BOSS
						"The_Worship_Dict_Hefu" : False, 	#删除合服BOSS
						"SuperDiscount_Buy_Record":False, 	#删除超值大礼
						"LimitChestDict":False, 			#删除限次宝箱
						"LuckyBagDict":False, 				#删除福袋
						"LuckyBagCntDict":False, 			#删除福袋每日购买次数 
						"NationDayKillData":False, 		#删除国庆副本全服击杀次数
						"KaifuActDict":False, 			#删除北美开服活动数据
						"HalloweenNaDict":False, 		#删除北美通用活动数据
						"JT_CrossTeamDict":None, 		#跨服数据，不做处理
						"JT_CrossTeamDictNew":None, 		#跨服数据，不做处理
						"JT_FightGroupDict":None, 		#跨服数据，不做处理
						"JT_Final_Dict":None, 			#跨服数据，不做处理
						"JT_Final_Old_Dict":None, 		#跨服数据，不做处理
						"Rank_ZumaUnionScore":None, 	#删除祖玛公会排行榜
						"ZUMA_ROLE_RANK_DICT":None, 	#删除祖玛个人排行字典
						"Rank_MarryQinMi":False, 		#删除亲密排行榜
						"Rank_EquipmentGem":False, 		#删除宝石排行榜
						"Rank_RoleZDL":False, 			#删除主角战力排行榜
						"JT_Final_Role":None, 			#跨服数据，不做处理
						"SevenDayHegemonyDict":None, 		#合服时确认活动已经结束故数据不做处理
						"DKC_ChallengeRecord_Dict":False, 	#删除龙骑试炼数据
						"KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST":None, 	#跨服数据，不做处理
						"KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT":None, 	#跨服数据，不做处理
						"KUAFU_JJC_CROSS_RANK":None, 					#跨服数据，不做处理
						"KUAFU_JJC_CROSS_ZONEID_TO_GROUP":None, 		#跨服数据，不做处理
						"KUAFU_JJC_CROSS_UNION_SCORE":None, 				#跨服数据，不做处理
						"KUAFU_JJC_CROSS_UNION_TODAY_SCORE":None, 		#跨服数据，不做处理
						"KUAFU_JJC_CROSS_UNION_PROCESS_ID":None, 		#跨服数据，不做处理
						"KUAFU_JJC_CROSS_PALACE_DATA":None, 				#跨服数据，不做处理
						"MarryDict":None, 							#旧数据不处理
						"CrazyShopping_Goods_Dict":None, 			#数据不处理
						"CrazyShopping_LuckList":None, 				#数据不处理
						"KUAFU_JJC_FINALS_GUESS_DICT":None, 				#跨服数据，不做处理
						"KuafuPartyDict":None, 						#跨服数据，不做处理
						"Rank_UnionExplore":False, 			#删除公会魔域探秘排行榜
						"HeroShengdianRecordDict" : False, #删除英雄圣殿数据
						"UNION_EXPOLRE_METER_DICT":None, 		#错误的数据
						"UNION_KUAFU_WAR_END_DATA_DICT":False, 	#删除公会圣域争霸活动数据
						"SuperPromption_Buy_Record":False, 		#删除超值特惠购买记录
						"RankClashOfTitansPersonalScore":False, 	#删除诸神之战个人积分排行榜
						"RechargeEverydayRoleDict":False, 			#删除今日首充数据
						"CROSS_TEAM_TOWER_RANK":None, 		#跨服数据不处理
						"JT_ZBSelectData":None, 			#跨服数据不处理
						"NJT_Final_Dict":None, 				#跨服数据不处理
						"NJT_Statue_Data":None, 			#跨服数据不处理
						"NJT_Final_Role":None, 				#跨服数据不处理
						"main_data":False, 					#跨服喝彩错误数据
						"QANDA_ROLE_RANK_LIST":False, 		#删除答题排行榜
						"CatchingFish_RANK_LIST":False,		#删除捕鱼活动
						"HONGBAO_DICT":None, 				#删除红包数据
						"ChaosDivinityBossList":None,		#混沌神域,不做处理
						"ChaosDivinity_BestChallage":None,	#混沌神域排行榜，不作处理
						}

def RegTable(fun):
	MERGE_TABLE[fun.__name__] = fun

def RegTableEx(fun):
	MERGE_TABLE_EX[fun.__doc__] = fun

def RetPersistence(fun):
	MERGE_PRESISTENCE[fun.__name__] = fun

def DoMerge():
	from ComplexServer.Plug.DB import TableMerge
	from ComplexServer.Plug.DB import PersisteneceMerge
	TableMerge, PersisteneceMerge
	
	# 获取所有的表并确保所以的表、持久对象都有合服逻辑
	main_con = DBHelp.ConnectMasterDBByID(cProcess.ProcessID)
	with main_con as main_cur:
		main_cur.execute("show tables;")
		#判断所有的表都有自己的合服处理逻辑
		tables = [row[0] for row in main_cur.fetchall()]
		for table in tables:
			if table.startswith("role_obj"):
				#obj带了后缀，特殊处理，暂时不理会这些表
				continue
			if table not in MERGE_TABLE:
				print "GE_EXC, DoMerge not this table ", table
			assert table in MERGE_TABLE
		#所有的持久化数据也都有自己的合服处理逻辑
		main_cur.execute("select per_key from sys_persistence;")
		for per_key, in main_cur.fetchall():
			if per_key not in MERGE_PRESISTENCE:
				print "GE_EXC, DoMerge not this MERGE_PRESISTENCE ", per_key
			assert per_key in MERGE_PRESISTENCE
	
	# 获取已经合的区
	has_merge_zone_ids = set()
	with main_con as main_cur:
		main_cur.execute("select zone_id from merge_info;")
		for zone_id, in main_cur.fetchall():
			assert zone_id not in has_merge_zone_ids
			has_merge_zone_ids.add(zone_id)
	
	# 获取应该要合的区
	global_con = DBHelp.ConnectGlobalWeb()
	with global_con as global_cur:
		global_cur.execute("select be_merge_zid, merge_zids from zone where zid = %s;" % cProcess.ProcessID)
		global_result = global_cur.fetchall()
		# 当前服务器要被合服，则不做任何处理
		if global_result[0][0]:
			return
		need_merge_zone_ids = set(eval(global_result[0][1]))
	
	if not need_merge_zone_ids:
		#没有需要合的服
		return
	
	# 计算是是否有新合的区
	has_new_merge = False
	for zone_id in need_merge_zone_ids:
		if zone_id in has_merge_zone_ids:
			continue
		has_new_merge = True
		break
	if not has_new_merge:
		#没有需要合的服
		return
	
	# 获取要合的区的信息
	new_merge_zone_ids = []
	extend_merge_zone_ids = []
	global_cur.execute("select zid, be_merge_cnt from zone where be_merge_zid = %s;" % cProcess.ProcessID)
	for zid, be_merge_cnt in global_cur.fetchall():
		#有主区记录(be_merge_zid),则一定是合过服的，断言一下
		assert be_merge_cnt
		#先删除一个，记录一下，等下要判断这个容器是否是空的
		need_merge_zone_ids.remove(zid)
		# 已经合过的区不必再合
		if zid in has_merge_zone_ids:
			continue
		# 合区信息匹配
		if be_merge_cnt == 1:
			#第一次合区
			new_merge_zone_ids.append(zid)
		else:
			extend_merge_zone_ids.append(zid)
	# 配置要匹配(所有要和的区都已经分析好了)
	assert (not need_merge_zone_ids)
	# 获取所有的MySQL连接
	has_merge_cons = []
	new_merge_cons = []
	extend_merge_cons = []
	for zone_id in has_merge_zone_ids:
		merge_con = DBHelp.ConnectMasterDBByID(zone_id)
		has_merge_cons.append(merge_con)
	for zone_id in new_merge_zone_ids:
		merge_con = DBHelp.ConnectMasterDBByID(zone_id)
		new_merge_cons.append(merge_con)
	for zone_id in extend_merge_zone_ids:
		merge_con = DBHelp.ConnectMasterDBByID(zone_id)
		extend_merge_cons.append(merge_con)
	# 处理表
	with main_con as main_cur:
		for table, table_fun in MERGE_TABLE.iteritems():
			if table_fun is None:
				continue
			elif table_fun is False:
				main_cur.execute("delete from %s;" % table)
			else:
				if table == "role_data":
					table_fun(main_cur, has_merge_cons, new_merge_cons, extend_merge_cons)
				else:
					table_fun(main_cur, new_merge_cons, extend_merge_cons)
		# 处理持久化数据
		for per_key, per_fun in MERGE_PRESISTENCE.iteritems():
			if per_fun is None:
				continue
			elif per_fun is False:
				main_cur.execute("delete from sys_persistence where per_key = %s;", per_key)
			else:
				per_fun(main_cur, new_merge_cons, extend_merge_cons)
		# 处理额外表数据
		for _, table_fun in MERGE_TABLE_EX.iteritems():
			table_fun(main_cur, new_merge_cons, extend_merge_cons)
		# 记录处理过的区信息(新合的主区ID)
		for zone_id in new_merge_zone_ids:
			assert main_cur.execute("insert into merge_info (zone_id) values (%s);" % zone_id)
		# 记录(已经被合过的附加区)
		for zone_id in extend_merge_zone_ids:
			assert main_cur.execute("insert into merge_info (zone_id) values (%s);" % zone_id)
		

def RevertDBMerge(funname):
	#只适用于一次合服,并且需要在逻辑进程修复数据
	mergefun = MERGE_PRESISTENCE.get(funname)
	if not mergefun:
		print "GE_EXC RevertDBMerge error not this fun",funname
		return
	main_con = DBHelp.ConnectMasterDBByID(cProcess.ProcessID)
	with main_con as main_cur:
		main_cur.execute("select zone_id from merge_info;")
		new_merge_cons = []
		for zone_id, in main_cur.fetchall():
			merge_con = DBHelp.ConnectMasterDBByID(zone_id)
			new_merge_cons.append(merge_con)
		mergefun(main_cur, new_merge_cons, [])
	

