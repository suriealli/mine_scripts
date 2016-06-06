# -*- coding:UTF-8 -*-
import time,traceback
import me,tool,memory,user,model,body
def add():
	if not user.inGroup("operate"):return user.ban()
	if 'content' in me.S['P']:
		me.S['P']['content']=me.S['P']['content'].strip()
		me.S['P']['sender']=me.S['user']['name']
		#interval time
		if "interval_time" in me.S['P'] and me.S['P']["interval_time"]!="":
			me.S['P']["interval_time"]=int(me.S['P']["interval_time"])
		else:
			me.S['P']["interval_time"]=0
	done=model.add()
	if 'id' in done and done['id']>0:
		#send to server
		temp=send(done['id'])
		done['tips']+=temp['tips']
	return done
def edit():
	if not user.inGroup("operate"):return user.ban()
	return model.edit()
def guide():
	if not user.inGroup("operate"):return user.ban()
	data={}
	try:
		data=model.guide({"option":{"order":"end_time,desc"},"filter":'game="%s" and `operator`=%s'%(me.S['A']["game"],me.S['A']['operator'])})
	except:
		traceback.print_exc()
		print me.S['A']['game'],me.S['A']['operator']
	return data
	
def send(nid):
	data={}
	msg=memory.get("recall",{"model":"notice","one":True,"filter":{"nid":nid}})
	import time
	msg['now_time']=int(time.time())
	data=me.post('notice/send',msg)
	memory.get("remember",{"action":"edit","model":"notice","data":{"track":"%s%s"%(msg.get('track',""),data['track'])},"filter":{"nid":nid}})
	return data

def loop():
	import time,math
	now_time=int(time.time())
	from_time=now_time-60 #从哪个时间开始计算公告
	temp=memory.get("recall",{"field":"game,operator,nid,server,content,UNIX_TIMESTAMP(end_time) as endtime,UNIX_TIMESTAMP(start_time) as starttime,interval_time,track","model":"notice","filter":"interval_time>0 and UNIX_TIMESTAMP(end_time)>%s"%from_time})
	for v in temp:
		times=int(math.floor((from_time-v['starttime'])/v['interval_time'])+1)
		#times
		#print times,'james'
		left=(from_time-v['starttime'])%v['interval_time']
		if v['interval_time']-left>60 or v['track'].find("/%s,"%(times))>=0:
			continue
		#send
		me.S['user']={"name":"robot"}
		me.S['A']['game']=v['game']
		me.S['A']['operator']=v['operator']
		send(v['nid'])
	return {"response":""}
		