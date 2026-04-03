"""
JWT 鉴权依赖项 — 用于 FastAPI Depends() 注入
"""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.utils.auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """解析 JWT Token，返回 {"user_id": int, "username": str}；无效则 401"""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="未登录或登录已过期",
        )
    return {"user_id": payload["user_id"], "username": payload["username"]}
