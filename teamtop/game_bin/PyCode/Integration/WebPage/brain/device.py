#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#=========================================================================
# 机器设备
#=========================================================================
import game
def showLog():
	if not user.inGroup("host"):return user.ban()
	data={}
	data=game.act({"model":"machine","action":"ShowFile","msg":{"chdir":me.S['P']['G'].get('chdir')}})
	return data