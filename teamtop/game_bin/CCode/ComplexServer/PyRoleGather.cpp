/*角色聚合接口（自动生成） */
#include "PyRoleGather.h"
#include "Role.h"

ScriptHold::ScriptHold()
{

	
}

ScriptHold::~ScriptHold()
{

}

void ScriptHold::LoadPyData()
{
	this->m_pyIncExp.Load("Game.Role.Base.LevelEXP", "IncExp");
	this->m_pyGetExpCoef.Load("Game.Role.Base.LevelEXP", "GetExpCoef");
	this->m_pyGetAllHero.Load("Game.Hero.HeroFun", "GetAllHero");
	this->m_pyGetHero.Load("Game.Hero.HeroFun", "GetHero");
	this->m_pyIsLocalServer.Load("Game.Role.KuaFu", "IsLocalServer");
	this->m_pyGetPid.Load("Game.Role.KuaFu", "GetPid");
	this->m_pyGotoLocalServer.Load("Game.Role.KuaFu", "GotoLocalServer");
	this->m_pyGotoCrossServer.Load("Game.Role.KuaFu", "GotoCrossServer");
	this->m_pyRegPersistenceTick.Load("Game.Role.PersistenceTick", "RegPersistenceTick");
	this->m_pyGetTeam.Load("Game.Team.TeamBase", "GetTeam");
	this->m_pyHasTeam.Load("Game.Team.TeamBase", "HasTeam");
	this->m_pyClientCommand.Load("Game.ClientPanel.PanelBase", "ClientCommand");
	this->m_pyAddHero.Load("Game.Hero.HeroOperate", "AddHero");
	this->m_pyGetUnionObj.Load("Game.Union.UnionMgr", "GetUnionObj");
	this->m_pyAddWing.Load("Game.Wing.WingMgr", "AddWing");
	this->m_pyAddPet.Load("Game.Pet.PetMgr", "AddPet");
	this->m_pyAddTarotCard.Load("Game.Tarot.TarotOperate", "AddTarotCard");
	this->m_pyTarotPackageIsFull.Load("Game.Tarot.TarotOperate", "TarotPackageIsFull");
	this->m_pyGetTarotEmptySize.Load("Game.Tarot.TarotOperate", "GetTarotEmptySize");
	this->m_pyActiveWeddingRing.Load("Game.Marry.WeddingRing", "ActiveWeddingRing");
	this->m_pyAddTalentCard.Load("Game.TalentCard.TalentCardOperate", "AddTalentCard");
	this->m_pyAddMount.Load("Game.Mount.MountMgr", "AddMount");
	this->m_pyToLevel.Load("Game.Role.Base.LevelEXP", "ToLevel");
	this->m_pyGetOnLineTimeToday.Load("Game.Activity.OnLineReward.OnLineRewardMgr", "GetOnLineTimeToday");
	this->m_pyGetJTObj.Load("Game.JT.JTeam", "GetJTObj");
	this->m_pyGetJTeamScore.Load("Game.JT.JTeam", "GetJTeamScore");
	this->m_pyGetTotalGemLevel.Load("Game.Item.Gem", "GetTotalGemLevel");
	this->m_pyGetRoleZDL.Load("Game.ZDL.ZDL", "GetRoleZDL");
	this->m_pyGetHeroZDL.Load("Game.ZDL.ZDL", "GetHeroZDL");
	this->m_pyAddCardAtlas.Load("Game.CardAtlas.CardAtlasMgr", "AddCardAtlas");
	this->m_pyCardAtlasPackageIsFull.Load("Game.CardAtlas.CardAtlasMgr", "CardAtlasPackageIsFull");
	this->m_pyCardAtlasPackageEmptySize.Load("Game.CardAtlas.CardAtlasMgr", "CardAtlasPackageEmptySize");
	this->m_pyGetAnti.Load("Game.YYAnti.YYAnti", "GetAnti");
	this->m_pyAddItem.Load("Game.Item.FunGather", "AddItem");
	this->m_pyDecPropCnt.Load("Game.Item.FunGather", "DecPropCnt");
	this->m_pyDelItem.Load("Game.Item.FunGather", "DelItem");
	this->m_pyDelProp.Load("Game.Item.FunGather", "DelProp");
	this->m_pyFindGlobalProp.Load("Game.Item.FunGather", "FindGlobalProp");
	this->m_pyFindItem.Load("Game.Item.FunGather", "FindItem");
	this->m_pyFindPackProp.Load("Game.Item.FunGather", "FindPackProp");
	this->m_pyItemCnt.Load("Game.Item.FunGather", "ItemCnt");
	this->m_pyItemCnt_NotTimeOut.Load("Game.Item.FunGather", "ItemCnt_NotTimeOut");
	this->m_pyPackageEmptySize.Load("Game.Item.FunGather", "PackageEmptySize");
	this->m_pyPackageIsFull.Load("Game.Item.FunGather", "PackageIsFull");
	this->m_pyAddCuiLian.Load("Game.Role.Data.FunGather", "AddCuiLian");
	this->m_pyChangeSex.Load("Game.Role.Data.FunGather", "ChangeSex");
	this->m_pyDecBindRMB.Load("Game.Role.Data.FunGather", "DecBindRMB");
	this->m_pyDecContribution.Load("Game.Role.Data.FunGather", "DecContribution");
	this->m_pyDecDragonSoul.Load("Game.Role.Data.FunGather", "DecDragonSoul");
	this->m_pyDecGongXun.Load("Game.Role.Data.FunGather", "DecGongXun");
	this->m_pyDecKuaFuMoney.Load("Game.Role.Data.FunGather", "DecKuaFuMoney");
	this->m_pyDecMoney.Load("Game.Role.Data.FunGather", "DecMoney");
	this->m_pyDecRMB.Load("Game.Role.Data.FunGather", "DecRMB");
	this->m_pyDecReputation.Load("Game.Role.Data.FunGather", "DecReputation");
	this->m_pyDecRongYu.Load("Game.Role.Data.FunGather", "DecRongYu");
	this->m_pyDecStarLucky.Load("Game.Role.Data.FunGather", "DecStarLucky");
	this->m_pyDecUnbindRMB.Load("Game.Role.Data.FunGather", "DecUnbindRMB");
	this->m_pyDecUnbindRMB_Q.Load("Game.Role.Data.FunGather", "DecUnbindRMB_Q");
	this->m_pyDecUnbindRMB_S.Load("Game.Role.Data.FunGather", "DecUnbindRMB_S");
	this->m_pyGetArtifactCuiLianHoleLevel.Load("Game.Role.Data.FunGather", "GetArtifactCuiLianHoleLevel");
	this->m_pyGetArtifactMgr.Load("Game.Role.Data.FunGather", "GetArtifactMgr");
	this->m_pyGetBindRMB.Load("Game.Role.Data.FunGather", "GetBindRMB");
	this->m_pyGetCampID.Load("Game.Role.Data.FunGather", "GetCampID");
	this->m_pyGetColorCode.Load("Game.Role.Data.FunGather", "GetColorCode");
	this->m_pyGetConsumeQPoint.Load("Game.Role.Data.FunGather", "GetConsumeQPoint");
	this->m_pyGetContribution.Load("Game.Role.Data.FunGather", "GetContribution");
	this->m_pyGetCuiLian.Load("Game.Role.Data.FunGather", "GetCuiLian");
	this->m_pyGetCuiLian_MaxCnt.Load("Game.Role.Data.FunGather", "GetCuiLian_MaxCnt");
	this->m_pyGetDayBuyUnbindRMB_Q.Load("Game.Role.Data.FunGather", "GetDayBuyUnbindRMB_Q");
	this->m_pyGetDayConsumeUnbindRMB.Load("Game.Role.Data.FunGather", "GetDayConsumeUnbindRMB");
	this->m_pyGetDayWangZheJiFen.Load("Game.Role.Data.FunGather", "GetDayWangZheJiFen");
	this->m_pyGetDragonCareerID.Load("Game.Role.Data.FunGather", "GetDragonCareerID");
	this->m_pyGetDragonSoul.Load("Game.Role.Data.FunGather", "GetDragonSoul");
	this->m_pyGetEarningExpBuff.Load("Game.Role.Data.FunGather", "GetEarningExpBuff");
	this->m_pyGetEarningGoldBuff.Load("Game.Role.Data.FunGather", "GetEarningGoldBuff");
	this->m_pyGetElementBrandMgr.Load("Game.Role.Data.FunGather", "GetElementBrandMgr");
	this->m_pyGetElementSpiritSkill.Load("Game.Role.Data.FunGather", "GetElementSpiritSkill");
	this->m_pyGetEquipmentMgr.Load("Game.Role.Data.FunGather", "GetEquipmentMgr");
	this->m_pyGetExp.Load("Game.Role.Data.FunGather", "GetExp");
	this->m_pyGetFTVIP.Load("Game.Role.Data.FunGather", "GetFTVIP");
	this->m_pyGetFightType.Load("Game.Role.Data.FunGather", "GetFightType");
	this->m_pyGetGongXun.Load("Game.Role.Data.FunGather", "GetGongXun");
	this->m_pyGetGrade.Load("Game.Role.Data.FunGather", "GetGrade");
	this->m_pyGetHallowsMgr.Load("Game.Role.Data.FunGather", "GetHallowsMgr");
	this->m_pyGetHistoryContribution.Load("Game.Role.Data.FunGather", "GetHistoryContribution");
	this->m_pyGetJTProcessID.Load("Game.Role.Data.FunGather", "GetJTProcessID");
	this->m_pyGetJTeamID.Load("Game.Role.Data.FunGather", "GetJTeamID");
	this->m_pyGetJobID.Load("Game.Role.Data.FunGather", "GetJobID");
	this->m_pyGetKuaFuMoney.Load("Game.Role.Data.FunGather", "GetKuaFuMoney");
	this->m_pyGetLevel.Load("Game.Role.Data.FunGather", "GetLevel");
	this->m_pyGetMFZSkill.Load("Game.Role.Data.FunGather", "GetMFZSkill");
	this->m_pyGetMFZSkillPointDict.Load("Game.Role.Data.FunGather", "GetMFZSkillPointDict");
	this->m_pyGetMagicSpiritMgr.Load("Game.Role.Data.FunGather", "GetMagicSpiritMgr");
	this->m_pyGetMoFaZhen.Load("Game.Role.Data.FunGather", "GetMoFaZhen");
	this->m_pyGetMoney.Load("Game.Role.Data.FunGather", "GetMoney");
	this->m_pyGetPet.Load("Game.Role.Data.FunGather", "GetPet");
	this->m_pyGetPortrait.Load("Game.Role.Data.FunGather", "GetPortrait");
	this->m_pyGetRMB.Load("Game.Role.Data.FunGather", "GetRMB");
	this->m_pyGetReputation.Load("Game.Role.Data.FunGather", "GetReputation");
	this->m_pyGetRightMountID.Load("Game.Role.Data.FunGather", "GetRightMountID");
	this->m_pyGetRongYu.Load("Game.Role.Data.FunGather", "GetRongYu");
	this->m_pyGetSex.Load("Game.Role.Data.FunGather", "GetSex");
	this->m_pyGetStar.Load("Game.Role.Data.FunGather", "GetStar");
	this->m_pyGetStarLucky.Load("Game.Role.Data.FunGather", "GetStarLucky");
	this->m_pyGetStationID.Load("Game.Role.Data.FunGather", "GetStationID");
	this->m_pyGetStationSoulSkill.Load("Game.Role.Data.FunGather", "GetStationSoulSkill");
	this->m_pyGetTalentEmptySize.Load("Game.Role.Data.FunGather", "GetTalentEmptySize");
	this->m_pyGetTalentMgr.Load("Game.Role.Data.FunGather", "GetTalentMgr");
	this->m_pyGetTalentZDL.Load("Game.Role.Data.FunGather", "GetTalentZDL");
	this->m_pyGetUnbindRMB.Load("Game.Role.Data.FunGather", "GetUnbindRMB");
	this->m_pyGetUnbindRMB_Q.Load("Game.Role.Data.FunGather", "GetUnbindRMB_Q");
	this->m_pyGetUnbindRMB_S.Load("Game.Role.Data.FunGather", "GetUnbindRMB_S");
	this->m_pyGetUnionID.Load("Game.Role.Data.FunGather", "GetUnionID");
	this->m_pyGetVIP.Load("Game.Role.Data.FunGather", "GetVIP");
	this->m_pyGetWeek.Load("Game.Role.Data.FunGather", "GetWeek");
	this->m_pyGetWingID.Load("Game.Role.Data.FunGather", "GetWingID");
	this->m_pyGetXinYueLevel.Load("Game.Role.Data.FunGather", "GetXinYueLevel");
	this->m_pyGetZDL.Load("Game.Role.Data.FunGather", "GetZDL");
	this->m_pyGetZhuanShengHaloAddi.Load("Game.Role.Data.FunGather", "GetZhuanShengHaloAddi");
	this->m_pyGetZhuanShengHaloLevel.Load("Game.Role.Data.FunGather", "GetZhuanShengHaloLevel");
	this->m_pyGetZhuanShengLevel.Load("Game.Role.Data.FunGather", "GetZhuanShengLevel");
	this->m_pyIncBindRMB.Load("Game.Role.Data.FunGather", "IncBindRMB");
	this->m_pyIncConsumeQPoint.Load("Game.Role.Data.FunGather", "IncConsumeQPoint");
	this->m_pyIncContribution.Load("Game.Role.Data.FunGather", "IncContribution");
	this->m_pyIncDragonSoul.Load("Game.Role.Data.FunGather", "IncDragonSoul");
	this->m_pyIncGongXun.Load("Game.Role.Data.FunGather", "IncGongXun");
	this->m_pyIncHistoryContribution.Load("Game.Role.Data.FunGather", "IncHistoryContribution");
	this->m_pyIncKuaFuMoney.Load("Game.Role.Data.FunGather", "IncKuaFuMoney");
	this->m_pyIncLevel.Load("Game.Role.Data.FunGather", "IncLevel");
	this->m_pyIncMoney.Load("Game.Role.Data.FunGather", "IncMoney");
	this->m_pyIncReputation.Load("Game.Role.Data.FunGather", "IncReputation");
	this->m_pyIncRongYu.Load("Game.Role.Data.FunGather", "IncRongYu");
	this->m_pyIncStarLucky.Load("Game.Role.Data.FunGather", "IncStarLucky");
	this->m_pyIncTarotHP.Load("Game.Role.Data.FunGather", "IncTarotHP");
	this->m_pyIncTouchGoldPoint.Load("Game.Role.Data.FunGather", "IncTouchGoldPoint");
	this->m_pyIncUnbindRMB_Q.Load("Game.Role.Data.FunGather", "IncUnbindRMB_Q");
	this->m_pyIncUnbindRMB_S.Load("Game.Role.Data.FunGather", "IncUnbindRMB_S");
	this->m_pyIsKongJianDecennialRole.Load("Game.Role.Data.FunGather", "IsKongJianDecennialRole");
	this->m_pyIsMonthCard.Load("Game.Role.Data.FunGather", "IsMonthCard");
	this->m_pySetBindRMB.Load("Game.Role.Data.FunGather", "SetBindRMB");
	this->m_pySetCampID.Load("Game.Role.Data.FunGather", "SetCampID");
	this->m_pySetCanChatTime.Load("Game.Role.Data.FunGather", "SetCanChatTime");
	this->m_pySetCanLoginTime.Load("Game.Role.Data.FunGather", "SetCanLoginTime");
	this->m_pySetConsumeQPoint.Load("Game.Role.Data.FunGather", "SetConsumeQPoint");
	this->m_pySetContribution.Load("Game.Role.Data.FunGather", "SetContribution");
	this->m_pySetDragonCareerID.Load("Game.Role.Data.FunGather", "SetDragonCareerID");
	this->m_pySetDragonSoul.Load("Game.Role.Data.FunGather", "SetDragonSoul");
	this->m_pySetEarningExpBuff.Load("Game.Role.Data.FunGather", "SetEarningExpBuff");
	this->m_pySetEarningGoldBuff.Load("Game.Role.Data.FunGather", "SetEarningGoldBuff");
	this->m_pySetExp.Load("Game.Role.Data.FunGather", "SetExp");
	this->m_pySetFightType.Load("Game.Role.Data.FunGather", "SetFightType");
	this->m_pySetGongXun.Load("Game.Role.Data.FunGather", "SetGongXun");
	this->m_pySetGrade.Load("Game.Role.Data.FunGather", "SetGrade");
	this->m_pySetHistoryContribution.Load("Game.Role.Data.FunGather", "SetHistoryContribution");
	this->m_pySetJTeamID.Load("Game.Role.Data.FunGather", "SetJTeamID");
	this->m_pySetJobID.Load("Game.Role.Data.FunGather", "SetJobID");
	this->m_pySetKuaFuMoney.Load("Game.Role.Data.FunGather", "SetKuaFuMoney");
	this->m_pySetMoney.Load("Game.Role.Data.FunGather", "SetMoney");
	this->m_pySetReputation.Load("Game.Role.Data.FunGather", "SetReputation");
	this->m_pySetRightMountID.Load("Game.Role.Data.FunGather", "SetRightMountID");
	this->m_pySetRongYu.Load("Game.Role.Data.FunGather", "SetRongYu");
	this->m_pySetStarLucky.Load("Game.Role.Data.FunGather", "SetStarLucky");
	this->m_pySetStationID.Load("Game.Role.Data.FunGather", "SetStationID");
	this->m_pySetUnbindRMB_Q.Load("Game.Role.Data.FunGather", "SetUnbindRMB_Q");
	this->m_pySetUnbindRMB_S.Load("Game.Role.Data.FunGather", "SetUnbindRMB_S");
	this->m_pySetUnionID.Load("Game.Role.Data.FunGather", "SetUnionID");
	this->m_pySetVIP.Load("Game.Role.Data.FunGather", "SetVIP");
	this->m_pySetWeek.Load("Game.Role.Data.FunGather", "SetWeek");
	this->m_pySetWingID.Load("Game.Role.Data.FunGather", "SetWingID");
	this->m_pySetZDL.Load("Game.Role.Data.FunGather", "SetZDL");
	this->m_pySetZhuanShengHaloLevel.Load("Game.Role.Data.FunGather", "SetZhuanShengHaloLevel");
	this->m_pySetZhuanShengLevel.Load("Game.Role.Data.FunGather", "SetZhuanShengLevel");
	this->m_pyUpdateAndSyncMFZSkillPassive.Load("Game.Role.Data.FunGather", "UpdateAndSyncMFZSkillPassive");
	this->m_pyCreateHeroProperty.Load("Game.Property.PropertyFun", "CreateHeroProperty");
	this->m_pyGetPropertyGather.Load("Game.Property.PropertyFun", "GetPropertyGather");
	this->m_pyGetPropertyMgr.Load("Game.Property.PropertyFun", "GetPropertyMgr");
	this->m_pyPropertyIsValid.Load("Game.Property.PropertyFun", "PropertyIsValid");
	this->m_pyRemoveHeroProperty.Load("Game.Property.PropertyFun", "RemoveHeroProperty");
	this->m_pyResetAllTarotProperty.Load("Game.Property.PropertyFun", "ResetAllTarotProperty");
	this->m_pyResetElementBrandBaseProperty.Load("Game.Property.PropertyFun", "ResetElementBrandBaseProperty");
	this->m_pyResetElementSpiritProperty.Load("Game.Property.PropertyFun", "ResetElementSpiritProperty");
	this->m_pyResetGlobalCardAtlasProperty.Load("Game.Property.PropertyFun", "ResetGlobalCardAtlasProperty");
	this->m_pyResetGlobalDragonProperty.Load("Game.Property.PropertyFun", "ResetGlobalDragonProperty");
	this->m_pyResetGlobalFashionProperty.Load("Game.Property.PropertyFun", "ResetGlobalFashionProperty");
	this->m_pyResetGlobalHelpStationProperty.Load("Game.Property.PropertyFun", "ResetGlobalHelpStationProperty");
	this->m_pyResetGlobalMountAppProperty.Load("Game.Property.PropertyFun", "ResetGlobalMountAppProperty");
	this->m_pyResetGlobalMountProperty.Load("Game.Property.PropertyFun", "ResetGlobalMountProperty");
	this->m_pyResetGlobalQinmiGradeProperty.Load("Game.Property.PropertyFun", "ResetGlobalQinmiGradeProperty");
	this->m_pyResetGlobalQinmiProperty.Load("Game.Property.PropertyFun", "ResetGlobalQinmiProperty");
	this->m_pyResetGlobalStationSoulItemProperty.Load("Game.Property.PropertyFun", "ResetGlobalStationSoulItemProperty");
	this->m_pyResetGlobalWStationBaseProperty.Load("Game.Property.PropertyFun", "ResetGlobalWStationBaseProperty");
	this->m_pyResetGlobalWStationItemProperty.Load("Game.Property.PropertyFun", "ResetGlobalWStationItemProperty");
	this->m_pyResetGlobalWStationThousandProperty.Load("Game.Property.PropertyFun", "ResetGlobalWStationThousandProperty");
	this->m_pyResetGlobalWeddingRingProperty.Load("Game.Property.PropertyFun", "ResetGlobalWeddingRingProperty");
	this->m_pyResetGlobalWeddingRingSProperty.Load("Game.Property.PropertyFun", "ResetGlobalWeddingRingSProperty");
	this->m_pyResetGlobalWeddingRingSkillProperty.Load("Game.Property.PropertyFun", "ResetGlobalWeddingRingSkillProperty");
	this->m_pyResetGlobalWingProperty.Load("Game.Property.PropertyFun", "ResetGlobalWingProperty");
	this->m_pyResetGlobalZhuanShengHaloBaseProperty.Load("Game.Property.PropertyFun", "ResetGlobalZhuanShengHaloBaseProperty");
	this->m_pyResetMarryRingProperty.Load("Game.Property.PropertyFun", "ResetMarryRingProperty");
	this->m_pyResetSealProperty.Load("Game.Property.PropertyFun", "ResetSealProperty");
	this->m_pyResetStationSoulProperty.Load("Game.Property.PropertyFun", "ResetStationSoulProperty");
	this->m_pyResetTitleProperty.Load("Game.Property.PropertyFun", "ResetTitleProperty");
	this->m_pySyncAllProperty.Load("Game.Property.PropertyFun", "SyncAllProperty");
};

namespace ServerPython
{
	PyObject* IncExp( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetExpCoef( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetExpCoef.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetAllHero( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetAllHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetHero( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IsLocalServer( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIsLocalServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetPid( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPid.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GotoLocalServer( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGotoLocalServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GotoCrossServer( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGotoCrossServer.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* RegPersistenceTick( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyRegPersistenceTick.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetTeam( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTeam.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* HasTeam( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyHasTeam.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ClientCommand( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyClientCommand.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddHero( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddHero.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetUnionObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnionObj.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddWing( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddWing.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddPet( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddPet.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddTarotCard( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddTarotCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* TarotPackageIsFull( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyTarotPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetTarotEmptySize( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTarotEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ActiveWeddingRing( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyActiveWeddingRing.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddTalentCard( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddTalentCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddMount( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddMount.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ToLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyToLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetOnLineTimeToday( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetOnLineTimeToday.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetJTObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTObj.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetJTeamScore( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTeamScore.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetTotalGemLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTotalGemLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetRoleZDL( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRoleZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetHeroZDL( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHeroZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddCardAtlas( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddCardAtlas.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* CardAtlasPackageIsFull( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyCardAtlasPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* CardAtlasPackageEmptySize( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyCardAtlasPackageEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetAnti( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetAnti.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddItem( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecPropCnt( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecPropCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DelItem( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDelItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DelProp( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDelProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* FindGlobalProp( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyFindGlobalProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* FindItem( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyFindItem.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* FindPackProp( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyFindPackProp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ItemCnt( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyItemCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ItemCnt_NotTimeOut( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyItemCnt_NotTimeOut.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* PackageEmptySize( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyPackageEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* PackageIsFull( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyPackageIsFull.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* AddCuiLian( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyAddCuiLian.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ChangeSex( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyChangeSex.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecBindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecDragonSoul( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecGongXun( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecKuaFuMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecReputation( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecRongYu( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecStarLucky( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecUnbindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecUnbindRMB_Q( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* DecUnbindRMB_S( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyDecUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetArtifactCuiLianHoleLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetArtifactCuiLianHoleLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetArtifactMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetArtifactMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetBindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetCampID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCampID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetColorCode( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetColorCode.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetConsumeQPoint( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetCuiLian( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCuiLian.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetCuiLian_MaxCnt( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetCuiLian_MaxCnt.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetDayBuyUnbindRMB_Q( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayBuyUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetDayConsumeUnbindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayConsumeUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetDayWangZheJiFen( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDayWangZheJiFen.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetDragonCareerID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDragonCareerID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetDragonSoul( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetEarningExpBuff( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEarningExpBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetEarningGoldBuff( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEarningGoldBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetElementBrandMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetElementBrandMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetElementSpiritSkill( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetElementSpiritSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetEquipmentMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetEquipmentMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetExp( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetFTVIP( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetFTVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetFightType( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetFightType.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetGongXun( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetGrade( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetGrade.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetHallowsMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHallowsMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetHistoryContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetJTProcessID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTProcessID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetJTeamID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJTeamID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetJobID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetJobID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetKuaFuMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetMFZSkill( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMFZSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetMFZSkillPointDict( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMFZSkillPointDict.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetMagicSpiritMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMagicSpiritMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetMoFaZhen( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMoFaZhen.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetPet( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPet.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetPortrait( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPortrait.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetReputation( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetRightMountID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRightMountID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetRongYu( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetSex( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetSex.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetStar( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStar.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetStarLucky( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetStationID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStationID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetStationSoulSkill( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetStationSoulSkill.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetTalentEmptySize( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentEmptySize.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetTalentMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetTalentZDL( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetTalentZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetUnbindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetUnbindRMB_Q( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetUnbindRMB_S( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetUnionID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetUnionID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetVIP( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetWeek( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetWeek.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetWingID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetWingID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetXinYueLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetXinYueLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetZDL( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetZhuanShengHaloAddi( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengHaloAddi.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetZhuanShengHaloLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengHaloLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetZhuanShengLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetZhuanShengLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncBindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncConsumeQPoint( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncDragonSoul( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncGongXun( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncHistoryContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncKuaFuMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncReputation( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncRongYu( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncStarLucky( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncTarotHP( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncTarotHP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncTouchGoldPoint( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncTouchGoldPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncUnbindRMB_Q( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IncUnbindRMB_S( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIncUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IsKongJianDecennialRole( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIsKongJianDecennialRole.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* IsMonthCard( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyIsMonthCard.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetBindRMB( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetBindRMB.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetCampID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetCampID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetCanChatTime( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetCanChatTime.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetCanLoginTime( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetCanLoginTime.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetConsumeQPoint( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetConsumeQPoint.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetDragonCareerID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetDragonCareerID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetDragonSoul( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetDragonSoul.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetEarningExpBuff( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetEarningExpBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetEarningGoldBuff( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetEarningGoldBuff.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetExp( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetExp.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetFightType( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetFightType.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetGongXun( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetGongXun.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetGrade( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetGrade.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetHistoryContribution( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetHistoryContribution.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetJTeamID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetJTeamID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetJobID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetJobID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetKuaFuMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetKuaFuMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetMoney( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetMoney.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetReputation( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetReputation.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetRightMountID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetRightMountID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetRongYu( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetRongYu.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetStarLucky( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetStarLucky.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetStationID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetStationID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetUnbindRMB_Q( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnbindRMB_Q.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetUnbindRMB_S( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnbindRMB_S.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetUnionID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetUnionID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetVIP( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetVIP.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetWeek( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetWeek.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetWingID( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetWingID.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetZDL( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetZDL.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetZhuanShengHaloLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetZhuanShengHaloLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SetZhuanShengLevel( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pySetZhuanShengLevel.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* UpdateAndSyncMFZSkillPassive( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyUpdateAndSyncMFZSkillPassive.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* CreateHeroProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyCreateHeroProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetPropertyGather( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPropertyGather.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* GetPropertyMgr( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyGetPropertyMgr.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* PropertyIsValid( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyPropertyIsValid.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* RemoveHeroProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		if (!PyTuple_CheckExact(arg))
		{
			PY_PARAM_ERROR("param must be tuple.");
		}
		GE::Uint16 uSize = static_cast<GE::Uint16>(PyTuple_GET_SIZE(arg));
		GEPython::Tuple tup(uSize + 1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		GE_ITER_UI16(idx, uSize)
		{
			tup.AppendObj_BorrowRef(PyTuple_GET_ITEM(arg, idx));
		}
		return PyObject_CallObject(ScriptHold::Instance()->m_pyRemoveHeroProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetAllTarotProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetAllTarotProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetElementBrandBaseProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetElementBrandBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetElementSpiritProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetElementSpiritProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalCardAtlasProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalCardAtlasProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalDragonProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalDragonProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalFashionProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalFashionProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalHelpStationProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalHelpStationProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalMountAppProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalMountAppProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalMountProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalMountProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalQinmiGradeProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalQinmiGradeProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalQinmiProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalQinmiProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalStationSoulItemProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalStationSoulItemProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWStationBaseProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWStationItemProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationItemProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWStationThousandProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWStationThousandProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWeddingRingProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWeddingRingSProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingSProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWeddingRingSkillProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWeddingRingSkillProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalWingProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalWingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetGlobalZhuanShengHaloBaseProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetGlobalZhuanShengHaloBaseProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetMarryRingProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetMarryRingProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetSealProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetSealProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetStationSoulProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetStationSoulProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* ResetTitleProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pyResetTitleProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

	PyObject* SyncAllProperty( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_pySyncAllProperty.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

};


