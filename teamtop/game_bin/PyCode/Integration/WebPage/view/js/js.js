// JavaScript Document
function getobj(itemid){
	return document.getElementById(itemid)
}

function isUndefined(variable) {
	return typeof variable == 'undefined' ? true : false;
}

function Fun_PubSwitch_V(itemid){
	if (getobj(itemid).style.visibility == "hidden") {
		getobj(itemid).style.visibility = "";
	}
	else{
		getobj(itemid).style.visibility = "hidden";
	}
}


function autoswitch (itemid){
	if (getobj(itemid).style.display != "")getobj(itemid).style.display = "";
	else getobj(itemid).style.display = "none";
}

function changClass(Front,id,count,de_class,indexclass,show){
	
	for(i=1;i<=count;i++){
		getobj(Front + i).className = de_class;
		if (show != false){
			getobj(Front + "S_" + i).style.display = "none";
		}
	}
	
	getobj(Front + id).className = indexclass;
	if (show != false){
		getobj(Front + "S_" + id).style.display = "";
	}
}


function allchangClass(form,itemid,de_class,indexclass){
	var form = getobj(form);
	var item_arr = form.getElementsByTagName('div');
    for (var i=0;i<item_arr.length;i++){
		var e = item_arr[i];
		if (e.title == 'sidebar_items')
			e.className = de_class;
	}
	getobj(itemid).className = indexclass;
}


function onechangClass(itemid,de_class,indexclass){
	if (getobj(itemid).className == de_class){
		getobj(itemid).className = indexclass;
	}
	else{
		getobj(itemid).className = de_class;
	}
}

