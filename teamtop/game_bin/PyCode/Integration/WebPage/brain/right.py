# -*- coding:UTF-8 -*-
import time,traceback
import me,tool,memory,user,model
def add():
	if not user.inGroup("host"):return user.ban()
	return model.add()
def edit():
	if not user.inGroup("host"):return user.ban()
	if 'rid' in me.S['P'] and 'game' not in me.S['P']:
		me.S['P']['game']=''
	return model.edit()
def guide():
	if not user.inGroup("host"):return user.ban()
	return model.guide()

#获取权限列表
def getAll():
	data={}
	groups=me.S.get('user',{"group":""}).get('group').split(",")
	groups.append('public')
	groups.append('common')
	game=''
	if not str(me.S['A']['game'])=='0':
		game=me.S['A']['game']
	data=memory.get("recall",{"key":"byname","model":"rights","field":"name,byname,ugroup","filter":'(game="" or instr(game,"%s")<=0) and ugroup in ("%s")'%(game,'","'.join(groups)),"option":{"order":"byname,asc"}})
	return data