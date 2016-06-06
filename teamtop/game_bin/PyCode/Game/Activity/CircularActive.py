#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CircularActive")
#===============================================================================
# 循环活动控制
#===============================================================================
import time
import datetime
import DynamicPath
import Environment
import cComplexServer
import cNetMessage
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity.DoubleTwelve import RichRankMgr
from Game.Role import Event
from Game.SysData import WorldData, WorldDataNotSync
from Util.File import TabFile
from Game.Activity.SuperPromption import SuperPromptionMgr
from Game.Activity.YeYouJieKuangHuan import YeYouJieRechargeMgr

#1天的秒数
OneDaySecs = 24 * 3600

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CircularActive")
	#配置
	CircularActiveConfig_Dict = {}
	#缓存同步数据
	CircularActiveCache_Dict = {}
	
	#GM指令临时预先停止的活动ID
	#临时措施，为了预防关服导致的活动重新开启，每次操作的时候需要热更循环活动配置表
	Cancle_GM_Set = set()
	
	#勇者英雄坛
	BraveHero_Dict = {}
	#超值特惠活动控制表
	SuperPromption_ActiveControl_Dict = {}
	#全名转转乐
	TurnTableActive_Dict = {}
	#古堡探秘
	GuBaoTanMiActive_Dict = {}
	#跨服鲜花榜
	KuafuFlowerRank_Dict = {}
	#激情活动_天降横财
	PassionTJHCActive_Config = None
	#捕鱼活动
	CatchingFishActive_Dict = {}
	PassionRechargeRankActiveObj = None		#激情活动--充值排名开启配置对象
	PassionConsumeRankActiveObj = None 		#激情活动--消费排名开启配置对象
	#春节太回馈活动时间控制
	FestivalRebate_Active_Control = None
	#秘密花园时间控制
	SecretGarden_Active_Control = None
	
class LanternFestivalRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LanternFestivalActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	

	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		#本地也要晚一分钟结束, 用于发奖
		from Game.Activity.LanternFestival import LanternRank
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			LanternRank.Start(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, LanternRank.End)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, LanternRank.Start)
			cComplexServer.RegTick(endTime - nowTime + 60, LanternRank.End)


def LoadLanternFestivalRankConfig():
	for cfg in LanternFestivalRankConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in LanternFestivalRankConfig"
			return
		#无依赖, 起服触发
		cfg.Active()



class SpringBActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SpringBActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		from Game.Activity.SpringFestival import SpringBeautiful
		#控制进程晚一分钟结束
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			SpringBeautiful.OpenSpringB(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, SpringBeautiful.CloseSpringB)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, SpringBeautiful.OpenSpringB, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, SpringBeautiful.CloseSpringB)
			
def LoadSpringBActive():
	for cfg in SpringBActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in LoadSpringBActive"
			return
		#不需要依赖什么, 在起服的时候就可以触发了
		cfg.Active()
		

class NewYearHaoActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("NewYearHaoActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		#本地也要晚一分钟结束, 用于发奖
		from Game.Activity.HappyNewYear import NewYearHao
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			NewYearHao.OpenNewYearHao(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, NewYearHao.CloseNewYearHao)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, NewYearHao.OpenNewYearHao)
			cComplexServer.RegTick(endTime - nowTime + 60, NewYearHao.CloseNewYearHao)
		
def LoadNewYearHaoActiveConfig():
	for cfg in NewYearHaoActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in NewYearHaoActive"
			return
		#无依赖, 起服触发
		cfg.Active()
	
class HaoqiActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HaoqiActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		#本地也要晚一分钟结束, 用于发奖
		from Game.Activity.Haoqi import HaoqiMgr
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			HaoqiMgr.OpenHaoqi(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, HaoqiMgr.CloseHaoqi)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, HaoqiMgr.OpenHaoqi)
			cComplexServer.RegTick(endTime - nowTime + 60, HaoqiMgr.CloseHaoqi)
		
def LoadHaoqiActiveConfig():
	for cfg in HaoqiActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in HaoqiActive"
			return
		#无依赖, 起服触发
		cfg.Active()
	
class ChristmasHaoActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ChristmasHaoActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		#本地正常时间结束, 不用延后了, 没有本地排行榜奖励
		from Game.Activity.Christmas import ChristmasHao
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			ChristmasHao.OpenChristmasHao(None, None)
			cComplexServer.RegTick(endTime - nowTime, ChristmasHao.CloseChristmasHao)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, ChristmasHao.OpenChristmasHao)
			cComplexServer.RegTick(endTime - nowTime, ChristmasHao.CloseChristmasHao)
		
def LoadChristmasHaoActiveConfig():
	for cfg in ChristmasHaoActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in ChristmasHaoActive"
			return
		#无依赖, 起服触发
		cfg.Active()
	
class BraveHeroActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("BraveHeroActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		from Game.Activity.BraveHero import BraveHeroMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			BraveHeroMgr.OpenBraveHero(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime, BraveHeroMgr.CloseBraveHero)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, BraveHeroMgr.OpenBraveHero, self.activeID)
			cComplexServer.RegTick(endTime - nowTime, BraveHeroMgr.CloseBraveHero)
		
def LoadBraveHeroActiveConfig():
	global BraveHero_Dict
	
	for cfg in BraveHeroActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in BraveHeroActive"
			return
		BraveHero_Dict[cfg.activeID] = cfg

class KuafuFlowerRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("KuafuFlowerRankActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		from Game.Flower import Flower
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#膜拜比排行榜晚一天开， 晚一天关
		worshipBeginTime = beginTime + 60 * 60 * 24
		worshipEndTime = endTime + 60 * 60 * 24
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			Flower.OpenKuafuFlowerRank(None, (self.activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, Flower.CloseKuafuFlowerRank)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, Flower.OpenKuafuFlowerRank, (self.activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, Flower.CloseKuafuFlowerRank)
		
		if worshipBeginTime <= nowTime < worshipEndTime:
			#激活
			Flower.OpenKuafuFlowerRankWorship(None, worshipEndTime)
			cComplexServer.RegTick(worshipEndTime - nowTime, Flower.CloseKuafuFlowerRankWorship)
		elif nowTime < worshipBeginTime:
			#注册一个tick激活
			cComplexServer.RegTick(worshipBeginTime - nowTime, Flower.OpenKuafuFlowerRankWorship, worshipEndTime)
			cComplexServer.RegTick(worshipEndTime - nowTime, Flower.CloseKuafuFlowerRankWorship)
		
		
def LoadKuafuFlowerRankActiveConfig():
	global KuafuFlowerRank_Dict, KuafuFlowerRankWorship_Dict
	
	for cfg in KuafuFlowerRankActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in KuafuFlowerRankActiveConfig"
			return
		KuafuFlowerRank_Dict[cfg.activeID] = cfg
	
class TurnTableActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TurnTableActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		from Game.Activity.TurnTable import TurnTable
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			TurnTable.OpenActive(None, (self.activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, TurnTable.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, TurnTable.OpenActive, (self.activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, TurnTable.CloseActive)
		
def LoadTurnTableActiveConfig():
	global TurnTableActive_Dict
	
	for cfg in TurnTableActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in TurnTableActive_Dict"
			return
		TurnTableActive_Dict[cfg.activeID] = cfg
		
		
#捕鱼活动
class CatchingFishActiveConfig(TabFile.TabLine):
	#自定义开启的文件位置
	CF_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CF_FILE_FOLDER_PATH.AppendPath("CatchingFish")
	FilePath = CF_FILE_FOLDER_PATH.FilePath("CatchingFishActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		from Game.Activity.CatchingFish import CatchingFishMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		Hasopedays = (nowTime - beginTime)/(24*60*60) 
		if WorldData.GetWorldKaiFuDay() - Hasopedays < 8 :
			return
		if beginTime <= nowTime < endTime:
			#激活
			CatchingFishMgr.OpenActive(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CatchingFishMgr.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, CatchingFishMgr.OpenActive, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CatchingFishMgr.CloseActive)
		
def LoadCatchingFishActiveConfig():
	for cfg in CatchingFishActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in CatchingFishActive_Dict"
			return
		CatchingFishActive_Dict[cfg.activeID] = cfg
#开启捕鱼活动
def OpenCatchingFishActive():
	for cfg in CatchingFishActive_Dict.itervalues():
		cfg.Active()
		
#此部分若放在GroupBuyPartyConfig模块 会导致模块间循环引用问题
class GroupBuyPartyBase(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GroupBuyPartyBase.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.totalDay = int
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		from Game.Activity.DoubleTwelve import GroupBuyPartyMgr
		if self.startTime <= nowDate < self.endTime:
			GroupBuyPartyMgr.OnStartGroupBuyParty(None, endTime)
			cComplexServer.RegTick(endTime - nowTime + GroupBuyPartyMgr.GBP_DELAY_SECONDS, GroupBuyPartyMgr.OnEndGroupBuyParty)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, GroupBuyPartyMgr.OnStartGroupBuyParty, endTime)
			cComplexServer.RegTick(endTime - nowTime + GroupBuyPartyMgr.GBP_DELAY_SECONDS, GroupBuyPartyMgr.OnEndGroupBuyParty)

def LoadGroupBuyPartyBase():
	'''
	此处仅仅是为了触发开启而做的配置加载
	'''
	for cfg in GroupBuyPartyBase.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in LoadGroupBuyPartyBase"
			continue
		cfg.init_active()
		
class RichRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("RichRankActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		if self.beginTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			RichRankMgr.OpenRichRank(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, RichRankMgr.CloseRichRank)
		elif nowDate < self.beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, RichRankMgr.OpenRichRank)
			cComplexServer.RegTick(endTime - nowTime + 60, RichRankMgr.CloseRichRank)
		
def LoadRichRankActiveConfig():
	for config in RichRankActiveConfig.ToClassType(False):
		if config.beginTime > config.endTime:
			print "GE_EXC, beginTime > endTime in RichRankActive"
			return
		#读取配置表的时候尝试激活活动
		config.active()

class GlamourRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourRankActive.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		from Game.Activity.ValentineDay import GlamourRankMgr
		if self.startTime <= nowDate < self.endTime:
			GlamourRankMgr.OnStartGlamourRank(None,endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, GlamourRankMgr.OnEndGlamourRank)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, GlamourRankMgr.OnStartGlamourRank, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, GlamourRankMgr.OnEndGlamourRank)

def LoadGlamourRankActiveConfig():
	'''
	此处仅仅是为了触发开启而做的配置加载
	'''
	for cfg in GlamourRankActiveConfig.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in GlamourRankActive"
			return
		cfg.init_active()

class LianChongRebateActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LianChongRebateActive.txt")
	def __init__(self):
		self.activeID = int
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		from Game.Activity.LianChongRebate import LianChongRebateMgr
		if self.startTime <= nowDate < self.endTime:
			LianChongRebateMgr.OnStartLianChongRebate(None,(self.activeID,endTime))
			cComplexServer.RegTick(endTime - nowTime, LianChongRebateMgr.OnEndLianChongRebate)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, LianChongRebateMgr.OnStartLianChongRebate, (self.activeID,endTime))
			cComplexServer.RegTick(endTime - nowTime, LianChongRebateMgr.OnEndLianChongRebate)
			
def LoadLianChongRebateActive():
	for cfg in LianChongRebateActive.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in LianChongRebateActive"
			return
		#不需要依赖什么, 在起服的时候就可以触发了
		cfg.init_active()

class QingMingRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingRankActive.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		from Game.Activity.QingMing import QingMingRankMgr
		if self.startTime <= nowDate < self.endTime:
			QingMingRankMgr.OnStartQingMingRank(None,endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, QingMingRankMgr.OnEndQingMingRank)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, QingMingRankMgr.OnStartQingMingRank, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, QingMingRankMgr.OnEndQingMingRank)

def LoadQingMingRankActiveConfig():
	'''
	此处仅仅是为了触发开启而做的配置加载
	'''
	for cfg in QingMingRankActiveConfig.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in QingMingRankActive"
			return
		cfg.init_active()

class ZaiXianJiangLiActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ZaiXianJiangLiActive.txt")
	def __init__(self):
		self.activeID = int
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		from Game.Activity.ZaiXianJiangLi import ZaiXianJiangLiMgr
		if self.startTime <= nowDate < self.endTime:
			ZaiXianJiangLiMgr.OnStartZaiXianJiangLi(None,(self.activeID,endTime))
			cComplexServer.RegTick(endTime - nowTime, ZaiXianJiangLiMgr.OnEndZaiXianJiangLi)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, ZaiXianJiangLiMgr.OnStartZaiXianJiangLi, (self.activeID,endTime))
			cComplexServer.RegTick(endTime - nowTime, ZaiXianJiangLiMgr.OnEndZaiXianJiangLi)
			
def LoadZaiXianJiangLiActive():
	for cfg in ZaiXianJiangLiActive.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in LianChongRebateActive"
			return
		#不需要依赖什么, 在起服的时候就可以触发了
		cfg.init_active()

class SuperPromptionControl(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SuperPromptionControl.txt")
	def __init__(self):
		self.activeId = int
		self.activeType = int
		self.activeName = str
		self.startTime = self.GetEvalByString
	
	def pre_process(self, nowSec):
		#开始时间戳
		beginSec = int(time.mktime(datetime.datetime(*self.startTime).timetuple()))
		#结束时间戳
		endSec = beginSec + OneDaySecs - 60
		if beginSec <= nowSec < endSec:
			#直接开启 并注册 结束tick
			SuperPromptionMgr.OnStartSuperPromption(None,(self.activeId, self.activeType))
			cComplexServer.RegTick(endSec - nowSec, SuperPromptionMgr.OnEndSuperPromption, (self.activeId, self.activeType))
		elif nowSec < beginSec:
			#注册开启 和 结束
			cComplexServer.RegTick(beginSec - nowSec, SuperPromptionMgr.OnStartSuperPromption, (self.activeId, self.activeType))
			cComplexServer.RegTick(endSec - nowSec, SuperPromptionMgr.OnEndSuperPromption, (self.activeId, self.activeType))

def LoadSuperPromptionControl():
	#当前时间戳
	nowSec = cDateTime.Seconds()
	global SuperPromption_ActiveControl_Dict
	for cfg in SuperPromptionControl.ToClassType():
		activeId = cfg.activeId
		if activeId in SuperPromption_ActiveControl_Dict:
			print "GE_EXC,repeat activeId in SuperPromption_ActiveControl_Dict"
		SuperPromption_ActiveControl_Dict[activeId] = cfg
		cfg.pre_process(nowSec)

class YeYouJieRechargeActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("YeYouJieRechargeActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.startTime = self.GetEvalByString
		self.endTime = self.GetEvalByString
	
	def pre_process(self):
		#当前时间戳
		nowSec = cDateTime.Seconds()
		#开始时间戳
		beginSec = int(time.mktime(datetime.datetime(*self.startTime).timetuple()))
		#结束时间戳
		endSec = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		if beginSec <= nowSec < endSec:
			#直接开启 并注册 结束tick
			YeYouJieRechargeMgr.OnStartYeYouJieRecharge(None,(beginSec, endSec))
			cComplexServer.RegTick(endSec - nowSec, YeYouJieRechargeMgr.OnEndYeYouJieRecharge)
		elif nowSec < beginSec:
			#注册开启 和 结束
			cComplexServer.RegTick(beginSec - nowSec, YeYouJieRechargeMgr.OnStartYeYouJieRecharge, (beginSec, endSec))
			cComplexServer.RegTick(endSec - nowSec, YeYouJieRechargeMgr.OnEndYeYouJieRecharge)

def LoadYeYouJieRechargeActive():
	for cfg in YeYouJieRechargeActive.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in LoadYeYouJieRechargeActive"
			continue
		cfg.pre_process()

class WangZheRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheRankActive.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		from Game.Activity.WangZheGongCe import WangZheRankMgr
		if self.startTime <= nowDate < self.endTime:
			WangZheRankMgr.OnStartWangZheRank(None,endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, WangZheRankMgr.OnEndWangZheRank)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, WangZheRankMgr.OnStartWangZheRank, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, WangZheRankMgr.OnEndWangZheRank)

def LoadWangZheRankActiveConfig():
	'''
	此处仅仅是为了触发开启而做的配置加载
	'''
	for cfg in WangZheRankActiveConfig.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in WangZheRankActiveConfig"
			return
		cfg.init_active()
	
class PassionRechargeRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionRechargeRankActive.txt")
	def __init__(self):
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.kaifuDay = int
	
	def init_active(self):
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		from Game.Activity.PassionAct import PassionRechargeRank
		if beginTime <= nowTime < endTime and WorldData.GetWorldKaiFuDay() >= self.kaifuDay :
			#当前开服时间  < 距离活动开启的天数 + 要求开服天数，返回
			if (cDateTime.Now() - self.startTime).days + self.kaifuDay > WorldData.GetWorldKaiFuDay():
				return
			
			#在开始和结束时间戳之间, 激活
			PassionRechargeRank.OnStartPassionRecharge(None, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, PassionRechargeRank.OnEndPassionRecharge)
		elif nowTime < beginTime :
			if (self.startTime - cDateTime.Now()).days + 1 + WorldData.GetWorldKaiFuDay() < self.kaifuDay:
				return
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, PassionRechargeRank.OnStartPassionRecharge, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, PassionRechargeRank.OnEndPassionRecharge)
			
			
def LoadPassionRechargeRankActiveConfig():
	global PassionRechargeRankActiveObj
	for cfg in PassionRechargeRankActiveConfig.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in PassionRechargeRankActive"
			return
		PassionRechargeRankActiveObj = cfg


class PassionConsumeRankActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionConsumeRankActive.txt")
	def __init__(self):
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.kaifuDay = int
	
	def init_active(self):
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		from Game.Activity.PassionAct import PassionConsumeRank
		if beginTime <= nowTime < endTime and WorldData.GetWorldKaiFuDay() >= self.kaifuDay:
			#当前开服时间  < 距离活动开启的天数 + 要求开服天数，返回
			if (cDateTime.Now() - self.startTime).days + self.kaifuDay > WorldData.GetWorldKaiFuDay():
				return
			#在开始和结束时间戳之间, 激活
			PassionConsumeRank.OnStartPassionConsume(None, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, PassionConsumeRank.OnEndPassionConsume)
		elif nowTime < beginTime:
			if (self.startTime - cDateTime.Now()).days + 1 + WorldData.GetWorldKaiFuDay() < self.kaifuDay:
				return
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, PassionConsumeRank.OnStartPassionConsume, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, PassionConsumeRank.OnEndPassionConsume)

def LoadPassionConsumeRankActiveConfig():
	global PassionConsumeRankActiveObj
	for cfg in PassionConsumeRankActiveConfig.ToClassType():
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in PassionConsumeRankActive"
			return
		PassionConsumeRankActiveObj = cfg


class GuBaoTanMiActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GuBaoTanMiActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		from Game.Activity.GuBaoTanMi import GuBaoTanMiMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			GuBaoTanMiMgr.OpenActive(None, (self.activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, GuBaoTanMiMgr.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, GuBaoTanMiMgr.OpenActive, (self.activeID, endTime))
			cComplexServer.RegTick(endTime - nowTime, GuBaoTanMiMgr.CloseActive)
		
def LoadGuBaoTanMiActiveConfig():
	global GuBaoTanMiActive_Dict
	for cfg in GuBaoTanMiActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in GuBaoTanMiActive_Dict"
			return
		GuBaoTanMiActive_Dict[cfg.activeID] = cfg


class DELoginRewardActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DELoginRewardActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = eval
		self.endTime = eval
		self.totalDay = int
	
	def Active(self):
		from Game.Activity.DoubleEleven import DELoginRewardMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			DELoginRewardMgr.OpenActive(None, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DELoginRewardMgr.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, DELoginRewardMgr.OpenActive, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DELoginRewardMgr.CloseActive)

def LoadDELoginRewardActive():
	'''
	加载并启动活动
	'''
	for cfg in DELoginRewardActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DELoginRewardActive_Dict"
			continue
		cfg.Active()
	

class DETopicActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DETopicActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = eval
		self.endTime = eval
		self.totalDay = int
	
	def Active(self):
		from Game.Activity.DoubleEleven import DETopicMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			DETopicMgr.OpenActive(None, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DETopicMgr.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, DETopicMgr.OpenActive, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DETopicMgr.CloseActive)

def LoadDETopicActive():
	'''
	加载并启动活动
	'''
	for cfg in DETopicActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DETopicActive_Dict"
			continue
		cfg.Active()
	

class DEGroupBuyActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DEGroupBuyActive.txt")
	def __init__(self):
		self.activeName = str
		self.beginTime = eval
		self.endTime = eval
		self.totalDay = int
	
	def Active(self):
		from Game.Activity.DoubleEleven import DEGroupBuyMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			DEGroupBuyMgr.OpenActive(None, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DEGroupBuyMgr.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, DEGroupBuyMgr.OpenActive, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DEGroupBuyMgr.CloseActive)

def LoadDEGroupBuyActive():
	'''
	加载并启动活动
	'''
	for cfg in DEGroupBuyActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DEGroupBuyActive"
			continue
		cfg.Active()
	

class DEQiangHongBaoActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DEQiangHongBaoActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = eval
		self.endTime = eval
		self.totalDay = int
	
	def Active(self):
		from Game.Activity.DoubleEleven import DEQiangHongBaoMgr
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			DEQiangHongBaoMgr.OpenActive(None, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DEQiangHongBaoMgr.CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, DEQiangHongBaoMgr.OpenActive, (endTime))
			cComplexServer.RegTick(endTime - nowTime, DEQiangHongBaoMgr.CloseActive)

def LoadDEQiangHongBaoActive():
	'''
	加载并启动活动
	'''
	for cfg in DEQiangHongBaoActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DEQiangHongBaoActive"
			continue
		cfg.Active()


class PassionTJHCActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTJHCActive.txt")
	def __init__(self):
		self.activeName = str
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.kaifuDay = int
	
	def Active(self):
		from Game.Activity.PassionAct import PassionTJHCMgr
		
		beginTime = int(time.mktime((self.beginTime).timetuple())) 
		endTime = int(time.mktime((self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime and WorldData.GetWorldKaiFuDay() >= self.kaifuDay:
			#当前开服时间  < 距离活动开启的天数 + 要求开服天数，返回
			if (cDateTime.Now() - self.beginTime).days + self.kaifuDay > WorldData.GetWorldKaiFuDay():
				return
			#激活
			PassionTJHCMgr.OpenActive(None, (endTime, self))
			cComplexServer.RegTick(endTime - nowTime, PassionTJHCMgr.CloseActive)
		elif nowTime < beginTime:
			if (self.beginTime - cDateTime.Now()).days + 1 + WorldData.GetWorldKaiFuDay() < self.kaifuDay:
				return
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, PassionTJHCMgr.OpenActive, (endTime, self))
			cComplexServer.RegTick(endTime - nowTime, PassionTJHCMgr.CloseActive)

def LoadPassionTJHCActive():
	'''
	加载并启动活动
	'''
	global PassionTJHCActive_Config
	for cfg in PassionTJHCActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in PassionTJHCActive"
			continue
		PassionTJHCActive_Config = cfg


class FestivalRebateActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("FestivalRebateActive.txt")
	def __init__(self):
		self.activeName = str
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.logDays = int
		self.minKaiFuDays = int
	
	def init_active(self):
		from Game.Activity.FestivalRebate import FestivalRebateMgr
		beginTime = int(time.mktime((self.beginTime).timetuple())) 
		endTime = int(time.mktime((self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			FestivalRebateMgr.StartFestivalRebate(None, (self, endTime))
			cComplexServer.RegTick(endTime - nowTime, FestivalRebateMgr.EndFestivalRebate)
		elif nowTime < beginTime:
			cComplexServer.RegTick(beginTime - nowTime, FestivalRebateMgr.StartFestivalRebate, (self, endTime))
			cComplexServer.RegTick(endTime - nowTime, FestivalRebateMgr.EndFestivalRebate)


def LoadFestivalRebateActive():
	global FestivalRebate_Active_Control
	for cfg in FestivalRebateActive.ToClassType():
		beginTime = cfg.beginTime
		endTime = cfg.endTime
		logDays = cfg.logDays
		if beginTime > endTime:
			print "GE_EXC, FestivalRebateActive Error:beginTime(%s) > endTime(%s)" % (beginTime, endTime)
		
		interval = endTime - beginTime
		totalDays = interval.days + (1 if interval.seconds > 0 else 0)
		if not(0 < logDays <= totalDays / 2):
			print "GE_EXC,FestivalRebateActive Error:0 < logDays(%s) <= totalDays(%s) / 2" % (logDays, totalDays)
		
		FestivalRebate_Active_Control = cfg


class SecretGradenActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SecretGradenActive.txt")
	def __init__(self):
		self.activeID = int
		self.activeName = str
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		from Game.Activity.SecretGarden import SecretGardenMgr
		beginTime = int(time.mktime((self.beginTime).timetuple())) 
		endTime = int(time.mktime((self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			SecretGardenMgr.StartSecretGarden(None, (self, endTime))
			cComplexServer.RegTick(endTime - nowTime, SecretGardenMgr.EndSecretGarden)
		elif nowTime < beginTime:
			cComplexServer.RegTick(beginTime - nowTime, SecretGardenMgr.StartSecretGarden, (self, endTime))
			cComplexServer.RegTick(endTime - nowTime, SecretGardenMgr.EndSecretGarden)


def LoadSecretGardenActive():
	global SecretGarden_Active_Control
	for cfg in SecretGradenActive.ToClassType():
		beginTime = cfg.beginTime
		endTime = cfg.endTime
		if beginTime >= endTime:
			print "GE_EXC, SecretGardenActive Error:beginTime(%s) > endTime(%s)" % (beginTime, endTime)
		
		SecretGarden_Active_Control = cfg
	
	TryStartSecretGarden()

def TryStartSecretGarden():
	'''
	尝试开启秘密花园
	'''
	if not WorldData.WD.returnDB:
#		print "GE_EXC,TryStartSecretGarden,not WorldData.WD.returnDB"
		return 
	
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
#		print "GE_EXC,TryStartSecretGarden,not WorldDataNotSync.WorldDataPrivate.returnDB"
		return
	
	global SecretGarden_Active_Control
	if not SecretGarden_Active_Control:
#		print "GE_EXC,TryStartSecretGarden,not SecretGarden_Active_Control"
		return 
	
	configVersion = SecretGarden_Active_Control.activeID
	oldVersion = WorldDataNotSync.GetSecretGardenVersion()
	if oldVersion > configVersion:
		print "GE_EXC, TryStartSecretGarden, oldVersion(%s) >= configVersion(%s)" % (oldVersion, configVersion)
		return 
	
	SecretGarden_Active_Control.init_active()
	
	
class CircularActiveConfig(TabFile.TabLine):
	startTickId = 0
	endTickId = 0
	FilePath = FILE_FOLDER_PATH.FilePath("CircularActive.txt")
	def __init__(self):
		self.activeID = int
		self.activeType = int
		self.name = str
		
		self.kaifuDay = self.GetEvalByString	#这个活动开启需要的服务器开服天数区间[1~11]#闭区间
		self.startDate = self.GetEvalByString	#第一次开启的日期
		self.startDays = int					#开启持续天数(注意，开启的持续天数不能跨越大于2个开服时间区间)
		self.circularDays = int					#结束后隔多少天会重新开启
		self.startType = int

	def Preprocess(self, kaifuday):
		if kaifuday > self.kaifuDay[1]:
			#当前开服时间大于这个活动的需求时间，证明是一个上一个阶段的活动
			#需要判断如果这个活动当前还是处于开启状态下，开启的时间区间内，这个服务器的开服时间是否也时候这个活动
			self.CheckBeforeOpen(kaifuday)
		elif kaifuday >= self.kaifuDay[0] and kaifuday <= self.kaifuDay[1]:
			#刚刚好处在这个开服天数区间内
			#检测这个活动是否需要开启或者等待一段时间开启
			#注意等待时间中服务器产生了阶段提升，则不开启这个活动
			self.CheckNowOpen(kaifuday)
		else:
			#当前开服时间小于配置的时间区间，暂时不做处理,等待达到的时候再检测
			pass

	def CheckBeforeOpen(self, kaifuday):
		#上一个阶段才会开启的活动
		nowdate = cDateTime.Now().date()
		nowSec = cDateTime.Seconds()
		#第一次开启的日期
		startdate = datetime.datetime(*self.startDate)
		#循环开启周期天数 = 开启天数 + 结束后到下一次开启的天数
		circularDays = self.startDays + self.circularDays
		#开启日期到当前日期过了多少天
		overdays = (nowdate - startdate.date()).days
		if  overdays <= 0:
			#不是这个阶段，并且还没开启过一次的活动
			return
		
		circularpassDays = overdays / circularDays * circularDays
		#计算当前天处于最近的一个循环周期中的天数
		start_overdays = overdays - circularpassDays
		
		if start_overdays > self.startDays:
			#处于关闭期间内,或者这个活动已经结束了
			return
		
		#当前天处于开启期间内
		#上次服务器转换类型时和当前的天数差
		changeDays = kaifuday - self.kaifuDay[1]
		if changeDays > start_overdays:
			#在服务器装备类型之后才开启的活动，证明这个活动不曾在上一阶段开启过
			return
		
		#在上一个阶段开启过，并且没有结束，持续到服务器跨期,这个时候应该要把这个活动开启来
		enddays = self.startDays - start_overdays
		#记录这个活动结束时间戳
		self.endSecs = int(time.mktime(nowdate.timetuple())) + enddays * OneDaySecs
		self.PrepareActive(10, self.endSecs - nowSec)
		
	def CheckNowOpen(self, kaifuday):
		#刚好处在这个开服天数内的活动
		#当前日期
		nowdate = cDateTime.Now().date()
		#当前时间戳
		nowSec = cDateTime.Seconds()
		#第一次开启的日期
		startdate = datetime.datetime(*self.startDate)
		#循环开启周期天数 = 开启天数 + 结束后到下一次开启的天数
		circularDays = self.startDays + self.circularDays
		#开启日期到当前日期过了多少天
		overdays = (nowdate - startdate.date()).days
		
		if overdays == 0:
			#者刚刚好开启
			startSecs = int(time.mktime(startdate.timetuple()))
			#注册结束时间触发 结束触发秒数 = 结束天的秒数时间戳 - 当前时间戳
			#记录这个活动结束时间戳
			self.endSecs = startSecs + self.startDays * OneDaySecs
			endTickSec = self.endSecs - nowSec
			#按照时间开始触发，或者已经过了开始时间了，但是还在持续时间内，10秒后开启这个活动
			self.PrepareActive(max(startSecs - nowSec, 10), endTickSec)
		elif overdays < 0:
			#还没有开启
			#判断这么多天后，服务器是否会跨期(注意overdays 是负数，所以用减法)
			if kaifuday - overdays > self.kaifuDay[1]:
				#开服天数已经跨期了，不要再开启了
				return 
			#没有跨期，等待开启
			startSecs = int(time.mktime(startdate.timetuple()))
			#注册结束时间触发 结束触发秒数 = 结束天的秒数时间戳 - 当前时间戳
			#记录这个活动结束时间戳
			self.endSecs = startSecs + self.startDays * OneDaySecs
			#按照时间开始触发，或者已经过了开始时间了，但是还在持续时间内，10秒后开启这个活动
			self.PrepareActive(max(startSecs - nowSec, 10), self.endSecs - nowSec)
		else:
			#当前日期比第一次开启日期大，这个活动已经开启过一次或者多次
			#计算已经进行的循环次数的跨越天数
			circularpassDays = overdays / circularDays * circularDays
			#计算当前天处于最近的一个循环周期中的天数
			start_overdays = overdays - circularpassDays
			if start_overdays < self.startDays:
				#活动开启日期，开服天数不满足要求的就不给开
				if self.startType and ((kaifuday - overdays) > self.kaifuDay[1] or (kaifuday - overdays) < self.kaifuDay[0]):
					return
				#属于开启期内，需要马上开启,并且计算结束天数
				enddays = self.startDays - start_overdays
				#记录这个活动结束时间戳
				self.endSecs = int(time.mktime(nowdate.timetuple())) + enddays * OneDaySecs
				self.PrepareActive(10, self.endSecs - nowSec)
			else:
				#处于等待开启时间段,计算还有多少天要开启
				nextOpendays = circularDays - start_overdays
				if kaifuday + nextOpendays > self.kaifuDay[1]:
					#开服天数已经跨期了，不要再开启了
					return
				
				#开启tick秒数 = 当当期时间 + 开启天数
				tickSec = int(time.mktime(nowdate.timetuple())) + nextOpendays * OneDaySecs - nowSec
				#结束时间
				self.endSecs = tickSec + self.startDays * OneDaySecs + nowSec
				self.PrepareActive(tickSec, self.endSecs - nowSec)
	
	def PrepareActive(self, startSec, endSec):
		#准备一次活动
		if self.startTickId:
			print "GE_EXC, repeat PrepareActive Start in CircularAcitve (%s)" % self.activeID
			cComplexServer.UnregTick(self.startTickId)
		
		if self.endTickId:
			print "GE_EXC, repeat PrepareActive End in CircularAcitve (%s)" % self.activeID
			cComplexServer.UnregTick(self.endTickId)
		
		#超过30天，不准备下一次开启
		if  startSec > 30 * 24 * 3600:
			return
		
		self.startTickId = cComplexServer.RegTick(startSec, StartActive, self.activeID)
		self.endTickId = cComplexServer.RegTick(endSec, EndActive, self.activeID)

	def ForceTrigger(self):
		#强制触发一次
		if self.startTickId:
			#准备开启的，没有开启，取消开启，取消关闭
			if not self.endTickId:
				print "GE_EXC, ForceTrigger error"
			cComplexServer.UnregTick(self.startTickId)
			cComplexServer.UnregTick(self.endTickId)
		elif self.endTickId:
			#已经开启，没有关闭的，强制触发一次关闭
			cComplexServer.TiggerTick(self.endTickId, True)
		self.startTickId = 0
		self.endTickId = 0
		self.endSecs = 0
	
	def AfterNewDay(self, kaifuday):
		#新的一天,检测是否进入一个新的服务器活动阶段
		if kaifuday != self.kaifuDay[0]:
			return
		#踏入新的时期，检测是否要开启活动
		self.CheckNowOpen(kaifuday)
	
	def CheckStart(self):
		#上一轮活动结束，检测下一次循环是否符合开启条件
		kaifuday = WorldData.GetWorldKaiFuDay()
		if kaifuday > self.kaifuDay[1] or kaifuday + self.circularDays > self.kaifuDay[1]:
			#这个活动已经不属于这个服务器的开服时期了，获取下次开启的时候，这个服务器也不适合开启这个活动了
			return
		
		#下次还是适合开启
		nowdate = cDateTime.Now().date()
		nowSec = cDateTime.Seconds()
		tickSec = int(time.mktime(nowdate.timetuple())) + self.circularDays * OneDaySecs - nowSec
		#结束时间戳
		self.endSecs = tickSec + self.startDays * OneDaySecs + nowSec
		
		

		self.PrepareActive(tickSec, self.endSecs - nowSec)

def StartAcitve_GM(activeId, activeType, endSecs):
	#GM指令开启活动  活动ID，活动类型，结束秒时间戳
	acfg = CircularActiveConfig_Dict.get(activeId)
	if not acfg:
		print "GE_EXC, error in StartAcitve_GM not this cfg (%s)" % activeId
		return
	global CircularActiveCache_Dict
	if activeId in CircularActiveCache_Dict:
		print "GE_EXC, repeat StartAcitve_GM ", activeId
		return
	
	with Tra_CircularActive_Start:
		CircularActiveCache_Dict[activeId] = (activeType, endSecs)
		Event.TriggerEvent(Event.Eve_StartCircularActive, None, activeType)
		#通知所有的玩家活动开始了
		cNetMessage.PackPyMsg(CircularActive_StartActive, (activeType, endSecs, activeId))
		cRoleMgr.BroadMsg()
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveCircularActiveStart, (activeId, activeType))
		
		acfg.endTickId = cComplexServer.RegTick(endSecs - cDateTime.Seconds(), EndActive, activeId)

def CancleActive_GM(activeId):
	global Cancle_GM_Set
	if activeId in Cancle_GM_Set:
		print "GE_EXC, repeat CancleActive_GM (%s)" %  activeId
		return
	
	global CircularActiveCache_Dict
	if activeId in CircularActiveCache_Dict:
		print "GE_EXC, can not cancle this active  is already Start !"
		return
	
	Cancle_GM_Set.add(activeId)


def StartActive(callArgv, regparam):
	#开启一个活动
	activeId = regparam
	cfg = CircularActiveConfig_Dict.get(activeId)
	if not cfg:
		print "GE_EXC, error in StartActive not this cfg (%s)" % activeId
		return
	global Cancle_GM_Set
	if activeId in Cancle_GM_Set:
		#GM指令提前结束的
		print "GE_EXC StartActive ID(%s) name(%s) but is cancle " % (activeId, cfg.name)
		return
	
	isRepeat = False
	with Tra_CircularActive_Start:
		#tickId要置成0
		cfg.startTickId = 0
		
		global CircularActiveCache_Dict
		for aId, aData in CircularActiveCache_Dict.items():
			if cfg.activeType != aData[0]:
				continue
			
			isRepeat = True
			
			
			#有相同类型的活动正在开启
			aCfg = CircularActiveConfig_Dict.get(aId)
			if not aCfg:
				return
			
			if cfg.kaifuDay < aCfg:
				#需求开服天数比正在开启的活动小, 取消结束tick
				if cfg.endTickId:
					cComplexServer.UnregTick(cfg.endTickId)
					cfg.endTickId = 0
				return
			
			#删除缓存活动ID
			if aId in CircularActiveCache_Dict:
				del CircularActiveCache_Dict[aId]
			#取消关闭tick
			cComplexServer.UnregTick(aCfg.endTickId)
			aCfg.endTickId = 0
			#替换活动ID
			Event.TriggerEvent(Event.Eve_ChangeCirActID, None, (cfg.activeType, activeId))
			#结束
			cNetMessage.PackPyMsg(CircularActive_EndActive, cfg.activeType)
			cRoleMgr.BroadMsg()
			
		CircularActiveCache_Dict[activeId] = (cfg.activeType, cfg.endSecs)
		
		if not isRepeat:
			#没有重复的话才触发
			Event.TriggerEvent(Event.Eve_StartCircularActive, None, cfg.activeType)
		
		#通知所有的玩家活动开始了
		cNetMessage.PackPyMsg(CircularActive_StartActive, (cfg.activeType, cfg.endSecs, activeId))
		cRoleMgr.BroadMsg()
		
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveCircularActiveStart, (activeId, cfg.activeType))

def EndActive(callArgv, regparam):
	#关闭一个活动
	activeId = regparam
	cfg = CircularActiveConfig_Dict.get(activeId)
	if not cfg:
		print "GE_EXC, error in EndActive not this cfg (%s)" % activeId
		return
	
	with Tra_CircularActive_End:
		cfg.endTickId = 0
		Event.TriggerEvent(Event.Eve_EndCircularActive, None, cfg.activeType)
		
		global CircularActiveCache_Dict
		if activeId in CircularActiveCache_Dict:
			del CircularActiveCache_Dict[activeId]
		
		
		#通知所有的玩家活动结束了
		cNetMessage.PackPyMsg(CircularActive_EndActive, cfg.activeType)
		cRoleMgr.BroadMsg()
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveCircularActiveEnd, (activeId, cfg.activeType))
		
		if callArgv is True:
			#强制触发的，不用检测
			return
		#10秒后再次检测下次开启时机
		cComplexServer.RegTick(10, CheckStart, cfg)

def CheckStart(callArgv, regparam):
	regparam.CheckStart()


def LoadConfig():
	#读取配置表
	global CircularActiveConfig_Dict
	for cac in CircularActiveConfig.ToClassType():
		CircularActiveConfig_Dict[cac.activeID] = cac


def AfterLoadWorldData(param1, param2):
	#载入世界数据之后,处理所有的循环活动
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for cfg in CircularActiveConfig_Dict.itervalues():
		cfg.Preprocess(kaifuDay)
	
	#激情活动_天降横财触发启动
	PassionTJHCActive_Config.Active()
	#捕鱼活动触发启动
	OpenCatchingFishActive()
	#激情活动——充值排名触发启动
	PassionRechargeRankActiveObj.init_active()
	#激情活动——消费排名触发启动
	PassionConsumeRankActiveObj.init_active()
	#春节大回馈
	FestivalRebate_Active_Control.init_active()
	#尝试开启秘密花园
	TryStartSecretGarden()
	
def AfterLoadWorldDataNotSync(param1, param2):
	#载回不广播客户端世界数据后, 尝试激活勇者英雄坛、跨服鲜花榜
	global BraveHero_Dict, KuafuFlowerRank_Dict
	for cfg in BraveHero_Dict.itervalues():
		cfg.Active()
	
	for cfg in KuafuFlowerRank_Dict.itervalues():
		cfg.Active()
	
	#尝试开启秘密花园
	TryStartSecretGarden()
	
def AfterSetKaiFuTime(param1, param2):
	#设置开服时间后
	#强制触发所有的tick,并且重新处理一次所有的活动
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for cfg in CircularActiveConfig_Dict.itervalues():
		cfg.ForceTrigger()
		cfg.Preprocess(kaifuDay)

def AfterNewDay():
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for cfg in CircularActiveConfig_Dict.itervalues():
		cfg.AfterNewDay(kaifuDay)

def SyncRoleOtherData(role, param):
	#角色登录同步数据
	global CircularActiveCache_Dict
	role.SendObj(CircularActive_AllData, CircularActiveCache_Dict)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadConfig()
		LoadBraveHeroActiveConfig()
		LoadHaoqiActiveConfig()
		LoadGroupBuyPartyBase()
		LoadRichRankActiveConfig()
		LoadChristmasHaoActiveConfig()
		LoadNewYearHaoActiveConfig()

		LoadLanternFestivalRankConfig()
		LoadSpringBActive()
		LoadGlamourRankActiveConfig()
		LoadLianChongRebateActive()
		LoadQingMingRankActiveConfig()
		LoadZaiXianJiangLiActive()
		LoadSuperPromptionControl()
		LoadYeYouJieRechargeActive()
		LoadWangZheRankActiveConfig()
		LoadPassionRechargeRankActiveConfig()
		LoadPassionConsumeRankActiveConfig()
		
		LoadTurnTableActiveConfig()
		LoadGuBaoTanMiActiveConfig()
		LoadCatchingFishActiveConfig()
		LoadKuafuFlowerRankActiveConfig()
		LoadDELoginRewardActive()
		LoadDETopicActive()
		LoadDEGroupBuyActive()
		LoadDEQiangHongBaoActive()
		LoadPassionTJHCActive()
		LoadFestivalRebateActive()
		LoadSecretGardenActive()
		
		CircularActive_AllData = AutoMessage.AllotMessage("CircularActive_AllData", "同步循环活动所有数据")
		CircularActive_StartActive = AutoMessage.AllotMessage("CircularActive_StartActive", "同步开启一个循环活动")
		CircularActive_EndActive = AutoMessage.AllotMessage("CircularActive_EndActive", "同步结束一个循环活动")
		
		Tra_CircularActive_Start = AutoLog.AutoTransaction("Tra_CircularActive_Start", "开启一个循环活动")
		Tra_CircularActive_End = AutoLog.AutoTransaction("Tra_CircularActive_End", "结束一个循环活动")
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, AfterLoadWorldDataNotSync)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay, 1)
