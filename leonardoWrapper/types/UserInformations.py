import sys
from typing import List, TypedDict

sys.dont_write_bytecode = True

class SubscriptionInfo(TypedDict):
    subscriptionTokens: List[str]
    plan: str

class UserInfo(TypedDict):
    email: str
    access_token: str
    sub: str
    email_verified: bool
    username: str
    created_at: str
    api_credit: int
    user_id: str
    subscriptions: SubscriptionInfo