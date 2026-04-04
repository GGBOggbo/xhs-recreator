"""
认证路由 — 注册 / 登录 / Me
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.middleware.auth import get_current_user
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- Pydantic 模型 ----------

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6)


# ---------- DB helper ----------

def _get_db() -> Session:
    from app.api.routes import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- 路由 ----------

@router.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(_get_db)):
    # 查重
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 第一个用户为 admin
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "user"

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=role,
    )
    db.add(user)
    db.commit()

    return {"success": True, "message": "注册成功，请登录"}


@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(_get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user.id, user.username)

    return {
        "success": True,
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "has_cookie": user.xhs_cookies_encrypted is not None,
            },
        },
    }


@router.get("/me")
async def me(user: dict = Depends(get_current_user), db: Session = Depends(_get_db)):
    db_user = db.query(User).filter(User.id == user["user_id"]).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return {
        "success": True,
        "data": {
            "id": db_user.id,
            "username": db_user.username,
            "role": db_user.role,
            "has_cookie": db_user.xhs_cookies_encrypted is not None,
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
        },
    }
