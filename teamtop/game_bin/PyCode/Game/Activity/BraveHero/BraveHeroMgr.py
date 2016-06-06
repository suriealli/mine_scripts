#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.BraveHero.BraveHeroMgr")
#===============================================================================
# 勇者英雄坛逻辑模块
#===============================================================================
import Environment
import cProcess
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import PyMessage, AutoMessage
from Common.Other import EnumGameConfig, EnumFightStatistics, GlobalPrompt
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Role import Rank, Event, Status
from Game.SysData import WorldDataNotSync, WorldData
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt8, EnumInt32, EnumObj, EnumInt1
from Game.Activity.BraveHero import BraveHeroConfig
from Game.Fight import Fight
from Game.GlobalData import ZoneName
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	#跨服排行榜数据 ，前100名数据, 今天，昨天
	ControlRank = [] #单个排名内容(积分，角色ID，角色名字，服务器名字)
	ControlRank_Old = []
	
	#勇者英雄坛开启标志
	BraveHeroIsOpen = False
	#英雄徽章商店开启标志
	BraveHeroShopIsOpen = False
	#勇者英雄坛激活活动ID
	BraveHeroActID = 0
	
	BraveHeroTAllData = AutoMessage.AllotMessage("BraveHeroTAllData", "勇者英雄坛今日所有数据")
	BraveHeroYAllData = AutoMessage.AllotMessage("BraveHeroYAllData", "勇者英雄坛昨日所有数据")
	BraveHeroBossData = AutoMessage.AllotMessage("BraveHeroBossData", "勇者英雄坛boss数据")
	BraveHeroScoreData = AutoMessage.AllotMessage("BraveHeroScoreData", "勇者英雄坛个人积分奖励领取数据")
	BraveHeroShopData = AutoMessage.AllotMessage("BraveHeroShopData", "勇者英雄坛英雄徽章商店兑换数据")
	BraveHeroOpen = AutoMessage.AllotMessage("BraveHeroOpen", "勇者英雄坛活动开启")
	BraveHeroClose = AutoMessage.AllotMessage("BraveHeroClose", "勇者英雄坛活动关闭")
	BraveHeroFightWin = AutoMessage.AllotMessage("BraveHeroFightWin", "勇者英雄坛挑战boss胜利")
	
	BraveHeroBuyCnt_Log = AutoLog.AutoTransaction("BraveHeroBuyCnt_Log", "勇者英雄坛购买次数日志")
	BraveHeroShopEx_Log = AutoLog.AutoTransaction("BraveHeroShopEx_Log", "勇者英雄坛兑换日志")
	BraveHeroScore_Log = AutoLog.AutoTransaction("BraveHeroScore_Log", "勇者英雄坛个人积分兑换日志")
	BraveHeroGetScore_Log = AutoLog.AutoTransaction("BraveHeroGetScore_Log", "勇者英雄坛获得积分日志")
	BraveHeroLocalRank_Log = AutoLog.AutoTransaction("BraveHeroLocalRank_Log", "勇者英雄坛每日本地排名日志")
	BraveHeroResetType_Log = AutoLog.AutoTransaction("BraveHeroResetType_Log", "勇者英雄坛重算区域类型日志")
	
#===============================================================================
# 积分，角色ID，角色名字，服务器名字
#===============================================================================
class ScoreRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 30						#最大排行榜 30个
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_BraveHeroScore"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[0] < v2[0]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		global BraveHeroActID
		TryUpdate(BraveHeroActID)
		
#===============================================================================
def IsStart():
	#活动是否开启
	if BraveHeroIsOpen:
		return True
	else:
		return False

def IsPersistenceDataOK():
	#依赖的持久化数据时候都已经载入完毕
	if not SR.returnDB:
		#本服数据
		return False
	if not WorldData.WD.returnDB:
		#世界数据
		return False
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
		#不广播客户端世界数据
		return False
	return True

def GetServerType():
	#根据开服时间获取服务器类型
	return WorldDataNotSync.GetData(WorldDataNotSync.BraveHeroServerType)

def GetServerActiveId():
	return  WorldDataNotSync.GetData(WorldDataNotSync.BraveHeroActiveId)

def GetLogicRank():
	#获取本服前30名数据
	return SR.data.values()

def AfterFirstStart(activeID):
	#活动开始触发(从没开始到开启)
	#有服务器类型 --> 判断活动ID是否一致, 不一致重新分配服务器类型和活动ID
	#没有服务器类型 --> 分配服务器类型和活动ID
	TryUpdate(activeID)

def ReturnServerType():
	#计算服务器类型并返回
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for serverType, cfg in BraveHeroConfig.BraveHeroServerType_Dict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			return serverType
	else:
		print "GE_EXC, TryResetServerType can not find kaifuDay (%s) in BraveHeroServerType_Dict" % kaifuDay
		#找不到的话返回第三区域服务器类型
		return 3
	
def TryResetServerType(activeID, updateType):
	#尝试重新计算服务器类型
	#当前服务器类型
	nowType = WorldDataNotSync.WorldDataPrivate.get(WorldDataNotSync.BraveHeroServerType)
	#尝试重新分配后的服务器类型
	serverType = ReturnServerType()
	if not serverType:
		return
	if not nowType:
		#没有服务器类型, 分配服务器类型, 活动ID
		SetServerType(serverType, activeID)
	elif nowType and (updateType or activeID != WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.BraveHeroActiveId]):
		#有服务器类型, 需要更新服务器类型或者激活活动的ID不一致, 尝试重新计算服务器类型
		SetServerType(serverType, activeID)
		
	serverType = GetServerType()
	if serverType:
		#服务器区域有了, 广播开始
		cNetMessage.PackPyMsg(BraveHeroOpen, (activeID, serverType))
		cRoleMgr.BroadMsg()
	
	#检查服务器类型是否分配了
	return serverType
	
def SetServerType(serverType, activeID):
	#设置服务器类型和激活活动的ID
	
	with BraveHeroResetType_Log:
		oldServerType, oldActiveID = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.BraveHeroServerType], WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.BraveHeroActiveId]
		
		WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.BraveHeroServerType] = serverType
		WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.BraveHeroActiveId] = activeID
		
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveBraveHeroType, (oldServerType, oldActiveID, serverType, activeID))
	
def TryUpdate(activeID = 0, updateType = False):
	'''
	@param activeID:每次都要传入激活活动的ID, 如果ID不对的话尝试重新分配服务器类型
	@param updateType:是否需要更新服务器类型可选
	'''
	if not IsStart():
		#活动没有开启
		return
	if not activeID:
		#激活活动ID没有
		return
	if not IsPersistenceDataOK():
		#数据没有完全载回
		return
	#服务器启动后，尝试重新计算服务器区域类型
	if not TryResetServerType(activeID, updateType):
		#服务器类型没有分配
		return
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetBraveHeroRank, (cProcess.ProcessID, GetServerType(), GetLogicRank()))

def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global ControlRank
	ControlRank = msg

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global ControlRank, ControlRank_Old
	ControlRank, ControlRank_Old = msg
	
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前30名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
		return
	if not SR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType(), GetLogicRank()))

def AfterNewDay():
	isStart = IsStart()
	with BraveHeroLocalRank_Log:
		#记录今日本地排行榜
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveBraveHeroLocalRank, (isStart, SR.data))
	#新的一天,替换昨天的排名
	if not isStart:
		return
	#0点的时候使用本地缓存排行榜数据更新今日昨日排行榜数据
	global ControlRank, ControlRank_Old
	ControlRank_Old = ControlRank
	ControlRank = []
	
	#清理排名缓存
	SR.Clear()
	#重置boss
	ResetBoss()

def ResetBoss():
	#每日重置boss索引, -1
	global BraveHeroBossDict
	if not BraveHeroBossDict.returnDB:
		print 'GE_EXC, BraveHeroMgr ResetBoss BraveHeroBossDict not returnDB'
		return
	for bossData in BraveHeroBossDict.values():
		bossData[1] = {}
		if bossData[0] == 1:
			continue
		bossData[0] -= 1
	BraveHeroBossDict.changeFlag = True

def AfterSetKaiFuTime(param1, param2):
	#更改开服时间，尝试修改服务器区域类型
	#有服务器类型 --> 尝试修改服务器类型
	global BraveHeroActID
	TryUpdate(BraveHeroActID, updateType=True)

def AfterLoadWorldDataNotSync(param1, param2):
	#载入世界数据之后
	global BraveHeroActID
	TryUpdate(BraveHeroActID)

def AfterLoadWorldData(role, param):
	#载入世界数据之后
	global BraveHeroActID
	TryUpdate(BraveHeroActID)

def SyncRoleOtherData(role, param):
	if not IsStart():
		return
	role.SendObj(BraveHeroOpen, (GetServerActiveId(), GetServerType()))
	
def RequestOpenPanel(role, msg):
	'''
	请求打开面板
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	#发送今日排名所有数据, 要让客户端自己去找自己的排名
	global ControlRank
	role.SendObj(BraveHeroTAllData, ControlRank)
	
	#boss索引, boss血量
	global BraveHeroBossDict
	if not BraveHeroBossDict.returnDB:
		return
	
	roleID = role.GetRoleID()
	
	if roleID not in BraveHeroBossDict:
		#第一次
		BraveHeroBossDict[roleID] = [1, {}]
		#boss索引, 血量(0-最大血量)
		role.SendObj(BraveHeroBossData, (1, 0))
	else:
		bossData = BraveHeroBossDict[roleID]
		role.SendObj(BraveHeroBossData, (bossData[0], bossData[1].get('total_hp', 0)))
	
	#积分兑换记录
	role.SendObj(BraveHeroScoreData, role.GetObj(EnumObj.BraveHeroScore))
	
def RequestFight(role, msg):
	'''
	请求挑战boss
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	#次数判断
	if EnumGameConfig.BraveHeroCntMax + role.GetDI8(EnumDayInt8.BraveHeroBuyCnt) <= role.GetDI8(EnumDayInt8.BraveHeroCnt):
		return
	
	#时间判断(23点到0点半之间不能挑战)
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	if (23, 0) <= nowTime or nowTime <= (0, 30):
		role.Msg(2, 0, GlobalPrompt.BraveHero_TimeLimit)
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#获取boss索引
	roleID = role.GetRoleID()
	global BraveHeroBossDict
	if not BraveHeroBossDict.returnDB:
		return
	if roleID not in BraveHeroBossDict:
		return
	bossIndex, bossHpDict = BraveHeroBossDict[roleID]
	
	#boss配置
	bossCfg = BraveHeroConfig.BraveHeroBoss_Dict.get(bossIndex)
	if not bossCfg:
		print "GE_EXC, RequestFight can not find bossIndex (%s) in BraveHeroBoss_Dict" % bossIndex
		return
	
	#旧的血量
	oldHp = 0
	if not bossHpDict:
		#初始最大血量
		oldHp = bossCfg.maxHp
	else:
		#获得保存的血量
		oldHp = bossHpDict['total_hp']
	
	#增加挑战次数
	role.IncDI8(EnumDayInt8.BraveHeroCnt, 1)
	
	#进入pve挑战
	BraveHeroPve(role, EnumGameConfig.BraveHeroFightType, bossCfg.fightID, AfterFight, AfterPlay, (bossCfg, bossHpDict, oldHp))
	
def BraveHeroPve(role, fightType, mcid, AfterFight, AfterPlay, regparam):
	#战斗类型
	fight = Fight.Fight(fightType)
	fight.restore = True
	
	left_camp, right_camp = fight.create_camp()
	
	#可控
	left_camp.create_online_role_unit(role, role.GetRoleID())
	
	_, bossHpDict, _ = regparam
	
	#绑定boss血量字典
	right_camp.bind_hp(bossHpDict)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = AfterFight
	fight.after_play_fun = AfterPlay
	fight.after_fight_param = regparam
	
	fight.start()
	
def AfterFight(fightObj):
	if fightObj.result is None:
		print "GE_EXC, GloryWarMgr fight with role error"
		return
	
	#获取角色
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	bossCfg, bossHpDict, oldHp = fightObj.after_fight_param
	
	#新的血量
	newHp = bossHpDict['total_hp']
	#战斗打掉的血量
	fightHp = oldHp - newHp
	
	#没有造成伤害 ? 新的血量比旧的血量大 ?
	if fightHp <= 0:
		return
	
	roleID = role.GetRoleID()
	global BraveHeroBossDict
	bossData = BraveHeroBossDict[roleID]
	
	total_hp = bossHpDict.get('total_hp')
	if not total_hp:
		#总血量为0, 击杀boss, boss索引加1, 重新赋值一个boss血量字典
		if bossCfg.index >= 100:
			#100关循环
			bossData = [100, {}]
		else:
			bossData = [bossCfg.index + 1, {}]
	else:
		#总血量不为0
		bossData[1] = bossHpDict
	BraveHeroBossDict[roleID] = bossData
	
	#计算积分
	with BraveHeroGetScore_Log:
		fightScore = CalSocre(bossCfg, fightHp, fightObj.round)
		role.IncI32(EnumInt32.BraveHeroScore, fightScore)
	
	fightObj.set_fight_statistics(roleID, EnumFightStatistics.EnumBraveHeroScore, fightScore)
	
	#更新排行榜
	UpdateScoreRank(role)
	
	role.SendObj(BraveHeroBossData, (bossData[0], total_hp))
	
def AfterPlay(fightObj):
	if fightObj.result is None:
		print "GE_EXC, GloryWarMgr fight with role error"
		return
	
	#获取角色
	roles = fightObj.left_camp.roles
	if not roles:
		return
	
	role = list(roles)[0]
	roleID = role.GetRoleID()
	global BraveHeroBossDict
	if roleID not in BraveHeroBossDict:
		return
	
	#胜利告诉客户端播放动画
	if not BraveHeroBossDict[roleID][1].get('total_hp', 0):
		role.SendObj(BraveHeroFightWin, None)
	
def CalSocre(bossCfg, fightHp, fightRound):
	#计算积分
	if fightRound >= 5:
		fightRound = 5
	fightRound -= 1
	return min(fightHp, bossCfg.maxHp) / 4000 + bossCfg.winScore[fightRound]

def RequestFastFight(role, msg):
	'''
	请求快速挑战
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#vip等级判断
	if role.GetVIP() < EnumGameConfig.BraveHeroVIP:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	#次数判断
	if EnumGameConfig.BraveHeroCntMax + role.GetDI8(EnumDayInt8.BraveHeroBuyCnt) <= role.GetDI8(EnumDayInt8.BraveHeroCnt):
		return
	
	#时间判断(23点到0点半之间不能挑战)
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	if (23, 0) <= nowTime or nowTime <= (0, 30):
		role.Msg(2, 0, GlobalPrompt.BraveHero_TimeLimit)
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#获取boss索引
	roleID = role.GetRoleID()
	global BraveHeroBossDict
	if not BraveHeroBossDict.returnDB:
		return
	if roleID not in BraveHeroBossDict:
		return
	bossIndex, bossHpDict = BraveHeroBossDict[roleID]
	
	#boss配置
	bossCfg = BraveHeroConfig.BraveHeroBoss_Dict.get(bossIndex)
	if not bossCfg:
		print "GE_EXC, RequestFight can not find bossIndex (%s) in BraveHeroBoss_Dict" % bossIndex
		return
	
	#旧的血量
	oldHp = 0
	if not bossHpDict:
		#初始最大血量
		oldHp = bossCfg.maxHp
	else:
		#获得保存的血量
		oldHp = bossHpDict['total_hp']
	
	#增加挑战次数
	role.IncDI8(EnumDayInt8.BraveHeroCnt, 1)
	
	#进入快速pve挑战
	BraveHeroFastPve(role, EnumGameConfig.BraveHeroFightType, bossCfg.fightID, AfterFight, AfterPlay, (bossCfg, bossHpDict, oldHp))
	
def BraveHeroFastPve(role, fightType, mcid, AfterFight, AfterPlay, regparam):
	#战斗类型
	fight = Fight.Fight(fightType)
	
	left_camp, right_camp = fight.create_camp()
	
	#不可控
	left_camp.create_online_role_unit(role)
	
	_, bossHpDict, _ = regparam
	
	#绑定boss血量字典
	right_camp.bind_hp(bossHpDict)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = AfterFight
	fight.after_play_fun = AfterPlay
	fight.after_fight_param = regparam
	#跳过不播放战斗
	fight.skip_fight_play = True
	
	fight.start()
	
def RequestScoreReward(role, msg):
	'''
	请求领取个人积分奖励
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#等级判断
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	#积分索引判断
	index = msg
	if not index:
		return
	
	#兑换过了
	braveScoreSet = role.GetObj(EnumObj.BraveHeroScore)
	if index in braveScoreSet:
		return
	
	#配置
	cfg = BraveHeroConfig.BraveHeroScore_Dict.get((index, GetCloseValue(roleLevel, BraveHeroConfig.BraveHeroScoreLevel_List)))
	if not cfg:
		print "GE_EXC, RequestScoreReward can not find index : %s, level : %s" % (index, GetCloseValue(roleLevel, BraveHeroConfig.BraveHeroScoreLevel_List))
		return
	
	#积分不足
	if role.GetI32(EnumInt32.BraveHeroScore) < cfg.needScore:
		return
	
	#背包空间不足
	if role.PackageEmptySize() < len(cfg.reward):
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	braveScoreSet.add(index)
	role.SetObj(EnumObj.BraveHeroScore, braveScoreSet)
	role.SendObj(BraveHeroScoreData, braveScoreSet)
	
	#发放奖励
	with BraveHeroScore_Log:
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.reward:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		if cfg.money:
			role.IncMoney(cfg.money)
			tips += GlobalPrompt.Money_Tips % cfg.money
		
	role.Msg(2, 0, tips)
	
def GetCloseValue(value, value_list):
	'''
	返回第一个大于value的上一个值
	'''
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
	
def RequestWatchToday(role, msg):
	'''
	请求查看今日排名
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	global ControlRank
	role.SendObj(BraveHeroTAllData, ControlRank)
	
def RequestWatchYesterday(role, msg):
	'''
	请求查看昨日排名
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	global ControlRank_Old
	role.SendObj(BraveHeroYAllData, ControlRank_Old)
	
def RequestBuyCnt(role, msg):
	'''
	请求购买次数
	@param role:
	@param msg:
	'''
	#活动是否开启判断
	if not IsStart():
		return
	
	#时间判断(23点到0点半之间不能购买次数)
	nowTime = (cDateTime.Hour(), cDateTime.Minute())
	if (23, 0) <= nowTime or nowTime <= (0, 30):
		role.Msg(2, 0, GlobalPrompt.BraveHero_BuyLimit)
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	nowCnt = role.GetDI8(EnumDayInt8.BraveHeroBuyCnt)
	#超过124次不让买了
	if nowCnt >= 124:
		return
	#超过按最大值扣神石
	if nowCnt >= 39:
		nowCnt = 39
	cfg = BraveHeroConfig.BraveHeroBuy_Dict.get(nowCnt)
	if not cfg:
		print "GE_EXC, RequestBuyCnt can not find nowCnt (%s) in BraveHeroBuy_Dict" % nowCnt
		return
	
	#神石不足
	if role.GetUnbindRMB() < cfg.needRMB:
		return
	
	with BraveHeroBuyCnt_Log:
		role.DecUnbindRMB(cfg.needRMB)
		#增加购买次数
		role.IncDI8(EnumDayInt8.BraveHeroBuyCnt, 1)
	
def RequestOpenShop(role, msg):
	'''
	请求打开英雄徽章商店
	@param role:
	@param msg:
	'''
	global BraveHeroShopIsOpen
	if not BraveHeroShopIsOpen:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	role.SendObj(BraveHeroShopData, role.GetObj(EnumObj.BraveHeroShop))
	
def RequestBraveHeroEx(role, msg):
	'''
	请求英雄徽章商店兑换
	@param role:
	@param msg:
	'''
	global BraveHeroShopIsOpen
	if not BraveHeroShopIsOpen:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	coding, cnt = msg
	cfg = BraveHeroConfig.BraveHeroShop_Dict.get(coding)
	if not cfg:
		print "GE_EXC, RequestBraveHeroEx can not find coding (%s) in BraveHeroShop_Dict" % coding
		return
	
	#角色等级不足
	if role.GetLevel() < cfg.needLevel:
		return
	
	#世界等级不足
	if WorldData.GetWorldLevel() < cfg.needWorldLevel:
		return
	
	if not cnt: return
	#兑换需要物品不够
	needCnt = cfg.needItemCnt * cnt
	if role.ItemCnt(cfg.needCoding) < needCnt:
		return
	
	if cfg.limitCnt:
		if cnt > cfg.limitCnt:
			#购买个数超过限购
			return
		braveShopObj = role.GetObj(EnumObj.BraveHeroShop)
		if coding not in braveShopObj:
			braveShopObj[coding] = cnt
		elif braveShopObj[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			braveShopObj[coding] += cnt
		#限购的记录购买数量
		role.SetObj(EnumObj.BraveHeroShop, braveShopObj)
		role.SendObj(BraveHeroShopData, braveShopObj)
	
	with BraveHeroShopEx_Log:
		#发放兑换物品
		role.DelItem(cfg.needCoding, needCnt)
		role.AddItem(coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
def OpenBraveHero(callArgv, regparam):
	#开启勇者英雄坛
	global BraveHeroIsOpen
	if BraveHeroIsOpen:
		print "GE_EXC, BraveHero is already open"
		return
	
	BraveHeroIsOpen = True
	
	#记下激活的活动ID
	global BraveHeroActID
	BraveHeroActID = regparam
	
	AfterFirstStart(regparam)
	
def CloseBraveHero(callArgv, regparam):
	#关闭勇者英雄坛
	global BraveHeroIsOpen
	if not BraveHeroIsOpen:
		print "GE_EXC, BraveHero is already close"
		return
	
	BraveHeroIsOpen = False
	
	global ControlRank, ControlRank_Old, SR, BraveHeroBossDict
	#清理排行榜数据
	ControlRank, ControlRank_Old = [], []
	#清理本地排行榜数据
	SR.Clear()
	#清理boss数据
	if not BraveHeroBossDict.returnDB:
		print 'GE_EXC, BraveHeroMgr BraveHeroBossDict not returnDB'
	else:
		BraveHeroBossDict.clear()
	
	#广播结束
	cNetMessage.PackPyMsg(BraveHeroClose, None)
	cRoleMgr.BroadMsg()
	
def OpenBraveHeroShop(role, param):
	#开启英雄徽章商店
	if param != CircularDefine.CA_BraveHeroShop:
		return
	
	global BraveHeroShopIsOpen
	if BraveHeroShopIsOpen:
		print "GE_EXC, BraveHeroShop is already open"
		return
	
	BraveHeroShopIsOpen = True

def CloseBraveHeroShop(role, param):
	#关闭英雄徽章商店
	if param != CircularDefine.CA_BraveHeroShop:
		return
	
	global BraveHeroShopIsOpen
	if not BraveHeroShopIsOpen:
		print "GE_EXC, BraveHeroShop is already close"
		return
	
	BraveHeroShopIsOpen = False

def UpdateScoreRank(role):
	#尝试入榜
	if not IsStart():
		return
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	
	roleID = role.GetRoleID()
	SR.HasData(roleID, [role.GetI32(EnumInt32.BraveHeroScore), roleID, role.GetRoleName(), ZoneName.ZoneName])

def AfterLogin(role, param):
	#初始化积分兑换记录为一个集合
	if type(role.GetObj(EnumObj.BraveHeroScore)) == dict:
		role.SetObj(EnumObj.BraveHeroScore, set())
	
def RoleDayClear(role, param):
	if role.GetLevel() < EnumGameConfig.BraveHeroLevelLimit:
		return
	if role.GetObj(EnumObj.BraveHeroScore):
		#每日清理积分兑换记录
		role.SetObj(EnumObj.BraveHeroScore, set())
		if IsStart():
			#活动是开启的话, 同步积分兑换记录
			role.SendObj(BraveHeroScoreData, set())
	if role.GetI32(EnumInt32.BraveHeroScore):
		#清理积分
		role.SetI32(EnumInt32.BraveHeroScore, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if (Environment.HasLogic and not Environment.IsCross and not Environment.IsRUGN) or Environment.HasWeb:
		SR = ScoreRank()
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicBraveHeroRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataBraveHeroRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataBraveHeroRankToLogic_T, OnControlUpdataRank_T)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		Init.InitCallBack.RegCallbackFunction(TryUpdate)
		
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, AfterLoadWorldDataNotSync)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		#{role_id:(bossIndex, bossHpDict)}
		BraveHeroBossDict = Contain.Dict("BraveHeroBossDict", (2038, 1, 1))
	
		Event.RegEvent(Event.Eve_StartCircularActive, OpenBraveHeroShop)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseBraveHeroShop)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_OpenPanel", "请求打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_Fight", "请求挑战boss"), RequestFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_FastFight", "请求快速挑战"), RequestFastFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_ScoreReward", "请求领取个人积分奖励"), RequestScoreReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_WatchToday", "请求查看今日排名"), RequestWatchToday)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_WatchYesterday", "请求查看昨日排名"), RequestWatchYesterday)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_BuyCnt", "请求购买次数"), RequestBuyCnt)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_Exchange", "请求英雄徽章商店兑换"), RequestBraveHeroEx)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BraveHero_OpenShop", "请求请求打开英雄徽章商店"), RequestOpenShop)
		
	
		