#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ElementSpirit.ElementBrandMgr")
#===============================================================================
# 元素印记 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Property import PropertyEnum
from Game.ElementSpirit import ElementBrandConfig
from Game.Role.Data import EnumObj, EnumTempObj, EnumInt32, EnumInt16

KEY_PACKAGE = 1
KEY_EQUIP = 2
KEY_MATERIAL = 3
KEY_SET = set([KEY_PACKAGE, KEY_EQUIP, KEY_MATERIAL])

IDX_TYPE = 0
IDX_COLOR = 1
IDX_LEVEL = 2
IDX_TALENT = 3
IDX_POS = 4
IDX_SAVEPRO = 5
IDX_UNSAVEPRO = 6

DEFAULT_LEVEL = 1
DEFALUT_POS = 0
DEFALUT_SAVEPRO = {}
DEFALUT_UNSAVEPRO = {}


if "_HasLoad" not in dir():
	
	#格式: {1:{brandId:[type,color,level,talent,pos,savePro,unsavePro],}, 2:{brandId:[type,color,level,talent,pos,savePro,unsavePro]}, 3:{(type,color,level):cnt,},}
	#其中1为背包中的印记数据 2为玩家嵌的印记数据 3为玩家背包的材料印记数据
	ElementBrand_AllData_S = AutoMessage.AllotMessage("ElementBrand_AllData_S", "元素印记_所有数据_同步")
	#格式： (targetBrandId, targetPos)
	ElementBrand_EquipBrand_S = AutoMessage.AllotMessage("ElementBrand_EquipBrand_S", "元素印记_镶嵌一个印记_同步")
	#格式： targetBrandId
	ElementBrand_UnEquipBrand_S = AutoMessage.AllotMessage("ElementBrand_UnEquipBrand_S", "元素印记_卸载一个印记_同步")
	#格式同ElementBrand_AllData_S 但是其中key：1，2，3可选 有1则表示1同步过来1的最新数据
	ElementBrand_UpdateDataByKey_S = AutoMessage.AllotMessage("ElementBrand_UpdateDataByKey_S", "元素印记_部分数据_同步") 
	
	Tra_ElementBrand_Sculpture = AutoLog.AutoTransaction("Tra_ElementBrand_Sculpture", "元素印记_雕刻")
	Tra_ElementBrand_Equip = AutoLog.AutoTransaction("Tra_ElementBrand_Equip", "元素印记_镶嵌")
	Tra_ElementBrand_UnEquip = AutoLog.AutoTransaction("Tra_ElementBrand_UnEquip", "元素印记_卸载")
	Tra_ElementBrand_ShenJi = AutoLog.AutoTransaction("Tra_ElementBrand_ShenJi", "元素印记_升级")
	Tra_ElementBrand_FenJie = AutoLog.AutoTransaction("Tra_ElementBrand_FenJie", "元素印记_分解")
	Tra_ElementBrand_WashPro = AutoLog.AutoTransaction("Tra_ElementBrand_WashPro", "元素印记_洗练") 
	Tra_ElementBrand_SavePro = AutoLog.AutoTransaction("Tra_ElementBrand_SavePro", "元素印记_保存洗练")
	Tra_ElementBrand_TransmitPro = AutoLog.AutoTransaction("Tra_ElementBrand_TransmitPro", "元素印记_继承")

#===============================================================================
# 管理类
#===============================================================================
class ElementBrandMgr(object):
	'''
	元素印记管理类
	'''
	def __init__(self, role):
		self.role = role
		#背包中的普通印记 {brandId:brandObj,}
		self.package_dict = {}
		#镶嵌的印记{brandId:brandObj,}
		self.equip_dict = {}
		#背包中的材料印记{(type,color,level):cnt,}
		self.meterial_dict = {}
		
		
		self.after_init()
	
	
	def after_init(self):
		elementBrandData = self.role.GetObj(EnumObj.ElementBrandData)
		#装载背包中的印记数据
		packageDataDict = elementBrandData.get(KEY_PACKAGE, {})
		for brandId, brandDataList in packageDataDict.iteritems():
			self.package_dict[brandId] = ElementBrand(self.role, brandId, brandDataList)
		#装载镶嵌的印记数据
		equipDataDict = elementBrandData.get(KEY_EQUIP, {})
		for brandId, brandDataList in equipDataDict.iteritems():
			self.equip_dict[brandId] = ElementBrand(self.role, brandId, brandDataList)
		#装载材料印记数据
		equipDataDict = elementBrandData.get(KEY_MATERIAL, {})
		for dataKey, brandCnt in equipDataDict.iteritems():
			self.meterial_dict[dataKey] = brandCnt

		
	def new_brand(self, brandDataList):
		'''
		获得一个新的元素印记
		@param brandDataList: [IDX_TYPE,IDX_COLOR,IDX_LEVEL,IDX_TALENT,IDX_TALENT,IDX_POS,IDX_SAVEPRO,IDX_UNSAVEPRO] 
		'''
		brandId = self.role.GetI32(EnumInt32.ElementBrandAllotID) + 1
		self.role.IncI32(EnumInt32.ElementBrandAllotID, 1)
		self.package_dict[brandId] = ElementBrand(self.role, brandId, brandDataList)
		
		return brandId
	
	
	def new_brand_meterial(self, brandType, brandColor, brandLevel, brandCnt):
		'''
		获得材料印记
		'''
		keyData = (brandType, brandColor, brandLevel)
		if keyData not in self.meterial_dict:
			self.meterial_dict[keyData] = brandCnt
		else:
			self.meterial_dict[keyData] += brandCnt
	
	
	def can_equip(self, targetBrandId, targetPos):
		'''
		印记 targetBrandId 是否可以 镶嵌到 targetPos
		'''
		#目标位置非法
		if targetPos not in ElementBrandConfig.ElementBrand_PosControl_Dict:
			return False
		
		#未解锁目标位置
		if self.role.GetI16(EnumInt16.ElementSpiritId) < ElementBrandConfig.ElementBrand_PosControl_Dict[targetPos]:
			return False
		
		#背包中是否存在该印记 
		if targetBrandId not in self.package_dict:
			return False
		
		#目标印记不可镶嵌
		targetBrandObj = self.package_dict[targetBrandId]
		if not targetBrandObj.brand_cfg.canEquip:
			return False
		
		#目标位置上已经镶嵌了印记 或者 已经镶嵌了同类型的印记
		for tmpBrandObj in self.equip_dict.values():
			if tmpBrandObj.brand_pos == targetPos or tmpBrandObj.brand_type == targetBrandObj.brand_type:
				return False
		
		return True
		
	
	def equip_brand(self, targetBrandId, targetPos):
		'''
		镶嵌目标印记 targetBrandId 到 目标位置 targetPos
		'''
		targetBrandObj = self.package_dict.get(targetBrandId, None)
		if not targetBrandObj:
			print "GE_EXC,ElementBrandMgr::equip_brand:: can not find target brand() obj in package_dict, role(%s)" % (targetBrandId, self.role.GetRoleID())
			return 
		
		#移除背包中印记
		del self.package_dict[targetBrandId]
		#镶嵌印记
		self.equip_dict[targetBrandId] = targetBrandObj
		targetBrandObj.set_pos(targetPos)
		
		#更新变化的数据
		self.role.SendObj(ElementBrand_EquipBrand_S, (targetBrandId, targetPos))
		
		#重算属性
		self.role.ResetElementBrandBaseProperty()
	
	def can_unequip(self, targetBrandId):
		'''
		是否可以卸载目标印记 targetBrandId
		'''
		if targetBrandId not in self.equip_dict:
			return False
		
		if self.get_empty_size() < 1:
			return False
		
		return True
	
	
	def unequip_brand(self, targetBrandId):
		'''
		卸载目标印记 targetBrandId
		'''
		targetBrandObj = self.equip_dict.get(targetBrandId, None)
		if not targetBrandObj:
			print "GE_EXC,unequip_brand::can not find brand(%s) obj in equip_dict,role(%s)" % (targetBrandId, self.role.GetRoleID())
			return
		
		#删除镶嵌的印记
		del self.equip_dict[targetBrandId]
		#清除印记位置数据
		targetBrandObj.set_pos(DEFALUT_POS)
		#背包中增加印记
		self.package_dict[targetBrandId] = targetBrandObj
		
		#重算属性
		self.role.ResetElementBrandBaseProperty()
		
		#同步客户端
		self.role.SendObj(ElementBrand_UnEquipBrand_S, targetBrandId)
		

	def can_shenji(self, targetBrandId):
		'''
		印记 targetBrandId 是否可以 升级
		'''
		targetBrandObj = self.package_dict.get(targetBrandId, None)
		if not targetBrandObj:
			targetBrandObj = self.equip_dict.get(targetBrandId, None)
		
		#目标印记不在背包 也 没有镶嵌
		if not targetBrandObj:
			return False
		
		#目标印记不可升级
		brandCfg = targetBrandObj.brand_cfg
		if not brandCfg.canShenJi:
			return False
		
		#升级需要普通材料不足
		if brandCfg.shenJiNeedItem:
			needCoding, needCnt = brandCfg.shenJiNeedItem
			if self.role.ItemCnt(needCoding) < needCnt:
				return False
		
		#升级需要印记不足
		if brandCfg.shenJiNeedBrandCnt:
			shenJiNeedBrandCnt, shenJiNeedBrand = brandCfg.shenJiNeedBrandCnt, brandCfg.shenJiNeedBrand
			if self.count_brand(shenJiNeedBrand, targetBrandId) < shenJiNeedBrandCnt:
				return False
		
		return True
	
	
	def shenji_brand(self, targetBrandId):
		'''
		升级目标印记
		'''
		if targetBrandId in self.package_dict:
			#升级背包中印记
			targetBrandObj = self.package_dict[targetBrandId]
		elif targetBrandId in self.equip_dict:
			#升级已镶嵌印记
			targetBrandObj = self.equip_dict[targetBrandId]
		else:
			print "GE_EXC,ElementBrandMgr::shenji_brand:: target brand() obj not in package_dict and not in equip_dict, role(%s)" % (targetBrandId, self.role.GetRoleID())
			return
	
		brandCfg = targetBrandObj.brand_cfg
		#消耗升级普通材料
		if brandCfg.shenJiNeedItem:
			self.role.DelItem(*brandCfg.shenJiNeedItem)
		#消耗升级需要印记
		isChangeMeterial = False
		isChangePackage = False
		needBrandCnt = brandCfg.shenJiNeedBrandCnt
		if needBrandCnt:
			isChangeMeterial, isChangePackage = self.del_brand(brandCfg.shenJiNeedBrand, needBrandCnt, targetBrandId)
		#印记升级
		targetBrandObj.shenji()
		
		#同步最新印记数据给客户端
		keyList = []
		if targetBrandId in self.package_dict:
			keyList.append(KEY_PACKAGE)
			if isChangeMeterial:
				keyList.append(KEY_MATERIAL)
		else:
			#重算属性
			self.role.ResetElementBrandBaseProperty()
			if isChangePackage:
				keyList.append(KEY_PACKAGE)
			if isChangeMeterial:
				keyList.append(KEY_MATERIAL)
		
		#同步变化的部分数据
		self.role.SendObj(ElementBrand_UpdateDataByKey_S, self.get_data_by_key(keyList))

	
	def can_fenjie(self, targetBrandId):
		'''
		印记 targetBrandId 是否可以 分解
		'''
		#目标是否存在印记背包中
		if targetBrandId not in self.package_dict:
			return False
		
		#目标不可分解
		targetBrandObj = self.package_dict[targetBrandId]
		brandCfg = targetBrandObj.brand_cfg
		if not brandCfg.canFenjie:
			return False
		
		#印记背包剩余空间不足
		if self.get_empty_size() < brandCfg.fenJieNeedPackageSize:
			return False
		
		#神石不足
		if self.role.GetUnbindRMB() < brandCfg.fenJieNeedRMB:
			return False
		
		return True
	
	
	def fenjie_brand(self, targetBrandId):
		'''
		分解目标印记
		'''
		if targetBrandId not in self.package_dict:
			print "GE_EXC,ElementBrandMgr::fenJie_brand::targetBrandId(%s) not in package_dict,role(%s)" % (targetBrandId, self.role.GetRoleID())
			return
		
		targetBrandObj = self.package_dict[targetBrandId]
		brandCfg = targetBrandObj.brand_cfg
		if not brandCfg.canFenjie:
			return
		
		#删除分解的印记
		del self.package_dict[targetBrandId]
		#消耗神石
		self.role.DecUnbindRMB(brandCfg.fenJieNeedRMB)
		#获得分解材料
		if brandCfg.fenJieAddItem:
			coding, cnt = brandCfg.fenJieAddItem
			self.role.AddItem(coding, cnt)
		
		isMeterialChange = False
		#获得分解材料印记
		if brandCfg.fenJieAddBrand:
			isMeterialChange = True
			for brandType, brandColor, brandLevel, brandCnt in brandCfg.fenJieAddBrand:
				self.new_brand_meterial(brandType, brandColor, brandLevel, brandCnt)
		
		return isMeterialChange
	
	
	def can_wash(self, targetBrandId, lockList, isRMBLock, isRMBStone):
		'''
		判断此次洗练条件是否满足
		@return: None 条件不满足 
		@return: [washStoneCnt, washLockCnt, washRMB] --- [消耗洗练石数量， 消耗洗练锁数量， 消耗神石数量]
		'''
		washStoneCnt = 0
		washLockCnt = 0
		washRMB = 0
		targetBrandObj = None
		if targetBrandId in self.equip_dict:
			targetBrandObj = self.equip_dict[targetBrandId]
		elif targetBrandId in self.package_dict:
			targetBrandObj = self.package_dict[targetBrandId]
		
		#目标印记不存在
		if not targetBrandObj:
			return None
		
		#参数锁定列表有不存在属性类型
		for proType in lockList:
			if proType not in targetBrandObj.brand_savePro:
				return None
		
		#全部锁定了洗个鸡巴毛啊
		if len(lockList) > 0 and len(lockList) == len(targetBrandObj.brand_savePro):
			return None
		
		#洗练石判断 材料不足时  不自动购买 或者 自动购买不够钱
		if self.role.ItemCnt(EnumGameConfig.ElementBrand_WashStoneCoding) < 1:
			if (not isRMBStone) or (isRMBStone and self.role.GetUnbindRMB() < EnumGameConfig.ElementBrand_WashStoneRMB):
				return None
			washRMB += EnumGameConfig.ElementBrand_WashStoneRMB
		else:
			washStoneCnt = 1
		
		#洗练锁判断  材料不足 不自动购买 或者自动购买不够钱
		haveLockCnt = self.role.ItemCnt(EnumGameConfig.ElementBrand_WashLockCoding)
		needLockCnt = len(lockList)
		if haveLockCnt < needLockCnt:
			if (not isRMBLock) or isRMBLock and self.role.GetUnbindRMB() < (EnumGameConfig.ElementBrand_WashLockRMB * (needLockCnt - haveLockCnt)):
				return None
			washLockCnt = haveLockCnt
			washRMB += EnumGameConfig.ElementBrand_WashLockRMB * (needLockCnt - haveLockCnt)
		else:
			washLockCnt = needLockCnt
			
		return [washStoneCnt, washLockCnt, washRMB]
	
	
	def wash_brand(self, targetBrandId, lockList, washStoneCnt, washLockCnt, washRMB):
		'''
		印记洗练 
		@param targetBrandId, lockList, washStoneCnt, washLockCnt, washRMB: 印记ID,锁定属性列表,消耗洗练石数量.消耗洗练锁数量 ，消耗神石数量
		'''
		targetBrandObj = None
		if targetBrandId in self.equip_dict:
			targetBrandObj = self.equip_dict[targetBrandId]
		elif targetBrandId in self.package_dict:
			targetBrandObj = self.package_dict[targetBrandId]
		
		#目标印记不存在
		if not targetBrandObj:
			print "GE_EXC,ElementBrandMgr::wash_brand, can not get targetBrandObj,role(%s)" % self.role.GetRoleID()
			return
		
		#扣钱
		self.role.DecUnbindRMB(washRMB)
		#扣除洗练石
		if washStoneCnt > 0:
			self.role.DelItem(EnumGameConfig.ElementBrand_WashStoneCoding, washStoneCnt)
		#扣除洗练锁
		if washLockCnt > 0:
			self.role.DelItem(EnumGameConfig.ElementBrand_WashLockCoding, washLockCnt)
		#洗练
		targetBrandObj.wash_pro(lockList)
	
	
	def can_savepro(self, targetBrandId):
		'''
		判断是否可以保存洗练属性
		'''
		targetBrandObj = None
		if targetBrandId in self.equip_dict:
			targetBrandObj = self.equip_dict[targetBrandId]
		elif targetBrandId in self.package_dict:
			targetBrandObj = self.package_dict[targetBrandId]
		
		#目标印记不存在
		if not targetBrandObj:
			return False
		
		#没有未保存的洗练属性
		brandData = targetBrandObj.get_base_data()
		if not len(brandData[IDX_UNSAVEPRO]):
			return False 
		
		return True
	
	
	def save_washpro(self, targetBrandId):
		'''
		保存洗练属性
		'''
		targetBrandObj = None
		if targetBrandId in self.equip_dict:
			targetBrandObj = self.equip_dict[targetBrandId]
		elif targetBrandId in self.package_dict:
			targetBrandObj = self.package_dict[targetBrandId]
		
		#目标印记不存在
		if not targetBrandObj:
			print "GE_EXC,ElementBrandMgr::save_washpro,can not find brand object,role(%s)" % self.role.GetRoleID()
			return
		
		#保存
		targetBrandObj.save_pro()
		#重算洗练属性
		if targetBrandId in self.equip_dict:
			self.role.ResetElementBrandBaseProperty()
	
	
	def can_transmit(self, lowBrandId, highBrandId):
		'''
		判断是否可以继承
		'''
		lowBrandObj = self.package_dict.get(lowBrandId, None)
		highBrandObj = self.package_dict.get(highBrandId, None)
		if not lowBrandObj or not highBrandObj:
			return False
		
		if lowBrandObj.get_base_data()[IDX_COLOR] > highBrandObj.get_base_data()[IDX_COLOR]:
			return False
		
		return True	
	
	
	def transmit_brand(self, lowBrandId, highBrandId):
		'''
		执行印记继承
		'''
		transmitAddItem = []
		transmitAddBrandCnt = 0
		lowBrandObj = self.package_dict.get(lowBrandId, None)
		highBrandObj = self.package_dict.get(highBrandId, None)
		if not lowBrandObj or not highBrandObj:
			print "GE_EXC,ElementBrandMgr::transmit_brand, can not find brand object,role(%s)" % self.role.GetRoleID()
			return
		
		#洗练属性继承
		highBrandObj.excute_transmit(lowBrandObj.get_savepro())
		#低阶印记删除
		del self.package_dict[lowBrandId]
		#返还被继承的印记材料
		lowBrandCfg = lowBrandObj.brand_cfg
		if lowBrandCfg.transmitAddItem:
			transmitAddItem.append(lowBrandCfg.transmitAddItem)
			self.role.AddItem(*lowBrandCfg.transmitAddItem)
			
		if lowBrandCfg.transmitAddBrand:
			for brandType, brandColor, brandLevel, brandCnt in lowBrandCfg.transmitAddBrand:
				transmitAddBrandCnt += brandCnt
				self.new_brand_meterial(brandType, brandColor, brandLevel, brandCnt)
		
		return [transmitAddItem, transmitAddBrandCnt]
	
	def get_empty_size(self):
		'''
		返回印记背包剩余空格
		'''
		return EnumGameConfig.ElementBrand_MaxPackageSize - (len(self.package_dict) + len(self.meterial_dict))
	
	
	def count_brand(self, adapterDataList, exceptBrandId):
		'''
		统计背包中除开exceptBrandId 满足adapterDataList条件的印记数量 
		adapterDataList [brandType, brandColor, brandLevel]
		'''
		totalCnt = 0
		#统计背包中普通印记
		for brandId, brandObj in self.package_dict.iteritems():
			if brandId == exceptBrandId:
				continue
			for tBrandType, tBrandColor, tBrandLevel in adapterDataList:
				if tBrandType == brandObj.brand_type and tBrandColor == brandObj.brand_color and tBrandLevel == brandObj.brand_level:
					totalCnt += 1
					break
		#统计材料印记
		for keyData, brandCnt in self.meterial_dict.iteritems():
			for adapterData in adapterDataList:
				if adapterData == keyData:
					totalCnt += brandCnt
					
		return totalCnt
	

	def del_brand(self, adapterDataList, brandCnt, exceptBrandId):
		'''
		删除背包中符合条件  adapterDataList 的印记 
		除开exceptBrandId
		'''
		tobeDelCnt = brandCnt
		packageDelSet = set()
		meterialDelDict = {}
		for adapterData in adapterDataList:
			if tobeDelCnt < 1:
				break 
			isMeterial = False
			for keyData, haveCnt in self.meterial_dict.iteritems():
				if tobeDelCnt < 1:
					break 
				if adapterData == keyData:
					isMeterial = True
					if haveCnt >= tobeDelCnt:
						meterialDelDict[keyData] = tobeDelCnt
						tobeDelCnt = 0
					else:
						meterialDelDict[keyData] = haveCnt
						tobeDelCnt -= haveCnt
			
			#材料印记数据没有处理 背包印记数据继续处理
			if not isMeterial and tobeDelCnt > 0:
				for brandId, brandObj in self.package_dict.iteritems():
					if tobeDelCnt < 1:
						break 
					if brandId == exceptBrandId:
						continue
					if adapterData == (brandObj.brand_type, brandObj.brand_color, brandObj.brand_level):
						tobeDelCnt -= 1
						packageDelSet.add(brandId)
		
		isChangeMeterial = False
		#删除材料印记数据
		for keyData, cnt in meterialDelDict.iteritems():
			isChangeMeterial = True
			if cnt < self.meterial_dict[keyData]:
				self.meterial_dict[keyData] -= cnt
			else:
				del self.meterial_dict[keyData]
		
		#删除背包印记
		isChangePackage = False
		for brandId in packageDelSet:
			isChangePackage = True
			del self.package_dict[brandId]
		
		return isChangeMeterial, isChangePackage
	
	
	def get_brand_data_by_brand_id(self, brandId):
		'''
		获取普通印记基本数据
		''' 
		if brandId in self.package_dict:
			return self.package_dict[brandId].get_base_data()
		elif brandId in self.equip_dict:
			return self.equip_dict[brandId].get_base_data()
		else:
			return []
		
	
	def get_base_pro(self):
		'''
		获取镶嵌的印记的所有属性总和
		'''
		ppt_dict = {}
		for _, brandObj in self.equip_dict.iteritems():
			brandCfg = brandObj.brand_cfg
			factor = (brandObj.brand_talent / (brandCfg.tanlentLimit * 1.0))
			if brandCfg.attack_pt:
				ppt_dict[PropertyEnum.attack_p] = ppt_dict.setdefault(PropertyEnum.attack_p, 0) + int(brandCfg.attack_pt * factor)
			if brandCfg.attack_mt:
				ppt_dict[PropertyEnum.attack_m] = ppt_dict.setdefault(PropertyEnum.attack_m, 0) + int(brandCfg.attack_mt * factor)
			if brandCfg.maxhp_t:
				ppt_dict[PropertyEnum.maxhp] = ppt_dict.setdefault(PropertyEnum.maxhp, 0) + int(brandCfg.maxhp_t * factor)
			if brandCfg.crit_t:
				ppt_dict[PropertyEnum.crit] = ppt_dict.setdefault(PropertyEnum.crit, 0) + int(brandCfg.crit_t * factor)
			if brandCfg.critpress_t:
				ppt_dict[PropertyEnum.critpress] = ppt_dict.setdefault(PropertyEnum.critpress, 0) + int(brandCfg.critpress_t * factor)
			if brandCfg.parry_t:
				ppt_dict[PropertyEnum.parry] = ppt_dict.setdefault(PropertyEnum.parry, 0) + int(brandCfg.parry_t * factor)
			if brandCfg.puncture_t:
				ppt_dict[PropertyEnum.puncture] = ppt_dict.setdefault(PropertyEnum.puncture, 0) + int(brandCfg.puncture_t * factor)
			if brandCfg.antibroken_t:
				ppt_dict[PropertyEnum.antibroken] = ppt_dict.setdefault(PropertyEnum.antibroken, 0) + int(brandCfg.antibroken_t * factor)
			if brandCfg.notbroken_t:
				ppt_dict[PropertyEnum.notbroken] = ppt_dict.setdefault(PropertyEnum.notbroken, 0) + int(brandCfg.notbroken_t * factor)
		
		return ppt_dict
	
	def get_wash_pro(self):
		'''
		获取镶嵌的印记的所有洗练属性
		'''
		p_dict = {}
		for _, brandObj in self.equip_dict.iteritems():
			PTVG = ElementBrandConfig.ElementBrand_ProTypeValue_Dict.get
			saveProDict = brandObj.get_savepro()
			for proType, percentValue in saveProDict.iteritems():
				#物攻的把发功也弄进去先 最后有根据职业剔除无用属性的逻辑维护
				if PropertyEnum.attack_p == proType:
					p_dict[PropertyEnum.attack_p] = p_dict.setdefault(PropertyEnum.attack_p, 0) + int((PTVG(proType, 0) * percentValue) / 10000.0)
					p_dict[PropertyEnum.attack_m] = p_dict.setdefault(PropertyEnum.attack_m, 0) + int((PTVG(proType, 0) * percentValue) / 10000.0)
				else:
					p_dict[proType] = p_dict.setdefault(proType, 0) + int((PTVG(proType, 0) * percentValue) / 10000.0)
					
		return p_dict
		
		
	def get_data_by_key(self, keyList):
		'''
		获取对应key的字典
		'''
		dataDict = {}
		for k in keyList:
			if k == KEY_PACKAGE:
				dataDict[KEY_PACKAGE] = {}
				for brandId, brandObj in self.package_dict.iteritems():
					dataDict[KEY_PACKAGE][brandId] = brandObj.get_base_data()
			elif k == KEY_EQUIP:
				dataDict[KEY_EQUIP] = {}
				for brandId, brandObj in self.equip_dict.iteritems():
					dataDict[KEY_EQUIP][brandId] = brandObj.get_base_data()
			elif k == KEY_MATERIAL:
				dataDict[KEY_MATERIAL] = {}
				for keyData, brandCnt in self.meterial_dict.iteritems():
					dataDict[KEY_MATERIAL][keyData] = brandCnt
				
		return dataDict
			

	def get_all_data(self):
		'''
		返回印记数据字典
		'''
		return self.get_data_by_key([KEY_PACKAGE, KEY_EQUIP, KEY_MATERIAL])
			
	
	def save_all_data(self):
		'''
		保存所有数据
		'''
		self.role.SetObj(EnumObj.ElementBrandData, self.get_all_data())
		
		
	def sync_all_data(self):
		'''
		同步所有数据
		'''
		self.role.SendObj(ElementBrand_AllData_S, self.get_all_data())
	
	
	def show_all(self):
		'''
		展示所有数据
		'''
		print "ElementBrandMgr::show_all,role(%s)" % self.role.GetRoleID()
		if len(self.package_dict):
			print "==== package data start ======="
			for brandId, brandObj in self.package_dict.iteritems():
				print brandId, brandObj.get_base_data()
			print "=== package data end   ======"
		
		if len(self.equip_dict):
			print "======= equip data start ======,role(%s)" % self.role.GetRoleID()
			for brandId, brandObj in self.equip_dict.iteritems():
				print brandId, brandObj.get_base_data()
			print "======= equip data end   ====="
		
		if len(self.meterial_dict):
			print "===== meterial data start ====,role(%s)" % self.role.GetRoleID()
			for keyData, brandCnt in self.meterial_dict.iteritems():
				print keyData, brandCnt
			print "====== meterial data end   ====="
	
	
	def clear_all(self):
		'''
		清楚所有印记数据
		'''
		print "GE_EXC,ElementBrandMgr::clear_all,role(%s)" % self.role.GetRoleID()
		self.package_dict.clear()
		self.equip_dict.clear()
		self.meterial_dict.clear()
		
		#重算属性
		self.role.ResetElementBrandBaseProperty()
		
		
class ElementBrand(object):
	'''
	元素印记类
	'''
	def __init__(self, role, brandId, dataList):
		self.role = role
		self.brand_id = brandId
		
		self.brand_type = dataList[IDX_TYPE]
		self.brand_color = dataList[IDX_COLOR]
		self.brand_level = dataList[IDX_LEVEL]
		self.brand_talent = dataList[IDX_TALENT]
		self.brand_pos = dataList[IDX_POS]
		self.brand_savePro = dataList[IDX_SAVEPRO]
		self.brand_unsavePro = dataList[IDX_UNSAVEPRO]
		
		self.after_create()
	
	
	def after_create(self):
		self.brand_cfg = ElementBrandConfig.GetCfgByTCL(self.brand_type, self.brand_color, self.brand_level) 
	
	
	def get_base_data(self):
		'''
		返回基本核心数据
		'''
		return [self.brand_type, self.brand_color, self.brand_level, self.brand_talent, self.brand_pos, self.brand_savePro, self.brand_unsavePro]
	
	
	def set_pos(self, pos):
		self.brand_pos = pos
		
		
	def shenji(self):
		'''
		印记升级
		'''
		self.brand_level += 1
		self.brand_cfg = ElementBrandConfig.GetCfgByTCL(self.brand_type, self.brand_color, self.brand_level)
	
	
	def wash_pro(self, lockList=[]):
		'''
		属性洗练
		''' 
		tmpProDict = {}
		for proType in lockList:
			tmpProDict[proType] = self.brand_savePro[proType]
		
		#条数足够了
		needWashCnt = self.brand_cfg.maxProCnt - len(tmpProDict)
		if needWashCnt < 1:
			return 
		
		#随机洗练几条属性
		newWashProDict = ElementBrandConfig.WashBrandByData(lockList, needWashCnt)
		#整合
		tmpProDict.update(newWashProDict)
		#保存
		self.brand_unsavePro = tmpProDict

	
	def save_pro(self):
		'''
		保存洗练属性
		'''
		#覆盖
		self.set_savepro(self.get_unsanvepro())
		#清理
		self.set_unsavepro_dict()
	
	
	def get_unsanvepro(self):
		'''
		获取为保存的属性字典
		'''
		return self.brand_unsavePro
	
	
	def set_unsavepro_dict(self, unsavepro_dict={}):
		'''
		设置未保存洗练属性字典
		'''
		self.brand_unsavePro = unsavepro_dict
		
	
	def get_savepro(self):
		'''
		获取保存的洗练属性字典
		'''
		return self.brand_savePro
	
	
	def set_savepro(self, pro_dict={}):
		'''
		设置已保存的洗练属性
		''' 
		self.brand_savePro = pro_dict
	
	
	def excute_transmit(self, low_savepro_dict={}):
		'''
		执行继承(把需要保留的低阶印记属性当作锁定属性列表 然后执行洗练即可)
		'''
		#保留低阶印记属性
		self.brand_savePro = low_savepro_dict
		#锁定保留的低阶属性 洗练
		tmpProDict = {}
		for proType in self.brand_savePro:
			tmpProDict[proType] = self.brand_savePro[proType]
		
		#条数足够了
		needWashCnt = self.brand_cfg.maxProCnt - len(tmpProDict)
		if needWashCnt < 1:
			return 
		
		#随机洗练几条属性
		newWashProDict = ElementBrandConfig.WashBrandByData(tmpProDict, needWashCnt)
		self.brand_savePro.update(newWashProDict)
	
	
#===============================================================================
# 客户端请求
#===============================================================================
def OnSculpture(role, msg):
	'''
	元素印记_请求印记雕刻
	@param msg: sculptureType 雕刻类型
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	backId, sculptureType = msg
	sculptureCfg = ElementBrandConfig.ElementBrand_SculptureConfig_Dict.get(sculptureType, None)
	if not sculptureCfg:
		return
	
	needCoding, needCnt = sculptureCfg.needItem
	needRMBQ = sculptureCfg.needRMBQ
	#不能用神石代替 并且 材料不够
	if  not needRMBQ and role.ItemCnt(needCoding) < needCnt:
		return 
	
	#材料不够 并且 可以神石代替 但是 神石不足
	if (role.ItemCnt(needCoding) < needCnt and needRMBQ) and role.GetUnbindRMB_Q() < needRMBQ:
		return 
	
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	if elementBrandMgr.get_empty_size() < 1:
		return
	
	sculptureData = ElementBrandConfig.RandomSculptureDataByType(sculptureType)
	if not sculptureData:
		print "GE_EXC,ElementBrandMgr::OnSculpture, can not random sculpture data by sculptureType(%s), role(%s)" % (sculptureType, role.GetRoleID())
		return
	
	brandType, brandColor, talentValue = sculptureData
	brandDataList = [brandType, brandColor, DEFAULT_LEVEL, talentValue, DEFALUT_POS, DEFALUT_SAVEPRO, DEFALUT_UNSAVEPRO]
	with Tra_ElementBrand_Sculpture:
		#删除雕刻道具
		if role.ItemCnt(needCoding) >= needCnt:
			role.DelItem(needCoding, needCnt)
		elif role.GetUnbindRMB_Q() >= needRMBQ:
			role.DecUnbindRMB_Q(needRMBQ)
		else:
			print "GE_EXC,ElementBrandMgr::OnSculpture, not any pay for sculpture(%s),role(%s)" % (sculptureType, role.GetRoleID())
			return 
		#获得印记
		brandId = elementBrandMgr.new_brand(brandDataList)
		#日志记录
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveBrandSculpture, (brandId, brandType, brandColor, DEFAULT_LEVEL, talentValue))
	
	brandDataList = elementBrandMgr.get_brand_data_by_brand_id(brandId)
	role.CallBackFunction(backId, (brandId, brandDataList))	

		
def OnEquip(role, msg):
	'''
	元素印记_请求印记镶嵌
	@param msg: tarBrandId, pos 目标印记ID, 目标位置
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	backId, param = msg
	tarBrandId, targetPos = param
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	if not elementBrandMgr.can_equip(tarBrandId, targetPos):
		return
	
	with Tra_ElementBrand_Equip:
		elementBrandMgr.equip_brand(tarBrandId, targetPos)

	role.CallBackFunction(backId, (tarBrandId, targetPos))


def OnUnEquip(role, msg):
	'''
	元素印记_请求印记卸载
	@param msg: targetBrandId 目标印记ID
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	backId, tarBrandId = msg
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	if not elementBrandMgr.can_unequip(tarBrandId):
		return
	
	with Tra_ElementBrand_UnEquip:
		elementBrandMgr.unequip_brand(tarBrandId)
	
	role.CallBackFunction(backId, (tarBrandId))


def OnShenJi(role, msg):
	'''
	元素印记_请求印记升级
	@param msg: tarBrandId 目标印记ID
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	backId, tarBrandId = msg
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	if not elementBrandMgr.can_shenji(tarBrandId):
		return
	
	with Tra_ElementBrand_ShenJi:
		elementBrandMgr.shenji_brand(tarBrandId)
		#获取该印记最新数据
		brandDataList = elementBrandMgr.get_brand_data_by_brand_id(tarBrandId)
		#日志记录
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveBrandShenJi, (tarBrandId, brandDataList[IDX_LEVEL]))
	
	role.CallBackFunction(backId, (tarBrandId,brandDataList))
	

def OnFenJie(role, msg):
	'''
	元素印记_请求印记分解
	@param msg: tarBrandIdList 目标印记ID列表
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	backId, tarBrandIdList = msg
	fenJieBrandList = []
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	fenJieFlag = False
	isMeterialChange = False
	with Tra_ElementBrand_FenJie:
		for tarbrandId in tarBrandIdList:
			if not elementBrandMgr.can_fenjie(tarbrandId):
				continue
			fenJieFlag = True
			isMeterialChange = elementBrandMgr.fenjie_brand(tarbrandId)
			fenJieBrandList.append(tarbrandId)	
			#日志记录
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveBrandFenJie, (tarbrandId))
	
	role.CallBackFunction(backId, fenJieBrandList)
	
	#成功分解了至少一个 背包 or 材料印记 数据变化更新
	if fenJieFlag:
		if isMeterialChange:
			role.SendObj(ElementBrand_UpdateDataByKey_S, elementBrandMgr.get_data_by_key([KEY_PACKAGE, KEY_MATERIAL]))
		else:
			role.SendObj(ElementBrand_UpdateDataByKey_S, elementBrandMgr.get_data_by_key([KEY_PACKAGE]))


def OnWashPro(role, msg):
	'''
	元素印记_请求印记洗练
	@param msg: [targetBrandId, lockList, isRMBLock, isRMBStone]----[印记ID, 锁定列表, 自动购买洗练锁, 自动购买洗练石]
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	backId, param = msg
	targetBrandId, lockList, isRMBLock, isRMBStone = param
	retvalue = elementBrandMgr.can_wash(targetBrandId, lockList, isRMBLock, isRMBStone)
	if not retvalue:
		return 
	
	washStoneCnt, washLockCnt, washRMB = retvalue
	if (washStoneCnt < 0 or washLockCnt < 0 or washRMB < 0) or (washStoneCnt == 0 and washLockCnt == 0 and washRMB == 0):
		return
	
	oldUnsavePro = {}
	brandDataOld = elementBrandMgr.get_brand_data_by_brand_id(targetBrandId)
	if len(brandDataOld):
		oldUnsavePro = brandDataOld[IDX_UNSAVEPRO]
	with Tra_ElementBrand_WashPro:
		elementBrandMgr.wash_brand(targetBrandId, lockList, washStoneCnt, washLockCnt, washRMB)
		#日志 记录最新洗练出来的属性
		newUnsavePro = {}
		brandDataNew = elementBrandMgr.get_brand_data_by_brand_id(targetBrandId)
		if len(brandDataNew):
			newUnsavePro = brandDataNew[IDX_UNSAVEPRO]
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveElementBrandWashPro, (targetBrandId, oldUnsavePro, newUnsavePro))	
		#回调客户端最新印记数据
		role.CallBackFunction(backId, {targetBrandId:brandDataNew})
	

def OnSavePro(role, msg):
	'''
	元素印记_请求保存属性
	@param msg: targetBrandId 印记ID
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	backId, param = msg
	targetBrandId = param
	if not elementBrandMgr.can_savepro(targetBrandId):
		return 
	
	oldSavePro = {}
	brandDataOld = elementBrandMgr.get_brand_data_by_brand_id(targetBrandId)
	if len(brandDataOld):
		oldSavePro = brandDataOld[IDX_SAVEPRO]
	with Tra_ElementBrand_SavePro:
		#保存
		elementBrandMgr.save_washpro(targetBrandId)
		#日志
		newSavePro = {}
		brandDataNew = elementBrandMgr.get_brand_data_by_brand_id(targetBrandId)
		if len(brandDataNew):
			newSavePro = brandDataNew[IDX_SAVEPRO]
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveElementBrandSavePro, (targetBrandId, oldSavePro, newSavePro))
		#回调
		role.CallBackFunction(backId, {targetBrandId:brandDataNew})


def OnTransmit(role, msg):
	'''
	元素印记_请求继承
	@param msg: [lowBrandId,highBrandId] --- [低阶印记ID，高阶印记ID]
	'''
	if role.GetLevel() < EnumGameConfig.ElementBrand_NeedLevel:
		return
	
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	backId, param = msg
	lowBrandId, highBrandId = param
	if not elementBrandMgr.can_transmit(lowBrandId, highBrandId):
		return 
	
	oldLowBrandData = elementBrandMgr.get_brand_data_by_brand_id(lowBrandId)
	oldHighBrandData = elementBrandMgr.get_brand_data_by_brand_id(highBrandId)
	with Tra_ElementBrand_TransmitPro:
		#继承
		retData = elementBrandMgr.transmit_brand(lowBrandId, highBrandId)
		#日志
		newHighBrandData = elementBrandMgr.get_brand_data_by_brand_id(highBrandId)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveElementBrandTransmit, (lowBrandId, highBrandId, oldLowBrandData, oldHighBrandData, newHighBrandData))
		#回调客户端
		role.CallBackFunction(backId, [lowBrandId, highBrandId, newHighBrandData, retData])
		#同步印记背包数据
		role.SendObj(ElementBrand_UpdateDataByKey_S, elementBrandMgr.get_data_by_key([KEY_MATERIAL, KEY_PACKAGE]))


#===============================================================================
# 事件
#===============================================================================
def OnInitRolePyObj(role, param = None):
	'''
	初始化玩家obj
	'''
	elementBrandData = role.GetObj(EnumObj.ElementBrandData)
	if KEY_PACKAGE not in elementBrandData:
		elementBrandData[KEY_PACKAGE] = {}
	
	if KEY_EQUIP not in elementBrandData:
		elementBrandData[KEY_EQUIP] = {}
	
	if KEY_MATERIAL not in elementBrandData:
		elementBrandData[KEY_MATERIAL] = {}
	
	role.SetTempObj(EnumTempObj.ElementBrandMgr, ElementBrandMgr(role))
	

def OnSyncRoleOtherData(role, param = None):
	'''
	同步客户端相关数据
	'''
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	elementBrandMgr.sync_all_data()


def BeforeSaveRole(role, param = None):
	'''
	保存角色之前
	'''
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	elementBrandMgr.save_all_data()


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRolePyObj)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_BeforeSaveRole, BeforeSaveRole)
		
	if  Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnSculpture", "元素印记_请求印记雕刻"), OnSculpture)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnEquip", "元素印记_请求印记镶嵌"), OnEquip)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnUnEquip", "元素印记_请求印记卸载"), OnUnEquip)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnShenJi", "元素印记_请求印记升级"), OnShenJi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnFenJie", "元素印记_请求印记分解"), OnFenJie)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnWashPro", "元素印记_请求印记洗练"), OnWashPro)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnSavePro", "元素印记_请求保存属性"), OnSavePro)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementBrand_OnTransmit", "元素印记_请求继承"), OnTransmit)
