# EVSU Fleet Tracker - Render Deployment Guide

## Prerequisites
- GitHub account (for connecting your repository)
- Render account (https://render.com)
- PostgreSQL database (Render provides this)

## Deployment Steps

### 1. Push to GitHub
Ensure your repository is on GitHub (if not already):
```bash
git remote add origin https://github.com/yourusername/evsu_fleet_tracker.git
git branch -M main
git push -u origin main
```

### 2. Connect to Render

1. Go to https://render.com and sign in/create account
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account and select the `evsu_fleet_tracker` repository
5. Fill in the deployment settings:
   - **Name:** `evsu-fleet-tracker`
   - **Environment:** Python 3
   - **Build Command:** (Render will auto-detect from render.yaml)
   - **Start Command:** (Render will auto-detect from render.yaml)
   - **Plan:** Free tier to start

### 3. Set Environment Variables in Render Dashboard

After creating the web service, go to **Environment** settings and add:

```
DEBUG=False
SECRET_KEY=(Render generates this automatically)
ALLOWED_HOSTS=yourdomain.onrender.com,localhost
```

### 4. Create PostgreSQL Database

1. In Render Dashboard, click "New +" → "PostgreSQL"
2. Set name: `evsu-fleet-tracker-db`
3. Keep other settings as default
4. Copy the connection string (DATABASE_URL)
5. Go back to your web service's environment variables
6. Add `DATABASE_URL` from the PostgreSQL connection string (or link it directly)

### 5. Deploy

1. Connect the database in your web service settings
2. Click "Deploy" 
3. Wait for the build to complete (watch the logs)
4. Once deployed, click on the service URL to visit your app

## Important Notes

### First Deploy
On your first deploy, the migrations will run automatically. The database will be empty, so you'll need to create a superuser:

1. In Render Dashboard, go to your web service
2. Click "Shell" tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow the prompts to create an admin account

### Static Files
- Static files are collected automatically during build
- WhiteNoise handles static file serving in production
- Ensure all CSS/JS are in the `static/` directory

### Database Migrations
- Migrations run automatically on deployment
- If you make model changes locally, commit them to GitHub, then redeploy

### Troubleshooting

**Build fails:**
- Check render.yaml syntax
- Ensure requirements.txt has all dependencies
- Check build logs in Render Dashboard

**Static files not loading:**
- Run `collectstatic` manually in shell if needed
- Check STATIC_ROOT and STATIC_URL in settings.py

**Database connection issues:**
- Verify DATABASE_URL environment variable is set
- Check PostgreSQL database is running in Render
- Ensure connection string is correct

**App crashes on first visit:**
- Check application logs in Render Dashboard
- Ensure migrations ran successfully
- Verify SECRET_KEY is set

## Manual Deployment (Alternative)

If not using Render's auto-deploy:

```bash
# Connect to Render's Git repository
git remote add render <your-render-git-url>
git push render main
```

## Monitoring

- **Logs:** View in Render Dashboard under "Logs"
- **Metrics:** Check CPU, Memory usage in Dashboard
- **Email:** Render sends alerts if service fails

## Next Steps

1. Customize `ALLOWED_HOSTS` with your actual domain
2. Set up proper email backend for production
3. Configure Cloudinary if using image uploads
4. Set up SSL certificate (automatic on Render)
5. Enable CSRF protection settings

## Environment Variables Reference

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| DEBUG | Yes | False | Always False in production |
| SECRET_KEY | Yes | - | Generate a secure key |
| ALLOWED_HOSTS | Yes | - | Comma-separated list of domains |
| DATABASE_URL | Auto | - | Set by PostgreSQL service |

## Support

For Render-specific help: https://render.com/docs
For Django help: https://docs.djangoproject.com
