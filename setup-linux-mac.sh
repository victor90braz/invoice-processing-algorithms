#!/bin/bash

# Step 1: Create a virtual environment
python3 -m venv myenv

# Step 2: Activate the virtual environment
source ./myenv/bin/activate

# Step 3: Upgrade pip
python3 -m pip install --upgrade pip

# Step 4: Install Django (or any other dependencies)
pip install django

# Step 5: Install cryptography
pip install cryptography

# Step 6: Prompt for project name and create the project if needed
read -p "Enter the name of your Django project (leave blank to skip creation): " projectName

if [ -n "$projectName" ]; then
    echo "Creating a new Django project: $projectName"
    # Check if django-admin is available
    if ! command -v django-admin &> /dev/null; then
        echo "django-admin command not found. Please ensure Django is installed properly."
        exit 1
    fi
    django-admin startproject "$projectName" .
    echo "New Django project '$projectName' created."
else
    echo "Skipping project creation. Make sure the project is already set up."
fi

# Step 7: Generate requirements.txt
pip freeze > requirements.txt

# Step 8: Run migrations to apply any unapplied migrations
echo "Running migrations..."
python3 manage.py migrate

# Step 9: Create .gitignore file to ignore .env
echo ".env" > .gitignore
echo ".gitignore file created to ignore .env"

# Step 10: Create .env-example file with example values
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
echo ".env-example file created with example values."

# Step 11: Run the Django development server
if [ -f "manage.py" ]; then
    echo "Running the Django development server..."
    python3 manage.py runserver
else
    echo "manage.py not found! Make sure you're in the project directory."
fi
