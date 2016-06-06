#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQRank")
#===============================================================================
# 查询排行榜(消费排行榜)
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from Util import Time


#"body" :
#    {
#        "AreaId" : ,       /* 所在大区ID */
#        "BeginTime" : ,    /* 开始时间 */
#        "EndTime" : ,      /* 结束时间 */
#        "PageNo" : ,       /* 页码 */
#        "DataNum" :        /* 条数 */
#    }
#
#  "body" :
#    {
#        "ConsumeRankList_count" : ,    /* 消费排行榜信息列表的最大数量 */
#        "ConsumeRankList" :            /* 消费排行榜信息列表 */
#        [
#            {
#                "Uin" : "",     /* 用户QQ号 */
#                "RoleId" : ,    /* 角色ID */
#                "Num" :         /* 消费额度 */
#            }
#        ]
#    }

SQL = "select data from qq_consume_rank where rank_dayid between %s and %s "
#页码从0 开始
#每页最大30条


def Rank(request):
	#serverid = request.BodyGet("AreaId")
	BeginTime = request.BodyGet("BeginTime")
	EndTime = request.BodyGet("EndTime")
	PageNo = request.BodyGet("PageNo")
	DataNum = request.BodyGet("DataNum")
	

	
	#转换时间
	Begindate = int(Time.UnixTime2DateTime(BeginTime).strftime('%Y%m%d'))
	Enddate = int(Time.UnixTime2DateTime(EndTime).strftime('%Y%m%d'))
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute(SQL, (Begindate, Enddate))
		result = cur.fetchall()
		if not result:
			return request.response({}, 1)
		
		rankdict = {}
		for data in result:
			data = eval(data[0])
			for rankdata in data:
				rmb, roleid, _, account = rankdata
				olddata = rankdict.get(roleid)
				if not olddata:
					rankdict[roleid] = (rmb, account)
				else:
					rankdict[roleid] = (rmb + olddata[0], account)
		
		resrank = rankdict.items()
		resrank.sort(key = lambda it:it[1][0], reverse = True)
		
		ConsumeRankList_count = len(resrank)
		if PageNo == 0:
			resrank = resrank[:DataNum]
		elif PageNo == 1:
			if ConsumeRankList_count <= 30:
				resrank = []
			else:
				resrank = resrank[30:30 + DataNum]
		elif PageNo == 2:
			if ConsumeRankList_count <= 60:
				resrank = []
			else:
				resrank = resrank[60 : 60 + DataNum]
		elif PageNo == 3:
			if ConsumeRankList_count <= 90:
				resrank = []
			else:
				resrank = resrank[90 : 90 + DataNum]
		else:
			resrank = []
		
		#返回列表
		res_rank = []
		for data in resrank:
			res_rank.append({"RoleId" : str(data[0]), "Uin" : data[1][1], "Num":data[1][0]})
		
		
		return request.response({"ConsumeRankList_count":min(len(res_rank), 30), "ConsumeRankList":res_rank})




