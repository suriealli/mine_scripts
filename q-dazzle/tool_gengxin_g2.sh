#!/bin/sh

#进入到更新目录
cd /g2/centerg2/0/rsync/

date=`date +%m%d%H%M`

#调用
help(){
	echo "$0 managertool all   更新兰陵王全平台managertool"
	echo "$0  gametool   all   更新兰陵王全平台gametool"
	echo "$0 managertool 平台名1 平台名2    分别更新各平台managertool"
	echo "$0  gametool   平台名1 平台名2    分别更新各平台gametool"
	exit
}

#更新全服的managertool
gengxin_all_managertool(){
for i in mixed youmi 49app apple tw aiyou lewan 49pt yuenan kor ty zz kakao ios;do
echo "===========================================更新$i平台managertool=============================================="
echo $date >> /home/suriealli/log/managertool/g2_${i}_managertool.log
/g2/centerg2/0/rsync/gengxin.sh $i manager managertool 2>&1|tee /home/suriealli/log/managertool/g2_${i}_managertool.log
done
}


#更新全服的gametool
gengxin_all_gametool(){
for i in mixed youmi 49app apple tw aiyou lewan 49pt yuenan kor ty zz ios;do
echo "=========================================================更新$i平台gametool==========================================="
check_plat $i
/usr/local/php/bin/php g2_srv_handle.php create_server_list_conf $i
tmp=`cat dlplat_sn|grep -v $i`
if [ -n $tmp ];then
	echo "服列表不正确，请检查服列表！$i"
	exit
fi
echo $date >>/home/suriealli/log/gametool/g2_${i}_gametool.log
/g2/centerg2/0/rsync/qf_gengxin.sh gametool 2>&1|grep "log\|err" >>/home/suriealli/log/gametool/g2_${i}_gametool.log
done
}

#生成G2所有配置
create_all_rsync_conf(){
	sed -i "s#\$g_game_config\['id'\] = 2;#\$g_game_config\['id'\] = 4;#" /g2/centerg2/0/rsync/g2_srv_handle.php
	/usr/local/php/bin/php g2_srv_handle.php create_all_rsync_conf
	sed -i "s#\$g_game_config\['id'\] = 2;#\$g_game_config\['id'\] = 4;#" /g2/centerg2/0/rsync/g2_srv_handle.php
	/usr/local/php/bin/php g2_srv_handle.php create_all_rsync_conf
}

#检查平台，修改gameid
check_plat(){
	if [[ "$1" == "paojiao" || "$1" == "49pt" || "$1" == "lewan" || "$1" == "aiyou" || "$1" == "yntest" || "$1" == "yuenan" || "$1" == "wp" || "$1" == "tyx" || "$1" == "xkor" || "$1" == "kor" || "$1" == "ty" || "$1" == "yncenter" ]];then
        sed -i "s#\$g_game_config\['id'\] = 2;#\$g_game_config\['id'\] = 4;#" /g2/centerg2/0/rsync/g2_srv_handle.php
        else
        sed -i "s#\$g_game_config\['id'\] = 4;#\$g_game_config\['id'\] = 2;#" /g2/centerg2/0/rsync/g2_srv_handle.php
        fi
}

if [ $# -lt 1 ];then
	help
elif [[ "$1" == "managertool" ]];then
	if [[ "$2" == "all" ]];then
	   echo "将更新兰陵王全平台的managertool，继续？(任意字符退出)"
	   read -p "" select
	   if [[ $select != "" ]];then
		 echo "用户取消操作"
       		 exit
	   fi
	 #  create_all_rsync_conf
	   gengxin_all_managertool
	else
	   echo "将更新兰陵王$@平台的managertool，继续？(任意字符退出)"
           read -p "" select
           if [[ $select != "" ]];then
                 echo "用户取消操作"
                 exit
           fi
	  # create_all_rsync_conf
	   for i in $@;do
	   if [[ "$i" == "$1" ]];then
		continue
	   fi
	   echo "============================================更新$i managertool=============================="
	   echo $date >> /home/suriealli/log/managertool/g2_${i}_managertool.log
	   /g2/centerg2/0/rsync/gengxin.sh $i manager managertool 2>&1|grep "log\|err" >>/home/suriealli/log/managertool/g2_${i}_managertool.log
	   done
	fi
elif [[ "$1" == "gametool" ]];then
	if [[ "$2" == "all" ]];then
	   echo "将更新兰陵王全平台的gametool，继续？(任意字符退出)"
           read -p "" select
           if [[ $select != "" ]];then
		 echo "用户取消操作"
                 exit
           fi
	   #create_all_rsync_conf
	   gengxin_all_gametool
	else
	   echo "将更新兰陵王$@平台的gametool，继续？(任意字符退出)"
           read -p "" select
           if [[ $select != "" ]];then
                 echo "用户取消操作"
                 exit
           fi
	  # create_all_rsync_conf
	   for i in $@;do
		echo "===============================更新$i平台gametool============================================"
		check_plat $i
		/usr/local/php/bin/php g2_srv_handle.php create_server_list_conf $i
		tmp=`cat dlplat_sn|grep -v $i`
		if [ -n $tmp ];then
        		echo "服列表不正确，请检查服列表！$i"
       			exit
		fi
		echo $date >> /home/suriealli/log/gametool/g2_${i}_gametool.log
		/g2/centerg2/0/rsync/qf_gengxin.sh gametool 2>&1|grep "log\|err" >>/home/suriealli/log/gametool/g2_${i}_gametool.log
	   done   
	fi
fi
