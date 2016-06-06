/************************************************************************
基础服务
************************************************************************/
#pragma once
#include <boost/unordered_map.hpp>
#include "../GameEngine/GameEngine.h"

class ComplexServer
	: public GEControlSingleton<ComplexServer>
{
	GE_DISABLE_BOJ_CPY(ComplexServer);
	typedef boost::unordered_map<GE::Uint16, PyObject*>		PyMsgDistribute;
public:
	ComplexServer();
	~ComplexServer();

public:
	void						Init(int argc, char* argv[]);				//初始化基类
	void						InitC();									//初始化其他C数据
	void						InitCPython();								//初始化C和python相关的数据
	void						Loop();										//不支持Python线程的主循环
	void						Loop_PyThread();							//支持Python线程的主循环
	void						FinalC();									//结束其他C数据

public:
	// Tick
	GETick*						Tick() {return m_pTick;}
	GEFastTick*					FastTick() {return m_pFastTick;}
	/*
	Update函数会触发下面的时间函数，如果同一时刻有多个触发
	那么他们触发的顺序是：
	Update -> CallBeforeNewDay --> CallBeforeNewHour --> CallBeforeNewMinute -->
	CallPerSecond --> CallAfterNewMinute --> CallAfterNewHour --> CallAfterNewDay
	*/
	void						Update();
	void						CallBeforeNewDay();//注意，这个已经是新的一天了，只是按照顺序定义了函数的名字而已
	void						CallBeforeNewHour();//同理，这个已经是新的一个小时了
	void						CallBeforeNewMinute();
	void						CallPerSecond();
	void						CallAfterNewMinute();
	void						CallAfterNewHour();
	void						CallAfterNewDay();//注意！这个和CallBeforeNewDay中获取的时间是一样的，只是调用先后顺序不一样而已
	PyFunctionCall_Vector&		GetCallBeforeNewDayFunction(){return m_PyFunctionCallBeforeNewDay;}
	PyFunctionCall_Vector&		GetCallBeforeNewHourFunction(){return m_PyFunctionCallBeforeNewHour;}
	PyFunctionCall_Vector&		GetCallBeforeNewMinuteFunction(){return m_PyFunctionCallBeforeNewMinute;}
	PyFunctionCall_Vector&		GetCallPerSecondFunction(){return m_PyFunctionCallPerSecond;}
	PyFunctionCall_Vector&		GetCallAfterNewMinuteFunction(){return m_PyFunctionCallAfterNewMinute;}
	PyFunctionCall_Vector&		GetCallAfterNewHourFunction(){return m_PyFunctionCallAfterNewHour;}
	PyFunctionCall_Vector&		GetCallAfterNewDayFunction(){return m_PyFunctionCallAfterNewDay;}
	/*
	为了保证状态的一致，还是统一由一个地方保存整个进程的状态
	*/
	virtual void				CallSave1();
	virtual void				CallSave2();
	virtual void				CallSave3();
	PyFunctionCall_Vector&		GetCallSaveFunction1() {return m_PyFunctionCallSave1;}
	PyFunctionCall_Vector&		GetCallSaveFunction2() {return m_PyFunctionCallSave2;}
	PyFunctionCall_Vector&		GetCallSaveFunction3() {return m_PyFunctionCallSave3;}

public:
	void						CreateNetwork(GE::Uint32 uMaxConnect, GE::Uint16 uThread);									//创建网络层
	void						Listen(GE::Uint32 uPort);																	//监听网络层
	void						SetConnectParam(ConnectParam& CP);															//设置连接参数
	void						StopNetwork();																				//停止网络层和消息循环
	GE::Uint32					Connect(const char* sIP, GE::Uint32 uPort, GE::Uint16 uWho, ConnectParam* pCP = NULL);		//主动连接
	void						DisConnect(GE::Uint32 uSessionID, GE::Uint16 uReason);										//断开连接
	bool						HasConnect(GE::Uint32 uSessionID);															//是否有这个连接
	void						SetConnectForward(GE::Uint32 uSessionID);													//设置连接消息导向
	void						OnLost();																					//有连接断开
	void						OnMsg();																					//有消息
	bool						IsSendOver(GE::Uint32 uSessionID);															//该连接的消息是否发生完毕
	
	bool						RemoteEndPoint(GE::Uint32 uSessionID, std::string& sIP, GE::Uint32& uPort);

	void						SendMsg(GE::Uint32 uSessionID, MsgBase* pMsg);												//发送一个消息
	void						BroadMsg(GE::Uint16 uWho, MsgBase* pMsg);													//广播一个消息
	void						SendBytes(GE::Uint32 uSessionID, void* pHead, GE::Uint16 uSize);							//发送一个字节流
	void						BroadBytes(GE::Uint16 uWho, void* pHead, GE::Uint16 uSize);									//广播一个字节流
	void						SendPyMsg(GE::Uint32 uSessionID, GE::Uint16 uMsgType, PyObject* msg_BorrowRef);				//发送一个消息体为Python的消息
	void						SendPyMsgAndBack(GE::Uint32 uSessionID, GE::Uint16 uMsgType, PyObject* msg_BorrowRef,
										GE::Uint32 uSec, PyObject* cbfun_BorrowRef, PyObject* regparam_BorrowRef);			//发送一个消息体为Python的消息并且等待回调
	void						CallBackFunction(GE::Uint32 uSessionID, GE::Int64 ID, PyObject* arg_BorrowRef);				//呼唤一个等待回调的函数
	void						RegDistribute(GE::Uint16 uMsgType, PyObject* fun_borrorRef);								//注册Python消息处理函数
	void						UnregDistribute(GE::Uint16 uMsgType);														//取消Python消息处理函数
	PyObject*					GetDistribute_NewRef(GE::Uint16 uMsgType);													//获取Python消息处理函数

	inline bool					DoWho();																					//调用当前身份的处理函数
	inline bool					DoMsg();																					//调用当前消息的处理函数
	bool						DoDistribute(GE::Uint16 uMsgType, PyObject* borrowRef);										//进行消息处理
	bool						DoCallBackFunction(GE::Int64 uTickID, PyObject* borrowRef);									//进行回调函数处理
	bool						DoCurDistribute();																			//调用当前消息的处理Python函数
	bool						DoCurCallBackFunction();																	//调用当前回调的Python函数
	
public:
	void						SetPyThread(bool b) {m_bPyThread = b;}
	void						InitMySQLdb();
	GE::Uint32&					SaveGapMinute1() {return m_SaveGapMinute1;}
	GE::Uint32&					SaveGapMinute2() {return m_SaveGapMinute2;}
	GE::Uint32&					SaveGapMinute3() {return m_SaveGapMinute3;}
	bool						IsTimeDriver() {return m_bIsTimeDriver;}
	GE::Uint32					LastMsgTime() {return m_uLastMsgTime;}
	void						SetSendModel(bool bThreadSend) {this->m_pNetWork->SetSendModel(bThreadSend);}
	void						SetFastEndTime(GE::Uint32 ui32) {m_uFastEndTime = ui32;}

private:
	// 网络
	GENetWork*					m_pNetWork;
	PyMsgDistribute				m_PyMsgDistribute;
	// 时间（这里要等到Python初始化后才能构建Tick对象）
	GETick*						m_pTick;
	GEFastTick*					m_pFastTick;
	PyFunctionCall_Vector		m_PyFunctionCallBeforeNewDay;
	PyFunctionCall_Vector		m_PyFunctionCallBeforeNewHour;
	PyFunctionCall_Vector		m_PyFunctionCallBeforeNewMinute;
	PyFunctionCall_Vector		m_PyFunctionCallPerSecond;
	PyFunctionCall_Vector		m_PyFunctionCallAfterNewMinute;
	PyFunctionCall_Vector		m_PyFunctionCallAfterNewHour;
	PyFunctionCall_Vector		m_PyFunctionCallAfterNewDay;
	GE::Uint32					m_SaveGapMinute1;
	GE::Uint32					m_SaveGapMinute2;
	GE::Uint32					m_SaveGapMinute3;
	PyFunctionCall_Vector		m_PyFunctionCallSave1;
	PyFunctionCall_Vector		m_PyFunctionCallSave2;
	PyFunctionCall_Vector		m_PyFunctionCallSave3;
	// 多线程Python函数调用
	GEPython::Function			m_pyFunction;
	// 是否是多Python线程
	bool						m_bPyThread;
	// 脚本函数
	GEPython::Function			m_PyFunction_NewConnect;
	GEPython::Function			m_PyFunction_LostConnect;
	// 是否在非保存回调的时间回调函数中
	bool						m_bIsTimeDriver;
	GE::Uint32					m_uLastMsgTime;
	GE::Uint32					m_uFastEndTime;

};

