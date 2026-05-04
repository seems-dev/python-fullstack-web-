from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any

from fastapi import Cookie, Depends, Header, HTTPException, Request, Response

from xania.web.config import Settings, get_settings


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def _json_dumps(obj: Any) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _pbkdf2_hash(password: str, *, salt: bytes, iterations: int = 210_000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64url_encode(salt)}${_b64url_encode(dk)}"


def _pbkdf2_verify(password: str, encoded: str) -> bool:
    try:
        algo, iters_s, salt_s, dk_s = encoded.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iters_s)
        salt = _b64url_decode(salt_s)
        expected = _b64url_decode(dk_s)
    except Exception:
        return False

    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(dk, expected)


@dataclass(frozen=True)
class Session:
    sub: str
    csrf: str
    exp: int


class AuthManager:
    """
    Minimal cookie-session auth for demos.

    - Signed session cookie (HMAC-SHA256) with exp.
    - CSRF token stored inside session; client must echo it for mutating requests.
    - In-memory user DB (demo only).
    """

    cookie_name = "xania_session"
    cookie_path = "/"

    def __init__(self, secret_key: bytes, *, ttl_seconds: int = 60 * 60 * 8, cookie_secure: bool = False) -> None:
        if not secret_key:
            raise ValueError("secret_key must be non-empty")
        self._secret_key = secret_key
        self._ttl = int(ttl_seconds)
        self._cookie_secure = bool(cookie_secure)

        # Demo users (in-memory).
        salt = b"xania-demo-salt"
        self._users = {
            "admin": {
                "username": "admin",
                "name": "Admin",
                "password_hash": _pbkdf2_hash("admin", salt=salt),
                "roles": ["admin"],
            }
        }

    def _sign(self, payload: bytes) -> str:
        mac = hmac.new(self._secret_key, payload, hashlib.sha256).digest()
        return _b64url_encode(mac)

    def _encode_session(self, sess: Session) -> str:
        payload = _json_dumps({"sub": sess.sub, "csrf": sess.csrf, "exp": sess.exp})
        token = _b64url_encode(payload)
        sig = self._sign(payload)
        return f"{token}.{sig}"

    def _decode_session(self, token: str) -> Session | None:
        if not token or "." not in token:
            return None
        token_part, sig_part = token.split(".", 1)
        try:
            payload = _b64url_decode(token_part)
        except Exception:
            return None

        expected = self._sign(payload)
        if not hmac.compare_digest(expected, sig_part):
            return None

        try:
            obj = json.loads(payload.decode("utf-8"))
            sub = str(obj["sub"])
            csrf = str(obj["csrf"])
            exp = int(obj["exp"])
        except Exception:
            return None

        if int(time.time()) >= exp:
            return None

        return Session(sub=sub, csrf=csrf, exp=exp)

    def set_session_cookie(self, response: Response, sess: Session) -> None:
        response.set_cookie(
            self.cookie_name,
            self._encode_session(sess),
            httponly=True,
            secure=self._cookie_secure,
            samesite="lax",
            path=self.cookie_path,
            max_age=max(0, sess.exp - int(time.time())),
        )

    def clear_session_cookie(self, response: Response) -> None:
        response.delete_cookie(self.cookie_name, path=self.cookie_path)

    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        user = self._users.get(username)
        if not user:
            return None
        if not _pbkdf2_verify(password, user["password_hash"]):
            return None
        return {"username": user["username"], "name": user["name"], "roles": list(user["roles"])}

    def new_session(self, *, username: str) -> Session:
        csrf = secrets.token_urlsafe(24)
        exp = int(time.time()) + self._ttl
        return Session(sub=username, csrf=csrf, exp=exp)

    def current_user(self, sess: Session) -> dict[str, Any] | None:
        user = self._users.get(sess.sub)
        if not user:
            return None
        return {"username": user["username"], "name": user["name"], "roles": list(user["roles"])}

    def require_csrf(
        self,
        sess: Session,
        csrf_header: str | None,
        *,
        origin: str | None,
        referer: str | None,
        host: str | None,
    ) -> None:
        if not csrf_header or not hmac.compare_digest(csrf_header, sess.csrf):
            raise HTTPException(status_code=403, detail="CSRF token missing or invalid")
        # Cheap Origin/Referer defense-in-depth for browser POSTs.
        # Only enforce when headers are present; API clients often omit them.
        expected = f"https://{host}" if host else None
        if origin and expected and not origin.startswith(expected) and not origin.startswith(expected.replace("https://", "http://")):
            raise HTTPException(status_code=403, detail="Origin mismatch")
        if referer and expected and not referer.startswith(expected) and not referer.startswith(expected.replace("https://", "http://")):
            raise HTTPException(status_code=403, detail="Referer mismatch")


def get_auth_manager() -> AuthManager:
    settings = get_settings()
    return AuthManager(
        settings.secret_key.encode("utf-8"),
        ttl_seconds=settings.session_ttl_seconds,
        cookie_secure=settings.cookie_secure,
    )


def get_session(
    auth: AuthManager = Depends(get_auth_manager),
    cookie: str | None = Cookie(default=None, alias=AuthManager.cookie_name),
) -> Session | None:
    if not cookie:
        return None
    return auth._decode_session(cookie)


def require_session(sess: Session | None = Depends(get_session)) -> Session:
    if not sess:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return sess


def require_csrf(
    request: Request,
    sess: Session = Depends(require_session),
    auth: AuthManager = Depends(get_auth_manager),
    x_csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> Session:
    auth.require_csrf(
        sess,
        x_csrf_token,
        origin=request.headers.get("origin"),
        referer=request.headers.get("referer"),
        host=request.headers.get("host"),
    )
    return sess


def require_role(*roles: str):
    role_set = {r for r in roles if r}

    def _dep(sess: Session = Depends(require_session), auth: AuthManager = Depends(get_auth_manager)) -> Session:
        user = auth.current_user(sess)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if role_set and not any(r in set(user.get("roles") or []) for r in role_set):
            raise HTTPException(status_code=403, detail="Forbidden")
        return sess

    return _dep


__all__ = [
    "AuthManager",
    "Session",
    "get_auth_manager",
    "get_session",
    "require_session",
    "require_csrf",
    "require_role",
]
