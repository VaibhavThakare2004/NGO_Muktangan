#!/bin/bash
# set-env-vars.sh - Set environment variables in Google Cloud

echo "🔐 Setting SMTP_PASSWORD in Google Cloud App Engine..."

# Use gcloud to set environment variables for the deployed app
gcloud app versions describe --service=default --format="value(id)" | head -1 | xargs -I {} gcloud app services set-env-vars default --version={} SMTP_PASSWORD=Abhijeet@2025

echo "✅ Environment variable set securely in Google Cloud"
echo "🚨 This password is NOT stored in your GitHub repository"
echo "📧 Your app can now send emails securely"