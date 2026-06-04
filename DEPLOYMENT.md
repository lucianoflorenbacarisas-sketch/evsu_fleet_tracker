Deploying EVSU Fleet Tracker

This project is configured for Render (and Heroku-compatible) deployments.

Render
- `render.yaml` is configured to install dependencies, run migrations, collect static files, and start Gunicorn.
- The `startCommand` and `Procfile` run migrations and start Gunicorn.

Recommended environment variables on the host:
- `SECRET_KEY` (or let Render generate it)
- `DEBUG=false`
- `ALLOWED_HOSTS` (e.g. `evsu-fleet-tracker.onrender.com`)
- `DATABASE_URL` (Render Postgres connection)

Local quickstart
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r evsu_fleet_tracker/requirements.txt
python evsu_fleet_tracker/manage.py migrate
python evsu_fleet_tracker/manage.py collectstatic --noinput
python evsu_fleet_tracker/manage.py runserver
```

Notes
- Static files are served with WhiteNoise via `STATICFILES_STORAGE` and `whitenoise.middleware.WhiteNoiseMiddleware`.
- The project uses `dj-database-url` to parse `DATABASE_URL` in production.
