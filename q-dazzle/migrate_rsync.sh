#!/bin/sh
start_time=`date +"%s"`
game_name=$1
plat=$2
sn=$3
ip=$4
local_ip=$5
action=$6

if [ $# -ne 6 ];then
	echo "游戏名 平台 服 原来ip 本地ip 目录"
	exit
fi


add_rsync_module(){
    if [[ `grep ${game_name}_${plat}_${sn}_${action} /etc/rsyncd.conf` == "" ]];then
	cp /etc/rsyncd.conf /etc/rsyncd.conf.`date +%s`
	echo "" >> /etc/rsyncd.conf
	echo "[${game_name}_${plat}_${sn}_${action}]">>/etc/rsyncd.conf
	echo "path = /${game_name}/${plat}/${sn}/${action}/">>/etc/rsyncd.conf
	echo "read only = no">>/etc/rsyncd.conf
	echo "write only = yes">>/etc/rsyncd.conf
	echo "list = no">>/etc/rsyncd.conf
	echo "auth users = root">>/etc/rsyncd.conf
	echo "secrets file = /etc/rsyncd.password">>/etc/rsyncd.conf
	echo "uid = root">>/etc/rsyncd.conf
	echo "gid = root">>/etc/rsyncd.conf
    else
	echo "模块已增加"
    fi
}

#add_rsync_module


command="/usr/bin/sudo /usr/bin/rsync --port=7988  -rlptDvzHS  --progress --delete --password-file=/etc/rsyncd.password_client /${game_name}/${plat}/${sn}/${action}/ root@${local_ip}::${game_name}_${plat}_${sn}_${action}/   "
ssh -i /data/key/dazzle_rsa -p62919 -ldazzle ${ip} $command






end_time=`date +"%s"`
minute=$(( (${end_time} - ${start_time})/60 ))
second=$(( (${end_time} - ${start_time})%60 ))
echo "执行时间：${minute}分${second}秒"
exit
