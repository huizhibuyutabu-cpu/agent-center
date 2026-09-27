from dataclasses import dataclass


@dataclass
class ToolContext:
    user_token: str
    request_id: str