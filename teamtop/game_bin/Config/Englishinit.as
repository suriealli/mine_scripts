package
{
	
	import flash.display.Sprite;
	
	
	public class Englishinit extends Sprite
	{


		[Embed(source='ClientConfig/configList.txt',mimeType = "application/octet-stream")]
		public var configList:Class;

		[Embed(source='ClientConfig/EnglishLoadList.xml',mimeType = "application/octet-stream")]
		public var loadList:Class;

		[Embed(source='ClientConfig/EnglishRandomName.txt',mimeType = "application/octet-stream")]
		public var randomRoleName:Class;
		[Embed(source='ClientConfig/EnglishFilter.txt',mimeType = "application/octet-stream")]
		public var filter:Class;

		[Embed(source = 'language/english_configs.txt',mimeType = "application/octet-stream")]
		public var languageCfg:Class;
		[Embed(source = 'ClientConfig/US_language.txt',mimeType = "application/octet-stream")]
		public var LanguageConfig:Class;



				
		


		/**  
		 * description:
		 *<p> <<请在此处简要描述 init 的主要功能>>  </p>
		 *<p> <b>粗体<b>  </p>
		 * @author: hardy (黄春豪)
		 * @date: 2014-1-16 下午5:00:33  
		 * @version: GameClient V1.0.0  
		 * 
		 */  
		public function Englishinit()
		{
			super();
		}
		
		
	}
}