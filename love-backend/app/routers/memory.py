"""
时光档案馆模块路由
处理时光线、纪念日、心愿清单、悄悄话等接口
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
from typing import Optional, List
import os
import uuid
import shutil
from app.database import get_db
from app.security import get_current_user
from app.models import User, Memory, Anniversary, Wish, Whisper
from app.schemas import (
    MemoryCreate, MemoryUpdate,
    AnniversaryCreate, AnniversaryUpdate,
    WishCreate, WishComplete,
    WhisperCreate
)
from app.response import success_response, error_response
import json


from app.utils import try_achieve

router = APIRouter()


# ==================== 时光线接口 ====================

@router.post("/timeline")
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发布时光线事件
    - 需要JWT鉴权
    - 可选择是否同步给情侣
    """
    new_memory = Memory(
        user_id=current_user.id,
        title=memory_data.title,
        content=memory_data.content,
        event_time=memory_data.event_time,
        images=memory_data.images,
        is_sync=memory_data.is_sync
    )

    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)

    # 成就检测：发布第一条时光线 -> "故事的开始"
    try_achieve(current_user.id, "故事的开始", db)

    return success_response(
        data={"id": new_memory.id},
        message="发布成功"
    )


@router.put("/timeline/{memory_id}")
async def update_memory(
    memory_id: int,
    memory_data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑时光线事件
    - 仅发布者可编辑
    """
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        return error_response(404, "时光线记录不存在")

    # 权限校验：仅发布者可编辑
    if memory.user_id != current_user.id:
        return error_response(403, "无权限编辑")

    # 更新字段
    if memory_data.title is not None:
        memory.title = memory_data.title
    if memory_data.content is not None:
        memory.content = memory_data.content
    if memory_data.event_time is not None:
        memory.event_time = memory_data.event_time
    if memory_data.images is not None:
        memory.images = memory_data.images
    if memory_data.is_sync is not None:
        memory.is_sync = memory_data.is_sync

    db.commit()
    db.refresh(memory)

    return success_response(message="编辑成功")


@router.delete("/timeline/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除时光线事件
    - 仅发布者可删除
    """
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        return error_response(404, "时光线记录不存在")

    # 权限校验：仅发布者可删除
    if memory.user_id != current_user.id:
        return error_response(403, "无权限删除")

    db.delete(memory)
    db.commit()

    return success_response(message="删除成功")


@router.get("/timeline")
async def get_memory_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取时光线列表
    - 返回本人和情侣的时光线数据
    - 按事件发生时间倒序排列
    - 支持按时间筛选
    """
    # 构建查询条件：本人或情侣的数据
    query = db.query(Memory)

    if current_user.lover_id:
        query = query.filter(
            or_(
                Memory.user_id == current_user.id,
                and_(
                    Memory.user_id == current_user.lover_id,
                    Memory.is_sync == True
                )
            )
        )
    else:
        query = query.filter(Memory.user_id == current_user.id)

    # 时间筛选
    if start_date:
        query = query.filter(Memory.event_time >= start_date)
    if end_date:
        query = query.filter(Memory.event_time <= end_date)

    # 计算总数
    total = query.count()

    # 分页查询
    memories = query.order_by(Memory.event_time.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 构建返回数据
    user_ids = list(set(m.user_id for m in memories))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    memory_list = []
    for memory in memories:
        user = users_map.get(memory.user_id)
        memory_list.append({
            "id": memory.id,
            "user_id": memory.user_id,
            "nickname": user.nickname if user else "",
            "avatar": user.avatar if user else None,
            "title": memory.title,
            "content": memory.content,
            "event_time": memory.event_time.strftime("%Y-%m-%d %H:%M:%S") if memory.event_time else None,
            "images": json.loads(memory.images) if memory.images else [],
            "is_sync": memory.is_sync,
            "created_at": memory.created_at.strftime("%Y-%m-%d %H:%M:%S") if memory.created_at else None
        })

    return success_response(
        data={
            "list": memory_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/timeline/{memory_id}")
async def get_memory_detail(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取时光线详情
    - 本人和情侣可查看
    """
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        return error_response(404, "时光线记录不存在")

    # 权限校验
    if memory.user_id != current_user.id:
        if not current_user.lover_id or memory.user_id != current_user.lover_id:
            return error_response(403, "无权限查看")
        if not memory.is_sync:
            return error_response(403, "无权限查看")

    user = db.query(User).filter(User.id == memory.user_id).first()

    memory_data = {
        "id": memory.id,
        "user_id": memory.user_id,
        "nickname": user.nickname if user else "",
        "avatar": user.avatar if user else None,
        "title": memory.title,
        "content": memory.content,
        "event_time": memory.event_time.strftime("%Y-%m-%d %H:%M:%S") if memory.event_time else None,
        "images": json.loads(memory.images) if memory.images else [],
        "is_sync": memory.is_sync,
        "created_at": memory.created_at.strftime("%Y-%m-%d %H:%M:%S") if memory.created_at else None
    }

    return success_response(data=memory_data)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    图片上传接口
    - 支持jpg/png/gif/webp格式
    - 单文件限制5MB
    - 自动压缩大图(超过1920px宽)
    - 校验文件magic bytes防止伪造
    - 返回图片访问URL
    """
    from PIL import Image
    from loguru import logger
    import io

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        return error_response(400, "仅支持jpg/png/gif/webp格式图片")

    max_size = 5 * 1024 * 1024  # 5MB
    contents = await file.read()
    if len(contents) > max_size:
        return error_response(400, "图片大小不能超过5MB")

    # Magic bytes校验 - 防止伪造文件
    magic_signatures = {
        b'\xff\xd8\xff': 'jpg',
        b'\x89PNG\r\n\x1a\n': 'png',
        b'GIF87a': 'gif',
        b'GIF89a': 'gif',
        b'RIFF': 'webp',
    }
    detected_ext = None
    for sig, ext in magic_signatures.items():
        if contents[:len(sig)] == sig:
            detected_ext = ext
            break
    if not detected_ext:
        return error_response(400, "文件内容与图片格式不符")

    # 用Pillow二次验证+压缩
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()  # 验证图片完整性
    except Exception:
        return error_response(400, "图片文件已损坏")

    # 重新打开（verify后需要重新open）
    img = Image.open(io.BytesIO(contents))

    # 压缩：宽度超过1920px时等比缩放
    max_width = 1920
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        logger.info(f"图片压缩: {file.filename} {img.width}x{img.height} -> {new_size[0]}x{new_size[1]}")

    # 重新编码保存
    ext_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "gif": "GIF", "webp": "WEBP"}
    save_ext = detected_ext if detected_ext != "gif" else "png"  # gif转png保存（压缩后）
    pil_format = ext_map.get(save_ext, "JPEG")

    buf = io.BytesIO()
    if pil_format == "PNG":
        img.save(buf, format="PNG", optimize=True)
    elif pil_format == "WEBP":
        img.save(buf, format="WEBP", quality=85)
    else:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=85, optimize=True)
    contents = buf.getvalue()

    # 生成唯一文件名
    filename = f"{uuid.uuid4().hex}.{save_ext}"

    # 保存到本地 uploads 目录
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    logger.info(f"图片上传: user={current_user.id} file={filename} size={len(contents)}")
    url = f"/uploads/{filename}"
    return success_response(
        data={"url": url},
        message="上传成功"
    )


# ==================== 纪念日接口 ====================

@router.post("/anniversary")
async def create_anniversary(
    anniversary_data: AnniversaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建纪念日
    - 支持个人纪念日和情侣纪念日
    """
    new_anniversary = Anniversary(
        user_id=current_user.id,
        title=anniversary_data.title,
        target_date=anniversary_data.target_date,
        is_yearly=anniversary_data.is_yearly,
        remind_days=anniversary_data.remind_days,
        type=anniversary_data.type,
        note=anniversary_data.note
    )

    db.add(new_anniversary)
    db.commit()
    db.refresh(new_anniversary)

    return success_response(
        data={"id": new_anniversary.id},
        message="创建成功"
    )


@router.put("/anniversary/{anniversary_id}")
async def update_anniversary(
    anniversary_id: int,
    anniversary_data: AnniversaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑纪念日
    - 个人纪念日仅本人可编辑
    - 情侣纪念日双方均可编辑
    """
    anniversary = db.query(Anniversary).filter(Anniversary.id == anniversary_id).first()
    if not anniversary:
        return error_response(404, "纪念日不存在")

    # 权限校验
    if anniversary.type == "personal" and anniversary.user_id != current_user.id:
        return error_response(403, "无权限编辑")
    elif anniversary.type == "couple":
        if anniversary.user_id != current_user.id:
            if not current_user.lover_id or anniversary.user_id != current_user.lover_id:
                return error_response(403, "无权限编辑")

    # 更新字段
    if anniversary_data.title is not None:
        anniversary.title = anniversary_data.title
    if anniversary_data.target_date is not None:
        anniversary.target_date = anniversary_data.target_date
    if anniversary_data.is_yearly is not None:
        anniversary.is_yearly = anniversary_data.is_yearly
    if anniversary_data.remind_days is not None:
        anniversary.remind_days = anniversary_data.remind_days
    if anniversary_data.type is not None:
        anniversary.type = anniversary_data.type
    if anniversary_data.note is not None:
        anniversary.note = anniversary_data.note

    db.commit()
    db.refresh(anniversary)

    return success_response(message="编辑成功")


@router.delete("/anniversary/{anniversary_id}")
async def delete_anniversary(
    anniversary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除纪念日
    - 个人纪念日仅本人可删除
    - 情侣纪念日双方均可删除
    """
    anniversary = db.query(Anniversary).filter(Anniversary.id == anniversary_id).first()
    if not anniversary:
        return error_response(404, "纪念日不存在")

    # 权限校验
    if anniversary.type == "personal" and anniversary.user_id != current_user.id:
        return error_response(403, "无权限删除")
    elif anniversary.type == "couple":
        if anniversary.user_id != current_user.id:
            if not current_user.lover_id or anniversary.user_id != current_user.lover_id:
                return error_response(403, "无权限删除")

    db.delete(anniversary)
    db.commit()

    return success_response(message="删除成功")


@router.get("/anniversary")
async def get_anniversary_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取纪念日列表
    - 返回本人和情侣的纪念日
    - 按目标日期排序
    """
    today = date.today()

    # 查询本人和情侣的纪念日
    query = db.query(Anniversary)
    if current_user.lover_id:
        query = query.filter(
            or_(
                Anniversary.user_id == current_user.id,
                and_(
                    Anniversary.user_id == current_user.lover_id,
                    Anniversary.type == "couple"
                )
            )
        )
    else:
        query = query.filter(Anniversary.user_id == current_user.id)

    anniversaries = query.order_by(Anniversary.target_date).all()

    # 批量查询用户信息
    user_ids = list(set(a.user_id for a in anniversaries))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # 构建返回数据
    anniversary_list = []
    for anniversary in anniversaries:
        # 计算倒计时
        target_date = anniversary.target_date
        if anniversary.is_yearly:
            this_year_target = target_date.replace(year=today.year)
            if this_year_target < today:
                this_year_target = target_date.replace(year=today.year + 1)
            target_date = this_year_target

        days_left = (target_date - today).days

        user = users_map.get(anniversary.user_id)
        anniversary_list.append({
            "id": anniversary.id,
            "user_id": anniversary.user_id,
            "nickname": user.nickname if user else "",
            "title": anniversary.title,
            "target_date": target_date.strftime("%Y-%m-%d"),
            "is_yearly": anniversary.is_yearly,
            "remind_days": anniversary.remind_days,
            "type": anniversary.type,
            "note": anniversary.note,
            "days_left": days_left,
            "created_at": anniversary.created_at.strftime("%Y-%m-%d %H:%M:%S") if anniversary.created_at else None
        })

    return success_response(data=anniversary_list)


# ==================== 心愿清单接口 ====================

@router.post("/wish")
async def create_wish(
    wish_data: WishCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建心愿
    - 支持个人心愿和情侣心愿
    """
    new_wish = Wish(
        user_id=current_user.id,
        content=wish_data.content,
        type=wish_data.type,
        note=wish_data.note
    )

    db.add(new_wish)
    db.commit()
    db.refresh(new_wish)

    return success_response(
        data={"id": new_wish.id},
        message="创建成功"
    )


@router.put("/wish/{wish_id}/complete")
async def complete_wish(
    wish_id: int,
    complete_data: WishComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记心愿完成
    - 需要填写完成时间、上传打卡图片
    - 完成后自动同步到时光线
    """
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        return error_response(404, "心愿不存在")

    # 权限校验
    if wish.type == "personal" and wish.user_id != current_user.id:
        return error_response(403, "无权限操作")
    elif wish.type == "couple":
        if wish.user_id != current_user.id:
            if not current_user.lover_id or wish.user_id != current_user.lover_id:
                return error_response(403, "无权限操作")

    # 更新心愿状态
    wish.status = "completed"
    wish.complete_time = complete_data.complete_time
    wish.image = complete_data.image

    # 自动同步到时光线（发布者为心愿创建者）
    new_memory = Memory(
        user_id=wish.user_id,
        title=f"完成心愿：{wish.content}",
        content=wish.content,
        event_time=complete_data.complete_time,
        images=json.dumps([wish.image]) if wish.image else None,
        is_sync=True
    )
    db.add(new_memory)

    db.commit()
    db.refresh(wish)

    # 成就检测：完成情侣心愿 -> "旅行最佳搭子"
    if wish.type == "couple":
        try_achieve(wish.user_id, "旅行最佳搭子", db)

    return success_response(message="心愿已完成")


@router.delete("/wish/{wish_id}")
async def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除心愿
    - 仅创建者可删除
    """
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        return error_response(404, "心愿不存在")

    # 权限校验：仅创建者可删除
    if wish.user_id != current_user.id:
        return error_response(403, "无权限删除")

    db.delete(wish)
    db.commit()

    return success_response(message="删除成功")


@router.get("/wish")
async def get_wish_list(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取心愿列表
    - 返回本人和情侣的心愿
    - 支持按状态筛选
    """
    # 查询本人和情侣的心愿
    query = db.query(Wish)
    if current_user.lover_id:
        query = query.filter(
            or_(
                Wish.user_id == current_user.id,
                and_(
                    Wish.user_id == current_user.lover_id,
                    Wish.type == "couple"
                )
            )
        )
    else:
        query = query.filter(Wish.user_id == current_user.id)

    # 状态筛选
    if status:
        query = query.filter(Wish.status == status)

    wishes = query.order_by(Wish.created_at.desc()).all()

    # 批量查询用户信息
    user_ids = list(set(w.user_id for w in wishes))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # 构建返回数据
    wish_list = []
    for wish in wishes:
        user = users_map.get(wish.user_id)
        wish_list.append({
            "id": wish.id,
            "user_id": wish.user_id,
            "nickname": user.nickname if user else "",
            "content": wish.content,
            "status": wish.status,
            "complete_time": wish.complete_time.strftime("%Y-%m-%d %H:%M:%S") if wish.complete_time else None,
            "note": wish.note,
            "image": wish.image,
            "type": wish.type,
            "created_at": wish.created_at.strftime("%Y-%m-%d %H:%M:%S") if wish.created_at else None
        })

    return success_response(data=wish_list)


# ==================== 悄悄话接口 ====================

@router.post("/whisper")
async def create_whisper(
    whisper_data: WhisperCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送悄悄话
    - 仅绑定情侣可互发
    - 支持定时发送
    """
    # 检查是否绑定情侣
    if not current_user.lover_id:
        return error_response(400, "请先绑定情侣")

    # 定时发送必须提供定时时间
    if whisper_data.is_scheduled and not whisper_data.scheduled_time:
        return error_response(400, "定时发送必须设置发送时间")

    # 创建悄悄话
    new_whisper = Whisper(
        sender_id=current_user.id,
        receiver_id=current_user.lover_id,
        content=whisper_data.content,
        is_scheduled=whisper_data.is_scheduled,
        scheduled_time=whisper_data.scheduled_time
    )

    # 如果不是定时发送，设置发送时间
    if not whisper_data.is_scheduled:
        new_whisper.send_time = datetime.now()

    db.add(new_whisper)
    db.commit()
    db.refresh(new_whisper)

    return success_response(
        data={"id": new_whisper.id},
        message="发送成功"
    )


@router.put("/whisper/{whisper_id}/read")
async def mark_whisper_read(
    whisper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记悄悄话已读
    - 接收人打开悄悄话后自动标记
    """
    whisper = db.query(Whisper).filter(Whisper.id == whisper_id).first()
    if not whisper:
        return error_response(404, "悄悄话不存在")

    # 权限校验：仅接收人可标记已读
    if whisper.receiver_id != current_user.id:
        return error_response(403, "无权限操作")

    whisper.is_read = True
    db.commit()

    return success_response(message="已标记已读")


@router.get("/whisper")
async def get_whisper_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取悄悄话列表
    - 返回与情侣之间的悄悄话
    - 按发送时间倒序排列
    """
    if not current_user.lover_id:
        return success_response(data={"list": [], "total": 0})

    # 查询与情侣之间的悄悄话
    # 定时消息在发送时间前对接收方隐藏
    now = datetime.now()
    query = db.query(Whisper).filter(
        or_(
            and_(
                Whisper.sender_id == current_user.id,
                Whisper.receiver_id == current_user.lover_id
            ),
            and_(
                Whisper.sender_id == current_user.lover_id,
                Whisper.receiver_id == current_user.id,
                # 对接收方：已发送的（send_time不为空）或定时时间已到的才显示
                or_(
                    Whisper.send_time.isnot(None),
                    and_(Whisper.is_scheduled == True, Whisper.scheduled_time <= now),
                    Whisper.is_scheduled == False
                )
            )
        )
    )

    # 计算总数
    total = query.count()

    # 分页查询
    whispers = query.order_by(Whisper.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 批量查询用户信息
    sender_ids = list(set(w.sender_id for w in whispers))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(sender_ids)).all()} if sender_ids else {}

    # 构建返回数据
    whisper_list = []
    for whisper in whispers:
        sender = users_map.get(whisper.sender_id)
        whisper_list.append({
            "id": whisper.id,
            "sender_id": whisper.sender_id,
            "sender_nickname": sender.nickname if sender else "",
            "sender_avatar": sender.avatar if sender else None,
            "content": whisper.content,
            "send_time": whisper.send_time.strftime("%Y-%m-%d %H:%M:%S") if whisper.send_time else None,
            "is_read": whisper.is_read,
            "is_self": whisper.sender_id == current_user.id,
            "is_scheduled": whisper.is_scheduled,
            "scheduled_time": whisper.scheduled_time.strftime("%Y-%m-%d %H:%M:%S") if whisper.scheduled_time else None,
            "created_at": whisper.created_at.strftime("%Y-%m-%d %H:%M:%S") if whisper.created_at else None
        })

    return success_response(
        data={
            "list": whisper_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/debug/test-achieve")
async def test_achieve(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to test achievement unlock"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.routers.love import try_unlock_achievement
        logger.info(f"Import success, calling try_unlock_achievement for user {current_user.id}")
        result = try_unlock_achievement(current_user.id, "故事的开始", db)
        logger.info(f"Result: {result}")
        return success_response({"result": result, "user_id": current_user.id})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return error_response(500, str(e))
