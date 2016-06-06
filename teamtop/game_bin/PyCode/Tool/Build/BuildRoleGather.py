#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Tool.Build.BuildRoleGather")
#===============================================================================
# 自动构建角色绑定函数
#===============================================================================
import types
import inspect
import DynamicPath
from Game.ClientPanel import PanelBase
from Game.Hero import HeroFun, HeroOperate
from Game.Item import FunGather as ItemFun
from Game.Pet import PetMgr
from Game.Role import KuaFu, PersistenceTick
from Game.Role.Base import LevelEXP
from Game.Role.Data import FunGather as DataFun
from Game.Tarot import TarotOperate
from Game.Team import TeamBase
from Game.Union import UnionMgr
from Game.Wing import WingMgr
from Game.Property import PropertyFun as PFun
from Game.Marry import WeddingRing
from Game.TalentCard import TalentCardOperate
from Game.Mount import MountMgr
from Game.Activity.OnLineReward import OnLineRewardMgr
from Game.JT import JTeam
from Game.Item import Gem
from Game.ZDL import ZDL
from Game.CardAtlas import CardAtlasMgr
from Game.YYAnti import YYAnti


# 要绑定到role上面的函数
GatherFun = [
	LevelEXP.IncExp,
	LevelEXP.GetExpCoef,
	HeroFun.GetAllHero,
	HeroFun.GetHero,
	KuaFu.IsLocalServer,
	KuaFu.GetPid,
	KuaFu.GotoLocalServer,
	KuaFu.GotoCrossServer,
	PersistenceTick.RegPersistenceTick,
	TeamBase.GetTeam,
	TeamBase.HasTeam,
	PanelBase.ClientCommand,
	HeroOperate.AddHero,
	UnionMgr.GetUnionObj,
	WingMgr.AddWing,
	PetMgr.AddPet,
	TarotOperate.AddTarotCard,
	TarotOperate.TarotPackageIsFull,
	TarotOperate.GetTarotEmptySize,
	WeddingRing.ActiveWeddingRing,
	TalentCardOperate.AddTalentCard,
	MountMgr.AddMount,
	LevelEXP.ToLevel,
	OnLineRewardMgr.GetOnLineTimeToday,
	JTeam.GetJTObj,
	JTeam.GetJTeamScore,
	Gem.GetTotalGemLevel,
	ZDL.GetRoleZDL,
	ZDL.GetHeroZDL,
	CardAtlasMgr.AddCardAtlas,
	CardAtlasMgr.CardAtlasPackageIsFull,
	CardAtlasMgr.CardAtlasPackageEmptySize,
	YYAnti.GetAnti
	]
# 要绑定到role上面的模块函数
GatherModule = [ItemFun, DataFun, PFun]

H1 = '''/************************************************************************
角色聚合接口（自动生成）
************************************************************************/
#pragma once
#include "../GameEngine/GameEngine.h"
#include "PyRole.h"

class ScriptHold
	: public GEControlSingleton<ScriptHold>
{
public:
	ScriptHold();
	~ScriptHold();

public:
	void							LoadPyData();

public:
'''

H2 = '''#define RoleGather_Methods \\
'''

BEGIN = '''namespace ServerPython
{
'''

END = '''};

'''
EMPTY = '''
'''


CPP1 = '''/*角色聚合接口（自动生成） */
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
'''

HOLD_FUN = '''	GEPython::Function				m_py%(fun)s;
'''
REG = '''	{"%(fun)s", (PyCFunction)%(fun)s, %(argv)s, "%(doc)s "}, \\
'''
DECLARE = '''	PyObject*  %(fun)s(PyRoleObject* self, PyObject* arg);
'''
LOAD = '''	this->m_py%(fun)s.Load("%(module)s", "%(fun)s");
'''
CODE_VARARGS = '''	PyObject* %(fun)s( PyRoleObject* self, PyObject* arg )
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
		return PyObject_CallObject(ScriptHold::Instance()->m_py%(fun)s.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

'''

CODE_NOARGS = '''	PyObject* %(fun)s( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GEPython::Tuple tup(1);
		tup.AppendObj_BorrowRef(self->cptr->GetPySelf().GetObj_BorrowRef());
		return PyObject_CallObject(ScriptHold::Instance()->m_py%(fun)s.GetFun_BorrowRef(), tup.GetTuple_BorrowRef());
	}

'''

def BuildGather():
	u = set()
	l = []
	for FUN in GatherFun:
		argv = inspect.getargspec(FUN)[0]
		if argv[0] != "role":
			print "GE_EXC, module(%s) fun(%s) first argv(%s) is not role." % (FUN.__module__, FUN.__name__, argv[0])
		if FUN.__name__ in u:
			print "GE_EXC, repeat fun(%s)." % FUN.__name__
		u.add(FUN.__name__)
		l.append({"module":FUN.__module__, "fun" : FUN.__name__, "doc":FUN.__doc__, "argv":"METH_VARARGS" if len(argv) > 1 else "METH_NOARGS"})
	for MODULE in GatherModule:
		for name in dir(MODULE):
			FUN = getattr(MODULE, name)
			if type(FUN) != types.FunctionType:
				continue
			argv = inspect.getargspec(FUN)[0]
			if argv[0] != "role":
				print "GE_EXC, module(%s) fun(%s) first argv(%s) is not role." % (FUN.__module__, FUN.__name__, argv[0])
			if FUN.__name__ in u:
				print "GE_EXC, repeat fun(%s)." % FUN.__name__
			u.add(FUN.__name__)
			l.append({"module":FUN.__module__, "fun" : FUN.__name__, "doc":FUN.__doc__, "argv":"METH_VARARGS" if len(argv) > 1 else "METH_NOARGS"})
	with open(DynamicPath.CFloderPath + "ComplexServer\PyRoleGather.h", "w") as f:
		f.write(H1)
		for d in l:
			f.write(HOLD_FUN % d)
		f.write(END)
		f.write(H2)
		for d in l:
			f.write(REG % d)
		f.write(EMPTY)
		f.write(EMPTY)
		f.write(BEGIN)
		for d in l:
			f.write(DECLARE % d)
		f.write(END)
	
	with open(DynamicPath.CFloderPath + "ComplexServer\PyRoleGather.cpp", "w") as f:
		f.write(CPP1)
		for d in l:
			f.write(LOAD % d)
		f.write(END)
		f.write(BEGIN)
		for d in l:
			if d["argv"] == "METH_VARARGS":
				f.write(CODE_VARARGS % d)
			else:
				f.write(CODE_NOARGS % d)
		f.write(END)
		f.write("\n")

if __name__ == "__main__":
	BuildGather()
	print "BuildGather, OK"
	
	#顺便吧帮助文件也生成一下吧
	from Tool.Build import BuildPyHelpCode
	BuildPyHelpCode.CPYBuild()
	print "BuildPyHelpCode ok"


