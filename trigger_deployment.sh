#!/bin/bash

echo "================================================================================"
echo "TRIGGERING RAILWAY DEPLOYMENT - Consensus Rankings Update"
echo "================================================================================"
echo ""
echo "Latest commits ready to deploy:"
git log --oneline -5
echo ""
echo "================================================================================"
echo ""
echo "Railway auto-deploys from GitHub. Checking if deployment is needed..."
echo ""

# Check if we have unpushed commits
UNPUSHED=$(git log origin/main..HEAD --oneline | wc -l)

if [ $UNPUSHED -gt 0 ]; then
    echo "⚠ Found $UNPUSHED unpushed commit(s). Pushing now..."
    git push origin main
    echo "✓ Pushed to origin/main"
else
    echo "✓ All commits already pushed to origin/main"
fi

echo ""
echo "================================================================================"
echo "DEPLOYMENT STATUS"
echo "================================================================================"
echo ""
echo "✓ All code changes pushed to GitHub"
echo "✓ Railway should auto-deploy within 1-2 minutes"
echo ""
echo "What was deployed:"
echo "  • Consensus rankings (TABC + MaxPreps + Calculated)"
echo "  • Fixed TABC records for all teams"
echo "  • Removed location suffixes"
echo "  • Added RR Westwood name mapping"
echo "  • Fixed Huckabay statistics"
echo ""
echo "To monitor deployment:"
echo "  1. Check Railway dashboard: https://railway.app/"
echo "  2. Look for deployment triggered by commit: 8ccf7f6"
echo ""
echo "After deployment (1-2 min):"
echo "  1. Visit https://tbbas.teamarete.net/"
echo "  2. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)"
echo "  3. Check UIL 6A: Little Elm should be #2 (not #3)"
echo "  4. Check UIL 1A: Gordon should be #1 (not #2)"
echo ""
echo "If website still shows old data after 5 minutes:"
echo "  • Check Railway logs for deployment errors"
echo "  • Verify Railway is connected to correct GitHub repo"
echo "  • Manual trigger: Railway dashboard → Deploy → Deploy Now"
echo ""
echo "================================================================================"

