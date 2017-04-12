check_mobileclient(){
md5sum=`/usr/bin/md5sum /$1/$2/0/web/mobileclient/version/remote/version.wvf|awk '{print $1}'`
res=`/bin/cat /$1/$2/0/web/gametool/global/configure/replace.php |grep -A1 \'$3\'|grep http|awk -F\" '{print $2}'`
if [ "$res" == "" ];then
        echo "没有找到CDN源地址，请检查"
        exit
fi
wget -S $res/version/remote/version.wvf
md5sum1=`/usr/bin/md5sum version.wvf|awk '{print $1}'`
if [ "$md5sum1" == "$md5sum" ];then
	echo -e "$md5sum \t $md5sum1"
        echo "$1 $2与CDN对应的version.wvf一致, 可以更新!" 
else
	echo -e "$md5sum \t $md5sum1"
        echo "$1 $2与CDN对应的version.wvf不一致, 不可以更新!"
fi
rm -rf version.wvf
}

help(){
echo "=========$0 游戏名 发布服名 正式服名 =========="
exit

}
if [ $# -ne 3 ];then
        help
elif [ ! -d /$1/$2 ];then
        echo “没有找到对应游戏对应平台”
        exit
fi
check_mobileclient $1 $2 $3  
