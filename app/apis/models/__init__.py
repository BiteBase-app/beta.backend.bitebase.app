# Models package initialization
# This file allows the directory to be recognized as a Python package

# Import and re-export models directly from base.py
from .base import User, BaseResponse

__all__ = ['User', 'BaseResponse']

