#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ChaosDomainSkill.ChangelessBeHurt")
#===============================================================================
# 混沌神域技能，受到固定值伤害
#===============================================================================
from Game.Fight import SkillBase

class ChangelessBeHurt(SkillBase.PassiveSkill):
	skill_id = 853
	be_hurt_basic = 666666		#受到固定伤害值
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_hurt.add(self.auto_u_before_hurt)
	
	def unload_event(self):
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_hurt(self,unit,original_jap,now_jap):
		if now_jap <= 0:
			return 0
		if original_jap > 999999999:
			return now_jap
		else:
			return self.be_hurt_basic
		

if "_HasLoad" not in dir():
	ChangelessBeHurt.reg()
