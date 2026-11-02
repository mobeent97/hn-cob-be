# HN COB Portal — Backend (`hn-cob-be`)

Backend for the **HN Customer Onboarding (COB) Portal**, built as a **Django monolith**.
It replaces the earlier microservices-based implementation with a single deployable
application organised into modular Django apps.

## Tech Stack

| Concern        | Choice                                   |
|----------------|------------------------------------------|
| Language       | Python 3.12+                             |
| Framework      | Django 5.x                               |
| API            | Django REST Framework                    |
| Database       | PostgreSQL                               |
| Auth           | JWT (via `djangorestframework-simplejwt`) |
| Frontend       | Angular — see [`hn-cob-fe`](https://github.com/mobeent97/hn-cob-fe) |

## Architecture: Microservices → Monolith

Each former microservice becomes a **Django app** inside one project. Apps talk to
each other through in-process service functions instead of HTTP calls, and share
one database (with clear per-app model ownership).

```
hn-cob-be/
├── config/              # Django project: settings (base/dev/staging/prod), urls, wsgi/asgi
├── apps/
│   ├── accounts/        # users, authentication, roles
│   ├── customers/       # customer profiles & KYC data
│   ├── onboarding/      # onboarding workflow / application status
│   ├── documents/       # document upload & verification
│   └── notifications/   # email / SMS notifications
├── requirements/        # base.txt, dev.txt, prod.txt
├── manage.py
└── README.md
```

*(App list is a starting point. Adjust it to match the existing microservices as they are migrated.)*

## Branching Strategy

| Branch        | Purpose                                   | Deploys to  |
|---------------|-------------------------------------------|-------------|
| `development` | Integration branch for day-to-day work    | Dev env     |
| `staging`     | Release candidates for QA / UAT           | Staging env |
| `production`  | Stable, released code only                | Production  |

**Flow:** `feature/*` → PR into `development` → merge into `staging` for testing →
merge into `production` for release. Hotfixes branch from `production` (`hotfix/*`)
and are merged back into `production`, `staging`, and `development`.

## Getting Started

```bash
# clone & switch to the development branch
git clone https://github.com/mobeent97/hn-cob-be.git
cd hn-cob-be
git checkout development

# virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt

# environment variables
cp .env.example .env        # then edit values

# database & run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver   # http://localhost:8000
```

## Environment Variables

| Variable                 | Description                              |
|--------------------------|------------------------------------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` / `staging` / `prod` |
| `SECRET_KEY`             | Django secret key                        |
| `DEBUG`                  | `True` only in development               |
| `ALLOWED_HOSTS`          | Comma-separated hostnames                |
| `DATABASE_URL`           | PostgreSQL connection string             |
| `CORS_ALLOWED_ORIGINS`   | Angular frontend origin(s)               |

## Common Commands

```bash
python manage.py test               # run tests
python manage.py makemigrations     # create migrations
python manage.py startapp <name> apps/<name>   # add a new module
```
