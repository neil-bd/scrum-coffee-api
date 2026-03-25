"""Slack notification module for Coffee Brew API.

Implements SCRUM-18: Send Slack notifications when brew is complete.
"""
import os
import json
import logging
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#coffee-alerts")


def notify_brew_complete(brew: dict, requested_by: str = "unknown") -> bool:
    """Send a Slack notification when a brew is complete.

    Args:
        brew: The brew dict with id, strength, roast, status, created_at.
        requested_by: Display name of who requested the brew.

    Returns:
        True if notification sent successfully, False otherwise.
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not set - skipping notification")
        return False

    if requests is None:
        logger.error("requests library not installed")
        return False

    strength = brew.get("strength", "medium")
    roast = brew.get("roast", "house blend")
    brew_id = brew.get("id", "?")
    now = datetime.utcnow().strftime("%H:%M UTC")

    message = {
        "channel": SLACK_CHANNEL,
        "username": "Coffee Bot",
        "icon_emoji": ":coffee:",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Fresh coffee is ready!", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Strength:* {strength}"},
                    {"type": "mrkdwn", "text": f"*Roast:* {roast}"},
                    {"type": "mrkdwn", "text": f"*Requested by:* {requested_by}"},
                    {"type": "mrkdwn", "text": f"*Brew ID:* #{brew_id}"},
                ],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Completed at {now}"}],
            },
        ],
    }

    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=message, timeout=5)
        resp.raise_for_status()
        logger.info(f"Slack notification sent for brew #{brew_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False
