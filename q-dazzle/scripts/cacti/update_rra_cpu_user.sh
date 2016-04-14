#/bin/sh

for i in `ls /usr/local/cacti/cacti/rra|grep  "_cpu_user"`;do 
	cur=`rrdtool info /usr/local/cacti/cacti/rra/$i|grep ".max"|awk -F= '{print $2}'|awk -F+ '{print $2}'`
	if [[ "$cur" == "02" ]];then
		echo "1"
		rrdtool tune /usr/local/cacti/cacti/rra/$i -a cpu_user:1000
	fi
done

