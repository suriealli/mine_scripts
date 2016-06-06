ulimit -c unlimited
ulimit -n 10240
export PYTHONHOME=/data/games/GS/PyLib
cd ..
cd Bin
./ComplexServer GHL 10002 8999 &> /dev/null < /dev/null &
./ComplexServer D 10002 20002 &> /dev/null < /dev/null &
cd ..
cd Script
