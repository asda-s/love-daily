"""
恋爱养成模块路由
处理心动分、等级系统、成就系统等接口
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models import User, Achievement, LevelBenefit
from app.schemas import HeartPointAdd
from app.security import get_current_user
from app.response import success_response, error_response
import os

router = APIRouter()

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")

LEVEL_THRESHOLDS = {
    1: 0,
    2: 101,
    3: 301,
    4: 601,
    5: 1001,
    6: 2001,
    7: 3501,
    8: 5501,
    9: 8001,
    10: 12001
}

ACHIEVEMENT_DEFINITIONS = [
    {"name": "故事的开始", "description": "完成初遇/告白时光线记录", "condition": "发布第一条时光线", "reward_points": 20},
    {"name": "一周年快乐", "description": "在一起满365天", "condition": "情侣绑定满365天", "reward_points": 100},
    {"name": "满分守护者", "description": "完整填写饮食偏好档案", "condition": "填写饮食偏好", "reward_points": 30},
    {"name": "生理期小太阳", "description": "连续3个周期提前完成暖心准备", "condition": "连续3个周期有生理期记录", "reward_points": 50},
    {"name": "30天早安约定", "description": "连续30天完成早安打卡", "condition": "连续打卡30天", "reward_points": 50},
    {"name": "旅行最佳搭子", "description": "完成第一次双人旅行心愿", "condition": "完成一个couple类型心愿", "reward_points": 80},
    {"name": "日记达人", "description": "累计写下30篇心情日记", "condition": "发布30篇日记", "reward_points": 50},
    {"name": "心情收藏家", "description": "体验过全部8种心情类型", "condition": "使用8种不同心情发日记", "reward_points": 80},
    {"name": "灵魂共鸣", "description": "与伴侣同一天都写了日记", "condition": "同一天双方各发一篇日记", "reward_points": 30},
]


@router.get("/overview")
async def love_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    level = current_user.level
    points = current_user.heart_points
    next_level_points = LEVEL_THRESHOLDS.get(level + 1, LEVEL_THRESHOLDS.get(10, 12001))
    current_level_points = LEVEL_THRESHOLDS.get(level, 0)
    progress = 0
    if next_level_points > current_level_points:
        progress = min(100, int((points - current_level_points) / (next_level_points - current_level_points) * 100))

    level_benefit = db.query(LevelBenefit).filter(LevelBenefit.level == level).first()

    achievements = db.query(Achievement).filter(Achievement.user_id == current_user.id).all()
    unlocked_count = sum(1 for a in achievements if a.is_unlocked)
    total_achievements = len(achievements)

    return success_response({
        "level": level,
        "heart_points": points,
        "next_level_points": next_level_points,
        "progress": progress,
        "level_benefit": {
            "name": level_benefit.benefit_name if level_benefit else "",
            "description": level_benefit.description if level_benefit else ""
        },
        "achievements_unlocked": unlocked_count,
        "achievements_total": total_achievements
    })


@router.get("/levels")
async def get_levels(
    db: Session = Depends(get_db)
):
    benefits = db.query(LevelBenefit).order_by(LevelBenefit.level.asc()).all()

    result = []
    for b in benefits:
        result.append({
            "level": b.level,
            "name": b.benefit_name,
            "description": b.description,
            "points_required": LEVEL_THRESHOLDS.get(b.level, 0)
        })

    return success_response(result)


@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    achievements = db.query(Achievement).filter(
        Achievement.user_id == current_user.id
    ).order_by(Achievement.id.asc()).all()

    if not achievements:
        _init_achievements(current_user.id, db)
        achievements = db.query(Achievement).filter(
            Achievement.user_id == current_user.id
        ).order_by(Achievement.id.asc()).all()

    result = []
    for a in achievements:
        result.append({
            "id": a.id,
            "name": a.achievement_name,
            "description": a.description,
            "condition": a.condition,
            "reward_points": a.reward_points,
            "is_unlocked": a.is_unlocked,
            "unlock_time": str(a.unlock_time) if a.unlock_time else None
        })

    return success_response(result)


@router.post("/unlock-achievement")
async def unlock_achievement(
    achievement_name: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    achievement = db.query(Achievement).filter(
        Achievement.user_id == current_user.id,
        Achievement.achievement_name == achievement_name
    ).first()

    if not achievement:
        return error_response(404, "成就不存在")

    if achievement.is_unlocked:
        return error_response(400, "成就已解锁")

    achievement.is_unlocked = True
    achievement.unlock_time = datetime.now()
    current_user.heart_points += achievement.reward_points

    _check_level_up(current_user, db)

    db.commit()
    return success_response({
        "achievement_name": achievement.achievement_name,
        "reward_points": achievement.reward_points,
        "total_points": current_user.heart_points,
        "level": current_user.level
    })


@router.post("/add-points")
async def add_points(
    data: HeartPointAdd,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 仅允许系统内部调用（通过内部密钥头验证）
    internal_key = request.headers.get("X-Internal-Key")
    if not INTERNAL_API_KEY or internal_key != INTERNAL_API_KEY:
        return error_response(403, "此接口仅限系统内部调用")

    current_user.heart_points += data.points
    _check_level_up(current_user, db)
    db.commit()

    return success_response({
        "points_added": data.points,
        "total_points": current_user.heart_points,
        "level": current_user.level,
        "reason": data.reason
    })


@router.get("/points-history")
async def points_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    unlocked = db.query(Achievement).filter(
        Achievement.user_id == current_user.id,
        Achievement.is_unlocked == True
    ).all()

    result = []
    for a in unlocked:
        result.append({
            "type": "achievement",
            "name": a.achievement_name,
            "points": a.reward_points,
            "time": str(a.unlock_time)
        })

    result.sort(key=lambda x: x["time"], reverse=True)
    return success_response(result)


def _init_achievements(user_id: int, db: Session):
    for defn in ACHIEVEMENT_DEFINITIONS:
        achievement = Achievement(
            user_id=user_id,
            achievement_name=defn["name"],
            description=defn["description"],
            condition=defn["condition"],
            reward_points=defn["reward_points"],
            is_unlocked=False
        )
        db.add(achievement)
    db.commit()


def _check_level_up(user: User, db: Session):
    new_level = 1
    for level, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if user.heart_points >= threshold:
            new_level = level
            break
    if new_level > user.level:
        user.level = new_level


def try_unlock_achievement(user_id: int, achievement_name: str, db: Session) -> bool:
    """尝试解锁指定成就，成功返回True，已解锁或不存在返回False"""
    achievement = db.query(Achievement).filter(
        Achievement.user_id == user_id,
        Achievement.achievement_name == achievement_name
    ).first()

    if not achievement or achievement.is_unlocked:
        return False

    achievement.is_unlocked = True
    achievement.unlock_time = datetime.now()

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.heart_points += achievement.reward_points
        _check_level_up(user, db)

    db.commit()
    return True


@router.get("/health")
async def love_health():
    return success_response(message="恋爱养成模块正常")


@router.get("/stats")
async def love_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """恋爱数据统计面板"""
    from datetime import date, timedelta
    from app.models import Memory, Anniversary, Wish, CheckinRecord, Bill, Emotion, MoodDiary

    today = date.today()

    # 在一起天数
    days_together = (today - current_user.created_at.date()).days if current_user.created_at else 0

    # 时光线数量
    memory_count = db.query(Memory).filter(
        (Memory.user_id == current_user.id) |
        (current_user.lover_id and (Memory.user_id == current_user.lover_id))
    ).count() if current_user.lover_id else db.query(Memory).filter(Memory.user_id == current_user.id).count()

    # 纪念日数量
    anniversary_count = db.query(Anniversary).filter(
        Anniversary.user_id == current_user.id
    ).count()

    # 心愿完成数
    wish_completed = db.query(Wish).filter(
        Wish.user_id == current_user.id,
        Wish.status == "completed"
    ).count()

    # 本月打卡次数
    month_start = today.replace(day=1)
    checkin_count = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date >= month_start
    ).count()

    # 本月账单总额
    month_bills = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        Bill.pay_time >= datetime.combine(month_start, datetime.min.time())
    ).all()
    month_expense = sum(b.amount for b in month_bills)

    # 情绪记录数
    emotion_count = db.query(Emotion).filter(
        Emotion.user_id == current_user.id
    ).count()

    # 日记数量
    diary_count = db.query(MoodDiary).filter(
        MoodDiary.user_id == current_user.id,
        MoodDiary.publish_status == "published"
    ).count()

    return success_response({
        "days_together": days_together,
        "heart_points": current_user.heart_points,
        "level": current_user.level,
        "memory_count": memory_count,
        "anniversary_count": anniversary_count,
        "wish_completed": wish_completed,
        "month_checkins": checkin_count,
        "month_expense": round(month_expense, 2),
        "emotion_count": emotion_count,
        "diary_count": diary_count
    })


def check_diary_achievements(user_id: int, db: Session):
    """检查日记相关成就"""
    from app.models import MoodDiary
    from sqlalchemy import func

    # 日记达人：累计30篇
    diary_count = db.query(MoodDiary).filter(
        MoodDiary.user_id == user_id,
        MoodDiary.publish_status == "published"
    ).count()
    if diary_count >= 30:
        try_unlock_achievement(user_id, "日记达人", db)

    # 心情收藏家：使用过8种心情
    mood_types = db.query(func.distinct(MoodDiary.mood_type)).filter(
        MoodDiary.user_id == user_id,
        MoodDiary.publish_status == "published"
    ).all()
    if len(mood_types) >= 8:
        try_unlock_achievement(user_id, "心情收藏家", db)

    # 灵魂共鸣：同一天双方都写了日记
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.lover_id:
        from sqlalchemy import cast, Date
        today = func.current_date()
        my_today = db.query(MoodDiary).filter(
            MoodDiary.user_id == user_id,
            MoodDiary.publish_status == "published",
            func.date(MoodDiary.created_at) == today
        ).first()
        lover_today = db.query(MoodDiary).filter(
            MoodDiary.user_id == user.lover_id,
            MoodDiary.publish_status == "published",
            func.date(MoodDiary.created_at) == today
        ).first()
        if my_today and lover_today:
            try_unlock_achievement(user_id, "灵魂共鸣", db)
            try_unlock_achievement(user.lover_id, "灵魂共鸣", db)
