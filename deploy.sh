#!/bin/bash

# Install Cloudflare Wrangler if not already installed
if ! command -v wrangler &> /dev/null; then
    echo "Installing Cloudflare Wrangler..."
    npm install -g wrangler
fi

# Update wrangler if needed
npm update -g wrangler

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Login to Cloudflare (if not already logged in)
wrangler login

# Deploy to Cloudflare Workers
echo "Deploying to Cloudflare Workers..."
wrangler deploy

echo "Deployment complete! Your API is available at https://apis.bitebase.app"

