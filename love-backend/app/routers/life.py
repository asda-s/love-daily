"""
生活管家模块路由
处理生理期管理、饮食偏好、待办事项、好物收纳等接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date, timedelta
from typing import Optional, List
from app.database import get_db
from app.security import get_current_user
from app.models import User, Period, DietPreference, Todo, Item
from app.schemas import (
    PeriodCreate, PeriodUpdate,
    DietPreferenceCreate,
    TodoCreate, TodoUpdate,
    ItemCreate, ItemUpdate
)
from app.response import success_response, error_response


from app.utils import try_achieve

router = APIRouter()


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


# ==================== 好物收纳接口 ====================

@router.post("/item")
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建好物记录
    - 仅本人可创建
    """
    new_item = Item(
        user_id=current_user.id,
        name=item_data.name,
        brand=item_data.brand,
        model=item_data.model,
        spec=item_data.spec,
        expiry_date=item_data.expiry_date,
        purchase_date=item_data.purchase_date,
        open_date=item_data.open_date,
        remind_days=item_data.remind_days,
        category=item_data.category,
        note=item_data.note
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return success_response(
        data={"id": new_item.id},
        message="添加成功"
    )


@router.put("/item/{item_id}")
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑好物记录
    - 仅本人可编辑
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return error_response(404, "物品不存在")

    # 权限校验：仅本人可编辑
    if item.user_id != current_user.id:
        return error_response(403, "无权限编辑")

    # 更新字段
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.brand is not None:
        item.brand = item_data.brand
    if item_data.model is not None:
        item.model = item_data.model
    if item_data.spec is not None:
        item.spec = item_data.spec
    if item_data.expiry_date is not None:
        item.expiry_date = item_data.expiry_date
    if item_data.purchase_date is not None:
        item.purchase_date = item_data.purchase_date
    if item_data.open_date is not None:
        item.open_date = item_data.open_date
    if item_data.remind_days is not None:
        item.remind_days = item_data.remind_days
    if item_data.category is not None:
        item.category = item_data.category
    if item_data.note is not None:
        item.note = item_data.note

    db.commit()
    db.refresh(item)

    return success_response(message="编辑成功")


@router.delete("/item/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除好物记录
    - 仅本人可删除
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return error_response(404, "物品不存在")

    # 权限校验：仅本人可删除
    if item.user_id != current_user.id:
        return error_response(403, "无权限删除")

    db.delete(item)
    db.commit()

    return success_response(message="删除成功")


@router.get("/item")
async def get_item_list(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取好物列表
    - 返回本人和情侣的好物
    - 支持按分类筛选
    """
    # 查询本人和情侣的好物
    query = db.query(Item)
    if current_user.lover_id:
        query = query.filter(
            or_(
                Item.user_id == current_user.id,
                Item.user_id == current_user.lover_id
            )
        )
    else:
        query = query.filter(Item.user_id == current_user.id)

    # 分类筛选
    if category:
        query = query.filter(Item.category == category)

    items = query.order_by(Item.created_at.desc()).all()

    # 批量查询用户信息
    user_ids = list(set(i.user_id for i in items))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # 构建返回数据
    today = date.today()
    item_list = []
    for item in items:
        user = users_map.get(item.user_id)

        # 计算临期天数
        days_to_expiry = None
        is_expiring = False
        if item.expiry_date:
            days_to_expiry = (item.expiry_date - today).days
            is_expiring = 0 <= days_to_expiry <= item.remind_days

        item_list.append({
            "id": item.id,
            "user_id": item.user_id,
            "nickname": user.nickname if user else "",
            "name": item.name,
            "brand": item.brand,
            "model": item.model,
            "spec": item.spec,
            "expiry_date": item.expiry_date.strftime("%Y-%m-%d") if item.expiry_date else None,
            "purchase_date": item.purchase_date.strftime("%Y-%m-%d") if item.purchase_date else None,
            "open_date": item.open_date.strftime("%Y-%m-%d") if item.open_date else None,
            "remind_days": item.remind_days,
            "category": item.category,
            "note": item.note,
            "days_to_expiry": days_to_expiry,
            "is_expiring": is_expiring,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None
        })

    # 按临期状态排序，临期物品置顶
    item_list.sort(key=lambda x: (not x["is_expiring"], x["days_to_expiry"] if x["days_to_expiry"] is not None else 999))

    return success_response(data=item_list)


@router.get("/item/expiring")
async def get_expiring_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取临期物品列表
    - 返回即将过期的物品
    """
    today = date.today()

    # 查询本人和情侣的好物
    query = db.query(Item).filter(Item.expiry_date.isnot(None))
    if current_user.lover_id:
        query = query.filter(
            or_(
                Item.user_id == current_user.id,
                Item.user_id == current_user.lover_id
            )
        )
    else:
        query = query.filter(Item.user_id == current_user.id)

    items = query.all()

    # 批量查询用户信息
    user_ids = list(set(i.user_id for i in items))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # 筛选临期物品
    expiring_items = []
    for item in items:
        days_to_expiry = (item.expiry_date - today).days
        if 0 <= days_to_expiry <= item.remind_days:
            user = users_map.get(item.user_id)
            expiring_items.append({
                "id": item.id,
                "user_id": item.user_id,
                "nickname": user.nickname if user else "",
                "name": item.name,
                "brand": item.brand,
                "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                "days_to_expiry": days_to_expiry,
                "category": item.category
            })

    # 按临期天数排序
    expiring_items.sort(key=lambda x: x["days_to_expiry"])

    return success_response(data=expiring_items)
