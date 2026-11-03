import os
from typing import Literal, Type
import json

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SlackToolInput(BaseModel):
    """Input schema for SlackTool."""
    action: Literal["list_channels", "post_message"] = Field(
        ..., description="Action to perform: 'list_channels' or 'post_message'."
    )
    slack_channel: str | None = Field(
        default=None, description="Required for post_message: the Slack channel ID."
    )
    message: str | None = Field(
        default=None, description="Required for post_message: the message to send.")


class SlackTool(BaseTool):
    name: str = "SlackTool"
    description: str = "Lists public Slack channels and their IDs, or posts a message to a channel."
    args_schema: Type[BaseModel] = SlackToolInput

    def _run(
        self,
        action: Literal["list_channels", "post_message"],
        slack_channel: str | None = None,
        message: str | None = None,
    ) -> str:
        if action == "list_channels":
            return json.dumps(self.get_slack_channels())

        if slack_channel is None or message is None:
            raise ValueError(
                "slack_channel and message are required for post_message."
            )
        return self.post_to_channel(slack_channel, message)

    def post_to_channel(self, slack_channel: str, message: str) -> str:
        token = os.environ.get("SLACK_BOT_TOKEN")
        if not token:
            raise ValueError("SLACK_BOT_TOKEN environment variable is not set.")

        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            },
            json={"channel": slack_channel, "text": message},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            error = result.get("error", "unknown_error")
            raise RuntimeError(f"Slack rejected the message: {error}")

        return f"Message posted successfully to Slack channel {slack_channel}."
        
    def get_slack_channels(self) -> list[dict[str, str]]:
        """
        
        Retrieves the Slack channel information
        
        """
        token = os.environ.get("SLACK_BOT_TOKEN")
        if not token:
            raise ValueError("SLACK_BOT_TOKEN environment variable is not set.")

        response = requests.get(
            "https://slack.com/api/conversations.list?types=public_channel",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            error = result.get("error", "unknown_error")
            raise RuntimeError(f"Slack API error: {error}")

        channels = result.get("channels", [])
        return [{"id": channel["id"], "name": channel["name"]} for channel in channels]
