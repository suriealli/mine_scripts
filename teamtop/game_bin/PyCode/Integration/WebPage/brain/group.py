# -*- coding:UTF-8 -*-
import time,traceback
import me,tool,memory,user,model
def add():
	if not user.inGroup("host"):return user.ban()
	return model.add()
def edit():
	if not user.inGroup("host"):return user.ban()
	return model.edit()
def guide():
	if not user.inGroup("host"):return user.ban()
	return model.guide()