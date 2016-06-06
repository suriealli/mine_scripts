#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.IDIPVisit")
#===============================================================================
# idip
#===============================================================================
import Environment
from ComplexServer.Plug.DB import DBWork


class IDIP_Event(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("replace into qq_idip_event (event_allot_id, role_id, account, event_id, event_num, event_time) values(%s, %s, %s, %s, %s, NOW())", self.arg)


if Environment.HasDB and "_HasLoad" not in dir():
	IDIP_Event.reg()