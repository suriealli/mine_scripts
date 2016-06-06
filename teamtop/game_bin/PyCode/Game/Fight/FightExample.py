#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.FightExample")
#===============================================================================
# 战斗样例
# 注意，保存血量和保存士气的还没做
#===============================================================================
import cRoleMgr
from Game.Fight import Fight

HP_DICT = {}
MORAL_DICT = {}

def DoOneFight(role):
	# 1创建一场战斗(必须传入战斗类型，不同的战斗不要让策划复用战斗类型)
	fight = Fight.Fight(4)
	# 可以手动设置是否为pvp战斗，否则将是战斗配子表中战斗类型对应的pvp战斗取值
	# fight.pvp = True
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	# 2创建两个阵营
	left_camp, right_camp = fight.create_camp()
	# 将阵营绑定一个血量字典，便可以保存血量
	#left_camp.bind_hp(HP_DICT)
	#right_camp.bind_hp(HP_DICT)
	# 3在阵营中创建战斗单位
	# create_online_role_unit、create_outline_role_unit、create_monster_camp_unit
	# 这3个函数都是创建一波战斗单位，重复创建将是车轮战模式
	# create_online_role_unit和create_outline_role_unit必须要指定由谁操作主角（第2参数）
	# 如果不必操作则使用默认值0
	left_camp.create_online_role_unit(role)
	#left_camp.create_online_role_unit(role, role.GetRoleID(), None, True)
	roles = cRoleMgr.GetAllRole()
	for _role in roles:
		if _role == role:
			continue
		right_camp.create_online_role_unit(_role)
		break
	# create_monster_camp_unit是创建一波怪物
	#right_camp.create_monster_camp_unit(1)
	#right_camp.create_monster_camp_unit(1)
	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发或者角色提前跳过战斗）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#所有客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	# 注意参数用一个有意义并且不冲突的名字，具体冲突参见Game.Fight.Fight中Fight类__init__中的定义
	fight.after_fight_param = None
	fight.after_play_param = "a"
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()
	# 如果没有指定任何操作角色，则战斗是瞬间计算完毕的，可不利用after_fight_fun回调函数而是直接在下面做战斗结果处理
	# 注意一定要先判断战斗是否真正结束（战斗bug，或者设置bug都可能导致战斗不是瞬间结束的）
	return
	if fight.result == 1:
		print "left win"
	elif fight.result == -1:
		print "right win"
	else:
		print "all lost"
	
def OnLeave(fight, role):
	print "OnLeave", role.GetRoleID(), fight.result
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None

def AfterFight(fight):
	print "AfterFight", fight.after_fight_param
	# fight.round当前战斗回合
	print "fight round", fight.round
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		print "left win"
	elif fight.result == -1:
		print "right win"
	else:
		print "all lost"
	# 遍历左右阵营未掉线的玩家
	for role in fight.left_camp.roles:
		print role.GetRoleID()
	for role in fight.right_camp.roles:
		print role.GetRoleID()

def AfterPlay(fight):
	print "AfterPlay", fight.after_play_param
