#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Slave.SlaveOperate")
#===============================================================================
# 奴隶系统
#===============================================================================
import Environment
import cDateTime
import cRoleMgr
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Persistence import BigTable
from Game.Fight import Fight
from Game.Role.Data import EnumInt1, EnumDayInt8, EnumTempObj
from Game.Role import Status, Event
from Game.Slave import SlaveConfig, SlaveDefine
from Game.RoleFightData import RoleFightData
from Game.Role.Mail import Mail
from Game.Union import UnionMgr
from Game.DailyDo import DailyDo
from Game.ThirdParty.QQLZ import QQLZShopMgr


if "_HasLoad" not in dir():
	#管理角色对象字典
	SlaveRole_Dict = {}

######################################################################################
Slave_Free = 1#自由人身份
Slave_Slave = 2#奴隶身份
Slave_Manster = 3#地主身份

######################################################################################
Enum_Slave_RoleName = 1		#自己的名字
Enum_Slave_RoleLevel = 2	#自己的等级
Enum_Slave_RolePortrait = 3	#自己的头像(性别，职业，进阶)
Enum_Slave_Statue = 4		#自己的身份
Enum_Slave_MansterID = 5	#主人ID
Enum_Slave_Slaves = 6		#奴隶数据字典{}
Enum_Slave_PlayTimes = 7	#互动CD时间戳
Enum_Slave_DayExp = 8		#今日的获得经验
Enum_Slave_Loser = 9		#手下败将列表
Enum_Slave_Enemy = 10		#仇人列表
Enum_Slave_UnionID = 11		#公会ID
Enum_Slave_UnionName = 12	#公会名字
Enum_Slave_Log = 13			#日志数据
######################################################################################
#存储在主人对象上面的奴隶数据字典KEY
S_LEVEL = 1			#奴隶等级
S_FREETIME = 2		#自动获得自由的时间戳
S_STARTWORKTIME = 3	#开始工作的时间戳
S_ENDWORKTIME = 4	#未来结束工作的时间戳
######################################################################################

def GetPlayReward(role, level):
	#获取互动奖励
	allReward, halfReward = SlaveConfig.SlavePlayReward_Dict.get(level)
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		return halfReward
	elif yyAntiFlag == 0:
		return allReward
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		return None

def InitSlave(role, isForce = False):
	#初始化奴隶系统
	if role.GetI1(EnumInt1.SlaveInitFlag) and isForce is False:
		return
	role.SetI1(EnumInt1.SlaveInitFlag, True)
	roleId = role.GetRoleID()
	if roleId in SlaveRole_Dict:
		print "GE_EXC, repeat InitSlave (%s)" % roleId
		return
	#初始化
	SlaveRole_Dict[roleId] = SlaveRole(roleId, role)

def AddLoser(roleId, loserId):
	#增加一个手下败将
	if loserId not in SlaveRole_Dict:
		return
	
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	sRole.AddLoser(loserId)

def AddEnemy(roleId, enemyId):
	#增加一个夺奴之敌
	if enemyId not in SlaveRole_Dict:
		return
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	sRole.AddEnemy(enemyId)



	


######################################################################################
#持久化数据操作对象
class SlaveData(object):
	def __init__(self, data):
		self.role_id = data["role_id"]
		self.slaveData = data["slaveData"]
	
	def HasChange(self):
		#改变之后
		Slave_BT.SetValue(self.__dict__)

######################################################################################
#角色对象
class SlaveRole(object):
	def __init__(self, roleId, role = None, slaveData = None):
		self.roleId = roleId
		self.role = role
		if role is not None:
			#自己的信息
			self.roleName = role.GetRoleName()
			self.roleLevel = role.GetLevel()
			self.rolePortrait = role.GetPortrait()
			self.unionId = role.GetUnionID()
			unionObj = role.GetUnionObj()
			if unionObj:
				self.unionName = unionObj.name
			else:
				self.unionName = ""
			
			#第一次初始化，是自由人
			self.statue = Slave_Free
			#主人信息
			self.mansterId = 0
			self.mansterLevel = 0
			self.mansterName = ""
			self.mansterUnionName = ""
			self.mansterPortrait = (0, 0, 0)
			
			#拥有的奴隶信息
			self.slave_dict = {}#slaveId --> [slaveLevel, freetimeSec, starWorkTimeSec, EndWorkTimeSec]
			#互动数据
			self.playCDTimes = 0			
			self.dayExp = 0
			#手下败将，仇人
			self.loser_list = []
			self.enemy_list = []
			#日志数据
			self.logdata = []
			#持久化数据对象
			self.slaveData = self.InitSlaveData()
			self.slaveData.HasChange()
			
		elif slaveData is not None:
			#持久化数据对象
			self.slaveData = SlaveData(slaveData)
			
			slaveData = slaveData["slaveData"]
			self.roleName = slaveData.get(Enum_Slave_RoleName, "")
			self.roleLevel = slaveData.get(Enum_Slave_RoleLevel, 31)
			self.rolePortrait = slaveData.get(Enum_Slave_RolePortrait, (0, 0, 0))
			self.unionId = slaveData.get(Enum_Slave_UnionID, 0)
			self.unionName = slaveData.get(Enum_Slave_UnionName, "")
			
			self.statue = slaveData.get(Enum_Slave_Statue, Slave_Free)
			#主人信息(全部数据载入完毕后，会更新)
			self.mansterId = slaveData.get(Enum_Slave_MansterID, 0)
			self.mansterLevel = 0
			self.mansterName = ""
			self.mansterUnionName = ""
			self.mansterPortrait = (0, 0, 0)
			
			#奴隶信息
			self.slave_dict = slaveData.get(Enum_Slave_Slaves, {})
			#互动数据
			self.playCDTimes = slaveData.get(Enum_Slave_PlayTimes, 0)
			self.dayExp = slaveData.get(Enum_Slave_DayExp, 0)
			
			#手下败将，仇人
			self.loser_list = slaveData.get(Enum_Slave_Loser, [])
			self.enemy_list = slaveData.get(Enum_Slave_Enemy, [])
			
			self.logdata = slaveData.get(Enum_Slave_Log, [])
			
		else:
			print "GE_EXC, error in SlaveRole init "
		
		self.slave_role_dict = {}
		
		
	def InitSlaveData(self):
		#初始化持久化数据对象
		data = {}
		data["role_id"] = self.roleId
		data["slaveData"] = {Enum_Slave_RoleName : self.roleName,
							Enum_Slave_RoleLevel: self.roleLevel,
							Enum_Slave_RolePortrait: self.rolePortrait,
							Enum_Slave_Statue:self.statue,
							Enum_Slave_MansterID:self.mansterId,
							Enum_Slave_Slaves: self.slave_dict,
							Enum_Slave_PlayTimes: self.playCDTimes,
							Enum_Slave_DayExp: self.dayExp,
							Enum_Slave_Loser: self.loser_list,
							Enum_Slave_Enemy: self.enemy_list,
							Enum_Slave_UnionID: self.unionId,
							Enum_Slave_UnionName: self.unionName,
							Enum_Slave_Log: self.logdata}
		return SlaveData(data)
	
	def SaveData(self):
		#保存数据
		self.slaveData.slaveData = {Enum_Slave_RoleName : self.roleName,
									Enum_Slave_RoleLevel: self.roleLevel,
									Enum_Slave_RolePortrait: self.rolePortrait,
									Enum_Slave_Statue:self.statue,
									Enum_Slave_MansterID:self.mansterId,
									Enum_Slave_Slaves: self.slave_dict,
									Enum_Slave_PlayTimes: self.playCDTimes,
									Enum_Slave_DayExp: self.dayExp,
									Enum_Slave_Loser: self.loser_list,
									Enum_Slave_Enemy: self.enemy_list,
									Enum_Slave_UnionID: self.unionId,
									Enum_Slave_UnionName: self.unionName,
									Enum_Slave_Log: self.logdata}
		self.slaveData.HasChange()
	
	def UpdataRole(self, role, save = False):
		#更新自己的数据
		self.role = role
		self.roleName = role.GetRoleName()
		self.roleLevel = role.GetLevel()
		self.rolePortrait = role.GetPortrait()
		self.unionId = role.GetUnionID()
		uobj = role.GetUnionObj()
		if uobj:
			self.unionName = uobj.name
		
		if self.slave_dict:
			if not self.slave_role_dict or len(self.slave_role_dict) != len(self.slave_dict):
				print "GE_EXC, error  not build link in slave UpdataRole (%s)" % self.roleId
				for slaveId in self.slave_dict.iterkeys():
					slaveRole = SlaveRole_Dict.get(slaveId)
					if not slaveRole:
						print "GE_EXC, error in slave UpdataRole not slaveRole"
						#需要TODO
						continue
					#奴隶主动更新主人的数据
					slaveRole.UpdataManster(self)
			else:
				for slaveRole in self.slave_role_dict.values():
					#奴隶主动更新主人的数据
					slaveRole.UpdataManster(self)
					
		if save is True:
			self.SaveData()
	
	def UpdataManster(self, manster = None):
		#更新主人的数据
		if manster is None:
			if not self.mansterId:
				return
			manster = SlaveRole_Dict.get(self.mansterId)
			if not manster:
				print "GE_EXC, UpdataManster not master slaverole (%s)" % self.roleId
				return False
		
		#建立一个互相缓存对象
		self.manster = manster
		manster.slave_role_dict[self.roleId] = self
		
		self.mansterId = manster.roleId
		self.mansterName = manster.roleName
		self.mansterLevel = manster.roleLevel
		self.mansterPortrait = manster.rolePortrait
		self.mansterUnionName = manster.unionName
		return True
	
	def UpdataSlave(self, slaveId, slaveData):
		#更新自己拥有的奴隶数据
		#可以做优化，主人缓存奴隶对象，奴隶缓存主人对象
		pass
	
	def GetSyncData(self):
		#获取自己的头像同步数据
		return (self.roleId, self.roleName, self.roleLevel, self.rolePortrait, self.unionName, self.statue)
	
	def GetSlavePlayData(self):
		#获取互动数据
		data_Dict = {}
		if not self.slave_dict:
			return data_Dict
		if not self.slave_role_dict or len(self.slave_role_dict) != len(self.slave_dict):
			print "GE_EXC, GetSlavePlayData not slave_role_dict (%s)" % self.roleId
			for slaveId in self.slave_dict.iterkeys():
				slaveRole = SlaveRole_Dict.get(slaveId)
				if not slaveRole:
					print "GE_EXC, GetSlavePlayData not slaveRole"
					continue
				data_Dict[slaveId] = (slaveRole.playCDTimes, slaveRole.GetSyncData())
		else:
			for slaveId, slaveRole in self.slave_role_dict.iteritems():
				data_Dict[slaveId] = (slaveRole.playCDTimes, slaveRole.GetSyncData())
		
		return data_Dict
	
	def GetSlaveExpData(self):
		data_Dict = {}
		if not self.slave_dict:
			return data_Dict
		if not self.slave_role_dict or len(self.slave_role_dict) != len(self.slave_dict):
			print "GE_EXC, error in GetSlaveExpData not slave_role_dict"
			for slaveId, sd in self.slave_dict.iteritems():
				slaveRole = SlaveRole_Dict.get(slaveId)
				if not slaveRole:
					#需要TODO
					continue
				data_Dict[slaveId] = (sd[S_STARTWORKTIME], sd[S_ENDWORKTIME], slaveRole.GetSyncData())
		else:
			for slaveId, slaveRole in self.slave_role_dict.iteritems():
				sd = self.slave_dict.get(slaveId)
				if not sd:
					print "GE_EXC, error in GetSlaveExpData not sd"
					continue
				data_Dict[slaveId] = (sd[S_STARTWORKTIME], sd[S_ENDWORKTIME], slaveRole.GetSyncData())
		return data_Dict
	
	def GetSlaveDictData(self, slaveID):
		return self.slave_dict.get(slaveID)
	
	def GetMansterData(self):
		#获取主人数据
		if self.statue != Slave_Slave:
			return None
		return (self.mansterId, self.mansterLevel, self.mansterName, self.mansterPortrait, self.mansterUnionName)
	
	def GetLog(self):
		#获取日志数据
		return self.logdata
	
	def AddLog(self, logType, param):
		self.logdata.insert(0, (logType, param))
		if len(self.logdata) > 12:
			#最多保存12个日志
			self.logdata = self.logdata[:12]
		
		if self.role and not self.role.IsKick():
			#发送日志
			self.role.SendObj_NoExcept(Slave_S_AddLog, (logType, param))
	
	def CallPerHour(self):
		if self.statue != Slave_Manster:
			return
		#看看是否有奴隶到自由
		nowSec = cDateTime.Seconds()
		for slaveId, slaveData in self.slave_dict.items():
			if slaveData[S_FREETIME] > nowSec:
				continue
			self.BeFree(slaveId)
	
	def BeFree(self, slaveId):
		#提取经验
		exp = self.GetSlaveExp(slaveId)
		#释放奴隶
		del self.slave_dict[slaveId]
		#清理缓存对象
		if slaveId in self.slave_role_dict:
			del self.slave_role_dict[slaveId]
		
		if len(self.slave_dict) <= 0:
			#没有奴隶了， 成为自由人
			self.statue = Slave_Free
			if self.role and not self.role.IsKick():
				self.role.SendObj(Slave_S_UpdataStatus, self.statue)
		
		#记录一个消息日志
		slave = SlaveRole_Dict.get(slaveId)
		#修改奴隶数据
		if slave:
			slave.ClearSlaveData()
			#获得经验(邮件)
			exp = self.GetRealExp(exp)
			self.MailExp(exp, SlaveDefine.content_1 % (slave.roleName, exp))
			#日志
			slave.AddLog(SlaveDefine.Log_15, (self.roleName, ))
			self.AddLog(SlaveDefine.Log_16, (slave.roleName, ))
		else:
			print "GE_EXC befree slave not this slave(%s)" % slaveId
			
		#触发修改持久化数据
		self.SaveData()
		
	
	def DayExpIsFull(self):
		maxExp = SlaveConfig.SlaveMaxExp_Dict.get(self.roleLevel)
		if not maxExp:
			return True
		return self.dayExp >= maxExp
		
	def IncExp(self, role, exp):
		exp = self.GetRealExp(exp)
		if not exp:
			return
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			exp = exp / 2
		elif yyAntiFlag == 0:
			pass
		else:
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
			exp = 0
			return
		self.dayExp += exp
		self.SaveData()
		role.IncExp(exp)
		role.SendObj(Slave_S_UpdataSlaveExpData, self.dayExp)
		
		role.Msg(2, 0, GlobalPrompt.Exp_Tips % exp)

	
	def GetRealExp(self, exp):
		maxExp = SlaveConfig.SlaveMaxExp_Dict.get(self.roleLevel)
		if not maxExp:
			return 0
		if self.dayExp >= maxExp:
			#经验已经满了
			return 0
		return min(exp, maxExp - self.dayExp)
		
	def MailExp(self, mail_exp, content):
		self.dayExp += mail_exp
		with Tra_Slave_Mail:
			#邮件发送经验
			Mail.SendMail(self.roleId, SlaveDefine.mailTitle, SlaveDefine.mainSender, content, exp = mail_exp)
	
	def CanCatch(self, role = None):
		#是否可以捉别人
		if self.statue == Slave_Slave:
			#如果自己是奴隶，不能抓
			return False
		#最多可以抓3个
		if len(self.slave_dict) >= 3:
			if role:
				role.Msg(2, 0, GlobalPrompt.Slave_Tips_5)
			return False
		return True
		

	
	def CatchLose(self, other):
		#抓捕失败的各种不同的日志
		if other.statue == Slave_Free:
			self.AddLog(SlaveDefine.Log_2, (other.roleName, ))
			other.AddLog(SlaveDefine.Log_4, (self.roleName, ))
		elif other.statue == Slave_Manster:
			self.AddLog(SlaveDefine.Log_6, (other.roleName, ))
			if not other.slave_dict:
				#强制修正
				other.statue = Slave_Free
				print "GE_EXC slave, CatchLose statue error (%s)" % other.roleId
				return
			slaveId = other.slave_dict.keys()[0]
			slaveRole = SlaveRole_Dict.get(slaveId)
			if slaveRole:
				other.AddLog(SlaveDefine.Log_8, (self.roleName, slaveRole.roleName))
		else:
			manster = SlaveRole_Dict.get(other.roleId)
			if manster:
				self.AddLog(SlaveDefine.Log_6, (manster.roleName, ))
				manster.AddLog(SlaveDefine.Log_8, (self.roleName, other.roleName))

	def CatchSlave(self, slave):
		#抓到一个奴隶(需要判断奴隶身份，如果是主人，则抢他一个奴隶)
		#修改自己状态
		#self.statue = Slave_Manster
		if slave.statue == Slave_Free:
			#抓住的是自由人
			self.AddSlave(slave)
			#日志
			self.AddLog(SlaveDefine.Log_1, (slave.roleName, ))
			slave.AddLog(SlaveDefine.Log_3, (self.roleName, ))
		elif slave.statue == Slave_Slave:
			#抓住了一个别人的奴隶
			if slave.playCDTimes > cDateTime.Seconds():
				#这个奴隶竟然处在互动CD中，需要一个提示
				if self.role and not self.role.IsKick():
					self.role.Msg(2, 0, GlobalPrompt.Slave_Tips_4)
				return
			
			oldmanster = SlaveRole_Dict.get(slave.mansterId)
			if oldmanster:
				oldmanster.BeGrab(self, slave)
			else:
				self.AddSlave(slave)
				self.AddLog(SlaveDefine.Log_1, (slave.roleName, ))
				slave.AddLog(SlaveDefine.Log_3, (self.roleName, ))
		else:
			#打赢的是一个地主，随机抢夺一名奴隶
			slave.RandomGrab(self)
		
	def AddSlave(self, slave):
		#获得一个奴隶
		self.statue = Slave_Manster
		slave.statue = Slave_Slave
		slave.UpdataManster(self)
		
		#创建奴隶数据
		nowSec = cDateTime.Seconds()
		self.slave_dict[slave.roleId] = {S_LEVEL : slave.roleLevel, S_FREETIME : nowSec + 24 * 3600, S_STARTWORKTIME: nowSec, S_ENDWORKTIME : nowSec + 24 * 3600}
		#清理这个奴隶的互动CD
		slave.playCDTimes = 0
		#触发修改持久化数据
		self.SaveData()
		slave.SaveData()
		if self.role:
			self.role.SendObj_NoExcept(Slave_S_UpdataStatus, self.statue)
		if slave.role:
			slave.role.SendObj_NoExcept(Slave_S_UpdataStatus, slave.statue)

	def BeGrab(self, grabRole, slave):
		#被某个人抢了一个奴隶
		#先提取经验
		exp = self.GetSlaveExp(slave.roleId)
		
		#清理数据
		if slave.roleId in self.slave_dict:
			del self.slave_dict[slave.roleId]
		if len(self.slave_dict) <= 0:
			self.statue = Slave_Free
			if self.role:
				self.role.SendObj_NoExcept(Slave_S_UpdataStatus, self.statue)
		#清理缓存对象
		if slave.roleId in self.slave_role_dict:
			del self.slave_role_dict[slave.roleId]
		
		#抢得一个奴隶
		grabRole.AddSlave(slave)
		#触发修改持久化数据
		self.SaveData()
		
		#邮件经验
		exp = self.GetRealExp(exp)
		self.MailExp(exp, SlaveDefine.content_3 % (slave.roleName, grabRole.roleName, exp))
		
		#增加一个夺奴之敌
		AddEnemy(self.roleId, grabRole.roleId)
		#分类日志
		grabRole.AddLog(SlaveDefine.Log_5, (self.roleName, slave.roleName, slave.roleName))
		slave.AddLog(SlaveDefine.Log_3, (grabRole.roleName, ))
		self.AddLog(SlaveDefine.Log_7, (grabRole.roleName, slave.roleName))
		
		
	def RandomGrab(self, grabRole):
		#随机被抢夺的奴隶
		if len(self.slave_dict) < 1:
			print "GE_EXC RandomGrab not slave statue"
			#强制修正
			self.statue = Slave_Free
			#抓住的是自由人
			grabRole.AddSlave(self)
			#日志
			grabRole.AddLog(SlaveDefine.Log_1, (self.roleName, ))
			self.AddLog(SlaveDefine.Log_3, (grabRole.roleName, ))
			return
		beGrabOne = None
		nowSec = cDateTime.Seconds()
		for slaveRole in self.slave_role_dict.itervalues():
			if slaveRole.playCDTimes <= nowSec:
				beGrabOne = slaveRole
				break
		
		if beGrabOne is None:
			#所有的奴隶都在CD中
			if grabRole.role and not grabRole.role.IsKick():
				grabRole.role.Msg(2, 0, GlobalPrompt.Slave_Tips_4)
			return

		self.BeGrab(grabRole, beGrabOne)

	def AddLoser(self, loserId):
		#增加一个手下败将，按照增加顺序优先排序，不超过20人
		if loserId not in self.loser_list:
			self.loser_list.insert(0, loserId)
			if len(self.loser_list) > 20:
				self.loser_list = self.loser_list[:20]
		else:
			self.loser_list.remove(loserId)
			self.loser_list.insert(0, loserId)
		#触发修改持久化数据
		self.SaveData()
	
	def AddEnemy(self, enemyId):
		#增加一个仇人，规则同上
		if enemyId not in self.enemy_list:
			self.enemy_list.insert(0, enemyId)
			if len(self.enemy_list) > 20:
				self.enemy_list = self.enemy_list[:20]
		else:
			self.enemy_list.remove(enemyId)
			self.enemy_list.insert(0, enemyId)
		
		#触发修改持久化数据
		self.SaveData()
	
	def DelLoserOrEnemy(self, roleId):
		#删除一个仇人或者夺奴之敌
		if roleId in self.loser_list:
			self.loser_list.remove(roleId)
			return
		if roleId in self.enemy_list:
			self.enemy_list.remove(roleId)
		#触发修改持久化数据
		self.SaveData()
	
	def ReleaseSlave(self, role, slaveId):
		#释放一个奴隶
		slaveData = self.slave_dict.get(slaveId)
		if not slaveData:
			return False
		
		#判断是否互动CD中
		slave = SlaveRole_Dict.get(slaveId)
		if not slave:
			print "GE_EXC, error in ReleaseSlave not slave role"
			return False
		if slave.playCDTimes > cDateTime.Seconds():
			#互动CD中
			role.Msg(2, 0, GlobalPrompt.Slave_Tips_2)
			return False
		#提取经验
		exp = self.GetSlaveExp(slaveId)
		
		#释放奴隶
		del self.slave_dict[slaveId]
		if len(self.slave_dict) <= 0:
			#没有奴隶了， 成为自由人
			self.statue = Slave_Free
			role.SendObj(Slave_S_UpdataStatus, self.statue)
		
		#清理缓存对象
		if slaveId in self.slave_role_dict:
			del self.slave_role_dict[slaveId]

		#修改奴隶数据
		slave.ClearSlaveData()
		#获得经验
		self.IncExp(role, exp)
		#触发修改持久化数据
		self.SaveData()
		#日志
		self.AddLog(SlaveDefine.Log_14, (slave.roleName, ))
		slave.AddLog(SlaveDefine.Log_13, (self.roleName, ))
		return True
	
	def ClearSlaveData(self):
		#变成自由人，清理数据
		self.playCDTimes = 0
		self.statue = Slave_Free
		
		self.manster = None
		self.mansterId = 0
		self.mansterName = ""
		self.mansterPortrait = (0, 0, 0)
		
		#触发修改持久化数据
		self.SaveData()
		
		if self.role:
			self.role.SendObj_NoExcept(Slave_S_UpdataStatus, self.statue)

	def BeSave(self, saver):
		#被拯救了,清理数据,写日志
		manster = SlaveRole_Dict.get(self.mansterId)
		if manster:
			exp = manster.GetSlaveExp(self.roleId)
			del manster.slave_dict[self.roleId]
			if len(manster.slave_dict) <= 0:
				#没有奴隶了， 成为自由人
				manster.statue = Slave_Free
				if manster.role:
					manster.role.SendObj_NoExcept(Slave_S_UpdataStatus, manster.statue)
			#删除缓存对象
			if self.roleId in manster.slave_role_dict:
				del manster.slave_role_dict[self.roleId]
			#邮件发送信息
			exp = manster.GetRealExp(exp)
			manster.MailExp(exp, SlaveDefine.content_2 % (self.roleName, saver.roleName, exp))
			#日志
			manster.AddLog(SlaveDefine.Log_12, (saver.roleName, self.roleName))
			saver.AddLog(SlaveDefine.Log_10, (manster.roleName, self.roleName))
			manster.SaveData()
			
		self.ClearSlaveData()
		
		if self.role:
			self.role.SendObj_NoExcept(Slave_S_UpdataStatus, self.statue)
	
	def BattleWin(self, mansterRole):
		#反抗成功
		exp = mansterRole.GetSlaveExp(self.roleId)

		del mansterRole.slave_dict[self.roleId]
		if len(mansterRole.slave_dict) <= 0:
			#没有奴隶了， 成为自由人
			mansterRole.statue = Slave_Free
			if mansterRole.role:
				mansterRole.role.SendObj_NoExcept(Slave_S_UpdataStatus, mansterRole.statue)
		#删除缓存对象
		if self.roleId in mansterRole.slave_role_dict:
			del mansterRole.slave_role_dict[self.roleId]
		#邮件发送信息
		exp = mansterRole.GetRealExp(exp)
		mansterRole.MailExp(exp, SlaveDefine.content_4 % (self.roleName, exp))
		
		#修正自己的数据
		self.ClearSlaveData()
		mansterRole.SaveData()
		#日志
		mansterRole.AddLog(SlaveDefine.Log_19, (self.roleName, ))
		self.AddLog(SlaveDefine.Log_17, (mansterRole.roleName, ))
	
	
	def BeHelp(self, mansterRole, helperRole):
		#求助成功
		exp = mansterRole.GetSlaveExp(self.roleId)

		del mansterRole.slave_dict[self.roleId]
		if len(mansterRole.slave_dict) <= 0:
			#没有奴隶了， 成为自由人
			mansterRole.statue = Slave_Free
			if mansterRole.role:
				mansterRole.role.SendObj_NoExcept(Slave_S_UpdataStatus, mansterRole.statue)
		#删除缓存对象
		if self.roleId in mansterRole.slave_role_dict:
			del mansterRole.slave_role_dict[self.roleId]
		
		#邮件发送信息
		exp = mansterRole.GetRealExp(exp)
		mansterRole.MailExp(exp, SlaveDefine.content_2 % (self.roleName, helperRole.roleName, exp))
		
		#修正自己的数据
		self.ClearSlaveData()
		mansterRole.SaveData()
		#日志
		mansterRole.AddLog(SlaveDefine.Log_24, (helperRole.roleName, self.roleName))
		self.AddLog(SlaveDefine.Log_22, (helperRole.roleName, ))
	
	
	def GetSlaveExp(self, slaveId):
		#提取经验
		slaveDataDict = self.slave_dict.get(slaveId)
		if not slaveDataDict:
			return 0
		
		nowSec = cDateTime.Seconds()
		endSec = min(slaveDataDict[S_ENDWORKTIME], nowSec)
		totalSec = endSec - slaveDataDict[S_STARTWORKTIME]
		if totalSec <= 0:
			return 0
		expPerSec = SlaveConfig.SlaveExp_Dict.get(slaveDataDict[S_LEVEL])
		if not expPerSec:
			print "GE_EXC, error in GetSlaveExp cfg null level(%s)" % slaveDataDict[S_LEVEL]
			return 0
		#总的经验
		totalExp = expPerSec * totalSec / 10000
		if totalExp <= 0:
			return 0
		#更新起始工作时间为当前时间
		slaveDataDict[S_STARTWORKTIME] = nowSec
		
		#保存数据
		self.SaveData()
		return totalExp
	
	def GetSlaveExpOneHour(self, role, slaveId):
		#提交经验，强制提取一个小时经验
		slaveDataDict = self.slave_dict.get(slaveId)
	
		expPerSec = SlaveConfig.SlaveExp_Dict.get(slaveDataDict[S_LEVEL])
		if not expPerSec:
			print "GE_EXC, error in GetSlaveExpOneHour cfg null level(%s)" % slaveDataDict[S_LEVEL]
			return
		
		nowSec = cDateTime.Seconds()
		endSec = slaveDataDict[S_ENDWORKTIME]
		if endSec < nowSec:
			#这里不可能把
			print "GE_EXC, error in GetSlaveExpOneHour"
			return
		totalSec = nowSec - slaveDataDict[S_STARTWORKTIME]
		#计算总经验 = 已经工作的经验 + 压榨一个小时的经验
		totalExp = expPerSec * totalSec / 10000
		totalExp += expPerSec * 3600 / 10000
		#扣除魔晶
		role.DecRMB(EnumGameConfig.SlaveOnHourNeedRMB)
		#更新起始工作时间为当前时间
		slaveDataDict[S_STARTWORKTIME] = nowSec
		#更新结束时间(扣除一个小时,有可能导致结束时间比开始时间少，麻烦客户端和谐)
		slaveDataDict[S_ENDWORKTIME] = endSec - 3600
		
		#保存数据
		self.SaveData()
		return totalExp
	
	
	def GetExpToDie(self, role, slaveId):
		#抽干经验
		slaveDataDict = self.slave_dict.get(slaveId)
		
		expPerSec = SlaveConfig.SlaveExp_Dict.get(slaveDataDict[S_LEVEL])
		if not expPerSec:
			print "GE_EXC, error in GetExpToDie cfg null level(%s)" % slaveDataDict[S_LEVEL]
			return 0
		
		nowSec = cDateTime.Seconds()
		endSec = slaveDataDict[S_ENDWORKTIME]
		if endSec < nowSec:
			print "GE_EXC, error in GetExpToDie"
			return 0
		#已经工作的时间,可以计算出已经工作的经验
		totalFinishWorkSec = nowSec - slaveDataDict[S_STARTWORKTIME]
		#剩余工作时间,推算出多少个小时，并且计算需要花费的魔晶
		totalWordSec = endSec - nowSec
		hour = 0
		if totalWordSec <= 3600:
			#不足一个小时按照一个小时算
			hour = 1
		else:
			hour = totalWordSec / 3600
			if totalWordSec % 3600 > 0:
				hour += 1
		
		needRMB = EnumGameConfig.SlaveOnHourNeedRMB * hour
		if not needRMB:
			return 0
		
		if role.GetRMB() < needRMB:
			return 0
		
		role.DecRMB(needRMB)
		totalExp = expPerSec * totalFinishWorkSec / 10000
		totalExp += expPerSec * hour * 3600 / 10000
		#更新起始工作时间为当前时间
		slaveDataDict[S_STARTWORKTIME] = nowSec
		#更新结束时间(扣除所有的时间，就是开始时间和结束时间都是一样的)
		slaveDataDict[S_ENDWORKTIME] = nowSec
		#保存数据
		self.SaveData()
		return totalExp
		
	def Play(self, role, playRoleId, playType):
		#互动
		if self.statue == Slave_Free:
			#自由人不能互动
			return False
		
		nowSec = cDateTime.Seconds()
		if self.playCDTimes > nowSec:
			#互动CD中
			return False
		if self.statue == Slave_Manster:
			#主人和奴隶互动
			slave = SlaveRole_Dict.get(playRoleId)
			if not slave:
				return False
			slaveData = self.slave_dict.get(playRoleId)
			if not slaveData:
				return False

			if slave.playCDTimes > nowSec:
				#这个奴隶存在互动CD中
				return False
			#获取互动奖励
			item = GetPlayReward(role, slave.roleLevel)
			if not item:
				return False
			with Tra_Slave_Play:
				if QQLZShopMgr.IsQQLZ(role) and role.GetDI8(EnumDayInt8.QQLZBuffSlave) < EnumGameConfig.QQLZSlaveBuff:
					#优先扣除蓝钻渠道蓝钻特权次数
					role.IncDI8(EnumDayInt8.QQLZBuffSlave, 1)
				else:
					#扣除互动次数
					role.IncDI8(EnumDayInt8.Slave_PlayTimes, 1)
				#增加CD
				slave.playCDTimes = nowSec + EnumGameConfig.SlavePlayCD
				#保存数据
				self.SaveData()
				#发奖
				itemCoding, itemCnt = item
				role.AddItem(itemCoding, itemCnt)
				
				#双方互动日志
				if playType == 1:
					self.AddLog(SlaveDefine.Log_25, (slave.roleName, ))
					slave.AddLog(SlaveDefine.Log_26, (self.roleName, ))
				else:
					self.AddLog(SlaveDefine.Log_27, (slave.roleName, ))
					slave.AddLog(SlaveDefine.Log_28, (self.roleName, ))
				#活跃度任务
				Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_SlaveOperate, 1))
				#奖励提示
				role.Msg(2, 0, GlobalPrompt.Item_Tips % (itemCoding, itemCnt))
			return slave.playCDTimes 
		else:
			#奴隶和主人互动
			if self.mansterId != playRoleId:
				#只能和主人互动
				return False
			
			mansterRole = SlaveRole_Dict.get(playRoleId)
			if not mansterRole:
				return False
			#获取互动奖励
			item = GetPlayReward(role, mansterRole.roleLevel)
			if not item:
				return False
			with Tra_Slave_Play:
				if QQLZShopMgr.IsQQLZ(role) and role.GetDI8(EnumDayInt8.QQLZBuffSlave) < EnumGameConfig.QQLZSlaveBuff:
					#优先扣除蓝钻渠道蓝钻特权次数
					role.IncDI8(EnumDayInt8.QQLZBuffSlave, 1)
				else:
					#扣除互动次数
					role.IncDI8(EnumDayInt8.Slave_PlayTimes, 1)
				#更新互动CD
				self.playCDTimes = nowSec + EnumGameConfig.SlavePlayCD
				#保存数据
				self.SaveData()
				#发奖
				itemCoding, itemCnt = item
				role.AddItem(itemCoding, itemCnt)
				
				#双方互动日志
				if playType == 1:
					self.AddLog(SlaveDefine.Log_29, (mansterRole.roleName, ))
					mansterRole.AddLog(SlaveDefine.Log_30, (self.roleName, ))
				else:
					self.AddLog(SlaveDefine.Log_31, (mansterRole.roleName, ))
					mansterRole.AddLog(SlaveDefine.Log_32, (self.roleName, ))
				#活跃度任务
				Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_SlaveOperate, 1))
				#奖励提示
				role.Msg(2, 0, GlobalPrompt.Item_Tips % (itemCoding, itemCnt))
			return self.playCDTimes
		return False
	
######################################################################################
#战斗相关
######################################################################################
def PVP_Slave(role, right_role_data, fightType, regParam, AfterFight, AfterPlay, OnLeave = None):
	'''
	抓奴隶，反抗,解救战斗
	@param role:
	@param roleData:
	@param fightType:
	@param AfterFightRole:
	@param regparam:
	'''
	fight = Fight.Fight(fightType)
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True)
	right_camp.create_outline_role_unit(right_role_data)
	
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam
	
	fight.start()

def PVP_Help(role, left_role_data, right_role_data, fightType, regParam, AfterFight, AfterPlay, OnLeave = None):
	'''
	公会求救
	@param role:
	@param roleData:
	@param fightType:
	@param AfterFightRole:
	@param regparam:
	'''
	fight = Fight.Fight(fightType)
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, 0, left_role_data, use_px = True)
	right_camp.create_outline_role_unit(right_role_data)
	
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam
	
	fight.start()

######################################################################################
#客户端消息处理
######################################################################################
def RequestMainData(role, msg):
	'''
	请求面板数据
	@param role:
	@param msg:
	'''
	backId, _ = msg
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	#同步数据
	role.CallBackFunction(backId, (sRole.statue, sRole.playCDTimes, sRole.dayExp, sRole.GetMansterData(), sRole.GetLog()))
	
def RequestPlaySlaveData(role, msg):
	'''
	请求主人和奴隶互动的数据
	@param role:
	@param msg:
	'''
	backId, _ = msg
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	role.CallBackFunction(backId, sRole.GetSlavePlayData())

def RequestSlaveExpData(role, msg):
	'''
	请求奴隶工作经验数据
	@param role:
	@param msg:
	'''
	backId, _ = msg
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	role.CallBackFunction(backId, sRole.GetSlaveExpData())

def RequestLoserEnemyData(role, msg):
	'''
	请求手下败将夺奴之敌数据列表
	@param role:
	@param msg:
	'''
	backId, _ = msg
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	
	if sRole.statue == Slave_Slave:
		#自己是奴隶，不能查看
		return
	SD = sRole.slave_dict
	SG = SlaveRole_Dict.get
	loserdataList = []
	LA = loserdataList.append
	for rId in sRole.loser_list:
		if rId in SD:
			#是自己的奴隶
			continue
		sr = SG(rId)
		if not sr:
			#没有这个对象
			continue
		
		LA((sr.GetSyncData(), sr.mansterName))
	enemydataList = []
	EA = enemydataList.append
	for rId in sRole.enemy_list:
		if rId in SD:
			#是自己的奴隶
			continue
		sr = SG(rId)
		if not sr:
			continue
		EA((sr.GetSyncData(), sr.mansterName))
	
	role.CallBackFunction(backId, (loserdataList, enemydataList))

def RequestHelpList(role, msg):
	'''
	请求求助数据列表
	@param role:
	@param msg:
	'''
	backId, _ = msg
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	
	if sRole.statue != Slave_Slave:
		#不是奴隶，不能查看求助列表
		return
	mansterId = sRole.mansterId
	dataList = []
	DA = dataList.append
	SG = SlaveRole_Dict.get
	for sroleId in unionObj.members.iterkeys():
		if sroleId == roleId or mansterId == sroleId:
			#自己,或者自己的主人
			continue
		sr = SG(sroleId)
		if not sr:
			continue
		if sr.statue == Slave_Slave:
			continue
		DA(sr.GetSyncData())
		
	role.CallBackFunction(backId, dataList)
	
def RequestSaveList(role, msg):
	'''
	可以解救的奴隶数据列表
	@param role:
	@param msg:
	'''
	backId, _ = msg
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	
	if sRole.statue == Slave_Slave:
		#奴隶，不能
		return

	dataList = []
	DA = dataList.append
	SG = SlaveRole_Dict.get
	for sroleId in unionObj.members.iterkeys():
		if sroleId == roleId:
			continue
		sr = SG(sroleId)
		if not sr:
			continue
		if sr.statue != Slave_Slave or sr.mansterId == roleId:
			#不是奴隶或者是自己的奴隶
			continue
		DA((sr.GetSyncData(), sr.mansterName))
		
	role.CallBackFunction(backId, dataList)

def BuyCatchTime(role, msg):
	'''
	购买抓捕次数
	@param role:
	@param msg:
	'''
	if not role.GetI1(EnumInt1.SlaveInitFlag) : return
	
	buyTimes = role.GetDI8(EnumDayInt8.Slave_BuyCatchTimes) + 1
	if buyTimes > EnumGameConfig.SlaveBuyCatchTimes:
		return
	
	needRMB = SlaveConfig.SlaveBuyCatchTimes_Dict.get(buyTimes)
	if not needRMB:
		return
	
	if role.GetRMB() < needRMB:
		return
	with Tra_Slave_BuyCatchTimes:
		role.DecRMB(needRMB)
		role.IncDI8(EnumDayInt8.Slave_BuyCatchTimes, 1)
		role.DecDI8(EnumDayInt8.Slave_CatchTimes, 1)
	
def BuyBattleTime(role, msg):
	'''
	购买反抗(求救)次数
	@param role:
	@param msg:
	'''
	if not role.GetI1(EnumInt1.SlaveInitFlag) : return
	
	buyTimes = role.GetDI8(EnumDayInt8.Slave_BuyBattleTimes) + 1
	if buyTimes > EnumGameConfig.SlaveBuyBattleTimes:
		return
	
	needRMB = SlaveConfig.SlaveBuyBattleTimes_Dict.get(buyTimes)
	if not needRMB:
		return
	
	if role.GetRMB() < needRMB:
		return
	with Tra_Slave_BuyBattleTimes:
		role.DecRMB(needRMB)
		role.IncDI8(EnumDayInt8.Slave_BuyBattleTimes, 1)
		role.DecDI8(EnumDayInt8.Slave_BattleTimes, 1)

def BuySaveTime(role, msg):
	'''
	购买解救次数
	@param role:
	@param msg:
	'''
	if not role.GetI1(EnumInt1.SlaveInitFlag) : return
	
	buyTimes = role.GetDI8(EnumDayInt8.Slave_BuySaveTimes) + 1
	if buyTimes > EnumGameConfig.SlaveBuySaveTimes:
		return
	
	needRMB = SlaveConfig.SlaveBuySaveTimes_Dict.get(buyTimes)
	if not needRMB:
		return
	
	if role.GetRMB() < needRMB:
		return
	with Tra_Slave_BuySaveTimes:
		role.DecRMB(needRMB)
		role.IncDI8(EnumDayInt8.Slave_BuySaveTimes, 1)
		role.DecDI8(EnumDayInt8.Slave_SaveTimes, 1)

def CatchSlave(role, msg):
	'''
	抓捕一个奴隶
	@param role:
	@param msg:
	'''
	slaveId = msg
	if not slaveId : return
	roleId = role.GetRoleID()
	if roleId == slaveId : return
	
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		#不可以进入战斗状态
		return
	
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole : return
	
	if not sRole.CanCatch(role):
		return
	
	if role.GetDI8(EnumDayInt8.Slave_CatchTimes) >= EnumGameConfig.SlaveCatchTimes:
		#没次数了
		return
	
	beCatchOne = SlaveRole_Dict.get(slaveId)
	if not beCatchOne:
		return
	nowSec = cDateTime.Seconds()
	if beCatchOne.playCDTimes > nowSec:
		#奴隶正在互动CD中
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_2)
		return
	if abs(role.GetLevel() - beCatchOne.roleLevel) > EnumGameConfig.SlaveFightNeedLevel:
		#只能抓捕10级以内的玩家
		return
	
	if beCatchOne.slave_role_dict:
		#抓捕的是领主，选者一个不在CD时间的奴隶
		beCatchOne_Slave = None
		for besr in beCatchOne.slave_role_dict.itervalues():
			if besr.playCDTimes < nowSec:
				beCatchOne_Slave = besr
				break
		if beCatchOne_Slave is None:
			#全部奴隶都在互动CD中
			role.Msg(2, 0, GlobalPrompt.Slave_Tips_2)
			return
			
	
	mansterId = beCatchOne.mansterId
	fightData = None
	if mansterId:
		fightData = RoleFightData.GetRoleFightData(mansterId)
	else:
		fightData = RoleFightData.GetRoleFightData(slaveId)
	if not fightData:
		#没有战斗数据
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_3)
		#print "GE_EXC, error in catch slave not fightdata"
		#清理这个奴隶
		sRole.DelLoserOrEnemy(slaveId)
		return
	#扣除次数
	role.IncDI8(EnumDayInt8.Slave_CatchTimes, 1)
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.CatchSlave()
	#进入战斗
	PVP_Slave(role, fightData, EnumGameConfig.SlaveFightType_1, (sRole, beCatchOne, mansterId), None, AfterPlayInFightSlave)


def AfterPlayInFightSlave(fightObj):
	#战斗回调
	sRole, beCatchOne, mansterId = fightObj.after_fight_param
	if fightObj.result != 1:
		sRole.CatchLose(beCatchOne)
		return
	
	if not sRole.CanCatch() or beCatchOne.mansterId != mansterId:
		#前后状态不一致
		return

	sRole.CatchSlave(beCatchOne)
	
def ReleaseSlave(role, msg):
	'''
	释放一个奴隶
	@param role:
	@param msg:
	'''
	slaveId = msg
	if not slaveId:
		return
	roleId = role.GetRoleID()
	if roleId == slaveId:
		return
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	sRole.ReleaseSlave(role, slaveId)

def SaveSlave(role, msg):
	'''
	解救一个奴隶
	@param role:
	@param msg:
	'''
	slaveId = msg
	roleId = role.GetRoleID()
	if roleId == slaveId:
		return
	unionId = role.GetUnionID()
	if not unionId:
		#没有公会，不能解救
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	if sRole.statue == Slave_Slave:
		#自己都是奴隶，不能解救别人
		return
	
	if role.GetDI8(EnumDayInt8.Slave_SaveTimes) >= EnumGameConfig.SlaveSaveTimes:
		#没有次数了
		return
	
	beCatchOne = SlaveRole_Dict.get(slaveId)
	if not beCatchOne:
		return
	
	if beCatchOne.statue != Slave_Slave:
		#对方不是奴隶
		return
	
	if beCatchOne.playCDTimes > cDateTime.Seconds():
		#奴隶正在互动CD中
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_2)
		return
	
	if beCatchOne.mansterId == roleId:
		#不能解救自己的奴隶
		return
	if beCatchOne.unionId != unionId:
		#不是同公会的不能解救
		return
	if abs(role.GetLevel() - beCatchOne.roleLevel) > EnumGameConfig.SlaveFightNeedLevel:
		#只能解救10级以内的玩家
		return
	mansterFightData = RoleFightData.GetRoleFightData(beCatchOne.mansterId)
	if not mansterFightData:
		#没有战斗数据
		#TODO
		return
	#扣除一个拯救次数
	role.IncDI8(EnumDayInt8.Slave_SaveTimes, 1)
	if Environment.EnvIsNA():
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.SaveSlave()
	PVP_Slave(role, mansterFightData, EnumGameConfig.SlaveFightType_1, (sRole, beCatchOne, beCatchOne.mansterId), None, AfterPlaySave, None)


def AfterPlaySave(fightObj):
	sRole, beCatchOne, mansterId = fightObj.after_fight_param
	if fightObj.result != 1:
		manster = SlaveRole_Dict.get(mansterId)
		if manster:
			sRole.AddLog(SlaveDefine.Log_9, (manster.roleName, beCatchOne.roleName))
			manster.AddLog(SlaveDefine.Log_11,(sRole.roleName, beCatchOne.roleName))
		return
	
	if beCatchOne.mansterId != mansterId:
		#前后状态不一致了
		return
	beCatchOne.BeSave(sRole)

def BattleManster(role, msg):
	'''
	奴隶反抗主人
	@param role:
	@param msg:
	'''
	roleId = role.GetRoleID()
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	if sRole.statue != Slave_Slave:
		#自己不是奴隶
		return

	if sRole.playCDTimes > cDateTime.Seconds():
		#正在互动CD中
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_1)
		return
	
	if role.GetDI8(EnumDayInt8.Slave_BattleTimes) >= EnumGameConfig.SlaveBattleTimes:
		return
	
	mansterId = sRole.mansterId
	mansterRole = SlaveRole_Dict.get(mansterId)
	if not mansterRole:
		return
	mansterFightData = RoleFightData.GetRoleFightData(mansterId)
	if not mansterFightData:
		#没有战斗数据
		#TODO
		return
	role.IncDI8(EnumDayInt8.Slave_BattleTimes, 1)
	PVP_Slave(role, mansterFightData, EnumGameConfig.SlaveFightType_1, (sRole, mansterRole), None, AfterPlayBattle, None)


def AfterPlayBattle(fightObj):
	sRole, mansterRole = fightObj.after_fight_param
	if fightObj.result != 1:
		sRole.AddLog(SlaveDefine.Log_18, (mansterRole.roleName, ))
		mansterRole.AddLog(SlaveDefine.Log_20, (sRole.roleName, ))
		return
	
	if sRole.mansterId != mansterRole.roleId:
		return
	sRole.BattleWin(mansterRole)

def SayHelp(role, msg):
	'''
	奴隶求救
	@param role:
	@param msg:
	'''
	helperId = msg
	roleId = role.GetRoleID()
	if helperId == roleId:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	unionId = role.GetUnionID()
	if not unionId:
		#没有公会，不能求助
		return
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	if sRole.statue != Slave_Slave:
		#自己不是奴隶
		return
	if sRole.playCDTimes > cDateTime.Seconds():
		#正在互动CD中
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_1)
		return
	if role.GetDI8(EnumDayInt8.Slave_BattleTimes) >= EnumGameConfig.SlaveBattleTimes:
		return
	helperRole = SlaveRole_Dict.get(helperId)
	if not helperRole:
		return
	
	if helperRole.statue == Slave_Slave:
		#对方也是奴隶
		return
	
	if unionId != helperRole.unionId:
		#不是同一个公会的
		return
	if abs(role.GetLevel() - helperRole.roleLevel) > EnumGameConfig.SlaveFightNeedLevel:
		#只能求救10级以内的玩家
		return
	
	mansterId = sRole.mansterId
	mansterRole = SlaveRole_Dict.get(mansterId)
	if not mansterRole:
		return
	
	mansterFightData = RoleFightData.GetRoleFightData(mansterId)
	if not mansterFightData:
		#没有战斗数据
		#TODO
		return
	
	helperRoleFightData = RoleFightData.GetRoleFightData(helperId)
	if not helperRoleFightData:
		#没有战斗数据
		#TODO
		return
	
	role.IncDI8(EnumDayInt8.Slave_BattleTimes, 1)
	PVP_Help(role, helperRoleFightData, mansterFightData, EnumGameConfig.SlaveFightType_2, (sRole, mansterRole, helperRole), None, AfterPlayHelp, None)


def AfterPlayHelp(fightObj):
	sRole, mansterRole, helperRole = fightObj.after_fight_param
	if fightObj.result != 1:
		sRole.AddLog(SlaveDefine.Log_21, (helperRole.roleName, ))
		mansterRole.AddLog(SlaveDefine.Log_23, (helperRole.roleName, sRole.roleName))
		return
	
	if sRole.mansterId != mansterRole.roleId:
		#已经不是这个主人了
		return
	sRole.BeHelp(mansterRole, helperRole)

def SlavePlay(role, msg):
	'''
	奴隶互动
	@param role:
	@param msg:
	'''
	backId, (playRoleId, playType) = msg
	if not playRoleId :
		return
	if playType < 1 or playType > 12:
		return
	roleId = role.GetRoleID()
	if roleId == playRoleId:
		return
	#在蓝钻渠道登录的用户QQ蓝钻特权互动次数可以+1
	QQLZBufcnt = 0
	addCnt = 0
	if QQLZShopMgr.IsQQLZ(role):
		QQLZBufcnt = EnumGameConfig.QQLZSlaveBuff
		addCnt = role.GetDI8(EnumDayInt8.QQLZBuffSlave)#蓝钻渠道蓝钻特权已经互动次数
	if role.GetDI8(EnumDayInt8.Slave_PlayTimes) + addCnt >= EnumGameConfig.SlavePlayTimes + QQLZBufcnt:
		#没次数了
		return
	
	
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	sec = sRole.Play(role, playRoleId, playType)
	if sec:
		role.CallBackFunction(backId, (playRoleId, sec))
		
		#每日必做 -- 奴隶互动
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_Slave, 1))
		
	#版本判断
	if Environment.EnvIsNA():
		#北美万圣节
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.slave_play()
	elif Environment.EnvIsRU():
		#七日活动
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		sevenActMgr.slave_play()
		
def GetSlaveExp(role, msg):
	'''
	提取奴隶的经验
	@param role:
	@param msg:
	'''
	backId, slaveId = msg
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole:
		return
	if sRole.DayExpIsFull():
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_6)
		return
	
	slaveRole = SlaveRole_Dict.get(slaveId)
	if not slaveRole:
		return
	sd = sRole.GetSlaveDictData(slaveId)
	if not sd:
		return
	with Tra_GetSlaveExp:
		exp = sRole.GetSlaveExp(slaveId)
		if not exp:
			return
		sRole.IncExp(role, exp)
		role.CallBackFunction(backId, (sd[S_STARTWORKTIME], sd[S_ENDWORKTIME]))
	

def GetOnHourExp(role, msg):
	'''
	压榨一个奴隶一个小时的经验
	@param role:
	@param msg:
	'''
	backId, slaveId = msg
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole : return
	
	if sRole.DayExpIsFull() :
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_6)
		return
	
	slaveRole = SlaveRole_Dict.get(slaveId)
	if not slaveRole : return
	
	sd = sRole.GetSlaveDictData(slaveId)
	if not sd : return
	
	startTime = sd[S_STARTWORKTIME]
	endTime = sd[S_ENDWORKTIME]
	nowSec = cDateTime.Seconds()
	if endTime <= startTime or endTime < nowSec:
		#已经不能压榨一个小时了
		return
	if role.GetRMB() < EnumGameConfig.SlaveOnHourNeedRMB:
		return
	with Tra_GetOnHourExp:
		exp = sRole.GetSlaveExpOneHour(role, slaveId)
		if not exp:
			return
		sRole.IncExp(role, exp)
		role.CallBackFunction(backId, (sd[S_STARTWORKTIME], sd[S_ENDWORKTIME]))


def GetExpToDie(role, msg):
	'''
	抽干一个奴隶所有的经验
	@param role:
	@param msg:
	'''
	backId, slaveId = msg
	roleId = role.GetRoleID()
	sRole = SlaveRole_Dict.get(roleId)
	if not sRole : return
	
	if sRole.DayExpIsFull() :
		role.Msg(2, 0, GlobalPrompt.Slave_Tips_6)
		return
	
	slaveRole = SlaveRole_Dict.get(slaveId)
	if not slaveRole : return
	
	sd = sRole.GetSlaveDictData(slaveId)
	if not sd : return
	
	startTime = sd[S_STARTWORKTIME]
	endTime = sd[S_ENDWORKTIME]
	nowSec = cDateTime.Seconds()
	if endTime <= startTime or endTime < nowSec:
		#已经不能抽干了
		return
	if role.GetRMB() < EnumGameConfig.SlaveOnHourNeedRMB:
		return
	with Tra_GetExpToDie:
		exp = sRole.GetExpToDie(role, slaveId)
		if not exp:
			return
		sRole.IncExp(role, exp)
		role.CallBackFunction(backId, (sd[S_STARTWORKTIME], sd[S_ENDWORKTIME]))

######################################################################################
def AfterLoad():
	#载入完毕后
	slavedata = Slave_BT.GetData()
	if not slavedata:
		return
	for roleId, sd in slavedata.iteritems():
		#创建管理对象
		SlaveRole_Dict[roleId] = SlaveRole(roleId, None, sd)
	
	for srole in SlaveRole_Dict.itervalues():
		#更新自己的主人的缓存数据
		srole.UpdataManster()


def UpdataSlaveRole(role, save = False):
	sRole = SlaveRole_Dict.get(role.GetRoleID())
	if not sRole:
		if Slave_BT.returnDB:
			#载回数据了，但是没有这个角色的奴隶数据，重新初始化一次
			InitSlave(role, True)
			return
		print "GE_EXC, error in UpdataSlaveRole not sRole (%s) not returnDB" % role.GetRoleID()
		return
	sRole.UpdataRole(role, save)

def AfterLogin(role, param):
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		#如果等级满足条件则激活系统
		if role.GetLevel() >= EnumGameConfig.SlaveNeedLevel:
			InitSlave(role)
		return
	
	UpdataSlaveRole(role)

def BeforeExit(role, param):
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	sRole = SlaveRole_Dict.get(role.GetRoleID())
	if not sRole:
		print "GE_EXC, error BeforeExit not slave role (%s)" % role.GetRoleID()
		return
	#保存数据
	sRole.SaveData()
	#置空缓存角色
	sRole.role = None
	
def AfterLevelUp(role, param):
	if role.GetLevel() < EnumGameConfig.SlaveNeedLevel:
		return
	if role.GetI1(EnumInt1.SlaveInitFlag):
		# 升级更新数据
		UpdataSlaveRole(role, True)
	else:
		InitSlave(role)

def AfterChangeRoleGrade(role, param):
	#升阶，更新自己的数据
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	UpdataSlaveRole(role, True)


def AfterJoinUnion(role, param):
	#更新自己的数据
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	UpdataSlaveRole(role, True)


def AfterLeaveUnion(role, param):
	#更新自己的数据
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	UpdataSlaveRole(role, True)


def AfterChangeName(role, param):
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	UpdataSlaveRole(role, True)

def AfterChangeSex(role, param):
	if not role.GetI1(EnumInt1.SlaveInitFlag):
		return
	UpdataSlaveRole(role, True)

def AfterChangeUnionName(role, param):
	#公会改名
	unionObj = UnionMgr.UNION_OBJ_DICT.get(param)
	if not unionObj:
		print "GE_EXC error in AfterChangeUnionName not union (%s)" % param
		return
	SG = SlaveRole_Dict.get
	uname = unionObj.name
	for roleId in unionObj.members.iterkeys():
		sr = SG(roleId)
		if not sr:
			continue
		sr.unionName = uname
		sr.SaveData()
		if sr.slave_role_dict:
			for slr in sr.slave_role_dict.itervalues():
				slr.mansterUnionName = uname
				

def AfterNewDay():
	for sRole in SlaveRole_Dict.itervalues():
		#清理每日已经获取的经验
		sRole.dayExp = 0
		sRole.SaveData()

def CallPerHour():
	#每小时检测是否有可以变成自由的奴隶
	for sRole in SlaveRole_Dict.itervalues():
		sRole.CallPerHour()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Slave_BT = BigTable.BigTable("sys_role_slave", 50, AfterLoad)
	
	if Environment.HasLogic and not Environment.IsCross:
		
		cComplexServer.RegAfterNewHourCallFunction(CallPerHour)
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_AfterChangeRoleGrade, AfterChangeRoleGrade)
		
		Event.RegEvent(Event.Eve_AfterJoinUnion, AfterJoinUnion)
		Event.RegEvent(Event.Eve_AfterLeaveUnion, AfterLeaveUnion)
		Event.RegEvent(Event.Eve_AfterChangeName, AfterChangeName)
		Event.RegEvent(Event.Eve_RoleChangeGender, AfterChangeSex)
		
		Event.RegEvent(Event.Eve_AfterChangeUnionName, AfterChangeUnionName)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_RequestMainData", "请求奴隶系统面板数据"), RequestMainData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_RequestPlaySlaveData", "请求主人和奴隶互动的数据"), RequestPlaySlaveData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_RequestSlaveExpData", "请求奴隶工作经验数据"), RequestSlaveExpData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_RequestLoserEnemyData", "请求手下败将和夺奴之敌数据列表"), RequestLoserEnemyData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_RequestHelpList", "请求请求求助数据列表"), RequestHelpList)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_RequestSaveList", "请求可以解救的奴隶数据列表"), RequestSaveList)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_BuyCatchTime", "请求购买抓捕次数"), BuyCatchTime)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_BuyBattleTime", "请求购买反抗(求救)次数"), BuyBattleTime)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_BuySaveTime", "请求购买解救次数"), BuySaveTime)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_CatchSlave", "请求抓捕一个奴隶"), CatchSlave)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_ReleaseSlave", "请求释放一个奴隶"), ReleaseSlave)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_SaveSlave", "请求解救一个奴隶"), SaveSlave)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_BattleManster", "请求奴隶反抗主人"), BattleManster)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_SayHelp", "请求奴隶求救"), SayHelp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_SlavePlay", "请求奴隶互动"), SlavePlay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_GetSlaveExp", "提取奴隶的经验"), GetSlaveExp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_GetOnHourExp", "请求压榨一个奴隶一个小时的经验"), GetOnHourExp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Slave_GetExpToDie", "请求抽干一个奴隶所有的经验"), GetExpToDie)
		
		#发给客户端的消息
		Slave_S_UpdataStatus = AutoMessage.AllotMessage("Slave_S_UpdataStatus", "同步更新自己的身份")
		Slave_S_UpdataSlaveExpData = AutoMessage.AllotMessage("Slave_S_UpdataSlaveExpData", "同步更新今天获取的奴隶经验数据")
		Slave_S_AddLog = AutoMessage.AllotMessage("Slave_S_AddLog", "同步增加一个奴隶日志")
		
		#日志
		Tra_Slave_Play = AutoLog.AutoTransaction("Tra_Slave_Play", "奴隶互动日志")
		Tra_Slave_Mail = AutoLog.AutoTransaction("Tra_Slave_Mail", "奴隶邮件经验")
		Tra_GetSlaveExp = AutoLog.AutoTransaction("Tra_GetSlaveExp", "提取奴隶的经验")
		Tra_GetOnHourExp = AutoLog.AutoTransaction("Tra_GetOnHourExp", "压榨一个奴隶一个小时的经验")
		Tra_GetExpToDie = AutoLog.AutoTransaction("Tra_GetExpToDie", "抽干一个奴隶所有的经验")
		Tra_Slave_BuyCatchTimes = AutoLog.AutoTransaction("Tra_Slave_BuyCatchTimes", "购买抓奴隶次数")
		Tra_Slave_BuyBattleTimes = AutoLog.AutoTransaction("Tra_Slave_BuyBattleTimes", "购买奴隶反抗次数")
		Tra_Slave_BuySaveTimes = AutoLog.AutoTransaction("Tra_Slave_BuySaveTimes", "购买解救奴隶次数")


