/*我是UTF8无签名编码 */
#include "PyRoleArray.h"
#include "Role.h"

namespace ServerPython
{
	PyObject* InitI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitI64(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriI64_NewRef();
	}

	PyObject* GetI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16");
		}
		if (uIdx >= self->cptr->GetInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI64(self->cptr->GetI64(uIdx));
	}

	PyObject* SetI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* IncI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* DecI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecI64(uIdx, nValue);
		Py_RETURN_NONE;
	}


	PyObject* InitDI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitDI32(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriDI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriDI32_NewRef();
	}

	PyObject* GetDI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetDisperseInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetDI32(uIdx));
	}

	PyObject* SetDI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDisperseInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetDI32(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* IncDI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDisperseInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncDI32(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* DecDI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDisperseInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecDI32(uIdx, nValue);
		Py_RETURN_NONE;
	}


	PyObject* InitI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitI32(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriI32_NewRef();
	}

	PyObject* GetI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetI32(uIdx));
	}

	PyObject* SetI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetI32(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* IncI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncI32(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* DecI32(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt32Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecI32(uIdx, nValue);
		Py_RETURN_NONE;
	}


	PyObject* InitI16(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitI16(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriI16(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriI16_NewRef();
	}

	PyObject* GetI16(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetInt16Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetI16(uIdx));
	}

	PyObject* SetI16(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt16Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetI16(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* IncI16(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt16Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncI16(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* DecI16(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt16Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecI16(uIdx, nValue);
		Py_RETURN_NONE;
	}


	PyObject* InitI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitI8(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriI8_NewRef();
	}

	PyObject* GetI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetI8(uIdx));
	}

	PyObject* SetI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* IncI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* DecI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* InitDI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitDI8(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriDI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriDI8_NewRef();
	}

	PyObject* GetDI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetDayInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetDI8(uIdx));
	}

	PyObject* SetDI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDayInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetDI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* IncDI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDayInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncDI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* DecDI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDayInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecDI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}


	PyObject* InitI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitI1(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriI1_NewRef();
	}

	PyObject* GetI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetInt1Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		PY_RETURN_BOOL(self->cptr->GetI1(uIdx));
	}

	PyObject* SetI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		PyObject* pValue = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetInt1Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (PyObject_IsTrue(pValue))
		{
			self->cptr->SetI1(uIdx, true);
		}
		else
		{
			self->cptr->SetI1(uIdx, false);
		}
		Py_RETURN_NONE;
	}

	PyObject* InitDI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitDI1(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriDI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriDI1_NewRef();
	}

	PyObject* GetDI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetDayInt1Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		PY_RETURN_BOOL(self->cptr->GetDI1(uIdx));
	}

	PyObject* SetDI1(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		PyObject* pValue = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetDayInt1Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (PyObject_IsTrue(pValue))
		{
			self->cptr->SetDI1(uIdx, true);
		}
		else
		{
			self->cptr->SetDI1(uIdx, false);
		}
		Py_RETURN_NONE;
	}

	PyObject* InitDI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitDI64(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriDI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriDI64_NewRef();
	}

	PyObject* GetDI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= RoleDataMgr::Instance()->GetDynamicInt64Size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI64(self->cptr->GetDI64(uIdx));
	}

	PyObject* SetDI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= RoleDataMgr::Instance()->GetDynamicInt64Size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetDI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* IncDI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= RoleDataMgr::Instance()->GetDynamicInt64Size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncDI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* DecDI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= RoleDataMgr::Instance()->GetDynamicInt64Size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecDI64(uIdx, nValue);
		Py_RETURN_NONE;
	}


	PyObject* InitCI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitCI8(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriCI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriCI8_NewRef();
	}

	PyObject* GetCI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetClientInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetCI8(uIdx));
	}

	PyObject* SetCI8(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int16 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hh", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetClientInt8Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetCI8(uIdx, static_cast<GE::Int8>(nValue));
		Py_RETURN_NONE;
	}

	PyObject* GetTI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetTempInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI64(self->cptr->GetTI64(uIdx));
	}

	PyObject* SetTI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetTempInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetTI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* IncTI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetTempInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->IncTI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* DecTI64(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int64 nValue = 0;
		if (!PyArg_ParseTuple(arg, "HL", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetTempInt64Array().size())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		if (nValue < 0)
		{
			PY_PARAM_ERROR("value must > 0.")
		}
		self->cptr->DecTI64(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* InitObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitObj(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriObj_NewRef();
	}

	PyObject* GetObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetObjArray().size())
		{
			PY_PARAM_ERROR("index out of range.");
		}
		return self->cptr->GetObj_NewRef(uIdx);
	}

	PyObject* GetObj_ReadOnly( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetObjArray().size())
		{
			PY_PARAM_ERROR("index out of range.");
		}
		return self->cptr->GetObj_ReadOnly_NewRef(uIdx);
	}

	PyObject* SetObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		PyObject* pValue = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pValue))
		{
			return NULL;
		}
		if (uIdx >= self->cptr->GetObjArray().size())
		{
			PY_PARAM_ERROR("index out of range.");
		}
		self->cptr->SetObj(uIdx, pValue);
		Py_RETURN_NONE;
	}

	PyObject* GetObjVersion( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= self->cptr->GetObjArray().size())
		{
			PY_PARAM_ERROR("index out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetObjVersion(uIdx));
	}

	PyObject* InitCD(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		self->cptr->InitCD(arg);
		Py_RETURN_NONE;
	}

	PyObject* SeriCD(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		return self->cptr->SeriCD_NewRef();
	}

	PyObject* GetCD(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= RoleDataMgr::Instance()->GetCDSize())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return GEPython::PyObjFromI32(self->cptr->GetCD(uIdx));
	}

	PyObject* SetCD(PyRoleObject* self, PyObject* arg)
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		GE::Int32 nValue = 0;
		if (!PyArg_ParseTuple(arg, "Hi", &uIdx, &nValue))
		{
			return NULL;
		}
		if (uIdx >= RoleDataMgr::Instance()->GetCDSize())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		self->cptr->SetCD(uIdx, nValue);
		Py_RETURN_NONE;
	}

	PyObject* GetTempObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		if (!GEPython::PyObjToUI16(arg, uIdx))
		{
			PY_PARAM_ERROR("param must be GE::Uint16.");
		}
		if (uIdx >= RoleDataMgr::Instance()->GetTempObjSize())
		{
			PY_PARAM_ERROR("uIdx out of range.");
		}
		return self->cptr->GetTempObj_NewRef(uIdx);
	}

	PyObject* SetTempObj( PyRoleObject* self, PyObject* arg )
	{
		IF_LOST_C_OBJ_RETURN;
		GE::Uint16 uIdx = 0;
		PyObject* pValue = Py_None;
		if (!PyArg_ParseTuple(arg, "HO", &uIdx, &pValue))
		{
			return NULL;
		}
		if (uIdx >= RoleDataMgr::Instance()->GetTempObjSize())
		{
			PY_PARAM_ERROR("index out of range.");
		}
		self->cptr->SetTempObj(uIdx, pValue);
		Py_RETURN_NONE;
	}

}

