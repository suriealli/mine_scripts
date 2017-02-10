#!/bin/bash
#write by suriealli
#run by crond
#filename:network_monitor.sh
#ipfilename:./IPlist
#
cur_dir=`pwd`
scr_dir=`dirname $0`
cd $scr_dir
date=`date +%Y%m%d-%H:%M:%S`
ipfile='./IPlist'
mkdir -p log
if [ ! -f $iplist ];then
	exit
fi
iplist=`cat $ipfile|awk '{print $1}'|grep -v '#'|grep -v '^$'`


#ping 整个ip列表
function Ping_ip
{

for i in $iplist
do
  per_ip_file=./log/${i}_`cat IPlist|grep $i|awk '{print $2"_"$3}'`_ping.log
  if [ ! -f $per_ip_file ];then
	echo "$i ping值分析">>$per_ip_file
	echo -e "date\t\t\tmin\t\tmax\t\tavg\t\tmdev\t\tRecevied_pak\t\tLoss_percent">>$per_ip_file
  fi
  #ping后的数据
  ping_data=`/bin/ping -A -c $1 $i |grep "rtt\|received"`
  
  rece_pak=`echo $ping_data|awk '{print $4}'`
  if [ $rece_pak -eq 0 ];then
        min_time=0
	max_time=0
	avg_time=0
	mdev_time=0
        loss_percent="100%"
  elif [ -z "`echo $ping_data|grep "duplicates"`" ];then
  min_time=`echo $ping_data|awk '{print $14}'|awk -F/ '{print $1}'`
  max_time=`echo $ping_data|awk '{print $14}'|awk -F/ '{print $3}'`
  avg_time=`echo $ping_data|awk '{print $14}'|awk -F/ '{print $2}'`
  mdev_time=`echo $ping_data|awk '{print $14}'|awk -F/ '{print $4}'`
  loss_percent=`echo $ping_data|awk '{print $6}'`
  elif [ -n "`echo $ping_data|grep "duplicates"`" ];then
#  echo $ping_data
  min_time=`echo $ping_data|awk '{print $16}'|awk -F/ '{print $1}'`
  max_time=`echo $ping_data|awk '{print $16}'|awk -F/ '{print $3}'`
  avg_time=`echo $ping_data|awk '{print $16}'|awk -F/ '{print $2}'`
  mdev_time=`echo $ping_data|awk '{print $16}'|awk -F/ '{print $4}'`
  loss_percent=`echo $ping_data|awk '{print $8}'`
  fi
  
#将数据格式化保存到文件中 
  echo -e "$date\t$min_time\t\t$max_time\t\t$avg_time\t\t$mdev_time\t\t$rece_pak\t\t\t$loss_percent">>$per_ip_file
  if_trac_ip=0 #是否要对该IP进行traceroute，0否，1是
  per_ip_trac=./log/${i}_`cat IPlist|grep $i|awk '{print $2"_"$3}'`_traceroute.log
  #丢包时
  if [ $loss_percent != '0%' -a  $loss_percent != '100%' ];then   
	if_trac_ip=1
  fi
  #延迟过大，或者波动过大
  if [ `echo $max_time|awk -F. '{print $1}'` -ge `/bin/cat $ipfile|grep $i|awk '{print $4}'` -o `echo $mdev_time|awk -F. '{print $1}'` -ge $2 ];then
	if_trac_ip=1
  fi
  #对需要追踪的ip进行追踪
  if [ $if_trac_ip -eq 1 ];then
	echo $date >> $per_ip_trac
	/usr/sbin/mtr  -c 4 -n $i --report  >>$per_ip_trac
  fi

done 
}
#如超过指定值，则进行traceroute
#参数说明：ping的次数	平均偏差值
Ping_ip 20 30
cd $cur_dir
