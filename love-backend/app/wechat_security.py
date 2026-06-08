"""
微信内容安全检测模块
调用微信 msgSecCheck API 对用户发布的内容进行安全审核
"""

import os
import time
import httpx
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

WX_APPID = os.getenv("WX_APPID", "")
WX_SECRET = os.getenv("WX_SECRET", "")

# token 缓存
_token_cache = {"token": None, "expires_at": 0}


async def _get_access_token() -> str:
    """获取微信 access_token，自动缓存"""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    if not WX_APPID or not WX_SECRET:
        logger.warning("WX_APPID/WX_SECRET 未配置，跳过内容安全检测")
        return ""

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": WX_APPID,
                "secret": WX_SECRET,
            },
        )
        data = resp.json()
        if "access_token" in data:
            _token_cache["token"] = data["access_token"]
            _token_cache["expires_at"] = now + data.get("expires_in", 7200)
            return _token_cache["token"]
        else:
            logger.error(f"获取微信access_token失败: {data}")
            return ""


async def check_text_content(content: str) -> bool:
    """
    检测文本内容是否合规
    返回 True 表示合规，False 表示违规
    未配置密钥时默认放行
    """
    if not WX_APPID or not WX_SECRET:
        return True

    token = await _get_access_token()
    if not token:
        return True

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.weixin.qq.com/wxa/msg_sec_check",
                params={"access_token": token},
                json={"content": content, "version": 2, "scene": 2},
            )
            data = resp.json()
            if data.get("errcode") == 0:
                return True
            logger.warning(f"内容安全检测不通过: {data}")
            return False
    except Exception as e:
        logger.error(f"内容安全检测异常: {e}")
        # 检测服务异常时放行，不影响用户体验
        return True


async def check_image_content(media_url: str) -> bool:
    """
    检测图片内容是否合规（异步提交方式）
    返回 True 表示合规，False 表示违规
    """
    if not WX_APPID or not WX_SECRET:
        return True

    token = await _get_access_token()
    if not token:
        return True

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.weixin.qq.com/wxa/img_sec_check",
                params={"access_token": token},
                json={"media_url": media_url, "version": 2, "scene": 2},
            )
            data = resp.json()
            if data.get("errcode") == 0:
                return True
            logger.warning(f"图片安全检测不通过: {data}")
            return False
    except Exception as e:
        logger.error(f"图片安全检测异常: {e}")
        return True
