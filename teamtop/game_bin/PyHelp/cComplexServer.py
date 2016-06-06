#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import cRole
cRole

#automatic_start
# 有41个Py函数定义

def RegBeforeNewDayCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册新的一天前的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 21 Py_RETURN_NONE;
	@see : { "RegBeforeNewDayCallFunction", RegBeforeNewDayCallFunction, METH_VARARGS, "注册新的一天前的回调函数 " },
	'''

def RegBeforeNewHourCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册新的一小时前的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 33 Py_RETURN_NONE;
	@see : { "RegBeforeNewHourCallFunction", RegBeforeNewHourCallFunction, METH_VARARGS, "注册新的一小时前的回调函数 " },
	'''

def RegBeforeNewMinuteCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册新的一分钟前的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 46 Py_RETURN_NONE;
	@see : { "RegBeforeNewMinuteCallFunction", RegBeforeNewMinuteCallFunction, METH_VARARGS, "注册新的一分钟前的回调函数 " },
	'''

def RegPerSecondCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册每秒钟的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 59 Py_RETURN_NONE;
	@see : { "RegPerSecondCallFunction", RegPerSecondCallFunction, METH_VARARGS, "注册每秒钟的回调函数 " },
	'''

def RegAfterNewMinuteCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册新的一分钟后的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 72 Py_RETURN_NONE;
	@see : { "RegAfterNewMinuteCallFunction", RegAfterNewMinuteCallFunction, METH_VARARGS, "注册新的一分钟后的回调函数 " },
	'''

def RegAfterNewHourCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册新的一小时后的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 85 Py_RETURN_NONE;
	@see : { "RegAfterNewHourCallFunction", RegAfterNewHourCallFunction, METH_VARARGS, "注册新的一小时后的回调函数 " },
	'''

def RegAfterNewDayCallFunction( fun_BorrowRef, idx=None ):
	'''
	注册新的一天后的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 97 Py_RETURN_NONE;
	@see : { "RegAfterNewDayCallFunction", RegAfterNewDayCallFunction, METH_VARARGS, "注册新的一天后的回调函数 " },
	'''

def RegSaveCallFunction1( fun_BorrowRef, idx=None ):
	'''
	注册保存进程状态时的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 109 Py_RETURN_NONE;
	@see : { "RegSaveCallFunction1", RegSaveCallFunction1, METH_VARARGS, "注册保存进程状态时的回调函数 " },
	'''

def RegSaveCallFunction2( fun_BorrowRef, idx=None ):
	'''
	注册保存进程状态时的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 121 Py_RETURN_NONE;
	@see : { "RegSaveCallFunction2", RegSaveCallFunction2, METH_VARARGS, "注册保存进程状态时的回调函数 " },
	'''

def RegSaveCallFunction3( fun_BorrowRef, idx=None ):
	'''
	注册保存进程状态时的回调函数
	@param fun_BorrowRef : PyObject*
	@param idx : I32
	@return: None 
			 line 133 Py_RETURN_NONE;
	@see : { "RegSaveCallFunction3", RegSaveCallFunction3, METH_VARARGS, "注册保存进程状态时的回调函数 " },
	'''

def RegTick( uSec, fun_BorrowRef, regparam_BorrowRef=None ):
	'''
	注册Tick
	@param uSec : UI32
	@param fun_BorrowRef : PyObject*
	@param regparam_BorrowRef : PyObject*
	@return: I64 
			 line 146 return GEPython::PyObjFromI64(ID);
	@see : { "RegTick", RegTick, METH_VARARGS, "注册Tick " },
	'''

def UnregTick( arg):
	'''
	取消Tick
	@param arg : PyObject*
	@return: None 
			 line 157 Py_RETURN_NONE;
	@warning: if (!GEPython::PyObjToI64(arg, ID))
	@see : { "UnregTick", UnregTick, METH_O, "取消Tick " },
	'''

def TiggerTick( ID, param_BorrowRef=None ):
	'''
	触发Tick
	@param ID : UI64
	@param param_BorrowRef : PyObject*
	@return: None 
			 line 169 Py_RETURN_NONE;
	@see : { "TiggerTick", TiggerTick, METH_VARARGS, "触发Tick " },
	'''

def RegFastTick( uSec, fun_BorrowRef, regparam_BorrowRef=None ):
	'''
	注册FastTick
	@param uSec : UI32
	@param fun_BorrowRef : PyObject*
	@param regparam_BorrowRef : PyObject*
	@return: I64 
			 line 192 return GEPython::PyObjFromI64(ID);
	@see : { "RegFastTick", RegFastTick, METH_VARARGS, "注册FastTick " },
	'''

def UnregFastTick( arg):
	'''
	取消FastTick
	@param arg : PyObject*
	@return: None 
			 line 203 Py_RETURN_NONE;
	@warning: if (!GEPython::PyObjToI64(arg, ID))
	@see : { "UnregFastTick", UnregFastTick, METH_O, "取消FastTick " },
	'''

def TriggerFastTick( arg):
	'''
	触发FastTick
	@param arg : PyObject*
	@return: None 
			 line 214 Py_RETURN_NONE;
	@warning: if (!GEPython::PyObjToI64(arg, ID))
	@see : { "TriggerFastTick", TriggerFastTick, METH_O, "触发FastTick " },
	'''

def CreateNetwork( uMaxConnect, uThread=None , uTGWMaxSize=None ):
	'''
	创建网络层
	@param uMaxConnect : UI32
	@param uThread : UI16
	@param uTGWMaxSize : UI16
	@return: None 
			 line 228 Py_RETURN_NONE;
	@see : { "CreateNetwork", CreateNetwork, METH_VARARGS, "创建网络层 " },
	'''

def Listen( uPort):
	'''
	监听端口
	@param uPort : UI32
	@return: None 
			 line 239 Py_RETURN_NONE;
	@see : { "Listen", Listen, METH_O, "监听端口 " },
	'''

def SetConnectParam( CP_uRecvBlockNum, CP_uRecvBlockSize, CP_uSendBlockNum, CP_uSendBlockSize):
	'''
	设置网络层参数
	@param CP_uRecvBlockNum : UI16
	@param CP_uRecvBlockSize : UI16
	@param CP_uSendBlockNum : UI16
	@param CP_uSendBlockSize : UI16
	@return: None 
			 line 250 Py_RETURN_NONE;
	@see : { "SetConnectParam", SetConnectParam, METH_VARARGS, "设置网络层参数 " },
	'''

def SetPyThread( arg):
	'''
	设置是否可以多线程
	@param arg : PyObject*
	@return: None 
			 line 260 Py_RETURN_NONE;
	@warning: int ret = PyObject_IsTrue(arg);
	@see : { "SetPyThread", SetPyThread, METH_O, "设置是否可以多线程 " },
	'''

def InitMySQLdb( ):
	'''
	初始化MySQLdb模块
	@return: None 
			 line 266 Py_RETURN_NONE;
	@see : { "InitMySQLdb", InitMySQLdb, METH_NOARGS, "初始化MySQLdb模块" },
	'''

def Stop( ):
	'''
	停止，跳出循环
	@return: None 
			 line 272 Py_RETURN_NONE;
	@see : { "Stop", Stop, METH_NOARGS, "停止，跳出循环 " },
	'''

def Connect( sIP, uPort, uWho, CP_uRecvBlockNum=None , CP_uRecvBlockSize=None , CP_uSendBlockNum=None , CP_uSendBlockSize=None ):
	'''
	连接
	@param sIP : string
	@param uPort : UI32
	@param uWho : UI16
	@param CP_uRecvBlockNum : UI16
	@param CP_uRecvBlockSize : UI16
	@param CP_uSendBlockNum : UI16
	@param CP_uSendBlockSize : UI16
	@return: UI32 
			 line 286 return GEPython::PyObjFromUI32(uSessionID);
	@see : { "Connect", Connect, METH_VARARGS, "连接 " },
	'''

def DisConnect( uSession):
	'''
	断开连接
	@param uSession : UI32
	@return: None 
			 line 297 Py_RETURN_NONE;
	@see : { "DisConnect", DisConnect, METH_O, "断开连接 " },
	'''

def IsSendOver( uSession):
	'''
	消息是否发送完毕
	@param uSession : UI32
	@see : { "IsSendOver", IsSendOver, METH_O, "消息是否发送完毕 " },
	'''

def Ping( uSession):
	'''
	给连接发心跳包（异步发送模式下可以驱动消息发送）
	@param uSession : UI32
	@return: None 
			 line 319 Py_RETURN_NONE;
	@see : { "Ping", Ping, METH_O, "给连接发心跳包（异步发送模式下可以驱动消息发送） " },
	'''

def SendPyMsg( uSessionID, uMsgType, msg_BorrowRef):
	'''
	发送Python消息
	@param uSessionID : UI32
	@param uMsgType : UI16
	@param msg_BorrowRef : PyObject*
	@return: None 
			 line 332 Py_RETURN_NONE;
	@see : { "SendPyMsg", SendPyMsg, METH_VARARGS, "发送Python消息 " },
	'''

def SendPyMsgAndBack( uSessionID, uMsgType, msg_BorrowRef, uTimeOver, fun_BorrowRef, param_BorrowRef=None ):
	'''
	发送Python消息并等待回调
	@param uSessionID : UI32
	@param uMsgType : UI16
	@param msg_BorrowRef : PyObject*
	@param uTimeOver : UI32
	@param fun_BorrowRef : PyObject*
	@param param_BorrowRef : PyObject*
	@return: None 
			 line 349 Py_RETURN_NONE;
	@see : { "SendPyMsgAndBack", SendPyMsgAndBack, METH_VARARGS, "发送Python消息并等待回调 " },
	'''

def RegDistribute( uMsgType, fun_BorrowRef):
	'''
	注册消息处理函数
	@param uMsgType : UI16
	@param fun_BorrowRef : PyObject*
	@return: None 
			 line 362 Py_RETURN_NONE;
	@see : { "RegDistribute", RegDistribute, METH_VARARGS, "注册消息处理函数 " },
	'''

def UnregDistribute( uMsgType):
	'''
	取消消息处理函数
	@param uMsgType : UI16
	@return: None 
			 line 373 Py_RETURN_NONE;
	@see : { "UnregDistribute", UnregDistribute, METH_O, "取消消息处理函数 " },
	'''

def GetDistribute( uMsgType):
	'''
	获取消息处理函数
	@param uMsgType : UI16
	@return: PyObject* 
			 line 383 return ComplexServer::Instance()->GetDistribute_NewRef(uMsgType);
	@warning: return ComplexServer::Instance()->GetDistribute_NewRef(uMsgType);
	@see : { "GetDistribute", GetDistribute, METH_O, "获取消息处理函数 " },
	'''

def DoDistribute( uMsgType, pyMsg):
	'''
	进行消息处理
	@param uMsgType : UI16
	@param pyMsg : PyObject*
	@see : { "DoDistribute", DoDistribute, METH_VARARGS, "进行消息处理 " },
	'''

def CallBackFunction( uSessionID, ID, arg_BorrowRef=None ):
	'''
	呼叫等待回调的函数
	@param uSessionID : UI32
	@param ID : UI64
	@param arg_BorrowRef : PyObject*
	@return: None 
			 line 407 Py_RETURN_NONE;
	@see : { "CallBackFunction", CallBackFunction, METH_VARARGS, "呼叫等待回调的函数 " },
	'''

def DoBackFunction( ID, arg_BorrowRef):
	'''
	进行回调处理
	@param ID : UI64
	@param arg_BorrowRef : PyObject*
	@see : { "DoBackFunction", DoBackFunction, METH_VARARGS, "进行回调处理 " },
	'''

def SetSaveGapMinute( uSGM1=None , uSGM2=None , uSGM3=None ):
	'''
	设置保存时间间隔（分钟）
	@param uSGM1 : UI32
	@param uSGM2 : UI32
	@param uSGM3 : UI32
	@return: None 
			 line 437 Py_RETURN_NONE;
	@see : { "SetSaveGapMinute", SetSaveGapMinute, METH_VARARGS, "设置保存时间间隔（分钟） " },
	'''

def GetSaveGapMinute( ):
	'''
	获取保存时间间隔（分钟）
	@return: UI32,UI32,UI32 
			 line 442 return Py_BuildValue("III", ComplexServer::Instance()->SaveGapMinute1(), ComplexServer::Instance()->SaveGapMinute2(), ComplexServer::Instance()->SaveGapMinute3());
	@see : { "GetSaveGapMinute", GetSaveGapMinute, METH_NOARGS, "获取保存时间间隔（分钟） " },
	'''

def IsTimeDriver( ):
	'''
	是否是在时间驱动中
	@see : { "IsTimeDriver", IsTimeDriver, METH_VARARGS, "是否是在时间驱动中 " },
	'''

def CallSave( ):
	'''
	直接触发保存回调函数
	@return: None 
			 line 455 Py_RETURN_NONE;
	@see : { "CallSave", CallSave, METH_VARARGS, "直接触发保存回调函数 " },
	'''

def GetLastMsgTime( ):
	'''
	获取最后处理的消息时间
	@return: UI32 
			 line 460 return GEPython::PyObjFromUI32(ComplexServer::Instance()->LastMsgTime());
	@see : { "GetLastMsgTime", GetLastMsgTime, METH_VARARGS, "获取最后处理的消息时间 " },
	'''

def SetSendModel( arg):
	'''
	设置网络层发送消息模式
	@param arg : PyObject*
	@return: None 
			 line 474 Py_RETURN_NONE;
	@warning: if (PyObject_IsTrue(arg))
	@see : { "SetSendModel", SetSendModel, METH_O, "设置网络层发送消息模式 " },
	'''

def SetFastEndTime( ui32):
	'''
	设置时间速度
	@param ui32 : UI32
	@return: None 
			 line 485 Py_RETURN_NONE;
	@see : { "SetFastEndTime", SetFastEndTime, METH_O, "设置时间速度 " },
	'''

#automatic_end
