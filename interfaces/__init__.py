"""
Devlar AI Workforce - User Interfaces
Primary interfaces for interacting with the AI workforce
"""

from .telegram_bot import TelegramInterface
from .streamlit_app import StreamlitInterface

__all__ = [
    "TelegramInterface",
    "StreamlitInterface"
]