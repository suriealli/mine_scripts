#!/bin/sh

start_time=`date +"%s"`
script_path=`dirname $0`
cd  $script_path
file="migrate_rsync.conf"
game_name="ssqy"
module_name=$1

TMPFILE=$$.fifo
mkfifo $TMPFILE
exec 6<>$TMPFILE
rm -f $TMPFILE
PARALLEL=5
mkdir -p ./log

exe_migrate_fu_rsync(){
    plat=`echo $plat_sn|awk -F- '{print $1}'`
    sn=`echo $plat_sn|awk -F- '{print $2}'`
    ip=`cat migrate_rsync.conf|awk '{if($1==plat_sn)print $2}' plat_sn=$plat_sn`
    local_ip=`cat migrate_rsync.conf|awk '{if($1==plat_sn)print $3}' plat_sn=$plat_sn`
    /bin/sh ./migrate_rsync.sh ${game_name} ${plat} ${sn} ${ip} ${local_ip} ${module_name}>> ./log/${game_name}_${plat}_${sn}_${ip}_${local_ip}_${module_name}.log
}

add_rsync_module(){
    plat=`echo $plat_sn|awk -F- '{print $1}'`
    sn=`echo $plat_sn|awk -F- '{print $2}'`
    ip=`grep $plat_sn $file|awk '{print $2}'`
    local_ip=`grep $plat_sn $file|awk '{print $3}'` 

    command="[[ \`grep ${game_name}_${plat}_${sn}_$1 /etc/rsyncd.conf\` == \"\" ]] && sudo cp -f /etc/rsyncd.conf /etc/rsyncd.conf.bak_`date +%s`;sudo echo -e \"\n[${game_name}_${plat}_${sn}_$1]\npath = /${game_name}/${plat}/${sn}/$1/\nread only = no\nwrite only = yes\nlist = no\nauth users = root\nsecrets file = /etc/rsyncd.password\nuid = root\ngid = root\n\"|sudo tee -a /etc/rsyncd.conf && sudo mkdir -p /${game_name}/${plat}/${sn}/$1"
#    command="sudo cp -f /etc/rsyncd.conf /etc/rsyncd.conf.bak_`date +%s`;sudo echo -e \"\n[${plat}_${sn}_$1]\npath = /${game_name}/${plat}/${sn}/out/$1/\nread only = no\nwrite only = yes\nlist = no\nauth users = root\nsecrets file = /etc/rsyncd.password\nuid = root\ngid = root\n\"|sudo tee -a /etc/rsyncd.conf && sudo mkdir -p /${game_name}/${plat}/${sn}/out/$1"
#    echo $command
    ssh -i /data/key/dazzle_rsa -ldazzle -p62919 ${local_ip} "$command"
}




if [ $# -ne 1 ];then
	echo "$0 module_name"
	exit
fi



for ((i=0;i<${PARALLEL};i++))
do
    echo
done >&6

for plat_sn in `cat ${file}|awk '{print $1}'|grep -v '#'`
do

    if [[ "$module_name" == "add_module" ]];then
	for i in web log data;do
	add_rsync_module $i
	done
	continue
    fi

    read <&6
    (
        exe_migrate_fu_rsync
        echo >&6
    )&
done
wait
exec 6>&-

end_time=`date +"%s"`
minute=$(( (${end_time} - ${start_time})/60 ))
second=$(( (${end_time} - ${start_time})%60 ))
echo "执行时间：${minute}分${second}秒"
exit
