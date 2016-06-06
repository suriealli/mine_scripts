#!/bin/sh

#plat="yy"
#hostname="lqyy_game5"
read -p "Enter the plat name:" plat
read -p "Enter the ip:" s_ip
read -p "Enter the host name:" host_name
read  -sp "Enter the host  password:" passwd
echo ""

#sed -i "s/HOSTNAME=.*/HOSTNAME=${host_name}/" /etc/sysconfig/network
#sed -i "s#SELINUX=.*#SELINUX=disabled#" /etc/sysconfig/selinux
#sed -i "s#LANG=.*#LANG=\"en_US.UTF-8\"#" /etc/sysconfig/i18n
ssh -p

