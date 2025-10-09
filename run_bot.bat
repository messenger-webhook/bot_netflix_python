@echo off
:: === Auto Refresh Bot Netflix ===
:: Dossier du bot
cd /d "C:\Users\LENOVO\Desktop\bot_netflix_python"

:: Date et heure pour le log
set DATETIME=%date%_%time%
set DATETIME=%DATETIME::=-%
set DATETIME=%DATETIME: =_%
set DATETIME=%DATETIME:/=-%
set DATETIME=%DATETIME:.=-%

:: Exécution du script et enregistrement du log
echo =============================== >> logs.txt
echo Lancement du bot à %date% %time% >> logs.txt
python auto_refresh_token.py >> logs.txt 2>&1
echo Fin d'exécution à %date% %time% >> logs.txt
echo =============================== >> logs.txt
echo. >> logs.txt

:: Fin
exit
