#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Base.LevelEXP")
#===============================================================================
# 等级经验处理
#===============================================================================
import Environment
import cProcess
from World import Define
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumKick
from ComplexServer.Log import AutoLog
from Game.Hero import HeroConfig
from Game.Role import Event
from Game.Role.Config import RoleConfig, RoleBaseConfig
from Game.Role.Data import EnumInt32
from Game.SysData import WorldData
from Game.Task import EnumTaskType

if "_HasLoad" not in dir():
	Hero_Level = AutoMessage.AllotMessage("Hero_Level", "同步英雄等级")
	Hero_Exp = AutoMessage.AllotMessage("Hero_Exp", "更新英雄经验")

	LEVEL_LIMIT_FOR_NA = 179		#北美版限制等级
	LEVEL_LIMIT_FOR_RU = 159		#俄罗斯版限制等级
	LEVEL_LIMIT_FOR_FR = 119		#法语版本等级限制
	LEVEL_LIMIT_FOR_EN = 119		#英文版本等级限制
	LEVEO_LIMIT_FOR_YY = 99			#YY版本等级限制

def GetExpCoef(role):
	#实际经验=原经验值*（1+世界经验加成系数+城主BUFF系数），
	p = role.GetEarningExpBuff()
	roleLevel = role.GetLevel()
	if roleLevel < 40:
		return p
	else:
		#世界经验加成系数=MIN(50%,5%*MAX（0，世界等级-玩家等级）)，
		return p + min(50, 5 * max(0, WorldData.GetWorldBuffLevel() - roleLevel))
	

def IncExp(role, exp):
	#给主角加经验
	#防止小数
	exp = int(exp)
	IncRoleExp(role, exp)
	
def IncRoleExp(role, exp):
	#角色加经验接口
	RL_GET = RoleConfig.LevelExp_Dict.get
	#获取经验累积值
	nowExp = role.GetExp() + exp
	#根据等级获取经验配置
	level = role.GetLevel()
	
	#版本判断
	if Environment.EnvIsNA():
		#北美版
		#等级限制
		if level >= LEVEL_LIMIT_FOR_NA:
			role.Msg(2, 2, GlobalPrompt.ROLE_EXP_LIMIT_PROMPT)
			return
	elif Environment.EnvIsRU():
		#俄罗斯版
		#等级限制
		if level >= LEVEL_LIMIT_FOR_RU:
			role.Msg(2, 2, GlobalPrompt.ROLE_EXP_LIMIT_PROMPT)
			return
	elif Environment.EnvIsFR():
		#法语版
		if level >= LEVEL_LIMIT_FOR_FR:
			role.Msg(2, 2, GlobalPrompt.ROLE_EXP_LIMIT_PROMPT)
			return
	elif Environment.EnvIsEN():
		#英文版本
		if level >= LEVEL_LIMIT_FOR_EN:
			role.Msg(2, 2, GlobalPrompt.ROLE_EXP_LIMIT_PROMPT)
			return
	elif Environment.EnvIsYY():
		#YY等国内联运
		if level >= LEVEO_LIMIT_FOR_YY:
			role.Msg(2, 2, GlobalPrompt.ROLE_EXP_LIMIT_PROMPT)
			return
	maxExp = RL_GET(level)
	if maxExp:
		#判断经验是否符合
		while nowExp >= maxExp:
			if not LevelUp(role):
				#国服满级后经验可以继续加,每天增加1亿经验需要约2亿年可使经验值溢出，故不考虑经验加爆的情况
				if not(Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT()):
					nowExp = maxExp
				break
			
			level += 1
			nowExp -= maxExp
			maxExp = RL_GET(level)
			if not maxExp:
				break
		#设置当前经验
		role.SetExp(nowExp)

def IncHeroExp(role, hero, totalExp, heroId):
	#英雄当前等级
	level = hero.GetLevel()
	#新英雄等级
	newLevel = level
	#英雄当前最大等级
	maxLevel = hero.cfg.maxLevel
	#英雄星级
	star = hero.cfg.star
	#英雄当前经验
	nowExp = hero.GetExp() + totalExp
	RL_GET = HeroConfig.HeroLevelExp_Dict.get
	#当前英雄星级最大经验
	cfg = RL_GET(level)
	if not cfg:
		return
	maxExp = cfg.get(star)
	if maxExp:
		while nowExp > maxExp and newLevel < maxLevel:
			#是否有下级经验配置
			cfg = RL_GET(newLevel + 1)
			if not cfg:
				break
			if not cfg.get(star):
				break
			nowExp -= maxExp
			newLevel += 1
			maxExp = cfg.get(star)
	if nowExp > maxExp:
		nowExp = maxExp
	if newLevel > level:
		hero.SetLevel(newLevel)
		#重算基础属性
		hero.propertyGather.ReSetRecountBaseFlag()
		role.SendObj(Hero_Level, (hero.oid, newLevel))
		#如果该英雄在助阵位上, 重算助阵属性
		if hero.GetHelpStationID():
			role.ResetGlobalHelpStationProperty()
	
	#记录英雄升级日志事件 -- 英雄ID, 旧等级, 新等级, 旧经验, 新经验
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveUseExpItemHero, (heroId, level, newLevel, hero.GetExp(), nowExp))
	
	hero.SetExp(nowExp)
	role.SendObj(Hero_Exp, (hero.oid, nowExp))
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_LevelUpHero, None))
	
def LevelUp(role):
	if role.GetLevel() >= RoleBaseConfig.ROLE_MAX_LEVEL:
		return False
	role.IncLevel(1)
	#重算属性
	role.GetPropertyGather().ReSetRecountBaseFlag()
	#必须在设置重算属性之后才能触发事件
	Event.TriggerEvent(Event.Eve_AfterLevelUp, role)
	
	skillPoint = RoleConfig.LevelSkillPoint_Dict.get(role.GetLevel())
	if skillPoint:
		role.IncI32(EnumInt32.SkillPoint, skillPoint)
	return True

def ToLevel(role, level):
	'''直接升至多少级'''
	if not Environment.IsDevelop and cProcess.ProcessID not in Define.TestWorldIDs:
		#不是开发环境, 同时也不是测试服
		print 'GE_EXC, use ToLevel not in IsDevelop and TestWorldIDs'
		return
	if level > RoleBaseConfig.ROLE_MAX_LEVEL:
		print 'GE_EXC, ToLevel level (%s) > RoleBaseConfig.ROLE_MAX_LEVEL' % level
		return
	nowLevel = role.GetLevel()
	if nowLevel >= level:
		#往下调, 踢掉角色
		role.Kick(True, EnumKick.OtherError)
		print 'GE_EXC, ToLevel level (%s) less nowLevel (%s)' % (level, nowLevel)
		return
	exp = RoleConfig.LevelExp_Dict.get(level)
	if not exp:
		print 'GE_EXC, ToLevel can not find level (%s) in LevelExp_Dict' % level
		return
	#升级
	while nowLevel < level:
		nowLevel += 1
		LevelUp(role)
	#设置经验
	role.SetExp(exp)

