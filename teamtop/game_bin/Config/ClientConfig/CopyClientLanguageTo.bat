
@echo off
:loop
set cho=
set/p cho=1:na  2:tw 3:tuerqi 4:bl 5:fr	6:esp
if "%cho%"=="1" goto startEnglish
if "%cho%"=="2" goto startFT
if "%cho%"=="3" goto startTuErQi
if "%cho%"=="4" goto startpl
if "%cho%"=="5" goto startfr
if "%cho%"=="6" goto startEsp
goto loop
:startEnglish
%python% CopyClientLanguage.py check US_language.txt
pause
exit
:startFT
%python% CopyClientLanguage.py check FT_language.txt
pause
exit
:startTuErQi
%python% CopyClientLanguage.py check Turkish_language.txt
pause
exit
:startpl
%python% CopyClientLanguage.py check PL_language.txt
pause
exit
:startfr
%python% CopyClientLanguage.py check Fr_language.txt
pause
exit
:startEsp
%python% CopyClientLanguage.py check Esp_language.txt
pause
exit
