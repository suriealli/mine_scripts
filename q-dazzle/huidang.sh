#!/bin/bash


game_name=$1
db_format=`echo $2|awk -F. '{print $1}'|awk -F_ '{print $1 "_" $2 "_" $3 "_" $4}'`
file=$2

ERROR_PRINT()
{
	echo "本脚本用于同个游戏服回档、迁服回档，文件名格式必须为备份文件的标准格式"
        echo "=============使用格式：./huidang.sh 游戏名 使用回档文件==============="
        echo "===============-===./huidang.sh ssqy a.tar.gz========================="
        echo "===================./huidang.sh g2 a.tar.gz==========================="
        echo "===================./huidang.sh fshx a.tar.gz========================="
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


if [ $# -ne 2 ];then
	ERROR_PRINT
fi
exe_huidang_game


