@echo off
:: Step 1: Create a virtual environment
python -m venv myenv

:: Step 2: Activate the virtual environment
call .\myenv\Scripts\activate

:: Step 3: Upgrade pip
python -m pip install --upgrade pip

:: Step 4: Install Django (or any other dependencies)
pip install django

:: Step 5: Install cryptography
pip install cryptography

:: Step 6: Prompt for project name and create the project if needed
echo Enter the name of your Django project (leave blank to skip creation):
set /p projectName=

if not "%projectName%"=="" (
    echo Creating a new Django project: %projectName%
    :: Check if django-admin is available
    where django-admin >nul 2>nul
    if %errorlevel% neq 0 (
        echo django-admin command not found. Please ensure Django is installed properly.
        exit /b
    )
    django-admin startproject %projectName% .
    echo New Django project '%projectName%' created.
) else (
    echo Skipping project creation. Make sure the project is already set up.
)

:: Step 7: Generate requirements.txt
pip freeze > requirements.txt

:: Step 8: Run migrations to apply any unapplied migrations
echo Running migrations...
python manage.py migrate

:: Step 9: Run the Django development server
echo Checking for manage.py...
if exist manage.py (
    echo Running the Django development server...
    python manage.py runserver
) else (
    echo manage.py not found! Make sure you're in the project directory.
)

:: End of script
pause
