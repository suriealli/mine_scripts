#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import game
def getAll():
	data={}
	data=game.act({"model":"item","action":"getAll"})
	return data
def getAllGoods():
	data={}
	data=game.act({"model":"item","action":"getAllGoods"})
	return data