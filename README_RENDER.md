# SRMCEM Event Portal — GitHub + Render

This repository is a Django event portal. The production configuration uses Render PostgreSQL, WhiteNoise, Gunicorn/Uvicorn and a Render Blueprint.

## Local setup

```powershell
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_app_admin --username admin --email your-email@example.com --password ChangeThisPassword
python manage.py runserver
```

Do not commit `env/`, `db.sqlite3`, or secrets.

## GitHub

The target repository is:

`https://github.com/Srijan-Pandey-20/Customer-Support-Project`

From this directory:

```powershell
git init -b main
git add .
git status
git commit -m "Deploy SRMCEM Event Portal"
git remote add origin https://github.com/Srijan-Pandey-20/Customer-Support-Project.git
git push -u origin main
```

## Render

The root `render.yaml` provisions the web service and Postgres database. In Render, connect the GitHub repository and create a new Blueprint from the repository. During the first Blueprint creation, Render prompts for the three `sync: false` variables used to create the application's first custom admin account.

The build runs:

1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --no-input`
3. `python manage.py migrate`
4. `python manage.py create_app_admin ...` when the initial admin variables are supplied.

The local `db.sqlite3` is deliberately ignored by Git, so the Render Postgres database starts empty. Create/add events through the application's admin dashboard after deployment, or migrate existing data separately.

## Free-tier limitations

Render Free web services spin down after 15 minutes of inactivity and have an ephemeral filesystem. Free Render Postgres databases currently expire after 30 days. Free web services also cannot send outbound SMTP traffic on ports 25, 465 or 587, so Gmail SMTP registration emails are not reliable on the Free web service. The application catches email failures so event registration itself still succeeds.
