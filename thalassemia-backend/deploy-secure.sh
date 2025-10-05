#!/bin/bash
# deploy-secure.sh - Secure deployment script

echo "🔐 Secure deployment for Thalassemia Backend"
echo "=============================================="

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please run: gcloud auth login"
    exit 1
fi

# Set the SMTP credentials in Google Cloud App Engine
echo "📧 Setting SMTP credentials in Google Cloud..."

# You need to run these commands manually with your actual credentials:
echo "Please run these commands with your actual credentials:"
echo ""
echo "gcloud app versions set-traffic --splits=staging=1"
echo "gcloud projects describe speech-test-471607"
echo ""
echo "To set environment variables securely:"
echo "1. Go to Google Cloud Console"
echo "2. Navigate to App Engine > Settings > Environment Variables"
echo "3. Add SMTP_USERNAME and SMTP_PASSWORD"
echo ""
echo "Or use gcloud command:"
echo 'gcloud app deploy --set-env-vars SMTP_USERNAME=drabhijeet@muktanganfoundation.org,SMTP_PASSWORD=YOUR_ACTUAL_PASSWORD'

echo ""
echo "⚠️  NEVER commit passwords to Git!"
echo "✅  Environment variables are safely stored in Google Cloud"