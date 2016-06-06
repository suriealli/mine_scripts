#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DeepHell.DeepHellDefine")
#===============================================================================
# 深渊炼狱 Define
#===============================================================================
#深渊炼狱 等级限制
DeepHell_NeedLevel = 100
#开服天数限制						
DeepHell_NeedKaiFuDay = 10						
	

#活动持续时间秒
DeepHell_ActiveSeconds = 2520 								
#跨服迟秒
DeepHell_RealStartDelaySec = 600

	
#本服去跨服的中转场景点
DeepHell_TempSceneId = 85
DeepHell_TempPos_X = 958
DeepHell_TempPos_Y = 579


#房间号场景ID {roomId:[sceneid,],}
DeepHell_SceneConfig_Dict = {
								1:[724,725,726,727,728,729,730,731,732,733],
								2:[734,735,736,737,738,739,740,741,742,743],
								3:[744,745,746,747,748,749,750,751,752,753],
								4:[754,755,756,757,758,759,760,761,762,763],
								5:[764,765,766,767,768,769,770,771,772,773],
								6:[774,775,776,777,778,779,780,781,782,783],
								7:[784,785,786,787,788,789,790,791,792,793],
								8:[794,795,796,797,798,799,800,801,802,803],
								9:[804,805,806,807,808,809,810,811,812,813],
								10:[814,815,816,817,818,819,820,821,822,823],
								11:[824,825,826,827,828,829,830,831,832,833],
								12:[834,835,836,837,838,839,840,841,842,843],
								13:[844,845,846,847,848,849,850,851,852,853],
								14:[854,855,856,857,858,859,860,861,862,863],
								15:[864,865,866,867,868,869,870,871,872,873],
								16:[874,875,876,877,878,879,880,881,882,883],
								17:[884,885,886,887,888,889,890,891,892,893],
								18:[894,895,896,897,898,899,900,901,902,903],
								19:[904,905,906,907,908,909,910,911,912,913],
								20:[914,915,916,917,918,919,920,921,922,923],
								21:[924,925,926,927,928,929,930,931,932,933],
								22:[934,935,936,937,938,939,940,941,942,943],
								23:[944,945,946,947,948,949,950,951,952,953],
								24:[954,955,956,957,958,959,960,961,962,963],
								25:[964,965,966,967,968,969,970,971,972,973],
								26:[974,975,976,977,978,979,980,981,982,983],
								27:[984,985,986,987,988,989,990,991,992,993],
								28:[994,995,996,997,998,999,1000,1001,1002,1003],
								29:[1004,1005,1006,1007,1008,1009,1010,1011,1012,1013],
								30:[1014,1015,1016,1017,1018,1019,1020,1021,1022,1023]
							}
	
	
#战斗类型
DeepHell_FightType_PVP = 177
DeepHell_FightType_PVE = 178
	
	
#NPC数据字典key
IDX_ROOM_ID = 1
IDX_FLOOR_INDEX = 2
IDX_IN_FIGHT = 3
IDX_MONSTER_INFO = 4
IDX_MONSTER_INDEX = 5
IDX_MONSTER_SCENEID = 6
IDX_MASTER_FIGHTDATA = 7
IDX_MASTER_ROLENAME = 8
	
	
#默认塔层
DEFAULT_FLOOR = 1

#同步房间数据间隔
Sync_RoomData_Interval = 60

#炼狱者对象状态
STATE_UNDEFINE = 0
STATE_ONLINE = 1
STATE_OFFLINE = 2 
STATE_FIGHT = 4
STATE_WAITCHOICE = 8

#初始保护CD
DeepHell_ProtectCD_Init = 10
#保护CD
DeepHell_ProtectCD_Nomal = 10
#战斗CD
DeepHell_FightCD = 20
	
#中转延迟秒
REVIVE_DELAY = 5

#积分排行榜大小
DeepHell_ScoreRankSize = 20

#活动结束 踢出玩家延迟秒
DeepHell_KickOut_Delay = 60

#怪物阵营
DeepHeel_MCID = 18093

#增伤buff需要连续被击杀数
DeepHell_Buff_NeedBeKillCnt = 5
DeepHell_Buff_DamageUpgradeRate = 5
DeepHell_Buff_DamageReduceRate = 0.9

#英魂掉落击杀数限制
DeepHell_DropSoul_NeedCnt = 3 
DeepHell_RumorKill = 5

#英魂NPC类型
DeepHell_NPCSoulType = 22010

#战败等待复活选项
DeepHell_AfterPVPFailWaitSec = 15

#不保层复活
DeepHell_ReviewChoice_No = 0
#保层复活
DeepHell_ReviewChoice_Yes = 1

#复活选项最低塔层
DeepHell_ReviewTips_MinFloor = 2

#复活跨服币
ProtectReview_NeedRMB = 10