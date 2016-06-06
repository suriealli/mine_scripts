/**
 * UserInterface 用户接口
 * need jQuery library
 * @lostnote
 * example use: UI.date(obj)
 */
 
function UserInterface(){
	this.init=function(){
		//init select value
		$('select').each(function(){
			if($(this).attr('val')){
				$(this).val($(this).attr('val'));
			}
		});
	}
	this.tab=function(group,id){
		$('div[id^='+group+'_details]:visible').hide();
		$('div[id='+group+'_details_'+id+']:hidden').show();
		$('a[id^='+group+'_anchor]').removeClass('active');
		$('a[id='+group+'_anchor_'+id+']').addClass('active');
	}
    //检查表单
    this.check=function(formname){
	    var errors='';
		//先保存编辑器内容
		if(typeof(tinyMCE)!='undefined'){tinyMCE.triggerSave();}
	    $('form[name='+formname+'] textarea,form[name='+formname+'] input').each(function(){
		    if($(this).attr('check')){
			    var value=$(this)[0].value;
				
				if($(this).attr('forname')){
				    if($("input[name="+$(this).attr('name')+"]:checked").length<1){
					    value='';
					}
				}
			    var label='<span style="color:blue;">'+$(this).attr('label')+"</span>";
			    switch($(this).attr('check')){
				    case "required":
					    if(value.length==''){
                            if($(this).attr('forname')){
							    errors+=label+"为必选！ ";
							}else{
						        errors+=label+"不能为空！ ";
							}
						}
					break;
					case "datetime":
					    var reg = /^(\d{4})(-|\/)(\d{2})\2(\d{2}) (\d{2}):(\d{2}):(\d{2})$/;
                        var r =value.match(reg);
                        if(r==null){
						    errors+=label+"正确格式为：2012-05-21 00:00:00！";
						}
					break;
				}
			}
		});
		if(errors.length>0){
		    $('p[id=errors]').remove();
		    $('body').prepend("<p id='errors'><br /><span style='color:red'>"+errors+"</span><br /><br /></p>");
		}else{
		    $('form[name='+formname+']').submit();
		}
	}
	//全选复选框
    this.checkAll=function(selector){
	    $(selector).click(function(){
		    var name=$(this).attr('forname');
			if($(this).attr("checked")){
				$('input[type=checkbox][name="'+name+'"]').each(function(){
					$(this).attr({"checked":true});
				});
			}else{
				$('input[type=checkbox][name="'+name+'"]').each(function(){
					$(this).attr({"checked":false});
				});
			}
		});
	}
    this.date=function(selector){
	    var format="yyyy-MM-dd HH:mm:ss";
	    this.getLibrary(["/site_medias/js/datetime/WdatePicker.js"],function(){
			$(selector).each(function(){
			    if($(this).attr('format')){
				    format=$(this).attr('format');
				}
			    $(this).parent().append('&nbsp;&nbsp;<img onClick="WdatePicker({el:&quot;'+$(this).attr('id')+'&quot;,dateFmt:&quot;'+format+'&quot;})" src="/site_medias/js/datetime/skin/datePicker.gif" width="16" height="22" align="absmiddle" style="cursor:pointer" />');
			});
		});
    }
	this.edit=function(){
	    this.getLibrary(["templates/js/editor/tiny_mce.js"],function(){
		    tinyMCE.init({
				theme : "advanced",
				mode : "textareas",
				width: "100%",
				height: "100",
				language: "cn",
				theme_advanced_buttons1 : "bold,italic,seperator,forecolor,backcolor,seperator,link,unlink",
				theme_advanced_buttons2 : "",
				theme_advanced_buttons3 : ""
			});
		});
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
	this.toggle=function(selector){
	    $(selector).slideToggle();
	}
	this.setSwitch=function(name){
	    $('#'+name+'_switch').unbind('click').click(function(){
			if($('#'+name).css('display')=="block"){
				$('#'+name+'_display').val("none");
			}else{
				$('#'+name+'_display').val("block");
			}
			UI.toggle('#'+name);
		});
	}
	this.remove=function(selector){
	    $(selector).remove();
	}
	this.exist=function(selector){
	    if(jQuery(selector).size()>0){
		    return jQuery(selector).size();
		}
	}
}
var UI=new UserInterface();