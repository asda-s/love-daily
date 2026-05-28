"""
定时任务模块
负责纪念日提醒、生理期提醒、日记定时发布、心情周报等定时任务
使用APScheduler实现，时区固定为东八区
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Anniversary, Period, Todo, Whisper, User, Notification, MoodDiary
import pytz
import asyncio
import logging

logger = logging.getLogger(__name__)

CHINA_TZ = pytz.timezone('Asia/Shanghai')

scheduler = BackgroundScheduler(timezone=CHINA_TZ)


def _broadcast_notification(user_id: int, title: str, content: str, ntype: str):
    """通过WebSocket推送通知（在后台线程中调用async函数）"""
    try:
        from app.routers.websocket import broadcast_to_user
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(
                broadcast_to_user(user_id, {
                    "type": "notification",
                    "data": {"title": title, "content": content, "notification_type": ntype}
                }),
                loop
            )
    except Exception as e:
        logger.debug(f"WebSocket推送跳过: {e}")


def _create_notification(db: Session, user_id: int, title: str, content: str, ntype: str):
    now_china = datetime.now(CHINA_TZ).replace(tzinfo=None)
    existing = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.title == title,
        Notification.created_at >= now_china.replace(hour=0, minute=0, second=0)
    ).first()
    if existing:
        return
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=ntype
    )
    db.add(notification)
    _broadcast_notification(user_id, title, content, ntype)


def check_anniversaries():
    db = SessionLocal()
    try:
        today = date.today()
        anniversaries = db.query(Anniversary).all()

        for anniversary in anniversaries:
            target_date = anniversary.target_date
            if anniversary.is_yearly:
                this_year_target = target_date.replace(year=today.year)
                if this_year_target < today:
                    this_year_target = target_date.replace(year=today.year + 1)
                target_date = this_year_target

            days_left = (target_date - today).days

            if 0 <= days_left <= anniversary.remind_days:
                user = db.query(User).filter(User.id == anniversary.user_id).first()
                if user:
                    title = f"纪念日提醒"
                    content = f"「{anniversary.title}」还有{days_left}天到来"
                    _create_notification(db, user.id, title, content, "anniversary")

                    if user.lover_id:
                        _create_notification(db, user.lover_id, title, content, "anniversary")

        db.commit()
        logger.info("纪念日提醒检查完成")
    except Exception as e:
        logger.error(f"纪念日提醒检查失败: {e}")
        db.rollback()
    finally:
        db.close()


def check_periods():
    db = SessionLocal()
    try:
        today = date.today()
        periods = db.query(Period).order_by(Period.start_date.desc()).all()

        user_periods = {}
        for period in periods:
            if period.user_id not in user_periods:
                user_periods[period.user_id] = period

        for user_id, period in user_periods.items():
            next_period_start = period.start_date + timedelta(days=period.cycle_days)
            days_left = (next_period_start - today).days

            if 0 <= days_left <= 3:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    title = "生理期提醒"
                    if days_left == 0:
                        content = "预计今天到来，注意休息哦"
                    else:
                        content = f"预计还有{days_left}天到来，提前准备一下吧"
                    _create_notification(db, user_id, title, content, "period")

                    if user.lover_id:
                        lover_content = f"TA的生理期预计还有{days_left}天到来，记得关心TA哦"
                        _create_notification(db, user.lover_id, title, lover_content, "period")

        db.commit()
        logger.info("生理期提醒检查完成")
    except Exception as e:
        logger.error(f"生理期提醒检查失败: {e}")
        db.rollback()
    finally:
        db.close()


def publish_scheduled_diaries():
    """发布定时日记"""
    db = SessionLocal()
    try:
        now = datetime.now(CHINA_TZ).replace(tzinfo=None)
        diaries = db.query(MoodDiary).filter(
            MoodDiary.publish_status == "scheduled",
            MoodDiary.scheduled_time.isnot(None),
            MoodDiary.scheduled_time <= now
        ).all()

        for diary in diaries:
            diary.publish_status = "published"
            user = db.query(User).filter(User.id == diary.user_id).first()
            if user and user.lover_id:
                title = "新日记提醒"
                content = f"TA发布了一篇心情日记，快去看看吧"
                _create_notification(db, user.lover_id, title, content, "diary")

        db.commit()
        if diaries:
            logger.info(f"定时日记发布完成，共{len(diaries)}篇")
    except Exception as e:
        logger.error(f"定时日记发布失败: {e}")
        db.rollback()
    finally:
        db.close()


def generate_weekly_emotion_report():
    """生成心情周报"""
    db = SessionLocal()
    try:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        users = db.query(User).filter(User.lover_id.isnot(None)).all()
        for user in users:
            diaries = db.query(MoodDiary).filter(
                MoodDiary.user_id == user.id,
                MoodDiary.publish_status == "published",
                func.date(MoodDiary.created_at) >= week_start,
                func.date(MoodDiary.created_at) <= week_end
            ).all()

            if not diaries:
                continue

            mood_counts = {}
            for d in diaries:
                mood_counts[d.mood_type] = mood_counts.get(d.mood_type, 0) + 1

            MOOD_NAMES = {
                "happy": "开心", "sweet": "甜蜜", "calm": "平静", "tired": "疲惫",
                "sad": "难过", "angry": "生气", "wronged": "委屈", "surprised": "惊喜"
            }
            top_mood = max(mood_counts, key=mood_counts.get)
            top_mood_name = MOOD_NAMES.get(top_mood, top_mood)

            title = "心情周报"
            content = f"本周共写了{len(diaries)}篇日记，最常见的心情是「{top_mood_name}」"
            _create_notification(db, user.id, title, content, "diary")

        db.commit()
        logger.info("心情周报生成完成")
    except Exception as e:
        logger.error(f"心情周报生成失败: {e}")
        db.rollback()
    finally:
        db.close()


def check_todos():
    db = SessionLocal()
    try:
        now = datetime.now(CHINA_TZ).replace(tzinfo=None)
        todos = db.query(Todo).filter(
            Todo.remind_time.isnot(None),
            Todo.status == "pending",
            Todo.remind_time <= now
        ).all()

        for todo in todos:
            user = db.query(User).filter(User.id == todo.user_id).first()
            if user:
                title = "待办提醒"
                content = f"「{todo.title}」需要完成"
                _create_notification(db, user.id, title, content, "todo")

                if todo.type == "couple" and user.lover_id:
                    _create_notification(db, user.lover_id, title, content, "todo")

            todo.remind_time = None

        db.commit()
        logger.info("待办提醒检查完成")
    except Exception as e:
        logger.error(f"待办提醒检查失败: {e}")
        db.rollback()
    finally:
        db.close()


def send_scheduled_whispers():
    db = SessionLocal()
    try:
        now = datetime.now(CHINA_TZ).replace(tzinfo=None)
        whispers = db.query(Whisper).filter(
            Whisper.is_scheduled == True,
            Whisper.scheduled_time <= now,
            Whisper.send_time.is_(None)
        ).all()

        for whisper in whispers:
            whisper.send_time = now
            title = "悄悄话"
            content = whisper.content[:50] + "..." if len(whisper.content) > 50 else whisper.content
            _create_notification(db, whisper.receiver_id, title, content, "whisper")

        db.commit()
        if whispers:
            logger.info(f"定时悄悄话发送完成，共{len(whispers)}条")
    except Exception as e:
        logger.error(f"定时悄悄话发送失败: {e}")
        db.rollback()
    finally:
        db.close()


def check_anniversary_achievements():
    """检测"一周年快乐"成就：情侣绑定满365天"""
    db = SessionLocal()
    try:
        from app.routers.love import try_unlock_achievement
        today = date.today()
        users = db.query(User).filter(User.lover_id.isnot(None)).all()
        for user in users:
            days_together = (today - user.created_at.date()).days
            if days_together >= 365:
                try_unlock_achievement(user.id, "一周年快乐", db)
        logger.info("一周年成就检查完成")
    except Exception as e:
        logger.error(f"一周年成就检查失败: {e}")
        db.rollback()
    finally:
        db.close()


def init_scheduler():
    scheduler.add_job(
        check_anniversaries,
        CronTrigger(hour=8, minute=0, timezone=CHINA_TZ),
        id="anniversary_check",
        replace_existing=True
    )

    scheduler.add_job(
        check_periods,
        CronTrigger(hour=8, minute=0, timezone=CHINA_TZ),
        id="period_check",
        replace_existing=True
    )

    scheduler.add_job(
        publish_scheduled_diaries,
        CronTrigger(minute="*/5", timezone=CHINA_TZ),
        id="diary_scheduled_publish",
        replace_existing=True
    )

    scheduler.add_job(
        generate_weekly_emotion_report,
        CronTrigger(hour=20, minute=0, day_of_week="sun", timezone=CHINA_TZ),
        id="weekly_emotion_report",
        replace_existing=True
    )

    scheduler.add_job(
        check_todos,
        CronTrigger(hour=8, minute=0, timezone=CHINA_TZ),
        id="todo_check",
        replace_existing=True
    )

    scheduler.add_job(
        send_scheduled_whispers,
        CronTrigger(minute="*", timezone=CHINA_TZ),
        id="whisper_send",
        replace_existing=True
    )

    scheduler.add_job(
        check_anniversary_achievements,
        CronTrigger(hour=0, minute=5, timezone=CHINA_TZ),
        id="anniversary_achievement_check",
        replace_existing=True
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")


def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("定时任务调度器已关闭")
