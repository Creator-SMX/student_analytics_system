@echo off
REM 学生消费分析系统启动批处理脚本
REM 此脚本会持续运行应用程序，并在退出后自动重启

echo ===================================
echo 学生消费分析系统自动启动脚本
echo ===================================
echo 正在启动应用程序...
echo 按Ctrl+C可以停止此脚本

echo. > server_status.log

:START_LOOP
  echo [%date% %time%] 启动应用程序... >> server_status.log
  echo [%date% %time%] 启动应用程序...
  
  REM 使用pythonw.exe运行以避免显示控制台窗口
  REM 这里使用python.exe以便查看输出
  python app.py
  
  REM 检查退出代码
  if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] 应用程序正常退出，准备重启... >> server_status.log
    echo [%date% %time%] 应用程序正常退出，准备重启...
  ) else (
    echo [%date% %time%] 应用程序异常退出 (错误代码: %ERRORLEVEL%), 准备重启... >> server_status.log
    echo [%date% %time%] 应用程序异常退出 (错误代码: %ERRORLEVEL%), 准备重启...
  )
  
  REM 等待2秒后重启
  echo [%date% %time%] 2秒后自动重启... >> server_status.log
  echo 2秒后自动重启...
  ping -n 3 127.0.0.1 > nul
  
  echo. >> server_status.log
goto START_LOOP