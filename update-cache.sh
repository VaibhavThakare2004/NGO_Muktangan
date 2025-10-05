#!/bin/bash
# update-cache.sh - Update cache busting versions

# Get current timestamp
VERSION=$(date +%Y%m%d-%H%M)

# Update HTML file with new version
sed -i "s/\?v=[0-9]\{8\}-[0-9]\{1,2\}/\?v=$VERSION/g" Thalassemia_detection.html

echo "Updated cache version to: $VERSION"
echo "Files updated:"
echo "- Thalassemia_detection.css?v=$VERSION"
echo "- Thalassemia_detection.js?v=$VERSION"

# Optional: Commit changes
read -p "Commit changes to git? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add Thalassemia_detection.html
    git commit -m "Update cache version to $VERSION"
    git push origin main
    echo "Changes committed and pushed!"
fi