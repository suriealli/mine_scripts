# -*- coding: utf-8 -*-
import traceback,time
import me,model,memory,user,tool,server,body
def check():
	if not user.inGroup("operate"):return user.ban()
	data=tool.Dict()
	if 'game' not in me.S['A'] or me.S['A']['game']==0:
		return {"tips":"请先选择游戏！"}
	#server
	all_server=server.getAll()
	#statistics
	statistics=getStatistics()
	#get msg
	me.S['P']['server']=me.S['P'].get('server','0')
	me.S['P']['servers']=me.S['P'].getlist('servers')
	me.S['P']['statistic']=me.S['P'].getlist('statistic')
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['no_group']=me.S['P'].get('no_group','')
	me.S['P']['server_view']=me.S['P'].get('server_view','')
	
	#servers
	servers=[me.S['P']['server']]
	if me.S['P']['server']=="5201314":
		if len(me.S['P']['servers'])>0:
			servers=me.S['P']['servers']
		else:
			servers=all_server.keys()
	#statistic
	tips=[]
	if len(me.S['P']['statistic'])>0 and me.S['P']['statistic']!=[""]:
		#dates
		dates=[]
		if me.S['P']['no_group']=="true":
			dates=['%s~%s'%(me.S['P']['date_start'],me.S['P']['date_end'])]
		else:
			dates=tool.getDateRange(me.S['P']['date_start'],me.S['P']['date_end'])
		import collections
		#server_view
		if me.S['P']['server_view']!="":
			for single_statistic in me.S['P']['statistic']:
				if not single_statistic in data:
					data[single_statistic]=tool.Dict()
				data[single_statistic]["0"]=tool.Dict()
				for dk in dates:
					data[single_statistic]["0"][dk]=dk
				for single_server in servers:
					single_server=int(single_server)
					data[single_statistic][single_server]=tool.Dict()
					#add dates
					for dk in dates:
						data[single_statistic][single_server][dk]=0
					#get memory
					t=getStatisticMemory([single_server],statistics[single_statistic])
					for v in t:
						for vv in t:
							tips.append(v[1])
							for value in v[0]:
								try:
									key=value["spliter"]
								except:
									traceback.print_exc()
									print value
								data[single_statistic][int(value['server'])][key]=value[single_statistic]
		else:
			#common view
			for single_statistic in me.S['P']['statistic']:
				#set keys
				if not single_statistic in data:
					data[single_statistic]=collections.OrderedDict()
					#add server
					data[single_statistic]['servers']=collections.OrderedDict()
					for sk in servers:
						sk=int(sk)
						if int(sk)==0:
							data[single_statistic]['servers'][sk]="全区汇总"
							continue
						data[single_statistic]['servers'][sk]=all_server.get(sk,{"value":sk})['value']
					#add dates
					for dk in dates:
						data[single_statistic][dk]=collections.OrderedDict()
						#all servers in this date,set default 0
						for sk in servers:
							sk=int(sk)
							data[single_statistic][dk][sk]=0
				t=getStatisticMemory(servers,statistics[single_statistic])
				for v in t:
					for vv in v:
						tips.append(v[1])
						for value in v[0]:
							if me.S['P']['no_group']=="true":
								key=dates[0]
							else:
								try:
									key=value["spliter"]
								except:
									traceback.print_exc()
									print v
							data[single_statistic][key][int(value['server'])]=value[single_statistic]
	tips='<br />'.join(tips)
	return {"data":data,"servers":all_server,"statistics":statistics,"tips":tips}
#查看各项数据记录
def getStatisticMemory(servers,statistic):
	#memory
	temp=tool.copy(statistic['property'])
	temp['field']+=',date_format(%s,"%%Y-%%m-%%d") as spliter'%(temp['spliter'])
	if 'filter' not in temp:
		temp['filter']=''
	else:
		temp['filter']+=" and "
	temp["filter"]+='date_format(%s,"%%Y-%%m-%%d") between "%s" and "%s"'%(temp["spliter"],me.S['P']['date_start'],me.S['P']['date_end'])
	if 'option' not in temp:
		temp['option']={}
	if 'order' not in temp['option']:
		temp["option"]={"order":"spliter,asc"}
	if me.S['P']['no_group']!="true" and 'join' not in temp and 'group' not in temp['option']:
		temp["option"]["group"]="spliter"
	temp['track']="return"
	#each server
	msg=[]
	t=[]
	for single_server in servers:
		mmsg=tool.copy(temp)
		mmsg['field']+=',"%s" as server'%single_server
		mmsg['memory']="server:%s"%single_server
		t.append(memory.get('recall',mmsg))
		#msg.append(("recall",mmsg))
	#temp=model.parallel(memory.getParallel,msg)
	return t
def getStatistics():
	#all statistics
	temp=memory.get("recall",{"model":"statistic","key":"byname","filter":{"game":me.S['A']['game']}})
	import tool
	for k,v in temp.items():
		v['property']=eval(tool.filterJSON(v['property']))
	return temp