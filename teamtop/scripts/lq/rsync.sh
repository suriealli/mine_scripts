#!/bin/sh
#only for longqi
Help(){
	echo "             $0 PLAT ID start|status   启动或查看状态，启动前会自动检查状态，如运行中，则终止"
	echo "             $0 PLAT ID qingdang       未实现"
	echo "             $0 PLAT ID data           备份data 数据库"
	echo "             $0 PLAT global globaldata 备份global 数据库"
	exit
}

GetConf()
{
	echo `grep "^$2=" $1 | awk 'BEGIN{FS="="} { for(i=2;i<=NF;i++) if(i==2) { printf "%s",$i } else { printf "=%s",$i } }' | sed 's#/#\\\/#g' | sed 's#"#\\\"#g' | tr -d '\r' `
}

make_conf(){
	[ ! -f $conf_file ] && echo "配置文件$conf_file不存在。请检查" && exit 3
	Server_id=`GetConf $conf_file Server_id`
	Server_name=`GetConf $conf_file Server_name`
	Server_site=`GetConf $conf_file Server_site`
	GHL_name=`GetConf $conf_file GHL_name`
	D_name=`GetConf	$conf_file	D_name`
	GHL_port=`GetConf $conf_file GHL_port`
	D_port=`GetConf $conf_file D_port`
	public_ip=`GetConf	$conf_file public_ip`
	intranet_ip=`GetConf $conf_file	intranet_ip`
	mysql_db=`GetConf $conf_file	mysql_db`
	mysql_ip=`GetConf $conf_file    mysql_ip`
	mysql_user=`GetConf $conf_file	mysql_user`
	mysql_passwd=`GetConf $conf_file	mysql_passwd`
	mysql_port=`GetConf $conf_file	mysql_port`
	merge_zids=`GetConf $conf_file merge_zids`
}

exe_back_data(){
	db_name="role_sys_${1}_${id}"
	Tdate=`date +%Y-%m-%d-%H-%M-%S`
	bak_dir="$script_path/mysql_bak/`date +%Y-%m-%d`/${plat}_${db_name}_${Tdate}/"
	Result="fail"
	TableList=`echo "SHOW TABLES;"| mysql -h${mysql_ip} -u${mysql_user} -p${mysql_passwd} -P${mysql_port} ${db_name} 2>/dev/null | grep -v "Tables_in_" `
	[[ "$TableList" == "" ]] && exit 3;
	mkdir -p ${bak_dir}
	for table in $TableList;do
		mysqldump -h${mysql_ip} -u${mysql_user} -p${mysql_passwd} -P${mysql_port}  --quick --single-transaction ${db_name} ${table} > ${bak_dir}/${table}.sql 2>/dev/null
		if [ $? -eq 0 ];then
			Result="success"
		else
			Result="fail ${table}"
			break
		fi
	done
	cd ${bak_dir}/.. && tar zcf ${plat}_${db_name}_${Tdate}.tar.gz ${plat}_${db_name}_${Tdate}
	rm -rf ${plat}_${db_name}_${Tdate}
	cd ${script_path}
	echo "${Tdate} ${db_name} backup ${Result}!!" 2>&1 
}

exe_status(){
	merge_zids_list=`echo $merge_zids|sed 's#\[##g'|sed 's#\]##g'|sed 's#,# #g'`
    merge_zids_list=(${merge_zids_list// ,/ })
    total_d_proc=`echo ${#merge_zids_list[@]}`
	check_command="ps aux|grep ComplexServer|grep -v grep |grep -E \"GHL $id \"|wc -l"
	GHL_NO=`ssh $host $check_command`
	check_command="ps aux|grep ComplexServer|grep -v grep|grep -E \"D $id`for i in ${merge_zids_list[@]};do echo "|D $i";done` \"|wc -l"
	D_NO=`ssh $host $check_command`
	if [[ "$GHL_NO" == 0 && "$D_NO" == 0 ]];then
		echo -e "#########Server $id \tcan not be found!!!!!"
	else
		echo -e "#########Server $id \tis running! #### process GHL num is $GHL_NO, D num is $D_NO --total:`expr $total_d_proc + 1`"	
		exit		
	fi


}

exe_start(){
	start_command="cd /data/games/GS/Script/ && sh auto_start_${Server_id}\[*\].sh"
	ssh $host $start_command
	[[ "`echo $?`" == "0" ]] && echo "启动完成。"
}


#############################
########start script#########
#############################
cd `dirname $0`
script_path=`pwd`
plat=$1
id=$2
conf_file="$script_path/conf/${plat}_${id}.conf"
global_config="$script_path/global_config.py"
if [ $# -lt 3 ];then
	Help
fi

#读取配置
if [[ "$2" != "global" ]];then
	make_conf
	#从hosts中查找主机名，如没有，则使用公网ip
	host=`grep -E "$intranet_ip|$public_ip" /etc/hosts|awk '{print $2}'|tail -1`
	if [[ "$host" == "" ]];then
		host=$public_ip
	fi
fi
case $3 in
	status)
		exe_status
	;;
	start)
		exe_status
		exe_start
		exe_status
	;;
	data)
		exe_back_data data
	;;
	log)
		exe_back_data log
	;;
	globaldata)
		python $script_path/exec_sql_global.py -s backup -p $plat
	;;
	*)
		Help
	;;
esac
