"""
Cookie 加密工具 — Fernet 对称加密
"""
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

_fernet = Fernet(settings.cookie_encryption_key.encode("utf-8"))


def encrypt_cookie(plaintext: str) -> str:
    """Fernet 加密 Cookie 明文，返回 base64 字符串"""
    return _fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_cookie(encrypted: str) -> str:
    """Fernet 解密 Cookie，返回明文；密钥不匹配时抛出 InvalidToken"""
    return _fernet.decrypt(encrypted.encode("utf-8")).decode("utf-8")
