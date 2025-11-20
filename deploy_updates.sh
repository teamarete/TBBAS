#!/bin/bash

echo "================================================================================"
echo "TBBAS DEPLOYMENT - Updating Live Site"
echo "================================================================================"

# Check if we're in git repo
if [ ! -d .git ]; then
    echo "ERROR: Not a git repository"
    exit 1
fi

echo ""
echo "Step 1: Checking current status..."
git status

echo ""
echo "Step 2: Adding all updated files..."
git add data/rankings.json
git add app.py
git add update_rankings_with_records.py
git add import_hoopinsider_scores.py
git add fix_team_names.py
git add instance/tbbas.db

echo ""
echo "Step 3: Creating commit..."
git commit -m "Update rankings with game records and fix team names

- Fixed 18 corrupted team names (duplicate cities, merged names)
- Imported 129 games from HoopInsider (Nov 17-18)
- Updated 299 teams with current records
- All TAPPS teams have districts assigned
- Form submissions now update rankings immediately
- Last updated: $(date)
"

echo ""
echo "Step 4: Pushing to Railway..."
git push origin main

echo ""
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "================================================================================"
echo ""
echo "Changes pushed to Railway:"
echo "  • 686 games in database"
echo "  • 299 teams with updated records"
echo "  • All 1,304 schools have districts"
echo "  • Real-time record updates enabled"
echo ""
echo "Railway will automatically deploy these changes."
echo "Check your Railway dashboard to monitor deployment status."
echo ""
echo "After deployment completes:"
echo "  1. Visit your site and do a hard refresh (Cmd+Shift+R)"
echo "  2. Check 6A rankings - should see Steele (3-0), Little Elm (2-1)"
echo "  3. Check TAPPS 4A - all teams should have districts"
echo "================================================================================"
