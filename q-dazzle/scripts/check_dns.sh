#!/bin/sh
for i in `/bin/cat dns_name_list|awk '{print $1}'|grep -v "^$"`
do
	data=`/bin/ping -A -c 4 $i 2>&1`

	host=`echo $data|grep "unknow"|grep -v "^$"|awk '{print $4}'`
#	echo $data
	if [ -z $host ];then
		host_ip=`echo $data|grep PING|awk '{print $3}'|awk -F\( '{print $2}' |awk -F\) '{print $1}'`
#		echo $host_ip
		if [[ $host_ip == `/bin/cat dns_name_list|grep $i|awk '{print $2}'` ]];then

			echo -e $i "\t" $host_ip "\t\t解析正确！"
		else
			echo -e $i "\t" $host_ip "\t解析错误！\t应为:"`/bin/cat dns_name_list|grep $i|awk '{print $2}'`
		fi
		continue
		
	fi
	echo -e "$host \t\t `cat dns_name_list|grep $host|awk '{print $2}'`\t未解析！"

done	
