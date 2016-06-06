#!/usr/bin/env python
# -*- coding:UTF-8 -*-
def getAll(msg=None):
	data={}
	if not msg:msg={}
	from Integration.Help import ConfigHelp
	data=ConfigHelp.GetPropName()
	return data
	
def getAllGoods(msg=None):
	data={}
	if not msg:msg={}
	data=game.act({"model":"item","action":"getAllGoods"})
	return data