"""
双人互动模块路由
处理打卡系统、积分福利、情绪树洞、情侣账本等接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
from typing import Optional, List

from app.database import get_db
from app.models import (
    User, CheckinProject, CheckinRecord, Benefit, ExchangeRecord,
    Emotion, Bill, Greeting, Notification, Memory
)
from app.schemas import (
    CheckinProjectCreate, CheckinCreate, BenefitCreate, BenefitUpdate,
    EmotionCreate, BillCreate, BillUpdate, GreetingCreate
)
from app.security import get_current_user, check_couple_permission
from app.response import success_response, error_response


from app.utils import try_achieve

router = APIRouter()


# ==================== 打卡项目管理 ====================

@router.post("/checkin/project")
async def create_project(
    data: CheckinProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = CheckinProject(
        user_id=current_user.id,
        name=data.name,
        points=data.points,
        is_joint=data.is_joint
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return success_response({
        "id": project.id,
        "name": project.name,
        "points": project.points,
        "is_joint": project.is_joint,
        "created_at": str(project.created_at)
    })


@router.get("/checkin/project")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import or_
    query = db.query(CheckinProject)
    if current_user.lover_id:
        query = query.filter(or_(
            CheckinProject.user_id == current_user.id,
            CheckinProject.user_id == current_user.lover_id
        ))
    else:
        query = query.filter(CheckinProject.user_id == current_user.id)
    projects = query.order_by(CheckinProject.created_at.desc()).all()

    result = []
    for p in projects:
        today = date.today()
        today_record = db.query(CheckinRecord).filter(
            CheckinRecord.project_id == p.id,
            CheckinRecord.user_id == current_user.id,
            CheckinRecord.checkin_date == today
        ).first()

        total_days = db.query(CheckinRecord).filter(
            CheckinRecord.project_id == p.id,
            CheckinRecord.user_id == current_user.id
        ).count()

        consecutive = _get_consecutive_days(db, p.id, current_user.id)

        result.append({
            "id": p.id,
            "name": p.name,
            "points": p.points,
            "is_joint": p.is_joint,
            "is_checked_today": today_record is not None,
            "total_days": total_days,
            "consecutive_days": consecutive,
            "created_at": str(p.created_at)
        })

    return success_response(result)


@router.delete("/checkin/project/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(CheckinProject).filter(
        CheckinProject.id == project_id,
        CheckinProject.user_id == current_user.id
    ).first()
    if not project:
        return error_response(404, "打卡项目不存在")

    db.query(CheckinRecord).filter(CheckinRecord.project_id == project_id).delete()
    db.delete(project)
    db.commit()
    return success_response(message="删除成功")


# ==================== 打卡记录 ====================

@router.post("/checkin")
async def do_checkin(
    data: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(CheckinProject).filter(
        CheckinProject.id == data.project_id
    ).first()
    if not project:
        return error_response(404, "打卡项目不存在")

    if not check_couple_permission(current_user, project.user_id):
        return error_response(403, "无权限操作此打卡项目")

    today = date.today()
    existing = db.query(CheckinRecord).filter(
        CheckinRecord.project_id == data.project_id,
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date == today
    ).first()
    if existing:
        return error_response(400, "今日已打卡")

    record = CheckinRecord(
        project_id=data.project_id,
        user_id=current_user.id,
        checkin_date=today,
        note=data.note,
        image=data.image
    )
    db.add(record)

    # 计算连续打卡天数（包含今天）
    consecutive = _get_consecutive_days(db, data.project_id, current_user.id) + 1

    # 基础积分
    earned_points = project.points

    # 连续打卡奖励：连续7天+10分，连续30天+50分
    bonus = 0
    if consecutive == 30:
        bonus = 50
    elif consecutive == 7:
        bonus = 10
    earned_points += bonus

    current_user.heart_points += earned_points
    db.commit()
    db.refresh(record)

    # 成就检测：连续打卡30天 -> "30天早安约定"
    if consecutive >= 30:
        try_achieve(current_user.id, "30天早安约定", db)

    # 同步到时光线
    try:
        memory = Memory(
            user_id=current_user.id,
            title=f"✅ 打卡：{project.name}",
            content=f"连续打卡第{consecutive}天" + (f"，获得{bonus}分连续奖励！" if bonus else ""),
            event_time=datetime.now(),
            is_sync=True
        )
        db.add(memory)
        db.commit()
    except Exception:
        pass

    return success_response({
        "id": record.id,
        "project_id": record.project_id,
        "checkin_date": str(record.checkin_date),
        "points_earned": earned_points,
        "bonus": bonus,
        "consecutive_days": consecutive,
        "total_points": current_user.heart_points
    })


@router.get("/checkin/history")
async def checkin_history(
    project_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id
    )
    if project_id:
        query = query.filter(CheckinRecord.project_id == project_id)

    records = query.order_by(CheckinRecord.checkin_date.desc()).limit(100).all()

    # 批量查询项目信息
    project_ids = list(set(r.project_id for r in records))
    projects_map = {p.id: p for p in db.query(CheckinProject).filter(CheckinProject.id.in_(project_ids)).all()} if project_ids else {}

    result = []
    for r in records:
        project = projects_map.get(r.project_id)
        result.append({
            "id": r.id,
            "project_id": r.project_id,
            "project_name": project.name if project else "已删除",
            "checkin_date": str(r.checkin_date),
            "note": r.note,
            "image": r.image,
            "created_at": str(r.created_at)
        })

    return success_response(result)


@router.get("/checkin/stats")
async def checkin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_checkins = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id
    ).count()

    today = date.today()
    today_checkins = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date == today
    ).count()

    projects = db.query(CheckinProject).filter(
        CheckinProject.user_id == current_user.id
    ).all()

    max_consecutive = 0
    for p in projects:
        consecutive = _get_consecutive_days(db, p.id, current_user.id)
        if consecutive > max_consecutive:
            max_consecutive = consecutive

    return success_response({
        "total_checkins": total_checkins,
        "today_checkins": today_checkins,
        "max_consecutive_days": max_consecutive,
        "heart_points": current_user.heart_points
    })


def _get_consecutive_days(db: Session, project_id: int, user_id: int) -> int:
    records = db.query(CheckinRecord).filter(
        CheckinRecord.project_id == project_id,
        CheckinRecord.user_id == user_id
    ).order_by(CheckinRecord.checkin_date.desc()).all()

    if not records:
        return 0

    consecutive = 0
    expected_date = date.today()

    for r in records:
        if r.checkin_date == expected_date:
            consecutive += 1
            expected_date = expected_date - timedelta(days=1)
        elif r.checkin_date < expected_date:
            break

    return consecutive


# ==================== 积分福利 ====================

@router.post("/benefit")
async def create_benefit(
    data: BenefitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    benefit = Benefit(
        user_id=current_user.id,
        name=data.name,
        points=data.points,
        rule=data.rule,
        is_repeatable=data.is_repeatable
    )
    db.add(benefit)
    db.commit()
    db.refresh(benefit)
    return success_response({
        "id": benefit.id,
        "name": benefit.name,
        "points": benefit.points,
        "rule": benefit.rule,
        "is_repeatable": benefit.is_repeatable
    })


@router.get("/benefit")
async def list_benefits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    benefits = db.query(Benefit).filter(
        Benefit.user_id == current_user.id
    ).order_by(Benefit.points.asc()).all()

    # 批量查询兑换次数
    benefit_ids = [b.id for b in benefits]
    if benefit_ids:
        count_rows = db.query(
            ExchangeRecord.benefit_id,
            func.count(ExchangeRecord.id)
        ).filter(ExchangeRecord.benefit_id.in_(benefit_ids)).group_by(ExchangeRecord.benefit_id).all()
        exchange_counts = {bid: cnt for bid, cnt in count_rows}
    else:
        exchange_counts = {}

    result = []
    for b in benefits:
        exchanged_count = exchange_counts.get(b.id, 0)
        result.append({
            "id": b.id,
            "name": b.name,
            "points": b.points,
            "rule": b.rule,
            "is_repeatable": b.is_repeatable,
            "exchanged_count": exchanged_count,
            "can_exchange": current_user.heart_points >= b.points
        })

    return success_response(result)


@router.put("/benefit/{benefit_id}")
async def update_benefit(
    benefit_id: int,
    data: BenefitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    benefit = db.query(Benefit).filter(
        Benefit.id == benefit_id,
        Benefit.user_id == current_user.id
    ).first()
    if not benefit:
        return error_response(404, "福利不存在")

    if data.name is not None:
        benefit.name = data.name
    if data.points is not None:
        benefit.points = data.points
    if data.rule is not None:
        benefit.rule = data.rule
    if data.is_repeatable is not None:
        benefit.is_repeatable = data.is_repeatable

    db.commit()
    return success_response(message="修改成功")


@router.delete("/benefit/{benefit_id}")
async def delete_benefit(
    benefit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    benefit = db.query(Benefit).filter(
        Benefit.id == benefit_id,
        Benefit.user_id == current_user.id
    ).first()
    if not benefit:
        return error_response(404, "福利不存在")

    db.delete(benefit)
    db.commit()
    return success_response(message="删除成功")


@router.post("/benefit/{benefit_id}/exchange")
async def exchange_benefit(
    benefit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    benefit = db.query(Benefit).filter(Benefit.id == benefit_id).first()
    if not benefit:
        return error_response(404, "福利不存在")

    # 权限校验：只能兑换自己或伴侣创建的福利
    if benefit.user_id != current_user.id:
        if not current_user.lover_id or benefit.user_id != current_user.lover_id:
            return error_response(403, "无权兑换此福利")

    # 使用 SELECT FOR UPDATE 锁定用户行，防止并发扣分
    user = db.query(User).filter(User.id == current_user.id).with_for_update().first()
    if user.heart_points < benefit.points:
        return error_response(400, "心动分不足")

    if not benefit.is_repeatable:
        existing = db.query(ExchangeRecord).filter(
            ExchangeRecord.benefit_id == benefit_id,
            ExchangeRecord.user_id == current_user.id
        ).first()
        if existing:
            return error_response(400, "该福利不可重复兑换")

    record = ExchangeRecord(
        benefit_id=benefit_id,
        user_id=current_user.id,
        points=benefit.points
    )
    db.add(record)

    user.heart_points -= benefit.points
    db.commit()
    db.refresh(record)
    db.refresh(user)

    return success_response({
        "id": record.id,
        "points_consumed": benefit.points,
        "remaining_points": user.heart_points
    })


@router.get("/exchange/history")
async def exchange_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(ExchangeRecord).filter(
        ExchangeRecord.user_id == current_user.id
    ).order_by(ExchangeRecord.exchange_time.desc()).all()

    # 批量查询福利信息
    benefit_ids = list(set(r.benefit_id for r in records))
    benefits_map = {b.id: b for b in db.query(Benefit).filter(Benefit.id.in_(benefit_ids)).all()} if benefit_ids else {}

    result = []
    for r in records:
        benefit = benefits_map.get(r.benefit_id)
        result.append({
            "id": r.id,
            "benefit_name": benefit.name if benefit else "已删除",
            "points": r.points,
            "exchange_time": str(r.exchange_time),
            "is_fulfilled": r.is_fulfilled
        })

    return success_response(result)


@router.put("/exchange/{record_id}/fulfill")
async def fulfill_exchange(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(ExchangeRecord).filter(
        ExchangeRecord.id == record_id
    ).first()
    if not record:
        return error_response(404, "兑换记录不存在")

    benefit = db.query(Benefit).filter(Benefit.id == record.benefit_id).first()
    if not benefit or benefit.user_id != current_user.id:
        return error_response(403, "无权操作")

    record.is_fulfilled = True
    db.commit()
    return success_response(message="已兑现")


# ==================== 情绪树洞 ====================

@router.post("/emotion")
async def create_emotion(
    data: EmotionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    emotion = Emotion(
        user_id=current_user.id,
        emotion_type=data.emotion_type,
        content=data.content,
        is_sync=data.is_sync
    )
    db.add(emotion)
    db.commit()
    db.refresh(emotion)

    # 负面情绪自动暖心回复
    warm_reply = None
    negative_emotions = {"sad", "angry", "wronged", "anxious", "难过", "生气", "委屈", "焦虑"}
    if data.emotion_type in negative_emotions:
        warm_messages = [
            "抱抱你，不管发生了什么，我都在你身边。",
            "你的心情我懂，想聊聊吗？我一直都在。",
            "难过的时候就靠在我肩上吧，我会一直陪着你。",
            "别怕，有我在呢。一切都会好起来的。",
            "你不是一个人，我永远站在你这边。"
        ]
        import random
        warm_reply = random.choice(warm_messages)

    # 如果选择同步给情侣，发送通知
    if data.is_sync and current_user.lover_id:
        try:
            from app.models import Notification
            emotion_labels = {"sad": "难过", "angry": "生气", "wronged": "委屈", "anxious": "焦虑",
                              "happy": "开心", "calm": "平静", "excited": "兴奋"}
            label = emotion_labels.get(data.emotion_type, data.emotion_type)
            notification = Notification(
                user_id=current_user.lover_id,
                title=f"你的情侣刚刚发布了{label}情绪",
                content=data.content[:50] + "..." if len(data.content) > 50 else data.content,
                type="emotion"
            )
            db.add(notification)
            db.commit()
        except Exception:
            db.rollback()
            import logging
            logging.getLogger(__name__).warning("情绪通知创建失败", exc_info=True)

    return success_response({
        "id": emotion.id,
        "emotion_type": emotion.emotion_type,
        "content": emotion.content,
        "is_sync": emotion.is_sync,
        "warm_reply": warm_reply,
        "created_at": str(emotion.created_at)
    })


@router.get("/emotion")
async def list_emotions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.lover_id:
        query = db.query(Emotion).filter(
            (Emotion.user_id == current_user.id) |
            ((Emotion.user_id == current_user.lover_id) & (Emotion.is_sync == True))
        )
    else:
        query = db.query(Emotion).filter(Emotion.user_id == current_user.id)

    emotions = query.order_by(Emotion.created_at.desc()).limit(100).all()

    # 批量查询用户信息
    user_ids = list(set(e.user_id for e in emotions))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    negative_emotions = {"sad", "angry", "wronged", "anxious", "难过", "生气", "委屈", "焦虑"}
    warm_messages = [
        "抱抱你，不管发生了什么，我都在你身边。",
        "你的心情我懂，想聊聊吗？我一直都在。",
        "难过的时候就靠在我肩上吧，我会一直陪着你。",
        "别怕，有我在呢。一切都会好起来的。",
        "你不是一个人，我永远站在你这边。"
    ]

    result = []
    for e in emotions:
        user = users_map.get(e.user_id)
        warm_reply = None
        if e.emotion_type in negative_emotions:
            import random
            random.seed(e.id)
            warm_reply = random.choice(warm_messages)
        result.append({
            "id": e.id,
            "user_id": e.user_id,
            "nickname": user.nickname if user else "",
            "emotion_type": e.emotion_type,
            "content": e.content,
            "is_sync": e.is_sync,
            "is_mine": e.user_id == current_user.id,
            "warm_reply": warm_reply,
            "created_at": str(e.created_at)
        })

    return success_response(result)


@router.delete("/emotion/{emotion_id}")
async def delete_emotion(
    emotion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    emotion = db.query(Emotion).filter(
        Emotion.id == emotion_id,
        Emotion.user_id == current_user.id
    ).first()
    if not emotion:
        return error_response(404, "情绪记录不存在")

    db.delete(emotion)
    db.commit()
    return success_response(message="删除成功")


# ==================== 情侣账本 ====================

@router.post("/bill")
async def create_bill(
    data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = Bill(
        user_id=current_user.id,
        amount=data.amount,
        type=data.type,
        pay_time=data.pay_time,
        payer=data.payer,
        note=data.note,
        is_aa=data.is_aa
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return success_response({
        "id": bill.id,
        "amount": bill.amount,
        "type": bill.type,
        "pay_time": str(bill.pay_time),
        "payer": bill.payer,
        "note": bill.note,
        "is_aa": bill.is_aa
    })


@router.get("/bill")
async def list_bills(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Bill).filter(Bill.user_id == current_user.id)

    if current_user.lover_id:
        query = db.query(Bill).filter(
            (Bill.user_id == current_user.id) | (Bill.user_id == current_user.lover_id)
        )

    if year and month:
        query = query.filter(
            extract('year', Bill.pay_time) == year,
            extract('month', Bill.pay_time) == month
        )

    total = query.count()
    bills = query.order_by(Bill.pay_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 批量查询用户信息
    user_ids = list(set(b.user_id for b in bills))
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    result = []
    for b in bills:
        user = users_map.get(b.user_id)
        result.append({
            "id": b.id,
            "user_id": b.user_id,
            "nickname": user.nickname if user else "",
            "amount": b.amount,
            "type": b.type,
            "pay_time": str(b.pay_time),
            "payer": b.payer,
            "note": b.note,
            "is_aa": b.is_aa,
            "is_mine": b.user_id == current_user.id,
            "created_at": str(b.created_at)
        })

    return success_response({"list": result, "total": total, "page": page, "page_size": page_size})


@router.put("/bill/{bill_id}")
async def update_bill(
    bill_id: int,
    data: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    if not bill:
        return error_response(404, "账单不存在")

    if data.amount is not None:
        bill.amount = data.amount
    if data.type is not None:
        bill.type = data.type
    if data.pay_time is not None:
        bill.pay_time = data.pay_time
    if data.payer is not None:
        bill.payer = data.payer
    if data.note is not None:
        bill.note = data.note
    if data.is_aa is not None:
        bill.is_aa = data.is_aa

    db.commit()
    return success_response(message="修改成功")


@router.delete("/bill/{bill_id}")
async def delete_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    if not bill:
        return error_response(404, "账单不存在")

    db.delete(bill)
    db.commit()
    return success_response(message="删除成功")


@router.get("/bill/monthly-summary")
async def monthly_summary(
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_ids = [current_user.id]
    if current_user.lover_id:
        user_ids.append(current_user.lover_id)

    bills = db.query(Bill).filter(
        Bill.user_id.in_(user_ids),
        extract('year', Bill.pay_time) == year,
        extract('month', Bill.pay_time) == month
    ).all()

    my_total = 0
    lover_total = 0
    aa_total = 0
    type_totals = {}

    for b in bills:
        if b.user_id == current_user.id:
            my_total += b.amount
        else:
            lover_total += b.amount

        if b.is_aa:
            aa_total += b.amount

        type_totals[b.type] = type_totals.get(b.type, 0) + b.amount

    # AA计算：aa_total的一半是每人应付，再根据谁多付了计算差额
    aa_each = round(aa_total / 2, 2) if aa_total > 0 else 0
    # 计算AA账单中各方已付金额
    my_aa_paid = sum(b.amount for b in bills if b.is_aa and b.user_id == current_user.id)
    lover_aa_paid = sum(b.amount for b in bills if b.is_aa and b.user_id != current_user.id)
    # 差额：正数表示伴侣欠我，负数表示我欠伴侣
    aa_balance = round(my_aa_paid - aa_each, 2)

    return success_response({
        "year": year,
        "month": month,
        "my_total": round(my_total, 2),
        "lover_total": round(lover_total, 2),
        "total": round(my_total + lover_total, 2),
        "type_totals": type_totals,
        "aa": {
            "total": round(aa_total, 2),
            "each": aa_each,
            "my_paid": round(my_aa_paid, 2),
            "lover_paid": round(lover_aa_paid, 2),
            "balance": aa_balance,
            "balance_desc": f"伴侣应付给你{abs(aa_balance)}元" if aa_balance > 0 else (f"你应付给伴侣{abs(aa_balance)}元" if aa_balance < 0 else "已平账")
        }
    })


# ==================== 早安晚安 ====================

@router.post("/greeting")
async def create_greeting(
    data: GreetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送早安/晚安问候"""
    if not current_user.lover_id:
        return error_response(400, "请先绑定情侣")

    today = date.today()

    # 防重复
    existing = db.query(Greeting).filter(
        Greeting.sender_id == current_user.id,
        Greeting.greeting_date == today,
        Greeting.type == data.type
    ).first()
    if existing:
        type_label = "早安" if data.type == "morning" else "晚安"
        return error_response(400, f"今天已经说过{type_label}了")

    greeting = Greeting(
        sender_id=current_user.id,
        receiver_id=current_user.lover_id,
        type=data.type,
        greeting_date=today
    )
    db.add(greeting)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        type_label = "早安" if data.type == "morning" else "晚安"
        return error_response(400, f"今天已经说过{type_label}了")

    # 奖励心动分
    current_user.heart_points += 2

    # 创建通知
    type_label = "早安" if data.type == "morning" else "晚安"
    notification = Notification(
        user_id=current_user.lover_id,
        title=f"TA跟你说{type_label}了",
        content=f"{current_user.nickname or 'TA'}跟你说{type_label}啦~",
        type="greeting"
    )
    db.add(notification)
    db.commit()

    # WebSocket 推送
    try:
        from app.routers.websocket import broadcast_to_user
        await broadcast_to_user(current_user.lover_id, {
            "type": "greeting",
            "data": {
                "sender_id": current_user.id,
                "sender_nickname": current_user.nickname or "TA",
                "type": data.type
            }
        })
    except Exception:
        pass

    return success_response(data={
        "type": data.type,
        "points_earned": 2,
        "total_points": current_user.heart_points
    }, message=f"{type_label}成功")


@router.get("/greeting/today")
async def get_today_greetings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日早安晚安状态"""
    today = date.today()

    my_greetings = db.query(Greeting).filter(
        Greeting.sender_id == current_user.id,
        Greeting.greeting_date == today
    ).all()
    my_types = {g.type for g in my_greetings}

    partner_greetings = {}
    if current_user.lover_id:
        partner_g = db.query(Greeting).filter(
            Greeting.sender_id == current_user.lover_id,
            Greeting.receiver_id == current_user.id,
            Greeting.greeting_date == today
        ).all()
        partner_greetings = {g.type: True for g in partner_g}

    return success_response(data={
        "my_morning": "morning" in my_types,
        "my_evening": "evening" in my_types,
        "partner_morning": partner_greetings.get("morning", False),
        "partner_evening": partner_greetings.get("evening", False)
    })


@router.get("/health")
async def interact_health():
    return success_response(message="双人互动模块正常")


@router.get("/emotion/monthly-stats")
async def emotion_monthly_stats(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """情绪树洞月度统计"""
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    query = db.query(Emotion).filter(
        Emotion.created_at >= datetime.combine(month_start, datetime.min.time()),
        Emotion.created_at < datetime.combine(month_end, datetime.min.time())
    )
    if current_user.lover_id:
        query = query.filter(
            (Emotion.user_id == current_user.id) |
            ((Emotion.user_id == current_user.lover_id) & (Emotion.is_sync == True))
        )
    else:
        query = query.filter(Emotion.user_id == current_user.id)

    emotions = query.all()

    my_emotions = [e for e in emotions if e.user_id == current_user.id]
    lover_emotions = [e for e in emotions if e.user_id != current_user.id]

    emotion_labels = {
        "happy": "开心", "sad": "难过", "angry": "生气",
        "wronged": "委屈", "anxious": "焦虑"
    }

    my_dist = {}
    for e in my_emotions:
        label = emotion_labels.get(e.emotion_type, e.emotion_type)
        my_dist[label] = my_dist.get(label, 0) + 1

    lover_dist = {}
    for e in lover_emotions:
        label = emotion_labels.get(e.emotion_type, e.emotion_type)
        lover_dist[label] = lover_dist.get(label, 0) + 1

    # 每日情绪趋势
    daily = {}
    for e in emotions:
        day_key = e.created_at.strftime("%m-%d")
        if day_key not in daily:
            daily[day_key] = []
        daily[day_key].append({
            "user_id": e.user_id,
            "emotion_type": e.emotion_type
        })

    return success_response({
        "year": year,
        "month": month,
        "my_count": len(my_emotions),
        "lover_count": len(lover_emotions),
        "my_distribution": my_dist,
        "lover_distribution": lover_dist,
        "daily_trend": daily
    })
