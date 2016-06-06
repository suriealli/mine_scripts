#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.HongLongTuXi")
#===============================================================================
#红龙突袭：普通攻击技能
#===============================================================================
from Game.Fight.ActiveSkill.GroupSkill import JingLongTuXi

class HongLongTuXi(JingLongTuXi.JingLongTuXi):
	skill_id = 2004			#技能ID

if "_HasLoad" not in dir():
	HongLongTuXi.reg()
