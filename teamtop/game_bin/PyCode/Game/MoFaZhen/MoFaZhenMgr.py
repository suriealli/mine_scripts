#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.MoFaZhen.MoFaZhenMgr")
#===============================================================================
# 魔法阵 mgr
#===============================================================================
import cRoleMgr
import cProcess
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Item import ItemMsg
from Game.Role.Obj import Base
from Game.MoFaZhen import MoFaZhenConfig
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Role import Event

if "_HasLoad" not in dir():
	
	Tra_MFZ_UpgradeMagicSpirit = AutoLog.AutoTransaction("Tra_MFZ_UpgradeMagicSpirit", "魔法阵_魔灵升级")
	Tra_MFZ_RefreshMagicSpirit = AutoLog.AutoTransaction("Tra_MFZ_RefreshMagicSpirit", "魔法阵_魔灵洗练")
	
	MFZ_PutOnOK_Role_S = AutoMessage.AllotMessage("MFZ_PutOnOK_Role_S", "魔法阵_同步角色成功穿上一个魔灵")
	MFZ_PutOnOK_Hero_S = AutoMessage.AllotMessage("MFZ_PutOnOK_Hero_S", "魔法阵_同步英雄成功穿上一个魔灵")
	
	MFZ_UpgradeOk_S = AutoMessage.AllotMessage("MFZ_UpgradeOk_S", "魔法阵_同步魔灵升级成功")
	
	MFZ_RefreshOk_S = AutoMessage.AllotMessage("MFZ_RefreshOk_S", "魔法阵_同步魔灵洗练成功")
	
	MFZ_RefreshSaveOk_S = AutoMessage.AllotMessage("MFZ_RefreshSaveOk_S", "魔法阵_同步魔灵洗练保存成功")
	
	MFZ_MagicSpiritSkill_S = AutoMessage.AllotMessage("MFZ_MagicSpiritSkill_S", "魔法阵_同步当前携带技能")
	
	MFZ_MagicSpiritSkill_All_S = AutoMessage.AllotMessage("MFZ_MagicSpiritSkill_All_S", "魔法阵_同步所有英雄主角携带技能")
	
#### 客户端请求 start
def OnPutOnMagicSpiritRole(role, msg):
	'''
	魔法阵_请求角色穿上魔灵
	@param role:
	@param msg:魔灵ID
	'''
	msId = msg
	
	#等级不足魔法阵
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.MFZ_NeedLevel:
		return

	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	#一定要在背包查找这个魔灵
	magicSpirit = packMgr.FindProp(msId)
	if not magicSpirit:
		return
	
	if magicSpirit.Obj_Type != Base.Obj_Type_MagicSpirit:
		#竟然不是魔灵?
		return
	
	#等级不足已穿戴
	if roleLevel < magicSpirit.cfg.needlevel:
		return
	
	#这件魔灵需要放置的位置
	posType = magicSpirit.cfg.magicSpiritType
	if posType < 1 or posType > 6:
		print "GE_EXC, OnPutOnMagicSpiritRole error pos (%s)" % posType
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	magicSpiritIdSet = role.GetObj(EnumObj.En_RoleMagicSpirits)
	roleMagicSpiritMgr = role.GetTempObj(EnumTempObj.enRoleMagicSpiritMgr)
	#看看原来的位置是否已经佩戴了一件魔灵
	magicSpirit_2 = None
	for ms in roleMagicSpiritMgr.objIdDict.values():
		if ms.cfg.magicSpiritType == posType:
			magicSpirit_2 = ms
			break
	#1.脱下原来魔灵
	if magicSpirit_2:
		#1.1从 角色魔灵背包 移出 magicSpirit_2  
		magicSpiritIdSet.discard(magicSpirit_2.oid)
		RemoveMagicSpirit(roleMagicSpiritMgr, magicSpirit_2)
		
		#1.2移入 magicSpirit_2 到 角色物品背包
		packIdSet.add(magicSpirit_2.oid)
		InsertMagicSpirit(packMgr, magicSpirit_2)
		#1.3穿戴者
		magicSpirit_2.owner = None
		
		#同步客户端，身上的魔灵脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, magicSpirit_2.oid)
	
	#2.穿上新的魔灵
	#2.1从 角色物品背包 移出 magicSpirit
	packIdSet.discard(msId)
	RemoveMagicSpirit(packMgr, magicSpirit)
	
	#2.2移入 magicSpirit 到 角色魔灵背包
	magicSpiritIdSet.add(msId)
	InsertMagicSpirit(roleMagicSpiritMgr, magicSpirit)
	#2.3穿戴者
	magicSpirit.owner = role
	
	#重算属性
	role.GetPropertyGather().ResetRecountMagicSpiritFlag()
	#更新 魔法阵技能携带状态 
	magicSpirit.owner.UpdateAndSyncMFZSkillPassive()
	
	#同步穿魔灵成功
	role.SendObj(MFZ_PutOnOK_Role_S, msId)

def OnPutOffMagicSpiritRole(role, msg):
	'''
	魔法阵_请求角色脱下魔灵
	@param role:
	@param msg:魔灵ID
	'''
	
	msId = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#背包满了
	if role.PackageIsFull():
		return
	
	#双验证魔灵是否穿在角色魔灵背包
	roleMagicSpiritMgr = role.GetTempObj(EnumTempObj.enRoleMagicSpiritMgr)
	magicSpirit = roleMagicSpiritMgr.FindProp(msId)
	if not magicSpirit:
		return
	
	magicSpiritIdSet = role.GetObj(EnumObj.En_RoleMagicSpirits)
	if msId not in magicSpiritIdSet:
		return
	
	#1.在角色魔灵背包中移除该魔灵
	magicSpiritIdSet.discard(msId)
	RemoveMagicSpirit(roleMagicSpiritMgr, magicSpirit)
	
	#2.在角色物品背包中添加该魔灵
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	packIdSet.add(msId)
	InsertMagicSpirit(role.GetTempObj(EnumTempObj.enPackMgr), magicSpirit)
	#3.穿戴者
	oldOwner = magicSpirit.owner
	magicSpirit.owner = None
	
	#重算属性
	role.GetPropertyGather().ResetRecountMagicSpiritFlag()
	
	#更新 魔法阵技能携带状态 （脱下魔灵会导致魔法阵技能等级变化）
	oldOwner.UpdateAndSyncMFZSkillPassive()

	#同步客户端 身上的魔灵脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, msId)
	
def OnPutOnMagicSpiritHero(role, msg):
	'''
	魔法阵_请求英雄穿上魔灵
	@param role:
	@param msg:(heroId, msId)
	'''
	heroId, msId = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#英雄不存在
	hero = role.GetHero(heroId)
	if not hero : 
		return
	
	#英雄未上阵
	if not hero.GetStationID():
		return
	
	#英雄魔灵管理器
	heroMagicSpiritMgr = hero.GetMagicSpiritMgr()
	if not heroMagicSpiritMgr: 
		return
	
	#角色物品背包中不存在该物品 or 该物品不是魔灵
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	magicSpirit= packMgr.FindProp(msId)
	if not magicSpirit:
		return
	
	if magicSpirit.Obj_Type != Base.Obj_Type_MagicSpirit:
		return
	
	#这件魔灵需要放置的位置
	posType = magicSpirit.cfg.magicSpiritType
	if posType < 1 or posType > 6:
		return
	
	#英雄等级不足佩戴
	if role.GetLevel() < magicSpirit.cfg.needlevel:
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	magicSpiritIdSet = role.GetObj(EnumObj.En_HeroMagicSpirits).get(heroId)
	
	##看看原来的位置是否已经佩戴了一件魔灵
	magicSpirit_2 = None
	for ms in heroMagicSpiritMgr.objIdDict.values():
		if ms.cfg.magicSpiritType == posType:
			magicSpirit_2 = ms
			break
	#1.脱下原来魔灵
	if magicSpirit_2:
		#1.1从英雄魔灵背包 移出 magicSpirit_2 
		magicSpiritIdSet.discard(magicSpirit_2.oid)		
		RemoveMagicSpirit(heroMagicSpiritMgr, magicSpirit_2)
		#1.2 移入 magicSpirit_2 到 角色物品背包
		packIdSet.add(magicSpirit_2.oid)		
		InsertMagicSpirit(packMgr, magicSpirit_2)
		#1.3 穿戴者
		magicSpirit_2.owner = None
		
		#同步英雄身上的魔灵脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, magicSpirit_2.oid)
	
	#2.穿上新的魔灵 
	#2.1 从 角色物品背包 移出  magicSpirit
	packIdSet.discard(msId)
	RemoveMagicSpirit(packMgr, magicSpirit)
	#2.2 移入 magicSpirit 到  英雄魔灵背包
	magicSpiritIdSet.add(msId)
	InsertMagicSpirit(heroMagicSpiritMgr, magicSpirit)
	#2.3 穿戴者
	magicSpirit.owner = hero
	
	#重算属性Flag
	hero.GetPropertyGather().ResetRecountMagicSpiritFlag()
	#更新 魔法阵技能携带状态 
	magicSpirit.owner.UpdateAndSyncMFZSkillPassive()
	#同步穿戴成功
	role.SendObj(MFZ_PutOnOK_Hero_S, (heroId, msId))

def OnPutOffMagicSpiritHero(role, msg):
	'''
	魔法阵_请求英雄脱下魔灵
	@param role:
	@param msg:(英雄ID, 魔灵ID)
	'''
	heroId, msId = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#背包满了
	if role.PackageIsFull():
		return
	
	#没有此英雄
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	heroMagicSpiritMgr = hero.GetMagicSpiritMgr()
	if not heroMagicSpiritMgr:
		return
	
	#双验证 英雄没有穿戴对应魔灵
	magicSpirit = heroMagicSpiritMgr.FindProp(msId)
	if not magicSpirit:
		return
	
	magicSpiritIdSet = role.GetObj(EnumObj.En_HeroMagicSpirits).get(heroId)
	if msId not in magicSpiritIdSet: 
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	#1. 从 英雄魔灵背包  移出  magicSpirit
	magicSpiritIdSet.discard(msId)
	RemoveMagicSpirit(heroMagicSpiritMgr, magicSpirit)
	#2. 移入 magicSpirit 到 角色物品背包
	packIdSet.add(msId)
	InsertMagicSpirit(role.GetTempObj(EnumTempObj.enPackMgr), magicSpirit)
	#3. 穿戴者
	oldOwner = magicSpirit.owner
	magicSpirit.owner = None
	
	#重算属性Flag
	hero.GetPropertyGather().ResetRecountMagicSpiritFlag()
	#更新 魔法阵技能携带状态 
	oldOwner.UpdateAndSyncMFZSkillPassive()
	#同步客户端身上的魔灵脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, msId)

def OnUpgradeMagicSpirit(role, msg):
	'''
	魔法阵_请求升级魔灵
	@param role:
	@param msg:魔灵ID
	'''
	msId = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#是否存在该魔灵
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	magicSpirit = globaldict.get(msId)
	if not magicSpirit:
		return
	
	if magicSpirit.Obj_Type != Base.Obj_Type_MagicSpirit:
		return
	
	#该魔灵是否可升级
	curMagicSpiritCoding = magicSpirit.otype
	cfg = magicSpirit.cfg
	if not cfg:
		return
	
	if not cfg.nextLevelID:
		return
	
	#未穿戴的魔灵
	if not magicSpirit.owner:
		return
	
	#升级材料是否足够  (辅助材料+低阶魔灵)
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	needItem =  cfg.needItem
	needItemEx =  cfg.needItemEx
	if needItem:
		if packageMgr.ItemCnt(needItem[0]) < needItem[1]:
			return
	if needItemEx:
		if packageMgr.ItemCnt(needItemEx[0]) < needItemEx[1]:
			return
	
	#高阶魔灵是否存在
	nextMagicSpiritCoding = cfg.nextLevelID 
	fun = Base.Obj_Type_Fun.get(nextMagicSpiritCoding)
	if not fun:
		print "GE_EXC, UpGrademagicSpirit can not find fun , coding = (%s)" % nextMagicSpiritCoding
		return
	
	with Tra_MFZ_UpgradeMagicSpirit:
		#扣物品
		if needItem:
			role.DelItem(*needItem)
		if needItemEx:
			role.DelItem(*needItemEx)
			
		owner = magicSpirit.owner
		
		owerId = 0
		mgr = magicSpirit.package
		
		magicSpiritIdSet = None
		if mgr.heroId:
			owerId = mgr.heroId
			magicSpiritIdSet = role.GetObj(mgr.ObjEnumIndex).get(owerId)
		else:
			owerId = role.GetRoleID()
			magicSpiritIdSet = role.GetObj(mgr.ObjEnumIndex)
			
		#删除旧魔灵
		magicSpiritIdSet.discard(msId)
		RemoveMagicSpirit(mgr, magicSpirit)
		#穿戴者
		magicSpirit.owner = None
		#全局管理器删除记录
		del globaldict[msId]

		#构建数据对象
		newId = cProcess.AllotGUID64()
		obj = newId, nextMagicSpiritCoding, 1, {}
		#根据注册函数，数据对象，生成物品对象
		newMagicSpirit = fun(role, obj)
		
		newMagicSpirit.package = mgr
		newMagicSpirit.AfterCreate()
			
		#获得新魔灵
		magicSpiritIdSet.add(newId)
		InsertMagicSpirit(mgr, newMagicSpirit)
		#穿戴者
		newMagicSpirit.owner = owner
		#加入全局管理器
		globaldict[newId] = newMagicSpirit	
		
		#升级成功 保留（技能点类型+技能点值+ 属性类型） 根据新等级更新对应属性值
		newMagicSpirit.SetSavedRefreshSkillPoint(magicSpirit.GetSavedRefreshSkillPoint())
		newMagicSpirit.SetUnSavedRefreshSkillPoint(magicSpirit.GetUnSavedRefreshSkillPoint())
		
		#已保存的属性升级
		oldSavedProType, oldSavedProValue = magicSpirit.GetSavedRefreshPro()
		newSavedProValue = newMagicSpirit.cfg.GetProValueByProType(oldSavedProType)
		if newSavedProValue is None:
			print "GE_EXC, OnUpgradeMagicSpirit newSavedProValue(%s) with oldSavedProType(%s) by magicSpirit.cfg(%s),role(%s)" % (newSavedProValue, oldSavedProType, magicSpirit.cfg.coding, role.GetRoleID())
			#保险起见 进来这里了 暂时保持不变先
			newSavedProValue = oldSavedProValue
		newMagicSpirit.SetSavedRefreshPro([oldSavedProType, newSavedProValue])
		
		#未保存的属性升级
		oldUnSavedProList = magicSpirit.GetUnSavedRefreshPro()
		if len(oldUnSavedProList) == 2:
			oldUnSavedProType, oldUnSavedProValue = oldUnSavedProList
			newUnSavedProValue = newMagicSpirit.cfg.GetProValueByProType(oldUnSavedProType)
			if newUnSavedProValue is None:
				print "GE_EXC, OnUpgradeMagicSpirit newUnSavedProValue(%s) with oldUnSavedProType(%s) by magicSpirit.cfg(%s),role(%s)" % (newSavedProValue, oldUnSavedProType, magicSpirit.cfg.coding, role.GetRoleID())
				#保险起见 进来这里了 暂时保持不变先
				newUnSavedProValue = oldUnSavedProValue
			newMagicSpirit.SetUnSavedRefreshPro([oldUnSavedProType, newUnSavedProValue])
		
		#重算属性
		newMagicSpirit.owner.GetPropertyGather().ResetRecountMagicSpiritFlag()
		#记录日志
		if len(oldUnSavedProList) == 2:
			AutoLog.LogObj(role.GetRoleID(), AutoLog.eveMagicSpiritUpgrade, newId, newMagicSpirit.otype, newMagicSpirit.oint, newMagicSpirit.odata, (msId, curMagicSpiritCoding, oldSavedProValue, oldUnSavedProValue))
		else:
			AutoLog.LogObj(role.GetRoleID(), AutoLog.eveMagicSpiritUpgrade, newId, newMagicSpirit.otype, newMagicSpirit.oint, newMagicSpirit.odata, (msId, curMagicSpiritCoding, oldSavedProValue, 0))
		#同步客户端
		role.SendObj(MFZ_UpgradeOk_S, (newId, msId, owerId, newMagicSpirit.GetSyncData(), ))

def OnRefreshPro(role, msg):
	'''
	魔法阵_请求洗练魔灵属性
	@param role:
	@param msg: msId
	'''
	msId = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#物品不存在 or 不是 魔灵
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	magicSpirit = globaldict.get(msId)
	if not magicSpirit:
		return
	
	if magicSpirit.Obj_Type != Base.Obj_Type_MagicSpirit:
		return
	
	#未穿戴的魔灵
	if not magicSpirit.owner:
		return
	
	#魔灵刷新石不足
	if role.ItemCnt(EnumGameConfig.MFZ_RefreshCoding) < 1:
		return
	
	oldProList = magicSpirit.GetUnSavedRefreshPro()
	oldSPList = magicSpirit.GetUnSavedRefreshSkillPoint()
	
	cfg = magicSpirit.cfg
	proList = cfg.RandomPropertyList()
	spList = cfg.RandomSkillPointList()
	
	with Tra_MFZ_RefreshMagicSpirit:
		#消耗材料
		role.DelItem(EnumGameConfig.MFZ_RefreshCoding, 1)
		#先将新生成的洗练属性存到未保存属性中
		magicSpirit.SetUnSavedRefreshPro(proList)
		magicSpirit.SetUnSavedRefreshSkillPoint(spList)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMagicSpiritRefresh, (msId, proList, spList, oldProList, oldSPList))
	
	role.SendObj(MFZ_RefreshOk_S, (msId, proList, spList,))

def OnSaveRefreshPro(role, msg):
	'''
	魔法阵_请求保存魔灵属性
	@param role:
	@param msg: msId
	'''
	msId = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#物品不存在 or 不是 魔灵
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	magicSpirit = globaldict.get(msId)
	if not magicSpirit:
		return
	
	if magicSpirit.Obj_Type != Base.Obj_Type_MagicSpirit:
		return
	
	#未穿戴的魔灵
	if not magicSpirit.owner:
		return
	
	oldProList = magicSpirit.GetSavedRefreshPro()
	oldSpList = magicSpirit.GetSavedRefreshSkillPoint()
	
	newProList = magicSpirit.GetUnSavedRefreshPro()
	newSpList = magicSpirit.GetUnSavedRefreshSkillPoint()
	
	#临时洗练属性未空的时候 不能保存 否则会出现空魔灵
	if not newProList or not newSpList:
		return
	
	with Tra_MFZ_RefreshMagicSpirit:
		#清除未保存的洗练属性
		#先将新生成的洗练属性存到未保存属性中
		magicSpirit.SetUnSavedRefreshPro([])
		magicSpirit.SetUnSavedRefreshSkillPoint([])
		magicSpirit.SetSavedRefreshPro(newProList)
		magicSpirit.SetSavedRefreshSkillPoint(newSpList)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMagicSpiritRefresh, (msId, newProList, newSpList, oldProList, oldSpList))
	
	#重算属性
	magicSpirit.owner.GetPropertyGather().ResetRecountMagicSpiritFlag()
	#更新 魔法阵技能携带状态 
	magicSpirit.owner.UpdateAndSyncMFZSkillPassive()
	#同步
	role.SendObj(MFZ_RefreshSaveOk_S, (msId, newProList, newSpList,))

def OnPutOnMagicSpiritSkillRole(role,msg):
	'''
	魔法阵_请求携带魔灵技能
	@param msg: skillType
	'''
	skillType = msg
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#当前已携带该类型技能
	roleMFZSkill = role.GetObj(EnumObj.MFZData)[1]
	if len(roleMFZSkill) > 0 and skillType == roleMFZSkill[0]:
		return
	
	#该技能类型各个等级需要的技能点{level:[st,sv],}
	needSPDict = MoFaZhenConfig.GetNeedSkillPointDict(skillType)
	if needSPDict is None:
		return
		
	#当前拥有的技能点{st:sv,}
	spDict = role.GetMFZSkillPointDict()
	
	#提取当前可携带该技能的最高等级
	skillLevel = 0
	for level, stsv in needSPDict.iteritems():
		if level > skillLevel:
			st, sv = stsv
			if st in spDict and spDict[st] >= sv:
				skillLevel = level
	
	#携带
	roleMFZSkill = [skillType,skillLevel]
	role.GetObj(EnumObj.MFZData)[1] = roleMFZSkill
	#同步最新技能携带
	role.SendObj(MFZ_MagicSpiritSkill_S, (0, roleMFZSkill))

def OnPutOffMagicSpiritSkillRole(role, msg = None):
	'''
	魔法阵_请求取消魔灵技能
	'''
	#等级不足
	if role.GetLevel() < EnumGameConfig.MFZ_NeedLevel:
		return
	
	#当前未携带任何类型技能
	roleMFZSkill = role.GetObj(EnumObj.MFZData)[1]
	if len(roleMFZSkill) < 1:
		return
	
	#取消携带
	roleMFZSkill = []
	role.GetObj(EnumObj.MFZData)[1] = roleMFZSkill
	#同步最新技能携带
	role.SendObj(MFZ_MagicSpiritSkill_S, (0, roleMFZSkill))

def OnPutOnMagicSpiritSkillHero(role,msg):
	'''
	魔法阵_请求携带魔灵技能英雄
	@param msg: (heroId, skillType) 
	'''
	heroId, skillType = msg
	
	#英雄不存在
	hero = role.GetHero(heroId)
	if not hero: 
		return
	
	#英雄未上阵
	if not hero.GetStationID():
		return
	
	#当前已携带该类型技能
	heroMFZSkillDict = role.GetObj(EnumObj.MFZData)[2]
	heroMFZSkill = heroMFZSkillDict.setdefault(heroId, [])
	if len(heroMFZSkill) == 2 and skillType == heroMFZSkill[0]:
		return
	
	#该技能类型各个等级需要的技能点{level:[st,sv],}
	needSPDict = MoFaZhenConfig.GetNeedSkillPointDict(skillType)
	if needSPDict is None:
		return
		
	#当前拥有的技能点{st:sv,}
	spDict = hero.GetMFZSkillPointDict()
	
	#提取当前可携带该技能的最高等级
	skillLevel = 0
	for level, stsv in needSPDict.iteritems():
		if level > skillLevel:
			st, sv = stsv
			if st in spDict and spDict[st] >= sv:
				skillLevel = level
	
	#携带
	heroMFZSkill = [skillType, skillLevel]
	heroMFZSkillDict[heroId] = heroMFZSkill
	#同步最新技能携带
	role.SendObj(MFZ_MagicSpiritSkill_S, (heroId, heroMFZSkill))

def OnPutOffMagicSpiritSkillHero(role,msg):
	'''
	魔法阵_请求取消魔灵技能英雄
	@param msg: heroId 
	'''
	heroId = msg
	#英雄不存在
	hero = role.GetHero(heroId)
	if not hero: 
		return
	
	#英雄未上阵
	if not hero.GetStationID():
		return
	
	#当前未携带该类型技能
	heroMFZSkillDict = role.GetObj(EnumObj.MFZData)[2]
	if heroId not in heroMFZSkillDict:
		return
	
	#取消携带
	del heroMFZSkillDict[heroId]
	#同步最新技能携带
	role.SendObj(MFZ_MagicSpiritSkill_S, (heroId, []))

#### 辅助 start
def InsertMagicSpirit(mgr, prop):
	#管理器增加魔灵操作
	mgr.objIdDict[prop.oid] = prop
	prop.package = mgr
	
	cd_dict = mgr.codingGather.get(prop.otype)
	if not cd_dict:
		mgr.codingGather[prop.otype] = cd_dict = {}
	cd_dict[prop.oid] = prop
		
	
def RemoveMagicSpirit(mgr, prop):
	#管理器移除魔灵操作
	del mgr.objIdDict[prop.oid]
	prop.package = None
	
	cd_dict = mgr.codingGather.get(prop.otype)
	del cd_dict[prop.oid]
	if not cd_dict:
		del mgr.codingGather[prop.otype]

def RealUpdateAndSyncMFZSkill(role, hero):
	'''
	被动影响魔法阵技能状态触发
	更新并同步 角色或者英雄当前魔法阵技能
	@param role: 角色身上魔灵变化触发  not role is None  
	@param hero: 英雄身上魔灵变化触发 not hero is None
	'''
	if role:
		#主角技能点状态有变
		roleMFZSkill = role.GetObj(EnumObj.MFZData)[1]
		#没有携带魔法阵技能 无需处理
		if len(roleMFZSkill) < 1:
			return
		
		oldSkillType, oldSkillLevel = roleMFZSkill
		#old技能类型各个等级需要的技能点{level:[st,sv],}
		needSPDict = MoFaZhenConfig.GetNeedSkillPointDict(oldSkillType)
		if needSPDict is None:
			return
		
		#当前拥有的技能点{st:sv,}
		spDict = role.GetMFZSkillPointDict()
		
		#提取当前可携带该技能的最高等级
		skillLevel = 0
		for level, stsv in needSPDict.iteritems():
			if level > skillLevel:
				st, sv = stsv
				if st in spDict and spDict[st] >= sv:
					skillLevel = level
		
		if skillLevel != oldSkillLevel:
			#有变化 更新 同步
			if skillLevel > 0:
				#技能等级变化 
				roleMFZSkill = [oldSkillType, skillLevel]
				
			else:
				#取消技能携带
				roleMFZSkill = []
			#保存更新
			role.GetObj(EnumObj.MFZData)[1] = roleMFZSkill
			#同步英雄魔法阵技能
			role.SendObj(MFZ_MagicSpiritSkill_S, (0, roleMFZSkill))
	elif hero:
		#英雄技能点状态有变触发
		role = hero.role
		if not role:
			return
		
		heroId = hero.oid
		heroMFZSKillDict = role.GetObj(EnumObj.MFZData)[2]
		if heroId not in heroMFZSKillDict:
			return
		
		heroMFZSKill = heroMFZSKillDict[heroId]
		oldSkillType, oldSkillLevel = heroMFZSKill
		
		#old技能类型各个等级需要的技能点{level:[st,sv],}
		needSPDict = MoFaZhenConfig.GetNeedSkillPointDict(oldSkillType)
		if needSPDict is None:
			return
			
		#当前拥有的技能点{st:sv,}
		spDict = hero.GetMFZSkillPointDict()
		
		#提取当前可携带该技能的最高等级
		skillLevel = 0
		for level, stsv in needSPDict.iteritems():
			if level > skillLevel:
				st, sv = stsv
				if st in spDict and spDict[st] >= sv:
					skillLevel = level
		
		if skillLevel != oldSkillLevel:
			#有变化 更新 同步
			if skillLevel > 0:
				#技能等级变化 
				heroMFZSKill = [oldSkillType, skillLevel]
				heroMFZSKillDict[heroId] = heroMFZSKill
				
			else:
				#取消技能携带
				heroMFZSKill = []
				del heroMFZSKillDict[heroId]
				
			#保存更新
			role.GetObj(EnumObj.MFZData)[2] = heroMFZSKillDict
			#同步英雄魔法阵技能
			role.SendObj(MFZ_MagicSpiritSkill_S, (heroId, heroMFZSKill))
	
#### 事件 start
def OnInitRole(role, param = None):
	'''
	角色初始化
	'''
	roleMFZData = role.GetObj(EnumObj.MFZData)
	if 1 not in roleMFZData:
		roleMFZData[1] = []
	if 2 not in roleMFZData:
		roleMFZData[2] = {}
		
	if role.GetObj(EnumObj.En_RoleMagicSpirits) == {}:
		role.SetObj(EnumObj.En_RoleMagicSpirits, set())
	

def OnSyncRoleOtherData(role, param = None):
	'''
	上线同步魔法阵技能携带数据
	'''
	role.SendObj(MFZ_MagicSpiritSkill_All_S, role.GetObj(EnumObj.MFZData))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOnMagicSpirit_Role", "魔法阵_请求角色穿上魔灵"), OnPutOnMagicSpiritRole)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOffMagicSpirit_Role", "魔法阵_请求角色脱下魔灵"), OnPutOffMagicSpiritRole)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOnMagicSpirit_Hero", "魔法阵_请求英雄穿上魔灵"), OnPutOnMagicSpiritHero)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOffMagicSpirit_Hero", "魔法阵_请求英雄脱下魔灵"), OnPutOffMagicSpiritHero)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnUpgradeMagicSpirit", "魔法阵_请求升级魔灵"), OnUpgradeMagicSpirit)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnRefreshPro", "魔法阵_请求洗练魔灵属性"), OnRefreshPro)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnSaveRefreshPro", "魔法阵_请求保存魔灵属性"), OnSaveRefreshPro)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOnMagicSpiritSkillRole", "魔法阵_请求携带魔灵技能角色"), OnPutOnMagicSpiritSkillRole)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOffMagicSpiritSkillRole", "魔法阵_请求取消魔灵技能角色"), OnPutOffMagicSpiritSkillRole)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOnMagicSpiritSkillHero", "魔法阵_请求携带魔灵技能英雄"), OnPutOnMagicSpiritSkillHero)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MFZ_OnPutOffMagicSpiritSkillHero", "魔法阵_请求取消魔灵技能英雄"), OnPutOffMagicSpiritSkillHero)