# TBBAS Deployment Guide

## Local Development

### Quick Start
```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py
```

The app will be available at http://localhost:5000

### Environment Variables (Optional)
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

## Production Deployment

This application is ready to deploy to multiple platforms. Here are the most popular options:

### Option 1: Railway (Recommended - Free Tier Available)

1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI or use the web interface
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Railway will auto-detect the Procfile and deploy

**Using CLI:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

### Option 2: Render (Free Tier Available)

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** TBBAS
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click "Create Web Service"

### Option 3: Heroku

1. Create account at [heroku.com](https://heroku.com)
2. Install Heroku CLI

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-tbbas-app

# Deploy
git push heroku main

# Open your app
heroku open
```

### Option 4: Google Cloud Run

1. Install Google Cloud SDK
2. Build and deploy:

```bash
# Create Dockerfile (Railway/Render handle this automatically)
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/tbbas

# Deploy
gcloud run deploy --image gcr.io/PROJECT-ID/tbbas --platform managed
```

### Option 5: DigitalOcean App Platform

1. Create account at [digitalocean.com](https://digitalocean.com)
2. Go to App Platform
3. Click "Create App" → Connect GitHub
4. Select repository
5. DigitalOcean will auto-detect Python app
6. Deploy

### Option 6: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

## Environment Configuration

For production deployments, set these environment variables in your platform:

- `FLASK_ENV=production`
- `FLASK_DEBUG=False`

Most platforms (Railway, Render, Heroku) automatically set the `PORT` variable.

## Post-Deployment

After deployment, your app will be available at the URL provided by your platform:
- Railway: `https://your-app.up.railway.app`
- Render: `https://your-app.onrender.com`
- Heroku: `https://your-app.herokuapp.com`
- Fly.io: `https://your-app.fly.dev`

## Troubleshooting

### Check logs
- **Railway:** View in dashboard or `railway logs`
- **Render:** View in dashboard under "Logs"
- **Heroku:** `heroku logs --tail`
- **Fly.io:** `flyctl logs`

### Common issues
1. **Dependencies not installing:** Check `requirements.txt` is present
2. **App not starting:** Verify `Procfile` is correct
3. **Port errors:** Most platforms set `PORT` automatically via environment variable

## Custom Domain

All platforms support custom domains:
1. Add your domain in the platform dashboard
2. Update your DNS records as instructed
3. Enable SSL (usually automatic)

## Scaling

For high traffic:
- **Railway/Render/Heroku:** Upgrade to paid tier for more resources
- **DigitalOcean:** Scale app instances in dashboard
- **Fly.io:** Add regions and scale instances
