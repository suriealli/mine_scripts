#!/bin/sh
#将自己home目录下的文件传播到另外的服务器的脚本

help()
{
echo $0 "IP地址1   IP地址2"
exit
}
if [ $# -lt 1 ];then
help
fi

cd /home/suriealli
tar czf ./suriealli.tar.gz ./*

command="sudo mv -f /home/dazzle/suriealli.tar.gz /home/suriealli/ && sudo tar xf /home/suriealli/suriealli.tar.gz -C /home/suriealli/ && sudo rm -rf /home/suriealli/suriealli.tar.gz"
for i in $@;do

	scp -rp -i /data/key/dazzle_rsa -P62919 /home/suriealli/suriealli.tar.gz dazzle@$i:/home/dazzle/
	ssh -i  /data/key/dazzle_rsa -ldazzle -p62919 $i "$command"

done

rm -rf ./suriealli.tar.gz
