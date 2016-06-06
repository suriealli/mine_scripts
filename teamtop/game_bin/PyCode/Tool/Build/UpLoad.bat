@ECHO OFF

ECHO ftp>command.txp
ECHO ^^O$11;`)_FWz>>command.txp
ECHO cd LongQiHelp>>command.txp
ECHO put BuildAS3.py>>command.txp
ECHO put BuildAS3.bat>>command.txp
ECHO close>>command.txp
ECHO quit>>command.txp
ftp -i -s:command.txp 192.168.8.108

DEL command.txp
ECHO UpLoad Success!
PAUSE