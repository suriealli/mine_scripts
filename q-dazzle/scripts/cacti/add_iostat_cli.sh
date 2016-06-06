#!/bin/sh


if [ $# -lt 1 ];then
help
fi
help(){
echo "新增客户端iostat监控：$0 ip地址1 IP地址2"
exit
}


for i in $@;do
	scp -rp -i /ssqy/center/0/rsync/key/dazzle/dazzle_rsa /home/suriealli/scripts/cacti/cacti-iostat-1.5/scripts/ dazzle@$i:/home/dazzle/tmp
	command1="sudo sed -i '\$a \pass .1.3.6.1.3.1 /usr/bin/perl /usr/local/bin/iostat.pl' /etc/snmp/snmpd.conf;sudo /etc/init.d/snmpd restart"
	command2='sudo mv -f /home/dazzle/tmp/* /usr/local/bin/;sudo rm -rf /home/dazzle/tmp'
	command3='sudo chmod 777 /var/spool/cron;sudo echo "*/5 * * * * /bin/sh /usr/local/bin/iostat.sh 2>/dev/null" >> /var/spool/cron/dazzle;sudo chown dazzle:wheel /var/spool/cron/dazzle;sudo /etc/init.d/crond reload;sudo chmod 700 /var/spool/cron;sudo chmod 600 /var/spool/cron/dazzle'
	ssh -i /ssqy/center/0/rsync/key/dazzle/dazzle_rsa -p 62919 -ldazzle $i "$command1"
	ssh -i /ssqy/center/0/rsync/key/dazzle/dazzle_rsa -p 62919 -ldazzle $i "$command2"
	ssh -i /ssqy/center/0/rsync/key/dazzle/dazzle_rsa -p 62919 -ldazzle $i "$command3"
done
