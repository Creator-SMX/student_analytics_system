# 启动Flask服务器并捕获所有输出
Write-Host "正在启动学生消费分析系统..."
Write-Host "输出将保存到 server.log"

# 启动服务器并捕获所有输出
python -u app.py *> server.log

Write-Host "服务器已退出，退出代码: $LASTEXITCODE"
Write-Host "请查看 server.log 获取详细信息"