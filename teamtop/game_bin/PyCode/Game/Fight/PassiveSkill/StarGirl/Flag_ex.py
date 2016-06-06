#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.Flag_ex")
#===============================================================================
# 标记被动技能拓展
#===============================================================================
from Game.Fight.PassiveSkill.StarGirl import Flag

class ZengJiaXiShou(Flag.Flag):
	skill_id = 3004

class JiangDiFangYu(Flag.Flag):
	skill_id = 3014

class JiLvNuQi(Flag.Flag):
	skill_id = 3013

class XunaYun(Flag.Flag):
	skill_id = 3012
	
class EWaiXiShou(Flag.Flag):
	skill_id = 3001
	
class FanTanShangHai(Flag.Flag):
	skill_id = 3005
	
class EWaiHuiFu(Flag.Flag):
	skill_id = 3019
	
class QuChuFuMian(Flag.Flag):
	skill_id = 3020
	
class EWaiJiaXue(Flag.Flag):
	skill_id = 3021
	
class JiangDiFangYuJuXieZuo(Flag.Flag):
	skill_id = 3023
	
class jiangdifangyuShuangZiZuo(Flag.Flag):
	skill_id = 3027
	
class jiangdifangyuShiZiZuo(Flag.Flag):
	skill_id = 3031
	
class EWaiJiaXueMoJieZuo(Flag.Flag):
	skill_id = 3038
	
class ChiXuHuiXueMoJieZuo(Flag.Flag):
	skill_id = 3037
	level_to_rate = [0, 0.1, 0.15, 0.2, 0.25]
	
	def get_flag(self):
		return self.level_to_rate[self.argv]

class ZengJiaMuBiaoMoJieZuo(Flag.Flag):
	skill_id = 3044

if "_HasLoad" not in dir():
	ZengJiaXiShou.reg()
	JiangDiFangYu.reg()
	JiLvNuQi.reg()
	XunaYun.reg()
	EWaiXiShou.reg()
	FanTanShangHai.reg()
	EWaiHuiFu.reg()
	QuChuFuMian.reg()
	EWaiJiaXue.reg()
	JiangDiFangYuJuXieZuo.reg()
	jiangdifangyuShuangZiZuo.reg()
	jiangdifangyuShiZiZuo.reg()
	EWaiJiaXueMoJieZuo.reg()
	ChiXuHuiXueMoJieZuo.reg()
	ZengJiaMuBiaoMoJieZuo.reg()
