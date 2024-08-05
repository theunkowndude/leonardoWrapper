import sys

import requests

from leonardoWrapper.types.Res import DefaultResponseType
from leonardoWrapper.util.userAgents import get_random_user_agent


sys.dont_write_bytecode = True

class RequestsHandler:
    def __init__(self, proxy: str = None) -> None:
        self.requests_session: requests.Session = requests.Session()
        if proxy is not None:
            self.requests_session.proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
        self.requests_session.headers.update(
            {
                "User-Agent": get_random_user_agent()
            }
        )
        self.graphql_authorization_token: str = ""


    def send_get_request(self, url: str, headers: dict = None) -> DefaultResponseType:
        send_request = self.requests_session.get(url=url, headers=headers)

        try:
            return {
                "status_code": send_request.status_code,
                "json": send_request.json(),
                "text": ""
            }
        except:
            return {
                "status_code": send_request.status_code,
                "json": "",
                "text": send_request.text
            }


    def send_post_request(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        send_request = self.requests_session.post(url=url, data=data, json=json, headers=headers)

        try:
            return {
                "status_code": send_request.status_code,
                "json": send_request.json(),
                "text": ""
            }
        except:
            return {
                "status_code": send_request.status_code,
                "json": "",
                "text": send_request.text
            }


    def send_graphql_request(self, json_data: dict) -> DefaultResponseType:
        graphql_req = self.requests_session.post(url="https://api.leonardo.ai/v1/graphql", json=json_data,
            headers={
                "Authorization": f"Bearer {self.graphql_authorization_token}"
            }
        )

        try:
            return {
                "status_code": graphql_req.status_code,
                "json": graphql_req.json(),
                "text": ""
            }
        except:
            return {
                "status_code": graphql_req.status_code,
                "json": "",
                "text": graphql_req.text
            }

    def get_authed_session(self) -> DefaultResponseType:
        get_authed_session = self.requests_session.get(url="https://app.leonardo.ai/api/auth/session")

        try:
            return {
                "status_code": get_authed_session.status_code,
                "json": get_authed_session.json(),
                "text": ""
            }
        except:
            return {
                "status_code": get_authed_session.status_code,
                "json": "",
                "text": get_authed_session.text
            }