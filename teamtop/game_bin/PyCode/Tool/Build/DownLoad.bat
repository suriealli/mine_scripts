@ECHO OFF

ECHO anonymous>command.txp
ECHO pwd>>command.txp
ECHO cd LongQiHelp>>command.txp
ECHO get BuildAS3.py>>command.txp
ECHO get BuildAS3.bat>>command.txp
ECHO close>>command.txp
ECHO quit>>command.txp
ftp -i -s:command.txp 192.168.8.108

DEL command.txp
ECHO UpLoad Success!
PAUSE