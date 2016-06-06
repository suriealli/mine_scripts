#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ShangHaiJiaQiang1_ex")
#===============================================================================
# 伤害提升一定百分比
#===============================================================================
from Game.Fight.PassiveSkill.StarGirl import ShangHaiJiaQiang1

class ShangHaiJiaQiangShuangZiZuo(ShangHaiJiaQiang1.ShangHaiJiaQiang1):
	skill_id = 3035
	level_to_damage_upgrade_rate = 0.12
	

if "_HasLoad" not in dir():
	ShangHaiJiaQiangShuangZiZuo.reg()
