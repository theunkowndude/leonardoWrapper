import base64
import json
import sys
from datetime import datetime, timezone;

from leonardoWrapper.types.UserInformations import UserInfo
from leonardoWrapper.util.api import RequestsHandler

sys.dont_write_bytecode = True

class User:
    def __init__(self, username: str, password: str, requests_handler: RequestsHandler) -> None:
        self.acc_secrets = {
            "username": username,
            "password": password
        }
        self.requests_handler = requests_handler
        self.user_informations: UserInfo = {}

        self.login()
        self.get_user_informations()



    def login(self) -> None:
        get_csrf_token = self.requests_handler.send_get_request(url="https://app.leonardo.ai/api/auth/csrf")

        if get_csrf_token["status_code"] != 200 or "csrfToken" not in get_csrf_token["json"]:
            raise Exception("Failed to get CSRF token")


        self.requests_handler.send_post_request(url="https://app.leonardo.ai/api/auth/callback/credentials",
            data={
                "username": self.acc_secrets["username"],
                "password": self.acc_secrets["password"],
                "redirect": False,
                "callbackUrl": "/",
                "csrfToken": get_csrf_token["json"]["csrfToken"],
                "json": True
            },
            headers={
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "app.leonardo.ai",
                "Origin": "https://app.leonardo.ai",
                "Referer": "https://app.leonardo.ai/auth/login?callbackUrl=%2F",
            }
        )

        authed_session = self.requests_handler.get_authed_session()
        if authed_session["status_code"] != 200 or authed_session["json"] == {}:
            raise Exception("Failed to login, check your credentials")

        self.requests_handler.graphql_authorization_token = authed_session["json"]["accessToken"]
        get_user_informations = json.loads(base64.b64decode(authed_session["json"]["accessToken"].split(".")[1]))

        self.user_informations.update(
            {
                "email": authed_session["json"]["user"]["email"],
                "access_token": authed_session["json"]["accessToken"],
                "sub": get_user_informations["sub"],
                "email_verified": get_user_informations["email_verified"],
            }
        )



    def get_user_informations(self) -> dict:
        get_user_id = self.requests_handler.send_graphql_request(
            json_data={
                "operationName": "GetUserDetails",
                "variables": {
                    "userSub": self.user_informations["sub"]
                },
                "query": "query GetUserDetails($userSub: String) { users(where: {user_details: {cognitoId: {_eq: $userSub}}}) { id username createdAt user_details { apiCredit subscriptionTokens plan } } }"
            }
        )

        if get_user_id["status_code"] != 200 or "data" not in get_user_id["json"]:
            raise Exception("Failed to get user informations")

        self.user_informations.update(
            {
                "username": get_user_id["json"]["data"]["users"][0]["username"],
                "created_at": get_user_id["json"]["data"]["users"][0]["createdAt"],
                "api_credit": get_user_id["json"]["data"]["users"][0]["user_details"][0]["apiCredit"],
                "user_id": get_user_id["json"]["data"]["users"][0]["id"],
                "subscriptions": {
                    "subscriptionTokens": get_user_id["json"]["data"]["users"][0]["user_details"][0]["subscriptionTokens"],
                    "plan": get_user_id["json"]["data"]["users"][0]["user_details"][0]["plan"]
                }
            }
        )



    def update_user_name(self, username: str) -> None:
        update_username = self.requests_handler.send_graphql_request(
            json_data={
                "operationName": "UpdateUsername",
                "variables": {
                    "arg1": {
                        "username": username
                    }
                },
                "query": "mutation UpdateUsername($arg1: UpdateUsernameInput!) { updateUsername(arg1: $arg1) { id __typename } }"
            }
        )

        if "errors" in update_username["json"]:
            raise Exception(update_username["json"]["errors"][0]["message"])



    def view_nsfw(self, enabled: bool) -> None:
        view_nsfw = self.requests_handler.send_graphql_request(
            json_data={
                "operationName": "UpdateUserDetails",
                "variables": {
                    "where": {
                        "userId": {
                            "_eq": self.user_informations["user_id"]
                        }
                    },
                    "_set": {
                        "showNsfw": enabled
                    }
                },
                "query":"mutation UpdateUserDetails($where: user_details_bool_exp!, $_set: user_details_set_input) { update_user_details(where: $where, _set: $_set) { affected_rows __typename } }"
            }
        )

        if "errors" in view_nsfw["json"]:
            raise Exception(view_nsfw["json"]["errors"][0]["message"])



    def get_global_models(self, limit: int = 50) -> dict:
        get_models = self.requests_handler.send_graphql_request(
            json_data={
                "operationName": "GetFeedModels",
                "variables": {
                    "order_by": {
                        "createdAt": "desc"
                    },
                    "userId": self.user_informations["user_id"],
                    "limit": limit,
                    "where": {
                        "official": {
                            "_eq": True
                        },
                        "status": {
                            "_eq": "COMPLETE"
                        },
                        "name": {
                            "_ilike": "%%"
                        },
                        "type": {},
                        "nsfw": {
                            "_eq": False
                        },
                        "createdAt": {
                            "_lt": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
                        }
                    },
                    "generationsWhere": {
                        "generated_images": {
                            "nsfw": {
                                "_eq": False
                            }
                        }
                    }
                },
                "query": "query GetFeedModels($order_by: [custom_models_order_by!] = [{createdAt: desc}], $where: custom_models_bool_exp, $generationsWhere: generations_bool_exp, $userId: uuid!, $limit: Int, $offset: Int) { custom_models( order_by: $order_by where: $where limit: $limit offset: $offset ) { ...ModelParts generations(limit: 1, where: $generationsWhere, order_by: [{createdAt: asc}]) { prompt generated_images(limit: 1, order_by: [{likeCount: desc}]) { id url likeCount __typename } __typename } user_favourite_custom_models(where: {userId: {_eq: $userId}}) { userId __typename } __typename } } fragment ModelParts on custom_models { id name description instancePrompt modelHeight modelWidth coreModel createdAt sdVersion type nsfw motion public trainingStrength user { id username __typename } generated_image { url id __typename } imageCount teamId __typename }"
            }
        )

        
        if "errors" in get_models["json"]:
            raise Exception(get_models["json"]["errors"][0]["message"])
        
        return get_models["json"]
