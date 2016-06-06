#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.QiShiJiNeng")
#===============================================================================
# 骑士技能
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

class QiShiJiNengOne(FuMoZhan.FuMoZhan):
	skill_id = 1
	play_time = 2.35			#播放时间（秒）

class QiShiJiNengTwo(QianJunPo.QianJunPo):
	skill_id = 2			#技能ID
	play_time = 2.53			#播放时间（秒）

class QiShiJiNengThree(NiTianShaShen.NiTianShaShen):
	skill_id = 3
	play_time = 2.90			#播放时间（秒）

class QiShiJiNengFour(ZhanLongJue.ZhanLongJue):
	skill_id = 4
	play_time = 1.64			#播放时间（秒）

class QiShiJiNengFive(HuiTianMianDi.HuiTianMianDi):
	skill_id = 5
	play_time = 3.30			#播放时间（秒）

class QiShiJiNengSix(ShenGuiMoDi.ShenGuiMoDi):
	skill_id = 6			#技能ID
	play_time = 2.94			#播放时间（秒）

class QiShiJiNengSeven(QianBianWanHua.QianBianWanHua):
	skill_id = 7			#技能ID
	play_time = 4.2			#播放时间（秒）
	
class QiShiJiNengOneA(FuMoZhanA.FuMoZhanA):
	skill_id = 18
	play_time = 2.37			#播放时间（秒）

class QiShiJiNengTwoB(QianJunPoA.QianJunPoA):
	skill_id = 19			#技能ID
	play_time = 2.45			#播放时间（秒）
	
class QiShiJiNengEight(JiSuLengQue.JiSuLengQue):
	skill_id = 22			#技能ID
	play_time = 1.33			#播放时间（秒）
	
class QiShiJiNengNine(NiTianShaShenA.NiTianShaShenA):
	skill_id = 26			#技能ID
	play_time = 2.33			#播放时间（秒）
	
class QiShiJiNengTen(ZhanLongJueA.ZhanLongJueA):
	skill_id = 27			#技能ID
	play_time = 1.63			#播放时间（秒）

if "_HasLoad" not in dir():
	QiShiJiNengOne.reg()
	QiShiJiNengTwo.reg()
	QiShiJiNengThree.reg()
	QiShiJiNengFour.reg()
	QiShiJiNengFive.reg()
	QiShiJiNengSix.reg()
	QiShiJiNengSeven.reg()
	QiShiJiNengOneA.reg()
	QiShiJiNengTwoB.reg()
	QiShiJiNengEight.reg()
	QiShiJiNengNine.reg()
	QiShiJiNengTen.reg()
