#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.ZengJiaShenMing_ex")
#===============================================================================
# 注释
#===============================================================================
from Game.Fight.PassiveSkill.StarGirl import ZengJiaShenMing

class ZengJiaShenMing1(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3008
	level_to_max_hp = [0,
					1500, 3000, 4500, 6000, 7500,
					9000, 10500, 12000, 13500, 15000,
					16500, 18000, 19500, 21000, 22500,
					24000, 25500, 27000, 28500, 30000]
	level_to_rate = 0.1
	
class ZengJiaShenMing2(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3017
	level_to_max_hp = [0,
					2000, 4000, 6000, 8000, 10000,
					12000, 14000, 16000, 18000, 20000,
					22000, 24000, 26000, 28000, 30000,
					32000, 34000, 36000, 38000, 40000]
	level_to_rate = 0.12
	
class ZengJiaShenMingJuXieZuo(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3022
	level_to_max_hp = [0,
					2000, 3500, 5000, 6500, 8000,
					9500, 11000, 12500, 14000, 15500,
					17000, 18500, 20000, 21500, 23000,
					24500, 26000, 27500, 29000, 30500]
	level_to_rate = 0.12
	
class ZengJiaShenMingShuangZiZuo(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3026
	level_to_max_hp = [0,
					3000, 5000, 7000, 9000, 11000,
					13000, 15000, 17000, 19000, 21000,
					23000, 25000, 27000, 29000, 31000,
					33000, 35000, 37000, 39000, 41000]
	level_to_rate = 0.12
	
class ZengJiaShenMingShiZiZuo(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3030
	level_to_max_hp = [0,
					5000, 7500, 10000, 12500, 15000,
					17500, 20000, 22500, 25000, 27500,
					30000, 32500, 35000, 37500, 40000,
					42500, 45000, 47500, 50000, 52500]
	level_to_rate = 0.15
	
class ZengJiaShenMingMoJieZuo(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3036
	level_to_max_hp = [0,
					5000, 7500, 10000, 12500, 15000,
					17500, 20000, 22500, 25000, 27500,
					30000, 32500, 35000, 37500, 40000,
					42500, 45000, 47500, 50000, 52500]
	level_to_rate = 0.15
	
class ZengJiaShenMingShuangYuZuo(ZengJiaShenMing.ZengJiaShenMing):
	skill_id = 3045
	level_to_max_hp = [0,
					8000, 10700, 13400, 16100, 18800,
					21500, 24200, 26900, 29600, 32300,
					35000, 37700, 40400, 43100, 45800,
					48500, 51200, 53900, 56600, 59300]
	level_to_rate = 0.15
	
	
if "_HasLoad" not in dir():
	ZengJiaShenMing1.reg()
	ZengJiaShenMing2.reg()
	ZengJiaShenMingJuXieZuo.reg()
	ZengJiaShenMingShuangZiZuo.reg()
	ZengJiaShenMingShiZiZuo.reg()
	ZengJiaShenMingMoJieZuo.reg()
	ZengJiaShenMingShuangYuZuo.reg()
