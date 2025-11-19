@echo off
REM クイック保存スクリプト - 作業中の変更を即座にローカルコミット
REM 使い方: quick-save.bat "変更内容の説明"

cd /d "%~dp0"

REM 変更があるかチェック
for /f %%i in ('git status --short') do set HAS_CHANGES=1
if not defined HAS_CHANGES (
    echo [OK] 変更なし - コミットの必要はありません
    exit /b 0
)

REM コミットメッセージを取得（引数があればそれを使用、なければタイムスタンプ）
set COMMIT_MSG=%~1
if "%COMMIT_MSG%"=="" (
    for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set DATE_STR=%%c-%%a-%%b
    for /f "tokens=1-2 delims=:. " %%a in ("%time%") do set TIME_STR=%%a:%%b
    set COMMIT_MSG=WIP: 作業保存 %DATE_STR% %TIME_STR%
)

echo.
echo === クイック保存 ===
echo 時刻: %date% %time%
echo.

REM 変更されたファイルを表示
echo [変更されたファイル:]
git status --short
echo.

REM 全てをステージング
git add -A

REM コミット
git commit -m "%COMMIT_MSG%

🤖 Quick save by Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

if errorlevel 1 (
    echo [ERROR] コミットに失敗しました
    exit /b 1
)

echo.
echo [OK] 保存完了！
echo.
echo 最新のコミット:
git log -1 --oneline
echo.
echo --- 復元方法 ---
echo このコミットに戻る: git checkout %hash%
echo 直前に戻る: git reset --soft HEAD~1
echo.

exit /b 0
