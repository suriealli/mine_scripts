#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionDefine")
#===============================================================================
# 公会定义
#===============================================================================

UNION_NEED_LEVEL = 32		#公会需求等级
UNION_NAME_LEN_MAX = 18		#最大公会名字长度
UNION_STATION_SCENE_ID = 372#公会驻地场景ID

#职位ID
LEADER_JOB_ID = 1			#团长职位ID
MEMBER_JOB_ID = 5			#成员职位ID

#军团成员数据索引ID
M_NAME_IDX = 1				#名字
M_LEVEL_IDX = 2				#等级
M_JOB_IDX = 3				#职位
M_CONTRIBUTION_IDX = 4		#贡献
M_ONLINE_IDX = 5			#在线
M_OFFLINE_TIME_IDX = 6		#离线时间
M_PICTURE_IDX = 7			#头像(性别，职业，进阶)
M_VIP_IDX = 8				#VIP
M_ZDL_IDX = 9				#战斗力
M_H_CONTRIBUTION_IDX = 10	#历史贡献
M_TASK_HELP_IDX = 11		#助人次数

#选举
ELECTION_START_IDX = 1		#选举是否开始(0:未开始 1:开始)
ELECTION_JOIN_IDX = 2		#参与选举的roleId列表
ELECTION_ROLE_VOTES_IDX = 3	#选举角色票数

#夺宝
TREASURE_GOLD_IDX = 1		#金宝箱开启字典roleId->roleName
TREASURE_SILVER_IDX = 2		#银宝箱开启字典roleId->roleName
TREASURE_COPPER_IDX = 3		#铜宝箱开启字典roleId->roleName

#魔神
GOD_TOP_IDX = 1				#最高挑战魔神(godId, roleId, roleName, sex, career, grade)
GOD_TODAY_PASS_LIST_IDX = 2	#魔神今日通关列表
GOD_DAYS_IDX = 3			#保存一个天数，用来做每日清理
GOD_FIGHT_IDX = 4			#记录公会魔神击杀次数，godId->次数
#公会副本
FB_CHAPTER_IDX = 1		#章节索引

#OtherData枚举
O_Building = 1					#公会建筑字典BuildingId-->建筑等级
O_ShenShouId = 2				#当前神兽ID
O_ShenShouGrowthValue = 3		#神兽成长值
O_ShenShouCalledTimes = 4		#当日已经召唤过神兽的次数
O_ShenShouIdCalled = 5			#当前被召唤出的神兽的id
O_ShenShouHurt = 6				#挑战神兽伤害roleID-->(roleName,伤害值)
O_ShenShouFeedLog = 7			#公会神兽喂养记录(roleID, 成长值)
O_UnionSkillProgress = 8		#公会技能研究进度skillId-->{'level':技能等级,'time':开始研究的时间戳,'process':当前等级研究的进度值,'enable':是否研究满值}
O_UnionSillResearching = 9		#当前处在研究状态的技能
O_StoreGoods = 10				#公会商店已经激活的商品id  set([goodId])
O_ShenShouGoods = 11			#公会神兽击杀掉落物品goodId-->掉落数量 
O_TASK_IDX = 12					#公会任务
O_TASK_HELP_OTHER_LIST_IDX = 13	#记录公会任务帮助别人的列表
O_PRISONER_IDX = 14				#记录公会战俘数据
O_PRISONER_RESOURCE_IDX = 15	#记录战俘生产的可以领取的公会资源
O_SUPER_CARDS_DAYS_IDX = 16		#至尊周卡角色ID对应周卡时间
O_TotalFillRMB = 17				#公会每日累计充值数
O_ShenShowDayFeed = 18			#神兽每日喂养次数
O_DailyResource = 19			#公会资源每日增加数
O_DailyResourceLackDays = 20	#公会资源每日增加数连续不达标天数
O_HongBao = 21					#公会红包数据# { 'allHongBao': { 红包id: ( 角色名, [红包随机列表], [红包领取的角色名], [玩家Id列表], 红包是否可以领取(1-红包可领取, 0-不可领取) ) },
								#			'HongBaoId': 红包分配id
								#			'recordList':[(玩家名，祝福语),(领红包玩家名字，发红包玩家名字，金额)]
								#			'outDateTime':{红包id:(发红包角色id, 红包过期时间)}
								#			}
#公会建筑类型枚举 
BuildingT_MagicTower = 1		#魔法塔
BuildingT_ShenShouTan = 2		#神兽坛
BuildingT_Store = 3				#商店

#公会任务
TASK_ID_IDX = -1		#任务ID
TASK_HELP_ME_IDX = -2	#保存帮助提星的角色ID
TASK_STAR_IDX = 0		#任务星级
TASK_MONSTER_1 = 1		#任务怪物1状态
TASK_MONSTER_2 = 2		#任务怪物2状态


