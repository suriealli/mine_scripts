#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Common.Other.GlobalPrompt")
#===============================================================================
# 全局提示
#===============================================================================
import random

#===============================================================================
#常用奖励提示头
#===============================================================================
SubTask_Reward = 	"奖励内容:#H"				#支线奖励
Reward_Tips = 		"恭喜你获得:#H"			#恭喜奖励
Reward_Item_Tips = 	"你获得了：#Z(%s,%s)"		#物品获得
Item_Use_Tips = 	"使用成功 #H 获得了：#H"		#物品使用
#===============================================================================
#常用奖励提示
#===============================================================================
Exp_Tips = 			"经验 +%s#H"
Money_Tips = 		"金币 +%s#H"
BindRMB_Tips = 		"魔晶 +%s#H"
TiLi_Tips = 		"体力 +%s#H"
UnBindRMB_Tips = 	"神石 +%s#H"
Reputation_Tips = 	"声望 +%s#H"
TarotHp_Tips = 		"命力 +%s#H"
DragonSoul_Tips = 	"龙灵 +%s#H"
Qinmi_Tips = 		"亲密+%s#H"
RongYu_Tips = 		"荣誉+%s#H"
GongXun_Tips = 		"功勋+%s#H"
RMB_Tips = 			"神石+%s#H"
KJDExchangeCoin_Tips = "周年纪念币+%s#H"
Item_Tips = 		"#Z(%s,%s)#H"			#物品(coding, cnt)
Item_Tips_1 = 		"#Z(%s,%s)"				#物品(coding, cnt)
Tarot_Tips = 		"#t(#K(sTT,%s,%s))#H"	#命魂(命魂类型, 数量)
UnionExp_Tips = 	"公会经验+%s#H"
UnionResource_Tips = "公会资源+%s#H"
UnionContribution_Tips = "公会贡献+%s#H"
TaortHP_Tips = 		"命力+%s#H"
Talent_Tips = 		"#L(%s,%s)#H"				#天赋卡（天赋卡类型，数量）
Hero_Tips = 		"#Y(%s,%s)#H"				#英雄
LostSceneSocre_Tips = "迷失之境冒险点+%s#H"
Item_Use_Tips_1 = "使用成功 #H 获得了：#H金币 +%s"
Item_Use_Tips_2 = "使用成功 #H 获得了：#H魔晶 +%s"
Item_Use_Tips_3 = "使用成功 #H 获得了：#H神石 +%s"
Item_Use_Tips_4 = "使用成功 #H 获得了：#H体力 +%s"
Item_Use_Tips_5 = "使用成功 #H 获得了：#H命力 +%s"
Item_Use_Tips_6 = "使用成功 #H 获得了：#H#Z(%s,%s)"
Item_Use_Tips_7 = "使用成功 #H 获得了：#H#t(#K(sTT,%s,%s))"
Item_Exchang_Tips = "兑换成功#H"
SendFlower_Tips = "恭喜你获得：#H金币 +%s#H膜拜成功!"

MallBuyOk = "购买成功"


VIPLibaoLevel = "等级不足，到达20级可以领取"

Talent_Libao_Tips = "#C(#00FF00)%s#n使用天赋卡礼包，开出了天赋卡#L(%s,%s)，真是吉星高照，势不可挡啊！"
Talent_Libao_Tips_1 = "#C(#00FF00)%s#n在#C(#EE7600)【十二宫宝箱】#n中开出了天赋卡#L(%s,%s)，真是吉星高照，势不可挡啊！"
Talent_Libao_Tips_2 = "恭喜你获得：#L(%s,%s)#H"

CardAtlas_Tips = "#X(%s, %s)#H"
CardAtlasChip_Tips = "卡牌碎片+%s#H"

#===============================================================================
#常用条件提示
#===============================================================================
TarotIsFull_Tips = "命魂背包空间不足"
PackageIsFull_Tips = "背包剩余空间不足！"
GLOBAL_NotOnlineRole = "该角色不在线或者在跨服中！"
UnbindRMB_Q_NotEnough = "充值神石不足，购买失败"
PackageIsFull_Tips2 = "背包空间不足，请先清理背包！"

TalentIsFull_Tips = "天赋卡背包空间不足"
HeroIsFull_Tips = "英雄位置已满，请先解雇多余的英雄"
CardAtlasFull_Tips = "卡牌图鉴卡牌背包空间不足"
#===============================================================================
#物品
#===============================================================================
PackageFullTitle = "由于您的背包已满"
Sender = "系统"
Content = "你获得了新的物品，由于你当时的背包已满，系统已将物品暂时保存于邮件附件中。请尽快整理您的背包，预留足够的背包格子，并且在7天内提取附件中的物品。"


#===============================================================================
#物品
#===============================================================================
ItemSell_TIPS_3 = "出售成功 ：#H#Z(%s,%s,0)#H金币+%s"
ItemSell_TIPS_4 = "出售成功 ：#H#Z(%s,%s,0)#H获得：#Z(%s,%s)"
ItemSell_TIPS_5 = "出售成功 ：#H#Z(%s,%s,0)#H获得：#H"
ItemSell_TIPS_6 = "#Z(%s,%s)"
ItemSell_TIPS_7 = "金币+ %s"
ItemSell_TIPS_8 = "#Z(%s,%s)#H"
#===============================================================================
#购买体力
#===============================================================================
TiLi_Buy_Tips = "购买成功,获得#C(#00FF00)%s点#n体力"
TiLi_Buy_Times = "购买次数不足"
#===============================================================================
#副本
#===============================================================================
FB_Tips_1 = "请按照顺序击杀怪物哟"
FB_Tips_2 = "#C(#00EE00)%s#n#C(#EE7600)通关神速，第1个通关副本—#C(#00FF00)%s#n,真是战力超群。#n"


#===============================================================================
#英雄
#===============================================================================
HeroDataExcept = "英雄数据异常"
HeroAltar_Change = "兑换成功"
HeroZhaoMuSuccess = "招募成功"
HeroGradeTips_1 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将紫色英雄#C(#FF33CC)%s#n进化为成为橙色英雄#C(#FF6600)%s#n, 这是要称霸全服的节奏啊#n"
HeroGradeTips_2 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将橙色英雄#C(#FF6600)%s#n进化为成为红色英雄#C(#FF0000)%s#n, 这是要称霸全服的节奏啊#n"
HeroUpStar_1 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将3星英雄#C(#FF6600)%s#n进化为成为4星, 这是要称霸全服的节奏啊#n"
HeroUpStar_2 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将4星英雄#C(#FF0000)%s#n进化为成为5星, 这是要称霸全服的节奏啊#n"
HeroUpStar_3 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将5星英雄#C(#FF0000)%s#n进化为成为6星, 这是要称霸全服的节奏啊#n"
HeroUpStar_4 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将6星英雄#C(#FF0000)%s#n进化为成为7星, 这是要称霸全服的节奏啊#n"
HeroUpStar_5 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻, 终于将7星英雄#C(#FF0000)%s#n进化为成为8星, 这是要称霸全服的节奏啊#n"
HeroFire_Tips = "解雇成功：#H#Z(%s,%s)"
HeroAltar_AddHero_Tips_1 = "#C(#ffffff)#U#A(#K(playerMenu,%s,%s,%s,TYPE8,%s,0,%s,%s))#C(#0099cc)%s#n#n#n在#C(#0099cc)[%s]#n幸运召唤到[#C(#FF33CC)%s#n]前来效力, 这是要称霸全服的节奏啊。"
HeroAltar_AddHero_Tips_2 = "#C(#ffffff)#U#A(#K(playerMenu,%s,%s,%s,TYPE8,%s,0,%s,%s))#C(#0099cc)%s#n#n#n在[#C(#0099cc)%s#n]幸运召唤到[#C(#FF33CC)%s#n]和[#C(#FF33CC)%s#n]前来效力, 这是要称霸全服的节奏啊。"
#===============================================================================
# 阵位
#===============================================================================
Station_SuccessIn = "布阵成功"
Station_TypeInStation = "该类型英雄已上阵, 不能助阵"

#===============================================================================
#组队相关
#===============================================================================
TEAM_NOT_EXIST_PROMPT = "队伍不存在"
TEAM_NOT_ONLINE_PROMPT = "该玩家不在线"
TEAM_HAS_TEAM_PROMPT = "对方已经加入队伍"
TEAM_FULL_PROMPT = "该队伍已经满了，无法加入"
TEAM_IN_FIGHT_PROMPT = "队伍已经开始战斗"
TEAM_TransferTeamLeader = "转让队长成功"
#===============================================================================
# 等级礼包
#===============================================================================
NavicePackLessPackage = "您的背包空间不足, 无法领取奖励"
NavicePackEnd = "您的等级礼包已经领取完"

#===============================================================================
# 首充五重礼包奖励
#===============================================================================
FIVEGIFT_HEARSAY_1 = "#C(#ffff37)%s#n成功领取了价值#C(#0DF6FF)888#n神石的首充大礼包"
FIVEGIFT_HEARSAY_2 = "#C(#ffff37)%s#n完成了幸运3重大礼，成功领取了价值#C(#0DF6FF)388#n神石的幸运大礼包"
FIVEGIFT_HEARSAY_3 = "#C(#ffff37)%s#n经过一番努力，提升到了35级，成功领取了价值#C(#0DF6FF)488#n神石的等级大礼包"
FIVEGIFT_HEARSAY_4 = "#C(#ffff37)%s#n通过购买月卡，成功领取了价值#C(#0DF6FF)688#n神石的月卡大礼包"
FIVEGIFT_HEARSAY_5 = "#C(#ffff37)%s#n通过购买超值攻击宝石礼盒，成功领取了价值#C(#0DF6FF)1488#n神石的宝石大礼包"
DAY_FP_REWARD_HEARSAY = "#C(#ffff37)%s#n成功完成了#C(#00EE00)五日首充#n活动，领取了丰富的奖励物品。"
#===============坐骑相关=========================================================
MOUNT_PROMPT_1 = "当前位置不能下坐骑"
MOUNT_PROMPT_2 = "在这里不能骑坐骑"	
SUC_EVOLVE_MSG = "恭喜您坐骑升至%s阶%s星。"
SUC_ADVANCE = "#C(fbfc87)#C(#ffff37)%s#n努力培养坐骑，终于将坐骑进阶至#C(#ffff37)%s#n，真是令人羡慕啊#n。"
MOUNT_EATED_FOOD = "您已使用过该食物"
MOUNT_LIMIT_FOOD = "坐骑等级不足"
MOUNT_FOOD_SUC = "使用成功，坐骑属性永久加成如下:#H物攻:+%s#H法攻: +%s#H生命上限: +%s"
ACTIVE_MOUNT_SUC = "恭喜，激活%s外形成功"
ACTIVE_MOUNT_REPEAT = "已激活过该外形，无需重复激活"
CHANGE_MOUNT_TIME_SUC = "使用成功，您的坐骑#C(#ffff37)%s#n变为永久性坐骑"
CHANGE_MOUNT_TIME_FAILT = "须事先激活过该坐骑外形"
CHANGE_MOUNT_TIME_FAILT_2 = "该坐骑已经是永久坐骑！"
MOUNT_APPERANCE_UP = "进化成功，坐骑品质+1"
MOUNT_MAX_LEVEL = "当前坐骑已满阶满星!"
#===============================================================================
#============宝石相关=================
GEM_NO_HOLE_MSG = "该装备没有镶嵌孔，不能镶嵌"
GEM_SAME_TYPE_MSG = "已经镶嵌了同类型的宝石"
GEM_NO_ENOUGH_MSG = "装备孔数不足，无法进行镶嵌"
GEM_GET_OFF_MSG = "拆卸成功"

#================================================================================
#============英雄竞技=================
JJC_SUCCESS_MSG = "#C(#00FF00)%s#n挑战了你，你获胜了，排名不变"
JJC_FAILURE_MSG = "#C(#00FF00)%s#n挑战了你，你#C(#FF0000)失败#n了，排名跌至#C(#0DF6FF)%s第%s名#n"
JJC_FIRST_HEARSAY = "#C(#66FF00)%s#n#C(#FFFF00)战胜了#n#C(#66FF00)%s#n，#C(#FFFF00)获得了英雄竞技第一名，名震天下#n"


#=============炼金================================================================
GOLD_END_MSG = "这次炼金已结束"
GOLD_INIT_MSG = "你已经在协助队列中"
GOLD_FULL_MSG = "协助人数已满"
GOLD_HELP_SUC_MSG = "协助炼金成功，金币+%s"
GOLD_HELP_SUC_MSG2 = "协助炼金成功，您今日已经没有协助炼金收益次数了。"
GOLD_SUC_MSG = "炼金成功，金币+%s。#H"
GOLD_HELP_LEVEL_MSG = "等级达到30级可协助炼金。"
GOLD_HELP_DESC_MSG = "#C(#EE7600)【炼金】#n#C(#FFFFFF)#C(#00FF00)%s#n玩家开启炼金炉，朋友们快来协助炼金，获取更多的奖励。  #C(#00ff00)#U#A(#K(OPEN_HELP_LIANJIN,%s))立即协助#n#n#n"
#=================================================================================
#=================巨龙宝藏=========================================================
NO_TIMES_FOR_SECRCH_MSG = "你已没有剩余的金锄头，今日无法继续挖宝了。"
NO_TIMES_FOR_BUY_MSG = "今日挖宝次数已用尽，请明日继续。"
FRESH_EVENT_MSG = "当前地图中拥有当前特殊事件的下一张地图，是否确定刷新？"
DIG_REWARD_MSG = "#C(#E87D22)%s#n在巨龙宝藏探险中，寻得%s魔晶。"
DRAGON_REWARD_MSG1 = "恭喜你获得:魔晶+ %s"
DRAGON_REWARD_MSG2 = "恭喜你获得:经验+ %s"
DRAGON_REWARD_MSG3 = "恭喜你获得:金币+ %s"
DRAGON_REWARD_MSG4 = "恭喜你获得:金锄头+1"
DRAGON_REWARD_MSG5 = "恭喜你获得:幸运挖宝次数+1"
DRAGON_REWARD_MSG6 = "恭喜你获得:#H#Z(%s,%s)"
DRAGON_LUCKY_DIG_MSG = "每次挖宝仅可使用一次幸运挖宝"
#===============================================================================
# 公会
#===============================================================================
#============公会提示=================
UNION_CREATE_NO_NAME_PROMPT = "请输入公会名称"
UNION_CREATE_NO_RMB_PROMPT = "神石不足"
UNION_CREATE_SUCCESS_PROMPT = "恭喜你成功创建了公会，快前往邀请朋友加入吧。"
UNION_JOB_UP_FULL_PROMPT = "上一级职位已满，请先调整。"
UNION_JOB_DOWN_FULL_PROMPT = "下一级职位已满，请先调整。"
UNION_NAME_REPEAT = "这个公会名字已被占用。"
UNION_QQ_NOT_LOGIN = "当前无法连接至游戏平台，请刷新页面或者重新登录游戏后再试。"
UNION_HAS_JOIN_IN_UNION = "该玩家已加入其它公会"
UNION_MEMBER_FULL = "公会人数已达上限，请提升公会等级或者先清理人数"
UNION_ROLE_OFFLINE = "该玩家已离线。"
UNION_APPLY_ERROR = "对方已撤销公会申请。"
UNION_FB_NO_COST = "你选择不消耗行动力进行挑战#H战斗不会获得奖励，且不增加占领度。"
UNION_CLEAR_JOIN_CD = "现在您可以申请公会，请申请吧"
UNION_ACT_CANT_QUIT = "在20:00-22:00期间，无法退出公会！"
UNION_GOD_CANT_CHALLENGE = "在23:55-24:00为结算时间，请明日再挑战！"
UNION_TASK_NO_HELP_CNT = "今日已经没有提星次数"
UNION_TASK_STAR_FULL = "任务已满星，提星失败"
UNION_TASK_UPGRADE_SUCCESS = "任务提星成功"
UNION_TASK_HAS_HELPED = "您已对该任务进行过提星"
UNION_TASK_WHO_HELP_YOU = "#C(#00FF00)%s#n将您的任务提至#C(#fbfe00)%s#n星"
UNION_TASK_FINISHED_HELP_FAIL = "任务已完成，协助失败"
UNION_CANT_USE_ITEM = "您没有公会，不能使用该道具"
UNION_FB_INVITE_SUBSTITUTE = "【公会副本—替身组队】#C(#00FF00)%s#n正在和您的替身组队"
#============公会頻道=================
UNION_JOIN_WELCOME_MSG = "欢迎#C(#fefb00)%s#n加入公会。"
UNION_PRESIDENT_TRANSFER_MSG = "恭喜#C(#fefb00)%s#n成为新任会长！"
UNION_GOD_FIRST_KILL_MSG = "本公会#C(#fefb00)%s#n首个通关公会魔神第#C(#fefb00)%s#n关。"
UNION_OPEN_TREASURE_GOLD_MSG = "公会富豪#C(#FFFF00)%s#n为大家开启了#C(#FF6600)金宝箱#n，大家快去夺取吧！#C(#00ff00)#U#A(#K(GHDB))前往夺宝#n#n#n"
UNION_OPEN_TREASURE_SILVER_MSG = "公会富豪#C(#FFFF00)%s#n为大家开启了#C(#FF6600)银宝箱#n，大家快去夺取吧！#C(#00ff00)#U#A(#K(GHDB))前往夺宝#n#n#n"
UNION_OPEN_TREASURE_COPPER_MSG = "公会富豪#C(#FFFF00)%s#n为大家开启了#C(#FF6600)铜宝箱#n，大家快去夺取吧！#C(#00ff00)#U#A(#K(GHDB))前往夺宝#n#n#n"
UNION_DONATE_MSG = "#C(#FEFB00)%s#n一掷千金，捐献了#C(#FEFB00)%s#n神石，公会资源增加#C(#00FF00)%s#n，个人贡献增加#C(#00FF00)%s#n"
UNION_TASK_INVITE_MSG = "#C(#EE7600)【公会任务】#n#C(#FFFFFF)#C(#00FF00)%s#n玩家接取了一个公会任务，完成后可以大大增加公会资源，大家快来帮他提星吧。 #C(#00ff00)#U#A(#K(helpUpStar,%s))立即协助#n#n#n"
#============公会廣播=================
UNION_GOD_FIRST_KILL_NEWS = "本公会#C(#fefb00)%s#n首个通关公会魔神第#C(#fefb00)%s#n关。"
UNION_OPEN_TREASURE_GOLD_NEWS = "富豪#C(#fefb00)%s#n开启了#C(#FF6600)金宝箱#n。"
UNION_OPEN_TREASURE_SILVER_NEWS = "富豪#C(#fefb00)%s#n开启了#C(#FF6600)银宝箱#n。"
UNION_OPEN_TREASURE_COPPER_NEWS = "富豪#C(#fefb00)%s#n开启了#C(#FF6600)铜宝箱#n。"
#============公会邮件=================
UNION_CHANGE_NAME_TITLE = "【公会改名】系统通知"
UNION_CHANGE_NAME_SENDER = "系统"
UNION_CHANGE_NAME_MAIL = "会长#C(#66FF00)%s#n已经更改公会名为#C(#FFFF00)%s#n，请大家继续努力，共同建设公会"
#============公会解散邮件=================
UnionDismissTitle = "公会自动解散说明"
UnionDismissSender = "系统"
UnionDismissCotent = "亲爱的龙骑士，您所在的【%s】公会由于连续7日新增公会资源不足%s，公会已自动解散。若您之前不在【%s】公会中，请忽略此邮件。"
#============公会解散警告邮件=================
UnionDismissWarnTitle = "公会自动解散警告"
UnionDismissWarnSender = "系统"
UnionDismissWarnCotent = "亲爱的龙骑士，您所在的【%s】公会昨日新增公会资源不足%s。若连续7天增加的资源小于%s，公会将被强制解散。目前是第%s天。若您已不在【%s】公会中请忽略此邮件。"
UnionCntMaxTips = "公会数量已达上限，无法创建新公会，请选择其他公会加入。"
#============公会红包=================
UnionHongBaoTitle = "公会红包过期返还"
UnionHongBaoCotent = "亲爱的龙骑士，您发放的公会红包已过期，现将未领取的神石数量以奖励神石返还。请注意查收。"
UnionHongBaoSet_Tip = "#C(#EE7600)【公会红包】#n#C(#00FF00)%s#n发放了一个公会红包#n#C(#FF0000)【%s】#n #U#C(#00ff00)#A(#K(dlg,OPEN_UNION_RED_POCKET_VIEW_FROM_CHAT))查看红包"
UnionHongBaoGet_Tip_1 = "#C(#EE7600)【公会红包】#n#C(#00FF00)%s#n领取了#C(#00FF00)%s#n的红包 #n #U#C(#00ff00)#A(#K(dlg,OPEN_UNION_RED_POCKET_VIEW_FROM_CHAT))我也要抢"
UnionHongBaoGet_Tip_2 = "#C(#EE7600)【公会红包】#n#C(#00FF00)%s#n以极快的手速领取了#C(#00FF00)%s#n的红包#n #U#C(#00ff00)#A(#K(dlg,OPEN_UNION_RED_POCKET_VIEW_FROM_CHAT))我也要抢"
UnionHongBaoGet_Tip_3 = "#C(#EE7600)【公会红包】#n#C(#00FF00)%s#n伸手拿走了红包并高兴地对#C(#00FF00)%s#n说：“谢谢老板”#n #U#C(#00ff00)#A(#K(dlg,OPEN_UNION_RED_POCKET_VIEW_FROM_CHAT))我也要抢"
UnionHongBaoGet_Tip_4 = "#C(#EE7600)【公会红包】#n#C(#00FF00)%s#n以迅雷不及掩耳之势抢了#C(#00FF00)%s#n的一个红包，心里乐开了花#n #U#C(#00ff00)#A(#K(dlg,OPEN_UNION_RED_POCKET_VIEW_FROM_CHAT))我也要抢"
UnionHongBaoGet_Tip_5 = "#C(#EE7600)【公会红包】#n#C(#00FF00)%s#n抱起了#C(#00FF00)%s#n原地转了150个圈，趁着老板晕眩时，立即抢到了一个红包#n #U#C(#00ff00)#A(#K(dlg,OPEN_UNION_RED_POCKET_VIEW_FROM_CHAT))我也要抢"
def GetHongBaoTip():
	return random.choice((UnionHongBaoGet_Tip_1, UnionHongBaoGet_Tip_2, UnionHongBaoGet_Tip_3, UnionHongBaoGet_Tip_4, UnionHongBaoGet_Tip_5))
UnionHongBaoOutData = "该红包已经过期，已经被系统回收！"
#============内部使用的公会红包道具==============
UnionHongBaoUseCntError = "公会红包道具使用成功"
UnionHongBaoMessage = "恭喜发财，大吉大利！"

#===============================================================================
# 地精宝库
#===============================================================================
GT_Begin_Tips = "#C(#EE7600)【劫宝】神秘的地精族人带着稀世珍宝行走在#C(#00FF00)%s、%s，#n只有智勇双全的勇士们才有实力劫得珍宝。勇士你还等什么？夺得圣灵碎片，可兑换惊世奇珍，机不可失！#n"
GT_End_Tips = "#C(#EE7600)神秘的地精族人回到了各自的种族继续准备下一次运宝。#n"
GT_Fight_CD = "战斗冷却中：%s秒"
GT_Rob_Success = "#C(#EE7600)【劫宝】#C(#00EE00)%s#n劫获了#C(#FF0000)%s#n运送的宝物#Z(%s,%s)"
GT_Rob_Name = "劫宝者-"
GT_Open_Tips = "劫宝活动30级开启"
GT_Fly = "前往%s需要等级%s"
GT_Mail_Title = "劫宝奖励"
GT_Mail_Send = "系统"
GT_Mail_Content = "亲爱的玩家：#H    地精宝库的奖励我们已经通过邮件发送给您了。您可以提取附件获得奖励。"
GT_Exchang_S = "兑换成功"
GT_NA_No_Reward_Cnt = "您今日已经成功劫宝4次，请把机会留给其他人吧"
GT_LimitLevel = "等级不足"
#============城主轮值=================
DUKE_PLAYER_LOST = "该玩家已被击败，请选择其他战斗对象"
DUKE_BUFF_MSG = "#C(#00EE00)%s#n公会的#C(#00EE00)%s#n激活了#C(#ffff37)%s#n级神力BUFF"
DUKE_READY_MSG2 = "#C(#EE7600)【城主轮值】#n将于#C(#ffff37)2#n小时后开始，请各公会做好参加准备"
DUKE_READY_MSG1 = "#C(#EE7600)【城主轮值】#n将于#C(#ffff37)1#n小时后开始，请各公会做好参加准备"
DUKE_READY_MSG3 = "#C(#EE7600)【城主轮值】#n将于#C(#ffff37)5#n分钟后开始，请各公会做好参加准备"
DUKE_READY_MSG4 = "#C(#EE7600)【城主轮值】#n将于#C(#ffff37)1#n分钟后开始，各公会可进场提前准备"
DUKE_START_MSG = "#C(#EE7600)【城主轮值】#n活动已经开始，勇士们请速速进入战场"
DUKE_END_MSG1 = "#C(#EE7600)【城主轮值】#n活动已经结束，防守方胜利，获胜公会为#C(#00EE00)%s#n"
DUKE_END_MSG2 = "#C(#EE7600)【城主轮值】#n活动已经结束，攻击方胜利，获胜公会为#C(#00EE00)%s#n"
DUKE_MAIL = "【城主轮值】"
DUKE_MAIL_TITLE = "系统"
DUKE_MAIL_DESC = "你所在的公会获得了参与活动【城主轮值】的资格，请注意准时参加。若你现在退出公会，将失去参加资格。"
DUKE_KILL_FIVE = "#C(#00EE00)%s#n在#C(#EE7600)【城主轮值】#n活动中已经连续击杀#C(#ffff37)5#n人了，真是如妖怪一般的杀戮"
DUKE_KILL_TEN = "#C(#00EE00)%s#n在#C(#EE7600)【城主轮值】#n活动中已经连续击杀#C(#ffff37)10#n人了，围观的小伙伴们都惊呆了"
DUKE_KILL_FIFTEEN = "#C(#00EE00)%s#n在#C(#EE7600)【城主轮值】#n活动中已经连续击杀#C(#ffff37)%s#n人了，地球人已经无法阻挡他了"
DUKE_ON_CD = "冷却中，请稍等。。。"
DUKE_NO_START = "活动还未开启"
DUKE_NO_PER = "您未满足参与该活动的资格"
DUKE_LEADER_NAME = "城主"
DUKE_ATTACK = "攻"
DUKE_DEFENCE = "守"
DUKE_KILLED_MSG = "众寡悬殊，再强的勇士也抵挡不住。#C(#00EE00)%s#n终结了#C(#00EE00)%s#n的#C(#ffff37)%s#n连杀"
DUKE_GAME_OVER = "#C(#EE7600)【城主轮值】#n经过一番苦战，终于连圣城守护神也被击败了，已经没人能阻止他们了！"
DUKE_NOT_JION_MSG = "离开公会24小时内，无法参加城主轮值"
#===============================================================================
# 魔兽入侵
#===============================================================================
DD_READY_HEARSAY_1 = "#C(#EE7600)【魔兽入侵】#n将于10分钟后开启，请各位勇士做好准备"
DD_READY_HEARSAY_2 = "#C(#EE7600)【魔兽入侵】#n将于1分钟后开启，勇士们可以进场提前做好活动准备"
DD_START_HEARSAY = "#C(#EE7600)【魔兽入侵】#n已经开启，勇士们请速速进入战场"
DD_END_HEARSAY = "#C(#EE7600)【魔兽入侵】#n活动已经结束，经过勇士们的浴血奋战，圣辉城成功的抵挡住了魔兽的入侵"
DD_RANK_FIRST_HEARSAY = "#C(#EE7600)【魔兽入侵】#n当前伤害排名#C(#ffff37)第1#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)%s#n。活动结束后与#C(#ffff37)第1名#n相同公会的玩家将会获得丰厚奖励"
DD_RANK_SECOND_HEARSAY = "#C(#EE7600)【魔兽入侵】#n当前伤害排名#C(#ffff37)第2#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)%s#n。活动结束后与#C(#ffff37)第2名#n相同公会的玩家将会获得丰厚奖励"
DD_RANK_THIRD_HEARSAY = "#C(#EE7600)【魔兽入侵】#n当前伤害排名#C(#ffff37)第3#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)%s#n。活动结束后与#C(#ffff37)第3名#n相同公会的玩家将会获得丰厚奖励"
DD_RANK_FIRST_NO_UNION_HEARSAY = "#C(#EE7600)【魔兽入侵】#n当前伤害排名#C(#ffff37)第1#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)无#n。"
DD_RANK_SECOND_NO_UNION_HEARSAY = "#C(#EE7600)【魔兽入侵】#n当前伤害排名#C(#ffff37)第2#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)无#n。"
DD_RANK_THIRD_NO_UNION_HEARSAY = "#C(#EE7600)【魔兽入侵】#n当前伤害排名#C(#ffff37)第3#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)无#n。"
DD_HAS_GET_REWARD_PROMPT = "您今天已经参与过1次魔兽入侵，每天只能参与1次。"
#===============================================================================
# 魔龙降临
#===============================================================================
MD_READY_HEARSAY_1 = "#C(#EE7600)【魔龙降临】#n魔龙将于10分钟后降临，请各位勇士做好准备"
MD_READY_HEARSAY_2 = "#C(#EE7600)【魔龙降临】#n魔龙将于1分钟后降临，请各位勇士做好准备"
MD_START_HEARSAY = "#C(#EE7600)【魔龙降临】#n已经开启，勇士们请速速进入战场"
MD_END_HEARSAY = "#C(#EE7600)【魔龙降临】#n活动已经结束，经过勇士们的浴血奋战，圣辉城成功的抵挡住了邪恶的魔龙"
MD_RANK_FIRST_HEARSAY = "#C(#EE7600)【魔龙降临】#n当前伤害排名#C(#ffff37)第1#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)%s#n。活动结束后与#C(#ffff37)第1名#n相同公会的玩家将会获得丰厚奖励"
MD_RANK_SECOND_HEARSAY = "#C(#EE7600)【魔龙降临】#n当前伤害排名#C(#ffff37)第2#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)%s#n。活动结束后与#C(#ffff37)第2名#n相同公会的玩家将会获得丰厚奖励"
MD_RANK_THIRD_HEARSAY = "#C(#EE7600)【魔龙降临】#n当前伤害排名#C(#ffff37)第3#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)%s#n。活动结束后与#C(#ffff37)第3名#n相同公会的玩家将会获得丰厚奖励"
MD_RANK_FIRST_NO_UNION_HEARSAY = "#C(#EE7600)【魔龙降临】#n当前伤害排名#C(#ffff37)第1#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)无#n。"
MD_RANK_SECOND_NO_UNION_HEARSAY = "#C(#EE7600)【魔龙降临】#n当前伤害排名#C(#ffff37)第2#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)无#n。"
MD_RANK_THIRD_NO_UNION_HEARSAY = "#C(#EE7600)【魔龙降临】#n当前伤害排名#C(#ffff37)第3#n：#C(#00EE00)%s#n, 公会：#C(#00EE00)无#n。"
#MD_HAS_GET_REWARD_PROMPT = "您今天已经参与过1次魔兽降临，每天只能参与1次。"
#===============================================================================
# 会员
#===============================================================================
Card_Award = "魔晶 + %s"
Card_Give = "赠送成功"
Card_Revive = "你收到来自#C(#00EE00)%s#n赠送的尊贵#C(#00EE00)%s"
CardWeek = "周卡"
CardMonth = "月卡"
CardHalfYear = "半年卡"
CardReviveMail_Title = "您收到赠送卡片"
CardReviveMail_Sender = "系统"
VIP_TIPS = "#C(#00FF00)%s#n贵族等级提升至#C(#00FF00)%s#n级，获得更多优惠，这是要制霸全服啊"
Card_GoldBuff_Tips = "您是半年卡玩家, 您获得了额外10%的金币加成#H"
def ReturnCardName(cardID):
	CardNameDict = {1:CardWeek, 2:CardMonth, 3:CardHalfYear}
	if cardID not in CardNameDict:
		return
	else:
		return CardNameDict[cardID]
CardWeekBuy = "#C(#E87D22)【月卡】#n #C(#00FF00)%s#n购买了周卡，魔晶每日领，轻松遨龙骑！"
CardMonthBuy = "#C(#E87D22)【月卡】#n #C(#00FF00)%s#n购买了月卡，魔晶不用愁，CD不用等，瞬间高富帅！"
CardHalfYearBuy = "#C(#E87D22)【月卡】#n #C(#00FF00)%s#n购买了半年卡，魔晶天天领，金币滚滚来，会当凌绝顶，一览众山小！"
def ReturnBuyCardTips(cardID):
	BuyCardTipsDict = {1:CardWeekBuy, 2:CardMonthBuy, 3:CardHalfYearBuy}
	return BuyCardTipsDict.get(cardID)
#===============================================================================
# 心魔炼狱
#===============================================================================
Purgatory_Revive_Success = "领取成功：#H"
Purgatory_Fuhuo_Success = "复活成功"
#===============================================================================
# 答题
#===============================================================================
QandA_READY_BROADCAST_5 = "#C(#00FF00)【答题】#n答题活动将在五分钟后正式开始。"
QandA_READY_BROADCAST_1 = "#C(#00FF00)【答题】#n即将开始答题活动，龙骑士们请做好准备。"
QandA_READY_BROADCAST_0 = "#C(#00FF00)【答题】#n答题活动正式开始！"
QandA_READY_BROADCAST_last = "#C(#00FF00)【答题】#n现在是答题最后一题了！"
QandA_Mail_Title = "由于你的背包已满"
QandA_Mail_Send = "系统"
QandA_Mail_Content = "亲爱的玩家：#H    您的背包已满，答题的奖励我们已经通过邮件发送给您了。您可以先整理背包，然后提取附件获得奖励。"
QandA_Has_Join = "您今天已经参与过1次答题，每天只能参与1次。"
#=================精彩活动==========================
WONDERFUL_TIME_LESS = "活动没开启"
WONDERFUL_TIME_OUT = "活动已结束"
WONDERFUL_GET_REWARD = "#C(#00EE00)%s#n领取了#Z(%s,%s)，感谢玩家#C(#00EE00)%s#n对大家做出的贡献。"
WONDERFUL_NO_TIMES = "已没剩余次数可以领取"
ADD_HERO_MSG = "获得：#C(##FF33CC)%s×1"
FULL_HERO_MSG = "英雄位置已满，请先解雇多余的英雄再来领取"
WONDERFUL_ONCE_RMB_MAIL_TITLE = "单笔充值返利"
WONDERFUL_ONCE_RMB_MAIL_SENDER = "系统"
WONDERFUL_ONCE_RMB_MAIL_CONTENT = "亲爱的玩家：#H    您在%s充值了%s神石，获取了对应单笔充值活动的奖励，请注意查收！"
#===============================================================================
# 翅膀
#===============================================================================
WING_LIBAO_PROMPT = "成功开启首充羽翼礼盒，获得【白色恋人】羽翼"
WING_TRAIN_PROMPT = "培养成功，获得%s经验。"
WING_ADVANCED_TRAIN_PROMPT = "培养成功，共%s次暴击，共获得%s经验。"

#===============================================================================
# 在线奖励
#===============================================================================
OnLineReward_PackageSize_warning = "您的背包空间不足, 无法领取奖励"
OnLineRewardMsg_Head = "恭喜你获得#H"
OnLineRewardMsg_RMB = "魔晶+ %s#H"
OnLineRewardMsg_Money = "金币+ %s#H"
OnLineRewardMsg_Item = "#Z(%s,%s)#H"
#===============================================================================
# 荣耀之战
#===============================================================================
GloryWar_CampName_1 = "烈阳城"
GloryWar_CampName_2 = "暗月郡"
GloryWar_FightTips_1 = "你攻击了%s, 你胜利了，获得%s积分"
GloryWar_FightTips_2 = "你攻击了%s, 你战败了，获得3积分"
GloryWar_FightTips_3 = "%s攻击了你, 你胜利了，获得了%s积分"
GloryWar_FightTips_4 = "%s攻击了你, 你战败了，获得了3积分"
GloryWar_TenMinuteReady = "#C(#EE7600)【荣耀之战】#n将于5分钟后开始, 请各位勇士做好准备"
GloryWar_OneMinuteReady = "#C(#EE7600)【荣耀之战】#n将于1分钟后开始, 各位勇士可以提前入场准备了"
GloryWar_PvpBegin = "#C(#EE7600)【荣耀之战】#n已经开始, 勇士们请速速进入战场"
GloryWar_PveBegin = "#C(#00EE00)魔兽将领#n突袭营地, 请勇士们速速返回营地救援"
GloryWar_End = "魔兽将领的突袭已被击退, 本次#C(#EE7600)【荣耀之战】#n活动结束。"
GloryWar_OwnCD = "你正在战斗冷却时间中, 请稍后再进行挑战"
GloryWar_OtherCD = "该玩家当前不可以挑战, 请先挑战其他玩家"
GloryWar_EightKill = "#C(#00EE00)%s#n已经连续击杀#C(#ffff37)%s#n人了！真可谓是勇冠三军！"
GloryWar_FifteenKill = "#C(#00EE00)%s#n已经连续击杀#C(#ffff37)15#n人了！新一代的战神就此出现了！"
GloryWar_TwentyKill = "#C(#00EE00)%s#n已经连续击杀#C(#ffff37)%s#n人了！战场上还有人能阻挡他吗？？"
GloryWar_EndKill = "双拳难敌四手，好汉也怕人多，#C(#00EE00)%s#n终结#C(#00EE00)%s#n的#C(#ffff37)%s#n连杀"
GloryWar_KillNpc_1 = "#C(#EE7600)【%s】#n阵营的#C(#00EE00)【%s】#n公会的#C(#00EE00)【%s】#n成功击败了【%s】！#C(#EE7600)【%s】#n阵营的玩家攻击它时将会获得强力BUFF！！"
GloryWar_KillNpc_2 = "#C(#EE7600)【%s】#n阵营的#C(#00EE00)【%s】#n成功击败了【%s】！#C(#EE7600)【%s】#n阵营的玩家攻击它时将会获得强力BUFF！！"
GloryWar_Mail_Title = "【荣耀之战】"
GloryWar_Mail_Send = "系统"
GloryWar_Mail_Content = "亲爱的玩家：#H    您的背包已满，荣耀之战的奖励我们已经通过邮件发送给您了。您可以先整理背包，然后提取附件获得奖励"
GloryWar_CampWin = "胜利"
GloryWar_CampFail = "失败"
GloryWar_Has_Join = "您今天已经参与过1次荣耀之战，每天只能参与1次。"
#===============================================================================
# 符文宝轮
#===============================================================================
RuneWheel_Once = "[#C(#00FF00)%s#n]获得 #C(#0DF6FF)%s#n种相同符文，获得 【#C(#0DF6FF)%s#n】 倍奖励 "
RuneWheel_Fiftyth = "[#C(#00FF00)%s#n]开启了#C(#0DF6FF)50#n次符文宝轮，获得【#C(#0DF6FF)1#n】倍奖励#C(#0DF6FF)%s#n次，【#C(#0DF6FF)6#n】倍奖励#C(#0DF6FF)%s#n次，【#C(#0DF6FF)30#n】倍奖励#C(#0DF6FF)%s#n次"
#===============================================================================
# 幸运转盘
#===============================================================================
LuckTurntable_award = "玩家#C(#00FF00)%s#n人品大爆发，在幸运转转乐中获得#C(#0DF6FF)%s#n神石奖励"
LuckTurntable_RMB_award = "恭喜获得： 神石 +%s"
LuckTurntable_Item_award = "恭喜获得： #Z(%s,%s)"
#===============================================================================
# 冲级排名
#===============================================================================
RUSH_LEVEL_GET_REWARD_PROMPT = "领取成功：#H"
RUSH_LEVEL_TOP_HEARSAY = "冲级竞技活动完美结束，#C(#00FF00)%s#n力压全服，获得丰厚奖励"
#===============================================================================
# 装备强化
#===============================================================================
EQUIPMENT_STRENG_MSG = "双倍强化"
#繁体一键强化提示
EQUIPMENT_OnekeySTRENG_MSG1 = "金币不足，本次强化出现双倍强化%s次。"
EQUIPMENT_OnekeySTRENG_MSG2 = "强化等级不能高于角色等级，本次强化出现双倍强化%s次."
EQUIPMENT_OnekeySTRENG_MSG3 = "金币不足"
EQUIPMENT_OnekeySTRENG_MSG4 = "强化等级不能高于角色等级"
UpGradeEquipment_Failt = "英雄等级不足"
#===============================================================================
# 英灵神殿
#===============================================================================
HeroTemple_Mail_Title = "背包空间不足"
HeroTemple_Mail_Sender = "系统"
HeroTemple_Mail_Content = "你的背包空间不足，已将本次英灵神殿获得的奖励通过邮件发放。请您及时提取。"
HeroTemple_First = "#C(#00EE00)%s#n率先通关了英灵神殿的#C(#ffff37)%s[%s]#n！所谓兵贵神速啊！"
HeroTemple_Fast = "#C(#00EE00)%s#n仅用#C(#00EE00)%s#n回合便通关了英灵神殿的#C(#ffff37)%s[%s]#n！还有更快的吗？"

HeroTemple_LevelLimit = "等级不足，该副本尚未开启"

HT_1 = "少将"
HT_2 = "中将"
HT_3 = "上将"
HT_4 = "大将"
HT_5 = "元帅"

def Return_GuanqiaName(stageId):
	HeroTemple_GuanqiaName = {1:HT_1, 2:HT_2, 3:HT_3, 4:HT_4, 5:HT_5}
	if stageId not in  HeroTemple_GuanqiaName:
		return
	else:
		return HeroTemple_GuanqiaName[stageId]
	
#===============================================================================
# 英雄圣殿
#===============================================================================
HeroShengdian_Mail_Title = "背包空间不足"
HeroShengdian_Mail_Sender = "系统"
HeroShengdian_Mail_Content = "你的背包空间不足，已将本次英雄圣殿获得的奖励通过邮件发放。请您及时提取。"
HeroShengdian_First = "#C(#00EE00)%s#n率先通关了英雄圣殿的#C(#ffff37)%s[%s]#n！所谓兵贵神速啊！"
HeroShengdian_Fast = "#C(#00EE00)%s#n仅用#C(#00EE00)%s#n回合便通关了英雄圣殿的#C(#ffff37)%s[%s]#n！还有更快的吗？"

HeroShengdian_LevelLimit = "等级不足，该副本尚未开启"

HS_1 = "左神卫"
HS_2 = "右神卫"
HS_3 = "神卫"

def Return_ShengdianGuanqiaName(stageId):
	HeroShengdian_GuanqiaName = {1:HS_1, 2:HS_2, 3:HS_3}
	if stageId not in  HeroShengdian_GuanqiaName:
		return
	else:
		return HeroShengdian_GuanqiaName[stageId]

#===============================================================================
# 宠物
#===============================================================================
PET_RMB_NOT_ENOUGH_PROMPT = "神石不足"
PET_TRAIN_SUCCESS_PROMPT = "培养成功，属性提升%s"
PET_TRAIN_FAIL_PROMPT = "培养失败，幸运值增加"
PET_FAST_TRAIN_PROMPT = "培养%s次，成功%s次，失败%s次"
PET_SOUL_ON_SUCCESS_PROMPT = "附灵成功"
PET_SOUL_OFF_SUCCESS_PROMPT = "卸载成功"
PET_SOUL_UPGRADE_SUCCESS_PROMPT = "升级成功"
PET_LUCKY_DRAW_REWARD_PROMPT = "恭喜获得： #Z(%s,%s)"
PET_LIBAO_USE_MSG = "使用成功：获得%s"
#===============================================================================
# 奴隶系统
#===============================================================================
Slave_Tips_1 = "正在保护时间，请稍后继续"
Slave_Tips_2 = "对方正在保护时间，请稍后继续"
Slave_Tips_3 = "对方数据异常，操作失败"#没有战斗数据
Slave_Tips_4 = "对方处于已进入保护时间,抢夺失败,请稍后继续"
Slave_Tips_5 = "奴隶数量不能超过3个"
Slave_Tips_6 = "今日获取的经验已满"
#================================================================================
#改名系统
#=================================================================================
ERROR_NULL_MSG = "修改名字不能为空,请输入名字"
ERROR_WRONG_NAME = "该名字不合法，请重新输入"
ERROR_SAME_NAME = "该角色名已被使用，请重新输入"
CHANGE_NAME_SUC_MSG = "龙骑士#C(#E87D22)%s#n使用角色改名卡将名字改为#C(#E87D22)%s#n,闻名天下。"
CHANGE_NAME_SUC_MSG2 = "龙骑士#C(#E87D22)%s#n合服后将名字改为#C(#E87D22)%s#n。"
#================================================================================
#宠物灵树
#=================================================================================
PetFarm_BuyCD_Ok = "加速成功"
PetFarm_LuckRole = "#C(#00FF00)%s#n在宠物灵树鸿运当头，幸运收获#Z(%s,%s)"
#===============================================================================
# QQ登陆面板
#===============================================================================
QQ_APP_ON_PANEL_REWARD_PROMPT = "成功将龙骑士传添加到QQ应用面板获得奖励#Z(%s,%s)#H"
#===============================================================================
# 狂欢充值
#===============================================================================
CarnivalOfTopup_Awrad_Msg = "您的人品太好了，获得：#H"
TarotPackageOrlPackageIsFull = "背包，或者命魂背包空间不足，请整理后再来。"
TalentCardPackageIsFull = "天赋卡背包已满，请清理后再来!"
CarnivalOfTopup_Award_GlobalMsg_1 = "#C(#00FF00)%s#n幸运之极，在#C(#00FF00)狂欢充值#n礼盒中开出了"
CarnivalOfTopup_Award_GlobalMsg_2 = "，真是让人羡慕嫉妒啊！"
CarnivalOfTopup_Item_Tips = 		"#Z(%s,%s)"			#物品(coding, cnt)
CarnivalOfTopup_Tarot_Tips = 		"#t(#K(sTT,%s,%s))"	#命魂(命魂类型, 数量)
CarnivalOfTopup_Talent_Tips = 		"#L(%s,%s)"				#天赋卡（天赋卡类型，数量）

#===============================================================================
# 世界杯
#===============================================================================
WorldCup_Tips_1 = "猜对%s支队伍，获得世界杯宝箱+%s"
WorldCup_Tips_2 = "领取成功：世界杯宝箱+%s"
WorldCup_Gjjc_Msg = "#C(#fefb00)%s#n#C(#66FF00)参与世界杯决赛神石竞猜，获得世界杯纪念宠物#C(#FFFF00)福來哥#n+1，#U#A(#K(dlg,OPEN_WORLDCUP))我要宠物#n#n"
WorldCup_Gjjc_Msg_1 = "领取成功：获得了#Z(%s,%s)"
#===============================================================================
# 一球成名
#===============================================================================
BallFameGoalsTips = "哇! 射的真准, 获得: #Z(%s,%s)"
BallFameCheersTips = "喝彩成功, 奖励已发送, 获得: #Z(%s,%s)"
#===============================================================================
# 魔域星宫
#===============================================================================
AsteroidFields_Tips_OneKeyAward = "一键挑战获得：#H"
#================================================================================
#天降神石
#================================================================================
HeavenUpRMB_MSG = "#C(#EE7600)【神石转转乐】#n#C(#00EE00)%s#n拿出#C(#00EE00)%s#n神石接受神灵的恩泽，圣光一闪，掉落#C(#00EE00)%s#n神石。真是福星高照，好运连连啊！"
HeavenUpRMB_MSG2 = "#C(#EE7600)【神石转转乐】#n#C(#00EE00)%s#n拿出#C(#00EE00)%s#n神石接受神灵的恩泽，圣光一闪，掉落#C(#00EE00)%s#n神石。还未来得及回神，只见神灵现形小手一抖，又有#C(#00EE00)%s#n神石掉落手中，幸福来得真是太突然！"
#===============================================================================
#圣器
#===============================================================================
Hallows_InheritanceSuccessfully = "继承成功"
Hallows_ShenzaoOkay = "神造成功，经验值加1"
Hallows_OneKeyShenzaoOkay = "神造成功，经验值加+%s"
#===============================================================================
# 砸龙蛋
#===============================================================================
DRAGON_REWARD_HEARSAY = "#C(#EE7600)【砸龙蛋】#n#C(#00EE00)%s#n人品真是太好了，在#C(#00EE00)砸龙蛋#n活动中砸出了震惊全服的奖励：#Z(%s,%s)"
#===============================================================================
# 勇闯十二宫
#===============================================================================
TwelvePalace_AskForHelp_Tips = "#C(#EE7600)【勇闯十二宫】#n#C(#FFFFFF)#C(#00FF00)%s#n玩家在十二宫门口召集英勇战士，欲闯宫夺宝，此等美事怎能错过？  #C(#00ff00)#U#A(#K(help12Palace, %s))立即协助#n#n#n"
TwelvePalace_HelpFull_Tips = "协助人数已满"
TwelvePalace_HelpAlready_Tips = "已协助过此场闯宫"
TwelvePalace_HelpAwrad_Tips = "协助闯宫成功，获得#Z(%s,%s)"
TwelvePalace_HelpNoAwrad_Tip = "协助闯宫成功，今日协助奖励次数已用尽"
TwelvePalace_Awrad_Tips = "闯宫成功，获得#Z(%s,%s)"
TwelvePalace_Helpself_Tips = "不可协助自己"
TwelvePalace_HelpOver_Tips = "此次闯宫已结束"


#===============================================================================
# 婚戒
#===============================================================================
WeddingRingNormalTips = "锻造成功：婚戒经验 + 10"
WeddingRingCritTips = "锻造暴击：婚戒经验 + 20"
WeddingAdvancedTips = "婚戒姻缘石 -% s，获得经验 +% s"
#===============================================================================
# 结婚
#===============================================================================
MarryProposeWait_1 = "您心仪之人正好离开了游戏，请等待上线后再求婚"

MarryProposeWait_2 = "您已发送过求婚，让他再考虑一会吧！"
MarryProposeWait_3 = "您已发送过求婚，让她再考虑一会吧！"
def ReturnMarryProposeWait(sex):
	if sex == 1:
		return MarryProposeWait_2
	else:
		return MarryProposeWait_3

MarryProposTooLate = "您心仪之人已接受了他人求婚"

MarryThird_1 = "您已有未婚妻，岂可再找第三者"
MarryThird_2 = "您已有未婚夫，岂可再找第三者"
def ReturnMarryThird(sex):
	if sex == 1:
		return MarryThird_1
	else:
		return MarryThird_2

MarryWorldPropose = "#C(#E87D22)【深情告白】#C(#00FF00)%s#n#C(#FFFFFF)含情脉脉的望着#n#C(#00FF00)%s#n#C(#FFFFFF)，勇敢的向全世界告白求婚：#C(#00FF00)%s#n"
MarryProposeSuccess = "您的求婚已成功发送给心仪之人"
MarryAcceptNotLine = "您的爱慕者正好离开了游戏，请等待上线后再同意"
MarryAcceptMarried = "你们情深缘浅，#C(#00FF00)%s#n已寻到另一半"
MarryIsVow = "有人正在宣誓, 请稍后"

HoneymoonSay_1 = "#C(#E87D22)【两人蜜月】#C(#00FF00)%s#n#C(#FFFFFF)悄悄跟#C(#00FF00)%s#n说：#C(#00FF00)%s#n"
HoneymoonSay_2 = "#C(#E87D22)【环游蜜月】#C(#00FF00)%s#n#C(#FFFFFF)对#C(#00FF00)%s#n情意绵绵的说：#C(#00FF00)%s#n"

HoneymoonMailTitle = "蜜月奖励"
HoneymoonMailSender = "系统"
HoneymoonMailContent = "由于你们相亲相爱，共同度过了一段甜蜜的蜜月时光，我代表爱情天使，给你们送上蜜月祝福：#Z(%s,%s), 亲密值：%s"
HoneymoonBegin_1 = "#C(#E87D22)【环游蜜月】#C(#00FF00)%s#n#C(#FFFFFF)和#C(#00FF00)%s#n两人相知相爱，共结连理，两人骑着飞马环游圣辉城，留下甜蜜的爱情足迹！让我们为他们的爱情欢呼吧！#n"
HoneymoonBegin_2 = "#C(#E87D22)【两人蜜月】#C(#00FF00)%s#n#C(#FFFFFF)和你开始静静的享受两人蜜月时光，快找他聊聊吧！珍惜这一刻，珍惜这么温馨与幸福的每一秒#n"
HoneymoonFinish_1 = "#C(#E87D22)【环游蜜月】#C(#FFFFFF)不知不觉，#C(#00FF00)%s#n#C(#FFFFFF)和#C(#00FF00)%s#n的环游蜜月时光已经结束，大家为他们祝福吧，这是一对天下最幸福的一对，他们的每一分每一秒都将成为最美好的回忆#n"
HoneymoonFinish_2 = "#C(#E87D22)【两人蜜月】#C(#FFFFFF)不知不觉，#C(#00FF00)%s#n#C(#FFFFFF)和你的两人蜜月时光已经结束，这每一分每一秒都将成为最美好的回忆#n"

HoneymoonBegin = "蜜月开启成功，使用#C(#00FF00)甜言蜜语#n享受快乐的蜜月之旅吧"

RingImprintSuccess = "铭刻成功"

MarryFindError = "你的伴侣已经超过15天未登录，无法举办派对，请他登录后再举办"
RingFindError = "您的伴侣已经超过15天未上线，召唤伴侣上线后才能铭刻"
AuctionFindError = "您的伴侣已经超过15天未登录，无法前往竞拍跨服派对，请让您的伴侣登录后再前往"

MarryProposeQinshou = "禽兽，连小学生也不放过"
MarryProposeTrueQinshou = "真禽兽，连男人你都不放过"

MarryRefusal = "#C(#00EE00)%s#n拒绝了你的求婚申请，莫灰心，天涯何处无芳草！"

MarryAcceptGirl = "对方是女性！！！"
MarryAcceptSuccess = "接受成功，请耐心等待对方预约婚礼"

MarryCancelDinghun = "取消婚约成功"
MarryCancelDinghun_Title = "【系统】取消婚约"
MarryCancelDinghun_Sender = "系统"
MarryCancelDinghun_Content = "%s觉得您们情深缘浅，无法走完人生的爱情之路，取消了您们的婚约"

MarryDivorce_1 = "#C(#00EE00)%s#n结束了你们的婚姻，好聚好散，仍是朋友"
MarryDivorce_2 = "离婚成功，莫伤心，您还有一大片森林"
MarryHandsel_Title = "【系统】结婚红包"
MarryHandsel_Sender = "系统"
MarryHandsel_Content = "#C(#00EE00)%s#n赠送了一个巨大的结婚红包，祝恋人们同心永结，比翼齐飞啊 "

MarryInvite_Title = "【系统】婚礼邀请"
MarryInvite_Sender = "系统"
MarryInvite_ContentA = "#C(#00EE00)%s#n与#C(#FF00CC)%s#n将于#C(#FFFF00)%s#n日#C(#FFFF00)%s#n时#C(#FFFF00)%s#n分举行#C(#66FF00)普通婚礼#n，大家羡慕吧，嫉妒吧！婚礼中新郎新娘将送出大量#C(#FF33CC)新婚礼盒#n，到时记得来参加他们的婚礼哦。有钱的捧个钱场，没钱的捧个人场。"
MarryInvite_ContentB = "#C(#00EE00)%s#n与#C(#FF00CC)%s#n将于#C(#FFFF00)%s#n日#C(#FFFF00)%s#n时#C(#FFFF00)%s#n分举行#C(#FF33CC)贵族婚礼#n，大家羡慕吧，嫉妒吧！婚礼中新郎新娘将送出大量#C(#FF33CC)新婚礼盒#n，到时记得来参加他们的婚礼哦。有钱的捧个钱场，没钱的捧个人场。"
MarryInvite_ContentC = "#C(#00EE00)%s#n与#C(#FF00CC)%s#n将于#C(#FFFF00)%s#n日#C(#FFFF00)%s#n时#C(#FFFF00)%s#n分举行#C(#FF6600)皇室婚礼#n，大家羡慕吧，嫉妒吧！婚礼中新郎新娘将送出大量#C(#FF33CC)新婚礼盒#n，到时记得来参加他们的婚礼哦。有钱的捧个钱场，没钱的捧个人场。"

MarryXuanshiman = "#C(#FF6600)新郎#C(#00EE00)%s#n宣誓：#C(#FFFF00)我愿意#C(#FF00CC)%s#n成为我的妻子，从今天开始相互拥有，相互扶持，无论是打怪升级还是PK竞技场、我们都互相帮助，彼此相爱，永不分离。#n"
MarryXuanshiwoman = "#C(#FF6600)新娘#C(#FF00CC)%s#n宣誓：#C(#FFFF00)我愿意#C(#00EE00)%s#n成为我的丈夫，从今天开始互相拥有，相互扶持，无论是打怪升级还是PK竞技场，我们都互相帮助，彼此相爱，永不分离。#n"
MarryBeginInform = "你与#C(#00EE00)%s#n的婚礼都已经开始了，还在磨蹭什么？#C(#00ff00)#U#A(#K(ENTER_WED_SCENE,%s))立即进入#n#n#n"
MarryBeginInformB = "#C(#00EE00)%s#n与#C(#FF00CC)%s#n的婚礼正式开始，大家羡慕吧，嫉妒吧！婚礼中新郎新娘将送出大量#C(#FF33CC)新婚礼盒#n，还等什么？有钱的捧个钱场，没钱的捧个人场。#C(#00ff00)#U#A(#K(ENTER_WED_SCENE,%s))前往参加婚礼#n#n#n"

MarryInvite_Tips = "一场幸福美满的婚礼正在进行中，新郎#C(#00EE00)%s#n与新娘#C(#FF00CC)%s#n邀请各位英雄前来捧场。#C(#00ff00)#U#A(#K(ENTER_WED_SCENE,%s))前往参加婚礼#n#n#n"
MarryVow = "#C(#FFFF00)恭喜#C(#00EE00)%s#n与#C(#FF00CC)%s#n喜结良缘，成为#C(#FF0000)《龙骑士传》#n本服务器第#C(#FF0000)%s#n对夫妻。祝他们海枯石烂，天长地久，龙腾凤翔，笙磬同音！"
MarryUnburden = "#C(#00EE00)%s#n对#C(#FF00CC)%s#n深情表白说：#C(#FFFF00)%s#n"

MarrySendLibaoWorld = "新郎#C(#00EE00)%s#n和新娘#C(#FF00CC)%s#n在婚礼上发放了#C(#00EE00)%s#n个#C(#FF33CC)新婚礼盒#n，数量有限，先到先得。还犹豫什么？#C(#00ff00)#U#A(#K(ENTER_WED_SCENE,%s))马上去抢#n#n#n"
MarryGetLibaoWorld = "#C(#FFFF00)%s#n以迅雷不及掩耳之势从人群中抢到了新郎#C(#00EE00)%s#n与新娘#C(#00EE00)%s#n赠送的#C(#FF33CC)#Z(%s,%s)#n。#C(#00ff00)#U#A(#K(ENTER_WED_SCENE,%s))我也去抢#n#n#n"
MarryGetLibaoGeren = "领取成功： #Z(%s,%s)"
MarryGetLibaoCntMax = "今日已达最大收益次数，无法继续获得奖励"
MarrySendHeliWorld = "#C(#FFFF00)%s#n赠送了新人#C(#00EE00)%s#n与#C(#FF00CC)%s#n#C(#FF6600)新婚贺礼#n，并且送上了祝福：#C(#FFFF00)愿你们真诚的相爱之火，如初升的太阳，越久越旺；让众水也不能熄灭，大水也不能淹没！"
MarryPlayFireworksSystem = "#C(#00EE00)%s#n点燃了烟花，这是全服秀恩爱的节奏啊！"

MarryReviveHeli = "您收到#C(#00EE00)%s#n赠送的结婚贺礼，恭喜恭喜！"

MarryNotBegin = "婚礼未开始"
MarryFinish = "婚礼结束，但爱意长存啊"
MarryTooMuchPeople = "婚礼内已人满为患，真是热闹非凡啊！"

MarrySuccessBiaobai = "表白成功"

MarryXuanshiman = "新郎#C(#00EE00)%s#n宣誓：#C(#FFFF00)我愿意#C(#FF00CC)%s#n成为我的妻子，从今天开始相互拥有，相互扶持，无论是打怪升级还是PK竞技场、我们都互相帮助，彼此相爱，永不分离。#n"
MarryXuanshiwoman = "新娘#C(#FF00CC)%s#n宣誓：#C(#FFFF00)我愿意#C(#00EE00)%s#n成为我的丈夫，从今天开始互相拥有，相互扶持，无论是打怪升级还是PK竞技场，我们都互相帮助，彼此相爱，永不分离。#n"

MarryFinisMail_Title = "【系统】婚礼"
MarryFinisMail_Sender = "系统"
MarryFinisMail_Content = "恭喜你和#C(#00EE00)%s#n完成了终身大事，恭喜你们分别获得了#C(#FF33CC)#Z(%s,%s)#n奖励"

MarryInScene_1 = "已在婚礼场景中，无法直接切换"
MarryInScene_2 = "已在婚礼场景中"

MarryRebateTips = "新人#C(#00EE00)%s#n收到了#C(#FFFF00)%s#n赠送的#C(#FF6600)新婚贺礼#n，表示非常感谢，立即回赠了对方#Z(%s,%s)"

MarryRebateMail_Title = "【系统】新人回礼"
MarryRebateMail_Sender = "系统"

MarryDivorceToday = "离婚玩家当天无法被求婚，请明日再来"
MarryRequestTips = "想和你一起慢慢变老"
#===============================================================================
#情缘副本
#================================================================================
COUPLES_LEVEL_MSG = "您或您的恋人等级达不到该副本的等级，你可以挑选等级低点的哟"
COUPLES_NO_BUY_TIMES = "今日已没有剩余的购买次数了"
COUPLES_INVITE_MSG = "您的爱人不在，一个人也可以去闯关哟"
COUPLES_INVITE_SUC = "邀请成功，恋人正在换衣服，稍等下哟"
COUPLES_INVETE_MSG2 = "您的爱人奖励还未领取，快提醒他领取通关奖励吧"
COUPLES_DELCD_MSG = "立即减少%s秒行动CD"
COUPLES_ADDCD_MSG = "立即增加%s秒行动CD"
COUPLES_DELPASS_MSG = "立即减少%s秒总通关时间"
COUPLES_ADDPASS_MSG = "立即增加%s秒总通关时间"
COUPLES_NO_TIMES = "您或您的爱人已经没有闯关次数了！"
COUPLES_ADD_BUFF = "成功获得Buff"
COUPLES_FB_FAILED = "本次通关已结束，您的挑战失败！"
#===============================================================================
#变性
#================================================================================
ChangeRoleGender_Tips1 = "有家室的人无法进行变性操作"

#==================================================================================
#天赋卡
#==================================================================================
TalentIsFull_Tips = "天赋卡背包空间不足"
TalentSameTpye_Tips = "已装备了同类型的天赋卡了"
TalentNeedLevel = "80级以上英雄才可装备天赋卡"
Talent_Exchange_Suc = "获得天赋卡:#L(%s,%s)"
Talent_Dec_Suc = "#L(%s,%s,-)#H"
Talent_Unlock_Suc = "解锁成功！"
Talent_DecCard = "分解卡片成功:"
Talent_LevelUp = "天赋卡成功升级至%s星"

#===============================================================================
# 使用烟花
#===============================================================================
UseFireWorks_Tips = "#C(#00EE00)%s#n在#C(#FFFF00)%s#n使用了烟花，“嘭”的一声巨响,烟花腾空而起，在天空中绽开五颜六色，绚丽如梦"
UseFireWorksFail = "当前场景无法使用烟花"

#===============================================================================
# 游戏联盟登录奖励
#===============================================================================
GameUnionAward_tips = "恭喜你，获得："

#===============================================================================
# 神石银行
#===============================================================================
RMBBankExtract_Tips = "领取成功：#H神石+%s#H魔晶+%s"

#===============================================================================
#全民团购
#===============================================================================
UniverBuy_Msg = "#C(#E87D22)由于大家疯狂地抢购，#C(#FFFF00)全民团购活动全民大礼包（%s）#C(#E87D22)购买人数已达#C(#00FF00)%s#C(#E87D22)人，每日参与团购的玩家在0点结算后统一发放福利宝箱，巨量回馈，等你来拿。#C(#00FF00)#U#A(#K(openQMTG))我也要团购！#n#n"

#===============================================================================
# GVE
#===============================================================================
GVE_NEED_CAREER_PROMPT = "您的队伍中尚缺#C(#FFFF00)%s#n人，无法进入副本"
GVE_NEED_DRAGON_LEVEL_PROMPT = "队友神龙等级不足#C(#00EE00)%s#n，无法进入该副本。"
GVE_WORLD_CALL = "#C(#4169e1)组队副本，#C(#FFFF00)%s#n队伍尚缺#C(#FFFF00)%s#n人，等待你的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
GVE_TEAM_FULL_CANT_INVITE_PROMPT = "当前组队人数已满，无法发送邀请"

#===============================================================================
# 开服boss
#===============================================================================
KaifuBossTeamTips = '齐心协力共同成功击败了开服BOSS中的#C(#FF6600)%s#n'
KaifuBossSingleTips = '独自一人成功击败了开服BOSS中的#C(#FF6600)%s#n'
KaifuBossActiveSeverAward = '并且为全服激活了开服BOSS奖励。#C(#00FF00)#U#A(#K(OPEN_KAIFU_BOSS_PANEL))前往领取#n#n'
KaifuBossSingleAwardTips = '，独自获得了奖励'
KaifuBossTeamAwardTips = '，分别获得了奖励'
KaifuBossItem_Tips = "#Z(%s,%s)"#物品(coding, cnt)
KaifuBossServerTips1 = '#C(#FFFF00)%s#n领取了'
KaifuBossServerTips2 = '奖励，感谢'
KaifuBossServerTips3 = '击败了开服BOSS中的#C(#FF6600)%s#n。'
KaifuBossNiubilityNameTips = '#C(#FFFF00)%s#n'
KaifuBossComma = '，'#中文逗号
KaifuBossWorshipTip = '你膜拜了大神'
#===============================================================================
# 许愿池
#===============================================================================
WishPoolRevive = "许愿获得:#H"
WishPoolMail_Title = "许愿池"
WishPoolMail_Sender = "系统"
WishPoolMail_Content = "背包剩余空间不足，本次许愿奖励通过系统邮件发放。"

WishPoolPackFull = "背包剩余空间不足，本次许愿奖励已通过系统邮件发放。"
WishPoolEx_Tips = "背包剩余空间不足，购买失败！"

WishPoolSpecItem = "%s在许愿池许愿获得了#Z(%s,%s),#C(#00FF00)#U#A(#K(WishPool))前往许愿#n#n"
WishPoolSpecTarot = "%s在许愿池许愿获得了#t(#K(sTT,%s,%s)),#C(#00FF00)#U#A(#K(WishPool))前往许愿#n#n"

WPG_LevelLimit = "主角达到30级时才可以参与金币副本。"
WPG_NoCnt = "今日没有次数"
WPG_GOLD_MSG = "获取%s金币"
WPG_Finish = "已完成本次接金币玩法，共获得%s金币！"
WPG_Open = "%s在许愿池中完成了本服今日第%s次许愿,为大家开启了第%s次金币宝藏。#C(#00FF00)#U#A(#K(JBFB))前往掘金#n#n"
WPG_Pick = "捡金币玩法获得:%s金币"
WPG_Drop = "接金币玩法获得:%s金币"
#===============================================================================
# 宠物进化
#===============================================================================
PET_EVOLUTION_SUC = "修行成功，修行进度+%s"
PET_ONEKEY_EVOLUTION_SUC = "修行%s次，修行进度+%s"
PET_EVOLUTION_FALSE = "太遗憾了，修行失败，下次修行成功率+%s%s，再试一次吧！"
PET_EVOLUTION_FULL = "当前修行进度已经满了，先去进阶吧！"
PET_EVOLUTION_STAR = "宠物星级不足%s星,不能进行宠物修行"
#===============================================================================
# 神龙系统
#===============================================================================
DRAGON_UPGRADE_PROMPT = "进化成功"
Dragon_Equip_Upgrade_Okay = "恭喜，升阶成功"
#===============================================================================
# 天天秒杀
#===============================================================================
DailySeckill_GetReadyTips = "天天秒杀活动即将开启，英雄们请做好准备哟！"
DailySeckill_StartTips = "天天秒杀时刻开始，全城秒杀，心动不如手动"
DailySeckill_PreciousItemTips = "#C(#00FF00)【天天秒杀】#n快抢手#C(#FFFF00)%s#n抢到了震惊全服的物品#Z(%s,%s)，可喜可贺啊！"
DailySeckill_PreciousTarotTips = "#C(#00FF00)【天天秒杀】#n快抢手#C(#FFFF00)%s#n抢到了震惊全服的物品#t(#K(sTT,%s,%s)),可喜可贺啊！"
DailySeckill_PreciousTalentTips = "#C(#00FF00)【天天秒杀】#n快抢手#C(#FFFF00)%s#n抢到了震惊全服的物品#L(%s,%s)，可喜可贺啊！"
DailySeckill_PackageFulltips = "您的背包空间不足，请先整理背包"
DailySeckill_PersonalTarottips = "您的手真快，秒到了令人眼红的物品 #t(#K(sTT,%s,%s))"
DailySeckill_PersonalItemtips = "您的手真快，秒到了令人眼红的物品 #Z(%s,%s)"
DailySeckill_PersonalTalenttips = "您的手真快，秒到了令人眼红的物品 #L(%s,%s)"
DailySeckill_CDTips = "您的手太快了，请%s秒后再点击购买"
DailySeckill_SlowTips = "您的手慢了，该道具已被他人秒掉"
DailySeckill_TimesTips = "#C(#00FF00)【天天秒杀】#n今日秒杀第#C(#FFFF00)%s#n波将在1分钟后开始，赶紧准备#C(#00FF00)#U#A(#K(openeverydaybuy))参与抢购吧！#n#n"

#===============================================================================
# 勇者英雄坛
#===============================================================================
BraveHero_Title = "【勇者英雄坛】跨服排名奖励"
BraveHero_Sender = "系统"
BraveHero_Content = "恭喜！您在【勇者英雄坛】活动中排名第%s，达到了排名奖励标准，获得了丰厚奖励！"
BraveHero_TimeLimit = "当前时间不可挑战"
BraveHero_BuyLimit = "当前时间无法购买行动力"

#===============================================================================
# 装备附魔
#===============================================================================
Enchant_Suc_Msg = "附魔成功，%s附魔等级提升至%s级"
Enchant_Abroad_Msg = "要逆天了！%s将#Z(%s,%s)附魔等级提升到了%s级，这是要称霸全服的节奏啊。#C(#00FF00)#U#A(#K(ZBFM))我要附魔！#n#n" 

#===============================================================================
# 开服boss
#===============================================================================
HefuBossTeamTips = '齐心协力共同成功击败了合服BOSS中的#C(#FF6600)%s#n'
HefuBossSingleTips = '独自一人成功击败了合服BOSS中的#C(#FF6600)%s#n'
HefuBossActiveSeverAward = '并且为全服激活了合服BOSS奖励。#C(#00FF00)#U#A(#K(OPEN_KAIFU_BOSS_PANEL))前往领取#n#n'
HefuBossSingleAwardTips = '，独自获得了奖励'
HefuBossTeamAwardTips = '，分别获得了奖励'
HefuBossItem_Tips = "#Z(%s,%s)"#物品(coding, cnt)
HefuBossServerTips1 = '#C(#FFFF00)%s#n领取了'
HefuBossServerTips2 = '奖励，感谢'
HefuBossServerTips3 = '击败了合服BOSS中的#C(#FF6600)%s#n。'
HefuBossNiubilityNameTips = '#C(#FFFF00)%s#n'
HefuBossComma = '，'#中文逗号
HefuBossWorshipTip = '你膜拜了大神'

#===============================================================================
# NA北美版
#===============================================================================
ROLE_EXP_LIMIT_PROMPT = "等级已满，无法增加经验"

#===============================================================================
# 超值大礼
#===============================================================================
SuperDiscountRMBNotEnough = "神石不足"
SDRewardMsg_Head = "恭喜你获得#H"
SDRewardMsg_Money = "金币+ %s#H"
SDRewardMsg_BindRMB = "魔晶+ %s#H"
SDRewardMsg_RMB = "奖励神石+ %s#H"
SDRewardMsg_Item = "#Z(%s,%s)#H"

#========坐骑经验丹提示==============
MOUNT_EXP_MSG = "当前星级已满，请转生后再使用！"
USE_EXP_SUC_MSG = "使用成功，获得%s坐骑经验。"
USE_EVO_SUC_MSG = "使用成功，您的坐骑升阶至%s阶%s星"
CAN_NOT_USE_MSG = "该道具不可在%s阶及以上的坐骑上使用"
#===============================================================================
# 野外寻宝
#===============================================================================
WildBoss_Ready = "#C(#EE7600)【野外夺宝】#n5分钟后开启，请各位勇士开始准备"
WildBoss_Begin = "#C(#EE7600)【野外夺宝】#n活动已经开启，请勇士们尽快加入战斗，#C(#00ff00)#U#A(#K(openYWDBBM))前往夺宝#n#n"
WildBoss_KillBoss = "#C(#EE7600)【野外夺宝】#n本地图的BOSS已被击杀，现在开启宝箱争夺战，战胜拥有宝箱的玩家可获得对方一半宝箱，点击玩家直接进入战斗！"
WildBoss_PropectionTime = "玩家正处于保护时间，剩余%s秒"
WildBoss_SnatchCD = "正处于抢夺冷却时间，剩余%s秒"
WildBoss_InFight = "对方正在战斗中"
WildBoss_BeSnatch = "%s战胜了你，夺走#H"
WildBoss_BeSnatchWin = "%s挑战你失败，你获得%s积分"
WildBoss_Snatch = "抢夺成功，夺得#H "
WildBoss_SnatchFail = "抢夺失败，丢失%s积分 "
WildBoss_PickUpBuff = "你拾取了%s的英魂，获得附体效果，下一场战斗属性将临时变为%s的属性。"
WildBoss_PickUpBuffFail = "你已经拥有一个英魂BUFF"
WildBoss_PickUpBuffMsg = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n拾取了”#C(#0066CC)%s的英魂#n”，战斗力发生了翻天覆地的变化！"
WildBoss_LeaveScene = "您已离开活动场景，丢失全部宝箱."
WildBoss_RegionName_1 = "初级战区"
WildBoss_RegionName_2 = "中级战区"
WildBoss_RegionName_3 = "高级战区"
WildBoss_RegionName_4 = "顶级战区"
def GetWildBossRegionName(index):
	return {1 : WildBoss_RegionName_1, 2 : WildBoss_RegionName_2, 3:WildBoss_RegionName_3, 4 : WildBoss_RegionName_4}.get(index)

WildBoss_Kill_1 = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n初露锋芒，已经连杀10人，额外获得10积分，击败他的玩家可获得大量积分。"
WildBoss_Kill_2 = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n锋芒毕露，已经连杀20人，额外获得20积分，击败他的玩家可获得大量积分。"
WildBoss_Kill_3 = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n势不可挡，已经连杀30人，额外获得30积分，击败他的玩家可获得大量积分。"
WildBoss_Kill_4 = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n无人可当，已经连杀%s人，即将成为战区第一人，击败他的玩家大量积分！"
WildBoss_Kill_5 = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n所向披靡，已经突破100连杀，额外获得100积分，击败他可获得大量积分！"
WildBoss_Kill_6 = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n战神附体，已经连杀200人，额外获得200积分，击败他可获得其大量积分！"
WildBoss_Bekill = "#C(#EE7600)【野外夺宝】#n#C(#FFFF00)%s#n成功终结了#C(#FFFF00)%s#n的%s连杀，获得大量积分！地图坐标#C(#00ff00)#U#A(#K(MoveXY,%s,%s))(%s,%s)#n#n#n处出现了“#C(#0066CC)%s的英魂#n”，拾取后可获得%s的属性。"
WildBoss_AddScore = "积分+%s"
WildBoss_DecScore = "%s积分。"
WildBoss_DropBox = "#C(#EE7600)【野外夺宝】#n坐标#C(#00ff00)#U#A(#K(MoveXY,%s,%s))(%s,%s)#n#n#n附近出现了其他玩家丢失的宝箱，机不可失，赶紧来拾取吧！"
WildBoss_PickUpBox = "拾取成功"
WildBoss_BuffName = "%s的英魂"
#===============================================================================
# facebook like
#===============================================================================
FACEBOOK_LIKE_PROMPT = "You completed the Facebook Like quest."

#===============================================================================
# Time
#===============================================================================
TIME_STRING_DAY_1 = "%s天"
TIME_STRING_HOUR_1 = "%s小时"
TIME_STRING_MINUTE_1 = "%s分钟"
TIME_STRING_SECOND_1 = "%s秒"
TIME_STRING_DAY_2 = "%s天前"
TIME_STRING_HOUR_2 = "%s小时前"
TIME_STRING_MINUTE_2 = "%s分钟前"
TIME_STRING_SECOND_2 = "%s秒前"


#===============================================================================
# 中秋活动
#===============================================================================
AF_LatteryRewardMsg_Head = "恭喜你获得#H"
AF_LatteryRewardMsg_Money = "#C(#FFFF00)金币+ %s#n"
AF_LatteryRewardMsg_Item = "#Z(%s,%s)#H"
AF_LatteryRewardMsg_ItemEx = "#Z(%s,%s)"
AF_LatteryRewardNotifySep = "，"
AF_LatteryMasterReward = "#C(#FFFF00)%s#n在中秋博饼活动中投出#C(#00FF00)%s#n，获得奖励%s，真是可喜可贺！" 
AF_LatteryMasterTip1 = "对堂"
AF_LatteryMasterTip2 = "状元"
AF_LatteryMasterTip3 = "五王"
AF_LatteryMasterTip4 = "金花"
AF_MoonCakeTooMuchTip = "每日最多使用20个月饼"
AF_MoonCakeUseTip = "使用成功，获得体力+ %s#H" 
def AF_LatteryType2Name(diceType):
	if diceType == 6:
		return AF_LatteryMasterTip1
	elif diceType == 7:
		return AF_LatteryMasterTip2
	elif diceType == 8:
		return AF_LatteryMasterTip3
	elif diceType == 9:
		return AF_LatteryMasterTip4
	else:
		return None

#===============================================================================
#限次宝箱
#===============================================================================
LimitChest_PackageFullTips = "背包已满，请先清理背包"
LimitChest_RewardTips = "宝箱开启成功获得："
#================================================================================
#时装
#=================================================================================
FASHION_STAR_FAILED_MSG = "本次升星失败，不要灰心，幸运值增加了%s。"
FASHION_STAR_SUC_MSG = "恭喜你！本次升星成功！"
FASHION_STAR_ITEM_TIMEOUT = "已选升星石已过期，升星失败。"
FASHION_ORDER_SUC_MSG = "恭喜你！本次进阶成功！"
FASHION_ORDER_FAILED_MSG = "本次升阶失败，不要灰心，幸运值增加了%s。"
FASHION_ACTIVE_FAILED = "激活失败，必须拥有%s 时装才能激活该图鉴"
FASHION_ACTIVE_SUC = "%s时装激活成功"
FASHION_ACTIVE_WING_FALSE = "没有这个翅膀道具无法激活"
FASHION_IDE_FAILED = "时装鉴定失败，额外增加成功率5%。"
FASHION_MUST_ACTIVE = "请先激活该时装！"
FASHION_MAIL_TITLE = "时装翅膀道具领取"
FASHION_MAIL_SENDER = "系统"
FASHION_MAIL_DESC = "亲爱的玩家，你在本次版本更新前已购买了部分羽翼翅膀，现在羽翼翅膀穿戴功能调整为从时装系统中进行，因此将你已购买过的时装翅膀现在将道具发放给你。时装翅膀道具新增了时装属性，你可以查看时装系统了解。提取时装翅膀时，请检测背包是否有足够的空间。"
FASHION_ACTIVE_WING_SUC = "激活%s翅膀成功，你现在可以培养这个翅膀了。"
FASHION_SAVE_SUC = "时装保存成功"
FASHION_ACTIVE_FALSE = "该时装已激活，可出售该道具"
FASHION_MAIL_TITLE2 = "时装系统奖励"
FASHION_MAIL_SENDER2 = "系统"
FASHION_MAIL_DESC2 = "亲爱的玩家：#H    系统检测到您身上原本穿戴的时装未脱下出售，这里特此献上#C(#00EE00)%s#n个时装之魄，请您领取！"
#===============================================================================
# 深海寻宝
#===============================================================================
SeaXunbaoRumor_1 = "#C(#EE7600)【深海寻宝】#n#C(#00ff00)%s#n在藏宝图的指引下找到了埋于深海的宝藏，获得珍贵奖励：#Z(%s,%s)。#C(#00ff00)#U#A(#K(OPEN_SEA_XUN_BAO))点击寻宝#n#n"
SeaXunbaoRumor_2 = "#C(#EE7600)【深海寻宝】#n#C(#00ff00)%s#n在藏宝图的指引下找到了埋于深海的宝藏，获得珍贵奖励：#t(#K(sTT,%s,%s))。#C(#00ff00)#U#A(#K(OPEN_SEA_XUN_BAO))点击寻宝#n#n"
SeaXunbaoRumor_3 = "#C(#EE7600)【深海寻宝】#n#C(#00ff00)%s#n在藏宝图的指引下找到了埋于深海的宝藏，获得珍贵奖励：#L(%s,%s)。#C(#00ff00)#U#A(#K(OPEN_SEA_XUN_BAO))点击寻宝#n#n"
SeaXunbaoMail_Title = "深海寻宝"
SeaXunbaoMail_Sender = "系统"
SeaXunbaoMail_Content = "深海寻宝奖励"
SeaXunbaoPackageFull = "背包已满, 请在邮件中领取剩余奖励"
#================================================================================
#黄钻活动
#=================================================================================
QQHZGift_Tips_Reward_Head = "恭喜你获得#H"
QQHZGift_Tips_Reward_Item = "#Z(%s,%s)#H"
QQHZGift_Tips_Reward_Master = "#C(#FFFF00)白羊圣骑#C(#E87D22)"

#===============================================================================
# 驯龙系统
#===============================================================================
DT_COLLECT_SOUL_SUCCESS_PROMPT = "聚灵成功，获得%s龙灵"
DT_COLLECT_SOUL_CRIT_SUCCESS_PROMPT = "暴击成功，出现%s倍暴击，获得%s龙灵"
DT_UPGRADE_BALL_SUCCESS_PROMPT = "恭喜，点亮龙魂成功"
DT_AWAKEN_SUCCESS_HEARSAY = "#C(#EE7600)【神龙】#n#C(#00EE00)%s#n唤醒了#C(#00EE00)%s#n，竟然拥有这等呼风唤雨的能力，究竟是何方神圣？！"
DT_EVOLVE_FAIL_PROMPT = "进化失败，祝福值提升%s点"
DT_EVOLVE_SUCCESS_PROMPT = "恭喜，%s成功进化至%s"
DT_EVOLVE_SUCCESS_HEARSAY = "#C(#EE7600)【神龙】#n#C(#00EE00)%s#n将#C(#00EE00)%s#n进化至#C(#00EE00)%s#n，实在是太不可思议了！"
#===============================================================================
# 组队爬塔
#===============================================================================
TT_First_Reward_Tips = "恭喜你，你首次通关了第%s层，获得奖励:#H"

TT_JumpReward_Tips = "您直接获得击杀该怪物奖励:#H"
TT_Level_Tips = "组队爬塔玩法45级开启第一章！"
TT_Level_Tips_0 = "组队爬塔玩法35级开启序章！"
TT_JoinMount_Tips = "您当前骑乘的坐骑不是飞行坐骑，无法进入该副本！"

TT_WorldCall_Tips_0 = "#C(#E87D22)【组队爬塔-序章·精灵之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
TT_WorldCall_Tips_1 = "#C(#E87D22)【组队爬塔-第一章·寂灭之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
TT_WorldCall_Tips_2 = "#C(#E87D22)【组队爬塔-第二章·天空之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
TT_WorldCall_Tips_3 = "#C(#E87D22)【组队爬塔-第三章·失落之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
TT_WorldCall_Tips_4 = "#C(#E87D22)【组队爬塔-第四章·梦魇之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
TT_WorldCall_Tips_5 = "#C(#E87D22)【组队爬塔-第五章·圣域之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
TT_WorldCall_Tips_6 = "#C(#E87D22)【组队爬塔-第六章·冥皇之塔】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"


def GetTT_WorldCall_Tips(index):
	return {0:TT_WorldCall_Tips_0, 1 : TT_WorldCall_Tips_1, 2 : TT_WorldCall_Tips_2, 3: TT_WorldCall_Tips_3, 4 : TT_WorldCall_Tips_4, 5 : TT_WorldCall_Tips_5, 6:TT_WorldCall_Tips_6}.get(index)


TT_OneKeyTips = "一键收益成功，获得:#H"

#===============================================================================
# 星灵系统
#===============================================================================
STAR_GIRL_LEVEL_LESS = "等级不足"
STAR_GIRL_LEVEL_LESS_PARAM = "等级不足%s级,无法使用"
STAR_GIRL_DEAD_ITEM = "道具已过期"
STAR_GIRL_NO_FIGHT = "当前没有出战星灵，无法使用"
STAR_GIRL_MAX_STAR = "当前出战星灵已满星"
STAR_GIRL_DIVINE_SUCCESS = "占星成功，获得星运+%s"
STAR_GIRL_TOTAL_EXP_PROMPT = "升级获得经验+%s"
STAR_GIRL_Tips_1 = "解锁成功"
STAR_GIRL_Tips_2 = "升星成功" 
STAR_GIRL_Tips_3 = "升星失败，祝福值+%s"
STAR_GIRL_Tips_4 = "进化成功"
STAR_GIRL_Tips_5 = "今日购买次数已经达到上限"
STAR_GIRL_Tips_6 = "出战星灵临时祝福值+%s"
STAR_GIRL_Tips_7 = "祝福值已满，不能使用"
STAR_GIRL_UNLOCK_HEARSAY = "#C(#00ff00)%s#n使用#C(#FF33CC)%s#n诚心召唤，成功解锁了#C(#FFFF00)%s#n，真是令人羡慕！"

#===============================================================================
# 3366一周豪礼
#===============================================================================
WR3366_Tips_Reward_Head = "恭喜你获得#H"
WR3366_Tips_Reward_Item = "#Z(%s,%s)#H"
WR3366_Tips_Reward_Money = "#C(#FFFF00)金币+ %s#H"
WR3366_Tips_Reward_BindRMB = "#C(#0099FF)魔晶+ %s#H"

#===============================================================================
# 国庆活动
#===============================================================================
ND_Tips_DailyLiBao = "你成功领取了#Z(%s,%s)"


ND_Exchange_PackageIsFull = "背包空间不足，无法兑换"
ND_Exchange_MountExchange = "#C(#00FF00)%s#n在#C(#00FF00)#U#A(#K(open_nationaldaypanel,4))节日奖励兑换！#n#n#n中成功兑换获得#Z(%s,%s)，真是太霸气了！"

ND_DailyLiBao_PackageIsFull = "背包空间不足，领取失败"

ND_KILL_MSG = "#C(#E87D22)【全民击杀】#n大家在国庆副本的战斗次数已经成功达到了#C(#00FF00)%s#n,大家快去领取全民战斗奖励！#C(#00FF00)#U#A(#K(open_nationaldaygiftpanel))马上领取！"

ND_StrikeBoss_KillElite = "成功击杀%s次精英boss，获得：#H"
ND_StrikeBoss_KillNormal = "成功击杀%s次普通boss，获得：#H"
ND_StrikeBoss_tarot_ServerTell = "#C(#FFFF00)%s#n在#C(#EE7600)【击杀节日boss】#n活动中成功获得#t(#K(sTT,%s,%s))，真是太霸气了！"
ND_StrikeBoss_item_ServerTell = "#C(#FFFF00)%s#n在#C(#EE7600)【击杀节日boss】#n活动中成功获得#Z(%s,%s)，真是太霸气了！"

#===============================================================================
# 福袋
#===============================================================================
LuckyBagUseTips = "福袋开启成功获得："


#===============================================================================
# 找回系统
#===============================================================================

FindBackTips_1 = "恭喜你，找回%s收益成功，本次找回:#H"


#===============================================================================
# 每日集龙印
#===============================================================================
CollectLongyin_MailTitle = "每日集龙印"
CollectLongyin_MailSender = "系统"
CollectLongyin_MailContent = "由于您的背包已满, 签到奖励通过邮件发放"
CollectLongyin_Add = "龙印+%s"

#===============================================================================
# 万圣节活动
#===============================================================================
HalloweenKillMsg = "#C(#E87D22)【万圣节】#n#C(#00EE00)%s#n在万圣节打鬼活动中成功获得 #Z(%s,%s)，真是太霸气了！"
HalloweenKillMsg2 = "%s在万圣节打鬼活动中成功获得 #t(#K(sTT,%s,%s))，真是太霸气了！"
HallowKillMsg = "成功打鬼%s次，获得:"
HalloweenLightMsg = "你成功消耗%s神石，释放了%s次烟花，获得:"
HallowFire = "#C(#E87D22)【万圣节】#n#C(#00EE00)%s#n在万圣节宴会活动中放烟花成功获得#Z(%s,%s)，真是太霸气了！"
HallowFire2 = "#C(#E87D22)【万圣节】#n#C(#00EE00)%s#n在万圣节宴会活动中放烟花成功获得#t(#K(sTT,%s,%s))#H，真是太霸气了！"
HallowFireGlobal = "#C(#E87D22)【万圣节】#n#C(#00EE00)%s#n在万圣节宴会活动中使用了万紫千红烟花，宴会中的玩家都获得了#Z(%s,%s)奖励，快来膜拜吧！"
HallowMailTitle = "宴会烟花额外奖励"
HallowDesc = "亲爱的玩家，因%s在宴会中使用了万紫千红烟花，你额外获得#Z(%s,%s)，现邮件发放给你，请查收。"
HallowCardOverTime = "变身卡已过期"
HallowCollect = "#C(#E87D22)【万圣节】#n#C(#00EE00)%s#n在变身卡收集活动中成功达到收集条件，获得:"
HallowCollect2 = "获得#Z(%s,%s)，真是太霸气了！"
HallowItemTips = "#Z(%s,%s)  "
HallowTaskMsg = "当前形象不符合宴会任务要求变身形象，无法领取奖励。"
HallowNotChange = "在婚礼场景中不能变身"
ChangeCardUseLimit = "最多同时使用5张变身卡"

#===============================================================================
# 龙脉
#===============================================================================
DragonVein_LevelMax = "已达最高等级，无法继续升级"
DragonVein_LevelLuckUp = "升级失败，祝福值提升%s"
DragonVein_LevelUp = "升级成功，%s提升至%s级"
DragonVein_GradeUp = "进化成功，%s提升至%s阶"
DragonVein_GradeLuckUp = "进化失败，进化值提升%s点"
DragonVein_AcvateOk = "恭喜，成功激活了%s"
DragonVein_Lackof = "材料不足"

DragonVeinOnekeyLevelUpOkay = "升级%s次，升级成功！%s提升至%s级"
DragonVeinOnekeyLevelUpFailed = "升级%s次，升级失败，%s的祝福值提升了%s点"
DragonVeinOnekeyGradeUpOkay = "进化%s次，进化成功 ！%s提升至%s阶"
DragonVeinOnekeyGradeUpFailed = "进化%s次，进化失败，%s的进化值提升%s点"

#===============================================================================
# 混乱时空
#===============================================================================
HunluanSpace_Begin = "#C(#EE7600)【混乱时空】#n混乱时空界门已经开启，英雄们纷纷涌入混乱时空中！"
HunluanSpace_End = "#C(#EE7600)【混乱时空】#n今日混乱时空活动已结束，请及时领取奖励"
HunluanSpace_HalfHourReady = "#C(#EE7600)【混乱时空】#n混乱时空界门即将在#C(#ffff37)30#n分钟后开启，请大家做好准备！"
HunluanSpace_TenMinuteReady = "#C(#EE7600)【混乱时空】#n混乱时空界门即将在#C(#ffff37)10#n分钟后开启，请大家做好准备！"
HunluanSpace_DevilBoss = "#C(#EE7600)【混乱时空】#n公会成员在时空中迷失方向的瞬间，#C(#ffff37)%s#n向他们袭来，全公会团结共同抗敌！"
HunluanSpace_DevilBoss_1 = "活动开启前五分钟可挑战时空守护者"
HunluanSpace_DemonBoss_1 = "#C(#EE7600)【混乱时空】#n幻境中层见迭出，公会的BOSS幻影出在第#C(#ffff37)%s#n层！"
HunluanSpace_DemonBoss_2 = "#C(#EE7600)【混乱时空】#n公会成员英勇无敌，击败了BOSS幻影，一大批混乱大军正在袭来。"
HunluanSpace_DemonBoss_3 = "#C(#EE7600)【混乱时空】#n公会成员战力无双，击败了时空中的所有大军！"
HunluanSpace_CD = "冷却中，无法进行操作！"
HunluanSpace_URT = "#C(#EE7600)【混乱时空】#n公会伤害排行"
HunluanSpace_PRT = "#C(#EE7600)【混乱时空】#n个人伤害排行"
HunluanSpace_RT_1 = "，第一名：#C(#ffff37)%s#n"
HunluanSpace_RT_2 = "，第二名：#C(#ffff37)%s#n"
HunluanSpace_RT_3 = "，第三名：#C(#ffff37)%s#n"
HunluanSpace_RT_4 = "，第四名：#C(#ffff37)%s#n"
HunluanSpace_RT_5 = "，第五名：#C(#ffff37)%s#n"
HunluanSpace_UnionLimit = "今日您的公会未达到参与活动条件"
HunluanSpace_First = "#C(#EE7600)【混乱时空】#n公会大神#C(#ffff37)%s#n真是神勇非凡，首次到达第#C(#ffff37)%s#n层！"
HunluanSpace_NoDamage = "#C(#ffff37)%s#n神武非凡，给予了怪物最后一击，此次战斗您将不会增加伤害值。"
#================================================================================
#天马行空
#=================================================================================
DML_Tips_Head = "恭喜你获得#H"
DML_Tips_Item = "#Z(%s,%s)#H"
DML_Broadcast_Mount = "#C(#E87D22)【天马行空】#n#C(#00EE00)%s#n在天马行空活动运气爆棚，获得了#Z(%s,%s)，实在是太令人羡慕了！"

#================================================================================
#蓝钻转大礼
#=================================================================================
QQLZKaiTongGift_Tips_Reward_Head = "恭喜你获得#H"
QQLZKaiTongGift_Tips_Reward_Item = "#Z(%s,%s)#H"
QQLZKaiTongGift_Tips_Reward_Master = "#C(#FFFF00)天马流星#C(#E87D22)"
QQLZKaiTongGift_Tips_Ended = "活动已结束"


#===============================================================================
# 大厅搏饼
#===============================================================================
QQHall_LotteryRewardMsg_Head = "恭喜你获得#H"
QQHall_LotteryRewardMsg_Money = "#C(#FFFF00)金币+ %s#n"
QQHall_LotteryRewardMsg_Item = "#Z(%s,%s)#H"

#===============================================================================
#组队竞技场
#===============================================================================

JT_SameName = "队伍名已经存在"

JT_ExchangeOkay = "兑换成功，获得"
JT_StoreRrfreshOkay = "刷新成功"
JT_ActiveMedalOkay = "激活成功"
JT_UplevelMedalOkay = "升级成功"
JTItemLackOf = "道具不足 "
JTSealingOk_1 = "封印成功，封印等级提升至 %s级"
JTSealingOk_2 = "封印成功"
JTCrystalUpLevelOk = "升级成功"
JTCrystalInlayOk = "镶嵌成功"


JT_Ready_1 = "#C(#E87D22)[跨服组队竞技]#n将在5分钟后进入倒计时，倒计时阶段无法进行战队操作，请各位玩家提前做好准备！"
JT_Ready_2 = "#C(#E87D22)[跨服组队竞技]#n进入活动倒计时，活动将在5分钟后开启，请各位玩家及时参与。"
JT_Start = "#C(#E87D22)[跨服组队竞技]#n已经开始，群雄并起，谁与争锋！"

JT_CanNotDo = "当前时间暂时不能进行战队操作"

JT_NotStart = "跨服组队竞技场还没开启"

JT_WorldLevel = "世界等级不足"

JT_Team_Full = "队伍人数已满"

JT_ChangeInfo = "成功修改战队资料"
JT_InviteReduce = "%s拒绝了你的战队邀请"

JT_Tips_1 = "转移队长成功"
JT_Tips_2 = "对方已被踢出战队"
JT_Tips_3 = "您的战队已被解散"
JT_Tips_4 = "%s加入战队"

JT_Tips_6 = "您已被踢出战队"
JT_Tips_7 = "正在等待对方回应"
JT_Tips_8 = "对方已加入其他战队"
JT_Tips_9 = "正在等待对方回应"
JT_Tips_10 = "战队人数已满"
JT_Tips_11 = "队长不在线"
JT_Tips_12 = "对方不在线"
JT_Tips_13 = "队伍已经解散了"
JT_Tips_14 = "%s拒绝了你的邀请"
JT_Tips_15 = "你的操作太频繁了"
JT_Tips_16 = "已有匹配记录，今日暂不能加入战队。"
JT_Tips_17 = "该玩家今日暂不能加入战队"
JT_Tips_18 = "玩家当前正在战斗或组队等状态，不可进行邀请！"
JT_Tips_19 = "当前不在活动时间内不能进行邀请"
JT_Tips_20 = "当前没有战队或战队成员不足，不能进入跨服"
JT_Tips_21 = "对方不在线"

JT_GroupCanNotSignUp = "当前不是小组赛报名时间"
JT_GroupNotThisTime = "当前时间不能查看分组"

JT_GroupStart = "#C(#E87D22)【跨服争霸赛】#n将在#C(#00ff00)5分钟#n后开始，请获得选拔赛资格的战队成员尽快进入争霸场景，等待比赛进行！"
JT_GroupTips1 = "您未获得比赛资格，无法进入"
JT_GroupTips2 = "当前不是比赛时间"

JT_SignupSucceed = "恭喜您的战队成功报名跨服争霸小组赛"

JT_GroupMail = "系统"
JT_GroupMailTitle = "跨服战队争霸赛"
JT_GroupMailContent = "恭喜您的战队获得了跨服战队争霸赛#C(#ffff00)小组赛#n资格，请战队队长在今日24：00前点击#C(#00ff00)争霸赛况-小组选择#n进行小组赛分组，逾期未选择分组的战队将由系统随机分配。小组赛比赛时间为#C(#00ff00)周一下午18：30#n，请#C(#ff0000)提前10分钟#n进入比赛地图。#n"

JT_ZB_Tips_1 = "本轮未匹配到比赛对手，比赛获胜"
JT_ZB_Tips_2 = "当前不是竞猜时间"
JT_ZB_Tips_3 = "恭喜你竞猜成功"

JT_FinalMail = "系统"
JT_FinalMailTitle = "跨服战队争霸赛"
JT_FinalMailContent_1 = "恭喜您所在的战队小组赛排名#C(#ffff00)第%s#n，成功晋级跨服战队争霸赛决赛-天榜，比赛将于#C(#00ff00)明日（周二）下午18:30#n开始，请#C(#ff0000)提前10分钟#n进入比赛。比赛分组将于次日公布。"
JT_FinalMailContent_2 = "恭喜您所在的战队小组赛排名#C(#ffff00)第%s#n，成功晋级跨服战队争霸赛决赛-地榜，比赛将于#C(#00ff00)明日（周二）下午18:30#n开始，请#C(#ff0000)提前10分钟#n进入比赛。比赛分组将于次日公布。"

JT_GuessTitle = "跨服战队争霸赛竞猜"
JT_GuessContent = "您参与的%s%s比赛竞猜已经结束，请及时查收竞猜奖励，竞猜结果可在#C(#00FF00)争霸赛况-我的竞猜#n中查看。"

JT_FightTypeName_1 = "天榜"
JT_FightTypeName_2 = "地榜"

JT_FightStep_Name_1 = "32强"
JT_FightStep_Name_2 = "16强"
JT_FightStep_Name_3 = "8强"
JT_FightStep_Name_4 = "半决赛"
JT_FightStep_Name_5 = "决赛"

JT_SR_1 = "冠军"
JT_SR_2 = "亚军"
JT_SR_3 = "季军"



def GetJTFightTypeName(finalType):
	return {1 : JT_FightTypeName_1, 2 : JT_FightTypeName_2}.get(finalType, "")

def GetJTFightStepName(finalStep):
	return {3:JT_FightStep_Name_1, 5 :JT_FightStep_Name_1, 7:JT_FightStep_Name_3, 9 :JT_FightStep_Name_4, 11:JT_FightStep_Name_5}.get(finalStep, "")

def GetGuessMailContent(finalType, finalStep):
	typeName = GetJTFightTypeName(finalType)
	stepName = GetJTFightStepName(finalStep)
	return JT_GuessContent % (typeName, stepName)


JT_FinalTips_0 = "#C(#E87D22)【跨服争霸赛】#n决赛竞猜活动已经开始，竞猜成功将获得高额奖励，快来选出你心目中最中意的战队吧！#C(#00FF00)#U#A(#K(dlg,ZHENGBATWO))前往竞猜#n#n#n"
JT_FinalTips_1 = "#C(#E87D22)【跨服争霸赛】#n恭喜战队#C(#00ff00)%s#n成功晋级决赛，获得角逐跨服争霸赛冠军资格。"
JT_FinalTips_2 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)32强#n比赛将在#C(#00FF00)5分钟#n后开启，请拥有参赛资格的战队马上进入比赛场景准备比赛。"
JT_FinalTips_3 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)16强#n比赛将在#C(#00FF00)5分钟#n后开启，请拥有参赛资格的战队马上进入比赛场景准备比赛。"
JT_FinalTips_4 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)8强#n比赛将在#C(#00FF00)5分钟#n后开启，请拥有参赛资格的战队马上进入比赛场景准备比赛。"
JT_FinalTips_5 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)总决赛#n比赛将在#C(#00FF00)5分钟#n后开启，请拥有参赛资格的战队马上进入比赛场景准备比赛。"

JT_FinalTips_16 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)16强#n比赛将在#C(#00ff00)10分钟#n后开始，请晋级的战队提前进入地图准备。"
JT_FinalTips_8 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)8强#n比赛将在#C(#00ff00)5分钟#n后开始，请晋级的战队提前进入地图准备。"
JT_FinalTips_6 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)半决赛#n比赛将在#C(#00ff00)10分钟#n后开始，请晋级的战队提前进入地图准备。"
JT_FinalTips_7 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)决赛#n比赛将在#C(#00ff00)10分钟#n后开始，请晋级的战队提前进入地图准备。"

JT_FinalTips_9 = "恭喜您所在的战队成功晋级#C(#ffff00)决赛#n，请您在#C(#00FF00)明日（周四）下午19：30#n参加比赛，比赛需#C(#ff0000)提前10分钟#n进入，请及时做好准备。"


JT_FinalTips_10 = "#C(#E87D22)【跨服争霸赛】#n#C(#ffff00)%s#n领取了#C(#00ff00)%s#n全服奖励，感谢#C(#ffff00)%s%s#n#C(#00ff00)%s#n为本服做出的杰出贡献。"
JT_FinalTips_11 = "#C(#E87D22)【跨服争霸赛】#n恭喜战队#C(#00ff00)[%s]%s#n击败全部对手，成为本届跨服战队争霸赛#C(#ffff00)巅峰冠军#n，并开启了全服奖励！#C(#00FF00)#U#A(#K(OPEN_KF_REWARD_PANEL))前往领取#n"


JT_FinalTips_12 = "跨服争霸赛奖励已发放，请通过“玩法奖励”领取，争霸赛冠军请点击“冠军领奖”按钮领取专属奖励。"

JT_FinalTips_21 = "#C(#E87D22)【跨服争霸赛】#n恭喜战队#C(#00ff00)%s#n夺得天榜冠军，战队成员#C(#00ff00)%s#n成功领取了#Z(%s,1)#H。"
JT_FinalTips_22 = "#C(#E87D22)【跨服争霸赛】#n恭喜战队#C(#00ff00)%s#n夺得地榜冠军，战队成员#C(#00ff00)%s#n成功领取了#Z(%s,1)#H。"


JT_FinalGuessServerMsg = "#C(#E87D22)【跨服战队争霸赛】#n争夺赛竞猜活动已经开始，竞猜成功将获得高额奖励，快来选出你心目中最中意的战队吧！#C(#00FF00)#U#A(#K(dlg,ZHENGBATWO))前往竞猜#n#n#n"

###############新增#################
JT_100Title = "跨服争霸赛参赛资格"
JT_100Sender = "系统"
JT_100Content = "您所在的战队由于强大的实力被所有人认可，获得了本届跨服争霸赛%s战区的参赛资格，32强选拔赛将于星期一21:55分开始，请准时参加，比赛必须战队3人同时在比赛场景中才能进行。"

JT_32Title = "32强淘汰赛参赛资格"
JT_32Sender = "系统"
JT_32Content = "恭喜您所在的战队在选拔赛中脱颖而出，成功晋级跨服争霸%s战区32强淘汰赛，比赛将于星期二21:55分开始，请准时参加，比赛必须战队3人同时在比赛场景中才能进行，错过了的比赛场次当弃权处理，请准时参加！"

JT_16Title = "16强淘汰赛参赛资格"
JT_16Sender = "系统"
JT_16Content = "恭喜您所在的战队在32强淘汰赛中脱颖而出，成功晋级跨服争霸%s战区16强淘汰赛，比赛将于星期二22:25分开始，请准时参加，比赛必须战队3人同时在比赛场景中才能进行，错过了的比赛场次当弃权处理，请准时参加！"

JT_8Title = "8强淘汰赛参赛资格"
JT_8Sender = "系统"
JT_8Content = "恭喜您所在的战队在16强淘汰赛中脱颖而出，成功晋级跨服争霸%s战区8强淘汰赛，比赛将于星期三21:55分开始，请准时参加，比赛必须战队3人同时在比赛场景中才能进行，错过了的比赛场次当弃权处理，请准时参加！"

JT_4Title = "总决赛参赛资格"
JT_4Sender = "系统"
JT_4Content = "恭喜您所在的战队在8强淘汰赛中脱颖而出，成功晋级跨服争霸%s战区总决赛赛，比赛将于星期四21:55分开始，请准时参加，比赛必须战队3人同时在比赛场景中才能进行，错过了的比赛场次当弃权处理，请准时参加！"


JT_RewardMailTitle = "跨服争霸赛奖励"
JT_RewardMailSender = "系统"
JT_RewardMailContent1 = "您所在的战队在本届跨服争霸赛参与奖"
JT_RewardMailContent2 = "您所在的战队在本届跨服争霸赛%s战区中获得了第%s名，可喜可贺希望下次能再接再厉，请收下奖励。"

JT_Chuji = "初级"
JT_Jingrui = "精锐"
JT_Dianfeng = "巅峰"

def ReturnJTZhanqu(index):
	ZhanQuDict = {1:JT_Chuji, 2:JT_Jingrui, 3:JT_Dianfeng}
	if index not in ZhanQuDict:
		print 'GE_EXC, ReturnJTZhanqu error index %s' % index
		return
	else:
		return ZhanQuDict[index]
	
JT_EndFight1 = "#C(#E87D22)【跨服争霸赛】“32强选拔赛”#n#C(#00FF00)比赛已经全部结束，获得晋级资格的玩家请准时参加明天的比赛！"
JT_EndFight2 = "#C(#E87D22)【跨服争霸赛】“32强淘汰赛”#n”#C(#00FF00)比赛已经全部结束，获得晋级资格的玩家请准时参加即将开始的#C(#E87D22)“16强淘汰赛”#n！"
JT_EndFight3 = "#C(#E87D22)【跨服争霸赛】“16强淘汰赛”#n”#C(#00FF00)比赛已经全部结束，获得晋级资格的玩家请准时参加明天的比赛！"
JT_EndFight4 = "#C(#E87D22)【跨服争霸赛】“8强淘汰赛”#n”#C(#00FF00)比赛已经全部结束，获得决赛资格的玩家请准时参加明天的总决赛，冠军荣誉即将揭晓！"
JT_EndFight5 = "#C(#E87D22)【跨服争霸赛】“总决赛”#n”#C(#00FF00)已经结束，本届的所有比赛结束，恭喜获胜的战队，下一届再接再厉！比赛奖励将通过邮件发放，获胜战队所在服务器玩家福利可通过争霸福利领取！"

JT_32RoundMsg = "#C(#E87D22)【32强选拔赛】#n#C(#FF0000)第%s场#n#C(#00FF00)比赛正在激烈进行，让我们一起为各位参赛选手进行喝彩吧！"
JT_16RoundMsg = "#C(#E87D22)【32强淘汰赛】#n#C(#FF0000)第%s场#n#C(#00FF00)比赛正在激烈进行，让我们一起为各位参赛选手进行喝彩吧！"
JT_8RoundMsg = "#C(#E87D22)【16强淘汰赛】#n#C(#FF0000)第%s场#n#C(#00FF00)比赛正在激烈进行，让我们一起为各位参赛选手进行喝彩吧！"
JT_4RoundMsg = "#C(#E87D22)【8强淘汰赛】#n#C(#FF0000)第%s场#n#C(#00FF00)比赛正在激烈进行，让我们一起为各位参赛选手进行喝彩吧！"
JT_1RoundMsg = "#C(#E87D22)【总决赛】#n#C(#FF0000)第%s场#n#C(#00FF00)比赛正在激烈进行，冠亚季军的争夺非常激烈，这是王者对战的风范啊，让我们期待即将诞生的至强战队吧！"
JT_NextGrade = "恭喜您的战队获得两场胜利，成功晋级！"
JT_OutGrade = "很遗憾您的战队不幸遭到淘汰！"

#===============================================================================
# 背包加密锁
#===============================================================================
PackagePasswd_UnlockFailedTip = "很抱歉，您输入的密码错误，建议您再想想！如果实在想不起来，您可以选择清除加密锁后重新设置，但是那样您将需要耐心等待7天！"
PackagePasswd_UnlockOkayTip = "您已经成功解锁，本次登录中您可以进行其他相关高级操作了（下线或者顶号需重新输入）。"
PackagePasswd_ResetPasswdUnnecessary = "您当前并未设置加密锁，无需修改密码。"
PackagePasswd_ResetPasswdFailed = "原始密码不正确，无法修改密码。"
PackagePasswd_PasswdCleanning = "清除密码中，清除密码后可重新设置密码"
PackagePasswd_ResetPasswdOkay = "您的加密锁修改成功，重新登录后做危险操作将需输入新的加密锁解锁，如果您忘记密码，请使用“清除加密锁”功能。"
PackagePasswd_ClearPasswdOkay = "您已经申请了清除加密锁，将于%s天%s小时%s分钟后生效，届时您可以重新设置加密锁"
PackagePasswd_ClearPasswdRequest = "您当前已经申请清除加密锁，请耐心等待7天后系统清除加密锁。"
PackagePasswd_ClearPasswdSuccess = "清除加密锁成功"
PackagePasswd_SetPasswdOkay = "您的加密锁设置成功，重新登录后做高级操作将需输入加密锁解锁，如果您要重新修改加密锁，可以选择“修改密码”。"
PackagePasswd_SetPasswdFailed = "您已经设置了加密锁，无需再次设置，若需要修改密码请选择修改加密锁。"

#===============================================================================
#祝福轮盘
#===============================================================================
BlessRoulette_Tips_Reward_Head = "恭喜你获得#H"
BlessRoulette_Tips_Reward_Item = "#Z(%s,%s)#H"
#===============================================================================
# 豪气冲天
#===============================================================================
Haoqi_Title = "【豪气冲天】跨服排名奖励"
Haoqi_Sender = "系统"
Haoqi_Content = "恭喜！您在#C(#E87D22)【豪气冲天】#n活动中跨服排名第%s，达到了排名奖励标准，获得了丰厚奖励！"
HaoqiLocal_Title = "【豪气冲天】本服排名奖励"
HaoqiLocal_Sender = "系统"
HaoqiLocal_Content = "恭喜！您在#C(#E87D22)【豪气冲天】#n活动中本服排名第%s，达到了排名奖励标准，获得了丰厚奖励！"
HaoqiReward_Title = "【豪气冲天】充值奖励"
HaoqiReward_Sender = "系统"
HaoqiReward_Content = "由于您的背包已满, 系统已将【豪气冲天】充值奖励暂时保存于邮件附件中。请尽快整理您的背包，预留足够的背包格子，并且在7天内提取附件中的物品。"

#===============================================================================
#团购嘉年华
#===============================================================================
GBC_Tips_Reward_Head = "恭喜你获得#H"
GBC_Tips_Reward_Item = "#Z(%s,%s)#H"
GBC_Tips_LastFiveMinute_Limit = "本轮团购已结束"

#===============================================================================
# 双十一秒杀汇
#===============================================================================
SECKILL_ITEM_CNT_OVER_PROMPT = "当前商品已卖光，请下次抓紧时间哦"
SECKILL_ITEM_TIME_OVER_PROMPT = "当前商品已过期，请下次抓紧时间哦"
SECKILL_START_HEARSAY = "#C(#E87D22)【双十一狂欢】#n新一轮秒杀汇活动开始了，超级优惠的价格，还在等什么？快快来抢购吧！！"
#===============================================================================
# 宠物福田
#===============================================================================
PetLuckyFarmTips = "恭喜获得："
PetLuckFarmBroadcast_1 = "#C(#E87D22)【宠物福田】#n#C(#00EE00)%s#n在宠物福田采集过程中好运爆棚，挖到了"
PetLuckFarmBroadcast_2 = "实在是太令人羡慕了！"
PetLuckFarmItemTips = "#Z(%s,%s)，"
PetLuckFarmTarotTips = "#t(#K(sTT,%s,%s))，"

#===============================================================================
# 龙魂石碑
#===============================================================================
DragonStele_Tips_Head = "得到神龙祝福，获得：#H"
DragonStele_Tips_Item = "#Z(%s,%s)#H"
DragonStele_Msg_Item = "#Z(%s,%s)"
DragonStele_Tips_Tarot = "#t(#K(sTT,%s,%s))#H"
DragonStele_Msg_Tarot = "#t(#K(sTT,%s,%s))"
DragonStele_Msg_Precious = "#C(#00EE00)%s#C(#E87D22)诚心祈祷，感动了龙神，得到了%s真是让人羡慕啊！"
DragonStele_Msg_Extra = "#C(#00EE00)%s#C(#E87D22)祈祷满一百次，获得了龙神眷顾，额外得到了%s真是让人羡慕啊！"
DragonStele_Msg_Sep = " "

#================================================================================
#蓝钻献大礼
#=================================================================================
QQLZGift_Tips_Reward_Head = "恭喜你获得#H"
QQLZGift_Tips_Reward_Item = "#Z(%s,%s)#H"
QQLZGift_Tips_Reward_Master = "#C(#FFFF00)白羊圣骑#C(#E87D22)"
DragonStele_Msg_Sep = " "

#===============================================================================
# 结婚派对
#===============================================================================
PartyNotBegin = "派对暂未开启"
PartyBless_Title = "【系统】结婚派对"
PartyBless_Sender = "系统"
PartyBless_Content = "#C(#00EE00)%s#n祝福了你们"
PartyBless_Content_2 = "#C(#00EE00)%s#n祝福了您们并送上%s，但是由于今日可领取的祝福奖励已达上限，无法获得祝福礼盒。"
PartyCandy_Title = "【系统】结婚派对"
PartyCandy_Sender = "系统"
PartyCandy_Content = "#C(#00EE00)%s#n和ta的伴侣#C(#00EE00)%s#n发放的派对喜糖奖励请查收。"
PartyBeginNormal = "#C(#E87D22)【结婚派对】#n#C(#00EE00)%s#n与玩家#C(#00EE00)%s#n举行了一场#C(#00EE00)%s#n,大家快去点击新人送上祝福吧！#C(#00ff00)#U#A(#K(ENTER_PARTY_SCENE,%s,%s))立即前往！#n#n#n"
PartyBeginKuafu = "#C(#E87D22)【结婚派对】#n#C(#00EE00)%s#n与玩家#C(#00EE00)%s#n举行了一场#C(#00EE00)%s#n,大家快去点击新人送上祝福吧！#C(#00ff00)#U#A(#K(ENTER_KFPARTY_SCENE,%s,%s))立即前往！#n#n#n"
PartyEnd = "#C(#E87D22)【结婚派对】#n#C(#00EE00)%s#n与#C(#00EE00)%s#n的#C(#00EE00)%s#n派对已结束，感谢大家的参与"
PartyOneMinuteTips = "#C(#E87D22)【结婚派对】#n#C(#00EE00)%s#n和#C(#00EE00)%s#n派对1分钟后结束，请大家尽情庆祝"
PartyGrade_1 = "高档派对"
PartyGrade_2 = "豪华派对"
PartyGrade_3 = "跨服派对"
PartyWorldInvite_Logic = "#C(#E87D22)【结婚派对】#n玩家#C(#00EE00)%s#n与玩家#C(#00EE00)%s#n举行了一场#C(#00EE00)%s#n，大家快去送上祝福吧！#C(#00ff00)#U#A(#K(ENTER_PARTY_SCENE,%s,%s))立即前往#n#n#n"
PartyWorldInvite_Kuafu = "#C(#E87D22)【结婚派对】#n玩家#C(#00EE00)%s#n与玩家#C(#00EE00)%s#n举行了一场#C(#00EE00)%s#n，大家快去送上祝福吧！#C(#00ff00)#U#A(#K(ENTER_KFPARTY_SCENE,%s,%s))立即前往#n#n#n"

PartyCandy_1 = "高档喜糖"
PartyCandy_2 = "豪华喜糖"
PartyCandy_3 = "跨服喜糖"
PartyCandy = "#C(#E87D22)【结婚派对】#n#C(#00EE00)%s#n和ta的伴侣#C(#00EE00)%s#n果真是一方土豪，给参与派对的所有玩家发放了#C(#00EE00)%s#n！"
PartyBless_1 = "普通祝福"
PartyBless_2 = "豪华祝福"
PartyBless = "#C(#E87D22)【结婚派对】#n#C(#00EE00)%s#n一掷千金，送给新人#C(#00EE00)%s#n和#C(#00EE00)%s#n#C(#E87D22)%s#n"
PartyNotOnLine = "邀请的伴侣不在线"
def ReturnBlessGrade(grade):
	blessGradeDict = {1:PartyBless_1, 2:PartyBless_2}
	if grade not in blessGradeDict:
		print 'GE_EXC, ReturnBlessGrade error grade %s' % grade
		return
	else:
		return blessGradeDict[grade]
def ReturnCandyGrade(grade):
	candyGradeDict = {1:PartyCandy_1, 2:PartyCandy_2, 3:PartyCandy_3}
	if grade not in candyGradeDict:
		print 'GE_EXC, ReturnCandyGrade error grade %s' % grade
		return
	else:
		return candyGradeDict[grade]
def ReturnPartyGrade(grade):
	partyGradeDict = {1:PartyGrade_1, 2:PartyGrade_2, 3:PartyGrade_3}
	if grade not in partyGradeDict:
		print 'GE_EXC, ReturnPartyGrade error grade %s' % grade
		return
	else:
		return partyGradeDict[grade]

PartyKuafuFull = "本次跨服派对参与人数已达上限"

PartyAuctionSuccessTitle = "跨服竞价成功"
PartyAuctionSender = "系统"
PartyAuctionSuccessContent = "您与您的伴侣在跨服派对中以最高竞价打败各路富豪，获得今日跨服派对资格，请您与您的伴侣19:30-19:50准时出席跨服派对，炫出你的豪富派对吧！"

PartyAuctionFailTitle = "跨服竞价失败"
PartyAuctionFailContent = "您的跨服派对竞价已被#C(#00EE00)%s#n竞价超越，导致跨服派对竞拍失败，您竞价的跨服币原额返还，请查收附件！"


PartyAuctionFailTitle_2 = "跨服派对开启失败"
PartyAuctionFailContent_2 = "您与您的伴侣在跨服派对中以最高竞价打败各路富豪，获得今日跨服派对资格，但是由于您在举办派对之前意外离婚，我们只能遗憾的通知您：今日的跨服派对将取消举办，您的跨服派对竞拍费用也不能获得返还！"

PartyKuafuInviteSuccess = "您已经向所有服务器发送了跨服派对邀请，宾客即将前来庆祝"
PartyAuctionRumor = "#C(#E87D22)【跨服派对】#n#C(#FFFF00)我们的恩爱，在跨服盛开，让全世界都知道我们的爱！！！#n跨服派对正在火热进行中，您还在等什么，快去竞拍您们的情深似海吧！！#C(#00ff00)#U#A(#K(ENTER_KFPARTY_JP))我要竞拍#n#n#n"
PartyAuctionSuccess = "#C(#E87D22)【跨服派对】#n#C(#00EE00)%s#n与#C(#00EE00)%s#n在跨服派对中以最高竞价打败各路富豪，获得今日跨服派对资格，即将在19:30举行一场盛大的#C(#00EE00)跨服派对#n，豪宴喜糖多多，大家务必记得准时前往！"

PartyFlower = "#C(#00FF00)%s#n在全场为#C(#00FF00)两位新人#n抛洒花瓣，祝福他们永结同心，喜庆度增加#C(#00FF00)39#n，真是一方土豪啊！"
PartyFireworks = "#C(#00FF00)%s#n在全场为#C(#00FF00)两位新人#n点燃激情四射的烟花，祝愿他们#C(#00FF00)天荒地老永远幸福#n，喜庆度增加#C(#00FF00)499#n，真是土豪中的浪漫天使啊！！"

PartyHostFlower = "#C(#00FF00)%s#n在全场为#C(#00FF00)心爱的伴侣#n抛洒花瓣，表达永恒不变的爱意，喜庆度增加#C(#00FF00)39#n，让我们为他们欢呼吧！"
PartyHostFireworks = "#C(#00FF00)%s#n在全场为#C(#00FF00)心爱的伴侣#n点燃激情四射的烟花，献上#C(#00FF00)我要我爱人的永远幸福#n的甜蜜爱语，喜庆度增加#C(#00FF00)499#n，让我们祝他们永远相爱！"

PartyHappyTitle = "跨服派对新人礼盒补领"
PartyHappySender = "系统"
PartyHappyContent = "由于您在跨服派对中漏领取喜庆度达到10000的新人礼盒，我们特专机为您送上礼盒，祝您和您的爱人永远幸福！"
PartyHappyReward = "礼盒领取成功，请回本服在背包查看"

#===============================================================================
# 亲密
#===============================================================================
QinmiLvUp = "升级成功！"
#===============================================================================
#步步高升
#===============================================================================
StepByStepBroadCast = "#C(#00FF00)%s#n在步步高升活动中开启了#C(#0DF6FF)%s#n，获得了大量奖励，周边的小伙伴都惊呆了。"
StepByStepTips = "恭喜你获得奖励："

#===============================================================================
# 众神秘宝
#===============================================================================
GODS_TREASURE_ONE_SUCCESS_PROMPT = "探宝成功，获得#Z(%s,%s)"
GODS_TREASURE_SUCCESS_PROMPT = "探宝成功，获得%s"
GODS_TREASURE_ITEM_PROMPT = "#Z(%s,%s)#H"
GODS_TREASURE_GOOD_ITEM_HEARSAY = "#C(#E87D22)【众神秘宝】#C(#00FF00)%s#C(#FFFFFF)在神殿探宝千百度，默默的找到神灵埋下的秘宝：#Z(%s,%s)。#C(#00ff00)#U#A(#K(openZSMB))前往探宝#n#n"

#===============================================================================
# 狂欢感恩节-充值送豪礼
#===============================================================================
TG_RechargeReward_Tips_Head = "抽奖成功 获得："
TG_RechargeReward_Tips_Item = "#Z(%s,%s)"
TG_RechargeReward_Msg_Precious_Item = "#C(#E87D22)【狂欢感恩节】#n玩家【#C(#00EE00)%s#n】在充值送豪礼中获得#Z(%s,%s)"
TG_RechargeReward_Msg_Precious_CDK = "#C(#E87D22)【狂欢感恩节】#n玩家【#C(#00EE00)%s#n】在充值送豪礼中获得蓝钻CDK，威武霸气！"
TG_RechargeReward_Tips_MailPrompt = "恭喜你中了CDK 请稍后查收邮件内容" 
TG_RechargeReward_Mail_CDK_TiTle = "充值送豪礼CDK奖励"
TG_RechargeReward_Mail_CDK_Sender = "充值送豪礼" 
TG_RechargeReward_Mail_CDK_Content = "尊敬的龙骑士： #H您好，恭喜您在感恩节活动中获得蓝钻开通一个月奖励（ctrl+c复制CDK号码：#C(#00ff00)%s#n），小伙伴们加油吧！#W(http://qqgame.qq.com/act/a20090223cdkey/cdkey.htm)#U#C(#00ff00)请点击此进行兑换#n。#n#n#H若有其他疑问，欢迎您随时向我们提出您的问题，我们会为您进行跟进解答。您的支持是我们持续的动力！ #H注：每个QQ号码1天最多可兑换12次（多余CDK可次日再兑换），开通月数是可以叠加的哦~#H—————————————《龙骑士传》研发与运营团队全体成员敬上"

#===============================================================================
# 狂欢感恩节-在线赢大礼
#===============================================================================
TG_OnlineReward_Tips_Head = "领取成功 获得：#H"
TG_OnlineReward_Tips_Item = "#Z(%s,%s)#H"
TG_OnlineReward_Tips_Money = "#C(#FFFF00)金币+ %s#H"
TG_OnlineReward_Tips_BindRMB = "#C(#0099FF)魔晶+ %s#H"
TG_OnlineReward_Tips_ExtraTimes = "抽奖次数 +%s"

#===============================================================================
# 切火鸡
#===============================================================================
CutTurkeyFail = "切火鸡失败，获得参与奖励：#Z(%s,%s)"
CutTurkeySuccess = "感恩节快乐，获得：#Z(%s,%s)"
#===============================================================================
# 北美流失召回
#===============================================================================
NARoleBack_TITKE = "流失召回"
NARoleBack_SENDER = "系统"
NARoleBack_DESC = "流失内容"

#===============================================================================
# 盛宴摩天轮
#===============================================================================
FeastWheel_Tips_Head = "恭喜您 获得：#H"
FeastWheel_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 爱在一起
#===============================================================================
LoveTogether_Tips_Head = "恭喜您 获得：#H"
LoveTogether_Tips_Item = "#Z(%s,%s)#H"
LoveTogether_Tips_Money = "#C(#FFFF00)金币+ %s#H"
LoveTogether_Tips_BindRMB = "#C(#0099FF)魔晶+ %s#H"
LoveTogether_Tips_FWTimes = "幸运摩天轮抽奖次数 +%s#H"

#===============================================================================
# 好运币专场
#===============================================================================
LuckyCoinLottery_Precious_Msg = "#C(#00FF00)%s#n在2015狂欢派对活动中的#C(##00FF00)好运币专场#n人品爆发,抽中：#Z(%s,%s)的奖励,真是羡慕妒忌恨啊!"
LuckyCoinLottery_Tips_Head = "恭喜您 获得：#H"
LuckyCoinLottery_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 团购派对
#===============================================================================
GroupBuyParty_Tips_Head = "购买成功，获得：#H"
GroupBuyParty_Tips_Item = "#Z(%s,%s)#H"
GroupBuyParty_Tips_LastFiveMinute_Limit = "本轮团购已结束"
GroupBuyParty_Tips_FirstOneMinute_Limit = "本轮团购未开始"
#===============================================================================
# 七日目标邮件
#===============================================================================
KaifuTarget_MTitle = "七日目标奖励"
KaifuTarget_MSender = "系统"
KaifuTarget_MContent = "恭喜您，你在第%s天的七日目标排行榜中排行第%s。奖励已发送，请注意查收"
KaifuTarget_MContent_2 = "恭喜您，你在七日目标-冲级榜排行榜中排行第%s。奖励已发送，请注意查收"
KaifuTarget_MContent_3 = "恭喜您，你在七日目标-总战力排行榜中排行第%s。奖励已发送，请注意查收"
KaifuTarget_EndTips = "#C(#E87D22)【七日目标】#n—#C(#00FF00)%s#n已结束，#C(#00FF00)%s#n力压全服夺得第一名，获得丰厚奖励"
KaifuTarget_EndTips_2 = "#C(#E87D22)【七日目标】#n—#C(#00FF00)冲级榜#n已结束，#C(#00FF00)%s#n力压全服夺得第一名，获得丰厚奖励"
KaifuTarget_EndTips_3 = "#C(#E87D22)【七日目标】#n—#C(#00FF00)总战力#n已结束，#C(#00FF00)%s#n力压全服夺得第一名，获得丰厚奖励"
#===============================================================================
# 北美通用活动邮件
#===============================================================================
HalloweenNA_TITLE = "题目"
HalloweenNA_SENDER = "发邮人"
HalloweenNA_CONTENT = "内容"

AddTemp_Bless = "星灵临时祝福值+%s"

#===============================================================================
# 蓝钻豪华六重礼
#===============================================================================
QQLZLuxuryGift_Tips_Head = "领取成功，获得：#H"
QQLZLuxuryGift_Tips_Item = "#Z(%s,%s)#H"
QQLZLuxuryGift_Precious_Msg = "#C(#00FF00)%s#n在蓝钻豪华六重礼活动中成功领取：#Z(%s,%s)的奖励,真是羡慕妒忌恨啊!"

#===============================================================================
# 祖玛
#===============================================================================
ZUMA_EXPLODE_SCORE_PROMPT = "消除+ %s分"
ZUMA_COMBO_SCORE_PROMPT = "连锁%s次+ %s分"
ZUMA_RMB_HEARSAY = "#C(#EE7600)【天天消龙珠】#n玩游戏也能得神石！#C(#00FF00)%s#n在游戏中获得了#Z(%s,%s)，#C(#00ff00)#U#A(#K(dlg,OPEN_MARBLE_FRAME))我也要玩！#n#n#n"

#===============================================================================
# 圣诞许愿树
#===============================================================================
ChristmasWishTree_Tips_Head = "购买成功，获得：#H"
ChristmasWishTree_Tips_Item = "#Z(%s,%s)#H"

Christmas_Tips_ConsumeEXp = "恭喜获得%s圣诞活动积分" 

#===============================================================================
# 圣诞羽翼转转乐
#===============================================================================
ChristmasWingLottery_Tips_Head = "抽奖成功，获得：#H"
ChristmasWingLottery_Tips_Item = "#Z(%s,%s)#H"
ChristmasWingLottery_Precious_Msg = "#C(#00FF00)%s#n在圣诞羽翼转转乐活动中抽奖获得：#Z(%s,%s)的奖励,真是羡慕妒忌恨啊!"

#===============================================================================
# 圣诞坐骑转转乐
#===============================================================================
ChristmasMountLottery_Tips_Head = "抽奖成功，获得：#H"
ChristmasMountLottery_Tips_Item = "#Z(%s,%s)#H"
ChristmasMountLottery_Precious_Msg = "#C(#00FF00)%s#n在圣诞坐骑转转乐活动中抽奖获得：#Z(%s,%s)的奖励,真是羡慕妒忌恨啊!"

#===============================================================================
# 圣诞时装秀
#===============================================================================
ChristmasFashionShow_Tips_Head = "购买成功，获得：#H"
ChristmasFashionShow_DonateTips_Head = "赠送成功，获得返利：#H"
ChristmasFashionShow_Tips_Item = "#Z(%s,%s)#H"
ChristmasFashionShow_Tips_NotLocalServer = "非本服好友，不能赠送"
ChristmasFashionShowMail_Title = "您收到赠送"
ChristmasFashionShowMail_Sender = "系统"
ChristmasFashionShowMail_Content = "你收到来自#C(#00EE00)%s#n赠送的#Z(%s,%s)"
#===============================================================================
# 圣诞嘉年华 -- 有钱就是任性
#===============================================================================
ChristmasHao_Title = "【圣诞嘉年华】跨服积分排名奖励"
ChristmasHao_Sender = "系统"
ChristmasHao_Content = "恭喜！您在#C(#E87D22)【圣诞嘉年华-有钱就是任性】#n活动中跨服排名第%s，达到了排名奖励标准，获得了丰厚奖励！"

ChristmasHaoReward_Title = "【圣诞嘉年华】跨服积分排名奖励"
ChristmasHaoReward_Sender = "系统"
ChristmasHaoReward_Content = "由于您的背包已满, 系统已将【圣诞嘉年华-有钱就是任性】充值奖励暂时保存于邮件附件中。请尽快整理您的背包，预留足够的背包格子，并且在7天内提取附件中的物品。"
#===============================================================================
# 占卜
#===============================================================================
TarotGradeTips = "#C(#FF6600)【占卜】#C(#FFFFFF)恭喜玩家#C(#66FF00)%s#C(#FFFFFF)人品大爆发,通过占卜获得#C(#FFFF00)#t(#K(sTT,%s,%s))#H"
TarotSuperSuccess = "超级占卜成功"
#===============================================================================
# 元旦活动-- 在线奖励
#===============================================================================
HolidayOnlineReward_Tips_Head = "领取成功，获得：#H"
HolidayOnlineReward_Tips_Item = "#Z(%s,%s)#H"
HolidayOnlineReward_Tips_prayTimes = "祈福次数 +%s#H"
HolidayOnlineReward_Tips_Money = "金币 +%s#H"

#===============================================================================
# 元旦活动-- 充值抽奖
#===============================================================================
HolidayRechargeReward_Tips_Head = "领取成功，获得：#H"
HolidayRechargeReward_Tips_LotteryTimes = "抽奖次数 +%s#H"

HolidayLotteryReward_Tips_Head = "恭喜你成功获得：#H"
HolidayLotteryReward_Tips_Item = "#Z(%s,%s)#H"
HolidayLotteryReward_Msg_Precious = "#C(#E87D22)【元旦大狂欢】#n%s在#C(#00ff00)充值开宝箱#n活动中获得了#Z(%s,%s)，真是令人羡慕！#C(#00ff00)#U#A(#K(OPEN_YUANDAN_PANEL,2))前往抽奖！#n#n#n"

#===============================================================================
# 元旦购物节
#===============================================================================
HolidayShoppingTips = "#C(#E87D22)【元旦大狂欢】#n在全服玩家的努力下，跨年购物节活动#C(#00ff00)%s#n分的积分奖励已被开启。#C(#00ff00)#U#A(#K(OPEN_YUANDAN_PANEL,1))前往领取#n#n#n"
HShoppingMailTitle_1 = "元旦跨年购物节"
HShoppingMailSender_1 = "系统"
HShoppingMailContent_1 = "由于您的背包已满，您在元旦跨年购物节中购买的物品通过邮件发放。"
HShoppingMailTitle_2 = "元旦跨年购物节"
HShoppingMailSender_2 = "系统"
HShoppingMailContent_2 = "由于您的背包已满，您在元旦跨年购物节中领取的积分奖励礼包通过邮件发放。"
#===============================================================================
# 元旦金币祈福
#===============================================================================
HolidayWishTips = "祈福成功，获得#Z(%s,%s)"
HWishMailTitle = "元旦金币祈福礼"
HWishMailSender = "系统"
HWishMailContent = "由于您的背包已满，您在元旦金币祈福礼许愿获得的物品通过邮件发放。"

#===============================================================================
# 豪华蓝钻转大礼
#===============================================================================
QQLZLuxuryRoll_Tips_Head = "领奖成功，获得：#H"
QQLZLuxuryRoll_Tips_HeadEx = "兑换成功，获得：#H"
QQLZLuxuryRoll_Tips_Item = "#Z(%s,%s)#H"
QQLZLuxuryRoll_Tips_Crystal = "蓝钻水晶 +%s#H"

#===============================================================================
# 新年活动
#===============================================================================
NYEAR_ONLINE_REWARD_ITEM_MSG = "【2015狂欢派对】%s在2015狂欢派对活动中获得了#Z(%s,%s)，真是令人羡慕！前往抽奖"
NYEAR_ONLINE_REWARD_TAROT_MSG = "【2015狂欢派对】%s在2015狂欢派对活动中获得了#t(#K(sTT,%s,%s))，真是令人羡慕！前往抽奖"
NYEAR_ONLINE_REWARD_CARD_MSG = "【2015狂欢派对】%s在2015狂欢派对活动中获得了#L(%s,%s)，真是令人羡慕！前往抽奖"
NYEAR_ONLINE_REWARD_ITEM_MSG = "#C(#E87D22)【2015狂欢派对】#n#C(#00ff00)%s#n在2015狂欢派对活动中获得了#Z(%s,%s)，真是令人羡慕！#C(#00ff00)#U#A(#K(open_newyear_panel2))前往抽奖！#n#n#n"
NYEAR_ONLINE_REWARD_TAROT_MSG = "#C(#E87D22)【2015狂欢派对】#n#C(#00ff00)%s#n在2015狂欢派对活动中获得了#t(#K(sTT,%s,%s))，真是令人羡慕！#C(#00ff00)#U#A(#K(open_newyear_panel2))前往抽奖！#n#n#n"
NYEAR_ONLINE_REWARD_CARD_MSG = "#C(#E87D22)【2015狂欢派对】#n#C(#00ff00)%s#n在2015狂欢派对活动中获得了#L(%s,%s)，真是令人羡慕！#C(#00ff00)#U#A(#K(open_newyear_panel2))前往抽奖！#n#n#n"
NYEAR_ONLINE_FREE_TIMES_MSG = "2015狂欢派对免费开启宝箱次数+%s#H"
NYEARHao_Title = "【2015狂欢派对】跨服充值排名奖励"
NYEARHao_Sender = "系统"
NYEARHao_Content = "恭喜！您在#C(#E87D22)【2015狂欢派对-狂欢冲冲冲】#n活动中跨服排名第%s，达到了排名奖励标准，获得了丰厚奖励！"

NYEARHaoReward_Title = "【2015狂欢派对】本服充值排名奖励"
NYEARHaoReward_Sender = "系统"
NYEARHaoReward_Content = "恭喜！您在#C(#E87D22)【2015狂欢派对-狂欢冲冲冲】#n活动中本服排名第%s，达到了排名奖励标准，获得了丰厚奖励！"

NYEAR_DISCOUNT_REFRESH = "已消耗%s积分，刷新成功！"

#===============================================================================
# 公会神兽
#===============================================================================
UnionShenShouDisappear = "【神兽挑战】公会神兽#C(#00FF00)%s#n全身雷光闪烁，腾空而去，离开公会驻地，请大家明天再召唤！"
UnionShenShouChallengeFail = "神兽挑战失败，获得战斗奖励"
UnionShenShouChallengeSuccess = "神兽挑战成功，获得战斗奖励"
UnionShenShouChallengeSuccessAll = "#C(#E87D22)【神兽挑战】#n#C(#00FF00)%s#n#C(#FFFFFF)神勇无敌，挑战神兽成功，神兽口吐%s,飞入#C(#ff0000)公会商店#n，大家快去抢购啊！#C(#00ff00)#U#A(#K(OPEN_UNION_SHOP_PANEL))前往购买#n"
UnionShenShouChallengeLimitCnt = "今日挑战次数已达上限"
UnionShenShouCallSuccess = "神兽召唤操作成功"
UnionShenShouCallSuccessAll = "#C(#E87D22)【神兽召唤】#n平地起惊雷，公会神兽#C(#00FF00)%s#n随着一道闪电出现在公会驻地，请大家前往挑战，获得丰厚奖励！"
UnionShenShouCallLimitCnt = "今日已召唤神兽，请明日再召唤"
UnionShenShouGrowthValueNotEnough = '神兽成长值不足，召唤失败'
UnionShenShouUpGradeOkayAll = "#C(#E87D22)【神兽升级】#n#C(#FFFFFF)经过大家不懈的努力，公会神兽升阶为#C(#00FF00)%s#n，召唤后即可获得更多的奖励，快去喂养吧！#n"
UnionShenShouUpGradeOkay = "神兽升阶操作成功"
UnionShenShouFeedOkay = "喂养成功，获得个人贡献%s，神兽成长%s"
UnionShenShouUpperFeedOkay = "#C(#E87D22)【神兽喂养】#n#C(#00FF00)%s#n#C(#FFFFFF)从口袋中掏出一把神石高级喂养神兽，神兽成长值增加#n#C(#00FF00)%s点#n#C(#FFFFFF)，乐得神兽嗷嗷大叫：好爽啊，多喂我一点吧！"
UnionShenShouPerfectFeedOkay = "#C(#E87D22)【神兽喂养】#n#C(#00FF00)%s#n#C(#FFFFFF)挥毫撒神石，神兽瞬间完美成熟，正在公会嗷嗷撒娇：求召唤！求挑战！"
UnionShenShouFeedFull = "#C(#E87D22)【神兽喂养】#n#C(#00FF00)%s#n#C(#FFFFFF)已经成熟，正在公会嗷嗷撒娇：快来召唤我吧！快来请挑战我吧！"
UnionShenShouBlessingOkay = "祝福成功，在神兽战斗中攻击力%s%%"
UnionShenShouFeedAfterFull = "喂养成功，获得个人贡献+%s"

UnionShenShouHurtRankMailTitle = "公会神兽排行奖励"
UnionShenShouHurtRankMailSender = "系统"
UnionShenShouHurtRankMailCotent = "您昨日在公会神兽挑战中伤害排名第%s,获得排名奖励,请尽快提取！"

UnionShenShouChallengeTime = "#C(#fbfe00)今日神兽挑战还剩余%s次#n"
#===============================================================================
# 公会建筑
#===============================================================================
UnionBuildingLevelUpAll = "#C(#E87D22)【建筑升级】#n#C(#FFFFFF)经过我们的共同努力，公会#n#C(#FEFB00)%s#n#C(#FFFFFF)提升到#C(#FEFB00)%s级#n#C(#FFFFFF)，让我们一起享受成果吧！"
UnionBuildingLevelUp = "升级操作成功"
UnionMagicTower = "魔法塔"
UnionShenShoutan = "神兽坛"
UnionStore = "商店"
#===============================================================================
# 公会技能
#===============================================================================
UnionSkillResearchSuccessAll = "#C(#E87D22)【技能研究】#n#C(#00FF00)%s#n#C(#FFFFFF)开启了#C(#FEFB00)%s技能#n研究，请大家务必保证每小时有充足的公会资源！"
UnionSkillResearchSuccess = "技能研究操作成功"
UnionSkillResearchPause = "#C(#E87D22)【技能研究】#n#C(#FEFB00)%s#n #C(#FFFFFF)由于公会资源不足暂停研究，请大家尽快增加公会资源，保证技能恢复研究！"
UnionSkillResearchGoOn = "#C(#E87D22)【技能研究】#n#C(#FEFB00) %s技能#n #C(#FFFFFF)由于公会资源充足，继续开始研究！"
UnionSkillLearnOkay = "技能学习成功"
UnionSkillActiveOkay = "技能重新激活"
UnionSkillTimeOut = "您有公会技能过期，请前往公会技能重新激活"
UnionSkillResearchOkay = "#C(#E87D22)【技能研究】#n#C(#FFFFFF)经过大家共同努力，#n#C(#FEFB00) %s#n #C(#FFFFFF)研究成功，大家可前往工会技能学习！"
#===============================================================================
# 公会商店
#===============================================================================
UnionStoreActiveGoodOkay = "商品激活操作成功"
UnionStoreActiveGoodOkayAll = "#C(#E87D22)【商店激活】#n#C(#FFFFFF)经过大家不懈的努力，公会商店开始出售#Z(%s,%s)，大家快去商店购买吧！"
UnionGoodBuyOkay = "购买成功"
UnionGoodNoLeft = "商品已售空"


#===============================================================================
# 勇者试炼场
#===============================================================================
DailyFB_Tips_Head = "顺利通关"
DailyFB_Tips_Item = "#Z(%s,%s)#H"
DailyFB_Tips_Money = "金币 +%s#H"
DailyFB_Tips_Exp = "经验 +%s#H"
DailyFB_Tips_MaxFight = "你击杀怪物数量已达到今日最大击杀上限，已传出试炼场景"
DailyFB_Tips_AfterNewDayFail = "试炼场在每日00:00重置后自动传出场景"
DailyFB_Name_0 = "试炼场"
DailyFB_Name_1 = "初级试炼场，获得：#H"
DailyFB_Name_2 = "中级试炼场，获得：#H"
DailyFB_Name_3 = "高级试炼场，获得：#H"
def GetDailyFBNameByLevel(FBLevel):
	DailyFB_Name_Dict = {1:DailyFB_Name_1, 2:DailyFB_Name_2, 3:DailyFB_Name_3}
	return DailyFB_Name_Dict.get(FBLevel, DailyFB_Name_0)
	

#===============================================================================
# 称号
#===============================================================================
Title_tips_1 = "培养成功，经验增加%s"
Title_tips_2 = "培养成功，出现暴击经验增加%s"
Title_tips_3 = "培养成功，出现了%s次暴击，获得了%s经验"
Title_tips_Star = "恭喜，升星成功"
Title_RepeatTitle = "您已经拥有了此称号！"
#===============================================================================
# 豪华蓝钻转大礼
#===============================================================================
QQHZRoll_Tips_Head = "领奖成功，获得：#H"
QQHZRoll_Tips_HeadEx = "兑换成功，获得：#H"
QQHZRoll_Tips_Item = "#Z(%s,%s)#H"
QQHZRoll_Tips_Crystal = "黄钻水晶 +%s#H"
#===============================================================================
# 商城赠送
#===============================================================================
MALL_GIVING_MSG = '对方等级不足，无法赠送'
MALL_GIVING_TITLE = "您收到赠送"
MALL_GIVING_SENDER = "系统"
MALL_GIVINT_DESC = "#C(#00FF00)%s#n给你赠送了一份豪华大礼，赶紧查收吧！！"
MALL_GIVING_GETED_MSG = "您获得了%s赠送的#Z(%s,%s)，请在邮件中查收"
MALL_GIVING_SUC = "赠送成功"

#===============================================================================
# 七日争霸
#===============================================================================
SevenDayHegemony_MTitle = "七日争霸奖励"
SevenDayHegemony_MSender = "系统"
SevenDayHegemony_MContent = "恭喜您，你在七日争霸活动中的 #C(#00FF00)%s#n排行榜中排行第 #C(#00FF00)%s#n。奖励已发送，请注意查收。"
SevenDayHegemony_MContent_Union = "恭喜您，你的公会在七日争霸活动中的#C(#00FF00)公会争霸#n排行榜中排行第 #C(#00FF00)%s#n。奖励已发送，请注意查收。"

SevenDayHegemonyGlobalTell_UnionFb = "#C(#E87D22)【七日争霸】#n—#C(#E87D22)公会争霸#n已结束，公会 #C(#00FF00)%s#n力压全服夺得第一名，全公会成员获得丰厚奖励。"
SevenDayHegemonyGlobalTell_TeamTower = "#C(#E87D22)【七日争霸】#n—#C(#E87D22)爬塔争霸#n已结束， #C(#00FF00)%s#n力压全服夺得第一名，获得丰厚奖励。"
SevenDayHegemonyGlobalTell_Purgatory = "#C(#E87D22)【七日争霸】#n—#C(#E87D22)心魔争霸#n已结束， #C(#00FF00)%s#n力压全服夺得第一名，获得丰厚奖励。"


#===============================================================================
# 女神卡牌
#===============================================================================
GODDESS_CARD_ALREADY_FINAL_PROMPT = "本轮已进行终极开启"
GODDESS_CARD_REWARD_HEARSAY = "#C(#FF6600)【女神卡牌】#C(#FFFFFF)恭喜玩家#C(#66FF00)%s#C(#FFFFFF)受到女神的青睐,在女神卡牌中获得#Z(%s,%s)"

#===============================================================================
# 龙骑试炼
#===============================================================================
DKC_Tips_Head = "试练成功通关，获得：#H"
DKC_Tips_Item = "#Z(%s,%s)#H"
DKC_Msg_Pass = "玩家#C(#00EE00)%s#n成功通关#C(#ffff37)%s#n，激活称号#C(#F2FE5E)%s#n"
#===============================================================================
# 超级贵族
#===============================================================================
SUPER_VIP_ADD_EXP_MSG = "富豪值 +%s"
SUPER_VIP_LEVEL_UP = "#C(#00EE00)%s#n意气风发，风华绝代，成功达到#C(#F2FE5E)超级贵族%s#n，从此登上人生巅峰！"
HERO_IS_FULL = "英雄已满，无法领取"
VIP_LIBAO_MSG1 = "#C(#00FF00)%s#n领取了贵族#C(#0DF6FF)%s#n奖励:"
VIP_LIBAO_MSG2 = "真是羡煞旁人！"
VIP_ITEM = "#Z(%s,%s),"
VIP_UNBIND = "神石 +%s,"
VIP_BINDRMB = "魔晶+%s,"
VIP_GOLD = "金币+%s,"
VIP_HELO = "#Y(%s,%s),"
VIP_TAROT = "#t(#K(sTT,%s,%s)),"
#===============================================================================
# GS礼包
#===============================================================================
GS_Birthday_Ok = "设置成功"
GS_LiBao_None = "当前不是节日时间"
GS_Birthday_0 = "我还不知道你的生日日期，先把你的生日告诉我吧。"
GS_Birthday_1 = "你已经领取过今年的生日礼包"
GS_Birthday_2 = "当前不是生日"

#===============================================================================
# 跨服商店
#===============================================================================
KuaFuShop_Tips_Head = "兑换成功，获得：#H"
KuaFuShop_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 送人玫瑰
#===============================================================================
RosePresent_Tips_NotLocalServer = "非本服好友，不能赠送"
RosePresent_Tips_Item = "#Z(%s,%s)#H"
RosePresent_Tips_SendSucceed = "赠送成功，获得：#H%s魅力值#H"
RosePresent_Msg_Precious = "#C(#EE7600)【魅力情人节】#n—送人玫瑰，手有余香，#C(#00EE00)%s#n获得返利稀有物品#Z(%s,%s),#C(#00ff00)#U#A(#K(openSRMJ))前往赠送！#n#n#n"

RosePresent_Mail_Title = "您收到赠送"
RosePresent_Mail_Sender = "系统"
RosePresent_Mail_Content = "你收到来自#C(#00EE00)%s#n赠送的#Z(%s,%s)，您将会收到一定的魅力值哟，快去看看吧！"


#===============================================================================
# 玫瑰返利
#===============================================================================
RoseRebate_Tips_Head = "成功领取返利，获得：#H"
RoseRebate_Tips_Item = "#Z(%s,%s)#H"
#===============================================================================
# 蓝钻转大礼
#===============================================================================
QQLZRoll_Tips_Head = "领奖成功，获得：#H"
QQLZRoll_Tips_HeadEx = "兑换成功，获得：#H"
QQLZRoll_Tips_Item = "#Z(%s,%s)#H"
QQLZRoll_Tips_Crystal = "蓝钻水晶 +%s#H"

#===============================================================================
# 跨服个人竞技场
#===============================================================================
KUAFU_JJC_ELECTION_READY = "#C(#EE7600)【跨服英雄竞技】#n群英汇聚将于5分钟后开始，各位勇士前往准备"
KUAFU_JJC_ELECTION_START = "#C(#EE7600)【跨服英雄竞技】#n群英汇聚活动已经开始，请各位勇士抓紧前往"
KUAFU_JJC_FINALS_READY = "#C(#EE7600)【跨服英雄竞技】#n王者之风将于5分钟后开始，各位勇士前往准备"
KUAFU_JJC_FINALS_START = "#C(#EE7600)【跨服英雄竞技】#n王者之风活动已经开始，请各位勇士抓紧前往"
KUAFU_JJC_NOT_FIGHT_MSG = "本局你不战而胜，获得了对应积分"
#============邮件=================
KUAFU_JJC_ELECTION_TITLE = "群英汇聚资格"
KUAFU_JJC_ELECTION_SENDER = "系统"
KUAFU_JJC_ELECTION_MAIL = "恭喜您获得次日群英汇聚的参赛资格，请于次日12:00-21:55参加"
KUAFU_JJC_FINALS_TITLE = "王者之风资格"
KUAFU_JJC_FINALS_SENDER = "系统"
KUAFU_JJC_FINALS_MAIL = "恭喜您获得活动第7天王者之风的参赛资格，请于当天22:00准时参加"

#===============================================================================
# 春节
#===============================================================================
SpringBA_Title = "【新春最靓丽】跨服排行奖励"
SpringBA_Sender = "系统"
SpringBA_Contend = "恭喜恭喜！您本次在新春最靓丽【跨服】排行中获得了第%s名，获得了丰厚的奖励真是可喜可贺啊！"
SpringBL_Title = "【新春最靓丽】本服排行奖励"
SpringBL_Contend = "恭喜恭喜！您本次在新春最靓丽【本服】排行中获得了第%s名，获得了丰厚的奖励，真是可喜可贺啊！"
SpringFashion_Title = "好友赠送物品"
SpringFashion_Sender = "系统"
SpringFashion_Contend = "新春到来之际，为了表达我的心意，送上新春最时尚的时装，让你整个春节都靓丽全场。"
SpringNianComing = "领取成功，获得%s抽奖次数"
SpringExchangeComing = "祥瑞气象，年兽贺喜！#C(#00FF00)%s#n在#C(#FF0000)春节活动-年兽来了#n活动中兑换了#C(#FF0000)烈焰年兽坐骑#n，正酷炫地在新春中奔腾，真是可喜可贺啊！#C(#00ff00)#U#A(#K(OPEN_NIANSHOU_ITEM))马上去兑换！#n#n#n"
#===============================================================================
# 元宵节
#===============================================================================
LanternFesitivalC_Title = "【点灯高手】跨服排行奖励"
LanternFesitivalC_Sender = "系统"
LanternFesitivalC_Content = "恭喜，您在【元宵节点灯高手】活动中跨服排行中获得了第%s名，达到了排名奖励标准，获得了丰厚的奖励!"
LanternFesitivalL_Title = "【点灯高手】本服排行奖励"
LanternFesitivalL_Sender = "系统"
LanternFesitivalL_Content = "恭喜，您在【元宵节点灯高手】活动中本服排行中获得了第%s名，达到了排名奖励标准，获得了丰厚的奖励!"

LanternHappnessGlobalTell = "#C(#FF6600)【欢乐花灯】#n恭喜玩家#C(#66FF00)%s#n在元宵节点花灯活动中获取珍贵道具：#Z(%s,%s)，真是洋洋得意啊！"

LanternPointTips = "点灯积分+%s#H"
LanternRebateGlobalTips = '#C(#00EE00)%s#n领取了花灯返利奖励，获得#Z(%s,%s)，感谢#C(#00EE00)%s#n为大家作出的贡献'

LanternRiddleRight = '恭喜回答正确，奖励#Z(%s,%s)'
LanternRiddleWrong = '非常遗憾，回答错误，请下一题继续加油。'

LanternRiddle_Title = '欢乐猜灯谜'
LanternRiddle_Sender = "系统"
LanternRiddle_Content = '亲爱的龙骑士们，3月2日-3月6日#C(#FF6600)【元宵活动】#n期间，前往#C(#66FF00)圣辉城（5179,1471）#n的灯谜NPC可以进行#C(#FF6600)【欢乐猜灯谜游戏】#n，猜中灯谜可以获得灯谜礼包， 开启礼包将有惊喜等着你哦！心动不如行动，智勇双全的龙骑士们还等什么呢！'


LanternRiddleGlobalTell = '#C(#EE7600)【欢乐猜灯谜】#n元宵节活动期间，每天有10次猜灯谜机会，猜中答案奖励灯谜礼包，开启礼包可获得珍贵道具，根本停不下来！！#U#C(#00FF00)#A(#K(dlg,goto_lanternfestival_caidengminpc))我要猜灯谜#n#n#n'

#===============================================================================
# 情侣炫酷时装
#===============================================================================
CouplesFashion_Tips_Head = "购买成功，获得：#H"
CouplesFashion_DonateTips_Head = "赠送成功，获得返利：#H"
CouplesFashion_Tips_Item = "#Z(%s,%s)#H"
CouplesFashion_Tips_NotLocalServer = "非本服好友，不能赠送"
CouplesFashion_Mail_Title = "您收到赠送"
CouplesFashion_Mail_Sender = "系统"
CouplesFashion_Mail_Content = "你收到来自#C(#00EE00)%s#n赠送的#Z(%s,%s)"

#===============================================================================
# 魅力派对
#===============================================================================
GlamourParty_Tips_PartyQinmi = "#C(#EE7600)【【魅力情人节】#n活动期间，获得额外加成#C(#00EE00)%s#n点亲密值"
GlamourParty_Tips_PartyGlamour = "#C(#EE7600)【【魅力情人节】#n活动期间，举办派对获得了#C(#00EE00)%s#n点魅力值"
GlamourParty_Tips_Head = "成功领取目标奖励，获得：#H"
GlamourParty_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 情人目标
#===============================================================================
CouplesGoal_Tips_Head = "成功领取目标奖励，获得：#H"
CouplesGoal_Tips_Item = "#Z(%s,%s)#H"
CouplesGoal_Tips_Addinmi = "使用成功，获得亲密值 + %s"

#===============================================================================
# 魅力排行
#===============================================================================
GlamourRank_Title = "【魅力排行】跨服排名奖励"
GlamourRank_Sender = "系统"
GlamourRank_Content = "恭喜！您在【魅力排行】活动中跨服排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！"

GlamourRank_Local_Title = "【魅力排行】本服排名奖励"
GlamourRank_Local_Sender = "系统"
GlamourRank_Local_Content = "恭喜！您在#C(#E87D22)【魅力情人节-魅力排行】#n活动中本服排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！"

GlamourRank_Tips_Head = "成功领取奖励，获得：#H"
GlamourRank_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 疯狂抢购乐
#===============================================================================
CrazyShoppingGlobalTell = "#C(#FF0000)【疯狂抢购乐】#n#C(#00FF00)%s#n以迅雷不及掩耳之的速度抢到了#Z(%s,%s)，真是羡煞旁人啊!"
CrazyShoppingGetReady1 = "#C(#FF0000)【疯狂抢购乐】#n本日的疯狂抢购将在#C(#00FF00)10分钟#n后开始，马上去参与抢购吧。"
CrazyShoppingGetReady2 = "#C(#FF0000)【疯狂抢购乐】#n本日的疯狂抢购将在#C(#00FF00)5分钟#n后开始，马上去参与抢购吧。"
CrazyShoppingGetReady3 = "#C(#FF0000)【疯狂抢购乐】#n本日的疯狂抢购将在#C(#00FF00)1分钟#n后开始，马上去参与抢购吧。"
CrazyShoppingCD = "抢购正在冷却中"

#===============================================================================
# 天降财神
#===============================================================================
TheMammonMailTitle = "恭喜你获得财神的眷顾"
TheMammonMailSender = "财神"
TheMammonMailContent = "财神降临，好运连连，你获得了财神眷顾，得到了财神返利，真是好福气啊！"

#===============================================================================
# 连充返利
#===============================================================================
LianChongRebate_Tips_Head = "成功领取奖励，获得：#H"
LianChongRebate_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 魔域探秘
#===============================================================================
UNION_EXPLORE_QUESTION_RIGHT_PROMPT = "回答正确，获得个人贡献#C(#00FF00)%s#n, 公会资源#C(#00FF00)%s#n，前进#C(#00FF00)%s#n米"
UNION_EXPLORE_QUESTION_WRONG_PROMPT = "回答错误，获得个人贡献#C(#00FF00)%s#n, 公会资源#C(#00FF00)%s#n，后退#C(#00FF00)%s#n米"
UNION_EXPLORE_MONSTER_WIN_PROMPT = "打败怪物，获得个人贡献#C(#00FF00)%s#n, 公会资源#C(#00FF00)%s#n，前进#C(#00FF00)%s#n米"
UNION_EXPLORE_MONSTER_LOST_PROMPT = "战斗失败，获得个人贡献#C(#00FF00)%s#n, 公会资源#C(#00FF00)%s#n, 后退#C(#00FF00)%s#n米"
UNION_EXPLORE_MONSTER_ESCAPE_PROMPT = "遇怪逃跑，获得个人贡献#C(#00FF00)%s#n, 公会资源#C(#00FF00)%s#n, 后退#C(#00FF00)%s#n米"
UNION_EXPLORE_GET_TREASURE_PROMPT = "您挖出一个宝箱，获得#Z(%s,%s)，高兴的前进了#C(#00FF00)%s#n米"
UNION_EXPLORE_GET_TREASURE_fcm = "前进了#C(#00FF00)%s#n米"
UNION_EXPLORE_TAKE_PRISONER_SUCCESS_PROMPT = "您抓获一个战俘，获得个人贡献#C(#00FF00)%s#n，前进#C(#00FF00)%s#n米"
UNION_EXPLORE_TAKE_PRISONER_FAIL_PROMPT = "您战斗失败，获得个人贡献#C(#00FF00)%s#n，后退#C(#00FF00)%s#n米"
UNION_EXPLORE_PRISONER_FULL_PROMPT = "战俘已满抓捕失败，获得个人贡献#C(#00FF00)%s#n，前进#C(#00FF00)%s#n米"
UNION_EXPLORE_PRISONER_ESCAPE_PROMPT = "战俘逃跑，您获得个人贡献#C(#00FF00)%s#n，前进#C(#00FF00)%s#n米"
UNION_EXPLORE_YOU_ESCAPE_PROMPT = "您不战而逃，获得个人贡献#C(#00FF00)%s#n，后退#C(#00FF00)%s#n米"
UNION_EXPLORE_MAX_METER_PROMPT = "您已深入魔域顶点，无法前进了"
UNION_EXPLORE_MIN_METER_PROMPT = "您已在魔域入口，不用再后退了"
UNION_EXPLORE_GET_RESOURE_PROMPT = "领取成功，获得战俘贡献的公会资源#C(#00FF00)%s#n"

#===============================================================================
# 英雄觉醒
#===============================================================================
HeroAwaken_Msg_Succeed = "#C(#fefb00)%s#n#C(#66FF00)不畏艰辛，克服重重阻碍，终于将英雄#C(#FF0000)%s#n成功觉醒为#C(#FF0000)%s#n，这是要逆天的节奏啊！"

#===============================================================================
# 清明踏青
#===============================================================================
QMO_Tips_Head = "恭喜您，获得：#H"
QMO_Tips_Item = "#Z(%s,%s)#H"
QMO_MSG_Precious = "清明时节郊游踏青，恭喜玩家#C(#00FF00)%s#n在踏青游玩时幸运地获得：#Z(%s,%s),#U#C(#00FF00)#A(#K(dlg,open_qingming_panel|4))我也要踏青#n#n#n"
QMO_Tips_LuckyKey = "翻开全部卡牌，额外获得：#Z(%s,%s)#H"
QMO_Tips_UnlockRewardHead = "领取成功，获得：#H"

#===============================================================================
# 清明幸运大轮盘
#===============================================================================
QMLL_Tips_Head = "恭喜您，获得：#H"
QMLL_Tips_Item = "#Z(%s,%s)#H"
QMLL_MSG_Precious = "幸运连连，挡也挡不住，恭喜玩家#C(#00FF00)%s#n在幸运轮盘中获得#Z(%s,%s)，#U#C(#00FF00)#A(#K(dlg,open_qingming_panel|5))我也要抽奖#n#n#n"

#===============================================================================
# 清明消费排行
#===============================================================================
QingMingRank_Title = "【清明消费排行】跨服排名奖励"
QingMingRank_Sender = "系统"
QingMingRank_Content = "恭喜！您在#C(#E87D22)【清明消费排行】#n活动中跨服排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！"

QingMingRank_Local_Title = "【清明消费排行】本服排名奖励"
QingMingRank_Local_Sender = "系统"
QingMingRank_Local_Content = "恭喜！您在#C(#E87D22)【清明消费排行】#n活动中本服排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！"

QingMingRank_Tips_Head = "成功领取奖励，获得：#H"
QingMingRank_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 公会圣域争霸
#===============================================================================
#提示
UNION_KUAFU_WAR_CANT_ENTER_PROMPT = "只有本服排名#C(#00FF00)第1～3名#n的公会勇士才能前往"
UNION_KUAFU_WAR_NEW_JOIN_PROMPT = "#C(#E87D22)【圣域争霸】#n%s进入圣域，公会总积分#C(#00FF00)+%s#n"
UNION_KUAFU_WAR_OTHER_CD_PROMPT = "该玩家当前不可以挑战，请先挑战其他玩家。"
UNION_KUAFU_WAR_LEAVE_PROMPT = "对方已经离开了城门，请选择其他玩家挑战。"
UNION_KUAFU_WAR_ALL_GATE_BROKEN_PROMPT = "所有城门已被攻破，圣域争霸活动已结束"
UNION_KUAFU_WAR_GODDESS_PROMPT = "您正受到女神的庇护，获得#C(#E87D22)%s#n"
UNION_KUAFU_WAR_BUFF_PROMPT = "#C(#00FF00)%s#n激活了#C(#FFFF00)%s#n，公会全体成员获得#C(#00F6FF)%s#n效果"
#传闻
UNION_KUAFU_WAR_TEN_MINUTE_READY_HEARSAY = "#C(#E87D22)【圣域争霸】#n跨服圣域争霸将在10分钟后开启，请本服#C(#00FF00)其他公会#n界面排名#C(#00FF00)第1～3名#n的公会勇士做好准备！"
UNION_KUAFU_WAR_CAN_JOIN_HEARSAY = "#C(#E87D22)【圣域争霸】#n跨服圣域争霸已经开启，请本服#C(#00FF00)其他公会#n界面排名#C(#00FF00)第1～3名#n的公会勇士尽快前往准备，夺取属于您的圣城！"
UNION_KUAFU_WAR_START_HEARSAY = "#C(#E87D22)【圣域争霸】#n跨服圣域争霸正式开启，夺取城门，攻破圣域，圣城就是您的啦！"
UNION_KUAFU_WAR_WIN_STREAK_HEARSAY2 = "#C(#E87D22)【圣域争霸】#n#C(#00FF00)%s#n连杀！#C(#00FF00)%s#n已经杀人如麻！"
UNION_KUAFU_WAR_WIN_STREAK_HEARSAY3 = "#C(#E87D22)【圣域争霸】#n#C(#00FF00)%s#n连杀！#C(#00FF00)%s#n已经暴走杀戮！"
UNION_KUAFU_WAR_WIN_STREAK_HEARSAY4 = "#C(#E87D22)【圣域争霸】#n#C(#00FF00)%s#n连杀！#C(#00FF00)%s#n已经如同神一般的杀戮！"
UNION_KUAFU_WAR_WIN_STREAK_HEARSAY5 = "#C(#E87D22)【圣域争霸】#n#C(#00FF00)%s#n连杀！#C(#00FF00)%s#n已经遇神杀神，遇佛杀佛，无人能挡！"
UNION_KUAFU_WAR_BREAK_WIN_STREAK = "#C(#E87D22)【圣域争霸】#n功夫再高，也怕菜刀，#C(#00FF00)%s#n破掉#C(#00FF00)%s#n的#C(#00FF00)%s#n连杀，真是新一代神人！"
UNION_KUAFU_WAR_GATE_BROKEN_HEARSAY = "#C(#E87D22)【圣域争霸】#n#C(#00FF00)%s#n已被攻破，入驻圣域就在眼前，各位公会勇士大展神威，让我们一起开创新的伟业吧！"
UNION_KUAFU_WAR_END_HEARSAY = "#C(#E87D22)【圣域争霸】#n勇者无敌，圣域永驻，#C(#00FF00)%s#n公会获得圣域入驻权利，让我们一起觐见新的#C(#00FF00)圣域独裁者#n吧！"
#记录
UNION_KUAFU_WAR_WIN_PVP_RECORD = "您战胜了#C(#00FF00)%s#n，您的积分#C(#00FF00)+%s#n"
UNION_KUAFU_WAR_LOST_PVP_RECORD = "#C(#00FF00)%s#n击败了您，您的积分#C(#00FF00)-%s#n"
UNION_KUAFU_WAR_WIN_GUARD_RECORD = "您战胜了#C(#00FF00)圣域守卫#n，您的积分#C(#00FF00)+%s#n"
UNION_KUAFU_WAR_LOST_GUARD_RECORD = "#C(#00FF00)圣域守卫#n击败了您，您的积分#C(#00FF00)-%s#n"
#===============================================================================
# 清明节全民炼金
#===============================================================================
QingMingLianJinBuffTips1 = "和%s%%的全民齐炼金加成"
QingMingLianJinBuffTips2 = "您获得了额外%s%%的全民齐炼金加成"

#===============================================================================
# 魔灵大转盘
#===============================================================================
MOLING_LUCKY_DRAW_REWARD_PROMPT = "恭喜获得： #Z(%s,%s)"

#===============================================================================
# 超级投资
#===============================================================================
SuperInvestSuccess = "投资成功"

#===============================================================================
# 新在线奖励
#===============================================================================
ZaiXianJiangLi_Msg_Precious = "玩家#C(#00FF00)%s#n从在线奖励中获得了#Z(%s,%s)，运气真是好到爆！#U#C(#00FF00)#A(#K(dlg,OPEN_ONLINEREWARD_PANEL))你也来试试吧#n#n#n"
ZaiXianJiangLi_Tips_LotterySuccess = "领取成功，获得： #Z(%s,%s)"

#================================================================================
# 五一活动
#=================================================================================
FiveOne_AttickBadDragon = "五一活动勇者斗恶龙"
FiveOne_AttickBadDragon_Content = "勇者斗恶龙未拾取物品"

#================================================================================
# 超值特惠
#=================================================================================
SuperPromption_Tips_Success = "购买成功"

#===============================================================================
# 至尊周卡
#===============================================================================
SuperCardsBuySuccess = "至尊周卡购买成功"
SuperCardsUseSuccess = "勾选成功，至尊特权已开启"
SuperCardsBuySucess2 = "#C(#E87D22)【至尊周卡】#n#C(#00FF00)%s#n购买了至尊周卡，享用至尊特权！从此登上人生巅峰！"
#===============================================================================
# 腾讯页游节预热
#===============================================================================
YeYouJieWarmupRechargeRewardsTips = "你成功领取了喜迎页游节豪华奖励"
YeYouJieWarmupLoginRewardsTip = "你成功领取了喜迎页游节登陆奖励"
#===============================================================================
# 腾讯页游节折扣汇
#===============================================================================
YeYouJieDiscountRefreshTips = "已消耗%s神石，刷新成功！"

#===============================================================================
# 空间十周年
#===============================================================================
KJD_Tips_Head = "恭喜获得： "

#===============================================================================
# 王者公测
#===============================================================================
ZXLR_Tips_Head = "恭喜获得： "
WZE_Tips_Head = "兑换成功，获得："
WZFS_Tips_Head = "购买成功，获得："
WZFS_Tips_NotLocalServer = "非本服好友，不能赠送"
WZFS_DonateTips_Head = "赠送成功，获得返利：#H"
WangZheFashionShowMail_Title = "您收到赠送"
WangZheFashionShowMail_Sender = "系统"
WangZheFashionShowMail_Content = "你收到来自#C(#00EE00)%s#n赠送的#Z(%s,%s)"
WZZKH_Tips_Head = "购买成功，获得："
WangZheZheKouHui_Tips_Refresh = "刷新成功，消耗%s神石！"
WZCR_Tips_Head = "领取成功，获得： "
WZRR_Tips_Head = "恭喜获得： "
WZRR_Tips_Precious = "#C(#E87D22)【王者公测-充值大返利】#n#C(#00FF00)%s#n运气真是逆天啊，大手一挥，抽到了震惊全服的奖励：#Z(%s,%s)"
WZRR_Tips_HeadEx = "领取成功，获得： "
WZRR_Tips_GameOver = "#C(#E87D22)【王者公测-充值大返利】#n#C(#00FF00)%s#n完成一轮十二个奖励的抽取，获得自动重置奖励，可喜可贺啊！"
WZRR_Msg_AutoRefresh = "#C(#E87D22)【王者公测-充值大返利】#n奖励自动重置，小伙伴们还在等什么？来领取自己的充值返利吧！" 
WangZheRank_Title = "【王者公测】跨服排名奖励"
WangZheRank_Sender = "系统"
WangZheRank_Content = "恭喜！您在#C(#E87D22)【王者公测】#n活动中跨服排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！"

WangZheRank_Local_Title = "【王者公测】本服排名奖励"
WangZheRank_Local_Sender = "系统"
WangZheRank_Local_Content = "恭喜！您在#C(#E87D22)【王者公测】#n活动中本服排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！"

WangZheRank_Tips_Head = "成功领取奖励，获得：#H"
WangZheRank_Tips_Item = "#Z(%s,%s)#H"

#===============================================================================
# 诸神之战
#===============================================================================
ClashOfTitansEndWithOutTitan = "#C(#EE7600)【诸神之战】#n活动已结束，仍有#C(#ffff37)%s#n位战神存活，下一次他们能分出胜负吗？"
ClashOfTitansTitanStandOut = "#C(#EE7600)【诸神之战】#n战神诞生，#C(#FFFF00)%s#n击败全部对手战到最后，下一次荣耀又将归属于谁？"
ClashOfTitansKillTips4 = "#C(#E87D22)【诸神之战】#n#C(#00FF00)%s#n连杀！#C(#FFFF00)%s：“还有谁？还有谁！ ”#n"
ClashOfTitansBeKilledTips = "#C(#EE7600)【诸神之战】#n#C(#FFFF00)%s#n成功终结了#C(#FFFF00)%s#n的%s连杀！地图坐标#C(#00ff00)#U#A(#K(MoveXY,%s,%s))(%s,%s)#n#n#n处出现了“#C(#0066CC)%s的英魂#n”，拾取后可获得%s的属性。"
ClashOfTitansPickUpSoulSelf = "你拾取了%s的英魂，获得附体效果，下一场战斗属性将临时变为%s的属性。"
ClashOfTitansPickUpSoulGlobal = "#C(#EE7600)【诸神之战】#n#C(#FFFF00)%s#n拾取了”#C(#0066CC)%s的英魂#n”，战斗力发生了翻天覆地的变化！"
ClashOfTitansKillTips1 = "#C(#EE7600)【诸神之战】#n#C(#FFFF00)%s#n气势如虹，完成%s连杀。"
ClashOfTitansKillTips2 = "#C(#EE7600)【诸神之战】#n#C(#FFFF00)%s#n完成了%s连杀，已经势不可挡了。"
ClashOfTitansKillTips3 = "#C(#EE7600)【诸神之战】#n#C(#FFFF00)%s#n正在大杀特杀，达成%s连杀。"
ClashOfTitansFiveMiniutesReady = "#C(#EE7600)【诸神之战】#n活动已开启，#C(#ffff37)5#n分钟后活动入口将关闭，请各位骑士及时进入"
ClashOfTitansOneMiniutesReady = "#C(#EE7600)【诸神之战】#n活动已开启，#C(#ffff37)1#n分钟后活动入口将关闭，请各位骑士及时进入。"
ClashOfTitansStart = "#C(#EE7600)【诸神之战】#n活动正式开启，这次谁又能战到最后成为新的王者？让我们拭目以待！"
ClashOfTitansRoleInProtected = "该角色正处于保护时间内！"
ClashOfTitansRoleDieWithoutFighting = "由于你在60秒内没有进行战斗，复活次数-1"
ClashOfTitansDeadoutTips = "本次诸神之战您的个人积分为#C(#ffff37)%s#n，奖励将在活动结束后发放 "
ClashOfTitansSoulNpcName = "%s的英魂"
ClashOfTitansNotInScene = "该角色目前不在场景中 "
ClashOfTitansPerMinuteScore = "您获得了系统发放的积分#C(#00FF00)+%s#n"
ClashOfTitansCanNotReborn = "你的复活次数已经用完，请等待下次活动开启"
ClashOfTitansEntryClose = "活动入口已关闭，下次活动请及时参与以免错过"
ClashOfTitansEnd = "本次活动已结束 "
ClashOfTitansTimeOutTip = "您由于战斗超时，复活次数-1。点击跳过战斗可避免战斗超时。"
#===============================================================================
# 繁体老玩家回流活动
#===============================================================================
OldRoleBackFTMailTitle1 = "欢迎再次回归龙骑圣殿"
OldRoleBackFTMailContent1 = "亲爱的玩家您好，欢迎再次回归《新龙骑士传》与伙伴一同冒险，感谢您对《新龙骑士传》的支持，您的支持就是我们最大的动力。"
OldRoleBackFTMailTitle2 = "恭喜你完成回归储值返利"
OldRoleBackFTMailContent2 = "恭喜你在活动期间完成首次储值，储值金额：%s神石，额外获得%s奖励神石返利，真是好福气啊！"
OldRoleBackFTMailSender = "《新龙骑士传》营运团队"

#=============================================================================
#最新活动
#=============================================================================
PET_ITEM_NOT_STAR = "没有对应星级的宠物，无法使用！"
PET_ITEM_USE_SUC = "使用成功"
PET_ITEM_NOT_EVO = "没有对应阶数的宠物，无法使用！"
DRAGON_ITEM_NOT_EVO = "没有对应品质的神龙，无法使用！"
#=============================================================================
#欢庆端午节
#=============================================================================
DuanWuJieGlobalTell = "#C(#E87D22)【欢乐粽子】#C(#00FF00)%s#C(#FFFFFF)玩家用一双巧手剥开黄金粽，意外发现了黄金粽中隐藏的神秘礼物："
DuanWuJieZongzi = "剥粽成功，获得"
DuanWuJieLink = "#U#C(#00FF00)#A(#K(dlg,open_duanwu_panel))我要剥粽子#n#n#n"
DuanWuJieItem_Tips = "#Z(%s,%s)，" 
DuanWuJieTarot_Tips = "#t(#K(sTT,%s,%s))，" 
DuanWuJieTalent_Tips = "#L(%s,%s)，" 

#=============================================================================
#QQ蓝钻宝箱
#=============================================================================
QQLZBXTianMa = "领取成功，"
QQLZBXKaiQi = "开启成功，"

#===============================================================================
# 激情活动
#===============================================================================
PassionMultiReward_Tips_Head = "领取成功，获得： "
PassionMarket_Tips_Refresh = "刷新成功，消耗%s神石！"
PassionMarket_Tips_Head = "购买成功，获得："
PassionDiscount_Tips_Head = "购买成功，获得："
PassionDiscount_DonateTips_Head = "赠送成功，获得返利：#H"
PassionDiscount_Mail_Title = "您收到赠送"
PassionDiscount_Mail_Sender = "系统"
PassionDiscount_Mail_Content = "你收到来自#C(#00EE00)%s#n赠送的#Z(%s,%s)"
PassionDiscount_DonateTips_Head = "赠送成功"
PassionRechargeRank_Local_Title = "本服充值排名奖励"
PassionRechargeRank_Local_Sender = "系统"
PassionRechargeRank_Local_Content = "您在%s-%s-%s的本服充值排名中位于第%s名，请领取奖励。"
PassionRechargeRank_Tips_Head = "成功领取奖励，获得：#H"
PassionRechargeRank_KuaFu_Title = "跨服充值排名奖励"
PassionRechargeRank_KuaFu_Sender = "系统"
PassionRechargeRank_KuaFu_Content = "您在%s-%s-%s的跨服充值排名中位于第%s名，请领取奖励。"

PassionConsumeRank_Local_Title = "本服消费排名奖励"
PassionConsumeRank_Local_Sender = "系统"
PassionConsumeRank_Local_Content = "您在%s-%s-%s的本服消费排名中位于第%s名，请领取奖励。"
PassionConsumeRank_Tips_Head = "成功领取奖励，获得：#H"
PassionConsumeRank_KuaFu_Title = "跨服消费排名奖励"
PassionConsumeRank_KuaFu_Sender = "系统"
PassionConsumeRank_KuaFu_Content = "您在%s-%s-%s的跨服消费排名中位于第%s名，请领取奖励。"


PassionExchangeFresh = "已消耗%s神石，刷新成功！"

PassionGift_Tips_Head = "领取成功，获得："

PassionTurntableChangeTips = "刷新成功"
PassionTurntableGlobalTell = "#C(#00FF00)%s#n在#C(#FF0000)幸运转盘#n中，获得了#Z(%s,%s)奖励"
PassionGodTree = "恭喜#C(#00EE00)%s#n在神树探秘时获得了#Z(%s,%s) #C(#00ff00)#U#A(#K(OPEN_PASSION_ACT|13))快去看看#n#n#n"
PassionGodTreeExchange = '恭喜#C(#00EE00)%s#n在藏宝商店中兑换了#Z(%s,%s) #C(#00ff00)#U#A(#K(OPEN_PASSION_ACT|14))快去看看#n#n#n'

PassionTaoGuanOne = "轻轻一锤砸碎了一个陶罐，获得了"
PassionTaoGuanTen = "大力一锤将一堆陶罐砸了个粉碎，获得了"
PassionTaoGuanGlobalTell = "#C(#00EE00)%s#n运气爆棚，在陶瓷堆中翻出"


#===============================================================================
# 今日首充
#===============================================================================
RechargeEverydayTitle = "【今日首充】系统通知"
RechargeEverydaySender = "系统"
RechargeEverydayContent = " #C(#66FF00)【今日首充】#n奖励已发送您邮件，快去把它们提取掉吧！ "
RechargeEverydayGlobalTell = "#C(#EE7600)【今日首充】#n #C(#00FF00)%s#n成功完成了【今日首充】活动，领取豪华礼包，从此横行圣辉，坐拥天下啊。"

#===============================================================================
# 神秘宝箱
#===============================================================================
ShenMiBaoXiang_Tip = "恭喜#C(#00EE00)%s#n在神秘宝箱中开出了#Z(%s,%s)"
#===============================================================================
# 战阵系统
#===============================================================================
WarStation_Msg = "玩家#C(#00FF00)%s#n经过不懈努力，终于成功将#C(#FF0000)%s级#n战魂升到#C(#FF0000)%s级#n战魂，称霸全服指日可待！"
WarStation_UpStar_Msg = "战魂升星成功"
WarStation_Item_False = "已达到当前星数使用上限。"
WarStation_Item_Suc = "使用成功，#C(#00FF00)生命+75、攻击+20、暴击+5、破挡+5#n！当前已使用#C(#00FF00)%s#n个，当前星级最多可使用#C(#00FF00)%s#n个！"
#===============================================================================
# 阵灵系统
#===============================================================================
StationSoul_Tips_Upgrade_Head = "升星成功"

StationSoul_Tips_BreakSucceed = "玩家#C(#00FF00)%s#n经过不懈努力，终于成功将#C(#FF0000)%s级#n阵灵升到#C(#FF0000)%s级#n阵灵，称霸全服指日可待！"

StationSoul_Tips_BreakFailed = "增加突破值%s"

StationSoul_Tips_OneKeyBreakSucceed = "一键突破突破成功"

StationSoul_Item_Suc = "使用成功，#C(#00FF00)生命+75、攻击+20、免暴+5、格挡+5#n！当前已使用#C(#00FF00)%s#n个，当前星级最多可使用#C(#00FF00)%s#n个！"
StationSoul_Item_Fail = "使用阵灵强化石失败,已达到目前星级使用上限，阵灵升星可提高阵灵强化石使用个数！"

#===============================================================================
# 新龙骑试炼
#===============================================================================
DKCNew_Tips_Head = "抽奖成功，恭喜获得:"
DKCNew_Msg_UnlockLevel = "【龙骑试炼】玩家#C(#00FF00)%s#n经过不懈努力，终于成功通关#C(#FF0000)%s#n，称霸全服指日可待！" 

DKCNew_Tips_OneKeyFreeHead = "一键免费收益成功，获得:"
DKCNew_Tips_OneKeyAllHead = "一键全部收益成功，获得:"

#===============================================================================
# 神秘宝箱
#===============================================================================
MysteryBox_Tips_Head = "领取成功，恭喜获得:"
MysteryBox_Msg_Precioud = "【%s】#C(#00FF00)%s#n运气爆表，终于抽到了#Z(%s,%s)，可喜可贺！" 

#===============================================================================
# 专属礼包
#===============================================================================
ZhuanShuLibaoTips = "#C(#00FF00)%s#n在打开#C(#FF0000)【%s】#n时，发现%s数量多了#C(#00FF00)%s#n个！真的是运气爆棚啊！"


#===============================================================================
# 防沉迷
#===============================================================================
Anti_Kick = "离线不足5小时，为了保证您能正常游戏，请%s分钟后登陆"

#===============================================================================
# 新跨服组队竞技场
#===============================================================================
JTKickTitle = "您已经被队长请离出战队"
JTKickContent = "您已经被%s战队请离出战队，您失去了该战队的战队积分和段位，要继续参加跨服组队竞技需要重新加入/创建新的战队。"


#===============================================================================
# 全民转转乐
#===============================================================================
TurnTableRewardRMB_TIPS = "#C(#00FF00)%s#n在全民转转乐中小手一挥，带走了#C(#E87D22)%s神石#n"
TurnTableRewardItem_TIPS = "恭喜#C(#00FF00)%s#n在全民转转乐中获得了#Z(%s,%s)"
TurnTableEnd = "全民转转乐活动已结束，已返还投入%s神石"
#===============================================================================
# 淬炼提示
#===============================================================================
CuiLian_Tips_1 = "使用成功，获属性加成：生命+%s 物攻+%s 物防+%s 法防+%s 暴击+%s 免爆+%s 格挡+%s 破挡+%s"
CuiLian_Tips_2 = "使用成功，获属性加成：生命+%s 物攻 +%s 法攻 +%s 物防+%s 法防+%s 暴击+%s 免爆+%s 格挡+%s 破挡+%s"


#===============================================================================
# 抢红包
#===============================================================================
QiangHongBao_Msg_OneMin = "【抢红包】活动将在1分钟后开启，请各位龙骑士做好准备！"
QiangHongBao_Msg_Start = "【抢红包】活动已开启！通过活动界面可快速传送至活动Npc身边."
QiangHongBao_Msg_End = "【抢红包】本次抢红包活动已结束!"
QiangHongBao_Tips_Head = "恭喜抢到:"
QiangHongBao_Msg_Presious = "【抢红包】玩家#C(#00FF00)%s#n运气爆表，获得#Z(%s,%s)，可喜可贺！"


#===============================================================================
# 神石基金
#===============================================================================
RMBFundMail_Title = "神石基金"
RMBFundMail_Sender = "系统"
RMBFundMail_Content = "亲爱的龙骑士，本次神石基金活动已经到期，您有尚未领取的基金本金%s+利息%s奖励神石，感谢参与本次活动！"

#===============================================================================
# 古堡探秘
#===============================================================================
GuBaoTanMi_Tips_Head = "恭喜获得:"

GuBaoTanMi_Msg_Precious = "【古堡探秘】玩家#C(#00FF00)%s#n在探索中获得#Z(%s,%s)，运气真是好到没朋友！"
GuBaoTanMi_MSg_Special = "【古堡探秘】玩家#C(#00FF00)%s#n集齐3把%s，获得#Z(%s,%s)"
#===============================================================================
# 虚空幻境
#===============================================================================
CTT_WorldCall_Tips = "#C(#E87D22)【虚空幻境】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
CTT_START_MSG = "#C(#E87D22)【神界】神界入口已开启，诸位勇士战个痛快！#n"
CTT_END_MSG = "#C(#E87D22)【神界】神界入口已关闭，请诸位勇士明日再战！#n"
CTT_CROSS_END_MSG = "#C(#E87D22)【神界】神界入口已关闭，请尽快离开神界，神界将会在#C(#FFFF00)23:59#n分将全部玩家驱逐出神界地图."
CTT_CROSS_END_MSG2 = "#C(#E87D22)【神界】神界入口已关闭，请尽快离开神界，神界将会在#C(#FFFF00)30#n分后将全部玩家驱逐出神界地图。"
CTT_CROSS_END_MSG3 = "#C(#E87D22)【神界】神界入口已关闭，请尽快离开神界，神界将会在#C(#FFFF00)10#n分后将全部玩家驱逐出神界地图。"
CTT_CROSS_END_MSG4 = "#C(#E87D22)【神界】神界入口已关闭，请尽快离开神界，神界将会在#C(#FFFF00)1#n分后将全部玩家驱逐出神界地图。"
CTT_SCENE_IS_FULL = "当前神界人数已满，您可以排队等候！"
CTT_MAIL_TITLE = "【虚空幻境】排行榜周结算奖励"
CTT_MAIL_SENDER = "系统"
CTT_MAIL_CONTENT = "亲爱的玩家：#H您在【虚空幻境】玩法中排名第#C(#00EE00)%s#n，达到了排名奖励标准，获得了丰厚奖励！前十名的玩家将会额外获得对应的炫酷称号奖励哟！"
CTT_STATUE_NO_DATA = "虚空幻境第%s名"
CTT_STATUE_DATA = "虚空幻境第%s名-%s"
CTT_MIRROR_CLOSED = "虚空幻境已关闭，请明日再来！"
CTT_POINT_Tips = 	"幻境点+%s#H"
CTT_LIMIT_LEVEL = "160级才可参与该玩法！"
CTT_APPLY_SUC = "请求成功，请耐心等待！"
CTT_APPLY_PLAYER = "该玩家已经加入其他队伍或不在神界"
#===============================================================================
# 鲜花系统
#===============================================================================
Flower_Outline = "该玩家不在线，无法送花。"
Flower_Send = "#C(#FFFF00)%s#n给#C(#FFFF00)%s#n赠送了%s朵鲜花，并对TA说：“%s”"
Flower_SendSuccess = "鲜花已经送到#C(#FFFF00)%s#n手里，等待Ta的回吻吧^_^"
Flower_AnonymousSend = "#C(#FF0000)神秘人物#n给#C(#FFFF00)%s#n赠送了%s朵鲜花，并对TA说：“%s”"
Flower_FeedbackKiss = "%s嘟起小嘴儿，狠狠地啵了一个，说：谢谢你的鲜花哦！"
Flower_ManMail_Title = "护花榜结算奖励"
Flower_WomenMail_Title = "鲜花榜结算奖励"
Flower_Mail_Sender = "系统"
Flower_Mail_Content = "根据上周魅力值排行，你获得了本周排行榜第一，这是你的奖励，请收好！。"
FlowerKuafuRank_ManTitle = "【跨服护花榜】跨服排名奖励"
FlowerKuafuRank_WomenTitle = "【跨服鲜花榜】跨服排名奖励"
FlowerKuafuRank_Sender = "系统"
FlowerKuafuRank_ManContent = "恭喜！您在【跨服护花榜】活动中排名第%s，达到了排名奖励标准，获得了丰厚奖励！"
FlowerKuafuRank_WomenContent = "恭喜！您在【跨服鲜花榜】活动中排名第%s，达到了排名奖励标准，获得了丰厚奖励！"
Flower_WorshipSuccess = "膜拜成功， 获得金币%s"
#===============================================================================
# 中秋活动2015
#===============================================================================
ZhongQiuShangYue_Mail_Title = "中秋赏月未拾取的奖励"
ZhongQiuShangYue_Mail_Sender = "系统"
ZhongQiuShangYue_Mail_Content = "亲爱的龙骑士，本次中秋赏月活动已结束，您有尚未拾取的奖励，请提取邮件附件!"

ZhongQiuShangYue_Msg_Precious = "#C(#E87D22)【欢庆中秋】#n玩家#C(#00FF00)%s#C(#FFFFFF)在中秋赏月期间打开月饼礼盒，获得了#Z(%s,%s)，真是羡煞旁人！#U#C(#00FF00)#A(#K(dlg,open_choneqiu_panel|4))前往赏月#n#n#n"

HuoYueDaLi_Tips_Move = "前进成功，您共前进了%s格"

HuoYueDaLi_Tips_Steps = "前进步数 +%s#H"
#===============================================================================
# 转生
#===============================================================================
ZhuanShengHeroTips1 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻，终于将8星觉醒英雄#C(#FF0000)%s#n转生为#C(#FF0000)%s#n转英雄#C(#FF0000)%s#n，这是要称霸全服的节奏啊#n"
ZhuanShengHeroTips2 = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻，终于将#C(#FF0000)%s#n转英雄#C(#FF0000)%s#n转生为#C(#FF0000)%s#n转英雄#C(#FF0000)%s#n，这是要称霸全服的节奏啊#n"
ZhuanShengRoleTips = "#C(#fefb00)%s#n#C(#66FF00)历尽艰难险阻，终于成功#C(#FF0000)%s#n转，走上人生巅峰，称霸全服，指日可待！#n"

ArtifactCuiLian = '淬炼成功，淬炼经验增加 %s'
ArtifactCuiLianHole1 = '强化成功'
ArtifactCuiLianHole2 = ', 光环等级提升至  %s 级'
#===============================================================================
# 跨服争霸赛喝彩
#===============================================================================
JTCheersMail_Title = '巅峰喝彩奖励'
JTCheersMail_Sender = '系统'
JTCheersMail_Content = '感谢您积极参与跨服争霸赛巅峰喝彩活动，你的热情大大激励了各大战队的士气，希望再接再厉，您在本次活动中获得了巅峰喝彩奖励%s神石，可喜可贺啊！'
JTCheersOneSuc = "喝彩一次成功"
JTCheersTenSuc = "喝彩十次成功"
JTCheersRespOneSuc = "回应一次成功"
JTCheersRespTenSuc = "回应十次成功"
JTCheersEnd = "喝彩已结束"

#===============================================================================
# 宝石锻造
#===============================================================================
GemForge_Tips_FotrgeSuccess = "恭喜您，锻造成功,获得:#Z(%s,%s)"
GemForge_Tips_TransformSuccess = "恭喜您，转换成功,获得:#Z(%s,%s)"

#===============================================================================
# 迷失之境
#===============================================================================
LostSceneWorldInvite = "#C(#E87D22)【迷失之境】#n%s队伍向全世界发出召唤，他们尚缺%s人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
LostSceneInviteSuccess = "发出邀请成功"
LostSceneInviteCDTips = "已发出邀请，请稍后再试"
LostSceneInviteOutline = "对方不在线"
LostSceneExchangeSUC = "兑换成功:#H"
LostSceneUseSpeedSkill = "持续5秒，移动速度增加150%"
LostSceneTips_1 = "#C(#FF0000)#C(#E87D22)【迷失之境】#n#C(#00FF00)第%s轮开始，#n20秒后追捕者将出现，快快躲起来！！#n"
LostSceneTips_2 = "#C(#FF0000)#C(#E87D22)【迷失之境】#n#C(#00FF00)追捕者%s#n正在行动......#n"
LostSceneTips_3 = "#C(#FF0000)#C(#E87D22)【迷失之境】#n#C(#00FF00)%s#n抓住了#C(#00FF00)%s#n，其他人要小心了。#n"
LostSceneTips_4 = "#C(#E87D22)你仔细的感应了周围，并没有发现可疑之处。#n"
LostSceneTips_5 = "额外获得冒险点+%s"
LostSceneCannotIn = "今日已参与， 明日再来"

#===============================================================================
# 双十一2015 
#===============================================================================
DELoginReward_Tips_Head = "恭喜您，成功领取登录有礼，获得：#H"
DETopic_Tips_YiCiHead = "恭喜您，获得：#H"
DETopic_Tips_ShiCiHead = "恭喜您，成功开启十次轮盘，获得：#H"
DEGroup_Title = "团购送神石活动奖励"
DEGroup_Sender = "系统"
DEGroup_Content = "您积极参与双十一狂欢中第%s轮团购送神石活动，获得如下奖励，请查收!"
DEGroup_Tips_Head = "购买成功，获得：#H"
DEGroupBuy_Msg_Hour = "#C(#E87D22)【双十一狂欢】#n由于大家热情高涨，在双十一狂欢团购中的参与人数已经到达#C(#FF0000)%s#n人，参与团购即可获得巨额神石福利！#U#C(#00FF00)#A(#K(dlg,SINGDAY_TUANGOU_OPENMSG))我也要团购#n#n#n"
DEQiangHongBao_Tips_QHB = "您的手真快，恭喜您抢到了：#H"
DEQiangHongBao_Tips_QG = "抢购成功， 获得：#H"

TunableTip_special = "#C(#E87D22)【双十一狂欢】#n玩家#C(#00FF00)%s#n在双十一轮盘中获得了#Z(%s,%s)，真是羡煞旁人。"
TunableTip_special_RMB = "#C(#E87D22)【双十一狂欢】#n玩家#C(#00FF00)%s#n在双十一轮盘中获得了%s奖励神石，真是羡煞旁人。"
PointChangeTip_special = "#C(#E87D22)【双十一狂欢】#n玩家#C(#00FF00)%s#n在在返利兑不停活动中兑换了#Z(%s,%s)"
ElevenMallRewardTitle = "商城满返奖励"
ElevenMallRewardContent = "您在昨日商城购物额度达到%s，获得了%s神石的奖励。"
ElevenTuntable = "恭喜你获得： %s 奖励神石"
DEQiangHongBao_Msg_QHBEnd = "#C(#E87D22)【双十一狂欢】#n抢红包现在结束，请各位龙骑士使用抢到的红包狂购，享受超低折扣吧！#U#C(#00FF00)#A(#K(dlg,SINGDAY_REDBAG_OPENMSG))前往狂购#n#n#n！"
DEQiangHongBao_Msg_QHBBegan = "#C(#E87D22)【双十一狂欢】#n狂购抢红包活动现在开始，请各位龙骑士踊跃参与。#U#C(#00FF00)#A(#K(dlg,SINGDAY_REDBAG_OPENMSG))我要抢红包#n#n#n！"
DEQiangHongBao_Tips_NoHongBao = "抱歉，您的手慢了，请下次再来"
DEQiangHongBao_Msg_QGEnd = "#C(#E87D22)【双十一狂欢】#n本轮狂购已经结束，下轮抢红包将于30分钟后开启，请各位龙骑士做好准备。"
DEQiangHongBao_Msg_OneMinBefore = "#C(#E87D22)【双十一狂欢】#n大量红包将于1分钟后出现，请各位龙骑士踊跃参与。#U#C(#00FF00)#A(#K(dlg,SINGDAY_REDBAG_OPENMSG))我要抢红包#n#n#n！"
#==============================================================================
#宝石分解
#==============================================================================
Can_not_resolve = "该宝石等级不足，不能分解"
Not_Enough_RMB = "神石不足，不能分解！"
Suc_Resovle = "分解成功：%s-1，%s+2"

#===============================================================================
# 神树密境
#===============================================================================
ShenshumijingTenMinuteReady = "#C(#EE7600)【神树秘境】#n将于10分钟后开始，请各位勇士做好准备。"
ShenshumijingOneMinuteReady = "#C(#EE7600)【神树秘境】#n将于1分钟后开始，请各位勇士做好准备。"
ShenshumijingBegin = "#C(#EE7600)【神树秘境】#n秘境神树已绽放出了神秘光芒，各位勇士可前往为神树浇水培养。"
ShenshumijingMail_Title = "神树秘境排名奖励"
ShenshumijingMail_Sender = "系统"
ShenshumijingMail_Content = "亲爱的勇士，您的公会在守卫神树活动中获得第%s名，这是排名奖励，请查收！"
ShenshumijingInFight = "战斗中，请勿打扰。"
ShenshumijingPeiyangTips = "神树培养成功，成长度+1"
ShenshumijingCaijiFail = "%s已被抢走"
ShenshumijingBrushCaiji = "#C(#EE7600)【神树秘境】#n秘境中出现了一批神秘的物品。"
ShenshumijingBrushGuard = "#C(#EE7600)【神树秘境】#n白色羊驼不甘示弱带领着恶魔精英-狂暴羊驼前来宣战，请各位勇士做好准备。"
ShenshumijingBeforeBG = "#C(#EE7600)【神树秘境】#n白色羊驼大军和狂暴羊驼大军将在1分钟后进攻神树，请各位勇士做好准备。"
ShenshumijingCaijiTips = "#C(#EE7600)【神树秘境】#n#C(#00FF00)%s#n在采集的过程中偶然发现采集物旁边亮闪闪的东西，定睛一看，原来是#Z(%s,%s)"
ShenshumijingSuccess = "#C(#EE7600)【神树秘境】#n经过一场激烈的混战，狂暴羊驼带着白色羊驼逃之夭夭了，恭喜龙骑士们取得胜利。"
ShenshumijingFail = "#C(#EE7600)【神树秘境】#n在恶魔精英-恶魔羊驼的带领下，我方神树遭到了致命的攻击，神树成长度降低了#C(#EE7600)%s#n点。"
ShenshumijingClearRole = "#C(#EE7600)【神树秘境】#n神树秘境将于1分钟后关闭。"
ShenshumijingSucMail_Title = "神树秘境守卫成功奖励"
ShenshumijingSucMail_Content = "亲爱的勇士，在您顽强的抵御下，成功守卫了神树，这是成功守护奖励，请查收！"
#===============================================================================
# 点石成金
#===============================================================================
TouchGold_PointMsg = "点金积分+%s"
TouchGold_Title = "原石回收通知"
TouchGold_Sender = "系统"
TouchGold_Content = "您昨天未使用的原石已折算为%s积分，请领取附件。"
#===============================================================================
# 新答题活动
#===============================================================================
CanFinalsTitle = "问答比赛决赛参加资格"
CanFinalsContent = "恭喜您在问答比赛的初赛中表现优异，获得参加决赛的资格，请于本周日14:00-16:00期间准时参加并完成决赛答题。"
FinalsRewardTitle_1 = '问答比赛决赛排名奖励'
FinalsRewardContent_1 = '您在问答比赛决赛的跨服排名中位于第%s名，请领取奖励。'
FinalsReady = "#C(#EE7600)【问答比赛】#n决赛现在开始，展现你的智慧的时刻到了，快快来参加吧。#U#C(#00ff00)#A(#K(dlg,OPEN_QUESTION_MSG))我要参加决赛"
FinalsReady_2 = "#C(#EE7600)【问答比赛】#n决赛将于5分钟后开启，请获得决赛资格的龙骑士们做好准备。"
FinalsRewardTitle_2 = "问答比赛决赛参与奖"
FinalsRewardContent_2 = "恭喜您在问答比赛中成功完成决赛答题，请领取决赛奖励。"

#===============================================================================
# 天降横财
#===============================================================================
TJHC_Tips_Reward = "成功领取兑奖码奖励，获得：#H"
TJHC_Tips_IsLottery = "正在结算奖励，结算完毕后才能激活兑奖码！"
TJHC_Mail_Title = "奖券也疯狂"
TJHC_Mail_Sender = "系统"
TJHC_Mail_Content = "您在奖券也疯狂活动结束时尚未领取的奖励，请查收"
TJHC_Tips_RoleDataOverFlow_1 = "最多同时存在%s个已激活的兑奖码，请重新输入激活数量或领取已开奖的奖品再激活"
TJHC_Tips_ServerDataOverFlow = "本轮激活的兑奖码已达上限，请等待下轮活动"
TJHC_Tips_RoleDataOverFlow_2 = "您激活的兑奖码已达本次活动上限，无法继续激活"
TJHC_Msg_AfterLottery = "#C(#EE7600)【奖券也疯狂】#n本轮已开奖，你中奖了吗？！"
TJHC_Mail_Title2 = "奖券也疯狂未激活的兑奖码"
TJHC_Mail_Sender2 = "系统"
TJHC_Mail_Content2 = "您在奖券也疯狂活动结束时尚有%s个激活码未使用，每个激活码将返回10神石给您，请查收"
#===============================================================================
# 魔龙降临
#===============================================================================
MD_NoTimes = "您的挑战次数已用完。"
MD_Name = "魔龙降临"
#===============================================================================
# 深渊炼狱
#===============================================================================
DeepHell_Msg_OneMinBefore = "#C(#EE7600)【深渊炼狱】#n活动将于一分钟后开始，请各位勇士做好准备！"
DeepHell_Msg_RealActive = "#C(#EE7600)【深渊炼狱】#n活动入口已经开启！"
DeepHell_Tips_MonsterInFight = "该怪物已在战斗中！"
DeepHell_BuffName = "%s的英魂"
DeepHell_Msg_DropSoul = "#C(#EE7600)【深渊炼狱】#n#C(#FFFF00)%s#n成功终结了#C(#FFFF00)%s#n的%s连杀！地图坐标#C(#00ff00)#U#A(#K(MoveXY,%s,%s))(%s,%s)#n#n#n处出现了“#C(#0066CC)%s的英魂#n”，拾取后可获得%s的属性"
DeepHell_Tips_PickUpBuffFail = "你已经拥有一个英魂BUFF"
DeepHell_Tips_PickUpBuff = "你拾取了%s的英魂，获得附体效果，下一场战斗属性将临时变为%s的属性。"
DeepHell_Msg_PickUpBuffMsg = "#C(#EE7600)【深渊炼狱】#n#C(#FFFF00)%s#n拾取了”#C(#0066CC)%s的英魂#n”，战斗力发生了翻天覆地的变化！"
DeepHell_Msg_RealStart = "#C(#EE7600)【深渊炼狱】#n活动正式开始，炼狱场内，决战登顶！！"
DeepHell_Tips_InProtectCD = "对方处于保护时间中, 请%s秒后再进行挑战"
DeepHell_Tips_TargetOffLine = "对方处于离线状态, 请挑战其他玩家"
DeepHell_Tips_InFightCD = "您处于战斗冷却中, 请%s秒后再选择对手"

DeepHell_Msg_ManyMinBefore = "#C(#EE7600)【深渊炼狱】#n万人酣战，决战登顶，深渊炼狱活动将于%s分钟后开启，请各位勇士做好准备！"

DeepHell_Msg_KillMany_1 = "#C(#EE7600)【深渊炼狱】#n#C(#FFFF00)%s#n气势如虹，已经完成%s连杀。"
DeepHell_Msg_KillMany_2 = "#C(#EE7600)【深渊炼狱】#n#C(#FFFF00)%s#n已经%s连杀了，爆发出无人能挡的气势啊！"
DeepHell_Msg_KillMany_3 = "#C(#EE7600)【深渊炼狱】#n#C(#FFFF00)%s#n正在大杀特杀，达成%s连杀的辉煌战绩，这是要逆天啊！"
DeepHell_Msg_KillMany_4 = "#C(#E87D22)【深渊炼狱】#n#C(#00FF00)%s#n已经突破至#C(#FFFF00)%s#n连杀！强大实力威震四方，真是神魔难挡啊！ "
DeepHell_NPC_Name = "深渊守卫"

def GetDeepHellKillRumor(roleName, killCnt):
	DeepHell_Msg_KillMany_List = [DeepHell_Msg_KillMany_1, DeepHell_Msg_KillMany_2, DeepHell_Msg_KillMany_3]
	if killCnt < 30:
		return (DeepHell_Msg_KillMany_List[random.randint(0, len(DeepHell_Msg_KillMany_List) - 1)]) % (roleName, killCnt)
	else:
		return DeepHell_Msg_KillMany_4 % (roleName, killCnt)
#===============================================================================
# 点金大放送
#===============================================================================
TouchGoldRewardBuff_1 = "购买原石6折优惠"
TouchGoldRewardBuff_2 = "点金积分翻倍效果"
def ReturnTouchGoldRewardBuffTips(index):
	buffTips = {1:TouchGoldRewardBuff_1, 2:TouchGoldRewardBuff_2}
	return buffTips.get(index, None)
#===============================================================================
#捕鱼达人
#===============================================================================
CatchingFishRmb = "%s的%s在神石大转盘中获得了%s神石。我要领奖"
CatchingFishItem = "%s的%s在神石大转盘中获得了%s+%s。我要领奖"
CatchingFishAwardTitle = "捕鱼达人积分排行榜奖励"
CatchingFishAwardContent = '您在捕鱼达人积分排行榜排名中位于第%s名，请领取奖励。'
CatchingFishOverTime = "每天23:55-24:00为排行榜发奖时间，暂时不能捕鱼"
#===============================================================================
# 双十二超值团购
#===============================================================================
D12GroupBuyPre20_Title = "前20名参团奖励"
D12GroupBuyPre20_Sender = "系统"
D12GroupBuyPre20_Content = "亲爱的勇士，您在超值团购里购买%s排名前20，额外赠送一份奖励。"

D12GroupBuyDiscount_Title = "超值团购神石返还"
D12GroupBuyDiscount_Sender = "系统"
D12GroupBuyDiscount_Content = "亲爱的勇士，您在超值团购里购买的%s原价为%s，实际购买人数达到%s人，这是对应档次的神石奖励，请注意查收。"

D12GroupBuy_Tip = "#C(#EE7600)【超值团购】由于大家热情高涨，在团购中人数急剧上升，每个物品前20名购买还可额外获得一份参团奖励！ #U#C(#00ff00)#A(#K(dlg,OPEN_PASSION_ACT|26))我也要团购！"
#===============================================================================
# 双十二激情活动
#===============================================================================
HonBao_Tip = "#C(#EE7600)【幸运红包】#n#C(#00FF00)%s#n发放了一个幸运红包#n#C(#FF0000)【%s】#n #U#C(#00ff00)#A(#K(dlg,OPEN_PASSION_ACT|28))抢红包"
HongBaoOutMax = "今日领取红包已达上限"
RechargePointItemUsed = "使用成功，充值积分增加 %s"
ConsumePointItemUsed = "使用成功，消费积分增加 %s"
ActivityClosed = "活动未开启，不可使用道具"
CannotSendHongBao = "现在发红包的人太多了，请稍后再试。"
#===============================================================================
# 卡牌图鉴
#===============================================================================
CardAtlasAct = "恭喜获得新图鉴"
CardAtlasLevelUp = "图鉴强化成功"
CardAtlasGradeUp = "图鉴进阶成功"
CardAtlasChip = "分解获得：#H卡牌碎片+%s"
#===============================================================================
# 元素精炼
#===============================================================================
ElementalEssenceAmounts = "精炼成功，获得元素精华+%s"

#===============================================================================
#元旦金猪活动
#===============================================================================
NewYearDayPigAmountTips = "恭喜获得：元旦金猪+%s"
NewYearDayEggHummer = "恭喜获得%s个锤子，快砸金蛋吧"
NewYearDayEggAward = "新年砸金蛋，好运连连有，恭喜获得：#Z(%s,%s)#H"

#===============================================================================
# 临时婚戒经验道具
#===============================================================================
WeddingRing_Exp_Tips = "使用成功，获得%s婚戒经验"
WeddingRing_MAX_LEVEL = "当前婚戒已满阶满星！"
#===============================================================================
# 超级转盘
#===============================================================================
STT_Random_Reward_Tips = 	"恭喜你获得:#H"			#恭喜奖励
STT_Super_Reward_Tips = 	"您触发了超级抽奖，恭喜获得:#H"

#===============================================================================
# 元素之灵
#===============================================================================
ElementSpirit_Tips_CultivateSuccess = "培养成功，元素之灵等级提升至%s级%s星"
ElementSpirit_Msg_BreakSuccess = "#C(#EE7600)【元素之灵】#n玩家#C(#00FF00)%s#n长期研习元素之道，成功将元素之灵突破至#C(#FF0000)%s级#n，获取元素之灵的祝福技能，称霸全服指日可待！"
ElementSpirit_Tips_FirstChoose = "选择元素之灵成功，请前往培养元素之灵"
ElementSpirit_Tips_ChangeType = "您已成功切换至%s"
#===============================================================================
# 宝石2048
#===============================================================================
Game2048Title = '宝石2048个人跨服排名奖励'
Game2048Content = '由于你出色的表现，恭喜你在宝石2048获得了全服第%s名，请收下丰厚的奖励，希望你再接再厉，取得更好的成绩！'

#================================================================================
#圣印系统
#================================================================================
ActiveSealSuccess = '恭喜，激活成功！'
NotActiveSeal = '前置圣印未激活，请按顺序激活圣印'
NotEnoughLiLianAmout = '历练值不足，无法升级'
MaxSealLevel = '当前圣印已满级，无法继续升级'
#===============================================================================
# 跨服战场
#===============================================================================
KFZC_TIPS_1 = "#C(#FF0000)【跨服战场】#n#C(#FF9933)剩余#C(#00FF00)25分钟#n#C(#FF9933)开启，请各方战士做好入场准备！"
KFZC_TIPS_2 = "#C(#FF0000)【跨服战场】#n#C(#FF9933)剩余#C(#00FF00)5分钟#n#C(#FF9933)开启，各方战士别错过了入场时间哦！"
KFZC_TIPS_3 = "#C(#FF0000)【跨服战场】#n#C(#FF9933)正式开启，各方勇士有#C(#00FF00)4分钟#n#C(#FF9933)进场准备时间，错过入场时间将无法进入战场，跨服激战一触即发！"
KFZC_TIPS_4 = "#C(#FF0000)【跨服战场】#n#C(#FF9933)激战马上就要开始了，剩余最后#C(#00FF00)1分钟#n#C(#FF9933)进场准备时间，还没进场的勇士请马上进入，跨服激战一触即发！"
KFZC_TIPS_5 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)5人#n，真是实力超群啊！"
KFZC_TIPS_6 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)10人#n，简直是深不见底的实力啊！"
KFZC_TIPS_7 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)20人#n，惊呆了周围的小伙伴了！"
KFZC_TIPS_8 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)40人#n人，已经接近超神了，快来人阻止他啊！"
KFZC_TIPS_9 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)70人#n人，已经超神了，无人能挡啊！"
KFZC_TIPS_10 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)100人#n人，无限超神的节奏！"
KFZC_TIPS_11 = "#C(#FF0000)【跨服战场】#n#C(#00FF00)%s#n已经连杀了#C(#FF9933)150人#n人，实在匪夷所思，这实力已经超越想象了！"
def KFZCReturnKillTips(killCnt):
	KillTipsDict = {5:KFZC_TIPS_5, 10:KFZC_TIPS_6, 20:KFZC_TIPS_7, 40:KFZC_TIPS_8, 70:KFZC_TIPS_9, 100:KFZC_TIPS_10, 150:KFZC_TIPS_11}
	
	return KillTipsDict.get(killCnt)
KFZC_TIPS_12 = "保护时间不能进行攻击！"
KFZC_TIPS_13 = "守卫人数大于1，无法攻击！"
KFZC_TIPS_16 = "主动攻击冷却中，请稍候！"
KFZC_TIPS_17 = "该玩家已被击杀或者离开据点！"
KFZC_TIPS_18 = "胜利"
KFZC_TIPS_19 = "失败"
KFZC_TIPS_20 = "大据点(中)"
KFZC_TIPS_21 = "小据点(上)"
KFZC_TIPS_22 = "小据点(下)"
def KFZCReturnJudianName(judianType):
	JudianNameDict = {1:KFZC_TIPS_20, 2:KFZC_TIPS_21, 3:KFZC_TIPS_22}
	return JudianNameDict.get(judianType)

KFZC_TIPS_23 = "【暗月郡】"
KFZC_TIPS_24 = "【烈阳城】"
def KFZCReturnCampName(campId):
	return KFZC_TIPS_23 if campId == 2 else KFZC_TIPS_24

KFZC_TIPS_25 = "#C(#FF0000)%s#n各位勇士经过激烈的进攻，终于攻陷了#C(#FF9933)%s#n所占领的#C(#00FF00)%s#n，坚守住一举拿下胜利吧！"
KFZC_TIPS_26 = "#C(#FF0000)%s#n众人以迅雷不及掩耳的速度果断入驻#C(#FF9933)%s#n，夺得了防守的先机，局势大好啊！"
KFZC_TIPS_27 = "#C(#FF0000)【跨服战场】#n#C(#FF9933)入口已关闭！"

#===============================================================================
# 混沌神域
#===============================================================================
SealExp_Tips = 		"历练值 +%s#H"
Seal_Tips = 		"印章 +%s#H"

CD_WorldCall_Tips_1 = "#C(#E87D22)【混沌神域-第一章·巨龙山谷】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
CD_WorldCall_Tips_2 = "#C(#E87D22)【混沌神域-第二章·精灵神殿】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
CD_WorldCall_Tips_3 = "#C(#E87D22)【混沌神域-第三章·混沌之地】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
CD_WorldCall_Tips_4 = "#C(#E87D22)【混沌神域-第四章·诸神黄昏】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"
CD_WorldCall_Tips_5 = "#C(#E87D22)【混沌神域-第五章·审判神域】#C(#FFFF00)%s#n队伍向全世界发出召唤，他们尚缺#C(#FFFF00)%s#n人，等待您的加入！#C(#00ff00)#U#T(#K(YQZD,%s,立即加入,))"

CD_TeamCanNotJoin_Tips = "您未通关前置章节，无法加入队伍!"

CD_RankReward_Tips = "#C(#00EE00)%s#n领取了混沌神域排行榜第%s名的奖励，感谢#C(#00EE00)%s、%s、%s#n做出的贡献。"

def GetCD_WorldCall_Tips(index):
	return { 1 : CD_WorldCall_Tips_1
			, 2 : CD_WorldCall_Tips_2
			, 3 : CD_WorldCall_Tips_3
			, 4 : CD_WorldCall_Tips_4
			, 5 : CD_WorldCall_Tips_5
			}.get(index)


#===============================================================================
# 打年兽
#===============================================================================
PassionDaNianShouTip = "#C(#E87D22)【春节献礼】#n玩家#C(#00FF00)%s#C(#FFFFFF)在春节期间攻击年兽，掉落#Z(%s,%s)，真是羡煞旁人！#U#C(#00FF00)#A(#K(dlg,OPEN_PASSION_ACT|33))前往打年兽#n#n#n"


#===============================================================================
# 春节大回馈
#===============================================================================
FestivalRebate_Mail_Sender = "系统"
FestivalRebate_Mail_Title = "春节大回馈奖励"
FestivalRebate_Mail_Content = "您在春节大回馈活动中尚有未领取的奖励：%s神石，请查收！"
FestivalRebate_Tips_Reward = "成功领取返利，获得%s神石"

#================================================================================
#元宵活动
#================================================================================
PassionYuanXiaoTip = "花灯个数 +%s#H"
PassionYuanXiaoLightHuaDeng = "恭喜，成功点亮元宵花灯!"
PassionYuanXiaoIncHeightTip = "恭喜，元宵花灯高度提高了 %s米"
PassionYuanXiaoIncMoreHeightTip = "太不可思议了，您在提升元宵花灯高度时触发暴击，花灯高度提高%s米"
PassionYuanXiaoHuaDengAward = "完成目标%s获得奖励：#Z(%s,%s)#H"
#===============================================================================
# 连连看
#===============================================================================
LLKan_No_Start = "游戏未完成，不能开始下一盘！"
LLKan_BorMst = "好运连连！玩家#C(#00FF00)%s#C(#FFFFFF)在连连看中获得#Z(%s,%s)真是可喜可贺啊！#U#C(#00ff00)#A(#K(dlg,OPEN_LLK_PANEL))我也要玩！"

#===============================================================================
# 秘密花园
#===============================================================================
SecretGarden_Tips_Head = "恭喜您 获得：#H"
SecretGarden_Msg_Precious = "#C(#E87D22)【魔法花园】#n#C(#FFFF00)%s#n在探秘时意外获得#Z(%s,%s)，运气真是好到爆！！！"
SecretGarden_Msg_Lucky = "#C(#E87D22)【魔法花园】#n#C(#FFFF00)%s#n在辛勤地培养后，获得了#Z(%s,%s)"

SecretGarden_Mail_Title_1 = "魔法花园未领果实奖励"
SecretGarden_Mail_Sender_1 = "系统"
SecretGarden_Mail_Content_1 = "您在魔法花园中有未领取的奖励，请查收附件"

SecretGarden_Mail_Title_2 = "魔法花园未领累计抽奖奖励"
SecretGarden_Mail_Sender_2 = "系统"
SecretGarden_Mail_Content_2 = "您在魔法花园中有未领取的奖励，请查收附件"

#===============================================================================
# 幸运扭蛋--时装扭蛋
#===============================================================================
GashaponGoodTip = '#C(#E87D22)【幸运扭蛋】#n#C(#FFFF00)%s#n在高级扭蛋时获得了珍稀奖励#Z(%s,%s)，下一个幸运者会是谁？'
GashaponSuperTip = '#C(#E87D22)【幸运扭蛋】#n#C(#FFFF00)%s#n在超级扭蛋时获得了珍稀奖励#Z(%s,%s)，下一个幸运者会是谁？'
#坐骑扭蛋
MountGashaponGoodTip = '#C(#E87D22)【幸运扭蛋】#n#C(#FFFF00)%s#n通过高级扭蛋获得了珍稀奖励#Z(%s,%s)，下一个幸运者会是谁？'
MountGashaponSuperTip = '#C(#E87D22)【幸运扭蛋】#n#C(#FFFF00)%s#n通过超级扭蛋获得了珍稀奖励#Z(%s,%s)和1个万能碎片！稀有坐骑换换换！'
#===============================================================================
# 充值送代币
#===============================================================================
DaiBiMailTitle = "春天特惠活动未领物品" 
DaiBiMailContent = "您在充值送大礼活动中有未领取的奖励，系统已将物品暂存在邮件附件中。请在7天内及时提取物品，避免过期损失。"

#===============================================================================
# 收集大作战
#===============================================================================
CollectFightEnd = "#C(#E87D22)【收集大作战】#n活动已结束，已返还投入%s神石"
CollectFightRumor = "#C(#00FF00)%s#n在#C(#E87D22)【收集大作战】#n中获得了#Z(%s,%s)。#U#C(#00ff00)#A(#K(dlg,COLLECTION_OPEN_COLLECTION_PANEL))我要参加！"
CollectFightWord_1 = "【至】"
CollectFightWord_2 = "【尊】"
CollectFightWord_3 = "【龙】"
CollectFightWord_4 = "【骑】"
CollectFightWord_5 = "【士】"
def ReturnCollectWord(index):
	CollectFightWordDict = {1:CollectFightWord_1, 2:CollectFightWord_2, 3:CollectFightWord_3, 4:CollectFightWord_4, 5:CollectFightWord_5}
	return CollectFightWordDict.get(index)
CollectFightUseFail = "活动暂未开启， 不能使用该物品"
CollectFightUseSuccess = "激活成功， 收集到%s个%s字"
CollectFightMail_Title = "收集大作战奖金奖励"
CollectFightMail_Sender = "系统"
CollectFightMail_Content = "亲爱的玩家，您在本次收集大作战中共集齐【龙骑士】%s套，获得%s神石。【至尊龙骑士】%s套，获得%s神石，请注意查收！"
CollectThree = "“%s”“%s”“%s”"
CollectFive = "“%s”“%s”“%s”“%s”“%s”"
CollectWordTips = "#C(#E87D22)【收集大作战】#n#C(#00FF00)%s#n左拼右凑终于集齐了#C(#E87D22)%s#n,获得了平分高额奖池的资格！"

#===============================================================================
# gm禁言
#===============================================================================
GMPowerUseSuccess = "禁言成功"

#===============================================================================
# 印记排行榜
#===============================================================================
EBRank_Local_Title = "印记本服排名奖励"
EBRank_Local_Sender = "系统"
EBRank_Local_Content = "恭喜！您在【印记本服排行榜】活动中排名第%s，获得了丰厚奖励！"

EBRank_KuaFu_Title = "印记跨服排名奖励"
EBRank_KuaFu_Sender = "系统"
EBRank_KuaFu_Content = "恭喜！您在【印记跨服排行榜】活动中排名第%s，获得了丰厚奖励！"
#===============================================================================
# YY防沉迷\月卡
#===============================================================================
YYAnti_Msg = "您本日已累计在线%s小时，请合理安排游戏时间。"
YYCard_Mail_Title = "购月卡返利"
YYCard_Mail_Title2 = "购周卡返利"
YYCard_Mail_Send = "系统"
YYCard_Mail_Content = "恭喜您成为了至尊月卡用户，每次开通均可享受神石全额返还的福利，至尊卡激活期间，每天还可领取每日魔晶返利，多买多送！从此享有至尊特权，走上人生巅峰！"
YYCard_Mail_Content2 = "恭喜您成为了至尊周卡用户，每次开通均可享受神石全额返还，至尊卡激活期间，每天还可领取每日魔晶返利，多买多送！开通月卡或者半年卡，还可以享受至尊特权！"
YYCard_MailS_Content = "恭喜您为好友开通了至尊月卡，每次给好友赠送至尊卡，您可享受神石全额返还的福利"
YYAntiNoReward = "您已在线5小时以上，收益降为0！"
#===============================================================================
# 印记铸灵幻化
#===============================================================================
ElementBrand_Tips_ZhuLingSingle = "铸灵成功，获得%s倍经验%s"
ElementBrand_Tips_ZhuLingMulti_H = "共铸灵%s次，共获得经验%s。其中"
ElementBrand_Tips_ZhuLingMulti_T = "%s倍经验%s次;"

EB_Vision_None = "新的幻化外形"
EB_Vision_1 = "骑士之剑"
EB_Vision_Dict = {1:EB_Vision_1}
ElementBrand_Tips_NewVision = "恭喜获得%s"
def GetNameByVisionID(visionId):
	if visionId in EB_Vision_Dict:
		return EB_Vision_Dict[visionId]
	else:
		return EB_Vision_None

ElementSoul_Tips_EquipTalent = "使用%s天赋成功"
ElementSoul_Tips_VisionUp = "幻化成功"
ElementSoul_Tips_VisionDown = "取消幻化"