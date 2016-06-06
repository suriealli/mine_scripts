#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.StarGirl.StarGirlBase")
#===============================================================================
# 星灵基础模块
#===============================================================================
import cDateTime
from Game.Role.Data import EnumObj, EnumInt8
from Game.StarGirl import StarGirlConfig, StarGirlDefine
from Game.Role import Event
from Common.Message import AutoMessage

if "_HasLoad" not in dir():
	#驯龙管理器枚举
	STAR_GIRL_MGR_GIRL_DICT_IDX = 1				#星灵
	STAR_GIRL_MGR_SEAL_DICT_IDX = 2				#魂炼
	
	#星灵枚举
	LEVEL_IDX= 1				#等级
	EXP_IDX = 2					#经验
	GRADE_IDX = 3				#阶级
	STAR_LEVEL_IDX = 4			#星级
	STAR_BLESS_VALUE_IDX = 5	#星级祝福值
	PRAY_CNT_IDX = 6			#祈祷次数
	TEMP_BLESS_IDX = 7			#临时幸运值
	TEMP_BLESS_TICK = 8			#临时幸运值Tick
	#魂印枚举
	SEAL_LEVEL_IDX = 1			#等级
	SEAL_EXP_IDX = 2			#经验
	
	Star_Girl_Syn_Temp_Bless = AutoMessage.AllotMessage("Star_Girl_Syn_Temp_Bless", "同步星灵临时幸运值信息")

class StarGirl(object):
	def __init__(self, girlId, girlDataDict, sgm, returnDB = False):
		self.sgm = sgm
		self.girl_id = girlId
		self.level = girlDataDict.get(LEVEL_IDX, 1)
		self.exp = girlDataDict.get(EXP_IDX, 0)
		self.grade = girlDataDict.get(GRADE_IDX, 1)
		self.star_level = girlDataDict.get(STAR_LEVEL_IDX, 1)
		self.star_bless_value = girlDataDict.get(STAR_BLESS_VALUE_IDX, 0)
		self.pray_cnt = girlDataDict.get(PRAY_CNT_IDX, 0)
		
		self.temp_bless_data = girlDataDict.get(TEMP_BLESS_IDX, [])
		self.temp_bless_tick = girlDataDict.get(TEMP_BLESS_TICK, 0)
		#属性字典重算使用不保存
		self.property_dict = {}
		
		#从数据库载入的时候，暂时不算属性
		if returnDB is False:
			#重算属性
			self.recount_property()
			
	def GetGrilTotleBless(self):
		#临时祝福值
		temp_bless = 0
		
		if self.temp_bless_data:
			temp_bless, _ = self.temp_bless_data
		
		return self.star_bless_value + temp_bless
			
	def AddGrilTempBless(self, role, bless, keepTime):
		#增加临时幸运值
		if self.temp_bless_data:
			old_bless, _ = self.temp_bless_data
			self.temp_bless_data = [old_bless + bless, int(cDateTime.Seconds() + keepTime)]
		else:
			self.temp_bless_data = [bless, int(cDateTime.Seconds() + keepTime)]
		if self.temp_bless_tick:
			role.UnregTick(self.temp_bless_tick)
		self.temp_bless_tick = role.RegTick(keepTime, self.EndBless, None)
		
	def EndBless(self, role, callargv, regparam):
		#清空临时幸运值
		self.CancelBless()
		
	def CancelBless(self):
		if self.temp_bless_data:
			self.temp_bless_data = []
			self.temp_bless_tick = 0
			#同步信息
			self.sgm.SynTempBless()
		
	def SetTempTick(self, role):
		#重新设置临时幸运值
		nowTime = cDateTime.Seconds()
		
		if not self.temp_bless_data: return
		
		_, endTime = self.temp_bless_data
		
		if endTime > nowTime:#未结束
			self.temp_bless_tick = role.RegTick(int(endTime - nowTime), self.EndBless, None)
		else:
			self.temp_bless_data = []
			self.temp_bless_tick = 0
		
	def get_active_skill(self):
		baseConfig = StarGirlConfig.STAR_GIRL_BASE.get((self.girl_id, self.grade))
		if not baseConfig:
			return ()
		
		return baseConfig.activeSkill
	
	def get_passive_skill(self):
		starLevelConfig = StarGirlConfig.STAR_LEVEL.get((self.girl_id, self.star_level))
		if not starLevelConfig:
			return []
		
		return starLevelConfig.passiveSkill
		
	def recount_property(self):
		
		self.property_dict = propertyDict = {}
		PG = propertyDict.get
		
		#获取配置
		baseConfig = StarGirlConfig.STAR_GIRL_BASE.get((self.girl_id, self.grade))
		if baseConfig:
			for pt, pv in baseConfig.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv
		
		levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((self.girl_id, self.level))
		if levelConfig:
			for pt, pv in levelConfig.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv
		
		starLevelConfig = StarGirlConfig.STAR_LEVEL.get((self.girl_id, self.star_level))
		if starLevelConfig:
			for pt, pv in starLevelConfig.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv
		
		#魂印
		for pt, pv in self.sgm.seal_property.iteritems():
			propertyDict[pt] = PG(pt, 0) + pv

			
class Seal(object):
	def __init__(self, sealId, sealDataDict, sgm):
		self.seal_id = sealId
		self.level = sealDataDict.get(SEAL_LEVEL_IDX, 1)
		self.exp = sealDataDict.get(SEAL_EXP_IDX, 0)
		
		self.levelcfg = StarGirlConfig.SEAL_LEVEL.get((self.seal_id, self.level))
		#管理器对象
		self.sgm = sgm
		
class StarGirlMgr(object):
	def __init__(self, role):
		starGirlDict = role.GetObj(EnumObj.StarGirl)
		
		self.role = role
		self.girl_dict = {}
		self.seal_dict = {}
		self.girl_power_tick_id_dict = {}
		
		self.seal_property = {}
		#星灵
		if STAR_GIRL_MGR_GIRL_DICT_IDX in starGirlDict:
			girlDict = starGirlDict[STAR_GIRL_MGR_GIRL_DICT_IDX]
			for girlId, girlDataDict in girlDict.iteritems():
				self.girl_dict[girlId] = StarGirl(girlId, girlDataDict, self, True)
				
		#魂炼
		if STAR_GIRL_MGR_SEAL_DICT_IDX in starGirlDict:
			sealDict = starGirlDict[STAR_GIRL_MGR_SEAL_DICT_IDX]
			for sealId, sealDataDict in sealDict.iteritems():
				self.seal_dict[sealId] = Seal(sealId, sealDataDict, self)
			
			#重算属性，会触发其他的星灵属性重算
			self.Recount_seal_property(False)
			
	def create_star_girl(self, girlId):
		d = {LEVEL_IDX: 1, 
			EXP_IDX: 0, 
			GRADE_IDX: 1, 
			STAR_LEVEL_IDX: 1, 
			STAR_BLESS_VALUE_IDX: 0, 
			PRAY_CNT_IDX: 0,
			TEMP_BLESS_IDX: [],
			TEMP_BLESS_TICK: 0
			}
		self.girl_dict[girlId] = StarGirl(girlId, d, self)
		
	def create_seal(self, sealId):
		d = {SEAL_LEVEL_IDX: 1, 
			SEAL_EXP_IDX: 0}
		self.seal_dict[sealId] = Seal(sealId, d, self)
		
	def get_star_girl_property(self, girlId):
		#是否解锁星灵
		if girlId not in self.girl_dict:
			return {}
		girlObj = self.girl_dict[girlId]
		
		return girlObj.property_dict
	
	def recount_star_girl_property(self, girlId):
		#是否解锁星灵
		if girlId not in self.girl_dict:
			return
		girlObj = self.girl_dict[girlId]
		
		girlObj.recount_property()
		
		if self.role.GetI8(EnumInt8.StarGirlFightId) == girlId:
			Event.TriggerEvent(Event.Eve_RecountZDL, self.role)
	
	def recount_star_girl_propertyByObj(self, girlObj, recountZDL = True):
		girlObj.recount_property()
		if recountZDL is True and self.role.GetI8(EnumInt8.StarGirlFightId) == girlObj.girl_id:
			Event.TriggerEvent(Event.Eve_RecountZDL, self.role)
	
	def Recount_seal_property(self, recountZDL = True):
		#重算魂印属性
		self.seal_property = SSP = {}
		PG = SSP.get
		for seal in self.seal_dict.itervalues():
			for pt, pv in seal.levelcfg.property_dict.iteritems():
				SSP[pt] = PG(pt, 0) + pv
		
		#重算所有的
		SR = self.recount_star_girl_propertyByObj
		for gobj in self.girl_dict.itervalues():
			SR(gobj, recountZDL)
		
	def get_role_view_data(self):
		#只显示出战星灵信息
		fightGirlId = self.role.GetI8(EnumInt8.StarGirlFightId)
		
		if fightGirlId not in self.girl_dict:
			return ()
		
		fightGirlObj = self.girl_dict[fightGirlId]
		
		isStarPowerActive = 0
		cdEnum = StarGirlDefine.GIRL_ID_TO_CD_ENUM.get(fightGirlId)
		if self.role.GetCD(cdEnum):
			isStarPowerActive = 1
		
		sealData = {}
		for sealId, sealObj in self.seal_dict.iteritems():
			sealData[sealId] = (sealObj.level, sealObj.exp)
		
		return (fightGirlObj.girl_id, fightGirlObj.level, fightGirlObj.exp, fightGirlObj.grade, 
				fightGirlObj.star_level, fightGirlObj.star_bless_value, fightGirlObj.pray_cnt, isStarPowerActive, sealData)
		
	def AddTempBless(self, tempBless, keepTime):
		#给星级最高的星灵增加临时祝福值
		starLevelConfig = StarGirlConfig.STAR_LEVEL.get((1, 1))
		if not starLevelConfig:
			print "GE_EXC,Is wrong in StarGirl AddTempBless"
			return
		maxLevel, maxGrilId = 0, 0
		for girlId, girlObj in self.girl_dict.iteritems():
			if girlObj.star_level < starLevelConfig.maxStarlevel and girlObj.star_level > maxLevel:
				maxLevel, maxGrilId = girlObj.star_level, girlId
				
		if not maxLevel or not maxGrilId: return

		girlObj = self.girl_dict.get(maxGrilId)
		girlObj.AddGrilTempBless(self.role, tempBless, keepTime)
		#同步客户端
		self.SynTempBless()
		
	def SynTempBless(self):
		#同步星灵临时祝福值信息
		bless_dict = {}
		for girlId, girlObj in self.girl_dict.iteritems():
			if not girlObj.temp_bless_data:
				continue
			bless_dict[girlId] = girlObj.temp_bless_data
		
		self.role.SendObj(Star_Girl_Syn_Temp_Bless, bless_dict)
		
	def GetAllStarGirlStarLevel(self):
		d = {}
		for girlId, girlObj in self.girl_dict.iteritems():
			d[girlId] = girlObj.star_level
			
		return d
		
	def save(self):
		starGirlDict = self.role.GetObj(EnumObj.StarGirl)
		
		girlDict = starGirlDict.setdefault(STAR_GIRL_MGR_GIRL_DICT_IDX, {})
		sealDict = starGirlDict.setdefault(STAR_GIRL_MGR_SEAL_DICT_IDX, {})
		
		for girlId, girlObj in self.girl_dict.iteritems():
			girlDict[girlId] = {LEVEL_IDX: girlObj.level, 
								EXP_IDX: girlObj.exp, 
								GRADE_IDX: girlObj.grade, 
								STAR_LEVEL_IDX: girlObj.star_level, 
								STAR_BLESS_VALUE_IDX: girlObj.star_bless_value, 
								PRAY_CNT_IDX: girlObj.pray_cnt,
								TEMP_BLESS_IDX: girlObj.temp_bless_data,
								TEMP_BLESS_TICK: girlObj.temp_bless_tick
								}
			
		for sealId, sealObj in self.seal_dict.iteritems():
			sealDict[sealId] = {SEAL_LEVEL_IDX: sealObj.level, 
								SEAL_EXP_IDX: sealObj.exp}
		
		