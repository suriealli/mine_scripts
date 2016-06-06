package
{
	
	import flash.display.Sprite;
	
	
	public class init extends Sprite
	{
		[Embed(source='ClientConfig/configList.txt',mimeType = "application/octet-stream")]
		public var configList:Class;

		[Embed(source='ClientConfig/loadList.xml',mimeType = "application/octet-stream")]
		public var loadList:Class;

		[Embed(source='ClientConfig/角色随机名.txt',mimeType = "application/octet-stream")]
		public var randomRoleName:Class;


		[Embed(source='ClientConfig/filter.txt',mimeType = "application/octet-stream")]
		public var filter:Class;

				
		


		/**  
		 * description:
		 *<p> <<请在此处简要描述 init 的主要功能>>  </p>
		 *<p> <b>粗体<b>  </p>
		 * @author: hardy (黄春豪)
		 * @date: 2014-1-16 下午5:00:33  
		 * @version: GameClient V1.0.0  
		 * 
		 */  
		public function init()
		{
			super();
		}
		
		
	}
}