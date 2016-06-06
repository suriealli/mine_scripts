/*我是UTF8无签名编码 */
#include "PyRoleContain.h"
#include "Role.h"
#include "PyRoleGather.h"

namespace ServerPython
{

	PyObject* SetCareer(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Int32 nValue = 0;
		if (!GEPython::PyObjToI32(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Int32.");
		}
		self->cptr->SetCareer(nValue);
		Py_RETURN_NONE;
	}

	PyObject* GetCareer(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetCareer());
	}

	PyObject* SetFly(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint8 uValue;
		if (!GEPython::PyObjToUI8(arg, uValue))
		{
			PyErr_SetString(PyExc_RuntimeError, "param must be GE::Uint8.");
			return NULL;
		}
		self->cptr->SetFly(uValue);
		Py_RETURN_NONE;
	}

	PyObject* IsFlying(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PY_RETURN_BOOL(self->cptr->IsFlying());
	}

	PyObject* IncTiLi(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->IncTiLi(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* DecTiLi(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->DecTiLi(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* SetTiLi(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->SetTiLi(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* GetTiLi(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetTiLi());
	}

	PyObject* GetNowSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetNowSpeed());
	}

	
	PyObject* SetMoveSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->SetMoveSpeed(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* GetMoveSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetMoveSpeed());
	}

	PyObject* SetMountSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->SetMountSpeed(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* GetMountSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetMountSpeed());
	}



	PyObject* SetTempSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->SetTempSpeed(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* GetTempSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetTempSpeed());
	}

	PyObject* CancleTempSpeed(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SetTempSpeed(0);
		Py_RETURN_NONE;
	}

	PyObject* GetTempFly(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI32(self->cptr->GetTempFly());
	}

	PyObject* SetTempFly(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 nValue = 0;
		if (!GEPython::PyObjToUI16(arg, nValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->SetTempFly(static_cast<GE::Int16>(nValue));
		Py_RETURN_NONE;
	}


	PyObject* CancleTempFly(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->SetTempFly(0);
		Py_RETURN_NONE;
	}
	


	PyObject* SetAppStatus(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uValue = 0;
		if (!GEPython::PyObjToUI16(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}

		self->cptr->SetAppStatus(uValue);
		Py_RETURN_NONE;
	}

	PyObject* GetAppStatus(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return GEPython::PyObjFromI64(self->cptr->GetTI64(RoleDataMgr::Instance()->uRoleAppStatusIndex));
	}

	PyObject* MustFlying(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		PY_RETURN_BOOL(self->cptr->IsFlyingPos());
	}

	PyObject* GetRoleSyncAppearanceObj(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->GetRoleSyncAppearanceObj();
	}

	PyObject* SetQQHZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uValue = 0;
		if (!GEPython::PyObjToUI16(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		GE::B4 tempHZ = self->cptr->GetDI32(RoleDataMgr::Instance()->uHuangZuanIndex);
		if (tempHZ.UI16_0() == uValue)
		{
			//低位是黄钻等级
			Py_RETURN_NONE;
		}
		//必须这样做才能触发同步客户端
		tempHZ.UI16_0() = uValue;
		self->cptr->SetDI32(RoleDataMgr::Instance()->uHuangZuanIndex, tempHZ.I32());
		Py_RETURN_NONE;
	}

	PyObject* GetQQHZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::B4& tempHZ = GE_AS_B4(self->cptr->GetDI32Ref(RoleDataMgr::Instance()->uHuangZuanIndex));
		return GEPython::PyObjFromI32(tempHZ.I16_0());
	}

	PyObject* SetQQYHZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint8 uValue = 0;
		if (!GEPython::PyObjToUI8(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint8.");
		}
		GE::B4 tempHZ = self->cptr->GetDI32(RoleDataMgr::Instance()->uHuangZuanIndex);
		if (tempHZ.UI8_2() == uValue)
		{
			//高16位中的低8位是年费
			Py_RETURN_NONE;
		}
		//必须这样做才能触发同步客户端
		tempHZ.UI8_2() = uValue;
		self->cptr->SetDI32(RoleDataMgr::Instance()->uHuangZuanIndex, tempHZ.I32());
		Py_RETURN_NONE;
	}

	PyObject* GetQQYHZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::B4& tempHZ = GE_AS_B4(self->cptr->GetDI32Ref(RoleDataMgr::Instance()->uHuangZuanIndex));
		return GEPython::PyObjFromI32(tempHZ.UI8_2());
	}


	PyObject* SetQQHHHZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint8 uValue = 0;
		if (!GEPython::PyObjToUI8(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint8.");
		}
		GE::B4 tempHZ = self->cptr->GetDI32(RoleDataMgr::Instance()->uHuangZuanIndex);
		if (tempHZ.UI8_3() == uValue)
		{
			//高16位中的高8位是年费
			Py_RETURN_NONE;
		}
		//必须这样做才能触发同步客户端
		tempHZ.UI8_3() = uValue;
		self->cptr->SetDI32(RoleDataMgr::Instance()->uHuangZuanIndex, tempHZ.I32());
		Py_RETURN_NONE;
	}

	PyObject* GetQQHHHZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::B4& tempHZ = GE_AS_B4(self->cptr->GetDI32Ref(RoleDataMgr::Instance()->uHuangZuanIndex));
		return GEPython::PyObjFromI32(tempHZ.UI8_3());
	}


	PyObject* SetQQLZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uValue = 0;
		if (!GEPython::PyObjToUI16(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		GE::B4 tempHZ = self->cptr->GetDI32(RoleDataMgr::Instance()->uLanZuanIndex);
		if (tempHZ.UI16_0() == uValue)
		{
			//低位是黄钻等级
			Py_RETURN_NONE;
		}
		//必须这样做才能触发同步客户端
		tempHZ.UI16_0() = uValue;
		self->cptr->SetDI32(RoleDataMgr::Instance()->uLanZuanIndex, tempHZ.I32());
		Py_RETURN_NONE;
	}

	PyObject* GetQQLZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::B4& tempHZ = GE_AS_B4(self->cptr->GetDI32Ref(RoleDataMgr::Instance()->uLanZuanIndex));
		return GEPython::PyObjFromI32(tempHZ.I16_0());
	}

	PyObject* SetQQYLZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint8 uValue = 0;
		if (!GEPython::PyObjToUI8(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint8.");
		}
		GE::B4 tempHZ = self->cptr->GetDI32(RoleDataMgr::Instance()->uLanZuanIndex);
		if (tempHZ.UI8_2() == uValue)
		{
			//高16位中的低8位是年费
			Py_RETURN_NONE;
		}
		//必须这样做才能触发同步客户端
		tempHZ.UI8_2() = uValue;
		self->cptr->SetDI32(RoleDataMgr::Instance()->uLanZuanIndex, tempHZ.I32());
		Py_RETURN_NONE;
	}

	PyObject* GetQQYLZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::B4& tempHZ = GE_AS_B4(self->cptr->GetDI32Ref(RoleDataMgr::Instance()->uLanZuanIndex));
		return GEPython::PyObjFromI32(tempHZ.UI8_2());
	}


	PyObject* SetQQHHLZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint8 uValue = 0;
		if (!GEPython::PyObjToUI8(arg, uValue))
		{
			PY_PARAM_ERROR("param must be GE::Uint8.");
		}
		GE::B4 tempHZ = self->cptr->GetDI32(RoleDataMgr::Instance()->uLanZuanIndex);
		if (tempHZ.UI8_3() == uValue)
		{
			//高16位中的高8位是年费
			Py_RETURN_NONE;
		}
		//必须这样做才能触发同步客户端
		tempHZ.UI8_3() = uValue;
		self->cptr->SetDI32(RoleDataMgr::Instance()->uLanZuanIndex, tempHZ.I32());
		Py_RETURN_NONE;
	}

	PyObject* GetQQHHLZ(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::B4& tempHZ = GE_AS_B4(self->cptr->GetDI32Ref(RoleDataMgr::Instance()->uLanZuanIndex));
		return GEPython::PyObjFromI32(tempHZ.UI8_3());
	}


}

