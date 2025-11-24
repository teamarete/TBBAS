# TBBAS - Texas Boys Basketball Analytics System

KenPom-style efficiency ratings for Texas high school basketball.

## Features

- **Real rankings** from Texas Association of Basketball Coaches (TABC)
- Rankings for all Texas classifications (6A, 5A, 4A, 3A, 2A, 1A, Private)
- Web scraper to fetch latest rankings from TABC
- Clean, responsive web interface
- API endpoint to refresh data on demand

### Coming Soon
- Advanced analytics including:
  - Net Rating
  - Offensive Efficiency
  - Defensive Efficiency
  - Adjusted Tempo
  - Strength of Schedule

## Quick Start

### Running Locally

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Fetch the latest rankings (first time):**
   ```bash
   python scraper.py
   ```

3. **Start the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
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

## Updating Rankings

### Manual Update
Run the scraper to fetch the latest rankings from TABC:
```bash
source venv/bin/activate
python scraper.py
```

### API Endpoint
Visit `/refresh` in your browser or use curl:
```bash
curl http://localhost:5000/refresh
```

Rankings are sourced from:
- TABC UIL Rankings: https://tabchoops.org/uil-boys-rankings/
- TABC Private School Rankings: https://tabchoops.org/private-school-boys-rankings/

## Development

To add new features or modify rankings:

1. Edit `app.py` for backend logic
2. Modify `scraper.py` to add new data sources
3. Update templates in `templates/` for UI changes
4. Add styles in `static/css/` if needed

## Support

For issues or questions:
- Check the methodology page in the app
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help

## License

Open source - feel free to modify and use for your analytics needs.
# Last manual update: Mon Nov 24 13:16:34 CST 2025
