#!/bin/sh
#qf_rsync.sh 多线程操作，可指定进程数







nǐ dē




yīng yǚ zhēn làn



script_path=`dirname $0`
cd ${script_path}
mkdir -p log_qf_rsync/
start_gengxin=`date +"%s"`
CDATE=`date '+%Y-%m-%d-%H-%M-%-S'`
ACTION=$(${@// ,/ })
plat=${#ACTION[1]}
sleep 2
TMPFILE=$$.fifo
mkfifo $TMPFILE
exec 6<>$TMPFILE
rm -f $TMPFILE 
PARALLEL=6


for ((i=0;i<${PARALLEL};i++))
do
	echo
done >&6 

if [[ ${ACTION} == 'data' ]];then
for plat_sn in `cat dlplat_sn`
do 
	read <&6 
	(
		exe_stop
		echo >&6
	)&
done   


