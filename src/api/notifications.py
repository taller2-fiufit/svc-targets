from typing import List
import requests
from requests.exceptions import ConnectionError, HTTPError
from exponent_server_sdk import (  # type: ignore
    PushClient,
    PushMessage,
    PushTicketError,
)
from src.api.model.target import Target

from src.logging import error


# Optionally providing an access token within a session
# if you have enabled push security
def send_push(token: str, completed: List[Target]) -> None:
    send_push_messages(
        token,
        [
            f"Congratulations on your completion of target '{target.name}'!"
            for target in completed
        ],
    )


# TAKEN from https://github.com/expo-community/expo-server-sdk-python

EXPO_SESSION = requests.Session()
# session.headers.update(
#     {
#         "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
#         "accept": "application/json",
#         "accept-encoding": "gzip, deflate",
#         "content-type": "application/json",
#     }
# )


# Basic arguments. You should extend this function with the push
# features you want to use, or simply pass in a `PushMessage` object.
def send_push_messages(token: str, messages: List[str]) -> None:
    for tries in range(5):
        try:
            client = PushClient(session=EXPO_SESSION)
            responses = client.publish_multiple(
                [PushMessage(to=token, body=msg) for msg in messages]
            )
            # We got a response back, but we don't know whether it's an error yet.
            # This call raises errors so we can handle them with normal exception
            # flows.
            [response.validate_response() for response in responses]
        except (ConnectionError, HTTPError, PushTicketError) as exc:
            # Encountered some Connection or HTTP error - retry a few times in
            # case it is transient.
            if tries <= 4:
                tries += 1
                continue
            error(str(exc))
        except Exception as exc:
            error(str(exc))
