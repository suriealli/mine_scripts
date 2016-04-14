#/bin/sh
#author by suriealli
#开服时间默认为明天10:00
#带域名，开服时间检查
start_time=`date +"%s"`
CURRENTPATH=`pwd`

center=`pwd|awk -F/ '{print $3"/"$4}'`

#确认下是否执行
echo -e "将新增$1平台$2服，从$center上更新，确认？（Enter确定，任意字符退出)" 
read act
if [[ ! "$act" == "" ]];then
        echo "用户取消操作，操作终止"
        exit
fi

#帮助信息
help(){ 
	echo ”带域名检查及开服时间检查，默认开服时间为明天10:00“
	echo "使用：========$0 平台名 服务器号 ================"

}

#检查当前用户
checkUser(){
user=`whoami`
if [ $user != "root" ];then
        echo "permission deny"
        exit
fi
}

#检查开服时间以及域名解析
checkConf(){
#/usr/bin/php $CURRENTPATH/ssqy_srv_handle.php create_all_rsync_conf
name=`cat $CURRENTPATH/conf/$1/$1_s$2.conf|grep C_ServerIP|awk -F= '{print $2}'`
ip=`cat $CURRENTPATH/conf/$1/$1_s$2.conf|grep S_IP|grep -v CROSS|awk -F= '{print $2}'`
data=`/bin/ping -A -c 4 $name 2>&1`
host=`echo $data|grep "unknow"|grep -v "^$"|awk '{print $4}'`
  if [ -z $host ];then
       host_ip=`echo $data|grep PING|awk '{print $3}'|awk -F\( '{print $2}' |awk -F\) '{print $1}'`
       if [ $host_ip = $ip ];then
            echo "域名解析正确！"
       else
            echo "域名解析错误！是否继续？(任意字符退出)"
	    read -p "" select1
            if [[  "$select1" != "" ]];then
                 exit
            fi
       fi 
  else 
	echo "域名未解析！是否继续？(任意字符退出)"
	read -p "" select2
        if [[  "$select2" != "" ]];then
                exit
        fi
  fi
day=`date +%d`
#开服时间设置
opentime="`date -d '1 day' +%Y-%m-%d` 10:00:00"

cur_opentime=`cat $CURRENTPATH/conf/$1/$1_s$2.conf|grep S_OPENDAY|awk -F= '{print $2}'`
if [[ "$opentime" == "$cur_opentime" ]];then
	echo "开服时间正确!"
else 
	echo -e "开服时间不正确，当前开服时间为：$cur_opentime\n请检查！(是否继续)"
	read -p "" select3
        if [[  "$select3" != "" ]];then
                exit
        fi
fi
}


#开服操作
add_new_game(){
	$CURRENTPATH/remote_exe.sh add_new_srv $1 $2 game_srv
	wait
	$CURRENTPATH/remote_exe.sh add_new_srv $1 $2 log_srv
	wait
	$CURRENTPATH/gengxin.sh $1 $2 no_db_gengxin_without_qingdang
	wait
	$CURRENTPATH/gengxin.sh $1 $2 sqlgamelog
	wait
	$CURRENTPATH/gengxin.sh $1 $2 start
	wait
	$CURRENTPATH/gengxin.sh $1 $2 status

}

#检查更新结果
checkresult(){
TDATE=`date '+%Y-%m-%d'`
LOGPATH="${CURRENTPATH}/log_gengxin/${TDATE}_log"
grep "失败\|不正确\|错" ${LOGPATH}/$1-$2-*
grep "失败\|不正确\|错" $CURRENTPATH/log_add_new_srv/$1-$2*

}
#检查所带参数
if [ $# -lt 2 ];then 
	help
	exit
fi


#正式执行
checkUser
checkConf $1 $2 
add_new_game $1 $2 2>&1
checkresult $1 $2 

end_time=`date +"%s"`
minute=$(( (${end_time} - ${start_time})/60 ))
second=$(( (${end_time} - ${start_time})%60 ))
echo "执行$0时间：${minute}分${second}秒"
