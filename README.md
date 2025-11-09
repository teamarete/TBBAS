# TBBAS - Texas Boys Basketball Analytics System

KenPom-style efficiency ratings for Texas high school basketball.

## Features

- Rankings for all Texas classifications (6A, 5A, 4A, 3A, 2A, 1A, Private)
- Advanced analytics including:
  - Net Rating
  - Offensive Efficiency
  - Defensive Efficiency
  - Adjusted Tempo
  - Strength of Schedule
- Clean, responsive web interface
- Real-time data updates

## Quick Start

### Running Locally

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

### First Time Setup

If you haven't run the setup script yet:

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

## Deployment

This application is ready to deploy to multiple platforms. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Recommended platforms:**
- Railway (Free tier, easiest)
- Render (Free tier)
- Heroku
- Fly.io
- DigitalOcean App Platform

All necessary deployment files are included:
- `Procfile` - For Heroku/Railway/Render
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification

## Project Structure

```
TBBAS Project/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration
├── runtime.txt        # Python version
├── setup.sh           # Initial setup script
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── classification.html
│   └── methodology.html
└── static/           # CSS/JS files
    ├── css/
    └── js/
```

## Technology Stack

- **Backend:** Flask (Python)
- **Analytics:** NumPy, Pandas, SciPy
- **Deployment:** Gunicorn
- **Frontend:** HTML/CSS (Jinja2 templates)

## Environment Variables

For production deployments:
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`
- `PORT` (set automatically by most platforms)

## Development

To add new features or modify rankings:

1. Edit `app.py` for backend logic
2. Modify templates in `templates/` for UI changes
3. Update styles in `static/css/` if needed

## Support

For issues or questions:
- Check the methodology page in the app
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help

## License

Open source - feel free to modify and use for your analytics needs.
