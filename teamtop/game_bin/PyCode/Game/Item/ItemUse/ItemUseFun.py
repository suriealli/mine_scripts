#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.ItemUseFun")
#===============================================================================
# 物品使用
#===============================================================================
import Environment
from Game.Item.ItemUse import ItemUserClass

#坐骑食物(1为配置表中对应的食物ID)
MountFood1 = ItemUserClass.MountFood(25601, 1)
MountFood2 = ItemUserClass.MountFood(25602, 2)
MountFood3 = ItemUserClass.MountFood(25603, 3)
MountFood4 = ItemUserClass.MountFood(25604, 4)
MountFood5 = ItemUserClass.MountFood(25605, 5)
MountFood6 = ItemUserClass.MountFood(25606, 6)
MountFood7 = ItemUserClass.MountFood(25607, 7)
MountFood8 = ItemUserClass.MountFood(25608, 8)
MountFood9 = ItemUserClass.MountFood(25609, 9)
MountFood10 = ItemUserClass.MountFood(25610, 10)
MountFood11 = ItemUserClass.MountFood(25611, 11)
MountFood12 = ItemUserClass.MountFood(25612, 12)
MountFood13 = ItemUserClass.MountFood(25613, 13)
MountFood14 = ItemUserClass.MountFood(25614, 14)
MountFood15 = ItemUserClass.MountFood(25615, 15)
MountFood16 = ItemUserClass.MountFood(25616, 16)
MountFood17 = ItemUserClass.MountFood(25617, 17)
MountFood18 = ItemUserClass.MountFood(25618, 18)
MountFood19 = ItemUserClass.MountFood(25619, 19)
MountFood20 = ItemUserClass.MountFood(25620, 20)
MountFood21 = ItemUserClass.MountFood(25621, 21)
MountFood22 = ItemUserClass.MountFood(25622, 22)
MountFood23 = ItemUserClass.MountFood(25623, 23)
MountFood24 = ItemUserClass.MountFood(25624, 24)
MountFood25 = ItemUserClass.MountFood(25625, 25)
MountFood26 = ItemUserClass.MountFood(25626, 26)
MountFood27 = ItemUserClass.MountFood(25627, 27)
MountFood28 = ItemUserClass.MountFood(25628, 28)
MountFood29 = ItemUserClass.MountFood(25629, 29)
MountFood30 = ItemUserClass.MountFood(25630, 30)
MountFood31 = ItemUserClass.MountFood(25631, 31)
MountFood32 = ItemUserClass.MountFood(25632, 32)
MountFood33 = ItemUserClass.MountFood(25633, 33)
MountFood34 = ItemUserClass.MountFood(25634, 34)
MountFood35 = ItemUserClass.MountFood(25635, 35)

#首充羽翼礼盒
WingLiBao =  ItemUserClass.WingLiBao(25835, 37009)
WingLiBao1 = ItemUserClass.WingLiBao(26985, 37011)
WingLiBao2 = ItemUserClass.WingLiBao(27068, 37014)#北美用
WingLiBao3 = ItemUserClass.WingLiBao(29489, 37003)#国内联运
#太阳神英雄礼包
HeroLiBao =  ItemUserClass.HeroLiBao(26120, [92, 92])
#紫色圣光祭祀英雄礼包
HeroLiBao =  ItemUserClass.HeroLiBao(26652, [24])
#紫色红袍女巫英雄礼包
HeroLiBao =  ItemUserClass.HeroLiBao(26653, [39])
#紫色众神之王礼包
HeroLiBao =  ItemUserClass.HeroLiBao(27077, [59])
#神天空射手礼包
HeroLiBao = ItemUserClass.HeroLiBao(27527, [81])
#神冠军骑士礼包
HeroLiBao = ItemUserClass.HeroLiBao(27528, [145])
#紫色太阳神礼包
HeroLiBao = ItemUserClass.HeroLiBao(27529, [92])

#龙晶礼包[ 1-39 40 -59 60-79 80 -99 100 -119]
#LJ = ItemUserClass.LongJingLiBao(25601, [(25601, 100), (25601, 100), (25601, 100), (25601, 100), (25601, 100)])

#矮人礼包(礼包coding, (必出物品, 必出数量), [(随机物品概率， 物品coding, 数量)], (神石最小值, 神石最大值), [(随机金币概率， 金币数量)])
AR = ItemUserClass.AiRenLiBao(26154, (25970, 1), [(3333, 26157, 1), (3333, 26157, 2), (3333, 26157, 3)], (20, 40), [(200, 50000), (400, 60000), \
									(600, 70000), (800, 80000), (1200, 90000), (1600, 100000), (2000, 110000), (1600, 120000), (1200, 130000), \
									(800, 140000), (600, 150000), (400, 160000), (200, 170000), (200, 180000), (100, 190000), (100, 200000)])

#死灵飞龙礼包(礼包coding, (必出物品, 必出数量), [(随机物品概率， 物品coding, 数量)], (神石最小值, 神石最大值), [(随机金币概率， 金币数量)])
AP = ItemUserClass.AiRenLiBao(29098, (27566, 1), [(5000, 29097, 2), (5000, 29097, 4)], (10, 30), [(200, 50000), (400, 60000), \
									(600, 70000), (800, 80000), (1200, 90000), (1600, 100000), (2000, 110000), (1600, 120000), (1200, 130000), \
									(800, 140000), (600, 150000), (400, 160000), (200, 170000), (200, 180000), (100, 190000), (100, 200000)])	
#绯红飞鹿礼包(礼包coding, (必出物品, 必出数量), [(随机物品概率， 物品coding, 数量)], (神石最小值, 神石最大值), [(随机金币概率， 金币数量)])
AQ = ItemUserClass.AiRenLiBao(29269, (27566, 1), [(5000, 29270, 2), (5000, 29270, 3), (5000, 29270, 4)], (10, 30), [(200, 50000), (400, 60000), \
									(600, 70000), (800, 80000), (1200, 90000), (1600, 100000), (2000, 110000), (1600, 120000), (1200, 130000), \
									(800, 140000), (600, 150000), (400, 160000), (200, 170000), (200, 180000), (100, 190000), (100, 200000)])										
AS = ItemUserClass.AiRenLiBao(29412, (27566, 1), [(1000, 29411, 1), (1000, 29411, 2), (1000, 29411, 3)], (10, 30), [(200, 50000), (400, 60000), \
									(600, 70000), (800, 80000), (1200, 90000), (1600, 100000), (2000, 110000), (1600, 120000), (1200, 130000), \
									(800, 140000), (600, 150000), (400, 160000), (200, 170000), (200, 180000), (100, 190000), (100, 200000)])

#世界杯礼包[ 1-39 40 -59 60-79 80 -99 100 -119]
#IW = ItemUserClass.WorldCupLevelLiBao(26154, [[(25601, 1, 1000), (25601, 2, 1000)], \
											#[(25601, 1, 1000), (25601, 2, 1000)],\
											#[(25601, 1, 1000), (25601, 2, 1000)],\
											#[(25601, 1, 1000), (25601, 2, 1000)],\
											#[(25601, 1, 1000), (25601, 2, 1000)]])
#世界杯淘汰赛神石竞猜胜利宝箱[ 1-39 40 -59 60-79 80 -99 100 -119]
TSS = ItemUserClass.WorldCupLevelLiBao(26257, [[(26224,1,1000),(25600,15,2500),(25600,18,2500),(25600,20,2500),(25656,1,1500)] ,\
											[(26224,1,1000),(25600,15,2000),(25600,18,2000),(25600,20,2000),(25657,1,1500),(26042,1,1500)],\
											[(25831,15,1000),(25970,15,1000),(26043,15,1000),(26224,1,1000),(26144,15,2000),(25837,15,2000),(26227,1,1500),(26228,1,500)],\
											[(25831,15,1000),(25970,15,1000),(26043,15,1000),(26224,1,1000),(26144,15,2000),(25837,15,2000),(26227,1,1500),(26228,1,500)],\
											[(25831,15,1000),(25970,15,1000),(26043,15,1000),(26224,1,1000),(26144,15,2000),(25837,15,2000),(26227,1,1500),(26228,1,500)]])
#世界杯淘汰赛神石竞猜失败宝箱
TSF = ItemUserClass.WorldCupLevelLiBao(26258, [[(26223,1,4500),(25600,15,1500),(25600,18,1500),(25600,20,1500),(25656,1,1000)], \
                                            [(26223,1,4500),(25600,15,1500),(25600,18,1000),(25600,20,1000),(25657,1,1000),(26042,1,1000)],\
                                            [(25831,10,1300),(25970,10,1300),(26043,10,1300),(26223,1,2500),(26144,10,1300),(25837,10,1300),(26227,1,1000)],\
                                            [(25831,10,1300),(25970,10,1300),(26043,10,1300),(26223,1,2500),(26144,10,1300),(25837,10,1300),(26227,1,1000)],\
                                            [(25831,10,1300),(25970,10,1300),(26043,10,1300),(26223,1,2500),(26144,10,1300),(25837,10,1300),(26227,1,1000)]])
#世界杯淘汰赛金币竞猜胜利宝箱
TJS = ItemUserClass.WorldCupLevelLiBao(26259, [[(25671,5,1500),(25681,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,2500),(26033,1,1000),(26044,1,500)], \
                                            [(25671,5,1500),(25682,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,2500),(26033,1,1000),(26044,1,500)],\
                                            [(26144,2,1000),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,2,1000),(26032,1,1450),(26033,1,600),(26044,1,250),(26266,1,1150),(26119,1,400),(26267,1,150)],\
                                            [(26144,2,1000),(25673,5,1000),(25684,20,1000),(25663,10,1000),(25668,10,1000),(25837,1,1000),(26032,1,1450),(26033,1,600),(26044,1,250),(26266,1,1150),(26119,1,400),(26267,1,150)],\
                                            [(26144,2,1000),(25673,5,1000),(25684,20,1000),(25663,10,1000),(25668,10,1000),(25837,1,1000),(26032,1,1450),(26033,1,600),(26044,1,250),(26266,1,1150),(26119,1,400),(26267,1,150)]])
#世界杯淘汰赛金币竞猜失败宝箱
TJF = ItemUserClass.WorldCupLevelLiBao(26260, [[(25671,5,1500),(25681,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,3000),(26033,1,1000)], \
                                            [(25671,5,1500),(25682,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,3000),(26033,1,1000)],\
                                            [(26144,1,1100),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,1,1100),(26032,1,1550),(26033,1,650),(26266,1,1150),(26119,1,450)],\
                                            [(26144,1,1100),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,1,1100),(26032,1,1550),(26033,1,650),(26266,1,1150),(26119,1,450)],\
                                            [(26144,1,1100),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,1,1100),(26032,1,1550),(26033,1,650),(26266,1,1150),(26119,1,450)]])
#世界杯冠军神石竞猜胜利宝箱[ 1-39 40 -59 60-79 80 -99 100 -119]
GSS = ItemUserClass.WorldCupLevelLiBao(26261, [[(26224,1,1000),(25600,15,2500),(25600,18,2500),(25600,20,2500),(25656,1,1500)] ,\
											[(26224,1,1000),(25600,15,2000),(25600,18,2000),(25600,20,2000),(25657,1,1500),(26042,1,1500)],\
											[(25831,15,1000),(25970,15,1000),(26043,15,1000),(26224,1,1000),(26144,15,2000),(25837,15,2000),(26227,1,1500),(26228,1,500)],\
											[(25831,15,1000),(25970,15,1000),(26043,15,1000),(26224,1,1000),(26144,15,2000),(25837,15,2000),(26227,1,1500),(26228,1,500)],\
											[(25831,15,1000),(25970,15,1000),(26043,15,1000),(26224,1,1000),(26144,15,2000),(25837,15,2000),(26227,1,1500),(26228,1,500)]])
#世界杯冠军神石竞猜失败宝箱
SF = ItemUserClass.WorldCupLevelLiBao(26262, [[(26223,1,4500),(25600,15,1500),(25600,18,1500),(25600,20,1500),(25656,1,1000)], \
                                            [(26223,1,4500),(25600,15,1500),(25600,18,1000),(25600,20,1000),(25657,1,1000),(26042,1,1000)],\
                                            [(25831,10,1300),(25970,10,1300),(26043,10,1300),(26223,1,2500),(26144,10,1300),(25837,10,1300),(26227,1,1000)],\
                                            [(25831,10,1300),(25970,10,1300),(26043,10,1300),(26223,1,2500),(26144,10,1300),(25837,10,1300),(26227,1,1000)],\
                                            [(25831,10,1300),(25970,10,1300),(26043,10,1300),(26223,1,2500),(26144,10,1300),(25837,10,1300),(26227,1,1000)]])
#世界杯冠军金币竞猜胜利宝箱
JS = ItemUserClass.WorldCupLevelLiBao(26263, [[(25671,5,1500),(25681,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,2500),(26033,1,1000),(26044,1,500)], \
                                            [(25671,5,1500),(25682,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,2500),(26033,1,1000),(26044,1,500)],\
                                            [(26144,2,1000),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,2,1000),(26032,1,1450),(26033,1,600),(26044,1,250),(26266,1,1150),(26119,1,400),(26267,1,150)],\
                                            [(26144,2,1000),(25673,5,1000),(25684,20,1000),(25663,10,1000),(25668,10,1000),(25837,1,1000),(26032,1,1450),(26033,1,600),(26044,1,250),(26266,1,1150),(26119,1,400),(26267,1,150)],\
                                            [(26144,2,1000),(25673,5,1000),(25684,20,1000),(25663,10,1000),(25668,10,1000),(25837,1,1000),(26032,1,1450),(26033,1,600),(26044,1,250),(26266,1,1150),(26119,1,400),(26267,1,150)]])
#世界杯冠军金币竞猜失败宝箱
JF = ItemUserClass.WorldCupLevelLiBao(26264, [[(25671,5,1500),(25681,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,3000),(26033,1,1000)], \
                                            [(25671,5,1500),(25682,20,1500),(25661,10,1500),(25666,10,1500),(26032,1,3000),(26033,1,1000)],\
                                            [(26144,1,1100),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,1,1100),(26032,1,1550),(26033,1,650),(26266,1,1150),(26119,1,450)],\
                                            [(26144,1,1100),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,1,1100),(26032,1,1550),(26033,1,650),(26266,1,1150),(26119,1,450)],\
                                            [(26144,1,1100),(25672,5,1000),(25683,20,1000),(25662,10,1000),(25667,10,1000),(25837,1,1100),(26032,1,1550),(26033,1,650),(26266,1,1150),(26119,1,450)]])
#花灯礼包											
HDLB = ItemUserClass.WorldCupLevelLiBao(27883, [[(25600,1,2000),(26344,1,2000),(25600,2,1000),(26344,2,1000),(26044,1,400),(26033,1,800),(26032,1,1500),(25656,1,100),(26450,1,500),(27856,1,1000),(27857,1,200)], \
                                            [(25600,1,2000),(26344,1,2000),(25600,2,1000),(26344,2,1000),(26044,1,400),(26033,1,800),(26032,1,1500),(25657,1,100),(26450,1,500),(27856,1,1000),(27857,1,200),(26042,1,50)],\
                                            [(25600,2,1500),(26344,2,1500),(26144,1,2000),(25837,1,2000),(26144,2,700),(25837,2,700),(26044,1,400),(26033,1,800),(26032,1,1600),(25657,1,100),(26450,1,500),(27856,1,1600),(27857,1,336),(26042,1,80),(26485,1,200),(26484,1,800),(26924,1,800),(26925,1,800),(26934,1,400),(26933,1,800)],\
                                            [(25600,2,1500),(26344,2,1500),(26144,1,2000),(25837,1,2000),(26144,2,700),(25837,2,700),(26044,1,400),(26033,1,800),(26032,1,1600),(25658,1,100),(26450,1,500),(27856,1,1600),(27857,1,336),(26042,1,80),(26485,1,200),(26484,1,800),(26924,1,800),(26925,1,800),(26934,1,400),(26933,1,800)],\
											[(25600,2,1500),(26344,2,1500),(26144,1,2000),(25837,1,2000),(26144,2,700),(25837,2,700),(26044,1,400),(26033,1,800),(26032,1,1600),(25659,1,100),(26450,1,500),(27856,1,1600),(27857,1,336),(26042,1,80),(26485,1,200),(26484,1,800),(26924,1,800),(26925,1,800),(26934,1,400),(26933,1,800)],\
											[(25600,2,1500),(26344,2,1500),(26144,1,2000),(25837,1,2000),(26144,2,700),(25837,2,700),(26044,1,400),(26033,1,800),(26032,1,1600),(25660,1,100),(26450,1,500),(27856,1,1600),(27857,1,336),(26042,1,80),(26485,1,200),(26484,1,800),(26924,1,800),(26925,1,800),(26934,1,400),(26933,1,800)],\
                                            [(25600,2,1500),(26344,2,1500),(26144,1,2000),(25837,1,2000),(26144,2,700),(25837,2,700),(26044,1,400),(26033,1,800),(26032,1,1600),(26525,1,100),(26450,1,500),(27856,1,1600),(27857,1,336),(26042,1,80),(26485,1,200),(26484,1,800),(26924,1,800),(26925,1,800),(26934,1,400),(26933,1,800)],\
                                            [(25600,2,1500),(26344,2,1500),(26144,1,2000),(25837,1,2000),(26144,2,700),(25837,2,700),(26044,1,400),(26033,1,800),(26032,1,1600),(27047,1,100),(26450,1,500),(27856,1,1600),(27857,1,336),(26042,1,80),(26485,1,200),(26484,1,800),(26924,1,800),(26925,1,800),(26934,1,400),(26933,1,800)]])
#跨服个人竞技场金币竞猜正确礼包
KFJJCJB = ItemUserClass.WorldCupLevelLiBao(27920, [[(25681, 20, 500), (25666, 10, 200), (25661, 10, 300), (25671, 5, 300), (25600, 2, 1000), (26344, 2, 1000)], \
												[(25682, 20, 500), (25666, 10, 200), (25661, 10, 300), (25671, 5, 300), (25600, 2, 1200), (26344, 2, 1200), (26032, 1, 800)], \
												[(25683, 20, 500), (25667, 10, 200), (25662, 10, 300), (25672, 5, 300), (25600, 3, 400), (26344, 3, 400), (26032, 1, 500), (26033, 1, 200), (26266, 1, 500), (26119, 1, 200), (26144, 2, 100), (25837, 2, 100)], \
												[(25684, 20, 500), (25668, 10, 200), (25663, 10, 300), (25673, 5, 300), (25600, 3, 200), (26344, 3, 200), (26032, 1, 300), (26033, 1, 400), (26044, 1, 100), (26266, 1, 300), (26119, 1, 200), (26267, 1, 100), (26144, 2, 500), (25837, 2, 500)], \
												[(25685, 20, 500), (25669, 10, 200), (25664, 10, 300), (25674, 5, 300), (25600, 3, 200), (26344, 3, 200), (26032, 1, 200), (26033, 1, 400), (26044, 1, 100), (26026, 1, 10), (26266, 1, 500), (26119, 1, 500), (26267, 1, 100), (26227, 1, 10), (26144, 2, 300), (25837, 2, 300)], \
												[(25686, 20, 500), (25670, 10, 200), (25665, 10, 300), (25675, 5, 300), (25600, 3, 300), (26344, 3, 300), (26033, 1, 400), (26044, 1, 200), (26026, 1, 10), (26119, 1, 400), (26267, 1, 200), (26227, 1, 10), (26144, 2, 500), (25837, 2, 500)], \
												[(26607, 20, 500), (27049, 10, 200), (27048, 10, 300), (27050, 5, 300), (25600, 3, 300), (26344, 3, 300), (26033, 1, 500), (26044, 1, 200), (26026, 1, 10), (26119, 1, 500), (26267, 1, 200), (26227, 1, 10), (26144, 2, 500), (25837, 2, 500)],\
                                                [(27066, 20, 500), (27905, 10, 200), (27904, 10, 300), (27906, 5, 300), (25600, 3, 300), (26344, 3, 300), (26033, 1, 500), (26044, 1, 200), (26026, 1, 10), (26119, 1, 500), (26267, 1, 200), (26227, 1, 10), (26144, 2, 500), (25837, 2, 500)]])


#十二星宫礼包，（类型，数量，概率） 类型小于1000的属于天赋卡， 天赋卡数量只能是1
TL = ItemUserClass.TwelvePalacePLiBao(26352, [(28032,1,1400),(26676,3,1200),(26677,30,2100),(27710,1,1400),(26341,300,1350),(26341,800,550),(106,1,50),(101,1,50),(6,1,950),(1,1,950)])

#天赋卡随机礼包
TCL1 = ItemUserClass.TalentCardRandomLiBao(27492, [(1,1,1000),(3,1,1000),(6,1,1000),(8,1,1000),(9,1,1000),(10,1,1000),(11,1,1000),(12,1,1000),(7,1,400)])
TCL2 = ItemUserClass.TalentCardRandomLiBao(27493, [(101,1,1000),(103,1,1000),(106,1,1000),(108,1,1000),(109,1,1000),(110,1,1000),(111,1,1000),(112,1,1000),(107,1,400)])
TCL3 = ItemUserClass.TalentCardRandomLiBao(28895,[(201,1,1000),(202,1,1000),(203,1,1000),(205,1,1000),(206,1,1000),(213,1,1000),(216,1,1000),(220,1,1000)])


#首充礼包 礼包coding， 开启需要神石， 开启获得金币， 开启获得的物品列表
#姻缘石礼包
#版本判断
if Environment.EnvIsNA():
	#北美版
	SC1_NA = ItemUserClass.ShouChongLiBao(26362, 888, 1880000, [(25600,120)])
else:
	#其他版本
	SC1 = ItemUserClass.ShouChongLiBao(26362, 888, 1880000, [(26344,120)])

#宝石礼包
SC2 = ItemUserClass.ShouChongLiBao(26363, 888, 1880000, [(25747,3),(25748,3),(25749,3),(25750,2),(25751,2),(25738,1)])
#占卜礼盒
SC3 = ItemUserClass.ShouChongLiBao(26364, 888, 1880000, [(26042,6)])
#符文礼盒
SC4 = ItemUserClass.ShouChongLiBao(26365, 888, 1880000, [(26227,10)])
#优惠小礼包
#宝石优惠小礼包
if Environment.EnvIsNA():
	NA_SC5 = ItemUserClass.ShouChongLiBao(26466, 275, 188000, [(26026,1),(26033,1),(26035,1)])
else:
	SC5 = ItemUserClass.ShouChongLiBao(26466, 88, 188000, [(26026,1),(26033,1),(26035,1)])
#占卜优惠小礼包
if Environment.EnvIsNA():
	NA_SC6 = ItemUserClass.ShouChongLiBao(26467, 495, 320000, [(26042,1),(26036,1)])
else:
	SC6 = ItemUserClass.ShouChongLiBao(26467, 148, 320000, [(26042,1),(26036,1)])

#符文优惠小礼包
if Environment.EnvIsNA():
	NA_SC7 = ItemUserClass.ShouChongLiBao(26468, 225, 188000, [(26227,1),(26035,1)])
else:
	SC7 = ItemUserClass.ShouChongLiBao(26468, 88, 188000, [(26227,1),(26035,1)])
	
#羽翼优惠小礼包
if Environment.EnvIsNA():
	NA_SC8 = ItemUserClass.ShouChongLiBao(26469, 395, 188000, [(25837,12),(26035,1)])
else:
	SC8 = ItemUserClass.ShouChongLiBao(26469, 88, 188000, [(25837,12),(26035,1)])
	
#宠物优惠小礼包
if Environment.EnvIsNA():
	NA_SC9 = ItemUserClass.ShouChongLiBao(26470, 695, 188000, [(26144,12),(26035,1)])
else:
	SC9 = ItemUserClass.ShouChongLiBao(26470, 88, 188000, [(26144,12),(26035,1)])
	
#圣器精炼优惠小礼盒
if Environment.EnvIsNA():
	NA_SC10 = ItemUserClass.ShouChongLiBao(26489, 315, 288000, [(26302,12)])
else:
	SC10 = ItemUserClass.ShouChongLiBao(26489, 88, 288000, [(26302,12)])
	
#宝石超值礼盒
SC11 = ItemUserClass.ShouChongLiBao(26490, 888, 2880000, [(26026,10)])
#宠物培养超值礼盒
SC12 = ItemUserClass.ShouChongLiBao(26491, 888, 2880000, [(26144,100)])
#羽翼培养超值礼盒
SC13 = ItemUserClass.ShouChongLiBao(26492, 888, 2880000, [(25837,100)])
#圣器精炼超值礼盒
SC14 = ItemUserClass.ShouChongLiBao(26493, 888, 2880000, [(26302,100)])
#符文超值礼盒
SC15 = ItemUserClass.ShouChongLiBao(26494, 888, 2880000, [(26227,10)])
#宝石优惠小礼盒
if Environment.EnvIsNA():
	NA_SC16 = ItemUserClass.ShouChongLiBao(26495, 225, 288000, [(26026,1),(26033,1)])
else:
	SC16 = ItemUserClass.ShouChongLiBao(26495, 88, 288000, [(26026,1),(26033,1),(26035,1)])
	
#羽翼培养优惠小礼盒
if Environment.EnvIsNA():
	NA_SC17 = ItemUserClass.ShouChongLiBao(26496, 345, 288000, [(25837,12)])
else:
	SC17 = ItemUserClass.ShouChongLiBao(26496, 88, 288000, [(25837,12),(26035,1)])
	
#宠物培养优惠小礼盒
if Environment.EnvIsNA():
	NA_SC18 = ItemUserClass.ShouChongLiBao(26497, 625, 288000, [(26144,12)])
else:
	SC18 = ItemUserClass.ShouChongLiBao(26497, 88, 288000, [(26144,12),(26035,1)])
	
#符文优惠小礼盒
if Environment.EnvIsNA():
	NA_SC19 = ItemUserClass.ShouChongLiBao(26498, 195, 288000, [(26227,1)])
else:
	SC19 = ItemUserClass.ShouChongLiBao(26498, 88, 288000, [(26227,1),(26035,1)])
	
#坐骑优惠礼盒
SC20= ItemUserClass.ShouChongLiBao(26642, 888, 1880000, [(25600,120)])
#羽翼折扣礼包
SC21= ItemUserClass.ShouChongLiBao(27394, 1995, 0, [(37013,1)])
#时装折扣礼包Ⅰ
SC22= ItemUserClass.ShouChongLiBao(27396, 495, 0, [(37004,1),(27397,1)])
#时装折扣礼包Ⅱ
SC23= ItemUserClass.ShouChongLiBao(27397, 695, 0, [(37001,1),(27398,1)])
#时装折扣礼包Ⅲ
SC24= ItemUserClass.ShouChongLiBao(27398, 695, 0, [(37002,1)])
#天赋卡折扣礼包
SC25= ItemUserClass.ShouChongLiBao(28040, 2995, 0, [(28039,1)])
#坐骑进化石折扣礼包
SC26= ItemUserClass.ShouChongLiBao(29515, 888, 1880000, [(27566,24)])

#烟花
Fireworks = ItemUserClass.Fireworks(26369)

#天赋卡礼包coding [(概率， 天赋卡类型)]
#紫色白羊天賦卡禮包
TL1 = ItemUserClass.TalentLiBao(26438, [(7, 1)])
#橙色白羊天賦卡禮包
TL2 = ItemUserClass.TalentLiBao(26439, [(107, 1)])
#紫色射手天賦卡禮包
TL3= ItemUserClass.TalentLiBao(26458, [(11, 1)])
#橙色射手天賦卡禮包
TL4= ItemUserClass.TalentLiBao(26459, [(111, 1)])
#紫色狮子天賦卡禮包
TL5= ItemUserClass.TalentLiBao(26481, [(5, 1)])
#橙色狮子天賦卡禮包
TL6= ItemUserClass.TalentLiBao(26482, [(105, 1)])
#紫色金牛天賦卡禮包
TL7= ItemUserClass.TalentLiBao(27109, [(8, 1)])
#橙色金牛天賦卡禮包
TL8= ItemUserClass.TalentLiBao(27110, [(108, 1)])
#紫色飞马天賦卡禮包
TL9 = ItemUserClass.TalentLiBao(27177, [(13, 1)])
#橙色飞马天賦卡禮包
TL10 = ItemUserClass.TalentLiBao(27178, [(113, 1)])
#紫色双鱼天赋卡礼包
TL11 = ItemUserClass.TalentLiBao(27427, [(2, 1)])
#橙色双鱼天赋卡礼包
TL12 = ItemUserClass.TalentLiBao(27428, [(102, 1)])
#紫色天鹅天赋卡礼包
TL11 = ItemUserClass.TalentLiBao(27705, [(15, 1)])
#橙色天鹅天赋卡礼包
TL12 = ItemUserClass.TalentLiBao(27706, [(115, 1)])
#紫色巨蟹天赋卡礼包
TL13 = ItemUserClass.TalentLiBao(27880, [(4, 1)])
#紫色天秤天赋卡礼包
TL14 = ItemUserClass.TalentLiBao(27893, [(9, 1)])
#紫色摩羯天赋卡礼包
TL15 = ItemUserClass.TalentLiBao(28039, [(12, 1)])
#紫色天鹰天赋卡礼包
TL16 = ItemUserClass.TalentLiBao(28241, [(18, 1)])
#橙色天鹰天赋卡礼包
TL17 = ItemUserClass.TalentLiBao(28242, [(118, 1)])
#紫色水瓶天赋卡礼包
TL18 = ItemUserClass.TalentLiBao(28268, [(1, 1)])
#橙色天蝎天赋卡礼包
TL19 = ItemUserClass.TalentLiBao(28269, [(110, 1)])
#橙色巨蟹天赋卡礼包
TL19 = ItemUserClass.TalentLiBao(28825, [(104, 1)])
#红色水瓶天赋卡礼包
TL20 = ItemUserClass.TalentLiBao(28898, [(201, 1)])
#红色双鱼天赋卡礼包
TL21 = ItemUserClass.TalentLiBao(28897, [(202, 1)])
#橙色天秤天赋卡礼包
TL22 = ItemUserClass.TalentLiBao(28899, [(109, 1)])
#紫色猎户座天赋卡礼包
TL23 = ItemUserClass.TalentLiBao(28969, [(19 , 1)])
#橙色猎户座天赋卡礼包
TL24 = ItemUserClass.TalentLiBao(28978, [(119 , 1)])
#红色处女座天赋卡礼包
TL25 = ItemUserClass.TalentLiBao(29015, [(206 , 1)])
#紫色处女座天赋卡礼包
TL26 = ItemUserClass.TalentLiBao(29042, [(6 ,1)])
#紫色仙女座天赋卡礼包
TL27 = ItemUserClass.TalentLiBao(29043, [(16 ,1)])
#紫色天琴座天赋卡礼包
TL28 = ItemUserClass.TalentLiBao(29092, [(14 ,1)])
#橙色天琴座天赋卡礼包
TL29 = ItemUserClass.TalentLiBao(29486, [(114 ,1)])

#年卡礼包
#月卡
CARD1 = ItemUserClass.CardLiBao(26473, 5, [(25600,1)])
#季度卡
CARD2 = ItemUserClass.CardLiBao(26474, 5, [(25600,1),(26150,1)])
#半年卡
CARD3 = ItemUserClass.CardLiBao(26475, 10, [(25600,2),(26150,2)])
#年卡
CARD4 = ItemUserClass.CardLiBao(26476, 10, [(25600,2),(26150,2),(26032,1)])

#装备附魔礼包 礼包id，开启需要消耗道具，[(获得的道具，获得数量，概率)…]
EQEN = ItemUserClass.EquipmentEnchantLibao(26485, [(26479, 1 ,1000), (26479,2,1000), (26479,3,1000), (26479,4,1000), (26479,5,1000), (26479,6,1000), (26479,7,1000), (26479,8,1000), (26479,9,1000), (26479,10,1000)])

#坐骑经验珠 (道具id, 获得坐骑经验)
MountExp1 =  ItemUserClass.MountExpFood(26639, 500)
MountExp2 =  ItemUserClass.MountExpFood(26640, 1000)
MountExp3 =  ItemUserClass.MountExpFood(26641, 1500)
#坐骑升星精华(道具ID, 最高的进阶数（坐骑进阶id）)
MountEval = ItemUserClass.MountEvolveFood(26638, 51)
MountEval = ItemUserClass.MountEvolveFood(26643, 61)
MountEval = ItemUserClass.MountEvolveFood(26644, 71)
#月饼：使用增加体力（道具ID,使用增加体力数值）
MoonCakeTili1 = ItemUserClass.MoonCakeTili(26660,5)
MoonCakeTili2 = ItemUserClass.MoonCakeTili(26661,10)
MoonCakeTili3 = ItemUserClass.MoonCakeTili(26662,20)
MoonCakeTili4 = ItemUserClass.MoonCakeTili(27579,60)
MoonCakeTili5 = ItemUserClass.MoonCakeTili(28046,100)
MoonCakeTili6 = ItemUserClass.MoonCakeTili(28047,120)
MoonCakeTili7 = ItemUserClass.MoonCakeTili(28048,150)
MoonCakeTili8 = ItemUserClass.MoonCakeTili(28049,180)
MoonCakeTili9 = ItemUserClass.MoonCakeTili(28085,200)
MoonCakeTili10 = ItemUserClass.MoonCakeTili(28380,50)

#随机金币礼包
RDMM1= ItemUserClass.RandomMoneyLibao(26667, [((50000, 100000), 5000), ((100001, 200000), 2500), ((200001, 300000), 1000), ((300001, 500000), 500), ])
RDMM2= ItemUserClass.RandomMoneyLibao(26668, [((100000, 300000), 5000), ((300001, 400000), 2500), ((400001, 600000), 1000), ((600001, 1000000), 500),])
RDMM3= ItemUserClass.RandomMoneyLibao(26669, [((150000, 450000), 5000), ((450001, 600000), 2500), ((600001, 800000), 1000), ((800001, 1000000), 500),])
RDMM4 = ItemUserClass.RandomMoneyLibao(26670, [((200000, 600000), 5000), ((600001, 800000), 2500), ((800001, 1000000), 1000), ((1000001, 1200000), 500), ])


#龙灵礼包（id=26901发龙灵，其他id发普通道具）
DSLB1 = ItemUserClass.DragonSoulLibao(26902, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26681, 1, 25), (26682, 1, 25)])
DSLB2 = ItemUserClass.DragonSoulLibao(26903, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26683, 1, 25), (26684, 1, 25)])
DSLB3 = ItemUserClass.DragonSoulLibao(26904, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26685, 1, 25), (26686, 1, 25)])
DSLB4 = ItemUserClass.DragonSoulLibao(26943, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26705, 1, 25), (26706, 1, 25)])
DSLB5 = ItemUserClass.DragonSoulLibao(26944, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26707, 1, 25), (26708, 1, 25)])
DSLB6 = ItemUserClass.DragonSoulLibao(26945, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26709, 1, 25), (26710, 1, 25)])
DSLB7 = ItemUserClass.DragonSoulLibao(26946, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26729, 1, 25), (26730, 1, 25)])
DSLB8 = ItemUserClass.DragonSoulLibao(26947, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26731, 1, 25), (26732, 1, 25)])
DSLB9 = ItemUserClass.DragonSoulLibao(26948, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (26733, 1, 25), (26734, 1, 25)])
DSLB10 = ItemUserClass.DragonSoulLibao(27365, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27197, 1, 25), (27198, 1, 25)])
DSLB11 = ItemUserClass.DragonSoulLibao(27366, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27199, 1, 25), (27200, 1, 25)])
DSLB12 = ItemUserClass.DragonSoulLibao(27367, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27201, 1, 25), (27202, 1, 25)])
DSLB13 = ItemUserClass.DragonSoulLibao(27645, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27215, 1, 25), (27216, 1, 25)])
DSLB14 = ItemUserClass.DragonSoulLibao(27646, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27217, 1, 25), (27218, 1, 25)])
DSLB15 = ItemUserClass.DragonSoulLibao(27647, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27219, 1, 25), (27220, 1, 25)])
DSLB16 = ItemUserClass.DragonSoulLibao(28639, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27233, 1, 25), (27234, 1, 25)])
DSLB17 = ItemUserClass.DragonSoulLibao(28640, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27235, 1, 25), (27236, 1, 25)])
DSLB18 = ItemUserClass.DragonSoulLibao(28641, None, [(26901, 200 , 400), (26901, 300 , 300), (26901, 400 , 200), (26901, 500 , 100), (27237, 1, 25), (27238, 1, 25)])

#龙灵礼包-神龙宝箱（礼包ID，必得物品（ID,数量），随机物品（ID，数量））
DSLB100 = ItemUserClass.DragonSoulLibao(26969, None, [(26901, 10000 , 800), (26753, 1, 1000), (26754, 1, 1000), (26755, 1, 1000), (26756, 1, 1000), (26757, 1, 500), (26758, 1, 1000)])
DSLB101 = ItemUserClass.DragonSoulLibao(27102, None, [(26901, 30000 , 800)])
DSLB102 = ItemUserClass.DragonSoulLibao(27103, None, [(26901, 35000 , 800)])
DSLB103 = ItemUserClass.DragonSoulLibao(27104, None, [(26901, 40000 , 800)])
DSLB104 = ItemUserClass.DragonSoulLibao(27169, [(27041, 3)], [(26901, 10000 , 550), (26777, 1, 500), (26778, 1, 200), (26779, 1, 500), (26780, 1, 200), (26781, 1, 500), (26782, 1, 200)])
DSLB105 = ItemUserClass.DragonSoulLibao(27170, None, [(26901, 30000 , 800)])
DSLB106 = ItemUserClass.DragonSoulLibao(27171, None, [(26901, 50000 , 800)])
if Environment.EnvIsNA():
	NA_DSLB107 = ItemUserClass.DragonSoulLibao(27445, [(26031, 1), (26043, 5)], [])#60级等级大礼（2）
else:
	DSLB107 = ItemUserClass.DragonSoulLibao(27445, [(26925, 5), (26924, 5), (26901, 10000)], [])#60级等级大礼（2）
DSLB108 = ItemUserClass.DragonSoulLibao(27468, [(26925, 5), (26924, 5), (26901, 10000)], [])#神龙进阶宝箱
DSLB109 = ItemUserClass.DragonSoulLibao(27471, None, [(26901, 1000 , 800)])
DSLB110 = ItemUserClass.DragonSoulLibao(27475, None, [(26901, 12000 , 800)])
DSLB111 = ItemUserClass.DragonSoulLibao(27526, None, [(26901, 20000 , 800)])
DSLB112 = ItemUserClass.DragonSoulLibao(27657, None, [(26901, 40000 , 800)])
DSLB113 = ItemUserClass.DragonSoulLibao(27658, None, [(26901, 35000 , 800)])
DSLB114 = ItemUserClass.DragonSoulLibao(27659, None, [(26901, 30000 , 800)])
DSLB115 = ItemUserClass.DragonSoulLibao(27660, None, [(26901, 25000 , 800)])
DSLB116 = ItemUserClass.DragonSoulLibao(27661, None, [(26901, 20000 , 800)])
DSLB117 = ItemUserClass.DragonSoulLibao(27662, None, [(26901, 10000 , 800)])
DSLB118 = ItemUserClass.DragonSoulLibao(27663, None, [(26901, 5000 , 800)])
DSLB119 = ItemUserClass.DragonSoulLibao(27668, None, [(26901, 500 , 800)])
DSLB120 = ItemUserClass.DragonSoulLibao(28248, None, [(26901, 120000 , 800)])

#坐骑外形激活道具 (item, 坐骑id)
ItemUserClass.ItemAddMount(26923, 11)
ItemUserClass.ItemAddMount(26972, 12)
ItemUserClass.ItemAddMount(27028, 10)
ItemUserClass.ItemAddMount(27039, 13)
ItemUserClass.ItemAddMount(27073, 14)
ItemUserClass.ItemAddMount(27419, 16)
ItemUserClass.ItemAddMount(27864, 18)
ItemUserClass.ItemAddMount(28456, 21)
ItemUserClass.ItemAddMount(28511, 20)
ItemUserClass.ItemAddMount(28973, 22)
ItemUserClass.ItemAddMount(28971, 23)
ItemUserClass.ItemAddMount(28972, 24)
ItemUserClass.ItemAddMount(29066, 26)
ItemUserClass.ItemAddMount(29271, 27)
ItemUserClass.ItemAddMount(29389, 28)
ItemUserClass.ItemAddMount(29390, 29)
ItemUserClass.ItemAddMount(29392, 30)

#首充大礼包坐骑
ItemUserClass.ItemAddFirstPayMount(27399, 15)
#首充坐骑永久激活道具
ItemUserClass.ChangeMountTime(27422, 15)

#随机魔晶礼包
RBRMB1 = ItemUserClass.RandomBindRMBLibao(26977,[(2500,50),(2000,60),(1500,70),(1250,80),(1000,90),(500,100),(400,120),(300,150),(200,180),(100,200),(50,300),(20,400),(10,500),(5,1000)])

#变身卡
ItemUserClass.CardBuff(26988, 2501)
ItemUserClass.CardBuff(26989, 2502)
ItemUserClass.CardBuff(26990, 2503)
ItemUserClass.CardBuff(26991, 2504)
ItemUserClass.CardBuff(26992, 2505)
ItemUserClass.CardBuff(26993, 2506)
ItemUserClass.CardBuff(26994, 2507)
ItemUserClass.CardBuff(26995, 2508)
ItemUserClass.CardBuff(26996, 2509)
ItemUserClass.CardBuff(26997, 2510)
ItemUserClass.CardBuff(26998, 2511)
ItemUserClass.CardBuff(26999, 2512)
ItemUserClass.CardBuff(27000, 2513)
ItemUserClass.CardBuff(27001, 2514)
ItemUserClass.CardBuff(27002, 2515)
ItemUserClass.CardBuff(27003, 2516)
ItemUserClass.CardBuff(27004, 2517)
ItemUserClass.CardBuff(27005, 2518)
ItemUserClass.CardBuff(27006, 2519)
ItemUserClass.CardBuff(27007, 2520)
ItemUserClass.CardBuff(27008, 2521)
ItemUserClass.CardBuff(27009, 2522)
ItemUserClass.CardBuff(27010, 2523)
ItemUserClass.CardBuff(27011, 2524)
ItemUserClass.CardBuff(27012, 2525)
ItemUserClass.CardBuff(27013, 2526)
ItemUserClass.CardBuff(27014, 2527)
ItemUserClass.CardBuff(27015, 2528)
ItemUserClass.CardBuff(27016, 2529)
ItemUserClass.CardBuff(27017, 2530)
ItemUserClass.CardBuff(27018, 2531)
ItemUserClass.CardBuff(27019, 2532)
ItemUserClass.CardBuff(27020, 2533)
ItemUserClass.CardBuff(27021, 2534)
ItemUserClass.CardBuff(27022, 2535)
ItemUserClass.CardBuff(27023, 2536)
ItemUserClass.CardBuff(27024, 2537)
ItemUserClass.CardBuff(27025, 2538)


#宠物折扣礼包（物品coding, 宠物类型, 开启需要的神石）(北美)
petLB1 = ItemUserClass.PetLiBao(27395, 2, 495)

#国服宠物礼包 物品coding, 宠物类型
petLB2 = ItemUserClass.PetLiBao_1(27577, 1)
petLB2 = ItemUserClass.PetLiBao_1(28354, 2)
petLB2 = ItemUserClass.PetLiBao_1(27699, 2)
petLB2 = ItemUserClass.PetLiBao_1(27700, 3)
#荣誉礼包(金券)
ItemUserClass.JTGoldLiBao(27420, 50)

#龙珠变身卡普通礼包
ItemUserClass.ZumaCardNormalLiBao(27481, [(26988,1,575),(26995,1,575),(27002,1,575),(26989,1,575),(26996,1,575),(27003,1,575),(26990,1,575),(26997,1,575),
										(27004,1,575),(26991,1,575),(26998,1,575),(27005,1,575),(26992,1,575),(26999,1,575),(27006,1,575),(26993,1,575),
										(27000,1,575),(27007,1,575),(26994,1,575),(27001,1,575),(27008,1,575),(27018,1,100),(27019,1,100),(27020,1,100),
										(27021,1,100),(27022,1,100),(27023,1,100)])
#龙珠变身卡高级礼包
ItemUserClass.ZumaCardAdvancedLiBao(27482, [(27018,1,750),(27019,1,750),(27020,1,750),(27021,1,750),(27022,1,750),(27023,1,750),(27024,1,100),(27025,1,100)])

#称号道具
AddTitle_1 = ItemUserClass.ItemAddTitle(27895, 31)
AddTitle_2 = ItemUserClass.ItemAddTitle(28577, 19)
AddTitle_3 = ItemUserClass.ItemAddTitle(28578, 20)
AddTitle_4 = ItemUserClass.ItemAddTitle(28579, 21)
AddTitle_5 = ItemUserClass.ItemAddTitle(28580, 22)
AddTitle_6 = ItemUserClass.ItemAddTitle(28581, 23)
AddTitle_7 = ItemUserClass.ItemAddTitle(28582, 24)
AddTitle_8 = ItemUserClass.ItemAddTitle(28583, 25)
AddTitle_9 = ItemUserClass.ItemAddTitle(28584, 26)
AddTitle_10 = ItemUserClass.ItemAddTitle(28585, 27)
AddTitle_11 = ItemUserClass.ItemAddTitle(28586, 28)
AddTitle_12 = ItemUserClass.ItemAddTitle(28793, 72)
AddTitle_13 = ItemUserClass.ItemAddTitle(28795, 73)
AddTitle_14 = ItemUserClass.ItemAddTitle(28797, 74)
AddTitle_15 = ItemUserClass.ItemAddTitle(28799, 75)
AddTitle_16 = ItemUserClass.ItemAddTitle(28835, 76)
AddTitle_17 = ItemUserClass.ItemAddTitle(28843, 120)
AddTitle_18 = ItemUserClass.ItemAddTitle(28902, 77)
AddTitle_19 = ItemUserClass.ItemAddTitle(28903, 78)
AddTitle_20 = ItemUserClass.ItemAddTitle(29004, 92)
AddTitle_21 = ItemUserClass.ItemAddTitle(29005, 93)
AddTitle_22 = ItemUserClass.ItemAddTitle(29006, 94)
AddTitle_23 = ItemUserClass.ItemAddTitle(29374, 95)
AddTitle_24 = ItemUserClass.ItemAddTitle(29445, 96)
AddTitle_25 = ItemUserClass.ItemAddTitle(29446, 97)
AddTitle_26 = ItemUserClass.ItemAddTitle(29447, 98)
AddTitle_27 = ItemUserClass.ItemAddTitle(29476, 103)

#加亲密道具	参数-->道具coding, 亲密值
Qinmi_1 = ItemUserClass.ItemAddQinmi(27873, 1)

#公会道具
UnionResourceItem = ItemUserClass.ItemAddResource(28277)
UnionContributionItem = ItemUserClass.ItemAddContribution(28278)

#声望道具 参数 --> 道具coding, 声望值
itemAddReputation1 = ItemUserClass.ItemAddReputation(28377, 100000)
itemAddReputation2 = ItemUserClass.ItemAddReputation(29488, 1000)
#给坐骑增加临时经验值
MountTempExp1 =  ItemUserClass.MountExpFoodTemp(28398, 100)

#==============宠物增加临时培养值==================
#1生命，4物攻，6法攻，8暴击，9免暴，10破防，11免破，12格挡，13破档
#(coding, [星级, {属性：临时值}])
ItemUserClass.ItemAddPetTrainValue(28408, [1, {1:200,4:100,6:100,8:100,9:100}])
ItemUserClass.ItemAddPetTrainValue(28410, [2, {1:400,4:100,6:100,8:100,9:100,12:100,13:100}])
ItemUserClass.ItemAddPetTrainValue(28412, [3, {1:600,4:200,6:200,8:200,9:200,12:100,13:100}])
ItemUserClass.ItemAddPetTrainValue(28414, [4, {1:1000,4:300,6:300,8:300,9:300,10:100,11:100,12:200,13:200}])
ItemUserClass.ItemAddPetTrainValue(28426, [5, {1:1500,4:400,6:400,8:400,9:400,10:100,11:100,12:300,13:300}])

#=============宠物增加临时修行值===================
#(coding, [宠物阶数, 临时修行进度])
ItemUserClass.ItemAddPetEvoValue(28416,(1, 1))
ItemUserClass.ItemAddPetEvoValue(28418,(2, 1))
ItemUserClass.ItemAddPetEvoValue(28420,(3, 1))
ItemUserClass.ItemAddPetEvoValue(28422,(4, 1))
#==============羽翼增加临时进度值=================
#使用该道具后100%增加玩家当前所有羽翼对应级数的进度值，每个级数增加的临时进度值不同
#(coding, 增加的临时进度值)
ItemUserClass.ItemAddWingTrainValue(28439, 100)
#==============神龙进化增加临时进度=================
#(coding, (神龙品阶, 临时进度))
ItemUserClass.ItemAddDragonTrainValue(28502, (1,1))
ItemUserClass.ItemAddDragonTrainValue(28504, (2,1))
ItemUserClass.ItemAddDragonTrainValue(28506, (3,1))
ItemUserClass.ItemAddDragonTrainValue(28508, (4,1))
#=================战魂强化石=====================
ItemUserClass.ItemAddWarStationPro(28588)
#=================阵灵强化石=====================
ItemUserClass.ItemAddStationSoulPro(28617)
#=================专属礼包=====================
ItemUserClass.ZhuanshuLibao(28618, 25600, 10, [(0, 100), (10, 100), (20, 1100)])
ItemUserClass.ZhuanshuLibao(28671, 27167, 10, [(1, 1000), (2, 1000), (3, 1000), (4, 800), (5, 700), (6, 600), (7, 500), (8, 400), (9, 300), (10, 200)])
ItemUserClass.ZhuanshuLibao(28672, 27566, 20, [(2, 1000), (4, 1000), (6, 1000), (8, 800), (10, 700), (12, 600), (14, 500), (16, 400), (18, 300), (20, 200)])
ItemUserClass.ZhuanshuLibao(28673, 4, 20, [(4, 1000), (8, 800), (12, 600), (16, 400), (20, 200)])
ItemUserClass.ZhuanshuLibao(28674, 25837, 50, [(10, 1000), (20, 800), (30, 600), (40, 400), (50, 200)])
ItemUserClass.ZhuanshuLibao(28675, 26144, 50, [(10, 1000), (20, 800), (30, 600), (40, 400), (50, 200)])
ItemUserClass.ZhuanshuLibao(28676, 26676, 4, [(1, 800), (2, 600), (3, 400), (4, 200)])
ItemUserClass.ZhuanshuLibao(28677, 26677, 20, [(4, 1000), (8, 800), (12, 600), (16, 400), (20, 200)])


#红包礼包 【30,39】【40,59】【60,79】【80,99】【100,179】 格式【coding,cnt rate,isPrecious】
BigHongBao = ItemUserClass.HongBaoLiBao(28685, [[(28687, 100, 7, 1), (27532, 1, 7, 1), (28687, 10, 800, 1), (28689, 1, 900, 0), (27368, 1, 900, 0), (27369, 1, 1000, 0), (27824, 20, 1000, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (27517, 1, 300, 0), (25600, 2, 1000, 0), (25600, 3, 1000, 0), (25600, 4, 1000, 0), (25656, 1, 50, 0), (26344, 2, 1000, 0), (26344, 3, 1000, 0), (26344, 4, 1000, 0), (26342, 2, 1000, 0)], \
												[(28687, 100, 7, 1), (27532, 1, 7, 1), (28687, 10, 800, 1), (28689, 1, 900, 0), (27368, 1, 900, 0), (27369, 1, 1000, 0), (27824, 20, 1000, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (27517, 1, 300, 0), (27518, 1, 80, 0), (25600, 2, 1000, 0), (25600, 3, 1000, 0), (25600, 4, 1000, 0), (25657, 1, 50, 0), (26344, 2, 1000, 0), (26344, 3, 1000, 0), (26344, 4, 1000, 0), (26342, 2, 1000, 0), (26042, 1, 50, 0)], \
												[(28687, 100, 12, 1), (27532, 1, 12, 1), (28687, 10, 1500, 1), (28689, 1, 1500, 0), (27368, 1, 1500, 0), (27369, 1, 1600, 0), (27824, 20, 1600, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (27517, 1, 300, 0), (27518, 1, 80, 0), (26144, 1, 1000, 0), (26144, 2, 1000, 0), (26144, 3, 500, 0), (25837, 1, 1000, 0), (25837, 2, 1000, 0), (25837, 3, 500, 0), (25658, 1, 50, 0), (26936, 1, 1000, 0), (26936, 2, 1000, 0), (26936, 3, 500, 0), (26934, 1, 1000, 0), (26933, 1, 1000, 0), (26266, 1, 1000, 0), (26119, 1, 1000, 0), (26267, 1, 300, 0), (25970, 2, 1000, 0), (25831, 2, 1000, 0), (26485, 1, 500, 0)], \
												[(28687, 100, 14, 1), (27532, 1, 14, 1), (28687, 10, 1800, 1), (28689, 1, 1800, 0), (27368, 1, 1800, 0), (27369, 1, 1900, 0), (27824, 20, 1900, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (27517, 1, 300, 0), (27518, 1, 80, 0), (26144, 1, 1000, 0), (26144, 2, 1000, 0), (26144, 3, 500, 0), (25837, 1, 1000, 0), (25837, 2, 1000, 0), (25837, 3, 500, 0), (25659, 1, 50, 0), (26936, 1, 1000, 0), (26936, 2, 1000, 0), (26936, 3, 500, 0), (26934, 1, 1000, 0), (26933, 1, 1000, 0), (26266, 1, 1000, 0), (26119, 1, 1000, 0), (26267, 1, 300, 0), (27621, 1, 80, 0), (25970, 2, 1000, 0), (25831, 2, 1000, 0), (26485, 1, 500, 0), (26298, 1, 300, 0), (28033, 1, 800, 0), (28034, 1, 400, 0)], \
												[(28687, 100, 15, 1), (27532, 1, 15, 1), (28687, 10, 2000, 1), (28689, 1, 2000, 0), (27368, 1, 2000, 0), (27369, 1, 2000, 0), (27824, 20, 2100, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (27517, 1, 300, 0), (27518, 1, 80, 0), (26144, 1, 1000, 0), (26144, 2, 1000, 0), (26144, 3, 500, 0), (25837, 1, 1000, 0), (25837, 2, 1000, 0), (25837, 3, 500, 0), (25660, 1, 50, 0), (26936, 1, 1000, 0), (26936, 2, 1000, 0), (26936, 3, 500, 0), (26934, 1, 1000, 0), (26933, 1, 1000, 0), (26266, 1, 1000, 0), (26119, 1, 1000, 0), (26267, 1, 300, 0), (27621, 1, 80, 0), (25970, 2, 1000, 0), (25831, 2, 1000, 0), (26485, 1, 500, 0), (26298, 1, 300, 0), (28033, 1, 800, 0), (28034, 1, 400, 0), (28035, 1, 100, 0), (27587, 1, 1000, 0), (27587, 2, 1000, 0), (27587, 3, 500, 0)]
												])

SmallHongBao = ItemUserClass.HongBaoLiBao(28686, [[(28687, 5, 800, 1), (28688, 1, 900, 0), (27368, 1, 900, 0), (27824, 10, 900, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (25600, 1, 1000, 0), (25600, 2, 1000, 0), (26344, 1, 1000, 0), (26344, 2, 1000, 0), (26342, 1, 1000, 0)], \
												   [(28687, 5, 800, 1), (28688, 1, 900, 0), (27368, 1, 900, 0), (27824, 10, 900, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (25600, 1, 1000, 0), (25600, 2, 1000, 0), (26344, 1, 1000, 0), (26344, 2, 1000, 0), (26342, 1, 1000, 0)], \
												   [(28687, 5, 1800, 1), (28688, 1, 1900, 0), (27368, 1, 1900, 0), (27824, 10, 1900, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (26266, 1, 1000, 0), (26266, 2, 1000, 0), (25837, 1, 1000, 0), (25837, 2, 1000, 0), (26144, 1, 1000, 0), (26144, 2, 1000, 0), (26479, 1, 1000, 0), (25831, 1, 1000, 0), (25970, 1, 1000, 0), (26936, 1, 1000, 0), (26936, 2, 1000, 0), (26934, 1, 1000, 0), (26933, 1, 1000, 0)], \
												   [(28687, 5, 2100, 1), (28688, 1, 2100, 0), (27368, 1, 2100, 0), (27824, 10, 2200, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (26266, 1, 1000, 0), (26266, 2, 1000, 0), (25837, 1, 1000, 0), (25837, 2, 1000, 0), (26144, 1, 1000, 0), (26144, 2, 1000, 0), (26479, 1, 1000, 0), (25831, 1, 1000, 0), (25970, 1, 1000, 0), (28033, 1, 1000, 0), (28240, 1, 1000, 0), (26936, 1, 1000, 0), (26936, 2, 1000, 0), (26934, 1, 1000, 0), (26933, 1, 1000, 0)], \
												   [(28687, 5, 2300, 1), (28688, 1, 2400, 0), (27368, 1, 2400, 0), (27824, 20, 2400, 0), (26032, 1, 1000, 0), (27516, 1, 1000, 0), (26266, 1, 1000, 0), (26266, 2, 1000, 0), (25837, 1, 1000, 0), (25837, 2, 1000, 0), (26144, 1, 1000, 0), (26144, 2, 1000, 0), (26479, 1, 1000, 0), (25831, 1, 1000, 0), (25970, 1, 1000, 0), (28033, 1, 1000, 0), (28240, 1, 1000, 0), (27587, 1, 1000, 0), (27587, 2, 1000, 0), (26936, 1, 1000, 0), (26936, 2, 1000, 0), (26934, 1, 1000, 0), (26933, 1, 1000, 0)]
												])


#神石随机礼包  格式 ： (coding,[神石下限，神石上限])
RandomUnBindRMBLiBao_1 = ItemUserClass.RandomUnBindRMBLiBao(28722,[1000,2000])
#星灵幸运石
StarGirlLucky1 = ItemUserClass.StarGirlLucky(28907)
StarGirlLucky2 = ItemUserClass.StarGirlLucky(28908)
StarGirlLucky3 = ItemUserClass.StarGirlLucky(28909)
StarGirlLucky4 = ItemUserClass.StarGirlLucky(28910)
StarGirlLucky5 = ItemUserClass.StarGirlLucky(28911)
StarGirlLucky6 = ItemUserClass.StarGirlLucky(28912)

#临时婚戒经验道具
RingTempExp1 = ItemUserClass.ItemAddRingValue(29106,10)
#幸运红包
LuckyHongBaoConsume = ItemUserClass.LuckyHongBao(29057)
LuckyHongBaoRecharge = ItemUserClass.LuckyHongBao(29059)

#公会发红包内部道具
UnionHongBaoItemUse = ItemUserClass.ItemUnionHongBao(29448)

#===============================================================================
#卡牌图鉴
#===============================================================================
#(道具coding, 使用获得卡牌id)
CardAtlas_1 = ItemUserClass.CardAtlas(29115, 1)
CardAtlas_2 = ItemUserClass.CardAtlas(29116, 2)
CardAtlas_3 = ItemUserClass.CardAtlas(29117, 3)
CardAtlas_4 = ItemUserClass.CardAtlas(29118, 4)
CardAtlas_5 = ItemUserClass.CardAtlas(29119, 5)
CardAtlas_6 = ItemUserClass.CardAtlas(29120, 6)
CardAtlas_7 = ItemUserClass.CardAtlas(29121, 7)
CardAtlas_8 = ItemUserClass.CardAtlas(29122, 8)
CardAtlas_9 = ItemUserClass.CardAtlas(29123, 9)
CardAtlas_10 = ItemUserClass.CardAtlas(29124, 10)
CardAtlas_11 = ItemUserClass.CardAtlas(29125, 11)
CardAtlas_12 = ItemUserClass.CardAtlas(29126, 12)
CardAtlas_13 = ItemUserClass.CardAtlas(29127, 13)
CardAtlas_14 = ItemUserClass.CardAtlas(29128, 14)
CardAtlas_15 = ItemUserClass.CardAtlas(29129, 15)
CardAtlas_16 = ItemUserClass.CardAtlas(29130, 16)
CardAtlas_17 = ItemUserClass.CardAtlas(29131, 17)
CardAtlas_18 = ItemUserClass.CardAtlas(29132, 18)
CardAtlas_19 = ItemUserClass.CardAtlas(29133, 19)
CardAtlas_20 = ItemUserClass.CardAtlas(29134, 20)
CardAtlas_21 = ItemUserClass.CardAtlas(29135, 21)
CardAtlas_22 = ItemUserClass.CardAtlas(29136, 22)
CardAtlas_23 = ItemUserClass.CardAtlas(29137, 23)
CardAtlas_24 = ItemUserClass.CardAtlas(29138, 24)
CardAtlas_25 = ItemUserClass.CardAtlas(29139, 25)
CardAtlas_26 = ItemUserClass.CardAtlas(29140, 26)
CardAtlas_27 = ItemUserClass.CardAtlas(29141, 27)
CardAtlas_28 = ItemUserClass.CardAtlas(29142, 28)
CardAtlas_29 = ItemUserClass.CardAtlas(29143, 29)
CardAtlas_30 = ItemUserClass.CardAtlas(29144, 30)
CardAtlas_31 = ItemUserClass.CardAtlas(29145, 31)
CardAtlas_32 = ItemUserClass.CardAtlas(29146, 32)
CardAtlas_33 = ItemUserClass.CardAtlas(29147, 33)
CardAtlas_34 = ItemUserClass.CardAtlas(29148, 34)
CardAtlas_35 = ItemUserClass.CardAtlas(29149, 35)
CardAtlas_36 = ItemUserClass.CardAtlas(29150, 36)
CardAtlas_37 = ItemUserClass.CardAtlas(29151, 37)
CardAtlas_38 = ItemUserClass.CardAtlas(29152, 38)
CardAtlas_39 = ItemUserClass.CardAtlas(29153, 39)
CardAtlas_40 = ItemUserClass.CardAtlas(29154, 40)
CardAtlas_41 = ItemUserClass.CardAtlas(29155, 41)
CardAtlas_42 = ItemUserClass.CardAtlas(29156, 42)
CardAtlas_43 = ItemUserClass.CardAtlas(29157, 43)
CardAtlas_44 = ItemUserClass.CardAtlas(29158, 44)
CardAtlas_45 = ItemUserClass.CardAtlas(29159, 45)
CardAtlas_46 = ItemUserClass.CardAtlas(29160, 46)
CardAtlas_47 = ItemUserClass.CardAtlas(29161, 47)
CardAtlas_48 = ItemUserClass.CardAtlas(29162, 48)
CardAtlas_49 = ItemUserClass.CardAtlas(29163, 49)
CardAtlas_50 = ItemUserClass.CardAtlas(29164, 50)
CardAtlas_51 = ItemUserClass.CardAtlas(29165, 51)
CardAtlas_52 = ItemUserClass.CardAtlas(29166, 52)
CardAtlas_53 = ItemUserClass.CardAtlas(29167, 53)
CardAtlas_54 = ItemUserClass.CardAtlas(29168, 54)
CardAtlas_55 = ItemUserClass.CardAtlas(29169, 55)
CardAtlas_56 = ItemUserClass.CardAtlas(29170, 56)
CardAtlas_57 = ItemUserClass.CardAtlas(29171, 57)
CardAtlas_58 = ItemUserClass.CardAtlas(29172, 58)
CardAtlas_59 = ItemUserClass.CardAtlas(29173, 59)
CardAtlas_60 = ItemUserClass.CardAtlas(29174, 60)
CardAtlas_61 = ItemUserClass.CardAtlas(29175, 61)
CardAtlas_62 = ItemUserClass.CardAtlas(29176, 62)
CardAtlas_63 = ItemUserClass.CardAtlas(29177, 63)
CardAtlas_64 = ItemUserClass.CardAtlas(29178, 64)
CardAtlas_65 = ItemUserClass.CardAtlas(29179, 65)
CardAtlas_66 = ItemUserClass.CardAtlas(29180, 66)
CardAtlas_67 = ItemUserClass.CardAtlas(29181, 67)
CardAtlas_68 = ItemUserClass.CardAtlas(29182, 68)
CardAtlas_69 = ItemUserClass.CardAtlas(29183, 69)
CardAtlas_70 = ItemUserClass.CardAtlas(29184, 70)
CardAtlas_71 = ItemUserClass.CardAtlas(29185, 71)
CardAtlas_72 = ItemUserClass.CardAtlas(29186, 72)
CardAtlas_73 = ItemUserClass.CardAtlas(29187, 73)
CardAtlas_74 = ItemUserClass.CardAtlas(29188, 74)
CardAtlas_75 = ItemUserClass.CardAtlas(29189, 75)
CardAtlas_76 = ItemUserClass.CardAtlas(29190, 76)
CardAtlas_77 = ItemUserClass.CardAtlas(29191, 77)
CardAtlas_78 = ItemUserClass.CardAtlas(29192, 78)
CardAtlas_79 = ItemUserClass.CardAtlas(29193, 79)
CardAtlas_80 = ItemUserClass.CardAtlas(29194, 80)
CardAtlas_81 = ItemUserClass.CardAtlas(29195, 81)
CardAtlas_82 = ItemUserClass.CardAtlas(29196, 82)
CardAtlas_83 = ItemUserClass.CardAtlas(29197, 83)
CardAtlas_84 = ItemUserClass.CardAtlas(29198, 84)
CardAtlas_85 = ItemUserClass.CardAtlas(29199, 85)
CardAtlas_86 = ItemUserClass.CardAtlas(29200, 86)
CardAtlas_87 = ItemUserClass.CardAtlas(29201, 87)
CardAtlas_88 = ItemUserClass.CardAtlas(29202, 88)
CardAtlas_89 = ItemUserClass.CardAtlas(29203, 89)
CardAtlas_90 = ItemUserClass.CardAtlas(29204, 90)
CardAtlas_91 = ItemUserClass.CardAtlas(29205, 91)
CardAtlas_92 = ItemUserClass.CardAtlas(29206, 92)
CardAtlas_93 = ItemUserClass.CardAtlas(29207, 93)
CardAtlas_94 = ItemUserClass.CardAtlas(29208, 94)
CardAtlas_95 = ItemUserClass.CardAtlas(29209, 95)
CardAtlas_96 = ItemUserClass.CardAtlas(29210, 96)
CardAtlas_97 = ItemUserClass.CardAtlas(29211, 97)
CardAtlas_98 = ItemUserClass.CardAtlas(29212, 98)
CardAtlas_99 = ItemUserClass.CardAtlas(29213, 99)
CardAtlas_100 = ItemUserClass.CardAtlas(29214, 100)
CardAtlas_101 = ItemUserClass.CardAtlas(29280, 101)
CardAtlas_102 = ItemUserClass.CardAtlas(29281, 102)
CardAtlas_103 = ItemUserClass.CardAtlas(29282, 103)
CardAtlas_104 = ItemUserClass.CardAtlas(29283, 104)
CardAtlas_105 = ItemUserClass.CardAtlas(29284, 105)
CardAtlas_106 = ItemUserClass.CardAtlas(29285, 106)
CardAtlas_107 = ItemUserClass.CardAtlas(29286, 107)
CardAtlas_108 = ItemUserClass.CardAtlas(29287, 108)
CardAtlas_109 = ItemUserClass.CardAtlas(29288, 109)
CardAtlas_110 = ItemUserClass.CardAtlas(29289, 110)
CardAtlas_111 = ItemUserClass.CardAtlas(29290, 111)
CardAtlas_112 = ItemUserClass.CardAtlas(29291, 112)
CardAtlas_113 = ItemUserClass.CardAtlas(29292, 113)
CardAtlas_114 = ItemUserClass.CardAtlas(29293, 114)
CardAtlas_115 = ItemUserClass.CardAtlas(29294, 115)
CardAtlas_116 = ItemUserClass.CardAtlas(29295, 116)
CardAtlas_117 = ItemUserClass.CardAtlas(29296, 117)
CardAtlas_118 = ItemUserClass.CardAtlas(29297, 118)
CardAtlas_119 = ItemUserClass.CardAtlas(29298, 119)
CardAtlas_120 = ItemUserClass.CardAtlas(29299, 120)
CardAtlas_121 = ItemUserClass.CardAtlas(29300, 121)
CardAtlas_122 = ItemUserClass.CardAtlas(29301, 122)
CardAtlas_123 = ItemUserClass.CardAtlas(29302, 123)
CardAtlas_124 = ItemUserClass.CardAtlas(29303, 124)
CardAtlas_125 = ItemUserClass.CardAtlas(29304, 125)
CardAtlas_126 = ItemUserClass.CardAtlas(29305, 126)
CardAtlas_127 = ItemUserClass.CardAtlas(29306, 127)
CardAtlas_128 = ItemUserClass.CardAtlas(29307, 128)
CardAtlas_129 = ItemUserClass.CardAtlas(29308, 129)
CardAtlas_130 = ItemUserClass.CardAtlas(29309, 130)
CardAtlas_131 = ItemUserClass.CardAtlas(29310, 131)
CardAtlas_132 = ItemUserClass.CardAtlas(29311, 132)
CardAtlas_133 = ItemUserClass.CardAtlas(29312, 133)
CardAtlas_134 = ItemUserClass.CardAtlas(29313, 134)
CardAtlas_135 = ItemUserClass.CardAtlas(29314, 135)
CardAtlas_136 = ItemUserClass.CardAtlas(29315, 136)
CardAtlas_137 = ItemUserClass.CardAtlas(29316, 137)
CardAtlas_138 = ItemUserClass.CardAtlas(29317, 138)
CardAtlas_139 = ItemUserClass.CardAtlas(29318, 139)
CardAtlas_140 = ItemUserClass.CardAtlas(29319, 140)


#(道具coding, 使用获得卡牌碎片)
CardAtlasChip_1 = ItemUserClass.CardAtlasChip(29114, 1)

#(使用coding,[(获得数量， 概率)])
PigAmounts = ItemUserClass.NewYearPigAmount(29327,[(1,1000),(2,1000),(3,1000),(4,1000),(5,1000),(6,1000),(7,1000),(8,1000)])


#圣印历练值 -- (道具coding, 获得历练值)
SealLilian_1 = ItemUserClass.ItemAddSealLiLian(29375, 100)


#元素幻化道具 (coding,visionId) -- (道具coding,解锁幻化Id)
ElementVisionItem_1 = ItemUserClass.ElementVisionItem(29464, 1)


CollectFightWord_1 = ItemUserClass.ItemAddCollectWord(29465, 1)
CollectFightWord_2 = ItemUserClass.ItemAddCollectWord(29466, 2)
CollectFightWord_3 = ItemUserClass.ItemAddCollectWord(29467, 3)
CollectFightWord_4 = ItemUserClass.ItemAddCollectWord(29468, 4)
CollectFightWord_5 = ItemUserClass.ItemAddCollectWord(29469, 5)

#增加指定等级的英雄，coding, 英雄ID， 等级
#ItemUserClass.ItemAddHeroByLevel(29469,20,100)
ItemUserClass.ItemAddHeroByLevel(29495,173,130)
