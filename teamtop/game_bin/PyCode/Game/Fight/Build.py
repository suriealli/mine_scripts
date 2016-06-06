#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Build")
#===============================================================================
# 构建被动技能和buff的事件
#===============================================================================
import inspect
import traceback
from Game.Fight import Handle
from Util.PY import Load, PyParseBuild

ListenObjs = {"u":"unit", "c":"camp", "o":"other_camp", "f":"fight"}

def ShowBuild():
	h = Handle.Handle()
	for name in dir(h):
		if not name.startswith("event_"):
			continue
		v = getattr(h, name)
		args, _, _, _ = inspect.getargspec(v)
		print "\t#%s\n\tdef auto_u_%s(%s):\n\t\tpass\n\t" % (v.__doc__, name[6:], ", ".join(args))

def GetHandleInfo():
	hs = set()
	info = {}
	h = Handle.Handle()
	for name in dir(h):
		if name.startswith("__") and name.endswith("__"):
			continue
		v = getattr(h, name)
		# 获取事件集合
		if type(v) == type(set()):
			hs.add(name[1:])
		# 获取触发函数
		if name.startswith("event_"):
			# 计算出各个直需要的参数个数
			args, _, _, _ = inspect.getargspec(v)
			info[name[6:]] = len(args)
	assert(hs == set(info.iterkeys()))
	return info

def GetBuildModule():
	for module in Load.LoadPartModule("Game.Fight.PassiveSkill."):
		yield module
	for module in Load.LoadPartModule("Game.Fight.Buff."):
		yield module

def BuildOneModule(module, handle_info):
	# 拓展模块不构建
	if module.__name__.endswith("_ex"):
		return
	# init模块不构建
	if module.__file__.find("__init__") >= 0:
		return
	cls_name = module.__name__.split('.')[-1]
	cls_type = getattr(module, cls_name)
	load_infos = []
	unload_infos = []
	for name in dir(cls_type):
		if not name.startswith("auto_"):
			continue
		# 获取监听对象
		listen_obj = name[5]
		# 获取监听事件
		listen_event = name[7:]
		if listen_event == "round" and listen_obj != "f":
			print "GE_EXC, module(%s) round event must listen f" % (module.__name__)
			continue
		# 获取参数
		args, _, _, _ = inspect.getargspec(getattr(cls_type, name))
		# 检测
		assert listen_obj in ListenObjs
		assert handle_info[listen_event] == len(args)
		# 保存之
		load_infos.append("\t\tself.%s._%s.add(self.%s)" % (ListenObjs[listen_obj], listen_event, name))
		unload_infos.append("\t\tself.%s._%s.discard(self.%s)" % (ListenObjs[listen_obj], listen_event, name))
	# 注意没事件的情况
	if not load_infos: load_infos.append("\t\tpass")
	if not unload_infos: unload_infos.append("\t\tpass")
	# 构建完整的代码
	code_infos = ["\tdef load_event(self):"]
	code_infos.extend(load_infos)
	code_infos.append("\t")
	code_infos.append("\tdef unload_event(self):")
	code_infos.extend(unload_infos)
	# 构建载入和卸载函数
	pf = PyParseBuild.PyFile(module.__name__)
	pf.ReplaceXRLAM()
	pf.ReplaceCode(code_infos)
	pf.Write()
	
if __name__ == "__main__":
	Load.LoadPartModule("Game.Fight.ActiveSkill")
	Load.LoadPartModule("Game.Fight.Buffs")
	Load.LoadPartModule("Game.Fight.PassiveSkill")
	handle_info = GetHandleInfo()
	for module in GetBuildModule():
		try:
			BuildOneModule(module, handle_info)
		except:
			print "GE_EXC, Build module(%s) error." % module.__name__
			traceback.print_exc()




	