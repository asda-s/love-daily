"""
WebSocket实时通知模块
提供消息推送能力，支持通知实时送达
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger
import jwt
import json
from typing import Dict, Set

router = APIRouter()

# 在线连接池: user_id -> set of WebSocket connections
_connections: Dict[int, Set[WebSocket]] = {}


async def broadcast_to_user(user_id: int, message: dict):
    """向指定用户的所有连接推送消息"""
    if user_id in _connections:
        dead = []
        for ws in _connections[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _connections[user_id].discard(ws)
        if not _connections[user_id]:
            del _connections[user_id]


async def broadcast_to_couple(user_id: int, lover_id: int, message: dict):
    """向情侣双方推送消息"""
    await broadcast_to_user(user_id, message)
    await broadcast_to_user(lover_id, message)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket通知连接
    连接地址: ws://host/ws/notifications?token=<jwt_token>
    """
    from app.security import decode_access_token
    from app.database import SessionLocal
    from app.models import User

    # 验证token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="无效的认证凭据")
        return

    user_id = int(payload.get("sub", 0))
    if not user_id:
        await websocket.close(code=4001, reason="无效的用户ID")
        return

    # 验证用户存在
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4001, reason="用户不存在")
            return
    finally:
        db.close()

    # 注册连接
    await websocket.accept()
    if user_id not in _connections:
        _connections[user_id] = set()
    _connections[user_id].add(websocket)
    logger.info(f"WebSocket连接: user_id={user_id}")

    try:
        # 发送连接成功消息
        await websocket.send_json({"type": "connected", "message": "连接成功"})

        # 保持连接，接收心跳
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"WebSocket异常: user_id={user_id} error={e}")
    finally:
        if user_id in _connections:
            _connections[user_id].discard(websocket)
            if not _connections[user_id]:
                del _connections[user_id]
        logger.info(f"WebSocket断开: user_id={user_id}")
