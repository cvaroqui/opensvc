@echo off
call osvcenv.cmd
"%OSVCPYTHONEXEC%" "%OSVCROOT%\lib\svcmgr.py" %*
