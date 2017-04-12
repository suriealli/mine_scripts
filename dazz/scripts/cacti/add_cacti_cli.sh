#/bin/sh
#to add a cacti client

help(){
	echo "$0 ip地址"
	exit
}
if [ $# -lt 1 ];then
	help
fi
add_cacti_cli(){
	command1="/bin/cat /etc/snmp/snmpd.conf|grep 183.61.119.173"
	command2="sed -i '63i com2sec notConfigUser 183.61.119.173    dazzle0312' /etc/snmp/snmpd.conf;/usr/bin/sudo /etc/init.d/snmpd restart"
	snmp=`ssh -i /ssqy/center/0/rsync/key/dazzle/dazzle_rsa -p62919 -ldazzle $1 "/usr/bin/sudo $command1"`
	
	if [[ "$snmp" == "" ]];then
		ssh -i /ssqy/center/0/rsync/key/dazzle/dazzle_rsa -p62919 -ldazzle $1 "/usr/bin/sudo $command2"
	else 
		echo $snmp
		
	fi
}






for i in $@;
do
add_cacti_cli $i
done
exit
