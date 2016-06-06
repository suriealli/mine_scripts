#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Statistics")
#===============================================================================
# 统计模块
#===============================================================================
import cProcess
import cComplexServer
import Environment

if "_HasLoad" not in dir():
	StatisticsDict = {}

class Statistics(object):
	def __init__(self, key, activity = True):
		assert key not in StatisticsDict
		self.key = key
		self.activity = activity
		self.sta = {}
		if not self.activity: return
		StatisticsDict[self.key] = self
		if Environment.HasLogic:
			cComplexServer.RegSaveCallFunction3(self.Save)
	
	def Inc(self, role_id, count = 1):
		if not self.activity: return
		old = self.sta.get(role_id, 0)
		self.sta[role_id] = old + 1
	
	def Show(self):
		print "Statistics(%s)" % self.key
		for role_id, count in self.sta.iteritems():
			print "-->", role_id, count
	
	def Clear(self):
		self.sta.clear()
	
	def Save(self):
		if not self.sta:
			return
		count = 0
		min_count = 99999999
		max_count = 0
		for cnt in self.sta.itervalues():
			if cnt < min_count:
				min_count = cnt
			if cnt > max_count:
				max_count = cnt
			count += cnt
		from ComplexServer.Plug.DB import DBProxy
		DBProxy.DBVisit(cProcess.ProcessID, None, "Statistics", (self.key, len(self.sta), count, min_count, max_count))
		self.sta.clear()

def SaveStatistics(key, data):
	from ComplexServer.Plug.DB import DBProxy
	DBProxy.DBVisit(cProcess.ProcessID, None, "Statistics", (key, repr(data)))

