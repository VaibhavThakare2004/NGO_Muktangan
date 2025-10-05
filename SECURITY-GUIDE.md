# 🔐 Secure Deployment Guide

## The Problem
- Passwords in public GitHub = Security Risk ❌
- But emails need passwords to work ✅

## The Solution: Environment Variables During Deployment

### Step 1: Deploy with Secure Command
Instead of storing passwords in files, set them during deployment:

```bash
cd thalassemia-backend

# Deploy with environment variables (SECURE)
gcloud app deploy --set-env-vars SMTP_USERNAME=drabhijeet@muktanganfoundation.org,SMTP_PASSWORD=Abhijeet@2025
```

### Step 2: Alternative - Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **App Engine > Settings**
3. Click **Environment Variables**
4. Add:
   - `SMTP_USERNAME` = `drabhijeet@muktanganfoundation.org`
   - `SMTP_PASSWORD` = `Abhijeet@2025`

### Step 3: Verify Security
✅ **What's Safe Now:**
- GitHub repository has NO passwords
- Google Cloud securely stores environment variables
- Code retrieves password at runtime
- Public can see code, but not credentials

✅ **What Happens:**
1. Code asks: "What's the SMTP password?"
2. Google Cloud responds: "Abhijeet@2025" (securely)
3. Email gets sent successfully
4. Password never appears in your GitHub

### Step 4: Future Updates
When you need to change the password:
```bash
# Update password securely
gcloud app deploy --set-env-vars SMTP_PASSWORD=NEW_PASSWORD
```

## 🚨 Security Rules
- ❌ NEVER put passwords in any file that goes to GitHub
- ✅ ALWAYS use environment variables for secrets
- ✅ Keep GitHub public for hosting
- ✅ Keep passwords in Google Cloud environment variables

## Testing
After deployment, the form will:
1. ✅ Send emails (password works)
2. ✅ Update Google Sheets
3. ✅ Show thank you page
4. ✅ Keep passwords secure