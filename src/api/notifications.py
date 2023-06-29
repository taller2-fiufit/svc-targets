import asyncio
from typing import Any, List
from httpx import AsyncClient

from src.api.model.target import Target
from src.logging import error


# Optionally providing an access token within a session
# if you have enabled push security
async def send_push(token: str, completed: List[Target]) -> None:
    messages = [
        {
            "to": token,
            "sound": "default",
            "title": "Kinetix",
            "body": f"Congratulations on your completion of target '{target.name}'!",
            "data": {"screen": "Messages"},
        }
        for target in completed
    ]
    await asyncio.gather(*[send_push_message(message) for message in messages])


async def send_push_message(message: dict[str, Any]) -> None:
    headers = {
        "Accept": "application/json",
        "Accept-encoding": "gzip, deflate",
        "Content-Type": "application/json",
    }
    try:
        async with AsyncClient(base_url="https://exp.host") as client:
            await client.post(
                "/--/api/v2/push/send", headers=headers, json=message
            )
    except Exception as e:
        error(str(e))
