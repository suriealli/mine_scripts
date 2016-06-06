#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.RoleInit")
#===============================================================================
# 角色初始化模块
#===============================================================================
import cDateTime
from ComplexServer.Log import AutoLog
from Game.Role import Version, Event
from Game.Role.Config import RoleBaseConfig
from Game.Role.Data import EnumInt1, EnumInt32, EnumObj, EnumDisperseInt32, EnumInt8, EnumTempObj
from Game.SysData import WorldData


if "_HasLoad" not in dir():
	TraInit = AutoLog.AutoTransaction("TraInit", "角色初始化")

def InitRole(role):
	#新角色数据初始化
	if role.GetI1(EnumInt1.En_IsInitOk):
		#每一个角色有且仅有初始化一次
		return
	with TraInit:
		#初始化第一次登陆时间
		role.SetDI32(EnumDisperseInt32.FirstLoginTimes, cDateTime.Seconds())
		#初始化合服数据
		role.SetDI32(EnumDisperseInt32.HerFuRecord, WorldData.GetHeFuCnt())
		#====================================================================
		#初始化等级
		role.SetDI32(EnumDisperseInt32.enLevel, 1)
		
		role.SetObj(EnumObj.En_PackageItems, set())
		role.SetObj(EnumObj.En_RoleEquipments, set())
		#初始化体力
		role.SetTiLi(RoleBaseConfig.MaxAutoTiLi)
		#体力回复时间
		role.SetI32(EnumInt32.TiLiMinute, cDateTime.Minutes())
		#VIP
		role.SetObj(EnumObj.VIPData, {1:{}})
		#记录角色第一次登录来源
		role.SetObj(EnumObj.Create_PF, role.GetTempObj(EnumTempObj.LoginInfo).get("pf"))
		#黄钻/蓝钻等级礼包设置
		role.SetI8(EnumInt8.QQVIPLevelIndex, 1)
		role.SetI8(EnumInt8.QQLZLevelIndex, 1)
		#初始化竞技场挑战次数
		role.SetI8(EnumInt8.JJC_Challenge_Cnt, 15)
		#初始化竞技场兑换字典
		role.SetObj(EnumObj.JJC, {1:{}})
		#初始化公会{1:成就宝箱领取状态列表}
		role.SetObj(EnumObj.Union, {1:[]})
		#初始化玩家坐骑
		role.SetObj(EnumObj.Mount, {1:[],2:[]})
		#初始化玩家阵位
		role.SetStationID(3)
		#初始化技能
		role.SetObj(EnumObj.RoleFightSkill, {1 : []})
		#初始化主角品阶
		role.SetGrade(1)
		
		role.SetObj(EnumObj.FB_ZJReward, {1 : set(), 2: set()})
		#初始化恶魔深渊数据
		role.SetObj(EnumObj.EvilHole_StarBoxReward, {1 : set()})
		#初始化玩法奖励{1->玩法奖励字典{enum:[]}}
		role.SetObj(EnumObj.Award, {1: {}})
		#炼金
		role.SetObj(EnumObj.Gold_Player_Data, {1: 0, 2: {}})
		#巨龙宝藏
		role.SetObj(EnumObj.Dragon_Treasure, {1: [], 2: [], 3: [], 4:[]})
		#支线任务
		role.SetObj(EnumObj.SubTaskDict, {1 : set(), 2: set(), 3 : set()})
		#送花记录
		role.SetObj(EnumObj.FlowerRecord, {1 : set()})
		#登录奖励
		role.SetObj(EnumObj.LEGION_REWARD, {1:set(), 2:set(), 3:0})
		#每日必做
		role.SetObj(EnumObj.DailyDoDict, {1:{}, 2:set()})
		#神器
		role.SetObj(EnumObj.En_RoleArtifact, set())
		#圣器
		role.SetObj(EnumObj.En_RoleHallows, set())
		#翅膀
		role.SetObj(EnumObj.Wing, {1:{}, 2:{}})
		#占卜
		role.SetI8(EnumInt8.TarotIndex, 1)
		role.SetObj(EnumObj.TarotCardDict, {1 : {}, 2 : {}})
		role.SetObj(EnumObj.Wonder_Reward_List, {1:set(), 2:set()})
		role.SetObj(EnumObj.Wonder_Vip_Reward_Dict, {1:{}})
		#好友邀请和分享
		role.SetObj(EnumObj.InviteFriendObj, {1:[], 2:set(), 3:set(), 4:set()})
		#初始化天降神石档次
		role.SetI8(EnumInt8.HeavenUnRMBIndex, 1)
		#专题活动
		role.SetObj(EnumObj.ProjectGetedObj, {1:set(), 2:set()})
		role.SetObj(EnumObj.ProjectObj, {1:{}, 2:{}})
		#时装
		role.SetObj(EnumObj.En_RoleFashions, set())
		#国庆活动
		role.SetObj(EnumObj.NationData, {1:set(), 2:set()})
		#初始化角色今日在线时间
		role.SetI32(EnumInt32.OnLineTimeToday, 1)
		#称号
		role.SetObj(EnumObj.Title, {1 : {}, 2 : []})
		#蓝钻转转乐
		role.SetObj(EnumObj.QQLZHDData, set())
		#魔灵
		role.SetObj(EnumObj.En_RoleMagicSpirits, set())
		#虚空幻境
		role.SetObj(EnumObj.CTTRoleData, {1:{}, 2:0})
		#圣印系统
		role.SetObj(EnumObj.SealData, {})
		#====================================================================
		#注意，以下2个是最后才执行，如果要插入，请插入上面一行
		#====================================================================
		#设置角色版本
		role.SetDI32(EnumDisperseInt32.Version, len(Version.VersionList))
		#最后最后 标记初始化OK
		role.SetI1(EnumInt1.En_IsInitOk, True)
		Event.TriggerEvent(Event.Eve_FirstInitRole, role)
		#====================================================================
		#不要插入到这下面去啊啊啊
		#====================================================================

