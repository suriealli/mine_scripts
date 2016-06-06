sh show.sh $1
ps -ef | grep "ComplexServer $1" | grep -v grep | awk '{print $2}' |xargs  kill

