#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Version")
#===============================================================================
# 角色版本
# 注意，这里是依赖于版本函数顺序的。一旦放外网了就不要删除了，修改语义要谨慎。
#===============================================================================
import traceback
import Environment
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Item import ItemConfig
from Game.Pet import PetConfig
from Game.Role.Data import EnumDisperseInt32, EnumInt1, EnumTempObj, EnumInt8, EnumInt64,\
	EnumObj, EnumInt16
from Game.Slave import SlaveOperate
from Game.SysData import WorldData
from Game.Task import TaskConfig, SubTask

#热更新修复指南
#提交代码后台先reload代码
#XRLAM("Game.Role.Version")
#手动插入列表，针对不在线玩家
#import Game.Role.Version as A
#A.VersionList.append(A.QQLZBaoXiangTimes)
#修复在线玩家,注意要调用BeforeRoleLogin而不是对应函数，不然会有问题
#import Game.Role.Version as A
#for role in GAR():
#    A.BeforeRoleLogin(role)

VersionList = []
if "_HasLoad" not in dir():
	Tra_Version = AutoLog.AutoTransaction("Tra_Version", "角色版本修复")
	
def BeforeRoleLogin(role):
	last_version = role.GetDI32(EnumDisperseInt32.Version)
	# 如果不需要升级角色数据，直接返回
	if last_version >= len(VersionList):
		return True
	try:
		with Tra_Version:
			for idx in xrange(last_version, len(VersionList)):
				fun = VersionList[idx]
				# 尝试升级角色数据
				if fun and (not fun(role)):
					print "GE_EXC fun error in Version BeforeRoleLogin"
					return False
				# 标记角色数据升级了
				role.SetDI32(EnumDisperseInt32.Version, idx + 1)
		# 所有的角色数据都升级了，返回之
		return True
	except:
		traceback.print_exc()
		return False

#===============================================================================
# 角色数据的各种版本升级,修正完毕需要返回 True
#===============================================================================
def RevertSlave(role):
	if role.GetLevel() < EnumGameConfig.SlaveNeedLevel:
		return True
	if role.GetI1(EnumInt1.SlaveInitFlag):
		return True
	SlaveOperate.InitSlave(role)
	return True



def RevertTarotPos(role):
	#命魂增加位置属性
	TM = role.GetTempObj(EnumTempObj.enTarotMgr)
	for packageId, cardDict in TM.tarotOwner_ID_Dict.iteritems():
		if packageId == 1:
			#背包里面的暂时不用
			continue
		for idx, card in enumerate(cardDict.values()):
			card.pos = idx + 1
	TM.SaveRoleTarot()
	return True

def RevertPetType(role):
	#这里做些老数据兼容，原来保存的是宠物类型，现需要改成宠物外观
	pettype = role.GetI8(EnumInt8.PetType)
	if pettype and pettype < 100:
		cfg2 = PetConfig.PET_EVOLUTION_DICT.get((pettype, 1))
		if not cfg2:
			print "GE_EXC,can not find petType(%s) and evoid=1 in OnRoleLogin roleId(%s)" % (pettype, role.GetRoleID())
			return False
		else:
			role.SetI8(EnumInt8.PetType, cfg2.shapeId)
		#取消跟随
		role.SetI64(EnumInt64.PetFollowID, 0)
		role.SetI8(EnumInt8.PetFollowType, 0)
		
	followId = role.GetI8(EnumInt8.PetFollowType)
	if followId and followId < 100:
		#取消跟随
		role.SetI64(EnumInt64.PetFollowID, 0)
		role.SetI8(EnumInt8.PetFollowType, 0)
	return True

def RevertGT(role):
	#修复地精宝库的兑换记录格式 set([coding1, coding2]) --> {coding:cnt, ...}
	exRecordObj = role.GetObj(EnumObj.GT_Record)
	if type(exRecordObj) == dict:
		return True
	if not exRecordObj:
		role.SetObj(EnumObj.GT_Record, {})
		return True
	tmpDict = {}
	for coding in exRecordObj:
		tmpDict[coding] = 1
	role.SetObj(EnumObj.GT_Record, tmpDict)
	return True

def RevertJJCByMerge(role):
	import cProcess
	if not Environment.IsQQ:
		return True
	if cProcess.ProcessID != 21:
		return True
	from Game.JJC import JJCMgr
	if role.GetLevel()<= JJCMgr.JJC_ACTIVATE_LEVEL:
		return True
	JJCMgr.OnRoleHeFu(role, None)
	return True
	
def RevertKaifuAct(role):
	if Environment.EnvIsNA():
		from Game.Activity.KaiFuAct import KaiFuActMgr
		KaiFuActMgr.ChangeMountCntOnly(role)
		return True
	return True

def RevertFashiuon(role):
	from Game.Fashion import FashionOperate
	#进行时装外形的初始化
	fashionData = role.GetTempObj(EnumTempObj.enRoleFashionMgr).GetSyncObjDict()
	FashionApeData = role.GetObj(EnumObj.SaveFashionApe)
	for _, data in fashionData.iteritems():
		coding, _, _ = data
		if not coding:
			continue
		cfg = ItemConfig.ItemCfg_Dict.get(coding)
		if not cfg:
			continue
		FashionApeData[cfg.posType] = coding
		FashionOperate.AfterChangeFashion(role, cfg.posType, coding)
	return True

def RevertFirstPayBox(role):
	if role.GetI1(EnumInt1.FirstPayBoxOpen):
		role.SetI1(EnumInt1.FirstPayBoxOpen, False)
	return True

def RevertRoleFightSkill(role):
	'''
	100级以上玩家 修复出战技能为前五个
	'''
	#100级以下的玩家没有技能进化 不会有错乱
	if role.GetLevel() < 100:
		return True
	
	#职业区分
	canProcess = True	#是否能够处理
	fightSkillList = []
	roleSkillDict = role.GetObj(EnumObj.RoleSkill)
	if role.GetCareer() == 1:
		#骑士
		#出战技能1修复为  英勇打击  or 恶魔血月斩
		if 1 in roleSkillDict :
			fightSkillList.append(1)
		elif 18 in roleSkillDict:
			fightSkillList.append(18)
		else:
			canProcess = False
		
		if 2 in roleSkillDict:
			if 19 in roleSkillDict:
				del roleSkillDict[2]
		
		#出战技能2修复为 审判 or 天使审判 
		if 2 in roleSkillDict:
			fightSkillList.append(2)
		elif 19 in roleSkillDict:
			fightSkillList.append(19)
		else:
			canProcess = False
		
		#技能3、4、5 如果存在就顺序出战
		if 3 in roleSkillDict:
			fightSkillList.append(3)
		
		if 4 in roleSkillDict:
			fightSkillList.append(4)
		
		if 5 in roleSkillDict:
			fightSkillList.append(5)
	elif role.GetCareer() == 2:
		#法师
		#出战技能1修复为  英勇打击  or 恶魔血月斩
		if 11 in roleSkillDict:
			fightSkillList.append(11)
		elif 20 in roleSkillDict:
			fightSkillList.append(20)
		else:
			canProcess = False
		
		if 12 in roleSkillDict:
			if 21 in roleSkillDict:
				del roleSkillDict[12]
		
		#出战技能2修复为 审判 or 天使审判 
		if 12 in roleSkillDict:
			fightSkillList.append(12)
		elif 21 in roleSkillDict:
			fightSkillList.append(21)
		else:
			canProcess = False
		
		#技能3、4、5 如果存在就顺序出战
		if 13 in roleSkillDict:
			fightSkillList.append(13)
		
		if 14 in roleSkillDict:
			fightSkillList.append(14)
		
		if 15 in roleSkillDict:
			fightSkillList.append(15)
	else:
		pass
	#process
	if canProcess:
		role.GetObj(EnumObj.RoleFightSkill)[1] = fightSkillList
		import Game.Fight.SkillOperate as B
		B.SyncRoleOtherData(role, None)
	else:
		print "GE_EXC,can not process role(%s) fightSkill replace to newFightSkill(%s)" % (role.GetRoleID(), fightSkillList)	
	return True

def RevertHeavenUnRMB(role):
	#重置玩家的神石转转乐
	role.SetI8(EnumInt8.HeavenUnRMBIndex2, 1)
	return True

def RevertHeavenUnRMB2(role):
	#重置玩家的神石转转乐
	if not Environment.EnvIsQQ() and not Environment.IsDevelop:
		return True
	role.SetI8(EnumInt8.HeavenUnRMBIndex2, 1)
	return True

def RevertHeavenUnRMBNA(role):
	#重置玩家的神石转转乐(北美)
	if not Environment.EnvIsNA() and not Environment.IsDevelop:
		return True
	role.SetI8(EnumInt8.HeavenUnRMBIndex2, 1)
	return True
	
def RevertSubTaskStarGirl(role):
	if Environment.EnvIsNA():
		return True
	if role.GetLevel() < 60:
		return True
	taskCfg = TaskConfig.SubTaskConfig_Dict.get(900)
	if not taskCfg:
		print "GE_EXC, RevertSubTaskStarGirl not this sub task"
		return False
	subTaskObj = role.GetObj(EnumObj.SubTaskDict)
	subTaskObj[2].add(900)
	SubTask.CheckSubTask(role, taskCfg)
	return True

def RevertZumaCnt(role):
	#重置挑战次数
	role.SetI8(EnumInt8.ZumaCnt, EnumGameConfig.ZUMA_FREE_CNT)
	return True
	
def ResetRoleContribution(role):
	#重置角色公会个人贡献
	role.SetContribution(0)
	return True


def RevertTitle(role):
	#新的称号系统数据
	titleDict = role.GetObj(EnumObj.Title)
	newDict = {1 : {}, 2 : []}
	titleData = newDict[1]
	for titleId, time in titleDict.items():
		#时间，等级，经验，星级
		titleData[titleId] = [time, 1, 0, 1]
	role.SetObj(EnumObj.Title, newDict)
	return True

def RevertFindBack(role):
	import Game.FindBack.FindBack as A
	if role.GetLevel() < A.NeedLevel:
		return True
	fbdict = role.GetObj(EnumObj.FindBackData)
	if not fbdict:
		return True
	import Game.FindBack.FindBackDefine as D
	if D.ExpFB in fbdict[1]:
		del fbdict[1][D.ExpFB]
	if D.ExpFB in fbdict[2]:
		del fbdict[2][D.ExpFB]
	return True


def RevertMarryMsg(role):
	#修复结婚信息
	marryMsg = role.GetObj(EnumObj.MarryObj).get(2)
	if not marryMsg:
		return True
	role.GetObj(EnumObj.MarryObj)[2] = {}
	role.GetObj(EnumObj.MarryObj)[4] = []
	if role.GetI8(EnumInt8.MarryStatus) == 1:
		#答应了别人的求婚, 修复自己的结婚对象ID
		answerData = role.GetObj(EnumObj.MarryObj).get(3)
		if answerData:
			role.GetObj(EnumObj.MarryObj)[1] = answerData[0]
		else:
			print "GE_EXC, Version RevertMarryMsg role:%s error" % role.GetRoleID()
			return False
	return True
	
def RevertPartyFreeHost(role):
	#修复派对免费次数
	if not role.GetI1(EnumInt1.PartyIsHost):
		return True
	role.SetI1(EnumInt1.PartyIsHost, False)
	return True

def RevertInviteReward(role):
	#替换邀请好友抽奖次数从I8到I16
	if not role.GetI8(EnumInt8.InviteReward):
		return True
	role.SetI16(EnumInt16.InviteReward, role.GetI8(EnumInt8.InviteReward))
	role.SetI8(EnumInt8.InviteReward, 0)
	return True
	
def RevertDragonSkill(role):
	#修复北美神龙技能bug,以前的代码把被动技能2501, 2502, 2503，3个被动技能当主动技能用了，
	#被动技能本应保存到DragonMgr.passive_skill_dict,结果全保存到DragonMgr.active_skill_dict里了
	if not Environment.EnvIsNA():
		return True
	DragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	skill_list = [2501, 2502, 2503]
	
	passive_skill_dict = {}
	active_skill_dict = {}
	for skillId, level in DragonMgr.active_skill_dict.iteritems():
		if skillId in skill_list:
			passive_skill_dict[skillId] = level
		else:
			active_skill_dict[skillId] = level
	DragonMgr.active_skill_dict = active_skill_dict
	DragonMgr.passive_skill_dict = passive_skill_dict
	return True

def RevertMagicSpiritPro(role):
	'''
	修复魔灵强化 将技能点数据保存到了属性数据里面的数据bug
	'''
	if (not Environment.EnvIsFT()) and (not Environment.EnvIsQQ()) and (not Environment.IsDevelop):
		return True
	
	okSet = set([1,4,5,6,7,8,9,12,13])
	globalItemMgr = role.GetTempObj(5)
	for _, obj in globalItemMgr.iteritems():
		if obj.Obj_Type == 11:
			if 29 in obj.odata:
				saveProList = obj.odata[29]
				if len(saveProList) == 2:
					if saveProList[0] not in okSet:
						newSaveProList = obj.cfg.RandomPropertyList()
						obj.odata[29] = newSaveProList
						if obj.owner:
							obj.owner.GetPropertyGather().ResetRecountMagicSpiritFlag()
	
			if 30 in obj.odata:
				unsaveProList = obj.odata[30]
				if len(unsaveProList) == 2:
					if unsaveProList[0] not in okSet:
						newUnsaveProList = obj.cfg.RandomPropertyList()
						obj.odata[30] = newUnsaveProList
						if obj.owner:
							obj.owner.GetPropertyGather().ResetRecountMagicSpiritFlag()
	return True

def RevertSuperCardsUnionFB(role):
	'''
	已经购买至尊周卡的玩家可以激活全服公会副本替身组队功能
	@param role:
	'''
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return True
	buyDays = cardsObj.get(1)
	if not buyDays:
		return True
	
	#全服开启公会副本替身组队
	WorldData.SetSuperCardsUnionFB(1)
	
	return True
	
def ReverVIPLibaoData(role):
	'''
	重置vip礼包已领取状态
	@param role:
	'''
	#其他语言版本也会重置
	VIPLibaoData = role.GetObj(EnumObj.VIPLibaoData)
	newData = {}
	newData[20] = VIPLibaoData.get(20, set())
	newData[21] = VIPLibaoData.get(21, {})
	role.SetObj(EnumObj.VIPLibaoData, newData)
	
	return True
	
def RevertFashionData(role):
	#重构时装数据，将时装上的升星和升阶祝福值移至指定数据中
	from Game.Role.Obj import Base
	
	star_bless_dict = {}	#缓存升星祝福值，同coding的祝福值只取最大
	order_bless_dict = {}	#缓存升阶祝福值，同coding的祝福值只取最大
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	for _, obj in globaldict.iteritems():
		if obj.Obj_Type != Base.Obj_Type_Fashion:
			continue
		coding = obj.cfg.coding
		#升星祝福值
		_, nowlucky = obj.GetStarData()
		if coding not in star_bless_dict:
			star_bless_dict[coding] = nowlucky
		else:
			if star_bless_dict.get(coding) < nowlucky:
				star_bless_dict[coding] = nowlucky
		#升阶祝福值
		_, lucky = obj.GetOrderData()
		if coding not in order_bless_dict:
			order_bless_dict[coding] = lucky
		else:
			if order_bless_dict.get(coding) < lucky:
				order_bless_dict[coding] = lucky
	
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	FGM = FashionGlobalMgr.fashion_active_dict
	for coding, data in FashionGlobalMgr.fashion_active_dict.items():
		#原来的格式：{0:是否鉴定, 1:时装阶数, 2:套装ID, 3:时装星数, 4:鉴定额外幸运值}
		#需要的格式：{0:是否鉴定, 1:时装阶数, 2:套装ID, 3:时装星数, 4:鉴定额外幸运值, 5:升星祝福值, 6:升阶祝福值}
		star_bless = star_bless_dict.get(coding, 0)
		order_bless = order_bless_dict.get(coding, 0)
		#重新对时装的数据格式进行初始化
		if len(data) == 4:
			FGM[coding] = [data[0], data[1], data[2], data[3], 0, star_bless, order_bless]
		else:
			FGM[coding] = [data[0], data[1], data[2], data[3], data[4], star_bless, order_bless]
	return True

def RevertEquipedFashion(role):
	#返还玩家已穿戴的时装时装之魄
	FashionIdSet = role.GetObj(EnumObj.En_RoleFashions)
	if not FashionIdSet:
		return True
	from Game.Role.Mail import Mail
	from Common.Other import GlobalPrompt
	cnt = len(FashionIdSet)
	Mail.SendMail(role.GetRoleID(), GlobalPrompt.FASHION_MAIL_TITLE2, GlobalPrompt.FASHION_MAIL_SENDER2, GlobalPrompt.FASHION_MAIL_DESC2 % cnt, \
				[(26676, cnt)])
	return True

def RevertJTCheersCnt(role):
	#重置玩家的喝彩次数
	role.SetI16(EnumInt16.JTCheersCnt, 0)
	return True
	
def QQLZBaoXiangTimes(role):
	if not Environment.EnvIsQQ():
		return True
	if role.GetI8(EnumInt8.QQLZBaoXiangTimes) == 0:
		return True
	role.GetObj(EnumObj.QQLZBaoXiang)[1] = {}
	for i in range(1, 10):
		role.GetObj(EnumObj.QQLZBaoXiang)[1][i] = None
	role.GetObj(EnumObj.QQLZBaoXiang)[2] = [0]			
	role.SetI8(EnumInt8.QQLZBaoXiangTimes, 0)
	return True

def RevertFBZJReward(role):
	#重置玩家副本通关、三星通关奖励
	if (not Environment.EnvIsFT()) and (not Environment.EnvIsQQ()) and (not Environment.IsDevelop):
		return True
	role.GetObj(EnumObj.FB_ZJReward)[1] = set()
	role.GetObj(EnumObj.FB_ZJReward)[2] = set()
	return True

def RevertNewYearObj(role):
	#修复新年活动新年砸旦和金猪的obj
	if (not Environment.EnvIsFT()) and (not Environment.EnvIsQQ()) and (not Environment.IsDevelop):
		return True
	role.SetObj(EnumObj.NewYearDayEgg, {})
	role.SetObj(EnumObj.NewYearDayPigData, {})
	return True


if "_HasLoad" not in dir():
	#必须按顺序往后面加，不能删除，也不能往中间插入,注意函数的返回值必须是True，除非逻辑有必要返回其他的值
	VersionList.append(RevertSlave)
	VersionList.append(RevertTarotPos)
	VersionList.append(RevertPetType)
	VersionList.append(RevertGT)
	VersionList.append(RevertJJCByMerge)
	VersionList.append(RevertKaifuAct)
	VersionList.append(RevertFashiuon)
	VersionList.append(RevertFirstPayBox)
	VersionList.append(RevertRoleFightSkill)
	VersionList.append(RevertHeavenUnRMB)
	VersionList.append(RevertSubTaskStarGirl)
	VersionList.append(RevertZumaCnt)
	VersionList.append(ResetRoleContribution)
	VersionList.append(RevertTitle)
	VersionList.append(RevertFindBack)
	VersionList.append(RevertMarryMsg)
	VersionList.append(RevertPartyFreeHost)
	VersionList.append(RevertInviteReward)
	VersionList.append(RevertDragonSkill)
	VersionList.append(RevertMagicSpiritPro)
	VersionList.append(RevertSuperCardsUnionFB)
	VersionList.append(ReverVIPLibaoData)
	VersionList.append(RevertFashionData)
	VersionList.append(RevertEquipedFashion)
	VersionList.append(QQLZBaoXiangTimes)
	VersionList.append(RevertHeavenUnRMB2)
	VersionList.append(RevertHeavenUnRMBNA)
	VersionList.append(RevertJTCheersCnt)
	VersionList.append(RevertFBZJReward)
	VersionList.append(RevertNewYearObj)
#===============================================================================
# 断言下列表唯一
assert len(VersionList) == len(set(VersionList))

