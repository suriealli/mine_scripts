ulimit -c unlimited
ulimit -n 10240
export PYTHONHOME=/data/games/GS/PyLib
cd ..
cd Bin
./ComplexServer C 10002 9999 &> /dev/null < /dev/null &
cd ..
cd Script
