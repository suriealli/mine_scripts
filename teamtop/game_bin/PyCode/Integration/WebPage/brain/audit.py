# -*- coding:UTF-8 -*-
import os,sys,time,traceback
import server,game,operators,me,tool,memory,user,model
def get():
	import tool
	data={}
	#for robot
	import log
	if 'user' not in me.S:
		if me.S['A']['host']=="ly.app100718848.twsapp.com:8008" and me.S['G'].get('key','')=="follow-my-own-soul":
			log.add('robot action from %s;'%(me.S['A']['ip']))
			me.S['user']={"name":'james','group':"host,operate,common"}
	if not user.inGroup('host'):
		log.add('No permission to report audit;')
		return user.ban()
	data['models']=['item','consume','order','loginlog','online','account','user','loginloss','reglog','ulist']
	me.S['G']['date_start']=me.S['G'].get('date_start',tool.date(time.time()))
	me.S['G']['date_end']=me.S['G'].get('date_end',tool.date(time.time()))
	if 'game' in me.S['G']:
		me.S['G']['step']=me.S['G'].get('step',"report")#默认为生成报告
		me.S['G']['target']=me.S['G'].get('target','file')
		me.S['A']['game']=me.S['G']['game']
		me.S['A']['operator']=me.S['G']['operator']
		#models
		models=me.S['G'].get('model')
		if models=="all":
			models=data['models']
		else:
			models=[models]
		#act
		dates=tool.getDateRange(me.S['G']['date_start'],me.S['G']['date_end'])
		#absolute path
		ABSPATH=os.path.abspath(os.path.dirname(__file__))
		#parallel msg
		mmsg=[]
		log_path=ABSPATH.replace('brain','file%saudit%s%s%s'%(os.sep,os.sep,me.S['G']['game'],os.sep))
		if me.S['G']['step']=="report":
			print "report dates range:",dates
			for vvv in dates:
				#games
				try:
					if not os.path.isdir('%s%s'%(log_path,vvv)):
						print 'crated path:%s%s'%(log_path,vvv)
						os.makedirs('%s%s'%(log_path,vvv))
				except:
					#print 'Cannot Create Dir %s'%log_path
					#traceback.print_exc()
					pass
				for vv in models:
					mmsg.append((me.S['G']['operator'],me.S['G']['game'],vv,vvv))
			for v in mmsg:
				print "report:",v
				report(v)
		elif me.S['G']['step']=="upload":
			#file
			for vvv in dates:
				#games
				#tar file
				import tarfile
				#压缩，创建tar.gz包
				#创建压缩包名
				now_path="%s%s"%(log_path,vvv)
				initPath = os.getcwd()
				os.chdir(now_path)
				tar_name="%s%s%s_%s.tar.gz"%(now_path,os.sep,me.S['G']['game'],vvv.replace('-',''))
				#print '【tar files】%s'%tar_name
				try:
					tar = tarfile.open(tar_name,"w:gz")
					#创建压缩包
					files=os.listdir(now_path)
					for file in files:
						try:
							if os.path.getsize(file)==0:
								continue
						except:
							pass
						tar.add(file)
					tar.close()
					#to ftp
					if me.S['G']['target']=="ftp":
						ftp_config={
							"shanhai":{
								"user":"user_shcs",
								"key":"]DO3)2tnR]qv"
							},
							"longqi":{
								"user":"user_lqs",
								"key":"zlg-p$!yYAZl"
							}
						}
						game_config=ftp_config[me.S['G']['game']]
						cmd="lftp -u %s,'%s' tjftp.3737.com:38000 -e 'mput %s; quit'"%(game_config['user'],game_config['key'],tar_name)
						os.system(cmd)
				except:
					traceback.print_exc()
					pass
				os.chdir(initPath)
	return data
#models
def report(msg):
	data={}
	if not msg:msg={}
	if not msg[0] or not msg[1] or not msg[2]:
		print msg
		return
	servers={}
	servers=server.getAll({"operator":msg[0],"game":msg[1]})
	
	mmsg=[]
	#single
	if me.S['G'].get("parallel","")=="":
		for k,v in servers.items():
			reportServer(({"server":k,"server_name":v['value'],"action":"report","operator":msg[0],"game":msg[1],"audit_model":msg[2],"audit_date":msg[3]}))
	else:
		print "Parallel report Audit:"
		for k,v in servers.items():
			mmsg.append(({"server":k,"server_name":v['value'],"action":"report","operator":msg[0],"game":msg[1],"audit_model":msg[2],"audit_date":msg[3]}))
		data=model.parallel(reportServer,mmsg)

def reportServer(msg):
	data={}
	game_index={"longqi":7,"shanhai":2}
	try:
		data=game.act(msg[0])
	except:
		traceback.print_exc()
		pass
	try:
		#print 'report server %s'%msg[1]['game']
		data=export(data,msg[0])
		#创建目录
		#absolute path
		ABSPATH=os.path.abspath(os.path.dirname(__file__))
		log_path=ABSPATH.replace('brain','file%saudit%s%s%s%s'%(os.sep,os.sep,msg[0]['game'],os.sep,msg[0]['audit_date']))
		#创建文件
		code=open('%s%s%s___%s___%s___%s___%s___1.txt'%(log_path,os.sep,msg[0]['operator'],game_index[msg[0]['game']],msg[0]['server'],msg[0]['audit_model'],msg[0]['audit_date'].replace('-','')), "w")
		try:
			code.write(data)
		except:
			pass
		code.close()
		data=1
	except:
		data=0
		#print 'reportServer %s ERROR'%(msg[1]['server'])
		#traceback.print_exc()
		pass
	return data
			
def export(D,msg=None):
	data=[]
	if not D:
		return
	i=1
	for v in D:
		content=''
		for vv in v:	
			if ('%s'%vv).strip()=="":
				vv="^A"
			elif vv==0:
				vv="-1"
			content+='\t%s'%(('%s'%vv).replace('\t',''))
		try:
			v='%s%s'%(i,content)
		except:
			v=''
			print msg['server_name']
			pass
		i+=1
		data.append(v)
	data='\r\n'.join(data)
	return data
