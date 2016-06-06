#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoblinTreasure.GoblinTreasure")
#===============================================================================
# 地精宝库
#===============================================================================
import Environment
import cRoleMgr
import cSceneMgr
import cComplexServer
import cNetMessage
import cDateTime
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumRoleStatus
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.GoblinTreasure import GTConfig
from Game.Fight import Fight
from Game.NPC import NPCServerFun, EnumNPCData
from Game.Role import Event, Status, Call
from Game.Role.Data import EnumObj, EnumInt1, EnumCD, EnumDayInt8
from Game.Role.Mail import Mail
from Game.RoleFightData import RoleFightData
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	#消息
	GoblinTreasureData = AutoMessage.AllotMessage("GoblinTreasureData", "地精宝库兑换数据")
	GTRobBeginOrEnd = AutoMessage.AllotMessage("GTRobBeginOrEnd", "劫宝开始")
	GTRobMsg = AutoMessage.AllotMessage("GTRobMsg", "劫宝信息")
	
	#日志
	GTExchange_Log = AutoLog.AutoTransaction("GTExchange_Log", "地精宝库兑换物品")
	GTRob_Log = AutoLog.AutoTransaction("GTRob_Log", "地精宝库劫宝奖励")
	
	#劫宝是否开始
	GTRob = False
	
	#活动结束后删除npc用 -- [(sceneId, npcId),...]
	GT_SN_List = []
	
	#宝物是否被劫走字典 -- {pos-->[roleName, 是否被劫走]}	上线同步
	GT_RobMsg_DICT = {}
	
	#劫宝npc男女类型
	GT_RobNpc_Dict = {(1, 1) : 1073, (2, 1) : 1074, (1, 2) : 1075, (2, 2) : 1076}
	
	#世界等级 -- 活动开始初始化, 活动结束置0
	GT_WorldLevel = 0
#===============================================================================
# 战斗相关
#===============================================================================
def InitGTNpcClickFun():
	'''
	注册点击函数
	'''
	#小妖点击函数
	for npcType in GTConfig.GTNpcTypeSet:
		if npcType > 0:
			NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickGoblin)
	
	#劫宝者点击函数
	global GT_RobNpc_Dict
	for npcType in GT_RobNpc_Dict.values():
		if npcType > 0:
			NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickRob)
	
def ClickGoblin(role, npc):
	'''
	小妖点击函数
	'''
	global GTRob
	if not GTRob: return
	
	#等级不足
	level = role.GetLevel()
	if level < EnumGameConfig.GT_Level:
		role.Msg(2, 0, GlobalPrompt.GT_Open_Tips)
		return
	
	#北美版
	if Environment.EnvIsNA():
		if role.GetDI8(EnumDayInt8.GoblinRewardCnt) >= EnumGameConfig.GT_NA_REWARD_CNT_MAX:
			#提示
			role.Msg(2, 0, GlobalPrompt.GT_NA_No_Reward_Cnt)
			return
	
	#战斗CD中
	if role.GetCD(EnumCD.GT_Rob_CD):
		role.Msg(2, 0, GlobalPrompt.GT_Fight_CD % role.GetCD(EnumCD.GT_Rob_CD))
		return
	
	#是否能进入战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#点击等级限制
	npcDict = npc.GetPyDict()
	if level < npcDict[5]:
		role.Msg(2, 0, GlobalPrompt.GT_LimitLevel)
		return
	
	#进战斗前先设置战斗CD
	role.SetCD(EnumCD.GT_Rob_CD, EnumGameConfig.GT_CD)
	
	#和小妖战斗
	PVE_Goblin(role, npcDict[4], EnumGameConfig.GT_PVE_TYPE, npc)
	
def ClickRob(role, npc):
	'''
	劫宝者npc点击函数
	'''
	global GTRob
	if not GTRob: return
	
	#等级
	level = role.GetLevel()
	if level < EnumGameConfig.GT_Level:
		role.Msg(2, 0, GlobalPrompt.GT_Open_Tips)
		return
	
	#北美版
	if Environment.EnvIsNA():
		if role.GetDI8(EnumDayInt8.GoblinRewardCnt) >= EnumGameConfig.GT_NA_REWARD_CNT_MAX:
			#提示
			role.Msg(2, 0, GlobalPrompt.GT_NA_No_Reward_Cnt)
			return
	
	#战斗CD中
	if role.GetCD(EnumCD.GT_Rob_CD):
		role.Msg(2, 0, GlobalPrompt.GT_Fight_CD % role.GetCD(EnumCD.GT_Rob_CD))
		return
	
	#是否能进入战斗
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#点击等级限制
	npcDict = npc.GetPyDict()
	if level < npcDict[8]:
		role.Msg(2, 0, GlobalPrompt.GT_LimitLevel)
		return
	
	#设置战斗CD
	role.SetCD(EnumCD.GT_Rob_CD, EnumGameConfig.GT_CD)
	
	PVP_Goblin_D(role, RoleFightData.GetRoleFightData(npcDict[5]), EnumGameConfig.GT_PVP_TYPE, npc)
#===============================================================================
# 打包
#===============================================================================
def PackNpcDict(npc, sceneId, pos, direct, tickId, roleId, npcName, roleName, limitLevel):
	npc.SetPyDict(1, sceneId)		#场景ID
	npc.SetPyDict(2, pos)			#位置 --> 刷怪的点
	npc.SetPyDict(3, direct)		#朝向
	npc.SetPyDict(4, tickId)		#注册的服务器tickID
	npc.SetPyDict(5, roleId)		#玩家ID
	npc.SetPyDict(6, npcName)		#npc名字
	npc.SetPyDict(7, roleName)		#玩家名字
	npc.SetPyDict(8, limitLevel)	#点击等级限制
	
def PackMsg(pos, npcName, roleName, isRob, reward = None):
	global GTRob
	
	#如果活动没有结束, 打包数据广播给所有玩家 -- {位置 --> [玩家, 劫宝信息(占领(0), 劫走(1))}
	if GTRob:
		global GT_RobMsg_DICT
		GT_RobMsg_DICT[pos] = [roleName, isRob]
		cNetMessage.PackPyMsg(GTRobMsg, GT_RobMsg_DICT)
		cRoleMgr.BroadMsg()
	
	#传闻
	if isRob:
		cRoleMgr.Msg(1, 0, GlobalPrompt.GT_Rob_Success % (roleName, npcName, reward[0], reward[1]))
#===============================================================================
# 战斗
#===============================================================================
def PVE_Goblin(role, fightId, fightType, npc):
	'''
	地精宝库小妖战斗 -- 怪物在右边, 玩家在左边
	@param role:
	@param fightId:mcid
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role)
	right_camp.create_monster_camp_unit(fightId)
	fight.start()
	
	#战斗后处理
	if fight.result is None:
		print "GE_EXC, GoblinTreasure fight with goblin error"
		return
	if fight.result != 1:
		return
	
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	
	npcId = npc.GetNPCID()
	npcDict = npc.GetPyDict()
	npcName = npc.GetNPCName()
	posX, posY = npc.GetPos()
	
	sceneId = npcDict[1]
	pos = npcDict[2]
	direct = npcDict[3]
	limitLevel = npcDict[5]
	
	role.SetCD(EnumCD.GT_Occ_CD, EnumGameConfig.GT_Sec)
	
	#删除npc
	global GT_SN_List
	GT_SN_List.remove((sceneId, npcId))
	npc.Destroy()
	
	#获取npc外形
	global GT_RobNpc_Dict
	npcType = GT_RobNpc_Dict.get((role.GetSex(), role.GetCareer()))
	if not npcType:
		return
	scene = cSceneMgr.SearchPublicScene(sceneId)
	if not scene:
		print "GE_EXC, GoblinTreasure can not find sceneId:(%s)" % sceneId
		return
	
	#胜利创建特殊npc
	robNpc = scene.CreateNPC(npcType, posX, posY, direct, 0, {EnumNPCData.EnNPC_Name : GlobalPrompt.GT_Rob_Name + roleName, EnumNPCData.EnNPC_Statu : EnumRoleStatus.GT_NPC})
	
	#注册tick
	tickId = cComplexServer.RegTick(EnumGameConfig.GT_Sec, WaitSecond, robNpc)
	
	#构建npc字典
	PackNpcDict(robNpc, sceneId, pos, direct, tickId, roleId, npcName, roleName, limitLevel)
	
	#加入npc列表
	GT_SN_List.append((sceneId, robNpc.GetNPCID()))
	
	#更新战斗数据
	RoleFightData.UpdateRoleFightData(role)
	
	#打包抢劫信息
	PackMsg(pos, npcName, roleName, 0)
	
def PVP_Goblin_D(role, right_role_data, fightType, npc):
	'''
	地精宝库与玩家离线数据战斗 -- 防守方先出手
	@param role:
	@param roleData:
	@param fightType:
	@param AfterFightRole:
	@param regparam:
	'''
	fight = Fight.Fight(fightType)
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_outline_role_unit(right_role_data)
	right_camp.create_online_role_unit(role, use_px = True)
	fight.start()
	
	if fight.result is None:
		print "GE_EXC, GoblinTreasure fight with role error"
		return
	if fight.result != -1:
		return
	
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	
	npcId = npc.GetNPCID()
	npcDict = npc.GetPyDict()
	posX, posY = npc.GetPos()
	
	sceneId = npcDict[1]
	pos = npcDict[2]
	direct = npcDict[3]
	tickId = npcDict[4]
	oRoleId = npcDict[5]
	npcName = npcDict[6]
	limitLevel = npcDict[8]
	
	#取消服务器tick
	cComplexServer.UnregTick(tickId)
	
	#清理玩家设置占领CD
	orole = cRoleMgr.FindRoleByRoleID(oRoleId)
	if orole:
		orole.SetCD(EnumCD.GT_Occ_CD, 0)
	role.SetCD(EnumCD.GT_Occ_CD, EnumGameConfig.GT_Sec)
	
	#根据性别、职业拿到要创建的npc外形
	global GT_RobNpc_Dict
	npcType = GT_RobNpc_Dict.get((role.GetSex(), role.GetCareer()))
	if not npcType:
		return
	scene = cSceneMgr.SearchPublicScene(sceneId)
	if not scene:
		print "GE_EXC, GoblinTreasure can not find sceneId:(%s)" % sceneId
		return
	
	if npc.GetNPCType() == npcType:
		#改名
		npc.SetPySyncDict(EnumNPCData.EnNPC_Name, GlobalPrompt.GT_Rob_Name + roleName)
		npc.AfterChange()
		#注册tick
		tickId = cComplexServer.RegTick(EnumGameConfig.GT_Sec, WaitSecond, npc)
		#修改tickId、roleId、roleName
		npc.SetPyDict(4, tickId)
		npc.SetPyDict(5, roleId)
		npc.SetPyDict(7, roleName)
	else:
		#删除npc
		global GT_SN_List
		GT_SN_List.remove((sceneId, npcId))
		npc.Destroy()
		#创建npc
		robNpc = scene.CreateNPC(npcType, posX, posY, direct, 0, {EnumNPCData.EnNPC_Name : GlobalPrompt.GT_Rob_Name + roleName, EnumNPCData.EnNPC_Statu : EnumRoleStatus.GT_NPC})
		tickId = cComplexServer.RegTick(EnumGameConfig.GT_Sec, WaitSecond, robNpc)
		#加入列表
		GT_SN_List.append((sceneId, robNpc.GetNPCID()))
		#构建劫宝npc字典
		PackNpcDict(robNpc, sceneId, pos, direct, tickId, roleId, npcName, roleName, limitLevel)
	
	#更新战斗数据
	RoleFightData.UpdateRoleFightData(role)
	
	#广播
	PackMsg(pos, npcName, roleName, 0)
	
def WaitSecond(argv, regparam):
	'''
	15s后劫宝成功,发放奖励
	@param argv:
	@param regparam:玩家Id, npcDict
	'''
	npc = regparam
	npcDict = npc.GetPyDict()
	
	#删除npc
	global GT_SN_List
	GT_SN_List.remove((npcDict[1], npc.GetNPCID()))
	npc.Destroy()
	
	#发放奖励
	RobReward(npcDict)
	
	#所有宝物被劫走, 结束劫宝活动
	if len(GT_RobMsg_DICT) != 4:
		return
	for robMsg in GT_RobMsg_DICT.values():
		if 0 == robMsg[1]:
			return
	else:
		EndRob()
	
def CreateGoblin():
	'''
	创建小妖
	'''
	global GT_SN_List
	global GT_WorldLevel
	
	if GT_SN_List: return
	
	if not GT_WorldLevel: return
	
	cfg = GTConfig.GTNpc_Dict.get(GT_WorldLevel)
	if not cfg:
		print "GE_EXC, CreateGoblin GoblinTreasure can not find GT_WorldLevel:(%s) in GTNpc_Dict" % GT_WorldLevel
		return
	
	sceneToNpcDict = cfg.sceneToNpc
	
	#场景名字列表
	sceneName = []
	
	for sceneId, NpcList in sceneToNpcDict.iteritems():
		scene = cSceneMgr.SearchPublicScene(sceneId)
		if not scene:
			print "GE_EXC, GoblinTreasure can not find sceneId:(%s)" % sceneId
			continue
		
		sceneName.append(scene.GetSceneName())
		if len(sceneName) > 2:
			print "GE_EXC, GoblinTreasure to much scene"
			continue
		
		for npc in NpcList:
			#创建npc
			npcObj = scene.CreateNPC(npc[0], npc[2], npc[3], npc[4], 0, {EnumNPCData.EnNPC_Statu : EnumRoleStatus.GT_NPC})
			#构建npc字典
			npcObj.SetPyDict(1, sceneId)				#场景Id
			npcObj.SetPyDict(2, npc[5])					#pos
			npcObj.SetPyDict(3, npc[4])					#direct
			npcObj.SetPyDict(4, npc[1])					#mcid
			#点击等级限制
			if npc[5] in (1, 2):
				npcObj.SetPyDict(5, cfg.levelLimit1)
			else:
				npcObj.SetPyDict(5, cfg.levelLimit2)
			#加入全局列表
			GT_SN_List.append((sceneId, npcObj.GetNPCID()))
	
	#提示所有玩家劫宝开始
	cNetMessage.PackPyMsg(GTRobBeginOrEnd, True)
	cRoleMgr.BroadMsg()
	
	#世界传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.GT_Begin_Tips % (sceneName[0], sceneName[1]))
	
def DestroyNpc():
	'''
	活动结束, 删除所有该活动创建的npc
	'''
	global GT_SN_List
	
	#逆序删除
	for nCfg in reversed(GT_SN_List):
		scene = cSceneMgr.SearchPublicScene(nCfg[0])
		if not scene:
			print "GE_EXC, GoblinTreasure can not find sceneId:(%s)" % nCfg[0]
			continue
		npc = scene.SearchNPC(nCfg[1])
		npcDict = npc.GetPyDict()
		#删除npc
		scene.DestroyNPC(nCfg[1])
		GT_SN_List.remove(nCfg)
		#这个npc是个特殊npc
		if npcDict.get(6):
			#取消tick
			cComplexServer.UnregTick(npcDict[4])
			#发放奖励
			RobReward(npcDict)
	
	if GT_SN_List:
		print "GE_EXC, GoblinTreasure destroy npc not clear"
		return
	
	#清理劫宝信息
	global GT_RobMsg_DICT
	GT_RobMsg_DICT = {}
	
	#重置匹配地精宝库的世界等级
	global GT_WorldLevel
	GT_WorldLevel = 0
	
	#提示所有玩家劫宝结束
	cNetMessage.PackPyMsg(GTRobBeginOrEnd, False)
	cRoleMgr.BroadMsg()
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.GT_End_Tips)
	
def RobReward(npcDict):
	'''
	发放劫宝奖励
	'''
	global GT_WorldLevel
	
	sceneId = npcDict[1]
	pos = npcDict[2]
	roleId = npcDict[5]
	npcName = npcDict[6]
	roleName = npcDict[7]
	
	#获取配置
	cfg = GTConfig.GTNpc_Dict.get(GT_WorldLevel)
	if not cfg:
		print "GE_EXC, RobReward GoblinTreasure can not find GT_WorldLevel:(%s) in GTNpc_Dict" % GT_WorldLevel
		return
	#随机奖励
	RD = cfg.rewardDict.get(sceneId)
	if not RD:
		print "GE_EXC, GoblinTreasure can not find sceneId:(%s) in cfg.rewardDict" % sceneId
		return
	reward = RD.RandomOne()
	
	#北美版
	if Environment.EnvIsNA():
		Call.LocalDBCall(roleId, OutLineCall, cDateTime.Days())
	
	role = cRoleMgr.FindRoleByRoleID(roleId)
	with GTRob_Log:
		if role:
			role.AddItem(*reward)
		else:
			#离线奖励邮件发放
			Mail.SendMail(roleId, GlobalPrompt.GT_Mail_Title, GlobalPrompt.GT_Mail_Send, GlobalPrompt.GT_Mail_Content, items = [reward, ])
	
	#取消玩家占领CD
	if role and role.GetCD(EnumCD.GT_Occ_CD):
		role.SetCD(EnumCD.GT_Occ_CD, 0)
	
	PackMsg(pos, npcName, roleName, 1, reward)
	
def OutLineCall(role, param):
	if cDateTime.Days() != param:
		return
	
	role.IncDI8(EnumDayInt8.GoblinRewardCnt, 1)
	
def ChoiceLevel():
	'''
	根据世界等级返回获取配置的key
	'''
	#世界数据没有载回, 不开启活动
	if not WorldData.WD.returnDB:
		print "GE_EXC, ChoiceLevel world data have not return"
		return
	
	worldLevel = WorldData.GetWorldLevel()
	
	tmp = 0
	if worldLevel < GTConfig.GTWorldLevel_List[0]:
		return
	for level in GTConfig.GTWorldLevel_List:
		if level > worldLevel:
			return tmp
		tmp = level
	else:
		return tmp
#===============================================================================
# 宝物兑换
#===============================================================================
def ExchangeTre(role, (coding, cnt)):
	'''
	兑换宝物
	'''
	if not cnt:
		return
	cfg = GTConfig.GT_Dict.get(coding)
	if not cfg:
		print "GE_EXC, GoblinTreasure can not find coding:(%s) in GT_Dict" % coding
		return
	#兑换个数超过限购个数
	if cfg.limitCnt < cnt:
		return
	#兑换需要的物品不足
	needCnt = cfg.needCnt * cnt
	if role.ItemCnt(cfg.needCoding) < needCnt:
		return
	#物品背包满
	if cfg.itemType == 1 and role.PackageIsFull():
		return
	#占卜背包满
	elif cfg.itemType == 2 and role.TarotPackageIsFull():
		return
	
	exRecordObj = role.GetObj(EnumObj.GT_Record)
	if cfg.limitCnt:
		#限购
		if coding not in exRecordObj:
			#没有购买过
			exRecordObj[coding] = cnt
		elif exRecordObj[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			#没有超过
			exRecordObj[coding] += cnt
		
	with GTExchange_Log:
		role.DelItem(cfg.needCoding, needCnt)
		role.SetObj(EnumObj.GT_Record, exRecordObj)
		if cfg.itemType == 1:
			role.AddItem(coding, cnt)
		elif cfg.itemType == 2:
			role.AddTarotCard(coding, cnt)
	role.SendObj(GoblinTreasureData, role.GetObj(EnumObj.GT_Record))
	role.Msg(2, 0, GlobalPrompt.GT_Exchang_S)
	
def Fly(role, pos):
	'''
	传送
	'''
	global GT_WorldLevel
	
	cfg = GTConfig.GTNpc_Dict.get(GT_WorldLevel)
	if not cfg:
		print "GE_EXC, Fly GoblinTreasure can not find GT_WorldLevel:(%s) in GTNpc_Dict" % GT_WorldLevel
		return
	
	#flyCfg --> [地图等级限制, (sceneId, posX, posY), 地图名字]
	flyCfg = cfg.PTP.get(pos)
	if not flyCfg:
		return
	
	#等级不足
	if role.GetLevel() < flyCfg[0]:
		role.Msg(2, 0, GlobalPrompt.GT_Fly % (flyCfg[2], flyCfg[0]))
		return
	
	#相同点不传送
	posX, posY= role.GetPos()
	if flyCfg[1][0] == role.GetSceneID() and posX == flyCfg[1][1] and posY == flyCfg[1][2]:
		return
	
	role.Revive(*flyCfg[1])
#===============================================================================
# 活动开启关闭
#===============================================================================
def BeginRob():
	'''
	活动开始, 通知客户端活动开始, 创建npc
	'''
	global GT_WorldLevel
	GT_WorldLevel = ChoiceLevel()
	#世界等级不够
	if not GT_WorldLevel:
		return
	
	global GTRob
	if GTRob: return
	GTRob = True
	
	#创建npc
	CreateGoblin()
	
def EndRob():
	'''
	活动结束, 通知客户端活动结束, 删除所有该活动创建的npc
	'''
	global GTRob
	if not GTRob: return
	GTRob = False
	
	#删除npc
	DestroyNpc()
#===============================================================================
# 上线同步
#===============================================================================
def SyncGoblinTreasureData(role, param):
	#同步客户端兑换记录
	role.SendObj(GoblinTreasureData, role.GetObj(EnumObj.GT_Record))
	
	global GTRob
	if not GTRob: return
	
	#通知客户端活动开始
	role.SendObj(GTRobBeginOrEnd, True)
	#同步客户端劫宝进度
	global GT_RobMsg_DICT
	role.SendObj(GTRobMsg, GT_RobMsg_DICT)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestExchange(role, msg):
	'''
	客户端请求兑换宝物
	@param role:
	@param msg:itemCoding
	'''
	if not msg: return
	
	if role.GetLevel() < EnumGameConfig.GT_Level:
		return
	
	ExchangeTre(role, msg)
	
def RequestFly(role, msg):
	'''
	请求飞到劫宝npc旁边
	@param role:
	@param msg:
	'''
	if not msg: return
	
	global GTRob
	#没有开启
	if not GTRob: return
	
	if role.GetLevel() < EnumGameConfig.GT_Level:
		return
	
	#北美版
	if Environment.EnvIsNA():
		if role.GetDI8(EnumDayInt8.GoblinRewardCnt) >= EnumGameConfig.GT_NA_REWARD_CNT_MAX:
			#提示
			role.Msg(2, 0, GlobalPrompt.GT_NA_No_Reward_Cnt)
			return
	
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	Fly(role, msg)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		InitGTNpcClickFun()
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncGoblinTreasureData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GT_Exchange", "请求兑换宝物"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GT_Fly", "请求飞到劫宝npc旁边"), RequestFly)
		
		Cron.CronDriveByMinute((2038, 1, 1), BeginRob, H = "H in (14, 15, 16, 17, 18, 19)", M = "M == 0 or M == 30")
		Cron.CronDriveByMinute((2038, 1, 1), EndRob, H = "H in (14, 15, 16, 17, 18, 19)", M = "M == 10 or M == 40")
		