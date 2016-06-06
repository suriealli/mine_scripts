#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ElementSpirit.ElementSpiritMgr")
#===============================================================================
# 元素之灵 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.ElementSpirit import ElementSpiritConfig
from Game.Role.Data import EnumInt8, EnumInt32, EnumInt16


if "_HasLoad" not in dir():
	#日志
	Tra_ElementSpirit_SystemCorrect = AutoLog.AutoTransaction("Tra_ElementSpirit_SystemCorrect", "元素之灵_系统纠正衍生数据")
	Tra_ElementSpirit_Cultivate = AutoLog.AutoTransaction("Tra_ElementSpirit_Cultivate", "元素之灵_培养")
	Tra_ElementSpirit_Break = AutoLog.AutoTransaction("Tra_ElementSpirit_Break", "元素之灵_突破")
	Tra_ElementSpirit_ChooseSkillType = AutoLog.AutoTransaction("Tra_ElementSpirit_ChooseSkillType", "元素之灵_选择技能类型")


#===============================================================================
# 客户端请求
#===============================================================================
def OnChooseSpiritType(role, msg):
	'''
	元素之灵_选择元素之灵类型_请求
	@param msg: skillType 目标元素之灵技能类型
	'''
	if role.GetLevel() < EnumGameConfig.ElementSpiritNeedLevel:
		return
	
	targetSkillType = msg
	if targetSkillType not in ElementSpiritConfig.ElementSpirit_SkillConfig_Dict:
		return
	
	needRMB = 0
	oldSkillType = role.GetI8(EnumInt8.ElementSpiritSkillType)
	if oldSkillType == targetSkillType:
		return
	
	prompt = GlobalPrompt.ElementSpirit_Tips_FirstChoose
	
	#当前已经有类型了 切换要钱！ 否则，即首次免费选择
	if oldSkillType:
		prompt = GlobalPrompt.ElementSpirit_Tips_ChangeType % ElementSpiritConfig.ElementSpirit_SpiritName_Dict.get(targetSkillType, "")
		needRMB = EnumGameConfig.ElementSpirit_ChangeSkillTypeRMB
	
	if role.GetUnbindRMB() < needRMB:
		return
	
	with Tra_ElementSpirit_ChooseSkillType:
		role.DecUnbindRMB(needRMB)
		role.SetI8(EnumInt8.ElementSpiritSkillType, targetSkillType)
	
#	#同步更新元素之灵跟随状态
#	if role.GetI8(EnumInt8.ElementSpiritFollow):
#		role.SetI8(EnumInt8.ElementSpiritFollow, role.GetI8(EnumInt8.ElementSpiritSkillType))
	
	role.Msg(2, 0, prompt)

def OnCultivate(role, msg):
	'''
	元素之灵_培养元素之灵_请求
	@param msg: cultivateCnt 培养次数 限定单次 或者 50此
	'''
	if role.GetLevel() < EnumGameConfig.ElementSpiritNeedLevel:
		return
	
	#选择了技能类型才可以操作其他
	if not role.GetI8(EnumInt8.ElementSpiritSkillType):
		return
	
	#剩余可培养次数不足
	targetCultivateCnt = msg
	cultivatedCnt = role.GetI32(EnumInt32.ElementSpiritCultivateCnt)
	canCultivateCnt = role.GetI32(EnumInt32.ElementalEssenceAmount) - cultivatedCnt
	if targetCultivateCnt > canCultivateCnt:
		return
	
	#对应配置不存在 纠正一下先 下次再来就好了
	elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId), None)
	if not elementSpiritCfg or elementSpiritCfg.canBreak:
		return
	
	#最后一级的 达到即可 没有培养之说了
	if not elementSpiritCfg.nextId:
		return
	
	#计算此次实际培养次数
	needCultivateCnt = targetCultivateCnt
	#下一阶段是突破  采取保守培养 判断是否需要截断请求培养次数
	nextElementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(elementSpiritCfg.nextId)
	if not nextElementSpiritCfg:
		print "GE_EXC,ElementSpiritMgr::OnCultivate::config error, can not get cfg by nextId(%s) or cfg(%s)" % (role.GetI16(EnumInt16.ElementSpiritId),elementSpiritCfg.nextId) 
		return
	if nextElementSpiritCfg.canBreak:
		needCultivateCnt = min(targetCultivateCnt, elementSpiritCfg.elementCreamRange[1] - cultivatedCnt + 1)
	
	if needCultivateCnt < 1:
		return
	
	with Tra_ElementSpirit_Cultivate:
		#更新最终培养次数
		role.IncI32(EnumInt32.ElementSpiritCultivateCnt, needCultivateCnt)
		#若更新元素之灵ID 
		oldElementSpiritId = role.GetI16(EnumInt16.ElementSpiritId)
		newElementSpiritId = ElementSpiritConfig.GetElementSpiritIDByCultivateCnt(role.GetI32(EnumInt32.ElementSpiritCultivateCnt))
		if oldElementSpiritId != newElementSpiritId:
			role.SetI16(EnumInt16.ElementSpiritId, newElementSpiritId)
			AfterChangeElementSpiritId(role)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveElementSpiritCultivate, (needCultivateCnt))
	
	#培养成功提示
	nowElementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId), None)
	if nowElementSpiritCfg:
		role.Msg(2, 0, GlobalPrompt.ElementSpirit_Tips_CultivateSuccess % (nowElementSpiritCfg.gradeLevel, nowElementSpiritCfg.starLevel))

def OnBreak(role, msg = None):
	'''
	元素之灵_元素之灵突破_请求
	'''
	if role.GetLevel() < EnumGameConfig.ElementSpiritNeedLevel:
		return
	
	#选择了技能类型才可以操作其他
	if not role.GetI8(EnumInt8.ElementSpiritSkillType):
		return
	
	oldElementSpiritId = role.GetI16(EnumInt16.ElementSpiritId)
	elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(oldElementSpiritId)
	if not elementSpiritCfg:
		return
	
	if not (elementSpiritCfg.nextId and elementSpiritCfg.canBreak):
		return
	
	#消耗元素精华异常
	needCultivateCnt = elementSpiritCfg.elementCreamRange[1] - elementSpiritCfg.elementCreamRange[0] + 1
	if needCultivateCnt < 1:
		print "GE_EXC, ElementSpiritMgr::OnBreak::config error,needCultivateCnt < 1 in cfg(%s)" % oldElementSpiritId
		return
	
	#突破材料不足
	coding, cnt = elementSpiritCfg.breakNeedItem
	if role.ItemCnt(coding) < cnt:
		return
	
	with Tra_ElementSpirit_Break:
		#更新消耗元素精华总数
		role.IncI32(EnumInt32.ElementSpiritCultivateCnt, needCultivateCnt)
		#同步更新拥有元素精华总数 达到保持剩余元素精华总量不变的效果
		role.IncI32(EnumInt32.ElementalEssenceAmount, needCultivateCnt)
		#消耗道具
		role.DelItem(coding, cnt)
		#更新元素之灵ID
		role.SetI16(EnumInt16.ElementSpiritId, elementSpiritCfg.nextId)
		AfterChangeElementSpiritId(role)
		
	nowElementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId), None)
	if nowElementSpiritCfg:
		cRoleMgr.Msg(11, 0, GlobalPrompt.ElementSpirit_Msg_BreakSuccess % (role.GetRoleName(), nowElementSpiritCfg.gradeLevel))


def OnChangeFollow(role, msg):
	'''
	元素之灵_请求元素之灵改变跟随状态
	'''
	return 
	if role.GetLevel() < EnumGameConfig.ElementSpiritNeedLevel:
		return
	
	#选择了技能类型才可以操作其他
	if not role.GetI8(EnumInt8.ElementSpiritSkillType):
		return
	
	elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId))
	if not elementSpiritCfg or not elementSpiritCfg.canFollow:
		return 
	
	backId, followRequest = msg
	if followRequest:
		role.SetI8(EnumInt8.ElementSpiritFollow, role.GetI8(EnumInt8.ElementSpiritSkillType))
	else:
		role.SetI8(EnumInt8.ElementSpiritFollow, 0)
	
	role.CallBackFunction(backId, None)
	
	
#===============================================================================
# 辅助
#===============================================================================
def CorrectElementSpiritId(role):
	'''
	可能配置区段调整了 上线走一下纠正逻辑
	'''
	oldElementSpiritId = role.GetI8(EnumInt8.ElementSpiritSkillType)
	elementSpiritId = ElementSpiritConfig.GetElementSpiritIDByCultivateCnt(role.GetI32(EnumInt32.ElementSpiritCultivateCnt))
	if oldElementSpiritId != elementSpiritId:
		with Tra_ElementSpirit_SystemCorrect:
			role.SetI16(EnumInt16.ElementSpiritId, elementSpiritId)
			AfterChangeElementSpiritId(role)


def AfterChangeElementSpiritId(role):
	'''
	元素之灵ID变更
	'''
	#重算属性
	role.ResetElementSpiritProperty()

#===============================================================================
# 事件
#===============================================================================
def SyncRoleOtherData(role, param = None):
	'''
	角色上线同步处理
	根据基本数据 和 配置 重算衍生数据
	'''
	if role.GetLevel() < EnumGameConfig.ElementSpiritNeedLevel:
		return
	
	CorrectElementSpiritId(role)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		#通信协议
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementSpirit_OnChooseSpiritType", "元素之灵_请求选择元素之灵类型"), OnChooseSpiritType)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementSpirit_OnCultivate", "元素之灵_请求元素之灵培养"), OnCultivate)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementSpirit_OnBreak", "元素之灵_请求元素之灵突破"), OnBreak)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementSpirit_OnChangeFollow", "元素之灵_请求元素之灵改变跟随状态"), OnChangeFollow)
		
