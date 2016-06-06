#!/usr/bin/env python
# -*- coding:UTF-8 -*-

def getAll(msg=None):
	data = {}
	from Integration.Help import WorldHelp
	import collections
	for zid,zone in WorldHelp.GetZone().iteritems():
		data[zid] = {}
		data[zid]['value'] = zone.get_name()
		data[zid]['key'] = zid
		try:
			index = data[zid]['value'].index('模拟')
			del data[zid]
		except:
			pass
	data = collections.OrderedDict(sorted(data.items(),key = lambda t:t[0]))
	return data

def getZoneInfo(msg=None):
	data = {}
	from Integration.Help import WorldHelp
	for zid, zone in WorldHelp.GetZone().iteritems():
		zonename = zone.name
		if "模拟" not in zonename:
			data[zid] = {}
			data[zid]['name'] = zonename
	return data
