#!/bin/sh

read -p "Enter the plat name:" plat
read -p "Enter the ip:" s_ip
read -p "Enter the host name:" host_name

run_in_version(){
	[ -z `grep ${s_ip} /data/admin/etc/cvmlists/game.conf` ] && echo -e "\t#{$host_name}\nroot@10.104.232.123:22">> /data/admin/etc/cvmlists/game.conf
	[ -z `grep ${s_ip} /etc/hosts` ] && echo -e "${s_ip}\t ${host_name}"  >> /etc/hosts
	ssh-copy-id root@s_ip
}

run_for_new_srv(){
	#升级一些包
	command="yum install -y gdb wget lrzsz xz;rpm -Uvh http://mirrors.kernel.org/fedora-epel/6/i386/epel-release-6-8.noarch.rpm"
	ssh ${s_ip} $command


	echo "时区部分请自行处理，现今服务器上做的时间服务器是："
	command1="crontab -l|grep ntpdate"
	ssh ${s_ip} $command1


	#有些运营商可能有apf策略，删除
	command2="[ -f /etc/cron.daily/apf ] && rm /etc/cron.daily/apf;[-d /etc/apf/] && rm -rf /etc/apf/"
	ssh ${s_ip} $command2

 
	#关闭selinux，修改防火墙，先删除防火墙策略，策略可参照其他服务器的/etc/sysconfig/iptables文件，
	command3="sed -i \"s/HOSTNAME=.*/HOSTNAME=${host_name}/\" /etc/sysconfig/network;sed -i \"s#SELINUX=.*#SELINUX=disabled#\" /etc/sysconfig/selinux;sed -i 's#LANG=.*#LANG=\"en_US.UTF-8\"#' /etc/sysconfig/i18n"
	ssh ${s_ip} $command3

}

#传输文件过去
rsync_file(){
	command="/bin/mkdir -p /data/{admin,games}"
	ssh $host_name ${command}
	/usr/bin/rsync -a --delete --exclude-from=/data/admin/etc/sync/GS_exclude.conf /data/games/GS root@${s_ip}:/data/games/

	/usr/bin/rsync -a /data/admin root@${host_name}:/data/

	command1="echo \"${plat}\" > /data/games/GS/PyCode/ENV.txt"
	ssh ${s_ip} ${command1}
	#开启843端口的某个功能，写入到/etc/rc.loacl开机自启：
	command2="cd /data/games/GS/PyCode/Policyd && nohup python FlashPolicyd.py --file=FlashPolicy.xml --port=843 &;echo \'cd /data/games/GS/PyCode/Policyd && nohup python FlashPolicyd.py --file=FlashPolicy.xml --port=843 &\'>>/etc/rc.local"
	ssh ${s_ip} ${command2}
}




#基本跑完了，重启机器
echo "防火墙部分请自行配置。"
read -p "机器${s_ip}将被重启，确定重启(Yes/No)?" sel
if [[ "$sel" == "Yes" ]];then
	ssh ${host_name} "reboot"
else
	echo "用户取消。"
	exit 3
fi



