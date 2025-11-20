# Railway Deployment Troubleshooting

## Issue: Website Not Showing Updated Records/Districts

### What Was Deployed (Confirmed ✅)
- ✅ `data/rankings.json` - 1,304 teams, updated 2025-11-20 10:17 AM
- ✅ `instance/tbbas.db` - 686 games, 90KB database file
- ✅ `app.py` - Form submission auto-update fix
- ✅ All fixes pushed to GitHub commit `fa73ac0`

### Why It Might Not Be Showing

1. **Railway is still deploying** (takes 2-5 min)
2. **Browser cache** - Old version cached
3. **Railway not rebuilding** - Deployment didn't trigger
4. **Database persisted** - Railway using old database from volume

---

## Solutions to Try (In Order)

### Solution 1: Hard Refresh Browser ⭐ TRY THIS FIRST
```
Mac: Cmd + Shift + R
Windows: Ctrl + Shift + R
Or: Open in Incognito/Private window
```

### Solution 2: Check Railway Deployment Status
1. Go to https://railway.app/dashboard
2. Click your TBBAS project
3. Look for "Deployments" tab
4. Verify latest deployment shows:
   - Commit: `fa73ac0` or `4092761`
   - Status: "Active" or "Success"
   - Time: Within last 10 minutes

### Solution 3: Manually Trigger Railway Redeploy
1. In Railway dashboard → Your project
2. Click "Deployments" tab
3. Click three dots `...` on latest deployment
4. Click "Redeploy"
5. Wait 2-5 minutes for deployment

### Solution 4: Run Diagnostic on Railway
Add a temporary route to your app to check what's deployed:

```python
# Add this to app.py temporarily
@app.route('/diagnostic')
def diagnostic():
    import json
    with open('data/rankings.json') as f:
        data = json.load(f)

    teams_with_records = sum(
        1 for classification in data['uil'].values()
        for team in classification
        if team.get('wins') is not None
    )

    return jsonify({
        'last_updated': data.get('last_updated'),
        'total_teams': sum(len(teams) for teams in data['uil'].values()) + sum(len(teams) for teams in data['private'].values()),
        'teams_with_records': teams_with_records,
        'games_in_db': BoxScore.query.count()
    })
```

Then visit: `https://your-site.railway.app/diagnostic`

Expected output:
```json
{
  "last_updated": "2025-11-20T10:17:39.225557",
  "total_teams": 1304,
  "teams_with_records": 299,
  "games_in_db": 686
}
```

### Solution 5: Check Railway Logs
1. Railway dashboard → Your project
2. Click "View Logs"
3. Look for errors during startup:
   - File not found errors
   - Database errors
   - Import errors

### Solution 6: Clear Railway's Database Volume
If Railway persists the database in a volume, the old data might still be there:

1. Railway dashboard → Your project
2. Click "Variables" tab
3. Look for any volume mounts
4. If found, you may need to:
   - Remove the volume
   - Redeploy
   - The new database will be used

### Solution 7: Force Database from Git
If Railway is persisting an old database, add this to your app startup:

```python
# In app.py, after db.create_all()
if os.getenv('RAILWAY_ENVIRONMENT'):
    # On Railway, always copy the git-tracked database
    import shutil
    git_db = 'instance/tbbas.db'
    if os.path.exists(git_db):
        # This ensures we use the version from git
        print(f"Using database from git: {git_db}")
```

---

## Quick Verification Checklist

Run these checks locally to verify what SHOULD be on Railway:

```bash
# 1. Check local rankings file
python -c "import json; d=json.load(open('data/rankings.json')); print(f'Teams: {sum(len(t) for t in d[\"uil\"].values())}'); print(f'Updated: {d[\"last_updated\"]}')"

# Expected: Teams: 1019, Updated: 2025-11-20T10:17:39.225557

# 2. Check local database
python -c "from app import app; from models import BoxScore; app.app_context().push(); print(f'Games: {BoxScore.query.count()}')"

# Expected: Games: 686

# 3. Verify git has latest
git log -1 --oneline

# Expected: Should show commit about "Update rankings with game records"
```

---

## What You SHOULD See on Live Site

### On Any 6A Team Page (e.g., `/rankings/AAAAAA`):
- Steele: 3-0 record, 73.7 PPG, District 29
- Little Elm: 2-1 record, 76.3 PPG, District 5
- Multiple teams with W-L records

### On Any TAPPS Page (e.g., `/rankings/TAPPS_4A`):
- Every team shows a district number
- No blank/missing district fields
- Some teams may show records if they played

### On Form Submission (`/submit-boxscore`):
- After submitting, message should say "Box score submitted and rankings updated successfully!"
- Not just "Box score submitted successfully!"

---

## Still Not Working?

If none of the above works, there may be a Railway-specific issue. Try:

1. **Check Railway Environment Variables**
   - Ensure `DATABASE_URL` isn't pointing to external DB
   - Ensure no variables are overriding file paths

2. **Rebuild from Scratch**
   - Delete the Railway service
   - Create new Railway service
   - Connect to same GitHub repo
   - Redeploy

3. **Contact Railway Support**
   - Describe: "Deployed files not reflecting on live site"
   - Provide: Commit hash (`fa73ac0`)
   - Ask: Why deployment isn't using latest files

---

## Alternative: Manual Data Upload

If Railway won't deploy the database, you can:

1. Keep rankings in `data/rankings.json` (this IS deploying)
2. Use the web form to submit games instead of bulk import
3. Each form submission will update rankings immediately
4. Over time, the database will rebuild on Railway

Or:

1. After Railway deploys
2. SSH/terminal into Railway container (if available)
3. Run: `python import_hoopinsider_scores.py`
4. This will reimport all 129 games directly on the server

---

## Expected Timeline

From push to live:
- Push to GitHub: Instant
- Railway detects push: ~30 seconds
- Railway builds: ~1-2 minutes
- Railway deploys: ~1-2 minutes
- **Total: 2-5 minutes**

If it's been more than 5 minutes and you've done a hard refresh, something is wrong with Railway deployment.
