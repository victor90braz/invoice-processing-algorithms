#!/bin/bash

# Set the project name
PROJECT_NAME="my_django_project"

# Step 1: Ensure Python is installed
echo "[1/12] Ensuring Python is installed..."
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python is not installed. Please install Python 3."
    exit 1
else
    echo "[SUCCESS] Python is installed."
fi

# Step 2: Ensure pip is installed
echo "[2/12] Ensuring pip is installed..."
if ! command -v pip3 &>/dev/null; then
    echo "[ERROR] pip is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install pip!"
        exit 1
    else
        echo "[SUCCESS] pip installed."
    fi
else
    echo "[SUCCESS] pip is installed."
fi

# Step 3: Create a virtual environment
echo "[3/12] Creating a virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment!"
    exit 1
else
    echo "[SUCCESS] Virtual environment created."
fi

# Step 4: Activate the virtual environment
echo "[4/12] Activating the virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Activation failed!"
    exit 1
else
    echo "[SUCCESS] Virtual environment activated."
fi

# Step 5: Upgrade pip
echo "[5/12] Upgrading pip..."
pip install --upgrade pip > /dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to upgrade pip!"
    exit 1
else
    echo "[SUCCESS] pip upgraded!"
fi

# Step 6: Install Django and required dependencies
echo "[6/12] Installing Django and required dependencies..."
pip install django cryptography > /dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Django installation failed!"
    exit 1
else
    echo "[SUCCESS] Django installed!"
fi

# Step 7: Create Django project
echo "[7/12] Creating Django project: $PROJECT_NAME..."
django-admin startproject $PROJECT_NAME .
if [ $? -ne 0 ]; then
    echo "[ERROR] Project creation failed!"
    exit 1
else
    echo "[SUCCESS] Project '$PROJECT_NAME' created!"
fi

# Step 8: Generate requirements.txt
echo "[8/12] Generating requirements.txt..."
pip freeze > requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to generate requirements.txt!"
    exit 1
else
    echo "[SUCCESS] requirements.txt created!"
fi

# Step 9: Run migrations
echo "[9/12] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[ERROR] Migration failed!"
    exit 1
else
    echo "[SUCCESS] Migrations applied!"
fi

# Step 10: Create .gitignore if it doesn’t exist
if [ ! -f .gitignore ]; then
    echo "[10/12] Creating .gitignore..."
    echo ".env" > .gitignore
    echo "[SUCCESS] .gitignore created and configured."
else
    echo "[INFO] .gitignore already exists. Skipping."
fi

# Step 11: Create .env-example if it doesn’t exist
if [ ! -f .env-example ]; then
    echo "[11/12] Creating .env-example..."
    cat <<EOL > .env-example
DB_NAME=inmaticpart2
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
EOL
    echo "[SUCCESS] .env-example created."
else
    echo "[INFO] .env-example already exists. Skipping."
fi

# Step 12: Run the Django development server
echo "[12/12] Running the Django development server..."
python manage.py runserver
