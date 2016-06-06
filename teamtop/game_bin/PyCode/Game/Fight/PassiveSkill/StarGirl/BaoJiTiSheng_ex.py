#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.BaoJiTiSheng_ex")
#===============================================================================
# 注释
#===============================================================================
from Game.Fight.PassiveSkill.StarGirl import BaoJiTiSheng

class BaoJiTiShengJuXieZuo(BaoJiTiSheng.BaoJiTiSheng):
	skill_id = 3024
	level_to_crit_hurt = 0.12
	
class BaoJiTiShengShuangZiZuo(BaoJiTiSheng.BaoJiTiSheng):
	skill_id = 3028
	level_to_crit_hurt = 0.12
	
class BaoJiTiShengShiZiZuo(BaoJiTiSheng.BaoJiTiSheng):
	skill_id = 3032
	level_to_crit_hurt = 0.15
	

if "_HasLoad" not in dir():
	BaoJiTiShengJuXieZuo.reg()
	BaoJiTiShengShuangZiZuo.reg()
	BaoJiTiShengShiZiZuo.reg()
