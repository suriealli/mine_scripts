#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Mount.MountMgr")
#===============================================================================
# 坐骑
#===============================================================================
import random
import cRoleDataMgr
import cRoleMgr
import Environment
import cDateTime
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Mount import MountBase, MountConfig, MountDefine
from Game.Role import Event
from Game.Role.Data import EnumInt16, EnumInt32, EnumDayInt8, EnumInt8,\
	EnumTempObj, EnumObj
from Game.Activity.ProjectAct import ProjectAct, EnumProActType
from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
from Game.Team import EnumTeamType

if "_HasLoad" not in dir():
	
	MAX_EVOLVEID = 90
	
	#坐骑进化限时道具
	Mount_Grade_Coding = 28400
	#消息
	Mount_Evolve_Prompt = AutoMessage.AllotMessage("Mount_Evolve_Prompt", "坐骑培养提示")
	Mount_Evolve_Hign_Prompt = AutoMessage.AllotMessage("Mount_Evolve_Hign_Prompt", "坐骑高级培养提示")
	Mount_Evolve_Crit_Prompt = AutoMessage.AllotMessage("Mount_Evolve_Crit_Prompt", "坐骑培养暴击提示")
	Mount_EvolveBig_Crit_Prompt = AutoMessage.AllotMessage("Mount_EvolveBig_Crit_Prompt", "坐骑培养大暴击提示")
	Mount_Advanced_for_client = AutoMessage.AllotMessage("Mount_Advanced_for_client", "坐骑进阶")
	Mount_Metempsychosis_for_client = AutoMessage.AllotMessage("Mount_Metempsychosis_for_client", "坐骑可转生")
	Mount_Eat_Food_Suc = AutoMessage.AllotMessage("Mount_Eat_Food_Suc", "坐骑吃食物成功")
	Mount_Send_Attribute = AutoMessage.AllotMessage("Mount_Send_Attribute", "坐骑属性发送")
	Mount_Send_Unreal = AutoMessage.AllotMessage("Mount_Send_Unreal", "坐骑解锁列表")
	Mount_Syn_Time = AutoMessage.AllotMessage("Mount_Syn_Time", "同步时限坐骑时间")
	
	#日志
	TraMountEvolve = AutoLog.AutoTransaction("TraMountEvolve", "坐骑培养")
	TraMountActivate = AutoLog.AutoTransaction("TraMountActivate", "坐骑激活")
	OutDateMount = AutoLog.AutoTransaction("OutDateMount", "坐骑过期")
	MountMetempsychosis = AutoLog.AutoTransaction("MountMetempsychosis", "坐骑转生")
	MountApperanceUpLog = AutoLog.AutoTransaction("MountApperanceUpLog", "坐骑外形品质进阶")
	Tra_Mount_ExchangeMount = AutoLog.AutoTransaction("Tra_Mount_ExchangeMount", "坐骑系统_兑换激活坐骑")
	
	
def AddMount(role, mountId):
	#增加一个坐骑
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if mountId in mountMgr.MountId_list:
		return
	
	mountCfg = MountConfig._MOUNT_BASE.get(mountId)
	if not mountCfg:
		print "GE_EXC,can not find role(%s) mountId(%s) in AddMount" % (role.GetRoleID(), mountId)
		return
	
	mountMgr.MountId_list.append(mountId)
	
	if mountCfg.timeLimit:#有时限
		mountMgr.Mount_outData_dict[mountId] = cDateTime.Days() + mountCfg.timeLimit
		role.SendObj(Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
	mountMgr.ResetAttribute()
	role.ResetGlobalMountProperty()
	#最新活动触发,新增坐骑进化ID为0
	LatestActivityMgr.GetFunByType(EnumLatestType.MountGrade_Latest, role)

def ChangeMountTime(role, mountId):
	'''
	将限时坐骑改为永久坐骑
	@param role:
	'''
	basecfg = MountConfig._MOUNT_BASE.get(mountId)
	if not basecfg:
		return
	if not basecfg.timeLimit:#不是有时限坐骑
		return
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	#玩家激活的坐骑中没有
	if mountId not in mountMgr.MountId_list:
		#在历史记录也没有，即该玩家在调用该接口前未激活过该坐骑,直接返回
		if mountId not in mountMgr.history_outData_mountId:
			return
		else:
			mountMgr.MountId_list.append(mountId)
	
	if mountId in mountMgr.Mount_outData_dict:
		del mountMgr.Mount_outData_dict[mountId]

	mountMgr.ResetAttribute()
	role.ResetGlobalMountProperty()
	
	role.SendObj(Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
		
def AddDefaultMount(role):
	mountId = 1
	#日志
	with TraMountActivate:
		#设置坐骑进化ID
		role.SetI16(EnumInt16.MountEvolveID, 1)
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	#加入幻化列表
	mountMgr.MountId_list.append(mountId)
	role.SetI8(EnumInt8.LastMountID, mountId)
	#骑乘坐骑
#	OnMount(role, mountId)

def AddMountExpTemp(role, exp):
	'''
	给坐骑增加临时经验
	@param role:
	@param exp:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if not mountMgr:
		return
	#获取玩家坐骑进阶等级
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	if evolveId >= MAX_EVOLVEID:#坐骑已经是最高阶了
		return
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, can not find role(%s) evolveId:(%s) Config in _MOUNT_EVOLVE in AddMountExp, " % (role.GetRoleID(), evolveId)
		return
	nowExp = role.GetI32(EnumInt32.MountExp)
	if config.totalExp == nowExp:
		return
	role.IncI32(EnumInt32.MountTempExp, exp)
	totalExp = nowExp + role.GetI32(EnumInt32.MountTempExp)
	if totalExp >= config.totalExp:
		if config.NextID:#可转生
			#将经验设为满经验
			role.SetI32(EnumInt32.MountExp, config.totalExp)
			#将临时经验清空
			role.SetI32(EnumInt32.MountTempExp, 0)
			role.SendObj(Mount_Metempsychosis_for_client,config.NextID )
			return
		#进化到下一个层次
		role.IncI16(EnumInt16.MountEvolveID, 1)
		#设置剩余经验
		role.SetI32(EnumInt32.MountExp, max(0, nowExp - config.totalExp))
		#将临时经验清空
		role.SetI32(EnumInt32.MountTempExp, 0)
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		SendAttriClient(role)
		
def AddMountExp(role, exp):
	'''
	给坐骑增加经验
	@param role:
	@param exp:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if not mountMgr:
		return
	#获取玩家坐骑进阶等级
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	if evolveId >= MAX_EVOLVEID:#坐骑已经是最高阶了
		return
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, can not find role(%s) evolveId:(%s) Config in _MOUNT_EVOLVE in AddMountExp, " % (role.GetRoleID(), evolveId)
		return
	if config.totalExp == role.GetI32(EnumInt32.MountExp):
		return
	role.IncI32(EnumInt32.MountExp, exp)
	
	
def SeniorMountEvolve(role):
	'''
	坐骑高级培养
	@param role:
	'''
	if role.GetVIP() < EnumGameConfig.VIP_Senior_Mount:
		return
	#坐骑进化ID
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	if evolveId >= MAX_EVOLVEID:
		return
	#坐骑初始配置属性
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, can not find role(%s) evolveId:(%s) Config in _MOUNT_EVOLVE in MountEvolve58, " % (role.GetRoleID(), evolveId)
		return
	#优化扣道具
	item_cnt = 0
	cnt = role.ItemCnt(MountDefine.MOUNT_EVOLVE_ID)
	times = MountDefine.SENIOR_MOUNT_TIMES
	if cnt:
		if cnt < times:
			times = times - cnt
			item_cnt = cnt
		else:
			item_cnt = MountDefine.SENIOR_MOUNT_TIMES
			times = 0
	needRMB = config.needRMB * times
	#判断是否有元宝
	if role.GetRMB() < needRMB:
		return
	if needRMB:
		role.DecRMB(needRMB)
	if item_cnt:
		if role.DelItem(MountDefine.MOUNT_EVOLVE_ID, item_cnt) < item_cnt:
			return
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	addExp     = config.RMBaddExp
	GoldCrit1 = config.RMBCrit1 #小暴击概率
	GoldTimes1 = config.RMBTimes1
	GoldCrit2 = config.RMBCrit2 #大暴击概率
	times1 = 0#记录产生暴击一的次数
	times2 = 0#记录产生暴击而的次数
	total_exp = 0
	for _ in xrange(MountDefine.SENIOR_MOUNT_TIMES):
		random_value = random.randint(1, 10000)
		#是否出现暴击
		if random_value < GoldCrit2:
			times2 += 1
		elif random_value < GoldCrit1:#
			total_exp += addExp * GoldTimes1
			times1 += 1
		else:
			total_exp += addExp
	exp = role.GetI32(EnumInt32.MountExp)
	temp_exp = role.GetI32(EnumInt32.MountTempExp)
	nowExp = exp + total_exp + temp_exp
	levelUpExp = config.totalExp
	if nowExp >= levelUpExp:
		nextConfig = config
		while nowExp >= levelUpExp:
			if nextConfig.NextID:#可转生了
				#将经验设为满经验
				role.SetI32(EnumInt32.MountExp, nextConfig.totalExp)
				role.SendObj(Mount_Metempsychosis_for_client,nextConfig.NextID )
				MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
				role.SendObj(Mount_Evolve_Hign_Prompt, [times1, times2, total_exp, MountEvolveID])		
				#假如有临时经验，清0
				if temp_exp > 0:
					role.SetI32(EnumInt32.MountTempExp, 0)
				#专题活动
				ProjectAct.GetFunByType(EnumProActType.ProjectMountEvent, [role, MountDefine.SENIOR_MOUNT_TIMES])
				#版本判断
				if Environment.EnvIsNA():
					#通用活动
					HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
					HalloweenNAMgr.mount_train(2, MountDefine.SENIOR_MOUNT_TIMES)
				elif Environment.EnvIsRU():
					#七日活动
					sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
					#坐骑养成
					sevenActMgr.mount_train(MountDefine.SENIOR_MOUNT_TIMES)
				
				return
			#进化到下一个层次
			role.IncI16(EnumInt16.MountEvolveID, 1)
			nowExp -= levelUpExp
			if temp_exp > 0:#假如有临时经验
				nowExp = max(nowExp - temp_exp, 0)
				role.SetI32(EnumInt32.MountTempExp, 0)
			nextConfig = MountConfig._MOUNT_EVOLVE.get(role.GetI16(EnumInt16.MountEvolveID))
			if not nextConfig:
				break			
			levelUpExp = nextConfig.totalExp
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		SendAttriClient(role)
		#设置剩余的经验
		role.SetI32(EnumInt32.MountExp, nowExp)
	else:
		role.IncI32(EnumInt32.MountExp, total_exp)
	if times2:#大暴击直接加进化次数
		for _ in xrange(times2):
			MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
			evolve_cfg = MountConfig._MOUNT_EVOLVE.get(MountEvolveID)
			if not evolve_cfg:
				return
			if evolve_cfg.NextID:
				role.SetI32(EnumInt32.MountExp, evolve_cfg.totalExp)
				role.SendObj(Mount_Metempsychosis_for_client,evolve_cfg.NextID )
				MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
				role.SendObj(Mount_Evolve_Hign_Prompt, [times1, times2, total_exp, MountEvolveID])
				return
			role.IncI16(EnumInt16.MountEvolveID, 1)
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		SendAttriClient(role)
		#假如有临时经验，清0
		if role.GetI32(EnumInt32.MountTempExp) > 0:
			role.SetI32(EnumInt32.MountTempExp, 0)
	MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
	role.SendObj(Mount_Evolve_Hign_Prompt, [times1, times2, total_exp, MountEvolveID])		
	#专题活动相关
	ProjectAct.GetFunByType(EnumProActType.ProjectMountEvent, [role, MountDefine.SENIOR_MOUNT_TIMES])
	#版本判断
	if Environment.EnvIsNA():
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.mount_train_count(times)
	
	#版本判断
	if Environment.EnvIsNA():
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.mount_train(2, MountDefine.SENIOR_MOUNT_TIMES)
	elif Environment.EnvIsRU():
		#七日活动
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		#坐骑养成
		sevenActMgr.mount_train(MountDefine.SENIOR_MOUNT_TIMES)
		
def MountEvolve(role, moneyType):
	'''
	坐骑培养，普通和元宝培养
	@param role:
	@param moneyType:培养类型
	'''
	
	#坐骑进化ID
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	if evolveId >= MAX_EVOLVEID:
		return
	#坐骑初始配置属性
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, can not find role(%s) evolveId:(%s) Config in _MOUNT_EVOLVE in MountEvolve156, " % (role.GetRoleID(), evolveId)
		return
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	addExp = 0
	GoldCrit1 = 0#暴击概率
	GoldTimes1 = 0#暴击产生的倍数
	GoldCrit2 = 0#大暴击概率
	if 1 == moneyType:#普通培养
		#判断是否还有普通培养次数，大于LEVEL_NO_LIMIT 的可以无限培养
		if role.GetLevel() < MountDefine.LEVEL_NO_LIMIT:
			LIMIT_TIMES = 0
			#根据玩家等级获取每日可普通培养次数
			for level, times in MountDefine.NORMAL_EVOLVE_TIMES.iteritems():
				if role.GetLevel() < level:
					LIMIT_TIMES = times
					break
			if role.GetDI8(EnumDayInt8.MountEvolveCnt) >= LIMIT_TIMES:
				return
		#判断金钱
		if role.GetMoney() < config.needMoney:
			return
		
		#扣钱
		role.DecMoney(config.needMoney)
		addExp = config.addExp #每次非暴击加的经验
		GoldCrit1 = config.GoldCrit #暴击概率
		GoldTimes1 = config.GoldTimes #暴击产生的倍数
		#是普通培养且等级小于限制等级
		if role.GetLevel() < MountDefine.LEVEL_NO_LIMIT:
			role.IncDI8(EnumDayInt8.MountEvolveCnt, 1)
		#环境判断
		if Environment.EnvIsNA():
			kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			kaifuActMgr.mount_train_count(1)
		
	else:#元宝培养
		#先判断是否有道具
		if not role.ItemCnt(config.itemId):
			#判断是否有元宝
			if role.GetRMB() < config.needRMB:
				return
			role.DecRMB(config.needRMB)
		else:
			#扣除进化道具(非绑定)
			if role.DelItem(config.itemId, 1) < 1:
				print "GE_EXC, error in role(%s) MountEvolve item not enough (%s, %s)" % (role.GetRoleID(), config.needPropID2, config.needPropCnt2)
				return
		addExp     = config.RMBaddExp
		GoldCrit1  = config.RMBCrit1
		GoldTimes1 = config.RMBTimes1
		GoldCrit2  = config.RMBCrit2
		#版本判断
		if Environment.EnvIsNA():
			kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			kaifuActMgr.mount_train_count(1)
		
	#是否出现暴击
	isCrit1 = False	#记录是否出现小暴击
	isCrit2 = False #记录是否出现大暴击
	random_value = random.randint(1, 10000)
	if random_value < GoldCrit2:
		isCrit2 = True
	else:
		if random_value < GoldCrit1:
			addExp = addExp * GoldTimes1
			isCrit1 = True
	if isCrit2 == True:
		if config.NextID and config.NextID not in mountMgr.MountId_list:
			role.SetI32(EnumInt32.MountExp, config.totalExp)
			role.SendObj(Mount_Metempsychosis_for_client,config.NextID )
			role.SendObj(Mount_EvolveBig_Crit_Prompt, evolveId)
			return
		role.IncI16(EnumInt16.MountEvolveID, 1)
	else:
		exp = role.GetI32(EnumInt32.MountExp)
		#增加经验
		temp_exp = role.GetI32(EnumInt32.MountTempExp)
		nowExp = exp + addExp + temp_exp
		levelUpExp = config.totalExp
		#是否可以升级
		if nowExp >= levelUpExp:
			nextConfig = config
			while nowExp >= levelUpExp:
				if nextConfig.NextID:#可转生
					#将经验设为满经验
					role.SetI32(EnumInt32.MountExp, levelUpExp)
					role.SendObj(Mount_Metempsychosis_for_client,nextConfig.NextID )					
					#通知客户端提示信息
					if isCrit1 is True:
						role.SendObj(Mount_Evolve_Crit_Prompt, addExp)
					elif isCrit2 is True:
						role.SendObj(Mount_EvolveBig_Crit_Prompt, role.GetI16(EnumInt16.MountEvolveID))
					else:
						role.SendObj(Mount_Evolve_Prompt, addExp)
					#假如有临时经验，清0
					if temp_exp > 0:
						role.SetI32(EnumInt32.MountTempExp, 0)
					#专题活动相关
					if moneyType != 1:
						ProjectAct.GetFunByType(EnumProActType.ProjectMountEvent, [role, 1])
					#北美通用活动
					if Environment.EnvIsNA():
						HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
						HalloweenNAMgr.mount_train(moneyType, 1)
					return
				#进化到下一个层次
				role.IncI16(EnumInt16.MountEvolveID, 1)
			
				nowExp -= levelUpExp
				if temp_exp > 0:#有临时经验值
					nowExp = max(nowExp -temp_exp, 0)
					role.SetI32(EnumInt32.MountTempExp, 0)
				nextConfig = MountConfig._MOUNT_EVOLVE.get(role.GetI16(EnumInt16.MountEvolveID))
				if not nextConfig:
					break
				levelUpExp = nextConfig.totalExp
			mountMgr.ResetAttribute()
			role.ResetGlobalMountProperty()
			SendAttriClient(role)
			#设置剩余的经验
			role.SetI32(EnumInt32.MountExp, nowExp)
			MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
			newconfig = MountConfig._MOUNT_EVOLVE.get(MountEvolveID)
			role.Msg(2, 0, GlobalPrompt.SUC_EVOLVE_MSG % (newconfig.level, newconfig.starNum))
		else:
			role.IncI32(EnumInt32.MountExp, addExp)
	
	#通知客户端提示信息
	if isCrit1 is True:
		role.SendObj(Mount_Evolve_Crit_Prompt, addExp)
	elif isCrit2 is True:
		role.SendObj(Mount_EvolveBig_Crit_Prompt, role.GetI16(EnumInt16.MountEvolveID))
	else:
		role.SendObj(Mount_Evolve_Prompt, addExp)
	#专题活动相关
	if moneyType != 1:
		ProjectAct.GetFunByType(EnumProActType.ProjectMountEvent, [role, 1])
		
	#版本判断
	if Environment.EnvIsNA():
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.mount_train(moneyType, 1)
	elif Environment.EnvIsRU():
		#七日活动
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		#坐骑养成
		sevenActMgr.mount_train(1)
		
def OnMount(role, mountId):
	'''
	骑乘坐骑
	@param role:
	@param mountId:
	'''
	
	if not mountId:
		return
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if mountId not in  mountMgr.MountId_list:
		return
	
	baseConfig = MountConfig._MOUNT_BASE.get(mountId)
	if not baseConfig:
		print "GE_EXC, can not find role(%s) mountId:(%s) Config in _MOUNT_BASE in OnMount, " % (role.GetRoleID(), mountId)
		return
	
	#当前点是否可以走动
	if role.MustFlying():
		#提示
		role.Msg(2, 0, GlobalPrompt.MOUNT_PROMPT_2)
		return		
	role.SetFly(0)
	
	role.SetRightMountID(mountId)
	role.SetI8(EnumInt8.LastMountID, mountId)
	#修改移动速度
	role.SetMountSpeed(baseConfig.moveSpeed)
	mountMgr.ResetAttribute()
#	#主角坐骑属性需要重算
	role.ResetGlobalMountProperty()
	
def OffMount(role):
	role.SetRightMountID(0)
	#还原飞行状态
	role.SetFly(0)
	#还原移动速度
	role.SetMountSpeed(0)
	
def GetAttribute(role):
	'''
	获取玩家坐骑所加的属性
	@param role:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	return mountMgr.GetAttribute()

def GetAppAttrubute(role):
	'''
	获取玩家坐骑外形品质加的属性
	@param role:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	return mountMgr.GetAppAttribute()

def SendMsgClient(role):
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	#获取食物加的属性
	FoodAttribute = mountMgr.GetAttributeFood()
	SendAttriClient(role)
	role.SendObj(Mount_Eat_Food_Suc, FoodAttribute)
#=============客户端消息处理======================
def RequestMountPanel(role, msg):
	'''
	打开坐骑面板
	@param role:
	@param msg:
	'''
	backFunId, _ = msg
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	#获取食物加的属性
	FoodAttribute = mountMgr.GetAttributeFood()
	#坐骑进化ID
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, can not find role(%s) evolveId:(%s) Config in _MOUNT_EVOLVE in MountEvolve337, " % (role.GetRoleID(), evolveId) 
		return	
	need_exp = config.totalExp
	exp = role.GetI32(EnumInt32.MountExp)	
	if config.NextID and need_exp == exp:
		role.SendObj(Mount_Metempsychosis_for_client,config.NextID )
	#回调客户端
	role.CallBackFunction(backFunId, [mountMgr.MountId_list,FoodAttribute])

def RequestMountApperancePanel(role, msg):
	'''
	请求打开坐骑外形品质面板
	@param role:
	@param msg:
	'''
	backId, _ = msg
	
	if role.GetLevel() < EnumGameConfig.MountApperanceGradeLv:
		return
	
	role.CallBackFunction(backId, role.GetTempObj(EnumTempObj.MountMgr).MountAGDict)
	
def RequestMountEvolve(role, msg):
	'''
	客户端请求坐骑培养
	@param role:
	@param msg:
	'''
	moneyType = msg
	#日志
	with TraMountEvolve:
		if 3 == moneyType:
			SeniorMountEvolve(role)
		else:
			MountEvolve(role, moneyType)

def RequestMountOnOff(role, msg):
	'''
	客户端请求坐骑骑乘或休息
	@param role:
	@param msg:
	'''
	onOrOff = msg
	
	if onOrOff == 1:
		#是否已经骑乘了坐骑
		if role.GetRightMountID():
			return
		team = role.GetTeam()
		if team and team.team_type == EnumTeamType.T_LostScene:
			#迷失之境不能上坐骑
			return
		OnMount(role, role.GetI8(EnumInt8.LastMountID))
	elif onOrOff == 0:
		#当前没有骑乘坐骑
		if not role.GetRightMountID():
			return
		#当前点是否可以走动
		if role.MustFlying():
			#提示
			role.Msg(2, 0, GlobalPrompt.MOUNT_PROMPT_1)
			return
		OffMount(role)

def RequestMountUnreal(role, msg):
	'''
	客户端请求幻化
	@param role:
	@param msg:
	'''
	mountId = msg
	if not mountId:
		return
	OnMount(role, mountId)
	
def RequestMountMetempsychosis(role, msg):
	'''
	客户端请求转生
	@param role:
	@param msg:
	'''
	mountId = msg
	
	#坐骑进化ID
	evolveId = role.GetI16(EnumInt16.MountEvolveID)
	#坐骑初始配置属性
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, can not find role(%s) evolveId:(%s) Config in _MOUNT_EVOLVE in MountEvolve408, " % (role.GetRoleID(), evolveId)
		return
	if not config.NextID:#不存在幻化ID
		return
	if mountId != config.NextID:
		mountId = config.NextID
	need_exp = config.totalExp
	exp = role.GetI32(EnumInt32.MountExp)	
	if need_exp != exp:#没达转生要求
		return
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	
	if mountId in mountMgr.MountId_list:
		return
	with MountMetempsychosis:
		role.IncI16(EnumInt16.MountEvolveID, 1)
		role.SetI32(EnumInt32.MountExp, 0)
	#解锁
	mountMgr.MountId_list.append(mountId)
	mountMgr.ResetAttribute()
	role.ResetGlobalMountProperty()
	OnMount(role, mountId)
	SendAttriClient(role)
	role.SendObj(Mount_Advanced_for_client, mountId)
	role.SendObj(Mount_Send_Unreal, mountMgr.MountId_list)
	cfg = MountConfig._MOUNT_BASE.get(mountId)
	if not cfg:
		return
	#各版本判断
	if Environment.EnvIsNA():
		#进化成狼不提示
		if mountId == 2:
			return
		cRoleMgr.Msg(3, 0, GlobalPrompt.SUC_ADVANCE % (role.GetRoleName(), cfg.mountName))
	else:
		cRoleMgr.Msg(3, 0, GlobalPrompt.SUC_ADVANCE % (role.GetRoleName(), cfg.mountName))
		
def RequestUnrealPanel(role, param):
	'''
	客户端请求打开幻化面板
	@param role:
	@param param:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	role.SendObj(Mount_Send_Unreal, mountMgr.MountId_list)
	
def RequestUpApperanceGrade(role, msg):
	'''
	请求坐骑外形品质进阶
	@param role:
	@param msg:
	'''
	backId, mountId = msg
	
	roleLevel = role.GetLevel()
	
	if roleLevel < EnumGameConfig.MountApperanceGradeLv:
		return
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	
	if mountId not in mountMgr.MountId_list:
		#没有激活这个坐骑
		return
	if mountId in mountMgr.Mount_outData_dict:
		#限时坐骑
		return
	
	#默认0阶, 0阶的不记录在字典中
	mountGrade = mountMgr.MountAGDict.get(mountId, 0)
	
	cfg = MountConfig.MountApperanceGrade_Dict.get((mountId, mountGrade))
	if not cfg:
		return
	if cfg.nextGrade == -1:
		#最高阶了
		return
	if roleLevel < cfg.needLevel:
		#等级不够
		return
	global Mount_Grade_Coding
	TimeLimitCnt = role.ItemCnt_NotTimeOut(Mount_Grade_Coding)
	if role.ItemCnt(cfg.needItemCoding) + TimeLimitCnt < cfg.needItemCnt:
		#物品不足
		return
	if role.GetI16(EnumInt16.MountEvolveID) < cfg.needevolveId:
		#坐骑进化ID不够
		return
	
	with MountApperanceUpLog:
		#删物品
		if TimeLimitCnt:
			if TimeLimitCnt >= cfg.needItemCnt:
				role.DelItem(Mount_Grade_Coding, cfg.needItemCnt)
			else:
				role.DelItem(Mount_Grade_Coding, TimeLimitCnt)
				role.DelItem(cfg.needItemCoding, cfg.needItemCnt - TimeLimitCnt)
		else:
			role.DelItem(cfg.needItemCoding, cfg.needItemCnt)
		#品阶+1
		if mountId not in mountMgr.MountAGDict:
			mountMgr.MountAGDict[mountId] = 1
		else:
			mountMgr.MountAGDict[mountId] += 1
		
		#重算属性
		mountMgr.ResetAppAttribute()
		role.ResetGlobalMountAppProperty()
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMountApperanceUp, (mountId, mountMgr.MountAGDict[mountId]))
	
	role.CallBackFunction(backId, mountMgr.MountAGDict)
	#最新活动触发,新增坐骑进化ID为0
	LatestActivityMgr.GetFunByType(EnumLatestType.MountGrade_Latest, role)
	
	role.Msg(2, 0, GlobalPrompt.MOUNT_APPERANCE_UP)


def OnExchangeMount(role, msg):
	'''
	坐骑系统_请求兑换激活坐骑
	@param msg:targetMountId 
	'''
	targetMountId = msg
	mountExchangeCfg = MountConfig.MOUNT_EXCHANGE_DICT.get(targetMountId)
	if not mountExchangeCfg:
		return
	
	#所需道具不足
	needItemCoding, needItemCnt = mountExchangeCfg.needItemCoding, mountExchangeCfg.needItemCnt
	if role.ItemCnt(needItemCoding) < needItemCnt:
		return
	
	#已经解锁了
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if targetMountId in mountMgr.MountId_list:
		return
	
	with Tra_Mount_ExchangeMount:
		#扣除道具
		role.DelItem(needItemCoding, needItemCnt)
		#增加坐骑
		role.AddMount(targetMountId)
		#log
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMountExchange, (targetMountId, mountMgr.MountId_list))
	
	#同步最新解锁坐骑列表 增加坐骑之后mountMgr改变 需要重新获取
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	role.SendObj(Mount_Send_Unreal, mountMgr.MountId_list)
#==============================================================
# 注册函数
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	#设置坐骑管理器
	role.SetTempObj(EnumTempObj.MountMgr, MountBase.MountMgr(role))

def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if mountMgr:
		mountMgr.save()

def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	mountId = role.GetRightMountID()
	if not mountId:
		return
	
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	if mountId not in mountMgr.MountId_list:
		return
	
	baseConfig = MountConfig._MOUNT_BASE.get(mountId)
	if not baseConfig:
		print "GE_EXC, can not find role(%s) mountId:(%s) Config in _MOUNT_BASE in OnMount, " % (role.GetRoleID(), mountId)
		return
	
	role.SetFly(0)
	
	role.SetRightMountID(mountId)
	role.SetI8(EnumInt8.LastMountID, mountId)
		
	#修改移动速度
	role.SetMountSpeed(baseConfig.moveSpeed)
	SendAttriClient(role)
	#检测坐骑是否过期
	CheckOutData(role)
	
def RoleDayClear(role, param):
	#假如有临时经验，清0
	if role.GetI32(EnumInt32.MountTempExp) > 0:
		role.SetI32(EnumInt32.MountTempExp, 0)
	#玩家每日清理
	CheckOutData(role)
	
def CheckOutData(role):
	'''
	检测坐骑是否过期
	@param role:
	'''
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	
	nowDays = cDateTime.Days()
	roleMountId = role.GetRightMountID()
	delMountIdList = []	#需要删除的坐骑列表
	
	for mountId in mountMgr.MountId_list:
		
		baseConfig = MountConfig._MOUNT_BASE.get(mountId)
		if not baseConfig:
			print "GE_EXC, can not find role(%s) mountId:(%s) Config in _MOUNT_BASE in OnMount, " % (role.GetRoleID(), mountId)
			continue
		
		if not baseConfig.timeLimit:#无时限
			continue
		
		if mountId not in mountMgr.Mount_outData_dict:#坐骑ID不在过期字典里
			continue
		
		#先要处理了首冲坐骑才继续处理其他的限时坐骑
		if mountId == EnumGameConfig.FirstPayMountId:
			TreatFirstPayMount(role, mountId)
		
		if mountId in mountMgr.Mount_outData_dict and mountMgr.Mount_outData_dict[mountId] <= nowDays:#过期了
			#加入删除列表
			delMountIdList.append(mountId)
			if mountId == roleMountId:#玩家正在骑乘
				OffMount(role)
				#特殊处理
				role.SetI8(EnumInt8.LastMountID, 1)
				
	if delMountIdList:#有过期的坐骑
	
		for mountId in delMountIdList:
			mountMgr.MountId_list.remove(mountId)
			del mountMgr.Mount_outData_dict[mountId]
			#加入历史过期时限列表
			mountMgr.history_outData_mountId.add(mountId)
			
		#主角坐骑属性需要重算
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
	
		with OutDateMount:
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMountOutDate, delMountIdList)
	
	role.SendObj(Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
	
def TreatFirstPayMount(role, mountId):
	#处理首冲坐骑
	firstPayMountData = role.GetObj(EnumObj.FirstPayBoxDay).get(mountId)
	if not firstPayMountData:
		print 'GE_EXC, RoleDayClear FirstPayBox mount error role(%s)' % role.GetRoleID()
		return
	
	#不连续
	if not firstPayMountData[3]:
		return
	
	nowDays = cDateTime.Days()
	if nowDays == firstPayMountData[2]:
		return
	
	if nowDays != (firstPayMountData[2] + 1):
		#不连续了
		firstPayMountData[3] = 0
		return
	
	#今日天数
	firstPayMountData[2] = nowDays
	
	pastDays = nowDays - firstPayMountData[1]
	if pastDays >= 6:
		#从使用道具后的第七天就获得
		#七天了, 将坐骑变成永久坐骑
		ChangeMountTime(role, mountId)
		firstPayMountData[3] = 0
	
def SyncRoleOtherData(role, param):
	#同步坐骑属性
	SendAttriClient(role)
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	#同步限时坐骑
	role.SendObj(Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
	
#	role.SendObj(Mount_Syn_Time, mountMgr.MountAGDict)
	
def SendAttriClient(role):
	attribute = GetAttribute(role)
	role.SendObj(Mount_Send_Attribute, attribute)
	
def AfterLevelUp(role, param):
	'''
	玩家升级
	@param role:
	@param param:
	'''
	level = role.GetLevel()
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	mountList = mountMgr.MountId_list
	if EnumGameConfig.ACTIVE_MOUNT_LEVLE <= level and not mountList:
		AddDefaultMount(role)

def AfterChangeMountID(role, oldValue, newValue):
	Event.TriggerEvent(Event.Eve_AfterMountEvolve, role, (oldValue, newValue))
	
	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.mount_train()
	
	
if "_HasLoad" not in dir():	
	#角色初始化
	Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
	#角色登陆
	Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
	#角色保存
	Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
	#玩家升级
	Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	cRoleDataMgr.SetInt16Fun(EnumInt16.MountEvolveID, AfterChangeMountID)
	#消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_Open_Mount_Panel", "客户端请求打开坐骑面板"), RequestMountPanel)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_Evolve", "客户端请求坐骑培养"), RequestMountEvolve)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_On_Off", "客户端请求坐骑骑乘或休息"), RequestMountOnOff)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_Unreal", "客户端请求幻化坐骑"), RequestMountUnreal)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_Metempsychosis", "客户端请求转生"), RequestMountMetempsychosis)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_Open_Unreal_Panel", "客户端请求打开坐骑幻化面板"), RequestUnrealPanel)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_UpApperanceGrade", "客户端请求坐骑外形品质进化"), RequestUpApperanceGrade)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_Open_Mount_ApperancePanel", "客户端请求打开坐骑外形品质面板"), RequestMountApperancePanel)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mount_OnExchangeMount", "坐骑系统_请求兑换激活坐骑"), OnExchangeMount)
	
	
