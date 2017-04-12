#!/bin/bash


game_name=$1
action=$2
plat=$3
sn=$4
file=$5


if [[ "$game_name" == "ssqy" ]];then
        db_format=${plat}_${sn}_${game_name}_${action}
else
        db_format=${game_name}_${plat}_${sn}_${action}
fi

ERROR_PRINT()
{
	echo "本脚本用于跨平台回档，一个游戏服数据迁移到另一个游戏服时，可使用本脚本，备份文件名使用备份标准格式，使用原备份文件名即可"
        echo "使用格式：./huidang.sh 游戏名 数据库类型 平台 游戏服 使用回档文件"
        echo "======./huidang.sh ssqy game uc 1 a.tar.gz====="
        echo "======./huidang.sh g2 game mixed 1 a.tar.gz===="
        echo "======./huidang.sh fshx game mixed 1 a.tar.gz=="
        exit
}

exe_huidang_game()
{
tar xf $file
cd `echo $file|awk -F. '{print $1}'`
/bin/cat ./* >> game_huidang.sql
/usr/bin/mysql -uroot -pUQEnZcVXdjzA3uZC $db_format < game_huidang.sql
/bin/rm -rf ../`echo $file|awk -F. '{print $1}'`
}


if [ $# -ne 5 ];then
	ERROR_PRINT
fi
exe_huidang_game


