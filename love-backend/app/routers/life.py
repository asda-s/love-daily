"""
生活管家模块路由
处理生理期管理、饮食偏好、待办事项、好物收纳等接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date, timedelta
from typing import Optional, List
import json
import asyncio
from app.database import get_db
from app.security import get_current_user
from app.models import (
    User, Period, DietPreference, Todo,
    MoodDiary, MoodDiaryReaction, MoodDiaryReply, MoodDiaryDraft,
    Notification
)
from app.schemas import (
    PeriodCreate, PeriodUpdate,
    DietPreferenceCreate,
    TodoCreate, TodoUpdate,
    MoodDiaryCreate, MoodDiaryUpdate,
    MoodDiaryReactionCreate, MoodDiaryReplyCreate,
    MoodDiaryDraftSave
)
from app.response import success_response, error_response
from app.routers.websocket import broadcast_to_user


from app.utils import try_achieve

router = APIRouter()

REACTION_EMOJI = {"hug": "\U0001f917", "kiss": "\U0001f618", "like": "\U0001f44d", "cheer": "\U0001f4aa", "pat": "\U0001f970", "heart": "\U0001faf0"}


# ==================== 生理期管理接口 ====================

@router.post("/period")
async def create_period(
    period_data: PeriodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建生理期记录
    - 仅本人可创建
    """
    new_period = Period(
        user_id=current_user.id,
        start_date=period_data.start_date,
        cycle_days=period_data.cycle_days,
        duration_days=period_data.duration_days,
        note=period_data.note,
        body_status=period_data.body_status
    )

    db.add(new_period)
    db.commit()
    db.refresh(new_period)

    # 成就检测：连续3个周期有生理期记录 -> "生理期小太阳"
    period_count = db.query(Period).filter(Period.user_id == current_user.id).count()
    if period_count >= 3:
        try_achieve(current_user.id, "生理期小太阳", db)

    return success_response(
        data={"id": new_period.id},
        message="记录成功"
    )


@router.get("/period/predict")
async def predict_period(
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取生理期预测信息
    - 基于多条记录的加权平均进行预测
    - 情侣可查看此接口（通过user_id参数指定）
    """
    # 确定查询目标：默认查自己，传了user_id则查对方（需权限校验）
    target_id = current_user.id
    if user_id and user_id != current_user.id:
        if not current_user.lover_id or user_id != current_user.lover_id:
            return error_response(403, "无权限查看")
        target_id = user_id

    # 获取最近的生理期记录（最多取6条用于加权平均）
    recent_periods = db.query(Period).filter(
        Period.user_id == target_id
    ).order_by(Period.start_date.desc()).limit(6).all()

    if not recent_periods:
        return success_response(data=None, message="暂无记录")

    latest = recent_periods[0]
    today = date.today()

    # 计算加权平均周期和经期天数（越近的记录权重越高）
    if len(recent_periods) >= 2:
        total_weight = 0
        weighted_cycle = 0
        weighted_duration = 0
        for i, p in enumerate(recent_periods):
            weight = len(recent_periods) - i  # 最新的权重最高
            weighted_cycle += p.cycle_days * weight
            weighted_duration += p.duration_days * weight
            total_weight += weight
        avg_cycle = round(weighted_cycle / total_weight)
        avg_duration = round(weighted_duration / total_weight)
    else:
        avg_cycle = latest.cycle_days
        avg_duration = latest.duration_days

    # 计算下次经期开始日期
    next_period_start = latest.start_date + timedelta(days=avg_cycle)

    # 如果预测日期已过，继续往后推算
    while next_period_start <= today:
        next_period_start += timedelta(days=avg_cycle)

    next_period_end = next_period_start + timedelta(days=avg_duration - 1)

    # 排卵期预测：下次月经前14天为排卵日，前5天到后1天为排卵期
    ovulation_day = next_period_start - timedelta(days=14)
    ovulation_start = ovulation_day - timedelta(days=5)
    ovulation_end = ovulation_day + timedelta(days=1)

    # 安全期预测：
    # 前安全期：下次经期结束后到排卵期开始前
    # 后安全期：排卵期结束后到下下次经期前
    safe_before_start = next_period_end + timedelta(days=1)
    safe_before_end = ovulation_start - timedelta(days=1)
    safe_after_start = ovulation_end + timedelta(days=1)
    safe_after_end = next_period_start + timedelta(days=avg_cycle) - timedelta(days=1)

    # 计算倒计时
    days_to_next = (next_period_start - today).days

    predict_data = {
        "latest_period": {
            "start_date": latest.start_date.strftime("%Y-%m-%d"),
            "cycle_days": avg_cycle,
            "duration_days": avg_duration,
            "record_count": len(recent_periods)
        },
        "next_period": {
            "start_date": next_period_start.strftime("%Y-%m-%d"),
            "end_date": next_period_end.strftime("%Y-%m-%d"),
            "days_left": days_to_next
        },
        "ovulation": {
            "day": ovulation_day.strftime("%Y-%m-%d"),
            "start_date": ovulation_start.strftime("%Y-%m-%d"),
            "end_date": ovulation_end.strftime("%Y-%m-%d")
        },
        "safe_period": {
            "before": {
                "start_date": safe_before_start.strftime("%Y-%m-%d"),
                "end_date": safe_before_end.strftime("%Y-%m-%d")
            },
            "after": {
                "start_date": safe_after_start.strftime("%Y-%m-%d"),
                "end_date": safe_after_end.strftime("%Y-%m-%d")
            }
        }
    }

    return success_response(data=predict_data)


@router.get("/period/{period_id}")
async def get_period_detail(
    period_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单条生理期记录详情
    """
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        return error_response(404, "记录不存在")
    if period.user_id != current_user.id:
        return error_response(403, "无权限查看")

    end_date = period.start_date + timedelta(days=period.duration_days - 1)
    return success_response(data={
        "id": period.id,
        "start_date": period.start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "cycle_days": period.cycle_days,
        "duration_days": period.duration_days,
        "note": period.note,
        "body_status": period.body_status
    })


@router.put("/period/{period_id}")
async def update_period(
    period_id: int,
    period_data: PeriodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑生理期记录
    - 仅本人可编辑
    """
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        return error_response(404, "记录不存在")

    # 权限校验：仅本人可编辑
    if period.user_id != current_user.id:
        return error_response(403, "无权限编辑")

    # 更新字段
    if period_data.start_date is not None:
        period.start_date = period_data.start_date
    if period_data.cycle_days is not None:
        period.cycle_days = period_data.cycle_days
    if period_data.duration_days is not None:
        period.duration_days = period_data.duration_days
    if period_data.note is not None:
        period.note = period_data.note
    if period_data.body_status is not None:
        period.body_status = period_data.body_status

    db.commit()
    db.refresh(period)

    return success_response(message="编辑成功")


@router.delete("/period/{period_id}")
async def delete_period(
    period_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除生理期记录
    - 仅本人可删除
    """
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        return error_response(404, "记录不存在")

    # 权限校验：仅本人可删除
    if period.user_id != current_user.id:
        return error_response(403, "无权限删除")

    db.delete(period)
    db.commit()

    return success_response(message="删除成功")


@router.get("/period")
async def get_period_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取生理期记录列表
    - 本人可查看完整记录
    - 情侣仅可查看预测信息
    """
    # 查询本人的生理期记录
    periods = db.query(Period).filter(
        Period.user_id == current_user.id
    ).order_by(Period.start_date.desc()).all()

    # 构建返回数据
    period_list = []
    for period in periods:
        end_date = period.start_date + timedelta(days=period.duration_days - 1)
        period_list.append({
            "id": period.id,
            "user_id": period.user_id,
            "start_date": period.start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "cycle_days": period.cycle_days,
            "duration_days": period.duration_days,
            "duration": period.duration_days,
            "note": period.note,
            "body_status": period.body_status,
            "created_at": period.created_at.strftime("%Y-%m-%d %H:%M:%S") if period.created_at else None
        })

    return success_response(data=period_list)


# ==================== 饮食偏好接口 ====================

@router.get("/diet")
async def get_diet_preference(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取饮食偏好档案
    - 本人可查看完整信息
    - 情侣仅可查看
    """
    preference = db.query(DietPreference).filter(
        DietPreference.user_id == current_user.id
    ).first()

    if not preference:
        return success_response(data=None, message="暂未设置")

    pref_data = {
        "id": preference.id,
        "user_id": preference.user_id,
        "liked_food": preference.liked_food,
        "avoid_food": preference.avoid_food,
        "allergic_food": preference.allergic_food,
        "coffee_pref": preference.coffee_pref,
        "delivery_address": preference.delivery_address,
        "note": preference.note,
        "created_at": preference.created_at.strftime("%Y-%m-%d %H:%M:%S") if preference.created_at else None,
        "updated_at": preference.updated_at.strftime("%Y-%m-%d %H:%M:%S") if preference.updated_at else None
    }

    return success_response(data=pref_data)


@router.get("/diet/{user_id}")
async def get_lover_diet_preference(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取情侣的饮食偏好档案
    - 仅绑定情侣可查看
    """
    # 权限校验
    if user_id != current_user.id:
        if not current_user.lover_id or user_id != current_user.lover_id:
            return error_response(403, "无权限查看")

    preference = db.query(DietPreference).filter(
        DietPreference.user_id == user_id
    ).first()

    if not preference:
        return success_response(data=None, message="暂未设置")

    pref_data = {
        "id": preference.id,
        "user_id": preference.user_id,
        "liked_food": preference.liked_food,
        "avoid_food": preference.avoid_food,
        "allergic_food": preference.allergic_food,
        "coffee_pref": preference.coffee_pref,
        "delivery_address": preference.delivery_address,
        "note": preference.note
    }

    return success_response(data=pref_data)


@router.post("/diet")
async def create_or_update_diet_preference(
    diet_data: DietPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建或更新饮食偏好档案
    - 仅本人可编辑
    """
    # 查找现有记录
    preference = db.query(DietPreference).filter(
        DietPreference.user_id == current_user.id
    ).first()

    if preference:
        # 更新记录
        if diet_data.liked_food is not None:
            preference.liked_food = diet_data.liked_food
        if diet_data.avoid_food is not None:
            preference.avoid_food = diet_data.avoid_food
        if diet_data.allergic_food is not None:
            preference.allergic_food = diet_data.allergic_food
        if diet_data.coffee_pref is not None:
            preference.coffee_pref = diet_data.coffee_pref
        if diet_data.delivery_address is not None:
            preference.delivery_address = diet_data.delivery_address
        if diet_data.note is not None:
            preference.note = diet_data.note
    else:
        # 创建新记录
        preference = DietPreference(
            user_id=current_user.id,
            liked_food=diet_data.liked_food,
            avoid_food=diet_data.avoid_food,
            allergic_food=diet_data.allergic_food,
            coffee_pref=diet_data.coffee_pref,
            delivery_address=diet_data.delivery_address,
            note=diet_data.note
        )
        db.add(preference)

    db.commit()
    db.refresh(preference)

    # 成就检测：完整填写饮食偏好 -> "满分守护者"
    if preference.liked_food and preference.avoid_food and preference.allergic_food:
        try_achieve(current_user.id, "满分守护者", db)

    return success_response(message="保存成功")


# ==================== 待办事项接口 ====================

@router.post("/todo")
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建待办事项
    - 支持个人待办和情侣待办
    """
    new_todo = Todo(
        user_id=current_user.id,
        title=todo_data.title,
        deadline=todo_data.deadline,
        remind_time=todo_data.remind_time,
        note=todo_data.note,
        type=todo_data.type
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return success_response(
        data={"id": new_todo.id},
        message="创建成功"
    )


@router.put("/todo/{todo_id}")
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑待办事项
    - 个人待办仅本人可编辑
    - 情侣待办双方均可编辑
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        return error_response(404, "待办不存在")

    # 权限校验
    if todo.type == "personal" and todo.user_id != current_user.id:
        return error_response(403, "无权限编辑")
    elif todo.type == "couple":
        if todo.user_id != current_user.id:
            if not current_user.lover_id or todo.user_id != current_user.lover_id:
                return error_response(403, "无权限编辑")

    # 更新字段
    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.deadline is not None:
        todo.deadline = todo_data.deadline
    if todo_data.remind_time is not None:
        todo.remind_time = todo_data.remind_time
    if todo_data.note is not None:
        todo.note = todo_data.note
    if todo_data.status is not None:
        todo.status = todo_data.status

    db.commit()
    db.refresh(todo)

    return success_response(message="编辑成功")


@router.delete("/todo/{todo_id}")
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除待办事项
    - 仅创建者可删除
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        return error_response(404, "待办不存在")

    # 权限校验：仅创建者可删除
    if todo.user_id != current_user.id:
        return error_response(403, "无权限删除")

    db.delete(todo)
    db.commit()

    return success_response(message="删除成功")


@router.get("/todo")
async def get_todo_list(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取待办事项列表
    - 返回本人和情侣的待办
    - 支持按状态筛选
    """
    # 查询本人和情侣的待办
    query = db.query(Todo)
    if current_user.lover_id:
        query = query.filter(
            or_(
                Todo.user_id == current_user.id,
                and_(
                    Todo.user_id == current_user.lover_id,
                    Todo.type == "couple"
                )
            )
        )
    else:
        query = query.filter(Todo.user_id == current_user.id)

    # 状态筛选
    if status:
        query = query.filter(Todo.status == status)

    todos = query.order_by(Todo.created_at.desc()).all()

    # 批量查询用户信息
    user_ids = list(set(t.user_id for t in todos))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # 构建返回数据
    todo_list = []
    for todo in todos:
        user = users_map.get(todo.user_id)
        todo_list.append({
            "id": todo.id,
            "user_id": todo.user_id,
            "nickname": user.nickname if user else "",
            "title": todo.title,
            "deadline": todo.deadline.strftime("%Y-%m-%d %H:%M:%S") if todo.deadline else None,
            "remind_time": todo.remind_time.strftime("%Y-%m-%d %H:%M:%S") if todo.remind_time else None,
            "note": todo.note,
            "status": todo.status,
            "type": todo.type,
            "created_at": todo.created_at.strftime("%Y-%m-%d %H:%M:%S") if todo.created_at else None
        })

    return success_response(data=todo_list)


# ==================== 心情日记接口 ====================

@router.post("/diary")
async def create_diary(
    data: MoodDiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建心情日记
    - 最多9张图片，最多3个标签
    """
    images_json = json.dumps(data.images) if data.images else None
    tags_json = json.dumps(data.tags) if data.tags else None
    diary = MoodDiary(
        user_id=current_user.id,
        mood_type=data.mood_type,
        mood_intensity=data.mood_intensity,
        second_mood=data.second_mood,
        content=data.content,
        images=images_json,
        tags=tags_json,
        diary_date=data.diary_date,
        publish_status=data.publish_status,
        scheduled_time=data.scheduled_time
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)

    # 检查日记成就
    if data.publish_status == "published":
        try:
            from app.routers.love import check_diary_achievements
            check_diary_achievements(current_user.id, db)
        except Exception:
            pass

    # If published immediately and has lover, create notification
    if data.publish_status == "published" and current_user.lover_id:
        notification = Notification(
            user_id=current_user.lover_id,
            title="心情日记",
            content=f"{current_user.nickname or 'TA'}发布了一篇心情日记",
            type="diary"
        )
        db.add(notification)
        db.commit()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    broadcast_to_user(
                        current_user.lover_id,
                        {
                            "type": "notification",
                            "data": {
                                "title": "心情日记",
                                "content": f"{current_user.nickname or 'TA'}发布了一篇心情日记",
                                "notification_type": "diary"
                            }
                        }
                    ),
                    loop
                )
        except:
            pass

    return success_response(data={"id": diary.id}, message="发布成功")


@router.put("/diary/draft")
async def save_draft(
    data: MoodDiaryDraftSave,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存心情日记草稿
    """
    draft = db.query(MoodDiaryDraft).filter(MoodDiaryDraft.user_id == current_user.id).first()
    if draft:
        draft.content = data.content
    else:
        draft = MoodDiaryDraft(user_id=current_user.id, content=data.content)
        db.add(draft)
    db.commit()
    return success_response(message="草稿已保存")


@router.get("/diary/draft")
async def get_draft(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取心情日记草稿
    """
    draft = db.query(MoodDiaryDraft).filter(MoodDiaryDraft.user_id == current_user.id).first()
    if not draft:
        return success_response(data=None)
    return success_response(data={
        "content": draft.content,
        "updated_at": draft.updated_at.strftime("%Y-%m-%d %H:%M:%S") if draft.updated_at else None
    })


@router.get("/diary/search")
async def search_diaries(
    keyword: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索心情日记
    - 按内容关键字搜索
    """
    query = db.query(MoodDiary).filter(MoodDiary.publish_status == "published", MoodDiary.content.contains(keyword))
    if current_user.lover_id:
        query = query.filter(or_(MoodDiary.user_id == current_user.id, MoodDiary.user_id == current_user.lover_id))
    else:
        query = query.filter(MoodDiary.user_id == current_user.id)

    diaries = query.order_by(MoodDiary.created_at.desc()).limit(50).all()
    user_ids = list(set(d.user_id for d in diaries))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    result = [
        {
            "id": d.id,
            "user_id": d.user_id,
            "nickname": (users_map.get(d.user_id).nickname if users_map.get(d.user_id) else ""),
            "mood_type": d.mood_type,
            "content": d.content[:100],
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for d in diaries
    ]
    return success_response(data=result)


@router.get("/diary/calendar")
async def mood_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    心情日历
    - 返回指定月份每天的心情记录
    """
    from datetime import date as date_type
    start = date_type(year, month, 1)
    if month == 12:
        end = date_type(year + 1, 1, 1)
    else:
        end = date_type(year, month + 1, 1)

    query = db.query(MoodDiary).filter(
        MoodDiary.publish_status == "published",
        MoodDiary.diary_date >= start,
        MoodDiary.diary_date < end
    )
    if current_user.lover_id:
        query = query.filter(or_(MoodDiary.user_id == current_user.id, MoodDiary.user_id == current_user.lover_id))
    else:
        query = query.filter(MoodDiary.user_id == current_user.id)

    diaries = query.all()
    calendar = {}
    for d in diaries:
        day = d.diary_date.day
        if day not in calendar:
            calendar[day] = []
        calendar[day].append({
            "user_id": d.user_id,
            "mood_type": d.mood_type,
            "mood_intensity": d.mood_intensity,
            "diary_id": d.id
        })

    return success_response(data={"year": year, "month": month, "calendar": calendar})


@router.get("/diary/report")
async def emotion_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    每周情绪报告
    """
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)

    query = db.query(MoodDiary).filter(
        MoodDiary.publish_status == "published",
        MoodDiary.created_at >= week_start,
        MoodDiary.created_at < week_end
    )
    if current_user.lover_id:
        query = query.filter(or_(MoodDiary.user_id == current_user.id, MoodDiary.user_id == current_user.lover_id))
    else:
        query = query.filter(MoodDiary.user_id == current_user.id)

    diaries = query.all()
    my_diaries = [d for d in diaries if d.user_id == current_user.id]
    lover_diaries = [d for d in diaries if d.user_id != current_user.id] if current_user.lover_id else []

    # Mood distribution
    mood_names = {
        "happy": "开心", "sweet": "甜蜜", "calm": "平静", "tired": "疲惫",
        "sad": "难过", "angry": "生气", "wronged": "委屈", "surprised": "惊喜"
    }
    my_mood_dist = {}
    for d in my_diaries:
        name = mood_names.get(d.mood_type, d.mood_type)
        my_mood_dist[name] = my_mood_dist.get(name, 0) + 1
    lover_mood_dist = {}
    for d in lover_diaries:
        name = mood_names.get(d.mood_type, d.mood_type)
        lover_mood_dist[name] = lover_mood_dist.get(name, 0) + 1

    # Daily trend
    daily_moods = {}
    for d in diaries:
        day_key = d.created_at.strftime("%m-%d")
        if day_key not in daily_moods:
            daily_moods[day_key] = []
        daily_moods[day_key].append({
            "user_id": d.user_id,
            "mood": d.mood_type,
            "intensity": d.mood_intensity
        })

    return success_response(data={
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
        "my_count": len(my_diaries),
        "lover_count": len(lover_diaries),
        "my_mood_distribution": my_mood_dist,
        "lover_mood_distribution": lover_mood_dist,
        "daily_trend": daily_moods
    })


@router.get("/diary/{diary_id}")
async def get_diary_detail(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取心情日记详情
    - 自动标记已读
    """
    diary = db.query(MoodDiary).filter(MoodDiary.id == diary_id).first()
    if not diary:
        return error_response(404, "日记不存在")

    # Check permission
    if current_user.lover_id:
        if diary.user_id != current_user.id and diary.user_id != current_user.lover_id:
            return error_response(403, "无权查看")
    elif diary.user_id != current_user.id:
        return error_response(403, "无权查看")

    # Mark as read if viewer is the partner
    if diary.user_id != current_user.id and not diary.is_read:
        diary.is_read = True
        diary.read_time = datetime.now()
        db.commit()

    user = db.query(User).filter(User.id == diary.user_id).first()
    reactions = db.query(MoodDiaryReaction).filter(MoodDiaryReaction.diary_id == diary_id).all()
    reaction_users = {u.id: u for u in db.query(User).filter(User.id.in_(list(set(r.user_id for r in reactions)))).all()} if reactions else {}
    reaction_list = [
        {
            "type": r.reaction_type,
            "emoji": REACTION_EMOJI.get(r.reaction_type, ""),
            "user_id": r.user_id,
            "nickname": (reaction_users.get(r.user_id).nickname if reaction_users.get(r.user_id) else "")
        }
        for r in reactions
    ]

    # My reaction
    my_reaction = db.query(MoodDiaryReaction).filter(
        MoodDiaryReaction.diary_id == diary_id,
        MoodDiaryReaction.user_id == current_user.id
    ).first()

    return success_response(data={
        "id": diary.id,
        "user_id": diary.user_id,
        "nickname": user.nickname if user else "",
        "avatar": user.avatar if user else None,
        "mood_type": diary.mood_type,
        "mood_intensity": diary.mood_intensity,
        "second_mood": diary.second_mood,
        "content": diary.content,
        "images": json.loads(diary.images) if diary.images else [],
        "tags": json.loads(diary.tags) if diary.tags else [],
        "is_read": diary.is_read,
        "read_time": diary.read_time.strftime("%Y-%m-%d %H:%M:%S") if diary.read_time else None,
        "diary_date": diary.diary_date.isoformat() if diary.diary_date else None,
        "publish_status": diary.publish_status,
        "scheduled_time": diary.scheduled_time.strftime("%Y-%m-%d %H:%M:%S") if diary.scheduled_time else None,
        "reactions": reaction_list,
        "my_reaction": my_reaction.reaction_type if my_reaction else None,
        "created_at": diary.created_at.strftime("%Y-%m-%d %H:%M:%S") if diary.created_at else None
    })


@router.put("/diary/{diary_id}")
async def update_diary(
    diary_id: int,
    data: MoodDiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑心情日记
    - 仅本人可编辑
    """
    diary = db.query(MoodDiary).filter(MoodDiary.id == diary_id).first()
    if not diary:
        return error_response(404, "日记不存在")
    if diary.user_id != current_user.id:
        return error_response(403, "无权编辑")

    for field in ['mood_type', 'mood_intensity', 'second_mood', 'content']:
        val = getattr(data, field)
        if val is not None:
            setattr(diary, field, val)
    if data.images is not None:
        diary.images = json.dumps(data.images)
    if data.tags is not None:
        diary.tags = json.dumps(data.tags)
    if data.diary_date is not None:
        diary.diary_date = data.diary_date
    if data.publish_status is not None:
        diary.publish_status = data.publish_status
    if data.scheduled_time is not None:
        diary.scheduled_time = data.scheduled_time

    db.commit()
    return success_response(message="编辑成功")


@router.delete("/diary/{diary_id}")
async def delete_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除心情日记
    - 仅本人可删除
    """
    diary = db.query(MoodDiary).filter(MoodDiary.id == diary_id).first()
    if not diary:
        return error_response(404, "日记不存在")
    if diary.user_id != current_user.id:
        return error_response(403, "无权删除")

    # Delete reactions and replies first
    db.query(MoodDiaryReaction).filter(MoodDiaryReaction.diary_id == diary_id).delete()
    db.query(MoodDiaryReply).filter(MoodDiaryReply.diary_id == diary_id).delete()
    db.delete(diary)
    db.commit()
    return success_response(message="删除成功")


@router.get("/diary")
async def list_diaries(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    mood_type: Optional[str] = None,
    tag: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取心情日记列表（分页，支持筛选）
    - 返回本人和情侣的已发布日记
    """
    query = db.query(MoodDiary).filter(MoodDiary.publish_status == "published")
    if current_user.lover_id:
        query = query.filter(or_(MoodDiary.user_id == current_user.id, MoodDiary.user_id == current_user.lover_id))
    else:
        query = query.filter(MoodDiary.user_id == current_user.id)

    if mood_type:
        query = query.filter(MoodDiary.mood_type == mood_type)
    if user_id:
        query = query.filter(MoodDiary.user_id == user_id)
    if start_date:
        query = query.filter(MoodDiary.created_at >= start_date)
    if end_date:
        query = query.filter(MoodDiary.created_at <= end_date)

    query = query.order_by(MoodDiary.created_at.desc())

    if tag:
        # Tag filter requires JSON parsing, so over-fetch and filter in Python
        all_diaries = query.limit(500).all()
        filtered = []
        for d in all_diaries:
            tags = json.loads(d.tags) if d.tags else []
            if tag in tags:
                filtered.append(d)
        total = len(filtered)
        diaries = filtered[(page - 1) * page_size: page * page_size]
    else:
        total = query.count()
        diaries = query.offset((page - 1) * page_size).limit(page_size).all()

    user_ids = list(set(d.user_id for d in diaries))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # Batch query reactions for these diaries
    diary_ids = [d.id for d in diaries]
    reactions = db.query(MoodDiaryReaction).filter(MoodDiaryReaction.diary_id.in_(diary_ids)).all() if diary_ids else []
    reaction_users = {u.id: u for u in db.query(User).filter(User.id.in_(list(set(r.user_id for r in reactions)))).all()} if reactions else {}

    # Batch query reply counts
    reply_counts = {}
    if diary_ids:
        rows = db.query(MoodDiaryReply.diary_id, func.count(MoodDiaryReply.id)).filter(
            MoodDiaryReply.diary_id.in_(diary_ids)
        ).group_by(MoodDiaryReply.diary_id).all()
        reply_counts = {r[0]: r[1] for r in rows}

    result = []
    for d in diaries:
        user = users_map.get(d.user_id)
        diary_reactions = [r for r in reactions if r.diary_id == d.id]
        reaction_list = [
            {
                "type": r.reaction_type,
                "emoji": REACTION_EMOJI.get(r.reaction_type, ""),
                "user_id": r.user_id,
                "nickname": (reaction_users.get(r.user_id).nickname if reaction_users.get(r.user_id) else "")
            }
            for r in diary_reactions
        ]

        result.append({
            "id": d.id,
            "user_id": d.user_id,
            "nickname": user.nickname if user else "",
            "avatar": user.avatar if user else None,
            "mood_type": d.mood_type,
            "mood_intensity": d.mood_intensity,
            "second_mood": d.second_mood,
            "content": d.content,
            "images": json.loads(d.images) if d.images else [],
            "tags": json.loads(d.tags) if d.tags else [],
            "is_read": d.is_read,
            "reactions": reaction_list,
            "reply_count": reply_counts.get(d.id, 0),
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else None
        })

    return success_response(data={"list": result, "total": total, "page": page, "page_size": page_size})


@router.post("/diary/{diary_id}/reaction")
async def add_reaction(
    diary_id: int,
    data: MoodDiaryReactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加日记反应
    """
    diary = db.query(MoodDiary).filter(MoodDiary.id == diary_id).first()
    if not diary:
        return error_response(404, "日记不存在")

    valid_types = ["hug", "kiss", "like", "cheer", "pat", "heart"]
    if data.reaction_type not in valid_types:
        return error_response(400, "无效的反应类型")

    existing = db.query(MoodDiaryReaction).filter(
        MoodDiaryReaction.diary_id == diary_id,
        MoodDiaryReaction.user_id == current_user.id
    ).first()

    if existing:
        existing.reaction_type = data.reaction_type
    else:
        reaction = MoodDiaryReaction(
            diary_id=diary_id,
            user_id=current_user.id,
            reaction_type=data.reaction_type
        )
        db.add(reaction)

    db.commit()

    # Notify diary author
    if diary.user_id != current_user.id:
        emoji = REACTION_EMOJI.get(data.reaction_type, "")
        notification = Notification(
            user_id=diary.user_id,
            title="日记反应",
            content=f"{current_user.nickname or 'TA'}对你的日记{emoji}了",
            type="diary_reaction"
        )
        db.add(notification)
        db.commit()

    return success_response(message="已发送")


@router.delete("/diary/{diary_id}/reaction")
async def remove_reaction(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    撤回日记反应
    """
    reaction = db.query(MoodDiaryReaction).filter(
        MoodDiaryReaction.diary_id == diary_id,
        MoodDiaryReaction.user_id == current_user.id
    ).first()
    if not reaction:
        return error_response(404, "未找到反应")

    db.delete(reaction)
    db.commit()
    return success_response(message="已撤回")


@router.post("/diary/{diary_id}/reply")
async def add_reply(
    diary_id: int,
    data: MoodDiaryReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加日记回复
    """
    diary = db.query(MoodDiary).filter(MoodDiary.id == diary_id).first()
    if not diary:
        return error_response(404, "日记不存在")

    if data.parent_id:
        parent = db.query(MoodDiaryReply).filter(
            MoodDiaryReply.id == data.parent_id,
            MoodDiaryReply.diary_id == diary_id
        ).first()
        if not parent:
            return error_response(404, "父回复不存在")

    reply = MoodDiaryReply(
        diary_id=diary_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        content=data.content
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    # Notify diary author
    if diary.user_id != current_user.id:
        notification = Notification(
            user_id=diary.user_id,
            title="日记回复",
            content=f"{current_user.nickname or 'TA'}回复了你的日记",
            type="diary_reply"
        )
        db.add(notification)
        db.commit()

    return success_response(data={"id": reply.id}, message="回复成功")


@router.get("/diary/{diary_id}/replies")
async def list_replies(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取日记回复列表
    """
    replies = db.query(MoodDiaryReply).filter(
        MoodDiaryReply.diary_id == diary_id
    ).order_by(MoodDiaryReply.created_at.asc()).all()

    user_ids = list(set(r.user_id for r in replies))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    result = []
    for r in replies:
        user = users_map.get(r.user_id)
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "nickname": user.nickname if user else "",
            "avatar": user.avatar if user else None,
            "content": r.content,
            "parent_id": r.parent_id,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None
        })

    return success_response(data=result)


@router.delete("/diary/reply/{reply_id}")
async def delete_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除日记回复
    - 仅本人可删除
    """
    reply = db.query(MoodDiaryReply).filter(MoodDiaryReply.id == reply_id).first()
    if not reply:
        return error_response(404, "回复不存在")
    if reply.user_id != current_user.id:
        return error_response(403, "无权删除")

    # Delete children first
    db.query(MoodDiaryReply).filter(MoodDiaryReply.parent_id == reply_id).delete()
    db.delete(reply)
    db.commit()
    return success_response(message="删除成功")
