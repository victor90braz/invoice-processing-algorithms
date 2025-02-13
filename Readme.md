## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <https://github.com/victor90braz/invoice-processing-algorithms.git>
   cd <inmaticpart2>
   ```

2. Run the `setup-windows.bat` Script for Windows:
   ```bash
   ./setup-windows.bat
   ```

3. Run the `setup-linux-mac.sh` Script for Linux or macOS:
   ```bash
   ./setup-linux-mac.sh
   ```

This will:
- Create and activate a virtual environment (`myenv`).
- Install required dependencies such as Django.
- Optionally create a new Django project if it doesn't exist.
- Apply any pending migrations to your database.
- Start the Django development server at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

To start the server:

```bash
python manage.py runserver
```

---

Running Migrations:

```bash
python manage.py migrate
```

---

## Creating a Test

To create a test:

1. Create a file called `tests.py` in your app directory if it doesn't already exist.

2. Add your test case to the `tests.py` file:

   ```python
   from django.test import TestCase

   class SimpleTest(TestCase):
       def test_basic(self):
           self.assertEqual(1 + 1, 2)
   ```

---

## Running Tests

To run your tests:

```bash
python manage.py test
```

---

## Running Tests for a Specific App

To run tests for a specific app (e.g., `myapp`), use:

```bash
python manage.py test myapp
```

---

## Running a Specific Test Method

To run a specific test method from a test case, use this format:

```bash
python manage.py test myapp.tests.TestClass.test_method
```

---

## Generating Test Coverage Report in HTML

Install the `coverage` package if it's not already installed:

   ```bash
   pip install coverage
   ```

Run the tests with coverage:

   ```bash
   python -m coverage html
   ```