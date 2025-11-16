# Email Notifications Setup Guide

TBBAS now sends automatic email notifications to **blood@teamarete.net** for:
- Daily box score collection results
- Weekly rankings updates
- Errors that occur during updates

## Quick Setup on Railway

### Option 1: Using SendGrid (Recommended - Free & Reliable)

SendGrid offers 100 emails/day free forever - perfect for TBBAS!

**Steps:**

1. **Get SendGrid API Key:**
   - Go to https://sendgrid.com and create free account
   - Navigate to Settings → API Keys
   - Click "Create API Key"
   - Give it a name: "TBBAS Notifications"
   - Select "Full Access"
   - Copy the API key (save it - you won't see it again!)

2. **Configure Railway:**
   - Go to your Railway project: https://railway.app
   - Click on your TBBAS service
   - Go to "Variables" tab
   - Add these environment variables:

   ```
   EMAIL_NOTIFICATIONS_ENABLED=True
   NOTIFICATION_EMAIL=blood@teamarete.net
   FROM_EMAIL=tbbas@teamarete.net
   SENDGRID_API_KEY=your-sendgrid-api-key-here
   ```

3. **Deploy:**
   - Railway will automatically redeploy with new variables
   - Email notifications are now active!

---

### Option 2: Using Gmail SMTP

If you prefer Gmail, you'll need an "App Password" (not your regular Gmail password).

**Steps:**

1. **Enable 2-Step Verification on Gmail:**
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification" if not already enabled

2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter: "TBBAS Notifications"
   - Click "Generate"
   - Copy the 16-character password

3. **Configure Railway:**
   - Add these environment variables:

   ```
   EMAIL_NOTIFICATIONS_ENABLED=True
   NOTIFICATION_EMAIL=blood@teamarete.net
   FROM_EMAIL=your-gmail-address@gmail.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-gmail-address@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   ```

4. **Deploy:**
   - Railway will redeploy automatically

---

## What Emails You'll Receive

### Daily Collection Email (Every Day at 6 AM)
```
Subject: TBBAS Daily Update - 25 games collected

Total Games Collected: 25

Source Breakdown:
  - MaxPreps: 20 games
  - Newspapers: 5 games

✓ Collection completed successfully

Next collection: Tomorrow at 6:00 AM
View rankings: https://web-production-0429a.up.railway.app/
```

### Weekly Rankings Email (Every Monday at 6 AM)
```
Subject: TBBAS Weekly Rankings Updated

RANKINGS UPDATED

UIL:
  AAAAAA: 25 teams
  AAAAA: 25 teams
  AAAA: 25 teams

PRIVATE:
  TAPPS_6A: 10 teams
  TAPPS_5A: 10 teams

DATA SOURCES
1. Calculated from box score data
2. MaxPreps rankings
3. TABC rankings (backup)
4. GASO rankings

✓ Update completed successfully

Next update: Next Monday at 6:00 AM
```

### Error Email (If something goes wrong)
```
Subject: ⚠️ TBBAS Error: Weekly Rankings Update

ERROR DETAILS
Type: Weekly Rankings Update
Message: [Error description]

Please check the Railway logs for more details.
```

---

## Testing Email Notifications

After configuring, you can test by:

1. **Manual Test:**
   - SSH into Railway or run locally
   - Run: `python email_notifier.py`
   - Check if test email arrives at blood@teamarete.net

2. **Trigger Manual Update:**
   - Visit: https://web-production-0429a.up.railway.app/refresh
   - Check for email notification

---

## Troubleshooting

### Not Receiving Emails?

1. **Check Railway Logs:**
   - Railway dashboard → Deployments → View Logs
   - Look for: "Email sent successfully" or error messages

2. **Check Spam Folder:**
   - Emails might be marked as spam initially
   - Mark as "Not Spam" to whitelist

3. **Verify Environment Variables:**
   - Railway dashboard → Variables
   - Make sure all required variables are set
   - No extra spaces in values

4. **Test Email Service:**
   - SendGrid: Check dashboard for send activity
   - Gmail: Make sure app password is correct (16 chars, no spaces)

### Still Not Working?

Check Railway logs for specific error messages:
- "SMTP credentials not configured" → Need to add SMTP variables
- "SendGrid failed: 401" → API key is invalid
- "SendGrid failed: 403" → API key doesn't have permission

---

## Disabling Email Notifications

To temporarily disable emails without removing configuration:

1. Railway → Variables
2. Set: `EMAIL_NOTIFICATIONS_ENABLED=False`
3. Redeploy

To re-enable, set it back to `True`.

---

## Email Limits

**SendGrid Free Tier:**
- 100 emails/day
- TBBAS usage: ~30-35 emails/month (1 daily + 4 weekly)
- Well within limits ✅

**Gmail SMTP:**
- 500 emails/day for regular accounts
- 2,000 emails/day for Google Workspace
- TBBAS usage well within limits ✅

---

## Support

If you need help setting this up, check:
- Railway logs for error messages
- SendGrid activity dashboard
- Gmail app password setup guide

Current notification recipient: **blood@teamarete.net**

To change recipient, update `NOTIFICATION_EMAIL` variable in Railway.
