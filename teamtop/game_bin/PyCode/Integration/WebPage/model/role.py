#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback,time
import me,server,tool

#查看角色信息
def check(R):
	data={}
	get={}
	get['type']=me.G(R,'type')
	get['id']=me.G(R,'id')
	get['server']=me.G(R,'server','int')
	data['get']=get
	data['servers']=server.getAll()
	if get['id']:
		#transfer id
		id=get['id']
		if get['type']!='roleid':
			id=getID({"from":get['type'],"id":get['id'],"server":get['server']})
		elif not id.isdigit():
			data['tips']="角色ID必须为数字！"
			return data
		if not id:
			data['tips']="角色ID不存在！"
		else:
			data['data']=me.M('recall',{"one":"true","memory":"role:%s" % id,"model":"role_data","field":"role_id,di32_3,di32_4,di32_6,di32_11,di32_12,di32_13,di32_14,di32_16,di32_21,account,role_name","filter":{"role_id":id}})
			data['data']['last_save']=tool.date(data['data']['di32_16'],'%Y-%m-%d %H:%M:%S') #最后保存
			data['data']['ban_login']=tool.date(data['data']['di32_3']) #封号
			if data['data']['di32_4']<time.time():
				data['data']['di32_4']=0
			data['data']['ban_speak']=tool.date(data['data']['di32_4']) #禁言
			data['data']['spent_q']=data['data']['di32_6'] #消费Q点
			data['data']['level']=data['data']['di32_11'] #等级
			data['data']['vip']=data['data']['di32_12'] #VIP贵族
			#data['data']['royalty']=data['data']['di32_21'] #皇室
			data['data']['bindrmb']=data['data']['di32_14'] #魔晶
			data['data']['unbindrmb']=data['data']['di32_13'] #神石
	return data
	
def getID(m):
	if 'server' not in m or 'from' not in m or 'id' not in m:
		return
	id_field="role_name"
	if m['from']=="account":
		id_field="account"
	temp=me.M('recall',{"one":"true","memory":"server:%s" % m['server'],"model":"role_data","field":"role_id","filter":{id_field:m['id']}})
	if temp and 'role_id' in temp:
		return temp['role_id']
def getInfo(roleid,field="role_name"):
	temp=me.M('recall',{"one":"true","memory":"role:%s" % roleid,"model":"role_data","field":field,"filter":{"role_id":roleid}})
	if temp:
		return temp

def ban(R):
	data={}
	get={}
	get['type']=me.G(R,'type')
	get['id']=me.G(R,'id')
	get['ban_type']=me.G(R,'ban_type','int')
	get['end_date']=me.G(R,'end_date')
	get['server']=me.G(R,'server','int')
	data['get']=get
	data['servers']=server.getAll()
	import time,tool
	if not get['end_date']:#默认封禁1年
		get['end_date']=tool.date(int(time.time())+86400*365)
	if get['id']:
		#transfer id
		id=get['id']
		if get['type']!='roleid':
			id=getID({"from":get['type'],"id":get['id'],"server":get['server']})
		elif not id.isdigit():
			data['tips']="角色ID必须为数字！"
			return data
		if not id:
			data['tips']="角色ID不存在！"
		else:
			id=int(id) #to digit
			command=''
			end_time=tool.strtotime(get['end_date'],'%Y-%m-%d')
			expire_time=int(time.time())-864000
			commands={
				0:'role.SetCanChatTime(%s)' % end_time,
				1:'role.SetCanLoginTime(%s)' % end_time,
				2:'role.SetCanChatTime(%s)' % expire_time
			}
			if get['ban_type'] in commands:
				command=commands[get['ban_type']]
			try:
				result=False
				if get['ban_type'] in [0,1,2]:
					result=sendCommand(id,command)
				elif get['ban_type']==3: #解除封禁
					result=me.M("remember",{"action":"edit","memory":"role:%s" % id,"from":"lostnote","model":"role_data","data":{"di32_3":0},"filter":{"role_id":id}})
				data['tips']='执行：%s 成功！' % command
				if not result:
					data['tips']='角色已经流失或系统异常，请到角色信息功能查询最新玩家信息，没必要请不要重复操作！'
			except:
				traceback.print_exc()
				data['tips']="执行出错，请联系管理员!%s"%command
			
	data['get']=get
	return data

def sendCommand(role,m):
	from ComplexServer.Plug.DB import DBHelp
	con=me.openMemory({"memory":"role:%s" % role,"dict":False})
	return DBHelp.InsertRoleCommand_Con(con, role, m)
	
#send mail
def sendMail(R):
	data={}
	get={}
	import json
	#to send
	if 'content' in R.POST:
		get['content']=me.G(R,"content")
		get['title']=me.G(R,"title")
		get['sender']=me.G(R,"sender")
		get['roleid']=me.G(R,"roleid","int")
		get['items']=me.G(R,"items","list")
		get['servers']=me.G(R,"database","list")
		get['money']=me.G(R,"money","int")
		get["exp"]=me.G(R,"exp","int")
		get["strength"]=me.G(R,"strength","int")
		get["unbindrmb"]=me.G(R,"unbindrmb","int")
		get["bindrmb"]=me.G(R,"bindrmb","int")
		
		data['get']=get
		if get['sender'] and get['title'] and get['content'] and get['servers'] and get['roleid']:
			try:
				mail_item=[]
				for v in get['items']:
					v=v.split('_')
					mail_item.append((int(v[0]),int(v[1])))
				mail_wealth=(get['money'],get['exp'],get['unbindrmb'],get['bindrmb'],get['strength'])
				
				from ComplexServer.Plug.DB import DBHelp
				roles={}
				if get['roleid']!=5201314:
					#single
					roles={get['servers'][0]:[get['roleid']]}
				else:
					#multi server
					for v in get['servers']:
						roles[v]=[]
						#find active roles in two weeks
						temp=()
						sql="select role_id from role_data where unix_timestamp(now()) - di32_0 < %s;" % DBHelp.TwoWeekSecond
						temp=me.M("query",{"memory":"server:%s"%v,"sql":sql})
						for vv in temp:
							roles[v].append(vv['role_id'])
							
				#send
				log=[(get['sender'],get["title"],get['content'],mail_item,mail_wealth)]
				for server,roleids in roles.items():
					#server cur
					with me.openMemory({"dict":False,"memory":"server:%s"%server}) as cur:
						#send to each role
						for roleid in roleids:
							result=DBHelp.InsertRoleMail(cur,roleid,get['title'],get['sender'],get['content'],0,{6:mail_item,1:mail_wealth[0],4:mail_wealth[3],5:mail_wealth[2],2:mail_wealth[1],3:mail_wealth[4]})
							log.append((roleid, result))
				from ThirdLib import PrintHelp
				data['log']=repr(log)
				from Integration.WebPage.User import Permission
				Permission.monitor(R,data['log'],"/role/sendMail",True)
				data['tips']="邮件已经成功发送！"
			except:
				traceback.print_exc()
				data['tips']="邮件发送失败！请重新发送！"
		else:
			data['tips']="请先完整填写邮件！"
			
	#get common param
	from Integration import AutoHTML
	from Integration.Help import ConfigHelp
	data['servers']=AutoHTML.ToDataBase()
	data['items']=ConfigHelp.GetPropName()
	items_json=[]
	for k,v in data['items'].items():
		items_json.append("%s/%s"%(v,k))
	data['items_json']=json.dumps(items_json)
	return data