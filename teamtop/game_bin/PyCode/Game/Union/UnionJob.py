#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionJob")
#===============================================================================
# 公会职位
#===============================================================================
import Environment
import cComplexServer
import cDateTime
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Union import UnionMgr, UnionDefine, UnionConfig

if "_HasLoad" not in dir():
	SEVEN_DAY_SECONDS = 7 * 24 * 60 * 60	#7天总秒数
	
	#消息
	Union_Show_Transfer_Leader_Panel = AutoMessage.AllotMessage("Union_Show_Transfer_Leader_Panel", "通知客户端显示会长转让面板")
	Union_Show_Election_Panel = AutoMessage.AllotMessage("Union_Show_Election_Panel", "通知客户端显示选举面板")

def ShowTransferLeaderPanel(role):
	'''
	显示转让会长面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	memberList = []
	for memberId, memberDict in unionObj.members.iteritems():
		#vip，roleId，名字，等级，职位，历史贡献，战斗力
		memberList.append([ memberDict[UnionDefine.M_VIP_IDX], 
							memberId, 
							memberDict[UnionDefine.M_NAME_IDX], 
							memberDict[UnionDefine.M_LEVEL_IDX], 
							memberDict[UnionDefine.M_JOB_IDX], 
							memberDict[UnionDefine.M_H_CONTRIBUTION_IDX], 
							memberDict[UnionDefine.M_ZDL_IDX]])
	
	#按职位排序
	memberList.sort(key=lambda x:x[3], reverse=False)
	
	#同步客户端
	role.SendObj(Union_Show_Transfer_Leader_Panel, memberList)
	
def ShowElectionPanel(role):
	'''
	显示选举面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	memberList = []
	for memberId, memberDict in unionObj.members.iteritems():
		#vip，roleId，名字，等级，职位，历史贡献，选票，战斗力
		memberList.append([ memberDict[UnionDefine.M_VIP_IDX], 
							memberId, 
							memberDict[UnionDefine.M_NAME_IDX], 
							memberDict[UnionDefine.M_LEVEL_IDX], 
							memberDict[UnionDefine.M_JOB_IDX], 
							memberDict[UnionDefine.M_H_CONTRIBUTION_IDX], 
							unionObj.election[UnionDefine.ELECTION_ROLE_VOTES_IDX].get(memberId, 0), 
							memberDict[UnionDefine.M_ZDL_IDX]])
	
	#按职位排序
	memberList.sort(key=lambda x:x[3], reverse=False)
	
	#投票角色ID列表
	voteRoleIdList = unionObj.election[UnionDefine.ELECTION_JOIN_IDX]
	#是否已经投票
	hasVotedFlag = 1 if role.GetRoleID() in voteRoleIdList else 0
	
	#同步客户端
	role.SendObj(Union_Show_Election_Panel, (hasVotedFlag, memberList))

def TransferLeader(role, desRoleId, backFunId):
	'''
	转让会长
	@param role:
	@param desRoleId:
	@param backFunId:
	'''
	roleId = role.GetRoleID()
	
	#不能转让给自己
	if roleId == desRoleId:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否公会成员
	if not unionObj.IsMember(desRoleId):
		return
	
	#只有团长可以转让
	if not unionObj.IsLeader(roleId):
		return
	
	#原职位的玩家变成员
	unionObj.SetMemberJob(roleId, UnionDefine.MEMBER_JOB_ID)
	
	#转让团长
	newLeaderName = unionObj.GetMemberName(desRoleId)
	unionObj.leader_id = desRoleId
	unionObj.leader_name = newLeaderName
	unionObj.SetMemberJob(desRoleId, UnionDefine.LEADER_JOB_ID)
	
	#保存
	unionObj.HasChange()
	
	#回调客户端转让成功
	role.CallBackFunction(backFunId, None)
	
	#日志事件
	AutoLog.LogBase(roleId, AutoLog.eveUnionTransferLeader, (unionObj.union_id, desRoleId))
	
	#更新面板
	ShowTransferLeaderPanel(role)
	UnionMgr.ShowMainPanel(role)
	
def UpJob(role, desRoleId):
	'''
	提升职位
	@param role:
	@param desRoleId:
	'''
	#不能对自己操作
	if role.GetRoleID() == desRoleId:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是不是团员
	if not unionObj.IsMember(desRoleId):
		return
	
	#判断role是否有权限
	roleJobId = unionObj.GetMemberJob(role.GetRoleID())
	roleJobConfig = UnionConfig.UNION_JOB.get(roleJobId)
	if not roleJobConfig:
		return
	if not roleJobConfig.allotJob:
		return
	
	desRoleJobId = unionObj.GetMemberJob(desRoleId)
	#不能提升职位比自己高或者相同的人
	if desRoleJobId <= roleJobId:
		return
	
	#获取要提升的职位配置
	upJobId = desRoleJobId - 1
	upJobConfig = UnionConfig.UNION_JOB.get(upJobId)
	if not upJobConfig:
		return
	
	#判断公会职位数量
	jobCnt = unionObj.GetJobCnt(upJobId)
	if jobCnt >= upJobConfig.jobMaxCnt:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_JOB_UP_FULL_PROMPT)
		return
	
	unionObj.SetMemberJob(desRoleId, upJobId)
	
	#保存
	unionObj.HasChange()
	
	#更新面板
	UnionMgr.ShowMemberPanel(role)
	
def DownJob(role, desRoleId):
	'''
	降低职位
	@param role:
	@param desRoleId:
	'''
	#不能对自己操作
	if role.GetRoleID() == desRoleId:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是不是团员
	if not unionObj.IsMember(desRoleId):
		return
	
	#判断role是否有权限
	roleJobId = unionObj.GetMemberJob(role.GetRoleID())
	roleJobConfig = UnionConfig.UNION_JOB.get(roleJobId)
	if not roleJobConfig:
		return
	if not roleJobConfig.allotJob:
		return
	
	desRoleJobId = unionObj.GetMemberJob(desRoleId)
	#不能降低职位比自己高或者相同的人
	if desRoleJobId <= roleJobId:
		return
	
	#获取要提升的职位配置
	downJobId = desRoleJobId + 1
	downJobConfig = UnionConfig.UNION_JOB.get(downJobId)
	if not downJobConfig:
		return
	
	#如果是普通成员不用判断次数
	if downJobId != UnionDefine.MEMBER_JOB_ID:
		#判断公会职位数量
		jobCnt = unionObj.GetJobCnt(downJobId)
		if jobCnt >= downJobConfig.jobMaxCnt:
			#提示
			role.Msg(2, 0, GlobalPrompt.UNION_JOB_DOWN_FULL_PROMPT)
			return
	
	unionObj.SetMemberJob(desRoleId, downJobId)
	
	#保存
	unionObj.HasChange()
	
	#更新面板
	UnionMgr.ShowMemberPanel(role)
	
def Vote(role, desRoleId, backFunId):
	'''
	投票
	@param role:
	@param desRoleId:
	@param backFunId:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#被投票的人是否公会成员
	if not unionObj.IsMember(desRoleId):
		return
	
	roleId = role.GetRoleID()
	joinSelectionList = unionObj.election[UnionDefine.ELECTION_JOIN_IDX]
	#是否已经投过票
	if roleId in joinSelectionList:
		return
	
	#记录选票
	roleVotesDict = unionObj.election[UnionDefine.ELECTION_ROLE_VOTES_IDX]
	if desRoleId in roleVotesDict:
		roleVotesDict[desRoleId] += 1
	else:
		roleVotesDict[desRoleId] = 1
		
	#标记已经投过票
	joinSelectionList.append(roleId)
		
	#保存
	unionObj.HasChange()
	
	#回调客户端成功投票
	role.CallBackFunction(backFunId, None)
	
#===============================================================================
# 每日调用
#===============================================================================
def AfterNewDay():
	#判断是否有公会需要进行公会选举
	btData = UnionMgr.BT.GetData()
	seconds = cDateTime.Seconds()
	for unionId in btData.keys():
		unionObj = UnionMgr.GetUnionObjByID(unionId)
		if not unionObj:
			continue
		
		#公会是否正在选举中
		if unionObj.election[UnionDefine.ELECTION_START_IDX]:
			newLeaderId = 0
			maxVotes = 0
			#选出会长
			for roleId, votes in unionObj.election[UnionDefine.ELECTION_ROLE_VOTES_IDX].iteritems():
				#选出票数最高
				if votes > maxVotes:
					newLeaderId = roleId
					maxVotes = votes
			
			#是否已经是会长
			if not unionObj.IsLeader(newLeaderId):
				#是否公会成员
				if unionObj.IsMember(newLeaderId):
					#旧会长变为成员
					unionObj.SetMemberJob(unionObj.leader_id, UnionDefine.MEMBER_JOB_ID)
					#设置新会长
					unionObj.leader_id = newLeaderId
					unionObj.leader_name = unionObj.members[newLeaderId][UnionDefine.M_NAME_IDX]
					unionObj.SetMemberJob(newLeaderId, UnionDefine.LEADER_JOB_ID)
					#还原选举状态
					unionObj.election[UnionDefine.ELECTION_START_IDX] = 0
					unionObj.election[UnionDefine.ELECTION_JOIN_IDX] = []
					unionObj.election[UnionDefine.ELECTION_ROLE_VOTES_IDX] = {}
					#保存
					unionObj.HasChange()
					
			continue
		else:
			offLineSeconds = seconds - unionObj.members[unionObj.leader_id][UnionDefine.M_OFFLINE_TIME_IDX]
			#会长是否离线7天
			if offLineSeconds >= SEVEN_DAY_SECONDS:
				#开启选举
				unionObj.election[UnionDefine.ELECTION_START_IDX] = 1
				#保存
				unionObj.HasChange()
			
		
	
#===============================================================================
# 客户端消息
#===============================================================================
def RequestUnionOpenTransferLeaderPanel(role, msg):
	'''
	客户端请求打开转让会长面板
	@param role:
	@param msg:
	'''
	ShowTransferLeaderPanel(role)
	
def RequestUnionOpenElectionPanel(role, msg):
	'''
	客户端请求打开选举面板
	@param role:
	@param msg:
	'''
	backFunId, _ = msg
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#公会是否正在选举中
	if not unionObj.election[UnionDefine.ELECTION_START_IDX]:
		role.CallBackFunction(backFunId, 0)
	else:
		role.CallBackFunction(backFunId, 1)
		#显示面板
		ShowElectionPanel(role)
	
def RequestUnionTransferLeader(role, msg):
	'''
	客户端请求转让团长
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	desRoleId = data
	
	#日志
	with TraUnionTransferLeader:
		TransferLeader(role, desRoleId, backFunId)
	
def RequestUnionUpJob(role, msg):
	'''
	客户端请求公会提升职位
	@param role:
	@param msg:
	'''
	desRoleId = msg
	
	UpJob(role, desRoleId)
	
def RequestUnionDownJob(role, msg):
	'''
	客户端请求公会降低职位
	@param role:
	@param msg:
	'''
	desRoleId = msg
	
	DownJob(role, desRoleId)
	
def RequestUnionVote(role, msg):
	'''
	客户端请求公会降低职位
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	
	desRoleId = data
	
	Vote(role, desRoleId, backFunId)
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#公会每日调用
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		#日志
		TraUnionTransferLeader = AutoLog.AutoTransaction("TraUnionTransferLeader", "公会转让会长")
			
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Transfer_Leader_Panel", "客户端请求打开转让会长面板"), RequestUnionOpenTransferLeaderPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Election_Panel", "客户端请求打开选举面板"), RequestUnionOpenElectionPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Transfer_Leader", "客户端请求转让团长"), RequestUnionTransferLeader)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Up_Job", "客户端请求公会提升职位"), RequestUnionUpJob)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Down_Job", "客户端请求公会降低职位"), RequestUnionDownJob)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Vote", "客户端请求公会选举投票"), RequestUnionVote)
		
		