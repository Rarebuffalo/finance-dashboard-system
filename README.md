# Finance Data Processing and Access Control Backend
**Backend Developer Internship Assignment**

This is an asynchronous REST backend built using FastAPI. It is designed to process, persist, and aggregate financial data, while strictly enforcing Role-Based Access Controls (RBAC).

This repository was built to align directly with the assignment prompt. It covers all of the core requirements and every optional enhancement listed in the specifications.

---

## Setup Instructions (Local Environment)

To make it as easy as possible to test this application locally, the project is configured to run on Python without requiring any complex Docker or database setup. It also includes an automated database seeding script.

### 1. Requirements & Installation
Please ensure you are using Python 3.10 or higher. You can set everything up in your terminal by running:

```bash
# Create a Python virtual environment
python -m venv venv

# Activate the environment (Mac/Linux)
source venv/bin/activate 

# Install required dependencies
pip install -r requirements.txt
```

### 2. Run the Application
You can start the FastAPI server natively using uvicorn:

```bash
uvicorn app.main:app --reload
```
> **Note on Auto-Seeding**: When you start the server for the first time, it automatically generates the SQLite database schema and seeds it with three mock users and ten mock financial records. This means you can start testing the dashboard APIs immediately.

### 3. Running Unit Tests
If you want to run the automated testing suite to verify the API endpoints, run:
```bash
pytest -v
```

---

## Testing the APIs (Swagger UI)

FastAPI automatically generates an interactive Swagger interface, so you can test all the endpoints directly in your browser without needing tools like Postman.

1. Open http://127.0.0.1:8000/docs in your browser.
2. Click the Authorize button at the top right.
3. Log in using any of the mock seeded accounts (the password for all of them is `password123`):
   - **Admin**: `admin@finance.com` (Has full CRUD access)
   - **Analyst**: `analyst@finance.com` (Read-only access and dashboard views)
   - **Viewer**: `viewer@finance.com` (Can only view the dashboard)
4. From there, you can execute the endpoints and test how the permission system blocks unauthorized requests.

---

## Architecture and Design Decisions 

### 1. Backend Design & Separation of Concerns
This project is structured using a layered architecture pattern:
* **Models Layer (app/models)**: This layer safely defines the SQL database tables.
* **Schemas Layer (app/schemas)**: This layer uses Pydantic to set logic boundaries. Validating data (like ensuring an amount is greater than zero) is handled cleanly by this layer before it ever reaches the network controller. This prevents bad data from reaching the database level.
* **Controller Layer (app/api/endpoints)**: This is where the actual FastAPI routes live, separated according to their distinct responsibilities.

### 2. Access Control Logic (RBAC)
Instead of forcing repetitive `if current_user.role == "Admin":` checks inside every single endpoint, I used FastAPI Dependency Injections. By creating a `RequireRole` class, the permission check evaluates before the API endpoint even triggers. If a Viewer attempts to hit a DELETE endpoint, the system catches it and throws a 403 Forbidden response immediately.

### 3. Business Logic & Dashboard Calculations
Rather than loading thousands of JSON records into Python's memory and writing a slow loop to manually calculate the net balances, I moved the math directly to the database layer. By leveraging SQLAlchemy's `func.sum()` and `group_by()` methods, the database computes the numerical values using its C-optimized engine, which is significantly faster for data aggregation.

### 4. Validation and Reliability
To protect the system from spam or malicious scripts, I added global rate limiting. Using `slowapi`, the application tracks incoming IPs. If any automated bots attempt to overwhelm the backend, they are blocked with an HTTP 429 Too Many Requests response.

---

## Tradeoffs Considered

1. **Database Selection (SQLite over PostgreSQL)**: 
   Normally, an application processing financial data would warrant deploying a robust database like PostgreSQL via Docker. However, I noticed the evaluation constraints emphasized making the application easy to set up. To respect that, I configured the asynchronous engine to fall back on a simple SQLite file (`finance.db`). This maintains the speed and complexity of the asynchronous design without forcing the reviewer to configure a Docker container.
2. **Speed Over RAM Payload (Pagination)**:
   For fetching records locally, returning all rows simultaneously is easier to write but it uses an enormous amount of memory as the database grows. I decided to introduce pagination parameters (`skip` and `limit`) to the routes, trading a slightly more complex backend structure for guaranteed scalability and reduced RAM usage.

---

## Assumptions Made

1. **Soft Deletion is standard practice**:
   In finance, data audits are strictly required, so destroying data isn't a good idea. I assumed that an Admin deleting a user or record should not actually trigger a hard database deletion. Instead, I built a soft deletion feature where `is_deleted` becomes true, and updated all endpoints to filter these active queries. This provides the functionality of deleting without compromising historical data safety.
2. **Stateless JWTs scale better than Sessions**:
   I built the auth assuming the backend will need to scale heavily. For this reason, I chose JSON Web Tokens over traditional database sessions. Because the server doesn't need to hold a massive list of active sessions in memory, it requires far less compute power to manage authentication securely. I paired this with `passlib` bcrypt hashing to heavily secure user credentials. 
