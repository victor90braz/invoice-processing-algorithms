@echo off
title Django Setup Script
color 0A
chcp 65001 > nul

echo =============================================
echo [INFO]    Django Project Setup Script        
echo =============================================

:: Step 1: Ensure pip is installed
echo [1/12] Ensuring pip is installed...
python -m ensurepip
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install pip!
) else (
    echo [SUCCESS] Pip is installed.
)

:: Step 2: Create a virtual environment
echo [2/12] Creating a virtual environment...
python -m venv myenv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment!
) else (
    echo [SUCCESS] Virtual environment created.
)

:: Step 3: Activate the virtual environment
echo [3/12] Activating the virtual environment...
call myenv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Activation failed!
) else (
    echo [SUCCESS] Virtual environment activated.
)

:: Step 4: Upgrade pip
echo [4/12] Upgrading pip...
python -m pip install --upgrade pip > nul
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip!
) else (
    echo [SUCCESS] Pip upgraded!
)

:: Step 5: Install Django and dependencies
echo [5/12] Installing Django and required dependencies...
pip install django cryptography > nul
if %errorlevel% neq 0 (
    echo [ERROR] Django installation failed!
) else (
    echo [SUCCESS] Django installed!
)

:: Step 6: Prompt for project name and create the project if needed
echo.
echo ---------------------------------------------
echo  Enter your Django project name  
echo  (or press Enter to skip)  
echo ---------------------------------------------

set /p projectName=

if not "%projectName%"=="" (
    echo [6/12] Creating Django project: %projectName%...
    where django-admin >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] django-admin not found! Ensure Django is installed.
        exit /b
    )
    django-admin startproject %projectName% .
    if %errorlevel% neq 0 (
        echo [ERROR] Project creation failed!
    ) else (
        echo [SUCCESS] Project '%projectName%' created!
    )
) else (
    echo [INFO] Skipping project creation.
)

:: Step 7: Generate requirements.txt
echo [7/12] Generating requirements.txt...
pip freeze > requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate requirements.txt!
) else (
    echo [SUCCESS] requirements.txt created!
)

:: Step 8: Run migrations
echo [8/12] Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration failed!
) else (
    echo [SUCCESS] Migrations applied!
)

:: Step 9: Create .gitignore if it doesn’t exist
if not exist .gitignore (
    echo [9/12] Creating .gitignore...
    echo .env > .gitignore
    echo [SUCCESS] .gitignore created and configured.
) else (
    echo [INFO] .gitignore already exists. Skipping.
)

:: Step 10: Create .env-example if it doesn’t exist
if not exist .env-example (
    echo [10/12] Creating .env-example...
    (
        echo DB_NAME=inmaticpart2
        echo DB_USER=root
        echo DB_PASSWORD=root
        echo DB_HOST=127.0.0.1
        echo DB_PORT=3306
        echo SECRET_KEY=your-secret-key
        echo DEBUG=True
        echo ALLOWED_HOSTS=127.0.0.1,localhost
    ) > .env-example
    echo [SUCCESS] .env-example created.
) else (
    echo [INFO] .env-example already exists. Skipping.
)

:: Step 11: Final message
echo.
echo =============================================
echo               SETUP COMPLETE
echo                HAPPY CODING!
echo =============================================

:: Step 12: Run the Django server
echo [11/12] Running the Django development server...
python manage.py runserver

