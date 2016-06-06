#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQSystemRank")
#===============================================================================
# 腾讯查询系统排行榜
#===============================================================================
from Common import Serialize
from ComplexServer.Plug.DB import DBHelp

'''
	"body" :
	{
		"AreaId" : ,	 /* 所在大区ID */
		"Type" : ,	   /* 排行榜类型 */
		"PageNo" : ,	 /* 页码 */
		"DataNum" :	  /* 条数 */
	}
	
	 "body" :
    {
        "GameRankList_count" : ,    /* 游戏排行榜信息列表的最大数量 */
        "GameRankList" :            /* 游戏排行榜信息列表 */
        [
            {
                "RoleId" : "",          /* 角色ID */
                "RoleName" : "",        /* 角色名 */
                "PageNo" : ,            /* 页码 */
        		"TotalPageCount" :      /* 总条数 */
            }
        ]
        
    }
	
'''

#页码从0 开始
#每页最大30条
SQL_1 = "select data from sys_persistence where per_key = 'Rank_Level';"
SQL_2 = "select data from sys_persistence where per_key = 'Rank_ZDL';"
SQL_3 = "select data from sys_persistence where per_key = 'Rank_Mount';"
SQL_4 = "select data from sys_persistence where per_key = 'Rank_WeddingRing';"

def GetRank_1(con):
	with con as cur:
		cur.execute(SQL_1)
		result = cur.fetchall()
		if not result:
			return []
		data = Serialize.String2PyObj(result[0][0])
		l = []
		LA = l.append
		#(name, level, zdl, flower, exp)
		for roleid, d in data.iteritems():
			#roleid, name level zdl exp
			LA((roleid, d[0], d[1], d[2], d[4]))
		l.sort(key = lambda it:(it[2], it[4]), reverse = True)
		return l

def GetRank_2(con):
	with con as cur:
		cur.execute(SQL_2)
		result = cur.fetchall()
		if not result:
			return []
		data = Serialize.String2PyObj(result[0][0])
		l = []
		LA = l.append
		#name, level, zdl, flower, roleId
		for roleid, d in data.iteritems():
			#roleid, name zdl 
			LA((roleid, d[0], d[2],))
		l.sort(key = lambda it:it[2], reverse = True)
		#只要角色ID 和名字
		return l

def GetRank_3(con):
	with con as cur:
		cur.execute(SQL_3)
		result = cur.fetchall()
		if not result:
			return []
		data = Serialize.String2PyObj(result[0][0])
		l = []
		LA = l.append
		#name, MountEvolveID, exp...
		for roleid, d in data.iteritems():
			#roleid, name MountEvolveID, exp
			LA((roleid, d[0], d[1], d[2]))
		l.sort(key = lambda it:(it[2], it[3]), reverse = True)
		
		#只要角色ID 和名字
		return l

def GetRank_4(con):
	
	with con as cur:
		cur.execute(SQL_4)
		result = cur.fetchall()
		if not result:
			return []
		data = Serialize.String2PyObj(result[0][0])
		l = []
		LA = l.append
		#name, weddingRingID, exp...
		for roleid, d in data.iteritems():
			#roleid, name weddingRingID ,exp
			LA((roleid, d[0], d[1], d[2]))
		l.sort(key = lambda it:(it[2], it[3]), reverse = True)
		#只要角色ID 和名字
		return l


#正式接口
def SystemRank(request):
	serverid = request.BodyGet("AreaId")
	Type = request.BodyGet("Type")
	PageNo = request.BodyGet("PageNo")
	DataNum = request.BodyGet("DataNum")
	
	con = DBHelp.ConnecMianZoneMasterDBByID(serverid)
	if not con:
		return request.ErrorResponse(-1007, "area error")
	
	rank = []
	if Type == 1:
		rank = GetRank_1(con)
	elif Type == 2:
		rank = GetRank_2(con)
	elif Type == 3:
		rank = GetRank_3(con)
	elif Type == 4:
		rank = GetRank_4(con)
	else:
		return request.ErrorResponse(-1012, "type error")
		
	#总数量
	GameRankList_count = len(rank)
	if PageNo == 0:
		rank = rank[:DataNum]
	elif PageNo == 1:
		if GameRankList_count <= 30:
			rank = []
		else:
			rank = rank[30:30 + DataNum]
	elif PageNo == 2:
		if GameRankList_count <= 60:
			rank = []
		else:
			rank = rank[60 : 60 + DataNum]
	elif PageNo == 3:
		if GameRankList_count <= 90:
			rank = []
		else:
			rank = rank[90 : 90 + DataNum]
	else:
		rank = []
	#返回的这一页的数量
	TotalPageCount = len(rank)
	
	#返回列表
	res_rank = []
	for data in rank:
		res_rank.append({"RoleId" : str(data[0]), "RoleName" : data[1], "PageNo":PageNo, "TotalPageCount":TotalPageCount})
	
	return request.response({"GameRankList_count":min(TotalPageCount, 30), "GameRankList":res_rank})

