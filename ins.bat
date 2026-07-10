@echo off
chcp 65001 > nul

if not exist "env" (
    python -m venv env
) else (
    echo Виртуальное окружение env уже существует.
)

call env\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt