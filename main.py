import os
import pathlib
import json
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends
from typing import TypeVar

# Define a custom type for BiteBase Intelligence APIs
BiteBaseIntelligenceAPIs = TypeVar('BiteBaseIntelligenceAPIs', bound=FastAPI)

load_dotenv()

from databutton_app.mw.auth_mw import AuthConfig, get_authorized_user


def get_router_config() -> dict:
    try:
        # Try to load the router configuration
        cfg = json.loads(open("routers.json").read())
        return cfg
    except Exception as e:
        print(f"Error loading routers.json: {e}")
        # Return a default configuration if file is missing
        return {
            "routers": {
                "workflow": {"disableAuth": True},
                "langflow": {"disableAuth": True},
                "user": {"disableAuth": True},
                "data": {"disableAuth": True}
            }
        }


def is_auth_disabled(router_config: dict, name: str) -> bool:
    try:
        return router_config.get("routers", {}).get(name, {}).get("disableAuth", True)
    except Exception:
        # Default to disabling auth if there's any issue
        return True


def import_api_routers() -> APIRouter:
    """Create top level router including all user defined endpoints."""
    routes = APIRouter(prefix="/routes")

    router_config = get_router_config()

    src_path = pathlib.Path(__file__).parent

    # Import API routers from "src/app/apis/*/__init__.py"
    apis_path = src_path / "app" / "apis"

    api_names = [
        p.relative_to(apis_path).parent.as_posix()
        for p in apis_path.glob("*/__init__.py")
    ]

    api_module_prefix = "app.apis."

    for name in api_names:
        print(f"Importing API: {name}")
        try:
            api_module = __import__(api_module_prefix + name, fromlist=[name])
            api_router = getattr(api_module, "router", None)
            if isinstance(api_router, APIRouter):
                routes.include_router(
                    api_router,
                    dependencies=(
                        []
                        if is_auth_disabled(router_config, name)
                        else [Depends(get_authorized_user)]
                    ),
                )
        except Exception as e:
            print(e)
            continue

    print(routes.routes)

    return routes


def get_firebase_config() -> dict | None:
    extensions = os.environ.get("DATABUTTON_EXTENSIONS", "[]")
    extensions = json.loads(extensions)

    for ext in extensions:
        if ext["name"] == "firebase-auth":
            return ext["config"]["firebaseConfig"]

    return None


def create_app() -> BiteBaseIntelligenceAPIs:
    """Create the app. This is called by uvicorn with the factory option to construct the app object."""
    app = FastAPI()
    app.include_router(import_api_routers())

    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                print(f"{method} {route.path}")

    firebase_config = get_firebase_config()

    if firebase_config is None:
        print("No firebase config found")
        app.state.auth_config = None
    else:
        print("Firebase config found")
        auth_config = {
            "jwks_url": "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com",
            "audience": firebase_config["projectId"],
            "header": "authorization",
        }

        app.state.auth_config = AuthConfig(**auth_config)

    return app


app = create_app()
