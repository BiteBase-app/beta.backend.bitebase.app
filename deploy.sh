#!/bin/bash

# Install or update wrangler
npm install -g wrangler@latest

# Deploy to Cloudflare Workers
echo "Deploying to Cloudflare Workers..."
wrangler deploy --compatibility-date 2024-04-09

echo "Deployment complete! Your API is available at https://apis.bitebase.app"


