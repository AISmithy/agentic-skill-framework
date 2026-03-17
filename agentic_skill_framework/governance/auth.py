import secrets
from typing import Optional

class AuthManager:
    def __init__(self):
        self._users: dict[str, dict] = {}
        self._tokens: dict[str, str] = {}

    def create_user(self, user_id: str, roles: list[str], permissions: list[str]) -> dict:
        self._users[user_id] = {"roles": roles, "permissions": permissions, "tokens": set()}
        return {"user_id": user_id, "roles": roles, "permissions": permissions}

    def authenticate(self, user_id: str, token: str) -> bool:
        return token in self._tokens and self._tokens[token] == user_id

    def authorize(self, user_id: str, resource: str, action: str) -> bool:
        user = self._users.get(user_id)
        if not user:
            return False
        perms = user["permissions"]
        return (
            f"{resource}:{action}" in perms or
            f"{resource}:*" in perms or
            "*:*" in perms
        )

    def generate_token(self, user_id: str) -> str:
        token = secrets.token_hex(32)
        self._tokens[token] = user_id
        if user_id in self._users:
            self._users[user_id]["tokens"].add(token)
        return token

    def revoke_token(self, token: str) -> bool:
        if token in self._tokens:
            user_id = self._tokens[token]
            del self._tokens[token]
            if user_id in self._users:
                self._users[user_id]["tokens"].discard(token)
            return True
        return False
