#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.QQRank")
#===============================================================================
# 消费排行榜
#===============================================================================
import Environment
from Integration.Help import OtherHelp
from Integration import AutoHTML
from World import Define
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission


def NewDayRank(request):
	return OtherHelp.Apply(_NewDayRank, request, __name__)
	
	
def _NewDayRank(request):
	DayID = AutoHTML.AsInt(request.POST, "DayID")
	rank = AutoHTML.AsString(request.POST, "rank")
	process_id = AutoHTML.AsInt(request.POST, "pid")
	if Environment.IsDevelop:
		if process_id != 2:
			return
	else:
		if process_id in Define.TestWorldIDs:
			return
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		h = cur.execute("replace into qq_consume_rank (rank_dayid, data, save_datetime) values(%s, %s, now());", (DayID, rank))
	con.close()
	return h

Permission.reg_public(NewDayRank)

