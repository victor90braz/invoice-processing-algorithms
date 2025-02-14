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

Activate a virtual environment (`myenv`)

```bash
.\myenv\Scripts\Activate.ps1
```

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

## Running Tests

To run tests for a specific app (e.g., `inmaticpart2`), use:

```bash
python manage.py test inmaticpart2.tests
```

---

## Running a Specific Test Method

To run a specific test method from a test case, use this format:

```bash
python manage.py test inmaticpart2.tests.unit.test_invoice_processor
```

---

## Generating Test Coverage Report in HTML

Install the `coverage` package if it's not already installed:

   ```bash
   pip install coverage
   ```

Run the tests with coverage:

   ```bash
   coverage run --source=inmaticpart2 manage.py test inmaticpart2
   coverage report
   coverage html
   ```