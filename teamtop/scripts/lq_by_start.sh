#!/bin/sh
#write by suriealli/Joklin
#use lonqgi to start the logic server
EXE_start(){
	id=$1

	GHL_NO=`ps aux|grep ComplexServer|grep -v grep |grep -E "GHL $id "|wc -l`
	D_NO=`ps aux|grep ComplexServer|grep -v grep|grep -E "D $id "|wc -l`
	if [[ "$GHL_NO" == 0 && "$D_NO" == 0 ]];then
		[ -f auto_start_${id}\[*\].sh ] && /bin/sh auto_start_${id}\[*\].sh || echo "could not find the Server $id Script";continue
		GHL_NO=`ps aux|grep ComplexServer|grep -v grep |grep -E "GHL $id "|wc -l`
		D_NO=`ps aux|grep ComplexServer|grep -v grep|grep -E "D $id "|wc -l`
		if [[ "$GHL_NO" == 1 && "$D_NO" == 1 ]];then
			echo "Start OK,#### process DHL num is $GHL_NO, D num is $D_NO"
		else
			echo "Start Error,Please Check."
		fi
	else
		echo -e "#########Server $id \tis running! #### process DHL num is $GHL_NO, D num is $D_NO"	
		
	fi

}
EXE_status(){
	id=$1

	GHL_NO=`ps aux|grep ComplexServer|grep -v grep |grep -E "GHL $id "|wc -l`
	D_NO=`ps aux|grep ComplexServer|grep -v grep|grep -E "D $id "|wc -l`
	if [[ "$GHL_NO" == 0 && "$D_NO" == 0 ]];then
		echo -e "#########Server $id \tcan not be found!!!!!"
	else
		echo -e "#########Server $id \tis running! #### process DHL num is $GHL_NO, D num is $D_NO"	
		
	fi


}
if [[ "$#" == 0 ]];then
        echo -e "\t####################"
        echo -e "\tUsage $0 id1 id2"
        echo -e "\t$0 start id1 id2   启动id为id1、id2的服"
        echo -e "\t$0 status [id] 查看[id]是否已经运行，id为空则查看全部"
        echo -e "\t####################"
        exit 3
fi
################

Script_path=`dirname $0`
cd $Script_path

if [[ "$1" == "start" && "$2" != "" ]];then
	for i in ${@:2};do	
	EXE_start $i
	done
elif [[ "$1" == "status" ]];then
	if [[ "$2" == "" ]];then
		for i in `ls|grep auto_start|awk -F_ '{print $3}'|awk -F[ '{print $1}'`;do
			EXE_status $i
		done
	else
		for i in ${@:2};do
			EXE_status $i
		done
	fi
fi