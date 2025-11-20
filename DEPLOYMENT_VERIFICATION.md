# TBBAS Deployment Verification Guide

## 🚀 Latest Deployment Status

**Commit:** `b26e350` - Complete multi-source ranking system with enhanced diagnostics
**Pushed:** November 20, 2025
**Status:** ✅ Successfully pushed to Railway

---

## ✅ What Was Deployed

### Core System Enhancements
- ✅ **1,304 total schools** tracked (up from 210)
  - 1,019 UIL schools (all classifications 6A-1A)
  - 285 TAPPS schools (all classifications 6A-1A)
- ✅ **686 games** in database
- ✅ **299 teams** with current records
- ✅ **100% district coverage** (UIL + TAPPS)

### Multi-Source Ranking Integration
- ✅ GASO rankings (130 teams)
- ✅ MaxPreps rankings (scraper active)
- ✅ TABC rankings (scraper active)
- ✅ Calculated rankings from game data
- ✅ **Priority system:** Calculated > GASO > MaxPreps > TABC

### Real-Time Updates
- ✅ Form submissions instantly update rankings
- ✅ Automatic Monday 6 AM ranking updates
- ✅ Daily 10 PM game collection

### Files Deployed
```
app.py                          - Enhanced debug endpoint
scheduler.py                    - GASO integration
gaso_scraper.py                 - GASO rankings (130 teams)
initialize_all_schools.py       - 1,304 school expansion
data/rankings.json              - 278KB, updated 2025-11-20 10:17 AM
instance/tbbas.db               - 90KB, 686 games
diagnose_server.py              - Server diagnostics
force_update_on_server.py       - Manual update trigger
deploy_updates.sh               - Deployment automation
RAILWAY_TROUBLESHOOTING.md      - Deployment guide
```

---

## 🔍 How to Verify Deployment

### Step 1: Check Railway Dashboard
1. Go to https://railway.app/dashboard
2. Click your TBBAS project
3. Click "Deployments" tab
4. Verify latest deployment shows:
   - **Commit:** `b26e350`
   - **Status:** "Active" or "Success"
   - **Time:** Within last 10 minutes

### Step 2: Hard Refresh Your Browser
This is the most common issue - browser caching old version.

**Mac:** `Cmd + Shift + R`
**Windows:** `Ctrl + Shift + R`
**Or:** Open in Incognito/Private window

### Step 3: Test the Debug Endpoint
Visit: `https://your-site.railway.app/debug`

**Expected Output:**
```json
{
  "last_updated": "2025-11-20T10:17:39.225557",
  "total_teams": 1304,
  "teams_with_records": 299,
  "games_in_db": 686,
  "tapps_teams_total": 285,
  "tapps_teams_with_districts": 285,
  "sample_teams_with_records": [
    {
      "name": "Steele",
      "record": "3-0",
      "ppg": 73.7,
      "district": "29"
    },
    {
      "name": "Little Elm",
      "record": "2-1",
      "ppg": 76.3,
      "district": "5"
    }
  ]
}
```

### Step 4: Check 6A Rankings Page
Visit: `https://your-site.railway.app/rankings/AAAAAA`

**You Should See:**
- ✅ Steele: **3-0** record, 73.7 PPG, District 29
- ✅ Little Elm: **2-1** record, 76.3 PPG, District 5
- ✅ Multiple teams with W-L records
- ✅ All teams have district numbers

### Step 5: Check TAPPS Rankings Page
Visit: `https://your-site.railway.app/rankings/TAPPS_4A`

**You Should See:**
- ✅ Every team shows a district number
- ✅ No blank/missing district fields
- ✅ Some teams may show records if they played games

### Step 6: Test Form Submission
Visit: `https://your-site.railway.app/submit-boxscore`

**Submit a test game:**
1. Fill out the form with any game data
2. Submit
3. **Expected message:** "Box score submitted and rankings updated successfully!"
4. **Not:** "Box score submitted successfully! Rankings will update on next scheduled update."

The first message indicates the real-time update is working.

---

## ⏱️ Expected Deployment Timeline

From push to live:
- **Push to GitHub:** Instant ✅ (Done)
- **Railway detects push:** ~30 seconds
- **Railway builds:** ~1-2 minutes
- **Railway deploys:** ~1-2 minutes
- **Total:** 2-5 minutes

**If it's been more than 5 minutes** and you've done a hard refresh, check Railway logs for errors.

---

## 🐛 Troubleshooting

### Issue: Still Showing Old Data After 5+ Minutes

**Solution 1:** Check Railway Logs
1. Railway dashboard → Your project
2. Click "View Logs"
3. Look for deployment errors or startup issues

**Solution 2:** Manually Trigger Redeploy
1. Railway dashboard → Your project
2. Click "Deployments" tab
3. Click three dots `...` on latest deployment
4. Click "Redeploy"
5. Wait 2-5 minutes

**Solution 3:** Run Server Diagnostic Script
If you have Railway CLI access:
```bash
railway run python diagnose_server.py
```

This will show exactly what's deployed on the server.

**Solution 4:** Force Rankings Update
If the database deployed but rankings didn't update:
```bash
railway run python force_update_on_server.py
```

This will manually trigger the ranking update process.

---

## ✅ Verification Checklist

Check each item after deployment completes:

- [ ] Railway dashboard shows deployment "Active" (commit `b26e350`)
- [ ] Hard refresh browser (Cmd+Shift+R or Incognito mode)
- [ ] `/debug` endpoint shows 299 teams with records
- [ ] `/debug` endpoint shows 686 games in database
- [ ] `/debug` endpoint shows last_updated: "2025-11-20T10:17:39.225557"
- [ ] 6A page shows Steele (3-0) and Little Elm (2-1)
- [ ] TAPPS 4A page shows all teams with districts
- [ ] Form submission shows "rankings updated successfully" message

---

## 📊 What's Different From Before

### Before This Deployment:
- ❌ Only 210 schools tracked (top 25 UIL, top 10 TAPPS per class)
- ❌ Form submissions didn't update rankings
- ❌ Some TAPPS teams missing districts
- ❌ Corrupted team names (Humble Humble Atascocita, etc.)
- ❌ No GASO rankings integration
- ❌ 557 games in database

### After This Deployment:
- ✅ 1,304 schools tracked (all UIL + TAPPS)
- ✅ Form submissions update rankings immediately
- ✅ 100% district coverage (all 1,304 schools)
- ✅ All team names cleaned and fixed
- ✅ GASO rankings integrated (130 teams)
- ✅ 686 games in database (+129)
- ✅ 299 teams with current records

---

## 🆘 Still Need Help?

If verification fails after trying all troubleshooting steps:

1. Share the output from `/debug` endpoint
2. Share Railway deployment logs
3. Confirm which step in the checklist is failing
4. Take a screenshot of what you're seeing vs. what's expected

This will help diagnose whether it's:
- A Railway deployment issue
- A database persistence issue
- A browser caching issue
- A file permission issue

---

**Last Updated:** November 20, 2025
**Deployment Commit:** `b26e350`
**Expected Live In:** 2-5 minutes from push
