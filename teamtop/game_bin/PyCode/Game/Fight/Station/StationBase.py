#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Station.StationBase")
#===============================================================================
# 阵位管理器
#===============================================================================
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Property import PropertyEnum

#检查主(辅)助阵位对应的辅(主)助阵位星级
CheckStarDict = {1:4, 2:5, 3:6, 4:1, 5:2, 6:3}
#合法主阵位ID
StationLimit = [1,2,3,4]

class StationMgr(object):
	def __init__(self, role):
		self.role = role
		
		#注意这两个要分开的, 因为有换阵
		self.type_to_station = {}								#类型 --> 阵位ID
		self.type_to_help_station = {}							#类型 --> 助阵位ID
		
		self.station_to_id = {}									#阵位ID --> heroId or roleId
		
		self.help_station_to_id = {}							#助阵位ID --> heroId
		self.help_station_limit = [1,2,3]						#合法助阵位ID(默认三个主助阵位是合法的, 解锁副助阵位的时候会将副助阵位的id加入)
		
		self.help_station_star = {}								#助阵位ID --> 英雄星级
		
		#提出到外面, 所有对象使用同一份数据引用
		#self.station_limit = [1,2,3,4]							#合法阵位ID
		#self.help_station_pro_enum = [1,4,6,16]					#血、物攻、法功、战斗力
		
		self.help_station_mosaic = {}							#{助阵位ID-->水晶等级}
		
		#初始化主角阵位
		roleId = role.GetRoleID()
		roleStation = role.GetStationID()
		
		if role.GetRoleID() not in self.station_to_id.values() and roleStation not in self.station_to_id:
			self.station_to_id[roleStation] = roleId
		else:
			print "GE_EXC stationID(%s) error in StationMgr init, roleID (%s)" % (roleStation, roleId)
			return
		
		#初始化助阵位镶嵌字典 {助阵位ID --> 镶嵌等级}
		stationObj = role.GetObj(EnumObj.StationObj)
		self.help_station_mosaic = stationObj.get(1, {})
		self.help_station_limit.extend(stationObj.get(2, []))
		
		roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
		global StationLimit
		for heroId, heroObj in roleHeroMgr.HeroDict.iteritems():
			heroStationID = heroObj.GetStationID()
			heroHelpStationID = heroObj.GetHelpStationID()
			
			if not heroStationID and not heroHelpStationID:
				continue
			
			#同时在阵位和助阵位上
			if heroStationID and heroHelpStationID:
				print "GE_EXC, heroID (%s) in station and help station" % heroId
				return
			
			#阵位ID合法并且对应阵位上没有别的人
			if heroStationID in StationLimit and heroStationID not in self.station_to_id:
				self.station_to_id[heroStationID] = heroId
				self.type_to_station[heroObj.cfg.heroType] = heroStationID
			elif heroHelpStationID in self.help_station_limit and heroHelpStationID not in self.help_station_to_id:
				#助阵位ID --> 英雄ID
				self.help_station_to_id[heroHelpStationID] = heroId
				#英雄类型 --> 助阵位ID
				self.type_to_help_station[heroObj.cfg.heroType] = heroHelpStationID
				#助阵位ID --> 英雄星级
				self.help_station_star[heroHelpStationID] = heroObj.GetStar()
			else:
				print "GE_EXC, heroID:%s can have error station or help station" % heroId
				return
		
	def get_heroid_from_station(self, station):
		return self.station_to_id.get(station)
	
	def get_heroid_from_help_station(self, station):
		return self.help_station_to_id.get(station)
	
	def swap_station(self, station1, station2):
		#交换两个阵位上英雄(主角)ID
		tmpHeroId = self.station_to_id[station1]
		self.station_to_id[station1] = self.station_to_id[station2]
		self.station_to_id[station2] = tmpHeroId
	
	def in_station(self, peopleId, station):
		if peopleId in self.station_to_id.itervalues():
			print "GE_EXC station has people, peopleId(%s), station(%s) in in_station" % (peopleId, station)
			return
		
		if peopleId != self.role.GetRoleID() and self.role.GetHero(peopleId).cfg.heroType not in self.type_to_station:
			self.type_to_station[self.role.GetHero(peopleId).cfg.heroType] = station
			
		self.station_to_id[station] = peopleId
	
	def in_help_station(self, heroId, station):
		if heroId in self.help_station_to_id.itervalues():
			print "GE_EXC help station has hero, heroId(%s), help station(%s) in in_help_station" % (heroId, station)
			return
		
		hero = self.role.GetHero(heroId)
		heroType = hero.cfg.heroType
		heroStar = hero.cfg.star
		
		#英雄类型 --> 助阵位ID
		self.type_to_help_station[heroType] = station
		
		#助阵位ID --> 英雄ID
		self.help_station_to_id[station] = heroId
		
		#记录助阵位英雄星级
		self.help_station_star[station] = heroStar
		
	def cal_next_help_station_id(self):
		#计算下一个可用的助阵位ID
		for i in self.help_station_limit:
			if i not in self.help_station_star:
				return i
		return 0
		
	def out_station(self, station):
		if station not in self.station_to_id:
			return
		
		heroId = self.station_to_id[station]
		del self.station_to_id[station]
		
		if heroId != self.role.GetRoleID():
			del self.type_to_station[self.role.GetHero(heroId).cfg.heroType]
	
	def out_help_station(self, station):
		if station not in self.help_station_to_id:
			return
		
		heroId = self.help_station_to_id[station]
		del self.help_station_to_id[station]
		
		del self.type_to_help_station[self.role.GetHero(heroId).cfg.heroType]
		
		del self.help_station_star[station]
			
	def is_station_role(self, station):
		if station in self.station_to_id and self.station_to_id[station] == self.role.GetRoleID():
			return True
		return False
	
	def type_in_station(self, heroType):
		if heroType in self.type_to_station:
			return self.type_to_station[heroType]
		return None
	
	def type_in_help_station(self, heroType):
		if heroType in self.type_to_help_station:
			return self.type_to_help_station[heroType]
		return None
	
	def check_can_in_help_station(self, hero, station_id):
		#检查英雄是否能够上阵(判断星级)
		#对应的助阵位ID
		global CheckStarDict
		check_station_id = CheckStarDict.get(station_id)
		if not check_station_id:
			return False
		
		#对应的助阵位英雄星级
		check_station_star = self.help_station_star.get(check_station_id)
		station_star = hero.GetStar()
		
		if station_id in (1, 2, 3):
			#主助阵位需要判断星级大于对应的副助阵位
			if check_station_star and station_star <= check_station_star:
				return False
		elif station_id in (4, 5, 6):
			#副助阵位需要判断星级小于对应的主助阵位
			if not check_station_star:
				#对应的主助阵位没有上阵英雄
				return False
			if check_station_star <= station_star:
				#主助阵位星级小于要上阵的副助阵位星级
				return False
		return True
		
	def station_is_legal(self, station):
		global StationLimit
		if station in StationLimit:
			return True
		return False
	
	def help_station_is_legal(self, station):
		if station in self.help_station_limit:
			return True
		return False
	
	def GetHelpStationNumbers(self):
		#获取助阵英雄编号
		l = []
		limitStationId = (1,2,3)
		RG = self.role.GetHero
		for heroId in self.help_station_to_id.values():
			hero = RG(heroId)
			if not hero:
				continue
			if hero.GetHelpStationID() not in limitStationId:
				continue
			l.append(hero.GetNumber())
		return l
	
	def GetViewData(self):
		#获取别人查看的数据
		d = {}
		RG = self.role.GetHero
		for heroId in self.help_station_to_id.values():
			hero = RG(heroId)
			if not hero:
				continue
			d[hero.GetNumber()] = (hero.GetLevel(), hero.GetPropertyGather().total_p_m.p_dict.get(PropertyEnum.zdl, 0))
		return d
	
	def UnlockHelpStationId(self, stationId):
		self.help_station_limit.append(stationId)
		self.role.GetObj(EnumObj.StationObj)[2].append(stationId)
		
	def save(self, role):
		role.GetObj(EnumObj.StationObj)[1] = self.help_station_mosaic
