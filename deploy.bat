@echo off
chcp 65001 > nul

REM 檢查是否已初始化git倉庫
if not exist .git (
    echo 正在初始化git倉庫...
    git init
)

REM 添加所有文件
echo 正在添加文件到暫存區...
git add .

REM 提交更改
set /p commit_msg=請輸入提交訊息: 
echo 正在提交更改...
git commit -m "%commit_msg%"

REM 推送到遠端倉庫
echo 正在推送到GitHub...
git remote add origin https://github.com/aken1023/Role-playing-AI-Dialogue.git
git push -u origin master

echo 上傳完成！
pause