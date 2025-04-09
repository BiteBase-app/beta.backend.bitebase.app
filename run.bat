@echo off
set FIREBASE_PROJECT_ID=bitebase-3d5f9
set FIREBASE_AUTH_DOMAIN=bitebase-3d5f9.firebaseapp.com
set FIREBASE_STORAGE_BUCKET=bitebase-3d5f9.firebasestorage.app
set FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n
python -m uvicorn main:app --reload


