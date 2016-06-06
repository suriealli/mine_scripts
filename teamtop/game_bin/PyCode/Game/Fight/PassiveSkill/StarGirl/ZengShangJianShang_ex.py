#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ZengShangJianShang_ex")
#===============================================================================
# ע��
#===============================================================================
from Game.Fight.PassiveSkill.StarGirl import ZengShangJianShang

class ZengShangJianShangJuXieZuo(ZengShangJianShang.ZengShangJianShang):
	skill_id = 3025
	level_to_damage_upgrade_rate = 0.06
	level_to_damage_reduce_rate = 0.06
	
class ZengShangJianShangShuangZiZuo(ZengShangJianShang.ZengShangJianShang):
	skill_id = 3029
	level_to_damage_upgrade_rate = 0.06
	level_to_damage_reduce_rate = 0.06

class ZengShangJianShangShiZiZuo(ZengShangJianShang.ZengShangJianShang):
	skill_id = 3033
	level_to_damage_upgrade_rate = 0.08
	level_to_damage_reduce_rate = 0.08
	
class ZengShangJianShangMoJieZuo(ZengShangJianShang.ZengShangJianShang):
	skill_id = 3043
	level_to_damage_upgrade_rate = 0.05
	level_to_damage_reduce_rate = 0.05
	
class ZengShangJianShangShuangYuZuo(ZengShangJianShang.ZengShangJianShang):
	skill_id = 3046
	level_to_damage_upgrade_rate = 0.05
	level_to_damage_reduce_rate = 0.05

if "_HasLoad" not in dir():
	ZengShangJianShangJuXieZuo.reg()
	ZengShangJianShangShuangZiZuo.reg()
	ZengShangJianShangShiZiZuo.reg()
	ZengShangJianShangMoJieZuo.reg()
	ZengShangJianShangShuangYuZuo.reg()
