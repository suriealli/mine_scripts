#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Flower.Flower")
#===============================================================================
# 鲜花系统
#===============================================================================
import Environment
import cProcess
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage, PyMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.Flower import FlowerConfig
from Game.Persistence import Contain
from Game.GlobalData import ZoneName
from Game.SystemRank import SystemRank
from Game.SysData import WorldData, WorldDataNotSync
from Game.Role.Data import EnumInt32, EnumInt8, EnumTempInt64

if "_HasLoad" not in dir():
	IsStart = False					#跨服鲜花榜是否开启
	IsWorshipStart = False			#跨服鲜花榜膜拜是否开启(膜拜会比排行榜晚一天结束)
	
	EndTime = 0						#活动结束时间戳
	WorshipEndTime = 0				#膜拜活动结束时间戳
	
	KuafuFlowerActID = 0			#活动id
	
	TmpManData = []					#临时护花榜数据
	TmpWomenData = []				#临时鲜花榜数据
	
	KuafuManRank = [] 				#跨服护花榜数据
	KuafuManRank_old = []			#昨日跨服护花榜
	KuafuWomenRank = []				#跨服鲜花榜数据
	KuafuWomenRank_old = []			#昨日跨服鲜花榜数据
	FirstManRoleId = 0				#昨日护花榜排名第一id
	FirstWomenRoleId = 0			#昨日鲜花榜排名第一id
	
	FlowerReceive = AutoMessage.AllotMessage("FlowerReceive", "收到鲜花")
	FlowerManData = AutoMessage.AllotMessage("FlowerManData", "护花榜数据")
	FlowerWomenData = AutoMessage.AllotMessage("FlowerWomenData", "鲜花榜数据")
	FlowerDonghua = AutoMessage.AllotMessage("FlowerDonghua", "播放飘花动画")
	FlowerMeili = AutoMessage.AllotMessage("FlowerMeili", "魅力值")
	FlowerSendSuccess = AutoMessage.AllotMessage("FlowerSendSuccess", "赠送成功")
	
	KuafuFlowerMeili = AutoMessage.AllotMessage("KuafuFlowerMeili", "跨服鲜花榜魅力值")
	KuafuFlowerRankOpen = AutoMessage.AllotMessage("KuafuFlowerRankOpen", "跨服鲜花榜开启")
	KuafuFlowerRankWorshipOpen = AutoMessage.AllotMessage("KuafuFlowerRankWorshipOpen", "跨服鲜花榜膜拜开启")
	KuafuFlowerRankTodayData = AutoMessage.AllotMessage("KuafuFlowerRankTodayData", "跨服鲜花榜排行榜今日数据")
	KuafuFlowerRankYesterdayData = AutoMessage.AllotMessage("KuafuFlowerRankYesterdayData", "跨服鲜花榜排行榜今日数据")
	KuafuFlowerRankWorshipData = AutoMessage.AllotMessage("KuafuFlowerRankWorshipData", "跨服鲜花榜膜拜数据")
	
	FlowerReceive_Log = AutoLog.AutoTransaction("FlowerReceive_Log", "送花奖励日志")
	FlowerClearing_Log = AutoLog.AutoTransaction("FlowerClearing_Log", "魅力值排行榜结算日志")
	FlowerWorship_Log = AutoLog.AutoTransaction("FlowerWorship_Log", "魅力值排行榜膜拜日志")
	KuafuFlowerRankResetType_Log = AutoLog.AutoTransaction("KuafuFlowerRankResetType_Log", "跨服鲜花榜重算区域类型日志")
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestSend(role, msg):
	'''
	请求赠送鲜花
	@param role:
	@param msg:
	'''
	level = role.GetLevel()
	if level < EnumGameConfig.FlowerLvLimit:
		return
	
	if not msg:
		return
	
	#赠送id, 鲜花数量, 寄语, 是否匿名
	sRoleId, flowerCnt, message, isAnonymous = msg
	
	#不能超过20个汉字
	if (not message) or (not len(message)) or (len(message) > 60):
		return
	
	roleId = role.GetRoleID()
	if roleId == sRoleId:
		#自己不能给自己送
		return
	
	if flowerCnt not in FlowerConfig.FlowerCntSet:
		return
	
	sRole = cRoleMgr.FindRoleByRoleID(sRoleId)
	if not sRole:
		#对方需要在线
		role.Msg(2, 0, GlobalPrompt.Flower_Outline)
		return
	if sRole.GetLevel() < EnumGameConfig.FlowerLvLimit:
		#需要够等级
		return
	
	flowerCfg = FlowerConfig.Flower_Dict.get(flowerCnt)
	if not flowerCfg:
		return
	
	if role.ItemCnt(flowerCfg.needItemCoding) < 1:
		#每次送一个
		return
	
	global FlowerMeili_Dict, IsStart
	with FlowerReceive_Log:
		#扣物品
		role.DelItem(flowerCfg.needItemCoding, 1)
		
		roleSex, roleName = role.GetSex(), role.GetRoleName()
		sRoleName = sRole.GetRoleName()
		
		#记录魅力值
		if roleId not in FlowerMeili_Dict[roleSex]:
			newValue = flowerCfg.meili
		else:
			newValue = FlowerMeili_Dict[roleSex][roleId][0] + flowerCfg.meili
		#每次重新写数据吧, 等级什么的会变
		#{role_id :[魅力值, 角色名, 角色等级, 角色经验, 角色id, 膜拜（此膜拜非跨服鲜花榜膜拜）]}
		FlowerMeili_Dict[roleSex][roleId] = [newValue,\
											roleName,\
											role.GetLevel(),\
											role.GetExp(),\
											roleId,\
											role.GetZDL(),\
											SystemRank.GetRoleFlower(role)]
		FlowerMeili_Dict.HasChange()
		if IsStart:
			#活动开启的时候记录一份不同于日常的数据
			if roleId not in FlowerMeili_Dict[3][roleSex]:
				kNewValue = flowerCfg.meili
			else:
				kNewValue = FlowerMeili_Dict[3][roleSex][roleId][0] + flowerCfg.meili
			#魅力值, 名字, 等级, 经验, 性别, 职业, 品阶, 时装武器, 时装衣服, 时装帽子, 时装翅膀, 进程id, 服务器名字
			FlowerMeili_Dict[3][roleSex][roleId] = [kNewValue,\
												roleName,\
												role.GetLevel(),\
												role.GetExp(),\
												roleSex,\
												role.GetCareer(),\
												role.GetGrade(),\
												role.GetZDL(),\
												role.GetTI64(EnumTempInt64.FashionWeapons),\
												role.GetTI64(EnumTempInt64.FashionClothes),\
												role.GetTI64(EnumTempInt64.FashionHat),\
												role.GetI8(EnumInt8.WingId),\
												cProcess.ProcessID,\
												ZoneName.ZoneName]
			FlowerMeili_Dict.HasChange()
		
		#同步魅力值
		role.SendObj(FlowerMeili, newValue)
		#结婚的加亲密值
		if role.GetI8(EnumInt8.MarryStatus) == 3:
			role.IncI32(EnumInt32.Qinmi, flowerCfg.qinmi)
		
		sRoleSex = sRole.GetSex()
		if sRoleId not in FlowerMeili_Dict[sRoleSex]:
			tnewValue = flowerCfg.meili
		else:
			tnewValue = FlowerMeili_Dict[sRoleSex][sRoleId][0] + flowerCfg.meili
		FlowerMeili_Dict[sRoleSex][sRoleId] = [tnewValue,\
											sRoleName,\
											sRole.GetLevel(),\
											sRole.GetExp(),\
											sRoleId,\
											sRole.GetZDL(),\
											SystemRank.GetRoleFlower(sRole)]
		FlowerMeili_Dict.HasChange()
		
		if IsStart:
			#活动开启的时候记录
			if sRoleId not in FlowerMeili_Dict[3][sRoleSex]:
				kNewValue = flowerCfg.meili
			else:
				kNewValue = FlowerMeili_Dict[3][sRoleSex][sRoleId][0] + flowerCfg.meili
			#魅力值, 名字, 等级, 经验, 性别, 职业, 品阶, 时装武器, 时装衣服, 时装帽子, 时装翅膀, 进程id, 服务器名字
			FlowerMeili_Dict[3][sRoleSex][sRoleId] = [kNewValue,\
													sRoleName,\
													sRole.GetLevel(),\
													sRole.GetExp(),\
													sRoleSex,\
													sRole.GetCareer(),\
													sRole.GetGrade(),\
													sRole.GetZDL(),\
													sRole.GetTI64(EnumTempInt64.FashionWeapons),\
													sRole.GetTI64(EnumTempInt64.FashionClothes),\
													sRole.GetTI64(EnumTempInt64.FashionHat),\
													sRole.GetI8(EnumInt8.WingId),\
													cProcess.ProcessID,\
													ZoneName.ZoneName]
			FlowerMeili_Dict.HasChange()
		
		#同步魅力值
		sRole.SendObj(FlowerMeili, tnewValue)
		
		if sRole.GetI8(EnumInt8.MarryStatus) == 3:
			sRole.IncI32(EnumInt32.Qinmi, flowerCfg.qinmi)
		
		#记录加完后的魅力值
		AutoLog.LogBase(roleId, AutoLog.eveFlowerMeili, (newValue, sRoleId, tnewValue, flowerCfg.meili))
	
	#通知收到鲜花
	sRole.SendObj(FlowerReceive, (roleId, roleName, flowerCnt, level, roleSex, role.GetCareer(), role.GetGrade()))
	#通知赠送成功
	role.SendObj(FlowerSendSuccess, (sRoleName, flowerCnt, flowerCfg.meili, flowerCfg.qinmi))
	
	#飘花动画
	if flowerCnt == 9:
		#对方飘花
		sRole.SendObj(FlowerDonghua, 1)
	elif flowerCnt == 99:
		#双方飘花
		role.SendObj(FlowerDonghua, 2)
		sRole.SendObj(FlowerDonghua, 2)
	elif flowerCnt == 999:
		#所有人飘花
		cNetMessage.PackPyMsg(FlowerDonghua, 3)
		cRoleMgr.BroadMsg()
		
	if flowerCfg.isRumor:
		#喇叭
		if isAnonymous:
			#匿名
			cRoleMgr.Msg(12, 0, GlobalPrompt.Flower_AnonymousSend % (sRoleName, flowerCnt, message))
		else:
			cRoleMgr.Msg(12, 0, GlobalPrompt.Flower_Send % (roleName, sRoleName, flowerCnt, message))
	
	if flowerCnt != 1:
		if isAnonymous:
			#匿名
			cRoleMgr.Msg(1, 0, GlobalPrompt.Flower_AnonymousSend % (sRoleName, flowerCnt, message))
		else:
			cRoleMgr.Msg(1, 0, GlobalPrompt.Flower_Send % (roleName, sRoleName, flowerCnt, message))
		
	role.Msg(2, 0, GlobalPrompt.Flower_SendSuccess % sRoleName)
	
def RequestFeedbackKiss(role, msg):
	'''
	回吻
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.FlowerLvLimit:
		return
	
	tRole = cRoleMgr.FindRoleByRoleID(msg)
	if not tRole:
		return
	if role.GetSex() == tRole.GetSex():
		#同性没有回吻
		return
	tRole.Msg(2, 0, GlobalPrompt.Flower_FeedbackKiss % role.GetRoleName())
	
def RequestManRank(role, msg):
	'''
	同步护花榜（男性）
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.FlowerLvLimit:
		return
	
	global TmpManData
	role.SendObj(FlowerManData, TmpManData)
	
def RequestWomenRank(role, msg):
	'''
	同步鲜花榜（女性）
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.FlowerLvLimit:
		return
	
	global TmpWomenData
	role.SendObj(FlowerWomenData, TmpWomenData)
#===============================================================================
# 事件
#===============================================================================
def RoleChangeGender(role, param):
	#变性后处理
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB:
		print 'GE_EXC, role change sex when FlowerMeili_Dict not returnDB %s' % role.GetRoleID()
		return
	
	roleId, roleSex = role.GetRoleID(), role.GetSex()
	
	#本地排行榜数据处理
	value = None
	if roleSex == 1 and roleId in FlowerMeili_Dict[2]:
		value = FlowerMeili_Dict[2][roleId]
		del FlowerMeili_Dict[2][roleId]
	elif roleSex == 2 and roleId in FlowerMeili_Dict[1]:
		value = FlowerMeili_Dict[1][roleId]
		del FlowerMeili_Dict[1][roleId]
	
	#跨服活动排行榜数据处理
	tValue = None
	if roleSex == 1 and roleId in FlowerMeili_Dict[3][2]:
		tValue = FlowerMeili_Dict[3][2][roleId]
		del FlowerMeili_Dict[3][2][roleId]
	elif roleSex == 2 and roleId in FlowerMeili_Dict[3][1]:
		tValue = FlowerMeili_Dict[3][1][roleId]
		del FlowerMeili_Dict[3][1][roleId]
	
	if value:
		FlowerMeili_Dict[roleSex][roleId] = value
	if tValue:
		FlowerMeili_Dict[3][roleSex][roleId] = tValue
	FlowerMeili_Dict.HasChange()
	
def SyncRoleOtherData(role, param):
	#上线同步魅力值
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB: return
	
	roleId, roleSex = role.GetRoleID(), role.GetSex()
	if roleId in FlowerMeili_Dict[roleSex]:
		role.SendObj(FlowerMeili, FlowerMeili_Dict[roleSex][roleId][0])
	else:
		role.SendObj(FlowerMeili, 0)
	
	global EndTime, WorshipEndTime
	role.SendObj(KuafuFlowerRankOpen, EndTime)
	role.SendObj(KuafuFlowerRankWorshipOpen, WorshipEndTime)
	
	#同步膜拜数据
	role.SendObj(KuafuFlowerRankWorshipData, FlowerMeili_Dict[4].get(roleId, 0))
#===============================================================================
# 时间触发
#===============================================================================
def CallPerHour():
	#每小时排序一次
	
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB: return
	
	global TmpManData, TmpWomenData
	TmpManData = FlowerMeili_Dict[1].items()
	TmpManData.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	TmpManData = TmpManData[:100]
	
	TmpWomenData = FlowerMeili_Dict[2].items()
	TmpWomenData.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	TmpWomenData = TmpWomenData[:100]
	
	if cDateTime.Hour() == 0:
		#活动数据每日清理
		FlowerMeili_Dict[3] = {1:{}, 2:{}}
		FlowerMeili_Dict[4] = {}
		FlowerMeili_Dict.HasChange()
		
		cNetMessage.PackPyMsg(KuafuFlowerRankWorshipData, 0)
		cRoleMgr.BroadMsg()
		
	if cDateTime.Hour() == 0 and cDateTime.WeekDay() == 1:
		#周一0点结算
		with FlowerClearing_Log:
			if TmpManData:
				#支持多个排名， 但目前只有排名第一有奖励
				for rank, data in enumerate(TmpManData):
					rank += 1
					for (begin, end), reward in FlowerConfig.FlowerLocalRank_Dict[1].iteritems():
						if (begin == end) and (rank == begin):
							#begin == end
							break
						elif (begin != end) and (begin <= rank <= end):
							#begin != end
							break
					else:
						print "GE_EXC, GetRankMailReward can not find index by rank (%s) KuafuFlowerRankToIndex_Dict" % rank
						return
					Mail.SendMail(data[0], GlobalPrompt.Flower_ManMail_Title, GlobalPrompt.Flower_Mail_Sender, GlobalPrompt.Flower_Mail_Content, items = reward)
					#只发第一
					break
				
			if TmpWomenData:
				for rank, data in enumerate(TmpWomenData):
					rank += 1
					for (begin, end), reward in FlowerConfig.FlowerLocalRank_Dict[2].iteritems():
						if (begin == end) and (rank == begin):
							#begin == end
							break
						elif (begin != end) and (begin <= rank <= end):
							#begin != end
							break
					else:
						print "GE_EXC, GetRankMailReward can not find index by rank (%s) KuafuFlowerRankToIndex_Dict" % rank
						return
					Mail.SendMail(data[0], GlobalPrompt.Flower_WomenMail_Title, GlobalPrompt.Flower_Mail_Sender, GlobalPrompt.Flower_Mail_Content, items = reward)
					#只发第一
					break
			#记录榜单
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveFlowerRankData, (TmpManData, TmpWomenData, FlowerMeili_Dict.data))
		
		#日常数据清理
		FlowerMeili_Dict[1] = {}
		FlowerMeili_Dict[2] = {}
		FlowerMeili_Dict.HasChange()
		TmpManData = []
		TmpWomenData = []
		
		cNetMessage.PackPyMsg(FlowerMeili, 0)
		cRoleMgr.BroadMsg()
		
def GetRankReward(sex, rank):
	if sex not in FlowerConfig.FlowerLocalRank_Dict:
		print 'GE_EXC, Flower GetRankReward can not find sex %s in FlowerLocalRank_Dict' % sex
		return
	for (begin, end), reward in FlowerConfig.FlowerLocalRank_Dict[sex].iteritems():
		if (begin == end) and (rank == begin):
			#begin == end
			return reward
		elif (begin != end) and (begin <= rank <= end):
			#begin != end
			return reward
	else:
		print "GE_EXC, GetRankMailReward can not find index by rank (%s) FlowerLocalRank_Dict" % rank
		return
	
#===============================================================================
# 数据载回
#===============================================================================
def AfterLoad():
	#载回处理
	global FlowerMeili_Dict, TmpManData, TmpWomenData
	if not FlowerMeili_Dict:
		#初始化
		FlowerMeili_Dict[1] = {}
		FlowerMeili_Dict[2] = {}
		FlowerMeili_Dict[3] = {1:{}, 2:{}}
		FlowerMeili_Dict[4] = {}
		FlowerMeili_Dict.HasChange()
	
	#载回时排序
	TmpManData = FlowerMeili_Dict[1].items()
	TmpManData.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	TmpManData = TmpManData[:100]
	
	TmpWomenData = FlowerMeili_Dict[2].items()
	TmpWomenData.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	TmpWomenData = TmpWomenData[:100]
	
	#尝试开启活动
	global KuafuFlowerActID
	TryUpdate(KuafuFlowerActID)
	
#===============================================================================
# 跨服鲜花
#===============================================================================
def RequestKuafuRankWorship(role, msg):
	'''
	请求膜拜
	@param role:
	@param msg:
	'''
	global IsWorshipStart
	if not IsWorshipStart: return
	
	if role.GetLevel() < EnumGameConfig.FlowerLvLimit:
		return
	
	global FlowerMeili_Dict, FirstManRoleId, FirstWomenRoleId
	if (not FirstManRoleId) and (not FirstWomenRoleId):
		#两个榜都没有产生第一
		return
	
	roleId = role.GetRoleID()
	if roleId in FlowerMeili_Dict[4]:
		return
	
	FlowerMeili_Dict[4][roleId] = 1
	FlowerMeili_Dict.HasChange()
	
	with FlowerWorship_Log:
		#膜拜获得金币
		money = role.GetLevel() * EnumGameConfig.FlowerWorshipCoe
		if money >= EnumGameConfig.FlowerWorshipMaxMoney:
			money = EnumGameConfig.FlowerWorshipMaxMoney
		role.IncMoney(money)
	role.SendObj(KuafuFlowerRankWorshipData, FlowerMeili_Dict[4][roleId])
	
	role.Msg(2, 0, GlobalPrompt.Flower_WorshipSuccess % money)
	
def RequestOpenKuafuFlowerRank(role, param):
	'''
	请求打开跨服鲜花榜面板
	@param role:
	@param param:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.FlowerLvLimit:
		return
	
	#同步今日排行榜
	global KuafuManRank, KuafuWomenRank, FlowerMeili_Dict
	role.SendObj(KuafuFlowerRankTodayData, (KuafuManRank, KuafuWomenRank))
	roleSex, roleId = role.GetSex(), role.GetRoleID()
	if roleSex not in FlowerMeili_Dict[3] or roleId not in FlowerMeili_Dict[3][roleSex]:
		role.SendObj(KuafuFlowerMeili, 0)
	else:
		role.SendObj(KuafuFlowerMeili, FlowerMeili_Dict[3][roleSex][roleId][0])
	
def RequestYesterdayKuafuFlowerRank(role, msg):
	'''
	请求打开跨服鲜花榜昨日数据
	@param role:
	@param msg:
	'''
	global IsWorshipStart
	if not IsWorshipStart: return
	
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB: return
	
	if role.GetLevel() < EnumGameConfig.FlowerLvLimit:
		return
	
	#同步昨日排行榜数据
	global KuafuManRank_old, KuafuWomenRank_old
	role.SendObj(KuafuFlowerRankYesterdayData, (KuafuManRank_old, KuafuWomenRank_old))
	
def OpenKuafuFlowerRank(callArgv, regparam):
	#开启跨服鲜花榜
	global IsStart
	if IsStart:
		print "GE_EXC, KuafuFlowerRank is already open"
	IsStart = True
	
	#记下激活的活动ID
	global KuafuFlowerActID, EndTime
	KuafuFlowerActID, EndTime = regparam
	
	TryUpdate(KuafuFlowerActID)
	
	cNetMessage.PackPyMsg(KuafuFlowerRankOpen, EndTime)
	cRoleMgr.BroadMsg()
	
def CloseKuafuFlowerRank(callArgv, regparam):
	#关闭跨服鲜花榜
	global IsStart
	if not IsStart:
		print "GE_EXC, KuafuFlowerRank is already close"
	IsStart = False
	
	global KuafuManRank, KuafuWomenRank, FlowerMeili_Dict
	#清理排行榜数据(这里只清理今日的, 昨日的会在膜拜结束后清理)
	KuafuManRank, KuafuWomenRank,  = [], []
	#清理本地排行榜数据、膜拜数据
	FlowerMeili_Dict[3] = {1:{}, 2:{}}
	FlowerMeili_Dict[4] = {}
	FlowerMeili_Dict.HasChange()
	
	global KuafuFlowerActID, EndTime
	KuafuFlowerActID, EndTime = 0, 0
	
	#广播结束
	cNetMessage.PackPyMsg(KuafuFlowerRankOpen, EndTime)
	cRoleMgr.BroadMsg()
	
def OpenKuafuFlowerRankWorship(callargv, regparam):
	#开启跨服鲜花榜膜拜
	global IsWorshipStart
	if IsWorshipStart:
		print "GE_EXC, KuafuFlowerRankWorship is already open"
	IsWorshipStart = True
	
	#膜拜结束时间
	global WorshipEndTime
	WorshipEndTime = regparam
	
	cNetMessage.PackPyMsg(KuafuFlowerRankWorshipOpen, WorshipEndTime)
	cRoleMgr.BroadMsg()
	
def CloseKuafuFlowerRankWorship(callargv, regparam):
	#关闭跨服鲜花榜膜拜
	global IsWorshipStart
	if not IsWorshipStart:
		print "GE_EXC, KuafuFlowerRankWorship is already close"
	IsWorshipStart = False
	
	global WorshipEndTime, FlowerMeili_Dict
	WorshipEndTime = 0
	FlowerMeili_Dict[4] = {}
	FlowerMeili_Dict.HasChange()
	
	global KuafuManRank_old, KuafuWomenRank_old, FirstManRoleId, FirstWomenRoleId
	KuafuManRank_old, KuafuWomenRank_old, FirstManRoleId, FirstWomenRoleId = [], [], 0, 0
	
	cNetMessage.PackPyMsg(KuafuFlowerRankWorshipOpen, WorshipEndTime)
	cRoleMgr.BroadMsg()
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global KuafuManRank, KuafuWomenRank
	KuafuManRank, KuafuWomenRank = msg
	
def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global KuafuManRank, KuafuWomenRank, KuafuManRank_old, KuafuWomenRank_old, FirstManRoleId, FirstWomenRoleId
	(KuafuManRank, KuafuWomenRank), (KuafuManRank_old, KuafuWomenRank_old), (FirstManRoleId, FirstWomenRoleId) = msg
	
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前50名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB: return
	
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType(), GetLogicRank()))
	
def GetServerType():
	return WorldDataNotSync.WorldDataPrivate.get(WorldDataNotSync.KuafuFlowerRankServerType)

def TryUpdate(activeID = 0, updateType = False):
	'''
	@param activeID:每次都要传入激活活动的ID, 如果ID不对的话尝试重新分配服务器类型
	@param updateType:是否需要更新服务器类型可选
	'''
	global IsStart
	if not IsStart: return
	
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
	ControlProxy.SendControlMsg(PyMessage.Control_GetFlowerRank, (cProcess.ProcessID, GetServerType(), GetLogicRank()))

def IsPersistenceDataOK():
	#依赖的持久化数据时候都已经载入完毕
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB:
		#魅力值数据
		return
	if not WorldData.WD.returnDB:
		#世界数据
		return False
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
		#不广播客户端世界数据
		return False
	return True

def TryResetServerType(activeID, updateType):
	#尝试重新计算服务器类型
	#当前服务器类型
	nowType = WorldDataNotSync.WorldDataPrivate.get(WorldDataNotSync.KuafuFlowerRankServerType)
	
	#尝试重新分配后的服务器类型
	serverType = ReturnServerType()
	if not serverType:
		return
	
	if not nowType:
		#没有服务器类型, 分配服务器类型, 活动ID
		SetServerType(serverType, activeID)
	elif nowType and (updateType or activeID != WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.KuafuFlowerRankActiveId]):
		#有服务器类型, 需要更新服务器类型或者激活活动的ID不一致, 尝试重新计算服务器类型
		SetServerType(serverType, activeID)
		
	serverType = GetServerType()
	if serverType:
		#服务器区域有了, 广播开始
		cNetMessage.PackPyMsg(KuafuFlowerRankOpen, True)
		cRoleMgr.BroadMsg()
	
	#检查服务器类型是否分配了
	return serverType

def ReturnServerType():
	#计算服务器类型并返回
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for serverType, cfg in FlowerConfig.KuafuFlowerRankServerType_Dict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			return serverType
	else:
		print "GE_EXC, TryResetServerType can not find kaifuDay (%s) in KuafuFlowerRankServerType_Dict" % kaifuDay
		#找不到的话返回第三区域服务器类型
		return 3
	
def SetServerType(serverType, activeID):
	#设置服务器类型和激活活动的ID
	
	with KuafuFlowerRankResetType_Log:
		oldServerType, oldActiveID = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.KuafuFlowerRankServerType], WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.KuafuFlowerRankActiveId]
		
		WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.KuafuFlowerRankServerType] = serverType
		WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.KuafuFlowerRankActiveId] = activeID
		
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKuafuFlowerRankType, (oldServerType, oldActiveID, serverType, activeID))
		
def GetLogicRank():
	#返回前50
	global FlowerMeili_Dict
	if not FlowerMeili_Dict.returnDB:
		return [], []
	
	manRankData = FlowerMeili_Dict[3][1].items()
	manRankData.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	manRankData = manRankData[:50]
	
	womenRankData = FlowerMeili_Dict[3][2].items()
	womenRankData.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	womenRankData = womenRankData[:50]
	
	return manRankData, womenRankData
	
def AfterSetKaiFuTime(param1, param2):
	#更改开服时间，尝试修改服务器区域类型
	#有服务器类型 --> 尝试修改服务器类型
	global KuafuFlowerActID
	TryUpdate(KuafuFlowerActID, updateType=True)

def AfterLoadWorldDataNotSync(param1, param2):
	#载入世界数据之后
	global KuafuFlowerActID
	TryUpdate(KuafuFlowerActID)

def AfterLoadWorldData(role, param):
	#载入世界数据之后
	global KuafuFlowerActID
	TryUpdate(KuafuFlowerActID)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		#魅力值 -- 周日0点要清理所有玩家的魅力值
		#{1:{男性魅力值}, 2:{女性魅力值}, 3:{活动期间魅力值   活动版本号:{1:{男性数据}, 2:{女性数据}}}, 4:{膜拜字典}}
		FlowerMeili_Dict = Contain.Dict("FlowerMeili_Dict", (2038, 1, 1), AfterLoad)
		
		Event.RegEvent(Event.Eve_RoleChangeGender, RoleChangeGender)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, AfterLoadWorldDataNotSync)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		
		Init.InitCallBack.RegCallbackFunction(TryUpdate)
		
		cComplexServer.RegBeforeNewHourCallFunction(CallPerHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Flower_Send", "请求赠送鲜花"), RequestSend)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Flower_FeedbackKiss", "请求回吻"), RequestFeedbackKiss)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Flower_ManRank", "请求护花榜"), RequestManRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Flower_WomenRank", "请求鲜花榜"), RequestWomenRank)
		
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuFlowerRank_Worship", "请求跨服鲜花榜膜拜"), RequestKuafuRankWorship)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuFlowerRank_OpenPanel", "请求打开跨服鲜花榜面板"), RequestOpenKuafuFlowerRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuFlowerRank_YesterdayData", "请求打开跨服鲜花榜昨日数据"), RequestYesterdayKuafuFlowerRank)
		
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicFlowerRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataFlowerRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataKuafuFlowerRankToLogic_T, OnControlUpdataRank_T)
		
		
