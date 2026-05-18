"""
安全模块
负责JWT Token生成与验证、密码加密、权限校验
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import secrets
from fastapi import Depends, status
from app.exceptions import AppException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from loguru import logger
from dotenv import load_dotenv
import os

load_dotenv()

_raw_key = os.getenv("SECRET_KEY", "")
if not _raw_key or _raw_key == "your-secret-key-change-this-in-production":
    SECRET_KEY = secrets.token_hex(32)
    logger.warning("未配置SECRET_KEY，已生成随机密钥（重启后失效，请在.env中配置固定密钥）")
else:
    SECRET_KEY = _raw_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise AppException(code=401, message="无效的认证凭据")

    user_id = payload.get("sub")
    if user_id is None:
        raise AppException(code=401, message="无效的认证凭据")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise AppException(code=401, message="用户不存在")

    return user


def check_couple_permission(current_user: User, target_user_id: int) -> bool:
    if current_user.id == target_user_id:
        return True
    if current_user.lover_id == target_user_id:
        return True
    return False
