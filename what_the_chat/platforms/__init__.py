"""Platform integrations for different chat services."""

from .discord import DiscordPlatform
from .slack import SlackPlatform

__all__ = ["DiscordPlatform", "SlackPlatform"]
