# TeamBoard

TeamBoard is a Django REST Framework backend for an AI-powered, business-to-business knowledge-base API.

Companies can register, receive an automatically generated API key, log in to obtain a JWT access token, search a curated technical knowledge base, and have their API usage recorded. Platform administrators can view aggregated usage statistics.

## Features

- Company registration
- Automatic Company profile creation using a Django signal
- Secure API-key generation
- JWT-based authentication
- Company login
- Protected knowledge-base searching
- Case-insensitive search across questions and answers
- Atomic query logging
- Admin-only usage dashboard
- PostgreSQL database running through Docker
- Repeatable knowledge-base seed command
- Exported Postman collection with automated tests

## Technology Stack

- Python
- Django
- Django REST Framework
- Django REST Framework SimpleJWT
- PostgreSQL
- Docker Compose
- Psycopg
- python-dotenv
- Postman

## Project Structure

```text
teamboard/
├── api/
│   ├── management/
│   │   └── commands/
│   │       └── seed_kb.py
│   ├── migrations/
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── postman/
│   └── TeamBoard.postman_collection.json
├── teamboard/
│   ├── settings.py
│   └── urls.py
├── .env.example
├── .gitignore
├── compose.yaml
├── manage.py
├── README.md
└── requirements.txt
```

## Data Models

### Company

Represents a registered business customer.

Each Company has:

- A one-to-one relationship with Django's built-in User model
- A company name
- A unique API key
- A role of either `client` or `admin`
- A creation timestamp

A Company profile is created automatically whenever a new Django User is created.

### KBEntry

Represents one knowledge-base question and answer.

Each entry contains:

- A question
- An answer
- A category
- A creation timestamp

Supported categories are:

- `api`
- `database`
- `cloud`
- `framework`
- `general`

### QueryLog

Records every valid knowledge-base query.

Each log contains:

- The company that made the request
- The submitted search term
- The number of matching results
- The query timestamp

Queries returning zero results are still logged because they consume platform resources.

## Prerequisites

Install:

- Python 3.12 or compatible version
- Docker
- Docker Compose
- Git

## Clone the Repository

```bash
git clone <your-github-repository-url>
cd Team-Board
```

## Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Generate a Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Update `.env`:

```dotenv
DJANGO_SECRET_KEY=replace-with-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=teamboard
POSTGRES_USER=teamboard_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

## Start PostgreSQL

```bash
docker compose up -d
```

Check container health:

```bash
docker compose ps
```

If port `5432` is already in use, either stop the locally installed PostgreSQL service:

```bash
sudo systemctl stop postgresql
```

or change the host port in `.env`:

```dotenv
POSTGRES_PORT=5433
```

## Apply Database Migrations

```bash
python manage.py migrate
```

Verify the application migration:

```bash
python manage.py showmigrations api
```

## Seed the Knowledge Base

```bash
python manage.py seed_kb
```

The first run creates the initial entries:

```text
Knowledge base seeding complete: 12 created, 0 already existed.
```

Running it again does not create duplicates:

```text
Knowledge base seeding complete: 0 created, 12 already existed.
```

## Run the Development Server

```bash
python manage.py runserver
```

The server is available at:

```text
http://127.0.0.1:8000
```

## Authentication

Protected endpoints use JWT authentication.

Send the access token using:

```http
Authorization: Bearer <access-token>
```

Registration and login are public endpoints. Every other endpoint requires a valid JWT unless a stricter custom permission applies.

## API Endpoints

### Register Company

```text
POST /api/auth/register/
```

Request:

```json
{
  "username": "acmecorp",
  "password": "securepass123",
  "company_name": "Acme Corp",
  "email": "dev@acmecorp.com"
}
```

Successful response:

```json
{
  "username": "acmecorp",
  "company_name": "Acme Corp",
  "api_key": "automatically-generated-api-key",
  "access": "jwt-access-token"
}
```

### Login

```text
POST /api/auth/login/
```

Request:

```json
{
  "username": "acmecorp",
  "password": "securepass123"
}
```

Successful response:

```json
{
  "access": "jwt-access-token",
  "company_name": "Acme Corp",
  "api_key": "company-api-key"
}
```

### Query Knowledge Base

```text
POST /api/kb/query/
```

Requires a JWT.

Request:

```json
{
  "search": "JWT"
}
```

Successful response:

```json
{
  "search": "JWT",
  "count": 3,
  "results": [
    {
      "id": 5,
      "question": "What is a JWT access token?",
      "answer": "A JWT access token is a signed credential...",
      "category": "api"
    }
  ]
}
```

A query returning no results still returns `200 OK`:

```json
{
  "search": "unknown subject",
  "count": 0,
  "results": []
}
```

### Usage Summary

```text
GET /api/admin/usage-summary/
```

Requires a JWT belonging to a Company with the `admin` role.

Successful response:

```json
{
  "total_queries": 10,
  "active_companies": 2,
  "top_search_terms": [
    {
      "search_term": "JWT",
      "count": 4
    },
    {
      "search_term": "Django",
      "count": 3
    }
  ]
}
```

A regular client receives:

```text
403 Forbidden
```

## Making a Company an Admin

For local testing:

```bash
python manage.py shell
```

```python
from api.models import Company

company = Company.objects.get(user__username="acmecorp")
company.role = Company.Role.ADMIN
company.save(update_fields=["role"])

exit()
```

Log in again and use the returned access token to call the usage-summary endpoint.

## Postman Collection

The exported Postman collection is located at:

```text
postman/TeamBoard.postman_collection.json
```

It contains tests for:

- Successful registration
- Duplicate registration
- Successful login
- Invalid login
- Query without authentication
- Successful knowledge-base query
- Query with zero matches
- Blank search validation
- Usage summary without authentication
- Client access to the admin endpoint
- Admin access to the usage summary

Import the collection into Postman and set:

```text
base_url = http://127.0.0.1:8000
```

Do not commit active JWT tokens inside the exported collection.

## Design Decisions

### Secure defaults for authentication

JWT authentication and `IsAuthenticated` are configured globally. This ensures every new API endpoint is protected unless it is explicitly made public.

Only registration and login override the global authentication settings because users need those endpoints to obtain a token.

### API-key creation through a signal

The Company profile and API key are created through a `post_save` signal on Django's User model. This keeps profile creation consistent regardless of whether a user is created through the registration endpoint, Django admin, a management command, or the Django shell.

The registration view updates the Company name but never generates the API key manually.

### Atomic knowledge-base logging

The knowledge-base search and QueryLog creation are wrapped in `transaction.atomic()`.

This keeps usage tracking tied to the successful query operation. Searches returning zero results are also logged because the API request still consumes platform resources.

### Custom admin role

Admin access is controlled through `Company.role`, not Django's `is_staff` or `is_superuser`.

The custom `IsAdminUser` permission checks whether the authenticated user's Company has the `admin` role.

## Running Checks

```bash
python manage.py check
python manage.py showmigrations
```

## Stopping PostgreSQL

```bash
docker compose down
```

To also delete the local PostgreSQL volume and its data:

```bash
docker compose down -v
```

Use the `-v` option carefully because it permanently removes the local database contents.
