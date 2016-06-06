#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.LvLongTuXi")
#===============================================================================
# 绿龙突袭
#===============================================================================
from Game.Fight.ActiveSkill.GroupSkill import JingLongTuXi

class LvLongTuXi(JingLongTuXi.JingLongTuXi):
	skill_id = 2007			#技能ID

if "_HasLoad" not in dir():
	LvLongTuXi.reg()
