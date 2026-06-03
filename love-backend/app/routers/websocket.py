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
        # 先复制一份，避免异步迭代期间集合变化导致 RuntimeError
        conns = list(_connections[user_id])
        dead = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        if dead:
            for ws in dead:
                _connections[user_id].discard(ws)
            if not _connections[user_id]:
                del _connections[user_id]


async def broadcast_to_couple(user_id: int, lover_id: int, message: dict):
    """向情侣双方推送消息"""
    await broadcast_to_user(user_id, message)
    await broadcast_to_user(lover_id, message)


async def broadcast_whisper(receiver_id: int, whisper_data: dict):
    """向接收者推送悄悄话消息"""
    await broadcast_to_user(receiver_id, {
        "type": "whisper",
        "data": whisper_data
    })


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

        # 保持连接，接收心跳和消息
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                continue
            # 解析JSON消息
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")
                if msg_type == "typing":
                    # 转发输入状态给伴侣
                    db2 = SessionLocal()
                    try:
                        user = db2.query(User).filter(User.id == user_id).first()
                        if user and user.lover_id:
                            await broadcast_to_user(user.lover_id, {
                                "type": "typing",
                                "data": {
                                    "user_id": user_id,
                                    "is_typing": msg.get("data", {}).get("is_typing", False)
                                }
                            })
                    finally:
                        db2.close()
            except (json.JSONDecodeError, AttributeError):
                pass
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
