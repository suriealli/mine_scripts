#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import time,traceback
from Integration.WebPage.brain import me,tool
from Integration.WebPage.brain.serve import db

def levelUp(msg={}):
	data={}
	#必须提供角色ID
	if 'role_id' not in msg or 'level_up' not in msg: 
		data['tips']="请提供角色ID及提升等级！-Please Provide Role ID and LEVEL"
		
	#构造封禁命令
	command='import Game.Role.RoleGM as gm;gm.ToLevelEx(role,%s)'%(msg['level_up'])
	try:
		result=sendCommand(msg['role_id'],command)
		data['tips']="执行成功! %s"%command
	except:
		traceback.print_exc()
		data['tips']="执行出错，请联系管理员!ERROR %s"%command
	return data

def ban(msg={}):
	data={}
	#默认封禁类型为 禁言
	if 'type' not in msg: 
		msg['type']="speak"
	#必须提供角色ID
	if 'role_id' not in msg: 
		data['tips']="请提供角色ID！-Please Provide Role ID"
		
	#构造封禁命令
	command=''
	commands={
		"speak":'role.SetCanChatTime(%s)' % (msg['end_time']),
		"login":'role.SetCanLoginTime(%s)' % (msg['end_time']),
		"ban_speak":'role.SetCanChatTime(%s)'%(msg['expire_time'])
	}
	if msg['type'] in commands:
		command=commands[msg['type']]
	
	#获取用户ID列表
	msg['role_id']=msg['role_id'].split(',')
	#结果记录
	done=[[],[]]
	for role_id in msg['role_id']:
		role_id=int(role_id)
		#ban
		try:
			result=False
			if command!="":
				result=sendCommand(role_id,command)
			elif msg['type']=="ban_login": #解除封禁
				result=db.M.get("remember",{
					"action":"edit",
					"db":"role:%s"%role_id,
					"from":"lostnote",
					"app":"role_data",
					"data":{"di32_3":0},
					"filter":{
						"role_id":role_id
					}
				})
			if not result:
				done[0].append(str(role_id))
			else:
				done[1].append(str(role_id))
		except:
			traceback.print_exc()
			#data['tips']="执行出错，请联系管理员!ERROR %s"%command
	data['tips']='操作结果：成功SUCCESS[%s],失败FAILED[%s],COMMAND:%s' % (
		','.join(done[1]),
		','.join(done[0]),
		command
	)
	return data

def sendMsg(msg=None):
	if not msg:msg={}
	data={}
	if msg.get('role_id','')=='' or msg.get('msg','')=='':
		data['tips']="参数不全"
		return data
	#from Integration.Help import Concurrent
	#from Integration.WebPage.brain import tool
	from ComplexServer.Plug.DB import DBHelp
	command='''("Game.ThirdParty.GameMsg", "RoleGSEX", ('%s', '%s'))'''
	from django.utils import encoding
	msg['msg'] = msg['msg'].replace("'",'').replace('"','')
	command = command % (msg['msg'], msg.get('link',''))
	command = encoding.smart_str(command)
	done=[]
	failed=[]
	for v in msg['role_id'].split(','):
		try:
			if DBHelp.SendRoleCommend(int(v), command):
				done.append(v)
			else:
				failed.append(v)
				data['tips']="发送失败，没有这个角色"
		except:
			data['tips']="发送失败(异常)，请重试或联系管理员！"
			traceback.print_exc()
	data['tips']="发送：%s(成功：[%s]失败:[%s])"%(msg['msg'],','.join(done),','.join(failed))
	#print data
	return data

def sendCommand(role_id,m):
	from ComplexServer.Plug.DB import DBHelp
	con=db.M.openMemory({"db":"role:%s" % role_id,"dict":False})
	done=False
	try:
		done=DBHelp.InsertRoleCommand_Con(con, int(role_id), m)
	except:
		traceback.print_exc()
		pass
	return done

def sendMail(msg=None):
	from ComplexServer.Plug.DB import DBHelp
	data={}
	if not msg:msg={}
	
	#全服等级限制
	msg['level']=msg.get('level',"0")
	
	#items
	mail_item=[]
	msg['items']=msg['items'].split(',')
	for v in msg['items']:
		v=v.split('_')
		if len(v)==1:
			continue
		mail_item.append((int(v[0]),int(v[1])))
	#mail obj
	for k,v in msg.items():
		if k in ['money','exp','strength','bindrmb','unbindrmb']:
			if v=='':
				msg[k]='0'
	mail_obj={
		1:int(msg['money']),
		2:int(msg['exp']),
		3:int(msg['strength']),
		4:int(msg['bindrmb']),
		5:int(msg['unbindrmb']),
		6:mail_item
	}
	#print mail_obj
	#servers
	servers=msg['server'].split(',')
	import server,os,time
	if str(msg['server'])=="all":
		servers=server.getAll().keys()
	#log
	log=[(msg['sender'],msg["title"],msg['content'],mail_obj)]
	#mail_log
	log_tra = 30005
	for sv in servers:
		#roles		
		roles={}
		if str(msg['role_id'])!="5201314":
			#single
			single_role=int(msg['role_id'])
			link=db.M.openMemory({"dict":False,"db":"server:%s"%sv})
			with link as cur:
				#send to each role
				result=DBHelp.InsertRoleMail(cur,single_role,msg['title'],msg['sender'],msg['content'],log_tra,mail_obj)
				log.append((single_role,result))
			link.close()
		else:
			roles=[]
			#find active roles in two weeks
			temp=()
			sql="select role_id from role_data where unix_timestamp(now()) - di32_0 < %s and di32_11>=%s;" % (DBHelp.TwoWeekSecond,int(msg['level']))
			link=db.M.openMemory({"dict":False,"db":"server:%s"%sv})
			with link as cur:
				cur.execute(sql)
				temp=cur.fetchall()
				for v in temp:
					roles.append(v[0])
				#send
				#send to each role
				for single_role in roles:
					result=DBHelp.InsertRoleMail(cur,single_role,msg['title'],msg['sender'],msg['content'],log_tra,mail_obj)
					log.append((single_role,result))
			link.close()
	from ThirdLib import PrintHelp
	data['log']=repr(log)
	#if all,log to file in case of log loss
	if str(msg['role_id'])=="5201314":
		#创建目录
		#absolute path
		log_path=os.path.abspath(os.path.dirname(__file__)).replace("brain%sserve"%os.sep,"file%slog"%os.sep)
		try:
			if not os.path.isdir(log_path):
				print 'created path:%s'%(log_path)
				os.makedirs('%s'%(log_path))
		except:
			print 'Cannot Create Dir %s'%log_path
			traceback.print_exc()
			pass
		#创建文件
		code=open('%s%srole-sendMail-%s-%s-%s.txt'%(log_path,os.sep,msg['server'],msg['role_id'],int(time.time())), "w")
		try:
			code.write(data['log'])
		except:
			traceback.print_exc()
			pass
		code.close()
	#common log
	from Integration.WebPage.User import Permission
	Permission.monitor({"get":repr(msg)},data['log'],"/role/sendMail",True)
	data['tips']="邮件已经成功发送！"
	return data