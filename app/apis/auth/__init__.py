from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import json
from pathlib import Path
from ..models.base import User, BaseResponse
from app.core.logging import log_info, log_error, log_warning

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Initialize Firebase Admin if available
firebase_initialized = False

try:
    from firebase_admin import auth, credentials, initialize_app

    # Try to load from service account file first
    service_account_path = Path("bitebase-3d5f9-1475e1373cfa.json")
    if service_account_path.exists():
        try:
            with open(service_account_path, "r") as f:
                service_account_info = json.load(f)
            cred = credentials.Certificate(service_account_info)
            initialize_app(cred)
            firebase_initialized = True
            log_info("Firebase initialized from service account file")
        except Exception as e:
            log_error(f"Failed to initialize Firebase from service account file: {str(e)}")

    # If service account file not available or failed, try environment variables
    if not firebase_initialized:
        try:
            # Check if required env vars are present
            required_vars = [
                "FIREBASE_PROJECT_ID",
                "FIREBASE_PRIVATE_KEY_ID",
                "FIREBASE_PRIVATE_KEY",
                "FIREBASE_CLIENT_EMAIL",
                "FIREBASE_CLIENT_ID",
                "FIREBASE_CLIENT_CERT_URL"
            ]

            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                log_warning(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
                log_warning("Firebase authentication will be disabled")
            else:
                # Get private key and handle newlines
                private_key = os.getenv("FIREBASE_PRIVATE_KEY")
                if private_key:
                    # Handle different formats of private key
                    if "\\n" in private_key:
                        private_key = private_key.replace("\\n", "\n")

                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": private_key,
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                })

                initialize_app(cred)
                firebase_initialized = True
                log_info("Firebase initialized from environment variables")
        except Exception as e:
            log_error(f"Failed to initialize Firebase from environment variables: {str(e)}")
            log_warning("Firebase authentication will be disabled")

except ImportError:
    log_warning("Firebase Admin SDK not available, authentication will be disabled")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    # Check if Firebase is initialized
    if not firebase_initialized:
        log_warning("Firebase not initialized, using mock user for development")
        # Return a mock user for development
        return User(
            id="mock-user-id",
            email="dev@example.com",
            display_name="Development User",
            photo_url=None,
            disabled=False
        )

    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return User(
            id=decoded_token["uid"],
            email=decoded_token.get("email", ""),
            display_name=decoded_token.get("name"),
            photo_url=decoded_token.get("picture"),
            disabled=False
        )
    except Exception as error:
        log_error(f"Authentication error: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=BaseResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    # Use model_dump instead of dict for Pydantic v2 compatibility
    user_data = current_user.model_dump() if hasattr(current_user, "model_dump") else current_user.dict()
    return BaseResponse(
        success=True,
        message="User information retrieved successfully",
        data={"user": user_data}
    )

@router.post("/refresh-token", response_model=BaseResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    # Check if Firebase is initialized
    if not firebase_initialized:
        log_warning("Firebase not initialized, returning mock token")
        return BaseResponse(
            success=True,
            message="Mock token generated for development",
            data={"token": "mock-token-for-development"}
        )

    try:
        custom_token = auth.create_custom_token(current_user.id)
        token_value = custom_token.decode() if hasattr(custom_token, "decode") else custom_token
        return BaseResponse(
            success=True,
            message="Token refreshed successfully",
            data={"token": token_value}
        )
    except Exception as error:
        log_error(f"Failed to refresh token: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )