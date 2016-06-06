/************************************************************************
区域定义
************************************************************************/
#include <boost/intrusive/list.hpp>

#pragma once

//自动解链 成员链表钩子
typedef boost::intrusive::link_mode< boost::intrusive::auto_unlink >		LinkMode;
typedef boost::intrusive::constant_time_size< false >						ConstantTimeSize;
typedef boost::intrusive::list_member_hook< LinkMode >						ListMemberHook;

