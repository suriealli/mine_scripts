#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.FaShiJiNeng")
#===============================================================================
# 法师技能
#===============================================================================
from Game.Fight.ActiveSkill.RoleSkill import FuMoZhan
from Game.Fight.ActiveSkill.RoleSkill import NiTianShaShen
from Game.Fight.ActiveSkill.RoleSkill import HuiTianMianDi
from Game.Fight.ActiveSkill.RoleSkill import ZhanLongJue
from Game.Fight.ActiveSkill.RoleSkill import QianJunPo
from Game.Fight.ActiveSkill.RoleSkill import ShenGuiMoDi
from Game.Fight.ActiveSkill.RoleSkill import QianBianWanHua
from Game.Fight.ActiveSkill.RoleSkill import FuMoZhanA
from Game.Fight.ActiveSkill.RoleSkill import QianJunPoA
from Game.Fight.ActiveSkill.RoleSkill import JiSuLengQue
from Game.Fight.ActiveSkill.RoleSkill import NiTianShaShenA
from Game.Fight.ActiveSkill.RoleSkill import ZhanLongJueA

class FaShiJiNengOne(FuMoZhan.FuMoZhan):
	skill_id = 11			#技能ID
	play_time = 2.45			#播放时间（秒）

class FaShiJiNengTwo(QianJunPo.QianJunPo):
	skill_id = 12			#技能ID
	play_time = 2.50			#播放时间（秒）

class FaShiJiNengThree(NiTianShaShen.NiTianShaShen):
	skill_id = 13			#技能ID
	play_time = 2.30			#播放时间（秒）

class FaShiJiNengFour(ZhanLongJue.ZhanLongJue):
	skill_id = 14
	play_time = 1.60			#播放时间（秒）

class FaShiJiNengFive(HuiTianMianDi.HuiTianMianDi):
	skill_id = 15			#技能ID
	play_time = 3.33			#播放时间（秒）

class FaShiJiNengSix(ShenGuiMoDi.ShenGuiMoDi):
	skill_id = 16			#技能ID
	play_time = 2.62			#播放时间（秒）

class FaShiJiNengSeven(QianBianWanHua.QianBianWanHua):
	skill_id = 17			#技能ID
	play_time = 3.7			#播放时间（秒）
	
class FaShiJiNengOneA(FuMoZhanA.FuMoZhanA):
	skill_id = 20			#技能ID
	play_time = 2.50			#播放时间（秒）

class FaShiJiNengTwoB(QianJunPoA.QianJunPoA):
	skill_id = 21			#技能ID
	play_time = 2.47			#播放时间（秒）
	
class FaShiJiNengEight(JiSuLengQue.JiSuLengQue):
	skill_id = 23			#技能ID
	play_time = 1.33			#播放时间（秒）
	
class FaShiJiNengNine(NiTianShaShenA.NiTianShaShenA):
	skill_id = 24			#技能ID
	play_time = 2.33			#播放时间（秒）
	
class FaShiJiNengTen(ZhanLongJueA.ZhanLongJueA):
	skill_id = 25			#技能ID
	play_time = 1.63			#播放时间（秒）

if "_HasLoad" not in dir():
	FaShiJiNengOne.reg()
	FaShiJiNengTwo.reg()
	FaShiJiNengThree.reg()
	FaShiJiNengFour.reg()
	FaShiJiNengFive.reg()
	FaShiJiNengSix.reg()
	FaShiJiNengSeven.reg()
	FaShiJiNengOneA.reg()
	FaShiJiNengTwoB.reg()
	FaShiJiNengEight.reg()
	FaShiJiNengNine.reg()
	FaShiJiNengTen.reg()
