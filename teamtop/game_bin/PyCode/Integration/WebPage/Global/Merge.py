#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 合服
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Util import OutBuf
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.Global import Add

html = '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>合并区</title>
</head>
<body>
%s
<form action="%s" method="GET" target="_blank">
主区: <input type="text" name="main_zone" value=""><br>
合区: <input type="text" name="merge_zones" value=""><br>
<input type="submit" name="提交" />
</form>
</body>
</html>'''

def Reg(request):
	'''【配置】--合并游戏区'''
	cp = '''<iframe  src='%s'  style="width:100%%;height:50px""  frameborder="0" marginwidth="0" marginheight="0"></iframe><br><hr>'''%AutoHTML.GetURL(Add.CopyTmpConfig)
	return HttpResponse(html % (cp, AutoHTML.GetURL(Res)))

def Res(request):
	#主区ID
	main_zone_id = AutoHTML.AsInt(request.GET, "main_zone")
	#被融合的区ID列表，用空格分隔
	be_merge_zone_ids = [int(i) for i in AutoHTML.AsString(request.GET, "merge_zones").split(" ") if i.isdigit()]
	#附加融合的区
	extend_be_merge_zone_ids = []
	#需要删除的合区GHL进程数据
	delete_ghl_processs = []
	#需要更新的DB进程数据
	update_d_processs = []
	
	with OutBuf.OutBuf_NoExcept() as O:
		#合区ID列表要非空且唯一
		assert be_merge_zone_ids
		assert len(be_merge_zone_ids) == len(set(be_merge_zone_ids))
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("select ztype, be_merge_zid, merge_zids, ghl_process_key, public_ip from zone_tmp where zid = %s;" % main_zone_id)
			result = cur.fetchall()
			# 确保主区是标准进程区且未被合区
			assert result[0][0] == "Standard"
			assert result[0][1] == 0
			#主区已经融合过的区ID列表
			main_merge_zone_ids = eval(result[0][2])
			main_ghl_process_key = result[0][3]
			main_public_ip = result[0][4]
			for be_merge_zone_id in be_merge_zone_ids:
				# 确保区ID大小
				assert be_merge_zone_id > main_zone_id
				# 确保没重复合区
				assert be_merge_zone_id not in main_merge_zone_ids
				cur.execute("select ztype, be_merge_zid, merge_zids, ghl_process_key, d_process_key from zone_tmp where zid = %s;" % be_merge_zone_id)
				merge_result = cur.fetchall()
				# 确保被合区未被合过
				assert merge_result[0][0] == "Standard"
				assert merge_result[0][1] == 0
				delete_ghl_processs.append(merge_result[0][3])
				update_d_processs.append(merge_result[0][4])
				# 确保拓展的区没重复合并
				for extend_merge_zone_id in eval(merge_result[0][2]):
					assert extend_merge_zone_id != main_zone_id
					assert extend_merge_zone_id not in be_merge_zone_ids
					assert extend_merge_zone_id not in extend_be_merge_zone_ids
					cur.execute("select ztype, be_merge_zid, d_process_key from zone_tmp where zid = %s;" % extend_merge_zone_id)
					# 确保被合区和拓展被合区关系对应
					extend_result = cur.fetchall()
					assert extend_result[0][0] == "Standard"
					assert extend_result[0][1] == be_merge_zone_id
					# 确认OK
					extend_be_merge_zone_ids.append(extend_merge_zone_id)
					update_d_processs.append(extend_result[0][2])
			# 修正数据
			for be_merge_zone_id in be_merge_zone_ids:
				assert cur.execute("update zone_tmp set be_merge_zid = %s, merge_zids = %s, public_ip = %s, be_merge_cnt = be_merge_cnt + 1 where zid = %s;", (main_zone_id, repr([]), main_public_ip, be_merge_zone_id))
				main_merge_zone_ids.append(be_merge_zone_id)
			for extend_merge_zone_id in extend_be_merge_zone_ids:
				assert cur.execute("update zone_tmp set be_merge_zid = %s, merge_zids = %s, public_ip = %s, be_merge_cnt = be_merge_cnt + 1 where zid = %s;", (main_zone_id, repr([]), main_public_ip, extend_merge_zone_id))
				main_merge_zone_ids.append(extend_merge_zone_id)
			# 修改进程信息
			cur.execute("select computer_name from process_tmp where pkey = %s;", main_ghl_process_key)
			mani_computer_name = cur.fetchall()[0][0]
			for ghl_key in delete_ghl_processs:
				assert cur.execute("delete from process_tmp where pkey = %s;", ghl_key)
			for d_key in update_d_processs:
				assert cur.execute("update process_tmp set work_zid = %s, computer_name = %s where pkey = %s;", (main_zone_id, mani_computer_name, d_key))
			# 写入主区信息
			assert cur.execute("update zone_tmp set merge_zids = %s where zid = %s;", (repr(main_merge_zone_ids), main_zone_id))
			print "%s merge %s" % (main_zone_id, repr(be_merge_zone_ids))
	return HttpResponse(AutoHTML.PyStringToHtml(O.get_value()))


Permission.reg_develop(Reg)
Permission.reg_develop(Res)
