package
{
	
	import flash.display.Sprite;
	
	
	public class USConfig extends Sprite
	{
		[Embed(source = 'SceneConfig/SceneConfig.txt',mimeType = "application/octet-stream")]
		public var SceneConfig:Class;
		[Embed(source = 'ClientConfig/TXT/Status/StatusRelation.txt',mimeType = "application/octet-stream")]
		public var StatusRelation:Class;
		
		
		[Embed(source = 'ClientConfig/TXT/displayConfig/BtnOpenLevel.txt',mimeType = "application/octet-stream")]
		public var BtnOpenLevel:Class;
		[Embed(source = 'ClientConfig/TXT/displayConfig/BtnSecond.txt',mimeType = "application/octet-stream")]
		public var BtnSecond:Class;

		[Embed(source = 'ClientConfig/US_language.txt',mimeType = "application/octet-stream")]
		public var LanguageConfig:Class;
		[Embed(source = 'ClientConfig/color_english.txt',mimeType = "application/octet-stream")]
		public var color:Class;
		[Embed(source = 'ClientConfig/formation.xml',mimeType = "application/octet-stream")]
		public var Formation:Class;
		[Embed(source = 'ClientConfig/ChannelConfig.txt',mimeType = "application/octet-stream")]
		public var ChannelCfg:Class;
		[Embed(source = 'ClientConfig/SystemPrompts.txt',mimeType = "application/octet-stream")]
		public var SystemPromptCfg:Class;

		[Embed(source = 'WordMap/WordMap.txt',mimeType = "application/octet-stream")]
		public var WordMap:Class;

		[Embed(source = 'RuneWheel/runewheellib.txt',mimeType = "application/octet-stream")]
		public var runewheellib:Class;

		[Embed(source = 'Npc/SceneNpc.txt',mimeType = "application/octet-stream")]
		public var SceneNpc:Class;
		[Embed(source = 'Npc/NpcConfig.txt',mimeType = "application/octet-stream")]
		public var NpcConfig:Class;
		[Embed(source = 'Npc/NpcXuanXiang.txt',mimeType = "application/octet-stream")]
		public var NpcXuanXiang:Class;

		[Embed(source = 'RoleStatus/RoleStatus.txt',mimeType = "application/octet-stream")]
		public var RoleStatus:Class;

		[Embed(source = 'RoleConfig/LevelExp.txt',mimeType = "application/octet-stream")]
		public var LevelExp:Class;


		[Embed(source = 'DragonTreasure/DragonDigEvent.txt',mimeType = "application/octet-stream")]
		public var DragonDigEvent:Class;
		[Embed(source = 'DragonTreasure/DragonEvent.txt',mimeType = "application/octet-stream")]
		public var DragonEvent:Class;
		[Embed(source = 'DragonTreasure/DragonIdName.txt',mimeType = "application/octet-stream")]
		public var DragonIdName:Class;
		[Embed(source = 'DragonTreasure/EventForType.txt',mimeType = "application/octet-stream")]
		public var EventForType:Class;
		[Embed(source = 'DragonTreasure/DragonReward.txt',mimeType = "application/octet-stream")]
		public var DragonReward:Class;

		//等级礼包
		[Embed(source = 'LevelGife/LevelGife.txt',mimeType = "application/octet-stream")]
		public var LevelGife:Class;
		//等级提升增加数据表
		[Embed(source = 'LevelGife/LevelUp.txt',mimeType = "application/octet-stream")]
		public var LevelUp:Class;

		[Embed(source = 'ClientConfig/sameScreen.txt',mimeType = "application/octet-stream")]
		public var sameScreen:Class;
		[Embed(source = 'HeavenUnRMB/HeavenUnRMB_english.txt',mimeType = "application/octet-stream")]
		public var HeavenUnRMBCfg:Class;





		[Embed(source = 'RoleConfig/RoleBaseProConfig.txt',mimeType = "application/octet-stream")]
		public var RoleBaseProConfig:Class;

		[Embed(source = 'HeroConfig/GradeConfig.txt',mimeType = "application/octet-stream")]
		public var GradeConfig:Class;

		[Embed(source = 'HeroConfig/HeroBaseConfig.txt',mimeType = "application/octet-stream")]
		public var HeroBaseConfig:Class;
		[Embed(source = 'HeroConfig/HeroLevelExp.txt',mimeType = "application/octet-stream")]
		public var HeroLevelExp:Class;
		[Embed(source = 'HeroConfig/HeroExpItem.txt',mimeType = "application/octet-stream")]
		public var HeroExpItem:Class;
		[Embed(source = 'Station/HelpStation.txt',mimeType = "application/octet-stream")]
		public var HelpStation:Class;
		[Embed(source = 'Station/HelpStationCrystalEx.txt',mimeType = "application/octet-stream")]
		public var HelpStationCrystalEx:Class;
		[Embed(source = 'Station/HelpStationMosaic.txt',mimeType = "application/octet-stream")]
		public var HelpStationMosaic:Class;
		[Embed(source = 'Station/HelpStationMosaicPrecent.txt',mimeType = "application/octet-stream")]
		public var HelpStationMosaicPrecent:Class;

		[Embed(source = 'HeroConfig/HeroSkill.txt',mimeType = "application/octet-stream")]
		public var HeroSkill:Class;
		[Embed(source = 'HeroConfig/HeroAltar_english.txt',mimeType = "application/octet-stream")]
		public var HeroAltar:Class;
		[Embed(source = 'HeroConfig/HeroChangeConfig.txt',mimeType = "application/octet-stream")]
		public var HeroChangeConfig:Class;


		[Embed(source = 'Mount/MountIllusion_english.txt',mimeType = "application/octet-stream")]
		public var MountIllusion:Class;
		[Embed(source = 'Mount/MountEvolve_english.txt',mimeType = "application/octet-stream")]
		public var MountEvolve:Class;
		[Embed(source = 'Mount/MountFood.txt',mimeType = "application/octet-stream")]
		public var MountFood:Class;
		[Embed(source = 'Mount/MountItem.txt',mimeType = "application/octet-stream")]
		public var MountItem:Class;
		[Embed(source = 'Mount/MountGrade.txt',mimeType = "application/octet-stream")]
		public var MountGrade:Class;
		[Embed(source = 'Mount/MountExchange.txt',mimeType = "application/octet-stream")]
		public var MountExchange:Class;

		[Embed(source = 'ItemConfig/PackageGrid.txt',mimeType = "application/octet-stream")]
		public var PackageGrid:Class;

		[Embed(source = 'ItemConfig/PackageSize.txt',mimeType = "application/octet-stream")]
		public var PackageSize:Class;

		[Embed(source = 'ItemConfig/Equipment.txt',mimeType = "application/octet-stream")]
		public var Equipment:Class;

		[Embed(source = 'ItemConfig/EquipmentGodcast.txt',mimeType = "application/octet-stream")]
		public var EquipmentGodcast:Class;

		[Embed(source = 'ItemConfig/EquipmentSell.txt',mimeType = "application/octet-stream")]
		public var EquipmentSell:Class;

		[Embed(source = 'ItemConfig/EquipmentUpgrade.txt',mimeType = "application/octet-stream")]
		public var EquipmentUpgrade:Class;

		[Embed(source = 'ItemConfig/Item_english.txt',mimeType = "application/octet-stream")]
		public var Item:Class;

		[Embed(source = 'ItemConfig/Strengthen.txt',mimeType = "application/octet-stream")]
		public var Strengthen:Class;

		[Embed(source = 'ItemConfig/EquipmentSuit.txt',mimeType = "application/octet-stream")]
		public var EquipmentSuit:Class;


		[Embed(source = 'ItemConfig/EquipmentGem.txt',mimeType = "application/octet-stream")]
		public var EquipmentGem:Class;

		[Embed(source = 'ItemConfig/GemSealingSpirit.txt',mimeType = "application/octet-stream")]
		public var GemSealingSpirit:Class;





		[Embed(source = 'ItemConfig/Artifact.txt',mimeType = "application/octet-stream")]
		public var Artifact:Class;
		[Embed(source = 'ItemConfig/ArtifactGem.txt',mimeType = "application/octet-stream")]
		public var ArtifactGem:Class;
		[Embed(source = 'ItemConfig/ArtifactGemSealing.txt',mimeType = "application/octet-stream")]
		public var ArtifactGemSealing:Class;
		[Embed(source = 'ItemConfig/ArtifactStrengthen.txt',mimeType = "application/octet-stream")]
		public var ArtifactStrengthen:Class;
		[Embed(source = 'ItemConfig/ArtifactUpgrade.txt',mimeType = "application/octet-stream")]
		public var ArtifactUpgrade:Class; 
		[Embed(source = 'ItemConfig/ArtifactSuit.txt',mimeType = "application/octet-stream")]
		public var ArtifactSuit:Class;
		[Embed(source = 'ItemConfig/ArtifactSell.txt',mimeType = "application/octet-stream")]
		public var ArtifactSell:Class;
		[Embed(source = 'ItemConfig/Hallows.txt',mimeType = "application/octet-stream")]
		public var Hallows:Class;
		[Embed(source = 'ItemConfig/HallowsBaseProp.txt',mimeType = "application/octet-stream")]
		public var HallowsBaseProp:Class;
		[Embed(source = 'ItemConfig/HallowsEnchant.txt',mimeType = "application/octet-stream")]
		public var HallowsEnchant:Class;
		[Embed(source = 'Hallows/HallowsHero.txt',mimeType = "application/octet-stream")]
		public var HallowsHero:Class;
		[Embed(source = 'ItemConfig/HallowsGem.txt',mimeType = "application/octet-stream")]
		public var HallowsGem:Class;
		
		[Embed(source = 'KuaFuJJC/KuaFuShop_english.txt',mimeType = "application/octet-stream")]
		public var KuaFuShop:Class;
		[Embed(source = 'KuaFuJJC/KuaFuJJCFinalsRankReward.txt',mimeType = "application/octet-stream")]
		public var KuaFuJJCFinalsRankReward:Class;
		[Embed(source = 'KuaFuJJC/KuaFuJJCUnionRankReward_english.txt',mimeType = "application/octet-stream")]
		public var KuaFuJJCUnionRankReward:Class;
		[Embed(source = 'KuaFuJJC/KuaFuJJCUnionScoreReward_english.txt',mimeType = "application/octet-stream")]
		public var KuaFuJJCUnionScoreReward:Class;

		[Embed(source = 'FBAndEvilHoleConfig/FB.txt',mimeType = "application/octet-stream")]
		public var FB:Class;
		[Embed(source = 'FBAndEvilHoleConfig/FBAddTimes.txt',mimeType = "application/octet-stream")]
		public var FBAddTimes:Class;
		[Embed(source = 'FBAndEvilHoleConfig/FBReward.txt',mimeType = "application/octet-stream")]
		public var FBReward:Class;
		[Embed(source = 'FBAndEvilHoleConfig/FBZhangJie.txt',mimeType = "application/octet-stream")]
		public var FBZhangJie:Class;
		[Embed(source = 'FBAndEvilHoleConfig/EvilHole.txt',mimeType = "application/octet-stream")]
		public var EvilHole:Class;
		[Embed(source = 'FBAndEvilHoleConfig/EvilHoleReward.txt',mimeType = "application/octet-stream")]
		public var EvilHoleReward:Class;

		[Embed(source = 'StudySkill/SkillList.txt',mimeType = "application/octet-stream")]
		public var SkillList:Class;
		[Embed(source = 'StudySkill/SkillLevelup.txt',mimeType = "application/octet-stream")]
		public var SkillLevelup:Class;

		[Embed(source = 'JJC/JJCBuyCnt_english.txt',mimeType = "application/octet-stream")]
		public var JJCBuyCnt:Class;
		[Embed(source = 'JJC/JJCRankReputation.txt',mimeType = "application/octet-stream")]
		public var JJCRankReputation:Class;
		[Embed(source = 'JJC/JJCRankAward.txt',mimeType = "application/octet-stream")]
		public var JJCRankAward:Class;
		[Embed(source = 'JJC/JJCExchange.txt',mimeType = "application/octet-stream")]
		public var JJCExchange:Class;
		[Embed(source = 'JJC/JJCChallengeAward.txt',mimeType = "application/octet-stream")]
		public var JJCChallengeAward:Class;

		[Embed(source = 'Gold/GoldConfig.txt',mimeType = "application/octet-stream")]
		public var GoldConfig:Class;
		[Embed(source = 'Gold/GoldTimes_english.txt',mimeType = "application/octet-stream")]
		public var GoldTimes:Class;
		[Embed(source = 'VIP/VIPBase_english.txt',mimeType = "application/octet-stream")]
		public var VIPBase:Class;
		[Embed(source = 'VIP/CardsConfig_english.txt',mimeType = "application/octet-stream")]
		public var CardsConfig:Class;
		[Embed(source = 'VIP/VipDesc_english.txt',mimeType = "application/octet-stream")]
		public var VipDesc:Class;
		[Embed(source = 'VIP/VipPower_english.txt',mimeType = "application/octet-stream")]
		public var VipPower:Class;
		[Embed(source = 'VIP/VipReward_english.txt',mimeType = "application/octet-stream")]
		public var VipReward:Class;
		[Embed(source = 'VIP/SuperVIPDReward_english.txt',mimeType = "application/octet-stream")]
		public var SuperVIPDReward:Class;
		[Embed(source = 'VIP/SuperVIPPointShop.txt',mimeType = "application/octet-stream")]
		public var SuperVIPPointShop:Class;
		[Embed(source = 'VIP/SuperVIPTitle.txt',mimeType = "application/octet-stream")]
		public var SuperVIPTitle:Class;
		[Embed(source = 'VIP/SuperVIPicon.txt',mimeType = "application/octet-stream")]
		public var SuperVIPicon:Class;

		[Embed(source = 'Award/AwardBase.txt',mimeType = "application/octet-stream")]
		public var AwardBase:Class;
		
		[Embed(source = 'Union/UnionShenShouLevel.txt',mimeType = "application/octet-stream")]
		public var UnionShenShouLevel:Class;
		[Embed(source = 'Union/UnionShenShouFeed_english.txt',mimeType = "application/octet-stream")]
		public var UnionShenShouFeed:Class;
		[Embed(source = 'Union/UnionShenShouGood_english.txt',mimeType = "application/octet-stream")]
		public var UnionShenShouGood:Class;
		[Embed(source = 'Union/UnionShenShouBuf_english.txt',mimeType = "application/octet-stream")]
		public var UnionShenShouBuf:Class;
		[Embed(source = 'Union/UnionShenShouHurtRankAward.txt',mimeType = "application/octet-stream")]
		public var UnionShenShouHurtRankAward:Class;
		[Embed(source = 'Union/UnionSkill.txt',mimeType = "application/octet-stream")]
		public var UnionSkill:Class;
		[Embed(source = 'Union/UnionGood_english.txt',mimeType = "application/octet-stream")]
		public var UnionGood:Class;
		[Embed(source = 'Union/UnionMagicTower.txt',mimeType = "application/octet-stream")]
		public var UnionMagicTower:Class;
		[Embed(source = 'Union/UnionShenShouTan.txt',mimeType = "application/octet-stream")]
		public var UnionShenShouTan:Class;
		[Embed(source = 'Union/UnionStore.txt',mimeType = "application/octet-stream")]
		public var UnionStore:Class;

		[Embed(source = 'Union/AchievementBox.txt',mimeType = "application/octet-stream")]
		public var AchievementBox:Class;
		[Embed(source = 'Union/DayBox.txt',mimeType = "application/octet-stream")]
		public var DayBox:Class;
		[Embed(source = 'Union/Job.txt',mimeType = "application/octet-stream")]
		public var Job:Class;
		[Embed(source = 'Union/TreasureGet.txt',mimeType = "application/octet-stream")]
		public var TreasureGet:Class;
		[Embed(source = 'Union/TreasureRob.txt',mimeType = "application/octet-stream")]
		public var TreasureRob:Class;
		[Embed(source = 'Union/UnionBase.txt',mimeType = "application/octet-stream")]
		public var UnionBase:Class;
		[Embed(source = 'Union/God.txt',mimeType = "application/octet-stream")]
		public var God:Class;
		[Embed(source = 'Union/UnionTaskRewardFactor.txt',mimeType = "application/octet-stream")]
		public var UnionTaskRewardFactor:Class;
		
		[Embed(source = 'Union/UnionFBBase.txt',mimeType = "application/octet-stream")]
		public var UnionFBBase:Class;
		[Embed(source = 'Union/UnionFBMonster.txt',mimeType = "application/octet-stream")]
		public var UnionFBMonster:Class;
		[Embed(source = 'Union/UnionFBBuyCnt_english.txt',mimeType = "application/octet-stream")]
		public var UnionFBBuyCnt:Class;
		[Embed(source = 'Union/UnionTask.txt',mimeType = "application/octet-stream")]
		public var UnionTask:Class;
		
		[Embed(source = 'Union/UnionExploreBuyCnt_english.txt',mimeType = "application/octet-stream")]
		public var UnionExploreBuyCnt:Class;
		[Embed(source = 'Union/UnionExploreQuestion_english.txt',mimeType = "application/octet-stream")]
		public var UnionExploreQuestion:Class;
		[Embed(source = 'Union/UnionExplorePrisonerOutput.txt',mimeType = "application/octet-stream")]
		public var UnionExplorePrisonerOutput:Class;
		
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarTime_english.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarTime:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarZone.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarZone:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarGate.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarGate:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarTotalRank.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarTotalRank:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarUnionRank.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarUnionRank:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarUnionRoleRank.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarUnionRoleRank:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarBuffBase.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarBuffBase:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarBuffZDL.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarBuffZDL:Class;
		[Embed(source = 'UnionKuaFuWar/UnionKuaFuWarGoddessBuff.txt',mimeType = "application/octet-stream")]
		public var UnionKuaFuWarGoddessBuff:Class;

		//任务 	MainTask
		[Embed(source = 'Task/MainTask_english.txt',mimeType = "application/octet-stream")]
		public var MainTask:Class;
		[Embed(source = 'Task/TaskFightReward.txt',mimeType = "application/octet-stream")]
		public var TaskFightReward:Class;

		//对白表
		[Embed(source = 'Task/DuiBai.txt',mimeType = "application/octet-stream")]
		public var DuiBai:Class;
		//支线任务
		[Embed(source = 'Task/SubTask_english.txt',mimeType = "application/octet-stream")]
		public var SubTask:Class;
		//日常任务
		[Embed(source = 'Task/DayTask.txt',mimeType = "application/octet-stream")]
		public var DayTask:Class;
		//体力任务
		[Embed(source = 'Task/TiLiTask.txt',mimeType = "application/octet-stream")]
		public var TiLiTask:Class;

		[Embed(source = 'Fight/Fight.txt',mimeType = "application/octet-stream")]
		public var Fight:Class;
		[Embed(source = 'Fight/Monster_english.txt',mimeType = "application/octet-stream")]
		public var Monster:Class;
		[Embed(source = 'Fight/BossDesc.txt',mimeType = "application/octet-stream")]
		public var BossDesc:Class;
		[Embed(source = 'Fight/Buff.txt',mimeType = "application/octet-stream")]
		public var Buff:Class;
		[Embed(source = 'Fight/ResourceFightShow.txt',mimeType = "application/octet-stream")]
		public var ResourceFightShow:Class;
		[Embed(source = 'StudySkill/SkillCfg.txt',mimeType = "application/octet-stream")]
		public var SkillCfg:Class;

		[Embed(source = 'GoblinTreasure/GTConfig.txt',mimeType = "application/octet-stream")]
		public var GTConfig:Class;
		[Embed(source = 'GoblinTreasure/GTNpcConfig.txt',mimeType = "application/octet-stream")]
		public var GTNpcConfig:Class;
		[Embed(source = 'Purgatory/PurgatoryConfig.txt',mimeType = "application/octet-stream")]
		public var PurgatoryConfig:Class;
		[Embed(source = 'Purgatory/PurgatoryFuhuo_english.txt',mimeType = "application/octet-stream")]
		public var PurgatoryFuHuo:Class;

		[Embed(source = 'DemonDefense/KillReward.txt',mimeType = "application/octet-stream")]
		public var KillReward:Class;
		[Embed(source = 'DemonDefense/LuckyDrawBase.txt',mimeType = "application/octet-stream")]
		public var LuckyDrawBase:Class;
		[Embed(source = 'DukeOnDuty/AttackBuffInfo.txt',mimeType = "application/octet-stream")]
		public var AttackBuffInfo:Class;
		[Embed(source = 'DukeOnDuty/BuffInfo.txt',mimeType = "application/octet-stream")]
		public var BuffInfo:Class;
		[Embed(source = 'DukeOnDuty/CDCost.txt',mimeType = "application/octet-stream")]
		public var CDCost:Class;

		[Embed(source = 'Shop/FBShop_english.txt',mimeType = "application/octet-stream")]
		public var FBShop:Class;
		[Embed(source = 'ClientConfig/TXT/Reputation/ReputationConfig.txt',mimeType = "application/octet-stream")]
		public var ReputationConfig:Class;

		[Embed(source = 'exam/examAward.txt',mimeType = "application/octet-stream")]
		public var examAward:Class;
		[Embed(source = 'exam/examLib_english.txt',mimeType = "application/octet-stream")]
		public var examLib:Class;
		[Embed(source = 'DailyDo/DailyDoConfig_english.txt',mimeType = "application/octet-stream")]
		public var DailyDoConfig:Class;
		[Embed(source = 'DailyDo/DailyDoRewardConfig_english.txt',mimeType = "application/octet-stream")]
		public var DailyDoRewardConfig:Class;

		[Embed(source = 'FiveGift/FiveGiftBase_english.txt',mimeType = "application/octet-stream")]
		public var FiveGiftBase:Class;
		[Embed(source = 'FiveGift/FiveGiftLuckyDraw.txt',mimeType = "application/octet-stream")]
		public var FiveGiftLuckyDraw:Class;
		[Embed(source = 'FiveGift/DayFirstPayReward.txt',mimeType = "application/octet-stream")]
		public var DayFirstPayReward:Class;

		// 在线奖励
		[Embed(source = 'OnLineReward/OnLineReward.txt',mimeType = "application/octet-stream")]
		public var OnLineReward:Class;
		
		
		[Embed(source = 'Shop/Mall_english.txt',mimeType = "application/octet-stream")]
		public var Mall:Class;
		[Embed(source = 'Shop/Coupons.txt',mimeType = "application/octet-stream")]
		public var Coupons:Class;
		[Embed(source = 'Shop/GSMall.txt',mimeType = "application/octet-stream")]
		public var GSMall:Class;
		
		[Embed(source = 'ThirdParty/QGoods.txt',mimeType = "application/octet-stream")]
		public var QGoods:Class;

		[Embed(source = 'Wing/WingBase_english.txt',mimeType = "application/octet-stream")]
		public var WingBase:Class;
		[Embed(source = 'Wing/WingCollect.txt',mimeType = "application/octet-stream")]
		public var WingCollect:Class;


		//7日礼包配置表
		[Embed(source = 'LegionReward/LegionSevenReward.txt',mimeType = "application/octet-stream")]
		public var LegionSevenReward:Class;
		//登录礼包配置表
		[Embed(source = 'LegionReward/LegionReward.txt',mimeType = "application/octet-stream")]
		public var LegionReward:Class;

		[Embed(source = 'Tarot/CardLevelExp.txt',mimeType = "application/octet-stream")]
		public var CardLevelExp:Class;
		[Embed(source = 'Tarot/LevelOpenPackage.txt',mimeType = "application/octet-stream")]
		public var LevelOpenPackage:Class;
		[Embed(source = 'Tarot/Tarot.txt',mimeType = "application/octet-stream")]
		public var Tarot:Class;
		[Embed(source = 'Tarot/TarotCard.txt',mimeType = "application/octet-stream")]
		public var TarotCard:Class;
		[Embed(source = 'Tarot/TarotRing.txt',mimeType = "application/octet-stream")]
		public var TarotRing:Class;
		[Embed(source = 'Tarot/TarotShop.txt',mimeType = "application/octet-stream")]
		public var TarotShop:Class;

		[Embed(source = 'GloryWar/GloryWarScoreReward.txt',mimeType = "application/octet-stream")]
		public var GloryWarScoreReward:Class;
		[Embed(source = 'GloryWar/GloryWarNpc.txt',mimeType = "application/octet-stream")]
		public var GloryWarNpc:Class;
		[Embed(source = 'ClientConfig/TXT/ZYConfig/ZYSure.txt',mimeType = "application/octet-stream")]
		public var ZYSure:Class;
		[Embed(source = 'WonderfulAct/WonderfulAct_english.txt',mimeType = "application/octet-stream")]
		public var WonderfulAct:Class;
		[Embed(source = 'WonderfulAct/WonderfulActClient.txt',mimeType = "application/octet-stream")]
		public var WonderfulActClient:Class;
		[Embed(source = 'WonderfulAct/WonderfulReward_english.txt',mimeType = "application/octet-stream")]
		public var WonderfulReward:Class;
		[Embed(source = 'ProjectAct/ProjectAct_english.txt',mimeType = "application/octet-stream")]
		public var ProjectAct:Class;
		[Embed(source = 'ProjectAct/ProjectActReward_english.txt',mimeType = "application/octet-stream")]
		public var ProjectActReward:Class;
		[Embed(source = 'LatestActivity/LatestActBase.txt',mimeType = "application/octet-stream")]
		public var LatestActBase:Class;
		[Embed(source = 'LatestActivity/LatestActReward.txt',mimeType = "application/octet-stream")]
		public var LatestActReward:Class;
		[Embed(source = 'LatestActivity/TaskConfig.txt',mimeType = "application/octet-stream")]
		public var TaskConfig:Class;
		[Embed(source = 'ClientConfig/TXT/BuffConfig/SpecialBuffCfg.txt',mimeType = "application/octet-stream")]
		public var SpecialBuffCfg:Class;
		[Embed(source = 'RushLevel/RushLevelReward.txt',mimeType = "application/octet-stream")]
		public var RushLevelReward:Class;
		[Embed(source = 'Activity/ActivityTime.txt',mimeType = "application/octet-stream")]
		public var ActivityTime:Class;

		[Embed(source = 'LuckTurantable/reward_english.txt',mimeType = "application/octet-stream")]
		public var reward:Class;
		[Embed(source = 'LuckTurantable/lukcnt.txt',mimeType = "application/octet-stream")]
		public var lukcnt:Class;
		[Embed(source = 'LuckTurantable/LuckType.txt',mimeType = "application/octet-stream")]
		public var LuckType:Class;
		[Embed(source = 'Title/Title_english.txt',mimeType = "application/octet-stream")]
		public var Title:Class;
		[Embed(source = 'Title/TitleLevel.txt',mimeType = "application/octet-stream")]
		public var TitleLevel:Class;
		[Embed(source = 'Title/TitleStar.txt',mimeType = "application/octet-stream")]
		public var TitleStar:Class;
		[Embed(source = 'Title/TitleNode.txt',mimeType = "application/octet-stream")]
		public var TitleNode:Class;

		[Embed(source = 'QQHZ/QQHZnovice.txt',mimeType = "application/octet-stream")]
		public var QQHZnovice:Class;

		[Embed(source = 'QQHZ/QQHZlevel.txt',mimeType = "application/octet-stream")]
		public var QQHZlevel:Class;
		[Embed(source = 'QQHZ/QQHZdaily.txt',mimeType = "application/octet-stream")]
		public var QQHZdaily:Class;
		[Embed(source = 'QQHZ/Day3366Reward.txt',mimeType = "application/octet-stream")]
		public var Day3366Reward:Class;
		[Embed(source = 'QQHZ/DailyReward.txt',mimeType = "application/octet-stream")]
		public var DailyReward:Class;

		[Embed(source = 'ClientConfig/TXT/displayConfig/mainIcon.txt',mimeType = "application/octet-stream")]
		public var mainIcon:Class;

		[Embed(source = 'ClientConfig/TXT/displayConfig/TaskPanel.txt',mimeType = "application/octet-stream")]
		public var TaskPanel:Class;


		[Embed(source = 'InviteFriend/InviteFriendReward.txt',mimeType = "application/octet-stream")]
		public var InviteFriendReward:Class;
		[Embed(source = 'InviteFriend/InviteFriend_english.txt',mimeType = "application/octet-stream")]
		public var InviteFriend:Class;
		[Embed(source = 'WeiXin/WeiboZoneConfig.txt',mimeType = "application/octet-stream")]
		public var WeiboZoneConfig:Class;
		[Embed(source = 'WeiXin/WeiXinConfig.txt',mimeType = "application/octet-stream")]
		public var WeiXinConfig:Class;

		[Embed(source = 'Fly/FlyWorld.txt',mimeType = "application/octet-stream")]
		public var FlyWorld:Class;

		[Embed(source = 'CoolTime/CoolTime.txt',mimeType = "application/octet-stream")]
		public var CoolTime:Class;
		[Embed(source = 'ClientConfig/TXT/FailGuide/FailGuideInfo.txt',mimeType = "application/octet-stream")]
		public var FailGuideInfo:Class;
		[Embed(source = 'Pet/PetBase_english.txt',mimeType = "application/octet-stream")]
		public var PetBase:Class;
		[Embed(source = 'Pet/PetInitProperty.txt',mimeType = "application/octet-stream")]
		public var PetInitProperty:Class;
		[Embed(source = 'Pet/PetMaxProperty.txt',mimeType = "application/octet-stream")]
		public var PetMaxProperty:Class;
		[Embed(source = 'Pet/propStarLv.txt',mimeType = "application/octet-stream")]
		public var propStarLv:Class;
		[Embed(source = 'Pet/PetSoulBase.txt',mimeType = "application/octet-stream")]
		public var PetSoulBase:Class;
		[Embed(source = 'Pet/PetLuckyDraw_english.txt',mimeType = "application/octet-stream")]
		public var PetLuckyDraw:Class;
		[Embed(source = 'Pet/PetEvolution_english.txt',mimeType = "application/octet-stream")]
		public var PetEvolution:Class;
		[Embed(source = 'Pet/PetItemLuck.txt',mimeType = "application/octet-stream")]
		public var PetItemLuck:Class;
		[Embed(source = 'PetFarm/petfarm_harvest.txt',mimeType = "application/octet-stream")]
		public var petfarm_harvest:Class;

		[Embed(source = 'HeroTemple/HeroTemple.txt',mimeType = "application/octet-stream")]
		public var HeroTemple:Class;
		[Embed(source = 'HeroTemple/HeroTempleCnt_english.txt',mimeType = "application/octet-stream")]
		public var HeroTempleCnt:Class;

		//捉奴隶
		[Embed(source = 'Slave/SlaveBuyBattle_english.txt',mimeType = "application/octet-stream")]
		public var SlaveBuyBattle:Class;
		[Embed(source = 'Slave/SlaveBuyCatch_english.txt',mimeType = "application/octet-stream")]
		public var SlaveBuyCatch:Class;
		[Embed(source = 'Slave/SlaveBuySave_english.txt',mimeType = "application/octet-stream")]
		public var SlaveBuySave:Class;
		[Embed(source = 'Slave/SlaveExp.txt',mimeType = "application/octet-stream")]
		public var SlaveExp:Class;
		[Embed(source = 'Slave/SlaveMaxExp.txt',mimeType = "application/octet-stream")]
		public var SlaveMaxExp:Class;
		[Embed(source = 'Slave/SlaveDescribe.txt',mimeType = "application/octet-stream")]
		public var SlaveDescribe:Class;

		[Embed(source = 'ToSky/ToSkyConfig_english.txt',mimeType = "application/octet-stream")]
		public var ToSkyConfig:Class;

		//游戏更新公告表
		[Embed(source = 'ClientConfig/TXT/GongGaoConfig/GongGaoCfg_english.txt',mimeType = "application/octet-stream")]
		public var GongGaoCfg:Class;
		[Embed(source = 'ClientConfig/TXT/GongGaoConfig/GongGaoCfg_kgg.txt',mimeType = "application/octet-stream")]
		public var GongGaoCfg_kgg:Class;
		[Embed(source = 'ClientConfig/TXT/GongGaoConfig/GongGaoCfg_englishRBK.txt',mimeType = "application/octet-stream")]
		public var GongGaoCfg_englishRBK:Class;
		[Embed(source = 'LiBaoCanChoose/LiBaoForChoose.txt',mimeType = "application/octet-stream")]
		public var LiBaoChooseCfg:Class;
		[Embed(source = 'LiBaoCanChoose/LiBaoForReward_english.txt',mimeType = "application/octet-stream")]
		public var LiBaoRewardCfg:Class;



		[Embed(source = 'MysteryShop/MineShopConfig_english.txt',mimeType = "application/octet-stream")]
		public var MineShopConfig:Class;
		[Embed(source = 'MysteryShop/MysteryShopConfig.txt',mimeType = "application/octet-stream")]
		public var MysteryShopConfig:Class;
		[Embed(source = 'QQAppPanel/AppPanelLoginReward.txt',mimeType = "application/octet-stream")]
		public var QQLoginCfg:Class;

		[Embed(source = 'RMBFund/RMBFundConfig.txt',mimeType = "application/octet-stream")]
		public var RMBFundConfig:Class;
		[Embed(source = 'RMBFund/RMBPointConfig_english.txt',mimeType = "application/octet-stream")]
		public var RMBPointConfig:Class;
		[Embed(source = 'RMBFund/RMBFundActive.txt',mimeType = "application/octet-stream")]
		public var RMBFundActive:Class;
		[Embed(source = 'CarnivalOfTopup/CarnivalOfTopup_english.txt',mimeType = "application/octet-stream")]
		public var CarnivalOfTopup:Class;


		//一球成名
		[Embed(source = 'BallFame/BFASCheersConfig.txt',mimeType = "application/octet-stream")]
		public var BFASCheersConfig:Class;
		[Embed(source = 'BallFame/BFGoalsConfig.txt',mimeType = "application/octet-stream")]
		public var BFGoalsConfig:Class;
		[Embed(source = 'BallFame/BFRewards_english.txt',mimeType = "application/octet-stream")]
		public var BFRewards:Class;
		[Embed(source = 'BallFame/BFUnionCheersConfig.txt',mimeType = "application/octet-stream")]
		public var BFUnionCheersConfig:Class;


		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlpfList.txt',mimeType = "application/octet-stream")]
		public var ZdlpfList:Class;
		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlpfObject_english.txt',mimeType = "application/octet-stream")]
		public var ZdlpfObject:Class;
		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlpfValue_english.txt',mimeType = "application/octet-stream")]
		public var ZdlpfValue:Class;
		
		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlCanUp.txt',mimeType = "application/octet-stream")]
		public var ZdlCanUp:Class;
		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlCanUpType.txt',mimeType = "application/octet-stream")]
		public var ZdlCanUpType:Class;
		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlTuijian.txt',mimeType = "application/octet-stream")]
		public var ZdlTuijian:Class;
		[Embed(source = 'ClientConfig/TXT/Zdlpf/ZdlTujianType.txt',mimeType = "application/octet-stream")]
		public var ZdlTujianType:Class;

		[Embed(source = 'Dragon/ChangeJob.txt',mimeType = "application/octet-stream")]
		public var ChangeJob:Class;
		[Embed(source = 'Dragon/DragonBase.txt',mimeType = "application/octet-stream")]
		public var DragonBase:Class;
		[Embed(source = 'Dragon/DragonCareer.txt',mimeType = "application/octet-stream")]
		public var DragonCareer:Class;
		[Embed(source = 'Dragon/DragonExp.txt',mimeType = "application/octet-stream")]
		public var DragonExp:Class;
		[Embed(source = 'Dragon/DragonExpItem.txt',mimeType = "application/octet-stream")]
		public var DragonExpItem:Class;
		[Embed(source = 'Dragon/SkillPointProperty.txt',mimeType = "application/octet-stream")]
		public var SkillPointProperty:Class;
		[Embed(source = 'Dragon/DragonGrade.txt',mimeType = "application/octet-stream")]
		public var DragonGrade:Class;
		[Embed(source = 'Dragon/DragonSkill.txt',mimeType = "application/octet-stream")]
		public var DragonSkill:Class;

		//魔域星空
		[Embed(source = 'AsteroidFields/AsteroidFields.txt',mimeType = "application/octet-stream")]
		public var AsteroidFields:Class;
		[Embed(source = 'AsteroidFields/AsteroidFieldsGuanka.txt',mimeType = "application/octet-stream")]
		public var AsteroidFieldsGuanka:Class;

		[Embed(source = 'Marry/WeddingRing.txt',mimeType = "application/octet-stream")]
		public var WeddingRing:Class;
		[Embed(source = 'Marry/WeddingRingBase.txt',mimeType = "application/octet-stream")]
		public var WeddingRingBase:Class;
		[Embed(source = 'Marry/WeddingRingSkill.txt',mimeType = "application/octet-stream")]
		public var WeddingRingSkill:Class;
		[Embed(source = 'Marry/WeddingRingSoul.txt',mimeType = "application/octet-stream")]
		public var WeddingRingSoul:Class;
		[Embed(source = 'Marry/WeddingRingSoulPM.txt',mimeType = "application/octet-stream")]
		public var WeddingRingSoulPM:Class;
		[Embed(source = 'Marry/WeddingRingSoulR.txt',mimeType = "application/octet-stream")]
		public var WeddingRingSoulR:Class;
		[Embed(source = 'Marry/MarryTime.txt',mimeType = "application/octet-stream")]
		public var MarryTime:Class;
		[Embed(source = 'Marry/MarryGrade_english.txt',mimeType = "application/octet-stream")]
		public var MarryGrade:Class;
		[Embed(source = 'Marry/MarryLibao_english.txt',mimeType = "application/octet-stream")]
		public var MarryLibao:Class;
		[Embed(source = 'Marry/PartyGrade_english.txt',mimeType = "application/octet-stream")]
		public var PartyGrade:Class;
		[Embed(source = 'Marry/PartyCandy_english.txt',mimeType = "application/octet-stream")]
		public var PartyCandy:Class;
		[Embed(source = 'Marry/PartyBless_english.txt',mimeType = "application/octet-stream")]
		public var PartyBless:Class;
		[Embed(source = 'Marry/Qinmi.txt',mimeType = "application/octet-stream")]
		public var Qinmi:Class;
		[Embed(source = 'Marry/QinmiGrade.txt',mimeType = "application/octet-stream")]
		public var QinmiGrade:Class;
		[Embed(source = 'Marry/HoneymoonGrade_english.txt',mimeType = "application/octet-stream")]
		public var HoneymoonGrade:Class;
		[Embed(source = 'Marry/Ring.txt',mimeType = "application/octet-stream")]
		public var Ring:Class;
		[Embed(source = 'Marry/PartyHappy_english.txt',mimeType = "application/octet-stream")]
		public var PartyHappy:Class;
		[Embed(source = 'Marry/KuaFuPartyReward.txt',mimeType = "application/octet-stream")]
		public var KuaFuPartyReward:Class;

		[Embed(source = 'DragonEgg/ActivityEgg.txt',mimeType = "application/octet-stream")]
		public var ActivityEgg:Class;
		[Embed(source = 'DragonEgg/EggReward_english.txt',mimeType = "application/octet-stream")]
		public var EggReward:Class;
		[Embed(source = 'DragonEgg/GoldEggConsume_english.txt',mimeType = "application/octet-stream")]
		public var GoldEggConsume:Class;

		//星座天赋卡
		[Embed(source = 'TalentCard/CardLevelExp.txt',mimeType = "application/octet-stream")]
		public var CardLevelExpSky:Class;
		[Embed(source = 'TalentCard/DecTalent.txt',mimeType = "application/octet-stream")]
		public var DecTalent:Class;
		[Embed(source = 'TalentCard/TakentClientSkill.txt',mimeType = "application/octet-stream")]
		public var TakentClientSkill:Class;
		[Embed(source = 'TalentCard/TakentClientSkillGroup.txt',mimeType = "application/octet-stream")]
		public var TakentClientSkillGroup:Class;
		[Embed(source = 'TalentCard/TalentCard.txt',mimeType = "application/octet-stream")]
		public var TalentCard:Class;
		[Embed(source = 'TalentCard/TalentCardSuit.txt',mimeType = "application/octet-stream")]
		public var TalentCardSuit:Class;
		[Embed(source = 'TalentCard/UnLockTalent.txt',mimeType = "application/octet-stream")]
		public var UnLockTalent:Class;



		[Embed(source = 'CouplesFB/CouBuffInfo.txt',mimeType = "application/octet-stream")]
		public var CouBuffInfo:Class;
		[Embed(source = 'CouplesFB/CouplesEvent.txt',mimeType = "application/octet-stream")]
		public var CouplesEvent:Class;
		[Embed(source = 'CouplesFB/CouplesFB_english.txt',mimeType = "application/octet-stream")]
		public var CouplesFB:Class;
		[Embed(source = 'CouplesFB/CouplesReward.txt',mimeType = "application/octet-stream")]
		public var CouplesReward:Class;
		[Embed(source = 'CouplesFB/LuckyDraw.txt',mimeType = "application/octet-stream")]
		public var LuckyDraw:Class;
		[Embed(source = 'CouplesFB/EventName.txt',mimeType = "application/octet-stream")]
		public var EventName:Class;
		[Embed(source = 'CouplesFB/BuyTimes_english.txt',mimeType = "application/octet-stream")]
		public var BuyTimes:Class;
		[Embed(source = 'CircularActive/CircularActive_english.txt',mimeType = "application/octet-stream")]
		public var CircularActive:Class;

		[Embed(source = 'twelvePalace/twelvePalaceAward.txt',mimeType = "application/octet-stream")]
		public var twelvePalaceAward:Class;


		[Embed(source = 'GVE/GVEFB.txt',mimeType = "application/octet-stream")]
		public var GVEFB:Class;
		[Embed(source = 'GVE/GVEFBReward.txt',mimeType = "application/octet-stream")]
		public var GVEFBReward:Class;
		[Embed(source = 'GVE/GVEZhangJie.txt',mimeType = "application/octet-stream")]
		public var GVEZhangJie:Class;
		[Embed(source = 'GameZoneName.txt',mimeType = "application/octet-stream")]
		public var GameZoneName:Class;

		[Embed(source = 'RMBBank/RMBBankGradeConfig_english.txt',mimeType = "application/octet-stream")]
		public var RMBBankGradeConfig:Class;
		[Embed(source = 'RMBBank/RMBBankRateConfig_english.txt',mimeType = "application/octet-stream")]
		public var RMBBankRateConfig:Class;

		[Embed(source = 'GameUnionLogAward/GameUnionAiwan.txt',mimeType = "application/octet-stream")]
		public var GameUnionAiwan:Class;
		[Embed(source = 'GameUnionLogAward/GameUnionQQGJ.txt',mimeType = "application/octet-stream")]
		public var GameUnionQQGJ:Class;
		[Embed(source = 'GameUnionLogAward/GameUnionAiwanLog.txt',mimeType = "application/octet-stream")]
		public var GameUnionAiwanLog:Class;
		[Embed(source = 'GameUnionLogAward/GameUnionQQGJLog.txt',mimeType = "application/octet-stream")]
		public var GameUnionQQGJLog:Class;

		[Embed(source = 'UniversalBuy/UniversalReward_english.txt',mimeType = "application/octet-stream")]
		public var UniversalReward:Class;
		[Embed(source = 'CircularActive/UniversalBuy_english.txt',mimeType = "application/octet-stream")]
		public var UniversalBuy:Class;
		[Embed(source = 'WishPool/ScoreShopConfig.txt',mimeType = "application/octet-stream")]
		public var ScoreShopConfig:Class;
		[Embed(source = 'WishPool/WishPoolConfig_english.txt',mimeType = "application/octet-stream")]
		public var WishPoolConfig:Class;
		[Embed(source = 'KaifuBoss/KaifuBossMonster_english.txt',mimeType = "application/octet-stream")]
		public var KaifuBossMonster:Class;
		[Embed(source = 'HefuBoss/HefuBossMonster_english.txt',mimeType = "application/octet-stream")]
		public var HefuBossMonster:Class;
		[Embed(source = 'ItemConfig/LibaoInfo_english.txt',mimeType = "application/octet-stream")]
		public var LibaoInfo:Class;
		[Embed(source = 'ItemConfig/EquipmentEnchant.txt',mimeType = "application/octet-stream")]
		public var EquipmentEnchant:Class;
		
		[Embed(source = 'GoldMirror/GoldMirror.txt',mimeType = "application/octet-stream")]
		public var GoldMirror:Class;
		[Embed(source = 'GoldMirror/LevelMapGold.txt',mimeType = "application/octet-stream")]
		public var LevelMapGold:Class;
		[Embed(source = 'GoldMirror/Pickmoney.txt',mimeType = "application/octet-stream")]
		public var Pickmoney:Class;
		[Embed(source = 'GoldMirror/Pickmoneymax.txt',mimeType = "application/octet-stream")]
		public var Pickmoneymax:Class;
		[Embed(source = 'GoldMirror/GoldDropLimit.txt',mimeType = "application/octet-stream")]
		public var GoldDropLimit:Class;

		
		[Embed(source = 'BraveHero/BraveHeroBoss.txt',mimeType = "application/octet-stream")]
		public var BraveHeroBoss:Class;
		[Embed(source = 'BraveHero/BraveHeroBuy_english.txt',mimeType = "application/octet-stream")]
		public var BraveHeroBuy:Class;
		[Embed(source = 'BraveHero/BraveHeroRank_english.txt',mimeType = "application/octet-stream")]
		public var BraveHeroRank:Class;
		[Embed(source = 'BraveHero/BraveHeroScore.txt',mimeType = "application/octet-stream")]
		public var BraveHeroScore:Class;
		[Embed(source = 'BraveHero/BraveHeroShop_english.txt',mimeType = "application/octet-stream")]
		public var BraveHeroShop:Class;

		
		[Embed(source = 'GoldChest/GoldChest_english.txt',mimeType = "application/octet-stream")]
		public var GoldChest:Class;
		[Embed(source = 'GoldChest/GoldChestCost.txt',mimeType = "application/octet-stream")]
		public var GoldChestCost:Class;
		[Embed(source = 'StaryMerchant/StrayMerchant_english.txt',mimeType = "application/octet-stream")]
		public var StrayMerchant:Class;
		[Embed(source = 'StaryMerchant/StrayRefresh_english.txt',mimeType = "application/octet-stream")]
		public var StrayRefresh:Class;
		
		[Embed(source = 'DailySeckill/dailyseckill_english.txt',mimeType = "application/octet-stream")]
		public var dailyseckill:Class;
		[Embed(source = 'DailySeckill/worldlevelsection_english.txt',mimeType = "application/octet-stream")]
		public var worldlevelsection:Class;
		
		[Embed(source = 'SuperDiscount/DiscountLiBao_english.txt',mimeType = "application/octet-stream")]
		public var DiscountLiBao:Class;
		
		[Embed(source = 'CircularActive/BraveHeroActive_english.txt',mimeType = "application/octet-stream")]
		public var BraveHeroActive:Class;

		[Embed(source = 'backGift/backGift.txt',mimeType = "application/octet-stream")]
		public var backGift:Class;
		
		[Embed(source = 'WildBoss/WildBossTime.txt',mimeType = "application/octet-stream")]
		public var WildBossTime:Class;
		[Embed(source = 'WildBoss/WildBossAward.txt',mimeType = "application/octet-stream")]
		public var WildBossAward:Class;
		[Embed(source = 'Fashion/Fashion_english.txt',mimeType = "application/octet-stream")]
		public var Fashion:Class;
		[Embed(source = 'Fashion/FashionStar.txt',mimeType = "application/octet-stream")]
		public var FashionStar:Class;
		[Embed(source = 'Fashion/FashionUp.txt',mimeType = "application/octet-stream")]
		public var FashionUp:Class;
		[Embed(source = 'Fashion/FashionWardrobe.txt',mimeType = "application/octet-stream")]
		public var FashionWardrobe:Class;
		[Embed(source = 'Fashion/FashionGorgeous.txt',mimeType = "application/octet-stream")]
		public var FashionGorgeous:Class;
		
		[Embed(source = 'AutumnFestival/AFDailyLiBao.txt',mimeType = "application/octet-stream")]
		public var AFDailyLiBao:Class;
		[Embed(source = 'AutumnFestival/AFExtraLattery.txt',mimeType = "application/octet-stream")]
		public var AFExtraLattery:Class;
		[Embed(source = 'AutumnFestival/AFLatteryReward.txt',mimeType = "application/octet-stream")]
		public var AFLatteryReward:Class;
	
				
		[Embed(source = 'LimitChest/LimitChest.txt',mimeType = "application/octet-stream")]
		public var LimitChest:Class;
		[Embed(source = 'Fashion/FashionSuit_english.txt',mimeType = "application/octet-stream")]
		public var FashionSuit:Class;
		
		[Embed(source = 'DragonTrain/DragonTrainBase.txt',mimeType = "application/octet-stream")]
		public var DragonTrainBase:Class;
		[Embed(source = 'DragonTrain/DragonEquipment.txt',mimeType = "application/octet-stream")]
		public var DragonEquipment:Class;
		[Embed(source = 'DragonTrain/DragonCollectSoul_english.txt',mimeType = "application/octet-stream")]
		public var DragonCollectSoul:Class;
		[Embed(source = 'DragonTrain/DragonBallBase.txt',mimeType = "application/octet-stream")]
		public var DragonBallBase:Class;
		
		
		
		[Embed(source = 'QQHZGift/QQHZGiftOGLiBao.txt',mimeType = "application/octet-stream")]
		public var QQHZGiftOGLiBao:Class;
		[Embed(source = 'QQHZGift/QQHZGiftRGLiBao.txt',mimeType = "application/octet-stream")]
		public var QQHZGiftRGLiBao:Class;
		[Embed(source = 'Fashion/body.txt',mimeType = "application/octet-stream")]
		public var body:Class;
		[Embed(source = 'Fashion/hair.txt',mimeType = "application/octet-stream")]
		public var hair:Class;
		[Embed(source = 'Fashion/weapon.txt',mimeType = "application/octet-stream")]
		public var weapon:Class;
		[Embed(source = 'SeaXunbao/SeaXunbao_english.txt',mimeType = "application/octet-stream")]
		public var SeaXunbao:Class;

		[Embed(source = 'TeamTower/TeamTower.txt',mimeType = "application/octet-stream")]
		public var TeamTower:Class;
		[Embed(source = 'TeamTower/TeamTowerLayer.txt',mimeType = "application/octet-stream")]
		public var TeamTowerLayer:Class;
		[Embed(source = 'TeamTower/TeamTowerReward.txt',mimeType = "application/octet-stream")]
		public var TeamTowerReward:Class;
		[Embed(source = 'Fashion/FashionWing.txt',mimeType = "application/octet-stream")]
		public var FashionWing:Class;
		[Embed(source = 'WeekReward3366/WR3366Rewards.txt',mimeType = "application/octet-stream")]
		public var WR3366Rewards:Class;
		[Embed(source = 'Fashion/FashionSell.txt',mimeType = "application/octet-stream")]
		public var FashionSell:Class;
		[Embed(source = 'StarGirl/SuperDivine.txt',mimeType = "application/octet-stream")]
		public var SuperDivine:Class;
		[Embed(source = 'StarGirl/StarGirlBase.txt',mimeType = "application/octet-stream")]
		public var StarGirlBase:Class;
		[Embed(source = 'StarGirl/StarGirlLevel.txt',mimeType = "application/octet-stream")]
		public var StarGirlLevel:Class;
		[Embed(source = 'StarGirl/LevelUpCrit.txt',mimeType = "application/octet-stream")]
		public var LevelUpCrit:Class;
		[Embed(source = 'StarGirl/StarLevel.txt',mimeType = "application/octet-stream")]
		public var StarLevel:Class;
		[Embed(source = 'StarGirl/PowerProperty.txt',mimeType = "application/octet-stream")]
		public var PowerProperty:Class;
		[Embed(source = 'StarGirl/BuyLoveCnt.txt',mimeType = "application/octet-stream")]
		public var BuyLoveCnt:Class;
		[Embed(source = 'StarGirl/PowerConsume.txt',mimeType = "application/octet-stream")]
		public var PowerConsume:Class;
		[Embed(source = 'StarGirl/InheritConsume.txt',mimeType = "application/octet-stream")]
		public var InheritConsume:Class;
		[Embed(source = 'StarGirl/SealBase.txt',mimeType = "application/octet-stream")]
		public var SealBase:Class;
		[Embed(source = 'StarGirl/SealLevel.txt',mimeType = "application/octet-stream")]
		public var SealLevel:Class;
		[Embed(source = 'StarGirl/StarGirlItem.txt',mimeType = "application/octet-stream")]
		public var StarGirlItem:Class;
		
		[Embed(source = 'KaiFuAct/KaiFuActBase.txt',mimeType = "application/octet-stream")]
		public var KaiFuActBase:Class;
		[Embed(source = 'KaiFuAct/KaiFuActReward.txt',mimeType = "application/octet-stream")]
		public var KaiFuActReward:Class;
		
		[Embed(source = 'NationDay/DailyLiBao.txt',mimeType = "application/octet-stream")]
		public var DailyLiBao:Class;		
		[Embed(source = 'NationDay/ExchangeReward.txt',mimeType = "application/octet-stream")]
		public var ExchangeReward:Class;
		[Embed(source = 'NationDay/StrikeBossIndex.txt',mimeType = "application/octet-stream")]
		public var StrikeBossIndex:Class;
		[Embed(source = 'NationDay/NationFBKillReward.txt',mimeType = "application/octet-stream")]
		public var NationFBKillReward:Class;
		[Embed(source = 'NationDay/NationFBReward.txt',mimeType = "application/octet-stream")]
		public var NationFBReward:Class;
		[Embed(source = 'NationDay/StrikeBossShow.txt',mimeType = "application/octet-stream")]
		public var StrikeBossShow:Class;
		
		[Embed(source = 'LuckyBag/LuckBag.txt',mimeType = "application/octet-stream")]
		public var LuckBag:Class;
		
		[Embed(source = 'FindBack/FindBack_english.txt',mimeType = "application/octet-stream")]
		public var FindBack:Class;
		[Embed(source = 'FindBack/FindBackPercent_VIP.txt',mimeType = "application/octet-stream")]
		public var FindBackPercent_VIP:Class;
		[Embed(source = 'FindBack/FindBackReward_RMB.txt',mimeType = "application/octet-stream")]
		public var FindBackReward_RMB:Class;
		[Embed(source = 'FindBack/FindBackReward_Time.txt',mimeType = "application/octet-stream")]
		public var FindBackReward_Time:Class;
		[Embed(source = 'FindBack/FindBackReward_BindRMB.txt',mimeType = "application/octet-stream")]
		public var FindBackReward_BindRMB:Class;
		[Embed(source = 'FindBack/FindBackFB.txt',mimeType = "application/octet-stream")]
		public var FindBackFB:Class;
		[Embed(source = 'FindBack/FindBackHT.txt',mimeType = "application/octet-stream")]
		public var FindBackHT:Class;
		[Embed(source = 'FindBack/FindBackReward_Money.txt',mimeType = "application/octet-stream")]
		public var FindBackReward_Money:Class;
		[Embed(source = 'FindBack/FindBackNeedMoney.txt',mimeType = "application/octet-stream")]
		public var FindBackNeedMoney:Class;
		
		[Embed(source = 'QQMiniClient/DayReward.txt',mimeType = "application/octet-stream")]
		public var DayReward:Class;
		[Embed(source = 'QQMiniClient/Start.txt',mimeType = "application/octet-stream")]
		public var Start:Class;
		[Embed(source = 'QQMiniClient/ReadyStart.txt',mimeType = "application/octet-stream")]
		public var ReadyStart:Class;
		
		
		[Embed(source = 'SevenAct/SevenActBase.txt',mimeType = "application/octet-stream")]
		public var SevenActBase:Class;
		[Embed(source = 'SevenAct/SevenActReward.txt',mimeType = "application/octet-stream")]
		public var SevenActReward:Class;
		
		//高级技能
		[Embed(source = 'StudySkill/SuperSkillLevelup.txt',mimeType = "application/octet-stream")]
		public var SuperSkillLevelup:Class;
		[Embed(source = 'Shop/LingShiShop.txt',mimeType = "application/octet-stream")]
		public var LingShiShop:Class;
		
		[Embed(source = 'CollectLongyin/CollectBuqian_english.txt',mimeType = "application/octet-stream")]
		public var CollectBuqian:Class;
		[Embed(source = 'CollectLongyin/CollectLongReward_english.txt',mimeType = "application/octet-stream")]
		public var CollectLongReward:Class;
		[Embed(source = 'CollectLongyin/CollectLongyinActive.txt',mimeType = "application/octet-stream")]
		public var CollectLongyinActive:Class;
		[Embed(source = 'CollectLongyin/CollectLongyinRmbReward_english.txt',mimeType = "application/octet-stream")]
		public var CollectLongyinRmbReward:Class;
		[Embed(source = 'CollectLongyin/SignReward.txt',mimeType = "application/octet-stream")]
		public var SignReward:Class;
		
		[Embed(source = 'HalloweenAct/KillGhost_english.txt',mimeType = "application/octet-stream")]
		public var KillGhost:Class;
		[Embed(source = 'HalloweenAct/OpenLight_english.txt',mimeType = "application/octet-stream")]
		public var OpenLight:Class;
		[Embed(source = 'HalloweenAct/HalloweenTask.txt',mimeType = "application/octet-stream")]
		public var HalloweenTask:Class;
		[Embed(source = 'HalloweenAct/CollectCard_english.txt',mimeType = "application/octet-stream")]
		public var CollectCard:Class;
		[Embed(source = 'HalloweenAct/CardBuff.txt',mimeType = "application/octet-stream")]
		public var CardBuff:Class;
		
		[Embed(source = 'DragonTrain/DragonVeinBase.txt',mimeType = "application/octet-stream")]
		public var DragonVeinBase:Class;
		[Embed(source = 'DragonTrain/DragonVeinGrade.txt',mimeType = "application/octet-stream")]
		public var DragonVeinGrade:Class;
		[Embed(source = 'DragonTrain/DragonVeinLevel.txt',mimeType = "application/octet-stream")]
		public var DragonVeinLevel:Class;
		[Embed(source = 'DragonTrain/DragonVeinBuff.txt',mimeType = "application/octet-stream")]
		public var DragonVeinBuff:Class;
		
		
		[Embed(source = 'HunluanSpace/HunluanSpacePersonRank.txt',mimeType = "application/octet-stream")]
		public var HunluanSpacePersonRank:Class;
		[Embed(source = 'HunluanSpace/HunluanSpaceUnionRank.txt',mimeType = "application/octet-stream")]
		public var HunluanSpaceUnionRank:Class;
		[Embed(source = 'HunluanSpace/HunluanSpaceUnionScore.txt',mimeType = "application/octet-stream")]
		public var HunluanSpaceUnionScore:Class;
		
		[Embed(source = 'BlessRoulette/BlessRouletteReward.txt',mimeType = "application/octet-stream")]
		public var BlessRouletteReward:Class;
		[Embed(source = 'Haoqi/HaoqiLocalRank.txt',mimeType = "application/octet-stream")]
		public var HaoqiLocalRank:Class;
		[Embed(source = 'Haoqi/HaoqiRank.txt',mimeType = "application/octet-stream")]
		public var HaoqiRank:Class;
		[Embed(source = 'Haoqi/HaoqiRMBReward.txt',mimeType = "application/octet-stream")]
		public var HaoqiRMBReward:Class;
		[Embed(source = 'CircularActive/HaoqiActive.txt',mimeType = "application/octet-stream")]
		public var HaoqiActive:Class;
		[Embed(source = 'GroupBuyCarnival/GroupBuyCarnival.txt',mimeType = "application/octet-stream")]
		public var GroupBuyCarnival:Class;
		[Embed(source = 'GroupBuyCarnival/GroupBuyCarnivalReward.txt',mimeType = "application/octet-stream")]
		public var GroupBuyCarnivalReward:Class;
		
		[Embed(source = 'HalloweenNA/HalloweenNABase.txt',mimeType = "application/octet-stream")]
		public var HalloweenNABase:Class;
		[Embed(source = 'HalloweenNA/HalloweenNAReward.txt',mimeType = "application/octet-stream")]
		public var HalloweenNAReward:Class;
		[Embed(source = 'DailyMountLottery/DailyMountLottery_english.txt',mimeType = "application/octet-stream")]
		public var DailyMountLottery:Class;
		
		[Embed(source = 'QQLZ/QQLZKaiTongReward.txt',mimeType = "application/octet-stream")]
		public var QQLZKaiTongReward:Class;
		[Embed(source = 'QQLZ/QQLZGiftOGLiBao.txt',mimeType = "application/octet-stream")]
		public var QQLZGiftOGLiBao:Class;
		
		
		[Embed(source = 'QQHallLottery/QQHallLotteryTimes_english.txt',mimeType = "application/octet-stream")]
		public var QQHallLotteryTimes:Class;
		[Embed(source = 'QQHallLottery/QQHallLotteryReward.txt',mimeType = "application/octet-stream")]
		public var QQHallLotteryReward:Class;
		[Embed(source = 'JT/jtmedal.txt',mimeType = "application/octet-stream")]
		public var jtmedal:Class;
		[Embed(source = 'JT/jtstore.txt',mimeType = "application/octet-stream")]
		public var jtstore:Class;
		[Embed(source = 'JT/jtmonthreward.txt',mimeType = "application/octet-stream")]
		public var jtmonthreward:Class;
		[Embed(source = 'JT/jtdayreward.txt',mimeType = "application/octet-stream")]
		public var jtdayreward:Class;
		[Embed(source = 'JT/jtstoreRefresh.txt',mimeType = "application/octet-stream")]
		public var jtstoreRefresh:Class;
		
		[Embed(source = 'DoubleEleven/SeckillBase.txt',mimeType = "application/octet-stream")]
		public var SeckillBase:Class;
		[Embed(source = 'DoubleEleven/SeckillItem.txt',mimeType = "application/octet-stream")]
		public var SeckillItem:Class;
		[Embed(source = 'DoubleElevenShop/DoubleElevenShop.txt',mimeType = "application/octet-stream")]
		public var DoubleElevenShop:Class;
		[Embed(source = 'PetLuckyFarm/petluckyfarm_english.txt',mimeType = "application/octet-stream")]
		public var petluckyfarm:Class;
		[Embed(source = 'PetLuckyFarm/rewardconfig_english.txt',mimeType = "application/octet-stream")]
		public var rewardconfig:Class;
		
		[Embed(source = 'TimeLimitGoods/TimeLimitGoods.txt',mimeType = "application/octet-stream")]
		public var TimeLimitGoods:Class;
		[Embed(source = 'TimeLimitGoods/TimeLimitIcon.txt',mimeType = "application/octet-stream")]
		public var TimeLimitIcon:Class;
		[Embed(source = 'DragonStele/DragonSteleReward_english.txt',mimeType = "application/octet-stream")]
		public var DragonSteleReward:Class;
		[Embed(source = 'GodsTreasure/GodsTreasureBase_english.txt',mimeType = "application/octet-stream")]
		public var GodsTreasureBase:Class;
		[Embed(source = 'GodsTreasure/GodsTreasureReward_english.txt',mimeType = "application/octet-stream")]
		public var GodsTreasureReward:Class;
		[Embed(source = 'Wing/WingEvolve.txt',mimeType = "application/octet-stream")]
		public var WingEvolve:Class;
		
		[Embed(source = 'StepByStep/stepbystep.txt',mimeType = "application/octet-stream")]
		public var stepbystep:Class;
		
		[Embed(source = 'DragonHole/DragonHoleConfig.txt',mimeType = "application/octet-stream")]
		public var DragonHoleConfig:Class;
		[Embed(source = 'ThanksGiving/CutTurkeyQ.txt',mimeType = "application/octet-stream")]
		public var CutTurkeyQ:Class;
		[Embed(source = 'ThanksGiving/CutTurkeyAward.txt',mimeType = "application/octet-stream")]
		public var CutTurkeyAward:Class;
		
		
		
		[Embed(source = 'DragonTrain/DragonEquipmentUpgrade.txt',mimeType = "application/octet-stream")]
		public var DragonEquipmentUpgrade:Class;
		
		[Embed(source = 'ThanksGiving/RechargeRewardItems.txt',mimeType = "application/octet-stream")]
		public var RechargeRewardItems:Class;
		[Embed(source = 'ThanksGiving/RechargeRewardTimes.txt',mimeType = "application/octet-stream")]
		public var RechargeRewardTimes:Class;
		[Embed(source = 'ThanksGiving/OnlineReward.txt',mimeType = "application/octet-stream")]
		public var OnlineReward:Class;
		
		[Embed(source = 'JTGroup/jtgroupreward.txt',mimeType = "application/octet-stream")]
		public var jtgroupreward:Class;
		
		[Embed(source = 'Zuma/ZumaBase.txt',mimeType = "application/octet-stream")]
		public var ZumaBase:Class;
		
		[Embed(source = 'Zuma/ZumaScoreReward_english.txt',mimeType = "application/octet-stream")]
		public var ZumaScoreReward:Class;
		
		[Embed(source = 'Zuma/ZumaCollect.txt',mimeType = "application/octet-stream")]
		public var ZumaCollect:Class;
		[Embed(source = 'Zuma/ZumaRoleRankReward.txt',mimeType = "application/octet-stream")]
		public var ZumaRankGift:Class;
		[Embed(source = 'Zuma/ZumaKFRankGift.txt',mimeType = "application/octet-stream")]
		public var ZumaKFRankGift:Class;
		[Embed(source = 'Zuma/ZumaScore.txt',mimeType = "application/octet-stream")]
		public var ZumaScore:Class;
		
		
		[Embed(source = 'DoubleTwelve/FWLotteryReward.txt',mimeType = "application/octet-stream")]
		public var FWLotteryReward:Class;
		[Embed(source = 'DoubleTwelve/FWRechargeReward_english.txt',mimeType = "application/octet-stream")]
		public var FWRechargeReward:Class;
		[Embed(source = 'DoubleTwelve/LTOnlineReward.txt',mimeType = "application/octet-stream")]
		public var LTOnlineReward:Class;
		[Embed(source = 'DoubleTwelve/LCLotteryCost.txt',mimeType = "application/octet-stream")]
		public var LCLotteryCost:Class;
		[Embed(source = 'DoubleTwelve/LCLotteryReward_english.txt',mimeType = "application/octet-stream")]
		public var LCLotteryReward:Class;
		[Embed(source = 'DoubleTwelve/LCResetTimesCost_english.txt',mimeType = "application/octet-stream")]
		public var LCResetTimesCost:Class;
		[Embed(source = 'KaifuTarget/KaifuTarget_english.txt',mimeType = "application/octet-stream")]
		public var KaifuTarget:Class;
		[Embed(source = 'KaifuTarget/KaifuTargetAct.txt',mimeType = "application/octet-stream")]
		public var KaifuTargetAct:Class;
		[Embed(source = 'KaifuTarget/KaifuTargetRank_english.txt',mimeType = "application/octet-stream")]
		public var KaifuTargetRank:Class;
		[Embed(source = 'KaifuTarget/NewKaifuTarget.txt',mimeType = "application/octet-stream")]
		public var NewKaifuTarget:Class;
		[Embed(source = 'KaifuTarget/NewKaifuTargetAct.txt',mimeType = "application/octet-stream")]
		public var NewKaifuTargetAct:Class;
		[Embed(source = 'KaifuTarget/NewKaifuTargetRank.txt',mimeType = "application/octet-stream")]
		public var NewKaifuTargetRank:Class;

		[Embed(source = 'DoubleTwelve/GroupBuyPartyGood_english.txt',mimeType = "application/octet-stream")]
		public var GroupBuyPartyGood:Class;
		[Embed(source = 'DoubleTwelve/GroupBuyPartyReward.txt',mimeType = "application/octet-stream")]
		public var GroupBuyPartyReward:Class;
		[Embed(source = 'DoubleTwelve/Rebate.txt',mimeType = "application/octet-stream")]
		public var Rebate:Class;
		[Embed(source = 'DoubleTwelve/richRankAward_english.txt',mimeType = "application/octet-stream")]
		public var richRankAward:Class;
		
		[Embed(source = 'Shop/UStypeShop.txt',mimeType = "application/octet-stream")]
		public var UStypeShop:Class;
		[Embed(source = 'CircularActive/RichRankActive_english.txt',mimeType = "application/octet-stream")]
		public var RichRankActive:Class;
		
		[Embed(source = 'QQLZ/QQLZLuxuryGiftReward.txt',mimeType = "application/octet-stream")]
		public var QQLZLuxuryGiftReward:Class;	
		[Embed(source = 'DragonTreasure/BuyDigCost_english.txt',mimeType = "application/octet-stream")]
		public var BuyDigCost:Class;	

		[Embed(source = 'Christmas/ChristmasHaoARank_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasHaoARank:Class;
		[Embed(source = 'Christmas/ChristmasHaoReward.txt',mimeType = "application/octet-stream")]
		public var ChristmasHaoReward:Class;
		[Embed(source = 'Christmas/ChristmasShop_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasShop:Class;
		[Embed(source = 'Christmas/ChristmasFashionShowGoods_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasFashionShowGoods:Class;
		[Embed(source = 'Christmas/ChristmasFashionShowSuit_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasFashionShowSuit:Class;
		[Embed(source = 'CircularActive/ChristmasHaoActive_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasHaoActive:Class;		
		
		[Embed(source = 'TimeLimitSupply/TimeLimitSupply.txt',mimeType = "application/octet-stream")]
		public var TimeLimitSupply:Class;
		[Embed(source = 'Fashion/FashionHole.txt',mimeType = "application/octet-stream")]
		public var FashionHole:Class;
		
		
		[Embed(source = 'Christmas/ChristmasWingLotteryReward_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasWingLotteryReward:Class;
		[Embed(source = 'Christmas/ChristmasWishTreeGoods_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasWishTreeGoods:Class;
		[Embed(source = 'Christmas/ChristmasWishTreeRefresh.txt',mimeType = "application/octet-stream")]
		public var ChristmasWishTreeRefresh:Class;
		[Embed(source = 'Christmas/ChristmasWishTreeDiscountPreview_english.txt',mimeType = "application/octet-stream")]
		public var ChristmasWishTreeDiscountPreview:Class;
		[Embed(source = 'Christmas/ChristmasMountLotteryReward.txt',mimeType = "application/octet-stream")]
		public var ChristmasMountLotteryReward:Class;
		[Embed(source = 'ItemConfig/EquipmentWashMaxPro.txt',mimeType = "application/octet-stream")]
		public var EquipmentWashMaxPro:Class;
		[Embed(source = 'ItemConfig/EquipmentWashBase.txt',mimeType = "application/octet-stream")]
		public var EquipmentWashBase:Class;
		[Embed(source = 'ItemConfig/EquipmentUnlockCost_english.txt',mimeType = "application/octet-stream")]
		public var EquipmentUnlockCost:Class;
		
		//元旦活动
		[Embed(source = 'Holiday/HolidayLotteryReward_english.txt',mimeType = "application/octet-stream")]
		public var HolidayLotteryReward:Class;
		[Embed(source = 'Holiday/HolidayMoneyWish_english.txt',mimeType = "application/octet-stream")]
		public var HolidayMoneyWish:Class;
		[Embed(source = 'Holiday/HolidayOnlineReward_english.txt',mimeType = "application/octet-stream")]
		public var HolidayOnlineReward:Class;
		[Embed(source = 'Holiday/HolidayRechargeReward_english.txt',mimeType = "application/octet-stream")]
		public var HolidayRechargeReward:Class;
		[Embed(source = 'Holiday/HolidayShoppingFestival_english.txt',mimeType = "application/octet-stream")]
		public var HolidayShoppingFestival:Class;
		[Embed(source = 'Holiday/HolidayShoppingScore_english.txt',mimeType = "application/octet-stream")]
		public var HolidayShoppingScore:Class;
		[Embed(source = 'ItemConfig/EquipmentWashStar.txt',mimeType = "application/octet-stream")]
		public var EquipmentWashStar:Class;
		[Embed(source = 'JTGroup/jtallreward.txt',mimeType = "application/octet-stream")]
		public var jtallreward:Class;
		[Embed(source = 'QQLZ/QQLZLuxuryRollReward.txt',mimeType = "application/octet-stream")]
		public var QQLZLuxuryRollReward:Class;
				
		[Embed(source = 'QQHK/QQHK.txt',mimeType = "application/octet-stream")]
		public var QQHK:Class;
		
		[Embed(source = 'DailyFB/DailyFBBase.txt',mimeType = "application/octet-stream")]
		public var DailyFBBase:Class;
		
		[Embed(source = 'DailyFB/DailyFBPassReward.txt',mimeType = "application/octet-stream")]
		public var DailyFBPassReward:Class;
		
		[Embed(source = 'DailyFB/DailyFBFight.txt',mimeType = "application/octet-stream")]
		public var DailyFBFight:Class;
		
		
		[Embed(source = 'HappyNewYear/NewYearDiscountConfig.txt',mimeType = "application/octet-stream")]
		public var NewYearDiscountConfig:Class;
		[Embed(source = 'HappyNewYear/NewYearHaoARank.txt',mimeType = "application/octet-stream")]
		public var NewYearHaoARank:Class;
		[Embed(source = 'HappyNewYear/NewYearHaoLRank.txt',mimeType = "application/octet-stream")]
		public var NewYearHaoLRank:Class;
		[Embed(source = 'HappyNewYear/NewYearHaoReward.txt',mimeType = "application/octet-stream")]
		public var NewYearHaoReward:Class;
		[Embed(source = 'HappyNewYear/NewYearShop.txt',mimeType = "application/octet-stream")]
		public var NewYearShop:Class;
		[Embed(source = 'HappyNewYear/NYearDiscountFresh.txt',mimeType = "application/octet-stream")]
		public var NYearDiscountFresh:Class;
		[Embed(source = 'HappyNewYear/NYearOnlineFreeTimes.txt',mimeType = "application/octet-stream")]
		public var NYearOnlineFreeTimes:Class;
		[Embed(source = 'HappyNewYear/NYearOnlineReward.txt',mimeType = "application/octet-stream")]
		public var NYearOnlineReward:Class;
		[Embed(source = 'HappyNewYear/NewYearDiscountDiscountPreview.txt',mimeType = "application/octet-stream")]
		public var NewYearDiscountDiscountPreview:Class;
		[Embed(source = 'HappyNewYear/NewYearDiscountGetWay.txt',mimeType = "application/octet-stream")]
		public var NewYearDiscountGetWay:Class;
		[Embed(source = 'CircularActive/NewYearHaoActive.txt',mimeType = "application/octet-stream")]
		public var NewYearHaoActive:Class;
		
		
		[Embed(source = 'GoddessCard/GoddessCardReward_english.txt',mimeType = "application/octet-stream")]
		public var GoddessCardReward:Class;
		[Embed(source = 'GoddessCard/GoddessGroupReward.txt',mimeType = "application/octet-stream")]
		public var GoddessGroupReward:Class;
		[Embed(source = 'GoddessCard/GoddessTreasureReward.txt',mimeType = "application/octet-stream")]
		public var GoddessTreasureReward:Class;
		[Embed(source = 'GoddessCard/GoddessTreasureBase.txt',mimeType = "application/octet-stream")]
		public var GoddessTreasureBase:Class;
		
		
		[Embed(source = 'QQHZ/QQHZRollExchange.txt',mimeType = "application/octet-stream")]
		public var QQHZRollExchange:Class;
		[Embed(source = 'QQHZ/QQHZRollReward.txt',mimeType = "application/octet-stream")]
		public var QQHZRollReward:Class;
		
		[Embed(source = 'QQLZ/QQLZRollReward.txt',mimeType = "application/octet-stream")]
		public var QQLZRollReward:Class;
		[Embed(source = 'QQLZ/QQLZRollExchange.txt',mimeType = "application/octet-stream")]
		public var QQLZRollExchange:Class;
		
		
		[Embed(source = 'SevenDayHegemony/SDHTarget.txt',mimeType = "application/octet-stream")]
		public var SDHTarget:Class;
		[Embed(source = 'SevenDayHegemony/SDHAct.txt',mimeType = "application/octet-stream")]
		public var SDHAct:Class;
		[Embed(source = 'SevenDayHegemony/SDHRank.txt',mimeType = "application/octet-stream")]
		public var SDHRank:Class;
		[Embed(source = 'WildBoss/WildBossScore.txt',mimeType = "application/octet-stream")]
		public var WildBossScore:Class;
		[Embed(source = 'WildBoss/WildBossStatus.txt',mimeType = "application/octet-stream")]
		public var WildBossStatus:Class;
		[Embed(source = 'DragonKnightChallenge/DragonKnightChallengeBase.txt',mimeType = "application/octet-stream")]
		public var DragonKnightChallengeBase:Class;
		[Embed(source = 'JJC/JJCRankToGroup.txt',mimeType = "application/octet-stream")]
		public var JJCRankToGroup:Class;
		[Embed(source = 'WildBoss/WildBossScene.txt',mimeType = "application/octet-stream")]
		public var WildBossScene:Class;
		
		[Embed(source = 'XinYueVIP/XinYuelReward.txt',mimeType = "application/octet-stream")]
		public var XinYuelReward:Class;
		[Embed(source = 'XinYueVIP/XinYueRoleLevelReward.txt',mimeType = "application/octet-stream")]
		public var XinYueRoleLevelReward:Class;
		
		[Embed(source = 'ItemConfig/crystal.txt',mimeType = "application/octet-stream")]
		public var crystal:Class;
		[Embed(source = 'ItemConfig/crystalSealing.txt',mimeType = "application/octet-stream")]
		public var crystalSealing:Class;
		[Embed(source = 'KuaFuJJC/KuaFuJJCBuyCnt_english.txt',mimeType = "application/octet-stream")]
		public var KuaFuJJCBuyCnt:Class;
		[Embed(source = 'KuaFuJJC/KuaFuJJCGroup.txt',mimeType = "application/octet-stream")]
		public var KuaFuJJCGroup:Class;
		
		[Embed(source = 'OpenYear/Consum.txt',mimeType = "application/octet-stream")]
		public var Consum:Class;
		[Embed(source = 'OpenYear/ContinueLogin.txt',mimeType = "application/octet-stream")]
		public var ContinueLogin:Class;
		[Embed(source = 'OpenYear/TotalLogin.txt',mimeType = "application/octet-stream")]
		public var TotalLogin:Class;
		[Embed(source = 'OpenYear/ClientTitleDesc.txt',mimeType = "application/octet-stream")]
		public var ClientTitleDesc:Class;
		
		
		[Embed(source = 'SpringFestival/GodWealth.txt',mimeType = "application/octet-stream")]
		public var GodWealth:Class;
		[Embed(source = 'SpringFestival/NianComingExchange.txt',mimeType = "application/octet-stream")]
		public var NianComingExchange:Class;
		[Embed(source = 'SpringFestival/NianComingReward.txt',mimeType = "application/octet-stream")]
		public var NianComingReward:Class;
		[Embed(source = 'SpringFestival/NianComingTimes.txt',mimeType = "application/octet-stream")]
		public var NianComingTimes:Class;
		[Embed(source = 'SpringFestival/RedEnvelope.txt',mimeType = "application/octet-stream")]
		public var RedEnvelope:Class;
		[Embed(source = 'SpringFestival/RedEnvelopeReward.txt',mimeType = "application/octet-stream")]
		public var RedEnvelopeReward:Class;
		[Embed(source = 'SpringFestival/SpringBLRank.txt',mimeType = "application/octet-stream")]
		public var SpringBLRank:Class;
		[Embed(source = 'SpringFestival/SpringBReward.txt',mimeType = "application/octet-stream")]
		public var SpringBReward:Class;
		[Embed(source = 'SpringFestival/SpringBServerType.txt',mimeType = "application/octet-stream")]
		public var SpringBServerType:Class;
		[Embed(source = 'SpringFestival/SpringFDiscountConfig.txt',mimeType = "application/octet-stream")]
		public var SpringFDiscountConfig:Class;
		[Embed(source = 'SpringFestival/SpringFDiscountFresh.txt',mimeType = "application/octet-stream")]
		public var SpringFDiscountFresh:Class;
		[Embed(source = 'SpringFestival/SpringShop.txt',mimeType = "application/octet-stream")]
		public var SpringShop:Class;
		[Embed(source = 'SpringFestival/SprintBARank.txt',mimeType = "application/octet-stream")]
		public var SprintBARank:Class;
		[Embed(source = 'SpringFestival/SpringFDDiscountPreview.txt',mimeType = "application/octet-stream")]
		public var SpringFDDiscountPreview:Class;
		
		
		[Embed(source = 'RMBComing/RMBComing.txt',mimeType = "application/octet-stream")]
		public var RMBComing:Class;
		[Embed(source = 'RMBComing/RMBComingReward.txt',mimeType = "application/octet-stream")]
		public var RMBComingReward:Class;
		
		
		[Embed(source = 'ValentineDay/RosePresentBase.txt',mimeType = "application/octet-stream")]
		public var RosePresentBase:Class;
		[Embed(source = 'ValentineDay/RoseRebate.txt',mimeType = "application/octet-stream")]
		public var RoseRebate:Class;
		[Embed(source = 'ValentineDay/GlamourParty.txt',mimeType = "application/octet-stream")]
		public var GlamourParty:Class;
		[Embed(source = 'ValentineDay/GlamourPartyTarget.txt',mimeType = "application/octet-stream")]
		public var GlamourPartyTarget:Class;
		[Embed(source = 'ValentineDay/GlamourCoinExchange.txt',mimeType = "application/octet-stream")]
		public var GlamourCoinExchange:Class;
		[Embed(source = 'ValentineDay/CouplesGoal.txt',mimeType = "application/octet-stream")]
		public var CouplesGoal:Class;
		[Embed(source = 'ValentineDay/CouplesFashionShop.txt',mimeType = "application/octet-stream")]
		public var CouplesFashionShop:Class;
		[Embed(source = 'ValentineDay/GlamourKuaFuRank.txt',mimeType = "application/octet-stream")]
		public var GlamourKuaFuRank:Class;
		[Embed(source = 'ValentineDay/GlamourLocalRank.txt',mimeType = "application/octet-stream")]
		public var GlamourLocalRank:Class;
		[Embed(source = 'ValentineDay/GlamourRankConsolationReward.txt',mimeType = "application/octet-stream")]
		public var GlamourRankConsolationReward:Class;

		
		[Embed(source = 'LanternFestival/LanternCrossRank_english.txt',mimeType = "application/octet-stream")]
		public var LanternCrossRank:Class;
		[Embed(source = 'LanternFestival/LanternHappnessFestival_english.txt',mimeType = "application/octet-stream")]
		public var LanternHappnessFestival:Class;
		[Embed(source = 'LanternFestival/LanternLocalRank.txt',mimeType = "application/octet-stream")]
		public var LanternLocalRank:Class;
		[Embed(source = 'LanternFestival/LanternExtended.txt',mimeType = "application/octet-stream")]
		public var LanternExtended:Class;
		[Embed(source = 'LanternFestival/LanternRebate.txt',mimeType = "application/octet-stream")]
		public var LanternRebate:Class;
		[Embed(source = 'LanternFestival/LanternRebateActive_english.txt',mimeType = "application/octet-stream")]
		public var LanternRebateActive:Class;
		[Embed(source = 'LanternFestival/LanternServerType.txt',mimeType = "application/octet-stream")]
		public var LanternServerType:Class;
		[Embed(source = 'LanternFestival/LanternStore_english.txt',mimeType = "application/octet-stream")]
		public var LanternStore:Class;
		[Embed(source = 'LanternFestival/RiddleBuyPrice.txt',mimeType = "application/octet-stream")]
		public var RiddleBuyPrice:Class;
		[Embed(source = 'LanternFestival/RiddlesLib.txt',mimeType = "application/octet-stream")]
		public var RiddlesLib:Class;
		[Embed(source = 'CircularActive/LanternFestivalActive_english.txt',mimeType = "application/octet-stream")]
		public var LanternFestivalActive:Class;
		[Embed(source = 'LanternFestival/LanternTarget.txt',mimeType = "application/octet-stream")]
		public var LanternTarget:Class;
		
		
		
		[Embed(source = 'CircularActive/RedEnvelopeActive.txt',mimeType = "application/octet-stream")]
		public var RedEnvelopeActive:Class;
		
		
		[Embed(source = 'CrazyShopping/CrazyShopping.txt',mimeType = "application/octet-stream")]
		public var CrazyShopping:Class;
		[Embed(source = 'CrazyShopping/CrazyShoppingActive.txt',mimeType = "application/octet-stream")]
		public var CrazyShoppingActive:Class;
		
		[Embed(source = 'TheMammon/TheMammon.txt',mimeType = "application/octet-stream")]
		public var TheMammon:Class;
		[Embed(source = 'ItemConfig/HallowsShenzao.txt',mimeType = "application/octet-stream")]
		public var HallowsShenzao:Class;
		
		[Embed(source = 'GodWarChest/ChestReward.txt',mimeType = "application/octet-stream")]
		public var ChestReward:Class;
		[Embed(source = 'GodWarChest/GoldWarChestConfig.txt',mimeType = "application/octet-stream")]
		public var GoldWarChestConfig:Class;
		[Embed(source = 'Shop/GMShop.txt',mimeType = "application/octet-stream")]
		public var GMShop:Class;		
		
		[Embed(source = 'OldRoleBakcFT/SignUpAward.txt',mimeType = "application/octet-stream")]
		public var SignUpAward:Class;
		[Embed(source = 'OldRoleBakcFT/SignUpRemedyPrice.txt',mimeType = "application/octet-stream")]
		public var SignUpRemedyPrice:Class;
		
		[Embed(source = 'OldPlayerBack/DuXiangJiangLiLaoFu.txt',mimeType = "application/octet-stream")]
		public var DuXiangJiangLiLaoFu:Class;
		[Embed(source = 'OldPlayerBack/DuXiangJiangLiXinFu.txt',mimeType = "application/octet-stream")]
		public var DuXiangJiangLiXinFu:Class;
		[Embed(source = 'OldPlayerBack/GuizuDuXiangLaoFu.txt',mimeType = "application/octet-stream")]
		public var GuizuDuXiangLaoFu:Class;
		[Embed(source = 'OldPlayerBack/GuizuDuXiangXinFu.txt',mimeType = "application/octet-stream")]
		public var GuizuDuXiangXinFu:Class;
		[Embed(source = 'OldPlayerBack/HuiGuiDengjiDaliXinFu.txt',mimeType = "application/octet-stream")]
		public var HuiGuiDengjiDaliXinFu:Class;
		[Embed(source = 'OldPlayerBack/HuiGuiDengluDaliLaoFu.txt',mimeType = "application/octet-stream")]
		public var HuiGuiDengluDaliLaoFu:Class;
		[Embed(source = 'CircularActive/LianChongRebateActive_english.txt',mimeType = "application/octet-stream")]
		public var LianChongRebateActive:Class;
		[Embed(source = 'LianChongRebate/LianChongDayRange.txt',mimeType = "application/octet-stream")]
		public var LianChongDayRange:Class;
		[Embed(source = 'LianChongRebate/LianChongLevelRange.txt',mimeType = "application/octet-stream")]
		public var LianChongLevelRange:Class;
		[Embed(source = 'LianChongRebate/LianChongReward_english.txt',mimeType = "application/octet-stream")]
		public var LianChongReward:Class;
		[Embed(source = 'LianChongRebate/LianChongRewardCondition_english.txt',mimeType = "application/octet-stream")]
		public var LianChongRewardCondition:Class;
		[Embed(source = 'LianChongRebate/LianChongUnlock.txt',mimeType = "application/octet-stream")]
		public var LianChongUnlock:Class;
		[Embed(source = 'LianChongRebate/LianChongUnlockReward.txt',mimeType = "application/octet-stream")]
		public var LianChongUnlockReward:Class;
				
		[Embed(source = 'HeroShengdian/HeroShenddianCnt.txt',mimeType = "application/octet-stream")]
		public var HeroShenddianCnt:Class;
		[Embed(source = 'HeroShengdian/HeroShengdian.txt',mimeType = "application/octet-stream")]
		public var HeroShengdian:Class;

		[Embed(source = 'ShenWangBaoKu/pointStore_english.txt',mimeType = "application/octet-stream")]
		public var SwbkpointStore:Class;
		[Embed(source = 'ShenWangBaoKu/reward.txt',mimeType = "application/octet-stream")]
		public var Swbkreward:Class;
		[Embed(source = 'ShenWangBaoKu/rewardconfig_english.txt',mimeType = "application/octet-stream")]
		public var Swbkrewardconfig:Class;
		[Embed(source = 'ShenWangBaoKu/ShiJianKongZhi_english.txt',mimeType = "application/octet-stream")]
		public var SwbkShiJianKongZhi:Class;
		
		[Embed(source = 'QingMing/QingMingOutingUnlockReward.txt',mimeType = "application/octet-stream")]
		public var QingMingOutingUnlockReward:Class;
		[Embed(source = 'QingMing/QingMingOutingLottery.txt',mimeType = "application/octet-stream")]
		public var QingMingOutingLottery:Class;
		[Embed(source = 'QingMing/QingMingLuckyLotteryReward.txt',mimeType = "application/octet-stream")]
		public var QingMingLuckyLotteryReward:Class;
		[Embed(source = 'QingMing/QingMingKuaFuRank.txt',mimeType = "application/octet-stream")]
		public var QingMingKuaFuRank:Class;
		[Embed(source = 'QingMing/QingMingLocalRank.txt',mimeType = "application/octet-stream")]
		public var QingMingLocalRank:Class;
		[Embed(source = 'CircularActive/QingMingRankActive.txt',mimeType = "application/octet-stream")]
		public var QingMingRankActive:Class;
		[Embed(source = 'QingMing/QingMingRankConsolationReward.txt',mimeType = "application/octet-stream")]
		public var QingMingRankConsolationReward:Class;
		[Embed(source = 'QingMing/QingMingSevenDayRecharge.txt',mimeType = "application/octet-stream")]
		public var QingMingSevenDayRecharge:Class;
		[Embed(source = 'QingMing/QingMingSevenDayConsume.txt',mimeType = "application/octet-stream")]
		public var QingMingSevenDayConsume:Class;
		[Embed(source = 'QingMing/QingMingExchange.txt',mimeType = "application/octet-stream")]
		public var QingMingExchange:Class;
		[Embed(source = 'QingMing/QingMingLianjinReward.txt',mimeType = "application/octet-stream")]
		public var QingMingLianjinReward:Class;	
		[Embed(source = 'QQLZ/QQLZHappyDraw.txt',mimeType = "application/octet-stream")]
		public var QQLZHappyDraw:Class;	
		[Embed(source = 'QQLZ/QQLZHappyDrawExchange.txt',mimeType = "application/octet-stream")]
		public var QQLZHappyDrawExchange:Class;	
		[Embed(source = 'QQHZ/QQHZHappyDraw.txt',mimeType = "application/octet-stream")]
		public var QQHZHappyDraw:Class;	
		[Embed(source = 'QQHZ/QQHZHappyDrawExchange.txt',mimeType = "application/octet-stream")]
		public var QQHZHappyDrawExchange:Class;	
		
		[Embed(source = 'FiveOneDay/FiveOneCostReward_english.txt',mimeType = "application/octet-stream")]
		public var FiveOneCostReward:Class;
		[Embed(source = 'FiveOneDay/FiveOneLoginReward.txt',mimeType = "application/octet-stream")]
		public var FiveOneLoginReward:Class;

		[Embed(source = 'MoLing/MoLingLuckyDraw.txt',mimeType = "application/octet-stream")]
		public var MoLingLuckyDraw:Class;	
		[Embed(source = 'MoLing/MoLingVIPConfig.txt',mimeType = "application/octet-stream")]
		public var MoLingVIPConfig:Class;	
		[Embed(source = 'ItemConfig/MagicSpirit.txt',mimeType = "application/octet-stream")]
		public var MagicSpirit:Class;	
		[Embed(source = 'MoFaZhen/MFZSkillLevelup.txt',mimeType = "application/octet-stream")]
		public var MFZSkillLevelup:Class;
		[Embed(source = 'SuperInvest/SuperInvestLevel_english.txt',mimeType = "application/octet-stream")]
		 public var SuperInvestLevel:Class;
		[Embed(source = 'ZaiXianJiangLi/ZaiXianJiangLiReward.txt',mimeType = "application/octet-stream")]
		 public var ZaiXianJiangLiReward:Class;
		 [Embed(source = 'FiveOneDay/BadDragonReward_english.txt',mimeType = "application/octet-stream")]
		public var BadDragonReward:Class;
		[Embed(source = 'CircularActive/ZaiXianJiangLiActive.txt',mimeType = "application/octet-stream")]
		public var ZaiXianJiangLiActive:Class;
		[Embed(source = 'FiveOneDay/DragonBaoKu_english.txt',mimeType = "application/octet-stream")]
		public var DragonBaoKu:Class;
		[Embed(source = 'SuperCards/SuperCardsReward.txt',mimeType = "application/octet-stream")]
		public var SuperCardsReward:Class;

		[Embed(source = 'SuperPromption/SuperPromptionGoods.txt',mimeType = "application/octet-stream")]
		public var SuperPromptionGoods:Class;
				
		[Embed(source = 'YeYouJieWarmUp/LoginRewards.txt',mimeType = "application/octet-stream")]
		public var LoginRewards:Class;
		[Embed(source = 'YeYouJieWarmUp/RechargeRewards.txt',mimeType = "application/octet-stream")]
		public var RechargeRewards:Class;
		[Embed(source = 'YeYouJieRecharge/YeYouJieRechargeReward.txt',mimeType = "application/octet-stream")]
		public var YeYouJieRechargeReward:Class;
		[Embed(source = 'YeYouJieRecharge/YeYouJieRechargeLevelRange.txt',mimeType = "application/octet-stream")]
		public var YeYouJieRechargeLevelRange:Class;
		[Embed(source = 'YeYouJieRecharge/YeYouJieRechargeUnlock.txt',mimeType = "application/octet-stream")]
		public var YeYouJieRechargeUnlock:Class;
		[Embed(source = 'CircularActive/YeYouJieRechargeActive.txt',mimeType = "application/octet-stream")]
		public var YeYouJieRechargeActive:Class;

		[Embed(source = 'RewardBuff/RewardBuff_english.txt',mimeType = "application/octet-stream")]
		public var RewardBuff:Class;
		
		[Embed(source = 'YeYouJieDiscount/YeYouJieDiscountConfig.txt',mimeType = "application/octet-stream")]
		public var YeYouJieDiscountConfig:Class;
		[Embed(source = 'YeYouJieDiscount/YeYouJieDiscountDiscountPreview.txt',mimeType = "application/octet-stream")]
		public var YeYouJieDiscountDiscountPreview:Class;
		[Embed(source = 'YeYouJieDiscount/YeYouJieDiscountRefresh.txt',mimeType = "application/octet-stream")]
		public var YeYouJieDiscountRefresh:Class;
		[Embed(source = 'YeYouJieRecharge/YeYouJiefengbaokongzhi.txt',mimeType = "application/octet-stream")]
		public var YeYouJiefengbaokongzhi:Class;
		
		[Embed(source = 'KongJianDecennial/RegressRewards.txt',mimeType = "application/octet-stream")]
		public var RegressRewards:Class;
		[Embed(source = 'KongJianDecennial/KongJianRechargeUnlock.txt',mimeType = "application/octet-stream")]
		public var KongJianRechargeUnlock:Class;
		[Embed(source = 'KongJianDecennial/KongJianRechargeReward.txt',mimeType = "application/octet-stream")]
		public var KongJianRechargeReward:Class;
		[Embed(source = 'KongJianDecennial/KongJianLoginReward.txt',mimeType = "application/octet-stream")]
		public var KongJianLoginReward:Class;
		[Embed(source = 'KongJianDecennial/KongJianFirstRechargeReward.txt',mimeType = "application/octet-stream")]
		public var KongJianFirstRechargeReward:Class;
		[Embed(source = 'KongJianDecennial/KongJianDecennialLevelRange.txt',mimeType = "application/octet-stream")]
		public var KongJianDecennialLevelRange:Class;
		[Embed(source = 'KongJianDecennial/KongJianDecennialExchange.txt',mimeType = "application/octet-stream")]
		public var KongJianDecennialExchange:Class;
		
		[Embed(source = 'ClashOfTitans/ClashOfTitansPersonRank.txt',mimeType = "application/octet-stream")]
		public var ClashOfTitansPersonRank:Class;
		[Embed(source = 'ClashOfTitans/ClashOfTitansPersonScore.txt',mimeType = "application/octet-stream")]
		public var ClashOfTitansPersonScore:Class;
		[Embed(source = 'ClashOfTitans/ClashOfTitansUnionScore.txt',mimeType = "application/octet-stream")]
		public var ClashOfTitansUnionScore:Class;
		[Embed(source = 'ClashOfTitans/LevelRange.txt',mimeType = "application/octet-stream")]
		public var LevelRange:Class;
		[Embed(source = 'WangZheGongCe/ZaiXianLuxuryReward.txt',mimeType = "application/octet-stream")]
		public var ZaiXianLuxuryReward:Class;
		[Embed(source = 'WangZheGongCe/WangZheCrazyReward.txt',mimeType = "application/octet-stream")]
		public var WangZheCrazyReward:Class;
		[Embed(source = 'WangZheGongCe/WangZheRechargeRebate.txt',mimeType = "application/octet-stream")]
		public var WangZheRechargeRebate:Class;
		[Embed(source = 'WangZheGongCe/WangZheRechargeLottery.txt',mimeType = "application/octet-stream")]
		public var WangZheRechargeLottery:Class;
		[Embed(source = 'WangZheGongCe/ChouJiangYuLan.txt',mimeType = "application/octet-stream")]
		public var ChouJiangYuLan:Class;
		[Embed(source = 'WangZheGongCe/WangZheZheKouHuiConfig.txt',mimeType = "application/octet-stream")]
		public var WangZheZheKouHuiConfig:Class;
		[Embed(source = 'WangZheGongCe/WangZheZheKouHuiPreview.txt',mimeType = "application/octet-stream")]
		public var WangZheZheKouHuiPreview:Class;
		[Embed(source = 'WangZheGongCe/WangZheZheKouHuiRefresh.txt',mimeType = "application/octet-stream")]
		public var WangZheZheKouHuiRefresh:Class;
		[Embed(source = 'WangZheGongCe/WangZheExchange.txt',mimeType = "application/octet-stream")]
		public var WangZheExchange:Class;
		[Embed(source = 'WangZheGongCe/WangZheFashionShow.txt',mimeType = "application/octet-stream")]
		public var WangZheFashionShow:Class;
		[Embed(source = 'WangZheGongCe/WangZheFashionShowSuit.txt',mimeType = "application/octet-stream")]
		public var WangZheFashionShowSuit:Class;
		[Embed(source = 'WangZheGongCe/WangZheGuangGaoTu.txt',mimeType = "application/octet-stream")]
		public var WangZheGuangGaoTu:Class;
		[Embed(source = 'WangZheGongCe/WangZheRankConsolationReward.txt',mimeType = "application/octet-stream")]
		public var WangZheRankConsolationReward:Class;
		[Embed(source = 'WangZheGongCe/WangZheLocalRank.txt',mimeType = "application/octet-stream")]
		public var WangZheLocalRank:Class;
		[Embed(source = 'WangZheGongCe/WangZheKuaFuRank.txt',mimeType = "application/octet-stream")]
		public var WangZheKuaFuRank:Class;
		
		[Embed(source = 'DuanWuJie/goldZongzi.txt',mimeType = "application/octet-stream")]
		public var goldZongzi:Class;
		[Embed(source = 'DuanWuJie/normalZongzi.txt',mimeType = "application/octet-stream")]
		public var normalZongzi:Class;
		[Embed(source = 'DuanWuJie/reward.txt',mimeType = "application/octet-stream")]
		public var duanWureward:Class;
		[Embed(source = 'DuanWuJie/LevelRange.txt',mimeType = "application/octet-stream")]
		public var duanwuLevelRange:Class;
		[Embed(source = 'CircularActive/WangZheRankActive.txt',mimeType = "application/octet-stream")]
		public var WangZheRankActive:Class;
		[Embed(source = 'ClientConfig/TXT/GongGaoConfig/GongGaoCfg_ruxp.txt',mimeType = "application/octet-stream")]
		public var GongGaoCfg_ruxp:Class;
		[Embed(source = 'ClientConfig/TXT/GongGaoConfig/GongGaoCfg_naxp.txt',mimeType = "application/octet-stream")]
		public var GongGaoCfg_naxp:Class;
		[Embed(source = 'QQLZ/QQLZBaoXiangReward.txt',mimeType = "application/octet-stream")]
		public var QQLZBaoXiangReward:Class;
		[Embed(source = 'QQLZ/QQLZXunBaoReward.txt',mimeType = "application/octet-stream")]
		public var QQLZXunBaoReward:Class;
		[Embed(source = 'QQLZ/QQLZXunBaoBase.txt',mimeType = "application/octet-stream")]
		public var QQLZXunBaoBase:Class;
		[Embed(source = 'QQLZ/QQLZBaoXiangBase.txt',mimeType = "application/octet-stream")]
		public var QQLZBaoXiangBase:Class;
		[Embed(source = 'VIP/VipLibao_english.txt',mimeType = "application/octet-stream")]
		public var VipLibao:Class;
		[Embed(source = 'PassionAct/PassionActClient_english.txt',mimeType = "application/octet-stream")]
		public var PassionActClient:Class;
		[Embed(source = 'PassionAct/PassionGiftReward_english.txt',mimeType = "application/octet-stream")]
		public var PassionGiftReward:Class;
		[Embed(source = 'PassionAct/PassionMultiReward_english.txt',mimeType = "application/octet-stream")]
		public var PassionMultiReward:Class;
		[Embed(source = 'PassionAct/PassionConsumeConfig_english.txt',mimeType = "application/octet-stream")]
		public var PassionConsumeConfig:Class;
		[Embed(source = 'PassionAct/PassionExchange_english.txt',mimeType = "application/octet-stream")]
		public var PassionExchange:Class;
		[Embed(source = 'PassionAct/PassionExchangeFresh_english.txt',mimeType = "application/octet-stream")]
		public var PassionExchangeFresh:Class;
		[Embed(source = 'PassionAct/PassionRechargeConfig_english.txt',mimeType = "application/octet-stream")]
		public var PassionRechargeConfig:Class;
		[Embed(source = 'PassionAct/PassionRechargeKuaFuRank.txt',mimeType = "application/octet-stream")]
		public var PassionRechargeKuaFuRank:Class;
		[Embed(source = 'PassionAct/PassionRechargeLocalRank.txt',mimeType = "application/octet-stream")]
		public var PassionRechargeLocalRank:Class;
		[Embed(source = 'PassionAct/PassionRechargeRankReward.txt',mimeType = "application/octet-stream")]
		public var PassionRechargeRankReward:Class;
		[Embed(source = 'PreciousStore/PreciousStore_english.txt',mimeType = "application/octet-stream")]
		public var PreciousStore:Class;
		[Embed(source = 'PassionAct/PassionDiscount_english.txt',mimeType = "application/octet-stream")]
		public var PassionDiscount:Class;
		[Embed(source = 'PassionAct/PassionMarketPrecious_english.txt',mimeType = "application/octet-stream")]
		public var PassionMarketPrecious:Class;
		[Embed(source = 'PassionAct/PassionMarketConfig_english.txt',mimeType = "application/octet-stream")]
		public var PassionMarketConfig:Class;
		[Embed(source = 'PassionAct/PassionMarketRefresh_english.txt',mimeType = "application/octet-stream")]
		public var PassionMarketRefresh:Class;
		[Embed(source = 'PassionAct/PassionTutableAwardScheme.txt',mimeType = "application/octet-stream")]
		public var PassionTutableAwardScheme:Class;
		[Embed(source = 'PassionAct/PassionOnlineGift.txt',mimeType = "application/octet-stream")]
		public var PassionOnlineGift:Class;
		[Embed(source = 'PassionAct/PassionTutablePrice.txt',mimeType = "application/octet-stream")]
		public var PassionTutablePrice:Class;
		
		
		
		[Embed(source = 'WarStation/WarStation.txt',mimeType = "application/octet-stream")]
		public var WarStation:Class;
		[Embed(source = 'WarStation/WarStationSkill.txt',mimeType = "application/octet-stream")]
		public var WarStationSkill:Class;
		[Embed(source = 'ShenMiBaoXiang/ShenMiBaoXiangConfig_english.txt',mimeType = "application/octet-stream")]
		public var ShenMiBaoXiangConfig:Class;
		[Embed(source = 'ShenMiBaoXiang/ShenMiBaoXiangReward_english.txt',mimeType = "application/octet-stream")]
		public var ShenMiBaoXiangReward:Class;
		[Embed(source = 'RechargeEveryDay/RechargeEveryDay.txt',mimeType = "application/octet-stream")]
		public var RechargeEveryDay:Class;
		[Embed(source = 'StationSoul/StationSoul.txt',mimeType = "application/octet-stream")]
		public var StationSoul:Class;
		[Embed(source = 'StationSoul/StationSoulNode.txt',mimeType = "application/octet-stream")]
		public var StationSoulNode:Class;
		[Embed(source = 'StationSoul/StationSkill.txt',mimeType = "application/octet-stream")]
		public var StationSkill:Class;
		[Embed(source = 'StationSoul/StationSoulItem.txt',mimeType = "application/octet-stream")]
		public var StationSoulItem:Class;
		
		[Embed(source = 'DragonKnightChallenge/DKCNewBase.txt',mimeType = "application/octet-stream")]
		public var DKCNewBase:Class;
		[Embed(source = 'DragonKnightChallenge/DKCNewReward_english.txt',mimeType = "application/octet-stream")]
		public var DKCNewReward:Class;
		
		[Embed(source = 'WarStation/WarStationItem.txt',mimeType = "application/octet-stream")]
		public var WarStationItem:Class;
		[Embed(source = 'JT/JTGrade.txt',mimeType = "application/octet-stream")]
		public var JTGrade:Class;
		[Embed(source = 'JT/JTDayRewardNew.txt',mimeType = "application/octet-stream")]
		public var JTDayRewardNew:Class;
		[Embed(source = 'JT/JTWeekReward.txt',mimeType = "application/octet-stream")]
		public var JTWeekReward:Class;
		
		[Embed(source = 'ItemConfig/MysteryBox.txt',mimeType = "application/octet-stream")]
		public var MysteryBox:Class;
		[Embed(source = 'TurnTable/TurnTable.txt',mimeType = "application/octet-stream")]
		public var TurnTable:Class;
		[Embed(source = 'TurnTable/TurnTableBox.txt',mimeType = "application/octet-stream")]
		public var TurnTableBox:Class;

		[Embed(source = 'HeroConfig/CuiLianShi.txt',mimeType = "application/octet-stream")]
		public var CuiLianShi:Class;

		/**  
		 * description:
		 *<p> <<请在此处简要描述 Config 的主要功能>>  </p>
		 *<p> <b>粗体<b>  </p>
		 * @author: hardy (黄春豪)
		 * @date: 2014-1-16 下午5:00:33  
		 * @version: GameClient V1.0.0  
		 * 
		 */  
		public function USConfig()
		{
			super();
		}
		
		
	}
}