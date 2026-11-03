import os
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SlackToolInput(BaseModel):
    """Input schema for SlackTool."""

    slack_channel: str = Field(
        ..., description="Slack channel ID where the message will be posted."
    )
    message: str = Field(..., description="Message text to post to the Slack channel.")


class SlackTool(BaseTool):
    name: str = "SlackTool"
    description: str = "Posts a message to a Slack channel."
    args_schema: Type[BaseModel] = SlackToolInput

    def _run(self, slack_channel: str, message: str) -> str:
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

    def get_slack_channels(self) -> str:
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

        return result
        #channels = result.get("channels", [])
        #return [{"id": channel["id"], "name": channel["name"]} for channel in channels]
