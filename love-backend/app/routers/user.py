"""
用户模块路由
处理用户注册、登录、信息管理、情侣绑定等接口
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
from app.database import get_db
from app.security import get_current_user
from app.models import User, Notification
from app.schemas import (
    UserRegister, UserLogin, UserUpdate, BindLover,
    UserResponse, LoverResponse, TokenResponse
)
from app.response import success_response, error_response
from app.security import create_access_token, verify_password, get_password_hash
import random
import string

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def generate_invite_code():
    """生成6位大写字母+数字邀请码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=6))


@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口
    - 输入：账号、密码、昵称
    - 输出：注册成功/失败提示
    - 规则：自动生成6位大写字母+数字邀请码，密码bcrypt加密存储
    """
    # 检查账号是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return error_response(400, "账号已存在")

    # 生成唯一邀请码
    while True:
        invite_code = generate_invite_code()
        existing_code = db.query(User).filter(User.invite_code == invite_code).first()
        if not existing_code:
            break

    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        nickname=user_data.nickname,
        invite_code=invite_code,
        heart_points=0,
        level=1
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 初始化成就记录
    from app.routers.love import _init_achievements
    _init_achievements(new_user.id, db)

    return success_response(
        data={"invite_code": invite_code},
        message="注册成功"
    )


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    - 输入：账号、密码
    - 输出：JWT Token
    - 规则：校验账号密码，成功返回Token
    """
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        return error_response(400, "账号不存在")

    # 验证密码
    if not verify_password(user_data.password, user.password):
        return error_response(400, "密码错误")

    # 生成Token
    access_token = create_access_token(data={"sub": str(user.id)})

    return success_response(
        data={
            "token": access_token,
            "user_id": user.id,
            "nickname": user.nickname
        },
        message="登录成功"
    )


@router.get("/info")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """
    获取用户信息接口
    - 需要JWT鉴权
    - 返回用户完整信息（不含密码）
    """
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "invite_code": current_user.invite_code,
        "lover_id": current_user.lover_id,
        "heart_points": current_user.heart_points,
        "level": current_user.level,
        "created_at": current_user.created_at.strftime("%Y-%m-%d %H:%M:%S") if current_user.created_at else None
    }
    return success_response(data=user_data)


@router.put("/info")
async def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改用户信息接口
    - 需要JWT鉴权
    - 支持修改：昵称、头像、密码
    - 修改密码需校验原密码
    """
    # 修改昵称
    if user_data.nickname is not None:
        current_user.nickname = user_data.nickname

    # 修改头像
    if user_data.avatar is not None:
        current_user.avatar = user_data.avatar

    # 修改密码
    if user_data.new_password is not None:
        if not user_data.old_password:
            return error_response(400, "请输入原密码")
        if not verify_password(user_data.old_password, current_user.password):
            return error_response(400, "原密码错误")
        current_user.password = get_password_hash(user_data.new_password)

    db.commit()
    db.refresh(current_user)

    return success_response(message="修改成功")


@router.post("/bind")
async def bind_lover(
    bind_data: BindLover,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    情侣绑定接口
    - 需要JWT鉴权
    - 校验用户是否已绑定，已绑定返回错误
    - 校验邀请码是否有效，无效返回错误
    - 校验对方是否已绑定，已绑定返回错误
    - 绑定成功后双方lover_id字段双向更新
    """
    # 检查是否已绑定
    if current_user.lover_id:
        return error_response(400, "您已绑定情侣，无法重复绑定")

    # 查找邀请码对应用户
    lover = db.query(User).filter(User.invite_code == bind_data.invite_code).first()
    if not lover:
        return error_response(400, "邀请码无效")

    # 检查是否绑定自己
    if lover.id == current_user.id:
        return error_response(400, "不能绑定自己")

    # 检查对方是否已绑定
    if lover.lover_id:
        return error_response(400, "对方已绑定情侣")

    # 执行双向绑定
    current_user.lover_id = lover.id
    lover.lover_id = current_user.id

    db.commit()
    db.refresh(current_user)

    return success_response(message="绑定成功")


@router.get("/lover")
async def get_lover_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取情侣信息接口
    - 需要JWT鉴权
    - 已绑定返回情侣信息
    - 未绑定返回null
    """
    if not current_user.lover_id:
        return success_response(data=None, message="未绑定情侣")

    lover = db.query(User).filter(User.id == current_user.lover_id).first()
    if not lover:
        return success_response(data=None, message="未绑定情侣")

    lover_data = {
        "id": lover.id,
        "nickname": lover.nickname,
        "avatar": lover.avatar,
        "heart_points": lover.heart_points,
        "level": lover.level
    }

    return success_response(data=lover_data)


@router.get("/notifications")
async def get_notifications(
    is_read: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    notifications = query.order_by(Notification.created_at.desc()).limit(50).all()

    result = []
    for n in notifications:
        result.append({
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": str(n.created_at)
        })

    return success_response(data=result)


@router.get("/notifications/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return success_response(data={"count": count})


@router.put("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notification:
        return error_response(404, "通知不存在")

    notification.is_read = True
    db.commit()
    return success_response(message="已读")


@router.put("/notifications/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return success_response(message="全部已读")


@router.post("/unbind")
async def unbind_lover(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """情侣解绑接口"""
    if not current_user.lover_id:
        return error_response(400, "您尚未绑定情侣")

    lover = db.query(User).filter(User.id == current_user.lover_id).first()
    if lover:
        lover.lover_id = None
    current_user.lover_id = None

    db.commit()
    logger.info(f"用户 {current_user.id} 解绑情侣")
    return success_response(message="解绑成功")


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """账号注销接口 - 删除用户及其关联数据"""
    # 解绑情侣
    if current_user.lover_id:
        lover = db.query(User).filter(User.id == current_user.lover_id).first()
        if lover:
            lover.lover_id = None

    # 删除关联数据
    from app.models import (
        Memory, Anniversary, Wish, Whisper, Period, DietPreference,
        Todo, Item, CheckinProject, CheckinRecord, Benefit,
        ExchangeRecord, Emotion, Bill, Achievement
    )
    uid = current_user.id
    for model in [Memory, Anniversary, Wish, Period, DietPreference,
                  Todo, Item, CheckinRecord, Emotion, Bill, Achievement, ExchangeRecord]:
        db.query(model).filter(model.user_id == uid).delete(synchronize_session=False)

    # Whisper使用sender_id/receiver_id，需单独处理
    db.query(Whisper).filter(
        (Whisper.sender_id == uid) | (Whisper.receiver_id == uid)
    ).delete(synchronize_session=False)

    # CheckinProject和Benefit通过cascade删除
    db.query(CheckinProject).filter(CheckinProject.user_id == uid).delete(synchronize_session=False)
    db.query(Benefit).filter(Benefit.user_id == uid).delete(synchronize_session=False)

    # 删除通知
    db.query(Notification).filter(Notification.user_id == uid).delete(synchronize_session=False)

    # 删除用户
    db.delete(current_user)
    db.commit()

    logger.info(f"账号注销: user_id={uid}")
    return success_response(message="账号已注销")
