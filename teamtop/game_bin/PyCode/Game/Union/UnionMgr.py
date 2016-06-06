#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionMgr")
#===============================================================================
# 公会管理
#===============================================================================
import random
import cComplexServer
import cDateTime
import cRoleDataMgr
import cRoleMgr
import cSceneMgr
import Environment
from Common import CValue
from Common.Message import AutoMessage
from Common.Other import EnumSysData, GlobalPrompt,EnumSocial, EnumAppearance,\
	EnumGameConfig
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from ComplexServer.Plug import Switch
from Game.Activity.SevenDayHegemony import SDHFunGather, SDHDefine
from Game.Persistence import BigTable
from Game.RoleFightData import RoleFightData
from Game.Role import Event, Call
from ComplexServer.Time import Cron
from Game.Role.Data import EnumTempObj, EnumInt32, EnumInt8, EnumCD, EnumDayInt8,\
	EnumInt1, EnumObj
from Game.Role.Mail import Mail
from Game.Scene import SceneMgr, PublicScene
from Game.SysData import WorldData
from Game.Union import UnionConfig, UnionDefine
from Util import Time

if "_HasLoad" not in dir():
	LastUnionID = None
	MaxUnionID = (Switch.MaxProcessId + 1) * CValue.P2_16
	
	UNION_NEWS_CNT_MAX = 5				#公会广播最大数量
	UNION_NOTICE_LEN_MAX = 300			#公会公告最大长度
	CAMP_NEED_LEVEL = 32				#阵营需求等级
	UnionNewsNeedLevel = 40
	UnionNewsNeedVIP = 2
	
	CHANGE_NAME_ITEM_CODING = 26148		#公会改名卡物品coding
	
	UNION_LEFT_CAMP_LIST = []			#左阵营公会对象列表
	UNION_RIGHT_CAMP_LIST = []			#右阵营公会对象列表
	
	UNION_OBJ_DICT = {}					#公会对象字典
	ROLEID_TO_UNIONID = {}				#角色ID索引公会ID
	UNIONID_TO_APPLY_ROLE_DATA = {}		#公会ID索引申请加入公会的角色数据{unionId -> {roleId: [data]}}
	ROLEID_TO_APPLYING_UNIONID = {}		#角色正在申请的公会列表roleId -> [unionId,...]
	
	UNION_RECRUIT_JOB_ID_LIST = []		#可以招聘成员的职位列表
	
	UNION_ACT_START_HOUR = 20			#公会相关活动开始时间(小时)
	UNION_ACT_END_HOUR = 22				#公会相关活动结束时间(小时)
	
	
	#消息
	Camp_Show_Panel = AutoMessage.AllotMessage("Camp_Show_Panel", "通知客户端显示阵营面板")
	Union_Show_Create_Panel = AutoMessage.AllotMessage("Union_Show_Create_Panel", "通知客户端显示公会创建面板")
	Union_Show_Main_Panel = AutoMessage.AllotMessage("Union_Show_Main_Panel", "通知客户端显示公会主面板")
	Union_Show_Apply_Panel = AutoMessage.AllotMessage("Union_Show_Apply_Panel", "通知客户端显示公会申请管理面板")
	Union_Show_Member_Panel = AutoMessage.AllotMessage("Union_Show_Member_Panel", "通知客户端显示成员面板")
	Union_Show_Other_Union_Panel = AutoMessage.AllotMessage("Union_Show_Other_Union_Panel", "通知客户端显示其他公会面板")
	Union_Show_Union_Name = AutoMessage.AllotMessage("Union_Show_Union_Name", "通知客户端显示公会名字")
	Union_Success_Join_In = AutoMessage.AllotMessage("Union_Success_Join_In", "通知客户端成功加入了公会")
	Union_Change_Name_Success = AutoMessage.AllotMessage("Union_Change_Name_Success", "通知客户端改名成功")
	Union_Exclamatory_Mark = AutoMessage.AllotMessage("Union_Exclamatory_Mark", "通知客户端公会感叹号")
	Union_Member_Panel_Exclamatory_Mark = AutoMessage.AllotMessage("Union_Member_Panel_Exclamatory_Mark", "通知客户端公会成员面板感叹号")
	SyncUnionResource = AutoMessage.AllotMessage("SyncUnionResource", "同步公会资源")
	SyncUnionFBData = AutoMessage.AllotMessage("SyncUnionFBData", "同步公会副本数据")
	UnionHongBaoShowTips = AutoMessage.AllotMessage("UnionHongBaoShowTips", "公会红包是否显示叹号提示")
	
	#日志
	TraChooseCamp = AutoLog.AutoTransaction("TraChooseCamp", "选择阵营")
	TraJoinUnion = AutoLog.AutoTransaction("TraJoinUnion", "加入公会")
	TraQuitUnion = AutoLog.AutoTransaction("TraQuitUnion", "退出公会")
	TraBeKickedUnion = AutoLog.AutoTransaction("TraBeKickedUnion", "被踢出公会")
	TraUnionRMBContribute = AutoLog.AutoTransaction("TraUnionRMBContribute", "公会RMB贡献")
	TraUnionError = AutoLog.AutoTransaction("TraUnionError", "公会异常修复")
	TraUnionChangeName = AutoLog.AutoTransaction("TraUnionChangeName", "公会改名")
	TraClearUnionJoinCD = AutoLog.AutoTransaction("TraClearUnionJoinCD", "清除加入公会CD")
	TraUnionLoginSetContribution = AutoLog.AutoTransaction("TraUnionLoginSetContribution", "公会登录设置个人贡献")
	TraUnionDailyResourceLackDismiss = AutoLog.AutoTransaction("TraUnionDailyResourceLackDismiss", "公会连续每日增加资源不达标自动解散")
	TraUnionDailyResourceLackDismissWarn = AutoLog.AutoTransaction("TraUnionDailyResourceLackDismissWarn", "公会连续每日增加资源不达标自动解散警告")
	TraUnionDailyResourceLackDismissClear = AutoLog.AutoTransaction("TraUnionDailyResourceLackDismissClear", "公会连续每日增加资源不达标自动解散清理玩家公会数据")
	TraUnionHongBaoMail = AutoLog.AutoTransaction("TraUnionHongBaoMail", "公会红包未领完神石返回邮件")

def AllotUnionID():
	global LastUnionID
	assert LastUnionID is not None
	LastUnionID += 1
	assert LastUnionID < MaxUnionID
	global UNION_OBJ_DICT
	if LastUnionID in UNION_OBJ_DICT:
		return AllotUnionID()
	#公会ID已达到一定的数量
	#if MaxUnionID - LastUnionID < 10000:
	#	print "GE_EXC unionId remind (%s) in AllotUnionID" % (MaxUnionID - LastUnionID)
	
	return LastUnionID


def AfterLoad():
	global LastUnionID
	btData = BT.GetData()
	if btData:
		LastUnionID = max(btData.iterkeys())
	else:
		LastUnionID = Switch.MaxProcessId * CValue.P2_16
	
	#载完数据后做处理,维护角色ID对应公会ID字典
	global ROLEID_TO_UNIONID
	global UNION_LEFT_CAMP_LIST
	global UNION_RIGHT_CAMP_LIST
	for unionId, uniondata in btData.iteritems():
		UNION_OBJ_DICT[unionId] = unionObj = Union(uniondata)
	
		#生成阵营列表
		if unionObj.camp_id == 1:
			UNION_LEFT_CAMP_LIST.append(unionObj)
		elif unionObj.camp_id == 2:
			UNION_RIGHT_CAMP_LIST.append(unionObj)
		else:
			print "GE_EXC error camp in union init (%s) (%s)" % (unionId, unionObj.camp_id)
		
		#新增
		for memberId, memberData in unionObj.members.iteritems():
			ROLEID_TO_UNIONID[memberId] = unionId
			#新添加成员战斗力数据
			if UnionDefine.M_ZDL_IDX not in memberData:
				memberData[UnionDefine.M_ZDL_IDX] = 0
			#新添加成员历史贡献
			if UnionDefine.M_H_CONTRIBUTION_IDX not in memberData:
				memberData[UnionDefine.M_H_CONTRIBUTION_IDX] = memberData[UnionDefine.M_CONTRIBUTION_IDX]
			#新添加公会任务助人次数
			if UnionDefine.M_TASK_HELP_IDX not in memberData:
				memberData[UnionDefine.M_TASK_HELP_IDX] = 0
			
		#公会任务
		if UnionDefine.O_TASK_IDX not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_TASK_IDX] = {}
		if UnionDefine.O_TASK_HELP_OTHER_LIST_IDX not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_TASK_HELP_OTHER_LIST_IDX] = {}
		
		#魔域探秘战俘
		if UnionDefine.O_PRISONER_IDX not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_PRISONER_IDX] = {}
		if UnionDefine.O_PRISONER_RESOURCE_IDX not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX] = {}
			
		#至尊周卡
		if UnionDefine.O_SUPER_CARDS_DAYS_IDX not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX] = {}
		
		#公会每日魔神挑战次数，godid->次数
		if UnionDefine.GOD_FIGHT_IDX not in unionObj.god:
			unionObj.god[UnionDefine.GOD_FIGHT_IDX] = {}
		#公会每日累计充值
		if UnionDefine.O_TotalFillRMB not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_TotalFillRMB] = 0
		#神兽每日喂养次数
		if UnionDefine.O_ShenShowDayFeed not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_ShenShowDayFeed] = 0
			
		if UnionDefine.O_HongBao not in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_HongBao] = {'allHongBao':{}, 'HongBaoId':0, 'recordList':[], 'outDateTime':{}}
		#保存
		unionObj.HasChange()
		
	#创建每个公会的公会驻地场景
	SCPS = cSceneMgr.CreatePublicScene
	#获取注册的场景相关函数
	PSCG = PublicScene.SceneCreateFun.get
	PSJG = PublicScene.SceneJoinFun.get
	PSBG = PublicScene.SceneBeforeLeaveFun.get
	PSRG = PublicScene.SceneRestoreFun.get
	for unionId in btData.iterkeys():
		unionSceneConfig = SceneMgr.SceneConfig_Dict.get(UnionDefine.UNION_STATION_SCENE_ID)
		if unionSceneConfig:
			SID = unionId
			SCPS(SID, unionSceneConfig.SceneName, unionSceneConfig.MapId, unionSceneConfig.AreaSize, unionSceneConfig.IsSaveData, unionSceneConfig.CanSeeOther, PSCG(SID), PSJG(SID), PSBG(SID), PSRG(SID))
	
	
	from Game.Union import UnionMagicTower, UnionShenShou
	for unionId in btData.iterkeys():
		unionObj = GetUnionObjByID(unionId)
		if unionObj is None:
			continue
		UnionShenShou.ShenShouNPCInit(unionObj)
		UnionShenShou.RecountHurtRank(unionObj)
		UnionMagicTower.AfterUnionObjInit(unionObj)

	
class Union(object):
	def __init__(self, datas):
		self.union_id = datas["union_id"]		#公会ID
		self.camp_id = datas["camp_id"]			#阵营ID
		self.name = datas["name"]				#公会名
		self.leader_id = datas["leader_id"]		#会长ID
		self.leader_name = datas["leader_name"]	#会长名
		self.level = datas.get("level", 1)		#公会等级
		self.exp = datas.get("exp", 0)			#公会经验
		self.notice = datas.get("notice", "")	#公告
		self.population = datas.get("population", UnionConfig.UNION_POPULATION_MIN)	#公会最大人口
		self.resource = datas.get("resource", 0)
		self.news = datas.get("news", [])		#公会广播
		#成员
		self.members = datas.get("members", {})
		#选举
		self.election = datas.get("election", { UnionDefine.ELECTION_START_IDX: 0, 
												UnionDefine.ELECTION_JOIN_IDX: [], 
												UnionDefine.ELECTION_ROLE_VOTES_IDX: {}})
		#夺宝
		self.treasure = datas.get("treasure", { UnionDefine.TREASURE_GOLD_IDX: {}, 
												UnionDefine.TREASURE_SILVER_IDX: {}, 
												UnionDefine.TREASURE_COPPER_IDX: {}})
		#魔神
		self.god = datas.get("god", { UnionDefine.GOD_TOP_IDX: (0, 0, "", 0, 0, 0), 
										UnionDefine.GOD_TODAY_PASS_LIST_IDX: [], 
										UnionDefine.GOD_DAYS_IDX: 0,
										UnionDefine.GOD_FIGHT_IDX: {}
										})
		#副本
		self.fb = datas.get("fb", {})
		
		#公会其它数据
		self.other_data = datas.get("other_data", { UnionDefine.O_TASK_IDX: {}, 
													UnionDefine.O_TASK_HELP_OTHER_LIST_IDX: {}, 
													UnionDefine.O_PRISONER_IDX: {}, 
													UnionDefine.O_PRISONER_RESOURCE_IDX: {}, 
													UnionDefine.O_SUPER_CARDS_DAYS_IDX: {},
													UnionDefine.O_TotalFillRMB: 0, 
													UnionDefine.O_ShenShowDayFeed: 0,
													UnionDefine.O_DailyResource:0,
													UnionDefine.O_DailyResourceLackDays:0,
													UnionDefine.O_HongBao:{
																		'allHongBao':{},
																		'HongBaoId':0,
																		'recordList':[],
																		'outDateTime':{}}
													}
								)
		
		self.IsDelete = False
		
	def HasChange(self):
		if self.IsDelete:
			print "GE_EXC,union(%s) has delete but still has change" % self.union_id
			return
		BT.SetValue(self.__dict__)
	
	def HasDelete(self):
		BT.DelKey(self.union_id)
		BT.SaveData()
		self.IsDelete = True
		
	def IncUnionExp(self, incExp):
		if incExp > 0:
			#已升级到最高等级
			if self.level >= UnionConfig.UNION_LEVEL_MAX:
				return
			#获取等级配置
			unionConfig = UnionConfig.UNION_BASE.get(self.level)
			if not unionConfig:
				return
			
			nowExp = self.exp + incExp
			levelUpExp = unionConfig.levelUpNeedExp
			
			#未达到升级条件
			if nowExp < levelUpExp:
				self.exp = nowExp
			
			while nowExp >= levelUpExp:
				nowExp = nowExp - unionConfig.levelUpNeedExp
				self.level += 1		#等级
				self.exp = nowExp	#经验
				
				#获取下一等级配置
				nextLevelUnionConfig = UnionConfig.UNION_BASE.get(self.level)
				if not nextLevelUnionConfig:
					return
				self.population = nextLevelUnionConfig.population	#下一等级的人口
				
				#已升级到最高等级
				if self.level >= UnionConfig.UNION_LEVEL_MAX:
					return
				#获取等级配置
				unionConfig = UnionConfig.UNION_BASE.get(self.level)
				if not unionConfig:
					return
				levelUpExp = unionConfig.levelUpNeedExp
				
	def IncUnionResource(self, incResource):
		if incResource > 0:
			self.resource += incResource
			#增加公会每日增加资源数
			self.other_data[UnionDefine.O_DailyResource] = self.other_data.get(UnionDefine.O_DailyResource, 0) + incResource

		for roleId in self.members.iterkeys():
			the_role = cRoleMgr.FindRoleByRoleID(roleId)
			if the_role is None:
				continue
			the_role.SendObj(SyncUnionResource, self.resource)
			
	def DecUnionResource(self, decRecource):
		if self.resource < decRecource:
			print "GE_EXC, decRecource larger than UnionResource"
			return
		if decRecource > 0:
			self.resource -= decRecource
		for roleId in self.members.iterkeys():
			the_role = cRoleMgr.FindRoleByRoleID(roleId)
			if the_role is None:
				continue
			the_role.SendObj(SyncUnionResource, self.resource)
	
	
	def GetDailyResource(self):
		return self.other_data.get(UnionDefine.O_DailyResource, 0)
		
	def ResetDailyResource(self):
		self.other_data[UnionDefine.O_DailyResource] = 0
	
	def GetResourceLackDays(self):
		return self.other_data.get(UnionDefine.O_DailyResourceLackDays, 0)
	
	def ResetResourceLackDays(self):
		self.other_data[UnionDefine.O_DailyResourceLackDays] = 0
	
	def IncResourceLackDays(self):
		self.other_data[UnionDefine.O_DailyResourceLackDays] = self.other_data.get(UnionDefine.O_DailyResourceLackDays, 0) + 1
		
	def IsMember(self, roleId):
		if roleId in self.members:
			return True
		return False
	
	def IsLeader(self, roleId):
		if roleId == self.leader_id:
			return True
		return False
	
	def NextRoleTask(self):
		for roleId in self.members.iterkeys():
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if not role:
				continue
	
	def NewMember(self, role, jobId):
		roleId = role.GetRoleID()
		if roleId in self.members:
			print "GE_EXC repeat member in UnionId(%s), RoleID(%s)" % (self.union_id, roleId)
			return
		
		self.members[roleId] = {UnionDefine.M_NAME_IDX: role.GetRoleName(), 
								UnionDefine.M_LEVEL_IDX: role.GetLevel(), 
								UnionDefine.M_JOB_IDX: jobId, 
								UnionDefine.M_CONTRIBUTION_IDX: role.GetContribution(), 
								UnionDefine.M_ONLINE_IDX: 1, 
								UnionDefine.M_OFFLINE_TIME_IDX: cDateTime.Seconds(),
								UnionDefine.M_PICTURE_IDX: role.GetPortrait(), 
								UnionDefine.M_VIP_IDX: role.GetVIP(), 
								UnionDefine.M_ZDL_IDX: role.GetZDL(), 
								UnionDefine.M_H_CONTRIBUTION_IDX: role.GetHistoryContribution(), 
								UnionDefine.M_TASK_HELP_IDX: 0}
		
		#保存公会ID
		global ROLEID_TO_UNIONID
		ROLEID_TO_UNIONID[roleId] = self.union_id
		
		#日志
		with TraJoinUnion:
			#设置公会ID
			role.SetUnionID(self.union_id)
		
		#设置职位ID
		role.SetJobID(jobId)
		
		#设置公会中状态
		role.SetI1(EnumInt1.InUnion, 1)
		
		#设置外形
		role.SetApperance(EnumAppearance.App_UnionId, self.union_id)
		
		#设置至尊周卡天数
		cardObj = role.GetObj(EnumObj.SuperCards)
		outDateDays = cardObj.get(1, 0)
		if outDateDays:
			self.SetSuperCardsDays(roleId, outDateDays)
		
		#加入公会后删除此玩家在别的公会的申请信息
		JoinInUnionAndDeleteOtherUnionData(role)
		
		#加入公会事件触发
		Event.TriggerEvent(Event.Eve_AfterJoinUnion, role, self.name)
		
	def DelMember(self, roleId):
		#删除成员
		del self.members[roleId]
		#是否有公会任务,有则删除帮助我的角色的帮助信息，删除公会相关
		if roleId in self.other_data[UnionDefine.O_TASK_IDX]:
			taskDataDict = self.other_data[UnionDefine.O_TASK_IDX][roleId]
			helpMeRoleIdList = taskDataDict[UnionDefine.TASK_HELP_ME_IDX]
			for helpMeRoleId in helpMeRoleIdList:
				if not self.IsMember(helpMeRoleId):
					continue
				helpRoleIdList =  self.other_data[UnionDefine.O_TASK_HELP_OTHER_LIST_IDX].get(helpMeRoleId, [])
				if roleId in helpRoleIdList:
					helpRoleIdList.remove(roleId)
			
			del self.other_data[UnionDefine.O_TASK_IDX][roleId]
			
		if roleId in self.other_data[UnionDefine.O_TASK_HELP_OTHER_LIST_IDX]:
			del self.other_data[UnionDefine.O_TASK_HELP_OTHER_LIST_IDX][roleId]
		
		#删除公会魔域探秘
		if roleId in self.other_data[UnionDefine.O_PRISONER_IDX]:
			del self.other_data[UnionDefine.O_PRISONER_IDX][roleId]
		if roleId in self.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX]:
			del self.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX][roleId]
		
		#删除至尊周卡
		if roleId in self.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX]:
			del self.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX][roleId]
		
	def AddNews(self, news):
		'''
		添加广播
		@param news:
		'''
		self.news.insert(0, news)
		#最多只能保存5条公会广播
		if len(self.news) > UNION_NEWS_CNT_MAX:
			self.news.pop()
		
	def GetJobCnt(self, jobId):
		cnt = 0
		for _, v in self.members.iteritems():
			if jobId == v[UnionDefine.M_JOB_IDX]:
				cnt += 1
		return cnt
	
	def get_member_data(self, roleId, idx):
		return self.members[roleId][idx]
	
	def get_other_data(self, idx):
		return self.other_data[idx]
	
	def GetMemberName(self, roleId):
		return self.members[roleId][UnionDefine.M_NAME_IDX]
	
	def GetMemberJob(self, roleId):
		return self.members[roleId][UnionDefine.M_JOB_IDX]
	
	def SetMemberJob(self, roleId, jobId):
		self.members[roleId][UnionDefine.M_JOB_IDX] = jobId
		
		#如果在线还要设置数组
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if role:
			role.SetJobID(jobId)
			
	def GetMemberContribution(self, roleId):
		return self.members[roleId][UnionDefine.M_CONTRIBUTION_IDX]
	
	def SetMemberContribution(self, roleId, value):
		self.members[roleId][UnionDefine.M_CONTRIBUTION_IDX] = value
		
	def GetMemberHistoryContribution(self, roleId):
		return self.members[roleId][UnionDefine.M_H_CONTRIBUTION_IDX]
	
	def SetMemberHistoryContribution(self, roleId, value):
		self.members[roleId][UnionDefine.M_H_CONTRIBUTION_IDX] = value
		
	def GetZDL(self):
		zdl = 0
		for memberData in self.members.itervalues():
			zdl += memberData.get(UnionDefine.M_ZDL_IDX, 0)
		return zdl
	
	def GetMemberHelpTaskCnt(self, roleId):
		return self.members[roleId][UnionDefine.M_TASK_HELP_IDX]
	
	def IncUnionTaskHelpCnt(self, roleId):
		self.members[roleId][UnionDefine.M_TASK_HELP_IDX] += 1
	
	def GetMaxOccupation(self):
		'''
		返回当前最高占领进度 (章节等级 章节光卡 光卡占领度)
		'''
		maxFBId = 0
		for fbId, _ in self.fb.iteritems():
			if fbId > maxFBId:
				maxFBId = fbId
		
		if not maxFBId:
			return (0, 0, 0)
		
		maxLevel = 0
		maxOccupation = 0
		for level, occupation in self.fb[maxFBId].iteritems():
			if level > maxLevel:
				maxLevel = level
				maxOccupation = occupation
		
		return (maxFBId, maxLevel, maxOccupation) 
	
	def GetPrisonerData(self, roleId):
		if roleId not in self.other_data[UnionDefine.O_PRISONER_IDX]:
			self.other_data[UnionDefine.O_PRISONER_IDX][roleId] = {}
		
		return self.other_data[UnionDefine.O_PRISONER_IDX][roleId]
	
	def GetPrisonerCnt(self, roleId):
		return len(self.other_data[UnionDefine.O_PRISONER_IDX].get(roleId, {}))
	
	def GetAllPrisonerOutputPerHour(self, roleId):
		prisonerDict = self.other_data[UnionDefine.O_PRISONER_IDX].get(roleId, {})
		if not prisonerDict:
			return 0
		
		resourcePerHour = 0
		for prisonerData in prisonerDict.itervalues():
			#统计未过期的战俘产出
			if prisonerData[4] > 0:
				resourcePerHour += prisonerData[3]
			
		return resourcePerHour
	
	def GetPrisonerOutputResource(self, roleId):
		if roleId not in self.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX]:
			self.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX][roleId] = 0
	
		return self.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX][roleId]
	
	def ResetPrisonerOutputResource(self, roleId):
		self.other_data[UnionDefine.O_PRISONER_RESOURCE_IDX][roleId] = 0
		
	def GetSuperCardsDays(self, roleId):
		return self.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX].get(roleId, 0)
		
	def SetSuperCardsDays(self, roleId, days):
		self.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX][roleId] = days
	
	def DelSuperCardsDays(self, roleId):
		if roleId in self.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX]:
			del self.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX][roleId]
			
	##############################################################
	# 公会红包方法
	##############################################################
	def GetOnLineMemberIds(self):
		#获取所有公会在线玩家id列表
		tmpMemberRoleIdList = []
		for memberId, memberDict in self.members.iteritems():
			if memberDict[UnionDefine.M_ONLINE_IDX]:
				tmpMemberRoleIdList.append(memberId)
		return tmpMemberRoleIdList
				
	def CanGetHongBao(self, hongbaoId, roleId):
		if hongbaoId not in self.other_data[UnionDefine.O_HongBao]['allHongBao']:
			return 1
		#角色名，神石列表，玩家名列表, 玩家Id列表,红包是否可领取
		hongBaoList = self.other_data[UnionDefine.O_HongBao]['allHongBao'][hongbaoId]
		if not hongBaoList[-1]:
			return 2
		if roleId in hongBaoList[-2]:
			return 2
		return 0
	
	def GetHongBao(self, hongbaoid, roleId, roleName):
		#领取一个红包
		hongbaoDict = self.other_data[UnionDefine.O_HongBao]
		#角色名，神石列表，玩家名列表, 玩家Id列表,红包是否可领取
		hongBaoList = hongbaoDict['allHongBao'][hongbaoid]
		name, moneyList, roleNameList, roleIdList, flag = hongBaoList 
		
		roleNameList.append(roleName)
		roleIdList.append(roleId)
		#设置不可领取
		roleLen = len(roleIdList)
		if len(moneyList) <= roleLen:
			hongBaoList[-1] = 0
			flag = 0
		RMB = moneyList[roleLen - 1]
		hongbaoDict['recordList'].append((roleName, name, RMB))
		hongbaoDict['recordList'] = hongbaoDict['recordList'][-200:]
		self.HasChange()
		return flag, name, RMB
		
	def SetHongBao(self, roleId, roleName, moneyList, message):
		#发一个红包
		hongbaoDict = self.other_data[UnionDefine.O_HongBao]
		hongbaoid = hongbaoDict['HongBaoId']
		#角色名，神石列表，玩家名列表, 玩家Id列表, 是否可领取
		outDateTime = cDateTime.Seconds() + 24 * 60 * 60
		hongbaoDict['outDateTime'][hongbaoid] = (roleId, outDateTime)
		hongbaoDict['allHongBao'][hongbaoid] = [roleName, moneyList, [], [], 1]
		hongbaoDict['HongBaoId'] = hongbaoid + 1
		hongbaoDict['recordList'].append((roleName, message))
		hongbaoDict['recordList'] = hongbaoDict['recordList'][-200:]
		self.HasChange()
		return hongbaoid
	
	def GetRecordList(self):
		#获取红包发放领取记录的数据
		#发红包数据（玩家角色名，祝福语）
		#领红包数据（领红包角色名，发红包角色名，神石数）
		return self.other_data[UnionDefine.O_HongBao]['recordList']
	
	def HongBaoshowTips(self, roleId):
		#hongbaoList = 角色名，神石列表，玩家名列表, 玩家Id列表,红包是否可领取
		for hongbaoList in self.other_data[UnionDefine.O_HongBao]['allHongBao'].itervalues():
			if len(hongbaoList[1]) > len(hongbaoList[3]) and roleId not in hongbaoList[3]:
				return True
		return False
	
	
	def GetHongBaoDetail(self, hongbaoId, roleId):
		#获取红包明细，返回(角色名，红包金额，红包金额，领红包玩家名)
		#角色名，神石列表，玩家名列表, 玩家Id列表, 红包是否可领取
		honbaoDetail = self.other_data[UnionDefine.O_HongBao]['allHongBao'].get(hongbaoId, None)
		if not honbaoDetail:
			return []
		name, moneyList, roleNameList, roleIdList, _ = honbaoDetail 
		RMB = 0
		if roleId in roleIdList:
			RMB = moneyList[roleIdList.index(roleId)]
		return (name, RMB, moneyList[0:len(roleNameList)], roleNameList, len(moneyList))
	
	
	def GetAllHongBao(self, roleId):
		#获取所有红包信息
		#角色名，神石列表，玩家名列表, 玩家Id列表,是否可领取
		allHongbaoList = []
		for hongbaoId, hongbaoList in self.other_data[UnionDefine.O_HongBao]['allHongBao'].iteritems():
			#角色名，神石列表，玩家名列表, 玩家Id列表, 是否可领取 = hongbaoList
			flag = hongbaoList[4]
			if roleId in hongbaoList[3]:
				flag = 0
			allHongbaoList.append((hongbaoId, hongbaoList[0], flag))
		return allHongbaoList
	
	def OverHongBao(self, delAll=False):
		#删除超时红包
		nowTimes = cDateTime.Seconds()
		idSet = set()
		hongbaoDict = self.other_data[UnionDefine.O_HongBao]
		for hongbaoId, (roleId, times) in hongbaoDict['outDateTime'].items():
			if not delAll and nowTimes < times:
				continue
			#角色名，神石列表，玩家名列表, 玩家Id列表,是否可领取
			if hongbaoId not in hongbaoDict['allHongBao']:
				continue
			_, RMBList, _, roleIdList, flag = hongbaoDict['allHongBao'][hongbaoId]
			returnMoney = 0
			if flag:
				returnMoney += sum(RMBList[len(roleIdList):])
			del hongbaoDict['allHongBao'][hongbaoId]
			del hongbaoDict['outDateTime'][hongbaoId]
			if not returnMoney:
				continue
			idSet.add(hongbaoId)
			with TraUnionHongBaoMail:
				#发邮件
				AutoLog.LogBase(roleId, AutoLog.eveReturnUnionHongBao, (returnMoney, self.union_id, hongbaoId))
				Mail.SendMail(roleId, GlobalPrompt.UnionHongBaoTitle, GlobalPrompt.Sender, GlobalPrompt.UnionHongBaoCotent, unbindrmb=returnMoney)
	
	
def GetUnionObjByID(unionId):
	return UNION_OBJ_DICT.get(unionId, None)


def IsUnionExclamatoryMark(unionObj):
	'''
	是否出现公会感叹号
	@param role:
	'''
	global UNION_RECRUIT_JOB_ID_LIST
	if not UNION_RECRUIT_JOB_ID_LIST:
		for jobId, jobConfig in UnionConfig.UNION_JOB.iteritems():
			if jobConfig.recruit:
				UNION_RECRUIT_JOB_ID_LIST.append(jobId)
	
	#是否有人申请加入公会
	isRecruit = True
	if unionObj.union_id not in UNIONID_TO_APPLY_ROLE_DATA or not UNIONID_TO_APPLY_ROLE_DATA[unionObj.union_id]:
		isRecruit = False
		
	for memberId, memberData in unionObj.members.iteritems():
		member = cRoleMgr.FindRoleByRoleID(memberId)
		if not member:
			continue
		
		isNeed = False
		
		if isRecruit is True:
			if memberData[UnionDefine.M_JOB_IDX] in UNION_RECRUIT_JOB_ID_LIST:
				isNeed = True
				#通知客户端有成员申请
				member.SendObj(Union_Member_Panel_Exclamatory_Mark, None)
		
		for treasureDict in unionObj.treasure.itervalues():
			#是否有夺宝
			if not treasureDict:
				continue
			for data in treasureDict.itervalues():
				if memberId not in data[2]:
					isNeed = True
		
		if isNeed is True:
			#通知客户端
			member.SendObj(Union_Exclamatory_Mark, None)
			
def IsRoleExclamatoryMark(role):
	'''
	是否出现公会感叹号
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	global UNION_RECRUIT_JOB_ID_LIST
	if not UNION_RECRUIT_JOB_ID_LIST:
		for jobId, jobConfig in UnionConfig.UNION_JOB.iteritems():
			if jobConfig.recruit:
				UNION_RECRUIT_JOB_ID_LIST.append(jobId)
	
	#是否有人申请加入公会
	isRecruit = True
	if unionObj.union_id not in UNIONID_TO_APPLY_ROLE_DATA or not UNIONID_TO_APPLY_ROLE_DATA[unionObj.union_id]:
		isRecruit = False
		
	isNeed = False
	if isRecruit is True:
		if role.GetJobID() in UNION_RECRUIT_JOB_ID_LIST:
			isNeed = True
			#通知客户端有成员申请
			role.SendObj(Union_Member_Panel_Exclamatory_Mark, None)
	
	roleId = role.GetRoleID()
	for treasureDict in unionObj.treasure.itervalues():
		#是否有夺宝
		if not treasureDict:
			continue
		for data in treasureDict.itervalues():
			if roleId not in data[2]:
				isNeed = True
	#红包叹号
	if unionObj.HongBaoshowTips(role.GetRoleID()):
		role.SendObj(UnionHongBaoShowTips, True)
	
	if isNeed is True:
		#通知客户端
		role.SendObj(Union_Exclamatory_Mark, None)
		
def ShowUnionName(role):
	unionObj = role.GetUnionObj()
	name = ""
	if unionObj:
		name = unionObj.name
	
	role.SendObj(Union_Show_Union_Name, name)
			
def ApplyJoinUnion(role, unionId):
	'''
	申请加入公会
	@param role:
	@param unionId:
	'''
	#自己是否已经有了公会
	if role.GetUnionID():
		return
	
	unionObj = GetUnionObjByID(unionId)
	if not unionObj:
		return
	
	#北美版
	if Environment.EnvIsNA():
		if role.GetCD(EnumCD.UnionJoinCD):
			return
	
	#阵营ID是否相同
	if role.GetCampID() != unionObj.camp_id:
		return
	
	roleId = role.GetRoleID()
	#是否已经申请过对应公会
	if roleId in ROLEID_TO_APPLYING_UNIONID:
		if unionId in ROLEID_TO_APPLYING_UNIONID[roleId]:
			return
	
	#是否超过公会人数上限
	if len(unionObj.members) >= unionObj.population:
		return
	
	#保存申请信息
	SaveApplyData(role, unionId)
	
	#是否出现感叹号
	IsUnionExclamatoryMark(unionObj)
	
def CancelJoinUnion(role, unionId):
	'''
	撤销加入公会
	@param role:
	@param unionId:
	'''
	roleId = role.GetRoleID()
	#是否有申请加入的公会
	if roleId not in ROLEID_TO_APPLYING_UNIONID:
		return
	
	unionIdList = ROLEID_TO_APPLYING_UNIONID[roleId]
	if unionId in unionIdList:
		unionIdList.remove(unionId)
	
	#判断玩家是否在线,不在线则删除申请公会数据
	DelApplyUnionData(unionId, roleId)
	
def SaveApplyData(role, unionId):
	'''
	保存申请加入公会相关的信息
	@param role:
	@param unionId:
	'''
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	level = role.GetLevel()
	vip = role.GetVIP()
	seconds = cDateTime.Seconds()
	zdl = role.GetZDL()
	
	global UNIONID_TO_APPLY_ROLE_DATA
	global ROLEID_TO_APPLYING_UNIONID
	#缓存申请加入公会相关的信息(roleId，名字，等级，vip，时间，战斗力)
	if unionId not in UNIONID_TO_APPLY_ROLE_DATA:
		UNIONID_TO_APPLY_ROLE_DATA[unionId] = {roleId: [roleId, roleName, level, vip, seconds, zdl]}
	else:
		if roleId not in UNIONID_TO_APPLY_ROLE_DATA[unionId]:
			UNIONID_TO_APPLY_ROLE_DATA[unionId][roleId] = [roleId, roleName, level, vip, seconds, zdl]
			
	if roleId not in ROLEID_TO_APPLYING_UNIONID:
		ROLEID_TO_APPLYING_UNIONID[roleId] = [unionId, ]
	else:
		ROLEID_TO_APPLYING_UNIONID[roleId].append(unionId)
		
def CanJoinUnion(role, wantedRole):
	#获取公会对象
	unionId = role.GetUnionID()
	if not unionId:
		return False
	unionObj = GetUnionObjByID(unionId)
	if not unionObj:
		return False
	
	wantedRoleId = wantedRole.GetRoleID()
	
	#目标玩家阵营ID是否和公会相同
	if wantedRole.GetCampID() != unionObj.camp_id:
		return False
	
	#申请的玩家是否已经有公会
	if wantedRole.GetUnionID():
		#删除申请公会数据
		DelApplyUnionData(unionId, wantedRoleId)
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_HAS_JOIN_IN_UNION)
		return False
	
	#目标玩家是否有申请加入公会
	if wantedRoleId not in ROLEID_TO_APPLYING_UNIONID:
		#删除申请公会数据
		DelApplyUnionData(unionId, wantedRoleId)
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_APPLY_ERROR)
		return False
	else:
		#是否申请过此公会
		applyUnionIdList = ROLEID_TO_APPLYING_UNIONID[wantedRoleId]
		if unionId not in applyUnionIdList:
			#删除申请公会数据
			DelApplyUnionData(unionId, wantedRoleId)
			return False
	
	#公会人数上限
	if len(unionObj.members) >= unionObj.population:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_MEMBER_FULL)
		return False
	
	#是否已经是成员
	if unionObj.IsMember(wantedRoleId):
		#删除申请公会数据
		DelApplyUnionData(unionId, wantedRoleId)
		return False
	
	#判断是否有权限
	roleJobId = unionObj.GetMemberJob(role.GetRoleID())
	roleJobConfig = UnionConfig.UNION_JOB.get(roleJobId)
	if not roleJobConfig:
		return False
	if not roleJobConfig.recruit:
		return False
	
	return True
		
def AgreeJoinUnion(role, wantedRoleId):
	'''
	同意加入公会
	@param role: 审核的role
	@param wantedRoleId: 申请人
	'''
	#获取公会对象
	unionId = role.GetUnionID()
	if not unionId:
		return
	unionObj = GetUnionObjByID(unionId)
	if not unionObj:
		return
	
	wantedRole = cRoleMgr.FindRoleByRoleID(wantedRoleId)
	if not wantedRole:
		#判断玩家是否在线,不在线则删除申请公会数据
		DelApplyUnionData(unionId, wantedRoleId)
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_ROLE_OFFLINE)
		return
	
	#成功加入
	if CanJoinUnion(role, wantedRole) is True:
		#加入
		unionObj.NewMember(wantedRole, UnionDefine.MEMBER_JOB_ID)
		#保存
		unionObj.HasChange()
		#通知客户端
		wantedRole.SendObj(Union_Success_Join_In, None)
		wantedRole.GetPropertyMgr().ResetGlobalUnionSkillProperty()
		#公会频道
		UnionMsg(unionObj, GlobalPrompt.UNION_JOIN_WELCOME_MSG % wantedRole.GetRoleName())
	
	#刷新一下申请面板
	ShowApplyPanel(role)
	
	if SDHFunGather.StartFlag[SDHDefine.UnionFB]:
		wantedRole.SendObj(SyncUnionFBData, unionObj.fb)
	
	
def RejectJoinUnion(role, wantedRoleId):
	'''
	拒绝加入公会
	@param role: 审核的role
	@param wantedRoleId: 申请人
	'''
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	unionObj = GetUnionObjByID(unionId)
	if not unionObj:
		return
	
	#删除申请公会数据
	DelApplyUnionData(unionId, wantedRoleId)
	
	#刷新一下申请面板
	ShowApplyPanel(role)
	
def RMBContribute(role, rmb):
	'''
	RMB贡献
	@param role:
	@param rmb: 贡献的RMB
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if role.GetUnbindRMB() < rmb:
		return
	role.DecUnbindRMB(rmb)
	
	addUnionResource = rmb * EnumGameConfig.Union_Per_RMB_To_Union_Resource
	addContribution = rmb * EnumGameConfig.Union_Per_RMB_To_Member_Contribution
	#增加公会资源
	unionObj.IncUnionResource(addUnionResource)
	#增加贡献度
	role.IncContribution(addContribution)
	
	roleName = role.GetRoleName()
	#公会广播
	unionObj.AddNews(GlobalPrompt.UNION_DONATE_MSG % (roleName, rmb, addUnionResource, addContribution))
	
	#保存
	unionObj.HasChange()
	
	#提示
	role.Msg(2, 0, GlobalPrompt.UNION_DONATE_MSG % (roleName, rmb, addUnionResource, addContribution))
	#公会频道
	UnionMsg(unionObj, GlobalPrompt.UNION_DONATE_MSG % (roleName, rmb, addUnionResource, addContribution))
	
	#刷新主面板
	ShowMainPanel(role)
	
def DelApplyUnionData(unionId, roleId):
	#删除申请公会数据
	global UNIONID_TO_APPLY_ROLE_DATA
	global ROLEID_TO_APPLYING_UNIONID
	
	#删除UNIONID_TO_APPLY_ROLE_DATA
	applyDict = UNIONID_TO_APPLY_ROLE_DATA.get(unionId)
	if applyDict:
		if roleId in applyDict:
			del applyDict[roleId]
	
	#删除ROLEID_TO_APPLYING_UNIONID
	if roleId in ROLEID_TO_APPLYING_UNIONID:
		unionList = ROLEID_TO_APPLYING_UNIONID[roleId]
		if unionId in unionList:
			unionList.remove(unionId)
	
def KickOutMember(role, desRoleId):
	#添加时间限制
	hour = cDateTime.Hour()
	if hour >= UNION_ACT_START_HOUR and hour < UNION_ACT_END_HOUR:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_ACT_CANT_QUIT)
		return
	
	roleId = role.GetRoleID()
	
	#不能把自己T了
	if roleId == desRoleId:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否本公会的人
	if not unionObj.IsMember(desRoleId):
		return
	
	#判断是否有权限
	roleJobId = unionObj.GetMemberJob(roleId)
	roleJobConfig = UnionConfig.UNION_JOB.get(roleJobId)
	if not roleJobConfig:
		return
	if not roleJobConfig.kickOut:
		return
	
	#只能T掉职位等级比自己低的
	desRoleJobId = unionObj.GetMemberJob(desRoleId)
	if desRoleJobId <= roleJobId:
		return
	
	#删除成员
	unionObj.DelMember(desRoleId)
	
	#保存
	unionObj.HasChange()
	
	#离线命令
	Call.LocalDBCall(desRoleId, BeKicked, None)
	#提出后干掉其公会技能
	desRole = cRoleMgr.FindRoleByRoleID(desRoleId)
	if desRole:
		desRole.GetPropertyMgr().ResetGlobalUnionSkillProperty()
	
	#通知客户端更新成员面板
	ShowMemberPanel(role)
	#干掉七日争霸活动的数据
	if SDHFunGather.StartFlag[SDHDefine.UnionFB]:
		if desRole:
			desRole.SendObj(SyncUnionFBData, {})
	
def BeKicked(role, param):
	#日志
	with TraBeKickedUnion:
		#清理角色公会数据
		ClearRoleUnionData(role)
		#离开公会事件触发
		Event.TriggerEvent(Event.Eve_AfterLeaveUnion, role, None)
	
def QuitUnion(role):
	#添加时间限制
	hour = cDateTime.Hour()
	if hour >= UNION_ACT_START_HOUR and hour < UNION_ACT_END_HOUR:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_ACT_CANT_QUIT)
		return
	
	roleId = role.GetRoleID()
	
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	unionObj = GetUnionObjByID(unionId)
	if not unionObj:
		return
	
	if not unionObj.IsMember(roleId):
		return
	
	memberCnt = len(unionObj.members)
	#当公会人数超过1时，团长不能退出公会
	if unionObj.IsLeader(roleId) and memberCnt > 1:
		return
	
	#北美版
	if Environment.EnvIsNA():
		role.SetCD(EnumCD.UnionJoinCD, 24 * 60 * 60)#24小时CD
	role.SetCD(EnumCD.UnionDukeCD, 24 * 60 * 60)
	#公会只剩下团长， 如果团长退出公会则公会解散
	if memberCnt == 1:
		if unionObj.IsLeader(roleId):
			#删除所有公会红包并返回未领完红包
			unionObj.OverHongBao(delAll=True)
			#删除阵营中的公会
			DelUnionInCamp(unionObj)
			#删除公会
			unionObj.HasDelete()
			#清理角色公会数据
			ClearRoleUnionData(role)
			
			#删除缓存的公会对象
			global UNION_OBJ_DICT
			if unionId in UNION_OBJ_DICT:
				del UNION_OBJ_DICT[unionId]
			
			#解散公会触发离开混乱时空
			Event.TriggerEvent(Event.Eve_DelUnion, role, unionId)
			role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
			
			return
	
	#删除成员
	unionObj.DelMember(roleId)
	
	#清理角色公会数据
	ClearRoleUnionData(role)
	
	#保存
	unionObj.HasChange()
	
	#离开公会事件触发
	Event.TriggerEvent(Event.Eve_AfterLeaveUnion, role, unionId)
	role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
	
	if SDHFunGather.StartFlag[SDHDefine.UnionFB]:
		role.SendObj(SyncUnionFBData, {})
	
	
def DelUnionInCamp(unionObj):
	'''
	删除阵营中的公会
	@param unionObj:
	'''
	global UNION_LEFT_CAMP_LIST
	global UNION_RIGHT_CAMP_LIST
	
	#公会对象加入阵营公会列表中
	if unionObj.camp_id == 1:
		UNION_LEFT_CAMP_LIST.remove(unionObj)
	elif unionObj.camp_id == 2:
		UNION_RIGHT_CAMP_LIST.remove(unionObj)
	else:
		pass
	
def ClearRoleUnionData(role):
	#重置公会ID
	role.SetUnionID(0)
	#重置公会职位
	role.SetJobID(0)
	#重置公会中状态
	role.SetI1(EnumInt1.InUnion, 0)
	#重置城主相关buff
	role.SetI8(EnumInt8.EarningExpBuff, 0)	#城主收益buff(经验加成)
	role.SetI8(EnumInt8.EarningGoldBuff, 0)	#城主收益buff(金钱加成)
	role.SetChatInfo(EnumSocial.RoleDukeKey, 0)
	#清除角色ID对应公会ID
	global ROLEID_TO_UNIONID
	roleId = role.GetRoleID()
	if roleId in ROLEID_TO_UNIONID:
		del ROLEID_TO_UNIONID[roleId]
	
def EditUnionNotice(role, notice):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	unionObj.notice = notice
	
	unionObj.HasChange()
	
	ShowMainPanel(role)

def GetZDLRank(role,up_to_zdl_rank,limit_level = 0):
	'''
	获取战斗力
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return None

	memberList = []
	role_id = role.GetRoleID()
	for memberId, memberDict in unionObj.members.iteritems():
		if role_id == memberId:
			continue
		if limit_level and memberDict[UnionDefine.M_LEVEL_IDX] < limit_level:
			continue
		#没有战斗数据
		if not RoleFightData.GetRoleFightData(memberId):
			continue

		memberList.append([memberId, 
		memberDict[UnionDefine.M_NAME_IDX], 
		memberDict[UnionDefine.M_LEVEL_IDX], 
		memberDict[UnionDefine.M_ZDL_IDX]])

	memberList.sort(key = lambda x : x[3],reverse = True)
	memberList = memberList[:up_to_zdl_rank]

	return memberList

def ShowMemberPanel(role):
	'''
	显示成员面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	memberList = []
	seconds = cDateTime.Seconds()
	for memberId, memberDict in unionObj.members.iteritems():
		online = memberDict[UnionDefine.M_ONLINE_IDX]
		offLineTimeStr = ""
		#是否在线
		if not online:
			#若不在线，生成最后在线时间字符串
			offLineTimeStr = Time.DifToString2(seconds - memberDict[UnionDefine.M_OFFLINE_TIME_IDX])
		
		#在线，vip，roleId，名字，等级，职位，贡献，最后在线时间字符串，战斗力
		memberList.append([online, 
							memberDict[UnionDefine.M_VIP_IDX], 
							memberId, 
							memberDict[UnionDefine.M_NAME_IDX], 
							memberDict[UnionDefine.M_LEVEL_IDX], 
							memberDict[UnionDefine.M_JOB_IDX], 
							memberDict[UnionDefine.M_H_CONTRIBUTION_IDX], 
							offLineTimeStr, 
							memberDict[UnionDefine.M_ZDL_IDX]])
	
	#同步客户端
	role.SendObj(Union_Show_Member_Panel, memberList)
	
def ShowApplyPanel(role):
	'''
	显示申请加入管理面板
	@param role:
	'''
	unionId = role.GetUnionID()
	sendList = []
	#是否已经申请过对应公会
	if unionId in UNIONID_TO_APPLY_ROLE_DATA:
		roleDataDict = UNIONID_TO_APPLY_ROLE_DATA[unionId]
		sendList = [applyRoleData for applyRoleData in roleDataDict.itervalues()]
	
	#同步客户端
	role.SendObj(Union_Show_Apply_Panel, sendList)
	
def ShowOtherUnionPanel(role):
	role.SendObj(Union_Show_Other_Union_Panel, GetOtherUnionSortList())
	
def GetOtherUnionSortList():
	campUnionList = []
	campUnionList.extend(UNION_LEFT_CAMP_LIST)
	campUnionList.extend(UNION_RIGHT_CAMP_LIST)
	
	#公会ID，公会名，会长名，公会阵营ID，公会等级，公会总战斗力，公会当前成员数，公会最大人口
	sortList = [[unionObj.union_id, unionObj.name, unionObj.leader_name, unionObj.camp_id, unionObj.level, unionObj.GetZDL(), len(unionObj.members), unionObj.population] for unionObj in campUnionList]
	#先用等级排序，相同等级则用公会人数排序
	sortList.sort(key = lambda x:(x[5], x[4], -x[0]), reverse = True)
	if len(sortList) > 100:
		sortList = sortList[0:100]
	return sortList
	
def JoinInUnionAndDeleteOtherUnionData(role):
	'''
	加入公会后删除此玩家在别的公会的申请信息
	@param role:
	'''
	global UNIONID_TO_APPLY_ROLE_DATA
	global ROLEID_TO_APPLYING_UNIONID
	
	roleId = role.GetRoleID()
	unionIdList = ROLEID_TO_APPLYING_UNIONID.get(roleId)
	if not unionIdList:
		return
	
	for unionId in unionIdList:
		roleDataDict = UNIONID_TO_APPLY_ROLE_DATA.get(unionId)
		if not roleDataDict:
			continue
		if roleId in roleDataDict:
			del roleDataDict[roleId]
			
	del ROLEID_TO_APPLYING_UNIONID[roleId]
		
def ShowCampPanel(role):
	'''
	显示阵营面板
	@param role:
	'''
	campLeftCnt = WorldData.WD[EnumSysData.CampLeftKey]
	campRightCnt = WorldData.WD[EnumSysData.CampRightKey]
	
	whichHasAward = 0
	if campLeftCnt == campRightCnt:
		#随机
		whichHasAward = random.randint(1,2)
	
	#加入人少的阵营有奖励
	if campLeftCnt > campRightCnt:
		whichHasAward = 2
	else:
		whichHasAward = 1
	
	#同步客户端
	role.SendObj(Camp_Show_Panel, whichHasAward)
	
def ShowCreatePanel(role):
	'''
	显示创建面板
	@param role:
	'''
	#没有阵营不能创建军团
	campId = role.GetCampID()
	if not campId:
		return
	
	campUnionList = []
	if campId == 1:
		campUnionList = UNION_LEFT_CAMP_LIST
	elif campId == 2:
		campUnionList = UNION_RIGHT_CAMP_LIST
	else:
		pass
	
	roleId = role.GetRoleID()
	applyUnionIdList = []
	#是否有申请加入的公会
	if roleId in ROLEID_TO_APPLYING_UNIONID:
		applyUnionIdList = ROLEID_TO_APPLYING_UNIONID[roleId]
	
	#公会ID，公会名，公会等级，会长名，公会当前成员数，公会最大人口，角色是否正在申请中标志，公会总战斗力
	sortList = [[unionObj.union_id, unionObj.name, unionObj.level, unionObj.leader_name, len(unionObj.members), unionObj.population, 1 if unionObj.union_id in applyUnionIdList else 0, unionObj.GetZDL()] for unionObj in campUnionList]
	
	role.SendObj(Union_Show_Create_Panel, sortList)
	
def ShowMainPanel(role):
	'''
	展示主面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	#公会魔神可挑战次数
	canChallengeUnionGodCnt = 0
	topGodId = unionObj.god[UnionDefine.GOD_TOP_IDX][1]
	nowGodId = role.GetDI8(EnumDayInt8.UnionGodProgress)
	if nowGodId < UnionConfig.UNION_GODID_MAX:
		if nowGodId < topGodId:
			canChallengeUnionGodCnt = topGodId - nowGodId
		else:
			canChallengeUnionGodCnt = 1
	else:
		canChallengeUnionGodCnt = 0
		
	#剩余未夺取宝箱数量
	canRobTreasureCnt = len(unionObj.treasure[1]) + len(unionObj.treasure[2]) + len(unionObj.treasure[3])
	for boxDataDict in unionObj.treasure.itervalues():
		for data in boxDataDict.itervalues():
			hasChallengedRoleIdList = data[2]
			if roleId not in hasChallengedRoleIdList:
				continue
			canRobTreasureCnt -= 1
			
	#公会名，公会等级，公会经验，公会会长名，公会当前人口，公会最大人口，公告，公会广播，公会资源，公会魔神可挑战次数，剩余未夺取宝箱数量
	role.SendObj(Union_Show_Main_Panel, (unionObj.name, unionObj.level, unionObj.exp, 
										unionObj.leader_name, len(unionObj.members), 
										unionObj.population, unionObj.notice, unionObj.news, 
										unionObj.resource, canChallengeUnionGodCnt, canRobTreasureCnt))

def ShowUnionResource(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	role.SendObj(SyncUnionResource, unionObj.resource)


def ChooseCamp(role, campId, hasAward):
	'''
	选择阵营
	@param role: 角色
	@param campId: 阵营ID
	@param hasAward: 是否给予奖励
	'''
	#是否已经有阵营
	if role.GetCampID():
		return
	
	#阵营ID是否合理
	if campId not in (1, 2):
		return
	
	#设置阵营ID
	role.SetCampID(campId)
	
	#添加进全服阵营人数
	if campId == 1:
		WorldData.WD[EnumSysData.CampLeftKey] += 1
	elif campId == 2:
		WorldData.WD[EnumSysData.CampRightKey] += 1
	
	#是否有奖励（信任客户端）
	if hasAward:
		role.IncMoney(10000)
		role.AddItem(25637, 1)
		
def ChangeUnionName(role, newName):
	'''
	修改公会名字
	@param role:
	@param newName:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否公会会长
	if not unionObj.IsLeader(role.GetRoleID()):
		return
	
	#日志
	with TraUnionChangeName:
		
		#如果合服之后名字重复，则公会名和公会ID一致，此时可以免费改名
		if unionObj.name != str(unionObj.union_id):
			itemCnt = role.ItemCnt(CHANGE_NAME_ITEM_CODING)
			if itemCnt == 0:
				return
			#扣物品
			role.DelItem(CHANGE_NAME_ITEM_CODING, 1)
			
		#发邮件
		for memberId in unionObj.members.iterkeys():
			Mail.SendMail(memberId, GlobalPrompt.UNION_CHANGE_NAME_TITLE, GlobalPrompt.UNION_CHANGE_NAME_SENDER, GlobalPrompt.UNION_CHANGE_NAME_MAIL % (unionObj.leader_name, newName))
		#日志事件
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveUnionChangeName, (unionObj.name, newName))
	
	unionObj.name = newName
	
	#保存
	unionObj.HasChange()
	
	#触发公会改名事件
	Event.TriggerEvent(Event.Eve_AfterChangeUnionName, role, unionObj.union_id)
	
	#通知客户端改名成功
	role.SendObj(Union_Change_Name_Success, None)
	#通知客户端公会名字
	role.SendObj(Union_Show_Union_Name, unionObj.name)
	
	#更新客户端
	ShowMainPanel(role)
	
	#公会频道
	UnionMsg(unionObj, GlobalPrompt.UNION_CHANGE_NAME_MAIL % (unionObj.leader_name, newName))
	
def ClearJoinCD(role):
	if role.GetCD(EnumCD.UnionJoinCD) == 0:
		return
	
	if role.GetRMB() < EnumGameConfig.Union_Clear_Join_CD_RMB:
		return
	
	role.DecRMB(EnumGameConfig.Union_Clear_Join_CD_RMB)
	
	role.SetCD(EnumCD.UnionJoinCD, 0)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.UNION_CLEAR_JOIN_CD)
	
#===============================================================================
# 触发事件管理
#===============================================================================
def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	#是否逻辑服
	if not role.IsLocalServer():
		return
	
	#数据还没载回
	if not BT.returnDB:
		return
	
	roleId = role.GetRoleID()
	unionId = role.GetUnionID()
	
	#没有对应的公会对象，证明公会已经不存在了
	unionObj = GetUnionObjByID(unionId)
	if not unionObj:
		#如果有公会ID,则公会数据异常，和谐
		if unionId > 0:
			#日志
			with TraUnionError:
				role.SetUnionID(0)
		return
	
	member = unionObj.members.get(roleId)
	if not member:
		#如果有公会ID,则公会数据异常，和谐
		if unionId > 0:
			#日志
			with TraUnionError:
				role.SetUnionID(0)
		return
	
	#上线状态
	unionObj.members[roleId][UnionDefine.M_ONLINE_IDX] = 1
	#更新等级
	unionObj.members[roleId][UnionDefine.M_LEVEL_IDX] = role.GetLevel()
	#更新头像
	unionObj.members[roleId][UnionDefine.M_PICTURE_IDX] = role.GetPortrait()
	#更新角色最后在线时间
	unionObj.members[roleId][UnionDefine.M_OFFLINE_TIME_IDX] = cDateTime.Seconds()
	#更新战斗力
	unionObj.members[roleId][UnionDefine.M_ZDL_IDX] = role.GetZDL()
	
	#设置角色职位(以公会为准)
	role.SetJobID(unionObj.GetMemberJob(roleId))
	#设置公会中状态
	role.SetI1(EnumInt1.InUnion, 1)
	
	#日志
	with TraUnionLoginSetContribution:
		#设置角色贡献(以公会为准)
		role.SetContribution(unionObj.GetMemberContribution(roleId))
	
	#若历史贡献为0，则判断是否公会有记录历史贡献，若也没有，则设置为个人贡献
	if not role.GetHistoryContribution():
		unionHistoryContribution = unionObj.GetMemberHistoryContribution(roleId)
		if unionHistoryContribution > 0:
			role.SetHistoryContribution(unionHistoryContribution)
		else:
			role.SetHistoryContribution(role.GetContribution())
	
	#保存
	unionObj.HasChange()
	
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	ShowUnionName(role)
	
	IsRoleExclamatoryMark(role)
	
	
def OnRoleLevelUp(role, param):
	'''
	角色升级
	@param role:
	@param param:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	
	member = unionObj.members.get(roleId)
	if not member:
		return
	
	#更新等级
	unionObj.members[roleId][UnionDefine.M_LEVEL_IDX] = role.GetLevel()
	
	#保存
	unionObj.HasChange()
	
def OnRoleExit(role, param):
	'''
	角色离线
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	
	#离线删除个人申请公会信息
	global ROLEID_TO_APPLYING_UNIONID
	if roleId in ROLEID_TO_APPLYING_UNIONID:
		del ROLEID_TO_APPLYING_UNIONID[roleId]
	
	#如果有公会
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否公会成员
	if not unionObj.IsMember(roleId):
		return
	
	#设置离线状态
	unionObj.members[roleId][UnionDefine.M_ONLINE_IDX] = 0
	#保存角色最后在线时间
	unionObj.members[roleId][UnionDefine.M_OFFLINE_TIME_IDX] = cDateTime.Seconds()
	
	#保存
	unionObj.HasChange()
	
def OnRoleDayClear(role, param):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	
	member = unionObj.members.get(roleId)
	if not member:
		return
	
	#更新角色最后在线时间
	unionObj.members[roleId][UnionDefine.M_OFFLINE_TIME_IDX] = cDateTime.Seconds()
	
	#保存
	unionObj.HasChange()
		
def AfterChangeRoleName(role, param):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	newRoleName = role.GetRoleName()
	#公会团长改名
	if roleId == unionObj.leader_id:
		unionObj.leader_name = newRoleName
	#公会成员改名(团长也是成员)
	if roleId in unionObj.members:
		unionObj.members[roleId][UnionDefine.M_NAME_IDX] = newRoleName
	
	#保存
	unionObj.HasChange()
	

#===============================================================================
#接口
#===============================================================================	
def GetUnionName(role):
	'''
	获取公会名字
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return ""
	return unionObj.name

def GetAllUnionLeaderId():
	'''
	获取所有公会会长id
	'''
	btData = BT.GetData()
	leaderIdList = []
	for unionId in btData.iterkeys():
		unionObj = GetUnionObjByID(unionId)
		if not unionObj:
			continue
		leaderIdList.append(unionObj.leader_id)
	return leaderIdList
		
def UnionMsg(unionObj, msg):
	'''
	公会频道公告
	@param unionObj:
	@param msg:
	'''
	#遍历发召集信息
	for memberRoleId in unionObj.members.iterkeys():
		memberRole = cRoleMgr.FindRoleByRoleID(memberRoleId)
		if not memberRole:
			continue
		#公会频道
		memberRole.Msg(8, 0, msg)
		
#===============================================================================
# 设置数组改变调用的函数
#===============================================================================
def AfterChangeContribution(role, oldValue, newValue):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	if not unionObj.IsMember(roleId):
		return
	
	unionObj.SetMemberContribution(roleId, newValue)
	
	#保存
	unionObj.HasChange()
	
def AfterChangeHistoryContribution(role, oldValue, newValue):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	if not unionObj.IsMember(roleId):
		return
	
	unionObj.SetMemberHistoryContribution(roleId, newValue)
	
	#保存
	unionObj.HasChange()
	
#===============================================================================
# 时间
#===============================================================================
def AfterNewHour():
	btData = BT.GetData()
	for unionId in btData.iterkeys():
		unionObj = GetUnionObjByID(unionId)
		if not unionObj:
			continue
		
		#每小时更新成员公会战斗力
		for memberId, memberData in unionObj.members.iteritems():
			member = cRoleMgr.FindRoleByRoleID(memberId)
			if not member:
				continue
			memberData[UnionDefine.M_ZDL_IDX] = member.GetZDL()

	
def AfterNewDay():
	'''
	每天都要检测每个公会当日的公会资源增加量，对于连续7天增加量不满足要求的公会，直接解散
	'''	
	#土耳其版本没有这个要求
	if Environment.EnvIsTK():
		return
	
	btData = BT.GetData()
	unionToBeDismissed = []
	for unionId in btData.iterkeys():
		unionObj = GetUnionObjByID(unionId)
		if not unionObj:
			continue
		dailyResource = unionObj.GetDailyResource()
		unionObj.ResetDailyResource()
		if not dailyResource < EnumGameConfig.UnionNeedResourceDaily:
			unionObj.ResetResourceLackDays()
			continue
		unionObj.IncResourceLackDays()
		if unionObj.GetResourceLackDays() < EnumGameConfig.UnionMaxLackResourceDays:
			with TraUnionDailyResourceLackDismissWarn:
				DismissWarn(unionObj, unionObj.GetResourceLackDays())
			continue
		#不能在遍历的时候改变btData里的内容，故这里先把要解散的 公会记到一个列表里
		unionToBeDismissed.append(unionObj)
	
	for unionObj in unionToBeDismissed:
		DismissUnion(unionObj)


def AfterNewMinute():
	global UNION_LEFT_CAMP_LIST, UNION_RIGHT_CAMP_LIST
	nowMinute = cDateTime.Minute()
	if nowMinute not in (0, 30):
		return
	#删除超时红包
	for UnionObj_1 in UNION_LEFT_CAMP_LIST:
		UnionObj_1.OverHongBao()
	for UnionObj_2 in UNION_RIGHT_CAMP_LIST:
		UnionObj_2.OverHongBao()
	

def DismissWarn(unionObj, days):
	'''
	公会解散警告，这里调用离线命令发邮件是为了保证角色身上记载的公会id跟实际公会id一致 
	'''
	members = unionObj.members
	unionName = unionObj.name
	needResource = EnumGameConfig.UnionNeedResourceDaily
	
	for roleId in members.iterkeys():
		Mail.SendMail(roleId,
			GlobalPrompt.UnionDismissWarnTitle,
			GlobalPrompt.UnionDismissWarnSender,
			GlobalPrompt.UnionDismissWarnCotent % (unionName, needResource, needResource, days, unionName))


def DismissUnion(unionObj):
	'''
	解散公会
	'''
	unionId = unionObj.union_id
	members = unionObj.members
	
	with TraUnionDailyResourceLackDismiss:
		#删除阵营中的公会
		DelUnionInCamp(unionObj)
		#删除公会
		unionObj.HasDelete()
		#删除缓存的公会对象
		global UNION_OBJ_DICT
		if unionId in UNION_OBJ_DICT:
			del UNION_OBJ_DICT[unionId]
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUnionDismissByResourceLack, unionId)
	
		CLC = Call.LocalDBCall
		FR = role = cRoleMgr.FindRoleByRoleID
		ET = Event.TriggerEvent
		SDHIsStart = SDHFunGather.StartFlag[SDHDefine.UnionFB]
		needResource = EnumGameConfig.UnionNeedResourceDaily
		unionName = unionObj.name
		
		for roleId in members:
			CLC (roleId, RoleUnionDataClear, unionId)
			Mail.SendMail(roleId, GlobalPrompt.UnionDismissTitle,
				GlobalPrompt.UnionDismissSender,
				GlobalPrompt.UnionDismissCotent % (unionName, needResource, unionName))
			
			role = FR(roleId)
			if role is not None:
				ET(Event.Eve_DelUnion, role, unionId)
				#重算公会技能属性
				role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
				if SDHIsStart:
					role.SendObj(SyncUnionFBData, {})


def RoleUnionDataClear(role, param):
	unionId = param
	if role.GetUnionID() != unionId:
		return
	#清理角色公会数据
	with TraUnionDailyResourceLackDismissClear:
		ClearRoleUnionData(role)
	#离开公会事件触发
	Event.TriggerEvent(Event.Eve_AfterLeaveUnion, role, None)

#===============================================================================
# role接口
#===============================================================================
def GetUnionObj(role):
	'''获取公会对象'''
	unionId = role.GetUnionID()
	if not unionId:
		return None
	return GetUnionObjByID(unionId)
		
#===============================================================================
# 腾讯接口返回
#===============================================================================
def OnCheckUnionNotice(response, regparam):
	role, notice = regparam
	if response is None:
		return
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_QQ_NOT_LOGIN)
		return
	#判断是否有敏感字
	if body["is_dirty"] != 0:
		return
	
	EditUnionNotice(role, notice)
	
def OnCheckUnionChangeName(response, regparam):
	role, unionName = regparam
	if response is None:
		return
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_QQ_NOT_LOGIN)
		return
	#判断是否有敏感字
	if body["is_dirty"] != 0:
		return
	
	ChangeUnionName(role, unionName)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestCampOpenPanel(role, msg):
	'''
	客户端请求打开阵营面板
	@param role:
	@param msg:
	'''
	ShowCampPanel(role)
	

def RequestChooseCamp(role, msg):
	'''
	客户端请求选择阵营
	@param role:
	@param msg:
	'''
	campId, hasAward = msg
	
	#等级是否满足条件
	if role.GetLevel() < CAMP_NEED_LEVEL:
		return
	
	#日志
	with TraChooseCamp:
		ChooseCamp(role, campId, hasAward)
	
def RequestUnionOpenCreatePanel(role, msg):
	'''
	客户端请求打开创建公会面板
	@param role:
	@param msg:
	'''
	ShowCreatePanel(role)
	
def RequestUnionOpenMainPanel(role, msg):
	'''
	客户端请求打开公会主面板
	@param role:
	@param msg:
	'''
	ShowMainPanel(role)
	
def RequestUnionOpenMemberPanel(role, msg):
	'''
	客户端请求打开公会成员面板
	@param role:
	@param msg:
	'''
	ShowMemberPanel(role)
	
def RequestUnionOpenApplyPanel(role, msg):
	'''
	客户端打开公会申请管理面板
	@param role:
	@param msg:
	'''
	ShowApplyPanel(role)
	
def RequestUnionOpenOtherUnionPanel(role, msg):
	'''
	客户端打开其他公会面板
	@param role:
	@param msg:
	'''
	ShowOtherUnionPanel(role)
	
def RequestUnionApplyJoin(role, msg):
	'''
	客户端请求申请加入公会
	@param role:
	@param msg:
	'''
	unionId = msg
	
	#等级是否满足条件
	if role.GetLevel() < UnionDefine.UNION_NEED_LEVEL:
		return
	
	ApplyJoinUnion(role, unionId)
	
def RequestUnionCancelJoin(role, msg):
	'''
	客户端请求撤销加入公会
	@param role:
	@param msg:
	'''
	unionId = msg
	
	CancelJoinUnion(role, unionId)
	
def RequestYesOrNoToJoinUnion(role, msg):
	'''
	客户端回应是否答应加入公会
	@param role:
	@param msg:
	'''
	yesOrNo, wantedRoleId = msg
	if yesOrNo == 1:
		#同意加入公会
		AgreeJoinUnion(role, wantedRoleId)
		
		#公会红包出现叹号
		unionObj = role.GetUnionObj()
		if not unionObj:
			return
		if unionObj.HongBaoshowTips(wantedRoleId):
			tmpRole = cRoleMgr.FindRoleByRoleID(wantedRoleId)
			if not tmpRole:
				return
			tmpRole.SendObj(UnionHongBaoShowTips, True)
	elif yesOrNo == 2:
		#拒绝加入公会
		RejectJoinUnion(role, wantedRoleId)

def RequestUnionRMBContribute(role, msg):
	'''
	客户端请求公会RMB贡献
	@param role:
	@param msg:
	'''
	rmb = msg
	#日志
	with TraUnionRMBContribute:
		RMBContribute(role, rmb)
	
def RequestUnionKickOutMember(role, msg):
	'''
	客户端请求公会踢出成员
	@param role:
	@param msg:
	'''
	desRoleId = msg
	
	KickOutMember(role, desRoleId)
	
def RequestUnionQuit(role, msg):
	'''
	客户端请求退出公会
	@param role:
	@param msg:
	'''
	#日志
	with TraQuitUnion:
		QuitUnion(role)
		
	
def RequestUnionEditNotice(role, msg):
	'''
	客户端请求编辑公会公告
	@param role:
	@param msg:
	'''
	notice = msg
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if role.GetLevel() < UnionNewsNeedLevel and role.GetVIP() < UnionNewsNeedVIP:
		return
	
	#是否超过长度
	if len(notice) > UNION_NOTICE_LEN_MAX:
		return
	
	#判断是否有权限
	roleJobId = unionObj.GetMemberJob(role.GetRoleID())
	roleJobConfig = UnionConfig.UNION_JOB.get(roleJobId)
	if not roleJobConfig:
		return
	if not roleJobConfig.notice:
		return
	
	#QQ平台过滤公会名
	if Environment.EnvIsQQ():
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		#过滤公会名
		QQHttp.word_filter(openid, openkey, pf, notice, OnCheckUnionNotice, (role, notice))
		return
	else:
		#非腾讯平台直接可以编辑
		EditUnionNotice(role, notice)
		
def RequestUnionChangeName(role, msg):
	'''
	客户端请求修改公会名字
	@param role:
	@param msg:
	'''
	newName = msg
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否公会会长
	if not unionObj.IsLeader(role.GetRoleID()):
		return
	
	#是否超过长度
	if len(newName) > UnionDefine.UNION_NAME_LEN_MAX:
		return
	
	#名字是否有空格或者Tab
	if newName.count(' ') or newName.count('\t'):
		return
	
	#判断名字是否有重复
	btData = BT.GetData()
	nameList = [union["name"] for union in btData.itervalues()]
	if newName in nameList:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_NAME_REPEAT)
		return
	
	#QQ平台过滤军团名
	if Environment.EnvIsQQ():
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		#过滤军团名
		QQHttp.word_filter(openid, openkey, pf, newName, OnCheckUnionChangeName, (role, newName))
		return
	else:
		ChangeUnionName(role, newName)
		
def RequestUnionClearJoinCD(role, msg):
	'''
	客户端请求清除加入公会CD
	@param role:
	@param msg:
	'''
	#日志
	with TraClearUnionJoinCD:
		ClearJoinCD(role)
	
def RequestUnionGoStation(role, msg):
	'''
	客户端请求返回公会驻地
	@param role:
	@param msg:
	'''
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	role.Revive(unionId, 1015, 1233)
	
def RequestUnionLeaveStation(role, msg):
	'''
	客户端请求离开公会驻地
	@param role:
	@param msg:
	'''
	role.BackPublicScene()


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		BT = BigTable.BigTable("sys_union", 4, AfterLoad)
		
		#角色登陆
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#角色升级
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		#角色离线
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#角色改名后
		Event.RegEvent(Event.Eve_AfterChangeName, AfterChangeRoleName)
		
		#设置数组改变调用的函数
		cRoleDataMgr.SetInt32Fun(EnumInt32.UnionContribution, AfterChangeContribution)
		cRoleDataMgr.SetInt32Fun(EnumInt32.UnionHistoryContribution, AfterChangeHistoryContribution)
		
		#时间
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		Cron.CronDriveByMinute((2038, 1, 1), AfterNewDay, H="H == 0", M="M == 5")
		
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Camp_Open_Panel", "客户端请求打开阵营面板"), RequestCampOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Camp_Choose", "客户端请求选择阵营"), RequestChooseCamp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Create_Panel", "客户端请求打开创建公会面板"), RequestUnionOpenCreatePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Main_Panel", "客户端请求打开公会主面板"), RequestUnionOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Member_Panel", "客户端打开公会成员面板"), RequestUnionOpenMemberPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Apply_Panel", "客户端打开公会申请管理面板"), RequestUnionOpenApplyPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Other_Union_Panel", "客户端打开其他公会面板"), RequestUnionOpenOtherUnionPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Apply_Join", "客户端请求申请加入公会"), RequestUnionApplyJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Cancel_Join", "客户端请求撤销加入公会"), RequestUnionCancelJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Join_Yes_Or_No", "客户端回应是否答应加入公会"), RequestYesOrNoToJoinUnion)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_RMB_Contribute", "客户端请求公会RMB贡献"), RequestUnionRMBContribute)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Quit", "客户端请求退出公会"), RequestUnionQuit)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Kick_Out", "客户端请求公会踢出成员"), RequestUnionKickOutMember)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Edit_Notice", "客户端请求编辑公会公告"), RequestUnionEditNotice)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Change_Name", "客户端请求修改公会名字"), RequestUnionChangeName)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Clear_Join_CD", "客户端请求清除加入公会CD"), RequestUnionClearJoinCD)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Go_Station", "客户端请求返回公会驻地"), RequestUnionGoStation)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Leave_Station", "客户端请求离开公会驻地"), RequestUnionLeaveStation)

