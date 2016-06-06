#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fashion.FashionForing")
#===============================================================================
# 时装激活，升星，升阶，鉴定。。。
#===============================================================================
import random
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt1, EnumInt8, EnumInt32
from Game.Role.Mail import Mail
from Game.Fashion import FashionConfig
from Game.Item import ItemConfig
from Game.Role import Event
from Game.Wing import WingMgr, WingConfig
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType

if "_HasLoad" not in dir():
	MAX_HOLE_LEVEL = 15	#最高的光环等级
	
	Fashion_BackInfo = AutoMessage.AllotMessage("Fashion_BackInfo", "返回时装界面相关信息")
	
	#日志
	FashionStarCost = AutoLog.AutoTransaction("FashionStarCost", "时装升星消耗")
	FashionOrderCost = AutoLog.AutoTransaction("FashionOrderCost", "时装升阶消耗")
	FashionIdeCost = AutoLog.AutoTransaction("FashionIdeCost", "时装鉴定消耗")
	FashionMail = AutoLog.AutoTransaction("FashionMail", "时装补发羽翼邮件")
	FashionHoleCost = AutoLog.AutoTransaction("FashionHoleCost", "时装升时装光环消耗")
	FashionActiveCost = AutoLog.AutoTransaction("FashionActiveCost", "时装激活消耗")
	FashionWardrobe = AutoLog.AutoTransaction("FashionWardrobe", "时装衣柜升级")
	
def FashionUpStar(role, param):
	'''
	时装升星
	@param role:
	@param param:
	'''
	
	backId, (Fashioncoding, Starcoding) = param
	#等级不足
	if role.GetLevel() < EnumGameConfig.FORING_FASHION_LEVEL:
		return
	
	if Starcoding:
		if role.ItemCnt(Starcoding) < 1:
			return
	
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	actived_dict = FashionGlobalMgr.fashion_active_dict
	if Fashioncoding not in actived_dict:#激活的时装才能升星
		role.Msg(2, 0, GlobalPrompt.FASHION_MUST_ACTIVE)
		return
	#获取该时装的星阶和幸运值
	#{0:是否鉴定, 1:时装阶数, 2:套装ID, 3:时装星数, 4:鉴定额外幸运值， 升星祝福值， 升阶祝福值}
	fashionData = actived_dict.get(Fashioncoding)
	starNum, lucky = fashionData[3], fashionData[5]
	
	item_cfg = ItemConfig.ItemCfg_Dict.get(Fashioncoding)
	if not item_cfg:
		return
	
	key = None
	if Fashioncoding in FashionConfig.STAR_CODING_SET:
		#通过时装coding判断升星消耗
		key = (Fashioncoding, starNum)
	else:
		key = (item_cfg.posType, starNum)
		#根据星级取配置
	cfg = FashionConfig.FASHION_STAR_DICT.get(key)
	if not cfg:
		return
	if not cfg.nextStar:#没有下一级
		return
	if Starcoding and Starcoding != cfg.Starcoding:#幸运符coding不对
		return
	coding, cnt = cfg.needItem
	if role.ItemCnt(coding) < cnt:#道具不足
		return
	with FashionStarCost:
		if role.DelItem(coding, cnt) < cnt:
			return
		if Starcoding:#有幸运符100%成功
			packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
			codingGatherDict = packageMgr.codingGather.get(Starcoding)
			if not codingGatherDict:
				return
			delItemId = 0
			for itemId, item in codingGatherDict.iteritems():
				if item.IsDeadTime():
					continue
				delItemId = itemId
				break
			if not delItemId:#全部是过期道具
				return#不消耗时装精华,不会触发精彩活动三三
			role.DelProp(delItemId)
			#重新设定时装图鉴的星数
			FashionGlobalMgr.SetStarByCoding(Fashioncoding, cfg.nextStar)
			
			role.CallBackFunction(backId, [1, Fashioncoding, cfg.nextStar, 0])#1代表成功，id, 现在的阶数，幸运值
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFashionStarSuc, (Fashioncoding, cfg.nextStar))
			role.Msg(2, 0, GlobalPrompt.FASHION_STAR_SUC_MSG)
			
			#触发 情人目标-亲密恋人衣服升星
			if Fashioncoding == EnumGameConfig.QinmiLover_Coding:
				Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_ClothesStar, cfg.nextStar))
		else:
			if lucky < cfg.minLucky:#当前幸运值小于最小幸运值，直接按失败处理
				addLucky = random.randint(cfg.addLucky[0], cfg.addLucky[1])
				nowLucky = min(lucky + addLucky, cfg.maxLucky)
				fashionData[5] = nowLucky
				role.CallBackFunction(backId, [0, Fashioncoding, starNum, nowLucky])#0代表失败，id, 现在的星级，幸运值
				role.Msg(2, 0, GlobalPrompt.FASHION_STAR_FAILED_MSG % addLucky)
			else:
				#额外的幸运
				extend_random = int(lucky / (cfg.maxLucky * 1.0) * 10000)
				#总共的成功率
				total = extend_random + cfg.baseLucky
				
				randomNum = random.randint(1, 10000)
				if randomNum <= total:#升星成功
					#修改图鉴的对应时装的星级
					FashionGlobalMgr.SetStarByCoding(Fashioncoding, cfg.nextStar)
					
					AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFashionStarSuc, (Fashioncoding, cfg.nextStar))
					role.CallBackFunction(backId, [1, Fashioncoding, cfg.nextStar, 0])#1代表成功，id, 现在的星级，幸运值
					role.Msg(2, 0, GlobalPrompt.FASHION_STAR_SUC_MSG)
	
					#触发 情人目标-亲密恋人衣服升星
					if Fashioncoding == EnumGameConfig.QinmiLover_Coding:
						Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_ClothesStar, cfg.nextStar))
				else:#升星失败
					addLucky = random.randint(cfg.addLucky[0], cfg.addLucky[1])
					if lucky >= cfg.maxLucky:#当前的幸运值已为最大值
						return
					nowLucky = min(lucky + addLucky, cfg.maxLucky)
					fashionData[5] = nowLucky
					role.CallBackFunction(backId, [0, Fashioncoding, starNum, nowLucky])#0代表失败，id, 现在的星级，幸运值
					role.Msg(2, 0, GlobalPrompt.FASHION_STAR_FAILED_MSG % addLucky)
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_FashionUpStar, (role, cnt))
	
def FashionUpOrder(role, param):
	'''
	时装升阶
	@param role:
	@param param:
	'''
	backId, (fashionCoding, coding) = param
	#等级不足
	if role.GetLevel() < EnumGameConfig.FORING_FASHION_LEVEL:
		return
	
	if coding:#没有该道具
		if role.ItemCnt(coding) < 1:
			return
		
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	actived_dict = FashionGlobalMgr.fashion_active_dict
	if fashionCoding not in actived_dict:#激活的时装才能升阶
		role.Msg(2, 0, GlobalPrompt.FASHION_MUST_ACTIVE)
		return
	fashionData = actived_dict.get(fashionCoding)
	#{是否鉴定, 时装阶数, 套装ID, 时装星数, 鉴定额外幸运值， 升星祝福值， 升阶祝福值}
	#未鉴定的时装不让进阶
	if not fashionData[0]:
		return
	#获取该装备阶数和幸运值
	order, lucky = fashionData[1], fashionData[6]
	
	item_cfg = ItemConfig.ItemCfg_Dict.get(fashionCoding)
	if not item_cfg:
		return
	
	key = None
	if fashionCoding in FashionConfig.ORDER_CODING_SET:
		key = (fashionCoding, order)
	else:
		key = (item_cfg.posType, order)
	cfg = FashionConfig.FASHION_ORDER_DICT.get(key)
	if not cfg:
		return
	if not cfg.nextOrder:#没有下一级
		return
	if coding and coding != cfg.Luckcoding:#幸运符coding不对
		return
	needItem, cnt = cfg.needItem
	if role.ItemCnt(needItem) < cnt:
		return
	
	with FashionOrderCost:
		if role.DelItem(needItem, cnt) < cnt:
			return
		if coding:#有幸运符100%成功
			packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
			codingGatherDict = packageMgr.codingGather.get(coding)
			if not codingGatherDict:
				return
			delItemId = 0
			for itemId, item in codingGatherDict.iteritems():
				if item.IsDeadTime():
					continue
				delItemId = itemId
				break
			if not delItemId:
				return
			role.DelProp(delItemId)
			#重新设定时装图鉴的阶数
			FashionGlobalMgr.ResetOrderbyCoding(fashionCoding, cfg.nextOrder)
			
			role.CallBackFunction(backId, [1, fashionCoding, cfg.nextOrder, 0])#1代表成功，id, 现在的阶数，幸运值
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFashionOrderSuc, (fashionCoding, cfg.nextOrder))
			role.Msg(2, 0, GlobalPrompt.FASHION_ORDER_SUC_MSG)
			
			#触发 情人目标-亲密恋人衣服升阶
			if fashionCoding == EnumGameConfig.QinmiLover_Coding:
				Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_ClothesStage, cfg.nextOrder))
		else:
			if lucky < cfg.minLucky:#当前幸运值小于最小幸运值，直接按失败处理
				addLucky = random.randint(cfg.addLucky[0], cfg.addLucky[1])
				nowlucky = min(cfg.maxLucky, lucky + addLucky)
				fashionData[6] = nowlucky
				role.CallBackFunction(backId, [0, fashionCoding, order, nowlucky])#0代表失败，现在的阶数，幸运值
				role.Msg(2, 0, GlobalPrompt.FASHION_ORDER_FAILED_MSG % addLucky)
			else:
				#额外的幸运
				extend_random = int(lucky / (cfg.maxLucky * 1.0) * 10000)
				#总共的成功率
				total = extend_random + cfg.baseLucky
				
				randomNum = random.randint(1, 10000)
				if randomNum <= total:#升阶成功
					#重新设定时装图鉴的阶数
					FashionGlobalMgr.ResetOrderbyCoding(fashionCoding, cfg.nextOrder)
					
					role.CallBackFunction(backId, [1, fashionCoding, cfg.nextOrder, 0])#1代表成功，id, 现在的阶数，幸运值
					AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFashionOrderSuc, (fashionCoding, cfg.nextOrder))
					role.Msg(2, 0, GlobalPrompt.FASHION_ORDER_SUC_MSG)
					
					#触发 情人目标-亲密恋人衣服升阶
					if fashionCoding == EnumGameConfig.QinmiLover_Coding:
						Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_ClothesStage, cfg.nextOrder))
				else:#失败
					addLucky = random.randint(cfg.addLucky[0], cfg.addLucky[1])
					if lucky >= cfg.maxLucky:#当前的幸运值已为最大值
						return
					nowlucky = min(cfg.maxLucky, lucky + addLucky)
					fashionData[6] = nowlucky
					role.CallBackFunction(backId, [0, fashionCoding, order, nowlucky])#0代表失败，现在的阶数，幸运值
					role.Msg(2, 0, GlobalPrompt.FASHION_ORDER_FAILED_MSG % addLucky)
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_FashionUpOrder, (role, cnt))
				
def FashionIde(role, param):
	'''
	时装鉴定
	@param role:
	@param param:
	'''
	coding = param
	#等级不足
	if role.GetLevel() < EnumGameConfig.IDE_FASHION_LEVEL:
		return
	
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	if not FashionGlobalMgr:
		return
	#该时装coding还未激活
	if coding not in FashionGlobalMgr.fashion_active_dict:
		return
	#已经鉴定了
	fashionData = FashionGlobalMgr.fashion_active_dict.get(coding)
	if fashionData[0] != 0:
		return
	
	cfg = ItemConfig.ItemCfg_Dict.get(coding)
	if not cfg:
		print "GE_EXC,can not find coding(%s) in GetIdePro" % coding
		return
	#道具不足
	needItem, cnt = cfg.needItem
	if role.ItemCnt(needItem) < cnt:
		return
	
	with FashionIdeCost:
		if role.DelItem(needItem, cnt) < cnt:
			return
		#额外幸运值
		extendPro = FashionGlobalMgr.GetIdxExtendPro(coding)
		randomNum = random.randint(1, 10000)
		suc_state = False
		if randomNum <= cfg.Idepro + extendPro:#成功
			FashionGlobalMgr.SetIdeByCoding(coding)
			suc_state = True
		else:
			#增加失败幸运值
			FashionGlobalMgr.AddIdeExtendPro(coding, cfg.FaileIdepro)
			role.Msg(2, 0, GlobalPrompt.FASHION_IDE_FAILED)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFashionJD, (coding, suc_state))
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_FashionUpOrder, (role, cnt))

def RequestActiveFashion(role, param):
	'''
	客户端玩家激活时装
	@param role:
	@param param:
	'''
#	if role.GetLevel() < EnumGameConfig.ACTIVE_FASHION_LEVEL:
#		return
	coding = param
	item_cfg = ItemConfig.ItemCfg_Dict.get(coding)
	if not item_cfg:
		return
	if role.GetLevel() < item_cfg.needlevel:
		return
	ActiveFashion(role, coding)
	
def ActiveFashion(role, coding):
	#激活时装
	cfg = ItemConfig.ItemCfg_Dict.get(coding)
	if not cfg:
		print "GE_EXC,can not find coding(%s) in GetIdePro" % coding
		return

	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	actived_dict = FashionGlobalMgr.fashion_active_dict
	
	if coding in actived_dict:#该时装类型已经激活
		role.Msg(2, 0, GlobalPrompt.FASHION_ACTIVE_FALSE)
		return
	
	#背包里没有该时装道具
	if role.ItemCnt(coding) < 1:
		role.Msg(2, 0, GlobalPrompt.FASHION_ACTIVE_FAILED % cfg.name)
		return
	
	with FashionActiveCost:
		role.DelItem(coding, 1)
		#新激活的时装是未鉴定,阶数为0的
		actived_dict[coding] = [0, 0, cfg.suitId, 0, 0, 0, 0]#是否鉴定，时装阶数，套装ID, 时装星数,临时幸运值,升星祝福值,升阶祝福值
		#设定华丽度
		FashionGlobalMgr.SetGorByCoding(coding)
		#重算基础属性
		FashionGlobalMgr.ReSetAllBasePro()
		role.GetPropertyGather().ReSetRecountFashionFlag()
		#遍历下，看该时装是否满足套装属性
		suitCnt = 0
	
		for fcoding, _ in actived_dict.iteritems():
			fashion_cfg = ItemConfig.ItemCfg_Dict.get(fcoding)
			if not fashion_cfg:
				print "GE_EXC,can not find coding(%s) in GetSuitPro" % fcoding
				continue
			if not fashion_cfg.suitId:
				continue
			if fashion_cfg.suitId == cfg.suitId:
				suitCnt += 1
				
		if suitCnt:#有套装属性，需要属性重算
			#时装套装属性重算
			FashionGlobalMgr.ResetFashionSuit()
			role.GetPropertyGather().ReSetRecountFashionSuitFlag()
		
		if role.GetI8(EnumInt8.FashionHaloLevel) > 0:
			#重算光环属性
			role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
		
		#进行羽翼激活
		if cfg.wingId:
			ActiveWing(role, cfg.wingId)
			
		if coding == 37009:
			from Game.Fashion import FashionOperate
			FashionOperate.OnSaveFashion(role, {1:0, 2:0, 3:0, 4:coding})
			
		role.Msg(2, 0, GlobalPrompt.FASHION_ACTIVE_SUC % cfg.name)
	
def RequestActiveWing(role, param):
	'''
	客户端请求激活羽翼
	@param role:
	@param param:
	'''
	wingId = param
	ActiveWing(role, wingId)
	
def ActiveWing(role, wingId):
	#激活羽翼
	wingDict = role.GetObj(EnumObj.Wing)[1]
	wingEvolveDict = role.GetObj(EnumObj.Wing)[2]
	
	#是否已经拥有这个翅膀
	if wingId in wingDict:
		return
	#是否有这个翅膀配置
	wingConfig = WingConfig.WING_BASE.get((wingId, 1))
	if not wingConfig:
		return
	
	fashionCfg = FashionConfig.FASHION_WING_DICT.get(wingId)
	if not fashionCfg:
		return
	
	fashionId = fashionCfg.coding
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	#假如翅膀对应的时装未激活，就判断是否有这个道具，没有的话不给激活
	if fashionId not in FashionGlobalMgr.fashion_active_dict:
		if role.ItemCnt(fashionId) < 1:
			role.Msg(2, 0, GlobalPrompt.FASHION_ACTIVE_WING_FALSE)
			return
	#等级，经验
	wingDict[wingId] = [1, 0]
	#属性重算
	role.ResetGlobalWingProperty()
	#发送给客户端
	role.SendObj(WingMgr.Wing_Show_Panel, (wingDict, wingEvolveDict))
	#提示
	role.Msg(2, 0, GlobalPrompt.FASHION_ACTIVE_WING_SUC % fashionCfg.name)
	#最新活动
	from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	LatestActivityMgr.GetFunByType(EnumLatestType.WingTrain_Latest, role)
	
def RequestFashionHole(role, param):
	'''
	客户端请求升级时装光环
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.FASHION_HOLE_LEVEL:
		return
	
	backId, _ = param
	
	FashionHaloLevel = role.GetI8(EnumInt8.FashionHaloLevel)
	
	cfg = FashionConfig.FASHION_HOLE_DICT.get(FashionHaloLevel)
	if not cfg:
		print "GE_EXC,can not find FashionHaloLevel(%s) in RequestFashionHole" % FashionHaloLevel
		return
	#已是最高级的了
	if not cfg.nextLevel: return
	
	itemCnt = role.ItemCnt(cfg.needCoding)
	#没有升级需要的道具
	if itemCnt <= 0:
		return
	global MAX_HOLE_LEVEL
	#倒数第二级，需要判断道具是否溢出
	now_exp = role.GetI32(EnumInt32.FashionHoleExp)
	if FashionHaloLevel == MAX_HOLE_LEVEL - 1:
		if now_exp + itemCnt * cfg.addexp > cfg.needexp:
			itemCnt = (cfg.needexp - now_exp) / cfg.addexp
	
	with FashionHoleCost:
		role.DelItem(cfg.needCoding, itemCnt)
		AddExp = itemCnt * cfg.addexp
		total_exp = now_exp + AddExp
		need_exp = cfg.needexp
		IsLevelUp = False
		while total_exp >= need_exp:
			IsLevelUp = True
			role.IncI8(EnumInt8.FashionHaloLevel, 1)
			total_exp -= need_exp
			if role.GetI8(EnumInt8.FashionHaloLevel) == MAX_HOLE_LEVEL:
				role.SetI32(EnumInt32.FashionHoleExp, 0)
				role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
				role.CallBackFunction(backId, 1)
				return
			new_cfg = FashionConfig.FASHION_HOLE_DICT.get(role.GetI8(EnumInt8.FashionHaloLevel))
			if not new_cfg:
				print "GE_EXC,Is Wrong in RequestFashionHole, can not find FashionHaloLevel(%s)" % role.GetI8(EnumInt8.FashionHaloLevel)
				return
			need_exp = new_cfg.needexp
		role.SetI32(EnumInt32.FashionHoleExp, total_exp)
		if IsLevelUp:
			role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
		role.CallBackFunction(backId, 1)
		
def RequestFashionUpwardrobe(role, param):
	'''
	客户端请求升级衣柜
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.FASHION_YIGUI_LEVEL:
		return
	WardrobeLevel = role.GetI8(EnumInt8.FashionWardrobeLevel)
	cfg = FashionConfig.FASHION_WARDROBE_DICT.get(WardrobeLevel)
	if not cfg:
		return
	if not cfg.nextLevel:#已是最高级
		return
	
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	gorgeous = FashionGlobalMgr.total_gorgeous
	
	if cfg.needexp > gorgeous:
		return
	with FashionWardrobe:
		role.IncI8(EnumInt8.FashionWardrobeLevel, 1)
		#重算鉴定属性
		FashionGlobalMgr.ResetFashionIde()
		role.ResetGlobalFashionProperty()
		
		
		
def ActiveWingSys(role, coding):
	#通过时装ID激活羽翼
	cfg = ItemConfig.ItemCfg_Dict.get(coding)
	if not cfg:
		print "GE_EXC,can not find coding(%s) in ActiveWingSys" % coding
		return
	wingId = cfg.wingId
	
	wingDict = role.GetObj(EnumObj.Wing)[1]
	#是否已经拥有这个翅膀
	if wingId in wingDict:
		return
	#等级，经验
	wingDict[wingId] = [1, 0]
	#属性重算
	role.ResetGlobalWingProperty()
	#提示
	role.Msg(2, 0, GlobalPrompt.FASHION_ACTIVE_WING_SUC % cfg.name)
	#最新活动
	from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	LatestActivityMgr.GetFunByType(EnumLatestType.WingTrain_Latest, role)
	
def SynRoleClient(role):
	#激活的时装数据，套装属性，鉴定属性，光环属性，时装总基础属性,每个时装的华丽值，总的华丽值
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	if not FashionGlobalMgr:
		return
	role.SendObj(Fashion_BackInfo, [FashionGlobalMgr.fashion_active_dict, FashionGlobalMgr.suit_pro_dict, FashionGlobalMgr.ide_pro_dict,\
												FashionGlobalMgr.hole_pro_dict, role.GetPropertyGather().fashion_p.p_dict, FashionGlobalMgr.Gorgeous_dict, \
												FashionGlobalMgr.total_gorgeous])

def SyncRoleOtherData(role, param):
	SynRoleClient(role)

def AfterLogin(role, param):
	#玩家登陆后
	if role.GetObj(EnumObj.En_RoleFashions) == {}:
		role.SetObj(EnumObj.En_RoleFashions, set())
		
	if not role.GetI1(EnumInt1.FashionState):#跟新第一次登陆
		role.SetI1(EnumInt1.FashionState, 1)
		#检测玩家是否有翅膀，有的话发翅膀对应的时装，用邮件
		wingDict = role.GetObj(EnumObj.Wing)[1]
		if not wingDict:#没有激活羽翼
			return
		ItemList = []
		for wingId, _ in wingDict.iteritems():
			wingCfg = FashionConfig.FASHION_WING_DICT.get(wingId)
			if not wingCfg:
				print "GE_EXC, can not find wingId(%s) in RevertWing" % wingId
				return
			ItemList.append((wingCfg.coding, 1))
		if not ItemList:
			return
		with FashionMail:
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.FASHION_MAIL_TITLE, \
						GlobalPrompt.FASHION_MAIL_SENDER, GlobalPrompt.FASHION_MAIL_DESC, ItemList)
			
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Fashion_Upstar", "客户端请求时装升星"), FashionUpStar)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Fashion_Uporder", "客户端请求时装升阶"), FashionUpOrder)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Fashion_Ide", "客户端请求时装鉴定"), FashionIde)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Fashion_Active", "客户端请求时装激活"), RequestActiveFashion)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Wing_Active", "客户端请求羽翼激活"), RequestActiveWing)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Fashion_Hole", "客户端请求升级时装光环"), RequestFashionHole)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Fashion_Upwardrobe", "客户端请求升级衣柜"), RequestFashionUpwardrobe)
