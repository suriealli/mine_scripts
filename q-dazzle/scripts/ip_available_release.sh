#!/bin/sh
#use this script to know the ip in the list's available

date=`date +%m-%d-%H:%M`
if [ ! -d  result ];then
/bin/mkdir -p result
fi
echo -e "IP\t\t\t总发送包\t总接收包\t接收率\t\t平均延时\t最大延迟\t位置"|tee -a ./result/result_$date.log
for i in `ls ./log|grep ./*ping.log`
do
	ip=`echo $i |awk -F_ '{print $1}'`
	addr=`echo $i |awk -F_ '{print $2" "$3}'`
	rece_sum=`/bin/cat  ./log/$i|grep -v "+\|min\|ping"|awk '{sum+=$6} END {print sum}'`
	send_sum=`/bin/cat ./log/$i|grep -v "+\|min\|ping"|awk '{sum+=20} END {print sum}'`
	rec_percent=`echo "scale=2;$rece_sum*100/$send_sum"|bc -l`"%"
	totle_time=`/bin/cat  ./log/$i|grep -v "+\|min\|ping"|awk '{time=$6*$4}{sum+=time} END {printf "%d",sum}'`
	max_time=`/bin/cat ./log/$i|grep -v "+\|min\|ping"|awk '{max=max>$3?max:$3} END {print max}'`
	if [ $rece_sum -ne 0 ];then
	avg_time=`echo "scale=2;$totle_time/$rece_sum"|bc -l`
	else 
	avg_time=0
	fi

#	echo $totle_time $rece_sum $avg_time
        echo -e $ip"\t\t"$send_sum"\t\t"$rece_sum"\t\t"$rec_percent"\t\t$avg_time\t\t$max_time\t\t$addr"|tee -a ./result/result_$date.log
done

