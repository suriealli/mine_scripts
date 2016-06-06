#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Task.MainTaskFight.MainTaskFight")
#===============================================================================
# 主线任务战斗
#===============================================================================
from Game.Task.MainTaskFight import TaskFightBase
from Game.Task import TaskConfig


def InitMainTaskFight():
	TT = TaskFightBase.TFight
	for step, cfg in TaskConfig.MainTaskFightRewardConfig_Dict.iteritems():
		TT(step, cfg)

if "_HasLoad" not in dir():
	InitMainTaskFight()


