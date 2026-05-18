"""共享工具函数模块"""

import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def try_achieve(user_id: int, name: str, db: Session):
    """尝试解锁成就的便捷封装，失败时记录日志但不抛异常"""
    try:
        from app.routers.love import try_unlock_achievement
        result = try_unlock_achievement(user_id, name, db)
        logger.info(f"成就检测 [{name}] user={user_id} result={result}")
    except Exception as e:
        logger.error(f"成就检测失败 [{name}] user={user_id}: {e}", exc_info=True)
