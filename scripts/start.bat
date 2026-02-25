@echo off
REM Dermo-CRM - Script de démarrage Windows

echo ==========================================
echo Dermo-CRM - Demarrage
echo ==========================================

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Lancer l'application
python run.py

pause
