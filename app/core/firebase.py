import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    print("Firebase Admin SDK not available, Firebase integration will be disabled")
    FIREBASE_AVAILABLE = False

from app.core.logging import log_info, log_error, log_warning
from app.core.errors import ExternalServiceError

class FirebaseClient:
    """Firebase client for authentication and Firestore operations."""

    def __init__(self):
        self.app = None
        self.db = None
        self.initialized = False

        if not FIREBASE_AVAILABLE:
            log_warning("Firebase Admin SDK not available, Firebase integration is disabled")
            return

        try:
            self.initialize()
        except Exception as e:
            log_error(f"Failed to initialize Firebase: {str(e)}")

    def initialize(self):
        """Initialize Firebase Admin SDK with service account credentials"""
        if self.initialized or not FIREBASE_AVAILABLE:
            return

        # Try to load from service account file first
        service_account_path = Path("bitebase-3d5f9-1475e1373cfa.json")
        if service_account_path.exists():
            try:
                cred = credentials.Certificate(str(service_account_path))
                self.app = firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                log_info("Firebase initialized from service account file")
                return
            except Exception as e:
                log_error(f"Failed to initialize Firebase from service account file: {str(e)}")

        # If service account file not available, try environment variables
        try:
            # Check if all required env vars are present
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
                return

            # Create credential from environment variables
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
                "universe_domain": "googleapis.com"
            })

            try:
                self.app = firebase_admin.initialize_app(cred)
            except ValueError:
                # App already exists
                self.app = firebase_admin.get_app()

            self.db = firestore.client()
            self.initialized = True
            log_info("Firebase initialized from environment variables")
        except Exception as e:
            log_error(f"Failed to initialize Firebase from environment variables: {str(e)}")

    def verify_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and return decoded token"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            log_error(f"Failed to verify Firebase token: {str(e)}")
            raise ExternalServiceError(f"Invalid token: {str(e)}")

    def get_user(self, uid: str) -> Dict[str, Any]:
        """Get user data from Firebase Auth"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled,
                "email_verified": user.email_verified,
                "provider_data": [{
                    "provider_id": provider.provider_id,
                    "uid": provider.uid,
                    "email": provider.email,
                    "display_name": provider.display_name,
                    "photo_url": provider.photo_url
                } for provider in user.provider_data]
            }
        except Exception as e:
            log_error(f"Failed to get user {uid}: {str(e)}")
            raise ExternalServiceError(f"Failed to get user: {str(e)}")

    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            log_error(f"Failed to get document {collection}/{doc_id}: {str(e)}")
            raise ExternalServiceError(f"Failed to get document: {str(e)}")

    def set_document(self, collection: str, doc_id: str, data: Dict[str, Any], merge: bool = True) -> None:
        """Set a document in Firestore"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.set(data, merge=merge)
        except Exception as e:
            log_error(f"Failed to set document {collection}/{doc_id}: {str(e)}")
            raise ExternalServiceError(f"Failed to set document: {str(e)}")

    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Update a document in Firestore"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
        except Exception as e:
            log_error(f"Failed to update document {collection}/{doc_id}: {str(e)}")
            raise ExternalServiceError(f"Failed to update document: {str(e)}")

    def delete_document(self, collection: str, doc_id: str) -> None:
        """Delete a document from Firestore"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
        except Exception as e:
            log_error(f"Failed to delete document {collection}/{doc_id}: {str(e)}")
            raise ExternalServiceError(f"Failed to delete document: {str(e)}")

    def query_collection(self, collection: str, filters: List[tuple] = None, order_by: str = None,
                        limit: int = None, start_after: Any = None) -> List[Dict[str, Any]]:
        """Query a collection in Firestore"""
        if not self.initialized or not FIREBASE_AVAILABLE:
            raise ExternalServiceError("Firebase is not initialized")

        try:
            query = self.db.collection(collection)

            # Apply filters
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)

            # Apply order by
            if order_by:
                query = query.order_by(order_by)

            # Apply start after
            if start_after:
                query = query.start_after(start_after)

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute query
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            log_error(f"Failed to query collection {collection}: {str(e)}")
            raise ExternalServiceError(f"Failed to query collection: {str(e)}")

# Create a singleton instance
firebase_client = FirebaseClient()