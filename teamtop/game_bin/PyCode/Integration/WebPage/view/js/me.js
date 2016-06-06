var GET={};
var POST={};
var SESSION={};
var SCENE={}
var LOSTNOTE='';
var LANGUAGE='';
var DOMAIN='';
var FILE='';
var BODY='';
var MOTOR='';
var INFO={};
function lostnote(){
	//the action take by lostnote self
	this.models=['lostnote','file'];
	this.modelActions={'lostnote':
	                      ['remove','refresh','tabNav','checkAll','selectEntity','hover','say'],
					   'file':
					      ['collect','select','link','add']
					};
	this.memory={temp:''};
	this.scene=jQuery('body');
	//get the words from server side lostnote
    this.prepare=function(){
        jQuery('html').unbind('click').click(function(e){
			//take lost note's msg
			var msg=jQuery(e.target).attr('msg');
			if(msg){
				lostnote.get(msg);
			}
		});
    }
	//get lostnote's msg
	this.get=function(msg){
	    SESSION['path']=msg;
		SESSION['msg']={};
		SESSION['path_msg']='';
		msg=msg.split('/');
		if(msg[0]){
			SESSION.active.model=msg[0];
			SESSION['path']=SESSION['path'].replace(SESSION.active.model,SESSION.active.model+"/scene/instant");
		}else{
		    SESSION.active.model='guide';
		}
		//get entity
		if(msg.length%2==0){
		    SESSION.active.engity=msg[msg.length-1];
		    delete msg[msg.length-1];
		}
		//get info
	    //alert(POST['model']+'/'+POST['action']+'/'+POST['entity']);
		jQuery.each(msg,function(k,v){
			if(k%2==1){
			    SESSION['msg'][v]=msg[k+1];
			}else{
			    if(k!=0){
					SESSION['path_msg']+='/'+msg[k-1]+"/"+v;
				}
			}
		});
		if(SESSION['msg']['action']!=""){
		    SESSION.active.action=SESSION['msg']['action'];
			delete SESSION['msg']['action'];
		}else{
		    if(SESSION.active.entity!=''){
			    SESSION.active.action="view";
			}else{
			    SESSION.active.action="guide";
			}
		}
		//action
		var data=false;
		if(lostnote.tool.in_array(SESSION.active.model,this.models)){
		    if(lostnote.tool.in_array(SESSION.active.action,this.modelActions[SESSION.active.model])){
			    eval('data='+SESSION.active.model+'.'+SESSION.active.action+'()');
			}
		}
	    //**from motor to brain
		if(!data){
		    //prepare
			//send
			this.process();
			jQuery.post(LOSTNOTE+'/'+SESSION['path'],POST,function(json){
				lostnote.render(json);
			},'json');
		}else if(data!=true){
			this.render(data);
		}
		//console.dir(msg);
	}
	this.process=function(done){
	    if(!this.exist('#loading')){
		    jQuery('body').append('<img id="loading" src="'+BODY+'/host/icon/loading.gif" style="position:absolute;left:50%;top:50%;margin-left:-32px;margin-top:-32px;opacity:0.8;z-index:40008804"/>');
		}
	    if(done){
		    jQuery('#loading').hide();
			return;
		}
	    jQuery('#loading').show();
	}
	//************ render ***********
	this.render=function(data){
	    this.process('done');
	    //console.dir(data);
		if(data.SESSION){
			this.updateSession(data.SESSION);
		}
		
		//has specified handler
		if(data.handler){
		    GET=data.post;
			lostnote.get(data.handler);
			return;
		}
	  //**if has view,just show it
	    if(data.tips){
		    data.tips.title=data.title;
		    this.say(data.tips);
		}else if(typeof(data.content)!='undefined'){
		    this.show(data);
		}else{
		    jQuery('#view,#words').fadeOut();
		}
	}
	this.say=function(msg){
	    if(typeof(msg)=='string'){
		    msg={"msg":msg};
		    this.say(msg);
			return;
		}
		//jQuery('#view').dialog('close');
	    if(!this.exist('#words')){
		    jQuery('body').prepend('<div id="words"><div class="console"></div></div>');
		}
		var words=jQuery('#words .console');
		words.prepend('<p>'+msg.msg+'</p>').find('p:first').addClass('active').siblings('p').removeClass('active');
		if(!msg.title){msg.title='提示信息';}
		var closeFun=function(){};
		if(msg.url){
		    closeFun=function(){
			    lostnote.get(msg.url);
			}
		}
		if(msg.close){
		    closeFun=msg.close;
		}
		var mask=false;
		if(msg.mask){
		    mask=msg.mask;
		}
		jQuery('#words').attr({"title":msg.title}).dialog({
		    zIndex:400088,
		    width:'auto',
			close:closeFun,
			modal:mask
		});
	}
	this.show=function(data){
	    var view=data.content;
		var dialogID=SESSION.active.model+'_'+SESSION.active.action;
	    if(!this.exist('#view')){
		    jQuery('body').prepend('<div id="view"></div>');
		}
		
		jQuery('#'+dialogID).dialog('destroy').remove();
		
		var viewer=jQuery('#view');
		var dialog=viewer.append(view).find('.console:last');
		dialog.attr({'title':data.title,"id":dialogID}).show().siblings('.console:hidden').remove();
		this.initScene();
		//dialog.dialog('distroy');
		var index=100088;
		//cover mce dialog
		if((SESSION.active.model+'_'+SESSION.active.action)=='file_select'){
		    index=400088;
		//if(this.exist("div[id^=mce_][role=dialog]:visible")){
		    //if(index<jQuery("div[id^=mce_][role=dialog]:visible").css('z-index')){
			//    index=jQuery("div[id^=mce_][role=dialog]:visible").css('z-index')+1;
			//}
		}
		dialog.dialog({
		    minWidth:400,
		    zIndex:index,
		    width:'auto',//jQuery(this).find('.console').width()+60,
			maxHeight:600,
			close: function(event, ui) {
			    jQuery('#'+dialogID).dialog('destroy').remove();
			}
		});
		//submit
		dialog.find('input[type=submit]').click(function(){
		    if(!jQuery(this).hasClass('pending')){
			    dialog.dialog('close');
			}
		});
	}
	this.center=function(selector){
	    var width=jQuery(selector).width();
		var height=jQuery(selector).height();
	    jQuery(selector).css({'margin-left':-width/2,'margin-top':-height/2});
	}
	//***************************render************
	this.initScene=function(){
	    this.initActive();
		this.initGuide();
	    this.initForm();
		this.initList();
		this.initLinks();
		this.initScaler();
	}
	this.initScaler=function(){
	    if(lostnote.exist('.scaler')){
		    jQuery('.scaler').each(function(){
				var target={};
				var linkTo='';
				var input=jQuery(this).find('input');
				var max=parseInt(jQuery(this).attr('max'));
				var min=parseInt(jQuery(this).attr('min'));
				if(!min){min=1;}
				target=jQuery(jQuery(this).attr('target'));
				//select links
				//linkTo=target.attr('link');
				var linked='';
				
				//search links
				jQuery(this).find('a.up,a.down').unbind('click').click(function(){
					var value=parseInt(input.val());
					if(jQuery(this).hasClass('up')){
					    if(value==max){return;}
						value=value+1;
						input.val(value);
					}else{
					    if(value==min){return;}
						value=value-1;
						input.val(value);
					}
					target.each(function(){
					    linked=jQuery(this).attr('link').replace(/#/,input.attr('name')+'/'+input.val());
					    jQuery(this).attr({"href":linked});
						if(jQuery(this).attr('id')==input.attr('id')){
							window.location.href=linked;
						}
					});
				});
				input.change(function(){
				    //jQuery(this).val()
				    if(jQuery(this).val()>max){
					    jQuery(this).val(max);
					}
					target.each(function(){
					    linked=jQuery(this).attr('link').replace(/#/,input.attr('name')+'/'+input.val());
					    jQuery(this).attr({"href":linked});
					});
					if(jQuery(this).attr('link')!=''){
					    window.location.href=linked;
					}
				})
			});
		}
	}
	this.initLinks=function(){
	    if(lostnote.exist('.links')){
		    var linkTo='';
			linkTo=jQuery('.links').attr('link');
			//select links
			jQuery('.links select').change(function(){
				lostnote.get(linkTo.replace(/#/,'/'+jQuery(this).attr('name')+'/'+jQuery(this).val()));
			});
			//search links
			jQuery('.links input[name=search]').change(function(){
			    jQuery(this).val(jQuery(this).val().replace(/<|>|'|;|&|#|"|'/,''));
			    jQuery(this).next('a').attr({"msg":linkTo.replace(/#/,'/search/'+jQuery(this).val())});
				//jQuery(this).next('a').attr({"href":linkTo.replace(/#/,'/search/'+jQuery(this).val())});
			});
		}
	}
	this.initActive=function(){
	    if(!SESSION.active)return;
	    //initActive
	    jQuery.each(SESSION.active,function(k,v){
			jQuery('#'+k+'_'+v).addClass('active').siblings('a[id^='+k+'_]').removeClass('active');
		});
		//active category
		if(SESSION.msg&&!SESSION.msg.category){
		    jQuery('#category_all').addClass('active');
		}else if(SESSION.msg){
		    jQuery('#category_'+SESSION.msg.category).addClass('active');
		}
		//init category
		//init category with model
		jQuery('a[id^=category_][level=0]').css({'font-weight':'bold'}).prev('b').addClass('open');
		if(this.exist('a[id^=category_][level=0]')){
		    jQuery('a[id^=category_][level!=0][level!=1]').hide().prev('b').hide();
		}else{
            jQuery('a[id^=category_][level!=1]').hide().prev('b').hide();
		}
		//init level
		jQuery('a[id^=category_]').each(function(){
			var id=jQuery(this).attr('id');
			var level=parseInt(jQuery(this).attr('level'));
			if(level=='0'){
			   jQuery(this).css({"font-weight":"bold"});
			   return;
			}
			jQuery(this).prev('b').css({"margin-left":10*(level+1)+'px'});
			jQuery(this).prev('b').prev('a').prev('b[level='+(level-1)+']').addClass('parent').css({'cursor':"pointer"});
			if(jQuery(this).hasClass('active')&&jQuery(this).attr('level')!='1'){
			    //if(jQuery(this).attr(level)!='1'){
					//open
					var top_level=lostnote.tool.explode('_',jQuery(this).attr('id'));
					
					jQuery(this).prevAll('a[id^='+top_level[0]+"_"+top_level[1]+"]").prev('b').addClass('open');
					//jQuery(this).prevUntil('b.parent[level=1]').last().addClass('open');
					//jQuery(this).prevAll('b.parent').addClass('open');
					var this_level=parseInt(jQuery(this).attr('level'));
					jQuery(this).show().prevUntil('a[id^=category][level=1]').each(function(){
					    if(parseInt(jQuery(this).attr('level'))<=this_level){
						    jQuery(this).show();
						}
					});
					jQuery(this).nextUntil('b[level!='+jQuery(this).attr('level')+']').show();
					//parent siblings show
				    jQuery(this).nextUntil('b[level=1]').filter('a[level=2],b[level=2]').show();
				//}
			}
		});
		//jQuery('a[id^=category_][level!=1][class=active]').show().prevUntil('a[id^=category_][level=1]').show();
		jQuery('a[id^=category_]').prev('b').unbind('click').click(function(){
		    var id=jQuery(this).next('a').attr('id');
			var level=parseInt(jQuery(this).attr('level'));
			var open=jQuery(this).hasClass('open');
		    jQuery(this).toggleClass('open').next('a').nextUntil('b[level='+level+']').each(function(){
				if(open){
			        jQuery(this).removeClass('open').hide();
				}else{
				    if(jQuery(this).attr('level')!=level+1){return;}
				    jQuery(this).show();
				}
			});
		});
	}
	this.initGuide=function(){
	    //init guide
		jQuery('#guide a').hover(function(){
		    var anchor=jQuery(this);
		    jQuery(this).addClass('hover').siblings('a[display!=block]').removeClass('hover');
			var tips=jQuery(this).next('ul');
			if(tips.length>0&&jQuery(this).position().left&&tips.position().left!=jQuery(this).position().left&&tips.css('left')=='auto'&&tips.css('right')=='auto'){
			    tips.css({'left':jQuery(this).position().left});
			}
			var parent=jQuery(this).parent('ul');//console.dir(parent.length);
			if(parent.length>0){
			    if(!tips.css('left')){
			        tips.css({'left':parent.width()});
				}
				if(!tips.css('top')){
				    tips.css({'top':jQuery(this).position().top});
				}
			}
			if(tips.length>0){
				tips.siblings('ul[display!=block]').fadeOut(50);
				tips.fadeIn(50).hover(function(){
					jQuery(this).addClass('hover');
					jQuery(this).unbind('mouseleave').bind('mouseleave',function(e){
						if(!lostnote.isHover(e,anchor)){
							jQuery(this).removeClass('hover');
							if(jQuery(this).attr('display')=='block'){return;}//do not init displayed tips
							jQuery(this).fadeOut(50);
							anchor.removeClass('hover');
						}
					});
				});
			}
			jQuery(this).unbind('mouseleave').bind('mouseleave',function(e){
			    if(!lostnote.isHover(e,tips)){
				    if(jQuery(this).attr('display')=='block'){return;}//do not init displayed tips
					anchor.removeClass('hover');
					tips.removeClass('hover').fadeOut(50);
				}
			});
			return false;
		});
	}
	this.initList=function(){
		//init tabs
		if(lostnote.exist('.tabs[inited!=true]')){
		    jQuery('.tabs[inited!=true]').each(function(){
			    var tabsOption={};
			    eval('tabsOption={'+jQuery(this).attr('option')+'}');
		        jQuery(this).tabs(tabsOption).attr({'inited':'true'});
			});
		}
		//init lists
	    jQuery('table.list,div.list table').each(function(){
		    jQuery(this).find('tr').each(function(k,v){
				if(k%2==0){
					jQuery(this).addClass("even");
				}else{
					jQuery(this).addClass('odd');
				}
			});
		});
		jQuery('table.list .title').find('td[title]').html(jQuery('table.list .title').find('td[title]').attr('title'));
	}
	this.move=function(args){
			args.speed=args.speed||'slow';
			if(!args.id){args.id='lostnote'};
		var obj=jQuery('#'+args.id);
		var baseObj=jQuery('#'+args.base);
		    if(args.left!=0){
			    args.left=args.left||baseObj.width();
			}
			if(args.top!=0){
			    args.top=args.top||-50;
			}
		var parent=obj.parent();
		
		var baseOffset=baseObj.offset();
		var parentOffset=parent.offset();
			args.left=baseOffset.left-parentOffset.left+args.left;
			args.top=baseOffset.top-parentOffset.top+args.top;
			args.width=obj.width();
			args.height=obj.height();
			if(args.get){
				return args;
			}
			obj.animate({'left':args.left,'top':args.top},args.speed);
			if(args.move){
				jQuery(document).mousemove(function(e){
					args.left=args.left+e.pageX-baseOffset.left;
					args.top=args.top+e.pageY-baseOffset.top;
					obj.css({left:args.left,top:args.top});
				});
			}
	}
	this.startSession=function(msg){
	    LOSTNOTE=msg.LOSTNOTE;
		LANGUAGE=msg.LANGUAGE;
		DOMAIN=msg.DOMAIN;
		FILE=msg.FILE;
		BODY=msg.BODY;
		MOTOR=msg.MOTOR;
		INFO=msg.INFO;
		SCENE=msg.SCENE;
		SESSION=msg.SESSION;
		this.updateSession(SESSION);
		this.initScene();
	}
	this.updateSession=function(session){
	    if(session.card){
		    jQuery('#user').find('#profile .name').html(session.card.name).parent('#profile').show().siblings('#quick_login').hide();
		}else{
		    jQuery('#user').find('#quick_login').show().siblings('#profile').hide().find('.name').html('');
		}
	    SESSION=session;
	}
	this.initToggle=function(selector){
	    jQuery(selector).each(function(){
			jQuery(this).click(function(){
			    var target=jQuery(this).attr('toggle');
				jQuery('#'+target).toggle();
			})
		});
	}
	this.initHover=function(selector){
	    jQuery(selector).each(function(){
			jQuery(this).hover(function(){
			    var from_obj=jQuery(this);
				var from=jQuery(this).attr('id');
				var id=jQuery(this).attr('hover');
				jQuery(this).addClass('hover');
				var to=jQuery('#'+jQuery(this).attr('hover'));
				to.fadeIn(200).hover(function(){
				},function(e){
					if(!lostnote.isHover(e,from)){
					    to.fadeOut(200);
						from_obj.removeClass('hover');
					}
				});
				jQuery(this).mouseleave(function(e){
					if(!lostnote.isHover(e,id)){
					    jQuery('#'+id).fadeOut(200);
						from_obj.removeClass('hover');
					}
				});
			},function(){
			});
		});
	}
	this.isHover=function(e,id){
	    if(!id){return false;}
		var error=5;
		var x=e.pageX;
		var y=e.pageY;
		if(typeof(id)=='string'){
		    var target=jQuery('#'+id);
		}else{
		    var target=id;
		}
		var offset=target.offset();
		if(!offset){return;}
	    var x1=offset.left-error;
		var y1=offset.top-error;
		var x2=x1+target.outerWidth()+error;
		var y2=y1+target.outerHeight()+error;
		if(x>x1&&x2>x&&y2>y&&y>y1){
		    return true;
		}else{
		    return false;
		} 
	}
	this.initForm=function(){
	    if(this.exist('form')){
			//init textarea
		    if(this.exist('form .textarea')){	
				this.initEditor();
			}
			//init date
		    jQuery('form .date').datepicker({dateFormat:'yy-mm-dd'});
			//init submit
			jQuery('input[type=submit]').click(function(){
			    lostnote.process();
			});
			//init check
			jQuery('input[check]').each(function(){
			    jQuery(this).blur(function(){
				    if(!jQuery(this).attr('checking')||jQuery(this).attr('checking')!=jQuery(this).val()){
					    var name=jQuery(this).attr('name');
					    if(!lostnote.exist('#input_'+jQuery(this).attr('name')+'_check_img')){
						    jQuery('#input_'+jQuery(this).attr('name')+'_tips').before('<img id="input_'+jQuery(this).attr('name')+'_check_img" src="'+BODY+'/host/icon/checking.gif"/>&nbsp;&nbsp;');
						}
						jQuery('#input_'+jQuery(this).attr('name')+'_check_img').show();
						if(jQuery(this).attr('checking')==jQuery(this).val()){
						    return true;
						}
						jQuery(this).attr({"checking":jQuery(this).val()});
						var data={'check_key':name};
						data[name]=jQuery(this).val();
						if(lostnote.tool.strpos(name,'_confirm')){
						    if(data[name]!=jQuery('#form_input_'+name.replace('_confirm','')).val()){
							    jQuery('#input_'+name+'_check_img').attr({"src":BODY+'/icon/warn.gif'});
							    jQuery('#input_'+name+'_tips').html("确认有误！");
								return;
							}
						}
						var check=jQuery(this).attr('check')
						check=check.replace(check.split('/')[0],check.split('/')[0]+"/scene/instant")
						jQuery.post(LOSTNOTE+'/'+check,data,function(data){
						    //data=jQuery.parseJSON(data);
							//console.dir(data);
						    if(data.ERROR&&data.ERROR[name]){
							    jQuery('#input_'+name+'_check_img').attr({"src":BODY+'/host/icon/warn.gif'});
							    data.ERROR[name]='<span class="warn">'+data.ERROR[name]+'</span>';
							    jQuery('#input_'+name+'_tips').html(data.ERROR[name]);
							}else{
							    jQuery('#input_'+name+'_tips').html('');
							    jQuery('#input_'+name+'_check_img').attr({"src":BODY+'/host/icon/tick.png'});
							}
						},"json");
					}
				});
			});
		}
	}
	this.initEditor=function(){
	    jQuery('form .textarea[inited!=true]').each(function(){
		    jQuery(this).tinymce({
				// Location of TinyMCE script
				script_url : 'http://'+document.domain+'/body/motor/editor/tiny_mce.js',
				// General options
				theme : "advanced",
				skin : "o2k7",
				language:"cn",
					convert_urls:false,
				plugins : "autolink,lists,pagebreak,style,layer,table,save,advhr,advimage,advlink,iespell,insertdatetime,preview,media,searchreplace,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,inlinepopups",

				// Theme options
				theme_advanced_buttons1 : "save,code,fullscreen,preview,|,styleprops,formatselect,fontselect,fontsizeselect,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,numlist,bullist,outdent,indent,|,forecolor,backcolor",
				theme_advanced_buttons2 : "image,media,link,unlink,anchor,cleanup,|,insertdate,inserttime,|,cut,copy,paste,pastetext,pasteword,|,search,|,tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,advhr",
				theme_advanced_buttons3 : "",
				theme_advanced_toolbar_location : "top",
				theme_advanced_toolbar_align : "left",
				theme_advanced_statusbar_location : "bottom",
				theme_advanced_resizing : true,

				// Example word content CSS (should be your site CSS) this one removes paragraph margins
				content_css : 'http://'+document.domain+"/body/motor/editor/css/word.css",

				// Drop lists for link/image/media/template dialogs
				template_external_list_url : 'http://'+document.domain+"/body/motor/editor/lists/template_list.js",
				external_link_list_url : 'http://'+document.domain+"/body/motor/editor/lists/link_list.js",
				external_image_list_url : 'http://'+document.domain+"/body/motor/editor/lists/image_list.js",
				media_external_list_url : 'http://'+document.domain+"/body/motor/editor/lists/media_list.js",
				
				// Replace values for the template plugin
				template_replace_values : {
					username : "Some User",
					staffid : "991234"
				}
			}).attr({'inited':'true'});
		});
		jQuery('#form input[type=submit]').click(function(e){
			tinyMCE.triggerSave();
		});
	}
    this.exist=function(selector){
	    if(jQuery(selector).size()>0){
		    return jQuery(selector).size();
		}
	}
	this.getLibrary=function(scripts,callback){
	    if(typeof(scripts) != "object") var scripts = [scripts];
	    var HEAD = document.getElementsByTagName("head").item(0) || document.documentElement;
	    var s = new Array(), last = scripts.length - 1, recursiveLoad = function(i) {  //递归
			s[i] = document.createElement("script");
			s[i].setAttribute("type","text/javascript");
			s[i].onload = s[i].onreadystatechange = function() { //Attach handlers for all browsers
				if(!/*@cc_on!@*/0 || this.readyState == "loaded" || this.readyState == "complete") {
					this.onload = this.onreadystatechange = null; this.parentNode.removeChild(this); 
					if(i != last) recursiveLoad(i + 1); else if(typeof(callback) == "function") callback();
				}
			}
			s[i].setAttribute("src",scripts[i]);
			HEAD.appendChild(s[i]);
	    };
	    recursiveLoad(0);
	} 
	this.getScript=function(url){
		var script= document.createElement("script");
		script.type = 'text/javascript';
		script.src = url;
		document.getElementsByTagName("head")[0].appendChild(script);
	}
	this.tabNav=function(){
	    jQuery('#action a[location='+SESSION.msg.target+']').addClass('active').parent('li').addClass('active').siblings('li').removeClass('active').find('a').removeClass('active');
        var height=jQuery('#'+SESSION.msg.group+'_'+SESSION.msg.target).next('.box').css('height');
		jQuery('#'+SESSION.msg.group+'_'+SESSION.msg.target).next('.box').slideDown('fast').siblings('.box').slideUp('fast');
		if(SESSION.msg.type=='fade'){
		    jQuery('#'+SESSION.msg.group+'_'+SESSION.msg.target+'_details').fadeIn(1000).siblings('*[id$=_details]:visible').fadeOut(1000);
		}else{
		    jQuery('#'+SESSION.msg.group+'_'+SESSION.msg.target+'_details').show().siblings('*[id$=_details]:visible').hide();
		}
		jQuery('#'+SESSION.msg.group+'_'+SESSION.msg.target+'_details').fadeIn(1000).siblings('*[id$=_details]:hidden').fadeOut(1000);
		jQuery('#'+SESSION.msg.group+'_'+SESSION.msg.target).addClass('active').siblings('*[id^='+SESSION.msg.group+']').removeClass('active');

		//trigger
		if(SESSION.msg.trigger){
		    var trigger=(SESSION.msg.trigger).split('_');
			//console.dir(trigger);
			eval(trigger[0]+'.'+trigger[1]+'({})');
		}
		return true;
	}
	//play Slide
	this.playSlide=function(data,time){
	    if(typeof(time)=='undefined'){time=5;}
	    jQuery.each(data,function(k,v){
			var html='';
			var slide=jQuery('#'+k);
			var count=v.length;
			jQuery.each(v,function(key,value){
		        value.content=value.content?value.content:'';
				html='<img content="'+value.content+'" href="'+value.link+'" style="cursor:pointer;" src="'+value.src+'"/>'+html;
				if(count==1){return false;}
				html='<a id="slideIndex_'+key+'">'+(Number(key)+1)+'</a>'+html;
			});
		    slide.prepend(html);
			slide.find('a[id^=slideIndex_]').each(function(){
			    jQuery(this).css({"position":"relative",'z-index':'1'}).click(function(){
				    jQuery(this).addClass('active').siblings('a[class=active]').removeClass('active');
					jQuery(this).next('img').fadeIn().siblings('img:visible').fadeOut();
					jQuery(this).siblings('.content').html(jQuery(this).next('img').attr('content'));
				});
			}).siblings('img').click(function(){
			    window.location.href=jQuery(this).attr('href');
			});
			slide.find("a:last").click();
			jQuery('body').everyTime(time+'s',function(){
			    var next=slide.find('a[class=active]').prev('img').prev('a');
				if(next.size()==0){
				    next=slide.find('a:last');
				}
				next.click();
			});
		});
	}
	this.function_exists=function(model,action){
	    return eval(model.action);
	}
	this.copy=function(data){
	    if (document.all){                                            //判断Ie
			window.clipboardData.setData('text',data);
			    lostnote.say('Copied!');
		}else{
			    lostnote.say('Please copy by yourself:<br /><textarea class="warn">'+data+'</textarea>');
		}
	}
	this.href=function(target){
	    window.location.href=target;
	}
	this.refresh=function(){
	     window.location.reload();
		 return 'true';
	}
	this.addFavor=function(){
		var url = window.location;
		var title = document.title;
		var ua = navigator.userAgent.toLowerCase();
		if (ua.indexOf("360se") > -1) {
			alert("由于360浏览器功能限制，请按 Ctrl+D 手动收藏！");
		}
		else if (ua.indexOf("msie 8") > -1) {
			window.external.AddToFavoritesBar(url, title); //IE8
		}
		else if (document.all) {
	  try{
	   window.external.addFavorite(url, title);
	  }catch(e){
	   alert('您的浏览器不支持,请按 Ctrl+D 手动收藏!');
	  }
		}
		else if (window.sidebar) {
			window.sidebar.addPanel(title, url, "");
		}
		else {
	  alert('您的浏览器不支持,请按 Ctrl+D 手动收藏!');
		}
	}
	this.setHome=function(){
	    if (document.all) {
            document.body.style.behavior='url(#default#homepage)';
               document.body.setHomePage(url);
        }else{
            alert("您好,您的浏览器不支持自动设置页面为首页功能,请您手动在浏览器里设置该页面为首页!");
        }
	}
	this.tool =  {
		ns: function(string) {
		 
			return lostnote.config.ns + string;
		 
		},
		 
		nsAll: function(obj) {
		 
			var nsObj = new Object();
			 
			for(param in obj) {  // print out the params
				if (obj.hasOwnProperty(param)) {
					nsObj[lostnote.config.ns+param] = obj[param];
				}
			}
			 
			return nsObj;
		},
		 
		getScript: function(file, path) {
		 
			jQuery.getScript(path + file);
			 
			return;
		 
		},
		 
		makeUrl: function(template, uri, params) {
			var url = jQuery.sprintf(template, uri, jQuery.param(lostnote.util.nsAll(params)));
			//alert(url);
			return url;
		},
		 
		createCookie: function (name,value,days,domain) {
			if (days) {
				var date = new Date();
				date.setTime(date.getTime()+(days*24*60*60*1000));
				var expires = "; expires="+date.toGMTString();
			}
			else var expires = "";
			document.cookie = name+"="+value+expires+"; path=/";
		},
	 
		setCookie: function (name,value,days,path,domain,secure) {
			var date = new Date();
			date.setTime(date.getTime()+(days*24*60*60*1000));
			 
			document.cookie = name + "=" + escape (value) +
			((days) ? "; expires=" + date.toGMTString() : "") +
			((path) ? "; path=" + path : "") +
			((domain) ? "; domain=" + domain : "") +
			((secure) ? "; secure" : "");
		},
		 
		readAllCookies: function() {
		 
			lostnote.debug('Reading all cookies...');
			//var dhash = '';
			var jar = {};
			//var nameEQ = name + "=";
			var ca = document.cookie.split(';');
			 
			if (ca) {
				lostnote.debug(document.cookie);
				for(var i=0;i < ca.length;i++) {
					 
					cat = lostnote.util.trim(ca[i]);
					var pos = lostnote.util.strpos(cat, '=');
					var key = cat.substring(0,pos);
					var value = cat.substring(pos+1, cat.length);
					//lostnote.debug('key %s, value %s', key, value);
					// create cookie jar array for that key
					// this is needed because you can have multiple cookies with the same name
					if ( ! jar.hasOwnProperty(key) ) {
						jar[key] = [];
					}
					// add the value to the array
					jar[key].push(value);
				}
				 
				lostnote.debug(JSON.stringify(jar));
				return jar;
			}
		},
		 
		/**
		 * Reads and returns values from cookies.
		 *
		 * NOTE: this function returns an array of values as there can be
		 * more than one cookie with the same name.
		 *
		 * @return  array
		 */
		readCookie: function (name) {
			lostnote.debug('Attempting to read cookie: %s', name);
			var jar = lostnote.util.readAllCookies();
			if ( jar ) {
				if ( jar.hasOwnProperty(name) ) {
					return jar[name];
				} else {
					return '';
				}
			}
		},
		 
		eraseCookie: function (name, domain) {
			lostnote.debug(document.cookie);
			if ( ! domain ) {
				domain = lostnote.getSetting('cookie_domain') || document.domain;
			}
			lostnote.debug("erasing cookie: " + name + " in domain: " +domain);
			this.setCookie(name,"",-1,"/",domain);
			// attempt to read the cookie again to see if its there under another valid domain
			var test = lostnote.util.readCookie(name);
			// if so then try the alternate domain              
			if (test) {
				 
				var period = domain.substr(0,1);
				lostnote.debug('period: '+period);
				if (period === '.') {
					var domain2 = domain.substr(1);
					lostnote.debug("erasing " + name + " in domain2: " + domain2);
					this.setCookie(name,"",-2,"/", domain2);
					 
						 
				} else {
					//  domain = '.'+ domain
					lostnote.debug("erasing " + name + " in domain3: " + domain);
					this.setCookie(name,"",-2,"/",domain);  
				}
				//lostnote.debug("erasing " + name + " in domain: ");
				//this.setCookie(name,"",-2,"/");   
			}
			 
		},
		 
		eraseMultipleCookies: function(names, domain) {
			 
			for (var i=0; i < names.length; i++) {
				this.eraseCookie(names[i], domain);
			}
		},
		 
		loadScript: function (url, callback){
	 
			   return LazyLoad.js(url, callback);
		},
	 
		loadCss: function (url, callback){
	 
			return LazyLoad.css(url, callback);
		},
		 
		parseCookieString: function parseQuery(v) {
			var queryAsAssoc = new Array();
			var queryString = unescape(v);
			var keyValues = queryString.split("|||");
			//alert(keyValues);
			for (var i in keyValues) {
				if (keyValues.hasOwnProperty(i)) {
					var key = keyValues[i].split("=>");
					queryAsAssoc[key[0]] = key[1];
				}
				//alert(key[0] +"="+ key[1]);
			}
			 
			return queryAsAssoc;
		},
		 
		parseCookieStringToJson: function parseQuery(v) {
			var queryAsObj = new Object;
			var queryString = unescape(v);
			var keyValues = queryString.split("|||");
			//alert(keyValues);
			for (var i in keyValues) {
				if (keyValues.hasOwnProperty(i)) {
					var key = keyValues[i].split("=>");
					queryAsObj[key[0]] = key[1];
					//alert(key[0] +"="+ key[1]);
				}
			}
			//alert (queryAsObj.period);
			return queryAsObj;
		},
		 
		nsParams: function(obj) {
			var new_obj = new Object;
			 
			for(param in obj) {
				if (obj.hasOwnProperty(param)) {
					new_obj['lostnote_'+ param] = obj[param];
				}
			}
			 
			return new_obj;
		},
		 
		urlEncode : function(str) {
			// URL-encodes string  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/urlencode
			// +   original by: Philip Peterson
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: AJ
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Brett Zamir (http://brett-zamir.me)
			// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: travc
			// +      input by: Brett Zamir (http://brett-zamir.me)
			// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Lars Fischer
			// +      input by: Ratheous
			// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
			// +   bugfixed by: Joris
			// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
			// %          note 1: This reflects PHP 5.3/6.0+ behavior
			// %        note 2: Please be aware that this function expects to encode into UTF-8 encoded strings, as found on
			// %        note 2: pages served as UTF-8
			// *     example 1: urlencode('Kevin van Zonneveld!');
			// *     returns 1: 'Kevin+van+Zonneveld%21'
			// *     example 2: urlencode('http://kevin.vanzonneveld.net/');
			// *     returns 2: 'http%3A%2F%2Fkevin.vanzonneveld.net%2F'
			// *     example 3: urlencode('http://www.google.nl/search?q=php.js&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a');
			// *     returns 3: 'http%3A%2F%2Fwww.google.nl%2Fsearch%3Fq%3Dphp.js%26ie%3Dutf-8%26oe%3Dutf-8%26aq%3Dt%26rls%3Dcom.ubuntu%3Aen-US%3Aunofficial%26client%3Dfirefox-a'
			str = (str+'').toString();
			 
			// Tilde should be allowed unescaped in future versions of PHP (as reflected below), but if you want to reflect current
			// PHP behavior, you would need to add ".replace(/~/g, '%7E');" to the following.
			return encodeURIComponent(str).replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').replace(/\)/g, '%29').replace(/\*/g, '%2A').replace(/%20/g, '+');
		 
		},
		 
		urldecode : function (str) {
			// Decodes URL-encoded string  
			// 
			// version: 1008.1718
			// discuss at: http://phpjs.org/functions/urldecode
			// +   original by: Philip Peterson
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: AJ
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Brett Zamir (http://brett-zamir.me)
			// +      input by: travc
			// +      input by: Brett Zamir (http://brett-zamir.me)
			// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Lars Fischer
			// +      input by: Ratheous
			// +   improved by: Orlando
			// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
			// +      bugfixed by: Rob
			// %        note 1: info on what encoding functions to use from: http://xkr.us/articles/javascript/encode-compare/
			// %        note 2: Please be aware that this function expects to decode from UTF-8 encoded strings, as found on
			// %        note 2: pages served as UTF-8
			// *     example 1: urldecode('Kevin+van+Zonneveld%21');
			// *     returns 1: 'Kevin van Zonneveld!'
			// *     example 2: urldecode('http%3A%2F%2Fkevin.vanzonneveld.net%2F');
			// *     returns 2: 'http://kevin.vanzonneveld.net/'
			// *     example 3: urldecode('http%3A%2F%2Fwww.google.nl%2Fsearch%3Fq%3Dphp.js%26ie%3Dutf-8%26oe%3Dutf-8%26aq%3Dt%26rls%3Dcom.ubuntu%3Aen-US%3Aunofficial%26client%3Dfirefox-a');
			// *     returns 3: 'http://www.google.nl/search?q=php.js&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a'
			 
			return decodeURIComponent(str.replace(/\+/g, '%20'));
		},
		 
		parseUrlParams : function(url) {
			 
			var _GET = {};
			for(var i,a,m,n,o,v,p=location.href.split(/[?&]/),l=p.length,k=1;k<l;k++)
				if( (m=p[k].match(/(.*?)(\..*?|\[.*?\])?=([^#]*)/)) && m.length==4){
					n=decodeURI(m[1]).toLowerCase(),o=_GET,v=decodeURI(m[3]);
					if(m[2])
						for(a=decodeURI(m[2]).replace(/\[\s*\]/g,"[-1]").split(/[\.\[\]]/),i=0;i<a.length;i++)
							o=o[n]?o[n]:o[n]=(parseInt(a[i])==a[i])?[]:{}, n=a[i].replace(/^["\'](.*)["\']$/,"$1");
							n!='-1'?o[n]=v:o[o.length]=v;
				}
			 
			return _GET;
		},
		 
		strpos : function(haystack, needle, offset) {
			// Finds position of first occurrence of a string within another  
			// 
			// version: 1008.1718
			// discuss at: http://phpjs.org/functions/strpos
			// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Onno Marsman    
			// +   bugfixed by: Daniel Esteban
			// +   improved by: Brett Zamir (http://brett-zamir.me)
			// *     example 1: strpos('Kevin van Zonneveld', 'e', 5);
			// *     returns 1: 14
			var i = (haystack+'').indexOf(needle, (offset || 0));
			return i === -1 ? false : i;
		},
		 
		strCountOccurances : function(haystack, needle) {
			return haystack.split(needle).length - 1;
		},
		 
		implode : function(glue, pieces) {
			// Joins array elements placing glue string between items and return one string  
			// 
			// version: 1008.1718
			// discuss at: http://phpjs.org/functions/implode
			// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Waldo Malqui Silva
			// +   improved by: Itsacon (http://www.itsacon.net/)
			// +   bugfixed by: Brett Zamir (http://brett-zamir.me)
			// *     example 1: implode(' ', ['Kevin', 'van', 'Zonneveld']);
			// *     returns 1: 'Kevin van Zonneveld'
			// *     example 2: implode(' ', {first:'Kevin', last: 'van Zonneveld'});
			// *     returns 2: 'Kevin van Zonneveld'
			var i = '', retVal='', tGlue='';
			if (arguments.length === 1) {
				pieces = glue;
				glue = '';
			}
			if (typeof(pieces) === 'object') {
				if (pieces instanceof Array) {
					return pieces.join(glue);
				}
				else {
					for (i in pieces) {
						retVal += tGlue + pieces[i];
						tGlue = glue;
					}
					return retVal;
				}
			}
			else {
				return pieces;
			}
		},
		 
		checkForState: function( store_name ) {
		 
			return lostnote.checkForState( store_name );
		},
		 
		setState : function(store_name, key, value, is_perminant,format, expiration_days) {
			 
			return lostnote.setState(store_name, key, value, is_perminant,format, expiration_days);
		},
		 
		replaceState : function (store_name, value, is_perminant, format, expiration_days) {
	 
			return lostnote.replaceState(store_name, value, is_perminant, format, expiration_days);
		},
		 
		getRawState : function(store_name) {
			 
			return lostnote.getStateFromCookie(store_name);
		},
		 
		getState : function(store_name, key) {
			 
			return lostnote.getState(store_name, key);
		},
		 
		clearState : function(store_name) {
			 
			return lostnote.clearState(store_name);
		},
		 
		getCookieValueFormat : function(cstring) {
			var format = '';
			var check = cstring.substr(0,1);            
			if (check === '{') {
				format = 'json';
			} else {
				format = 'assoc';
			}
			 
			return format;
		},
		 
		decodeCookieValue : function(string) {
			 
			var format = lostnote.util.getCookieValueFormat(string);
			var value = '';
			//lostnote.debug('decodeCookieValue - string: %s, format: %s', string, format);      
			if (format === 'json') {
				value = JSON.parse(string);
			 
			} else {
				value = lostnote.util.jsonFromAssocString(string);
			}
			lostnote.debug('decodeCookieValue - string: %s, format: %s, value: %s', string, format, JSON.stringify(value));      
			return value;
		},
		 
		encodeJsonForCookie : function(json_obj, format) {
			 
			format = format || 'assoc';
			 
			if (format === 'json') {
				return JSON.stringify(json_obj);
			} else {
				return lostnote.util.assocStringFromJson(json_obj);
			}
		},
		 
		getCookieDomainHash: function(domain) {
			// must be string
			return lostnote.util.dechex(lostnote.util.crc32(domain));
		},
		 
		loadStateJson : function(store_name) {
			var store = unescape(lostnote.util.readCookie( lostnote.getSetting('ns') + store_name ) );
			if (store) {
				state = JSON.parse(store);
			}
			lostnote.state[store_name] = state;
			lostnote.debug('state store %s: %s', store_name, JSON.stringify(state));
		},
	 
		is_array : function (input) {
			return typeof(input)=='object'&&(input instanceof Array);   
		},
		 
		// Returns true if variable is an object  
		// 
		// version: 1008.1718
		// discuss at: http://phpjs.org/functions/is_object
		// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
		// +   improved by: Legaev Andrey
		// +   improved by: Michael White (http://getsprink.com)
		// *     example 1: is_object('23');
		// *     returns 1: false
		// *     example 2: is_object({foo: 'bar'});
		// *     returns 2: true
		// *     example 3: is_object(null);
		// *     returns 3: false
		is_object : function (mixed_var) {
	 
			if (mixed_var instanceof Array) {
				return false;
			} else {
				return (mixed_var !== null) && (typeof( mixed_var ) == 'object');
			}
		},
		 
		countObjectProperties : function( obj ) {
			 
			var size = 0, key;
			for (key in obj) {
				if (obj.hasOwnProperty(key)) size++;
			}
			return size;
		},
		 
		jsonFromAssocString : function(str, inner, outer) {
			 
			inner = inner || '=>';
			outer = outer || '|||';
			 
			if (str){
			 
				if (!this.strpos(str, inner)) {
		 
					return str;
					 
				} else {
					 
					var assoc = {};
					outer_array = str.split(outer);
					//lostnote.debug('outer array: %s', JSON.stringify(outer_array));
					for (var i = 0, n = outer_array.length; i < n; i++) {
					 
						var inside_array = outer_array[i].split(inner);
						 
						assoc[inside_array[0]] = inside_array[1];
					}   
				}
				 
				//lostnote.debug('jsonFromAssocString: ' + JSON.stringify(assoc));
				return assoc;
			}
		},
		 
		assocStringFromJson : function(obj) {
			 
			var string = '';
			var i = 0;
			var count = lostnote.util.countObjectProperties(obj);
			 
			for (prop in obj) {
				i++;
				string += prop + '=>' + obj[prop];
				 
				if (i < count) {
					string += '|||';
				}
			}
			//lostnote.debug('lostnote.util.assocStringFromJson: %s', string);
			return string;  
		 
		},
		 
		getDomainFromUrl : function (url, strip_www) {
			 
			var domain = url.split(/\/+/g)[1];
			 
			if (strip_www === true) {
				var fp = domain.split('.')[0];
				 
				if (fp === 'www') {
					return domain.substring(4);
				} else {
					return domain;
				}
				 
			} else {
				return domain;
			}
		},
		 
		getCurrentUnixTimestamp : function() {
			return Math.round(new Date().getTime() / 1000);
		},
		 
		generateHash : function(value) {
		 
			return this.crc32(value);
		},
		 
		generateRandomGuid : function(salt) {
			var time = this.getCurrentUnixTimestamp();
			var random = this.rand();
			return this.generateHash(time + random + salt);
		},
		 
		crc32 : function ( str ) {
			// Calculate the crc32 polynomial of a string  
			// 
			// version: 1008.1718
			// discuss at: http://phpjs.org/functions/crc32
			// +   original by: Webtoolkit.info (http://www.webtoolkit.info/)
			// +   improved by: T0bsn
			// -    depends on: utf8_encode
			// *     example 1: crc32('Kevin van Zonneveld');
			// *     returns 1: 1249991249
			str = this.utf8_encode(str);
			var table = "00000000 77073096 EE0E612C 990951BA 076DC419 706AF48F E963A535 9E6495A3 0EDB8832 79DCB8A4 E0D5E91E 97D2D988 09B64C2B 7EB17CBD E7B82D07 90BF1D91 1DB71064 6AB020F2 F3B97148 84BE41DE 1ADAD47D 6DDDE4EB F4D4B551 83D385C7 136C9856 646BA8C0 FD62F97A 8A65C9EC 14015C4F 63066CD9 FA0F3D63 8D080DF5 3B6E20C8 4C69105E D56041E4 A2677172 3C03E4D1 4B04D447 D20D85FD A50AB56B 35B5A8FA 42B2986C DBBBC9D6 ACBCF940 32D86CE3 45DF5C75 DCD60DCF ABD13D59 26D930AC 51DE003A C8D75180 BFD06116 21B4F4B5 56B3C423 CFBA9599 B8BDA50F 2802B89E 5F058808 C60CD9B2 B10BE924 2F6F7C87 58684C11 C1611DAB B6662D3D 76DC4190 01DB7106 98D220BC EFD5102A 71B18589 06B6B51F 9FBFE4A5 E8B8D433 7807C9A2 0F00F934 9609A88E E10E9818 7F6A0DBB 086D3D2D 91646C97 E6635C01 6B6B51F4 1C6C6162 856530D8 F262004E 6C0695ED 1B01A57B 8208F4C1 F50FC457 65B0D9C6 12B7E950 8BBEB8EA FCB9887C 62DD1DDF 15DA2D49 8CD37CF3 FBD44C65 4DB26158 3AB551CE A3BC0074 D4BB30E2 4ADFA541 3DD895D7 A4D1C46D D3D6F4FB 4369E96A 346ED9FC AD678846 DA60B8D0 44042D73 33031DE5 AA0A4C5F DD0D7CC9 5005713C 270241AA BE0B1010 C90C2086 5768B525 206F85B3 B966D409 CE61E49F 5EDEF90E 29D9C998 B0D09822 C7D7A8B4 59B33D17 2EB40D81 B7BD5C3B C0BA6CAD EDB88320 9ABFB3B6 03B6E20C 74B1D29A EAD54739 9DD277AF 04DB2615 73DC1683 E3630B12 94643B84 0D6D6A3E 7A6A5AA8 E40ECF0B 9309FF9D 0A00AE27 7D079EB1 F00F9344 8708A3D2 1E01F268 6906C2FE F762575D 806567CB 196C3671 6E6B06E7 FED41B76 89D32BE0 10DA7A5A 67DD4ACC F9B9DF6F 8EBEEFF9 17B7BE43 60B08ED5 D6D6A3E8 A1D1937E 38D8C2C4 4FDFF252 D1BB67F1 A6BC5767 3FB506DD 48B2364B D80D2BDA AF0A1B4C 36034AF6 41047A60 DF60EFC3 A867DF55 316E8EEF 4669BE79 CB61B38C BC66831A 256FD2A0 5268E236 CC0C7795 BB0B4703 220216B9 5505262F C5BA3BBE B2BD0B28 2BB45A92 5CB36A04 C2D7FFA7 B5D0CF31 2CD99E8B 5BDEAE1D 9B64C2B0 EC63F226 756AA39C 026D930A 9C0906A9 EB0E363F 72076785 05005713 95BF4A82 E2B87A14 7BB12BAE 0CB61B38 92D28E9B E5D5BE0D 7CDCEFB7 0BDBDF21 86D3D2D4 F1D4E242 68DDB3F8 1FDA836E 81BE16CD F6B9265B 6FB077E1 18B74777 88085AE6 FF0F6A70 66063BCA 11010B5C 8F659EFF F862AE69 616BFFD3 166CCF45 A00AE278 D70DD2EE 4E048354 3903B3C2 A7672661 D06016F7 4969474D 3E6E77DB AED16A4A D9D65ADC 40DF0B66 37D83BF0 A9BCAE53 DEBB9EC5 47B2CF7F 30B5FFE9 BDBDF21C CABAC28A 53B39330 24B4A3A6 BAD03605 CDD70693 54DE5729 23D967BF B3667A2E C4614AB8 5D681B02 2A6F2B94 B40BBE37 C30C8EA1 5A05DF1B 2D02EF8D";
		  
			var crc = 0;
			var x = 0;
			var y = 0;
		  
			crc = crc ^ (-1);
			for (var i = 0, iTop = str.length; i < iTop; i++) {
				y = ( crc ^ str.charCodeAt( i ) ) & 0xFF;
				x = "0x" + table.substr( y * 9, 8 );
				crc = ( crc >>> 8 ) ^ x;
			}
		  
			return crc ^ (-1);
		},
		 
		utf8_encode : function ( argString ) {
			// Encodes an ISO-8859-1 string to UTF-8  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/utf8_encode
			// +   original by: Webtoolkit.info (http://www.webtoolkit.info/)
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: sowberry
			// +    tweaked by: Jack
			// +   bugfixed by: Onno Marsman
			// +   improved by: Yves Sucaet
			// +   bugfixed by: Onno Marsman
			// +   bugfixed by: Ulrich
			// *     example 1: utf8_encode('Kevin van Zonneveld');
			// *     returns 1: 'Kevin van Zonneveld'
			var string = (argString+''); // .replace(/\r\n/g, "\n").replace(/\r/g, "\n");
		  
			var utftext = "";
			var start, end;
			var stringl = 0;
		  
			start = end = 0;
			stringl = string.length;
			for (var n = 0; n < stringl; n++) {
				var c1 = string.charCodeAt(n);
				var enc = null;
		  
				if (c1 < 128) {
					end++;
				} else if (c1 > 127 && c1 < 2048) {
					enc = String.fromCharCode((c1 >> 6) | 192) + String.fromCharCode((c1 & 63) | 128);
				} else {
					enc = String.fromCharCode((c1 >> 12) | 224) + String.fromCharCode(((c1 >> 6) & 63) | 128) + String.fromCharCode((c1 & 63) | 128);
				}
				if (enc !== null) {
					if (end > start) {
						utftext += string.substring(start, end);
					}
					utftext += enc;
					start = end = n+1;
				}
			}
		  
			if (end > start) {
				utftext += string.substring(start, string.length);
			}
		  
			return utftext;
		},
		 
		utf8_decode : function( str_data ) {
			// Converts a UTF-8 encoded string to ISO-8859-1  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/utf8_decode
			// +   original by: Webtoolkit.info (http://www.webtoolkit.info/)
			// +      input by: Aman Gupta
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: Norman "zEh" Fuchs
			// +   bugfixed by: hitwork
			// +   bugfixed by: Onno Marsman
			// +      input by: Brett Zamir (http://brett-zamir.me)
			// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// *     example 1: utf8_decode('Kevin van Zonneveld');
			// *     returns 1: 'Kevin van Zonneveld'
			var tmp_arr = [], i = 0, ac = 0, c1 = 0, c2 = 0, c3 = 0;
			 
			str_data += '';
			 
			while ( i < str_data.length ) {
				c1 = str_data.charCodeAt(i);
				if (c1 < 128) {
					tmp_arr[ac++] = String.fromCharCode(c1);
					i++;
				} else if ((c1 > 191) && (c1 < 224)) {
					c2 = str_data.charCodeAt(i+1);
					tmp_arr[ac++] = String.fromCharCode(((c1 & 31) << 6) | (c2 & 63));
					i += 2;
				} else {
					c2 = str_data.charCodeAt(i+1);
					c3 = str_data.charCodeAt(i+2);
					tmp_arr[ac++] = String.fromCharCode(((c1 & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
					i += 3;
				}
			}
		  
			return tmp_arr.join('');
		},
		 
		trim : function (str, charlist) {
			// Strips whitespace from the beginning and end of a string  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/trim
			// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: mdsjack (http://www.mdsjack.bo.it)
			// +   improved by: Alexander Ermolaev (http://snippets.dzone.com/user/AlexanderErmolaev)
			// +      input by: Erkekjetter
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: DxGx
			// +   improved by: Steven Levithan (http://blog.stevenlevithan.com)
			// +    tweaked by: Jack
			// +   bugfixed by: Onno Marsman
			// *     example 1: trim('    Kevin van Zonneveld    ');
			// *     returns 1: 'Kevin van Zonneveld'
			// *     example 2: trim('Hello World', 'Hdle');
			// *     returns 2: 'o Wor'
			// *     example 3: trim(16, 1);
			// *     returns 3: 6
			var whitespace, l = 0, i = 0;
			str += '';
			 
			if (!charlist) {
				// default list
				whitespace = " \n\r\t\f\x0b\xa0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u200b\u2028\u2029\u3000";
			} else {
				// preg_quote custom list
				charlist += '';
				whitespace = charlist.replace(/([\[\]\(\)\.\?\/\*\{\}\+\$\^\:])/g, '$1');
			}
			 
			l = str.length;
			for (i = 0; i < l; i++) {
				if (whitespace.indexOf(str.charAt(i)) === -1) {
					str = str.substring(i);
					break;
				}
			}
			 
			l = str.length;
			for (i = l - 1; i >= 0; i--) {
				if (whitespace.indexOf(str.charAt(i)) === -1) {
					str = str.substring(0, i + 1);
					break;
				}
			}
			 
			return whitespace.indexOf(str.charAt(0)) === -1 ? str : '';
		},
		 
		rand : function(min, max) {
			// Returns a random number  
			// 
			// version: 1008.1718
			// discuss at: http://phpjs.org/functions/rand
			// +   original by: Leslie Hoare
			// +   bugfixed by: Onno Marsman
			// *     example 1: rand(1, 1);
			// *     returns 1: 1
			 
			var argc = arguments.length;
			if (argc === 0) {
				min = 0;
				max = 2147483647;
			} else if (argc === 1) {
				throw new Error('Warning: rand() expects exactly 2 parameters, 1 given');
			}
			return Math.floor(Math.random() * (max - min + 1)) + min;
		},
		 
		base64_encode: function (data) {
			// Encodes string using MIME base64 algorithm  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/base64_encode
			// +   original by: Tyler Akins (http://rumkin.com)
			// +   improved by: Bayron Guevara
			// +   improved by: Thunder.m
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   bugfixed by: Pellentesque Malesuada
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// -    depends on: utf8_encode
			// *     example 1: base64_encode('Kevin van Zonneveld');
			// *     returns 1: 'S2V2aW4gdmFuIFpvbm5ldmVsZA=='
			// mozilla has this native
			// - but breaks in 2.0.0.12!
			//if (typeof this.window['atob'] == 'function') {
			//    return atob(data);
			//}
				 
			var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
			var o1, o2, o3, h1, h2, h3, h4, bits, i = 0, ac = 0, enc="", tmp_arr = [];
		  
			if (!data) {
				return data;
			}
		  
			data = this.utf8_encode(data+'');
			 
			do { // pack three octets into four hexets
				o1 = data.charCodeAt(i++);
				o2 = data.charCodeAt(i++);
				o3 = data.charCodeAt(i++);
		  
				bits = o1<<16 | o2<<8 | o3;
		  
				h1 = bits>>18 & 0x3f;
				h2 = bits>>12 & 0x3f;
				h3 = bits>>6 & 0x3f;
				h4 = bits & 0x3f;
		  
				// use hexets to index into b64, and append result to encoded string
				tmp_arr[ac++] = b64.charAt(h1) + b64.charAt(h2) + b64.charAt(h3) + b64.charAt(h4);
			} while (i < data.length);
			 
			enc = tmp_arr.join('');
			 
			switch (data.length % 3) {
				case 1:
					enc = enc.slice(0, -2) + '==';
				break;
				case 2:
					enc = enc.slice(0, -1) + '=';
				break;
			}
		  
			return enc;
		},
		 
		base64_decode: function (data) {
			// Decodes string using MIME base64 algorithm  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/base64_decode
			// +   original by: Tyler Akins (http://rumkin.com)
			// +   improved by: Thunder.m
			// +      input by: Aman Gupta
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   bugfixed by: Onno Marsman
			// +   bugfixed by: Pellentesque Malesuada
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: Brett Zamir (http://brett-zamir.me)
			// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// -    depends on: utf8_decode
			// *     example 1: base64_decode('S2V2aW4gdmFuIFpvbm5ldmVsZA==');
			// *     returns 1: 'Kevin van Zonneveld'
			// mozilla has this native
			// - but breaks in 2.0.0.12!
			//if (typeof this.window['btoa'] == 'function') {
			//    return btoa(data);
			//}
		  
			var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
			var o1, o2, o3, h1, h2, h3, h4, bits, i = 0, ac = 0, dec = "", tmp_arr = [];
		  
			if (!data) {
				return data;
			}
		  
			data += '';
		  
			do {  // unpack four hexets into three octets using index points in b64
				h1 = b64.indexOf(data.charAt(i++));
				h2 = b64.indexOf(data.charAt(i++));
				h3 = b64.indexOf(data.charAt(i++));
				h4 = b64.indexOf(data.charAt(i++));
		  
				bits = h1<<18 | h2<<12 | h3<<6 | h4;
		  
				o1 = bits>>16 & 0xff;
				o2 = bits>>8 & 0xff;
				o3 = bits & 0xff;
		  
				if (h3 == 64) {
					tmp_arr[ac++] = String.fromCharCode(o1);
				} else if (h4 == 64) {
					tmp_arr[ac++] = String.fromCharCode(o1, o2);
				} else {
					tmp_arr[ac++] = String.fromCharCode(o1, o2, o3);
				}
			} while (i < data.length);
		  
			dec = tmp_arr.join('');
			dec = this.utf8_decode(dec);
		  
			return dec;
		},
		 
		sprintf : function( ) {
			// Return a formatted string  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/sprintf
			// +   original by: Ash Searle (http://hexmen.com/blog/)
			// + namespaced by: Michael White (http://getsprink.com)
			// +    tweaked by: Jack
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: Paulo Freitas
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +      input by: Brett Zamir (http://brett-zamir.me)
			// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// *     example 1: sprintf("%01.2f", 123.1);
			// *     returns 1: 123.10
			// *     example 2: sprintf("[%10s]", 'monkey');
			// *     returns 2: '[    monkey]'
			// *     example 3: sprintf("[%'#10s]", 'monkey');
			// *     returns 3: '[####monkey]'
			var regex = /%%|%(\d+\$)?([-+\'#0 ]*)(\*\d+\$|\*|\d+)?(\.(\*\d+\$|\*|\d+))?([scboxXuidfegEG])/g;
			var a = arguments, i = 0, format = a[i++];
		  
			// pad()
			var pad = function (str, len, chr, leftJustify) {
				if (!chr) {chr = ' ';}
				var padding = (str.length >= len) ? '' : Array(1 + len - str.length >>> 0).join(chr);
				return leftJustify ? str + padding : padding + str;
			};
		  
			// justify()
			var justify = function (value, prefix, leftJustify, minWidth, zeroPad, customPadChar) {
				var diff = minWidth - value.length;
				if (diff > 0) {
					if (leftJustify || !zeroPad) {
						value = pad(value, minWidth, customPadChar, leftJustify);
					} else {
						value = value.slice(0, prefix.length) + pad('', diff, '0', true) + value.slice(prefix.length);
					}
				}
				return value;
			};
		  
			// formatBaseX()
			var formatBaseX = function (value, base, prefix, leftJustify, minWidth, precision, zeroPad) {
				// Note: casts negative numbers to positive ones
				var number = value >>> 0;
				prefix = prefix && number && {'2': '0b', '8': '0', '16': '0x'}[base] || '';
				value = prefix + pad(number.toString(base), precision || 0, '0', false);
				return justify(value, prefix, leftJustify, minWidth, zeroPad);
			};
		  
			// formatString()
			var formatString = function (value, leftJustify, minWidth, precision, zeroPad, customPadChar) {
				if (precision != null) {
					value = value.slice(0, precision);
				}
				return justify(value, '', leftJustify, minWidth, zeroPad, customPadChar);
			};
		  
			// doFormat()
			var doFormat = function (substring, valueIndex, flags, minWidth, _, precision, type) {
				var number;
				var prefix;
				var method;
				var textTransform;
				var value;
		  
				if (substring == '%%') {return '%';}
		  
				// parse flags
				var leftJustify = false, positivePrefix = '', zeroPad = false, prefixBaseX = false, customPadChar = ' ';
				var flagsl = flags.length;
				for (var j = 0; flags && j < flagsl; j++) {
					switch (flags.charAt(j)) {
						case ' ': positivePrefix = ' '; break;
						case '+': positivePrefix = '+'; break;
						case '-': leftJustify = true; break;
						case "'": customPadChar = flags.charAt(j+1); break;
						case '0': zeroPad = true; break;
						case '#': prefixBaseX = true; break;
					}
				}
		  
				// parameters may be null, undefined, empty-string or real valued
				// we want to ignore null, undefined and empty-string values
				if (!minWidth) {
					minWidth = 0;
				} else if (minWidth == '*') {
					minWidth = +a[i++];
				} else if (minWidth.charAt(0) == '*') {
					minWidth = +a[minWidth.slice(1, -1)];
				} else {
					minWidth = +minWidth;
				}
		  
				// Note: undocumented perl feature:
				if (minWidth < 0) {
					minWidth = -minWidth;
					leftJustify = true;
				}
		  
				if (!isFinite(minWidth)) {
					throw new Error('sprintf: (minimum-)width must be finite');
				}
		  
				if (!precision) {
					precision = 'fFeE'.indexOf(type) > -1 ? 6 : (type == 'd') ? 0 : undefined;
				} else if (precision == '*') {
					precision = +a[i++];
				} else if (precision.charAt(0) == '*') {
					precision = +a[precision.slice(1, -1)];
				} else {
					precision = +precision;
				}
		  
				// grab value using valueIndex if required?
				value = valueIndex ? a[valueIndex.slice(0, -1)] : a[i++];
		  
				switch (type) {
					case 's': return formatString(String(value), leftJustify, minWidth, precision, zeroPad, customPadChar);
					case 'c': return formatString(String.fromCharCode(+value), leftJustify, minWidth, precision, zeroPad);
					case 'b': return formatBaseX(value, 2, prefixBaseX, leftJustify, minWidth, precision, zeroPad);
					case 'o': return formatBaseX(value, 8, prefixBaseX, leftJustify, minWidth, precision, zeroPad);
					case 'x': return formatBaseX(value, 16, prefixBaseX, leftJustify, minWidth, precision, zeroPad);
					case 'X': return formatBaseX(value, 16, prefixBaseX, leftJustify, minWidth, precision, zeroPad).toUpperCase();
					case 'u': return formatBaseX(value, 10, prefixBaseX, leftJustify, minWidth, precision, zeroPad);
					case 'i':
					case 'd':
						number = parseInt(+value, 10);
						prefix = number < 0 ? '-' : positivePrefix;
						value = prefix + pad(String(Math.abs(number)), precision, '0', false);
						return justify(value, prefix, leftJustify, minWidth, zeroPad);
					case 'e':
					case 'E':
					case 'f':
					case 'F':
					case 'g':
					case 'G':
						number = +value;
						prefix = number < 0 ? '-' : positivePrefix;
						method = ['toExponential', 'toFixed', 'toPrecision']['efg'.indexOf(type.toLowerCase())];
						textTransform = ['toString', 'toUpperCase']['eEfFgG'.indexOf(type) % 2];
						value = prefix + Math.abs(number)[method](precision);
						return justify(value, prefix, leftJustify, minWidth, zeroPad)[textTransform]();
					default: return substring;
				}
			};
		  
			return format.replace(regex, doFormat);
		},
		 
		clone : function (mixed) {
			 
			var newObj = (mixed instanceof Array) ? [] : {};
			for (i in mixed) {
				if (mixed[i] && (typeof mixed[i] == "object") ) {
					newObj[i] = lostnote.util.clone(mixed[i]);
				} else {
					newObj[i] = mixed[i];
				}
			}
			return newObj;
		},
		 
		strtolower : function( str ) {
			 
			return (str+'').toLowerCase();
		},
		 
		in_array : function(needle, haystack, argStrict) {
			// Checks if the given value exists in the array  
			// 
			// version: 1008.1718
			// discuss at: http://phpjs.org/functions/in_array
			// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +   improved by: vlado houba
			// +   input by: Billy
			// +   bugfixed by: Brett Zamir (http://brett-zamir.me)
			// *     example 1: in_array('van', ['Kevin', 'van', 'Zonneveld']);
			// *     returns 1: true
			// *     example 2: in_array('vlado', {0: 'Kevin', vlado: 'van', 1: 'Zonneveld'});
			// *     returns 2: false
			// *     example 3: in_array(1, ['1', '2', '3']);
			// *     returns 3: true
			// *     example 3: in_array(1, ['1', '2', '3'], false);
			// *     returns 3: true
			// *     example 4: in_array(1, ['1', '2', '3'], true);
			// *     returns 4: false
			var key = '', strict = !!argStrict;
		  
			if (strict) {
				for (key in haystack) {
					if (haystack[key] === needle) {
						return true;
					}
				}
			} else {
				for (key in haystack) {
					if (haystack[key] == needle) {
						return true;
					}
				}
			}
		  
			return false;
		},
		 
		dechex: function (number) {
			// Returns a string containing a hexadecimal representation of the given number  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/dechex
			// +   original by: Philippe Baumann
			// +   bugfixed by: Onno Marsman
			// +   improved by: http://stackoverflow.com/questions/57803/how-to-convert-decimal-to-hex-in-javascript
			// +   input by: pilus
			// *     example 1: dechex(10);
			// *     returns 1: 'a'
			// *     example 2: dechex(47);
			// *     returns 2: '2f'
			// *     example 3: dechex(-1415723993);
			// *     returns 3: 'ab9dc427'
			if (number < 0) {
				number = 0xFFFFFFFF + number + 1;
			}
			return parseInt(number, 10).toString(16);
		},
		 
		explode: function (delimiter, string, limit) {
			// Splits a string on string separator and return array of components. 
			// If limit is positive only limit number of components is returned. 
			// If limit is negative all components except the last abs(limit) are returned.  
			// 
			// version: 1009.2513
			// discuss at: http://phpjs.org/functions/explode
			// +     original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +     improved by: kenneth
			// +     improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +     improved by: d3x
			// +     bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// *     example 1: explode(' ', 'Kevin van Zonneveld');
			// *     returns 1: {0: 'Kevin', 1: 'van', 2: 'Zonneveld'}
			// *     example 2: explode('=', 'a=bc=d', 2);
			// *     returns 2: ['a', 'bc=d']
		  
			var emptyArray = { 0: '' };
			 
			// third argument is not required
			if ( arguments.length < 2 ||
				typeof arguments[0] == 'undefined' ||
				typeof arguments[1] == 'undefined' ) {
				return null;
			}
		  
			if ( delimiter === '' ||
				delimiter === false ||
				delimiter === null ) {
				return false;
			}
		  
			if ( typeof delimiter == 'function' ||
				typeof delimiter == 'object' ||
				typeof string == 'function' ||
				typeof string == 'object' ) {
				return emptyArray;
			}
		  
			if ( delimiter === true ) {
				delimiter = '1';
			}
			 
			if (!limit) {
				return string.toString().split(delimiter.toString());
			} else {
				// support for limit argument
				var splitted = string.toString().split(delimiter.toString());
				var partA = splitted.splice(0, limit - 1);
				var partB = splitted.join(delimiter.toString());
				partA.push(partB);
				return partA;
			}
		}   
	}
}
function fileModel(){
    this.select=function(msg){
	    if(msg){
		    //if multiple
			if(msg.multi){
			    msg.url=[];
			    //get multi urls
				$('.file').each(function(k,v){
					if($(this).attr('checked')=='checked'){
						msg.url.push($(this).attr("value"));
					}
				});
				if(msg.url.length==0){
					lostnote.say({'title':'No File Selected!','msg':"Please Select At Least One File!"});
					return false;
				}
				msg.url=jQuery.toJSON(msg.url);
			}
			if(msg.window!='top'){
				jQuery('iframe[id^='+msg.window+']').contents().find('input[name='+msg.target+']:visible').val(msg.url);
			}else{
			    if(msg.multi){
				    jQuery('textarea[name='+msg.target+']').val(msg.url);
				}else{
					jQuery('input[name='+msg.target+']:visible').val(msg.url);
				}
				/* if(lostnote.exist('textarea[name='+msg.target+']')){
				    var result=tinyMCE.execCommand('mceInsertRawHTML',false,'<img src="'+msg.url+'"/>');
				} */
			}
			//if preview
			if(!msg.multi&&lostnote.exist('#'+msg.target+'_preview')){
				jQuery('#'+msg.target+'_preview').attr({"src":msg.url});
			}
			var data={'title':'Select Done!','msg':"select done!"};
			lostnote.say(data);
		}else{
		    if(!SESSION.msg.window){
			    SESSION.msg.window='top';
			}
		}
	}
	this.add=function(){
	    if(SESSION.msg.step=='done'){
		    if(!SESSION.msg.window){
			    SESSION.msg.window='top';
			}
			jQuery.each(GET,function(k,v){//alert('<a msg="file/target/'+info.target+'/entity/'+v.id+'.insertEntity">dddddd'+v.name+'</a>');
			    jQuery('#file_add .file:eq('+k+')').find('input').replaceWith('<span style="float:left;clear:both;"><span class="warm">click to insert:</span><a onclick="file.select({&quot;url&quot;:&quot;'+FILE+lostnote.tool.urldecode(v.path)+'&quot;,&quot;target&quot;:&quot;'+SESSION.msg.target+'&quot;,&quot;window&quot;:&quot;'+SESSION.msg.window+'&quot;});">'+v.name+'</a></span>');
				//alert('jame'+k);
			});
		    return true;
		}else if(lostnote.exist('#file_add')){
	        jQuery('#file_add').find('.file:first').clone().insertBefore('#file_add .file:first');
			var index=parseInt(jQuery('#file_add').find('.file:eq(1)').attr('index'))+1;
			jQuery('#file_add').find('.file:first').attr({"index":index,"id":"file"+index}).find('input').attr({"name":"file"+index});
			jQuery("#file"+index).append('<a class="close">X</a>').find('a').click(function(){
				jQuery("#file"+index).remove();
				jQuery(this).remove();
			});
		    return true;
		}
	}
	this.link=function(){
		if(lostnote.exist('#file_link')){
			if(jQuery('#file_link input:eq(0)').val()==''){
				lostnote.say({'title':'URL Error!','msg':"Please Input a Valid File URL!"});
				return true;
			}else{
				var msg=SESSION.msg;
				msg['url']=jQuery('#file_link input:eq(0)').val();
				this.select(msg);
				return true;
			}
		}
	}
}
var lostnote=new lostnote();
var file=new fileModel();
lostnote.prepare();
//other functions for lostnote
jQuery.fn.bgPosition = function(x,y,multiple,add,get){
	var position=[];
	if(typeof(jQuery(this).css("background-position"))!='undefined'){
		position=jQuery(this).css("background-position").split(" ");
	}else if(typeof(jQuery(this).css("background-position-x"))!='undefined'){
		position[0]=jQuery(this).css("background-position-x");
		position[1]=jQuery(this).css("background-position-y");
	}else{
            return true;
	}
        position[0]=parseInt(position[0]);
        position[1]=parseInt(position[1]);
        if(typeof(x)=='undefined'){return position[0]+"px "+position[1]+'px';}
	if(!add){add=0}
	if(!multiple){multiple=0;}else{if(add==0){add=1;}}
        if(typeof(x)!='string'&&typeof(x)!='undefined'){position[0]=x-multiple*jQuery(this).width()+add*position[0];}
        if(typeof(y)!='string'&&typeof(y)!='undefined'){position[1]=y-multiple*jQuery(this).height()+add*position[1];}
        if(get=='true'){
        	return position[0]+"px "+position[1]+'px';
        }
        jQuery(this).css("background-position",position[0]+"px "+position[1]+'px');
}
String.prototype.trim   =   function(){   
  return   this.replace(/(^\s*)|(\s*$)/g,"");   
}
//object to json
jQuery.extend({
   /** * @see 将json字符串转换为对象 * @param json字符串 * @return 返回object,array,string等对象 */
   evalJSON: function(strJson) {
     return eval("(" + strJson + ")");
   }
});
jQuery.extend({
   /** * @see 将javascript数据类型转换为json字符串 * @param 待转换对象,支持object,array,string,function,number,boolean,regexp * @return 返回json字符串 */
   toJSON: function(object) {
     var type = typeof object;
     if ('object' == type) {
       if (Array == object.constructor) type = 'array';
       else if (RegExp == object.constructor) type = 'regexp';
       else type = 'object';
     }
     switch (type) {
     case 'undefined':
     case 'unknown':
       return;
       break;
     case 'function':
     case 'boolean':
     case 'regexp':
       return object.toString();
       break;
     case 'number':
       return isFinite(object) ? object.toString() : 'null';
       break;
     case 'string':
       return '"' + object.replace(/(\\|\")/g, "\\$1").replace(/\n|\r|\t/g, function() {
         var a = arguments[0];
         return (a == '\n') ? '\\n': (a == '\r') ? '\\r': (a == '\t') ? '\\t': ""
       }) + '"';
       break;
     case 'object':
       if (object === null) return 'null';
       var results = [];
       for (var property in object) {
         var value = jQuery.toJSON(object[property]);
         if (value !== undefined) results.push(jQuery.toJSON(property) + ':' + value);
       }
       return '{' + results.join(',') + '}';
       break;
     case 'array':
       var results = [];
       for (var i = 0; i < object.length; i++) {
         var value = jQuery.toJSON(object[i]);
         if (value !== undefined) results.push(value);
       }
       return '[' + results.join(',') + ']';
       break;
     }
   }
});